# Conditionals, Guards, and Boolean Logic — Study Guide and Complete Exercise Solutions

**Source lesson:** `01-conditionals-guards-and-boolean-logic.md`  
**Roadmap location:** Stage 1 — Programming & Computational Thinking → Module 03 — Control Flow, Functions, Scope, and Errors → Lesson 01  
**Scope:** This guide teaches the concepts and examples in the supplied lesson, then solves all five “Try it yourself” exercises. It intentionally stays within the lesson's scope.

---

# Part A — Complete lesson summary and teaching guide

## 1. Why control flow matters

A basic Python program normally executes statements from top to bottom, one after another. This is called **sequence**.

Real programs cannot always execute the same instructions in the same way. They need to make decisions:

- A checkout system applies a discount only if a coupon is valid.
- A login system welcomes a user only if the password is correct.
- A data pipeline accepts a record only if required values are present.
- An AI agent chooses a tool only when the request and its arguments meet the required conditions.

**Control flow** is the order in which statements actually execute, including decisions about which statements to run and which to skip. This lesson focuses on selection: choosing between alternative paths. Repetition is handled by loops in the next lesson.

A **branch** is one possible path through a decision.

## 2. Boolean values and Boolean expressions

Python's Boolean type is `bool`. It has exactly two Boolean values:

- `True`: a condition is satisfied.
- `False`: a condition is not satisfied.

A **Boolean expression** is an expression that evaluates to `True` or `False`.

```python
print(5 > 3)                    # True
print(5 == 6)                   # False
print("cat" in "concatenate")   # True
```

Explanation:

1. `5 > 3` asks whether 5 is greater than 3.
2. `5 == 6` asks whether the two values are equal. They are not.
3. `"cat" in "concatenate"` checks whether `"cat"` occurs inside the larger string.

The `in` operator performs a **membership test**. It can check whether a string contains a substring or whether a collection contains an item.

```python
role = "admin"

if role in {"admin", "editor"}:
    print("Access allowed")
```

The set contains `"admin"` and `"editor"`. Since `role` is `"admin"`, the membership expression is true and the message is printed.

Output:

```text
Access allowed
```

### Truth-value testing: truthy and falsey

An `if` condition does not have to be literally `True` or `False`. Python truth-tests its result.

- A **truthy** value behaves like `True` in a condition.
- A **falsey** value behaves like `False`.

```python
if "hello":
    print("runs")

if []:
    print("does not run")

if 0:
    print("does not run")
```

Output:

```text
runs
```

Common falsey built-in values include:

- `False`
- `None`
- `0`
- `""` (empty string)
- Empty collections such as `[]`, `{}`, and `set()`

Most other ordinary built-in values are truthy. For example, a non-empty string such as `"hello"` is truthy. Custom objects can define their own truth-value behavior, so this list is a practical rule for common built-in values, not a universal rule for every Python object.

## 3. The `if` statement

An `if` statement executes its indented block only when its condition is true.

```python
temperature = 35

if temperature > 30:
    print("It's a hot day.")
```

Step by step:

1. `temperature = 35` stores the number 35.
2. `temperature > 30` evaluates to `True`.
3. Because the condition is true, Python executes the indented `print`.
4. If the temperature were 20, the condition would be false. Python would skip the indented block and continue after it.

Indentation is important: it tells Python which statements belong to the `if` block.

## 4. The `if` / `else` statement

Use `else` when you want one action for a true condition and another action for every other case.

```python
age = 16

if age >= 18:
    print("You may vote.")
else:
    print("You may not vote yet.")
```

Python checks `age >= 18`. Since 16 is less than 18, the condition is false and the `else` block runs.

Exactly one of these two blocks runs:

- `if` runs when its condition is true.
- `else` runs when the `if` condition is false.

`else` has no condition of its own. It means “in every other case.”

## 5. The `if` / `elif` / `else` chain

Use `elif` (“else if”) when there are more than two possible outcomes.

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

Output:

```text
Grade: B
```

How Python evaluates it:

1. Check `score >= 90`. For 82, this is false.
2. Check `score >= 80`. This is true.
3. Assign `"B"` to `grade`.
4. Skip every remaining `elif` and `else` block.

Python checks conditions from top to bottom and runs only the **first matching branch**. It does not continue checking later branches after finding a true condition.

### Why condition order matters

For a grade chain, put the highest threshold first. If `score >= 70` appeared before `score >= 90`, a score of 95 would match the first condition and never reach the A-grade condition.

This is an incorrect ordering:

