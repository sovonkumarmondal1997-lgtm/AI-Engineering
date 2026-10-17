# Designing Declarative APIs and Mini-DSLs

> **Module:** Stage 1 — Programming & Computational Thinking, `12-Metaprogramming-and-Dynamic-Python/`  
> **Lesson:** 10 — Integration capstone for Lessons 01–09  
> **Level:** Beginner → advanced  
> **Primary goal:** Design small declarative interfaces that are readable, inspectable, typed as far as practical, testable, and safe by default.

## Learning outcomes

By the end of this lesson, you should be able to:

- Contrast imperative instructions with declarative descriptions of intent.
- Build fluent APIs and immutable query builders that can be safely reused.
- Explain why `&` and `|` can construct expression trees while `and` and `or` cannot provide equivalent overloadable behavior.
- Represent expressions as data, validate them, and interpret or compile them later.
- Collect declarative fields with descriptors, `__set_name__`, and `__init_subclass__`.
- Design useful errors, reasonable typing support, parameterized SQL, and compatibility policies.
- Test a complete mini-DSL, including invalid inputs and security boundaries.
- Decide when ordinary functions are better than a DSL.

---

# 1. Prerequisites and design principles

This lesson combines earlier module concepts: introspection; dynamic attribute access; decorators; class decorators and factories; `__init_subclass__`; `type()` and dynamic class creation; metaclasses; AST parsing and transformation; and the risks of `eval()`/`exec()`. A DSL is not a reason to use every metaprogramming feature. Prefer the least magical design that meets the requirement.

## 1.1 What is a DSL?

A **domain-specific language (DSL)** is a constrained interface designed around a particular problem domain. It may be a string grammar (`"age > 18"`), a Python API (`col("age") > 18`), a declarative class (`class User(Schema): ...`), a decorator (`@task`), or a context manager (`with pipeline(): ...`). A **mini-DSL** deliberately supports only a small, documented subset of operations.

A declarative API describes **what** is wanted. An implementation decides **how** to do it. Declarative does not mean “no code runs”; it means the user expresses intent through a structured contract.

## 1.2 The simplest-first design ladder

1. Plain function with keyword arguments.
2. A small immutable data object or builder.
3. Named expression objects and explicit validation.
4. Operator overloading for genuinely domain-natural syntax.
5. Descriptors, decorators, context managers, or class hooks when declarations need collection.
6. A string parser or AST only when a string grammar is a real product requirement.
7. A metaclass only when simpler hooks cannot express the invariant.

At every rung, ask: is readability improved enough to justify debugging, typing, documentation, and compatibility costs?

## 1.3 Imperative and declarative styles for the same task

Imperative: the caller specifies steps.

```python
people = [
    {"name": "Asha", "age": 31},
    {"name": "Ben", "age": 17},
    {"name": "Chen", "age": 24},
]
result = []
for person in people:
    if person["age"] > 18:
        result.append(person["name"])
print(result)
```

Expected output:

```text
['Asha', 'Chen']
```

Declarative with ordinary Python functions:

```python
people = [
    {"name": "Asha", "age": 31},
    {"name": "Ben", "age": 17},
    {"name": "Chen", "age": 24},
]
result = [p["name"] for p in people if p["age"] > 18]
print(result)
```

Expected output is the same. The comprehension is declarative relative to the explicit loop, but it is still ordinary Python—not a separate query language. A DSL becomes useful when it enables additional behavior such as validation, query planning, SQL compilation, explainability, or execution against different backends.

## 1.4 Design principles

- **Explicit grammar:** document which operations, types, fields, and combinations are valid.
- **Safe defaults:** values are parameters, identifiers are validated/quoted by backend rules, and execution is explicit.
- **Immutable descriptions:** prefer values that describe a query without mutating a shared builder.
- **Separation of concerns:** build → validate → explain/compile → execute.
- **Useful errors:** tell users what failed and how to fix it; avoid exposing secrets.
- **Introspection:** `repr()`, structured nodes, and `.explain()` should reveal what the API built.
- **No unnecessary magic:** use functions when a function is clearer.
- **Compatibility:** treat public node classes, error messages, generated SQL, and accepted syntax as API contracts.

---

# 2. Builder patterns

A fluent interface chains method calls. A method may mutate and return `self`, or return a new value. Mutable builders can be efficient for local construction, but shared mutable state is easy to misuse. Immutable builders make branching and reuse predictable.

## 2.1 Small immutable query builder

This first version stores **validated column names and parameter values separately**. It intentionally supports only simple equality predicates; it is a teaching example, not a complete SQL library.

```python
from dataclasses import dataclass
import re

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def check_identifier(name: str) -> str:
    if not isinstance(name, str) or not _IDENTIFIER.fullmatch(name):
        raise ValueError(f"invalid SQL identifier: {name!r}")
    return name


@dataclass(frozen=True)
class Query:
    table: str
    filters: tuple[tuple[str, object], ...] = ()
    row_limit: int | None = None

    def __post_init__(self) -> None:
        check_identifier(self.table)
        if not isinstance(self.filters, tuple):
            raise TypeError("filters must be a tuple of (column, value) pairs")
        for item in self.filters:
            if not isinstance(item, tuple) or len(item) != 2:
                raise TypeError("each filter must be a (column, value) tuple")
            name, _value = item
            check_identifier(name)
        if self.row_limit is not None:
            if isinstance(self.row_limit, bool) or not isinstance(self.row_limit, int):
                raise TypeError("limit must be an integer")
            if not 1 <= self.row_limit <= 10_000:
                raise ValueError("limit must be between 1 and 10000")

    def where_eq(self, column: str, value: object) -> "Query":
        check_identifier(column)
        return Query(self.table, (*self.filters, (column, value)), self.row_limit)

    def limit(self, count: int) -> "Query":
        return Query(self.table, self.filters, count)

    def compile_sql(self) -> tuple[str, tuple[object, ...]]:
        sql = f'SELECT * FROM "{self.table}"'
        params: list[object] = []
        if self.filters:
            clauses = []
            for column, value in self.filters:
                clauses.append(f'"{column}" = ?')
                params.append(value)
            sql += " WHERE " + " AND ".join(clauses)
        if self.row_limit is not None:
            # The limit is validated as an integer and is emitted as a literal here.
            # A backend with parameter support for LIMIT can parameterize it too.
            sql += f" LIMIT {self.row_limit}"
        return sql, tuple(params)


base = Query("users")
active = base.where_eq("active", True)
recent = active.limit(20)
print(base.compile_sql())
print(active.compile_sql())
print(recent.compile_sql())
```

