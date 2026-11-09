# Stage 1 — Module 03: Conditionals, Guards, and Boolean Logic

**Purpose:** A beginner-friendly study note and complete exercise solutions, based on the supplied lesson.  
**Scope:** Stage 1 concepts only: variables, basic types, comparisons, Boolean logic, conditionals, strings, collections, loops already previewed, and `match`/`case`.

---

# Part 1 — Step-by-step lesson summary

## 1. Control flow: how a program makes decisions

Normally, Python executes statements from top to bottom. This is **sequence**. **Control flow** describes the actual order in which statements run, including decisions to skip some statements or choose one path over another. A **branch** is one possible path. For example, a checkout applies a discount only if a coupon is valid. This lesson covers selection; loops cover repetition.

## 2. Boolean values, expressions, and truth testing

A Boolean expression evaluates to `True` or `False`:

```python
print(5 > 3)                    # True
print(5 == 6)                   # False
print("cat" in "concatenate")   # True
```

`in` checks membership. It works with substrings and collection elements:

```python
role = "admin"
if role in {"admin", "editor"}:
    print("Access allowed")
# Output: Access allowed
```

An `if` condition need not literally produce a Boolean. Python **truth-tests** its result. For common built-in values, `False`, `None`, `0`, `""`, and empty collections such as `[]` are falsey; non-empty strings such as `"hello"` are truthy.

```python
if "hello":
    print("runs")
if []:
    print("does not run")
if 0:
    print("does not run")
# Output: runs
```

Custom objects can define their own truth-value behavior, so the list above is a rule of thumb for built-in values.

## 3. `if`, `else`, and `elif`

An `if` block runs only when its condition is true:

```python
temperature = 35
if temperature > 30:
    print("It's a hot day.")
# Output: It's a hot day.
```

If the condition is false, Python skips the indented block and continues after it.

Use `else` for the alternative path. Exactly one of the two blocks runs:

```python
age = 16
if age >= 18:
    print("You may vote.")
else:
    print("You may not vote yet.")
# Output: You may not vote yet.
```

Use `elif` for additional conditions. Python checks from top to bottom and runs only the first matching block:

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
# Output: Grade: B
```

Put overlapping ranges in the correct order—here, highest first. Otherwise, a broad condition can capture values intended for a later branch:

```python
score = 95
if score >= 70:
    print("C or better")
elif score >= 90:
    print("A")
# Output: C or better; the A branch is unreachable.
```

## 4. Comparisons and Boolean operators

Python supports chained comparisons:

```python
age = 25
if 18 <= age < 65:
    print("Working-age range")
# Output: Working-age range
```

This means `18 <= age` **and** `age < 65`.

`==` tests value equality; `is` tests object identity. Use `value is None` to check for the unique `None` object. Do not use `is` for ordinary value comparisons.

- `and`: both conditions must be true.
- `or`: at least one condition must be true.
- `not`: reverses a truth value.

```python
has_ticket = True
is_on_time = False
if has_ticket and is_on_time:
    print("Boarding allowed.")
else:
    print("Boarding denied.")
# Output: Boarding denied.
```

Parentheses make combined conditions easier for people to read:

```python
age = 15
has_guardian = True
is_eligible = age >= 18 or (age >= 13 and has_guardian)
print(is_eligible)
# Output: True
```

## 5. Short-circuit evaluation

Python may stop evaluating an `and`/`or` expression once its result is certain. With `and`, a false left side makes the whole expression false, so the right side is skipped. Put a safe check first when the next operation could fail:

```python
denominator = 0
if denominator != 0 and 10 / denominator > 1:
    print("Result is greater than 1.")
else:
    print("Cannot safely check that (denominator may be zero).")
# Output: Cannot safely check that (denominator may be zero).
```

The division is never attempted. With `or`, a truthy left side means the right side is skipped.

`and` and `or` can return an operand, not necessarily `True` or `False`:

```python
print(False and "hello")   # False
print(True and "hello")    # hello
print("" or "fallback")    # fallback
print("Python" or "fallback")  # Python
```

More precisely, `x and y` returns `x` if `x` is falsey; otherwise it evaluates and returns `y`. `x or y` returns `x` if `x` is truthy; otherwise it evaluates and returns `y`.

## 6. Guard conditions: handle invalid cases first

A guard condition checks invalid, missing, or special input before normal processing. This avoids deeply nested code. The nested username example is:

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
# Output: Error: username must be at least 3 characters.
```

A flatter guard-style chain handles bad cases first:

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
# Output: Error: username must be at least 3 characters.
```

A **guard clause** also exits the current path early with `return`, `raise`, `continue`, or `break`; those become especially useful with functions and loops. The `elif` example is guard-style branching, but does not itself exit early.

## 7. `match`/`case`

`match` compares one value with patterns in order. The first matching `case` runs. `_` is a wildcard default that matches anything:

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
# Output: Prepare to stop
```

`match` was introduced in Python 3.10. Use `if`/`elif` for comparisons and ranges; use `match` for a known set of exact values. A case can match multiple literal values with `|`:

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
# Output:
# warm
# Weekday
```

## 8. All four lesson examples

**Example 1 — Driving permit eligibility**

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

The first test is false. The `elif` is true because age is at least 16 and consent is true. Output: `You can get a learner's permit with guardian consent.`

**Example 2 — Password rule checks**

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

The outer loop checks each password. The inner loop examines its characters; `.isdigit()` detects a digit. The guard chain reports the first failed rule. Output:

```text
 -> Error: password cannot be empty.
short1 -> Error: password must be at least 8 characters long.
longenoughbutnodigits -> Error: password must contain at least one digit.
hunter22 -> Password meets all the rules.
```

