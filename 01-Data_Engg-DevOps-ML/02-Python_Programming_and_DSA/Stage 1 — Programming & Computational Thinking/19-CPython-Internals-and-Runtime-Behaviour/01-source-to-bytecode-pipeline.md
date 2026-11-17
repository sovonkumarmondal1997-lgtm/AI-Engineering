# Source-to-Bytecode Pipeline

> **Target:** CPython 3.12–3.14  
> **Scope:** How Python source is tokenised, parsed, analysed, compiled to a code object, and evaluated; how bytecode caches and compiler options affect imports and deployment.  
> **Version warning:** Python language semantics are broader than CPython. Bytecode, code-object layout details, parser implementation, private symbols, and command-line implementation switches are version- and build-sensitive. Treat `dis` output as evidence about the interpreter you actually run, not as a cross-version contract.

## Learning outcomes

After this lesson, you should be able to:

1. Explain why CPython is a bytecode compiler plus virtual machine rather than a source-text interpreter that simply executes one line at a time.
2. Trace source through tokenisation, PEG parsing, AST construction, symbol-table analysis, code-object generation, and evaluation.
3. Inspect the stages with `tokenize`, `ast`, `symtable`, `compile`, and `dis`.
4. Distinguish compile-time errors from errors that arise only when code executes.
5. Explain local, global, free, and cell variables, including `UnboundLocalError`, closures, and `nonlocal`.
6. Inspect useful code-object metadata while avoiding reliance on unstable bytecode details.
7. Explain `.pyc` caching, `__pycache__`, PEP 552 invalidation modes, and why bytecode caches chiefly reduce import-time compilation work.
8. Use compile modes, AST-only compilation, optimisation levels, and source-position metadata safely.
9. Recognise the deployment implications of encoding declarations, future imports, `__debug__`, frozen modules, import-time costs, and bytecode-cache policy.
10. Describe when AST transformation or import-time source rewriting is useful and why it needs careful design.
11. Complete the pipeline-inspection exercise and answer the three self-check questions.

## Prerequisites

You should already be comfortable with Python expressions, assignments, functions, exceptions, imports, and basic scope rules. You do not need to read C to benefit from this lesson. Helpful background includes the difference between source code and machine instructions, the idea of a virtual machine, and the role of an interpreter process.

Examples target CPython 3.12–3.14. Commands use `python` to mean the interpreter under test; check it with `python --version`. If several Python versions are installed, use the explicit executable (for example, `python3.12` or `python3.14`). Most examples use documented standard-library APIs. Bytecode and some metadata examples can vary between these versions.

## 1. Mental model: compiler plus virtual machine

CPython does not normally read a `.py` file and execute each source line directly as text. It compiles source into **code objects** containing bytecode and metadata. The CPython evaluation machinery then executes that bytecode.

A useful high-level model is:

```text
source bytes / source text
        |
        v
encoding detection and tokenisation
        |
        v
PEG parsing (grammar and syntax)
        |
        v
abstract syntax tree (AST)
        |
        v
symbol-table and scope analysis
        |
        v
code generation and compiler optimisations
        |
        v
code object(s): bytecode + constants + names + positions + flags
        |
        v
evaluation in the CPython runtime
        |
        v
program effects, values, exceptions, I/O
```

This is a conceptual pipeline, not a promise that each stage is a separately exposed object or that every implementation performs all work in exactly this order internally. The AST and symbol table are useful public inspection interfaces; internal compiler passes and data structures can change.

### What each stage contributes

| Stage | What it does | Why it matters |
| --- | --- | --- |
| Encoding and tokenisation | Decodes source according to Python's source-encoding rules and groups characters into tokens such as names, operators, numbers, strings, and indentation markers. | Explains encoding errors, token boundaries, and why lexical tools are not full parsers. |
| Parsing | Checks whether the token sequence fits Python's grammar and builds a syntactic structure. CPython has used a PEG parser since Python 3.9. | Many `SyntaxError`s are detected before execution. |
| AST | Represents constructs such as assignments, calls, loops, and function definitions as structured nodes. | Linters, formatters, static analysers, and source transformers can reason about structure instead of matching text. |
| Symbol-table analysis | Determines how names are classified in each block, including local, global, free, and cell variables. | Explains closure construction and compile-time decisions that lead to `UnboundLocalError`. |
| Code generation | Produces code objects and bytecode, with constants, names, flags, source locations, and other metadata. | Makes the source executable by the CPython runtime. |
| Evaluation | Runs bytecode and invokes Python operations, built-ins, and native code as needed. | Runtime errors such as `NameError` and `TypeError` occur when the relevant operation is reached. |

### Language semantics versus CPython implementation

The Python language defines observable behaviour such as expression evaluation, lexical scope, exceptions, and function semantics. CPython's bytecode instruction set, code-object representation, PEG parser implementation, adaptive interpreter, and `.pyc` format details are implementation-specific.

PyPy, GraalPy, MicroPython, and other implementations can execute Python code using different internal strategies. A program should rely on documented language behaviour, not on a particular opcode sequence, object address, private C function, or incidental optimisation.

**Real-world example:** A linter can parse code and report an undefined name without running the application. A production process, by contrast, must execute the compiled code and may then encounter an input-dependent `TypeError`. Both tools interact with the language, but they answer different questions at different stages.

## 2. Inspecting the front of the pipeline

We'll use a small source string throughout the lesson:

```python
src = "total = price * 2\n"
```

It assigns the result of multiplying `price` by `2` to `total`. The source can be tokenised, parsed, analysed, and compiled without executing the assignment.

### 2.1 Tokenisation with `tokenize`

**What it is.** Tokenisation groups source characters into lexical units. Python's standard-library `tokenize` module exposes a useful Python-level tokenizer for source text or files.

**Why it matters.** Token streams help explain indentation, operators, identifiers, string literals, comments, and source formatting. They are useful for editors, syntax highlighters, linters, and diagnostics.

```python
import io
import tokenize

src = "total = price * 2\n"

tokens = tokenize.generate_tokens(io.StringIO(src).readline)
for token in tokens:
    print(token.type, tokenize.tok_name[token.type], repr(token.string))
```

