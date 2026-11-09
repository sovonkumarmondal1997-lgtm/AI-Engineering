# Module 03 — Practice Questions: Complete Solutions and Line-by-Line Explanations

**Roadmap:** Stage 1 → Module 03  
**Coverage:** A1–A20 and B1–B20. **Scope:** Topics 01–07; Python 3.10+ for `match`/`case`.

---

## 1. Your current learning level and scope review

### Where this practice file fits

The current roadmap places this file in **Stage 1 → Module 03 — Control Flow, Functions, Scope, and Errors**, alongside seven lessons: conditionals and guards; loops; functions and return values; argument design and docstrings; scope and global state; pure functions and side effects; and exceptions, validation, and useful errors. The Stage 1 overview also defines four stage-level projects: a personal expense ledger CLI, a log investigation and reliability CLI, a data quality and transformation pipeline, and a rule-based risk review engine.

The module's seven lessons build in a deliberate order: conditions and guards; loops; functions and return values; argument design and docstrings; scope and global state; pure functions and side effects; then exceptions, validation, and useful errors. The attached practice file explicitly rehearses these Topics 01–07 and earlier Python foundations.

### Current level assessment

Your demonstrated level is **beginner progressing toward intermediate Python programming**. You have studied the prerequisites these questions combine: control flow, loops, functions, arguments, scope, mutability, pure functions, collections, parsing, and exceptions.

Solutions stay within Topics 01–07 and earlier foundations: conditionals, loops, functions, argument design, scope, pure functions, collections, validation, and exception handling. No files, databases, APIs, decorators, recursion, comprehensions, external libraries, testing frameworks, or advanced OOP are introduced. The single custom exception is explicitly allowed by the module.

Study method: predict the output, run the code, then compare your prediction with the execution-order explanation. Blank lines are for readability and do not execute.

---

# Part A — Control Flow Practice (A1–A20)

Part A deliberately uses top-level code only. Functions are not introduced until Topic 03, so none are used in these first 20 solutions.

## Basic — A1 to A5

### A1. Even or odd

```python
number = 17

if number % 2 == 0:
    print(f"{number} is even.")
else:
    print(f"{number} is odd.")
```

**Line by line**

1. `number = 17` stores the number to test.
2. `number % 2` calculates the remainder after division by two.
3. `== 0` checks whether that remainder is zero; even numbers have remainder zero.
4. The `if` branch prints the even message when the condition is true.
5. Otherwise, `else` prints the odd message.

**Output:** `17 is odd.`

**Edge cases:** zero is even; negative integers also work. Do not use `/` because it performs division rather than remainder calculation.

### A2. Average threshold with short-circuit protection

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

**Line by line**

1. `scores_a` is deliberately empty; `scores_b` contains three scores.
2. In each combined condition, `len(scores) > 0` is evaluated first.
3. Python's `and` short-circuits: if the first condition is false, the division on the right is not evaluated.
4. The `elif` distinguishes an empty group from a non-empty group whose average is below 75.
5. For Group B, the average is `(70 + 85 + 90) / 3 = 81.67`, so it meets the threshold.

**Output**
```text
Group A has no scores.
Group B meets the threshold.
```

**Important:** putting the division before the length check would raise `ZeroDivisionError` for Group A.

### A3. Number fruits with a manual counter

```python
fruits = ["apple", "banana", "cherry"]

count = 0
for fruit in fruits:
    count = count + 1
    print(count, fruit)
```

**Line by line**

1. `fruits` stores the three values.
2. `count = 0` initializes the counter before the loop.
3. The `for` loop visits each fruit in order.
4. `count = count + 1` increments before printing, so the first item is numbered 1.
5. `print(count, fruit)` prints the current position and value.

**Output**
```text
1 apple
2 banana
3 cherry
```

If the increment happened after `print`, the first item would incorrectly be numbered zero. The counter must be initialized or Python would raise `NameError`.

### A4. Countdown with `while`

```python
countdown = 5

while countdown > 0:
    print(countdown)
    countdown = countdown - 1

print("Go!")
```

**Line by line**

