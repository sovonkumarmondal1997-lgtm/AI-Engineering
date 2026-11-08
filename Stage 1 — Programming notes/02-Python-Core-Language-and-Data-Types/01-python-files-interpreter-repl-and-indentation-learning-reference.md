# Python Files, the Interpreter, the REPL, and Indentation

**Learning reference and solved exercises**

Source: `01-python-files-interpreter-repl-and-indentation.md`\
Curriculum context: Stage 1 --- Programming & Computational Thinking.

------------------------------------------------------------------------

## Part 1 --- Lesson summary and step-by-step teaching

### 1. Why this topic matters

Before writing larger programs, understand the tools that run Python and
the formatting rules Python uses. This prevents confusing environment or
indentation problems with mistakes in program logic.

By the end, you should be able to explain a `.py` file and interpreter,
check Python's version, create and run a script, use and exit the REPL,
write comments, indent code blocks, and recognize `SyntaxError` and
`IndentationError`.

### 2. Key terms

-   **Python file:** A plain-text file, normally named with the `.py`
    extension, containing Python source code. The extension is a
    convention; the contents must still follow Python grammar.
-   **Interpreter:** The installed `python` program that reads, parses,
    prepares, and executes Python source code.
-   **Terminal:** A text-based window where you enter commands for the
    operating system.
-   **REPL:** Read--Eval--Print Loop; an interactive Python session that
    reads an entry, evaluates it, displays a result when appropriate,
    and waits for the next entry.
-   **Comment:** Human-readable text beginning with `#`; Python ignores
    the comment.
-   **Indentation:** Leading whitespace that shows which statements
    belong to a code block.
-   **Code block (suite):** One or more statements grouped under a
    compound statement, such as `if`.
-   **SyntaxError:** Python reports that code does not follow its
    grammar.
-   **IndentationError:** A SyntaxError subtype specifically about
    invalid or inconsistent indentation. `TabError` is a more specific
    indentation error associated with inconsistent tab/space use.

### 3. What a Python file and interpreter do

A `.py` file is source code saved on disk. It is just text until an
interpreter runs it. The interpreter reads the text, checks it against
Python's grammar, prepares it for execution, and executes statements. In
a simple script, statements normally run in source order, unless control
flow, a function call, an exception, or another language feature changes
what runs next.

Check installation and version in a terminal:

``` text
python3 --version
```

Some systems use:

``` text
python --version
```

A result such as `Python 3.12.4` confirms that the command found an
interpreter and reports its version. "Command not found" usually means
Python is not installed or the terminal cannot find it; that is an
environment issue, not a Python logic error.

### 4. Create and run a `.py` file

1.  Create a file named `hello.py` in a folder you can locate from the
    terminal.
2.  Put this line in it:

``` python
print("Hello, Python!")
```

3.  Save the file.
4.  In the terminal, move to that folder and run:

``` text
python3 hello.py
```

Expected output:

``` text
Hello, Python!
```

Running the command again executes the file again. Each normal script
run starts a fresh Python process: variables and objects in the previous
process are not retained in memory. However, changes made to external
resources such as files or databases may persist.

### 5. The REPL and how it differs from a script

Start the interactive interpreter by entering `python3` without a
filename:

``` text
$ python3
>>> 2 + 2
4
>>> print("hi")
hi
>>>
```

`$` represents the terminal prompt; `>>>` is the Python REPL prompt. The
REPL immediately evaluates entries. A multi-line construct uses
continuation prompts (`...`):

``` python
>>> if True:
...     print("hello")
...
hello
```

Use the REPL for quick expression checks, testing a small idea, or
exploring syntax. Do not use it as the only home for a program you need
to keep, reuse, or share: REPL definitions and state are not
automatically saved as a `.py` file. When the Python process ends, its
in-memory state disappears, although terminal command history may
remain.

Exit with `exit()` and Enter, `Ctrl-D` on Linux/macOS, or `Ctrl-Z`
followed by Enter on Windows.

  -----------------------------------------------------------------------
  Saved `.py` file                    REPL
  ----------------------------------- -----------------------------------
  Source is saved on disk.            Entries are interactive and are not
                                      automatically saved as a source
                                      file.

  Run the script, normally from       Runs entries as you enter them.
  beginning to end.                   

  Suitable for programs you keep and  Suitable for quick, temporary
  reuse.                              experiments.
  -----------------------------------------------------------------------

