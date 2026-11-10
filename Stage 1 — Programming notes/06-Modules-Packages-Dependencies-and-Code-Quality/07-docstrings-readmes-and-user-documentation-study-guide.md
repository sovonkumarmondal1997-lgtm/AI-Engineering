# Module 1.6 — Lesson 07: Docstrings, READMEs, and User Documentation
## Complete Chapter Summary, Roadmap Assessment, Exercises, Debugging, and Project Guide

> Source: `07-docstrings-readmes-and-user-documentation.md` (4,461 lines; 25,396 words). This guide follows the uploaded lesson and your established Stage 1 / Module 1.6 sequence.

# Part A — Complete Chapter Summary

## 1. Why documentation exists

Documentation is written information explaining what software does, how to use it, why it was designed in a particular way, and how to operate or recover it. Code describes *mechanism*—the statements Python executes. It often does not explain intent, assumptions, guarantees, business rules, failure behavior, or operational procedures.

```python
def charge_customer(customer_id: str, amount_cents: int) -> str:
    if amount_cents <= 0:
        raise ValueError("amount_cents must be positive")
    payment = payment_gateway.create_charge(customer_id, amount_cents)
    return payment.id
```

The implementation shows validation, a gateway call, and a returned ID. It does not tell a caller whether retrying can charge twice, which currency is used, how long the call can block, or what happens if the gateway times out after accepting a charge. A useful docstring records those non-obvious contracts.

Different readers need different documentation:
- **Users:** installation and usage.
- **Developers/integrators:** function contracts, inputs, outputs, and errors.
- **Maintainers/architects:** system structure and reasons for design decisions.
- **Reviewers:** whether changes preserve public contracts.
- **Operators/on-call engineers:** deployment, monitoring, incident response, and recovery.
- **Data engineers:** pipeline schemas, transformations, quality rules, and failure handling.
- **ML engineers:** model inputs, preprocessing, outputs, evaluation, versions, and limitations.
- **AI/agent engineers:** model configuration, tool permissions, failure/retry behavior, and safety boundaries.
- **DevOps engineers:** deployment, configuration, health checks, and rollback.

## 2. Documentation categories

| Category | What it answers | Typical artifact |
|---|---|---|
| Code | What does this function/class/module promise? | Docstring |
| API | What is the stable interface contract? | API reference |
| User | How do I install and use it? | README / user guide |
| Developer | How do I set up and contribute? | `CONTRIBUTING.md` |
| Project | What is the project and its history? | README / changelog |
| Operational | How do I deploy, monitor, and recover it? | Runbook |
| Architecture | How is it structured, and why? | Architecture overview / ADR |

A README may contain a short user guide and developer setup, but it should not become an unstructured encyclopedia. Link to deeper documents when necessary.

## 3. Docstrings: definition, placement, runtime behavior

A **docstring** is a string literal that is the first statement in a module, class, function, or method. Python stores it in the object's `__doc__` attribute.

```python
def calculate_total(price: float, quantity: int) -> float:
    """Calculate the total price."""
    return price * quantity

print(calculate_total.__doc__)
help(calculate_total)
```

The first-statement rule matters. A string after an assignment is not a docstring:

```python
def bad_example():
    value = 1
    """Not a docstring: it is not the first statement."""
    return value

print(bad_example.__doc__)  # None
```

Module docstrings go at the top of the `.py` file, before imports. Class and function docstrings go immediately inside their definitions. `help()` reads the docstring and signature. IDE tooltips and documentation generators use the same metadata. Running Python with `-OO` strips docstrings, so code must not depend on them for application behavior.

Triple-quoted strings (`"""..."""` or three single quotes) are ordinary Python string syntax; they are not inherently docstrings. Triple double-quotes are the conventional docstring form, following PEP 257.

## 4. Comments versus docstrings

| Comment | Docstring |
|---|---|
| Begins with `#` | String literal in first-statement position |
| Explains a particular line/block, usually *why* | Explains a callable/type/module contract: *what*, meaning, constraints, usage |
| Not stored as runtime object metadata | Stored in `__doc__` |
| Not shown by `help()` | Shown by `help()` and documentation tools |

```python
def calculate_discount(price: float, is_member: bool) -> float:
    """Calculate a customer's discounted price.

    Members receive an additional 5% discount on the supplied price.
    """
    # Multiplicative discount is required by the pricing policy.
    if is_member:
        price *= 0.95
    return price
```

The docstring helps callers. The comment helps a maintainer understand why a specific implementation choice must not be casually changed. Avoid comments that merely narrate the next statement (`# increment x` above `x += 1`).

## 5. Function docstrings: document the contract

A function docstring gives a caller the information needed to use the function without reading its implementation. Common sections:
- **Summary:** one concise, imperative statement; always include one.
- **Description:** extra context for important behavior or business rules.
- **Args/Parameters:** meaning and constraints of parameters.
- **Returns:** what the result represents, not merely its Python type.
- **Raises:** documented exceptions callers may need to handle.
- **Examples:** short, runnable examples when usage is not obvious.
- **Side effects:** file writes, network calls, mutation, logging, metrics.
- **Notes/Warnings:** performance, thread safety, caching, deprecation, idempotency.

```python
def divide(a: float, b: float) -> float:
    """Divide a by b.

    Raises:
        ZeroDivisionError: If b is zero.
    """
    return a / b
```

A payment function should state whether it is idempotent, what ID `customer_id` represents, which currency `amount_cents` uses, what it returns, and what happens on a gateway timeout. A timeout may leave the charge's outcome ambiguous; a caller must not blindly retry a non-idempotent operation.

Do not force every section into every docstring. A simple `get_user_count()` may need only `"""Return the number of registered users."""`. Document what is useful and non-obvious.

