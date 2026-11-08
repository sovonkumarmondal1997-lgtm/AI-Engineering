# Lists: Mutation, Copying, and Aliasing

**Complete lesson summary, Stage 1 assessment, and solved exercises**

Source: `05-lists-mutation-copying-and-aliasing(1).md`

------------------------------------------------------------------------

## Part 1 --- Lesson summary (under 1,000 words)

### 1. What a list is

A **list** is an ordered, mutable collection of values, written in
square brackets. Use it when several related values belong together,
such as scores, shopping items, or tasks. Lists preserve order, allow
duplicates, and can contain different data types.

``` python
empty_list = []
scores = [10, 20, 30]
mixed = ["Ada", 30, True]
numbers = [5, 3, 5, 1, 3]
print(numbers)  # [5, 3, 5, 1, 3]
```

A list element/item is one value. *Mutable* means the same list can be
changed in place.

### 2. Indexing and slicing

Indexing starts at zero. Negative indexes count from the end (`-1` is
last). An invalid index raises `IndexError`.

``` python
fruits = ["apple", "banana", "cherry"]
print(fruits[0])   # apple
print(fruits[-1])  # cherry
# fruits[10] raises IndexError
```

For a calculated non-negative position, check its range first:

``` python
position = 10
if 0 <= position < len(fruits):
    print(fruits[position])
else:
    print("That position does not exist in this list.")
```

Slicing uses `[start:stop:step]`; the stop is excluded. It supports
omitted boundaries, negative indexes, and steps. A slice always creates
a **new outer list**.

``` python
numbers = [10, 20, 30, 40, 50]
print(numbers[1:3])   # [20, 30]
print(numbers[:2])    # [10, 20]
print(numbers[3:])    # [40, 50]
print(numbers[-2:])   # [40, 50]
print(numbers[::2])   # [10, 30, 50]
print(numbers[::-1])  # [50, 40, 30, 20, 10]

original = [1, 2, 3]
copy_via_slice = original[:]
copy_via_slice.append(4)
print(original)        # [1, 2, 3]
print(copy_via_slice)  # [1, 2, 3, 4]
```

Use `in` / `not in` to test membership; each returns a Boolean:

``` python
print("banana" in fruits)      # True
print("orange" not in fruits)  # True
```

### 3. Mutation: changing a list in place

Unlike immutable strings, lists can be changed without assigning a new
list:

``` python
cart = ["apples", "bread"]
cart.append("milk")       # add at end
cart[0] = "green apples"  # replace by index
cart.remove("bread")      # remove first matching value
cart.reverse()            # reorder in place
cart.clear()              # remove all elements
print(cart)               # []
```

A key distinction: `.sort()` and `.reverse()` mutate the original and
return `None`. Do not assign their result:

``` python
numbers = [3, 1, 2]
result = numbers.sort()
print(numbers)  # [1, 2, 3]
print(result)   # None
# numbers = numbers.sort() would replace numbers with None
```

Use `sorted(numbers)` for a new sorted list. `reversed(numbers)` returns
an iterator; use `list(reversed(numbers))` to make a new list.

### 4. Aliasing, copying, and nested lists

An **alias** is another name for the exact same list. Assignment does
not copy:

``` python
original_list = [1, 2, 3]
alias_list = original_list
alias_list.append(4)
print(original_list)  # [1, 2, 3, 4]
print(alias_list)     # [1, 2, 3, 4]
```

To make an independent **shallow copy**, use `.copy()`, `[:]`, or
`list(...)`:

``` python
original_list = [1, 2, 3]
copy_a = original_list.copy()
copy_b = original_list[:]
copy_c = list(original_list)
copy_a.append(99)
print(original_list)  # [1, 2, 3]
print(copy_a)         # [1, 2, 3, 99]
```

A shallow copy duplicates only the outer list. Inner lists remain
shared:

``` python
matrix = [[1, 2], [3, 4]]
shallow = matrix.copy()
shallow[0].append(99)
print(matrix)   # [[1, 2, 99], [3, 4]]
shallow.append([5, 6])
print(matrix)   # unchanged by this outer-list append
```

For independent nested mutable objects, the standard-library
`copy.deepcopy()` can recursively copy them:

``` python
import copy
matrix = [[1, 2], [3, 4]]
deep = copy.deepcopy(matrix)
deep[0].append(99)
print(matrix)  # [[1, 2], [3, 4]]
print(deep)    # [[1, 2, 99], [3, 4]]
```

