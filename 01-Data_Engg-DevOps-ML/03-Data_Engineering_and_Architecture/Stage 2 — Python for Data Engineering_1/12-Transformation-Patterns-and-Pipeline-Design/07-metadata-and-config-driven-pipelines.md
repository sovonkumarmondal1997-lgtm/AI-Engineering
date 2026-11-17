# Metadata and Config-Driven Pipelines

> **Module 2.12 — Transformation Patterns and Pipeline Design**
>
> This chapter teaches the transition from individually hard-coded pipelines to
> metadata-driven and configuration-driven systems that can safely operate
> hundreds of similar datasets without duplicating business logic.

The central progression is:

```text
Hard-Coded Pipeline
        ↓
Configuration
        ↓
Metadata
        ↓
Schema Validation
        ↓
Generic Execution Engine
        ↓
Strategies / Registry
        ↓
Plugins
        ↓
Templated SQL
        ↓
Environment Configuration
        ↓
Operational Metadata
        ↓
Testing
        ↓
Production Platform Design
```

The core principle is:

> **Configuration describes controlled variation; code implements reusable behavior; metadata describes the data and operational context around both.**

A configuration-driven system is valuable only when it reduces duplication and improves consistency without turning configuration into an opaque programming language.

## 1. Learning Objectives

By the end of this chapter you should be able to:

- explain why hard-coded pipelines become difficult to operate at scale;
- distinguish **code**, **configuration**, and **metadata**;
- design dataset definitions in YAML;
- validate configuration before execution with Pydantic;
- build nested `DatasetConfig` models with required fields, optional fields, defaults, and cross-field validation;
- design a generic execution engine that separates validation, planning, and execution;
- represent append, partition-overwrite, merge, and full-refresh strategies safely;
- represent partitioning, quality rules, owners, SLAs, and dependencies as controlled metadata;
- use a registry/strategy pattern instead of a giant conditional tree;
- design plugins and custom-step escape hatches;
- generate repetitive SQL with Jinja without treating templating as a SQL-safety mechanism;
- distinguish SQL identifiers from SQL values;
- use allowlists, quoting, and parameterization appropriately;
- design development/staging/production environment overlays;
- keep credentials and secrets outside ordinary dataset configuration;
- compare runtime interpretation with code generation;
- design a metadata catalog containing ownership, dependencies, lineage, SLAs, and operational state;
- build dry-run execution plans;
- create golden tests for plans and rendered SQL;
- detect configuration drift;
- recognize when configuration has become a programming language;
- avoid excessive flags and the internal-platform trap;
- design production metadata-driven architecture;
- debug configuration and engine failures;
- reason about framework boundaries like a senior Data Engineer.

---


## 2. Prerequisites

This chapter assumes you already understand the earlier Module 2.12 topics:

- deterministic transformations;
- idempotent loads;
- deduplication and merge-based loading;
- incremental processing;
- backfills;
- late-arriving data and reprocessing windows;
- deterministic hashing;
- lookup and enrichment patterns;
- Python data processing;
- SQL and relational joins;
- basic data-quality validation.

The dependency chain is:

```text
01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09
```

Topic 07 does not replace the earlier transformation patterns. It **packages reusable implementations of those patterns behind validated dataset-specific configuration**.

A useful mental transition is:

```text
Earlier topics:
"How do I build one correct pipeline?"

This topic:
"How do I build one correct engine that can safely run hundreds of similar pipelines?"

---


## 3. The Problem with Hard-Coded Pipelines

Start with three individually coded pipelines:

```python
def run_orders():
    source = "bronze.orders"
    target = "silver.orders"
    # read
    # standardize
    # validate
    # deduplicate
    # merge


def run_customers():
    source = "bronze.customers"
    target = "silver.customers"
    # read
    # standardize
    # validate
    # deduplicate
    # merge


def run_products():
    source = "bronze.products"
    target = "silver.products"
    # read
    # standardize
    # validate
    # deduplicate
    # merge
```

The code is manageable at three datasets.

At 10 datasets, duplication becomes noticeable.

At 50 datasets, a bug fix may need to be applied repeatedly.

At 300 datasets, the organization is effectively maintaining a private copy of the same pipeline logic hundreds of times.

At 1,000 datasets, the operational problem becomes larger than the transformation problem.

### Typical failure modes

**Duplicated behavior**

The same deduplication logic exists in many files.

**Inconsistent fixes**

One pipeline receives a bug fix while another remains on the old behavior.

**Testing explosion**

Every copied implementation needs separate regression coverage.

**Onboarding cost**

A new dataset requires another implementation instead of a controlled definition.

**Operational inconsistency**

Different pipelines report different metadata, quality results, and failure states.

**Configuration hidden in code**

Dataset-specific values become constants scattered throughout Python modules.

### The goal

The goal is not:

> "Never write another pipeline."

The goal is:

> **Move repeated behavior into well-tested reusable code and move controlled dataset variation into validated configuration.**

A first configuration might be:

```yaml
name: orders
source: bronze.orders
target: silver.orders
load_strategy: merge
```

Now the engine can interpret the definition instead of requiring another copy of the implementation.

---


## 4. What Is Configuration-Driven Design?

Configuration-driven design means the engine contains reusable behavior while configuration describes controlled variation.

Conceptually:

```text
                    ┌─────────────────────┐
                    │ Generic Pipeline    │
                    │       Engine        │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
         orders.yaml     customers.yaml   products.yaml
```

The engine knows **how** to:

- validate;
- plan;
- read;
- transform;
- deduplicate;
- enrich;
- load;
- test;
- record operational metadata.

The configuration says **which**:

- source;
- target;
- keys;
- strategy;
- partition;
- quality rules;
- owner;
- schedule;
- dependencies;
- controlled transformation options.

### Benefits

| Benefit | Meaning |
|---|---|
| Consistency | Common behavior is implemented once |
| Scalability | New datasets can often be onboarded through configuration |
| Reuse | Tested strategies serve many datasets |
| Centralized fixes | Engine fixes can benefit many datasets |
| Faster onboarding | Dataset-specific variation becomes explicit |
| Better governance | Configuration can be reviewed and versioned |

### Risks

Configuration-driven design introduces its own complexity:

- configuration can become too large;
- behavior can become hidden inside flags;
- invalid configuration can fail late;
- inheritance can become confusing;
- debugging can require understanding both config and engine;
- a generic engine can become an inner platform that nobody understands.

Therefore:

> **The abstraction must remain simpler than the repeated problems it solves.**

---


## 5. What Is Metadata?

Metadata is **data about data and data-processing operations**.

Examples:

```text
dataset name
source
target
schema
owner
partition column
load strategy
schedule
SLA
quality rules
dependencies
last successful run
status
logic version
```

### Technical metadata

Describes the physical or structural properties of data:

- column names;
- types;
- schema version;
- partitioning;
- source;
- target;
- storage format.

### Operational metadata

Describes how a dataset is operated:

- owner;
- schedule;
- SLA;
- status;
- last successful run;
- current run;
- row count;
- logic version.

### Business metadata

Describes meaning:

- business domain;
- criticality;
- business definition;
- sensitivity classification.

### Lineage metadata

Describes dependencies:

- upstream datasets;
- downstream datasets;
- transformation relationships;
- source systems.

Metadata becomes valuable when it is machine-readable enough to support:

- planning;
- orchestration;
- lineage;
- impact analysis;
- ownership;
- quality;
- observability;
- incident response.

A critical distinction:

> **Configuration can control execution; metadata describes the system and its data. The boundary can overlap, but the concepts should remain understandable.**

---


## 6. Configuration vs Metadata

A practical distinction is:

| Configuration | Metadata |
|---|---|
| Controls execution | Describes the data/system |
| Load strategy | Owner |
| Partition strategy | Schema |
| Batch parameters | Lineage |
| Transformation parameters | Business domain |
| Quality thresholds | Historical status |
| Runtime options | Last successful run |

For example:

```yaml
name: orders
load_strategy: merge
keys:
  - order_id
partition:
  column: order_date
  strategy: daily
```

This is execution configuration.

Operational metadata might look like:

```yaml
dataset: orders
owner: orders-team
last_successful_run: 2026-10-02T18:10:00Z
status: healthy
row_count: 1284300
logic_version: transform-v7
```

Do not create an artificial taxonomy just for its own sake. The useful question is:

> What information is needed to make the pipeline understandable, controllable, testable, and operable?

---


## 7. Code vs Configuration

A durable design separates stable behavior from controlled variation.

### Code

```python
def load_dataset(config, context):
    plan = build_plan(config, context)
    return execute(plan)
```

### Configuration

```yaml
name: orders
source: bronze.orders
target: silver.orders

