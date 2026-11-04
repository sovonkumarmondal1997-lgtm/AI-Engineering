# Python Core Language and Data Types --- Complete Exercise Solutions

## Beginner-friendly teaching guide \| Questions 1--20

### How to use this guide

This guide follows the attached practice file in its original order.
Each question includes the goal, the reasoning, runnable Python code,
expected result, and the concept to remember. Read the approach first,
predict the output, then run the code yourself.

### Learning material reviewed

The practice set covers the same foundations taught in Topics 1--10:

1.  Python files, interpreter, REPL, comments, and indentation
2.  Variables, `int`, `float`, `bool`, `str`, and `None`
3.  Operators and precedence
4.  Strings, indexing, slicing, methods, and formatting
5.  Lists, mutation, copying, and aliasing
6.  Tuples and unpacking
7.  Dictionaries and lookups
8.  Sets and unique values
9.  Type conversion and truthiness
10. Mutability, identity, shallow copying, and deep copying

The solutions stay within those concepts and the functions already
introduced in Module 1.1. Question 11 uses Python's standard-library
`copy` module because the source exercise explicitly requires
`copy.deepcopy()`.

------------------------------------------------------------------------

# Basic questions

## Question 1 --- Store a person's details and print each type

**What the problem asks:** Create five clearly named variables: name,
age, height, student status, and an unknown middle name. Print each
value and its type.

**Reasoning:** Match the data to the correct Python type: - Name → `str`
(text) - Age → `int` (whole number) - Height → `float` (measurement that
can contain a fraction) - Student status → `bool` (`True` or `False`) -
Unknown middle name → `None` (no value supplied)

`None` is not the same as an empty string. `""` means the field contains
known text that happens to be empty; `None` means no value is available.

**Solution:**

``` python
full_name = "Maria Alvarez"
age = 21
height_m = 1.68
is_student = True
middle_name = None

print(f"{full_name} ({type(full_name)})")
print(f"{age} ({type(age)})")
print(f"{height_m} ({type(height_m)})")
print(f"{is_student} ({type(is_student)})")
print(f"{middle_name} ({type(middle_name)})")
```

**Expected output:**

``` text
Maria Alvarez (<class 'str'>)
21 (<class 'int'>)
1.68 (<class 'float'>)
True (<class 'bool'>)
None (<class 'NoneType'>)
```

**Important points:** `type()` reports a value's type; it does not
change the value. A value such as `2.0` is still a `float`, not an
`int`. Comments beginning with `#` are notes for people and are ignored
by Python.

**Common mistake:** Using `""`, `0`, or `False` for an unknown middle
name. Those are real values and communicate different meanings.

**Optional challenge --- favorite number `0`:**

``` python
favorite_number = 0
print(f"{favorite_number} ({type(favorite_number)})")
# 0 is a real, meaningful number; None means no value was supplied.
```

------------------------------------------------------------------------

## Question 2 --- Calculate an order total and discount

**What the problem asks:** Three items cost \$12.50 each. Shipping is
\$5. A 10% discount applies to the items only.

**Reasoning:** 1. Items total = unit price × quantity = \$37.50. 2.
Discount = items total × 0.10 = \$3.75. 3. Final price = items total −
discount + shipping = \$38.75.

Keep these steps separate. This makes the business rule clear and
prevents accidentally discounting shipping.

**Solution:**

``` python
unit_price = 12.50
quantity = 3
shipping_fee = 5.00
discount_rate = 0.10

items_total = unit_price * quantity
discount_amount = items_total * discount_rate
final_price = items_total - discount_amount + shipping_fee

print(f"Items total: ${items_total:.2f}")
print(f"Discount: ${discount_amount:.2f}")
print(f"Final price: ${final_price:.2f}")
```

**Expected output:**

``` text
Items total: $37.50
Discount: $3.75
Final price: $38.75
```

**Important points:** `*` multiplies; `-` subtracts; `+` adds. The `.2f`
f-string format displays exactly two digits after the decimal point. The
discount is calculated before shipping is added.

