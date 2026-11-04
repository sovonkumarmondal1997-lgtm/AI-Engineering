# Summary: Algorithms, Programs, and Data

Based on your uploaded Python programming lesson | Beginner level

This topic introduces three fundamental concepts of programming: Algorithms, Programs, and Data. Every software application, data engineering pipeline, and AI system is built using these three components.

## 1. What is an Algorithm?

An algorithm is a finite, well-defined sequence of steps used to solve a particular problem.

You already use algorithms in everyday life. For example, following a recipe:

1. Boil water.
2. Add pasta.
3. Wait 10 minutes.
4. Drain the water.

This is an algorithm because it provides instructions to achieve a result.

A good algorithm has three important characteristics:

- Precise: Every step must be clear and unambiguous.
- Finite: It must eventually finish; it should not run forever.
- Correct: It must solve the problem according to its requirements.

An algorithm is not necessarily a computer program. It is simply a plan for solving a problem.

## 2. Input, Process, and Output

Algorithms commonly follow the Input → Process → Output model.

- Input: Information given to the algorithm.
- Process: Operations performed on the input.
- Output: The final result.

Example:

Problem: Calculate shopping expenses.

```text
Input: Item prices (100, 200, 300)
Process: Add all item prices.
Output: Total = 600
```

Not every algorithm requires external input. Some algorithms operate on existing data or internal state.

## 3. What is a Program?

A program is a collection of instructions written in a programming language that a computer can execute to perform a task.

Computers cannot directly understand ordinary English instructions. Therefore, we use programming languages such as Python.

For example:

```python
print("Hello, World!")
```

Here:

- print() is a built-in Python function.
- "Hello, World!" is the text we want to display.
- Python executes the instruction and displays the text.

Important: An algorithm is the plan, whereas a program is the implementation of that plan using a programming language.

One program can implement multiple algorithms.

## 4. What is Data?

Data is the information that a program reads, processes, modifies, or produces.

Examples:

- Numbers: 100, 500
- Text: "Sovon"
- Lists: [10, 20, 30]
- Expenses, customer records, temperatures, and passwords.

Consider:

```python
expenses = [12, 45, 9, 20]
```

Here, expenses stores a list containing four numbers.

Remember:

```text
Program = Instructions (What to do)
Data    = Information (What to work on)
```

The same algorithm can process different datasets without changing its basic instructions.

## 5. Source Code vs Runtime Behavior

These are two important programming concepts.

Source Code: The human-readable Python instructions written and saved in a .py file.

Runtime Behavior: What actually happens when the program executes, including calculations, output, and errors.

Example:

```python
total = 86
count = 4
average = total / count
print(average)
```

Output:

```text
21.5
```

Now change the data:

```python
total = 86
count = 0
average = total / count
print(average)
```

Output:

```text
ZeroDivisionError
```

Why?

Because division by zero is not allowed in Python.

Important lesson: The source code remained the same, but changing the data changed the runtime behavior.

Therefore, code that looks correct does not necessarily work correctly for every input.

## 6. How Python Executes a Program

When you execute a Python file using your terminal:

```bash
python my_program.py
```

The following process happens:

1. Read: The Python interpreter opens and reads your source file.
2. Syntax checking: Python checks whether your code follows Python's grammar rules. Invalid syntax produces a SyntaxError.
3. Compilation: In CPython, Python compiles the source code into an internal representation called bytecode.
4. Execution: The Python interpreter executes the instructions.
5. Output or errors: The program may display results, modify data, or produce errors.

By default, Python executes instructions from top to bottom, one at a time.

Later, you will learn control-flow concepts such as selection and iteration, which allow Python to change this execution order.

## 7. Practical Coding Example: Adding Expenses

Let's understand how an algorithm works through Python code.

```python
expenses = [12, 45, 9, 20]
total = 0
total = total + expenses[0]
total = total + expenses[1]
total = total + expenses[2]
total = total + expenses[3]
print(total)
```

