# Notebooks, Git Folders and Project Structure

> **Module:** G4 — Databricks Lakehouse Platform Deep Dive  
> **Topic:** 03 — Notebooks, Git Folders and Project Structure  
> **Phase:** A — Platform Foundations  
> **Level:** Basic → Intermediate → Advanced → Production

---

# What You Will Learn

This module teaches how professional Data Engineers develop and organize code in Databricks.

You will progress from interactive notebook work to production-oriented software engineering:

```text
Databricks Notebook
        ↓
Notebook Development
        ↓
Notebook Features
        ↓
Widgets / Parameters
        ↓
dbutils
        ↓
Secrets
        ↓
Git Folders
        ↓
Project Structure
        ↓
Python Modules / Packages
        ↓
Local Development
        ↓
Databricks Connect
        ↓
Testing
        ↓
Linting / Formatting
        ↓
Code Review
        ↓
Deployment
        ↓
Production Engineering
```

By the end, you should be able to explain not only **how** to use a Databricks notebook, but also **when a notebook is appropriate, when logic should move into reusable Python code, how Git becomes the source of truth, how parameters and secrets should be handled, and how a project moves from experimentation to production**.

## Why This Topic Matters

Many beginners stop at:

```text
Open notebook
→ write code
→ run cells
→ manually fix production
```

Professional Data Engineering moves toward:

```text
Experiment
   ↓
Notebook
   ↓
Reusable Code
   ↓
Git
   ↓
Python Package
   ↓
Tests
   ↓
CI/CD
   ↓
Production
```

A notebook is therefore not the opposite of production engineering. It is one development surface within a larger engineering system.

The key transition is:

> **Use notebooks for interactive thinking; use version-controlled, testable code for reusable production behavior.**

---

# 1. Module Scope and Boundaries

This topic covers:

- Databricks notebooks
- notebook cells
- Markdown cells
- code cells
- notebook state
- notebook magics
- `%run`
- widgets
- visualizations
- `dbutils`
- secrets
- workspace files
- Git folders
- Git workflows
- Python modules and packages
- project organization
- local development
- IDE integration
- Databricks Connect
- job parameters
- Python function arguments
- configuration management
- code quality
- linting
- formatting
- testing
- code review
- notebook anti-patterns
- production refactoring

This topic intentionally does **not** deeply teach:

- Unity Catalog governance — Topic 04
- Auto Loader — Topic 05
- Lakeflow Connect — Topic 06
- Lakeflow Declarative Pipelines — Topic 07
- Lakeflow Jobs — Topic 08
- Asset Bundles in depth — Topic 12
- general Python programming from first principles
- generic Git training unrelated to Databricks engineering

The goal is to connect those later capabilities to a professional development model.

---

# 2. What Is a Databricks Notebook?

A Databricks notebook is an interactive development surface containing executable cells and documentation.

A simple example:

```python
df = spark.read.table("bronze.orders")

display(df)
```

Conceptually:

```text
Notebook
   |
   +-- Code
   +-- Markdown
   +-- Parameters
   +-- Outputs
   +-- Visualizations
   +-- Execution state
   |
   v
Attached / selected compute
   |
   v
Data + Spark execution
```

## What Happens When a Cell Runs?

At a high level:

1. The notebook submits code for execution.
2. The selected execution environment processes it.
3. Spark/Python/SQL performs the requested work.
4. The result is returned to the notebook interface.
5. The notebook displays output, errors, tables, or visualizations.

The notebook is therefore an **interactive interface to execution**, not the compute engine itself.

Topic 02 covers compute architecture. Here the important relationship is:

```text
Notebook
   ↓
Execution context
   ↓
Databricks compute
   ↓
Data / Spark / SQL execution
```

## When Notebooks Are Excellent

Notebooks are particularly useful for:

- exploration
- data investigation
- prototyping
- debugging
- demonstrations
- interactive validation
- learning
- lightweight operational workflows
- communicating analytical reasoning

## When Notebooks Become Weak

They become problematic when they contain:

- hundreds of lines of tightly coupled business logic
- hidden state
- undocumented execution order
- credentials
- environment-specific constants
- duplicated transformations
- no automated tests
- manual production edits
- long `%run` chains

---

# 3. Notebook Cells

A notebook is normally organized into cells.

## 3.1 Code Cells

Code cells can contain supported languages such as:

- Python
- SQL
- Scala
- R where supported

Example:

```python
df = spark.read.table("bronze.orders")
display(df)
```

SQL example:

```sql
SELECT
    order_id,
    customer_id,
    order_total
FROM bronze.orders;
```

A code cell should ideally perform a coherent operation rather than becoming an enormous block of unrelated logic.

## 3.2 Markdown Cells

Markdown cells document the notebook.

Useful content includes:

- purpose
- assumptions
- inputs
- outputs
- architecture notes
- experiment findings
- validation results
- operational instructions

A useful notebook outline is:

```text
# Purpose

## Inputs

## Configuration

## Read

## Transform

## Validate

## Write

## Validation

## Notes
```

The objective is not decorative documentation. The notebook should communicate enough context that another engineer can understand what it is doing.

## Cell Design Rule

Prefer:

```text
one conceptual responsibility
```

over:

```text
one giant cell containing the entire pipeline
```

---

# 4. Notebook State and Reproducibility

Notebook state is one of the most important concepts for production engineering.

Consider:

```python
x = 10
```

and later:

```python
x = x + 5
```

If the cells are executed in the expected order, the result is:

```text
15
```

But interactive notebooks allow cells to be executed in different orders.

For example:

```text
Cell 1: x = 10
Cell 2: x = x + 5
Cell 3: x = x * 2
```

If Cell 3 is executed before Cell 2, the result depends on what state already exists.

## Hidden State

Common hidden-state problems include:

- variables created in earlier cells
- objects left from previous runs
- imported modules with changed definitions
- temporary views
- cached values
- configuration variables
- partially executed transformations

This creates a dangerous situation:

```text
Notebook appears to work
        ↓
But only after a particular execution sequence
```

## Critical Production Principle

> **A notebook that only works when cells are executed in a specific undocumented order is not production-ready code.**

## Reproducibility Test

A useful development habit is:

1. Restart the execution environment where appropriate.
2. Run the notebook from a clean state.
3. Execute cells in the documented order.
4. Confirm outputs.
5. Repeat with different valid parameters.

The goal is to expose hidden dependencies before deployment.

---

# 5. Notebook Organization

A production-oriented notebook should make the execution flow visible.

Example:

```text
1. Purpose
2. Imports
3. Parameters
4. Configuration
5. Input validation
6. Read
7. Transform
8. Data-quality checks
9. Write
10. Output validation
11. Operational notes
```

A notebook should answer:

- What does this notebook do?
- What does it read?
- What does it write?
- Which parameters control it?
- Which environment is it targeting?
- What assumptions does it make?
- What validations are performed?
- What should an operator do if it fails?

---

# 6. Notebook Magics

Notebook magic commands provide notebook-specific execution or utility behavior.

Common examples include:

```text
%python
%sql
%md
%run
%sh
```

Exact availability and behavior can vary by Databricks product and runtime version, so version-sensitive syntax should be checked against current official Databricks documentation.

## `%python`

Used to explicitly indicate Python execution where supported.

```text
%python
print("hello")
```

## `%sql`

Used for SQL execution.

```sql
%sql
SELECT *
FROM catalog.schema.orders;
```

## `%md`

Used for Markdown content in environments that support the magic form.

```text
%md
# Data Quality Investigation
```

## `%sh`

Used for supported shell operations.

```text
%sh
echo "Inspecting runtime environment"
```

Shell commands should be used intentionally. Do not treat a notebook as an unmanaged server terminal.

## Magic Command Trade-Offs

Magics are useful because they make interactive development convenient.

They can become a problem when:

- they hide dependencies
- they reduce portability
- shell commands become essential production logic
- notebook-specific behavior replaces reusable code
- a deployment process depends on undocumented runtime behavior

