# Dictionaries and Lookups

## Why dictionaries matter

Back in
[Strings: Indexing, Slicing, and Formatting](04-strings-indexing-slicing-and-formatting.md),
the `format_map()` method needed a mapping, and you were told,
"dictionaries are covered fully in Topic 7." This lesson is that promise
kept. A list finds things by **position** — "give me item number 2." A
**dictionary** finds things by **meaning** — "give me whatever is stored
under `"email"`," regardless of where it happens to live. This is an
enormous shift in how you can organize data: a user profile, a product's
price list, a configuration file, or a count of how many times each word
appears are all naturally "look something up by name," not "look something
up by position." Dictionaries are how Python represents exactly that.

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain what a dictionary is: a mapping from unique keys to values.
- Create empty and populated dictionaries, and explain which value types
  are valid as keys and why.
- Look up a value safely, using both direct lookup and `.get()`, and
  explain `KeyError`.
- Add, update, and safely remove key-value pairs.
- Check whether a key exists using `in` and `not in`.
- Iterate over a dictionary's keys, values, and key-value pairs, and
  explain why `.items()` is usually clearest when you need both.
- Explain that modern Python preserves insertion order, and why you
  should not rely on that as an accidental business rule.
- Explain dictionary aliasing versus `.copy()`, and what a shallow copy
  does and does not protect.
- Use the most common dictionary methods and built-in functions
  confidently, and know how to look up any other dictionary method in the
  appendix.

## Prerequisites

- [Tuples and Unpacking](06-tuples-and-unpacking.md) — this lesson shows
  how a list of tuples converts directly into a dictionary with `dict()`.
- [Lists: Mutation, Copying, and Aliasing](05-lists-mutation-copying-and-aliasing.md) —
  the ideas of mutation, aliasing, and shallow copying return here in the
  context of dictionaries, and are assumed already familiar.

## Key terms

| Term | Plain-English definition |
|---|---|
| **Dictionary (`dict`)** | A changeable mapping from unique keys to values, where values are looked up by key rather than by position, written between curly braces, such as `{"name": "Ada"}`. |
| **Key** | The unique name used to look up a value in a dictionary. |
| **Value** | The piece of data stored under a key. |
| **Key-value pair** | One `key: value` entry inside a dictionary. |
| **Mapping** | A general term for any collection that connects keys to values, of which `dict` is Python's main example. |
| **Hashable** | An object that has a stable hash value and can therefore be used as a dictionary key. Many common hashable objects are immutable, such as strings, numbers, and tuples containing hashable values, but hashability and immutability are not exactly the same concept. Lists and dictionaries are not hashable. |
| **`KeyError`** | The error Python raises when you look up a key that does not exist, using direct lookup. |
| **Dictionary view** | A live, linked object returned by `.keys()`, `.values()`, or `.items()`, which reflects the dictionary's current contents rather than freezing a copy. |
| **Mutation** | Changing a dictionary in place — adding, updating, or removing key-value pairs — without replacing it with a different dictionary. |
| **Alias** | A second variable name referring to the exact same dictionary, rather than to a separate copy. |
| **Shallow copy** | A copy of the dictionary's own key-value structure only; any mutable values inside it (like a list) are still shared with the original. |
| **Insertion order** | The order key-value pairs were added to a dictionary, which modern Python remembers and preserves. |

## Step-by-step explanation

### 1. What a dictionary is

A **dictionary** is a collection that maps unique **keys** to **values** —
a **mapping**. Instead of finding an item by counting positions, the way
lists and tuples work, you find a value by naming the key it is stored
under:

```python
person = {"name": "Ada", "age": 30}
```

Read this as: "under the key `"name"`, store the value `"Ada"`; under the
key `"age"`, store the value `30`." Use a dictionary whenever data is
naturally described as "this named thing has this value" — a person's
fields, a product's price, a setting's current value — rather than "this
is the third item in a sequence."

### 2. Creating empty and populated dictionaries

```python
empty_dict = {}
scores = {"Ada": 95, "Grace": 88}
```

