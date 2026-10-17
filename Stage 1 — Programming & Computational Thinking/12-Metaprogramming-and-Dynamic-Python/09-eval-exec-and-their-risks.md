# 09 — `eval()`, `exec()`, and Their Risks

> **Security rule:** never pass untrusted text to `eval()` or `exec()`. An empty `__builtins__` mapping is not a sandbox. If users need expressions, define a small language and interpret only allow-listed syntax. If arbitrary code is unavoidable, execute it outside the trusted process with defense-in-depth isolation and resource limits.

## Learning outcomes

Distinguish expression evaluation from statement execution; explain compilation and namespace behavior; threat-model dynamic execution; choose safer alternatives; implement and test a bounded arithmetic interpreter; and review code for dynamic execution and adjacent deserialization/shell risks.

## 1. Prerequisites and threat-model fundamentals

### 1.1 Terms and risks

- **Source** is text supplied to a parser/compiler. It is not inherently safe because it is text.
- **Trusted source** is controlled by a reviewed deployment process. Data from a database, internal service, template, or model is not automatically trusted.
- **Code injection** occurs when data is interpreted as instructions because a program crosses a data/code boundary unsafely.
- **Sandbox/isolation boundary** limits what a workload can access or consume. A Python globals dictionary is not an OS security boundary.
- **Confidentiality, integrity, availability:** dynamic execution can expose secrets, alter state, or exhaust resources.

For every dynamic-code feature, ask who controls the bytes, what process authority they inherit (credentials, files, network, database handles), what impact is possible, what resource limits apply, and whether a data format or smaller language meets the requirement.

### 1.2 Data and code are different

`"2 + 3"` is data until interpreted. `eval("2 + 3")` treats it as a Python expression; `exec("x = 3")` treats it as statements. Parsing is not execution, but parsing and compilation can still consume resources. Apply size and operational limits at trust boundaries.

## 2. Basic `eval()`, `exec()`, and `compile()`

### 2.1 `eval`: one expression, return a value

```python
print(eval("2 + 3 * 4"))
print(eval("len('abc')"))
```

Expected output:

```text
14
3
```

`eval(source, globals=None, locals=None)` evaluates a Python expression and returns its value. It does not accept an assignment statement in expression mode. This example uses fixed trusted source; do not use `eval()` to process user input.

### 2.2 `exec`: execute statements

```python
namespace = {}
exec("def square(n):\n    return n * n", namespace)
print(namespace["square"](5))
print(exec("answer = 42", namespace))
print(namespace["answer"])
```

Expected output:

```text
25
None
42
```

`exec()` executes a suite of statements and returns `None`. The function definition is created by `exec`; calling the resulting function is a separate operation.

### 2.3 `compile`: produce a code object, not execute it

```python
expression_code = compile("2 + 3", "<demo-expression>", "eval")
statement_code = compile("answer = 42", "<demo-statements>", "exec")
print(eval(expression_code))
ns = {}
exec(statement_code, ns)
print(ns["answer"])
```

Expected output:

```text
5
42
```

Common `compile()` modes are `"eval"` (one expression), `"exec"` (a module/suite), and `"single"` (interactive single-statement input). Compilation creates a code object or raises an error; it does not run that code object. Compiler flags, `dont_inherit`, and `optimize` are not security controls. A code object is executable capability, not evidence of safety.

### 2.4 Expressions versus statements

Expressions produce values (`x + 1`, `f(3)`, `[1, 2]`); statements perform actions or control flow (`x = 1`, `if`, `for`, `def`, `import`). Expressions can still have side effects: a call expression may write files or mutate state. Syntactic category is not a security rating.

| Operation | Result | Runs submitted program? |
|---|---|---|
| `ast.parse()` | Syntax tree | No |
| `compile(source, ..., mode)` | Code object | No; compilation still consumes resources |
| `eval(expr_or_code)` | Expression result | Yes |
| `exec(code_or_suite)` | Usually `None` | Yes |
| `ast.literal_eval()` | Supported literal value | Does not execute arbitrary Python |