Expected output:

```text
('SELECT * FROM "users"', ())
('SELECT * FROM "users" WHERE "active" = ?', (True,))
('SELECT * FROM "users" WHERE "active" = ? LIMIT 20', (True,))
```

`base`, `active`, and `recent` are distinct immutable query values. Extending `active` does not mutate `base`; a branch can be reused safely:

```python
base = Query("users")
active = base.where_eq("active", True)
by_region = active.where_eq("region", "EU")
by_role = active.where_eq("role", "admin")
assert len(base.filters) == 0
assert len(active.filters) == 1
assert len(by_region.filters) == len(by_role.filters) == 2
```

### Important SQL boundary

The roadmap's shortest `Query.sql()` sketch accepts string conditions and interpolates them into SQL to demonstrate a fluent interface. Treat that snippet as a shape-only teaching sketch, not production code: never let user-controlled strings become SQL fragments. The builder here stores column/value pairs and binds values separately.

- `?` is a SQLite-style parameter placeholder. Placeholder syntax varies by DB-API driver (`?`, `%s`, `:name`, etc.). Use the placeholder style required by the selected driver.
- Values are passed separately to the database driver. Never interpolate untrusted values into SQL strings.
- SQL identifiers (table/column names) generally cannot be passed as value parameters. This example accepts only a conservative identifier grammar and quotes the validated names. Production code must follow the target database's identifier and quoting rules, including reserved words and schema-qualified names. For dynamic identifiers, prefer a backend-supported identifier composition API or a strict allow-list.
- `compile_sql()` constructs a query; it does **not** connect to a database or execute anything.
- A frozen dataclass is shallowly immutable. This example stores a tuple of pairs, but arbitrary mutable values may still be referenced as filter values. If deep immutability matters, constrain/copy values at the boundary.

## 2.2 Mutable versus immutable builders

| Property | Mutable builder | Immutable builder |
|---|---|---|
| Typical method result | Mutates `self`, often returns `self` | Returns a new object |
| Allocation | Often fewer allocations | More allocations for each extension |
| Branching/reuse | Can accidentally share later mutations | Natural, explicit branches |
| Concurrency | Requires careful ownership/synchronization | Safer to share if contained data is also immutable |
| Debugging | History may affect current object | Each value represents one state |
| Best fit | Local one-shot construction, internal performance-sensitive code | Public query descriptions, configuration, functional composition |

Immutability is not automatically faster or thread-safe in every detail. Measure real workloads, and ensure nested values are immutable or defensively copied.

## 2.3 Context-manager and decorator DSLs

A context manager can make a scoped workflow readable:

```python
from contextlib import contextmanager

@contextmanager
def transaction_scope(label: str):
    print(f"begin:{label}")
    try:
        yield
    except Exception:
        print(f"rollback:{label}")
        raise
    else:
        print(f"commit:{label}")

with transaction_scope("load"):
    print("work")
```

Expected output:

```text
begin:load
work
commit:load
```

This is a lifecycle DSL, not a database transaction implementation. A real transaction manager must integrate with the database connection and preserve exception semantics.

Decorators provide a declaration-time hook:

```python
from functools import wraps

def task(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"task:{fn.__name__}")
        return fn(*args, **kwargs)
    return wrapper

@task
def refresh():
    return "done"

print(refresh())
```

Expected output:

```text
task:refresh
done
```

Use decorators for cross-cutting behavior such as registration, validation, tracing, or retries. Preserve metadata with `functools.wraps`; handle async functions deliberately rather than assuming a synchronous wrapper correctly wraps coroutines.

---

# 3. Expression objects and operator overloading

An expression DSL returns objects describing operations rather than immediately returning booleans or computed results. This enables later validation, optimization, SQL compilation, or interpretation.

## 3.1 Why `&` and `|`, not `and` and `or`?

Python's `and` and `or` are language-level short-circuiting control-flow operators. They evaluate truthiness and return one of their operands; they cannot be overloaded with `__and__`/`__or__` equivalents. A DSL therefore commonly uses bitwise operators `&` and `|` to construct logical nodes.

Operator precedence matters: bitwise `&` and `|` bind more tightly than comparisons, which can make an unparenthesized expression parse differently than intended. Parenthesize each comparison:

```python
condition = (col("age") > 18) & (col("score") >= 70)
```

Do not write `col("age") > 18 and col("score") >= 70` expecting a tree. Python will ask the first expression object for truthiness; a robust DSL should make that fail clearly.

## 3.2 Define the expression grammar first

The mini-DSL below supports only:

- A field reference created by `col(name)` where `name` belongs to an explicit schema.
- Numeric or string literal values appropriate for a field.
- Comparisons `==`, `!=`, `<`, `<=`, `>`, `>=` between a field and a compatible literal.
- Logical composition with `&` and `|` between expression objects.
- No arbitrary Python evaluation, calls, attribute access, arithmetic expressions, negation, implicit truthiness, or chained comparisons.

This is intentionally small. Adding syntax means adding validation, evaluation/compilation rules, typing decisions, tests, and documentation.

## 3.3 A typed expression tree and interpreter

The tree is data. `Compare` and `Logical` nodes do not execute when constructed. Evaluation happens only when `evaluate()` is called, against a record mapping after validation.

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping, TypeAlias

FieldTypes = dict[str, type]


class Expr:
    def __and__(self, other: "Expr") -> "Expr":
        if not isinstance(other, Expr):
            return NotImplemented
        return Logical("and", self, other)

    def __or__(self, other: "Expr") -> "Expr":
        if not isinstance(other, Expr):
            return NotImplemented
        return Logical("or", self, other)

    def __bool__(self) -> bool:
        raise TypeError("DSL expressions have no truth value; use '&' or '|', not 'and' or 'or'")

    def evaluate(self, row: Mapping[str, Any], schema: FieldTypes) -> bool:
        raise NotImplementedError

    def explain(self, indent: int = 0) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class Column(Expr):
    name: str

    def _check(self, schema: FieldTypes) -> type:
        if self.name not in schema:
            raise ValueError(f"unknown field {self.name!r}; expected one of {sorted(schema)}")
        expected = schema[self.name]
        if not isinstance(expected, type):
            raise TypeError(f"schema entry for {self.name!r} must be a runtime type")
        return expected

    def _compare(self, op: str, value: object) -> "Compare":
        return Compare(self, op, value)

    def __eq__(self, value: object) -> "Compare":  # type: ignore[override]
        return self._compare("==", value)

    def __ne__(self, value: object) -> "Compare":  # type: ignore[override]
        return self._compare("!=", value)

    def __lt__(self, value: object) -> "Compare":
        return self._compare("<", value)

    def __le__(self, value: object) -> "Compare":
        return self._compare("<=", value)

    def __gt__(self, value: object) -> "Compare":
        return self._compare(">", value)

    def __ge__(self, value: object) -> "Compare":
        return self._compare(">=", value)

    # Identity hashing only; use `name` for semantic lookup. This does not make
    # `Column == Column` a boolean comparison because __eq__ builds a DSL node.
    __hash__ = object.__hash__

    def evaluate(self, row: Mapping[str, Any], schema: FieldTypes) -> bool:
        raise TypeError("a bare column is not a boolean condition")

    def explain(self, indent: int = 0) -> str:
        return " " * indent + f"Column({self.name!r})"