`empty_dict` starts with no key-value pairs at all — a common starting
point before filling one in gradually. One thing worth flagging now: `{}`
creates an **empty dictionary**, not an empty set (sets, which also use
curly braces when populated, are covered in the next topic) — `{}` always
means "empty dict" in Python.

### 3. Keys and values

**Valid key types, at a beginner level:** a dictionary key must be
**hashable**. Many common hashable keys are immutable values, such as
strings, numbers, and tuples containing hashable values, but hashability
and immutability are different concepts. Strings, numbers, and booleans
are the most common valid keys. Lists (and other dictionaries) are **not**
allowed as keys, because they are unhashable:

```python
bad_dict = {[1, 2]: "value"}
```

```text
TypeError: unhashable type: 'list'
```

**Keys are matched by hashing and equality:** Python decides whether two
keys are the same using their hash and equality, not their apparent type.

```python
data = {1: "integer"}

print(data[True])   # integer
print(data[1.0])    # integer
```

`1`, `True`, and `1.0` compare equal in Python, so they refer to the same
dictionary key in this example. Dictionary key behavior is based on hashing
and equality, not simply on the key's apparent type.

**Why lists and dictionaries cannot be used as keys:** a dictionary key
must be hashable, and lists and dictionaries are unhashable built-in
types, so Python refuses them outright. The reason is that a dictionary
needs a key's hash and equality behavior to stay stable for as long as it
is used to find things — if a list used as a key could later be mutated,
Python would lose the ability to reliably find that entry again. Hashability
and mutability are related for many common built-in types, but they are
not the same concept.

**Keys must be unique.** If the same key is written twice while creating a
dictionary, the second value silently wins — there is no error, and no
way to recover the first value afterward:

```python
data = {"a": 1, "a": 2}
print(data)   # {'a': 2}
```

Values, unlike keys, have no such restriction — the same value can appear
under many different keys with no problem at all.

### 4. Looking up values

**Direct lookup** with square brackets reads a value by its key:

```python
person = {"name": "Ada", "age": 30}
print(person["name"])   # Ada
```

**`KeyError`:** looking up a key that does not exist stops the program:

```python
person = {"name": "Ada", "age": 30}
print(person["missing"])
```

```text
KeyError: 'missing'
```

**Safer lookup with `.get()`:** `.get(key)` returns `None` instead of
raising an error when the key is missing, which is usually far more
useful than crashing:

```python
person = {"name": "Ada", "age": 30}
print(person.get("missing"))          # None
```

**`.get()` with a default value:** a second argument lets you choose
exactly what comes back instead of `None`:

```python
person = {"name": "Ada", "age": 30}
print(person.get("missing", "N/A"))   # N/A
```

Prefer `.get()` over direct lookup whenever a missing key is a normal,
expected possibility you plan to handle; use direct lookup only when a
missing key should be treated as a genuine bug you want to surface
immediately.

### 5. Adding and updating key-value pairs

The same square-bracket syntax both **adds** a brand-new key and
**updates** an existing one — Python decides which based on whether the
key is already present:

```python
person = {"name": "Ada"}

person["age"] = 30    # "age" is new — this ADDS a key-value pair
print(person)          # {'name': 'Ada', 'age': 30}

person["age"] = 31    # "age" already exists — this UPDATES its value
print(person)          # {'name': 'Ada', 'age': 31}
```

### 6. Removing values safely

The `del` statement removes a key-value pair, but raises `KeyError` if the
key is missing:

```python
person = {"name": "Ada", "age": 30}
del person["age"]
print(person)   # {'name': 'Ada'}

del person["age"]
```

```text
KeyError: 'age'
```

For a **safe** removal — one that will not crash your program if the key
happens not to be there — use `.pop(key, default)`, covered fully in the
appendix, which returns a fallback value instead of raising an error:

```python
person = {"name": "Ada"}
removed = person.pop("age", "not found")
print(removed)   # not found
print(person)     # {'name': 'Ada'}
```

### 7. Checking whether a key exists

`in` and `not in` check dictionary **keys** by default — not values:

```python
person = {"name": "Ada", "age": 30}

print("name" in person)       # True
print("email" in person)      # False
print("email" not in person)  # True
```

