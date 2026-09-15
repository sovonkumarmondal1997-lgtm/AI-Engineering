# Concept 8 — Compilation & Interpretation — Answer Key

> **Answer Key — Open Only After Attempting the Exercises**
>
> This file contains reasoning and explanations for every exercise in
> [`../08-compilation-and-interpretation.md`](../08-compilation-and-interpretation.md), Section
> 13. Attempt every question yourself first, with your own worked reasoning, before reading any
> answer below.

---

## Level 1 — Recognition

**1. What is source code?** The human-readable text a person writes in a programming language —
the original form a program starts from, before any translation or execution.

**2. What is a compiler?** A program that translates one representation of a program into another
representation, before that program runs.

**3. What is compilation?** The process a compiler performs — translating a program's
representation into another representation, ahead of execution.

**4. What is an interpreter?** A program that carries out what a program representation means, at
the time it runs, rather than only translating it ahead of time into something else first.

**5. What is interpretation?** The process an interpreter performs — executing a program
representation's meaning directly, at runtime.

**6. What is an executable?** A file containing a program in a form the operating system can load
and run directly — commonly containing native machine code.

**7. What is bytecode?** A translated, intermediate representation of a program, produced by a
compiler, meant to be run by a separate runtime/virtual machine — not the same thing as CPU
machine code.

**8. What is a runtime?** The software system present while a program is actually running, that
supports its execution.

**9. What is a virtual machine, in the sense this lesson uses the term?** A software system that
executes bytecode — an execution environment that sits between bytecode and the physical CPU
(distinct from a virtualized-computer "virtual machine").

**10. What is JIT compilation?** Just-In-Time compilation — compiling code during a program's
execution, rather than entirely beforehand.

**11. Is bytecode the same thing as machine code?** No. Bytecode is instructions for a virtual
machine/runtime; machine code is instructions encoded for a specific CPU architecture. A CPU
cannot execute bytecode directly without a runtime interpreting or JIT-compiling it first.

**12. Is "compiled" or "interpreted" a fixed, permanent property of a language itself?** No.
Compilation and interpretation are implementation strategies; the same language can have multiple
implementations, potentially using different strategies.

---

## Level 2 — Understanding

**13. Why do programming languages need an implementation mechanism at all?**

Because a CPU only ever executes precise, architecture-specific machine code (Concept 7) and has
no built-in capacity to understand human-readable source code directly. Something must bridge the
gap between what a human writes and what the CPU can actually run — that bridging mechanism is a
language implementation (a compiler, interpreter, or some hybrid).

**14. What is compilation?**

The process of translating a program's source representation into another representation (which
could be native machine code, bytecode, or another intermediate representation), performed before
that translated result is executed.

**15. What is interpretation?**

Executing a program representation's meaning directly, at runtime, via an interpreter — without
necessarily first producing a separate, permanent, native executable.

**16. What is the difference between source code and machine code?**

