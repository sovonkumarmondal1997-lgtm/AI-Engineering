# Stage 1 — Topic 04: Sequence, Selection, and Iteration
## Simple Study Summary and Worked Exercises (No Functions)

**Learning constraint:** This guide follows your current learning stage. It does not use `def`, user-defined functions, function calls, parameters, or `return` in any code example. The source lesson introduces abstraction/functions, but their implementation is deliberately deferred because you have said you have not learned functions yet. Exercises that originally request functions are adapted to practise the same decision-making logic without them.

# Part 1 — Lesson summary (under 1,000 words)

## 1. The three coding patterns in this guide

- **Sequence:** Python runs statements from top to bottom, in the order written. This is the normal execution flow.
- **Selection:** The program chooses which statements to run based on a condition that is either `True` or `False`. Python uses `if`, `elif`, and `else`.
- **Iteration:** The program repeats statements. Use `for` to process items in a collection or a known range; use `while` to repeat while a condition remains true.

Programs commonly combine these patterns: statements run in sequence, decisions select a path, and loops repeat work.

## 2. Selection and conditions

A **condition** is an expression that evaluates to `True` or `False`. Comparison operators are:

| Operator | Meaning |
|---|---|
| `==` | equal to |
| `!=` | not equal to |
| `<`, `>` | less than, greater than |
| `<=`, `>=` | less than or equal, greater than or equal |

Remember: `=` assigns a value; `==` compares two values.

Example from the lesson, checking voting age:

```python
age = 20
if age >= 18:
    print("You can vote.")
```

Because 20 is at least 18, the condition is true and the message is printed.

Several paths can be checked with `if` / `elif` / `else`:

```python
temperature = 15
if temperature > 30:
    print("It's hot.")
elif temperature > 15:
    print("It's warm.")
else:
    print("It's cool.")
```

Python checks conditions from top to bottom and runs only the first matching block. At exactly 15, the result is “It's cool.” At exactly 30, the result is “It's warm.” Above 30, it is “It's hot.”; above 15 through 30, it is “It's warm.”; at or below 15, it is “It's cool.” `else` means “otherwise” and has no condition.

Boolean operators combine or reverse conditions:
- `and`: both conditions must be true.
- `or`: at least one condition must be true.
- `not`: reverses a Boolean value.

Lesson example:

```python
has_ticket = True
is_on_time = False
if has_ticket and is_on_time:
    print("Boarding allowed.")
else:
    print("Boarding denied.")
```

The combined condition is false because the passenger is not on time, so boarding is denied.

## 3. Iteration: `for` and `while`

A `for` loop processes each item in a collection:

```python
for number in [10, 20, 30]:
    print(number)
```

The indented statement runs three times. `number` is 10, then 20, then 30.

A `while` loop repeats as long as its condition is true:

```python
count = 0
while count < 3:
    print(count)
    count = count + 1
```

It prints 0, 1, and 2. Increasing `count` eventually makes `count < 3` false, so the loop stops. If the condition never becomes false, the loop can run forever. Always ensure a terminating `while` loop updates the relevant state.

## 4. Lesson examples rewritten without functions

**Password length selection:**

```python
password = "hunter2"
if len(password) >= 8:
    print("Password length is OK.")
else:
    print("Password is too short.")
```

`len(password)` is 7. Since 7 is not at least 8, the `else` message is printed.

**Counting positive, negative, and zero values:**

```python
numbers = [4, -2, 0, 7, -9, 0, 1]
positive_count = 0
negative_count = 0
zero_count = 0

for number in numbers:
    if number > 0:
        positive_count = positive_count + 1
    elif number < 0:
        negative_count = negative_count + 1
    else:
        zero_count = zero_count + 1

print("Positive:", positive_count)
print("Negative:", negative_count)
print("Zero:", zero_count)
```

The three counters start at zero. The loop visits all seven values. Selection inside the loop increments exactly one counter for each value. Final counts are positive 3, negative 2, and zero 2. This is **selection inside iteration**.

## 5. Abstraction — concept only, implementation deferred

The source lesson also introduces **abstraction**: giving a useful name to a group of steps so the logic can be reused without rewriting it. In Python, functions are the usual mechanism. The lesson defines these terms:
- **Function:** a named, reusable block of code.
- **Parameter:** a named placeholder for input a function receives.
- **Return value:** a result handed back to the code that used the function.
- `print` displays something; a return value makes a result available for later computation.

Functions can make code easier to read, test, and fix because reusable logic is kept in one place. This is important lesson theory, but no function syntax or function-based solution is used in this guide, in line with your instruction.

## 6. Common mistakes and final takeaways