Checking membership before a direct lookup is a common, safe pattern:
`if "email" in person: print(person["email"])` avoids a `KeyError`
entirely — though for simple cases, `.get()` from Section 4 is often even
more direct.

### 8. Iterating through a dictionary

Looping over a dictionary directly visits its **keys**, one at a time —
exactly the same as looping over `.keys()` explicitly:

```python
scores = {"Ada": 95, "Grace": 88, "Alan": 76}

for name in scores:
    print(name)

for name in scores.keys():
    print(name)
```

Both loops above print the same three names. To visit just the
**values**, loop over `.values()`:

```python
scores = {"Ada": 95, "Grace": 88, "Alan": 76}
for score in scores.values():
    print(score)
```

**`.items()` for both at once:** when you need the key *and* its value
together, `.items()` is almost always the clearest choice, since it
unpacks each key-value pair directly in the loop header — exactly the
tuple-unpacking pattern from the previous lesson:

```python
scores = {"Ada": 95, "Grace": 88, "Alan": 76}
for name, score in scores.items():
    print(name, score)
```

```text
Ada 95
Grace 88
Alan 76
```

Compare this with the alternative of looping over keys and then indexing
back in (`for name in scores: print(name, scores[name])`) — it works, but
it is usually less clear than using `.items()` when you need both the key
and its value directly.

### 9. Dictionary ordering

Modern Python (3.7 and later) **preserves insertion order**: a dictionary
remembers the order key-value pairs were added, and iterating over it
always visits them in that same order:

```python
data = {}
data["z"] = 1
data["a"] = 2
data["m"] = 3
print(data)   # {'z': 1, 'a': 2, 'm': 3}  — insertion order, not sorted order
```

This is a real, documented language guarantee, not an accident of one
particular Python version. Even so, treat it carefully: do not let a
program's *correctness* silently depend on dictionary order unless that
order is genuinely part of the design and is clearly documented as such —
a reader skimming your code should not have to know this guarantee exists
just to understand what your program does. If order actually matters to
your logic, say so explicitly in a comment or variable name, rather than
relying on it silently.

### 10. Copying: aliasing versus `.copy()`

Exactly as with lists, writing `second = first` for a dictionary does
**not** create a copy — it creates an **alias**, a second name for the
same dictionary, so mutating either name affects both:

```python
original = {"a": 1}
alias = original
alias["b"] = 2

print(original)   # {'a': 1, 'b': 2}  — changed too!
print(alias)       # {'a': 1, 'b': 2}
```

For a genuine, independent copy, use `.copy()`:

```python
original = {"a": 1, "b": 2}
copy_dict = original.copy()
copy_dict["c"] = 3

print(original)     # {'a': 1, 'b': 2}      — unaffected
print(copy_dict)     # {'a': 1, 'b': 2, 'c': 3}
```

**Shallow copying, at a beginner level:** `.copy()` only duplicates the
dictionary's own key-value structure. If a value stored inside it is
itself mutable — a list, for example — that inner value is still *shared*
between the original and the copy, exactly like the nested-list situation
from the lists lesson. Mutating a shared inner list through the copy would
still show up in the original, even though the top-level dictionaries
themselves are independent.

### 11. Practical use cases, at a glance

Four realistic dictionary situations this lesson's Examples section
builds on directly:

- **A product and quantity record**, such as
  `inventory = {"apples": 50, "bread": 12}` — looking up and updating a
  quantity by product name.
- **A small user profile**, such as
  `{"name": "Ada", "email": "ada@example.com"}` — a fixed set of named
  fields describing one person.
- **Counting simple categories**, such as tallying how many purchases fall
  into each category, building the counts up one dictionary entry at a
  time.
- **Safe configuration lookup with defaults**, such as reading a
  `timeout` setting that falls back to a sensible default if it was never
  explicitly configured.

## Examples

### Example 1 — A product and quantity record

```python
inventory = {"apples": 50, "bananas": 30, "bread": 12}

inventory["apples"] -= 5
print(inventory)

inventory["milk"] = 20
print(inventory)

print(inventory.get("eggs", 0))
```

**Plain-English explanation:**