```python
score = 95

if score >= 70:
    print("C or better")
elif score >= 90:
    print("A")
```

Output:

```text
C or better
```

The second branch is unreachable because every score of 90 or more also satisfies `score >= 70`, and the first branch catches it first.

**Rule:** Order overlapping conditions from the most specific or restrictive condition to the broader one, so the intended branch gets a chance to match.

## 6. Comparisons and Boolean operators

### Chained comparisons

Python can express a range with a chained comparison:

```python
age = 25

if 18 <= age < 65:
    print("Working-age range")
```

`18 <= age < 65` means both of these must be true:

- `18 <= age`
- `age < 65`

It is equivalent to:

```python
age >= 18 and age < 65
```

The chained form is often easier to read.

### Equality (`==`) versus identity (`is`)

These operators answer different questions:

- `==` asks whether two values compare equal.
- `is` asks whether two references point to the exact same object.

For ordinary value comparisons, use `==`.

For checking whether a value is `None`, use the conventional identity check:

```python
if value is None:
    print("No value was supplied.")
```

`None` is a unique singleton object, so `value is None` checks specifically whether the value is that `None` object. Do not replace ordinary equality comparisons with `is`.

### `and`, `or`, and `not`

Boolean operators combine or invert conditions:

| Operator | Meaning |
|---|---|
| `and` | Both sides must be truthy for the combined condition to be truthy. |
| `or` | At least one side must be truthy. |
| `not` | Reverses truth value: truthy becomes false, falsey becomes true. |

Example:

```python
has_ticket = True
is_on_time = False

if has_ticket and is_on_time:
    print("Boarding allowed.")
else:
    print("Boarding denied.")
```

`True and False` is false, so the `else` block prints `Boarding denied.`

### Parentheses make conditions easier to read

When a condition combines multiple operators, parentheses show the intended grouping.

```python
age = 15
has_guardian = True

is_eligible = age >= 18 or (age >= 13 and has_guardian)
print(is_eligible)
```

Output:

```text
True
```

The grouped expression `(age >= 13 and has_guardian)` is true. The whole expression is therefore true because the left side of `or` is not required to be true when the right side is true.

Even when Python's precedence rules would produce the same result without parentheses, parentheses help readers understand the intended logic.

### Short-circuit evaluation

Python sometimes stops evaluating an `and` or `or` expression before reaching its final part. This is called **short-circuit evaluation**.

For `and`:

- If the left side is falsey, the entire expression is already determined to be falsey.
- Python does not evaluate the right side.

For `or`:

- If the left side is truthy, the entire expression is already determined to be truthy.
- Python does not evaluate the right side.

Example: protect division from a zero denominator.

```python
denominator = 0

if denominator != 0 and 10 / denominator > 1:
    print("Result is greater than 1.")
else:
    print("Cannot safely check that (denominator may be zero).")
```

Output:

```text
Cannot safely check that (denominator may be zero).
```

Step by step:

1. `denominator != 0` evaluates to false.
2. The operator is `and`. Both sides would need to be true.
3. The first side is already false, so Python knows the whole expression cannot be true.
4. Python skips `10 / denominator`.
5. No division-by-zero error occurs.

This is a useful safety pattern: put the safe validation first and the potentially risky operation second.

### `and` and `or` can return operands, not just Booleans

A subtle but important detail: `and` and `or` return one of their operands. They do not always return the Boolean objects `True` or `False`.

```python
print(False and "hello")
print(True and "hello")
print("" or "fallback")
print("Python" or "fallback")
```

Output:

```text
False
hello
fallback
Python
```

Rules:

- `x and y` returns `x` if `x` is falsey; otherwise it evaluates and returns `y`.
- `x or y` returns `x` if `x` is truthy; otherwise it evaluates and returns `y`.

This behavior is another result of short-circuiting. Python returns the operand that determines the result.

## 7. Guard conditions and flatter code

A **guard condition** checks invalid, missing, or special-case input early, before normal processing. This lets the normal path assume that earlier checks have passed.

Without guards, code can become deeply nested:

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

Output:

```text
Error: username must be at least 3 characters.
```

The code works, but each condition adds another indentation level. The successful path is buried inside three nested blocks.

A flatter guard-style version checks invalid cases first:

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

Output:

```text
Error: username must be at least 3 characters.
```

The output is the same for the same input, but the structure is easier to read:

1. Reject an empty username.
2. Reject a username containing characters other than letters and numbers.
3. Reject a username shorter than three characters.
4. Otherwise, accept it.

