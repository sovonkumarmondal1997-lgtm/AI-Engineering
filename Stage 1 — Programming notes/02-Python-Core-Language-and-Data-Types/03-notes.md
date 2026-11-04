# Lesson 03: Python Operators and Precedence

**Complete lesson summary** · Beginner level

This lesson teaches you how Python performs calculations, compares values, makes decisions, checks conditions, and determines which operation should execute first.

The central concept: Operators allow Python to perform calculations and make decisions by evaluating expressions that produce results, often `True` or `False`.

---

## 1. What are operators and operands?

- **Operator:** A symbol or keyword that performs an operation.
- **Operand:** The value on which an operator works.

Example:

```python
result = 3 + 4
```

Here, `+` is the operator, `3` and `4` are operands, and the result is `7`.

---

## 2. Arithmetic operators

These operators perform mathematical calculations.

| Operator | Meaning | Example | Result |
|---|---|---|---|
| `+` | Addition | `3 + 4` | `7` |
| `-` | Subtraction | `10 - 3` | `7` |
| `*` | Multiplication | `6 * 7` | `42` |
| `/` | Division | `7 / 2` | `3.5` |
| `//` | Floor division | `7 // 2` | `3` |
| `%` | Modulo (remainder) | `7 % 2` | `1` |
| `**` | Exponentiation | `2 ** 3` | `8` |

Understand these three carefully:

- `/` performs normal division and returns a float for integer operands.
- `//` divides and rounds down towards negative infinity.
- `%` returns the remainder.

Example:

```python
total_items = 23
box_size = 4

full_boxes = total_items // box_size
leftover_items = total_items % box_size

print(full_boxes)       # 5
print(leftover_items)   # 3
```

Five complete boxes can be filled, with three items remaining.

**Important:** `-7 // 2` produces `-4`, not `-3`, because floor division rounds towards negative infinity.

---

## 3. Comparison operators

Comparison operators compare two values and produce `True` or `False`.

| Operator | Meaning | Example |
|---|---|---|
| `==` | Equal to | `5 == 5` → `True` |
| `!=` | Not equal to | `5 != 3` → `True` |
| `<` | Less than | `3 < 5` → `True` |
| `>` | Greater than | `5 > 3` → `True` |
| `<=` | Less than or equal to | `5 <= 5` → `True` |
| `>=` | Greater than or equal to | `5 >= 6` → `False` |

Important differences:

- `=` assigns a value.
- `==` compares two values.

Different types can sometimes compare equal:

```python
print(5 == "5")   # False
print(1 == 1.0)   # True
```

Comparing incompatible types using ordering, such as `"5" < 5`, causes `TypeError`.

Python also supports chained comparisons:

```python
age = 25
print(18 <= age < 65)  # True
```

This means `age` must be at least 18 and less than 65.

---

## 4. Boolean operators: `and`, `or`, `not`

These operators combine or reverse conditions.

| Operator | Meaning |
|---|---|
| `and` | Both conditions must be `True`. |
| `or` | At least one condition must be `True`. |
| `not` | Reverses `True` and `False`. |

Example:

```python
has_ticket = True
is_on_time = False

print(has_ticket and is_on_time)  # False
print(has_ticket or is_on_time)   # True
print(not is_on_time)             # True
```

**Advanced detail introduced in this lesson:**

`and` and `or` can return actual operands, not necessarily Boolean values.

```python
print(0 and "hello")          # 0
print("hello" and "world")    # world
print(0 or "fallback")        # fallback
print("hello" or "fallback")  # hello
```

They also use short-circuit evaluation:

- `and` stops when its left operand is falsy.
- `or` stops when its left operand is truthy.

Falsy values introduced here include `False`, `0`, `None`, and `""`.

---

## 5. Membership operators: `in` and `not in`

These operators check whether particular text exists inside another string.

```python
print("cat" in "concatenate")      # True
print("dog" in "concatenate")      # False
print("dog" not in "concatenate")  # True
```

They are also used with collections such as lists, which you will study later.

---

## 6. Identity operators: `is` and `is not`

These operators check whether two references point to the exact same object.

- `==` checks whether values are equal.
- `is` checks whether they are the same object.

**Important beginner rule:** Use `==` for normal value comparisons. Use `is` specifically when checking `None`.

```python
score = None

if score is None:
    print("No score recorded yet.")
```

---

## 7. Operator precedence

Precedence means the order Python follows when multiple operators appear in one expression.

Simplified order, highest to lowest:

1. Parentheses `()`
2. Exponentiation `**`
3. Unary minus `-x`
4. `*`, `/`, `//`, `%`
5. `+`, `-`
6. Comparisons, membership and identity
7. `not`
8. `and`
9. `or`

Example:

```python
print(2 + 3 * 4)  # 14
```

Multiplication happens before addition.

Two important details:

```python
print(2 ** 3 ** 2)  # 512
print(-2 ** 2)      # -4
print((-2) ** 2)    # 4
```

Exponentiation evaluates right to left, and parentheses can change the grouping.

**Best practice:** Use parentheses whenever an expression might be confusing. They make your intended calculation clear.

---

## 8. Three practical examples

### Example 1: Dividing products into boxes

```python
total_items = 23
box_size = 4

print(total_items // box_size)  # 5
print(total_items % box_size)   # 3
```

### Example 2: Combining conditions

```python
age = 15
has_guardian = True

is_eligible = age >= 18 or (age >= 13 and has_guardian)
print(is_eligible)  # True
```

### Example 3: Checking a password and optional value

```python
password = "hunter2"
has_digit = "2" in password
has_space = " " not in password

discount_code = None

if discount_code is None:
    print("No discount code was entered.")
```

---

## 9. Common beginner mistakes

1. Confusing `=` with `==`.
2. Using `is` instead of `==` for ordinary comparisons.
3. Assuming operators always execute left to right.
4. Using `/` when whole-number division (`//`) is required.
5. Writing `not x == y` instead of the clearer `x != y`.

---

## 10. Practical exercises

Complete these five exercises:

1. An item costs `37.5`, and a customer pays `50`. Calculate the change using subtraction.
2. Create a discount rule using `and` and `or`. Test different conditions.
3. Convert `135` minutes into whole hours and remaining minutes using `//` and `%`.
4. Predict and verify the results of `"5" == 5` and `5 == 5`.
5. Set `a = 4`, `b = 5`, `c = 2`. Evaluate `a * b - c` using two different parenthesis placements and explain the results.

---

## 11. Connection to Data Engineering and AI Engineering

Operators are essential for implementing business rules and data-processing decisions.

- **Arithmetic:** Calculate revenue, totals, and data quantities.
- **Comparisons:** Validate records against business rules.
- **Boolean logic:** Decide whether a record should be accepted or rejected.
- **Membership:** Check whether a value exists in an allowed list.
- **Identity:** Check whether an API field or configuration value is `None`.
- **Precedence:** Ensure complex validation conditions execute correctly.

For example, an AI agent deciding whether it has enough information to execute a tool call uses comparisons and Boolean logic.