**Common mistake:** Calculating 10% of `$42.50` (items plus shipping),
which incorrectly discounts shipping too.

**Optional challenge --- extra \$2 discount when items exceed \$30:**

``` python
if items_total > 30:
    final_price -= 2.00

print(f"Final price after extra discount: ${final_price:.2f}")
```

With the given data, the extra discount applies and the final price
becomes `$36.75`.

------------------------------------------------------------------------

## Question 3 --- Index, slice, and reverse a string

**What the problem asks:** From `"backpropagation"`, extract the first
character, last character, first four characters, next five characters,
and reversed word.

**Reasoning:** Python string indexes start at `0`. Negative index `-1`
means the last character. In a slice `[start:stop]`, the stop position
is excluded. A step of `-1` walks backward.

**Solution:**

``` python
word = "backpropagation"

first_letter = word[0]
last_letter = word[-1]
first_four = word[:4]
next_five = word[4:9]
reversed_word = word[::-1]

print(first_letter)
print(last_letter)
print(first_four)
print(next_five)
print(reversed_word)
```

**Expected output:**

``` text
b
n
back
propa
noitagaporpkcab
```

**Important points:** `word[:4]` means start at the beginning and stop
before index 4. `word[4:9]` selects indexes 4 through 8, exactly five
characters. Strings are immutable; slicing creates another string and
leaves `word` unchanged.

**Common mistake:** Writing `word[4:8]`, which returns only four
characters.

**Optional challenge --- every second character:**

``` python
print(word[::2])
```

Output: `bcpoaain`

------------------------------------------------------------------------

## Question 4 --- Modify a list of movies

**What the problem asks:** Start with three movies, append a fourth,
replace the second, and print the list, first movie, last movie, and
count.

**Reasoning:** A list is ordered and mutable. `.append()` adds one item
at the end. Index `1` is the second item because indexing starts at
zero. `[-1]` always selects the last item.

**Solution:**

``` python
favorite_movies = ["Arrival", "Coco", "Spirited Away"]

favorite_movies.append("The Matrix")
favorite_movies[1] = "Inside Out"

print(favorite_movies)
print(favorite_movies[0])
print(favorite_movies[-1])
print(len(favorite_movies))
```

**Expected output:**

``` text
['Arrival', 'Inside Out', 'Spirited Away', 'The Matrix']
Arrival
The Matrix
4
```

**Important points:** `.append()` mutates the existing list. Index
assignment replaces an item. `len()` returns the number of items.

**Common mistakes:** Using `.insert()` when you mean replace; using a
fixed index instead of `[-1]`; assigning the result of `.append()` back
to the list. `.append()` returns `None`.

**Optional challenge --- remove a movie:**

``` python
favorite_movies.remove("Spirited Away")
print(favorite_movies)
```

------------------------------------------------------------------------

## Question 5 --- Unpack a tuple and swap two variables

**What the problem asks:** Store latitude and longitude in a tuple,
unpack them into separate variables, then swap two city names without a
temporary variable.

**Reasoning:** A tuple groups a fixed set of related values. Unpacking
assigns its values to variables in order. In `a, b = b, a`, Python
evaluates the complete right-hand side before assigning the left-hand
side.

**Solution:**

``` python
location = (28.6139, 77.2090)

latitude, longitude = location
print(f"Latitude: {latitude}")
print(f"Longitude: {longitude}")

city_a = "Delhi"
city_b = "Tokyo"

city_a, city_b = city_b, city_a
print(city_a, city_b)
```

**Expected output:**

``` text
Latitude: 28.6139
Longitude: 77.209
Tokyo Delhi
```

**Important points:** The number of variables must match the number of
tuple values, or Python raises `ValueError`. A trailing zero in a float
is not preserved when printed because it does not change the numeric
value.

**Common mistake:** Writing `city_a = city_b` and then
`city_b = city_a`; the original value of `city_a` is lost.

