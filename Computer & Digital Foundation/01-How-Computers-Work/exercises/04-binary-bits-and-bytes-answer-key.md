# Concept 4 — Binary, Bits, and Bytes — Answer Key

> **Answer Key — Open Only After Attempting the Exercises**
>
> This file contains reasoning and explanations for every exercise in
> [`../04-binary-bits-and-bytes.md`](../04-binary-bits-and-bytes.md), Section 12. Attempt every
> question yourself first, in your own words and with your own worked reasoning, before reading
> any answer below.

---

## Level 1 — Recognition

**1. What is a bit?** The smallest unit of digital information — a single value that is always
exactly one of two states, `0` or `1`.

**2. What is a byte?** A standard grouping of 8 bits, handled together as one unit.

**3. What is a binary digit? Is it the same thing as a bit?** A binary digit is a single digit in
the base-2 number system (`0` or `1`). Yes — "bit" is literally short for "binary digit"; they are
the same thing.

**4. What is a binary number, as distinct from a single bit?** A binary number is a sequence of
one or more bits, read together and interpreted (typically under place-value rules) as
representing a numeric value — for example, `1011`. A single bit is just one digit; a binary
number is a full pattern of digits with an interpreted value.

**5. What is a "bit pattern"?** A specific sequence of bits (e.g., `01000001`), considered as raw
data before or independent of any particular interpretation being applied to it.

**6. What does "digital representation" mean?** Representing information using a limited number
of distinct, discrete states (in computing, specifically two states, represented as 0 and 1),
rather than something that varies smoothly.

**7. How many bits are in a byte?** 8.

**8. How many combinations can 3 bits represent?** `2^3 = 8`.

**9. How many combinations can 8 bits represent?** `2^8 = 256`.

---

## Level 2 — Understanding

**10. Why do computers use binary rather than a ten-state (decimal-matching) system?**

Digital electronic hardware is engineered to reliably distinguish between physical states.
Building circuitry that reliably tells apart only two clearly distinct states is far more
practical and error-resistant than building circuitry that has to reliably distinguish ten
finely-graded states, especially given electrical noise and manufacturing variation. Binary
matches, exactly, how many distinguishable states digital hardware is actually built to produce
and detect.

**11. Why can 2 bits represent exactly 4 combinations?**

Each bit is independently either `0` or `1`. For the first bit, there are 2 choices. For each of
those 2 choices, the second bit again has 2 choices — giving `2 × 2 = 4` total combinations:
`00, 01, 10, 11`. This is the doubling pattern described in Section 5 — each additional bit
doubles the number of possible combinations because it adds an independent 2-way choice on top of
every combination that already existed.

**12. Why can 8 bits represent exactly 256 combinations?**

Following the same doubling logic eight times: `2 × 2 × 2 × 2 × 2 × 2 × 2 × 2 = 2^8 = 256`. Each
of the 8 bits independently contributes a factor of 2 to the total count of possible patterns.

**13. Why does a bit pattern need context to be interpreted correctly?**

A bit pattern is just raw data — a sequence of 0s and 1s — with no built-in, automatic meaning.
The same exact pattern (e.g., `01000001`) can represent a number under one interpretation system
and something entirely different (like a character) under another. Without knowing which system
is being used to interpret it, there's no way to know what a given bit pattern is meant to
represent.

**14. What is the difference between a bit and a byte?**

A bit is the smallest unit — a single 0 or 1. A byte is a standard grouping of 8 bits, handled
together as one unit. A bit is one building block; a byte is a fixed-size collection of 8 of them.

**15. What is the difference between binary and a programming language?**

Binary is a number/representation system — a way of writing values using only two digits (0 and
1). A programming language (like Python) is a structured system with its own vocabulary, grammar,
and rules that humans use to write instructions. Those instructions eventually get translated into
binary-encoded machine code so a CPU can execute them, but binary itself has no commands, syntax,
or grammar — it's purely a representation format, not a language for expressing instructions.

---

## Level 3 — Application

Each answer shows the place-value reasoning method from Section 5.

**16. Convert binary `1010` to decimal.**

```text
digit:        1    0    1    0
place value:  8    4    2    1
contributes:  8  + 0  + 2  + 0  =  10
```

Answer: **10**

**17. Convert binary `1111` to decimal.**

```text
digit:        1    1    1    1
place value:  8    4    2    1
contributes:  8  + 4  + 2  + 1  =  15
```

Answer: **15**

**18. Convert decimal `9` to binary.**

Using repeated division by 2 (Method 2 — divide by 2, record the remainder, repeat with the
quotient, then read remainders bottom-to-top / in reverse order):

```text
9 ÷ 2 = 4 remainder 1
4 ÷ 2 = 2 remainder 0
2 ÷ 2 = 1 remainder 0
1 ÷ 2 = 0 remainder 1

Reading remainders bottom to top: 1 0 0 1
```

Answer: **1001**

Check using the place-value method: `8 + 0 + 0 + 1 = 9`. Correct.

**19. Convert decimal `13` to binary.**

```text
13 ÷ 2 = 6 remainder 1
6 ÷ 2  = 3 remainder 0
3 ÷ 2  = 1 remainder 1
1 ÷ 2  = 0 remainder 1

Reading remainders bottom to top: 1 1 0 1
```

Answer: **1101**

Check: `8 + 4 + 0 + 1 = 13`. Correct.

**20. Convert binary `11001` to decimal.**

```text
digit:        1     1     0    0    1
place value:  16    8     4    2    1
contributes:  16  + 8   + 0  + 0  + 1  =  25
```

Answer: **25**

**21. Convert decimal `100` to binary.**