load_strategy: merge

keys:
  - order_id

partition:
  column: order_date
  strategy: daily
```

The rule is:

> **Code defines HOW the system behaves. Configuration defines WHICH supported behavior applies to this dataset.**

### What should usually stay in code?

- algorithms;
- complex business logic;
- error-handling mechanics;
- retry behavior;
- transaction semantics;
- security controls;
- reusable transformations;
- execution strategies.

### What can often be configuration?

- dataset name;
- source and target;
- supported load strategy;
- keys;
- partition column;
- quality thresholds;
- owner;
- schedule;
- dependency declarations;
- selected registered transformations.

### A warning

Do not put arbitrary Python expressions into YAML:

```yaml
transform: "eval(row['amount'] * complex_business_rule())"
```

That moves the programming language into configuration while losing the normal benefits of code review, typing, tooling, testing, and debugging.

---


## 8. Designing a Dataset Configuration

Start with the smallest useful contract:

```yaml
dataset:
  name: orders
  owner: data-platform
  source: bronze.orders
  target: silver.orders

  keys:
    - order_id

  load_strategy: merge

  partition:
    column: order_date
    strategy: daily

  quality:
    required_columns:
      - order_id
      - order_date
      - customer_id
```

Each field has a purpose.

| Field | Purpose |
|---|---|
| `name` | Stable dataset identity |
| `owner` | Operational accountability |
| `source` | Input relation |
| `target` | Output relation |
| `keys` | Dataset grain / merge identity |
| `load_strategy` | Controlled loading behavior |
| `partition` | Incremental processing semantics |
| `quality` | Declarative quality checks |

A good schema is deliberately boring. If every dataset requires ten pages of configuration to express simple behavior, the framework is probably over-generalized.

### Design sequence

1. List datasets.
2. Identify what is identical.
3. Identify what genuinely varies.
4. Define only the meaningful variation.
5. Validate the configuration schema.
6. Implement the engine around the schema.

---


## 9. YAML Configuration

YAML is useful because it is readable and naturally represents nested configuration.

### Mapping

```yaml
name: orders
load_strategy: merge
```

### List

```yaml
keys:
  - order_id
  - source_system
```

### Nested mapping

```yaml
partition:
  column: order_date
  strategy: daily
```

### Boolean

```yaml
enabled: true
```

### Null

```yaml
description: null
```

### Common mistakes

#### Indentation

YAML is indentation-sensitive.

#### Wrong types

A value intended to be an integer can accidentally become a string depending on how it is represented and parsed.

#### Duplicate keys

Duplicate mapping keys can be confusing and should be detected by your chosen parser/tooling where possible.

#### Missing fields

A valid YAML document is not necessarily a valid dataset configuration.

#### Accidental strings

For example:

```yaml
enabled: "false"
```

The semantic type is now different from:

```yaml
enabled: false
```

Do not turn this into a general YAML course. The goal is to use YAML as a clear, version-controlled configuration representation.

---


## 10. Configuration Schema Validation with Pydantic

Raw YAML only answers:

> Can I parse this document?

It does not answer:

> Is this a valid dataset configuration?

Suppose the configuration contains:

```yaml
name: orders
load_strategy: mergee
```

A typo such as `mergee` should fail before the pipeline begins.

Pydantic provides a typed validation layer.

```python
from typing import Literal

from pydantic import BaseModel


class DatasetConfig(BaseModel):
    name: str
    source: str
    target: str
    load_strategy: Literal[
        "append",
        "overwrite_partition",
        "merge",
        "full_refresh",
    ]
```

Now an unsupported strategy is rejected during validation.

### Why validate early?

Early validation prevents:

- destructive operations;
- confusing runtime errors;
- invalid execution plans;
- accidental production changes;
- partial work before discovering configuration errors.

The desired sequence is:

```text
Load YAML
   ↓
Parse
   ↓
Validate with Pydantic
   ↓
Build plan
   ↓
Execute
```

not:

```text
Load YAML
   ↓
Start writing data
   ↓
Discover invalid configuration
```

Pydantic should be the first safety boundary, not the only one.

---


## 11. DatasetConfig Model

A realistic model should use nested models instead of one giant untyped dictionary.

```python
from typing import Literal

from pydantic import BaseModel, Field


class PartitionConfig(BaseModel):
    column: str
    strategy: Literal["daily", "hourly", "monthly"]


class QualityConfig(BaseModel):
    required_columns: list[str] = Field(default_factory=list)
    not_null: list[str] = Field(default_factory=list)
    unique: list[str] = Field(default_factory=list)


class DatasetConfig(BaseModel):
    name: str
    source: str
    target: str

    keys: list[str] = Field(default_factory=list)

    load_strategy: Literal[
        "append",
        "overwrite_partition",
        "merge",
        "full_refresh",
    ]

    partition: PartitionConfig | None = None
    quality: QualityConfig = Field(default_factory=QualityConfig)

    owner: str | None = None
    schedule: str | None = None
    sla_minutes: int | None = None
    dependencies: list[str] = Field(default_factory=list)
```

This gives the engine a predictable object rather than arbitrary nested dictionaries.

### Why nested models?

They provide:

- clear boundaries;
- readable validation errors;
- reusable schemas;
- explicit optionality;
- type information;
- easier testing;
- better IDE support.

Configuration models should evolve like APIs: deliberately and compatibly.

---


## 12. Required vs Optional Configuration

Not every field should be mandatory.

A reasonable starting point:

### Required

```text
name
source
target
load_strategy
```

### Conditionally required

```text
keys
partition.column
```

For example:

- `merge` requires keys;
- `overwrite_partition` requires partition metadata.

### Optional

```text
owner
schedule
description
dependencies
quality
```

Optional does not mean meaningless. It means the engine can operate safely without the field.

### Dangerous defaults

Avoid:

```python
load_strategy = "full_refresh"
```

as a universal default.

If an operator forgets to specify a strategy, silently choosing a destructive operation is unacceptable.

A safer approach is:

- make dangerous choices explicit;
- use conservative defaults;
- reject ambiguous configurations.

The general rule is:

> **Defaults should reduce accidental damage, not merely reduce typing.**

---


## 13. Defaults and Validation Rules

Validation should encode relationships between fields.

Examples:

- `merge` requires at least one key;
- `overwrite_partition` requires a partition definition;
- partition strategy must be supported;
- dataset names must match an allowlisted naming pattern;
- source and target cannot be empty;
- SLA values must be positive;
- quality thresholds must be within valid ranges.

A conceptual Pydantic validator:

```python
from pydantic import BaseModel, model_validator


class DatasetConfig(BaseModel):
    name: str
    source: str
    target: str
    keys: list[str] = []
    load_strategy: str
    partition: dict | None = None

    @model_validator(mode="after")
    def validate_strategy_requirements(self):
        if self.load_strategy == "merge" and not self.keys:
            raise ValueError("merge requires at least one key")

        if (
            self.load_strategy == "overwrite_partition"
            and self.partition is None
        ):
            raise ValueError(
                "overwrite_partition requires partition configuration"
            )

        return self
```

The important design idea is:

> **Validate semantic relationships before execution, not merely field types.**

For larger systems, keep the validation model readable. If validation itself becomes a second programming language, reconsider the schema.

---


## 14. Generic Pipeline Engines

A generic engine separates validation, planning, and execution.

```python
def run_dataset(config, context):
    validated = validate_config(config)
    plan = build_plan(validated, context)
    return execute(plan, context)
```

Conceptually:

```text
Configuration
     ↓
Validation
     ↓
Planning
     ↓
Execution
```

### Why planning matters

A plan can be inspected without touching data.

It can answer:

```text
What source will be read?
What target will be written?
Which partition will be processed?
Which strategy will run?
Which quality checks will execute?
Which dependencies are required?
Which plugins are selected?
```

This enables:

- dry runs;
- better logging;
- easier testing;
- safer production review;
- deterministic execution plans.

A generic engine should not hide its decisions.

---


## 15. Building a Metadata-Driven Execution Engine

A minimal engine can process multiple validated configurations:

```python
for raw_config in configs:
    config = DatasetConfig.model_validate(raw_config)
    plan = build_plan(config, context)
    execute(plan, context)
```

The scaling effect is:

```text
1 engine
+
100 configurations
=
100 datasets
```

But only when those datasets share sufficiently similar execution patterns.

The engine should not attempt to make fundamentally different workflows look identical.

### Planning object

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionPlan:
    dataset: str
    source: str
    target: str
    strategy: str
    keys: tuple[str, ...]
    partition: str | None
    quality_checks: tuple[str, ...]
    dependencies: tuple[str, ...]
```

