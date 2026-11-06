# 04-Abstruction

> This guide follows the attached lesson, **Sequence, Selection, Iteration, and Abstraction**. It focuses on abstraction through Python functions, then completes all four source exercises. The explanations are beginner-friendly and follow the lesson's terminology.

## Part 1 — Abstraction with functions (under 1,000 words)

### 1. What is abstraction?

**Abstraction means giving a group of related instructions one meaningful name, so the rest of the program can use that task without repeating or understanding every internal step.**

Everyday example: when you use an ATM, you select “Withdraw cash,” enter an amount, and receive cash. You do not need to know all the internal banking and machine operations. The option hides those details behind a clear task.

In Python, a **function** is the main way to create this kind of abstraction.

### 2. Why do we use functions?

1. **Reusability:** write the logic once and use it many times.
2. **Readability:** a name such as `count_signs` communicates the task.
3. **Easier maintenance:** fix the logic in one place instead of editing repeated copies.
4. **Organization:** divide a large program into smaller responsibilities.

### 3. Understand the parts of a function

```python
def greet(name):
    print("Hello, " + name + "!")

greet("Ada")
greet("Grace")
```

1. `def` tells Python that you are defining a function.
2. `greet` is the function's name. It describes its responsibility.
3. `name` is a **parameter**: a placeholder for the input the function needs.
4. The indented `print(...)` line is the function body—the instructions that run when the function is called.
5. `greet("Ada")` is a **function call**. It runs the function and supplies `"Ada"` as the input.
6. `greet("Grace")` calls the same function again with different input. The instructions do not need to be rewritten.

The function definition creates the reusable instructions; the function call executes them.

### 4. Parameters and arguments

A **parameter** is the variable named in the function definition, such as `name`. An **argument** is the actual value supplied in a call, such as `"Ada"`.

```python
def greet(name):       # name is the parameter
    print(name)

greet("Ada")           # "Ada" is the argument
```

### 5. Return value versus print

A function can return a result using `return`.

```python
def add(a, b):
    return a + b

result = add(3, 4)
print(result)
```

- `a` and `b` are parameters.
- `add(3, 4)` calls the function with arguments `3` and `4`.
- `return a + b` calculates the sum and hands the value back to the calling code.
- `result = add(3, 4)` stores the returned value.
- `print(result)` displays `7`.

**Important difference:** `print` displays something on the screen. `return` sends a value back so the program can store it, compare it, or use it in another calculation.

### 6. Abstraction can contain selection and iteration

A function does not replace `if` statements or loops. It can organize them under one responsibility.

```python
def is_password_long_enough(password):
    return len(password) >= 8
```

The function hides the length-checking detail behind the descriptive name. It returns `True` when the password has at least 8 characters and `False` otherwise. Passing this length check does **not** prove that a password is secure.

The lesson's `count_signs(numbers)` example similarly places three counters, a `for` loop, and `if`/`elif`/`else` decisions inside one reusable function. It returns the positive, negative, and zero counts together. This is a tuple (a grouped collection of values), which the lesson says will be studied properly in Module 1.2.

### 7. Common function mistakes

- Defining a function does not run its body; you must call it.
- The argument must provide the input the function expects.
- Indent the function body consistently.
- `print` and `return` are not interchangeable.
- A function that prints a value but does not return it cannot provide that displayed value for later calculations.

---

## Part 2 — All exercises with functions where requested (under 1,500 words)

### Exercise 1 — Write and test `is_even(number)`

**Requirement:** return `True` for an even number and `False` for an odd number; test at least four numbers, including both types.

```python
def is_even(number):
    return number % 2 == 0

test_numbers = [4, 7, 10, 13]

for number in test_numbers:
    result = is_even(number)
    print(number, "->", result)
```

**Line-by-line explanation**

1. `def is_even(number):` defines a reusable function named `is_even`. `number` is its parameter.
2. `return number % 2 == 0` calculates the remainder after division by 2, checks whether it is zero, and returns the Boolean result (`True` or `False`).
3. `test_numbers = [4, 7, 10, 13]` stores four test values, including even and odd numbers.
4. `for number in test_numbers:` visits each value in the list.
5. `result = is_even(number)` calls the function with the current value and stores its returned Boolean.
6. `print(number, "->", result)` displays the number and its result.

**Expected output**
```text
4 -> True
7 -> False
10 -> True
13 -> False
```

### Exercise 2 — Print multiples of 3 from 1 to 20

**Requirement:** use a `for` loop; print only numbers divisible by 3. This exercise does not ask for a function, so keep it as the requested loop.

```python
for number in range(1, 21):
    if number % 3 == 0:
        print(number)
```

**Line-by-line explanation**

1. `for number in range(1, 21):` checks every integer from 1 through 20; `21` is excluded.
2. `if number % 3 == 0:` checks whether division by 3 leaves remainder zero.
3. `print(number)` displays the number only when the condition is true.

**Expected output**
```text
3
6
9
12
15
18
```

### Exercise 3 — Double a counter until it exceeds 1,000

**Requirement:** use a `while` loop, start at 1, double repeatedly, and print every value produced by a doubling. The starting value does not have to be printed.

```python
counter = 1

while counter <= 1000:
    counter = counter * 2
    print(counter)
```

**Line-by-line explanation**

1. `counter = 1` sets the starting value.
2. `while counter <= 1000:` repeats while the current value is at most 1,000.
3. `counter = counter * 2` doubles the value.
4. `print(counter)` displays the new value after the doubling.

**Expected output**
```text
2
4
8
16
32
64
128
256
512
1024
```

The loop begins its final iteration when `counter` is `512`. It doubles and prints `1024`. At the next check, `1024 <= 1000` is false, so the loop stops.

### Exercise 4 — Create `traffic_light_message(color)`

**Requirement:** return the correct instruction for red, yellow, or green. Call the function in a loop over the exact list supplied in the lesson.

```python
def traffic_light_message(color):
    if color == "red":
        return "Stop"
    elif color == "yellow":
        return "Prepare to stop"
    elif color == "green":
        return "Go"
    else:
        return "Unknown color"

colors = ["green", "yellow", "red", "green"]

for color in colors:
    message = traffic_light_message(color)
    print(message)
```

**Line-by-line explanation**

1. `def traffic_light_message(color):` defines a function with the parameter `color`.
2. `if color == "red":` checks whether the supplied color is red.
3. `return "Stop"` sends the red instruction back to the caller.
4. `elif color == "yellow":` checks yellow if the red condition was false.
5. `return "Prepare to stop"` sends back the yellow instruction.
6. `elif color == "green":` checks green if the earlier conditions were false.
7. `return "Go"` sends back the green instruction.
8. `else:` handles any color other than the three recognized values.
9. `return "Unknown color"` sends back a clear fallback message.
10. `colors = [...]` stores the exact four colors required by the exercise.
11. `for color in colors:` processes each list item once.
12. `message = traffic_light_message(color)` calls the function for the current color and stores the returned instruction.
13. `print(message)` displays that instruction.

**Expected output**
```text
Go
Prepare to stop
Stop
Go
```

---

## Final understanding

Abstraction gives a group of instructions a clear name and hides its internal details. In Python, functions provide this reusable boundary. A function can receive information through **parameters**, run its internal sequence/selection/iteration, and send a result back through **return**. Exercises 1 and 4 practise this directly; Exercises 2 and 3 practise the specific loop requirements stated in the source.