1. The countdown starts at five.
2. `while countdown > 0` repeats while the condition is true.
3. The current number is printed.
4. The value is reduced by one on every iteration; this update guarantees progress toward the stopping condition.
5. Once the value reaches zero, the loop ends.
6. `"Go!"` is outside the loop, so it prints once after the countdown.

**Output:** `5`, `4`, `3`, `2`, `1`, then `Go!` on separate lines.

Forgetting line 4 creates an infinite loop. Indentation determines which statements belong to the loop.

### A5. Multiples of three

```python
for number in range(3, 31, 3):
    print(number)
```

**Line by line**

1. `range(3, 31, 3)` starts at 3, advances by 3, and stops before 31.
2. Because the stop is exclusive, 31 allows 30 to be included.
3. The `for` loop assigns each generated value to `number`.
4. `print(number)` displays each multiple.

**Output:** `3, 6, 9, 12, 15, 18, 21, 24, 27, 30`, one per line.

`range(3, 30, 3)` would omit 30.

## Moderate — A6 to A10

### A6. Score to letter grade

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

**Line by line**

1. `score` stores the test score.
2. The first condition checks the highest band (90 and above).
3. If it fails, the next condition checks 80 and above.
4. If that fails, the next checks 70 and above.
5. `else` catches scores below 70.
6. The final f-string prints the original score and selected grade.

**Output:** `Score 74 -> Grade C`

Order matters: check from highest to lowest. Use `>=` so boundary values 90, 80, and 70 enter the intended band.

### A7. Validate a four-digit PIN

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

**Line by line**

1. `pin` stores the candidate as text, preserving leading zeroes if present.
2. The first guard rejects an empty string.
3. `isdigit()` checks whether every character is a digit; `not` reverses that result.
4. The length check runs only if the earlier checks passed.
5. `else` means all three validation rules passed.

**Output:** `Error: PIN must contain only digits.`

The `elif` chain prints only the first applicable error. Check digits before length so a four-character value containing a letter receives the more useful message.

### A8. Find banned words with `enumerate`

```python
words = ["hello", "scam", "world", "spam", "friend"]
banned_words = ["scam", "spam"]

for position, word in enumerate(words, start=1):
    if word in banned_words:
        print(f"Word {position}: '{word}' is banned.")
```

**Line by line**

1. `words` contains the text being inspected.
2. `banned_words` contains the values to detect.
3. `enumerate(words, start=1)` supplies each word with a one-based position.
4. Tuple unpacking assigns the two values to `position` and `word`.
5. `word in banned_words` performs the membership test.
6. Only matching words are printed.

**Output**
```text
Word 2: 'scam' is banned.
Word 4: 'spam' is banned.
```

Without `start=1`, positions begin at zero. Non-matching words are skipped without printing blank lines.

### A9. Skip negatives and stop at zero

```python
numbers = [4, -2, 7, 0, 9, -5]

for number in numbers:
    if number < 0:
        continue
    if number == 0:
        break
    print(number)
```

**Line by line**

1. `numbers` provides values in processing order.
2. The loop takes one value at a time.
3. A negative value triggers `continue`, skipping the rest of that iteration.
4. Zero triggers `break`, ending the entire loop.
5. Only values that are neither negative nor zero reach `print`.

**Output**
```text
4
7
```

The `break` must occur before printing zero. `continue` means skip one iteration; `break` means stop the loop.

### A10. Pair names and scores with `zip`

```python
names = ["Ada", "Grace", "Alan"]
scores = [92, 88, 76]

for name, score in zip(names, scores):
    print(name, "scored", score)
```

**Line by line**

1. `names` and `scores` store corresponding values at matching indexes.
2. `zip(names, scores)` produces pairs: first name with first score, and so on.
3. The loop unpacks each pair into `name` and `score`.
4. `print` displays the pair.

**Output**
```text
Ada scored 92
Grace scored 88
Alan scored 76
```

`zip()` stops at the shortest input. The next exercise handles the mismatch case.

## Hard — A11 to A15

### A11. Classify days using `match`/`case`

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

**Line by line**

1. `days` contains recognized and unrecognized abbreviations.
2. The loop assigns each value to `day`.
3. `match day` compares the value with the patterns below.
4. `"Sat" | "Sun"` means either weekend literal matches.
5. The second case groups the five weekday literals.
6. `_` is the fallback pattern for every other value.
7. The final print displays the classification.

