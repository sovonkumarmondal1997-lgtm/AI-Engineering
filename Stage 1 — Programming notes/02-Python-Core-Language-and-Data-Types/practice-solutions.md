# Python Core Language and Data Types --- 20 Exercise Solutions

## Current learning level and scope

Your Stage 1 roadmap progresses from computational thinking into Python
fundamentals, control flow, collections, files and CLI programs,
modules, testing, debugging, and object-oriented design. Based on the
lessons completed in our learning sequence, you have studied Python
files/interpreter/REPL, variables and basic types, operators, strings,
lists, tuples, dictionaries, sets, type conversion, truthiness, and
mutability.

You are currently consolidating the early Python foundations. These 20
exercises integrate Topics 01--10 and are appropriate revision. The
project tree describes the planned curriculum; it does not prove
independent mastery. Your practical level is best verified by running
these programs, predicting their output, and then reproducing them
without looking.

The solutions below stay within the file's scope. Question 11 uses
`copy.deepcopy()` because that exercise explicitly requires it.
Functions and loops are used only where the exercise itself requires
them or where they have already been introduced.

------------------------------------------------------------------------

## Basic questions (1--5)

### 1. Variables and types

``` python
full_name = "Maria Alvarez"  # str
age = 21                     # int
height_m = 1.68              # float
is_student = True            # bool
middle_name = None           # no value supplied

print(f"{full_name} ({type(full_name)})")
print(f"{age} ({type(age)})")
print(f"{height_m} ({type(height_m)})")
print(f"{is_student} ({type(is_student)})")
print(f"{middle_name} ({type(middle_name)})")
```

The assignments create the requested types; type() verifies them. None
means unknown, unlike an empty string or zero.

### 2. Shopping calculation

``` python
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

Calculate item subtotal, discount on items only, then add shipping. The
format specifier prints two decimal places.

### 3. String indexing and slicing

``` python
word = "backpropagation"
print(word[0])
print(word[-1])
print(word[:4])
print(word[4:9])
print(word[::-1])
```

Indexes select single characters; slices select ranges. The stop is
excluded and a negative step reverses the string.

### 4. List operations

``` python
favorite_movies = ["Arrival", "Coco", "Spirited Away"]
favorite_movies.append("The Matrix")
favorite_movies[1] = "Inside Out"

print(favorite_movies)
print(favorite_movies[0])
print(favorite_movies[-1])
print(len(favorite_movies))
```

append() adds at the end; index assignment replaces an item. Negative
indexing gets the last item; len() counts the list.

### 5. Tuple unpacking and swapping

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

The tuple stores the coordinate pair. Unpacking assigns each value; the
right side is evaluated before the swap.

### 6. Clean name and email

``` python
raw_name = "  ada LOVELACE  "
raw_email = "  ADA@Example.COM "
clean_name = raw_name.strip().title()
clean_email = raw_email.strip().lower()

print(f"Name: {clean_name}")
print(f"Email: {clean_email}")
print(f"[{clean_name:<20}] length={len(clean_name)}")
```

strip() trims whitespace; title() and lower() normalize case. The
f-string aligns the name and reports its cleaned length.

### 7. Convert ages and evaluate truthiness

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
print(all(filled_flags), any(filled_flags))
```

int() converts ages before addition. bool() creates truth flags; all()
requires all true, while any() requires one true.

### 8. Safe dictionary lookup

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

.get() returns a value, None, or a supplied default. The loop totals
available prices; unknown prices should be flagged in real checkout.

### 9. Unique tags

``` python
submitted_tags = ["python", "ai", "python", "beginner", "ai", "python"]
unique_tags = set(submitted_tags)
print(sorted(unique_tags))
print(len(submitted_tags), len(unique_tags))
print("ml" in unique_tags)
print("python" in unique_tags)
```

set() removes duplicates, sorted() orders them, len() counts them, and
in checks membership.

### 10. Aliasing versus copying

``` python
playlist_original = ["Song A", "Song B", "Song C"]
playlist_alias = playlist_original
playlist_alias.append("Song D")
print(playlist_original, playlist_alias)

playlist_copy = playlist_original.copy()
playlist_copy.append("Song E")
print(playlist_original, playlist_copy)
```

Assignment creates an alias, so mutation is shared. copy() creates a
separate list, so its mutation does not affect the original.

### 11. Shallow and deep copies

``` python
import copy

classroom = [["Ada", "Grace"], ["Alan"]]
shallow = classroom.copy()
shallow[0].append("Marie")
print(classroom, shallow)

shallow.append(["Linus"])
print(classroom, shallow)

deep = copy.deepcopy(classroom)
deep[0].append("Katherine")
print(classroom, deep)
```

A shallow copy shares nested lists; deepcopy() duplicates nested lists
too, so later inner mutations are independent.

### 12. Convert application settings

``` python
raw_settings = {"max_retries": "5", "timeout": "30"}
max_retries = int(raw_settings.get("max_retries", "3"))
timeout = int(raw_settings.get("timeout", "10"))
max_connections = int(raw_settings.get("max_connections", "100"))

print(max_retries, type(max_retries))
print(timeout, type(timeout))
print(max_connections, type(max_connections))
```

