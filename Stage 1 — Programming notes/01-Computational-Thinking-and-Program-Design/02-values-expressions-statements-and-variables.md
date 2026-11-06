# Values, Expressions, Statements, and Variables

**Stage:** Stage 1 — Programming & Computational Thinking  
**Topic:** 02 — Values, Expressions, Statements, and Variables  
**Prerequisite:** Algorithms, Programs, and Data

## 1. Purpose of This Topic

This topic introduces four foundational Python concepts: values, expressions, statements, and variables. It also explains how variables can refer to different data at different times and the difference between reassignment and mutation.

After studying this topic, you should be able to:
- Identify values, expressions, statements, and variables in Python code.
- Explain assignment and why `=` is not mathematical equality.
- Explain the difference between reassignment and mutation.
- Predict the state of variables after a sequence of assignments.
- Understand that some objects are mutable while others are immutable.

## 2. Values

A **value** is a piece of data represented in a Python program.

```python
42
3.14
"hello"
True
[1, 2, 3]
```

Each value has a type:

| Value | Type | Meaning |
|---|---|---|
| `42` | `int` | An integer |
| `3.14` | `float` | A decimal number |
| `"hello"` | `str` | Text (a string) |
| `True` | `bool` | A Boolean value |
| `[1, 2, 3]` | `list` | A collection of items |

A value is the actual data that a program works with. In data engineering, values might represent a customer's age, a transaction amount, a product name, or a collection of records.

## 3. Expressions

An **expression** is a piece of Python code that is evaluated to produce a value.

```python
3 + 4
"a" + "b"
len("hello")
```

| Expression | Result |
|---|---|
| `3 + 4` | `7` |
| `"a" + "b"` | `"ab"` |
| `len("hello")` | `5` |

Even a literal value such as `42` is technically an expression: evaluating it produces `42`. Expressions can combine values, variables, operators, and function calls to produce a result.

## 4. Statements

A **statement** is a unit of Python code that performs an action or carries out an instruction.

```python
total = 3 + 4
print(total)
```

- `total = 3 + 4` evaluates the expression `3 + 4` and assigns its result to `total`.
- `print(total)` calls `print()` to display the value referred to by `total`.

An expression produces a value; a statement performs an instruction or action.

A bare expression in a normal Python script is evaluated, but its result is not automatically displayed or saved:

```python
3 + 4
```

By contrast:

```python
print(3 + 4)
```

displays:

```text
7
```

## 5. Variables and Assignment

A **variable** is a name that refers to an object or value.

```python
age = 25
```

- `age` is the variable name.
- `25` is the value.
- `=` is the assignment operator.

Read this as: “Assign the value 25 to the name `age`.” Do not read `=` as mathematical equality. In Python, `=` performs assignment. The equality comparison operator is `==`, which will be covered later.

```python
age = 25
age = 25
next_year_age = age + 1
print(next_year_age)
```

Output:

```text
26
```

The expression `age + 1` is evaluated first. Since `age` refers to `25`, the result is `26`, which is assigned to `next_year_age`.

**Important assignment rule:** Python evaluates the right-hand side first, then assigns the resulting value to the name on the left-hand side. For example, `age = age + 1` reads the current value of `age`, adds `1`, and assigns the new result back to `age`. This is why `=` is not mathematical equality.

## 6. Reassignment

**Reassignment** means making a variable name refer to a different object or value.

```python
score = 10
print(score)

score = 20
print(score)
```

Output:

```text
10
20
```

First, `score` refers to `10`. Then it is printed. Next, `score` is reassigned to refer to `20`, which is printed. The integer object `10` was not changed into `20`; the name `score` was reassigned.

A useful mental model is to think of a variable name as a label referring to an object. This is only a mental model: in Python, names refer to objects; they are not literal boxes that contain values.

## 7. Mutation

**Mutation** means changing an existing mutable object in place. Lists are mutable, so their contents can be changed after the list is created.

```python
scores = [10, 20, 30]
scores.append(40)
print(scores)
```

Output:

```text
[10, 20, 30, 40]
```

The `append()` method adds `40` to the existing list. The list object is changed in place. The variable `scores` has not been reassigned to a different list.

- **Reassignment:** a variable name is made to refer to a different object.
- **Mutation:** an existing mutable object is changed in place.

This distinction is especially important when more than one variable refers to the same mutable object.

## 8. Immutable Objects: Strings

Strings are immutable. An existing string object cannot be changed in place.

```python
name = "sam"
name.upper()
print(name)
```

