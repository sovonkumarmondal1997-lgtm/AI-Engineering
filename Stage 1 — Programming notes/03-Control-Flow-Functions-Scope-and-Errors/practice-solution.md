# Stage 1 — Control Flow, Functions, Scope, and Errors
## Complete Solutions to All 40 Practice Questions

**Scope:** Topics 01–07 of `03-Control-Flow-Functions-Scope-and-Errors`.  
**Python version:** Python 3.10+ (required for `match`/`case`).  
**Approach:** Each question includes runnable code and concise line-by-line notes. The solutions use only concepts in this module and the earlier Python foundations.

## 1. Current learning level and permitted concepts

The roadmap places this module after computational thinking and Python core language/data types. The relevant foundations include variables, expressions, operators, strings, lists, tuples, dictionaries, type conversion, truthiness, mutability, and unpacking.

| Topic | Concepts used in these solutions |
|---|---|
| 01 — Conditionals | `if`/`elif`/`else`, comparisons, Boolean logic, short-circuiting, guards, `match`/`case` |
| 02 — Loops | `for`, `while`, `range`, `break`, `continue`, `enumerate`, `zip` |
| 03 — Functions | `def`, parameters, return values |
| 04 — Arguments | positional/keyword arguments, defaults, keyword-only arguments, docstrings |
| 05 — Scope | local/global names, lifetime, hidden dependencies |
| 06 — Function design | pure functions, side effects, mutable arguments |
| 07 — Errors | validation, standard exceptions, `try`/`except`/`else`/`finally`, `raise`, one custom exception |

The roadmap also lists later subjects such as algorithmic habits, testing, file I/O, OOP, generators, advanced typing, and packaging. They are not needed here and are deliberately excluded. A folder or project appearing in a roadmap is not evidence that it has already been completed.

---

# Part A — Control Flow (A1–A20)

Part A deliberately uses no user-defined functions, matching the practice file's instruction that functions begin in Topic 03.

## Basic: A1–A5

### A1 — Even or odd

```python
number = 17

if number % 2 == 0:
    print(f"{number} is even.")
else:
    print(f"{number} is odd.")
```

**Line notes**
- Store the test integer. `% 2` gives its remainder; `0` means even, otherwise odd. The branches print one result.


### A2 — Average and empty-list guard

```python
scores_a = []
scores_b = [70, 85, 90]

if len(scores_a) > 0 and sum(scores_a) / len(scores_a) >= 75:
    print("Group A meets the threshold.")
elif len(scores_a) == 0:
    print("Group A has no scores.")
else:
    print("Group A is below the threshold.")

if len(scores_b) > 0 and sum(scores_b) / len(scores_b) >= 75:
    print("Group B meets the threshold.")
elif len(scores_b) == 0:
    print("Group B has no scores.")
else:
    print("Group B is below the threshold.")
```

**Line notes**
- Define empty and populated groups. Put the non-empty guard first: `and` short-circuits before division on an empty list. `elif` reports no data; `else` reports a below-threshold average.


### A3 — Number items with a manual counter

```python
fruits = ["apple", "banana", "cherry"]
count = 0

for fruit in fruits:
    count = count + 1
    print(count, fruit)
```

**Line notes**
- Store the fruit list and initialize `count`. Each pass increments before printing, producing 1-based numbering.


### A4 — Countdown

```python
countdown = 5

while countdown > 0:
    print(countdown)
    countdown = countdown - 1

print("Go!")
```

**Line notes**
- Start at five. The `while` condition controls repetition; print then decrement so it terminates at zero. Print `Go!` after the loop.


### A5 — Multiples of three

```python
for number in range(3, 31, 3):
    print(number)
```

**Line notes**
- `range(3, 31, 3)` starts at 3, steps by 3, and excludes 31; therefore 30 is included.


## Moderate: A6–A10

### A6 — Letter grade

```python
score = 74

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"

print(f"Score {score} -> Grade {grade}")
```

**Line notes**
- Check grade thresholds from highest to lowest. The first true branch assigns the grade; `else` handles scores below 70.


### A7 — PIN validation

```python
pin = "12a4"

if pin == "":
    print("Error: PIN cannot be empty.")
elif not pin.isdigit():
    print("Error: PIN must contain only digits.")
elif len(pin) != 4:
    print("Error: PIN must be exactly 4 digits.")
else:
    print("PIN accepted.")
```

