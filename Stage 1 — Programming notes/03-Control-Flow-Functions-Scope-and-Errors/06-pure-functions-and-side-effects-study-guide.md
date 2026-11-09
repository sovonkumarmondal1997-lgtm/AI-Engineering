# 06 — Pure Functions and Side Effects
## Complete Lesson Summary, Project-Tree Assessment, and Exercise Solutions

**Roadmap position:** Stage 1 → Module 03 — Control Flow, Functions, Scope, and Errors → Lesson 06  
**Source lesson:** `06-pure-functions-and-side-effects.md`

---

# Part A — Complete Lesson Summary (under 5,000 words)

## 1. Why pure functions and side effects matter

Two functions can calculate the same answer but behave very differently.

- One function may use only its inputs, return its result, and leave all outside data unchanged.
- Another may read a global variable, change a list it was given, or print its result instead of returning it.

The first is easier to predict, test, reuse, and debug. The second can become difficult to understand as a program grows.

The goal is not to remove every side effect. A useful program eventually has to display information, save data, or communicate with something outside itself. The goal is to make side effects intentional and keep them in clearly identifiable parts of the program.

## 2. Learning outcomes and prerequisites

After this lesson, you should be able to:

- Define a pure function and identify its defining properties.
- Define a side effect and name common examples.
- Compare pure and impure functions that calculate the same result.
- Explain why mutating an input list, dictionary, or set is a side effect.
- Return a new collection instead of unexpectedly changing the caller's collection.
- Explain the difference between `print()` and `return`.
- Separate calculations from presentation.
- Replace hidden global dependencies with explicit parameters.
- Apply practical rules for containing side effects.

Prerequisites are functions, parameters, return values, global scope, lists, mutation, copying, and aliasing.

## 3. Key terms

| Term | Meaning |
|---|---|
| Pure function | A function whose result depends only on its explicit inputs and which has no observable side effects. |
| Side effect | An observable interaction or change beyond producing a result, such as printing or changing a collection. |
| Impure function | A function with a side effect or a dependency on something outside its explicit arguments. |
| Mutation | Changing a mutable object in place rather than creating a new object. |
| Hidden dependency | A value a function uses that is not shown in its parameters, often a global variable. |
| Business logic | The calculations and decisions that implement what the program is meant to do. |
| Presentation | Formatting and displaying information, for example with `print()`. |

## 4. What a pure function is

A pure function has three practical properties:

1. **Same inputs, same output.** If you call it repeatedly with the same arguments, it produces the same result.
2. **No outside mutation.** It does not change global state or mutate a collection supplied by the caller.
3. **No hidden dependencies.** Its result depends only on the values supplied through its parameters, not a global variable, current time, or random value.

A pure calculation normally uses `return` to make its result available to the caller. Returning a value alone does not make a function pure: it could return a value and still print, mutate a list, or read global state.

### Example: pure discount calculation

```python
def calculate_discounted_price(price, discount_rate):
    return price * (1 - discount_rate)

print(calculate_discounted_price(100, 0.20))
print(calculate_discounted_price(100, 0.20))
print(calculate_discounted_price(50, 0.10))
```

Output:

```text
80.0
80.0
45.0
```

Step by step:

- The function receives `price` and `discount_rate`.
- It calculates the price after discount.
- It returns the result.
- It does not read or change anything outside itself.
- The same arguments `(100, 0.20)` produce `80.0` both times.

This predictability makes the function easy to test: provide known inputs and compare the returned result with the expected result.

## 5. What a side effect is

A side effect is an observable interaction or change beyond simply producing a return value. Common examples are:

- **Printing:** `print()` sends text to the screen.
- **Mutating a supplied collection:** appending to a list or changing a dictionary affects the object the caller still refers to.
- **Changing global state:** assigning to a global variable changes shared program state.
- **External changes:** writing to a file or sending data elsewhere. This lesson introduces these conceptually; file and input/output handling are taught later.

An external read is slightly different. Reading the current time, a random value, an environment variable, a database, or a global variable does not itself change that state. However, it is an external dependency. The result is no longer determined solely by the function's explicit arguments, so the function is not pure.

### Example: printing inside a function

