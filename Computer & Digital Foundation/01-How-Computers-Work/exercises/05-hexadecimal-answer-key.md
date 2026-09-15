# Concept 5 — Hexadecimal — Answer Key

> **Answer Key — Open Only After Attempting the Exercises**
>
> This file contains reasoning and explanations for every exercise in
> [`../05-hexadecimal.md`](../05-hexadecimal.md), Section 12. Attempt every question yourself
> first, with your own worked reasoning, before reading any answer below.

Reference table used throughout:

```text
Binary   Hex        Binary   Hex
0000      0         1000      8
0001      1         1001      9
0010      2         1010      A
0011      3         1011      B
0100      4         1100      C
0101      5         1101      D
0110      6         1110      E
0111      7         1111      F
```

---

## Level 1 — Recognition

**1. What 16 symbols does hexadecimal use?** `0 1 2 3 4 5 6 7 8 9 A B C D E F`.

**2. What decimal value does `A` represent?** 10.

**3. What decimal value does `F` represent?** 15.

**4. What is a "nibble"?** A group of 4 bits — exactly half of a byte, and exactly the number of
bits one hexadecimal digit represents.

**5. How many bits correspond to one hexadecimal digit?** 4 bits.

**6. How many hexadecimal digits correspond to one full byte?** 2 hexadecimal digits (8 bits ÷ 4
bits per digit = 2 digits).

**7. What does "base" mean?** The number of distinct single-digit symbols a number system uses
before it must combine digits to represent larger values (base 10 has 10 symbols, base 2 has 2,
base 16 has 16).

---

## Level 2 — Understanding

**8. Why does hexadecimal exist?**

Long binary strings (e.g., `1101011010111010`) are hard for humans to read, write, and compare
accurately. Hexadecimal represents the exact same values far more compactly, making them much
easier for humans to work with, without changing the underlying data itself.

**9. Why is hexadecimal useful specifically for binary data?**

Because of the exact 4-bits-to-1-hex-digit relationship (Section 4/6), hexadecimal can represent
any binary value using roughly a quarter as many characters, with a simple, reliable, group-and-map
conversion process in both directions — no other common base has this clean a relationship to
binary.

**10. Why does one hexadecimal digit represent exactly four bits?**

Hexadecimal has 16 digit symbols. Using Concept 4's `n bits → 2^n combinations` relationship,
`2^4 = 16` — exactly matching hexadecimal's 16 symbols. Since 4 bits produce exactly 16 possible
patterns, and hexadecimal has exactly 16 digit symbols, there's an exact one-to-one correspondence
between every possible 4-bit pattern and a single hex digit.

**11. Why do two hexadecimal digits represent exactly one byte?**

A byte is 8 bits (Concept 4). Since 1 hex digit = 4 bits, 2 hex digits = 8 bits — exactly one
byte, with nothing left over and nothing missing.

**12. Why is hexadecimal not a programming language?**

It's a number/representation system — a way of writing numeric values using base 16 — with no
commands, syntax, grammar, or instructions of its own. A programming language is a structured
system for writing instructions; hexadecimal is just a notation for writing numbers.

**13. Why doesn't hexadecimal make data smaller, even though it looks shorter?**

The underlying binary data (the actual bits stored) doesn't change at all — hexadecimal is only a
different, more compact way of *writing down* that same value for human reading. A byte is still
8 bits whether written as `11111111` or as `FF`; only the textual representation shown to a human
is shorter.

**14. Why does context matter when interpreting `10` or `FF`?**

The exact same digit sequence represents different actual values depending on which base is
intended: `10` is ten in decimal, but sixteen in hexadecimal (and two in binary). Without knowing
the base/context, a bare digit sequence can't be reliably interpreted — this mirrors Concept 4's
"bit patterns require context" principle, applied here to which base is in use.

---

## Level 3 — Application

### Binary → hexadecimal

**15. `1010`** → single group, `1010 → A`. **Answer: A**

**16. `1111`** → single group, `1111 → F`. **Answer: F**

**17. `10101100`** → split `1010 1100` → `1010→A`, `1100→C`. **Answer: AC**

**18. `11010110`** → split `1101 0110` → `1101→D`, `0110→6`. **Answer: D6**

**19. `111100001010`** → split into 4-bit groups from the right: `1111 0000 1010` →
`1111→F`, `0000→0`, `1010→A`. **Answer: F0A**

### Hexadecimal → binary

**20. `A`** → `1010`. **Answer: 1010**

**21. `F`** → `1111`. **Answer: 1111**

**22. `2A`** → `2→0010`, `A→1010` → **Answer: 00101010**

**23. `B6`** → `B→1011`, `6→0110` → **Answer: 10110110**

**24. `F0A`** → `F→1111`, `0→0000`, `A→1010` → **Answer: 111100001010**

### Hexadecimal → decimal

**25. `A`** = 10. **Answer: 10**

**26. `F`** = 15. **Answer: 15**

**27. `10`** = `1×16 + 0×1 = 16`. **Answer: 16**

**28. `2A`** = `2×16 + 10×1 = 32 + 10 = 42`. **Answer: 42**

**29. `3F`** = `3×16 + 15×1 = 48 + 15 = 63`. **Answer: 63**

**30. `1F4`** = `1×256 + 15×16 + 4×1 = 256 + 240 + 4 = 500`. **Answer: 500**

### Decimal → hexadecimal

**31. `10`** → single digit: `A`. **Answer: A**

**32. `15`** → single digit: `F`. **Answer: F**

**33. `16`** → repeated division by 16:

```text
16 ÷ 16 = 1 remainder 0
1 ÷ 16  = 0 remainder 1
Reading remainders bottom to top: 1 0
```

