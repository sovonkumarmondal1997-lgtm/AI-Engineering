# Refactoring Catalogue: From Local Python Changes to Safe Architectural Evolution

> **Module:** Stage 1 — Programming & Computational Thinking · Module 23 — Code Reading, Refactoring and Code Review  
> **Repository path:** `Stage 1 — Programming & Computational Thinking/23-Code-Reading-Refactoring-and-Code-Review/03-refactoring-catalogue.md`  
> **Lesson:** 03 of 08  
> **Target environment:** Python 3.12+, Git 2.40+, `pytest`, `ruff`, `mypy` or `pyright`; optional `radon`, `coverage`, `import-linter`, `libcst`, and `rope`.

## Learning outcomes

After completing this lesson, you should be able to:

- Define refactoring precisely and distinguish it from feature work, bug fixes, and rewrites.
- Apply small, named transformations with tests and reviewable commits protecting externally observable behaviour.
- Select a suitable transformation from a practical catalogue rather than applying patterns mechanically.
- Evolve Python functions and public APIs using delegation and expand–migrate–contract sequencing.
- Improve domain models, conditional logic, inheritance, module boundaries, tests, data pipelines, notebooks, and ML paths.
- Use codemods and architecture checks for repetitive or cross-package changes.
- Detect “refactors” that accidentally change evaluation order, exceptions, I/O, floating-point results, laziness, mutability, or equality.
- Measure the impact of a refactor and present evidence in a pull request.
- Complete the capstone: refactor a characterized 200-line function into well-named units using a parameter object, guard clauses, and a dispatch table, with at least 15 small passing commits and a documented final PR.

## 1. What refactoring is—and is not

**Refactoring is a disciplined change to the internal structure of software that preserves its externally observable behaviour.** The goal is to make code easier to understand, test, extend, or operate without changing what callers, users, downstream systems, or operators can observe.

Observable behaviour includes more than a return value. It can include:

- Function signatures and accepted input forms.
- Return values, ordering, and mutation of caller-owned objects.
- Exceptions, exception types, and when they are raised.
- Database writes, emitted events, file contents, API responses, and network calls.
- Logging and metrics relied on by operations or integrations.
- Timing, resource usage, and performance constraints where these are part of the service contract.
- Compatibility with persisted schemas, serialized payloads, command-line flags, and import paths.

A refactor may change names, decomposition, class structure, or dependency direction. If you intend to change externally observable behaviour, call that out as a separate behaviour change, with its own rationale and tests. Do not hide a bug fix inside a “cleanup” commit.

### Why refactor?

- **Comprehension:** reduce cognitive load through clear names and cohesive units.
- **Changeability:** put behaviour where it belongs and reduce shotgun changes across modules.
- **Testability:** isolate pure domain rules from databases, clocks, network calls, and filesystem effects.
- **Reliability:** make invariants visible and failure paths easier to verify.
- **Performance, when measured:** remove avoidable work or improve algorithms without guessing.
- **Safe evolution:** create boundaries that allow gradual replacement of legacy implementations.

### Limits and trade-offs

Refactoring is not automatically beneficial. A new abstraction can add indirection; a class can be less clear than a function; a dispatch table can hide control flow; a generator can make execution lazy; a dataclass can accidentally change equality semantics. Avoid restructuring code solely to match a fashionable pattern. Prefer the smallest transformation that solves a concrete maintenance problem.

### Refactoring versus adjacent activities

| Activity | Primary intent | Example | How to keep it distinct |
|---|---|---|---|
| Refactoring | Improve internal structure, preserve behaviour | Extract `calculate_tax()` | Existing behaviour tests remain green |
| Feature development | Add capability | Support a new invoice currency | New behaviour and tests are explicit |
| Bug fix | Change incorrect behaviour | Reject a negative quantity | Regression test demonstrates the defect and fix |
| Rewrite | Replace a substantial implementation | Replace a legacy ETL service | Needs migration plan, parity evidence, and rollback strategy |
| Formatting / mechanical cleanup | Normalize presentation or repetitive structure | Apply formatter | Inspect generated diff; formatter output alone does not prove safety |

A defect discovered during refactoring should be recorded separately. Preserve it during the structural phase unless leaving it unchanged is unsafe; if an urgent fix must happen immediately, split the work and document the behaviour change explicitly.

## 2. Preconditions and the safe-refactoring loop

### Five rules from the roadmap

1. **No behaviour change** during a pure refactor.
2. **Small steps**: make one coherent, easy-to-review change at a time.
3. **Tests green after each step**: run the narrow test first, then the broader suite.
4. **Commit often**: each commit should explain one transformation and be independently understandable.
5. **Separate refactor commits from feature and bug-fix commits.**

These are not a guarantee that behaviour is preserved. Tests can be incomplete or encode only a subset of the contract. Supplement them with characterization tests, type checking, static analysis, diff review, and runtime evidence appropriate to the risk.

### Preconditions checklist

Before changing code:

- [ ] Identify the callers, public API, entry points, and downstream consumers.
- [ ] Run existing tests and record baseline failures; do not attribute pre-existing failures to your change.
- [ ] Add or improve tests around the behaviour you will touch, including edge and error paths.
- [ ] Capture representative output for large reports, ETL partitions, or serialized payloads when useful.
- [ ] Note side effects: writes, network calls, logging, mutation, timing, retries, and import-time behaviour.
- [ ] Check repository status and start from a known commit.
- [ ] Identify performance-critical paths and benchmark them before changing their algorithm or allocation pattern.
- [ ] Decide how to roll back the change or disable it if deployed behind a toggle.

### The change loop

```text
Understand contract → add/confirm tests → make one small change
        ↑                                      ↓
review diff ← run tests + types + lint ← inspect result
        ↓
commit one coherent transformation → repeat
```