## 3. Namespace behavior

### 3.1 Explicit globals and locals

```python
globals_ns = {"x": 2}
print(eval("x + 1", globals_ns))

scope = {"base": 10}
exec("result = base * 3", scope)
print(scope["result"])
```

Expected output:

```text
3
30
```

If a supplied globals dictionary has no `"__builtins__"` key, Python normally inserts a reference to the builtins namespace. So `eval(expr, {"x": 2})` does not mean “no built-ins.” Explicit namespace dictionaries control name lookup and where results are stored; they do not make arbitrary code safe.

### 3.2 Separate globals and locals

With `exec(source, globals_dict, locals_dict)` and distinct mappings, execution behaves similarly to a class body. Assignments can go into the locals mapping, but functions defined there do not capture arbitrary entries from that mapping as a normal enclosing function scope.

```python
g = {}
l = {"x": 7}
exec("y = x + 1\ndef get_x():\n    return x", g, l)
print(l["y"])
try:
    l["get_x"]()
except NameError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
8
NameError
```

Do not use namespace quirks as a security boundary.

### 3.3 `locals()` and Python 3.13+

Python 3.13 changed default locals semantics in connection with PEP 667. In optimized scopes such as function bodies, `locals()` returns a snapshot-like mapping; writing to it does not assign ordinary local variables, and each call returns a fresh mapping. `frame.f_locals` has defined proxy behavior in optimized scopes under the new model. Module and class scopes differ from optimized function scopes. Python 3.12 and earlier had different historical behavior.

The default locals behavior relevant to `eval()` and `exec()` also changed in Python 3.13. In 3.13, `globals` and `locals` may be passed as keyword arguments to both built-ins; code supporting older versions should not assume that call syntax is portable. Do not use `exec()` inside a function to create or mutate ordinary locals. When legitimate dynamic execution is needed, pass explicit dictionaries and retrieve results from those dictionaries. In Python 3.14, the C API function `PyEval_GetLocals()` emits `DeprecationWarning` under PEP 667; extension authors should review the recommended replacements (`PyEval_GetFrameLocals()` or `PyFrame_GetLocals()` depending on intent). This C API change does not make dynamic execution a sandbox. Verify version-sensitive assumptions against the documentation for the target interpreter.

### 3.4 Namespace control is not capability control

Objects can expose methods, classes, descriptors, modules, and references to other objects. Attribute access can invoke custom behavior; operators can call overloaded special methods. Removing a name such as `open` does not remove every path to powerful objects. Never use namespace manipulation to sandbox hostile Python.

## 4. Code-injection risks

### 4.1 Harmless demonstration of the trust-boundary failure

```python
user_text = "__import__('math').sqrt(81)"
print(eval(user_text))
```

Expected output:

```text
9.0
```

The module is benign, but the design flaw is real: user-controlled text is interpreted as Python. Depending on the process authority, the same pattern may read files, mutate application state, or perform network activity. Destructive payloads are unnecessary to demonstrate the risk.

### 4.2 Why an empty `__builtins__` is not a sandbox

```python
print(eval("1 + 2", {"__builtins__": {}}))
```

Expected output: `3`

This proves only that this simple expression works without built-ins. Python's object model includes attribute access, class relationships, descriptors, and reachable objects; historical object-graph techniques can recover capabilities in some contexts. Specific exploit paths vary by runtime and are not universal. The defensible conclusion is general: restricting built-in names is not a reliable boundary around arbitrary Python.

**Production rule:** do not run untrusted source with `eval()` or `exec()`, even if `__builtins__` is empty or replaced.

### 4.3 Regex is not a Python parser

Regex can validate deliberately flat formats, but Python contains nested parentheses, strings with punctuation, escaped quotes, precedence, indentation, comprehensions, and comments. A blacklist such as rejecting `import` or `__` is both bypassable and prone to false positives. Use a parser for a deliberately small grammar and reject every syntax form outside it.

### 4.4 Common injection entry points