### 5. Built-ins and iteration

``` python
numbers = [4, 8, 1, 9, 3]
print(len(numbers))                 # 5
print(min(numbers), max(numbers))   # 1 9
print(sum(numbers))                 # 25
print(sorted(numbers))              # [1, 3, 4, 8, 9]
print(numbers)                      # original order unchanged
print(list(reversed(numbers)))      # [3, 9, 1, 8, 4]

fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)
for position, fruit in enumerate(fruits):
    print(position, fruit)
```

`any(values)` is true if at least one element is truthy; `all(values)`
is true only if every element is truthy:

``` python
scores = [55, 82, 91, 40]
passing_results = []
for score in scores:
    passing_results.append(score >= 60)
print(passing_results)  # [False, True, True, False]
print(any(passing_results))  # True
print(all(passing_results))  # False
```

### 6. Lesson's three practical examples

-   **To-do list:** start with `tasks = []`, append `"Write report"`,
    `"Review code"`, and `"Email client"`; print the list, `len(tasks)`
    (3), and `tasks[0]` (first task).
-   **Exam statistics:** `raw_scores = [72, 95, 68, 88, 91]`;
    `sorted(raw_scores)` creates `[68, 72, 88, 91, 95]` without changing
    the original. `max`, `min`, and `sum(raw_scores) / len(raw_scores)`
    produce highest 95, lowest 68, average 82.8.
-   **Aliasing pitfall:** `team_b = team_a` means appending `"Alan"`
    through `team_b` also changes `team_a`. `team_c = team_a.copy()`
    creates an independent list; appending `"Linus"` to `team_c` does
    not change `team_a`.

### 7. Common mistakes and method reference

Avoid: assuming assignment copies; assigning `.sort()`/`.reverse()`
results; indexing at `len(list)`; confusing `.remove(value)` with
`.pop(index)`; assuming shallow copies isolate nested lists; assuming
lists remove duplicates or enforce one type.

The appendix lists all **11 public non-dunder list methods**:

  -----------------------------------------------------------------------
  Method                              Purpose and effect
  ----------------------------------- -----------------------------------
  `append(item)`                      Add one item at end; mutates,
                                      returns `None`.

  `extend(iterable)`                  Add each iterable element; mutates,
                                      returns `None`. Unlike `append`, it
                                      does not add the whole iterable as
                                      one nested item.

  `insert(index, item)`               Insert at position; mutates,
                                      returns `None`.

  `remove(value)`                     Remove first matching value;
                                      mutates, returns `None`; raises
                                      `ValueError` if absent.

  `pop(index=-1)`                     Remove and return item at index
                                      (last by default); mutates.

  `clear()`                           Remove all items; mutates, returns
                                      `None`.

  `index(value)`                      Return first matching position; no
                                      mutation; raises `ValueError` if
                                      absent.

  `count(value)`                      Count occurrences; no mutation.

  `reverse()`                         Reverse in place; returns `None`.

  `sort(reverse=True)`                Sort in place; returns `None`;
                                      `reverse=True` gives descending
                                      order.

  `copy()`                            Return a new shallow copy; original
                                      unchanged.
  -----------------------------------------------------------------------

The lesson also gives `dir(list)` as a way to inspect public methods.
Lists later represent batches of documents, conversation messages, tool
calls, and search results; accidental shared mutation can corrupt
application state.

------------------------------------------------------------------------

## Part 2 --- Current learning-level assessment from the Stage 1 project tree

The Stage 1 tree starts with computational thinking and program design,
then Python fundamentals (values, variables, data types, operators,
strings, lists), followed by control flow/functions/errors, collections
and algorithmic habits, files/structured data/CLI, modules and code
quality, testing/debugging, and OOP/data modelling. Later modules cover
production Python, advanced data model and metaprogramming, standard
library, binary/text processing, modern Python, advanced testing,
performance, packaging, CPython internals, design patterns,
visualization, security, refactoring, and functions/OOP gaps. Projects
include an expense-ledger CLI, log-investigation CLI,
data-quality/transformation pipeline, and rule-based risk-review engine.

**Assessment:** This lesson is the next step in Python core data types
after strings. Your curriculum places you at an early Stage
1/foundational level. The project tree describes intended coverage; it
does not prove mastery. I have not received independently executed
exercise outputs, so practical proficiency is not yet verified. The
solutions below stay within the lesson and previously introduced ideas:
variables, strings, indexing/slicing, `if`, `for`, `len`, and simple
methods/functions. `pop`, `sorted(reverse=True)`, and nested lists are
explicitly introduced by this lesson.

