# Lesson 01: Python Files, Interpreter, REPL, and Indentation

This lesson explains how Python code is written, where it is stored, how it executes, and how Python understands the structure of your code.

The central idea is simple: Before learning to build programs, you must understand how Python reads and executes them.

---

## 1. What is a Python file?

A Python file is a normal text file containing Python source code. Its filename normally ends with `.py`.

Example:

```python
# hello.py
print("Hello, Python!")
```

Here:

- `hello.py` is the Python file.
- `print("Hello, Python!")` is the source code.
- The file stores instructions but does not execute them automatically.
- Python needs an interpreter to execute those instructions.

Think of a Python file as a recipe: it contains instructions, but someone must read and follow them.

---

## 2. What is a Python interpreter?

A Python interpreter is a program installed on your computer that reads, checks, prepares, and executes Python code.

Its basic workflow:

1. Reads your `.py` file.
2. Parses the code according to Python's grammar.
3. Prepares the code for execution.
4. Executes instructions according to their order and control flow.

For example, when you execute `hello.py`, the interpreter reads the file and displays its output.

Without the interpreter, your Python file is simply text stored on your computer.

---

## 3. How to check Python installation

Open your terminal and execute:

```bash
python3 --version
```

On some systems, use:

```bash
python --version
```

Example output:

```text
Python 3.12.4
```

This confirms that Python is installed and shows its version.

If you receive `command not found`, Python might not be installed, or your terminal might not be able to locate it.

---

## 4. How to create and execute a Python file

Follow these steps:

1. Open VS Code or another text editor.
2. Create a file named `hello.py`.
3. Write the following code:

```python
print("Hello, Python!")
```

4. Save the file.
5. Open your terminal and navigate to the folder containing the file.
6. Execute:

```bash
python3 hello.py
```

Output:

```text
Hello, Python!
```

**Important:** Every normal script execution starts with a fresh Python process. Variables from the previous execution are not retained in memory, although external changes, such as writing to files or databases, can remain.

---

## 5. What is REPL?

REPL stands for **Read–Eval–Print Loop**.

It is an interactive Python environment where you write code, Python executes it immediately, and displays the result.

Start it using:

```bash
python3
```

Example:

```python
>>> 2 + 2
4
>>> print("Hello")
Hello
```

REPL is useful for:

- Quickly testing mathematical expressions.
- Checking how Python functions work.
- Experimenting with unfamiliar syntax.
- Testing small pieces of code.

You can also write multiline statements, such as:

```python
>>> if True:
...     print("Hello")
...
Hello
```

Exit REPL using:

```python
exit()
```

Alternatively:

- Linux/macOS: `Ctrl + D`
- Windows: `Ctrl + Z`, then `Enter`.

### Python file vs REPL

| Python file (`.py`) | REPL |
|---|---|
| Code is saved on disk. | Code is not automatically saved. |
| Runs the script when requested. | Executes input interactively. |
| Suitable for real programs. | Suitable for quick experiments. |
| Can be reused and shared. | In-memory state disappears when the session ends. |

---

## 6. What are comments?

Comments are notes written for humans reading the code. Python ignores them during execution.

A comment starts with `#`.

```python
# This program greets the user.
print("Hello!")
```

Only the `print()` instruction executes.

Comments improve code readability and help developers understand why particular instructions exist.

---

## 7. What is indentation?

Indentation means spaces at the beginning of a line.

Python uses indentation to understand which instructions belong together in a code block.

Unlike languages that use `{}` to define blocks, Python uses indentation.

Example:

```python
age = 20

if age >= 18:
    print("You are an adult.")
    print("You can vote.")

print("This always runs.")
```

Explanation:

- `if age >= 18:` checks whether the age is at least 18.
- The two indented statements belong to the `if` block.
- They execute only when the condition is true.
- The final statement is outside the block, so it always executes.

Important indentation rules:

- Use four spaces per indentation level.
- Maintain consistent indentation.
- Never mix tabs and spaces.
- VS Code can automatically insert spaces when you press Tab.

---

## 8. Common Python errors

Three important errors introduced in this lesson:

| Error | Meaning | Example |
|---|---|---|
| `SyntaxError` | Code violates Python grammar. | Missing `:` after an `if` statement. |
| `IndentationError` | Incorrect indentation. | Missing indentation inside an `if` block. |
| `NameError` | Using a name that has not been defined. | `print(Hello)` when `Hello` does not exist. |

A `TabError` is a specific type of `IndentationError` caused by inconsistent mixing of tabs and spaces.

**Important difference:** Syntax and indentation errors are normally detected before a script executes. A runtime error such as `NameError` occurs when Python executes the problematic statement. Earlier statements may already have executed.

---

## 9. Three practical examples

### Example 1: Basic Python program

```python
# Display a greeting
print("Hello, Python!")
```

### Example 2: Variables and sequential execution

```python
name = "Asha"
favorite_number = 7

print("This program belongs to", name)
print("Their favorite number is", favorite_number)
```

Output:

```text
This program belongs to Asha
Their favorite number is 7
```

### Example 3: Conditional execution

```python
age = 20

if age >= 18:
    print("You are old enough to vote.")
    print("You are an adult.")

print("Program completed.")
```

This demonstrates how indentation determines which statements belong to a condition.

---

## 10. Common beginner mistakes

Remember these six mistakes:

1. Forgetting the colon after an `if` statement.
2. Using inconsistent indentation inside a block.
3. Mixing tabs and spaces.
4. Confusing REPL with a permanently saved Python file.
5. Running a file from the wrong directory or using the wrong filename.
6. Forgetting quotation marks around text. For example, `print(Hello)` treats `Hello` as a variable name, not text. If it is undefined, Python raises `NameError`.

---

## 11. Practical exercises

The lesson requires you to complete five exercises:

1. Check your installed Python version using `python3 --version`.
2. Create `about_me.py` with your name, age, and a print statement.
3. Start REPL, test three or four expressions, and exit correctly.
4. Remove indentation from an `if` block and observe the resulting error. Restore it afterward.
5. Change the age in Example 3 to a number below 18. Predict the output before executing the program.

---

## 12. Why this matters for Data Engineering and AI Engineering

Every Python-based system starts with Python source code executed by the interpreter.

The same fundamentals apply when building:

- Data ingestion scripts.
- ETL and ELT pipelines.
- Data processing applications.
- Machine learning pipelines.
- AI applications and agents.
- Automation scripts.

Understanding REPL helps you experiment quickly, while understanding files and indentation helps you build maintainable programs and debug errors.
