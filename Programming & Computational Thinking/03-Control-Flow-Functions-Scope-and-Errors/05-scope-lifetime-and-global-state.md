# Scope, Lifetime, and Global State

## Why scope and state matter

Every name in a Python program — every variable — exists somewhere, and
that "somewhere" has boundaries. A variable created inside one function
is not automatically visible inside another; a variable created outside
every function behaves differently again. Without understanding these
boundaries, a program's behavior can feel unpredictable: a value that
"should" be there is missing, or worse, a function quietly changes data
that some completely different part of the program was relying on. This
lesson makes those boundaries explicit, so you can always answer two
questions with confidence: "where can I use this name?" and "who else
might be affected if I change this value?"

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain what **scope** means, and describe the difference between
  **local scope** and **global (module) scope** in plain English.
- Explain why a variable created inside a function cannot normally be
  used outside it, and read the resulting `NameError`.
- Explain why a function can freely **read** a global variable, and why
  that is different from **assigning** a new value to it.
- Explain **local shadowing**: what happens when a local variable shares
  its name with a global one, and show that the global value is
  unaffected.
- Explain why assigning to a name anywhere inside a function makes Python
  treat that name as local for the *entire* function, and read the
  resulting `UnboundLocalError`.
- Explain what the `global` keyword does, write one small correct example
  of it, and explain why it should be rare in real programs.
- Explain why a global **list** or **dictionary** can be mutated inside a
  function *without* `global`, why this is risky, and how to avoid it
  using parameters and return values instead.
- Explain the difference between a local name's **scope** and the
  **lifetime** of the value it refers to.
- List the safe engineering habits that avoid most scope-related bugs
  entirely.

## Prerequisites

- [Functions, Parameters, and Return Values](03-functions-parameters-and-return-values.md) —
  this lesson assumes functions, parameters, and `return` are already
  comfortable.
- [Lists: Mutation, Copying, and Aliasing](../02-Python-Core-Language-and-Data-Types/05-lists-mutation-copying-and-aliasing.md)
  and
  [Dictionaries and Lookups](../02-Python-Core-Language-and-Data-Types/07-dictionaries-and-lookups.md) —
  the mutable global state section mutates a list and a dictionary
  directly, and assumes both are already familiar.
- [Mutability and Immutability](../02-Python-Core-Language-and-Data-Types/10-mutability-and-immutability.md) —
  the "labels on boxes" model this lesson relies on to explain exactly
  why mutating a global collection is different from reassigning a
  global name.

## Key terms

| Term | Plain-English definition |
|---|---|
| **Scope** | The region of a program where a given variable name can actually be used. |
| **Local scope** | The scope belonging to one function call; names created inside a function exist only there. |
| **Global scope** (also called **module scope**) | The scope belonging to the whole file; names created outside every function exist here. |
| **`NameError`** | The error Python raises when code tries to use a name that does not exist in any scope it can currently see. |
| **Shadowing** | When a local variable uses the same name as a global variable, temporarily hiding the global one inside that function. |
| **Assignment** | Creating or updating what a name refers to, using `=`. |
| **`UnboundLocalError`** | The error Python raises when code tries to *read* a local name before that name has been assigned a value inside the current function. |
| **`global` keyword** | A statement inside a function that tells Python "the name that follows refers to the global variable, not a new local one." |
| **Mutable global state** | A mutable object (such as a list or dictionary) stored in global scope, which can be changed from inside a function without ever reassigning its name. |
| **Lifetime** | How long an object or value remains alive, which lasts as long as it is still referenced somewhere. This is separate from a name's scope, which is only where that name can be used. |

## Step-by-step explanation

### 1. What scope means

**Scope** is simply the answer to "where in the program can this name be
used?" Python commonly describes name lookup with the **LEGB** model:
**L**ocal, **E**nclosing, **G**lobal, and **B**uilt-in. This lesson
focuses on the two that matter for everyday functions, Local and Global;
enclosing scopes (functions nested inside functions) can be covered
later:

- **Local scope**: the names created **inside** one function call. Those
  names are available only inside that function, and only while that call
  is running.
- **Global scope** (also called **module scope**): the names created
  **outside** every function, directly in the file. They exist for as
  long as the program keeps running, and can be *read* from almost
  anywhere in that file, including from inside a function.

Every time a function runs, it gets its own **fresh** local scope — even
if the same function is called five times, each call gets its own
separate set of local names, unconnected to any other call.

### 2. Local variables

A variable **created inside a function** belongs to that function's local
scope. It cannot normally be used outside it:

```python
def calculate_total(price, quantity):
    order_total = price * quantity
    print(order_total)

calculate_total(9.99, 3)
```

```text
29.97
```

`order_total` is created inside `calculate_total`, so it belongs to that
one function call. Trying to use it afterward, outside the function,
fails:

```text
calculate_total(9.99, 3)
print(order_total)
```

```text
NameError: name 'order_total' is not defined
```

Python raises `NameError` because, by the time that `print(order_total)`
line runs, the name `order_total` is no longer available anywhere Python can see —
it only ever belonged to `calculate_total`'s own local scope, which ended
the moment the function finished running. This is not a bug; it is
exactly what local scope means: a function's own working variables stay
private to that function.

### 3. Global variables

A variable created **outside** every function, directly in the file,
lives in global scope — and any function can **read** it, without doing
anything special:

```python
tax_rate = 0.08

def calculate_total_with_tax(price):
    return price * (1 + tax_rate)

print(calculate_total_with_tax(100))
print(tax_rate)
```

```text
108.0
0.08
```

`calculate_total_with_tax` never receives `tax_rate` as a parameter, yet
it reads it directly — Python looks for `tax_rate` inside the function
first, does not find it there, and then automatically checks the global
scope, where it does find it. **Reading a global does not require the
`global` statement, and it is common.** It is still a dependency on
module-level state that is not visible in the function's parameters, so
use it deliberately (for example, for a configuration value). What is
*not* the same thing, covered next, is **assigning** to a global
name from inside a function — that behaves very differently, and is the
source of nearly every scope-related bug in this lesson.

### 4. Local shadowing

If a function creates a **local** variable with the *same name* as a
global variable, the local one **shadows** — temporarily hides — the
global one, but only inside that one function:

```python
tax_rate = 0.08

def use_special_rate():
    tax_rate = 0.0
    print("Inside function:", tax_rate)

use_special_rate()
print("Outside function:", tax_rate)
```

```text
Inside function: 0.0
Outside function: 0.08
```

`tax_rate = 0.0` inside `use_special_rate` does **not** touch the global
`tax_rate` at all — it creates a brand-new *local* variable that just
happens to share the same name, visible only inside this one function.
Once the function ends, that local name `tax_rate` is no longer
available, and
the global `tax_rate`, printed afterward, is exactly as it always was:
`0.08`. This is a common source of beginner confusion — two variables
with an identical name, coexisting safely in two different scopes,
without ever interfering with each other.

### 5. Assignment and `UnboundLocalError`

Here is the rule that trips up almost every beginner at some point:
**if a function assigns to a name *anywhere* in its body, Python treats
that name as local for the *entire* function** — not just from the
assignment line onward, but from the very first line of the function.

```text
score = 0

def add_point():
    score = score + 1
    print(score)

add_point()
```

```text
UnboundLocalError: cannot access local variable 'score' where it is not associated with a value
```

This looks like it should simply read the global `score`, add `1`, and
print the result — but it does not. Because `add_point` contains
`score = score + 1`, Python decides, from the function's code, before it runs the function
body, that `score` is a **local** name for this whole function. That means the
right-hand side, `score + 1`, tries to **read** the local `score` —
before it has ever been assigned anything — which is exactly what
`UnboundLocalError` reports. This is a different error from `NameError`
for a reason: Python already knows `score` is *meant* to be local here;
it just is not usable yet.

