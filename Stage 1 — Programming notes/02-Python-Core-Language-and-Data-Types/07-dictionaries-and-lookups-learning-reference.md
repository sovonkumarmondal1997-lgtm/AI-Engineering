# Dictionaries and Lookups --- Complete Learning Reference

**Source lesson:** `07-dictionaries-and-lookups(1).md`\
**Purpose:** Simple step-by-step teaching summary, Stage 1 assessment,
and all six solved exercises.

------------------------------------------------------------------------

# Part 1 --- Lesson summary (under 1,200 words)

## 1. Dictionaries: lookup by meaning

A **dictionary (`dict`)** is a mutable mapping of unique keys to values.
Lists and tuples retrieve by position; dictionaries retrieve by
meaningful key. Use them for profiles, inventory, configuration, prices,
and category counts.

``` python
person = {"name": "Ada", "age": 30}
empty_dict = {}
scores = {"Ada": 95, "Grace": 88}
```

`{}` creates an empty dictionary, not an empty set.

## 2. Keys, values, hashability, uniqueness

A **key** identifies an entry; a **value** is the stored data. Keys must
be **hashable**. Strings, numbers, booleans, and tuples containing
hashable values are common keys. Lists and dictionaries are unhashable:

``` python
bad_dict = {[1, 2]: "value"}  # TypeError: unhashable type: 'list'
```

Hashability and immutability are related for many built-in types, but
are not identical. Python matches keys using hashing and equality: `1`,
`True`, and `1.0` compare equal and therefore refer to the same key:

``` python
data = {1: "integer"}
print(data[True])  # integer
print(data[1.0])   # integer
```

Keys are unique; a repeated key silently keeps the last value. Values
may repeat:

``` python
data = {"a": 1, "a": 2}
print(data)  # {'a': 2}
```

## 3. Lookup, missing keys, and `.get()`

Square brackets perform direct lookup. A missing key raises `KeyError`:

``` python
person = {"name": "Ada", "age": 30}
print(person["name"])     # Ada
print(person["missing"])  # KeyError: 'missing'
```

Use `.get()` when absence is expected; it returns `None` or a supplied
default:

``` python
print(person.get("missing"))         # None
print(person.get("missing", "N/A"))  # N/A
```

Use direct lookup when a missing key should expose a bug.

## 4. Add, update, remove, and membership

The same assignment adds a new key or updates an existing one:

``` python
person = {"name": "Ada"}
person["age"] = 30  # add
person["age"] = 31  # update
```

`del person["age"]` removes a key but raises `KeyError` if absent.
`.pop(key, default)` safely removes and returns the value, or the
default if missing:

``` python
person = {"name": "Ada"}
removed = person.pop("age", "not found")
print(removed)  # not found
print(person)   # {'name': 'Ada'}
```

`in` and `not in` test **keys**, not values:

``` python
print("name" in person)   # True
print("email" not in person)  # True
```

## 5. Iteration and insertion order

A direct dictionary loop visits keys. `.keys()` gives keys, `.values()`
gives values, and `.items()` gives key-value pairs as two-item tuples.
`.items()` is clearest when both are needed:

``` python
scores = {"Ada": 95, "Grace": 88, "Alan": 76}
for name in scores:
    print(name)
for score in scores.values():
    print(score)
for name, score in scores.items():
    print(name, score)
```

Modern Python (3.7+) preserves insertion order, not sorted order. Do not
make correctness depend on this accidentally; document it if order is
part of the design.

## 6. Aliasing and shallow copying

`second = first` creates an **alias**: both names refer to the same
dictionary. `.copy()` creates a separate top-level dictionary:

``` python
original = {"a": 1}
alias = original
alias["b"] = 2
print(original)  # {'a': 1, 'b': 2}

copy_dict = original.copy()
copy_dict["c"] = 3
print(original)   # {'a': 1, 'b': 2}
print(copy_dict)  # {'a': 1, 'b': 2, 'c': 3}
```

This is a **shallow copy**: mutable values nested inside (such as lists)
remain shared.

## 7. Three practical examples

**Inventory:** `inventory = {"apples": 50, "bananas": 30, "bread": 12}`.
`inventory["apples"] -= 5` changes apples to 45;
`inventory["milk"] = 20` adds milk; `inventory.get("eggs", 0)` returns 0
safely.

**Category counts:** For
`purchases = ["fruit", "dairy", "fruit", "bakery", "dairy", "fruit"]`,
start `category_counts = {}`. Loop over each category: increment its
existing count or create it with 1. Result:
`{'fruit': 3, 'dairy': 2, 'bakery': 1}`. This is a running tally.

