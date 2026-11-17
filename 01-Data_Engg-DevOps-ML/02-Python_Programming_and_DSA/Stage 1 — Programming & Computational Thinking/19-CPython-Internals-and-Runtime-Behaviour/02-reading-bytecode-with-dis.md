# Reading Bytecode with `dis`

> **Target:** CPython 3.12–3.14.  
> **Purpose:** Learn to read bytecode as evidence about how CPython implements Python operations—not as a stable description of Python language semantics.  
> **Compatibility rule:** Never assume that an opcode sequence, offset, cache layout, instruction count, or disassembly format is stable across Python versions. Record the interpreter version for every experiment.

## Learning outcomes

By the end of this lesson, you should be able to:

1. Explain CPython's stack-machine evaluation model and how instructions use a value stack and local-variable storage.
2. Read the columns produced by `dis.dis()` and interpret instruction offsets, opcodes, arguments, and resolved arguments.
3. Recognise common load/store, arithmetic, call, return, comparison, and jump instructions.
4. Explain how branches, loops, short-circuit expressions, and conditional expressions appear in bytecode.
5. Inspect functions and closures, including closure cells, `MAKE_CELL`, `LOAD_DEREF`, and late-binding behaviour.
6. Explain the implementation change for comprehensions in Python 3.12 under PEP 709.
7. Recognise generator, context-manager, exception-table, async, f-string, pattern-matching, and exception-group bytecode patterns.
8. Use `dis.Bytecode`, `dis.get_instructions()`, `show_caches=True`, and `adaptive=True` appropriately.
9. Compare code variants using both bytecode inspection and sound timing methodology.
10. Build a small stack-machine interpreter and answer the three syllabus self-check questions.
11. Explain why bytecode-based tools and decompilers are version-sensitive and why bytecode is weak source-code protection.

## Prerequisites

You should know basic Python functions, expressions, loops, conditionals, exceptions, generators, and closures. Lesson 01, **Source-to-Bytecode Pipeline**, explains how source is compiled into code objects; this lesson concentrates on reading those code objects.

Use CPython 3.12, 3.13, or 3.14. Check your interpreter before running examples:

```bash
python --version
python -c "import sys; print(sys.implementation); print(sys.executable)"
```

If you have multiple interpreters, invoke the version explicitly. Many examples run on all three target versions, but the bytecode shown is intentionally not pinned to one exact listing.

## 1. Mental model: a stack machine

CPython compiles a function into a code object. Its bytecode is a sequence of instructions. In a simplified mental model, instructions operate on a **value stack**: they push values onto it, pop values from it, or replace several values with a result. Local variables are stored separately from that value stack; CPython has specialised instructions for common local-variable access.

For example, an expression such as:

```python
def add_scaled(a, b):
    return a + b * 2
```

must load `b` and the constant `2`, multiply them, load `a`, add the results, and return the final value. `dis` lets us inspect how the compiler represents those operations.

```text
Python source
    |
    v
code object
    |
    v
bytecode instructions
    |
    v
value stack + locals + globals/builtins + runtime objects
    |
    v
evaluation loop performs Python operations
```

This is a conceptual model, not a complete description of CPython's C implementation. Modern CPython also uses inline caches, adaptive specialisation, exception tables, and implementation-specific execution strategies. The exact execution strategy and instruction set differ between CPython releases and builds.

### What this model is good for

- Understanding the order of operations and control flow.
- Explaining why closures need cells or why a generator suspends.
- Investigating compiler changes between Python releases.
- Forming hypotheses about performance before measuring them.
- Building educational tools such as bytecode visualisers and tiny interpreters.

### Limitations

Bytecode is not machine code. Instructions can trigger rich Python operations, including method dispatch, descriptors, allocation, exceptions, and calls into native extensions. One opcode is not necessarily one CPU instruction or one unit of time. Python's language semantics—not a particular bytecode listing—define the behaviour programs should rely on.

## 2. Reading `dis.dis()` output

### 2.1 First example

```python
import dis

def add(a, b):
    return a + b * 2

dis.dis(add)
```

`dis.dis()` prints a disassembly of the function's code object. On modern CPython, the display commonly includes some or all of these columns:

- **Source location:** a line number by default; Python 3.14 can display finer source positions with `show_positions=True`.
- **Offset:** bytecode instruction offset, not a source line number. Python 3.13 added `show_offsets=True`; offsets are hidden in the default text display on 3.13+, even though `Instruction.offset` remains available programmatically. Inline caches can create gaps in offsets.
- **Opcode:** instruction name, such as a load, arithmetic operation, call, or jump.
- **Argument:** the numeric or symbolic operand encoded for an instruction, when it has one.
- **Resolved argument / instruction detail:** a human-readable interpretation such as a constant, local variable name, logical jump label, or global name.

Exact columns, offsets, opcodes, jump labels, and display formatting vary by version. Python 3.13 changed jump-target display to logical labels by default; do not assert a literal disassembly in a cross-version test.

The semantic order in this example is multiplication before addition because Python expression precedence requires it. A representative conceptual sequence is:

```text
load local b
load constant 2
multiply
load local a
add
return result
```

A modern CPython listing may use `LOAD_FAST`, `LOAD_CONST`, `BINARY_OP`, and `RETURN_VALUE`, but it may differ in offsets, specialisation, or other details. The important point is the data flow, not memorising the printed offsets.

### 2.2 Key opcode families

These names are useful for orientation. Exact availability and semantics must be checked for the Python version being inspected.