**The safer solution: pass required values as parameters, and return new
values**, instead of reading and reassigning a global name at all:

```python
def add_point(score):
    return score + 1

current_score = 0
current_score = add_point(current_score)
current_score = add_point(current_score)

print(current_score)
```

```text
2
```

`add_point` now takes `score` as a **parameter** — an ordinary local
variable that is *given* a value the moment the function is called, so
there is no "read before assignment" problem at all. The caller decides
which global (or any other) variable to pass in, and what to do with the
returned result — the function itself never needs to know or care that
`current_score` happens to live in global scope.

### 6. The `global` keyword

Python does provide a way to let a function **assign** to a genuinely
global name: the **`global` keyword**, written as a single statement
naming the variable, before it is used:

```python
total_signups = 0

def register_user():
    global total_signups
    total_signups = total_signups + 1

register_user()
register_user()
print(total_signups)
```

```text
2
```

`global total_signups` tells Python, explicitly, "do not create a local
variable named `total_signups` — every use of that name in this function
refers to the global one." With that stated up front, `total_signups =
total_signups + 1` correctly reads and then updates the *global*
variable, and the change is visible everywhere, including after the
function returns.

**Why this should be rare in real programs:** a function that uses
`global` has a **hidden dependency** — you cannot tell what it does just
from its parameters and return value; you have to read its entire body
to discover that it secretly reads and changes something far away in the
file. As a program grows, several functions quietly relying on `global`
to share state becomes very difficult to reason about: any one of them
could have changed the shared value, in any order, and there is no
record of it in any function's signature. **This lesson explains `global`
so you can recognize and understand it — not as a design pattern you
should reach for.** The parameter-and-return-value pattern from Section 5
solves the same kind of problem far more safely, and should be your
default.

### 7. Mutable global state

Here is a subtlety that catches almost everyone at least once: a global
**list or dictionary** can be **mutated** from inside a function
**without** using `global` at all — because mutating an object is not
the same thing as assigning a new value to its name:

```python
shopping_cart = ["apples"]

def add_to_cart(item):
    shopping_cart.append(item)

add_to_cart("bread")
add_to_cart("milk")
print(shopping_cart)
```

```text
['apples', 'bread', 'milk']
```

`shopping_cart.append(item)` never assigns anything to the name
`shopping_cart` — it only reaches into the list `shopping_cart` already
refers to, and adds an item to it. Since there is no assignment to the
name `shopping_cart` anywhere in `add_to_cart`, Python never treats it
as local; it is simply *read* (found in global scope), and then mutated
through the ordinary list methods from
[Lists: Mutation, Copying, and Aliasing](../02-Python-Core-Language-and-Data-Types/05-lists-mutation-copying-and-aliasing.md).
No `global` statement was needed, because the *name* `shopping_cart` was
never reassigned — only the *list it refers to* was changed.

**Why this is risky:** this function has exactly the same "hidden
dependency" problem as `global` did in Section 6, but it is even easier
to miss, since there is no `global` keyword to spot while skimming the
code — a reader has to notice that `.append(...)` silently reaches
outside the function entirely. Any other function that also touches
`shopping_cart` could change it in ways this function never expects.

**The safer approach: pass the list in as a parameter, and return the
result:**

```python
def add_to_cart(cart, item):
    cart.append(item)
    return cart

shopping_cart = ["apples"]
shopping_cart = add_to_cart(shopping_cart, "bread")
shopping_cart = add_to_cart(shopping_cart, "milk")
print(shopping_cart)
```

```text
['apples', 'bread', 'milk']
```

The result is identical, but the function's dependency on `shopping_cart`
is now completely **visible** in its signature: `add_to_cart(cart, item)`
plainly states "I need a cart and an item, and I will hand back the
updated cart" — nothing about the file's global variables needs to be
inspected just to understand what this function touches.

### 8. Variable lifetime

**Scope** and **lifetime** are related but not identical. Scope is where
a *name* can be used; lifetime is how long the *object or value* that the
name referred to stays alive. A local name is created when its assignment
line runs and is no longer available once its function call finishes —
this is why Section 2's `order_total` could not be used afterward. What
happens to the value it referred to is a separate question.

```python
def build_profile(name):
    greeting = f"Welcome, {name}!"
    return greeting

