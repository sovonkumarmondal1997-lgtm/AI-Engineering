# Stage 1 — Topic 07: Pseudocode, Flowcharts, and Dry Runs
## Complete Study Guide, Level Assessment, and Solved Exercises

---

## Part 1 — Lesson summary (under 750 words)

### 1. Why plan before coding?
When you start coding immediately, you must solve two problems at once: deciding the algorithm and remembering Python syntax. Planning first separates them. You can change the logic quickly before worrying about colons, indentation, and exact Python grammar.

### 2. Key terms
- **Pseudocode:** A plan written in simple, structured English or code-like phrases. It explains the algorithm without requiring valid Python syntax.
- **Flowchart:** A diagram of an algorithm's steps and decisions. Boxes represent actions, diamonds (or labelled branches) represent decisions, and arrows show the order and loops.
- **Dry run:** Manually execute code line by line, recording how variables change, without running the program.
- **Trace table:** A table used during a dry run. It has a column for each important variable and rows for each step/state change.

### 3. Pseudocode
The lesson's style uses words such as `START`, `SET`, `FOR EACH`, `IF`, `RETURN`, and `END`:

```text
START
  SET total TO 0
  FOR EACH expense IN expenses
    ADD expense TO total
  END FOR
  RETURN total
END
```

This means: start with a total of zero; visit every expense; add it to the running total; return the final total. The structure maps naturally to Python, but does not require Python syntax while you are designing the logic.

### 4. Flowcharts
The same expense-total algorithm can be represented as:

```text
[Start]
   |
   v
[Set total = 0]
   |
   v
<More expenses?>
   | Yes                 | No
   v                     v
[Take next expense]  [Return total]
   |                     |
   v                     v
[Add expense to total] [End]
   |
   +-------- back to <More expenses?>
```

The loop-back arrow represents repetition. If the list is empty, the first decision is No and the function returns `0`. Flowcharts are particularly useful when a problem has multiple branches or repeated paths, because they help reveal missing or incorrect paths.

### 5. Dry runs and trace tables
A dry run follows every relevant statement in execution order. Track variables after each state change; do not skip lines that look unimportant. Dry runs help predict unfamiliar code and locate bugs by comparing actual traced values with expected values.

**Example 1 — Count values greater than 10**

```text
START
  SET count TO 0
  FOR EACH number IN numbers
    IF number > 10
      ADD 1 TO count
    END IF
  END FOR
  RETURN count
END
```

```python
def count_greater_than_10(numbers):
    count = 0
    for number in numbers:
        if number > 10:
            count = count + 1
    return count

print(count_greater_than_10([5, 15, 8, 20, 10]))
```

The pseudocode maps directly to Python: `SET` becomes assignment, `FOR EACH` becomes `for`, `IF` becomes `if`, and `ADD 1` becomes `count = count + 1`. Only `15` and `20` are strictly greater than 10; `10` does not qualify. Output: `2`.

**Example 2 — A deliberately tricky dry run**

```python
total = 0
count = 0
for number in [4, 7, 2, 9]:
    total = total + number
    count = count + 1
    if number > 5:
        total = total + 1

average = total / count
print(average)
```

| Iteration | number | total after addition | count | bonus? | total after bonus |
|---:|---:|---:|---:|---|---:|
| Start | — | — | 0 | — | 0 |
| 1 | 4 | 4 | 1 | No | 4 |
| 2 | 7 | 11 | 2 | Yes, +1 | 12 |
| 3 | 2 | 14 | 3 | No | 14 |
| 4 | 9 | 23 | 4 | Yes, +1 | 24 |

After the loop, `average = 24 / 4 = 6.0`, so output is `6.0`. A quick guess based only on the original numbers would give `5.5`; the dry run exposes the extra increments for 7 and 9.

**Example 3 — Find a bug manually**

```python
def count_positive_and_negative(numbers):
    positive_count = 0
    negative_count = 0
    for number in numbers:
        if number > 0:
            positive_count = positive_count + 1
        if number < 0:
            positive_count = positive_count + 1
    return positive_count, negative_count

print(count_positive_and_negative([3, -1, 5, -2, 0]))
```

The second `if` mistakenly increments `positive_count` instead of `negative_count`. The trace produces positive count `4` and negative count `0`; expected negative counts are `1` after `-1` and `2` after `-2`. Fix that line to `negative_count = negative_count + 1`. Comparing actual and expected columns pinpoints the error without executing the program.

### 6. Common mistakes and practical relevance
Avoid skipping planning, writing vague steps such as “do the calculation,” rushing a dry run, or tracing only normal inputs. Also dry-run edge cases such as empty lists and boundary values. These habits later help when tracing data pipelines and AI-agent decision loops: map the steps and decisions first, then follow state changes to find where actual behavior diverges from expected behavior.

---

## Part 2 — Current learning level and roadmap fit

Based on the Stage 1 project tree previously shared, the roadmap progresses from computational thinking and program design into Python fundamentals, control flow, collections, functions, files/CLI, testing, OOP, and production-oriented practices. Its practical work includes an expense-ledger CLI, log-investigation CLI, data-quality pipeline, and rule-based risk-review engine.

**Current assessment: foundational/beginner, progressing toward structured problem-solving.** The earlier lessons you worked through cover IPO, sequence/selection/iteration/functions, decomposition, preconditions/postconditions, and edge cases. Topic 07 builds directly on those skills: you now need to express a solution before coding and verify its behavior manually.

