# Algorithms, Programs, and Data

> **Reference file:** `01-algorithms-programs-and-data.md`  
> **Stage:** Stage 1 — Programming & Computational Thinking  
> **Section:** 01 — Computational Thinking and Program Design  
> **Purpose:** Consolidated lesson reference, including the lesson explanations and the exercises discussed and worked through.

---

## 1. Why this topic matters

Every piece of software you will ever build — from a simple expense tracker to a future AI agent — is made of the same three ingredients:

- **Data:** information.
- **Algorithm:** a plan for what to do with that information.
- **Program:** the plan written in a language a computer can run.

If you do not clearly understand these three ideas and how they fit together, every later topic will feel like memorized syntax instead of something you actually understand. This topic gives you the vocabulary and mental model that the rest of this stage builds on.

## 2. Learning outcomes

By the end of this lesson, you will be able to:

- Explain, in your own words, what an algorithm is and give an everyday example that is not a computer program.
- Explain the difference between a **program** and the **data** it works with.
- Explain the difference between **source code** and **runtime behavior**.
- Describe, at a high level, what happens when Python runs a file.
- Write and run your first Python program.

## 3. Prerequisites

- A working computer with Python installed (from Stage 0).
- Comfort opening a terminal and running a simple command.
- No prior programming knowledge is required.

## 4. Key terms

| Term | Plain-English definition |
|---|---|
| **Algorithm** | A finite, well-defined sequence of steps for solving a specified problem. |
| **Program** | A set of instructions written in a programming language that a computer can execute to perform a task. A program may implement one or more algorithms. |
| **Data** | The information a program reads, uses, changes, or produces (numbers, text, lists of values, and so on). |
| **Source code** | Human-readable program text, written or generated in a programming language and stored in a source file, which is read before the computer runs it. |
| **Runtime behavior** | What actually happens — the calculations, the output, any errors — while the program is running. |
| **Interpreter** | A program (here, `python`) that reads your source code and carries out its instructions one by one. |
| **Instruction** | One single step the computer is told to do, such as “add these two numbers” or “print this text.” |

## 5. Step-by-step explanation

### 5.1 An algorithm is not a computer thing — it is a plan

An algorithm is just a clear set of steps for solving a problem. You already use algorithms every day without calling them that.

A recipe is an algorithm:

1. Boil water.
2. Add pasta.
3. Wait 10 minutes.
4. Drain.

Following a recipe correctly produces the dish it describes. A bad recipe — one that skips steps or is vague (“cook until done”) — produces inconsistent results.

A good algorithm should have clear steps, terminate when it should, and produce a correct result according to the problem's specification. Good algorithms share three qualities:

- **Precise:** each step is unambiguous.
- **Finite:** the steps come to an end; they do not run forever.
- **Correct:** following the steps actually solves the stated problem, as the problem is specified.

### 5.2 Inputs and outputs

A common way to describe an algorithm is the **input-process-output** model: it takes some **input**, performs operations on that input or on some state, and produces an **output** (a result).

Not every algorithm fits this exact model, though: some work on existing state, or need no explicit external input.

Example:

```text
Problem: Calculate the total cost of a shopping basket.
Input:   A collection of item prices.
Output:  The total price.
```

This is only a starting mental model; a later topic (`03-input-process-output.md`) covers input, process, and output in detail.

### 5.3 A program is written for a computer

A computer cannot read a recipe written in casual English. A **program** is a set of instructions written in a **programming language** — a strict, limited language with exact rules — that a computer can execute to perform a task.

A program may implement one or more algorithms. In this curriculum, that language is **Python**.

### 5.4 Data is what the algorithm works on

Algorithms usually operate on input data or state to produce a result.

**Data** is that “something”: a person's name, a list of expenses, a password someone typed, today's temperature. The same algorithm (for example, “add up all the numbers in this list”) can run on many different pieces of data (different lists of numbers) and still follow the exact same steps.

It helps to keep these two ideas separate:

```text
Program  = the set of instructions that define what the computer can do (the recipe)
Data     = the information those instructions operate on (today's ingredients)
```

