# What Happens When a Function Executes

**Module:** Stage 0 — Module 0.1: How Computers Work | Concept 18

---

## 1. What Is a Function?

A **function** is a reusable block of program logic that can receive inputs, perform operations, and optionally return a result. Calling a function involves real work: transferring control, preparing inputs, managing execution state, executing instructions, and returning to the caller.

Functions allow developers to reuse logic instead of writing the same instructions repeatedly.

---

## 2. How Function Execution Works

The conceptual sequence is:

1. The caller requests a function call.
2. **Arguments** (actual input values) are supplied to the function's **parameters** (names that receive those values).
3. Control transfers to the called function, known as the **callee**.
4. Execution state is established for that particular call.
5. The CPU executes the function's instructions.
6. The function may calculate and return a value.
7. Control returns to the caller, which continues execution.

A **return value** is the result handed back to the caller. A **local variable** is used inside a function's execution.

---

## 3. Call Stack, Stack Frames, and Recursion

The **call stack** tracks active function calls using **LIFO (Last In, First Out)** ordering. Each active call commonly has a **stack frame**, which may hold or reference arguments, local variables, return information, saved registers, and temporary state.

For example:

```
main() → calculate() → process()
```

The return order is `process()` → `calculate()` → `main()`. As functions finish, their call state unwinds and can be released or reused.

**Recursion** occurs when a function calls itself. Each active call has separate execution state. Excessive recursion can exceed Python's recursion-depth limit (`RecursionError`); this is related to, but not identical to, native stack overflow.

---

## 4. CPU, Registers, RAM, and Threads

The CPU executes instructions, while registers may hold arguments, temporary values, addresses, or return-related information. Call-related state commonly resides in RAM. The call stack is only one part of process memory; it is not the same as the heap or all of RAM.

Each thread generally needs its own call stack because each thread can have a different active call sequence.

Function calls have overhead, although compiler optimizations such as inlining can reduce or eliminate some call overhead. Exact implementation varies by language, runtime, compiler, and architecture. Python functions do not map one-to-one to CPU instructions.

---

## 5. Practical Work, Debugging, and AI Engineering

The module demonstrates:

- Python function calls and nested calls, confirming the return order.
- Controlled recursion and a `RecursionError`.
- Reading Python tracebacks to understand the call chain leading to an error.
- Compiling C code and inspecting actual `call`, `ret`, and register-related instructions using `gcc` and `objdump`.
- Checking tool availability first and using an isolated temporary directory in WSL2; `gdb` was unavailable in the documented environment.

It includes 37 exercises, review questions, expected learning outcomes, debugging scenarios, and an answer key at `exercises/18-what-happens-when-a-function-executes-answer-key.md`. Common mistakes addressed include confusing functions with processes, assuming every variable lives on the stack, and treating function calls as cost-free.

For AI engineers, this knowledge helps debug Python applications, API handlers, data pipelines, preprocessing and inference flows, recursion problems, and production incidents using tracebacks.

**Scope boundary:** Detailed calling conventions, runtime internals, memory-management internals, thread synchronization, and advanced optimization are deferred.

---

## Next Concept

**Concept 19 — Why RAM and Storage Are Different**
