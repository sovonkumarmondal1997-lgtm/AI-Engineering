# Summary: Problem Decomposition

Main idea: Problem decomposition means breaking one large programming problem into smaller, manageable tasks and writing a separate function for each task. This makes programs easier to understand, test, reuse, and fix.

## 1. Why is decomposition important?

Imagine writing one large Python program that:

- Reads expenses.
- Validates the expenses.
- Calculates the total and average.
- Prints a report.

If everything is written in one long block of code:

- Finding a particular calculation becomes difficult.
- Testing one part requires running the entire program.
- Reusing existing logic requires copying and pasting code.
- A bug in one section can affect other sections.

Solution: Divide the program into smaller functions, each responsible for one clear task.

## 2. Important concepts

| Concept | Simple meaning |
| --- | --- |
| Decomposition | Breaking a big problem into smaller tasks. |
| Responsibility | One specific job performed by a piece of code. |
| Single Responsibility | Each function should have one clear purpose. |
| Composition | Combining multiple functions to build a complete program. |
| Coupling | How much one function or part of a program depends on another. |

Good function boundaries, clear inputs, and return values help reduce unwanted coupling.

## 3. How to decompose a problem

Consider this task:

"Read expenses, validate each expense, calculate the total, and print a summary."

Break it into four responsibilities:

1. read_expenses() – collect expense data.
2. validate_expenses() – check whether expenses are valid.
3. calculate_total() – calculate the total.
4. print_report() – display the summary.

This follows the Input → Process → Output model. The processing part is divided into smaller processes.

A useful technique is to identify:

- Verbs (actions): Possible functions, such as read, validate, calculate, and print.
- Nouns (things): Possible variables or data, such as expenses, scores, and passwords.

## 4. Coding examples

### Example 1: One function, one responsibility

```python
def total_of(expenses):
    total = 0
    for expense in expenses:
        total = total + expense
    return total

expenses = [12, 45, 9, 20]
print(total_of(expenses))
```

Output: 86

Explanation:

- total_of() has one responsibility: add all expenses.
- for loops through each expense.
- total stores the running sum.
- return sends the result back.
- You can test it independently: total_of([1, 2, 3]) returns 6.

### Example 2: Multiple functions working together

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

Output: Total: 86, Average: 21.5

Important concepts:

- total_of() calculates the total.
- average_of() calculates the average and prevents division by zero.
- An empty list returns 0 as a design choice, not a mathematical average.
- describe_spending() creates a readable message.
- str() converts numbers into strings so they can be joined with +.
- average_of() reuses total_of() instead of duplicating its calculation. This is composition.

If the total calculation changes, you only need to update total_of().

### Example 3: Decomposing a password checker

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

Output:

```text
hunter2 -> too short
abc -> too short
correcthorsebattery9 -> OK
```

Explanation:

- has_minimum_length() checks whether a password has at least eight characters.
- has_a_digit() checks whether a password contains a number. .isdigit() checks an individual character.
- check_password() combines these checks and decides the result.
- print_password_report() loops through passwords and prints their results.

Each function has a separate responsibility. Each can also be tested independently.

Security note: These are demonstration passwords. Never print or log real passwords.

## 5. Common beginner mistakes

1. One giant function: Avoid putting every task into one function.
2. Too many small functions: Do not create unnecessary functions for every one-line calculation. Use judgment.
3. Vague names: Avoid names like process(), handle(), and doStuff(). Prefer meaningful names.
4. Unwanted coupling: A function should depend on another function's inputs, return values, and promised behavior—not its internal implementation.

Changing a function's internal code should not require changing its callers if its interface and behavior remain compatible.

## 6. Exercises

1. Exam scores: Break this problem into functions: read scores, count students who passed (60 or above), calculate the average, and print a report.
2. Implement those functions and combine them into a working program. Decide what happens when the score list is empty.
3. Add a function to the password checker that checks whether a password contains no spaces. Integrate it into check_password().
4. Choose a function you have written. Describe its job in one sentence without using "and". If it performs unrelated tasks, consider splitting it.

## 7. Connection to Applied AI and Agentic AI

AI agents use multiple small functions, often called tools, to perform tasks. An AI model decides which tool to call and when.

For example, an agent might have separate tools for:

- Searching information.
- Validating data.
- Calculating results.
- Generating reports.

Each tool needs a clear responsibility, input, and output. Decomposition makes these tools easier to understand, test, reuse, and combine reliably.

## Final takeaway

Decomposition = Break a big problem into small functions, give each function one clear responsibility, and combine those functions to build a complete program.

## Exercise 6 – Problem Decomposition (Complete Solutions)

We will solve all four exercises step by step using Python functions.

The main objective is to understand how to break a large programming problem into smaller functions, give each function one responsibility, and combine them into a working program.

### Exercise 1 & 2: Exam Scores – Decompose and Implement

Problem: Create a Python program that:

1. Reads students' exam scores.
2. Counts how many students passed (score of 60 or above).
3. Calculates the average score.
4. Prints an exam report.

#### Step 1: Decompose the problem

We can divide this problem into four functions.

| Function | Responsibility |
| --- | --- |
| read_scores() | Collect exam scores |
| count_passed() | Count students scoring 60 or above |
| calculate_average() | Calculate the average score |
| print_report() | Display the exam report |

We will also use a main section to coordinate these functions.

#### Step 2: Implement the functions

Complete Python program:

```python
# Function 1: Read student scores
def read_scores():
    scores = [85, 45, 90, 55, 70, 35, 60]
    return scores

# Function 2: Count students who passed
def count_passed(scores):
    passed = 0
    for score in scores:
        if score >= 60:
            passed = passed + 1
    return passed

# Function 3: Calculate average score
def calculate_average(scores):
    if len(scores) == 0:
        return 0
    total = 0
    for score in scores:
        total = total + score
    average = total / len(scores)
    return average

# Function 4: Print exam report
def print_report(scores, passed, average):
    print("EXAM REPORT")
    print("Total Students:", len(scores))
```

#### Step 3: Understand the output

PROGRAM OUTPUT

```text
EXAM REPORT
Total Students: 7
Students Passed: 4
Students Failed: 3
Average Score: 62.857142857142854
```

#### Step 4: Understand the calculations

Our input scores are:

```python
scores = [85, 45, 90, 55, 70, 35, 60]
```

A. Count students who passed

Passing condition: Score greater than or equal to 60.

| Student | Score | Result |
| --- | --- | --- |
| 1 | 85 | Pass |
| 2 | 45 | Fail |
| 3 | 90 | Pass |
| 4 | 55 | Fail |
| 5 | 70 | Pass |
| 6 | 35 | Fail |
| 7 | 60 | Pass |

Total passed = 4.

B. Calculate the average

$$
\text{Average} = \frac{\text{Sum of scores}}{\text{Number of students}}
$$

$$
= \frac{440}{7} = 62.8571
$$

#### Step 5: Understand how functions work together

This is called function composition.

```text
Main Program
Coordinates the complete program
        ↓
read_scores()
Returns the list of scores
        ↓
count_passed()
Counts passing students
        ↓
calculate_average()
Calculates average
        ↓
print_report()
Displays the final report
```

Notice that each function performs a specific responsibility.

For example:

- count_passed() does not print the report.
- calculate_average() does not count passing students.
- print_report() does not perform the calculations.

This makes the program easier to maintain and test.

#### Step 6: What happens when the score list is empty?

Consider:

```python
scores = []
```

Our calculate_average() function contains:

```python
if len(scores) == 0:
    return 0
```

This prevents division by zero.

The program can safely produce:

```text
EXAM REPORT
Total Students: 0
Students Passed: 0
Students Failed: 0
Average Score: 0
```

Returning zero here is a design decision. Mathematically, the average of an empty list is undefined.

One additional engineering improvement: Our example's read_scores() returns predefined sample data. In a real application, it could collect scores using input(), read a CSV file, or retrieve records from a database. The other functions would not need to change as long as they receive a list of scores.

### Exercise 3: Add a No-Spaces Function to the Password Checker

Problem: Add a function that checks whether a password contains spaces. Integrate this validation into the existing check_password() function.

#### Step 1: Understand the requirement

Our password checker already has two functions:

1. has_minimum_length() – checks whether the password has at least eight characters.
2. has_a_digit() – checks whether the password contains a number.

Now we need another function:

3. has_no_spaces() – checks whether the password contains any spaces.

#### Step 2: Implement the new function

