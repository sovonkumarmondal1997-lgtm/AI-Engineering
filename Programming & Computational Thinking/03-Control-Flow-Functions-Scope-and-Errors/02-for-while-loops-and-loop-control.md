# `for`/`while` Loops and Loop Control

## Why this topic matters

Real work is repetitive: adding up every price in a cart, checking every
row of a spreadsheet, trying a password field until the user gets it
right. Writing one line of code per item is unworkable the moment a
collection has more than a handful of items, and impossible when you do
not even know in advance how many times something needs to happen. This
lesson covers **iteration**: Python's tools for repeating a block of code,
either once per item in a collection, or for as long as some condition
stays true, plus the finer controls — `break`, `continue`, `enumerate()`,
and `zip()` — that let you shape exactly how a loop repeats.

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain what iteration is and why it matters for repeated work.
- Write a `for` loop over a string, a list, a tuple, a dictionary, and a
  set, and explain that looping over a dictionary directly visits its
  keys.
- Use `range()` with a start, a stop, and a step, and explain why the
  stop value is always excluded.
- Write a `while` loop with a condition that is correctly updated inside
  the loop, and explain when a `while` loop suits a problem better than a
  `for` loop.
- Explain why infinite loops happen, how to stop one safely if it happens
  to you by accident, and how to prevent one in your own code.
- Use `break` to stop a loop as soon as a goal is reached.
- Use `continue` to skip just one pass of a loop and carry on with the
  next.
- Use `enumerate()` to get both a position and a value while looping.
- Use `zip()` to loop through two related collections together, and
  explain what happens when they are different lengths.
- Choose sensibly between `for`, `while`, `break`, and `continue` for a
  given problem.

## Prerequisites

- [Conditionals, Guards, and Boolean Logic](01-conditionals-guards-and-boolean-logic.md) —
  `break` and `continue` are both written inside an `if` statement, and
  this lesson assumes `if`/`elif`/`else` is already comfortable.
- [Sequence, Selection, Iteration, and Abstraction](../01-Computational-Thinking-and-Program-Design/04-sequence-selection-iteration-and-abstraction.md) —
  your first, informal look at `for` and `while` loops; this lesson gives
  both a complete, formal treatment.
- [Lists: Mutation, Copying, and Aliasing](../02-Python-Core-Language-and-Data-Types/05-lists-mutation-copying-and-aliasing.md),
  [Tuples and Unpacking](../02-Python-Core-Language-and-Data-Types/06-tuples-and-unpacking.md),
  [Dictionaries and Lookups](../02-Python-Core-Language-and-Data-Types/07-dictionaries-and-lookups.md), and
  [Sets and Unique Values](../02-Python-Core-Language-and-Data-Types/08-sets-and-unique-values.md) —
  this lesson loops over every one of these collection types.

## Key terms

| Term | Plain-English definition |
|---|---|
| **Iteration** | Repeating a block of statements, either once per item in a collection or until a condition becomes false. |
| **`for` loop** | A loop that runs its block once for each item in an iterable, in order. |
| **`while` loop** | A loop that keeps running its block for as long as a condition stays `True`. |
| **Loop variable** | The name a `for` loop assigns each item to, one at a time, as it repeats. |
| **Iterable** | Anything a `for` loop can step through one item at a time — a string, list, tuple, dictionary, or set are all examples. |
| **`range()`** | A built-in function that produces a sequence of integers, useful for counting a fixed number of times. |
| **Step** | How much a `range()` (or a slice) moves forward — or backward — between one value and the next. |
| **Loop body** | The indented block of statements that a loop repeats. |
| **Infinite loop** | A loop whose condition never becomes false, so it never stops on its own. |
| **`break`** | A statement that immediately exits the loop it is inside, skipping any remaining items or conditions. |
| **`continue`** | A statement that immediately skips the rest of the current pass through a loop and moves on to the next one. |
| **`enumerate()`** | A built-in function that pairs each item in a loop with its position, so both are available at once. |
| **`zip()`** | A built-in function that pairs up items from two (or more) collections at the same position, so they can be looped over together. |

