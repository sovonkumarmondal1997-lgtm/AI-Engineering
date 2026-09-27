# Mutability and Immutability

## Why mutability matters

Across every collection lesson in this module, one idea kept resurfacing
in a slightly different costume: strings cannot be changed in place, but
lists can; tuples are locked, but dictionaries and sets are not; two
variable names can secretly point at the very same list, so changing one
changes what the other shows too. This lesson pulls all of that together
into one clear, unified picture. Understanding **mutability** — whether a
value can be changed in place, or must instead be replaced — is one of the
single most important ideas in Python, because it explains *why* so many
beginner bugs happen: a variable that "changed on its own," a copy that
was not really a copy, a function's data quietly altered from somewhere
else entirely.

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain that a variable is a name referring to an object, using the
  "labels on boxes" mental model.
- Classify Python's common built-in types as mutable or immutable.
- Explain, with a clear example, the difference between reassigning a
  variable and mutating the object it refers to.
- Explain the difference between `==` (equality) and `is` (identity), and
  state the rule for when `is` is actually appropriate.
- Use `.copy()`, slicing, and type constructors to make a real copy
  instead of an alias, and explain why these are all *shallow* copies.
- Explain, with a runnable example, why a tuple can still "change" if it
  contains a mutable list.
- Explain the difference in behavior between `+=` on a list and `+=` on a
  tuple or string.
- Explain hashability at a beginner level, including why a tuple
  containing a list cannot be used as a dictionary key or set member.
- Apply safe habits that prevent accidental, shared mutation in your own
  code.

## Prerequisites

This lesson assumes you have completed every earlier lesson in this
module, and draws directly on:

- [Values, Expressions, Statements, and Variables](../01-Computational-Thinking-and-Program-Design/02-values-expressions-statements-and-variables.md) —
  the original "label on a box" introduction to assignment, reassignment,
  and mutation.
- [Strings: Indexing, Slicing, and Formatting](04-strings-indexing-slicing-and-formatting.md) —
  your first encounter with immutability.
- [Lists: Mutation, Copying, and Aliasing](05-lists-mutation-copying-and-aliasing.md) —
  aliasing, copying, and shallow copies, first taught in full there.
- [Tuples and Unpacking](06-tuples-and-unpacking.md),
  [Dictionaries and Lookups](07-dictionaries-and-lookups.md), and
  [Sets and Unique Values](08-sets-and-unique-values.md) — each type's own
  mutability rules and aliasing behavior.

## Key terms

| Term | Plain-English definition |
|---|---|
| **Object** | A piece of data that exists somewhere in memory while your program runs — every value (a number, a string, a list) is an object. |
| **Reference** | The connection a variable name has to an object; a variable does not "contain" its object, it refers to it. |
| **Mutable** | Able to be changed in place, without becoming a different object. |
| **Immutable** | Unable to be changed in place; any "change" actually produces a different, new object. |
| **Alias** | A second variable name referring to the exact same object as another name. |
| **Shallow copy** | A copy of a collection's own structure only; any mutable objects nested inside it are still shared with the original. |
| **Equality (`==`)** | Whether two objects have the same *value*. |
| **Identity (`is`)** | Whether two names refer to the exact same *object*. |
| **`id()`** | A built-in function that returns a number identifying an object's identity, useful only for comparison, never as a meaningful value on its own. |
| **Hashable** | Able to be used as a dictionary key or set member; roughly, "immutable, and made only of other hashable values." |

## Step-by-step explanation

### 1. Objects and references

Every value in Python — `5`, `"Ada"`, `[1, 2, 3]` — is an **object**: a
piece of data that exists somewhere while your program runs. A variable
does not "hold" that object the way a box holds an item; a variable is a
**reference** — a name pointing at an object, like a label stuck onto a
box. Multiple labels can point at the very same box:

```python
first_name = "Ada"
also_first_name = first_name

print(first_name)        # Ada
print(also_first_name)    # Ada
```

Here, `also_first_name = first_name` does not copy `"Ada"` into a new,
separate piece of data — it simply sticks a second label,
`also_first_name`, onto the exact same object `first_name` already points
at. This is called **aliasing**.