These are teaching rules, not a complete production password policy.

**Example 3 — Traffic light with `match`**

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

Each exact color selects its case; `"flashing yellow"` selects `_`. Output:

```text
red -> Stop
yellow -> Prepare to stop
green -> Go
flashing yellow -> Proceed with caution
```

**Example 4 — Optional value and `None`**

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

`None` means no value was provided; `""` means a provided but blank string. They are different states, even though both are falsey. Output:

```text
No referral code was used.
Bonus points earned: 0
```

## 9. Common mistakes and practical rules

- `=` assigns; `==` compares. `if age = 18:` is a syntax error.
- Order overlapping `elif` ranges carefully, usually most specific/highest first.
- Only the first true branch in an `if`/`elif` chain runs.
- Prefer flat guard chains over excessive nesting.
- The literal `match` patterns taught here do not test ranges; use `if`/`elif` for `>`, `<`, `>=`, and `<=`.
- Include `case _:` when an unmatched value needs a defined default.
- In later AI/agent systems, the same ideas route known tool names, validate inputs, and reject invalid arguments before an expensive model call.

---

# Part 2 — Complete solutions to all five exercises

## Exercise 1 — Classify body temperature

```python
temperature = 37.2

if temperature >= 38.0:
    print("Fever")
elif 36.0 <= temperature < 38.0:
    print("Normal")
else:
    print("Low")
```

**Line by line**

1. `temperature = 37.2` stores the sample Celsius value.
2. `temperature >= 38.0` checks the fever threshold. It is false for `37.2`.
3. `36.0 <= temperature < 38.0` checks both bounds. It is true for `37.2`.
4. Python prints `Normal` and skips `else`.
5. `else` handles values below `36.0`.

**Test values:** `38.0` prints `Fever`; `36.0` and `37.2` print `Normal`; `35.9` prints `Low`.

## Exercise 2 — Free-shipping eligibility

```python
order_total = 25
is_member = True

qualifies = (order_total >= 50) or (is_member and order_total >= 20)
print(qualifies)
```

**Line by line**

1. `order_total` stores the order amount.
2. `is_member` stores whether the customer is a member.
3. The first parenthesized condition is true when the order is at least 50.
4. The second is true only when the customer is a member **and** the order is at least 20.
5. `or` means either complete condition is enough.
6. `print` displays `True` for these sample values.

**Try these cases:** `(60, False)` → `True`; `(25, True)` → `True`; `(25, False)` → `False`; `(15, True)` → `False`.

## Exercise 3 — Flat username guard chain plus a 20-character limit

```python
username = "ab"

if username == "":
    print("Error: username cannot be empty.")
elif not username.isalnum():
    print("Error: username must contain only letters and numbers.")
elif len(username) < 3:
    print("Error: username must be at least 3 characters.")
elif len(username) > 20:
    print("Error: username must be no longer than 20 characters.")
else:
    print("Username accepted:", username)
```

**Line by line**

1. `username = "ab"` provides the value to validate.
2. The first guard rejects an empty string.
3. The second rejects characters that are not letters or numbers; `not` reverses `.isalnum()`.
4. The third rejects strings shorter than three characters.
5. The fourth is the added rule: reject strings longer than 20 characters.
6. `else` is reached only if every invalid-input check failed, so the username is accepted.

For `"ab"`, the output is `Error: username must be at least 3 characters.` The order preserves the original lesson's error priority and adds the length limit.

## Exercise 4 — Weekday/weekend using `match` and `|`

```python
day = "Sun"

match day:
    case "Mon" | "Tue" | "Wed" | "Thu" | "Fri":
        print("Weekday")
    case "Sat" | "Sun":
        print("Weekend")
    case _:
        print("Unknown day")
```

**Line by line**

1. `day = "Sun"` stores the abbreviation.
2. `match day:` begins matching that value.
3. The first case matches any one of Monday through Friday; `"Sun"` does not match.
4. The second case matches either Saturday or Sunday, so it runs and prints `Weekend`.
5. `_` handles an abbreviation outside the listed seven days.
6. This syntax requires Python 3.10 or newer.

## Exercise 5 — Distinguish `None`, empty string, and real text

```python
middle_name = None

if middle_name is None:
    print("No middle name was provided.")
elif middle_name == "":
    print("Middle name was provided as blank text.")
else:
    print("Middle name:", middle_name)
```

**Line by line**

1. `middle_name = None` represents a value that was not supplied. Change this line to test the other cases.
2. `is None` checks object identity with Python's unique `None` value.
3. `elif middle_name == ""` checks for a real string whose length is zero.
4. `else` handles actual text, such as `"Kumar"`.
5. Exactly one branch runs.

**Test results:** `None` → `No middle name was provided.`; `""` → `Middle name was provided as blank text.`; `"Kumar"` → `Middle name: Kumar`.

---

## Review checklist

- [ ] I can explain sequence, control flow, and branches.
- [ ] I can distinguish Boolean expressions from truth-value testing.
- [ ] I can write `if`, `if`/`else`, and `if`/`elif`/`else`.
- [ ] I understand comparison operators, `is None`, and chained comparisons.
- [ ] I can use `and`, `or`, `not`, parentheses, and short-circuit evaluation.
- [ ] I can flatten nested validation into guard-style branching.
- [ ] I can use literal `match` cases, `|`, and the `_` wildcard on Python 3.10+.
- [ ] I completed and tested all five exercises.

**Source:** User-provided lesson, `01-conditionals-guards-and-boolean-logic.md`. This document summarizes and solves the material in that lesson; it does not claim to cover topics outside it.