- **Configuration:** Python expressions where JSON/TOML plus schema validation would work.
- **Templates:** user-authored expressions evaluated with application objects in scope.
- **Notebooks/REPLs:** cells are executable programs; metadata and output are not proof of trust.
- **Serialized objects:** `pickle` can execute code during deserialization. Never unpickle untrusted bytes. Prefer schema-validated data formats. For YAML, use a safe loader and validate the schema; loader safety does not replace validation/resource limits.
- **Generated code:** untrusted values interpolated into source can become code injection. Represent values safely and control the grammar.
- **LLM output:** model-generated code is untrusted even if the model is internal, prompted to be safe, or produces plausible explanations.

## 5. Safer alternatives, in preference order

### 5.1 First: data formats (`json`, `tomllib`)

```python
import json

config = json.loads('{"retries": 3, "enabled": true}')
retries = config.get("retries")
if type(retries) is not int or not 0 <= retries <= 10:
    raise ValueError("retries must be an integer from 0 to 10")
print(retries, config["enabled"])
```

Expected output: `3 True`

JSON parsing does not execute Python, but it does not validate business rules automatically. Validate allowed keys, types, ranges, and structure. Cap payload size/depth in exposed services. `tomllib` is in the standard library from Python 3.11 and parses TOML (it does not write TOML).

### 5.2 Second: `ast.literal_eval()` for literals only

```python
import ast

print(ast.literal_eval("{'region': 'ap-south-1', 'ports': [8000, 8001]}"))
for text in ("2 + 3", "open('x')"):
    try:
        ast.literal_eval(text)
    except (ValueError, SyntaxError) as exc:
        print(type(exc).__name__)
```

Expected output:

```text
{'region': 'ap-south-1', 'ports': [8000, 8001]}
ValueError
ValueError
```

`literal_eval` accepts literal structures such as strings, bytes, numbers, tuples, lists, dicts, sets, booleans, `None`, and certain simple unary numeric forms. It does not evaluate calls or arithmetic like `2 + 3`. It is much safer than `eval` for literals, but official documentation warns that sufficiently complex input can exhaust memory, CPU, or the C stack. Bound size/depth and do not treat it as risk-free for attacker-controlled large input.

### 5.3 Third: dispatch tables and allow-listed operations

```python
from operator import add, mul, sub

OPERATIONS = {"add": add, "subtract": sub, "multiply": mul}

def calculate(operation: str, left: float, right: float) -> float:
    try:
        fn = OPERATIONS[operation]
    except KeyError as exc:
        raise ValueError("unsupported operation") from exc
    return fn(left, right)

print(calculate("multiply", 6, 7))
```

Expected output: `42`

The operation table must be trusted and arguments validated. An allow-list can still expose dangerous behavior if allowed functions have side effects or accept attacker-controlled objects. Prefer exact primitive types and ranges.

### 5.4 Fourth: a restricted expression interpreter

If expressions are necessary, parse them with `ast.parse(mode="eval")` and interpret only explicitly approved nodes. Do not `eval()` or `compile()` the parsed expression. The implementation below is a bounded teaching example, not a general Python sandbox.

### 5.5 Fifth: isolated execution when arbitrary code is unavoidable

Run arbitrary code in a disposable worker with a dedicated low-privilege identity and OS-level restrictions. Combine container/VM or equivalent isolation, no secrets, restricted filesystem, network egress controls, CPU/memory/PID/file-size limits, wall-clock timeout, bounded output, and reliable process cleanup. Keep the control plane outside the worker.

Containers are not automatically perfect boundaries: kernel/runtime vulnerabilities, misconfiguration, mounted credentials, writable host paths, or excessive privileges can defeat them. For high-risk multi-tenant execution, consider hardened VMs/microVMs or managed isolated execution. `RestrictedPython` helps define a restricted language but is not itself a sandbox. WebAssembly can reduce capabilities only when host imports are tightly controlled. Validate the deployed boundary; do not infer security merely from the word “container.”

## 6. Build a bounded AST arithmetic interpreter

### 6.1 Grammar and policy

Allowed grammar:

```text
expression := number
            | + expression | - expression
            | expression (+ | - | * | / | // | % | **) expression
```

The parser handles precedence and parentheses. The interpreter accepts exact `int` and `float` constants, unary `+`/`-`, and the listed binary operators. It rejects names, calls, attributes, subscripts, containers, comparisons, booleans, strings, bitwise operators, and every unlisted AST node. `bool` is rejected even though it subclasses `int`.

Limits: source length ≤ 256 characters; AST ≤ 64 nodes; AST depth ≤ 12; literal magnitude ≤ 1,000,000; exponent must be an integer in `[0, 8]`; each intermediate result must be finite and have magnitude ≤ 1,000,000,000,000. These are example policy values, not universal defaults. Source length is checked before parsing; node/depth limits apply after parsing. An AST allow-list does not automatically prevent denial of service: use request limits and OS-level CPU/memory/time controls for exposed services too.

### 6.2 Complete implementation

Save as `safe_arithmetic.py`:

```python
import ast
import math
import operator

MAX_SOURCE_CHARS = 256
MAX_NODES = 64
MAX_DEPTH = 12
MAX_LITERAL_MAGNITUDE = 1_000_000
MAX_RESULT_MAGNITUDE = 1_000_000_000_000
MAX_EXPONENT = 8

BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}

class ExpressionRejected(ValueError):
    """Input is outside the calculator's supported language."""


def _check_number(value, *, literal=False):
    if type(value) not in (int, float):  # deliberately rejects bool
        raise ExpressionRejected("only integer and float values are allowed")
    if type(value) is float and not math.isfinite(value):
        raise ExpressionRejected("non-finite numbers are not allowed")
    limit = MAX_LITERAL_MAGNITUDE if literal else MAX_RESULT_MAGNITUDE
    if abs(value) > limit:
        raise ExpressionRejected("numeric magnitude limit exceeded")
    return value


def _check_tree_limits(root):
    count = 0
    stack = [(root, 1)]
    while stack:
        node, depth = stack.pop()
        count += 1
        if count > MAX_NODES:
            raise ExpressionRejected("AST node limit exceeded")
        if depth > MAX_DEPTH:
            raise ExpressionRejected("AST depth limit exceeded")
        stack.extend((child, depth + 1) for child in ast.iter_child_nodes(node))


def _evaluate_node(node):
    if isinstance(node, ast.Constant):
        return _check_number(node.value, literal=True)
    if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPERATORS:
        value = _evaluate_node(node.operand)
        return _check_number(UNARY_OPERATORS[type(node.op)](value))
    if isinstance(node, ast.BinOp) and type(node.op) in BINARY_OPERATORS:
        left = _evaluate_node(node.left)
        right = _evaluate_node(node.right)
        if type(node.op) is ast.Pow:
            if type(right) is not int or not 0 <= right <= MAX_EXPONENT:
                raise ExpressionRejected("exponent must be an integer from 0 to 8")
        return _check_number(BINARY_OPERATORS[type(node.op)](left, right))
    raise ExpressionRejected(f"unsupported syntax: {type(node).__name__}")


def safe_arithmetic(source: str):
    if not isinstance(source, str):
        raise TypeError("expression must be text")
    if len(source) > MAX_SOURCE_CHARS:
        raise ExpressionRejected("source length limit exceeded")
    try:
        tree = ast.parse(source, mode="eval")
    except (SyntaxError, ValueError, MemoryError, RecursionError) as exc:
        raise ExpressionRejected("invalid or excessively complex expression") from exc
    _check_tree_limits(tree)
    return _evaluate_node(tree.body)


if __name__ == "__main__":
    for expression in ("2 + 3 * 4", "-(8 // 3)", "2 ** 8"):
        print(f"{expression} = {safe_arithmetic(expression)}")
```

Expected output:

```text
2 + 3 * 4 = 14
-(8 // 3) = -2
2 ** 8 = 256
```

### 6.3 Security properties and limitations