```text
100 ÷ 2 = 50 remainder 0
50 ÷ 2  = 25 remainder 0
25 ÷ 2  = 12 remainder 1
12 ÷ 2  = 6  remainder 0
6 ÷ 2   = 3  remainder 0
3 ÷ 2   = 1  remainder 1
1 ÷ 2   = 0  remainder 1

Reading remainders bottom to top: 1 1 0 0 1 0 0
```

Answer: **1100100**

Check using place values `64 32 16 8 4 2 1`: `64 + 32 + 0 + 0 + 4 + 0 + 0 = 100`. Correct.

**22. `0101 + 0011` (binary addition).**

Using the rules `0+0=0`, `0+1=1`, `1+0=1`, `1+1=10` (write 0, carry 1), adding right to left:

```text
    0101
  + 0011
  ------
Position 1 (rightmost): 1 + 1 = 10  → write 0, carry 1
Position 2:              0 + 1 + carry 1 = 10  → write 0, carry 1
Position 3:              1 + 0 + carry 1 = 10  → write 0, carry 1
Position 4 (leftmost):   0 + 0 + carry 1 = 1   → write 1

Result: 1000
```

Answer: **1000**

Check in decimal: `0101 = 5`, `0011 = 3`, `5 + 3 = 8`, and `1000` in binary = `8`. Correct.

**23. `0110 + 0110` (binary addition).**

```text
    0110
  + 0110
  ------
Position 1: 0 + 0 = 0
Position 2: 1 + 1 = 10 → write 0, carry 1
Position 3: 1 + 1 + carry 1 = 11 → write 1, carry 1
Position 4: 0 + 0 + carry 1 = 1

Result: 1100
```

Answer: **1100**

Check in decimal: `0110 = 6`, `6 + 6 = 12`, and `1100` in binary = `8 + 4 = 12`. Correct.

---

## Level 4 — Debugging

**24. "`1010` = `10` because `10` is written at the end of the pattern."**

This reasoning is wrong. `1010` is a binary number and must be converted using binary place
values, not read as if the last two digits were a decimal number. Correctly, using place values
`8 4 2 1`: `1010 = 8 + 0 + 2 + 0 = 10` in decimal — coincidentally landing on the same numeral
"10," but only because the actual place-value calculation happens to produce that decimal result,
not because of where digits are positioned in the written pattern. The correct method is always
Section 5's place-value reasoning, not visually reading off trailing digits.

**25. "`11111111` always means `255`, in every possible system, with no exceptions."**

This is incorrect. `11111111` equals `255` specifically under the unsigned interpretation this
lesson uses. Under a different interpretation system (for example, one designed to represent
negative numbers, which this lesson does not teach), the exact same bit pattern could represent a
different value entirely (such as `-1` in some signed systems, mentioned in Section 11, Scenario
2). The correct understanding is that a bit pattern's numeric meaning depends on which
interpretation system is being applied — "always," with no exceptions, is never accurate for a
raw bit pattern (Section 6).

**26. "`00000101` and `101` must be different values, because they don't look different... they
don't look the same."**

This is incorrect. They represent the exact same value, `5`. Leading zeros never change a binary
number's value, for the same reason `005` and `5` are equal in decimal — each leading zero
occupies a place value that, multiplied by 0, contributes nothing to the total (Section 11,
Scenario 1).

**27. "Since `printf '%08d' 5` outputs `00000005`, that must be the binary form of `5`."**

This is incorrect. `%d` in `printf` always means "format as a decimal integer" — the `08` only
controls padding that decimal output to 8 characters with leading zeros. `00000005` is decimal
`5` padded with zeros, not a binary conversion at all. The actual binary form of `5` is `101` (or
`00000101` padded to a byte) — a completely different value from `00000005`. This is exactly the
distinction Section 9 and Section 11 (Scenario 5) make explicit: formatting flags control *display
padding*, not *number base*.

---

## Level 5 — Integration

**28. Scenario A — a file is 100 bytes. How many bits does that represent?**

```text
1 byte = 8 bits
100 bytes × 8 bits/byte = 800 bits
```

Answer: **800 bits**. The reasoning is a direct application of the fixed 8-bits-per-byte
relationship from Section 1/Section 5 — multiply the byte count by 8.

**29. Scenario B — a 2 GB AI model artifact. Why does its byte count matter for storage and
memory?**

For storage: the file has to physically fit within whatever storage device or allocated storage
space is available — a 2 GB file requires the storage system to have at least that much free
capacity, measured ultimately in bytes. For memory: before the model can actually be used
(loaded and run), its data typically needs to be brought into the computer's working memory — a
2 GB model requires enough memory capacity to hold it, and loading that much data takes real time,
proportional to its size (connecting back to Section 3's data-movement point). Both concerns trace
directly back to the fact that "2 GB" is a concrete, meaningful count of actual bytes that must be
stored and moved, not an abstract label.

**30. Scenario C — a system receives bits from another system. Why does it need to know the
encoding/context before interpreting them?**

As established in Section 6, a bit pattern has no built-in, automatic meaning — the same exact
bits could correctly represent a number under one interpretation and something completely
different (a character, part of an image, part of an instruction) under another. If the receiving
system doesn't know which interpretation/encoding the sending system used, it has no reliable way
to recover the intended meaning of the bits — it might misinterpret them as the wrong kind of data
entirely. Agreeing on encoding/context in advance is what makes the bits meaningful and usable
once received.

---

_This answer key covers Concept 4 (Binary, Bits, and Bytes) only. It does not contain, reference,
or anticipate answers for Concept 5 (Hexadecimal) or any later concept._