## 6. Three major docstring styles

Pick one style per project and apply it consistently.

**Google style** uses plain section names and compact prose:

```python
def calculate_total(price: float, quantity: int) -> float:
    """Calculate the total price.

    Args:
        price: Unit price.
        quantity: Number of items.

    Returns:
        The total price.

    Raises:
        ValueError: If quantity is negative.
    """
    if quantity < 0:
        raise ValueError("quantity must be non-negative")
    return price * quantity
```

**NumPy style** uses underlined headings and lists types separately:

```python
def calculate_total(price: float, quantity: int) -> float:
    """Calculate the total price.

    Parameters
    ----------
    price : float
        Unit price.
    quantity : int
        Number of items.

    Returns
    -------
    float
        The total price.
    """
    return price * quantity
```

NumPy style is common in scientific computing, data science, and ML libraries such as NumPy, SciPy, pandas, and scikit-learn. Its layout helps document many parameters, units, array shapes, and dtypes.

**Sphinx/reStructuredText style** uses field markers:

```python
def calculate_total(price: float, quantity: int) -> float:
    """Calculate the total price.

    :param price: Unit price.
    :param quantity: Number of items.
    :return: The total price.
    :raises ValueError: If quantity is negative.
    """
    return price * quantity
```

It fits Sphinx-first and older projects. Google is a practical default for general application/backend work. Consistency matters more than declaring one style universally best.

## 7. Docstring best practices and type hints

Use concise imperative summaries (`"""Calculate..."""`, `"""Return..."""`). Parameter descriptions should add meaning or constraints, not repeat names. Document non-obvious ordering, idempotency, mutation, caching, side effects, thread safety, and contract exceptions. Do not list every theoretical Python exception.

Type hints and docstrings are complementary:
- `user_id: int` and `-> User` describe **data shape** and can be checked by mypy/Pyright.
- Prose explains **meaning and behavior**: whether the ID is caller-supplied, whether email must already be validated, whether duplicates raise an exception, or whether the call has side effects.

Avoid repeating `name (str): a string` when the signature already says `name: str`. Instead explain what the name means and its domain constraints. Google style in typed codebases usually omits redundant type parentheticals. NumPy style commonly repeats types by its structure.

## 8. Class, attribute, method, module, and package documentation

A **class docstring** explains what the class represents, its invariants, state, lifecycle, side effects, thread-safety, and usage assumptions. A `BankAccount` docstring should describe whether negative balances are possible and whether concurrent withdrawals are safe.

Document instance attributes in the class docstring's `Attributes:` section. `ClassVar` fields are shared class-level state, not per-instance state; an inline comment can explain why sharing is intentional. Dataclass field types/defaults help, but prose should explain domain meaning such as whether `max_attempts=1` means no retry.

**Method docstrings:** public methods normally document their contract. Private helpers need docstrings only when behavior is non-obvious. Properties should be documented as values/attributes. Special methods need explanation when behavior differs from the obvious default.

**Module docstrings** are first in the file, before imports. They explain the file's purpose, scope, public names, and important assumptions. Example: a transaction module may state it contains pure normalization functions and performs no I/O.

**Package documentation** explains the library as a whole: purpose, public modules/classes/functions, getting-started example, installation, and dependencies. `__init__.py` can contain the package docstring and re-export a deliberate public surface.

`__all__` names what `from package import *` imports and signals the intended public API; it does not enforce access control. A public API is a supported contract external callers can rely on. Underscore-prefixed modules/names are conventionally internal and may change without compatibility guarantees. Document public APIs carefully; document internal details only when useful.

## 9. API contracts

A public API contract should state valid input and preconditions; return value and meaning; documented errors; side effects and external calls; idempotency, ordering, concurrency, and performance guarantees when relevant; compatibility/deprecation expectations; and security/privacy constraints. Docstrings, annotations, README/API reference, and tests each contribute different evidence. A type hint cannot express every business guarantee.

## 10. README: the first useful entry point

A README answers: what is this project, why would I use it, and how do I get a working result? It should let a new reader move from clone to successful run/test without asking a basic question.

A useful structure:
1. Project name and one-sentence description.
2. Purpose and main features.
3. Prerequisites (Python version, tools, external services).
4. Installation with exact copy-pasteable commands.
5. Configuration table.
6. Usage examples showing actual commands and output.
7. Testing and quality-check commands.
8. Project structure when it helps orientation.
9. Troubleshooting.
10. Development/contribution link and license.

Avoid vague statements like “install dependencies and run the app.” Show actual commands, e.g. `uv sync` and `uv run python -m billing_service`, with realistic output. Keep README concise and link to architecture, API reference, runbooks, and contribution guides.

## 11. README installation, configuration, and usage

**Installation:** list prerequisites and exact commands, including cloning, changing directory, installing dependencies, and external service setup. State supported Python version. Do not assume Python packages install system dependencies or start databases.

**Configuration:** document every required/optional value, type/format, default, purpose, allowed values, and secret status.

| Variable | Required | Type | Default | Meaning |
|---|---|---|---|---|
| `DATABASE_URL` | Yes | string | — | Database connection string |
| `API_KEY` | Yes | secret | — | Provider credential |
| `API_TIMEOUT_SECONDS` | No | integer | `30` | Request timeout |
| `LOG_LEVEL` | No | string | `INFO` | Logging threshold |
| `FEATURE_FLAG_TAX_V2` | No | Boolean | `false` | Enables new tax engine |

Never put real credentials in docs. Use `.env.example` with placeholders and instruct users to copy it to an ignored `.env`.

**Usage:** give realistic CLI and Python examples with expected output. Ensure names, arguments, defaults, and output match the current implementation. Examples are part of the public contract and can become stale.

## 12. CLI and error documentation

