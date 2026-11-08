# Strings: Indexing, Slicing, and Formatting

**Lesson summary, Stage 1 assessment, and all exercise solutions**

Source lesson: `04-strings-indexing-slicing-and-formatting.md`\
Curriculum reference: Stage 1 --- Programming & Computational Thinking.

------------------------------------------------------------------------

## Part 1 --- Complete lesson summary (under 1,000 words)

### 1. Strings and how to create them

A string (`str`) is text: a sequence of characters. A character is one
letter, digit, symbol, or space. Python accepts single, double, and
triple quotes; this course uses double quotes consistently. Triple
quotes preserve typed line breaks.

``` python
greeting_a = 'Hello'
greeting_b = "Hello"
message = """This is
a multi-line
string."""
print(message)
```

Output:

``` text
This is
a multi-line
string.
```

The backslash introduces escape sequences: `\n` newline, `\t` tab, `\"`
double quote, `\'` single quote, and `\\` literal backslash.

``` python
print("Line one\nLine two")
print("Name:\tAda")
print("She said \"hello\"")
print('It\'s sunny today')
print("Backslash: \\")
```

A raw string `r"..."` prevents ordinary escape processing, useful for
Windows paths:

``` python
normal_path = "C:\\Users\\Ada"
raw_path = r"C:\Users\Ada"
print(normal_path)
print(raw_path)
```

Both display `C:\Users\Ada`.

### 2. Immutability and methods

Strings are **immutable**: methods create a new result; they do not
alter the original string. Keep the result by assigning it:

``` python
name = "sam"
name.upper()
print(name)       # sam
name = name.upper()
print(name)       # SAM
```

Methods may return other types too: `"hello".count("l")` returns `2`
(`int`), `.isalpha()` returns a Boolean, and `"a b".split()` returns a
list.

### 3. Indexing and safe access

An index identifies one character. Indexing starts at zero; negative
indexes count from the end (`-1` is last):

``` python
word = "python"
print(word[0])    # p
print(word[-1])   # n
print(word[-2])   # o
print(word[10])   # IndexError: string index out of range
```

For a calculated non-negative position, check it before access:

``` python
username = "ada"
position = 10
if 0 <= position < len(username):
    print(username[position])
else:
    print("That position does not exist in this text.")
```

### 4. Slicing

`text[start:stop:step]` extracts characters from `start` up to but
excluding `stop`. Omitted boundaries mean beginning/end; negative
indexes count from the end; step controls spacing. The exclusive stop
makes slice length easy (`stop - start`) and lets adjacent slices meet
without overlap.

``` python
word = "python"
print(word[0:3])  # pyt
print(word[2:])   # thon
print(word[:4])   # pyth
print(word[:])    # python
print(word[-3:])  # hon
print(word[::2])  # pto
print(word[::-1]) # nohtyp (reverse)
```

### 5. String operations

``` python
first = "Py"
second = "thon"
print(first + second)       # Python (concatenate)
print("ha" * 3)             # hahaha (repeat)
print(len("python"))        # 6
print("th" in "python")     # True
print("xy" not in "python") # True
```

`+` joins strings; `*` repeats a string by an integer; `len()` counts
characters; `in`/`not in` test substring membership.

### 6. Formatting

f-strings (`f"..."`) are preferred: expressions inside braces are
evaluated.

``` python
name = "Ada"
age = 30
print(f"{name} is {age} years old.")
```

Output: `Ada is 30 years old.` Format specifiers after `:` control
display:

``` python
price = 1234.5
print(f"{price:.2f}")    # 1234.50
print(f"{price:,.2f}")   # 1,234.50
ratio = 0.4567
print(f"{ratio:.1%}")    # 45.7%
label = "Total"
print(f"[{label:>10}]")  # right aligned
print(f"[{label:<10}]")  # left aligned
print(f"[{label:^10}]")  # centered
```

`.2f` means two decimal places; `,.2f` adds thousands separators; `.1%`
multiplies by 100 and displays one decimal; `>`, `<`, `^` align within
width 10. Older `.format()` supports positional and named placeholders;
recognize legacy `%` formatting but do not use it in new code:

``` python
print("{} is {} years old.".format(name, age))
print("{n} is {a} years old.".format(n=name, a=age))
print("%s is %d years old." % (name, age))
```

### 7. Unicode and case comparison

Python `str` supports accented letters, other scripts, symbols and
emoji:

``` python
greeting = "café ☕ こんにちは 🐍"
print(greeting)
print(len(greeting))  # 14
text = "e\u0301"
print(text)           # visually é
print(len(text))      # 2 code points
```

Strings are sequences of Unicode code points; `len()` counts code
points, not always user-perceived characters. Text comparison is
case-sensitive. `lower()` lowercases for ordinary display; `casefold()`
is more aggressive for multilingual equality comparisons:

``` python
word = "straße"
print(word.lower())     # straße
print(word.casefold())  # strasse
```

`casefold()` does not perform all Unicode normalization; visually
identical text can have different code-point sequences.

### 8. Lesson examples

**Display name:** `first_name = "ada"; last_name = "lovelace"`;
`full_name = first_name.title() + " " + last_name.title()`;
`initials = first_name[0].upper() + last_name[0].upper()`. f-strings
print `Hello, Ada Lovelace!` and `Initials: AL`.

**Username cleanup:** `raw_input_value = "  Ada_2024  "`;
`username = raw_input_value.strip()` removes outer whitespace.
`.isalnum()` is false because `_` is not a letter or digit, so the
invalid-character message prints.

**Receipt:** `unit_price = 24.5`, `quantity = 3`, `tax_rate = 0.08`;
calculate subtotal `73.5`, tax `5.88`, total `79.38`. f-strings align
item/quantity/price and format amounts with `:,.2f`, percentage with
`:.0%`. Output:

``` text
Wireless Mouse        3 x $ 24.50
Subtotal: $73.50
Tax (8%): $5.88
Total:    $79.38
```

Common errors: expecting methods to mutate strings; off-by-one slice
stops; indexing at `len(text)`; unescaped matching quote marks;
case-sensitive comparisons; using `%` or manual concatenation instead of
f-strings.

### 9. Appendix: string method reference

The appendix lists 47 public non-dunder `str` methods. Know the
categories, not all by memory:

-   Case: `capitalize`, `casefold`, `lower`, `upper`, `swapcase`,
    `title`.
-   Trimming/padding: `strip`, `lstrip`, `rstrip`, `zfill`.
-   Search/count: `count`, `find`, `rfind`, `index`, `rindex`,
    `startswith`, `endswith`. `find` returns `-1` if absent; `index`
    raises `ValueError`.
-   Replace/remove: `replace`, `removeprefix`, `removesuffix`.
-   Split/join/lines: `split`, `rsplit`, `splitlines`, `join`.
    Explicit-separator `split` preserves empty pieces; no-argument
    `split` collapses whitespace. `join` is called on the separator.
-   Character tests: `isalpha`, `isdigit`, `isdecimal`, `isnumeric`,
    `isalnum`, `isspace`, `isupper`, `islower`, `istitle`,
    `isidentifier`, `isascii`, `isprintable`. `isdecimal` is stricter
    than `isdigit`; `isnumeric` is broader. `isidentifier` does not
    reject keywords by itself.
-   Alignment/formatting: `center`, `ljust`, `rjust`, `format`,
    `format_map`.
-   Partition: `partition` splits at first separator; `rpartition` at
    last, each returning three parts.
-   Translation/tabs: `maketrans` creates a translation table;
    `translate` applies it; `expandtabs` expands tabs to tab stops.
-   Encoding: `encode()` converts `str` to `bytes` (UTF-8 by default).

`strip(chars)` removes any of the supplied characters from both ends,
not one exact substring. `repr()` displays spaces/escapes clearly.
`title()` can capitalize unexpectedly around apostrophes. The lesson
notes that list/tuple return types from `split`, `join`, and `partition`
are only previews; those types are taught later.

Strings are central to prompts, model responses, tool arguments, logs,
input cleanup, parsing, and user-facing output in later AI systems.

------------------------------------------------------------------------

## Part 2 --- Current level assessment using the entire Stage 1 project tree

The supplied Stage 1 tree begins with computational thinking
(algorithms, values/expressions/variables, input-process-output,
sequence/selection/iteration, decomposition, preconditions/edge cases,
pseudocode/dry runs, state modelling). It then moves through Python core
types (this is Topic 4), collections, control flow/functions/errors,
algorithmic habits, files/CSV/JSON/CLI, packages/dependencies/code
quality, testing/debugging, and OOP/data modelling. Later modules cover
production Python, advanced object model, metaprogramming, standard
library, binary/text processing, modern Python, advanced testing,
performance, packaging, CPython internals, design patterns,
visualization, security, refactoring, and functions/OOP gap lessons.
Projects include an expense ledger, log investigation CLI,
data-quality/transformation pipeline, and rule-based risk-review engine.

