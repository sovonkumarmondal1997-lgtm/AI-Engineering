# 05 — Scope, Lifetime, and Global State
## Complete Lesson Summary, Project-Tree Assessment, and Exercise Solutions

**Roadmap position:** Stage 1 → Module 03 — Control Flow, Functions, Scope, and Errors → Lesson 05  
**Source lesson:** `05-scope-lifetime-and-global-state.md`

---

# Part A — Complete Lesson Summary (under 5,000 words)

## 1. Why scope and state matter

Every variable name in Python exists within a region of the program. That region determines where the name can be used. A variable created inside one function is not automatically available in another function or outside the function.

Understanding scope helps prevent two common problems:

- A program tries to use a name that is not available, causing an error.
- A function unexpectedly changes data that another part of the program depends on.

For every variable, ask:

1. Where can this name be used?
2. Who else might be affected if the value it refers to changes?

## 2. Learning outcomes and prerequisites

After this lesson, you should be able to explain:

- Local scope and global/module scope.
- Why a function's local variable cannot normally be used outside it.
- Why a function can read a global variable without `global`.
- Why assigning to a global-sounding name inside a function is different from reading it.
- Local shadowing.
- `NameError` and `UnboundLocalError`.
- The purpose and risks of the `global` keyword.
- Why a global list or dictionary can be mutated without `global`.
- The difference between a name's scope and the lifetime of the object it refers to.
- Safe habits for managing state.

The lesson assumes that you already understand functions, parameters, `return`, lists, dictionaries, mutation, and immutability.

## 3. Key terms

| Term | Meaning |
|---|---|
| Scope | The part of a program where a name can be used. |
| Local scope | The names belonging to one function call. |
| Global/module scope | Names created outside every function in a Python file. |
| `NameError` | Python cannot find the name in a scope it can access. |
| Shadowing | A local name temporarily hides a global name with the same spelling. |
| Assignment | Using `=` to make a name refer to a value. |
| `UnboundLocalError` | A function tries to read a local variable before assigning it. |
| `global` | Declares that a name used in a function refers to the module-level name. |
| Mutable global state | A global list, dictionary, or other mutable object that functions can change. |
| Lifetime | How long an object remains alive because it is still referenced. |

## 4. What scope means: Local and Global

Python commonly describes name lookup using **LEGB**:

- **L — Local:** the current function's local names.
- **E — Enclosing:** names in an enclosing function when functions are nested.
- **G — Global:** names defined at module level.
- **B — Built-in:** names supplied by Python, such as `print`.

This lesson focuses on Local and Global. Enclosing scope is mentioned as part of LEGB but is not taught in detail here.

### Local scope

A name created inside a function belongs to that function call. It is available inside that call, not automatically outside it.

```python
def calculate_total(price, quantity):
    order_total = price * quantity
    print(order_total)

calculate_total(9.99, 3)
```

Output:

```text
29.97
```

Step by step:

1. Python defines `calculate_total`.
2. The call passes `9.99` into `price` and `3` into `quantity`.
3. The function creates the local name `order_total`.
4. It calculates `9.99 * 3`, which is `29.97`.
5. `print` displays the result.

This does not work:

```python
calculate_total(9.99, 3)
print(order_total)
```

Python raises:

```text
NameError: name 'order_total' is not defined
```

`order_total` was created only inside the function. The outside code cannot use that local name. This is normal scope behavior, not a Python bug.

Every function call gets its own fresh local scope. Calling the same function several times creates separate local working names for each call.

### Global/module scope

A variable created outside all functions belongs to the module's global scope. A function can read it without any special declaration.

```python
tax_rate = 0.08

def calculate_total_with_tax(price):
    return price * (1 + tax_rate)

print(calculate_total_with_tax(100))
print(tax_rate)
```

Output:

```text
108.0
0.08
```

How lookup works:

1. The function needs `tax_rate`.
2. Python first checks the function's local scope.
3. It does not find `tax_rate` locally.
4. Python checks global scope and finds `tax_rate = 0.08`.
5. The function calculates `100 * (1 + 0.08)`, producing `108.0`.

