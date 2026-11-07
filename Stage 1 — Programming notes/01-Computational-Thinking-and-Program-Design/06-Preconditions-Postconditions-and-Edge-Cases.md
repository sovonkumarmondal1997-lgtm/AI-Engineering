# Stage 1 — Topic 06: Preconditions, Postconditions, and Edge Cases
## Complete Study Guide, Learning-Level Analysis, and Exercise Solutions

**Source lesson:** `06-preconditions-postconditions-and-edge-cases.md`

---

# Part 1 — Lesson summary (under 750 words)

## 1. Why this topic matters

Code may work with normal, friendly data but fail when it receives an empty list, duplicate values, invalid input, or a value at the edge of an allowed range. Professional programmers identify these possibilities before declaring a function complete. This lesson introduces the vocabulary and habits needed to make program behavior deliberate and testable.

## 2. Key terms

- **Precondition:** Something that must be true before a function can work correctly. For example, an average function that divides by the number of items requires a non-empty list. A precondition is part of the function's contract; checking it and deciding what to do if it is false is validation/handling. A function may check a precondition or simply assume it.
- **Postcondition:** A guarantee about the result after a function finishes correctly, assuming its preconditions were met. For `sorted_ascending(numbers)`, the result should contain the same values as the input, ordered from smallest to largest.
- **Invariant:** A fact that must remain true throughout the relevant computation or system states. For example, if expenses cannot be negative, a running expense total should never become negative. During a transfer between two bank accounts, their combined balance should remain unchanged if money is only moved between them.
- **Normal case:** Typical, expected input.
- **Edge case:** Unusual input near the limits of what a function is designed to handle.
- **Invalid input:** Input that violates basic expectations, such as text where a number is required.
- **Empty input:** No data, such as `[]` or `""`.
- **Duplicate:** A value that occurs more than once.
- **Boundary value:** A value exactly at an allowed limit, or just outside it. If ages 0–120 are allowed, test `0`, `120`, `-1`, and `121`.

## 3. The four edge-case questions

For every function, ask:

1. What if the input is empty?
2. What if the input is invalid or the wrong type?
3. What if values are duplicated?
4. What happens at the minimum and maximum boundaries, and just beyond them?

Also state what the function should do when an assumption is not met. Do not let a crash happen merely by accident.

## 4. Example 1 — An unstated precondition causes a crash

```python
def average(numbers):
    total = 0
    for number in numbers:
        total = total + number
    return total / len(numbers)

print(average([10, 20, 30]))
print(average([]))
```

The function assumes `numbers` is a non-empty collection of numeric values. The first call returns `20.0`. The second call has length zero, so it divides by zero and raises `ZeroDivisionError`. The hidden precondition was that the list must not be empty.

## 5. Example 2 — Explicitly handle empty input

```python
def average(numbers):
    if len(numbers) == 0:
        return None
    total = 0
    for number in numbers:
        total = total + number
    return total / len(numbers)

print(average([10, 20, 30]))
print(average([]))
```

The function now checks for an empty list first. It returns the numeric average for non-empty input, or `None` when empty. `None` represents the absence of a result. This defines a postcondition for both cases, but callers must check for `None` before treating the result as a number. Another design could raise an exception; the important point is to choose deliberately. Normal input still returns `20.0`.

## 6. Example 3 — Validate password input against edge cases

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
    "hunter22",
    "",
    "short",
    "a" * 8,
    "a" * 64,
    "a" * 65,
    12345678,
]

for case in test_cases:
    print(repr(case), "->", validate_password(case))