**Optional challenge --- include elevation:**

``` python
location_3d = (28.6139, 77.2090, 216)
latitude, longitude, elevation_m = location_3d
print(latitude, longitude, elevation_m)
```

------------------------------------------------------------------------

# Moderate questions

## Question 6 --- Clean a name and email

**What the problem asks:** Remove extra spaces around a name and email,
put the name in title case, put the email in lowercase, and display the
name in a 20-character left-aligned field.

**Reasoning:** `.strip()` removes whitespace from the beginning and end.
`.title()` capitalizes the start of each word. `.lower()` converts text
to lowercase. String methods return new strings; they do not change the
original string.

**Solution:**

``` python
raw_name = "  ada LOVELACE  "
raw_email = "  ADA@Example.COM "

clean_name = raw_name.strip().title()
clean_email = raw_email.strip().lower()

print(f"Name:  {clean_name}")
print(f"Email: {clean_email}")
print(f"[{clean_name:<20}] length={len(clean_name)}")
```

**Expected output:**

``` text
Name:  Ada Lovelace
Email: ada@example.com
[Ada Lovelace        ] length=12
```

**Important points:** Method chaining runs left to right. `<20` means
left-align in a field at least 20 characters wide. `len()` measures the
cleaned name, not the original text.

**Common mistake:** Calling `raw_name.strip()` without saving or using
its returned value.

**Optional challenge --- check that the name contains only letters and
spaces:**

``` python
name_without_spaces = clean_name.replace(" ", "")
if name_without_spaces.isalpha():
    print("Name contains only letters and spaces.")
else:
    print("Warning: name contains other characters.")
```

------------------------------------------------------------------------

## Question 7 --- Convert ages and use truthiness

**What the problem asks:** Convert text ages to integers and calculate
their average. Then classify form values with `bool()`, and use `all()`
and `any()`.

**Reasoning:** Values read or stored as text are strings. Convert each
age with `int()` before adding. In Python, an empty string and numeric
zero are falsy; non-empty strings are truthy. `all()` is true only when
every item is truthy. `any()` is true when at least one item is truthy.

**Solution:**

``` python
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

**Expected output:**

``` text
Average age: 25.0
[True, False, True, False]
All filled: False
At least one filled: True
```

**Important points:** `int("25")` converts text to the integer `25`.
Dividing by `len(raw_ages)` calculates the average. This exercise
demonstrates Python truthiness, not complete form validation: a zero can
be a valid answer depending on the field.

**Common mistakes:** Adding a string directly to an integer; confusing
`any()` and `all()`; assuming all falsy values mean the same thing.

**Optional challenge --- add the string `"0"`:**

``` python
form_values.append("0")
print(bool("0"))  # True: it is a non-empty string.
```

------------------------------------------------------------------------

## Question 8 --- Safely look up dictionary prices

**What the problem asks:** Look up an existing product, look up a
missing product with and without a default, and calculate a shopping
total even when a product is missing.

**Reasoning:** A dictionary maps keys to values. `prices.get(key)`
returns the value or `None` if the key is missing.
`prices.get(key, default)` returns the chosen default instead. Direct
lookup with `prices[key]` raises `KeyError` for a missing key.

**Solution:**

``` python
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

**Expected output:**

``` text
2.75
None
0.0
Total cost: $2.40
```

**Important points:** `.get()` makes a missing key manageable. The `0.0`
default is used here to demonstrate safe lookup. In a real checkout
system, an unknown product price should normally be flagged instead of
silently treated as free.

**Common mistake:** Thinking `.get("cheese")` returns zero
automatically. Without a default, it returns `None`.

**Optional challenge --- check for eggs before direct lookup:**

``` python
if "eggs" in prices:
    print(prices["eggs"])
else:
    print("Eggs are not listed in the price dictionary.")
```

------------------------------------------------------------------------

## Question 9 --- Find unique tags with a set