**Reassignment** peels a label off one object and sticks it onto a
different one, leaving the first object, and any other labels still on
it, completely untouched:

```python
first_name = "Ada"
also_first_name = first_name

first_name = "Grace"

print(first_name)        # Grace
print(also_first_name)    # Ada  — unaffected
```

`first_name` now points at a brand-new object, `"Grace"`. `also_first_name`
was never touched by this line at all — it still points at the original
`"Ada"` object, exactly as before.

### 2. Mutable versus immutable objects

A **mutable** object can be changed in place — its contents can be
altered without it becoming a different object. An **immutable** object
cannot: any apparent "change" actually builds and returns a brand-new
object, leaving the original completely alone.

| Immutable | Mutable |
|---|---|
| `int`, `float`, `bool` | `list` |
| `str` | `dict` |
| `tuple` | `set` |
| `frozenset` | |
| `None` | |

You have already met every one of these types across this module's
lessons: strings, tuples, and `frozenset` (from the
[strings](04-strings-indexing-slicing-and-formatting.md),
[tuples](06-tuples-and-unpacking.md), and
[sets](08-sets-and-unique-values.md) lessons) cannot be changed in place;
lists, dictionaries, and sets can. Numbers, booleans, and `None`
(from
[Variables, Basic Types, and None](02-variables-basic-types-and-none.md))
are immutable too — `age = age + 1` never changes the number `age`
originally pointed at, it makes `age` point at a new number instead,
exactly like the reassignment in Section 1.

### 3. Reassignment versus mutation, side by side

This is the single most important comparison in this lesson. Two
variables point at the same list. In one version, the *second name* is
**reassigned**; in the other, the *shared list* is **mutated**.

**Reassignment — the first name is unaffected:**

```python
list_a = [1, 2, 3]
list_b = list_a          # alias

list_b = [9, 9, 9]         # REASSIGNMENT: list_b now points elsewhere

print(list_a)   # [1, 2, 3]   — unaffected
print(list_b)   # [9, 9, 9]
```

`list_b = [9, 9, 9]` peels the `list_b` label off the original list and
sticks it onto a brand-new one. `list_a` still points at the original
list, which was never touched.

**Mutation — both names see the change:**

```python
list_a = [1, 2, 3]
list_b = list_a          # alias

list_b.append(4)          # MUTATION: changes the shared list in place

print(list_a)   # [1, 2, 3, 4]   — changed too!
print(list_b)   # [1, 2, 3, 4]
```

`list_b.append(4)` does not touch the `list_b` label at all — it reaches
*inside* the one list both names point at and changes its contents.
Because `list_a` and `list_b` are two labels on the very same object,
printing `list_a` shows the change too, even though the code never wrote
`list_a.append(...)`.

### 4. Equality versus identity

`==` and `is` ask two genuinely different questions. `==` asks **"do
these have the same value?"**; `is` asks **"are these the exact same
object?"**:

```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(a == b)   # True   — same value
print(a is b)   # False  — two separate objects that happen to match
print(a is c)   # True   — literally the same object (an alias)
```

`a` and `b` are two completely separate lists that happen to contain the
same values — equal, but not identical. `c = a` makes `c` an alias for
`a`, so `a is c` is `True`: they are not just equal, they are the *same*
object.

**Use `is` mainly for `None` checks**, exactly as covered in
[Operators and Precedence](03-operators-and-precedence.md):

```python
value = None
print(value is None)   # True
```

This works reliably because Python guarantees there is only ever one
`None` object in your entire program.

**Why beginners should avoid `is` for normal text or number comparison:**
it can appear to "work" by coincidence, which is more dangerous than an
obvious failure. CPython (the standard Python implementation) happens to
reuse the same small number objects for performance:

```python
p = 5
q = 5
print(p == q)   # True
print(p is q)   # True   — looks like it "works"... but don't rely on this
```

That coincidence disappears the moment a value is computed at runtime
rather than typed as a literal, even though the *value* is still equal:

```python
x = 1000
y = int("1000")
print(x == y)   # True
print(x is y)   # False  — two separate objects, despite equal values

a = "hello"
b = "".join(["h", "e", "l", "l", "o"])
print(a == b)   # True
print(a is b)   # False  — same story for strings
```