```

`isinstance(password, str)` first checks that the input is text. The function then checks empty input, minimum length, and maximum length. It returns a known message rather than failing for the demonstrated inputs. `"a" * 8` creates eight `a` characters; `"a" * 64` creates 64; `"a" * 65` is one beyond the maximum. `repr()` displays an empty string clearly as `''`, and the loop tests every case. The strings are demonstrations, not real credentials; never print or log actual passwords. `"valid"` means only that these length/type rules passed, not that the password is secure.

## 7. Common mistakes and engineering lesson

Do not test only the happy path, assume user/file/external input is well-formed, or leave bad-input behavior undecided. A boundary value means the exact edge of an allowed range and values just outside it—not simply any small number. Remember invariants as a program gains more operations, because new paths can accidentally violate them.

The central habit is: state assumptions, define promised behavior, construct tests for edge cases, and verify the results. This is directly relevant to data pipelines and AI agents, which receive empty, malformed, duplicated, or unexpected records and tool responses. Predictable handling makes production systems safer and easier to debug.

---

# Part 2 — Current learning-level analysis

Your previously shared Stage 1 roadmap progresses from computational thinking and core Python through control flow, collections, files and CLI work, packages, testing, OOP, production practices, advanced Python, performance, packaging, CPython internals, design patterns, visualization, security, code review, and refactoring. It also includes practical projects such as the Personal Expense Ledger CLI, Log Investigation and Reliability CLI, Data Quality and Transformation Pipeline, and Rule-Based Risk Review Engine.

This lesson builds directly on Topic 05 (Problem Decomposition): once a problem is split into functions, you must define each function's assumptions and guarantees and test its unusual inputs. The `total_of(expenses)` exercise connects to your expense-ledger project; validation and duplicate handling connect to data-quality pipelines.

**Your current position:** Based on the lessons shared so far, you are studying foundational Python—functions, parameters, return values, decomposition, and now defensive reasoning about inputs. For this topic, your working level is **beginner / foundational, progressing toward reliable function design**.

The roadmap describes intended learning coverage, not demonstrated mastery. I cannot infer that you have mastered all Stage 1 modules or projects from the folder tree alone. Your next priorities are to write contracts in plain English, decide error behavior intentionally, and test normal, empty, invalid, duplicate, and boundary inputs. You are ready to progress when you can explain why each test exists and predict its result before running it.

---

# Part 3 — Completed exercises (under 1,500 words)

## Exercise 1 — Define the contract for `total_of(expenses)`

From Topic 05:

```python
def total_of(expenses):
    total = 0
    for expense in expenses:
        total = total + expense
    return total
```

**Preconditions (assumptions):**
- `expenses` must be an iterable collection, such as a list.
- Each item must be a number compatible with addition to `total`.
- The function assumes values represent amounts in a consistent unit/currency.

**Postcondition (promise):** Returns the arithmetic sum of all values in the input collection. It does not modify the input list.

**Empty list:** It handles `[]` correctly: the loop runs zero times and the function returns the initial `total`, which is `0`.

**Negative values:** For an expense ledger, I would treat negative values as valid when they represent refunds or reversals. For example, `[100, -20]` totals `80`. The application should document that negative values mean refunds; if the business rule forbids negative expenses, validation should reject them before calling `total_of`. The summation function itself should not silently impose a business rule it does not own.

## Exercise 2 — Implement `first_positive(numbers)`

**Design decision:** Return the first positive number in list order. If there is no positive number—including an empty list—return `None`.

**Edge cases to test before coding:**
1. Empty list: `[]` → `None`.
2. No positive values: `[-3, 0, -1]` → `None`.
3. First item is positive: `[5, -2, 8]` → `5`.
4. Positive value appears later: `[-4, 0, 7, 9]` → `7`.
5. Multiple positive values: `[2, 4, 6]` → `2`, proving the first is returned.
6. Boundary around zero: `[0, 0, 1]` → `1`; zero is not positive.

### Code

```python
def first_positive(numbers):
    for number in numbers:
        if number > 0:
            return number
    return None


test_cases = [
    [],
    [-3, 0, -1],
    [5, -2, 8],
    [-4, 0, 7, 9],
    [2, 4, 6],
    [0, 0, 1],
]

for numbers in test_cases:
    print(numbers, "->", first_positive(numbers))