**Line notes**
- Check empty input, non-digits, then length. The `elif` chain reports only the first failure; `else` accepts the PIN.


### A8 — Find banned words with positions

```python
words = ["hello", "scam", "world", "spam", "friend"]
banned_words = ["scam", "spam"]

for position, word in enumerate(words, start=1):
    if word in banned_words:
        print(f"Word {position}: '{word}' is banned.")
```

**Line notes**
- `enumerate(..., start=1)` supplies position and word. Membership in `banned_words` determines whether that word is printed.


### A9 — Skip negatives and stop at zero

```python
numbers = [4, -2, 7, 0, 9, -5]

for number in numbers:
    if number < 0:
        continue
    if number == 0:
        break
    print(number)
```

**Line notes**
- `continue` skips negative values. `break` exits at zero. Printing after both checks prints only positive values before zero.


### A10 — Pair names and scores

```python
names = ["Ada", "Grace", "Alan"]
scores = [92, 88, 76]

for name, score in zip(names, scores):
    print(name, "scored", score)
```

**Line notes**
- `zip()` pairs corresponding list values; unpack each pair into `name` and `score`. It stops at the shorter list.


## Hard: A11–A15

### A11 — Classify days with `match`

```python
days = ["Mon", "Sat", "Xyz", "Sun"]

for day in days:
    match day:
        case "Sat" | "Sun":
            day_type = "Weekend"
        case "Mon" | "Tue" | "Wed" | "Thu" | "Fri":
            day_type = "Weekday"
        case _:
            day_type = "Unknown"
    print(day, "->", day_type)
```

**Line notes**
- Loop through days; `match` selects a classification. `|` combines alternatives; `_` handles unknown abbreviations. Print the classification.


### A12 — Find the highest value without `max()`

```python
number_lists = [[], [4, 9, 2, 7]]

for numbers in number_lists:
    if len(numbers) == 0:
        print("No numbers to check.")
    else:
        highest = numbers[0]
        for number in numbers:
            if number > highest:
                highest = number
        print("Highest number:", highest)
```

**Line notes**
- Check emptiness before indexing. Initialize `highest` from the first value; scan and replace it when a larger value appears.


### A13 — Report unmatched product names

```python
product_names = ["Pen", "Notebook", "Eraser", "Ruler"]
product_prices = [1.5, 2.0, 0.75]

for name, price in zip(product_names, product_prices):
    print(name, "costs", price)

print("Products without a listed price:")
for position in range(len(product_prices), len(product_names)):
    print("-", product_names[position])
```

**Line notes**
- `zip()` prints matched pairs. A second `range()` starts at the price count and indexes each remaining product name.


### A14 — Menu selection with a default case

```python
menu_selections = ["1", "2", "9", "3"]

for selection in menu_selections:
    match selection:
        case "1":
            print("Starting new game.")
        case "2":
            print("Loading saved game.")
        case "3":
            print("Exiting.")
        case _:
            print(f"'{selection}' is not a valid menu option.")
```

**Line notes**
- Loop through string selections. Exact cases perform actions; `_` rejects any other value and includes it in the message.


### A15 — Average while skipping `None`

```python
scores_a = [85, None, 92, None, 78]
scores_b = [None, None, None]

for scores in (scores_a, scores_b):
    total = 0
    count = 0
    for score in scores:
        if score is None:
            continue
        total = total + score
        count = count + 1

    if count == 0:
        print("No valid scores were recorded.")
    else:
        print(f"Average of valid scores: {total / count:.1f}")
```

**Line notes**
- Reset total/count for each list. `is None` plus `continue` skips missing values. Guard count before division; format to one decimal.


## Advanced: A16–A20

### A16 — Grade every score and count each grade

```python
scores = [95, 82, 67, 74, 58, 90]
grade_counts = {"A": 0, "B": 0, "C": 0, "F": 0}

for score in scores:
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    else:
        grade = "F"
    grade_counts[grade] = grade_counts[grade] + 1
    print(f"{score} -> {grade}")

print("Summary:", grade_counts)
```

**Line notes**
- Pre-create all grade keys. Classify each score, increment its grade's count, print the result, then display the final totals.


### A17 — Validate candidate passwords