**Important:** Reading a global variable does not require `global`. However, the function now has a dependency that is not visible in its parameter list. A stable configuration value can sometimes be reasonable, but use this dependency deliberately.

Reading a global and assigning to a global are different operations.

## 5. Local shadowing

Shadowing happens when a function creates a local variable with the same name as a global variable.

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

Explanation:

1. The module-level `tax_rate` is `0.08`.
2. The assignment inside `use_special_rate` creates a local `tax_rate`.
3. Inside that function, Python uses the local value `0.0`.
4. The local variable does not overwrite the global variable.
5. After the call, the outside print reads the global value `0.08`.

The two names have the same spelling but belong to different scopes.

## 6. Assignment and `UnboundLocalError`

A critical Python rule:

**If a function assigns to a name anywhere in its body, Python treats that name as local throughout the entire function, unless it is declared `global`.**

Consider:

```python
score = 0

def add_point():
    score = score + 1
    print(score)

add_point()
```

Python raises an error similar to:

```text
UnboundLocalError: cannot access local variable 'score'
where it is not associated with a value
```

Why?

1. Python sees `score = score + 1` inside the function.
2. Because the function assigns to `score`, Python classifies `score` as local for the whole function.
3. The right-hand side tries to read that local `score`.
4. But the local `score` has not received a value yet.
5. The read-before-assignment causes `UnboundLocalError`.

This differs from `NameError`: Python has identified `score` as a local name, but it has not yet been assigned a usable value.

### Safer solution: parameters and return values

```python
def add_point(score):
    return score + 1

current_score = 0
current_score = add_point(current_score)
current_score = add_point(current_score)

print(current_score)
```

Output:

```text
2
```

Line by line:

- `def add_point(score):` defines a function with a parameter.
- `return score + 1` calculates and returns a new number.
- `current_score = 0` initializes the caller's value.
- The first call passes `0` and returns `1`.
- The second call passes `1` and returns `2`.
- The final `print` displays `2`.

The function does not need to know that the caller stores the value in a variable named `current_score`. Its input and output are explicit.

## 7. The `global` keyword

Python allows a function to assign to a module-level name by declaring it with `global`.

```python
total_signups = 0

def register_user():
    global total_signups
    total_signups = total_signups + 1

register_user()
register_user()
print(total_signups)
```

Output:

```text
2
```

Explanation:

1. `total_signups = 0` creates the global variable.
2. `global total_signups` tells Python that this function uses the global name, not a new local name.
3. The assignment reads the global value, adds one, and updates the global value.
4. The function is called twice.
5. The global value becomes `2`.

### Why `global` should be rare

A function that changes global state has a hidden dependency. Its signature does not reveal that it changes `total_signups`. To understand the function's effects, a reader must inspect its body and other code that uses the same global.

As a program grows, many functions changing shared state make behavior harder to trace and debug. Learn `global` so you can understand it when you encounter it, but prefer parameters and return values for ordinary function design.

## 8. Mutable global state

A global list or dictionary can be changed inside a function without `global`, as long as the function mutates the object rather than assigning a new object to the global name.

```python
shopping_cart = ["apples"]

def add_to_cart(item):
    shopping_cart.append(item)

add_to_cart("bread")
add_to_cart("milk")
print(shopping_cart)
```

Output:

```text
['apples', 'bread', 'milk']
```

Why no `global` is required:

- `shopping_cart.append(item)` does not assign a new value to the name `shopping_cart`.
- Python reads the global name and obtains the list it refers to.
- `.append()` changes that existing list object.
- Since the function does not assign to the name `shopping_cart`, Python does not classify it as local.

### Why this is risky

The function signature `add_to_cart(item)` suggests that the function needs only an item. It does not reveal that the function also changes a global shopping cart. Another function could also modify that same list, making the overall behavior difficult to follow.

### Safer approach: pass the list and return it

```python
def add_to_cart(cart, item):
    cart.append(item)
    return cart

shopping_cart = ["apples"]
shopping_cart = add_to_cart(shopping_cart, "bread")
shopping_cart = add_to_cart(shopping_cart, "milk")
print(shopping_cart)
```

Output:

```text
['apples', 'bread', 'milk']
```

