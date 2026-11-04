# Summary: Values, Expressions, Statements, and Variables

This lesson covers four fundamental building blocks of Python programming: Values, Expressions, Statements, and Variables. Understanding these concepts is essential before learning loops, functions, classes, data structures, and eventually AI engineering.

## 1. Values – The Raw Data

A value is a piece of data used in a Python program.

Examples:

```python
42                  # Integer (int)
3.14                # Decimal number (float)
"hello"             # Text (string)
True                # Boolean
[1, 2, 3]           # List
```

Every value has a data type, which tells Python what kind of data it is and what operations can be performed on it.

For example:

- 42 is a whole number.
- 3.14 is a decimal number.
- "hello" is text.
- True represents a Boolean value.

## 2. Expressions – Producing a Value

An expression is a piece of Python code that Python evaluates to produce a value.

Examples:

```python
3 + 4
```

Result: 7

```python
"a" + "b"
```

Result: "ab"

```python
len("hello")
```

Result: 5

Even a single value, such as 42, is technically an expression because it evaluates to itself.

Remember: An expression calculates or produces a value.

## 3. Statements – Complete Instructions

A statement is an instruction that performs an action in a Python program.

Example:

```python
total = 3 + 4
print(total)
```

Here:

- total = 3 + 4 is an assignment statement.
- 3 + 4 is an expression inside that statement.
- print(total) is a statement that displays the result.

Important difference:

- Expression → Produces a value.
- Statement → Performs an action.

Writing 3 + 4 alone in a Python script calculates the result but does not automatically display it.

## 4. Variables and Assignment – Giving Names to Values

A variable is a name that refers to a value (object), allowing you to reuse that value without typing it repeatedly.

Example:

```python
age = 25
```

Here:

- age is the variable name.
- 25 is the value.
- = is the assignment operator.

Read this as: "Age is assigned the value 25."

Important: Python's = does not mean mathematical equality. It means assigning the value on the right to the name on the left.

Example:

```python
age = 25
next_year_age = age + 1
print(next_year_age)
```

Output:

```text
26
```

Python calculates age + 1 and assigns the result to next_year_age.

## 5. Reassignment – Changing What a Variable Refers To

Reassignment means assigning a different value to an existing variable.

Example:

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

The variable score initially refers to 10. Later, it refers to 20.

The original integer is not modified. Only the variable's reference changes.

Another example:

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

How it works:

1. Initial balance = 100.
2. Subtract 30 → 70.
3. Subtract 15 → 55.
4. Display 55.

Python evaluates the entire right-hand expression using the current value before assigning the new result.

## 6. Mutation – Changing Existing Data

Mutation means changing an existing mutable object without assigning a new object to its variable.

Lists are mutable in Python.

Example:

```python
scores = [10, 20, 30]
scores.append(40)
print(scores)
```

Output:

```text
[10, 20, 30, 40]
```

Here:

- .append(40) adds an element to the existing list.
- The variable scores was never reassigned.
- The original list itself was modified.

However, strings and numbers are immutable. They cannot be changed in place.

Example:

```python
name = "sam"
name.upper()
print(name)
```

Output:

```text
sam
```

.upper() produces a new string "SAM" without changing the original.

To retain the new value:

```python
name = name.upper()
print(name)
```

Output: SAM

## 7. Reassignment vs Mutation – Understanding Shared Data

This is an important Python concept because it explains how variables refer to objects in memory, how modifying an object affects other variables, and how reassignment works.

Let's understand it step by step.

### 1. First, understand two important terms

Mutation: Mutation means changing an existing object without creating a new object.

Reassignment: Reassignment means making a variable refer to a different object.

For example:

```python
numbers = [10, 20, 30]

# Mutation
numbers.append(40)

# Reassignment
numbers = [100, 200]
```

- append(40) modifies the existing list.
- numbers = [100, 200] makes numbers refer to a new list.

### 2. Understand the original example

Let's break down your code line by line.

```python
password_attempts = []
password_attempts.append("qwerty")
password_attempts.append("letmein")
backup_attempts = password_attempts
backup_attempts.append("hunter2")
print(password_attempts)
password_attempts = ["reset"]
print(password_attempts)
print(backup_attempts)
```

#### Step 1: Create an empty list

```python
password_attempts = []
```

Python creates an empty list in memory.

Memory representation

```text
List A
[]

password_attempts → List A
```

#### Step 2: Add elements using append()

```python
password_attempts.append("qwerty")
password_attempts.append("letmein")
```

The existing list is modified.

Its contents become:

```python
["qwerty", "letmein"]
```

This is called mutation.

#### Step 3: Assign one variable to another

```python
backup_attempts = password_attempts
```

Here is the most important part.

Python does not create another list. Both variables refer to the same list object.

Shared object in memory

```text
Original List A
["qwerty", "letmein"]

password_attempts
        ↓
     List A
        ↑
backup_attempts
```

Both variables point to the same list object.

#### Step 4: Modify the list using backup_attempts

```python
backup_attempts.append("hunter2")
```

Because both variables refer to the same list, the original list changes.

Now both variables see:

```python
["qwerty", "letmein", "hunter2"]
```

Therefore:

```python
print(password_attempts)
```

Output:

```text
['qwerty', 'letmein', 'hunter2']
```

#### Step 5: Reassign password_attempts

```python
password_attempts = ["reset"]
```

This creates a new list object.

Now the two variables refer to different lists.

Updated memory representation

```text
New List B
["reset"]

password_attempts points here

Original List A
["qwerty", "letmein", "hunter2"]

backup_attempts still points here
```

