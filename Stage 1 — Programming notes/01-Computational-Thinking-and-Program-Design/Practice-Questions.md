# Stage 1 — Module 1.1: Six Practice Questions (No Functions)

**Important:** These solutions deliberately do not use `def`, function definitions, or function calls written by you. They use the beginner concepts practised in Module 1.1: variables, input/output, lists, sequence, `if` / `elif` / `else`, `for` and `while` loops, comparisons, string operations, counters, pseudocode, dry runs, and state.

Each code block is a separate program. Run one at a time.

## 1. Total and average of expenses

**Assumptions:** Zero is allowed; a negative amount represents a refund. An empty list has total `0`, but no defined average, so display a message instead.

**Pseudocode:** Start total at zero; add each expense; if there are no expenses, report no average; otherwise divide total by the number of expenses.

```python
expenses = [12, 45, 9, 20]
total = 0

for amount in expenses:
    total = total + amount

print("Total:", total)

if len(expenses) == 0:
    print("Average: cannot calculate an average for an empty list.")
else:
    average = total / len(expenses)
    print("Average:", average)
```

**Line by line:** `expenses` stores the input list. `total = 0` initializes the running total. The `for` loop takes each amount in turn. The indented statement adds that amount to `total`. `print` displays the total. `len(expenses)` gives the number of items. The `if` prevents division by zero; the `else` calculates and displays the average.

**Dry run:** `12 → 57 → 66 → 86`; there are 4 expenses; average = `86 / 4 = 21.5`.

**Tests:** Replace the list with `[]`, `[7]`, `[5, 5, 5]`, and `[0.001, 1000000]`. Expected totals/averages: empty → `0` / message; one item → `7` / `7.0`; same values → `15` / `5.0`.

## 2. Check password rules

**Rules chosen:** At least 8 characters, at least one digit, and no spaces. Check all rules and report every failure.

```python
password = input("Enter a password: ")
has_digit = False
has_space = False

for character in password:
    if character.isdigit():
        has_digit = True
    if character == " ":
        has_space = True

if len(password) >= 8 and has_digit == True and has_space == False:
    print("Password accepted.")
else:
    print("Password rejected.")
    if len(password) < 8:
        print("It must contain at least 8 characters.")
    if has_digit == False:
        print("It must contain at least one digit.")
    if has_space == True:
        print("It must not contain spaces.")
```

**Line by line:** `input()` reads the password as text. The two Boolean variables record whether a digit or space has been found; both start as `False`. The loop checks every character. `isdigit()` identifies a digit; the equality check identifies a space. The combined condition accepts only when all three rules pass. Otherwise, the nested `if` statements print each rule that failed.

**Tests:** `abc12345` passes; `abc1234` fails length; `abcdefgh` fails digit; `abc 12345` fails the no-space rule; an empty password fails length and digit. Exactly 8 characters passes if the other rules also pass.

## 3. Traffic-light state transitions

**Model:** Start at red. The only allowed transitions are red → green, green → yellow, and yellow → red. Requests that do not match are rejected and leave the state unchanged.

```python
state = "red"
requests = ["green", "yellow", "red", "yellow"]

for requested_state in requests:
    if state == "red" and requested_state == "green":
        state = "green"
        print("Accepted. Current state:", state)
    elif state == "green" and requested_state == "yellow":
        state = "yellow"
        print("Accepted. Current state:", state)
    elif state == "yellow" and requested_state == "red":
        state = "red"
        print("Accepted. Current state:", state)
    else:
        print("Rejected. Current state remains:", state)
```

**Line by line:** `state` stores the current state. `requests` stores the requested changes. The loop processes requests in order. Each `if` / `elif` checks both the current state and requested next state. Only a valid pair changes `state`. The final `else` rejects every other request and does not assign a new state, so the old state remains.

**Dry run:** red → green accepted; green → yellow accepted; yellow → red accepted; red → yellow rejected, state stays red.

**Tests:** The list above tests a full cycle and an invalid jump. Try `["yellow"]` from red to test immediate rejection. Try two full cycles to confirm repeated valid transitions work.