CLI `--help` output is user documentation generated from `argparse` definitions. Document commands, subcommands, positional arguments, options, defaults, choices, required/optional status, examples, stdout/stderr behavior where relevant, and exit codes.

| Exit code | Meaning |
|---|---|
| `0` | Success |
| `1` | Expected operational/input failure |
| `2` | CLI usage/argument error (often argparse default) |

Use the actual application's contract rather than blindly adopting illustrative values.

Document errors with: **symptom/error message → likely cause → diagnosis → solution → verification**. Prefer actionable fixes and exact commands. Avoid “check your config” without naming the setting and expected value.

## 13. Examples are executable documentation

Useful examples are correct for the current API/version, minimal but complete, copy-pasteable, explicit about prerequisites and expected output, safe, and tested where practical. Distinguish:
- **Minimal example:** smallest successful use.
- **Realistic example:** representative workflow.
- **Anti-pattern example:** clearly labeled incorrect and explained.

Do not omit critical setup or silently depend on undeclared state. Examples should not include stale imports, old command names, missing environment variables, or impossible output.

## 14. Accuracy, documentation drift, and Documentation as Code

Documentation accuracy means commands, options, function names, paths, defaults, and behavior match the implementation. Recheck examples after renames, refactors, dependency/config changes, and releases.

**Documentation drift** is the process of code and docs becoming inconsistent. Causes include code changes without doc updates, renamed functions, changed CLI flags, altered defaults, stale screenshots, and untested examples.

**Documentation debt** is the accumulated backlog of missing, stale, contradictory, or low-quality docs caused by drift and neglect. Drift is the process; debt is the backlog/impact.

**Documentation as Code** means keeping docs in the repository, editing them with code, using Git branches/PRs/reviews, and applying automated checks. Update docs in the same commit/PR as the behavior change. Review documentation as part of code review.

## 15. Git, code review, changelogs, release notes, deprecation

Docs belong in Git beside the code. Benefits include version history, review, rollback, traceability, and branch/version alignment. A public-contract change may require docstrings, README/API docs, tests/examples, changelog, and migration notes.

A **changelog** is a concise cumulative record organized by release/version (added, changed, fixed, removed). **Release notes** are a narrative announcement for a specific release, explaining impact, highlights, migration steps, and known issues.

Deprecation documentation identifies the deprecated name/behavior, replacement, warning/version timeline, removal target, migration example, and compatibility period. Breaking changes need clear before/after examples, affected versions, migration steps, and release notes. Do not silently remove a public API.

## 16. API documentation tools

API documentation is structured reference for public interfaces: signatures, parameters, returns, exceptions, and examples. Generate what can be mechanically derived; write human guides for intent and workflows.

- **`pydoc`:** Python standard-library tool/module. Displays documentation from `__doc__`, signatures, and module metadata; can be used from the terminal and generate simple HTML.
- **Sphinx:** mature Python documentation generator, reStructuredText support, extensions, cross-references, and strong API reference generation. More configurable, steeper learning curve. Napoleon parses Google/NumPy docstrings.
- **MkDocs:** Markdown-first static site generator with a gentler workflow; plugins can provide generated API reference.
- **Automatic API docs:** extract public signatures/docstrings into reference pages; generated docs still need review.
- Generate exhaustive lookup/reference material; hand-write tutorials, how-to guides, architecture rationale, and “why” explanations.

## 17. Documentation testing, doctest, executable examples

Documentation tests reduce drift:
- Run doctests in docstrings/docs.
- Execute README commands in a smoke-test environment where practical.
- Test examples against supported Python/dependency versions.
- Check links and Markdown structure.
- Validate configuration examples and CLI help.

`doctest` is in Python's standard library. It scans `>>>` interactive examples, executes them, and compares actual to expected output:

```python
def square(value: int) -> int:
    """Return the square.

    >>> square(4)
    16
    """
    return value * value
```

Doctests suit small deterministic examples. Avoid network/time/random/unstable examples unless controlled. Not every prose example should be a doctest.

## 18. Links, navigation, and Diátaxis

Use descriptive link text, valid relative paths, stable heading anchors, and cross-links between README, API reference, tutorials, architecture docs, and runbooks. Avoid “click here” and broken links. Organize docs so readers can find answers quickly.

Diátaxis separates:
- **Tutorial:** guided learning for a beginner's first result.
- **How-to guide:** task-oriented instructions for a reader with a goal.
- **Reference:** factual, exhaustive descriptions of API/configuration/options.
- **Explanation:** conceptual context and rationale (“why”).

A tutorial teaches; how-to helps complete a task; reference is looked up; explanation builds understanding.

**User docs** explain install/configure/use. **Developer docs** explain local setup, architecture, testing, coding standards, debugging, contribution, and release process. A README can link to both but should identify the audience.

## 19. CONTRIBUTING and developer documentation

`CONTRIBUTING.md` commonly documents prerequisites, environment setup, dependency installation, branch/commit conventions, coding standards, tests, linting, type checking, PR expectations, issue reporting, and review process.

Developer docs should include exact commands such as `uv sync --group dev`, `uv run pytest`, `uv run ruff check .`, and `uv run mypy .`, adapted to the real project. Include how to run one test and common setup/import errors. Keep instructions aligned with `pyproject.toml`, lock files, and CI.

Onboarding sequence:
prerequisites → clone → install → configure → run → test → lint/type-check → understand architecture → make a first small change/PR. If a contributor must ask a teammate at a step, docs likely have a gap.

## 20. Architecture docs and ADRs

Architecture docs explain components, boundaries, dependencies, data flow, failure behavior, deployment, and rationale. State whether calls are synchronous/asynchronous, internal/external, and what happens during outages.