Output:

```text
sam
```

The `.upper()` method returns a **new string** containing uppercase characters. It does not modify the original string. Here, the returned string is not assigned to a variable, so it is not retained.

To keep the uppercase result:

```python
name = name.upper()
print(name)
```

Output:

```text
SAM
```

Here, `name` is reassigned to refer to the new string `"SAM"`.

Remember:
- Strings and numbers are immutable.
- Lists are mutable.
- Some other Python data types are mutable; others are immutable.

## 9. Worked Examples from the Lesson

### Example 1 — Calculate a total cost

```python
price = 19.99
quantity = 3
total_cost = price * quantity
print(total_cost)
```

Output:

```text
59.97
```

Explanation:
1. `price` is assigned the float value `19.99`.
2. `quantity` is assigned the integer value `3`.
3. Python evaluates `price * quantity`.
4. The result, `59.97`, is assigned to `total_cost`.
5. `print(total_cost)` displays the result.

This example demonstrates values, variables, an arithmetic expression, assignment, and output.

### Example 2 — Update a running balance

```python
balance = 100
balance = balance - 30
balance = balance - 15
print(balance)
```

Output:

```text
55
```

Explanation:
1. Initially, `balance` is `100`.
2. Python evaluates `100 - 30`, producing `70`, and reassigns `balance` to `70`.
3. Python evaluates `70 - 15`, producing `55`, and reassigns `balance` to `55`.
4. `print(balance)` displays `55`.

The right-hand side is evaluated using the current value before assignment. `balance = balance - 30` is valid Python assignment; it is not a mathematical equality statement.

### Example 3 — Shared list references and reassignment

This example demonstrates mutation, shared references (also called aliasing), and reassignment.

```python
password_attempts = []

password_attempts.append("qwerty")
password_attempts.append("letmein")
print(password_attempts)          # ['qwerty', 'letmein']

backup_attempts = password_attempts
backup_attempts.append("hunter2")
print(password_attempts)          # ['qwerty', 'letmein', 'hunter2']

password_attempts = ["reset"]
print(password_attempts)          # ['reset']
print(backup_attempts)            # ['qwerty', 'letmein', 'hunter2']
```

Output:

```text
['qwerty', 'letmein']
['qwerty', 'letmein', 'hunter2']
['reset']
['qwerty', 'letmein', 'hunter2']
```

Explanation:
1. `password_attempts = []` creates an empty list.
2. The first two `append()` calls add `"qwerty"` and `"letmein"` to that list.
3. `backup_attempts = password_attempts` does **not** create a copy. Both names now refer to the same list object.
4. `backup_attempts.append("hunter2")` mutates that shared list. The change is visible through `password_attempts` too.
5. `password_attempts = ["reset"]` creates a new list and reassigns only `password_attempts` to it.
6. `backup_attempts` still refers to the original list, which contains the three earlier items.

Mutation changes the shared list object; reassignment changes what one variable name refers to.

**Security note:** The password-like strings in this teaching example are placeholders used to demonstrate list behaviour. This is not a secure way to store passwords.

To create a separate outer list rather than another name for the same list, use either:

```python
variable_2 = variable_1.copy()
```

or:

```python
variable_2 = list(variable_1)
```

These create a shallow copy. If the list contains other mutable objects, those nested objects may still be shared between the original and copied lists.

## 10. Common Beginner Mistakes

### Mistake 1 — Reading `=` as mathematical equality

```python
x = x + 1
```

This is not an equation claiming that `x` equals `x + 1`. Python evaluates the current value of `x`, adds `1`, and assigns the result back to `x`.

### Mistake 2 — Assuming assignment copies a mutable object

```python
variable_2 = variable_1
```

If `variable_1` refers to a list, this does not create a new list. Both names refer to the same list object. Use `variable_1.copy()` or `list(variable_1)` to create a shallow copy of the outer list. Nested mutable objects are still shared in a shallow copy.

### Mistake 3 — Expecting `.upper()` to modify the original string

Strings are immutable. `name.upper()` returns a new uppercase string but does not change `name`. To retain the result:

```python
name = name.upper()
```

### Mistake 4 — Forgetting that the right-hand side is evaluated first

In:

```python
balance = balance - 30
```

Python first evaluates `balance - 30` using the current value of `balance`. It then assigns the result to `balance`.

## 11. Original Lesson Exercises

### Exercise 1

```python
x = 5
y = x
x = x + 10
print(x, y)
```