The plan should be immutable once created. That makes it easier to:

- snapshot;
- compare;
- log;
- test;
- hash;
- review.

A production engine should make the plan a first-class artifact.

---


## 16. Load Strategies in Configuration

The engine can expose controlled strategies:

```yaml
load_strategy: append
```

```yaml
load_strategy: overwrite_partition
```

```yaml
load_strategy: merge
```

```yaml
load_strategy: full_refresh
```

The implementation should dispatch to tested strategy functions.

A basic implementation:

```python
LOAD_STRATEGIES = {
    "append": append_load,
    "merge": merge_load,
    "overwrite_partition": overwrite_partition,
    "full_refresh": full_refresh_load,
}


def execute_load(config, source, target):
    handler = LOAD_STRATEGIES[config.load_strategy]
    return handler(
        source=source,
        target=target,
        keys=config.keys,
    )
```

A registry is cleaner than an ever-growing `if/elif` tree.

### Important safety rule

The configuration can select a supported strategy.

It should not define arbitrary executable behavior.

Bad:

```yaml
load_function: "python://some.module:arbitrary_function"
```

unless your platform has a carefully controlled plugin system, trust boundary, versioning, and review process.

The configuration layer should select from known capabilities.

---


## 17. Partitioning Metadata

Partition metadata connects configuration-driven execution to incremental processing and backfills.

```yaml
partition:
  column: order_date
  strategy: daily
```

The engine can derive:

```text
dataset = orders
partition column = order_date
granularity = daily
requested date = 2026-10-02
```

and build the appropriate plan.

Partition metadata can support:

- incremental processing;
- partition overwrite;
- backfills;
- dry-run previews;
- cost estimation;
- affected-partition calculation.

Example:

```yaml
partition:
  column: event_date
  strategy: daily
  timezone: UTC
```

The timezone becomes important when a timestamp is converted to a business-date partition.

### Backfill configuration

A safe design keeps the dataset definition separate from the requested execution interval.

```text
Dataset configuration
        +
Run request
        ↓
Execution plan
```

For example:

```text
Dataset:
orders

Run:
2026-01-01 through 2026-01-31
```

This avoids encoding every possible historical run into configuration.

---


## 18. Quality Rules in Metadata

Quality checks can be represented declaratively when they are simple and standardized.

```yaml
quality:
  required_columns:
    - order_id
    - order_date

  not_null:
    - order_id
    - order_date

  unique:
    - order_id
```

The engine can translate these into known validation operations.

### Three categories

**Structural rules**

Examples:

- column exists;
- expected type;
- schema version.

**Data-quality rules**

Examples:

- not null;
- unique;
- range;
- allowed values.

**Business rules**

Examples:

```text
refund_amount <= order_amount
```

or:

```text
customer_status changes must follow domain-specific logic
```

Simple business constraints may be representable as a controlled rule type. Complex business behavior should generally remain code.

The key question is:

> Can this rule be represented clearly, safely, tested independently, and understood by operators?

If not, configuration may be the wrong abstraction.

---


## 19. Ownership and Operational Metadata

Operational metadata turns configuration into something useful to the people who run the platform.

```yaml
owner: orders-team
criticality: high
sla_minutes: 60
schedule: "0 * * * *"
```

This can support:

- alert routing;
- SLA monitoring;
- escalation;
- ownership dashboards;
- incident response;
- prioritization.

A useful operational record might contain:

```text
dataset
owner
run_id
status
started_at
completed_at
row_count
logic_version
configuration_version
```

Do not confuse this mutable runtime state with the desired configuration.

A useful separation is:

```text
Version-controlled configuration
        +
Mutable operational state
```

Configuration says what should happen.

Operational state says what happened.

---


## 20. Registry and Plugin Patterns

A registry maps a stable configuration name to a trusted implementation.

### Strategy registry

```python
LOAD_STRATEGIES = {
    "append": append_load,
    "merge": merge_load,
    "overwrite_partition": overwrite_partition,
}
```

Then:

```python
handler = LOAD_STRATEGIES[config.load_strategy]
result = handler(...)
```

### Transformation registry

```python
TRANSFORMS = {
    "standardize_orders": standardize_orders,
    "standardize_customers": standardize_customers,
}
```

This enables configuration such as:

```yaml
transformations:
  - standardize_orders
```

### Why registries help

They provide:

- explicit supported capabilities;
- centralized registration;
- easier testing;
- clear failure for unknown names;
- fewer giant conditional statements.

### Plugin pattern

A plugin can implement a capability that the common engine does not need to understand internally.

For example:

```text
Generic Engine
      ↓
Plugin Interface
      ↓
Customer Identity Resolution Plugin
```

Plugins should have:

- defined interface;
- versioning;
- tests;
- ownership;
- controlled loading;
- clear failure behavior.

Plugin systems become dangerous when every dataset creates a new plugin. At that point the framework may have failed to identify the true common pattern.

---


## 21. Jinja SQL Templating

Jinja can generate repetitive SQL from a template.

Example:

```sql
SELECT
    order_id,
    customer_id,
    amount
FROM {{ source_table }}
WHERE order_date = {{ partition_value }}
```

A template contains placeholders that are rendered into SQL.

This is useful for:

- repeated staging queries;
- standardized column projections;
- dataset-specific table names;
- repeated filter patterns;
- generated SQL for many similar datasets.

However:

> **Jinja is a text templating engine. It does not automatically make SQL safe.**

The engine must distinguish:

```text
identifier
```

from:

```text
value
```

and apply the appropriate safety mechanism to each.

Do not treat arbitrary user-controlled strings as safe template input.

---


## 22. Safe SQL Generation

SQL safety is especially important in metadata-driven systems because one template may generate SQL for hundreds of datasets.

### Values

Values should generally be parameterized by the database interface where supported.

Conceptually:

```python
cursor.execute(
    "SELECT * FROM orders WHERE order_date = %s",
    (partition_date,),
)
```

### Identifiers

Table names and column names usually cannot be bound as ordinary values. They require validation and safe quoting.

Bad:

```python
sql = f"SELECT * FROM {config.source}"
```

If `config.source` is not trusted and validated, it can create invalid or unsafe SQL.

Better:

```text
Configuration
    ↓
Validate identifier
    ↓
Check allowlist / naming rules
    ↓
Quote identifier
    ↓
Render SQL
```

The important lesson is:

> **Template safety is an application responsibility.**

---


## 23. Identifier Quoting and Allowlists

A simple allowlist might be:

```python
ALLOWED_TABLES = {
    "bronze.orders",
    "bronze.customers",
    "bronze.products",
}


def validate_table_name(name: str) -> str:
    if name not in ALLOWED_TABLES:
        raise ValueError(f"Unsupported table: {name}")
    return name
```

The allowlist can be generated from trusted catalog metadata in a larger system.

### Why quote identifiers?

A valid identifier may contain characters requiring database-specific quoting.

The quoting mechanism should come from the database driver or SQL abstraction rather than ad hoc string manipulation.

### Never confuse these

```text
Parameterized value
```

is not the same thing as:

```text
Validated identifier
```

For example:

```sql
WHERE order_date = ?
```

can parameterize the date value.

But:

```sql
FROM ?
```

usually cannot be used to bind a table name.

The safe architecture therefore validates identifiers separately.

---


## 24. Environment Overlays

The same logical dataset may run in:

```text
development
staging
production
```

The dataset's core definition should be shared where possible.

Base configuration:

```yaml
dataset:
  name: orders
  source: bronze.orders
  target: silver.orders
```

Environment-specific configuration might select a database, schema, compute profile, or operational setting.

Conceptually:

```text
Base configuration
        +
Environment overlay
        ↓
Resolved configuration
```

### Overlay risks

Inheritance can become confusing:

```text
base
 ↓
development
 ↓
staging
 ↓
production
 ↓
emergency override
```

Operators may no longer know which value wins.

Therefore:

- document precedence;
- keep overlays shallow;
- print resolved configuration in dry runs;
- avoid hidden environment magic;
- test every production overlay.

A good dry run should show the resolved non-secret configuration.

---


## 25. Secrets Outside Configuration

Never put credentials directly into ordinary dataset configuration.

Bad:

```yaml
password: super-secret
api_key: abc123
```

Problems include:

- accidental Git commits;
- broad access;
- difficult rotation;
- poor auditability;
- credential leakage in logs.

Instead:

```text
Dataset Configuration
        +
Environment / Secret Manager
        ↓
Runtime credential resolution
```

Examples of secret categories:

- database password;
- cloud credential;
- API token;
- private key.

The configuration can reference a secret by logical name:

```yaml
database:
  credential_ref: production/orders-db
```

The secret value is resolved at runtime through an appropriate secret-management mechanism.

### Operational rules

- never print secret values;
- avoid putting secrets in execution plans;
- rotate independently from dataset configuration;
- restrict access;
- audit retrieval;
- make development credentials distinct from production credentials.

---


## 26. Code Generation vs Runtime Interpretation

There are two broad approaches.

### Runtime interpretation

```text
configuration
    ↓
engine
    ↓
execution
```

The engine reads configuration when the pipeline runs.

Advantages:

- dynamic;
- centralized behavior;
- simpler artifact lifecycle;
- configuration can change without regenerating code.

Risks:

- runtime behavior depends on engine version;
- debugging may require understanding resolution logic;
- generated SQL may be less visible before execution.

### Code generation

```text
configuration
    ↓
generate Python/SQL
    ↓
review generated artifact
    ↓
execute
```

Advantages:

- generated artifacts can be inspected;
- some systems integrate naturally with generated SQL/code;
- generated code can become a reviewable build artifact.

Risks:

- generated artifacts require lifecycle management;
- regeneration can create noisy diffs;
- generated code can be harder to debug;
- source configuration and generated output can drift.

### Decision rule

Prefer runtime interpretation when:

- the engine is stable;
- the execution model is straightforward;
- configuration itself is the desired source of truth.

Prefer generation when:

- the generated artifact has an independent operational value;
- downstream tooling expects source-like artifacts;
- reviewability of generated SQL/code is important.

The choice is architectural, not ideological.

---


## 27. Metadata Catalogs

A metadata catalog can contain:

```text
dataset
owner
source
target
schema
dependencies
SLA
last successful run
current status
quality status
logic version
configuration version
```

The catalog supports:

### Discovery

"What datasets exist?"

### Ownership

"Who owns orders?"

### Operations

"Which datasets are failing?"

### Governance

"Which datasets are sensitive?"

### Lineage

"What depends on this table?"

### Debugging

"What configuration and logic version produced this output?"

A metadata catalog becomes increasingly valuable as dataset count grows.

---


## 28. Dependencies and Lineage Metadata

Configuration can declare dependencies:

```yaml
dependencies:
  - bronze.orders
  - silver.customers
```

The engine or orchestration layer can use this to construct a DAG.

```text
bronze.orders
      ↓
silver.orders
      ↓
gold.daily_revenue
```

Dependency metadata can support:

- execution ordering;
- impact analysis;
- backfills;
- lineage;
- change review;
- failure propagation.

### Important boundary

A transformation engine can describe dependencies.

An orchestration system usually decides **when** and **under what operational conditions** those dependencies execute.

This leads naturally into Module 2.13.

Do not make the metadata-driven transformation engine secretly become the entire orchestrator.

---


## 29. Dry-Run Execution Plans

A dry run answers:

> What would this pipeline do if I executed it?

The flow is:

```text
Configuration
      ↓
Validate
      ↓
Resolve environment
      ↓
Build execution plan
      ↓
Print / inspect plan
      ↓
NO WRITE
```

Example output:

```text
Dataset: orders
Source: bronze.orders
Target: silver.orders
Strategy: merge
Partition: 2026-10-02
Keys:
  - order_id

Dependencies:
  - bronze.orders
  - silver.customers

Quality checks:
  - not_null(order_id)
  - unique(order_id)

Resolved environment: production
Write operations: DISABLED
```

Dry runs are particularly valuable for:

- production changes;
- backfills;
- configuration reviews;
- debugging;
- incident response.

A strong dry run should make the engine's decisions visible without exposing secrets.

---


## 30. Golden Tests

A golden test compares a generated artifact against an approved expected artifact.

For metadata-driven pipelines, useful golden artifacts include:

- execution plans;
- rendered SQL;
- normalized configuration;
- dependency graphs.

Conceptually:

```text
orders.yaml
    ↓
execution planner
    ↓
expected plan
        ↕
actual plan
```

Example test idea:

```python
def test_orders_plan_matches_golden():
    config = load_config("orders.yaml")
    plan = build_plan(config, context)

    assert plan == expected_orders_plan
```

For SQL:

```python
def test_orders_sql_matches_golden():
    sql = render_orders_sql(config)
    assert normalize(sql) == normalize(expected_sql)
```

### Why golden tests matter

An engine change can affect hundreds of datasets.

A small code change in:

```text
strategy selection
partition calculation
SQL template
quality rules
```

can silently alter many pipelines.

Golden tests create a regression boundary.

---


## 31. Custom Step Escape Hatches

A generic framework must support genuinely exceptional workloads.

For example:

```yaml
custom_step: customer_identity_resolution
```

The custom step should implement a known interface.

Conceptually:

```text
Generic Engine
      ↓
Custom Step Interface
      ↓
Customer Identity Resolution
```

The escape hatch should be:

- explicit;
- versioned;
- tested;
- observable;
- owned;
- limited.

Do not create special configuration flags for every exceptional case.

A healthy framework might have a large majority of datasets using common behavior and a smaller set using controlled extensions. Any percentage such as 80–95% is illustrative, not a universal target.

The important question is:

> Is this behavior genuinely unique, or have we failed to model a common pattern?

---


## 32. Avoiding Configuration Becoming a Programming Language

This is one of the most important design boundaries.

Bad configuration starts to look like:

```yaml
if:
  condition:
    ...
  then:
    ...
  else:
    ...
```

Then someone adds:

```text
loops
nested conditions
expressions
arbitrary transformations
function calls
custom operators
```

Eventually:

```text
YAML
  ↓
custom parser
  ↓
custom interpreter
  ↓
debugger
  ↓
runtime
```

You have created a new programming language.

### Symptoms

- configuration files are hundreds of lines;
- operators cannot predict behavior;
- IDE support is poor;
- testing becomes complicated;
- every new feature adds another syntax rule;
- documentation becomes larger than the implementation;
- error messages become opaque.

The governing rule is:

> **Put stable logic in code; put controlled variation in configuration.**

If a behavior requires substantial branching or algorithmic logic, write it as code and expose a small, typed configuration surface if necessary.

---


## 33. Common Failure Modes

### Failure: invalid configuration reaches runtime

**Cause:** YAML parsed successfully but semantic validation was skipped.

**Fix:** Pydantic validation before planning.

### Failure: accidental full refresh

**Cause:** dangerous default or typo in strategy resolution.

**Fix:** make destructive strategies explicit and validate them.

### Failure: merge without keys

**Cause:** incomplete configuration.

**Fix:** cross-field validation.

### Failure: unsafe SQL

**Cause:** raw Jinja interpolation of untrusted identifiers or values.

**Fix:** parameterize values and validate/allowlist/quote identifiers.

### Failure: production overlay surprises

**Cause:** unclear precedence.

**Fix:** explicit resolution rules and dry-run output.

### Failure: plugin not found

**Cause:** configuration references an unregistered capability.

**Fix:** validate plugin names during planning.

### Failure: 200 datasets change unexpectedly

**Cause:** shared engine behavior changed without sufficient regression testing.

**Fix:** golden tests, compatibility checks, canary execution, and configuration/version review.

### Failure: framework becomes impossible to debug

**Cause:** excessive abstraction.

**Fix:** simplify the generic path and move unique logic into explicit custom code.

---


## 34. Hands-On Implementation

We will build a conceptual mini-framework for:

```text
orders
customers
products
```

The target flow is:

```text
DatasetConfig
     ↓
Pydantic validation
     ↓
ExecutionPlan
     ↓
Generic Engine
     ↓
Load Strategy Registry
     ↓
Transformation Registry
     ↓
Quality Rules
     ↓
Dry Run
     ↓
Execution
     ↓
Operational Metadata
```

All implementation below is intentionally contained in this chapter. It does not require creating separate helper files to understand the architecture.

---


## 35. Testing

Metadata-driven systems need multiple layers of testing.

### Configuration tests

Test:

- valid configuration;
- missing fields;
- invalid enum;
- invalid nested configuration;
- unsafe defaults;
- invalid strategy combinations.

### Engine tests

Test:

- strategy selection;
- transformation selection;
- plan generation;
- dependency resolution;
- partition calculation.

### SQL tests

Test:

- template rendering;
- identifier validation;
- parameter handling;
- expected SQL structure.

### Golden tests

Test:

- expected plan;
- expected rendered SQL;
- normalized configuration.

### Integration tests

Test:

```text
config
  ↓
validation
  ↓
plan
  ↓
execution
  ↓
quality
```

### Regression tests

The most important additional concern is regression across existing datasets.

If 300 datasets share one engine, an engine change can affect all 300.

