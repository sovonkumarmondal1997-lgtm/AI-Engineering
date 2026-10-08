# Conditionals, Guards, and Boolean Logic

## Why this topic matters

Every useful program has to make decisions: whether a customer is old
enough to buy something, whether a password is strong enough, whether a
traffic light means "stop" or "go." Until now, your programs have mostly
run every line, in order, every single time. This lesson is about
**control flow**: the tools that let a program choose which lines to run,
based on real data, instead of blindly running everything the same way
every time. You already saw a first, informal preview of some of this in
Module 1.1. This lesson gives it a complete, formal treatment, and adds
two new ideas beginners are not usually shown early enough: **guard
conditions**, which keep decision-heavy code flat and readable, and
Python's modern `match` statement.

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain what control flow is and why programs need to make decisions.
- Write Boolean expressions and explain what makes a value `True` or
  `False`.
- Write `if`, `if`/`else`, and `if`/`elif`/`else` statements correctly.
- Combine conditions with `and`, `or`, and `not`, use parentheses to make
  the order of evaluation clear, and explain short-circuit evaluation in
  plain terms.
- Write a **guard condition** that checks for invalid or special-case
  input early, and explain why guards keep code flatter and easier to
  read than deeply nested `if` statements.
- Write a simple `match` statement using literal values and the `_`
  default case, and explain when it needs a modern Python version.
- Decide, for a given problem, whether an `if`/`elif` chain or a `match`
  statement is the clearer choice.

## Prerequisites

- [Sequence, Selection, Iteration, and Abstraction](../01-Computational-Thinking-and-Program-Design/04-sequence-selection-iteration-and-abstraction.md) —
  your first, informal look at `if`/`elif`/`else` and `and`/`or`/`not`;
  this lesson gives all of it a complete, formal treatment.
- [Variables, Basic Types, and None](../02-Python-Core-Language-and-Data-Types/02-variables-basic-types-and-none.md) —
  the `bool` type and `None`, both used throughout this lesson.
- [Operators and Precedence](../02-Python-Core-Language-and-Data-Types/03-operators-and-precedence.md) —
  comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`), `and`, `or`,
  `not`, and `is None`, all reused directly here.

## Key terms

| Term | Plain-English definition |
|---|---|
| **Control flow** | The order in which a program's statements actually run, including any choices about which statements to skip or repeat. |
| **Branch** | One possible path a program can take when it reaches a decision point. |
| **Boolean expression** | An expression that evaluates to exactly `True` or `False`. |
| **Condition** | A Boolean expression used to decide whether a block of code should run. |
| **`if` statement** | A statement that runs a block of code only when its condition is `True`. |
| **`elif`** | Short for "else if"; introduces another condition to check only if every condition above it was `False`. |
| **`else`** | Introduces a block that runs only when every `if`/`elif` condition above it was `False`; it has no condition of its own. |
| **Boolean operator** | `and`, `or`, or `not`: an operator that combines or inverts `True`/`False` values. |
| **Short-circuit evaluation** | Python's habit of stopping partway through `and`/`or` as soon as the final result is already certain, without checking the remaining parts. |
| **Guard condition** | A condition, usually checked early, that handles an invalid or special-case input so the rest of the code can assume "normal" data. |
| **Nested code** | Code placed inside another block, which is itself inside another block, and so on; too much nesting makes code hard to follow. |
| **`match` statement** | A Python statement that compares one value against a list of patterns, one `case` at a time, and runs the block under the first match. |
| **`case`** | One possible pattern inside a `match` statement, paired with the block to run if the value matches it. |
| **Wildcard pattern (`_`)** | A special `case` pattern that matches anything at all; conventionally used as the default, "none of the above" case. |

## Step-by-step explanation

### 1. What control flow is

By default, Python runs a program's statements **in order, top to
bottom**, exactly once each. This default is called **sequence**, and you
already met it in Module 1.1. But real programs need more than "always do
the same fixed list of steps." A checkout program should only apply a
discount *if* a coupon was entered. A login screen should only welcome a
user *if* their password was correct. **Control flow** is the general
name for every tool that lets a program's statements run in something
other than a fixed, always-identical order — skipping some statements,
choosing between alternatives, or repeating others. This lesson covers
the tools for *choosing* between alternatives; the next lesson,
[For/While Loops and Loop Control](02-for-while-loops-and-loop-control.md),
covers the tools for *repeating* statements.

### 2. Boolean values and Boolean expressions

Every decision a program makes eventually comes down to a single `bool`
value: `True` or `False`. A **Boolean expression** is any expression that
evaluates to one of these two values. You have already built Boolean
expressions with comparison operators:

```python
print(5 > 3)          # True
print(5 == 6)          # False
print("cat" in "concatenate")   # True
```

`5 > 3`, `5 == 6`, and `"cat" in "concatenate"` are all Boolean
expressions — Python evaluates each one down to exactly `True` or
`False`, nothing else. Control flow tools like `if` are built entirely on
top of this one idea: "evaluate this expression, then act differently
depending on whether it came out `True` or `False`."

The expression `item in collection` tests **membership**: it is `True`
when `item` is found inside `collection` (a substring of a string, or an
element of a list, set, or similar collection), and `False` otherwise:

```python
role = "admin"