Each invalid case is at the same indentation level. The normal success path is easy to locate.

### Guard-style branching versus a guard clause

These terms are related but not identical:

- **Guard-style branching** checks invalid or exceptional cases early. The `elif` example above is guard-style branching.
- A **guard clause** also exits the current control-flow path early, for example with `return`, `raise`, `continue`, or `break`.

The lesson's `elif` chain demonstrates the flattening idea. Later, when functions and loops are covered, you can use actual guard clauses to exit early.

## 8. Match-style branching

Python's `match` statement compares one value against a series of patterns. Each pattern is introduced by `case`. Python runs the block under the first matching case.

This lesson focuses on exact literal values and the wildcard `_` case.

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

Output:

```text
Prepare to stop
```

Explanation:

1. Python evaluates `light_color`.
2. It compares the value with `"red"`, then `"yellow"`, then `"green"`.
3. `"yellow"` matches, so that block runs.
4. The remaining cases are skipped.
5. `case _` is a wildcard: it matches anything not matched earlier. It acts like the default `else`.

**Version requirement:** `match` was introduced in Python 3.10. It will not run in older Python versions. `if`/`elif`/`else` remains a valid alternative even in modern Python.

## 9. Choosing between `if`/`elif` and `match`

Use `if`/`elif` when decisions depend on comparisons, ranges, or combined Boolean conditions:

```python
temperature = 28

if temperature > 30:
    forecast = "hot"
elif temperature > 20:
    forecast = "warm"
else:
    forecast = "cool"

print(forecast)
```

Output:

```text
warm
```

Use `match` when one value must be compared with a known, fixed set of exact choices:

```python
day_name = "Wed"

match day_name:
    case "Sat" | "Sun":
        schedule = "Weekend"
    case _:
        schedule = "Weekday"

print(schedule)
```

Output:

```text
Weekday
```

The `|` inside a case pattern means “or”: either `"Sat"` or `"Sun"` matches the same block.

In this lesson's simple literal-pattern form, `match` is not for checking whether a number is greater than a threshold. Use `if`/`elif` for ranges. Python's broader pattern-matching features are outside this lesson's scope.

## 10. The four complete lesson examples

### Example 1 — Driving permit eligibility

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

Step by step:

1. Store the age as `16`.
2. Store guardian consent as `True`.
3. Check whether age is at least 18. It is false.
4. Check the second condition: age is at least 16 **and** consent is true.
5. Both parts are true, so the `elif` block runs.
6. The final `else` is skipped.

Output:

```text
You can get a learner's permit with guardian consent.
```

This demonstrates multiple branches and `and`.

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

The outer `for` loop repeats the validation for each candidate password. The inner loop examines each character.

Important statements:

- `len(password) >= 8` checks the minimum length.
- `has_digit = False` starts by assuming no digit has been found.
- `character.isdigit()` checks whether the current character is a digit.
- If a digit is found, `has_digit` becomes `True`.
- The guard chain reports the first failing rule. The success branch runs only if all earlier checks pass.

Output:

```text
 -> Error: password cannot be empty.
short1 -> Error: password must be at least 8 characters long.
longenoughbutnodigits -> Error: password must contain at least one digit.
hunter22 -> Password meets all the rules.
```

These are illustrative validation rules, not a complete production password-security policy.

### Example 3 — Traffic-light instructions with `match`

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

The loop processes each signal. `match` chooses the instruction:

- `"red"` matches the red case.
- `"yellow"` matches the yellow case.
- `"green"` matches the green case.
- `"flashing yellow"` matches none of those exact values, so `_` supplies the default.

Output:

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

The lesson distinguishes three states:

1. `None`: the customer did not provide or interact with the field.
2. `""`: the field is present but deliberately blank.
3. A non-empty string: a referral code was supplied.

The first condition uses `is None` to check the specific `None` object. The second uses `== ""` to check an empty string. Since the current value is `None`, the first branch runs and the points remain zero.

Output:

```text
No referral code was used.
Bonus points earned: 0
```

A simple truthiness test such as `if customer_referral_code:` would treat both `None` and `""` as falsey, so it could not distinguish these two cases.

## 11. Common beginner mistakes