The original list has not been deleted because backup_attempts still refers to it.

Therefore, the final output is:

```text
['qwerty', 'letmein', 'hunter2']
['reset']
['qwerty', 'letmein', 'hunter2']
```

### 3. How to create a separate copy of a list

If you don't want two variables to share the same outer list, create a copy.

Python provides two common methods.

#### Method 1: Using .copy()

```python
password_attempts = ["qwerty", "letmein"]
backup_attempts = password_attempts.copy()
backup_attempts.append("hunter2")
print(password_attempts)
print(backup_attempts)
```

Output:

```text
['qwerty', 'letmein']
['qwerty', 'letmein', 'hunter2']
```

#### Method 2: Using list()

```python
password_attempts = ["qwerty", "letmein"]
backup_attempts = list(password_attempts)
backup_attempts.append("hunter2")
print(password_attempts)
print(backup_attempts)
```

Both methods create a separate outer list.

### 4. What is a shallow copy?

A shallow copy creates a new outer object but does not recursively copy the objects inside it.

Consider this example:

```python
original = [[10, 20], [30, 40]]
backup = original.copy()
backup[0].append(50)
print(original)
print(backup)
```

Output:

```text
[[10, 20, 50], [30, 40]]
[[10, 20, 50], [30, 40]]
```

Why did this happen?

Because the outer lists are different, but their nested lists are shared.

Shallow copy memory representation

```text
Original list
Outer List A

Backup list
Outer List B

Both reference the same nested lists

Shared nested list
[10, 20, 50]
```

### 5. What if you want a completely independent copy?

Use deepcopy() from Python's copy module.

```python
import copy

original = [[10, 20], [30, 40]]
backup = copy.deepcopy(original)
backup[0].append(50)
print(original)
print(backup)
```

Output:

```text
[[10, 20], [30, 40]]
[[10, 20, 50], [30, 40]]
```

Now even the nested lists are independent.

### 6. Important differences to remember

| Operation | What happens? |
| --- | --- |
| b = a | Both variables refer to the same object |
| a.append(10) | Modifies the existing list |
| b.append(10) | Modifies the shared list if b = a |
| a = [10, 20] | Reassigns a to a new list |
| a.copy() | Creates a shallow copy |
| list(a) | Creates a shallow copy |
| copy.deepcopy(a) | Creates a deep copy |

## 8. Common Beginner Mistakes

1. Thinking = means mathematical equality. Python uses == to compare values.
2. Assuming variable_2 = variable_1 creates an independent copy.
3. Expecting .upper() to modify the original string.
4. Forgetting that Python evaluates the entire right-hand expression before assignment.

## 9. Practical Exercises

Complete these exercises:

### Exercise 1 – Reassignment

```python
x = 5
y = x
x = x + 10
print(x, y)
```

Predict the output and explain why y does not change.

### Exercise 2 – Mutation

Create an empty cart list, add three grocery items using .append(), assign it to also_cart, and add another item through also_cart. Print both variables.

### Exercise 2 – Mutation

Let's implement this step by step.

Python code:

```python
# Step 1: Create an empty cart
cart = []

# Step 2: Add three grocery items
cart.append("Milk")
cart.append("Bread")
cart.append("Eggs")

# Step 3: Assign cart to another variable
also_cart = cart

# Step 4: Add another item through also_cart
also_cart.append("Butter")

# Step 5: Print both variables
print("Cart:", cart)
print("Also Cart:", also_cart)
```

Output:

```text
Cart: ['Milk', 'Bread', 'Eggs', 'Butter']
Also Cart: ['Milk', 'Bread', 'Eggs', 'Butter']
```

Explanation

1. cart = [] creates an empty list.
2. .append() adds grocery items to the list.
3. also_cart = cart makes both variables refer to the same list.
4. also_cart.append("Butter") modifies the shared list.
5. Both variables display the updated list.

Important concept: This is called mutation because we modified an existing list rather than creating a new list.

### Exercise 3 – Reassignment

Increase steps_taken by 1,000 twice, starting from zero, using reassignment. Expected result: 2000.

### Exercise 3 – Reassignment

Python code:

```python
# Step 1: Initialize steps_taken
steps_taken = 0

# Step 2: Increase by 1,000 using reassignment
steps_taken = steps_taken + 1000

# Step 3: Increase by another 1,000
steps_taken = steps_taken + 1000

# Step 4: Print the result
print(steps_taken)
```

Output:

```text
2000
```

Explanation

| Operation | Calculation | Value |
| --- | --- | --- |
| Initial value | steps_taken = 0 | 0 |
| First reassignment | 0 + 1000 | 1000 |
| Second reassignment | 1000 + 1000 | 2000 |

Important concept:

```python
steps_taken = steps_taken + 1000
```

Python first calculates the right-hand side (steps_taken + 1000) and then assigns the result back to steps_taken.

This is called reassignment because the variable receives a new value.

You can also write the same operation using shorthand:

```python
steps_taken += 1000
```

Both approaches produce the same result.

### Exercise 4 – String immutability

```python
name = "ada"
shout_name = name.upper()
name = "grace"
print(name, shout_name)
```

Predict the output before running it.

## 10. Connection to Applied AI and Agentic AI Engineering

In real-world AI applications, multiple components frequently share data, including:

- Conversation histories.
- Lists of tool results.
- Shopping cart information.
- Document collections.
- Agent internal state.

Accidentally mutating shared lists or dictionaries can introduce difficult bugs.

Understanding variables, reassignment, mutation, and copying will help you manage shared data correctly when developing production-level AI applications and agents.
