# Python Files, the Interpreter, the REPL, and Indentation

## Why this topic matters

Before you write real programs, you need to understand the physical tools
you are actually using: what a Python file is, what program actually reads
and runs your code, and the exact formatting rules Python enforces. Skipping
this feels like a shortcut, but it causes constant confusion later —
mysterious errors that are really just misunderstandings about how Python is
being run, or about spacing. This topic makes the mechanics fully explicit,
so that from here on, every error you see is about your logic, not about how
the tool works.

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain what a Python file is and what makes it different from a plain
  text file.
- Explain what the Python interpreter is and describe, at a high level, what
  it does with your code.
- Check that Python is installed and find its version from a terminal.
- Create and run a simple `.py` file from the command line.
- Explain what the Python REPL is, start it, use it for a quick check, and
  exit it correctly.
- Explain the difference between working in the REPL and running a `.py`
  file.
- Write comments using `#` and explain why comments exist.
- Explain why indentation matters in Python and use it correctly to form a
  code block.
- Recognize a `SyntaxError` and an `IndentationError` and explain, in plain
  English, what each one is telling you.

## Prerequisites

- Stage 0: a working computer with Python installed, and comfort opening a
  terminal.
- [Algorithms, Programs, and Data](../01-Computational-Thinking-and-Program-Design/01-algorithms-programs-and-data.md) —
  the algorithm / program / data / source-code / runtime vocabulary this
  lesson builds on directly.
- [Sequence, Selection, Iteration, and Abstraction](../01-Computational-Thinking-and-Program-Design/04-sequence-selection-iteration-and-abstraction.md) —
  this lesson uses one simple `if` block; the full rules for `if` were
  taught there, so it is only reused here, not re-taught.

## Key terms

| Term | Plain-English definition |
|---|---|
| **Python file** | A plain text file whose name normally ends in `.py`, containing Python source code. |
| **Interpreter** | The `python` program installed on your computer that reads a Python file's text, parses it, and executes it. |
| **Terminal** | A text window where you type commands for your computer to run, instead of clicking icons. |
| **REPL** | Short for Read–Eval–Print Loop: an interactive Python session where you type Python code, Python runs it immediately, and shows the result. |
| **Comment** | Text in a Python file that Python completely ignores; it exists only for humans reading the code. |
| **Indentation** | Blank space at the start of a line, used in Python to show which lines belong together as one block. |
| **Code block** | A group of one or more lines that belong together and run together, shown by being indented at the same level. |
| **SyntaxError** | An error Python reports when your code does not follow Python's grammar rules at all. |
| **IndentationError** | A specific kind of error caused by incorrect or inconsistent spacing at the start of lines. |

## Step-by-step explanation

### 1. What a Python file actually is

A **Python file** is just a plain text file — the same basic kind of file
you would get from a simple text editor — with one important difference:
its name normally ends in `.py` (for example, `hello.py`), and its content
follows Python's grammar. The extension is a naming convention; the
contents still need to be valid Python source code. As you learned in
[Algorithms, Programs, and Data](../01-Computational-Thinking-and-Program-Design/01-algorithms-programs-and-data.md),
this file is the **source code**: it just sits on your disk, unmoving,
until something reads and runs it.

### 2. The interpreter's job

Python is an **interpreted** language. The **interpreter** is a separate
program, already installed on your computer, whose whole job is to open a
`.py` file, read its text, parse it according to Python's grammar, prepare
it for execution, and then execute the code according to Python's rules and
control flow. For a simple script, statements normally execute in source
order unless a control-flow construct, function call, exception, or other
language feature changes what executes next. Without the interpreter, a `.py` file is just inert text sitting on a
disk — nothing happens until you ask the interpreter to run it.

### 3. Checking Python from a terminal

Before writing any code, confirm Python is available. In a terminal, type:

```text
python3 --version
```