```python
def report_discounted_price(price, discount_rate):
    discounted = price * (1 - discount_rate)
    print(f"Discounted price: ${discounted:.2f}")

report_discounted_price(100, 0.20)
```

Output:

```text
Discounted price: $80.00
```

The function prints, which is a side effect. It has no explicit `return`, so Python returns `None`. The caller cannot take the computed numeric result and use it in another calculation.

**Side effects are not automatically bad.** Printing a report or saving a result may be the whole purpose of a program. The engineering goal is to make these effects intentional and isolated, instead of mixing them into every calculation.

## 6. Pure versus impure functions

The following functions both calculate a price including tax:

```python
tax_rate = 0.08

def add_tax_impure(price):
    return price * (1 + tax_rate)

def add_tax_pure(price, tax_rate):
    return price * (1 + tax_rate)

print(add_tax_impure(100))
print(add_tax_pure(100, 0.08))
```

Output:

```text
108.0
108.0
```

The results are equal, but the functions are different:

- `add_tax_impure(price)` silently reads the global `tax_rate`. Its dependency is hidden.
- `add_tax_pure(price, tax_rate)` receives both required values explicitly.

Now change the global:

```python
tax_rate = 0.08

def add_tax_impure(price):
    return price * (1 + tax_rate)

def add_tax_pure(price, tax_rate):
    return price * (1 + tax_rate)

print(f"{add_tax_impure(100):.2f}")

tax_rate = 0.15

print(f"{add_tax_impure(100):.2f}")
print(f"{add_tax_pure(100, 0.08):.2f}")
```

Output:

```text
108.00
115.00
108.00
```

The same-looking impure call changes its result because another part of the program changed the global. The pure call continues to use the explicitly supplied `0.08`.

This is why pure functions are easier to predict and test: you can understand a call from its arguments without inspecting unrelated code.

## 7. Mutation as a side effect

A function mutates a caller's data when it changes a list, dictionary, or set passed into it. The caller can see that change after the function returns.

```python
def add_to_receipt(receipt, item):
    receipt.append(item)

receipt_items = ["apples"]
add_to_receipt(receipt_items, "bread")
print(receipt_items)
```

Output:

```text
['apples', 'bread']
```

`receipt` and `receipt_items` refer to the same list object. This is aliasing. Calling `.append()` changes that shared object, even though the function does not return anything.

This may be intentional, but the caller should know that the function changes its input.

### Safer alternative: build a new collection

```python
def add_to_receipt_safe(receipt, item):
    updated_receipt = receipt.copy()
    updated_receipt.append(item)
    return updated_receipt

receipt_items = ["apples"]
new_receipt = add_to_receipt_safe(receipt_items, "bread")

print("Original:", receipt_items)
print("New:", new_receipt)
```

Output:

```text
Original: ['apples']
New: ['apples', 'bread']
```

`.copy()` creates a new outer list. For these flat-list examples, the new list is independent. A shallow copy does not recursively copy nested lists or dictionaries inside the list; nested mutable objects may still be shared.

## 8. Printing versus returning

`print()` displays a value. `return` gives a value back to the caller so that the caller can store it, calculate with it, pass it to another function, or print it later.

```python
def calculate_total_prints(price, quantity):
    print(price * quantity)

def calculate_total_returns(price, quantity):
    return price * quantity

calculate_total_prints(9.99, 3)

order_total = calculate_total_returns(9.99, 3)
shipping = 5
final_amount = order_total + shipping
print(f"Final amount: ${final_amount:.2f}")
```

Output:

```text
29.97
Final amount: $34.97
```

The first function displays `29.97` and returns `None`. It cannot provide its computed number to the caller. The second function returns `29.97`, which is stored in `order_total`; the program can add shipping and display the final amount.

Returning gives the caller control over how to use the result. Printing inside the calculation function removes that flexibility.

## 9. Separate calculation from presentation

Keep business logic (the calculation) separate from presentation (displaying the result).

```python
def calculate_order_total(prices):
    total = 0
    for price in prices:
        total = total + price
    return total

order_prices = [12.50, 7.25, 4.00]
order_total = calculate_order_total(order_prices)

print(f"Order total: ${order_total:.2f}")
```

Output:

```text
Order total: $23.75
```