@dataclass(frozen=True, eq=False)
class Compare(Expr):
    left: Column
    op: str
    value: object

    def _validate(self, row: Mapping[str, Any], schema: FieldTypes) -> Any:
        expected = self.left._check(schema)
        if self.left.name not in row:
            raise ValueError(f"row is missing field {self.left.name!r}")
        if expected is int:
            # bool is a subclass of int; reject it for a strict integer field.
            valid = isinstance(self.value, int) and not isinstance(self.value, bool)
            actual_valid = isinstance(row[self.left.name], int) and not isinstance(row[self.left.name], bool)
        elif expected is float:
            valid = isinstance(self.value, (int, float)) and not isinstance(self.value, bool)
            actual_valid = isinstance(row[self.left.name], (int, float)) and not isinstance(row[self.left.name], bool)
        else:
            valid = isinstance(self.value, expected)
            actual_valid = isinstance(row[self.left.name], expected)
        if not valid:
            raise TypeError(f"value for {self.left.name!r} must be {expected.__name__}")
        if not actual_valid:
            raise TypeError(f"row field {self.left.name!r} must be {expected.__name__}")
        if self.op not in {"==", "!=", "<", "<=", ">", ">="}:
            raise ValueError(f"unsupported comparison operator {self.op!r}")
        return row[self.left.name]

    def evaluate(self, row: Mapping[str, Any], schema: FieldTypes) -> bool:
        actual = self._validate(row, schema)
        if self.op == "==": return actual == self.value
        if self.op == "!=": return actual != self.value
        if self.op == "<": return actual < self.value
        if self.op == "<=": return actual <= self.value
        if self.op == ">": return actual > self.value
        if self.op == ">=": return actual >= self.value
        raise AssertionError("operator validation invariant violated")

    def explain(self, indent: int = 0) -> str:
        return " " * indent + f"Compare(field={self.left.name!r}, op={self.op!r}, value={self.value!r})"


@dataclass(frozen=True, eq=False)
class Logical(Expr):
    op: str
    left: Expr
    right: Expr

    def __post_init__(self) -> None:
        if self.op not in {"and", "or"}:
            raise ValueError(f"unsupported logical operator {self.op!r}")
        if not isinstance(self.left, Expr) or not isinstance(self.right, Expr):
            raise TypeError("logical operands must be expression objects")

    def evaluate(self, row: Mapping[str, Any], schema: FieldTypes) -> bool:
        if self.op == "and":
            return self.left.evaluate(row, schema) and self.right.evaluate(row, schema)
        return self.left.evaluate(row, schema) or self.right.evaluate(row, schema)

    def explain(self, indent: int = 0) -> str:
        pad = " " * indent
        return f"{pad}Logical({self.op!r})\n{self.left.explain(indent + 2)}\n{self.right.explain(indent + 2)}"


def col(name: str) -> Column:
    if not isinstance(name, str) or not name.isidentifier():
        raise ValueError(f"invalid field name {name!r}")
    return Column(name)


SCHEMA: FieldTypes = {"age": int, "score": int, "country": str}
ROWS = [
    {"age": 31, "score": 90, "country": "DE"},
    {"age": 17, "score": 95, "country": "DE"},
    {"age": 25, "score": 61, "country": "IN"},
]

expr = (col("age") > 18) & ((col("score") >= 70) | (col("country") == "IN"))
print(expr.explain())
print([row for row in ROWS if expr.evaluate(row, SCHEMA)])
```

Expected output:

```text
Logical('and')
  Compare(field='age', op='>', value=18)
  Logical('or')
    Compare(field='score', op='>=', value=70)
    Compare(field='country', op='==', value='IN')
[{'age': 31, 'score': 90, 'country': 'DE'}, {'age': 25, 'score': 61, 'country': 'IN'}]
```

### Notes on this implementation

- The expression tree is **constructed** by operator methods and **evaluated** only by `.evaluate()`. It is not using `eval()` and does not parse user-supplied Python source.
- `__bool__` deliberately raises to catch accidental use of `and`/`or` or `if expr:`. This is a common defensive design for expression DSLs.
- The interpreter validates fields and value types during evaluation. A production system should validate the whole tree against the schema once before iterating many rows, rather than repeating schema checks for every row.
- This example uses Python's type objects in a small trusted schema. For richer type semantics, nullability, decimal/date types, or coercion, define an explicit type system instead of relying on `isinstance` alone.
- Overloading `__eq__` has consequences: dataclasses, collections, and static type checkers may expect boolean equality. The `type: ignore` comments are local hints, not proof of clean typing. `Compare` and `Logical` disable generated structural equality (`eq=False`) so dataclass equality does not accidentally truth-test a `Column.__eq__` expression. Expression-node equality is therefore identity-based; it is not a DSL predicate. Many mature DSLs use a distinct expression base and carefully document these semantics; a static checker may still need overloads or stubs.
- The implementation supports only `Column op literal` comparisons. It does not support column-to-column comparisons, reverse comparisons such as `18 < col("age")`, chained comparisons, null semantics, arithmetic, unary `~`, or automatic coercion. Those are intentionally unsupported, not silently accepted.

## 3.4 Testing invalid combinations

```python
schema = {"age": int, "country": str}
row = {"age": 22, "country": "DE"}

assert (col("age") > 18).evaluate(row, schema) is True
assert (col("country") == "DE").evaluate(row, schema) is True

for bad in (col("missing") > 1,):
    try:
        bad.evaluate(row, schema)
    except ValueError as exc:
        print(type(exc).__name__, str(exc))