An **Architecture Decision Record (ADR)** captures one significant decision:
1. **Context:** problem and constraints.
2. **Decision:** chosen approach.
3. **Alternatives Considered:** credible options and why rejected.
4. **Consequences:** benefits, trade-offs, follow-up work, limitations.

Example: default file encoding to UTF-8, with `WORDCOUNT_ENCODING` override. Explain why auto-detection was rejected (it can silently guess incorrectly), and document that legacy files need explicit configuration.

## 21. Data-pipeline documentation

A production pipeline document should capture purpose/owner/schedule/SLA; source systems, location, format, schema, partitioning, sample records; required fields/types/nullability/uniqueness/quality rules; transformations and business definitions; output tables/files/schema/partitioning/retention; incremental/full-load behavior, watermark/CDC semantics, idempotency; retries/backfills/late data/duplicates/bad records/quarantine; dependencies/configuration references; monitoring/metrics/alerts/logs/recovery/runbooks.

Example `daily_transaction_load`: read daily transactions, validate required fields, deduplicate by transaction ID, normalize currency/amount, write a partitioned warehouse table, and report rejected records. State how missing source data, schema changes, retries, and reruns behave. Pipeline documentation must support lineage and recovery.

## 22. ML-system documentation

ML failures can be silent: a system may return plausible but wrong predictions without crashing. Document:
- model name/version, owner, purpose, intended/non-intended use;
- training/inference data sources, schema, feature definitions, labels, data windows;
- exact preprocessing (normalization, encoding, missing-value handling, tokenization, feature order);
- model artifact/runtime/framework/dependency pins/hardware assumptions;
- input/output contracts, shapes, dtypes, ranges, errors;
- evaluation datasets, metrics, thresholds, baselines, limitations, bias/drift checks;
- deployment, monitoring, rollback, retraining, reproducibility.

Inference preprocessing must match training preprocessing. A model trained on normalized features can confidently mispredict if production sends raw values.

## 23. AI and agentic-system documentation

AI docs should capture provider/model/version, parameters, prompts/templates, context limits, retrieval sources, embedding/vector-index versions, safety constraints, evaluations, latency/cost expectations, fallback behavior, and privacy/data handling.

Agent docs additionally need per-tool purpose, schemas, permissions, side effects, allowed resources/allow-lists, timeout/retry/idempotency, failure behavior, human approval/escalation, audit logs, traces, and observability. Critical safety boundaries must be enforced in code/tool authorization, not only in prompts. Example: `send_email` must enforce recipient allow-lists even if the model requests another address. Document model nondeterminism and provider/prompt changes.

## 24. Configuration and dependency documentation

For every configuration setting document name, required/optional, type/format, default, allowed values/range, purpose, precedence/source, secret status, and safe example. Explain `.env.example`, ignored `.env`, deployment secret manager, and missing/invalid behavior. Distinguish missing from empty and strings from parsed integers/Booleans. Never show real credentials or log secrets.

Human docs state supported Python version, system dependencies (e.g. `ffmpeg`, database client libraries), and external services (database, queue, API). `pyproject.toml` and `uv.lock` are authoritative machine-readable sources for Python package declarations and resolved versions. README explains how humans get external services running.

## 25. Documentation tooling, linting, and coverage

Ruff's optional `D` docstring rules (derived from pydocstyle) can check presence and basic style; they cannot verify semantic correctness. Markdown linters detect malformed Markdown, headings, fences, tables, and inconsistent style. Link checkers detect broken links. Doctest verifies executable examples. Type checkers check code signatures and usage, not docstring prose.

Documentation coverage measures the proportion of public symbols with docstrings. It is a signal for missing docs, not a quality score: `"""Get id."""` may count while adding no information. Do not chase 100% mechanically.

## 26. What to document—and what not to document

Document public APIs, non-obvious behavior, assumptions, side effects, errors, configuration, operations, architecture decisions, and user workflows.

Avoid comments that repeat code; docstrings that repeat names/type hints without meaning; volatile implementation details (e.g. “uses a for loop”); empty sections; inaccurate claims/unverified commands; secrets, personal data, private production details, or exploit-sensitive information.

Every sentence creates maintenance cost. More documentation is not automatically better; useful, accurate, discoverable documentation is better.

## 27. Documentation debt, maintenance, versioning, breaking changes

Documentation debt accumulates when required updates are deferred. Maintain docs through same-PR updates, review ownership, periodic audits, release checks, executable examples, and post-incident improvements. Version docs in line with supported software versions. If multiple major versions are supported, keep matching doc versions; otherwise maintain one current set.

For breaking changes document affected API/CLI/config, old and new behavior, migration steps, deprecation window, compatibility implications, release notes, and examples. Never make users infer how to migrate.

## 28. Documentation security

Never include real API keys, passwords, tokens, private certificates, production database URLs, customer data, sensitive internal hostnames, or privileged operational details. Git history preserves committed secrets even after deletion; rotate exposed credentials and follow incident procedures. Use fake placeholders and safe `.env.example` files. Be careful with screenshots, logs, copied payloads, and generated docs.

## 29. Operational docs, runbooks, troubleshooting

Operational docs cover deployment, rollback, health checks, log locations/search, alerts, common incidents, and recovery.

A **runbook** is a specific procedural response for a known scenario under time pressure. Example for HTTP 500s: inspect recent logs; check database connectivity; check known causes (connection pool exhaustion/provider outage); apply remediation or wait for external recovery; escalate if unresolved within a stated time. Commands must match the real deployment type and be verified before operational use.

A broader troubleshooting entry uses:
**Problem → Symptoms → Likely Cause → Diagnosis → Solution → Verification → Prevention.**
A troubleshooting guide is a scannable collection of issues; a runbook is a focused incident procedure.