.get() supplies stored text or a default; int() converts every setting
to an integer.

### 13. Compare visitor sets

``` python
monday_set = set(["ana", "bo", "ana", "chen", "bo"])
tuesday_set = set(["bo", "dee", "chen", "chen"])

print(sorted(monday_set.intersection(tuesday_set)))
print(sorted(monday_set.difference(tuesday_set)))
print(sorted(monday_set.union(tuesday_set)))
print(sorted(monday_set.symmetric_difference(tuesday_set)))

empty_set = set()
print(empty_set.isdisjoint(monday_set))
```

Intersection finds shared visitors; difference finds one-sided visitors;
union combines them; symmetric difference finds exactly-one-day
visitors.

### 14. Case-insensitive word comparison

``` python
raw_entries = [("Straße", "STRASSE"), ("Cafe", "café"), ("Hello", "world")]
for original, candidate in raw_entries:
    same_word = original.casefold() == candidate.casefold()
    print(f'"{original}" vs "{candidate}" -> {same_word}')
```

The loop unpacks each pair. casefold() ignores case but does not remove
accents.

### 15. `None`, equality, and identity

``` python
survey = {"rating": 0, "comment": "none yet", "bonus_score": None}
rating = survey.get("rating")
if rating is None:
    print("Rating unanswered")
else:
    print("Rating:", rating)

bonus = survey.get("bonus_score")
if bonus is None:
    print("Bonus score unanswered")

x = 1000
y = int("1000")
print(x == y)
print(x is y)
```

is None distinguishes unset data from zero. == compares values; is
checks identity and should not compare ordinary numbers.

### 16. Inventory summary

``` python
inventory = {"apples": 42, "bread": 5, "milk": 0, "rice": 120}
threshold = 10
low_stock = []

for product, quantity in inventory.items():
    if quantity < threshold:
        low_stock.append(product)

total_units = sum(inventory.values())
for product, quantity in inventory.items():
    print(f"{product:<10}{quantity:>5} units")

print("Total units:", total_units)
print("Low stock:", sorted(low_stock))
print("eggs:", inventory.get("eggs", 0), "units on hand")
```

.items() supplies product/quantity pairs. The loop finds low stock;
sum() totals inventory and get() handles missing products.

### 17. Student-score analyzer

``` python
student_scores = [("Ada", 92), ("Grace", 78), ("Alan", 85), ("Marie", 60)]
scores = []
for name, score in student_scores:
    scores.append(score)

average = sum(scores) / len(scores)
passed_flags = []
threshold = 70
for score in scores:
    passed_flags.append(score >= threshold)

for name, score in student_scores:
    status = "PASS" if score >= threshold else "FAIL"
    print(f"{name:<10}{score:>4} {status}")

print("Average:", average)
print("Highest:", max(scores), "Lowest:", min(scores))
print("Everyone passed:", all(passed_flags))
print("At least one passed:", any(passed_flags))

top_name, top_score = student_scores[0]
for name, score in student_scores:
    if score > top_score:
        top_name, top_score = name, score
print("Top student:", top_name, top_score)
```

Tuple unpacking keeps names paired with scores. Loops and built-ins
calculate statistics, pass flags, statuses, and the top student.

### 18. Compare article tags

``` python
def clean_tags(raw_tags):
    cleaned = set()
    for tag in raw_tags:
        cleaned.add(tag.strip().casefold())
    return cleaned

article_a = clean_tags(["Python", " python", "AI", "Beginner", "ai "])
article_b = clean_tags(["python", "Advanced", "TIPS", " AI"])

print(sorted(article_a))
print(sorted(article_b))
print(sorted(article_a & article_b))
print(sorted(article_a - article_b))
print(sorted(article_b - article_a))
print(sorted(article_a | article_b))
print(not article_a.isdisjoint(article_b))
```

The function trims and casefolds tags before set operations calculate
shared, unique, and combined tags.

### 19. Safe profile updater

``` python
profile = {
    "username": "grace92", "bio": "",
    "newsletter_opt_in": False, "referral_code": None
}
updates = {
    "bio": "Engineer and lifelong learner.",
    "age": "34", "referral_code": "REF-2026"
}

for field, new_value in updates.items():
    current = profile.get(field)
    if current is None and field not in profile:
        print("Adding:", field)
    elif current is None:
        print("Filling previously unset:", field)
    else:
        print("Overwriting:", field)
    profile[field] = new_value

profile["age"] = int(profile["age"])
print(profile)
print(profile.get("referral_code") is None)
```

The update loop checks key existence and None separately, preserving the
distinction between missing, unset, and real falsy values.

### 20. Clean and deduplicate contacts

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
    name = contact["name"].strip().title()
    email = contact["email"].strip().casefold()
    if email not in seen_emails:
        seen_emails.add(email)
        cleaned_contacts.append({"name": name, "email": email})

print(len(raw_contacts), len(cleaned_contacts))
for contact in cleaned_contacts:
    print(contact)
```

Normalize each email before duplicate checking. The set tracks seen
addresses; the list retains only the first matching contact.