Use magics as tools, not as a substitute for project architecture.

---

# 7. `%run`

`%run` is explicitly important because it can be useful and also become an anti-pattern.

Conceptually:

```text
Notebook A
   |
   +--> %run Notebook B
              |
              +--> %run Notebook C
```

## Why Engineers Use `%run`

Typical reasons include:

- sharing notebook code
- loading helper functions
- reusing configuration
- avoiding copy/paste
- composing notebook-based workflows

## The Problem With Long Chains

Consider:

```text
A
 ↓
B
 ↓
C
 ↓
D
 ↓
E
```

An engineer opening A may not immediately know:

- what B imports
- what C changes
- which variables D creates
- whether E depends on hidden state
- which notebook owns the business logic

Debugging becomes increasingly difficult.

## `%run` vs Python Package

Notebook dependency:

```text
Notebook
   ↓
%run another notebook
   ↓
hidden shared state
```

Python dependency:

```text
Notebook
   ↓
Python module
   ↓
explicit import
   ↓
reusable function
```

The second model makes dependencies clearer.

## When `%run` Can Be Reasonable

It can be appropriate for:

- small notebook utilities
- controlled educational workflows
- limited interactive composition
- legacy migration stages
- simple notebook-only helper code

## When a Module Is Better

Prefer Python modules/packages when:

- logic is reused
- logic needs unit tests
- multiple jobs depend on it
- business rules matter
- code review is important
- dependency structure should be explicit
- the code should run outside a particular notebook

## Migration Strategy

Do not blindly remove every `%run`.

Instead:

```text
Identify dependency
      ↓
Extract reusable functions
      ↓
Create Python module
      ↓
Add tests
      ↓
Replace %run dependency
      ↓
Validate behavior
      ↓
Remove obsolete notebook helper
```

---

# 8. Notebook Widgets

Widgets provide runtime inputs to notebook execution.

A conceptual example:

```python
dbutils.widgets.text("environment", "dev")

environment = dbutils.widgets.get("environment")

print(environment)
```

A widget can make a notebook reusable across runs:

```text
environment = dev
environment = staging
environment = prod
```

The exact widget capabilities and UI behavior can vary by current Databricks environment.

## Good Widget Uses

Widgets are useful for:

- environment
- date
- source
- target
- processing mode
- backfill date
- test mode

Example:

```text
environment
run_date
processing_mode
```

## Poor Widget Use

Avoid turning widgets into a replacement for application architecture.

For example, a notebook should not have dozens of unrelated widgets controlling every internal implementation detail.

Prefer:

```text
Job parameter
      ↓
Notebook parameter
      ↓
Python function argument
      ↓
Business logic
```

---

# 9. Notebook Parameters vs Python Arguments

This distinction is critical.

## Notebook Widget

```text
Notebook
   ↓
Widget
   ↓
Runtime parameter
```

Best for:

- interactive notebook execution
- simple job parameters
- operator-controlled inputs

## Job Parameter

```text
Workflow
   ↓
Job parameter
   ↓
Task / notebook
```

Best for:

- workflow-level configuration
- scheduled runs
- orchestration
- environment-independent runtime values

## Python Function Argument

```python
def load_orders(input_path, target_table):
    ...
```

Best for:

- reusable business logic
- unit testing
- explicit dependencies
- modular code

## Configuration

Best for:

- environment-specific settings
- non-secret deployment configuration

## Secret

Best for:

- passwords
- tokens
- API credentials
- other sensitive values

### Decision Table

| Mechanism | Best Use |
|---|---|
| Widget | Interactive/job notebook parameter |
| Job parameter | Workflow-level configuration |
| Python argument | Reusable business logic |
| Environment/config | Environment configuration |
| Secret | Sensitive credential |

The professional principle is:

> **Keep runtime input at the boundary and business logic independent of the notebook interface.**

---

# 10. Visualizations

Databricks notebooks are valuable for interactive data inspection.

Typical uses include:

- `display()`
- DataFrame inspection
- notebook charts
- exploratory analysis
- debugging
- validation
- communicating findings

Example:

```python
display(
    df.groupBy("status")
      .count()
)
```

Use visualizations to answer questions such as:

```text
Did the transformation work?
Are nulls increasing?
Are values distributed as expected?
Did a filter remove the expected records?
```

## What Not to Do

Do not turn notebook visualization code into an accidental replacement for an appropriate production analytics or dashboarding system.

The notebook is excellent for:

```text
Explore
Debug
Validate
Communicate
```

Production reporting should use the appropriate analytics/dashboarding capability.

---

# 11. `dbutils`

`dbutils` provides Databricks runtime utilities.

The exact API surface can evolve, so current official documentation should be consulted before relying on version-specific behavior.

Relevant areas include:

- file utilities
- secrets
- widgets
- notebook/runtime utilities where supported

Example:

```python
dbutils.fs.ls("/mnt/example")
```

Widget example:

```python
dbutils.widgets.text("date", "2026-01-01")
```

Secret example:

```python
password = dbutils.secrets.get(
    scope="database",
    key="password"
)
```

The key architectural point is that `dbutils` is an environment/runtime utility interface. It should not become the place where all business logic lives.

---

# 12. Secrets

Secrets are sensitive configuration that must not be embedded in source code.

Examples:

- API keys
- passwords
- access tokens
- database credentials
- service credentials

## Bad

```python
password = "my-super-secret-password"
```

This creates multiple risks:

```text
Source code
   ↓
Git history
   ↓
Clones / backups
   ↓
Potential exposure
```

It may also appear in:

- notebook content
- notebook output
- logs
- screenshots
- error messages

## Better Conceptual Pattern

```python
password = dbutils.secrets.get(
    scope="database",
    key="password"
)
```

The exact secret-scope architecture and APIs are version-sensitive and should be verified against current Databricks documentation.

## Secret Management Principles

1. Never hardcode secrets.
2. Do not commit secrets to Git.
3. Avoid printing secrets.
4. Avoid placing secrets in notebook outputs.
5. Separate environments.
6. Apply least privilege.
7. Rotate credentials according to organizational policy.
8. Audit access.
9. Use automation identities rather than personal credentials for production workflows.
10. Treat accidental secret exposure as a security incident.

## If a Secret Reaches Git History

Deleting the line from the latest commit is not sufficient.

The response should conceptually be:

```text
Stop using credential
       ↓
Rotate / revoke credential
       ↓
Assess exposure
       ↓
Remove secret from source/history according to organizational process
       ↓
Audit usage
       ↓
Prevent recurrence
```

---

# 13. Workspace Files

Workspace files are project-oriented files stored in the Databricks workspace environment.

Use them intentionally for supported project assets, documentation, and code organization.

Compare the concepts:

```text
Notebook
vs
Workspace File
vs
Git Folder
vs
Cloud Storage
```

| Asset | Typical Role |
|---|---|
| Notebook | Interactive executable development |
| Workspace file | Workspace-level project/document/code asset |
| Git Folder | Version-controlled development project |
| Cloud storage | Persistent data / external storage |

The exact capabilities and terminology can evolve. Verify current workspace-file behavior before designing production deployment around a particular feature.

## Principle

A workspace is not automatically the same thing as a source-code repository.

For production engineering:

```text
Git repository
       ↓
reviewed source
       ↓
controlled deployment
       ↓
Databricks environment
```

---

# 14. Git Folders

Git-based development is the bridge from notebook experimentation to software engineering.

Important concepts:

- repository
- branch
- commit
- pull
- push
- merge
- pull request
- code review

Conceptual workflow:

```text
Developer
   |
Git Folder
   |
Branch
   |
Code
   |
Commit
   |
Push
   |
Pull Request
   |
Review
   |
Merge
```

## Why Git Matters

Git provides:

- history
- collaboration
- review
- rollback capability
- change visibility
- branching
- controlled integration

Without Git, the workspace can become the accidental source of truth:

```text
Developer A edits notebook
Developer B edits notebook
Developer C copies notebook
Nobody knows which version is current
```

With Git:

```text
Repository
   |
   +-- main
   +-- feature/order-cleanup
   +-- feature/dq-rules
```

The project becomes explicit and reviewable.

## Git-First Principle

> **Databricks is an execution and development platform; Git should provide the authoritative history for source code.**

Exact Git-folder capabilities, supported providers, authentication mechanisms, and terminology can change. Verify the current Databricks documentation for your environment.

---

# 15. Git Folder Project Organization

A production-oriented project might look like:

```text
orders-platform/
├── README.md
├── databricks.yml
├── src/
│   └── orders/
│       ├── __init__.py
│       ├── ingestion.py
│       ├── transformations.py
│       ├── validation.py
│       └── publishing.py
├── tests/
│   ├── test_ingestion.py
│   ├── test_transformations.py
│   └── test_validation.py
├── notebooks/
│   ├── exploration/
│   └── operational/
├── sql/
│   ├── bronze/
│   ├── silver/
│   └── gold/
└── docs/
    └── architecture.md
```

## Directory Responsibilities

### `README.md`

Explains:

- project purpose
- setup
- development workflow
- testing
- deployment assumptions

### `src/`

Contains reusable application/data-engineering logic.

### `tests/`

Contains automated tests.

### `notebooks/`

Contains interactive development, exploration, and controlled operational notebooks.

### `sql/`

Contains SQL assets when SQL is the appropriate implementation language.

### `docs/`

Contains architecture, operational, and engineering documentation.

### `databricks.yml`

May be used as project/deployment configuration where the chosen Databricks deployment approach supports it. Asset Bundles are covered in depth later in Topic 12.

The exact structure can vary. A project is healthy when responsibilities are clear, dependencies are explicit, and deployment does not depend on a developer's personal workspace state.

---

# 16. Python Modules and Packages

Reusable business logic should generally be separated from notebooks.

Good architecture:

```text
Notebook
   |
   +--> Python Module
           |
           +--> Business Logic
```

Weak architecture:

```text
Notebook
   |
   +--> 500 lines of business logic
```

## Python Module

Example:

```python
# src/orders/transformations.py

def clean_orders(df):
    return (
        df
        .filter("order_id IS NOT NULL")
        .dropDuplicates(["order_id"])
    )
```

Notebook:

```python
from orders.transformations import clean_orders

clean_df = clean_orders(df)
```

This makes the transformation:

- reusable
- testable
- reviewable
- composable

## Modules

A module is a Python source file containing related code.

Example:

```text
transformations.py
```

## Package

A package organizes multiple modules under a coherent boundary.

Example:

```text
orders/
├── __init__.py
├── ingestion.py
├── transformations.py
├── validation.py
└── publishing.py
```

## Package Boundaries

A useful package boundary reflects a business or technical responsibility.

Avoid:

```text
everything.py
```

Prefer:

```text
ingestion.py
transformations.py
validation.py
publishing.py
```

when those responsibilities are genuinely distinct.

## Classes

Use classes where they improve:

- state management
- abstraction
- dependency management
- reusable interfaces

Do not introduce classes merely to make simple transformation functions appear sophisticated.

---

# 17. Notebook vs Python Module

| Dimension | Notebook | Python Module |
|---|---|---|
| Exploration | Excellent | Moderate |
| Reuse | Limited | Excellent |
| Testing | Harder | Easier |
| Code review | Harder | Better |
| Version control | Possible | Strong |
| Visualization | Excellent | Limited |
| Production logic | Limited | Preferred |
| Interactive documentation | Strong | Code/docs |

The correct conclusion is **not**:

> Never use notebooks.

The correct conclusion is:

> **Use the development surface that matches the job.**

---

# 18. Notebooks in Production

Notebooks can be legitimate production assets.

Appropriate examples:

- operational investigation
- lightweight parameterized workflows
- demonstrations
- controlled scheduled tasks
- interactive debugging

But when the code contains significant reusable business logic, move that logic into modules/packages.

A mature progression is:

```text
Prototype Notebook
       ↓
Refactor
       ↓
Python Module
       ↓
Tests
       ↓
Package
       ↓
Job
       ↓
CI/CD
       ↓
Production
```

---

# 19. Local Development

Local development provides software-engineering capabilities that are often more comfortable in an IDE.

The roadmap environment includes:

- Python 3.12+
- `uv`
- Git
- pytest
- Databricks Connect
- VS Code / IDE tooling

The exact dependency and IDE setup should be verified against current Databricks and project documentation.

## Why Develop Locally?

Local development supports:

- fast editing
- structured project navigation
- source control
- unit tests
- linting
- formatting
- debugging
- dependency management
- code review preparation

## IDE Integration

A professional workflow may look like:

```text
VS Code / IDE
     |
     +-- source code
     +-- tests
     +-- configuration
     +-- Git
     |
     v
Databricks
```

The IDE becomes the software-engineering environment while Databricks provides the managed data/compute execution environment.

---

# 20. Local vs Databricks Development

| Activity | Local | Databricks |
|---|---|---|
| Git development | Excellent | Good |
| Unit tests | Excellent | Possible |
| Interactive Spark | Limited/local | Excellent |
| Production data | Usually no | Yes |
| IDE experience | Excellent | Integrated |
| Debugging | Strong | Strong |
| Deployment | CI/CD | Runtime |

A professional hybrid workflow:

```text
Local IDE
   |
Git
   |
Unit Tests
   |
Push
   |
Databricks
   |
Databricks Connect / CI
   |
Integration Test
   |
Production
```

The objective is not to move everything local or everything into Databricks. It is to put each development activity in the environment where it is most effective and safe.

---

# 21. Databricks Connect

Databricks Connect enables supported local development workflows against remote Databricks compute.

Conceptually:

```text
VS Code
   |
Python Code
   |
Databricks Connect
   |
Remote Databricks Compute
   |
Cloud Data
```

This can provide:

- local IDE workflow
- organized source code
- local debugging experience
- automated testing patterns
- remote Spark execution

## Important Limitations

Engineers must account for:

- authentication
- network access
- version compatibility
- remote compute requirements
- dependency differences
- supported feature differences

Do not assume that every notebook behavior is identical to local Python execution.

## Version Compatibility

A common failure class is:

```text
Local client
    ≠
Remote runtime / supported server configuration
```

Always verify current Databricks Connect compatibility requirements before implementation.

Do not rely on remembered commands when the current product syntax may have changed.

---

# 22. Job Parameters and Python Arguments

Think in three levels:

```text
Workflow Parameters
        ↓
Notebook Parameters
        ↓
Python Function Arguments
```

Example:

```python
def run_pipeline(
    input_table: str,
    output_table: str,
    run_date: str,
):
    ...
```

Configuration should flow from the execution boundary toward the business logic.

Typical parameters include:

- environment
- date
- source
- target
- mode
- backfill

The function should not need to know whether its values came from:

- a widget
- a job
- a CLI
- a test
- a configuration file

That separation improves reuse.

---

# 23. Configuration Management

Separate configuration from business logic.

Bad:

```python
catalog = "production_catalog"
```

Better:

```python
catalog = config.catalog
```

The exact implementation may be:

- a configuration object
- environment configuration
- deployment configuration
- job parameters
- another approved configuration mechanism

The principle is:

```text
Business logic
      ≠
Environment identity
```

The same business logic should ideally be deployable to:

```text
dev
staging
prod
```

without editing the business logic itself.

---

# 24. Hard-Coded Paths

The roadmap explicitly identifies hardcoded paths as an anti-pattern.

Bad:

```python
path = "s3://company-prod-bucket/orders/"
```

Problems:

- environment coupling
- deployment problems
- accidental production writes
- testing difficulty
- hidden assumptions

Prefer configuration or governed table references appropriate to the architecture.

For example:

```python
input_table = config.input_table
```

or:

```python
path = config.input_path
```