| Opcode family / examples | Conceptual role |
| --- | --- |
| `LOAD_CONST` | Push a constant from the code object's constant table. |
| `LOAD_FAST`, `STORE_FAST` | Read/write a local variable in the function's fast-local storage. |
| `LOAD_GLOBAL` | Resolve a global name, with built-ins participating in fallback lookup. |
| `LOAD_ATTR` | Retrieve an attribute, potentially invoking descriptors or other dynamic behaviour; argument encoding and method-call optimisations vary by version. |
| `STORE_NAME`, `LOAD_NAME` | Name access used in code blocks such as module/class scopes, depending on context. |
| `STORE_GLOBAL`, `STORE_DEREF`, `LOAD_DEREF`, `MAKE_CELL`, `LOAD_CLOSURE`, `MAKE_FUNCTION` | Store globals, access closure/cell variables, or construct a function with its metadata/closure. The exact closure-building sequence is version-sensitive. |
| `BINARY_OP` | Perform an arithmetic or related binary operation; modern CPython uses an argument to identify the operation. |
| `COMPARE_OP` | Compare values, with version-specific details for comparison operations. |
| `CALL` | Invoke a callable using the current call protocol. |
| `RETURN_VALUE`, `RETURN_CONST` | Return a value; availability and compiler use vary by version. |
| `POP_JUMP_IF_*`, other jump instructions | Branch based on a condition or transfer control to another instruction. Exact names change across versions. |
| `GET_ITER`, `FOR_ITER` | Obtain an iterator and advance a `for` loop. |
| `BEFORE_WITH` | Enter the context-manager protocol in versions using this opcode; cleanup and exceptional flow also depend on the exception table and other instructions. |
| `BINARY_SUBSCR` / `BINARY_OP` | Subscription historically used `BINARY_SUBSCR`; in CPython 3.14 it was replaced by `BINARY_OP` with the `NB_SUBSCR` operation argument. |
| `YIELD_VALUE`, `RETURN_GENERATOR`, `RESUME` | Participate in generator/coroutine execution in modern CPython. |
| `CACHE` | Represents inline-cache entries in disassembly when requested; cache layout is an implementation detail. |

**Do not memorise this table as a fixed opcode inventory.** It is a map for reading output. For authoritative opcode definitions, use the `dis` documentation for the target version and the matching CPython source, particularly `Python/bytecodes.c`.

### 2.3 Inspecting instructions programmatically

Printed output is convenient for humans. For tools, use `dis.get_instructions()` or `dis.Bytecode`.

```python
import dis

def compute(value):
    return value * 3 + 1

for instruction in dis.get_instructions(compute):
    print(
        instruction.offset,
        instruction.opname,
        instruction.arg,
        instruction.argval,
        instruction.starts_line,
    )
```

`Instruction` objects expose attributes such as `offset`, `opname`, `arg`, `argval`, `argrepr`, `starts_line`, and `positions` where supported. This is better than scraping `dis.dis()` text, but the instruction stream itself is still version-sensitive. In Python 3.13, `get_instructions()` no longer yields separate `CACHE` items; cache details are exposed through instruction metadata, and its `show_caches` parameter is deprecated/has no effect. Check the docs for the exact minor version before depending on these details.

`dis.Bytecode(compute)` provides an iterable wrapper and convenient disassembly methods. `show_offsets` is available from Python 3.13 and `show_positions` from 3.14 for supported disassembly APIs. The `python -m dis` CLI also gained cache/offset options in 3.13 and position/specialized-output options in 3.14; do not pass these flags to older interpreters without checking support. Use these APIs for inspection and teaching tools; avoid making production behaviour depend on exact offsets or opcodes unless the tool explicitly supports a narrowly defined CPython version matrix.

## 3. Control flow in bytecode

Control-flow instructions transfer execution between positions in a code object. The compiler must preserve the language's rules for conditions, loops, short-circuit evaluation, and exceptions, but it can choose different instruction sequences across releases.

### 3.1 `if` and `else`

```python
import dis

def classify(value):
    if value > 0:
        return "positive"
    else:
        return "zero or negative"

dis.dis(classify)
```

Conceptually, the code loads `value`, compares it with zero, branches based on the truth value of the comparison, and returns one of the strings. The compiler may use conditional jump instructions whose names and direction differ by version.

**Why it matters:** reading the branch structure helps explain which paths can run and why an operation may not execute. It can also support coverage analysis, although coverage tools must account for line tables, branches, and version-specific instruction mapping.

**Limitation:** a disassembly alone does not tell you which branch will be taken for a particular input. You must reason about values and runtime semantics.

### 3.2 `while`, `for`, `break`, and `continue`

```python
def sum_until(values, limit):
    total = 0
    for value in values:
        if value > limit:
            break
        total += value
    return total
```

A `for` loop obtains an iterator and repeatedly asks for the next item. `GET_ITER` and `FOR_ITER` are familiar markers in many CPython versions. The loop body may contain a conditional branch for `break`, a store for `total`, and a jump back to the iteration point. `while` loops similarly compile into conditional tests and jumps.

`continue` transfers control to the next loop test/iteration point. `break` exits the loop. The compiler may rearrange or combine instructions, so identify the control-flow graph rather than expecting a fixed sequence.

**Real-world example:** when investigating a slow ETL loop, disassembly may confirm that a global function is looked up inside the loop, but it does not establish that this lookup is the dominant cost. Profiling and representative benchmarks are still needed.

### 3.3 Short-circuit evaluation: `and` and `or`

Python's `and` and `or` operators short-circuit: they do not evaluate the right-hand operand when the left-hand operand determines the result.

```python
def eligible(user):
    return user is not None and user.is_active()
```

If `user is None`, `user.is_active()` is not called. Bytecode implements this behaviour using conditional control flow. The precise jump names and stack effects vary by Python version.

This matters for correctness when the right side has side effects or may raise an exception. It also means that replacing a short-circuit expression with an eager function call can change semantics.

### 3.4 Conditional expressions

```python
def label(score):
    return "pass" if score >= 50 else "retry"
```

A conditional expression evaluates the condition and chooses exactly one result expression. Disassembly shows a conditional branch and a path to the selected value. Do not confuse this with an eager expression that evaluates both alternatives.

### 3.5 How to reason about jumps safely