### 5.5 Source code versus runtime behavior

**Source code** is the program text in a file (typed by you or generated by software). It sits there, unmoving, like a recipe printed on paper.

**Runtime behavior** is what happens when that recipe is actually followed: pots heat up, water boils, pasta gets cooked. In programming terms:

- Source code is the `.py` file on your disk.
- Runtime behavior is what you see happen — numbers calculated, text printed, errors shown — when you actually run that file.

This distinction matters because a program can look correct as source code (no typing mistakes) but still behave incorrectly at runtime (wrong answer, crash, or unexpected result).

Reading code is not the same as knowing what it will do. You have to trace through it, which you will practice in `07-pseudocode-flowcharts-and-dry-runs.md`.

### 5.6 How Python actually runs your instructions

At a beginner level, you can think of Python as executing a program in order, from top to bottom, unless a control-flow construct changes that order.

When you type:

```bash
python my_program.py
```

in a terminal, roughly the following happens:

1. The **Python interpreter** (a program installed on your machine) opens your file and reads the source code as text.
2. It checks that the text follows Python's grammar rules (this is called **syntax**). If it does not, you get a `SyntaxError` before anything runs.
3. If the syntax is valid, the interpreter goes through your instructions **one at a time, from top to bottom**, and carries each one out.
4. Each instruction can produce output (text on the screen), change some data, or cause an error that stops the program.

This “one instruction at a time, top to bottom” behavior is the default. Later topics (selection and iteration) show how you can make Python skip some instructions or repeat others.

A more precise picture separates three stages: the source code is first **processed** (read and checked), then **compiled**, then **executed**.

In **CPython** (the standard Python implementation, and the one this curriculum assumes), the source is parsed and compiled into an internal form called **bytecode** before that bytecode is executed. Other Python implementations may use different execution mechanisms.

In every case, the beginner mental model still holds: simple statements normally take effect in order, and control-flow constructs can change that order. You do not need to understand bytecode or implementation details yet; they are covered in `02-Python-Core-Language-and-Data-Types`.

## 6. Examples

### 6.1 Example 1 — Your first program: a single instruction

```python
print("Hello, this is my first program.")
```

**Plain-English explanation:**

- `print(...)` is a built-in function that displays whatever is inside the parentheses on the screen.
- `"Hello, this is my first program."` is a piece of **data** — specifically text, which in programming is called a **string**. The quotation marks tell Python “this is text, not an instruction.”
- When you run this file, the interpreter reads this one line, recognizes `print` as a built-in function, and carries out the call: it shows the text on the screen.
- There is one instruction and no data was changed — only shown.

**Expected output:**

```text
Hello, this is my first program.
```

### 6.2 Example 2 — A tiny algorithm: adding up expenses

This example shows an algorithm (a small plan), some data, and a program that carries out the plan.

```python
expenses = [12, 45, 9, 20]
total = 0
total = total + expenses[0]
total = total + expenses[1]
total = total + expenses[2]
total = total + expenses[3]
print(total)
```

**Plain-English explanation:**

- `expenses = [12, 45, 9, 20]` creates a piece of data: a **list** of four numbers, representing four amounts of money spent. The list is stored under the name `expenses` so we can refer to it later.
- `total = 0` creates a second piece of data, a single number, and gives it the name `total`. It starts at zero because nothing has been added yet. This is the **running total** the algorithm will build up.
- `total = total + expenses[0]` looks up the first item in the list (`expenses[0]` — the first position, counting from zero) and adds it to whatever `total` currently is, then stores the new result back into `total`. After this line, `total` is `12`.
- The next three lines repeat the same idea for the second, third, and fourth items in the list (`expenses[1]`, `expenses[2]`, `expenses[3]`). After all four lines, `total` holds `12 + 45 + 9 + 20 = 86`.
- `print(total)` displays the final answer, `86`.

**Expected output:**

```text
86
```

Notice the **algorithm** here is simple and reusable: “start at zero, add each number one at a time.” The **data** (`expenses`) could be completely different numbers and the same steps would still work — that is exactly why separating algorithm from data is powerful.