## 4. Count positive, negative, and zero numbers

**Assumptions:** Every list item is a number; decimals are allowed. An empty list should produce three zero counts.

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

**Line by line:** `numbers` is the input list. Each counter starts at zero because no items have been counted yet. The loop examines every number. A number greater than zero increments the positive counter. Otherwise, a number less than zero increments the negative counter. The `else` counts zero. The final lines display all three totals.

**Dry run:** For `[4, -2, 0, 7, -9, 0, 1]`, the result is positive `3`, negative `2`, zero `2`.

**Tests:** `[]` → `0, 0, 0`; `[1, 2]` → `2, 0, 0`; `[0, 0]` → `0, 0, 2`; `[-3]` → `0, 1, 0`.

## 5. Find the largest number without `max()`

**Assumptions:** An empty list has no largest value; display a message. For a non-empty list, start with its first item. This also works when every number is negative.

```python
numbers = [3, 9, 2, 9, 4]

if len(numbers) == 0:
    print("There is no largest number in an empty list.")
else:
    largest = numbers[0]

    for number in numbers:
        if number > largest:
            largest = number

    print("Largest number:", largest)
```

**Line by line:** The list stores the input. The `if` checks whether it is empty before accessing an item. Otherwise, `largest` starts as the first number. The loop compares each number with the best value found so far. If the current number is greater, it replaces `largest`. Finally, the largest value is displayed. Starting from the first item—not zero—is important for lists containing only negative values.

**Dry run:** Start `largest = 3`; see `9`, so update to 9; `2`, `9`, and `4` do not replace it. Result: `9`.

**Tests:** `[]` → message; `[6]` → `6`; `[3, 9, 2, 9, 4]` → `9`; `[-8, -2, -10]` → `-2`.

## 6. Count words, ignoring case and punctuation

**Assumptions:** Convert to lowercase and remove only comma, period, exclamation mark, question mark, colon, and semicolon. Use two lists: one for distinct words and one for matching counts. This avoids introducing dictionaries.

```python
sentence = "The cat sat. The cat sat on the mat!"
cleaned = sentence.lower()

for mark in ",.!?:;":
    cleaned = cleaned.replace(mark, "")

words = cleaned.split()
unique_words = []
word_counts = []

for word in words:
    found = False
    index = 0

    while index < len(unique_words):
        if unique_words[index] == word:
            word_counts[index] = word_counts[index] + 1
            found = True
        index = index + 1

    if found == False:
        unique_words.append(word)
        word_counts.append(1)

index = 0
while index < len(unique_words):
    print(unique_words[index], ":", word_counts[index])
    index = index + 1
```

**Line by line:** `lower()` makes capitalization consistent. The first loop removes each selected punctuation mark with `replace()`. `split()` separates the sentence into words and handles extra spaces. `unique_words` stores each word once; `word_counts` stores its count at the same position. For every word, `found` starts false and `index` starts at zero. The `while` loop searches existing words. If it finds a match, it increases the count at that position and sets `found` to true. If no match was found, the word and starting count `1` are appended to their respective lists. The final `while` loop prints each word with its matching count.

**Expected counts:** `the: 3`, `cat: 2`, `sat: 2`, `on: 1`, `mat: 1`.

**Tests:** `""` prints no word rows; `"Hello"` → `hello: 1`; `"Cat, cat. CAT!"` → `cat: 3`; `"one   two one"` → `one: 2`, `two: 1`.

---

## Your current learning level

These solutions stay within the procedural concepts of Module 1.1 and deliberately avoid function definitions. Q1 practises running totals; Q2 selection and Boolean flags; Q3 state transitions; Q4 counters; Q5 the “best so far” pattern; Q6 string processing, lists, and nested iteration.

The roadmap shows the topics you are studying, not automatic proof of mastery. Before moving to Module 1.2, practise recreating these programs from a blank file and explaining each variable, condition, and loop. Do not worry about functions or dictionaries yet; learn them when they appear in your sequence.