1. **Using assignment instead of equality.** `if age = 18:` is invalid syntax. Use `==` to compare values; use `=` to assign a value.
2. **Putting broad conditions before specific conditions.** In an `elif` chain, an earlier broad condition can catch values intended for a later branch.
3. **Assuming multiple branches run.** Only the first true branch in one `if`/`elif`/`else` chain runs.
4. **Nesting too deeply.** Prefer a flat guard-style chain when checking several invalid cases.
5. **Expecting simple `match` patterns to check ranges.** Use `if`/`elif` for comparisons such as `score >= 80`.
6. **Forgetting the wildcard case.** Without `case _:`, an unmatched value may result in no case block running. Include a default when you need to handle unknown values.

## 12. Connection to Applied AI and Agentic AI

The lesson's decision-making patterns also appear in AI systems:

- Check required tool arguments before invoking a tool.
- Reject invalid user input before making an expensive model call.
- Decide whether a model response meets a safety condition before showing it.
- Route a known intent or tool name to the corresponding handler.

Guard conditions are useful because they validate inputs early and keep the main processing path simple. `match` can be useful when routing a fixed set of known categories or tool names. These are applications of the same Python fundamentals, not new topics required for this lesson.

## 13. Completion checklist

You should be able to:

- Explain control flow and branches.
- Write `if`, `if`/`else`, and `if`/`elif`/`else`.
- Explain why only the first matching branch runs.
- Use `and`, `or`, and `not`.
- Use parentheses to make combined conditions clear.
- Explain short-circuit evaluation and why safe checks should come first.
- Distinguish `==` from `is`, especially `value is None`.
- Rewrite nested conditions as a flat guard-style chain.
- Write a literal-value `match` with a wildcard `_` case.
- Explain that `match` requires Python 3.10 or newer.
- Choose `if`/`elif` for ranges and `match` for fixed exact choices.

---

# Part B — Project-tree and current-level assessment

## 1. Where this lesson sits in the roadmap

The roadmap places this file at:

`Stage 1 — Programming & Computational Thinking / 03-Control-Flow-Functions-Scope-and-Errors / 01-conditionals-guards-and-boolean-logic.md`

The project tree shows that this lesson follows:

- **Module 01 — Computational Thinking and Program Design:** algorithms, values and expressions, input/process/output, sequence/selection/iteration/abstraction, decomposition, preconditions/postconditions/edge cases, pseudocode, and state.
- **Module 02 — Python Core Language and Data Types:** Python files and indentation, variables and basic types, `None`, operators and precedence, strings, lists, tuples, dictionaries, sets, truthiness, and mutability.

It is followed in Module 03 by:

1. `02-for-while-loops-and-loop-control.md`
2. `03-functions-parameters-and-return-values.md`
3. `04-function-arguments-defaults-and-docstrings.md`
4. `05-scope-lifetime-and-global-state.md`
5. `06-pure-functions-and-side-effects.md`
6. `07-exceptions-validation-and-useful-errors.md`

This ordering is sensible: first learn decisions, then repetition, then functions and error handling.

## 2. Overall Stage 1 context

The roadmap describes Stage 1 as a substantial programming foundation with 24 modules, 212 lessons, and 282 files. It includes four stage-level projects:

- Personal Expense Ledger CLI
- Log Investigation and Reliability CLI
- Data Quality and Transformation Pipeline
- Rule-Based Risk Review Engine

The conditionals lesson contributes directly to all four projects. For example, a ledger needs conditional checks for valid transaction categories; a log investigation tool needs severity-based decisions; a data-quality pipeline needs validation branches; and a risk-review engine needs rules that route records into different outcomes.

## 3. Current level and how to approach this lesson

The available learning history indicates that you have already worked through later Stage 1 problem-solving material, including collections, complexity, comprehensions, recursion, parsing, and a set of 35 practice questions. That is beyond the prerequisite position of this lesson. Therefore, this lesson should be treated as a **foundational review and consolidation**, rather than evidence that you are still at the very beginning.

For the solutions below, I deliberately restrict the implementation to the concepts needed by this lesson: variables, comparisons, Boolean operators, `if`/`elif`/`else`, membership, string methods, `match`, and the simple `for` loop already demonstrated in the source examples. I do not introduce functions, classes, external libraries, or advanced validation frameworks.

---

# Part C — Complete solutions to all five exercises

## Exercise 1 — Temperature classification

**Task:** Print `"Fever"` for temperatures of 38.0°C or above, `"Normal"` for values from 36.0°C up to but not including 38.0°C, and `"Low"` below 36.0°C.

### Solution

```python
temperature = 37.2

if temperature >= 38.0:
    print("Fever")
elif 36.0 <= temperature < 38.0:
    print("Normal")
else:
    print("Low")
```

### Line-by-line explanation