Predict the output and explain why `y` did or did not change. Success means the output matches and you can explain that `x` was reassigned while `y` retained its original value.

### Exercise 2

Create `cart = []`; append three grocery names; assign `also_cart = cart`; append one more item through `also_cart`; print both. Predict the result and explain why both names show the same four items.

### Exercise 3

Use four lines of Python: set `steps_taken = 0`, increment it by 1,000 twice using reassignment (not mutation), and print it. Predict the output.

### Exercise 4

```python
name = "ada"
shout_name = name.upper()
name = "grace"
print(name, shout_name)
```

Predict the output and explain why `shout_name` does not change.

---

# Complete Exercise Solutions and Explanations

The following walkthroughs solve all four exercises from the lesson. Each solution includes the code, line-by-line execution, variable states, and the correct output.

## Exercise 1 — Assignment and reassignment

**Question:** Predict the output. Explain why `y` does or does not change when `x` is reassigned.

### Complete code

```python
x = 5
y = x
x = x + 10
print(x, y)
```

### Step 1 — First assignment

```python
x = 5
```

Python assigns the integer value `5` to `x`.

| Variable | Value |
|---|---:|
| `x` | 5 |

### Step 2 — Assign the value of `x` to `y`

```python
y = x
```

Python evaluates the right-hand side. The current value of `x` is `5`, so `y` is also assigned the integer value `5`.

| Variable | Value |
|---|---:|
| `x` | 5 |
| `y` | 5 |

### Step 3 — Reassign `x`

```python
x = x + 10
```

Python first evaluates the right-hand side:

```python
5 + 10
```

The result is `15`. Python then assigns `15` to `x`.

| Variable | Value |
|---|---:|
| `x` | 15 |
| `y` | 5 |

`y` remains `5`. Reassigning `x` does not reassign `y`.

### Step 4 — Print the values

```python
print(x, y)
```

**Correct output:**

```text
15 5
```

**What this exercise teaches:** Assignment and reassignment affect the variable name on the left-hand side. Reassigning one variable does not automatically change another variable.

## Exercise 2 — Mutation and shared lists

**Question:** Create a grocery cart, add three items, assign another variable to the same cart, add another item through the second variable, and print both variables.

### Complete Python code

```python
cart = []

cart.append("Milk")
cart.append("Bread")
cart.append("Eggs")

also_cart = cart

also_cart.append("Rice")

print(cart)
print(also_cart)
```

### Step 1 — Create an empty list

```python
cart = []
```

This creates an empty list and assigns it to `cart`.

### Step 2 — Add three grocery items

```python
cart.append("Milk")
cart.append("Bread")
cart.append("Eggs")
```

The `append()` method adds each item to the existing list. The list now contains:

```python
["Milk", "Bread", "Eggs"]
```

### Step 3 — Assign another name to the same list

```python
also_cart = cart
```

This does not create a new list. Both variable names refer to the same list object.

Conceptual representation:

```text
             One shared list object
          ["Milk", "Bread", "Eggs"]
                    /       \
                   /         \
                cart       also_cart
```

### Step 4 — Mutate the shared list through `also_cart`

```python
also_cart.append("Rice")
```

This adds `"Rice"` to the shared list. Because both names refer to that same list, the change is visible through both names.

### Step 5 — Print both variables

```python
print(cart)
print(also_cart)
```

**Correct output:**

```text
['Milk', 'Bread', 'Eggs', 'Rice']
['Milk', 'Bread', 'Eggs', 'Rice']
```

**What this exercise teaches:** This behaviour is called a shared reference or aliasing. When two variables refer to the same mutable list, a mutation made through one variable is visible through the other.

## Exercise 3 — Reassignment and running totals

**Question:** Start with zero steps, increase the count by 1,000 twice using reassignment (not mutation), and print the result.

### Complete Python code

```python
steps_taken = 0

steps_taken = steps_taken + 1000

steps_taken = steps_taken + 1000

print(steps_taken)
```

### Step 1 — Set the initial value

```python
steps_taken = 0
```

Initial state:

| Variable | Value |
|---|---:|
| `steps_taken` | 0 |

### Step 2 — Add the first 1,000 steps

```python
steps_taken = steps_taken + 1000
```

Python evaluates:

```text
0 + 1000 = 1000
```

It assigns the result back to `steps_taken`. New value: `1000`.

### Step 3 — Add another 1,000 steps

```python
steps_taken = steps_taken + 1000
```

Python now evaluates:

```text
1000 + 1000 = 2000
```