## Step-by-step explanation

### 1. What iteration is, and why repeated work needs loops

Printing `"Hello"` three times could be written as three separate lines:

```python
print("Hello")
print("Hello")
print("Hello")
```

This works, but it does not scale: printing it 1,000 times would need
1,000 lines, and the number of repeats would be locked into the code
itself. **Iteration** solves this by repeating one block of code as many
times as needed, based on data rather than on how many lines you happened
to type:

```python
for _ in range(3):
    print("Hello")
```

```text
Hello
Hello
Hello
```

Both pieces of code print `"Hello"` three times, but the second one would
print it 1,000 times just as easily, by changing one number. `_` here is
just an ordinary variable name, conventionally used when a loop does not
actually need the value it produces — you will use `range()` properly in
Section 3.

### 2. `for` loops

A **`for` loop** repeats its block once for each item in an **iterable**
— anything Python can step through one item at a time — assigning each
item, in turn, to a **loop variable**. A collection such as a list or a
dictionary is one common kind of iterable, but a `for` loop works with
any iterable, including a string or a `range()`.

#### Looping through a string

```python
word = "cat"

for letter in word:
    print(letter)
```

```text
c
a
t
```

Each pass through the loop, `letter` takes the next character of `word`,
in order, until every character has been visited exactly once.

#### Looping through a list and a tuple

```python
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

coordinates = (10, 20, 30)
for value in coordinates:
    print(value)
```

```text
apple
banana
cherry
10
20
30
```

Looping over a list or a tuple works exactly the same way as looping over
a string: one pass per item, in order, exactly as you first saw
informally in Module 1.1.

#### Looping through a dictionary

As you learned in
[Dictionaries and Lookups](../02-Python-Core-Language-and-Data-Types/07-dictionaries-and-lookups.md),
looping over a dictionary directly visits its **keys**, not its values or
its key-value pairs:

```python
prices = {"apple": 0.50, "bread": 2.75, "milk": 1.90}

for product in prices:
    print(product)
```

```text
apple
bread
milk
```

When you need **both** the key and its value together, loop over
`.items()` instead, which unpacks each key-value pair directly in the
loop header:

```python
prices = {"apple": 0.50, "bread": 2.75, "milk": 1.90}

for product, price in prices.items():
    print(product, "costs", price)
```

```text
apple costs 0.5
bread costs 2.75
milk costs 1.9
```

#### Looping through a set

A set (from
[Sets and Unique Values](../02-Python-Core-Language-and-Data-Types/08-sets-and-unique-values.md))
can be looped over too, but remember sets are **unordered** — wrap it in
`sorted(...)` first whenever the display order matters:

```python
unique_colors = {"red", "green", "blue"}
for color in sorted(unique_colors):
    print(color)
```

```text
blue
green
red
```

### 3. `range()`

**`range()`** produces a sequence of integers, most often used to
repeat a block a fixed number of times, or to count through numbers
directly.

```python
for number in range(5):
    print(number)
```

```text
0
1
2
3
4
```

`range(5)` produces `0, 1, 2, 3, 4` — five numbers, starting at `0` and
stopping **before** `5`. This mirrors exactly how slicing's `stop` value
works (from
[Strings: Indexing, Slicing, and Formatting](../02-Python-Core-Language-and-Data-Types/04-strings-indexing-slicing-and-formatting.md)):
excluding the stop value makes the *count* of numbers produced easy to
predict — `range(5)` always produces exactly `5` numbers.

`range()` also accepts an explicit **start**, and a **step**, exactly
like a slice's `[start:stop:step]`:

```python
for number in range(2, 10, 2):
    print(number)
```

```text
2
4
6
8
```

`range(2, 10, 2)` starts at `2`, stops before `10`, and moves forward by
`2` each time. A **negative step** counts downward instead:

```python
for number in range(5, 0, -1):
    print(number)
```

```text
5
4
3
2
1
```

`range(5, 0, -1)` starts at `5` and moves backward by `1` each time,
stopping before it would reach `0` — notice `0` itself is never printed,
for the same "stop is excluded" reason as always.

A range can also be empty. When the start and stop are equal, there is
nothing to produce, so the loop body never runs:

```python
for number in range(5, 5):
    print(number)
```

This prints nothing. A range is empty in the same way when the step moves
away from the stop, such as `range(5, 0)` (the default step is `+1`).

### 4. `while` loops

A **`while` loop** repeats its block for as long as its condition stays
`True`, checking the condition again before every single pass, including
the very first one:

```python
countdown = 3

while countdown > 0:
    print(countdown)
    countdown = countdown - 1

print("Liftoff!")
```

```text
3
2
1
Liftoff!
```

A `while` loop that is meant to finish needs some way to stop: either its
condition eventually becomes `False`, or a `break` exits it. A very common
way to make the condition become `False` is to **update the state** the
condition depends on inside the loop body — here,
`countdown = countdown - 1`. Once `countdown` reaches `0`, the condition
`countdown > 0` becomes `False`, and the loop stops on its own, moving on
to `print("Liftoff!")`. Updating a variable is a common pattern, not a
requirement of every `while` loop.

**When `while` beats `for`:** a `for` loop is the right choice when you
already know exactly what you are iterating over — a specific list, a
specific `range()`. A `while` loop is the right choice when you do **not**
know in advance how many repeats you will need, only the condition that
should eventually stop it:

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

```text
Days needed to reach $300: 3
Total after those days: 355
```

Here, nobody can say in advance exactly how many days it will take to
reach `$300` in total sales — it depends entirely on the data itself.
`while total_so_far < 300 and ...` naturally expresses "keep going until
this becomes true," which a `for` loop over a fixed `range()` cannot
express nearly as directly. The extra `day_index < len(daily_sales)` check
means the loop stops when either the target is reached or there are no
more days available, so it can never run past the end of the list.

### 5. Infinite loops

An **infinite loop** is a `while` loop whose condition never becomes
`False`, so it never stops on its own. Infinite loops
can be written on purpose in some programs, but at this stage the concern
is the accidental kind, usually caused by forgetting to update the
variable the condition depends on:

```text
count = 0
while count < 5:
    print(count)
    # forgot to update count here -> this loop never ends, do not run it
```

If you were to run code shaped like this, `count` would stay `0` forever,
`count < 5` would always stay `True`, and the program would print `0`
forever without ever stopping by itself.

**If this ever happens to you by accident:** in a terminal, press
`Ctrl-C` (on any operating system this course targets) to interrupt the
running program safely and get your terminal back. This does not damage
anything — it simply stops the program where it currently is.

**How to prevent one:** always make sure something inside the loop body
genuinely moves the condition toward becoming `False`, on every single
pass, with no way to skip that update:

```python
count = 0

while count < 5:
    print(count)
    count = count + 1  # without this line, the loop would never stop
```

```text
0
1
2
3
4
```

This is the exact same loop shape as the broken version above, with one
crucial line restored: `count = count + 1` guarantees `count` gets closer
to `5` every single pass, so the loop is guaranteed to finish.

### 6. `break`: stopping a loop early

**`break`** immediately exits the loop it is inside — skipping any
remaining items in a `for` loop, or any further condition checks in a
`while` loop — as soon as some goal has been reached, without waiting for
the loop to finish on its own:

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

```text
Found alan_t in the list.
```

Once `username == target` is `True`, there is no reason to keep checking
the remaining usernames — `break` exits the `for` loop immediately,
before `"marie_c"` is ever even checked.

### 7. `continue`: skipping just one pass

**`continue`** skips the rest of the *current* pass through a loop and
moves straight on to the next one — unlike `break`, the loop itself keeps
running:

```python
temperatures = [18, -5, 22, -1, 30, 0]

total_valid = 0
for temperature in temperatures:
    if temperature < 0:
        continue
    total_valid = total_valid + temperature

print("Total of non-negative temperatures:", total_valid)
```

```text
Total of non-negative temperatures: 70
```

Whenever `temperature < 0` is `True`, `continue` immediately skips
`total_valid = total_valid + temperature` for that one pass and moves on
to the next temperature — the two negative readings (`-5` and `-1`) never
get added to the running total, while every other value does:
`18 + 22 + 30 + 0 = 70`.

### 8. `enumerate()`: getting both a position and a value

When you do not need the position, loop directly over the items:
`for item in items:` is generally clearer than
`for i in range(len(items)): print(items[i])`. A manual index is
appropriate only when the index itself is actually needed, and
`enumerate()` is the tidy way to get it.

**`enumerate()`** wraps an iterable so that a `for` loop receives both the
**position** and the **value** together, on every pass:

```python
tasks = ["Write report", "Review code", "Email client"]

for position, task in enumerate(tasks):
    print(position, "-", task)
```

```text
0 - Write report
1 - Review code
2 - Email client
```

`enumerate(tasks)` produces pairs of `(position, task)`, starting the
position count at `0` by default, which `for position, task in ...:`
unpacks directly, exactly like unpacking a tuple. Pass `start=1` when a
count starting from `1` reads more naturally, such as a numbered list
shown to a person:

```python
tasks = ["Write report", "Review code", "Email client"]

for position, task in enumerate(tasks, start=1):
    print(position, "-", task)
```

```text
1 - Write report
2 - Review code
3 - Email client
```

### 9. `zip()`: looping through two collections together

**`zip()`** pairs up items from two (or more) collections at the same
position, so a single `for` loop can visit both together:

```python
names = ["Ada", "Grace", "Alan"]
scores = [92, 88, 79]

for name, score in zip(names, scores):
    print(name, "scored", score)
```

```text
Ada scored 92
Grace scored 88
Alan scored 79
```

`zip(names, scores)` pairs `names[0]` with `scores[0]`, `names[1]` with
`scores[1]`, and so on, which `for name, score in ...:` unpacks directly.

**`zip()` stops at the shortest input:** if the two collections do
not have the same length, `zip()` simply stops once the *shorter* one
runs out, silently ignoring any leftover items in the longer one:

```python
names_extra = ["Ada", "Grace", "Alan", "Marie"]
scores = [92, 88, 79]

for name, score in zip(names_extra, scores):
    print(name, "scored", score)
```

```text
Ada scored 92
Grace scored 88
Alan scored 79
```

Even though `names_extra` has four names, `scores` only has three, so
`"Marie"` is never paired with anything and never appears in the output
at all — no error occurs, so it is worth double-checking that two
collections are genuinely meant to be the same length before relying on
`zip()`.

When equal lengths are required, modern Python (3.10 or newer) offers
`zip(names, scores, strict=True)`, which raises a `ValueError` if the
lengths differ instead of silently stopping at the shorter one.

### 10. Choosing between `for`, `while`, `break`, and `continue`

- Choose **`for`** when you already have a specific collection (or a
  `range()`) to step through, and you want to visit every item exactly
  once.
- Choose **`while`** when the number of repeats depends on a condition
  that can only be checked as you go, not on a fixed collection you
  already have in hand.
- Add **`break`** when a loop should stop as soon as some goal is
  reached, even if there is more left to check.
- Add **`continue`** when some items should be skipped entirely, but the
  loop itself should keep going for everything else.

These are not mutually exclusive — the search example in Section 6 is a
`for` loop *with* a `break`, and the temperature example in Section 7 is
a `for` loop *with* a `continue`; choosing the loop type and choosing
whether to add `break`/`continue` are two separate decisions.

## Examples

### Example 1 — Totaling a list of purchases

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