if role in {"admin", "editor"}:
    print("Access allowed")
```

```text
Access allowed
```

#### Truth-value testing

An `if` condition does not have to be the Boolean object `True` or
`False` itself. Python evaluates the expression and then **truth-tests**
the result: every value counts as either "truthy" (treated like `True`)
or "falsey" (treated like `False`).

```python
if "hello":
    print("runs")

if []:
    print("does not run")

if 0:
    print("does not run")
```

```text
runs
```

Common falsey values are `False`, `None`, `0`, `""` (the empty string),
and empty collections such as `[]`. Almost everything else is truthy,
including non-empty strings like `"hello"`.

### 3. `if` statements

An **`if` statement** runs an indented block of code only when its
condition evaluates to `True`. If the condition is `False`, the block is
skipped entirely, and the program continues after it:

```python
temperature = 35

if temperature > 30:
    print("It's a hot day.")
```

`temperature > 30` is the condition. Because `35 > 30` is `True`, the
indented `print(...)` line runs. If `temperature` had instead been `20`,
the condition would be `False`, the `print(...)` line would never run,
and the program would simply move on to whatever comes after the `if`
block, with no error and no output from this statement at all.

### 4. `if` / `else` statements

Often you want to do one thing when a condition is `True` and a
*different* thing when it is `False`. Adding an **`else`** block covers
exactly that second case:

```python
age = 16

if age >= 18:
    print("You may vote.")
else:
    print("You may not vote yet.")
```

Python checks `age >= 18` first. Since `16 >= 18` is `False`, the `if`
block is skipped, and the `else` block runs instead, printing
`You may not vote yet.` Exactly one of the two blocks runs, never both,
and never neither — `else` has no condition of its own; it simply means
"in every other case."

### 5. `if` / `elif` / `else` statements

When there are more than two possible outcomes, add one or more
**`elif`** ("else if") blocks between `if` and `else`:

```python
score = 82

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"

print("Grade:", grade)
```

```text
Grade: B
```

Python checks each condition **top to bottom** and runs the block under
the **first** one that is `True`, then skips every remaining `elif` and
`else` entirely, even if a later condition would also have been `True`.
Here, `score >= 90` is `False` (`82 >= 90` is `False`), so Python checks
`score >= 80` next, which is `True` (`82 >= 80`), so `grade = "B"` runs,
and the `elif score >= 70:` and `else:` blocks are never even checked.
This is why the conditions are written from highest to lowest: if they
were written smallest first (`score >= 70` before `score >= 90`), a score
of `95` would incorrectly stop at the very first, too-broad condition.
The final `else` always catches everything not matched by any condition
above it — here, any score below `70`.

Branches can also overlap in a way that makes a later one unreachable:

```python
score = 95

if score >= 70:
    print("C or better")
elif score >= 90:
    print("A")
```

```text
C or better
```

Every score of `90` or more is already caught by `score >= 70`, so the
`elif score >= 90:` branch can never run.

### 6. Comparisons and Boolean operators

#### Chained comparisons

Python lets you chain comparisons to test a range directly:

```python
age = 25

if 18 <= age < 65:
    print("Working-age range")
