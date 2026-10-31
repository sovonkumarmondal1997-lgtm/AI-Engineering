# Module 1.1 — Solutions to All Six Python Practice Questions

I have analysed your attached practice file. It contains six exercises covering the Python fundamentals from your first eight lessons: variables, loops, conditions, functions, decomposition, pseudocode, edge cases, and state modelling. practice-questions.md

We will solve all six exercises in order. For each one, I will show:

1. Problem understanding.
2. Assumptions and inputs/outputs.
3. Pseudocode.
4. Complete Python solution.
5. Expected output and explanation.
6. Important edge cases.

I will use concepts from your lessons and avoid introducing advanced Python features unnecessarily.

## Question 1 — Calculate the total and average of expenses

Source exercise: Question 1

### Step 1: Understand the problem

We receive a list of expenses and need to calculate:

- Total: Sum of all expenses.
- Average: Total divided by the number of expenses.

Example:

```python
expenses = [12, 45, 9, 20]
```

Expected total = 86

Expected average = 21.5

### Step 2: Define assumptions

- Zero expenses are allowed.
- Negative expenses are allowed because they may represent refunds.
- We will show the average as Python calculates it, without rounding.
- For an empty list, total will be 0 and average will be None, meaning no average is available.

### Step 3: Pseudocode

```text
START

FUNCTION calculate_total(expenses)
    SET total TO 0
    FOR EACH expense IN expenses
        ADD expense TO total
    RETURN total
END FUNCTION

FUNCTION calculate_average(expenses)
    IF expense list is empty
        RETURN None
    CALCULATE total
    RETURN total divided by number of expenses
END FUNCTION

CALL both functions
DISPLAY total and average

END
```

### Step 4: Python solution

```python
def calculate_total(expenses):
    total = 0
    for expense in expenses:
        total = total + expense
    return total

def calculate_average(expenses):
    if len(expenses) == 0:
        return None
    total = calculate_total(expenses)
    average = total / len(expenses)
    return average

# Main program
expenses = [12, 45, 9, 20]
total = calculate_total(expenses)
average = calculate_average(expenses)
print("Total expenses:", total)
print("Average expense:", average)
```

### Step 5: Expected output

```text
Total expenses: 86
Average expense: 21.5
```

### Step 6: Understand the code

#### Function 1: calculate_total()

```python
total = 0
for expense in expenses:
    total = total + expense
```

The loop takes each expense and adds it to total.

| Expense | Calculation | Total |
| --- | --- | --- |
| 12 | 0 + 12 | 12 |
| 45 | 12 + 45 | 57 |
| 9 | 57 + 9 | 66 |
| 20 | 66 + 20 | 86 |

#### Function 2: calculate_average()

```python
if len(expenses) == 0:
    return None
```

This prevents division by zero.

```python
average = total / len(expenses)
```

There are four expenses, so 86 / 4 = 21.5.

### Step 7: Edge-case tests

Try these inputs:

| Input | Expected total | Expected average |
| --- | --- | --- |
| [] | 0 | None |
| [50] | 50 | 50.0 |
| [10, 10, 10] | 30 | 10.0 |
| [-10, 20] | 10 | 5.0 |

What you learned: Running totals, for loops, len(), functions, return, and empty-list handling.

## Question 2 — Check whether a password meets minimum rules

Source exercise: Question 2

### Step 1: Understand the problem

We need to check whether a password satisfies a set of rules.

We will choose these three rules:

1. Password must contain at least 8 characters.
2. Password must contain at least one digit.
3. Password must not contain spaces.

If a password fails a rule, our program will report the first failed rule and stop checking.

### Step 2: Define assumptions

| Rule | Example |
| --- | --- |
| Minimum length is 8 | python123 passes |
| At least one digit | pythonabc fails |
| No spaces | python 123 fails |

An empty password fails the minimum-length rule.

### Step 3: Pseudocode