The lesson here is not "large numbers behave differently from small
numbers" — it is that `is` for ordinary values depends on internal
implementation details you should never rely on. Always use `==` to
compare values; reserve `is` for `None`.

**`id()` as an optional observation tool:** `id(...)` returns a number
identifying an object's identity — two names have `is`-equal objects
exactly when `id()` gives the same number for both. `id()` is useful only
for this kind of comparison; the actual number it returns has no meaning
of its own and can differ every time you run your program. This lesson
uses it only to *observe* behavior, never as a value to print or rely on
directly, and Section 6 uses it this way.

### 5. Copying mutable objects

As shown throughout this module's lessons, plain assignment
(`second = first`) never copies a mutable object — it only aliases it.
Three tools build a genuine, independent copy instead: the `.copy()`
method, slicing an entire sequence with `[:]`, and passing the original
into its own type's constructor:

```python
original = [1, 2, 3]

alias = original
copy_via_method = original.copy()
copy_via_slice = original[:]
copy_via_constructor = list(original)

alias.append(99)

print(original)              # [1, 2, 3, 99]   — changed; alias shares the object
print(copy_via_method)        # [1, 2, 3]        — unaffected
print(copy_via_slice)          # [1, 2, 3]
print(copy_via_constructor)    # [1, 2, 3]
```

Only `alias`, sharing the same object, sees the mutation. All three real
copies remain exactly as they were.

**These are all *shallow* copies.** As covered in full in
[Lists: Mutation, Copying, and Aliasing](05-lists-mutation-copying-and-aliasing.md),
a shallow copy duplicates only the *outer* collection — any mutable object
nested inside it is still shared between the original and the copy:

```python
matrix = [[1, 2], [3, 4]]
shallow = matrix.copy()

shallow[0].append(99)
print(matrix)     # [[1, 2, 99], [3, 4]]   — changed too!
print(shallow)     # [[1, 2, 99], [3, 4]]
```

`shallow[0]` is the very same inner list `matrix[0]` refers to — only the
outer list was truly duplicated. Revisit the lists lesson for the full
treatment of this behavior, including how far it extends and where it
does not apply.

**Deep copying, briefly:** for the rarer situations where every nested
object must be independently copied too, Python provides a tool for that
— but it is a later-module concern, not something this lesson requires
you to use. For now, just know the limitation exists: a shallow copy
protects the outer collection, not what is nested inside it.

### 6. Important edge cases

**A tuple can contain a mutable list, and that list can still change.**
Immutability applies to the tuple's own *slots* — which object each
position refers to — not to whatever those objects are capable of doing
internally:

```python
record = ("Ada", [90, 85, 92])

record[1].append(100)
print(record)   # ('Ada', [90, 85, 92, 100])

record[0] = "Grace"
```

```text
TypeError: 'tuple' object does not support item assignment
```

`record[1].append(100)` never tries to change what `record` refers to at
position `1` — it reaches *inside* the list already stored there and
mutates that list, which is perfectly legal. `record[0] = "Grace"` tries
to make position `0` refer to a *different* object entirely, which the
tuple correctly refuses. The tuple itself never changed in either case;
only the mutable object living inside it did.

**`+=` behaves differently depending on the type.** On a **mutable**
list, `+=` mutates the existing list in place; on an **immutable** tuple
or string, `+=` must build a brand-new object, since the original cannot
be changed. `id()` reveals the difference directly:

```python
numbers = [1, 2, 3]
original_id = id(numbers)
numbers += [4]

print(numbers)                    # [1, 2, 3, 4]
print(id(numbers) == original_id)  # True   — same object, mutated in place
```

```python
coordinates = (1, 2, 3)
original_id = id(coordinates)
coordinates += (4,)

print(coordinates)                     # (1, 2, 3, 4)
print(id(coordinates) == original_id)   # False  — a brand-new tuple was created
```

Both examples *look* identical on the surface — `something += more_stuff`
— but they do fundamentally different things underneath, entirely because
of each type's mutability. This matters most when another name is
aliasing the same object: `+=` on a list is visible through every alias;
`+=` on a tuple or string only ever affects the one name being reassigned.