(on some systems the command is `python --version` instead). This prints
something like `Python 3.12.4`. Seeing a version number confirms the
interpreter is installed and tells you which version you have. If you
instead see an error such as "command not found," Python is not installed,
or your terminal cannot find it — a Stage 0 environment problem to fix
before continuing, not a code problem.

### 4. Creating and running a simple `.py` file

Follow these steps once, for real, before reading further:

1. In a text editor (such as VS Code, from Stage 0), create a new file and
   save it as `hello.py`, inside a folder you can find in your terminal.
2. Type one line of code into it: `print("Hello, Python!")`
3. Save the file.
4. In your terminal, move into that folder and run:
   `python3 hello.py`
5. The interpreter reads `hello.py` from top to bottom and runs it; you
   should see `Hello, Python!` printed on the screen.

If you run the same command again, it prints the same thing again, because
you are asking the interpreter to read and run the same file a second time.
Each normal script execution starts with a fresh Python process state.
Variables and objects from the previous run are not retained in Python
memory, although changes made to external resources such as files or
databases can persist.

### 5. The REPL: an interactive Python session

Typing `python3` alone, with no filename after it, starts the **REPL**
instead of running a file. Rather than reading a whole file at once, the
REPL waits for you to type something, immediately runs it, shows you the
result, and then waits for your next input — hence the name
**Read–Eval–Print Loop**:

```text
$ python3
>>> 2 + 2
4
>>> print("hi")
hi
>>>
```

Here, `$` is the terminal prompt before starting Python, and `>>>` is the
REPL's own prompt, shown by Python itself once it is running and waiting
for your next line.

The REPL lets you enter Python interactively. Simple expressions and
statements can often be entered and evaluated immediately, while
multi-line constructs such as `if` statements, loops, and function
definitions require continuation lines (shown with the `...` prompt):

```text
>>> if True:
...     print("hello")
...
hello
```

**When to use the REPL:** quickly checking what an expression evaluates to,
testing one small idea, or exploring how an unfamiliar piece of syntax
behaves.

**When not to use the REPL:** for any real program you want to keep, reuse,
share, or run again later. Code and definitions created during a REPL
session are not automatically saved as a `.py` source file. When the Python
process ends, its in-memory program state is gone, although your terminal
or interactive environment may retain command history.

**Exiting the REPL:** type `exit()` and press Enter, or press `Ctrl-D` (on
Linux or macOS) or `Ctrl-Z` followed by Enter (on Windows).

The core difference to remember:

```text
.py file  = saved permanently, runs top-to-bottom all at once when you run it,
            used for real programs you keep.
REPL      = not saved as a file, runs each statement as you enter it,
            used only for quick, throwaway experiments.
```

### 6. Comments: notes that Python ignores

A **comment** starts with `#`. Everything after `#` on that line is ignored
completely by the interpreter — it has zero effect on what the program
does. Comments exist purely to explain something to a human reading the
code later (including your future self):

```python
# This program greets the user.
print("Hello!")  # this line displays the greeting
```

Both comments above are ignored when this file runs; only `print("Hello!")`
actually does anything.

### 7. Indentation and code blocks

Many programming languages use symbols such as `{` and `}` to show which
lines belong together. Python instead uses **indentation** — consistent
leading spaces at the start of a line — for the same purpose. Any lines
indented at the same level, placed directly under a line that ends in `:`,
form one **code block**, and Python treats them as belonging together:

```python
age = 20
if age >= 18:
    print("You are an adult.")
    print("You can vote.")
print("This runs no matter what age is.")
```

The two indented `print` lines are inside the `if` block, so they only run
when the condition is true. The third `print` line is not indented, so it
is outside the `if` block entirely — it always runs, regardless of `age`,
because Python's default behavior (as you saw in
[Algorithms, Programs, and Data](../01-Computational-Thinking-and-Program-Design/01-algorithms-programs-and-data.md))
is to run statements in sequence, one after another.