```

```text
Working-age range
```

`18 <= age < 65` means `18 <= age` **and** `age < 65`, and it is clearer
than writing `age >= 18 and age < 65`.

#### Equality vs identity

```text
==   # equality: values compare equal
is   # identity: the two references refer to the same object
```

`None` is a single, unique object, so the conventional way to check for
it is `value is None`, which asks "is this the `None` object?" You do
not switch to `is` for ordinary value comparisons; keep using `==` for
those.

#### `and`, `or`, and `not`

You can combine several conditions into one using the **Boolean
operators** from
[Operators and Precedence](../02-Python-Core-Language-and-Data-Types/03-operators-and-precedence.md):
`and` (both sides must be `True`), `or` (at least one side must be
`True`), and `not` (flips `True` to `False`, and back).

```python
has_ticket = True
is_on_time = False

if has_ticket and is_on_time:
    print("Boarding allowed.")
else:
    print("Boarding denied.")
```

```text
Boarding denied.
```

`has_ticket and is_on_time` is `True and False`, which is `False`, so the
`else` block runs.

#### Parentheses for clarity

When a condition combines `and`, `or`, and comparisons in one line,
**parentheses** make the intended grouping obvious to any reader, instead
of relying on them to recall precedence rules:

```python
age = 15
has_guardian = True

is_eligible = age >= 18 or (age >= 13 and has_guardian)
print(is_eligible)
```

```text
True
```

Here, `age >= 13 and has_guardian` is grouped explicitly with
parentheses, showing clearly that it is checked as one combined unit,
before being combined with `or`. Even where Python's own precedence rules
would already group things this way, writing the parentheses removes any
doubt for a human reader.

#### Short-circuit evaluation, in simple terms

Python does not always evaluate every part of an `and`/`or` expression.
It stops as soon as the final answer is already certain — this is called
**short-circuit evaluation**. For `and`, if the left side is `False`, the
whole expression must be `False` no matter what the right side is, so
Python never even looks at the right side:

```python
denominator = 0

if denominator != 0 and 10 / denominator > 1:
    print("Result is greater than 1.")
else:
    print("Cannot safely check that (denominator may be zero).")
```

```text
Cannot safely check that (denominator may be zero).
```

`denominator != 0` is `False` (because `denominator` really is `0`), so
Python already knows the whole `and` expression must be `False` — it
never evaluates `10 / denominator`, and no error occurs, even though
dividing by zero would normally crash the program. Placing the safe check
*first* in an `and` expression, relying on short-circuiting to skip the
risky part, is a common, deliberate pattern. `or` short-circuits the
opposite way: if the left side is already `True`, Python never bothers
checking the right side, since the whole expression is already known to
be `True`.

Short-circuiting has a second consequence: `and` and `or` do not
necessarily return `True` or `False`. They return one of their
**operands**:

```python
print(False and "hello")
print(True and "hello")
print("" or "fallback")
print("Python" or "fallback")
```

```text
False
hello
fallback
Python
```

- `x and y` returns `x` if `x` is falsey; otherwise it evaluates and
  returns `y`.
- `x or y` returns `x` if `x` is truthy; otherwise it evaluates and
  returns `y`.

This is the same short-circuit rule as above: Python stops at `x` when
`x` already decides the result, and that operand is what you get back.

### 7. Guard conditions

A **guard condition** checks for invalid, missing, or special-case input
**early**, before the "normal" logic runs, so the rest of the code can
simply assume the data is already sensible. Guards matter because,
without them, checks tend to pile up as deeply **nested** `if`
statements, which get harder to read with every extra level:

```python
username = "ab"

if username != "":
    if username.isalnum():
        if len(username) >= 3:
            print("Username accepted:", username)
        else:
            print("Error: username must be at least 3 characters.")
    else:
        print("Error: username must contain only letters and numbers.")
else:
    print("Error: username cannot be empty.")
```

```text
Error: username must be at least 3 characters.
```

This works, but notice how far to the right the "normal," successful case
(`print("Username accepted:", ...)`) ends up — three levels of
indentation deep, buried behind three separate conditions, each one
undone by its own `else`. As more checks are added, this shape only gets
worse. The **guard-style** rewrite checks the bad cases first, one after
another with `elif`, so the successful case stays at the *top level*,
easy to find at the very bottom.

A quick terminology note: **guard-style branching** means checking an
invalid, exceptional, or special case early. A **guard clause** is a
guard that also exits the current control-flow path early, for example
with `return`, `raise`, `continue`, or `break` where appropriate. The
`elif` chain below is guard-style branching; true guard clauses appear
once you have functions and loops.

```python
username = "ab"