The interpreter never executes a code object and never resolves user-supplied names. It operates on numeric primitives created by the parser and uses a fixed operator table. All unknown nodes are rejected; numeric bounds are checked before/after operations. It is still not a general sandbox. Parsing precedes AST-count checks, and recursion, CPU, or memory can be exhausted by inputs outside the example's intended envelope. The length limit mitigates but does not replace process-level resource controls. Do not add calls, attributes, subscripts, arbitrary objects, or overloaded operators without a new threat model and review.

### 6.4 Tests

Save as `test_safe_arithmetic.py` next to `safe_arithmetic.py`; run `python -m pytest -q` (install pytest if necessary).

```python
import pytest
from safe_arithmetic import ExpressionRejected, safe_arithmetic

@pytest.mark.parametrize(("source", "expected"), [
    ("2 + 3 * 4", 14), ("-(8 // 3)", -2), ("2 ** 8", 256),
    ("7 % 4", 3), ("+3.5", 3.5),
])
def test_valid_expressions(source, expected):
    assert safe_arithmetic(source) == expected

@pytest.mark.parametrize("source", [
    "f(1)", "x", "x.y", "[1, 2]", "1 < 2", "1 << 2",
    "'text'", "True + 1", "2 ** 9", "10 ** -2", "1 +",
])
def test_rejected_syntax(source):
    with pytest.raises(ExpressionRejected):
        safe_arithmetic(source)

def test_division_by_zero_is_not_silently_accepted():
    with pytest.raises(ZeroDivisionError):
        safe_arithmetic("1 / 0")

def test_non_text_input():
    with pytest.raises(TypeError):
        safe_arithmetic(123)

def test_source_length_limit():
    with pytest.raises(ExpressionRejected, match="source length"):
        safe_arithmetic("1" * 257)

def test_node_count_limit():
    with pytest.raises(ExpressionRejected, match="node limit"):
        safe_arithmetic("(" + ",".join(["1"] * 70) + ",)")

def test_depth_limit():
    with pytest.raises(ExpressionRejected, match="depth limit"):
        safe_arithmetic("-" * 13 + "1")

def test_literal_magnitude_limit():
    with pytest.raises(ExpressionRejected, match="magnitude"):
        safe_arithmetic("1000001")

def test_result_magnitude_limit():
    with pytest.raises(ExpressionRejected, match="magnitude"):
        safe_arithmetic("1000000 * 1000000 + 1")

def test_non_finite_intermediate_result_rejected():
    # Both literals are individually permitted; division overflows to infinity.
    with pytest.raises(ExpressionRejected, match="non-finite"):
        safe_arithmetic("1000000 / 1e-308")
```

Expected result: all tests pass. Arithmetic exceptions such as division by zero intentionally propagate in this teaching implementation; a production API may normalize them to a documented domain error. Never return raw tracebacks to clients.

## 7. Resource exhaustion and isolation

### 7.1 CPU, memory, and recursion

Expressions such as `9**9**9`, huge string/list multiplication, extremely deep syntax, or large literal containers can consume disproportionate resources. Never “test” these by running uncontrolled payloads in a production process. Use bounded test cases and isolated workers with hard time/memory limits. `ast.literal_eval()` also has resource-exhaustion caveats; it is not a universal defense against hostile input.

### 7.2 In-process restrictions are not hostile-code isolation

Python has a rich object model and many runtime capabilities. Removing built-ins, filtering globals, or using a restricted execution wrapper cannot reliably make arbitrary Python safe against a determined attacker. A separate process reduces shared state but is insufficient if it inherits credentials, filesystem access, network access, or excessive privileges. Harden the OS boundary and assume the workload will try to escape its intended policy.

### 7.3 Practical isolation controls

- Run as a dedicated non-root user with no production secrets.
- Use an ephemeral filesystem; mount only required inputs read-only.
- Disable or tightly constrain network egress.
- Apply CPU, memory, process-count, file-size, and wall-clock limits.
- Cap stdin/stdout/stderr and terminate process trees on timeout.
- Use a container/VM/microVM or managed execution service appropriate to risk; keep host mounts and capabilities minimal.
- Patch the host kernel/runtime and monitor isolation failures.
- Do not reuse a worker after untrusted execution if residual state may cross tenants.
- Log identity, input digest, policy decision, resource usage, and exit status without logging secrets or sensitive source unnecessarily.