try:
    (col("age") > "18").evaluate(row, schema)
except TypeError as exc:
    print(type(exc).__name__, str(exc))

try:
    bool(col("age") > 18)
except TypeError as exc:
    print(type(exc).__name__, str(exc))

try:
    col("age") > 18 and col("age") < 60
except TypeError as exc:
    print(type(exc).__name__, str(exc))
```

Expected behavior: the unknown field raises `ValueError`, the wrong literal type raises `TypeError`, and both explicit truth conversion and `and` raise the message explaining that expressions have no truth value. The last `and` expression fails at truth testing of its left operand before it can construct a logical node.

---

# 4. Declarative class and schema definitions

Descriptors are useful when a class body declares fields and the framework must learn each field's name and metadata. `__set_name__(owner, name)` is called by Python when the descriptor is assigned in the class namespace. `__init_subclass__` can collect inherited and newly declared descriptors when a subclass is created.

## 4.1 A small descriptor-based schema

```python
class Field:
    def __init__(self, expected_type: type, *, required: bool = True):
        self.expected_type = expected_type
        self.required = required
        self.name: str | None = None

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.name not in instance.__dict__:
            raise AttributeError(f"field {self.name!r} has not been set")
        return instance.__dict__[self.name]

    def __set__(self, instance, value) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(f"{self.name} must be {self.expected_type.__name__}")
        instance.__dict__[self.name] = value


class Schema:
    __fields__: dict[str, Field] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        fields: dict[str, Field] = {}
        for base in reversed(cls.__mro__[1:]):
            fields.update(getattr(base, "__fields__", {}))
        fields.update({name: value for name, value in vars(cls).items() if isinstance(value, Field)})
        cls.__fields__ = fields

    def __init__(self, **values):
        unknown = set(values) - set(self.__fields__)
        if unknown:
            raise TypeError(f"unexpected fields: {sorted(unknown)}")
        missing = [name for name, field in self.__fields__.items()
                   if field.required and name not in values]
        if missing:
            raise TypeError(f"missing required fields: {missing}")
        for name, value in values.items():
            setattr(self, name, value)


class User(Schema):
    name = Field(str)
    age = Field(int)


user = User(name="Mira", age=28)
print(user.name, user.age)
print(sorted(User.__fields__))
```

Expected output:

```text
Mira 28
['age', 'name']
```

This is an instructional schema, not a replacement for Pydantic or attrs. It intentionally leaves out defaults, aliases, nested validation, immutable instances, field removal/override rules, generated signatures, serialization, and static typing integration. It also inherits Python's `bool`-is-an-`int` relationship; if `Field(int)` must reject booleans, add an explicit check. In production, specify inheritance/override semantics and test them.

## 4.2 `__signature__`, `dataclass_transform`, and typing

A framework may expose a synthetic `inspect.Signature` through `__signature__` so help systems and IDE tooling can inspect a dynamic constructor. That metadata does not change runtime behavior by itself; the actual `__init__` must still validate and bind arguments consistently.

`typing.dataclass_transform` (available in the standard library from Python 3.11) tells static type checkers that a decorator, base class, or metaclass behaves similarly to a dataclass. It does not generate runtime methods automatically. `Generic[T]` expresses parameterized relationships; `typing.overload` provides multiple static call signatures while a single implementation handles runtime calls. Stub files (`.pyi`) can describe dynamic APIs when the implementation cannot be inferred. Verify support with the type checker and versions your project actually uses.

A reasonable strategy:

- Keep runtime validation authoritative.
- Add annotations and generics for stable, expressible relationships.
- Use `overload` for meaningful call-shape distinctions.
- Use `dataclass_transform` only when the framework truly follows dataclass-like semantics.
- Provide stubs or generated typing metadata for dynamic fields.
- Document limitations; do not claim “type-checker clean” without running a named checker against a pinned version.

---

# 5. Deferred interpretation and compilation

The expression tree is an intermediate representation. It can be interpreted against Python objects, compiled to parameterized SQL, translated to another backend, validated, optimized, or explained. Keep these stages separate:

1. **Build:** operators create immutable node objects.
2. **Validate:** check field names, operators, types, nesting, and backend capability.
3. **Explain:** display the structure without executing the query.
4. **Compile:** convert the tree to a backend-specific representation and bound parameters.
5. **Execute:** pass the compiled query and parameter sequence to a driver.

A tiny parameterized SQL compiler for the expression classes above could be added like this (SQLite-style `?` placeholders):

```python
def compile_expr(expr: Expr, schema: FieldTypes) -> tuple[str, tuple[object, ...]]:
    params: list[object] = []

    def visit(node: Expr) -> str:
        if isinstance(node, Compare):
            node.left._check(schema)
            # Validate operator and literal type before producing SQL.
            if node.op not in {"==", "!=", "<", "<=", ">", ">="}:
                raise ValueError(f"unsupported operator {node.op!r}")
            expected = schema[node.left.name]
            if expected is int:
                valid = isinstance(node.value, int) and not isinstance(node.value, bool)
            elif expected is float:
                valid = isinstance(node.value, (int, float)) and not isinstance(node.value, bool)
            else:
                valid = isinstance(node.value, expected)
            if not valid:
                raise TypeError(f"value for {node.left.name!r} must be {expected.__name__}")
            params.append(node.value)
            sql_op = {"==": "=", "!=": "<>"}.get(node.op, node.op)
            return f'"{node.left.name}" {sql_op} ?'
        if isinstance(node, Logical):
            if node.op not in {"and", "or"}:
                raise ValueError(f"unsupported logical operator {node.op!r}")
            return f"({visit(node.left)} {'AND' if node.op == 'and' else 'OR'} {visit(node.right)})"
        raise TypeError(f"unsupported expression node: {type(node).__name__}")

    return visit(expr), tuple(params)