1. `temperature = 37.2` stores the temperature being checked. Change this value to test other cases.
2. `if temperature >= 38.0:` checks whether the temperature is at least 38.0. This includes exactly 38.0 and every larger value.
3. `print("Fever")` runs only when the first condition is true.
4. `elif 36.0 <= temperature < 38.0:` checks the normal range. The lower boundary is included; the upper boundary is excluded.
5. `print("Normal")` runs when the temperature is in that range.
6. `else:` catches every remaining value. Since the earlier conditions cover 36.0 and above, the remaining values are below 36.0.
7. `print("Low")` reports that remaining case.

Test cases:

| Temperature | Expected result | Reason |
|---:|---|---|
| 39.0 | Fever | At least 38.0 |
| 38.0 | Fever | Boundary is included |
| 37.2 | Normal | Between 36.0 and 38.0 |
| 36.0 | Normal | Lower boundary is included |
| 35.9 | Low | Below 36.0 |

**Key lesson:** Use an `if`/`elif`/`else` chain for ranges, and order the branches so each boundary is handled correctly.

## Exercise 2 — Free-shipping eligibility

**Task:** Free shipping applies if the order total is at least 50, or if the customer is a member and the order total is at least 20.

### Solution

```python
order_total = 25
is_member = True

if order_total >= 50 or (is_member and order_total >= 20):
    print("Free shipping")
else:
    print("Shipping fee applies")
```

### Line-by-line explanation

1. `order_total = 25` stores the customer's order amount.
2. `is_member = True` records whether the customer is a member.
3. `if` begins the eligibility decision.
4. `order_total >= 50` checks the first way to qualify: spend at least 50.
5. `or` means the customer can qualify through either the first rule or the second rule.
6. `(is_member and order_total >= 20)` groups the second rule. Both membership and a minimum order of 20 are required.
7. If either complete route is true, `print("Free shipping")` runs.
8. Otherwise, `else` runs and prints `"Shipping fee applies"`.

### Test the different combinations

| Order total | Member? | Result | Explanation |
|---:|---|---|---|
| 60 | No | Free shipping | First rule is satisfied |
| 25 | Yes | Free shipping | Member and total is at least 20 |
| 25 | No | Shipping fee applies | Neither rule is satisfied |
| 15 | Yes | Shipping fee applies | Member, but total is below 20 |
| 50 | No | Free shipping | Exactly 50 qualifies |

**Key lesson:** Parentheses make it clear that `and` binds the two requirements of the member rule, while `or` connects the two alternative ways to qualify.

## Exercise 3 — Rewrite nested username checks as guards

**Task:** Flatten the original nested checks without changing their messages, then add a rule rejecting usernames longer than 20 characters.

### Solution

```python
username = "ab"

if username == "":
    print("Error: username cannot be empty.")
elif not username.isalnum():
    print("Error: username must contain only letters and numbers.")
elif len(username) < 3:
    print("Error: username must be at least 3 characters.")
elif len(username) > 20:
    print("Error: username must be no more than 20 characters.")
else:
    print("Username accepted:", username)
```

### Line-by-line explanation

1. `username = "ab"` stores the username to validate.
2. `if username == "":` checks whether the string is empty.
3. The first `print` reports the empty-username error.
4. `elif not username.isalnum():` checks whether the username contains anything other than letters and numbers. `isalnum()` is true when all characters are letters or digits; `not` reverses that result.
5. The second `print` reports invalid characters.
6. `elif len(username) < 3:` checks whether the username is shorter than the minimum length.
7. The third `print` reports the minimum-length error.
8. `elif len(username) > 20:` adds the new maximum-length rule.
9. The fourth `print` reports a username that is too long.
10. `else:` runs only if every invalid-input check above it is false.
11. `print("Username accepted:", username)` handles the valid username.

For `username = "ab"`, the output is:

```text
Error: username must be at least 3 characters.
```

### Additional test values

| Username | Expected result |
|---|---|
| `""` | Empty username error |
| `"abc!"` | Letters-and-numbers error |
| `"ab"` | Minimum-length error |
| `"this_username_is_way_too_long"` | Maximum-length error |
| `"sovon2026"` | Username accepted |

**Why this is better:** Each invalid case is checked at the same indentation level. The successful path is not buried inside nested `if` blocks. The order also makes the first reported error predictable.

## Exercise 4 — Weekday and weekend using `match`

**Task:** Match day abbreviations `"Mon"` through `"Sun"`. Monday–Friday should print `"Weekday"`; Saturday and Sunday should print `"Weekend"`. Use the `|` pattern.

