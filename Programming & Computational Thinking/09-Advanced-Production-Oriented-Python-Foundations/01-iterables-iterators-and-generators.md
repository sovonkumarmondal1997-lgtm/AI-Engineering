# Iterables, Iterators, and Generators

> **Stage 1 — Programming and Computational Thinking**  
> **Module 1.9 — Advanced Production-Oriented Python Foundations**

## Learning Objectives

By the end of this chapter, you should be able to:

1. Explain what iteration means in programming.
2. Explain what an **iterable** is.
3. Explain what an **iterator** is.
4. Distinguish an iterable from an iterator.
5. Explain Python's iteration protocol.
6. Use `iter()` correctly.
7. Use `next()` correctly.
8. Explain `StopIteration`.
9. Explain how a `for` loop works conceptually.
10. Explain why common Python objects such as lists, strings, dictionaries, sets, ranges, and files are iterable.
11. Explain why iterators are consumed as they are traversed.
12. Explain why `iter(iterable)` produces an iterator.
13. Explain why `iter(iterator) is iterator` is generally true.
14. Build custom iterators with `__iter__()` and `__next__()`.
15. Write generator functions using `yield`.
16. Explain generator suspension, resumption, and state.
17. Write generator expressions.
18. Explain lazy evaluation.
19. Compare eager and lazy processing.
20. Reason about memory and traversal trade-offs.
21. Process large files incrementally with generators.
22. Build and compose generator-based pipelines.
23. Explain generator exhaustion.
24. Decide when to return a collection, iterator, or generator.
25. Debug iterator and generator problems.
26. Test normal behavior, edge cases, and exhaustion.
27. Explain practical production use cases and trade-offs.

---

# 1. Introduction

## 1.1 What does "iteration" mean?

**Iteration** means processing a series of values one at a time.

For example:

```python
numbers = [10, 20, 30]

for number in numbers:
    print(number)
```

Output:

```text
10
20
30
```

At the surface, this looks simple:

> "Take each item from `numbers` and run the loop body."

That is exactly the mental model you should start with.

But Python needs a well-defined mechanism for answering an important question:

> **How does Python know how to get the next value?**

That question leads to three related concepts:

- **Iterable** — something Python can obtain an iterator from.
- **Iterator** — an object that produces the next value and remembers its current position/state.
- **Generator** — a convenient Python mechanism for creating iterators lazily.

A useful relationship is:

```text
Iterable
   |
   | iter(...)
   v
Iterator
   |
   | next(...)
   v
value
   |
   | next(...)
   v
value
   |
   | ...
   v
StopIteration
```

The exact implementation details vary between objects, but this is the correct language-level mental model.

---

## 1.2 Why iteration matters so much in Python

Iteration is fundamental because programs constantly process sequences of things:

- rows from a file
- records from a database
- messages from a queue
- elements of a list
- keys in a dictionary
- samples in a dataset
- documents in an ingestion process
- log lines
- generated values
- transformed records in a pipeline

Python deliberately makes many different objects work with the same iteration mechanism.

That means code can often be written against the **iteration protocol** rather than against one particular data structure.

For example, this function does not care whether `values` is a list, tuple, file, generator, or another iterable:

```python
def print_values(values):
    for value in values:
        print(value)
```

This is one of the major reasons Python's iteration model is powerful.

---

## 1.3 Why the topic matters in production engineering

For a small dataset, this is usually harmless:

```python
records = [1, 2, 3, 4, 5]
```

For a very large source, materializing everything may be unnecessary or even impossible.

Imagine a 100 GB log file.

A design like this is often undesirable:

```python
with open("application.log", "r", encoding="utf-8") as file:
    lines = file.readlines()
```

The program asks for all lines to be materialized at once.

A streaming design can instead process one line at a time:

```python
with open("application.log", "r", encoding="utf-8") as file:
    for line in file:
        process(line)
```

Generators let you build this idea into reusable pipelines:

```text
input
  ↓
read
  ↓
parse
  ↓
filter
  ↓
transform
  ↓
aggregate/output
```

The computation can remain lazy until values are actually requested.

This is especially useful for:

- data processing
- log processing
- ETL-style workflows
- AI/ML preprocessing
- document ingestion
- evaluation dataset processing
- memory-sensitive utilities
- streaming transformations

---

## 1.4 A real-world analogy

Imagine a box containing 1,000 books.

An **iterable** is like a source from which you can obtain a way to access the books one by one.

An **iterator** is like the mechanism that keeps track of which book should be handed to you next.

A **generator** is like a simple machine that produces or retrieves the next book only when you ask for it, instead of preparing all 1,000 books in advance.

This analogy is useful for intuition, but it is not Python's actual implementation.

The Python rules are defined by the iteration protocol.

---

# 2. What Does "Iterable" Mean?

## 2.1 Beginner definition

An **iterable** is an object from which Python can obtain an iterator.

That means you can usually write:

```python
for item in object:
    ...
```

because Python knows how to obtain an iterator for that object.

A practical way to explore this is:

```python
numbers = [10, 20, 30]

iterator = iter(numbers)

print(type(numbers))
print(type(iterator))
```

Typical output:

```text
<class 'list'>
<class 'list_iterator'>
```

The exact iterator type name can be implementation-specific, so focus on the relationship:

```text
list
  ↓
iter(list)
  ↓
iterator
```

---

## 2.2 Common Python iterables

Many familiar Python objects are iterable:

- `list`
- `tuple`
- `str`
- `dict`
- `set`
- `range`
- file objects

Example:

```python
for value in [1, 2, 3]:
    print(value)

for value in (1, 2, 3):
    print(value)

for character in "Python":
    print(character)

for number in range(3):
    print(number)
```

Each object provides a way for Python to obtain an iterator.

---

## 2.3 Why is a list iterable?

A list is designed to represent an ordered collection of values.

Python therefore gives lists an iteration behavior so that code can request their elements sequentially.

You generally do not need to call `__iter__()` yourself.

Use:

```python
iterator = iter(numbers)
```

rather than:

```python
iterator = numbers.__iter__()
```

The built-in `iter()` expresses the intent clearly and uses Python's normal iteration machinery.

---

## 2.4 A subtle but important accuracy point

It is common to hear:

> "An iterable is anything that has `__iter__()`."

That is useful as an introductory rule, but it is not the complete practical story.

Python's built-in `iter(obj)` first uses the object's iteration machinery. For objects that do not provide the normal `__iter__()` method, Python also supports a legacy sequence-style mechanism based on indexed access beginning at zero.

For example, this object can be iterated:

```python
class LegacySequence:
    def __getitem__(self, index):
        values = ["a", "b", "c"]

        if index >= len(values):
            raise IndexError

        return values[index]


data = LegacySequence()

for value in data:
    print(value)
```

Output:

```text
a
b
c
```

This is a useful language-level nuance:

- Many modern iterables expose `__iter__()`.
- Python's `iter()` also supports certain sequence-style objects through `__getitem__()`.

Therefore, "an iterable is an object that can be passed to `iter()` successfully" is a safer conceptual definition.

### `collections.abc.Iterable` nuance

Python also provides an abstract base class:

```python
from collections.abc import Iterable

print(isinstance([1, 2, 3], Iterable))
```

This is useful for checking many standard iterable objects.

However, `collections.abc.Iterable` detection is not exactly the same question as:

> "Can `iter(obj)` successfully iterate over this object?"

In particular, legacy sequence-style iteration through `__getitem__()` is an important reason not to treat the ABC check as a perfect universal definition of iterability.

This is an advanced nuance; for day-to-day code, prefer the normal protocol rather than trying to manually reconstruct it.

---

# 3. Iterable vs Collection vs Sequence

These terms overlap, but they are not synonyms.

## 3.1 Iterable

An iterable is primarily about this capability:

> **Can Python obtain values from this object through the iteration protocol?**

Examples:

- list
- tuple
- string
- dict
- set
- range
- file
- generator

---

## 3.2 Collection

A collection generally represents a group of elements with richer collection-oriented behavior, such as:

- being iterable
- usually knowing its size
- usually supporting membership testing

Many familiar containers are collections.

Examples include lists, tuples, sets, and dictionaries.

A file object is iterable, but it is not a collection in the same sense as a list.

---

## 3.3 Sequence

A sequence represents an ordered series with sequence-oriented behavior such as positional access.

Typical examples:

- `list`
- `tuple`
- `str`
- `range`

For example:

```python
values = ["a", "b", "c"]

print(values[0])
print(values[1])
```

Output:

```text
a
b
```

A sequence is iterable, but "iterable" is the broader idea.

---

## 3.4 Important examples

### `range`

```python
r = range(1_000_000)

print(r.start)
print(r.stop)
print(r.step)
```

A `range` object represents an arithmetic progression without requiring a giant list of all those integers.

It is:

- iterable
- re-iterable
- sequence-like
- lightweight compared with materializing the same values in a list

### File object

```python
with open("application.log", "r", encoding="utf-8") as file:
    for line in file:
        print(line)
```

A file object is an iterable source of lines. It is not a collection containing every line of the file.

### Generator

```python
numbers = (x * 2 for x in range(5))
```

A generator is an iterable and an iterator. It does not represent a fully materialized collection of all generated results.

---

# 4. What Is an Iterator?

An **iterator** is an object that follows Python's iterator protocol.

Its core responsibility is:

> **Give me the next value, or tell me that there are no more values.**

An iterator has state.

For a list iterator over:

```python
[10, 20, 30]
```

the state conceptually includes where the iterator currently is in that sequence.

---

## 4.1 Creating an iterator

```python
numbers = [10, 20, 30]

iterator = iter(numbers)

print(next(iterator))
print(next(iterator))
print(next(iterator))
```

Output:

```text
10
20
30
```

Each call advances the iterator.

You can think of it like:

```text
iterator
   |
   +--> current position: before 10

next()
   |
   +--> 10
   |
   +--> position moves forward

next()
   |
   +--> 20
   |
   +--> position moves forward

next()
   |
   +--> 30
   |
   +--> position moves forward
```

The list itself still exists independently.

The iterator is the stateful traversal mechanism.

---

## 4.2 Iterator exhaustion

After the values have been produced:

```python
numbers = [10, 20, 30]

iterator = iter(numbers)

print(next(iterator))
print(next(iterator))
print(next(iterator))
print(next(iterator))
```

The fourth `next()` raises:

```text
StopIteration
```

This is not an ordinary indication that your entire program has failed.

It is the standard protocol signal meaning:

> **The iterator has no more values to provide.**

---

# 5. The Python Iteration Protocol

This is the central mechanism behind iteration.

## 5.1 The two important methods

For an iterator, the critical methods are:

### `__iter__()`

Returns an iterator.

### `__next__()`

Returns the next value.

When no values remain, `__next__()` raises `StopIteration`.

Conceptually:

```text
iterable
   |
   | iter(iterable)
   v
iterator
   |
   | next(iterator)
   v
value
   |
   | next(iterator)
   v
value
   |
   | ...
   v
StopIteration
```

---

## 5.2 Iterator contract

An object intended to be an iterator should satisfy:

```python
iterator.__iter__() is iterator
```

and provide `__next__()`.

A useful way to express the contract is:

```text
__iter__()
    ↓
returns the iterator object

__next__()
    ↓
returns the next value
    OR
raises StopIteration
```

Once an iterator is exhausted, repeated calls to `__next__()` should continue to signal exhaustion rather than unexpectedly restarting the sequence.

---

## 5.3 Minimal custom iterator

Here is the classic example:

```python
class CountUpTo:
    def __init__(self, limit):
        self.current = 1
        self.limit = limit

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > self.limit:
            raise StopIteration

        value = self.current
        self.current += 1
        return value
```

Using it manually:

```python
counter = CountUpTo(3)

print(next(counter))
print(next(counter))
print(next(counter))
```

Output:

```text
1
2
3
```

And then:

```python
try:
    print(next(counter))
except StopIteration:
    print("Finished")
```

Output:

```text
Finished
```

---

## 5.4 Line-by-line explanation

### Constructor

```python
def __init__(self, limit):
    self.current = 1
    self.limit = limit
```

The iterator needs state:

- `current` says which value should be produced next.
- `limit` tells it when to stop.

### `__iter__`

```python
def __iter__(self):
    return self
```

The object itself is the iterator.

That is why it returns `self`.

### `__next__`

The complete method is:

```python
def __next__(self):
    if self.current > self.limit:
        raise StopIteration

    value = self.current
    self.current += 1
    return value
```

This method is called by `next(counter)`.

The important state transition is:

```text
check completion
    ↓
read current value
    ↓
advance state
    ↓
return value
```

The iterator has reached the end when:

```python
if self.current > self.limit:
    raise StopIteration
```

The current value is saved before the state changes:

```python
value = self.current
```

Then the iterator advances:

```python
self.current += 1
```

Finally it returns the value:

```python
return value
```

---

## 5.5 Iterating the custom iterator with `for`

```python
for number in CountUpTo(3):
    print(number)
```

Output:

```text
1
2
3
```

The `for` loop obtains an iterator and repeatedly calls it until `StopIteration` occurs.

---

# 6. How a `for` Loop Actually Works

Consider:

```python
numbers = [10, 20, 30]

for number in numbers:
    print(number)
```

A useful conceptual model is:

```python
iterator = iter(numbers)

while True:
    try:
        number = next(iterator)
    except StopIteration:
        break

    print(number)
```

This is a **conceptual model**, not a claim that Python literally rewrites every `for` loop into this exact source code.

It explains the behavior you need to understand.

---

## 6.1 Why does `for` need an iterator?

A `for` loop needs a standard way to ask:

> "What is the next value?"

The iterator protocol provides exactly that interface.

That means the same `for` syntax can work with very different sources:

```python
for value in [1, 2, 3]:
    ...

for value in (1, 2, 3):
    ...

for character in "abc":
    ...

for key in {"a": 1, "b": 2}:
    ...

for line in open("application.log", encoding="utf-8"):
    ...
```

The sources are different, but they share an iteration mechanism.

---

## 6.2 Why does the loop stop?

The iterator eventually raises:

```python
StopIteration
```

The `for` machinery handles that signal and ends the loop.

That is why you normally do not write `try/except StopIteration` around every `for` loop.

---

# 7. `iter()` in Detail

## 7.1 One-argument form

The common form is:

```python
iter(object)
```

It asks Python to obtain an iterator for the object.

Example:

```python
numbers = [1, 2, 3]

iterator = iter(numbers)

print(type(iterator))
print(next(iterator))
```

Typical output:

```text
<class 'list_iterator'>
1
```

The exact iterator type name may vary by Python implementation, so treat the type name as diagnostic information rather than a part of your program's logic.

---

## 7.2 Why use `iter()` rather than `__iter__()` directly?

Prefer:

```python
iterator = iter(numbers)
```

rather than:

```python
iterator = numbers.__iter__()
```

Reasons:

1. `iter()` expresses the language-level operation directly.
2. It participates in Python's standard iteration protocol.
3. It can handle more than just the direct `__iter__()` method case.
4. It communicates intent to readers.

---

## 7.3 Iterators are iterable too

An iterator is itself iterable.

Consider:

```python
numbers = [1, 2, 3]

iterator = iter(numbers)

print(iter(iterator) is iterator)
```

Output:

```text
True
```

Why?

Because the iterator must provide a way to obtain itself as an iterator.

Conceptually:

```text
iterable
   |
   +--> iter(iterable) --> iterator

iterator
   |
   +--> iter(iterator) --> same iterator
```

This property lets an iterator work naturally with `for`.

---

# 8. `next()` in Detail

## 8.1 Basic form

```python
next(iterator)
```

asks the iterator:

> "Give me the next value."

Example:

```python
iterator = iter([1, 2, 3])

print(next(iterator))
print(next(iterator))
print(next(iterator))
```

Output:

```text
1
2
3
```

---

## 8.2 `next()` advances state

This is important:

```python
iterator = iter([10, 20, 30])

first = next(iterator)
second = next(iterator)

print(first)
print(second)
```

Output:

```text
10
20
```

The second call does not return `10` again.

The iterator has state and has moved forward.

---

## 8.3 `next(iterator, default)`

Python provides an optional default:

```python
iterator = iter([1, 2])

print(next(iterator, "DONE"))
print(next(iterator, "DONE"))
print(next(iterator, "DONE"))
```

Output:

```text
1
2
DONE
```

This can be useful when you want:

> "Give me the next value, but use this default if the iterator is exhausted."

It avoids explicitly catching `StopIteration` for that specific operation.

Use it intentionally. It does not make an iterator reusable; it only changes how exhaustion is reported for that `next()` call.

---

# 9. `StopIteration` in Detail

## 9.1 What does `StopIteration` mean?

`StopIteration` means:

> **This iterator has no more values.**

It is a protocol signal.

It is used internally by iteration constructs such as `for`.

---

## 9.2 Manual iteration exposes it

```python
iterator = iter([1, 2])

print(next(iterator))
print(next(iterator))

try:
    print(next(iterator))
except StopIteration:
    print("No more values")
```

Output:

```text
1
2
No more values
```

---

## 9.3 `for` hides it

With:

```python
for value in [1, 2]:
    print(value)
```

you do not see `StopIteration`.

The iteration machinery handles it for you.

---

## 9.4 Common mistakes involving `StopIteration`

### Mistake 1: Treating exhaustion as unexpected corruption

Exhaustion is normal for an iterator.

### Mistake 2: Catching it too broadly

Do not casually write:

```python
try:
    ...
except Exception:
    ...
```

around an iteration pipeline just because you expect exhaustion.

Usually, a `for` loop is the cleaner abstraction.

### Mistake 3: Forgetting that manual `next()` needs a plan

If you call `next()` directly, you need to decide what happens at exhaustion:

- catch `StopIteration`
- use `next(iterator, default)`
- or structure the code so exhaustion is expected and handled explicitly

---

# 10. Iterable vs Iterator — Critical Comparison

| Property | Iterable | Iterator |
|---|---|---|
| Main purpose | Provides a source from which an iterator can be obtained | Produces the next value |
| Has traversal state? | Not necessarily | Yes, typically |
| `iter(obj)` | Produces an iterator | Usually returns the same object |
| `__iter__()` | Must support obtaining an iterator in normal iteration | Returns itself |
| `__next__()` | Not required just to be an iterable | Required |
| Can be exhausted? | Not necessarily | Yes |
| Restartable? | Often, but not universally | Usually no; it is one-pass |
| Common examples | list, tuple, dict, set, range, string | list iterator, file object, generator |
| Typical behavior | Re-iterated by creating new iterators | Progressively consumed |

The key distinction is:

> **An iterable is a source from which iteration can begin. An iterator is the stateful object that performs the traversal.**

---

## 10.1 Reusable iterable

```python
numbers = [1, 2, 3]

for value in numbers:
    print(value)

for value in numbers:
    print(value)
```

Output:

```text
1
2
3
1
2
3
```

A new iterator can be obtained each time.

---

## 10.2 One iterator

```python
numbers = [1, 2, 3]
iterator = iter(numbers)

for value in iterator:
    print(value)

for value in iterator:
    print(value)
```

Output:

```text
1
2
3
```

The second loop produces nothing because the iterator has already been exhausted.

This distinction is one of the most important things to understand in the entire chapter.

---

# 11. Common Built-in Iterables

## 11.1 List

```python
numbers = [10, 20, 30]

for number in numbers:
    print(number)
```

A list is:

- iterable
- a collection
- a sequence
- reusable for iteration
- indexable

---

## 11.2 Tuple

```python
values = ("a", "b", "c")

for value in values:
    print(value)
```

A tuple is also:

- iterable
- a collection
- a sequence
- reusable

---

## 11.3 String

```python
word = "cat"

for character in word:
    print(character)
```

Output:

```text
c
a
t
```

Strings are iterable character by character.

---

## 11.4 Dictionary

By default:

```python
data = {
    "name": "Sovon",
    "role": "engineer",
}

for key in data:
    print(key)
```

Output:

```text
name
role
```

Dictionary iteration is over **keys** by default.

You can explicitly choose what to iterate:

```python
for key in data.keys():
    print(key)

for value in data.values():
    print(value)

for key, value in data.items():
    print(key, value)
```

The views returned by `.keys()`, `.values()`, and `.items()` are themselves iterable.

---

## 11.5 Set

```python
values = {"a", "b", "c"}

for value in values:
    print(value)
```

A set is iterable, but you should not rely on a particular iteration order for ordinary set usage.

---

## 11.6 Range