```python
candidate_passwords = ["short1", "longenoughbutnodigit", "GoodPass1", ""]

for password in candidate_passwords:
    if password == "":
        print(password, "-> rejected: cannot be empty")
        continue

    has_digit = False
    for character in password:
        if character.isdigit():
            has_digit = True

    if len(password) < 8:
        print(password, "-> rejected: must be at least 8 characters")
    elif not has_digit:
        print(password, "-> rejected: must contain a digit")
    else:
        print(password, "-> accepted")
```

**Line notes**
- Handle empty input and continue immediately. Otherwise scan characters to set `has_digit`; the final chain checks length, digit, then acceptance.


### A18 — Four traffic-light transitions

```python
current_light = "red"
cycles = 4

while cycles > 0:
    match current_light:
        case "red":
            print("Red -> Go to Green")
            current_light = "green"
        case "green":
            print("Green -> Go to Yellow")
            current_light = "yellow"
        case "yellow":
            print("Yellow -> Go to Red")
            current_light = "red"
    cycles = cycles - 1
```

**Line notes**
- Start red with four cycles. `match` prints and updates the state. Decrement outside `match` so every pass counts exactly once.


### A19 — Search an inventory

```python
inventory = ["hammer", "wrench", "pliers"]
search_term = "wrench"

found = False
for item in inventory:
    if item == search_term:
        found = True
        print(f"'{search_term}' found in inventory.")
        break

if not found:
    print(f"'{search_term}' not found in inventory.")

empty_inventory = []
search_term_2 = "screwdriver"
found_2 = False
for item in empty_inventory:
    if item == search_term_2:
        found_2 = True
        break

if not found_2:
    print(f"'{search_term_2}' not found in inventory.")
```

**Line notes**
- Start `found` false; set true and break on a match. Check the flag after the loop. An empty list leaves it false.


### A20 — Numbered pass/fail report with unmatched names

```python
names = ["Ada", "Grace", "Alan", "Marie"]
scores = [92, 58, 74]

position = 0
for name, score in zip(names, scores):
    position = position + 1
    if score >= 60:
        result = "PASS"
    else:
        result = "FAIL"
    print(position, name, score, result)

if len(names) != len(scores):
    print("Note: some names have no matching score and were skipped:")
    for index in range(len(scores), len(names)):
        print("-", names[index])
```

**Line notes**
- `zip()` processes matched students; increment the report position and classify pass/fail. Compare lengths and index leftover names.


## Basic: B1–B5

### B1 — Return a square

```python
def square(number):
    return number * number

print(square(4))
print(square(7))
```

**Line notes**
- Define `square` with one parameter. `return` sends the calculation back; the two calls print 16 and 49.


### B2 — Calculate a total

```python
def calculate_total(price, quantity):
    return price * quantity

print(calculate_total(9.99, 3))
```

**Line notes**
- The function receives required `price` and `quantity`, multiplies them, and returns the total for the caller to print.


### B3 — Compare `print` and `return`

```python
def show_square(number):
    print(number * number)

def get_square(number):
    return number * number

show_square(5)
result = get_square(5)
print("Stored result:", result)
```

**Line notes**
- `show_square` only displays. `get_square` returns a value that can be assigned to `result` and reused.


### B4 — Reuse a returned total

```python
def calculate_total(price, quantity):
    return price * quantity

order_total = calculate_total(12.5, 2)
shipping = 4
final_amount = order_total + shipping
print(f"Final amount: ${final_amount:.2f}")
```

**Line notes**
- Return the subtotal, store it, add shipping separately, then format the final amount to two decimal places.


### B5 — Check positive numbers

```python
def is_positive(number):
    return number > 0

numbers_to_check = [5, -3, 0, 12]

for number in numbers_to_check:
    print(number, "->", is_positive(number))
```

**Line notes**
- Return the Boolean comparison `number > 0`. The loop calls the function for every list value.


## Moderate: B6–B10

### B6 — Positional versus keyword arguments

```python
def describe_item(name, price):
    print(f"{name} costs ${price}")

describe_item("Pen", 1.5)
describe_item(1.5, "Pen")
describe_item(price=1.5, name="Pen")
```

**Line notes**
- Positional arguments follow parameter order, so the swapped call assigns wrong meanings. Keyword arguments name each destination explicitly.


### B7 — Default currency

```python
def format_price(amount, currency="$"):
    return f"{currency}{amount:.2f}"

print(format_price(20))
print(format_price(20, "€"))
```

**Line notes**
- `currency` defaults to `$`. The second call overrides it with `€`; both outputs format two decimal places.


### B8 — Keyword-only tax option

