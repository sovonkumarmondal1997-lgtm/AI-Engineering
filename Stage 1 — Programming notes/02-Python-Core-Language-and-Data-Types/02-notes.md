# Lesson 02: Variables, Basic Types, and None

**Complete lesson summary** · Beginner level

This lesson teaches you how Python stores information, identifies different kinds of data, and handles situations where information is not available.

The central concept is that every value in Python has a type, and its type determines what operations you can perform on it.

---

## 1. What is a variable?

A variable is a name that refers to a value (more precisely, a Python object).

Example:

```python
age = 25
```

Here:

- `age` is the variable name.
- `25` is the value.
- `=` is the assignment operator.
- Python binds the name `age` to an integer object.

You can change the value later. This is called reassignment.

```python
age = 25
age = 30
```

Now `age` refers to the value `30`.

**Best practice:** Use meaningful variable names instead of vague names.

```python
customer_name = "Amara"
total_price = 500
is_subscribed = True
```

Use lowercase words separated by underscores.

---

## 2. What is a data type?

A data type tells Python what kind of value an object represents and what operations are allowed.

This lesson covers four fundamental types and one special value.

---

## 3. The four fundamental Python types

### A. `int` – Integer

Stores whole numbers without decimal points.

Examples:

```python
age = 25
items_in_cart = 4
temperature = -3
```

**Real-world usage:** Age, number of products, number of attempts, and quantities.

### B. `float` – Floating-point number

Stores numbers that can contain fractional parts.

Examples:

```python
price = 19.99
height = 1.75
temperature = 36.6
```

Even `7.0` is a float, not an integer.

**Important:** Floats use finite binary precision. Some decimal numbers, such as `0.1`, cannot be represented exactly. This can cause small rounding differences.

For exact financial calculations, Python provides `decimal.Decimal`.

### C. `bool` – Boolean

Stores only two possible values:

- `True`
- `False`

Examples:

```python
is_completed = False
is_subscribed = True
```

**Real-world usage:** Whether a task is completed, a user is subscribed, or a system is active.

**Important Python detail:** `bool` is technically a subclass of `int`. Therefore, Boolean values can participate in certain numerical operations as `1` and `0`.

### D. `str` – String

Stores text, words, names, messages, and characters.

Examples:

```python
first_name = "Amara"
city = "Kolkata"
```

Python supports both single and double quotation marks.

**Important difference:**

```python
age = 7
number_text = "7"
```

- `7` is an integer.
- `"7"` is a string containing the character seven.

They are different data types.

---

## 4. What is `None`?

`None` is a special Python value representing the absence of a meaningful value.

Its type is `NoneType`.

Example:

```python
middle_name = None
```

This means the middle name is currently unavailable or has not been provided.

It is important to distinguish these four values:

| Value | Meaning |
|---|---|
| `None` | No meaningful value available |
| `0` | Actual numerical zero |
| `False` | Actual Boolean false |
| `""` | An existing string containing zero characters |

They are not interchangeable.

```python
print(None == 0)      # False
print(None == False)  # False
print(None == "")     # False
```

Also remember:

- `None` is a special value.
- `"None"` is ordinary text.

---

## 5. How to check data types using `type()`

Python provides the built-in `type()` function to identify the type of a value.

```python
print(type(25))
print(type(19.99))
print(type(True))
print(type("hello"))
print(type(None))
```

Output:

```text
<class 'int'>
<class 'float'>
<class 'bool'>
<class 'str'>
<class 'NoneType'>
```

This is particularly useful when debugging programs and inspecting unfamiliar data.

---

## 6. Can a variable change its data type?

Yes. Python allows a variable name to refer to objects of different types through reassignment.

```python
signup_status = "not started"
print(type(signup_status))

signup_status = True
print(type(signup_status))
```

Initially, the variable refers to a string. Later, it refers to a Boolean.

Python does not permanently lock a variable to its first type.

---

## 7. Combining text and numbers

One common beginner mistake is directly combining a string and an integer using `+`.

Incorrect:

```python
age = 25
print("Age: " + age)
```

This produces a `TypeError` because Python cannot directly concatenate a string and an integer.

A safe beginner-friendly solution is to use commas:

```python
age = 25
print("Age:", age)
```

Output:

```text
Age: 25
```

Python's `print()` function can display multiple values of different types separated by commas.

---

## 8. Three practical examples

### Example 1: Working with all basic types

```python
age = 25
price = 19.99
is_subscribed = True
name = "Amara"
middle_name = None

print(age, type(age))
print(price, type(price))
print(is_subscribed, type(is_subscribed))
print(name, type(name))
print(middle_name, type(middle_name))
```

### Example 2: Using `None` for optional information

```python
phone_number = None
print(phone_number)

phone_number = "555-0142"
print(phone_number)
```

Initially, the phone number is unavailable. Later, actual information is assigned.

### Example 3: Correctly displaying different data types

```python
age = 25
print("Age:", age)
```

This avoids the string-and-integer concatenation error.

---

## 9. Common beginner mistakes

1. Combining text and numbers directly with `+`, causing `TypeError`.
2. Confusing `None` with `0`, `False`, or `""`.
3. Confusing `None` with `"None"`.
4. Using vague variable names instead of descriptive names.
5. Assuming a variable permanently retains its first data type.

---

## 10. Practical exercises

Complete these five exercises:

1. Create variables for your age (`int`), height (`float`), and exercise completion status (`bool`). Print their values and types.
2. Create `discount_code = None`, print it, then reassign it to `"SAVE10"` and print again.
3. Predict the types of `10`, `10.0`, `True`, `"10"`, and `None`. Verify using `type()`.
4. Deliberately combine text and a number using `+`. Observe the error and fix it using commas.
5. Rename `x = 42` to a meaningful variable representing someone's age. Explain why the new name is better.

---

## 11. Connection to Data Engineering and AI Engineering

These concepts are fundamental when working with real-world data.

- `int`: Number of records processed.
- `float`: Product prices and measurements.
- `bool`: Whether a pipeline or validation check succeeded.
- `str`: Customer names, identifiers, and API responses.
- `None`: Missing database fields, unavailable API values, or information not yet received.

For example, when processing API responses or validating data in an ETL pipeline, distinguishing between missing information (`None`) and actual values (`0`, `False`, or `""`) prevents data-quality bugs.