```python
numbers = range(5)

for number in numbers:
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

A range is particularly useful because it represents a sequence mathematically instead of requiring the same kind of storage as a list containing all values.

---

## 11.7 File object

```python
with open("application.log", "r", encoding="utf-8") as file:
    for line in file:
        print(line.rstrip())
```

This is especially important for production work.

A file object can produce lines progressively, which supports streaming-style processing instead of loading the entire file into a list.

---

# 12. Re-iterable Objects vs One-Time Iterators

This is a deeper way to think about the iterable/iterator distinction.

## 12.1 An iterable can often create multiple independent iterators

```python
numbers = [1, 2, 3]

first = iter(numbers)
second = iter(numbers)

print(first is second)
```

Output:

```text
False
```

Each call to `iter(numbers)` creates a separate traversal object.

Their states are independent:

```python
numbers = [1, 2, 3]

first = iter(numbers)
second = iter(numbers)

print(next(first))
print(next(first))

print(next(second))
```

Output:

```text
1
2
1
```

`second` starts independently.

---

## 12.2 An iterator returns itself

```python
iterator = iter(numbers)

first = iter(iterator)
second = iter(iterator)

print(first is second)
```

Output:

```text
True
```

Both names refer to the same traversal state.

That is exactly why consuming the iterator through one reference affects another reference:

```python
iterator = iter([1, 2, 3])

a = iterator
b = iterator

print(next(a))
print(next(b))
```

Output:

```text
1
2
```

`a` and `b` are not independent traversals.

---

## 12.3 Why this matters in real programs

This distinction appears in:

- file processing
- pipeline code
- event streams
- generator chains
- shared data sources
- APIs that expose iterators

A common bug is accidentally passing the same iterator to two consumers and expecting both to see the complete sequence.

---

# 13. Building Custom Iterators

Generators are usually simpler, but custom iterator classes are worth learning because they teach the protocol directly.

---

## 13.1 Custom iterator: counter

Problem:

> Produce integers from `1` through `limit`.

```python
class Counter:
    def __init__(self, limit):
        self.current = 1
        self.limit = limit

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > self.limit:
            raise StopIteration

        value = self.current
        self.current += 1
        return value
```

Test:

```python
counter = Counter(4)

while True:
    try:
        print(next(counter))
    except StopIteration:
        break
```

Output:

```text
1
2
3
4
```

### Design reasoning

State:

```text
current
limit
```

Transition:

```text
emit current
current += 1
```

Stop condition:

```text
current > limit
```

---

## 13.2 Custom iterator: countdown

Problem:

> Produce `3, 2, 1`, then stop.

```python
class Countdown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration

        value = self.current
        self.current -= 1
        return value
```

Usage:

```python
for number in Countdown(3):
    print(number)
```

Output:

```text
3
2
1
```

### Edge case

```python
print(list(Countdown(0)))
```

Output:

```text
[]
```

---

## 13.3 Custom iterator: range-like iterator

Problem:

> Implement a small iterator that behaves like an increasing arithmetic sequence.

```python
class SimpleRange:
    def __init__(self, start, stop, step=1):
        if step == 0:
            raise ValueError("step must not be zero")

        self.current = start
        self.stop = stop
        self.step = step

    def __iter__(self):
        return self

    def __next__(self):
        if self.step > 0:
            if self.current >= self.stop:
                raise StopIteration
        else:
            if self.current <= self.stop:
                raise StopIteration

        value = self.current
        self.current += self.step
        return value
```

Usage:

```python
print(list(SimpleRange(2, 8, 2)))
print(list(SimpleRange(8, 2, -2)))
```

Output:

```text
[2, 4, 6]
[8, 6, 4]
```

### Important design lesson

A custom iterator must make its state transitions correct for:

- normal input
- empty ranges
- positive steps
- negative steps
- invalid step values

This is why iterator design is about **state machine design**, not merely writing two methods.

---

## 13.4 Custom iterator: chunk iterator

Problem:

> Read from another iterable and yield fixed-size chunks.

Example:

```python
class ChunkIterator:
    def __init__(self, iterable, chunk_size):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        self.iterator = iter(iterable)
        self.chunk_size = chunk_size

    def __iter__(self):
        return self

    def __next__(self):
        chunk = []

        for _ in range(self.chunk_size):
            try:
                chunk.append(next(self.iterator))
            except StopIteration:
                break

        if not chunk:
            raise StopIteration

        return chunk
```

Usage:

```python
chunks = ChunkIterator(range(7), 3)

for chunk in chunks:
    print(chunk)
```

Output:

```text
[0, 1, 2]
[3, 4, 5]
[6]
```

### Design reasoning

The iterator holds:

```text
underlying iterator
chunk size
```

Each `__next__()` call:

1. Creates an empty chunk.
2. Tries to read up to `chunk_size` values.
3. Returns the chunk.
4. If no value can be read at all, signals `StopIteration`.

### Production note

A class like this can be justified when you need a reusable abstraction with explicit configuration and state. But if the behavior is just "read some values and yield chunks," a generator is usually easier to read and maintain.

---

# 14. Generator Functions

Now that the iterator protocol is clear, generators become much easier to understand.

## 14.1 A generator function

```python
def count_up_to(limit):
    current = 1

    while current <= limit:
        yield current
        current += 1
```

This looks similar to an ordinary function, but `yield` changes its behavior.

Calling it:

```python
generator = count_up_to(3)

print(generator)
print(next(generator))
print(next(generator))
print(next(generator))
```

Typical output:

```text
<generator object count_up_to at 0x...>
1
2
3
```

The memory address in the first line is implementation-specific.

The important fact is:

> Calling a generator function creates a **generator object**. The function body does not run through to completion during that call.

---

## 14.2 What is a generator?

A generator is a kind of iterator.

It:

- can be passed to `next()`
- produces values one at a time
- keeps execution state between values
- can be used directly by a `for` loop
- becomes exhausted when it finishes

Generators are one of Python's most convenient tools for creating lazy iterators.

---

# 15. `yield` vs `return`

This distinction must be crystal clear.

## 15.1 Ordinary `return`

```python
def normal_function():
    return 1
```

Calling:

```python
result = normal_function()
print(result)
```

produces:

```text
1
```

The function executes and returns a result.

---

## 15.2 `yield`

```python
def generator_function():
    yield 1
```

Calling:

```python
result = generator_function()

print(result)
```

produces a generator object representation.

No `1` has been printed yet.

Only when you request a value:

```python
print(next(result))
```

do you get:

```text
1
```

---

## 15.3 Core difference

| `return` | `yield` |
|---|---|
| Returns from the function | Produces a value and suspends generator execution |
| Execution ends for that invocation | Execution can resume later |
| A normal function call gets the result immediately | Generator function call creates a generator object |
| Local execution state does not remain active for another `next()` | Generator state is retained across `next()` calls |

---

## 15.4 Execution trace

Consider:

```python
def demo():
    print("before")
    yield 1
    print("middle")
    yield 2
    print("after")
```

Now:

```python
g = demo()
```

At this point:

- a generator object exists
- `"before"` has not printed yet

Next:

```python
print(next(g))
```

Execution:

```text
before
1
```

The generator pauses at the first `yield`.

Next:

```python
print(next(g))
```

Execution resumes after the previous `yield`:

```text
middle
2
```

Next:

```python
try:
    print(next(g))
except StopIteration:
    print("done")
```

Execution resumes:

```text
after
done
```

The generator is now exhausted.

The key mental model is:

```text
call generator function
        ↓
generator object created
        ↓
next()
        ↓
run until yield
        ↓
pause
        ↓
next()
        ↓
resume after yield
        ↓
run until next yield
        ↓
...
        ↓
function ends
        ↓
StopIteration
```

---

# 16. How Generators Work Internally

## 16.1 Language-level model

When you call:

```python
generator = count_up_to(3)
```

the important language-level fact is:

> The call creates a generator object representing suspended generator execution.

The body does not run to completion immediately.

Then:

```python
next(generator)
```

starts or resumes execution until a `yield` is reached or the generator finishes.

At `yield`:

1. A value is produced.
2. The generator suspends.
3. Its execution state remains available for resumption.

The next:

```python
next(generator)
```

continues from where the previous `yield` left off.

---

## 16.2 What state is retained?

Conceptually, the generator retains enough information to continue execution, including things such as:

- local variables
- current execution position
- loop progress
- the values needed by the remaining code

For example:

```python
def counter():
    value = 1

    while value <= 3:
        yield value
        value += 1
```

After yielding `1`, the generator remembers that `value` is `1` and that execution must continue after the `yield`.

After resuming, it executes:

```python
value += 1
```

and can eventually yield `2`.

---

## 16.3 CPython implementation details

The explanation above is the Python language-level model.

CPython implements generators using interpreter-specific machinery for suspended execution frames and generator objects.

You do not need CPython internals to use generators correctly.

Do not confuse:

- **language behavior** — what Python programs can rely on
- **conceptual model** — a simplified explanation of that behavior
- **CPython implementation details** — how one Python implementation achieves it

For production code, the first two levels are usually what matter.

---

# 17. Generator State

Consider:

```python
def demo():
    print("A")
    yield 1
    print("B")
    yield 2
    print("C")
```

Now:

```python
g = demo()

print("created")
print(next(g))
print("between")
print(next(g))
print("between again")
print(next(g))
```

Expected output:

```text
created
A
1
between
B
2
between again
C
Traceback ... StopIteration
```

The final `next(g)` raises `StopIteration`.

### What happened?

1. `g = demo()` created the generator object.
2. The first `next(g)` started execution.
3. `"A"` printed.
4. `yield 1` produced `1` and paused.
5. The second `next(g)` resumed after `yield 1`.
6. `"B"` printed.
7. `yield 2` produced `2` and paused.
8. The third `next(g)` resumed after `yield 2`.
9. `"C"` printed.
10. The function ended.
11. The generator signaled `StopIteration`.

This is generator state in action.

---

# 18. Generator Expressions

A **generator expression** is a compact way to create a generator.

Compare:

```python
numbers = [x * 2 for x in range(5)]
```

with:

```python
numbers = (x * 2 for x in range(5))
```

The brackets mean list comprehension.

The parentheses create a generator expression.

---

## 18.1 Type difference

```python
eager = [x * 2 for x in range(5)]
lazy = (x * 2 for x in range(5))

