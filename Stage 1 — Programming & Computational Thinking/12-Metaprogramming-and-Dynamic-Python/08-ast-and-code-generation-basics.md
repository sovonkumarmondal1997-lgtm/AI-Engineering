# AST and Code-Generation Basics

> **Stage 1 · Module 12 — Metaprogramming and Dynamic Python · Lesson 08**  
> **Audience:** Python developers progressing from syntax fundamentals to source-analysis tooling, codemods, and controlled code generation.  
> **Baseline:** Python 3.12+ is a useful learning target. AST details are version-sensitive; this lesson calls out important differences rather than treating the current interpreter's tree as universal.

## Learning outcomes

By the end of this lesson, you should be able to:

- Explain the source-processing pipeline: tokenization, parsing, AST analysis, transformation, compilation, and execution.
- Inspect Python syntax with `ast.parse()` and `ast.dump()` and recognize common node types.
- Implement correct `ast.NodeVisitor` traversals and static checks for `print`, missing docstrings, bare `except`, and mutable default arguments.
- Rewrite a deliberately narrow expression grammar with `ast.NodeTransformer`, repair locations, and compile the result.
- Distinguish source transformation from executing the transformed program.
- Use `ast.literal_eval()`, `symtable`, and `tokenize` for their appropriate jobs.
- Explain why `ast.unparse()` is not a formatting-preserving round trip and when a concrete syntax tree (CST), such as LibCST, is a better fit.
- Build and test a repository lint rule/codemod with clear limits and version-aware behavior.

---

# 1. Prerequisites and mental model

## 1.1 What an AST is

An **abstract syntax tree (AST)** is a structured representation of a program's syntax. It captures meaningful syntactic relationships while discarding many surface details such as comments, whitespace, and the exact spelling choices that do not affect the parsed structure.

For example, these statements differ in formatting but have equivalent expression structure:

```python
total=price*(1+tax)
```

```python
total = price * (1 + tax)
```

An AST is not a full semantic model. It does not by itself resolve every name to the object it refers to, prove types, or determine whether a call is safe. Those tasks need additional analysis and often runtime context.

## 1.2 The source-processing pipeline

A useful conceptual pipeline is:

```text
source text
   │
   ▼
tokenization (tokenize)
   │
   ▼
parsing (grammar → AST)
   │
   ├── static analysis (read the tree)
   │
   └── transformation (produce a changed tree)
             │
             ▼
       compilation (AST/source → code object)
             │
             ▼
       execution (run code object in a namespace)
```

| Stage | Main question | Typical tools | Important limitation |
|---|---|---|---|
| Tokenization | Which lexical tokens and comments occur, and where? | `tokenize` | Tokens alone do not encode the complete nested syntax structure. |
| Parsing | Is the source syntactically valid, and what syntax tree represents it? | `ast.parse()` | Parsing is not full name resolution or type checking. |
| Analysis | What patterns and relationships occur in the tree? | `NodeVisitor`, `ast.walk`, `symtable` | A syntactic pattern is not automatically proof of runtime behavior. |
| Transformation | How should selected syntax nodes change? | `NodeTransformer` or direct AST construction | A valid transformed tree can still change semantics or be unsafe. |
| Compilation | Can the source/tree be turned into executable code for a mode? | `compile()` | Compilation does not mean the code is safe or has run. |
| Execution | What happens when the code object runs in an environment? | `exec()`, function calls | Execution can perform arbitrary side effects; do not run untrusted code as a shortcut for analysis. |

The compiler internally performs additional work, including symbol-table construction and bytecode generation. The exact internal pipeline is an implementation detail, but the conceptual distinctions above are stable and useful.

## 1.3 Why regex is not enough for structural source analysis

Regular expressions are useful for simple textual searches, but Python syntax is nested and context-sensitive enough that regex-only checks are fragile. A pattern for `print(` can miss whitespace or comments, match text inside a string, or mis-handle nested expressions. A regex looking for `except:` can also match a comment or string. AST-based checks operate on parsed syntax nodes, so they can distinguish a real `ast.Call` from text that merely looks like one.

ASTs have their own limit: because comments and much formatting are discarded, use `tokenize` or a CST when the requirement depends on exact tokens, comments, or preserving the original text.

## 1.4 A safe mental model

Keep these operations separate:

1. **Parse** source to discover its structure.
2. **Analyze** without changing it.
3. **Transform** selected nodes according to a narrow, documented rule.
4. **Compile** the transformed tree to validate it as executable syntax.
5. **Execute** only when necessary and only in an appropriately trusted environment.

Never treat “I can parse it,” “I can compile it,” and “it is safe to execute” as equivalent statements.

---

# 2. Inspecting ASTs

## 2.1 Parse source and inspect the tree

```python
import ast

source = "total = price * (1 + tax)"
tree = ast.parse(source)
print(type(tree).__name__)
print(ast.dump(tree, indent=2))
```

Representative output (node formatting is stable enough for learning, but exact dumps may vary with Python versions):

```text
Module
Module(
  body=[
    Assign(
      targets=[
        Name(id='total', ctx=Store())],
      value=BinOp(
        left=Name(id='price', ctx=Load()),
        op=Mult(),
        right=BinOp(
          left=Constant(value=1),
          op=Add(),
          right=Name(id='tax', ctx=Load()))))])
```

