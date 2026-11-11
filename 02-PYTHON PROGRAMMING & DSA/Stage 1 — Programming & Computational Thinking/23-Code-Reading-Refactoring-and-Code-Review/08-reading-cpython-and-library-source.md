# Reading CPython and Library Source

> **Stage 1 — Programming & Computational Thinking**  
> **Module 1.23 — Code Reading, Refactoring and Code Review**  
> **Lesson 08 of 08**  
> **Audience:** Python learners progressing to advanced engineers, with backend and data-platform examples.  
> **Baseline:** Python 3.12+ is a useful learning baseline, but implementation details must be checked against the exact interpreter and dependency version under investigation.  
> **Principle:** Start with a question, follow the implementation, run an experiment, and verify the conclusion against source and tests.

---

## 1. Why read source code?

Documentation describes supported behavior and contracts. Source code helps explain *how* a particular version implements that behavior, why a surprising result occurs, and where an exception or performance cost originates. Tests show which cases the project deliberately protects. Design notes and commit history help explain why a design exists.

Reading source is not a contest to read the most files. It is a targeted investigation.

By the end of this lesson, you should be able to:

- Locate the source of standard-library and installed third-party modules.
- Distinguish public API documentation, type stubs, pure-Python implementations, extension modules, and interpreter internals.
- Use `help`, `inspect`, IDE navigation, `rg`, Git history, tests, and design documents effectively.
- Trace a small execution path from public API to implementation and tests.
- Navigate the major areas of the CPython repository without reading it linearly.
- Compare Python-level fallbacks with C accelerators when such a comparison is valid.
- Build a minimal experiment or benchmark that tests a source-based hypothesis.
- Investigate a dependency exception, performance question, or security concern using evidence.
- Produce three version-pinned source-reading reports with diagrams, experiments, references, and explicit design lessons.

## 2. A source-reading workflow

Use this loop for a small, concrete question.

1. **State the question.** Example: “Does `functools.lru_cache` hold references to arguments and return values, and when are entries evicted?”
2. **Pin the environment.** Record Python version, implementation, platform, package version, and relevant build/configuration details.
3. **Observe behavior first.** Write a tiny reproducer or failing test. Record expected and actual results.
4. **Find the public entry point.** Start from the API users call, not from a random internal function.
5. **Locate the implementation.** Check whether it is Python, C, Rust, generated code, a wrapper, or a combination.
6. **Trace only the relevant path.** Follow calls and state changes. Search for names of functions, fields, flags, and error messages.
7. **Read tests and comments.** Tests often define edge cases; comments and design docs explain constraints that are not obvious from the code.
8. **Check history when intent matters.** Inspect the commit, pull request, issue, design document, or postmortem associated with a change.
9. **Test the hypothesis.** Use a minimal experiment, debugger, targeted test, or benchmark. Change one variable at a time.
10. **Write the conclusion with boundaries.** Separate documented guarantees from implementation details that may change across versions.

A useful investigation note is short and reproducible:

```text
Question:
Environment:
Observed behavior:
Public entry point:
Implementation files/functions:
Relevant tests:
Experiment and result:
Conclusion:
Version-specific caveats:
Source links / commit:
```

### A source-location decision tree

- `inspect.getsource()` works and returns Python code: likely a Python-defined object, but confirm the file and version.
- `inspect.getsource()` raises `OSError` or `TypeError`: the object may be built-in, implemented in an extension, dynamically generated, or unavailable to `inspect`. Do not infer that source does not exist anywhere.
- IDE navigation lands in a `.pyi` file: you are probably viewing a type stub, not executable implementation.
- A module imports successfully but the implementation is in an extension (`.so`, `.pyd`, or another platform-specific suffix): inspect its Python wrapper, C/Rust source, tests, and build configuration.
- Runtime behavior differs from the file you found: verify the active interpreter, virtual environment, import path, installed distribution version, optional accelerator, and whether the source tree matches the running binary.

## 3. Locate the code actually running

### 3.1 Record the runtime

Run these commands in the same environment where the behavior occurs:

```bash
python -VV
python -c "import platform, sys; print(platform.python_implementation()); print(sys.executable); print(sys.path)"
python -c "import sysconfig; print(sysconfig.get_paths())"
```

For a third-party package:

```bash
python -c "import requests; print(requests.__file__)"
python -m pip show requests
```

Replace `requests` with the package under investigation. `module.__file__` often points to the imported file, but namespace packages and built-in/frozen modules can behave differently. `pip show` describes the installed distribution; it does not prove that the import resolves to that distribution if the environment has path shadowing.

For a particular object:

```python
import inspect
import functools

obj = functools.lru_cache
print("module:", obj.__module__)
print("source file:", inspect.getsourcefile(obj))
print("source lines:", inspect.getsourcelines(obj)[1])
print(inspect.getsource(obj))
```

`inspect.getsource()` and `inspect.getsourcelines()` are best-effort source retrieval for objects whose source is available. They can fail for built-ins, extension-defined objects, interactive definitions, generated functions, or stripped source distributions. Catch the exception only when a fallback is meaningful; do not suppress it and pretend the output is complete.

```python
import inspect
import math

for obj in (math.sqrt, len):
    try:
        print(obj, inspect.getsourcefile(obj))
        print(inspect.getsource(obj))
    except (OSError, TypeError) as exc:
        print(f"Source unavailable through inspect for {obj!r}: {exc}")
```

The expected interpretation is that built-in/extension objects generally do not provide ordinary Python source to `inspect`. Their implementation may be available in the matching CPython or third-party source repository.

