# Summary: Sequence, Selection, Iteration, and Abstraction

This lesson introduces four fundamental programming concepts: Sequence, Selection, Iteration, and Abstraction. Almost every Python application, data engineering pipeline, and AI agent uses these concepts.

## 1. Sequence – Executing Instructions in Order

Sequence means Python executes instructions one after another, from top to bottom.

Example:

```python
name = "Sovon"
age = 25
print(name)
print(age)
```

Output:

```text
Sovon
25
```

Python executes the first instruction, then the second, and finally displays both values.

Sequence is the default execution behavior. Selection and iteration change which instructions execute and how often.

## 2. Selection – Making Decisions Using Conditions

Selection allows a program to choose which instructions to execute based on a condition.

Python uses:

- if – Checks a condition.
- elif – Checks another condition if the previous one was false.
- else – Executes when none of the previous conditions is true.

Example:

```python
age = 20
if age >= 18:
    print("You can vote.")
```

Output: You can vote.

### Comparison operators

| Operator | Meaning |
| --- | --- |
| == | Equal to |
| != | Not equal to |
| < | Less than |
| > | Greater than |
| <= | Less than or equal to |
| >= | Greater than or equal to |

Remember: = assigns a value, whereas == compares two values.

### Example: Multiple conditions

```python
temperature = 15
if temperature > 30:
    print("It's hot.")
elif temperature > 15:
    print("It's warm.")
else:
    print("It's cool.")
```

Output: It's cool.

Python checks conditions from top to bottom and executes the first matching block.

Boundary conditions:

- Above 30 → Hot.
- Above 15 and up to 30 → Warm.
- 15 or below → Cool.

### Boolean operators

Boolean operators combine or modify conditions:

- and – Both conditions must be true.
- or – At least one condition must be true.
- not – Reverses True into False and False into True.

Example:

```python
has_ticket = True
is_on_time = False
if has_ticket and is_on_time:
    print("Boarding allowed.")
else:
    print("Boarding denied.")
```

Output: Boarding denied.

## 3. Iteration – Repeating Instructions

Iteration means executing a block of code repeatedly.

Python provides two main loops.

### A. for loop

A for loop executes once for each item in an iterable, such as a list.

Example:

```python
numbers = [10, 20, 30]
for number in numbers:
    print(number)
```

Output:

```text
10
20
30
```

Python takes each item from the list and executes the indented instructions.

### B. while loop

A while loop repeats instructions as long as its condition remains true.

Example:

```python
count = 0
while count < 3:
    print(count)
    count = count + 1
```

Output:

```text
0
1
2
```

How it works:

1. Start with count = 0.
2. Check whether count < 3.
3. Print the current value.
4. Increase count by 1.
5. Repeat until the condition becomes false.

Important: Always ensure a while loop has a way to terminate. Otherwise, it may become an infinite loop.

## 4. Abstraction – Creating Reusable Code Using Functions

Abstraction means grouping instructions under a meaningful name so you can reuse them without rewriting the same logic.

Python uses functions for this purpose.

Example:

```python
def greet(name):
    print("Hello, " + name + "!")

greet("Ada")
greet("Grace")
```

Output:

```text
Hello, Ada!
Hello, Grace!
```

Explanation:

- def defines a function.
- greet is the function name.
- name is a parameter.
- greet("Ada") calls the function.
- The same function can be reused with different values.

### Parameters and Return Values

A parameter is a named placeholder for information a function needs.

A return value is the result a function sends back to the code that called it.

Example:

```python
def add(a, b):
    return a + b

result = add(3, 4)
print(result)
```

Output: 7

Important difference:

- print() displays information on the screen.
- return sends a value back so other parts of the program can use it.

## 5. Practical Example: Counting Positive, Negative, and Zero Numbers

This example combines iteration and selection.

```python
numbers = [4, -2, 0, 7, -9, 0, 1]
positive_count = 0
negative_count = 0
zero_count = 0
for number in numbers:
    if number > 0:
        positive_count = positive_count + 1
    elif number < 0:
        negative_count = negative_count + 1
    else:
        zero_count = zero_count + 1
print("Positive:", positive_count)
print("Negative:", negative_count)
print("Zero:", zero_count)
```

Output:

```text
Positive: 3
Negative: 2
Zero: 2
```

The for loop examines every number, while if, elif, and else decide which counter to increase.

This is called selection inside iteration.

## 6. Combining All Four Concepts Using Functions

```python
def is_password_long_enough(password):
    return len(password) >= 8

def count_signs(numbers):
    positive_count = 0
    negative_count = 0
    zero_count = 0
    for number in numbers:
        if number > 0:
            positive_count = positive_count + 1
        elif number < 0:
            negative_count = negative_count + 1
        else:
            zero_count = zero_count + 1
    return positive_count, negative_count, zero_count

passwords_to_check = ["hunter2", "correcthorsebatterystaple", "abc"]
for password in passwords_to_check:
    if is_password_long_enough(password):
        print(password, "-> OK")
    else:
        print(password, "-> too short")

positives, negatives, zeros = count_signs([4, -2, 0, 7, -9, 0, 1])
print("Positive:", positives, "Negative:", negatives, "Zero:", zeros)
```

Important new concepts:

- return can return multiple values as a tuple.
- Python can unpack those values into separate variables.
- Functions allow the same logic to be reused.
- A function can return a Boolean value (True or False).
- A function makes debugging easier because you can fix logic in one place.

The password example only checks length; passing this check does not guarantee password security.

## 7. Common Beginner Mistakes

1. Using = instead of == in conditions.
2. Forgetting colons (:) after if, elif, else, for, while, and def.
3. Incorrect indentation. Python uses indentation to identify code blocks.
4. Creating an infinite while loop by forgetting to update its condition.
5. Confusing print() with return. A function without an explicit return value returns None.
6. Using elif or else without a corresponding if.

## 8. Practical Exercises

Complete these four exercises:

1. Even Number Checker: Create is_even(number) that returns True for even numbers and False for odd numbers. Use % (remainder operator) and test at least four numbers.
2. Divisibility: Use a for loop to print numbers from 1 to 20 that are divisible by 3.
3. Doubling Counter: Start a counter at 1 and repeatedly double it using a while loop until it exceeds 1000. Print each new value.
4. Traffic Light Function: Create traffic_light_message(color) that returns:
   - "red" → "Stop"
   - "yellow" → "Prepare to stop"
   - "green" → "Go"

   Call the function inside a loop using ["green", "yellow", "red", "green"] and print each message.

## 9. Connection to Applied AI and Agentic AI Engineering

These four concepts are directly used in AI agent development.

| Concept | AI Engineering Application |
| --- | --- |
| Sequence | Executing agent instructions in order |
| Selection | Deciding which tool or action to use |
| Iteration | Repeating the agent's decision-and-action cycle |
| Abstraction | Creating reusable functions and agent tools |

For example, an AI agent observes a situation, decides what action to take, executes it, and repeats until the task is complete.