When reading a jump:
1. Identify the condition value and where it came from.
2. Determine which target the instruction names (a logical label in the default 3.13+ text output, or an offset if requested/available).
3. Trace both the jump and fall-through paths.
4. Check where each path leaves values on the stack.
5. Confirm where paths join and whether they return, raise, or continue a loop.

For tooling, `dis.stack_effect(opcode, oparg, jump=True/False)` can help estimate stack changes for a supported opcode and branch direction. It is not a substitute for matching the opcode and argument to the target CPython version.

Modern disassembly may display jump targets symbolically. Treat offsets as locations in that code object, not stable labels that survive recompilation.

## 4. Functions, calls, and global/local lookup

### 4.1 Local variables versus global variables

Function locals often use fast-local instructions such as `LOAD_FAST` and `STORE_FAST`. A global name typically uses `LOAD_GLOBAL`, which resolves the name in the function's global namespace and then, if needed, the built-ins namespace. Module and class bodies can use different name-access instructions.

```python
FACTOR = 10

def scale(value):
    return value * FACTOR
```

The parameter `value` is local; `FACTOR` is global. `dis.dis(scale)` can show the different lookup operations. The exact opcode names and any specialisation are version-specific.

### 4.2 Attribute access and method calls

```python
def get_name(user):
    return user.name

def call_method(user):
    return user.is_active()
```

Attribute access can invoke Python's descriptor protocol, custom `__getattribute__`, properties, or other dynamic behaviour. A `LOAD_ATTR` instruction is therefore not necessarily a cheap field read. Calling a method may involve attribute lookup and a call protocol that the compiler/interpreter can optimise.

In modern CPython, some instructions can have specialised forms or inline caches. These are implementation optimisations and may be invalidated when observed types or runtime conditions change.

### 4.3 Local aliasing and performance folklore

A common micro-optimisation is to bind a frequently used global function to a local variable before a loop. This changes lookup and local-load instructions, and it historically could reduce lookup overhead. Modern CPython versions specialise global and attribute access, so the benefit may be small, absent, or workload-dependent. Treat “local aliasing is faster” as a hypothesis, not a rule.

Use a benchmark to test a concrete hypothesis on the target interpreter and workload. Prefer readability unless a repeatable measurement shows a meaningful benefit.

## 5. Functions and closures: cells and late binding

A closure allows a nested function to access variables from an enclosing function after the outer call has returned. CPython represents captured bindings using **cell objects**.

```python
import dis

def make_adder(amount):
    def add(value):
        return value + amount
    return add

add_five = make_adder(5)
print(add_five(7))  # 12
dis.dis(make_adder)
dis.dis(add_five)
```

Depending on the version, outer-function bytecode may include instructions such as `MAKE_CELL` and `LOAD_CLOSURE`; inner-function bytecode may use `LOAD_DEREF` to read the captured binding. The exact sequence and names can change.

- `MAKE_CELL` is associated with making a local available as a closure cell in relevant CPython versions.
- `LOAD_CLOSURE` loads a cell for closure construction in versions that expose this instruction.
- `LOAD_DEREF` accesses a cell/free variable.
- `STORE_DEREF` stores through a cell, including for `nonlocal` assignments.

Do not assume every closure uses precisely this sequence in every release. Inspect the code objects' `co_freevars` and `co_cellvars` to connect the bytecode to the scope model.

### 5.1 Late binding captures a variable binding, not a snapshot

```python
def make_functions():
    functions = []
    for number in range(3):
        functions.append(lambda: number)
    return functions

functions = make_functions()
print([function() for function in functions])
```

Representative output:

```text
[2, 2, 2]
```

Each lambda refers to the same loop variable binding, whose final value is `2` when the functions are called. The closures capture a cell/binding rather than an independent copy of the value at each iteration.

A common fix is to bind the current value as a default argument:

```python
def make_functions():
    functions = []
    for number in range(3):
        functions.append(lambda number=number: number)
    return functions

print([function() for function in make_functions()])
# [0, 1, 2]
```

The default-argument technique changes how values are stored; it is not a general replacement for understanding closure semantics. Disassembly can help distinguish local/default handling from closure-cell access.

### 5.2 `nonlocal`

```python
def counter():
    value = 0

    def increment():
        nonlocal value
        value += 1
        return value

    return increment
```

The `nonlocal` declaration makes `increment` update the binding in the enclosing function. Bytecode commonly uses cell-related operations for that access. The language-level meaning of `nonlocal` is the contract; exact opcodes are CPython details.

## 6. Comprehensions: the Python 3.12 change (PEP 709)

Before Python 3.12, list, set, and dict comprehensions were generally implemented using a separate nested code object and function-like execution. PEP 709, implemented in CPython 3.12, inlined comprehensions into the surrounding code in common cases.

```python
import dis

def squares(values):
    return [value * value for value in values]

dis.dis(squares)
```

On CPython 3.11 and earlier, disassembly commonly shows a nested comprehension code object and a call into it. On CPython 3.12+, the comprehension is generally inlined, so the outer function's bytecode shows the iteration and element-building work directly. Exact details can vary for different comprehension forms and Python versions.

**Why it matters:** PEP 709 reduces overhead and changes the shape of disassembly and some introspection observations. Tooling that assumes every comprehension has its own code object must be updated.

**What does not change:** language-level comprehension scope semantics must be preserved. Inlining is an implementation technique, not permission for loop variables to leak into surrounding scope.

Generator expressions are different: they are lazy and produce generator objects, so they retain generator machinery rather than being equivalent to an eagerly built list comprehension.

## 7. Generators and `yield`

A generator function suspends execution when it yields a value and resumes later. Its local state and execution position must survive between calls to `next()` or `send()`.

```python
import dis

def gen():
    for i in range(3):
        yield i * i

dis.dis(gen)

g = gen()
print(next(g))  # 0
print(next(g))  # 1
print(next(g))  # 4
```

Modern CPython generator disassembly may include `RETURN_GENERATOR`, `RESUME`, `YIELD_VALUE`, and return-related instructions. These are version-sensitive implementation details. The language-level behaviour is that each `yield` suspends the generator and returns a value to its caller; a later resume continues from the suspension point.