Do not duplicate Topic 04's governance model here; the focus is development architecture.

---

# 25. Hard-Coded Catalogs and Schemas

Bad:

```python
spark.table("prod_catalog.gold.orders")
```

This binds the code directly to one environment.

Better conceptual pattern:

```python
catalog = config.catalog
schema = config.schema

table = f"{catalog}.{schema}.orders"

df = spark.table(table)
```

Now deployment can supply:

```text
dev
staging
prod
```

without modifying business logic.

The important production property is:

```text
same code
+
different configuration
=
different environment
```

---

# 26. Code Quality

Production Data Engineering code should emphasize:

- readable functions
- meaningful names
- small units of logic
- separation of concerns
- appropriate error handling
- useful logging
- type hints where useful
- documentation
- tests
- maintainable dependency boundaries

Bad:

```python
# 800 lines in one cell
```

Better:

```python
def extract_orders(...):
    ...

def transform_orders(...):
    ...

def validate_orders(...):
    ...

def publish_orders(...):
    ...
```

The objective is not maximum fragmentation. It is clear responsibility.

---

# 27. Linting

Linting is automated code-quality checking.

It can detect issues such as:

- unused imports
- undefined variables
- suspicious patterns
- style violations
- maintainability problems

A modern project may use a tool such as Ruff.

The exact rules belong in project configuration.

Example workflow:

```text
Write Code
   ↓
Format
   ↓
Lint
   ↓
Test
   ↓
Commit
```

Linting is valuable because it moves predictable review comments from humans to automation.

---

# 28. Formatting

Formatting provides consistent code presentation.

Benefits:

- easier review
- fewer style debates
- consistent codebase
- reduced diff noise
- faster onboarding

A modern formatter such as Ruff can be used where appropriate.

The important engineering principle is:

> **Automate mechanical style decisions so code review can focus on correctness and design.**

---

# 29. Testing Notebook Logic

Testing notebook logic is difficult when all logic is embedded directly in cells.

Weak:

```python
# Notebook cell
df = ...
df = transform(df)
```

Better:

```python
def transform(df):
    ...
```

Then the function can be tested independently.

Example:

```python
def test_transform_removes_null_ids(spark):
    ...
```

## Testing Layers

### Unit Tests

Test small deterministic functions.

### Integration Tests

Test interactions with:

- Spark
- Databricks
- data sources
- target systems

### DataFrame Tests

Validate:

- schema
- row-level behavior
- null handling
- duplicate behavior
- business rules

## Testing Principle

Extract logic first.

```text
Notebook logic
      ↓
Pure/reusable function
      ↓
Unit test
      ↓
Integration test where required
```

---

# 30. Code Review

A production Data Engineering pull request should be reviewed for more than syntax.

Review:

- correctness
- tests
- readability
- security
- performance
- data correctness
- configuration
- operational behavior
- permissions
- documentation

## Data Engineering PR Checklist

```text
[ ] Logic correct
[ ] Tests included
[ ] No secrets
[ ] No hardcoded production paths
[ ] No unnecessary %run chains
[ ] Configuration externalized
[ ] Logging sufficient
[ ] Performance considered
[ ] Permissions considered
[ ] Documentation updated
```

A senior reviewer should ask:

> What happens when the data is late, empty, duplicated, malformed, or much larger than expected?

---

# 31. Notebook Anti-Patterns

## Anti-Pattern 1 — Business Logic Entirely Inside Notebooks

### Symptom

A 1,000-line notebook contains every transformation.

### Why It Happens

Notebooks make experimentation easy.

### Risk

- difficult testing
- difficult reuse
- difficult review
- hidden dependencies

### Better Approach

Extract reusable logic into modules.

### Migration

```text
Identify functions
→ extract module
→ add tests
→ replace notebook logic
→ validate
```

---

## Anti-Pattern 2 — Long `%run` Chains

### Symptom

```text
A → B → C → D → E
```

### Risk

Hidden dependencies and difficult debugging.

### Better Approach

Use explicit Python imports for reusable code.

---

## Anti-Pattern 3 — Hardcoded Storage Paths

### Symptom

```python
"s3://company-prod-bucket/..."
```

### Risk

Environment coupling and accidental writes.

### Better Approach

External configuration or governed table references.

---

## Anti-Pattern 4 — Hardcoded Catalog/Schema Names

### Symptom

```python
spark.table("prod_catalog.gold.orders")
```

### Risk

Code cannot safely move across environments.

### Better Approach

Environment-aware configuration.

---

## Anti-Pattern 5 — Secrets in Notebooks

### Symptom

```python
password = "..."
```

### Risk

Credential exposure.

### Better Approach

Approved secret-management mechanisms.

---

## Additional Anti-Patterns

- giant cells
- hidden state
- out-of-order execution
- duplicated logic
- no tests
- no Git
- personal credentials
- manual production edits
- unpinned or uncontrolled dependencies
- environment-specific code embedded in business logic

---

# 32. Refactoring Lab — From Bad Notebook to Production Project

Start with a conceptual bad notebook:

```python
# Hardcoded production catalog
# Hardcoded S3 path
# Secret embedded
# 300 lines of transformation
# %run dependencies
# no tests
```

Refactor toward:

```text
Git Project
├── notebooks/
├── src/
├── tests/
├── config/
└── docs/
```

## Model Solution

### Step 1 — Identify Boundaries

Separate:

```text
Input
Transformation
Validation
Publishing
Configuration
Operations
```

### Step 2 — Extract Business Logic

Move transformations into:

```text
src/orders/transformations.py
```

### Step 3 — Add Tests

Create:

```text
tests/unit/test_transformations.py
```

### Step 4 — Externalize Configuration

Replace:

```python
catalog = "prod_catalog"
```

with a configuration object/value.

### Step 5 — Remove Secrets

Replace hardcoded credentials with approved secret retrieval.

### Step 6 — Reduce `%run`

Replace reusable dependencies with explicit imports.

### Step 7 — Put Project Under Git

Create a branch, test changes, commit, push, and open a pull request.

### Step 8 — Validate

Perform:

```text
format
→ lint
→ unit test
→ integration test
→ Databricks validation
```

### Step 9 — Deploy

Use the organization's controlled deployment mechanism rather than manually editing production.

---

# 33. Hands-On Labs

All labs are designed to remain within this learning module.

## Lab 1 — Build a Clean Notebook

Create a notebook structure containing:

- documentation
- parameters
- input
- transformation
- validation
- output

### Acceptance Criteria

```text
[ ] Purpose documented
[ ] Inputs documented
[ ] Parameters visible
[ ] Transformations organized
[ ] Validation included
[ ] Output explained
```

---

## Lab 2 — Notebook Parameterization

Create parameters for:

```text
environment
date
input
output
```

Demonstrate how the same notebook can run with different valid values.

### Acceptance Criteria

```text
[ ] Values are not embedded in business logic
[ ] Parameters are documented
[ ] Invalid input is handled
[ ] Environment is explicit
```

---

## Lab 3 — Refactor Notebook Logic

Start with transformation logic in a notebook.

Move it into Python functions.

Before:

```text
Notebook
└── transformation logic
```

After:

```text
Notebook
└── calls
    └── Python module
```

---

## Lab 4 — Build a Python Package

Use:

```text
orders/
├── __init__.py
├── ingestion.py
├── transformations.py
├── validation.py
└── publishing.py
```

Explain the responsibility of each module.

---

## Lab 5 — Git Workflow

Practice:

```text
branch
→ edit
→ test
→ commit
→ push
→ pull request
→ review
→ merge
```

Your goal is to understand the complete lifecycle, not just the Git commands.

---

## Lab 6 — Databricks Connect

Implement a local-to-remote development workflow where the current environment supports it.

Verify:

```text
[ ] Authentication
[ ] Version compatibility
[ ] Network connectivity
[ ] Remote compute
[ ] Dependency availability
[ ] Remote execution
```

Do not use remembered setup commands without checking the current Databricks documentation.