- Using `=` instead of `==` in a condition.
- Forgetting the colon `:` or using incorrect indentation after `if`, `elif`, `else`, `for`, or `while`.
- Forgetting to update a `while` loop's condition variable, causing an infinite loop.
- Putting `elif` or `else` without its matching `if`, or separating them with unrelated code.
- Sequence is the default; selection chooses a path; iteration repeats work. These ideas can be combined in one program.

# Part 2 — Worked exercises (under 1,500 words)

The attached lesson has four “Try it yourself” exercises. Exercises 1 and 4 originally request functions. Below, they are adapted into ordinary statements and loops, without defining functions.

## Exercise 1 — Identify even and odd numbers

**Goal:** An integer is even when its remainder after division by 2 is zero. `%` calculates the remainder.

**Pseudocode:** Take each test number; check whether its remainder after division by 2 is zero; print even or odd.

```python
numbers = [4, 7, 10, 13]

for number in numbers:
    if number % 2 == 0:
        print(number, "is even")
    else:
        print(number, "is odd")
```

**Line by line:**
1. `numbers` stores four test integers, including even and odd values.
2. `for number in numbers:` visits each value once.
3. `number % 2` calculates the remainder after division by 2.
4. If the remainder is `0`, the number is even.
5. Otherwise, the `else` block identifies it as odd.
6. `print` displays the classification.

**Dry run:** 4 → remainder 0 → even; 7 → remainder 1 → odd; 10 → even; 13 → odd.

**Expected output:** 4 is even; 7 is odd; 10 is even; 13 is odd.

## Exercise 2 — Print multiples of 3 from 1 through 20

**Pseudocode:** Examine every integer from 1 to 20. Print it only when its remainder after division by 3 is zero.

```python
for number in range(1, 21):
    if number % 3 == 0:
        print(number)
```

**Line by line:**
1. `range(1, 21)` produces integers starting at 1 and ending at 20; 21 is excluded.
2. The `for` loop checks each integer.
3. `% 3` calculates its remainder after division by 3.
4. `== 0` checks whether it divides evenly by 3.
5. Only matching numbers are printed.

**Expected output:** `3, 6, 9, 12, 15, 18`.

## Exercise 3 — Double a counter until it exceeds 1,000

**Pseudocode:** Start at 1. While the counter is at most 1,000, double it and print the new value. Stop once it exceeds 1,000.

```python
counter = 1

while counter <= 1000:
    counter = counter * 2
    print(counter)
```

**Line by line:**
1. `counter = 1` sets the starting value.
2. `while counter <= 1000:` repeats while the current value is not greater than 1,000.
3. `counter = counter * 2` doubles the value.
4. `print(counter)` displays the value after each doubling.
5. When the value becomes 1,024, the condition `1024 <= 1000` is false and the loop stops.

**Dry run:** 1 → 2 → 4 → 8 → 16 → 32 → 64 → 128 → 256 → 512 → 1,024. The last printed value is 1,024.

## Exercise 4 — Display a traffic-light instruction

**Original learning goal:** Choose an instruction for red, yellow, or green, then repeat this decision for every color in a list. The source asks for a function; this version performs the same selection directly inside the loop.

```python
colors = ["green", "yellow", "red", "green"]

for color in colors:
    if color == "red":
        print(color, "-> Stop")
    elif color == "yellow":
        print(color, "-> Prepare to stop")
    elif color == "green":
        print(color, "-> Go")
    else:
        print(color, "-> Unknown color")
```

**Line by line:**
1. `colors` stores the four traffic-light colors from the exercise.
2. The `for` loop processes each color in order.
3. The first `if` checks for red and prints “Stop.”
4. `elif` checks for yellow and prints “Prepare to stop” if it matches.
5. The next `elif` checks for green and prints “Go.”
6. `else` handles an unexpected value, so the program still gives a clear response.
7. The loop repeats the same decision for all four list items.

**Expected output:** green → Go; yellow → Prepare to stop; red → Stop; green → Go.

---

# Current learning-level assessment

Your Stage 1 roadmap is a 24-module progression with four practical projects: Personal Expense Ledger CLI, Log Investigation and Reliability CLI, Data Quality and Transformation Pipeline, and Rule-Based Risk Review Engine. Its broader sequence moves from computational thinking and Python foundations into problem-solving, software engineering, production Python, and advanced engineering.

Your demonstrated progress is through the foundational problem-solving topics: IPO, sequence/selection/iteration, decomposition, preconditions and edge cases, pseudocode/flowcharts/dry runs, and state modelling. Your current demonstrated level is **beginner/foundational**, building confidence with conditions, loops, variables, and structured reasoning. Although the attached lesson introduces functions as abstraction, you have explicitly said you have not learned functions; therefore, this guide treats function implementation as **not yet in scope**. A roadmap listing a concept does not prove mastery.

**Practice checkpoint:** Recreate all four exercise programs from a blank file. Make sure you can explain every variable, condition, loop, and update. Do not move ahead until you can predict the output before running each program.