**The rule that matters most:** use consistent spacing throughout an entire
file. Python requires consistent indentation to define blocks, and four
spaces per indentation level is the standard Python style convention. Never
mix tabs and spaces: mixing them inconsistently can cause a `TabError`,
which is a specific subclass of `IndentationError`. The safest beginner
practice is to use spaces consistently, with 4 spaces per indentation
level. Most text editors, including VS Code, insert spaces automatically
when you press Tab, which avoids this problem entirely.

### 8. Common errors from getting this wrong

- A **`SyntaxError`** is Python's general "this does not follow Python's
  grammar at all" error — for example, forgetting the colon at the end of
  an `if` line.
- An **`IndentationError`** is a specific kind of error about incorrect or
  inconsistent spacing at the start of a line — for example, a line that
  should be indented inside a block but is not, or two lines in the same
  block that use a different number of spaces from each other.

Both errors stop the whole program before any of it runs, because the
interpreter checks that the entire file's grammar is valid before it starts
carrying out any instructions.

## Examples

### Example 1 — Your first Python file, with a comment

```python
# This is a comment: Python ignores this whole line.
print("Hello, Python!")
```

**Plain-English explanation:**

- The first line starts with `#`, so the interpreter skips it entirely —
  it produces no output and has no effect.
- `print("Hello, Python!")` is the only instruction that actually runs. It
  displays the text between the quotation marks on the screen.
- Running this file (`python3 hello.py`) prints exactly one line:
  `Hello, Python!`.
- This is the simplest possible complete Python file: one real instruction,
  plus a note for humans that the interpreter never sees as "real work."

### Example 2 — Variables and multiple instructions running in order

```python
# Store two pieces of information, then use them together.
name = "Asha"
favorite_number = 7
print("This program belongs to", name)
print("Their favorite number is", favorite_number)
```

**Plain-English explanation:**

- `name = "Asha"` and `favorite_number = 7` each create a **variable** — a
  name that refers to a value, so it can be reused later. You will study
  variables properly in the next lesson; here, they are used only to show
  several instructions running one after another, in the order they are
  written.
- `print("This program belongs to", name)` passes **two** pieces of
  information to `print`, separated by a comma. Python prints them in
  order, automatically placing a single space between them, producing:
  `This program belongs to Asha`.
- The final line works the same way, producing:
  `Their favorite number is 7`.
- Running this file shows both lines, top to bottom, in the exact order
  they appear in the source code — this is **sequence**, the default
  behavior you first saw in
  [Algorithms, Programs, and Data](../01-Computational-Thinking-and-Program-Design/01-algorithms-programs-and-data.md).

### Example 3 — A basic `if` block: indentation decides what belongs together

```python
# Decide what to print based on one piece of information.
age = 20

if age >= 18:
    print("You are old enough to vote.")
    print("Both of these lines are inside the if block.")

print("This line always runs, no matter what age is.")
```

**Plain-English explanation:**

- `age = 20` stores a number. `age >= 18` is a condition — read it as "is
  `age` 18 or more?" (You will study comparison operators like `>=` fully
  in the next lesson; for now, just read it in plain English.)
- Because `age` is `20`, the condition is `True`, so Python runs every line
  indented underneath `if age >= 18:`. Both indented `print` lines belong
  to that one code block, because they are indented by the same amount,
  directly under the `if` line.
- The last `print` line has **no** indentation, so it is not part of the
  `if` block at all — it is a separate instruction that always runs,
  whether `age` is `20`, `10`, or anything else.
- Running this file with `age = 20` prints three lines: the two indented
  ones, then the always-running one. If you changed `age` to `10`, only the
  final, unindented line would print — the indented block would be skipped
  entirely, but the interpreter would not consider that an error, because
  the code is grammatically valid either way.

## Common beginner mistakes

- **Forgetting the colon (`:`) at the end of an `if` line.** Writing
  `if age >= 18` without the trailing colon produces a `SyntaxError`,
  because Python requires the colon to mark the start of a new block.