| Tool | Use | Important limit |
|---|---|---|
| `help(obj)` | Public-facing docs and signatures | May show docs without implementation |
| `inspect.getsource(obj)` | Python source for a function/class/module when available | Not a universal decompiler |
| `inspect.getsourcefile(obj)` | Source file associated with a Python object | May return `None` or raise for some objects |
| `inspect.getsourcelines(obj)` | Source lines and starting line number | Line numbers are tied to the local version |
| `inspect.signature(obj)` | Callable signature when introspectable | Some built-ins need custom signature metadata |
| IDE “Go to definition” | Navigate from usage to declaration | Can resolve to a stub, generated file, or wrapper |
| `module.__file__` | Imported module path when defined | Not guaranteed for every module type |

### 3.2 Stubs are not implementations

Type stubs (usually `.pyi` files) describe names, signatures, overloads, and types to static analyzers. They may intentionally omit executable bodies. Typeshed is a major source of standard-library stubs. A stub is useful for answering “what interface is expected?” but generally not “what does this code execute?”

When IDE navigation opens a stub:

1. Note the public signature and overloads.
2. Find the runtime module path with `module.__file__` or `inspect`.
3. Locate the implementation and its tests.
4. Compare the contracts; do not assume the stub fully describes runtime edge cases.

### 3.3 Find definitions and call sites

From a repository root, use ripgrep (`rg`) if installed:

```bash
rg -n "def lru_cache|class .*Cache|_lru_cache_wrapper" Lib/
rg -n "lru_cache" Lib/test/
rg -n "getsourcefile|getsourcelines" Lib/inspect.py Lib/test/
```

In a third-party checkout, search the package directory and tests. If `rg` is unavailable, use `grep -R`, IDE search, or GitHub code search. Search for a specific symbol or error string; do not begin by dumping thousands of lines.

Use GitHub source links pinned to a tag or commit whenever the result will be shared. A link to `main` can change after you write your report. Git history commands from the previous lesson are useful here:

```bash
git log --oneline -- path/to/file.py
git blame -L 80,120 path/to/file.py
git log -S"symbol_name" --oneline -- path/to/file.py
# HEAD is an executable example; replace the path with a real repository path.
git show HEAD -- path/to/file.py
```

Use a verified commit SHA or ref when you need a particular historical revision. Avoid pasting angle-bracket placeholders such as `<commit>` directly into a shell command: the shell interprets `<` as input redirection.

## 4. Where Python and CPython source lives

The Python language specification and the CPython implementation are related but not identical. CPython is the reference implementation most users run, but another Python implementation may behave differently internally while satisfying the language-level contract.

In a CPython checkout, major areas include:

| Area | Typical purpose | Questions to ask |
|---|---|---|
| `Lib/` | Python-level standard library | What wrapper, validation, or algorithm is expressed in Python? |
| `Lib/test/` | Standard-library and runtime tests | What behavior and edge cases are protected? |
| `Objects/` | Core object types and operations | How are lists, dictionaries, strings, tuples, and other objects represented/implemented? |
| `Modules/` | Built-in and extension modules | How does an extension expose functionality to Python? |
| `Python/` | Interpreter implementation and runtime machinery | How is execution, evaluation, or runtime state managed? |
| `Include/` | Public/internal C headers and declarations | Which structures and APIs are declared, and which are private? |
| `InternalDocs/` | Design and implementation notes in current trees | What rationale or architecture helps explain the implementation? |
| `Tools/` | Developer utilities and analysis tools | Is there an existing tool for this investigation? |

Directory organization evolves. The authoritative path is the checkout/tag you are examining. Do not assume an old blog post's filename or function name matches the current branch.

### 4.1 Start with comments and design notes

For complex internals, read the overview comment near the top of the relevant file and any matching design note before tracing every branch. Search the tree:

```bash
rg -n "over-allocation|overallocate|compact dict|dictionary" Objects InternalDocs
rg -n "interpreter|frame|garbage collection|exception handling" InternalDocs Python
```

Some terms or documents may not exist in a particular release. If a search returns no result, inspect the directory listing and source tag rather than inventing a path.

### 4.2 C navigation: lists and dictionaries

For list representation and resizing, begin with `Objects/listobject.c`. In versions where they exist, useful search terms include `list_resize` and `list_append_impl`; confirm the exact names in your target tag rather than treating them as stable API. For dictionaries, search `Objects/dictobject.c` for resize, insertion, and lookup helpers (names such as `dictresize`, `insertdict`, or `lookdict` may vary by version). These are navigation targets, not promises that every symbol exists in every release. Read declarations and helpers together—an allocation decision may be delegated to a helper.

```bash
# Run from the root of the CPython checkout; inspect matches before assuming a path.
rg -n "list_resize|list_append_impl" Objects/listobject.c
rg -n "dictresize|insertdict|lookdict|resize" Objects/dictobject.c
rg -n "list_resize|dictresize" Objects Include Lib/test
```

For dictionaries, begin with `Objects/dictobject.c`. Read its introductory design comments and search for lookup, insertion, resizing, and key/value storage. A useful investigation separates:

- **Language-visible contract:** mapping operations, insertion order guarantees, exceptions, equality/hash behavior.
- **CPython implementation:** table layout, probing strategy, split/combined table details, resizing policy, cached hashes, and optimizations.
- **Performance hypothesis:** the particular operation and workload you measured.

Do not infer a permanent complexity guarantee from a particular implementation detail. Average-case complexity claims are not promises that every operation has the same cost for every input, nor do they describe adversarial hash behavior or memory pressure.

### 4.3 Interpreter and bytecode

For bytecode execution, inspect the interpreter implementation in the specific CPython release. Older releases commonly concentrate evaluator logic in `Python/ceval.c`; modern releases may distribute opcode definitions and execution logic across `Python/bytecodes.c`, generated handlers, and supporting metadata instead of one historical file. For example, CPython 3.13.5 has `Python/bytecodes.c`; verify the path in your pinned tag before citing it. The filename and organization are implementation details, not stable interfaces.

Useful commands:

```bash
python -c "import dis; dis.dis(lambda x: x + 1)"
python -c "import sys; print(sys.version); print(sys.implementation)"
rg -n "BINARY_OP|FOR_ITER|RESUME" Python Include Tools
```

The opcode names above are examples for some versions, not a stable cross-version list. Always inspect output from the target interpreter. Bytecode is an implementation detail and can change between releases; it is not a portable representation for application logic.

To understand a bytecode path, follow: source-level construct → compiler/bytecode generation → opcode definition or metadata → execution implementation → tests. Use `dis` to observe the bytecode produced by the running interpreter; use the matching source tag to explain it.

### 4.4 C extensions and accelerators

`Modules/` contains many built-in or extension modules; some Python APIs have a wrapper in `Lib/` and a faster implementation in C. Others are entirely implemented in C. An installed module can be a combination of both.

For JSON, the C accelerator has historically been in `Modules/_json.c`; confirm that file and its role in the version under review. For heap operations, `heapq.py` can expose Python implementations while optionally using `_heapq`. For `functools`, some cache machinery may be implemented by a C callable such as `_lru_cache_wrapper`; the Python wrapper and the C implementation need not have identical source-level structure.

A useful import/runtime check:

```python
import heapq
import sys

print("heapq file:", heapq.__file__)
print("_heapq loaded:", "_heapq" in sys.modules)
print("heapq.heappush:", heapq.heappush)
```

This tells you whether `_heapq` is loaded at the moment of inspection, not by itself which exact code path every call used. Inspect `heapq.py`, `_heapq`'s source in the matching checkout, and relevant tests to establish the dispatch.

### 4.5 Compare fallback and accelerator safely

Do not replace production modules in `sys.modules` or monkey-patch interpreter internals casually. For controlled comparisons, use a separate process or the test suite's supported helper when available. CPython's test suite has used `test.support.import_helper.import_fresh_module` to import modules with selected accelerators blocked, but this is test-support infrastructure and can change. Inspect the helper in the version you run before using it.

Comparison plan:

1. Pin CPython version and build.
2. Identify the Python implementation and accelerator.
3. Read dispatch logic to understand which implementation is selected.
4. Compare the same public inputs, including edge cases and exceptions.
5. Run existing tests against both implementations if the project supports it.
6. Benchmark only after confirming equivalent semantics and a representative workload.
7. Record that internal implementation selection may differ on other builds/platforms.

`python -X importtime -c "import heapq"` can help examine import costs, but import-time output is not a benchmark of `heappush` or `heappop`.

### 4.6 Navigation and call-graph tools

Use the lightest tool that answers the question; generated graphs are hypotheses to verify, not proof of runtime behavior.

| Tool | Useful role | Limit to remember |
|---|---|---|
| `rg --type py` / `grep` | Search Python source and call sites | Text matches do not establish dynamic dispatch or execution order |
| `ctags` / IDE navigation | Jump to definitions and references | May land on stubs, generated code, or wrappers |
| `pydeps` / `pyreverse` | Explore module/class dependency structure | Static imports miss some dynamic/plugin relationships and do not prove runtime call paths |
| `pycg` / `code2flow` | Build approximate call graphs from Python source | Dynamic dispatch, decorators, reflection, and native boundaries can make graphs incomplete |
| `sys.settrace` / `sys.monitoring` | Observe selected Python execution events | Instrumentation adds overhead; event coverage and APIs depend on Python version |
| `strace` (Linux) | Observe process system calls | Does not explain Python-level call relationships or native internal state |

For a useful call graph, start from one public API and cross-check candidate edges against source, tests, or a debugger trace. Record the tool version and configuration if the graph is part of a report.

## 5. Worked investigation: how `functools.lru_cache` evicts entries

This worked example demonstrates method, not a claim about every internal detail of every Python version. Re-run the commands against your installed interpreter and pin the matching CPython source before reporting implementation-specific conclusions.

### Question and hypothesis

**Question:** With `@lru_cache(maxsize=2)`, what happens when a third distinct key is used, and which previously used key remains cached?

**Hypothesis:** A bounded least-recently-used cache retains at most two entries and evicts the least recently used entry when it needs room. A cache hit changes recency.

The public contract is documented by `functools.lru_cache`; exact linked-list structures, sentinels, locking details, and optimization strategy are implementation details.

The conceptual path is:

```text
call cached function
       |
       v
construct cache key -----> key already present? ---- yes ----> return cached value
                                      |
                                      no
                                      v
                              call wrapped function
                                      |
                                      v
                             store/update cache entry
                                      |
                                      v
                         over capacity? evict LRU entry
```

This is a behavioral model, not a source-level call graph. Use the pinned implementation to determine the actual helper names and ordering.

### 5.1 Run a minimal experiment

```python
from functools import lru_cache

calls = []

@lru_cache(maxsize=2)
def calculate(value: int) -> int:
    calls.append(value)
    return value * 10

assert calculate(1) == 10       # compute 1
assert calculate(2) == 20       # compute 2
assert calculate(1) == 10       # hit: 1 becomes recently used
assert calculate(3) == 30       # third key; least-recently-used key is evicted
assert calculate(2) == 20       # 2 was evicted, so compute again

print("function calls:", calls)
print("cache info:", calculate.cache_info())
```

Expected interpretation: `calls` is `[1, 2, 3, 2]`; `cache_info()` reports 1 hit, 4 misses, `maxsize=2`, and `currsize=2`. These results follow from the experiment's call sequence and documented LRU behavior. If you change the call sequence, the expected counts change.

The documented cache contract also retains references to arguments and return values while entries remain cached. This separate experiment checks that behavior for ordinary weak-referenceable objects; it does not prove every object type or concurrency scenario:

