# Algorithms, Programs, and Data

## Why this topic matters

Every piece of software you will ever build — from a simple expense tracker
to a future AI agent — is made of the same three ingredients: **data**
(information), an **algorithm** (a plan for what to do with that
information), and a **program** (the plan written in a language a computer
can run). If you do not clearly understand these three ideas and how they
fit together, every later topic will feel like memorized syntax instead of
something you actually understand. This topic gives you the vocabulary and
mental model that the rest of this stage builds on.

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain, in your own words, what an algorithm is and give an everyday
  example that is not a computer program.
- Explain the difference between a **program** and the **data** it works
  with.
- Explain the difference between **source code** and **runtime behavior**.
- Describe, at a high level, what happens when Python runs a file.
- Write and run your first Python program.

## Prerequisites

- A working computer with Python installed (from Stage 0).
- Comfort opening a terminal and running a simple command.
- No prior programming knowledge is required.

## Key terms

| Term | Plain-English definition |
|---|---|
| **Algorithm** | A precise, step-by-step plan for solving a problem, written so clearly that anyone (or any machine) following the steps gets the same correct result every time. |
| **Program** | An algorithm written in a language a computer can actually run, such as Python. |
| **Data** | The information a program reads, uses, changes, or produces (numbers, text, lists of values, and so on). |
| **Source code** | The text of a program, exactly as a human types and reads it, before the computer runs it. |
| **Runtime behavior** | What actually happens — the calculations, the output, any errors — while the program is running. |
| **Interpreter** | A program (here, `python`) that reads your source code and carries out its instructions one by one. |
| **Instruction** | One single step the computer is told to do, such as "add these two numbers" or "print this text." |

## Step-by-step explanation

### 1. An algorithm is not a computer thing — it is a plan

An algorithm is just a clear set of steps for solving a problem. You already
use algorithms every day without calling them that. A recipe is an
algorithm: "1. Boil water. 2. Add pasta. 3. Wait 10 minutes. 4. Drain."
Following a recipe correctly always produces the same dish. A bad recipe —
one that skips steps or is vague ("cook until done") — produces
inconsistent results. Good algorithms share three qualities:

- **Precise** — each step is unambiguous.
- **Finite** — the steps come to an end (they don't run forever).
- **Correct** — following the steps actually solves the stated problem.

### 2. A program is an algorithm written for a computer

A computer cannot read a recipe written in casual English. A **program** is
the same kind of step-by-step plan, but written in a **programming
language** — a strict, limited language with exact rules, so that a
machine can follow it with zero ambiguity. In this curriculum, that language
is **Python**.

### 3. Data is what the algorithm works on

An algorithm is useless without something to act on. **Data** is that
"something": a person's name, a list of expenses, a password someone typed,
today's temperature. The same algorithm (for example, "add up all the
numbers in this list") can run on many different pieces of data (different
lists of numbers) and still follow the exact same steps.

It helps to keep these two ideas separate in your head:

```text
Program  = the fixed set of steps (the recipe)
Data     = the specific information the steps are applied to (today's ingredients)
```

### 4. Source code versus runtime behavior

**Source code** is the text you type into a file — it just sits there,
unmoving, like a recipe printed on paper. **Runtime behavior** is what
happens when that recipe is actually followed: pots heat up, water boils,
pasta gets cooked. In programming terms: source code is the `.py` file on
your disk; runtime behavior is what you see happen (numbers calculated,
text printed, errors shown) when you actually run that file.

This distinction matters because a program can look correct as source code
(no typing mistakes) but still behave incorrectly at runtime (wrong
answer, crash, or unexpected result). Reading code is not the same as
knowing what it will do — you have to trace through it, which you will
practice in [topic 7](07-pseudocode-flowcharts-and-dry-runs.md).

### 5. How Python actually runs your instructions

Python is what's called an **interpreted** language. When you type
`python my_program.py` in a terminal, here is roughly what happens:

1. The **Python interpreter** (a program installed on your machine) opens
   your file and reads the source code as text.
2. It checks the text follows Python's grammar rules (this is called
   **syntax**). If it doesn't, you get a `SyntaxError` before anything
   runs.
3. If the syntax is valid, the interpreter goes through your instructions
   **one at a time, from top to bottom**, and carries each one out
   immediately.
4. Each instruction can produce output (text on the screen), change some
   data, or cause an error that stops the program.

This "one instruction at a time, top to bottom" behavior is the default.
Later topics (selection and iteration) show how you can make Python skip
some instructions or repeat others — but underneath, it is always
processing one instruction at a time.

## Examples

### Example 1 — Your first program: a single instruction

```python
print("Hello, this is my first program.")
```

**Plain-English explanation:**

- `print(...)` is a built-in Python instruction that displays whatever is
  inside the parentheses on the screen.
- `"Hello, this is my first program."` is a piece of **data** — specifically
  text, which in programming is called a **string**. The quotation marks
  tell Python "this is text, not an instruction."
- When you run this file, the interpreter reads this one line, recognizes
  `print` as an instruction, and carries it out: it shows the text on the
  screen. There is one instruction and no data was changed — only shown.

### Example 2 — A tiny algorithm: adding up expenses

This example shows an algorithm (a small plan), some data, and a program
that carries out the plan.

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

- `expenses = [12, 45, 9, 20]` creates a piece of data: a **list** of four
  numbers, representing four amounts of money spent. The list is stored
  under the name `expenses` so we can refer to it later.