**Configuration:** With `config = {"debug": True, "max_retries": 3}`,
`config.get("timeout", 30)` returns 30, while
`config.get("max_retries", 5)` returns 3. F-strings print `Timeout: 30`
and `Max retries: 3`. A `.items()` loop prints only stored settings
(`debug = True`, `max_retries = 3`); the fallback timeout is not
inserted.

Dictionaries also represent user profiles, product quantities, tool
arguments, model response fields, agent configuration, and retrieved
records.

## 8. Common mistakes

-   Direct lookup on a possibly missing key causes `KeyError`; use
    `.get()` or handle absence.
-   `second = first` aliases; it does not copy.
-   Lists and dictionaries cannot be keys because they are unhashable.
-   Duplicate keys keep only the last value.
-   Do not rely silently on insertion order.
-   `in` checks keys, not values.

## 9. Dictionary method appendix

The lesson lists 11 public, non-dunder methods:

  -----------------------------------------------------------------------
  Method                              Purpose and behavior
  ----------------------------------- -----------------------------------
  `clear()`                           Removes all entries; mutates;
                                      returns `None`.

  `copy()`                            Returns a new shallow copy.

  `dict.fromkeys(keys, value)`        Creates a dictionary with each key
                                      set to the same value. Mutable
                                      defaults (e.g. `[]`) are shared by
                                      all keys.

  `get(key, default=None)`            Reads value or default; no
                                      mutation.

  `items()`                           Live view of key-value pairs as
                                      two-item tuples.

  `keys()`                            Live view of keys.

  `pop(key, default)`                 Removes and returns value; default
                                      used if missing, otherwise
                                      `KeyError`.

  `popitem()`                         Removes and returns most recently
                                      inserted pair as a tuple; empty
                                      dict raises `KeyError`.

  `setdefault(key, default)`          Returns existing value or inserts
                                      and returns default; may mutate.

  `update(other)`                     Adds/overwrites entries in place;
                                      returns `None`.

  `values()`                          Live view of values.
  -----------------------------------------------------------------------

A **view** reflects current dictionary contents; it is not a frozen
copy. Inspect your Python's methods with:

``` bash
python3 -c "print([m for m in dir(dict) if not m.startswith('_')])"
```

`dict.fromkeys()` shares one mutable default object across keys. For
example, `dict.fromkeys(["a", "b"], [])` followed by
`result["a"].append(1)` makes both keys show `[1]`. Create a fresh list
per key if independent lists are required.

Related built-ins and operations:

``` python
scores = {"Ada": 95, "Grace": 88, "Alan": 76}
print(len(scores))      # 3
print(list(scores))     # list of keys
print(sorted(scores))  # sorted list of keys
print(scores == {"Grace": 88, "Ada": 95, "Alan": 76})  # True
```

`len()`, `list()`, and `sorted()` operate on keys by default. Dictionary
equality compares key-value content, not insertion order.

`dict()` builds a dictionary from two-item tuples:

``` python
pairs = [("a", 1), ("b", 2)]
new_dict = dict(pairs)
print(new_dict)  # {'a': 1, 'b': 2}
```

Python 3.9+ supports merge operator `|`, which creates a new dictionary
and leaves both inputs unchanged:

``` python
defaults = {"debug": False, "timeout": 30}
overrides = {"timeout": 60}
merged = defaults | overrides
print(merged)    # {'debug': False, 'timeout': 60}
print(defaults)  # {'debug': False, 'timeout': 30}
```

Use `.update()` to mutate an existing dictionary; use `|` for a new
merged result. Check `python3 --version` for version-specific support.

# Part 2 --- Current learning-level assessment

Your Stage 1 project tree progresses from computational thinking and
program design into Python core language and data types, then control
flow/functions/errors, collections and algorithmic habits,
files/structured data/CLI programs, modules and code quality,
testing/debugging, and object-oriented design. Its later advanced
modules include production Python, data modelling, metaprogramming,
standard library, binary/text processing, advanced testing, performance,
packaging, CPython internals, design patterns, visualization, security,
refactoring, and functions/OOP gap topics. Planned projects include an
expense-ledger CLI, log-investigation CLI, data-quality/transformation
pipeline, and rule-based risk-review engine.

**Current position:** Early Stage 1, Python Core Language and Data
Types. You have worked through strings, lists, tuples, and now
dictionaries. This lesson reuses list iteration, conditionals, tuple
unpacking, mutation, aliasing, and shallow copying.

**Important assessment boundary:** The project tree shows what your
roadmap intends to teach; it does not prove that every topic has been
mastered. No independently executed outputs are supplied with this
request, so I can assess your curriculum position but cannot certify
practical proficiency. The solutions below deliberately use only the
current lesson and previously introduced fundamentals.

------------------------------------------------------------------------

