# Instructions and Machine Code

**Module:** Stage 0 — Module 0.1: How Computers Work | Concept 7

---

## 1. What Are Instructions and Machine Code?

- **CPU instruction:** A precise operation telling the CPU what to do, such as adding, comparing, or moving values.
- **Machine code:** The exact binary-encoded instructions that a particular CPU architecture can execute.
- **Instruction encoding:** Converting an operation into its specific bit pattern.
- **Instruction set:** The collection of operations supported by a CPU architecture.

A CPU cannot understand English commands. It needs exact instructions with no ambiguity.

---

## 2. Why Are They Important?

The CPU needs precise operations to perform calculations reliably. Instructions specify what operation to perform and which values or locations to use.

Common instruction categories include:

- **Data movement:** Load, store, move.
- **Arithmetic:** Add, subtract, multiply.
- **Logical/bit operations:** AND, OR, XOR, shift.
- **Comparison and control flow:** Compare, jump, conditional branch.

---

## 3. How Does a CPU Execute Instructions?

The basic process is:

1. **Fetch:** Obtain the next instruction.
2. **Decode:** Identify the operation and its operands.
3. **Execute:** Perform the operation using CPU resources, such as the ALU and registers.
4. **Update state:** The result may change register values or other CPU state.

An instruction generally contains an **opcode** (the operation), **operands** (the values or locations involved), and sometimes an **immediate value** (a fixed value included in the instruction).

---

## 4. How Do Binary and Hexadecimal Relate to Machine Code?

Machine code consists of architecture-specific bit patterns. Binary represents those bits using 0 and 1; hexadecimal displays them more compactly.

The lesson gives a real x86-64 example:

- **Human-readable disassembly:** `add eax,edx`
- **Machine-code bytes:** `01 d0`
- **Binary representation:** `00000001 11010000`

This encoding is specific to that instruction and architecture. It is not universal across all CPUs.

---

## 5. How Does This Relate to Python and AI Engineering?

The execution path is approximately:

```
AI application → Python/framework → runtime or compiler → lower-level operations → machine instructions → CPU execution
```

One Python statement, such as `x = 5 + 3`, does not necessarily equal one CPU instruction. Python code must go through additional processing before CPU execution.

Understanding this foundation helps with future learning in performance engineering, profiling, systems programming, and AI inference optimization.

---

## 6. Practical Linux/WSL2 Commands

The module teaches how to inspect compiled code safely:

- `which gcc`, `which objdump`, `which xxd` — check tool availability.
- `gcc -O0 -c add.c -o add.o` — compile a small C function into an object file.
- `file add.o` — identify the file format and architecture.
- `xxd add.o` — display raw bytes in hexadecimal.
- `objdump -d -M intel add.o` — display a human-readable disassembly.
- `od -Ax -tx1z add.o | head` — alternative byte inspection.
- `rm -rf /tmp/instructions-lesson` — remove the lesson's temporary directory when finished.

> **Important:** `xxd` shows bytes, while `objdump` interprets relevant bytes as instructions. Neither shows the CPU's live execution state.

---

## 7. Common Mistakes and Practice

Remember that binary is not automatically machine code, assembly-style text is not the actual machine code, hexadecimal is only a display notation, and x86-64 and ARM64 generally use incompatible machine-code encodings.

The module finishes with recognition, understanding, conversion, application, debugging, and integration exercises, plus review questions. These test your ability to identify instructions, opcodes, operands, architecture-specific encodings, and the difference between data and instructions.

---

## Next Lesson

**Concept 8 — Compilation and Interpretation**, which explains how human-written code becomes executable operations.
