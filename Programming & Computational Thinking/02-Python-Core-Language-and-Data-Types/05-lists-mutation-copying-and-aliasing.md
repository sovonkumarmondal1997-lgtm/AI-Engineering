# Lists: Mutation, Copying, and Aliasing

## Why lists matter

Most real information does not come as a single value — it comes as a
collection: a shopping cart full of items, a set of exam scores, a list of
tasks to finish today, the messages in a conversation. Python's **list**
type is the general-purpose tool for holding an ordered collection of
values. This lesson teaches lists from the ground up, and then spends real
time on the single idea that trips up almost every beginner at some point:
that two variable names can secretly point to the *same* list, so that a
change made through one name silently shows up through the other. Getting
this right now will save you from a whole category of confusing bugs
later.

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain what a list is, when to use one, and create empty and populated
  lists.
- Explain that lists keep items in order and allow duplicate values.
- Read items out of a list using zero-based, positive, and negative
  indexes, and explain why `IndexError` happens.
- Extract part of a list using slicing, and explain why slicing produces a
  brand-new list.
- Add, remove, replace, reorder, and clear items in a list, and explain
  why this is possible because lists are **mutable**.
- Explain the difference between a method that mutates a list in place and
  a function that returns a new value, without changing the original.
- Explain **aliasing**: why `second_list = first_list` does not create a
  copy, and how a change through one name affects the other.
- Create a real, independent copy of a list using `.copy()`, `[:]`, or
  `list(...)`, and explain how a copy differs from an alias.
- Explain **shallow copying**: why copying a list that contains other
  lists does not independently copy those inner lists too.
- Use the most common list methods and built-in functions confidently, and
  know how to look up any other list method in the appendix.

## Prerequisites

- [Strings: Indexing, Slicing, and Formatting](04-strings-indexing-slicing-and-formatting.md) —
  indexing, slicing, and the idea of methods returning new values were
  first covered there for text; this lesson reuses the same mental model
  for lists.
- [Values, Expressions, Statements, and Variables](../01-Computational-Thinking-and-Program-Design/02-values-expressions-statements-and-variables.md) —
  you already saw a first, brief preview of list mutation and aliasing
  there (the "label on a box" idea, and the `password_attempts` example);
  this lesson gives that preview its full, proper treatment.

## Key terms

| Term | Plain-English definition |
|---|---|
| **List** | An ordered, changeable collection of values, written between square brackets, such as `[1, 2, 3]`. |
| **Element / item** | One single value stored inside a list. |
| **Mutable** | Able to be changed in place, without creating a brand-new value. |
| **Index** | A whole number identifying one element's position inside a list. |
| **Zero-based indexing** | Python's rule that the first element of a list is at position `0`. |
| **Negative index** | An index counted from the end of a list backward, where `-1` is the last element. |
| **`IndexError`** | The error Python raises when you ask for a position that does not exist in a list. |
| **Slice** | A piece of a list extracted using `[start:stop]` or `[start:stop:step]`, always returned as a new list. |
| **Mutation** | Changing a list in place — adding, removing, or altering its elements — without replacing it with a different list. |
| **In-place** | Describes an operation that changes the original data directly, rather than building and returning a new value. |
| **Alias** | A second variable name that refers to the exact same list as another name, rather than to a separate copy. |
| **Copy** | A genuinely separate list containing the same elements, which can be changed without affecting the original. |
| **Shallow copy** | A copy of the outer list only; any lists *inside* it are still shared with the original. |
| **Deep copy** | A copy where every nested list is also independently copied, all the way down. |

## Step-by-step explanation

### 1. What a list is, and when to use one

A **list** is an ordered collection of values, written between square
brackets and separated by commas: `["apple", "banana", "cherry"]`. Use a
list whenever you have more than one related value that naturally belongs
together as a group — the items in a shopping cart, the scores from a set
of exams, the lines read from a file. A single variable like
`price = 4.99` is right for one value; a list is right once you have
*several* values of the same kind to keep track of together.

### 2. Creating empty and populated lists

An **empty list** has no elements yet, and is often the starting point
before adding items one at a time. A **populated list** already contains
values when it is created:

```python
empty_list = []
scores = [10, 20, 30]
mixed = ["Ada", 30, True]
```

