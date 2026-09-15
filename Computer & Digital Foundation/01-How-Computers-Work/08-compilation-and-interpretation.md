# Compilation and Interpretation

**Module:** How Computers Work
**Roadmap reference:** Stage 0 — Module 0.1 — How Computers Work
**Concept(s) covered:** compilation, interpretation
**Status:** Not Started

---

## 1. What is it?

**Starting from what you already know.** Concept 7 established what an instruction and machine
code actually are, and made a deliberately unresolved point: a Python statement like `x = 5 + 3`
does **not** necessarily correspond to one CPU instruction (Concept 7, Section 10, Example 3). This
lesson finally answers the question that left open: **how does human-written code actually become
something a CPU can execute?**

Rather than defining every term at once, this section introduces them **progressively**, in the
order you'll need them.

**Source code — simple meaning:** Source code is the human-readable text a person writes in a
programming language — for example, a Python file, or a C file. It's called "source" because it's
the original form a program starts from, before anything happens to it.

**Compiler — simple meaning:** A compiler is a program that translates one representation of a
program into another representation, before that program runs.

**Compilation — simple meaning:** Compilation is the process a compiler performs — translating a
program's representation into another representation, ahead of execution.

**Interpreter — simple meaning:** An interpreter is a program that carries out what a program
representation means, at the time it runs, rather than only translating it ahead of time into
something else first.

**Interpretation — simple meaning:** Interpretation is the process an interpreter performs —
executing a program representation's meaning directly, at runtime.

**Executable — simple meaning:** An executable is a file containing a program in a form the
operating system can load and run directly — commonly, though not always, containing native
machine code (Concept 7).

**Bytecode — simple meaning:** Bytecode is a translated form of a program, produced by a
compiler, but **not** the same thing as CPU machine code (Concept 7) — it's an intermediate
representation meant to be run by a separate piece of software (introduced next), not directly by
the CPU. Section 5 covers this distinction fully; for now, just note that bytecode is a distinct
category from both source code and machine code.

**Runtime — simple meaning:** "Runtime" refers, broadly, to the software system present while a
program is actually running, that supports its execution — this term will be used carefully and
specifically throughout this lesson, since it means different things depending on context (a
runtime environment, or "at runtime" meaning "during execution").

**Virtual machine (in this context) — simple meaning:** A virtual machine, in the sense used in
this lesson, is a software system that executes bytecode — providing an execution environment
that isn't the physical CPU directly, but sits between bytecode and the CPU. (This is a different,
specific meaning from "virtual machine" as in a virtualized computer — like the WSL2 environment
you've used throughout this module — a distinction Section 11 returns to if it comes up.)

**JIT compilation — simple meaning:** "JIT" stands for **Just-In-Time** — compilation that happens
*during* a program's execution, rather than entirely beforehand. Section 5 and Section 6 explain
this properly; it's introduced here only by name.

**Why so many terms, all at once?** Because this lesson's entire point is that there is **not one
single execution pipeline** every programming language follows — different languages, and even
different implementations of the *same* language, combine these pieces (compiler, interpreter,
bytecode, virtual machine, JIT) in different ways. Having all these terms defined up front lets
Section 5 through Section 9 show you exactly how they combine differently across real, common
languages.

---

## 2. Why does it exist?