```text
START

FUNCTION has_minimum_length(password)
    CHECK whether length is at least 8
    RETURN result
END FUNCTION

FUNCTION has_digit(password)
    CHECK every character
    IF a digit is found
        RETURN True
    RETURN False
END FUNCTION

FUNCTION has_no_spaces(password)
    CHECK every character
    IF a space is found
        RETURN False
    RETURN True
END FUNCTION

FUNCTION check_password(password)
    IF minimum length fails
        RETURN "Too short"
    IF digit check fails
        RETURN "Needs a digit"
    IF space check fails
        RETURN "Spaces are not allowed"
    RETURN "Password accepted"
END FUNCTION

DISPLAY result

END
```

### Step 4: Python solution

```python
def has_minimum_length(password):
    return len(password) >= 8

def has_digit(password):
    for character in password:
        if character.isdigit():
            return True
    return False

def has_no_spaces(password):
    for character in password:
        if character == " ":
            return False
    return True

def check_password(password):
    if not has_minimum_length(password):
        return "Password is too short"
    if not has_digit(password):
        return "Password needs at least one digit"
    if not has_no_spaces(password):
        return "Password must not contain spaces"
    return "Password accepted"

# Main program
password = "python123"
```

### Step 5: Expected output

```text
Password accepted
```

Let's test different passwords:

```python
print(check_password("abc"))
print(check_password("pythonabc"))
print(check_password("python 123"))
print(check_password("python123"))
print(check_password(""))
print(check_password("12345678"))
```

Output:

```text
Password is too short
Password needs at least one digit
Password must not contain spaces
Password accepted
Password is too short
Password accepted
```

### Step 6: Understand the important code

Checking for a digit:

```python
for character in password:
    if character.isdigit():
        return True
```

The loop checks each character individually.

For "python123":

- p, y, t, h, o, n are not digits.
- 1 is a digit.
- The function immediately returns True.

Checking for spaces:

```python
if character == " ":
    return False
```

If a space is found, the function immediately returns False.

Checking all rules in order:

```python
if not has_minimum_length(password):
    return "Password is too short"
```

not reverses the Boolean result. If the password does not meet the minimum length, the function returns the failure message.

The next checks run only if the previous checks pass.

### Step 7: Edge-case tests

| Password | Expected result |
| --- | --- |
| "" | Too short |
| "12345678" | Accepted |
| "abcdefgh" | Needs a digit |
| "python 12" | Spaces are not allowed |
| "python123" | Accepted |

What you learned: Functions, string iteration, len(), .isdigit(), Boolean values, not, and early returns.

Security note: This is a beginner exercise, not a complete production password-security system. Real authentication requires secure password storage and additional controls.

## Question 3 — Simulate a traffic light with three states

Source exercise: Question 3

### Step 1: Understand the problem

A traffic light has three states:

- red
- green
- yellow

The allowed sequence is:

red → green → yellow → red

We will use the requested-transition approach: the program receives a requested state and checks whether the change is valid.

### Step 2: Define assumptions

- The starting state is red.
- Only the next state in the sequence is allowed.
- An invalid request is rejected.
- When a request is rejected, the current state must remain unchanged.
- Repeated valid requests can continue cycling.

### Step 3: Transition table

| Current state | Allowed next state |
| --- | --- |
| red | green |
| green | yellow |
| yellow | red |

### Step 4: Pseudocode

```text
START

FUNCTION is_transition_allowed(state, requested_state)
    IF state is red
        RETURN whether requested state is green
    ELSE IF state is green
        RETURN whether requested state is yellow
    ELSE IF state is yellow
        RETURN whether requested state is red
    ELSE
        RETURN False
END FUNCTION

SET current_state TO red

FOR EACH requested state
    IF transition is allowed
        UPDATE current state
        DISPLAY success
    ELSE
        REJECT request
        KEEP current state unchanged
    DISPLAY current state
END FOR

END
```

### Step 5: Python solution

```python
def is_transition_allowed(state, requested_state):
    if state == "red":
        return requested_state == "green"
    elif state == "green":
        return requested_state == "yellow"
    elif state == "yellow":
        return requested_state == "red"
    else:
        return False

def request_transition(state, requested_state):
    if is_transition_allowed(state, requested_state):
        return requested_state
    else:
        return state

# Main program
current_state = "red"
requests = ["green", "yellow", "yellow", "red", "green"]

for requested_state in requests:
    print("Requested state:", requested_state)
    if is_transition_allowed(current_state, requested_state):
        current_state = request_transition(
```

