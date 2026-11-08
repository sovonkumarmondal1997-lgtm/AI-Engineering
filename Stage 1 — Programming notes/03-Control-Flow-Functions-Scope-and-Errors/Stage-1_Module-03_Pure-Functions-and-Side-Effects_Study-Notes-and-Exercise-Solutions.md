# Pure Functions and Side Effects — Study Notes and Exercise Solutions

## Part 1 — Lesson summary and step-by-step teaching

### 1. Pure functions

A **pure function** is a function whose result depends only on the values passed through its parameters. It has no observable side effects and does not secretly rely on changing outside data.

A pure function has three practical properties:

1. Same arguments → same result every time.
2. It does not change data outside itself, such as a caller's list or a global variable.
3. It does not rely on hidden state; its required inputs are explicit parameters.

```python
def calculate_discounted_price(price, discount_rate):
    return price * (1 - discount_rate)

print(calculate_discounted_price(100, 0.20))  # 80.0
print(calculate_discounted_price(100, 0.20))  # 80.0
print(calculate_discounted_price(50, 0.10))   # 45.0
```

The function receives two values, calculates the discounted price, and returns it. It does not print or change outside data. `return` makes the answer available to the caller; returning alone does not guarantee purity.

### 2. Side effects

A **side effect** is an observable action beyond calculating and returning a result. Examples include:

- `print()` displays text.
- Mutating a list, dictionary, or set changes an object the caller can still access.
- Assigning to a global variable changes shared program state.
- Writing a file or sending data outside the program changes something beyond the function.

Reading outside data (such as a global variable, current time, random value, environment variable, or database value) is an **external dependency**. It is not necessarily a state-changing side effect, but it can make the result depend on something beyond the function's arguments.

```python
def report_discounted_price(price, discount_rate):
    discounted = price * (1 - discount_rate)
    print(f"Discounted price: ${discounted:.2f}")

report_discounted_price(100, 0.20)
# Discounted price: $80.00
```

This function prints, so it has a side effect. Because it has no `return`, its returned value is `None`. The caller cannot store and reuse the calculated number. Side effects are not automatically bad: programs need to display and save results. The goal is to make them intentional and keep them in clearly identified places.

### 3. Pure versus impure: hidden global dependency

```python
tax_rate = 0.08

def add_tax_impure(price):
    return price * (1 + tax_rate)

def add_tax_pure(price, tax_rate):
    return price * (1 + tax_rate)

print(add_tax_impure(100))       # 108.0
print(add_tax_pure(100, 0.08))   # 108.0
```

Both calculate tax, but the first reads a global `tax_rate` that is not visible in its call. The second receives the rate explicitly.

```python
tax_rate = 0.08
def add_tax_impure(price):
    return price * (1 + tax_rate)
def add_tax_pure(price, tax_rate):
    return price * (1 + tax_rate)

print(f"{add_tax_impure(100):.2f}")  # 108.00
tax_rate = 0.15
print(f"{add_tax_impure(100):.2f}")  # 115.00
print(f"{add_tax_pure(100, 0.08):.2f}")  # 108.00
```

The impure function changes its answer because code elsewhere changed the global. The pure call stays predictable because its inputs are visible. That makes pure functions easier to test and understand independently.

### 4. Mutation is a side effect

A function can change a list passed to it because the parameter and caller's variable refer to the same list (aliasing).

```python
def add_to_receipt(receipt, item):
    receipt.append(item)

receipt_items = ["apples"]
add_to_receipt(receipt_items, "bread")
print(receipt_items)  # ['apples', 'bread']
```

The function changed the caller's list in place. This may be intentional, but it is a side effect. A safer approach is to create and return a new list. `.copy()` makes a new outer list; it is sufficient for flat lists, but nested mutable objects can still be shared.

### 5. Printing versus returning

```python
def calculate_total_prints(price, quantity):
    print(price * quantity)

def calculate_total_returns(price, quantity):
    return price * quantity

calculate_total_prints(9.99, 3)  # displays 29.97
order_total = calculate_total_returns(9.99, 3)
shipping = 5
final_amount = order_total + shipping
print(f"Final amount: ${final_amount:.2f}")  # $34.97
```

The first function displays the number but returns `None`; the second gives the number back, so the caller can store it, add shipping, pass it elsewhere, or print it. Prefer `return` for calculations and let the caller decide how to display the result.

### 6. Separate business logic from presentation

**Business logic** performs calculations and decisions. **Presentation** formats or displays the result.

```python
def calculate_order_total(prices):
    total = 0
    for price in prices:
        total = total + price
    return total

order_prices = [12.50, 7.25, 4.00]
order_total = calculate_order_total(order_prices)
print(f"Order total: ${order_total:.2f}")  # $23.75
```

The function calculates and returns a total without printing. The separate `print()` displays it. The same calculation can later be reused with a different display format.

