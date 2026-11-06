# Stage 1 — Topic 03: Input → Process → Output
## Study Guide, Learner-Level Analysis, and Completed Exercises

**Source lesson:** `03-input-process-output.md`  
**Curriculum reference:** Stage 1 — Programming & Computational Thinking project tree

---

## Part 1 — Lesson summary and step-by-step teaching (under 650 words)

### 1. The IPO model

Many programs follow **Input → Process → Output (IPO)**:

- **Input:** data made available to the program. It may be typed by a user, stored in a variable, or read from a file.
- **Process:** operations performed on the data, such as calculations, comparisons, and transformations.
- **Output:** the result produced. It may be displayed, returned to another part of a program, or written somewhere. Output is not limited to `print()`.

Example outside programming: making tea takes water and tea leaves (input), boils and steeps them (process), and produces tea (output).

Before coding, answer three questions: What information is needed and where does it come from? What must happen to it? What result should be shown or returned, and in what form? This prevents coding before the problem is understood.

### 2. Getting input in Python

Input may already be stored in a variable or be typed while the program runs. Python's `input()` displays a prompt, pauses until the user presses Enter, and returns the typed value **as a string (text)**:

```python
name = input("What is your name? ")
```

The IPO concept of *input* means any data the program receives. `input()` is one particular Python function for interactive text input.

### 3. Processing and producing output

The process uses expressions, statements, and variables to transform input. `print()` displays output:

```python
name = input("What is your name? ")
greeting = "Hello, " + name + "!"
print(greeting)
```

If the user types `Maria`, the input is stored in `name`; the process joins `"Hello, "`, the name, and `"!"`; the output is `Hello, Maria!`.

### 4. Convert numeric text before arithmetic

Because `input()` always returns text, convert numeric input with `int()` for whole numbers or `float()` for decimal numbers:

```python
age_text = input("How old are you? ")
age_number = int(age_text)
```

If the user enters `16`, `age_text` is `"16"` and `age_number` is the integer `16`.

A price-and-quantity example separates conversion from calculation:

```python
price_text = input("Enter the price of the item: ")
quantity_text = input("Enter how many you are buying: ")
price = float(price_text)
quantity = int(quantity_text)
total = price * quantity
print("Total cost:", total)
```

For price `19.99` and quantity `3`, the process converts both strings, multiplies the numbers, and displays `Total cost: 59.97`. `print()` separates its comma-separated arguments with a space.

### 5. A multi-step IPO example

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

Each `float(input(...))` reads and immediately converts an expense. The program totals the three values, divides by three for the average, and prints both. The `if` previews **selection**: the warning is printed only when `total > 100`. A larger program is still IPO; it simply has more inputs, processing steps, and possible outputs.

### 6. Common mistakes and key takeaways

- Forgetting conversion: `"3" * 2` produces `"33"` (repeated text), not numeric `6`.
- Invalid numeric text: `int("abc")` and `float("nineteen")` raise `ValueError`. `float()` accepts `"42"` and `"3.5"`, but not `"abc"` or `"nineteen"`. Real programs must handle invalid input; exception handling comes later in the curriculum.
- Writing a dense one-liner such as `print(int(input())*float(input())+1)` makes code harder to read and debug. Prefer named, separate steps.
- Confusing processing with output: calculating a value does not display it. Use `print()` (or, later, `return`) when the result must be made observable or passed on.

The lesson's outcomes are to explain IPO, identify its parts before coding, write small input/process/output Python programs, and split a larger problem into multiple IPO steps. Its prerequisites are **Algorithms, Programs, and Data** and **Values, Expressions, Statements, and Variables**. The same design habit applies to an AI agent: receive a message or tool result, process it using a model or logic, then reply or call a tool.

---

## Part 2 — Learner-level analysis based on the complete Stage 1 project tree

Your tree is a broad, deliberately progressive Python curriculum. It begins with computational thinking, variables and core data types, then moves through control flow, collections, files/CLI, packages, testing, OOP, production habits, advanced Python, performance, packaging, runtime internals, design patterns, visualization, security, and code review/refactoring. It also contains four applied projects: an expense-ledger CLI, a log-investigation/reliability CLI, a data-quality/transformation pipeline, and a rule-based risk-review engine.

