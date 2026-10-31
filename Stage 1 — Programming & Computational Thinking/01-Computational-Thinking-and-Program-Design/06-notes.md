# Summary: Preconditions, Postconditions, and Edge Cases

Main idea: Before writing a Python function, understand what conditions must be satisfied before it runs, what result it promises after execution, and what unusual inputs might cause problems. This helps you write reliable programs that do not break unexpectedly. 06-preconditions-postconditions-and-edge-cases.md

## 1. Important Concepts

| Concept | Simple meaning |
| --- | --- |
| Precondition | Something that must be true before a function runs correctly. |
| Postcondition | Something guaranteed to be true after a function finishes correctly. |
| Invariant | A condition that must remain true throughout execution. |
| Normal case | Typical and expected input. |
| Edge case | Unusual input that might expose bugs. |
| Invalid input | Input that does not meet requirements, such as text instead of a number. |
| Empty input | Input containing no elements, such as [] or "". |
| Duplicate | A value appearing more than once. |
| Boundary value | A value at the smallest or largest allowed limit, or just outside it. |

Important distinction: A precondition describes what a function requires. Validation means checking incoming data and deciding what to do when requirements are not satisfied. 06-preconditions-postconditions-and-edge-cases.md

## 2. Preconditions – What Must Be True Before Execution?

A precondition is an assumption about the input that must hold for a function to work correctly.

Example:

```python
def average(numbers):
    total = 0
    for number in numbers:
        total = total + number
    return total / len(numbers)

print(average([10, 20, 30]))
print(average([]))
```

Output:

```text
20.0
ZeroDivisionError
```

Why does it crash?

- len(numbers) calculates the number of elements.
- An empty list has length 0.
- Dividing by zero raises ZeroDivisionError.

The hidden precondition is that the list must not be empty. The function also assumes iterable input with values compatible with addition and division. 06-preconditions-postconditions-and-edge-cases.md

## 3. Postconditions – What Must Be True After Execution?

A postcondition describes what a function guarantees after completing successfully.

We can improve the previous function:

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

Output:

```text
20.0
None
```

Explanation:

- if len(numbers) == 0 checks for an empty list.
- return None represents the absence of an average.
- Otherwise, the function calculates and returns the average.

Postcondition: Returns the numerical average for a non-empty list or None for an empty list.

The caller must check for None before using the result as a number. Another possible design is to raise an exception. 06-preconditions-postconditions-and-edge-cases.md

## 4. Invariants – What Must Always Remain True?

An invariant is a condition that must remain true throughout the relevant operations of a program.

Examples:

- Expense calculation: The running total should never become negative if negative expenses are prohibited.
- Bank transfer: The combined balance of two accounts should remain unchanged when money is transferred between them.

Invariants depend on the rules of the system being developed. 06-preconditions-postconditions-and-edge-cases.md

## 5. Edge Cases – Where Programming Bugs Hide

Always check these four categories:

1. Empty input: What happens when a list or string is empty?
2. Invalid input: What happens when the wrong data type or an impossible value is provided?
3. Duplicates: What happens when the same value appears multiple times?
4. Boundary values: What happens at the minimum, maximum, and just outside the permitted range?

Example: If valid ages are 0–120, test 0, 120, -1, and 121. 06-preconditions-postconditions-and-edge-cases.md

## 6. Example: Password Validation

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
    12345678
]

for case in test_cases:
    print(repr(case), "->", validate_password(case))
```

Important coding concepts:

| Python syntax | Purpose |
| --- | --- |
| def | Defines a function. |
| isinstance(password, str) | Checks whether input is a string. |
| len() | Calculates string length. |
| if | Checks a condition. |
| return | Returns a result. |
| "a" \* 8 | Repeats a string eight times. |
| for | Iterates through test cases. |
| repr() | Displays values in an unambiguous representation, such as '' for an empty string. |

The function checks input type, empty input, minimum length (8), and maximum length (64).

The test cases deliberately cover normal input, empty input, boundary values, values outside the boundary, and invalid input.

Security note: Passing these validation rules does not mean a password is secure. Never print or log real passwords. 06-preconditions-postconditions-and-edge-cases.md

## 7. Common Beginner Mistakes

1. Testing only normal inputs and ignoring unusual cases.
2. Assuming user input, files, or external system data are always correctly formatted.
3. Allowing programs to crash accidentally instead of defining how invalid input should be handled.
4. Confusing boundary values with ordinary small numbers.
5. Forgetting invariants when programs become more complex. 06-preconditions-postconditions-and-edge-cases.md

## 8. Practical Exercises

1. Expense calculation: Identify preconditions and postconditions for total_of(expenses). Test an empty list and negative values (refunds). Decide whether negative values are valid.
2. First positive number: Write first_positive(numbers) to return the first positive number. Test at least four edge cases, including an empty list and a list without positive numbers. Decide what to return when none exists.
3. Remove duplicates: Write remove_duplicates(items) that returns a new list without duplicates while preserving the first occurrence and original order. Test normal, duplicate-only, and empty lists.
4. Password validation: Add a new rule, such as requiring at least one digit. Update test cases to cover both passing and failing inputs. 06-preconditions-postconditions-and-edge-cases.md

## 9. Connection to Applied AI and Agentic AI

AI agents receive unpredictable inputs, including user messages, documents with missing fields, and malformed tool results.

Therefore, agent tools must:

- Define their input requirements (preconditions).
- Guarantee predictable outputs (postconditions).
- Maintain important system rules (invariants).
- Handle empty, invalid, duplicate, and boundary inputs.

These practices help prevent unexpected failures in production AI systems. 06-preconditions-postconditions-and-edge-cases.md

## 10. Final Takeaway

Remember these three fundamental rules:

- Precondition = What must be true before execution?
- Postcondition = What must be true after execution?
- Invariant = What must always remain true?

Always test four edge-case categories: empty input, invalid input, duplicates, and boundary values.

The ultimate objective is to stop writing code that merely works with normal inputs and start writing code that behaves predictably with unexpected inputs.