```python
import gc
import weakref
from functools import lru_cache

class Key:
    pass

class Result:
    pass

@lru_cache(maxsize=2)
def build(key):
    return Result()

key = Key()
result = build(key)
key_ref = weakref.ref(key)
result_ref = weakref.ref(result)
del key, result
gc.collect()
assert key_ref() is not None       # cached key still holds a reference
assert result_ref() is not None    # cached value still holds a reference
build.cache_clear()
gc.collect()
assert key_ref() is None
assert result_ref() is None
```

Run this in a fresh process if you want to avoid unrelated references from an interactive session. If an assertion fails in a different runtime, investigate that environment rather than assuming the experiment is universal.

### 5.2 Find the active wrapper

```python
import functools
import inspect
import sys

print("Python:", sys.version)
print("Implementation:", sys.implementation)
print("functools source:", functools.__file__)
print("lru_cache source:", inspect.getsourcefile(functools.lru_cache))
print(inspect.getsource(functools.lru_cache))
```

The decorator factory is usually inspectable as Python source. The decorated function's wrapper may be a C implementation on CPython. Inspect it rather than assuming it is a Python function:

```python
import functools

@functools.lru_cache(maxsize=2)
def sample(x):
    return x

print(type(sample))
print(type(sample).__module__)
print(getattr(sample, "__wrapped__", None))
```

`__wrapped__` commonly points back to the original function and is useful for introspection, but it is not the cached wrapper's internal algorithm.

### 5.3 Trace implementation and tests

In a matching CPython checkout:

```bash
rg -n "def lru_cache|_lru_cache_wrapper" Lib/functools.py
rg -n "lru_cache|cache_info|cache_clear" Lib/test
```

Then:

1. Read the decorator's argument validation and wrapper construction.
2. Follow how `maxsize` and `typed` affect the wrapper.
3. Find the C implementation if the wrapper is delegated to `_lru_cache_wrapper`.
4. Read relevant tests for hits, misses, `cache_info`, `cache_clear`, keyword arguments, and edge cases.
5. Use `git log` or blame to find the commit/issue if a design choice needs historical explanation.

Do not copy line numbers from a web page or another Python release. Record the tag or commit and obtain line references from that exact checkout:

```bash
git rev-parse HEAD
git describe --tags --always
nl -ba Lib/functools.py | sed -n '1,220p'
```

The `sed` range is only an example navigation window; find the actual relevant lines in your checkout before citing them.

### 5.4 State a careful conclusion

A good conclusion separates evidence:

- **Observed:** the test sequence yields the stated call list and cache statistics on the recorded runtime.
- **Documented:** the bounded cache uses least-recently-used eviction semantics.
- **Implementation-specific:** the selected CPython build may use a C wrapper and particular internal data structures.
- **Not established:** the experiment does not prove memory usage under all workloads, thread-scheduling behavior, or identical internals across Python implementations.

This distinction is central to reliable source reading.

## 6. Investigating `dataclasses`, `heapq`, `bisect`, and other modules

Use the same question-first workflow for each module.

| Module | Good investigation question | Where to look first | Experiment or evidence |
|---|---|---|---|
| `dataclasses` | How is a generated `__init__` assembled, and how do defaults/factories differ? | `Lib/dataclasses.py`, tests, PEP 557 | Inspect `dataclasses.fields`, generated signature, and behavior of `default_factory` |
| `collections` | How is `namedtuple` constructed, or how does `OrderedDict` differ from `dict`? | `Lib/collections/`, tests, relevant docs | Inspect generated type, order behavior, and version contract |
| `heapq` | How do `heappush` and `heappop` preserve the heap invariant? | `Lib/heapq.py`, `_heapq` source, tests | Compare pop order and invariant checks on a small list |
| `bisect` | Which boundary does `bisect_left` return when equal values exist? | `Lib/bisect.py`, accelerator if present, tests | Try duplicates and check insertion position |
| `enum` | How are members created and aliases handled? | `Lib/enum.py`, tests, PEP/docs | Compare `__members__`, iteration, and aliases |
| `contextlib` | What does a generator-based context manager do on exception exit? | `Lib/contextlib.py`, tests, PEP 343 | Use a context manager that logs entry/exit and re-raises |
| `argparse` | How are parse errors and defaults handled? | `Lib/argparse.py`, tests | Test missing arguments and invalid choices |
| `logging` | How does logger hierarchy and propagation affect duplicate output? | `Lib/logging/`, tests, logging docs | Configure parent/child loggers in an isolated process |
| `pathlib` | Which operations are lexical versus filesystem operations? | `Lib/pathlib/`, tests | Compare path composition with existence/stat checks |
| `shutil` | Which fast-copy path is used, and what are the fallback semantics? | `Lib/shutil.py`, platform tests | Copy representative files; inspect platform branches |
| `subprocess` | How do `run`, `Popen`, `check`, and timeout behavior interact? | `Lib/subprocess.py`, tests | Use a tiny child process; never experiment with untrusted shell input |
| `typing` | Is a type construct runtime behavior, static metadata, or both? | `Lib/typing.py`, typing docs, typeshed | Compare annotations/introspection with static checker results |
| `json` | How are `NaN`, custom encoders, and decoding errors handled? | `Lib/json/`, `_json` accelerator, tests | Run a small input with explicit options and inspect the result |

A source-reading exercise should not stop at “I found a function.” Record the entry point, its helpers, the relevant test, and a reproducible observation.

### 6.1 Example: `dataclasses.default_factory`

Question: “Does a `default_factory` run once when the class is defined, or once for each instance?”

```python
from dataclasses import dataclass, field

@dataclass
class Batch:
    rows: list[int] = field(default_factory=list)

first = Batch()
second = Batch()

assert first.rows == []
assert second.rows == []
assert first.rows is not second.rows
first.rows.append(7)
assert second.rows == []
```