Step by step:

1. The function starts `total` at zero.
2. It loops through each price.
3. It adds each price to the running total.
4. It returns the total without printing.
5. The caller stores the returned value.
6. The separate `print()` statement decides how to display it.

If the display format changes, the calculation function does not need to change. The result can also be stored or used in another calculation.

## 10. Hidden dependencies

A hidden dependency is a value used by a function but missing from its parameter list.

```python
shipping_fee = 5

def calculate_final_amount(order_total):
    return order_total + shipping_fee

print(calculate_final_amount(50))
```

Output:

```text
55
```

The call shows `order_total`, but the function also depends on global `shipping_fee`. That dependency is not visible in the signature.

Make it explicit:

```python
def calculate_final_amount(order_total, shipping_fee):
    return order_total + shipping_fee

shipping_fee = 5
print(calculate_final_amount(50, shipping_fee))
```

Output:

```text
55
```

The result is the same, but the function now states all its inputs. A reader can understand and test it without knowing which global variables happen to exist.

## 11. Practical design rules

- Prefer pure functions for calculations, validation, and transformations such as totals, discounts, grades, and cleaned data.
- Keep side effects near the edges of the program. Printing, reading input, and saving data should generally be in a thin layer that calls calculation functions.
- Use descriptive names for functions that intentionally mutate data. A name such as `add_item_to_cart` signals a change.
- Check whether input data changed when you expected a function to be pure.
- Document unavoidable side effects in the function name, a comment, or a docstring.

The intent is to make each function's behavior clear to its caller.

## 12. All six worked examples

### Example 1 — Discount calculation: pure versus impure

```python
discount_rate = 0.20

def calculate_discount_impure(price):
    print(f"Discounted: ${price * (1 - discount_rate):.2f}")

def calculate_discount_pure(price, discount_rate):
    return price * (1 - discount_rate)

calculate_discount_impure(100)

result = calculate_discount_pure(100, 0.20)
print(f"Discounted: ${result:.2f}")
```

Output:

```text
Discounted: $80.00
Discounted: $80.00
```

The impure function has two issues: it reads the global `discount_rate` and prints internally. Its signature reveals neither dependency nor display effect. The pure function takes the rate explicitly and returns the number. Printing happens outside it.

### Example 2 — Convert scores to grades

```python
def convert_score_to_grade(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    else:
        return "F"

student_scores = [95, 82, 68, 74]

for score in student_scores:
    grade = convert_score_to_grade(score)
    print(f"{score} -> {grade}")
```

Output:

```text
95 -> A
82 -> B
68 -> F
74 -> C
```

The function makes a decision using only `score`, returns a grade, and changes nothing. The loop performs the printing separately. The same score always maps to the same grade.

### Example 3 — Add tax and print a spending report separately

```python
def add_tax(price, tax_rate):
    return price * (1 + tax_rate)

def calculate_order_total(prices, tax_rate):
    total_before_tax = 0
    for price in prices:
        total_before_tax = total_before_tax + price
    return add_tax(total_before_tax, tax_rate)

order_prices = [12.50, 7.25, 4.00]
order_total = calculate_order_total(order_prices, 0.08)

print("Spending report")
print("-" * 20)
print(f"Items purchased: {len(order_prices)}")
print(f"Total with tax: ${order_total:.2f}")
```

Output:

```text
Spending report
--------------------
Items purchased: 3
Total with tax: $25.65
```

`add_tax` receives price and rate, then returns a number. `calculate_order_total` sums the prices and calls `add_tax`. Both functions are pure. The report formatting and printing are separate, so the display can change without rewriting the calculations.

### Example 4 — Clean names without changing the original list

```python
def clean_names_unsafe(names):
    for position in range(len(names)):
        names[position] = names[position].strip().title()
    return names

def clean_names_safe(names):
    cleaned_names = []
    for name in names:
        cleaned_names.append(name.strip().title())
    return cleaned_names

signup_names = ["  ada", "GRACE  ", "alan"]
unsafe_result = clean_names_unsafe(signup_names)
print("After unsafe cleaning, original list:", signup_names)

signup_names_again = ["  ada", "GRACE  ", "alan"]
safe_result = clean_names_safe(signup_names_again)
print("After safe cleaning, original list:", signup_names_again)
print("Safe cleaned result:", safe_result)
```

