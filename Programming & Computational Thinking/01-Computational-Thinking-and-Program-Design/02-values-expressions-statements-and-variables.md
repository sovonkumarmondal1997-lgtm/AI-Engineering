# Values, Expressions, Statements, and Variables

## Why this topic matters

Python programs rely on four foundational concepts: **values**,
**expressions**, **statements**, and **variables**. If these four ideas
are solid, everything else — loops, functions, classes, even future AI
agent code — will make sense as combinations of them. If they are shaky, every later topic will
feel confusing for reasons you can't quite name. This lesson slows down and
builds each block carefully, with an emphasis on the idea that most
beginners find hardest: that a variable can point to different data at
different times, and that some data can be changed in place while other
data cannot.

## Learning outcomes

By the end of this lesson, you will be able to:

- Identify a value, an expression, a statement, and a variable in a small
  piece of Python code.
- Explain what assignment does, and why `=` in Python does not mean
  "equals" the way it does in mathematics.
- Explain the difference between reassigning a variable and mutating the
  data it points to.
- Predict, correctly, what a variable holds after a sequence of assignments.

## Prerequisites

- [Algorithms, Programs, and Data](01-algorithms-programs-and-data.md)
- Ability to run a simple Python file (from Stage 0 and topic 1).

## Key terms

| Term | Plain-English definition |
|---|---|
| **Value** | A piece of data represented in a Python program, such as the number `7`, the text `"apple"`, or the list `[1, 2, 3]`. |
| **Expression** | A piece of Python syntax that Python can evaluate to produce a value, such as `3 + 4` or `len("hello")`. |
| **Statement** | A syntactic unit in a Python program that represents an action or other operation (some statements contain expressions), such as `total = 3 + 4` or `print(total)`. |
| **Variable** | A name that refers to an object (a value), so you can use that value again later by name instead of retyping it. |
| **Assignment** | The act of connecting a name to a value using `=`, such as `age = 25`. |
| **Reassignment** | Pointing a variable's name at a *new* value, replacing what it pointed to before. |
| **Mutation** | Changing the state of an existing mutable object in place — only possible for certain data types, like lists. |

## Step-by-step explanation

### 1. Values: the raw material

A **value** is a concrete piece of data represented in a Python program. Examples of values in
Python:

```text
42            # a whole number (int)
3.14          # a number with a decimal point (float)
"hello"       # text (a string)
True          # a Boolean value: True or False
[1, 2, 3]     # a list of values
```

Every value has a **type**, which tells Python (and you) what kind of thing
it is and what you're allowed to do with it. You will study types in detail
in Module 1.2; for now, just notice that values come in different kinds.

### 2. Expressions: recipes that produce a value

An **expression** is a piece of Python syntax that Python can evaluate
(work out) to produce a value. `3 + 4` is an expression; when Python evaluates it, it
produces the value `7`. `"a" + "b"` is also an expression; it produces the
value `"ab"`. Expressions can be as simple as a single value (`42` is
technically an expression that evaluates to itself) or as complex as a
combination of many operations.

### 3. Statements: complete instructions

A **statement** is a syntactic unit in a Python program that represents an
action or other operation. Some
statements contain an expression; some don't. Examples:

```text
total = 3 + 4     # an assignment statement (contains the expression 3 + 4)
print(total)      # a statement that calls the print instruction
```

The difference matters: an **expression** produces a value but does not, by
itself, do anything with it. A **statement** is a complete step in your
program. `3 + 4` alone, typed on its own line in a script, computes `7` and
then throws it away, because nothing tells Python to keep or show it.

### 4. Variables and assignment: naming a value

A **variable** is a name you give to a value so you can refer to it again.
In Python, a name refers to an object. In beginner examples, we often call
such a name a variable because its binding can change during the program.
You create one with an **assignment statement**, using the `=` sign:

```python
age = 25
```

Read this out loud as **"age is assigned the value 25"**, never as "age
equals 25." This distinction matters because `=` in Python does not test
whether two things are equal — that job belongs to `==`, which you will
meet in [topic 4](04-sequence-selection-iteration-and-abstraction.md). The
`=` sign always means "take the value on the right, and connect the name on
the left to it." For a simple assignment like this, Python evaluates the
right-hand side expression before binding the resulting value to the name
on the left.

Once a variable is assigned, you can use its name anywhere you could use
the value itself:

```python
age = 25
next_year_age = age + 1
print(next_year_age)   # 26
```

### 5. Reassignment: pointing the name somewhere new

A variable is not locked to its first value forever. You can **reassign**
it — point the same name at a different value:

```python
score = 10
print(score)   # 10
score = 20
print(score)   # 20
```

Nothing about the integer object itself was changed. What changed is that
the name `score` now refers to a different object (`20`). Think of a
variable as a **label on a box**, not a permanently fixed container: you
can peel the label off one box and stick it on a different box. This is
only a mental model: Python names refer to objects rather than acting as
physical containers.

### 6. Mutation: changing a value without reassigning the name

Some values in Python — importantly, **lists** — can be changed **in
place**, without reassigning the variable. Mutation means changing the
state of an existing mutable object in place. It is called **mutation**, and it is one of the most important ideas for
a beginner to get right, because it looks different from reassignment even
though both use a variable name.

```python
scores = [10, 20, 30]
scores.append(40)
print(scores)   # [10, 20, 30, 40]
```

Here, `scores` was **never reassigned** — there is no `scores = ...` line
after the first one. Instead, `.append(40)` reached *inside* the existing
list and added a new item to it. The variable `scores` still points to the
very same list it always did; that list itself just changed shape.

Compare this with numbers and text, which **cannot** be mutated:

```python
name = "sam"
name.upper()
print(name)   # still "sam" — upper() did NOT change name
```

`.upper()` produces a *new* piece of text (`"SAM"`) but does not change the
original. Since we never captured that new text with `name = name.upper()`,
it was calculated and then thrown away, and `name` still holds the
original, unchanged value. Text and numbers in Python are **immutable** —
they can never be changed in place, only replaced. Lists (and a few other
types you will meet later) are **mutable** — they can be changed in place.
This difference will matter a great deal once you start passing data
between functions.

## Examples

### Example 1 — Values, an expression, and a statement, side by side

```python
price = 19.99
quantity = 3
total_cost = price * quantity
print(total_cost)
```

**Plain-English explanation:**

- `price = 19.99` is an assignment statement. `19.99` is a value (a
  `float`, a number with a decimal point). After this line, the name
  `price` refers to `19.99`.
- `quantity = 3` is another assignment statement. `3` is a value (an
  `int`, a whole number). The name `quantity` now refers to `3`.
- `total_cost = price * quantity` is also an assignment statement. The part
  to the right of `=`, `price * quantity`, is an **expression** — Python
  first looks up what `price` and `quantity` currently refer to (`19.99`
  and `3`), multiplies them to get `59.97`, and *then* assigns that result
  to the new name `total_cost`. For a simple assignment like this, Python
  evaluates the right-hand side expression before binding the resulting
  value to the name on the left.
- `print(total_cost)` is a statement that displays `59.97` on the screen.

### Example 2 — Reassignment: the running-total pattern

```python
balance = 100
balance = balance - 30
balance = balance - 15
print(balance)
```

**Plain-English explanation:**

- `balance = 100` creates the variable `balance`, pointing it at the value
  `100`.