Therefore:

> **The more centralized the behavior, the stronger the regression boundary must be.**

---


## 36. Debugging

## Scenario 1 — `load_strategy` typo

**Symptom:** runtime reports an unknown strategy.

**Cause:** configuration contains `mergee`.

**Investigation:** inspect validated configuration and registry.

**Incorrect fix:** silently fall back to `append`.

**Correct fix:** fail validation with an explicit supported-values error.

**Prevention:** `Literal`/enum validation and configuration tests.

---

## Scenario 2 — Dataset accidentally uses `full_refresh`

**Symptom:** an enormous amount of data is rewritten.

**Cause:** destructive strategy was explicitly or accidentally selected.

**Investigation:** inspect resolved configuration and execution plan.

**Correct solution:** require explicit authorization for destructive strategies and expose the choice in dry runs.

**Prevention:** safe defaults, change review, plan approval.

---

## Scenario 3 — Merge configuration omits keys

**Symptom:** merge cannot identify target records.

**Cause:** `keys` is empty.

**Correct solution:** reject the configuration before execution.

**Prevention:** cross-field Pydantic validation.

---

## Scenario 4 — YAML indentation changes meaning

**Symptom:** configuration validates differently than expected.

**Cause:** nested values were placed at the wrong indentation level.

**Correct solution:** inspect parsed configuration and normalized output.

**Prevention:** schema validation and configuration formatting/linting.

---

## Scenario 5 — Jinja produces invalid SQL

**Symptom:** database parser rejects generated SQL.

**Investigation:**

1. inspect input configuration;
2. inspect rendered SQL;
3. compare against golden SQL;
4. identify the template branch;
5. reproduce with a minimal dataset.

**Prevention:** golden tests and dry-run rendering.

---

## Scenario 6 — Unsafe identifier

**Symptom:** generated SQL references an unsupported relation or contains malformed SQL.

**Cause:** arbitrary identifier passed into the template.

**Correct solution:** validate against an allowlist/catalog and quote through a trusted database mechanism.

---

## Scenario 7 — Production overlay changes an unexpected value

**Symptom:** production plan uses an unexpected target.

**Cause:** unclear precedence.

**Correct solution:** show resolved configuration and define precedence explicitly.

**Prevention:** overlay tests and dry-run snapshots.

---

## Scenario 8 — Engine change affects 200 datasets

**Symptom:** many regression tests fail or outputs change.

**Correct response:** stop broad deployment, identify affected strategy/plan change, compare golden artifacts, and roll back or release a compatibility-preserving change.

---

## Scenario 9 — Plugin not registered

**Symptom:** configuration references a transformation that cannot be resolved.

**Correct solution:** fail during planning with a clear plugin-resolution error.

---

## Scenario 10 — Generic engine is too complex

**Symptom:** engineers cannot predict what a configuration will do.

**Root cause:** too many flags, inheritance layers, plugins, and special cases.

**Correct solution:** simplify the generic path and move exceptional logic into explicit code.

**Prevention:** architecture reviews based on framework complexity, not only feature count.

---


## 37. Production Architecture

A production architecture can look like:

```text
                    ┌──────────────────────┐
                    │ Dataset Definitions  │
                    │ YAML / Metadata      │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │ Pydantic Validation  │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │ Configuration        │
                    │ Resolver / Overlay   │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │ Execution Planner    │
                    └──────────┬───────────┘
                               ↓
             ┌─────────────────┼─────────────────┐
             ↓                 ↓                 ↓
       Load Strategy      Transform Registry   SQL Templates
             │                 │                 │
             └─────────────────┼─────────────────┘
                               ↓
                    ┌──────────────────────┐
                    │ Quality Validation   │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │ Execution            │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │ Operational Metadata │
                    └──────────────────────┘
```

### Layer 1 — Definitions

Version-controlled dataset configuration.

### Layer 2 — Validation

Schema and semantic validation.

### Layer 3 — Resolution

Environment overlays and approved runtime parameters.

### Layer 4 — Planning

Build a deterministic execution plan.

### Layer 5 — Strategies

Select known load and transformation behavior.

### Layer 6 — SQL generation

Render safe SQL where SQL templates are appropriate.

### Layer 7 — Quality

Run standardized data-quality checks.

### Layer 8 — Execution

Perform I/O and transformations.

### Layer 9 — Operational metadata

Record:

- run;
- status;
- row counts;
- logic version;
- configuration version;
- timestamps;
- quality outcomes.

Keep orchestration concerns such as scheduling and dependency execution compatible with, but separate from, the transformation engine.

---


## 38. Production Case Study

A company has:

```text
300 datasets
```

Most follow:

```text
extract
→ standardize
→ validate
→ deduplicate
→ incremental load
```

They differ in:

- source;
- target;
- keys;
- partitions;
- load strategy;
- quality rules;
- owners;
- schedules.

Requirements:

- onboard new datasets quickly;
- maintain consistent behavior;
- allow custom transformations;
- support dry runs;
- support backfills;
- support dev/staging/prod;
- protect secrets;
- provide lineage and ownership.

### Reference solution

Start by cataloging the 300 datasets.

For each dataset identify:

```text
common behavior
vs
controlled variation
vs
genuinely unique behavior
```

Design:

```text
Version-controlled configuration
          ↓
Pydantic validation
          ↓
Execution planner
          ↓
Strategy registry
          ↓
Transformation registry
          ↓
Quality layer
          ↓
Execution
          ↓
Operational metadata
```

Use:

- explicit load strategies;
- typed configuration;
- dry-run plans;
- golden tests;
- environment resolution;
- secret references;
- dependency metadata;
- controlled plugins.

Do not put arbitrary business logic into YAML.

### New dataset onboarding

For a normal dataset:

```text
new YAML definition
      ↓
validation
      ↓
golden plan review
      ↓
test
      ↓
deploy
```

No new engine code should be required.

For an exceptional dataset:

```text
new dataset
      ↓
prove generic path is insufficient
      ↓
implement custom step
      ↓
register plugin
      ↓
test + observe
```

The architecture should optimize for consistency without pretending all datasets are identical.

---


## 39. Exercises

## Beginner

### Exercise 1 — Convert a hard-coded pipeline

Take one pipeline with hard-coded source, target, keys, and strategy. Extract those values into configuration.

**Goal:** identify controlled variation.

### Exercise 2 — Design `DatasetConfig`

Create a minimal schema containing:

```text
name
source
target
load_strategy
```

**Solution guidance:** make only truly required fields mandatory.

### Exercise 3 — Validate YAML

Create valid and invalid configurations and validate them with Pydantic.

### Exercise 4 — Required and optional fields

Add:

```text
owner
schedule
quality
```

and decide which should be optional.

### Exercise 5 — Load strategy

Support:

```text
append
merge
overwrite_partition
```

and reject unknown strategies.

## Intermediate

### Exercise 6 — Generic execution planner

Build a plan containing:

```text
dataset
source
target
strategy
partition
quality checks
```

### Exercise 7 — Strategy registry

Replace a growing `if/elif` tree with a registry.

### Exercise 8 — Partition metadata

Add daily/monthly partition configuration and produce a plan for a requested date.

### Exercise 9 — Quality rules

Implement declarative `not_null` and `unique` checks.

### Exercise 10 — Ownership/SLA metadata

Add owner and SLA fields and produce an operational summary.

### Exercise 11 — Dry run

Implement a command conceptually equivalent to:

```text
run --dataset orders --date 2026-10-02 --dry-run
```

The output must contain no write operation.

## Advanced

### Exercise 12 — Jinja SQL

Generate standardized staging SQL for several datasets.

### Exercise 13 — Identifier allowlisting

Reject a table not present in an approved catalog.

### Exercise 14 — Environment overlays

Design base + development + staging + production configuration resolution.

### Exercise 15 — Secret separation

Replace a database password with a secret reference.

### Exercise 16 — Plugin support

Create one custom transformation plugin for a genuinely exceptional dataset.

### Exercise 17 — Golden tests

Snapshot:

- execution plan;
- rendered SQL.

### Exercise 18 — Configuration versioning

Record configuration version alongside each execution.

## Expert

### Exercise 19 — 1,000-dataset platform

Design a metadata-driven platform for 1,000 datasets.

Cover:

- validation;
- planning;
- strategy registry;
- plugins;
- lineage;
- operational state;
- testing;
- deployment.

### Exercise 20 — Configuration vs code

Given 20 proposed configuration fields, classify each as:

```text
configuration
code
metadata
operational state
```

Explain every decision.

### Exercise 21 — Framework boundary

Identify three datasets that should remain custom code and explain why.

### Exercise 22 — Bad configuration rollback

