# Pure Functions and Side Effects

## Why pure functions and side effects matter

Two functions can compute the exact same number and still be completely
different to work with. One might always give the same answer for the
same input, touch nothing outside itself, and hand its result back
cleanly. The other might quietly depend on a value defined somewhere
else in the file, change a list the caller did not expect to be changed,
or only ever print its answer instead of returning it. The first kind of
function is easy to test, easy to reuse, and easy to reason about in
isolation. The second kind works fine in small programs, but becomes a
real source of confusing bugs the moment a program grows. This lesson
gives you the vocabulary and the habits to tell these two kinds of
functions apart, and to default to the safer one whenever you can.

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain what a **pure function** is, using all four of its defining
  properties.
- Explain what a **side effect** is, list several common kinds, and
  explain why a side effect is not automatically bad.
- Compare a pure and an impure function that compute the same result,
  and explain why the pure one is easier to predict and test.
- Explain why mutating a list, dictionary, or set passed into a function
  is a side effect, and write a safer function that returns a new
  collection instead.
- Explain why a function that only `print()`s its result is harder to
  reuse than one that `return`s it.
- Separate a pure calculation from the `print()` statements that display
  its result.
- Find a function with a hidden dependency on a global value, and
  refactor it to take that value as an explicit parameter.
- List practical design rules for deciding when a side effect is
  appropriate, and how to keep it clearly labeled and contained.

## Prerequisites

- [Functions, Parameters, and Return Values](03-functions-parameters-and-return-values.md) —
  this lesson assumes functions, parameters, and `return` are already
  comfortable.
- [Scope, Lifetime, and Global State](05-scope-lifetime-and-global-state.md) —
  the hidden-dependency section of this lesson directly reuses the
  global-variable ideas taught there.
- [Lists: Mutation, Copying, and Aliasing](../02-Python-Core-Language-and-Data-Types/05-lists-mutation-copying-and-aliasing.md) —
  the mutation examples in this lesson rely on aliasing and `.copy()`,
  both taught fully there.

## Key terms

| Term | Plain-English definition |
|---|---|
| **Pure function** | A function that always gives the same output for the same input, changes nothing outside itself, and hands its result back with `return`. |
| **Side effect** | Anything a function does besides computing and returning a value — such as printing, changing a collection it was given, or changing global state. |
| **Impure function** | A function that has at least one side effect, or whose result can depend on something other than its own arguments. |
| **Mutation** | Changing a mutable object (a list, dictionary, or set) in place, rather than building a new one. |
| **Hidden dependency** | A value a function relies on that does not appear anywhere in its parameter list, such as a global variable. |
| **Business logic** | The part of a program that performs calculations and decisions, independent of how results are eventually shown to a user. |
| **Presentation** | The part of a program responsible for displaying or formatting results, such as `print()` statements. |

## Step-by-step explanation

### 1. What a pure function is

A **pure function** has four properties, all at once:

- **The same input always produces the same output.** Call it twice with
  the same arguments, and you always get the identical result back.
- **It does not change data outside itself.** It never mutates a list,
  dictionary, or set that was handed to it, and never changes anything
  in global scope.
- **It does not depend on hidden state.** Its result is computed
  entirely from its parameters — never from a global variable, and never
  from anything that might be different the next time it runs.
- **It returns a result, rather than only printing it,** so the rest of
  the program can actually use that result.

```python
def calculate_discounted_price(price, discount_rate):
    return price * (1 - discount_rate)

print(calculate_discounted_price(100, 0.20))
print(calculate_discounted_price(100, 0.20))
print(calculate_discounted_price(50, 0.10))
```

```text
80.0
80.0
45.0
```

`calculate_discounted_price` is pure: calling it twice with `(100, 0.20)`
gives `80.0` both times, it never touches anything besides its own two
parameters, and it hands its answer back with `return` for the caller to
use however it likes.

### 2. What a side effect is

A **side effect** is anything a function does besides computing and
returning a value. Common side effects include:

- **Printing text.** `print(...)` shows something on the screen — a real
  effect on the outside world, separate from any value the function
  might also return.
- **Changing a list, dictionary, or set passed into a function.**
  Mutating a collection the caller handed over changes something the
  caller can still see afterward.
- **Changing global state.** Assigning to a global name (using `global`,
  as covered in
  [Scope, Lifetime, and Global State](05-scope-lifetime-and-global-state.md))
  changes something visible to the rest of the program.