if username == "":
    print("Error: username cannot be empty.")
elif not username.isalnum():
    print("Error: username must contain only letters and numbers.")
elif len(username) < 3:
    print("Error: username must be at least 3 characters.")
else:
    print("Username accepted:", username)
```

```text
Error: username must be at least 3 characters.
```

Both versions print exactly the same result for the same input, but the
second version never nests more than one level deep, no matter how many
checks are added — each new invalid case is just one more `elif` at the
same level, not one more level of nesting. This is the core idea behind a
guard: **handle the exceptions first, so the main path stays simple and
unindented.** Once you reach
[Functions, Parameters, and Return Values](03-functions-parameters-and-return-values.md),
you will see guards written using `return` to exit a function
immediately on bad input, which is even more direct — but the flattening
benefit you just saw with `elif` is exactly the same idea, and works
perfectly well outside of functions too.

### 8. Match-style branching

Python also provides a **`match` statement**, which compares one value
against a list of patterns, one **`case`** at a time, and runs the block
under the first pattern that matches. This lesson only uses the simplest
form: matching a value against exact, literal options, with a final `_`
**wildcard pattern** as the default.

```python
light_color = "yellow"

match light_color:
    case "red":
        print("Stop")
    case "yellow":
        print("Prepare to stop")
    case "green":
        print("Go")
    case _:
        print("Unknown signal")
```

```text
Prepare to stop
```

Python checks `light_color` against each `case` pattern, top to bottom,
exactly as `if`/`elif` checks its conditions. `case "yellow":` matches,
so its block runs, and every other `case` is skipped — only one `case`
block ever runs per `match`. `case _:` matches absolutely anything, so it
acts as the "none of the above" default, exactly like a final `else`.
**A version note:** `match` was added to Python in version 3.10; if you
are ever using an older Python, `if`/`elif`/`else` is the only option,
and even on modern Python, plain `if`/`elif`/`else` is never wrong —
`match` is an alternative for a specific situation, not a required
replacement.

### 9. Choosing between `if`/`elif` and `match`

Both tools pick one branch out of several, but they suit different
situations:

- Use **`if`/`elif`** when you are checking **comparisons or ranges** —
  anything using `>`, `<`, `>=`, `<=`, `and`, `or`, or `not`. `match`'s
  simple literal patterns cannot express "is this number 80 or above";
  `if score >= 80:` can.
- Use **`match`** when you have a **known, fixed set of exact values** to
  branch on — a color name, a menu choice, a status code — since lining
  up several `case` blocks is often easier to scan than a long chain of
  `elif value == ...:` comparisons.

```python
temperature = 28

if temperature > 30:
    forecast = "hot"
elif temperature > 20:
    forecast = "warm"
else:
    forecast = "cool"

print(forecast)

day_name = "Wed"

match day_name:
    case "Sat" | "Sun":
        schedule = "Weekend"
    case _:
        schedule = "Weekday"

print(schedule)
```

```text
warm
Weekday
```

`forecast` is decided with `if`/`elif`, because it depends on *ranges* of
temperature — the simple literal patterns taught in this lesson cannot
directly express "greater than 20," so `if`/`elif` is clearer here
(Python's full pattern-matching system has more features, which this
lesson intentionally defers).
`schedule`, by contrast, only ever depends on an *exact* day name, so
`match` reads clearly — and this example also shows that a single `case`
can list more than one literal option, separated by `|` (read as "or"),
to match several exact values with one block.

## Examples

### Example 1 — Driving permit eligibility (`if`/`elif`/`else` with `and`)

```python
age = 16
has_guardian_consent = True

if age >= 18:
    print("You can get a full driving permit.")
elif age >= 16 and has_guardian_consent:
    print("You can get a learner's permit with guardian consent.")
else:
    print("You are not yet eligible for a driving permit.")
```

**Plain-English explanation:**

- `age = 16` and `has_guardian_consent = True` store the two facts this
  decision depends on.
- `age >= 18` is `False` (16 is not 18 or more), so Python moves on to
  the `elif`.
- `age >= 16 and has_guardian_consent` requires *both* parts to be
  `True`: `age >= 16` is `True`, and `has_guardian_consent` is already
  `True`, so the whole `elif` condition is `True`.
- Because this `elif` was the first `True` condition Python found, its
  block runs, printing `You can get a learner's permit with guardian
  consent.`, and the final `else` is never reached.

**Expected output:**

```text
You can get a learner's permit with guardian consent.
```

### Example 2 — Password rule checks with a guard chain

```python
candidate_passwords = ["", "short1", "longenoughbutnodigits", "hunter22"]