Design a rollback procedure for a configuration deployment that changes the behavior of 100 datasets.

### Exercise 23 — Configuration-change impact analysis

Given:

```text
dataset A
  ↓
dataset B
  ↓
dataset C
```

and a configuration change to A, determine which downstream datasets require review or reprocessing.

---


## 40. Senior Data Engineer Reasoning

Use this decision process:

```text
How many datasets share the same execution pattern?
        ↓
What varies between datasets?
        ↓
Can the variation be represented safely as configuration?
        ↓
What belongs in reusable code?
        ↓
What needs validation?
        ↓
What should be extensible through plugins?
        ↓
How will configuration be versioned?
        ↓
How will changes be tested?
        ↓
Can we preview execution with a dry run?
        ↓
How will lineage and ownership be represented?
        ↓
Where do secrets live?
        ↓
When should we stop generalizing?
```

### Senior question 1

Do not ask:

> "Can I make this configurable?"

Ask:

> "Will making this configurable reduce repeated implementation without hiding important behavior?"

### Senior question 2

Do not ask:

> "How many configuration options can the framework support?"

Ask:

> "What is the smallest stable abstraction that supports the common workload?"

### Senior question 3

Do not ask:

> "Can every dataset run through one engine?"

Ask:

> "Which datasets share a sufficiently stable execution contract?"

### Senior question 4

Do not ask:

> "Can I put this rule in YAML?"

Ask:

> "Will operators understand, test, version, and debug this rule more safely in configuration than in code?"

The senior-level principle is:

> **Metadata-driven engineering removes repeated implementation while preserving explicitness, testability, and operational control.**

---


## 41. Interview Questions


### Basic — Question 1

**Question:** What is a configuration-driven pipeline?

**Expected answer:** A pipeline where reusable execution behavior is implemented in code and dataset-specific variation is supplied through validated configuration.

**Explanation:** Configuration moves controlled variation out of duplicated pipeline code.

**Key concepts:** code, configuration, reuse

**Senior-level insight:** The value comes from reducing repeated implementation without hiding behavior.


### Basic — Question 2

**Question:** What is metadata?

**Expected answer:** Metadata is information about data or data-processing operations, such as schema, owner, lineage, or status.

**Explanation:** It helps systems and people understand and operate datasets.

**Key concepts:** metadata, schema, lineage

**Senior-level insight:** Operational metadata can become an input to orchestration and governance.


### Basic — Question 3

**Question:** Why do hard-coded pipelines become difficult at scale?

**Expected answer:** Because duplicated logic creates inconsistent fixes, testing overhead, and onboarding cost.

**Explanation:** The number of independently maintained implementations grows with dataset count.

**Key concepts:** duplication, consistency, operations

**Senior-level insight:** Centralizing stable behavior creates a stronger regression boundary.


### Basic — Question 4

**Question:** What is YAML used for here?

**Expected answer:** YAML is a human-readable representation of dataset configuration.

**Explanation:** It naturally represents nested configuration structures.

**Key concepts:** YAML, configuration

**Senior-level insight:** YAML itself provides no semantic safety; validation is still required.


### Basic — Question 5

**Question:** Why is Pydantic useful?

**Expected answer:** It validates parsed configuration against an explicit typed schema.

**Explanation:** It catches invalid values and missing fields before execution.

**Key concepts:** Pydantic, schema validation

**Senior-level insight:** Cross-field validation is especially important for pipeline safety.


### Basic — Question 6

**Question:** What is a DatasetConfig?

**Expected answer:** A typed representation of the configuration required to run one dataset pipeline.

**Explanation:** It can contain source, target, keys, strategy, partition, quality, and operational fields.

**Key concepts:** typed configuration, nested models

**Senior-level insight:** A good DatasetConfig is an explicit contract between configuration and engine.


### Basic — Question 7

**Question:** What is a registry?

**Expected answer:** A mapping from a stable configuration name to a trusted implementation.

**Explanation:** It allows the engine to dispatch to known strategies without a giant conditional tree.

**Key concepts:** registry, strategy

**Senior-level insight:** Registries make supported capabilities explicit.


### Basic — Question 8

**Question:** What is a dry run?

**Expected answer:** A mode that validates and plans an operation without performing writes.

**Explanation:** It makes the intended execution visible before production changes.

**Key concepts:** planning, safety

**Senior-level insight:** Dry runs are particularly valuable for backfills and destructive strategies.


### Basic — Question 9

**Question:** Why should secrets stay out of ordinary configuration?

**Expected answer:** Because configuration is often broadly readable and version controlled.

**Explanation:** Secrets require stronger access control, rotation, and auditability.

**Key concepts:** secrets, security

**Senior-level insight:** Reference a secret rather than embedding its value.


### Basic — Question 10

**Question:** What is a golden test?

**Expected answer:** A regression test comparing a generated artifact with an approved expected artifact.

**Explanation:** Plans and rendered SQL are useful golden-test targets.

**Key concepts:** golden test, regression

**Senior-level insight:** Centralized engines benefit heavily from artifact-level regression tests.


### Moderate — Question 11

**Question:** How would you validate that merge configuration is complete?

**Expected answer:** Require at least one key and reject the configuration before execution.

**Explanation:** Merge semantics depend on a stable target identity.

**Key concepts:** cross-field validation, merge keys

**Senior-level insight:** The rule belongs in configuration validation rather than runtime discovery.


### Moderate — Question 12

**Question:** Why separate planning from execution?

**Expected answer:** Planning makes decisions inspectable and testable without performing I/O.

**Explanation:** It enables dry runs, golden tests, and clearer debugging.

**Key concepts:** execution plan, dry run

**Senior-level insight:** A plan is a useful operational artifact.


### Moderate — Question 13

**Question:** Why are nested Pydantic models preferable to a giant dictionary?

**Expected answer:** They provide explicit structure, typing, validation, and readable errors.

**Explanation:** Each configuration area gets a clear contract.

**Key concepts:** nested models, validation

**Senior-level insight:** Configuration models should evolve deliberately like APIs.


### Moderate — Question 14

**Question:** Why is `full_refresh` a dangerous default?

**Expected answer:** It can rewrite large amounts of data when a user omitted or misspelled the intended strategy.

**Explanation:** Destructive behavior should be explicit.

**Key concepts:** safe defaults, destructive operations

**Senior-level insight:** Defaults should reduce accidental damage.


### Moderate — Question 15

**Question:** When should a quality rule remain code?

**Expected answer:** When it contains complex domain logic or branching that cannot be represented clearly and safely as a declarative rule.

**Explanation:** Simple standardized checks are good configuration candidates.

**Key concepts:** quality, configuration boundary

**Senior-level insight:** Declarative rules should remain intentionally limited.


### Moderate — Question 16

**Question:** Why use a registry instead of many `if/elif` branches?

**Expected answer:** A registry makes supported strategies explicit and localizes dispatch.

**Explanation:** It is easier to test and extend.

**Key concepts:** registry, strategy pattern

**Senior-level insight:** The registry should still have a controlled capability set.


### Moderate — Question 17

**Question:** Why can Jinja be unsafe?

**Expected answer:** Because it generates text and does not automatically validate SQL identifiers or parameterize values.

**Explanation:** Untrusted interpolation can produce malformed or unsafe SQL.

**Key concepts:** Jinja, SQL safety

**Senior-level insight:** Templating and SQL safety are separate concerns.


### Moderate — Question 18

**Question:** What is the difference between an identifier and a value in SQL?

**Expected answer:** A table or column name is an identifier; a date or numeric filter is a value.

**Explanation:** Values can generally be parameterized, while identifiers require validation and safe quoting.

**Key concepts:** identifiers, parameters

**Senior-level insight:** Confusing the two is a common SQL-generation bug.


### Moderate — Question 19

**Question:** What should a dry-run output contain?

**Expected answer:** The resolved dataset, source, target, strategy, partitions, dependencies, quality checks, and confirmation that writes are disabled.

**Explanation:** Operators need enough information to predict the execution.

**Key concepts:** dry run, execution plan

**Senior-level insight:** Never expose secret values in a dry-run plan.


### Moderate — Question 20

**Question:** Why is configuration versioning important?

**Expected answer:** It makes behavior reproducible and provides an audit trail for changes.

**Explanation:** A run should be traceable to the configuration and logic versions that produced it.

**Key concepts:** versioning, reproducibility

**Senior-level insight:** Configuration version belongs in operational metadata.


### Hard — Question 21

**Question:** How would you design a generic engine for 300 datasets?

**Expected answer:** Identify common execution patterns, model controlled variation in typed configuration, validate before planning, dispatch through strategies, support controlled plugins, and test plans and SQL.