### 7. Make hidden dependencies explicit

```python
shipping_fee = 5
def calculate_final_amount(order_total):
    return order_total + shipping_fee

print(calculate_final_amount(50))  # 55
```

The call hides its dependency on `shipping_fee`. Refactor it:

```python
def calculate_final_amount(order_total, shipping_fee):
    return order_total + shipping_fee

shipping_fee = 5
print(calculate_final_amount(50, shipping_fee))  # 55
```

Now the function signature shows everything required to calculate the answer.

### 8. Practical design rules

- Prefer pure functions for calculations, validation, and transformations.
- Keep printing, input, and saving near the edges of the program, outside calculation functions.
- Give intentionally mutating functions descriptive names, such as `add_item_to_cart`.
- Check that input collections remain unchanged when a function is expected to be pure.
- Document unavoidable side effects in the function name, comment, or docstring.

### 9. All six lesson examples

**Example 1 — Discount:** `calculate_discount_impure(price)` reads global `discount_rate` and prints; it has both a hidden dependency and a printing side effect. `calculate_discount_pure(price, discount_rate)` returns the calculation and is pure. Both display `$80.00` for the sample input, but only the pure result can be reused directly.

**Example 2 — Grades:** `convert_score_to_grade(score)` uses `if`/`elif` to return `"A"` for 90+, `"B"` for 80+, `"C"` for 70+, otherwise `"F"`. A loop processes `[95, 82, 68, 74]` and prints `95 -> A`, `82 -> B`, `68 -> F`, `74 -> C`. The function calculates; the loop presents.

**Example 3 — Tax report:** `add_tax(price, tax_rate)` returns the taxed price. `calculate_order_total(prices, tax_rate)` loops through prices, totals them, then calls `add_tax`. For `[12.50, 7.25, 4.00]` and `0.08`, the report prints 3 items and `$25.65`. Both functions are pure; report formatting is separate.

**Example 4 — Clean names:** `clean_names_unsafe(names)` uses `range(len(names))` and index assignment to replace each item with `strip().title()`, changing the original list. `clean_names_safe(names)` loops through the names, appends cleaned values to a new list, and returns it. For `["  ada", "GRACE  ", "alan"]`, the unsafe original becomes `['Ada', 'Grace', 'Alan']`; the safe original stays unchanged and the returned list is `['Ada', 'Grace', 'Alan']`.

**Example 5 — Shopping cart:** `add_item_to_cart_hidden(cart, item)` appends directly to the supplied list, so `saved_cart` becomes `['apples', 'bread']`. The safer `add_item_to_cart(cart, item)` first makes `updated_cart = cart.copy()`, appends to the copy, and returns it. `original_cart` remains `['apples']`; `new_cart` is `['apples', 'bread']`.

**Example 6 — Receipt capstone:** `calculate_order_total(prices)` returns the subtotal; `add_tax(amount, tax_rate)` returns the taxed amount; `add_shipping(amount, shipping_fee)` returns the final amount. For `[19.99, 5.50, 42.00]`, tax `0.08`, and shipping `6.00`, the functions are chained: subtotal `$67.49`, with tax `$72.89`, final `$78.89`. Only the final receipt section prints.

### 10. Common mistakes to avoid

- Treating every side effect as wrong; the issue is unintended or scattered effects.
- Mutating an input and also returning a value without making the function's behavior clear.
- Assuming `return` automatically means pure; a function can return and still print, mutate, or read a global.
- Forgetting that aliases see the same mutated list.
- Using globals instead of explicit parameters for calculation inputs.
- Mixing calculation and printing, making calculations harder to reuse.

---

## Part 2 — Learning-level assessment and all exercise solutions

### Current learning level and scope

Based on the Stage 1 roadmap and topics previously covered, you have studied computational thinking, conditionals, loops, collections, functions, parameters, return values, defaults/docstrings, and scope/global state. The prerequisite list in this lesson also assumes list mutation, copying, and aliasing. The full current project tree was not attached in this turn, so this is a progress-based assessment, not a fresh audit of every project file.

The five exercises can be solved with the concepts above: function definitions, parameters, `return`, `if`/`else`, `for`, lists, dictionaries, `.append()`, `.copy()`, and basic string formatting. No advanced concepts are required.

### Exercise 1 — Pure and impure area calculations

```python
width = 5
height = 4

def area_impure():
    return width * height

def calculate_area(width, height):
    return width * height

print(area_impure())          # 20
width = 10
print(area_impure())          # 40
print(calculate_area(5, 4))   # 20
```

Line by line:
1. `width` and `height` are global values.
2. `area_impure()` reads those globals without receiving parameters.
3. `calculate_area()` receives both required values explicitly.
4. The first impure call multiplies 5 × 4.
5. Changing global `width` to 10 changes the next impure result to 40.
6. The pure call still returns 20 because its arguments are 5 and 4.