**Output**
```text
Mon -> Weekday
Sat -> Weekend
Xyz -> Unknown
Sun -> Weekend
```

`match` uses exact patterns here, not numeric ranges or arbitrary comparisons. Python 3.10+ is required.

### A12. Find the highest value without `max()`

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

**Line by line**

1. The outer list contains an empty list and a non-empty list.
2. The outer loop processes each list.
3. The guard detects the empty list before any index access.
4. For a non-empty list, the first item initializes `highest`.
5. The inner loop checks every number.
6. If a number is greater than the current highest, the tracking variable is updated.
7. The final print reports the result.

**Output**
```text
No numbers to check.
Highest number: 9
```

Initializing from `numbers[0]` before the empty-list guard would raise `IndexError`.

### A13. Pair products and report missing prices

```python
product_names = ["Pen", "Notebook", "Eraser", "Ruler"]
product_prices = [1.5, 2.0, 0.75]

for name, price in zip(product_names, product_prices):
    print(name, "costs", price)

print("Products without a listed price:")
for position in range(len(product_prices), len(product_names)):
    print("-", product_names[position])
```

**Line by line**

1. There are four product names but only three prices.
2. `zip()` prints the first three matched pairs and stops at the shorter list.
3. The heading introduces unmatched names.
4. `range(3, 4)` produces index 3, the first name with no price.
5. Direct indexing retrieves and prints `"Ruler"`.

**Output**
```text
Pen costs 1.5
Notebook costs 2.0
Eraser costs 0.75
Products without a listed price:
- Ruler
```

`zip()` does not raise an error when lengths differ; it silently stops. The second loop handles the leftovers.

### A14. Menu selection with a default case

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

**Line by line**

1. The list contains three valid choices and one invalid choice.
2. The loop processes every selection.
3. `match` checks the string value against each exact option.
4. Each valid case prints its corresponding action.
5. `_` catches `"9"` and includes the actual invalid value in the message.

**Output**
```text
Starting new game.
Loading saved game.
'9' is not a valid menu option.
Exiting.
```

The cases are strings (`"1"`), not integers (`1`), because the input list contains strings.

### A15. Average scores while skipping `None`

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

**Line by line**

1. Two lists are defined: one has real scores and missing values; one is entirely missing.
2. The outer loop processes both lists.
3. `total` and `count` are reset for each list.
4. The inner loop visits each score.
5. `score is None` detects a missing value; `continue` skips it.
6. Real scores are added to `total`, and `count` is increased.
7. After the loop, zero count is handled before division.
8. Otherwise, `total / count` calculates the average and `.1f` formats one decimal place.

**Output**
```text
Average of valid scores: 85.0
No valid scores were recorded.
```

Do not use `if not score` to detect missing values: a real score of zero would also be skipped. Use `is None`.

## Advanced — A16 to A20

### A16. Grade every score and count each grade

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

**Line by line**

1. `scores` stores the inputs.
2. The dictionary pre-creates every possible grade with a zero count.
3. The loop processes each score.
4. The ordered conditional chain assigns exactly one grade.
5. The dictionary value for that grade is incremented by one.
6. Each score and grade are printed.
7. After all scores, the dictionary prints the totals.

**Output**
```text
95 -> A
82 -> B
67 -> F
74 -> C
58 -> F
90 -> A
Summary: {'A': 2, 'B': 1, 'C': 1, 'F': 2}
```

Pre-populating the keys prevents `KeyError` when the first grade is counted.

### A17. Check candidate passwords and report one failure

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

**Line by line**

1. The list contains short, digit-free, valid, and empty candidates.
2. The outer loop processes one password at a time.
3. An empty password is reported immediately.
4. `continue` skips all remaining checks for that empty password.
5. `has_digit = False` initializes a flag for the current password.
6. The inner loop checks each character.
7. `isdigit()` sets the flag to `True` when a digit is found.
8. The conditional chain checks length first, then digit presence.
9. `else` accepts a password that passed both rules.

**Output**
```text
short1 -> rejected: must be at least 8 characters
longenoughbutnodigit -> rejected: must contain a digit
GoodPass1 -> accepted
 -> rejected: cannot be empty
```

