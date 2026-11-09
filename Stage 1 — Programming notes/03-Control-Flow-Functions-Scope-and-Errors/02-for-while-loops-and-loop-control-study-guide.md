# `for`/`while` Loops and Loop Control — Complete Study Guide and Exercise Solutions

**Source lesson:** `02-for-while-loops-and-loop-control.md`  
**Roadmap location:** Stage 1 — Programming & Computational Thinking → Module 03 — Control Flow, Functions, Scope, and Errors → Lesson 02  
**Purpose:** A beginner-friendly explanation of every lesson concept and example, followed by complete solutions to all five practice exercises.

---

# Part A — Complete lesson summary and teaching guide

## 1. What is iteration, and why do we need it?

A program normally executes statements in sequence: one statement after another. But many real tasks require the same operation to be repeated:

- Add every purchase amount in a shopping cart.
- Inspect every row in a data file.
- Check each product in an inventory.
- Process each document returned by a retrieval system.
- Retry an operation until it succeeds or reaches a limit.

Writing a separate line for every item does not scale. **Iteration** means repeating a block of code. Python provides two main loop types:

- `for`: repeat once for each item in an iterable.
- `while`: repeat as long as a condition remains true.

A loop's indented statements are called its **loop body**. A variable that receives each item during a `for` loop is the **loop variable**.

For example, these statements print `Hello` three times:

```python
print("Hello")
print("Hello")
print("Hello")
```

A loop expresses the same task more compactly:

```python
for _ in range(3):
    print("Hello")
```

Output:

```text
Hello
Hello
Hello
```

The underscore `_` is an ordinary variable name. By convention, it is used when the loop produces a value that the code does not need. Here, `range(3)` supplies three values, but the program only needs to repeat the print operation.

## 2. `for` loops and iterables

An **iterable** is an object that Python can visit one item at a time. Strings, lists, tuples, dictionaries, sets, and `range()` objects are common examples.

General structure:

```python
for item in iterable:
    # repeated statements
    print(item)
```

Python takes the next item from the iterable, assigns it to `item`, executes the indented body, and repeats until there are no items left.

### 2.1 Loop through a string

```python
word = "cat"

for letter in word:
    print(letter)
```

Output:

```text
c
a
t
```

The loop visits each character in the string in order. On the first pass, `letter` is `"c"`; then it is `"a"`; then `"t"`. The body runs once per character.

### 2.2 Loop through a list and a tuple

```python
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    print(fruit)

coordinates = (10, 20, 30)

for value in coordinates:
    print(value)
```

Output:

```text
apple
banana
cherry
10
20
30
```

Lists and tuples are both visited from their first item to their last item. The loop syntax is the same for both.

### 2.3 Loop through a dictionary

A dictionary stores key-value pairs. When you loop over a dictionary directly, Python gives you its **keys**, not its values and not complete key-value pairs.

```python
prices = {"apple": 0.50, "bread": 2.75, "milk": 1.90}

for product in prices:
    print(product)
```

Output:

```text
apple
bread
milk
```

If you need both a key and its corresponding value, use `.items()`:

```python
prices = {"apple": 0.50, "bread": 2.75, "milk": 1.90}

for product, price in prices.items():
    print(product, "costs", price)
```

Output:

```text
apple costs 0.5
bread costs 2.75
milk costs 1.9
```

`.items()` provides each key-value pair. Python unpacks the pair into the two loop variables, `product` and `price`.

### 2.4 Loop through a set

A set contains unique values, but it does not promise a predictable display order. If the order matters, sort the set first:

```python
unique_colors = {"red", "green", "blue"}

for color in sorted(unique_colors):
    print(color)
```

Output:

```text
blue
green
red
```

`sorted(unique_colors)` produces the values in sorted order, and the loop visits that result. Do not rely on the natural iteration order of a set when the output order matters.

## 3. `range()`: generating numbers for a loop

