# Binary, Bits, and Bytes

**Module:** How Computers Work — Stage 0, Module 0.1

---

## 1. What Are Binary, Bits, and Bytes?

Computers need a way to represent information such as numbers, text, images, videos, and instructions.

- **Binary:** A number system that uses only two digits: `0` and `1`.
- **Bit:** The smallest unit of digital information. It can have one of two values: `0` or `1`.
- **Byte:** A standard group of 8 bits.

Computers use two distinguishable electronic states because they are more reliable to detect than many different states. The symbols 0 and 1 represent these physical states; electricity itself is not literally zeroes and ones.

---

## 2. How Many Values Can Bits Represent?

Every additional bit doubles the number of possible patterns.

| Bits | Possible patterns |
|---|---|
| 1 bit | 2 |
| 2 bits | 4 |
| 3 bits | 8 |
| 4 bits | 16 |
| 8 bits (1 byte) | 256 |

The formula is $2^n$, where $n$ is the number of bits. Therefore, one byte has 256 possible patterns. When interpreted as an unsigned number, these represent values from 0 to 255.

---

## 3. How Do We Convert Binary Into Decimal?

Each binary position has a value based on powers of two:

```
8  4  2  1
```

For example, binary `1011` means:

$8+0+2+1=11$

Only add the position values where the binary digit is 1. Leading zeros do not change a number: `101` and `00000101` both represent decimal 5.

---

## 4. How Does a Computer Represent Different Information?

A bit pattern has no universal meaning. Its meaning depends on the system interpreting it.

For example, `01000001` can represent decimal 65 or the character `A` under a suitable character-encoding standard.

- **Text:** Characters are mapped to numeric codes and then binary.
- **Images:** Pixel colors are represented by numeric values and binary.
- **AI models:** Learned parameters are stored as binary data.
- **Datasets, documents, audio, logs, and network data:** Ultimately represented using bits and bytes.

---

## 5. Why Does This Matter in AI Engineering?

Data size affects storage capacity, memory requirements, transfer time, system capacity, performance, and cost.

Common decimal units are:

- **KB:** approximately 1,000 bytes
- **MB:** approximately 1 million bytes
- **GB:** approximately 1 billion bytes
- **TB:** approximately 1 trillion bytes

MB and MiB differ: MB uses powers of 1,000, while MiB uses powers of 1,024.

---

## 6. Practical Commands

In WSL2/Ubuntu, try:

- `echo "obase=2; 5" | bc` — converts decimal 5 into binary (`101`).
- `command -v bc` — checks whether `bc` is available.
- `printf 'A' | od -An -tx1` — displays the byte for `A` in hexadecimal.
- `printf '%d\n' 5` — displays decimal 5; it does not convert it to binary.

These commands are read-only. If a utility is unavailable, the worked examples are sufficient to learn the concepts.

---

## 7. Common Mistakes and Practice

Remember: binary is a representation system, not a programming language. One byte is not enough for every value, and the same bits can mean different things under different interpretation rules. More bytes also do not automatically mean better data.

Complete the module's exercises and review questions: identify bits and bytes, calculate combinations, convert binary and decimal, perform binary addition, debug misconceptions, and explain why a 2 GB AI model requires storage and memory.

**Expected outcome:** Understand binary representation, convert simple numbers in both directions, perform basic binary addition, and explain how data size affects AI systems.

---

## Next Lesson

**Hexadecimal** — a more compact way to write binary information.