- `inventory` maps each product name to how many units are in stock.
- `inventory["apples"] -= 5` looks up the current apple count, subtracts
  `5`, and stores the result back under the same key — an update, using
  the same "look up, compute, reassign" pattern you already know from
  ordinary variables. Printing shows
  `{'apples': 45, 'bananas': 30, 'bread': 12}`.
- `inventory["milk"] = 20` adds a brand-new key, since `"milk"` was not
  present before: `{'apples': 45, 'bananas': 30, 'bread': 12, 'milk': 20}`.
- `inventory.get("eggs", 0)` safely checks for a product that was never
  stocked at all, printing `0` instead of raising `KeyError` — a very
  common, realistic pattern for "how many do we have of X, treating
  'never stocked' as zero."

### Example 2 — Counting simple categories

```python
purchases = ["fruit", "dairy", "fruit", "bakery", "dairy", "fruit"]

category_counts = {}
for category in purchases:
    if category in category_counts:
        category_counts[category] += 1
    else:
        category_counts[category] = 1

print(category_counts)
```

**Plain-English explanation:**

- `purchases` is a list (from Topic 5) recording one category per
  purchase, in order, with repeats.
- `category_counts = {}` starts an empty dictionary that will accumulate
  one running total per category.
- The `for` loop visits each purchase in turn. `if category in
  category_counts:` (Section 7) checks whether this category has already
  been seen; if so, `category_counts[category] += 1` increases its
  existing count. If not, `category_counts[category] = 1` adds it as a
  brand-new key, starting its count at one.
- After all six purchases are processed, printing shows
  `{'fruit': 3, 'dairy': 2, 'bakery': 1}` — each category paired with how
  many times it appeared, built up one purchase at a time.
- This is the standard beginner counting pattern: a dictionary as a
  running tally, keyed by whatever you are counting.

### Example 3 — Safe configuration lookup with defaults

```python
config = {"debug": True, "max_retries": 3}

timeout = config.get("timeout", 30)
max_retries = config.get("max_retries", 5)

print(f"Timeout: {timeout}")
print(f"Max retries: {max_retries}")

for setting, value in config.items():
    print(f"{setting} = {value}")
```

**Plain-English explanation:**

- `config` represents settings someone actually provided — notice
  `"timeout"` was never set at all.
- `config.get("timeout", 30)` safely reads a setting that might not exist,
  falling back to `30` — a sensible default — instead of crashing.
  `config.get("max_retries", 5)` does the same for a setting that *is*
  present, so it simply returns the configured value, `3`, and the
  default `5` is never used.
- The two f-strings report both resolved settings clearly:
  `Timeout: 30` and `Max retries: 3`.
- The final loop uses `.items()` (Section 8) to print every setting that
  was *actually* provided in `config`, one per line:
  `debug = True` and `max_retries = 3` — notice `"timeout"` does not
  appear here, since it was never really in `config` at all, only
  supplied as a fallback at the moment it was read.
- This pattern — read configuration with `.get()` and a sensible default,
  rather than assuming every setting was explicitly provided — is
  extremely common in real programs.

## Common beginner mistakes

- **Using direct lookup (`data["key"]`) on a key that might not exist.**
  This raises `KeyError` and stops the program; use `.get()` (with a
  default, if appropriate) whenever a missing key is a normal
  possibility.
- **Assuming `second = first` makes a copy of a dictionary.** As Section
  10 showed, this only creates a second name for the same dictionary;
  mutating one mutates both. Use `.copy()` for a real, independent copy.
- **Trying to use a list (or another dictionary) as a key.** Keys must be
  hashable. Many common hashable keys are immutable, but hashability and
  immutability are different concepts; Python raises `TypeError`
  immediately rather than allowing a list as a key.
- **Writing the same key twice while creating a dictionary and expecting
  both values to be kept.** Only the last value written under a repeated
  key survives — Python does not warn you about this.
- **Relying on dictionary order as if it were a business rule**, without
  documenting that intent clearly, just because modern Python happens to
  preserve insertion order.
- **Forgetting that `in` checks keys, not values**, and being surprised
  when `"Ada" in {"name": "Ada"}` is `False` — the key here is `"name"`,
  not `"Ada"`.