### 6. Comments

A `#` starts a comment. Python ignores the comment; it is there for
people reading the program.

``` python
# This program greets the user.
print("Hello!")  # this line displays the greeting
```

Only the `print` instruction produces program output.

### 7. Indentation and code blocks

Python uses leading spaces rather than `{}` braces to show which
statements belong together. A compound-statement header such as `if`
ends with `:`. Statements indented consistently underneath it form its
block:

``` python
age = 20
if age >= 18:
    print("You are an adult.")
    print("You can vote.")
print("This runs no matter what age is.")
```

The first two `print` statements are inside the `if` block and run only
when `age >= 18` is true. The final statement is unindented, outside the
block, and runs regardless of age.

Use consistent indentation throughout a file. Four spaces per
indentation level is the standard Python style convention. Do not mix
tabs and spaces; inconsistent mixing can produce `TabError`. Configure
your editor (for example, VS Code) to insert spaces when you press Tab.

### 8. Errors and beginner mistakes

-   Forgetting the colon in `if age >= 18` causes `SyntaxError`: the
    `if` header is grammatically incomplete.
-   A block statement with no indented body, or inconsistent indentation
    within a block, causes `IndentationError`.
-   Mixing tabs and spaces inconsistently can cause `TabError`, a
    specific `IndentationError`.
-   A malformed file's syntax/indentation is checked before normal
    script execution begins, so these errors prevent the script from
    starting normally.
-   A runtime error such as `NameError` is different: it occurs when
    execution reaches a statement that refers to an undefined name.
    Earlier statements may already have run.
-   Running `python3 hello.py` from the wrong folder, or using the wrong
    filename, produces a file-not-found-style error. This is a terminal
    path/filename issue, not a grammar error.
-   `print(Hello)` treats `Hello` as a name, not text. If no value is
    assigned to that name, Python raises `NameError`. `print("Hello")`
    prints the string literal. If `Hello = "world"` was assigned first,
    `print(Hello)` prints `world`.

### 9. The lesson's three code examples

**Example 1 --- First file and comment**

``` python
# This is a comment: Python ignores this whole line.
print("Hello, Python!")
```

The comment has no effect. The `print` call displays the text. Running
`python3 hello.py` prints exactly `Hello, Python!`.

**Example 2 --- Variables and sequential instructions**

``` python
# Store two pieces of information, then use them together.
name = "Asha"
favorite_number = 7
print("This program belongs to", name)
print("Their favorite number is", favorite_number)
```

`name` refers to `"Asha"` and `favorite_number` refers to `7`. Each
`print` receives two arguments separated by a comma; `print` places a
space between them. Output:

``` text
This program belongs to Asha
Their favorite number is 7
```

The instructions run in the order written: this is sequence.

**Example 3 --- `if` block**

``` python
# Decide what to print based on one piece of information.
age = 20

if age >= 18:
    print("You are old enough to vote.")
    print("Both of these lines are inside the if block.")

print("This line always runs, no matter what age is.")
```

`age = 20` stores a number. `age >= 18` asks whether age is at least 18.
Since it is true, both indented statements run. The final unindented
statement is outside the block and always runs. If age becomes `10`, the
two indented statements are skipped and only the final line prints. That
is valid control flow, not an error.

### 10. Connection to later engineering work

AI tools, scripts, and agents are also Python source files run by the
interpreter. The REPL is useful for quickly checking a small expression
before placing working code in a saved file. Careful reading of
indentation and error messages remains important in larger systems.

------------------------------------------------------------------------

## Part 2 --- Learner-level assessment from the Stage 1 project tree

The supplied Stage 1 tree shows a broad progression: computational
thinking; Python core types; control flow and functions; collections and
algorithmic habits; files/CSV/JSON/CLI; packages and code quality;
testing/debugging; OOP; and advanced production-oriented Python topics.
It also contains practical projects such as a
data-quality/transformation pipeline and a rule-based risk-review
engine.

This lesson is the first topic in
`02-Python-Core-Language-and-Data-Types`. Its stated prerequisites are
Stage 0 terminal/Python familiarity and the earlier
computational-thinking lessons on algorithms/programs/data and
sequence/selection/iteration/abstraction.