- `total = 0` creates a second piece of data, a single number, and gives it
  the name `total`. It starts at zero because nothing has been added yet.
  This is the "running total" the algorithm will build up.
- `total = total + expenses[0]` looks up the first item in the list
  (`expenses[0]` — the first position, counting from zero) and adds it to
  whatever `total` currently is, then stores the new result back into
  `total`. After this line, `total` is `12`.
- The next three lines repeat the same idea for the second, third, and
  fourth items in the list (`expenses[1]`, `expenses[2]`, `expenses[3]`).
  After all four lines, `total` holds `12 + 45 + 9 + 20 = 86`.
- `print(total)` displays the final answer, `86`.
- Notice the **algorithm** here is simple and reusable: "start at zero, add
  each number one at a time." The **data** (`expenses`) could be completely
  different numbers and the same steps would still work — that is exactly
  why separating algorithm from data is powerful. (You will learn a much
  shorter way to write this using a loop in
  [topic 4](04-sequence-selection-iteration-and-abstraction.md); writing it
  out by hand here is intentional, so you can see every single step.)

### Example 3 — Source code versus runtime behavior, made visible

This example deliberately shows how the exact same line of source code can
behave differently depending on the data it is given, and how an error at
runtime is different from a mistake in the source code itself.

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

- `total = 86` and `count = 4` create two pieces of data: a total amount
  (for example, the sum from Example 2) and how many items made up that
  total.
- `average = total / count` divides `total` by `count` using Python's
  division operator `/`, and stores the result under the name `average`.
  `print(average)` then displays it. At **runtime**, this first block
  prints `21.5`.
- The second block assigns new data to `total` and `count`, then runs the
  **exact same line of source code** again — `average = total / count`,
  unchanged, character for character.
- This time `count` is `0`. Dividing by zero is not allowed, so Python
  stops the program right there and shows a `ZeroDivisionError` instead of
  printing anything.
- This is the key lesson: the **source code never changed** — the division
  line looks identical both times. But the **runtime behavior** changed
  completely because the **data** changed. A program that looks correct on
  paper can still fail at runtime for certain inputs. Thinking about which
  inputs might break your code is exactly what
  [topic 6](06-preconditions-postconditions-and-edge-cases.md) is about.

## Common beginner mistakes

- **Confusing "the code looks right" with "the code is correct."** Code
  with no red underlines or typos can still produce the wrong answer or
  crash on certain data, as Example 3 showed.
- **Forgetting that computers execute instructions in order, one at a
  time.** Beginners sometimes expect Python to "notice" a later line and
  use it earlier. It never does — it always goes top to bottom (until you
  learn about loops and functions, which control this more precisely).
- **Mixing up an algorithm with its implementation.** "Add up the numbers"
  is the algorithm; the specific Python lines that do it are one possible
  implementation. The same algorithm can be written in many different ways.
- **Not distinguishing text from instructions.** Forgetting the quotation
  marks around text (for example, writing `print(Hello)` instead of
  `print("Hello")`) makes Python think `Hello` is the name of some data,
  which usually causes an error.

## Try it yourself

Do not look up full solutions. Use the engineering loop from the module
[README](README.md): understand, predict, implement, test, debug, refactor,
document, explain aloud.

1. Write a program that prints your name and then, on a separate line,
   prints how many letters are in it. (Hint: `len("some text")` gives you
   the number of characters in a piece of text.)
2. Write down, in plain English, an algorithm (just the steps, no code) for
   deciding whether a bag of groceries is "over budget" if a shopper has a
   spending limit. Only after writing the steps in English, translate them
   into a Python program.
3. Take Example 2 (adding up expenses) and change the data — use a list of
   five different numbers of your choosing. Predict the total before you
   run it, then check if you were right.
4. Change Example 3 so that instead of crashing when `count` is `0`, it
   prints a friendly message like `"Cannot compute an average with zero
   items."` instead. (You do not need to understand `if` yet to think
   about *what* the fix should do — just describe it in English first.)

## Summary

- An **algorithm** is a precise, step-by-step plan for solving a problem.
- A **program** is an algorithm written in a language, like Python, that a
  computer can run exactly and without ambiguity.
- **Data** is the information a program works on; the same algorithm can run
  on many different pieces of data.
- **Source code** is the fixed text of a program; **runtime behavior** is
  what actually happens when that code runs, which can depend heavily on
  the data it is given.
- Python runs your instructions one at a time, from top to bottom, checking
  the syntax first and then carrying out each instruction in order.

## Completion checklist

- [ ] I can explain, without notes, what an algorithm is using a
      non-computer example.
- [ ] I can explain the difference between a program and the data it
      processes.
- [ ] I can explain the difference between source code and runtime
      behavior, using an example where the same code behaves differently
      on different data.
- [ ] I have run at least one Python program myself, not just read one.
- [ ] I have completed the "try it yourself" exercises above.

## Connection to later Applied AI and Agentic AI engineering work

Later, when you build AI-powered tools and agents, you will constantly work
with this same triangle: an **algorithm** (the plan an agent follows to
complete a task), **data** (the user's request, documents, or tool
results), and a **program** (the Python code that actually runs the
agent). You will also see the source-code-versus-runtime-behavior lesson
again in a bigger way: an AI agent's code can look correct, but its
behavior at runtime depends heavily on the data it receives (the user's
input, or what a tool returns) — which is exactly why careful testing with
different kinds of data, starting in this module, matters so much.