------------------------------------------------------------------------

## Part 3 --- All six exercises solved step by step (under 1,500 words)

### Exercise 1 --- Three favorite foods; first and last

``` python
favorite_foods = ["pizza", "rice", "mango"]
print(favorite_foods[0])
print(favorite_foods[-1])
```

-   The list stores three strings in order. Replace these example foods
    with your own.
-   `[0]` reads the first element; `[-1]` reads the last.

Output:

``` text
pizza
mango
```

### Exercise 2 --- Slice `[20, 40, 60]`

``` python
numbers = [10, 20, 30, 40, 50, 60]
selected = numbers[1::2]
print(selected)
```

-   Start at index `1`, which contains `20`.
-   The omitted stop means continue to the end.
-   Step `2` moves two positions each time: indexes 1, 3, 5.

Output: `[20, 40, 60]`

### Exercise 3 --- Append four items, then remove the second with `pop(1)`

``` python
items = []
print(items)

items.append("pen")
print(items)
items.append("book")
print(items)
items.append("notebook")
print(items)
items.append("ruler")
print(items)

removed_item = items.pop(1)
print("Removed:", removed_item)
print(items)
```

-   `[]` creates an empty list.
-   Each `append()` adds one item to the end; each print shows the list
    after that step.
-   `pop(1)` removes and returns the item at index 1 (the second item),
    `"book"`.
-   The returned item is stored in `removed_item`.

Output:

``` text
[]
['pen']
['pen', 'book']
['pen', 'book', 'notebook']
['pen', 'book', 'notebook', 'ruler']
Removed: book
['pen', 'notebook', 'ruler']
```

### Exercise 4 --- Demonstrate aliasing, then copying

``` python
first_list = ["red", "blue"]
second_list = first_list
second_list.append("green")
print(first_list)
print(second_list)

third_list = first_list.copy()
third_list.append("yellow")
print(first_list)
print(third_list)
```

-   `second_list = first_list` creates an alias, not a copy. Both names
    refer to one list.
-   Appending `"green"` through `second_list` therefore appears through
    `first_list` too.
-   `.copy()` creates a separate outer list. Appending `"yellow"` to
    `third_list` does not affect `first_list`.

Output:

``` text
['red', 'blue', 'green']
['red', 'blue', 'green']
['red', 'blue', 'green']
['red', 'blue', 'green', 'yellow']
```

### Exercise 5 --- Sort scores highest to lowest without changing original

``` python
scores = [45, 67, 89, 30, 95]
highest_first = sorted(scores, reverse=True)

print(highest_first)
print(scores)
```

-   `sorted(scores, reverse=True)` returns a new list in descending
    order.
-   `reverse=True` means highest to lowest.
-   `scores` remains in its original order because `sorted()` does not
    mutate it.

Output:

``` text
[95, 89, 67, 45, 30]
[45, 67, 89, 30, 95]
```

### Exercise 6 --- Show that a shallow copy shares inner lists

``` python
groups = [["Ada", "Grace"], ["Alan"]]
groups_copy = groups.copy()

groups_copy[0].append("Katherine")

print(groups)
print(groups_copy)
```

-   `groups` is an outer list containing two inner lists.
-   `.copy()` creates a new outer list, but its inner lists are still
    shared.
-   `groups_copy[0]` and `groups[0]` refer to the same inner list.
    Appending `"Katherine"` is therefore visible through both outer
    lists.

Output:

``` text
[['Ada', 'Grace', 'Katherine'], ['Alan']]
[['Ada', 'Grace', 'Katherine'], ['Alan']]
```

This is the shallow-copy behavior the exercise is designed to
demonstrate.

------------------------------------------------------------------------

## Completion checklist

-   [ ] I can create empty, populated, mixed-type, and
    duplicate-containing lists.
-   [ ] I can index safely and slice with start, stop, and step.
-   [ ] I can explain mutation and distinguish it from returning a new
    value.
-   [ ] I can explain aliasing and make an independent shallow copy.
-   [ ] I understand why nested lists remain shared after a shallow
    copy.
-   [ ] I can use the common list methods and built-in functions in this
    lesson.
-   [ ] I have run all six exercises and checked the outputs.