Generator expressions are also lazy. A list comprehension computes a collection immediately; a generator expression computes values as it is iterated. This has memory and timing implications, not just bytecode differences.

**When useful:** inspect generator bytecode when diagnosing suspension, cleanup, or unexpectedly deferred work. To understand state precisely, combine disassembly with `inspect`/generator attributes and a small runtime experiment.

## 8. `with`, `try`, and exception tables

A `with` statement guarantees that its context manager's exit protocol is invoked according to the language rules, including when an exception occurs inside the block. CPython must compile the body and cleanup paths so that exceptional control flow is correct.

Before Python 3.11, bytecode often used setup instructions such as `SETUP_FINALLY` to represent parts of exception handling. Python 3.11 and later use exception tables to describe exceptional control-flow regions, removing the need for the older setup-opcode pattern in the same form.

```python
import dis

def read_first_line(path):
    with open(path, encoding="utf-8") as stream:
        return stream.readline()

dis.dis(read_first_line)
```

On CPython 3.11+, inspect the exception-table display in `dis` output (where shown) as well as the ordinary instructions. The exact layout is version-specific.

The phrase **zero-cost exceptions** is shorthand for reducing normal-path setup overhead in the exception-handling implementation. It does not mean raising or handling exceptions is free, nor that all context-manager cleanup costs nothing.

**Real-world example:** when auditing resource handling, use the source semantics to verify that a file is closed correctly. Disassembly can help explain the compiled cleanup path, but it is not a substitute for tests that exercise both normal and exceptional exits.

## 9. Adaptive specialisation and inline caches

CPython 3.11 introduced the specialising adaptive interpreter. It can adapt execution of some instructions based on runtime observations. The baseline bytecode and the currently specialised execution form may differ.

Use `dis` options to inspect these views:

```python
import dis

def total(values):
    result = 0
    for value in values:
        result += value
    return result

print("Default disassembly:")
dis.dis(total)

print("With inline caches:")
dis.dis(total, show_caches=True)

# Execute repeatedly to give the interpreter opportunities to specialise.
for _ in range(20):
    total([1, 2, 3, 4])

print("Adaptive view, if supported by this interpreter:")
dis.dis(total, adaptive=True, show_caches=True)
```

`show_caches=True` displays cache entries associated with instructions where supported. `adaptive=True` requests an adaptive/specialised view in supported CPython versions. The exact output, cache count, specialisation names, and whether a given instruction specialises depend on version, build, and execution history.

**Why it matters:** reading only the baseline disassembly and drawing a performance conclusion can miss what the interpreter does after warm-up.

**Limitations:** adaptive disassembly is diagnostic, not a stable public format. Running a function a fixed number of times does not guarantee a particular specialisation state. Specialisation can depend on operand types and can change or deoptimise.

## 10. Async/await, async iteration, and async context managers

`async def` creates a coroutine function. Calling it creates a coroutine object; the coroutine's body runs when it is driven by an event loop or another await mechanism. `await` delegates through the awaitable protocol. The event loop's scheduling policy is not the same thing as bytecode execution.

```python
import dis

async def fetch_value(awaitable):
    value = await awaitable
    return value

dis.dis(fetch_value)
```

Depending on CPython version, async-related disassembly may include instructions such as `GET_AWAITABLE`, `SEND`, `YIELD_VALUE`, and `RESUME`. Older instructions such as `YIELD_FROM` should not be assumed to appear in current versions for every await pattern.

`async for` and `async with` compile into machinery that awaits iteration and context-manager operations. They still follow the language-level protocols for asynchronous iterators and asynchronous context managers.

**Practical use:** disassembly can help explain why calling an `async def` function without awaiting or scheduling its coroutine does not execute the body to completion. It cannot tell you when a coroutine will be scheduled relative to other tasks; inspect the event-loop code and runtime traces for that.

## 11. F-strings, `match`, and `except*`

### 11.1 F-strings

```python
import dis

def greeting(name, count):
    return f"Hello, {name}! Count={count:03d}"

dis.dis(greeting)
```

F-string compilation may use `FORMAT_VALUE` and `BUILD_STRING` in older target releases. `CONVERT_VALUE` and `FORMAT_SIMPLE` were added in CPython 3.13; exact instruction selection depends on the expression, conversion, format specification, and release. CPython 3.14 also adds template-string machinery such as `BUILD_INTERPOLATION` and `BUILD_TEMPLATE`, which is related but is not simply another spelling of an ordinary f-string. Do not assume a fixed sequence or that every formatted string compiles identically.

PEP 701 changed f-string grammar in Python 3.12. That is primarily a parsing/tokenisation change, but compiler output and tooling expectations can also differ as syntax evolves. For bytecode claims, inspect the target interpreter.

### 11.2 Structural pattern matching

```python
import dis

def describe(value):
    match value:
        case {"kind": "ok", "value": result}:
            return ("ok", result)
        case _:
            return ("other", None)

dis.dis(describe)
```

Pattern matching can compile into a series of checks, unpacking operations, comparisons, and conditional branches. The specific instruction sequence depends on the pattern and CPython version. Read it as a control-flow implementation of the language's pattern-matching rules, not as a one-to-one opcode per `case`.

### 11.3 Exception groups and `except*`

`except*` handles matching subgroups of an exception group, a feature introduced by PEP 654. Its implementation requires more elaborate exception-handling control flow than a simple `except` clause. Disassembly may contain exception-handling and stack-management instructions whose exact layout varies.

When analysing this area, first understand the source-level exception-group semantics. Use bytecode to investigate how a specific CPython release implements those semantics; do not infer the language rules solely from opcode names.

## 12. Bytecode count is not runtime speed

A shorter disassembly is not proof of a faster program. One instruction may invoke complex Python-level dispatch; another may operate on a cached or specialised path. Allocations, input size, CPU state, data layout, branch behaviour, and native-library work can dominate.

