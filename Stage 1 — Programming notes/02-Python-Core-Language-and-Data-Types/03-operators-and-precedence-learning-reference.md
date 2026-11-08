# Python Operators and Precedence

**Complete lesson summary, Stage 1 level assessment, and solved
exercises**

Source: `03-operators-and-precedence.md`\
Curriculum: Stage 1 --- Programming & Computational Thinking

------------------------------------------------------------------------

## Part 1 --- Lesson summary (under 1,000 words)

### 1. What are operators and operands?

An **operator** is a symbol or keyword that performs an operation. An
**operand** is the value an operator works on. In `3 + 4`, `+` is the
operator and `3` and `4` are operands; the expression produces `7`.

The lesson covers arithmetic, comparison, Boolean, membership, and
identity operators, plus operator precedence.

### 2. Arithmetic operators

  Operator   Meaning                 Example   Result
  ---------- -------------------- ---------- --------
  `+`        Addition                `3 + 4`      `7`
  `-`        Subtraction            `10 - 3`      `7`
  `*`        Multiplication          `6 * 7`     `42`
  `/`        Division                `7 / 2`    `3.5`
  `//`       Floor division         `7 // 2`      `3`
  `%`        Remainder (modulo)      `7 % 2`      `1`
  `**`       Exponent/power         `2 ** 3`      `8`

Important differences:

-   With built-in integer operands, `/` produces a `float`: `8 / 2` is
    `4.0`.
-   `//` divides and rounds down toward negative infinity. `7 // 2` is
    `3`, while `-7 // 2` is `-4` (not `-3`).
-   `%` gives the remainder under Python's floor-division rule. For
    positive values, `7 % 2` is `1`.
-   `//` and `%` work naturally together: they tell you the number of
    complete groups and what remains.

### 3. Comparison operators

  Operator   Meaning                 Example    Result
  ---------- ----------------------- ---------- ---------
  `==`       Equal                   `5 == 5`   `True`
  `!=`       Not equal               `5 != 3`   `True`
  `<`        Less than               `3 < 5`    `True`
  `>`        Greater than            `5 > 3`    `True`
  `<=`       Less than or equal      `5 <= 5`   `True`
  `>=`       Greater than or equal   `5 >= 6`   `False`

These comparisons produce Boolean results. Remember: `=` assigns a
value; `==` compares values. `5 == "5"` is `False`, while `1 == 1.0` is
`True`. String equality checks whether text matches, for example
`"python" == "python"` is `True`. But ordering unlike types, such as
`"5" < 5`, raises `TypeError`. Python also supports chained comparisons:
`18 <= age < 65` means `18 <= age and age < 65`.

### 4. Boolean operators: `and`, `or`, `not`

-   `and`: both conditions must be true.
-   `or`: at least one condition must be true.
-   `not`: reverses a Boolean value.

``` python
has_ticket = True
is_on_time = False
print(has_ticket and is_on_time)  # False
print(has_ticket or is_on_time)   # True
print(not is_on_time)             # True
```

More precisely, `and` returns the first falsy operand, or the last
operand if all are truthy. `or` returns the first truthy operand, or the
last operand if none is truthy. Among values covered so far, `False`,
`0`, `None`, and `""` are falsy; other values encountered are truthy.

``` python
print(0 and "hello")          # 0
print("hello" and "world")    # world
print(0 or "fallback")        # fallback
print("hello" or "fallback")  # hello
```

They **short-circuit**: `False and x` does not evaluate `x`; similarly,
a truthy left operand means `or` need not evaluate its right operand.

### 5. Membership operators

`in` and `not in` check whether text occurs inside other text:

``` python
print("cat" in "concatenate")       # True
print("dog" in "concatenate")       # False
print("dog" not in "concatenate")   # True
```

They also work with collections such as lists, which are covered later;
this lesson uses them with strings.

### 6. Identity operators and `None`

`is` and `is not` ask whether two references point to the **same
object**. `==` asks whether values are equal. For normal values such as
numbers and text, use `==`, not `is`.

The important beginner exception is checking for `None`. Python has one
`None` object, so use `is None`:

``` python
score = None
if score is None:
    print("No score has been recorded yet.")
```