expr = (col("age") > 18) & (col("country") == "DE")
print(compile_expr(expr, {"age": int, "country": str}))
```

Expected output:

```text
('("age" > ? AND "country" = ?)', (18, 'DE'))
```

The compiler validates expression nodes and values, and binds values separately. The roadmap's minimal `Cmp.sql()` example embeds `repr(value)` to illustrate tree-to-text translation; that is not a safe production SQL compiler. This snippet assumes the schema keys are trusted identifiers created by application code; a production compiler should apply the target dialect's identifier quoting and reserved-word rules. **Do not execute SQL by concatenating parameter values into the SQL string.** The next step would be a driver call such as `cursor.execute(sql, params)`, which is intentionally omitted here to keep compilation separate from execution.

## 5.1 Explainability and diagnostics

An `.explain()` method should show the tree, not execute it. For larger systems, include stable node names, inferred types, source labels, backend decisions, and parameter placeholders—but do not print secret parameter values in production logs. Prefer structured diagnostics (`code`, `message`, `path`, `hint`) over parsing exception strings.

Examples of useful errors:

- `unknown field 'agge'; did you mean 'age'?`
- `operator '>=' does not support str and int`
- `empty filter is not allowed for destructive operation`
- `backend 'sqlite' does not support expression node 'RegexMatch'`

Avoid silently coercing types or accepting unsupported syntax. If coercion is part of the API, make it explicit and documented.

---

# 6. Security and parameterization

A declarative API is not secure merely because it looks structured. Its implementation must enforce a grammar and preserve the distinction between **data** and **instructions**.

## 6.1 SQL injection

Unsafe pattern (do not use):

```python
# UNSAFE: untrusted input changes SQL syntax.
# sql = f"SELECT * FROM users WHERE name = '{user_input}'"
```

Safe value handling uses the driver's parameter mechanism:

```python
# SQLite example; `user_input` is data, not SQL syntax.
import sqlite3

connection = sqlite3.connect(":memory:")
connection.execute("CREATE TABLE users (name TEXT)")
connection.execute("INSERT INTO users(name) VALUES (?)", ("O'Reilly",))
user_input = "O'Reilly"
rows = connection.execute("SELECT name FROM users WHERE name = ?", (user_input,)).fetchall()
print(rows)
connection.close()
```

Expected output:

```text
[("O'Reilly",)]
```

Parameters generally represent values, not table names, column names, or SQL keywords. For identifiers, use a strict allow-list and/or a dialect-aware identifier composition feature; never assume quoting arbitrary input is sufficient for every database dialect.

## 6.2 String DSLs and `eval()`

Do not implement a filter by passing a user-provided string to `eval()`. Even if the grammar is intended to be small, Python expression syntax can reach far beyond the intended domain, and restricting `__builtins__` is not a security boundary. Prefer, in order:

1. Ordinary functions or explicit structured data.
2. Expression objects such as the tree built above.
3. A parser for a deliberately small grammar.
4. An AST allow-list that rejects every unapproved node and operator, with explicit resource bounds.

If a string grammar is necessary, parse it and interpret only supported nodes; never execute the resulting arbitrary Python code. Remember that node allow-lists still need limits for input size, node count, nesting, numeric magnitude, and expensive operations. Treat all inputs as adversarial when they cross a trust boundary.

## 6.3 Empty conditions and dangerous defaults

An empty filter can mean “all rows.” That may be acceptable for a read-only listing, but it is dangerous for update/delete APIs. Make the semantics explicit and require a separate opt-in for broad mutations. Similarly, validate limits as integers in a sensible range; reject `True` if a strict integer is required because `bool` subclasses `int`.

---

# 7. Production architecture and trade-offs

## 7.1 Recommended layers

```text
Public API / declarations
        ↓
Input validation and type checking
        ↓
Immutable expression tree / query model
        ↓
Validation against schema and backend capabilities
        ↓
Explain / optimize / compile
        ↓
Parameterized execution adapter (optional)
        ↓
Database, in-memory collection, or other backend
```

Keep backend-specific SQL out of the public expression nodes when practical. Separate dialect compilation from execution so unit tests can verify the compiler without requiring a database. Integration tests should then verify the driver boundary and database semantics.

## 7.2 Performance

Building a tree costs allocations and dispatches; for trivial one-off work, a list comprehension or normal function is likely simpler and faster. The tree pays for itself when you need deferred execution, multiple backends, validation, optimization, caching, or explainability.

- Measure tree construction, validation, compilation, and execution separately.
- Validate once and reuse a compiled plan when schema and dialect remain compatible.
- Do not cache blindly: keys must include every semantic input (schema, dialect, options), and cached objects must be safe to share.
- Avoid repeatedly traversing the same tree for every record. Compile an interpreter/plan once if profiling shows this is material.
- Bound expression depth and node count when inputs can be externally supplied.
- Preserve parameterization in every backend; a faster unsafe string formatter is not an optimization.

## 7.3 API evolution and documentation

Treat accepted operators, error types, `repr`, `.explain()`, generated signatures, and serialization as potential compatibility surfaces. Add new operators in a backward-compatible way; avoid changing the meaning of an existing operator. Deprecate behavior in stages, provide migration examples, and test documentation examples as doctests or executable snippets. Document unsupported features explicitly.

## 7.4 When ordinary functions are clearer

| Ordinary function | DSL |
|---|---|
| `filter_adults(rows, min_age=18)` | `col("age") >= 18` |
| Easy to type, debug, and call | Can be composed, inspected, optimized, and compiled |
| Execution usually immediate | Often deferred until interpretation/compilation |
| Limited to implemented operations | Can expose a domain grammar, but requires strict validation |
| Best for small stable tasks | Best when structured composition or multiple backends are valuable |

The restraint test from the roadmap: write both forms and ask whether the DSL provides real value. If not, keep the function.

---

# 8. Case study: SQLAlchemy-style declarative querying

The roadmap names SQLAlchemy's declarative API as one case-study option. The important pattern is not any one implementation detail; it is the architecture:

1. A class declaration maps fields to metadata (table, column, type, constraints).
2. Attribute access returns an instrumented object rather than merely a plain value in class context.
3. Comparisons construct expression objects.
4. `&`/`|` or dedicated combinators compose conditions.
5. A dialect-aware compiler translates the tree into SQL and bound parameters.
6. A connection/engine executes the compiled statement.

Illustrative SQLAlchemy 2.x style (requires SQLAlchemy installed and a model configured):

```python
# Illustrative API shape; requires SQLAlchemy 2.x and a configured mapping.
# stmt = select(User).where((User.age > 18) & (User.country == "DE"))
# result = session.execute(stmt)
```

This is not a self-contained runnable program because the `User` mapping, engine, session, and schema are application-specific. The lesson is the separation between declaration, expression construction, compilation, and execution. Consult the installed SQLAlchemy version's documentation for exact APIs and dialect behavior; do not infer security solely from a query's appearance.

Compare this with Pydantic, attrs, Typer, or Click: each turns declarations or annotations into runtime behavior, but the domain differs. Pydantic focuses on validation/serialization, attrs on class generation and attributes, and Typer/Click on command-line interfaces. A good case study traces where metadata is collected, when validation occurs, and how errors reach the user.

---

# 9. Complete mini-DSL project

This capstone combines an immutable query object, a small expression tree, a strict schema, a parameterized SQL compiler, and an in-memory interpreter. It deliberately does not execute arbitrary Python and does not open a database connection.

## 9.1 Acceptance criteria

- Valid comparisons and logical composition work.
- Unknown fields, invalid types, non-expression logical operands, and invalid limits fail clearly.
- Empty filters are allowed for query construction but visibly produce no `WHERE` clause; mutation APIs would need stricter policy.
- SQL values are placeholders plus a parameter tuple.
- Query objects can be branched and reused without interference.
- `.explain()` exposes the tree.
- Unsupported nodes/operators are rejected rather than guessed.

## 9.2 Suggested project layout

```text
declarative_mini_dsl/
├── pyproject.toml
├── README.md
├── DESIGN.md
├── src/
│   └── declquery/
│       ├── __init__.py
│       ├── expressions.py
│       ├── query.py
│       └── schema.py
└── tests/
    ├── test_expressions.py
    ├── test_query.py
    ├── test_security.py
    └── test_schema.py