- `balance = balance - 30` is where beginners often get confused, because
  it looks like an equation that can never be true ("balance equals
  balance minus 30"?). Remember: `=` is not equality. Python evaluates the
  right-hand side first, using `balance`'s *current* value: `100 - 30`
  equals `70`. Then it reassigns `balance` to point to this new value,
  `70`. The old value, `100`, is not changed — it's simply no longer
  referred to by anything.
- `balance = balance - 15` repeats the same idea: it reads the current
  value of `balance` (`70`), subtracts `15` to get `55`, and reassigns
  `balance` to `55`.
- `print(balance)` shows `55`. Every assignment statement in this example
  fully computes the right-hand side using the *current* values before
  changing what the name points to.

### Example 3 — Reassignment versus mutation, made concrete with passwords

This example is the hardest of the three, because it puts reassignment and
mutation side by side so you can see they are genuinely different actions.

```python
password_attempts = []

password_attempts.append("qwerty")
password_attempts.append("letmein")
print(password_attempts)          # ['qwerty', 'letmein']

backup_attempts = password_attempts
backup_attempts.append("hunter2")
print(password_attempts)          # ['qwerty', 'letmein', 'hunter2']

password_attempts = ["reset"]
print(password_attempts)          # ['reset']
print(backup_attempts)            # ['qwerty', 'letmein', 'hunter2']
```

**Plain-English explanation:**

- `password_attempts = []` creates an empty list and names it
  `password_attempts`.
- The two `.append(...)` calls **mutate** the list in place, adding items
  to the same list. `password_attempts` was never reassigned — it still
  points to the same list object, which now has two items in it.
- `backup_attempts = password_attempts` does **not** copy the list. It
  makes `backup_attempts` a second name for the *exact same* list that
  `password_attempts` already points to. Now there are two labels stuck on
  one box.
- `backup_attempts.append("hunter2")` mutates that shared list by adding a
  third item. Because both names point to the same list, printing
  `password_attempts` right after shows all three items too — the change
  is visible through either name, because there is only one list.
- `password_attempts = ["reset"]` is a **reassignment**, not a mutation. It
  makes the name `password_attempts` point to a brand-new list,
  `["reset"]`, completely separate from the list it used to point to. The
  old three-item list still exists — `backup_attempts` still points to it.
- The final two `print` lines show the result: `password_attempts` now
  shows the new, separate list (`['reset']`), while `backup_attempts`
  still shows the original shared list with all three attempts. This is
  exactly why the difference between reassignment and mutation matters:
  two names can silently point to the same mutable data, and changing the
  data through one name affects what you see through the other — but
  reassigning one name never affects the other.

## Common beginner mistakes

- **Reading `=` as mathematical equality.** `x = x + 1` is nonsense in
  algebra but completely normal in Python — it means "compute the current
  value of `x` plus one, then make `x` refer to that new result."
- **Assuming `variable_2 = variable_1` makes an independent copy.** As
  Example 3 shows, for mutable data like lists, this only creates a second
  name for the *same* data. To make a separate list, you can use
  `variable_2 = variable_1.copy()` (or `list(variable_1)`), which creates a
  shallow copy of the list. The new outer list is separate from the
  original list, but nested mutable objects inside it can still be shared.
  This becomes especially important in Module 1.2.
- **Expecting a method like `.upper()` to change the original text.** Text
  is immutable; methods that seem to "transform" it actually return a new
  value, which you must capture with an assignment if you want to keep it:
  `name = name.upper()`.
- **Forgetting that the right-hand side of `=` is evaluated completely
  first.** Some beginners think Python updates a variable "as it goes"
  while reading the line left to right; it actually finishes computing the
  whole right-hand side using the *old* values before changing anything on
  the left.

## Try it yourself

1. Predict the output of this code before running it, then run it to
   check:
   ```python
   x = 5
   y = x
   x = x + 10
   print(x, y)
   ```
   Explain in your own words why `y` did or did not change.
2. Create a variable `cart` pointing to an empty list. Use `.append(...)`
   to add three grocery item names to it. Then create a second variable
   `also_cart` pointing at `cart`, and add one more item using
   `also_cart.append(...)`. Print both variables and explain what you see.
3. Write three lines of code that start a variable called `steps_taken` at
   `0`, then increase it by `1000` twice using reassignment (not
   mutation), ending with the correct total printed.
4. Without running any code, write out on paper what each line of the
   following snippet does, then check yourself by running it:
   ```python
   name = "ada"
   shout_name = name.upper()
   name = "grace"
   print(name, shout_name)
   ```

## Summary

- A **value** is a piece of data; an **expression** is a piece of syntax
  that evaluates to a value; a **statement** is a unit of a program that
  represents an action.
- A **variable** is a name that refers to an object (a value), created with an
  **assignment** statement (`=`), which is not the same as mathematical
  equality.
- **Reassignment** points a variable's name at a new object, leaving the
  older object itself unchanged.
- **Mutation** changes the state of an existing mutable object in place,
  without reassigning any name; only certain types (like lists) can be mutated.
- Two variable names can refer to the *same* mutable value at once, so a
  mutation made through one name is visible through the other — this is
  different from reassignment, which only ever affects the one name being
  reassigned.

## Completion checklist

- [ ] I can point to a value, an expression, and a statement in a short
      piece of code and name each one correctly.
- [ ] I can explain why `=` in Python is not the same as mathematical
      equality.
- [ ] I can predict, correctly, what happens when two variables point to
      the same list and one of them is mutated.
- [ ] I can predict, correctly, what happens when one of two variables
      pointing to the same list is instead reassigned.
- [ ] I have completed the "try it yourself" exercises above and can
      explain my answers out loud.

## Connection to later Applied AI and Agentic AI engineering work

Agent and AI-application code constantly passes shared data — conversation
history, a list of tool results, a shopping cart, a document store —
between different parts of a program. Bugs caused by accidentally sharing
and mutating the same list or dictionary (instead of making an intentional
copy) are one of the most common real-world sources of confusing behavior
in exactly this kind of code. Understanding the difference between
reassignment and mutation now, on small examples like passwords and
grocery lists, is what will let you correctly reason about a much bigger
AI agent's internal state later, instead of guessing and getting surprised.