`password.isdigit()` would ask whether the entire password consists only of digits, which is not the requirement. We need to know whether at least one character is a digit.

### A18. Four traffic-light transitions

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

**Line by line**

1. The initial state is red.
2. `cycles` records how many transitions remain.
3. The `while` loop repeats while the counter is positive.
4. `match` selects the transition for the current state.
5. Each case prints the transition and updates the state for the next iteration.
6. The countdown is outside `match` but inside the loop, so it decreases once regardless of the matched state.

**Output**
```text
Red -> Go to Green
Green -> Go to Yellow
Yellow -> Go to Red
Red -> Go to Green
```

If the decrement were placed in only one case, the loop might not terminate for the other states.

### A19. Search inventory with a `found` flag

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

**Line by line**

1. The first inventory and search term are set.
2. `found = False` assumes no match until one is discovered.
3. The loop compares each item with the search term.
4. On a match, the flag becomes true, a message is printed, and `break` stops further searching.
5. After the loop, `if not found` prints a not-found message only if no match occurred.
6. The second search repeats the pattern with an empty list.
7. An empty list runs zero loop iterations, leaving `found_2` false, so the not-found message prints.

**Output**
```text
'wrench' found in inventory.
'screwdriver' not found in inventory.
```

Place the final not-found check after the loop. Putting it inside the loop would print misleading messages for individual non-matches.

### A20. Numbered pass/fail report with unmatched names

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

**Line by line**

1. Four names and three scores are stored.
2. `position = 0` initializes a manual one-based counter.
3. `zip()` pairs the three available name/score combinations.
4. The counter increments once per matched pair.
5. The condition assigns `PASS` for 60 or above; otherwise it assigns `FAIL`.
6. The report prints position, name, score, and result.
7. The length comparison detects the mismatch.
8. `range(3, 4)` produces the unmatched name's index.
9. The final loop prints Marie, who has no score.

**Output**
```text
1 Ada 92 PASS
2 Grace 58 FAIL
3 Alan 74 PASS
Note: some names have no matching score and were skipped:
- Marie
```

This combines `zip()` for matched records with `range()` and indexing for leftover records.

---

# Part B — Functions, Scope, Side Effects, and Errors (B1–B20)

## Basic — B1 to B5

### B1. Return the square of a number

```python
def square(number):
    return number * number

print(square(4))
print(square(7))
```

**Line by line**

1. `def square(number):` defines a function with one parameter.
2. `return number * number` computes and sends the result back to the caller.
3. `print(square(4))` calls the function with 4 and displays 16.
4. The second call uses 7 and displays 49.

**Output:** `16` then `49`.

The function returns a value instead of printing internally, so the result can be stored or used in another calculation.

### B2. Calculate order total

```python
def calculate_total(price, quantity):
    return price * quantity

print(calculate_total(9.99, 3))
```

**Line by line**

1. The function requires `price` and `quantity`.
2. It multiplies them and returns the result.
3. The call supplies 9.99 and 3 positionally.
4. `print` displays the returned total.

**Output:** `29.97`.

Both arguments are required. Supplying only one raises `TypeError`. Swapping them may still run but changes their meaning.

### B3. Compare `print()` and `return`

```python
def show_square(number):
    print(number * number)

def get_square(number):
    return number * number

show_square(5)
result = get_square(5)
print("Stored result:", result)
```

**Line by line**

1. `show_square` calculates and prints but has no explicit return.
2. `get_square` calculates and returns the value.
3. Calling `show_square(5)` immediately displays 25.
4. `get_square(5)` returns 25, which is stored in `result`.
5. The final print displays the stored value.

**Output**
```text
25
Stored result: 25
```

A function without a return statement returns `None` implicitly. That is why storing `show_square(5)` would not store 25.

### B4. Reuse a returned order total

```python
def calculate_total(price, quantity):
    return price * quantity

order_total = calculate_total(12.5, 2)
shipping = 4
final_amount = order_total + shipping
print(f"Final amount: ${final_amount:.2f}")
```

**Line by line**