message = build_profile("Ada")
print(message)
```

```text
Welcome, Ada!
```

`greeting` is a local name created fresh every time `build_profile` is
called. After the function returns, that local name is no longer
available through the function's local scope. But the **value** — the
text `"Welcome, Ada!"` — is still available, because `return greeting`
hands it to the caller, and `message` now refers to it. The local name is
gone, yet the value remains in use, which is why scope and lifetime should
not be treated as the same thing. (How Python eventually cleans up values
that nothing refers to is a separate topic you do not need for this
lesson. The useful beginner model is: **a value stays alive while it is
still referenced, or reachable, from somewhere in the program.**)

### 9. Safe engineering habits

The scope-related bugs in this lesson almost all come from the same root
cause: a function silently depending on, or changing, something outside
its own parameters. A short set of habits avoids nearly all of it:

- **Prefer parameters for inputs.** If a function needs a value, accept
  it as a parameter, rather than reading it from an outer scope.
- **Prefer return values for outputs.** If a function produces a result,
  `return` it, rather than assigning to (or mutating) something outside
  itself.
- **Avoid hidden dependencies.** A reader should be able to tell what a
  function needs and produces purely from its signature — not by reading
  its entire body.
- **Avoid unexpected mutation.** Do not mutate a list or dictionary that
  was not explicitly handed to the function as something it is expected
  to change.
- **Use clear names.** A parameter named `cart`, not `data` or `x`, tells
  a reader immediately what a function is working with.
- **Keep state ownership obvious.** For any given piece of data, there
  should be one clear place responsible for creating and updating it —
  not several functions each quietly reaching in from the outside.

## Examples

### Example 1 — Reading a global tax-rate configuration value

```python
tax_rate = 0.08

def calculate_total_with_tax(price, quantity):
    subtotal = price * quantity
    return subtotal * (1 + tax_rate)

order_total = calculate_total_with_tax(20, 3)
print(f"Order total with tax: ${order_total:.2f}")
print(f"Configured tax rate: {tax_rate}")
```

**Plain-English explanation:**

- `tax_rate` is a single, global configuration value, defined once at the
  top of the file — a realistic pattern for a setting that many parts of
  a program might need.
- `calculate_total_with_tax` never receives `tax_rate` as a parameter; it
  simply reads it from global scope, exactly as Section 3 described.
- Because the function only ever *reads* `tax_rate`, never assigns to it,
  there is no risk of `UnboundLocalError` here, and `tax_rate` remains
  completely unchanged after the call, as the final line confirms.

**Expected output:**

```text
Order total with tax: $64.80
Configured tax rate: 0.08
```

### Example 2 — Local shadowing with a practice score

```python
high_score = 100

def show_practice_score():
    high_score = 0
    print("Practice score starts at:", high_score)

show_practice_score()
print("Real high score is still:", high_score)
```

**Plain-English explanation:**

- `high_score = 100` is the real, global high score.
- Inside `show_practice_score`, `high_score = 0` creates a **local**
  variable that shadows the global one, only for the duration of this
  function call — exactly the pattern from Section 4.
- After the function returns, its local name `high_score` is no longer available;
  the global `high_score`, printed on the last line, is still `100`,
  completely unaffected by anything that happened inside the function.

**Expected output:**

```text
Practice score starts at: 0
Real high score is still: 100
```

### Example 3 — A score counter using parameters and return values

```python
def add_point(score):
    return score + 1

current_score = 0
current_score = add_point(current_score)
current_score = add_point(current_score)

