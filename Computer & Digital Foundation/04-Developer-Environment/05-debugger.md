# Debugger

**Module:** Developer Environment
**Roadmap reference:** Stage 0 — Module 0.4 — Developer Environment
**Concept(s) covered:** debugger
**Prerequisites:** Module 0.1 (How Computers Work), Module 0.2 (Operating System Fundamentals),
Module 0.3 (Command Line), Module 0.4 Lesson 01 (VS Code and Terminal), Module 0.4 Lesson 02 (IDE
Concepts), Module 0.4 Lesson 03 (Extensions), Module 0.4 Lesson 04 (Formatters and Linters)
**Status:** Complete

All code shown in this lesson is small and self-contained. Where output is shown, it is explicitly
labeled **Expected output** or **Illustrative** — no command was actually executed while writing
this lesson, and no output is presented as a genuine execution record.

---

## 1. Introduction

### What a debugger is

A **debugger** is a tool that lets a developer pause a running program, look at exactly what state
it is in at that moment, and control its execution one step at a time. Instead of only seeing a
program's final output (or its final crash), a debugger lets you watch the program *while it runs*.

### What debugging means

**Debugging** is the broader engineering activity of figuring out why a program behaves incorrectly
and fixing the actual cause. A debugger (the tool) is one way of doing debugging (the activity) — the
two words are related but not identical, and this distinction is made precise in Section 2 and
Section 3.

### Why debugging is necessary

Even a program that runs without crashing can still be wrong. Module 0.1 and Module 0.2 already
established that a computer executes exactly the instructions it is given — it has no independent
sense of what the *programmer intended*. If those instructions contain a mistake, the program will
faithfully carry out the mistake, often without any obvious signal that something is wrong.

### Why programs can fail even when they successfully start

"Starting successfully" only means the operating system was able to create the process (Module 0.2)
and begin executing its instructions. It says nothing about whether those instructions do what the
developer intended. A program can start, run to completion, print a result, and exit cleanly — while
still producing the *wrong* result.

### Why incorrect behavior can be harder to diagnose than an obvious crash

A **crash** typically comes with an immediate, visible signal: the program stops, and often reports
where and why (Section 11 covers this in more depth). **Incorrect behavior** — a program that runs to
completion but produces a wrong answer — gives no such signal. Nothing announces the mistake; the
developer must notice that the output does not match what was expected, and then work backward to
find out why. This is a fundamentally harder problem, because there is no obvious starting point.

### Observing a problem vs. understanding its root cause

Noticing that "the output is wrong" is only an **observation**. It tells you *that* something is
wrong, not *why*. Debugging is the process of moving from an observation to an explanation precise
enough that a fix can be made with confidence — this progression is formalized in Section 2.

### A simple beginner example

Imagine a small program meant to calculate the total price of items in a shopping cart, but it
reports a total that is too low. The program did not crash. It produced *an* answer — just the wrong
one. Simply seeing "the total is wrong" does not tell you which item's price was miscounted, or why.
That gap — between "something is wrong" and "I know exactly what line of code causes it and why" — is
precisely what this entire lesson is about closing.

---

## 2. What Is Debugging?

Debugging is an **engineering process**, not random trial-and-error. This section defines its
vocabulary precisely, because later sections rely on these terms being used consistently.

### Core vocabulary

- **Bug** — a mistake in a program that causes it to behave differently from what was intended.
- **Failure** — an observable instance of the program not doing what it should (a crash, a wrong
  result, an unexpected state).
- **Incorrect behavior** — behavior that differs from the intended/expected behavior, whether or not
  it causes a visible crash.
- **Unexpected state** — a situation where a variable, object, or the program's overall condition
  holds a value the developer did not intend or anticipate at that point in execution.
- **Symptom** — the *visible* sign that something is wrong (for example, "the total is too low").
- **Cause** — something that contributed to the incorrect behavior.
- **Root cause** — the actual, underlying mistake that, if corrected, eliminates the symptom (and
  ideally the whole category of related problems it could cause).
- **Hypothesis** — a specific, testable guess about what the root cause might be.
- **Evidence** — information gathered from the running program (or its output) that supports or
  contradicts a hypothesis.
- **Verification** — confirming that a fix actually resolves the problem and does not merely make the
  symptom disappear by coincidence.

### Symptom vs. cause vs. root cause vs. fix

These four are easy to blur, and blurring them is one of the most common debugging mistakes (returned
to in Section 20):

- The **symptom** is what you *observe* ("the total is too low").
- A **cause** is *something* that contributes to the symptom — there can be more than one, and not
  every cause is the one that actually needs fixing.
- The **root cause** is the *specific, underlying* mistake that, once corrected, actually eliminates
  the symptom — for example, "one item's price was read using the wrong field name."
- The **fix** is the specific change made to correct the root cause.

A fix applied to a mere symptom (for example, manually adding a fixed amount to the total to make one
test case look right) does not address the root cause, and will typically fail again under slightly
different conditions.

### Why debugging is not random trial-and-error

Randomly changing code and rerunning the program to see if the symptom goes away is unreliable: it
does not build understanding, it can introduce new problems, and a symptom can disappear by accident
without the actual root cause being fixed (leaving it to resurface later, differently). Debugging, done
well, is instead a **disciplined process of forming and testing hypotheses using evidence** — the same
general reasoning pattern used throughout engineering.

### The core reasoning model

```
Observe -> Hypothesize -> Inspect -> Test -> Isolate -> Fix -> Verify
```