The roadmap suggests comparing examples such as `+=` versus `join`, local alias versus global lookup, and a dictionary literal versus `dict()`. Use both disassembly and measurement. Keep each experiment narrow: verify semantic equivalence, vary input sizes where relevant, and measure on the exact interpreter/build you plan to deploy.

### 12.1 Example variants

```python
def concatenate_plus(parts):
    result = ""
    for part in parts:
        result += part
    return result

def concatenate_join(parts):
    return "".join(parts)
```

These functions may compile into different bytecode, but timing depends on input size, string lengths, interpreter version, and allocation behaviour. For many fragments, `join` is often the appropriate idiom because it avoids repeatedly constructing an accumulated result, but benchmark the actual workload.

Two more comparisons from the roadmap are useful when investigating a suspected hot loop:

```python
GLOBAL_FACTOR = 3

def global_lookup(values):
    total = 0
    for value in values:
        total += value * GLOBAL_FACTOR
    return total

def local_alias(values):
    total = 0
    factor = GLOBAL_FACTOR
    for value in values:
        total += value * factor
    return total

def make_with_literal():
    return {"a": 1, "b": 2}

def make_with_dict():
    return dict(a=1, b=2)
```

The global and local versions have the same result for an unchanged `GLOBAL_FACTOR`; if that global can be rebound during execution, their lookup timing can differ semantically. The dictionary forms also produce equivalent dictionaries here, but compile and call different machinery. Do not conclude which is faster from source length or instruction count alone.

### 12.2 A basic benchmark with `timeit`

```python
import timeit

parts = ["record"] * 500

plus_time = timeit.timeit(
    lambda: concatenate_plus(parts),
    number=200,
)
join_time = timeit.timeit(
    lambda: concatenate_join(parts),
    number=200,
)

print("plus:", plus_time)
print("join:", join_time)
```

The times are intentionally not supplied here: they must be measured on your environment. Repeat measurements, compare distributions or use `pyperf` for more rigorous work, and keep inputs equivalent. `timeit` can reduce some measurement noise but cannot make an unrealistic benchmark representative.

### 12.3 Better benchmarking practice

1. State the hypothesis before looking at results.
2. Record the Python version, build, OS, and workload.
3. Use identical inputs and verify equivalent results.
4. Inspect bytecode as an explanation aid, not the success criterion.
5. Repeat measurements; use `pyperf` for more reliable comparisons.
6. Avoid timing tiny one-off operations when startup, allocation, or timer noise dominates.
7. Benchmark the complete application path when that is what users experience.
8. For local-alias and dictionary-construction experiments, measure multiple repeats and relevant input sizes; avoid extrapolating a tiny constant-size case to a different workload.

For a repeatable multi-process benchmark, save the following as `bench_dis_variants.py` after copying the six functions from Section 12.1 into the file. Install `pyperf` in the same environment, then run `python bench_dis_variants.py`. This optional benchmark script is intentionally separate from the lesson's core standard-library examples:

```python
import pyperf

parts = ["record"] * 500
values = list(range(1000))
runner = pyperf.Runner()

# The functions concatenate_plus, concatenate_join, global_lookup,
# local_alias, make_with_literal, and make_with_dict are defined above.
runner.bench_func("concat_plus", concatenate_plus, parts)
runner.bench_func("concat_join", concatenate_join, parts)
runner.bench_func("global_lookup", global_lookup, values)
runner.bench_func("local_alias", local_alias, values)
runner.bench_func("dict_literal", make_with_literal)
runner.bench_func("dict_constructor", make_with_dict)
```

Before timing, inspect each pair and verify equivalent outputs (for the global/local pair, keep `GLOBAL_FACTOR` unchanged). You can count the baseline instructions with `len(list(dis.get_instructions(function)))`, but that count is itself version-sensitive. By default, this counts yielded instructions rather than treating inline cache slots as independent operations; the API for exposing cache details changed in Python 3.13. Use `pyperf` results—not instruction counts—as the performance evidence, and retain the benchmark JSON/report with the interpreter/build details.

## 13. Version differences and CPython source

Bytecode changes frequently. For example:

- `PRECALL` appeared in Python 3.11-era disassemblies and was removed from the instruction set in Python 3.13; do not expect it to appear in 3.13+ output.
- `BINARY_OP` represents multiple operations in modern CPython; in CPython 3.14 it also handles subscription via the `NB_SUBSCR` argument, replacing the old `BINARY_SUBSCR` opcode.
- `CONVERT_VALUE` and `FORMAT_SIMPLE` were added in 3.13 for f-string formatting; `BUILD_INTERPOLATION` and `BUILD_TEMPLATE` are new 3.14 template-string machinery.
- `RESUME`, `CACHE`, adaptive/specialised instruction forms, and super-instructions reflect interpreter implementation changes.
- Exception-table-based handling replaced older setup-opcode patterns in Python 3.11.
- PEP 709 changed common comprehension compilation in Python 3.12.
- Python 3.13 defaults to logical labels for jump targets and hides offsets in text output unless `show_offsets=True`; Python 3.14 adds `show_positions=True` to show fine-grained source positions.
- Instruction offsets, jump conventions, call protocol, and disassembly formatting can change.

The CPython source file `Python/bytecodes.c` is a useful source for opcode definitions and interpreter implementation in releases that use it. Its DSL and surrounding implementation are version-sensitive. When investigating a claim, select the matching CPython release tag rather than reading only the development branch.

Official docs for `dis` also contain version-change notes. Prefer the documentation for the exact interpreter being debugged.

## 14. Bytecode tooling, coverage, decompilation, and security

### 14.1 Coverage and tracing tools

Coverage tools associate execution events with source lines and branches. Bytecode and line tables can help explain how source constructs map to executable instructions, but line events are not a one-to-one record of every opcode. Python version changes can require coverage tools to update their mapping logic.