Output:

```text
After unsafe cleaning, original list: ['Ada', 'Grace', 'Alan']
After safe cleaning, original list: ['  ada', 'GRACE  ', 'alan']
Safe cleaned result: ['Ada', 'Grace', 'Alan']
```

`clean_names_unsafe` uses index assignment to overwrite values in the supplied list. The caller's list changes. `clean_names_safe` creates a new list, appends cleaned strings to it, and leaves the input untouched. It is pure because it only reads the input and creates/returns a new result.

### Example 5 — Shopping cart: hidden mutation versus safe copy

```python
def add_item_to_cart_hidden(cart, item):
    cart.append(item)

def add_item_to_cart(cart, item):
    updated_cart = cart.copy()
    updated_cart.append(item)
    return updated_cart

saved_cart = ["apples"]
add_item_to_cart_hidden(saved_cart, "bread")
print("Cart after hidden mutation:", saved_cart)

original_cart = ["apples"]
new_cart = add_item_to_cart(original_cart, "bread")
print("Original cart untouched:", original_cart)
print("New cart:", new_cart)
```

Output:

```text
Cart after hidden mutation: ['apples', 'bread']
Original cart untouched: ['apples']
New cart: ['apples', 'bread']
```

The first function mutates the caller's list. The second copies the list, changes the copy, and returns it. The original remains unchanged. This is a shallow copy, which is sufficient for this flat list of strings.

### Example 6 — Receipt built from pure calculations

```python
def calculate_order_total(prices):
    total = 0
    for price in prices:
        total = total + price
    return total

def add_tax(amount, tax_rate):
    return amount * (1 + tax_rate)

def add_shipping(amount, shipping_fee):
    return amount + shipping_fee

order_prices = [19.99, 5.50, 42.00]
tax_rate = 0.08
shipping_fee = 6.00

subtotal = calculate_order_total(order_prices)
total_with_tax = add_tax(subtotal, tax_rate)
final_amount = add_shipping(total_with_tax, shipping_fee)

print("Final Receipt")
print("-" * 20)
print(f"Subtotal: ${subtotal:.2f}")
print(f"With tax: ${total_with_tax:.2f}")
print(f"Final amount: ${final_amount:.2f}")
```

Output:

```text
Final Receipt
--------------------
Subtotal: $67.49
With tax: $72.89
Final amount: $78.89
```

The subtotal is `19.99 + 5.50 + 42.00 = 67.49`. Tax gives `67.49 * 1.08 = 72.8892`, displayed as `$72.89`. Shipping adds `$6.00`, producing `78.8892`, displayed as `$78.89`.

All three calculation functions receive explicit inputs and return numbers. Each result becomes the next function's input. Printing occurs only after the calculations finish.

## 13. Common beginner mistakes

- Thinking every side effect is bad. Side effects are necessary; the problem is making them unexpected or scattering them through calculation code.
- Mutating an input and also returning a result without making the intended behavior clear.
- Assuming a `return` statement automatically makes a function pure. It may still print, mutate data, or read global state.
- Forgetting that all aliases of a list see its in-place mutations.
- Reading a global variable in a calculation function instead of passing it as a parameter.
- Mixing calculations and printing, which makes calculation reuse and presentation changes harder.

## 14. Connection to Applied AI and Agentic AI engineering

AI systems calculate scores, validate tool arguments, rank retrieved documents, and decide what action to take. Keeping this decision logic pure makes it easier to test and debug. External tool calls, logging, and updates to conversation state are side effects and are often necessary. Keep them intentional and separate from the logic that decides what should happen.

---

# Part B — Project-Tree Review and Current Learning Level

## 1. Roadmap position

Your roadmap is **Stage 1 — Programming & Computational Thinking**. The previously reviewed Stage 1 tree contains 25 folders when the overview is included, 38 folders, and 311 files. It progresses from computational thinking and Python foundations toward production-oriented Python.

Relevant module sequence:

| Module | Main focus |
|---|---|
| 00 | Stage overview, learning plan, and capstone projects |
| 01 | Computational Thinking and Program Design |
| 02 | Python Core Language and Data Types |
| 03 | Control Flow, Functions, Scope, and Errors |
| 04 | Problem-Solving, Collections, and Algorithmic Habits |
| 05 | Text Files, Structured Data, and CLI Programs |
| 06 | Modules, Packages, Dependencies, and Code Quality |
| 07 | Testing and Systematic Debugging |
| 08 onward | Object-oriented design and further production-oriented and advanced Python topics |

Module 03's relevant sequence:

1. Conditionals, guards, and Boolean logic.
2. `for`/`while` loops and loop control.
3. Functions, parameters, and return values.
4. Function arguments, defaults, and docstrings.
5. Scope, lifetime, and global state.
6. **Pure functions and side effects — this lesson.**
7. Exceptions, validation, and useful errors.

This lesson builds directly on the previous scope/global-state lesson and on the earlier list mutation, copying, and aliasing material.

## 2. Current learning-level assessment

Your previous work demonstrates exposure to:

- Python variables, data types, strings, lists, tuples, dictionaries, and sets.
- Mutability, immutability, copying, and aliasing.
- Conditions, loops, and loop control.
- Functions, parameters, return values, defaults, and docstrings.
- Collections and problem-solving topics such as filtering, grouping, sorting, Big-O, comprehensions, recursion, and parsing.

Your current assessed level is **beginner progressing toward intermediate**. This is a learning-progress assessment, not a claim that every topic is already mastered.

## 3. Scope for the exercise solutions

All five exercises can be solved using concepts already taught:

- Functions, parameters, and return values.
- Conditions and loops.
- Lists and dictionaries.
- String formatting and string methods.
- List mutation, `.copy()`, and aliasing.
- Pure versus impure behavior and side effects.

No classes, external libraries, file handling, or advanced architecture are required.

---

# Part C — All Five Exercises Solved Step by Step (under 3,500 words)

## Exercise 1 — Pure and impure area calculations

**Requirement:** Write a pure `calculate_area(width, height)` and an impure version that reads global `width` and `height`. Change the globals between calls and observe the difference.

### Solution

```python
def calculate_area(width, height):
    return width * height

width = 5
height = 4

def calculate_area_impure():
    return width * height

print("Pure result:", calculate_area(5, 4))
print("Impure result:", calculate_area_impure())

width = 10
height = 3

print("Pure result with same inputs:", calculate_area(5, 4))
print("Impure result after global change:", calculate_area_impure())
```

### Line-by-line explanation

1. `def calculate_area(width, height):` defines a function with explicit dimensions.
2. `return width * height` calculates and returns the area.
3. `width = 5` and `height = 4` create global values for the impure example.
4. `def calculate_area_impure():` defines a function with no parameters.
5. `return width * height` reads the global variables rather than receiving inputs.
6. The first pure call passes `5` and `4`, returning `20`.
7. The first impure call reads the globals `5` and `4`, also returning `20`.
8. The assignments change the global dimensions to `10` and `3`.
9. The pure call still receives `5` and `4`, so it returns `20`.
10. The impure call now reads `10` and `3`, so it returns `30`.

Output:

```text
Pure result: 20
Impure result: 20
Pure result with same inputs: 20
Impure result after global change: 30
```

**Conclusion:** The pure function's result is controlled by its arguments. The impure function's result silently changes when global state changes.

---

## Exercise 2 — Remove duplicates: mutate in place versus return a new list

**Requirement:** Both functions must remove duplicates, preserve the original order, and keep the first occurrence. The unsafe function changes the supplied list. The safe function returns a new list and leaves the original untouched.

### Version A — In-place mutation

```python
def remove_duplicates_unsafe(numbers):
    unique_numbers = []

    for number in numbers:
        if number not in unique_numbers:
            unique_numbers.append(number)

    numbers[:] = unique_numbers
    return numbers

values = [4, 2, 4, 7, 2, 9]
result = remove_duplicates_unsafe(values)

print("Returned result:", result)
print("Original list after unsafe call:", values)
```

Output:

```text
Returned result: [4, 2, 7, 9]
Original list after unsafe call: [4, 2, 7, 9]
```

Line by line:

1. `def remove_duplicates_unsafe(numbers):` receives the caller's list.
2. `unique_numbers = []` creates a temporary list for first occurrences.
3. `for number in numbers:` examines each value in original order.
4. `if number not in unique_numbers:` checks whether this is the first occurrence.
5. `unique_numbers.append(number)` adds only values not already collected.
6. `numbers[:] = unique_numbers` replaces the contents of the original list in place. Slice assignment preserves the identity of the original list object.
7. `return numbers` returns that same, now-mutated list.
8. The caller prints the returned result and original list; both show the changed contents.

### Version B — Pure version returning a new list

```python
def remove_duplicates_safe(numbers):
    unique_numbers = []

    for number in numbers:
        if number not in unique_numbers:
            unique_numbers.append(number)

    return unique_numbers

values = [4, 2, 4, 7, 2, 9]
result = remove_duplicates_safe(values)

print("Returned result:", result)
print("Original list after safe call:", values)
```

Output:

```text
Returned result: [4, 2, 7, 9]
Original list after safe call: [4, 2, 4, 7, 2, 9]
```

Line by line:

1. The function receives `numbers`.
2. It creates a separate empty `unique_numbers` list.
3. It loops over the original list.
4. It appends only the first occurrence of each value.
5. It returns the new list.
6. It never assigns to or mutates `numbers`, so the caller's original list stays unchanged.

**Comparison:** Both produce the same deduplicated values and preserve order. The unsafe version changes the caller's object; the safe version creates and returns a separate result.

---

## Exercise 3 — Return formatted text instead of printing it

**Requirement:** Rewrite a function that prints a formatted price so it returns the formatted string. Use that returned string in two different ways.

### Solution

```python
def format_price(price):
    return f"${price:.2f}"

formatted_price = format_price(19.5)

print(formatted_price)
print("Your order total is " + formatted_price)
```

Output:

```text
$19.50
Your order total is $19.50
```

Line by line:

1. `def format_price(price):` defines a function that receives a price.
2. `return f"${price:.2f}"` creates and returns a formatted string with a dollar sign and two decimal places. It does not print.
3. `formatted_price = format_price(19.5)` calls the function and stores the returned string `"$19.50"`.
4. `print(formatted_price)` uses the returned string directly.
5. `print("Your order total is " + formatted_price)` uses the same returned string as part of a longer message.

**Key distinction:** The function formats and returns text. The caller decides how to display or combine it.

---

## Exercise 4 — Pure score validation and separate reporting

**Requirement:** Write a pure `is_valid_score(score)` that returns `True` or `False`. Choose a validity rule. Keep all printing outside the function and report several scores in a loop.

**Rule chosen:** A valid score is between `0` and `100`, inclusive.

### Solution

```python
def is_valid_score(score):
    return 0 <= score <= 100

scores = [95, 82, -5, 100, 120]

for score in scores:
    valid = is_valid_score(score)
    print(f"{score}: {valid}")
```

Output:

```text
95: True
82: True
-5: False
100: True
120: False
```

Line by line:

1. `def is_valid_score(score):` defines a function with one input.
2. `return 0 <= score <= 100` checks whether the score is at least zero and at most 100. Python returns `True` or `False`.
3. `scores = [...]` creates test values, including values below and above the allowed range.
4. `for score in scores:` processes each score.
5. `valid = is_valid_score(score)` calls the pure function and stores its Boolean result.
6. `print(...)` reports the score and result outside the function.

The function does not print, mutate data, or read global state. The loop owns presentation.

---

## Exercise 5 — Mutating and pure dictionary updates

**Requirement:** Write a clearly named function that mutates a flat dictionary, then a pure version that uses `.copy()` and returns a new dictionary. Confirm the original dictionary remains unchanged after the pure call.

**Chosen operation:** Apply a discount by adding an `discounted_price` entry to a product dictionary. The dictionary is flat: its values are strings or numbers, not nested mutable collections.

### Version A — Intentional mutation

```python
def apply_discount_to_profile_mutating(profile, discount_rate):
    profile["discounted_price"] = profile["price"] * (1 - discount_rate)
    return profile

product = {"name": "Keyboard", "price": 1000}
updated_product = apply_discount_to_profile_mutating(product, 0.10)

print("Mutated original:", product)
print("Returned dictionary:", updated_product)
```

