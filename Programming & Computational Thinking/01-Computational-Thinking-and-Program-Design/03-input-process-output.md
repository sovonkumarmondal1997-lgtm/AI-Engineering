# Input → Process → Output

## Why this topic matters

Many programs you will write — a small script, a command-line
tool, a web backend, or a future AI agent — can be described using one
simple shape: it takes something **in**, does some work on it, and produces
something **out**. This is called the **Input → Process → Output** model,
or **IPO** for short. Learning to see every problem through this lens is
one of the fastest ways to stop staring blankly at a problem and start
writing code, because it gives you three concrete questions to answer
before you type a single line: what comes in, what should come out, and
what has to happen in between.

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain the Input → Process → Output model in your own words.
- Identify the input, process, and output for a plain-English problem
  before writing any code.
- Write small Python programs that read input, process it, and produce
  output.
- Break a slightly bigger problem into more than one IPO step.

## Prerequisites

- [Algorithms, Programs, and Data](01-algorithms-programs-and-data.md)
- [Values, Expressions, Statements, and Variables](02-values-expressions-statements-and-variables.md)

## Key terms

| Term | Plain-English definition |
|---|---|
| **Input** | Any data made available to a program for processing — typed by a user, already stored in a variable, or read from a file. |
| **Process** | The steps a program performs to turn input into output — calculations, comparisons, and transformations. |
| **Output** | Information produced by a program — such as text displayed on the screen, a value returned to another part of a program, or data written somewhere. Output is more than just `print()`. |
| **`input()`** | A built-in Python function that pauses the program, waits for the user to type something, and gives back what they typed as text. |
| **`print()`** | A built-in Python function that displays information on the screen. |
| **Type conversion** | Turning one type of value into another, such as turning the text `"5"` into the number `5`, because `input()` always gives back text. |

## Step-by-step explanation

### 1. The IPO model in one sentence

**Input → Process → Output** means: gather what you need, do the work, show
or return the result. Almost any task can be described this way. Making
tea: input is water and tea leaves; process is boiling and steeping;
output is a cup of tea. Calculating a total: input is a list of expenses;
process is adding them up; output is the total.

### 2. Why this model helps you *before* you code

The biggest trap for beginners is opening an editor and starting to type
code before they know what the program is supposed to receive and produce.
The IPO model forces you to answer three questions **first**, in plain
English:

1. **Input** — What information does this program need? Where does it
   come from (typed by a user? already stored in a variable? a fixed
   list?)?
2. **Process** — What has to happen to that information to get the answer?
3. **Output** — What exactly should the program show or return, and in
   what form?

Only after these three questions have clear answers should you start
writing Python.

### 3. Input in Python

Input can come from different places. The two you will use constantly in
this module are:

- **Data already given to you**, stored directly in a variable (as in
  topic 2's examples).
- **Data typed by a user while the program runs**, using the built-in
  `input()` function.

```python
name = input("What is your name? ")
```

`input(...)` does three things: it displays the text inside the
parentheses as a prompt, it pauses the program and waits for the person
using it to type something and press Enter, and then it gives back
whatever they typed — **always as text (a string)**, even if they typed
numbers. This last point causes a very common bug, covered in detail
below.

Keep the two ideas apart: *input* (the IPO idea) is any data made
available to the program for processing, while `input()` is just one
Python function that obtains text from interactive user input.

### 4. Process in Python

The "process" step is simply the code you already learned in topics 1 and
2: expressions, statements, and variables, combined to transform the input
into the answer you want. Later topics (selection, iteration, and
functions) will make the "process" step far more powerful, but the basic
shape stays the same.

### 5. Output in Python

Output, in this module, mostly means using `print(...)` to display a
result. Later stages introduce writing output to files or returning values
from functions to be used elsewhere, but the core idea — presenting the
result of the process step — does not change.

### 6. The type-conversion trap

`input()` **always** returns text, never a number, even if the user types
digits. If you need to do arithmetic with what someone typed, you must
**convert** the text into a number yourself, using `int(...)` for whole
numbers or `float(...)` for numbers with decimals:

```python
age_text = input("How old are you? ")   # this is text, e.g. "16"
age_number = int(age_text)              # now this is the number 16
```

Skipping this conversion is one of the most common beginner mistakes and is
covered in the mistakes section below.

## Examples

### Example 1 — A minimal IPO program

```python
name = input("What is your name? ")
greeting = "Hello, " + name + "!"
print(greeting)
```

**Plain-English explanation:**

- **Input:** `input("What is your name? ")` shows the prompt `What is your
  name? `, waits for the user to type something (say, `Maria`), and stores
  the typed text in the variable `name`.
- **Process:** `greeting = "Hello, " + name + "!"` builds a new piece of
  text by joining three pieces together: the fixed text `"Hello, "`, the
  value stored in `name`, and the fixed text `"!"`. If `name` is
  `"Maria"`, `greeting` becomes `"Hello, Maria!"`.
- **Output:** `print(greeting)` displays `Hello, Maria!` on the screen.
- Notice how each line maps directly onto one part of the IPO model — this
  is intentional, and it's the pattern you should look for in your own
  code.

### Example 2 — IPO with type conversion and a calculation

```python
price_text = input("Enter the price of the item: ")
quantity_text = input("Enter how many you are buying: ")

price = float(price_text)
quantity = int(quantity_text)

total = price * quantity

print("Total cost:", total)
```

**Plain-English explanation:**

- **Input:** Two separate `input()` calls collect two pieces of text from
  the user — the price and the quantity. Both are stored as text (strings)
  at this point, even though they look like numbers.
- **Process, step one (conversion):** `float(price_text)` converts the
  price text (say, `"19.99"`) into an actual number Python can do math
  with, `19.99`. `int(quantity_text)` converts the quantity text (say,
  `"3"`) into the whole number `3`. Without this step, trying to multiply
  the two pieces of text together would either produce an error or a
  strange result (multiplying text by text is not allowed in Python; only
  text multiplied by a whole number repeats the text, which is not what we
  want here).
- **Process, step two (calculation):** `total = price * quantity`
  multiplies the two numbers together. With `19.99` and `3`, `total`
  becomes `59.97`.
- **Output:** `print("Total cost:", total)` displays two things separated
  by a comma; `print` automatically puts a space between them, showing
  `Total cost: 59.97`.
- This example shows a common two-stage process: first clean up / convert
  the input into a usable form, *then* do the actual calculation. Keeping
  these as separate, clearly named steps (rather than mashing everything
  into one confusing line) makes code far easier to read and to fix later.

### Example 3 — A multi-step IPO program: expense summary

This example chains together more than one round of input, process, and
output, and starts hinting at the idea that a bigger problem is really a
sequence of smaller IPO steps (fully developed in
[topic 5](05-problem-decomposition.md)).

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

**Plain-English explanation:**

- **Input:** Three separate prompts each collect one expense. Notice that
  `float(input(...))` combines two steps from Example 2 into a single
  line: the conversion happens immediately on the text that `input()`
  returns, rather than storing an intermediate "text" variable first. Both
  styles are correct; this shorter style is common once you're comfortable
  with it.
- **Process, part one:** `total = expense_1 + expense_2 + expense_3` adds
  the three numbers together. `average = total / 3` divides the total by
  the fixed count of three expenses to get the average.
- **Output, part one:** the two `print(...)` lines show the computed total
  and average.
- **Process and output, part two:** the `if total > 100:` line is a first,
  small preview of **selection** (fully covered in
  [topic 4](04-sequence-selection-iteration-and-abstraction.md)). It means
  "only run the next indented line if the condition `total > 100` is
  true." If the total spent is more than 100, an extra warning line of
  output is produced; otherwise, that line is simply skipped.
- Notice that this whole program is still just Input → Process → Output —
  it just has *more than one* input, *more than one* processing step, and
  *more than one* possible output, depending on the data. Recognizing that
  a bigger program is a longer or more branching version of the same IPO
  pattern, rather than something fundamentally different, is the key
  takeaway of this topic.

## Common beginner mistakes

- **Forgetting that `input()` always returns text.** Trying to do math
  directly on the result of `input()` without converting it first
  (`int(...)` or `float(...)`) either causes a crash (`TypeError`) or,
  worse, produces a wrong but non-crashing result, such as `"3" * 2`
  producing `"33"` (text repeated) instead of the number `6`.
- **Converting text that isn't actually a valid number.** `int("abc")` or
  `float("nineteen")` will raise a `ValueError`, because Python cannot
  turn those into numbers. Real programs need to handle this
  possibility — you will learn how, properly, in Module 1.3 when you study
  exceptions; for now, just be aware that user input is not automatically
  "safe."
- **Doing too much in one line.** Combining many operations into a single
  dense line (`print(int(input())*float(input())+1)`) makes code hard to
  read and hard to debug. Prefer separate, clearly named steps like
  Examples 2 and 3.
- **Confusing "process" with "output."** A calculation that is never
  printed or returned has no visible effect. Beginners sometimes compute
  the right answer but forget the `print(...)` (or, later, `return`)
  statement that actually shows or uses it.

## Try it yourself

1. Write a program that asks the user for their birth year, calculates
   their approximate current age (assume the current year is `2026`), and
   prints a sentence containing that age.
2. Write a program that asks for a temperature in Celsius and prints the
   equivalent in Fahrenheit. (Formula: `F = C * 9 / 5 + 32`.) Identify, in
   a comment above your code, which lines are input, which are process,
   and which are output.
3. Write a program that reads three numbers of test scores from the user,
   computes the average, and prints `"Pass"` if the average is 40 or above
   and `"Fail"` otherwise (you can use the small `if` preview from
   Example 3, even without fully understanding selection yet).
4. Take Example 3 and add a fourth expense input, updating the rest of the
   program so the average is still calculated correctly. Predict the
   output first, then run it.

## Summary

- The **Input → Process → Output** model describes many programs:
  gather information, transform it, present the result.
- Answering "what is the input, what is the process, what is the output?"
  in plain English *before* coding makes writing the actual code far
  easier.
- `input()` reads text typed by a user; it always returns a string, so
  numeric input must be converted with `int(...)` or `float(...)` before
  doing arithmetic.
- `print(...)` is the simplest way to produce output in this module.
- Bigger programs are usually just longer chains of input, process, and
  output steps — not a fundamentally different kind of thing.

## Completion checklist

- [ ] I can state the input, process, and output of a plain-English
      problem before writing code.
- [ ] I can explain why `input()` returns text and why that sometimes needs
      to be converted.
- [ ] I have written and run a program using `input()`, a calculation, and
      `print()`.
- [ ] I have written a program with more than one input and more than one
      output step.
- [ ] I have completed the "try it yourself" exercises above.

## Connection to later Applied AI and Agentic AI engineering work

An AI agent, at its core, is also an Input → Process → Output system: it
receives an input (a user's message, or a tool's result), processes it
(decides what to do, perhaps by calling a model or running some logic),
and produces an output (a reply, or a call to another tool). The habit you
are building here — always asking "what exactly is coming in, what exactly
should come out, and what has to happen in between" — is precisely the
first design question you will ask about every future AI feature or agent
step, long before any AI model is involved.