**Assessment:** Your current lesson position is early Stage 1,
specifically Python Core Language Topic 4, after files/interpreter,
variables/types, and operators. This tree describes the intended
curriculum, not proof that all modules have been completed. Without your
independently executed code and exercise outputs, mastery cannot be
confirmed. Current verified level: beginner/foundational for strings;
practical proficiency is pending. The exercises below use only concepts
already introduced in this lesson and earlier Stage 1 foundations. The
`if` used in the supplied lesson's safe-index example is a prerequisite
from computational thinking, not a new advanced topic.

------------------------------------------------------------------------

## Part 3 --- All six exercises solved step by step (under 1,500 words)

### Exercise 1 --- First, last, and `"phan"` in `"elephant"`

``` python
word = "elephant"

print(word[0])
print(word[-1])
print(word[3:7])
```

-   `word[0]` reads the first character: `e`.
-   `word[-1]` reads the last character: `t`.
-   `word[3:7]` starts at index 3 (`p`) and stops before index 7, giving
    `phan`.

Output:

``` text
e
t
phan
```

Indexes are `e=0, l=1, e=2, p=3, h=4, a=5, n=6, t=7`; therefore `[3:7]`
includes `p`, `h`, `a`, `n` and excludes index 7.

### Exercise 2 --- Reverse `"Applied AI"`

``` python
print("Applied AI"[::-1])
```

`[::-1]` means traverse the entire string with a step of negative one,
from last character to first.

Output:

``` text
IA deilppA
```

### Exercise 3 --- Strip spaces and compare lengths

``` python
sentence = "  Data Science and AI  "
clean_sentence = sentence.strip()

print(len(sentence))
print(len(clean_sentence))
```

-   `sentence` stores the original text with two spaces at each end.
-   `.strip()` returns a new string without leading/trailing whitespace;
    the original remains unchanged.
-   `len()` counts characters.

Output:

``` text
22
18
```

Four whitespace characters were removed: two at the beginning and two at
the end.

### Exercise 4 --- Format `7` and `0.256`

``` python
number = 7
ratio = 0.256

print(f"{number:02d}")
print(f"{ratio:.1%}")
```

-   `:02d` formats an integer with at least two digits, padding with a
    leading zero: `07`.
-   `:.1%` converts the ratio to percentage and shows one decimal place:
    `25.6%`.

Output:

``` text
07
25.6%
```

### Exercise 5 --- Count `"a"` regardless of case

``` python
sentence = "A data analyst analyzes data"
normalized_sentence = sentence.casefold()
letter_count = normalized_sentence.count("a")

print(letter_count)
```

-   The first line stores the made-up sentence.
-   `.casefold()` returns a lowercase-normalized string suitable for
    comparison.
-   `.count("a")` counts non-overlapping occurrences of the letter `a`.
-   `print` displays the count.

Output:

``` text
8
```

### Exercise 6 --- Use an unfamiliar appendix method

Example using `removeprefix()`:

``` python
file_name = "report_final.csv"
clean_name = file_name.removeprefix("report_")
print(clean_name)
```

-   `file_name` stores the original string.
-   `removeprefix("report_")` removes that exact prefix only if it
    occurs at the beginning, returning a new string.
-   The result is stored in `clean_name` and printed.

Output:

``` text
final.csv
```

**One-sentence explanation:** `removeprefix()` returns a new string with
a specified prefix removed only when that prefix is at the start.

------------------------------------------------------------------------

## Completion checklist

-   [ ] I can create quoted and multiline strings and use escape
    sequences/raw strings.
-   [ ] I understand immutability and reassign method results when
    needed.
-   [ ] I can use positive/negative indexing and avoid `IndexError`.
-   [ ] I can slice with start, stop, and step, including reverse
    slicing.
-   [ ] I can concatenate, repeat, measure length, and test membership.
-   [ ] I can format values with f-strings, decimals, commas,
    percentages, zero-padding, and alignment.
-   [ ] I understand Unicode code points and the purpose of
    `casefold()`.
-   [ ] I completed and ran all six exercises.
-   [ ] I can find a suitable method in the `str` appendix rather than
    trying to memorize all methods.