1. The function returns the product of price and quantity.
2. The call calculates 25.0 and stores it in `order_total`.
3. `shipping` stores a separate fee of 4.
4. `final_amount` adds shipping to the returned subtotal.
5. The f-string displays two decimal places.

**Output:** `Final amount: $29.00`.

Shipping is kept outside the function because the function's responsibility is only to calculate the item total.

### B5. Return a Boolean result

```python
def is_positive(number):
    return number > 0

numbers_to_check = [5, -3, 0, 12]

for number in numbers_to_check:
    print(number, "->", is_positive(number))
```

**Line by line**

1. The function returns the Boolean result of `number > 0`.
2. The list provides four test values.
3. The loop visits each value.
4. The function is called for that value and the result is printed.

**Output**
```text
5 -> True
-3 -> False
0 -> False
12 -> True
```

Zero is not positive. A comparison already returns `True` or `False`, so an extra `if`/`else` is unnecessary.

## Moderate — B6 to B10

### B6. Positional versus keyword arguments

```python
def describe_item(name, price):
    print(f"{name} costs ${price}")

describe_item("Pen", 1.5)
describe_item(1.5, "Pen")
describe_item(price=1.5, name="Pen")
```

**Line by line**

1. The function expects `name` first and `price` second.
2. The first call supplies arguments in the correct positional order.
3. The second call swaps them; Python accepts the values but assigns them to the wrong parameters.
4. The third call names both parameters, so argument order in the call does not matter.

**Output**
```text
Pen costs $1.5
1.5 costs $Pen
Pen costs $1.5
```

Python checks argument binding, not whether the meaning of a value matches the parameter name. Keyword arguments make calls clearer.

### B7. Default currency argument

```python
def format_price(amount, currency="$"):
    return f"{currency}{amount:.2f}"

print(format_price(20))
print(format_price(20, "€"))
```

**Line by line**

1. `amount` is required; `currency` defaults to the immutable string `"$"`.
2. The f-string places the currency before the amount and formats two decimal places.
3. The first call uses the default.
4. The second call overrides it with the euro symbol.

**Output**
```text
$20.00
€20.00
```

The string default is safe because it is immutable. Mutable defaults such as `[]` must be handled differently.

### B8. Keyword-only tax option

```python
def calculate_total(price, quantity, *, include_tax=False):
    subtotal = price * quantity
    if include_tax:
        return subtotal * 1.08
    return subtotal

print(calculate_total(10, 2))
print(calculate_total(10, 2, include_tax=True))
```

**Line by line**

1. `price` and `quantity` are ordinary parameters.
2. The `*` makes `include_tax` keyword-only; callers must name it.
3. `subtotal` is the product of price and quantity.
4. If tax is requested, the subtotal is multiplied by 1.08 (8% tax).
5. Otherwise the untaxed subtotal is returned.
6. The calls show the default and opted-in cases.

**Output:** `20` and `21.6`.

`calculate_total(10, 2, True)` is invalid because the third parameter must be passed by keyword.

### B9. Docstring and `help()`

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

**Line by line**

1. The function accepts width and height.
2. The triple-quoted text immediately inside the function is its docstring.
3. The docstring explains purpose, parameters, and return value.
4. The function returns width multiplied by height.
5. The call prints 20.
6. `help()` displays the function signature and stored docstring.

**Output begins with:** `20`, followed by help text describing `calculate_area(width, height)`.

A comment above the function is not a docstring and is not displayed by `help()`.

### B10. Local variable shadows a global

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

**Line by line**

1. The global `tax_rate` is set to 0.08.
2. `show_local_rate` defines a function.
3. Its assignment creates a local variable with the same name; it does not change the global.
4. The local value is printed as 0.0.
5. `calculate_with_tax` reads the global value because it does not assign a local `tax_rate`.
6. The calls show the local value, unchanged global value, and tax-inclusive calculation.

**Output**
```text
Inside function: 0.0
Outside function: 0.08
108.0
```

Rebinding a local name differs from mutating a global list or dictionary. A local assignment does not update a global variable unless `global` is used.

## Hard — B11 to B15

### B11. Impure global-dependent versus pure function