- **Reading input, or changing something outside the program**, such as
  asking the user to type something, or writing to a file. This lesson
  only covers this conceptually — real file and input/output handling
  comes in a later module — but it is worth knowing now that these also
  count as side effects, for exactly the same reason: they reach outside
  the function.

```python
def report_discounted_price(price, discount_rate):
    discounted = price * (1 - discount_rate)
    print(f"Discounted price: ${discounted:.2f}")

report_discounted_price(100, 0.20)
```

```text
Discounted price: $80.00
```

`report_discounted_price` has a side effect: it prints text to the
screen. It never returns anything usable (it gives back `None`, as every
function with no `return` does), so nothing about its result can be
reused elsewhere in the program.

**Side effects are not automatically bad.** A program that never prints
anything, never saves anything, and never changes anything would be
completely useless — side effects are how a program actually *does*
something a person can see or benefit from. The goal of this lesson is
not to eliminate side effects, but to make them **intentional** —
something you chose on purpose — and **isolated**, meaning kept in a
small, clearly identified part of the program, rather than scattered
throughout ordinary calculation code.

### 3. Pure versus impure functions

Compare two functions that calculate the exact same thing — adding tax to
a price — one pure, one depending on a hidden global value:

```python
tax_rate = 0.08

def add_tax_impure(price):
    return price * (1 + tax_rate)

def add_tax_pure(price, tax_rate):
    return price * (1 + tax_rate)

print(add_tax_impure(100))
print(add_tax_pure(100, 0.08))
```

```text
108.0
108.0
```

Both give the identical answer here — but they are not equally
trustworthy. `add_tax_impure` silently reads the *global* `tax_rate`; its
result depends on something that is not visible anywhere in its call,
`add_tax_impure(100)`. `add_tax_pure` takes `tax_rate` as a parameter, so
every value it depends on is right there in the call itself.

**Watch what happens if the global value changes elsewhere in the
program:**

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

```text
108.00
115.00
108.00
```

`add_tax_impure(100)` gives a **different answer** the second time,
purely because something *else*, far away in the file, changed
`tax_rate` in between the two calls — the call itself looks completely
unchanged. `add_tax_pure(100, 0.08)` gives the same answer both times,
because every one of its inputs is stated directly in the call — nothing
about it can be affected by code elsewhere in the file. **This is exactly
why a pure function is easier to predict and test:** you can look at one
call, in isolation, and know its result with total confidence, without
needing to know anything else about the rest of the program.

### 4. Mutation as a side effect

Changing a list, dictionary, or set that was passed into a function is a
side effect, because it changes something the caller can still see after
the call returns:

```python
def add_to_receipt(receipt, item):
    receipt.append(item)

receipt_items = ["apples"]
add_to_receipt(receipt_items, "bread")
print(receipt_items)
```

```text
['apples', 'bread']
```

`add_to_receipt` never returns anything useful, but it still visibly
changes `receipt_items`, because `receipt` inside the function and
`receipt_items` outside it are two names for the exact same list — the
**aliasing** behavior first taught in
[Lists: Mutation, Copying, and Aliasing](../02-Python-Core-Language-and-Data-Types/05-lists-mutation-copying-and-aliasing.md).
This might be exactly what you want sometimes, but it is still a side
effect worth naming clearly, since a caller could easily forget that
`add_to_receipt` changes the list they handed it.

**A safer alternative builds and returns a new collection**, using
`.copy()` (also from Module 1.2) so the original is never touched at
all — Section 8's Example 5 shows this pattern applied to a real
shopping cart in full.

### 5. Printing versus returning

A function that only `print()`s its result cannot be reused by the rest
of the program, because nothing was ever handed back for other code to
work with:

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

```text
29.97
Final amount: $34.97
```

`calculate_total_prints` only ever displays its answer — there is no way
to add shipping to it afterward, because its result was never captured
anywhere; it simply appeared on the screen and was gone.
`calculate_total_returns` hands its answer back as a real value, which
`order_total` stores, letting the rest of the program decide what to do
with it next — here, adding `shipping` and printing a different, final
message. **Returning a value lets the caller decide whether to print it,
store it, pass it to another function, or all three** — printing inside
the function itself removes that choice entirely.

### 6. Separating calculation from presentation

A clean way to apply everything so far is to keep a **pure calculation
function** completely separate from the `print()` statements that
eventually display its result:

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

```text
Order total: $23.75
```

