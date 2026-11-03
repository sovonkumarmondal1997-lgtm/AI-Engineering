# Lesson 04: Python Strings – Indexing, Slicing, and Formatting

This lesson teaches you how to store, access, extract, clean, search, modify, and format text using Python.

**Why it matters:** In Data Engineering, you constantly process customer names, CSV data, database records, file paths, API responses, and log messages. All these operations require string manipulation.

---

## 1. Creating strings

A string (`str`) represents text. Python supports three quotation styles:

```python
name = "Python"
name = 'Python'
message = """This is
a multiline
string."""
```

- Single and double quotes work identically.
- Triple quotes allow multiline strings.
- Choose one quotation style and remain consistent.

---

## 2. Escape sequences and raw strings

Escape sequences use `\` to represent special characters.

| Sequence | Meaning |
|---|---|
| `\n` | New line |
| `\t` | Tab |
| `\"` | Double quotation mark |
| `\'` | Single quotation mark |
| `\\` | Backslash |

Example:

```python
print("Hello\nWorld")
print("Name:\tAda")
print("She said \"Hello\"")
```

**Raw strings:** Add `r` before a string to prevent ordinary escape sequences from being interpreted.

```python
path = r"C:\Users\Ada"
```

Useful for Windows file paths and regular expressions.

---

## 3. String immutability

Strings are immutable, meaning their original characters cannot be changed directly.

String methods return new strings instead of modifying the original.

```python
name = "sam"
name.upper()
print(name)  # sam

name = name.upper()
print(name)  # SAM
```

**Remember:** assign the returned result if you want to keep the transformation.

---

## 4. String indexing

Indexing means accessing one character using its position.

Python uses zero-based indexing.

```python
word = "python"

print(word[0])   # p
print(word[-1])  # n
print(word[-2])  # o
```

- Positive indexes start from `0`.
- Negative indexes start from `-1` at the end.

Accessing a nonexistent position causes `IndexError`.

Use `len()` and comparisons to check whether a calculated positive index exists before accessing it.

---

## 5. String slicing

Slicing extracts a portion of a string.

Syntax:

```python
string[start:stop:step]
```

The stop position is excluded.

```python
word = "python"

print(word[0:3])  # pyt
print(word[2:])   # thon
print(word[:4])   # pyth
print(word[:])    # python
print(word[-3:])  # hon
```

Step controls how many positions Python moves between characters.

```python
print(word[::2])   # pto
print(word[::-1])  # nohtyp
```

`[::-1]` reverses a string.

---

## 6. Concatenation, repetition, length and membership

| Operation | Meaning |
|---|---|
| `+` | Joins strings |
| `*` | Repeats strings |
| `len()` | Counts characters |
| `in` | Checks whether text exists |
| `not in` | Checks whether text does not exist |

```python
first = "Py"
second = "thon"

print(first + second)        # Python
print("ha" * 3)              # hahaha
print(len("python"))         # 6
print("th" in "python")      # True
print("xy" not in "python")  # True
```

---

## 7. String formatting

Formatting combines fixed text with changing values.

### A. f-strings – Preferred modern approach

```python
name = "Ada"
age = 30

print(f"{name} is {age} years old.")
```

### B. Format specifiers

```python
price = 1234.5
ratio = 0.4567
label = "Total"

print(f"{price:.2f}")    # 1234.50
print(f"{price:,.2f}")   # 1,234.50
print(f"{ratio:.1%}")    # 45.7%
print(f"{label:>10}")    # Right aligned
print(f"{label:<10}")    # Left aligned
print(f"{label:^10}")    # Center aligned
```

### C. `str.format()` – Older alternative

```python
print("{} is {} years old.".format("Ada", 30))
print("{n} is {a} years old.".format(n="Ada", a=30))
```

### D. `%` formatting – Legacy approach

```python
print("%s is %d years old." % ("Ada", 30))
```

Recognize this style in older code, but prefer f-strings for new code.

---

## 8. Unicode and `casefold()`

Python strings support Unicode, allowing accented letters, international languages, symbols, and emoji.

```python
greeting = "café ☕ こんにちは 🐍"

print(greeting)
print(len(greeting))
```

Important details:

- Python strings contain Unicode code points.
- `len()` counts code points, not necessarily characters perceived by humans.
- Some visible characters consist of multiple code points.
- Text comparison is case-sensitive.

Difference between `lower()` and `casefold()`:

```python
word = "straße"

print(word.lower())     # straße
print(word.casefold())  # strasse
```