### Step 6: Expected output

```text
Requested state: green
Transition accepted
Current state: green
----------------------

Requested state: yellow
Transition accepted
Current state: yellow
----------------------

Requested state: yellow
Transition rejected
Current state: yellow
----------------------

Requested state: red
Transition accepted
Current state: red
----------------------

Requested state: green
Transition accepted
Current state: green
----------------------
```

### Step 7: Understand the important code

The validation function:

```python
if state == "red":
    return requested_state == "green"
```

If the current state is red, only green is allowed.

For example:

```python
is_transition_allowed("red", "green")
```

Returns True.

But:

```python
is_transition_allowed("red", "yellow")
```

Returns False.

The transition function:

```python
def request_transition(state, requested_state):
    if is_transition_allowed(state, requested_state):
        return requested_state
    else:
        return state
```

This function returns the requested state if it is valid. Otherwise, it returns the original state.

The loop:

```python
for requested_state in requests:
```

The program processes each requested transition one by one.

Notice the third request is yellow, while the current state is already yellow. It is rejected because the next valid state must be red.

What you learned: State modelling, transition validation, functions calling other functions, loops, and preventing invalid state changes.

## Question 4 — Count positive, negative, and zero numbers

Source exercise: Question 4

### Step 1: Understand the problem

Given a list of numbers, count:

1. How many numbers are positive.
2. How many numbers are negative.
3. How many numbers are exactly zero.

Example:

```python
numbers = [4, -2, 0, 7, -9, 0, 1]
```

Expected result:

- Positive = 3
- Negative = 2
- Zero = 2

### Step 2: Define assumptions

- Numbers can be integers or decimals.
- Every item in the list is assumed to be a valid number.
- An empty list should return three zero counts.

### Step 3: Pseudocode

```text
START

SET positive_count TO 0
SET negative_count TO 0
SET zero_count TO 0

FOR EACH number IN numbers

    IF number is greater than 0
        INCREASE positive_count

    ELSE IF number is less than 0
        INCREASE negative_count

    ELSE
        INCREASE zero_count

END FOR

RETURN all three counts

END
```

### Step 4: Python solution

```python
def count_numbers(numbers):
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

# Main program
numbers = [4, -2, 0, 7, -9, 0, 1]
positive, negative, zero = count_numbers(numbers)
print("Positive numbers:", positive)
print("Negative numbers:", negative)
print("Zero numbers:", zero)
```

### Step 5: Expected output

```text
Positive numbers: 3
Negative numbers: 2
Zero numbers: 2
```

### Step 6: Understand the code

We create three counters:

```python
positive_count = 0
negative_count = 0
zero_count = 0
```

All counters start at zero because we have not examined any numbers yet.

Next, the loop examines every number.

| Number | Condition | Positive | Negative | Zero |
| --- | --- | --- | --- | --- |
| 4 | Positive | 1 | 0 | 0 |
| -2 | Negative | 1 | 1 | 0 |
| 0 | Zero | 1 | 1 | 1 |
| 7 | Positive | 2 | 1 | 1 |
| -9 | Negative | 2 | 2 | 1 |
| 0 | Zero | 2 | 2 | 2 |
| 1 | Positive | 3 | 2 | 2 |

Finally:

```python
return positive_count, negative_count, zero_count
```

The function returns three values.

We receive them using:

```python
positive, negative, zero = count_numbers(numbers)
```

This is called multiple assignment (tuple unpacking): each returned value is assigned to its corresponding variable.

### Step 7: Edge-case tests

```python
print(count_numbers([]))
print(count_numbers([1, 2, 3]))
print(count_numbers([0, 0, 0]))
print(count_numbers([-5]))
print(count_numbers([2.5, -1.5, 0.0]))
```

Output:

```text
(0, 0, 0)
(3, 0, 0)
(0, 0, 3)
(0, 1, 0)
(1, 1, 1)
```

What you learned: Iteration, selection, three independent counters, comparison operators, and returning multiple values.