`empty_list` starts with nothing inside it. `scores` is created already
holding three numbers. `mixed` shows that a single Python list can hold
values of *different* types at once — a string, an `int`, and a `bool`,
all in the same list — Python does not require every element to share one
type.

### 3. Lists keep order and allow duplicates

Two properties matter from the very start: a list remembers the exact
**order** its elements were placed in, and it happily allows the **same
value more than once**:

```python
numbers = [5, 3, 5, 1, 3]
print(numbers)
```

```text
[5, 3, 5, 1, 3]
```

Nothing is reordered and nothing is removed just because `5` and `3` each
appear twice — a list is not automatically "cleaned up." (This is
different from some other collections you will meet later, such as sets in
Topic 8, which do not allow duplicates at all.)

### 4. List indexing

Just like the strings from the previous lesson, every element in a list
has a numbered position, called an **index**, using **zero-based
indexing**: the first element is at position `0`.

```python
fruits = ["apple", "banana", "cherry"]
print(fruits[0])    # apple  — the first element
print(fruits[-1])   # cherry — the last element, using a negative index
```

**Negative indexes** count backward from the end, exactly as they did for
strings: `-1` is always the last element, `-2` the one before it.

**`IndexError`:** asking for a position that does not exist stops the
program:

```python
fruits = ["apple", "banana", "cherry"]
print(fruits[10])
```

```text
IndexError: list index out of range
```

`fruits` only has valid indexes `0`, `1`, and `2` (or `-1`, `-2`, `-3`);
position `10` does not exist.

**Safely checking length first:** before indexing with a position you
calculated rather than typed directly, compare it against `len()`, exactly
as you practiced for strings:

```python
fruits = ["apple", "banana", "cherry"]
position = 10

if position < len(fruits):
    print(fruits[position])
else:
    print("That position does not exist in this list.")
```

### 5. List slicing

**Slicing** a list works exactly like slicing a string: `[start:stop]`
returns every element from index `start` up to, but not including, index
`stop`.

```python
numbers = [10, 20, 30, 40, 50]
print(numbers[1:3])    # [20, 30]
print(numbers[:2])     # [10, 20]
print(numbers[3:])     # [40, 50]
print(numbers[-2:])    # [40, 50]  — the last two elements
print(numbers[::2])    # [10, 30, 50]  — every second element
print(numbers[::-1])   # [50, 40, 30, 20, 10]  — reversed
```

Omitted `start`/`stop`, negative indexes, and the `step` value all behave
exactly as they did for strings in the previous lesson.

**Why slicing creates a new list:** a slice is never a window onto the
original list — it is always a completely separate, brand-new list. You
can prove this by mutating the slice and checking the original is
untouched:

```python
original = [1, 2, 3]
copy_via_slice = original[:]
copy_via_slice.append(4)

print(original)          # [1, 2, 3]        — unchanged
print(copy_via_slice)    # [1, 2, 3, 4]     — the new list grew
```

`original[:]` (omitting both `start` and `stop`) slices the *entire* list,
which is also, as you will see again in Section 9, one common way to make
a full copy of a list.

### 6. Mutating a list: lists are mutable

As you learned when comparing lists and strings in the previous two
lessons, a **mutable** value can be changed in place, without being
replaced by a new value. Lists are mutable; strings are not. This section
shows the main ways to mutate a list:

```python
cart = ["apples", "bread"]

cart.append("milk")            # add to the end
print(cart)                     # ['apples', 'bread', 'milk']

cart[0] = "green apples"        # replace by index
print(cart)                     # ['green apples', 'bread', 'milk']

cart.remove("bread")            # remove by value
print(cart)                     # ['green apples', 'milk']

cart.reverse()                  # reorder in place
print(cart)                     # ['milk', 'green apples']

cart.clear()                    # remove everything
print(cart)                     # []
```

Notice that `cart` was **never reassigned** with `cart = ...` at any point
after its creation — every line above changed the *same* list object in
place. This is the essence of mutation, and it is only possible because
lists are mutable.

### 7. Mutating methods versus functions that return a new value

Some list operations change the original list and give back nothing
useful; others leave the original completely alone and hand you back a
brand-new value instead. Confusing the two is one of the most common
beginner mistakes with lists, so it deserves its own section before you
meet the full method list.