# Part 3 --- All six exercises solved step by step (under 1,500 words)

## Exercise 1 --- Create a book dictionary and use `.get()`

``` python
book = {
    "title": "Python Basics",
    "author": "Alex",
    "year": 2024
}

print(book["title"])
print(book["author"])
print(book["year"])
print(book.get("isbn", "ISBN not available"))
```

-   `book` stores three named fields as key-value pairs.
-   `book["title"]`, `book["author"]`, and `book["year"]` directly
    retrieve values for keys that exist.
-   `book.get("isbn", "ISBN not available")` safely handles the missing
    key. It prints the supplied default instead of raising `KeyError`.

Expected output:

``` text
Python Basics
Alex
2024
ISBN not available
```

## Exercise 2 --- Update stock and add a new product

``` python
stock = {"pens": 100, "notebooks": 40}
stock["pens"] -= 15
print(stock)

stock["erasers"] = 60
print(stock)
```

-   The dictionary starts with 100 pens and 40 notebooks.
-   `stock["pens"] -= 15` subtracts 15 from the existing value and
    stores 85 under `"pens"`.
-   `print(stock)` shows the updated dictionary.
-   `stock["erasers"] = 60` adds a new key because `"erasers"` was not
    present.
-   The final print shows all three products.

Expected output:

``` text
{'pens': 85, 'notebooks': 40}
{'pens': 85, 'notebooks': 40, 'erasers': 60}
```

## Exercise 3 --- Safely remove a setting

``` python
settings = {"volume": 70, "brightness": 50}
removed_value = settings.pop("volume", "setting not found")

print(removed_value)
print(settings)
```

-   `settings` starts with two entries.
-   `.pop("volume", "setting not found")` removes `"volume"` and returns
    its value, 70.
-   If `"volume"` were absent, it would return the fallback instead of
    raising `KeyError`.
-   The first print displays the removed value; the second displays the
    remaining dictionary.

Expected output:

``` text
70
{'brightness': 50}
```

## Exercise 4 --- Count letters in "mississippi"

``` python
word = "mississippi"
letter_counts = {}

for letter in word:
    if letter in letter_counts:
        letter_counts[letter] += 1
    else:
        letter_counts[letter] = 1

print(letter_counts)
```

-   `word` contains the characters to count.
-   `letter_counts = {}` starts an empty dictionary.
-   `for letter in word` visits each character, including repeated
    characters.
-   `if letter in letter_counts` checks whether that character has
    already been counted.
-   If it exists, `+= 1` increases its count.
-   Otherwise, the `else` branch creates the key with its first count of
    1.

Expected output:

``` text
{'m': 1, 'i': 4, 's': 4, 'p': 2}
```

## Exercise 5 --- Demonstrate aliasing and copying

``` python
original = {"name": "Ada"}
alias = original
alias["city"] = "London"

print(original)
print(alias)

copy_dict = original.copy()
copy_dict["role"] = "Programmer"

print(original)
print(copy_dict)
```

-   `original` creates a dictionary.
-   `alias = original` does not copy it; both names refer to the same
    dictionary.
-   Adding `"city"` through `alias` therefore changes what `original`
    displays too.
-   `original.copy()` creates a separate top-level dictionary.
-   Adding `"role"` to `copy_dict` does not add it to `original`.

Expected output:

``` text
{'name': 'Ada', 'city': 'London'}
{'name': 'Ada', 'city': 'London'}
{'name': 'Ada', 'city': 'London'}
{'name': 'Ada', 'city': 'London', 'role': 'Programmer'}
```

This is a shallow copy: if a value inside the dictionary were itself a
mutable list, that inner list would still be shared.

## Exercise 6 --- Iterate over a user dictionary with `.items()`

``` python
user = {
    "name": "Grace",
    "email": "grace@example.com",
    "active": True
}

for field, value in user.items():
    print(f"{field}: {value}")
```

-   `user` stores three fields.
-   `.items()` provides each key-value pair.
-   `field, value` unpacks each pair into two variables.
-   The f-string prints the key, a colon, and its value.

Expected output:

``` text
name: Grace
email: grace@example.com
active: True
```

------------------------------------------------------------------------

# Completion checklist

-   [ ] I can create empty and populated dictionaries.
-   [ ] I understand keys, values, uniqueness, and hashability.
-   [ ] I can explain `KeyError` and choose between direct lookup and
    `.get()`.
-   [ ] I can add, update, delete, and safely remove entries.
-   [ ] I know `in` checks keys.
-   [ ] I can iterate over keys, values, and `.items()`.
-   [ ] I understand insertion order, aliasing, and shallow copying.
-   [ ] I can explain the dictionary methods and related operations in
    the appendix.
-   [ ] I have run all six exercises and checked their outputs.