---

## Lab 7 — Secret Management

Start from:

```python
password = "hardcoded-secret"
```

Replace it with an approved secret-management pattern.

Then verify:

```text
[ ] Secret not committed
[ ] Secret not printed
[ ] Access is restricted
[ ] Rotation is possible
```

---

## Lab 8 — Testing

Write pytest tests for transformation functions.

Test at least:

- valid data
- null identifiers
- duplicates
- empty input
- expected output schema

---

## Lab 9 — Linting and Formatting

Apply:

```text
format
→ lint
→ fix
→ test
```

Verify that the project has consistent formatting and no obvious static-analysis violations.

---

## Lab 10 — Production Refactoring

Take a notebook prototype and convert it into a production-oriented project.

Deliver:

```text
Notebook strategy
Git strategy
Project structure
Python package
Configuration
Parameters
Secrets
Tests
Linting
Formatting
Local workflow
Databricks Connect workflow
Review workflow
Deployment model
```

---

# 34. Troubleshooting / Break-Fix

For every incident use:

```text
Symptom
   ↓
Evidence
   ↓
Hypotheses
   ↓
Investigation
   ↓
Root Cause
   ↓
Fix
   ↓
Verification
   ↓
Prevention
```

## Incident 1 — Notebook Works Only After Specific Cell Order

### Symptom

The notebook succeeds when the author runs cells in a particular sequence but fails when another engineer runs it from a clean state.

### Evidence

Variables or temporary objects are referenced before their documented creation point.

### Hypotheses

- hidden state
- stale session state
- undocumented dependencies
- out-of-order execution

### Investigation

1. Start from a clean state.
2. Run top to bottom.
3. Identify the first missing variable/object.
4. Trace where it should have been created.

### Root Cause

Notebook logic depends on interactive state.

### Fix

Make dependencies explicit and organize initialization.

### Prevention

Add clean-run testing to development.

---

## Incident 2 — `%run` Chain Is Broken

### Symptom

Notebook A fails after Notebook C changes.

### Evidence

A depends indirectly on C through B.

### Hypothesis

Hidden transitive dependency.

### Fix

Map the dependency chain and extract reusable logic into modules.

### Prevention

Keep `%run` usage small and intentional.

---

## Incident 3 — Production Job Uses Wrong Catalog

### Symptom

A production run writes to or reads from an unexpected catalog.

### Investigation

Search for:

- hardcoded catalog names
- notebook defaults
- environment variables
- job parameters
- configuration

### Root Cause

Environment identity was embedded in code.

### Fix

Externalize environment configuration.

### Prevention

Add code-review and automated checks for forbidden hardcoded production identifiers.

---

## Incident 4 — Secret Appears in Git History

### Symptom

A credential is discovered in a commit.

### Immediate Response

```text
Stop use
→ revoke/rotate
→ assess exposure
→ clean repository according to security process
→ audit
→ prevent recurrence
```

Do not treat a normal code deletion as sufficient credential remediation.

---

## Incident 5 — Local Code Works but Databricks Connect Fails

Investigate in order:

```text
Authentication
   ↓
Network
   ↓
Version compatibility
   ↓
Compute availability
   ↓
Dependencies
   ↓
Supported feature set
```

Avoid changing five variables at once. Establish evidence for each layer.

---

## Incident 6 — Code Review Finds a 1,000-Line Notebook

### Diagnosis

The notebook likely mixes:

- orchestration
- configuration
- business logic
- validation
- operational behavior

### Refactoring

```text
Notebook
   ↓
Identify responsibilities
   ↓
Extract modules
   ↓
Add tests
   ↓
Keep notebook as orchestration / exploration surface
```

---

## Incident 7 — Production Job Works for Developer but Fails Under Service Principal

Investigate:

```text
Identity
Permissions
Configuration
Secrets
Environment
```

The most common mistake is assuming:

> "If it works under my identity, the production identity must have the same access."

That assumption is unsafe.

---

# 35. Production Project Structure

A recommended structure is:

```text
orders-platform/
├── README.md
├── pyproject.toml
├── databricks.yml
├── src/
│   └── orders/
│       ├── __init__.py
│       ├── config.py
│       ├── ingestion.py
│       ├── transformations.py
│       ├── validation.py
│       └── publishing.py
├── notebooks/
│   ├── exploration/
│   ├── development/
│   └── operations/
├── tests/
│   ├── unit/
│   └── integration/
├── sql/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── docs/
│   ├── architecture.md
│   └── runbook.md
└── resources/
```

## `pyproject.toml`

Project/dependency metadata and tool configuration.

## `src/orders/`

Production Python package.

## `notebooks/`

Interactive and controlled notebook assets.

## `tests/`

Automated tests.

## `sql/`

SQL transformation assets.

## `docs/`

Architecture and operational documentation.

## `resources/`

Deployment/resource definitions where the selected project/deployment approach uses them.

Do not interpret this as a universal mandatory structure. Adapt it to the organization's deployment model.

---

# 36. Professional Development Workflow

A mature workflow is:

```text
1. Create issue/task
        ↓
2. Create Git branch
        ↓
3. Develop locally
        ↓
4. Unit test
        ↓
5. Format
        ↓
6. Lint
        ↓
7. Develop/debug on Databricks
        ↓
8. Integration test
        ↓
9. Commit
        ↓
10. Pull request
        ↓
11. Code review
        ↓
12. Merge
        ↓
13. Deploy
```

## 1. Create Issue

Define:

- expected behavior
- data impact
- acceptance criteria
- operational constraints

## 2. Branch

Keep work isolated.

## 3. Develop Locally

Use the IDE for:

- source code
- tests
- linting
- formatting

## 4. Unit Test

Catch deterministic defects early.

## 5–6. Format and Lint

Automate mechanical quality checks.

## 7. Databricks Development

Use Databricks for realistic Spark/data interaction.

## 8. Integration Test

Validate interactions with remote services and data.

## 9–12. Review and Merge

Use Git history and peer review.

## 13. Deploy

Production should be updated through controlled deployment rather than personal manual editing.

---

# 37. Development Environment Separation

A professional topology is:

```text
Developer Machine
        |
        v
Git Repository
        |
        v
Databricks Development Workspace
        |
        v
CI/CD
        |
        v
Production Workspace
```

The exact number of workspaces depends on organizational architecture, but the principle remains:

> **Development and production changes should be controlled and auditable.**

Developers should not rely on direct manual production notebook editing for normal releases.

---

# 38. Security Best Practices

Apply:

- no secrets in source code
- no secrets in Git
- no production credentials in notebooks
- least privilege
- service principals or equivalent automation identities for automation
- environment separation
- secure configuration
- dependency security
- reviewed access
- auditability

## Relationship to Unity Catalog

This topic establishes **development discipline**.

Topic 04 establishes deeper **data and platform governance**.

Do not confuse:

```text
Git access
```

with:

```text
data access
```

An engineer being able to read source code does not automatically imply they should be able to access production data.

---

# 39. Code Organization Decision Matrix

| Situation | Recommended Approach |
|---|---|
| Quick exploration | Notebook |
| Data investigation | Notebook |
| Reusable transformation | Python module |
| Production ETL logic | Python package/module |
| SQL transformation | SQL file |
| Workflow orchestration | Job/pipeline |
| Shared configuration | Config |
| Sensitive credentials | Secret manager |
| Documentation | Markdown |
| Version control | Git |
| Unit testing | pytest |
| CI/CD | Git-based workflow |

The decision should be based on the **responsibility and lifecycle** of the code.

---

# 40. Notebook vs Git Folder vs Workspace File

| Capability | Notebook | Git Folder | Workspace File |
|---|---|---|---|
| Interactive execution | Excellent | Depends on asset | No |
| Version control | Good | Excellent | Depends |
| Collaboration | Good | Excellent | Good |
| Reusable code | Limited | Excellent | Good |
| Documentation | Excellent | Excellent | Excellent |
| Production code | Limited | Preferred | Depends |