```python
discount_rate = 0.10

def apply_discount_impure(price):
    return price * (1 - discount_rate)

def apply_discount_pure(price, discount_rate):
    return price * (1 - discount_rate)

print(apply_discount_impure(100))
print(apply_discount_pure(100, 0.10))
```

**Line by line**

1. The global discount rate is 10%.
2. The first function reads that global value, which is a hidden dependency.
3. The second function receives the rate explicitly as a parameter.
4. Both calculate price after discount.
5. The calls produce the same result for the current values.

**Output:** `90.0` and `90.0`.

`apply_discount_pure` is pure: its result depends only on its arguments. The first function's result can change if unrelated code changes the global rate. Returning a value alone does not make a function pure.

### B12. Mutable default bug and safe `None` pattern

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

**Line by line**

1. The unsafe function has a list as its default argument. That list is created once when the function is defined.
2. Each call appends to and returns the same default list.
3. The safe function uses `None` as its default.
4. `items is None` detects that no list was supplied.
5. `items = []` creates a fresh list for that call.
6. The item is appended and the list returned.
7. The four calls demonstrate shared versus independent lists.

**Output**
```text
['apple']
['apple', 'banana']
['apple']
['banana']
```

Do not use `items=[]` for a mutable default when you intend a fresh list per call. `None` is a safe sentinel; create the list inside the function.

### B13. Replace a hidden shipping-fee dependency

```python
shipping_fee = 5

def calculate_total_hidden(order_total):
    return order_total + shipping_fee

def calculate_total_explicit(order_total, shipping_fee):
    return order_total + shipping_fee

print(calculate_total_hidden(50))
print(calculate_total_explicit(50, shipping_fee))
```

**Line by line**

1. The global shipping fee is 5.
2. The first function reads that global implicitly.
3. The second function declares the fee as a required parameter.
4. The first call hides the fee dependency.
5. The second call makes the dependency visible by passing the fee explicitly.

**Output:** `55` and `55`.

The explicit function is easier to understand and test because every input it needs is visible in the call. The parameter named `shipping_fee` is local to that function.

### B14. Validate price with specific exceptions

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

**Line by line**

1. The function receives one candidate price.
2. `isinstance` accepts integers and floats.
3. The Boolean exclusion is necessary because `bool` is a subtype of `int` in Python.
4. Wrong type raises `TypeError` with a clear message.
5. A numeric value at or below zero raises `ValueError`.
6. The list contains one valid number, one negative number, and one string.
7. The loop validates each independently.
8. The narrow `try` contains the validation call.
9. If it returns normally, the value is valid.
10. The `except` catches only the two expected validation exceptions.

**Output**
```text
19.99 -> valid
-5 -> rejected: Invalid price: -5. Must be greater than zero.
twenty -> rejected: Invalid price: 'twenty'. Expected a number.
```

Check type before comparing the value with zero; otherwise comparing `"twenty" <= 0` itself raises `TypeError`. Do not catch every possible exception.

### B15. Handle three specific standard exceptions

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

**Line by line**

1. `get_safe` attempts direct dictionary lookup.
2. If the key is absent, only `KeyError` is caught and a fallback message is returned.
3. `get_item_safe` attempts list indexing.
4. If the index is out of range, only `IndexError` is caught.
5. `divide_safe` performs division.
6. If the denominator is zero, only `ZeroDivisionError` is caught.
7. The three calls deliberately trigger their respective exception types.

**Output**
```text
Key not found.
Position not found.
Cannot divide by zero.
```

For a simple optional dictionary value, `.get(key, default)` is often shorter than handling `KeyError`. This exercise demonstrates specific exception handling.

## Advanced — B16 to B20

### B16. Safe shopping-cart updater

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

**Line by line**

1. `cart=None` avoids a shared mutable default list.
2. The first condition rejects a non-string or empty item name.
3. `raise ValueError` stops the invalid call with a useful message.
4. If no cart was supplied, a new empty list is created.
5. `append` adds the item to the selected cart.
6. The function returns the cart.
7. Two calls without a cart create independent lists.
8. The final call passes an empty item; the caller catches the expected `ValueError`.

**Output**
```text
Cart one: ['Apples']
Cart two: ['Bread']
Rejected: Item name must be a non-empty string.
```