```python
numbers = [3, 1, 2]
result = numbers.sort()

print(numbers)   # [1, 2, 3]  — sort() mutated the list in place
print(result)    # None       — sort() itself returns nothing
```

**This is the trap:** `numbers.sort()` rearranges `numbers` in place and
returns `None`. If you write `numbers = numbers.sort()`, you have just
destroyed your list, replacing it with `None`! The list's built-in
`.sort()` and `.reverse()` methods (covered fully in the appendix) both
mutate in place and both return `None` — never assign their result to
anything. If you want a *new*, sorted or reversed list while keeping the
original list unchanged, use the built-in functions `sorted(...)` and
`reversed(...)` instead, covered in Section 11 below — they do the
opposite: they leave the original list alone and return a new value.

### 8. Aliasing: why `second_list = first_list` is not a copy

As you briefly saw with the "label on a box" idea in
[Values, Expressions, Statements, and Variables](../01-Computational-Thinking-and-Program-Design/02-values-expressions-statements-and-variables.md),
a variable is a name pointing at a value, not a box that owns it
exclusively. Writing `second_list = first_list` does **not** create a
second, independent list — it simply gives a **second name (an alias)** to
the *exact same* list. Any mutation made through either name is visible
through both, because there is really only one list:

```python
original_list = [1, 2, 3]
alias_list = original_list

alias_list.append(4)

print(original_list)   # [1, 2, 3, 4]  — changed too, even though we never touched this name directly!
print(alias_list)      # [1, 2, 3, 4]
```

This often surprises beginners: nothing was ever done to `original_list`
by name, yet it changed. That is exactly what **aliasing** means — two
labels stuck on the same box. This is entirely different from
reassignment (`original_list = [9, 9, 9]`), which would point
`original_list` at a brand-new list and leave whatever `alias_list` still
points to completely untouched.

### 9. Copying: making an independent list on purpose

When you genuinely want a separate list — one you can change without
affecting the original — you need a real **copy**, not an alias. Python
gives you three equivalent ways to make one:

```python
original_list = [1, 2, 3]

copy_a = original_list.copy()   # the .copy() method
copy_b = original_list[:]       # slicing the whole list
copy_c = list(original_list)    # passing the list to list(...)

copy_a.append(99)

print(original_list)   # [1, 2, 3]        — unaffected
print(copy_a)           # [1, 2, 3, 99]    — only this one grew
print(copy_b)           # [1, 2, 3]
print(copy_c)           # [1, 2, 3]
```

All three approaches build a genuinely separate list containing the same
starting elements. Compare this directly with Section 8: an **alias**
(`second_list = first_list`) shares one list under two names, so mutating
either name affects both; a **copy** (`.copy()`, `[:]`, or `list(...)`)
creates a second, independent list, so mutating the copy never touches the
original.

### 10. Shallow-copy awareness: lists that contain other lists

There is one more subtlety worth knowing before you move on: `.copy()`
(and `[:]`, and `list(...)`) makes what is called a **shallow copy**. If
your list contains other lists, only the *outer* list is truly duplicated
— the inner lists are still shared between the original and the copy.

```python
matrix = [[1, 2], [3, 4]]
shallow = matrix.copy()

shallow[0].append(99)
print(matrix)     # [[1, 2, 99], [3, 4]]   — changed too!
print(shallow)    # [[1, 2, 99], [3, 4]]

shallow.append([5, 6])
print(matrix)     # [[1, 2, 99], [3, 4]]        — unaffected this time
print(shallow)    # [[1, 2, 99], [3, 4], [5, 6]]
```

`shallow[0]` is the *same* inner list object as `matrix[0]` — the copy only
duplicated the outer list, not the lists inside it — so mutating that
inner list (`.append(99)`) shows up in both. Appending a brand-new inner
list directly to `shallow`, however, only changes the outer `shallow`
list itself, which really is independent — so `matrix` is unaffected by
that particular change. This is exactly what "shallow" means: one level
deep is copied; anything nested is still shared.

For the rare cases where you need every nested list to be fully
independent too, Python's standard library provides `copy.deepcopy()`:

```python
import copy

matrix = [[1, 2], [3, 4]]
deep = copy.deepcopy(matrix)

deep[0].append(99)
print(matrix)   # [[1, 2], [3, 4]]        — completely unaffected
print(deep)     # [[1, 2, 99], [3, 4]]
```

`import copy` brings in a standard-library module (imports are covered
properly in Module 1.6); for now, just know that `copy.deepcopy()` exists
as an advanced option for the specific situation of nested, mutable data.
Most beginner programs never need it — a plain `.copy()` is correct and
sufficient the overwhelming majority of the time, as long as you remember
it only copies one level deep.

### 11. Useful built-in functions for lists

Beyond list *methods* (covered fully in the appendix), several general
Python built-in functions work directly on lists and are used constantly:

```python
numbers = [4, 8, 1, 9, 3]

print(len(numbers))              # 5   — how many elements
print(min(numbers))              # 1   — the smallest value
print(max(numbers))              # 9   — the largest value
print(sum(numbers))              # 25  — the total of all elements

print(sorted(numbers))           # [1, 3, 4, 8, 9]  — a NEW sorted list
print(numbers)                    # [4, 8, 1, 9, 3]  — original untouched

print(list(reversed(numbers)))    # [3, 9, 1, 8, 4]  — a NEW reversed list
```

`sorted(...)` and `reversed(...)` are the non-mutating counterparts to the
`.sort()` and `.reverse()` methods from Section 7: they always leave the
original list exactly as it was, and hand back a new result instead —
`sorted(...)` gives back a real list directly, while `reversed(...)` gives
back a special reversible sequence, which is why it is wrapped in
`list(...)` above to display it as an ordinary list.

`enumerate(...)` is useful whenever you need both the position and the
value while going through a list, using a `for` loop (first taught in
Module 1.1):

```python
fruits = ["apple", "banana", "cherry"]
for position, fruit in enumerate(fruits):
    print(position, fruit)
```

```text
0 apple
1 banana
2 cherry
```

`any(...)` and `all(...)` each take a list of `True`/`False` values.
`any(...)` returns `True` if **at least one** is `True`; `all(...)` returns
`True` only if **every single one** is `True`:

```python
scores = [55, 82, 91, 40]

passing_results = []
for score in scores:
    passing_results.append(score >= 60)

print(passing_results)     # [False, True, True, False]
print(any(passing_results))  # True  — at least one student passed
print(all(passing_results))  # False — not every student passed
```

## Examples

### Example 1 — Building a simple to-do list

```python
tasks = []
tasks.append("Write report")
tasks.append("Review code")
tasks.append("Email client")

print(tasks)
print(f"You have {len(tasks)} tasks.")
print(f"Next task: {tasks[0]}")
```

**Plain-English explanation:**

- `tasks = []` starts an empty list, ready to be filled in one item at a
  time — a very common starting pattern.
- Each `.append(...)` call mutates `tasks` in place, adding one more task
  to the end, without ever reassigning the variable.
- `print(tasks)` shows all three tasks, in the exact order they were
  added: `['Write report', 'Review code', 'Email client']`.
- `f"You have {len(tasks)} tasks."` reuses `len()` and f-strings from
  earlier lessons to report the count: `You have 3 tasks.`
- `f"Next task: {tasks[0]}"` uses indexing to read the first task without
  removing it: `Next task: Write report`.

### Example 2 — Exam scores: reporting stats without disturbing the original order

```python
raw_scores = [72, 95, 68, 88, 91]

sorted_scores = sorted(raw_scores)
print(raw_scores)
print(sorted_scores)

highest = max(raw_scores)
lowest = min(raw_scores)
average = sum(raw_scores) / len(raw_scores)

print(f"Highest: {highest}, Lowest: {lowest}, Average: {average:.1f}")
```

**Plain-English explanation:**

- `raw_scores` stores five exam scores in the order they were recorded —
  perhaps the order students submitted them, which is worth preserving.
- `sorted(raw_scores)` — not `.sort()` — is used deliberately here, because
  it returns a *new*, sorted list without touching `raw_scores` at all.
  Printing both confirms this: `raw_scores` still shows the original
  submission order, `[72, 95, 68, 88, 91]`, while `sorted_scores` shows
  `[68, 72, 88, 91, 95]`.