for password in candidate_passwords:
    has_min_length = len(password) >= 8

    has_digit = False
    for character in password:
        if character.isdigit():
            has_digit = True

    if password == "":
        print(password, "-> Error: password cannot be empty.")
    elif not has_min_length:
        print(password, "-> Error: password must be at least 8 characters long.")
    elif not has_digit:
        print(password, "-> Error: password must contain at least one digit.")
    else:
        print(password, "-> Password meets all the rules.")
```

**Plain-English explanation:**

- `candidate_passwords` holds four example passwords, deliberately
  chosen to trigger every branch of the guard chain once each; the outer
  `for` loop (previewed in Module 1.1, formalized in the next lesson)
  simply repeats the whole check once per password.
- `has_min_length` and `has_digit` are computed first, using a small
  inner `for` loop to check each character for a digit — no digit means
  `has_digit` stays `False`.
- The guard chain checks the **worst** problem first (an empty password),
  then the next problem (too short), then the next (no digit), and only
  reaches `else` — "password meets all the rules" — once every earlier
  `elif` has failed to match. This is the same flattening pattern from
  Section 7, now checking three different invalid cases instead of one.

**Expected output:**

```text
 -> Error: password cannot be empty.
short1 -> Error: password must be at least 8 characters long.
longenoughbutnodigits -> Error: password must contain at least one digit.
hunter22 -> Password meets all the rules.
```

### Example 3 — Traffic light instructions with `match`

```python
light_colors = ["red", "yellow", "green", "flashing yellow"]

for light_color in light_colors:
    match light_color:
        case "red":
            instruction = "Stop"
        case "yellow":
            instruction = "Prepare to stop"
        case "green":
            instruction = "Go"
        case _:
            instruction = "Proceed with caution"
    print(light_color, "->", instruction)
```

**Plain-English explanation:**

- `light_colors` lists four possible signals, including one,
  `"flashing yellow"`, that does not match any of the three named
  `case` patterns.
- For each color, `match light_color:` compares it against `"red"`,
  `"yellow"`, and `"green"` in order. The first three colors each match
  one specific `case` exactly.
- `"flashing yellow"` matches none of the three literal cases, so it
  falls through to `case _:`, the wildcard default, producing
  `"Proceed with caution"` — proof that `_` really does catch anything
  not explicitly listed above it.

**Expected output:**

```text
red -> Stop
yellow -> Prepare to stop
green -> Go
flashing yellow -> Proceed with caution
```

### Example 4 — An optional value with `None`

```python
customer_referral_code = None
bonus_points = 0

if customer_referral_code is None:
    print("No referral code was used.")
elif customer_referral_code == "":
    print("Referral code field was left blank on purpose.")
else:
    bonus_points = 50
    print("Referral code", customer_referral_code, "applied.")