This exercise's stated contract uses `ValueError` for both empty and non-string names. A different API might choose `TypeError` for the wrong type, but follow the exercise's requested exception.

### B17. Discount batch with all four exception blocks

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

**Line by line**

1. The function checks that the percentage is between 0 and 100 inclusive.
2. An out-of-range percentage raises `ValueError`.
3. A valid percentage is applied and the final price returned.
4. The request list contains two valid requests and one invalid request.
5. The loop unpacks each price and discount.
6. `try` runs the calculation.
7. `except` handles an invalid discount and prints the reason.
8. `else` runs only when the calculation succeeded.
9. `finally` runs for every request, success or failure.

**Output**
```text
Final price: $80.00
Processed one request.
Skipped: Invalid discount_percentage: 150. Expected 0-100.
Processed one request.
Final price: $72.00
Processed one request.
```

`else` is success-only; `finally` runs when control leaves the `try` statement.

### B18. Collect all registration errors

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

**Line by line**

1. The function receives a dictionary containing registration data.
2. `errors = []` creates a list to collect all validation messages.
3. The name check catches a missing key or an empty string.
4. The age-key check distinguishes a missing age from a malformed age.
5. If the key exists, `int()` attempts conversion.
6. A successfully parsed age is checked against the 0–120 range.
7. `except ValueError` adds a message when conversion fails.
8. The function returns every collected error.
9. The caller checks whether the list is non-empty and prints either rejection or acceptance.

**Output**
```text
Accepted.
Rejected: ['Name is required.', "Age must be a whole number, got 'abc'."]
```

Unlike raising on the first issue, collecting messages lets the user fix multiple fields at once. This exercise assumes `data` is a dictionary and age is a value for which `int()` raises `ValueError` on malformed input; it does not handle every possible wrong type.

### B19. Safe withdrawal and update state only on success

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

**Line by line**

1. `withdraw` receives the current balance and requested amount.
2. If the amount exceeds the balance, it raises `ValueError`.
3. Otherwise it returns the calculated new balance; it does not mutate a global.
4. The caller starts with a balance of 100.
5. The loop attempts withdrawals of 30 and 200.
6. The first call succeeds and stores 70 in `new_balance`.
7. `else` updates the real `balance` only after successful calculation.
8. The second call exceeds the now-current balance of 70 and raises an exception.
9. `except` reports the failure; it does not update the balance.
10. `finally` prints the completion message after both attempts.

**Output**
```text
New balance: 70
Transaction attempt complete.
Transaction failed: Cannot withdraw 200; balance is only 70.
Transaction attempt complete.
```

The calculation function is pure with respect to the balance: it returns a proposed new value. The caller owns the state update and performs it only on success.

### B20. Custom exception for order-status transitions

```python
class InvalidTransitionError(Exception):
    pass

def change_order_status(current_status, requested_status):
    allowed_next = {"NEW": "PAID", "PAID": "SHIPPED", "SHIPPED": "DELIVERED"}

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

**Line by line**

1. The class creates a specific exception type derived from `Exception`.
2. `pass` means the class needs no additional implementation.
3. The function receives the current and requested statuses.
4. `allowed_next` maps each state to the one permitted next state.
5. `.get(current_status)` retrieves the allowed next value, or `None` if the current state is unknown.
6. If the requested status does not match, the function raises the custom exception.
7. A valid transition returns the requested status.
8. `status` begins as `"NEW"` and the request sequence contains one invalid transition.
9. The loop tries each transition.
10. The assignment to `status` occurs only if the function returns successfully.
11. The `except` block reports invalid transitions; because assignment did not complete, the old status remains available for the next attempt.

**Output**
```text
Status is now: PAID
Rejected: Cannot go from PAID to DELIVERED.
Status is now: SHIPPED
```

The rejected transition does not change state. The next request is correctly checked from `"PAID"`, the last successfully reached state.

---

# Final review

## Key engineering habits

- Guard before indexing or dividing.
- Pass dependencies explicitly; avoid hidden globals and mutable defaults.
- Return calculated values; catch specific expected exceptions.
- Validate inputs and update state only after success.
- Make errors specific without exposing sensitive information.

**End of Module 03 practice solutions.**