**The fundamental problem.** Concept 7 established that a CPU only ever executes precise,
architecture-specific machine code — it has no capacity to understand human-readable source code
directly (Concept 7, Section 1's recipe-analogy caution; Concept 7, Misconception 8). At the same
time, writing raw machine code by hand is extraordinarily impractical for humans — tedious,
error-prone, and disconnected from how people naturally think about solving problems.

**This creates a real abstraction gap that must be bridged somehow:**

```text
Human-readable code
        ↓
Programming-language implementation
        ↓
Lower-level representation
        ↓
Machine-level execution
```

Programming languages exist specifically to let humans express what they want a program to do at
a much higher, more manageable level of abstraction than machine code — using words, structure,
and logic that map to how people think, rather than to how a specific CPU architecture encodes
instructions (Concept 7's central theme). But because the CPU only ever executes machine code,
**something** has to bridge the gap between what a human wrote and what the CPU can actually run.

**Why a programming language cannot simply be executed directly by a CPU as written:** Exactly as
Concept 7 established, a CPU's circuitry is physically built to recognize only its own
architecture-specific instruction encoding — nothing resembling Python or C syntax. No matter how
"simple" a line of source code looks to a human, the CPU has no built-in mechanism for
understanding it directly. **Compilation and interpretation are two different general strategies
for bridging this gap** — mechanisms that transform or execute human-written code so that,
eventually, real machine-level work happens on real hardware.

**This is the direct, explicit connection to Concept 7:** everything this lesson covers is, in the
end, about how various strategies eventually produce or carry out the kind of instructions Concept
7 described. This lesson doesn't introduce a new destination — it explains the different *roads*
that lead there.

---

## 3. Why does an Applied AI Engineer need to understand it?

You interact with this abstraction gap constantly, every time you run Python code for AI work —
even though you may never have thought about it explicitly before this lesson.

**Concrete connections to your future work, kept foundational here:**

- **Python** — nearly all AI application code you'll write is Python; understanding that Python
  code goes through *some* implementation mechanism before anything executes is the direct
  foundation for everything else in this list.
- **AI frameworks** — the libraries you'll use (not named or taught here) are themselves software,
  built using some combination of the approaches this lesson describes.
- **Inference runtimes** — running a trained AI model to get a prediction involves a "runtime" in
  the sense this lesson defines — a supporting software system present while that execution
  happens. (This lesson does not teach what an "inference runtime" specifically does — only that
  the general concept of a runtime, introduced here, applies there too.)
- **Application performance** — later, when you study performance engineering (not taught here),
  understanding whether code is compiled, interpreted, or JIT-compiled will matter directly to
  reasoning about why something is fast or slow.
- **Startup behavior** — some programs take longer to start than others; this is often connected
  to *when* translation happens (Section 5's "when translation occurs" comparison) — a compiled
  program's translation already happened before you ran it; other approaches may do some
  translation work at startup or during execution.
- **Portability** — Concept 7 established that machine code is architecture-specific; this lesson
  will show (Section 9, Section 13 Scenario B) why source code is often more portable across
  different systems than a compiled executable is.
- **Dependencies** — running Python code depends on having a Python implementation installed;
  understanding what that implementation actually does (Section 7) demystifies why this dependency
  exists at all.
- **Debugging** — error messages and debugging tools sometimes reference concepts from this lesson
  (like "bytecode" or "compiled" vs. "interpreted" behavior); recognizing these terms prevents
  unnecessary confusion.
- **Deployment** — later stages of the roadmap (not taught here) will cover packaging and
  deploying AI applications; that work assumes you understand the basic distinction between source
  code and what actually gets executed.
- **CPU/GPU execution** — a later concept file (GPU) will build on the CPU-execution foundation
  from Concept 2 and Concept 7; this lesson's Section 9, Example 4 previews, only conceptually,
  how Python AI code eventually reaches either CPU or GPU execution.

**The concrete question this lesson equips you to start answering:**

```python
result = model(input)
```

What actually happens between this one line of Python and real hardware execution? This lesson
does not give you the complete, specific answer for any particular AI framework (that's far
outside Stage 0's scope) — but it gives you the **general conceptual vocabulary** (compilation,
interpretation, bytecode, runtime, JIT) needed to eventually understand that answer, whenever you
encounter it later in the roadmap. **This lesson does not teach model optimization, CUDA, GPU
kernels, compiler optimization, or inference-engine internals** — each of those is explicitly a
future topic.

---

## 4. Beginner Explanation

**A first analogy: translation.**

```text
Human language
      ↓
translator
      ↓
language another system understands
```

Imagine you need to communicate an instruction to someone who only speaks a different language.
A translator listens to your instruction (in your language) and produces an equivalent
instruction in the other language — the *meaning* is preserved, but the *form* changes
completely. This is a reasonable first mental image for **compilation**: a compiler takes source
code (in a human-readable language) and produces a translated version, in a different
representation (Section 1) — ahead of time, before anyone acts on it.

**Where this analogy is useful:** It captures the core idea of translation happening as a
distinct, complete step, producing a separate, finished result — matching compilation's basic
shape well.

**Where it breaks down:** A human translator understands meaning and context flexibly; a compiler
follows exact, mechanical rules with no flexibility or judgment (echoing Concept 7's point about
CPU precision). Also, a translator translates once, into a finished result meant to be used later
— but as Section 5 and Section 8 will show, not every programming-language implementation follows
this exact "translate everything, then run it later" shape.

**A second analogy, for interpretation:**

```text
A live interpreter helps execute instructions as they are encountered.
```

Imagine, instead, a live interpreter at a meeting — someone who listens to an instruction in one
language and immediately conveys its meaning and carries out an appropriate response in real
time, as the instruction is encountered, rather than translating an entire document in advance.
This is a reasonable first mental image for **interpretation**: rather than producing a complete,
separate translated version ahead of time, an interpreter (the software kind, from Section 1)
carries out a program representation's meaning as it goes.

**An immediate, required correction to this second analogy:** Real programming-language
interpreters are considerably more technically sophisticated than "a live human interpreter."
Crucially — and this is explicitly required by this lesson — **interpretation does not mean
"reading source code character by character" or line by line, in some naive way.** Real
interpreters generally operate on some structured representation of the program (for example, a
program that's already been broken down into a more organized internal form) rather than raw
source text — this lesson does not teach exactly how that structuring happens (that belongs to
genuinely advanced compiler-construction topics, explicitly out of scope), but the misconception
that interpretation is a simple, naive text-reading process must be corrected here directly (see
also Section 11, Misconception 3).

**What you should leave this section understanding:**

```text
Compilation:
translate before execution

Interpretation:
execute a program representation through a runtime mechanism
```

**And, critically, stated explicitly and immediately:** real systems can, and very commonly do,
**combine both approaches** — this is not an either/or choice for most real, modern programming
language implementations. Section 5 (hybrid execution) and Section 8 (the comparison table) both
return to this directly. Holding "compiled" and "interpreted" as two mutually exclusive categories
is precisely the oversimplification this lesson's Primary Learning Objective requires you to move
beyond.

---

## 5. Technical Explanation

### Compilation

```text
source program
    ↓
compiler
    ↓
target representation
```

A compiler takes a source program (or, in some systems, another intermediate representation) and
produces a **target representation** — the output of compilation. This target representation can
be one of several different things, depending on the specific compiler and system:

- **Native machine code** — instructions encoded directly for a specific CPU architecture (Concept
  7) — ready, potentially after some further steps this lesson does not cover, to be executed
  directly by that CPU.
- **Bytecode** — an intermediate representation (Section 1) meant to be executed by a separate
  runtime/virtual machine, not directly by the CPU.
- **Intermediate representation** — a general term for a representation that sits somewhere
  between source code and a final target, potentially used as a stepping stone within a compiler's
  own internal process (this lesson does not teach intermediate-representation design — that's
  explicitly out of scope).

**The key point: "compilation" does not automatically mean "produces native machine code."**
Compilation is a *translation process*; what it translates *into* varies by system, which is
exactly why the required distinctions at the top of this lesson insist on separating "compilation"
from "produces machine code" as two different claims.

### Interpretation

```text
program representation
    ↓
interpreter/runtime
    ↓
execution
```

An interpreter takes a program representation (which, as Section 4 clarified, is not necessarily
raw, unprocessed source text) and carries out its meaning directly, producing execution — actual
program behavior — without necessarily producing a separate, permanent, native executable file as
an end product first.

### Hybrid execution

```text
source
   ↓
bytecode/intermediate representation
   ↓
runtime
   ↓
interpreter and/or JIT
   ↓
machine code
   ↓
CPU
```

Many real, common systems combine compilation and interpretation together: source code is first
compiled (Section 5's compilation step) into bytecode or another intermediate representation, and
then a runtime executes that intermediate representation — potentially using an interpreter,
potentially using JIT compilation (translating parts of the program into native machine code
*during* execution, Section 1), or potentially using some combination of both at different times.

**Make this explicit and unambiguous:** real implementations vary considerably in exactly how they
combine these pieces. This lesson does not claim there is one single "hybrid" pipeline every
hybrid system follows — Section 8's comparison table and Section 9's real-world examples show
several genuinely different real combinations, each labeled by which real language/implementation
uses it.

---

## 6. How It Works Internally

This section walks through four general conceptual shapes, each one a simplified model — real
systems can and do vary in their exact details.

### AOT-style compilation

("AOT" = **Ahead-Of-Time** — compiled entirely before the program runs, as opposed to JIT.)

```text
Source code
    ↓
Compiler
    ↓
Executable / native machine code
    ↓
Operating system loads program
    ↓
CPU executes machine instructions
```

Source code is translated by a compiler, entirely before execution, directly into an
executable containing native machine code. When the program is later run, the operating system
loads that executable, and the CPU executes its machine instructions directly (Concept 7). **This
lesson does not teach OS loader internals** — exactly how the operating system "loads" a program
is a topic for Module 0.2 and beyond.

### Interpreted-style execution

```text
Source/program representation
    ↓
Runtime / interpreter
    ↓
execution
    ↓
CPU performs underlying machine instructions
```

A program representation is carried out by a runtime/interpreter as the program runs. **Even
here, the CPU is still ultimately involved** — the interpreter itself is software, which (like any
software) is, underneath, executing as machine instructions on the CPU; the interpreter's job is
to carry out the *target* program's behavior using its own machine-code execution as the mechanism
for doing so. This directly corrects Misconception 9 (Section 11): interpretation does not mean
the CPU is bypassed — it means an additional layer of software (the interpreter) is directing the
CPU's work, rather than the target program's own dedicated native machine code doing so directly.

### Bytecode + Virtual Machine

```text
Source code
    ↓
compiler
    ↓
bytecode
    ↓
virtual machine/runtime
    ↓
execution
```

Here, a compiler *is* involved (correcting Misconception 2 in advance) — but rather than producing
native machine code directly, it produces bytecode (Section 1) — an intermediate representation
meant for a virtual machine (Section 1's specific meaning) to execute, rather than for the
physical CPU to execute directly.

### JIT

```text
Program Representation
        ↓
Runtime
        ↓
JIT
        ↓
Native Machine Code
        ↓
CPU
```

Just-In-Time compilation means compiling code **during program execution** rather than entirely
before execution (Section 1). A runtime encounters a program representation (which might itself be
bytecode, per the previous model) and, rather than only interpreting it, compiles some or all of
it into native machine code *while the program is running*, which the CPU then executes directly.
**This lesson does not teach JIT optimization strategies or JIT internals** — those are
substantially advanced topics well beyond this foundational lesson.

**A required, final clarification for this entire section:** these four models are not mutually
exclusive categories that every real system fits into exactly one of — Section 8 and Section 9
show that real, common systems frequently combine elements from more than one of these models at
once (for example, bytecode + virtual machine + JIT, all together, as one real system).

---

## 7. From Python to CPU — Foundational Example

Take a simple example:

```python
x = 10 + 20
```

**Python source code is not itself CPU machine code** — this restates Concept 7's central caution
(Concept 7, Section 10, Example 3, and Misconception 3), now with the vocabulary to explain *why*
in more depth than Concept 7 could at the time.

**A conceptual path, connecting this lesson's models to that one line of Python:**

```text
Python source
      ↓
Python implementation
      ↓
bytecode / runtime representation
      ↓
runtime execution
      ↓
lower-level machine instructions
      ↓
CPU
```

Walking through this: the Python source text `x = 10 + 20` is processed by a Python
**implementation** (Section 8 explains why "implementation" is the careful, correct word here,
rather than just "Python"). That implementation commonly involves producing some kind of bytecode
or other runtime representation — matching Section 6's "Bytecode + Virtual Machine" model in
general shape. A runtime then executes that representation, which — as Section 6's "Interpreted-
style execution" model established — ultimately still involves the CPU carrying out real machine
instructions, at the bottom of this whole chain.

**Two required, explicit cautions:**

> Do not claim that every Python implementation follows exactly this path.

There is more than one real Python implementation in existence (Section 8's comparison table
touches on this briefly), and this lesson does not claim to describe every one of them precisely.

> This is a simplified model of a common implementation approach.

This conceptual path is offered as a reasonable, common general shape — **not a precise, verified
technical description of any one specific Python implementation's internals.** This lesson does
**not** teach CPython internals (the internal workings of the specific, most common Python
implementation) — that is explicitly out of scope, named here only so you know the term exists and
that deeper detail belongs to later, more advanced material.

---

## 8. Compiled, Interpreted, and Hybrid Approaches

| Approach | Basic idea | When translation occurs | Typical output/representation | Runtime role | Example | Important caveat |
|---|---|---|---|---|---|---|
| Ahead-of-time compilation | Translate the whole program before it ever runs | Entirely before execution | Native machine code (executable) | Minimal — mostly just the OS loading and the CPU executing | C | The resulting executable is tied to a specific CPU architecture (Concept 7) |
| Bytecode + runtime | Compile to an intermediate representation, then run that representation using a runtime | Compilation happens before execution; the runtime then executes the result | Bytecode | Substantial — the runtime carries out the bytecode's behavior | A Python implementation | Different Python implementations exist; this describes one common general approach, not a universal guarantee |
| Bytecode + JIT | Compile to bytecode, then compile parts of it to native code *during* execution | Compilation to bytecode happens before execution; JIT compilation happens during execution | Bytecode, then native machine code (produced at runtime) | Substantial — the runtime manages both bytecode execution and JIT compilation | Java/JVM | JIT behavior and exactly when/what gets JIT-compiled is implementation-specific and not covered here |

**The single most important statement this table exists to support:**

> The implementation determines how a language is executed.

**Do not label languages themselves as permanently "compiled" or "interpreted."** This is a
required, explicit correction to a very common oversimplification (directly named in this
lesson's Primary Learning Objective): **compilation and interpretation are implementation
strategies, and the same language can have multiple implementations**, potentially using entirely
different strategies from each other.

**Working through the examples in the table, carefully and precisely:**

- **C** commonly uses ahead-of-time compilation — this is a statement about how C is *typically*
  implemented in common, widely-used systems, not an inherent, unchangeable property of "the C
  language" as an abstract concept.
- **A Python implementation** can involve compilation to bytecode followed by execution by a
  runtime/virtual machine — phrased this way deliberately, because (as Section 7 already
  cautioned) this describes a common approach, not a guaranteed universal fact about every
  possible way Python could be implemented.
- **Java** commonly uses compilation to bytecode followed by JVM execution and potentially JIT
  compilation — again, a statement about typical, common real implementations, not an unchangeable
  property of "the Java language" itself.

**Clearly distinguishing the language from its implementation, one more time, explicitly:** "C,"
"Python," and "Java" are language *specifications* — definitions of syntax and meaning. "GCC," "a
specific Python implementation," and "the JVM" are *implementations* — actual software that
carries out programs written in those languages, using one of the strategies from Section 6. A
language specification does not, by itself, mandate compilation, interpretation, or any hybrid
approach — that choice belongs to whoever builds a specific implementation of that language.

---

## 9. Real-World Examples

### Example 1 — C

```text
C source
   ↓
compiler
   ↓
native executable
   ↓
CPU executes machine code
```

This matches Section 6's AOT-style compilation model directly, and Section 8's table entry for C.
**Compiler details are kept out of this example entirely** — this lesson does not teach how a
compiler internally performs this translation, only that it does, producing a native executable
whose machine code the CPU can then execute directly (Concept 7).

### Example 2 — Python

```text
Python source
   ↓
Python implementation
   ↓
runtime representation
   ↓
execution
```

Python is commonly described, in casual conversation, simply as "an interpreted language." **This
lesson requires you to understand that this common description hides important implementation
detail** — as Section 7 and Section 8 both established, a common Python implementation approach
involves a compilation step (producing bytecode or a similar runtime representation) *before* a
runtime/interpreter executes that representation. Calling Python "just interpreted," without
qualification, obscures this — it is not technically inaccurate as a rough, everyday label, but it
is an incomplete description of what commonly actually happens. **This lesson does not teach
CPython internals** — the precise mechanics of any specific Python implementation remain out of
scope.

### Example 3 — Java

```text
Java source
   ↓
compiler
   ↓
bytecode
   ↓
JVM
   ↓
possible JIT compilation
   ↓
native machine code
   ↓
CPU
```

This matches Section 6's "Bytecode + Virtual Machine" model, extended with the JIT model layered
on top, exactly as Section 8's table describes. Java source is compiled (a genuine compilation
step) to bytecode; a runtime (the JVM — Java Virtual Machine, matching Section 1's specific
"virtual machine" definition) executes that bytecode, and — depending on the specific JVM
implementation and circumstances — some of that bytecode may be JIT-compiled into native machine
code during execution, which the CPU then executes directly. **This lesson keeps this entirely
conceptual** — no JVM internals, no JIT internals, are taught here.

### Example 4 — AI Engineering

```python
output = model(input)
```

```text
Python source
      ↓
runtime/framework
      ↓
lower-level operations
      ↓
CPU/GPU execution
```

This line of Python expresses a clear intent — "run this model on this input and give me the
output" — but, exactly as Concept 7 and this lesson's Section 7 established for a much simpler
example, this Python text is **not** itself what's directly executed at the hardware level.
Between this line and actual hardware execution sits a Python implementation (Section 7), likely
an AI framework (not named or taught here), and eventually either CPU or GPU execution (GPU is a
later concept file — not taught here at all).

**An explicit, required caution:**

> This is a conceptual stack, not a single universal implementation pipeline.

Different AI frameworks, different Python implementations, and different hardware setups can
combine these layers differently — exactly the same lesson Section 8's comparison table already
taught, now applied to this more advanced, AI-specific example. **This lesson does not teach GPU
internals** — GPU execution is named here only as the eventual destination this conceptual stack
can lead to, not something explained in this lesson.

---

## 10. Practical Linux/WSL2 Work

As with previous concepts, this section is safe, read-only where possible, requires no `sudo`,
and does not modify system configuration or any existing files. All work happens in a temporary
directory. Reminder of your environment:

```text
Windows
   ↓
WSL2
   ↓
Ubuntu
```

**First, check what's actually available — do not assume every tool is installed:**

```bash
uname -m
which gcc
which python3
which javac
which java
which objdump
which file
```

If a tool prints nothing from `which`, it isn't installed — use only the tools that are actually
available on your system; skip any practical step below whose required tool is missing, rather
than trying to install anything.

**Set up a temporary working directory, used for all of the following:**

```bash
mkdir -p /tmp/compilation-lesson
cd /tmp/compilation-lesson
```

### Practical A — Compilation observation (requires `gcc`)

Create a tiny C program:

```bash
cat > program.c << 'EOF'
#include <stdio.h>

int main(void) {
    int x = 10;
    int y = 20;
    printf("%d\n", x + y);
    return 0;
}
EOF
```

Compile it:

```bash
gcc program.c -o program
```

Observe what kind of file was produced:

```bash
file program
```

*What this shows:* A description confirming this is an executable file, targeting a specific CPU
architecture (matching Concept 6 and Concept 7's practical sections) — the direct, concrete
result of Section 6's AOT-compilation model.

If `objdump` is available, inspect the disassembly:

```bash
objdump -d program | head -40
```

*What this shows:* Disassembly (Concept 7, Section 11) of this executable's machine code — a
human-readable rendering of the actual instructions the CPU will execute when this program runs,
including instructions corresponding conceptually to the addition your C source code specified.
**This lesson does not walk through the complete assembly output line by line** — the point of
this observation is simply to *see*, concretely, that your C source became something entirely
different (machine code) before it became runnable, exactly matching Section 9, Example 1's
diagram.

**Connecting back to Concept 7 explicitly:** the bytes `objdump -d` reveals here are the same kind
of real, architecture-specific machine code Concept 7 introduced — this practical section is
compilation's concrete result made visible using the exact same tools Concept 7 already taught you
to use.

### Practical B — Python observation

Check your Python implementation's version:

```bash
python3 --version
```

*What this shows:* Which specific Python implementation and version is installed. **If the output
identifies this as "Python" without further qualification, it is reasonable to note that the most
common Python implementation is called CPython** — this lesson mentions this only as a factual
label, without teaching anything about CPython's internals (explicitly out of scope, per Section
7's caution).

Create and run a tiny Python example:

```bash
cat > example.py << 'EOF'
x = 10
y = 20
print(x + y)
EOF
python3 example.py
```

*What this demonstrates:* Running this file involves your Python implementation, as a runtime
(Section 1), carrying out this program's behavior — matching Section 7's conceptual path. **This
lesson does not attempt to show you Python's internal bytecode or runtime representation
directly** — doing so accurately would require teaching CPython internals, which is out of scope.
The observation here is deliberately limited to: source code exists, you ran it through a
specific, identifiable Python implementation, and it produced a result — exactly the beginning and
end of Section 7's conceptual path, with the middle steps (bytecode, runtime execution) understood
conceptually rather than directly observed.

**Do not make unsupported claims about the exact implementation** beyond what `python3 --version`
actually tells you — if your environment's Python is explicitly identified as CPython, that can be
stated as a fact about your environment specifically, not generalized into a claim about "how
Python works" universally, since other Python implementations exist and were not taught here.

### Practical C — Compare representations

Using the files from Practical A and Practical B, explicitly compare what each of these commands
reveals:

```bash
file program
objdump -d program | head -10
cat program.c
cat example.py
```

Work through this explicit distinction, connecting every term back to Section 1's definitions:

```text
source code      → program.c and example.py — human-readable text you wrote
executable       → program — the compiled output of program.c, containing machine code
machine-code bytes → the raw bytes inside `program`, corresponding to real CPU instructions
disassembly      → the human-readable output of `objdump -d program`
runtime execution → what happens when you actually run `python3 example.py`, or run `./program`
```

Note that `program.c` never becomes an "executable" on its own — only after `gcc` compiles it. By
contrast, `example.py` is run directly by `python3` — there is no separate, standalone executable
file produced as a visible end product in this simple observation, even though (per Section 7's
conceptual path) real translation and execution work still happens internally.

**Clean up when finished:**

```bash
cd ~
rm -rf /tmp/compilation-lesson
```

**A final, required caution for this entire section:** none of these observations expose the
live, internal workings of a compiler, an interpreter, or a runtime while they operate — you are
observing *inputs* (source code) and *outputs* (executables, disassembly, printed results), not
the translation or execution process itself happening in real time. This mirrors the exact caution
Concept 6 and Concept 7 both gave about their own practical sections.

---

## 11. Common Mistakes

```text
Misconception 1  → "Compiled languages become machine code and interpreted languages never do."
Correct idea     → This is an oversimplification this lesson's Primary Learning Objective
                    explicitly requires correcting. Compilation does not always produce native
                    machine code (it may produce bytecode instead, Section 5) — and
                    interpretation does not mean "never compiled" (Java compiles to bytecode
                    before its runtime interprets/JIT-compiles it, Section 9 Example 3).
                    Compiled/interpreted describes strategies, which can combine, not two
                    cleanly opposite categories.
Why it happens   → "Compiled" and "interpreted" are commonly taught as a simple binary choice
                    in casual conversation, which hides the real variety of hybrid approaches
                    (Section 6, Section 8) that most real, modern systems actually use.
```

```text
Misconception 2  → "Python is not compiled."
Correct idea     → Common Python implementations do perform a compilation step — translating
                    source code into bytecode (Section 7, Section 8) — before a runtime executes
                    that bytecode. "Python is not compiled" is an oversimplified, incomplete
                    version of "Python source is not compiled all the way down to a standalone
                    native executable the way C typically is," which is a different, more
                    precise claim.
Why it happens   → Because Python doesn't typically produce a standalone `.exe`-style native
                    executable the way C does (Practical A vs. Practical B in Section 10), it's
                    easy to conclude "no compilation happens at all," rather than recognizing
                    that compilation to an intermediate representation (bytecode) is still
                    genuinely compilation.
```

```text
Misconception 3  → "An interpreter reads source code one character at a time."
Correct idea     → Real interpreters generally operate on some structured representation of a
                    program, not raw, unprocessed source text read character by character
                    (Section 4's required correction). The exact structuring process is not
                    taught in this lesson, but the naive "character by character" mental model
                    is explicitly incorrect.
Why it happens   → "Interpretation" sounds, informally, like it should mean reading something
                    live, moment to moment — which can suggest a naive, literal,
                    character-by-character process, rather than the more structured reality.
```

```text
Misconception 4  → "Bytecode is machine code."
Correct idea     → Bytecode is instructions for a virtual machine/runtime; machine code is
                    instructions encoded for a CPU architecture (this lesson's mandatory
                    distinction, Section 5, Section 6). They are different representations,
                    meant for different execution mechanisms — a CPU cannot directly execute
                    bytecode without some runtime translating or interpreting it first.
Why it happens   → Both bytecode and machine code are binary-encoded instruction-like
                    representations (echoing Concept 4/5/7's general point that many things
                    reduce to bit patterns), which makes it easy to conflate them without
                    remembering that *what* they're instructions *for* is fundamentally
                    different.
```

```text
Misconception 5  → "Java is purely interpreted."
Correct idea     → As Section 9, Example 3 shows, Java source is compiled to bytecode first
                    (a genuine compilation step), and the JVM may further use JIT compilation
                    to produce native machine code during execution — "purely interpreted"
                    omits both the initial compilation step and the possible JIT compilation
                    step.
Why it happens   → Java's bytecode-plus-JVM execution is sometimes loosely summarized as
                    "interpreted" because the JVM is, in a broad sense, a runtime that executes
                    a program representation (Section 1) — but this loose summary skips over
                    the compilation and possible JIT steps that are also genuinely part of the
                    picture.
```

```text
Misconception 6  → "Compilation happens only once."
Correct idea     → While AOT compilation (Section 6) does happen once, entirely before
                    execution, JIT compilation (Section 6) happens during execution, potentially
                    multiple times, for different parts of a running program, as needed. Modern
                    systems commonly include this kind of runtime/JIT compilation, not only a
                    single, one-time, ahead-of-time compilation step.
Why it happens   → AOT compilation (as in the familiar C example, Section 9 Example 1) is often
                    the first and most intuitive model people learn, which can create the
                    impression that "compilation" always means a single, one-time event.
```

```text
Misconception 7  → "A compiler directly converts every source-code line into one CPU
                    instruction."
Correct idea     → Exactly as Concept 7 established for the relationship between a single
                    Python statement and CPU instructions, a single line of source code
                    typically corresponds to multiple lower-level operations/instructions, not
                    exactly one. This holds true whether the target of compilation is native
                    machine code or bytecode.
Why it happens   → A simple line of source code and a simple CPU instruction can both look
                    deceptively similar ("add two things"), making a direct, one-to-one mapping
                    feel intuitive, even though real translation typically produces more
                    operations than that (this is the same misconception Concept 7 already
                    corrected, restated here in the context of compilation specifically).
```

```text
Misconception 8  → "An executable file is just source code."
Correct idea     → An executable file (Section 1) is the *output* of a compilation process —
                    typically containing native machine code (Section 6's AOT model) — a
                    fundamentally different representation from the human-readable source code
                    it was produced from. Section 10, Practical C explicitly distinguishes
                    these using real files (`program.c` vs. `program`).
Why it happens   → Because an executable is "made from" source code and conceptually
                    represents "the same program," it's easy to blur the two together, rather
                    than recognizing they are entirely different representations — one
                    human-readable text, the other architecture-specific machine code.
```

```text
Misconception 9  → "If a program is interpreted, the CPU is not involved."
Correct idea     → As Section 6's "Interpreted-style execution" model explicitly established,
                    the CPU is always ultimately involved on a CPU-based system — the
                    interpreter itself is software that runs as machine instructions on the
                    CPU, and it uses that execution to carry out the target program's behavior.
                    Interpretation adds a layer of software directing the CPU's work; it does
                    not remove the CPU from the picture.
Why it happens   → "Interpreted" is sometimes informally contrasted with "compiled to run
                    directly on the CPU," which can create the false impression that
                    interpreted programs somehow bypass the CPU entirely, rather than running
                    on it via an additional software layer.
```

```text
Misconception 10 → "Compilation and interpretation are mutually exclusive."
Correct idea     → As Section 6 (hybrid execution), Section 8 (comparison table), and Section 9
                    (Java example) all demonstrate, many real, common systems combine both —
                    compiling source to bytecode, then interpreting and/or JIT-compiling that
                    bytecode at runtime. They are not an either/or choice for most modern,
                    real-world language implementations.
Why it happens   → Presenting compilation and interpretation as a simple two-option choice
                    (Misconception 1) naturally extends into assuming they must be mutually
                    exclusive, rather than recognizing they are complementary strategies that
                    frequently work together within a single implementation.
```

---

## 12. Debugging/Troubleshooting

**Scenario 1 — a learner says: "Python is interpreted, therefore Python cannot be compiled."**

This requires correction, per Misconception 2. Common Python implementations do involve a genuine
compilation step (producing bytecode), which then gets executed by a runtime. "Python is
interpreted" (as a loose, everyday label) and "Python source is compiled to bytecode" are not
contradictory statements — they describe different, compatible parts of the same overall process
(Section 7's conceptual path).

**Scenario 2 — a learner says: "Java bytecode is CPU machine code."**

This requires correction, per Misconception 4 and this lesson's mandatory "Bytecode vs Machine
Code" distinction. Java bytecode is instructions for the JVM (a virtual machine, Section 1) — the
physical CPU cannot execute Java bytecode directly; it requires the JVM (potentially using JIT
compilation, Section 6) to either interpret it or translate relevant parts into actual native
machine code first.

**Scenario 3 — a learner says: "If source code is compiled, the CPU executes the source code
directly."**

This requires correction. Compilation *transforms* source code into a different representation
(Section 5) — the CPU never executes source code itself, in any case, compiled or not (this
directly echoes Concept 7's foundational point). What the CPU executes is machine code — the
*output* of a compilation process that targeted native machine code specifically (Section 6's AOT
model), not the original source text.

**Scenario 4 — a learner runs `objdump -d program` and says: "This is the C source code."**

This requires correction, per Misconception 8 and Concept 7's parallel caution (Concept 7,
Misconception 9). `objdump -d` output is **disassembly** — a human-readable rendering of the
compiled program's machine-code instructions, produced by analyzing the compiled executable
(`program`), not a display of the original `program.c` source text. Running `cat program.c` and
`objdump -d program` (as in Section 10, Practical C) shows two genuinely different
representations of the same underlying program.

**Scenario 5 — a learner says: "Interpretation means no translation ever happens."**

This requires correction, per Section 4's required clarification. Even in interpreted-style
execution, real interpreters generally operate on some structured representation, not raw,
unprocessed source text (Misconception 3) — and, as Section 9's Python example shows, many common
interpreted-style systems do involve a genuine compilation step (to bytecode) before
interpretation/execution even begins. "No translation ever happens" is not an accurate description
of how interpretation commonly works in real systems.

**Scenario 6 — a learner says: "Every programming language has exactly one execution model."**

This requires correction, per Section 8's central point: "the implementation determines how a
language is executed." The same language (Section 8 uses Python as an example) can have multiple,
different implementations, potentially using different execution strategies from each other. A
language specification does not, by itself, mandate one single execution model.

**Scenario 7 — a learner says: "If two programs are written in the same language, their machine
code must be identical."**

This requires correction. Even setting aside that different implementations of the same language
can use entirely different execution strategies (Scenario 6), even two programs compiled with the
*same* compiler, for the *same* language, will generally produce **different** machine code if
their source code differs at all — machine code is a translation of a program's specific logic,
not a fixed, universal template. Additionally (connecting to Concept 7, Section 8), even
*identical* source code compiled for two *different* CPU architectures will produce different
machine code, because machine code is architecture-specific.

---

## 13. Exercises

Work through these in order, showing your reasoning for every explanation or comparison — not
just a final answer.

### Level 1 — Recognition

1. What is source code?
2. What is a compiler?
3. What is compilation?
4. What is an interpreter?
5. What is interpretation?
6. What is an executable?
7. What is bytecode?
8. What is a runtime?
9. What is a virtual machine, in the sense this lesson uses the term?
10. What is JIT compilation?
11. Is bytecode the same thing as machine code? Why or why not?
12. Is "compiled" or "interpreted" a fixed, permanent property of a programming language itself?

### Level 2 — Understanding

Answer each in your own words, in at least one or two full sentences.

13. Why do programming languages need an implementation mechanism at all?
14. What is compilation?
15. What is interpretation?
16. What is the difference between source code and machine code?
17. What is bytecode?
18. Why is bytecode not the same as machine code?
19. Why is "Python is interpreted" an incomplete description?
20. Why can a system use both interpretation and JIT compilation?
21. Why can the same language have different execution implementations?
22. Why does an interpreted program still ultimately involve hardware execution?

### Level 3 — Application

**Exercise A — Execution pipeline.** Given:

```python
x = 10 + 20
```

23. Construct the conceptual path from Python source through to CPU execution, using this
    lesson's vocabulary (referencing Section 7).

**Exercise B — Compare approaches.** Compare C, Python, and Java in terms of: source code,
translation, intermediate representation, runtime, and machine code.

24. Fill in this comparison for all three languages, without requiring implementation internals —
    referencing Section 8's table structure.

**Exercise C — Identify representation.** For each item below, identify whether it is source
code, bytecode, machine code, an executable, or disassembly, and explain your reasoning:

25. A `.py` file you wrote containing Python statements.
26. The output of running `objdump -d` on a compiled C program.
27. The file produced by running `gcc program.c -o program`.
28. The internal representation a Java compiler produces before the JVM runs it.

**Exercise D — Abstraction.** Given:

```python
result = model(input)
```

29. Explain why this is not directly executed by the CPU as Python source text, using this
    lesson's vocabulary and Section 9, Example 4.

### Level 4 — Debugging

For each statement, identify exactly what's wrong and explain the corrected understanding.

30. "Python cannot be compiled."
31. "Bytecode is machine code."
32. "Interpreted programs do not use the CPU."
33. "Java is purely interpreted."
34. "Compilation and interpretation cannot be combined."
35. "One source-code line becomes one CPU instruction."

### Level 5 — Integration

**Scenario A — Python AI application.** Trace:

```text
Python AI application
        ↓
Python implementation
        ↓
runtime representation
        ↓
runtime execution
        ↓
lower-level operations
        ↓
CPU/GPU
```

36. For each stage, identify what is known from Stage 0 so far, and what will be studied later
    (naming the future concept, where applicable).

**Scenario B — Deployment.** A developer moves a compiled application from one CPU architecture
to another.

37. Why might the existing executable not work on the new architecture?
38. Why can the source code sometimes be reused, even when the executable cannot?
39. What role does CPU architecture play here (connect explicitly to Concept 7)?

**Scenario C — Performance.** A developer says: "Compiled always means faster than interpreted."

40. Critique this statement, discussing implementation, workload, runtime, and JIT/startup
    trade-offs, without proposing a specific performance-optimization technique.

**Solutions are not provided here.** See
[`exercises/08-compilation-and-interpretation-answer-key.md`](./exercises/08-compilation-and-interpretation-answer-key.md)
— open it only after attempting every question above.

---

## 14. Practical Project Preparation

This section does **not** create a new project, and does **not** modify the existing `project/`
folder — it exists only to prepare you, through observation, for future implementation work.

**A recommended practice sequence**, using the same temporary-directory approach as Section 10:

1. Create a tiny C source file (as in Section 10, Practical A).
2. Compile it, **if GCC is available** — check with `which gcc` first, and skip this step
   entirely if it isn't.
3. Inspect the resulting executable with `file`.
4. Inspect its disassembly with `objdump -d`, **if `objdump` is available**.
5. Run a tiny Python program (as in Section 10, Practical B).
6. Compare the conceptual execution models you observed — AOT compilation (for the C example) vs.
   the bytecode/runtime model (for the Python example) — using Section 8's comparison table as a
   reference.
7. Document your observations in your own notes — outside this repository's `project/` structure
   — describing, in your own words, what you actually saw at each step, and connecting it back to
   this lesson's vocabulary (source code, compiler, executable, bytecode, runtime, machine code).

**Explicit boundaries for this section:**

- Do not add any source-code files to this repository — all practical work happens in a temporary
  directory (`/tmp/...`), exactly as in Section 10, and is cleaned up afterward.
- Do not modify anything inside `project/` — the three Module 0.1 projects (binary/decimal/hex
  converter, memory-size calculator, CPU-bound benchmark) remain exactly as previously prepared,
  untouched by this lesson.
- This is observation and learning only — not a new software project, and not an addition to any
  existing one.

---

## 15. Review Questions and Production Relevance

### Review Questions

Answers are intentionally not provided directly below these questions.

1. What is source code?
2. What is a compiler, and what is compilation?
3. What is an interpreter, and what is interpretation?
4. What is bytecode, and how is it different from machine code?
5. What is a runtime?
6. What is a virtual machine, in the sense this lesson uses the term?
7. What is JIT compilation?
8. What does "hybrid execution" mean?
9. Why is it inaccurate to describe a language itself as permanently "compiled" or
   "interpreted"?
10. Why doesn't one source-code line necessarily equal one CPU instruction?
11. Why is a compiled executable tied to a specific CPU architecture?
12. Why does an Applied AI Engineer need this foundational mental model?

### Production Relevance

You now understand that programming languages allow humans to express intent at a high level of
abstraction, and that compilation and interpretation — often combined, per Section 6 and Section
8 — are the mechanisms that eventually turn that expressed intent into real, executed work on real
hardware (Concept 2, Concept 3, Concept 7).

**How this foundation connects to your future AI Engineering work:**

```text
AI application
      ↓
Python
      ↓
runtime/framework
      ↓
compiled/interpreted/JIT components
      ↓
machine-level execution
      ↓
CPU/GPU
```

This foundation becomes directly useful when you later study:

- **Dependency management** — understanding why a specific Python implementation, or a specific
  compiled library, needs to be present connects directly to what this lesson taught about
  runtimes and compiled output.
- **Deployment** — packaging and shipping software depends on understanding what's actually being
  shipped (source code? a compiled executable? bytecode requiring a runtime?) — exactly the
  distinctions Section 10, Practical C required you to make concretely.
- **Profiling** — measuring where a program spends its time often requires understanding whether
  code is being interpreted, JIT-compiled, or running as pre-compiled native code.
- **Performance engineering** — Section 13, Scenario C previewed exactly the kind of nuanced
  reasoning ("compiled isn't automatically faster") this future topic will require.
- **Runtime behavior** — later systems-level topics will assume you already understand what a
  "runtime" is, in the specific sense this lesson defined it.
- **AI inference systems** — Section 3 and Section 9, Example 4 previewed how this vocabulary
  applies to running AI models — a topic developed properly much later in the roadmap.
- **CPU/GPU execution** — the very next concept files in this module (Cache, RAM, Storage, and
  eventually GPU) build the remaining hardware vocabulary this conceptual chain depends on.

**These are explicitly future topics — none of them are taught in this lesson.** They are named
here only to show where this lesson's foundation eventually connects, exactly as every prior
concept file in this module has done at its own conclusion.

---

_This file was written as the completed Concept 8 lesson for Module 0.1. It does not teach lexical
analysis, tokenization internals, parsing algorithms, AST implementation, semantic-analysis
internals, type-checking algorithms, intermediate-representation design, SSA, compiler
optimization passes, register allocation, instruction scheduling, assembler internals, linker
internals, loader internals, ABI internals, calling conventions, garbage-collector implementation,
interpreter implementation, bytecode-interpreter implementation, JIT-compiler internals,
deoptimization, speculative optimization, tracing-JIT internals, runtime-implementation internals,
virtual-machine architecture in depth, CPython internals, JVM internals, .NET CLR internals,
WebAssembly internals, operating-system process internals, virtual memory, CPU microarchitecture,
CPU pipelines, cache architecture, GPU execution, CUDA compilation, or AI inference optimization
in depth — those remain scaffolded, unwritten concept files (or entirely untouched, in the case of
later-stage material) until their own turn in the sequence. Cache specifically is the very next
concept, Concept 9, and is not taught here._