**Hashability, at a beginner level:** as you saw in the
[dictionaries](07-dictionaries-and-lookups.md) and
[sets](08-sets-and-unique-values.md) lessons, dictionary keys and set
members must be **hashable** — in practice, immutable. Since tuples are
immutable, they are *usually* hashable and safe to use as keys — but only
if **every value inside them** is also hashable:

```python
valid_key = (1, 2)
data = {valid_key: "point"}
print(data)   # {(1, 2): 'point'}
```

```python
invalid_key = (1, [2, 3])
bad_data = {invalid_key: "point"}
```

```text
TypeError: cannot use 'tuple' as a dict key (unhashable type: 'list')
```

The outer tuple being immutable is not enough — `invalid_key` contains a
mutable list, so Python correctly refuses to use it as a key at all,
tracing the failure straight back to that one unhashable list.

### 7. Safe engineering habits

A short set of habits prevents almost every mutability-related bug:

- **Copy data intentionally before changing it**, whenever you did not
  create the data yourself and are not certain you are the only one using
  it — use `.copy()`, `[:]`, or a type constructor, as shown in Section 5.
- **Avoid changing shared input unexpectedly.** If a list, dictionary, or
  set was handed to you (from elsewhere in a larger program, once you
  reach that stage), assume something else might still be using it unless
  you know otherwise.
- **Use clear variable names when something is intended as a copy** —
  `scores_copy = scores.copy()` communicates intent far better than a
  second name that looks just like the first.
- **Deliberately test with two names pointing at the same object**, on
  purpose, while learning: create an alias, mutate through one name, and
  confirm what the other shows. This is exactly what this lesson's
  examples have done throughout.
- **Inspect behavior instead of guessing.** When in doubt about whether
  something is shared, print both names, compare with `==` and `is`, or
  check `id()` — do not assume.

## Examples

### Example 1 — A shared shopping cart: alias versus reassignment

```python
cart_a = ["apples", "bread"]
cart_b = cart_a

cart_b.append("milk")
print(cart_a)   # ['apples', 'bread', 'milk']
print(cart_b)   # ['apples', 'bread', 'milk']

cart_b = ["eggs"]
print(cart_a)   # ['apples', 'bread', 'milk']   — unaffected this time
print(cart_b)   # ['eggs']
```

**Plain-English explanation:**

- `cart_b = cart_a` makes `cart_b` an alias — a second label on the exact
  same list `cart_a` points at.
- `cart_b.append("milk")` mutates that one shared list. Since both names
  point at it, `cart_a` shows the new item too, even though the code
  never wrote `cart_a.append(...)` — this is the mutation half of the
  Section 3 comparison, shown here with a realistic shopping cart.
- `cart_b = ["eggs"]` is a reassignment: `cart_b` now points at a
  brand-new, unrelated list. `cart_a` is completely unaffected, still
  showing the three-item list from before — this is the reassignment half
  of the same comparison.
- Tracing through both halves side by side in one realistic scenario is
  exactly how to build reliable intuition for which situation you are in.

### Example 2 — A student record: tuple, list, and hashability together

```python
student = ("Ada", [90, 85, 92])

student[1].append(78)
print(student)   # ('Ada', [90, 85, 92, 78])

average = sum(student[1]) / len(student[1])
print(f"Average: {average:.1f}")

roster = {}
roster[student] = "enrolled"
```

**Plain-English explanation:**

- `student` is a tuple pairing a name with a *mutable* list of scores —
  exactly the Section 6 edge case, chosen deliberately as a record type
  here.
- `student[1].append(78)` legally mutates the inner scores list; the
  tuple's own two slots never change, only what the second slot's list
  contains. Printing confirms the new score is included.
- `average = sum(student[1]) / len(student[1])` computes the updated
  average directly from the mutated list, printing `Average: 86.2`.
- `roster[student] = "enrolled"` then tries to use the whole tuple as a
  dictionary key — but because `student` contains a list, it is not
  hashable, so this raises:
  ```text
  TypeError: cannot use 'tuple' as a dict key (unhashable type: 'list')
  ```