For diagnostics, prefer supported tracing/monitoring interfaces where suitable. Do not assume an opcode-level view is the same as line coverage.

### 14.2 Decompilers

Tools such as `uncompyle6`, `decompyle3`, and `pycdc` attempt to reconstruct source-like code from bytecode or code objects. They can be useful for authorised debugging or recovering structure when source is unavailable, but support often lags new Python releases and some constructs cannot be reconstructed exactly.

Bytecode does not preserve all source-level details. Comments and formatting are lost, and compiler transformations can erase distinctions between source forms. Decompiled output is therefore a reconstruction, not guaranteed original source.

### 14.3 Obfuscation and source protection

Distributing `.pyc` or otherwise obscuring source does not provide strong confidentiality. Bytecode can often be inspected, analysed, or partially decompiled. Do not put secrets, credentials, private algorithms that must remain confidential, or security-critical policy solely behind an assumption that users cannot inspect the shipped code.

### 14.4 Testing disassembly

It is possible to write tests that assert particular instructions exist, but such tests are brittle across interpreter versions and compiler changes. Avoid bytecode assertions in ordinary application tests. If you are writing a bytecode tool or supporting a specific CPython release, pin the interpreter version, document the supported range, and test each supported version deliberately.

## 15. Practical experiments

Record your exact interpreter version and keep an experiment notebook. For each experiment, write down what was observed and what it does **not** establish.

### Experiment A — Read a basic function's bytecode

**Question:** How does a simple arithmetic expression map to loads, operations, and return?

**Setup:**

```python
import dis

def add(a, b):
    return a + b * 2

dis.dis(add)
```

**Procedure:** run under CPython 3.12, 3.13, or 3.14. Identify instructions corresponding to loading `a`, `b`, and `2`, multiplying, adding, and returning.

**Expected observations:** the disassembly shows local and constant loads, arithmetic operations, and a return path. Exact opcode names, offsets, and cache/specialisation details can vary.

**Interpretation:** the bytecode implements Python's expression precedence and return semantics using a sequence of operations on values.

**What it does not prove:** it does not prove that the listing is stable across versions or that the function's performance can be inferred from instruction count.

### Experiment B — Compare a branch and a loop

**Question:** How do `if`, `for`, `break`, and short-circuiting affect control flow?

**Setup:**

```python
import dis

def first_large(values, limit):
    for value in values:
        if value > limit and value < limit * 10:
            return value
    return None

dis.dis(first_large)
```

**Procedure:** identify iterator setup, loop advancement, conditional tests, and return paths. Then compare with a version that separates the `and` condition into nested `if` statements.

**Expected observations:** there are jump instructions for loop control and conditional paths. The exact control-flow structure may differ with compiler optimisations and version.

**Interpretation:** short-circuiting means the second comparison is skipped when the first condition is false. The disassembly gives evidence of branch structure.

**What it does not prove:** it does not establish which branch dominates in production or whether one source version is faster. That requires representative input and measurement.

### Experiment C — Inspect a closure

**Question:** Which bytecode and metadata indicate that a nested function captures an enclosing variable?

**Setup:**

```python
import dis

def outer(amount):
    def inner(value):
        return value + amount
    return inner

fn = outer(5)
print("free vars:", fn.__code__.co_freevars)
dis.dis(outer)
dis.dis(fn)
```

**Procedure:** compare `co_freevars` with the inner function's disassembly. Look for cell-related instructions in the outer function and dereference operations in the inner function where present.

**Expected observations:** `amount` is identified as a free variable for `inner`; the bytecode shows closure-related machinery, though exact instructions vary.

**Interpretation:** a closure captures an enclosing binding through cell-based machinery in CPython.

**What it does not prove:** it does not mean every closure has an identical instruction sequence or that a closure captures a frozen value rather than a binding.

### Experiment D — Compare comprehension versions

**Question:** How did PEP 709 change the bytecode shape of common comprehensions?

**Setup:**

```python
import dis

def squares(values):
    return [value * value for value in values]

dis.dis(squares)
```

**Procedure:** run the same file under CPython 3.11 (if available) and CPython 3.12+. Compare whether the comprehension is represented by a nested code object or inlined into the enclosing function.

**Expected observations:** Python 3.11 commonly shows a separate comprehension code object; CPython 3.12+ generally inlines common list/set/dict comprehensions according to PEP 709.

**Interpretation:** implementation changes can alter disassembly and performance while preserving language-level scope semantics.

**What it does not prove:** it does not imply generator expressions are identical to list comprehensions or that every comprehension form has the same implementation.

### Experiment E — Inspect caches and adaptive disassembly

**Question:** How does adaptive disassembly differ from the baseline view?

**Setup:** use the example in Section 9.

**Procedure:** disassemble before running the function repeatedly, execute it with representative input, then disassemble with `adaptive=True` and `show_caches=True`.

**Expected observations:** cache entries and specialised forms may appear. Their presence and names depend on the runtime and warm-up history.

**Interpretation:** the interpreter may adapt instructions based on observed execution.

**What it does not prove:** it does not prove that a fixed number of calls guarantees specialisation or that a specialised listing will remain stable.

### Experiment F — Compare bytecode and measured performance

**Question:** Does a difference in bytecode correspond to a meaningful speed difference for this workload?

**Setup:** use the string-concatenation functions and benchmark in Section 12.

**Procedure:** verify both functions return the same string, disassemble both, then measure repeatedly with equivalent inputs. For a serious comparison, use `pyperf` and test the production Python version.

**Expected observations:** the code variants compile differently; timings are measured and may vary by environment. `join` often performs well for many fragments, but the magnitude is workload-dependent.

**Interpretation:** bytecode is one part of the explanation; timing evaluates the actual runtime effect.

**What it does not prove:** a microbenchmark does not guarantee the same relative performance in a different application, Python release, or workload.

### Experiment G — Compare local aliasing and dictionary construction

**Question:** Do a local alias for a global and a dictionary literal outperform their alternatives on the interpreter you deploy?