The output includes token entries corresponding to `total`, `=`, `price`, `*`, `2`, a newline, and an end marker. It also includes position information in each token object. The exact token stream and numeric token type values are not a stable teaching target; inspect token names and values rather than hard-coding numeric IDs.

**Important limitation:** tokenisation alone does not establish that a complete program is grammatically valid. A sequence of individually recognisable tokens may still be an invalid Python statement. Also, the Python-level `tokenize` module is not identical to every internal detail of CPython's C tokenizer. This distinction matters for tools that must support a particular interpreter version, especially around newer syntax such as f-strings.

### 2.2 Parsing and the AST

**What it is.** The parser checks grammar and constructs an abstract syntax tree (AST). The AST keeps semantic structure while omitting many surface details such as comments and most formatting choices.

```python
import ast

src = "total = price * 2\n"
tree = ast.parse(src, filename="<demo>", mode="exec")
print(ast.dump(tree, indent=2))
```

The AST describes a module containing an assignment. Its target is the name `total`; its value is a multiplication expression whose operands are the name `price` and the constant `2`. Exact AST fields can evolve as Python adds syntax, so consult the documentation for the version you target.

`ast.parse()` is convenient for analysis, but successful parsing does **not** guarantee that the program can be compiled or executed. For example, a contextually invalid construct may survive an AST-building step but fail later validation or compilation.

**When useful:** a code-quality tool can inspect `ast.Call` nodes to find calls to selected APIs, or inspect assignments without being confused by spaces and line breaks.

**Trade-off:** ASTs are structured but do not preserve all original source formatting. If a tool must retain comments and whitespace precisely, the standard AST alone may not be enough.

### 2.3 PEG parser context and soft keywords

CPython adopted a PEG (Parsing Expression Grammar) parser in Python 3.9. The PEG grammar is maintained in the CPython source tree at `Grammar/python.gram`; grammar and implementation details must be checked against the specific release.

A **soft keyword** is a word that has special syntactic meaning only in particular contexts rather than being reserved everywhere. For example, `match` and `case` participate in structural pattern-matching syntax but can still be ordinary identifiers in contexts where the grammar permits them. The `type` statement introduced in Python 3.12 also gives `type` a contextual role in type-alias syntax.

This contextual design allows Python to evolve its grammar while avoiding unnecessary breakage of existing identifiers. Do not build syntax tools by treating every soft keyword as globally reserved. Parse against the grammar of the Python version the tool claims to support.

### 2.4 F-string tokenisation changes in Python 3.12

PEP 701 formalised f-string grammar and enabled f-strings to use expressions and quoting patterns that were previously restricted by the older implementation. In Python 3.12, tokenisation-related interfaces changed to represent f-string pieces more explicitly, including token categories such as `FSTRING_START`, `FSTRING_MIDDLE`, and `FSTRING_END`.

**Why this matters:** syntax highlighters, formatters, and custom token processors that assumed an f-string was always one opaque string token may need updates. Test tools against the actual target interpreter and use the documented `tokenize` interface for that version.

Do not infer that every Python implementation uses CPython's internal tokenizer or exposes exactly the same token stream. PEP 701 concerns Python's f-string grammar; internal implementation details remain implementation-specific.

## 3. Symbol-table analysis and scope decisions

The symbol table records how identifiers are classified in code blocks. In CPython, scope classification is a compile-time decision, not a guess made afresh each time a line executes.

### 3.1 Local and global names

Consider:

```python
x = 10

def show():
    print(x)

show()
```

The function reads `x` without assigning to it, so `x` is resolved as a global name (with built-ins also participating in global-name lookup rules). At runtime, the function can find `x` in the module's global namespace.

Now change the function:

```python
x = 10

def show():
    print(x)
    x = 1

show()
```

Because the function contains an assignment to `x`, the compiler classifies `x` as local throughout that function block unless scope declarations change the rule. The `print(x)` therefore attempts to read the local before it has been assigned, and calling `show()` raises `UnboundLocalError`.

This is the important distinction:

- The **compile-time** scope analysis determines that `x` is local.
- The **runtime** failure occurs when execution tries to read that local before it has a value.

`UnboundLocalError` is a subclass of `NameError`. The compiler does not need to know the value of `x` to make the scope decision.

### 3.2 Inspecting scopes with `symtable`

```python
import symtable

src = """
x = 10

def show():
    print(x)
    y = 2
    return y
"""

table = symtable.symtable(src, "<scope-demo>", "exec")
print("module identifiers:", table.get_identifiers())

function_table = next(
    child for child in table.get_children()
    if child.get_name() == "show"
)
for name in function_table.get_identifiers():
    symbol = function_table.lookup(name)
    print(
        name,
        "local=", symbol.is_local(),
        "global=", symbol.is_global(),
        "referenced=", symbol.is_referenced(),
        "assigned=", symbol.is_assigned(),
    )
```

The function's `x` is global and referenced; `y` is local and assigned. Exact formatting of the output is determined by the `print` calls, while classifications come from the symbol-table API. Additional symbol predicates are available in the version-specific `symtable` documentation.

**Why useful:** the API can help explain a confusing scope error, and static-analysis tools can inspect scope relationships without executing the source.

**Limitations:** `symtable` describes the compiler's symbol classification; it does not prove that a name will exist at runtime or that execution will succeed.

### 3.3 Free variables, cell variables, closures, and `nonlocal`

A **free variable** is a name used in a nested code block but bound in an enclosing function scope. A **cell variable** is a local in an outer function whose value must be available to nested code. CPython uses closure cells to make that binding accessible after the outer function has returned.

```python
def make_counter():
    count = 0

    def increment():
        nonlocal count
        count += 1
        return count

    return increment

counter = make_counter()
print(counter())  # 1
print(counter())  # 2
```

The inner function retains access to the enclosing `count` binding through a closure cell. `nonlocal count` declares that assignments refer to the nearest enclosing function scope containing that name, rather than creating a new local or assigning a module global.

Without `nonlocal`, `count += 1` makes `count` local to `increment`; because the operation reads that local before assigning its updated value, calling the function raises `UnboundLocalError`.