- This example shows the real, practical consequence of Section 6's
  hashability rule: a record shaped like this one is genuinely useful for
  grouping related, changeable data, but that very same mutability is
  exactly what makes it unsuitable as a dictionary key.

### Example 3 — Curving scores safely: copy-then-mutate versus build-new

```python
original_scores = [55, 82, 91, 40]

curved_via_copy = original_scores.copy()
for position in range(len(curved_via_copy)):
    curved_via_copy[position] += 5

curved_via_build = []
for score in original_scores:
    curved_via_build.append(score + 5)

print(original_scores)    # [55, 82, 91, 40]   — untouched by either approach
print(curved_via_copy)     # [60, 87, 96, 45]
print(curved_via_build)    # [60, 87, 96, 45]
```

**Plain-English explanation:**

- `original_scores` represents data that should not be silently changed —
  the "safe engineering habits" scenario from Section 7.
- The first approach makes a real copy with `.copy()`, then mutates *that
  copy* in place, position by position, using `range(len(...))` to reach
  each index — the original is protected because the mutation only ever
  touches the independent copy.
- The second approach never copies anything at all: it builds a brand-new
  empty list and `.append()`s a freshly computed value for every original
  score, never touching `original_scores` in the first place.
- Both approaches produce the same correct, curved result while leaving
  `original_scores` completely untouched — proof that there is more than
  one valid way to honor the "do not mutate shared input" habit: copy
  first and mutate the copy, or build a new result from scratch. Either
  is safe; mutating the original directly would not be.

## Common beginner mistakes

- **Assuming `second = first` creates an independent copy.** It creates an
  alias — a second name for the same object. Use `.copy()`, `[:]`, or a
  type constructor for a real copy.
- **Mutating a list through one variable and being surprised another
  variable changed too.** If both names refer to the same object, this is
  expected, not a bug — check with `is` or `id()` if you are ever unsure
  whether two names are aliases.
- **Expecting `.copy()` to deeply copy nested lists or dictionaries.** As
  Section 5 showed, `.copy()` is shallow: nested mutable objects are still
  shared between the original and the copy.
- **Using `is` instead of `==`.** `is` checks identity, not value equality,
  and can look like it "works" for small numbers purely by coincidence.
  Use `==` for values; use `is` only for `None`.
- **Assuming an immutable outer tuple means everything inside it is also
  immutable.** As Section 6 showed, a tuple containing a list still allows
  that list to be mutated freely.
- **Accidentally using a mutable value where a hashable dictionary key or
  set member is required.** A tuple is hashable only if every value inside
  it is also hashable — a tuple containing so much as one list breaks
  this, even though the outer tuple itself is immutable.

## Try it yourself

Do not look up full solutions. Predict the output before running each one.

1. Create a list, assign it to a second name, and predict what happens if
   you (a) mutate it through the second name, versus (b) reassign the
   second name to a brand-new list. Verify both with `print`.
2. Given `a = "python"` and `b = "python"`, predict what `a == b` and
   `a is b` will show, then check. Now build a second string at runtime
   with `"".join(["p", "y", "t", "h", "o", "n"])`, compare it to `a` the
   same way, and explain any difference you see.
3. Create a dictionary, alias it with a second name, and use `is` to
   confirm both names refer to the same object. Then create a real copy
   with `.copy()` and confirm, with `is`, that the copy is a different
   object.
4. Create a small nested structure, such as `data = {"scores": [10, 20]}`,
   make a shallow copy with `.copy()`, mutate the inner list through the
   copy, and confirm — by printing the original — that the change is
   visible there too.
5. Create a tuple containing one mutable list, mutate the list, and then
   try to use the tuple as a dictionary key. Predict the error before you
   see it.
6. Write a short piece of code that takes a list you are given (call it
   `given_list`) and produces a new, independent, sorted version of it
   without changing `given_list` at all. Confirm with `print` that
   `given_list` is unchanged afterward.

## Summary

- A variable is a **reference** — a label pointing at an **object** — not
  a box that owns its value; several names can label the same object at
  once (**aliasing**).
