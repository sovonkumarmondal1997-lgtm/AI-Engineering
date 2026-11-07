# Stage 1 — Topic 05: Problem Decomposition
## Complete Study Guide, Learning-Level Analysis, and Exercise Solutions

**Source lesson:** `05-problem-decomposition.md`

---

# Part 1 — Lesson summary (under 750 words)

## 1. What is problem decomposition?

**Decomposition** means breaking one large problem into smaller, manageable jobs called **responsibilities**. In Python, each responsibility is usually implemented as a function.

Imagine a 40-line program that reads expenses, validates them, calculates totals, and prints a report in one large block. It may work, but it is difficult to locate the calculation, test it separately, reuse the validation, or safely change one part. A bug in one area can affect the rest.

For an expense program, separate responsibilities could be: (1) read or collect expense data, (2) validate each expense, (3) calculate the total and average, and (4) format and print a report. This extends **Input → Process → Output**: the processing part is divided into smaller processes.

## 2. Important terms

- **Responsibility:** One clear job that a piece of code is in charge of.
- **Single responsibility:** A function should have one cohesive job, accurately described by its name. `calculate_total_and_print_report` suggests two jobs, so separate it into `calculate_total` and `print_report`.
- **Composition:** Building a larger behavior by calling smaller functions together.
- **Coupling:** How much one part of a program depends on another. Clear inputs, outputs, and boundaries reduce unwanted dependence.

A useful heuristic: if you cannot describe a function's job in one short sentence without joining unrelated actions with “and,” consider splitting it. This is guidance, not a strict rule.

## 3. Finding responsibilities

Read the problem in plain English. Look for **verbs** (actions), which may become functions, and **nouns** (things), which may become variables or data passed between functions.

For “read expenses, validate each one, calculate the total, and print a summary,” possible functions are `read_expenses`, `validate_expense`, `calculate_total`, and `print_summary`. Use judgment; not every verb needs its own function.

## 4. Example 1 — One function, one job

```python
def total_of(expenses):
    total = 0
    for expense in expenses:
        total = total + expense
    return total

expenses = [12, 45, 9, 20]
print(total_of(expenses))
```

`total_of` receives a list, starts a running total at zero, visits each expense, adds it, and returns the final total: `86`. It can be tested independently, for example `total_of([1, 2, 3])` returns `6`, and reused without including input or report-printing logic.

## 5. Example 2 — Separate calculation from presentation

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

`total_of` calculates the sum. `average_of` calculates the mean and first checks for an empty list to avoid division by zero; returning `0` for an empty list is an example policy, not the mathematical average of an empty collection. It reuses `total_of`, rather than duplicating the sum logic. `describe_spending` focuses on creating readable text. `str(...)` converts numbers to strings so they can be joined with other text. For the sample list, the report is `Total: 86, Average: 21.5`. If total calculation changes, it is updated in one place.

## 6. Example 3 — A decomposed password report

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

`has_minimum_length` checks length. `has_a_digit` examines each character; `.isdigit()` checks whether a character is a digit. It returns `True` as soon as it finds one, otherwise `False` after the loop. `check_password` composes those checks: `not` reverses the Boolean, and the function returns the first failing rule or `"OK"`. `print_password_report` loops over passwords, asks `check_password` for each result, and prints it. Output: `hunter2 -> too short`, `abc -> too short`, and `correcthorsebattery9 -> OK`.

Each function can be tested separately. The passwords are demonstration data only: never print or log real passwords.

## 7. Common mistakes and key lesson

Avoid one giant function, but also avoid creating functions for every trivial one-line operation when that adds complexity. Use meaningful names instead of vague names such as `process()` or `doStuff()`. Keep callers dependent on a function's interface (inputs, outputs, and promised behavior), not its internal implementation. If compatible internals change, callers should not need changes; changing the interface or behavior may require them.

Decomposition is a judgment skill. It makes programs easier to read, test, reuse, and fix. In AI-agent systems, tools should likewise be small functions with clear inputs, outputs, and one job, which can be composed into larger tasks.

---

# Part 2 — Current learning-level analysis

Your previously shared Stage 1 roadmap progresses from computational thinking and program design through core Python, control flow, collections, files and CLI work, packages, testing, OOP, production practices, advanced Python, performance, packaging, CPython internals, design patterns, visualization, security, code review, and refactoring. It also includes practical projects such as the Personal Expense Ledger CLI, Log Investigation and Reliability CLI, Data Quality and Transformation Pipeline, and Rule-Based Risk Review Engine.

This lesson bridges individual Python functions and complete program organization. Its expense examples connect to the Personal Expense Ledger CLI; its password checks demonstrate independent validation rules; and its decomposition principles will later help organize data-quality and risk-review logic.

**Important:** The roadmap shows what you plan to study. It does not establish that you have mastered those topics. I assess the learning requirements and the lesson progression, not unseen practical performance.

Based on the lessons shared so far, you are working through foundational Python: sequence, selection, loops, functions, return values, and now decomposition. Your current level for this topic is **beginner / foundational, progressing toward structured program design**.

Priorities:
1. Translate a plain-English requirement into responsibilities before coding.
2. Give each function one cohesive job and a meaningful name.
3. Pass data through parameters and return values rather than hidden dependencies.
4. Compose functions in a readable order.
5. Test each function independently, including empty input and rule-failure cases.

**Readiness standard:** Explain why each function exists, its input and output, and which function calls it. Be able to change one rule without rewriting unrelated reporting code.

---

# Part 3 — Completed exercises (under 1,500 words)

## Exercise 1 — Decompose the exam-score problem before coding

**Problem:** Read exam scores, count students who passed (score 60 or above), calculate the class average, and print a short report.