```python
def has_no_spaces(password):
    return " " not in password
```

Let's understand this expression:

```python
" " not in password
```

- " " represents a space character.
- not in checks whether that character is absent from the string.
- If there are no spaces, Python returns True.
- If there is at least one space, Python returns False.

For example:

```python
print(has_no_spaces("hello123"))
print(has_no_spaces("hello 123"))
```

Output:

```text
True
False
```

#### Step 3: Integrate it into check_password()

Here is the complete updated program:

```python
# Function 1: Check minimum password length
def has_minimum_length(password):
    return len(password) >= 8

# Function 2: Check whether password contains a digit
def has_a_digit(password):
    for character in password:
        if character.isdigit():
            return True
    return False

# Function 3: Check whether password contains no spaces
def has_no_spaces(password):
    return " " not in password

# Function 4: Check the password
def check_password(password):
    if not has_minimum_length(password):
        return "too short"
    if not has_a_digit(password):
        return "needs a digit"
    if not has_no_spaces(password):
        return "contains spaces"
    return "OK"

# Function 5: Print password validation report
def print_password_report(passwords):
```

#### Step 4: Understand the output

```text
hunter2 -> too short
abc -> too short
correcthorsebattery9 -> OK
hello world123 -> contains spaces
python123 -> OK
```

#### Step 5: Understand function composition

The check_password() function calls three other functions.

```text
check_password(password)
        ↓
has_minimum_length()
Pass required
        ↓
has_a_digit()
Pass required
        ↓
has_no_spaces()
Pass required
        ↓
Return "OK"
All three checks passed
```

The if not statements mean that if a validation fails, the function immediately returns the corresponding error message.

Engineering observation: Each validation function can be tested independently. We can also change one validation rule without rewriting the entire password checker.

Security note: These are demonstration passwords. Never print or log real passwords in production applications.

### Exercise 4: Identify a Function's Responsibility

Problem: Choose a function you have written. Describe its job in one sentence without using "and". If it performs unrelated tasks, consider splitting it.

Let's use the following function:

```python
def calculate_total(expenses):
    total = 0
    for expense in expenses:
        total = total + expense
    return total
```

#### Step 1: Identify its responsibility

What does this function do?

It receives a list of expenses and calculates their sum.

Correct one-sentence description:

"Calculates the sum of all expenses in a given list."

Notice that this sentence describes only one responsibility.

#### Step 2: Check whether it violates Single Responsibility

Let's examine another example:

```python
def process_expenses(expenses):
    total = 0
    for expense in expenses:
        total = total + expense
    average = total / len(expenses)
    print("Total:", total)
    print("Average:", average)
```

This function performs multiple tasks:

1. Calculates the total.
2. Calculates the average.
3. Prints the report.

We can improve it by splitting those responsibilities.

Improved implementation:

```python
# Function 1: Calculate total
def calculate_total(expenses):
    total = 0
    for expense in expenses:
        total = total + expense
    return total

# Function 2: Calculate average
def calculate_average(expenses):
    if len(expenses) == 0:
        return 0
    total = calculate_total(expenses)
    return total / len(expenses)

# Function 3: Print report
def print_report(expenses):
    total = calculate_total(expenses)
    average = calculate_average(expenses)
    print("Total:", total)
    print("Average:", average)

# Main program
expenses = [100, 200, 300, 400]
print_report(expenses)
```

Output:

```text
Total: 1000
Average: 250.0
```

Now each function has a clear responsibility.

## Final Summary: What You Learned

| Concept | What you learned |
| --- | --- |
| Problem decomposition | Breaking a large problem into smaller tasks |
| Functions | Creating reusable blocks of code |
| Single Responsibility | Giving each function one clear purpose |
| Parameters | Passing data into functions |
| Return values | Sending results back to the caller |
| Function composition | Combining functions to build a complete program |
| Coupling | Managing dependencies between functions |
| Edge cases | Handling situations such as an empty list |
| Independent testing | Testing individual functions separately |

## Your understanding checkpoint

Before moving forward, make sure you can explain these five questions:

1. Why do we break a large program into smaller functions?
2. What is the difference between a parameter and a return value?
3. Why should a function have one clear responsibility?
4. What is function composition?
5. Why is return generally more useful than printing a calculation inside a reusable function?