It assigns the result back to `steps_taken`. New value: `2000`.

### Step 4 — Print the total

```python
print(steps_taken)
```

**Correct output:**

```text
2000
```

### Variable state table

| Execution point | `steps_taken` |
|---|---:|
| Initial assignment | 0 |
| After first addition | 1,000 |
| After second addition | 2,000 |

**What this exercise teaches:** This is a running total. Python reads the current value, calculates a new value, and reassigns the variable. This pattern is useful when calculating total expenses, revenue, records processed, or transaction amounts in data engineering.

## Exercise 4 — String immutability and reassignment

**Question:** Predict the output. Explain why `shout_name` does not change when `name` is reassigned.

### Complete Python code

```python
name = "ada"

shout_name = name.upper()

name = "grace"

print(name, shout_name)
```

### Step 1 — Assign the original string

```python
name = "ada"
```

The variable `name` refers to the string `"ada"`.

### Step 2 — Convert the name to uppercase

```python
shout_name = name.upper()
```

The `.upper()` method returns a new uppercase string. Python evaluates:

```python
"ada".upper()
```

Result:

```python
"ADA"
```

The new string is assigned to `shout_name`.

| Variable | Value |
|---|---|
| `name` | `"ada"` |
| `shout_name` | `"ADA"` |

### Step 3 — Reassign `name`

```python
name = "grace"
```

Python reassigns `name` to refer to the new string `"grace"`. It does not change `shout_name`.

| Variable | Value |
|---|---|
| `name` | `"grace"` |
| `shout_name` | `"ADA"` |

### Step 4 — Print both variables

```python
print(name, shout_name)
```

**Correct output:**

```text
grace ADA
```

**What this exercise teaches:**
- Strings are immutable in Python.
- `.upper()` returns a new string; it does not modify the original string.
- `shout_name` refers to the result `"ADA"`.
- Reassigning `name` does not change `shout_name`.

## Complete Exercise Review

| Exercise | Main concept | Correct result |
|---|---|---|
| 1 | Assignment and reassignment | `15 5` |
| 2 | Mutation and shared references | Both lists contain four items |
| 3 | Running total and reassignment | `2000` |
| 4 | String immutability | `grace ADA` |

---

## 12. Topic Summary and Completion Checklist

| Concept | Meaning |
|---|---|
| Value | The data represented in Python, such as `42`, `"hello"`, or `[1, 2, 3]`. |
| Expression | Code that is evaluated to produce a value, such as `3 + 4`. |
| Statement | A unit of code that performs an instruction or action, such as an assignment or `print()` call. |
| Variable | A name that refers to an object. |
| Assignment | Connecting a name to a value or object using `=`. |
| Reassignment | Making a variable name refer to a different object. |
| Mutation | Changing an existing mutable object in place. |
| Immutable object | An object that cannot be changed in place, such as a string. |
| Shared reference / aliasing | Two or more variable names referring to the same object. |

### Key points to remember

- A value is data.
- An expression produces a value when evaluated.
- A statement performs an instruction or action.
- A variable is a name that refers to an object.
- Assignment uses `=`, which is not the same as mathematical equality.
- Reassignment changes what a name refers to; it does not mutate the old object.
- Mutation changes an existing mutable object in place.
- Two names can refer to the same mutable object.
- A mutation through one of those names is visible through the other.
- Reassigning one name does not automatically reassign another name.
- Strings are immutable; methods such as `.upper()` return a new string.

### Completion checklist

- [ ] Identify a value, expression, statement, and variable in a short Python program.
- [ ] Explain why `=` means assignment rather than equality.
- [ ] Explain what happens when a variable is reassigned.
- [ ] Predict what happens when a shared list is mutated.
- [ ] Predict the result of string operations such as `.upper()`.
- [ ] Complete all four exercises and explain your reasoning aloud.

## 13. Why These Concepts Matter in Data Engineering and AI

These concepts are not limited to beginner exercises. They are important when building real software systems.

Data engineering and AI applications often maintain lists, dictionaries, conversation histories, tool results, shopping carts, document collections, and other application state.

For example, an AI agent may maintain a conversation history in a list. If two parts of the application unintentionally refer to the same mutable list, a change made by one part may affect the other. This can cause unexpected behaviour and difficult-to-debug state problems.

Understanding assignment, reassignment, mutation, immutability, and shared references helps engineers reason about how application state changes and prevents accidental changes to shared data.

---

**End of Topic 02 — Values, Expressions, Statements, and Variables**
