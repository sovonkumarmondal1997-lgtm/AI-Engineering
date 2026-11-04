# Summary: Pseudocode, Flowcharts, and Dry Runs

Main idea: Before writing Python code, plan how to solve the problem. Use pseudocode to write the steps, flowcharts to visualize the logic, and dry runs to manually check how the code works. These techniques help prevent programming mistakes.

## 1. Why are these techniques important?

Beginners often start coding without planning. This makes it difficult to understand the logic, find mistakes, and fix problems.

Planning before coding helps you:

- Understand the problem clearly.
- Organize the solution into steps.
- Find logical mistakes before writing code.
- Save debugging time.

## 2. Important concepts

| Concept | Simple meaning |
| --- | --- |
| Pseudocode | Writing program logic in simple, structured English before coding. |
| Flowchart | A diagram showing program steps, decisions, and their execution order. |
| Dry Run | Manually executing code step by step without running it on a computer. |
| Trace Table | A table that tracks how variable values change during a dry run. |

## 3. Pseudocode: Plan before coding

Pseudocode describes what a program should do without worrying about Python syntax.

Example: Calculate the total of expenses.

```text
START
  SET total TO 0
  FOR EACH expense IN expenses
    ADD expense TO total
  END FOR
  RETURN total
END
```

Explanation:

- START begins the algorithm.
- SET initializes a variable.
- FOR EACH repeats an operation for every item.
- ADD updates the total.
- RETURN provides the result.
- END finishes the algorithm.

Pseudocode is easier to modify than Python code because you do not need to worry about exact syntax, colons, or indentation.

## 4. Flowcharts: Visualize program logic

A flowchart represents the same algorithm using steps, decisions, and arrows.

Example: Calculate total expenses.

```text
[Start]
   |
   v
[Set total = 0]
   |
   v
<More expenses?>
   | Yes
   v
[Take next expense]
   |
   v
[Add expense to total]
   |
   +------ Back to decision

   No
   |
   v
[Return total]
   |
   v
 [End]
```

Explanation:

- Boxes represent operations.
- Decision points represent conditions.
- Arrows show execution direction.
- The arrow returning to the decision represents a loop.
- If the expense list is empty, the answer is immediately No, and the returned total is 0.

Flowcharts are particularly useful when a program has multiple decisions or repeated operations.

## 5. Dry Runs: Execute code manually

A dry run means acting like the computer and tracking every variable as the code executes.

A trace table helps record those changes.

### Example 1: Pseudocode converted into Python

Problem: Count how many numbers are greater than 10.

Pseudocode:

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

Python:

```python
def count_greater_than_10(numbers):
    count = 0
    for number in numbers:
        if number > 10:
            count = count + 1
    return count

print(count_greater_than_10([5, 15, 8, 20, 10]))
```

Output: 2

Only 15 and 20 are greater than 10. The number 10 does not qualify because the condition is > 10, not >= 10.

Important: Pseudocode statements map closely to Python:

- SET count TO 0 → count = 0
- FOR EACH → for
- IF → if
- ADD 1 TO count → count = count + 1
- RETURN → return

### Example 2: Dry run using a trace table

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

Trace table:

| Number | Total | Count | Explanation |
| --- | --- | --- | --- |
| Start | 0 | 0 | Initial values |
| 4 | 4 | 1 | No bonus |
| 7 | 12 | 2 | Add 7 and bonus 1 |
| 2 | 14 | 3 | No bonus |
| 9 | 24 | 4 | Add 9 and bonus 1 |

Final calculation:

average = 24 / 4 = 6.0

Output: 6.0

The important detail is that every number greater than 5 adds an extra 1 to the total. Without a dry run, you might miss this additional calculation.

### Example 3: Find a bug using a dry run

Consider this code:

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

The intention is to count positive and negative numbers separately.

However, the second if mistakenly increases positive_count instead of negative_count.

| Number | Positive count | Negative count |
| --- | --- | --- |
| Start | 0 | 0 |
| 3 | 1 | 0 |
| -1 | 2 | 0 |
| 5 | 3 | 0 |
| -2 | 4 | 0 |
| 0 | 4 | 0 |

Correction:

Replace:

```python
positive_count = positive_count + 1
```

inside the second if block with:

```python
negative_count = negative_count + 1
```

The dry run exposes the mistake without executing the program.

## 6. Common beginner mistakes

1. Skipping pseudocode and starting coding without understanding the logic.
2. Writing vague pseudocode instead of specific steps.
3. Performing dry runs too quickly and skipping variable changes.
4. Checking only normal inputs instead of edge cases, such as empty lists and boundary values.

## 7. Practice exercises

1. Write pseudocode and Python code to find the largest number in a non-empty list without using max(). Handle negative numbers correctly.
2. Draw a flowchart for checking whether a password contains at least eight characters. Handle exactly eight characters correctly.
3. Dry-run this code and predict the output:

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

4. Find the bug in this code:

   ```python
   def count_words_longer_than(words, minimum_length):
       count = 0
       for word in words:
           if len(word) > minimum_length:
               count = count
       return count
   ```

   The mistake is count = count. It does not increase the counter. Correct it using count = count + 1.

## 8. Connection to Applied AI and Agentic AI

When building AI agents, developers plan workflows using pseudocode and flowcharts before implementing them. An agent may perform several steps, make decisions, and call different tools.

When an agent produces an unexpected result, developers can trace its execution and state changes to identify where the logic went wrong.

## Final takeaway

Pseudocode = Plan the logic. Flowchart = Visualize the logic. Dry Run = Check the logic manually. Trace Table = Track variable changes.
