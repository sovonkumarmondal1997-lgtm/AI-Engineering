# Stage 1 — Scope, Lifetime, and Global State
## Study Notes and Exercise Solutions

This guide is based on the uploaded lesson `05-scope-lifetime-and-global-state.md`. It explains the lesson's concepts and examples, then solves all five exercises using only the Python topics covered so far.

---

# Part 1 — Lesson summary and step-by-step teaching

## 1. What is scope?

**Scope** means the part of a program where a variable name can be used.

- **Local scope:** a name created inside a function. It belongs to that particular function call.
- **Global (module) scope:** a name created outside all functions, directly in the Python file. Functions can read it.

Python commonly describes name lookup using LEGB: Local, Enclosing, Global, Built-in. This lesson focuses on Local and Global. Each function call gets its own fresh local scope.

## 2. Local variables and `NameError`

```python
def calculate_total(price, quantity):
    order_total = price * quantity
    print(order_total)

calculate_total(9.99, 3)
```

The function prints `29.97`. But `order_total` was created inside the function, so this fails outside:

```python
print(order_total)
# NameError: name 'order_total' is not defined
```

The name is local to the function. If you need the result outside, return it:

```python
def calculate_total(price, quantity):
    order_total = price * quantity
    return order_total

total = calculate_total(9.99, 3)
print(total)
```

## 3. Reading a global variable

A function can read a global variable without using `global`:

```python
tax_rate = 0.08

def calculate_total_with_tax(price):
    return price * (1 + tax_rate)

print(calculate_total_with_tax(100))
print(tax_rate)
```

Output: `108.0` and `0.08`. Python first looks for `tax_rate` locally; when it does not find it, it looks in global scope. Reading a global is different from assigning a new value to its name.

## 4. Local shadowing

A local variable can have the same name as a global variable. The local one temporarily hides the global one inside the function.

```python
tax_rate = 0.08

def use_special_rate():
    tax_rate = 0.0
    print("Inside function:", tax_rate)

use_special_rate()
print("Outside function:", tax_rate)
```

Output:
```text
Inside function: 0.0
Outside function: 0.08
```

The assignment inside the function creates a local `tax_rate`; it does not change the global value.

## 5. Assignment and `UnboundLocalError`

Important rule: if Python sees an assignment to a name anywhere inside a function, it treats that name as local throughout that function.

```python
score = 0

def add_point():
    score = score + 1
    print(score)

add_point()
```

This raises `UnboundLocalError`. Python treats `score` as local because the function assigns to it. The right-hand side tries to read that local variable before it has received a value.

The safer approach is to accept the value as a parameter and return the updated value:

```python
def add_point(score):
    return score + 1

current_score = 0
current_score = add_point(current_score)
current_score = add_point(current_score)
print(current_score)
```

Output: `2`. The function does not need to know where the caller stores the score.

## 6. The `global` keyword

`global` tells Python that assignment inside the function should update the module-level name:

```python
total_signups = 0

def register_user():
    global total_signups
    total_signups = total_signups + 1

register_user()
register_user()
print(total_signups)
```

Output: `2`.

Although this works, use it rarely. It creates a hidden dependency: the function changes data outside itself, and its signature does not reveal that. Prefer parameters for inputs and return values for outputs.

## 7. Mutating a global list or dictionary

A global list can be changed inside a function without `global`, provided you mutate the object rather than reassign its name:

```python
shopping_cart = ["apples"]

def add_to_cart(item):
    shopping_cart.append(item)

add_to_cart("bread")
add_to_cart("milk")
print(shopping_cart)
```

Output: `['apples', 'bread', 'milk']`.

`.append()` changes the existing list; it does not assign a new object to the name `shopping_cart`. This is still risky because the function secretly changes shared data.

Make the dependency visible by passing the list in and returning it:

```python
def add_to_cart(cart, item):
    cart.append(item)
    return cart

shopping_cart = ["apples"]
shopping_cart = add_to_cart(shopping_cart, "bread")
shopping_cart = add_to_cart(shopping_cart, "milk")
print(shopping_cart)
```

The output is the same, but the function's signature now reveals the data it works with. The lesson uses the same approach for dictionaries:

```python
def update_email(profile, new_email):
    profile["email"] = new_email
    return profile

user_profile = {"name": "Grace", "email": "old@example.com"}
user_profile = update_email(user_profile, "grace@example.com")
print(user_profile)
```

Output: `{'name': 'Grace', 'email': 'grace@example.com'}`. The function updates the dictionary explicitly passed to it.

## 8. Scope versus lifetime

**Scope** is where a name can be used. **Lifetime** is how long the object/value remains alive while something still refers to it.

```python
def build_profile(name):
    greeting = f"Welcome, {name}!"
    return greeting

message = build_profile("Ada")
print(message)
```

Output: `Welcome, Ada!`. The local name `greeting` is no longer available after the function returns. But its string value remains available because `return` passed it to the caller and `message` now refers to it.

## 9. All six lesson examples

1. **Global tax configuration:** `tax_rate = 0.08` is read by `calculate_total_with_tax(price, quantity)`. For price 20 and quantity 3, output is `Order total with tax: $64.80`; the rate remains `0.08`.
2. **Shadowing a practice score:** global `high_score = 100`; function-local `high_score = 0`. It prints practice score `0`, then global score `100`.
3. **Score counter:** `add_point(score)` returns `score + 1`. Calling it twice from `current_score = 0` produces `Current score: 2`.
4. **Shopping cart:** risky function mutates a global cart; safe function accepts `cart` and `item` and returns the cart. Both show `['apples', 'bread']`, but the safe function exposes its dependency.
5. **User profile:** `update_email(profile, new_email)` updates the passed dictionary and returns it; Grace's email becomes `grace@example.com`.
6. **Account balance:** `apply_deposit(balance, amount)` returns a new balance. Starting at 100, deposits of 50 and 25 produce 150 and then 175.