### Exercise 2 — Remove duplicates, unsafe and safe

```python
def remove_duplicates_unsafe(numbers):
    unique_numbers = []
    for number in numbers:
        if number not in unique_numbers:
            unique_numbers.append(number)
    numbers[:] = unique_numbers
    return numbers

def remove_duplicates_safe(numbers):
    unique_numbers = []
    for number in numbers:
        if number not in unique_numbers:
            unique_numbers.append(number)
    return unique_numbers

values_unsafe = [3, 1, 3, 2, 1]
result_unsafe = remove_duplicates_unsafe(values_unsafe)
print("Unsafe original:", values_unsafe)

values_safe = [3, 1, 3, 2, 1]
result_safe = remove_duplicates_safe(values_safe)
print("Safe original:", values_safe)
print("Safe result:", result_safe)
```

Line by line:
1. Each function starts an empty list to hold first occurrences.
2. The `for` loop visits each number in its original order.
3. `if number not in unique_numbers` checks whether it has appeared already.
4. `.append(number)` keeps only its first occurrence.
5. In the unsafe version, `numbers[:] = unique_numbers` replaces the contents of the original list in place. The caller sees the change.
6. In the safe version, the new list is returned and the input is untouched.

Expected: unsafe original `[3, 1, 2]`; safe original `[3, 1, 3, 2, 1]`; safe result `[3, 1, 2]`. The slice assignment uses basic list mutation to preserve the original list object while replacing its contents.

### Exercise 3 — Return formatted price instead of printing

```python
def format_price(price):
    return f"Price: ${price:.2f}"

message = format_price(19.5)
print(message)
print("Order summary — " + message)
```

Line by line:
1. `format_price` receives the numeric price.
2. The f-string formats it to two decimal places and builds text.
3. `return` gives the text back instead of displaying it.
4. `message` stores the returned string.
5. The first use prints it by itself.
6. The second use combines it with other text before printing.

Expected output:
```text
Price: $19.50
Order summary — Price: $19.50
```

### Exercise 4 — Pure score validation and separate reporting

The lesson leaves the validity rule open. Here, define a valid score as an integer from 0 through 100 inclusive.

```python
def is_valid_score(score):
    if score >= 0 and score <= 100:
        return True
    else:
        return False

scores = [95, 70, -5, 101, 0]

for score in scores:
    result = is_valid_score(score)
    print(f"{score}: {result}")
```

Line by line:
1. The function receives one score.
2. The condition checks both boundaries: at least 0 and at most 100.
3. It returns `True` when both are satisfied; otherwise it returns `False`.
4. The list contains valid and invalid examples.
5. The loop checks each score.
6. The loop prints the result; the function itself never prints or changes data.

Expected results: `95: True`, `70: True`, `-5: False`, `101: False`, `0: True`.

### Exercise 5 — Mutating and pure dictionary updates

Use a flat dictionary, as required by the lesson. Here, the discount is subtracted from the profile's `price`.

```python
def apply_discount_to_profile(profile, discount):
    profile["price"] = profile["price"] - discount

def apply_discount_to_profile_safely(profile, discount):
    updated_profile = profile.copy()
    updated_profile["price"] = updated_profile["price"] - discount
    return updated_profile

customer_a = {"name": "Asha", "price": 100}
apply_discount_to_profile(customer_a, 20)
print("Mutated profile:", customer_a)

customer_b = {"name": "Ravi", "price": 100}
discounted_profile = apply_discount_to_profile_safely(customer_b, 20)
print("Original profile:", customer_b)
print("New profile:", discounted_profile)
```

Line by line:
1. The first function receives a dictionary and discount amount.
2. It assigns a lower value to the dictionary's existing `"price"` key. This mutates the caller's dictionary.
3. The safe function first uses `.copy()` to create a new outer dictionary.
4. It changes the copied dictionary's `"price"` value, not the original.
5. `return` sends the updated copy back.
6. The first print shows `customer_a` changed to price 80.
7. The next print shows `customer_b` unchanged at 100.
8. The last print shows the new dictionary at price 80.

Expected:
```text
Mutated profile: {'name': 'Asha', 'price': 80}
Original profile: {'name': 'Ravi', 'price': 100}
New profile: {'name': 'Ravi', 'price': 80}
```

### Readiness check

You are ready to continue practicing this topic when you can explain, without looking at the notes:

- Why explicit parameters are safer than hidden global dependencies.
- Why printing is a side effect and why `return` is more reusable.
- Why changing a passed-in list or dictionary changes the caller's object.
- How to build and return a new collection without changing the original.
- Why calculation functions and presentation code should be separate.

**Important boundary:** This lesson introduces external file and I/O effects conceptually, but does not teach file handling. It also mentions time, randomness, environment variables, and databases as external dependencies without teaching those topics. Stay with the lesson's current Python concepts for now.