You will learn a much shorter way to write this using a loop in `04-sequence-selection-iteration-and-abstraction.md`. Writing it out by hand here is intentional, so you can see every single step.

### 6.3 Example 3 — Source code versus runtime behavior, made visible

This example deliberately shows how the exact same line of source code can behave differently depending on the data it is given, and how an error at runtime is different from a mistake in the source code itself.

```python
total = 86
count = 4
average = total / count
print(average)

total = 86
count = 0
average = total / count
print(average)
```

**Plain-English explanation:**

- `total = 86` and `count = 4` create two pieces of data: a total amount (for example, the sum from Example 2) and how many items made up that total.
- `average = total / count` divides `total` by `count` using Python's division operator `/`, and stores the result under the name `average`. `print(average)` then displays it. At **runtime**, this first block prints `21.5`.
- The second block assigns new data to `total` and `count`, then runs the **exact same line of source code** again — `average = total / count`, unchanged, character for character.
- This time `count` is `0`. Dividing by zero is not allowed, so Python stops the program right there and shows a `ZeroDivisionError` instead of printing anything. The second `print(average)` is never reached, because the division raises an exception first.

**Expected behavior:** the first block prints `21.5`. The second block raises a `ZeroDivisionError` with a message such as “division by zero” (the exact traceback wording can vary across Python versions and environments).

This is the key lesson: the **source code never changed** — the division line looks identical both times. But the **runtime behavior** changed completely because the **data** changed. A program that looks correct on paper can still fail at runtime for certain inputs. Thinking about which inputs might break your code is exactly what `06-preconditions-postconditions-and-edge-cases.md` is about.

## 7. Common beginner mistakes

- **Confusing “the code looks right” with “the code is correct.”** Code with no red underlines or typos can still produce the wrong answer or crash on certain data, as Example 3 showed.
- **Forgetting that computers execute instructions in order, one at a time.** Beginners sometimes expect Python to “notice” a later line and use it earlier. It never does — it always goes top to bottom (until you learn about loops and functions, which control this more precisely).
- **Mixing up an algorithm with its implementation.** “Add up the numbers” is the algorithm; the specific Python lines that do it are one possible implementation. The same algorithm can be written in many different ways.
- **Not distinguishing text from instructions.** Forgetting the quotation marks around text (for example, writing `print(Hello)` instead of `print("Hello")`) makes Python think `Hello` is the name of some data, which usually causes an error.

## 8. Try it yourself — original exercises

Do not look up full solutions. Use the engineering loop from the module README:

**understand → predict → implement → test → debug → refactor → document → explain aloud**

### Exercise 1

Write a program that prints your name and then, on a separate line, prints how many letters are in it.

Hint: `len("some text")` gives you the number of characters in a piece of text.

### Exercise 2

Write down, in plain English, an algorithm (just the steps, no code) for deciding whether a bag of groceries is “over budget” if a shopper has a spending limit.

Only after writing the steps in English, translate them into a Python program.

### Exercise 3

Take Example 2 (adding up expenses) and change the data — use a list of five different numbers of your choosing.

Predict the total before you run it, then check if you were right.

### Exercise 4

Change Example 3 so that instead of crashing when `count` is `0`, it prints a friendly message like:

```text
Cannot compute an average with zero items.
```

First describe in plain English how the program should behave when `count` is `0`.

If you already know how to use `if`, implement your solution in Python. Otherwise, write only the algorithm for now; you will implement it when you learn selection.

## 9. Exercise discussion — explanations and worked solutions

The following records the exercise examples and explanations discussed during the lesson review.

### 9.1 Exercise 1 — Print a name and its character count

**Goal:** Print a name, then print how many characters are in that name on a separate line.

**Worked solution:**

```python
name = "Sovon"
print(name)
print(len(name))
```

**Expected output:**

```text
Sovon
5
```

**Explanation:**