`range()` produces a sequence of integers. It is commonly used when you want a loop to run a known number of times or when you want to count through a numeric sequence.

### 3.1 One argument: `range(stop)`

```python
for number in range(5):
    print(number)
```

Output:

```text
0
1
2
3
4
```

`range(5)` starts at zero and stops **before** five. Therefore, it produces exactly five values: `0`, `1`, `2`, `3`, and `4`.

The stop value is excluded. This is deliberate: `range(5)` produces five numbers, which makes the number of repetitions easy to predict.

### 3.2 Two arguments: `range(start, stop)`

```python
for number in range(2, 6):
    print(number)
```

Output:

```text
2
3
4
5
```

The first argument is the starting value; the second is the excluded stopping value.

### 3.3 Three arguments: `range(start, stop, step)`

The third argument controls how much the value changes on each pass:

```python
for number in range(2, 10, 2):
    print(number)
```

Output:

```text
2
4
6
8
```

This starts at `2`, adds `2` each time, and stops before `10`.

A negative step counts downward:

```python
for number in range(5, 0, -1):
    print(number)
```

Output:

```text
5
4
3
2
1
```

The loop starts at five and subtracts one on each pass. It stops before zero, so zero is not printed.

### 3.4 Empty ranges

A range can contain no values. If the start and stop are equal, the loop body never runs:

```python
for number in range(5, 5):
    print(number)
```

There is no output.

A range is also empty when the step moves away from the stop value. For example, `range(5, 0)` uses the default positive step of one, so it cannot count down toward zero and produces no values.

**Remember:** `range(start, stop, step)` excludes `stop`. Check the direction of the step when counting backward.

## 4. `while` loops

A `while` loop repeats its body for as long as its condition is true. Python checks the condition before the first pass and again before every later pass.

```python
countdown = 3

while countdown > 0:
    print(countdown)
    countdown = countdown - 1

print("Liftoff!")
```

Output:

```text
3
2
1
Liftoff!
```

Step by step:

1. `countdown = 3` initializes the state.
2. Python checks `countdown > 0`. It is true, so the body runs.
3. The current value is printed.
4. `countdown = countdown - 1` decreases the value by one.
5. Python checks the condition again.
6. This repeats until `countdown` becomes zero.
7. `countdown > 0` is now false, so the loop ends and execution continues at `print("Liftoff!")`.

The variable that controls the condition is part of the loop's **state**. A common way to make a `while` loop finish is to update that state inside the body so the condition eventually becomes false.

### 4.1 When should you choose `while` instead of `for`?

Use `for` when you already have a collection or a known range to visit. Use `while` when you do not know in advance how many repetitions are required; you only know the condition that should stop the process.

Example: accumulate daily sales until the total reaches 300 dollars, or until no more days are available.

```python
daily_sales = [120, 95, 140, 80, 200, 60]

total_so_far = 0
day_index = 0

while total_so_far < 300 and day_index < len(daily_sales):
    total_so_far = total_so_far + daily_sales[day_index]
    day_index = day_index + 1

print("Days needed to reach $300:", day_index)
print("Total after those days:", total_so_far)
```

Output:

```text
Days needed to reach $300: 3
Total after those days: 355
```

Explanation:

- Initially, the total is zero and the index is zero.
- The condition requires both that the total is below 300 and that an item remains in the list.
- The first three sales are 120, 95, and 140. Their total is 355.
- The total is no longer below 300, so the loop stops after three days.
- The index check prevents an out-of-range list access if the target is never reached.

The number of days depends on the sales data, so `while` expresses the stopping rule naturally.

## 5. Infinite loops

An **infinite loop** is a loop that never stops by itself because its condition never becomes false.

A common beginner mistake is forgetting to update the variable used by a `while` condition:

```python
count = 0

while count < 5:
    print(count)
    # The missing update means count remains 0 forever.
```

Do not run this broken example. Since `count` remains zero, `count < 5` remains true forever and the program repeatedly prints zero.