## Try it yourself

Do not look up full solutions. Predict the output before running each one.

1. Create a dictionary describing a book, with keys `"title"`, `"author"`,
   and `"year"`. Print each value using direct lookup, then safely look up
   a key that does not exist (such as `"isbn"`) using `.get()` with a
   sensible default.
2. Given `stock = {"pens": 100, "notebooks": 40}`, decrease `"pens"` by
   `15`, then add a brand-new key `"erasers"` with the value `60`. Print
   `stock` after each change.
3. Given `settings = {"volume": 70, "brightness": 50}`, safely remove
   `"volume"` using a method that will not crash if the key happens to be
   missing, and print the removed value.
4. Write a small loop that counts how many times each letter appears in
   the word `"mississippi"`, using the counting pattern from Example 2.
5. Create a dictionary, assign it to a second variable name (an alias, not
   a copy), mutate it through the second name, and confirm both names show
   the change. Then repeat using `.copy()` and confirm the two dictionaries
   are now independent.
6. Given `user = {"name": "Grace", "email": "grace@example.com", "active": True}`,
   loop over it with `.items()` and print each field as
   `"field: value"`.

## Summary

- A **dictionary** maps unique **keys** to **values**; use one whenever
  data is naturally "look this up by name."
- Keys must be **hashable** (many common hashable keys are immutable) and
  unique; a
  repeated key silently keeps only the last value written.
- Direct lookup (`data["key"]`) raises `KeyError` on a missing key;
  `.get(key, default)` is the safer alternative.
- The same `data["key"] = value` syntax adds a new key or updates an
  existing one; `del data["key"]` removes one but can raise `KeyError`,
  while `.pop(key, default)` removes safely.
- `in` and `not in` check **keys**, not values.
- `.keys()`, `.values()`, and `.items()` iterate over keys, values, or
  both together; `.items()` is usually clearest when both are needed.
- Modern Python preserves insertion order, but that should not become an
  accidental, undocumented business rule.
- **Aliasing** (`second = first`) shares one dictionary under two names;
  `.copy()` makes a real, independent (shallow) copy.

## Completion checklist

- [ ] I can create empty and populated dictionaries and explain what
      makes a key valid.
- [ ] I can explain why keys must be unique and what happens with a
      repeated key.
- [ ] I can look up a value directly and with `.get()`, and explain
      `KeyError`.
- [ ] I can add, update, and safely remove key-value pairs.
- [ ] I can check whether a key exists using `in`.
- [ ] I can iterate over keys, values, and key-value pairs, and explain
      why `.items()` is usually clearest.
- [ ] I can explain dictionary insertion order and why not to rely on it
      silently.
- [ ] I can explain dictionary aliasing versus `.copy()`, including the
      shallow-copy limitation.
- [ ] I have completed the "try it yourself" exercises above.
- [ ] I know the appendix exists and can find a dictionary method in it
      when I need one.

## Connection to later Applied AI and Agentic AI engineering work

Dictionaries are the natural shape for almost every structured piece of
data an AI system passes around: a tool call's named arguments, a model's
structured response fields, a configuration for an agent's behavior, a
single retrieved record's fields. The safe-lookup habits from this lesson
— preferring `.get()` with a sensible default over a direct lookup that
can crash — are exactly what you will need when reading a tool's response
or a piece of configuration that might not always contain every field.
Dictionary aliasing is just as real a risk here as it was for lists:
accidentally sharing and mutating a dictionary of conversation state or
tool arguments between two parts of an agent's code, instead of
intentionally copying it, is a common, hard-to-trace source of bugs in
exactly this kind of system.

---

## Appendix: Complete `dict` Method Reference

This appendix was generated against the Python version installed in this
environment — check `python3 --version` yourself if you want to confirm
your own. Run
`python3 -c "print([m for m in dir(dict) if not m.startswith('_')])"`
in a terminal at any time to list every public method your own installed
Python provides.