`ast.dump(tree, indent=2, include_attributes=True)` also includes source locations when available. On Python 3.13+, empty fields are omitted by default; `show_empty=True` can display them when that keyword is supported. Python 3.15 also omits optional `Load()` context values from the default dump, so the illustrative output below matches Python 3.12–3.14 more closely than 3.15. The dump is version-sensitive. Use it for debugging and learning; avoid asserting against the entire textual dump in long-lived tests unless the exact representation is what you intend to test. See the [versioned `ast` documentation](https://docs.python.org/3.15/library/ast.html) for the target interpreter's behavior.

## 2.2 Common node types

Consider:

```python
class Invoice:
    def total(self, price, tax=0.2):
        subtotal = price * (1 + tax)
        if subtotal > 0:
            print(subtotal)
        for _ in range(1):
            return subtotal
```

Common nodes include:

- `Module`: module-level body.
- `ClassDef`: class declaration and its body.
- `FunctionDef` / `AsyncFunctionDef`: function declarations.
- `Assign`: assignment such as `x = expression`.
- `Call`: a call expression such as `print(subtotal)`.
- `Name`: an identifier such as `subtotal`; `ctx` distinguishes reading (`Load`) from binding (`Store`) and deletion (`Del`).
- `Attribute`: attribute access such as `obj.value`.
- `Constant`: literals such as `42`, `"hello"`, `None`, and booleans.
- `BinOp`: binary expression such as `a + b`; the operator is a child node such as `Add` or `Mult`.
- `If`, `For`, `While`, `Try`, `With`, `Match`: compound statements.
- `Return`: return statement.

A node is a Python object with fields, not a string containing source. Inspect fields with `ast.iter_fields(node)` or `ast.dump()`.

## 2.3 Expression mode, statement mode, and fragments

`ast.parse()` supports modes:

- `mode="exec"` (default): a module containing statements.
- `mode="eval"`: one expression, represented by `ast.Expression`.
- `mode="single"`: one interactive statement, represented by `ast.Interactive`.

```python
import ast

expr = ast.parse("a.b(c)", mode="eval")
print(ast.dump(expr, indent=2))
```

Expected output:

```text
Expression(
  body=Call(
    func=Attribute(
      value=Name(id='a', ctx=Load()),
      attr='b',
      ctx=Load()),
    args=[
      Name(id='c', ctx=Load())]))
```

This is the representative tree for `a.b(c)` on Python 3.12–3.14: an outer `Call`; its `func` is an `Attribute`; that attribute's `value` is `Name('a')`; and the call has one positional argument `Name('c')`. On Python 3.15, the default `ast.dump()` omits optional `Load()` context values, so the displayed text differs even though the source structure is the same.

## 2.4 Syntax errors are parsing failures

```python
import ast

try:
    ast.parse("def broken(:\n    pass\n")
except SyntaxError as exc:
    print(type(exc).__name__)
    print(exc.lineno)
```

Expected output:

```text
SyntaxError
1
```

`SyntaxError` may expose `filename`, `lineno`, `offset`, `end_lineno`, `end_offset`, and source text. Tooling should report these details when useful. Do not catch every exception and silently continue; a parser failure means the tool could not analyze that source unit.

## 2.5 `ast.literal_eval()` is not general evaluation

`ast.literal_eval()` accepts a limited set of literal structures: strings, bytes, numbers, tuples, lists, dictionaries, sets, booleans, `None`, and certain literal-only expressions. It does not evaluate names, calls, attribute access, or arbitrary operators as a general expression engine would.

```python
import ast

print(ast.literal_eval("{'region': 'ap-south-1', 'retries': 3}"))
for source in ("1 + 2", "open('secret.txt')", "settings.region"):
    try:
        ast.literal_eval(source)
    except (ValueError, SyntaxError) as exc:
        print(type(exc).__name__)
```

Expected output:

```text
{'region': 'ap-south-1', 'retries': 3}
ValueError
ValueError
ValueError
```

The exact exception class can depend on the invalid form and Python version; the key behavior is rejection. `literal_eval` avoids executing arbitrary Python expressions, but it is not a complete resource-exhaustion defense: hostile inputs can still consume substantial CPU, memory, or stack depth. Bound input size and handle errors.

---

# 3. Traversing nodes

## 3.1 `ast.NodeVisitor`

Subclass `ast.NodeVisitor` to inspect a tree without modifying it. When a matching `visit_<NodeType>()` method exists, it is called for that node. If your method needs descendants visited, call `self.generic_visit(node)` or explicitly visit selected child nodes. Omitting this call is a common source of missed nested constructs.

```python
import ast

class CallReporter(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            print(f"call-name={node.func.id} line={node.lineno}")
        elif isinstance(node.func, ast.Attribute):
            print(f"call-attribute={node.func.attr} line={node.lineno}")
        self.generic_visit(node)

source = """
def outer():
    print(helper(1))

class Worker:
    def run(self):
        service.send('ready')
"""
CallReporter().visit(ast.parse(source))
```

Expected output:

```text
call-name=print line=3
call-name=helper line=3
call-attribute=send line=7
```

The `generic_visit()` call reaches nested calls such as `helper(1)` inside `print(helper(1))`. It also traverses nested classes and functions. A visitor that deliberately wants to stop at a boundary may omit it, but should do so intentionally and document that behavior.

## 3.2 `ast.walk()`

`ast.walk(node)` yields all descendant nodes in no guaranteed semantic/source order. It is concise for simple inventory queries:

```python
import ast

tree = ast.parse("x = f(g())")
print(sum(isinstance(node, ast.Call) for node in ast.walk(tree)))
```

Expected output:

```text
2
```

Use a visitor when order, context, reporting details, or custom traversal behavior matters. Do not assume `ast.walk()` yields nodes in source order.

## 3.3 Nested scopes and class bodies

AST traversal follows syntactic containment. A nested function is a child of the outer function's body; a nested class is a child of the containing body. A generic visitor sees both. This does **not** mean every nested name belongs to the same lexical scope: scope-aware checks must model function, class, lambda, comprehension, and module boundaries where relevant.

Example inventory:

```python
import ast

source = """
def outer():
    class Inner:
        def method(self):
            def local():
                return 1
            return local()
    return Inner()
"""

class Definitions(ast.NodeVisitor):
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        print(f"function:{node.name}:{node.lineno}")
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        print(f"class:{node.name}:{node.lineno}")
        self.generic_visit(node)

Definitions().visit(ast.parse(source))
```

Expected output:

```text
function:outer:2
class:Inner:3
function:method:4
function:local:5
```

A visitor method for a node type that does not call `generic_visit()` will skip its descendants. For example, if `visit_ClassDef()` prints the class and returns without calling `generic_visit()`, it will not report methods inside the class.

## 3.4 Async functions, lambdas, and other forms

A complete checker should decide which forms it supports. Functions can be `FunctionDef` or `AsyncFunctionDef`; lambdas are `Lambda` nodes and do not have a docstring statement body. Comprehensions have their own nodes (`ListComp`, `SetComp`, `DictComp`, `GeneratorExp`). Pattern matching uses `Match` and related nodes on supported Python versions. Do not assume that checking only `FunctionDef` covers every callable or every modern syntax form.

---

# 4. Writing static checks

Static checks report syntactic patterns without executing the inspected code. They can be intentionally conservative: a linter may report a possible issue without proving that the runtime behavior will be wrong.

## 4.1 Calls to `print`

A basic syntactic check can report calls whose function is the unqualified name `print`:

```python
import ast

class PrintCallChecker(ast.NodeVisitor):
    def __init__(self) -> None:
        self.lines: list[int] = []

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            self.lines.append(node.lineno)
        self.generic_visit(node)

source = "print('top')\nlogger.print('not the builtin name')\nprint(value)\n"
checker = PrintCallChecker()
checker.visit(ast.parse(source))
print(checker.lines)
```

Expected output:

```text
[1, 3]
```

This rule does not prove the builtin `print` is being called: code can shadow `print`, and `builtins.print` is an `Attribute`, not a `Name`. A project rule may intentionally flag syntax rather than resolve runtime bindings.

## 4.2 Missing docstrings

`ast.get_docstring(node)` returns a docstring for supported module, class, and function nodes when the first body statement is a string literal expression.

```python
import ast

class MissingDocstrings(ast.NodeVisitor):
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if ast.get_docstring(node) is None:
            print(f"missing function docstring: {node.name}:{node.lineno}")
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if ast.get_docstring(node) is None:
            print(f"missing function docstring: {node.name}:{node.lineno}")
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if ast.get_docstring(node) is None:
            print(f"missing class docstring: {node.name}:{node.lineno}")
        self.generic_visit(node)

source = """
class Service:
    def run(self):
        \"\"\"Run the service.\"\"\"
        return 1

    async def stop(self):
        pass
"""
MissingDocstrings().visit(ast.parse(source))
```

Expected output:

```text
missing class docstring: Service:2
missing function docstring: stop:7
```

A production rule should clarify whether module docstrings, private functions, test functions, generated code, and abstract methods are exempt. The sample intentionally reports every class and function without a docstring, including private methods if present.

## 4.3 Bare `except:` handlers

A bare exception handler is represented by an `ExceptHandler` whose `type` is `None`:

```python
import ast

class BareExceptChecker(ast.NodeVisitor):
    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.type is None:
            print(f"bare except at line {node.lineno}")
        self.generic_visit(node)

source = """
try:
    run()
except:
    recover()
except ValueError:
    handle_value_error()
"""
BareExceptChecker().visit(ast.parse(source))
```

Expected output:

```text
bare except at line 4
```

A bare handler can catch `KeyboardInterrupt` and `SystemExit` as well as ordinary exceptions. Prefer specific exception classes or `except Exception` when that is the intended boundary. The linter should not automatically rewrite every bare handler without understanding its recovery behavior.

## 4.4 Complete visitor for mutable default arguments

A function default expression is evaluated when the function definition executes, not on each call. A mutable object used as a default can therefore be shared between calls. The following visitor checks both positional defaults and keyword-only defaults, reports line numbers, and descends into nested definitions.

The rule below is deliberately syntactic: it flags list, dict, and set literals, plus zero-argument calls to `list()`, `dict()`, or `set()`. It does not flag every possible mutable expression (for example `DEFAULTS` or `make_list()`), because deciding mutability and side effects would require deeper analysis. The constructor-call check can produce a false positive if a name such as `set` is shadowed. It also ignores immutable tuple literals, even though a tuple can contain mutable objects; a stricter rule could recursively inspect tuple elements.

```python
import ast

class MutableDefault:
    def __init__(self, function: str, parameter: str, line: int) -> None:
        self.function = function
        self.parameter = parameter
        self.line = line

    def __repr__(self) -> str:
        return (
            f"MutableDefault(function={self.function!r}, "
            f"parameter={self.parameter!r}, line={self.line})"
        )


class MutableDefaultVisitor(ast.NodeVisitor):
    """Find mutable container literals and empty constructor calls in functions."""

    def __init__(self) -> None:
        self.issues: list[MutableDefault] = []

    def _check(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        positional = [*node.args.posonlyargs, *node.args.args]
        # Positional defaults align with the final N positional parameters.
        if node.args.defaults:
            parameters = positional[-len(node.args.defaults):]
            for parameter, default in zip(parameters, node.args.defaults):
                self._record(node.name, parameter.arg, default)

        # Keyword-only defaults align one-to-one with kwonlyargs; None means required.
        for parameter, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
            if default is not None:
                self._record(node.name, parameter.arg, default)

    def _record(self, function: str, parameter: str, default: ast.expr) -> None:
        is_container_literal = isinstance(default, (ast.List, ast.Dict, ast.Set))
        is_empty_builtin_constructor = (
            isinstance(default, ast.Call)
            and isinstance(default.func, ast.Name)
            and default.func.id in {"list", "dict", "set"}
            and not default.args
            and not default.keywords
        )
        if is_container_literal or is_empty_builtin_constructor:
            self.issues.append(
                MutableDefault(function, parameter, default.lineno)
            )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check(node)
        self.generic_visit(node)  # required to find nested functions/classes

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check(node)
        self.generic_visit(node)


source = """
def outer(a, b=[], *, options={}, frozen=()):
    def inner(values=set()):
        return values
    class Nested:
        def method(self, cache=[]):
            return cache
    return inner

async def async_job(items=[]):
    return items
"""
visitor = MutableDefaultVisitor()
visitor.visit(ast.parse(source))
for issue in visitor.issues:
    print(issue)
```

Expected output:

```text
MutableDefault(function='outer', parameter='b', line=2)
MutableDefault(function='outer', parameter='options', line=2)
MutableDefault(function='inner', parameter='values', line=3)
MutableDefault(function='method', parameter='cache', line=6)
MutableDefault(function='async_job', parameter='items', line=10)
```

Why the argument alignment matters: `def f(a, b=1, c=[])` has two defaults corresponding to `b` and `c`, not `a` and `b`. Keyword-only defaults use `None` in `kw_defaults` to represent a required keyword-only parameter. The visitor handles both forms and traverses nested definitions. It reports the default expression's line, which is usually the definition line but may differ for a multiline default.

A robust production checker should add tests for positional-only parameters, `*args`, keyword-only arguments, async functions, nested functions, and nested classes. It should also state whether it flags only literal mutable containers or broader expressions.

## 4.5 Combining rules into diagnostics

Real linters usually collect structured diagnostics rather than printing inside visitors. A diagnostic record can include rule ID, filename, line, column, message, and optional fix. Keeping analysis separate from presentation makes the checker easier to test, reuse in an editor, or integrate into CI.

Avoid automatic fixes unless the rule can produce a semantics-preserving change. For example, changing `items=[]` to `items=None` usually requires also changing the function body to initialize a new list; simply replacing the default expression is not sufficient.

---

# 5. Transforming syntax trees

## 5.1 `ast.NodeTransformer`

`ast.NodeTransformer` is a visitor designed to change trees. A `visit_<NodeType>()` method may return:

- the original node, possibly modified;
- a replacement node;
- `None` to remove a node from a statement list where removal is supported; or
- a list of nodes for supported statement-list positions.

For child nodes to be transformed, call `generic_visit()` unless the method manually visits the relevant children. A transformation should define its input grammar and unsupported cases. “Rewrite all similar-looking code” is not a sufficient specification.

## 5.2 Carefully defined expression rewrite: `x ** 2` to `x * x`

This example rewrites only a power expression whose right operand is the integer literal `2`, excluding booleans. It recursively visits children first, so it can rewrite nested forms. It does not rewrite other exponents, negative-two syntax (`x ** -2` has a `UnaryOp` right operand), or arbitrary source strings.

**Important semantic caveat:** `x ** 2` and `x * x` are not guaranteed to be equivalent for arbitrary Python objects. User-defined operators, NumPy-like arrays, decimals, and side effects can make them behave differently. Use this as a controlled codemod only where the project contract guarantees numeric semantics and multiplication behavior; do not present it as a universal optimization.

```python
import ast
import copy

class SquarePowerToMultiply(ast.NodeTransformer):
    """Rewrite `value ** 2` to `value * value` for a narrow syntax pattern."""

    def visit_BinOp(self, node: ast.BinOp) -> ast.expr:
        node = self.generic_visit(node)  # transform nested expressions first
        if (
            isinstance(node.op, ast.Pow)
            and isinstance(node.right, ast.Constant)
            and type(node.right.value) is int
            and node.right.value == 2
        ):
            replacement = ast.BinOp(
                left=node.left,
                op=ast.Mult(),
                right=copy.deepcopy(node.left),
            )
            # A structural copy avoids reusing one AST object in two positions,
            # but the expression is still evaluated twice at runtime.
            return ast.copy_location(replacement, node)
        return node

source = "result = value ** 2\nnested = (value ** 2) ** 2\nother = value ** 3\n"
tree = ast.parse(source)
rewritten = SquarePowerToMultiply().visit(tree)
rewritten = ast.fix_missing_locations(rewritten)
print(ast.unparse(rewritten))
compile(rewritten, "<square-codemod>", "exec")
```

Expected output (formatting is generated by `ast.unparse()`):

```python
result = value * value
nested = value * value * (value * value)
other = value ** 3
```

This exact rewrite evaluates `value` twice instead of once. The code above deliberately demonstrates that risk; for a side-effecting expression such as `next(iterator) ** 2`, the transformation changes behavior. A safer codemod must either restrict the operand to a known-pure grammar (for example a simple `Name` or a literal) or introduce a temporary in a context where that is valid. The production project later in this lesson restricts the operand to a `Name` and avoids the double-evaluation problem for the chosen input grammar.

## 5.3 A safer transformer for a narrow grammar

This version rewrites `NAME ** 2` only when the left operand is a simple identifier. A `Name` read has no expression-level side effect, though the name's binding and overloaded `__mul__` semantics can still mean the result differs from exponentiation. The transformation remains a project-specific codemod, not a universal equivalence.

```python
import ast

class NameSquareToMultiply(ast.NodeTransformer):
    """Rewrite `name ** 2` into `name * name`; leave other operands unchanged."""

    def visit_BinOp(self, node: ast.BinOp) -> ast.expr:
        node = self.generic_visit(node)
        if (
            isinstance(node.op, ast.Pow)
            and isinstance(node.left, ast.Name)
            and isinstance(node.right, ast.Constant)
            and type(node.right.value) is int
            and node.right.value == 2
        ):
            replacement = ast.BinOp(
                left=node.left,
                op=ast.Mult(),
                right=ast.Name(id=node.left.id, ctx=ast.Load()),
            )
            return ast.copy_location(replacement, node)
        return node

source = "a = number ** 2\nb = obj.number ** 2\nc = number ** -2\nd = number ** 3\n"
tree = NameSquareToMultiply().visit(ast.parse(source))
tree = ast.fix_missing_locations(tree)
print(ast.unparse(tree))
compile(tree, "<name-square>", "exec")
```

Expected output:

```python
a = number * number
b = obj.number ** 2
c = number ** (-2)
d = number ** 3
```

The attribute expression and unsupported exponents remain unchanged. `ast.unparse()` may add parentheses or choose different spacing; this is a generated rendering, not the original source.

## 5.4 Source locations and `ast.fix_missing_locations()`

Most executable AST nodes need location metadata. A node parsed from source normally has `lineno`, `col_offset`, and often `end_lineno` and `end_col_offset`. Newly constructed nodes may lack them. `ast.copy_location(new, old)` copies the available location fields from one node to another; `ast.fix_missing_locations(tree)` recursively fills missing location attributes using parent locations.

A common pattern is:

```python
replacement = ast.Constant(value=0)
replacement = ast.copy_location(replacement, original_node)
```

or, after constructing an entire tree:

```python
tree = ast.fix_missing_locations(tree)
```

`fix_missing_locations()` does not infer ideal source positions for a transformation; it fills missing values well enough for compilation and tracebacks. If accurate diagnostics matter, copy locations thoughtfully and preserve end positions where supported. Column offsets in AST nodes are UTF-8 byte offsets, not necessarily Unicode character indices. Do not treat them as ordinary Python string indexes for non-ASCII source.

## 5.5 Transforming statements versus expressions

A transformer can replace an expression with another expression, or replace a statement-list node with a statement or list of statements where supported. However, inserting a statement into an expression context is not valid. For example, a temporary assignment cannot simply replace the expression in `return f(x)`. The surrounding scope and control flow determine whether a rewrite is possible.

Prefer local, structure-preserving transformations. If a rewrite needs to introduce names, handle name collisions, preserve evaluation order, and reason about scopes, the problem is significantly harder than replacing one expression node.

## 5.6 `ast.unparse()` does not preserve original text

`ast.unparse()` (available since Python 3.9) generates source code that reparses to an equivalent AST for supported constructs. It does **not** promise to preserve:

- comments;
- whitespace, indentation choices, or blank lines;
- quote style;
- redundant parentheses;
- exact formatting or line wrapping;
- source-level details that are absent from the AST.

For example, a comment between expressions usually does not appear in the AST at all, so `ast.unparse()` cannot reconstruct it. Use `ast.unparse()` for inspection, generated source, or debugging; use a CST-based tool when preserving comments and formatting is a requirement.

## 5.7 Invalid and unsupported transformation inputs

A transformer should be tested against:

- valid inputs it is meant to change;
- valid inputs it must leave unchanged;
- invalid source that fails before transformation;
- node forms outside its documented grammar;
- transformed trees that fail compilation;
- semantic edge cases such as side effects and overloaded operators.

Do not silently interpret unsupported syntax as supported. A codemod can leave it unchanged, emit a diagnostic, or fail closed—choose and document one policy.

---

# 6. Compiling transformed code

## 6.1 `compile()` and code objects

`compile()` accepts source text, an AST, or an AST/statement object and returns a code object when compilation succeeds. `mode` must match the input shape:

- `"exec"`: module-level statements;
- `"eval"`: a single expression;
- `"single"`: one interactive statement.

```python
import ast

source = "answer = 6 * 7"
tree = ast.parse(source)
code = compile(tree, filename="example.py", mode="exec")
namespace: dict[str, object] = {}
exec(code, namespace)
print(namespace["answer"])
print(type(code).__name__)
```

Expected output:

```text
42
code
```

The code object is compiled code, not a running function and not a sandbox. `exec()` executes the object in a namespace and may perform file I/O, import modules, mutate objects, start processes, or do anything the code has permission to do.

## 6.2 Compile an expression and evaluate its result

```python
code = compile("6 * 7", "<expr>", "eval")
print(eval(code))
```

Expected output:

```text
42
```

This example is for demonstrating modes, not a recommendation to `eval()` untrusted source. For user-supplied mathematical expressions, prefer an explicit allow-listed AST interpreter with limits and tests, as covered in the next lesson on `eval`/`exec` risks.

## 6.3 A transformed tree is not automatically executed

The transformation lifecycle should be explicit:

```python
import ast

source = "answer = number ** 2"
tree = ast.parse(source)
tree = NameSquareToMultiply().visit(tree)  # transform only
assert isinstance(tree, ast.Module)
tree = ast.fix_missing_locations(tree)
code = compile(tree, "<transformed>", "exec")  # validate/compile
namespace = {"number": 5}
exec(code, namespace)  # execute separately
print(namespace["answer"])
```

Expected output:

```text
25
```

This snippet assumes `NameSquareToMultiply` from Section 5.3 is defined in the same interpreter session. A production tool should not run code merely to validate a codemod. `compile()` checks whether the transformed tree is compilable; it does not check the behavior is correct.

## 6.4 Why compilation can fail after transformation

An AST can be structurally incomplete or semantically invalid for compilation. Common causes include:

- missing required fields;
- wrong node types in fields;
- missing source locations on constructed nodes;
- incompatible context nodes (`Load` versus `Store`);
- a statement placed where an expression is required;
- invalid combinations that the parser would never produce.

Run `compile(tree, filename, mode)` in tests after each transformation. For a tool that processes repositories, catch and report `SyntaxError`, `TypeError`, and `ValueError` at the file boundary, while preserving the original file unchanged when the transformed result fails validation.

---

# 7. Advanced analysis and code generation

## 7.1 Constant folding: semantics first

**Constant folding** replaces an expression with its computed value when the transformation can prove that doing so is safe. Python's own compiler may fold some constant expressions; the exact set is implementation- and version-dependent. A custom AST transformer should use a deliberately small grammar and avoid calling arbitrary overloaded operations on untrusted or unknown values.

For a safe demonstration, fold only integer literals for addition and multiplication, explicitly excluding booleans and guarding against a result-size policy:

```python
import ast

class SmallIntegerFolder(ast.NodeTransformer):
    """Fold integer-literal addition/multiplication with a small-result bound."""

    MAX_ABS_RESULT = 1_000_000

    def visit_BinOp(self, node: ast.BinOp) -> ast.expr:
        node = self.generic_visit(node)
        if not (
            isinstance(node.left, ast.Constant)
            and type(node.left.value) is int
            and isinstance(node.right, ast.Constant)
            and type(node.right.value) is int
        ):
            return node
        if isinstance(node.op, ast.Add):
            result = node.left.value + node.right.value
        elif isinstance(node.op, ast.Mult):
            result = node.left.value * node.right.value
        else:
            return node
        if abs(result) > self.MAX_ABS_RESULT:
            return node
        return ast.copy_location(ast.Constant(value=result), node)

source = "x = 2 + 3 * 4\ny = 10 - 2\nz = 1000000 * 1000000\n"
tree = SmallIntegerFolder().visit(ast.parse(source))
tree = ast.fix_missing_locations(tree)
print(ast.unparse(tree))
compile(tree, "<folded>", "exec")
```

Expected output:

```python
x = 14
y = 10 - 2
z = 1000000 * 1000000
```

Because children are visited before the parent, `3 * 4` folds to `12`, then `2 + 12` folds to `14`. Subtraction is not in the supported grammar and remains unchanged. The magnitude guard is only a simple policy demonstration; production resource limits need more complete analysis, because intermediate operations and parsing can also consume resources.

## 7.2 Assertion rewriting: the concept

A plain assertion such as:

```python
assert actual == expected
```

typically reports the failed expression and its values in a generic form. A test framework can transform the assertion into code that captures relevant subexpressions before comparing them, so a failure explains intermediate values. This is the conceptual basis of `pytest` assertion rewriting: parse or otherwise inspect the source, identify assertion expressions, transform them, and compile the resulting code.

This is not a recipe to replace every `assert` with arbitrary generated statements. A correct implementation must preserve evaluation count, evaluation order, short-circuit behavior, exception behavior, source locations, and behavior when assertions are disabled. Assertion rewriting is an advanced transformation problem because naïvely evaluating a subexpression twice can change program behavior.

## 7.3 Build ASTs by hand, source strings, or templates

Three broad approaches exist:

1. **Construct AST nodes directly.** Structured and easy to inspect, but verbose and sensitive to node schema/version changes.
2. **Generate source strings.** Often readable for small templates, but must handle quoting, escaping, indentation, and syntax errors. Never concatenate untrusted text into executable source.
3. **Use a template or CST library.** Useful when output must preserve source layout or when a larger codemod needs a higher-level API.

Libraries such as `dataclasses` generate methods and use dynamic code-generation techniques internally in some implementations. This is a reminder that code generation can be a legitimate performance or ergonomics technique—not a justification to execute untrusted generated source.

## 7.4 `symtable`: scope and binding analysis

The `symtable` module exposes compiler-generated symbol-table information for source text. It helps answer scope questions such as whether a name is local, global, free, or nonlocal within a block. It complements the AST: the AST describes syntactic structure; the symbol table describes compiler scope classification.

```python
import symtable

source = """
value = 10
def outer(arg):
    captured = arg
    def inner():
        return captured + value
    return inner
"""
root = symtable.symtable(source, "scope_demo.py", "exec")
outer = next(child for child in root.get_children() if child.get_name() == "outer")
inner = next(child for child in outer.get_children() if child.get_name() == "inner")
for name in ("captured", "value"):
    symbol = inner.lookup(name)
    print(name, "free=" + str(symbol.is_free()), "global=" + str(symbol.is_global()))
```

Expected output:

```text
captured free=True global=False
value free=False global=True
```

Exact API details should be checked against the Python version you support. `symtable` does not prove a name is safe or identify the runtime object bound to it; it reports compiler scope properties.

## 7.5 `tokenize`: comments, operators, and source positions

The AST drops comments and most formatting. `tokenize` can inspect lexical tokens and retain comments, which is useful for tools that need to detect `# noqa`, type comments, encoding declarations, or formatting-sensitive regions.

```python
import io
import tokenize

source = "x = 1  # keep this comment\n"
for token in tokenize.generate_tokens(io.StringIO(source).readline):
    if token.type in (tokenize.NAME, tokenize.NUMBER, tokenize.COMMENT):
        print(tokenize.tok_name[token.type], repr(token.string), token.start)
```

Expected output:

```text
NAME 'x' (1, 0)
NUMBER '1' (1, 4)
COMMENT '# keep this comment' (1, 7)
```

Token columns are character positions in the token stream; AST `col_offset` values use UTF-8 byte offsets. If combining these tools for non-ASCII source, convert offsets carefully rather than assuming the two coordinate systems are identical.

## 7.6 Concrete syntax trees and LibCST

An AST abstracts away comments and formatting. A **concrete syntax tree (CST)** retains more of the original syntax, including trivia such as comments and whitespace, depending on the library. [LibCST](https://libcst.readthedocs.io/) is a Python library designed for source-preserving transformations and codemods.

Choose:

- `ast` for built-in structural analysis, lightweight checks, and transformations where formatting preservation is not required;
- `tokenize` when token-level details or comments are needed without a full CST transformation model;
- a CST library such as LibCST when changing code while preserving comments, whitespace, and layout is a requirement.

LibCST is an external dependency; it is not part of the Python standard library. Pin and test its supported Python versions in a real project. A CST is not automatically a semantic analyzer, and preserving formatting does not prove a transformation is behavior-preserving.

## 7.7 Security analysis and taint-style reasoning

ASTs can support security scanners by finding calls such as `eval`, `exec`, `subprocess.run`, or unsafe deserialization APIs, and by tracking simple flows from sources (for example, request parameters) to sinks (for example, shell execution). But a basic visitor that sees a call name is only a first-pass syntactic check.

A more realistic taint analysis needs to consider:

- how imported names and aliases are resolved;
- assignment and reassignment;
- function parameters and return values;
- interprocedural data flow;
- sanitizers and validation boundaries;
- dynamic imports, reflection, monkey-patching, and framework behavior;
- false positives and false negatives.

Do not claim that a syntax scan proves an application secure. Use AST findings as review signals, add data-flow modeling where justified, and test the scanner against positive and negative fixtures.

---

# 8. Version compatibility

Python's AST schema evolves with the language. Tools that inspect or construct ASTs should declare supported Python versions and run tests on each supported interpreter.

| Version milestone | Change to know | Tooling implication |
|---|---|---|
| Python 3.8 | Literal-specific nodes such as `Num`, `Str`, `Bytes`, `NameConstant`, and `Ellipsis` were consolidated under `ast.Constant`. | Prefer `isinstance(node, ast.Constant)` and inspect `node.value`; do not write new code around legacy literal node classes. |
| Python 3.9 | `ast.unparse()` was added. | It generates source from the tree; it is not a source-preserving formatter. |
| Python 3.10 | Structural pattern matching added `Match`, `MatchCase`, and pattern nodes. | A tool targeting 3.10+ should account for `match` statements if relevant. |
| Python 3.12 | Generic/type-parameter syntax added `type_params` fields to relevant nodes and introduced type-parameter AST nodes such as `TypeVar`, `ParamSpec`, and `TypeVarTuple`. | Code constructing `FunctionDef` or `ClassDef` should follow the target interpreter's schema; visitors may need to inspect type parameters. |
| Python 3.13 | AST constructors increasingly enforce required fields and reject missing/invalid fields more strictly; deprecated constructor behavior continues to evolve. | Avoid relying on partially initialized nodes or passing arbitrary keyword attributes as substitutes for real AST fields. Test construction and compilation on supported versions. |
| Python 3.14 | Template string literals introduce AST nodes such as `TemplateStr` and `Interpolation`; `ast.compare()` is also available for structural AST comparisons. | Code that must parse 3.14 syntax needs to run on a 3.14+ interpreter and handle these nodes intentionally. Do not assume an older interpreter can parse newer syntax. |
| Python 3.15 | The default `ast.dump()` omits optional `Load()` context values; the `color` option is available for colorized dumps. AST APIs and schemas continue to evolve. | Do not treat a dump string from 3.12–3.14 as universal expected output. Pin versions for snapshot tests or compare AST structure using version-appropriate APIs. |

This table is a compatibility guide, not an exhaustive changelog. Consult the official [`ast` documentation](https://docs.python.org/3/library/ast.html), [`tokenize`](https://docs.python.org/3/library/tokenize.html), and [`symtable`](https://docs.python.org/3/library/symtable.html) documentation for the exact target version. A Python 3.12 interpreter cannot parse syntax added in 3.13 or 3.14 merely because a tool has version checks.

## 8.1 Practical compatibility rules

- Use `sys.version_info` only when behavior truly depends on the running interpreter; avoid scattering version checks when feature detection is clearer.
- Use `getattr(node, "type_params", [])` when reading optional fields across versions where that field may not exist.
- Construct nodes with the required fields for the interpreter you run on; do not assume one AST constructor signature works forever.
- Keep fixtures for each syntax family your tool supports, including `async def`, decorators, positional-only parameters, keyword-only parameters, comprehensions, `match`, and type parameters if relevant.
- Parse source with the same interpreter version used for compilation and CI validation.
- Avoid comparing complete `ast.dump()` strings across versions unless the version is pinned.

---

# 9. Practical project: a repository lint rule and codemod

This small project builds a command-line checker that reports mutable literal defaults and can optionally perform a deliberately narrow codemod. It is designed to be understandable and testable, not to replace a mature linter.

## 9.1 Project layout

```text
ast_tool/
├── ast_lint.py
├── test_ast_lint.py
└── fixtures/
    ├── clean.py
    └── mutable_defaults.py
```

## 9.2 Define the rule contract

**Rule `AST001`: mutable default.** Report list, dict, or set literal defaults and zero-argument `list()`, `dict()`, or `set()` constructor calls on sync and async functions, including nested functions and methods. Check positional, positional-only, and keyword-only defaults. Do not flag a name or an arbitrary call merely because it might produce a mutable value. The constructor-name check is syntactic and can be fooled by shadowing. Report the default expression's source line.

**Codemod `SQUARE001`:** rewrite only `NAME ** 2` to `NAME * NAME`. Do not rewrite attribute access, calls, subscripts, negative exponents, other exponents, or operands other than a simple name. This grammar avoids evaluating a complex operand twice, but it still assumes that the project's intended numeric domain makes the operator rewrite acceptable. The tool only writes transformed source to stdout in this example; it does not overwrite files.

## 9.3 `ast_lint.py`

```python
from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Diagnostic:
    rule: str
    path: str
    line: int
    column: int
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}:{self.column}: {self.rule} {self.message}"


class MutableDefaultRule(ast.NodeVisitor):
    def __init__(self, path: str) -> None:
        self.path = path
        self.diagnostics: list[Diagnostic] = []

    def _check_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        positional = [*node.args.posonlyargs, *node.args.args]
        if node.args.defaults:
            for arg, default in zip(positional[-len(node.args.defaults):], node.args.defaults):
                self._check_default(node, arg.arg, default)
        for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
            if default is not None:
                self._check_default(node, arg.arg, default)

    def _check_default(
        self,
        function: ast.FunctionDef | ast.AsyncFunctionDef,
        parameter: str,
        default: ast.expr,
    ) -> None:
        is_container_literal = isinstance(default, (ast.List, ast.Dict, ast.Set))
        is_empty_builtin_constructor = (
            isinstance(default, ast.Call)
            and isinstance(default.func, ast.Name)
            and default.func.id in {"list", "dict", "set"}
            and not default.args
            and not default.keywords
        )
        if is_container_literal or is_empty_builtin_constructor:
            self.diagnostics.append(
                Diagnostic(
                    rule="AST001",
                    path=self.path,
                    line=default.lineno,
                    column=default.col_offset,
                    message=(
                        f"mutable default expression for parameter {parameter!r} "
                        f"in function {function.name!r}"
                    ),
                )
            )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)


class NameSquareToMultiply(ast.NodeTransformer):
    def visit_BinOp(self, node: ast.BinOp) -> ast.expr:
        node = self.generic_visit(node)
        if (
            isinstance(node.op, ast.Pow)
            and isinstance(node.left, ast.Name)
            and isinstance(node.right, ast.Constant)
            and type(node.right.value) is int
            and node.right.value == 2
        ):
            return ast.copy_location(
                ast.BinOp(
                    left=node.left,
                    op=ast.Mult(),
                    right=ast.Name(id=node.left.id, ctx=ast.Load()),
                ),
                node,
            )
        return node


def check_source(source: str, path: str) -> list[Diagnostic]:
    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as exc:
        line = exc.lineno or 1
        column = max((exc.offset or 1) - 1, 0)
        return [Diagnostic("AST000", path, line, column, f"syntax error: {exc.msg}")]
    rule = MutableDefaultRule(path)
    rule.visit(tree)
    return rule.diagnostics


def transform_source(source: str, path: str) -> str:
    tree = ast.parse(source, filename=path)
    tree = NameSquareToMultiply().visit(tree)
    tree = ast.fix_missing_locations(tree)
    # Compile before returning output: never emit a transformation that cannot compile.
    compile(tree, path, "exec")
    return ast.unparse(tree) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Small AST lint/codemod demonstration")
    parser.add_argument("path", type=Path)
    parser.add_argument("--square-codemod", action="store_true")
    args = parser.parse_args(argv)
    try:
        source = args.path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"{args.path}: error: {exc}", file=sys.stderr)
        return 2

    if args.square_codemod:
        try:
            sys.stdout.write(transform_source(source, str(args.path)))
        except (SyntaxError, TypeError, ValueError) as exc:
            print(f"{args.path}: codemod failed: {exc}", file=sys.stderr)
            return 2
        return 0

    diagnostics = check_source(source, str(args.path))
    for diagnostic in diagnostics:
        print(diagnostic)
    return 1 if diagnostics else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### Fixture files

Create `fixtures/mutable_defaults.py`:

```python
def build_records(records=[]):
    return records

async def load_options(*, options=dict()):
    return options
```

Create `fixtures/clean.py`:

```python
def build_records(records=None):
    return [] if records is None else records
```

Create `fixtures/squares.py`:

```python
square = value ** 2
cube = value ** 3
nested = obj.value ** 2
```

### Usage

```bash
python ast_lint.py fixtures/mutable_defaults.py
python ast_lint.py fixtures/clean.py
python ast_lint.py --square-codemod fixtures/squares.py
```

Expected output for `mutable_defaults.py` (process exit status `1`):

```text
fixtures/mutable_defaults.py:1:26: AST001 mutable default expression for parameter 'records' in function 'build_records'
fixtures/mutable_defaults.py:4:34: AST001 mutable default expression for parameter 'options' in function 'load_options'
```

`clean.py` exits with status `0` and prints nothing. The codemod prints this transformed source to stdout:

```python
square = value * value
cube = value ** 3
nested = obj.value ** 2
```

A checker often uses exit code `1` when violations exist, `0` when clean, and `2` for an operational or parsing error. Teams should document this contract so CI can interpret the result correctly.

## 9.4 Tests with `pytest`

Save the following as `test_ast_lint.py` beside `ast_lint.py`:

```python
import ast

import pytest

from ast_lint import MutableDefaultRule, check_source, transform_source


def test_mutable_defaults_positional_and_keyword_only() -> None:
    source = "def f(a, b=[], *, options={}):\n    return a\n"
    diagnostics = check_source(source, "sample.py")
    assert len(diagnostics) == 2
    assert all(item.rule == "AST001" for item in diagnostics)
    assert "parameter 'b'" in diagnostics[0].message
    assert "parameter 'options'" in diagnostics[1].message


def test_positional_only_default_alignment() -> None:
    source = "def f(required, items=[], /, named=()):\n    return items\n"
    diagnostics = check_source(source, "posonly.py")
    assert len(diagnostics) == 1
    assert "parameter 'items'" in diagnostics[0].message


def test_visits_nested_function_class_method_and_async_function() -> None:
    source = """
def outer():
    def inner(items=[]):
        pass
    class Nested:
        def method(self, cache=set()):
            pass
    return inner

async def task(options={}):
    pass
"""
    diagnostics = check_source(source, "nested.py")
    assert [item.message.split("parameter ")[1].split(" ")[0] for item in diagnostics] == [
        "'items'", "'cache'", "'options'"
    ]


def test_does_not_flag_name_arbitrary_call_or_tuple_default() -> None:
    source = "DEFAULT = []\ndef f(a=DEFAULT, b=make_list(), c=()):\n    pass\n"
    assert check_source(source, "clean.py") == []


def test_flags_empty_builtin_container_constructor_calls() -> None:
    source = "def f(a=list(), b=dict(), c=set()):\n    pass\n"
    diagnostics = check_source(source, "constructors.py")
    assert len(diagnostics) == 3


def test_invalid_syntax_is_reported_not_crashed() -> None:
    diagnostics = check_source("def broken(:\n pass\n", "broken.py")
    assert len(diagnostics) == 1
    assert diagnostics[0].rule == "AST000"
    assert "syntax error" in diagnostics[0].message


def test_transform_rewrites_only_simple_name_square() -> None:
    result = transform_source(
        "a = number ** 2\nb = obj.number ** 2\nc = number ** -2\nd = number ** 3\n",
        "squares.py",
    )
    tree = ast.parse(result)
    assert ast.unparse(tree) == (
        "a = number * number\n"
        "b = obj.number ** 2\n"
        "c = number ** (-2)\n"
        "d = number ** 3"
    )
    compile(tree, "<test>", "exec")


def test_transform_compilation_rejects_invalid_input() -> None:
    with pytest.raises(SyntaxError):
        transform_source("def invalid(:\n pass\n", "invalid.py")


def test_transform_leaves_call_and_subscript_operands_unchanged() -> None:
    result = transform_source(
        "a = get_value() ** 2\nb = values[index] ** 2\n", "unsupported.py"
    )
    tree = ast.parse(result)
    assert isinstance(tree.body[0].value, ast.BinOp)
    assert isinstance(tree.body[0].value.left, ast.Call)
    assert isinstance(tree.body[1].value, ast.BinOp)
    assert isinstance(tree.body[1].value.left, ast.Subscript)
    compile(tree, "<unsupported-test>", "exec")


def test_transform_preserves_source_line_and_rejects_bool_exponent() -> None:
    result = transform_source("first = 1\nsecond = value ** True\n", "lines.py")
    tree = ast.parse(result)
    assert tree.body[0].lineno == 1
    assert tree.body[1].lineno == 2
    assert isinstance(tree.body[1].value, ast.BinOp)
    assert isinstance(tree.body[1].value.op, ast.Pow)


def test_mutable_default_rule_visits_child_nodes() -> None:
    tree = ast.parse("def outer():\n    class C:\n        def f(self, x=[]):\n            return x\n")
    rule = MutableDefaultRule("nested.py")
    rule.visit(tree)
    assert len(rule.diagnostics) == 1
    assert "parameter 'x'" in rule.diagnostics[0].message
```

Run:

```bash
python -m pytest -q
```

Expected result for these eleven tests:

```text
11 passed
```

The exact pytest summary may include duration and platform information. The project intentionally does not modify files in place. Before adding a write-back mode, add a dry-run diff, backup/version-control workflow, encoding/newline handling, per-file atomic writes, and an opt-in confirmation policy.

## 9.5 Production hardening checklist

- [ ] Define exact rule semantics and known false positives/negatives.
- [ ] Keep parsing, analysis, transformation, and output separate.
- [ ] Include filename, line, column, rule ID, and actionable message in diagnostics.
- [ ] Test nested definitions and all relevant argument forms.
- [ ] Compile every transformed tree before writing it.
- [ ] Use CST tooling if comments and formatting must survive.
- [ ] Preserve original files on parse/transform/compile failure.
- [ ] Test every supported Python version in CI.
- [ ] Bound file size and parser work when analyzing untrusted source.
- [ ] Do not execute scanned or transformed code as a validation shortcut.
- [ ] Treat security findings as evidence for review, not a proof of safety.

---

# 10. Exercises with solutions

## Exercise 1 — Read a call tree

Use `ast.parse("a.b(c)", mode="eval")` and explain the outer node and its children.

**Solution:** The outer node is `Expression`, whose `body` is a `Call`. The call's `func` is an `Attribute` with `value=Name('a', Load())`, `attr='b'`, and `ctx=Load()`. Its `args` contains `Name('c', Load())`; `keywords` is empty.

## Exercise 2 — Count calls inside nested expressions

Write a visitor or use `ast.walk()` to count calls in `save(parse(read()))`.

**Solution:** There are three `Call` nodes: `save`, `parse`, and `read`.

```python
import ast

tree = ast.parse("save(parse(read()))")
print(sum(isinstance(n, ast.Call) for n in ast.walk(tree)))
```

Expected output: `3`.

## Exercise 3 — Find bare exception handlers

Why is `except:` represented differently from `except Exception:`?

**Solution:** In `ExceptHandler`, a bare handler has `type is None`; `except Exception:` has a type expression, usually a `Name('Exception')`. A checker should inspect the node structure rather than match the text `except:`.

## Exercise 4 — Extend mutable-default detection

Add support for `Tuple` defaults that directly contain a list, dict, or set literal. Do not attempt to resolve names or calls.

**Solution:** Add a helper such as:

```python
def is_mutable_literal(node: ast.expr) -> bool:
    if isinstance(node, (ast.List, ast.Dict, ast.Set)):
        return True
    if isinstance(node, ast.Tuple):
        return any(is_mutable_literal(element) for element in node.elts)
    return False
```

Then call `is_mutable_literal(default)` instead of checking only the three container node types. This detects `([],)` but still does not prove whether `DEFAULT` or `factory()` returns a mutable object.

## Exercise 5 — Rewrite a simple expression

Change `value ** 2` to `value * value` but leave `value ** 3` unchanged. Why should the left operand be restricted?

**Solution:** Use `NodeTransformer` to match `BinOp(Pow)` with a `Name` left operand and integer `Constant(2)` right operand, as in Section 5.3. Restricting the left operand avoids duplicating a complex expression with side effects. It does not make the rewrite universally equivalent for all Python objects.

## Exercise 6 — Why did compilation fail?

You construct `ast.Name(id="x")` and pass the tree to `compile()`. What is missing?

**Solution:** A `Name` node requires a context such as `ast.Load()` or `ast.Store()`, and the containing tree may need source locations. Construct `ast.Name(id="x", ctx=ast.Load())` in an expression, then use `ast.fix_missing_locations()` where appropriate. Correct context depends on whether the name is being read, assigned, or deleted.

## Exercise 7 — Select the right representation

You must rename a function and preserve all comments and whitespace. Should you use `ast`, `tokenize`, or a CST?

**Solution:** A CST tool such as LibCST is the best fit because preserving formatting and comments is a requirement. AST alone discards those details. `tokenize` can locate tokens/comments but requires more manual editing and careful offset management for robust transformations.

## Exercise 8 — Explain the execution boundary

Why is `compile(tree, ...)` not a security check?

**Solution:** Compilation checks that the tree can be converted to a code object for the requested mode. It does not constrain what the code can do when executed. A valid program can read files, access the network, import modules, or perform other side effects. Do not execute untrusted code in-process as a validation step.

## Exercise 9 — Scope analysis

A nested function references a variable assigned in the enclosing function. Which tool can help classify the reference as a free variable?

**Solution:** `symtable` exposes compiler scope classification. The AST shows the nested structure, while the symbol table can report that the nested function uses a name as a free variable. It does not identify the runtime object or prove the program's behavior.

## Exercise 10 — Version-tolerant tooling

Why should a checker avoid assuming every `FunctionDef` has exactly the same fields on every supported Python version?

**Solution:** AST schemas evolve with language syntax. Python 3.12 introduced type-parameter support and associated fields/nodes; later versions can add syntax and change constructors. Declare supported versions, use feature-aware access where appropriate, and test on every supported interpreter.

---

# 11. Interview questions and final checklist

## Interview questions

1. What does an AST preserve that raw text does not, and what does it discard?
2. Explain the difference between tokenization, parsing, static analysis, transformation, compilation, and execution.
3. What is the AST for `a.b(c)`? Which nodes represent the attribute access and the call?
4. What is the difference between `ast.walk()` and `NodeVisitor`? Why does `generic_visit()` matter?
5. How do positional defaults align with `FunctionDef.args.defaults`? How are keyword-only defaults represented?
6. How would you detect `except:` without matching text in comments or strings?
7. Why can `ast.unparse()` not reproduce comments or original formatting?
8. What does `ast.fix_missing_locations()` do, and what does it not do?
9. Why should a `NodeTransformer` specify a grammar and unsupported cases?
10. Why might rewriting `x ** 2` to `x * x` change behavior?
11. How would you test a transformation for valid inputs, unsupported inputs, and compile failures?
12. What is the difference between AST and CST? When would you choose LibCST?
13. How do `symtable` and `tokenize` complement AST traversal?
14. What AST compatibility issues arise across Python 3.8, 3.12, and 3.14?
15. Why is `compile()` not a sandbox or proof of semantic correctness?
16. What extra analysis is needed to turn a call-finding visitor into a meaningful taint analyzer?

## Final checklist

- [ ] I can describe source → tokens → AST → compilation/code object → execution.
- [ ] I can parse code and inspect node types with `ast.parse()` and `ast.dump()`.
- [ ] I recognize `Module`, `FunctionDef`, `ClassDef`, `Assign`, `Call`, `Name`, `Attribute`, `Constant`, `BinOp`, `If`, `For`, and `Return`.
- [ ] I understand `Load`, `Store`, and `Del` contexts.
- [ ] I can write a `NodeVisitor` and traverse nested definitions correctly.
- [ ] I can report print calls, missing docstrings, bare exception handlers, and mutable literal defaults.
- [ ] I know the limits of syntactic checks and why regex is often the wrong abstraction.
- [ ] I can write a narrowly specified `NodeTransformer`, repair locations, and compile the result.
- [ ] I can explain why `ast.unparse()` is not source preserving.
- [ ] I know the intended scope and limitations of `ast.literal_eval()`.
- [ ] I keep transformation, compilation, and execution as separate operations.
- [ ] I can explain constant folding and the conceptual basis of assertion rewriting.
- [ ] I know when `symtable`, `tokenize`, and a CST are appropriate.
- [ ] I test transformations on nested syntax, unsupported forms, invalid syntax, and target Python versions.
- [ ] I understand that AST-based security scanning is a useful signal, not a proof that code is safe.

## Key takeaway

ASTs turn source code into a traversable structure, making reliable structural checks and controlled rewrites possible. The engineering challenge is not just to mutate nodes: it is to define the supported grammar, preserve semantics and locations, validate the transformed tree, respect Python-version differences, and keep code execution behind an explicit trust boundary.