**What the problem asks:** Remove duplicate tags, print unique tags
alphabetically, count submissions and unique tags, and check membership.

**Reasoning:** A set stores unique values. Converting a list to a set
removes duplicates. Sets do not guarantee a display order, so use
`sorted()` when predictable alphabetical output is required.

**Solution:**

``` python
submitted_tags = ["python", "ai", "python", "beginner", "ai", "python"]

unique_tags = set(submitted_tags)

print(sorted(unique_tags))
print(f"Total submissions: {len(submitted_tags)}")
print(f"Unique tags: {len(unique_tags)}")
print("ml" in unique_tags)
print("python" in unique_tags)
```

**Expected output:**

``` text
['ai', 'beginner', 'python']
Total submissions: 6
Unique tags: 3
False
True
```

**Important points:** The original list still contains six submissions.
The set contains only three distinct tags. `sorted()` returns a list,
not a set.

**Common mistakes:** Expecting a set to preserve alphabetical order;
trying to access a set with `[0]`; confusing total submissions with
distinct tags.

**Optional challenge --- find tags submitted on both days:**

``` python
day_two_tags = ["python", "ml", "ai"]
day_two_set = set(day_two_tags)
print(sorted(unique_tags & day_two_set))
```

Output: `['ai', 'python']`.

------------------------------------------------------------------------

## Question 10 --- Understand list aliasing and copying

**What the problem asks:** Give a list a second name, mutate through
that name, then make a real copy and mutate only the copy.

**Reasoning:** Assignment such as `alias = original` does not create a
second list. Both names refer to the same object. `.copy()` creates a
new outer list, so adding an item to the copy does not change the
original flat list.

**Solution:**

``` python
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

**Expected output:**

``` text
original after alias mutation: ['Song A', 'Song B', 'Song C', 'Song D']
alias: ['Song A', 'Song B', 'Song C', 'Song D']
original after copy mutation: ['Song A', 'Song B', 'Song C', 'Song D']
copy: ['Song A', 'Song B', 'Song C', 'Song D', 'Song E']
```

**Important points:** An alias is another name for the same object. A
shallow copy is a new outer list, but nested mutable objects can still
be shared.

**Common mistake:** Writing
`playlist_original = playlist_original.append("Song D")`. `.append()`
changes the list and returns `None`.

**Optional challenge --- verify identity:**

``` python
print(playlist_original is playlist_alias)  # True
print(playlist_original is playlist_copy)   # False
```

------------------------------------------------------------------------

# Hard questions

## Question 11 --- Shallow copy versus deep copy

**What the problem asks:** Copy a nested list shallowly, show that an
inner-list mutation is shared, show that adding a new outer item is
independent, then use `copy.deepcopy()` to make nested lists
independent.

**Reasoning:** A nested list is a list containing other lists. `.copy()`
duplicates only the outer list. The inner lists are still shared.
`copy.deepcopy()` recursively copies the nested objects in this example.

**Solution:**

``` python
import copy

classroom = [["Ada", "Grace"], ["Alan"]]

shallow = classroom.copy()
shallow[0].append("Marie")

print("original after inner mutation:", classroom)
print("shallow copy:", shallow)

shallow.append(["Linus"])
print("original after outer append:", classroom)
print("shallow copy:", shallow)

deep = copy.deepcopy(classroom)
deep[0].append("Katherine")