## Question 5 — Find the largest number without using max()

Source exercise: Question 5

### Step 1: Understand the problem

We receive a list of numbers and must find the largest number without using Python's built-in max() function.

Example:

```python
numbers = [3, 9, 2, 9, 4]
```

Expected result:

```text
9
```

### Step 2: Understand the main idea

We will use a concept called best value so far.

Imagine you are examining numbers one by one. You remember the largest number you have seen so far.

Whenever you find a bigger number, you replace the remembered value.

For example:

| Current number | Largest so far |
| --- | --- |
| 3 | 3 |
| 9 | 9 |
| 2 | 9 |
| 9 | 9 |
| 4 | 9 |

The final answer is 9.

### Step 3: Define assumptions

- The list should contain numbers.
- If the list is empty, the function returns None.
- Duplicate largest numbers are allowed.
- Negative numbers must be handled correctly.

### Step 4: Pseudocode

```text
START

FUNCTION find_largest(numbers)

    IF list is empty
        RETURN None

    SET largest TO first number

    FOR EACH number IN numbers

        IF number is greater than largest
            SET largest TO number

    RETURN largest

END FUNCTION

END
```

### Step 5: Python solution

```python
def find_largest(numbers):
    if len(numbers) == 0:
        return None
    largest = numbers[0]
    for number in numbers:
        if number > largest:
            largest = number
    return largest

# Main program
numbers = [3, 9, 2, 9, 4]
result = find_largest(numbers)
print("Largest number:", result)
```

### Step 6: Expected output

```text
Largest number: 9
```

### Step 7: Understand the code

First, check whether the list is empty:

```python
if len(numbers) == 0:
    return None
```

We cannot access the first element of an empty list. Therefore, we handle this case first.

Second, initialize the largest value:

```python
largest = numbers[0]
```

This is important.

We use the first number instead of 0.

Why?

Consider:

```python
numbers = [-10, -5, -20, -3]
```

If we start with largest = 0, the program would incorrectly return 0, even though zero is not in the list.

Starting with the first element ensures that negative numbers work correctly.

Third, compare every number:

```python
for number in numbers:
    if number > largest:
        largest = number
```

Whenever a number is greater than the current largest value, we update largest.

### Step 8: Edge-case tests

```python
print(find_largest([]))
print(find_largest([50]))
print(find_largest([3, 9, 2, 9, 4]))
print(find_largest([-10, -5, -20, -3]))
print(find_largest([7, 7, 7]))
```

Output:

```text
None
50
9
-3
7
```

What you learned: List indexing, initialization, comparison, iteration, and the best-value-so-far algorithm.

## Question 6 — Count words in a sentence, ignoring case and punctuation

Source exercise: Question 6

### Step 1: Understand the problem

We receive a sentence and must count how many times each word appears.

The program must:

1. Ignore capital and lowercase differences.
2. Remove punctuation from consideration.
3. Split the sentence into individual words.
4. Count how many times each distinct word appears.

Example input:

```python
sentence = "The cat sat. The cat sat on the mat!"
```

Expected word counts:

| Word | Count |
| --- | --- |
| the | 3 |
| cat | 2 |
| sat | 2 |
| on | 1 |
| mat | 1 |

### Step 2: Define assumptions

We will use these rules:

- Convert all text to lowercase.
- Handle these punctuation characters: . , ! ?.
- Treat punctuation as a word separator.
- Ignore extra spaces between words.
- An empty sentence returns two empty lists.

We will use two lists instead of a dictionary because the exercise allows a beginner-friendly solution using lists.

- unique_words stores each different word.
- word_counts stores the corresponding count.

For example:

```python
unique_words = ["the", "cat", "sat"]
word_counts = [3, 2, 2]
```

The positions match: the has count 3, cat has count 2, and sat has count 2.

### Step 3: Pseudocode