## 30. Documentation quality framework and good/bad examples

Review documentation against eight dimensions:
1. **Correctness:** matches current behavior.
2. **Completeness:** reader can do what is needed.
3. **Clarity:** understandable on first read.
4. **Consistency:** terminology and style align.
5. **Discoverability:** easy to find.
6. **Maintainability:** easy to update safely.
7. **Audience awareness:** right depth and language.
8. **Actionability:** gives concrete next steps.

Good docs replace vague claims with exact commands, real outputs, setting names, dependency/failure relationships, and verified examples. “Set your API key” is poor; “set required secret `API_KEY` in your ignored local `.env`, copied from `.env.example`; never commit it” is actionable.

## 31. Complete `invoicing` documentation mini-project

The chapter's `invoicing` package example demonstrates the full documentation stack for a realistic package with `generate_invoice(order, customer)`, a `Customer` dataclass, and a CLI.

Its README explains that the project generates PDF invoices; requires Python 3.12+ and `uv`; installs with `uv sync`; documents optional `INVOICE_OUTPUT_DIR` (default `./invoices`); shows `uv run python -m invoicing generate --order-id 501`; gives pytest, Ruff, and mypy commands; and explains that the CLI loads records while `invoicing.pdf.generate_invoice` builds PDF bytes without doing file I/O.

The function docstring explains that `generate_invoice(order: Order, customer: Customer) -> bytes` returns PDF bytes, requires at least one line item, raises `ValueError` for an empty order, and performs no file I/O. The `Customer` class docstring explains that the billing address is displayed on invoices but must be validated at intake. The `invoicing.pdf` module docstring states that it contains pure PDF-rendering logic and that `invoicing.cli` owns file writing.

The CLI contract documents the `generate` command, required integer `--order-id`, and exit codes: 0 success, 1 order not found, 2 customer not found. The developer setup uses `uv sync --group dev`; the project also documents changelog updates, Ruff/type-check/test commands, and a runbook for diagnosing a PDF-generation hang (distinguishing slow font loading from a genuine deadlock).

## 32. Complete examples from the chapter

**Complete README:** billing-service includes overview/features, Python/uv/PostgreSQL prerequisites, clone + `uv sync`, a config table (`DATABASE_URL`, secret `API_KEY`, `LOG_LEVEL`), a CLI balance command with output, pytest, Ruff and mypy commands, package tree, troubleshooting, contribution link, and license.

**Complete docstring module:** a pure pricing module documents module scope/no I/O; frozen `OrderItem` dataclass and fields; `calculate_total()` parameters, bulk-discount defaults, return, `ValueError`, and doctest examples; immutable `Order` class; `total()` and `add_item()` methods. It copies input items into a tuple and returns a new `Order` on `add_item`, so immutability claims are supported by implementation.

**Complete workflow:** write code → add type hints → write docstrings → update README → add tests/examples → run Ruff → run type checker → run tests/doctests → review docs → commit code/docs together → CI → update changelog/release docs. Stages may overlap, but none should be forgotten.

# Part B — Project-Tree and Current-Level Assessment

## Your roadmap position

Your known Stage 1 roadmap has 24 modules. It progresses from computational thinking and Python fundamentals through control flow, collections/algorithms, files/structured data/CLI, modules/packages/dependencies/code quality, testing/debugging, OOP/data modeling, and advanced production Python.

Four major Stage 1 projects:
1. **Personal Expense Ledger CLI**
2. **Log Investigation and Reliability CLI**
3. **Data Quality and Transformation Pipeline (`dqpipe`)** — CLI, config, pipeline, rules, tests, data contract.
4. **Rule-Based Risk Review Engine (`riskreview`)** — CLI, engine, I/O, models, rules, tests, golden decision data.

## Demonstrated foundation

You have completed Module 05 lessons on text files, pathlib, CSV, JSON, encodings/newlines, argparse, standard streams/exit codes, logging, environment configuration, and input validation. Module 1.6 Lessons 01–06 covered imports/`__main__`, project/package layout, `pyproject.toml`/lock files/`uv`, dependency management/SemVer, Ruff formatting/linting, and type hints/type checking.

That is a suitable prerequisite. You understand function signatures, exceptions, CLI commands, environment variables, packages, public/private names, annotations, `uv`, Ruff, and mypy. The new skill is explaining these engineering contracts clearly to users, developers, maintainers, and operators.

## Apply the lesson to your projects

- **Expense Ledger:** document currency units, rounding, input CSV schema, CLI examples, exit codes, and data-file safety.
- **Log Investigation CLI:** document log formats, timestamp/timezone assumptions, filtering options, severity meanings, output destinations, and troubleshooting.
- **`dqpipe`:** document source schema, required columns, validation rules, transformations, rejected-row behavior, idempotency, output schema, lineage, and backfill/recovery.
- **`riskreview`:** document rule precedence, decision meanings, thresholds, evidence requirements, false-positive limitations, audit trail, and safe configuration.
- **All four:** add meaningful public docstrings, a README that gets a user running, developer setup, architecture notes for non-obvious decisions, and runbooks for operational failures.

Your current level remains **beginner progressing toward intermediate** in Python engineering. You have enough technical foundation to write useful documentation now. Focus on contracts and accurate examples rather than long prose. Mastery means a new user can install/run a project, a caller can use APIs safely, a maintainer understands decisions, and an operator can recover failures.

# Part C — All 19 Exercises Solved

The exercises are documentation-design tasks. Solutions stay within the Python concepts already covered.

## Level 1 — Basic

### 1. Write a function docstring

```python
def square(n: int) -> int:
    """Return n squared."""
    return n * n
```

- `def square(...)` defines the typed input/output contract.
- The first statement is the docstring, stored in `square.__doc__`.
- `return n * n` returns the square.
- No `Args`/`Returns` sections are needed because the signature and summary are clear.