print("Current score:", current_score)
```

**Plain-English explanation:**

- `add_point` takes the current score as a **parameter** and returns the
  new score — it never reads or assigns any global name at all.
- Each call to `add_point(current_score)` passes in whatever
  `current_score` currently holds, and the result is immediately stored
  back into `current_score` by the caller.
- This is the safe fix from Section 5: it produces the same running
  total a `global`-based counter would, without a hidden dependency and
  without any risk of `UnboundLocalError`.

**Expected output:**

```text
Current score: 2
```

### Example 4 — A shopping cart: risky mutation versus the safe pattern

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

**Plain-English explanation:**

- `add_to_cart_risky` reaches directly into the global `shopping_cart`
  and mutates it, exactly as Section 7 warned against — its signature,
  `add_to_cart_risky(item)`, gives no hint at all that it also depends on
  a global list.
- `add_to_cart_safe` instead accepts the cart as a parameter, mutates
  *that* list (whichever one was actually passed in), and returns it —
  its signature honestly states everything it needs and produces.
- Both versions produce the same final cart contents here, but only the
  second version's dependencies are visible without reading its body —
  the whole point of Section 7's safer approach.

**Expected output:**

```text
Risky version result: ['apples', 'bread']
Safe version result: ['apples', 'bread']
```

### Example 5 — Updating a user-profile dictionary safely

```python
def update_email(profile, new_email):
    profile["email"] = new_email
    return profile

user_profile = {"name": "Grace", "email": "old@example.com"}
user_profile = update_email(user_profile, "grace@example.com")