**Setup:** use the `global_lookup`, `local_alias`, `make_with_literal`, and `make_with_dict` functions from Section 12.1. First assert that each pair returns equivalent results for the chosen input.

**Procedure:** disassemble each pair, then measure repeated calls with the same input and `timeit.repeat()` or `pyperf`. Test more than one `values` length for the loop pair. Record CPython version/build, OS, repeat count, and workload; avoid running unrelated CPU-heavy tasks during measurement.

**Expected observations:** the variants can compile to different instruction sequences. Modern specialisation may reduce or alter the cost of global lookup; dictionary literal construction and the `dict` call take different paths. Timing results are environment- and workload-dependent, so no fixed winner is asserted here.

**Interpretation:** a stable, meaningful difference across repeated runs can support a workload-specific choice. If the difference is within noise, prefer the clearer code.

**What it does not prove:** it does not establish a universal performance rule or show that bytecode count caused the measured difference. The global and local-alias functions can also differ semantically if the global is rebound during a call, so compare them only under a clearly stated invariant.

### Experiment H — Read a framework wrapper

**Question:** Can you explain a real function's control flow without confusing implementation details with its public behaviour?

**Setup:** choose an installed, authorised framework function or wrapper (for example, a small Flask view wrapper if Flask is already installed). Record the exact package and Python versions. Avoid dumping or sharing application secrets.

**Procedure:** inspect the function source with `inspect.getsource()` where available, then run `dis.dis(function)` and `dis.get_instructions(function)`. Identify argument loads, calls, branches, exception paths, and returns. If the function is decorated, compare the wrapper with `function.__wrapped__` only when that attribute exists and the library documents or conventionally exposes it.

**Expected observations:** the bytecode may contain more machinery than the visible source because of decorators, argument handling, instrumentation, or compiler choices. Source may be unavailable for native functions or dynamically generated wrappers.

**Interpretation:** bytecode can corroborate a control-flow hypothesis, but the public contract comes from the framework/API and runtime behaviour.

**What it does not prove:** it does not prove the wrapper is correct, that a branch is exercised in production, or that a specific instruction dominates latency.

## 16. Exercise: build a tiny stack-machine interpreter

This exercise internalises the core model. Implement a deliberately small instruction set with `PUSH`, `ADD`, `MUL`, `JUMP_IF_ZERO`, and `PRINT`. It is **not** a Python bytecode interpreter; it is a toy virtual machine.

### Instruction format

Represent each instruction as a tuple:

- `("PUSH", value)` — push an integer onto the value stack.
- `("ADD",)` — pop two values and push their sum.
- `("MUL",)` — pop two values and push their product.
- `("JUMP_IF_ZERO", target)` — pop a value; if it is zero, set the instruction pointer to `target`, otherwise continue.
- `("PRINT",)` — pop a value and print it.

The instruction pointer is an integer index into the program list. Define jump targets as zero-based instruction indices. Each instruction advances the pointer by one unless it explicitly changes the pointer. Use a loop to fetch and execute instructions until the pointer is outside the program.

### Starter implementation

```python
def run(program):
    stack = []
    ip = 0

    while 0 <= ip < len(program):
        instruction = program[ip]
        opcode, *args = instruction
        ip += 1

        if opcode == "PUSH":
            stack.append(args[0])

        elif opcode == "ADD":
            right = stack.pop()
            left = stack.pop()
            stack.append(left + right)

        elif opcode == "MUL":
            right = stack.pop()
            left = stack.pop()
            stack.append(left * right)

        elif opcode == "JUMP_IF_ZERO":
            value = stack.pop()
            if value == 0:
                ip = args[0]

        elif opcode == "PRINT":
            print(stack.pop())

        else:
            raise ValueError(f"unknown opcode: {opcode}")

    return stack
```

This implementation intentionally omits validation for malformed programs, stack underflow, and invalid jump targets. Add those checks as an extension.

### Test 1 — arithmetic

```python
program = [
    ("PUSH", 6),
    ("PUSH", 7),
    ("MUL",),
    ("PRINT",),
]
run(program)
```

Expected output:

```text
42
```

### Test 2 — conditional jump

```python
program = [
    ("PUSH", 0),              # 0
    ("JUMP_IF_ZERO", 4),      # 1: jump to instruction 4
    ("PUSH", 999),            # 2: skipped
    ("PRINT",),               # 3: skipped
    ("PUSH", 42),             # 4
    ("PRINT",),               # 5
]
run(program)
```

Expected output:

```text
42
```

### Test 3 — loop with a counter

Extend the instruction set with `DUP`, `SUB`, and unconditional `JUMP`, or design a loop using the existing conditional jump plus additional instructions. Write down the stack contents before and after each instruction for at least one full loop iteration. Ensure the loop has a termination condition.

**Questions to answer:**
1. Why does `ADD` pop the right operand before the left operand?
2. What goes wrong if the jump target is not a valid instruction index?
3. How would you add a `HALT` instruction?
4. Which details of this toy VM resemble CPython, and which details are deliberately simplified?

The exercise should take roughly 40 lines once you add validation and loop support. Keep it small enough that you can reason about stack effects manually.

## 17. Common mistakes and diagnostic steps

### Mistake: treating bytecode as a stable API

**Why wrong:** instruction sets, argument conventions, cache layouts, offsets, and disassembly output change.  
**Do instead:** check `sys.version`, use the matching `dis` documentation, and avoid cross-version opcode assertions.

### Mistake: assuming fewer instructions always means faster

**Why wrong:** instructions differ in cost, and one instruction may trigger a dynamic operation or native call.  
**Do instead:** state a hypothesis, inspect bytecode, and benchmark equivalent workloads.

### Mistake: reading only baseline bytecode

**Why wrong:** adaptive specialisation can change the runtime execution form.  
**Do instead:** where supported, compare baseline output with `dis.dis(..., adaptive=True, show_caches=True)` after representative execution.

### Mistake: reading opcode names without following stack effects