### 2. Identify comment versus docstring

```python
# validate input before processing

def process(value: str) -> str:
    """Validate input before processing."""
    return value.strip()
```

The `#` line is a comment and is not runtime metadata. The triple-quoted first statement is a docstring available through `process.__doc__`. They serve different purposes.

### 3. Document parameters

```python
def greet(name: str, formal: bool) -> str:
    """Build a greeting string.

    Args:
        name: Person to greet.
        formal: If True, use formal phrasing.
    """
    return f"Good day, {name}." if formal else f"Hi {name}!"
```

The summary states purpose. `name` explains whose name is inserted. `formal` explains the Boolean's effect. The conditional expression returns one of two greeting strings.

### 4. Document return values

Add to the previous docstring:

```text
Returns:
    The greeting string, formal or informal according to `formal`.
```

This explains the result's meaning rather than repeating `str`, already shown by `-> str`.

## Level 2 — Intermediate

### 5. Document a class

```python
class ShoppingCart:
    """A mutable collection of items a customer intends to purchase.

    Not thread-safe: concurrent add/remove calls on the same instance
    from multiple threads are not supported.
    """

    def __init__(self) -> None:
        self._items = []
```

The class docstring explains domain purpose, mutability, and concurrency assumptions. Retain the thread-safety statement only if it matches the actual implementation.

### 6. Document a module

Place this at the very top, before imports:

```python
"""Shopping cart data structures and pricing logic.

This module performs no I/O; callers handle persistence.
"""
```

It identifies purpose and the module boundary: logic/data structures live here; file/database access belongs to callers.

### 7. Write a minimal README

```markdown
# wordcount

Counts words in a text file.

## Installation

```bash
uv sync
```

## Usage

```bash
uv run python -m wordcount myfile.txt
# 452 words
```
```

The title names the tool; the overview states its purpose; installation gives an exact command; usage gives a runnable invocation and expected output. Verify the module name and output against the actual CLI.

### 8. Document CLI exit codes

```markdown
| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | File not found |
```

Exit codes let shell scripts distinguish success from known failure. They must match the application's actual `main()` return behavior.

### 9. Document configuration

```markdown
| Variable | Required | Default | Description |
|---|---|---|---|
| `WORDCOUNT_ENCODING` | No | `utf-8` | Text encoding used to read the input file. |
```

The table states optionality, default, and purpose. The application must actually read this variable and apply the documented default.

## Level 3 — Advanced

### 10. Document a package API

`textutils/__init__.py`:

```python
"""textutils: word and line counting utilities for plain-text files."""

from textutils.counting import count_words, count_lines

__all__ = ["count_words", "count_lines"]
```

The first string is the package docstring. Imports expose the supported functions. `__all__` declares names included by `from textutils import *` and signals the intended public surface. `_split_tokens` is excluded because it is internal.

### 11. Write an architecture overview

> The `wordcount` CLI (`wordcount/cli.py`) parses arguments and reads the target file, then calls the `textutils` library (`textutils/counting.py`) to perform counting. `textutils` does not depend on the CLI and performs no I/O, so other applications can reuse it independently.

This states responsibilities and dependency direction: the library owns counting logic; the CLI owns user interaction and file I/O.

### 12. Write an ADR

```markdown
# ADR 0001: Default to UTF-8 file encoding

## Context
Input files may use different encodings. Guessing incorrectly can
produce corrupted text or decoding errors.

## Decision
Use UTF-8 by default. Allow an explicit `WORDCOUNT_ENCODING`
override for legacy files.

## Alternatives Considered
- Automatic detection: rejected because it can guess incorrectly
  and silently.

## Consequences
Users with non-UTF-8 files must set `WORDCOUNT_ENCODING`.
Document this setting in the README.
```

Context describes the problem; Decision records the chosen approach; Alternatives records why auto-detection was rejected; Consequences states the burden for legacy files.

### 13. Document `UnicodeDecodeError`

```markdown
**Problem:** `UnicodeDecodeError` when running wordcount.

**Symptoms:** The CLI reports that a byte cannot be decoded as UTF-8.

**Likely Cause:** The input file is not UTF-8 encoded, or is not
actually text.

**Diagnosis:** Confirm the file type and determine its actual encoding.
Do not assume the extension proves its encoding.

**Solution:** Set `WORDCOUNT_ENCODING` to the correct supported
encoding, if the application supports it.

**Verification:** Run the command again and confirm the expected count.

**Prevention:** Document the required input encoding.
```

A decoding error usually means bytes cannot be interpreted using the selected encoding. Changing the setting will not fix a binary file or unrelated tokenizer bug.

### 14. Create developer onboarding instructions

```markdown
1. Clone the repository.
2. Run `uv sync` to install dependencies.
3. No configuration is needed for the default UTF-8 case.
4. Run `uv run python -m wordcount README.md`.
5. Run tests with `uv run pytest`.
6. Run linting with `uv run ruff check .`.
7. Read the architecture overview to understand CLI/library boundaries.
8. Pick a scoped good-first issue and submit a PR.
```

This takes a contributor from clean checkout to working run, tests, quality checks, architecture understanding, and first change.

## Level 4 — Production

### 15. Document a backend API contract

For `get_order(order_id: int) -> Order`, document:
- **Input:** `order_id` must identify an existing order.
- **Return:** the order representation permitted for the authenticated caller; do not expose private fields to unauthorized users.
- **Errors:** `OrderNotFoundError` when absent; `PermissionDeniedError` when unauthorized.
- **Side effects:** read-only; does not modify order state.
- **Compatibility:** identify stable fields and how breaking schema changes are versioned.