## 8. Production security controls

### 8.1 Audit hooks: monitoring, not prevention

`sys.addaudithook()` can observe selected runtime events such as `compile`, `exec`, imports, and file operations. Hooks can support detection, diagnostics, and policy telemetry, but they are not a complete sandbox or guaranteed universal prevention mechanism. Events and arguments depend on the operation; native extensions and process-level behavior complicate coverage. A Python audit hook cannot substitute for OS isolation.

```python
import sys

def audit(event, args):
    if event in {"compile", "exec", "import", "open"}:
        print("AUDIT EVENT:", event)

sys.addaudithook(audit)
code = compile("value = 4", "<audit-demo>", "exec")
namespace = {}
exec(code, namespace)
print(namespace["value"])
```

Expected output includes audit-event lines for events emitted by the running Python build, followed by `4`. Exact event arguments and event ordering can vary; do not write tests that assume an identical full trace across versions. Install hooks early when appropriate. Audit hooks are primarily observability controls, not the trust boundary.

### 8.2 Code-review checklist for dangerous APIs

Search and review every use of:

- `eval`, `exec`, `compile`, `__import__`, and `importlib` dynamic loading;
- `pickle.loads`, `pickle.load`, and unsafe object deserialization;
- `yaml.load` without a safe loader and schema validation;
- `subprocess` with `shell=True`, shell command construction, or untrusted command arguments;
- template engines configured to evaluate arbitrary expressions;
- dynamic SQL or query languages built by string concatenation;
- `marshal` or other internal serialization formats treated as trusted input.

For each finding, establish data provenance, reachable code paths, namespace/capability authority, validation, execution boundary, and resource controls. A grep is a useful starting point, not a complete static analysis: aliases, wrappers, helper functions, and dynamic dispatch can hide flows.

### 8.3 LLM-generated code

Treat model output exactly like untrusted third-party code. Prompt instructions and model confidence are not security controls. Do not execute generated code in the application server, CI runner, developer workstation, or credential-bearing agent process. If execution is needed, place it in an isolated worker, provide only minimal test fixtures, restrict network/filesystem access, use time/memory limits, review outputs, and validate any returned data against a schema. Never allow generated code to choose its own sandbox configuration or gain credentials based on its own claims.

### 8.4 Legitimate uses of dynamic execution

Dynamic compilation can be reasonable for trusted, generated source in carefully controlled library internals, REPLs/notebooks, benchmarking tools, or code-generation systems. The critical assumptions are that source construction is controlled, untrusted values are represented as data rather than interpolated as syntax, execution authority is appropriate, and failure/observability behavior is designed. Some standard-library and third-party libraries generate source for performance or introspection; that is not precedent for evaluating arbitrary user text.

## 9. Adversarial exercises and solutions

### Exercise 1 — choose the parser

A service accepts `{"timeout": 5, "enabled": true}` as user configuration. Should it use `eval`, `literal_eval`, or JSON?

**Solution:** JSON plus schema validation. It matches the data format and does not interpret Python code. Enforce payload size, allowed keys, types, and ranges.

### Exercise 2 — numeric calculator

Replace `eval(user_expression)` with a safe calculator supporting `+`, `-`, `*`, `/`, and parentheses. What must be rejected?

**Solution:** parse with `ast.parse(..., mode="eval")`, interpret only numeric `Constant`, approved `UnaryOp`, and approved `BinOp` nodes; reject names, calls, attributes, subscripts, containers, comparisons, and all unknown nodes. Add length, depth, node-count, numeric magnitude, and division-by-zero tests. The sample in Section 6 is a fuller version.

### Exercise 3 — “empty builtins” review

A reviewer sees `eval(expression, {"__builtins__": {}})` and marks it safe. What is wrong with that conclusion?