- **Mutable** objects (`list`, `dict`, `set`) can be changed in place;
  **immutable** objects (`int`, `float`, `bool`, `str`, `tuple`,
  `frozenset`, `None`) cannot, and any "change" produces a new object.
- **Reassignment** points one name at a different object and never
  affects any other name; **mutation** changes the shared object itself
  and is visible through every name that refers to it.
- `==` compares **values**; `is` compares **identity**. Use `==` for
  ordinary comparisons, and reserve `is` for checking `None`.
- `.copy()`, `[:]`, and type constructors all build genuine, independent,
  but **shallow** copies — nested mutable objects are still shared.
- A tuple's immutability only covers its own slots; a list stored inside
  a tuple can still be mutated. `+=` mutates a list in place but must
  build a new object for a tuple or string.
- A value is **hashable** (usable as a dictionary key or set member) only
  if it is immutable *and* everything inside it is also hashable.

## Completion checklist

- [ ] I can explain, in my own words, the "labels on boxes" model of
      variables and objects.
- [ ] I can correctly classify at least five common types as mutable or
      immutable.
- [ ] I can demonstrate the difference between reassignment and mutation
      with a small example of my own.
- [ ] I can explain the difference between `==` and `is`, and state when
      `is` is actually appropriate.
- [ ] I can make a real copy of a mutable collection and explain why it
      is only a shallow copy.
- [ ] I can explain why a tuple containing a list can still "change," and
      why that same tuple cannot be used as a dictionary key.
- [ ] I can explain the difference between `+=` on a list and `+=` on a
      tuple or string.
- [ ] I have completed the "try it yourself" exercises above.

## Connection to later Applied AI and Agentic AI engineering work

Mutability bugs are among the most common real bugs in exactly the kind of
code you will write for AI applications and agents: a shared conversation
history accidentally mutated by one part of the system while another part
still expects the original; a tool's input list changed in place when the
caller assumed it would be left alone; a "copy" of an agent's state that
turned out to be an alias, so two independent-seeming steps silently
affected each other. The habits from Section 7 — copy intentionally, avoid
touching shared input, name copies clearly, and test aliasing behavior
directly rather than assuming — are exactly the discipline that keeps
larger, more complex AI systems predictable as their internal state grows
far beyond anything this lesson's small examples show.

---

## Appendix: Mutability Tool Reference

A concise reference for the tools this lesson covers. For complete method
listings, see the appendices in the
[lists](05-lists-mutation-copying-and-aliasing.md#appendix-complete-list-method-reference),
[tuples](06-tuples-and-unpacking.md#appendix-complete-tuple-method-reference),
[dictionaries](07-dictionaries-and-lookups.md#appendix-complete-dict-method-reference),
and [sets](08-sets-and-unique-values.md#appendix-complete-set-method-reference)
lessons.

| Tool | Purpose | Example | Behavior |
|---|---|---|---|
| `=` | Assignment: point a name at an object | `x = [1, 2]` | Creates a reference; does not copy. |
| `==` | Equality: compare values | `[1, 2] == [1, 2]` → `True` | Never affects either operand. |
| `is` | Identity: compare objects | `x is y` | Reliable mainly for `None`; avoid for ordinary values. |
| `id()` | Observe an object's identity | `id(x) == id(y)` | Optional; the number itself is not meaningful. |
| `.copy()` | Shallow copy a list, dict, or set | `y = x.copy()` | Returns a new, independent outer object. |
| `list(x)` | Build a new list from `x` | `list((1, 2))` → `[1, 2]` | Shallow copy when `x` is already list-like. |
| `dict(x)` | Build a new dict from `x` | `dict({"a": 1})` | Shallow copy when `x` is already a mapping. |
| `set(x)` | Build a new set from `x` | `set([1, 1, 2])` → `{1, 2}` | Shallow copy; also removes duplicates. |
| `[:]` | Slice an entire sequence | `y = x[:]` | Shallow copy for lists; tuples/strings are already immutable, so this mainly matters for lists. |
| `+=` | In-place add (mutable) or rebind (immutable) | `x += [3]` vs `x += (3,)` | Mutates in place for a list; builds a new object for a tuple or string. |