`calculate_order_total` is pure: given the same list of prices, it always
returns the same total, and it never prints anything itself. The
`print(...)` line is written separately, outside the function, and is
the *only* part of this program that touches the screen at all. This is
a simple but powerful boundary: **business logic** (the calculation)
lives in one place, and **presentation** (deciding how to show the
result to a person) lives in another. If you later needed to show the
total in a different format, save it somewhere, or use it in a further
calculation, `calculate_order_total` would not need to change at all —
only the presentation code would.

### 7. Hidden dependencies

A **hidden dependency** is a value a function relies on that never
appears in its parameter list — usually a global variable, exactly as
covered in
[Scope, Lifetime, and Global State](05-scope-lifetime-and-global-state.md):

```python
shipping_fee = 5

def calculate_final_amount(order_total):
    return order_total + shipping_fee

print(calculate_final_amount(50))
```

```text
55
```

Nothing about the call `calculate_final_amount(50)` reveals that this
function also depends on `shipping_fee` — you would have to read the
function's entire body to discover that. **The fix is to make the
dependency explicit, as a parameter:**

```python
def calculate_final_amount(order_total, shipping_fee):
    return order_total + shipping_fee

shipping_fee = 5
print(calculate_final_amount(50, shipping_fee))
```

```text
55
```

The result is identical, but now `calculate_final_amount(order_total,
shipping_fee)` states, directly in its signature, everything it needs.
**Why explicit inputs make code safer:** a reader — or a future version
of you — can understand and test this function completely on its own,
without needing to know that a variable named `shipping_fee` happens to
exist somewhere else in the file, or trust that it still holds the value
you expect it to.

### 8. Practical design rules

Pulling this lesson together into habits you can apply immediately:

- **Prefer pure functions for calculations, validation, and
  transformations.** Anything that turns some input into an answer —
  totals, discounts, grades, cleaned data — is a strong candidate for a
  pure function.
- **Keep side effects near the edges of the program.** Printing,
  reading input, and saving data belong in a thin layer that calls your
  pure functions and does something with their results — not scattered
  throughout your calculation logic.
- **Use descriptive names for functions that intentionally mutate.** A
  name like `add_item_to_cart` openly announces that it changes a cart;
  compare this with a vaguely named function that mutates its argument
  as a surprise.
- **Test whether input data changed when it should not have.** After
  calling a function you expect to be pure, check that the collection
  you passed in still looks the way it did before the call — Section 4
  and the Examples below show exactly how to verify this.
- **Document unavoidable side effects clearly.** If a function must
  print, mutate, or depend on global state, say so plainly — in its name,
  or in a short comment or docstring — so nobody has to discover it by
  accident.

## Examples

### Example 1 — Calculating a discount: pure versus impure

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

**Plain-English explanation:**

- `calculate_discount_impure` **has two side effects**: it reads the
  global `discount_rate` (a hidden dependency) and it prints its result
  instead of returning it. Its signature, `calculate_discount_impure(price)`,
  gives no hint of either.
- `calculate_discount_pure` **is pure**: `discount_rate` is an explicit
  parameter, and the function only computes and returns a value — the
  `print(...)` line for it happens completely separately, outside the
  function.
- Both print the identical text here, but only the pure version's result
  could be stored, reused in a further calculation, or tested in
  isolation without capturing printed output.

**Expected output:**

```text
Discounted: $80.00
Discounted: $80.00
```

### Example 2 — Converting scores to grades: a pure transformation

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

**Plain-English explanation:**

- `convert_score_to_grade` **is pure**: for any given `score`, it always
  returns the same letter grade, it reads nothing outside its one
  parameter, and it changes nothing.
- The `for` loop calls this pure function once per score, and handles
  all of the printing itself, outside the function — the same
  calculation-versus-presentation boundary from Section 6.
- Because the function is pure, you could call
  `convert_score_to_grade(82)` anywhere in the program, at any time, and
  trust it to always report `"B"` — a strong guarantee an impure version
  reading some global grading scale could not offer.

**Expected output:**

```text
95 -> A
82 -> B
68 -> F
74 -> C
```

### Example 3 — Adding tax and printing a spending report separately

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

**Plain-English explanation:**

- `add_tax` and `calculate_order_total` **are both pure**: `add_tax`
  takes the price and tax rate as parameters and returns a new number;
  `calculate_order_total` takes the list of prices and the tax rate,
  calls `add_tax` internally, and returns the final total — neither
  function prints anything or depends on a global value.