**Explanation:** The engine should standardize the common path while preserving an explicit extension mechanism.

**Key concepts:** generic engine, strategy, plugins

**Senior-level insight:** The hard part is defining the boundary, not writing the loop.


### Hard — Question 22

**Question:** How would you prevent a dataset from accidentally performing a full refresh?

**Expected answer:** Require explicit full-refresh selection, validate it, surface it in dry runs, and apply appropriate deployment/review controls.

**Explanation:** The engine should make destructive intent visible.

**Key concepts:** safety, dry run

**Senior-level insight:** Safety should be designed into the configuration contract.


### Hard — Question 23

**Question:** How would you design safe Jinja SQL generation?

**Expected answer:** Use templates only for controlled structure, parameterize values, validate identifiers against trusted metadata or allowlists, and test rendered SQL.

**Explanation:** Jinja is not a security boundary.

**Key concepts:** Jinja, allowlist, parameterization

**Senior-level insight:** The renderer should reject unsupported identifiers before SQL reaches the database.


### Hard — Question 24

**Question:** How would you support dev, staging, and production?

**Expected answer:** Use a shared base configuration plus explicit environment overlays with documented precedence and dry-run visibility.

**Explanation:** Only environment-specific behavior should vary.

**Key concepts:** overlays, precedence

**Senior-level insight:** Keep inheritance shallow enough to reason about.


### Hard — Question 25

**Question:** How would you design a plugin architecture?

**Expected answer:** Define a stable interface, register named implementations, validate plugin names, version plugins, and provide ownership and tests.

**Explanation:** Plugins should extend the framework without changing its core for every exception.

**Key concepts:** plugins, interfaces

**Senior-level insight:** If every dataset needs a plugin, the common abstraction may be wrong.


### Hard — Question 26

**Question:** What belongs in operational metadata?

**Expected answer:** Run status, timestamps, row counts, configuration version, logic version, quality results, and ownership context.

**Explanation:** It records what happened rather than what should happen.

**Key concepts:** operational state, metadata

**Senior-level insight:** Keep mutable state separate from desired configuration.


### Hard — Question 27

**Question:** How would you test a centralized engine change?

**Expected answer:** Run unit tests, golden plan/SQL tests, integration tests, and regression tests across representative datasets before broad rollout.

**Explanation:** One engine change can affect many pipelines.

**Key concepts:** regression, golden tests

**Senior-level insight:** Centralization increases the importance of compatibility testing.


### Hard — Question 28

**Question:** How would you detect configuration drift?

**Expected answer:** Version configuration in Git, validate it in CI, record deployed versions, compare expected and deployed versions, and control manual changes.

**Explanation:** Drift occurs when runtime behavior no longer matches the reviewed configuration.

**Key concepts:** drift, version control

**Senior-level insight:** Configuration deployment should be observable like code deployment.


### Hard — Question 29

**Question:** When should a dataset leave the generic engine?

**Expected answer:** When its behavior is genuinely different enough that forcing it into configuration would create complexity or obscure correctness.

**Explanation:** A controlled custom-code path is healthier than endless flags.

**Key concepts:** escape hatch, framework boundary

**Senior-level insight:** The goal is useful reuse, not universal abstraction.


### Hard — Question 30

**Question:** Why are golden tests especially valuable in metadata-driven systems?

**Expected answer:** Because small engine or template changes can alter behavior across many datasets.

**Explanation:** Golden artifacts expose unexpected plan or SQL changes.

**Key concepts:** golden tests, regression

**Senior-level insight:** They provide a concrete diff of behavioral changes.


### Advanced — Question 31

**Question:** Design a metadata-driven platform for 300 datasets.

**Expected answer:** Use version-controlled typed definitions, Pydantic validation, environment resolution, deterministic planning, strategy registries, controlled plugins, quality checks, dry runs, golden tests, operational metadata, and lineage.

**Explanation:** The platform should standardize the common path while preserving custom extensions.

**Key concepts:** platform design, metadata, lineage

**Senior-level insight:** Keep orchestration and transformation responsibilities clearly bounded.


### Advanced — Question 32

**Question:** How would you design configuration validation for hundreds of pipelines?

**Expected answer:** Use nested typed models, semantic cross-field validators, CI validation, configuration tests, and fail-fast deployment checks.

**Explanation:** Validation must happen before data-changing execution.

**Key concepts:** Pydantic, CI, semantic validation

**Senior-level insight:** Treat configuration as a versioned API.


### Advanced — Question 33

**Question:** How would you design a generic incremental loading engine?

**Expected answer:** Represent strategy, keys, partitioning, and incremental parameters in validated configuration, produce a plan, dispatch to tested load strategies, and record the configuration/logic version.

**Explanation:** The engine should reuse the idempotent and backfill patterns from earlier topics.

**Key concepts:** incremental, strategies, planning

**Senior-level insight:** Configuration should select known semantics rather than encode the algorithm.


### Advanced — Question 34

**Question:** How would you make Jinja SQL generation safe at scale?

**Expected answer:** Restrict templates to approved structures, validate identifiers against catalog metadata, parameterize values, normalize rendered SQL, and golden-test representative outputs.

**Explanation:** Centralized templates magnify both good and bad changes.

**Key concepts:** SQL safety, allowlist, golden tests

**Senior-level insight:** A template engine must never be treated as a trust boundary.


### Advanced — Question 35

**Question:** How would you design environment overlays across dev/staging/prod?

**Expected answer:** Define a base schema, explicit overlay precedence, immutable deployment artifacts, protected production values, and resolved-config dry runs.

**Explanation:** Operators must be able to see exactly what configuration will execute.

**Key concepts:** overlays, deployment, safety

**Senior-level insight:** Avoid deep inheritance and implicit overrides.


### Advanced — Question 36

**Question:** How would you design plugins for exceptional datasets?

**Expected answer:** Define stable interfaces, registry discovery, compatibility/version checks, ownership, tests, observability, and a lifecycle for deprecation.

**Explanation:** Plugins should be rare, explicit extensions rather than the normal configuration path.

**Key concepts:** plugin lifecycle, interfaces

**Senior-level insight:** A growing plugin count is an architectural signal.


### Advanced — Question 37

**Question:** How would you design configuration rollback?

**Expected answer:** Version configurations, record deployed versions, make deployment atomic where possible, support selecting a previous version, validate it, and run a dry plan before activation.

**Explanation:** Rollback requires reproducible artifacts, not just a database backup.

**Key concepts:** rollback, versioning

**Senior-level insight:** Configuration rollback should be tested before an incident.


### Advanced — Question 38

**Question:** How would you design dry-run planning for backfills?

**Expected answer:** Resolve the requested interval, calculate affected partitions, dependencies, strategies, quality checks, estimated scope, and write operations without executing writes.

**Explanation:** The plan should expose the blast radius.

**Key concepts:** backfill, planning, safety

**Senior-level insight:** A dry run is an operational safety mechanism.


### Advanced — Question 39

**Question:** How would you design golden testing for a shared engine?

**Expected answer:** Maintain representative configs and expected plans/SQL, normalize nondeterministic formatting, run tests in CI, and require review for intentional changes.

**Explanation:** Golden tests should capture supported behavior rather than implementation formatting.

**Key concepts:** golden tests, CI, regression

**Senior-level insight:** Use representative coverage across strategies and dataset shapes.


## 35A. Anti-Patterns

| Anti-pattern | Why it fails | Better approach |
|---|---|---|
| Copy-paste one pipeline per dataset | Duplicated behavior | Generic engine + controlled configuration |
| Raw unvalidated YAML | Runtime failures | Pydantic validation |
| Giant `if/elif` engine | Hard to maintain | Registry/strategy pattern |
| Secrets in YAML | Security risk | Secret manager/environment |
| Blind Jinja interpolation | Unsafe SQL | Parameterization + identifier allowlists |
| Configuration as code | Impossible complexity | Keep logic in code |
| Hundreds of boolean flags | Combinatorial complexity | Structured strategies/enums |
| No dry run | Production surprises | Execution planning |
| No golden tests | Silent behavior changes | Plan/template regression tests |
| No config versioning | Reproducibility problems | Version-controlled configuration |
| Everything forced into framework | Framework complexity | Custom escape hatch |
| Runtime state mixed with config | Confusion | Separate configuration from operational metadata |
| Deep environment inheritance | Hidden precedence | Shallow explicit overlays |
| Arbitrary plugin loading | Uncontrolled execution surface | Registered, versioned plugins |
| Silent fallback on invalid config | Wrong behavior can look successful | Fail fast |

---


### Advanced — Question 40