**What this indicates:** the planned learning path aims well beyond beginner syntax. It includes the foundations and many advanced skills relevant to maintainable Python and data-engineering applications. Topic 03 is an early foundational lesson: it assumes the previous two topics, and it only previews selection rather than teaching it fully.

**What the tree cannot prove:** a list of modules and project files does not demonstrate that you can independently explain concepts, write working code, debug errors, or complete the projects. Your demonstrated level is therefore **not yet assessable from the tree alone**. For this lesson, treat yourself as a beginner until you can complete the exercises, explain each IPO stage, and predict program output. Do not interpret advanced modules later in the tree as skills already mastered.

**Current learning target:** reliably identify input, process, and output; understand string input and numeric conversion; write readable multi-step scripts; and explain the result. The exercises below test exactly those outcomes.

---

## Part 3 — Completed exercises with explanations (under 650 words)

### Exercise 1 — Approximate age from birth year

**IPO:** Input = birth year; Process = `2026 - birth_year`; Output = a sentence containing the age.

```python
birth_year = int(input("Enter your birth year: "))
age = 2026 - birth_year
print("Your approximate age is", age)
```

`input()` returns text, so `int()` converts it to a whole number. Subtract the birth year from 2026, then print the result. This is approximate because it does not check whether the birthday has occurred yet in 2026.

### Exercise 2 — Celsius to Fahrenheit

**IPO:** Input = Celsius temperature; Process = apply `F = C * 9 / 5 + 32`; Output = Fahrenheit temperature.

```python
# Input: collect Celsius as text and convert it to a number.
celsius = float(input("Enter temperature in Celsius: "))

# Process: convert Celsius to Fahrenheit.
fahrenheit = celsius * 9 / 5 + 32

# Output: display the converted temperature.
print("Temperature in Fahrenheit:", fahrenheit)
```

`float()` allows decimal temperatures. The calculation follows the supplied formula exactly. The comments identify the three IPO stages.

### Exercise 3 — Average of three test scores and pass/fail

**IPO:** Input = three scores; Process = calculate their average and compare it with 40; Output = `Pass` for an average of 40 or above, otherwise `Fail`.

```python
score_1 = float(input("Enter first score: "))
score_2 = float(input("Enter second score: "))
score_3 = float(input("Enter third score: "))

average = (score_1 + score_2 + score_3) / 3

if average >= 40:
    print("Pass")
else:
    print("Fail")
```

All three inputs are converted to numbers. Add them and divide by three. The condition `average >= 40` includes exactly 40 in the passing result; `else` handles every lower average.

### Exercise 4 — Add a fourth expense to Example 3

**IPO:** Input = four expenses; Process = add all four and divide by four; Output = total, average, and a warning only if the total exceeds 100.

```python
expense_1 = float(input("Enter first expense: "))
expense_2 = float(input("Enter second expense: "))
expense_3 = float(input("Enter third expense: "))
expense_4 = float(input("Enter fourth expense: "))

total = expense_1 + expense_2 + expense_3 + expense_4
average = total / 4

print("Total spent:", total)
print("Average expense:", average)

if total > 100:
    print("Warning: total spending is high this period.")
```

The fourth expense must be included in both the sum and the count used for the average. For a prediction, suppose the inputs are `10`, `20`, `30`, and `40`: total = `100`, average = `25.0`; the warning does **not** appear because the condition is strictly greater than 100. Run the program with those values to compare the actual output with the prediction.

---

## Completion check

- [ ] I can identify input, process, and output before coding.
- [ ] I can explain why `input()` returns a string and when to use `int()` or `float()`.
- [ ] I have run each exercise and checked its output.
- [ ] I can explain why Exercise 3 uses `>= 40` and Exercise 4 uses `> 100`.
- [ ] I can predict output before running a program.

**Progress status:** Exercises are provided as worked solutions. Mark them complete only after you type, run, and explain them yourself.