**You do not need to memorize this appendix.** Read through it once to
know what exists, get comfortable with the methods used throughout the
lesson above, and come back here as a reference whenever you need a
method you do not use every day. The appendix covers the public
dictionary methods and related constructor-level operation shown below.
Most entries are instance methods of `dict`; `fromkeys()` is called on the
`dict` type itself rather than on an individual dictionary instance. None of
Python's internal "dunder" methods (like `__len__`) or private methods are
included. For every method, the
note explicitly states whether it **mutates** the original dictionary or
**returns a separate value or view** without changing it.

#### `clear()`

Removes every key-value pair, leaving the dictionary empty.

```python
data = {"a": 1, "b": 2}
data.clear()
print(data)   # {}
```

**Mutates the dictionary in place; returns `None`.**

#### `copy()`

Returns a new, independent (shallow) copy of the dictionary.

```python
original = {"a": 1}
duplicate = original.copy()
duplicate["b"] = 2

print(original)    # {'a': 1}
print(duplicate)    # {'a': 1, 'b': 2}
```

**Does not mutate the original; returns a new dictionary.** See Section
10 for the full discussion of copying versus aliasing.

#### `fromkeys(keys, value)`

A helper (called on the `dict` type itself, as `dict.fromkeys(...)`, not
on one particular dictionary) that builds a new dictionary from a
collection of keys, giving every one of them the *same* starting value.

```python
keys = ["a", "b", "c"]
new_dict = dict.fromkeys(keys, 0)
print(new_dict)   # {'a': 0, 'b': 0, 'c': 0}
```

**Does not mutate anything existing; returns a new dictionary.**

**Warning — a mutable default value is shared, not copied:** if the
default value itself is mutable (such as a list), every key ends up
pointing at the *exact same* mutable object, not separate copies of it —
mutating it through one key changes what every other key shows too:

```python
keys = ["a", "b"]
shared_list_dict = dict.fromkeys(keys, [])
shared_list_dict["a"].append(1)

print(shared_list_dict)   # {'a': [1], 'b': [1]}  — both changed!
```

Only one list was ever created; both `"a"` and `"b"` were simply given
the same reference to it. Avoid `dict.fromkeys(keys, some_mutable_value)`
whenever each key genuinely needs its *own*, independent value — build
the dictionary a different way instead, such as looping and assigning a
fresh value per key.

#### `get(key, default=None)`

Returns the value for `key` if present; otherwise returns `default`
(which itself defaults to `None`) instead of raising an error.

```python
person = {"name": "Ada"}
print(person.get("name"))        # Ada
print(person.get("age"))          # None
print(person.get("age", 0))       # 0
```

**Does not mutate; returns the found value or the default.**

#### `items()`

Returns a **view** of all key-value pairs, each as a two-item tuple.

```python
scores = {"Ada": 95, "Grace": 88}
print(scores.items())   # dict_items([('Ada', 95), ('Grace', 88)])
```

**Does not mutate; returns a live dictionary view**, most often used
directly in a `for` loop, as in Section 8, rather than printed on its own.

#### `keys()`

Returns a **view** of all keys.

```python
scores = {"Ada": 95, "Grace": 88}
print(scores.keys())   # dict_keys(['Ada', 'Grace'])
```

**Does not mutate; returns a live dictionary view.**

#### `pop(key, default)`

Removes `key` and **returns its value**. If `key` is missing and a
`default` was given, returns that instead of raising an error; if no
default was given and the key is missing, raises `KeyError`.

```python
person = {"name": "Ada", "age": 30}
age = person.pop("age")
print(age)       # 30
print(person)     # {'name': 'Ada'}

email = person.pop("email", "not set")
print(email)      # not set
```

**Mutates the dictionary (removes the key) if found; returns the removed
value, or the default.** This is the safe removal tool from Section 6.

#### `popitem()`

Removes and returns the **most recently inserted** key-value pair, as a
`(key, value)` tuple. Raises `KeyError` if the dictionary is empty.

```python
data = {"a": 1, "b": 2, "c": 3}
last_item = data.popitem()
print(last_item)   # ('c', 3)
print(data)          # {'a': 1, 'b': 2}
```

**Mutates the dictionary in place; returns the removed `(key, value)`
tuple.** Unlike `pop()`, you do not choose which key to remove —
`popitem()` always takes the last one inserted (this relies directly on
the insertion-order guarantee from Section 9).