Closures capture bindings, not a frozen snapshot of a value at function-definition time. That distinction explains common late-binding behaviour in loops.

### 3.4 Inspecting symbol tables and code-object scope metadata

The symbol-table API gives a high-level view. After compilation, code objects expose `co_freevars` and `co_cellvars`, which are useful clues about closure relationships:

```python
def outer(value):
    def inner():
        return value
    return inner

fn = outer("captured")
print(fn.__code__.co_freevars)
print(fn.__closure__)
```

Representative observation: `co_freevars` identifies `value` as a free variable for `inner`; `fn.__closure__` is a tuple of cell objects for the captured values. The representation of a cell object is not a stable API, so use the documented code-object and function attributes rather than parsing its `repr`.

## 4. Compilation, code objects, and bytecode

### 4.1 `compile()` and the evaluation boundary

`compile()` compiles source text or an AST into a code object, or produces an AST when requested with `ast.PyCF_ONLY_AST`. It does not execute the resulting code object.

```python
src = "total = price * 2\n"
code = compile(src, "<demo>", "exec")

print(code.co_names)
print(code.co_consts)
```

The names include the identifiers referenced or bound by the module code, and constants include values used by the code. Exact tuple ordering and bytecode are implementation details. This snippet deliberately inspects metadata rather than asserting a particular opcode sequence.

Execution is a separate action:

```python
namespace = {"price": 21}
exec(code, namespace)
print(namespace["total"])  # 42
```

Here `exec()` executes the code object using the supplied namespace. If `price` were missing, the code could compile successfully but fail at execution with `NameError`.

**Operational warning:** `exec()` and `eval()` can execute arbitrary code. Never pass untrusted input to them as a way to “validate” it. Restricting the globals dictionary is not a reliable general-purpose sandbox.

### 4.2 Code-object fields

A code object stores executable code plus metadata. Useful attributes include:

| Attribute | Meaning and use |
| --- | --- |
| `co_code` | A bytes representation of bytecode. In CPython, it may be created on demand and need not reflect the exact specialised instructions currently executed by the adaptive interpreter. The format and opcode meanings are version-specific; do not treat it as a portable binary format. |
| `co_consts` | Constants used by the code, including nested code objects in many cases. |
| `co_names` | Names referenced by the code, often including globals and attributes. It is not a complete runtime dependency list. |
| `co_varnames` | Local variable and parameter names represented in the code object. Exact layout is compiler-dependent. |
| `co_freevars` | Names captured from enclosing scopes. |
| `co_cellvars` | Locals made available through closure cells to nested code. |
| `co_argcount` | Number of positional-only plus positional-or-keyword parameters. Interpret alongside the other argument-count fields. |
| `co_flags` | Flags describing properties of the code object, such as generator/coroutine-related characteristics. Flag bits are implementation details. |
| `co_stacksize` | The value-stack size the compiler determines is needed for the code. It is not the Python call-stack depth. |
| `co_filename`, `co_name`, `co_qualname` | Source filename and code names useful for diagnostics and introspection. |
| `co_firstlineno` | First source line associated with the code object. |
| `co_linetable` | Encoded source-line mapping in modern CPython. Its byte encoding is not a public parsing contract. |
| `co_positions()` | Fine-grained source positions, including line and column information where available (Python 3.11+). |

Older material may mention `co_lnotab`. It has been deprecated since Python 3.12 and should not be the basis for new tooling. For modern code, prefer documented line/position APIs such as `co_lines()` and `co_positions()` where appropriate. PEP 657 introduced fine-grained error locations, enabling more precise carets in tracebacks; the exact display depends on the source and runtime. Position details can be reduced or absent when the code was compiled with `-X no_debug_ranges` (or `PYTHONNODEBUGRANGES`) or when an instruction has no meaningful source span.

A code object's metadata is useful for profilers, debuggers, coverage tools, and educational inspection. It is not a stable serialized interface for storing code objects across Python versions.

### 4.3 Inspect bytecode with `dis`

```python
import dis

def calculate(a, b):
    return a + b * 2

dis.dis(calculate)
```

`dis` displays the bytecode for the function. Conceptually, the computation must load `b` and `2`, multiply them, load `a`, add the results, and return. The exact opcodes, offsets, cache entries, instruction ordering, and display columns can differ between CPython releases and may be affected by interpreter specialisation. On CPython versions that support it, `dis.dis(function, adaptive=True, show_caches=True)` can expose adaptive/specialised instructions and inline-cache entries after execution has warmed the function; those details are diagnostic observations, not a stable API.

Do not copy a bytecode listing from one Python version into production tests as if it were a language guarantee. This lesson's goal is to understand the compilation pipeline; detailed opcode reading belongs to the next lesson, **Reading Bytecode with `dis`**.

### 4.4 Compile modes: `exec`, `eval`, and `single`

`compile(source, filename, mode)` supports three common modes:

- **`"exec"`**: a suite of statements, such as a module or multiple assignments.
- **`"eval"`**: a single expression whose evaluated value is returned by `eval()`.
- **`"single"`**: a single interactive statement, with display behaviour intended for interactive use.

```python
expression_code = compile("2 + 3", "<expr>", "eval")
statement_code = compile("answer = 2 + 3", "<stmt>", "exec")
interactive_code = compile("2 + 3", "<single>", "single")

print(eval(expression_code))  # 5

scope = {}
exec(statement_code, scope)
print(scope["answer"])        # 5

# The "single" mode is designed for interactive-style statements.
# Its display behaviour depends on the interactive display hook.
exec(interactive_code, {})
```

The final line is valid. In CPython, `"single"` mode arranges for a non-`None` expression result to be passed to `sys.displayhook`; with the default display hook, this normally displays `5`. A custom display hook or redirected execution environment can change the visible effect. This is an example of why compile mode and execution environment must be considered together.

`eval()` expects an expression code object or expression source. `exec()` is used for statement suites and can also execute a code object compiled in `"single"` mode. Neither is safe for untrusted code.

### 4.5 AST-only compilation and AST transformation

`ast.PyCF_ONLY_AST` asks `compile()` to return an AST rather than bytecode:

```python
import ast

source = "result = 6 * 7\n"
tree = compile(
    source,
    "<ast-demo>",
    "exec",
    flags=ast.PyCF_ONLY_AST,
)
print(type(tree).__name__)  # Module
```

This can be useful when a tool needs compilation-compatible parsing before analysing or transforming the tree. You can also use `ast.parse()` directly for ordinary parsing tasks.

An AST transformer must preserve valid node structure and source locations where required, and the transformed tree must be compiled before it can execute:

```python
import ast

class MultiplyConstants(ast.NodeTransformer):
    def visit_BinOp(self, node):
        node = self.generic_visit(node)
        if (
            isinstance(node.op, ast.Mult)
            and isinstance(node.left, ast.Constant)
            and isinstance(node.right, ast.Constant)
            and isinstance(node.left.value, int)
            and isinstance(node.right.value, int)
        ):
            return ast.copy_location(
                ast.Constant(node.left.value * node.right.value),
                node,
            )
        return node

source = "answer = 6 * 7\n"
tree = ast.parse(source)
tree = MultiplyConstants().visit(tree)
tree = ast.fix_missing_locations(tree)
code = compile(tree, "<transformed>", "exec")

namespace = {}
exec(code, namespace)
print(namespace["answer"])  # 42
```

This toy transformer folds only direct integer constants. Real optimisers must account for semantics, types, exceptions, side effects, and source locations. AST transformation is not automatically semantics-preserving just because the transformed tree compiles.

**When useful:** code instrumentation, domain-specific languages, generated code, educational compiler experiments, and controlled source rewriting.

**Trade-offs:** transformations can make tracebacks confusing, invalidate assumptions made by tools, and introduce correctness or security defects. Keep original source and transformed-source provenance available for debugging.

## 5. Compile-time errors versus runtime errors

The stage at which an error appears narrows the diagnosis.

### 5.1 Syntax and compilation errors

```python
source = "if True print('missing colon')\n"
compile(source, "<bad-syntax>", "exec")
```

This raises `SyntaxError` during parsing/compilation; the code object is not returned. Similar compile-time failures include invalid syntax and certain scope declarations that violate compiler rules.

Encoding errors can occur even earlier, while Python is decoding source bytes. A source file with an invalid encoding declaration or malformed byte sequence may fail before a valid token stream or AST can be produced.

### 5.2 Runtime name and type errors

```python
code = compile("print(missing_name)\n", "<runtime-name>", "exec")
exec(code, {})
```

Compilation succeeds because an unresolved name is not necessarily a syntax error. Execution reaches the name lookup and raises `NameError`.

Likewise:

```python
code = compile("'text' + 10\n", "<runtime-type>", "exec")
exec(code, {})
```

This compiles but raises `TypeError` when the incompatible operands are evaluated.

### 5.3 A practical diagnostic sequence

1. **Cannot parse the file?** Check the traceback, source encoding, syntax, and interpreter version.
2. **Can compile but fails during execution?** Identify the exact executed statement and inspect values, namespaces, and control flow.
3. **Scope-related error?** Inspect the function's assignments and declarations, then use `symtable` and code-object metadata to confirm the compiler's classification.
4. **Only fails on a newer or older Python?** Reduce the case and compare the supported grammar, language changes, and version-specific runtime behaviour.
5. **Tool reports unexpected syntax?** Check whether it is using the intended interpreter version and whether it depends on assumptions about token streams or AST node shapes.

The distinction is useful in production incident response: a syntax error in a deployed module often prevents that module from loading, whereas a runtime exception may affect only a particular request or branch.

## 6. Compiler optimisations and optimisation levels

CPython may optimise generated code while preserving the language's required observable behaviour. Examples include folding some constant expressions and eliminating code that the compiler can prove unreachable. The exact transformations depend on the version and the expression; do not assume every mathematically reducible expression is folded.

For example:

```python
import dis

def constants():
    return 10 * 20

dis.dis(constants)
```

The compiler may represent the multiplication as a constant result rather than emit a runtime multiplication. Confirm with the interpreter under test instead of relying on a fixed disassembly.

Compiler optimisation is not a substitute for algorithmic improvement or profiling. A smaller bytecode sequence does not necessarily execute faster: dispatch costs, object operations, caches, branch behaviour, and the runtime environment all matter.

### 6.1 `-O`, `-OO`, and `__debug__`

CPython's optimisation level can be set from the command line or via `compile(..., optimize=...)`.

- Default level (`0`): normal compilation; `__debug__` is true.
- `-O` / level `1`: removes `assert` statements and sets `__debug__` to false.
- `-OO` / level `2`: also discards docstrings from compiled code.

The removal of assertions is an operationally important semantic difference. **Never use `assert` for validation that must always run**, such as checking external input, permissions, financial constraints, or security invariants. Use explicit conditionals and exceptions for required validation.

Check the behaviour with a tiny script:

```python
# save as optimise_demo.py
print("__debug__ =", __debug__)

def documented():
    """A docstring that may be removed by -OO."""
    assert 2 + 2 == 4
    return "ok"

print("docstring =", documented.__doc__)
```

Run:

```bash
python optimise_demo.py
python -O optimise_demo.py
python -OO optimise_demo.py
```

Expected observations: `__debug__` is true without `-O` and false with `-O` or `-OO`; the function's assertion is omitted at optimisation level 1 or higher; under `-OO`, its docstring is removed. Do not treat assertions as a reliable runtime safety mechanism.

### 6.2 Identifier interning and other implementation optimisations

CPython may intern identifiers or reuse constants as part of compilation and runtime implementation. These behaviours can reduce work or memory, but they are not a basis for equality or identity logic. Use `==` for value equality and `is` for identity checks such as `value is None`.

A small, version-sensitive illustration of constant folding and unreachable-code elimination is:

```python
import dis

def folded():
    return 10 * 20

def unreachable():
    if False:
        print("not reached")
    return 7

dis.dis(folded)
dis.dis(unreachable)
```

On CPython, the compiler commonly folds `10 * 20` and omits the unreachable suite. Verify the actual listing on the target interpreter; do not make application correctness depend on a particular opcode or optimisation pass.