print("original after deep-copy mutation:", classroom)
print("deep copy:", deep)
```

**Expected output:**

``` text
original after inner mutation: [['Ada', 'Grace', 'Marie'], ['Alan']]
shallow copy: [['Ada', 'Grace', 'Marie'], ['Alan']]
original after outer append: [['Ada', 'Grace', 'Marie'], ['Alan']]
shallow copy: [['Ada', 'Grace', 'Marie'], ['Alan'], ['Linus']]
original after deep-copy mutation: [['Ada', 'Grace', 'Marie'], ['Alan']]
deep copy: [['Ada', 'Grace', 'Marie', 'Katherine'], ['Alan']]
```

**Important points:** `shallow[0]` and `classroom[0]` refer to the same
inner list. Appending a new group to `shallow` changes only its outer
list. The deep copy has separate inner lists.

**Common mistakes:** Assuming `.copy()` duplicates every nested object;
forgetting `import copy`; using deep copy when a shallow copy is
sufficient.

**Optional challenge --- check inner-list identity:**

``` python
print(classroom[0] is shallow[0])  # True
print(classroom[0] is deep[0])     # False
```

------------------------------------------------------------------------

## Question 12 --- Read settings safely and convert them

**What the problem asks:** Read three settings from a dictionary. Two
exist as strings; one is missing. Use text defaults and convert all
three results to integers.

**Reasoning:** Call `.get()` first so a missing key returns a default
instead of raising `KeyError`. Then pass the returned string to `int()`.
This keeps the conversion step consistent whether the value was present
or supplied by the default.

**Solution:**

``` python
raw_settings = {"max_retries": "5", "timeout": "30"}

max_retries = int(raw_settings.get("max_retries", "3"))
timeout = int(raw_settings.get("timeout", "10"))
max_connections = int(raw_settings.get("max_connections", "100"))

print(f"max_retries = {max_retries} ({type(max_retries)})")
print(f"timeout = {timeout} ({type(timeout)})")
print(f"max_connections = {max_connections} ({type(max_connections)})")
```

**Expected output:**

``` text
max_retries = 5 (<class 'int'>)
timeout = 30 (<class 'int'>)
max_connections = 100 (<class 'int'>)
```

**Important points:** The dictionary stores text; the resulting
variables store integers. The default values are also text so the same
`int()` conversion handles both paths.

**Common mistakes:** Directly indexing a missing key; forgetting to
convert the default; assuming `int()` can convert arbitrary text.

**Optional challenge --- handle invalid numeric text:**

``` python
raw_settings["timeout"] = "soon"

try:
    timeout = int(raw_settings.get("timeout", "10"))
except ValueError:
    timeout = 10

print(timeout)
```

`ValueError` occurs because `"soon"` is not an integer representation.
The fallback sets `timeout` to `10`.

------------------------------------------------------------------------

## Question 13 --- Compare visitor sets across two days

**What the problem asks:** Find visitors present on both days, only
Monday, either day, and exactly one day. Also check whether an empty
Wednesday set overlaps with Monday.

**Reasoning:** Convert each visitor list to a set first to remove
repeated visits. Then: - Intersection (`&`) = in both sets - Difference
(`-`) = in the first set but not the second - Union (`|`) = in either
set - Symmetric difference (`^`) = in exactly one set - `isdisjoint()` =
no shared values

**Solution:**

``` python
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

**Expected output:**

``` text
Both days: ['bo', 'chen']
Only Monday: ['ana']
Either day: ['ana', 'bo', 'chen', 'dee']
Exactly one day: ['ana', 'dee']
Wednesday empty? True
```

**Important points:** Difference is directional: `A - B` is not the same
as `B - A`. An empty set is disjoint from every set because it contains
no values.

**Common mistake:** Confusing union (everyone from either day) with
symmetric difference (visitors from one day only).

**Optional challenge --- make Wednesday overlap with Monday:**

``` python
wednesday_set = {"ana", "eli"}
print(wednesday_set.isdisjoint(monday_set))  # False
```

------------------------------------------------------------------------

## Question 14 --- Compare words with Unicode-aware case folding

**What the problem asks:** Loop through pairs of words, unpack each
tuple, normalize both strings with `.casefold()`, and compare them.

**Reasoning:** `.casefold()` is designed for case-insensitive text
comparison. It is more aggressive than `.lower()`. For example,
`"Straße".casefold()` becomes `"strasse"`. Casefolding does not remove
accents, so `"cafe"` and `"café"` remain different.

**Solution:**

