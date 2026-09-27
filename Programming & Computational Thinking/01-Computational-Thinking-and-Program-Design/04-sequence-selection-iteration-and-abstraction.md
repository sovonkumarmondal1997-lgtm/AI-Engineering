# Sequence, Selection, Iteration, and Abstraction

## Why this topic matters

Every program, no matter how complex, is built from only four control
ideas: doing things **in order** (sequence), doing something **only if** a
condition is true (selection), doing something **repeatedly** (iteration),
and wrapping a set of steps into a **reusable, named unit** (abstraction).
Once you can recognize these four patterns, you can read almost any
program ever written and understand its shape, even before you understand
every detail. This lesson introduces all four using small, everyday
examples, and deliberately avoids advanced syntax so you can focus on the
underlying ideas.

## Learning outcomes

By the end of this lesson, you will be able to:

- Identify sequence, selection, and iteration in a piece of code.
- Write conditions using comparison and Boolean logic.
- Write `for` and `while` loops to repeat work.
- Write a simple function to give a set of steps a name and make them
  reusable.
- Explain why abstraction (functions) makes programs easier to read, test,
  and fix.

## Prerequisites

- [Values, Expressions, Statements, and Variables](02-values-expressions-statements-and-variables.md)
- [Input → Process → Output](03-input-process-output.md)

## Key terms

| Term | Plain-English definition |
|---|---|
| **Sequence** | Running statements one after another, in the order they are written. |
| **Selection** | Choosing whether to run some statements, based on whether a condition is true or false, using `if` / `elif` / `else`. |
| **Condition** | An expression that evaluates to `True` or `False`, such as `age >= 18`. |
| **Iteration** | Repeating a set of statements, either a fixed number of times or until a condition changes, using `for` or `while`. |
| **Abstraction** | Hiding a group of steps behind a single name so it can be reused without repeating the steps, in Python this usually means a **function**. |
| **Function** | A named, reusable block of code that can take input (parameters) and can give back a result (a return value). |
| **Parameter** | A named placeholder for a value a function needs, listed when the function is defined. |
| **Return value** | The result a function hands back to whatever called it. |

## Step-by-step explanation

### 1. Sequence: the default behavior

You already saw this in [topic 1](01-algorithms-programs-and-data.md):
Python runs statements one after another, top to bottom. This is called
**sequence**, and it's the default — every program is a sequence unless you
tell Python otherwise using selection or iteration.

### 2. Selection: doing something only if a condition is true

**Selection** lets a program choose between different paths depending on
data. The building block is the `if` statement:

```python
age = 20
if age >= 18:
    print("You can vote.")
```

The line `age >= 18` is a **condition** — an expression that evaluates to
either `True` or `False`. `>=` means "greater than or equal to." Common
comparison operators are `==` (equal to — note: **two** equals signs,
because a single `=` means assignment, as you learned in topic 2), `!=`
(not equal to), `<`, `>`, `<=`, and `>=`.

You can chain more options with `elif` ("else if") and `else`:

```python
temperature = 15
if temperature > 30:
    print("It's hot.")
elif temperature > 15:
    print("It's warm.")
else:
    print("It's cool.")
```

Python checks each condition top to bottom and runs the *first* block whose
condition is true, then skips the rest. If none of the `if`/`elif`
conditions are true, the `else` block runs. `else` has no condition of its
own — it means "otherwise."

You can also combine conditions with Boolean logic: `and` (both must be
true), `or` (at least one must be true), and `not` (flips true to false and
vice versa):

```python
has_ticket = True
is_on_time = False
if has_ticket and is_on_time:
    print("Boarding allowed.")
else:
    print("Boarding denied.")
```

### 3. Iteration: doing something repeatedly

**Iteration** repeats a block of statements. Python has two main loop
types.

A **`for` loop** repeats once for each item in a collection (like a list),
or a fixed number of times using `range(...)`:

```python
for number in [10, 20, 30]:
    print(number)
```

This runs the indented block three times, with `number` taking the value
`10`, then `20`, then `30` in turn.

A **`while` loop** repeats as long as a condition stays true, and is used
when you don't know in advance how many times you'll need to repeat:

```python
count = 0
while count < 3:
    print(count)
    count = count + 1
```

Every `while` loop needs something inside it that can eventually make the
condition false (here, increasing `count`); otherwise it repeats forever,
which is a common beginner bug.

### 4. Abstraction: giving steps a name with functions