#### `setdefault(key, default)`

Returns the current value for `key` if it already exists; if not, it
**inserts** `key` with `default` first, and then returns that same
default. This is its key difference from `.get()`, which never modifies
the dictionary no matter what.

```python
person = {"name": "Ada"}

age = person.setdefault("age", 0)
print(age)        # 0
print(person)       # {'name': 'Ada', 'age': 0}   — "age" was ADDED

name = person.setdefault("name", "Unknown")
print(name)        # Ada
print(person)        # {'name': 'Ada', 'age': 0}   — unchanged; "name" already existed
```

**Mutates the dictionary only if the key was missing (inserting the
default); always returns a value.** Use `.get()` when you only want to
*read* a value safely; use `.setdefault()` when you also want a missing
key to be filled in with that default at the same time.

#### `update(other)`

Merges another dictionary's key-value pairs into this one, in place —
adding new keys and overwriting matching existing ones.

```python
person = {"name": "Ada"}
person.update({"age": 30, "city": "London"})
print(person)   # {'name': 'Ada', 'age': 30, 'city': 'London'}
```

**Mutates the dictionary in place; returns `None`.** Compare this with
assigning one key directly (`person["age"] = 30`): direct assignment sets
exactly one key at a time, while `.update()` merges in *several* keys at
once from another dictionary — reach for `.update()` when you have a
whole group of new or changed values ready together, and direct
assignment for a single, individual change.

#### `values()`

Returns a **view** of all values.

```python
scores = {"Ada": 95, "Grace": 88}
print(scores.values())   # dict_values([95, 88])
```

**Does not mutate; returns a live dictionary view.**

## Appendix summary

That covers all 11 public, non-dunder methods on `dict` available in this
Python installation. Come back to this reference whenever you need it —
you are not expected to remember all of it, only to know it exists and
how to find what you need.

## Appendix: Built-in Functions and Operators Used With Dictionaries

```python
scores = {"Ada": 95, "Grace": 88, "Alan": 76}

print(len(scores))            # 3            — how many key-value pairs
print(list(scores))           # ['Ada', 'Grace', 'Alan']  — a list of keys
print(sorted(scores))         # ['Ada', 'Alan', 'Grace']  — keys, sorted alphabetically

print(scores == {"Ada": 95, "Grace": 88, "Alan": 76})   # True
print(scores == {"Grace": 88, "Ada": 95, "Alan": 76})   # True  — order does not affect equality
```

`len()`, `list()`, and `sorted()` all operate on a dictionary's **keys**
by default — the same behavior as looping over a dictionary directly, from
Section 8. `==` compares two dictionaries by their **content**, key by
key and value by value; two dictionaries with the same pairs are equal
even if those pairs were inserted in a different order, which is worth
noticing alongside Section 9's point that *iteration* order is still
preserved and meaningful, even though it does not affect equality.

`dict()` can build a dictionary directly from a list of two-item tuples —
a natural bridge from the previous lesson:

```python
pairs = [("a", 1), ("b", 2)]
new_dict = dict(pairs)
print(new_dict)   # {'a': 1, 'b': 2}
```

Finally, Python provides a dictionary **merge operator**, `|`, as a modern
alternative to `.update()`. The `|` operator for dictionaries is available
in Python 3.9 and later; on older versions, or when mutating the existing
dictionary is acceptable, use `.update()`:

```python
defaults = {"debug": False, "timeout": 30}
overrides = {"timeout": 60}

merged = defaults | overrides
print(merged)     # {'debug': False, 'timeout': 60}
print(defaults)    # {'debug': False, 'timeout': 30}  — unchanged
```

Unlike `.update()`, `|` does **not** mutate either dictionary — it builds
and returns a brand-new one, leaving both `defaults` and `overrides`
untouched. Treat `|` as optional, modern syntax worth recognizing; for
day-to-day beginner code, `.update()` (when you want to mutate in place)
or a clear, explicit new-dictionary assignment (when you want a new
result, as shown here) are generally more readable while you are still
building fluency.