### Solution

```python
day = "Sun"

match day:
    case "Sat" | "Sun":
        print("Weekend")
    case "Mon" | "Tue" | "Wed" | "Thu" | "Fri":
        print("Weekday")
    case _:
        print("Unknown day")
```

### Line-by-line explanation

1. `day = "Sun"` stores the day abbreviation to classify.
2. `match day:` tells Python to compare the value of `day` against the following patterns.
3. `case "Sat" | "Sun":` matches either Saturday or Sunday. The vertical bar means “or.”
4. `print("Weekend")` runs when either weekend abbreviation matches.
5. `case "Mon" | "Tue" | "Wed" | "Thu" | "Fri":` matches any of the five weekday abbreviations.
6. `print("Weekday")` runs for one of those values.
7. `case _:` is the wildcard default. It matches any value not matched by the earlier cases.
8. `print("Unknown day")` handles unexpected input such as `"Funday"`.

### Test cases

| Input | Output |
|---|---|
| `"Mon"` | Weekday |
| `"Wed"` | Weekday |
| `"Fri"` | Weekday |
| `"Sat"` | Weekend |
| `"Sun"` | Weekend |
| `"Funday"` | Unknown day |

**Version note:** This code requires Python 3.10 or newer because it uses `match`.

**Key lesson:** Use `match` for a fixed set of exact choices. The wildcard case prevents unexpected values from silently receiving no response.

## Exercise 5 — Distinguish `None`, empty string, and real text

**Task:** Check an optional `middle_name` value and print a different message for `None`, `""`, and actual text.

### Solution

```python
middle_name = None

if middle_name is None:
    print("Middle name was not provided.")
elif middle_name == "":
    print("Middle-name field was left blank.")
else:
    print("Middle name:", middle_name)
```

### Line-by-line explanation

1. `middle_name = None` represents a value that is absent or was not supplied.
2. `if middle_name is None:` checks whether the value is specifically the `None` object.
3. `print("Middle name was not provided.")` reports the missing value.
4. `elif middle_name == "":` checks whether the value is an empty string. This is different from `None`.
5. `print("Middle-name field was left blank.")` reports a present-but-empty string.
6. `else:` handles every other value, which in this exercise means real text.
7. `print("Middle name:", middle_name)` displays that text.

### Test all three cases

**Case A — Not supplied**

```python
middle_name = None
```

Output:

```text
Middle name was not provided.
```

**Case B — Supplied as an empty string**

```python
middle_name = ""
```

Output:

```text
Middle-name field was left blank.
```

**Case C — Real text**

```python
middle_name = "Kumar"
```

Output:

```text
Middle name: Kumar
```

**Why not write `if middle_name:`?** Because both `None` and `""` are falsey. A single truthiness check would combine two states that this exercise requires us to distinguish. Use `is None` for the missing-value case and `== ""` for the empty-string case.

---

# Part D — Final revision sheet

## Conditional syntax

```python
if condition:
    # runs when condition is true
elif another_condition:
    # runs when the first condition was false
    # and this condition is true
else:
    # runs when no earlier condition matched
```

## Boolean operators

```python
condition_a and condition_b   # both must be truthy
condition_a or condition_b    # at least one must be truthy
not condition_a              # reverses truth value
```

## Important comparisons

```python
value == other_value     # compare values
value is None            # check specifically for None
18 <= age < 65           # chained range comparison
item in collection       # membership check
```

## Short-circuit safety pattern

```python
if denominator != 0 and 10 / denominator > 1:
    print("Safe to evaluate the division")
```

The zero check comes first. If it is false, Python skips the division.

## Guard-style validation

```python
if value == "":
    print("Missing")
elif not value.isalnum():
    print("Invalid characters")
elif len(value) < 3:
    print("Too short")
else:
    print("Accepted")
```

Check invalid cases early and keep the normal path flat.

## Match-style routing

```python
match status:
    case "new":
        print("Create record")
    case "ready" | "approved":
        print("Continue processing")
    case _:
        print("Unknown status")
```

Use this style for exact, known values. It requires Python 3.10 or newer.

---

## Completion status

All concepts, code patterns, outputs, four full lesson examples, common mistakes, lesson checklist, and all five practice exercises from the supplied lesson are covered in this guide.

**Word-limit check:** The lesson summary (Part A) is designed to remain below 5,000 words. The five exercise solutions (Part C) are designed to remain below 3,500 words. Part B and Part D are separate roadmap assessment and revision material.