```

## 9.3 Compact end-to-end implementation

The following is runnable as a single file on Python 3.10+. It uses only the standard library. Save it as `mini_dsl.py`.

```python
from __future__ import annotations
from dataclasses import dataclass
import re
from typing import Any, Mapping

IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def identifier(name: str) -> str:
    if not isinstance(name, str) or not IDENTIFIER.fullmatch(name):
        raise ValueError(f"invalid identifier: {name!r}")
    return name


class Expr:
    def __and__(self, other: "Expr") -> "Expr":
        if not isinstance(other, Expr): return NotImplemented
        return Logic("AND", self, other)

    def __or__(self, other: "Expr") -> "Expr":
        if not isinstance(other, Expr): return NotImplemented
        return Logic("OR", self, other)

    def __bool__(self) -> bool:
        raise TypeError("expression has no truth value; use '&' or '|'")

    def evaluate(self, row: Mapping[str, Any], schema: Mapping[str, type]) -> bool:
        raise NotImplementedError

    def explain(self) -> str:
        raise NotImplementedError


@dataclass(frozen=True, eq=False)
class Col(Expr):
    name: str

    def __post_init__(self): identifier(self.name)

    def _cmp(self, op: str, value: object) -> "Cmp": return Cmp(self, op, value)
    def __eq__(self, value: object) -> "Cmp": return self._cmp("=", value)  # type: ignore[override]
    def __ne__(self, value: object) -> "Cmp": return self._cmp("!=", value)  # type: ignore[override]
    def __lt__(self, value: object) -> "Cmp": return self._cmp("<", value)
    def __le__(self, value: object) -> "Cmp": return self._cmp("<=", value)
    def __gt__(self, value: object) -> "Cmp": return self._cmp(">", value)
    def __ge__(self, value: object) -> "Cmp": return self._cmp(">=", value)

    def evaluate(self, row, schema): raise TypeError("column is not a condition")
    def explain(self): return f"Col({self.name!r})"


@dataclass(frozen=True, eq=False)
class Cmp(Expr):
    column: Col
    op: str
    value: object

    def _validate(self, row, schema):
        name = self.column.name
        if name not in schema: raise ValueError(f"unknown field {name!r}")
        if name not in row: raise ValueError(f"row missing field {name!r}")
        expected = schema[name]
        if expected is int:
            ok = isinstance(self.value, int) and not isinstance(self.value, bool)
            row_ok = isinstance(row[name], int) and not isinstance(row[name], bool)
        elif expected is float:
            ok = isinstance(self.value, (int, float)) and not isinstance(self.value, bool)
            row_ok = isinstance(row[name], (int, float)) and not isinstance(row[name], bool)
        else:
            ok = isinstance(self.value, expected)
            row_ok = isinstance(row[name], expected)
        if not ok: raise TypeError(f"comparison value for {name!r} must be {expected.__name__}")
        if not row_ok: raise TypeError(f"row value for {name!r} must be {expected.__name__}")
        if self.op not in {"=", "!=", "<", "<=", ">", ">="}:
            raise ValueError(f"unsupported operator {self.op!r}")
        return row[name]

    def evaluate(self, row, schema):
        actual = self._validate(row, schema)
        operations = {
            "=": lambda a, b: a == b, "!=": lambda a, b: a != b,
            "<": lambda a, b: a < b, "<=": lambda a, b: a <= b,
            ">": lambda a, b: a > b, ">=": lambda a, b: a >= b,
        }
        return operations[self.op](actual, self.value)

    def explain(self): return f"Cmp({self.column.name!r} {self.op} {self.value!r})"


@dataclass(frozen=True, eq=False)
class Logic(Expr):
    op: str
    left: Expr
    right: Expr

    def __post_init__(self):
        if self.op not in {"AND", "OR"}: raise ValueError(f"unsupported logical operator {self.op!r}")
        if not isinstance(self.left, Expr) or not isinstance(self.right, Expr):
            raise TypeError("logical operands must be expressions")

    def evaluate(self, row, schema):
        if self.op == "AND": return self.left.evaluate(row, schema) and self.right.evaluate(row, schema)
        return self.left.evaluate(row, schema) or self.right.evaluate(row, schema)

    def explain(self): return f"{self.op}(\n  {self.left.explain()}\n  {self.right.explain()}\n)"


def col(name: str) -> Col: return Col(name)


