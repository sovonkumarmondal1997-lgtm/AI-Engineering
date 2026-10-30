# Hexadecimal

**Module:** How Computers Work — Stage 0, Module 0.1

---

## 1. What Is Hexadecimal?

**Hexadecimal (hex)** is a base-16 number system used to represent values with 16 symbols:

```
0 1 2 3 4 5 6 7 8 9 A B C D E F
```

The letters represent these decimal values: A = 10, B = 11, C = 12, D = 13, E = 14, and F = 15.

Unlike binary, which uses only 0 and 1, hexadecimal can represent larger values using fewer digits.

---

## 2. Why Is Hexadecimal Useful?

Long binary numbers are difficult for humans to read and copy accurately. For example:

- **Binary:** `1101011010111010`
- **Hexadecimal:** `D6BA`

Both represent the same value. Hexadecimal makes values easier for humans to read; it does not make the computer more efficient or reduce the actual stored data.

---

## 3. The Most Important Rule: 1 Hex Digit = 4 Bits

Four binary bits can form $2^4=16$ different patterns, exactly matching hexadecimal's 16 symbols.

| Binary | Hex | Binary | Hex |
|---|---|---|---|
| 0000 | 0 | 1000 | 8 |
| 0001 | 1 | 1001 | 9 |
| 0010 | 2 | 1010 | A |
| 0011 | 3 | 1011 | B |
| 0100 | 4 | 1100 | C |
| 0101 | 5 | 1101 | D |
| 0110 | 6 | 1110 | E |
| 0111 | 7 | 1111 | F |

A group of 4 bits is called a **nibble**. Since a byte contains 8 bits, one byte equals two nibbles, or two hexadecimal digits.

---

## 4. How Do Conversions Work?

- **Binary to hex:** Split binary into groups of four bits from the right and convert each group using the table. Example: `10101100` → `1010 1100` → `AC`.
- **Hex to binary:** Replace each hex digit with its four-bit pattern. Example: `3F` → `0011 1111`.
- **Hex to decimal:** Multiply each digit by its positional value, based on powers of 16. Example: `2A` = $2×16+10=42$.
- **Hex place values:** From right to left, they are 1, 16, 256, 4096, and so on.

Hexadecimal is a positional number system, just like decimal and binary. Decimal `10` means ten, but hexadecimal `10` means sixteen.

---

## 5. Where Will You Use It in AI Engineering?

Hexadecimal commonly appears in memory-related output, debugging tools, technical logs, identifiers, hashes, and raw file inspection. AI models, datasets, images, documents, and serialized artifacts contain underlying binary data that tools may display in hexadecimal.

Remember: hexadecimal is a human-readable representation, not what AI systems use as a separate internal calculation mode.

---

## 6. Practical Linux/WSL2 Commands

- `printf '%x\n' 255` — displays `ff`.
- `printf '%02x\n' 10` — displays `0a`, padding the value to two digits.
- `echo -n 'AI' > /tmp/hex-lesson-demo.txt` — creates a temporary file.
- `xxd /tmp/hex-lesson-demo.txt` — displays its bytes in hexadecimal.
- `which xxd` — checks whether `xxd` is available.
- `od -An -tx1 /tmp/hex-lesson-demo.txt` — alternative hexadecimal byte display.
- `rm /tmp/hex-lesson-demo.txt` — removes the temporary file.

These commands are for observation; the file-inspection example creates and removes a temporary file. The hex characters displayed by `xxd` or `od` are not necessarily the literal characters stored in the file; they are a readable display of its bytes.

---

## 7. Common Mistakes and Practice

- Hexadecimal is a number system, not a programming language.
- `F` means 15 only when interpreted as a hexadecimal digit.
- `FF` equals 255 under the unsigned 8-bit interpretation.
- One hex digit represents 4 bits, not 8.
- `A`, `0A`, and `00A` have the same numeric value; leading zeros may be used for consistent formatting.
- `2A` equals 42, not 12; place values matter.
- A value such as `FACE` is valid hexadecimal, but `G` is not a valid hex digit.
- Always identify the number's base before interpreting it.

Complete the lesson's exercises and review questions: practice conversions in all directions, explain the nibble/byte relationship, debug incorrect calculations, and reason about inspecting AI artifacts.

**Expected outcome:** Read hexadecimal confidently, convert between binary, decimal, and hexadecimal with reasoning, and understand why engineers use it.

---

## Next Lesson

**Registers** — small, fast storage locations inside the CPU.