**Plain-English explanation:**

- `total` and `count` both start at `0`, using the running-total pattern
  from earlier lessons.
- The `for` loop visits each purchase amount once, adding it to `total`
  and increasing `count` by one every pass.
- After all four amounts have been visited, the two `print(...)` lines
  report the final count and total, with the total formatted as currency
  using the `.2f` specifier from
  [Strings: Indexing, Slicing, and Formatting](../02-Python-Core-Language-and-Data-Types/04-strings-indexing-slicing-and-formatting.md).

**Expected output:**

```text
Number of purchases: 4
Total spent: $75.74
```

### Example 2 — Searching an inventory list with `break`

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

**Plain-English explanation:**

- `found_tool` starts as `False`, a flag that will be flipped to `True`
  only if the requested tool is actually found.
- The loop checks each tool in order; the moment `tool == requested_tool`
  is `True`, it prints a confirmation and immediately `break`s, so
  `"pliers"` (which comes after `"wrench"` in the list) is never even
  checked.
- The final `if not found_tool:` only prints a "not in stock" message if
  the loop finished without ever finding a match — here, it does not run,
  since the tool *was* found.

**Expected output:**

```text
wrench is in stock.
```

### Example 3 — Validating simulated PIN attempts with a guard-style `while` loop

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

**Plain-English explanation:**

- `simulated_attempts` stands in for a sequence of attempts a real user
  might type, including one blank attempt and one attempt with letters
  in it.
- The `while` loop's condition combines two checks with `and`: keep going
  only while there are still attempts left *and* nothing has been
  accepted yet — exactly the "stop once a goal is reached" idea, expressed
  through the loop condition itself this time, instead of `break`.
- A blank attempt (`""`) is skipped entirely with `continue`, before it
  is even counted in `attempt_count` — a blank attempt should not count
  as a real, failed try.
- The remaining guard-style `if`/`elif`/`else` chain (from
  [Conditionals, Guards, and Boolean Logic](01-conditionals-guards-and-boolean-logic.md))
  rejects `"12"` for having only two digits, accepts `"1234"`, and the
  loop then stops on its own, since `accepted_pin is None` has become
  `False` — `"12ab"` is never even reached.

**Expected output:**

```text
12 -> rejected: PIN must be exactly 4 digits.
1234 -> accepted.
Attempts checked (blank ones skipped): 2
Accepted PIN: 1234
```

### Example 4 — Comparing paired student names and scores with `zip()`

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

**Plain-English explanation:**

- `student_names` and `student_scores` are two separate, but related,
  lists — each student's name and score share the same position in both
  lists.
- `zip(student_names, student_scores)` pairs each name with its matching
  score, so the loop can consider both together without ever indexing
  into either list by hand.
- `position` is tracked manually with a simple counter, increased by one
  every pass, giving each printed line a running number.
- The `if`/`else` inside the loop decides `"PASS"` or `"FAIL"` for each
  student, reusing the comparison and formatting skills from earlier
  lessons, all driven by data the `zip()` pairing already lined up
  correctly.

**Expected output:**

```text
1. Ada: 92 (PASS)
2. Grace: 58 (FAIL)
3. Alan: 74 (PASS)
4. Marie: 88 (PASS)
```

## Common beginner mistakes

- **Forgetting that looping over a dictionary directly visits only its
  keys.** Writing `for pair in prices:` and expecting `pair` to be a
  key-value pair is a common mix-up; use `.items()` when both are
  needed.
- **Writing a `while` loop and forgetting to update the variable its
  condition depends on**, producing an infinite loop that never stops on
  its own.
- **Using `break` when `continue` was intended, or the reverse.**
  `break` leaves the loop entirely; `continue` only skips to the next
  pass — mixing them up either stops too early or never skips anything.
- **Assuming `zip()` will raise an error for mismatched lengths.** It
  does not; it silently stops at the shorter collection, so leftover
  items in the longer one are quietly ignored without any warning.