```

**Line-by-line explanation**
- `def first_positive(numbers):` defines a function that receives a collection.
- `for number in numbers:` examines items in their original order.
- `if number > 0:` checks whether the current item is strictly greater than zero. Zero and negatives do not qualify.
- `return number` immediately returns the first matching value, ending the function.
- `return None` runs only if the loop finishes without finding a positive number. This also covers an empty list.
- `test_cases` stores the six deliberately chosen inputs.
- The final `for` loop calls the function for each test and prints its input and result.

Expected results in order: `None`, `None`, `5`, `7`, `2`, `1`.

## Exercise 3 — Remove duplicates while preserving first occurrence

**Design decision:** Return a new list, preserve original order, and keep the first occurrence of each value.

### Code

```python
def remove_duplicates(items):
    unique_items = []

    for item in items:
        if item not in unique_items:
            unique_items.append(item)

    return unique_items


print(remove_duplicates([1, 2, 3]))
print(remove_duplicates(["a", "a", "a"]))
print(remove_duplicates([]))
print(remove_duplicates([3, 1, 3, 2, 1]))
```

**Line-by-line explanation**
- `def remove_duplicates(items):` defines the function and accepts the original collection.
- `unique_items = []` creates a separate, initially empty result list. The input is not changed.
- `for item in items:` visits every input item in order.
- `if item not in unique_items:` checks whether an equal value has already been kept.
- `unique_items.append(item)` adds the item only on its first occurrence.
- `return unique_items` returns the new list after all items are checked.
- The four calls test no duplicates, all values identical, empty input, and a mixed list with repeated values.

Expected output:

```text
[1, 2, 3]
['a']
[]
[3, 1, 2]
```

This beginner implementation works with ordinary list values and preserves order. Membership checking against a list can become slow for very large inputs; later you can learn more efficient approaches, while preserving the same behavior.

## Exercise 4 — Add a digit requirement to `validate_password`

**New rule:** In addition to being text with length 8–64, a password must contain at least one digit.

### Code

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

    has_digit = False
    for character in password:
        if character.isdigit():
            has_digit = True
            break

    if not has_digit:
        return "invalid: needs a digit"

    return "valid"


test_cases = [
    "hunter22",          # normal: contains digits
    "",                  # empty
    "short",             # too short
    "abcdefgh",          # minimum length, but no digit
    "abcdefg1",          # minimum length and has a digit
    "a" * 64,            # maximum length, but no digit
    "a" * 63 + "1",      # maximum length and has a digit
    "a" * 65,            # too long
    12345678,            # invalid type
]

for case in test_cases:
    print(repr(case), "->", validate_password(case))
```

**Line-by-line explanation**
- The first four checks reject non-text, empty, too-short, and too-long input before character inspection. This prevents inappropriate string operations on non-text values and defines the length boundaries.
- `has_digit = False` starts with the assumption that no digit has been found.
- `for character in password:` checks each character.
- `character.isdigit()` returns `True` for a digit character.
- `has_digit = True` records that a digit exists.
- `break` stops the loop early because finding one digit is enough.
- `if not has_digit:` checks whether the loop found no digit; if so, it returns the specific failure message.
- `return "valid"` is reached only after every rule passes.
- `test_cases` checks normal input, empty and too-short input, the minimum boundary with and without a digit, the maximum boundary with and without a digit, one character beyond the maximum, and invalid type.
- The final loop runs the checker against every test. `repr()` makes the empty string visible in the output.

Expected results in order: `valid`, `invalid: empty`, `invalid: too short`, `invalid: needs a digit`, `valid`, `invalid: needs a digit`, `valid`, `invalid: too long`, `invalid: not text`.

**Security note:** This is a teaching validator, not a complete password-security policy. Real systems should use established authentication and password-storage practices and must never log actual passwords.

---

# Part 4 — Completion checklist

- [ ] I can state the preconditions and postconditions of a function.
- [ ] I can explain an invariant with my own example.
- [ ] I can identify empty, invalid, duplicate, and boundary cases.
- [ ] I can define deliberate behavior for empty or invalid input.
- [ ] I can test both normal and unusual inputs before calling a function complete.
- [ ] I can explain why each test case is included and predict its result.

**Stop here until you can reproduce these solutions and explain the contracts and edge cases yourself. I will wait for your instruction before moving to the next topic.**