These are not mutually exclusive.

A Git project can contain notebooks. A workspace can contain Git-backed development assets. The engineering question is which system is the authoritative source and how changes are deployed.

---

# 41. Architecture Decision Records

## ADR-001 — Notebook-Centric vs Package-Centric Development

### Context

Early exploration is faster in notebooks, while reusable production logic needs stronger engineering controls.

### Problem

Where should business logic live?

### Options

1. Keep everything in notebooks.
2. Move all work immediately to Python packages.
3. Use notebooks for interaction and packages for reusable logic.

### Decision

Choose option 3.

### Reasons

It preserves interactive development while improving reuse and testability.

### Trade-Offs

More project structure and packaging work.

### Consequences

Production logic becomes easier to test and review.

---

## ADR-002 — `%run` vs Python Package

### Context

`%run` is convenient for notebook reuse.

### Problem

Long dependency chains become difficult to understand.

### Options

- `%run`
- copy/paste
- Python modules/packages

### Decision

Use `%run` only for controlled notebook-oriented cases; prefer explicit Python modules for reusable business logic.

### Reasons

Explicit imports improve dependency visibility and testing.

### Trade-Offs

Requires package structure.

### Consequences

Better maintainability.

---

## ADR-003 — Workspace Development vs Git-First Development

### Context

Workspace editing is convenient.

### Problem

Manual workspace changes can become difficult to review.

### Options

- workspace as source of truth
- Git as source of truth

### Decision

Use Git as the source of truth for production code.

### Reasons

History, review, collaboration, and controlled deployment.

### Trade-Offs

Requires Git workflow discipline.

### Consequences

Production changes become auditable.

---

## ADR-004 — Local Development vs Notebook-Only Development

### Context

Notebooks are excellent for interactive Spark work.

### Problem

Software-engineering tasks can be cumbersome in notebook-only workflows.

### Decision

Use a hybrid local + Databricks workflow.

### Reasons

Local tooling is strong for:

- tests
- formatting
- linting
- source organization

Databricks is strong for:

- Spark
- managed data
- realistic execution

### Consequences

The team gets both engineering rigor and interactive data-platform capability.

---

## ADR-005 — Widgets vs Python Function Arguments

### Context

Notebooks need runtime inputs.

### Decision

Use widgets/job parameters at execution boundaries and Python arguments inside reusable logic.

### Consequences

Business logic remains independent of notebook UI.

---

# 42. Interview Preparation

## Question 1 — What Is a Databricks Notebook?

### Strong Answer

A Databricks notebook is an interactive development surface containing executable cells, documentation, parameters, outputs, and visualizations that runs code against Databricks execution resources.

### Detailed Explanation

It is an interface for interactive development, not a replacement for project architecture.

### Weak Answer

"It is where you write Spark code."

### Follow-Up

When would you move logic out of a notebook?

### Senior Consideration

Discuss reuse, testing, Git, reviewability, configuration, and production deployment.

---

## Question 2 — What Is Notebook State?

### Strong Answer

Notebook state is the runtime state created by executed cells, such as variables, imports, temporary objects, and configuration. Hidden state can make a notebook depend on execution order.

### Weak Answer

"State is the data in the notebook."

### Follow-Up

How do you detect hidden state?

### Senior Consideration

Run from a clean environment and validate reproducibility.

---

## Question 3 — Why Can Notebook State Be Dangerous?

### Strong Answer

Because a notebook may succeed only after cells have been executed in a particular order, creating behavior that is not reproducible from a clean run.

### Follow-Up

How would you fix it?

### Senior Consideration

Make dependencies explicit and extract reusable logic.

---

## Question 4 — What Is `%run`?

### Strong Answer

`%run` allows one notebook to execute another notebook in supported Databricks environments. It is useful for controlled notebook composition but can create hidden dependency chains when overused.

### Follow-Up

When would you replace it?

### Senior Consideration

Use a Python module/package when logic needs reuse and testing.

---

## Question 5 — Why Are Long `%run` Chains Problematic?

### Strong Answer

They create transitive dependencies and hidden execution order, making debugging, testing, and code ownership harder.

### Follow-Up

What is the alternative?

### Senior Consideration

Explicit imports and package boundaries.

---

## Question 6 — What Are Widgets?

### Strong Answer

Widgets provide runtime inputs to notebooks. They are useful at the notebook execution boundary but should not tightly couple reusable business logic to the notebook UI.

### Follow-Up

Widgets vs function arguments?

### Senior Consideration

Widgets are interface parameters; function arguments are code-level dependencies.

---

## Question 7 — What Is `dbutils`?

### Strong Answer

`dbutils` provides Databricks runtime utilities, including supported file, secret, widget, and notebook/runtime utilities. Its exact API can evolve.

### Follow-Up

Should business logic be implemented entirely with `dbutils`?

### Senior Consideration

No. Keep platform utilities at the infrastructure boundary.

---

## Question 8 — How Should Secrets Be Handled?

### Strong Answer

Secrets should be stored and retrieved through an approved secret-management mechanism and never hardcoded into source code or committed to Git.

### Follow-Up

What if a secret reaches Git?

### Senior Consideration

Revoke/rotate it immediately, assess exposure, clean the repository according to policy, audit, and prevent recurrence.

---

## Question 9 — Why Use Git Folders?

### Strong Answer

Git folders connect Databricks development to repository-based version control, enabling branches, commits, review, collaboration, and controlled source history.

### Follow-Up

Why should Git be the source of truth?

### Senior Consideration

It separates source history from mutable interactive workspace state.

---

## Question 10 — Notebook vs Python Package?

### Strong Answer

Use notebooks for interactive exploration and controlled notebook workflows; use Python modules/packages for reusable, testable, reviewable production logic.

### Follow-Up

Does this mean notebooks are bad?

### Senior Consideration

No. They serve a different development responsibility.

---

## Question 11 — How Would You Structure a Databricks Project?

### Strong Answer

Separate reusable source code, notebooks, tests, SQL, configuration/deployment assets, and documentation. Keep source under Git and make environment-specific configuration external to business logic.

### Follow-Up

Where should tests live?

### Senior Consideration

Near the project, normally under a dedicated test hierarchy.

---

## Question 12 — What Is Databricks Connect?

### Strong Answer

Databricks Connect supports local development workflows that execute supported code against remote Databricks compute.

### Follow-Up

What can make it fail?

### Senior Consideration

Authentication, networking, version compatibility, remote compute, dependencies, and unsupported feature differences.

---

## Question 13 — How Do You Test DataFrame Logic?

### Strong Answer

Extract logic into functions, use deterministic test data, validate schemas and business behavior, and combine unit tests with integration tests where remote platform behavior matters.

### Follow-Up

Why extract the logic?

### Senior Consideration

It reduces dependence on notebook state.

---

## Question 14 — What Is Linting?

### Strong Answer

Linting is automated static analysis that detects code-quality problems such as unused imports, undefined variables, suspicious patterns, and style issues.

### Follow-Up

Why automate it?

### Senior Consideration

It reduces mechanical review effort.

---

## Question 15 — What Is Formatting?

### Strong Answer

Formatting applies consistent code presentation automatically, reducing style noise in code reviews.

### Follow-Up

Should formatting be manual?

### Senior Consideration

Prefer automated project-level formatting.

---

## Question 16 — How Do You Review a Production Data Engineering PR?

### Strong Answer

Review correctness, tests, data behavior, security, configuration, performance, operational impact, permissions, documentation, and maintainability.

### Follow-Up

What is a common notebook red flag?

### Senior Consideration

Hidden state, secrets, hardcoded environment values, large business logic blocks, and no tests.

---

## Question 17 — What Notebook Anti-Patterns Have You Seen?

### Strong Answer

Giant notebooks, hidden state, long `%run` chains, hardcoded paths/catalogs, secrets, duplicated logic, no tests, manual production editing, and environment-specific business logic.

