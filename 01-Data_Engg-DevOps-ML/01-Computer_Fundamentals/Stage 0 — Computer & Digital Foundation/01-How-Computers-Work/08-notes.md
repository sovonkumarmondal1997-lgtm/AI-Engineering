# Compilation and Interpretation

**Module:** Stage 0 — Module 0.1: How Computers Work | Concept 8

---

## 1. What Are Compilation and Interpretation?

- **Source code:** Human-readable code written in languages such as Python or C.
- **Compiler:** Software that translates a program into another representation.
- **Compilation:** The translation process. It can happen before execution (AOT) or during execution (JIT).
- **Interpreter:** Software that carries out a program's behavior using its runtime representation.
- **Bytecode:** An intermediate form executed by a runtime or virtual machine, not directly by the CPU.
- **Executable:** A program representation the operating system can launch.
- **Runtime:** Software that supports a program while it runs.
- **Virtual machine:** In this lesson, software that provides an environment for executing bytecode.

---

## 2. Why Are They Needed?

A CPU executes machine instructions, not Python or C source code. Compilation and interpretation bridge the gap between human-readable programs and actual hardware execution.

The basic idea is:

```
Source code → language implementation → lower-level representation → hardware execution
```

---

## 3. How Do the Approaches Work?

- **Ahead-of-time (AOT) compilation:** Source code is compiled before the program runs, often into a native executable containing machine code.
- **Interpreted-style execution:** A runtime or interpreter carries out a program's behavior while it runs. The CPU still executes machine instructions underneath.
- **Bytecode and virtual machine:** Source code is compiled into bytecode, which a runtime executes.
- **JIT compilation:** During execution, a runtime compiles some code into native machine code.
- **Hybrid execution:** Real systems often combine compilation, interpretation, and JIT compilation.

Compilation does not always produce machine code; its output depends on the implementation.

---

## 4. How Do C, Python, Java, and AI Applications Differ?

- **C:** Commonly compiled ahead of time into a native executable.
- **Python:** A common implementation compiles source into bytecode or another runtime representation, then executes it through a runtime.
- **Java:** Source is compiled into bytecode, which the JVM executes and may JIT-compile.
- **AI applications:** A line such as `output = model(input)` passes through Python, runtime and framework layers before work reaches the CPU or GPU.

A language itself is not permanently "compiled" or "interpreted." Its implementation determines how it executes.

---

## 5. Practical Linux/WSL2 Exercises

The module teaches you to:

- Check tools with `which gcc`, `which python3`, `which javac`, `which java`, `which objdump`, and `which file`.
- Check architecture using `uname -m`.
- Compile a C program with `gcc program.c -o program`.
- Inspect executable type with `file program`.
- Inspect machine instructions with `objdump -d program | head -40`.
- Check Python with `python3 --version` and `python3 -c "import sys; print(sys.implementation.name)"`.
- Run a Python script using `python3 example.py`.
- Compare source code, executables, machine-code disassembly, and program output.

The exercises use a temporary directory, require no automatic tool installation, and should not modify the roadmap's existing project folder. Clean up afterward with `rm -rf /tmp/compilation-lesson`.

---

## 6. Common Mistakes, Exercises, and AI Relevance

Remember: bytecode is not machine code; interpreted programs still use the CPU; Python can involve compilation; one source line does not equal one CPU instruction; and compiled does not automatically mean faster. Executables can also depend on CPU architecture.

The module ends with troubleshooting scenarios, 40 exercises across recognition, understanding, application, debugging, and integration, plus review questions and production relevance. These prepare you for dependency management, deployment, profiling, performance engineering, and AI inference systems.

---

## Next Concept

**Cache** — the next step toward understanding how CPUs access data efficiently.