As programs grow, repeating the same steps in different places becomes
messy and error-prone. **Abstraction** means wrapping a set of steps into a
single named unit that can be reused. In Python, the main tool for this is
a **function**:

```python
def greet(name):
    print("Hello, " + name + "!")

greet("Ada")
greet("Grace")
```

`def greet(name):` **defines** a function called `greet` that expects one
piece of input, called a **parameter**, named `name`. Nothing runs yet at
definition time — Python just remembers the recipe. `greet("Ada")` **calls**
the function, meaning "run those steps now, using `"Ada"` wherever `name`
appears." The same function is called again with `"Grace"`, reusing the
exact same steps without retyping them.

A function can also **return** a value — hand a result back to whoever
called it — using `return`:

```python
def add(a, b):
    return a + b

result = add(3, 4)
print(result)
```

`return a + b` computes `a + b` and immediately sends that value back out
of the function; `result = add(3, 4)` captures that returned value in a
variable. `return` is different from `print`: `print` only *displays*
something; `return` *hands a value back* so the rest of the program can use
it in further calculations. This distinction matters a great deal once
programs get bigger, and is covered in more depth in Module 1.3.

## Examples

### Example 1 — Selection: checking a password rule

```python
password = "hunter2"

if len(password) >= 8:
    print("Password length is OK.")
else:
    print("Password is too short.")
```

**Plain-English explanation:**

- `password = "hunter2"` stores a piece of text.
- `len(password)` is an expression that gives the number of characters in
  `password` — here, `7`.
- `if len(password) >= 8:` checks whether that count is `8` or more. Since
  `7 >= 8` is `False`, the indented line under `if` is skipped.
- Because the condition was false, Python runs the `else` block instead,
  printing `Password is too short.`
- This is **selection** in its simplest useful form: one decision, two
  possible outcomes, based on a condition built from real data.

### Example 2 — Iteration: counting positive, negative, and zero numbers

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

**Plain-English explanation:**

- Three counters (`positive_count`, `negative_count`, `zero_count`) all
  start at `0`, following the same running-total pattern from
  [topic 2](02-values-expressions-statements-and-variables.md).
- `for number in numbers:` is **iteration**: the indented block runs once
  for every item in `numbers`, with `number` taking each value in turn:
  first `4`, then `-2`, then `0`, and so on.
- Inside the loop, **selection** decides which counter to increase.
  `if number > 0:` catches positive numbers, `elif number < 0:` catches
  negative numbers, and `else:` (meaning "neither of the above is true")
  catches exactly zero. This is selection nested inside iteration — a very
  common combination.
- After the loop finishes running for all seven numbers, the three
  `print(...)` lines show the final counts: `Positive: 3`,
  `Negative: 2`, `Zero: 2`.
- Notice this rewrites Example 2 from topic 1 (adding expenses one line at
  a time) using a loop instead of one line per item — this is exactly the
  "much shorter way" that topic 1 promised. The loop works correctly no
  matter how long the `numbers` list is, without adding more lines of
  code — a huge advantage over writing one line per item by hand.

### Example 3 — Abstraction: turning repeated logic into a function

This example takes the password check from Example 1 and the counting
logic from Example 2, and wraps each into a reusable function — showing
sequence, selection, iteration, *and* abstraction working together.

```python
def is_password_long_enough(password):
    return len(password) >= 8


def count_signs(numbers):
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
    return positive_count, negative_count, zero_count


passwords_to_check = ["hunter2", "correcthorsebatterystaple", "abc"]
for password in passwords_to_check:
    if is_password_long_enough(password):
        print(password, "-> OK")
    else:
        print(password, "-> too short")

positives, negatives, zeros = count_signs([4, -2, 0, 7, -9, 0, 1])
print("Positive:", positives, "Negative:", negatives, "Zero:", zeros)
```

**Plain-English explanation:**

- `def is_password_long_enough(password):` wraps the single condition from
  Example 1 into a function with a clear, descriptive name. It takes one
  parameter, `password`, and directly `return`s the result of the
  comparison (`True` or `False`) — there's no need for an `if`/`else` here
  because the comparison itself already produces a `True`/`False` value.
- `def count_signs(numbers):` wraps the entire loop-and-counters logic from
  Example 2 into a function. It takes one parameter, `numbers` (any list of
  numbers), and returns all three counts together, separated by commas —
  this is called returning a **tuple** of values, which you will study
  properly in Module 1.2. For now, just notice that a function can hand
  back more than one piece of information at once.