**Question:** How do you decide whether configuration has gone too far?

**Expected answer:** Measure configuration size, flag count, hidden control flow, plugin frequency, debugging cost, and conceptual complexity. Move algorithmic behavior back into code.

**Explanation:** Configuration should describe controlled variation, not implement arbitrary computation.

**Key concepts:** framework boundaries, complexity

**Senior-level insight:** If operators need to learn a new language to understand a config, the abstraction has likely failed.


## 42. Architecture Questions

### Architecture 1 — Metadata platform for 300 datasets

Design the platform described in the production case study.

**Reference solution:** use typed configuration, a validation boundary, deterministic execution planning, strategy registries, controlled plugins, quality rules, dry runs, golden tests, versioning, lineage, and operational metadata. Keep orchestration responsibilities explicit.

### Architecture 2 — Configuration validation

Design validation for hundreds of datasets.

**Reference solution:** version-controlled configuration, Pydantic models, semantic validators, CI checks, representative integration tests, and deployment-time validation.

### Architecture 3 — Generic incremental engine

Design an engine supporting append, overwrite-partition, merge, and full refresh.

**Reference solution:** typed strategy enum, strategy registry, explicit key/partition requirements, deterministic plan, idempotent implementations, and operational logging.

### Architecture 4 — Safe Jinja SQL system

Design a SQL templating layer.

**Reference solution:** templates define approved structure; values are parameterized; identifiers are validated against trusted catalog metadata and safely quoted; rendered SQL is golden-tested.

### Architecture 5 — Environment overlays

Design dev/staging/prod configuration.

**Reference solution:** shared base plus shallow explicit overlays, documented precedence, immutable deployments, secret references, and resolved-config dry runs.

### Architecture 6 — Plugin architecture

Design support for exceptional datasets.

**Reference solution:** stable plugin interface, named registry, compatibility/version checks, ownership, tests, observability, and deprecation policy.

### Architecture 7 — Configuration rollback

Design rollback for a bad configuration affecting 100 datasets.

**Reference solution:** version every configuration deployment, identify impacted datasets, restore previous approved version, validate, dry-run, canary, and then roll out.

### Architecture 8 — Dry-run planning

Design a plan generator for a backfill.

**Reference solution:** resolve environment, calculate partitions, dependencies, strategy, quality checks, estimated scope, and produce a write-disabled plan.

### Architecture 9 — Golden testing

Design regression testing for the shared engine.

**Reference solution:** maintain representative configuration fixtures and expected plans/SQL; compare normalized artifacts in CI; require intentional updates to golden files.

### Architecture 10 — Framework boundary

Decide when a dataset should become custom code.

**Reference solution:** compare its behavior to existing patterns. If forcing it into the framework requires many flags, nested conditions, or opaque plugins, keep the dataset custom and expose only stable shared interfaces.

---


## 43. Production Checklist

### Configuration

- [ ] Configuration schema defined
- [ ] Pydantic validation exists
- [ ] Required fields explicit
- [ ] Dangerous defaults avoided
- [ ] Configuration version controlled
- [ ] Configuration review process exists
- [ ] Semantic cross-field validation exists
- [ ] Configuration deployment is observable

### Engine

- [ ] Planning separated from execution
- [ ] Strategies are explicit
- [ ] Registry pattern used where appropriate
- [ ] Custom extension mechanism exists
- [ ] Generic engine remains understandable
- [ ] Unknown strategy/plugin names fail early

### SQL

- [ ] Values parameterized
- [ ] Identifiers validated/allowlisted
- [ ] Jinja templates reviewed
- [ ] Rendered SQL tested
- [ ] SQL generation cannot accept arbitrary unsafe identifiers

### Environment

- [ ] Environment overlays controlled
- [ ] Precedence documented
- [ ] Production overrides protected
- [ ] Secrets outside ordinary configuration
- [ ] Resolved configuration visible in dry runs without secret values

### Operations

- [ ] Dry run exists
- [ ] Golden tests exist
- [ ] Regression tests exist
- [ ] Ownership metadata exists
- [ ] Dependency metadata exists
- [ ] Operational state separated from configuration
- [ ] Configuration and logic versions recorded
- [ ] Rollback procedure exists

### Architecture

- [ ] Configuration complexity monitored
- [ ] Framework boundaries defined
- [ ] Custom escape hatch exists
- [ ] No unnecessary internal DSL
- [ ] New datasets can be onboarded safely
- [ ] Exceptional datasets do not drive the common path

---


## 44. Final Mental Model

Keep these three definitions:

```text
CODE
=
Reusable Behavior
```

```text
CONFIGURATION
=
Controlled Variation
```

```text
METADATA
=
Information About Data + Operations
```

Then:

```text
Validated Configuration
        ↓
Execution Plan
        ↓
Generic Engine
        ↓
Reusable Strategies
        ↓
Controlled Extensions
        ↓
Quality + Observability
        ↓
Production Pipeline
```

The purpose is not to eliminate code.

The purpose is to eliminate **unnecessary repeated code** while keeping behavior:

- explicit;
- validated;
- testable;
- observable;
- operationally safe.

The most important boundary is:

```text
Common stable behavior
        ↓
Reusable code

Controlled dataset variation
        ↓
Configuration

Information about data and operations
        ↓
Metadata

Genuinely unique algorithms
        ↓
Custom code / controlled plugin
```

The final principle is:

> **The purpose of metadata-driven pipelines is not to eliminate code. It is to eliminate unnecessary repeated code while keeping behavior explicit, validated, testable, and operationally safe.**

And:

> **If configuration becomes harder to understand than the code it replaced, the abstraction has gone too far.**

---


## 45. Exit Criteria

You are ready to move forward when you can independently:

- explain metadata-driven pipeline design;
- explain configuration-driven architecture;
- distinguish code from configuration;
- distinguish metadata from configuration;
- design YAML dataset definitions;
- validate configuration with Pydantic;
- design nested configuration models;
- define safe defaults;
- build a generic pipeline engine;
- separate planning from execution;
- represent load strategies safely;
- represent partition metadata;
- represent quality rules;
- represent ownership and SLA metadata;
- use strategy/registry patterns;
- design controlled plugins;
- define custom-step escape hatches;
- use Jinja safely;
- distinguish identifiers from values;
- use allowlists and safe SQL generation;
- design environment overlays;
- separate secrets from configuration;
- compare runtime interpretation with code generation;
- design metadata catalogs;
- model dependencies and lineage;
- build dry-run execution plans;
- create golden tests;
- detect configuration drift;
- prevent configuration from becoming a programming language;
- recognize excessive-flag and inner-platform risks;
- design production metadata-driven systems;
- decide when generic framework vs custom code is appropriate;
- explain these decisions in a senior Data Engineering interview.

The mastery progression is:

```text
Hard-Coded Pipelines
        ↓
Configuration
        ↓
Metadata
        ↓
YAML
        ↓
Pydantic Validation
        ↓
DatasetConfig
        ↓
Generic Engine
        ↓
Strategy / Registry
        ↓
Plugins
        ↓
Jinja SQL
        ↓
SQL Safety
        ↓
Environment Overlays
        ↓
Secret Separation
        ↓
Metadata Catalog
        ↓
Dry Runs
        ↓
Golden Tests
        ↓
Configuration Drift
        ↓
Framework Boundaries
        ↓
Production Architecture
        ↓
Testing
        ↓
Debugging
        ↓
Senior-Level Design
```

### Final quality gate

Before considering the topic complete, verify:

- beginner concepts precede advanced concepts;
- all roadmap-required concepts are covered;
- hard-coded pipeline limitations are explained;
- metadata is defined;
- configuration is defined;
- code vs configuration is explained;
- YAML is covered sufficiently;
- Pydantic validation is detailed;
- `DatasetConfig` is demonstrated;
- required/optional fields and defaults are covered;
- generic execution is demonstrated;
- load strategies and partition metadata are covered;
- quality rules and ownership/SLA metadata are covered;
- registry and plugin patterns are covered;
- custom escape hatch is covered;
- Jinja and SQL safety are covered;
- identifier allowlisting is covered;
- environment overlays and secret separation are covered;
- code generation vs runtime interpretation is covered;
- metadata catalog and lineage are covered;
- dry runs and golden tests are covered;
- configuration drift is covered;
- configuration-as-programming-language risk is covered;
- excessive flags and inner-platform risk are covered;
- hands-on implementation, testing, debugging, anti-patterns, production architecture, and case study are included;
- exercises progress from beginner to expert;
- 40 interview questions are included;
- 10 architecture questions are included;
- production checklist is included;
- final mental model is clear.

Do not introduce unrelated topics.

---
```
