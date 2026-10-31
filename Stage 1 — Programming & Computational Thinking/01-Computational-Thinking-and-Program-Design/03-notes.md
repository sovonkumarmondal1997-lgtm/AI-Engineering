# Summary: Input → Process → Output (IPO)

Python Programming – Beginner Level | Based on your uploaded Markdown lesson

This lesson explains the Input → Process → Output (IPO) model, one of the most important concepts in programming. Almost every software application, data engineering pipeline, and AI agent follows this basic structure.

## 1. What is the IPO Model?

IPO means:

1. Input: Collect the information required by the program.
2. Process: Perform calculations or operations on that information.
3. Output: Display or return the final result.

Example: Making tea.

- Input: Water and tea leaves.
- Process: Boil water and steep tea leaves.
- Output: A cup of tea.

Programming example:

Problem: Calculate total expenses.

```text
Input: 100, 200, 300
Process: Add all three numbers.
Output: 600
```

## 2. Why Should You Understand IPO Before Coding?

Before writing Python code, answer three questions:

- Input: What information does the program need? Where will it come from?
- Process: What operations must be performed?
- Output: What result should the program produce?

This approach helps you understand the problem before writing code and prevents unnecessary confusion.

Input can come from:

- User-entered information.
- Existing variables.
- Fixed lists or stored data.
- Files.

## 3. Input in Python – input()

Python provides a built-in function called input() to collect information from users while a program is running.

Example:

```python
name = input("What is your name? ")
```

How it works:

1. Python displays the question.
2. The program pauses.
3. The user types an answer and presses Enter.
4. Python stores the entered information in name.

Important: input() always returns data as a string (text), even when the user enters numbers.

Also remember: IPO input is a general concept; input() is just one Python function for collecting interactive input.

## 4. Process in Python

The process is the actual work performed by your program.

It uses concepts you have already learned:

- Variables.
- Expressions.
- Statements.
- Calculations.
- Transformations.

For example:

```python
price = 100
quantity = 3
total = price * quantity
```

Here, Python multiplies the price by the quantity and stores the result in total.

## 5. Output in Python – print()

The print() function displays information on the screen.

Example:

```python
total = 300
print(total)
```

Output:

```text
300
```

Output is not limited to print(). A program can also return values to another part of the program or write data to files. These are introduced in later stages.

## 6. Type Conversion – int() and float()

This is one of the most important concepts in this lesson.

Because input() always returns text, you must convert numeric input before performing arithmetic.

Python provides:

- int() – Converts valid numeric text into a whole number.
- float() – Converts valid numeric text into a decimal number.

Example:

```python
age_text = input("How old are you? ")
age_number = int(age_text)
print(age_number)
```

If the user enters 16, Python initially receives "16" as text. int() converts it into the number 16.

### Example: Price and Quantity

```python
price_text = input("Enter the price: ")
quantity_text = input("Enter quantity: ")
price = float(price_text)
quantity = int(quantity_text)
total = price * quantity
print("Total cost:", total)
```

If the user enters:

```text
Enter the price: 19.99
Enter quantity: 3
```

Output:

```text
Total cost: 59.97
```

Notice that:

- float() converts the price into a decimal number.
- int() converts quantity into a whole number.
- \* multiplies both values.
- print() displays the result.

## 7. Multi-Step IPO Program – Expense Summary

A bigger program can contain multiple input, process, and output steps.

```python
expense_1 = float(input("Enter first expense: "))
expense_2 = float(input("Enter second expense: "))
expense_3 = float(input("Enter third expense: "))
total = expense_1 + expense_2 + expense_3
average = total / 3
print("Total spent:", total)
print("Average expense:", average)
if total > 100:
    print("Warning: total spending is high this period.")
```

Explanation:

Input:

- Collects three expenses.
- float(input(...)) collects text and immediately converts it into a decimal number.

Process:

- Adds all three expenses.
- Calculates their average by dividing the total by three.

Output:

- Displays total spending.
- Displays average spending.
- Displays an additional warning if the total exceeds 100.

New concept: if statement

```python
if total > 100:
    print("Warning: total spending is high this period.")
```

This is an introduction to selection (conditional execution).

The indented instruction runs only when total > 100 is true. Otherwise, Python skips it.

## 8. Common Beginner Mistakes

1. Forgetting type conversion: input() returns text, not numbers.

   ```python
   "3" * 2
   ```

   Output: "33" because Python repeats the text instead of performing numerical multiplication.

2. Invalid conversion:

   ```python
   int("abc")
   ```

   Produces a ValueError because "abc" cannot be converted into an integer.

3. Writing too much in one line: Avoid combining too many operations into one complicated statement. Use separate variables and clear steps.
4. Confusing process with output: Calculating a result does not automatically display it. Use print() to show it.

## 9. Practical Exercises

Complete all four exercises:

1. Age Calculator: Ask for the user's birth year, calculate approximate age using 2026, and print a sentence containing the age.
2. Temperature Converter: Convert Celsius into Fahrenheit using:

   $$
   F = C \times \frac{9}{5} + 32
   $$

   Add comments identifying input, process, and output.

3. Pass or Fail: Collect three test scores, calculate their average, and print "Pass" if the average is 40 or above; otherwise print "Fail".
4. Expense Summary: Modify the expense example to accept four expenses instead of three. Update the total and average calculations accordingly.

## 10. Connection to Applied AI and Agentic AI Engineering

AI agents also follow the IPO model:

| Component | AI Engineering Example |
| --- | --- |
| Input | User message or tool result |
| Process | Model inference, decision-making, and execution of logic |
| Output | AI response or another tool call |

For example, an AI agent receives a user's question, processes it using an AI model and Python logic, and produces an answer.

Understanding IPO helps you design each step of an AI application before implementing it.