If a program accidentally gets stuck in a loop, press **Ctrl-C** in the terminal to interrupt it.

A corrected version updates the counter:

```python
count = 0

while count < 5:
    print(count)
    count = count + 1
```

Output:

```text
0
1
2
3
4
```

The counter moves closer to the stopping condition on every pass. A loop intended to finish must have a reliable termination path: its condition eventually becomes false, or it exits through `break`.

## 6. `break`: exit a loop immediately

`break` stops the loop in which it appears. It is useful when the program has already reached its goal and there is no reason to inspect the remaining items.

```python
usernames = ["ada99", "grace_h", "alan_t", "marie_c"]
target = "alan_t"

found = False

for username in usernames:
    if username == target:
        found = True
        print("Found", target, "in the list.")
        break

if not found:
    print(target, "is not in the list.")
```

Output:

```text
Found alan_t in the list.
```

How it works:

1. `found` begins as `False`.
2. The loop checks usernames one by one.
3. When `username` equals `target`, `found` becomes `True`.
4. The message is printed.
5. `break` exits the loop immediately. `"marie_c"` is not checked.
6. The final `if not found` does not print the failure message because `found` is true.

The `found` variable is a **flag**: a Boolean value that records whether the search succeeded.

## 7. `continue`: skip only the current pass

`continue` skips the rest of the current loop pass and moves to the next item. It does **not** terminate the entire loop.

```python
temperatures = [18, -5, 22, -1, 30, 0]

total_valid = 0

for temperature in temperatures:
    if temperature < 0:
        continue
    total_valid = total_valid + temperature

print("Total of non-negative temperatures:", total_valid)
```

Output:

```text
Total of non-negative temperatures: 70
```

Step by step:

- The total starts at zero.
- For `18`, the condition is false, so 18 is added.
- For `-5`, the condition is true, so `continue` skips the addition.
- For `22`, the value is added.
- For `-1`, the addition is skipped.
- `30` and `0` are added.
- The total is `18 + 22 + 30 + 0 = 70`.

**Difference:** `break` exits the loop completely; `continue` skips one pass and carries on.

## 8. `enumerate()`: get an item's position and value

When you only need each value, use the direct form:

```python
for item in items:
    print(item)
```

Do not use `range(len(items))` just to retrieve values. If you also need each item's position, `enumerate()` is the clearer tool.

```python
tasks = ["Write report", "Review code", "Email client"]

for position, task in enumerate(tasks):
    print(position, "-", task)
```

Output:

```text
0 - Write report
1 - Review code
2 - Email client
```

`enumerate(tasks)` supplies pairs containing a position and the corresponding value. By default, positions start at zero. The loop header unpacks each pair into `position` and `task`.

For a human-readable numbered list, use `start=1`:

```python
tasks = ["Write report", "Review code", "Email client"]

for position, task in enumerate(tasks, start=1):
    print(position, "-", task)
```

Output:

```text
1 - Write report
2 - Review code
3 - Email client
```

## 9. `zip()`: process related collections together

`zip()` pairs values from two or more iterables by their positions. This is useful when two lists store related information at matching positions.

```python
names = ["Ada", "Grace", "Alan"]
scores = [92, 88, 79]

for name, score in zip(names, scores):
    print(name, "scored", score)
```

Output:

```text
Ada scored 92
Grace scored 88
Alan scored 79
```

The first name is paired with the first score, the second name with the second score, and so on. The loop unpacks each pair into `name` and `score`.

### 9.1 What if the collections have different lengths?

By default, `zip()` stops when the **shortest** iterable runs out. Extra items in a longer iterable are ignored.

```python
names_extra = ["Ada", "Grace", "Alan", "Marie"]
scores = [92, 88, 79]

for name, score in zip(names_extra, scores):
    print(name, "scored", score)
```

Output:

```text
Ada scored 92
Grace scored 88
Alan scored 79
```

