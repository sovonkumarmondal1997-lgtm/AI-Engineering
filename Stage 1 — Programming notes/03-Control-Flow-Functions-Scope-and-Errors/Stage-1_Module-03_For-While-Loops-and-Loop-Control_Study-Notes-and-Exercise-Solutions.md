# Stage 1 — `for`/`while` Loops and Loop Control
## Study Notes, Step-by-Step Explanations, and Exercise Solutions

**Source lesson:** `02-for-while-loops-and-loop-control.md`  
**Module:** Control Flow, Functions, Scope and Errors  
**Learning position:** Beginner progressing toward intermediate Python

---

# Part 1 — Lesson Summary and Teaching Notes

## 1. What is iteration, and why do we need it?

**Iteration** means repeating a block of code. Without loops, printing `"Hello"` three times requires three separate `print()` statements. A loop performs the same work with less code:

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

`_` is an ordinary variable name conventionally used when the loop does not need the value.

## 2. `for` loops and iterables

A **`for` loop** runs once for each item in an **iterable**—an object Python can visit one item at a time. The variable after `for` is the **loop variable**. The indented repeated statements are the **loop body**.

```python
word = "cat"
for letter in word:
    print(letter)
```

Output: `c`, `a`, `t` on separate lines. The loop visits each character once.

Lists and tuples work the same way:

```python
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

coordinates = (10, 20, 30)
for value in coordinates:
    print(value)
```

A dictionary loop visits its **keys** by default:

```python
prices = {"apple": 0.50, "bread": 2.75, "milk": 1.90}
for product in prices:
    print(product)
```

To receive both key and value, use `.items()` and unpack the pair:

```python
for product, price in prices.items():
    print(product, "costs", price)
```

A set is also iterable, but its order is not guaranteed. Use `sorted()` when you need predictable display order:

```python
unique_colors = {"red", "green", "blue"}
for color in sorted(unique_colors):
    print(color)
```

## 3. `range()`

`range()` produces integers, often to repeat a task a fixed number of times.

```python
for number in range(5):
    print(number)
```

Output: `0, 1, 2, 3, 4`. The stop value (`5`) is **excluded**.

You can provide `start`, `stop`, and `step`:

```python
for number in range(2, 10, 2):
    print(number)       # 2, 4, 6, 8

for number in range(5, 0, -1):
    print(number)       # 5, 4, 3, 2, 1
```

A negative step counts downward. The stop is still excluded. `range(5, 5)` is empty, and `range(5, 0)` is also empty because its default step is `+1`, which moves away from the stop.

## 4. `while` loops and choosing the loop

A **`while` loop** repeats while its condition is `True`. Python checks the condition before every pass, including the first.

```python
countdown = 3
while countdown > 0:
    print(countdown)
    countdown = countdown - 1
print("Liftoff!")
```

Output: `3`, `2`, `1`, then `Liftoff!`. Updating `countdown` eventually makes the condition false.

Choose:
- **`for`** when you have a collection or fixed `range()` to visit.
- **`while`** when the number of repeats depends on a condition that must be checked as the work proceeds.

Example: keep adding daily sales until the total reaches $300, or the list runs out:

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

Output: `Days needed to reach $300: 3`; `Total after those days: 355`. The second condition prevents accessing beyond the list.

## 5. Infinite loops

An **infinite loop** never stops by itself because its condition never becomes false. A common cause is forgetting to update the variable used by the condition:

```python
count = 0
while count < 5:
    print(count)
    # Missing update: count stays 0 forever.
```

If this happens in a terminal, press **Ctrl-C** to interrupt the running program. To prevent it, ensure each pass moves the state toward the stopping condition:

```python
count = 0
while count < 5:
    print(count)
    count = count + 1
```

This prints `0` through `4` and stops.

## 6. `break` and `continue`

- **`break`** exits the loop immediately.
- **`continue`** skips the rest of the current pass and moves to the next pass.

Search example using `break`:

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

It finds `alan_t` and stops before checking `marie_c`. `found` records whether a match occurred.

Skip negative temperatures using `continue`:

```python
temperatures = [18, -5, 22, -1, 30, 0]
total_valid = 0

for temperature in temperatures:
    if temperature < 0:
        continue
    total_valid = total_valid + temperature

print("Total of non-negative temperatures:", total_valid)
```

Output: `70` (`18 + 22 + 30 + 0`). Negative values skip the addition.

## 7. `enumerate()`

Use `enumerate()` when you need both an item's position and its value. It starts at zero by default:

```python
tasks = ["Write report", "Review code", "Email client"]
for position, task in enumerate(tasks):
    print(position, "-", task)
```

Output positions: `0`, `1`, `2`. For human-friendly numbering, use `enumerate(tasks, start=1)`; the positions become `1`, `2`, `3`. This is clearer than manually looping over `range(len(tasks))` when you need an index.

## 8. `zip()`

`zip()` pairs items at matching positions from two or more collections:

```python
names = ["Ada", "Grace", "Alan"]
scores = [92, 88, 79]

for name, score in zip(names, scores):
    print(name, "scored", score)
```

It pairs Ada with 92, Grace with 88, and Alan with 79. **Important:** ordinary `zip()` stops at the shortest input and silently ignores extra items in a longer collection. In Python 3.10+, `zip(names, scores, strict=True)` raises `ValueError` if lengths differ.

## 9. Four worked examples from the lesson

**A. Total purchases:** initialize `total = 0` and `count = 0`; loop over `[19.99, 5.50, 42.00, 8.25]`; add each `amount` to `total` and add one to `count`. Print the count and `f"Total spent: ${total:.2f}"`. Output: `Number of purchases: 4` and `Total spent: $75.74`.

**B. Search inventory:** loop through `["hammer", "screwdriver", "wrench", "pliers"]`; compare each `tool` with `"wrench"`. Set `found_tool = True`, print the match and `break`. Print “not in stock” only if the flag remains false. Output: `wrench is in stock.`

**C. Simulated PIN attempts:** a `while` loop continues while attempts remain and `accepted_pin is None`. It advances `attempt_index`, skips blank input with `continue`, counts nonblank attempts, rejects nondigits with `.isdigit()`, rejects lengths other than four with `len(...) != 4`, and otherwise accepts the PIN. For `["", "12", "1234", "12ab"]`, output reports `12` rejected, `1234` accepted, 2 counted attempts, and accepted PIN `1234`. The loop stops before `12ab`.

**D. Student results with `zip()`:** pair names `["Ada", "Grace", "Alan", "Marie"]` with scores `[92, 58, 74, 88]`; increment a position counter; use `if score >= 60` to assign `"PASS"`, otherwise `"FAIL"`; print the numbered result. Output: Ada PASS, Grace FAIL, Alan PASS, Marie PASS, with their scores.

## 10. Common mistakes and practical relevance

Remember: dictionary iteration gives keys (use `.items()` for key-value pairs); a `while` loop needs a reliable stopping path; `break` is not `continue`; `zip()` does not normally report unequal lengths; `range()` excludes its stop; and `enumerate()` yields a pair that should be unpacked.

These patterns later support AI/data engineering: `for` processes documents or batch records; `enumerate()` reports item progress; `zip()` aligns prompts and responses; `continue` skips invalid records; and a bounded `while` loop models an agent's repeated actions without running forever.

---

# Part 2 — Exercise Solutions with Line-by-Line Explanations

The solutions below use only concepts from this lesson and the preceding conditionals/Boolean-logic material. Each exercise includes a runnable example.

## Exercise 1 — Dictionary of exam scores

**Requirement:** Print each student who scored at least 70, with their score.

```python
exam_scores = {
    "Ada": 85,
    "Grace": 68,
    "Alan": 92,
    "Marie": 70
}

for student, score in exam_scores.items():
    if score >= 70:
        print(student, "scored", score)
```

**Line by line:**
1. `exam_scores` stores student names as keys and scores as values.
2. `.items()` supplies each key-value pair.
3. `student, score` unpacks that pair on each pass.
4. `if score >= 70` checks the pass threshold.
5. `print(...)` runs only for qualifying students.

Output:
```text
Ada scored 85
Alan scored 92
Marie scored 70
```

## Exercise 2 — Multiples of 5 from 5 through 50

**Requirement:** Use one `for` loop and `range()` with a step.

