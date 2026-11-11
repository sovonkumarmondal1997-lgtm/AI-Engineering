# Operators and Precedence

## Why this topic matters

Almost every decision a program makes — is this price too high, is this
user old enough, does this password contain a digit, has this value even
been set yet — comes down to combining values with **operators** and
getting a `True` or `False` answer. You have already used a few operators
informally in earlier lessons. This lesson gathers every operator a
beginner needs, explains exactly what each one does, and explains
**precedence**: the order Python uses to work out an expression that
combines several operators at once, so you can read complex-looking
conditions with confidence instead of guessing.

## Learning outcomes

By the end of this lesson, you will be able to:

- Use all seven arithmetic operators and explain the difference between
  `/`, `//`, and `%`.
- Use all six comparison operators to compare numbers and text.
- Combine conditions using `and`, `or`, and `not`, and explain how each one
  behaves.
- Use `in` and `not in` to check whether one piece of text appears inside
  another.
- Explain the difference between `==` and `is`, and state the one common
  beginner rule for when to use `is`.
- Explain what operator precedence is, and use parentheses to make an
  expression's order of operations unambiguous.

## Prerequisites

- [Variables, Basic Types, and None](02-variables-basic-types-and-none.md)
- [Sequence, Selection, Iteration, and Abstraction](../01-Computational-Thinking-and-Program-Design/04-sequence-selection-iteration-and-abstraction.md) —
  `if`, `elif`, `else`, and the comparison operators `==`, `!=`, `<`, `>`,
  `<=`, `>=` were first introduced there; this lesson gives them a complete,
  formal treatment alongside several new operator families.

## Key terms

| Term | Plain-English definition |
|---|---|
| **Operator** | A symbol or keyword, such as `+`, `==`, or `and`, that performs an operation on one or more values to produce a result. |
| **Operand** | A value that an operator works on — in `3 + 4`, both `3` and `4` are operands. |
| **Arithmetic operator** | An operator that performs a mathematical calculation, such as `+` or `*`. |
| **Comparison operator** | An operator that compares two values and produces `True` or `False`, such as `==` or `<`. |
| **Boolean operator** | An operator used to combine or invert conditions: `and`, `or`, and `not`. With `True`/`False` operands they give `True`/`False`; `and` and `or` can also return one of their operands. |
| **Membership operator** | An operator that checks whether one value appears inside another, such as `in`. |
| **Identity operator** | An operator that checks whether two references refer to the same object, such as `is`. |
| **Operator precedence** | The fixed order in which Python evaluates different operators when several appear in one expression. |

## Step-by-step explanation

### 1. Operators and operands, in one sentence

An **operator** is a symbol or keyword (such as `+` or `and`) that does
something with one or more **operands** (the values on either side of it). `3 + 4` has the operator
`+` and the operands `3` and `4`; the whole expression evaluates to `7`.

### 2. Arithmetic operators

| Operator | Meaning | Example | Result |
|---|---|---|---|
| `+` | Addition | `3 + 4` | `7` |
| `-` | Subtraction | `10 - 3` | `7` |
| `*` | Multiplication | `6 * 7` | `42` |
| `/` | Division (gives a `float` for `int` operands) | `7 / 2` | `3.5` |
| `//` | Floor division (divides, then rounds down) | `7 // 2` | `3` |
| `%` | Modulo (the remainder left over) | `7 % 2` | `1` |
| `**` | Exponentiation (raise to a power) | `2 ** 3` | `8` |

The three operators beginners most often mix up are `/`, `//`, and `%`.
For built-in `int` operands, `/` produces a `float`, even when the numbers
divide evenly (`8 / 2` is `4.0`, not `4`). `//` performs floor division: it divides and
rounds the result down toward negative infinity. For positive whole numbers
such as `7 // 2`, this gives `3` full groups, because `2` goes into `7`
three whole times. `%` gives whatever is left over after those full groups
are removed (`7 % 2` is `1`, because `3` groups of `2` use up `6`, leaving
`1`). With negative values, remember that floor division rounds toward
negative infinity rather than simply cutting off the decimal part: `-7 // 2`
is `-4`, not `-3`. For negative operands, the `%` result follows Python's
floor-division rule, so the sign may differ from the remainder convention
you may have seen in basic arithmetic. `//` and `%` are commonly used together — for example, to work out
how many full boxes of a fixed size you can fill, and how many items are
left over.

### 3. Comparison operators