@dataclass(frozen=True)
class Query:
    table: str
    condition: Expr | None = None
    row_limit: int | None = None

    def __post_init__(self):
        identifier(self.table)
        if self.condition is not None and not isinstance(self.condition, Expr):
            raise TypeError("condition must be an Expr or None")
        if self.row_limit is not None:
            if isinstance(self.row_limit, bool) or not isinstance(self.row_limit, int):
                raise TypeError("limit must be an integer")
            if not 1 <= self.row_limit <= 10_000:
                raise ValueError("limit must be between 1 and 10000")

    def where(self, condition: Expr) -> "Query":
        if not isinstance(condition, Expr): raise TypeError("where() expects an expression")
        combined = condition if self.condition is None else self.condition & condition
        return Query(self.table, combined, self.row_limit)

    def limit(self, count: int) -> "Query": return Query(self.table, self.condition, count)

    def explain(self) -> str:
        return f"Query(table={self.table!r}, limit={self.row_limit!r}, condition={self.condition.explain() if self.condition is not None else 'None'})"

    def compile_sql(self, schema: Mapping[str, type]) -> tuple[str, tuple[object, ...]]:
        # The schema is application-controlled metadata, but validate its shape at
        # this boundary so malformed configuration fails with an actionable error.
        for field_name, field_type in schema.items():
            identifier(field_name)
            if not isinstance(field_type, type):
                raise TypeError(f"schema entry for {field_name!r} must be a runtime type")
        params: list[object] = []

        def visit(node: Expr) -> str:
            if isinstance(node, Cmp):
                name = node.column.name
                if name not in schema: raise ValueError(f"unknown field {name!r}")
                if node.op not in {"=", "!=", "<", "<=", ">", ">="}:
                    raise ValueError(f"unsupported operator {node.op!r}")
                expected = schema[name]
                if expected is int:
                    valid_value = isinstance(node.value, int) and not isinstance(node.value, bool)
                elif expected is float:
                    valid_value = isinstance(node.value, (int, float)) and not isinstance(node.value, bool)
                else:
                    valid_value = isinstance(node.value, expected)
                if not valid_value:
                    raise TypeError(f"comparison value for {name!r} must be {expected.__name__}")
                params.append(node.value)
                sql_op = {"=": "=", "!=": "<>", "<": "<", "<=": "<=", ">": ">", ">=": ">="}[node.op]
                return f'"{name}" {sql_op} ?'
            if isinstance(node, Logic):
                if node.op not in {"AND", "OR"}: raise ValueError(f"unsupported logical operator {node.op!r}")
                return f"({visit(node.left)} {node.op} {visit(node.right)})"
            raise TypeError(f"unsupported expression node {type(node).__name__}")

        sql = f'SELECT * FROM "{self.table}"'
        if self.condition is not None: sql += " WHERE " + visit(self.condition)
        if self.row_limit is not None: sql += f" LIMIT {self.row_limit}"
        return sql, tuple(params)


if __name__ == "__main__":
    schema = {"age": int, "country": str}
    q0 = Query("users")
    q1 = q0.where((col("age") >= 18) & (col("country") == "DE"))
    q2 = q1.limit(50)
    print(q0.compile_sql(schema))
    print(q2.compile_sql(schema))
    print(q2.explain())
```

Expected output:

```text
('SELECT * FROM "users"', ())
('SELECT * FROM "users" WHERE ("age" >= ? AND "country" = ?) LIMIT 50', (18, 'DE'))
Query(table='users', limit=50, condition=AND(
  Cmp('age' >= 18)
  Cmp('country' = 'DE')
))
```

> **Implementation note:** `explain()` is intended for inspection, not a stable serialization format. A production implementation should use a consistent tree renderer and avoid tests that are brittle to whitespace; test semantic structure separately. `Col.__eq__` constructs a comparison node, so `Cmp` and `Logic` use `eq=False` and retain identity-based equality. Do not use `==` to compare expression-tree structure; implement an explicit structural comparison if that is a requirement.

## 9.4 Tests

Save the implementation above as `mini_dsl.py`, then save the following as `test_mini_dsl.py`. From that directory, run `python -m unittest -v test_mini_dsl` (module name, without `.py`).

```python
import unittest
from mini_dsl import Cmp, Expr, Logic, Query, col

SCHEMA = {"age": int, "country": str}


class MiniDSLTests(unittest.TestCase):
    def test_empty_query(self):
        self.assertEqual(Query("users").compile_sql(SCHEMA), ('SELECT * FROM "users"', ()))

    def test_valid_expression_compiles_to_parameters(self):
        query = Query("users").where((col("age") >= 18) & (col("country") == "DE")).limit(50)
        sql, params = query.compile_sql(SCHEMA)
        self.assertEqual(sql, 'SELECT * FROM "users" WHERE ("age" >= ? AND "country" = ?) LIMIT 50')
        self.assertEqual(params, (18, "DE"))

    def test_immutable_branching(self):
        base = Query("users")
        adults = base.where(col("age") >= 18)
        german = adults.where(col("country") == "DE")
        self.assertIsNone(base.condition)
        self.assertIsNotNone(adults.condition)
        self.assertIsNot(adults.condition, german.condition)

    def test_expression_node_equality_does_not_truth_test_dsl_comparisons(self):
        first = col("age") > 18
        second = col("age") > 18
        # Expression nodes use identity equality; `Col.__eq__` builds a DSL node.
        self.assertFalse(first == second)

    def test_builder_rejects_mutable_filter_container(self):
        with self.assertRaises(TypeError):
            Query("users", filters=[("age", 18)])

    def test_invalid_identifier(self):
        with self.assertRaises(ValueError): Query("users; DROP TABLE users")
        with self.assertRaises(ValueError): col("age.name")

    def test_unknown_field(self):
        with self.assertRaisesRegex(ValueError, "unknown field"):
            Query("users").where(col("salary") > 1).compile_sql(SCHEMA)

    def test_wrong_value_type(self):
        with self.assertRaises(TypeError):
            Query("users").where(col("age") > "18").compile_sql(SCHEMA)

    def test_value_is_parameterized_not_interpolated(self):
        value = "DE' OR 1=1 --"
        sql, params = Query("users").where(col("country") == value).compile_sql(SCHEMA)
        self.assertEqual(sql, 'SELECT * FROM "users" WHERE "country" = ?')
        self.assertEqual(params, (value,))
        self.assertNotIn(value, sql)

    def test_invalid_schema_metadata(self):
        with self.assertRaisesRegex(TypeError, "runtime type"):
            Query("users").compile_sql({"age": "int"})

    def test_unsupported_expression_node_is_rejected(self):
        class CustomExpr(Expr):
            pass
        with self.assertRaisesRegex(TypeError, "unsupported expression node"):
            Query("users", CustomExpr()).compile_sql(SCHEMA)

    def test_invalid_condition(self):
        with self.assertRaises(TypeError): Query("users").where("age > 18")

    def test_invalid_limits(self):
        for bad in (0, -1, 10_001):
            with self.subTest(bad=bad), self.assertRaises(ValueError): Query("users").limit(bad)
        for bad in (True, 2.5, "10"):
            with self.subTest(bad=bad), self.assertRaises(TypeError): Query("users").limit(bad)

    def test_bool_conversion_is_rejected(self):
        with self.assertRaises(TypeError): bool(col("age") > 18)

    def test_unsupported_operator_is_rejected(self):
        from mini_dsl import Cmp
        expression = Cmp(col("age"), "**", 2)
        with self.assertRaisesRegex(ValueError, "unsupported operator"):
            Query("users", expression).compile_sql(SCHEMA)

    def test_invalid_logical_operator_is_rejected(self):
        from mini_dsl import Logic
        with self.assertRaisesRegex(ValueError, "unsupported logical operator"):
            Logic("XOR", col("age") > 18, col("age") < 60)


