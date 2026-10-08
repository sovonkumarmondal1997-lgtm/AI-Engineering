# Strings: Indexing, Slicing, and Formatting

## Why strings matter

Text is everywhere in real programs: a user's name, a password, a file
name, a product description, a line from a log file, a message an AI model
sends back. In Python, all of this text is represented by one type you
already met briefly — `str` — and this lesson is where you learn to work
with it properly. You will learn how to build strings, pull pieces out of
them precisely, glue them together, format them for clean output, and use
the large toolbox of built-in string methods Python provides. Strings are
also where you will first practice **indexing** and **slicing** — two
skills that reappear, almost unchanged, once you study lists in the next
topic.

## Learning outcomes

By the end of this lesson, you will be able to:

- Create strings with single quotes, double quotes, and triple quotes, and
  explain when each is useful.
- Use escape sequences to include newlines, tabs, quotation marks, and
  backslashes inside a string.
- Explain why strings are immutable, and why string methods that transform
  text return a new string instead of changing the original.
- Read a single character out of a string using zero-based, positive, and
  negative indexes, and explain why `IndexError` happens.
- Extract a piece of a string using slicing, including omitted start/stop
  values, negative indexes, step values, and reversing text.
- Combine strings with concatenation and repetition, measure their length,
  and check whether one string contains another.
- Build formatted output using f-strings (the modern, preferred approach),
  `str.format()`, and recognize (but avoid) old-style `%` formatting.
- Explain, at a beginner level, why Python strings can safely contain
  accented letters, other scripts, and emoji, and why `casefold()` can be a
  better choice than `lower()` when comparing text.
- Use the most common `str` methods confidently, and know how to look up
  any other method in the appendix at the end of this lesson.

## Prerequisites

- [Operators and Precedence](03-operators-and-precedence.md)
- [Values, Expressions, Statements, and Variables](../01-Computational-Thinking-and-Program-Design/02-values-expressions-statements-and-variables.md) —
  this lesson directly continues the immutability idea first shown there
  with `name.upper()`.

## Key terms