The function's signature makes the dependency visible: it receives a cart and an item, and returns the updated cart. The list is still mutated, but the object being changed is explicitly passed in.

The same idea applies to dictionaries:

```python
def update_email(profile, new_email):
    profile["email"] = new_email
    return profile

user_profile = {"name": "Grace", "email": "old@example.com"}
user_profile = update_email(user_profile, "grace@example.com")

print(user_profile)
```

Output:

```text
{'name': 'Grace', 'email': 'grace@example.com'}
```

`profile` is the dictionary passed by the caller. The assignment to `profile["email"]` changes that dictionary. Returning it makes the result explicit.

## 9. Scope versus lifetime

These two ideas are related, but they are not the same:

- **Scope** asks: where can I use this name?
- **Lifetime** asks: how long does the object/value remain alive?

Example:

```python
def build_profile(name):
    greeting = f"Welcome, {name}!"
    return greeting

message = build_profile("Ada")
print(message)
```

Output:

```text
Welcome, Ada!
```

Step by step:

1. The function is called with `"Ada"`.
2. It creates the local name `greeting`.
3. The string value becomes `"Welcome, Ada!"`.
4. `return greeting` hands that value back to the caller.
5. The caller stores the returned value in `message`.
6. The function call finishes, so its local name `greeting` is no longer available through that function's local scope.
7. The string value remains available because `message` refers to it.

A local name can stop being available while the value it referred to remains in use elsewhere. A useful beginner model is that an object remains alive while it is still referenced or reachable somewhere in the program. The details of Python memory cleanup are outside this lesson.

## 10. Six safe engineering habits

1. **Prefer parameters for inputs.** If a function needs a value, pass it in instead of silently reading an outer variable.
2. **Prefer return values for outputs.** Return the result rather than assigning to an outside variable.
3. **Avoid hidden dependencies.** A reader should understand what a function needs and produces from its signature.
4. **Avoid unexpected mutation.** Do not change a list or dictionary that was not explicitly passed to the function for that purpose.
5. **Use clear names.** `cart` communicates more than vague names such as `data` or `x`.
6. **Keep state ownership obvious.** Make it clear which part of the program is responsible for creating and updating each piece of data.

## 11. All six worked examples from the lesson

### Example 1 — Reading a global tax-rate configuration

```python
tax_rate = 0.08

def calculate_total_with_tax(price, quantity):
    subtotal = price * quantity
    return subtotal * (1 + tax_rate)

order_total = calculate_total_with_tax(20, 3)
print(f"Order total with tax: ${order_total:.2f}")
print(f"Configured tax rate: {tax_rate}")
```

Output:

```text
Order total with tax: $64.80
Configured tax rate: 0.08
```

Explanation:

- `tax_rate` is defined outside the function, so it is global.
- `calculate_total_with_tax` receives `price` and `quantity`.
- `subtotal` is local and becomes `20 * 3 = 60`.
- The function reads the global `tax_rate`, then calculates `60 * 1.08 = 64.8`.
- `:.2f` formats the amount with two digits after the decimal point.
- The function only reads the tax rate; it does not change it.

### Example 2 — Local shadowing with a practice score

```python
high_score = 100

def show_practice_score():
    high_score = 0
    print("Practice score starts at:", high_score)

show_practice_score()
print("Real high score is still:", high_score)
```

Output:

```text
Practice score starts at: 0
Real high score is still: 100
```

The function creates a local `high_score` equal to `0`. The global `high_score` remains `100`.

### Example 3 — A score counter using parameters and return values

```python
def add_point(score):
    return score + 1

current_score = 0
current_score = add_point(current_score)
current_score = add_point(current_score)

print("Current score:", current_score)
```

Output:

```text
Current score: 2
```

Each call receives the current score and returns the updated score. The caller stores the result. The function does not access global state.

### Example 4 — Risky and safe shopping-cart versions

```python
def add_to_cart_risky(item):
    shopping_cart.append(item)

shopping_cart = ["apples"]
add_to_cart_risky("bread")
print("Risky version result:", shopping_cart)


def add_to_cart_safe(cart, item):
    cart.append(item)
    return cart

fresh_cart = ["apples"]
fresh_cart = add_to_cart_safe(fresh_cart, "bread")
print("Safe version result:", fresh_cart)
```