``` python
raw_entries = [
    ("Straße", "STRASSE"),
    ("Cafe", "café"),
    ("Hello", "world"),
]

for original, candidate in raw_entries:
    normalized_original = original.casefold()
    normalized_candidate = candidate.casefold()
    same_word = normalized_original == normalized_candidate
    print(f'"{original}" vs "{candidate}" -> same word? {same_word}')
```

**Expected output:**

``` text
"Straße" vs "STRASSE" -> same word? True
"Cafe" vs "café" -> same word? False
"Hello" vs "world" -> same word? False
```

**Important points:** The loop unpacks each two-value tuple into
`original` and `candidate`. `==` compares the normalized values. Case
folding handles case differences; it does not make unrelated words equal
or strip accents.

**Common mistakes:** Using `.lower()` for the German `ß` example;
assuming casefold removes accents; comparing the original strings
without normalization.

**Optional challenge --- ignore leading/trailing spaces too:**

``` python
original = " Hello"
candidate = "hello "
same_word = original.strip().casefold() == candidate.strip().casefold()
print(same_word)  # True
```

------------------------------------------------------------------------

## Question 15 --- Distinguish `None`, zero, equality, and identity

**What the problem asks:** Report a real rating of `0` as an answer,
report a missing bonus score represented by `None` as unanswered, then
compare two equal integers using `==` and `is`.

**Reasoning:** Zero is falsy, but it is still a real value. `None`
represents no value. Therefore, check `is None`, not `if value`. `==`
checks whether values are equal; `is` checks whether two names refer to
the exact same object.

**Solution:**

``` python
survey_responses = {
    "rating": 0,
    "comment": "none yet",
    "bonus_score": None,
}

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

x = int("1000")
y = int("1000")
print(x == y)
print(x is y)
```

**Expected output on typical CPython builds:**

``` text
Rating: 0
Bonus score was never answered.
True
False
```

**Important qualification:** The first two lines and `x == y` are stable
results. The result of `x is y` for ordinary integers is not guaranteed
by the Python language; object reuse is an implementation detail. It
will commonly be `False` for these separately constructed integers in
CPython, but do not build program logic around that. Use `==` for values
and `is None` for the `None` check.

**Common mistakes:** Writing `if rating:` and incorrectly treating zero
as unanswered; using `is` to compare ordinary numbers.

**Optional challenge --- `False` is an answered value:**

``` python
agreed_to_terms = False

if agreed_to_terms is None:
    print("Never answered")
else:
    print(f"Answered: {agreed_to_terms}")
```

------------------------------------------------------------------------

# Advanced questions

## Question 16 --- Build an inventory summary

**What the problem asks:** Print every product and quantity, calculate
total units, identify products below a threshold, and safely look up a
product that is not in the dictionary.

**Reasoning:** `.items()` gives each key-value pair. `.values()` gives
the quantities, which can be passed to `sum()`. Use a list to collect
low-stock product names. Use `.get()` for a product that may be missing.

**Solution:**

``` python
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
    print(
        f"Low stock (below {low_stock_threshold} units):",
        sorted(low_stock_items),
    )
else:
    print("No products are low on stock.")

requested_product = "eggs"
quantity_on_hand = inventory.get(requested_product, 0)
print(f"\n{requested_product}: {quantity_on_hand} units on hand")
```

**Expected output:**

``` text
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

**Important points:** `"milk": 0` is a real inventory entry with zero
units. It is different from `"eggs"`, which is absent from the
dictionary. Both can produce a numeric zero in this example, so the
program should preserve the distinction when business logic needs it.
`<10` means strictly below 10.

**Common mistakes:** Using `inventory["eggs"]` and triggering
`KeyError`; dropping milk because its value is zero; forgetting to sort
the low-stock list.

**Optional challenge --- apply restock quantities:**

``` python
restock_amounts = {"bread": 20, "milk": 12}

for product, amount in restock_amounts.items():
    inventory[product] = inventory.get(product, 0) + amount