| Operator | Meaning | Example | Result |
|---|---|---|---|
| `==` | Equal to | `5 == 5` | `True` |
| `!=` | Not equal to | `5 != 3` | `True` |
| `<` | Less than | `3 < 5` | `True` |
| `>` | Greater than | `5 > 3` | `True` |
| `<=` | Less than or equal to | `5 <= 5` | `True` |
| `>=` | Greater than or equal to | `5 >= 6` | `False` |

For the built-in comparisons used in this lesson, the result is a Boolean
value: `True` or `False`. As you learned in
[Values, Expressions, Statements, and Variables](../01-Computational-Thinking-and-Program-Design/02-values-expressions-statements-and-variables.md),
`=` performs **assignment** ("make this name refer to this value"), while
`==` performs **comparison** ("are these two values equal?"). Confusing
the two is one of the most common beginner mistakes in any language that
uses this pattern.

Comparing values of *different* types with `==` does not cause an error.
Values of different types can still compare equal when Python defines their
values as equal. For example, `1 == 1.0` is `True`. But a value such as `5`
is not equal to the string `"5"`, so `5 == "5"` is `False`:

```python
print(5 == "5")   # False — an int is not equal to a str, even a matching-looking one
print(1 == 1.0)   # True — an int and a float can have equal values
```

Comparing two strings works the same way. String equality checks whether
the text values match:

```python
print("python" == "python")   # True — the two text values match
```

Not every comparison operator works for every pair of operand types, though.
For example, ordering a string against an integer, such as `"5" < 5`,
raises a `TypeError`.

This is different from `+`, which raises a `TypeError` for the operand-type
combination `str + int`, as you saw in the previous lesson. The `+`
operator supports particular combinations of operand types. For example,
Python can add compatible numeric values, and it can concatenate strings.
It does not directly combine a `str` and an `int`.

Python also lets you chain comparisons, so `18 <= age < 65` is valid:

```python
age = 25
print(18 <= age < 65)   # True
```

This is a **chained comparison**. It means the same as
`18 <= age and age < 65`, without you having to repeat `age`.

### 4. Boolean operators: `and`, `or`, `not`

**Boolean operators** combine or invert conditions:

- `and` — the whole expression is `True` only if **both** sides are `True`.
- `or` — the whole expression is `True` if **at least one** side is `True`.
- `not` — flips `True` to `False`, and `False` to `True`.

```python
has_ticket = True
is_on_time = False
print(has_ticket and is_on_time)   # False, because both must be True
print(has_ticket or is_on_time)    # True, because at least one is True
print(not is_on_time)              # True, because is_on_time was False
```

That description is exactly right when both sides are `True` or `False`.
More precisely, `and` and `or` can return one of their operands. `and`
evaluates the left operand first and returns the first falsy operand;
otherwise it returns the last operand. `or` evaluates the left operand
first and returns the first truthy operand; otherwise it returns the last
operand. (Here, "falsy" values include `False`, `0`, `None`, and `""`;
every other value you have met so far is "truthy". You will study this
fully in a later lesson.)

```python
print(0 and "hello")         # 0
print("hello" and "world")   # world
print(0 or "fallback")       # fallback
print("hello" or "fallback") # hello
```

Both operators also **short-circuit**: Python may not evaluate the
right-hand operand when the result is already determined. `and` stops when
the left operand is falsy, and `or` stops when the left operand is truthy.
For example, in `False and x`, Python never even looks at `x`.

### 5. Membership operators: `in` and `not in`

The **membership operators** `in` and `not in` check whether one piece of
text appears inside another piece of text:

```python
print("cat" in "concatenate")    # True
print("dog" in "concatenate")    # False
print("dog" not in "concatenate")  # True
```

`in` and `not in` also work on other collections of data, such as lists,
which you will meet properly later in this module; for now, only use them
on text.

### 6. Identity operators: `is` and `is not`, and the `None` rule

The **identity operators** `is` and `is not` test whether two
references refer to the **same object** — a stricter, different question
from whether two values are merely *equal*. `==` asks "same value?"; `is`
asks "same object?". For most everyday
comparisons — numbers, text, `True`/`False` — you should use `==`, not
`is`.

There is exactly one common, important exception: **checking for `None`**.
Python guarantees there is only ever one single `None` object in your
entire program, so `is None` checks whether the name refers to the
singleton `None` object. That is the standard, expected way to test for
it:

```python
score = None
if score is None:
    print("No score has been recorded yet.")
```