The type signature alone does not express authorization, privacy, or compatibility guarantees.

### 16. Document a data pipeline

```markdown
# Pipeline: Daily Wordcount Warehouse Load

**Input:** Per-file JSON results in
`s3://<bucket>/wordcount/<date>/`.

**Transformation:** Validate records and aggregate per-directory
word totals.

**Output:** `warehouse.wordcount_daily`, partitioned by `date`.

**Failure handling:** Missing files are logged and reported; they do
not fail the entire scheduled run.

**Retries and reruns:** Idempotent per date. Re-running a date
reconciles that date's output instead of duplicating it.

**Operations:** Record source/accepted/rejected/output counts, run ID,
and processing date. Link to the runbook.
```

A real contract should add owner, schedule/SLA, exact schemas, partition/retention policy, quality rules, late-data/backfill behavior, and monitoring.

### 17. Document an ML pipeline

```markdown
# Model: word_frequency_anomaly

**Input:** Daily word-frequency vector with documented feature names,
order, dtype, and allowed range.

**Output:** Anomaly score in `[0, 1]`.

**Preprocessing:** Inference normalization must exactly match
training-time normalization and feature ordering.

**Versioning:** Record model artifact, preprocessing, Python/runtime,
and dependency versions.

**Evaluation:** Link dataset, baseline, metrics, thresholds, and
known limitations.

**Deployment:** Link deployment, monitoring, drift-alert, and rollback
runbooks.
```

ML docs must preserve preprocessing/model reproducibility because mismatched features can produce plausible but wrong predictions without a crash.

### 18. Document an AI agent system

```markdown
# Agent: summarize_wordcount_report

**Purpose:** Summarize a wordcount report and optionally email it.

**Tool:** `send_email`
- Inputs: recipient, subject, body.
- Permission: send only to recipients in the configured allow-list.
- Side effect: sends an external email.
- Safety: recipient allow-list is enforced by tool implementation,
  not only by the model prompt.
- Failure: tool errors are surfaced and logged, not treated as success.
- Observability: record request ID, tool name, outcome, latency, and
  safe redacted metadata.
```

Document model/provider and prompt versions, tool schemas, permissions, retry/idempotency, human approval, failure behavior, and audit trail. Never rely on prompt text as the only security control.

### 19. Create a production runbook

```markdown
# Runbook: wordcount reports zero words for a non-empty file

**Symptom:** A known non-empty input produces a zero-word result.

**Diagnosis:**
1. Confirm the file is text, not binary.
2. Confirm the configured encoding matches the file.
3. Check whether decoding errors are raised, ignored, or replaced.
4. Inspect decoded text before tokenization/normalization.
5. Check whether tokenization rules discard the content.

**Likely causes:** Wrong encoding, binary input, or parsing/
normalization bug.

**Remediation:** Set `WORDCOUNT_ENCODING` to the correct supported
encoding. Fix tokenizer/normalization logic if decoded text is present
but produces no tokens.

**Verification:** Re-run on the same file and compare with a known
expected count.

**Escalation:** If correct encoding and valid text still produce zero,
capture a safe sample and open an issue.
```

A wrong encoding commonly raises `UnicodeDecodeError` unless the program ignores/replaces errors. Zero output can also come from binary input or logic that discards valid decoded content, so diagnosis checks each stage.

# Part D — Debugging Lab: All Eight Issues

1. `calculate_total()` says `Returns: None`, but returns a float. Replace it with “The total price.”
2. Its `Args:` section omits `quantity`. Add “Number of items; must be non-negative.”
3. It raises `ValueError` for negative quantity but does not document it. Add `Raises: ValueError: If quantity is negative.`
4. `apply_discount()` says `total (float): a floating point number`; this repeats the type hint and adds no meaning. Use “The pre-discount amount.”
5. `apply_discount()` has no return section. Explain it returns the discounted total for `SUMMER10`, otherwise the original total.
6. README installation references stale package name `billing-service-old-name`. Replace it with the actual distribution name from `pyproject.toml`.
7. README imports `calc_total`, but the function is named `calculate_total`. Correct the import and call.
8. README says “Set your discount codes in the environment” without naming the variable, format, or default. Document the actual variable (e.g. `DISCOUNT_CODES`), optionality, comma-separated format, default empty, and safe example.

Corrected docstrings:

```python
def calculate_total(price: float, quantity: int) -> float:
    """Calculate the total price.

    Args:
        price: Unit price.
        quantity: Number of items; must be non-negative.

    Returns:
        The total price.

    Raises:
        ValueError: If quantity is negative.
    """
    if quantity < 0:
        raise ValueError("quantity must be non-negative")
    return price * quantity


def apply_discount(total: float, code: str) -> float:
    """Apply a supported discount code.

    Args:
        total: The pre-discount amount.
        code: Discount code, such as "SUMMER10".

    Returns:
        The discounted total, or the original total if the code
        is not recognized.
    """
    if code == "SUMMER10":
        return total * 0.9
    return total