| Responsibility | Suggested function | Why separate? |
|---|---|---|
| Read/collect scores | `read_scores()` | Handles user input and builds the list. |
| Count passing students | `count_passes(scores)` | Applies the rule: score is at least 60. |
| Calculate average | `calculate_average(scores)` | Performs the mathematical calculation. |
| Produce report | `print_report(...)` | Presents the calculated results. |

The nouns are `scores`, `students`, `pass_count`, and `average`—these are data. The verbs are `read`, `count`, `calculate`, and `print`—these suggest functions. Changing report wording should not require changing the pass-count calculation.

## Exercise 2 — Implement and compose the functions

### Complete solution

```python
def read_scores():
    number_of_students = int(input("How many students? "))
    scores = []

    for student_number in range(number_of_students):
        score = float(input("Enter exam score: "))
        scores.append(score)

    return scores


def count_passes(scores):
    pass_count = 0
    for score in scores:
        if score >= 60:
            pass_count = pass_count + 1
    return pass_count


def calculate_average(scores):
    if len(scores) == 0:
        return 0

    total = 0
    for score in scores:
        total = total + score

    return total / len(scores)


def print_report(scores, pass_count, average):
    print("Exam Report")
    print("Number of students:", len(scores))
    print("Students passed:", pass_count)
    print("Class average:", average)


def main():
    scores = read_scores()
    pass_count = count_passes(scores)
    average = calculate_average(scores)
    print_report(scores, pass_count, average)


main()
```

### Line-by-line explanation by function

**1. `read_scores()`**
- `def read_scores():` defines the input function; it has no parameters because it asks the user directly.
- `int(input(...))` displays a prompt, receives text, and converts it to the integer number of students.
- `scores = []` creates an empty list.
- `for student_number in range(number_of_students):` repeats once per student.
- `float(input(...))` reads a score and converts it to a number that can include decimals.
- `scores.append(score)` adds the score to the list.
- `return scores` hands the completed list to the caller.

**2. `count_passes(scores)`**
- `scores` receives the list.
- `pass_count = 0` initializes the counter.
- The `for` loop examines every score.
- `if score >= 60:` checks the rule, including exactly 60.
- `pass_count = pass_count + 1` increments the count only for a passing score.
- `return pass_count` sends back the final count.

**3. `calculate_average(scores)`**
- `if len(scores) == 0:` checks whether the list is empty.
- `return 0` defines an empty-list policy and prevents division by zero. It is a chosen program policy, not a mathematical average.
- `total = 0` initializes the running sum.
- The `for` loop adds every score to `total`.
- `return total / len(scores)` divides the sum by the number of scores and returns the average.

**4. `print_report(...)`**
- Its parameters receive the list, pass count, and average.
- The `print` statements display the report.
- It does not recalculate anything; it only presents results.

**5. `main()`**
- `scores = read_scores()` collects data.
- `pass_count = count_passes(scores)` passes the list to the pass counter.
- `average = calculate_average(scores)` reuses the same list.
- `print_report(...)` passes the results to the reporting function.
- `main()` starts the overall sequence.

### Example run

For scores `80`, `60`, `40`, and `90`:

```text
Exam Report
Number of students: 4
Students passed: 3
Class average: 67.5
```

The average is `(80 + 60 + 40 + 90) / 4 = 67.5`. Three scores (80, 60, and 90) are at least 60.

**Assumption:** This beginner solution expects valid numeric input and a valid student count. Input validation and score-range rules are not specified by the exercise, so they are not added here.

## Exercise 3 — Add a no-spaces password rule

```python
def has_no_spaces(password):
    for character in password:
        if character == " ":
            return False
    return True


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
    if not has_no_spaces(password):
        return "must not contain spaces"
    return "OK"


print(has_no_spaces("secure9pass"))
print(has_no_spaces("bad pass9"))
print(check_password("secure9pass"))
print(check_password("bad pass9"))
```

**Line-by-line explanation**
- `has_no_spaces(password)` defines one independent responsibility: inspect a string for a space.
- `for character in password:` visits each character.
- `character == " "` checks for a literal space.
- `return False` immediately reports failure if a space is found.
- `return True` runs only if the loop finishes without finding a space.
- `has_minimum_length` and `has_a_digit` are the original independent checks.
- `check_password` calls each check in order. `not` reverses the Boolean result. A failed rule returns its message immediately; a password passing all three receives `"OK"`.
- The final four calls test both outcomes of the new rule and its integration into the complete checker.

Expected output:

```text
True
False
OK
must not contain spaces
```

The new function can be tested alone and does not need to know how the other rules work. These checks teach decomposition; they are not a complete production password-security policy.

## Exercise 4 — Describe a function in one sentence

Choose `print_password_report(passwords)` from Example 3.

**One-sentence description:** “Print one password-check result for every password in the supplied list.”

This describes one cohesive reporting responsibility without using “and.” The loop is part of producing the report; `check_password` owns the password-rule logic. The reporting function does not need splitting for this exercise because it coordinates display rather than implementing the validation rules. Splitting it further would not clearly improve the design at this stage.

---

# Part 4 — Completion checklist

- [ ] I can list responsibilities from a plain-English problem before coding.
- [ ] I can explain why input, calculation, and reporting are separate jobs.
- [ ] I can write a function with one cohesive responsibility and a meaningful name.
- [ ] I can compose functions by passing returned values into other functions.
- [ ] I can explain how clear interfaces reduce unwanted coupling.
- [ ] I can handle an empty score list using an explicit policy.
- [ ] I can test a function independently with inputs that pass and fail its rule.

**Stop here until you can reproduce the exercises and explain the function boundaries yourself. I will wait for your instruction before moving to the next topic.**