Use `lower()` for ordinary lowercase display. Prefer `casefold()` for reliable case-insensitive text comparison across languages. Unicode normalization may additionally be needed for equivalent-looking character sequences.

---

## 9. Three practical examples

### Example 1: Building a full name

```python
first_name = "ada"
last_name = "lovelace"

full_name = first_name.title() + " " + last_name.title()
initials = first_name[0].upper() + last_name[0].upper()

print(f"Hello, {full_name}!")
print(f"Initials: {initials}")
```

### Example 2: Cleaning and validating usernames

```python
raw_input_value = "  Ada_2024  "
username = raw_input_value.strip()

if username.isalnum():
    print("Valid username")
else:
    print("Invalid username")
```

`strip()` removes surrounding whitespace. `isalnum()` checks whether every character is a letter or digit. The underscore makes this username invalid under that rule.

### Example 3: Formatting a receipt

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

Output includes aligned columns, two-decimal prices, and percentage formatting.

---

## 10. Common beginner mistakes

1. Expecting string methods to modify the original string.
2. Forgetting that slicing excludes the stop index.
3. Accessing an index outside the string's valid range.
4. Forgetting to escape quotation marks.
5. Comparing text without considering case differences.
6. Using old `%` formatting or manual concatenation instead of f-strings.

---

## 11. Important Python string methods

The attached lesson's appendix documents 47 public, non-dunder string methods. You do not need to memorize all of them, but should know their purposes.

| Category | Methods | Purpose |
|---|---|---|
| Case conversion | `capitalize()`, `casefold()`, `lower()`, `upper()`, `swapcase()`, `title()` | Change letter casing. |
| Trimming/padding | `strip()`, `lstrip()`, `rstrip()`, `zfill()` | Remove whitespace or pad text. |
| Searching/counting | `count()`, `find()`, `rfind()`, `index()`, `rindex()` | Search for text and count occurrences. |
| Prefix/suffix | `startswith()`, `endswith()` | Check beginning or ending text. |
| Replacing | `replace()`, `removeprefix()`, `removesuffix()` | Replace or remove specific text. |
| Splitting/joining | `split()`, `rsplit()`, `splitlines()`, `join()` | Divide or combine text. |
| Character validation | `isalpha()`, `isdigit()`, `isdecimal()`, `isnumeric()`, `isalnum()`, `isspace()` | Validate character content. |
| Case validation | `isupper()`, `islower()`, `istitle()` | Check letter casing. |
| Other validation | `isidentifier()`, `isascii()`, `isprintable()` | Check identifier, ASCII and printable characters. |
| Alignment | `center()`, `ljust()`, `rjust()` | Align and pad text. |
| Formatting | `format()`, `format_map()` | Insert values into placeholders. |
| Partitioning | `partition()`, `rpartition()` | Split into three parts around a separator. |
| Translation | `maketrans()`, `translate()` | Replace characters using a translation table. |
| Tab handling | `expandtabs()` | Convert tabs into spaces. |
| Encoding | `encode()` | Convert text into bytes. |

Additional important distinctions:

- `find()` returns `-1` if text is missing; `index()` raises `ValueError`.
- `strip()` removes combinations of specified characters from both ends, not one exact substring.
- `split(",")` preserves empty pieces between repeated commas; `split()` without an argument handles whitespace and discards empty pieces.
- `isdigit()`, `isdecimal()`, and `isnumeric()` have different levels of numeric-character acceptance.
- `join()` joins pieces using the string on which it is called.
- `partition()` splits at the first separator; `rpartition()` uses the last.
- `encode()` converts a string into a bytes object, using UTF-8 by default.

---

## 12. Practical exercises

Complete all six:

1. Extract the first character, last character, and `"phan"` from `"elephant"`.
2. Reverse `"Applied AI"` using slicing.
3. Clean `"  Data Science and AI  "` using `strip()` and compare lengths.
4. Format `7` as a two-digit zero-padded string and `0.256` as a percentage with one decimal place.
5. Count occurrences of `"a"` in a sentence without case sensitivity.
6. Find one unfamiliar string method in the appendix, demonstrate it, and explain its purpose.

---

## 13. Connection to Data Engineering and AI Engineering

Strings are essential for processing:

- CSV files and database records.
- Customer information and usernames.
- File names and file paths.
- API requests and responses.
- Application logs.
- AI prompts and model-generated responses.

You will use slicing, cleaning, validation, formatting, and Unicode handling regularly when building ETL pipelines and AI applications.