Example commands (adapt to the repository's actual tooling and configuration):

```bash
git status --short
git switch -c refactor/invoice-calculation
uv run pytest -q tests/test_invoice.py
uv run ruff check src tests
uv run mypy src
# Make one change, then:
uv run pytest -q tests/test_invoice.py
uv run pytest -q
git diff --check
git diff --stat
git diff
git add src tests && git commit -m "refactor: extract invoice subtotal"
```

`mypy src` is appropriate only if the project has mypy configured and the selected source scope is supported; otherwise use the project's configured `pyright`/mypy command. `ruff check --fix` can apply supported mechanical fixes, but inspect the diff and run tests. `git restore` can discard uncommitted changes, but is destructive to those changes; use it only after reviewing `git status` and confirming the target. Prefer reverting a committed change with `git revert <commit>` on shared branches rather than rewriting shared history.

**Focused commits are a risk-control mechanism.** Avoid bundling a rename, an algorithm change, dependency upgrades, and formatting of unrelated files into one PR. A reviewer should be able to state the intent and expected invariant of each commit.

## 3. Beginner catalogue: small structural transformations

Each entry gives the intent, prerequisites/mechanics, risk, and a Python example. The examples are illustrative; in a real codebase, tests must establish the actual contract before changing implementation.

### 3.1 Rename variable, function, class, or module

**Intent:** make a name express its meaning without changing behaviour.

Before:

```python
def calc(xs):
    s = 0
    for x in xs:
        s += x.price * x.qty
    return s
```

After:

```python
def calculate_subtotal(line_items):
    subtotal = 0
    for line_item in line_items:
        subtotal += line_item.price * line_item.qty
    return subtotal
```

Use IDE symbol-aware rename for Python references, then search strings, imports, configuration, reflection, plugin registries, serialized names, and documentation. A rename can break `getattr(obj, "name")`, import paths, CLI entry points, or external consumers even when static references update cleanly.

### 3.2 Extract Function

**Intent:** give a cohesive operation a name, reduce nesting, and create a testable unit.

Before:

```python
def invoice_total(items, tax_rate):
    subtotal = sum(item.price * item.quantity for item in items)
    tax = subtotal * tax_rate
    return subtotal + tax
```

After:

```python
def subtotal(items):
    return sum(item.price * item.quantity for item in items)


def invoice_total(items, tax_rate):
    amount = subtotal(items)
    tax = amount * tax_rate
    return amount + tax
```

**Risk:** extracting a block can change local-variable scope, exception timing, evaluation order, or whether a value is computed once or multiple times. Extract side-effect-free logic first where possible; characterize side effects and call counts where they matter.

### 3.3 Inline Function

Use when a tiny wrapper adds no meaningful name or policy. Replace the call with its body, then remove the function only after searching all references. Do not inline a meaningful domain name merely to save a line; names can communicate intent and provide a stable seam.

```python
def is_billable(order):
    return order.status == "paid"

# Inline only if the wrapper adds no useful domain meaning:
if order.status == "paid":
    ...
```

If `is_billable()` is an extension point or a central policy, retaining it is usually better.

### 3.4 Extract Variable and Inline Variable

Extract a variable to name a complex expression or make a boundary visible:

```python
# Before
if user.active and user.verified and not user.suspended and user.balance >= minimum:
    approve(user)

# After
eligible_for_approval = (
    user.active and user.verified and not user.suspended and user.balance >= minimum
)
if eligible_for_approval:
    approve(user)
```

Inline a temporary when its name merely repeats the expression and the expression is cheap, pure, and clear:

```python
# Before
is_empty = len(records) == 0
if is_empty:
    return None

# After
if not records:
    return None
```

For ordinary lists, these conditions are equivalent. For a custom container, `bool(records)` may be defined differently from `len(records) == 0`; confirm the collection contract before applying the rewrite.

**Risk:** do not inline an expression with side effects or expensive/non-repeatable evaluation. A variable can intentionally freeze a value at one point in time.

### 3.5 Change Function Declaration safely

Do not rename or reorder a widely used public parameter in one step. Use **expand → migrate → contract**:

```python
# Existing public function; keep it working during migration.
def build_report(start_date, end_date, region=None):
    return build_report_for_period(start_date, end_date, region=region)


def build_report_for_period(start_date, end_date, *, region=None):
    # New canonical implementation.
    return _render_report(start_date, end_date, region)
```

Migrate internal callers to `build_report_for_period`, publish deprecation guidance if external callers exist, measure remaining use where possible, and remove the old entry point only in a planned breaking release. The example keeps the old positional shape. If the original function accepted keyword calls such as `region=`, preserve that compatibility too. If it accepted arbitrary positional arguments, inspect the full contract before wrapping.

**Compatibility checklist:** positional calls, keyword calls, defaults, introspection (`inspect.signature`), decorators, type stubs, docs, CLI bindings, plugin discovery, serialization, and downstream packages. A wrapper can preserve ordinary calls but still alter signature introspection, traceback frames, or warnings; test those if contractual.

### 3.6 Replace magic numbers/literals with named constants or enums

```python
# Before
if retry_count > 3:
    raise RuntimeError("bad status")

# After
MAX_RETRIES = 3
ERROR_MESSAGE = "bad status"

if retry_count > MAX_RETRIES:
    raise RuntimeError(ERROR_MESSAGE)
```

For a finite domain, an enum may be clearer:

```python
from enum import StrEnum

class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
```

**Risk:** a string enum member may compare equal to its string value but can change serialization, type identity, display, validation, and consumer expectations. Keep wire-format values stable and test them explicitly. Do not name every literal; only extract values that have domain meaning or are repeated/likely to change.

### 3.7 Introduce Parameter Object

Use when multiple parameters form one concept and travel together. A dataclass can make the contract visible:

```python
from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class ReportPeriod:
    start_date: date
    end_date: date
    region: str | None = None


def build_report(period: ReportPeriod) -> str:
    if period.end_date < period.start_date:
        raise ValueError("end_date must not precede start_date")
    return f"{period.region or 'all'}:{period.start_date}:{period.end_date}"
```

**Important:** the example adds validation and therefore may change behaviour if the old function accepted reversed dates. Treat that as a separate intended behavior change, not a pure refactor. To preserve behaviour, first make the object represent the same accepted states and add validation in a separate change.

A frozen dataclass is not deeply immutable if it contains mutable members. Parameter objects can also affect keyword calls, introspection, serialization, equality, and API ergonomics. Introduce them internally first or use a compatibility wrapper for public APIs.

### 3.8 Replace Temp with Query

Before:

```python
def price_with_tax(price, rate):
    tax = price * rate
    return price + tax
```

After:

```python
def tax_amount(price, rate):
    return price * rate


def price_with_tax(price, rate):
    return price + tax_amount(price, rate)
```

Use a query when recomputation is cheap and pure. Keep a temporary if it prevents duplicate expensive work, freezes a changing value, or preserves evaluation order. A query that reads the clock, database, mutable global, or network is not equivalent to a previously computed temporary.

### 3.9 Split Variable

One variable should represent one concept. Avoid reusing a name for unrelated stages:

```python
# Before
value = amount
value = value * tax_rate
value = format(value, ".2f")
```

```python
# After: preserve the original behavior (format the tax amount only).
raw_amount = amount
tax_amount = raw_amount * tax_rate
formatted_value = f"{tax_amount:.2f}"
```

Split variables according to the actual data flow, not according to a preferred naming scheme. Tests should cover intermediate types and final output.

### 3.10 Remove Dead Code

Delete unreachable branches, unused functions, stale commented-out code, and obsolete configuration only after checking dynamic entry points, reflection, plugins, generated imports, and external callers. Tools such as `vulture` produce candidates, not proof. Prefer version-control history over keeping large commented-out blocks. For feature flags, verify rollout state and removal criteria before deleting either branch.

## 4. Intermediate catalogue: responsibilities, data, and control flow

### 4.1 Move Function or Method

**Intent:** place behaviour near the data and policy it primarily uses, or in the layer that owns the responsibility.

Before:

```python
class ReportService:
    def customer_display_name(self, customer):
        return f"{customer.last_name}, {customer.first_name}"
```

After (if the display name is a stable customer-domain responsibility):

```python
from dataclasses import dataclass

@dataclass
class Customer:
    first_name: str
    last_name: str

    def display_name(self) -> str:
        return f"{self.last_name}, {self.first_name}"
```

Do not move logic solely because it reads fields. Presentation formatting may belong in a presentation layer, while canonical customer identity belongs in the domain. Check import direction and dependency ownership.

### 4.2 Hide Delegate and Remove Middle Man

These are related but opposite moves. **Hide Delegate** adds a small operation on the owning object so callers do not navigate through its internal collaborator. **Remove Middle Man** removes forwarding methods when the wrapper adds no policy or stability and callers should use the collaborator directly. Choose based on ownership and API stability, not on line count alone.

Before (callers know the internal object graph):

```python
class Order:
    def __init__(self, customer):
        self.customer = customer

# Caller: order.customer.name
```

After Hide Delegate (assuming `Customer.name` is a stable public attribute):

```python
class Order:
    def __init__(self, customer):
        self._customer = customer

    @property
    def customer_name(self) -> str:
        return self._customer.name

# Caller: order.customer_name
```

This changes the caller-facing API and may affect reflection, serialization, and code that relied on `order.customer`; migrate callers and retain a compatibility property if required. Conversely, if a wrapper only forwards every method without adding policy, **Remove Middle Man** can simplify the API—but first search callers and verify that the wrapper is not a compatibility or security boundary.

### 4.3 Extract Class and Inline Class

Extract a class when one type owns multiple independent responsibilities or state groups. Keep cohesion high and the interface small. Inline a class when it adds no meaningful boundary and only forwards calls. Do not create a class just to hold a single stateless function; Python modules and functions are valid abstractions.

```python
# Before: parsing, retry policy, and persistence mixed together.
class Importer:
    def run(self, payload):
        rows = parse_csv(payload)
        rows = [r for r in rows if r["id"]]
        save_rows(rows)
```

```python
# After: responsibility boundaries can be tested independently.
def parse_valid_rows(payload):
    rows = parse_csv(payload)
    return [row for row in rows if row["id"]]

class Importer:
    def __init__(self, repository):
        self.repository = repository

    def run(self, payload):
        self.repository.save_all(parse_valid_rows(payload))
```

The example assumes `parse_csv` and repository behavior already exist. If filtering invalid rows is new, that is a behavior change; characterize and separate it first.

### 4.4 Encapsulate Record and Collection

Replace direct access to a mutable record with a small interface when invariants need enforcement. Encapsulate a collection when callers must not mutate it arbitrarily.

```python
from dataclasses import dataclass, field

@dataclass
class Batch:
    _rows: list[dict[str, object]] = field(default_factory=list, repr=False)

    def add(self, row: dict[str, object]) -> None:
        self._rows.append(row)

    def snapshot(self) -> tuple[dict[str, object], ...]:
        # This tuple freezes the container, not the nested dictionaries.
        return tuple(self._rows)
```

This example does **not** provide deep immutability. A caller can still mutate a dictionary in the returned tuple. If deep isolation is part of the contract, return immutable value objects or defensive copies and test aliasing behavior.

### 4.5 Replace primitive obsession or unstructured dictionaries

Use a value object where a primitive represents a domain concept with validation or behavior:

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if (
            len(self.currency) != 3
            or not self.currency.isascii()
            or not self.currency.isalpha()
        ):
            raise ValueError("currency must contain three ASCII letters")
```

That validation checks only a three-ASCII-letter shape; it does not validate membership in an ISO currency-code registry or enforce uppercase. It may be stricter than legacy behavior; apply it as an explicit contract change if necessary. Avoid creating wrappers that merely rename a primitive without enforcing a useful invariant.

Choose the data structure based on the contract:

- `dataclass`: domain object with named fields and often behavior.
- `TypedDict`: static description of a dictionary-shaped mapping; does not validate at runtime.
- `NamedTuple`: immutable tuple-like record; positional tuple behavior remains part of its interface.
- `Protocol`: structural interface for collaborators.
- Value object: identity is its value; useful for `Money`, `EmailAddress`, or `UserId` when invariants are meaningful.

Changing `dict` to dataclass may alter key access, serialization, equality, mutability, default handling, and pickling. Add adapters at boundaries instead of changing every consumer at once.

#### Change Value to Reference and Change Reference to Value

Use **Change Value to Reference** when multiple callers must observe one shared identity or synchronized mutable state; use **Change Reference to Value** when independent immutable values are safer and identity is not meaningful. These are not mechanical swaps: identity, aliasing, mutation visibility, equality, hashing, caching, persistence, and concurrency may change.

For example, replacing two separately constructed `Customer` records with a shared customer loaded from an identity map can make updates visible across callers. The reverse—copying a shared mutable settings object into immutable per-request values—can isolate requests, but it intentionally changes shared-state behavior. Characterize aliasing and lifecycle semantics before choosing either transformation; test whether `a is b`, equality, mutation visibility, and serialization are part of the contract.

### 4.6 Simplify conditional logic

#### Decompose conditional and consolidate conditions

```python
# Before
if account.active:
    if account.verified:
        if not account.locked:
            grant_access(account)
```

```python
# After: flatten only when the boolean expression is equivalent.
if account.active and account.verified and not account.locked:
    grant_access(account)
```

For ordinary attributes, these conditions are equivalent. If property access has side effects, can raise, or is expensive, changing access order or count can change behaviour. Guard clauses can make the main path easier to see:

```python
def process(record):
    if record is None:
        return None
    if not record.is_valid:
        return None
    return transform(record)
```

This is safe only if the old code returned the same result for these cases and did not intentionally perform side effects before returning.

#### Replace a conditional with a dispatch table

Before:

```python
def normalize(kind: str, value: str) -> str:
    if kind == "upper":
        return value.upper()
    elif kind == "lower":
        return value.lower()
    elif kind == "strip":
        return value.strip()
    else:
        raise ValueError(f"unknown kind: {kind}")
```

After:

```python
_OPERATIONS = {
    "upper": str.upper,
    "lower": str.lower,
    "strip": str.strip,
}


def normalize(kind: str, value: str) -> str:
    try:
        operation = _OPERATIONS[kind]
    except KeyError:
        raise ValueError(f"unknown kind: {kind}") from None
    return operation(value)
```

For the annotated contract `kind: str`, the dispatch table preserves the intended results and unknown-kind `ValueError` in this example. It is built once rather than on every call. A non-string, unhashable runtime value could raise `TypeError` at dictionary lookup whereas the original comparisons might not; if such inputs are in scope, validate them explicitly or preserve the original error behavior. Do not use `dict.get(kind, default)` unless missing-key behavior is truly the same. If the original code raises a different exception type or message, preserve that contract or document the change.

A dispatch table is ideal for stable key-to-callable mappings. It is not always better than `match`, `functools.singledispatch`, or polymorphism: use `match` for structured patterns, `singledispatch` when behavior is dispatched on the first argument's runtime type and registrations are useful, and polymorphism when behavior varies with object type and belongs to those objects. Python 3.10+ supports structural pattern matching:

```python
def classify(value: object) -> str:
    match value:
        case None:
            return "missing"
        case bool():
            return "boolean"
        case int():
            return "integer"
        case str():
            return "text"
        case _:
            return "other"
```

**Subtlety:** `bool` is a subclass of `int`; ordering `bool()` before `int()` is intentional. Reordering cases changes behaviour.

#### Introduce Special Case / Null Object

Replace repeated `if customer is None` checks with a `GuestCustomer` or explicit `UnknownCustomer` only when “no customer” has a stable domain meaning and the fallback semantics are safe. Do not invent a fake object that silently grants access or turns data errors into empty values. A Null Object may hide missing-data defects if used indiscriminately.

#### Introduce Assertion

Use `assert` for internal invariants that indicate programmer errors, not for validating untrusted input or enforcing business rules: Python can remove assertions under optimization (`python -O`). Use explicit exceptions for public contracts.

### 4.7 API and function-design transformations

- **Separate Query from Modifier:** a query returns information without changing state; a command changes state and makes its side effects clear. Do not split if the old API promises an atomic read-modify-write transaction without designing a replacement transaction boundary.
- **Parameterize Function:** combine duplicated algorithms that differ only in a stable parameter. Avoid a generic “do everything” function with a dozen options.
- **Remove Flag Argument:** replace `render(data, as_csv=True)` with named functions such as `render_csv(data)` and `render_json(data)` if the modes have distinct policies. Keep a flag when the modes are truly the same operation with one minor variation.
- **Preserve Whole Object:** pass a cohesive object rather than many of its fields, but avoid leaking a large mutable object across layers.
- **Replace Parameter with Query:** useful when a parameter is always derived from an existing stable object; risk: repeated computation or querying mutable state.
- **Replace Constructor with Factory Function:** use a named factory when creation involves variants or non-obvious setup; preserve exceptions and initialization side effects.
- **Replace Function with Command:** introduce a command object when an operation needs explicit state, retries, scheduling, auditing, serialization, or undo; do not wrap every function in a class by default.

### 4.8 Inheritance refactoring: pull up, push down, delegate

- **Pull Up Method/Field:** move duplicated shared behavior into a base class only when the subclasses truly share the same contract.
- **Push Down Method/Field:** move behavior used by only one subclass out of a broad base class.
- **Extract Superclass:** model a stable “is-a” relationship with shared substitutable behavior.
- **Collapse Hierarchy:** remove a subclass that adds no meaningful behavior or contract.
- **Replace Subclass with Delegate / Replace Superclass with Delegate:** prefer composition when the relationship is “uses” rather than “is-a”, when inheritance exposes unwanted methods, or when base-class changes break unrelated subclasses.

Liskov substitution is a constraint: an implementation must honor the base contract. Do not pull methods into a base class just to remove a few duplicate lines if semantics differ subtly. Composition introduces explicit delegation and can change method resolution, identity, `isinstance`, pickling, and extension behavior; test those interfaces if observable.

### 4.9 Python-specific refactorings and their traps

| Transformation | Typical benefit | Behaviour risks to check |
|---|---|---|
| Loop → list comprehension | Concise transformation | Scope, evaluation order, side effects, memory use |
| Loop → generator expression | Lazy streaming, lower peak memory | Work moves to iteration time; exceptions and side effects happen later; one-shot consumption |
| Loop → `itertools` | Clear iterator composition | Iterator exhaustion, grouping/sorting assumptions, laziness |
| Manual `open`/`close` → `with` | Reliable cleanup | Exception timing and resource lifetime; ensure the same mode/encoding/newline behavior |
| Getter/setter → `@property` | Natural attribute interface | Descriptor behavior, exceptions, introspection, assignment timing |
| Class with only data → dataclass | Less boilerplate | Generated `__init__`, `__repr__`, equality, ordering, mutability, slots, hashing |
| Callback → closure / `functools.partial` | Bind context without a class | Late binding in loops, captured mutable state, argument order |
| String concatenation → f-string / `join` | Clearer construction, sometimes lower overhead | Exact separators, conversion rules, repeated copying, evaluation order |
| Module global → injected dependency | Testability and explicit dependencies | Initialization order, default lifetime, import graph, concurrency |
| Script body → `main()` + importable functions | Reuse and testability | Import-time side effects and CLI exit-code behavior |

Examples:

```python
# Loop -> comprehension: equivalent when the expression is pure and order is preserved.
cleaned = [value.strip() for value in values if value.strip()]
```

The expression `value.strip()` is evaluated twice for retained values. If the operation is expensive or has side effects, use a loop that computes it once rather than this comprehension.

```python
# Resource handling
with open(path, "r", encoding="utf-8", newline="") as stream:
    text = stream.read()
```

This is safer than manually closing a file in only the happy path, but preserve encoding, newline handling, buffering, and the exact point where the file is opened.

```python
# Partial application
from functools import partial

def publish(topic: str, payload: bytes, *, retries: int = 3) -> None:
    ...

publish_events = partial(publish, "events", retries=5)
publish_events(b"created")
```

`partial` binds arguments; it does not make the underlying operation pure or thread-safe.

```python
def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    run_job(args)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Moving code under `main()` prevents it running on import, which is usually desirable but is an observable change if other code depended on import-time execution. Test CLI output, exit codes, and import safety separately.

## 5. Public API evolution: expand, migrate, contract

A public signature can be used by internal code, external packages, notebooks, scheduled jobs, CLI scripts, and reflection. Treat its callers as a compatibility surface.

Suppose an old function takes a `region` string and the new design wants a `ReportOptions` object. Do not replace it immediately:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ReportOptions:
    region: str | None = None
    include_inactive: bool = False


def build_report(start_date, end_date, region=None):
    """Compatibility wrapper for the old public API."""
    return build_report_with_options(
        start_date,
        end_date,
        ReportOptions(region=region),
    )


def build_report_with_options(start_date, end_date, options: ReportOptions):
    # New canonical implementation; preserve the existing report semantics.
    return _render_report(start_date, end_date, options.region)
```

This simplified example intentionally does not use `include_inactive`; if the new option is added to behavior, that must be separately specified and tested. Migration sequence:

1. **Expand:** add the new function/type and tests; keep old signature working.
2. **Migrate:** move first-party callers in small PRs; keep parity tests across old/new APIs.
3. **Observe:** use deprecation warnings, telemetry, search, or downstream integration tests to discover remaining usage. Avoid logging sensitive arguments.
4. **Deprecate:** document the removal version and replacement.
5. **Contract:** remove the old API only at a planned breaking-change boundary.
6. **Rollback:** retain the compatibility wrapper or revert the caller migration if issues appear.

Do not issue deprecation warnings on every hot-path call without considering log volume and warning filters. A public API may require a major version bump or a formal compatibility policy. Type checking is useful but cannot prove runtime compatibility for dynamic calls, reflection, serialized data, or downstream consumers.

## 6. Tests as refactoring protection

A refactoring test suite should verify behavior, not duplicate implementation line by line. A useful pyramid is:

1. Focused unit tests for pure rules and edge cases.
2. Characterization tests for legacy behavior, including awkward edge cases that must remain stable during the structural phase.
3. Integration tests at database, file, network, CLI, or API boundaries.
4. Contract tests for external consumers and serialized interfaces.
5. Performance benchmarks for critical paths, interpreted with noise and workload context.

### Test refactoring itself

Tests are production assets. Refactor duplicated setup into fixtures, parameterize repeated cases, and replace excessive mocks with small fakes when behavior matters. Do not abstract test helpers so heavily that the assertion becomes invisible. Avoid asserting private call sequences unless call order is part of the contract.

Bad test pattern:

```python
# Over-mocked: proves only that the mock was called with the expected value.
service.repo.save.assert_called_once_with(expected)
```

Better when practical: use an in-memory fake repository and assert the externally visible result, while keeping a smaller number of adapter tests for the real database integration.

### Type checks and static analysis

Run the project's configured type checker and linter after each coherent step. Add annotations before a high-risk refactor if they expose implicit contracts. Where practical, run `mypy --strict` on the touched module/package or use a configured strict subset; applying strict mode to an entire untyped legacy repository may be too broad as a first move. Start with the touched area and increase coverage incrementally. Static checks catch some mismatches, not semantic changes.

## 7. Advanced refactoring: across modules, packages, and services

### 7.1 Branch by abstraction

Use when a large implementation must be replaced while the system remains live:

1. Introduce a stable interface around the current implementation.
2. Make the old implementation satisfy that interface.
3. Add the new implementation behind the same interface.
4. Route a controlled slice to the new implementation.
5. Compare outputs and operational metrics.
6. Gradually move traffic, then remove the old implementation after evidence and a rollback window.

The abstraction should express a real stable contract, not simply add indirection. Keep the old path available until confidence and operational readiness justify removal. For a huge function that cannot be tested as a whole, use **Sprout Method/Class** (add a small tested unit and call it from the old function) or **Wrap Method/Class** (put a seam around the hard-to-change boundary) before attempting broad extraction. A **scratch refactor** can be useful to understand possible structure, but treat it as disposable exploration: record insights, discard the experiment, and redo the change as small tested commits. Do not mistake the scratch branch for production-ready work.

### 7.2 Strangler-fig migration and feature toggles

A facade routes requests to the old or new system. Migrate a bounded capability at a time, monitor parity and failure metrics, and keep a clear fallback. Feature toggles need an owner, expiry/removal condition, default, audit trail, and test coverage for both states. A stale toggle can become a new source of complexity or a dangerous hidden code path.

### 7.3 Expand–contract for database schemas and APIs

For a column rename or schema evolution:

- **Expand:** add the new column/field as optional or dual-readable; do not remove the old field yet.
- **Dual write or backfill:** make writes consistent, with idempotent migration and reconciliation checks.
- **Migrate readers:** switch consumers to the new field while monitoring nulls, lag, and parity.
- **Verify:** compare counts, constraints, and representative values; include old and new application versions in compatibility testing.
- **Contract:** remove the old field only when all consumers are migrated and rollback no longer depends on it.

A database migration is not a pure refactor if it changes persistence, locks, query plans, or data availability. Plan for partial failure, restartability, backfills, and rollback/roll-forward. A destructive schema migration may not be reversible after writes; backup and forward-repair procedures matter more than a nominal down migration.

### 7.4 Architecture boundaries and dependency inversion

A modular monolith is often a safer intermediate state than premature service extraction. Define package boundaries around domain capabilities and keep dependencies directed inward:

```text
HTTP / CLI / scheduler adapters
              ↓
        application use cases
              ↓
        domain rules/types
              ↑
database, queue, file, API adapters implement ports
```

The domain should not import a concrete database client just to save one record. Define a small protocol or callable boundary, then implement it in infrastructure. This makes tests faster and reduces cyclic imports.

Practical steps to reduce cycles:

1. Draw the current import graph and identify the cycle's reason.
2. Move shared domain types to a lower-level module with no upward dependencies.
3. Introduce a protocol or callback at the dependency boundary.
4. Move wiring to a composition root (application startup or `main`).
5. Enforce the direction with `import-linter` contracts or architecture tests.
6. Avoid a catch-all `common.py` that becomes a new dependency hub.

When synchronous dependency chains create unwanted coupling, event-based decoupling can help—but it changes delivery, ordering, retry, duplication, and consistency semantics. Define event schemas, idempotency, observability, and failure recovery before switching a direct call to an event. For monorepo/package moves, preserve import paths with compatibility shims where needed and update packaging, entry points, test discovery, build configuration, and ownership metadata together.

Split packages or extract services only after ownership, data boundaries, deployment needs, and failure modes justify it. Service extraction adds network failure, serialization, operations, and consistency concerns; it is not just moving files.

### 7.5 Codemods with LibCST

Use a codemod for repetitive, syntax-aware changes across many files. Text substitution with `sed` can corrupt comments, strings, formatting, or unrelated identifiers. LibCST preserves concrete syntax and formatting more reliably than operating on raw text.

Install and pin the optional tool in the project's development environment:

```bash
uv add --dev libcst
```

Example: rename a direct function call from `old_total(...)` to `calculate_total(...)` in Python call expressions. This deliberately does not rename function definitions, string references, imports, or attribute calls; extend the transformer and tests if those are required.

```python
import libcst as cst
from libcst import matchers as m

class RenameDirectCall(cst.CSTTransformer):
    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        if m.matches(updated_node.func, m.Name(value="old_total")):
            return updated_node.with_changes(func=cst.Name("calculate_total"))
        return updated_node

source = "result = old_total(items)\n"
module = cst.parse_module(source)
rewritten = module.visit(RenameDirectCall())
assert rewritten.code == "result = calculate_total(items)\n"
```

Before applying to a repository, test the codemod on fixture snippets covering imports, comments, aliases, nested calls, and negative cases. Run it in a clean worktree, inspect `git diff`, run tests and static checks, and keep the transformation idempotent where possible. A codemod does not understand the semantic intent of arbitrary dynamic Python calls; it should report or skip ambiguous cases instead of guessing.

Other tools: IDE rename, Rope, `ruff` rule fixes, `comby` for structured textual patterns, AST scripts for simple syntax changes, and repository-specific codemods. Use `sed` only for patterns whose boundaries are demonstrably safe; it is not a Python-aware refactoring engine. Pin versions and dry-run where supported. For long-lived feature branches, land refactorings early in small pull requests, rebase/merge frequently according to repository policy, and resolve conflicts while diffs are still narrow; avoid mixing unrelated branch integration work into the refactor commit.

## 8. Refactoring data engineering and ML systems

### 8.1 ETL, reporting, and data transformations

A refactor in a data pipeline can alter data semantics even if the function still returns a DataFrame. Capture the contract at meaningful boundaries:

- Row counts before and after each filter/join.
- Column names, order where relevant, dtypes, nullability, and schema evolution.
- Key uniqueness, duplicate behavior, sort order, and join cardinality.
- Checksums or stable hashes over canonicalized output; distributions and aggregates for large data.
- Idempotency, checkpoint boundaries, retry behavior, partition selection, and backfill semantics.
- Decimal precision, timezone conversions, null handling, and late-arriving data behavior.
- Resource profile: peak memory, partition size, query count, duration, and spill behavior.

Example: extract a pure transform from an I/O-heavy job while retaining I/O orchestration:

```python
from collections.abc import Iterable
from typing import TypedDict

class RawOrder(TypedDict):
    order_id: str
    amount_cents: int
    status: str

class AcceptedOrder(TypedDict):
    order_id: str
    amount_cents: int


def transform_orders(rows: Iterable[RawOrder]) -> list[AcceptedOrder]:
    """Preserve the legacy rule: accept only paid rows with positive cents."""
    return [
        {"order_id": row["order_id"], "amount_cents": row["amount_cents"]}
        for row in rows
        if row["status"] == "paid" and row["amount_cents"] > 0
    ]
```

This function is testable without a warehouse. But a new type annotation does not validate runtime input, and changing the filter rules would be a behavior change. Preserve the old behavior first; improve validation or business rules separately.

For a large pipeline, run old and new transforms on the same immutable input partitions. Compare schemas, counts, key sets, checksums, aggregates, and sampled row-level differences. Avoid comparing only total row count: two incorrect outputs can have the same count. Use deterministic sorting/canonicalization only when ordering is not part of the contract. If output ordering is meaningful, assert it rather than normalizing it away.

### 8.2 Pandas, notebooks, and feature logic

- Extract notebook cells into importable functions with explicit inputs and outputs; keep orchestration in the notebook.
- Separate data loading, transformation, feature calculation, training, evaluation, and serving.
- Use `.pipe()` or named transform functions when they improve traceability; a long method chain is not automatically clearer.
- Version schemas and feature definitions; preserve missing-value semantics and index alignment.
- Add tests for train/serve parity, categorical encoding, timezone and window boundaries, and leakage-sensitive splits.
- Make random seeds and model/data versions explicit where reproducibility is expected.

Moving logic between pandas and NumPy or changing eager operations to lazy frameworks can change dtype promotion, null semantics, ordering, overflow, and execution timing. Compare representative outputs and performance on realistic data volumes.

### 8.3 ML and AI training/serving paths

Refactor around stable stages: load/version data → validate → transform/features → train/infer → evaluate → publish. Use fixed small datasets and deterministic test doubles for model calls; use tolerance bands for floating-point predictions where exact equality is not meaningful. Track evaluation metrics and per-segment results, not only one aggregate score. Keep seeds, dependency versions, model artifacts, prompts, and evaluation sets versioned.

For LLM integrations, separate deterministic orchestration logic from the remote model call. Test prompt construction, tool routing, parsing, retry policy, safety filters, and error handling using recorded/fake responses. Keep a smaller live evaluation suite for model behavior; do not claim that a recorded response proves current model quality. Provider responses can vary even at low temperature, so avoid brittle byte-for-byte assertions unless the provider contract guarantees determinism.

### 8.4 Performance-aware refactoring

Measure before optimizing. Use representative inputs, repeat runs, warm-up where relevant, and report median plus spread rather than a single wall-clock number. For example:

```bash
uv run python -m cProfile -s cumulative -m my_package.job
uv run python -m timeit -s 'from my_package import transform; data = list(range(10000))' 'transform(data)'
```

`timeit` is useful for isolated microbenchmarks but does not model a complete ETL workload. For memory, use representative process-level measurements or `tracemalloc` for Python allocations; it does not account for every native allocation. Benchmark realistic row counts, skew, and I/O when that is what production cares about.

A refactor can reduce complexity but increase allocation or latency. Set acceptance thresholds before the change, compare equivalent workloads, and investigate statistically meaningful regressions. Do not optimize based on aesthetics or synthetic data alone.

## 9. Behaviour-changing traps: inspect the semantics, not just the syntax

| Trap | Why a “structural” edit can change behaviour | Protection |
|---|---|---|
| Floating-point order | `(a + b) + c` can differ from `a + (b + c)` due to rounding | Tolerance-based numeric tests plus domain error bounds |
| Evaluation order | Extracting/inlining can call properties/functions in a different order or number of times | Test call counts, side effects, and exceptions where relevant |
| Laziness | List → generator delays work and errors until iteration; may consume input once | Test timing, repeated iteration, and exception behavior |
| Exceptions | New helper or guard clause can raise earlier or change exception type/message | Test failure paths and exception contract |
| Logging/metrics | Moving a call can duplicate, omit, or reorder telemetry | Assert important event counts/order or inspect integration behavior |
| I/O timing | Opening a file or committing a transaction earlier/later changes visible state | Test resource lifetime, transaction boundary, partial failures |
| Mutable defaults | Replacing a shared default with a fresh object fixes a bug but changes behavior | Treat as explicit bug fix unless legacy sharing was accidental and change is approved |
| Equality / identity | Dataclass-generated equality compares fields; `is` checks identity | Test equality, hashing, membership, and cache keys |
| Iteration order | Sorting or using a set can change output order; dict insertion order may be relied on | Assert ordering where contractual; normalize only when order is irrelevant |
| Truthiness | `if value` merges `0`, `False`, `""`, `[]`, and `None` into one branch | Test each meaningful input separately |
| Resource use | Comprehension/list materialization uses memory; generator streams but can repeat side effects later | Benchmark memory and test consumption semantics |
| Concurrency | Moving shared state to a module global or singleton can introduce races | Concurrency tests and explicit ownership/lifetime |
| Imports | Moving code can create import cycles or change import-time side effects | Test clean imports and startup in a subprocess |

Example: a generator is not a drop-in replacement for a list:

```python
# Eager: errors happen during this call; result can be iterated repeatedly.
def values_eager(rows):
    return [parse(row) for row in rows]

# Lazy: parse runs only when consumed; result is usually one-shot.
def values_lazy(rows):
    return (parse(row) for row in rows)
```

The outputs may contain the same values when fully consumed, but timing, exceptions, resource use, and repeatability differ. This is a behaviour change unless the contract explicitly allows it.

## 10. Measuring refactoring outcomes

Choose measures that correspond to the problem; no single metric proves maintainability.

| Measure | Example tool / method | Interpretation caveat |
|---|---|---|
| Cyclomatic complexity | `radon cc -s -a src` | High complexity flags review targets; low complexity does not prove clarity |
| Function length / nesting | IDE, lint rules, custom report | A short function can still be opaque or over-abstracted |
| Duplication | `pylint --enable=duplicate-code`, review | Similar code can encode distinct business rules; avoid false consolidation |
| Coupling / import cycles | `pydeps`, `import-linter` | Graphs reveal dependencies, not whether they are conceptually wrong |
| Test duration / flake rate | CI history, rerun tracking | Faster tests are useful only if they still check meaningful behavior |
| Changed-line coverage | `coverage.py` plus `diff-cover` | Coverage says lines ran, not that assertions would detect a defect |
| Mutation score | `mutmut` or `cosmic-ray` | Surviving mutants may be equivalent or outside the contract; inspect them |
| Runtime / memory | repeatable benchmark, profiler | Compare equivalent workloads and environment; account for noise |
| Change-failure rate / incidents | deployment and incident data | Many factors affect the metric; do not attribute all change to one refactor |
| Reviewability | changed-line count, logical themes, reviewer feedback | A numeric line limit is a heuristic, not a substitute for coherent scope |

Baseline before and after with the same tools, versions, configuration, and source scope. Report absolute values and context. Do not claim that reducing a complexity score automatically improved reliability.

## 11. Working with Git, IDEs, and review

Useful commands:

```bash
git status --short
git diff --check
git diff --word-diff
git diff --color-moved
uv run ruff check src tests
uv run pytest -q
uv run coverage run -m pytest
uv run coverage report --skip-covered
uv run radon cc -s -a src
uv run vulture src --min-confidence 80
```

Tool commands depend on installed packages and project configuration. Add `coverage`, `radon`, and `vulture` to development dependencies before using them if they are not already installed. Run them on the same scope before and after. `vulture` can flag dynamic uses as unused; manually verify findings.

IDE refactoring commands (rename, extract method, move symbol) use language-aware references and are generally safer than manual edits. They still cannot reliably discover every dynamic import, reflection, plugin name, database procedure, or external caller. Use repository search and tests after the IDE operation.

### Pull request structure

- State: **“Intent: structural refactor; no externally observable behavior change intended.”**
- Describe the contract and areas affected.
- List the tests, type checks, lint, and benchmarks run; report any that were not run.
- Include before/after metrics if they support the reason for the change.
- Call out compatibility wrappers, feature flags, migrations, and rollback steps.
- List suspected bugs deliberately left unchanged and link their separate issues.
- Keep one refactoring theme per PR where feasible; split large changes into reviewable stacks.

Pairing or mob refactoring is useful when a transformation is difficult to reason about: one engineer drives the edit while others continuously check invariants, edge cases, and diff shape; rotate roles and keep the test/commit loop short. Reviewers should first understand the intended behavior and tests, then inspect the mechanical change and any new abstractions.

## 12. Worked example: test-protected refactoring of a legacy discount function

This example demonstrates the workflow. It is intentionally small enough to execute. The legacy rules are treated as the contract for this exercise—even if a domain owner later decides some are bugs.

### Step A: legacy implementation

```python
def calculate_discount(amount, customer_type, coupon=None):
    if amount < 0:
        return 0
    if customer_type == "gold":
        discount = amount * 0.10
    elif customer_type == "silver":
        discount = amount * 0.05
    else:
        discount = 0
    if coupon == "SAVE5":
        discount = discount + amount * 0.05
    if discount > amount:
        discount = amount
    return round(discount, 2)
```

### Step B: characterize first

```python
import pytest

@pytest.mark.parametrize(
    ("amount", "customer_type", "coupon", "expected"),
    [
        (100, "gold", None, 10.0),
        (100, "silver", None, 5.0),
        (100, "unknown", None, 0),
        (100, "gold", "SAVE5", 15.0),
        (-10, "gold", "SAVE5", 0),
        (0, "gold", "SAVE5", 0),
        (100, "gold", "other", 10.0),
    ],
)
def test_legacy_discount_examples(amount, customer_type, coupon, expected):
    assert calculate_discount(amount, customer_type, coupon) == expected
```

In a real `test_pricing.py`, import `calculate_discount` from the module under test. These tests pin down selected examples. They do not prove all possible inputs, monetary correctness, or that unknown customer types should earn no discount. Record such domain questions separately.

### Step C: extract named units without changing rules

```python
def _base_discount(amount, customer_type):
    rates = {"gold": 0.10, "silver": 0.05}
    return amount * rates.get(customer_type, 0)


def _coupon_discount(amount, coupon):
    return amount * 0.05 if coupon == "SAVE5" else 0


def calculate_discount(amount, customer_type, coupon=None):
    if amount < 0:
        return 0
    discount = _base_discount(amount, customer_type)
    discount += _coupon_discount(amount, coupon)
    if discount > amount:
        discount = amount
    return round(discount, 2)
```

This refactor preserves the example's rules for ordinary numeric amounts and string types. Before production adoption, expand tests for decimals, booleans, numeric types, unknown types, extreme values, and rounding boundaries. Note that `True` behaves like integer `1`; if booleans can reach the function, test and document that behavior.

### Step D: dispatch table and parameter object

Only after the small extraction is green, introduce a parameter object internally if callers benefit from it:

```python
from dataclasses import dataclass

_BASE_DISCOUNT_HANDLERS = {
    "gold": lambda amount: amount * 0.10,
    "silver": lambda amount: amount * 0.05,
}

@dataclass(frozen=True)
class DiscountRequest:
    amount: float
    customer_type: str
    coupon: str | None = None

def calculate_discount_for(request: DiscountRequest) -> float:
    amount = request.amount
    if amount < 0:
        return 0

    handler = _BASE_DISCOUNT_HANDLERS.get(request.customer_type)
    discount = 0 if handler is None else handler(amount)
    if request.coupon == "SAVE5":
        discount += amount * 0.05
    if discount > amount:
        discount = amount
    return round(discount, 2)

def calculate_discount(amount, customer_type, coupon=None):
    """Compatibility wrapper retaining the original call shape."""
    return calculate_discount_for(
        DiscountRequest(amount, customer_type, coupon)
    )
```

This is the integrated replacement: the handler table and parameter object are used by the new implementation, while the old public call shape remains available through a wrapper. The characterization cases from Step B must pass unchanged before adopting it. Unknown customer-type strings still receive zero base discount, and negative amounts still return integer `0`. This table assumes the documented `customer_type: str` contract; if arbitrary unhashable objects historically reach the function, dictionary lookup can change their exception behavior, so characterize and preserve that case if it is part of the real contract. The adapter preserves ordinary positional and keyword calls to the old function, but it may change signature introspection and traceback frames; test those if callers rely on them. In financial production systems, prefer `Decimal` or integer minor units where appropriate, but switching numeric representations is a separate semantic change and must be planned and tested explicitly.

## 13. Exercises with solutions

### Exercise 1 — Extract Function without moving side effects

Given:

```python
def process(path, sink):
    with open(path, encoding="utf-8") as stream:
        rows = [line.rstrip("\n") for line in stream]
    valid = [row for row in rows if row]
    sink.write(valid)
    return len(valid)
```

Refactor the pure row filtering into a helper. Preserve when the file is opened, when it is closed, the order of rows, and the one `sink.write()` call.

**Solution:**

```python
def nonempty_rows(rows):
    return [row for row in rows if row]


def process(path, sink):
    with open(path, encoding="utf-8") as stream:
        rows = [line.rstrip("\n") for line in stream]
    valid = nonempty_rows(rows)
    sink.write(valid)
    return len(valid)
```

The transformation is safe for this filtering rule because it preserves order and does not introduce new side effects. Test empty files, blank lines, trailing whitespace, and sink failures. Note that `rstrip("\n")` removes newline characters only; replacing it with `strip()` would change behavior by removing spaces and tabs.

### Exercise 2 — Replace `if/elif` with dispatch table

**Task:** convert a `format_value(kind, value)` chain for `upper`, `lower`, and `strip`, preserving the unknown-kind error.

**Solution:** use a mapping from supported string keys to callables, look up the key, and raise the same documented exception for missing keys. Test every key and an unknown key. Avoid silently defaulting unknown keys to `str` or returning the original value.

### Exercise 3 — Parameter object migration

**Task:** a public `load_data(path, start, end, region=None)` is used across several packages. Introduce `LoadOptions` without breaking existing callers.

**Solution outline:** add `LoadOptions` and a new canonical function; keep `load_data` as a wrapper; migrate internal callers; test old positional and keyword calls; document deprecation; remove only at a planned breaking release. Do not change date validation during this migration unless separately specified.

### Exercise 4 — Is a list-to-generator change a refactor?

**Expected answer:** not necessarily. It can alter evaluation timing, exception timing, one-shot consumption, memory usage, and side effects. It is behavior-preserving only if the interface permits laziness and consumers do not rely on eager evaluation or repeated iteration. Add tests for consumption and errors before making the change.

### Exercise 5 — Review this “cleanup”

```python
# Old
if amount is None:
    return 0
return amount

# New
return amount or 0
```

**Solution:** not equivalent. The new code also maps `0`, `False`, empty strings, and other falsey values to `0`. Keep the explicit `None` check unless broad truthiness normalization is the intended, tested behavior change.

## 14. Common mistakes and troubleshooting

- **Big-bang rewrite:** split by responsibility and use incremental migrations; maintain a working path and rollback option.
- **Refactor plus feature in one commit:** separate them so intent is reviewable and regression localization is possible.
- **No tests:** first add characterization tests and record baseline behavior; if coverage cannot be added safely, introduce a seam or wrapper before broad changes.
- **Tests mirror implementation:** assert outputs, errors, side effects, and invariants rather than private line-by-line call sequences.
- **Over-abstraction:** do not turn every helper into a class or every conditional into polymorphism. Choose the smallest abstraction that clarifies a stable concept.
- **Premature dead-code deletion:** search dynamic references, configuration, plugin registration, and external imports; remove behind a measured migration plan.
- **False confidence from types:** static checking catches type inconsistencies, not semantic equivalence, SQL behavior, or runtime reflection.
- **False confidence from coverage:** line coverage does not show that assertions detect wrong results; mutation testing can reveal weak assertions.
- **Dispatch table with different error behavior:** explicitly preserve unknown-key exceptions and supported-key semantics.
- **Unsafe codemod:** test fixture inputs, run in a clean worktree, review all changes, and verify idempotence or document why it is not idempotent.
- **Performance regression:** benchmark representative workloads and compare the same environment; do not assume shorter code is faster.
- **Data output mismatch hidden by normalization:** normalize only fields that are truly volatile and irrelevant to the contract; never sort away a meaningful ordering defect.
- **Uncontrolled feature flags:** give each flag an owner, default, telemetry, expiry, and removal issue.
- **No rollback plan:** preserve the old implementation or compatibility adapter until migration evidence is sufficient.

Troubleshooting sequence when tests fail after a refactor:

1. Stop and identify the first failing test; do not immediately update the expected output.
2. Re-run it against the pre-refactor commit or compare the characterized baseline.
3. Inspect evaluation order, data types, exception paths, default values, mutation, and side-effect timing.
4. Minimize the failing input and add a focused regression/characterization test.
5. Fix the structural mistake or explicitly reclassify the change as a behavior change with approval.
6. Re-run focused tests, the full suite, types, lint, and relevant integration/performance checks.

## 15. Capstone: refactor a characterized 200-line legacy function

**Prerequisite:** complete Lesson 02, *Characterization Tests for Legacy Code*. Select a real or intentionally messy function of approximately 200 lines in the practice repository. Do not choose a function whose external dependencies or behavior you cannot observe at all; create seams first if necessary.

### Deliverables

1. A baseline note describing inputs, outputs, side effects, dependencies, and known behavior.
2. Characterization tests covering representative normal, boundary, malformed, and error-path inputs.
3. A golden master or snapshot for **20 sample inputs**, with volatile fields normalized only when they are not part of the contract.
4. A refactored implementation using:
   - Well-named units with one cohesive responsibility each.
   - A parameter object where a group of values represents one concept.
   - Guard clauses to reduce accidental nesting while preserving return/error behavior.
   - A dispatch table for a stable mapping of operation/type to handler.
5. **At least 15 small commits**, each passing the appropriate test suite and each focused on one understandable transformation.
6. A final PR description with intent, tests, type/lint results, before/after metrics, compatibility notes, rollback approach, and every suspected bug intentionally left unchanged.
7. A separate list or issue references for at least **three discovered bugs**. Do not silently fix them inside the refactoring sequence. If a bug must be fixed immediately for safety, create a separately identified change with its own regression test.

### Suggested 15-commit sequence

| Commit | Transformation | Evidence before moving on |
|---:|---|---|
| 1 | Add baseline characterization cases | Tests pass on original implementation |
| 2 | Add boundary and error-path cases | Baseline behavior recorded |
| 3 | Add 20-input golden master | Snapshot reviewed and volatile fields justified |
| 4 | Rename local variables | Tests, lint, and diff clean |
| 5 | Extract first pure helper | Focused helper and integration tests pass |
| 6 | Extract second cohesive helper | No change in side-effect order |
| 7 | Replace magic literals with named constants | Values and serialized output unchanged |
| 8 | Introduce parameter object internally | Adapter tests preserve old caller shape |
| 9 | Add compatibility wrapper if signature changes | Old positional/keyword calls still work |
| 10 | Convert nested checks to guard clauses | Early-return behavior verified |
| 11 | Extract a dispatch table | Every key and unknown-key path tested |
| 12 | Move responsibility to its owning module/class | Import and public API tests pass |
| 13 | Inject one hard-wired dependency behind a seam | Fake and integration tests pass |
| 14 | Remove verified dead code / consolidate duplication | Dynamic references checked; full suite passes |
| 15 | Final cleanup and measurement-only commit | Full checks and before/after report attached |

This is a suggested order, not a command to force all changes into every project. If a listed transformation does not fit, replace it with another justified, small structural change and document why. The requirement is at least 15 genuine, reviewable commits—not 15 artificial whitespace edits.

### Acceptance criteria

- All baseline characterization tests pass after each structural commit.
- Golden master covers 20 distinct, documented inputs and is reviewed rather than blindly generated.
- The original public API remains compatible until a separately planned contract change.
- No intentional bug fix is hidden in a refactor commit.
- New helpers and the parameter object reduce complexity or clarify ownership; they are not abstractions without a use case.
- The dispatch table preserves supported cases and failure behavior.
- At least three suspected bugs are recorded separately with reproduction evidence or clear uncertainty notes.
- Final PR documents tests, checks not run, metrics, risks, and rollback.

## 16. Self-assessment

Answer these without looking back, then verify your answers.

1. State the definition of refactoring and list five rules for safe refactoring.
2. Why should feature work and bug fixes be separate from a behavior-preserving refactor?
3. When is Extract Function unsafe even if the extracted code looks identical?
4. Explain expand–migrate–contract for a public function signature.
5. When is a parameter object appropriate, and how can it change behavior?
6. Compare dispatch tables, `match`, and polymorphism. Give one case where each is preferable.
7. Why can replacing a list with a generator alter observable behavior?
8. What can line coverage prove, and what can mutation testing add?
9. Outline a safe schema expand–contract migration.
10. How would you test parity between an old and new ETL transform?
11. Which behaviors can dataclass generation alter?
12. What should a safe LibCST codemod test before running across a repository?
13. Which metrics would you report before and after refactoring, and what are their limitations?
14. How do branch by abstraction and the strangler-fig pattern reduce migration risk?
15. What must the capstone PR say about known bugs and rollback?

### Answer key

1. Internal structure changes while externally observable behavior is preserved; small steps, tests green, frequent commits, separation from feature/bug changes, and no behavior change within a pure refactor.
2. Separate changes make intent reviewable and regression localization possible; behavior changes require explicit requirements and regression tests.
3. Scope, evaluation order/count, exception timing, mutable state, resource lifetime, or side effects may change.
4. Add the new API while preserving the old; migrate callers; observe/deprecate; remove only at a planned breaking boundary.
5. It groups cohesive parameters; it may change signatures, validation, defaults, equality, mutability, serialization, and callers.
6. Dispatch table for key-to-callable mapping; `match` for structured patterns; polymorphism for stable type-specific behavior under a common contract.
7. Work and exceptions become lazy, input may be consumed once, and repeated iteration/resource timing changes.
8. Coverage proves code executed; mutation testing checks whether tests detect selected behavioral changes, with equivalent-mutant caveats.
9. Add new schema, dual-read/write or backfill, migrate readers, verify parity, then remove old fields after consumers and rollback needs are clear.
10. Run both on the same immutable input, compare schema, counts, keys, checksums/aggregates, and row-level samples; normalize only non-contractual fields.
11. `__init__`, `__repr__`, equality, ordering if requested, hashing, and mutability/slots options.
12. Positive and negative fixtures, imports/aliases, comments and strings, nested calls, idempotence, diff scope, and test/type/lint results.
13. Complexity, duplication, coupling, test time/flake rate, changed-line coverage/mutation score, runtime/memory; each is a proxy and must be interpreted in context.
14. Both introduce a stable boundary and gradually route behavior to a replacement while retaining fallback and monitoring parity.
15. State tests and checks, compatibility, metrics, rollout/rollback, and suspected bugs intentionally left unchanged with separate tracking.

## 17. Quick reference: before committing

- [ ] Is the intent structural and behavior-preserving, or is a behavior change explicitly documented?
- [ ] Do tests capture the affected public contract and important edge/error paths?
- [ ] Did I change evaluation order, exceptions, mutation, ordering, I/O timing, imports, or resource lifetime?
- [ ] Did I preserve public positional/keyword calls and serialized/API formats?
- [ ] Is each change small enough to review and roll back independently?
- [ ] Did focused tests, full tests, configured type checking, linting, and `git diff --check` run?
- [ ] Did I inspect the diff for unrelated formatting or generated changes?
- [ ] If performance-sensitive, did I compare equivalent representative workloads?
- [ ] Are feature flags, compatibility wrappers, and migration steps documented with removal criteria?
- [ ] Are known bugs recorded separately instead of being silently fixed?

## References and tool documentation

Use the versions pinned by your project and consult official documentation for exact options:

- Martin Fowler, *Refactoring: Improving the Design of Existing Code* — catalogue and mechanics.
- Python documentation: `dataclasses`, `enum`, `functools`, `contextlib`, `typing`, `match` statements, and command-line execution.
- pytest documentation — fixtures, parametrization, markers, and test selection.
- LibCST documentation — metadata-aware, formatting-preserving Python codemods.
- `ruff`, `mypy`/`pyright`, `coverage.py`, `radon`, `vulture`, `import-linter`, and `mutmut` documentation.
- The module's Lesson 01, *Reading Unfamiliar Codebases*, and Lesson 02, *Characterization Tests for Legacy Code*, for repository investigation and baseline behavior capture.

**Final principle:** refactoring is a controlled engineering activity, not a license to change what the system does. Use tests and evidence to support the claim of behavior preservation; state uncertainty honestly; make intentional behavior changes explicit; and keep every step understandable and reversible.