Do not confuse compiler optimisations with the specialising adaptive interpreter. The compiler generates code before or during code loading; the adaptive interpreter may specialise execution based on observed runtime behaviour. The latter is covered in the later runtime lesson on specialisation and JIT.

## 7. `.pyc`, `__pycache__`, and PEP 552

### 7.1 What a bytecode cache is

When importing a Python source module, CPython can store compiled bytecode in a `.pyc` file, commonly beneath a directory such as:

```text
package/
    module.py
    __pycache__/
        module.cpython-312.pyc
```

The cache lets a later import avoid recompiling unchanged source. The filename's interpreter cache tag helps distinguish implementation/version variants (and some build variants when reflected in the tag); it is not, by itself, a universal compatibility guarantee.

A `.pyc` is not a portable executable and should not be treated as a durable cross-version artifact. It contains a header and marshalled code-related data whose compatibility is tied to the Python implementation/version. Never load bytecode from an untrusted source.

**Crucial distinction:** `.pyc` caching primarily reduces import-time compilation work. It does not make a program that is already running execute its bytecode faster simply because the bytecode was loaded from a cache. Runtime performance depends on the program, interpreter, workload, and other factors.

### 7.2 Cache invalidation

A cache must be checked against its source. CPython supports timestamp-based and hash-based invalidation schemes, specified by PEP 552.

- **Timestamp-based caches** record source metadata, notably modification time and size, to determine whether cached bytecode is stale. Because timestamps have finite resolution and metadata can be preserved during copying, timestamp-based invalidation is not the same as proving that source bytes are identical.
- **Hash-based caches** record a hash of source contents. PEP 552 distinguishes checked and unchecked hash-based caches; whether a hash is checked can depend on the cache header and interpreter policy. CPython also exposes the `--check-hash-based-pycs` interpreter option in relevant versions (`default`, `always`, or `never`); check `python -h` and the matching version's documentation before relying on it.

The import machinery decides whether to reuse or regenerate cached bytecode. Details are version-sensitive and should be confirmed against the interpreter and PEP 552. Do not assume that touching a file, preserving timestamps, or copying a `.pyc` across environments always gives the result you expect.

### 7.3 Inspecting cache behaviour

Create `cache_demo.py`:

```python
# cache_demo.py
VALUE = 42
```

Then run:

```bash
python -c "import cache_demo; print(cache_demo.VALUE); print(cache_demo.__cached__)"
```

Inspect the path printed by `__cached__`. The cache may be absent or unwritable depending on interpreter options, filesystem permissions, import mechanism, and environment.

Try a fresh temporary directory for repeatable experiments. Remove only the experiment's own `__pycache__` directory when testing regeneration; do not indiscriminately delete caches across a production environment.

### 7.4 Deployment implications

- **Read-only filesystems:** the interpreter may be unable to write `.pyc` files. Imports can still work from source, but compilation may recur on later starts.
- **`PYTHONDONTWRITEBYTECODE` / `-B`:** suppresses writing bytecode cache files; it does not mean source is executed without compilation.
- **`compileall`:** can precompile Python source during image or package build steps. Ensure it runs with the intended interpreter and that generated artifacts are appropriate for the runtime version.
- **Container layers:** precompiled caches can reduce startup work if they are preserved and compatible, but copying caches across Python versions or build environments is fragile.
- **Hash-based caches:** useful where reproducibility and source-content validation policy matter, but policy choices must be explicit.
- **Security:** `.pyc` files are executable program artifacts. Treat them as trusted code, not as harmless data.

The right policy depends on whether startup latency, image size, reproducibility, read-only operation, or source distribution is the primary constraint. Measure import time before changing cache policy.

## 8. Source-level rules that affect compilation

### 8.1 Encoding declarations and UTF-8 BOM

Python source is decoded before it can be tokenised. In modern Python, UTF-8 is the default source encoding. A coding declaration in the first or second line can specify another supported encoding, subject to the language's placement rules. A UTF-8 byte-order mark (BOM) is also recognised in the relevant source-file context; conflicts between a BOM and encoding declaration can cause an error.

Encoding declarations matter most for source files containing non-ASCII characters or generated files produced by tools with different encoding defaults. Prefer a consistent UTF-8 source policy in new projects and make file-generation tools explicit about encoding.

### 8.2 Future imports

A `from __future__ import ...` statement is a compiler directive for features whose behaviour is introduced or enabled through the future-import mechanism. Such imports are restricted to the beginning of a module, aside from permitted module documentation and comments. The compiler processes them during compilation; they are not ordinary runtime configuration switches.

The available future features and whether they remain necessary vary by Python version. Check the documentation for the target interpreter rather than copying a historical future import into every file.

### 8.3 `__debug__`

`__debug__` is a built-in constant whose value is true under normal execution and false when optimisation is enabled with `-O` or `-OO`. Code guarded by `if __debug__:` can therefore be omitted or simplified during optimised compilation. Do not use this mechanism to enforce required security checks or input validation.

## 9. Source positions, line tables, and diagnostic quality

Python 3.11 introduced fine-grained source position information (PEP 657) for many compiled instructions. Code objects expose `co_positions()` and line-mapping interfaces; tracebacks can use this information to highlight the relevant expression rather than only the entire line.

```python
def divide(total, count):
    return total / count

code = divide.__code__
print("first line:", code.co_firstlineno)

# Each item is a source-position tuple; exact values depend on the function.
for position in code.co_positions():
    print(position)
```

Each tuple is `(start_line, end_line, start_column, end_column)`. Column offsets are measured in UTF-8 bytes, not necessarily Unicode code points; positions can be `None` where information is unavailable. Exact tuples and their number depend on compiler output and Python version. This is why output should be inspected rather than copied into a golden file across versions.

The line table supports traceback and tracing tools. Fine-grained positions improve diagnostics, but they do not guarantee that every instruction has a unique source span or that transformed code will map perfectly to the original source. AST transformers should preserve or repair source locations when possible and test resulting tracebacks.

## 10. Import-time behaviour, frozen modules, and startup diagnostics