This establishes distinct list objects for these instances. To understand why, inspect `Lib/dataclasses.py` in the exact Python version and search for `default_factory`, then read the related tests. The experiment does not prove every internal code-generation detail; the source inspection supplies that explanation.

## 7. Read tests as executable specifications

Tests are evidence of intended behavior, but they are not a complete specification. A project may lack a test for a valid edge case, or tests may encode historical behavior that maintainers plan to change.

When a test looks relevant:

1. Identify the exact test function and fixtures.
2. Read setup and teardown, not just the assertion.
3. Find parametrization and platform/version guards.
4. Check whether the test runs against a fallback, accelerator, or both.
5. Run the narrow test first; then run the relevant module or suite.
6. If a test contradicts documentation, verify versions and report the discrepancy rather than assuming one is automatically correct.

Examples in a CPython checkout (run from the repository root using its built interpreter where appropriate):

```bash
./python -m test test_dataclasses -v
./python -m test test_functools -v
```

The test names and invocation details can vary by release. Check `./python -m test --help` and the test files in the target checkout before relying on a command. A regular installed interpreter can run many `unittest` tests, but CPython-specific tests may require the in-tree build or special test support.

## 8. Experiments, debugging, and performance analysis

### 8.1 Keep experiments minimal

A useful experiment changes one variable, has a clear expected result, and avoids external dependencies. Record the command and raw output, including Python version.

For behavioral questions, prefer assertions over a screenshot. For performance questions, separate correctness from timing.

### 8.2 A repeatable microbenchmark

`timeit` is useful for small controlled comparisons, but a single timing is not a performance conclusion.

```python
import statistics
import timeit

setup = "data = list(range(10_000))"
stmt = "sum(data)"

samples = timeit.repeat(stmt, setup=setup, repeat=7, number=100)
print("seconds per 100 runs:", samples)
print("median:", statistics.median(samples))
```

This benchmarks `sum` on a constructed list, not the entire behavior of a production pipeline. For a meaningful comparison:

- Use the same interpreter build and machine state.
- Include warm-up or specialization effects when relevant.
- Compare equivalent outputs and semantics.
- Use representative data sizes and distributions.
- Report median and spread, not only the fastest sample.
- Avoid drawing conclusions from noisy measurements or tiny differences.
- Use a benchmark suite such as `pyperf` for more rigorous comparisons when appropriate.

For memory, consider `tracemalloc` for Python allocation traces, while remembering that it does not account for every native allocation. Native profilers and OS tools may be needed for extension-heavy code.

### 8.3 Debug into library code

In an IDE, disable “Just My Code” or equivalent and add a breakpoint in the installed package. Confirm the debugger's file path matches the package version under test.

A generic `pdb` approach:

```python
import pdb
pdb.set_trace()

# Call the library function of interest below this point.
```

This pauses at the current line; step into the relevant call when execution reaches it. For a repeatable bug, create a small script first. Avoid debugging a full production job when a five-line reproduction will isolate the behavior.

When a traceback enters `site-packages`:

1. Read the complete traceback and identify the first frame that crosses into the dependency.
2. Check arguments and invariants at the call boundary.
3. Reproduce with the smallest input possible.
4. Inspect dependency source and tests for the installed version.
5. Search release notes, issues, and commits for a known fix.
6. Decide among correcting caller misuse, upgrading, a supported workaround, or reporting an upstream bug.
7. If a temporary monkey-patch is unavoidable, isolate it, test it, document why it exists, and set an explicit removal condition/date.

### 8.4 `strace` and native behavior

On Linux, `strace` can show system calls made by a process:

```bash
strace -f -o /tmp/python.trace python reproduce.py
```

Use it only where available and appropriate. It shows syscalls, not Python-level call relationships or the full internal state of a C function. Other operating systems require different tools.

## 9. CPython source investigation at advanced depth

### 9.1 Build and debug a separate checkout

Do advanced experiments in a disposable clone or worktree, never in the only copy of a production checkout.

A typical Unix-like development build may begin with:

```bash
./configure --with-pydebug
make -j2
./python -VV
./python -X dev -m test test_dataclasses -v
```

Build prerequisites and exact commands vary by OS, release, and toolchain. Read the CPython Developer's Guide for the selected version. Do not assume a build succeeded merely because a command was issued; inspect the exit status and run the built interpreter's version command.

Useful diagnostic options and environment settings include:

- `--with-pydebug`: a debug-oriented CPython build with additional checks.
- `-X dev`: enable development-mode runtime checks.
- `PYTHONMALLOC=debug`: enable allocator debugging where supported by the build.
- `gdb` / `lldb`: native debugging.
- `python-gdb.py`: CPython-aware GDB helpers when installed/configured for the build; commands such as `py-bt` and `py-locals` are available only when the helper setup supports them.

A debugger session is version/build dependent. Record the exact binary and build flags. Never infer that a memory issue is absent simply because one debug run did not reproduce it.

For deeper CPython work, consult the selected release's Developer's Guide before enabling profile-guided optimization (PGO) or link-time optimization (LTO), and inspect `Tools/` for existing developer utilities such as `Tools/c-analyzer` when present. These tools and build options are release- and platform-dependent; verify availability in the exact checkout. For learning-only experiments, use a disposable branch to add instrumentation (for example, a temporary `fprintf`) or trace a compiler-to-opcode-to-evaluator path. A new built-in method or opcode is a substantial multi-layer change, not a quick one-file edit: follow the required declarations, generated metadata, implementation, tests, and build steps for that version. Do not present a partial experiment as a working interpreter feature.

### 9.2 Trace an implementation path, not the whole interpreter

For a list operation, for example:

1. Observe the Python operation and measure/inspect its behavior.
2. Locate the public C API or type slot and its implementation in the target source.
3. Follow helper functions that manage allocation or mutation.
4. Inspect relevant headers and structure declarations.
5. Read tests for edge cases and debug assertions.
6. Use a debug build or native debugger if source reading alone leaves a question unanswered.