Output:

```text
Risky version result: ['apples', 'bread']
Safe version result: ['apples', 'bread']
```

Both versions change a list. The risky function silently uses the global `shopping_cart`; its parameter list does not show that dependency. The safe version receives the cart explicitly and returns it.

### Example 5 — Updating a user-profile dictionary safely

```python
def update_email(profile, new_email):
    profile["email"] = new_email
    return profile

user_profile = {"name": "Grace", "email": "old@example.com"}
user_profile = update_email(user_profile, "grace@example.com")

print(user_profile)
```

Output:

```text
{'name': 'Grace', 'email': 'grace@example.com'}
```

The function receives the dictionary and the new email. It updates the dictionary passed to it and returns that dictionary. It does not depend on a global `user_profile` name.

### Example 6 — Passing and returning a balance across calls

```python
def apply_deposit(balance, amount):
    updated_balance = balance + amount
    return updated_balance

account_balance = 100
account_balance = apply_deposit(account_balance, 50)
print("Balance after first deposit:", account_balance)

account_balance = apply_deposit(account_balance, 25)
print("Balance after second deposit:", account_balance)
```

Output:

```text
Balance after first deposit: 150
Balance after second deposit: 175
```

- The first call receives `100` and `50`, then returns `150`.
- The caller stores `150` in `account_balance`.
- The second call receives `150` and `25`, then returns `175`.
- `updated_balance` is local to each function call, but the returned number remains available through `account_balance`.

## 12. Common beginner mistakes

- Trying to use a local variable after its function has returned: this raises `NameError`.
- Assuming an assignment inside a function changes a global variable with the same name: it normally creates a local variable that shadows the global.
- Writing `score = score + 1` inside a function without `global` or a parameter: this can raise `UnboundLocalError`.
- Using `global` as the first solution instead of passing a value in and returning a result.
- Assuming a global list or dictionary cannot be changed unless `global` is used: mutation can change it without reassigning its name.
- Hiding a function's dependencies in global variables instead of showing them in its parameters.

## 13. Connection to Applied AI and Agentic AI engineering

An AI agent may need to keep conversation history, tool results, and a current plan. If many functions silently reach into and mutate one large global object, it becomes difficult to understand which function changed the state and why.

Passing state into functions and returning updated state makes dependencies visible. It also makes functions easier to inspect and test independently. This lesson's parameter-and-return-value discipline is therefore useful when building larger agent workflows.

---

# Part B — Project-Tree Review and Current Learning Level

## 1. Where this lesson fits

Your Stage 1 roadmap is **Programming & Computational Thinking**. The roadmap snapshot records 25 modules/folders including the overview, 38 folders, and 311 files. It progresses from basic programming concepts into production-oriented Python.

The relevant sequence is:

| Module | Main focus |
|---|---|
| 00 | Stage 1 overview, learning plan, and capstone projects |
| 01 | Computational Thinking and Program Design |
| 02 | Python Core Language and Data Types |
| 03 | Control Flow, Functions, Scope, and Errors |
| 04 | Problem-Solving, Collections, and Algorithmic Habits |
| 05 | Text Files, Structured Data, and CLI Programs |
| 06 | Modules, Packages, Dependencies, and Code Quality |
| 07 | Testing and Systematic Debugging |
| 08 | Object-Oriented Design, Data Modelling, and Functional Style |
| 09–10 | Advanced production-oriented Python foundations and production habits |
| 11–19 | Advanced object design, metaprogramming, standard library, binary/text processing, modern Python, testing, performance, packaging, and CPython internals |
| 20 onward | Further specialist Python engineering topics in the roadmap |

Module 03's lesson order is:

1. Conditionals, guards, and Boolean logic.
2. `for`/`while` loops and loop control.
3. Functions, parameters, and return values.
4. Function arguments, defaults, and docstrings.
5. Scope, lifetime, and global state.
6. Pure functions and side effects.
7. Exceptions, validation, and useful errors.

This attached lesson is therefore the fifth lesson in Module 03. It relies directly on the earlier function and mutability lessons.