1. `name = "Sovon"` stores the text `"Sovon"` in a variable named `name`.
2. `print(name)` displays the stored text.
3. `len(name)` calculates the number of characters in the string stored in `name`.
4. `print(len(name))` displays that count on a separate line.

The output is `5` because the string `"Sovon"` contains five characters.

### 9.2 Exercise 2 — Decide whether groceries are over budget

**Goal:** First describe the algorithm in plain English. Then translate it into Python.

**Example scenario:**

- Spending limit (budget): `1000`
- Rice: `300`
- Milk: `100`
- Vegetables: `250`
- Fruits: `200`

**Plain-English algorithm:**

1. Set the shopper's spending limit (budget).
2. Record the prices of the grocery items.
3. Add all item prices to calculate the total spending.
4. Compare the total spending with the budget.
5. If the total spending is greater than the budget, report that the budget has been exceeded.
6. Otherwise, report that the spending is within budget.

**Worked Python solution:**

```python
budget = 1000
rice = 300
milk = 100
vegetables = 250
fruits = 200

total_spending = rice + milk + vegetables + fruits

print("Total spending:", total_spending)

if total_spending > budget:
    print("Budget exceeded")
else:
    print("Within budget")
```

**Expected output:**

```text
Total spending: 850
Within budget
```

**Explanation:**

- `budget = 1000` stores the shopper's maximum spending limit.
- The next four assignments store the prices of the grocery items.
- `total_spending = rice + milk + vegetables + fruits` adds all four prices: `300 + 100 + 250 + 200 = 850`.
- `print("Total spending:", total_spending)` displays the calculated total.
- `if total_spending > budget:` checks whether the total is greater than the budget.
- Since `850` is not greater than `1000`, Python executes the `else` branch and displays `Within budget`.

**Important learning-level note:** This solution uses `if` and `else`. At this point in the roadmap, conditional statements have not yet been formally taught. The code is therefore a preview to demonstrate how the English algorithm can later be implemented. Do not treat `if`/`else` as a concept you must memorize before reaching the control-flow topic.

The algorithm itself should be understood now: calculate the total, compare it with the budget, and describe both possible outcomes.

### 9.3 Exercise 3 — Change the expense data and predict the total

**Goal:** Use five different numbers, predict their sum before running the program, and then verify the result.

**Chosen data:**

```python
expenses = [100, 250, 150, 300, 200]
```

**Prediction before execution:**

```text
100 + 250 + 150 + 300 + 200 = 1000
```

The predicted total is **1000**.

**Worked Python solution:**

```python
expenses = [100, 250, 150, 300, 200]
total = 0

total = total + expenses[0]
total = total + expenses[1]
total = total + expenses[2]
total = total + expenses[3]
total = total + expenses[4]

print(total)
```

**Expected output:**

```text
1000
```

**Step-by-step dry run:**

| Step | Operation | Value of `total` after the operation |
|---:|---|---:|
| Initial | `total = 0` | 0 |
| 1 | `total = total + expenses[0]` → `0 + 100` | 100 |
| 2 | `total = total + expenses[1]` → `100 + 250` | 350 |
| 3 | `total = total + expenses[2]` → `350 + 150` | 500 |
| 4 | `total = total + expenses[3]` → `500 + 300` | 800 |
| 5 | `total = total + expenses[4]` → `800 + 200` | 1000 |

**Explanation:**

- The list contains five values: `100`, `250`, `150`, `300`, and `200`.
- `total = 0` initializes the running total.
- Python list indexing starts at zero. Therefore, `expenses[0]` accesses the first item, and `expenses[4]` accesses the fifth item.
- Each assignment adds one list item to the current running total and stores the new result back in `total`.
- After all five additions, `total` is `1000`.
- `print(total)` displays the result.

The prediction and program output match: both are `1000`.

### 9.4 Exercise 4 — Handle a zero count without dividing

**Goal:** Change the average-calculation behavior so the program does not attempt to divide by zero. It should display a friendly message when `count` is zero.

The original calculation is:

```python
average = total / count
```

When `count` is `0`, Python raises a `ZeroDivisionError`. The intended friendly message is:

```text
Cannot compute an average with zero items.
```

**Plain-English algorithm:**

1. Store the total.
2. Store the count.
3. Check whether the count is zero.
4. If the count is zero, display `Cannot compute an average with zero items.` and do not perform division.
5. Otherwise, calculate the average by dividing the total by the count.
6. Display the calculated average.

**Dry run A — count is 4:**

Given:

```python
total = 86
count = 4
```

- Check whether `count` is zero.
- `count` is `4`, so it is not zero.
- Calculate `86 / 4`.
- The average is `21.5`.
- Display `21.5`.

Expected result:

```text
21.5
```

**Dry run B — count is 0:**

Given:

```python
total = 86
count = 0
```

- Check whether `count` is zero.
- `count` is `0`.
- Display the friendly message.
- Do not perform `86 / 0`.
- The program avoids the `ZeroDivisionError`.

Expected result:

```text
Cannot compute an average with zero items.
```

**Why the Python implementation was not written yet:**

The lesson explicitly says that learners who already know `if` may implement this exercise in Python; otherwise, they should write only the algorithm and implement it after learning selection.

At this learning point, conditional statements have not yet been formally covered. Therefore, the exercise was completed at the algorithm and dry-run level. The Python conditional implementation is intentionally deferred until the roadmap teaches selection (`if`/`else`).

## 10. Original lesson — How to know you are done

1. Your name is printed, the character count appears on a separate line, and the count matches what `len()` gives for your chosen string.
2. You wrote the English algorithm first, and it says what happens when spending is within the limit and when it exceeds the limit. If you implemented it in Python, the result matches those stated rules.
3. Your list has five numbers of your choosing, you predicted the total before running, and the program prints the correct sum of all five.
4. You described the intended behavior for `count` being zero. If you implemented it, the program checks for zero before dividing and shows the friendly message for zero items; otherwise a plain-English algorithm is sufficient.

## 11. Lesson summary

- An **algorithm** is a finite, well-defined sequence of steps for solving a specified problem.
- Algorithms are commonly described as taking input, processing it (or existing state), and producing an output (a result), though some need no explicit external input.
- A **program** is a set of instructions written in a language, like Python, that a computer can execute to perform a task; it may implement one or more algorithms.
- **Data** is the information a program works on; the same algorithm can run on many different pieces of data.
- **Source code** is the human-readable text stored in a source file; **runtime behavior** is what actually happens when that code runs, which can depend heavily on the data it is given.
- At a beginner level, Python runs your instructions in order, from top to bottom, unless a control-flow construct changes that order.

## 12. Completion checklist

- [ ] I can explain, without notes, what an algorithm is using a non-computer example.
- [ ] I can explain the difference between a program and the data it processes.
- [ ] I can explain the difference between source code and runtime behavior, using an example where the same code behaves differently on different data.
- [ ] I have run at least one Python program myself, not just read one.
- [ ] I have completed the “try it yourself” exercises above.

## 13. Connection to later Applied AI and Agentic AI engineering work

Later, when you build AI-powered tools and agents, you will constantly work with this same triangle:

- **Algorithm:** the plan an agent follows to complete a task.
- **Data:** the user's request, documents, or tool results.
- **Program:** the Python code that actually runs the agent.

You will also see the source-code-versus-runtime-behavior lesson again in a bigger way: an AI agent's code can look correct, but its behavior at runtime depends heavily on the data it receives (the user's input, or what a tool returns). This is exactly why careful testing with different kinds of data, starting in this module, matters so much.

## 14. Knowledge-check questions discussed after the exercises

Use these questions to check whether the core concepts are understood. The answers are intentionally not included here so that the questions can be used for self-testing.

1. **What is the difference between an algorithm and a program?**
2. **In the expression `expenses[0]`, which item is being accessed?**
3. **Why should a program check whether `count` is zero before calculating an average?**

---

**Scope note:** This reference consolidates the original lesson and the exercise explanations discussed in the learning session. The sections titled “Final Exercise Review” and “One important distinction” have intentionally been omitted as requested.