- Every `print(...)` line comes afterward, entirely separate from the
  calculation — this is the "spending report" pattern from the
  practical-examples list, and it is exactly Section 6's
  business-logic/presentation boundary applied to a small, realistic
  report.
- If you needed to show this report differently later — as a single
  line, or with a different currency symbol — only the `print(...)`
  lines would need to change; `add_tax` and `calculate_order_total`
  would stay exactly as they are.

**Expected output:**

```text
Spending report
--------------------
Items purchased: 3
Total with tax: $25.65
```

### Example 4 — Safely creating a cleaned list of names

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

**Plain-English explanation:**

- `clean_names_unsafe` **has a mutation side effect**: it overwrites each
  position of the *same* list it was given, using index assignment, so
  the caller's original list is permanently changed — printing
  `signup_names` afterward shows it already cleaned, which may well be a
  surprise if the caller expected their original data to survive.
- `clean_names_safe` **is pure**: it builds a brand-new list,
  `cleaned_names`, and appends a cleaned version of each name into it,
  never touching the list it was given at all. Printing
  `signup_names_again` afterward proves the original list is completely
  untouched, still in its messy, original form.
- This is the direct, worked example of Section 4's "safer alternative,"
  and the specific side-by-side contrast this lesson is built around:
  the *only* difference between the two functions is whether they mutate
  their input or build a new result — and that one difference completely
  changes what a caller can safely assume about their own data
  afterward.

**Expected output:**

```text
After unsafe cleaning, original list: ['Ada', 'Grace', 'Alan']
After safe cleaning, original list: ['  ada', 'GRACE  ', 'alan']
Safe cleaned result: ['Ada', 'Grace', 'Alan']
```

### Example 5 — A shopping cart: mutated accidentally versus handled safely

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

**Plain-English explanation:**

- `add_item_to_cart_hidden` **has a mutation side effect** that is easy
  to miss: its name gives no warning that it changes `saved_cart`
  directly — a caller holding onto `saved_cart` elsewhere in the program
  could easily be surprised that it now contains `"bread"` too.
- `add_item_to_cart` **is pure**: `cart.copy()` (from
  [Lists: Mutation, Copying, and Aliasing](../02-Python-Core-Language-and-Data-Types/05-lists-mutation-copying-and-aliasing.md))
  builds a genuinely independent list first, appends the new item to
  *that* copy, and returns it — `original_cart` is left completely
  untouched, confirmed by printing it afterward.
- Notice that even the pure version's name, `add_item_to_cart`, still
  clearly describes a mutation-flavored action — Section 8's advice to
  "use descriptive names for functions that intentionally mutate" is
  really about the *hidden* version here; a function that returns a new,
  updated cart instead of mutating one in place is safer precisely
  because it does not silently change data the caller still expects to
  be original.

**Expected output:**

```text
Cart after hidden mutation: ['apples', 'bread']
Original cart untouched: ['apples']
New cart: ['apples', 'bread']
```

### Example 6 — A capstone receipt: pure calculations, separated printing

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

**Plain-English explanation:**

- All three calculation functions — `calculate_order_total`, `add_tax`,
  and `add_shipping` — **are pure**: each takes exactly the values it
  needs as parameters, and returns a new number, with no printing and no
  hidden dependencies anywhere among them.
- The three calculations are **chained** together: each function's
  return value becomes the next function's input, building up the final
  receipt amount step by step, entirely through parameters and return
  values.
- Every `print(...)` line comes only at the very end, once every number
  needed for the report has already been calculated — this is the same
  business-logic/presentation boundary from Section 6 and Example 3, now
  applied across three cooperating pure functions instead of just one.

**Expected output:**

```text
Final Receipt
--------------------
Subtotal: $67.49
With tax: $72.89
Final amount: $78.89
```

## Common beginner mistakes

- **Assuming a side effect is always a mistake.** Side effects are
  necessary — a program needs to print, save, or display something
  eventually. The mistake is being *unintentional* about them, not
  having them at all.
- **Writing a function that both mutates its input and returns a value**,
  leaving a reader unsure which one they are actually supposed to use —
  pick one clear behavior per function.
- **Assuming a function is pure just because it has a `return`
  statement.** A function can `return` a value *and* still print, mutate
  an argument, or read a global variable — check all four properties
  from Section 1, not just whether `return` appears.