```python
def calculate_total(price, quantity, *, include_tax=False):
    subtotal = price * quantity
    if include_tax:
        return subtotal * 1.08
    return subtotal

print(calculate_total(10, 2))
print(calculate_total(10, 2, include_tax=True))
```

**Line notes**
- `*` makes `include_tax` keyword-only. Calculate subtotal, apply 8% tax only when true, otherwise return subtotal.


### B9 — Docstring and `help()`

```python
def calculate_area(width, height):
    """
    Calculate the area of a rectangle.

    width is the rectangle's width.
    height is the rectangle's height.
    Returns the area as a number.
    """
    return width * height

print(calculate_area(4, 5))
help(calculate_area)
```

**Line notes**
- The triple-quoted string is the docstring. The function returns width times height; `help()` displays its documentation.


### B10 — Local shadowing and reading a global

```python
tax_rate = 0.08

def show_local_rate():
    tax_rate = 0.0
    print("Inside function:", tax_rate)

def calculate_with_tax(price):
    return price * (1 + tax_rate)

show_local_rate()
print("Outside function:", tax_rate)
print(calculate_with_tax(100))
```

**Line notes**
- The function-local `tax_rate` shadows but does not change the global. The second function reads the global value without assigning it.


## Hard: B11–B15

### B11 — Global dependency versus pure function

```python
discount_rate = 0.10

def apply_discount_impure(price):
    return price * (1 - discount_rate)

def apply_discount_pure(price, discount_rate):
    return price * (1 - discount_rate)

print(apply_discount_impure(100))
print(apply_discount_pure(100, 0.10))
```

**Line notes**
- The first function reads a hidden global dependency. The second receives the rate explicitly and is pure for the same inputs.


### B12 — Mutable default bug and safe fix

```python
def add_item_unsafe(item, items=[]):
    items.append(item)
    return items

def add_item_safe(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

print(add_item_unsafe("apple"))
print(add_item_unsafe("banana"))

print(add_item_safe("apple"))
print(add_item_safe("banana"))
```

**Line notes**
- The unsafe default list is shared across calls. `None` lets the safe function create a fresh list whenever no list is supplied.


### B13 — Make shipping fee explicit

```python
shipping_fee = 5

def calculate_total_hidden(order_total):
    return order_total + shipping_fee

def calculate_total_explicit(order_total, shipping_fee):
    return order_total + shipping_fee

print(calculate_total_hidden(50))
print(calculate_total_explicit(50, shipping_fee))
```

**Line notes**
- The first function reads global shipping state. The refactored function receives the fee explicitly, making its dependency visible.


### B14 — Validate a price and raise precise errors

```python
def validate_price(price):
    if not isinstance(price, (int, float)) or isinstance(price, bool):
        raise TypeError(f"Invalid price: {price!r}. Expected a number.")
    if price <= 0:
        raise ValueError(f"Invalid price: {price}. Must be greater than zero.")

prices = [19.99, -5, "twenty"]

for price in prices:
    try:
        validate_price(price)
        print(price, "-> valid")
    except (TypeError, ValueError) as error:
        print(price, "-> rejected:", error)
```

**Line notes**
- Reject wrong types with `TypeError` (excluding booleans); reject non-positive numbers with `ValueError`. The caller catches only these expected errors.


### B15 — Handle three specific exceptions

```python
def get_safe(dictionary, key):
    try:
        return dictionary[key]
    except KeyError:
        return "Key not found."

def get_item_safe(items, position):
    try:
        return items[position]
    except IndexError:
        return "Position not found."

def divide_safe(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "Cannot divide by zero."

print(get_safe({"a": 1}, "b"))
print(get_item_safe([1, 2, 3], 10))
print(divide_safe(10, 0))
```

**Line notes**
- Each `try` contains one risky operation. Catch only its matching `KeyError`, `IndexError`, or `ZeroDivisionError`; return a clear fallback.


## Advanced: B16–B20

### B16 — Safe shopping-cart updater

```python
def add_to_cart(item, cart=None):
    if not isinstance(item, str) or item == "":
        raise ValueError("Item name must be a non-empty string.")
    if cart is None:
        cart = []
    cart.append(item)
    return cart

cart_one = add_to_cart("Apples")
cart_two = add_to_cart("Bread")

print("Cart one:", cart_one)
print("Cart two:", cart_two)

try:
    add_to_cart("")
except ValueError as error:
    print("Rejected:", error)
```