## 2. Relevant learning progress

Your prior work shows exposure to:

- Variables, basic Python data types, strings, lists, tuples, dictionaries, and sets.
- Mutability, immutability, copying, and aliasing.
- Conditions, loops, and loop control.
- Functions, parameters, return values, argument design, defaults, and docstrings.
- Collection operations and problem-solving topics such as filtering, grouping, sorting, Big-O, comprehensions, recursion, and parsing.

Your current level is assessed as **beginner progressing toward intermediate**. You have covered a meaningful range of Python foundations and problem-solving, but a roadmap topic being present or previously studied does not automatically prove independent mastery.

## 3. Scope boundaries for these solutions

The five exercises can be solved using only:

- Variables and assignment.
- Function definitions and calls.
- Parameters and return values.
- Local and global names.
- `NameError` and `UnboundLocalError`.
- Lists, dictionaries, and mutation.
- `print()` to inspect results.

No class definitions, external packages, decorators, file handling, or advanced testing framework is needed.

---

# Part C — All Five Exercises Solved Step by Step (under 3,500 words)

## Exercise 1 — Create a local variable and try to use it outside

**Requirement:** Create a local variable, print it inside the function, then try to print the same name outside. Identify the error and explain why it occurs.

### Solution

```python
def show_customer():
    customer_name = "Asha"
    print("Inside function:", customer_name)

show_customer()
print("Outside function:", customer_name)
```

### Line-by-line explanation

1. `def show_customer():` defines a function named `show_customer`.
2. `customer_name = "Asha"` creates a local variable inside the function.
3. `print("Inside function:", customer_name)` reads and displays that local variable.
4. `show_customer()` calls the function, so the first print succeeds.
5. `print("Outside function:", customer_name)` tries to use the local name from outside the function.

### Output

```text
Inside function: Asha
NameError: name 'customer_name' is not defined
```

The exact traceback includes a file name and line number, which vary by where you run the code.

**Why the error occurs:** `customer_name` belongs to the function's local scope. The outside code cannot access that local name. If you need the value outside, return it:

```python
def show_customer():
    customer_name = "Asha"
    return customer_name

customer_name = show_customer()
print("Outside function:", customer_name)
```

Output:

```text
Outside function: Asha
```

The function returns the value, and the caller stores it in its own variable.

---

## Exercise 2 — Read a global `discount_rate`

**Requirement:** Create a global `discount_rate`, read it inside a function without passing it as a parameter, calculate a discounted price, and confirm that the global value remains unchanged.

### Solution

```python
discount_rate = 0.10

def calculate_discounted_price(original_price):
    discount_amount = original_price * discount_rate
    final_price = original_price - discount_amount
    return final_price

price = 2000
discounted_price = calculate_discounted_price(price)

print("Original price:", price)
print("Discounted price:", discounted_price)
print("Discount rate:", discount_rate)
```

### Line-by-line explanation

1. `discount_rate = 0.10` creates a global value representing a 10% discount.
2. `def calculate_discounted_price(original_price):` defines a function with the original price as an input.
3. `discount_amount = original_price * discount_rate` calculates the discount. Python finds `discount_rate` in global scope because it is not a local name.
4. `final_price = original_price - discount_amount` subtracts the discount from the original price.
5. `return final_price` sends the result back to the caller.
6. `price = 2000` stores the original price.
7. `discounted_price = calculate_discounted_price(price)` calls the function and stores its returned value.
8. The three `print()` calls display the original price, result, and global discount rate.

### Calculation

- Discount = `2000 * 0.10 = 200`
- Final price = `2000 - 200 = 1800`

### Output

```text
Original price: 2000
Discounted price: 1800.0
Discount rate: 0.1
```

**Conclusion:** The function reads the global variable but never assigns a new value to it. Therefore, `discount_rate` remains `0.10`.

**Engineering note:** This exercise demonstrates global reading. For a function that needs a changing discount rate, passing `discount_rate` as a second parameter would make the dependency more visible. The exercise specifically asks you to read the global, so the main solution follows that requirement.

---

## Exercise 3 — Reproduce `UnboundLocalError`, then fix it two ways