**The beginner rule to remember:** use `==` to compare values, and use
`is` only when checking specifically for `None`. Writing `score == None`
usually still works, but `score is None` is what experienced Python code
uses, and is what you should get in the habit of writing.

### 7. Operator precedence: which operator runs first

When an expression combines several operators, Python evaluates them in a
fixed order, called **precedence** — not simply left to right. A simplified
precedence order for the operators covered in this lesson (not the complete
Python table), from highest priority (evaluated first) to lowest:

```text
1. Parentheses ( )
2. Exponent **
3. Negation (unary minus): -x
4. Multiplication, division, floor division, modulo: * / // %
5. Addition and subtraction: + -
6. Comparisons: == != < > <= >=, plus in, not in, is, is not
7. not
8. and
9. or
```

For example, `2 + 3 * 4` is `14`, not `20`, because `*` runs before `+`.
Two exponent details are worth knowing. `**` is evaluated right to left, so
`2 ** 3 ** 2` is read as `2 ** (3 ** 2)`, which is `512` (not
`(2 ** 3) ** 2`, which is `64`). And because `**` binds tighter than a
leading minus sign, `-2 ** 2` is read as `-(2 ** 2)`:

```python
print(-2 ** 2)    # -4
print((-2) ** 2)  # 4
```

In `(-2) ** 2`, the parentheses make `-2` the base.

`age >= 18 or age >= 13 and has_guardian` is read as
`age >= 18 or (age >= 13 and has_guardian)`, because `and` binds tighter
than `or`. Memorizing this whole table is not the goal — the goal is
knowing that this order exists, and using **parentheses** whenever there is
any doubt, both to force the order you actually want and to make the
expression instantly clear to a human reader, without them needing to
recall the table at all.

## Examples

### Example 1 — Arithmetic: splitting items into boxes

```python
total_items = 23
box_size = 4

full_boxes = total_items // box_size
leftover_items = total_items % box_size

print(full_boxes)
print(leftover_items)
```

**Plain-English explanation:**

- `total_items = 23` and `box_size = 4` store two whole numbers.
- `total_items // box_size` uses floor division to work out how many
  **whole** boxes of `4` fit into `23`: `4` goes into `23` five whole
  times (`5 * 4 = 20`), so `full_boxes` becomes `5`.
- `total_items % box_size` uses modulo to work out what is left over after
  those five full boxes are filled: `23 - 20 = 3`, so `leftover_items`
  becomes `3`.
- Running this prints `5` then `3`. Notice `//` and `%` are natural
  partners: one tells you the number of complete groups, the other tells
  you what remains — together they always account for the original total
  (`5 * 4 + 3 = 23`).

### Example 2 — Comparison, Boolean logic, and precedence together

```python
age = 15
has_guardian = True

is_eligible = age >= 18 or (age >= 13 and has_guardian)
print(is_eligible)
```

**Plain-English explanation:**

- `age = 15` and `has_guardian = True` store the two facts this decision
  depends on.
- `age >= 18` evaluates to `False` (15 is not 18 or more).
- `age >= 13 and has_guardian` evaluates to `True and True`, which is
  `True` (15 is 13 or more, and `has_guardian` is `True`).
- `False or True` evaluates to `True`, so `is_eligible` becomes `True`.
- The parentheses around `age >= 13 and has_guardian` were not strictly
  required here — as step 7 explained, `and` already runs before `or` by
  default — but they were added anyway, so a human reader does not have to
  recall the precedence table to understand the rule at a glance. This is
  the recommended habit: let parentheses state your intent directly, even
  when Python's default order would already agree with you.

### Example 3 — Membership and identity: checking a password and an optional value

```python
password = "hunter2"

has_digit = "2" in password
has_space = " " not in password
print(has_digit)
print(has_space)

discount_code = None
if discount_code is None:
    print("No discount code was entered.")
else:
    print("Discount code entered:", discount_code)
```

**Plain-English explanation:**

- `"2" in password` checks whether the character `"2"` appears anywhere
  inside the text stored in `password`. Since `"hunter2"` ends with `2`,
  this is `True`.
- `" " not in password` checks whether a space character does **not**
  appear inside `password`. Since `"hunter2"` contains no space, this is
  `True`.
- `discount_code = None` represents "no discount code has been entered
  yet," exactly as you practiced in the previous lesson.
- `if discount_code is None:` uses the identity operator specifically to
  check for `None`, following the beginner rule from step 6. Since
  `discount_code` really is `None`, this prints
  `No discount code was entered.` If `discount_code` had instead been
  reassigned to a real string such as `"SAVE10"` before this check, the
  `else` branch would run instead, printing
  `Discount code entered: SAVE10`.