- **Forgetting `range()`'s stop value is excluded**, and being off by one
  — `range(1, 5)` produces `1, 2, 3, 4`, not `1, 2, 3, 4, 5`.
- **Using `enumerate()` but forgetting to unpack both values**, writing
  `for item in enumerate(tasks):` and then trying to use `item` as if it
  were just the task, when it is actually a `(position, task)` pair.

## Try it yourself

Do not look up full solutions. Predict the output before running each
one.

1. Write a `for` loop that visits a dictionary of exam scores with
   `.items()` and prints every student who scored `70` or above, along
   with their score.
2. Using `range()` with a step, print every multiple of `5` from `5` to
   `50`, inclusive, in a single `for` loop.
3. Write a `while` loop that starts a savings balance at `0` and adds
   `25` per week until the balance reaches at least `200`, printing how
   many weeks it took.
4. Write a `for` loop over a list of ten numbers that uses `continue` to
   skip any number greater than `100`, and `break` to stop entirely once
   five valid numbers have been printed. Here a number is valid when
   `number <= 100` (negative numbers count as valid).
5. Given two lists, `product_names` and `product_prices`, of possibly
   different lengths, use `zip()` and `enumerate()` together to print a
   numbered list of `"1. apple - $0.50"`-style lines, and explain, in a
   comment, what would happen if one list had an extra item.

## Summary

- **Iteration** repeats a block of code either once per item in an
  iterable, using **`for`**, or until a condition becomes `False`, using
  **`while`**.
- `for` loops work the same way over strings, lists, tuples, dictionaries
  (visiting keys by default, or key-value pairs with `.items()`), and
  sets.
- `range(start, stop, step)` produces integers, always excluding the
  stop value, and can count upward or, with a negative step, downward.
- A `while` loop that is meant to finish needs its condition to
  eventually become `False` (commonly by updating state inside the body)
  or a `break`; otherwise it becomes an **infinite loop** — press `Ctrl-C` to safely stop one by hand if it
  ever happens accidentally.
- **`break`** exits a loop immediately; **`continue`** skips just the
  current pass and moves on to the next one.
- **`enumerate()`** provides both a position and a value together;
  **`zip()`** pairs up matching positions from two collections, stopping
  as soon as the shorter one runs out.

## Completion checklist

- [ ] I can write a `for` loop over a string, a list, a tuple, a
      dictionary, and a set, and explain why looping over a dictionary
      directly gives its keys.
- [ ] I can use `range()` with a start, a stop, and a step, in both
      directions, and explain why the stop value is excluded.
- [ ] I can write a `while` loop with a correctly updating condition, and
      explain when I would choose it over a `for` loop.
- [ ] I can explain why an infinite loop happens, how to stop one safely
      by hand, and how to prevent one in my own code.
- [ ] I can use `break` to stop a loop early and `continue` to skip one
      pass, and explain the difference between them.
- [ ] I can use `enumerate()` to get a position and a value together, and
      `zip()` to loop through two collections in parallel.
- [ ] I can explain what happens when `zip()` is given collections of
      different lengths.
- [ ] I have completed the "try it yourself" exercises above.

## Connection to later Applied AI and Agentic AI engineering work

An AI agent's decision loop — "check the current state, take one action,
repeat until the task is done or a limit is reached" — is a `while` loop
in exactly the shape you practiced in Section 4, usually with a `break`
once the goal is reached, or once a maximum number of steps is hit, so
the agent cannot run forever the way an accidental infinite loop would.
Processing a batch of documents, retrieved search results, or tool
outputs one at a time is exactly the `for`-loop pattern from this lesson,
often combined with `enumerate()` to report progress ("processing item 3
of 20") or `zip()` to line up two related lists, such as a batch of
prompts and their corresponding responses. The habit of skipping invalid
items with `continue` rather than letting them crash a whole batch job is
also one you will rely on constantly once real, messy data is involved.