- `max()`, `min()`, and `sum() / len()` compute the highest score, lowest
  score, and average directly from the original list — none of these
  built-in functions mutate their argument either.
- The final f-string, using the `.1f` format specifier from the previous
  lesson, prints:
  `Highest: 95, Lowest: 68, Average: 82.8`.
- This example shows why choosing a non-mutating function (`sorted()`)
  over a mutating method (`.sort()`) matters in practice: the original
  submission order survives, right alongside a sorted view of the same
  data.

### Example 3 — Aliasing pitfall, and the fix with `.copy()`

```python
team_a = ["Ada", "Grace"]
team_b = team_a          # alias, NOT a copy

team_b.append("Alan")
print(team_a)             # ['Ada', 'Grace', 'Alan']  — changed too!
print(team_b)             # ['Ada', 'Grace', 'Alan']

team_c = team_a.copy()    # a real, independent copy
team_c.append("Linus")

print(team_a)   # ['Ada', 'Grace', 'Alan']          — unaffected this time
print(team_c)   # ['Ada', 'Grace', 'Alan', 'Linus']
```

**Plain-English explanation:**

- `team_b = team_a` looks like it creates a second, separate team roster,
  but it does not — as Section 8 explained, it just gives `team_a`'s list
  a second name, `team_b`.
- `team_b.append("Alan")` mutates the one shared list. Because `team_a`
  and `team_b` are two labels on the very same list, printing `team_a`
  right afterward shows `"Alan"` too, even though the code never wrote
  `team_a.append(...)` directly — this is the aliasing surprise from
  Section 8, shown in a realistic setting.
- `team_c = team_a.copy()` finally creates a genuinely independent list,
  starting with the same three names `team_a` currently holds.
- `team_c.append("Linus")` only grows `team_c`. Printing `team_a`
  afterward confirms it is completely unaffected this time — proof that
  `.copy()`, unlike plain assignment, produces a real, separate list.
- The lesson: whenever you want a *second, independent* list to
  experiment with or modify safely, always use `.copy()` (or `[:]`, or
  `list(...)`) — never plain assignment.

## Common beginner mistakes

- **Assuming `second_list = first_list` makes a copy.** As Section 8 and
  Example 3 showed, this only creates a second name for the same list;
  mutating one mutates both. Use `.copy()`, `[:]`, or `list(...)` for a
  real copy.
- **Assigning the result of `.sort()` or `.reverse()` to a variable.**
  Both mutate in place and return `None`; writing
  `numbers = numbers.sort()` destroys your list. Just call
  `numbers.sort()` on its own line, or use `sorted(numbers)` if you want a
  new list.
- **Indexing past the end of a list.** `my_list[len(my_list)]` is always
  one position too far and raises `IndexError`; the last valid index is
  `len(my_list) - 1`, or simply `my_list[-1]`.
- **Using `.remove(value)` when you meant to remove by position.**
  `.remove("bread")` deletes the *first* element equal to `"bread"`, not
  the element at index `"bread"` (which would not even make sense); to
  remove by position, use `.pop(index)` instead (covered in the appendix).
- **Believing `.copy()` fully protects nested lists.** As Section 10
  showed, `.copy()` is a shallow copy: mutating an inner list through the
  copy still affects the original's matching inner list, because both
  share the same inner list object.
- **Forgetting that a list can hold duplicate values and mixed types.**
  Unlike some collections you will meet later, a plain list never
  automatically removes duplicates or enforces one single type.

## Try it yourself

Do not look up full solutions. Predict the output before running each one.

1. Create a list of your three favorite foods. Print the first one using
   indexing, and the last one using a negative index.
2. Given `numbers = [10, 20, 30, 40, 50, 60]`, write one slice expression
   that returns only `[20, 40, 60]` (hint: think about the step value).
3. Start with an empty list, add four items to it one at a time with
   `.append()`, then remove the second item using `.pop(1)`. Print the
   list after each step.
4. Create a list, assign it to a second variable name (an alias, not a
   copy), mutate the list through the second name, and print both names to
   confirm they show the same change. Then repeat the exercise using
   `.copy()` instead, and confirm the two lists are now independent.