Importing a module can involve path searching, reading source or bytecode, compiling source, creating module objects, and executing top-level statements. A slow startup may be caused by expensive imports or module-level work, not only by compilation.

### 10.1 `-X importtime`

Run:

```bash
python -X importtime -c "import json"
```

This asks CPython to report import timing information. Output is diagnostic and timing-dependent; it varies with platform, filesystem cache, interpreter build, dependency graph, and version. Use it to identify expensive import chains, then repeat measurements under representative conditions.

Do not assume the report proves a module is intrinsically slow: parent imports, first-run effects, and the environment contribute to measured time.

### 10.2 `-X dev`

Run:

```bash
python -X dev -c "print('development mode enabled')"
```

Development mode enables additional runtime checks and warnings intended to help development and testing. It can reveal issues that normal execution does not surface as prominently, but it can add overhead and is not a substitute for a production observability plan. Check the version-specific command-line documentation for exactly which checks are enabled.

### 10.3 Frozen modules and `-X frozen_modules`

Some standard-library modules can be frozen into the interpreter as code/data rather than loaded from ordinary source files. Frozen modules can reduce startup filesystem work and are particularly relevant to import bootstrapping. They do not mean all modules are frozen, nor do they eliminate the cost of executing module code.

CPython has exposed a `-X frozen_modules` option in relevant versions/builds to control use of frozen modules. Availability, default behaviour, and interactions with development builds can vary; verify `python -h` and the version-specific docs before depending on it. `importlib._bootstrap` and related import machinery are implementation-sensitive; treat them as private unless the documentation explicitly promises an interface.

The `-X importtime` report is normally written to standard error and can help investigate startup costs, but it does not by itself explain every cost of interpreter startup or native extension initialisation.

## 11. AST transformations and import-time source rewriting

A tool can transform source into an AST, modify it, compile the result, and execute the resulting code. An import hook can perform similar work before a module is executed. Pytest's assertion rewriting is a well-known example of import-time source transformation: assertions in selected test modules are rewritten to provide more informative failure messages.

This technique is powerful but has operational costs:

- transformed source may not match the file a traceback points to;
- transformation can add import latency;
- caches must account for the transformed result and its validity;
- import hooks can conflict with other tooling;
- syntax changes can break transformers tied to a particular AST version;
- rewriting untrusted source does not make that source safe.

Use source rewriting only when the additional behaviour justifies the complexity. Preserve provenance, test against supported Python versions, and make failure modes understandable. For ordinary code generation, explicit generated files or a well-defined build step may be easier to debug than invisible import-time mutation.

## 12. CPython compared with other Python implementations

CPython is the implementation targeted by this lesson. Other implementations can preserve Python language semantics while using different runtime machinery.

- **CPython:** compiles to its own bytecode and executes it in its runtime. It includes the PEG parser, code-object structures, import bytecode caches, and adaptive-interpreter machinery discussed here.
- **PyPy:** has historically used a tracing JIT to optimise hot execution paths. Its runtime and performance profile differ from CPython; CPython bytecode details should not be assumed to apply.
- **GraalPy:** implements Python on the GraalVM ecosystem and can use different compiler/runtime techniques. Compatibility and performance depend on its supported version and environment.
- **MicroPython:** targets constrained devices and implements a subset of Python features with different resource trade-offs. Do not assume full CPython standard-library or introspection compatibility.
- **Jython:** a Python implementation for the JVM; it is not a current mainstream choice for modern Python development and should be treated as a legacy/limited compatibility target rather than assumed equivalent to CPython.

The practical rule is to separate **Python-language guarantees** from **implementation observations**. If a project relies on `dis` output, a private code-object field, CPython's `.pyc` layout, or a CPython-only command-line switch, document that dependency and test the supported interpreter matrix.

## 13. Practical experiments

Keep a small `notes/` directory of scripts and record the interpreter version, command, output, and interpretation for each experiment. Never record only “it worked”: explain what the result demonstrates and what it cannot demonstrate.

### Experiment A — Inspect the whole pipeline

**Question:** What can each public inspection tool tell you about the same source snippet?

**Setup:** Use CPython 3.12, 3.13, or 3.14 and save this as `pipeline_inspect.py`.

```python
import ast
import dis
import io
import symtable
import tokenize

SOURCE = """
factor = 3

def scale(value):
    adjusted = value * factor
    return adjusted
"""

print("== TOKENS ==")
for tok in tokenize.generate_tokens(io.StringIO(SOURCE).readline):
    print(tokenize.tok_name[tok.type], repr(tok.string), tok.start, tok.end)

print("\\n== AST ==")
tree = ast.parse(SOURCE, filename="<pipeline-demo>")
print(ast.dump(tree, indent=2))

print("\\n== SYMBOL TABLE ==")
module_table = symtable.symtable(SOURCE, "<pipeline-demo>", "exec")
for child in module_table.get_children():
    print("block:", child.get_name())
    for name in child.get_identifiers():
        symbol = child.lookup(name)
        print(
            name,
            "local=", symbol.is_local(),
            "global=", symbol.is_global(),
            "referenced=", symbol.is_referenced(),
            "assigned=", symbol.is_assigned(),
        )

print("\\n== CODE OBJECT ==")
module_code = compile(SOURCE, "<pipeline-demo>", "exec")
print("names:", module_code.co_names)
print("constants:", module_code.co_consts)

function_code = next(
    item for item in module_code.co_consts
    if isinstance(item, type(module_code))
)
print("function varnames:", function_code.co_varnames)
print("function names:", function_code.co_names)
print("function freevars:", function_code.co_freevars)
print("function cellvars:", function_code.co_cellvars)

print("\\n== BYTECODE ==")
dis.dis(function_code)
```

**Procedure:**
1. Run `python --version` and record the result.
2. Run `python pipeline_inspect.py`.
3. Identify the tokens for the function name, parameters, multiplication operator, and return statement.
4. Find the `FunctionDef` and its `Return`/`BinOp` structure in the AST.
5. Explain why `value` and `adjusted` are local to `scale`, while `factor` is global.
6. Compare the function code object's names and variable metadata with the bytecode listing.