- `passwords_to_check = [...]` is a list of three example passwords. The
  `for password in passwords_to_check:` loop calls
  `is_password_long_enough(password)` once for each one, and **selection**
  decides which message to print based on the `True`/`False` result.
  Notice this reuses the same function on three completely different
  pieces of data, without repeating the length-check logic three times.
- `positives, negatives, zeros = count_signs([4, -2, 0, 7, -9, 0, 1])` calls
  the second function on a specific list, and immediately unpacks the three
  returned values into three separate variable names, in the same order
  they were returned.
- This example is the payoff of **abstraction**: once `is_password_long_enough`
  and `count_signs` exist, you can reuse them on any password or any list
  of numbers, anywhere in your program, without ever retyping the
  underlying logic. If you later discover a bug in the counting logic, you
  fix it in exactly one place — inside `count_signs` — instead of hunting
  down every copy of it.

## Common beginner mistakes

- **Using `=` instead of `==` inside a condition.** `if age = 18:` is a
  syntax error in Python (good — it stops you immediately), because `=` is
  assignment, not comparison. The correct condition is `if age == 18:`.
- **Forgetting the colon or the indentation** after `if`, `elif`, `else`,
  `for`, `while`, or `def`. Python uses indentation (consistent spaces) to
  know which lines belong inside a block; missing or inconsistent
  indentation causes errors or, worse, silently wrong behavior.
- **Writing a `while` loop whose condition never becomes false.** Forgetting
  to update the variable being checked (for example, forgetting
  `count = count + 1` inside the loop body) causes an infinite loop that
  never stops on its own.
- **Confusing `print` inside a function with `return`.** A function that
  only prints a value but never returns it cannot have that value used
  later by the rest of the program — `result = my_function()` would then
  store `None` (Python's "nothing" value), not the printed number.
- **Forgetting that `elif`/`else` are optional but depend on the `if`
  directly above them.** An `elif` or `else` cannot exist by itself, and
  cannot have unrelated code between it and its `if`.

## Try it yourself

1. Write a function `is_even(number)` that returns `True` if a number is
   even and `False` otherwise. (Hint: `number % 2` gives the remainder
   after dividing by 2.) Test it by calling it on at least four different
   numbers.
2. Using a `for` loop, write a program that prints every number from 1 to
   20 that is divisible by 3, without printing the others.
3. Write a `while` loop that starts a counter at `1` and keeps doubling it
   (`counter = counter * 2`) until it is greater than `1000`, printing the
   counter's value each time it changes.
4. Combine the ideas above into a function `traffic_light_message(color)`
   that takes a string (`"red"`, `"yellow"`, or `"green"`) and returns an
   appropriate instruction such as `"Stop"`, `"Prepare to stop"`, or
   `"Go"`. Call it in a loop over the list
   `["green", "yellow", "red", "green"]` and print each message.

## Summary

- **Sequence** is the default: statements run top to bottom.
- **Selection** (`if` / `elif` / `else`) lets a program choose a path based
  on a condition that evaluates to `True` or `False`.
- **Iteration** (`for` and `while`) repeats a block of statements, either
  once per item in a collection or until a condition becomes false.
- **Abstraction**, in Python mainly through **functions**, gives a named,
  reusable identity to a group of steps, taking input through parameters
  and optionally handing back a result with `return`.
- Real programs almost always combine all four ideas: sequence as the
  backbone, selection and iteration inside it, and functions wrapping
  reusable pieces of logic.

## Completion checklist

- [ ] I can write an `if` / `elif` / `else` statement using a real
      comparison and explain what each branch does.
- [ ] I can write a `for` loop over a list and a `while` loop with a
      correctly updating condition.
- [ ] I can explain, in my own words, the difference between `print` and
      `return` inside a function.
- [ ] I have written at least one function with a parameter and a
      `return` value, and called it more than once with different data.
- [ ] I have completed the "try it yourself" exercises above.

## Connection to later Applied AI and Agentic AI engineering work

An AI agent's core loop — "look at the current situation, decide what to
do next, do it, repeat until finished" — is built directly out of
selection (deciding which action or tool to use) and iteration (repeating
that decision-and-action cycle). Functions are exactly how you will later
define individual "tools" an agent can call, each with clear inputs and a
clear return value. Everything you practice here on passwords, traffic
lights, and number lists is the same shape of thinking you will use to
design an agent's decision loop and its tools — just with more moving
parts.