## Common beginner mistakes

- **Confusing `=` and `==`.** `=` assigns a value to a name; `==` compares
  two values and produces `True` or `False`. Writing `if age = 18:` is a
  `SyntaxError` in Python — a helpful safeguard that stops you immediately.
- **Using `is` to compare ordinary values instead of `==`.** Writing
  `if age is 18:` may appear to work sometimes, purely by coincidence, but
  it is not the correct tool and can behave unpredictably. Use `==` for
  values; reserve `is` for checking `None`.
- **Assuming operators run strictly left to right.** Expressions such as
  `2 + 3 * 4` follow precedence rules, not left-to-right reading order;
  when in doubt, add parentheses rather than guessing.
- **Using `/` when a whole number was actually wanted.** `total // 4` gives
  a whole number of groups; `total / 4` gives a `float`, which is often not
  what you meant when counting discrete items such as boxes or people.
- **Writing `not x == y` instead of the clearer `x != y`.** Both work, but
  `!=` says the same thing more directly and is easier for a reader to
  scan.

## Try it yourself

1. A customer paid `50` for an item costing `37.5`. Compute and print how
   much change is owed, using `-`.
2. Invent your own discount rule using `and`/`or`, for example: a customer
   qualifies if they are a member, **or** if they have spent `100` or more
   in total. Write it as one Boolean expression and test it with a few
   different values.
3. A movie is `135` minutes long. Using `//` and `%`, compute and print how
   many whole hours that is, and how many minutes are left over.
4. Predict, then check: is `"5" == 5` `True` or `False`? Is `5 == 5`
   `True` or `False`? Write one sentence explaining why the two results
   differ.
5. Let `a = 4`, `b = 5`, and `c = 2`. Write the expression `a * b - c`
   with two different placements of parentheses (for example, around
   `a * b`, and separately around `b - c`). Evaluate both, and explain
   why the results differ when the grouping changes.

## Summary

- The **arithmetic operators** are `+`, `-`, `*`, `/`, `//`, `%`, and `**`;
  `/` gives a `float` for built-in `int` operands, `//` is floor division (it rounds down), and `%` gives
  the remainder.
- The **comparison operators** `==`, `!=`, `<`, `>`, `<=`, and `>=` produce
  a `bool` for the built-in comparisons used here; comparing values of
  different types with `==` does not raise an error, and can be `True`
  (`1 == 1.0`) or `False` (`5 == "5"`). Comparisons can be chained, as in
  `18 <= age < 65`.
- The **Boolean operators** `and`, `or`, and `not` combine or invert
  conditions; `and` and `or` can return one of their operands and
  short-circuit.
- The **membership operators** `in` and `not in`, used here on text, check
  whether one value appears inside another.
- The **identity operators** `is` and `is not` check whether two names
  refer to the same object; use `==` for ordinary comparisons and
  `is` only when checking for `None`.
- **Operator precedence** sets a fixed order of evaluation; parentheses
  override that order and make your intent explicit to any reader.

## Completion checklist

- [ ] I can use all seven arithmetic operators and explain the difference
      between `/`, `//`, and `%`.
- [ ] I can use all six comparison operators correctly.
- [ ] I can combine conditions with `and`, `or`, and `not`, and predict the
      result correctly.
- [ ] I can explain that `and` and `or` can return operands and can
      short-circuit.
- [ ] I can recognize a chained comparison such as `18 <= age < 65`.
- [ ] I can use `in` and `not in` to check whether text appears inside
      other text.
- [ ] I can explain the difference between `==` and `is`, and state the
      `None`-checking rule from memory.
- [ ] I can explain what operator precedence is and use parentheses to make
      an expression unambiguous.
- [ ] I have completed the "try it yourself" exercises above.

## Connection to later Applied AI and Agentic AI engineering work

The rule-based decision logic you will build later — deciding whether a
transaction looks risky, whether an AI agent has enough information to
proceed, or whether a tool's result counts as valid — is built almost
entirely out of exactly these operators: comparisons and Boolean logic
deciding which branch of code runs. The `is None` habit you practiced here
is exactly how you will later check, in much bigger programs, whether a
piece of data — a configuration value, an API field, a tool's response —
was actually supplied before your code tries to use it. Getting `==`
versus `is`, and operator precedence, right now prevents subtle logic bugs
that are far harder to track down once the surrounding code has grown much
larger.