## 10. Common mistakes and safe habits

- Using a local variable outside its function causes `NameError`.
- Assigning to a name inside a function makes it local; reading it before assignment causes `UnboundLocalError`.
- A local variable with a global's name shadows it; it does not update the global.
- `global` works but hides dependencies and should be rare.
- Mutating a global list or dictionary can change shared state even without `global`.
- Prefer explicit parameters, return values, clear names, and predictable ownership of data. Avoid unexpected mutation.

---

# Part 2 — Learning-level assessment and all exercise solutions

## Your current level

Based on the Stage 1 roadmap context from our earlier discussions, you have covered computational thinking, Python fundamentals, conditionals, loops, collections, and the preceding lessons on functions, parameters, and return values. Your appropriate level here is **beginner progressing toward intermediate Python**: you should now practise how functions access data and how values move between a caller and a function.

The complete, current project tree was not attached in this turn. Earlier reviews identified some Stage 1 overview and project files as incomplete or stubs, so I cannot claim to have freshly audited every folder. The solutions below stay within this lesson's concepts: functions, parameters, return values, lists, dictionaries, and scope.

## Exercise 1 — Local variable outside a function

```python
def show_message():
    message = "Python is learning"
    print(message)

show_message()
print(message)
```

- `def show_message()` defines a function.
- `message = ...` creates a local variable.
- The first `print` works because it runs inside the function.
- `show_message()` calls the function.
- The final `print(message)` is outside its local scope, so Python raises `NameError`.
- The function's local name is not available to outside code. To make the value available, return it and assign the result outside.

## Exercise 2 — Read a global discount rate

```python
discount_rate = 0.10

def calculate_discounted_price(price):
    return price * (1 - discount_rate)

final_price = calculate_discounted_price(200)
print(final_price)
print(discount_rate)
```

- `discount_rate = 0.10` creates a global value representing 10%.
- The function receives the price as a parameter.
- It reads the global rate and calculates price after discount.
- `200 * (1 - 0.10)` equals `180`.
- The function only reads the global; it does not assign to it.
- Output: `180.0`, then `0.1`. The global rate remains unchanged.

## Exercise 3 — Observe the error, then fix it two ways

**Incorrect version:**

```python
total = 0

def add_one():
    total = total + 1
    return total

add_one()
```

- Python sees `total = ...` inside the function and treats `total` as local throughout it.
- The right side tries to read that local value before it is assigned.
- Result: `UnboundLocalError`.

**Fix A — use `global`:**

```python
total = 0

def add_one_global():
    global total
    total = total + 1

add_one_global()
print(total)
```

`global total` tells Python to update the global variable. The output is `1`. This demonstrates the keyword, but it is not the preferred general design.

**Fix B — use a parameter and return value:**

```python
def add_one(total):
    return total + 1

total = 0
total = add_one(total)
print(total)
```

The caller passes the current value; the function returns the updated value. Output: `1`. This makes the function's dependency explicit and is the recommended pattern.

## Exercise 4 — Global list versus explicit parameter

```python
favorite_books = ["Dune"]

def add_book_global(book):
    favorite_books.append(book)

add_book_global("1984")
print(favorite_books)

def add_book(books, book):
    books.append(book)
    return books

favorite_books = ["Dune"]
favorite_books = add_book(favorite_books, "1984")
print(favorite_books)
```

- The first function reaches outside itself and mutates the global list. Its signature does not reveal that dependency.
- The second function receives the list and book explicitly, mutates the supplied list, and returns it.
- Both outputs are `['Dune', '1984']`.
- Prefer `add_book(books, book)` in a larger program because its signature clearly shows which list it changes. Note that it still mutates the passed-in list; the important improvement here is making that list an explicit input rather than secretly using a global.

## Exercise 5 — Apply interest three times

```python
def apply_interest(balance, rate):
    return balance * (1 + rate)

balance = 1000
rate = 0.05

balance = apply_interest(balance, rate)
print("After first period:", balance)

balance = apply_interest(balance, rate)
print("After second period:", balance)

balance = apply_interest(balance, rate)
print("After third period:", balance)
```

- The function accepts the current balance and interest rate.
- `balance * (1 + rate)` calculates the balance after interest. Here `0.05` means 5%.
- The first call calculates `1000 × 1.05 = 1050`.
- The result is assigned back to `balance`.
- The second call uses 1050, producing 1102.5.
- The third call uses 1102.5, producing 1157.625.
- Each returned value becomes the next call's input; the function does not need a global balance.

---

## Readiness checklist

Before moving on, confirm that you can:
- Explain local and global scope.
- Distinguish `NameError` from `UnboundLocalError`.
- Explain reading versus assigning a global name.
- Demonstrate local shadowing.
- Explain why a global list/dictionary can be mutated without `global`.
- Use parameters and return values to make dependencies explicit.
- Explain why a returned value can outlive the local name that first referred to it.

**Learning boundary:** this lesson covers scope, lifetime, and global state. Nested-function enclosing scopes and the full LEGB model are mentioned but intentionally not explored here; the source lesson says those can be covered later.