Output:

```text
86
```

Explanation:

- expenses stores four expense values.
- total = 0 initializes the running total.
- expenses[0] accesses the first element.
- expenses[1] accesses the second element.
- Python list indexing starts from 0, not 1.
- Each instruction adds another expense to total.
- print(total) displays the final result.

The algorithm is: Start at zero, add every expense, and display the total.

Later, you will learn to perform this operation more efficiently using loops.

## 8. Common Beginner Mistakes

1. Assuming code is correct just because there are no typing mistakes. It can still produce incorrect results or runtime errors.
2. Forgetting that Python normally executes instructions from top to bottom.
3. Confusing an algorithm with its Python implementation.
4. Forgetting quotation marks around text.

For example:

```python
print("Hello")
```

Correct.

```python
print(Hello)
```

Incorrect if Hello has not been defined as a variable.

## 9. Practical Exercises

Complete these four exercises:

1. Print your name and calculate its character count using len().

```python
print("Sovon")
print(len("Sovon"))
```

2. Write an algorithm to determine whether a shopping basket exceeds a spending budget. First write the steps in English, then implement them in Python.
3. Modify the expense example to use five different numbers. Predict the total before executing the program.
4. Modify the average calculation so that when count = 0, it displays:

```text
Cannot compute an average with zero items.
```

### Problem: Check Whether a Shopping Basket Exceeds a Spending Budget

Objective: Write an algorithm that calculates the total cost of items in a shopping basket and determines whether the total exceeds the available budget.

#### Step 1. Understand the problem

Suppose you have a shopping basket containing:

| Item | Price |
| --- | --- |
| Laptop bag | ₹1,000 |
| Keyboard | ₹1,500 |
| Mouse | ₹500 |
| Headphones | ₹2,000 |
| Total | ₹5,000 |

Your available budget is ₹4,000.

Since ₹5,000 is greater than ₹4,000, your shopping basket exceeds the budget.

#### Step 2. Write the algorithm in simple English

An algorithm is simply a sequence of instructions that tells a computer how to solve a problem.

Algorithm:

1. Start.
2. Initialize the shopping basket with the prices of all items.
3. Initialize the available spending budget.
4. Set the total basket cost to zero.
5. Go through each item in the shopping basket.
6. Add the price of each item to the total basket cost.
7. Compare the total basket cost with the available budget.
8. If the total cost is greater than the budget, display "Budget Exceeded".
9. Otherwise, display "Within Budget".
10. Stop.

#### Step 3. Implement the algorithm in Python

```python
# Step 1: Define shopping basket
shopping_basket = [1000, 1500, 500, 2000]

# Step 2: Define spending budget
budget = 4000

# Step 3: Initialize total cost
total_cost = 0

# Step 4: Calculate total basket cost
for price in shopping_basket:
    total_cost = total_cost + price

# Step 5: Compare total cost with budget
if total_cost > budget:
    print("Budget Exceeded")
else:
    print("Within Budget")

# Step 6: Display total cost
print("Total Basket Cost:", total_cost)
```

#### Step 4. Understand the output

PYTHON OUTPUT

```text
Budget Exceeded
Total Basket Cost: 5000
```

Calculation

- Total basket cost = ₹5,000
- Available budget = ₹4,000
- Difference = ₹1,000

Budget exceeded by ₹1,000

If you haven't learned if statements yet, write the algorithm in plain English first.

## 10. Connection to Applied AI and Agentic AI Engineering

These three concepts are fundamental to building AI systems.

| Concept | Application in AI Engineering |
| --- | --- |
| Algorithm | Steps an AI agent follows to complete a task |
| Data | User requests, documents, and tool results |
| Program | Python code that executes the AI agent |

For example, an AI agent receives a user's question (data), follows a defined workflow (algorithm), and executes that workflow through Python code (program).

Testing with different inputs is essential because an AI system's runtime behavior depends heavily on the data it receives.