`"Marie"` is not printed because there is no fourth score. No error is raised by ordinary `zip()`, so check that the collections have the lengths you expect.

In Python 3.10 or newer, `zip(names, scores, strict=True)` raises a `ValueError` if their lengths differ. This is useful when equal lengths are a requirement.

## 10. Choosing the right loop control

These choices answer different questions:

| Tool | Choose it when… |
|---|---|
| `for` | You have an iterable or a known range and want to visit its items. |
| `while` | Repetition depends on a condition, and the number of passes is not known in advance. |
| `break` | You have reached a goal and want to exit the loop immediately. |
| `continue` | The current item should be skipped, but processing should continue with later items. |

They can be combined. A search can use a `for` loop with `break`; a data-cleaning loop can use `for` with `continue`; a retry process can use `while` and `break`.

## 11. All four complete lesson examples

### Example 1 — Total the purchase amounts

```python
purchase_amounts = [19.99, 5.50, 42.00, 8.25]

total = 0
count = 0

for amount in purchase_amounts:
    total = total + amount
    count = count + 1

print("Number of purchases:", count)
print(f"Total spent: ${total:.2f}")
```

Output:

```text
Number of purchases: 4
Total spent: $75.74
```

Explanation:

1. `purchases` contains four amounts.
2. `total` and `count` both start at zero.
3. The `for` loop visits each purchase once.
4. `total = total + amount` adds the current amount to the running total.
5. `count = count + 1` records that another purchase was processed.
6. After the loop, `count` is four and `total` is 75.74.
7. `:.2f` formats the total with exactly two digits after the decimal point, which is useful for displaying currency.

### Example 2 — Search inventory and stop with `break`

```python
inventory = ["hammer", "screwdriver", "wrench", "pliers"]
requested_tool = "wrench"

found_tool = False

for tool in inventory:
    if tool == requested_tool:
        found_tool = True
        print(f"{requested_tool} is in stock.")
        break

if not found_tool:
    print(f"{requested_tool} is not in stock.")
```

Output:

```text
wrench is in stock.
```

Explanation:

- `found_tool` starts false and acts as a flag.
- The loop compares each inventory item with the requested tool.
- When `"wrench"` matches, the flag becomes true and the success message is printed.
- `break` prevents unnecessary checks of later items.
- The final `if` prints the not-in-stock message only if the loop never found the tool.

### Example 3 — Validate simulated PIN attempts with `while` and `continue`

```python
simulated_attempts = ["", "12", "1234", "12ab"]

attempt_index = 0
accepted_pin = None
attempt_count = 0

while attempt_index < len(simulated_attempts) and accepted_pin is None:
    pin_attempt = simulated_attempts[attempt_index]
    attempt_index = attempt_index + 1

    if pin_attempt == "":
        continue

    attempt_count = attempt_count + 1

    if not pin_attempt.isdigit():
        print(pin_attempt, "-> rejected: PIN must contain only digits.")
    elif len(pin_attempt) != 4:
        print(pin_attempt, "-> rejected: PIN must be exactly 4 digits.")
    else:
        accepted_pin = pin_attempt
        print(pin_attempt, "-> accepted.")

print("Attempts checked (blank ones skipped):", attempt_count)
print("Accepted PIN:", accepted_pin)
```

Output:

```text
12 -> rejected: PIN must be exactly 4 digits.
1234 -> accepted.
Attempts checked (blank ones skipped): 2
Accepted PIN: 1234
```

Explanation:

1. `simulated_attempts` represents four attempts, including a blank one.
2. `attempt_index` tracks which attempt should be read next.
3. `accepted_pin` begins as `None`, meaning no valid PIN has been accepted yet.
4. `attempt_count` counts non-blank attempts.
5. The `while` condition requires both that attempts remain and that no PIN has been accepted.
6. The current attempt is read using its index, then the index is increased so the next pass moves forward.
7. A blank attempt triggers `continue`. It is skipped before increasing `attempt_count`.
8. A non-blank attempt increments the attempt counter.
9. `isdigit()` checks whether every character is a digit.
10. The `elif` checks that the PIN contains exactly four characters.
11. If both checks pass, the PIN is stored in `accepted_pin`.
12. On the next condition check, `accepted_pin is None` is false, so the loop ends. `"12ab"` is never processed.