**Expected observations:** the token list represents the source's lexical pieces; the AST contains a module and a function definition; the symbol table identifies local parameters/assignment targets and a global reference; compilation produces a module code object containing a nested function code object. `dis` shows executable instructions for the function.

**Interpretation:** no single tool explains every stage. Tokenisation shows lexical units, the AST shows syntax structure, `symtable` shows name classification, the code object carries executable data and metadata, and `dis` provides a version-specific bytecode view.

**What this does not prove:** it does not prove that the code has executed, that `factor` will exist when `scale` runs, that the program is correct, or that a particular bytecode listing is stable across Python versions.

### Experiment B — Compare compile-time and runtime failures

**Question:** Which failures happen before execution, and which occur only when the relevant code runs?

**Setup and commands:**

```bash
python -c "compile('if True print(1)', '<syntax>', 'exec')"
python -c "code = compile('print(missing_name)', '<runtime>', 'exec'); exec(code, {})"
python -c "code = compile(\"'a' + 1\", '<type>', 'exec'); exec(code, {})"
```

**Procedure:** run each command separately and compare the exception type and traceback location.

**Expected observations:** the first raises `SyntaxError` during compilation. The second compiles, then raises `NameError` during execution. The third compiles, then raises `TypeError` when the operation executes.

**Interpretation:** the exception stage helps localise the problem. Syntax errors block compilation of that source unit; runtime exceptions depend on executed operations and values.

**What this does not prove:** it does not imply that all `NameError`s are runtime-only in every possible dynamic setup, or that compilation catches all program defects. Static correctness is a separate problem.

### Experiment C — Observe `.pyc` generation and reuse

**Question:** Does importing source create a cache, and what does the cache tell you about execution speed?

**Setup:** create a temporary directory with `cache_demo.py` containing `VALUE = 42`.

**Procedure:**
1. Run `python -c "import cache_demo; print(cache_demo.__cached__)"` from that directory.
2. Inspect the reported cache path and its timestamp.
3. Run the same import in a new process.
4. Remove only that temporary experiment's `__pycache__` directory and import again.
5. Optionally repeat with `python -B -c "import cache_demo; print(cache_demo.__cached__)"`.

**Expected observations:** where bytecode writing is enabled and permitted, an import commonly creates a version-tagged `.pyc` file. A later import may reuse it if it is valid. `-B` prevents writing bytecode caches, although the module can still be compiled in memory.

**Interpretation:** the cache reduces repeated source-compilation work during import. A second import in the same process usually reuses the module in `sys.modules`, which is a different mechanism from reading `.pyc`.

**What this does not prove:** it does not prove that all imports write caches, that every cache is valid, or that the already-running process executes faster due to `.pyc`. Filesystem permissions, import loaders, invalidation mode, and interpreter version affect the result.

### Experiment D — Demonstrate scope classification

**Question:** Why can adding an assignment change a read from a global lookup into an unbound-local failure?

**Setup:**

```python
x = 10

def read_then_assign():
    print(x)
    x = 20

print("global x:", x)
read_then_assign()
```

**Procedure:** run the script and observe the exception. Then use `symtable.symtable()` to inspect the function's `x` symbol, and remove the assignment to compare behaviour.

**Expected observations:** with the assignment present, `x` is classified as local in the function and the read fails with `UnboundLocalError`. Without the assignment, the function reads the module-level `x`.

**Interpretation:** scope classification is determined from the whole code block during compilation, not from the order in which statements happen to execute.

**What this does not prove:** it does not mean every missing name causes `UnboundLocalError`; a name classified as global and absent at runtime normally raises `NameError`.

### Experiment E — Inspect fine-grained positions

**Question:** What source-position metadata does a compiled function expose?

**Setup:**

```python
def ratio(numerator, denominator):
    return numerator / denominator

print("line:", ratio.__code__.co_firstlineno)
print("positions:")
for item in ratio.__code__.co_positions():
    print(item)
```

**Procedure:** run on CPython 3.12–3.14, record the version, and compare the position entries with the function's source lines.

**Expected observations:** `co_positions()` yields source-position tuples for compiled instructions; exact entries and count vary with the compiler and version.

**Interpretation:** fine-grained positions support better diagnostics, coverage, and debugger displays.

**What this does not prove:** it does not make the encoded line table a stable external format or guarantee that transformed code maps perfectly to original source.

### Experiment F — Measure import costs rather than guessing

**Question:** Which imports contribute to startup time in a real command?

**Setup/command:**

```bash
python -X importtime -c "import json; import pathlib"
```

**Procedure:** record the output, identify modules with comparatively large cumulative times, and repeat a few times under the same conditions. Compare with a representative application command, not only a toy import.

**Expected observations:** CPython reports import timing lines with self and cumulative timing information. Values vary by machine, filesystem cache, build, and run.

**Interpretation:** the output helps identify where to investigate lazy imports or expensive module-level work.

**What this does not prove:** it does not prove a module should be removed, that the reported timing is a stable benchmark, or that all startup costs are import costs.

## 14. Common misconceptions and failure modes

### “Python interprets source one line at a time.”

**Correction:** CPython compiles source into code objects and executes bytecode. Interactive input can be compiled one entered unit at a time, but that does not make the execution model a simple source-line interpreter.

### “A `.pyc` makes my running program faster.”

**Correction:** `.pyc` primarily avoids recompiling imported source in later processes. It is not a runtime speed switch for an already-running program. Measure the import path and the actual workload separately.

### “If `ast.parse()` succeeds, the program is valid.”

**Correction:** parsing success is not a proof of successful compilation, name availability, type correctness, or runtime correctness. Later compiler validation and runtime execution can still fail.

### “`UnboundLocalError` means Python couldn't find a global variable.”

**Correction:** it normally means the name was classified as local in the current function and was read before a local value was bound. A missing global normally produces `NameError`.

### “Fewer bytecode instructions always means faster code.”

**Correction:** bytecode count alone ignores dispatch, object allocation, cache behaviour, native operations, branch behaviour, and workload. Use measurement such as `timeit` or `pyperf` for performance claims.

### “`assert` is safe for input validation.”

**Correction:** `-O` and `-OO` remove assertions. Use explicit validation and exceptions for conditions that must always be enforced.