print(type(eager))
print(type(lazy))
```

Typical output:

```text
<class 'list'>
<class 'generator'>
```

---

## 18.2 Eager comprehension

```python
values = [x * 2 for x in range(5)]
```

The transformed result is materialized as a list.

You can inspect it immediately:

```python
print(values)
```

Output:

```text
[0, 2, 4, 6, 8]
```

---

## 18.3 Generator expression

```python
values = (x * 2 for x in range(5))
```

The results are produced as they are requested.

```python
print(next(values))
print(next(values))
```

Output:

```text
0
2
```

The remaining values have not yet been produced.

---

## 18.4 When to use each

Use a list comprehension when:

- the data is reasonably small
- you need the complete result now
- you need repeated traversal
- you need indexing or other list behavior

Use a generator expression when:

- you only need one-pass consumption
- values can be computed incrementally
- eager materialization is unnecessary
- you want to feed the results into another consumer

---

# 19. Eager vs Lazy Evaluation

## 19.1 Eager evaluation

Eager processing performs the work and materializes the results now.

Example:

```python
squares = [x * x for x in range(1_000_000)]
```

The list contains all one million square results.

---

## 19.2 Lazy evaluation

Lazy processing defers work until values are requested.

Example:

```python
squares = (x * x for x in range(1_000_000))
```

The generator expression does not precompute the complete output sequence.

A value is produced when the generator advances.

---

## 19.3 Compare the mental model

### Eager

```text
source
  ↓
compute everything
  ↓
store everything
  ↓
use results
```

### Lazy

```text
source
  ↓
request one value
  ↓
compute one value
  ↓
consume one value
  ↓
request next value
  ↓
...
```

---

## 19.4 Lazy does not mean faster

A common mistake is:

> "Generators are always faster."

That is false.

A generator can:

- reduce peak memory usage
- defer unnecessary work
- allow processing to start before the entire input is ready
- support streaming composition

But generators can also:

- add per-item Python-level overhead
- make debugging less immediate
- prevent repeated traversal without regeneration/materialization
- defer errors until iteration occurs

Whether a generator is faster depends on the workload.

**Measure when performance matters.**

---

## 19.5 Debugging implication

With eager code:

```python
values = [transform(x) for x in data]
```

errors inside `transform()` happen while the list is being built.

With lazy code:

```python
values = (transform(x) for x in data)
```

errors may occur later, when `values` is consumed.

For example:

```python
def transform(value):
    if value == 3:
        raise ValueError("bad value")
    return value * 2

values = (transform(x) for x in range(5))

print("generator created")

for value in values:
    print(value)
```

The generator can be created successfully before the error is encountered.

This is a crucial debugging characteristic of lazy code.

---

# 20. Memory Trade-offs

The most important reason to understand generators is not that they look elegant.

It is that **they change when and how much data must be materialized**.

Consider:

```python
values = [transform(x) for x in data]
```

versus:

```python
values = (transform(x) for x in data)
```

The trade-offs are:

| Concern | List / eager | Generator / lazy |
|---|---|---|
| Peak memory | Usually higher when many results are materialized | Usually lower for one-pass processing |
| First-result latency | Work may occur before result is available | Can produce an early result |
| Repeated traversal | Easy | Usually requires regeneration |
| Indexing | Supported by list | Not directly |
| Debugging | Often straightforward | Requires understanding deferred execution |
| Composition | Possible, but may materialize stages | Naturally composable |
| Total computation | Usually performed immediately | Performed when values are consumed |
| Resource lifetime | Often shorter if fully materialized | May remain tied to active source while consuming |

The word **usually** matters.

A generator does not magically guarantee constant memory.

For example:

```python
def bad_generator(source):
    cached = list(source)
    for value in cached:
        yield value
```

This is a generator function, but it still materializes the entire input.

The presence of `yield` alone does not make a pipeline memory-efficient.

---

## 20.1 Peak memory vs total work

A generator often helps with **peak memory**, not necessarily with total computation.

Suppose you transform 10 million records.

A lazy pipeline may process:

```text
record 1 → transform → consume
record 2 → transform → consume
...
```

instead of:

```text
transform all 10 million
store all 10 million
then consume
```

Both may perform the same number of transformations.

The major difference can be the amount of intermediate data held at once.

---

## 20.2 When materialization is useful

Materialize intentionally when you need:

- repeated traversal
- random access
- sorting
- length immediately
- stable snapshot semantics
- a result independent of an underlying one-shot source

For example:

```python
records = list(generate_records())

for record in records:
    process_a(record)

for record in records:
    process_b(record)
```

That repeated traversal is a valid reason to materialize.

The engineering rule is not:

> "Never use lists."

It is:

> **Materialize data when the program actually benefits from having the complete result available.**

---

# 21. Generators for Large Files

This is one of the most practical uses of lazy iteration.

## 21.1 A potentially memory-heavy pattern

```python
with open("large.log", "r", encoding="utf-8") as file:
    lines = file.readlines()

for line in lines:
    process(line)
```

The `readlines()` call creates a list containing all lines.

For a large file, that can create substantial memory pressure.

---

## 21.2 Streaming approach

```python
def read_lines(path):
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            yield line
```

The generator yields one line at a time.

Now:

```python
for line in read_lines("application.log"):
    print(line.rstrip())
```

The complete file does not need to be loaded into a Python list first.

---

## 21.3 Filtering

```python
def error_lines(lines):
    for line in lines:
        if "ERROR" in line:
            yield line
```

Now we can compose:

```python
for line in error_lines(read_lines("application.log")):
    print(line.rstrip())
```

The pipeline is:

```text
application.log
     ↓
read_lines()
     ↓
one line
     ↓
error_lines()
     ↓
one matching line
     ↓
print()
```

---

## 21.4 Why this is useful

This pattern is useful for:

- large log files
- ETL-style transformations
- validation passes
- record filtering
- document ingestion
- streaming transformations

The key is that the pipeline can remain one-pass and incremental.

---

## 21.5 File resources and laziness

Notice this:

```python
def read_lines(path):
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            yield line
```

The file is opened when iteration starts and remains associated with the generator while values are being consumed.

This makes the boundary around the I/O resource explicit.

Do not hide long-lived external resources inside a generator without considering ownership and lifetime.

For simple file readers, the `with open(...)` pattern above is a reasonable design.

---

# 22. Generator Pipelines

A **generator pipeline** is a chain where each stage consumes an iterable and yields transformed values.

A common shape is:

```text
Input
  ↓
Read
  ↓
Filter
  ↓
Transform
  ↓
Aggregate / Output
```

---

## 22.1 A simple number pipeline

```python
def read_numbers():
    for number in range(-5, 6):
        yield number


def filter_positive(numbers):
    for number in numbers:
        if number > 0:
            yield number


def square(numbers):
    for number in numbers:
        yield number * number


pipeline = square(filter_positive(read_numbers()))

for value in pipeline:
    print(value)
```

Output:

```text
1
4
9
16
25
```

---

## 22.2 What happens when the pipeline is created?

This line:

```python
pipeline = square(filter_positive(read_numbers()))
```

builds a chain of lazy objects.

At this point, the entire sequence has not been processed.

The work starts when a consumer requests data:

```python
for value in pipeline:
    print(value)
```

---

## 22.3 Pull-based execution

A useful mental model is **pull-based** execution.

The final consumer asks:

```text
"I need the next result."
```

That request travels backward through the pipeline.

For the first result:

```text
consumer asks for next
        ↓
square asks filter_positive for next
        ↓
filter_positive asks read_numbers for next
        ↓
read_numbers produces -5
        ↓
filter rejects -5
        ↓
read_numbers produces -4
        ↓
...
        ↓
read_numbers produces 1
        ↓
filter yields 1
        ↓
square yields 1
        ↓
consumer receives 1
```

The important insight:

> A lazy pipeline often computes only as much as the consumer currently requests.

---

# 23. Generator Composition

Generators naturally feed other generators.

Consider:

```python
def numbers():
    for i in range(10):
        yield i


def even_numbers(values):
    for value in values:
        if value % 2 == 0:
            yield value


def squared(values):
    for value in values:
        yield value * value


pipeline = squared(even_numbers(numbers()))
```

Now:

```python
for value in pipeline:
    print(value)
```

Output:

```text
0
4
16
36
64
```

---

## 23.1 Step-by-step flow

When the consumer asks for the first result:

```text
squared
  ↓ asks even_numbers
even_numbers
  ↓ asks numbers
numbers
  ↓ produces 0
even_numbers
  ↓ accepts 0
squared
  ↓ produces 0
consumer
```

Second result:

```text
numbers → 1
even_numbers → rejects 1
numbers → 2
even_numbers → accepts 2
squared → 4
```

And so on.

This is the core idea of composable lazy processing.

---

# 24. Generator Exhaustion

Consider:

```python
g = (x for x in range(3))

print(list(g))
print(list(g))
```

Output:

```text
[0, 1, 2]
[]
```

Why is the second result empty?

Because `list(g)` consumes the generator.

After the first call:

```text
g
 ↓
0
 ↓
1
 ↓
2
 ↓
StopIteration
```

There are no values left.

---

## 24.1 Generators are normally one-pass

A generator is not a container holding a permanent set of results.

It is an iterator representing a progression of computation.

Once exhausted, it cannot normally be restarted from the beginning.

---

## 24.2 What should you do if you need to process the data twice?

### Option 1: Regenerate it

```python
def make_numbers():
    for number in range(3):
        yield number


for value in make_numbers():
    print(value)

for value in make_numbers():
    print(value)
```

Each call creates a fresh generator.

### Option 2: Materialize intentionally

```python
values = list(make_numbers())

for value in values:
    print(value)

for value in values:
    print(value)
```

### Option 3: Keep a reusable iterable

If the source is already reusable, such as a list or range, iterate over it again.

---

## 24.3 Choosing between the options

Use regeneration when:

- the source is cheap to recreate
- the source is deterministic
- repeatability matters

Materialize when:

- repeated access matters
- the dataset is acceptably sized
- a stable snapshot is useful

Keep a reusable iterable when the underlying object already supports repeated traversal.

---

# 25. Generator Return Values

A generator can use `return` to indicate completion with a value.

Example:

```python
def example():
    yield 1
    return "finished"
```

Now:

```python
g = example()

print(next(g))
```

Output:

```text
1
```

The next call raises `StopIteration`:

```python
try:
    next(g)