Source code is human-readable program text in a programming language. Machine code is the
binary-encoded representation of instructions that a specific CPU architecture can execute
directly (Concept 7). They are fundamentally different representations, connected by some
translation/execution mechanism (this lesson's subject).

**17. What is bytecode?**

An intermediate representation produced by a compiler, meant to be executed by a runtime/virtual
machine rather than directly by a physical CPU.

**18. Why is bytecode not the same as machine code?**

Because they target different execution mechanisms: bytecode is meant for a virtual
machine/runtime to interpret or JIT-compile; machine code is meant for a physical CPU to execute
directly, encoded specifically for that CPU's architecture (Concept 7). A CPU cannot run bytecode
without an intermediary runtime.

**19. Why is "Python is interpreted" an incomplete description?**

Because common Python implementations actually involve a genuine compilation step (translating
source to bytecode) before a runtime executes that bytecode — "interpreted" alone omits this
compilation step, giving an incomplete picture of what commonly happens.

**20. Why can a system use both interpretation and JIT compilation?**

Because these are complementary techniques, not mutually exclusive ones — a runtime can interpret
some parts of a program's representation while JIT-compiling other parts into native machine code
during execution, combining both approaches within the same overall execution process (as with
many real JVM implementations).

**21. Why can the same language have different execution implementations?**

Because a language is a specification (syntax and meaning), not an execution strategy — different
people/organizations can build different implementations of that same specification, each freely
choosing compilation, interpretation, or a hybrid approach, since nothing about the language
itself mandates one particular strategy.

**22. Why does an interpreted program still ultimately involve hardware execution?**

Because the interpreter itself is software, and all software ultimately runs as machine
instructions on the CPU (Concept 2, Concept 7). Interpretation adds a layer of software (the
interpreter) directing the CPU's work to carry out the target program's behavior — it does not
remove the CPU from the process; it just means the CPU is executing the interpreter's instructions
rather than dedicated native machine code compiled specifically from the target program.

---

## Level 3 — Application

### Exercise A — Execution pipeline: `x = 10 + 20`

**23. Conceptual path:**

```text
Python source (x = 10 + 20)
      ↓
Python implementation (processes the source)
      ↓
bytecode / runtime representation (a translated intermediate form)
      ↓
runtime execution (a runtime carries out that representation's meaning)
      ↓
lower-level machine instructions (real CPU-executable instructions, per Concept 7)
      ↓
CPU (actually performs the work)
```

This is a simplified model of a common implementation approach — not a guaranteed description of
every possible Python implementation.

### Exercise B — Compare approaches

**24.**

| | C | Python (common implementation) | Java |
|---|---|---|---|
| Source code | Human-readable C text | Human-readable Python text | Human-readable Java text |
| Translation | Ahead-of-time compilation | Compilation to bytecode | Compilation to bytecode |
| Intermediate representation | Generally none (goes straight to machine code) | Bytecode | Bytecode |
| Runtime | Minimal — mostly OS + CPU | Substantial — executes bytecode | Substantial — JVM executes bytecode, possibly with JIT |
| Machine code | Produced entirely ahead of time by the compiler | Ultimately involved when the runtime executes on the CPU | Produced ahead of time (initial compile) and/or at runtime (JIT) |

### Exercise C — Identify representation

**25. A `.py` file you wrote containing Python statements.** Source code — human-readable text in
a programming language, the original form you wrote.

**26. The output of running `objdump -d` on a compiled C program.** Disassembly — a human-readable
rendering of the compiled program's machine-code instructions, produced by analyzing the
executable; not the source code, and not the machine code bytes themselves (though it describes
them).

**27. The file produced by running `gcc program.c -o program`.** An executable — a file
containing (in this case) native machine code that the operating system can load and the CPU can
execute directly.

**28. The internal representation a Java compiler produces before the JVM runs it.** Bytecode —
an intermediate representation meant for the JVM (a virtual machine) to execute, not the original
source code and not native CPU machine code.

### Exercise D — Abstraction: `result = model(input)`

**29.** This Python statement expresses a high-level intent, but a CPU cannot execute Python
source text directly (Concept 7's foundational point, restated by this lesson). Between this line
and actual hardware execution sits a Python implementation, likely an AI framework, and eventually
CPU or GPU execution (Section 9, Example 4) — a conceptual stack, not a single universal pipeline,
none of which is directly "Python source text" at the point actual computation happens.

---

## Level 4 — Debugging

**30. "Python cannot be compiled."**

Wrong: common Python implementations do perform a genuine compilation step, translating source
code into bytecode, before a runtime executes that bytecode (Misconception 2). "Python source
isn't typically compiled all the way to a standalone native executable like C" would be a more
precise, correct claim.

**31. "Bytecode is machine code."**

Wrong: bytecode is instructions for a virtual machine/runtime; machine code is instructions
encoded for a specific CPU architecture. A CPU cannot directly execute bytecode without a runtime
interpreting or JIT-compiling it first (Misconception 4).

**32. "Interpreted programs do not use the CPU."**

Wrong: the interpreter itself is software running as machine instructions on the CPU — it uses
that execution to carry out the target program's behavior. The CPU is always involved on a
CPU-based system, whether execution is interpreted, compiled, or hybrid (Misconception 9).

**33. "Java is purely interpreted."**

Wrong: Java source is compiled to bytecode first (a genuine compilation step), and the JVM may
further JIT-compile bytecode into native machine code during execution — "purely interpreted"
omits both the initial compilation and the possible JIT compilation (Misconception 5).

**34. "Compilation and interpretation cannot be combined."**

Wrong: many real, common systems combine both — compiling source to bytecode, then interpreting
and/or JIT-compiling that bytecode at runtime (Section 6, Section 8, Section 9's Java example)
(Misconception 10).

**35. "One source-code line becomes one CPU instruction."**

Wrong: a single line of source code typically corresponds to multiple lower-level
operations/instructions, not exactly one — this holds whether the compilation target is native
machine code or bytecode (Misconception 7, extending Concept 7's identical point about Python
statements).

---

## Level 5 — Integration

### Scenario A — Python AI application

**36. Known vs. deferred, by stage:**

```text
Python AI application
      ↓  [KNOWN: high-level code expressing intent, not directly CPU-executable — Concept 7,
          this lesson's Section 7]
Python implementation
      ↓  [KNOWN (conceptually): involves some translation/compilation step, per Section 7-8;
          DEFERRED: exact CPython/implementation internals — explicitly out of scope]
runtime representation
      ↓  [KNOWN: bytecode/intermediate representation concept, per Section 1, Section 5;
          DEFERRED: exact representation used by any specific real implementation]
runtime execution
      ↓  [KNOWN: a runtime carries out this representation's meaning, per Section 6;
          DEFERRED: interpreter/VM/JIT implementation internals — explicitly out of scope]
lower-level operations
      ↓  [KNOWN: eventually becomes real instructions, per Concept 7]
CPU/GPU
      [KNOWN: CPU execution model from Concept 2/3/7; DEFERRED: GPU — a later concept file,
       not yet taught]
```

### Scenario B — Deployment across architectures

**37. Why might the existing executable not work on the new architecture?**

Because a compiled executable contains native machine code, which is architecture-specific
(Concept 7) — a CPU physically built to recognize one architecture's instruction encoding
generally cannot execute machine code encoded for a different architecture.

**38. Why can the source code sometimes be reused?**

Because source code is written at a higher level of abstraction (Section 4), independent of any
specific CPU architecture — it expresses intent, not architecture-specific instructions. It can be
recompiled for the new architecture, producing new, architecture-appropriate machine code, even
though the original executable cannot be reused directly.

**39. What role does CPU architecture play?**

CPU architecture determines the specific instruction set (Concept 7, Section 8 of this lesson)
that machine code must be encoded for. Since different architectures define different instruction
sets, machine code is never automatically portable between them — only source code (or an
intermediate representation not yet tied to a specific architecture) can realistically move
between architectures, requiring a fresh compilation step for each target.

### Scenario C — Performance

**40. Critique: "Compiled always means faster than interpreted."**

This oversimplifies a genuinely nuanced situation. It depends on: **implementation** — a poorly
implemented compiler or a well-optimized interpreter/JIT could reverse the expected outcome, and
"compiled" doesn't specify what it's compiled *to* (native machine code vs. bytecode, Section 5)
— a compile-to-bytecode approach still requires runtime execution, which has its own performance
characteristics. **Workload** — some workloads may not meaningfully benefit from ahead-of-time
compilation if, for example, they spend most of their time waiting on other resources rather than
executing CPU instructions (a point this lesson doesn't develop further, but which prevents any
blanket "compiled = faster" claim). **Runtime and JIT** — a JIT compiler (Section 6) can compile
frequently-used code to native machine code during execution, sometimes narrowing or eliminating
performance gaps with AOT-compiled code for long-running programs. **Startup/runtime trade-offs**
— AOT-compiled programs typically start immediately (translation already happened, Section 3's
"startup behavior" point), while JIT-based systems may have startup or warm-up costs as
compilation happens during early execution — meaning "faster" can depend heavily on whether you're
measuring a program's startup time or its long-running throughput. Overall: "compiled always means
faster" ignores implementation quality, exactly what's being compiled to, workload
characteristics, and the specific trade-offs different runtimes make — it is not a reliable,
universal claim.

---

_This answer key covers Concept 8 (Compilation & Interpretation) only. It does not contain,
reference, or anticipate answers for Concept 9 (Cache) or any later concept._