5. Given `scores = [45, 67, 89, 30, 95]`, use `sorted()` to print the
   scores from highest to lowest without changing `scores` itself (hint:
   look up `sorted()`'s `reverse` option, or reverse the sorted result with
   slicing).
6. Create a small nested list such as `groups = [["Ada", "Grace"], ["Alan"]]`,
   make a shallow copy with `.copy()`, and demonstrate — by mutating one of
   the inner lists — that the copy and the original still share that inner
   list.

## Summary

- A **list** is an ordered, changeable collection of values, written
  between square brackets; use one whenever you have several related
  values to keep together.
- Lists preserve insertion order and allow duplicate values.
- Indexing (`my_list[0]`, `my_list[-1]`) and slicing
  (`my_list[start:stop:step]`) work just like they do for strings, except
  a list slice is always a brand-new **list**, not a new string.
- Lists are **mutable**: methods like `.append()`, `.remove()`,
  `.reverse()`, and `.clear()` change the list in place, without
  reassigning the variable.
- Some list operations mutate in place and return `None` (`.sort()`,
  `.reverse()`); others leave the original alone and return a new value
  (`sorted()`, `reversed()`) — confusing the two is a very common mistake.
- **Aliasing** (`second_list = first_list`) makes two names share one
  list; mutating through either name affects both. A real **copy**
  (`.copy()`, `[:]`, or `list(...)`) makes a second, independent list.
- A plain copy is a **shallow copy**: nested lists inside it are still
  shared with the original; `copy.deepcopy()` is an advanced tool for the
  rare cases where fully independent nested lists are required.

## Completion checklist

- [ ] I can create empty and populated lists, and explain that lists allow
      duplicates and preserve order.
- [ ] I can index a list with positive and negative positions and explain
      why an index can go out of range.
- [ ] I can write a slice with a start, a stop, and a step, and explain
      why a slice is always a new list.
- [ ] I can add, remove, replace, reorder, and clear items in a list, and
      explain why this is possible because lists are mutable.
- [ ] I can explain the difference between a mutating method (like
      `.sort()`) and a non-mutating function (like `sorted()`), including
      that mutating methods return `None`.
- [ ] I can explain aliasing, demonstrate it with a small example, and fix
      it using `.copy()`.
- [ ] I can explain, with an example, what a shallow copy does and does
      not protect against.
- [ ] I have completed the "try it yourself" exercises above.
- [ ] I know the appendix exists and can find a list method in it when I
      need one I have not memorized.

## Connection to later Applied AI and Agentic AI engineering work

Lists are how you will represent almost every "many things" scenario in
AI-adjacent code later: a conversation's message history, a batch of
documents to process, the sequence of tool calls an agent has made so far,
a list of retrieved search results. The aliasing pitfall from Section 8 is
an especially common, especially costly real-world bug in exactly this
kind of code — accidentally sharing and mutating a list of conversation
messages or tool results between two parts of a program, instead of
intentionally copying it, can silently corrupt state in ways that are very
hard to trace back to their cause. Getting comfortable now with the
difference between an alias and a copy, and between a method that mutates
and a function that returns something new, is exactly the discipline that
prevents that entire category of bug later, when the lists involved are
much bigger and the consequences of a silent mistake are much higher.

---

## Appendix: Complete `list` Method Reference

This appendix was generated against the Python version installed in this
environment — check `python3 --version` yourself if you want to confirm
your own. Run
`python3 -c "print([m for m in dir(list) if not m.startswith('_')])"`
in a terminal at any time to list every public method your own installed
Python provides.

**You do not need to memorize this appendix.** Read through it once to
know what exists, get comfortable with the methods used throughout the
lesson above, and come back here as a reference whenever you need a method
you do not use every day. Every method below is a **public instance
method** of `list` — none of Python's internal "dunder" methods (like
`__len__`) or private methods are included, since you use those indirectly
through built-in functions and operators, not by calling them directly.

For every method, the note explicitly states whether it **mutates** the
original list (changing it in place, usually returning `None`) or
**returns a value** without changing the original.

#### `append(item)`

Adds `item` to the end of the list, as a single new element.

```python
fruits = ["apple", "banana"]
fruits.append("cherry")
print(fruits)   # ['apple', 'banana', 'cherry']
```