Rule: use `==` for ordinary value comparisons and `is` when checking
specifically for `None`. `score == None` often works, but
`score is None` is the standard habit.

### 7. Operator precedence

Precedence is Python's fixed evaluation order when an expression
contains multiple operators. Simplified order, highest to lowest:

1.  Parentheses `( )`
2.  Exponentiation `**`
3.  Unary minus `-x`
4.  `*`, `/`, `//`, `%`
5.  `+`, `-`
6.  Comparisons, membership, and identity (`==`, `!=`, `<`, `>`, `<=`,
    `>=`, `in`, `not in`, `is`, `is not`)
7.  `not`
8.  `and`
9.  `or`

Thus `2 + 3 * 4` is `14`, because multiplication happens first.
Exponentiation groups right to left: `2 ** 3 ** 2` means `2 ** (3 ** 2)`
and equals `512`. Exponentiation binds more tightly than a leading
minus:

``` python
print(-2 ** 2)    # -4: -(2 ** 2)
print((-2) ** 2)  # 4
```

Likewise, `age >= 18 or age >= 13 and has_guardian` groups as
`age >= 18 or (age >= 13 and has_guardian)`, because `and` has higher
precedence than `or`. Use parentheses to make intended grouping explicit
and easier for people to read.

### 8. All three lesson examples

**Example 1 --- Count complete boxes and leftovers**

``` python
total_items = 23
box_size = 4
full_boxes = total_items // box_size
leftover_items = total_items % box_size
print(full_boxes)
print(leftover_items)
```

`//` calculates five full boxes; `%` calculates three remaining items.
Output is `5` then `3`; `5 * 4 + 3 = 23`.

**Example 2 --- Eligibility decision**

``` python
age = 15
has_guardian = True
is_eligible = age >= 18 or (age >= 13 and has_guardian)
print(is_eligible)
```

`age >= 18` is `False`. The parenthesized condition is `True and True`,
hence `True`. `False or True` is `True`, so output is `True`.
Parentheses clarify the rule even though precedence would already
evaluate `and` first.

**Example 3 --- Password text and optional discount**

``` python
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

The character `"2"` is in the password, and a space is not, so the first
two outputs are `True` and `True`. Since `discount_code` is `None`, the
message `No discount code was entered.` prints. If it were reassigned to
`"SAVE10"`, the `else` branch would print
`Discount code entered: SAVE10`.

### 9. Common mistakes and key takeaways

Do not confuse assignment `=` with comparison `==`; `if age = 18:` is a
`SyntaxError`. Do not use `is` for ordinary values; use it for `None`.
Do not assume expressions run left to right; use parentheses when
unsure. Use `//` rather than `/` when counting whole groups. Prefer
`x != y` over `not x == y` because it is clearer.

These operators power later rule-based systems: transaction-risk
decisions, checking whether an AI agent has enough information, and
validating tool results. Correct comparisons, `is None`, and explicit
parentheses help prevent logic bugs.

------------------------------------------------------------------------

## Part 2 --- Current learning-level assessment from the Stage 1 project tree

The Stage 1 curriculum tree progresses from computational thinking and
program design to Python core language, control flow/functions,
collections and algorithmic habits, files and CLI programs,
modules/packages/code quality, testing/debugging, and object-oriented
design/data modelling. It also contains advanced Python and
production-oriented topics and applied projects, including a
data-quality/transformation pipeline and a rule-based risk-review
engine.

This operators lesson builds on variables/types and earlier
selection/condition concepts. It is foundational because later programs
use arithmetic for calculations, comparisons and Boolean logic for
decisions, membership for checking text, and identity checks for missing
optional values.

**Assessment:** A project tree shows the intended curriculum, not proof
that all topics have been completed or mastered. No independently
executed answers for this lesson's exercises have been supplied here.
Therefore, the defensible assessment is *beginner/foundational for this
topic, with practical mastery not yet verified*. The solutions below
stay within the lesson's concepts and its stated prerequisites; lists
and later topics are not required.

------------------------------------------------------------------------

## Part 3 --- All five exercises solved step by step (under 1,500 words)

### Exercise 1 --- Calculate change