Output:

```text
Mutated original: {'name': 'Keyboard', 'price': 1000, 'discounted_price': 900.0}
Returned dictionary: {'name': 'Keyboard', 'price': 1000, 'discounted_price': 900.0}
```

Line by line:

1. The function receives a dictionary and discount rate.
2. `profile["price"]` reads the original price.
3. `1 - discount_rate` calculates the fraction remaining after the discount.
4. The assignment to `profile["discounted_price"]` adds a new key to the supplied dictionary. This mutates the caller's object.
5. `return profile` returns the same dictionary object.
6. The caller prints the original and returned references; both show the added key because they refer to the same dictionary.

### Version B — Pure update using `.copy()`

```python
def apply_discount_to_profile(profile, discount_rate):
    updated_profile = profile.copy()
    updated_profile["discounted_price"] = updated_profile["price"] * (1 - discount_rate)
    return updated_profile

product = {"name": "Keyboard", "price": 1000}
updated_product = apply_discount_to_profile(product, 0.10)

print("Original dictionary:", product)
print("New dictionary:", updated_product)
```

Output:

```text
Original dictionary: {'name': 'Keyboard', 'price': 1000}
New dictionary: {'name': 'Keyboard', 'price': 1000, 'discounted_price': 900.0}
```

Line by line:

1. The function receives the original dictionary and discount rate.
2. `profile.copy()` creates a new, separate outer dictionary.
3. The new dictionary receives the `discounted_price` key.
4. The function returns the new dictionary.
5. The caller stores it in `updated_product`.
6. Printing `product` shows that the original is unchanged.
7. Printing `updated_product` shows the new key and calculated price.

**Important:** `.copy()` is a shallow copy. It is suitable here because the exercise uses a flat dictionary. If nested lists or dictionaries were present, those nested objects could still be shared.

---

# Part D — Revision Sheet and Self-Check

## 1. Essential rules

| Concept | Remember |
|---|---|
| Pure function | Same explicit inputs produce the same result; no observable side effects or hidden dependencies. |
| Side effect | An observable action or change beyond returning a result. |
| Global dependency | A function reads a value not shown in its parameters. |
| Mutation | Changes the same list or dictionary object the caller supplied. |
| `.copy()` | Creates a shallow copy of a list or dictionary. |
| `print()` | Displays information; does not provide the displayed value as a return result. |
| `return` | Gives a result back to the caller for reuse. |
| Business logic | Performs calculations and decisions. |
| Presentation | Formats and displays results. |
| Good design | Keep calculations pure where practical; make necessary side effects explicit and contained. |

## 2. Five questions to test yourself

1. What are the defining properties of a pure function?
2. Why is printing inside a calculation function a side effect?
3. Why does mutating a list parameter change the caller's list?
4. Why is passing `tax_rate` as a parameter safer than reading a global `tax_rate`?
5. Why does returning a new list or dictionary make it easier for the caller to preserve the original data?

## 3. Completion checklist

- [ ] I can define a pure function.
- [ ] I can identify printing, mutation, and global-state changes as side effects.
- [ ] I understand that a side effect is not automatically wrong.
- [ ] I can explain why a hidden global dependency makes a function harder to predict.
- [ ] I can distinguish `print()` from `return`.
- [ ] I can separate calculation from presentation.
- [ ] I can explain aliasing and mutation of a supplied collection.
- [ ] I can create and return a new list or dictionary.
- [ ] I understand that `.copy()` is shallow.
- [ ] I have completed all five exercises.

## 4. Final engineering takeaway

Use functions that make their dependencies explicit and return the values they calculate:

```python
def calculate_final_price(price, discount_rate, shipping_fee):
    discounted_price = price * (1 - discount_rate)
    return discounted_price + shipping_fee

final_price = calculate_final_price(100, 0.10, 5)
print(f"Final price: ${final_price:.2f}")
```

The function receives every input it needs and returns a result without printing or changing outside state. The caller decides how to present that result. This is the central habit of this lesson.

**Lesson status:** The guide covers the lesson's concepts, all six worked examples, common mistakes, and all five exercises. To check mastery, predict the outputs and reproduce the exercises without looking at the solutions.