- **Inconsistent indentation inside one block.** A line that should be
  indented inside a block, but is not, causes an `IndentationError`. For
  example:

  ```python
  age = 20
  if age >= 18:
  print("You are an adult.")
  ```

  Running this produces something like
  `IndentationError: expected an indented block after 'if' statement on line 2`,
  because the `print` line needed to be indented under `if` but was not.
- **Mixing tabs and spaces in the same file.** Even if a line "looks"
  correctly indented, mixing tab characters and space characters for
  indentation can cause Python to see it differently than you do, leading
  to a confusing `TabError` (a specific kind of `IndentationError`). Let
  your editor insert spaces for you.
- **Confusing the REPL with a saved file.** Typing a real, useful program
  directly into the REPL and then closing the terminal loses it completely,
  because the REPL never saves anything to disk on its own.
- **Running the wrong filename, or running from the wrong folder.** Typing
  `python3 hello.py` while sitting in a different folder than the one
  containing `hello.py` produces a "No such file or directory" style error
  — this is a terminal/location problem, not a Python grammar problem.
- **Forgetting quotation marks around text.** Writing `print(Hello)`
  instead of `print("Hello")` treats `Hello` as a name, not as text. If no
  value is bound to the name `Hello`, Python raises a `NameError` rather
  than showing the text. If `Hello` has already been defined, the statement
  is valid: after `Hello = "world"`, `print(Hello)` prints `world`. The
  difference is `"Hello"` (a string literal) versus `Hello` (a name).

## Try it yourself

Do not look up full solutions. Predict what you expect to happen before you
run anything, then compare.

1. Run `python3 --version` (or `python --version`) yourself, and write down
   exactly what it prints.
2. Create a file called `about_me.py` containing variables for your name
   and age, and one `print(...)` line that displays both together using the
   comma technique from Example 2. Run it from the terminal.
3. Start the REPL, type three or four small expressions of your own (such
   as `5 * 6` or `"cat" + "fish"`), then exit it correctly using one of the
   methods from step 5.
4. In Example 3, remove the indentation from the first `print()` line
   immediately below the `if` statement. Run the file and write down the
   exact error message Python shows you. Then restore the indentation and
   run the program again.
5. In Example 3, change `age` to a number below `18`, predict the exact
   output before running, then run it to check whether you were right.

## Summary

- A **Python file** is plain text ending in `.py`; it is source code that
  does nothing on its own until it is run.
- The **interpreter** reads a Python file's text, parses it, and executes
  it; for a simple script, statements normally run in source order.
- The **REPL** runs Python interactively as you enter it and is meant
  for quick checks, not for programs you want to keep — use a `.py` file
  for that instead.
- A **comment**, starting with `#`, is ignored completely by the
  interpreter and exists only to help human readers.
- **Indentation** (consistent spaces) is how Python shows which lines
  belong together as one **code block**; getting it wrong causes a
  `SyntaxError` or, more specifically, an `IndentationError`.

## Completion checklist

- [ ] I can explain what a `.py` file is and what the interpreter does with
      it, in my own words.
- [ ] I have checked my Python version from a terminal.
- [ ] I have created and run at least one `.py` file myself.
- [ ] I have started the REPL, run a few expressions in it, and exited it
      correctly.
- [ ] I can explain, without notes, the difference between working in the
      REPL and running a `.py` file.
- [ ] I can explain why indentation matters in Python and deliberately
      break it once to see the resulting error message.
- [ ] I have completed the "try it yourself" exercises above.

## Connection to later Applied AI and Agentic AI engineering work

Every AI tool, script, or agent you build later still starts exactly this
way: as a `.py` file, read and run by the same interpreter you just used.
The habit of quickly checking an idea in the REPL before committing it to a
real file is one you will use constantly once you are experimenting with
prompts, tool definitions, or small pieces of agent logic. And indentation
mistakes are the same category of small, easy-to-miss error you will need
to catch quickly in much bigger, more consequential files later — the
discipline of reading an error message carefully, rather than guessing,
starts here.