**What the tree supports:** your planned curriculum includes the
prerequisite concepts and later engineering topics.\
**What the tree does not prove:** a project tree cannot establish that
you have completed the lessons, can independently write code, or have
mastered the concepts. No submitted exercise results or working code are
available here, so your demonstrated proficiency is not yet measurable.
The appropriate level for this lesson is therefore *beginner /
foundational, with mastery to be checked through the exercises below*.
The solutions stay within this lesson's concepts and the earlier
prerequisite vocabulary; they do not rely on later topics such as loops,
collections, or functions.

------------------------------------------------------------------------

## Part 3 --- All five exercises solved and explained

### Exercise 1 --- Check the installed Python version

Run one of these in your own terminal:

``` text
python3 --version
```

If that command is not recognized, try:

``` text
python --version
```

The output depends on the Python installation on your computer, so it
would be incorrect to invent your exact version. Record the complete
output, for example `Python 3.x.y`. A version string means the command
found an interpreter. A command-not-found message indicates an
installation or PATH/environment issue to resolve before proceeding.

### Exercise 2 --- Create `about_me.py`

Create and save a file named `about_me.py`:

``` python
# Store two details about the user.
name = "Your Name"
age = 20
print("My name is", name, "and my age is", age)
```

Line by line:

1.  `# ...` is a comment; Python ignores it.
2.  `name = "Your Name"` assigns a string value to the name `name`.
    Replace the placeholder with your name.
3.  `age = 20` assigns a number to `age`. Replace `20` with your age.
4.  `print(...)` displays its arguments in order, with spaces between
    them.

With the example values, output is:

``` text
My name is Your Name and my age is 20
```

Run it from the folder containing the file:

``` text
python3 about_me.py
```

### Exercise 3 --- Try expressions in the REPL

Start the REPL:

``` text
python3
```

Enter these examples one at a time:

``` text
>>> 5 * 6
30
>>> "cat" + "fish"
'catfish'
>>> 10 - 3
7
>>> print("Python practice")
Python practice
```

`5 * 6` evaluates multiplication and displays `30`. The `+` joins the
two strings into `'catfish'`. `10 - 3` evaluates to `7`. `print(...)`
displays the supplied text. The quotes around a string result in the
REPL representation are normal.

Exit using:

``` python
exit()
```

Alternatively, use `Ctrl-D` on Linux/macOS or `Ctrl-Z`, then Enter, on
Windows.

### Exercise 4 --- Deliberately break indentation, then repair it

**Incorrect version** --- the `print` line is not indented under `if`:

``` python
age = 20
if age >= 18:
print("You are an adult.")
```

Python reports an error similar to:

``` text
IndentationError: expected an indented block after 'if' statement on line 2
```

The exact wording and line number can vary by Python version. The
meaning is that the `if` header starts a block, but its body was not
indented.

**Corrected version:**

``` python
age = 20
if age >= 18:
    print("You are an adult.")
```

Line by line: `age = 20` stores the age; `if age >= 18:` checks the
condition and opens a block; the four leading spaces place `print`
inside that block. With age 20, the condition is true and the message
prints.

### Exercise 5 --- Change age to below 18

Use the complete example with `age = 10`:

``` python
age = 10

if age >= 18:
    print("You are old enough to vote.")
    print("Both of these lines are inside the if block.")

print("This line always runs, no matter what age is.")
```

**Prediction before running:** `10 >= 18` is false, so Python skips both
indented `print` statements. The final statement is outside the block,
so it still runs.

**Exact output:**

``` text
This line always runs, no matter what age is.
```

This is not an error. The code is valid; the condition simply evaluates
to false.

------------------------------------------------------------------------

## Completion check

-   [ ] I checked and recorded the Python version on my own machine.
-   [ ] I created and ran `about_me.py`.
-   [ ] I used the REPL for several expressions and exited it.
-   [ ] I caused an indentation error, read it, corrected the code, and
    ran it again.
-   [ ] I predicted the output for an age below 18 before running the
    program.
-   [ ] I can explain the difference between a syntax/indentation error
    and a runtime `NameError`.

**Scope note:** Exercise 1's actual version output and proof that the
commands ran must come from your computer. The remaining outputs above
are the expected results for the exact code shown.