For a bytecode question:

1. Use `dis` on the running interpreter.
2. Locate compiler/bytecode metadata in the matching source.
3. Locate the execution path or generated handler.
4. Inspect specialization/deoptimization logic if relevant to the observed build.
5. Run a minimal test with development mode or debugger.
6. Repeat across versions only if the question is explicitly about version differences.

Do not treat private structure fields or opcode names as public API. They are useful for understanding a version, not for writing portable application code.

### 9.3 Performance-sensitive designs to cross-read

The roadmap identifies these valuable topics:

- `dict` and `set`: hashing, probing, resizing, and collision behavior.
- Unicode strings: PEP 393 and representation choices.
- Small integers and string interning: understand what is an optimization, what is an implementation detail, and what is not guaranteed.
- `list.sort`: study the design notes around Timsort (including `Objects/listsort.txt` where present).
- `re` / `_sre`: compile-time versus match-time work and backtracking risks.
- `asyncio` event loop and `selectors`: readiness notification and scheduling boundaries.
- `concurrent.futures`, `queue`, `threading`, and `multiprocessing`: coordination, locking, and start-method differences.
- Free-threaded builds and concurrency work: verify the exact build/configuration and relevant PEPs, rather than assuming the conventional GIL-enabled build tells the whole story.

Relate source findings to measurements from profiling/performance work. A clever data structure does not prove it is the bottleneck in your application.

## 10. Reading third-party libraries as a vertical slice

Start from the public API and trace one request through the architecture. Do not try to understand the entire package before answering one question.

Examples from the roadmap include:

- **HTTP clients:** `requests.get` → session-level request handling → adapters → transport dependency such as `urllib3`.
- **FastAPI/Starlette:** public route declaration → ASGI application path → middleware/dependency injection → response handling.
- **SQLAlchemy:** public Core/ORM call → statement construction or unit-of-work behavior → dialect/driver boundary.
- **Pydantic:** model declaration → schema construction/validation entry point → native core where used.
- **httpx/httpcore:** public client → transport interface → lower-level protocol/network layer.
- **pytest:** test discovery/call path → hooks/plugins → assertion rewriting.
- **pandas/NumPy/scikit-learn/PyTorch/transformers:** choose one operation or model path and follow it through the public API, internal layers, tests, and relevant native components.

The actual call graph depends on the version, configuration, plugins, backend, and optional dependencies. Confirm it from the installed code and tests.

### 10.1 A vertical-slice worksheet

```text
Public API:
Input and output contract:
First implementation file:
Call path (ordered):
Extension/backend boundary:
Relevant tests:
Extension points or plugins:
Version and configuration:
Experiment:
Conclusion:
Open questions:
```

For each library, sketch the architecture and list **three design decisions worth adopting** and **one decision you would avoid**, with reasons. This forces critical analysis rather than admiration without evidence.

## 11. PEPs, design documents, issues, and Git history

Source answers “what this version does.” Design documents and history often answer “why it does that.”

The roadmap names several relevant PEPs:

- PEP 557 — data classes.
- PEP 3119 — abstract base classes.
- PEP 343 — the `with` statement/context managers.
- PEP 484, PEP 585, and PEP 695 — Python typing evolution.
- PEP 554, PEP 684, and PEP 703 — interpreter/concurrency-related proposals and changes.
- PEP 659 — specializing adaptive interpreter.

A PEP may describe an original proposal, while current implementation and behavior may have evolved. Read the accepted PEP, current documentation, release notes, tests, and source for the target version. Do not treat the PEP alone as proof of current implementation details.

A disciplined history investigation:

```bash
git log --oneline -- path/to/module.py
COMMIT_SHA=$(git rev-parse HEAD)
git show "$COMMIT_SHA" -- path/to/module.py
git blame -L 1,20 path/to/module.py
git log -S"interesting_symbol" --oneline -- path/to/module.py
```

Replace placeholders with real values from the checked-out repository. Follow the commit to its pull request/issue or design note when possible. If no rationale is documented, say so; do not fabricate intent from the code alone.

## 12. Security and dependency quality review

Reading source is one part of dependency assessment. Inspect packaging and build metadata as well as runtime code:

- `pyproject.toml`, build backend, `setup.py` if present, setup hooks, and entry points.
- Network, subprocess, dynamic execution, deserialization, filesystem, and credential-handling paths.
- Obfuscation or unexpected generated/binary files, maintainer/release history, dependency changes, and package-name confusion.
- Installation-time code paths, which can execute before the package is imported.
- License metadata and the project's contribution policy.

Possible supporting tools include `pip-audit` for known vulnerable dependencies and tools such as `bandit` or `guarddog` for particular classes of risks. No scanner proves a package is safe. Read tool documentation and interpret findings in context.

For suspicious packages, use an isolated disposable environment/container and deny network access unless network behavior is the subject of a controlled test. Do not install an untrusted package into your primary development environment. A package's source repository may differ from the published artifact; compare exact release artifacts and source tags where provenance matters.

### 12.1 Read-only historical case study: the `ctx` PyPI compromise (2022)

Use this documented incident to practise supply-chain investigation without executing the package:

- Read the [Python Security incident report](https://python-security.readthedocs.io/pypi-vuln/index-2022-05-24-ctx-domain-takeover.html) and the [GitHub Security Advisory GHSA-4g82-3jcr-q52w](https://github.com/advisories/GHSA-4g82-3jcr-q52w). Verify the incident dates, affected distribution artifacts, and described behavior against the advisory rather than relying on a secondary summary.
- Examine the documented payload statically. Identify where environment variables are read, how data is transformed, and where a network request is made. Do not copy or run the payload, contact the historical endpoint, or install a compromised release.
- Compare the published distribution artifact described by the incident with the corresponding source repository/release where evidence is available. Record any mismatch; a repository checkout is not proof that a registry artifact was identical.
- Write a short evidence chain: package/version and artifact identity → suspicious code path → sensitive data accessed → attempted exfiltration path → available mitigations and prevention controls. Separate verified facts from hypotheses.
- Explain why dependency review must include release provenance, maintainer-account security, install-time behavior, runtime behavior, and lockfile/artifact verification—not only whether the current source repository looks benign.

This is a static, historical learning exercise. It is not an instruction to download, install, or execute the compromised package.

## 13. Responsible AI-assisted source navigation

An AI assistant can help generate search terms, summarize a function you provide, suggest a call path, or propose experiments. It can also hallucinate filenames, APIs, line numbers, version behavior, and causal explanations.

Use this verification protocol:

1. Ask for candidate files and symbols, not unverified final truth.
2. Check every named path and symbol in the exact checkout.
3. Re-run suggested commands and tests.
4. Verify any line citations against a pinned commit/tag.
5. Distinguish the model's inference from comments, tests, docs, or observed output.
6. Do not paste secrets, customer data, private source, or restricted code into tools not approved for that data.
7. Record unresolved uncertainties instead of smoothing them over.

A useful source claim should be reproducible by another engineer with the same commit and environment. Once verified, preserve the investigation in a versioned source-reading notebook (one page per mechanism: question, exact version, file/line references, diagram, experiment, result, and uncertainty). For knowledge sharing, turn a well-supported investigation into a short deep-dive article or internal walkthrough; if you discover a documentation gap, consider a focused upstream docs/comment/test contribution using the project's contribution process.

## 14. Common mistakes and how to recover

| Mistake | Why it misleads | Better approach |
|---|---|---|
| Reading a `.pyi` as runtime code | Stub bodies are often declarations only | Find the imported module and actual implementation |
| Assuming `inspect` must expose all source | C, built-in, generated, or stripped objects may not be inspectable | Locate matching native source and tests |
| Using `main` branch links in a long-lived report | Line references drift | Pin to a release tag or commit SHA |
| Reading the entire repository linearly | High effort, low signal | Start with a specific question and vertical slice |
| Trusting comments without checking tests | Comments can be stale | Compare docs, tests, behavior, and history |
| Benchmarking a different code path | Result may not reflect the implementation being investigated | Confirm dispatch, version, and workload |
| Inferring a language guarantee from CPython internals | Other Python implementations may differ | Label contract versus implementation detail |
| Editing core source in a working production tree | Experiments contaminate the checkout | Use a disposable clone/worktree and record the diff |
| Treating one experiment as universal proof | Inputs and environment are limited | State scope, limitations, and what remains untested |
| Trusting AI-generated line numbers | They may be fabricated or stale | Generate line references locally from the pinned tree |

## 15. Source-reading report template

Use this template for each report. The capstone requires three reports, each approximately 2–4 pages.

```markdown
# Source Reading Report: <mechanism>

## Question
A single, falsifiable question.

## Version and environment
- Project:
- Release tag / commit SHA:
- Python implementation and version:
- OS / architecture:
- Build flags or relevant configuration:
- Dependency versions:

## Public contract
What do official docs promise? Cite the documentation/version.

## Source map
| File and line range | Symbol | Role | Evidence |
|---|---|---|---|
| `path/to/file.py:Lx-Ly` | `symbol` | entry point/helper | pinned source link |

## Execution path
1. Public API:
2. Validation/dispatch:
3. Main algorithm:
4. Native/backend boundary:
5. Return/error path:

## Diagram
Use a Mermaid flowchart or a small ASCII diagram.

## Experiment
- Hypothesis:
- Reproduction or benchmark command:
- Expected observation:
- Actual output:
- Repeatability/limitations:

## Tests and history
- Relevant tests:
- Commit/PR/issue/design note:
- What the evidence establishes:
- What remains uncertain:

## Conclusion
Separate documented guarantees from version-specific implementation details.

## Design critique
- Three decisions worth adopting, with reasons:
- One decision to avoid or reconsider, with reasons:
- What I would change, if anything:
```

Line ranges must be obtained from the exact checkout. If the project does not provide a documented rationale or relevant test, note that gap instead of inventing a reference.

## 16. Exercises with worked solutions

### Exercise 1 — Stub or implementation?

Your IDE opens `package/api.pyi` for `Client.send`. You need to know whether the method retries automatically.

**Work it out:** What do you inspect next?

**Worked solution:** The stub is useful for the callable's interface, but it cannot establish runtime retry behavior. Find the imported package path using `package.__file__`, inspect the implementation and configuration defaults, search tests for `send` and retry behavior, and reproduce with a local fake transport if feasible. Record the installed version. If retrying is delegated to an adapter or transport, follow that path too.

### Exercise 2 — `inspect.getsource` fails

`inspect.getsource(math.sqrt)` raises `TypeError`.

**Worked solution:** This is expected for many built-in/extension callables. It does not mean the function has no source implementation. Record the interpreter/build, identify the corresponding CPython source and C API path in the matching tag, and read the tests. Do not use a different version's line number as evidence for the running binary.

### Exercise 3 — Explain `default_factory`

Write a minimal experiment proving that two dataclass instances do not share the same default list, then explain what it does and does not prove.

**Worked solution:** Use the example in Section 6.1. The identity assertion and mutation isolation demonstrate distinct per-instance list objects for this class. To explain implementation, inspect the matching `dataclasses.py` and tests. The experiment alone does not prove how the generated initializer is assembled.

### Exercise 4 — Find list growth logic

You want to understand why repeated `list.append` calls do not require a fresh allocation for every element.

**Worked solution:** Record `python -VV`; inspect `Objects/listobject.c` in the matching CPython tag; search for append, resize, and allocation helpers; read the relevant structure declarations and comments; inspect tests; then run a controlled allocation/capacity experiment only if you have a reliable way to observe capacity in that build. Do not infer exact capacity from `sys.getsizeof` alone without accounting for object header, allocator, and version differences. Report the implementation strategy for the pinned version, not a permanent Python-language guarantee.

### Exercise 5 — A dependency traceback

A data pipeline fails inside a third-party parser on one malformed row.

**Worked solution:** Save the complete traceback, package version, and minimal input. Reduce the input until one row reproduces the error. Inspect the public parser API, the failing internal path, and tests for malformed inputs. Search release notes and history for a fix. If caller input violates the documented contract, fix the caller; if behavior contradicts the contract, create a regression test and report it upstream. Avoid monkey-patching without tests and a removal plan.

### Exercise 6 — Performance claim

A colleague says “the C accelerator is always faster.”

**Worked solution:** Treat this as a hypothesis. First verify that the selected accelerator is actually used, then compare equivalent operations and semantics on representative inputs, multiple sizes, and the same build. Use repeated measurements and report variance. Consider import costs, allocation, conversion, and workload shape. One benchmark cannot establish “always,” and an accelerator can be faster for one workload but not another.

### Exercise 7 — AI-generated source map

An assistant claims that `Objects/dictobject.c:900` implements dictionary resizing in your target Python release.

**Worked solution:** Treat the line number as unverified. Check out the release tag, run `rg -n` for resize-related symbols, inspect the surrounding implementation, and derive the line range locally with `nl -ba`. If the symbol or file layout differs, correct the map and document the discrepancy. Do not cite the claim until verified.

### Exercise 8 — Design rationale is missing

You understand what a helper does, but cannot find why it was introduced.

**Worked solution:** Inspect Git history, the associated PR/issue, design docs, release notes, and tests. Search for removed code or previous implementations. If no evidence records intent, state “rationale not found in inspected sources” and separate any inference from fact. Consider proposing a concise explanatory comment or design note if future maintainers would benefit.

## 17. Self-check with answers

1. **Where should you look to understand dictionary resizing?** Start with `Objects/dictobject.c` in the exact CPython tag, read its design comments, search for insertion/resize helpers, and follow the relevant structure declarations and tests. Use `InternalDocs/` if the checkout contains relevant design notes.
2. **How do you step through a third-party library?** Reproduce the issue in a minimal script, confirm the installed package version/path, enable stepping into library code in the debugger, set a breakpoint in the matching implementation, and follow the call path. Keep the reproduction and environment recorded.
3. **How do you explain which entry `lru_cache` evicts?** Construct a bounded cache, record function calls, hit an older key to update recency, add a new key, and inspect `cache_info()`. Then read the matching Python wrapper, C implementation if used, and tests. State observed behavior separately from implementation details.
4. **Why is a source-reading notebook useful?** It preserves the question, version, source locations, diagram, experiment, result, and uncertainty so another engineer can reproduce the investigation without starting over.
5. **Why not read every file first?** Source reading is most effective when guided by a concrete question. A vertical slice limits scope, produces a testable conclusion, and exposes the most relevant abstractions and dependencies.

## 18. Capstone: three source-reading reports

Produce three reports, each about 2–4 pages, using the template in Section 15. Each report must pin a specific commit or release tag, cite source locations from that version, include a diagram, run an experiment, and contain a “what I would copy / avoid” critique.

### Report A — Pure-Python standard-library mechanism

Choose `functools.lru_cache` or `dataclasses`.

Required work:

- Record the exact Python version and source tag/commit.
- Describe the public contract from version-matched documentation.
- Trace a public call through the relevant Python implementation.
- Read the relevant tests and, for `lru_cache`, inspect the C wrapper if the selected build uses one.
- Run a reproducible behavioral experiment.
- Include a diagram and explicit design critique.

### Report B — CPython C-level mechanism

Choose list growth, dictionary lookup/resizing, or a bytecode execution path.

Required work:

- Record the exact CPython commit/tag and build configuration.
- Map relevant files in `Objects/`, `Python/`, `Modules/`, and/or `Include/`.
- Cite verified file paths and line ranges.
- Read implementation comments and tests.
- Run an experiment or debugger session that supports a narrow claim. If a reliable measurement requires an instrumented/debug build, state that requirement rather than inventing a result.
- Explain which details are CPython-specific and may change.

### Report C — Third-party library vertical slice

Choose a real library such as `httpx`, `pytest`, `pandas`, `SQLAlchemy`, `FastAPI`, or another package you use.

Required work:

- Record the installed package version and a matching source tag/commit.
- Start at one public API and trace the call path to a key internal layer or native boundary.
- Inspect tests, extension points, and release notes.
- Reproduce a behavior, exception, or performance observation.
- Include a diagram, source references, limitations, and design critique.

### Final quality gate

A report is not complete until another engineer can reproduce its central experiment and verify its source links. Do not claim that a command, benchmark, or debugger session ran unless you actually ran it. If a specific source version is unavailable, state the limitation and use a version you can verify.

## 19. Further reading

Use version-matched primary sources first:

- Python documentation: `https://docs.python.org/`
- CPython source: `https://github.com/python/cpython`
- CPython Developer's Guide: `https://devguide.python.org/`
- Python Enhancement Proposals: `https://peps.python.org/`
- Typeshed: `https://github.com/python/typeshed`

For third-party projects, use their official source repository, release tags, documentation, tests, changelog, contribution guide, and security policy. Pin references to the version you actually investigated.

---

**Completion criterion:** You can start from a precise question, find the actual implementation, trace the relevant path, validate a hypothesis with tests or an experiment, cite a specific source version, and explain both what the evidence proves and what it does not prove.