**Requirement:** First write `total = total + 1` inside a function without `global` or a parameter. Then fix it using `global`, and fix it again using a parameter and return value.

### Version A — The incorrect version

Run this snippet separately:

```python
total = 0

def increase_total():
    total = total + 1
    print(total)

increase_total()
```

Expected error:

```text
UnboundLocalError: cannot access local variable 'total'
where it is not associated with a value
```

**Why:** Python sees an assignment to `total` inside the function and treats `total` as local throughout that function. The right-hand side tries to read the local value before it has been assigned.

### Version B — Fix using `global`

Run this as a separate example:

```python
total = 0

def increase_total():
    global total
    total = total + 1

increase_total()
increase_total()

print("Total:", total)
```

Output:

```text
Total: 2
```

Line by line:

1. `total = 0` creates the global counter.
2. `def increase_total():` defines the function.
3. `global total` declares that the function refers to the global name.
4. `total = total + 1` reads the global number and updates it by one.
5. The first call changes `total` from `0` to `1`.
6. The second call changes it from `1` to `2`.
7. `print` displays the updated global value.

This works, but the function changes shared state that is not visible in its parameters.

### Version C — Fix using a parameter and return value (preferred)

Run this as another separate example:

```python
def increase_total(total):
    return total + 1

total = 0
total = increase_total(total)
total = increase_total(total)

print("Total:", total)
```

Output:

```text
Total: 2
```

Line by line:

1. `def increase_total(total):` defines a function that receives the current total.
2. `return total + 1` calculates and returns the new total.
3. `total = 0` initializes the caller's value.
4. The first call passes `0` and returns `1`; the caller stores `1`.
5. The second call passes `1` and returns `2`; the caller stores `2`.
6. The final print displays `2`.

**Comparison:** Both corrected versions work. The parameter-and-return-value version is preferred because its input and output are visible in the function interface. It does not secretly update a global variable.

---

## Exercise 4 — Add a book to a global list and with a parameter

**Requirement:** Create a global `favorite_books` list. Write one function that directly mutates the global list and another that accepts a list and returns the updated list. Compare their signatures.

### Version A — Direct global mutation

```python
favorite_books = ["The Hobbit"]

def add_book_risky(book):
    favorite_books.append(book)

add_book_risky("Dune")
print("Global-list version:", favorite_books)
```

Output:

```text
Global-list version: ['The Hobbit', 'Dune']
```

Line by line:

1. `favorite_books = ["The Hobbit"]` creates a global list.
2. `def add_book_risky(book):` defines a function that receives only a book name.
3. `favorite_books.append(book)` looks up the global list and mutates it by adding the book.
4. `add_book_risky("Dune")` adds `"Dune"` to the global list.
5. `print` displays the changed list.

No `global` statement is required because the function mutates the existing list; it does not reassign the name `favorite_books`.

### Version B — Pass the list and return it

```python
def add_book_safe(books, book):
    books.append(book)
    return books

favorite_books = ["The Hobbit"]
favorite_books = add_book_safe(favorite_books, "Dune")

print("Parameter version:", favorite_books)
```

Output:

```text
Parameter version: ['The Hobbit', 'Dune']
```

Line by line:

1. `def add_book_safe(books, book):` defines a function that explicitly receives the list and the new book.
2. `books.append(book)` adds the book to the list passed by the caller.
3. `return books` returns the updated list.
4. `favorite_books = ["The Hobbit"]` creates the caller's list.
5. `favorite_books = add_book_safe(favorite_books, "Dune")` passes the list and book into the function, then stores the returned list.
6. `print` displays the result.

### Signature comparison

| Function | Signature | Dependency |
|---|---|---|
| Risky | `add_book_risky(book)` | Secretly uses the global `favorite_books` list. |
| Safer | `add_book_safe(books, book)` | Clearly receives the list and book as inputs. |

**Preferred choice:** `add_book_safe(books, book)`. Its signature makes the dependency explicit, so another caller can pass a different list. It is easier to understand and reuse.

---

## Exercise 5 — Apply interest three times using the previous result

**Requirement:** Write `apply_interest(balance, rate)`, return a new balance, call it three times, and use each returned balance as the next call's input.