if __name__ == "__main__":
    unittest.main()
```

The tests deliberately do not connect to a database. They verify the model and compiler boundary. Add integration tests against the actual DB-API driver, plus tests for inherited schemas, null handling, field overrides, reserved identifiers, dialect differences, and maximum expression depth if those features are added.

### Suggested `DESIGN.md` decisions

- Why use immutable query values instead of mutating a shared builder?
- Why use expression objects instead of `eval()` or a string grammar?
- Which identifiers are accepted and why?
- Which SQL dialect and parameter style are supported?
- Why is execution separate from compilation?
- What are the unsupported expression forms?
- How will new operators, nodes, and backends be versioned?
- Which performance benchmarks would justify compilation caching?

---

# 10. Exercises with solutions

## Exercise 1 — Choose the simplest interface

You need to select records with `status="ready"` from a small in-memory list, once per run. Should you build a DSL?

**Solution:** Usually no. Use a comprehension or function with keyword arguments. A DSL is justified if you need composable expressions, explainability, query optimization, or multiple backends.

## Exercise 2 — Why does `and` fail?

Explain why this does not construct a SQL predicate:

```python
# condition = (col("age") > 18) and (col("score") > 70)
```

**Solution:** `and` is not overloadable. It truth-tests its left operand and short-circuits. If an expression's `__bool__` raises, it fails clearly; use parenthesized expressions joined by `&`.

## Exercise 3 — Add `>=` to a compiler

What must change when a new comparison operator is added?

**Solution:** Add it to the expression builder, validation allow-list, interpreter, compiler mapping, type rules, explanation output, documentation, and tests. Adding it in only one layer creates inconsistent behavior.

## Exercise 4 — Secure dynamic identifiers

Why is `cursor.execute("SELECT * FROM ?", (table_name,))` generally not a valid way to parameterize a table name?

**Solution:** SQL parameters bind values, not syntax elements such as identifiers. Use a strict allow-list or a dialect-aware identifier API, and validate identifiers separately from value parameters.

## Exercise 5 — Empty filters

A delete API uses the same `Query` object. Is an empty condition safe?

**Solution:** Not by default. An empty condition can mean all rows. Make broad mutations require an explicit, separate opt-in or reject an empty condition for update/delete operations.

## Exercise 6 — Type checking dynamic schemas

How can IDEs and type checkers understand fields generated by a base class?

**Solution:** Prefer statically visible declarations when possible; use `Generic`, `overload`, `.pyi` stubs, or `dataclass_transform` when its semantics genuinely match. These mechanisms communicate information to static tools; they do not replace runtime validation or generate methods automatically in every case.

## Exercise 7 — Expression-tree safety

A teammate proposes parsing `"age > 18 and country == 'DE'"` with `eval()` and an empty builtins dictionary. What should you recommend?

**Solution:** Reject that approach. Use expression objects or a parser with a small, explicit grammar and strict node/type/resource limits. Empty builtins is not a secure sandbox for arbitrary Python execution.

## Exercise 8 — Add a regression test

Write a test proving that adding a second filter does not mutate the original query.

**Solution:**

```python
base = Query("users")
first = base.where(col("age") >= 18)
second = first.where(col("country") == "DE")
assert base.condition is None
assert first.condition is not None
assert second.condition is not first.condition
```

---

# 11. Interview questions

1. What makes an API declarative, and how is that different from a string DSL?
2. When is a fluent interface useful, and when does it become harder to debug?
3. Compare mutable and immutable builders in terms of aliasing, reuse, allocation, and concurrency.
4. Why can `&` and `|` construct expression objects while `and` and `or` cannot be overloaded equivalently?
5. What is the role of `__bool__` in an expression DSL?
6. How do descriptors and `__set_name__` support declarative field definitions?
7. What can `__init_subclass__` do that a descriptor alone cannot do?
8. Explain the interpreter pattern for expression trees.
9. Why should query construction, compilation, and execution be separate?
10. How do parameterized queries prevent value-based SQL injection?
11. Why do SQL identifiers require a separate strategy from value parameters?
12. How would you validate field names, operators, and types?
13. What should `.explain()` reveal, and what should it avoid logging?
14. What do `Generic`, `overload`, `.pyi` files, and `dataclass_transform` contribute?
15. What are the limitations of static typing for dynamically generated fields?
16. How would you test a DSL's invalid combinations and error messages?
17. What compatibility promises does a public DSL make?
18. How would you benchmark and cache compiled expressions safely?
19. When would ordinary keyword arguments be clearer than a DSL?
20. How does SQLAlchemy's declarative/query model separate declarations, expressions, compilation, and execution?

---

# 12. Completion checklist

- [ ] I can show imperative and declarative forms of the same task.
- [ ] I can justify a builder instead of a plain function.
- [ ] I can explain the trade-offs of mutable and immutable builders.
- [ ] I can build expression objects with comparisons and logical composition.
- [ ] I understand why DSLs commonly use `&`/`|`, with parentheses, rather than `and`/`or`.
- [ ] I can collect fields with descriptors, `__set_name__`, and `__init_subclass__`.
- [ ] I can separate expression construction, validation, explanation, compilation, and execution.
- [ ] I can implement useful errors and an inspectable `.explain()` method.
- [ ] I can describe the practical roles and limitations of `Generic`, `overload`, stubs, and `dataclass_transform`.
- [ ] I never use `eval()` to interpret an untrusted DSL.
- [ ] I parameterize SQL values and validate/quote identifiers according to the backend.
- [ ] I test empty conditions, invalid fields/types/operators, and invalid limits.
- [ ] I can explain why a DSL may be slower than ordinary code and how to benchmark it.
- [ ] I completed the mini-DSL and documented its grammar, limitations, and compatibility policy.

## Final engineering rule

**A good DSL makes valid intent easy to express, invalid intent easy to diagnose, and unsafe behavior difficult to trigger.** Keep the grammar small, the expression tree inspectable, and the execution boundary explicit. Use ordinary Python until a declarative layer demonstrably improves composition, validation, portability, or explainability.