except StopIteration as exc:
    print(exc.value)
```

Output:

```text
finished
```

---

## 25.1 Relationship between `return` and `StopIteration.value`

Inside a generator:

```python
return some_value
```

signals completion.

That completion is exposed through the `value` attribute of the resulting `StopIteration` exception when the generator is manually advanced.

This is mainly useful when composing generators or when you deliberately need to inspect the completion value.

It is not necessary for ordinary `for` loops.

---

# 26. `yield from`

Once normal generators are understood, `yield from` becomes straightforward.

Suppose:

```python
def numbers():
    yield 1
    yield 2
    yield 3
```

Without `yield from`:

```python
def combined():
    for value in numbers():
        yield value

    yield 4
```

With `yield from`:

```python
def combined():
    yield from numbers()
    yield 4
```

Usage:

```python
for value in combined():
    print(value)
```

Output:

```text
1
2
3
4
```

---

## 26.1 What does `yield from` mean?

At a simple level:

> **Delegate iteration to another iterable or iterator.**

Instead of writing a loop that repeatedly yields values from another source, you can express the delegation directly.

It improves readability when generator composition becomes nested.

---

## 26.2 `yield from` works with general iterables

For example:

```python
def combined():
    yield from [1, 2]
    yield from range(3, 5)
```

Output:

```text
1
2
3
4
```

---

## 26.3 Advanced note

`yield from` also has semantics for propagating the delegated generator's completion value.

For example, if a delegated generator finishes with a `return` value, `yield from` can make that value available to the outer generator.

That capability is important in advanced generator composition, but ordinary data pipelines usually use `yield from` simply to delegate iteration.

No coroutine semantics are required to understand or use it here.

---

# 27. Generator vs Custom Iterator

| Concern | Custom iterator class | Generator function |
|---|---|---|
| Amount of code | More | Usually less |
| State representation | Explicit attributes | Local variables retained automatically |
| Readability | Useful when state machine is complex | Often simpler for sequential logic |
| Boilerplate | `__iter__`, `__next__`, exhaustion handling | Mostly just `yield` |
| Fine-grained control | High | High, but expressed differently |
| Best for | Rich iterator objects with explicit behavior/configuration | Straightforward lazy production |
| Maintainability | Can be verbose | Often easier to maintain |

---

## 27.1 When a generator is usually simpler

Use a generator when the problem is naturally:

```text
do something
yield value
continue
yield value
...
```

Example:

```python
def positive_numbers(values):
    for value in values:
        if value > 0:
            yield value
```

This is much easier to read than implementing the same behavior with a manual state class.

---

## 27.2 When a custom iterator may be justified

A class may be appropriate when you need:

- explicit state exposed through attributes
- a more complex state machine
- reusable methods beyond iteration
- configurable iterator behavior
- a distinct object abstraction
- behavior that is clearer as a type

A custom iterator should be an engineering decision, not a demonstration of advanced syntax.

---

# 28. Iterable, Iterator, Generator Relationship

A useful conceptual hierarchy is:

```text
Iterable
   |
   +---- list
   +---- tuple
   +---- dict
   +---- set
   +---- range
   +---- string
   +---- file object
   +---- generator
            |
            +---- iterator
```

Be precise about what this means.

A generator object is:

- an iterable
- an iterator

So:

```python
g = (x for x in range(3))

print(iter(g) is g)
```

Output:

```text
True
```

A list is iterable but its list object is not itself the iterator:

```python
values = [1, 2, 3]

print(iter(values) is values)
```

Output:

```text
False
```

The exact iterator is a separate traversal object.

---

## 28.1 Important classification

You can think of the relationship like this:

```text
                 Iterable
               /          \
          re-iterable     iterator
           objects           |
              |              |
          list, tuple        +---- generator
          dict, range
          string, etc.
```

This is a mental model, not a formal class inheritance hierarchy.

The protocol matters more than the visual categories.

---

# 29. One Complete Mental Model: `for`, `iter`, `next`, and Generators

Consider:

```python
def count_up_to(limit):
    current = 1

    while current <= limit:
        yield current
        current += 1


generator = count_up_to(3)

for value in generator:
    print(value)
```

The end-to-end conceptual flow is:

```text
generator object
      ↓
iter(generator)
      ↓
iterator
      ↓
next(...)
      ↓
run generator
      ↓
yield value
      ↓
pause
      ↓
consumer receives value
      ↓
next(...)
      ↓
resume generator
      ↓
yield next value
      ↓
...
      ↓
generator finishes
      ↓
StopIteration
      ↓
for loop stops
```

This is the central mental model for the chapter.

---

# 30. Production Use Cases

## 30.1 Large log files

```python
def read_lines(path):
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            yield line
```

Useful for:

- error searches
- auditing
- operational analysis
- filtering by timestamps or levels
- extracting selected fields

---

## 30.2 CSV processing

Using the standard library:

```python
import csv