**Answer: 10** (check: `1×16 + 0 = 16` ✓)

**34. `42`** →

```text
42 ÷ 16 = 2 remainder 10 (A)
2 ÷ 16  = 0 remainder 2
Reading bottom to top: 2 A
```

**Answer: 2A** (check: `2×16 + 10 = 42` ✓)

**35. `63`** →

```text
63 ÷ 16 = 3 remainder 15 (F)
3 ÷ 16  = 0 remainder 3
Reading bottom to top: 3 F
```

**Answer: 3F** (check: `3×16 + 15 = 63` ✓)

**36. `255`** →

```text
255 ÷ 16 = 15 remainder 15 (F)
15 ÷ 16  = 0  remainder 15 (F)
Reading bottom to top: F F
```

**Answer: FF** (check: `15×16 + 15 = 255` ✓)

**37. `500`** →

```text
500 ÷ 16 = 31 remainder 4
31 ÷ 16  = 1  remainder 15 (F)
1 ÷ 16   = 0  remainder 1
Reading bottom to top: 1 F 4
```

**Answer: 1F4** (check: `1×256 + 15×16 + 4 = 256+240+4 = 500` ✓ — matches Section 7, Example 5)

*Why remainders are read in reverse order:* the first remainder obtained is the value's
**least-significant** (rightmost) digit, since it's the "leftover" after removing as many of the
*largest* possible groupings of 16 as fit at each step — division peels off the smallest place
value first, so the digits naturally come out from right to left, and must be reversed to be
written in normal left-to-right order.

---

## Level 4 — Debugging

**38. "`2A` = 12 decimal, because 2 + 10 = 12."**

Wrong: this ignores positional place value entirely, simply adding the digit values as if both
were in the "ones" place. `2` is actually in the `16¹` position, worth `2×16 = 32`, not just `2`.
Correct: `2×16 + 10×1 = 32 + 10 = 42`.

**39. "`FF` = 15 decimal, because F means 15."**

Wrong: this only accounts for one `F`'s value and ignores that the two digits occupy different
place values (`16¹` and `16⁰`). Correct: `15×16 + 15×1 = 240 + 15 = 255`.

**40. "`A` = 1010 in binary."**

This is actually **correct** — `A` does equal `1010` in binary, per the mapping table. (If this
was presented as an error to find, the correct response is to confirm it's right and explain why:
`A = 10` in decimal, and `10` in binary is `1010`, matching the direct table lookup as well.)

**41. "1 hex digit = 8 bits."**

Wrong: 1 hex digit = 4 bits (a nibble), not 8. 8 bits is a full byte, which requires **two**
hexadecimal digits, not one (Section 6).

**42. "`10` hex = `10` decimal."**

Wrong: `10` in hexadecimal equals `16` in decimal (`1×16 + 0×1 = 16`), not `10`. The digit
sequence "10" only equals ten specifically in decimal; in another base, the same written digits
represent a different value (Misconception 4).

---

## Level 5 — Integration

### Scenario A — Byte inspection: `41 42 43`

**43. What does each pair represent structurally?** Each two-character pair (`41`, `42`, `43`) is
one byte, written as its two hexadecimal digits (Section 6's "2 hex digits = 1 byte").

**44. How many bytes are shown?** 3 bytes (three pairs).

**45. How many bits does that represent?** `3 bytes × 8 bits/byte = 24 bits`.

**46. Why is hexadecimal useful here?** Displaying `41 42 43` is far more compact and readable
than displaying the equivalent 24-character binary string (`01000001 01000010 01000011`), while
representing the exact same underlying data — exactly Section 2's core justification for
hexadecimal.

### Scenario B — AI artifact inspection

**47. What are you actually looking at?** A human-readable hexadecimal translation of the file's
actual raw bytes, produced by the viewing tool — not the bytes themselves in some hexadecimal
physical form.

**48. Are the displayed characters necessarily stored as literal characters?** No. The file
stores raw binary data; the hex viewer reads those bytes and converts them to hexadecimal text
purely for display, on the fly, each time you view it (Section 9, Section 11 Scenario 6). The
hexadecimal text itself is not what exists on disk.

**49. Why might an engineer inspect bytes this way?** To verify a file's actual low-level content
or structure — for example, confirming a file isn't corrupted, checking its format/header,
diagnosing unexpected behavior, or understanding what's really stored when the normal
higher-level view (e.g., opening it as an image or text file) isn't sufficient or is behaving
unexpectedly.

### Scenario C — Binary debugging: `11010110`

**50. Convert to hexadecimal, showing work.** Split: `1101 0110`. Map: `1101→D`, `0110→6`.
**Answer: D6**

**51. Why is hexadecimal more practical to communicate?** `D6` (2 characters) conveys the exact
same value as `11010110` (8 characters) far more compactly and with much less chance of a
transcription error (e.g., miscounting digits or swapping a 0/1) — directly reflecting Section 2's
core rationale for hexadecimal's existence.

### Scenario D — Data-size reasoning: `3F A2 00 1B`

**52. How many hexadecimal digits are shown (ignoring spaces)?** 8 digits (`3,F,A,2,0,0,1,B`).

**53. How many bytes does this represent?** 4 bytes (each pair of hex digits = 1 byte; 8 digits ÷
2 = 4 bytes).

**54. How many bits does this represent?** `4 bytes × 8 bits/byte = 32 bits` (equivalently, `8
hex digits × 4 bits/digit = 32 bits` — both routes give the same answer, confirming the
consistency of the hex/binary/byte relationships from Section 6).

---

_This answer key covers Concept 5 (Hexadecimal) only. It does not contain, reference, or
anticipate answers for Concept 6 (Registers) or any later concept._