| Term | Plain-English definition |
|---|---|
| **String (`str`)** | Python's text type: a sequence of characters written between quotation marks. |
| **Character** | One single letter, digit, symbol, or space inside a string. |
| **Method** | A named action attached to a value, called with a dot, such as `text.upper()`. |
| **Index** | A whole number that identifies one character's position inside a string. |
| **Zero-based indexing** | Python's rule that the first character of a string is at position `0`, not `1`. |
| **Negative index** | An index counted from the end of a string backward, where `-1` is the last character. |
| **`IndexError`** | The error Python raises when you ask for a position that does not exist in a string. |
| **Slice** | A piece of a string extracted using `[start:stop]` or `[start:stop:step]`. |
| **Step** | The third slicing value, controlling how many positions to move forward (or backward) between each character kept. |
| **Immutable** | Unable to be changed in place; every string "change" actually produces a brand-new string. |
| **Escape sequence** | A backslash (`\`, the escape character) followed by a letter or symbol, representing a character that is hard or impossible to type directly, such as `\n` for a new line. |
| **Concatenation** | Joining two or more strings together, usually with `+`. |
| **Membership** | Checking whether one piece of text exists inside another, using `in` or `not in`. |
| **f-string** | A string written as `f"..."` that can evaluate Python expressions directly inside `{ }`. |
| **Placeholder** | The `{ }` part inside an f-string or a `str.format()` template, which gets replaced by a real value. |
| **Format specifier** | Extra instructions after a `:` inside a placeholder, controlling how a value is displayed (decimal places, width, alignment, and so on). |
| **Unicode** | The standard Python uses internally to represent virtually every character from every human language, plus symbols and emoji, consistently. |
| **Case folding** | An aggressive form of lowercasing, done by `casefold()`, designed specifically to make text comparison more reliable across languages. |
| **Prefix** | The characters at the very start of a string. |
| **Suffix** | The characters at the very end of a string. |

## Step-by-step explanation

### 1. Creating strings: single, double, and triple quotes

A **string** is text written between matching quotation marks. Python
accepts three styles:

```python
greeting_a = 'Hello'
greeting_b = "Hello"
```

Single quotes and double quotes work identically — pick one style and stay
consistent within a project. This course uses double quotes. One practical
reason to keep both available: if your text itself contains one kind of
quote mark, use the other kind to wrap it, avoiding extra escaping (covered
next).

**Triple quotes** (`"""..."""` or `'''...'''`) create a string that can
span multiple lines exactly as typed, including the line breaks:

```python
message = """This is
a multi-line
string."""
print(message)
```

```text
This is
a multi-line
string.
```

Triple-quoted strings are useful for longer blocks of text, such as a
multi-line message to print, without manually inserting line-break
characters.

### 2. Escape sequences

The backslash (`\`) is the **escape character**. An **escape sequence** is
a backslash followed by another character, representing something you
cannot (or would rather not) type directly inside a string:

| Escape sequence | Meaning |
|---|---|
| `\n` | New line |
| `\t` | Tab |
| `\"` | A literal double-quote character, inside a double-quoted string |
| `\'` | A literal single-quote character, inside a single-quoted string |
| `\\` | A single literal backslash |

```python
print("Line one\nLine two")
print("Name:\tAda")
print("She said \"hello\"")
print('It\'s sunny today')
print("Backslash: \\")
```

```text
Line one
Line two
Name:	Ada
She said "hello"
It's sunny today
Backslash: \
```

Notice the third line: because the string itself was wrapped in double
quotes, the double quotes *inside* the text had to be escaped with `\"` so
Python knows they are part of the text, not the end of the string. The
fourth line shows the easier alternative: since that string was wrapped in
*single* quotes, only the apostrophe (a single quote) needed escaping.

#### Raw strings

When backslashes are common, a **raw string literal** — written with an `r`
before the opening quote — is easier, because ordinary escape sequences
such as `\n` and `\t` are not interpreted in the same way:

```python
normal_path = "C:\\Users\\Ada"
raw_path = r"C:\Users\Ada"

print(normal_path)
print(raw_path)
```

```text
C:\Users\Ada
C:\Users\Ada
```

Raw strings are particularly useful for Windows-style paths and for
regular-expression patterns (which this course does not cover here).

### 3. Strings are immutable

As you briefly saw in
[Values, Expressions, Statements, and Variables](../01-Computational-Thinking-and-Program-Design/02-values-expressions-statements-and-variables.md),
strings in Python are **immutable**: once created, a string's own
characters can never be changed in place. String methods do not mutate the original
string. A method that seems to "transform" text — making it uppercase,
replacing a word, trimming spaces — builds and returns a resulting string,
leaving the original completely untouched. (Other methods return other
types: `"hello".count("l")` returns an `int`, `"hello".isalpha()` returns a
`bool`, and `"a b".split()` returns a list.)

```python
name = "sam"
name.upper()
print(name)          # still "sam" — upper() built a new string and threw it away

name = name.upper()
print(name)          # "SAM" — only now, because we reassigned the name
```

The first `name.upper()` call does compute `"SAM"`, but since nothing
captures that result, it is calculated and discarded. Only the second line,
which reassigns `name` to the method's return value, actually changes what
`name` points to. The habit to build is: **read the method's result, and if you want to
keep it, assign it to a variable.**

### 4. String indexing

Every character in a string has a numbered position, called an **index**.
Python uses **zero-based indexing**: the first character is at position
`0`, the second at position `1`, and so on.

```python
word = "python"
print(word[0])    # p  (first character)
print(word[-1])   # n  (last character)
print(word[-2])   # o  (second-to-last character)
```

Python also supports **negative indexes**, counting backward from the end:
`-1` is always the last character, `-2` the one before it, and so on. This
is often more convenient than calculating `len(word) - 1` to reach the last
character.

**`IndexError`:** asking for a position that does not exist raises an
error and stops the program:

```python
word = "python"
print(word[10])
```

```text
IndexError: string index out of range
```

`"python"` only has valid indexes `0` through `5` (and `-1` through `-6`);
position `10` does not exist.

**Safe reasoning before accessing a position:** before indexing into a
string using a position you calculated (rather than typed directly), check
that the position is actually within range using `len()` and a comparison,
both of which you already know:

```python
username = "ada"
position = 10

if position < len(username):
    print(username[position])
else:
    print("That position does not exist in this text.")
```

### 5. String slicing

**Slicing** extracts a piece of a string using `[start:stop]`. It returns
every character from index `start` up to, but **not including**, index
`stop`.

```python
word = "python"
print(word[0:3])   # pyt   — indexes 0, 1, 2
print(word[2:])    # thon  — start at 2, go to the end
print(word[:4])    # pyth  — start at the beginning, stop before 4
print(word[:])     # python — the whole string, start to end
```

**Why the stop position is excluded:** this design makes the *length* of a
slice easy to compute — `word[0:3]` has exactly `3 - 0 = 3` characters —
and makes adjacent slices line up cleanly, since `word[0:3]` and
`word[3:6]` together cover the whole string with no overlap and no gap.

Slicing also accepts **negative indexes**, counting from the end, exactly
like single-character indexing:

```python
word = "python"
print(word[-3:])   # hon  — the last three characters
```

A third value, the **step**, controls how many positions to move between
each character kept: `word[start:stop:step]`.

```python
word = "python"
print(word[::2])    # pto      — every second character
print(word[::-1])   # nohtyp   — the whole string, reversed
```

`word[::2]` omits both `start` and `stop`, meaning "the whole string," and
uses a step of `2` to keep every other character. `word[::-1]` is the
standard, idiomatic way to reverse a string in Python: a step of `-1` walks
backward through the entire string, one character at a time, from the last
character to the first.

### 6. Concatenation, repetition, length, and membership

Four operations you already partly know, applied specifically to strings:

```python
first = "Py"
second = "thon"
print(first + second)      # Python   — concatenation: joining strings with +
print("ha" * 3)             # hahaha   — repetition: repeating a string with *
print(len("python"))        # 6        — length: how many characters
print("th" in "python")     # True     — membership: does "th" appear inside?
print("xy" not in "python") # True     — the opposite check
```

`+` between two strings joins them; `*` between a string and an `int`
repeats it that many times. `len()` and `in`/`not in`, first introduced in
earlier lessons, work on strings exactly as you would expect: `len()`
counts characters, and `in`/`not in` check whether one piece of text
appears anywhere inside another.

### 7. String formatting

Formatting means building a piece of output text that combines fixed
wording with values that can change — a name, a price, a percentage.

#### f-strings: the modern, preferred approach

An **f-string** is written as `f"..."`. Anything inside `{ }` is treated as
a real Python expression, evaluated and inserted into the text:

```python
name = "Ada"
age = 30
print(f"{name} is {age} years old.")
```

```text
Ada is 30 years old.
```

For ordinary application output and string construction, f-strings are
the preferred modern approach — they are the clearest to read.

#### Formatting numbers with a format specifier

After the expression inside `{ }`, a colon (`:`) introduces a **format
specifier** — extra instructions about exactly how to display the value:

```python
price = 1234.5
print(f"{price:.2f}")     # 1234.50   — exactly 2 decimal places
print(f"{price:,.2f}")    # 1,234.50  — thousands comma, 2 decimal places

ratio = 0.4567
print(f"{ratio:.1%}")     # 45.7%     — as a percentage, 1 decimal place

label = "Total"
print(f"[{label:>10}]")   # [     Total]  — right-aligned, width 10
print(f"[{label:<10}]")   # [Total     ]  — left-aligned, width 10
print(f"[{label:^10}]")   # [  Total   ]  — centered, width 10
```

Reading these specifiers: `.2f` means "fixed-point notation with 2 digits
after the decimal point"; adding a comma before it (`,.2f`) inserts
thousands separators; `.1%` multiplies by 100, adds a `%` sign, and shows 1
decimal place; `>`, `<`, and `^` control alignment (right, left, centered)
within a fixed total width, here `10` characters.

#### `str.format()`: positional and named placeholders

Before f-strings existed, and still common in code you may read,
`str.format()` fills in `{ }` **placeholders** from arguments passed to
`.format(...)`:

```python
name = "Ada"
age = 30
print("{} is {} years old.".format(name, age))       # positional
print("{n} is {a} years old.".format(n=name, a=age))  # named
```

Both lines print `Ada is 30 years old.`. The first fills placeholders in
order; the second matches each placeholder to a named argument, which can
make longer templates easier to follow.

#### Old-style `%` formatting (recognize it, do not use it)

You may encounter one more style in older Python code:

```python
name = "Ada"
age = 30
print("%s is %d years old." % (name, age))
```

This also prints `Ada is 30 years old.` — `%s` stands for "insert as text"
and `%d` for "insert as a whole number." This style predates both
f-strings and `str.format()`. You only need to **recognize** it when
reading existing code; do not use it in new code you write, since
f-strings are clearer and less error-prone.

### 8. Unicode awareness

Python strings are built on **Unicode**, a single standard that can
represent virtually any character from any human language, along with
symbols and emoji, all inside an ordinary `str`:

```python
greeting = "café ☕ こんにちは 🐍"
print(greeting)
print(len(greeting))
```

```text
café ☕ こんにちは 🐍
14
```

You do not need to do anything special to use accented letters, other
scripts, or emoji — they are just characters, like any other. (How these
characters get converted into bytes for storage or network transfer is a
separate topic, **encoding**, which you will study properly in Module 1.5;
for now, just know that ordinary text handling in Python already fully
supports this.)

**Case sensitivity** applies to every character, including accented ones:
`"Café"` and `"café"` are different strings, and `==` treats them as
unequal.

**Why `casefold()` can beat `lower()`:** both lowercase text, but
`casefold()` is more aggressive and is specifically designed for reliably
*comparing* text across languages. A well-known example is the German
letter `ß`:

```python
word = "straße"
print(word.lower())      # straße   — unchanged; ß is already "lowercase"
print(word.casefold())   # strasse  — ß expanded to "ss" for comparison
```

If you were comparing user-entered text where `"straße"` and `"strasse"`
should reasonably be treated as the same word, comparing with `casefold()`
on both sides catches this; comparing with `lower()` would not. As a
practical rule: use `lower()` for everyday display purposes, and prefer
`casefold()` specifically when the goal is comparing two pieces of text for
equality, especially text that might not be plain English.

## Examples

### Example 1 — Building a display name from parts

```python
first_name = "ada"
last_name = "lovelace"

full_name = first_name.title() + " " + last_name.title()
initials = first_name[0].upper() + last_name[0].upper()

print(f"Hello, {full_name}!")
print(f"Initials: {initials}")
```

**Plain-English explanation:**

- `first_name` and `last_name` store lowercase text, as if typed carelessly
  into a form.
- `.title()` is a string method (covered fully in the appendix) that
  capitalizes the first letter of each word; `first_name.title()` turns
  `"ada"` into `"Ada"`.
- `full_name = first_name.title() + " " + last_name.title()` concatenates
  three pieces — the capitalized first name, a literal space, and the
  capitalized last name — into one string, `"Ada Lovelace"`.
- `initials = first_name[0].upper() + last_name[0].upper()` uses indexing
  (`[0]`, the first character of each name) followed by `.upper()`, then
  concatenates the two single-letter results together.
- The f-strings display both results:
  `Hello, Ada Lovelace!` and `Initials: AL`.
- This example combines indexing, concatenation, and two string methods to
  turn messy input into clean, presentable output — a very common pattern.

### Example 2 — Cleaning and validating a username

```python
raw_input_value = "  Ada_2024  "

username = raw_input_value.strip()
print(username)

if username.isalnum():
    print("Username is valid (letters and numbers only).")
else:
    print("Username contains characters other than letters and numbers.")
```

**Plain-English explanation:**

- `raw_input_value` simulates text a user typed, with extra spaces at both
  ends — a very realistic situation.
- `.strip()` returns a new string with leading and trailing whitespace
  removed (but leaves internal characters alone), so `username` becomes
  `"Ada_2024"`.
- `.isalnum()` checks whether **every** character in the string is a
  letter or a digit, returning `True` or `False`. Because `"Ada_2024"`
  contains an underscore (`_`), which is neither a letter nor a digit,
  `.isalnum()` returns `False`.
- The `if`/`else` (already familiar from Module 1.1) picks the matching
  message. Running this prints `Ada_2024`, then
  `Username contains characters other than letters and numbers.`
- This example shows the common real pattern: clean the text first
  (`.strip()`), then check a property of the cleaned result
  (`.isalnum()`), rather than trusting raw input directly.

### Example 3 — Formatting a receipt line

```python
item_name = "Wireless Mouse"
unit_price = 24.5
quantity = 3
tax_rate = 0.08

subtotal = unit_price * quantity
tax = subtotal * tax_rate
total = subtotal + tax

print(f"{item_name:<20}{quantity:>3} x ${unit_price:>6.2f}")
print(f"Subtotal: ${subtotal:,.2f}")
print(f"Tax ({tax_rate:.0%}): ${tax:,.2f}")
print(f"Total:    ${total:,.2f}")
```

**Plain-English explanation:**

- Four values describe one line item: its name, its unit price, how many
  were bought, and the tax rate to apply.
- `subtotal`, `tax`, and `total` are computed using ordinary arithmetic
  operators from the previous lesson.
- The first `print` uses three format specifiers in one line:
  `{item_name:<20}` left-aligns the name in a 20-character-wide field,
  `{quantity:>3}` right-aligns the quantity in a 3-character field, and
  `{unit_price:>6.2f}` right-aligns the price in a 6-character field with
  exactly 2 decimal places — together producing neatly lined-up columns.
- The remaining lines use `,.2f` to show dollar amounts with a thousands
  separator and 2 decimal places, and `.0%` to show the tax rate as a
  whole-number percentage.
- Running this prints:

  ```text
  Wireless Mouse        3 x $ 24.50
  Subtotal: $73.50
  Tax (8%): $5.88
  Total:    $79.38
  ```

- This is the payoff of format specifiers: precise, predictable,
  professional-looking output built from a handful of numbers, without
  manually counting spaces or rounding numbers by hand.

## Common beginner mistakes

- **Expecting a string method to change the original variable.** As
  Section 3 showed, `text.upper()` alone does nothing to `text`; you must
  write `text = text.upper()` to keep the result.
- **Off-by-one errors in slicing.** Forgetting that `word[0:3]` stops
  *before* index `3`, not at it, is one of the most common slicing
  mistakes — when in doubt, count carefully or test in the REPL.
- **Indexing past the end of a string.** `word[len(word)]` is always one
  position too far and raises `IndexError`; the last valid index is
  `len(word) - 1`, or simply `word[-1]`.
- **Forgetting to escape quotation marks that match the string's own
  quotes.** `"She said "hi""` is invalid; either escape the inner quotes
  (`"She said \"hi\""`) or switch the outer quotes to the other style
  (`'She said "hi"'`).
- **Using `==` to compare text that might differ only in case or
  accents**, instead of normalizing both sides first with `.casefold()` (or
  at least `.lower()`) before comparing.
- **Reaching for old-style `%` formatting or manual `+` concatenation for
  new code**, instead of an f-string, which is clearer and less error-prone
  for combining text and values.

## Try it yourself

Do not look up full solutions. Predict the output before running each one.

1. Given `word = "elephant"`, write expressions (without running them
   first) for: the first character, the last character, and the substring
   `"phan"`. Then check yourself.
2. Write a one-line slice expression that reverses the string
   `"Applied AI"`.
3. Given `sentence = "  Data Science and AI  "`, clean it with `.strip()`,
   then print its length before and after cleaning to see how many
   whitespace characters were removed.
4. Using f-string format specifiers, print the number `7` as a
   two-digit, zero-padded string (hint: look at `zfill()` and the `0`
   format specifier in the appendix), and print `0.256` as a percentage
   with one decimal place.
5. Write a short program that takes a made-up sentence, counts how many
   times the letter `"a"` appears (case-insensitively — think about which
   method to apply first), and prints the count.
6. Using the appendix, find one method you have not used before, write a
   two-line example with it, and explain in one sentence what it does.

## Summary

- Strings can be created with single quotes, double quotes, or triple
  quotes (for multi-line text); pick one quote style and stay consistent.
- Escape sequences, such as `\n` and `\t`, let you include characters
  that are otherwise hard to type directly inside a string.
- Strings are immutable, so string methods do not modify the original
  string. Methods that produce changed text return a new string result that
  can be assigned or otherwise used.
- Indexing (`word[0]`, `word[-1]`) reads one character by position, using
  zero-based, optionally negative, indexes; an out-of-range index raises
  `IndexError`.
- Slicing (`word[start:stop:step]`) extracts a range of characters; the
  stop position is always excluded, and a step of `-1` reverses a string.
- Strings support concatenation (`+`), repetition (`*`), length (`len()`),
  and membership checks (`in`, `not in`).
- f-strings are the modern, preferred way to format output, including
  precise control over decimal places, thousands separators, percentages,
  width, and alignment; `str.format()` is a common older alternative, and
  `%` formatting is legacy syntax to recognize but not use.
- Python strings natively support accented letters, other scripts, and
  emoji through Unicode; `casefold()` is generally more reliable than
  `lower()` when the goal is comparing text for equality.

## Completion checklist

- [ ] I can create strings with all three quoting styles and explain when
      to use each.
- [ ] I can use at least five escape sequences correctly.
- [ ] I can explain, using my own words, why strings are immutable and why
      `text.upper()` alone does not change `text`.
- [ ] I can index a string with positive and negative positions and
      explain why an index can go out of range.
- [ ] I can write a slice with a start, a stop, and a step, and reverse a
      string using slicing.
- [ ] I can combine strings with `+` and `*`, and check membership with
      `in`.
- [ ] I can format output with f-strings, including at least one number
      format specifier (decimals, commas, percentage, width, or
      alignment).
- [ ] I can explain the difference between `lower()` and `casefold()`.
- [ ] I have completed the "try it yourself" exercises above.
- [ ] I know the appendix exists and can find a method in it when I need
      one I have not memorized.

## Connection to later Applied AI and Agentic AI engineering work

Almost every AI system you build later is, underneath, a text-processing
system: prompts are strings, model responses are strings, tool arguments
and results are usually passed as strings (or formats built out of
strings), and log messages you will depend on for debugging are strings
too. The exact skills from this lesson — slicing out a relevant piece of
text, cleaning input with `.strip()`, checking content with `.isalnum()` or
similar, and building precisely formatted output with f-strings — are
skills you will use constantly when constructing prompts, parsing model
output, and presenting results to a user. The Unicode awareness from
Section 8 also matters directly: real user input and real AI-generated
text will routinely include accents, other scripts, and emoji, and code
that only expects plain English text will break in exactly the ways this
lesson warned about.

---

## Appendix: Complete `str` Method Reference

This appendix was generated against the Python version installed in this
environment — check `python3 --version` yourself if you want to confirm
your own. Run `python3 -c "print([m for m in dir(str) if not m.startswith('_')])"`
in a terminal at any time to list every public method your own installed
Python provides; recent Python versions add methods only rarely, so this
list should match almost any modern Python 3 install.

**You do not need to memorize this appendix.** Read through it once to
know what exists, get comfortable with the methods marked as especially
common in the main lesson above, and come back to this appendix as a
reference whenever you need a method you do not use every day. Every
entry below is a public method of `str` — almost all are instance methods,
called on a particular string, while `maketrans()` is a static helper
called on the `str` type itself. None of Python's internal "dunder" methods (like `__add__`) or private methods are included,
since you call those indirectly through operators, not directly by name.

A few methods below (`join`, `split`, `partition`) naturally return a
**list** or a **tuple** — a small bundle of several values. Lists are
covered fully in [Topic 5](05-lists-mutation-copying-and-aliasing.md) and
tuples in [Topic 6](06-tuples-and-unpacking.md); here, the examples simply
print the result so you can see the shape of what comes back, without yet
learning to manipulate it further.

### Case conversion

#### `capitalize()`

Returns a new string with only the first character uppercase and every
other character lowercase.

```python
print("hello world".capitalize())   # Hello world
```

Note: unlike `.title()` below, only the very first letter of the whole
string changes — not the first letter of every word.

#### `casefold()`

Returns an aggressively lowercased version of the string, designed for
reliable text comparison rather than display. Covered in detail in
Section 8.

```python
print("straße".casefold())   # strasse
```

#### `lower()`

Returns a new string with every character lowercase.

```python
print("HELLO World".lower())   # hello world
```

Use case: normalizing text before comparing it, such as
`answer.lower() == "yes"`.

#### `upper()`

Returns a new string with every character uppercase.

```python
print("hello world".upper())   # HELLO WORLD
```

#### `swapcase()`

Returns a new string with every uppercase character made lowercase, and
every lowercase character made uppercase.

```python
print("Hello World".swapcase())   # hELLO wORLD
```

#### `title()`

Returns a new string with the first letter of each word uppercase and the
rest lowercase — useful for names and titles.

```python
print("hello world".title())   # Hello World
```

Warning: `.title()` capitalizes after *any* non-letter character, so
`"it's a party".title()` produces `"It'S A Party"` — the apostrophe counts
as a word break. Check results carefully with real-world text.

### Trimming and padding

#### `strip()`

Returns a new string with leading and trailing whitespace removed. Can
also take a string of characters to remove instead of whitespace.

```python
print(repr("  Hello, World!  ".strip()))   # 'Hello, World!'
print("xxHelloxx".strip("x"))              # Hello
```

A note on `repr()`: it produces a developer-oriented representation of a
value, which is useful for making things such as surrounding spaces and
escape characters visible. Compare:

```python
text = "  Hello  "
print(text)
print(repr(text))
```

```text
  Hello  
'  Hello  '
```

Use case: cleaning up user-typed text before validating or storing it, as
shown in Example 2 above.

#### `lstrip()`

Like `strip()`, but only removes from the left (start) side.

```python
print(repr("  Hello, World!  ".lstrip()))   # 'Hello, World!  '
```

#### `rstrip()`

Like `strip()`, but only removes from the right (end) side.

```python
print(repr("  Hello, World!  ".rstrip()))   # '  Hello, World!'
```

#### `zfill(width)`

Returns a new string padded with leading zeros until it reaches the given
total length; correctly keeps a leading `-` sign at the very front.

```python
print("42".zfill(5))    # 00042
print("-42".zfill(5))   # -0042
```

Use case: formatting numbers like invoice IDs or time components (`"7"` →
`"07"`) that should always show a fixed number of digits.

### Searching and counting

#### `count(substring)`

Returns how many non-overlapping times `substring` appears.

```python
print("banana".count("a"))    # 3
```

#### `find(substring)`

Returns the index of the first occurrence of `substring`, or `-1` if it is
not found. `find()` returns `-1` when the substring is not found rather
than raising `ValueError`.

```python
print("banana".find("na"))   # 2
print("banana".find("zz"))   # -1
```

#### `rfind(substring)`

Like `find()`, but searches from the right and returns the index of the
*last* occurrence, or `-1` if not found.

```python
print("banana".rfind("na"))   # 4
```

#### `index(substring)`

Like `find()`, but raises `ValueError` instead of returning `-1` when the
substring is not found.

```python
print("banana".index("na"))   # 2
```

Warning: prefer `find()` when a missing substring is a normal possibility
you plan to check for; prefer `index()` only when *not* finding it should
be treated as an unexpected problem.

#### `rindex(substring)`

Like `rfind()`, but raises `ValueError` instead of returning `-1`.

```python
print("banana".rindex("na"))   # 4
```

#### `startswith(prefix)`

Returns `True` if the string begins with `prefix`.

```python
print("hello.py".startswith("hello"))   # True
```

Note: also accepts a tuple of options to check several prefixes at once,
for example `"report.csv".startswith(("report", "summary"))` — tuples are
covered in Topic 6, so treat this as an optional bonus for now.

#### `endswith(suffix)`

Returns `True` if the string ends with `suffix`.

```python
print("hello.py".endswith(".py"))   # True
```

Use case: checking a file name's extension before processing it.

### Replacing and removing prefixes/suffixes

#### `replace(old, new)`

Returns a new string with every occurrence of `old` replaced by `new`.

```python
print("2024-01-15".replace("-", "/"))   # 2024/01/15
```

#### `removeprefix(prefix)`

Returns a new string with `prefix` removed from the start, only if it is
actually present there; otherwise returns the string unchanged.

```python
print("HELLOWORLD".removeprefix("HELLO"))   # WORLD
print("HELLOWORLD".removeprefix("BYE"))     # HELLOWORLD
```

#### `removesuffix(suffix)`

Returns a new string with `suffix` removed from the end, only if it is
actually present there; otherwise returns the string unchanged.

```python
print("HELLOWORLD".removesuffix("WORLD"))   # HELLO
```

Use case: `removeprefix`/`removesuffix` are safer and clearer than manual
slicing for stripping a known, fixed prefix or suffix, such as a file
extension or a URL scheme.

### Splitting, joining, and line handling

#### `split(separator)`

Splits a string into a list of pieces wherever `separator` occurs. With no
argument, splits on any whitespace and discards empty pieces.

```python
print("a,b,,c".split(","))   # ['a', 'b', '', 'c']
print("a b  c".split())       # ['a', 'b', 'c']
```

Warning: splitting on a specific separator keeps empty pieces between
repeated separators (as `""` in the first example); splitting with no
argument at all does not.

#### `rsplit(separator, maxsplit)`

Like `split()`, but splitting proceeds from the right; most useful when
combined with a `maxsplit` limit.

```python
print("a.b.c".rsplit(".", 1))   # ['a.b', 'c']
```

#### `splitlines()`

Splits a string at line boundaries (handling `\n`, `\r\n`, and a few other
line-ending styles) and returns the lines without their line-ending
characters.

```python
print("line1\nline2\r\nline3".splitlines())   # ['line1', 'line2', 'line3']
```

#### `join(iterable)`

Called *on* the separator string, and joins the pieces of `iterable`
together with that separator between each pair.

```python
print("-".join("abc"))   # a-b-c
```

Use case: `join` is very commonly used to combine a list of words into one
sentence, or a list of path pieces into one path — you will use it that
way constantly once lists are covered in Topic 5. The example above joins
the individual characters of a string instead, just to show the mechanism
without needing lists yet.

### Checking character/content properties

Each method below returns `True` or `False` and takes no arguments.

#### `isalpha()`

`True` if every character is a letter, and there is at least one
character.

```python
print("abc".isalpha())   # True
```

#### `isdigit()`

`True` if every character is a digit-like character (this includes a few
special digit symbols beyond plain `0`–`9`).

```python
print("123".isdigit())   # True
print("²".isdigit())     # True
```

#### `isdecimal()`

`True` when every character is a Unicode decimal digit (such as `0`–`9`) —
the strictest of the three digit-related checks.

```python
print("123".isdecimal())   # True
print("²".isdecimal())     # False
```

#### `isnumeric()`

`True` for digits, and also broader numeric characters such as Roman
numerals or fraction symbols — the widest of the three checks.

```python
print("123".isnumeric())     # True
print("²".isnumeric())       # True
print("Ⅷ".isnumeric())       # True  (Roman numeral eight)
print("Ⅷ".isdigit())         # False
```

Note: for everyday input validation (such as "did the user type a plain
number?"), `isdigit()` is usually the right choice; reach for `isdecimal()`
or `isnumeric()` only when you specifically need their stricter or wider
behavior.

#### `isalnum()`

`True` if every character is a letter or a digit (no spaces, punctuation,
or symbols).

```python
print("Ab1".isalnum())    # True
print("Ab1 ".isalnum())   # False — the trailing space breaks it
```

#### `isspace()`

`True` if every character is whitespace, and there is at least one
character.

```python
print("   ".isspace())   # True
```

#### `isupper()`

`True` if all cased characters are uppercase, and there is at least one
cased character.

```python
print("HELLO".isupper())   # True
```

#### `islower()`

`True` if all cased characters are lowercase, and there is at least one
cased character.

```python
print("hello".islower())   # True
```

#### `istitle()`

`True` if the string follows title-case rules (each word starts with an
uppercase letter, followed by lowercase letters).

```python
print("Hello World".istitle())   # True
print("Hello world".istitle())   # False
```

#### `isidentifier()`

`True` if the string is syntactically valid as a Python identifier.
Python keywords such as `class` and `def` also pass this test, so
`isidentifier()` alone does not guarantee that the text can be used as a
variable name.

```python
print("valid_name".isidentifier())   # True
print("2bad".isidentifier())         # False — cannot start with a digit
print("class".isidentifier())        # True — but `class` is a keyword
```

#### `isascii()`

`True` if every character is in the ASCII range (U+0000 through U+007F),
which excludes accented characters, most other writing systems, and emoji.

```python
print("hello".isascii())   # True
print("héllo".isascii())   # False
```

#### `isprintable()`

`True` if all characters in the string are printable (Python treats
control characters such as a newline as non-printable).

```python
print("Hello".isprintable())     # True
print("Hello\n".isprintable())   # False
```

### Alignment and formatting

#### `center(width)`

Returns a new string centered within a field of the given total width,
padded with spaces (or a custom fill character).

```python
print("hello".center(11, "*"))   # ***hello***
```

#### `ljust(width)`

Returns a new string left-aligned within a field of the given total width.

```python
print("hello".ljust(10, "-") + "|")   # hello-----|
```

#### `rjust(width)`

Returns a new string right-aligned within a field of the given total
width.

```python
print("hello".rjust(10, "-"))   # -----hello
```

Note: f-string alignment specifiers (`:<`, `:>`, `:^`, shown in Section 7)
achieve the same result and are generally preferred in new code, since they
combine alignment with the rest of your formatting in one place.

#### `format(*args, **kwargs)`

Fills `{ }` placeholders in the string with the given values. Covered in
detail in Section 7.

```python
print("{} is {}".format("Ada", 30))   # Ada is 30
```

#### `format_map(mapping)`

Like `format()`, but takes a single ready-made mapping (such as a
dictionary) instead of separate named arguments. Dictionaries are covered
fully in Topic 7; here is a minimal preview so the method is not skipped:

```python
data = {"name": "Ada"}
print("{name}".format_map(data))   # Ada
```

### Partitioning

#### `partition(separator)`

Splits the string at the **first** occurrence of `separator`, returning a
3-tuple containing everything before it, the separator itself, and
everything after it.

```python
print("2024-01-15".partition("-"))   # ('2024', '-', '01-15')
```

#### `rpartition(separator)`

Like `partition()`, but splits at the **last** occurrence of `separator`.

```python
print("2024-01-15".rpartition("-"))   # ('2024-01', '-', '15')
```

Use case: `partition`/`rpartition` are a clear, simple choice when you
specifically need to split into exactly three pieces around one separator
— for example, splitting `"key=value"` into `"key"`, `"="`, and `"value"`.

### Translation and tab expansion

#### `maketrans(from_chars, to_chars)`

A helper (called on the `str` type itself, as `str.maketrans(...)`, not on
one particular string) that builds a translation table, mapping each
character in `from_chars` to the character at the same position in
`to_chars`. Used together with `translate()`.

```python
table = str.maketrans("lo", "LO")
print(table)   # {108: 76, 111: 79}
```

Note: the numbers shown are Unicode code points for `l`, `L`, `o`, and `O`
— you do not need to understand these numbers to use `translate()`
successfully, as the next example shows.

#### `translate(table)`

Returns a new string with characters replaced according to a translation
table built by `maketrans()`.

```python
table = str.maketrans("lo", "LO")
print("Hello World".translate(table))   # HeLLO WOrLd
```

#### `expandtabs(tabsize)`

Returns a new string with every tab character (`\t`) replaced by enough
spaces to reach the next multiple of `tabsize`.

```python
print("Hello Tab\tHere".expandtabs(4))   # Hello Tab   Here
```

### Encoding and other less-common methods

#### `encode()`

Converts a `str` into a `bytes` object, using a text encoding (UTF-8 by
default). This is the bridge between Python's text world and the raw bytes
used for files and networks — full coverage of character encoding is in
Module 1.5; for now, just recognize what this method is for.

```python
print("café".encode())   # b'caf\xc3\xa9'
```

Note: the `b'...'` result is a different type from `str` (a `bytes`
object); you are not expected to work with it yet.

## Appendix summary

That covers all 47 public, non-dunder methods on `str` available in this
Python installation. Come back to this reference whenever you need it —
you are not expected to remember all of it, only to know it exists and how
to find what you need.