**Solution:** the mapping only restricts ordinary built-in-name lookup. Python's object model and reachable objects mean arbitrary Python is not confined by that mapping. Replace it with a defined interpreter or execute arbitrary code behind OS-level isolation.

### Exercise 4 — audit hook

An application logs `exec` audit events and assumes malicious code is prevented. Is that sufficient?

**Solution:** no. Logging supports detection and incident analysis; it does not guarantee prevention or complete event coverage. Enforce the boundary through a restricted language and/or OS isolation.

### Exercise 5 — LLM-produced migration script

An LLM writes a database migration script. What controls are required before running it?

**Solution:** review the source and intended changes, run only in a disposable isolated environment with synthetic or least-privilege data, no production secrets, network/filesystem restrictions, CPU/memory/time limits, and explicit approval before production deployment. Treat model output as untrusted regardless of prompt.

## 10. Interview questions

1. **What is the difference between `eval`, `exec`, and `compile`?** `eval` evaluates an expression; `exec` executes a statement suite; `compile` creates a code object without executing it.
2. **Why is `eval(..., {"__builtins__": {}})` unsafe as a sandbox?** Restricting built-in names does not isolate Python's object model or all reachable capabilities.
3. **When is `ast.literal_eval` appropriate?** Parsing supported Python literal structures, not expressions or calls; resource limits still matter.
4. **Why use JSON/TOML over Python syntax for configuration?** Data formats keep values separate from executable code and have simpler schemas.
5. **What does a safe expression interpreter need?** A small grammar, explicit node/operator allow-list, exact value types, bounds, rejection of unknown syntax, tests, and resource controls.
6. **Why is AST allow-listing alone not a complete DoS defense?** Parsing occurs first, and permitted operations or input complexity may still consume resources; apply size and process-level limits.
7. **What changed in Python 3.13 around locals?** PEP 667 formalized snapshot/proxy semantics for optimized scopes; writes to `locals()` do not mutate ordinary fast locals. Avoid depending on older behavior.
8. **What do audit hooks provide?** Runtime observability for selected events, not a complete prevention or isolation boundary.
9. **Why is a container not automatically a sandbox?** Its security depends on runtime configuration, privileges, mounts, credentials, kernel/runtime integrity, and resource/network policy.
10. **How should LLM-generated code be handled?** As untrusted code, executed only in a properly isolated, least-privilege environment if execution is necessary.

## 11. Final security checklist

- [ ] No untrusted input reaches `eval()` or `exec()`.
- [ ] `compile()` is treated as code preparation, not execution or validation of trust.
- [ ] Config uses JSON/TOML or another data format plus schema validation.
- [ ] `ast.literal_eval()` is used only for supported literals and bounded inputs.
- [ ] User expressions run through a documented, tested grammar and AST interpreter.
- [ ] Unknown AST nodes/operators and unexpected value types are rejected by default.
- [ ] Input length, node count/depth, numeric magnitude, exponentiation, and output size are bounded where applicable.
- [ ] Resource limits are enforced outside the interpreter for exposed services.
- [ ] Arbitrary code runs only in a disposable, least-privilege isolated worker when unavoidable.
- [ ] Workers have no production secrets and minimal filesystem/network access.
- [ ] Audit hooks are treated as monitoring, not the security boundary.
- [ ] Review covers `pickle`, YAML loaders, dynamic imports, shell execution, and template/query injection.
- [ ] LLM-generated code is treated as untrusted and never runs in a credential-bearing process.
- [ ] Python-version-sensitive namespace assumptions are tested on every supported interpreter.

## References for further verification

- Python documentation: `eval`, `exec`, `compile`, `ast.literal_eval`, `ast`, `sys.addaudithook`, and `locals`.
- PEP 667: Consistent views of namespaces.
- Python `pickle` documentation: warning about unpickling untrusted data.
- `RestrictedPython` project documentation: restricted execution is not a sandbox.
- OWASP guidance on code injection, insecure deserialization, and command injection.

**Core principle:** prefer data over code; prefer a deliberately small interpreter over general Python; and when arbitrary code must run, enforce isolation outside the Python process.