print(inventory)
```

------------------------------------------------------------------------

## Question 17 --- Analyze student scores

**What the problem asks:** Print each student's pass/fail status,
calculate class statistics, report `all()` and `any()` pass results, and
identify the top student.

**Reasoning:** Keep each student's name and score together in a tuple.
Build a list of scores for numeric calculations. Use one passing
threshold consistently. To find the top student, track the name and
score together rather than using `max(scores)` alone.

**Solution:**

``` python
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

**Expected output:**

``` text
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

**Important points:** The average is `315 / 4 = 78.75`, displayed as
`78.8`. `all()` is false because Marie failed. `any()` is true because
at least one student passed. The `>` comparison updates the top student
only when a strictly higher score is found.

**Common mistakes:** Losing the name when calculating `max(scores)`;
using different pass thresholds in different parts of the program;
dividing by zero if the student list is empty (the exercise assumes at
least one student).

**Optional challenge --- collect names of students who passed:**

``` python
passed_names = []
for name, score in student_scores:
    if score >= passing_threshold:
        passed_names.append(name)

print(passed_names)
```

------------------------------------------------------------------------

## Question 18 --- Compare article tags after cleaning

**What the problem asks:** Create a function that trims and casefolds
tags, removes duplicates, and compares two articles' tag sets.

**Reasoning:** Clean each tag before adding it to a set. This makes
`"Python"`, `" python"`, and `"python "` become the same normalized tag.
Set operations then compare already-clean values.

**Solution:**

``` python
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
print(
    "Do the articles share any tag at all?",
    not tags_a.isdisjoint(tags_b),
)
```

**Expected output:**

``` text
Article A tags: ['ai', 'beginner', 'python']
Article B tags: ['advanced', 'ai', 'python', 'tips']
Shared tags: ['ai', 'python']
Only in A: ['beginner']
Only in B: ['advanced', 'tips']
All tags combined: ['advanced', 'ai', 'beginner', 'python', 'tips']
Do the articles share any tag at all? True
```

**Important points:** A function avoids repeating the same cleaning
logic. `&` means intersection, `-` means difference, and `|` means
union. `not isdisjoint(...)` means the sets share at least one item.

**Common mistakes:** Comparing raw tags before normalization; confusing
`tags_a - tags_b` with `tags_b - tags_a`; forgetting that a set has no
guaranteed display order.

**Optional challenge --- add a third article and find tags common to all
three:**

``` python
article_c_raw = ["AI", "python", "data"]
tags_c = clean_tags(article_c_raw)

common_to_all = tags_a & tags_b & tags_c
print(sorted(common_to_all))
```

------------------------------------------------------------------------

## Question 19 --- Update a profile without confusing empty values

**What the problem asks:** Update a profile while distinguishing a new
field, a present field whose value is `None`, and a field with an
existing value. Convert the new age from text to an integer.

**Reasoning:** `.get(field)` returns `None` both when a key is absent
and when a key exists with value `None`. Therefore, also test
`field not in profile`: - `current_value is None` and key absent →
brand-new field - `current_value is None` and key present → previously
unset field - otherwise → existing value is being overwritten

An empty string `""` and `False` are real values. Do not treat them as
missing merely because they are falsy.

**Solution:**

``` python
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

**Expected output:**

``` text
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

**Important clarification:** In this exercise, `"bio": ""` is a real
existing value, so it is classified as an overwrite.
`"referral_code": None` is a present field whose value is unset, so it
is classified as being filled in. `"age"` is absent, so it is brand new.
The final referral-code check reports a code because the update supplied
one; if that update is removed, the final message says no code is on
file.

**Common mistakes:** Using `if current_value:` and misclassifying `""`
or `False`; failing to check key membership; converting age before the
update has created the key.

**Optional challenge --- update the real `False` field:**

``` python
updates["newsletter_opt_in"] = True
```

When applied by the same loop, it is correctly reported as an overwrite
because `False` is a real existing value, not `None`.

------------------------------------------------------------------------

## Question 20 --- Clean contact records and remove duplicates

**What the problem asks:** Clean names and emails in a list of
dictionaries, then keep only the first record for each cleaned email
address.

**Reasoning:** Normalize the email before checking duplicates. Use a set
(`seen_emails`) to remember which cleaned email addresses have already
been kept. Use a list (`cleaned_contacts`) to preserve the order of the
retained records.

**Solution:**

``` python
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
        cleaned_contacts.append({
            "name": clean_name,
            "email": clean_email,
        })