A project tree describes planned coverage; it does not prove mastery. The evidence of mastery for this topic is whether you can independently write precise pseudocode, represent decisions/loops in a flowchart, and produce an accurate trace table—including edge cases. The exercises below reinforce those skills without assuming advanced Python knowledge.

---

## Part 3 — Solved exercises (under 1,500 words)

### Exercise 1 — Find the largest number without `max()`

**Requirement:** The list is non-empty. Handle negative numbers correctly.

**Pseudocode**

```text
START
  SET largest TO the first number in numbers
  FOR EACH number IN numbers
    IF number > largest
      SET largest TO number
    END IF
  END FOR
  RETURN largest
END
```

**Python solution**

```python
def find_largest(numbers):
    largest = numbers[0]
    for number in numbers:
        if number > largest:
            largest = number
    return largest

print(find_largest([-8, -3, -12, -5]))
```

**Line by line**
1. `def find_largest(numbers):` defines a function receiving a list.
2. `largest = numbers[0]` starts with a real list value, not zero. This is essential: if every value is negative, starting at zero would give a wrong answer.
3. `for number in numbers:` visits each value.
4. `if number > largest:` checks whether the current value is larger.
5. `largest = number` updates the best value found so far.
6. `return largest` returns the final largest value.

**Output:** `-3`. No built-in `max()` is used. The list must contain at least one number, as specified.

### Exercise 2 — Password-length flowchart

**Requirement:** Ask for a password and report whether its length is at least 8. Exactly 8 must pass.

```text
             [Start]
                |
                v
        [Ask for password]
                |
                v
       [Get password length]
                |
                v
         <length >= 8?>
           /         \
         Yes          No
          |            |
          v            v
 [Print "Accepted:   [Print "Too short:
  at least 8"]       fewer than 8"]
          |            |
          v            v
         [End]        [End]
```

**Explanation:** First receive the password, then determine its length. The decision is `length >= 8`, not `length > 8`. Therefore lengths 8, 9, and above follow Yes; lengths 0 through 7 follow No. The two branches both reach an end, so no outcome is left undefined.

A direct Python translation would be:

```python
password = input("Enter password: ")
if len(password) >= 8:
    print("Accepted: at least 8")
else:
    print("Too short: fewer than 8")
```

`input()` reads the text; `len(password)` counts its characters; `if` chooses the branch; `else` handles every shorter length.

### Exercise 3 — Dry run the even/odd calculation

Given:

```python
values = [1, 2, 3, 4]
result = 0
for value in values:
    if value % 2 == 0:
        result = result + value
    else:
        result = result - value
print(result)
```

`%` is the remainder operator. A number is even when `value % 2 == 0`; otherwise this code treats it as odd and subtracts it.

| Step | value | Check | Operation | result |
|---:|---:|---|---|---:|
| Start | — | — | Set initial value | 0 |
| 1 | 1 | Odd (`1 % 2 = 1`) | `0 - 1` | -1 |
| 2 | 2 | Even (`2 % 2 = 0`) | `-1 + 2` | 1 |
| 3 | 3 | Odd (`3 % 2 = 1`) | `1 - 3` | -2 |
| 4 | 4 | Even (`4 % 2 = 0`) | `-2 + 4` | 2 |

**Predicted printed output:** `2`

**Line-by-line logic:** `values` stores the four inputs; `result = 0` initializes the accumulator; the `for` loop processes one value at a time; the `if` adds even values; `else` subtracts odd values; `print(result)` displays the final accumulator. The final arithmetic is `-1 + 2 - 3 + 4 = 2`.

### Exercise 4 — Find and fix the counter bug

**Original code**

```python
def count_words_longer_than(words, minimum_length):
    count = 0
    for word in words:
        if len(word) > minimum_length:
            count = count
    return count
```

**Bug:** `count = count` assigns the current value back to itself. It never increases the counter. When a qualifying word is found, the code must add one.

**Minimal correction**

```python
def count_words_longer_than(words, minimum_length):
    count = 0
    for word in words:
        if len(word) > minimum_length:
            count = count + 1
    return count

print(count_words_longer_than(["cat", "tiger", "ox"], 3))
```

**Line by line**
1. Define a function receiving a list of words and a minimum length.
2. Set `count` to zero because no qualifying words have been found yet.
3. Visit each word in the list.
4. `len(word) > minimum_length` checks the stated rule: strictly longer, not equal to.
5. `count = count + 1` increases the count for each qualifying word.
6. `return count` returns the number found.

**Check:** `"cat"` has length 3, so it does not qualify when the minimum is 3. `"tiger"` has length 5, so it qualifies and increases the count to 1. `"ox"` has length 2, so it does not qualify. Output: `1`. This verifies both a qualifying and a non-qualifying word.

---

## Completion checklist

- [ ] I can write pseudocode before translating it into Python.
- [ ] I can draw a flowchart with clearly labelled decisions and outcomes.
- [ ] I can trace every relevant variable change in execution order.
- [ ] I can compare actual and expected values to locate a bug.
- [ ] I can dry-run edge cases as well as normal inputs.
- [ ] I have completed all four exercises.

**Stop here and practise these skills before moving to the next lesson.**