### Follow-Up

How do you refactor them?

### Senior Consideration

Move reusable logic into packages, externalize configuration, add tests, adopt Git, and introduce controlled deployment.

---

# 43. Practice Questions

## Basic — 10 Questions

### Basic 1

What is a Databricks notebook?

**Answer:** An interactive development surface for executable cells, documentation, parameters, outputs, and visualizations.

### Basic 2

What is a code cell?

**Answer:** An executable notebook cell containing supported code such as Python or SQL.

### Basic 3

What is a Markdown cell used for?

**Answer:** Documentation, assumptions, explanations, and experiment notes.

### Basic 4

Why can notebook state be dangerous?

**Answer:** It can create hidden dependencies on execution order.

### Basic 5

What is `%run`?

**Answer:** A notebook magic used to execute another notebook in supported environments.

### Basic 6

What is a widget?

**Answer:** A runtime input mechanism for a notebook.

### Basic 7

What is `dbutils`?

**Answer:** A set of Databricks runtime utilities.

### Basic 8

Why should secrets not be hardcoded?

**Answer:** They can leak into source control, logs, outputs, or backups.

### Basic 9

Why use Git?

**Answer:** Version history, collaboration, branching, review, and controlled source management.

### Basic 10

When should business logic move out of a notebook?

**Answer:** When it becomes reusable, complex, important to test, or production-critical.

---

## Moderate — 10 Questions

### Moderate 1

Compare notebook parameters and Python function arguments.

**Answer:** Notebook parameters belong at the execution boundary; Python arguments belong inside reusable code.

### Moderate 2

Why are hardcoded catalog names problematic?

**Answer:** They bind business logic to one environment.

### Moderate 3

Why are long `%run` chains risky?

**Answer:** They create hidden dependency chains and make debugging difficult.

### Moderate 4

What belongs in `src/`?

**Answer:** Reusable application/data-engineering logic.

### Moderate 5

What belongs in `tests/`?

**Answer:** Automated unit and integration tests.

### Moderate 6

Why develop locally?

**Answer:** Better IDE, testing, linting, formatting, dependency management, and source organization.

### Moderate 7

What is Databricks Connect conceptually?

**Answer:** A bridge between local development and supported remote Databricks execution.

### Moderate 8

Why externalize environment configuration?

**Answer:** To deploy the same business logic safely across environments.

### Moderate 9

What should a production PR review?

**Answer:** Correctness, tests, security, performance, data behavior, configuration, and operational impact.

### Moderate 10

Why is a notebook not automatically production-ready?

**Answer:** Interactivity can hide state, dependencies, configuration, and lack of tests.

---

## Hard — 5 Questions

### Hard 1

A notebook works only after three cells are manually executed in a specific order. What do you investigate?

**Answer:** Hidden state and undocumented dependencies; reproduce from a clean state and identify the first missing dependency.

### Hard 2

A job uses the wrong production catalog. What is your likely design-level diagnosis?

**Answer:** Environment identity is probably hardcoded or incorrectly injected.

### Hard 3

A developer accidentally commits a database password. What is the correct first response?

**Answer:** Revoke/rotate the credential and assess exposure before treating repository cleanup as sufficient.

### Hard 4

A production notebook is 1,500 lines long. What is your refactoring strategy?

**Answer:** Separate orchestration from reusable logic, extract modules, add tests, externalize configuration, reduce `%run`, and put the project under controlled Git deployment.

### Hard 5

Local execution works but Databricks Connect fails. What investigation sequence should you use?

**Answer:**

```text
Authentication
→ Network
→ Version compatibility
→ Compute
→ Dependencies
→ Supported features
```

---

# 44. Knowledge Checkpoints

## Checkpoint — Notebook Foundations

```text
[ ] I understand notebooks.
[ ] I understand code cells.
[ ] I understand Markdown cells.
[ ] I understand notebook state.
[ ] I understand notebook magics.
[ ] I understand %run.
[ ] I understand widgets.
[ ] I understand visualizations.
```

## Checkpoint — Databricks Development

```text
[ ] I understand dbutils.
[ ] I understand workspace files.
[ ] I understand Git folders.
[ ] I understand Git-based development.
[ ] I understand project organization.
```

## Checkpoint — Python Engineering

```text
[ ] I can separate notebook logic from reusable code.
[ ] I understand modules.
[ ] I understand packages.
[ ] I can structure a Data Engineering project.
[ ] I can use Python arguments.
```

## Checkpoint — Configuration and Security

```text
[ ] I understand job parameters.
[ ] I understand widgets vs arguments.
[ ] I can avoid hardcoded paths.
[ ] I can avoid hardcoded catalogs.
[ ] I can manage secrets safely.
```

## Checkpoint — Local Development

```text
[ ] I understand local development.
[ ] I understand IDE workflows.
[ ] I understand Databricks Connect.
[ ] I understand dependency management.
```

## Checkpoint — Quality

```text
[ ] I understand unit testing.
[ ] I understand pytest.
[ ] I understand linting.
[ ] I understand formatting.
[ ] I understand code review.
```

## Checkpoint — Production

```text
[ ] I can identify notebook anti-patterns.
[ ] I can refactor notebook logic.
[ ] I can design a Git-first project.
[ ] I can design a production project structure.
[ ] I can troubleshoot development failures.
[ ] I can explain these practices in an interview.
```

---

# 45. Production Mental Models

Use these definitions:

```text
NOTEBOOK
= Interactive development environment

GIT FOLDER
= Version-controlled project workspace

PYTHON MODULE
= Reusable unit of business logic

PYTHON PACKAGE
= Structured collection of reusable modules

WIDGET
= Runtime input for notebook execution

JOB PARAMETER
= Workflow-level configuration

PYTHON ARGUMENT
= Function-level configuration

DBUTILS
= Databricks runtime utilities

SECRET
= Sensitive configuration that must not live in source code

LOCAL DEVELOPMENT
= Professional software-engineering workflow

DATABRICKS CONNECT
= Local development against supported remote Databricks compute

LINTING
= Automated code-quality checking

FORMATTING
= Consistent code presentation

TESTING
= Evidence that code behaves correctly

GIT
= Version history and collaboration system
```

The mental model to retain is:

```text
Interactive development
        ↓
Explicit dependencies
        ↓
Reusable code
        ↓
Version control
        ↓
Automated quality
        ↓
Review
        ↓
Controlled deployment
```

---

# 46. Final Capstone — Refactor a 1,500-Line Notebook

## Scenario

A Data Engineer has created a 1,500-line notebook that:

- contains all business logic
- uses `%run` several times
- hardcodes S3 paths
- hardcodes production catalog names
- contains a database password
- has no tests
- is manually edited in production
- cannot be run locally
- works only if cells are executed in a specific order

## Your Task

Redesign the solution.

Produce:

1. notebook strategy
2. Git strategy
3. project structure
4. Python package structure
5. configuration strategy
6. parameter strategy
7. secret strategy
8. testing strategy
9. linting/formatting strategy
10. local development workflow
11. Databricks Connect workflow
12. code-review process
13. production deployment model

## Model Solution

### 1. Notebook Strategy

Keep notebooks for:

- exploration
- debugging
- thin workflow interfaces
- controlled operational tasks

Move reusable business logic out.

### 2. Git Strategy

```text
main
 |
feature/refactor-orders
 |
tests
 |
pull request
 |
review
 |
merge
```

Git becomes the source of truth.

### 3. Project Structure

```text
orders-platform/
├── README.md
├── pyproject.toml
├── databricks.yml
├── src/orders/
├── notebooks/
├── tests/
├── sql/
├── docs/
└── resources/
```

### 4. Python Package

```text
orders/
├── config.py
├── ingestion.py
├── transformations.py
├── validation.py
└── publishing.py
```

### 5. Configuration

Externalize:

- environment
- catalogs
- schemas
- table names
- input/output configuration

### 6. Parameters

