# Practice Questions: Control Flow, Functions, Scope, and Errors

These 40 practice questions rehearse everything taught in Topics 01–07 of
this module: conditionals, guards, Boolean logic, `match`/`case`, `for`
and `while` loops, `range()`, `break`, `continue`, `enumerate()`,
`zip()`, functions, parameters, return values, positional and keyword
arguments, safe defaults, keyword-only arguments, docstrings, scope,
lifetime, global state, pure functions, side effects, validation,
standard exceptions, `try`/`except`/`else`/`finally`, `raise`, and one
minimal custom exception.

Every question uses **only** ideas already taught here or in Modules 1.1
and 1.2 — nothing from later modules (no files, databases, APIs,
decorators, recursion, comprehensions, or external libraries). The only
`class` in this entire file is the one minimal custom exception the
roadmap explicitly asks for.

Try to solve each question yourself — in plain English first, then in
Python — before reading its solution.

## Table of Contents

- [Part A — Control Flow Practice](#part-a--control-flow-practice)
  - [Basic (A1–A5)](#part-a-basic)
  - [Moderate (A6–A10)](#part-a-moderate)
  - [Hard (A11–A15)](#part-a-hard)
  - [Advanced (A16–A20)](#part-a-advanced)
- [Part B — Functions, Scope, Side Effects, and Errors Practice](#part-b--functions-scope-side-effects-and-errors-practice)
  - [Basic (B1–B5)](#part-b-basic)
  - [Moderate (B6–B10)](#part-b-moderate)
  - [Hard (B11–B15)](#part-b-hard)
  - [Advanced (B16–B20)](#part-b-advanced)

---

<a id="part-a--control-flow-practice"></a>

# Part A — Control Flow Practice

Part A covers only Topics 01–02: conditionals, guards, Boolean logic,
`match`/`case`, `for`/`while` loops, `range()`, `break`, `continue`,
`enumerate()`, and `zip()`. No functions are used anywhere in Part A —
functions are not taught until Topic 03.

<a id="part-a-basic"></a>

## Basic (A1–A5)

### Question A1 — Basic

#### Problem statement

Given a whole number, print whether it is even or odd.

#### Concepts practised

`if`/`else`, the modulo operator `%` (Topic 01; Module 1.2 operators).

#### Requirements and expected output

- Store a number in a variable.
- Use `%` to test divisibility by 2.
- Print exactly one of two messages.

#### Edge cases to consider

- `0` is even (`0 % 2 == 0` is `True`) — make sure your condition handles
  it the same way as any other even number, with no special case needed.
- Negative numbers work correctly too: `-7 % 2` is `1` in Python, so odd
  negative numbers are still detected correctly.

#### Solution approach

1. Store the number.
2. Check `number % 2 == 0`.
3. Print the matching message.

#### Complete runnable Python solution

```python
number = 17

if number % 2 == 0:
    print(f"{number} is even.")
else:
    print(f"{number} is odd.")
```

#### Explanation

- `number % 2` computes the remainder after dividing by 2 — `0` for
  every even number, `1` for every odd number.
- `if number % 2 == 0:` is `False` here (`17 % 2` is `1`), so the `else`
  branch runs.

#### Example output

```text
17 is odd.
```

#### Why this solution works

`%` gives a reliable, simple way to test evenness for any whole number,
positive or negative, without needing to check the number's digits or
sign.

#### Common beginner mistakes

- Using `/` instead of `%`, which gives a fractional result rather than
  a remainder, and cannot be compared to `0` the same way.
- Writing `number % 2 = 0` instead of `==`, which is a `SyntaxError`
  since `=` is assignment, not comparison.

#### Optional improvement challenge

Extend the program to also print `"zero"` specifically when the number
is exactly `0`, before checking even/odd.

---

### Question A2 — Basic

#### Problem statement

Given a list of scores, decide whether the group's average meets a pass
threshold of `75`. If the list is empty, do not attempt to compute an
average — report that there is no data instead, without crashing.

#### Concepts practised

Comparisons, `and`, and short-circuit evaluation (Topic 01, Section 6).

#### Requirements and expected output

- Check two groups: one with an empty list, one with real scores.
- Use one combined condition, with `and`, that never crashes even when
  the list is empty.
- Print a message for each group.

#### Edge cases to consider

- An empty list must never reach `sum(scores) / len(scores)`, since that
  would raise `ZeroDivisionError` — the whole point of this question is
  to prevent that using short-circuit evaluation, not an `if`/`else`
  around the division.

#### Solution approach

1. Put `len(scores) > 0` **first** in an `and` expression.
2. Only if that is `True` does Python evaluate the average comparison,
   thanks to short-circuiting.
3. Print the result for both an empty and a non-empty list.

#### Complete runnable Python solution

```python
scores_a = []
scores_b = [70, 85, 90]

if len(scores_a) > 0 and sum(scores_a) / len(scores_a) >= 75:
    print("Group A meets the threshold.")
else:
    print("Group A has no scores, or is below the threshold.")

if len(scores_b) > 0 and sum(scores_b) / len(scores_b) >= 75:
    print("Group B meets the threshold.")
else:
    print("Group B has no scores, or is below the threshold.")
```

#### Explanation

- For `scores_a`, `len(scores_a) > 0` is `False`, so Python never even
  evaluates `sum(scores_a) / len(scores_a)` — this is short-circuit
  evaluation, and it is exactly what prevents a crash.
- For `scores_b`, `len(scores_b) > 0` is `True`, so Python evaluates the
  second half: `(70 + 85 + 90) / 3 = 81.67`, which is `>= 75`, so the
  first branch runs.

#### Example output

```text
Group A has no scores, or is below the threshold.
Group B meets the threshold.
```

#### Why this solution works

`and` stops evaluating as soon as its left side is `False`, since the
whole expression is already known to be `False` — this is exactly the
guard pattern from Topic 01 that safely prevents a risky calculation
from ever running on invalid data.

#### Common beginner mistakes

- Writing the risky calculation first: `sum(scores) / len(scores) >= 75
  and len(scores) > 0` — this crashes on an empty list, because Python
  evaluates `and`'s left side first, and the "safe" check comes too late.
- Assuming `and` needs both sides to be written as separate `if`
  statements — one combined condition is simpler and equally safe here.

#### Optional improvement challenge

Add a third group with exactly one score equal to `75`, and confirm it
is correctly reported as meeting the threshold.

---

### Question A3 — Basic

#### Problem statement

Print each fruit in a list, numbered starting from 1, using a manual
counter (not `enumerate()` yet).

#### Concepts practised

Basic `for` loop, a running counter variable (Topic 02).

#### Requirements and expected output

- Loop over a list of three fruits.
- Track a count starting at `0`, increasing by `1` on every pass.
- Print the count and the fruit together.

#### Edge cases to consider

- The counter must be increased **before** printing, not after, so the
  first fruit is numbered `1`, not `0`.

#### Solution approach

1. Create the counter, starting at `0`.
2. Inside the loop, increase it by `1` first.
3. Print the counter and the current fruit.

#### Complete runnable Python solution

```python
fruits = ["apple", "banana", "cherry"]

count = 0
for fruit in fruits:
    count = count + 1
    print(count, fruit)
```

#### Explanation

- `count = 0` starts the counter before the loop begins.
- Each pass through `for fruit in fruits:` increases `count` by `1`
  first, then prints it alongside the current `fruit`.

#### Example output

```text
1 apple
2 banana
3 cherry
```

#### Why this solution works

Incrementing the counter at the very start of each pass guarantees it
always matches "how many items have been visited so far, including this
one," giving a correct 1-based count with no off-by-one error.

#### Common beginner mistakes

- Incrementing `count` **after** the `print(...)` line, which numbers
  the first fruit `0` instead of `1`.
- Forgetting to initialize `count` before the loop, which would raise
  `NameError` on the first pass.

#### Optional improvement challenge

Rewrite this using `enumerate(fruits, start=1)` instead of a manual
counter, and compare the two approaches.

---

### Question A4 — Basic

#### Problem statement

Print a countdown from 5 down to 1, then print `"Go!"`.

#### Concepts practised

Basic `while` loop with a correctly updating condition (Topic 02).

#### Requirements and expected output

- Start a counter at `5`.
- Print it and decrease it by `1` each pass, while it is greater than
  `0`.
- Print `"Go!"` once the loop finishes.

#### Edge cases to consider

- The loop must actually update `countdown` inside its body, or it would
  never stop — a classic infinite-loop risk from Topic 02.

#### Solution approach

1. Set `countdown = 5`.
2. Loop `while countdown > 0:`, printing then decreasing `countdown`.
3. Print `"Go!"` after the loop ends.

#### Complete runnable Python solution

```python
countdown = 5

while countdown > 0:
    print(countdown)
    countdown = countdown - 1

print("Go!")
```

#### Explanation

- The loop prints `countdown`, then subtracts `1` from it, on every
  pass, until `countdown > 0` becomes `False` (once `countdown` reaches
  `0`).
- `print("Go!")` sits outside the loop, so it runs exactly once, after
  the loop finishes.

#### Example output

```text
5
4
3
2
1
Go!
```

#### Why this solution works

Because `countdown` is guaranteed to decrease by exactly `1` every pass,
it is guaranteed to eventually reach `0`, so the loop is guaranteed to
finish — the essential requirement for any safe `while` loop.

#### Common beginner mistakes

- Forgetting `countdown = countdown - 1` inside the loop, causing an
  infinite loop.
- Placing `print("Go!")` inside the loop by mistake, causing it to print
  five times instead of once.

#### Optional improvement challenge

Modify the program to count upward from 1 to 5 instead, printing "Go!"
at the end either way.

---

### Question A5 — Basic

#### Problem statement

Print every multiple of 3 from 3 to 30, inclusive.

#### Concepts practised

`range()` with a step (Topic 02).

#### Requirements and expected output

- Use one `range(...)` call with a start, stop, and step.
- Print each value on its own line.

#### Edge cases to consider

- The stop value passed to `range()` must be `31`, not `30`, since
  `range()` always excludes its stop value — using `30` directly would
  leave out `30` itself.

#### Solution approach

1. Call `range(3, 31, 3)`.
2. Loop over it with `for`, printing each number.

#### Complete runnable Python solution

```python
for number in range(3, 31, 3):
    print(number)
```

#### Explanation

- `range(3, 31, 3)` starts at `3`, stops before `31`, and moves forward
  by `3` each time, producing `3, 6, 9, ..., 30`.
- The `for` loop prints each of these ten numbers, one per line.

#### Example output

```text
3
6
9
12
15
18
21
24
27
30
```

#### Why this solution works

Choosing a stop value one past the last number you actually want is the
standard way to correctly include that final number, since `range()`
always excludes its stop value.

#### Common beginner mistakes

- Writing `range(3, 30, 3)`, which incorrectly excludes `30`.
- Forgetting the step value entirely, which would print every whole
  number from 3 to 30, not just the multiples of 3.

#### Optional improvement challenge

Print the same multiples of 3 in reverse order, from 30 down to 3, using
a negative step.

---

<a id="part-a-moderate"></a>

## Moderate (A6–A10)

### Question A6 — Moderate

#### Problem statement

Given a numeric score, print its letter grade using the bands: 90+ is
`"A"`, 80–89 is `"B"`, 70–79 is `"C"`, and anything else is `"F"`.

#### Concepts practised

`if`/`elif`/`else` chains (Topic 01).

#### Requirements and expected output

- Store one score.
- Use exactly one `if`/`elif`/`elif`/`else` chain, checked from highest
  threshold to lowest.
- Print the score and its grade.

#### Edge cases to consider

- The conditions must be ordered from highest to lowest; ordering them
  the other way would make every score of 70 or above incorrectly match
  the first, too-broad condition.
- A score of exactly `90`, `80`, or `70` must land in the higher band
  (`>=`, not `>`).

#### Solution approach

1. Check `score >= 90` first.
2. Then `score >= 80`, then `score >= 70`.
3. Use `else` for anything below `70`.

#### Complete runnable Python solution

```python
score = 74

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"

print(f"Score {score} -> Grade {grade}")
```

#### Explanation

- `score >= 90` is `False` (`74 >= 90` is `False`), so Python checks
  `score >= 80`, also `False`, then `score >= 70`, which is `True` — so
  `grade = "C"` runs, and the chain stops there.

#### Example output

```text
Score 74 -> Grade C
```

#### Why this solution works

Checking from the highest threshold down guarantees that once a
condition matches, it is genuinely the correct, most specific band for
that score.

#### Common beginner mistakes

- Ordering the checks from lowest to highest, which misclassifies every
  high score.
- Using `>` instead of `>=`, which would incorrectly exclude a score of
  exactly `90`, `80`, or `70` from its intended band.

#### Optional improvement challenge

Add a `"D"` band for scores from 60–69, adjusting the `else` to only
catch scores below 60.

---

### Question A7 — Moderate

#### Problem statement

Validate a PIN: it must not be empty, must contain only digits, and must
be exactly 4 characters long. Print a clear message for whichever
problem is found first, or confirm acceptance.

#### Concepts practised

Guard conditions using a flat `elif` chain (Topic 01, Section 7).

#### Requirements and expected output

- Check the worst problem first (empty), then the next, then the next.
- Print exactly one message.

#### Edge cases to consider

- `"12a4"` is the wrong length rule to check *after* confirming it fails
  the digits-only rule — order matters, since it fails both `isdigit()`
  and, coincidentally, is the right length.

#### Solution approach

1. Check for an empty string first.
2. Then check `not pin.isdigit()`.
3. Then check the length.
4. Otherwise, accept it.

#### Complete runnable Python solution

```python
pin = "12a4"

if pin == "":
    print("Error: PIN cannot be empty.")
elif not pin.isdigit():
    print("Error: PIN must contain only digits.")
elif len(pin) != 4:
    print("Error: PIN must be exactly 4 digits.")
else:
    print("PIN accepted.")
```

#### Explanation

- `pin == ""` is `False`, so Python checks `not pin.isdigit()` next.
  `"12a4".isdigit()` is `False` (because of the letter `"a"`), so `not
  False` is `True`, and this branch runs, reporting the digits-only
  rule — even though the length also happens to be correct.

#### Example output

```text
Error: PIN must contain only digits.
```

#### Why this solution works

Checking bad cases one at a time, in a flat `elif` chain, means every
input is reported by exactly one clear, specific message, chosen in a
predictable, deliberate order.

#### Common beginner mistakes

- Checking the length before checking `isdigit()`, which can produce a
  confusing message when a PIN fails both checks at once.
- Using nested `if` statements instead of `elif`, making the code harder
  to follow as more rules are added.

#### Optional improvement challenge

Add a rule rejecting a PIN made of four identical digits (like
`"1111"`), and place it in a sensible position in the chain.

---

### Question A8 — Moderate

#### Problem statement

Given a list of words, print the position (starting at 1) and the word,
for every word that appears in a list of banned words.

#### Concepts practised

`enumerate()` and membership checks with `in` (Topic 02; Topic 01).

#### Requirements and expected output

- Loop with `enumerate(words, start=1)`.
- Check membership in `banned_words` with `in`.
- Print only the banned matches.

#### Edge cases to consider

- A word that never appears in `banned_words` must simply be skipped —
  no output at all for it, not an empty line.

#### Solution approach

1. Loop over `words` using `enumerate(words, start=1)`.
2. For each, check `if word in banned_words:`.
3. Print the position and the word when it matches.

#### Complete runnable Python solution

```python
words = ["hello", "scam", "world", "spam", "friend"]
banned_words = ["scam", "spam"]

for position, word in enumerate(words, start=1):
    if word in banned_words:
        print(f"Word {position}: '{word}' is banned.")
```

#### Explanation

- `enumerate(words, start=1)` pairs each word with its 1-based position,
  unpacked directly into `position` and `word`.
- `if word in banned_words:` checks membership in the second list;
  `"scam"` (position 2) and `"spam"` (position 4) both match, and are
  the only two lines printed.

#### Example output

```text
Word 2: 'scam' is banned.
Word 4: 'spam' is banned.
```

#### Why this solution works

`enumerate()` provides the position without any manual counter, and `in`
directly answers "does this word appear in the banned list?" without
writing a nested loop by hand.

#### Common beginner mistakes

- Forgetting `start=1`, which would number the first word `0` instead of
  `1`.
- Checking `banned_words in word` (the operands reversed), which asks a
  completely different, usually `False`, question.

#### Optional improvement challenge

Count and print, at the end, how many banned words were found in total.

---

### Question A9 — Moderate

#### Problem statement

Loop through a list of numbers. Skip negative numbers, but stop the
loop entirely the moment a `0` is reached.

#### Concepts practised

`break` and `continue` together (Topic 02).

#### Requirements and expected output

- Use `continue` for negative numbers.
- Use `break` for exactly `0`.
- Print every other number.

#### Edge cases to consider

- The number `0` should never itself be printed — the loop must stop
  *before* printing it, so `break` must come before any `print(...)`
  for that value.

#### Solution approach

1. Loop over the numbers.
2. If negative, `continue` immediately.
3. If exactly `0`, `break` immediately.
4. Otherwise, print the number.

#### Complete runnable Python solution

```python
numbers = [4, -2, 7, 0, 9, -5]

for number in numbers:
    if number < 0:
        continue
    if number == 0:
        break
    print(number)
```

#### Explanation

- `4` is printed. `-2` is negative, so `continue` skips straight to the
  next number. `7` is printed. `0` triggers `break`, which exits the
  loop immediately — `9` and `-5` are never even visited.

#### Example output

```text
4
7
```

#### Why this solution works

Checking the `continue` condition first, before the `break` condition,
correctly separates "skip this one" from "stop entirely" — swapping
their order or combining them into one condition would change the
behavior.

#### Common beginner mistakes

- Placing `print(number)` before the `continue`/`break` checks, which
  would print negative numbers and `0` as well.
- Confusing `break` and `continue`, expecting the loop to skip `0`
  rather than stop there.

#### Optional improvement challenge

Change the program to also stop if it encounters any number greater
than `100`, in addition to stopping at `0`.

---

### Question A10 — Moderate

#### Problem statement

Given a list of student names and a list of their scores, print each
name together with its matching score.

#### Concepts practised

`zip()` (Topic 02).

#### Requirements and expected output

- Both lists are the same length here.
- Loop over both together using `zip()`.
- Print a name and its score on each line.

#### Edge cases to consider

- If the two lists were different lengths, `zip()` would silently stop
  at the shorter one — not relevant to this exact input, but worth
  remembering (see Question A13 for the mismatched case).

#### Solution approach

1. Call `zip(names, scores)`.
2. Loop over the result, unpacking each pair into `name` and `score`.
3. Print both together.

#### Complete runnable Python solution

```python
names = ["Ada", "Grace", "Alan"]
scores = [92, 88, 76]

for name, score in zip(names, scores):
    print(name, "scored", score)
```

#### Explanation

- `zip(names, scores)` pairs `names[0]` with `scores[0]`,
  `names[1]` with `scores[1]`, and so on.
- `for name, score in zip(...):` unpacks each pair directly, so no
  manual indexing into either list is needed.

#### Example output

```text
Ada scored 92
Grace scored 88
Alan scored 76
```

#### Why this solution works

`zip()` handles the pairing-by-position automatically, which is both
shorter and less error-prone than indexing into both lists by hand
inside a `range(len(...))` loop.

#### Common beginner mistakes

- Looping over `names` alone and indexing into `scores[position]`
  separately, which works but is more error-prone than `zip()`.
- Assuming `zip()` returns a list directly — wrapping it in `list(...)`
  is only needed if you want to print or store the pairs themselves,
  not to loop over them.

#### Optional improvement challenge

Add a third list, `subjects`, and use `zip(names, scores, subjects)` to
print all three together.

---

<a id="part-a-hard"></a>

## Hard (A11–A15)

### Question A11 — Hard

#### Problem statement

Given a list of day abbreviations, classify each one as `"Weekday"`,
`"Weekend"`, or `"Unknown"` if it is not a recognized day.

#### Concepts practised

`match`/`case` with combined literal patterns and a `_` default (Topic
01, Section 8).

#### Requirements and expected output

- Use one `match` statement inside a loop.
- Combine `"Sat"`/`"Sun"` into one case using `|`.
- Combine the five weekday abbreviations into another case.
- Use `_` for anything else.

#### Edge cases to consider

- An unrecognized value, `"Xyz"`, must not raise an error — it must
  fall through to the `_` case cleanly.

#### Solution approach

1. Loop over the list of days.
2. `match day:` against the weekend case, the weekday case, and `_`.
3. Print the day and its classification.

#### Complete runnable Python solution

```python
days = ["Mon", "Sat", "Xyz", "Sun"]

for day in days:
    match day:
        case "Sat" | "Sun":
            day_type = "Weekend"
        case "Mon" | "Tue" | "Wed" | "Thu" | "Fri":
            day_type = "Weekday"
        case _:
            day_type = "Unknown"
    print(day, "->", day_type)
```

#### Explanation

- `"Mon"` matches the weekday case. `"Sat"` and `"Sun"` both match the
  weekend case (that is what `|` means: "or"). `"Xyz"` matches neither
  literal case, so it falls to `case _:`, the wildcard default.

#### Example output

```text
Mon -> Weekday
Sat -> Weekend
Xyz -> Unknown
Sun -> Weekend
```

#### Why this solution works

`match` compares `day` against each pattern in order and runs only the
first one that matches; `_` guarantees every possible value is handled,
even ones nobody anticipated by name.

#### Common beginner mistakes

- Forgetting the `case _:` default entirely, which would silently do
  nothing at all for `"Xyz"`, with no error and no output.
- Trying to use a comparison like `case day >= "Mon":` inside `match` —
  this lesson's `match` only supports exact literal patterns, not
  ranges or comparisons.

#### Optional improvement challenge

Add a `case "":` for a blank day value, reporting it as `"Missing"`
instead of `"Unknown"`.

---

### Question A12 — Hard

#### Problem statement

Given a list of numbers, find and print the highest one, without using
the built-in `max()` function. If the list is empty, report that
clearly instead of crashing.

#### Concepts practised

Combining a loop and a condition, handling an empty-list edge case
(Topic 01; Topic 02).

#### Requirements and expected output

- Check two lists: one empty, one with real numbers.
- Handle the empty case with a guard `if`, before attempting to find a
  maximum.
- Print the result for both.

#### Edge cases to consider

- `numbers[0]` cannot be safely accessed if `numbers` is empty — the
  empty check must come first, and must completely skip the
  maximum-finding logic.

#### Solution approach

1. Check `if len(numbers) == 0:` first.
2. Otherwise, start `highest` at the first item, and loop through the
   rest, updating `highest` whenever a bigger number is found.
3. Print the result.

#### Complete runnable Python solution

```python
number_lists = [[], [4, 9, 2, 7]]

for numbers in number_lists:
    if len(numbers) == 0:
        print("No numbers to check.")
    else:
        highest = numbers[0]
        for number in numbers:
            if number > highest:
                highest = number
        print("Highest number:", highest)
```

#### Explanation

- The outer loop tries an empty list, then a real one.
- For the empty list, `len(numbers) == 0` is `True`, so the safe message
  prints, and `numbers[0]` is never touched.
- For `[4, 9, 2, 7]`, `highest` starts at `4`; the inner loop then finds
  `9` is bigger (`highest` becomes `9`), and neither `2` nor `7` beats
  it.

#### Example output

```text
No numbers to check.
Highest number: 9
```

#### Why this solution works

Guarding against the empty case *before* trying to read `numbers[0]`
prevents `IndexError` entirely, exactly the kind of boundary check
covered in Topic 01.

#### Common beginner mistakes

- Writing `highest = numbers[0]` before checking whether the list is
  empty, which raises `IndexError: list index out of range` on an empty
  list.
- Using `>=` instead of `>` inside the inner loop — this would still
  give the correct highest value, but is worth being deliberate about.

#### Optional improvement challenge

Adapt the program to also find and print the *lowest* number in the
same pass, using a second tracking variable.

---

### Question A13 — Hard

#### Problem statement

Given a list of product names and a shorter list of prices, print each
matched name and price using `zip()`, then separately report which
products at the end of the name list have no listed price.

#### Concepts practised

`zip()` stopping at the shortest list, combined with `range()` and
`len()` to handle the leftover items (Topic 02).

#### Requirements and expected output

- `product_names` has four items; `product_prices` has three.
- Print the three matched pairs with `zip()`.
- Print the name(s) left over, using `range(len(product_prices),
  len(product_names))`.

#### Edge cases to consider

- `zip()` silently stops at the shorter list — it does **not** raise an
  error for the mismatch, so the leftover item must be found separately,
  by position.

#### Solution approach

1. Loop over `zip(product_names, product_prices)` and print each pair.
2. Loop over `range(len(product_prices), len(product_names))` to find
   the positions with no matching price.
3. Print each leftover name by that position.

#### Complete runnable Python solution

```python
product_names = ["Pen", "Notebook", "Eraser", "Ruler"]
product_prices = [1.5, 2.0, 0.75]

for name, price in zip(product_names, product_prices):
    print(name, "costs", price)

print("Products without a listed price:")
for position in range(len(product_prices), len(product_names)):
    print("-", product_names[position])
```

#### Explanation

- `zip(product_names, product_prices)` pairs only the first three names
  with the three available prices — `"Ruler"` is left out entirely by
  `zip()`, with no error.
- `range(len(product_prices), len(product_names))` is `range(3, 4)`,
  producing just the position `3`, which is exactly `"Ruler"`'s index.

#### Example output

```text
Pen costs 1.5
Notebook costs 2.0
Eraser costs 0.75
Products without a listed price:
- Ruler
```

#### Why this solution works

`zip()`'s behavior (stop at the shortest) is used deliberately here,
and the mismatch it leaves behind is handled explicitly with `range()`
and direct indexing, rather than assuming the two lists always match.

#### Common beginner mistakes

- Assuming `zip()` raises an error when lengths differ, and being
  surprised that `"Ruler"` is silently missing from the first loop's
  output.
- Getting the `range()` arguments backward
  (`range(len(product_names), len(product_prices))`), which would
  produce an empty range instead of the intended leftover positions.

#### Optional improvement challenge

Rewrite the leftover-reporting loop to also print `"No price listed"`
next to each leftover name, instead of just the name.

---

### Question A14 — Hard

#### Problem statement

Simulate a simple menu: given a list of pre-typed menu selections,
process each one, printing an action for `"1"`, `"2"`, and `"3"`, and a
clear rejection message for anything else.

#### Concepts practised

`match`/`case` handling an invalid menu choice with `_` (Topic 01,
Section 8).

#### Requirements and expected output

- Loop over a list of selections, including one invalid one, `"9"`.
- Use `match`/`case` to decide the action.
- Print a message for every selection, valid or not.

#### Edge cases to consider

- An invalid selection must produce a clear, specific message naming
  the invalid value — not be silently ignored.

#### Solution approach

1. Loop over `menu_selections`.
2. `match selection:` against `"1"`, `"2"`, `"3"`, and `_`.
3. Print the matching action or rejection message.

#### Complete runnable Python solution

```python
menu_selections = ["1", "2", "9", "3"]

for selection in menu_selections:
    match selection:
        case "1":
            print("Starting new game.")
        case "2":
            print("Loading saved game.")
        case "3":
            print("Exiting.")
        case _:
            print(f"'{selection}' is not a valid menu option.")
```

#### Explanation

- Each of `"1"`, `"2"`, and `"3"` matches its own specific `case` and
  prints the matching action. `"9"` matches none of them, falling
  through to `case _:`, which reports it by name rather than silently
  skipping it.

#### Example output

```text
Starting new game.
Loading saved game.
'9' is not a valid menu option.
Exiting.
```

#### Why this solution works

Naming the invalid selection directly in the rejection message (rather
than a generic "invalid choice") makes the program's behavior easy to
understand from its output alone — an early, small example of the
useful-error habits from Topic 07.

#### Common beginner mistakes

- Forgetting `case _:`, which would leave `"9"` completely unhandled,
  producing no output for it at all.
- Comparing `selection` as an integer (`case 1:`) when it is actually a
  string `"1"` — these would never match.

#### Optional improvement challenge

Add a `case "4":` for a "help" option that lists the other valid menu
choices.

---

### Question A15 — Hard

#### Problem statement

Given a list of scores that may include missing values (`None`),
compute the average of only the real scores. If every value is missing,
report that clearly instead of dividing by zero.

#### Concepts practised

`continue` to skip missing values, combined with an empty-result guard
(Topic 02; Topic 01).

#### Requirements and expected output

- Test two lists: one with some `None` values mixed in, one that is all
  `None`.
- Skip every `None` with `continue`.
- Guard against dividing by a count of `0`.

#### Edge cases to consider

- A list of all `None` values must produce `count == 0`, which must be
  checked **before** dividing, exactly like Question A2's short-circuit
  idea, but expressed here as a separate `if`/`else` instead.

#### Solution approach

1. For each list, loop through the scores, skipping `None` with
   `continue`, and accumulating a total and a count of real scores.
2. After the loop, check if `count == 0`.
3. Print the average, or the "no data" message.

#### Complete runnable Python solution

```python
scores_a = [85, None, 92, None, 78]
scores_b = [None, None, None]

for scores in (scores_a, scores_b):
    total = 0
    count = 0
    for score in scores:
        if score is None:
            continue
        total = total + score
        count = count + 1

    if count == 0:
        print("No valid scores were recorded.")
    else:
        print(f"Average of valid scores: {total / count:.1f}")
```

#### Explanation

- `for scores in (scores_a, scores_b):` loops over the two lists in
  turn, one full pass of the inner logic for each.
- `if score is None: continue` skips a missing value entirely, before
  it can be added to `total` or counted — using `is None`, the correct
  check for a genuinely missing value, from Topic 01.
- For `scores_a`, three real scores are found (`85 + 92 + 78 = 255`,
  count `3`, average `85.0`). For `scores_b`, `count` stays `0`, so the
  safe message prints instead of raising `ZeroDivisionError`.

#### Example output

```text
Average of valid scores: 85.0
No valid scores were recorded.
```

#### Why this solution works

Checking `count == 0` after the loop, before dividing, guarantees the
division only ever runs when there is at least one real score to divide
by.

#### Common beginner mistakes

- Checking `if score:` instead of `if score is None:` to detect a
  missing value — this would also incorrectly skip a real score of `0`,
  a genuinely valid value.
- Dividing by `len(scores)` instead of `count`, which would incorrectly
  include the `None` entries in the average's denominator.

#### Optional improvement challenge

Also print how many values were skipped as missing, for each list.

---

<a id="part-a-advanced"></a>

## Advanced (A16–A20)

These five questions are small, self-contained, top-level programs.
None of them use `def` — functions are not introduced until Topic 03.

### Question A16 — Advanced

#### Problem statement

Given a list of exam scores, classify each one into a letter grade,
print each classification, and print a final summary count of how many
scores fell into each grade.

#### Concepts practised

`if`/`elif`/`else`, a running dictionary of counts, `for` loops (Topics
01–02; Module 1.2 dictionaries).

#### Requirements and expected output

- Classify every score using the same bands as Question A6.
- Keep a running count per grade in a dictionary.
- Print each score's grade, then the final summary.

#### Edge cases to consider

- Every possible grade key (`"A"`, `"B"`, `"C"`, `"F"`) must already
  exist in the counts dictionary before the loop starts, so
  `grade_counts[grade] + 1` never fails with `KeyError`.

#### Solution approach

1. Create `grade_counts` with all four grades starting at `0`.
2. Loop through the scores, classify each with `if`/`elif`/`else`.
3. Increase the matching count and print the classification.
4. Print the final `grade_counts` dictionary.

#### Complete runnable Python solution

```python
scores = [95, 82, 67, 74, 58, 90]

grade_counts = {"A": 0, "B": 0, "C": 0, "F": 0}

for score in scores:
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    else:
        grade = "F"
    grade_counts[grade] = grade_counts[grade] + 1
    print(f"{score} -> {grade}")

print("Summary:", grade_counts)
```

#### Explanation

- `grade_counts` starts every grade at `0`, so incrementing any key is
  always safe.
- Each score is classified with the same `if`/`elif`/`else` chain from
  Question A6, then `grade_counts[grade] = grade_counts[grade] + 1`
  increases the matching running total.
- The final `print(...)` shows the completed tally after all six scores
  have been processed.

#### Example output

```text
95 -> A
82 -> B
67 -> F
74 -> C
58 -> F
90 -> A
Summary: {'A': 2, 'B': 1, 'C': 1, 'F': 2}
```

#### Why this solution works

Pre-populating every possible grade key avoids ever needing a
`.get(grade, 0)` fallback — every key the program will ever look up
already exists from the start.

#### Common beginner mistakes

- Starting with an empty `{}` and forgetting that
  `grade_counts[grade] + 1` raises `KeyError` the first time a brand-new
  grade is seen.
- Reusing the variable name `grade` for both the loop's classification
  and something else, causing confusing overwrites.

#### Optional improvement challenge

Also compute and print the class average alongside the grade summary.

---

### Question A17 — Advanced

#### Problem statement

Given a list of candidate passwords, report whether each one is
accepted or rejected, and if rejected, exactly which single rule it
broke: empty, too short, or missing a digit.

#### Concepts practised

Guard-style `elif` chains, `continue`, a nested `for` loop checking
characters (Topics 01–02).

#### Requirements and expected output

- Check each candidate password against three rules, in a sensible
  order.
- Skip straight to the next password immediately for an empty one.
- Print exactly one message per password.

#### Edge cases to consider

- An empty string must be handled **before** trying `len(password) < 8`
  or checking for digits — both would technically still work on `""`,
  but checking emptiness first gives a clearer, more specific message.

#### Solution approach

1. Loop through the candidate passwords.
2. If empty, print a message and `continue` to the next one.
3. Otherwise, check for a digit using a small inner loop.
4. Apply the length rule, then the digit rule, then accept.

#### Complete runnable Python solution

```python
candidate_passwords = ["short1", "longenoughbutnodigit", "GoodPass1", ""]

for password in candidate_passwords:
    if password == "":
        print(password, "-> rejected: cannot be empty")
        continue

    has_digit = False
    for character in password:
        if character.isdigit():
            has_digit = True

    if len(password) < 8:
        print(password, "-> rejected: must be at least 8 characters")
    elif not has_digit:
        print(password, "-> rejected: must contain a digit")
    else:
        print(password, "-> accepted")
```

#### Explanation

- `"short1"` is only 6 characters, so it fails the length check first.
- `"longenoughbutnodigit"` is long enough but has no digit, caught by
  the `elif not has_digit:` branch.
- `"GoodPass1"` passes both checks and is accepted.
- `""` is caught immediately by the first `if`, and `continue` skips the
  rest of that pass entirely — the inner digit-checking loop never even
  runs for it.

#### Example output

```text
short1 -> rejected: must be at least 8 characters
longenoughbutnodigit -> rejected: must contain a digit
GoodPass1 -> accepted
 -> rejected: cannot be empty
```

#### Why this solution works

Handling the empty-string case with an early `continue` avoids running
unnecessary checks on data that has already been fully diagnosed,
exactly the guard-clause spirit from Topic 01.

#### Common beginner mistakes

- Forgetting `continue` after handling the empty case, which would let
  the same password fall through into the length and digit checks too,
  potentially printing more than one message for it.
- Checking `has_digit` using `password.isdigit()` instead of checking
  each character, which asks "is the *entire* password only digits?" —
  a different, wrong question.

#### Optional improvement challenge

Add a rule requiring at least one uppercase letter, and report it as a
fourth possible rejection reason.

---

### Question A18 — Advanced

#### Problem statement

Simulate a traffic light cycling through red, green, and yellow, in the
correct order, for exactly four transitions.

#### Concepts practised

`while` loop with a countdown, `match`/`case` for state transitions
(Topics 01–02).

#### Requirements and expected output

- Start at `"red"`.
- Run the loop exactly `4` times, using a countdown variable.
- Print the transition made on each pass.

#### Edge cases to consider

- The countdown variable must be decreased exactly once per pass, no
  matter which `case` matched, or the loop could run more or fewer than
  four times.

#### Solution approach

1. Set `current_light = "red"` and `cycles = 4`.
2. While `cycles > 0`, use `match` to decide the next light and print
   the transition.
3. Decrease `cycles` by `1` after every pass.

#### Complete runnable Python solution

```python
current_light = "red"
cycles = 4

while cycles > 0:
    match current_light:
        case "red":
            print("Red -> Go to Green")
            current_light = "green"
        case "green":
            print("Green -> Go to Yellow")
            current_light = "yellow"
        case "yellow":
            print("Yellow -> Go to Red")
            current_light = "red"
    cycles = cycles - 1
```

#### Explanation

- Each pass matches `current_light` against the three known states,
  prints the transition being made, and updates `current_light` for the
  next pass.
- `cycles = cycles - 1` runs once per pass, regardless of which `case`
  matched, guaranteeing the loop runs exactly four times before
  stopping.

#### Example output

```text
Red -> Go to Green
Green -> Go to Yellow
Yellow -> Go to Red
Red -> Go to Green
```

#### Why this solution works

Placing `cycles = cycles - 1` outside the `match` statement, but still
inside the `while` loop, ensures it always runs exactly once per pass —
no matter which light was active.

#### Common beginner mistakes

- Placing `cycles = cycles - 1` inside one specific `case` only, which
  would make the loop run a different number of times depending on
  which light happened to be active.
- Forgetting a `case` for one of the three colors, which would silently
  do nothing on that pass (no `_` default is used here, since exactly
  three states are expected).

#### Optional improvement challenge

Add a `case _:` default that resets `current_light` to `"red"` if it
somehow becomes an unexpected value.

---

### Question A19 — Advanced

#### Problem statement

Search an inventory list for a specific item, reporting whether it was
found. Then repeat the search against a completely empty inventory.

#### Concepts practised

`break`, a `found` flag, an empty-collection edge case (Topic 02).

#### Requirements and expected output

- Search a real, non-empty inventory for an item that exists.
- Search an empty inventory for a different item.
- Print a clear found/not-found message for each search.

#### Edge cases to consider

- Looping over an empty list simply runs zero times — this must still
  correctly fall through to the "not found" message, not raise an
  error or produce no output at all.

#### Solution approach

1. Set `found = False`, loop through the inventory, and set `found =
   True` with `break` the moment a match is found.
2. After the loop, check `found` to decide which message to print.
3. Repeat the same pattern for the empty inventory.

#### Complete runnable Python solution

```python
inventory = ["hammer", "wrench", "pliers"]
search_term = "wrench"

found = False
for item in inventory:
    if item == search_term:
        found = True
        print(f"'{search_term}' found in inventory.")
        break

if not found:
    print(f"'{search_term}' not found in inventory.")

empty_inventory = []
search_term_2 = "screwdriver"
found_2 = False
for item in empty_inventory:
    if item == search_term_2:
        found_2 = True
        break

if not found_2:
    print(f"'{search_term_2}' not found in inventory.")
```

#### Explanation

- The first search finds `"wrench"` on the second item checked, prints
  a confirmation, and `break`s immediately — `"pliers"` is never
  checked.
- The second search loops over `empty_inventory`, which has zero items,
  so the loop body never runs at all; `found_2` stays `False`, and the
  "not found" message correctly prints afterward.

#### Example output

```text
'wrench' found in inventory.
'screwdriver' not found in inventory.
```

#### Why this solution works

Using a `found` flag, checked *after* the loop, correctly reports
"not found" whether the list had items that simply did not match, or
had no items at all — both cases end with `found` still `False`.

#### Common beginner mistakes

- Printing "not found" unconditionally *inside* the loop's `else`-less
  body, which would (incorrectly) print it once per non-matching item
  instead of once overall.
- Forgetting `break`, which would keep searching even after a match was
  already found — harmless here, but wasteful, and risky if a later,
  accidental duplicate match existed.

#### Optional improvement challenge

Modify the program to search for *all* matching items (in case of
duplicates) instead of stopping at the first one.

---

### Question A20 — Advanced

#### Problem statement

Given a list of student names and a shorter list of scores, print a
numbered pass/fail report for every matched pair, then separately list
any names that had no matching score.

#### Concepts practised

`zip()` with a manual position counter, `if`/`else`, mismatched-length
handling with `range()` (Topic 02).

#### Requirements and expected output

- `names` has four entries; `scores` has three.
- Print a numbered line per matched pair, with a pass/fail result
  (passing score is `60` or above).
- Separately report the unmatched name(s).

#### Edge cases to consider

- `zip()` silently stops at the shorter `scores` list — the unmatched
  name(s) must be found afterward, exactly as in Question A13.

#### Solution approach

1. Loop over `zip(names, scores)`, tracking a manual position counter.
2. Decide pass/fail with `if`/`else` and print the numbered line.
3. Afterward, compare `len(names)` and `len(scores)` to report any
   leftover names.

#### Complete runnable Python solution

```python
names = ["Ada", "Grace", "Alan", "Marie"]
scores = [92, 58, 74]

position = 0
for name, score in zip(names, scores):
    position = position + 1
    if score >= 60:
        result = "PASS"
    else:
        result = "FAIL"
    print(position, name, score, result)

if len(names) != len(scores):
    print("Note: some names have no matching score and were skipped:")
    for index in range(len(scores), len(names)):
        print("-", names[index])
```

#### Explanation

- The `zip()` loop processes exactly three matched pairs (`"Marie"` has
  no score to pair with, so `zip()` leaves her out entirely).
- `len(names) != len(scores)` is `True` (`4 != 3`), so the leftover
  check runs, correctly identifying `"Marie"` at zero-based index `3`,
  which is the fourth position in the list (the only index from
  `range(3, 4)`).

#### Example output

```text
1 Ada 92 PASS
2 Grace 58 FAIL
3 Alan 74 PASS
Note: some names have no matching score and were skipped:
- Marie
```

#### Why this solution works

Combining `zip()` for the easy, matched part of the problem with an
explicit `range()`-based check for the leftover part covers the entire
`names` list correctly, without assuming the two lists are always the
same length.

#### Common beginner mistakes

- Assuming every name always has a matching score, and never checking
  `len(names) != len(scores)` at all — silently losing track of
  `"Marie"` entirely.
- Reporting the leftover names using `zip()` again somehow — `zip()` has
  no way to express "the leftover part," which is exactly why `range()`
  and direct indexing are needed instead.

#### Optional improvement challenge

Instead of only listing unmatched names, also print how many students
in total passed, out of the ones that had a score to check.

---

<a id="part-b--functions-scope-side-effects-and-errors-practice"></a>

# Part B — Functions, Scope, Side Effects, and Errors Practice

Part B covers Topics 03–07: functions, parameters, return values,
positional and keyword arguments, safe defaults, keyword-only arguments,
docstrings, scope, lifetime, global state, pure functions, side
effects, validation, standard exceptions, and `try`/`except`/`else`/
`finally`/`raise`. The only `class` anywhere in this file is the one
minimal custom exception in Question B20.

<a id="part-b-basic"></a>

## Basic (B1–B5)

### Question B1 — Basic

#### Problem statement

Write a function that takes one number and returns its square. Call it
with two different numbers.

#### Concepts practised

`def`, one parameter, `return` (Topic 03).

#### Requirements and expected output

- Define `square(number)`.
- Call it twice, printing each result.

#### Edge cases to consider

- The function must `return` the result, not `print()` it, so the
  caller can decide what to do with it.

#### Solution approach

1. Define the function with one parameter.
2. `return number * number`.
3. Call it twice and print each returned value.

#### Complete runnable Python solution

```python
def square(number):
    return number * number

print(square(4))
print(square(7))
```

#### Explanation

- `square(number)` takes one parameter and hands back `number * number`
  using `return`, without printing anything itself.
- Each `print(square(...))` call displays whatever value was returned.

#### Example output

```text
16
49
```

#### Why this solution works

Because `square` returns its result instead of printing it, the exact
same function can be reused anywhere a squared number is needed, not
just for immediate display.

#### Common beginner mistakes

- Writing `print(number * number)` inside the function instead of
  `return`, which would make `square(4)` unusable in a later
  calculation.
- Forgetting parentheses when calling the function: `square 4` is not
  valid Python.

#### Optional improvement challenge

Write a second function, `cube(number)`, and call both functions on the
same list of numbers using a loop.

---

### Question B2 — Basic

#### Problem statement

Write a function that takes a price and a quantity and returns the
total cost.

#### Concepts practised

Two required parameters, `return` (Topic 03).

#### Requirements and expected output

- Define `calculate_total(price, quantity)`.
- Call it once and print the result.

#### Edge cases to consider

- Both arguments are required — calling the function with only one
  would raise `TypeError`.

#### Solution approach

1. Define the function with two parameters.
2. `return price * quantity`.
3. Call it and print the result.

#### Complete runnable Python solution

```python
def calculate_total(price, quantity):
    return price * quantity

print(calculate_total(9.99, 3))
```

#### Explanation

- `price` and `quantity` are both required parameters; the function
  multiplies them and returns the result.
- `calculate_total(9.99, 3)` returns `29.97`, which the outer
  `print(...)` displays.

#### Example output

```text
29.97
```

#### Why this solution works

Multiplying the two parameters directly and returning the result keeps
the function focused on exactly one calculation, ready to be reused with
any price and quantity.

#### Common beginner mistakes

- Calling `calculate_total(9.99)` with only one argument, which raises
  a `TypeError` because a required argument (`quantity`) is missing.
- Swapping the argument order, `calculate_total(3, 9.99)`, which still
  runs (both are numbers) but changes what the numbers are assumed to
  mean.

#### Optional improvement challenge

Add a third required parameter, `tax_rate`, and include it in the
returned total.

---

### Question B3 — Basic

#### Problem statement

Write two functions that both compute a square: one that only prints
it, and one that returns it. Show that only the second one's result can
be stored and reused.

#### Concepts practised

`print()` versus `return` (Topic 03).

#### Requirements and expected output

- Define `show_square(number)` (prints only) and `get_square(number)`
  (returns only).
- Call both, and store the second one's result in a variable.

#### Edge cases to consider

- Calling `show_square(...)` and trying to store its result would give
  `None`, since it has no `return` statement at all.

#### Solution approach

1. Define `show_square`, which only prints.
2. Define `get_square`, which only returns.
3. Call `show_square` directly; call `get_square` and store its result.

#### Complete runnable Python solution

```python
def show_square(number):
    print(number * number)

def get_square(number):
    return number * number

show_square(5)

result = get_square(5)
print("Stored result:", result)
```

#### Explanation

- `show_square(5)` computes `25` and prints it immediately, handing
  nothing back to the caller.
- `get_square(5)` computes the same `25`, but returns it instead;
  `result = get_square(5)` successfully stores that value, which the
  final `print(...)` then displays.

#### Example output

```text
25
Stored result: 25
```

#### Why this solution works

`return` is what makes a function's result available to the rest of the
program; `print()` alone only ever displays a value once, with no way
to capture it afterward.

#### Common beginner mistakes

- Writing `result = show_square(5)` and expecting `result` to be `25` —
  it would actually be `None`, since `show_square` never returns
  anything.
- Assuming a function needs both `print()` and `return` together —
  usually only one is appropriate, depending on whether the value needs
  to be seen immediately or reused later.

#### Optional improvement challenge

Rewrite `show_square` to call `get_square` internally and print its
result, avoiding repeating the multiplication logic twice.

---

### Question B4 — Basic

#### Problem statement

Calculate an order's total using a function, then use the returned
value in a further calculation that adds a flat shipping fee.

#### Concepts practised

Storing and reusing a returned value (Topic 03).

#### Requirements and expected output

- Define `calculate_total(price, quantity)`.
- Store its result, add shipping, and print the final amount.

#### Edge cases to consider

- The shipping fee must be added *after* the function call, using the
  stored return value — not inside the function itself, since the
  function's job is only to calculate the order total.

#### Solution approach

1. Call `calculate_total` and store the result.
2. Add the shipping fee to it.
3. Print the final amount, formatted as currency.

#### Complete runnable Python solution

```python
def calculate_total(price, quantity):
    return price * quantity

order_total = calculate_total(12.5, 2)
shipping = 4
final_amount = order_total + shipping
print(f"Final amount: ${final_amount:.2f}")
```

#### Explanation

- `calculate_total(12.5, 2)` returns `25.0`, stored in `order_total`.
- `final_amount = order_total + shipping` reuses that stored value in a
  completely separate calculation, giving `29.0`.

#### Example output

```text
Final amount: $29.00
```

#### Why this solution works

Because the function returned a real, usable number, the rest of the
program can freely build on it — exactly the reusability `return`
provides that `print()` alone cannot.

#### Common beginner mistakes

- Trying to add `shipping` directly inside `calculate_total`, which
  would incorrectly bake a specific shipping fee into a function meant
  only to calculate an order total.
- Forgetting to store the function's result at all, and trying to reuse
  `calculate_total(12.5, 2)` a second time instead of the stored value.

#### Optional improvement challenge

Add a second, separate shipping tier and let the program choose between
them with an `if`/`else` before adding it to `order_total`.

---

### Question B5 — Basic

#### Problem statement

Write a function that checks whether a number is positive, and use it
to check a list of numbers.

#### Concepts practised

A function returning a `bool`, basic validation (Topic 03).

#### Requirements and expected output

- Define `is_positive(number)`, returning `True` or `False`.
- Loop over a list of numbers, printing each one with its result.

#### Edge cases to consider

- `0` is **not** positive — `0 > 0` is `False`, and the function should
  reflect that directly.

#### Solution approach

1. Define the function using one comparison, returned directly.
2. Loop over a list of numbers, calling the function on each.

#### Complete runnable Python solution

```python
def is_positive(number):
    return number > 0

numbers_to_check = [5, -3, 0, 12]

for number in numbers_to_check:
    print(number, "->", is_positive(number))
```

#### Explanation

- `is_positive` directly returns the result of `number > 0` — no
  `if`/`else` is needed, since a comparison already produces `True` or
  `False`.
- The loop calls this function once per number, printing each one
  alongside its result.

#### Example output

```text
5 -> True
-3 -> False
0 -> False
12 -> True
```

#### Why this solution works

Returning a comparison's result directly is simpler and just as
correct as writing `if number > 0: return True else: return False`.

#### Common beginner mistakes

- Writing the unnecessary `if`/`else` version instead of returning the
  comparison directly — not wrong, just more code than needed.
- Assuming `0` should count as positive, since it is not negative — the
  function correctly treats it as `False`.

#### Optional improvement challenge

Write a second function, `is_negative(number)`, and print both results
for each number in the list.

---

<a id="part-b-moderate"></a>

## Moderate (B6–B10)

### Question B6 — Moderate

#### Problem statement

Call a two-parameter function three ways: correctly positional,
incorrectly positional (swapped), and by keyword. Compare the results.

#### Concepts practised

Positional versus keyword arguments (Topic 04).

#### Requirements and expected output

- Define `describe_item(name, price)`.
- Call it with correct positional order, swapped positional order, and
  keyword arguments.

#### Edge cases to consider

- The swapped call does not raise an error — both `1.5` and `"Pen"` are
  valid values for *some* parameter, so Python accepts the call and
  simply produces a nonsensical result.

#### Solution approach

1. Define the function.
2. Call it correctly.
3. Call it with the arguments swapped.
4. Call it again using keyword arguments, in a different order.

#### Complete runnable Python solution

```python
def describe_item(name, price):
    print(f"{name} costs ${price}")

describe_item("Pen", 1.5)
describe_item(1.5, "Pen")
describe_item(price=1.5, name="Pen")
```

#### Explanation

- `describe_item("Pen", 1.5)` matches `"Pen"` to `name` and `1.5` to
  `price`, by position — correct.
- `describe_item(1.5, "Pen")` matches them the other way around, purely
  by position, producing a nonsensical but non-crashing result.
- `describe_item(price=1.5, name="Pen")` names both arguments, so their
  order in the call no longer matters — this is correct again.

#### Example output

```text
Pen costs $1.5
1.5 costs $Pen
Pen costs $1.5
```

#### Why this solution works

Keyword arguments remove any dependence on the order they are written
in, since each one states exactly which parameter it belongs to.

#### Common beginner mistakes

- Assuming Python would catch the swapped-argument mistake — it never
  checks whether a value's *meaning* matches its parameter, only that
  something was supplied for every required parameter.
- Mixing a keyword argument before a positional one, such as
  `describe_item(name="Pen", 1.5)`, which raises `SyntaxError:
  positional argument follows keyword argument`.

#### Optional improvement challenge

Add a third parameter, `quantity`, and call the function using a mix of
one positional and two keyword arguments.

---

### Question B7 — Moderate

#### Problem statement

Write a function that formats a price with a currency symbol, defaulting
to `"$"` when no currency is specified.

#### Concepts practised

Safe, immutable default arguments (Topic 04).

#### Requirements and expected output

- Define `format_price(amount, currency="$")`.
- Call it once using the default, once overriding it.

#### Edge cases to consider

- The default value, `"$"`, is a `str` — immutable, and therefore safe
  to reuse as a default with no risk (unlike a mutable default such as
  `[]`).

#### Solution approach

1. Define the function with a default parameter.
2. Call it with just the required argument.
3. Call it again, overriding the default.

#### Complete runnable Python solution

```python
def format_price(amount, currency="$"):
    return f"{currency}{amount:.2f}"

print(format_price(20))
print(format_price(20, "€"))
```

#### Explanation

- `format_price(20)` supplies no `currency`, so it falls back to `"$"`,
  producing `"$20.00"`.
- `format_price(20, "€")` overrides the default positionally, producing
  `"€20.00"`.

#### Example output

```text
$20.00
€20.00
```

#### Why this solution works

An immutable default like `"$"` is created once and can safely be
reused, unchanged, across every call that relies on it — a mutable
default would not offer this same guarantee (see Question B12).

#### Common beginner mistakes

- Assuming a default parameter must always come *before* a required one
  in the definition — it is actually the reverse: for ordinary
  positional-or-keyword parameters, required parameters must come
  before parameters with defaults.
- Forgetting that overriding a default positionally requires it to be
  the correct position — using a keyword argument, `currency="€"`, is
  usually clearer.

#### Optional improvement challenge

Add a second default parameter, `decimal_places=2`, and use it inside
the format specifier instead of a hardcoded `.2f`.

---

### Question B8 — Moderate

#### Problem statement

Write a function that calculates a total, with an optional, keyword-only
setting for whether to include tax.

#### Concepts practised

Keyword-only arguments using `*` (Topic 04).

#### Requirements and expected output

- Define `calculate_total(price, quantity, *, include_tax=False)`.
- Call it once without tax, once with tax.

#### Edge cases to consider

- `include_tax` can never be supplied positionally — only by name — 
  since it comes after the `*`.

#### Solution approach

1. Define the function with two ordinary parameters and one
   keyword-only parameter.
2. Compute the subtotal, then apply tax only if requested.
3. Call it both ways.

#### Complete runnable Python solution

```python
def calculate_total(price, quantity, *, include_tax=False):
    subtotal = price * quantity
    if include_tax:
        return subtotal * 1.08
    return subtotal

print(calculate_total(10, 2))
print(calculate_total(10, 2, include_tax=True))
```

#### Explanation

- `price` and `quantity` remain ordinary parameters. `include_tax`
  comes after the `*`, so it must always be named when supplied.
- `calculate_total(10, 2)` never mentions `include_tax`, so it stays
  `False`, returning the plain subtotal, `20`.
- `calculate_total(10, 2, include_tax=True)` explicitly opts into the
  tax calculation, returning `21.6`.

#### Example output

```text
20
21.6
```

#### Why this solution works

Making `include_tax` keyword-only prevents it from ever being confused
with an ordinary positional argument, and forces every call that uses
it to state its purpose directly.

#### Common beginner mistakes

- Trying `calculate_total(10, 2, True)`, which raises a `TypeError`
  because `include_tax` is keyword-only and cannot be bound to a
  positional argument.
- Forgetting the `*` entirely, which would make `include_tax` an
  ordinary parameter, losing the "must be named" guarantee.

#### Optional improvement challenge

Add a second keyword-only parameter, `discount_rate=0.0`, applied before
the tax calculation.

---

### Question B9 — Moderate

#### Problem statement

Write a function that calculates a rectangle's area, with a clear
docstring, and display that docstring using `help()`.

#### Concepts practised

Docstrings and `help()` (Topic 04).

#### Requirements and expected output

- Define `calculate_area(width, height)` with a docstring covering
  purpose, parameters, and return value.
- Call it once, then call `help(calculate_area)`.

#### Edge cases to consider

- The docstring must be the very first line inside the function — after
  any other statement, it would just be an ordinary, unused string.

#### Solution approach

1. Write the function with a triple-quoted docstring as its first line.
2. Return the product of `width` and `height`.
3. Call the function, then call `help(...)` on it.

#### Complete runnable Python solution

```python
def calculate_area(width, height):
    """
    Calculate the area of a rectangle.

    width is the rectangle's width.
    height is the rectangle's height.
    Returns the area as a number.
    """
    return width * height

print(calculate_area(4, 5))
help(calculate_area)
```

#### Explanation

- The triple-quoted string, placed immediately after `def`, is the
  docstring — Python stores it on the function itself.
- `calculate_area(4, 5)` returns `20`, which the first `print(...)`
  displays.
- `help(calculate_area)` displays the function's signature together
  with its docstring, exactly as a reader would want to see it before
  using the function.

#### Example output

```text
20
Help on function calculate_area in module __main__:

calculate_area(width, height)
    Calculate the area of a rectangle.

    width is the rectangle's width.
    height is the rectangle's height.
    Returns the area as a number.
```

#### Why this solution works

A short, plain-English docstring covering purpose, parameters, and
return value gives a reader everything they need to use the function
correctly, without reading its body at all.

#### Common beginner mistakes

- Writing a comment (`# calculates area`) above the function instead of
  a docstring inside it — comments are not stored on the function and
  cannot be shown by `help()`.
- Writing a docstring that just repeats the function's name, without
  explaining the parameters or return value.

#### Optional improvement challenge

Add a note in the docstring about what happens if a negative width or
height is passed in (even though the function does not yet validate
this).

---

### Question B10 — Moderate

#### Problem statement

Show the difference between a local variable that shadows a global one,
and a function that safely reads a global value without changing it.

#### Concepts practised

Local versus global variables, shadowing (Topic 05).

#### Requirements and expected output

- Define a global `tax_rate`.
- Define one function that creates a same-named local variable
  (shadowing), and one that reads the global directly.
- Show that the global value survives both calls unchanged.

#### Edge cases to consider

- Assigning `tax_rate = 0.0` inside `show_local_rate` must **not**
  affect the global `tax_rate` at all — this is shadowing, not
  mutation. An assignment such as `tax_rate = 0.0` inside a function
  creates or rebinds a local name unless `global` is used, so it does
  not rebind the global `tax_rate`.

#### Solution approach

1. Define the global `tax_rate`.
2. Define `show_local_rate`, which assigns a local `tax_rate` and
   prints it.
3. Define `calculate_with_tax`, which only reads the global `tax_rate`.
4. Call both, and print the global value in between.

#### Complete runnable Python solution

```python
tax_rate = 0.08

def show_local_rate():
    tax_rate = 0.0
    print("Inside function:", tax_rate)

def calculate_with_tax(price):
    return price * (1 + tax_rate)

show_local_rate()
print("Outside function:", tax_rate)
print(calculate_with_tax(100))
```

#### Explanation

- `show_local_rate` creates its own **local** `tax_rate`, shadowing the
  global one only inside that function — it prints `0.0`.
- `print("Outside function:", tax_rate)` shows the global `tax_rate` is
  still `0.08`, completely unaffected by the function that just ran.
- `calculate_with_tax` never creates a local `tax_rate` at all, so it
  simply reads the global value, correctly using `0.08`.

#### Example output

```text
Inside function: 0.0
Outside function: 0.08
108.0
```

#### Why this solution works

A local assignment inside a function creates (or rebinds) a local name;
it does not rebind a global name unless the `global` keyword is
explicitly used. (Mutating an existing object, such as appending to a
global list, is a different action from rebinding a name.)

#### Common beginner mistakes

- Assuming `show_local_rate()` changes the global `tax_rate` to `0.0` —
  it does not, since `tax_rate = 0.0` inside the function only ever
  creates a local variable.
- Confusing this safe "read-only" pattern with the `UnboundLocalError`
  risk that happens only when a function *assigns* to a global-sounding
  name without `global` or a parameter.

#### Optional improvement challenge

Add a third function that uses the `global` keyword to genuinely change
`tax_rate`, and observe that the global value *does* change afterward.

---

<a id="part-b-hard"></a>

## Hard (B11–B15)

### Question B11 — Hard

#### Problem statement

Compare two functions that apply the same discount: one reads a global
discount rate, one takes it as a parameter. Explain which one is pure.

#### Concepts practised

Pure functions versus impure functions (Topic 06).

#### Requirements and expected output

- Define `apply_discount_impure(price)`, reading a global
  `discount_rate`.
- Define `apply_discount_pure(price, discount_rate)`.
- Call both and compare the results.

#### Edge cases to consider

- Both functions give the same answer here, but only one of them is
  guaranteed to keep doing so if something elsewhere in the program
  changes the global `discount_rate`.

#### Solution approach

1. Define the global `discount_rate`.
2. Define the impure version, reading the global.
3. Define the pure version, taking the rate as a parameter.
4. Call both and print the results.

#### Complete runnable Python solution

```python
discount_rate = 0.10

def apply_discount_impure(price):
    return price * (1 - discount_rate)

def apply_discount_pure(price, discount_rate):
    return price * (1 - discount_rate)

print(apply_discount_impure(100))
print(apply_discount_pure(100, 0.10))
```

#### Explanation

- `apply_discount_impure` depends on a **hidden** global value that
  never appears in its call — its signature, `apply_discount_impure(price)`,
  does not reveal this dependency at all.
- `apply_discount_pure` takes every value it needs as a parameter,
  making it a genuine **pure function**: its result depends only on its
  arguments, and nothing about it can change based on code elsewhere in
  the file.

#### Example output

```text
90.0
90.0
```

#### Why this solution works

Both give the same answer *right now*, but only `apply_discount_pure`'s
result depends only on its arguments: for the same arguments it
produces the same result, without depending on mutable external state —
exactly the predictability pure functions offer.

#### Common beginner mistakes

- Assuming a function is pure just because it uses `return` — 
  `apply_discount_impure` also returns a value, but is still impure
  because of its hidden dependency.
- Not noticing that changing the global `discount_rate` anywhere else in
  the program would silently change every future call to
  `apply_discount_impure`, without changing the call itself at all.

#### Optional improvement challenge

Add a line that changes `discount_rate` to `0.25` between the two
function calls, and observe how only the impure version's result
changes.

---

### Question B12 — Hard

#### Problem statement

Show the mutable-default-argument bug with a function that adds an item
to a list, and fix it using the safe `None` pattern.

#### Concepts practised

Mutation versus returning a new collection, the safe `None` default
(Topic 04, Section 6; Topic 06).

#### Requirements and expected output

- Define `add_item_unsafe(item, items=[])` and call it twice with no
  `items` argument.
- Define `add_item_safe(item, items=None)` and call it the same way.
- Compare the two sets of results.

#### Edge cases to consider

- The unsafe version's default list is created **once**, when the
  function is defined — every call that skips `items` shares that exact
  same list.

#### Solution approach

1. Define the unsafe version with `items=[]`.
2. Define the safe version with `items=None`, building a fresh list
   inside the function when needed.
3. Call each twice and compare.

#### Complete runnable Python solution

```python
def add_item_unsafe(item, items=[]):
    items.append(item)
    return items

def add_item_safe(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

print(add_item_unsafe("apple"))
print(add_item_unsafe("banana"))

print(add_item_safe("apple"))
print(add_item_safe("banana"))
```

#### Explanation

- `add_item_unsafe("apple")` appends to the one shared default list,
  returning `['apple']`. `add_item_unsafe("banana")` appends to that
  **same** list again, incorrectly returning `['apple', 'banana']`.
- `add_item_safe("apple")` builds a brand-new list, since `items is
  None` is `True`, returning `['apple']`. `add_item_safe("banana")`
  builds another brand-new list, correctly returning `['banana']` alone.

#### Example output

```text
['apple']
['apple', 'banana']
['apple']
['banana']
```

#### Why this solution works

`None` is immutable and safe to reuse as a default; the real, mutable
list is only ever created fresh inside the function body, once per call
that actually needs one.

#### Common beginner mistakes

- Believing each call to a function with a `[]` default gets its own new
  empty list — it does not; the same list object is reused every time.
- Fixing this by writing `items = items.copy()` instead of checking `is
  None` — this still shares the single default list as the *starting*
  point for every copy, which usually is not the intended behavior
  either.

#### Optional improvement challenge

Call `add_item_safe` a third time, explicitly passing in an existing
list, and confirm that one *is* correctly mutated and returned, since a
real list — not `None` — was supplied.

---

### Question B13 — Hard

#### Problem statement

Refactor a function with a hidden dependency on a global shipping fee so
that the fee is an explicit parameter instead.

#### Concepts practised

Hidden dependencies, explicit parameters (Topic 05; Topic 06).

#### Requirements and expected output

- Define `calculate_total_hidden(order_total)`, reading a global
  `shipping_fee`.
- Define `calculate_total_explicit(order_total, shipping_fee)`.
- Call both and confirm they give the same result.

#### Edge cases to consider

- Nothing about the call `calculate_total_hidden(50)` reveals that
  `shipping_fee` is involved at all — this is exactly the problem being
  fixed.

#### Solution approach

1. Define the global `shipping_fee`.
2. Define the hidden-dependency version.
3. Define the explicit-parameter version.
4. Call both, passing the same global value explicitly to the second.

#### Complete runnable Python solution

```python
shipping_fee = 5

def calculate_total_hidden(order_total):
    return order_total + shipping_fee

def calculate_total_explicit(order_total, shipping_fee):
    return order_total + shipping_fee

print(calculate_total_hidden(50))
print(calculate_total_explicit(50, shipping_fee))
```

#### Explanation

- `calculate_total_hidden(50)` silently reads the global `shipping_fee`
  — a reader cannot tell this just from the call.
- `calculate_total_explicit(50, shipping_fee)` states every value it
  needs directly in the call — a reader (or a test) can understand and
  verify this function completely on its own.

#### Example output

```text
55
55
```

#### Why this solution works

Both give the identical result, but only the explicit version's
dependencies are visible without reading its body — exactly the
"avoid hidden dependencies" habit from Topic 06.

#### Common beginner mistakes

- Assuming the hidden-dependency version is "simpler" because its call
  has fewer arguments — it is simpler to *call*, but harder to *trust*,
  since its real requirements are invisible.
- Forgetting that the explicit version's parameter, also named
  `shipping_fee`, is a **local** parameter — it does not accidentally
  refer to the global variable of the same name; it must still be
  passed in explicitly.

#### Optional improvement challenge

Change the global `shipping_fee` to `8` between the two calls, and
observe that only `calculate_total_hidden`'s result changes.

---

### Question B14 — Hard

#### Problem statement

Write a function that validates a price, raising `TypeError` for the
wrong type and `ValueError` for an out-of-range value, and a caller that
handles both.

#### Concepts practised

Input validation, `raise`, catching multiple specific exception types
(Topic 07).

#### Requirements and expected output

- Define `validate_price(price)`, raising the two specific exceptions.
- Loop over a list including a valid price, a negative price, and text.
- Print whether each was accepted or rejected, and why.

#### Edge cases to consider

- `True` and `False` are technically `int` in Python — checking
  `isinstance(price, bool)` separately prevents them from being
  mistaken for valid numeric prices.

#### Solution approach

1. Check the type first, raising `TypeError` if it is wrong.
2. Check the range next, raising `ValueError` if it is out of range.
3. In the caller, use `try`/`except (TypeError, ValueError)` around
   each check.

#### Complete runnable Python solution

```python
def validate_price(price):
    if not isinstance(price, (int, float)) or isinstance(price, bool):
        raise TypeError(f"Invalid price: {price!r}. Expected a number.")
    if price <= 0:
        raise ValueError(f"Invalid price: {price}. Must be greater than zero.")

prices = [19.99, -5, "twenty"]

for price in prices:
    try:
        validate_price(price)
        print(price, "-> valid")
    except (TypeError, ValueError) as error:
        print(price, "-> rejected:", error)
```

#### Explanation

- `19.99` passes both checks, so `validate_price` returns normally, and
  `"-> valid"` prints.
- `-5` is the right type but out of range, raising `ValueError`, caught
  and printed with its message.
- `"twenty"` is the wrong type entirely, raising `TypeError` first,
  before the range check is ever reached.

#### Example output

```text
19.99 -> valid
-5 -> rejected: Invalid price: -5. Must be greater than zero.
twenty -> rejected: Invalid price: 'twenty'. Expected a number.
```

#### Why this solution works

Raising the exact exception type that matches each specific problem,
and catching exactly those two expected types together, correctly
handles every case in this batch without ever masking an unrelated bug.

#### Common beginner mistakes

- Using a single, broad `except Exception:` instead of naming
  `(TypeError, ValueError)` specifically — this would also silently
  catch a genuine bug elsewhere in the loop.
- Checking the range before the type, which would crash with `TypeError:
  '<=' not supported between instances of 'str' and 'int'` on `"twenty"`
  before ever reaching the intended `ValueError`.

#### Optional improvement challenge

Add a fourth item to `prices`, the boolean `True`, and confirm it is
correctly rejected as the wrong type, not accidentally treated as `1`.

---

### Question B15 — Hard

#### Problem statement

Write three small functions that each safely handle one specific
standard exception: a missing dictionary key, an out-of-range list
position, and division by zero.

#### Concepts practised

`KeyError`, `IndexError`, and `ZeroDivisionError` (Topic 07).

#### Requirements and expected output

- Define `get_safe`, `get_item_safe`, and `divide_safe`.
- Call each once with input that triggers its specific exception.

#### Edge cases to consider

- Each function must catch **only** the one exception type it is
  actually designed for — not a broad `except:`.

#### Solution approach

1. Define each function with a `try`/`except` around its one risky
   operation.
2. Return a clear fallback message from each `except` block.
3. Call all three with failing input.

#### Complete runnable Python solution

```python
def get_safe(dictionary, key):
    try:
        return dictionary[key]
    except KeyError:
        return "Key not found."

def get_item_safe(items, position):
    try:
        return items[position]
    except IndexError:
        return "Position not found."

def divide_safe(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "Cannot divide by zero."

print(get_safe({"a": 1}, "b"))
print(get_item_safe([1, 2, 3], 10))
print(divide_safe(10, 0))
```

#### Explanation

- `get_safe({"a": 1}, "b")` looks up a key, `"b"`, that does not exist,
  raising `KeyError`, caught and replaced with a clear message.
- `get_item_safe([1, 2, 3], 10)` looks up a position that does not
  exist, raising `IndexError`, handled the same way.
- `divide_safe(10, 0)` divides by zero, raising `ZeroDivisionError`,
  also handled the same way.

#### Example output

```text
Key not found.
Position not found.
Cannot divide by zero.
```

#### Why this solution works

Each function anticipates exactly one, specific, expected failure —
using the exact exception type Python itself already raises for that
situation — rather than guessing broadly at what might go wrong.

#### Common beginner mistakes

- Using `.get(key, default)` and a `try`/`except KeyError` together
  redundantly — for a simple case like this, `.get()` alone is usually
  clearer, and `try`/`except` is better reserved for more complex
  handling.
- Catching `Exception` broadly across all three functions instead of
  each one's specific exception, losing the ability to tell the three
  different failure types apart.

#### Optional improvement challenge

Call `get_item_safe` with a negative position such as `-10`, and
predict whether it succeeds or fails before running it.

---

<a id="part-b-advanced"></a>

## Advanced (B16–B20)

These five questions build small, self-contained, function-based
programs, combining validation, `raise`, and `try`/`except`/`else`/
`finally` — including one minimal custom exception.

### Question B16 — Advanced

#### Problem statement

Write a safe shopping-cart updater function that validates the item
name, uses the safe `None` default pattern for the cart, and rejects
invalid items with a clear exception.

#### Concepts practised

Safe `None` default for a mutable list, `raise ValueError`, clear
function contracts (Topics 04, 06, 07).

#### Requirements and expected output

- Define `add_to_cart(item, cart=None)`.
- Raise `ValueError` for an empty or non-string item name.
- Call it twice with no cart argument, and once with an invalid item.

#### Edge cases to consider

- An empty string, `""`, is a `str`, so `isinstance(item, str)` alone
  would not catch it — the emptiness must be checked separately.

#### Solution approach

1. Validate `item` first: must be a non-empty string, or raise
   `ValueError`.
2. Apply the safe `None` default pattern for `cart`.
3. Append the item and return the cart.
4. Call the function three times, including one invalid call inside
   `try`/`except`.

#### Complete runnable Python solution

```python
def add_to_cart(item, cart=None):
    if not isinstance(item, str) or item == "":
        raise ValueError("Item name must be a non-empty string.")
    if cart is None:
        cart = []
    cart.append(item)
    return cart

cart_one = add_to_cart("Apples")
cart_two = add_to_cart("Bread")

print("Cart one:", cart_one)
print("Cart two:", cart_two)

try:
    add_to_cart("")
except ValueError as error:
    print("Rejected:", error)
```

#### Explanation

- `add_to_cart("Apples")` and `add_to_cart("Bread")` each supply no
  `cart`, so each gets its own brand-new list — thanks to the safe
  `None` pattern, they do not share one.
- `add_to_cart("")` fails the validation check first, raising
  `ValueError` before `cart` is even considered; the caller's
  `try`/`except` catches it and prints the message.

#### Example output

```text
Cart one: ['Apples']
Cart two: ['Bread']
Rejected: Item name must be a non-empty string.
```

#### Why this solution works

Validating the input *before* touching `cart` at all means an invalid
call never has a chance to partially succeed; the safe default pattern
then guarantees every valid call gets an independent cart unless one was
explicitly supplied.

#### Common beginner mistakes

- Writing `cart=[]` instead of `cart=None`, reintroducing the shared
  mutable default bug from Question B12.
- Validating `item` *after* checking `cart is None`, which would still
  work here, but puts the input check in a less obvious, less
  conventional place.

#### Optional improvement challenge

Call `add_to_cart("Milk", cart_one)` afterward, and confirm it correctly
appends to the *existing* `cart_one` list instead of starting a new one.

---

### Question B17 — Advanced

#### Problem statement

Write a discount engine that rejects an invalid discount percentage with
a clear exception, and process a batch of requests using
`try`/`except`/`else`/`finally`.

#### Concepts practised

`raise ValueError`, `try`/`except`/`else`/`finally` together (Topic 07).

#### Requirements and expected output

- Define `calculate_discounted_price(price, discount_percentage)`,
  raising `ValueError` outside the 0–100 range.
- Loop over three requests, one of which is invalid.
- Print the result, or the rejection, and a "processed" message either
  way.

#### Edge cases to consider

- `finally` must run for **every** request, whether it succeeded or was
  rejected — this is exactly what makes `finally` different from just
  adding a print statement at the end of `try`.

#### Solution approach

1. Define the function with a guard `if` that raises `ValueError`.
2. Loop over the requests inside `try`, using `else` for the success
   message and `except` for the rejection.
3. Print a `finally` message after every request, regardless of outcome.

#### Complete runnable Python solution

```python
def calculate_discounted_price(price, discount_percentage):
    if discount_percentage < 0 or discount_percentage > 100:
        raise ValueError(
            f"Invalid discount_percentage: {discount_percentage}. Expected 0-100."
        )
    return price * (1 - discount_percentage / 100)

requests = [(100, 20), (50, 150), (80, 10)]

for price, discount in requests:
    try:
        final_price = calculate_discounted_price(price, discount)
    except ValueError as error:
        print("Skipped:", error)
    else:
        print(f"Final price: ${final_price:.2f}")
    finally:
        print("Processed one request.")
```

#### Explanation

- `(100, 20)` succeeds: `try` completes with no exception, so `else`
  runs, printing the final price; `finally` then runs too.
- `(50, 150)` fails validation: `except` catches the `ValueError` and
  prints the rejection; `else` is skipped, but `finally` still runs.
- `(80, 10)` succeeds again, following the same path as the first
  request.

#### Example output

```text
Final price: $80.00
Processed one request.
Skipped: Invalid discount_percentage: 150. Expected 0-100.
Processed one request.
Final price: $72.00
Processed one request.
```

#### Why this solution works

`else` cleanly separates "what to do on success" from the risky
calculation itself, while `finally` guarantees the "processed" message
appears exactly once per request, no matter the outcome.

#### Common beginner mistakes

- Putting the success message inside `try` instead of `else` — this
  would still work here, but would also be (harmlessly) "protected" by
  the `except`, blurring the line between the risky code and its
  success-only follow-up.
- Forgetting that `finally` runs even when `except` handled the
  problem — some beginners expect `finally` to run only on the
  successful path.

#### Optional improvement challenge

Add a fourth request with a negative discount, such as `(60, -5)`, and
confirm it is rejected by the same `ValueError` check.

---

### Question B18 — Advanced

#### Problem statement

Write a registration validator that checks a name and an age, collecting
every error found instead of stopping at the first one.

#### Concepts practised

Validation, `try`/`except ValueError` for parsing, collecting multiple
errors (Topic 07).

#### Requirements and expected output

- Define `validate_registration(data)`, returning a list of error
  messages.
- Check a submission that is valid, and one that fails both checks at
  once.

#### Edge cases to consider

- For this exercise, assume `data["age"]`, if present, is a string
  representation of a whole number or another value accepted by
  `int()`. (Other values, such as `None`, would raise `TypeError`
  instead of `ValueError`, which this exercise does not handle.)
- A missing `"age"` key and an unparseable `"age"` value are two
  different problems and must be checked separately: first whether the
  key exists at all, then whether its value can be parsed.

#### Solution approach

1. Check for a missing or empty name, appending an error if found.
2. Check for a missing age key first; if present, try to parse it,
   appending an error either way it can fail.
3. Return the collected list of errors.

#### Complete runnable Python solution

```python
def validate_registration(data):
    errors = []

    if "name" not in data or data["name"] == "":
        errors.append("Name is required.")

    if "age" not in data:
        errors.append("Age is required.")
    else:
        try:
            age = int(data["age"])
            if age < 0 or age > 120:
                errors.append(f"Age must be between 0 and 120, got {age}.")
        except ValueError:
            errors.append(f"Age must be a whole number, got '{data['age']}'.")

    return errors

submissions = [
    {"name": "Ada", "age": "30"},
    {"name": "", "age": "abc"},
]

for submission in submissions:
    errors = validate_registration(submission)
    if errors:
        print("Rejected:", errors)
    else:
        print("Accepted.")
```

#### Explanation

- The first submission has a real name and a parseable, in-range age, so
  `errors` stays empty, and `"Accepted."` prints.
- The second submission has a blank name (one error) and an
  unparseable age (a second error, caught via `try`/`except
  ValueError`) — both are collected into the same list and reported
  together.

#### Example output

```text
Accepted.
Rejected: ['Name is required.', "Age must be a whole number, got 'abc'."]
```

#### Why this solution works

Collecting every problem into a list, instead of `raise`-ing on the
first one found, lets a caller see every issue with a submission at
once, rather than fixing and resubmitting repeatedly to discover the
next one.

#### Common beginner mistakes

- Using `raise` for each individual problem instead of appending to a
  list, which would stop at the very first error and hide any others.
- Trying `int(data["age"])` without first checking `"age" not in data`,
  which would raise `KeyError` instead of the intended, clearer
  "Age is required." message.

#### Optional improvement challenge

Add a check for an `"email"` field, requiring it to contain an `"@"`
character, following the same error-collecting pattern.

---

### Question B19 — Advanced

#### Problem statement

Write a budget checker that rejects a withdrawal larger than the current
balance, and process a sequence of withdrawal attempts safely.

#### Concepts practised

`raise ValueError`, `try`/`except`/`else`/`finally` updating state only
on success (Topic 07; Topic 06).

#### Requirements and expected output

- Define `withdraw(balance, amount)`, raising `ValueError` if the amount
  exceeds the balance.
- Attempt two withdrawals: one that succeeds, one that fails.
- Only update the real `balance` variable when a withdrawal succeeds.

#### Edge cases to consider

- The outer `balance` variable must **not** change when a withdrawal is
  rejected — only `else` (success only) should update it, never
  `except`.

#### Solution approach

1. Define `withdraw` as a pure function: it never changes `balance`
   itself, only returns what the new balance *would* be.
2. In the caller, use `try`/`except`/`else`/`finally`: update `balance`
   only inside `else`.
3. Print a "transaction attempt complete" message every time, in
   `finally`.

#### Complete runnable Python solution

```python
def withdraw(balance, amount):
    if amount > balance:
        raise ValueError(f"Cannot withdraw {amount}; balance is only {balance}.")
    return balance - amount

balance = 100

for amount in [30, 200]:
    try:
        new_balance = withdraw(balance, amount)
    except ValueError as error:
        print("Transaction failed:", error)
    else:
        balance = new_balance
        print("New balance:", balance)
    finally:
        print("Transaction attempt complete.")
```

#### Explanation

- Withdrawing `30` succeeds: `withdraw` returns `70`, `else` runs,
  updating `balance` to `70` and printing it; `finally` then runs.
- Withdrawing `200` fails, since it exceeds the current balance (`70`
  by now): `except` catches the `ValueError` and prints the failure;
  `else` is skipped, so `balance` is correctly **not** changed;
  `finally` still runs.

#### Example output

```text
New balance: 70
Transaction attempt complete.
Transaction failed: Cannot withdraw 200; balance is only 70.
Transaction attempt complete.
```

#### Why this solution works

Because `withdraw` is pure (it never mutates `balance` itself, only
returns a computed value), the caller has full, explicit control over
*when* `balance` actually changes — exactly once, only inside `else`,
only on genuine success.

#### Common beginner mistakes

- Updating `balance` inside `try`, before confirming success — if
  `withdraw` raised partway through a more complex function, `balance`
  could end up updated incorrectly.
- Making `withdraw` itself update a global `balance` directly, instead
  of returning the new value — this would reintroduce the hidden-global
  dependency risk from Question B13.

#### Optional improvement challenge

Add a third withdrawal attempt for exactly the remaining balance amount,
and confirm it succeeds, reducing the balance to zero.

---

### Question B20 — Advanced

#### Problem statement

Write a minimal custom exception for an invalid order-status transition,
and use it in a function-based state-transition validator.

#### Concepts practised

One minimal custom exception, `raise`, `try`/`except` (Topic 07, Section
8).

#### Requirements and expected output

- Define `InvalidTransitionError(Exception)` using only `pass`.
- Define `change_order_status(current_status, requested_status)`,
  raising it for any transition not in an allowed map.
- Process a sequence of requested transitions, one of which is invalid.

#### Edge cases to consider

- Rejecting an invalid transition must **not** change `status` — the
  next attempted transition should still start from the last
  successfully reached status, not the rejected one.

#### Solution approach

1. Define the minimal custom exception.
2. Define the transition function using a dictionary of allowed
   next-statuses.
3. Loop through requested transitions, updating `status` only on
   success.

#### Complete runnable Python solution

```python
class InvalidTransitionError(Exception):
    pass

def change_order_status(current_status, requested_status):
    allowed_next = {"NEW": "PAID", "PAID": "SHIPPED", "SHIPPED": "DELIVERED"}

    if requested_status != allowed_next.get(current_status):
        raise InvalidTransitionError(
            f"Cannot go from {current_status} to {requested_status}."
        )
    return requested_status

status = "NEW"
requested_sequence = ["PAID", "DELIVERED", "SHIPPED"]

for requested_status in requested_sequence:
    try:
        status = change_order_status(status, requested_status)
        print("Status is now:", status)
    except InvalidTransitionError as error:
        print("Rejected:", error)
```

#### Explanation

- `"NEW" -> "PAID"` is allowed (`allowed_next["NEW"]` is `"PAID"`), so
  `status` updates to `"PAID"`.
- `"PAID" -> "DELIVERED"` is **not** allowed (`allowed_next["PAID"]` is
  `"SHIPPED"`, not `"DELIVERED"`), so `InvalidTransitionError` is
  raised and caught; `status` stays `"PAID"`.
- `"PAID" -> "SHIPPED"` is then attempted (correctly starting from the
  still-`"PAID"` status) and succeeds.

#### Example output

```text
Status is now: PAID
Rejected: Cannot go from PAID to DELIVERED.
Status is now: SHIPPED
```

#### Why this solution works

`class InvalidTransitionError(Exception): pass` is the smallest possible
way to give this specific domain rule its own clear, catchable name —
far more readable in the `except` clause than a generic `ValueError`
would have been, and `status` is only ever reassigned on a genuinely
successful transition.

#### Common beginner mistakes

- Updating `status` before confirming the transition succeeded, which
  would incorrectly "accept" an invalid transition.
- Creating a custom exception for every possible error in a program,
  instead of reserving one for a rule — like this one — that genuinely
  deserves its own name.

#### Optional improvement challenge

Add a `"CANCELLED"` status reachable from any current status, and update
`allowed_next` and the validation logic to support it.

---