- **Observe** — notice and precisely describe the symptom (Section 1's example: "the total is too
  low," not just "something is wrong").
- **Hypothesize** — form a specific, testable guess about what might cause it.
- **Inspect** — gather evidence relevant to that hypothesis (this is where a debugger becomes useful
  — Section 3).
- **Test** — check whether the evidence supports or contradicts the hypothesis.
- **Isolate** — narrow down exactly where and why the incorrect behavior originates.
- **Fix** — make the smallest change that corrects the identified root cause.
- **Verify** — confirm the fix actually resolves the original symptom, and does not merely appear to.

This loop is expanded into a complete, numbered procedure in Section 17, and applied directly in
Section 18's examples, Section 30's structured exercise, and Section 31's mini-project.

---

## 3. What Is a Debugger?

### Definition

A **debugger** is a tool that observes and controls the execution of a running program, allowing a
developer to pause it, inspect its internal state, and resume or step through it in a controlled way.

### Key vocabulary

- **Debugger session** — a single, active instance of using a debugger to observe and control one
  running program, from the moment execution is launched (or attached to) under the debugger's
  control until that control ends.
- **Target program** — the specific program a debugger session is currently observing/controlling.
- **Execution control** — the debugger's ability to pause, resume, and step through the target
  program's execution, rather than letting it run uninterrupted from start to finish.
- **Program state** — the current values of a program's variables, its current location in the code,
  and (as covered in Section 9) which functions are currently active — everything a debugger can show
  you about "what the program currently looks like from the inside."
- **Observation** — the general act of examining program state without necessarily changing it.

### What a debugger allows that ordinary execution does not conveniently provide

Running a program normally only gives you its final output (or a crash). A debugger typically allows
an engineer to:

- **pause execution** — stop the program at a chosen point instead of letting it run straight through,
- **resume execution** — continue running from where it was paused,
- **execute one step at a time** — advance through the program's instructions in small, controlled
  increments (Section 7),
- **inspect variables** — see the current value of specific data at the paused moment (Section 8),
- **inspect the call stack** — see which functions led to the current point in execution (Section 9),
- **inspect the execution location** — see precisely which line of code is about to run,
- **inspect exceptions** — examine state at the moment something went wrong (Section 11),
- **evaluate expressions in supported contexts** — in many debuggers, type in a small expression and
  see its result using the program's current, paused state,
- **observe how state changes** — compare state before and after a specific operation (Section 8,
  Section 19).

**Accuracy note:** this lesson does not claim every debugger supports every one of these capabilities
identically. Different debuggers, for different languages and environments, vary in exactly what they
offer and how — the list above describes commonly available capabilities, not a universal, fixed
specification every debugger must implement.

---

## 4. Why Debuggers Exist

### The problems that motivate debuggers

- **Program crashes** — the program stops unexpectedly, and the developer needs to understand why.
- **Program produces wrong output** — the program runs to completion but the result is incorrect
  (Section 1's example).
- **Program enters an unexpected branch** — a conditional decision in the code takes a path the
  developer did not expect.
- **Variable contains an unexpected value** — data does not hold what the developer assumed it would.
- **Function receives incorrect input** — a function is called with arguments that are wrong,
  surprising the developer who expected different values.
- **Loop behaves incorrectly** — a repeated block of code runs too many times, too few times, or
  operates on the wrong data.
- **Exception occurs far away from the original mistake** — the *visible* failure (Section 11) is not
  necessarily located anywhere near the actual root cause; something earlier in execution set up the
  conditions for a later failure.
- **State changes unexpectedly** — a value that should have stayed the same, or changed in a specific
  way, does not.
- **Bug is difficult to reproduce by simply reading code** — some bugs only reveal themselves under
  specific runtime conditions that are hard to predict just by reading the source text.

### Why logs and print statements are useful but do not completely replace a debugger

**Logging** and **print statements** (fully compared in Section 14 and Section 15) show you
information the developer specifically thought, in advance, to record. A debugger, by contrast, lets
you inspect *any* state at the paused moment — including things the developer did not think to log
ahead of time. This is a genuine advantage for investigating an unfamiliar or unexpected problem, but
it is not a universal replacement — Section 14 and Section 15 explain specific situations where
logging or print statements are actually the better tool.

### Comparing available approaches

| Approach | What it shows | Best suited for |
|---|---|---|
| **Reading source code** | What the code is *supposed* to do | Forming initial hypotheses before running anything |
| **Print statements** | Specific values, at specific points the developer chose in advance | Quick, simple checks (Section 14) |
| **Logging** | A recorded history of chosen events over time | Long-running, production, or historical investigation (Section 15) |
| **Stack traces** | The path execution took to reach a failure (Section 10) | Understanding *how* execution reached a crash |
| **Debugger** | Live, interactive state at a paused moment, and step-by-step control | Detailed, local investigation of *why* state is wrong (Section 3) |

**Accuracy note:** this lesson does not claim debugger use is always superior. Each approach above has
situations where it is clearly the better tool — this comparison is expanded fully in Section 14 and
Section 15.

---

## 5. Internal Mental Model of Program Execution

This section builds directly on Module 0.1 and Module 0.2 rather than re-teaching them.

### The pieces, briefly reconnected

- **Source code** — the human-written text of a program (Module 0.1).
- **Running program** — the source code's instructions actually being carried out, as a **process**
  managed by the operating system (Module 0.2).
- **Instructions being executed** — the individual steps the running program is currently performing.
- **Current execution location** — the specific point in the source code corresponding to the
  instruction the process is about to execute.
- **Process** — the OS-managed running instance of the program (Module 0.2).
- **Thread, at a high level** — a single sequence of execution within a process; a process can have
  more than one, a topic returned to briefly in Section 22.
- **Memory/state** — the values currently held by the program's variables and data structures, stored
  in memory the OS has allocated to the process (Module 0.1, Module 0.2).
- **Function call** — the program transferring execution into a named block of code (a function),
  expected to eventually return.
- **Return** — the function call finishing and execution continuing from where it was called.
- **Exception** — an unexpected condition that interrupts a program's normal flow of execution
  (introduced fully in Section 11).

### How a debugger relates to the running program

A debugger does not run *instead of* the program — it runs *alongside* it, using facilities the
operating system provides (Module 0.2) to observe and, when instructed, pause the process's execution
at a chosen point, and to read its current memory/state without altering what the program's logic
does.

```text
Source Code
    |
Program Execution   (a running process, per Module 0.2)
    |
Current Execution Point
    |
Debugger Observes / Controls Execution
    |
Engineer Inspects State
```

This lesson deliberately does not go further into exactly how a debugger performs this observation
and control at the operating-system level — that level of detail belongs to more advanced,
later-stage material, not this developer-facing foundational lesson. The goal here is a
**developer-level mental model**: the debugger sits between the engineer and the running process,
letting the engineer see and control what would otherwise run invisibly and uninterrupted.

---

## 6. Breakpoints

### What a breakpoint is

A **breakpoint** is a marker, placed by the developer at a specific location in the source code, that
tells the debugger: "when execution reaches this point, pause here."

### Why breakpoints exist

Without a breakpoint, a debugger session would either run the entire program uninterrupted (no
different from running it normally) or require pausing execution manually at an arbitrary, unplanned
moment. A breakpoint lets the developer choose, in advance, exactly where in the program's execution
they want to stop and look around — directly supporting the "Inspect" step of Section 2's reasoning
model.

### What happens when execution reaches a breakpoint

Execution does not stop permanently — it **pauses**. The program remains loaded in memory, in
whatever state it had reached at that exact point, and the debugger gives control back to the
developer. From this paused state, the developer can inspect variables (Section 8), inspect the call
stack (Section 9), and then choose how to proceed (Section 7).

### Common breakpoint concepts

- **Line breakpoint** — the most basic kind: pause whenever execution reaches a specific line of code,
  regardless of any condition.
- **Conditional breakpoint** — a breakpoint that only pauses execution when a specified condition is
  true at that line (for example, only pausing when a loop's counter reaches a particular value) —
  useful when a line executes many times but only one specific occurrence is suspicious.
- **Exception breakpoint, at a conceptual level** — pausing execution automatically whenever an
  exception occurs (Section 11), rather than at a fixed line — useful when you know *something* fails
  but are not yet sure exactly where.
- **Function/method breakpoint, at a conceptual level** — pausing whenever a specific function is
  called, regardless of which line inside a file that corresponds to — useful when you care about
  every call to a particular function rather than one specific line.

**Accuracy note:** not every debugger supports every one of these breakpoint types, and the exact
terminology and behavior can vary between tools.

### Breakpoint placement strategy

**Do not place breakpoints randomly everywhere.** Section 20 explains in depth why this is a common
and costly mistake. Instead, follow a deliberate strategy:

1. **Identify suspicious behavior** — the specific symptom from Section 2's "Observe" step.
2. **Identify the relevant execution path** — which part of the code is actually involved in
   producing that behavior.
3. **Place a breakpoint at a meaningful location** — a point where inspecting state would meaningfully
   support or contradict your current hypothesis (Section 2).
4. **Run** — start (or resume) the program under the debugger.
5. **Inspect state** — examine variables and the call stack at the paused point (Section 8, Section
   9).
6. **Continue narrowing the problem** — based on what the evidence shows, refine the hypothesis and,
   if needed, move the breakpoint closer to the actual root cause.

---

## 7. Stepping Through Code

Once execution is paused at a breakpoint (Section 6), the developer needs a way to move forward in a
controlled way. This is called **stepping**.

### The core stepping actions

- **Continue / resume** — let the program run normally again, until it either finishes or reaches
  another breakpoint.
- **Step over** — execute the current line, without entering any function it calls, then pause again
  on the next line in the current function.
- **Step into** — if the current line calls a function, enter that function so its internal execution
  can be inspected line by line.
- **Step out** — finish executing the remainder of the current function and pause again immediately
  after returning to whichever line called it.

### A simple function-call example

```python
def double(value):
    result = value * 2
    return result

def main():
    number = 5
    doubled = double(number)
    print(doubled)

main()
```

Suppose a breakpoint is set on the line `doubled = double(number)` inside `main`.

- **Step Over** — executes that entire line (including the call to `double`) in one action, without
  pausing inside `double` itself, and pauses next on `print(doubled)`. Use this when you already trust
  `double` and only care about what happens in `main`.
- **Step Into** — pauses *inside* `double`, on the line `result = value * 2`, letting you inspect
  `value` and `result` directly as `double` executes. Use this when you suspect the problem is
  *inside* the function being called.
- **Step Out** — if you are currently paused inside `double` (for example, after stepping into it),
  Step Out finishes executing the rest of `double` and pauses again back in `main`, right after the
  call returned. Use this once you have seen what you needed inside the function and want to return to
  the caller without stepping through the rest of it line by line.

### Why stepping is useful for understanding control flow

Stepping lets a developer watch, in order, exactly which lines actually execute and in what sequence
— directly answering questions the source code alone cannot always answer with confidence, such as
"does this branch actually run in this case?" or "how many times does this loop actually execute
before things go wrong?" (Section 19 expands this into "when did the state become wrong?")

### A caution about complex or asynchronous systems

Stepping through large programs, or programs involving concurrent/asynchronous execution (briefly
introduced in Section 22), can become slow and confusing — there may simply be too many lines, or
execution may jump between different parts of the program in ways that are hard to follow one step at
a time. In these situations, developers should prefer **targeted inspection**: placing breakpoints
(especially conditional ones, Section 6) precisely where the evidence suggests the problem is, rather
than attempting to step through an entire large or complex execution from the very beginning.

---

## 8. Variables and Program State

### Variable inspection

**Variable inspection** is examining the current value held by a variable at the moment execution is
paused. This is one of the most fundamental things a debugger provides.

### What can be inspected

- **Local state** — the values of variables defined within the current function.
- **Function arguments** — the actual values a function was called with, which may differ from what
  the developer assumed at the call site.
- **Object state, at a conceptual level** — the current values held inside a more complex data
  structure, not just a single simple value.
- **State before and after an operation** — comparing a variable's value just before a specific line
  runs against its value just after, to see exactly what that line actually did to it.

### Why the value of a variable at runtime is evidence

Source code describes what the developer *intended* the program to do. The actual runtime value of a
variable tells you what the program *actually did*, up to that point. When these two disagree, the
runtime value is the more reliable signal — it reflects reality, not assumption. This directly
supports the "Inspect" and "Test" steps from Section 2's reasoning model: a hypothesis about what a
variable *should* contain can be directly tested against what it *actually* contains.

### Questions a debugger helps answer

- **What value did this variable actually contain?** — directly inspecting it at the paused moment.
- **What arguments reached this function?** — inspecting the function's parameters right after it was
  entered (using Step Into, Section 7).
- **Which branch executed?** — observed directly by watching which lines actually run during stepping
  (Section 7).
- **Did this value change before the failure?** — comparing state at two different points in execution
  (Section 19).
- **Which object state was present at the time?** — inspecting a data structure's current contents at
  the paused moment.

### Distinguishing source-code assumptions from runtime evidence

A very common root cause of confusion in debugging is a developer's *assumption* about what a variable
contains, formed by reading the code, turning out to be wrong. A debugger directly resolves this by
replacing assumption with **observed evidence** — you no longer have to guess what a variable held;
you can simply look.

---

## 9. Call Stack and Stack Frames

This section introduces these ideas carefully, from first principles, since they were not covered in
earlier modules.

### Function call, caller, callee

When one function (the **caller**) calls another function (the **callee**), execution transfers into
the callee, and — per Section 5 — is expected to eventually **return**, continuing execution back in
the caller.

### Call stack

The **call stack** is the ordered record, maintained automatically by the running program, of which
function called which — tracking the full chain of "who called whom" that led to the current point in
execution.

### Stack frame

A **stack frame** is the specific record, within the call stack, corresponding to one single active
function call — holding that call's local variables (Section 8) and remembering exactly where
execution should return to once that call finishes.

- **Current frame** — the stack frame for the function currently executing (or, when paused in a
  debugger, the function execution is currently paused inside).
- **Previous frame** — the stack frame for whichever function called the current one — the "next one
  up" in the call stack.

### A simple example

```text
main()
  |
process_data()
  |
validate_input()
  |
parse_value()
```

If execution is currently paused inside `parse_value()`, the call stack shows the full chain that led
there: `main()` called `process_data()`, which called `validate_input()`, which called
`parse_value()`. Each of these four has its own stack frame, each holding that specific call's own
local variables (Section 8) — for example, `validate_input()`'s stack frame is separate from, and does
not share variables with, `parse_value()`'s stack frame.

### How the call stack helps answer "How did execution get here?"

Simply looking at the current line of code tells you *where* execution is, but not *how it arrived
there*. The call stack answers exactly that: by reading it from the current frame upward, a developer
can see the entire chain of function calls responsible for reaching this specific point — directly
useful when the same function is called from several different places in a program, and you need to
know specifically *which* call path is currently active.

### Connection to stack traces

A **stack trace** (formalized fully in Section 10) is, conceptually, a *printed snapshot* of the call
stack at a specific moment — most commonly, the moment an exception occurred (Section 11). This lesson
does not go further into exception mechanics here; Section 10 and Section 11 build on this call-stack
foundation without turning into a separate exceptions course.

---

## 10. Stack Trace vs Debugger

### Stack trace

A **stack trace** is a static, printed record of the call stack (Section 9) at one specific moment —
most commonly, the point where a program failed. It is primarily **evidence about where execution
failed or propagated through calls.**

### Debugger

A **debugger** (Section 3) allows **interactive inspection and control of execution** — not just a
snapshot of the call stack, but the ability to pause, inspect variables (Section 8), step (Section 7),
and examine the call stack live, at any point you choose, not only at the moment of a failure.

### How they complement each other

```text
Stack trace:
"What path led to the failure?"

Debugger:
"What was the program state at that point?"
```

A stack trace is often the *first* piece of evidence a developer sees — it tells you the sequence of
function calls that led to a failure, immediately, without needing to set up a debugger session at
all. But it typically does not show you the *values* variables held along that path. A debugger can
then be used, often guided directly by what the stack trace revealed, to pause execution at (or near)
the relevant point and inspect exactly what state led to the problem.

**This distinction should not be oversimplified:** a stack trace is not simply "a weaker debugger,"
and a debugger is not simply "an interactive stack trace." A stack trace is a lightweight, always-
available static record particularly suited to understanding *call path*; a debugger is a heavier,
interactive tool particularly suited to understanding *state*. Professional debugging commonly uses
both together, in sequence, exactly as shown above.

---

## 11. Exceptions and Debugging

### Exception, at a foundational level

An **exception** is an unexpected condition that interrupts a program's normal flow of execution —
for example, attempting an operation that cannot be completed as written. When this happens, the
program does not continue executing its next instruction as normal; instead, control transfers to
whatever mechanism is responsible for dealing with the exception (or, if nothing handles it, the
program stops).

### Exception location and propagation

- **Exception location** — the specific line of code where the exception actually occurred.
- **Exception propagation** — an exception that is not immediately handled continues moving outward
  through the call stack (Section 9) — from the function where it occurred, to that function's caller,
  and so on — until something handles it or the program stops. This is exactly why, per Section 4, "an
  exception occurs far away from the original mistake" is a real and common pattern: the exception's
  *visible* location is not necessarily where the *actual mistake* was made.

### Debugger stopping on an exception

Many debuggers can be configured (Section 6's "exception breakpoint," at a conceptual level) to
automatically pause execution the moment an exception occurs, rather than requiring a manually placed
line breakpoint at the exact right location in advance. This is especially useful when a developer
knows *that* an exception happens but does not yet know *where*.

### Inspecting state around an exception

Once paused at (or near) the point of an exception, a developer can inspect the call stack (Section 9)
to see the full chain of calls that led there, and inspect variables (Section 8) to see what state
existed at that moment — directly supporting the investigation of *why* the exception occurred, not
just *that* it occurred.

### Stopping on an exception vs. stopping at a breakpoint vs. continuing

- **Stopping at a breakpoint** (Section 6) — pausing at a location the developer chose in advance,
  regardless of whether anything is currently wrong.
- **Stopping on an exception** — pausing automatically at the moment something unexpected happens,
  wherever that turns out to be.
- **Continuing after handling/inspection** — once the relevant state has been examined, execution can
  typically be resumed (Section 7's "continue"), letting the program proceed (and, depending on
  whether the exception is handled elsewhere in the code, either continue normally or ultimately stop).

**Scope note:** this lesson deliberately keeps exceptions at this foundational level. A full
treatment of exception types, handling strategies, and exception-safe code design belongs later, in
the Programming Foundations stage of this roadmap — not here.

---

## 12. Debugger and IDE

This section builds directly on `02-ide-concepts.md` and `03-extensions.md`.

### Common IDE-integrated debugger elements

- **Source editor** — the same editor used for writing code (Module 0.4 Lesson 01), also used to view
  the current execution location (Section 5) and place breakpoints (Section 6) directly next to the
  relevant lines.
- **Breakpoint markers** — visual indicators, shown directly in the source editor, marking which lines
  currently have a breakpoint set.
- **Debug controls** — buttons or commands for continue, step over, step into, step out (Section 7).
- **Variables panel** — a dedicated view listing current variable values (Section 8) at the paused
  point.
- **Call stack panel** — a dedicated view listing the current call stack (Section 9), typically letting
  the developer click between frames to inspect each one's local state.
- **Watch/evaluation area** — a place to type a specific variable name or small expression and see its
  current value, using the program's paused state (Section 3).
- **Exception information** — a display shown when execution pauses due to an exception (Section 11),
  typically including the exception's type/message and location.
- **Debug console** — an interactive area, often supporting typed expression evaluation, connected to
  the currently paused program.

### The relationship

```text
IDE / Editor
    +
Debugger
    +
Running Program
    =
Interactive Debugging Workflow
```

This mirrors the general pattern already established in `03-extensions.md`, Section 5 and Section 11:
the **IDE is the interface**; the **debugger is a separate capability**, often connected to the IDE
through an extension, that actually performs the execution control and inspection; the **running
program** is the actual target being observed. None of these three are the same thing, even though
they appear together as one integrated workflow.

**Scope note:** this lesson intentionally does not walk through a specific IDE's debugger UI in
exhaustive detail. The elements above describe the *concepts* an IDE-integrated debugger commonly
provides — the goal is understanding the underlying debugger abstraction, not memorizing any one
tool's exact interface.

---

## 13. Debugger and Terminal

This connects directly to Module 0.3 and to `01-vscode-and-terminal.md`.

### Debugging is not limited to an IDE

Just as formatters and linters can be invoked directly from a terminal (`04-formatters-and-linters.md`,
Section 12), debugging tooling can, depending on the language and tool, also be launched or driven
directly from the command line, without any IDE present at all.

### The general concepts

- **Launching a program from the terminal** — starting a program as a command, exactly as covered in
  Module 0.3 and `01-vscode-and-terminal.md`, Section 4.
- **Debugger tooling** — the underlying programs that actually perform execution control and state
  inspection (Section 3), which an IDE's debug controls (Section 12) typically invoke on the
  developer's behalf.
- **Command-line debugging, as a concept** — starting or attaching a debugger session using typed
  commands in a terminal, rather than clicking buttons in a graphical interface.
- **IDE-integrated debugging** — the same underlying capability, made more convenient through a
  graphical interface (Section 12).

### When terminal-based workflows are useful

- when working on a machine with no graphical IDE available (echoing `01-vscode-and-terminal.md`,
  Section 18 and `02-ide-concepts.md`, Section 24 — remote servers, containers, and similar
  environments),
- when a problem needs to be reproduced in a minimal, scriptable way,
- when automating a debugging-adjacent task rather than performing it interactively.

**Scope note:** this lesson does not teach a full command-line debugger course. The point here is the
same one made repeatedly in this module: the underlying debugging capability exists independently of
any one interface, and understanding it at that level makes a developer's skills portable across
environments.

---

## 14. Debugger vs Print Statements

### Print debugging

**Print debugging** means temporarily adding output statements (for example, printing a variable's
value) directly into the source code, to observe values as the program runs.

**Advantages:**

- simple — no additional tooling required,
- universally understandable — works in essentially any language or environment,
- easy to add — a single line inserted directly where needed,
- useful for quick observation — a fast way to confirm or rule out a simple hypothesis.

**Disadvantages:**

- modifies source code — temporary debugging statements must later be removed,
- can clutter output — especially if left in place or added in many locations,
- requires rerunning — each new question typically requires adding a new print statement and running
  the program again,
- may miss transient state — only shows what was explicitly printed, not everything that happened,
- difficult in complex control flow — many print statements across many conditional paths can become
  hard to read and correlate,
- can become noisy — excessive printing can obscure the specific information actually needed.

### Debugger

**Advantages:**

- pause execution — inspect the program without modifying its source code,
- inspect state interactively — look at *any* variable at the paused moment, not only ones specifically
  chosen in advance (Section 8),
- step through control flow — observe execution path directly, one line at a time (Section 7),
- inspect call stack — see exactly how execution reached the current point (Section 9),
- targeted investigation — narrow in precisely on a suspected location using breakpoints (Section 6).

**Disadvantages:**

- requires tooling familiarity — a developer must know how to set up and use a debugger session,
- interactive debugging can be slower — deliberately pausing and inspecting takes more active time
  than simply rerunning a program with print statements added,
- some environments make debugging harder — Section 21 and Section 24 cover several such cases,
- concurrency/distributed systems can complicate debugging — Section 22 and Section 24 cover this
  further.

### No universal winner

Neither approach is universally superior. Print debugging is often the fastest way to answer a very
simple, specific question; a debugger is often the better tool for a deeper, less-understood problem
requiring interactive exploration of state and control flow. Experienced engineers commonly use both,
choosing based on the specific situation.

---

## 15. Debugger vs Logging

### Interactive debugging vs. logs

**Interactive debugging** (this lesson's main subject) requires a live, running program that can be
paused and inspected in real time. **Logging** means recording chosen events and values, as the
program runs, into a persistent record (commonly a file or output stream) that can be reviewed later,
after the program has already finished running (or is still running elsewhere, out of reach of an
attached debugger).

### When each is better

| Debugger | Logging |
|---|---|
| Local development | Production systems |
| A reliably reproducible bug | Historical evidence, after the fact |
| Deep, interactive state inspection | Distributed services (Section 22, Section 24) |
| Control-flow investigation (Section 7) | Long-running processes |
| | Investigating incidents that already happened |

### Why production debugging often depends heavily on logs

A production system frequently cannot practically be paused mid-execution to attach an interactive
debugger — doing so could disrupt real users, and the specific problem being investigated may have
already happened and finished by the time anyone notices (Section 24 covers this in depth, including
the operational risks involved). Logs, by contrast, are recorded continuously and can be reviewed
*after* the fact, without needing to catch the problem happening live.

### A light connection to future observability topics

This lesson does not teach **observability** (a later-stage topic) in depth. For now, it is enough to
know that logging is one foundational building block of a broader set of practices — including
metrics and distributed tracing — used to understand the behavior of systems that cannot practically
be paused and inspected interactively. This connection is returned to, still only conceptually, in
Section 24 and Section 28.

---

## 16. Debugger vs Testing

**A debugger helps investigate behavior.** **A test helps verify expected behavior.** These serve
different, complementary purposes, and neither replaces the other.

A **test** (a later-stage topic, introduced here only to establish this distinction, consistent with
`04-formatters-and-linters.md`, Section 10) is code written specifically to run other code and check
whether its actual behavior matches an expected outcome. A test can tell you *that* something is
wrong — but, typically, not *why*.

### How they complement each other

```text
Test detects failure
        |
Debugger investigates root cause
        |
Code is fixed
        |
Test confirms the fix
```

A failing test is often an excellent, precise, reproducible starting point for a debugging session —
it already tells you exactly what condition is not being met. The debugger is then used to find *why*
the code produces the wrong result. Once fixed, rerunning the same test verifies the fix (Section 2's
"Verify" step) — and, ideally, continues to guard against the same mistake recurring later (Section
17's step 15, and Section 31's mini-project).

**Scope note:** this lesson does not teach how to write tests — that is a dedicated, later topic. The
point here is only the relationship between the two activities.

---

## 17. Debugging Workflow

A systematic, repeatable engineering process, directly expanding Section 2's core reasoning loop:

1. **Reproduce the problem.** Confirm it happens consistently before investigating further.
2. **Define the expected behavior.** Be precise about what the program *should* do.
3. **Observe the actual behavior.** Be precise about what it *actually* does (Section 1, Section 2).
4. **Identify the smallest useful reproduction.** Strip away anything not necessary to trigger the
   problem, to keep investigation focused.
5. **Form a hypothesis.** A specific, testable guess about the root cause (Section 2).
6. **Choose evidence to inspect.** Decide which variables, call paths, or state would actually confirm
   or refute the hypothesis (Section 8, Section 9).
7. **Set targeted breakpoints.** Following Section 6's placement strategy, not placed randomly.
8. **Run the program.** Under the debugger, with the breakpoints in place.
9. **Inspect variables and call stack.** Gather the evidence chosen in step 6 (Section 8, Section 9).
10. **Step through relevant execution.** Use Section 7's stepping actions to observe control flow where
    needed.
11. **Identify the root cause.** Distinguish it clearly from any mere symptom (Section 2).
12. **Make the smallest appropriate fix.** Address the root cause specifically, without unrelated
    changes.
13. **Re-run the reproduction.** Confirm the original problem no longer occurs.
14. **Verify expected behavior.** Confirm the program now does what it should — not merely that the
    original symptom disappeared (Section 2's "Verify").
15. **Add/strengthen a regression test when appropriate.** So the same mistake, if it reappears later,
    is caught automatically (Section 16).

### The convergence principle

Debugging should **converge toward a root cause** rather than becoming endless, unfocused inspection.
Each step in this workflow either gathers evidence that narrows down where the problem is, or applies
and verifies a fix. If an investigation is not narrowing down anything, that is itself a signal to
revisit the hypothesis (step 5) rather than continuing to inspect more state at random (directly
connected to the mistake described in Section 20: "guessing without evidence").

---

## 18. Debugging Example

All code and "expected" values below are illustrative teaching examples, not the output of an actual
execution.

### Example A — Wrong variable value

```python
def apply_discount(price, discount_percent):
    discount_amount = price * discount_percent
    return price - discount_amount

final_price = apply_discount(100, 10)
print(final_price)
```

The developer expected a 10% discount on a price of 100 to produce `90`.

```text
expected value -> 90
actual value   -> -900
```

**Illustrative debugging process:** a breakpoint is placed on the line `discount_amount = price *
discount_percent`, inside `apply_discount`. Stepping to that line and inspecting `discount_percent`
(Section 8) reveals it holds `10`, not `0.10` — the caller passed a whole-number percentage, but the
function's logic assumes a fraction (multiplying `price` directly by `discount_percent` rather than by
`discount_percent / 100`). The breakpoint made it possible to see the *actual* value reaching the
function (Section 8's "What arguments reached this function?"), rather than only assuming it from
reading the call site.

### Example B — Wrong branch

```python
def classify(score):
    if score > 90:
        return "excellent"
    elif score > 90:
        return "good"
    else:
        return "needs improvement"
```

A score of `95` is expected to return `"excellent"`, and does — but a score of `92` was expected to
return `"good"` and does not (it also returns `"excellent"`, correctly here, but a score of exactly
`90` unexpectedly falls straight to `"needs improvement"` instead of `"good"`, since the second
condition is mistakenly also `score > 90` instead of a lower threshold).

**Illustrative debugging process:** a breakpoint is placed on the `if score > 90:` line. Stepping
through with `score = 90` shows the first condition evaluates to `False`, and then — inspecting the
second condition before it runs — the developer notices it is *also* `score > 90`, an identical,
unreachable-in-a-useful-way condition. Inspecting the current values (`score` and each condition's
result, Section 8) and observing which branch actually executes (Section 7) directly reveals the
mistake: the second condition should have used a different threshold.

### Example C — Function receives wrong input

```text
caller -> function -> unexpected argument
```

```python
def process_order(order_id, quantity):
    total = quantity * 10
    return total

def main():
    order_id = "ORD-1"
    quantity = order_id  # mistake: assigned the wrong variable
    result = process_order(order_id, quantity)
    print(result)
```

**Illustrative debugging process:** stepping into `process_order` (Section 7) from the call in `main`
and inspecting its parameters (Section 8) shows `quantity` holds `"ORD-1"` — a text value — instead of
a number. Using the call stack (Section 9), the developer can move to `main`'s frame and see exactly
how `quantity` was assigned there, immediately revealing the copy-paste-style mistake of assigning
`order_id` to `quantity` instead of a numeric value.

### Example D — Exception

```python
def get_first_item(items):
    return items[0]

def main():
    results = []
    first = get_first_item(results)
    print(first)
```

Calling `get_first_item` with an empty list causes an exception when attempting to access an item at
position `0` that does not exist.

**Illustrative debugging process:** with an exception breakpoint enabled (Section 6, Section 11), the
debugger automatically pauses at the moment the exception occurs, inside `get_first_item`. Inspecting
`items` (Section 8) shows it is an empty list, and the call stack (Section 9) shows this function was
called from `main`, where `results` was never populated before being passed in — revealing that the
actual root cause is earlier than the exception's location: something upstream failed to add any items
to `results` before it was used (directly illustrating Section 4's and Section 11's point that an
exception's visible location is not necessarily where the mistake was made).

---

## 19. Debugging State Over Time

### Reframing the question

A common and often more productive question in debugging is not:

**"What is wrong now?"**

but:

**"When did the state become wrong?"**

### The state-transition model

```text
Correct State
    |
Transformation
    |
Transformation
    |
Incorrect State
```

A program's state typically does not become wrong all at once — it starts correct, and some specific
transformation (a line of code, a function call, a loop iteration) changes it into something
incorrect. Somewhere in that sequence of transformations, there is a specific transition where
"correct" became "incorrect." Finding *that specific transition* is often the most direct path to the
root cause.

### How breakpoints and stepping help locate the transition

Using Section 6's breakpoints and Section 7's stepping together, a developer can inspect state
(Section 8) at multiple points across a sequence of transformations — before the first transformation,
after it, after the next one, and so on — narrowing down which specific transformation is the one
where state actually went wrong, rather than only looking at the final, already-incorrect state and
guessing backward.

### State transition debugging, introduced

This general technique — deliberately inspecting state at multiple points across a sequence of
operations to locate exactly where it changes from correct to incorrect — is sometimes called **state
transition debugging**. It is not a separate tool; it is simply a deliberate *strategy* for using
breakpoints and stepping (Section 6, Section 7) in combination, guided by the reframed question above.

---

## 20. Common Debugging Mistakes

- **Guessing without evidence** — changing code based on a hunch rather than an inspected, tested
  hypothesis (Section 2).
- **Changing multiple things at once** — makes it impossible to know which change, if any, actually
  fixed the problem.
- **Placing breakpoints everywhere** — directly contradicts Section 6's placement strategy; produces
  overwhelming amounts of state to inspect with no clear focus.
- **Inspecting irrelevant variables** — spending time examining state that has no bearing on the
  current hypothesis.
- **Ignoring the call stack** — missing the "how did execution get here" evidence Section 9 provides,
  and therefore missing root causes located earlier in the call chain.
- **Assuming the error message is the root cause** — an error message (Section 11) often describes
  only the *symptom* or the point where a problem became visible, not necessarily its true origin
  (Section 4).
- **Assuming the first suspicious line is necessarily the root cause** — the first thing that looks
  wrong is not guaranteed to be the actual underlying mistake; it may itself be a downstream
  consequence of something earlier (Section 19).
- **Fixing symptoms instead of causes** — directly the failure mode Section 2 warns about: a change
  that hides the visible problem without addressing the actual mistake.
- **Failing to reproduce the bug** — attempting to fix something without first confirming, reliably,
  how to trigger it (Section 17, step 1).
- **Failing to verify the fix** — assuming a change worked without actually re-running the reproduction
  and checking (Section 17, step 13–14).
- **Forgetting regression testing** — leaving the fix unguarded against the same mistake quietly
  reappearing later (Section 16, Section 17 step 15).
- **Relying entirely on a debugger** — treating it as the only valid investigation tool, when Section
  14 and Section 15 both describe real situations where print statements or logging are more
  appropriate.
- **Debugging optimized/production systems as if they were simple local programs** — ignoring the real
  differences covered in Section 21, Section 24, and Section 26 between a small local program and a
  production or optimized deployment.

Each of these mistakes shares a common thread: they replace disciplined, evidence-based reasoning
(Section 2) with shortcuts that feel faster but tend to cost more time overall.

---

## 21. Debugging Failure Modes

These are problems specifically with the *debugging process itself*, not with the program being
debugged. Each follows: symptom, likely cause, investigation, corrective action.

### Breakpoint never hits

1. **Symptom:** execution runs past the breakpoint's location without pausing.
2. **Likely cause:** the line never actually executes under the conditions being tested; the debugger
   is not actually attached to the process being run; a conditional breakpoint's (Section 6) condition
   is never true.
3. **Investigation:** confirm the code path actually reaches that line under the current input; confirm
   which process the debugger session is attached to (see below).
4. **Corrective action:** adjust the breakpoint's location or condition, or confirm the correct program
   is actually being run under the debugger.

### Wrong source file

1. **Symptom:** the debugger pauses, but the source shown does not match what the developer expects.
2. **Likely cause:** more than one file or module with a similar name exists in the project; the
   debugger is showing a different, unrelated copy of similarly named code.
3. **Investigation:** confirm the exact file path shown by the debugger matches the file actually being
   edited.
4. **Corrective action:** resolve the naming ambiguity, or open the correct file directly from the
   debugger's own display.

### Wrong execution path

1. **Symptom:** the debugger pauses somewhere unexpected, not matching the developer's assumed
   control flow.
2. **Likely cause:** the actual runtime condition differs from what the developer assumed when reading
   the source code (Section 8's core point).
3. **Investigation:** inspect the relevant condition's actual values at the paused point.
4. **Corrective action:** update the mental model of the program's behavior to match the observed
   evidence, rather than the original assumption.

### Debugger attached to wrong process

1. **Symptom:** breakpoints never hit, or state shown does not match the program actually being tested.
2. **Likely cause:** more than one instance of a similar program is running, and the debugger session
   is connected to a different one (Module 0.2's process concept, applied here).
3. **Investigation:** confirm exactly which running process the debugger session is currently attached
   to.
4. **Corrective action:** stop unrelated running instances, or explicitly attach to the correct one.

### Code differs from running code

1. **Symptom:** stepping through the debugger does not match what the source file currently shows.
2. **Likely cause:** the running program was started from an older version of the code, before a recent
   edit; the file being viewed is not the one that was actually executed.
3. **Investigation:** confirm when the running program was last started relative to the most recent
   edit.
4. **Corrective action:** stop and restart the program under the debugger after saving the latest
   changes.

### Optimized code makes inspection confusing

1. **Symptom:** stepping or variable inspection behaves in a way that does not match the source code's
   apparent, straightforward structure.
2. **Likely cause:** some execution environments transform code before running it in ways that can
   make line-by-line correspondence with the original source less exact.
3. **Investigation:** confirm whether the environment being debugged applies such transformations, and
   whether a less-transformed mode is available for debugging.
4. **Corrective action:** where possible, debug using a mode intended for development/inspection rather
   than one optimized purely for performance.

### Environment mismatch

1. **Symptom:** a bug reproduces in one environment but the debugger session (run somewhere else) never
   shows the same behavior.
2. **Likely cause:** a difference in configuration, installed versions, or environment variables
   between where the bug was observed and where it is being debugged (directly echoing
   `02-ide-concepts.md`, Section 16, Scenario C).
3. **Investigation:** compare the relevant environment details between the two contexts.
4. **Corrective action:** debug in an environment that actually matches where the problem was observed.

### Dependency/version mismatch

1. **Symptom:** behavior differs from what documentation, past experience, or a teammate's report
   suggests it should be.
2. **Likely cause:** a different version of a tool or dependency is actually in use.
3. **Investigation:** confirm the exact version in use in the current debugging context.
4. **Corrective action:** align the version being debugged with the one relevant to the actual problem.

### Exception occurs outside the inspected path

1. **Symptom:** an exception breakpoint (Section 6) never triggers, even though the program is known to
   fail.
2. **Likely cause:** the exception occurs in a code path not covered by current breakpoint settings, or
   is being caught and handled silently somewhere before it becomes visible.
3. **Investigation:** broaden exception breakpoint settings, or search for exception-handling code that
   might be silently absorbing the failure.
4. **Corrective action:** adjust breakpoints or temporarily inspect the handling code directly.

### Multiple threads complicate state

1. **Symptom:** state appears to change unexpectedly between debugger steps, even without the developer
   apparently causing it.
2. **Likely cause:** another thread (Section 22) is modifying shared state concurrently.
3. **Investigation:** identify whether more than one thread is active and touching the same state.
4. **Corrective action:** narrow investigation specifically to the thread of interest, where the
   debugger's tooling supports this; treat concurrent modification as a distinct hypothesis.

### Asynchronous execution complicates stepping

1. **Symptom:** stepping (Section 7) does not proceed in the straightforward, linear order the source
   code's layout suggests.
2. **Likely cause:** the program's execution model allows work to be scheduled and resumed out of
   simple top-to-bottom order.
3. **Investigation:** confirm whether the code involves this kind of execution model before assuming
   stepping behavior is a debugger malfunction.
4. **Corrective action:** rely more on targeted breakpoints (Section 7's caution) than on continuous
   linear stepping in such code.

### Remote/distributed execution cannot be understood as a single local process

1. **Symptom:** a problem appears to involve behavior that a single local debugger session cannot fully
   explain.
2. **Likely cause:** the actual system involves more than one process, possibly on more than one
   machine, communicating with each other — something a single debugger session attached to one local
   process cannot show in full.
3. **Investigation:** determine whether the system under investigation is, in fact, a single program or
   several communicating ones.
4. **Corrective action:** recognize the limits of local, interactive debugging in this situation, and
   rely more heavily on logs (Section 15) and the production-debugging considerations in Section 24.

---

## 22. Debugging and Processes / Threads

This connects directly to Module 0.2.

- **Process** — an OS-managed running instance of a program (Module 0.2); a debugger session
  ultimately observes and controls one (or more, depending on the tool) specific process.
- **Thread** — a single sequence of execution within a process (Section 5); a process can contain more
  than one thread, each potentially executing different code at the same time.
- **Debugger target** — the specific process (Section 3) a debugger session is currently attached to
  and controlling.

### Why multiple threads complicate debugging

When more than one thread is active within the same process, more than one sequence of execution can
be modifying shared state at the same time. Pausing one thread at a breakpoint does not necessarily
pause the others (depending on the debugger and its configuration), meaning state can continue
changing "behind the scenes" even while one thread is paused for inspection — directly the scenario
described in Section 21's "Multiple threads complicate state."

### Why asynchronous execution can make linear stepping less intuitive

Some programs are structured so that pieces of work can be paused and resumed out of simple,
top-to-bottom order — allowing other work to proceed in the meantime. Stepping through such code
line-by-line (Section 7) does not always correspond to the intuitive, straightforward order the source
code's layout might suggest, directly echoing Section 21's corresponding failure mode.

### The essential awareness this section aims to establish

**"The program I see in the debugger may involve more than one execution path."** A beginner's early
debugging experience will typically involve simple, single-threaded, linear programs, where this
concern does not arise. As programs grow more complex — including many real-world backend, ML, and AI
systems referenced in Section 23 — this awareness becomes increasingly important, even though this
lesson does not teach advanced concurrency debugging techniques in depth.

---

## 23. Debugging and AI Engineering

This is a forward-looking preview only — none of the following systems are taught here.

### Python programs

Debugger skills apply directly to: incorrect data transformations, wrong function arguments (Example
C, Section 18), unexpected control flow (Example B, Section 18), and unexpected state (Section 8,
Section 19) — the same foundational skills this lesson teaches, applied to any Python program.

### Data pipelines

- malformed input reaching a processing stage,
- unexpected transformations changing data in ways not intended,
- missing records disappearing somewhere between stages,
- wrong assumptions about what a prior stage actually produced (directly connecting to Section 8's
  "distinguishing source-code assumptions from runtime evidence").

### ML systems

- preprocessing bugs — data transformed incorrectly before being used,
- tensor shape mistakes — data structured differently than a later step expects,
- incorrect configuration — settings that do not match what the code assumes,
- data-flow problems — state that should have propagated correctly between stages failing to do so
  (Section 19's state-transition model applies directly here).

### LLM applications

- wrong prompt construction — the actual text sent differs from what the developer intended (directly
  inspectable the same way as Example A in Section 18),
- incorrect context assembly — the wrong data ending up included or excluded,
- unexpected routing — the program taking an unintended branch (Example B, Section 18),
- malformed structured data — data not matching an expected shape before being used further,
- incorrect tool arguments — a function/tool called with the wrong values (Example C, Section 18),
- state-management bugs — data that should persist correctly between steps failing to do so.

### RAG systems

- incorrect ingestion — source data not processed as intended,
- wrong chunk data — a text segment not containing what was expected,
- metadata mistakes — descriptive information about data not matching the data itself,
- retrieval pipeline problems — the wrong information being found or returned,
- incorrect context passed downstream — data reaching a later stage in the wrong form.

### Agent systems

- incorrect state transitions — an agent's internal state changing incorrectly between steps (Section
  19),
- unexpected tool calls — a tool invoked with the wrong arguments or at the wrong time (Example C,
  Section 18),
- routing errors — the wrong branch of logic taken (Example B, Section 18),
- incorrect tool arguments,
- control-flow bugs,
- termination-condition problems — an agent's loop not stopping (or stopping) under the intended
  condition.

### A crucial distinction: software debugging vs. model/behavioral evaluation

**Software debugging** (this entire lesson) investigates whether a program's *execution* is doing what
its code actually specifies — tracing incorrect values, wrong branches, and broken state through the
mechanisms covered in this lesson.

**Model/behavioral evaluation** (a later-stage topic, not taught here) asks a fundamentally different
question: whether an AI model's *output* is semantically good, safe, useful, or aligned with what is
actually wanted.

**A debugger can help investigate software execution, but it cannot by itself determine whether an AI
model's output is semantically good, safe, useful, or aligned.** If an LLM-based system returns a
technically well-formed but unhelpful or incorrect answer, a debugger can confirm that the *code*
correctly assembled the prompt, called the model, and processed the response — it has no way to judge
whether the model's actual generated content was good. That judgment belongs to evaluation practices
covered later in this roadmap, entirely separate from the debugging skills taught here.

---

## 24. Debugging in Production

### Where interactive debugging is appropriate

Interactive debugging (this lesson's main subject) is well suited to:

- local development,
- development environments,
- controlled staging environments,

where a developer has full, safe control over the running program and no real users are affected by
pausing it.

### What production systems require instead

- **logs** (Section 15),
- **metrics** — a later-stage topic, mentioned here only as a forward reference,
- **traces** — a later-stage topic, mentioned here only as a forward reference,
- **error reports** — structured records of failures, generated automatically,
- **reproducible requests** — a way to recreate the exact conditions that caused a problem, often
  outside the live production system,
- **safe diagnostics** — investigation methods that do not risk disrupting real users or exposing
  sensitive data (Section 25),
- **controlled debugging** — debugging performed deliberately and safely, if at all, rather than ad
  hoc,
- **observability** — a later-stage topic (briefly connected in Section 15), mentioned here only as a
  forward reference.

### Why attaching an interactive debugger to a production AI service can introduce real risk

- **performance impact** — pausing a live process (Section 26) can slow or stall real requests being
  served at that moment,
- **security risk** — a debugger session, if accessible to the wrong party, provides deep access to a
  running system (Section 25),
- **privacy concerns** — a paused, inspectable process may hold real user data in memory at that moment
  (Section 25),
- **operational risk** — an accidental mistake made while interactively controlling a live production
  process (for example, resuming it in an unintended state) can cause real, user-facing harm,
- **request disruption** — pausing execution for inspection directly delays or breaks whatever request
  or job that process was handling at the time.

**Scope note:** this lesson does not teach the full Observability/LLMOps curriculum — those are
dedicated, later-stage topics. The goal here is only to establish this foundational principle:
**interactive debugging and production operation have different risk profiles, and the tools
appropriate for one are not automatically appropriate for the other.**

---

## 25. Security Considerations

Debugging access is powerful, and should be treated with the same seriousness as any other form of
privileged access to a running system.

### Risks

- **Inspecting secrets** — a paused program's memory may contain sensitive values.
- **Inspecting tokens** — authentication tokens can appear in variables just like any other data.
- **Inspecting credentials** — passwords or API keys used by the program may be directly visible
  during state inspection (Section 8).
- **Exposing sensitive input** — data a user submitted may be present in memory at the paused moment.
- **Exposing user data** — any personal or private data the program is currently processing is, by
  definition, inspectable while paused.
- **Debugger access becoming privileged access** — the ability to attach a debugger to a running
  process is, functionally, a form of deep access to that system and everything it currently holds in
  memory.
- **Remote debugging risks** — attaching a debugger to a process running on a different machine
  introduces additional exposure if that connection or access is not properly secured.
- **Leaving debugging enabled in production** — a debugging capability left accessible on a live system
  extends all of the above risks indefinitely, not just during an intentional investigation.
- **Accidental disclosure through screenshots/logs/debug sessions** — sensitive state inspected during
  debugging can be inadvertently captured or shared (for example, in a screenshot, a shared screen, or
  a saved debug log) well beyond the original debugging session.

### The core principle

**Debugging access must be treated as sensitive operational access.** It should be granted
deliberately, used carefully, and never left available by default on systems handling real data.

### For this lesson's exercises specifically

**Never use real credentials, API keys, production secrets, or personal data in exercises.** Every
exercise, example, and project in this lesson (Sections 18, 29, 30, 31) uses only small, disposable,
entirely fictional example programs and data.

---

## 26. Performance Considerations

- **Debugger overhead** — attaching a debugger and enabling breakpoints can, depending on the tool and
  environment, add some measurable cost to a program's execution compared to running it without any
  debugging tooling active.
- **Paused processes** — a process paused at a breakpoint (Section 6) is, by definition, not making
  progress on whatever work it was doing — directly relevant to Section 24's production concerns.
- **Stepping overhead** — interactively stepping through execution (Section 7) is inherently slower
  than letting a program run uninterrupted, since it deliberately introduces pauses.
- **Breakpoint overhead in some environments** — depending on the tool, having breakpoints active (even
  ones not currently triggering) can, in some environments, add some ongoing overhead to execution.
- **Timing-sensitive bugs** — some bugs depend specifically on the *precise timing* of events (for
  example, involving multiple threads, Section 22). Pausing execution to inspect such a bug can change
  that timing enough that the bug's behavior itself changes while being observed.
- **Heisenbug-like behavior, at a conceptual level** — a bug that seems to change or disappear when you
  attempt to observe or debug it, precisely because the act of debugging (pausing, stepping, adding
  print statements) altered the timing or conditions the bug depended on in the first place.

### Why debugging can sometimes change timing and behavior

Interactive debugging deliberately introduces pauses and interruptions into a program's normal
execution. For most bugs, this has no meaningful effect on the underlying mistake being investigated.
But for bugs that depend specifically on precise timing or concurrent execution (Section 22), the very
act of pausing to inspect can shift that timing enough to mask or alter the bug's observed behavior —
worth being aware of, without this lesson making any specific, unsupported claim about how often this
occurs or by how much.

---

## 27. Debugger Tool Examples

This section names tools only as **concrete examples**, consistent with how `04-formatters-and-linters.md`,
Section 16 introduced Ruff — not as a tutorial for any specific one.

- **VS Code debugger** — an IDE-integrated debugger (Section 12), commonly used alongside the editor
  and terminal already introduced in `01-vscode-and-terminal.md`.
- **Python debugging, generally** — the general capability, in the Python ecosystem, to pause and
  inspect a running Python program's state, applying every concept covered in this lesson.
- **`pdb`** — Python's built-in, terminal-based debugger (Section 13), one concrete example of a
  command-line debugging tool for Python.
- **IDE-integrated debuggers, generally** — debugging tooling built into or connected to a development
  environment (Section 12), for Python or other languages.

### Tools differ in interface and capabilities

Consistent with the accuracy requirements stated throughout this lesson (Section 3, Section 6): these
tools differ in their specific interfaces, exactly which breakpoint types and inspection features they
support, and how they are launched or attached. This lesson intentionally does **not** turn into a
detailed `pdb` course or a detailed VS Code debugger tutorial — **the objective is understanding the
debugger abstraction first**, so that whichever specific tool a learner later encounters, the
underlying concepts (breakpoints, stepping, state inspection, call stack) transfer directly.

---

## 28. Conceptual Distinctions

| Tool/concept | Purpose | When used | What information it provides | Controls execution? |
|---|---|---|---|---|
| **Debugger** (Section 3) | Interactive investigation of a running program | During active investigation of a specific problem | Live variable values, call stack, execution location | Yes — pause, resume, step |
| **Debugger session** (Section 3) | One specific active instance of using a debugger | For the duration of one investigation | Whatever is inspected during that session | Yes, for its duration |
| **Breakpoint** (Section 6) | A chosen pause point | Set in advance, before running under a debugger | Triggers a pause; state at that moment | Yes — causes execution to pause |
| **Stack trace** (Section 10) | A static record of the call path to a failure | Typically shown automatically when an unhandled exception occurs | Which functions called which, up to the failure point | No — a static snapshot |
| **Logging** (Section 15) | Recording chosen events over time | Continuously, especially in production | Whatever the developer specifically chose to record | No |
| **Print debugging** (Section 14) | Quick, ad hoc observation | Simple, well-understood questions | The specific value(s) printed | No |
| **Testing** (Section 16) | Verifying expected behavior | Before and after a fix, and continuously over time | Pass/fail against defined expectations | Runs the program, but does not interactively control it |
| **Profiler** (mentioned here only for this comparison; not taught in this lesson) | Measuring performance characteristics (for example, time spent in each part of a program) | Investigating performance, not correctness | Timing/resource-usage data | No, though it observes execution |
| **Monitoring** (a later-stage topic) | Continuous, automated observation of a running system's health | Ongoing, in production | Aggregated signals (for example, error rates) over time | No |
| **Observability** (a later-stage topic) | The broader practice/capability of understanding a system's internal state from its external outputs | Ongoing, especially for complex or production systems | Logs, metrics, and traces together | No |

**Important framing:** this table is a comparison to clarify *purpose*, not a claim that these tools
are interchangeable. Several rows above (profiler, monitoring, observability) name concepts only to
locate the debugger correctly among its neighbors — none of them are taught in this lesson.

---

## 29. Small Practical Exercises

All exercises use tiny, disposable, local Python programs. No external services, credentials, or
production data are required anywhere in this section.

### Level 1 — Conceptual Exercises

1. In your own words, define "debugger" and "debugging," and explain how they differ (Section 2,
   Section 3).
2. Define "breakpoint" and explain why a developer would choose to place one at a specific line rather
   than everywhere (Section 6).
3. Explain, in your own words, the difference between step over, step into, and step out (Section 7).
4. Define "call stack" and "stack frame," and explain the difference between them (Section 9).
5. Explain why a variable's runtime value is considered stronger evidence than an assumption formed by
   reading the source code (Section 8).
6. Define "stack trace" and explain how it differs from using a debugger (Section 10).
7. In your own words, describe the full debugging reasoning loop from Section 2
   (observe/hypothesize/inspect/test/isolate/fix/verify).
8. Explain the difference between a symptom and a root cause, using an example not already used in this
   lesson.

### Level 2 — Hands-On Exercises

Use this small program for the exercises below:

```python
def calculate_average(numbers):
    total = 0
    for number in numbers:
        total += number
    average = total / len(numbers)
    return average

def main():
    scores = [80, 90, 100]
    result = calculate_average(scores)
    print(result)

main()
```

1. Set a line breakpoint (Section 6) on the line `average = total / len(numbers)`.
2. Run the program under a debugger and confirm execution pauses at that breakpoint.
3. Inspect the variable `total` (Section 8) at the paused point and confirm its value matches what you
   expect given `scores`.
4. Inspect the function argument `numbers` inside `calculate_average` (Section 8) and confirm it
   matches `scores` from `main`.
5. Use Step Over (Section 7) to execute the `average = ...` line, then inspect the resulting value of
   `average`.
6. Use Step Out (Section 7) to return from `calculate_average` back into `main`, and confirm where
   execution pauses next.
7. Inspect the call stack (Section 9) while paused inside `calculate_average`, and identify which
   function is the caller.
8. Modify `scores` to an empty list (`[]`), set an exception breakpoint (Section 6, Section 11) if your
   tool supports one, and observe what happens when `len(numbers)` becomes `0` inside the division.

### Level 3 — Reasoning Exercises

For each scenario, answer: where would you place the breakpoint? what state would you inspect? what
hypothesis would you form? what evidence would confirm or refute it?

1. A function that is supposed to double every number in a list instead returns the list unchanged.
2. A total that should include tax is consistently too low by a fixed-looking amount.
3. A program that should print one message per item in a list only prints it once.
4. A function sometimes returns the correct result and sometimes does not, depending on the input.
5. An exception occurs, but the stack trace points to a line that looks completely correct on its own.
6. A value that was correct earlier in the program has become incorrect by the time it reaches a later
   function.
7. Two different code paths are supposed to produce the same result but do not.
8. A loop appears to run one time fewer (or more) than expected.

### Level 4 — Debugging Exercises

Each program below contains one intentional bug. Do not look ahead for a solution before attempting
your own investigation using this lesson's methodology (Section 17).

1. **Problem description:** a function meant to return the largest number in a list sometimes returns
   the wrong one.
   ```python
   def find_max(numbers):
       largest = 0
       for number in numbers:
           if number > largest:
               largest = number
       return largest
   ```
   **Expected behavior:** `find_max([-5, -2, -9])` should return `-2`.
   **Actual behavior:** it returns `0`.
   **Debugging objective:** find why the result is `0` instead of `-2`.
   **Suggested investigation direction:** inspect the initial value of `largest` before the loop runs.
   **Learner task:** use a breakpoint and stepping to confirm exactly where the wrong value originates.

2. **Problem description:** a function meant to check whether a number is even reports the wrong
   result for negative numbers.
   ```python
   def is_even(number):
       return number % 2 == 1
   ```
   **Expected/actual:** determine both by inspecting the condition's evaluated result for a known even
   number.
   **Debugging objective:** find the logical mistake in the condition.
   **Suggested investigation direction:** inspect the actual computed value of `number % 2` for a
   simple test case.
   **Learner task:** step through and inspect the comparison's operands and result.

3. **Problem description:** a function meant to greet a user with their name instead always greets
   "None."
   ```python
   def greet(name=None):
       message = f"Hello, {name}"
       return message

   def main():
       user_name = "Ava"
       greeting = greet()
       print(greeting)
   ```
   **Debugging objective:** find why `name` is `None` instead of `"Ava"`.
   **Suggested investigation direction:** step into `greet` and inspect its parameter immediately.
   **Learner task:** use the call stack to compare what `main` intended to pass against what actually
   arrived.

4. **Problem description:** a function meant to remove duplicate values from a list still returns
   duplicates.
   ```python
   def deduplicate(items):
       result = []
       for item in items:
           result.append(item)
       return result
   ```
   **Debugging objective:** find the missing logic.
   **Suggested investigation direction:** step through the loop and inspect `result` after each
   iteration.
   **Learner task:** identify exactly which check is missing by observing state over time (Section
   19).

5. **Problem description:** a function meant to build a full name from first and last name produces an
   extra, unexpected space.
   ```python
   def full_name(first, last):
       return first + " " + " " + last
   ```
   **Debugging objective:** find the exact source of the extra space.
   **Suggested investigation direction:** inspect the exact string value produced, character by
   character if needed.
   **Learner task:** confirm the root cause using variable inspection rather than only visual
   inspection of the source.

6. **Problem description:** a function that should raise no exception for valid input raises one
   unexpectedly.
   ```python
   def get_last_item(items):
       return items[len(items)]
   ```
   **Debugging objective:** find why accessing "the last item" causes an exception.
   **Suggested investigation direction:** inspect the exact index being accessed versus the list's
   actual valid range.
   **Learner task:** use an exception breakpoint (Section 6, Section 11) to pause exactly at the
   failure and inspect state there.

7. **Problem description:** a function meant to sum only positive numbers in a list includes negative
   numbers too.
   ```python
   def sum_positive(numbers):
       total = 0
       for number in numbers:
           if number != 0:
               total += number
       return total
   ```
   **Debugging objective:** find why negative numbers are being included.
   **Suggested investigation direction:** inspect the condition being used to decide inclusion.
   **Learner task:** step through with a list containing both positive and negative numbers and observe
   exactly which ones enter the `if` branch.

8. **Problem description:** a function meant to check whether a list is empty behaves incorrectly.
   ```python
   def is_empty(items):
       return not items == []
   ```
   **Debugging objective:** determine what this function actually returns for an empty list versus a
   non-empty one, and why it does not match the intended meaning of "is empty."
   **Suggested investigation direction:** inspect the boolean result of `items == []` before the `not`
   is applied.
   **Learner task:** identify the logical mistake using direct expression evaluation (Section 3,
   Section 12) if your debugger supports it.

### Level 5 — Applied AI Engineering Exercises

All examples below are small, local, and dependency-light — no API keys or external services are
required.

1. **Preprocessing:** a function meant to normalize text by lowercasing it only lowercases some words.
   Use a debugger to inspect the actual string state after each transformation step (Section 19) to
   find where the transformation is incomplete.
   ```python
   def normalize(text):
       words = text.split(" ")
       result = words[0].lower()
       return result
   ```
2. **Data transformation:** a function meant to convert a list of raw scores into percentages produces
   values far larger than 100. Use variable inspection (Section 8) to check the actual values being
   divided and multiplied.
   ```python
   def to_percentages(scores, max_score):
       return [score * 100 * max_score for score in scores]
   ```
3. **Model configuration:** a function meant to read a configuration value for "number of training
   epochs" always uses a default value, even when a specific value was provided. Use the call stack
   (Section 9) and variable inspection to trace why the provided value never reaches the point where it
   is used.
   ```python
   def get_epochs(config):
       epochs = config.get("epochs", 10)
       epochs = 10
       return epochs
   ```
4. **Prompt construction:** a function meant to build a prompt string by combining a system instruction
   and a user question instead only includes the system instruction. Step through the function
   (Section 7) and inspect the final constructed string (Section 8) to find the missing piece.
   ```python
   def build_prompt(system_instruction, user_question):
       prompt = system_instruction
       return prompt
   ```
5. **Retrieval/context assembly:** a function meant to combine several retrieved text chunks into one
   context string only includes the first chunk. Use state-transition debugging (Section 19) —
   inspecting the accumulating result after each step of a loop — to find where the accumulation stops
   happening.
   ```python
   def assemble_context(chunks):
       context = ""
       for chunk in chunks:
           context = chunk
       return context
   ```

---

## 30. Structured Debugging Exercise

### "Find the Root Cause"

The following small Python program is meant to process a list of customer orders, apply a discount to
orders over a certain size, and compute the total revenue across all orders. It contains one realistic,
intentionally introduced bug.

```python
def apply_discount(order_total, discount_rate):
    if order_total > 100:
        discounted = order_total - (order_total * discount_rate)
        return discounted
    return order_total

def process_orders(order_totals, discount_rate):
    grand_total = 0
    for order_total in order_totals:
        discounted_total = apply_discount(order_total, discount_rate)
        grand_total = discounted_total
    return grand_total

def main():
    orders = [50, 120, 80, 200]
    discount_rate = 0.1
    total_revenue = process_orders(orders, discount_rate)
    print(total_revenue)

main()
```

**Expected behavior:** `total_revenue` should equal the sum of all four (possibly discounted) order
totals.

**Actual behavior:** `total_revenue` reflects only one order's discounted total, not the sum of all
four.

### The learner's task

1. **Reproduce the problem** — confirm the printed result does not match the sum you would expect from
   manually applying the discount logic to all four orders.
2. **Define expected behavior** — state precisely what `total_revenue` should equal.
3. **Form a hypothesis** — where in `process_orders` might the accumulation across orders be going
   wrong?
4. **Place targeted breakpoints** — on the line inside the loop in `process_orders`.
5. **Inspect variables** — watch `discounted_total` and `grand_total` on each loop iteration.
6. **Inspect the call stack** — confirm how `apply_discount` is being called from `process_orders`, and
   how `process_orders` is called from `main`.
7. **Step through execution** — step through each iteration of the loop and observe exactly how
   `grand_total` changes (or fails to change as expected) each time.
8. **Identify the incorrect state transition** — using Section 19's model, find the specific line where
   "correct accumulated state" becomes "incorrect accumulated state."
9. **Identify the root cause** — state, precisely, the specific mistake (not just "the total is
   wrong").
10. **Fix it** — make the smallest correction that addresses that specific root cause.
11. **Verify the behavior** — confirm `total_revenue` now equals the correct sum for the given `orders`.
12. **Explain why the bug occurred** — in your own words, describe why this specific mistake produced
    exactly the observed symptom.

This exercise is intentionally not trivial: the visible symptom ("the total looks wrong") does not,
by itself, reveal whether the mistake is in `apply_discount`'s discount logic or in `process_orders`'s
accumulation logic — that distinction must be established through the investigation itself, using
Section 17's workflow, not assumed in advance.

---

## 31. Mini-Project

### Developer Debugging Workflow

The application below conceptually follows:

```text
input
  |
validation
  |
transformation
  |
processing
  |
result
```

It contains several intentional defects, spanning multiple bug categories, for the learner to
investigate using a debugger.

```python
def validate_input(raw_records):
    valid_records = []
    for record in raw_records:
        if "amount" in record:
            valid_records.append(record)
    return valid_records

def transform_record(record):
    amount = record["amount"]
    category = record.get("category", "general")
    return {"amount": amount, "category": category}

def apply_category_multiplier(transformed_record):
    multipliers = {"general": 1.0, "priority": 1.5, "bulk": 0.8}
    category = transformed_record["category"]
    multiplier = multipliers["general"]
    return transformed_record["amount"] * multiplier

def process_records(raw_records):
    validated = validate_input(raw_records)
    total = 0
    for record in validated:
        transformed = transform_record(record)
        value = apply_category_multiplier(transformed)
        total = value
    return total

def main():
    raw_records = [
        {"amount": 100, "category": "priority"},
        {"amount": 50, "category": "bulk"},
        {"amount": 30},
    ]
    result = process_records(raw_records)
    print(result)

main()
```

This program contains, among its defects, at least: an **incorrect value** (the multiplier lookup
does not actually use the record's own `category`), an **incorrect function argument/state usage** (a
variable is read but effectively never used to influence the result), and a **state transition
problem** (the running total is not actually accumulated across records — directly connecting to
Section 19). Depending on the exact data used, this can also produce **incorrect branch** behavior
and, with different input, an **exception** (for example, if a record without an `"amount"` key
reached `transform_record` without first passing through `validate_input` correctly).

### Objective

Apply this lesson's complete debugging methodology (Section 17) to investigate and correct the
program above.

### Requirements

- Use only this disposable example program; no external services, credentials, or production data.
- Use a debugger (Section 3) as the primary investigation tool, applying breakpoints (Section 6),
  stepping (Section 7), variable inspection (Section 8), and call-stack inspection (Section 9).
- Document your work as described below, in your own personal notes.

### Learner tasks

For **each** defect you find, document:

- **observed symptom** — what output or behavior is wrong,
- **hypothesis** — your specific, testable guess about the cause,
- **breakpoint strategy** — where you placed breakpoints and why (Section 6),
- **inspected state** — which variables and call-stack frames you examined (Section 8, Section 9),
- **call stack findings** — what the call stack revealed about how execution reached the relevant
  point,
- **root cause** — the specific underlying mistake, precisely stated (Section 2),
- **fix** — the specific correction applied,
- **verification** — how you confirmed the fix actually resolved the symptom (Section 2, Section 17),
- **regression-test idea** — in your own words, what a test guarding against this specific mistake
  reoccurring might check (Section 16) — you are not required to actually write the test, only to
  describe it conceptually.

### Suggested approach

1. Run the program once, unmodified, and record the actual printed result as your starting symptom.
2. Manually compute, on paper or in your notes, what the correct result *should* be for the given
   `raw_records`, to define expected behavior precisely (Section 17, step 2).
3. Use the structured process from Section 30 as a template, repeated for each defect you uncover.
4. After each fix, re-run the program and re-verify before moving to the next defect — do not attempt
   to fix every defect at once (directly avoiding the mistake described in Section 20: "changing
   multiple things at once").

This mini-project is intentionally the most substantial exercise in this lesson — it is meant to
exercise the entire debugging workflow (Section 17) against a small system with more than one
interacting defect, closely mirroring the kind of multi-stage processing code (Section 23) the learner
will encounter throughout the rest of this roadmap.

---

## 32. Review Section

- **What is debugging?** The engineering process of moving from an observed symptom to an understood,
  fixed root cause, using evidence rather than guessing (Section 2).
- **What is a debugger?** A tool that lets a developer pause a running program, inspect its state, and
  step through its execution in a controlled way (Section 3).
- **Why do debuggers exist?** Because ordinary program execution only shows final output or a crash,
  not the reasoning behind incorrect behavior; debuggers make the program's live state directly
  observable (Section 4).
- **What is a breakpoint?** A deliberately chosen point where execution should pause for inspection
  (Section 6).
- **What is stepping?** Controlled, incremental advancement through a paused program's execution —
  over, into, and out of function calls (Section 7).
- **What is program state?** The current values of a program's variables and data at a given moment
  (Section 8).
- **What is a call stack?** The ordered record of which function called which, leading to the current
  point in execution (Section 9).
- **What is a stack frame?** The specific record, within the call stack, of one active function call
  and its local variables (Section 9).
- **How does a stack trace differ from an interactive debugger?** A stack trace is a static snapshot
  showing *how* execution reached a failure; a debugger provides live, interactive inspection of *what
  state* existed there and control over further execution (Section 10).
- **Debugger vs logging?** A debugger requires a live, pausable program; logging records events for
  later review, especially useful where interactive debugging is impractical, such as production
  (Section 15).
- **Debugger vs print statements?** Both have genuine advantages and disadvantages; neither is
  universally superior (Section 14).
- **Debugger vs testing?** A debugger investigates *why* something is wrong; a test verifies *whether*
  behavior is correct — they complement each other directly (Section 16).
- **Debugger vs profiler?** A debugger investigates correctness/state; a profiler investigates
  performance characteristics (Section 28) — different questions entirely.
- **Debugging workflow?** A systematic, fifteen-step process converging from reproduction to a verified,
  root-cause fix (Section 17).
- **Debugging failure modes?** Problems with the debugging process itself — such as a breakpoint never
  hitting, or environment mismatches — distinct from bugs in the program being debugged (Section 21).
- **Production considerations?** Interactive debugging carries real operational, performance, and
  security risk in production; logs, metrics, and traces are generally the safer, more appropriate
  tools there (Section 24, Section 25, Section 26).
- **AI engineering applications?** The same fundamental skills — breakpoints, stepping, state and
  call-stack inspection — apply directly across Python programs, data pipelines, ML systems, LLM
  applications, RAG systems, and agent systems, though a debugger cannot evaluate whether an AI
  model's actual output is good (Section 23).

---

## 33. Self-Assessment

Answer "yes" only if you can actually perform the skill, not merely recall its definition.

- [ ] I can explain what a debugger is in my own words.
- [ ] I can explain why breakpoints exist.
- [ ] I can set a targeted breakpoint.
- [ ] I can inspect runtime state.
- [ ] I understand step over.
- [ ] I understand step into.
- [ ] I understand step out.
- [ ] I can interpret a call stack.
- [ ] I understand stack frames conceptually.
- [ ] I can use a debugger to investigate an exception.
- [ ] I can distinguish symptom from root cause.
- [ ] I can form and test a debugging hypothesis.
- [ ] I can explain debugger vs logging.
- [ ] I can explain debugger vs testing.
- [ ] I can debug a small Python program systematically.
- [ ] I understand why production debugging differs from local debugging.
- [ ] I understand how debugger skills apply to AI engineering.

---

## 34. Interview Questions

**Q: What is a debugger?**
A: A tool that lets a developer pause a running program's execution, inspect its current state, and
step through its execution in a controlled way (Section 3).

**Q: Why use a debugger instead of print statements?**
A: A debugger allows inspecting *any* state at a paused moment interactively, without modifying source
code or requiring a rerun for every new question, though print statements remain simpler for quick,
well-understood checks — neither is universally superior (Section 14).

**Q: What is a breakpoint?**
A: A marker placed at a specific location in code that tells the debugger to pause execution when that
point is reached (Section 6).

**Q: What is the difference between step over, step into, and step out?**
A: Step over executes the current line without entering any function it calls; step into enters a
called function to inspect it directly; step out finishes the current function and returns to its
caller (Section 7).

**Q: What is a call stack?**
A: The ordered record of which function called which, showing the full chain of calls that led to the
current point in execution (Section 9).

**Q: What is a stack frame?**
A: The specific record, within the call stack, corresponding to one active function call, holding its
local variables and its return location (Section 9).

**Q: How does a debugger differ from a stack trace?**
A: A stack trace is a static snapshot showing the call path to a failure; a debugger provides live,
interactive inspection and control of execution at any chosen point (Section 10).

**Q: When is logging preferable to interactive debugging?**
A: When investigating production systems, long-running or distributed processes, or incidents that
already happened — situations where pausing a live process is impractical or risky (Section 15,
Section 24).

**Q: What is a conditional breakpoint?**
A: A breakpoint that only pauses execution when a specified condition is true, useful when a line runs
many times but only a specific occurrence is of interest (Section 6).

**Q: How would you debug a function receiving an unexpected value?**
A: Step into the function and inspect its parameters directly, then use the call stack to trace back to
the caller and inspect what was actually passed at the call site (Section 8, Section 9; Example C,
Section 18).

**Q: How would you debug an exception?**
A: Use an exception breakpoint to pause automatically at the point of failure, then inspect the call
stack and variable state to trace the exception back toward its actual root cause, which may be earlier
than the exception's own location (Section 11; Example D, Section 18).

**Q: What would you do if a breakpoint is never hit?**
A: Confirm the code path actually reaches that line under the current input, confirm the debugger is
attached to the correct running process, and check whether a conditional breakpoint's condition is
ever actually true (Section 21).

**Q: Why can debugging change program timing?**
A: Because pausing and stepping deliberately interrupt normal execution, which can alter the behavior
of bugs that depend on precise timing or concurrent execution (Section 22, Section 26).

**Q: Why is interactive debugging problematic in production?**
A: It can disrupt real requests, expose sensitive data present in memory, and introduce operational and
security risk, whereas logs, metrics, and traces allow safer, after-the-fact investigation (Section 24,
Section 25).

**Q: How would debugger skills apply to an AI application?**
A: The same skills — breakpoints, stepping, state and call-stack inspection — apply directly to
investigating incorrect prompt construction, context assembly, tool arguments, and state-management
bugs, though they cannot by themselves evaluate whether a model's actual output is good (Section 23).

---

## 35. Architecture / Engineering Questions

**Q: How would you design a debugging workflow for a local Python service?**
A: Establish a reliable reproduction of the issue, define expected behavior precisely, and apply the
systematic workflow from Section 17 — targeted breakpoints, state and call-stack inspection, stepping —
converging toward a verified root-cause fix rather than open-ended inspection.

**Q: How would debugging differ between a monolithic application and a distributed system?**
A: A monolithic application can typically be fully understood within a single debugger session attached
to one process; a distributed system involves multiple communicating processes that a single local
debugger session cannot fully observe, requiring greater reliance on logs and traces across the whole
system (Section 21, Section 24).

**Q: How would you debug an AI pipeline with multiple processing stages?**
A: Apply state-transition debugging (Section 19) — inspecting state at the boundary between each
stage — to locate specifically which stage transforms correct input into incorrect output, rather than
only examining the final result.

**Q: Where should debugging responsibility exist in a production architecture?**
A: Primarily through logs, metrics, traces, and safe, deliberate diagnostic tooling built into the
system itself, rather than routine reliance on attaching an interactive debugger to live processes
(Section 24, Section 25).

**Q: How would you combine logs, metrics, traces, and interactive debugging?**
A: Use logs/metrics/traces to detect and narrow down where a problem occurred in a live or
already-finished system, then reproduce the issue locally where an interactive debugger can safely be
used for detailed root-cause investigation (Section 15, Section 24).

**Q: How would you protect secrets and user data during debugging?**
A: Avoid debugging with real credentials or production data (Section 25), be aware that paused state
may expose sensitive values, and restrict debugging access to trusted, deliberate sessions rather than
leaving debugging capability broadly available.

**Q: How would you debug an agent whose behavior depends on state transitions and tool calls?**
A: Apply call-stack and state inspection (Section 8, Section 9) at each state transition and each tool
invocation, using state-transition debugging (Section 19) to find exactly where the agent's internal
state or chosen action first diverges from what was intended (Section 23).

**Q: How would you distinguish a software execution bug from a model-quality problem?**
A: Use a debugger to confirm whether the surrounding code (prompt construction, context assembly, tool
invocation, response handling) executed exactly as intended; if the code is confirmed correct and the
output is still unsatisfactory, the issue lies in the model's behavior itself, which requires
evaluation practices outside the scope of software debugging (Section 23).

---

## 36. Production Application

```text
Bug
 |
Reproduction
 |
Evidence
 |
Hypothesis
 |
Debugger / Logs / Traces
 |
Root Cause
 |
Fix
 |
Verification
 |
Regression Prevention
```

This chain is the same disciplined reasoning process taught throughout this lesson (Section 2, Section
17), applied at any scale — from a single small local script to a large production system. What
changes at larger scale is primarily *which tools* are appropriate at the "Debugger / Logs / Traces"
step (Section 15, Section 24), not the underlying reasoning process itself.

### How this foundation connects forward

- **Software engineering** — this same methodology underlies professional debugging practice generally.
- **Backend engineering** — services with many interacting components rely on this same evidence-based
  investigation, often combined with logs and traces (Section 15).
- **Testing** — failing tests (Section 16) are frequently the trigger that starts this entire chain.
- **Observability** — a later-stage discipline built directly on the logging/tracing concepts touched
  on in Section 15 and Section 24.
- **Distributed systems** — extend the "Debugger / Logs / Traces" step across multiple communicating
  processes (Section 21, Section 24).
- **ML engineering** — applies this methodology to preprocessing, training, and evaluation code
  (Section 23).
- **LLM application engineering, RAG, agent systems** — apply this same methodology to the specific bug
  categories introduced in Section 23, while remaining clearly separate from model/behavioral
  evaluation.
- **Production incident investigation** — this exact chain, performed under real operational
  constraints and using the safer tools discussed in Section 24 and Section 25.

None of these later topics are taught in depth here. The purpose of this section is only to establish
that the debugging mental model built in this lesson is not a beginner-only technique — it is the same
reasoning process used throughout professional software and AI engineering, at every scale.

---

## 37. Key Takeaways

- A debugger is an observation and execution-control tool, not a source of automatic answers.
- A breakpoint is a deliberate investigation point, chosen strategically, not placed everywhere.
- Runtime evidence is more reliable than assumptions formed by reading source code alone.
- The call stack explains how execution reached a location, not just where it currently is.
- Stepping helps reveal actual control flow, which can differ from what the source code's layout
  suggests.
- Debugging should be hypothesis-driven — observe, hypothesize, inspect, test, isolate, fix, verify.
- A debugger does not replace testing — one investigates, the other verifies.
- A debugger does not replace logging or observability — each fits different situations, especially at
  different scales and in production.
- Interactive debugging is mainly a development/investigation technique, not a routine production
  practice.
- Production debugging requires operational safety — performance, security, and privacy all matter.
- Debugging software execution is different from evaluating AI behavior — a debugger can confirm code
  ran as written; it cannot judge whether a model's output is actually good.
- Good debugging focuses on root cause rather than symptoms, converging toward understanding rather
  than continuing indefinitely.