print(f"Raw contact count: {len(raw_contacts)}")
print(f"Unique contact count: {len(cleaned_contacts)}")
print()

for contact in cleaned_contacts:
    print(f"{contact['name']:<15} {contact['email']}")
```

**Expected output:**

``` text
Raw contact count: 4
Unique contact count: 3

Ada Lovelace    ada@example.com
Grace Hopper    grace@example.com
Alan Turing     alan@example.com
```

**Important points:** The first and third records have different raw
formatting but the same cleaned email. The first is kept; the later
duplicate is skipped. The set is used for fast membership checks, while
the list preserves the order of accepted records.

**Common mistakes:** Checking the raw email instead of the cleaned
email; appending a record before checking for duplicates; forgetting to
add each accepted email to `seen_emails`.

**Production caveat:** This exercise intentionally treats the entire
email address as case-insensitive. A production system should follow the
normalization rules of its identity/account model rather than assuming
that every email provider treats every part of an address identically.

**Optional challenge --- collect duplicate emails that were skipped:**

``` python
# Add this before the loop:
duplicate_emails = []

# Replace the existing if block inside the loop with:
if clean_email not in seen_emails:
    seen_emails.add(clean_email)
    cleaned_contacts.append({
        "name": clean_name,
        "email": clean_email,
    })
else:
    duplicate_emails.append(clean_email)

# After the loop:
print("Skipped duplicate emails:", duplicate_emails)
```

------------------------------------------------------------------------

# Final review --- what these 20 questions teach

  ---------------------------------------------------------------------
  Concept                                Questions What you should now
                                                   be able to do
  -------------------- --------------------------- --------------------
  Variables and basic                1, 12, 15, 19 Choose the right
  types                                            type and distinguish
                                                   `None` from real
                                                   falsy values

  Operators and                            2, 3, 6 Calculate values,
  formatting                                       slice text, and
                                                   format output

  Lists and mutation             4, 10, 11, 16, 20 Modify collections
                                                   and understand
                                                   aliasing/copying

  Tuples and unpacking                   5, 14, 17 Group fixed values
                                                   and unpack them
                                                   safely

  Dictionaries                   8, 12, 16, 19, 20 Store named data and
                                                   handle missing keys

  Sets                               9, 13, 18, 20 Remove duplicates
                                                   and compare groups

  Conversion and                 7, 12, 15, 16, 19 Convert values and
  truthiness                                       avoid confusing
                                                   falsy with missing

  Mutability and                        10, 11, 15 Explain shared
  identity                                         references,
                                                   shallow/deep copies,
                                                   `==`, and `is`
  ---------------------------------------------------------------------

## Completion checklist

-   [ ] I can explain each solution without simply memorizing the code.
-   [ ] I can predict the output before running each program.
-   [ ] I understand why `None`, `0`, `False`, and `""` are different.
-   [ ] I can explain why a list alias changes through both names.
-   [ ] I can distinguish a shallow copy from a deep copy.
-   [ ] I can use `.get()` when a dictionary key may be missing.
-   [ ] I can choose the correct set operation for a comparison.
-   [ ] I know that `==` compares values and `is` compares object
    identity.
-   [ ] I can modify each solution with a different input and explain
    the new output.

**Suggested practice method:** Re-type each program yourself, run it,
change one input, predict the new output, and then verify your
prediction. Do not move to the next Python topic until you can explain
the reasoning behind these solutions.