For this exercise, choose a rate of `5%`, represented as `0.05`. The formula is:

`new balance = current balance * (1 + rate)`

### Solution

```python
def apply_interest(balance, rate):
    new_balance = balance * (1 + rate)
    return new_balance

account_balance = 1000
interest_rate = 0.05

account_balance = apply_interest(account_balance, interest_rate)
print("After first application:", account_balance)

account_balance = apply_interest(account_balance, interest_rate)
print("After second application:", account_balance)

account_balance = apply_interest(account_balance, interest_rate)
print("After third application:", account_balance)
```

### Line-by-line explanation

1. `def apply_interest(balance, rate):` defines a function with two parameters: the current balance and the interest rate.
2. `new_balance = balance * (1 + rate)` calculates the balance after applying interest.
3. `return new_balance` sends the calculated value back to the caller.
4. `account_balance = 1000` sets the starting balance.
5. `interest_rate = 0.05` represents 5% as a decimal.
6. The first function call passes `1000` and `0.05`. The result is stored back in `account_balance`.
7. The first print displays the first updated balance.
8. The second call uses that already-updated balance as its input.
9. The second print displays the second updated balance.
10. The third call again uses the latest balance.
11. The final print displays the third updated balance.

### Calculation

- Start: `1000`
- First application: `1000 * 1.05 = 1050`
- Second application: `1050 * 1.05 = 1102.5`
- Third application: `1102.5 * 1.05 = 1157.625`

### Output

```text
After first application: 1050.0
After second application: 1102.5
After third application: 1157.625
```

**Important observation:** The function does not store or update a global balance. It receives a balance, calculates a result, and returns it. The caller owns the `account_balance` variable and decides to use the returned result for the next call.

---

# Part D — Revision Sheet and Self-Check

## 1. Essential rules to remember

| Situation | Result |
|---|---|
| Use a local name outside its function | Usually `NameError` |
| Read a global name inside a function | Allowed without `global` |
| Assign to a name inside a function | Python treats it as local throughout the function unless declared `global` |
| Read that local name before assigning it | `UnboundLocalError` |
| Assign to a same-named local variable | Shadows the global; does not update it |
| Use `global name` and then assign | Updates the module-level name |
| Mutate a global list/dictionary | Possible without `global`; still a hidden side effect |
| Pass a value in and return a result | Makes the function's dependency explicit |
| Return a local value | The caller can keep using the returned value |
| Function call finishes | Its local names are no longer available through that call |

## 2. Five questions to test your understanding

1. What is the difference between local scope and global scope?
2. Why does `score = score + 1` inside a function cause `UnboundLocalError` when `score` has not been declared global or passed as a parameter?
3. Why can `.append()` change a global list without using `global`?
4. Why is `add_to_cart(cart, item)` clearer than a function that accepts only `item` but secretly modifies a global cart?
5. How can a returned value remain usable after the local variable that originally referred to it is no longer available?

## 3. Completion checklist

- [ ] I can explain local and global scope.
- [ ] I can explain why a local variable cannot be used outside its function.
- [ ] I can recognize `NameError`.
- [ ] I can explain why reading a global differs from assigning to it.
- [ ] I can demonstrate shadowing.
- [ ] I can explain and recognize `UnboundLocalError`.
- [ ] I can write a small example using `global` and explain its trade-off.
- [ ] I can explain why a global list or dictionary can be mutated without `global`.
- [ ] I can rewrite hidden global dependencies using parameters and return values.
- [ ] I can distinguish a name's scope from the lifetime of the object it refers to.
- [ ] I have completed all five exercises.

## 4. Final engineering takeaway

For ordinary function design, prefer this pattern:

```python
def update_value(current_value, change):
    updated_value = current_value + change
    return updated_value

value = 10
value = update_value(value, 5)
print(value)
```

The function's inputs are visible in its parameters, and its result is visible through `return`. The caller owns the state and decides what to do with the returned value. This is easier to understand than functions that silently depend on and change global variables.

**Lesson status:** This guide covers the concepts and all five exercises from the attached source lesson. Understanding the explanations is the first step; independently predicting the outputs and writing the solutions again without looking are the practical checks of mastery.