```

# Part E — Interview Questions and Architecture Questions

## Interview answers

1. **Docstring?** First string statement in a function/class/module, stored in `__doc__` and exposed through `help()`.
2. **Comment vs docstring?** A comment explains a local implementation detail and is not runtime metadata; a docstring describes a callable/type/module contract.
3. **Why README?** It is the first project entry point and shows what the software does and how to run it.
4. **What is `__doc__`?** Runtime attribute containing a docstring or `None`.
5. **What belongs in function docs?** Summary and useful non-obvious arguments, returns, exceptions, side effects, examples, and constraints.
6. **Why combine types and docstrings?** Types describe data shape; docstrings describe behavior, meaning, business rules, and side effects.
7. **Google vs NumPy?** Google is compact prose; NumPy gives parameter types separate structured lines and is common in scientific Python.
8. **What belongs in README?** Overview, prerequisites, installation, configuration, usage, testing, troubleshooting, and contribution links.
9. **Documentation drift?** Docs gradually become inconsistent with code after changes that are not reflected in docs.
10. **How document a package?** Package docstring and deliberate exports, detailed module/API docstrings, README, and generated API reference.
11. **How keep docs synchronized?** Update docs in the same PR as code, review them, and use executable examples/doctests and CI checks to catch drift.
12. **How document a public API?** State input expectations, outputs, errors, side effects, guarantees, and compatibility expectations.
13. **Generate versus hand-write?** Generate exhaustive signatures/reference; hand-write tutorials, workflows, architecture rationale, and explanations.
14. **How document a large Python service?** Layer docstrings, generated API reference, getting-started README, architecture docs/ADRs, operational runbooks, and changelog.
15. **How document an ML pipeline?** Record inputs, exact preprocessing, model/version, pinned dependencies, evaluation metrics, deployment, monitoring, and rollback.
16. **How document an agentic AI system?** Record tool purpose/permissions, failure/retry behavior, model/prompt configuration, code-enforced safety boundaries, and observability.
17. **How prevent stale docs?** Documentation-as-code, same-PR review, executable examples, periodic audits, and a tracked documentation-debt backlog.
18. **How integrate documentation into CI?** Run doctests, Markdown/link checks, and practical README command smoke tests as independent checks.

## Architecture answers

1. **Where developer docs?** In the repository, versioned and reviewed with code.
2. **README vs architecture docs?** README explains how to run/use; architecture docs explain components, data flow, dependencies, and why.
3. **API reference vs tutorial?** Reference is exhaustive lookup; tutorial is an ordered beginner learning path.
4. **How version docs?** Match supported software versions; maintain versioned doc sets when multiple major versions are supported.
5. **Monorepo documentation?** Each package owns local README/API/ADRs; cross-cutting decisions belong at repository/system level.
6. **Runbook maintenance?** Update after incidents expose missing steps and audit periodically.
7. **Agent tool contracts?** Document purpose, schema, permissions, side effects, and code-enforced limits as rigorously as public APIs.

# Part F — Knowledge Check: All 25 Answers

1. A comment is a `#` source note; a docstring is a first-statement string stored as `__doc__`.
2. A docstring must be the first statement in the function/class/module body.
3. `__doc__`.
4. Google, NumPy, and Sphinx/reStructuredText.
5. Type hints already specify the type; repeating it creates redundancy and drift risk.
6. A module docstring describes one `.py` file; package docs describe the whole package and its public entry points.
7. `__all__` controls `from package import *` exports and signals intended public names; it is not access control.
8. Public API is a supported external contract; private implementation detail can change without compatibility promise.
9. Any three: overview, prerequisites, installation, configuration, usage, tests, troubleshooting, structure, development/contribution.
10. CLI `--help` is generated, terminal-native user documentation.
11. Drift is code/docs falling out of sync; a cause is a renamed function without README/example updates.
12. Drift is the process; documentation debt is the accumulated stale/missing/contradictory backlog.
13. Changelog is cumulative and concise per release; release notes are a narrative announcement for a specific release.
14. `doctest` executes `>>>` examples and checks expected output; it is in the Python standard library.
15. Sphinx is reStructuredText-oriented and highly extensible; MkDocs is Markdown-first and generally simpler to start with.
16. `pydoc` is part of Python's standard library.
17. Tutorials, how-to guides, reference, and explanation.
18. User docs explain installation/usage; developer docs explain setup, architecture, testing, and contribution.
19. `CONTRIBUTING.md` contains development setup, coding standards, tests/quality commands, branch/PR/commit expectations.
20. ADR records a decision; common sections are Context, Decision, Alternatives Considered, Consequences.
21. Runbook is a procedural response to one operational scenario; troubleshooting guide is a broader collection of known problems.
22. ML preprocessing must match training exactly; otherwise predictions can be silently wrong.
23. Agentic systems add model nondeterminism, provider changes, prompts, tool actions, permissions, and side effects that are not obvious from ordinary code.
24. Never include real credentials, API keys, passwords, private tokens, or sensitive production/customer information.
25. 100% coverage only measures docstring presence, not correctness or usefulness.

# Part G — Mastery Checklist

- [ ] Distinguish comments, docstrings, and external documentation.
- [ ] Place module/class/function/method docstrings correctly.
- [ ] Write concise Google-style docstrings and recognize NumPy/Sphinx styles.
- [ ] Explain type hints versus behavioral documentation.
- [ ] Document class invariants, attribute meaning, and public method contracts.
- [ ] Define a clear package public API with `__all__`.
- [ ] Write a README with tested install/configuration/usage commands.
- [ ] Document CLI arguments, help, output, errors, and exit codes.
- [ ] Explain documentation drift/debt and Documentation as Code.
- [ ] Distinguish pydoc, Sphinx, MkDocs, and doctest.
- [ ] Organize content with Diátaxis.
- [ ] Write CONTRIBUTING, architecture docs, ADRs, and runbooks.
- [ ] Document pipeline schemas, transformations, idempotency, and recovery.
- [ ] Document ML preprocessing/model versions/evaluation/rollback.
- [ ] Document agent tools, permissions, failure behavior, and code-enforced safety.
- [ ] Keep secrets out of docs and examples.
- [ ] Review docs for correctness, completeness, clarity, consistency, discoverability, maintainability, audience, and actionability.

## Final learning position

Module 1.6, Lesson 07 is covered in this guide. Apply it to the existing Stage 1 projects; do not advance to the next lesson until instructed. The most important habit is to update code and its documentation together, and to make every example and operational instruction match the real implementation.
