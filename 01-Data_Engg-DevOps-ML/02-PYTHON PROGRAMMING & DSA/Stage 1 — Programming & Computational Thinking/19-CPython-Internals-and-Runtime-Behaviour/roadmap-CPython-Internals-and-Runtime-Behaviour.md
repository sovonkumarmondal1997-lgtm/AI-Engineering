# Roadmap — Module 1.19: CPython Internals and Runtime Behaviour

This is the learning roadmap for the nineteenth module of Stage 1,
**Programming & Computational Thinking**. It tells you **what** to learn
about how CPython (the reference Python implementation) actually runs your
code, **in what order**, **how** to practise each topic, and **how to prove
to yourself** that you have learned it.

You do not need to read C to benefit from this module. You need a precise
mental model of: how source becomes bytecode, how bytecode is executed in
frames on a stack, how imports find and run modules, how memory is allocated,
what the GIL really protects, what the specialising interpreter and JIT
change, and how to introspect and debug a running interpreter. That model
turns mysterious behaviour (slow imports, memory that never shrinks, "why is
threading not faster?", odd tracebacks) into explainable facts.

It connects directly to earlier modules: Stage 0 (how computers, processes
and virtual memory work), Module 1.9 (object model, GC, concurrency
vocabulary), Module 1.11 (descriptors, `__slots__`, MRO), Module 1.12
(AST, `exec`), and Module 1.17 (profiling, GC, memory). Concurrency
*practice* (threads, processes, asyncio) is covered in Stage 2 module 10;
this module explains the **runtime mechanics** underneath.

> Target: **CPython 3.12–3.14**. Internals change quickly: always confirm
> details against the "What's New" notes and `Include/`/`Python/` sources of
> your exact version. Treat bytecode listings as illustrative, not stable.

---

## 1. Module outcome

By the end of this module you will be able to:

- Describe the pipeline: source → tokens → AST → symbol table → bytecode → evaluation.
- Read bytecode with `dis`, understand the stack machine, and explain what a function call, loop, comprehension and `with` compile to.
- Explain frames, the call stack, code objects, closures/cells, generators' suspended frames and why recursion has limits.
- Trace how `import` works: `sys.modules`, finders, loaders, specs, `sys.path`, `.pyc` caching and import hooks.
- Describe CPython memory management: reference counting, pymalloc arenas/pools, small-object optimisations, immortal objects, the cyclic GC.
- Explain the GIL, subinterpreters, and the free-threaded build, including what they do and do not guarantee.
- Describe the specialising adaptive interpreter, inline caches, and the experimental JIT.
- Use `sys`, `os`, `platform`, `inspect`, `gc` and `faulthandler` to introspect a runtime.
- Debug production-like failures post mortem and attach to live processes safely.
- Use `sys.monitoring` and tracing hooks to build tools.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| CPU, registers, instructions, compilation vs interpretation | Stage 0 — Module 0.1 (06, 07, 08) | Bytecode is a virtual ISA |
| Processes, threads, virtual memory, signals | Stage 0 — Module 0.2 | GIL, memory, `faulthandler` |
| What happens when a program/function starts | Stage 0 — Module 0.1 (17, 18) | Frames and stacks |
| Python object model & GC | Module 1.9 (10) | Foundation for lessons 03 and 05 |
| Concurrency vocabulary | Module 1.9 (11) | Lesson 06 |
| Descriptors, slots, MRO | Module 1.11 | Attribute lookup in bytecode |
| AST and `exec` | Module 1.12 (08, 09) | Front half of the pipeline |
| Profiling, GC tuning | Module 1.17 | Applications of internals |
| Packaging and imports | Modules 1.6, 1.18 | Import system context |
| Debuggers and tracebacks | Module 1.7 (05, 06) | Advanced debugging |

**Tools:** CPython 3.12+ (ideally also a 3.14 install via `uv python install`),
`dis`, `ast`, `symtable`, `tokenize`, `sys`, `gc`, `tracemalloc`, `faulthandler`,
`py-spy`, `gdb` (optional), and a clone of `github.com/python/cpython` for reading
`Python/ceval.c`, `Python/bytecodes.c`, `Objects/`, `Lib/importlib/`.

---

## 3. How the module is organised

```text
Phase A — From Source to Execution              (Basics → Intermediate)
  01 source-to-bytecode pipeline
  02 reading bytecode with dis
  03 frames, call stack, evaluation loop
Phase B — Modules and Memory                    (Intermediate)
  04 import system
  05 memory allocator and small-object optimisations
Phase C — Parallelism and Speed in the Runtime  (Advanced)
  06 GIL internals and subinterpreters
  07 specialising interpreter and JIT
Phase D — Observing and Debugging the Runtime   (Advanced)
  08 sys, os and runtime introspection
  09 post-mortem and remote-attach debugging
  10 sys.monitoring and tracing hooks
```

Pace: about 3–4 weeks part-time. Keep an **experiment notebook** (a
`notes/` folder of runnable scripts); each lesson requires at least two
experiments whose output you explain.

---

## Lesson 01 — `01-source-to-bytecode-pipeline.md`

**Why it matters.** When you know each compilation stage you can predict
which errors appear when (syntax vs name vs runtime), why `.pyc` files exist,
what `compile()` does, and how tools (linters, formatters, type checkers,
coverage, debuggers) hook in.

### Basic — what to learn

- CPython is a **bytecode compiler + virtual machine**, not a pure line-by-line interpreter.
- Pipeline stages: **tokenise** → **parse** (PEG parser since 3.9) → **AST** → **symbol table** (scopes) → **compile** to bytecode in a **code object** → **execute** in the evaluation loop.
- Seeing each stage from Python:

```python
import tokenize, io, ast, symtable, dis

src = "total = price * 2\n"
print([t.string for t in tokenize.generate_tokens(io.StringIO(src).readline)])
print(ast.dump(ast.parse(src), indent=2))
code = compile(src, "<demo>", "exec")
print(code.co_names, code.co_consts)
dis.dis(code)
```
- `.pyc` files in `__pycache__`: cached bytecode, keyed by source mtime/size or hash (PEP 552), invalidated automatically; they speed **import**, not execution.
- Errors by stage: `SyntaxError` (compile time) vs `NameError`/`TypeError` (run time).

### Intermediate — what to learn

- Code objects: `co_code`, `co_consts`, `co_names`, `co_varnames`, `co_freevars`, `co_cellvars`, `co_argcount`, `co_flags`, `co_stacksize`, `co_lnotab`/`co_positions()` (3.11+ fine-grained positions used in error carets).
- Compile modes: `"exec"`, `"eval"`, `"single"`; `compile(..., flags=ast.PyCF_ONLY_AST)`; optimisation levels (`-O` strips `assert`, `-OO` strips docstrings).
- The **symbol table** decides local/global/free/cell variables **at compile time**: this explains `UnboundLocalError` and closures (`nonlocal`).
- Compile-time optimisations: constant folding, dead-code elimination for `if False`, peephole/flow-graph optimisations, interning of identifiers.
- The importance of `__pycache__` in deployments (read-only filesystems, `PYTHONDONTWRITEBYTECODE`, `compileall`, container layers).
- `python -X importtime`, `-X dev`, `-X frozen_modules` basics.

```python
def f():
    print(x)      # x local? the symbol table says yes because of the assignment below
    x = 1
# f() -> UnboundLocalError: cannot access local variable 'x'
```

### Advanced — what to learn

- The PEG parser and grammar (`Grammar/python.gram`); soft keywords (`match`, `case`, `type`) and why they are context-sensitive; error-message improvements.
- Tokenizer changes (PEP 701 for f-strings in 3.12) and implications for tools; `tokenize` vs the C tokenizer.
- Frozen modules (`importlib._bootstrap`, startup speed), deep-frozen code objects, and how `python -X importtime` shows startup costs.
- Position information and exception carets (PEP 657); `co_positions()`; the "unreachable" and "line events" tables; line-number table (`co_linetable`).
- Source-level behaviours: encoding declarations, BOM, `from __future__` imports (compile-time directives), `__debug__`.
- Building tools on the pipeline: AST transformers (Module 1.12) → `compile()`; import hooks that transform source (e.g. pytest assertion rewriting) before compiling.
- Exercise: write a script that, for a given function, prints tokens, AST, symbol table, bytecode and `co_*` fields, and explain a surprising entry.
- Compare other implementations: PyPy (JIT, tracing), GraalPy, MicroPython, Jython (dead) — what is CPython-specific vs language semantics.

### Common mistakes

- Believing Python "interprets source text line by line".
- Expecting `.pyc` to make a running program faster.
- Forgetting that `-O` removes `assert` (never use assert for validation).

### Self-check

1. At which stage is `UnboundLocalError` determined and why?
2. What does a `.pyc` contain and when is it regenerated?
3. Write a script that shows the pipeline stages for a small function and explain every difference between `exec` and `eval` mode.

---

## Lesson 02 — `02-reading-bytecode-with-dis.md`

**Why it matters.** Bytecode explains performance folklore, closures,
comprehension scopes, `with`/`try` semantics, `async` machinery and f-string
costs. Being able to read it settles arguments with evidence.

### Basic — what to learn

- The evaluation model: a **stack machine** — instructions push/pop values on a value stack; locals are in a fast array (`LOAD_FAST`/`STORE_FAST`).
- `dis.dis(func)`: columns for line number, offset, opcode, argument, resolved argument.
- Key opcodes: `LOAD_CONST`, `LOAD_FAST`, `LOAD_GLOBAL`, `LOAD_ATTR`, `STORE_*`, `BINARY_OP`, `COMPARE_OP`, `CALL`, `RETURN_VALUE`/`RETURN_CONST`, `POP_JUMP_IF_*`, `FOR_ITER`, `GET_ITER`.

```python
import dis
def add(a, b):
    return a + b * 2
dis.dis(add)
# LOAD_FAST a ; LOAD_FAST b ; LOAD_CONST 2 ; BINARY_OP * ; BINARY_OP + ; RETURN_VALUE
```

### Intermediate — what to learn

- Control flow: `if/else`, `while`, `for` (`GET_ITER`, `FOR_ITER`, jump targets), `break`/`continue`, `and`/`or` short-circuit jumps, conditional expressions.
- Functions and closures: `MAKE_FUNCTION`, `LOAD_DEREF`/`STORE_DEREF`/`MAKE_CELL`, `LOAD_CLOSURE`; why late-binding closures capture variables (cells), not values.
- Comprehensions: separate code object (before 3.12) vs inlined (PEP 709, 3.12+); generator expressions and `YIELD_VALUE`.
- `with` statement: `BEFORE_WITH`, exception-table-based cleanup; **exception tables** (3.11+) instead of `SETUP_FINALLY` — "zero-cost" `try`.
- Attribute access, method calls (`LOAD_ATTR` method form), `LOAD_GLOBAL` with builtins; why local aliasing speeds loops.
- `dis` options: `dis.Bytecode`, `show_caches=True`, `adaptive=True` (3.11+) to see specialised instructions; `dis.get_instructions`.

```python
def gen():
    for i in range(3):
        yield i * i
dis.dis(gen)             # note RETURN_GENERATOR, YIELD_VALUE, RESUME
```

### Advanced — what to learn

- Reading async code: `async def`, `await` (`GET_AWAITABLE`, `SEND`, `YIELD_FROM`-like), `async with`/`async for`; how coroutine objects are driven.
- f-string bytecode (`FORMAT_VALUE`/`BUILD_STRING`, newer `FORMAT_SIMPLE`/`CONVERT_VALUE`), `match` statement compiled patterns, `try/except*`.
- Quantifying costs: compare variants (`+=` vs `join`, local alias vs global lookup, dict literal vs `dict()`) by bytecode count **and** `pyperf` timing; understand why bytecode count ≠ time.
- Version differences: `CALL` vs `PRECALL`, `BINARY_SUBSCR`, `RESUME`, `CACHE` entries, super-instructions; consult `Python/bytecodes.c` DSL for authoritative semantics.
- Building a **mini stack-machine interpreter** for a tiny bytecode (arithmetic + jumps) in Python to internalise evaluation.
- Using bytecode for tooling: coverage (line events), decompilers (`uncompyle6`/`decompyle3`/`pycdc`) and why they lag new versions; obfuscation realities and security implications (source protection is weak).
- Writing `dis` assertions in tests (not recommended for production) vs using it as a teaching/analysis aid; avoiding relying on bytecode details across versions.
- Reading the bytecode of a framework function (e.g. a Flask view wrapper) and describing what it does without source.

### Common mistakes

- Treating bytecode as a stable API.
- Assuming fewer instructions always means faster.
- Reading unspecialised bytecode and concluding performance facts (use `adaptive=True`).

### Self-check

1. Disassemble a closure and explain `MAKE_CELL`/`LOAD_DEREF`.
2. Where did the old `SETUP_FINALLY` go, and what replaced it?
3. Write a 40-line stack-machine interpreter for `PUSH`, `ADD`, `MUL`, `JUMP_IF_ZERO`, `PRINT` and test it with loops.

---

## Lesson 03 — `03-frames-call-stack-and-the-evaluation-loop.md`

**Why it matters.** Tracebacks, recursion errors, generators/coroutines,
debuggers, profilers and "why does my stack overflow?" are all about frames.
This is also the runtime picture that completes Stage 0's "what happens when
a function executes".

### Basic — what to learn

- A **frame** (execution record) holds: code object, locals/fast-locals, value stack, instruction pointer, globals, builtins, back pointer.
- The **call stack** = chain of frames; a traceback is a list of (frame, line) pairs.
- `sys._getframe()`, `inspect.currentframe()`, `inspect.stack()`, `frame.f_back`, `f_lineno`, `f_locals`, `f_globals`, `f_code`.
- Recursion limit: `sys.getrecursionlimit()`/`setrecursionlimit()`; `RecursionError`; why Python doesn't do tail-call elimination (design choice: tracebacks).

```python
import sys
def show():
    f = sys._getframe(1)
    print(f.f_code.co_name, f.f_lineno, list(f.f_locals))
def outer(): x = 1; show()
outer()
```

### Intermediate — what to learn

- Since 3.11: frames live in a contiguous **data stack** and are only materialised as Python objects (`PyFrameObject`) on demand — faster calls, cheap frames.
- Python-to-Python calls do not recurse in C ("inlined calls" in the evaluation loop), so the C stack depth differs from Python depth; C-stack-limited cases (3.12 separate limits for C recursion).
- Evaluation loop: `_PyEval_EvalFrameDefault` fetch–decode–execute (computed gotos / tail-call interpreter option in 3.14), `RESUME`, eval breaker (checked for signals, GIL drop requests, async exceptions, GC).
- **Generators and coroutines**: frame suspended and kept alive between `next()`/`send()`; `gi_frame`, `gi_running`, `yield from` delegation, `StopIteration`, `close()` raising `GeneratorExit`.
- Exceptions: raising unwinds frames using exception tables; `traceback` objects (`tb_frame`, `tb_next`, `tb_lineno`); chaining (`__cause__`, `__context__`).
- Locals inside functions: "fast locals" array vs dict-based class/module scope; `locals()` semantics (PEP 667 in 3.13: `frame.f_locals` write-through proxy for optimised scopes).

```python
def gen():
    x = yield 1
    print("got", x)
    yield 2
g = gen(); next(g); g.send("hello")
print(g.gi_frame.f_lineno, g.gi_frame.f_locals)
```

### Advanced — what to learn

- Stack depth and `RecursionError`: the recursion limit counts Python frames; deep recursion on huge inputs → iterative algorithm or explicit stack; threading stack size (`threading.stack_size`), `ulimit -s`; stack overflow in C extensions / deep `repr`/`json`/`pickle` structures.
- Frame inspection costs & hazards: reference cycles via frames (`inspect.stack()` retaining locals → memory leaks), holding tracebacks keeps frames alive (`del tb`, `except ... as e` cleanup).
- Debugger mechanics: `sys.settrace` (line/call/return/exception events), `pdb` using `Bdb`, breakpoints via tracing or `sys.monitoring`; why tracing slows programs (links to lesson 10).
- Coroutine/async internals: `await` as delegation to `__await__`; event-loop scheduling is not in the interpreter; `asyncio` task steps = coroutine `send`; "coroutine was never awaited" warnings; call-stack capture for async (`asyncio.print_call_graph`, 3.14).
- Python 3.14: tail-calling interpreter build option (needs Clang 19+), `sys._is_interned`, and other low-level changes — read the notes.
- Inspecting a hung process: stacks of all threads (`faulthandler.dump_traceback`, `sys._current_frames()`), mapping frames to what is blocked (lesson 09).
- Exercise: implement a tiny debugger-like tool using `sys.settrace` that prints each line executed in a function with locals, and measure the slowdown.
- Exercise: write a decorator that detects excessive recursion depth and raises a domain-specific error with a compact stack summary.

### Common mistakes

- Setting a huge recursion limit instead of fixing the algorithm.
- Keeping frames/tracebacks around (memory leaks).
- Relying on `f_locals` writes (undefined for optimised scopes before 3.13).

### Self-check

1. Why doesn't CPython do tail-call optimisation?
2. What lives in a frame, and what stays alive when a generator is suspended?
3. Build the `settrace` line tracer and use it to explain why a loop is slow under a debugger.

---

## Lesson 04 — `04-import-system-finders-loaders-and-sys-modules.md`

**Why it matters.** Import problems are among the most common Python
failures: `ModuleNotFoundError`, circular imports, shadowed stdlib names,
slow startup, wrong package version, plugins not found. Understanding the
machinery makes them mechanical to diagnose.

### Basic — what to learn

- `import x` does: check `sys.modules` cache → find a **spec** → create module → execute module code once → bind name.
- `sys.path` composition: script dir (or `''`), `PYTHONPATH`, stdlib, `site-packages`, `.pth` files; `python -m site`, `python -c "import sys; print(sys.path)"`.
- Module attributes: `__name__`, `__file__`, `__spec__`, `__package__`, `__path__`, `__loader__`, `__cached__`.
- Packages: `__init__.py`, relative imports (`from . import x`), absolute imports, namespace packages (PEP 420).
- Circular imports: cause (partially initialised module in `sys.modules`) and fixes (restructure, import inside function, import module not names).

```python
import sys, importlib
import json
print(json.__spec__.origin, "json" in sys.modules)
importlib.reload(json)           # re-executes the module code (use with care)
```

### Intermediate — what to learn

- **Finders** (`sys.meta_path`): `BuiltinImporter`, `FrozenImporter`, `PathFinder`; **path entry finders** (`sys.path_hooks`, `FileFinder`); **loaders** (`SourceFileLoader`, `ExtensionFileLoader`, `SourcelessFileLoader`).
- `importlib.util.find_spec`, `module_from_spec`, `spec_from_file_location`; importing a module from an arbitrary path programmatically.
- `importlib.metadata` (distributions, entry points, versions) vs imports; `importlib.resources` for package data.
- Import-time costs and lazy imports: `python -X importtime`, deferring heavy imports, `importlib.util.LazyLoader`, module-level `__getattr__` (PEP 562); (PEP 810 explicit lazy imports is proposed—check status).
- Shadowing pitfalls: a local `random.py`/`json.py`/`types.py` hiding stdlib; `python -I` isolated mode (ignores env and user site/CWD); `-P`/`PYTHONSAFEPATH` (3.11+) to avoid putting the script dir first.
- Virtual environments: `pyvenv.cfg`, `site.py`, prefix vs base prefix, user site, `sys.prefix` (links to Module 1.6 and Stage 0 dev env).
- Editable installs (PEP 660) implemented via `.pth` or import hooks.

### Advanced — what to learn

- Writing an **import hook**: a `MetaPathFinder` + `Loader` that (a) logs imports, (b) loads modules from a dict/zip/database, (c) blocks forbidden imports in a sandbox policy, (d) transforms source (AST rewrite → compile) — as pytest does for assertion rewriting.
- Extension modules: shared libraries (`.so`/`.pyd`), `PyInit_` functions, ABI tags, `abi3`, multi-phase initialisation, per-interpreter state; why a C extension fails to import in a different Python (links to Module 1.18 lesson 02).
- Import locks and threads: per-module locks, deadlocks with circular imports across threads; `importlib` in free-threaded builds.
- Reproducible/hermetic imports: `-I`, `sys.dont_write_bytecode`, zipimport/`zipapp`, frozen apps (PyInstaller bootstrapping), `sys.meta_path` modifications by tools (coverage, pytest, `six`, `editables`).
- Security: import path hijacking (CWD/PYTHONPATH/`.pth`), typosquatted packages, plugin auto-loading; hardening via isolated mode, minimal `PYTHONPATH`, verified wheels.
- Debugging recipes: "why is this module being imported from there?" → `python -v`, `importlib.util.find_spec`, `module.__file__`, `pip show -f`; tracing imports with an audit hook (`sys.addaudithook` events `import`).
- Performance: `.pyc` hash-based invalidation, `compileall`, `PYTHONPYCACHEPREFIX`, `-X frozen_modules`, import time budgets for CLIs (links to Module 1.18 lesson 03).
- Experiment: build a mini plugin loader using `importlib` that imports modules from a folder at runtime, with allow-lists and error isolation.

### Common mistakes

- Naming your own file `email.py`, `json.py`, `test.py` etc.
- Running scripts such that `sys.path[0]` points to the wrong directory.
- Using `reload` for production hot-swap.

### Self-check

1. Trace what happens, step by step, on the second `import json` in the same process.
2. Why does a circular import often yield `ImportError: cannot import name`?
3. Implement a meta-path finder that logs every import with the file location and time taken.

---

## Lesson 05 — `05-memory-allocator-and-small-object-optimizations.md`

**Why it matters.** Python programs create enormous numbers of tiny
objects. How CPython allocates, reuses and frees them explains memory
overhead, RSS that never shrinks, why integers/strings behave oddly with
`is`, and what `__slots__`, NumPy and Arrow are really saving you.

### Basic — what to learn

- Everything is a heap object with a header: refcount + type pointer (+ GC header for containers); typical sizes (`sys.getsizeof(1)` = 28 on 64-bit CPython ≤3.11, 28/32 variants later; empty list/dict/tuple sizes).
- Small-integer cache (−5…256), string interning, singleton `None/True/False`, empty tuple; why `a is b` is not equality and when "identity surprises" occur.
- `id()` is the object's address in CPython; `is` for singletons only.
- Memory returned to OS? Not always.

```python
a, b = 256, 256
c, d = 257, 257
print(a is b)                  # True (cached)
print(c is d)                  # implementation detail! (True within one code object, but don't rely on it)
import sys
print(sys.getsizeof([]), sys.getsizeof([1,2,3]), sys.getsizeof({}), sys.getsizeof(""))
```

### Intermediate — what to learn

- The three allocator layers: `PyMem_Raw*` (OS `malloc`), `PyMem_*` (Python memory), `PyObject_*` (object allocator → **pymalloc** for ≤512 bytes).
- **pymalloc**: arenas (1 MiB in 3.10+, mmap'd) → pools (16 KiB; 4 KiB earlier) → fixed-size blocks per size class (multiples of 16 bytes); free lists, why fragmentation prevents arenas from being released.
- Growth strategies: list over-allocation (amortised O(1) `append`), dict resizing and compact dicts/key-sharing dictionaries (PEP 412), string representation (compact ASCII / UCS-1/2/4, PEP 393), tuple free lists.
- Observing: `sys._debugmallocstats()`, `PYTHONMALLOC=debug|malloc|pymalloc`, `tracemalloc`, `memray --native` (Module 1.17).
- Why `__slots__`, tuples of floats vs `array('d')` vs NumPy arrays differ by 5–10× in memory (Module 1.11 lesson 07).
- Immortal objects (PEP 683, 3.12): refcount frozen for `None`, small ints, interned strings → fewer writes → better copy-on-write after `fork`.

### Advanced — what to learn

- Per-object overhead arithmetic: compute the bytes for a list of 1M ints, a list of 1M floats, a dict of 1M str→int; compare with `array`, NumPy, Arrow, and a `struct`-packed `bytes`; validate by measurement.
- Interaction with the C allocator: glibc `malloc` arenas/`M_ARENA_MAX`, `malloc_trim`, `jemalloc`/`mimalloc` (CPython 3.13+ builds can use mimalloc — required for the free-threaded build); effect on RSS and fragmentation; `LD_PRELOAD` experiments.
- Free-threaded build: mimalloc-based object allocation, biased/deferred reference counting, per-thread heaps (awareness; lesson 06).
- GC interplay: GC header cost for containers, untracking of tuples/dicts containing only atomic values, **why millions of small dicts hurt** (memory and GC traversal) → dataclasses with slots, structured arrays, columnar layouts.
- Large allocations: > 512 B go to system `malloc`/`mmap`; list resizing copy costs; `bytearray` and `io.BytesIO` growth; `memoryview` zero-copy.
- Containers and copy-on-write after `fork` (refcount writes dirty pages), `gc.freeze()` (Module 1.17 lesson 06), `multiprocessing` start methods and memory implications (3.14 default `forkserver` on Linux).
- Memory limits in containers: cgroup accounting, OOM kills, RSS vs working set vs page cache; setting `ulimit -v`; behaviour of `MemoryError`.
- Exercise: write a script that creates 1M tiny objects in several representations and prints a memory table (bytes/object) with `tracemalloc`, then explain every ratio.
- Exercise: demonstrate that freeing a large fraction of objects does not shrink RSS due to arena fragmentation, then show mitigation (process recycling / chunking).

### Common mistakes

- Using `is` for numeric/string equality.
- Assuming `del` returns memory to the OS.
- Ignoring per-object overhead in design (millions of dict-based records).

### Self-check

1. Why does `sys.getsizeof([1,2,3])` not equal `3 × sizeof(int)`?
2. What are arenas, pools and blocks and how do they cause fragmentation?
3. Reproduce a "memory never shrinks" case and remove it by changing the data representation.

---

## Lesson 06 — `06-gil-internals-and-subinterpreters.md`

**Why it matters.** "Python can't do parallelism because of the GIL" is
half-true and rapidly outdated. You need the precise picture to choose
between threads, processes, asyncio, subinterpreters and the free-threaded
build — and to write thread-safe code in all of them.

### Basic — what to learn

- What the **GIL** (global interpreter lock) is: a mutex so only one thread executes Python bytecode at a time in a given interpreter; protects interpreter state and reference counts.
- Consequences: CPU-bound threads don't run Python code in parallel; I/O-bound threads work well (GIL released during blocking I/O); many C extensions (NumPy, hashing, compression) release it for heavy work.
- Switching: the interpreter asks the running thread to release the GIL after a time slice (`sys.getswitchinterval()`, default 5 ms) — checked in the eval-breaker.
- Quick experiment: CPU-bound loop in 1 vs 4 threads vs 4 processes; I/O-bound with `sleep`/network.

```python
import threading, time
def burn(n=10_000_000):
    while n: n -= 1
t = time.perf_counter()
ts = [threading.Thread(target=burn) for _ in range(4)]
[x.start() for x in ts]; [x.join() for x in ts]
print("4 threads:", round(time.perf_counter() - t, 2))
```

### Intermediate — what to learn

- GIL does **not** make your code thread-safe: compound operations (`x += 1`, check-then-act, `list` iteration while mutating) can race; atomic-looking built-in operations (`list.append`, `dict[k] = v`) are safe individually but not as sequences; use `threading.Lock`, `queue.Queue`, `concurrent.futures`.
- The GIL and I/O: released around blocking syscalls; `time.sleep`; `socket` operations; file I/O; `subprocess`.
- C extensions: `Py_BEGIN_ALLOW_THREADS`; NumPy releases the GIL in many ufuncs; pure-Python code never does.
- Convoy effect and priority issues (old GIL vs new GIL since 3.2), contention measurement (`py-spy --gil`, Module 1.17 lesson 02).
- Alternatives for parallelism: `multiprocessing` (process pools, `spawn`/`fork`/`forkserver`, shared memory), `concurrent.futures.ProcessPoolExecutor`, native libraries, distributed frameworks (Stage 2: Dask/Ray/Spark).
- **Subinterpreters** (PEP 554/684/734): multiple interpreters in one process; since 3.12 each can have its **own GIL** (C-API), and 3.14 exposes `concurrent.interpreters` / `InterpreterPoolExecutor`; isolation (no shared objects), communicate via queues/channels, copying/shared-memory buffers; extension-module compatibility requirements (multi-phase init).

### Advanced — what to learn

- **Free-threaded CPython** (PEP 703): build `python3.13t`/`3.14t`; `sys._is_gil_enabled()`, `PYTHON_GIL=0|1`; how it works (biased + deferred reference counting, per-object locks / critical sections, mimalloc, immortalisation, specialisation constraints); single-thread overhead (smaller in 3.14), ecosystem readiness (check wheels `cp314t`), thread-safety obligations on C extensions (`Py_mod_gil`).
- Data races become *visible*: previously "accidentally safe" patterns may fail; need explicit locks/atomic structures; Python-level guarantees (per-container locks make `list`/`dict` operations individually safe, not compound ones).
- Choosing a model — decision table: I/O-bound many connections → `asyncio`; blocking libraries → threads; CPU-bound pure Python → processes or free-threaded; numeric → vectorise (NumPy releases GIL); isolation needed → subinterpreters/processes; distributed → Stage 2 tools.
- Measuring properly: pin cores, warm up, vary thread counts, compare `3.13` vs `3.13t` vs `3.14t`; watch memory (per-thread caches) and lock contention; use `py-spy`/`perf`.
- Python-level concurrency primitives: `Lock`, `RLock`, `Condition`, `Semaphore`, `Event`, `Barrier`, `queue`, atomic `itertools.count`; deadlock/livelock patterns; lock ordering; thread-local vs `contextvars`.
- Subinterpreter experiments (3.14): run CPU-bound tasks in an `InterpreterPoolExecutor`; measure vs processes (startup, memory, data transfer).
- Signal handling and the main thread; daemon threads at shutdown; `fork` in multi-threaded programs (deprecated in 3.12+ with warnings) — prefer `spawn`/`forkserver`.
- Writing a thread-safety audit checklist for your own library: global state, caches, singletons, lazy initialisation, C extensions, `__del__`.
- Case study: reproduce a classic race (shared counter) and fix it with a lock, an atomic queue-based design, and per-thread accumulation + merge.

### Common mistakes

- Using threads for CPU-bound pure Python and expecting a speed-up.
- Assuming the GIL makes `x += 1` atomic.
- Calling `fork` from threaded programs.

### Self-check

1. Why do I/O-bound threads benefit despite the GIL?
2. What changes in a free-threaded build, and what does it *not* fix?
3. Benchmark one CPU-bound task using threads, processes, and (if available) a free-threaded build or interpreter pool, and explain the numbers.

---

## Lesson 07 — `07-specializing-interpreter-and-jit.md`

**Why it matters.** Python got significantly faster in 3.11+ without code
changes. Understanding the adaptive interpreter and the experimental JIT
helps you write code that benefits, interpret benchmarks, and decide what to
upgrade or enable.

### Basic — what to learn

- The "Faster CPython" project: goals, results (≈25 % average speed-up 3.10 → 3.11, further gains in 3.12–3.14).
- The **specialising adaptive interpreter** (PEP 659): bytecode instructions start generic, observe operand types, then rewrite themselves to specialised variants (`LOAD_ATTR_INSTANCE_VALUE`, `BINARY_OP_ADD_INT`, `CALL_PY_EXACT_ARGS`, …) guarded by cheap checks; they de-specialise on guard failure.
- See it: `dis.dis(func, adaptive=True)` after warm-up (call it ~hundreds of times).

```python
import dis
def f(a, b): return a + b
for _ in range(1000): f(1, 2)
dis.dis(f, adaptive=True)        # BINARY_OP_ADD_INT after warm-up
```

### Intermediate — what to learn

- **Inline caches** in bytecode (the `CACHE` entries) hold type versions, dict key versions, function versions; **type version tags** make attribute lookups cacheable; mutating classes at runtime invalidates caches.
- What helps: stable types in hot loops, monomorphic call sites, instance attributes created in `__init__` in the same order (shared keys/inline values), avoiding `__dict__` fiddling and dynamic class changes, using local variables, built-ins.
- What hurts: polymorphic/megamorphic call sites, frequently changing types, `sys.settrace` / profilers (disable specialisation or slow it), `exec`-heavy code, huge functions.
- Warm-up effects in benchmarks (Module 1.17 lesson 03): first iterations are slower; microbenchmarks must account for specialisation.
- Other recent improvements: zero-cost exceptions, cheaper frames/calls, inlined comprehensions (PEP 709), `LOAD_FAST_LOAD_FAST` superinstructions, immortal objects, faster `str`/`dict` internals.
- Reading the "Faster CPython" ideas repository and release notes to follow progress.

### Advanced — what to learn

- **The experimental JIT (3.13+)**: build-time option `--enable-experimental-jit`; runtime `PYTHON_JIT=1`; copy-and-patch design: "tier 1" specialised bytecode → "tier 2" micro-op (uop) traces optimised → machine code templates stitched at runtime (LLVM-generated stencils); current state: modest/no speed-ups in many workloads, evolving fast (3.14/3.15 notes).
- Why a JIT in CPython is hard: C-API compatibility, dynamic semantics, startup time and memory cost, maintainability; comparison with PyPy's tracing JIT, V8/HotSpot tiered compilers, Numba (type-specialised, numeric subset), Cython (AOT).
- Tail-calling interpreter (3.14 opt-in with clang ≥ 19) giving ~few-% to 10 % gains in some builds; PGO/LTO build flags and why distributions matter (`python-build-standalone`, `uv` Python builds are optimised).
- Experiments: run a benchmark suite (`pyperformance`) or your workload on 3.10 vs 3.12 vs 3.14, with and without JIT, and on a free-threaded build; report speed-ups with confidence intervals and the CPU/OS.
- Observability of the tiers: environment/debug flags, `-X`/`PYTHON_*` variables, `sys._jit` introspection APIs (check your version), `perf` support for Python frames (`-X perf`, `PYTHONPERFSUPPORT`, 3.12+) and `py-spy --native`.
- Writing "JIT-friendly"/"specialisation-friendly" code without contortions: clear, type-stable, monomorphic where it matters; **don't** write code for the JIT before profiling.
- Where Python-level wins still dominate: algorithms, data layout, vectorisation, native extensions (Module 1.17) — interpreter speed-ups are multiplicative, not a replacement.
- Risk management: enabling experimental features in production — staged rollout, canaries, fallbacks, benchmarks on real workloads; keep a no-JIT flag.
- Future landscape (awareness): sub-interpreters, free-threading + JIT interplay, `mypyc` compiled modules, Mojo, Codon, Cinder, Pyston — what problems each addresses.

### Common mistakes

- Benchmarking without warm-up.
- Assuming the JIT makes numerical Python competitive with C.
- Enabling experimental flags in production without measurement.

### Self-check

1. What does "specialising" mean and what is a guard?
2. Show instruction specialisation using `dis(..., adaptive=True)` and then provoke de-specialisation by changing argument types.
3. Benchmark one CPU-bound pure-Python workload across two Python versions and (if possible) JIT on/off, and write a three-paragraph conclusion.

---

## Lesson 08 — `08-sys-os-and-runtime-introspection.md`

**Why it matters.** Production issues need answers to "which Python is
this, with what flags, from which path, with which environment, on which OS,
with how many CPUs, which limits?" The `sys`, `os`, `platform`, `sysconfig`
and related modules give precise, scriptable answers.

### Basic — what to learn

- `sys`: `sys.version`, `sys.version_info`, `sys.executable`, `sys.platform`, `sys.argv`, `sys.path`, `sys.modules`, `sys.stdin/stdout/stderr`, `sys.exit`, `sys.flags`, `sys.getsizeof`, `sys.byteorder`, `sys.maxsize`.
- `os`: `os.environ`, `os.getcwd/chdir`, `os.listdir/scandir/walk`, `os.getpid/getppid`, `os.cpu_count`, `os.process_cpu_count` (3.13), `os.urandom`, `os.name`, `os.cpu_count()` vs container CPU limits.
- `platform`: `platform.platform()`, `python_implementation()`, `machine()`; `sysconfig.get_config_vars()`.
- Build a **"doctor" report**: interpreter, venv, path, env vars (redacted), platform, installed packages (`importlib.metadata`), locale/encoding (`sys.getfilesystemencoding()`, `locale.getpreferredencoding()`), timezone.

```python
import sys, platform, os, sysconfig
print(sys.version.split()[0], sys.executable)
print(platform.platform(), os.cpu_count(), sys.flags.dev_mode)
print(sysconfig.get_config_var("Py_GIL_DISABLED"))
```

### Intermediate — what to learn

- Interpreter modes and flags: `-I` isolated, `-S` no site, `-E` ignore env, `-O/-OO`, `-X dev`, `-X utf8`, `-X importtime`, `-X faulthandler`, `-W`; `PYTHON*` environment variables (`PYTHONPATH`, `PYTHONHASHSEED`, `PYTHONUNBUFFERED`, `PYTHONDONTWRITEBYTECODE`, `PYTHONUTF8`, `PYTHONMALLOC`, `PYTHON_GIL`).
- `sys.stdout` buffering, `flush`, line buffering when attached to a TTY vs pipe (why logs appear late in containers → `-u`/`PYTHONUNBUFFERED`).
- Process and resource limits: `resource.getrlimit/setrlimit`, `os.sched_getaffinity` (true usable CPUs on Linux), cgroup limits (`/sys/fs/cgroup`), `os.getloadavg`, `shutil.disk_usage`.
- Signals: `signal.signal`, `SIGINT/SIGTERM` handling for graceful shutdown, `signal.alarm`, only in main thread; `atexit`; `sys.excepthook`, `threading.excepthook`, `sys.unraisablehook`.
- Exit semantics: `sys.exit()` raising `SystemExit`, `os._exit`, finalisation order and daemon threads, exit codes (Module 1.5 lesson 07).
- `sys.modules` manipulation (mocks, lazy modules) and `sys.getrefcount`, `sys.intern`, `sys.getswitchinterval`, `sys.getrecursionlimit`.
- Environment introspection safety: don't dump secrets; redact tokens/URLs with credentials.

### Advanced — what to learn

- **Audit hooks and runtime auditing**: `sys.addaudithook` events (`open`, `exec`, `import`, `socket.connect`, `subprocess.Popen`, `os.system`); building a policy logger or restrictive hook; limitations (not a sandbox; hooks can't be removed but can be bypassed in C).
- `sys.setprofile`/`settrace` vs `sys.monitoring` (lesson 10); `sys._current_frames()` and `sys._current_exceptions()` for live diagnostics (thread dumps).
- `faulthandler.enable()`, `dump_traceback_later`, register for signals (`SIGUSR1`) to dump stacks of a live program; `PYTHONFAULTHANDLER=1`.
- `gc` and `tracemalloc` hooks for runtime stats; exporting runtime metrics (GC counts, thread count, open fds via `/proc/self/fd`, RSS via `psutil`/`resource`) to monitoring systems.
- Container-aware sizing: cgroup v1/v2 CPU quotas (`os.process_cpu_count`, `os.sched_getaffinity`, `cpu.max`), memory limits, how thread/process pool defaults go wrong in Kubernetes.
- Cross-platform differences: Windows (`os.name == "nt"`, console encoding, `signal` limits, `fork` absent), macOS (`spawn` default, code signing), Linux distros (musl vs glibc), WSL2 quirks.
- Embedding and bootstrapping awareness: `python -c`, `python -m`, `runpy`, `site`/`sitecustomize`/`usercustomize`, `.pth` files (security-sensitive), `PYTHONSTARTUP`, `sys.orig_argv`.
- Build a **runtime diagnostics endpoint/CLI** (`python -m yourpkg doctor`) producing JSON with versions, limits, flags, thread stacks, GC stats, open files — redacting secrets — and test it.
- Security perspective: environment-driven behaviour (`PYTHONPATH`, `.pth`, `sitecustomize`) as persistence/hijack vectors; harden with `-I` and read-only site-packages in containers.

### Common mistakes

- Using `os.cpu_count()` as the number of usable CPUs inside containers.
- Logs missing at crash because stdout was buffered.
- Printing the whole environment in bug reports (leaks secrets).

### Self-check

1. How do you reliably find usable CPUs in a Kubernetes pod from Python?
2. Why do prints from a containerised Python job show up late, and how do you fix it?
3. Implement `doctor` with redaction and a unit test that asserts no secret-like values appear.

---

## Lesson 09 — `09-post-mortem-and-remote-attach-debugging.md`

**Why it matters.** Many serious bugs happen in production, on someone
else's machine, at 3 a.m., in a process you can't restart. Post-mortem
debugging and safe attach techniques let you diagnose crashes, hangs and
memory growth with evidence rather than guesses. Module 1.7 covered
`pdb` basics, breakpoints and tracebacks; this lesson goes further.

### Basic — what to learn

- Post-mortem with `pdb`: `python -m pdb script.py`; `pdb.pm()` after an uncaught exception in an interactive session; `pdb.post_mortem(tb)`; `breakpoint()` and `PYTHONBREAKPOINT`.
- Useful `pdb` commands: `w`/`bt`, `u`/`d`, `l`, `ll`, `p`, `pp`, `args`, `interact`, `!stmt`, `until`, `return`, conditional breakpoints (`b file:line, cond`), `tbreak`, `commands`.
- `sys.excepthook` for crash handling; `traceback` module to format and log; `logging.exception`.
- `faulthandler` for hard crashes (segfaults in C extensions, deadlocks): `python -X faulthandler`, `faulthandler.dump_traceback_later(30)`.

```python
import sys, traceback, pdb
def hook(exc_type, exc, tb):
    traceback.print_exception(exc_type, exc, tb)
    if sys.stdin.isatty():
        pdb.post_mortem(tb)
sys.excepthook = hook
```

### Intermediate — what to learn

- Debugging in IDEs (VS Code `debugpy`), remote debugging through `debugpy --listen` and port forwarding/SSH tunnels (Stage 2 Linux/SSH content), attach in containers; security of exposed debug ports (never open to the internet).
- Capturing state for later: dumping locals on exception (`traceback.TracebackException(capture_locals=True)`), structured error reports (Sentry-style), core dumps (`ulimit -c`, `coredumpctl`), `gdb` with `python3-dbg`/`py-bt` helpers.
- Hang diagnosis: `py-spy dump`, `faulthandler` signal registration (`faulthandler.register(signal.SIGUSR1)`), `sys._current_frames()`; recognise deadlock patterns (two threads each holding a lock waiting on the other).
- Segfault triage: `faulthandler` output pointing at a C extension; run with `PYTHONMALLOC=debug`, `python -X dev`, sanitizer builds; bisect dependency versions; minimal reproduction (Module 1.7 lesson 06).
- `pytest --pdb`, `--trace`, `-x --lf`; `pytest --pdbcls=IPython.terminal.debugger:TerminalPdb`; debugging flaky tests (Module 1.16 lesson 05).
- Debugging asyncio: `PYTHONASYNCIODEBUG=1`, `asyncio.run(debug=True)`, slow-callback warnings, task dumps (`asyncio.all_tasks()`, 3.14 `asyncio` introspection tools: `python -m asyncio ps PID` / `pstree`).

### Advanced — what to learn

- **Safe external debugger attach (PEP 768, Python 3.14)**: `sys.remote_exec(pid, script)` and `python -m pdb -p PID` to attach `pdb` to a running process without restart; how it works (the interpreter checks for a pending script at a safe point), permissions (`ptrace`/same user), the `PYTHON_DISABLE_REMOTE_DEBUG` / `-X disable-remote-debug` switch and security implications; compare to older hacks (`pyrasite`, `gdb` injection, `manhole`).
- Building a **debug backdoor safely**: signal-triggered stack dump / thread dump / heap summary endpoints; authentication, local-only binding, feature flags, audit logs.
- Live diagnostics sequence for "production process stuck at 100 % CPU": `top -H` → thread id → `py-spy dump` → `perf top`/`py-spy --native` → `gdb` backtrace → decide mitigation (restart, config change) while preserving evidence (dump stacks, `gcore`, logs, metrics) before killing.
- Memory incident: capture `tracemalloc`/`memray attach`/`objgraph` snapshots, `gc.get_objects()` type histograms, heap dumps (`guppy3`/`pympler`) and compare over time (Module 1.17).
- Record-and-replay debugging (`rr` for native code; awareness only) and deterministic reproduction by logging inputs and seeds.
- Exception forensics: reading chained tracebacks and exception groups, `__traceback__` frame locals, `sys.last_exc` (3.12), `traceback` in logs with `stack_info=True`, source-context rendering.
- Postmortem culture: incident timeline, evidence preserved, hypothesis log, root cause, corrective actions, regression test, runbook update (links to Module 1.10 lesson 08).
- Exercise: given a provided script with (a) a deadlock, (b) a C-extension segfault simulated via `ctypes`, (c) a memory leak, (d) a CPU spin — diagnose each using only the tools in this lesson and write the postmortem.
- Exercise: on Python 3.14 attach `pdb` to a running worker, inspect a variable, patch a flag, and detach; document the permission model.

### Common mistakes

- Killing the process before collecting stacks and heap evidence.
- Exposing a debug port without authentication.
- Debugging with print statements in production without logging discipline.

### Self-check

1. How do you diagnose a Python process stuck with no CPU use?
2. What does PEP 768 add and what are the security trade-offs?
3. Write the runbook for "service hangs under load" including exact commands and what evidence to preserve.

---

## Lesson 10 — `10-sys-monitoring-and-tracing-hooks.md`

**Why it matters.** Debuggers, coverage tools, profilers, tracers and
security monitors are built on hooks into the interpreter. `sys.settrace`
was slow and single-client; `sys.monitoring` (PEP 669, Python 3.12+) is a
low-overhead event system shared by tools. Knowing it lets you build your
own tools and understand why debuggers and coverage behave as they do.

### Basic — what to learn

- Legacy tools: `sys.settrace(fn)` (events `call`, `line`, `return`, `exception`, `opcode`), `sys.setprofile(fn)` (`call`/`return`/`c_call`/`c_return`/`c_exception`), `threading.settrace`.
- Trace function protocol: return the local trace function; set `frame.f_trace`; `frame.f_trace_lines`/`f_trace_opcodes`.
- Minimal tracer printing lines executed:

```python
import sys

def tracer(frame, event, arg):
    if event == "line":
        print(f"{frame.f_code.co_name}:{frame.f_lineno}")
    return tracer

def work():
    a = 1
    b = a + 1
    return b

sys.settrace(tracer); work(); sys.settrace(None)
```
- Overhead: tracing every line makes code 10–100× slower; only one tracer at a time.

### Intermediate — what to learn

- **`sys.monitoring` (3.12+)**: tool IDs (`DEBUGGER_ID`, `COVERAGE_ID`, `PROFILER_ID`, `OPTIMIZER_ID`), `use_tool_id`, `register_callback(tool, event, func)`, `set_events(tool, events)`, local events per code object (`set_local_events`), returning `DISABLE` to turn off an event at a location (zero further cost).
- Events: `PY_START`, `PY_RESUME`, `PY_RETURN`, `PY_YIELD`, `PY_THROW`, `PY_UNWIND`, `CALL`, `C_RETURN`, `RAISE`, `EXCEPTION_HANDLED`, `LINE`, `INSTRUCTION`, `JUMP`, `BRANCH` (3.12-3.13; `BRANCH_LEFT/RIGHT` in 3.14), `STOP_ITERATION`, `C_RAISE`.
- Why coverage got faster: `COVERAGE_CORE=sysmon` uses line/branch events that disable themselves after first hit (Module 1.16 lesson 01).
- Build a mini coverage tool and a call-counter profiler:

```python
import sys
mon = sys.monitoring
TOOL = mon.PROFILER_ID
mon.use_tool_id(TOOL, "mini-prof")
counts = {}

def on_start(code, offset):
    counts[code.co_qualname] = counts.get(code.co_qualname, 0) + 1

mon.register_callback(TOOL, mon.events.PY_START, on_start)
mon.set_events(TOOL, mon.events.PY_START)
run_workload()
mon.set_events(TOOL, 0); mon.free_tool_id(TOOL)
print(sorted(counts.items(), key=lambda kv: -kv[1])[:5])
```
- Comparing `settrace` vs `monitoring`: overhead, multiple tools, per-code-object granularity, `DISABLE`.

### Advanced — what to learn

- Tool design: choosing events minimally; instrumentation scope (only user code, skip stdlib/site-packages); thread-safety of callbacks; avoiding recursion (callbacks being traced); handling generators/coroutines (`PY_YIELD`/`PY_RESUME`); exceptions in callbacks.
- Building real tools: line/branch coverage with `DISABLE`, a time-per-function tracer (use `time.perf_counter_ns`, exclude callback time), an allocation-site correlator, a "who calls this deprecated function?" finder, a **security audit tracer** for risky calls (`CALL` event to `eval`, `os.system`, `subprocess`) with allow-lists — and its limits (not a sandbox).
- Debugger internals: breakpoints implemented with `LINE` events + `DISABLE`, step over/into via `PY_START/PY_RETURN`; `pdb` in 3.14 can use a `sys.monitoring` backend (check the `backend` option of `pdb`), while IDE debuggers such as `debugpy` have their own tracing strategies — read their sources.
- Interaction with the specialising interpreter/JIT: instrumentation rewrites bytecode (instrumented instructions), may de-optimise; measure overhead on your workload; JIT/tier-2 disabled when instrumented.
- OpenTelemetry/APM auto-instrumentation vs monitoring-based tracing: monkey-patching vs interpreter events; overhead and coverage trade-offs.
- `sys.audit`/`addaudithook` combined with `monitoring` for observability + policy; `faulthandler`, `sys.unraisablehook` for last-resort events.
- Testing tooling code: golden event sequences for small functions, property tests for coverage correctness (executed lines ⊆ lines with code), performance tests that bound overhead.
- Reading the sources: `Lib/bdb.py`, `Lib/pdb.py`, `Lib/trace.py`, `coverage.py` `sysmon` tracer, `Python/instrumentation.c`; summarise one in a design note.
- Exercise: implement `mini-trace`: CLI that runs a script and prints a call tree with timings and line hit counts, using `sys.monitoring`, with `--only-package` filter and overhead report vs `settrace`.

### Common mistakes

- Leaving a tracer installed (global slowdown).
- Tracing inside the tracer (infinite recursion).
- Expecting hook APIs to be a security sandbox.

### Self-check

1. Why can `sys.monitoring` disable events per location and why does that make coverage faster?
2. What are tool IDs and why do they let a debugger and a profiler coexist?
3. Build the mini call-counter profiler and compare overhead against `cProfile` on the same workload.

---

## 4. Practice questions (`practice-questions.md`)

About **35 questions**:

| Phase | Question types |
| --- | --- |
| A | Interpret `dis` output; predict `UnboundLocalError`; explain `.pyc`; frame/recursion puzzles |
| B | Trace imports and shadowing bugs; compute per-object memory; explain "memory not returned" |
| C | GIL/threads predictions and benchmarks; spot-the-race; specialisation/JIT reasoning |
| D | Build a `doctor` report; postmortem scenarios; design an event-based tool |

Include 6 **"what happens?"** traces (second import, generator suspension, closure capture, `fork` after threads, `sys.exit` in a thread, exception in a `__del__`).

---

## 5. Module mini-project

**Build `pyx-inspector`**, a diagnostics toolkit that exposes how the runtime behaves:

1. `pyx pipeline file.py`: prints tokens, AST, symbol table, bytecode and `co_*` summary for a chosen function.
2. `pyx imports script.py`: runs a script with a meta-path hook and prints an import tree with timings and file origins; flags shadowed stdlib names.
3. `pyx memory`: experiments on per-object sizes and arena behaviour with a table of representations (dict objects, dataclass, slots, tuple, array, NumPy).
4. `pyx threads`: CPU-bound vs I/O-bound benchmarks across threads, processes and (if available) interpreter pools / free-threaded builds, with a written analysis.
5. `pyx doctor`: JSON runtime report (versions, flags, limits, cgroup CPUs/memory, GC stats, thread stacks) with secret redaction.
6. `pyx trace`: `sys.monitoring`-based call-count/time/line-hit profiler with filters and overhead measurement.
7. `INTERNALS.md`: for each command, the finding(s) you learned, linked to CPython source locations (file and function) you read.

Acceptance: ≥ 85 % coverage on non-experimental code, works on Python 3.12–3.14 with graceful degradation for missing features, documented caveats for version-specific behaviour, all measurements reproducible by script.

---

## 6. Completion checklist

- [ ] I can describe each stage from source to execution and show it with stdlib tools.
- [ ] I can read bytecode, including closures, generators and `with`, and explain the stack machine.
- [ ] I can explain frames, recursion limits, generators' suspended state and traceback construction.
- [ ] I can trace the import system and write an import hook.
- [ ] I can explain object memory layout, pymalloc, interning, immortal objects and why RSS doesn't shrink.
- [ ] I can explain the GIL, subinterpreters and free-threaded Python, and choose a concurrency model with evidence.
- [ ] I can explain the specialising interpreter and the experimental JIT and benchmark them fairly.
- [ ] I can introspect and report runtime state safely, including container limits.
- [ ] I can run post-mortem and safe attach debugging and write a postmortem.
- [ ] I can build a tool on `sys.monitoring`.
- [ ] I completed the `pyx-inspector` mini-project.

**Next:** Module 1.20 — Design Patterns and Library API Design.