**Mutates the list in place; returns `None`.**

#### `extend(iterable)`

Adds every element of `iterable` to the end of the list, individually —
different from `append()`, which would add the whole iterable as one
single nested element.

```python
fruits = ["apple", "banana"]
fruits.extend(["cherry", "date"])
print(fruits)   # ['apple', 'banana', 'cherry', 'date']

fruits2 = ["apple", "banana"]
fruits2.append(["cherry", "date"])
print(fruits2)   # ['apple', 'banana', ['cherry', 'date']]
```

**Mutates the list in place; returns `None`.** Compare the two results
above carefully: `extend()` merged in two new elements; `append()` added
one single element that happens to itself be a list.

#### `insert(index, item)`

Adds `item` at position `index`, shifting later elements one position to
the right.

```python
fruits = ["apple", "cherry"]
fruits.insert(1, "banana")
print(fruits)   # ['apple', 'banana', 'cherry']
```

**Mutates the list in place; returns `None`.**

#### `remove(value)`

Removes the **first** element equal to `value`. Raises `ValueError` if
`value` is not present anywhere in the list.

```python
fruits = ["apple", "banana", "cherry"]
fruits.remove("banana")
print(fruits)   # ['apple', 'cherry']
```

**Mutates the list in place; returns `None`.** Warning: `remove()` takes a
*value* to search for, not a position — use `pop(index)` if you want to
remove by position instead.

#### `pop(index=-1)`

Removes the element at `index` (the last element, by default) and, unlike
`remove()`, **hands that removed value back** to you.

```python
fruits = ["apple", "banana", "cherry"]
removed_item = fruits.pop()
print(removed_item)   # cherry
print(fruits)          # ['apple', 'banana']

first_item = fruits.pop(0)
print(first_item)      # apple
print(fruits)           # ['banana']
```

**Mutates the list in place; returns the removed element.** This is the
key difference from `remove()`: `pop()` gives you back the value it took
out, which is very useful when you need to use that value next.

#### `clear()`

Removes every element, leaving the list empty.

```python
fruits = ["apple", "banana"]
fruits.clear()
print(fruits)   # []
```

**Mutates the list in place; returns `None`.**

#### `index(value)`

Returns the position of the **first** element equal to `value`. Raises
`ValueError` if `value` is not found.

```python
fruits = ["apple", "banana", "cherry"]
print(fruits.index("cherry"))   # 2
```

**Does not mutate; returns an `int`.**

#### `count(value)`

Returns how many times `value` appears in the list.

```python
numbers = [1, 2, 2, 3, 2]
print(numbers.count(2))   # 3
```

**Does not mutate; returns an `int`.**

#### `reverse()`

Reverses the order of the list's elements, in place.

```python
numbers = [1, 2, 3]
numbers.reverse()
print(numbers)   # [3, 2, 1]
```

**Mutates the list in place; returns `None`.** For a *new*, reversed list
that leaves the original untouched, use the built-in `reversed(...)`
function from Section 11 instead.

#### `sort()`

Sorts the list's elements in place, from smallest to largest by default.

```python
numbers = [3, 1, 2]
numbers.sort()
print(numbers)   # [1, 2, 3]

numbers.sort(reverse=True)
print(numbers)   # [3, 2, 1]
```

**Mutates the list in place; returns `None`.** This is the exact trap
covered in Section 7: never write `numbers = numbers.sort()`. The optional
`reverse=True` argument sorts largest to smallest instead; for a *new*
sorted list that leaves the original untouched, use the built-in
`sorted(...)` function from Section 11.

#### `copy()`

Returns a new, independent (shallow) copy of the list.

```python
original = [1, 2, 3]
duplicate = original.copy()
duplicate.append(4)

print(original)    # [1, 2, 3]
print(duplicate)    # [1, 2, 3, 4]
```

**Does not mutate the original; returns a new list.** See Sections 9 and
10 for a full discussion of copying versus aliasing, and the shallow-copy
limitation with nested lists.

## Appendix summary

That covers all 11 public, non-dunder methods on `list` available in this
Python installation. Come back to this reference whenever you need it —
you are not expected to remember all of it, only to know it exists and how
to find what you need.