```text
START

FUNCTION clean_sentence(sentence)

    CONVERT sentence to lowercase

    SET cleaned_text TO empty text

    FOR EACH character IN sentence

        IF character is punctuation
            ADD a space to cleaned_text
        ELSE
            ADD character to cleaned_text

    RETURN cleaned_text

END FUNCTION


FUNCTION count_words(sentence)

    CLEAN the sentence
    SPLIT cleaned sentence into words

    CREATE empty unique_words list
    CREATE empty word_counts list

    FOR EACH word IN words

        SET found TO False

        FOR EACH existing word position
            IF existing word matches current word
                INCREASE its matching count
                SET found TO True

        IF found is False
            ADD word to unique_words
            ADD 1 to word_counts

    RETURN unique_words and word_counts

END FUNCTION

DISPLAY each word and its count

END
```

### Step 4: Python solution

```python
def clean_sentence(sentence):
    sentence = sentence.lower()
    cleaned_text = ""
    punctuation = ".,!?"
    for character in sentence:
        if character in punctuation:
            cleaned_text = cleaned_text + " "
        else:
            cleaned_text = cleaned_text + character
    return cleaned_text

def count_words(sentence):
    cleaned_text = clean_sentence(sentence)
    words = cleaned_text.split()
    unique_words = []
    word_counts = []
    for word in words:
        found = False
        for i in range(len(unique_words)):
            if unique_words[i] == word:
                word_counts[i] = word_counts[i] + 1
```

### Step 5: Expected output

```text
Word counts:
the : 3
cat : 2
sat : 2
on : 1
mat : 1
```

### Step 6: Understand the code

#### A. Convert everything to lowercase

```python
sentence = sentence.lower()
```

For example:

```text
"The CAT Sat"
```

Becomes:

```text
"the cat sat"
```

This ensures "Cat", "cat", and "CAT" are counted as the same word.

#### B. Remove punctuation

```python
punctuation = ".,!?"
for character in sentence:
    if character in punctuation:
        cleaned_text = cleaned_text + " "
    else:
        cleaned_text = cleaned_text + character
```

We replace punctuation with spaces.

Why spaces instead of simply removing punctuation?

For example, "cat,dog" should become "cat dog", not "catdog".

#### C. Split the sentence into words

```python
words = cleaned_text.split()
```

The .split() method separates text into words using whitespace.

Example:

```python
"the cat sat".split()
```

Result:

```python
["the", "cat", "sat"]
```

It also handles extra spaces between words.

#### D. Create two empty lists

```python
unique_words = []
word_counts = []
```

The first list remembers words. The second list remembers their counts.

#### E. Check whether a word already exists

```python
for i in range(len(unique_words)):
    if unique_words[i] == word:
        word_counts[i] = word_counts[i] + 1
        found = True
```

This checks whether the current word is already stored.

If it exists, its matching counter increases by one.

#### F. Add a new word

```python
if found == False:
    unique_words.append(word)
    word_counts.append(1)
```

If the word has not appeared before, we add it to the first list and add its initial count of 1 to the second list.

### Step 7: Edge-case tests

Try these inputs:

| Sentence | Expected result |
| --- | --- |
| "" | No words found |
| "Python" | python: 1 |
| "Cat, cat. CAT!" | cat: 3 |
| "the   cat   sat" | the: 1, cat: 1, sat: 1 |

What you learned: String processing, .lower(), .split(), character iteration, lists, .append(), nested loops, and counting.

## Final revision — All six exercises

You have now covered six different programming problems using the concepts from Module 1.1.

| Question | Main concept | Important Python features |
| --- | --- | --- |
| 1. Expenses | Running total and average | for, len(), functions |
| 2. Password | Validation and conditions | if, not, .isdigit() |
| 3. Traffic light | State modelling | Functions, conditions, state transitions |
| 4. Number counting | Iteration and selection | for, if, elif, counters |
| 5. Largest number | Best value so far | List indexing, loops, comparisons |
| 6. Word counting | Text processing and decomposition | .lower(), .split(), lists, nested loops |

## What I recommend you practise before moving forward

The most important thing is not copying these six solutions. It is understanding how to create them yourself.

For each question, you should be able to:

- Explain the problem in your own words.
- Identify the inputs and outputs.
- Identify assumptions and edge cases.
- Write pseudocode before Python.
- Explain every variable and function.
- Trace the code manually.
- Predict the output before executing it.