**Why wrong:** an opcode's role depends on the values already on the stack and the control-flow path.  
**Do instead:** trace the stack, local values, and branch targets step by step. Consult `dis.stack_effect()` for supported opcode/argument combinations when writing tools, while remembering that opcode inputs are version-sensitive.

### Mistake: assuming a closure captures the value at definition time

**Why wrong:** closures capture bindings, which may change before the function is called.  
**Do instead:** inspect `co_freevars`, compare cell-related bytecode, and test late-binding examples.

### Mistake: assuming comprehensions always have a separate code object

**Why wrong:** PEP 709 changed common list, set, and dict comprehension implementation in CPython 3.12.  
**Do instead:** compare versions and preserve language-level semantics in your explanation.

### Mistake: treating decompiled output as original source

**Why wrong:** bytecode loses comments, formatting, and some source-level distinctions. Decompilers may also lack support for the version that produced the code.  
**Do instead:** label output as reconstructed and validate behaviour in an authorised environment.

### Troubleshooting checklist

1. Confirm the interpreter and build.
2. Reduce the code to a minimal function.
3. Inspect the baseline disassembly first.
4. Trace loads, stores, stack effects, and jump targets.
5. If investigating performance, inspect adaptive output only after recording the baseline.
6. Compare against version-specific docs and `Python/bytecodes.c`.
7. Test behaviour with normal Python tests; don't use a bytecode listing as the correctness oracle.
8. If analysing a framework function, inspect its source and runtime context as well as bytecode.
9. Never treat `.pyc` or bytecode obfuscation as a security boundary.

## 18. Summary and concept map

```text
function / code object
    |
    v
dis.dis / dis.Bytecode / dis.get_instructions
    |
    +--> loads and stores --> constants, locals, globals, attributes
    |
    +--> operations -------> arithmetic, comparisons, calls, returns
    |
    +--> control flow -----> branches, loops, short-circuit paths
    |
    +--> suspended state --> generators and coroutines
    |
    +--> exceptional flow -> exception tables and cleanup
    |
    +--> runtime adaptation -> caches and specialised instructions
    |
    v
interpret the listing as a version-specific implementation
    |
    v
verify semantics with tests and performance with benchmarks
```

Remember:

- Bytecode is a sequence of virtual-machine instructions, not native machine code.
- The value stack and local-variable storage are distinct.
- `dis` output helps explain implementation but is not a cross-version contract.
- Closures use captured bindings; late binding is not a bytecode bug.
- PEP 709 changed common comprehension implementation in CPython 3.12.
- Python 3.11+ exception tables changed the representation of exceptional control flow.
- Adaptive disassembly can reveal specialised execution, but it is diagnostic and unstable.
- Bytecode count is not runtime speed; measure the real workload.
- Decompilation is approximate and bytecode is not strong source protection.

## 19. Self-check questions with answers

### 1. Disassemble a closure and explain `MAKE_CELL` / `LOAD_DEREF`.

**Model answer:** Create an outer function with a local value and an inner function that reads it. Inspect `outer` and the returned inner function with `dis.dis()`, then inspect `inner.__code__.co_freevars` and `outer.__code__.co_cellvars`. In CPython versions that show these instructions, `MAKE_CELL` is associated with making a local available through a closure cell, while `LOAD_DEREF` reads a free/cell variable. The exact instruction sequence varies by version; the language-level explanation is that the inner function retains access to the enclosing binding.

### 2. Where did the old `SETUP_FINALLY` go, and what replaced it?

**Model answer:** Python 3.11 changed exception handling to use exception tables to describe exceptional control-flow regions, rather than relying on the older `SETUP_FINALLY` setup-opcode pattern. The normal path can avoid some setup overhead; exceptional paths still have real costs. Use `dis` output and documentation for the exact CPython release when examining a specific function.

### 3. Write a 40-line stack-machine interpreter for `PUSH`, `ADD`, `MUL`, `JUMP_IF_ZERO`, `PRINT` and test it with loops.

**Model answer:** Complete Section 16. Use a Python list as the value stack, an integer instruction pointer, and a dispatch loop. `PUSH` appends a value; `ADD` and `MUL` pop two values and push a result; `JUMP_IF_ZERO` pops a condition and changes the instruction pointer when it is zero; `PRINT` pops and displays a value. Add an unconditional jump or other instructions to build a terminating loop. Validate stack depth and jump targets so malformed programs fail with clear errors. The toy VM teaches stack effects and control flow, but it does not implement Python's object model, exception machinery, calls, closures, or CPython bytecode.

## References

Use the official documentation and source matching the interpreter being investigated:

- `dis` — Disassembler for Python bytecode: https://docs.python.org/3/library/dis.html (select the exact version, especially for Python 3.12–3.14 API/output changes).
- Python execution model: https://docs.python.org/3/reference/executionmodel.html
- What’s New in Python 3.12: https://docs.python.org/3.12/whatsnew/3.12.html
- What’s New in Python 3.13: https://docs.python.org/3.13/whatsnew/3.13.html
- What’s New in Python 3.14: https://docs.python.org/3.14/whatsnew/3.14.html
- Python expressions and evaluation order: https://docs.python.org/3/reference/expressions.html
- PEP 709 — Inlined comprehensions: https://peps.python.org/pep-0709/
- PEP 654 — Exception Groups and `except*`: https://peps.python.org/pep-0654/
- PEP 657 — Fine-grained error locations in tracebacks: https://peps.python.org/pep-0657/
- PEP 701 — Syntactic formalization of f-strings: https://peps.python.org/pep-0701/
- CPython source, `Python/bytecodes.c`, at the release tag matching the interpreter.
- The version-specific “What’s New” documentation for Python 3.11, 3.12, 3.13, and 3.14.

For every claim about an opcode, cache, offset, or specialised instruction, record the exact interpreter version and verify it there. Use language documentation to establish Python semantics and implementation sources to understand CPython-specific mechanics.