``` python
amount_paid = 50
item_cost = 37.5
change_owed = amount_paid - item_cost
print(change_owed)
```

1.  `amount_paid = 50` stores the amount the customer paid (`int`).
2.  `item_cost = 37.5` stores the price (`float`).
3.  `amount_paid - item_cost` subtracts the price from the payment and
    stores the result.
4.  `print(change_owed)` displays the result.

Expected output:

``` text
12.5
```

The customer should receive 12.5 in the same currency units as the input
amounts.

### Exercise 2 --- Create and test a discount rule

Rule: a customer qualifies if they are a member **or** have spent at
least 100.

``` python
is_member = False
total_spent = 120
qualifies_for_discount = is_member or (total_spent >= 100)
print(qualifies_for_discount)

is_member = True
total_spent = 40
qualifies_for_discount = is_member or (total_spent >= 100)
print(qualifies_for_discount)

is_member = False
total_spent = 40
qualifies_for_discount = is_member or (total_spent >= 100)
print(qualifies_for_discount)
```

Line by line: `is_member` stores a Boolean; `total_spent` stores the
amount. `total_spent >= 100` checks the spending threshold. `or` means
either membership or reaching the threshold is sufficient. The
expression is assigned to `qualifies_for_discount` and printed. The next
two groups change the inputs and repeat the same test.

Expected output:

``` text
True
True
False
```

Case 1 qualifies by spending 120. Case 2 qualifies by membership. Case 3
meets neither condition.

### Exercise 3 --- Convert 135 minutes into whole hours and remaining minutes

``` python
total_minutes = 135
minutes_per_hour = 60
whole_hours = total_minutes // minutes_per_hour
remaining_minutes = total_minutes % minutes_per_hour
print(whole_hours)
print(remaining_minutes)
```

1.  Store 135 total minutes.
2.  Store 60 minutes per hour.
3.  `//` calculates the number of complete hours: `135 // 60` is `2`.
4.  `%` calculates what remains: `135 % 60` is `15`.
5.  Print both values.

Expected output:

``` text
2
15
```

So 135 minutes is 2 whole hours and 15 minutes.

### Exercise 4 --- Predict and check equality

Predictions:

-   `"5" == 5` is `False`, because `"5"` is a string and `5` is an
    integer.
-   `5 == 5` is `True`, because both values are equal integers.

Verify:

``` python
print("5" == 5)
print(5 == 5)
```

Expected output:

``` text
False
True
```

**Explanation:** quotation marks make `"5"` text; the unquoted `5` is a
number. Python does not treat these as equal, even though they look
similar.

### Exercise 5 --- Change grouping with parentheses

Given `a = 4`, `b = 5`, and `c = 2`:

``` python
a = 4
b = 5
c = 2

first_result = (a * b) - c
second_result = a * (b - c)

print(first_result)
print(second_result)
```

Line by line:

1.  The first three lines assign the requested integer values.
2.  `(a * b) - c` multiplies first: `4 * 5 = 20`, then subtracts 2,
    giving `18`.
3.  `a * (b - c)` evaluates the parentheses first: `5 - 2 = 3`, then
    multiplies by 4, giving `12`.
4.  The final two lines print both results.

Expected output:

``` text
18
12
```

**Why are the results different?** Parentheses change which operation is
performed first. In the first expression multiplication is grouped
before subtraction; in the second, subtraction is grouped before
multiplication. Parentheses make the intended calculation explicit.

------------------------------------------------------------------------

## Completion checklist

-   [ ] I can use `+`, `-`, `*`, `/`, `//`, `%`, and `**`.
-   [ ] I can explain `/` versus `//` versus `%`.
-   [ ] I can use all six comparison operators and distinguish `=` from
    `==`.
-   [ ] I can combine conditions using `and`, `or`, and `not`.
-   [ ] I understand operand-return behavior and short-circuiting at the
    introductory level.
-   [ ] I can use `in` and `not in` with text.
-   [ ] I know to use `==` for value comparisons and `is None` for
    checking `None`.
-   [ ] I understand precedence and can use parentheses to make grouping
    clear.
-   [ ] I have run all five exercises and checked the results.