**Line notes**
- Validate the item first. `None` triggers a fresh cart; append and return it. The caller catches the invalid empty item.


### B17 — Discount calculation with all exception blocks

```python
def calculate_discounted_price(price, discount_percentage):
    if discount_percentage < 0 or discount_percentage > 100:
        raise ValueError(
            f"Invalid discount_percentage: {discount_percentage}. Expected 0-100."
        )
    return price * (1 - discount_percentage / 100)

requests = [(100, 20), (50, 150), (80, 10)]

for price, discount in requests:
    try:
        final_price = calculate_discounted_price(price, discount)
    except ValueError as error:
        print("Skipped:", error)
    else:
        print(f"Final price: ${final_price:.2f}")
    finally:
        print("Processed one request.")
```

**Line notes**
- Validate percentage and return the discounted price. `except` handles failure, `else` success, and `finally` runs for every request.


### B18 — Collect multiple registration errors

```python
def validate_registration(data):
    errors = []

    if "name" not in data or data["name"] == "":
        errors.append("Name is required.")

    if "age" not in data:
        errors.append("Age is required.")
    else:
        try:
            age = int(data["age"])
            if age < 0 or age > 120:
                errors.append(f"Age must be between 0 and 120, got {age}.")
        except ValueError:
            errors.append(f"Age must be a whole number, got '{data['age']}'.")

    return errors

submissions = [
    {"name": "Ada", "age": "30"},
    {"name": "", "age": "abc"},
]

for submission in submissions:
    errors = validate_registration(submission)
    if errors:
        print("Rejected:", errors)
    else:
        print("Accepted.")
```

**Line notes**
- Collect errors in a list. Check key presence before lookup; parse age in `try`, catch `ValueError`, check range, and return all messages. Assumes present age is int-convertible text/value.


### B19 — Safe withdrawal and state update

```python
def withdraw(balance, amount):
    if amount > balance:
        raise ValueError(f"Cannot withdraw {amount}; balance is only {balance}.")
    return balance - amount

balance = 100

for amount in [30, 200]:
    try:
        new_balance = withdraw(balance, amount)
    except ValueError as error:
        print("Transaction failed:", error)
    else:
        balance = new_balance
        print("New balance:", balance)
    finally:
        print("Transaction attempt complete.")
```

**Line notes**
- `withdraw` validates and returns a proposed balance without mutating outer state. Update balance only in `else`; `finally` always runs.


### B20 — Minimal custom exception for order transitions

```python
class InvalidTransitionError(Exception):
    pass

def change_order_status(current_status, requested_status):
    allowed_next = {
        "NEW": "PAID",
        "PAID": "SHIPPED",
        "SHIPPED": "DELIVERED"
    }

    if requested_status != allowed_next.get(current_status):
        raise InvalidTransitionError(
            f"Cannot go from {current_status} to {requested_status}."
        )
    return requested_status

status = "NEW"
requested_sequence = ["PAID", "DELIVERED", "SHIPPED"]

for requested_status in requested_sequence:
    try:
        status = change_order_status(status, requested_status)
        print("Status is now:", status)
    except InvalidTransitionError as error:
        print("Rejected:", error)
```

**Line notes**
- Define the required custom exception. The map defines allowed next states; invalid transitions raise. Assign returned status only after success, preserving state after rejection.


## 3. Key learning checks

After completing these 40 exercises, you should be able to explain and apply:

1. **Control flow:** choose a condition, order guard checks, and handle default cases.
2. **Loop control:** distinguish `break` (exit loop) from `continue` (skip current pass).
3. **Iteration helpers:** use `range`, `enumerate`, and `zip`, including their boundary behavior.
4. **Functions:** distinguish parameters from arguments and `return` from `print`.
5. **Arguments:** use positional, keyword, default, and keyword-only arguments correctly.
6. **Scope:** identify local variables, global reads, shadowing, and hidden dependencies.
7. **Function design:** explain why explicit inputs support pure, predictable functions.
8. **Mutable defaults:** explain why a default list is shared and how `None` avoids that bug.
9. **Validation and errors:** validate before risky operations, raise meaningful exceptions, and catch only expected exception types.
10. **Exception flow:** explain the different roles of `try`, `except`, `else`, and `finally`.

**Important boundary:** These exercises demonstrate the concepts at the current module level. They do not establish that later roadmap topics or the listed Stage 1 projects have been completed.