```python
for number in range(5, 51, 5):
    print(number)
```

**Line by line:**
1. `5` is the starting value.
2. `51` is the excluded stop. We use 51 because 50 must be included.
3. `5` is the step, so each value increases by five.
4. The loop prints each generated value.

Output: `5, 10, 15, 20, 25, 30, 35, 40, 45, 50` (one per line).

## Exercise 3 — Savings with a `while` loop

**Requirement:** Start at zero, add 25 each week until the balance is at least 200, and print the number of weeks.

```python
balance = 0
weeks = 0

while balance < 200:
    balance = balance + 25
    weeks = weeks + 1

print("Weeks needed:", weeks)
print("Final balance:", balance)
```

**Line by line:**
1. `balance = 0` sets the initial savings.
2. `weeks = 0` initializes the week counter.
3. `while balance < 200` repeats while the target has not been reached.
4. `balance = balance + 25` adds one week's savings.
5. `weeks = weeks + 1` counts that week.
6. When the balance reaches 200, the condition becomes false and the loop ends.
7–8. The final statements display the result.

Output:
```text
Weeks needed: 8
Final balance: 200
```

## Exercise 4 — Skip values above 100; stop after five valid values

**Requirement:** Visit a list of ten numbers. A valid number is `<= 100`; negative values are valid. Skip numbers above 100 with `continue`, and stop after printing five valid numbers with `break`.

```python
numbers = [25, 150, -5, 80, 120, 0, 95, 110, 40, 60]
valid_count = 0

for number in numbers:
    if number > 100:
        continue

    print(number)
    valid_count = valid_count + 1

    if valid_count == 5:
        break
```

**Line by line:**
1. `numbers` contains ten values, including values above 100 and negative values.
2. `valid_count` tracks how many valid values have been printed.
3. The `for` loop visits each number in order.
4. If a number is greater than 100, `continue` skips the remaining body for that number.
5. Otherwise, the number is printed.
6. The valid counter increases by one.
7. When five valid values have been printed, the condition becomes true.
8. `break` exits the loop completely.

Output:
```text
25
-5
80
0
95
```

`150` and `120` are skipped. The loop stops after printing the fifth valid value, so later values are not processed.

## Exercise 5 — Numbered product list with `zip()` and `enumerate()`

**Requirement:** Pair product names and prices, number the lines starting at 1, and explain unequal lengths in a comment.

```python
product_names = ["apple", "bread", "milk"]
product_prices = [0.50, 2.75, 1.90]

for position, (name, price) in enumerate(
    zip(product_names, product_prices), start=1
):
    print(f"{position}. {name} - ${price:.2f}")

# zip() stops when the shorter list runs out.
# Any extra item in the longer list is ignored.
```

**Line by line:**
1. `product_names` contains product names.
2. `product_prices` contains their corresponding prices in the same order.
3. `zip(...)` pairs each name with the price at the same position.
4. `enumerate(..., start=1)` adds a human-friendly number to each pair.
5. `position, (name, price)` unpacks the number and the paired values.
6. The f-string prints the number, name and price; `.2f` formats the price to two decimal places.
7–8. The comments explain the unequal-length behavior: ordinary `zip()` stops at the shortest input and ignores leftover items.

Output:
```text
1. apple - $0.50
2. bread - $2.75
3. milk - $1.90
```

If `product_names` had four items but `product_prices` had three, only three numbered lines would be printed. The fourth name would have no matching price and would be ignored by `zip()`.

---

## Final understanding checklist

Before moving forward, make sure you can:

- Loop over strings, lists, tuples, dictionaries and sets.
- Explain why dictionary loops visit keys, and when to use `.items()`.
- Use `range(start, stop, step)` and remember that `stop` is excluded.
- Write a `while` loop whose condition can become false.
- Explain, interrupt and prevent accidental infinite loops.
- Distinguish `break` (exit the loop) from `continue` (skip one pass).
- Use `enumerate()` for position plus value.
- Use `zip()` to pair collections and explain what happens when lengths differ.

**Learning boundary:** This lesson establishes iteration and loop control. The solutions intentionally do not introduce functions, comprehensions, exception handling, file processing, or other later-stage topics.