```text
Job parameter
   ↓
Notebook boundary
   ↓
Python function argument
```

### 7. Secrets

Use an approved secret-management mechanism.

Never:

```python
password = "..."
```

### 8. Testing

Add:

```text
tests/unit/
tests/integration/
```

Test transformation and validation behavior.

### 9. Quality

```text
Format
→ Lint
→ Unit test
→ Integration test
```

### 10. Local Development

Use:

```text
VS Code
Python
uv
Git
pytest
```

### 11. Databricks Connect

Use supported local-to-remote execution for realistic Spark validation.

### 12. Review

Review:

- correctness
- data behavior
- security
- tests
- configuration
- performance
- operational risk

### 13. Deployment

Move from:

```text
manual production notebook editing
```

to:

```text
Git
→ review
→ controlled deployment
→ production
```

---

# 47. Final Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Section | Practical Evidence |
|---|---|---|---|
| Notebooks | COMPLETE | 2 | Notebook architecture and use cases |
| Notebook cells | COMPLETE | 3 | Code/Markdown cell guidance |
| Markdown cells | COMPLETE | 3 | Documentation examples |
| Notebook magics | COMPLETE | 6 | `%python`, `%sql`, `%md`, `%run`, `%sh` |
| Widgets | COMPLETE | 8 | Widget parameterization |
| Visualizations | COMPLETE | 10 | `display()` and validation |
| Git folders | COMPLETE | 14 | Git-first workflow |
| Workspace files | COMPLETE | 13 | Workspace file comparison |
| Python project structure | COMPLETE | 15, 35 | Production structures |
| `dbutils` | COMPLETE | 11 | File, widget, secret concepts |
| Secrets | COMPLETE | 12 | Secure retrieval and incident response |
| Local development | COMPLETE | 19, 20 | IDE and hybrid workflow |
| IDE integration | COMPLETE | 19 | VS Code/IDE workflow |
| Databricks Connect | COMPLETE | 21 | Local-to-remote model and troubleshooting |
| Job parameters | COMPLETE | 9, 22 | Parameter hierarchy |
| Python arguments | COMPLETE | 9, 22 | Reusable function interfaces |
| Code review | COMPLETE | 30 | PR checklist |
| Linting | COMPLETE | 27 | Static analysis |
| Formatting | COMPLETE | 28 | Automated formatting |
| Notebook anti-patterns | COMPLETE | 31 | Detailed anti-pattern catalog |
| `%run` chains | COMPLETE | 7, 31 | Risks and migration |
| Hardcoded paths | COMPLETE | 24 | Failure modes and alternatives |
| Hardcoded catalogs | COMPLETE | 25 | Environment-aware configuration |
| Secrets in notebooks | COMPLETE | 12, 31 | Security and remediation |
| Production project structure | COMPLETE | 35 | Full project tree |
| Hands-on labs | COMPLETE | 33 | 10 labs |
| Troubleshooting | COMPLETE | 34 | 7 break/fix incidents |
| Interview preparation | COMPLETE | 42 | 17 interview questions |
| Practice questions | COMPLETE | 43 | 25 questions |
| Knowledge checkpoints | COMPLETE | 44 | Section-level checklists |
| Production refactoring | COMPLETE | 32, 46 | Refactoring lab and capstone |
| ADRs | COMPLETE | 41 | 5 ADRs |
| Final capstone | COMPLETE | 46 | 1,500-line notebook redesign |
| Completion checklist | COMPLETE | 44 | Topic checkpoints |
| Version-sensitive safety | COMPLETE | Throughout | Current-documentation notes |

**Coverage conclusion:** All authoritative Topic 03 requirements are meaningfully addressed in this learning file.

---

# 48. Completion Checklist

## Notebook Foundations

```text
[ ] I understand notebooks.
[ ] I understand code cells.
[ ] I understand Markdown cells.
[ ] I understand notebook state.
[ ] I understand notebook magics.
[ ] I understand %run.
[ ] I understand widgets.
[ ] I understand visualizations.
```

## Databricks Development

```text
[ ] I understand dbutils.
[ ] I understand workspace files.
[ ] I understand Git folders.
[ ] I understand Git-based development.
[ ] I understand project organization.
```

## Python Engineering

```text
[ ] I can separate notebook logic from reusable code.
[ ] I understand modules.
[ ] I understand packages.
[ ] I can structure a Data Engineering project.
[ ] I can use Python arguments.
```

## Configuration and Security

```text
[ ] I understand job parameters.
[ ] I understand widgets vs arguments.
[ ] I can avoid hardcoded paths.
[ ] I can avoid hardcoded catalogs.
[ ] I can manage secrets safely.
```

## Local Development

```text
[ ] I understand local development.
[ ] I understand IDE workflows.
[ ] I understand Databricks Connect.
[ ] I understand dependency management.
```

## Quality

```text
[ ] I understand unit testing.
[ ] I understand pytest.
[ ] I understand linting.
[ ] I understand formatting.
[ ] I understand code review.
```

## Production

```text
[ ] I can identify notebook anti-patterns.
[ ] I can refactor notebook logic.
[ ] I can design a Git-first project.
[ ] I can design a production project structure.
[ ] I can troubleshoot development failures.
[ ] I can explain these practices in an interview.
```

---

# 49. Current-Documentation Safety

Databricks terminology and development tooling can change.

Verify current official documentation for:

- Git folders terminology
- workspace files
- notebook capabilities
- `%run`
- `dbutils`
- secret APIs
- Databricks Connect
- IDE extensions
- authentication
- CLI commands
- current project/deployment tooling

Do not invent:

- CLI commands
- API endpoints
- Databricks Connect setup commands
- secret-scope behavior
- workspace-file capabilities
- Git functionality
- product limitations

When exact behavior cannot be confidently established, label an example as **conceptual/illustrative** and verify the current documentation before production use.

---

# 50. Final Operating Standard

A production Databricks engineer should be able to reason through:

```text
Notebook
   ↓
Execution State
   ↓
Parameters
   ↓
Configuration
   ↓
Reusable Python
   ↓
Git
   ↓
Tests
   ↓
Lint / Format
   ↓
Code Review
   ↓
Databricks Validation
   ↓
Controlled Deployment
   ↓
Production
```

The central rule is:

> **Notebooks are a powerful development interface, but production Data Engineering is a software-engineering discipline built around explicit dependencies, reusable code, version control, testing, secure configuration, review, and controlled deployment.**

## Final Quality Standard

This module is complete only when the learner can:

- explain notebook behavior
- diagnose notebook-state problems
- use notebook features appropriately
- parameterize notebooks
- use `dbutils` appropriately
- protect secrets
- work with Git folders
- organize a Python project
- separate notebooks from reusable logic
- develop locally
- use Databricks Connect where supported
- test DataFrame logic
- lint and format code
- review Data Engineering changes
- identify notebook anti-patterns
- refactor a notebook into a production-oriented project
- explain the design in a senior-level interview

---

# Final Validation

```text
Target file:
04-Databricks-Lakehouse-Platform-Deep-Dive/03-notebooks-git-folders-and-project-structure.md

Other files modified:
NONE

Roadmap coverage:
COMPLETE

Learning progression:
BASIC → INTERMEDIATE → ADVANCED → PRODUCTION

Notebook coverage:
COMPLETE

Git / Project Structure:
COMPLETE

Python Engineering:
COMPLETE

Local Development:
COMPLETE

Databricks Connect:
COMPLETE

Security / Secrets:
COMPLETE

Testing / Linting / Formatting:
COMPLETE

Troubleshooting:
INCLUDED

Hands-on labs:
INCLUDED

Production refactoring:
INCLUDED

Interview preparation:
INCLUDED

Final roadmap audit:
COMPLETED
```

> **Production rule:** Before using any version-sensitive Databricks syntax, authentication flow, Git integration, workspace-file behavior, `dbutils` API, or Databricks Connect command in a real environment, verify the current official Databricks documentation for the deployed runtime and product edition.