### “Bytecode is a stable interface.”

**Correction:** opcode names, arguments, offsets, cache layout, code-object fields, and compiler choices change across releases. Use `dis` for investigation and teaching, not as a portable contract.

### “A restricted `exec` namespace is a secure sandbox.”

**Correction:** arbitrary code execution is dangerous, and reducing the supplied globals dictionary does not create a robust sandbox. Do not execute untrusted source in-process as a validation technique.

### “All Python implementations use CPython's parser, bytecode, and caches.”

**Correction:** implementations differ. Keep language semantics separate from implementation-specific mechanisms.

## 15. Troubleshooting checklist

When an inspection result surprises you:

1. **Confirm the interpreter:** `python --version` and `python -c "import sys; print(sys.implementation); print(sys.executable)"`.
2. **Reproduce with a minimal source string:** remove unrelated imports and application state.
3. **Inspect stages independently:** tokenise, parse, inspect the symbol table, compile, then execute only if safe.
4. **Check the exact mode:** `exec`, `eval`, and `single` have different input and display semantics.
5. **Record the environment:** version, operating system, build, optimisation level, and relevant flags.
6. **Avoid hard-coded internals:** compare concepts and documented attributes, not numeric opcodes or private structure layouts.
7. **For import problems:** check `module.__file__`, `module.__cached__`, write permissions, `sys.dont_write_bytecode`, and import-time output.
8. **For confusing tracebacks:** check whether the source changed after compilation and whether a transformer rewrote it.
9. **For performance claims:** separate cold startup, warm imports, and steady-state execution; repeat measurements and use representative workloads.
10. **For security:** never compile-and-execute untrusted source merely to see whether it is syntactically valid. Parsing is not a sandbox.

## 16. Summary and concept map

The pipeline can be remembered as **lexical structure → grammatical structure → name classification → executable representation → runtime evaluation**.

```text
source bytes
  └─ encoding detection
      └─ tokens (`tokenize`)
          └─ grammar / PEG parser
              └─ AST (`ast`)
                  └─ scope analysis (`symtable`)
                      └─ compilation (`compile`)
                          └─ code object (`co_*`, bytecode)
                              └─ evaluation (`exec` / normal execution)
                                  └─ runtime values, effects, exceptions
```

Key takeaways:

- CPython compiles source to bytecode stored in code objects, then evaluates that code.
- `tokenize`, `ast`, `symtable`, `compile`, and `dis` expose different views; none alone proves the program is correct.
- Scope classification occurs at compile time; an unbound local is a runtime failure caused by that classification.
- `.pyc` caching can reduce repeated import compilation but does not accelerate an already-running program by itself.
- PEP 552 defines timestamp- and hash-based cache invalidation choices.
- Optimisation flags can remove assertions and docstrings; never rely on `assert` for mandatory validation.
- Fine-grained positions improve diagnostics, while bytecode and private internals remain version-sensitive.
- Source rewriting and import hooks are powerful but increase complexity, import cost, and debugging burden.
- Confirm claims on the exact CPython version and build you deploy.

## 17. Self-check questions with answers

### 1. At which stage is `UnboundLocalError` determined and why?

**Answer:** The name's local classification is determined during compile-time symbol-table/scope analysis. The exception itself is raised at runtime when execution attempts to read that local before a value has been bound. An assignment anywhere in a function body normally makes the name local throughout that function unless `global` or `nonlocal` changes the rule.

### 2. What does a `.pyc` contain and when is it regenerated?

**Answer:** A `.pyc` is a version-specific cache containing a header and marshalled compiled-code data. During import, CPython checks cache validity using the applicable timestamp- or hash-based invalidation scheme. If the cache is missing, invalid, stale, incompatible, or not usable under the loader's policy, the source may be compiled again and a cache may be written if permitted. Not every loader or environment behaves identically.

### 3. Write a script that shows the pipeline stages for a small function and explain every difference between `exec` and `eval` mode.

**Answer / model approach:** Use Experiment A to print tokens, AST, symbol-table entries, code-object fields, and bytecode for a small function. For compile modes:
- `exec` accepts a suite of statements and produces a code object suitable for statement execution; `exec()` executes it and does not return the value of a final expression.
- `eval` accepts a single expression; `eval()` evaluates it and returns the expression's value.
- `single` is for a single interactive statement and supports interactive display-hook behaviour; it is not equivalent to a general module suite.
- `compile(..., flags=ast.PyCF_ONLY_AST)` returns an AST rather than a code object.
- All modes are subject to syntax and compilation validation, and none makes untrusted source safe to execute.

## References and further verification

Prefer official documentation and release-specific sources when checking version-sensitive behaviour:

- Python language reference, *Lexical analysis*: https://docs.python.org/3/reference/lexical_analysis.html
- Python language reference, *Execution model*: https://docs.python.org/3/reference/executionmodel.html
- `tokenize`: https://docs.python.org/3/library/tokenize.html
- `ast`: https://docs.python.org/3/library/ast.html
- `symtable`: https://docs.python.org/3/library/symtable.html
- `compile`, `eval`, and `exec`: https://docs.python.org/3/library/functions.html
- Code objects and data model: https://docs.python.org/3/reference/datamodel.html#code-objects
- `dis`: https://docs.python.org/3/library/dis.html
- `py_compile` and `compileall`: https://docs.python.org/3/library/py_compile.html and https://docs.python.org/3/library/compileall.html
- PEP 552, *Deterministic pycs*: https://peps.python.org/pep-0552/
- PEP 657, *Fine-grained error locations in tracebacks*: https://peps.python.org/pep-0657/
- PEP 701, *Syntactic formalization of f-strings*: https://peps.python.org/pep-0701/
- CPython grammar source for the matching release: `Grammar/python.gram`
- CPython compiler and evaluation implementation: inspect the matching release's `Python/` and `Objects/` source directories. File names and internal function boundaries can change; verify against the release tag rather than relying on a moving development branch.

For a specific behaviour, record the Python version and test a minimal example. Documentation describes supported interfaces; CPython source can explain implementation details, but private implementation details are not automatically compatibility guarantees.
