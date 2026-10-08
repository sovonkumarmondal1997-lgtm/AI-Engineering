# Practice Questions: Python Core Language and Data Types

These 20 practice questions let you rehearse everything taught in Topics
01–10 of this module: the interpreter and indentation, variables and basic
types, operators and precedence, strings, lists, tuples, dictionaries,
sets, type conversion and truthiness, and mutability. Every question uses
**only** ideas already taught here or in Module 1.1 — nothing from later
modules (no files, databases, APIs, classes, decorators, or external
libraries).

Each question follows the same shape: read the problem, think about the
requirements and edge cases yourself, plan an approach in plain English,
*then* look at the solution. Try to solve each one yourself before reading
its solution — that is where the actual learning happens.

## Table of Contents

- [Basic Questions (1–5)](#basic-questions)
- [Moderate Questions (6–10)](#moderate-questions)
- [Hard Questions (11–15)](#hard-questions)
- [Advanced Questions (16–20)](#advanced-questions)

---

## Basic Questions

### Question 1 — Basic

#### Problem statement

Create variables describing a person: their full name, their age, their
height in meters, whether they are currently a student, and their middle
name (which they have not told you, so it should represent "no value has
been provided or assigned for this field"). Print each value together
with its type.

#### Concepts practised

Comments, indentation, variables with meaningful names, the `int`,
`float`, `bool`, `str`, and `None` types, and `type()` (Topics 1 and 2).

#### Requirements and expected output

- Create five variables, one of each type listed above, with clear,
  descriptive names (not `x`, `y`, `a`).
- The middle name is not known yet — use the value that means "no value
  has been provided," not an empty string.
- Print each value alongside `type(...)` applied to it, one line per
  variable.

#### Edge cases to consider

- `None` is not the same as `0`, `False`, or `""` — using any of those
  instead of `None` would claim something false (for example, that the
  middle name is known to be blank).
- A `float` still counts as a `float` even if it looks like a whole
  number (for example, `1.68` clearly has a decimal part, but a value
  like `2.0` would still be a `float`, not an `int`).

#### Solution approach

1. Assign the full name to a `str` variable, the age to an `int`
   variable, the height to a `float` variable, and the student flag to a
   `bool` variable.
2. Assign the middle name to `None`, since it genuinely has not been
   provided.
3. Print each variable together with `type()` of that same variable, one
   `print()` call per variable, using an f-string.

#### Complete runnable Python solution

```python
# This program stores a few basic facts about a person and shows
# each value together with its type.

full_name = "Maria Alvarez"      # str: the person's full name
age = 21                          # int: whole number of years
height_m = 1.68                   # float: height in meters, has a decimal point
is_student = True                 # bool: True/False fact
middle_name = None                # None: we do not know this yet

print(f"{full_name} ({type(full_name)})")
print(f"{age} ({type(age)})")
print(f"{height_m} ({type(height_m)})")
print(f"{is_student} ({type(is_student)})")
print(f"{middle_name} ({type(middle_name)})")
```

#### Explanation

- Five variables are created, one per basic type this module covers, each
  with a name that describes what it holds — this is the "meaningful
  names" habit from Topic 2.
- `middle_name = None` deliberately represents "not known yet," not an
  empty string — a completely different claim.
- Each `print(f"{value} ({type(value)})")` shows the value and its type
  side by side, using an f-string exactly as taught in Topic 4 (formally)
  and previewed in Topic 2.
- The comments (starting with `#`) explain what each variable is for, but
  are completely ignored by the interpreter, exactly as Topic 1 explained.

#### Example output

```text
Maria Alvarez (<class 'str'>)
21 (<class 'int'>)
1.68 (<class 'float'>)
True (<class 'bool'>)
None (<class 'NoneType'>)
```

#### Why this solution works

Each variable is assigned a value whose type matches what is being
described, and `type()` is a safe, side-effect-free way to confirm this —
it never changes the value, it only reports on it. Because `None` is a
distinct, real value (not a "missing" `str` or a zero `int`), printing it
shows `None` and `<class 'NoneType'>`, exactly as Topic 2 described.

#### Common beginner mistakes

- Using `""` (empty string) instead of `None` for the middle name, which
  incorrectly claims "the middle name is known to be blank."
- Writing `height_m = 168` (an `int`) when a `float` was intended — always
  include the decimal point for measurements that could have a fractional
  part.
- Using vague names like `a`, `b`, `c` instead of names that describe what
  each variable represents.

#### Optional improvement challenge

Add a sixth variable for the person's favorite number, deliberately set to
`0`, and print it with its type too — then, in a comment, explain in one
sentence why `0` is a real, meaningful value and not the same thing as
`None`.

---

### Question 2 — Basic

#### Problem statement

A customer buys 3 items priced at $12.50 each. Shipping costs a flat $5,
and there is a 10% discount that applies only to the cost of the items
(not to shipping). Compute and print the items' total, the discount
amount, and the final price the customer pays.

#### Concepts practised

Arithmetic operators and operator precedence (Topic 3), f-string number
formatting (Topic 4).

#### Requirements and expected output

- Store the unit price, quantity, shipping fee, and discount rate in
  clearly named variables.
- Compute the items' total, the discount amount (10% of the items' total
  only), and the final price (items' total minus the discount, plus
  shipping).
- Print all three amounts formatted as currency with exactly two decimal
  places.

#### Edge cases to consider

- The discount must be applied to the items' total *before* shipping is
  added — applying it after adding shipping would (incorrectly) discount
  the shipping fee too.
- `unit_price * quantity` must be computed before subtracting the
  discount; use parentheses or separate variables to make the order
  unambiguous, rather than relying purely on memorized precedence rules.

#### Solution approach

1. Store the four given facts (unit price, quantity, shipping fee,
   discount rate) as separate variables.
2. Compute the items' total by multiplying price by quantity.
3. Compute the discount amount from the items' total alone.
4. Compute the final price as items' total minus discount, plus shipping.
5. Print all three amounts using the `.2f` format specifier.

#### Complete runnable Python solution

```python
# Work out the final price of an order: 3 items at $12.50 each,
# with a flat $5 shipping fee, then a 10% discount on the item total only.

unit_price = 12.50
quantity = 3
shipping_fee = 5
discount_rate = 0.10

items_total = unit_price * quantity
discount_amount = items_total * discount_rate
final_price = items_total - discount_amount + shipping_fee

print(f"Items total: ${items_total:.2f}")
print(f"Discount: ${discount_amount:.2f}")
print(f"Final price: ${final_price:.2f}")
```

#### Explanation

- `items_total = unit_price * quantity` multiplies first, computing
  `12.50 * 3 = 37.5`, before anything else happens — storing this in its
  own variable avoids relying on precedence to get the order right later.
- `discount_amount = items_total * discount_rate` computes 10% of the
  items' total alone: `37.5 * 0.10 = 3.75`.
- `final_price = items_total - discount_amount + shipping_fee` subtracts
  the discount from the items' total, then adds shipping:
  `37.5 - 3.75 + 5 = 38.75`. Addition and subtraction run left to right
  when their precedence is equal, so this reads exactly as intended.
- Each `print(...)` uses an f-string with the `.2f` format specifier from
  Topic 4 to always show exactly two decimal places, like real currency.

#### Example output

```text
Items total: $37.50
Discount: $3.75
Final price: $38.75
```

#### Why this solution works

Breaking the calculation into three named, sequential steps — items'
total, then discount, then final price — makes the order of operations
explicit through the *structure* of the code, rather than depending on a
single, harder-to-read expression and precedence rules. This mirrors
Topic 3's own advice: when there is any doubt about order, make it
unambiguous rather than relying on memorized precedence.

#### Common beginner mistakes

- Adding shipping before applying the discount, which would incorrectly
  discount part of the shipping fee too.
- Using `/` instead of `*` when computing 10% of a total (`* 0.10`, not
  `/ 0.10`).
- Forgetting the `.2f` format specifier and getting a number of decimal
  places that is not fixed at two in the output.

#### Optional improvement challenge

Add a second discount: an extra flat $2 off if `items_total` is greater
than $30. Compute this using a comparison operator and an `if` statement,
and adjust `final_price` accordingly.

---

### Question 3 — Basic

#### Problem statement

Given the word `"backpropagation"`, extract and print: its first letter,
its last letter, its first four letters, the five letters right after
those, and the entire word reversed.

#### Concepts practised

String indexing (positive and negative) and slicing (Topic 4).

#### Requirements and expected output

- Use indexing (not slicing) to get the first and last letters.
- Use slicing for the first four letters, the middle five letters, and the
  reversed word.
- Print all five results, one per line.

#### Edge cases to consider

- Negative indexing (`word[-1]`) is often clearer than computing
  `word[len(word) - 1]` by hand — prefer it for "the last character."
- Slicing's `stop` value is always excluded, so the "next five letters"
  after the first four must start at index `4` and stop at index `9`
  (`word[4:9]`), not `word[4:8]`.
- `word[::-1]` reverses the whole string in one step; no loop is needed.

#### Solution approach

1. Store the word in a variable.
2. Use `word[0]` and `word[-1]` for the first and last letters.
3. Use `word[:4]` for the first four letters.
4. Use `word[4:9]` for the next five letters.
5. Use `word[::-1]` to reverse the entire word.
6. Print each result.

#### Complete runnable Python solution

```python
word = "backpropagation"

first_letter = word[0]
last_letter = word[-1]
first_four = word[:4]
middle_slice = word[4:9]
reversed_word = word[::-1]

print(first_letter)
print(last_letter)
print(first_four)
print(middle_slice)
print(reversed_word)
```

#### Explanation

- `word[0]` reads the character at index `0`, the very first letter,
  `"b"`. `word[-1]` counts backward from the end, giving the last letter,
  `"n"`.
- `word[:4]` omits `start` (meaning "from the beginning") and stops before
  index `4`, giving the four letters `"back"`.
- `word[4:9]` starts at index `4` and stops before index `9`, giving the
  five letters `"propa"` — indexes `4, 5, 6, 7, 8`.
- `word[::-1]` omits both `start` and `stop` (meaning "the whole string")
  and uses a step of `-1` to walk backward, producing the fully reversed
  word.

#### Example output

```text
b
n
back
propa
noitagaporpkcab
```

#### Why this solution works

Each extraction uses exactly the indexing or slicing rule that fits the
task: a single position for one character, a range for several
consecutive characters, and a full negative-step slice for reversal.
String slicing returns a string result without modifying the original
string, so none of these operations affect `word` itself or each other.

#### Common beginner mistakes

- Writing `word[4:8]` instead of `word[4:9]`, forgetting that the stop
  index is excluded, and getting only four letters instead of five.
- Trying to reverse a string with `word[-1:0]` or similar, instead of the
  idiomatic `word[::-1]`.
- Forgetting that `word[-1]` is a position (a single character), not a
  slice — `word[-1:]` would instead return a one-character *slice*, which
  looks identical when printed but is a different operation.

#### Optional improvement challenge

Using only what you have learned so far, write one more slice that
extracts every second letter of `"backpropagation"` (hint: think about the
step value), and print it.

---

### Question 4 — Basic

#### Problem statement

Start with a list of three favorite movies. Add a fourth movie to the end
of the list, then replace the second movie with a different title. Print
the final list, the first movie (by indexing), the last movie (using a
negative index), and how many movies are in the list.

#### Concepts practised

List creation, `.append()`, replacing an item by index, negative
indexing, and `len()` (Topic 5).

#### Requirements and expected output

- Start with a list of exactly three movie titles.
- Use `.append()` to add a fourth title to the end.
- Replace the item at index `1` with a new title, using direct index
  assignment (not `.append()` or `.remove()`).
- Print the whole list, the first item, the last item, and the length.

#### Edge cases to consider

- `.append()` always adds to the *end*, regardless of how many items are
  already there — do not confuse it with `.insert()`.
- Replacing by index (`movies[1] = ...`) is a mutation, not a
  reassignment of the whole list — the list keeps the same identity, only
  one slot changes.
- The last item should be read with `movies[-1]`, not a hardcoded index
  like `movies[3]`, so the code still works if the list's length changes
  later.

#### Solution approach

1. Create the list with three titles.
2. Call `.append(...)` to add a fourth title.
3. Assign a new value to index `1` to replace the second title.
4. Print the list, then `movies[0]`, then `movies[-1]`, then `len(movies)`.

#### Complete runnable Python solution

```python
favorite_movies = ["Arrival", "Coco", "Spirited Away"]

favorite_movies.append("The Matrix")
favorite_movies[1] = "Inside Out"

print(favorite_movies)
print(favorite_movies[0])
print(favorite_movies[-1])
print(len(favorite_movies))
```

#### Explanation

- `favorite_movies.append("The Matrix")` mutates the list in place,
  adding one new element to the end, without ever reassigning the
  variable — exactly the pattern Topic 5 introduced.
- `favorite_movies[1] = "Inside Out"` replaces whatever was previously at
  index `1` (`"Coco"`) with a new title, using direct index assignment —
  this is possible only because lists are mutable.
- `favorite_movies[0]` reads the first item without removing it;
  `favorite_movies[-1]` reads the last item, whatever the list's current
  length happens to be.
- `len(favorite_movies)` reports the current number of elements, `4`,
  after both changes.

#### Example output

```text
['Arrival', 'Inside Out', 'Spirited Away', 'The Matrix']
Arrival
The Matrix
4
```

#### Why this solution works

`.append()` and index assignment are both legal only because lists are
mutable (Topic 5); each operation changes the *same* list object in
place, so there is exactly one `favorite_movies` list throughout, and
every later `print()` sees all previous changes.

#### Common beginner mistakes

- Using `.insert(1, ...)` when the goal was to *replace* an item, which
  would add a fifth item instead of replacing the second one.
- Hardcoding `favorite_movies[3]` to mean "the last movie," which breaks
  the moment the list's length changes.
- Forgetting that `.append()` returns `None` — writing
  `favorite_movies = favorite_movies.append(...)` would destroy the list.

#### Optional improvement challenge

Add a line that removes `"Spirited Away"` from the list using `.remove()`,
and print the list again to confirm it is gone.

---

### Question 5 — Basic

#### Problem statement

A geographic coordinate is stored as a tuple of `(latitude, longitude)`.
Unpack it into two clearly named variables and print each one. Separately,
swap the values of two variables holding city names, using the one-line
swap technique, and print the result.

#### Concepts practised

Tuple creation and unpacking, the one-line variable swap (Topic 6).

#### Requirements and expected output

- Store a coordinate as a two-item tuple.
- Unpack it into `latitude` and `longitude` in a single statement.
- Print both values with clear labels.
- Swap two city-name variables using tuple unpacking, with no temporary
  variable, and print both afterward.

#### Edge cases to consider

- The number of variables on the left of an unpacking statement must
  exactly match the number of values in the tuple, or Python raises
  `ValueError`.
- The swap must use exactly the `a, b = b, a` pattern — using a manual
  three-line swap would still work, but does not demonstrate packing and
  unpacking, which is the point of this exercise.

#### Solution approach

1. Create a tuple holding the latitude and longitude.
2. Unpack it into two variables in one line.
3. Print both, clearly labeled.
4. Create two variables for city names, then swap them using
   `a, b = b, a`.
5. Print both city variables afterward to show the swap worked.

#### Complete runnable Python solution

```python
location = (28.6139, 77.2090)

latitude, longitude = location
print(f"Latitude: {latitude}")
print(f"Longitude: {longitude}")

city_a = "Delhi"
city_b = "Tokyo"
city_a, city_b = city_b, city_a
print(city_a, city_b)
```

#### Explanation

- `location = (28.6139, 77.2090)` packs two related values into one
  tuple, a natural fit for a coordinate that should not be edited
  piece-by-piece by accident.
- `latitude, longitude = location` unpacks the tuple's two values into two
  clearly named variables in a single statement.
- `city_a, city_b = city_b, city_a` first packs the *current* values of
  `city_b` and `city_a` into a temporary tuple, `("Tokyo", "Delhi")`,
  before assigning anything — which is exactly why no temporary variable
  is needed to swap them safely.
- The final `print(city_a, city_b)` confirms the swap: `city_a` now holds
  `"Tokyo"` and `city_b` now holds `"Delhi"`.

#### Example output

```text
Latitude: 28.6139
Longitude: 77.209
Tokyo Delhi
```

#### Why this solution works

Unpacking assigns each tuple value to a variable by position, and because
Python fully evaluates the right-hand side of an assignment before
changing any names on the left, the swap never risks reading an
already-overwritten value — exactly as Topic 6 explained.

#### Common beginner mistakes

- Writing `latitude, longitude, elevation = location` when `location`
  only has two values, causing `ValueError: not enough values to unpack`.
- Attempting to swap with `city_a = city_b` followed by `city_b = city_a`,
  which loses the original value of `city_a` before it can be assigned to
  `city_b`.
- Forgetting that `77.2090` prints as `77.209` — Python does not keep a
  trailing zero that adds no value to a `float`.

#### Optional improvement challenge

Add a third value, elevation in meters, to the tuple, and update the
unpacking statement to capture all three values in one line.

---

## Moderate Questions

### Question 6 — Moderate

#### Problem statement

A user typed their name and email into a form carelessly: extra spaces
around both, and inconsistent capitalization. Clean both values (title
case for the name, lowercase for the email), then print them neatly
formatted, including the cleaned name inside a fixed-width, left-aligned
field.

#### Concepts practised

String cleanup with `.strip()`, `.title()`, and `.lower()`, combined with
f-string formatting and alignment (Topic 4).

#### Requirements and expected output

- Start from messy raw text with leading/trailing spaces and inconsistent
  case.
- Produce a cleaned name in title case and a cleaned email in lowercase.
- Print both cleaned values, then print the cleaned name inside a
  left-aligned field at least 20 characters wide, alongside its length.

#### Edge cases to consider

- `.strip()` only removes leading and trailing whitespace — it does not
  touch spaces in the middle of a name, which should stay.
- Cleaning must happen in the right order: stripping first, *then*
  changing case, produces the same result here, but get in the habit of
  stripping raw input before doing anything else with it.
- `len(...)` should be measured on the *cleaned* name, not the original
  messy text, since that is the value that matters going forward.

#### Solution approach

1. Store the raw, messy name and email in variables.
2. Build the cleaned name with `.strip().title()`.
3. Build the cleaned email with `.strip().lower()`.
4. Print both cleaned values.
5. Print the cleaned name inside a 20-character left-aligned field next to
   its length, using an f-string format specifier.

#### Complete runnable Python solution

```python
raw_name = "  ada LOVELACE  "
raw_email = "  ADA@Example.COM "

clean_name = raw_name.strip().title()
clean_email = raw_email.strip().lower()

print(f"Name:  {clean_name}")
print(f"Email: {clean_email}")
print(f"[{clean_name:<20}] length={len(clean_name)}")
```

#### Explanation

- `raw_name.strip().title()` first removes the leading and trailing
  spaces, then capitalizes the first letter of each remaining word,
  turning `"  ada LOVELACE  "` into `"Ada Lovelace"`. Method calls chain
  left to right: `.strip()` runs first, and `.title()` runs on *its*
  result.
- `raw_email.strip().lower()` similarly trims whitespace, then lowercases
  everything, turning the messy email into `"ada@example.com"`.
- The two `print(f"Name:  {clean_name}")` and `print(f"Email:
  {clean_email}")` lines show the cleaned results directly.
- `f"[{clean_name:<20}] length={len(clean_name)}"` uses the `<20` format
  specifier from Topic 4 to left-align `clean_name` inside a 20-character
  field, padding with spaces, and reports its true length, `12`.

#### Example output

```text
Name:  Ada Lovelace
Email: ada@example.com
[Ada Lovelace        ] length=12
```

#### Why this solution works

The string-cleaning methods used here return strings rather than
modifying the original string in place (Topic 4), so chaining
`.strip().title()` and `.strip().lower()` safely builds a fully cleaned value in one expression,
without ever needing an intermediate variable — and the original
`raw_name`/`raw_email` values are left completely untouched, in case they
are needed again.

#### Common beginner mistakes

- Calling `.title()` before `.strip()` accidentally, which usually still
  works, but relying on that would produce different results if a string
  had non-space whitespace, such as a leading tab.
- Forgetting that `text.strip()` alone does nothing to `text` — the
  result must be captured or chained, as this solution does.
- Measuring `len(raw_name)` instead of `len(clean_name)`, which would
  include the extra spaces that were supposed to be removed.

#### Optional improvement challenge

Add a check using `.isalpha()` (ignoring the space between first and last
name) to confirm the cleaned name contains only letters and spaces, and
print a warning if it does not.

---

### Question 7 — Moderate

#### Problem statement

A list holds three ages typed as text, such as `["25", "31", "19"]`.
Convert them to numbers and compute the average age. Separately, given a
list of form field values, some of which are empty or zero, determine
whether *all* fields were filled in and whether *at least one* field was
filled in, without writing a manual `==` comparison for each value.

#### Concepts practised

Explicit type conversion with `int()`, truthiness, `bool()`, `any()`, and
`all()` (Topic 9).

#### Requirements and expected output

- Convert each text age to an `int` and compute the average as a `float`
  with one decimal place.
- Build a list of `True`/`False` flags from the form values using
  `bool(...)`, then summarize it with `any()` and `all()`.

#### Edge cases to consider

- `raw_ages` values are text; adding them directly without converting
  first would raise a `TypeError`.
- The form-values list intentionally includes `""` (falsy) and `0`
  (falsy, even though it is a "real" number) to show that truthiness
  treats every falsy value the same way, for better or worse.

#### Solution approach

1. Loop over the text ages, convert each with `int()`, and accumulate a
   running total.
2. Divide the total by the count to get the average, and format it to one
   decimal place.
3. Loop over the form values, convert each to `bool(...)`, and collect the
   results in a list.
4. Use `all(...)` and `any(...)` on that list to summarize it.

#### Complete runnable Python solution

```python
raw_ages = ["25", "31", "19"]

total_age = 0
for raw_age in raw_ages:
    total_age += int(raw_age)

average_age = total_age / len(raw_ages)
print(f"Average age: {average_age:.1f}")

form_values = ["Ada", "", "555-0142", 0]
filled_flags = []
for value in form_values:
    filled_flags.append(bool(value))

print(filled_flags)
print(f"All filled: {all(filled_flags)}")
print(f"At least one filled: {any(filled_flags)}")
```

#### Explanation

- `total_age += int(raw_age)` explicitly converts each text age to an
  `int` before adding it — without `int(...)`, this would try to add a
  `str` to an `int` and fail.
- `average_age = total_age / len(raw_ages)` uses ordinary division; the
  `.1f` format specifier then displays it with exactly one decimal place.
- `bool(value)` applies truthiness to each form value: `"Ada"` and
  `"555-0142"` are non-empty strings (truthy); `""` is an empty string
  (falsy); `0` is numeric zero (falsy) — giving
  `[True, False, True, False]`.
- `all(filled_flags)` is `False` because not every value was truthy;
  `any(filled_flags)` is `True` because at least one was.

#### Example output

```text
Average age: 25.0
[True, False, True, False]
All filled: False
At least one filled: True
```

#### Why this solution works

Converting explicitly with `int()` guarantees the arithmetic works on
real numbers, not text, avoiding the `TypeError` that direct arithmetic on
strings would raise. Applying `bool(...)` to each form value reuses
Python's built-in truthiness rules instead of writing four separate `==`
comparisons, and `any()`/`all()` summarize the resulting list in one
readable step each.

#### Common beginner mistakes

- Trying `total_age += raw_age` without converting to `int` first, which
  raises `TypeError: unsupported operand type(s) for +=: 'int' and
  'str'`.
- Assuming `0` in the form values means "not filled in" is the same
  concept as `""` — they are both falsy, but they are different values
  with different meanings, a distinction covered directly in Topic 9.
- Confusing `any()` (at least one truthy) with `all()` (every one
  truthy) — reading each function's name carefully avoids this.

#### Optional improvement challenge

Add a fifth form value, the text `"0"`, to `form_values`, predict whether
`bool("0")` is `True` or `False` before running it, and explain the result
in one sentence (hint: it is a non-empty string).

---

### Question 8 — Moderate

#### Problem statement

A dictionary maps grocery product names to their prices. Look up the
price of a product that exists, then safely look up a product that does
not exist — once with no default (getting `None`), and once with a
sensible default of `0.0`. Then compute the total cost of a shopping list
that might include a product not found in the price dictionary.

#### Concepts practised

Dictionary creation and safe lookups with `.get()`, including a custom
default (Topic 7).

#### Requirements and expected output

- Look up an existing product directly with `.get()`.
- Look up a missing product with `.get()` and no default, and again with a
  default of `0.0`.
- Loop over a shopping list, safely adding up prices even for a product
  that is not in the dictionary.

#### Edge cases to consider

- Using direct lookup (`prices["cheese"]`) on a missing key would raise
  `KeyError` and crash the program — `.get()` avoids this entirely.
- `.get("cheese")` with no default returns `None`, not `0` — printing it
  should show `None`, not an error or a zero.
- The shopping list total must not fail just because one item is not
  stocked; it should simply contribute `0.0` for that item.

#### Solution approach

1. Create a dictionary of products and prices.
2. Use `.get()` to look up an existing product.
3. Use `.get()` on a missing product with no default, then with a default
   of `0.0`.
4. Loop over a shopping list, using `.get(item, 0.0)` for each item, and
   accumulate a running total.
5. Print the total formatted as currency.

#### Complete runnable Python solution

```python
prices = {"apple": 0.50, "bread": 2.75, "milk": 1.90}

print(prices.get("bread"))
print(prices.get("cheese"))
print(prices.get("cheese", 0.0))

shopping_list = ["apple", "cheese", "milk"]
total_cost = 0.0
for item in shopping_list:
    total_cost += prices.get(item, 0.0)

print(f"Total cost: ${total_cost:.2f}")
```

#### Explanation

- `prices.get("bread")` finds `"bread"` in the dictionary and returns its
  price, `2.75`, exactly like direct lookup would, but without any risk of
  `KeyError`.
- `prices.get("cheese")` looks for a key that does not exist and, with no
  default given, returns `None` — a real, printable value meaning "not
  found."
- `prices.get("cheese", 0.0)` performs the same lookup but returns `0.0`
  instead of `None`, since a fallback was explicitly supplied.
- The loop adds up each shopping-list item's price using
  `prices.get(item, 0.0)`, so `"cheese"` (not stocked) safely contributes
  `0.0` to the running total instead of crashing the program: `0.50 + 0.0
  + 1.90 = 2.40`.

#### Example output

```text
2.75
None
0.0
Total cost: $2.40
```

#### Why this solution works

`.get()` treats a missing key as a normal, expected possibility rather
than an error, matching Topic 7's guidance to prefer `.get()` whenever a
missing key is something the program should handle gracefully, not treat
as a bug. Supplying `0.0` as the default specifically for the total-cost
loop means "an unstocked item costs nothing," a deliberate, sensible
choice rather than an accident.

#### Common beginner mistakes

- Using `prices["cheese"]` directly, which raises `KeyError: 'cheese'`
  and stops the whole program.
- Assuming `.get("cheese")` with no default returns `0` — it returns
  `None`, which is a different value with a different meaning.
- Forgetting to supply a default inside the loop, causing the total-cost
  calculation to crash on the very first unstocked item.

#### Optional improvement challenge

Add an `if "eggs" in prices:` check before looking eggs up directly, as an
alternative style to `.get()`, and explain in a comment which of the two
approaches you find clearer here.

---

### Question 9 — Moderate

#### Problem statement

A list of tag submissions contains many repeats, such as
`["python", "ai", "python", "beginner", "ai", "python"]`. Find how many
*distinct* tags were submitted, list them in alphabetical order, and check
whether `"ml"` and `"python"` were among them.

#### Concepts practised

Converting a list to a set to remove duplicates, membership checks with
`in`, and `sorted()` for predictable display order (Topic 8).

#### Requirements and expected output

- Convert the list of tags into a set to find the unique ones.
- Print the unique tags in a predictable (sorted) order.
- Print how many total submissions there were and how many unique tags
  there were.
- Check membership for a tag that was not submitted and one that was.

#### Edge cases to consider

- The set's own printed order is not guaranteed and should not be relied
  upon — use `sorted(...)` whenever a predictable display order matters.
- `len(submitted_tags)` (with duplicates) and `len(unique_tags)` (without)
  answer two different questions and should not be confused.

#### Solution approach

1. Store the raw list of tag submissions, including repeats.
2. Convert it to a set to collapse duplicates automatically.
3. Print the sorted unique tags.
4. Print the total submission count and the unique tag count.
5. Check membership of `"ml"` and `"python"` using `in`.

#### Complete runnable Python solution

```python
submitted_tags = ["python", "ai", "python", "beginner", "ai", "python"]

unique_tags = set(submitted_tags)

print(sorted(unique_tags))
print(f"Total submissions: {len(submitted_tags)}")
print(f"Unique tags: {len(unique_tags)}")
print("ml" in unique_tags)
print("python" in unique_tags)
```

#### Explanation

- `set(submitted_tags)` builds a set from the list, automatically keeping
  only one copy of each distinct value — `"python"` and `"ai"`, each
  submitted multiple times, appear only once in `unique_tags`.
- `sorted(unique_tags)` returns a new, alphabetically ordered **list**,
  giving a predictable, printable order: `['ai', 'beginner', 'python']`.
- `len(submitted_tags)` counts every submission, including repeats: `6`.
  `len(unique_tags)` counts only the distinct tags: `3` — this contrast is
  exactly why sets are useful here.
- `"ml" in unique_tags` is `False` (never submitted); `"python" in
  unique_tags` is `True`.

#### Example output

```text
['ai', 'beginner', 'python']
Total submissions: 6
Unique tags: 3
False
True
```

#### Why this solution works

A set is exactly the right tool for "how many distinct things are there,"
because it enforces uniqueness automatically, with no extra code needed
(Topic 8), and its membership checks (`in`) are the same clean syntax
already used for lists and dictionaries.

#### Common beginner mistakes

- Printing `unique_tags` directly and expecting a consistent order across
  runs, instead of wrapping it in `sorted(...)`.
- Confusing `len(submitted_tags)` with `len(unique_tags)` and reporting
  the wrong count for "how many distinct tags."
- Trying to index into a set, such as `unique_tags[0]`, which raises
  `TypeError`, since sets do not support indexing.

#### Optional improvement challenge

Given a second list of tags submitted the next day, convert it to a set
too, and print which tags were submitted on *both* days using
intersection.

---

### Question 10 — Moderate

#### Problem statement

Start with a playlist of three songs. Assign it to a second variable name
and add a song through that second name — notice the first name shows the
new song too. Then make a genuine, independent copy of the (now four-song)
playlist, add a different song through the copy, and confirm the original
is unaffected this time.

#### Concepts practised

List aliasing versus `.copy()` (Topic 5), reinforced by the "labels on
boxes" model (Topic 10).

#### Requirements and expected output

- Create a playlist, assign it to a second name (an alias, not a copy),
  and mutate through the second name.
- Print both names to show the change appears through both.
- Make a real copy with `.copy()`, mutate the copy, and print both again
  to show the original is now unaffected.

#### Edge cases to consider

- `playlist_alias = playlist_original` does not create a second list —
  both names point at the exact same object, so mutating either one
  affects what both names show.
- `.copy()` must be called *after* the alias mutation in this exercise,
  so the copy correctly starts from the four-song version, not the
  original three-song version.

#### Solution approach

1. Create the original three-song playlist.
2. Assign it to `playlist_alias` (no `.copy()` here — this is the alias).
3. Append a song through `playlist_alias` and print both names.
4. Create `playlist_copy` using `.copy()`.
5. Append a different song through `playlist_copy` and print both names
   again.

#### Complete runnable Python solution

```python
playlist_original = ["Song A", "Song B", "Song C"]

playlist_alias = playlist_original
playlist_alias.append("Song D")
print("original after alias mutation:", playlist_original)
print("alias:", playlist_alias)

playlist_copy = playlist_original.copy()
playlist_copy.append("Song E")
print("original after copy mutation:", playlist_original)
print("copy:", playlist_copy)
```

#### Explanation

- `playlist_alias = playlist_original` does not copy anything — it gives
  the *same* list a second name.
- `playlist_alias.append("Song D")` mutates that one shared list. Because
  `playlist_original` and `playlist_alias` are two labels on the same
  object, printing `playlist_original` afterward shows `"Song D"` too,
  even though the code never wrote `playlist_original.append(...)`
  directly.
- `playlist_copy = playlist_original.copy()` finally builds a genuinely
  independent list, starting from the current four-song version.
- `playlist_copy.append("Song E")` only grows `playlist_copy`; printing
  `playlist_original` afterward confirms it still has exactly four songs,
  unaffected this time.

#### Example output

```text
original after alias mutation: ['Song A', 'Song B', 'Song C', 'Song D']
alias: ['Song A', 'Song B', 'Song C', 'Song D']
original after copy mutation: ['Song A', 'Song B', 'Song C', 'Song D']
copy: ['Song A', 'Song B', 'Song C', 'Song D', 'Song E']
```

#### Why this solution works

The two halves of this program directly contrast aliasing and copying, so
the difference is visible rather than assumed: the first mutation shows up
through *both* names because there was only ever one list, while the
second mutation shows up through only *one* name because `.copy()`
genuinely built a second, separate list object.

#### Common beginner mistakes

- Assuming `playlist_alias = playlist_original` created a second,
  independent playlist — it did not.
- Calling `.copy()` at the very start (before "Song D" was added) and then
  being confused when the copy is missing that song — the copy only
  reflects the list's contents at the moment `.copy()` was called.
- Assigning the result of `.append(...)` to a variable, which would
  destroy the list, since `.append()` always returns `None`.

#### Optional improvement challenge

Add a line using `is` to confirm, directly, that `playlist_original is
playlist_alias` is `True` while `playlist_original is playlist_copy` is
`False`.

---

## Hard Questions

### Question 11 — Hard

#### Problem statement

A classroom roster is represented as a list of small group lists, such as
`[["Ada", "Grace"], ["Alan"]]`. Make a shallow copy of it and show that
mutating a name *inside* one of the inner groups affects both the
original and the copy, while adding a whole new group to just the copy
does not affect the original. Then use `copy.deepcopy()` to make a copy whose
nested lists are independent and show that mutating an inner group through the deep
copy leaves the original completely untouched.

#### Concepts practised

Shallow copying of a nested list structure, and `copy.deepcopy()` as the
fix (Topic 5, reinforced in Topic 10).

#### Requirements and expected output

- Create a nested list (a list of lists).
- Make a shallow copy with `.copy()`.
- Mutate an inner list through the shallow copy and show it also changes
  the original.
- Append a whole new inner list to the shallow copy and show the original
  is unaffected by *that* particular change.
- Make a deep copy with `copy.deepcopy()`, mutate an inner list through
  it, and show the original is now unaffected.

#### Edge cases to consider

- A shallow copy protects the *outer* list (adding or removing whole
  groups on one copy does not affect the other) but does **not** protect
  the *inner* lists nested inside it — those are still the same shared
  objects.
- `copy.deepcopy()` must be imported from the standard library `copy`
  module before it can be used.

#### Solution approach

1. Create the nested classroom list.
2. Make a shallow copy with `.copy()`.
3. Mutate `shallow[0]` (an inner list) and print both the original and the
   shallow copy to show the shared mutation.
4. Append a brand-new inner list directly to the shallow copy, and print
   both again to show the outer lists are independent.
5. Import `copy`, make a deep copy of the (mutated) original, mutate an
   inner list through the deep copy, and print both to show they are now
   fully independent.

#### Complete runnable Python solution

```python
classroom = [["Ada", "Grace"], ["Alan"]]

shallow = classroom.copy()
shallow[0].append("Marie")
print("original after inner mutation:", classroom)
print("shallow copy:", shallow)

shallow.append(["Linus"])
print("original after outer append:", classroom)
print("shallow copy:", shallow)

import copy

deep = copy.deepcopy(classroom)
deep[0].append("Katherine")
print("original after deep-copy mutation:", classroom)
print("deep copy:", deep)
```

#### Explanation

- `shallow = classroom.copy()` copies only the *outer* list; `shallow[0]`
  is the exact same inner list object as `classroom[0]`.
- `shallow[0].append("Marie")` mutates that shared inner list, so both
  `classroom` and `shallow` show `"Marie"` added to the first group —
  this is the shallow-copy limitation from Topic 5.
- `shallow.append(["Linus"])` adds a brand-new inner list directly to the
  *outer* shallow-copied list, which really is independent — so
  `classroom` is unaffected by this particular change.
- `copy.deepcopy(classroom)` creates independent copies of the nested list
  objects in this example.
  `deep[0].append("Katherine")` now mutates a completely separate inner
  list, leaving `classroom` untouched.

#### Example output

```text
original after inner mutation: [['Ada', 'Grace', 'Marie'], ['Alan']]
shallow copy: [['Ada', 'Grace', 'Marie'], ['Alan']]
original after outer append: [['Ada', 'Grace', 'Marie'], ['Alan']]
shallow copy: [['Ada', 'Grace', 'Marie'], ['Alan'], ['Linus']]
original after deep-copy mutation: [['Ada', 'Grace', 'Marie'], ['Alan']]
deep copy: [['Ada', 'Grace', 'Marie', 'Katherine'], ['Alan']]
```

#### Why this solution works

The example deliberately separates two different kinds of change —
mutating something *inside* an existing inner list, versus adding a whole
new inner list to the outer list — because a shallow copy behaves
differently for each: shared for the first, independent for the second.
`deepcopy()` closes that gap in this example by creating independent
copies of the nested list objects, which is exactly why it exists.

#### Common beginner mistakes

- Believing `.copy()` fully protects a list of lists, and being surprised
  when mutating a nested group changes both the original and the copy.
- Forgetting `import copy` before calling `copy.deepcopy(...)`.
- Using `copy.deepcopy()` everywhere out of caution, even for flat lists
  with no nested mutable values, where a plain `.copy()` is already
  completely sufficient and clearer.

#### Optional improvement challenge

Add a `print(classroom[0] is shallow[0])` and a `print(classroom[0] is
deep[0])` line, predict both results before running them, and explain in
one sentence why they differ.

---

### Question 12 — Hard

#### Problem statement

A dictionary of raw application settings stores every value as text, such
as `{"max_retries": "5", "timeout": "30"}`, and may be missing some
settings entirely. Safely read three settings — `max_retries`, `timeout`,
and `max_connections` — using sensible text defaults for any that are
missing, then convert every one of them to a real `int` before using them.

#### Concepts practised

Safe dictionary lookup with `.get()` and a default, combined with explicit
type conversion using `int()` (Topics 7 and 9).

#### Requirements and expected output

- Two of the three settings exist in the dictionary as text; one
  (`max_connections`) does not.
- Every setting must end up as a real `int`, whether it came from the
  dictionary or from a default.
- Print each setting's value and its type to confirm the conversion
  worked.

#### Edge cases to consider

- `.get(key, default)`'s default must itself be text (a `str`) here, to
  match the "shape" of the values that are actually present in
  `raw_settings` — mixing a text default with text values, then
  converting everything together afterward, keeps the logic consistent.
- Converting *after* the `.get()` call (not before) means the same
  `int(...)` conversion step works correctly whether the value came from
  the dictionary or from the fallback default.

#### Solution approach

1. Create the dictionary of raw, text-based settings, missing one key on
   purpose.
2. For each of the three settings, call `.get()` with a sensible text
   default, then wrap the whole call in `int(...)`.
3. Print each resulting value together with its type.

#### Complete runnable Python solution

```python
raw_settings = {"max_retries": "5", "timeout": "30"}

max_retries = int(raw_settings.get("max_retries", "3"))
timeout = int(raw_settings.get("timeout", "10"))
max_connections = int(raw_settings.get("max_connections", "100"))

print(f"max_retries = {max_retries} ({type(max_retries)})")
print(f"timeout = {timeout} ({type(timeout)})")
print(f"max_connections = {max_connections} ({type(max_connections)})")
```

#### Explanation

- `raw_settings.get("max_retries", "3")` finds `"max_retries"` already
  present and returns its text value, `"5"`; `int(...)` then converts it
  to the real number `5`.
- `raw_settings.get("timeout", "10")` behaves the same way for the second
  present key, converting `"30"` to `30`.
- `raw_settings.get("max_connections", "100")` does **not** find
  `"max_connections"` in the dictionary at all, so it returns the text
  default `"100"` instead; `int(...)` converts that fallback exactly the
  same way, producing `100`.
- All three variables end up as real `int` values, regardless of whether
  they came from the dictionary or from a default — confirmed by
  `type(...)` in each printed line.

#### Example output

```text
max_retries = 5 (<class 'int'>)
timeout = 30 (<class 'int'>)
max_connections = 100 (<class 'int'>)
```

#### Why this solution works

Combining `.get()` with a matching-type default, and converting the
*result* of that lookup once, means the exact same line of code correctly
handles both "the setting was provided" and "the setting was missing,"
without needing a separate `if`/`else` branch for each case.

#### Common beginner mistakes

- Mixing a numeric default with text values, such as
  `raw_settings.get("max_connections", 100)`, which technically still
  works after `int(100)` but is inconsistent with how every other value
  in `raw_settings` is stored, and could cause confusion if the
  conversion step were ever removed.
- Converting before calling `.get()`, such as
  `int(raw_settings["max_connections"])`, which raises `KeyError`
  immediately, since direct lookup does not know about defaults at all.
- Forgetting to convert the *default* value along with the "found" value,
  and ending up with a `str` in one branch and an `int` in the other.

#### Optional improvement challenge

Add a setting whose stored text is invalid for conversion, such as
`{"timeout": "soon"}`, and wrap the `int(...)` call in a `try`/`except
ValueError` block (as introduced in Topic 9) that falls back to a safe
default instead of crashing.

---

### Question 13 — Hard

#### Problem statement

Two days of visitor logs are recorded as lists (with repeats), such as
Monday's `["ana", "bo", "ana", "chen", "bo"]` and Tuesday's `["bo", "dee",
"chen", "chen"]`. Find which visitors came on both days, which came only
on Monday, everyone who visited on either day, and everyone who visited on
exactly one of the two days. Also confirm that an empty "Wednesday" set
shares nothing with Monday's visitors.

#### Concepts practised

Converting lists with duplicates into sets, and set intersection,
difference, union, symmetric difference, and `isdisjoint()` (Topic 8).

#### Requirements and expected output

- Convert both visitor logs into sets, automatically removing repeats.
- Compute and print, each in sorted order: the intersection, the
  Monday-only difference, the union, and the symmetric difference.
- Check that an empty set is disjoint from Monday's visitors.

#### Edge cases to consider

- `monday_set.difference(tuesday_set)` and
  `tuesday_set.difference(monday_set)` give *different* results — this
  operation is not symmetric, unlike union or intersection.
- An empty set (`set()`) is disjoint from *any* set, including one with
  visitors in it — this should always be `True`, since there is nothing
  in the empty set to overlap with.
- Set literals with duplicate values, or lists converted to sets,
  automatically collapse repeats — `"ana"` and `"bo"` each appear twice in
  the raw Monday list but only once in `monday_set`.

#### Solution approach

1. Store both days' visitor logs as lists, including repeats.
2. Convert each list to a set.
3. Compute intersection, Monday-only difference, union, and symmetric
   difference, printing each as a sorted list.
4. Create an empty set and confirm it is disjoint from Monday's set.

#### Complete runnable Python solution

```python
monday_visitors = ["ana", "bo", "ana", "chen", "bo"]
tuesday_visitors = ["bo", "dee", "chen", "chen"]

monday_set = set(monday_visitors)
tuesday_set = set(tuesday_visitors)

both_days = monday_set.intersection(tuesday_set)
only_monday = monday_set.difference(tuesday_set)
either_day = monday_set.union(tuesday_set)
one_day_only = monday_set.symmetric_difference(tuesday_set)

print("Both days:", sorted(both_days))
print("Only Monday:", sorted(only_monday))
print("Either day:", sorted(either_day))
print("Exactly one day:", sorted(one_day_only))

no_visitors_wed = set()
print("Wednesday empty?", no_visitors_wed.isdisjoint(monday_set))
```

#### Explanation

- `set(monday_visitors)` collapses `["ana", "bo", "ana", "chen", "bo"]`
  down to the three distinct visitors `{"ana", "bo", "chen"}`; likewise
  for Tuesday.
- `monday_set.intersection(tuesday_set)` keeps only visitors present in
  *both* sets: `"bo"` and `"chen"`.
- `monday_set.difference(tuesday_set)` keeps visitors unique to Monday:
  just `"ana"`, since `"bo"` and `"chen"` also appear on Tuesday.
- `monday_set.union(tuesday_set)` combines every distinct visitor from
  either day, with no duplicates: `"ana"`, `"bo"`, `"chen"`, `"dee"`.
- `monday_set.symmetric_difference(tuesday_set)` keeps only visitors who
  came on exactly one day, excluding anyone who came on both: `"ana"` and
  `"dee"`.
- `no_visitors_wed.isdisjoint(monday_set)` is `True`, since an empty set
  has no values at all to share with anything.

#### Example output

```text
Both days: ['bo', 'chen']
Only Monday: ['ana']
Either day: ['ana', 'bo', 'chen', 'dee']
Exactly one day: ['ana', 'dee']
Wednesday empty? True
```

#### Why this solution works

Converting each day's log to a set first means every subsequent
comparison automatically ignores repeat visits and focuses purely on
*who* showed up — exactly the "which distinct things exist, and how do
two groups compare" question sets are built for (Topic 8), instead of
writing manual loops and `if` checks to answer the same question.

#### Common beginner mistakes

- Assuming `monday_set.difference(tuesday_set)` and
  `tuesday_set.difference(monday_set)` give the same result — they do
  not, since difference keeps what is unique to the *first* set only.
- Confusing `symmetric_difference` (exactly one day) with the plain union
  (either day) — union includes `"bo"` and `"chen"`, symmetric difference
  excludes them.
- Forgetting that raw visitor *lists* still contain duplicates and
  reporting `len(monday_visitors)` as if it were the number of distinct
  visitors.

#### Optional improvement challenge

Add a Wednesday visitor list that shares at least one name with Monday's,
and print whether Wednesday and Monday are disjoint this time, comparing
it with the empty-set result above.

---

### Question 14 — Hard

#### Problem statement

Several pairs of words might represent "the same word," once case and a
few tricky characters (like the German `ß`) are normalized. Given a list
of `(original, candidate)` tuples, unpack each pair and compare the strings after Unicode-aware case
folding, a normalization technique more reliable than plain `.lower()`.

#### Concepts practised

Tuple unpacking inside a loop, and Unicode-aware string normalization with
`.casefold()` for reliable comparison (Topics 4 and 6).

#### Requirements and expected output

- Loop over a list of `(original, candidate)` tuples, unpacking each pair
  directly in the loop header.
- Normalize both words with `.casefold()` before comparing them with
  `==`.
- Print each pair along with whether they count as the same word.

#### Edge cases to consider

- `"Straße".lower()` does **not** become `"strasse"` — only `.casefold()`
  performs that specific, more aggressive normalization, which matters
  for this exact comparison.
- Two words that are simply different (such as `"Hello"` and `"world"`)
  must still correctly report as *not* the same word, even after
  normalization — normalizing does not make unrelated words match.

#### Solution approach

1. Store a list of `(original, candidate)` tuples to compare.
2. Loop over the list, unpacking each tuple into `original` and
   `candidate`.
3. Normalize both with `.casefold()`.
4. Compare the normalized versions with `==` and store the result.
5. Print the original pair and whether they matched.

#### Complete runnable Python solution

```python
raw_entries = [("Straße", "STRASSE"), ("Cafe", "café"), ("Hello", "world")]

for original, candidate in raw_entries:
    normalized_original = original.casefold()
    normalized_candidate = candidate.casefold()
    same_word = normalized_original == normalized_candidate
    print(f'"{original}" vs "{candidate}" -> same word? {same_word}')
```

#### Explanation

- `for original, candidate in raw_entries:` unpacks each two-item tuple
  directly in the loop header, exactly the pattern from Topic 6 —
  `original` and `candidate` are freshly assigned on every pass.
- `.casefold()` aggressively normalizes each word for comparison: it
  expands `"ß"` in `"Straße"` to `"ss"`, producing `"strasse"`, which
  matches the casefolded form of `"STRASSE"`.
- `"Cafe".casefold()` gives `"cafe"`, while `"café".casefold()` gives
  `"café"` — these differ because of the accented `é`, so they correctly
  report as *not* the same word, showing that casefolding normalizes case
  but does not strip accents.
- `"Hello"` and `"world"` remain unrelated words after normalization, so
  `same_word` is `False`, as expected.

#### Example output

```text
"Straße" vs "STRASSE" -> same word? True
"Cafe" vs "café" -> same word? False
"Hello" vs "world" -> same word? False
```

#### Why this solution works

`.casefold()` is specifically designed for reliable text *comparison*
across languages, unlike `.lower()`, which is meant for everyday display
(Topic 4). Comparing two casefolded strings with `==` correctly treats
`"Straße"` and `"STRASSE"` as the same word, while still correctly telling
apart words that only coincidentally share some letters, like `"Cafe"`
and `"café"`.

#### Common beginner mistakes

- Using `.lower()` instead of `.casefold()` for this comparison, and
  missing the `"Straße"`/`"STRASSE"` match entirely, since `"straße"`
  (lowercased but not casefolded) does not equal `"strasse"`.
- Assuming casefolding also strips accents — it does not; `"café"` and
  `"cafe"` remain different strings even after casefolding.
- Comparing `original == candidate` directly, without normalizing either
  side first, which would report every differently-cased pair as
  unequal.

#### Optional improvement challenge

Add a pair that differs only by leading/trailing spaces, such as
`(" Hello", "hello ")`, and update the normalization step to `.strip()`
each word before casefolding it, so that pair also reports correctly as
the same word.

---

### Question 15 — Hard

#### Problem statement

A survey stores three responses: a `rating` that is legitimately `0`, a
`comment`, and a `bonus_score` that was genuinely never answered. Write
code that correctly reports the rating as `0` (a real answer), and
correctly reports the bonus score as "never answered" rather than "zero."
Separately, demonstrate that two variables can hold *equal* values without
being the *same* object, using two integers built in different ways.

#### Concepts practised

Explicit `None` checks for values that could legitimately be a falsy
number, versus plain truthiness, and the difference between `==`
(equality) and `is` (identity) (Topics 2, 9, and 10).

#### Requirements and expected output

- Safely read `rating` and `bonus_score` from the dictionary using
  `.get()`.
- Use `is None` — not plain truthiness — to decide whether each one was
  actually answered, since `0` must be treated as a real answer.
- Compare two integers built differently with both `==` and `is`, and
  print both results.

#### Edge cases to consider

- `if rating:` would incorrectly treat a real rating of `0` as "not
  answered," exactly the trap Topic 9 warns about — this exercise
  requires `is None` specifically to avoid it.
- The two integers compared at the end must be *equal in value* but not
  guaranteed to be the *same object* — this only reliably shows up for
  numbers built at runtime (such as through `int("1000")`), not for small
  literal numbers, which CPython may coincidentally reuse.

#### Solution approach

1. Store the survey dictionary, including the real `0` rating and the
   genuinely missing `bonus_score`.
2. Read `rating` with `.get()` and check `is None` to decide which message
   to print.
3. Do the same for `bonus_score`.
4. Build two separate `int` values that are equal, compare them with `==`
   and `is`, and print both results.

#### Complete runnable Python solution

```python
survey_responses = {"rating": 0, "comment": "none yet", "bonus_score": None}

rating = survey_responses.get("rating")
if rating is None:
    print("Rating was never answered.")
else:
    print(f"Rating: {rating}")

bonus = survey_responses.get("bonus_score")
if bonus is None:
    print("Bonus score was never answered.")
else:
    print(f"Bonus score: {bonus}")

x = 1000
y = int("1000")
print(x == y)
print(x is y)
```

#### Explanation

- `survey_responses.get("rating")` returns `0`, the real, legitimate
  rating. `if rating is None:` is `False` here (because `0` is not
  `None`), so the `else` branch runs, correctly printing `Rating: 0`.
- `survey_responses.get("bonus_score")` returns `None`, since that field
  really was never answered. `if bonus is None:` is `True`, correctly
  printing that it was never answered.
- `x = 1000` and `y = int("1000")` are built in two different ways but
  end up with the same value, `1000`.
- `x == y` is `True`, since both represent the same value. `x is y`
  compares object identity, not value; whether two equal integers are the
  same object is an implementation detail, so the `False` shown here is
  what CPython typically prints but is not guaranteed.

#### Example output

```text
Rating: 0
Bonus score was never answered.
True
False
```

#### Why this solution works

Checking `is None` specifically distinguishes "a real, valid falsy
value" (`rating = 0`) from "no value was ever provided"
(`bonus_score = None`) — a distinction plain `if value:` truthiness
cannot make, since it treats every falsy value identically (Topic 9).
Separately, `==` and `is` answer genuinely different questions (Topic
10): equal value versus the exact same object — and using a
runtime-built integer (`int("1000")`) rather than a small literal usually avoids
the coincidental object-reuse behavior that can make `is` look like it
"works" for ordinary values; either way, `is` should not be relied on for
that.

#### Common beginner mistakes

- Writing `if rating:` instead of `if rating is None:`, incorrectly
  treating a genuine `0` rating the same as "never answered."
- Using `is` to compare `x` and `y` and expecting it to behave like `==`
  for ordinary values — as this example shows, it can give a different
  answer, because it tests identity rather than value.
- Assuming the `is` result for small literal integers (which can
  coincidentally be `True` in CPython) generalizes to all integers — it
  does not, and should never be relied upon either way.

#### Optional improvement challenge

Add a fourth survey field, `"agreed_to_terms": False`, and write the
correct `is None`-based check that reports it as "answered: False,"
rather than mistaking it for "never answered."

---

## Advanced Questions

### Question 16 — Advanced

#### Problem statement

Write a small inventory summary program. Given a dictionary mapping
product names to quantities in stock, print a neatly formatted report of
every product and its quantity, the total number of units in stock, and a
list of any products below a low-stock threshold. Also safely report the
quantity of a product that might not be stocked at all.

#### Concepts practised

Dictionaries and `.items()` iteration, `.get()` for a possibly-missing
product, list building, `sum()`, and f-string alignment — combining ideas
from Topics 4, 5, and 7.

#### Requirements and expected output

- Store an inventory as a dictionary of product names to quantities.
- Print each product and its quantity in two neatly aligned columns.
- Compute and print the total number of units across all products.
- Build and print a list of products below a chosen low-stock threshold
  (sorted alphabetically), or a clear message if none are low.
- Safely look up a product that is not in the inventory at all, without
  crashing.

#### Edge cases to consider

- A product legitimately in stock with `0` units (such as `"milk"`) must
  still be reported and must still count as low stock — it should not be
  confused with a product that was never stocked at all.
- Looking up an unstocked product must not raise `KeyError` — use `.get()`
  with a default of `0`.
- The low-stock list should print clearly even if it happens to be empty,
  rather than printing an empty list with no explanation.

#### Solution approach

1. Create the inventory dictionary and a low-stock threshold.
2. Loop over `.items()` to build a list of low-stock product names.
3. Use `sum()` on `.values()` to get the total units in stock.
4. Print a formatted report: each product/quantity pair, then the total,
   then the low-stock list (or a "none are low" message).
5. Safely look up one unstocked product using `.get(..., 0)`.

#### Complete runnable Python solution

```python
# Inventory summary program.
# Reports total stock, flags low-stock products, and safely looks up
# products that might not exist in the inventory at all.

inventory = {
    "apples": 42,
    "bread": 5,
    "milk": 0,
    "rice": 120,
}

low_stock_threshold = 10
low_stock_items = []

for product, quantity in inventory.items():
    if quantity < low_stock_threshold:
        low_stock_items.append(product)

total_units = sum(inventory.values())

print("Inventory report")
print("-" * 20)
for product, quantity in inventory.items():
    print(f"{product:<10}{quantity:>5} units")

print(f"\nTotal units in stock: {total_units}")

if low_stock_items:
    print("Low stock (below", low_stock_threshold, "units):", sorted(low_stock_items))
else:
    print("No products are low on stock.")

requested_product = "eggs"
quantity_on_hand = inventory.get(requested_product, 0)
print(f"\n{requested_product}: {quantity_on_hand} units on hand")
```

#### Explanation

- `inventory` maps each product name to its current quantity, including
  `"milk": 0`, a product that is genuinely in stock at zero units — a
  deliberate edge case.
- The first loop uses `.items()` to visit each product/quantity pair,
  checking each quantity against `low_stock_threshold` and collecting the
  names of any products below it.
- `sum(inventory.values())` adds up every quantity directly, using the
  `.values()` view from Topic 7, without needing a manual loop.
- The report loop reuses `.items()` again, this time printing each
  product left-aligned in a 10-character field and its quantity
  right-aligned in a 5-character field, for a neatly lined-up report,
  exactly the alignment technique from Topic 4.
- `if low_stock_items:` relies on truthiness (Topic 9): a non-empty list
  is truthy, so the low-stock message only prints when the list actually
  has entries.
- `inventory.get("eggs", 0)` safely reports `0` units for a product that
  was never stocked at all, without raising `KeyError`.

#### Example output

```text
Inventory report
--------------------
apples       42 units
bread         5 units
milk          0 units
rice        120 units

Total units in stock: 167
Low stock (below 10 units): ['bread', 'milk']

eggs: 0 units on hand
```

#### Why this solution works

Every piece of this program reuses a single, safe pattern from earlier
lessons: `.items()` for pairing keys with values, `.get()` with a default
for anything that might be missing, and truthiness for "is this list
empty?" — combined, they produce a program that handles a genuinely
unstocked product, a stocked-but-empty product, and a normal product all
correctly, without any special-case code for each situation.

#### Common beginner mistakes

- Using direct lookup, `inventory["eggs"]`, for the unstocked product,
  which raises `KeyError` and crashes the whole report.
- Treating `"milk": 0` as if it were the same as "not stocked," and
  leaving it out of the report entirely — it is a real, valid entry that
  should still be printed and still count as low stock.
- Building the low-stock list but forgetting to sort it before printing,
  producing an order that depends on the dictionary's insertion order
  rather than being predictable to a reader.

#### Optional improvement challenge

Add a second dictionary, `restock_amounts`, mapping some product names to
quantities to add, and write a small loop that updates `inventory` using
`+=` for each product mentioned in `restock_amounts`, leaving any product
not mentioned unchanged.

---

### Question 17 — Advanced

#### Problem statement

Write a small student-score analyzer. Given a list of `(name, score)`
tuples, print a per-student pass/fail report, the class average, the
highest and lowest scores, whether everyone passed, whether at least one
student passed, and the name of the top-scoring student.

#### Concepts practised

Lists of tuples, tuple unpacking in a loop, `sum()`/`len()` for an
average, `max()`/`min()`, `any()`/`all()` on a list of pass/fail flags —
drawing on Topics 5, 6, and 9.

#### Requirements and expected output

- Store student data as a list of `(name, score)` tuples.
- Print each student's name, score, and a `PASS`/`FAIL` status, neatly
  aligned.
- Compute and print the class average (one decimal place), the highest
  score, and the lowest score.
- Report whether every student passed and whether at least one passed.
- Determine and print the name and score of the top-scoring student.

#### Edge cases to consider

- The pass/fail threshold must be applied consistently in both the
  per-student report and the `any()`/`all()` summary — computing it twice
  in two different ways could give inconsistent results.
- Finding the "top student" needs both the name and the score together;
  `max(scores)` alone would give the highest score but lose track of
  *whose* score it was.

#### Solution approach

1. Store the student data as a list of tuples.
2. Build a separate `scores` list by unpacking each tuple in a loop
   (useful for the statistics that follow).
3. Compute the class average, highest, and lowest score from `scores`.
4. Build a list of pass/fail `bool` flags using a fixed passing threshold.
5. Print the per-student report, the statistics, and the `any()`/`all()`
   summary.
6. Find the top student by looping over the original list of tuples and
   tracking the best `(name, score)` seen so far.

#### Complete runnable Python solution

```python
# Student-score analyzer.
# Takes a list of (name, score) tuples and reports simple statistics.

student_scores = [
    ("Ada", 92),
    ("Grace", 78),
    ("Alan", 85),
    ("Marie", 60),
]

scores = []
for name, score in student_scores:
    scores.append(score)

class_average = sum(scores) / len(scores)
highest_score = max(scores)
lowest_score = min(scores)

passing_threshold = 70
passed_flags = []
for score in scores:
    passed_flags.append(score >= passing_threshold)

print("Student report")
print("-" * 20)
for name, score in student_scores:
    if score >= passing_threshold:
        status = "PASS"
    else:
        status = "FAIL"
    print(f"{name:<10}{score:>4}  {status}")

print(f"\nClass average: {class_average:.1f}")
print(f"Highest score: {highest_score}")
print(f"Lowest score:  {lowest_score}")
print(f"Everyone passed: {all(passed_flags)}")
print(f"At least one passed: {any(passed_flags)}")

top_name, top_score = student_scores[0]
for name, score in student_scores:
    if score > top_score:
        top_name = name
        top_score = score
print(f"Top student: {top_name} ({top_score})")
```

#### Explanation

- `for name, score in student_scores:` unpacks each tuple directly in the
  loop header, building a `scores` list (the names are not needed
  separately, because the later loops use `student_scores` directly).
- `sum(scores) / len(scores)` computes the average using the running-total
  pattern from earlier lessons; `max(scores)` and `min(scores)` find the
  extremes directly.
- The pass/fail loop applies `passing_threshold` once, consistently, and
  reuses that same constant again inside the per-student report loop, so
  both parts of the program always agree on what counts as passing.
- `top_name, top_score = student_scores[0]` starts by assuming the first
  student is the best so far; the loop then updates both `top_name` and
  `top_score` together whenever a higher score is found, so the name and
  score never get out of sync.

#### Example output

```text
Student report
--------------------
Ada         92  PASS
Grace       78  PASS
Alan        85  PASS
Marie       60  FAIL

Class average: 78.8
Highest score: 92
Lowest score:  60
Everyone passed: False
At least one passed: True
Top student: Ada (92)
```

#### Why this solution works

Storing the raw data as a list of tuples keeps each student's name and
score permanently paired together (Topic 6), so every later computation —
average, extremes, pass/fail, and "who is on top" — can be derived
directly from that one list, without ever risking a name and a score
drifting out of sync with each other.

#### Common beginner mistakes

- Computing `max(scores)` to find the top score, but then separately
  trying to guess which student it belonged to, rather than tracking the
  name and score together in one loop.
- Using two different, hardcoded threshold numbers in the per-student
  report and the `any()`/`all()` summary, risking silent disagreement if
  one is ever changed without the other.
- Forgetting that `passed_flags` must be built from the same `scores`
  list the report itself is printing, to keep both parts consistent.

#### Optional improvement challenge

Add a line that builds a new list of only the names of students who
passed (without their scores), by looping over `student_scores` and
appending just the name whenever the score meets the threshold.

---

### Question 18 — Advanced

#### Problem statement

Write a small tag-comparison tool for two articles. Each article's tags
arrive as a messy list, with inconsistent capitalization and stray spaces,
and possibly duplicates. Clean both tag lists, then report which tags they
share, which are unique to each article, and every distinct tag across
both, all case-insensitively.

#### Concepts practised

A small reusable function, string cleanup (`.strip()`, `.casefold()`),
building a set from a list, and set union/intersection/difference — drawing
on Topics 4, 5, 6 (functions were introduced in Module 1.1), and 8.

#### Requirements and expected output

- Write a small function that takes a raw list of tags and returns a
  cleaned set: stripped of extra spaces and casefolded, with duplicates
  automatically removed.
- Apply it to both articles' raw tag lists.
- Print each article's cleaned tags, the shared tags, the tags unique to
  each article, and the full combined tag set — all sorted.
- Report whether the two articles share any tag at all.

#### Edge cases to consider

- `"Python"`, `" python"`, and `"python "` must all be treated as the
  *same* tag once cleaned — stripping and casefolding must both happen
  before adding a tag to the set.
- Two articles might share zero tags; the "do they share any tag" check
  must work correctly in that case too, not just when they do overlap.

#### Solution approach

1. Define a function `clean_tags(raw_tags)` that builds and returns a set
   of stripped, casefolded tags from a raw list.
2. Call it once for each article's raw tag list.
3. Compute intersection, both one-sided differences, and the union.
4. Print each result, sorted for predictable output.
5. Use `isdisjoint()` to check whether the two sets share anything at
   all.

#### Complete runnable Python solution

```python
# Text and tag comparison tool.
# Compares the tags on two articles, ignoring case and extra spaces.

article_a_raw = ["Python", " python", "AI", "Beginner", "ai "]
article_b_raw = ["python", "Advanced", "TIPS", " AI"]

def clean_tags(raw_tags):
    cleaned = set()
    for tag in raw_tags:
        cleaned.add(tag.strip().casefold())
    return cleaned

tags_a = clean_tags(article_a_raw)
tags_b = clean_tags(article_b_raw)

shared_tags = tags_a & tags_b
only_in_a = tags_a - tags_b
only_in_b = tags_b - tags_a
all_tags = tags_a | tags_b

print("Article A tags:", sorted(tags_a))
print("Article B tags:", sorted(tags_b))
print("Shared tags:", sorted(shared_tags))
print("Only in A:", sorted(only_in_a))
print("Only in B:", sorted(only_in_b))
print("All tags combined:", sorted(all_tags))
print("Do the articles share any tag at all?", not tags_a.isdisjoint(tags_b))
```

#### Explanation

- `clean_tags(raw_tags)` loops over every raw tag, applies
  `.strip().casefold()` to normalize it, and adds the result to a set —
  automatically collapsing near-duplicates like `"Python"` and `" python"`
  down to one entry, `"python"`.
- Calling `clean_tags(...)` once per article keeps the cleaning logic in
  one place, reused for both inputs, rather than repeating the same three
  lines twice.
- `tags_a & tags_b`, `tags_a - tags_b`, `tags_b - tags_a`, and `tags_a |
  tags_b` compute the intersection, each one-sided difference, and the
  union, exactly as taught in Topic 8.
- `not tags_a.isdisjoint(tags_b)` reads as "the two sets are *not*
  completely separate," which is `True` here, since they share `"ai"` and
  `"python"`.

#### Example output

```text
Article A tags: ['ai', 'beginner', 'python']
Article B tags: ['advanced', 'ai', 'python', 'tips']
Shared tags: ['ai', 'python']
Only in A: ['beginner']
Only in B: ['advanced', 'tips']
All tags combined: ['advanced', 'ai', 'beginner', 'python', 'tips']
Do the articles share any tag at all? True
```

#### Why this solution works

Cleaning every tag the same way, in one small function, guarantees that
`"AI"` and `"ai "` are never accidentally treated as two different tags —
the set operations that follow only ever see already-normalized values,
so the comparison logic itself can stay simple and completely focused on
set relationships, not text cleanup.

#### Common beginner mistakes

- Comparing raw tags directly, without cleaning them first, so
  `"Python"` and `"python "` are (incorrectly) treated as two different
  tags.
- Casefolding before stripping, on a tag like `"  AI  "`, and assuming the
  order does not matter — for whitespace and case together it happens to
  work either order here, but stripping first is the safer, more
  general habit to build.
- Forgetting that `tags_a - tags_b` and `tags_b - tags_a` are different
  operations, and printing the same difference twice by mistake.

#### Optional improvement challenge

Add a third article's raw tag list, clean it the same way using the
existing function, and print which tags are common to *all three*
articles using two chained `.intersection()` calls (or nested `&`
operators).

---

### Question 19 — Advanced

#### Problem statement

Write a small, safe profile updater. Given an existing user profile
dictionary — including a field that is a real, meaningful empty string, a
real `False`, and a field that is genuinely `None` (never set) — apply a
batch of updates to it. For each updated field, report whether it was
brand new, previously empty, or being overwritten. Afterward, convert one
newly added field to the correct type, and clearly report whether the
"referral code" field still has no value at all.

#### Concepts practised

Dictionaries, `.get()`, distinguishing `None` from other falsy values,
looping over `.items()`, mutating a dictionary safely, and explicit type
conversion — Topics 2, 7, 9, and 10 together.

#### Requirements and expected output

- Store a profile with at least one empty-but-real string, one real
  `False`, and one genuinely unset (`None`) field.
- Apply a dictionary of updates, one field at a time, printing a message
  for each: "adding a new field," "filling in a previously empty field,"
  or "overwriting an existing value" — chosen correctly for each case.
- After all updates, convert the newly added `"age"` field from text to
  `int`.
- Print the final profile.
- Report whether `"referral_code"` is still unset.

#### Edge cases to consider

- `profile.get(field)` returns `None` both when a field is missing
  entirely *and* when a field exists but was deliberately set to `None` —
  telling these two situations apart requires also checking
  `field not in profile`.
- `"newsletter_opt_in": False` must never be reported as "empty" or
  "missing" — it is a real, valid `False` value, not an absence of data.

#### Solution approach

1. Create the starting profile dictionary with a mix of real values,
   falsy-but-real values, and one genuinely unset field.
2. Create a dictionary of updates to apply.
3. Loop over the updates with `.items()`; for each field, check whether it
   is missing entirely, present but `None`, or present with a real value,
   and print the matching message.
4. Apply each update by assigning into `profile`.
5. Convert `profile["age"]` to `int` after all updates are applied.
6. Print the final profile and check `"referral_code"` with `is None`.

#### Complete runnable Python solution

```python
# Safe profile updater.
# Updates a user profile dictionary without losing track of fields
# that are genuinely "not set yet" versus fields that are a real,
# meaningful falsy value such as 0 or "".

profile = {
    "username": "grace92",
    "bio": "",
    "newsletter_opt_in": False,
    "referral_code": None,
}

updates = {
    "bio": "Engineer and lifelong learner.",
    "age": "34",
    "referral_code": "REF-2026",
}

for field, new_value in updates.items():
    current_value = profile.get(field)
    if current_value is None and field not in profile:
        print(f"Adding new field '{field}'.")
    elif current_value is None:
        print(f"Filling in previously empty field '{field}'.")
    else:
        print(f"Overwriting existing value for '{field}'.")
    profile[field] = new_value

if "age" in profile:
    profile["age"] = int(profile["age"])

print("\nFinal profile:")
for field, value in profile.items():
    print(f"  {field}: {value}")

if profile.get("referral_code") is None:
    print("\nNo referral code on file yet.")
else:
    print(f"\nReferral code on file: {profile['referral_code']}")
```

#### Explanation

- The starting `profile` deliberately includes `"bio": ""` (a real, empty
  answer), `"newsletter_opt_in": False` (a real, valid `False`), and
  `"referral_code": None` (genuinely never set) — three different kinds
  of falsy-looking data.
- For `"bio"`, `current_value` is `""`, which is *not* `None`, so the
  `else` branch runs, correctly reporting an overwrite, even though `""`
  is falsy.
- For `"age"`, `current_value` is `None` *and* `"age" not in profile` is
  `True` (the key does not exist at all yet), so the first branch
  correctly reports it as a brand-new field.
- `profile["age"] = int(profile["age"])` converts the just-added text
  value `"34"` into the real number `34`, after all updates have been
  applied.
- For `"referral_code"`, `current_value` is `None` but the key *is* in
  `profile`, so the second branch runs, correctly reporting a previously
  empty field being filled in. That also shows all three cases: `"age"` is
  brand new, `"referral_code"` was previously empty, and `"bio"` is
  overwritten.
- `profile.get("referral_code") is None` is now `False` at the end, so the
  final message reports the referral code that is on file. (If you remove
  `"referral_code"` from `updates`, it stays `None` and the program
  reports "No referral code on file yet.")

#### Example output

```text
Overwriting existing value for 'bio'.
Adding new field 'age'.
Filling in previously empty field 'referral_code'.

Final profile:
  username: grace92
  bio: Engineer and lifelong learner.
  newsletter_opt_in: False
  referral_code: REF-2026
  age: 34

Referral code on file: REF-2026
```

#### Why this solution works

Checking both `current_value is None` and `field not in profile`
separately is exactly what correctly tells apart three genuinely
different situations — brand new, previously empty-on-purpose, and being
overwritten — none of which plain truthiness (`if current_value:`) could
distinguish, since `""`, `False`, and `None` are all equally falsy but
mean very different things here (Topic 9).

#### Common beginner mistakes

- Checking only `if current_value:` to decide whether a field is "new,"
  which would incorrectly treat the real, existing `""` value for
  `"bio"` as if the field did not exist yet.
- Converting `profile["age"]` to `int` *before* the update loop runs,
  which would raise `KeyError`, since `"age"` does not exist in `profile`
  until the loop adds it.
- Forgetting that `.get(field)` alone cannot distinguish "missing key"
  from "key present with value `None`" — both require the extra
  `field not in profile` check to tell apart.

#### Optional improvement challenge

Add `"newsletter_opt_in": True` to `updates`, run the program again, and
predict — before checking — which of the three messages should print for
that field, given that its *current* value is the real, valid `False`.

---

### Question 20 — Advanced

#### Problem statement

Write a small contact-data cleaner. Given a list of raw contact records
(each a small dictionary with a messy `"name"` and `"email"`), clean every
name and email, and remove duplicate people — where "duplicate" means the
*same* email address once cleaned, even if it was typed differently each
time (extra spaces, different capitalization).

#### Concepts practised

Lists of dictionaries, string cleanup (`.strip()`, `.title()`,
`.casefold()`), and using a set to track "already seen" values while
building a deduplicated list — drawing on Topics 4, 5, 7, and 8 together.

#### Requirements and expected output

- Start from a list of raw contact dictionaries, including one person
  entered twice with differently formatted name and email text.
- Clean each name to title case and each email to a trimmed, casefolded
  form.
- Keep only the *first* cleaned version of each unique email, skipping any
  later record with the same cleaned email.
- Print the raw contact count, the unique contact count, and the cleaned,
  deduplicated list.

#### Edge cases to consider

- Two records can represent the same person even though their raw text
  differs completely in spacing and case — cleaning must happen *before*
  checking for duplicates, not after.
- A `set` used to track "already seen" emails must be checked and updated
  together for every record, so a duplicate discovered partway through
  the list is still correctly skipped.

#### Solution approach

1. Store the raw list of contact dictionaries, including one intentional
   duplicate.
2. Create an empty set to track cleaned emails already seen, and an empty
   list to collect the cleaned, deduplicated contacts.
3. Loop over the raw contacts: clean the name and email, and only keep the
   record (and remember its email) if that cleaned email has not been
   seen before.
4. Print the raw count, the unique count, and every kept contact.

#### Complete runnable Python solution

```python
# Contact-data cleaner.
# Cleans messy contact records and removes duplicate people, using
# the email address (normalized) as the unique identifier.

raw_contacts = [
    {"name": "  ada lovelace ", "email": "  ADA@Example.com"},
    {"name": "Grace Hopper", "email": "grace@example.com"},
    {"name": "ada LOVELACE", "email": "ada@example.com  "},
    {"name": "Alan Turing", "email": "ALAN@Example.com"},
]

seen_emails = set()
cleaned_contacts = []

for contact in raw_contacts:
    clean_name = contact["name"].strip().title()
    clean_email = contact["email"].strip().casefold()

    if clean_email not in seen_emails:
        seen_emails.add(clean_email)
        cleaned_contacts.append({"name": clean_name, "email": clean_email})

print(f"Raw contact count: {len(raw_contacts)}")
print(f"Unique contact count: {len(cleaned_contacts)}")
print()
for contact in cleaned_contacts:
    print(f"{contact['name']:<15} {contact['email']}")
```

#### Explanation

- Each raw contact is a small dictionary with a `"name"` and an `"email"`
  key; the third record is a differently formatted duplicate of the
  first.
- `contact["name"].strip().title()` and `contact["email"].strip().casefold()`
  clean both fields the same way every time, so `"  ada lovelace "` and
  `"ada LOVELACE"` both become the identical cleaned name, `"Ada
  Lovelace"`, and their emails both become `"ada@example.com"`.
- `if clean_email not in seen_emails:` checks the *cleaned* email against
  everything already kept; the first Ada record passes this check and is
  added, but the third record's cleaned email is already in
  `seen_emails`, so it is skipped entirely.
- `seen_emails.add(clean_email)` and `cleaned_contacts.append(...)` only
  run together, for records that were actually kept, so the two stay in
  sync throughout the loop.

#### Example output

```text
Raw contact count: 4
Unique contact count: 3

Ada Lovelace    ada@example.com
Grace Hopper    grace@example.com
Alan Turing     alan@example.com
```

#### Why this solution works

Cleaning each field *before* the duplicate check, and using a set purely
to remember "which cleaned emails have already been kept," means the
deduplication logic never has to compare messy raw text directly — it
only ever compares already-normalized values, which is exactly what makes
`"  ADA@Example.com"` and `"ada@example.com  "` correctly collapse into
one contact.

#### Common beginner mistakes

- Checking `contact["email"] not in seen_emails` using the *raw* email
  instead of the cleaned one, which would fail to catch the duplicate at
  all, since the raw text differs.
- Adding to `cleaned_contacts` before confirming the email is actually
  new, which would let a duplicate slip through.
- Forgetting that `seen_emails` must be updated inside the loop, on every
  kept record — updating it only once outside the loop would never track
  anything.

#### Optional improvement challenge

Add a line that also builds a list of just the *duplicate* emails that
were skipped, so a real system could report them separately (for example,
to flag "these records looked like duplicates and were merged").