- **Forgetting that mutating a list changes it for every name that
  refers to it**, not just inside the function — this is the aliasing
  behavior from Module 1.2, and it applies here exactly as it did there.
- **Reaching for a global variable inside a calculation function**
  instead of adding an explicit parameter, creating a hidden dependency
  that makes the function harder to test and reuse.
- **Mixing calculation and printing inside the same function**, making
  it impossible to reuse the calculation without also triggering the
  printing, or to change the output format without touching the
  calculation logic.

## Try it yourself

Do not look up full solutions. Predict the output before running each
one.

1. Write a pure function `calculate_area(width, height)` and an impure
   version that reads `width` and `height` from global variables instead.
   Change the global values between two calls to the impure version and
   observe how its result silently changes.
2. Write a function `remove_duplicates_unsafe(numbers)` that mutates its
   input list in place to remove duplicates (hint: you may need to build
   a new list internally and then copy the values back), and a pure
   version, `remove_duplicates_safe(numbers)`, that returns a brand-new
   list instead. Confirm, by printing the original list afterward, which
   version leaves the caller's data untouched.
3. Take a function that only `print()`s a formatted price, and rewrite it
   to `return` the formatted text instead. Then write two different
   lines of code that each use the returned value differently (for
   example, printing it, and combining it with other text).
4. Write a pure function `is_valid_score(score)` that returns `True` or
   `False`, and keep every `print(...)` statement about it completely
   separate, in a loop that calls the function and reports the result
   for several scores.
5. Find (or write) a function that mutates a dictionary it was given,
   name it clearly to reflect that (for example, `apply_discount_to_profile`),
   and then write a second, pure version that returns a new dictionary
   instead, using `.copy()` from Module 1.2.

## Summary

- A **pure function** always gives the same output for the same input,
  changes nothing outside itself, depends on nothing hidden, and returns
  its result.
- A **side effect** is anything else a function does — printing,
  mutating a collection it was given, or changing global state; side
  effects are necessary in real programs, but should be intentional and
  isolated, not scattered through calculation code.
- Comparing a pure and an impure version of the same calculation shows
  why the pure one is easier to predict: its result can never silently
  change because of something happening elsewhere in the file.
- **Mutating** a list, dictionary, or set passed into a function is a
  side effect; building and returning a new collection instead — often
  using `.copy()` — avoids surprising the caller, exactly as Module 1.2's
  aliasing lesson would predict.
- A function that only `print()`s its result cannot be reused; a function
  that `return`s its result lets the caller decide whether to print,
  store, or reuse it.
- Separating **business logic** (pure calculation) from **presentation**
  (`print()` statements) keeps a program's calculation code reusable and
  its output format easy to change independently.
- A **hidden dependency** on a global value should be replaced with an
  explicit parameter, so a function's real requirements are visible in
  its signature.
- Prefer pure functions for calculations and transformations, keep side
  effects near the edges of a program, name mutating functions clearly,
  and check whether input data changed when it should not have.

## Completion checklist

- [ ] I can list all four properties of a pure function.
- [ ] I can list several kinds of side effects and explain why a side
      effect is not automatically a mistake.
- [ ] I can compare a pure and an impure version of the same calculation
      and explain why the pure one is easier to predict and test.
- [ ] I can explain why mutating a collection passed into a function is a
      side effect, and write a pure alternative that returns a new
      collection instead.
- [ ] I can explain why a function that only prints its result is harder
      to reuse than one that returns it.
- [ ] I can separate a pure calculation function from the `print()`
      statements that display its result.
- [ ] I can find a hidden dependency on a global value and refactor it
      into an explicit parameter.
- [ ] I can list the practical design rules from Section 8 from memory.
- [ ] I have completed the "try it yourself" exercises above.

## Connection to later Applied AI and Agentic AI engineering work

The purer you can keep an AI system's calculation and decision logic, the
easier that system is to test, debug, and trust — exactly the same
reasoning you practiced here applies directly to scoring a model's
output, validating a tool's arguments, or deciding whether a retrieved
document is relevant. Side effects still matter enormously in this kind
of system — calling an external tool, logging a decision, or updating a
conversation's state are all necessary side effects — but the same
discipline applies: keep them intentional and clearly separated from the
pure logic that decides *what* should happen, so that logic can be
tested and reasoned about without needing to trigger any of those
real-world effects. A tool function that mutates shared state instead of
returning a clear result is exactly the kind of hidden dependency that
becomes very difficult to trust once several parts of an agent are
calling it.