def read_csv(path):
    with open(path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            yield row
```

A downstream stage can filter:

```python
def active_rows(rows):
    for row in rows:
        if row.get("status") == "active":
            yield row
```

The reader and filter remain composable.

---

## 30.3 ETL-style transformations

A simple pipeline:

```text
source
  ↓
parse
  ↓
validate
  ↓
filter
  ↓
transform
  ↓
output
```

For example:

```python
def valid_records(records):
    for record in records:
        if "id" in record and "amount" in record:
            yield record


def normalized_records(records):
    for record in records:
        yield {
            "id": str(record["id"]),
            "amount": float(record["amount"]),
        }
```

This design makes each stage small and independently testable.

---

## 30.4 Data validation

A validation generator can yield only valid records:

```python
def valid_numbers(values):
    for value in values:
        if isinstance(value, int) and value >= 0:
            yield value
```

Or it can yield structured validation results if the application needs rejected records too.

The important design question is:

> What should the downstream consumer receive?

Do not throw away useful error information merely because a generator makes filtering easy.

---

## 30.5 Streaming transformations

A transformation can be naturally incremental:

```python
def strip_lines(lines):
    for line in lines:
        yield line.strip()
```

Then:

```python
def non_empty(lines):
    for line in lines:
        if line:
            yield line
```

Composed:

```python
pipeline = non_empty(strip_lines(lines))
```

---

## 30.6 Event-processing concepts

Even without a message broker, the iterator model teaches an important principle:

```text
source produces event
        ↓
consumer requests next event
        ↓
transform
        ↓
filter
        ↓
process
```

Real event systems may be push-based, concurrent, asynchronous, or distributed, so do not assume an iterator is a substitute for a production event platform.

The iteration model is valuable because it teaches **incremental processing and explicit state progression**.

---

## 30.7 AI/ML data preprocessing

Before learning machine-learning frameworks, you can understand the core idea using standard Python:

```python
def normalized_samples(samples):
    for sample in samples:
        cleaned = sample.strip().lower()

        if cleaned:
            yield cleaned
```

This can later support:

- text preprocessing
- evaluation datasets
- document cleaning
- batch preparation

The goal here is not to teach those disciplines. It is to show where lazy iteration becomes an engineering primitive.

---

## 30.8 Evaluation datasets

Suppose you have many test cases:

```python
def evaluation_cases(cases):
    for case in cases:
        if case.get("input") is None:
            continue

        yield case
```

A downstream evaluator can process cases one at a time instead of requiring all transformed cases to be materialized.

---

## 30.9 Document processing

A document ingestion pipeline might conceptually be:

```text
files
  ↓
read
  ↓
parse
  ↓
clean
  ↓
filter
  ↓
emit records
```

Generators are useful when each stage can process one document or chunk at a time.

---

## 30.10 RAG ingestion concepts

At a conceptual level, document ingestion often includes steps such as:

```text
documents
   ↓
read
   ↓
extract text
   ↓
clean
   ↓
split into chunks
   ↓
validate
   ↓
emit records
```

Generators can be useful at each incremental stage.

This chapter does **not** introduce vector databases, embedding APIs, orchestration frameworks, or LLM APIs. The focus is the Python iteration model underneath such pipelines.

---

# 31. Common Mistakes

## Mistake 1: Confusing iterable and iterator

### Why it happens

Both can work with `for`, so they appear interchangeable.

### Incorrect mental model

```python
numbers = [1, 2, 3]

# Thinking the list itself is the traversal state.
next(numbers)
```

This raises:

```text
TypeError
```

### Correct approach

```python
numbers = [1, 2, 3]
iterator = iter(numbers)

print(next(iterator))
```

---

## Mistake 2: Assuming every iterable is reusable

### Why it happens

Lists are reusable, so beginners generalize that behavior.

### Incorrect assumption

```python
g = (x for x in range(3))

print(list(g))
print(list(g))
```

Output:

```text
[0, 1, 2]
[]
```

### Correct approach

Know whether your source is:

- a reusable iterable
- or a one-pass iterator

---

## Mistake 3: Assuming generators store all results

### Why it happens

A generator can eventually produce many results, so it is easy to imagine all of them sitting inside the generator.

### Incorrect mental model

```text
generator = hidden list of all future values
```

### Correct mental model

```text
generator = suspended computation + state
```

Values are produced as the generator advances.

---

## Mistake 4: Iterating over an exhausted generator

### Why it happens

The variable still exists, so it looks like it should still contain data.

### Incorrect expectation

```python
g = (x for x in range(3))

list(g)

# Expecting this to restart it:
list(g)
```

### Correct approach

Regenerate or intentionally materialize:

```python
values = list(x for x in range(3))
```

or:

```python
def make_values():
    yield from range(3)

for value in make_values():
    ...

for value in make_values():
    ...
```

---

## Mistake 5: Forgetting that generators are lazy

### Why it happens

Creating the generator object looks like "running the function."

### Example

```python
def work():
    print("running")
    yield 1

g = work()

print("created")
```

Output:

```text
created
```

The `"running"` message does not appear until:

```python
next(g)
```

or another consumer advances the generator.

---

## Mistake 6: Accidentally consuming an iterator

### Why it happens

Some helper code may call `next()`, `list()`, `tuple()`, `sum()`, or a loop over the iterator.

Example:

```python
iterator = iter([1, 2, 3])

print(sum(iterator))
print(list(iterator))
```

Output:

```text
6
[]
```

The call to `sum()` consumed the iterator.

### Correct approach

Know whether a function **consumes** its input.

Document one-pass behavior where it matters.

---

## Mistake 7: Converting a huge generator to a list unnecessarily

### Problem

```python
values = list(huge_generator())
```

This defeats the main memory benefit of lazy processing.

### Correct approach

Consume incrementally when possible:

```python
for value in huge_generator():
    process(value)
```

Materialize only when the application actually needs a collection.

---

## Mistake 8: Using generators where repeated traversal is required

### Problem

```python
records = (load_record(i) for i in ids)

for record in records:
    validate(record)

for record in records:
    summarize(record)
```

The second loop sees no values because the generator may already be exhausted.

### Correct approach

Either regenerate:

```python
def records():
    for record_id in ids:
        yield load_record(record_id)
```

and call it separately, or materialize if repeated traversal is justified.

---

## Mistake 9: Writing an unnecessarily complicated custom iterator

### Why it happens

The protocol looks more advanced, so a developer may use a class simply to demonstrate the protocol.

### Incorrect style

A multi-method class for a simple sequential transformation.

### Correct approach

Prefer a generator when the problem is naturally sequential:

```python
def doubled(values):
    for value in values:
        yield value * 2
```

Use a custom class when explicit object state and behavior justify it.

---

## Mistake 10: Forgetting invalid state in a custom iterator

### Example

```python
class BadRange:
    def __init__(self, start, stop, step):
        self.current = start
        self.stop = stop
        self.step = step
```

If `step` can be zero, the iterator can never progress.

### Correct approach

Validate invariants early:

```python
if step == 0:
    raise ValueError("step must not be zero")
```

Iterator design is state-machine design. Invalid states must be prevented or handled.

---

## Mistake 11: Misunderstanding `yield`

### Incorrect assumption

```python
yield value
```

means:

> "Return this value and permanently finish."

### Correct mental model

`yield` means:

> "Produce this value and suspend generator execution so it can continue later."

---

## Mistake 12: Assuming generator-based code is automatically faster

### Problem

Replacing every list with a generator may increase overhead or make behavior less convenient.

### Correct approach

Choose based on:

- data size
- access pattern
- repeatability
- latency requirements
- memory constraints
- readability

Measure performance when it matters.

---

## Mistake 13: Assuming generators always use less memory

A generator can still wrap memory-heavy operations:

```python
def misleading(source):
    cached = list(source)
    for item in cached:
        yield item
```

The function is generator-based but still materializes the source.

### Correct approach

Inspect the whole pipeline, not just whether `yield` appears somewhere.

---

## Mistake 14: Assuming generators always reduce total computation

Lazy processing can reduce unnecessary work **if values are not all consumed**.

For example:

```python
next(value for value in expensive_values() if is_match(value))
```

may stop after the first match.

But if you eventually consume every value, a generator does not automatically reduce the number of transformations required.

---

# 32. Debugging Iterators and Generators

Iterator bugs are often state bugs.

## 32.1 Check the type

```python
obj = (x * 2 for x in range(3))

print(type(obj))
```

Typical result:

```text
<class 'generator'>
```

---

## 32.2 Check whether you can obtain an iterator

```python
obj = [1, 2, 3]

iterator = iter(obj)

print(iterator)
```

If `iter(obj)` fails, the object is not suitable for normal iteration.

---

## 32.3 Check whether an object is itself an iterator

A practical protocol check is:

```python
obj = iter([1, 2, 3])

print(iter(obj) is obj)
```

Output:

```text
True
```

You can also inspect the presence of `__next__` when debugging:

```python
print(hasattr(obj, "__next__"))
```

This is not a substitute for understanding the protocol, but it is a useful diagnostic.

---

## 32.4 Check consumption state

You often cannot ask an arbitrary iterator:

> "How many items are left?"

Instead, inspect behavior carefully.

For a small debugging case:

```python
iterator = iter([10, 20, 30])

print(next(iterator))
print(next(iterator))
```

Now the iterator has moved forward.

If you continue consuming it elsewhere, remember that its state is shared.

---

## 32.5 Check whether it is lazy

A simple technique is to add visible side effects:

```python
def source():
    print("source started")

    for value in range(3):
        print("producing", value)
        yield value


g = source()

print("generator created")
print(next(g))
```

Expected output:

```text
generator created
source started
producing 0
0
```

This demonstrates when execution actually happens.

---

## 32.6 Find accidental consumption

Watch for operations that consume an iterator:

```python
list(iterator)
tuple(iterator)
sum(iterator)
for value in iterator:
    ...
```

If a later stage unexpectedly receives no values, inspect earlier consumers first.

---

## 32.7 Debugging checklist

When a pipeline produces no values:

```text
1. Is the source actually iterable?
2. Is the object already an iterator?
3. Has something consumed it?
4. Is the generator condition rejecting everything?
5. Is a filter too strict?
6. Did lazy execution actually start?
7. Did an exception stop the generator?
8. Did you accidentally materialize and then reuse the exhausted iterator?
```

This checklist solves many real-world pipeline bugs.

---

# 33. Testing Iterators and Generators

The goal is not merely to prove that a happy-path example works.

Test the iterator's **state transitions** and **edge cases**.

---

## 33.1 Simple assertion tests

For the `CountUpTo` iterator:

```python
def test_count_up_to_values():
    result = list(CountUpTo(3))
    assert result == [1, 2, 3]
```

Empty input:

```python
def test_count_up_to_empty():
    result = list(CountUpTo(0))
    assert result == []
```

One value:

```python
def test_count_up_to_one():
    result = list(CountUpTo(1))
    assert result == [1]
```

These are ordinary Python test functions using `assert`.

---

## 33.2 Testing exhaustion explicitly

```python
def test_iterator_exhaustion():
    iterator = iter(CountUpTo(2))

    assert next(iterator) == 1
    assert next(iterator) == 2

    try:
        next(iterator)
    except StopIteration:
        pass
    else:
        raise AssertionError("Iterator should be exhausted")
```

This verifies both normal values and protocol completion.

---

## 33.3 Testing repeated iteration

For an iterable such as a list:

```python
def test_reusable_iterable():
    values = [1, 2, 3]

    assert list(values) == [1, 2, 3]
    assert list(values) == [1, 2, 3]
```

For a generator:

```python
def test_generator_is_one_pass():
    generator = (x for x in range(3))

    assert list(generator) == [0, 1, 2]
    assert list(generator) == []
```

---

## 33.4 Testing malformed input

Suppose a parser expects four pipe-delimited fields:

```python
def parse_line(line):
    parts = line.rstrip("\n").split("|", 3)

    if len(parts) != 4:
        return None

    timestamp, level, service, message = parts

    return {
        "timestamp": timestamp,
        "level": level,
        "service": service,
        "message": message,
    }
```

Test valid input:

```python
def test_parse_line_valid():
    record = parse_line(
        "2026-09-24T10:00:00|ERROR|payments|database unavailable"
    )

    assert record["level"] == "ERROR"
    assert record["service"] == "payments"
```

Test malformed input:

```python
def test_parse_line_malformed():
    assert parse_line("broken-line") is None
```

---

## 33.5 Testing large input conceptually

A strong test should not always build a giant list.

You can test with a generator:

```python
def generated_numbers(count):
    for number in range(count):
        yield number
```

Then:

```python
def test_large_streaming_input():
    total = sum(generated_numbers(1_000_000))
    assert total == 499_999_500_000
```

This does not prove every possible memory characteristic of a production system, but it does exercise the code on a large logical input without requiring a pre-built million-item result list.

---

## 33.6 Pytest-style organization

In a project using pytest, these functions can live in a test file:

```python
def test_generator_values():
    values = (x * 2 for x in range(3))
    assert list(values) == [0, 2, 4]
```

The important idea is to test:

- values
- exhaustion
- empty cases
- one-item cases
- repeatability expectations
- malformed inputs
- resource behavior where relevant

Testing the one-pass contract is particularly important for iterator-based APIs.

---

# 34. Performance and Memory Reasoning

Do not guess from syntax.

Reason about the work and measure when necessary.

---

## 34.1 Time complexity

Suppose you transform every item:

```python
def double(values):
    for value in values:
        yield value * 2
```

If there are `n` input items and each transformation is constant-time, the total transformation work is generally:

```text
O(n)
```

Lazy evaluation does not change the fact that consuming all `n` outputs requires processing all `n` inputs.

---

## 34.2 Space complexity

Compare:

```python
values = [x * 2 for x in data]
```

with:

```python
values = (x * 2 for x in data)
```

If `data` is already available and you consume the generator incrementally, the second form may require substantially less additional memory for the transformed results.

The exact memory usage is implementation- and workload-dependent.

Do not reduce the rule to:

> "generator = O(1) memory in every situation."

That is too simplistic.

---

## 34.3 Eager materialization

This:

```python
list(generator)
```

changes the memory profile by forcing the complete remaining sequence into a list.

That may be exactly what you want.

It may also defeat streaming.

Always ask:

> **Do I need all values at once?**

---

## 34.4 Streaming

A streaming design tries to keep only the state necessary to process the current portion of the input.

A simple pipeline:

```python
processed = transform(filter_valid(read_lines(path)))
```

can remain incremental if each function yields instead of materializing the whole input.

---

## 34.5 Measure instead of assuming

For real workloads, use profiling and measurements rather than intuition.

A tiny benchmark can compare two approaches:

```python
from time import perf_counter


def eager():
    return [x * x for x in range(1_000_000)]


def lazy():
    return (x * x for x in range(1_000_000))


start = perf_counter()
eager_result = eager()
eager_time = perf_counter() - start

start = perf_counter()
lazy_result = lazy()
lazy_creation_time = perf_counter() - start

print("eager creation:", eager_time)
print("lazy creation:", lazy_creation_time)
```

Do not interpret this as a universal speed comparison.

The lazy version has not done equivalent work yet.

A fair comparison depends on what you actually consume.

For example:

```python
start = perf_counter()
total = sum(lazy())
lazy_consumed_time = perf_counter() - start

print("lazy full consumption:", lazy_consumed_time)
print("total:", total)
```

This is a better illustration of the need to define what "performance" means.

---

# 35. Production Design Guidance

## Rule 1: Use a normal collection when data is small and repeated access matters

Example:

```python
users = ["alice", "bob", "carol"]

for user in users:
    ...

for user in users:
    ...
```

This is simple and readable.

---

## Rule 2: Use an iterator for one-pass traversal

An iterator is appropriate when the consumer naturally advances through a source exactly once.

Examples:

- consuming a file stream
- traversing a one-shot source
- stateful sequential processing

---

## Rule 3: Use a generator when lazy production is clearer

Example:

```python
def valid_values(values):
    for value in values:
        if value >= 0:
            yield value
```

The generator makes the incremental transformation explicit.

---

## Rule 4: Avoid unnecessary materialization

Do not do:

```python
for value in list(huge_generator()):
    process(value)
```

unless the list itself is needed.

Prefer:

```python
for value in huge_generator():
    process(value)
```

---

## Rule 5: Do not use generators merely because they look advanced

This is a maintainability trap.

Bad engineering:

> "A generator must be better because it uses less memory."

Better engineering:

> "This data is one-pass, large, and processed incrementally, so a generator matches the workload."

---

## Rule 6: Keep generator pipelines readable

Good:

```python
pipeline = square(filter_positive(read_numbers()))
```

Too much nesting can become hard to debug.

When the pipeline gets long, use named intermediate stages:

```python
numbers = read_numbers()
positive = filter_positive(numbers)
squared = square(positive)

for value in squared:
    ...
```

This may use the same lazy mechanics while making debugging easier.

---

## Rule 7: Document one-pass behavior

If a function returns an iterator or generator, readers should understand whether they can traverse it more than once.

For public APIs, documentation such as:

> "Returns a one-pass iterator over matching records."

can prevent subtle bugs.

---

## Rule 8: Test exhaustion and edge cases

A generator can produce the correct first three values and still be wrong at:

- empty input
- invalid state
- final value
- exhaustion
- repeated use

Always test the end of the stream.

---

## Rule 9: Keep I/O boundaries explicit

A generator that reads a file is convenient:

```python
def read_lines(path):
    with open(path, encoding="utf-8") as file:
        yield from file
```

But make resource ownership understandable.

Do not build abstractions that make it unclear:

- when a file is opened
- when it is closed
- whether a generator keeps it open
- who owns the resource lifetime

---

## Rule 10: Separate parsing, transformation, and business logic

Prefer:

```text
lines
  ↓
parse
  ↓
filter
  ↓
transform
  ↓
business processing
```

over one giant generator that handles everything.

This improves:

- testability
- maintainability
- debugging
- reuse

---

## A Compact Decision Guide

| Requirement | Good default |
|---|---|
| Small data, repeated use | Collection such as `list` |
| Need indexing | Collection such as `list` |
| Need all results immediately | Collection / eager result |
| One-pass traversal | Iterator |
| Lazily produce transformed values | Generator |
| Large file, process incrementally | Generator / file iteration |
| Multiple passes over results | Reusable iterable or materialized collection |
| Explicit complex iterator state | Custom iterator class |
| Simple sequential lazy logic | Generator function |
| Streaming pipeline | Chained generators |

The word **default** matters.

The correct choice depends on the workload and the API contract.

---

## Production Mental Models

## 42.1 Data source vs traversal state

This is perhaps the most useful distinction.

```text
DATA SOURCE
    |
    | "What can I iterate over?"
    v
ITERABLE

TRAVERSAL STATE
    |
    | "Where am I now?"
    v
ITERATOR
```

For a list:

```text
list = reusable source
iterator = one traversal through that source
```

For a generator:

```text
generator = source + traversal state + suspended computation
```

This is why generators behave differently from lists.

---

## 42.2 Lazy pipelines are pull-based

Think:

```text
consumer requests one result
            ↓
pipeline computes only what is required
            ↓
result returned
```

This is powerful because the pipeline can be composed without immediately running every stage.

---

## 42.3 Materialization is a design decision

Converting:

```python
iterator
```

into:

```python
list(iterator)
```

is not just a type conversion.

It changes:

- memory behavior
- repeatability
- timing
- lifetime of upstream computation
- availability of random access

Treat materialization as an explicit architectural choice.

---

# 36. Practical Mini-Project: Streaming Log Analyzer

## 36.1 Goal

Build a small program that demonstrates:

- iterable input
- iterator behavior
- generator functions
- lazy processing
- pipeline composition
- file streaming
- malformed input handling
- memory-aware design

The project is intentionally small.

It is not a full production logging system.

---

## 36.2 Log format

Assume each valid line follows:

```text
timestamp|level|service|message
```

Example:

```text
2026-09-24T10:15:00|INFO|api|request received
2026-09-24T10:15:01|ERROR|payments|database unavailable
2026-09-24T10:15:02|WARN|api|slow request
2026-09-24T10:15:03|ERROR|payments|timeout
malformed line
```

---

## 36.3 Stage 1: Read lazily

```python
def read_lines(path):
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            yield line.rstrip("\n")
```

This function does not call `readlines()`.

It yields one line at a time.

---

## 36.4 Stage 2: Parse lines

```python
def parse_lines(lines):
    for line in lines:
        parts = line.split("|", 3)

        if len(parts) != 4:
            continue

        timestamp, level, service, message = parts

        yield {
            "timestamp": timestamp,
            "level": level,
            "service": service,
            "message": message,
        }
```

Malformed lines are skipped.

In a larger production system, you would often also record a metric or structured diagnostic for malformed input.

---

## 36.5 Stage 3: Filter errors

```python
def error_records(records):
    for record in records:
        if record["level"] == "ERROR":
            yield record
```

---

## 36.6 Stage 4: Transform

Suppose we only want the information useful for a summary:

```python
def error_summary_rows(records):
    for record in records:
        yield {
            "service": record["service"],
            "message": record["message"],
        }
```

---

## 36.7 Stage 5: Aggregate

Aggregation is different from simple transformation because it must remember accumulated state.

```python
def summarize(records):
    counts = {}
    total = 0

    for record in records:
        service = record["service"]

        counts[service] = counts.get(service, 0) + 1
        total += 1

    return {
        "total_errors": total,
        "errors_by_service": counts,
    }
```

Notice that `summarize()` returns a normal dictionary.

Why?

Because aggregation produces a final result that needs to be available as a complete object.

This is a useful example of combining lazy stages with eager finalization.

---

## 36.8 Complete pipeline

```python
def analyze_log(path):
    lines = read_lines(path)
    records = parse_lines(lines)
    errors = error_records(records)
    summary_rows = error_summary_rows(errors)

    return summarize(summary_rows)


if __name__ == "__main__":
    summary = analyze_log("application.log")

    print("Total errors:", summary["total_errors"])
    print("Errors by service:", summary["errors_by_service"])
```

A useful mental model is:

```text
application.log
      ↓
read_lines
      ↓
parse_lines
      ↓
error_records
      ↓
error_summary_rows
      ↓
summarize
      ↓
final dictionary
```

---

## 36.9 Where is laziness?

These stages are lazy generators:

```python
read_lines(...)
parse_lines(...)
error_records(...)
error_summary_rows(...)
```

They produce values only when downstream code asks for them.

The final stage:

```python
summarize(...)
```

consumes those values and builds the final summary dictionary.

---

## 36.10 Why memory usage can stay manageable

The file is not first converted to a list of all lines.

Instead:

```text
read one line
  ↓
parse one line
  ↓
filter one record
  ↓
transform one record
  ↓
update counts
  ↓
read next line
```

The exact memory footprint depends on implementation details and the amount of state held by each stage, but the design avoids intentionally materializing the full input and full transformed record stream.

---

## 36.11 Create a small test file

Example `application.log` content:

```text
2026-09-24T10:15:00|INFO|api|request received
2026-09-24T10:15:01|ERROR|payments|database unavailable
2026-09-24T10:15:02|WARN|api|slow request
2026-09-24T10:15:03|ERROR|payments|timeout
2026-09-24T10:15:04|ERROR|api|dependency failed
malformed line
```

Expected summary:

```text
Total errors: 3
Errors by service: {'payments': 2, 'api': 1}
```

The dictionary order shown above reflects the input order in modern Python, but code should generally treat a mapping as a mapping unless ordering is part of the contract.

---

## 36.12 What this project teaches

This small project connects the whole chapter:

```text
File object
   ↓
iterable + iterator behavior
   ↓
generator wrapper
   ↓
lazy parser
   ↓
lazy filter
   ↓
lazy transformation
   ↓
eager aggregation
```

This is a strong foundational pattern for later engineering work.

---

# 37. Knowledge Check

Try answering these without looking back.

## 37.1 Basic

1. What is iteration?
2. What is an iterable?
3. What does `iter()` do?
4. What is an iterator?
5. What does `next()` do?
6. What is `StopIteration`?
7. Why can a `for` loop work with a list?
8. Why can a `for` loop work with a file object?
9. What does `iter(iterator) is iterator` mean?
10. What does `yield` do at a high level?

### Checkpoint

You should be able to explain this diagram in your own words:

```text
iterable
   ↓
iter()
   ↓
iterator
   ↓
next()
   ↓
value
   ↓
next()
   ↓
value
   ↓
StopIteration
```

---

## 37.2 Intermediate

1. Why is a list iterable but not normally its own iterator?
2. Why is an iterator consumed as it is traversed?
3. Why can two calls to `iter(list_object)` produce independent iterator objects?
4. Why does a generator usually not restart after exhaustion?
5. What is the difference between a list comprehension and a generator expression?
6. Why are generators useful for large files?
7. What happens when `list(generator)` is called?
8. Why can lazy execution make debugging more subtle?
9. Why does `range(1_000_000)` behave differently from a list of one million integers in terms of representation and storage?
10. Why is it incorrect to say that generators are always faster?

---

## 37.3 Advanced

1. Explain the iterator protocol in terms of `__iter__()`, `__next__()`, and `StopIteration`.
2. Explain how a `for` loop conceptually drives an iterator.
3. Explain generator suspension and resumption.
4. Explain what generator state means.
5. Explain how a generator pipeline executes when the final consumer requests one value.
6. Explain the difference between peak memory usage and total computation.
7. Explain when a generator is inappropriate.
8. Explain why a function containing `yield` behaves differently from an ordinary function.
9. Explain how `yield from` simplifies generator composition.
10. Explain why an iterator's one-pass behavior can become an API design concern.

---

## Review Checkpoints

## Checkpoint A — Iterable

You should now be able to explain:

```python
numbers = [1, 2, 3]
iterator = iter(numbers)
```

without simply saying "it converts a list into an iterator."

Explain:

- what the list is
- what the iterator is
- who owns traversal state
- why the objects are separate

---

## Checkpoint B — Iterator

You should be able to explain:

```python
next(iterator)
```

as a protocol operation:

```text
ask iterator for next value
         ↓
receive value
```

and understand what happens when no value remains.

---

## Checkpoint C — `for`

You should be able to explain why:

```python
for x in source:
    ...
```

works for many unrelated Python types.

---

## Checkpoint D — Generator

You should be able to explain why:

```python
g = count_up_to(3)
```

does not produce `1`, `2`, and `3` immediately.

---

## Checkpoint E — Lazy pipeline

You should be able to trace:

```python
pipeline = square(filter_positive(read_numbers()))
```

from the final consumer backward to the original source.

---

## Checkpoint F — Production choice

Given a problem, you should be able to justify one of:

```text
list
iterator
generator
```

using engineering requirements rather than syntax preference.

---

## Coding Challenges

Do not look for the final solution immediately. Design the state and protocol first.

## Challenge 1 — Manual iteration

Write code that:

1. creates an iterator from a list
2. calls `next()` repeatedly
3. handles `StopIteration`
4. prints every value

### Constraint

Do not use a `for` loop for the actual traversal.

---

## Challenge 2 — Custom counter

Implement:

```python
CountByStep(start, stop, step)
```

Requirements:

- support positive steps
- support negative steps
- reject `step == 0`
- raise `StopIteration` when complete

---

## Challenge 3 — Even-number generator

Write:

```python
def even_numbers(values):
    ...
```

Requirements:

- accept any iterable
- yield only even integers
- do not create an output list

---

## Challenge 4 — Chunk generator

Write:

```python
def chunks(values, size):
    ...
```

Requirements:

- accept any iterable
- produce lists of at most `size`
- the final chunk may be smaller
- reject non-positive sizes
- process the input incrementally

### Hint

Think about an underlying iterator:

```python
iterator = iter(values)
```

---

## Challenge 5 — Lazy log filter

Write a generator:

```python
def error_lines(lines):
    ...
```

Requirements:

- accept any iterable of strings
- yield only lines containing `"ERROR"`
- do not materialize the complete input

---

## Challenge 6 — Parsing pipeline

Build three stages:

```text
raw lines
   ↓
parse
   ↓
filter
   ↓
transform
```

Each stage should be a generator.

Then consume the final pipeline with a `for` loop.

---

## Challenge 7 — Exhaustion bug

Given:

```python
records = (x for x in range(5))

first = list(records)
second = list(records)
```

Explain why `second` is empty.

Then redesign the code so that the logical data can be processed twice **without** accidentally reusing the exhausted generator.

---

## Challenge 8 — Streaming log analyzer extension

Extend the mini-project so that it also:

- counts malformed lines
- reports error counts by service
- yields error records lazily
- keeps the final summary eager

Design the interface carefully so that the malformed-line count does not require loading the whole file into memory.

---

# 38. Interview and Architecture Questions

These questions are about reasoning, not memorizing definitions.

## 39.1 What is the difference between an iterable and an iterator?

**Expected reasoning direction:** Explain the roles separately. An iterable is a source from which an iterator can be obtained; an iterator owns traversal state and implements the next-value mechanism.

---

## 39.2 How does a Python `for` loop work internally?

**Expected reasoning direction:** Explain the conceptual sequence:

```text
iter(source)
   ↓
next(iterator)
   ↓
loop body
   ↓
repeat
   ↓
StopIteration
   ↓
loop ends
```

Be explicit that this is a conceptual model rather than a literal source-code rewrite.

---

## 39.3 What is the iterator protocol?

**Expected reasoning direction:** Discuss `__iter__()`, `__next__()`, and `StopIteration`, and explain the relationship between iterable objects and iterators.

---

## 39.4 What is `StopIteration`?

**Expected reasoning direction:** Describe it as the standard protocol signal that an iterator has no more values, and explain why `for` normally hides it.

---

## 39.5 What is a generator?

**Expected reasoning direction:** Explain that a generator is an iterator created conveniently by a generator function or generator expression, with lazy production and retained execution state.

---

## 39.6 What does `yield` do?

**Expected reasoning direction:** Say that it produces a value and suspends generator execution so it can resume later.

---

## 39.7 What is lazy evaluation?

**Expected reasoning direction:** Explain that computation is deferred until the consumer requests the value, rather than materializing every result immediately.

---

## 39.8 Generator expression vs list comprehension?

**Expected reasoning direction:** Compare:

```python
[x * 2 for x in values]
```

with:

```python
(x * 2 for x in values)
```

Discuss eager materialization, lazy production, repeatability, memory, and access patterns.

---

## 39.9 When would you use a generator in production?

**Expected reasoning direction:** Look for workloads involving:

- one-pass processing
- large inputs
- streaming transformations
- memory constraints
- composable stages

Then mention the counter-considerations:

- repeated traversal
- indexing
- debugging
- need for a stable materialized result

---

## 39.10 What happens when a generator is exhausted?

**Expected reasoning direction:** Explain that iteration eventually terminates with `StopIteration`; subsequent advancement remains exhausted rather than restarting the generator.

---

## 39.11 How would you process a 100 GB log file?

**Expected reasoning direction:** Start with streaming rather than full materialization:

```python
with open("application.log", encoding="utf-8") as file:
    for line in file:
        process(line)
```

Then consider:

- parsing
- filtering
- transformation
- aggregation
- malformed data
- resource ownership
- backpressure or downstream constraints in more advanced systems

For this chapter, keep the implementation based on Python's standard iteration mechanisms.

---

## 39.12 How would you design a memory-efficient data pipeline?

**Expected reasoning direction:** Separate stages and keep them lazy where incremental processing is possible:

```text
read → parse → validate → filter → transform → aggregate
```

Avoid unnecessary intermediate lists.

But identify where eager materialization is actually useful.

---

## 39.13 When would you deliberately materialize a generator?

**Expected reasoning direction:** Mention repeated traversal, indexing, sorting, stable snapshots, immediate length, or when the dataset is known to be small enough.

---

## 39.14 What are the trade-offs between generators and collections?

**Expected reasoning direction:** Compare:

- memory
- latency
- repeatability
- indexing
- debugging
- composability
- total computation
- resource lifetime

---

## 39.15 How would you debug a pipeline that unexpectedly produces no values?

**Expected reasoning direction:**

```text
Check source
  ↓
Check whether an iterator is already exhausted
  ↓
Check filters
  ↓
Check generator conditions
  ↓
Check whether lazy execution started
  ↓
Check earlier consumers
```

Demonstrate how `type()`, `iter()`, `next()`, and small diagnostic prints can reveal the state.

---

# 39. Final Summary / Mental Model

## Iterable

```text
Iterable
   ↓
Can produce an iterator
```

Examples:

```text
list
tuple
string
dict
set
range
file
generator
```

---

## Iterator

```text
Iterator
   ↓
Produces one value at a time
and remembers traversal state
```

Core operation:

```python
next(iterator)
```

---

## Generator

```text
Generator
   ↓
A convenient way to create iterators lazily
```

Created by:

- generator functions
- generator expressions

---

## `yield`

```text
yield
   ↓
Produce a value
   ↓
Suspend execution
   ↓
Retain state
```

---

## `next()`

```text
next()
   ↓
Resume the iterator/generator
   ↓
Produce the next value
```

---

## `StopIteration`

```text
StopIteration
   ↓
Signals that iteration is finished
```

`for` loops normally handle this signal for you.

---

## One complete model

```text
                 ITERABLE
                    |
                    | iter(...)
                    v
                 ITERATOR
                    |
                    | next(...)
                    v
                  VALUE
                    |
                    | next(...)
                    v
                  VALUE
                    |
                    | ...
                    v
             StopIteration


              GENERATOR
                    |
                    | is an iterator
                    v
                 next(...)
                    |
                    v
                  yield
                    |
                    v
               suspend state
                    |
                    v
                 next(...)
                    |
                    v
                 resume
                    |
                    v
                 yield...
```

---

## The Production Principle

The most important principle from this chapter is:

> **Use lazy iteration when data can be processed incrementally and retaining the entire dataset in memory is unnecessary.**

But pair that principle with a second one:

> **Do not use laziness automatically; choose it when the workload, access pattern, and API contract actually benefit from it.**

Good Python engineering means understanding both sides:

```text
LAZY
  + lower peak memory for many streaming workloads
  + early results
  + composable pipelines
  + deferred work

EAGER
  + simple inspection
  + repeated traversal
  + indexing
  + stable materialized results
  + straightforward debugging
```

The engineering decision is not:

> "Generators are better."

It is:

> **Choose the representation that matches the data, lifetime, access pattern, memory constraints, and behavior your program actually requires.**

---

## Final Mastery Checklist

Before moving beyond this topic, make sure you can explain and demonstrate all of the following without relying on memorized definitions:

- [ ] What iteration means.
- [ ] What an iterable is.
- [ ] What an iterator is.
- [ ] Iterable vs collection vs sequence.
- [ ] `iter()`.
- [ ] `next()`.
- [ ] `__iter__()`.
- [ ] `__next__()`.
- [ ] `StopIteration`.
- [ ] Why `for` works across many Python types.
- [ ] Why an iterable can often be traversed repeatedly.
- [ ] Why an iterator is generally one-pass.
- [ ] Why `iter(iterator) is iterator` generally holds.
- [ ] Custom iterator design.
- [ ] Generator functions.
- [ ] `yield`.
- [ ] Generator state.
- [ ] Generator suspension and resumption.
- [ ] Generator expressions.
- [ ] Eager vs lazy evaluation.
- [ ] Memory trade-offs.
- [ ] Large-file streaming.
- [ ] Generator pipelines.
- [ ] Generator composition.
- [ ] Generator exhaustion.
- [ ] Generator return values.
- [ ] `yield from`.
- [ ] Generator vs custom iterator.
- [ ] Debugging accidental iterator consumption.
- [ ] Testing exhaustion and edge cases.
- [ ] Reasoning about time and space complexity.
- [ ] Choosing list vs iterator vs generator.
- [ ] Designing clear, maintainable lazy pipelines.

If you can teach these concepts to another beginner using your own examples and can implement the mini-project without copying the solution, you have a solid foundation for production-oriented Python iteration.