This is an instructional example of loop control and validation, not a complete secure PIN authentication system.

### Example 4 — Pair student names and scores with `zip()`

```python
student_names = ["Ada", "Grace", "Alan", "Marie"]
student_scores = [92, 58, 74, 88]
passing_score = 60

position = 0

for name, score in zip(student_names, student_scores):
    position = position + 1

    if score >= passing_score:
        result = "PASS"
    else:
        result = "FAIL"

    print(f"{position}. {name}: {score} ({result})")
```

Output:

```text
1. Ada: 92 (PASS)
2. Grace: 58 (FAIL)
3. Alan: 74 (PASS)
4. Marie: 88 (PASS)
```

Explanation:

- The two lists store related data: each student's score is at the same position as their name.
- `zip(student_names, student_scores)` pairs the matching name and score.
- `position` starts at zero and increases once per pair, creating a one-based display number.
- The `if`/`else` decides whether the score meets the passing threshold.
- The formatted print statement displays the position, name, score, and result.

## 12. Common beginner mistakes

1. **Expecting a dictionary loop to produce key-value pairs.** A direct dictionary loop produces keys. Use `.items()` for both key and value.
2. **Forgetting to update a `while` loop's state.** If its condition remains true, the loop may never end.
3. **Confusing `break` and `continue`.** `break` exits the loop; `continue` skips only the current pass.
4. **Assuming `zip()` reports unequal lengths.** Ordinary `zip()` silently stops at the shorter input.
5. **Forgetting that `range()` excludes its stop.** `range(1, 5)` gives 1, 2, 3, and 4—not 5.
6. **Forgetting to unpack `enumerate()`.** Each item from `enumerate(tasks)` is a position-value pair. Use `for position, task in enumerate(tasks):` when you need both.

## 13. Connection to Applied AI and Agentic AI

The same loop patterns appear in production AI systems:

- A batch pipeline uses `for` to process each document, row, or model response.
- `enumerate()` can report progress, such as “processing item 3 of 20.”
- `zip()` can pair prompts with their corresponding responses.
- `continue` can skip an invalid record without stopping the whole batch.
- An agent can use a `while` loop to observe state, take an action, and repeat until it succeeds or reaches a maximum number of steps.
- `break` can stop an agent's loop once the goal is reached or a safety limit is met.

The production lesson is to define a clear stopping condition. An agent or data pipeline should never repeat indefinitely because a state variable was not updated or a termination condition was omitted.

## 14. Lesson completion checklist

You should now be able to:

- Explain iteration and distinguish `for` from `while`.
- Loop through strings, lists, tuples, dictionaries, and sets.
- Explain why a direct dictionary loop visits keys, and use `.items()` for key-value pairs.
- Use `range()` with start, stop, and step, including negative steps.
- Explain why the `range()` stop value is excluded and recognize empty ranges.
- Write a `while` loop whose condition can become false.
- Recognize, interrupt, and prevent accidental infinite loops.
- Use `break` to exit and `continue` to skip one pass.
- Use `enumerate()` to obtain a position and value.
- Use `zip()` to pair collections and explain what happens with unequal lengths.
- Select the appropriate loop and loop-control statement for a task.

---

# Part B — Project-tree analysis and current learning level

## 1. Exact location of this lesson

The roadmap places the attached lesson here:

```text
Stage 1 — Programming & Computational Thinking/
└── 03-Control-Flow-Functions-Scope-and-Errors/
    ├── 01-conditionals-guards-and-boolean-logic.md
    ├── 02-for-while-loops-and-loop-control.md
    ├── 03-functions-parameters-and-return-values.md
    ├── 04-function-arguments-defaults-and-docstrings.md
    ├── 05-scope-lifetime-and-global-state.md
    ├── 06-pure-functions-and-side-effects.md
    ├── 07-exceptions-validation-and-useful-errors.md
    ├── README.md
    └── practice-questions.md
```

This is Module 03, Lesson 02. It follows conditionals and Boolean logic because loop bodies frequently use `if`, `break`, and `continue`.

## 2. How the wider Stage 1 roadmap supports this lesson

The Stage 1 tree is organized as a progression:

- **Module 01 — Computational Thinking and Program Design:** algorithms, values and expressions, input-process-output, sequence/selection/iteration/abstraction, decomposition, preconditions and postconditions, dry runs, and state.
- **Module 02 — Python Core Language and Data Types:** Python syntax, variables and basic types, operators, strings, lists, tuples, dictionaries, sets, type conversion, truthiness, and mutability.
- **Module 03 — Control Flow, Functions, Scope, and Errors:** conditionals, loops, functions, arguments, scope, side effects, validation, and exceptions.
- **Module 04 — Problem-Solving, Collections, and Algorithmic Habits:** search, count, filter, map, aggregate, grouping, deduplication, sorting, Big-O, data-structure selection, comprehensions, recursion, and parsing.

The roadmap continues into file and command-line work, modules, testing, object-oriented programming, advanced Python, performance, packaging, internals, security, and code review. Those later topics are part of the broader plan; their presence in the tree does not itself prove they have all been completed.

Stage 1 also defines four larger projects:

1. Personal Expense Ledger CLI
2. Log Investigation and Reliability CLI
3. Data Quality and Transformation Pipeline
4. Rule-Based Risk Review Engine

Loops are foundational to all four because each project must process multiple transactions, log records, data rows, or risk cases.

## 3. Assessment of your current level

Your recorded work shows that you have already studied and practiced substantial Module 04 material: collection processing, grouping and sorting, Big-O, collection selection, comprehensions, recursion, parsing and regular expressions, plus a 35-question practice set. That work is beyond the prerequisites for this lesson.

Your current level is best described as **beginner progressing toward intermediate** in Python engineering. You are not approaching loops with no programming context: you have already used loops in examples and exercise solutions. This lesson formalizes the control-flow mechanics that support those later problem-solving tasks.

### Scope used in the exercise solutions

I keep the solutions within this lesson and its prerequisites:

- Variables and assignment
- Strings, lists, dictionaries, and basic collection access
- `if` / `elif` / `else` and Boolean conditions
- `for`, `while`, `range()`, `break`, and `continue`
- `enumerate()` and `zip()`
- Basic counters, running totals, comparisons, and formatted output

I do not introduce classes, recursion, file handling, pandas, external libraries, or advanced abstractions. The exercises are solved with ordinary loops so that the loop behavior remains visible.

---

# Part C — All five exercise solutions

## Exercise 1 — Print students scoring at least 70

**Task:** Loop through a dictionary of exam scores using `.items()` and print every student whose score is 70 or higher, including the score.

### Solution

```python
exam_scores = {
    "Ada": 92,
    "Grace": 68,
    "Alan": 75,
    "Marie": 70,
    "Linus": 55
}

for student, score in exam_scores.items():
    if score >= 70:
        print(student, "scored", score)
```

### Line-by-line explanation

1. `exam_scores = {...}` creates a dictionary. Each student's name is a key and the exam score is its value.
2. `for student, score in exam_scores.items():` visits every key-value pair. `.items()` provides the name and score together, and Python unpacks them into the two loop variables.
3. `if score >= 70:` checks whether the current student's score meets the threshold.
4. `print(student, "scored", score)` runs only for qualifying students.
5. When the loop has visited every pair, it ends automatically.

Expected output:

```text
Ada scored 92
Alan scored 75
Marie scored 70
```

The score of exactly 70 is included because the comparison uses `>=`, not `>`.

**Key concept:** Use `.items()` when a dictionary loop needs both keys and values.

## Exercise 2 — Print multiples of five from 5 through 50

**Task:** Use one `for` loop and `range()` with a step to print every multiple of five from 5 to 50, inclusive.

### Solution

```python
for number in range(5, 51, 5):
    print(number)
```

Expected output:

```text
5
10
15
20
25
30
35
40
45
50
```

### Line-by-line explanation

1. `range(5, 51, 5)` starts at 5.
2. The stop value is 51, which is excluded. This allows 50 to be included.
3. The step is 5, so Python adds five each time.
4. `for number in ...` assigns each generated number to `number`.
5. `print(number)` prints the current multiple.
6. When the next value would be 55, it is beyond the stop boundary, so the loop finishes.

**Common off-by-one mistake:** `range(5, 50, 5)` would stop before 50 and would not print it. Use 51 as the exclusive stop to include 50.

## Exercise 3 — Add 25 dollars per week until savings reach 200

**Task:** Start the balance at zero. Add 25 each week until the balance is at least 200, then print how many weeks were required.

### Solution

```python
balance = 0
weeks = 0

while balance < 200:
    balance = balance + 25
    weeks = weeks + 1

print("Weeks needed:", weeks)
print("Final savings balance: $", balance)
```

Expected output:

```text
Weeks needed: 8
Final savings balance: $ 200
```

### Line-by-line explanation

1. `balance = 0` sets the starting savings amount.
2. `weeks = 0` initializes a counter for completed weeks.
3. `while balance < 200:` repeats the body while the balance is below the target.
4. `balance = balance + 25` adds the weekly savings contribution.
5. `weeks = weeks + 1` records that one more week has passed.
6. Python checks `balance < 200` again. The loop continues until the balance reaches 200.
7. Once the balance is 200, the condition is false and the loop ends.
8. The two `print()` statements display the number of weeks and final balance.

Why the loop stops: both the balance and week counter are updated on each pass. The balance moves toward the target by 25 each time. Eight contributions are required because \(8 \times 25 = 200\).

**Key concept:** A `while` loop is appropriate because the repetition is controlled by a target condition. Updating `balance` inside the body guarantees progress toward that condition.

## Exercise 4 — Skip numbers above 100 and stop after five valid numbers

**Task:** Loop through a list of ten numbers. Use `continue` to skip numbers greater than 100. Use `break` to stop after five valid numbers have been printed. A number is valid when it is less than or equal to 100; negative numbers are valid.

### Solution

```python
numbers = [25, 150, -4, 80, 120, 0, 95, 101, 60, 40]

valid_count = 0

for number in numbers:
    if number > 100:
        continue

    print(number)
    valid_count = valid_count + 1

    if valid_count == 5:
        break
```

Expected output:

```text
25
-4
80
0
95
```

### Line-by-line explanation

1. `numbers = [...]` defines ten input numbers. Some are greater than 100, and some are valid, including negative values.
2. `valid_count = 0` initializes the number of valid values printed so far.
3. `for number in numbers:` visits each number in list order.
4. `if number > 100:` checks whether the current number is invalid.
5. `continue` skips the rest of this pass when the number is greater than 100. It does not increase the count and does not print that number.
6. `print(number)` runs for a valid value. Remember, valid means `number <= 100`, so negative values and zero are valid.
7. `valid_count = valid_count + 1` increases the count only after a valid number has been printed.
8. `if valid_count == 5:` checks whether five valid values have been printed.
9. `break` exits the loop as soon as the count reaches five. Later list items are not processed.

Trace of the valid values:

| Input item | Action | Valid count |
|---:|---|---:|
| 25 | Print | 1 |
| 150 | Skip with `continue` | 1 |
| -4 | Print | 2 |
| 80 | Print | 3 |
| 120 | Skip with `continue` | 3 |
| 0 | Print | 4 |
| 95 | Print, then stop with `break` | 5 |

**Important:** Put the count update after the `continue` check. Otherwise, skipped values could be counted incorrectly. Put `break` after printing and counting the fifth valid value.

## Exercise 5 — Number paired product names and prices with `zip()` and `enumerate()`

**Task:** Given `product_names` and `product_prices`, which may have different lengths, use `zip()` and `enumerate()` together to print numbered lines such as `"1. apple - $0.50"`. Include a code comment explaining what happens if one list has an extra item.

### Solution

```python
product_names = ["apple", "bread", "milk"]
product_prices = [0.50, 2.75, 1.90]

for position, (product, price) in enumerate(
    zip(product_names, product_prices),
    start=1
):
    print(f"{position}. {product} - ${price:.2f}")

# zip() stops when the shorter list runs out.
# Any extra item in the longer list is ignored.
```

Expected output:

```text
1. apple - $0.50
2. bread - $2.75
3. milk - $1.90
```

### Line-by-line explanation

1. `product_names = [...]` stores the product names.
2. `product_prices = [...]` stores the matching prices. Each price is intended to correspond to the name at the same position.
3. `zip(product_names, product_prices)` pairs each product name with the price at the same index.
4. `enumerate(..., start=1)` adds a position number to each pair. Starting at one is appropriate for a numbered list shown to a person.
5. `for position, (product, price) in ...:` unpacks the result. The outer pair contains the position and the zipped pair; the zipped pair is unpacked into `product` and `price`.
6. `print(f"{position}. {product} - ${price:.2f}")` displays the number, product name, and price. The `:.2f` format ensures two decimal places.
7. The comments explain the unequal-length behavior: ordinary `zip()` stops at the shorter input and ignores leftover items in the longer one.

### Test what happens when one list is longer

```python
product_names = ["apple", "bread", "milk", "rice"]
product_prices = [0.50, 2.75, 1.90]

for position, (product, price) in enumerate(
    zip(product_names, product_prices),
    start=1
):
    print(f"{position}. {product} - ${price:.2f}")
```

Output:

```text
1. apple - $0.50
2. bread - $2.75
3. milk - $1.90
```

`"rice"` is ignored because there is no fourth price. The program does not raise an error with ordinary `zip()`.

**Key concept:** `zip()` aligns related data by position; `enumerate()` adds a display number. If equal list lengths are mandatory, validate that requirement rather than silently accepting missing pairs. In Python 3.10 or newer, `zip(product_names, product_prices, strict=True)` can raise a `ValueError` on a length mismatch, but the basic exercise uses ordinary `zip()` to demonstrate its default behavior.

---

# Part D — Quick revision sheet

| Need | Python pattern |
|---|---|
| Visit every item | `for item in items:` |
| Visit dictionary keys and values | `for key, value in data.items():` |
| Repeat a fixed number of times | `for number in range(5):` |
| Count with a custom step | `range(start, stop, step)` |
| Repeat while a condition is true | `while condition:` |
| Stop the current loop | `break` |
| Skip the current pass | `continue` |
| Get position and value | `enumerate(items, start=1)` |
| Pair related collections | `zip(names, scores)` |

### The most important distinctions

- `for` is collection-driven; `while` is condition-driven.
- `range()` excludes its stop value.
- A `while` loop must have a reliable stopping path.
- `break` exits the loop; `continue` skips only the current pass.
- `enumerate()` supplies a position and an item.
- `zip()` pairs corresponding items and, by default, stops at the shortest input.

---

## Completion status

- Every major concept and key term in the source lesson is explained.
- All source code patterns and outputs are represented, including the four complete lesson examples.
- All five “Try it yourself” exercises are solved with line-by-line explanations.
- Solutions remain within the lesson's taught topics and prerequisite Python fundamentals.