print("Bonus points earned:", bonus_points)
```

**Plain-English explanation:**

- `customer_referral_code = None` represents "the customer never
  interacted with the referral field at all" — genuinely different from
  `""`, which would mean "the field exists and is known to be blank," as
  you learned in
  [Variables, Basic Types, and None](../02-Python-Core-Language-and-Data-Types/02-variables-basic-types-and-none.md).
- `if customer_referral_code is None:` uses the `is None` rule from
  [Operators and Precedence](../02-Python-Core-Language-and-Data-Types/03-operators-and-precedence.md)
  to check specifically for "never provided." Since that is exactly the
  case here, this branch runs, and `bonus_points` stays at its starting
  value, `0`.
- The `elif` and `else` branches are never reached this time, but they
  show how the same guard-style chain could also handle a
  deliberately blank code, or a real one worth `50` bonus points — three
  genuinely different situations that plain truthiness (`if
  customer_referral_code:`) could not tell apart, since `None` and `""`
  are both falsy.

**Expected output:**

```text
No referral code was used.
Bonus points earned: 0
```

## Common beginner mistakes

- **Writing `if age = 18:` instead of `if age == 18:`.** A single `=` is
  assignment; Python raises a `SyntaxError` here, which is a helpful,
  immediate signal that something is wrong, rather than silently doing
  the wrong thing.
- **Ordering `elif` conditions from smallest to largest** in a chain like
  the grade example, which causes a high score to incorrectly match the
  first, too-broad condition instead of the intended one.
- **Forgetting that only one `if`/`elif`/`else` block ever runs.** Once
  Python finds the first `True` condition, it skips every condition and
  block after it, even ones that would also have been `True`.
- **Nesting `if` statements many levels deep** instead of reaching for a
  guard-style `elif` chain, making the "normal," successful case hard to
  find, buried at the far right of the screen.
- **Assuming `match` can check ranges or comparisons.** The literal
  patterns shown in this lesson only match *exact* values; use
  `if`/`elif` for anything involving `>`, `<`, `>=`, or `<=`.
- **Forgetting the trailing `case _:`** in a `match` statement, so a
  value that matches nothing at all silently does nothing, with no
  error and no output — always include a wildcard case unless you have
  deliberately confirmed every possible value is already covered.

## Try it yourself

Do not look up full solutions. Predict the output before running each
one.

1. Write an `if`/`elif`/`else` chain that takes a body temperature (in
   Celsius) and prints `"Fever"` if it is `38.0` or above, `"Normal"` if
   it satisfies `36.0 <= temperature < 38.0`, and `"Low"` otherwise
   (below `36.0`).
2. Using `and`, `or`, and parentheses, write one condition that checks
   whether a customer qualifies for free shipping: either their order
   total is `50` or more, **or** they are a "member" **and** their order
   total is `20` or more. Test it with a few different values.
3. Take the nested `username` example from Section 7 and, without
   changing what it prints, rewrite it as a flat guard chain using
   `elif` — then add one more rule of your own (for example, rejecting a
   username longer than 20 characters).
4. Write a `match` statement that takes a day abbreviation (`"Mon"`
   through `"Sun"`) and prints `"Weekday"` for Monday through Friday and
   `"Weekend"` for Saturday and Sunday, using the `|` pattern from
   Section 9.
5. Write a guard-style check for an optional `middle_name` variable that
   correctly tells apart three cases: the value is `None`, the value is
   an empty string `""`, and the value is real text — printing a
   different message for each.

## Summary

- **Control flow** lets a program choose which statements run, instead of
  always running every line the same way.
- `if` runs a block only when its condition is `True`; `else` covers
  every other case; `elif` adds more conditions in between, checked top
  to bottom, with only the first matching block ever running.
- `and`, `or`, and `not` combine or invert conditions; parentheses make
  the intended grouping explicit, and Python **short-circuits**
  `and`/`or`, skipping evaluation of a part it no longer needs to check.
- A **guard condition** checks bad or special-case input first, using a
  flat `elif` chain, keeping the normal, successful path at the top
  level instead of buried inside several nested `if` statements.
- `match`/`case` compares one value against a list of exact, literal
  patterns, with `_` as the default; it requires Python 3.10 or newer and
  is best suited to a known, fixed set of exact choices, while
  `if`/`elif` remains the right tool for comparisons and ranges.

## Completion checklist

- [ ] I can explain what control flow is, in my own words.
- [ ] I can write `if`, `if`/`else`, and `if`/`elif`/`else` statements
      correctly, and explain why only one block ever runs.
- [ ] I can combine conditions with `and`, `or`, and `not`, use
      parentheses to make grouping clear, and explain short-circuit
      evaluation with an example.
- [ ] I can rewrite a deeply nested `if` statement as a flat guard-style
      `elif` chain, and explain why the flat version is easier to read.
- [ ] I can write a `match` statement with literal cases and a `_`
      default, and explain when it needs a modern Python version.
- [ ] I can explain, with an example, when to choose `if`/`elif` over
      `match`, and vice versa.
- [ ] I have completed the "try it yourself" exercises above.

## Connection to later Applied AI and Agentic AI engineering work

Every AI agent constantly makes exactly this kind of decision: which tool
to call next, whether a model's response is safe to show a user, whether
a piece of input is even valid before spending an expensive model call on
it. Guard conditions are especially important here — validating a tool's
arguments, or checking that a required field was actually provided,
*before* running the rest of the logic, is the same flattening habit you
practiced in Section 7, just applied to agent inputs instead of a
username. `match` statements are also a natural fit for routing a fixed
set of tool names or intent categories to the right handler, once you are
writing code that decides "which of my agent's known tools should run
now."