print(user_profile)
```

**Plain-English explanation:**

- `update_email` takes the dictionary to change, and the new value to
  put into it, as explicit parameters — exactly the same safe pattern
  from Example 4, now applied to a dictionary instead of a list.
- `profile["email"] = new_email` mutates the dictionary that was passed
  in, using the ordinary dictionary assignment from
  [Dictionaries and Lookups](../02-Python-Core-Language-and-Data-Types/07-dictionaries-and-lookups.md);
  `return profile` then hands the same, now-updated dictionary back.
- Nothing about this function depends on a global `user_profile` name at
  all — it would work identically no matter what the caller happened to
  name their dictionary.

**Expected output:**

```text
{'name': 'Grace', 'email': 'grace@example.com'}
```

### Example 6 — Passing and returning a balance across several calls

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

**Plain-English explanation:**

- `apply_deposit` takes the current balance and a deposit amount, and
  returns the new balance — it has no global state to depend on at all.
- `updated_balance` is a local variable that exists only for the
  duration of one call to `apply_deposit`; the moment the function
  returns, that particular local variable is gone — but its *value* lives
  on, because `account_balance` on the outside now refers to it, exactly
  as Section 8 described.
- The second call reuses the *already-updated* `account_balance` as its
  input, showing that this pattern chains correctly across as many calls
  as needed, entirely through parameters and return values, with no
  global variable ever being read or reassigned from inside the
  function.

**Expected output:**

```text
Balance after first deposit: 150
Balance after second deposit: 175
```

## Common beginner mistakes

- **Trying to use a function's local variable after the function has
  returned.** As Section 2 showed, this raises `NameError`, because that
  name never existed outside the function in the first place.
- **Assuming a variable assigned inside a function changes the global
  variable of the same name.** As Section 4 showed, this only creates a
  local variable that shadows the global one; the global value is
  completely unaffected.
- **Trying to read and update a global number with plain `score = score +
  1` inside a function, with no `global` statement and no parameter.**
  This raises `UnboundLocalError`, because assigning to `score` anywhere
  in the function makes Python treat it as local for the whole function
  body.
- **Reaching for `global` as a quick fix** instead of restructuring a
  function to accept a parameter and return a value — `global` works, but
  it hides a function's real dependencies from its signature.
- **Forgetting that mutating a global list or dictionary needs no
  `global` statement at all**, and being surprised that a function with
  no `global` keyword in sight still managed to change shared data.
- **Writing a function that silently depends on a global variable that
  might change later**, instead of accepting that value as a parameter,
  making the dependency explicit and the function easier to test on its
  own.

## Try it yourself

Do not look up full solutions. Predict the output before running each
one.

1. Write a function that creates a local variable, prints it inside the
   function, and then try to print that same variable name outside the
   function. Write down the type of error Python raises and why.
2. Create a global variable `discount_rate` and a function that reads it
   (without a parameter) to calculate a discounted price. Confirm the
   function works correctly, then confirm `discount_rate` is unchanged
   afterward.
3. Write a function that assigns to a global-sounding name without a
   `global` statement or a parameter (for example, `total = total + 1`)
   and observe the `UnboundLocalError` for yourself. Then fix it two
   ways: once using `global`, and once using a parameter and a return
   value.
4. Create a global list of `favorite_books` and write two versions of a
   function that adds a book to it: one that mutates the global list
   directly, and one that accepts the list as a parameter and returns
   the updated list. Compare their signatures and decide which one you
   would rather use in a larger program, and why.
5. Write a function `apply_interest(balance, rate)` that returns a new
   balance, and call it three times in a row, each time using the
   previous result as the next call's input, printing the balance after
   each call.

## Summary

- **Scope** is where a variable name can be used; **local scope** belongs
  to one function call, and **global (module) scope** belongs to the
  whole file.
- A local variable cannot be used outside the function that created it;
  trying to do so raises `NameError`.
- A function can freely **read** a global variable; this is completely
  different from **assigning** to one, which behaves in a special way
  inside a function.
- **Shadowing** happens when a local variable shares a global variable's
  name; the local one is used inside the function, and the global one is
  left completely unchanged.
- Assigning to a name *anywhere* inside a function makes Python treat it
  as local for the *entire* function; reading it before that assignment
  raises `UnboundLocalError`. The safer fix is to accept the value as a
  parameter and `return` the new value, instead of reading and
  reassigning a global name.
- The **`global`** keyword lets a function assign to a genuinely global
  name, but it creates a hidden dependency and should be rare — prefer
  parameters and return values instead.
- A global **list or dictionary** can be mutated from inside a function
  with no `global` statement at all, because mutating an object is not
  the same as reassigning its name; this is risky for the same reason
  `global` is, and the same parameter-and-return-value fix applies.
- A local **name** stops being available when its function call
  finishes, but the **value** it referred to can stay alive for as long
  as something else, such as a `return`ed result, still refers to it —
  scope and lifetime are related but not identical.

## Completion checklist

- [ ] I can explain, in my own words, the difference between local scope
      and global scope.
- [ ] I can explain why a local variable cannot be used outside its
      function, and read the resulting `NameError`.
- [ ] I can explain why reading a global variable inside a function is
      safe, and why assigning to one is different.
- [ ] I can demonstrate local shadowing and explain why the global value
      stays unchanged.
- [ ] I can explain why assigning to a name inside a function makes
      Python treat it as local for the whole function, and read the
      resulting `UnboundLocalError`.
- [ ] I can write one correct, small example using `global`, and explain
      why it should be rare in real programs.
- [ ] I can explain why a global list or dictionary can be mutated
      without `global`, and rewrite such a function to use a parameter
      and a return value instead.
- [ ] I can explain the difference between a local name's scope and a
      value's lifetime, and why a returned value can outlive the local
      name that first held it.
- [ ] I have completed the "try it yourself" exercises above.

## Connection to later Applied AI and Agentic AI engineering work

An AI agent typically has real, ongoing state: the conversation so far,
the results of tools it has already called, a running plan. The habits
from this lesson are exactly what keeps that state manageable as an
agent's code grows: passing the current state into a function as a
parameter and getting an updated version back, rather than having many
different functions silently reach into and mutate one big shared global
object, keeps every function's real dependencies visible and testable on
their own. A function that secretly mutates a global conversation history
or tool-result cache is precisely the kind of hidden dependency that
becomes very difficult to debug once an agent's logic spans many
functions — the parameter-and-return-value discipline you practiced here
is one of the most direct, practical defenses against that entire class
of bug.
