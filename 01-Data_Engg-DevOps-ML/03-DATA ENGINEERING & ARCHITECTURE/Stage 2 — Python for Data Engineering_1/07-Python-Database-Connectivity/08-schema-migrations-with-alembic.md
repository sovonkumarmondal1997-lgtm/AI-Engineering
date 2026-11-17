# Schema Migrations with Alembic

## Learning Objectives

By the end of this topic, you should be able to:

- Explain why a production database schema needs versioned migration history.
- Explain Alembic's relationship with SQLAlchemy Core, ORM metadata, and PostgreSQL.
- Describe the roles of `alembic.ini`, `env.py`, revisions, `upgrade()`, `downgrade()`, and `alembic_version`.
- Initialize an Alembic environment conceptually and connect it to application settings without committing production credentials.
- Create, apply, inspect, and review migrations.
- Explain what `target_metadata` is and why Alembic needs it for autogeneration.
- Use `--autogenerate` as a migration candidate generator, then manually review its output.
- Identify dangerous rename, type-change, constraint, default, and data-migration cases.
- Distinguish schema migrations from data migrations and design safer multi-stage changes.
- Explain why migration safety depends on table size, workload, locks, transactions, and deployment compatibility.
- Use `lock_timeout` deliberately when failing fast is safer than blocking application traffic.
- Explain why PostgreSQL `CREATE INDEX CONCURRENTLY` has special execution requirements.
- Design nullable-first changes and batched backfills for large active tables.
- Apply expand-and-contract thinking to zero-downtime schema evolution.
- Generate and review offline SQL with Alembic.
- Explain revision branches, multiple heads, merge revisions, and `alembic stamp`.
- Design CI/CD gates for migrations and reason about failure recovery.
- Decide where Alembic belongs in a platform that also contains warehouses, dbt, and lakehouse table formats.

The key outcome is not memorizing commands. It is being able to defend a schema-evolution plan in production planning, code review, architecture review, CI/CD design, and incident investigation.

## Prerequisites

This topic assumes you already understand:

- SQLAlchemy Core
- `Engine`, `Connection`, `MetaData`, `Table`, and `Column`
- SQLAlchemy ORM models and Sessions
- PostgreSQL basics
- transactions and locking
- schema changes from Module 2.6

Topics 06–07 taught SQLAlchemy metadata and runtime database access. Topic 08 uses that metadata and introduces Alembic for versioned schema evolution.

Do not re-learn Core or ORM here. Use them as foundations.

---

# 1. Why Schema Migrations Exist

A database schema is a contract between applications and stored data. That contract changes over time.

Imagine the first version of a database:

```text
customers
---------
id
name
```

Application version 1 knows only:

```text
id
name
```

Now the product needs:

```text
country
```

Changing a Python model or SQL query does not, by itself, add `country` to the database. The database must move from one schema state to another.

Think of the evolution as:

```text
Schema v1
   ↓
Migration 001
   ↓
Schema v2
   ↓
Migration 002
   ↓
Schema v3
   ↓
Migration 003
   ↓
Schema v4
```

Without a controlled migration history, different environments can drift:

```text
Developer database → schema A
CI database        → schema B
Staging            → schema C
Production         → schema D
```

That drift creates failures that are difficult to reproduce.

A migration-based approach makes the change explicit:

```text
Schema change
      ↓
Migration script
      ↓
Review
      ↓
Test
      ↓
Apply
      ↓
Record version
      ↓
Next environment
```

### Why not just edit the production database manually?

Manual changes can work for an emergency, but they are difficult to reproduce, review, audit, and apply consistently elsewhere.

A migration gives the schema change a durable identity.

### Production lesson

A schema change is part of software delivery. Treating it as code gives the team a common language for answering:

- What changed?
- When did it change?
- Which environments received it?
- What should happen next?
- How do we recover?

---

# 2. Schema as Code

A useful mental model is:

```text
Schema
=
code
+
history
+
review
+
deployment
```

Schema-as-code means that the intended evolution of a relational schema is represented in version-controlled artifacts.

That creates several engineering properties.

### Version control

A revision can be reviewed in Git just like application code.

### Code review

A reviewer can inspect:

- the intended schema change
- possible data loss
- lock behavior
- deployment compatibility
- rollback/recovery implications

### Reproducibility

A fresh environment can be created by applying the migration history in order.

### Auditability

The migration graph gives a durable record of how the schema is supposed to evolve.

### Deployment

CI/CD can validate and apply the same migration artifacts that were reviewed.

Compare the two approaches.

### Manual mutation

```text
Someone changes production manually
        ↓
Only production changed
        ↓
Other environments may drift
```

### Migration-based mutation

```text
Migration committed
        ↓
Code review
        ↓
CI validation
        ↓
Deployment
        ↓
Target database advances
```

### Production lesson

The migration file is not merely documentation. It is an executable representation of a state transition.

---

# 3. What Is Alembic?

Alembic is a database migration tool designed to work with SQLAlchemy.

At a high level:

```text
SQLAlchemy MetaData
        ↓
Alembic migration logic
        ↓
Database schema
```

Alembic provides a framework for describing and applying versioned schema changes.

It manages concepts such as:

- migration revisions
- revision relationships
- upgrade paths
- downgrade paths
- migration bookkeeping
- autogeneration support
- online and offline execution

It does **not** automatically understand your intent.

For example, if one column is renamed, Alembic can compare structural states, but it cannot always know whether:

```text
DROP old_name
ADD new_name
```

means:

```text
RENAME old_name TO new_name
```

or whether you intentionally wanted two different columns.

That is why human review remains essential.

### Core idea

> Alembic knows migration structure and schema differences; it does not magically know business intent.

---

# 4. Alembic Architecture

A useful runtime view is:

```text
Application settings
       ↓
Alembic env.py
       ↓
SQLAlchemy Engine / connection
       ↓
PostgreSQL
```

A migration-history view is:

```text
Migration files
       ↓
Revision graph
       ↓
upgrade / downgrade
       ↓
Database
       ↓
alembic_version
```

The important components are:

| Component | Role |
| --- | --- |
| `alembic.ini` | Default Alembic configuration |
| `env.py` | Migration runtime configuration and execution entry point |
| `versions/` | Versioned migration scripts |
| revision | One node in the migration graph |
| `upgrade()` | Forward schema operation |
| `downgrade()` | Reverse operation for that revision |
| `target_metadata` | SQLAlchemy metadata used for autogeneration |
| `alembic_version` | Database-side migration-version bookkeeping |

Keep this distinction clear:

```text
Migration files
=
instructions for schema evolution

Database
=
actual schema state

alembic_version
=
recorded migration state
```

Those three concepts are related, but they are not identical.

---

# 5. `alembic init`

The conceptual command is:

```bash
alembic init migrations
```

It initializes an Alembic environment.

A typical structure is:

```text
project/
├── alembic.ini
└── migrations/
    ├── env.py
    ├── script.py.mako
    └── versions/
```

The important ideas are:

### `alembic.ini`

Configuration for the Alembic environment.

### `env.py`

Python code Alembic executes to configure and run migrations.

### `script.py.mako`

A template used when creating revision files.

### `versions/`

The directory containing migration revisions.

The command is initialization, not migration execution.

It does **not** change your production schema by itself.

### Production lesson

Initialize the migration framework in a disposable/development environment, then review its configuration before connecting it to a real target.

---

# 6. `alembic.ini`

`alembic.ini` provides configuration for Alembic.

A common entry is a SQLAlchemy URL, but a production codebase should avoid committing production credentials into source control.

Conceptually:

```text
Bad
---
hard-coded production username/password

Better
------
environment/settings
        ↓
env.py
        ↓
database connection
```

A configuration file may still contain defaults for local development, but production secrets should come from the environment or the application's existing settings mechanism.

A conceptual settings loader might expose:

```python
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class DatabaseSettings:
    url: str


def load_database_settings() -> DatabaseSettings:
    url = os.environ["DATABASE_URL"]
    return DatabaseSettings(url=url)
```

The important design is:

```text
CI/staging/prod configuration
        ↓
runtime settings
        ↓
Alembic env.py
```

not:

```text
developer laptop credentials
        ↓
committed source file
```

### Production lesson

Alembic should use the same environment-aware configuration discipline as the rest of the application.

---

# 7. `env.py`

`env.py` is one of the most important Alembic files.

It controls how Alembic:

- obtains database configuration
- builds or receives SQLAlchemy connectivity
- runs online migrations
- generates SQL in offline mode
- receives `target_metadata`
- configures Alembic's migration context

For an ORM-based project, metadata often comes from the declarative base:

```python
from myapp.models import Base

target_metadata = Base.metadata
```

But ORM models are not the only possible metadata source. SQLAlchemy Core `MetaData` objects can also be supplied.

The key relationship is:

```text
SQLAlchemy model/table definitions
        ↓
MetaData
        ↓
target_metadata
        ↓
Alembic autogenerate
```

### Why Alembic needs metadata

Autogenerate needs a representation of what your application says the schema should look like.

It then compares that against the current database schema and proposes operations.

### Environment modes

Conceptually:

```text
env.py
 ├── online mode → connect and execute
 └── offline mode → generate SQL text
```

Do not think of `env.py` as boilerplate you never need to understand. It is the bridge between your application/database configuration and the migration engine.

---

# 8. Connecting Alembic to Application Settings

A production-oriented design uses the same settings source that the application uses.

For example:

```python
from sqlalchemy import engine_from_config, pool
from alembic import context

from myapp.settings import load_database_settings
from myapp.models import Base


config = context.config
settings = load_database_settings()

config.set_main_option("sqlalchemy.url", settings.url)

target_metadata = Base.metadata
```

The exact configuration structure can vary by project. The architectural rule is what matters:

```text
Environment
   ↓
Validated settings
   ↓
Alembic
   ↓
Database
```

This helps because different environments naturally have different targets:

```text
local     → local PostgreSQL
CI        → ephemeral/test PostgreSQL
staging   → staging PostgreSQL
production→ production PostgreSQL
```

### Production lesson

Connection configuration should be environment-specific; migration logic should be source-controlled and environment-independent.

---

# 9. First Migration

A revision can be created with:

```bash
alembic revision -m "create customers table"
```

A revision is a versioned migration script.

Conceptually it contains:

```python
def upgrade() -> None:
    ...

def downgrade() -> None:
    ...
```

A simplified migration could be:

```python
from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("customers")
```

The `upgrade()` function describes the forward transition.

The `downgrade()` function describes the reverse transition for that revision.

### Important warning

A downgrade being syntactically possible does not mean it is operationally safe in production.

For example:

```python
op.drop_table("customers")
```

can destroy data.

Use destructive examples only against disposable/local databases.

> ⚠️ INTENTIONALLY UNSAFE / DEVELOPMENT-ONLY MIGRATION EXAMPLE

Never use a destructive downgrade as a substitute for a tested recovery plan.

---

# 10. Revision Identifiers

Every revision has an identifier.

Conceptually:

```text
base
 ↓
a1b2c3
 ↓
d4e5f6
 ↓
g7h8i9
```

Each revision points to a parent revision.

The history is therefore a graph.

That matters because teams can create parallel changes:

```text
        base
       /    \
      A      B
       \    /
       merge
```

Do not reduce the graph to “files sorted alphabetically.”

The database needs to know the migration lineage so Alembic can determine which revisions should be applied.

### Production lesson

Migration files are nodes in a dependency graph, not independent SQL snippets.

---

# 11. `upgrade`

The most common forward operation is:

```bash
alembic upgrade head
```

`head` means the latest revision reachable on the current migration branch.

Conceptually:

```text
Database at revision A
        ↓
find pending revisions
        ↓
run upgrade() for each
        ↓
record new revision
```

You can also advance incrementally where appropriate:

```bash
alembic upgrade +1
```

Think in terms of state transition:

```text
Revision A
   ↓ upgrade
Revision B
   ↓ upgrade
Revision C
```

The database schema should move through the corresponding operations.

---

# 12. `downgrade`

The common command for stepping backward one revision is:

```bash
alembic downgrade -1
```

Conceptually:

```text
Revision C
   ↓ downgrade
Revision B
```

A downgrade is useful for development and for reversibility testing, but do not assume:

```text
downgrade
=
disaster recovery
```

These are different concerns.

### Migration rollback

Attempts to reverse a known schema change.

### Application rollback

Deploys an older application version.

### Recovery

Restores the overall system to a safe operating state.

A migration may be technically reversible but operationally unsafe.

Example:

```text
drop column
```

might be reversed only by recreating the column. That does not recover the data that was deleted from that column.

### Production lesson

Always ask whether a downgrade preserves business data and application compatibility, not merely whether it executes without syntax errors.

---

# 13. `current`

Use:

```bash
alembic current
```

This answers:

> Which Alembic revision does this database currently report?

The answer is associated with the `alembic_version` table.

This is a useful first diagnostic step when a migration fails.

---

# 14. `history`

Use:

```bash
alembic history
```

This shows migration history and revision relationships.

Conceptually:

```text
base
 ↓
revision A
 ↓
revision B
 ↓
revision C
```

For branch-heavy repositories, history also helps reveal:

- branches
- parent relationships
- multiple heads
- merge revisions

### Production lesson

When debugging migration state, inspect history before guessing.

---

# 15. `alembic_version`

Alembic keeps migration bookkeeping in the database.

A conceptual query is:

```sql
SELECT version_num
FROM alembic_version;
```

The version tells Alembic which migration state the database reports.

Think:

```text
Migration graph
        ↓
current revision path
        ↓
database
        ↓
alembic_version
```

`alembic_version` is bookkeeping. It is not a substitute for inspecting the real schema.

If someone manually changes the database but does not update the migration history correctly, you can end up with:

```text
Recorded version
        ≠
Actual schema
```

That is dangerous.

---

# 16. Upgrade/Downgrade State Machine

A simple state-machine mental model is:

```text
Database at revision A
        ↓
upgrade
        ↓
revision B
        ↓
upgrade
        ↓
revision C
```

Backward:

```text
Database at revision C
        ↓
downgrade
        ↓
revision B
```

The key is that Alembic moves between known revision states.

The revision graph tells Alembic what transition steps exist.

---

# 17. SQLAlchemy MetaData and Alembic

Topic 06 introduced:

```text
MetaData
 ├── Table
 ├── Table
 └── Table
```

Alembic can use that metadata when generating migrations.

Conceptually:

```text
SQLAlchemy MetaData
      ↓
desired application-side schema
      ↓
Alembic target_metadata
      ↓
compare with database
      ↓
candidate migration
```

This is one reason understanding `MetaData`, `Table`, and `Column` before Alembic is so useful.

But metadata is still a model of the schema, not a complete statement of developer intent.

For example, metadata can tell Alembic:

```text
column exists
column does not exist
type differs
```

It may not reliably tell Alembic:

```text
“This missing column is actually the same data as the differently named new column.”
```

That requires human intent.

---

# 18. Autogenerate

Autogenerate is one of Alembic's most useful features.

The command is:

```bash
alembic revision --autogenerate -m "add customer country"
```

Its conceptual flow is:

```text
Model / MetaData change
        ↓
Alembic autogenerate
        ↓
candidate revision
        ↓
human review
        ↓
corrected migration
        ↓
apply
```

Autogenerate compares SQLAlchemy metadata with the current database schema and proposes operations.

It is a productivity tool, not an autonomous schema designer.

### Common generated operations

A simple change may produce operations corresponding to:

- add column
- remove column
- add table
- remove table
- create index
- drop index
- some type or server-default changes

Exact behavior depends on the database, metadata configuration, and migration environment.

---

# 19. Autogenerate Limitations

This is a critical production skill.

Autogenerate sees structural differences. It does not always know semantic intent.

## Rename risk

Suppose the database has:

```text
full_name
```

and the model changes to:

```text
display_name
```

A structural comparison may be interpreted as:

```text
DROP full_name
ADD display_name
```

But the developer may intend:

```text
RENAME full_name TO display_name
```

The first interpretation can lose data.

### Why intent is difficult

The database schema contains:

```text
column called full_name
```

The new metadata contains:

```text
column called display_name
```

Without additional context, “rename” is a human interpretation.

### Type changes

A type difference may be more subtle than it looks.

Examples:

```text
VARCHAR
    ↓
TEXT
```

or:

```text
INTEGER
    ↓
BIGINT
```

may have different operational, storage, or compatibility implications.

Do not accept an autogenerated type change blindly.

### Constraints

Constraints can carry business semantics.

Examples:

- unique constraints
- check constraints
- foreign keys
- not-null requirements

Review whether the migration actually preserves the intended constraint behavior.

### Server defaults

Defaults can also need deliberate review.

A Python-side default and a database server default are not the same thing.

### Production lesson

> Autogenerate proposes. Engineers decide.

---

# 20. Reviewing Generated Migrations

Every autogenerated migration should be reviewed manually.

Use this checklist:

```text
Did a rename become DROP + ADD?
Did the intended type change appear correctly?
Are defaults preserved?
Are constraints correct?
Are indexes correct?
Could any existing data be lost?
Could this operation acquire a strong lock?
Is the operation safe for the current table size?
Does it need PostgreSQL-specific SQL?
Is downgrade actually safe?
```

A review should consider both:

```text
correctness
+
operational safety
```

A migration can produce the right schema and still be unsafe to execute on a live system.

---

# 21. Schema Migration vs Data Migration

Keep these concepts distinct.

## Schema migration

Changes structure:

- create table
- add column
- drop column
- add index
- add constraint
- alter type

## Data migration

Changes existing records:

- backfill values
- normalize data
- populate derived columns
- convert data into a new representation

The difference matters because data movement can be expensive.

A simple DDL change might be:

```sql
ALTER TABLE orders
ADD COLUMN currency TEXT;
```

A data backfill might be:

```sql
UPDATE orders
SET currency = 'USD'
WHERE currency IS NULL;
```

The second operation touches existing data.

### Production lesson

When a migration includes substantial data movement, design that work separately enough to control its transaction size, rate, failure behavior, and observability.

---

# 22. Data Migration Example

Suppose:

```text
orders
------
id
total
```

You need:

```text
currency
```

A compatibility-friendly sequence is:

```text
1. Add nullable currency
2. Deploy compatible application
3. Backfill existing rows
4. Validate
5. Enforce NOT NULL if required
6. Remove temporary compatibility later
```

This is often safer than:

```sql
ALTER TABLE orders
ADD COLUMN currency TEXT NOT NULL;
```

on a large active table, especially when existing rows cannot immediately satisfy the new requirement.

The exact safe sequence depends on the PostgreSQL version, table size, default behavior, application compatibility, and workload.

Do not turn a migration into a giant one-step event merely because one SQL statement exists.

---

# 23. Migration Separation

A useful conceptual decomposition is:

```text
Schema migration
      ↓
Application compatibility
      ↓
Data backfill
      ↓
Validation
      ↓
Constraint enforcement
      ↓
Compatibility cleanup
```

The exact number of releases can vary.

The important idea is to give each risk a controlled stage.

Large backfills have different operational characteristics from metadata-only changes.

---

# 24. CI and Deployment

Migrations should be tested before production.

A conceptual flow is:

```text
Migration commit
       ↓
Code review
       ↓
CI
       ↓
Fresh PostgreSQL database
       ↓
Upgrade to head
       ↓
Application tests
       ↓
Schema verification
       ↓
Deployment
```

A migration that runs successfully on an empty database is not automatically safe on a full production database.

Therefore test both:

```text
fresh schema correctness
```

and:

```text
production-scale operational behavior
```

where practical.

---

# 25. Migration Testing

At minimum, consider these test categories.

### Fresh database

Can all migrations build the schema from empty state?

### Upgrade path

Can an earlier schema state advance to the latest state?

### Downgrade

For migrations where reversal is intended and safe, does downgrade work?

### Data preservation

Does a rename/backfill preserve values?

### Application compatibility

Can the relevant application versions work with the intermediate schema states?

### Generated SQL

Does offline SQL look correct?

### Branch history

Are revision relationships coherent?

### Operational behavior

Does the migration behave acceptably under representative table size and concurrent activity?

Remember:

```text
Migration compiles
      ≠
Migration is production-safe
```

---

# 26. Production Migration Deployment Order

A compatibility-friendly deployment often looks like:

```text
1. Expand schema
2. Deploy compatible application
3. Backfill
4. Validate
5. Switch application behavior
6. Contract old schema
```

This reduces the need for an application deployment and schema deployment to happen in exactly the same instant.

The idea is especially important in rolling deployments where old and new application instances may coexist.

---

# 27. Large Table Migrations

Table size is part of migration design.

Compare:

```text
Development
10,000 rows
```

with:

```text
Production
100,000,000 rows
```

They may have the same SQL syntax but very different operational consequences.

Consider:

- row count
- indexes
- foreign keys
- check constraints
- query traffic
- lock contention
- transaction duration
- WAL generation
- replication
- disk usage
- migration window

### Production principle

```text
Simple local operation
        ≠
safe production operation
```

---

# 28. `lock_timeout`

A migration can wait for a lock held by an application transaction.

For example:

```sql
SET lock_timeout = '5s';
```

The conceptual behavior is:

```text
Migration requests lock
        ↓
Lock unavailable
        ↓
wait
        ↓
lock_timeout reached
        ↓
migration fails
```

Why can failing be better than waiting forever?

Because a migration blocked for a long time can become part of a production incident.

Potential symptoms include:

- blocked writes
- increased latency
- growing queues
- operational uncertainty

`lock_timeout` can implement a deliberate fail-fast policy.

### Important distinction

Fail-fast does not mean successful.

It means:

> Do not silently block production indefinitely while waiting for a lock.

The value should be chosen for the system's operational requirements rather than copied as a universal number.

---

# 29. Failure-Fast Migration Pattern

A useful design is:

```text
migration attempts DDL
        ↓
lock not available
        ↓
lock_timeout
        ↓
migration exits
        ↓
operator investigates
```

Before retrying, inspect:

- active blockers
- transaction age
- workload state
- migration behavior
- whether the operation is safe to retry

Do not automatically increase the timeout until the migration eventually succeeds.

The timeout is a safety control, not a performance knob.

---

# 30. `CREATE INDEX CONCURRENTLY`

PostgreSQL supports:

```sql
CREATE INDEX CONCURRENTLY ...
```

The feature is designed to reduce interference with concurrent table activity compared with a normal index build.

That does not mean:

```text
CONCURRENTLY
=
always faster
```

Its important property here is operational interference.

It also has special transaction requirements.

A normal Alembic migration generally runs inside migration transaction context. PostgreSQL's concurrent index operation is not compatible with being treated like ordinary transactional DDL.

That means the migration requires deliberate execution strategy.

---

# 31. Alembic and Concurrent Indexes

For PostgreSQL-specific operations, explicit migration code may be appropriate.

A conceptual migration may look like:

```python
from alembic import op


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_orders_customer_id",
            "orders",
            ["customer_id"],
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_orders_customer_id",
            table_name="orders",
            postgresql_concurrently=True,
        )
```

This example is intentionally PostgreSQL-specific.

> ✅ PRODUCTION-ORIENTED MIGRATION PATTERN

Before using it in production, verify:

- the target PostgreSQL version
- Alembic/SQLAlchemy versions
- the migration transaction behavior
- failure handling
- index existence state
- operational workload

Do not blindly copy an index pattern across database backends.

---

# 32. Nullable-First Column Changes

A common compatibility-oriented sequence is:

```text
Existing table
     ↓
Add nullable column
     ↓
Deploy code that understands both states
     ↓
Backfill
     ↓
Validate
     ↓
Enforce final constraint
```

Why is this useful?

Because application deployment and data migration can be separated.

For example, the application may temporarily support:

```text
currency IS NULL
```

while the data is being backfilled.

Once validation proves:

```text
no NULL values remain
```

a later step can enforce:

```text
NOT NULL
```

The exact database operation should be evaluated against the table size and traffic.

---

# 33. Batched Backfills

A backfill of millions of rows can be a serious operational workload.

Avoid assuming that this is harmless:

```sql
UPDATE orders
SET currency = 'USD'
WHERE currency IS NULL;
```

on a huge production table.

Potential effects include:

- a long transaction
- high WAL volume
- increased I/O
- replication lag
- lock contention
- large rollback scope
- increased application latency

Instead, use bounded batches.

Conceptually:

```text
Read a bounded range
        ↓
Update that range
        ↓
Commit
        ↓
Observe
        ↓
Next range
```

A keyset/range approach is often easier to reason about than a constantly shifting offset.

Example:

```sql
UPDATE orders
SET currency = 'USD'
WHERE id > :last_id
  AND id <= :next_id
  AND currency IS NULL;
```

The exact batching strategy depends on keys, indexes, write concurrency, and correctness requirements.

---

# 34. Backfill Strategy

A production backfill needs more than a loop.

Think about:

### Progress

How do you know where the job is?

### Checkpoints

What state lets you resume?

### Idempotency

What happens if a batch is retried?

### Failure handling

What happens after one batch fails?

### Validation

How do you prove the backfill is complete?

### Rate

What keeps the backfill from overwhelming the database?

A useful conceptual loop is:

```text
Choose batch
   ↓
Apply batch
   ↓
Commit
   ↓
Record progress
   ↓
Measure impact
   ↓
Repeat
```

This is migration safety thinking, not a full ingestion framework.

---

# 35. Expand and Contract

Expand-and-contract is one of the most important zero-downtime schema-evolution patterns.

The core idea is:

```text
EXPAND
Add new structure
      ↓
DUAL WRITE / BACKFILL
      ↓
SWITCH READERS
      ↓
VERIFY
      ↓
CONTRACT
Remove old structure
```

Why?

Because an actively deployed system may have multiple application versions running at once.

You want each intermediate schema to remain compatible enough for the deployment sequence.

---

# 36. Zero-Downtime Column Rename

Suppose:

```text
customers.full_name
```

should become:

```text
customers.display_name
```

A simple rename:

```sql
ALTER TABLE customers
RENAME COLUMN full_name TO display_name;
```

may be correct at the schema level, but it can be incompatible with an application version that still queries `full_name`.

A compatibility-oriented sequence is:

```text
1. Add display_name
2. Deploy code that can write both
3. Backfill display_name
4. Switch reads to display_name
5. Stop writing full_name
6. Remove full_name later
```

The exact dual-write mechanism belongs to the application design.

The database migration is only one part of the rollout.

### Production lesson

Zero-downtime migration is a coordination problem across:

```text
database
+
application
+
deployment system
+
data movement
```

---

# 37. Zero-Downtime Column Removal

Removal is usually a late step.

A compatibility-oriented sequence is:

```text
Stop application reads
        ↓
Stop application writes
        ↓
Verify dependencies are gone
        ↓
Drop old column
```

Dropping too early creates a hard dependency between schema deployment and application rollout.

Keep the old structure until there is evidence that it is no longer needed.

---

# 38. Offline Mode

Alembic can generate SQL without connecting to the target database.

A common command is:

```bash
alembic upgrade head --sql
```

Conceptually:

```text
Migration files
      ↓
Alembic offline mode
      ↓
Generated SQL
      ↓
Human review
      ↓
Controlled execution
```

This can be valuable when:

- DBAs review SQL
- change control requires pre-generated SQL
- production execution is performed by another system
- operators need to inspect DDL before execution

Offline SQL should be treated as an output artifact for review, not as a guarantee that the production operation is safe.

---

# 39. Offline SQL vs Online Execution

| Mode | Purpose |
| --- | --- |
| Online | Connect to database and execute migration |
| Offline | Generate SQL text for review or controlled external execution |

Online:

```text
Alembic → database
```

Offline:

```text
Alembic → SQL text
```

The migration logic is still the source of intent.

The offline output is a representation of what Alembic plans to emit.

### Production lesson

When review matters, inspect the actual SQL that will be applied instead of reviewing only Python syntax.

---

# 40. Migration Branches

Two developers can create revisions from the same parent.

For example:

```text
        base
       /    \
      A      B
```

Now the repository has two heads.

This is not automatically a bug.

It is a consequence of parallel development.

The important question is:

```text
How should these branches become a coherent migration history?
```

---

# 41. Multiple Heads and Merge Revisions

A merge revision reconciles two branches in the revision graph.

Conceptually:

```text
        base
       /    \
      A      B
       \    /
        M
```

The merge revision does not magically solve semantic schema conflicts.

For example:

- branch A adds column `x`
- branch B changes the same table in an incompatible way

A graph merge may be syntactically valid while the resulting schema intent is wrong.

Review the actual database operations.

### Production lesson

Migration graph coherence and schema correctness are related but separate review concerns.

---

# 42. `alembic stamp`

`stamp` changes Alembic's recorded revision state without running the migration operations.

For example:

```bash
alembic stamp head
```

Think:

```text
stamp
=
record this version
```

not:

```text
stamp
=
perform all migrations
```

This distinction is critical.

### Safe conceptual use

An existing database has been thoroughly verified to match revision `abc123`.

Then:

```bash
alembic stamp abc123
```

can tell Alembic:

```text
“This database is already at abc123.”
```

### Unsafe use

Do not do:

```bash
alembic stamp head
```

just because Alembic reports that migrations are pending.

If the schema does not actually match the stamped revision, you have made the recorded state less trustworthy.

---

# 43. Existing Database Adoption

Suppose a database already exists before Alembic is introduced.

The adoption problem is:

```text
Existing real schema
        ≠
existing migration history
```

The safe conceptual process is:

```text
Inspect existing schema
        ↓
Determine the intended baseline revision
        ↓
Verify actual schema matches it
        ↓
Stamp that revision
        ↓
Continue normal migration history
```

The difficult step is verification.

Do not treat `stamp` as a shortcut around unknown state.

---

# 44. Migration Graph vs Schema State

There are three distinct layers:

```text
Migration graph
=
versioned instructions

Database schema
=
actual database objects

alembic_version
=
recorded migration state
```

A healthy system keeps them aligned:

```text
Migration graph
      ↓
applied revisions
      ↓
alembic_version
      ↓
actual schema
```

A dangerous system can look like:

```text
Migration graph says: C
alembic_version says: C
database actually looks like: B
```

That situation creates false confidence.

### Production lesson

After a migration incident, inspect the database. Do not trust the recorded revision by itself.

---

# 45. Rollback Reality

A downgrade function existing in a migration file does not guarantee safe production reversibility.

Examples:

### Drop a column

```text
downgrade:
recreate column
```

The old values may already be gone.

### Data transformation

A transformation might lose information:

```text
high precision value
       ↓
rounded value
```

The previous value cannot necessarily be recovered.

### External dependencies

An application rollout may have changed behavior in ways that the old schema no longer supports.

Therefore:

```text
Can I execute downgrade?
```

is not the same question as:

```text
Can production safely recover?
```

---

# 46. Forward-Only Migrations

Some organizations treat production migrations as effectively forward-only.

This can be sensible when:

- data changes are irreversible
- distributed application versions coexist
- application rollback can be handled through compatibility rather than reversing schema
- restoring from backups is a separate disaster-recovery mechanism

This is not a universal rule.

The important decision is to define the recovery strategy explicitly.

---

# 47. Large-Table Migration Safety

Before changing a large active table, ask:

1. How many rows exist?
2. What indexes exist?
3. What queries run continuously?
4. What locks can the DDL require?
5. Could it block writes?
6. Could it block reads?
7. Could it produce substantial WAL?
8. Can `lock_timeout` protect the workload?
9. Can the change be expanded first?
10. Can the backfill be batched?
11. Can the index be built concurrently?
12. What is the recovery strategy?
13. Can old and new application versions coexist?

The migration design should be driven by these answers.

---

# 48. Production Migration Case Study

Assume:

```text
orders
10 million+ rows
```

Requirement:

```text
Add currency
```

The application must remain available.

A compatibility-oriented design is:

```text
Phase 1
Create nullable column

Phase 2
Deploy compatible application

Phase 3
Backfill in batches

Phase 4
Validate

Phase 5
Enforce final constraint

Phase 6
Create required index safely

Phase 7
Remove compatibility code later
```

Why split the work?

Because each phase solves a different problem:

| Phase | Main concern |
| --- | --- |
| Add column | schema expansion |
| Compatible deployment | application compatibility |
| Backfill | data transformation |
| Validation | correctness |
| Constraint | enforce final invariant |
| Index | query performance |
| Cleanup | remove temporary compatibility |

This is a production migration plan, not just a migration script.

---

# 49. Safe Index Migration Case Study

Requirement:

> Add an index to a heavily used production table.

Compare:

```sql
CREATE INDEX ...
```

with:

```sql
CREATE INDEX CONCURRENTLY ...
```

The relevant questions are:

- What lock behavior does each approach have?
- How much concurrent activity exists?
- Can the system tolerate waiting?
- Does the migration execution mode satisfy PostgreSQL's requirements?
- What happens if the index creation fails?
- How will you verify index state afterward?

Do not claim `CONCURRENTLY` is universally faster.

Its purpose is to reduce interference with concurrent table activity.

---

# 50. Schema vs Data Migration Case Study

### Schema change

```sql
ALTER TABLE orders
ADD COLUMN currency TEXT;
```

### Data change

```sql
UPDATE orders
SET currency = 'USD'
WHERE currency IS NULL;
```

The second statement can be operationally much more expensive on a large table.

A common mistake is to package both into one huge migration transaction without considering:

- lock duration
- WAL
- replication
- rollback size
- application load

The correct structure is workload-dependent.

---

# 51. CI Migration Gates

A production-oriented CI pipeline can look like:

```text
Migration commit
      ↓
Lint/static checks
      ↓
Fresh PostgreSQL database
      ↓
Upgrade to head
      ↓
Application tests
      ↓
Schema verification
      ↓
Optional downgrade tests
      ↓
Offline SQL generation/review
      ↓
Deploy
```

CI should catch:

- invalid migration order
- broken metadata integration
- syntax errors
- unsafe assumptions
- missing revisions
- unexpected schema state
- incompatibility between application code and schema

---

# 52. Migration Observability

Migration execution should be observable.

Useful things to watch include:

- migration duration
- lock wait
- blocked queries
- database CPU
- disk activity
- WAL pressure
- replication lag where relevant
- application error rate
- connection pressure

Do not copy generic thresholds without understanding the system.

For example, a 30-second migration may be harmless in one system and catastrophic in another.

The point is:

```text
Migration correctness
+
Migration operational safety
```

---

# 53. What If the Migration Fails Halfway?

Never guess.

Use this sequence:

```text
Migration failed
      ↓
Check current Alembic revision
      ↓
Inspect actual schema
      ↓
Inspect database errors/locks
      ↓
Determine transaction state
      ↓
Identify special non-transactional operations
      ↓
Choose retry / repair / manual intervention / forward migration
```

This is especially important when a migration includes:

- non-transactional DDL
- concurrent index operations
- data backfills
- multiple independent steps

### Production rule

> Never blindly rerun a failed migration before understanding the resulting database state.

---

# 54. Rollback vs Recovery

Think carefully about these two terms.

```text
Rollback
=
attempt to reverse a migration
```

```text
Recovery
=
restore the system to a safe operational state
```

Recovery might involve:

- a forward migration
- restoring data
- deploying a compatibility patch
- recreating a missing object
- restoring from backup
- repairing a failed concurrent index operation

The right recovery depends on what actually happened.

---

# 55. Production Migration Strategy

A reusable strategy is:

```text
1. Design
2. Review
3. Test
4. Generate SQL
5. Assess locks
6. Expand
7. Migrate data
8. Validate
9. Contract
10. Observe
```

### Design

Define the target schema state.

### Review

Identify data-loss, compatibility, and locking risks.

### Test

Run against realistic PostgreSQL environments.

### Generate SQL

Use offline mode when controlled SQL inspection is required.

### Assess locks

Understand active workload and lock behavior.

### Expand

Add structures in a compatibility-friendly way.

### Migrate data

Backfill in controlled batches if needed.

### Validate

Prove that the new invariant is satisfied.

### Contract

Remove obsolete structures only after dependencies are gone.

### Observe

Monitor the system after the change.

---

# 56. Alembic vs Other Schema-Management Layers

Alembic is designed around versioned relational schema changes.

Other platform components may own other schema-evolution problems.

## Alembic

Typical role:

- PostgreSQL operational databases
- application databases
- metadata/control databases

## dbt

Typical role:

- warehouse transformations
- analytical models
- SQL-based transformation workflows

## Lakehouse table formats

Examples:

- Delta Lake
- Apache Iceberg

These often have their own schema-evolution mechanisms.

The important architecture is not:

```text
One universal schema tool
```

It is:

```text
Operational PostgreSQL
        ↓
Alembic

Warehouse
        ↓
dbt / warehouse tooling

Lakehouse
        ↓
table-format schema evolution
```

Exact ownership depends on platform architecture.

Do not rank these systems against one another. They solve different classes of problems.

---

# 57. Alembic in the Data Platform

A data platform can legitimately contain several schema-management layers:

```text
Operational metadata DB
        ↓
Alembic

Warehouse models
        ↓
dbt / warehouse tooling

Lakehouse tables
        ↓
table-format schema evolution
```

An engineering team should define ownership boundaries.

For example:

- Alembic owns the operational PostgreSQL schema.
- dbt owns analytical transformation models.
- the lakehouse table format owns its table metadata evolution.

This separation avoids trying to force one migration model onto every storage system.

---

# 58. Alembic vs `metadata.create_all()`

You learned in Topic 06 that:

```python
metadata.create_all(engine)
```

can create missing database objects.

That remains useful for:

- controlled local setup
- disposable tests
- experiments
- simple environments where migrations are intentionally out of scope

Alembic is different.

It provides:

- explicit version history
- controlled evolution
- reviewable operations
- production migration sequencing
- deployment tracking

Think:

```text
create_all()
=
create what is missing

Alembic
=
move from known schema state
to another known schema state
```

Do not claim `create_all()` should never be used.

Use it where its semantics fit.

---

# 59. Alembic vs ORM

The responsibilities are different.

```text
ORM
=
runtime object mapping
```

```text
Alembic
=
schema change history
```

Changing:

```python
class Customer(Base):
    country: Mapped[str]
```

does not automatically modify the production database.

You still need a migration.

The normal relationship is:

```text
ORM model
   ↓
MetaData
   ↓
Alembic
   ↓
database schema
```

---

# 60. Migration Code Review Checklist

## Correctness

- Does the migration represent the intended schema change?
- Did a rename accidentally become drop + add?
- Are existing data values preserved?
- Are types correct?
- Are constraints correct?
- Are defaults correct?

## Safety

- Could this DDL block a large table?
- Should `lock_timeout` be used?
- Should an index be created concurrently?
- Does a backfill need to be batched?
- Is transaction scope appropriate?

## Deployment

- Can old and new application versions coexist?
- Does the change require expand-and-contract?
- Can compatibility be staged across releases?

## Recovery

- Is downgrade actually safe?
- What happens if the migration fails?
- Is a forward recovery path defined?

## Operational

- How long might this run?
- What metrics will be watched?
- How will the database state be verified?

---

# 61. Debugging Exercises

## Problem 1 — Alembic cannot connect

**Observed symptom**

```text
connection refused
```

**Root causes to inspect**

- wrong environment variable
- wrong database host
- wrong port
- incorrect credentials
- `env.py` configuration bug

**Correct process**

```text
settings
  ↓
env.py
  ↓
SQLAlchemy connection
  ↓
PostgreSQL
```

Do not modify migration logic until connectivity is proven.

---

## Problem 2 — `target_metadata` is missing

**Observed symptom**

Autogenerate does not detect model changes.

**Root cause**

Alembic was not given the intended SQLAlchemy metadata.

**Fix**

Ensure the relevant metadata is imported and exposed:

```python
from myapp.models import Base

target_metadata = Base.metadata
```

---

## Problem 3 — Rename generated as drop + add

**Observed symptom**

Autogenerate proposes:

```text
DROP full_name
ADD display_name
```

**Root cause**

Structural diff does not necessarily reveal semantic rename intent.

**Fix**

Write the intended rename explicitly and verify data preservation.

---

## Problem 4 — Migration blocks production

**Observed symptom**

Migration sits waiting for a lock.

**Root cause**

Active transactions are holding conflicting locks.

**Fix**

Inspect blockers and consider a deliberate `lock_timeout` policy.

---

## Problem 5 — Index creation interferes with production

**Observed symptom**

Index migration creates unacceptable operational impact.

**Root cause**

The index operation was treated like ordinary DDL without workload-aware strategy.

**Fix**

Evaluate `CREATE INDEX CONCURRENTLY` and its special execution requirements.

---

## Problem 6 — Backfill overloads PostgreSQL

**Observed symptom**

Database resource usage spikes.

**Root causes**

- enormous batch
- long transaction
- too much concurrent application traffic
- excessive WAL generation

**Fix**

Reduce batch size, bound transaction scope, and observe impact.

---

## Problem 7 — Downgrade would destroy data

**Observed symptom**

The migration's reverse operation removes information.

**Root cause**

The forward migration was irreversible.

**Fix**

Define recovery separately from downgrade.

---

## Problem 8 — Multiple migration heads

**Observed symptom**

Alembic reports multiple heads.

**Root cause**

Parallel revisions branched from the same parent.

**Fix**

Inspect the graph and create an appropriate merge revision.

---

## Problem 9 — `stamp head` was used incorrectly

**Observed symptom**

Alembic thinks the database is current, but the schema is not.

**Root cause**

`stamp` changed bookkeeping without changing schema.

**Fix**

Inspect the real schema and repair the migration state explicitly.

---

## Problem 10 — Existing database does not match stamped revision

**Observed symptom**

Later migrations fail unexpectedly.

**Root cause**

The baseline revision was stamped without proving schema equivalence.

**Fix**

Compare the actual schema against the intended baseline.

---

## Problem 11 — Incompatible application deployment

**Observed symptom**

A newly deployed application queries a column that production does not yet have.

**Root cause**

Application and database changes were deployed in the wrong order.

**Fix**

Use an expand-and-contract-compatible sequence.

---

# 62. Complete Hands-On Lab

All instructions below remain inside this document so no additional artifacts are required.

## Lab 1 — Initialize Alembic

**Objective**

Understand the generated project structure.

**Setup**

Use a disposable development PostgreSQL database.

**Learner prediction**

Before running the command, predict which configuration and migration files should appear.

**Command**

```bash
alembic init migrations
```

**Expected result**

You should have an Alembic configuration and migration directory.

**Verification**

Identify:

```text
alembic.ini
migrations/env.py
migrations/versions/
```

**Debugging**

If initialization fails, inspect the working directory and Alembic installation before changing application code.

**Production takeaway**

Initialization creates tooling structure; it does not migrate production.

---

## Lab 2 — Connect `env.py` to Settings

**Objective**

Avoid hard-coded database credentials.

**Learner prediction**

Trace:

```text
environment
  ↓
settings
  ↓
env.py
  ↓
PostgreSQL
```

**Representative code**

```python
from myapp.settings import load_database_settings

settings = load_database_settings()
config.set_main_option("sqlalchemy.url", settings.url)
```

**Expected result**

Alembic uses the configured environment-specific connection target.

**Production takeaway**

Keep secrets outside the migration source.

---

## Lab 3 — First Revision

**Objective**

Create a versioned schema change.

```bash
alembic revision -m "create customers table"
```

Write a migration that creates:

```text
customers
---------
id
name
```

**Verification**

Inspect both:

```python
upgrade()
downgrade()
```

**Production takeaway**

Every revision should tell a reviewer exactly what state transition it creates.

---

## Lab 4 — Upgrade

**Objective**

Apply a revision.

```bash
alembic upgrade head
```

**Learner prediction**

Predict:

1. which `upgrade()` functions will run
2. what schema should exist
3. what revision should be recorded

**Verification**

Run:

```bash
alembic current
```

and inspect the actual database.

---

## Lab 5 — `current` and `history`

**Objective**

Understand migration state.

Run:

```bash
alembic current
alembic history
```

**Expected result**

You should be able to map:

```text
revision graph
↔
database revision
```

---

## Lab 6 — Safe Development Downgrade

**Objective**

Practice reversibility on disposable data.

```bash
alembic downgrade -1
```

**Important**

Only use a destructive downgrade on a disposable/local database.

> ⚠️ INTENTIONALLY UNSAFE / DEVELOPMENT-ONLY MIGRATION EXAMPLE

**Production takeaway**

A development downgrade is useful for testing, but production recovery may use a different strategy.

---

## Lab 7 — Add a Column

Create a revision that adds:

```text
country
```

to `customers`.

Apply it and verify the database schema.

**Production takeaway**

Simple DDL still needs versioned history.

---

## Lab 8 — Autogenerate

Change your SQLAlchemy model/metadata and run:

```bash
alembic revision --autogenerate -m "add customer status"
```

Then stop.

Do **not** immediately upgrade.

Review the generated script first.

Check:

- intended columns
- types
- constraints
- defaults
- indexes

---

## Lab 9 — Rename Column Safely

Starting state:

```text
full_name
```

Desired state:

```text
display_name
```

Steps:

1. change your metadata
2. run autogenerate
3. inspect the revision
4. identify whether it proposes drop + add
5. explain possible data loss
6. replace with an explicit rename where appropriate
7. verify existing data remains intact

**Production takeaway**

Autogenerate does not replace human intent.

---

## Lab 10 — Data Migration

Add a new nullable field.

Then backfill existing rows.

Record separately:

```text
schema operation
data operation
validation
constraint enforcement
```

**Production takeaway**

Large data changes deserve explicit operational planning.

---

## Lab 11 — Large Table

Use a representative table and perform:

```text
nullable column
   ↓
batched backfill
   ↓
validation
   ↓
final constraint
```

Measure:

- elapsed time
- batch size
- transaction duration
- database load
- application impact

Do not invent the results.

---

## Lab 12 — `lock_timeout`

Create a controlled lock scenario in a disposable environment.

Set:

```sql
SET lock_timeout = '5s';
```

Then execute a migration that needs the blocked resource.

Observe:

```text
request lock
   ↓
wait
   ↓
timeout
   ↓
failure
```

**Production takeaway**

A failed migration can be safer than a migration that silently blocks production.

---

## Lab 13 — Concurrent Index

On a PostgreSQL test table, evaluate an index migration using the concurrent option.

Inspect:

- transaction requirements
- generated SQL
- failure behavior
- resulting index

Do this in a disposable environment first.

---

## Lab 14 — Expand and Contract

Perform a controlled column evolution.

Required stages:

```text
Expand
→ compatibility
→ backfill
→ verify
→ switch reads
→ stop old writes
→ contract
```

Write down the state of the application at every stage.

---

## Lab 15 — Offline SQL

Generate SQL:

```bash
alembic upgrade head --sql
```

Inspect:

- DDL order
- index operations
- transaction assumptions
- data updates
- potentially risky operations

---

## Lab 16 — Migration Branches

Create a conceptual branch:

```text
base
├── A
└── B
```

Inspect multiple heads and reason about the correct merge.

---

## Lab 17 — `stamp`

Use an existing disposable database whose schema has been independently verified.

Then:

```bash
alembic stamp <verified_revision>
```

Verify that:

```text
schema unchanged
revision bookkeeping changed
```

---

## Lab 18 — CI Migration Validation

Design a CI gate that:

1. creates a fresh PostgreSQL database
2. upgrades all revisions
3. runs application tests
4. verifies schema
5. optionally tests safe downgrades
6. generates offline SQL for review
7. checks migration graph coherence

---

# 63. Ten-Migration Evolution Exercise

Start from an empty database and evolve it through ten realistic revisions.

A possible sequence:

```text
1. create customers
2. create orders
3. add customer country
4. add customer status
5. create customer index
6. create pipeline_runs
7. add timestamps
8. create watermarks
9. add a constraint
10. final schema refinement
```

The learner must:

1. start from an empty database
2. create ten revisions
3. upgrade to head
4. verify schema state
5. downgrade all the way where safe
6. verify schema removal
7. upgrade to head again
8. verify the final schema

The exercise demonstrates:

```text
Migration history is reproducible.
```

Do not treat “all commands completed” as sufficient. Inspect the resulting schema.

---

# 64. Column Rename Autogenerate Exercise

Initial:

```text
customers.full_name
```

Desired:

```text
customers.display_name
```

Tasks:

1. change metadata
2. run autogenerate
3. inspect generated operations
4. identify whether drop + add was proposed
5. explain the data-loss risk
6. replace with an explicit rename operation
7. execute against test data
8. verify data preservation

The most important learning outcome is not the command.

It is understanding why structural comparison cannot always infer intent.

---

# 65. Large-Table Migration Exercise

Assume:

```text
orders
10 million rows
```

Requirement:

```text
currency
```

Build a plan with:

### Step 1

Add a nullable column.

### Step 2

Deploy compatible code.

### Step 3

Backfill in bounded batches.

### Step 4

Validate that required rows are populated.

### Step 5

Enforce final `NOT NULL` or another invariant if required.

### Step 6

Create any required index using an appropriate strategy.

### Step 7

Use a deliberate `lock_timeout`.

### Step 8

Generate offline SQL.

### Step 9

Review the SQL and deployment order.

### Step 10

Write a recovery plan.

---

# 66. Expand-and-Contract Exercise

Choose a column rename or replacement.

Required sequence:

```text
1. Expand
2. Deploy compatible application
3. Dual-write where needed
4. Backfill
5. Verify
6. Switch reads
7. Stop old writes
8. Contract
9. Remove old structure
```

For every stage write:

- schema state
- application state
- data state
- rollback/recovery consideration

The goal is to make deployment compatibility explicit.

---

# 67. Branch/Merge Exercise

Start with:

```text
base
```

Developer A creates:

```text
base → A
```

Developer B creates:

```text
base → B
```

Then merge.

Tasks:

1. identify multiple heads
2. create a merge revision
3. inspect parent relationships
4. verify actual schema intent
5. explain what the merge revision does **not** guarantee

---

# 68. Offline SQL Review Exercise

Run:

```bash
alembic upgrade head --sql
```

Review the output.

Ask:

- Which tables change?
- Which indexes change?
- Are any destructive operations present?
- What lock behavior might be relevant?
- Is data movement present?
- Is transaction behavior safe?
- Can old and new application versions coexist?

This exercise trains the habit:

```text
Review actual database operations,
not only Python migration syntax.
```

---

# 69. Existing Database + Stamp Exercise

Assume a database already exists and has been verified to match:

```text
revision = abc123
```

Then:

```bash
alembic stamp abc123
```

Observe:

```text
database schema
=
unchanged

migration bookkeeping
=
updated
```

Now deliberately imagine the schema does **not** match.

Explain why stamping would create a false state.

---

# 70. Testing Strategy

A strong migration test suite has multiple layers.

## Fresh database

Apply all migrations from base.

## Upgrade path

Start from earlier revisions and advance.

## Safe downgrade

Test only migrations where reversal is known to be safe.

## Data preservation

Verify rename and backfill behavior.

## Application compatibility

Test old/new application assumptions around staged migrations.

## Large-table behavior

Use realistic data volume.

## Offline SQL

Generate and inspect SQL.

## Branch/merge

Validate a coherent revision graph.

Representative pytest-style pseudocode:

```python
def test_schema_can_upgrade_to_head(database):
    run_alembic_upgrade_head(database)

    assert table_exists(database, "customers")
    assert column_exists(database, "customers", "country")
```

Data preservation:

```python
def test_rename_preserves_data(database):
    seed_customer(database, full_name="Alice")

    run_migration(database, "rename_full_name")

    assert read_display_name(database, "Alice") == "Alice"
```

The exact testing harness is environment-specific. The important principle is to test actual PostgreSQL behavior, not only migration function imports.

---

# 71. Performance and Capacity Testing

Migration cost depends on more than SQL text.

Relevant dimensions include:

- row count
- indexes
- constraints
- storage performance
- WAL generation
- lock contention
- concurrency
- replication
- transaction duration

Do not invent timing numbers.

Instead, record actual measurements:

```text
trial
table size
batch size
elapsed time
rows/s
lock wait
WAL impact
replication effect
```

A migration that works in seconds on a development table may behave very differently at production scale.

---

# 72. Production Hardening

Think of migration maturity in levels.

## Level 1 — Basic schema change

```python
op.add_column(...)
```

## Level 2 — Reviewed migration

Human review of generated/manual operations.

## Level 3 — Environment-aware configuration

`env.py` connected to settings.

## Level 4 — Tested migration

CI applies migrations on PostgreSQL.

## Level 5 — Large-table safety

Lock awareness, batch planning, and fail-fast controls.

## Level 6 — Compatibility rollout

Expand-and-contract.

## Level 7 — Offline SQL review

Actual SQL inspected before production.

## Level 8 — Observability and recovery

Migration behavior is monitored and recovery is explicit.

Each level addresses a different risk.

---

# 73. Internal Mechanics: Applying a Migration

A conceptual execution flow is:

```text
alembic upgrade head
        ↓
load migration environment
        ↓
read current database revision
        ↓
construct migration path
        ↓
execute revision upgrade()
        ↓
update migration bookkeeping
        ↓
database reaches new schema state
```

Key pieces:

```text
env.py
revision graph
upgrade()
alembic_version
```

Keep two views separate.

### Migration instruction

```text
upgrade()
```

### Actual database state

```text
tables
columns
indexes
constraints
data
```

After a failure, verify the second one.

---

# 74. Internal Mechanics: Autogenerate

The conceptual process is:

```text
Current database schema
        +
target SQLAlchemy MetaData
        ↓
comparison
        ↓
candidate operations
        ↓
generated revision
```

Then:

```text
candidate
   ↓
human review
   ↓
correct migration
```

Autogenerate is not a proof of semantic correctness.

The classic example is:

```text
old: full_name
new: display_name
```

A structural diff can see:

```text
old column disappeared
new column appeared
```

It does not inherently know:

```text
old column should be renamed
```

---

# 75. Internal Mechanics: Expand-and-Contract

A zero-downtime-style change separates application compatibility from final schema cleanup.

```text
Old application
      ↓
Expanded schema supports old + new
      ↓
New application
      ↓
Backfill complete
      ↓
New behavior becomes primary
      ↓
Old behavior removed
      ↓
Contract schema
```

The important insight is that database migration is a sequence of compatible states, not a single SQL statement.

---

# 76. Database Size as a Migration Requirement

Migration design should explicitly include scale.

Compare:

```text
10,000 rows
```

with:

```text
100,000,000 rows
```

The same operation may have a very different impact.

At larger scale, ask:

```text
How long can it run?
How much WAL can it generate?
What locks are requested?
What traffic is blocked?
How does replication react?
Can the operation be interrupted safely?
Can it resume?
```

This is why local development success does not prove production safety.

---

# 77. Alembic Code Review Exercises

Review each migration and identify risk.

## Snippet A — Rename

```text
DROP full_name
ADD display_name
```

Ask:

- Is this a rename?
- What happens to existing values?
- Should a compatibility rollout be used?

## Snippet B — Giant backfill

```sql
UPDATE orders
SET currency = 'USD';
```

Ask:

- How many rows?
- How long can the transaction run?
- Is batching required?

## Snippet C — Index

```sql
CREATE INDEX ...
```

Ask:

- What is the table size?
- Is the table continuously active?
- Is a concurrent strategy appropriate?

## Snippet D — Immediate removal

```text
deploy new application
drop old column immediately
```

Ask:

- Are older application instances still running?
- Are hidden dependencies gone?

## Snippet E — Stamp

```bash
alembic stamp head
```

Ask:

- Does the real schema actually match head?

---

# 78. Interview Questions

## Basic

1. What is a database migration?
2. Why do teams version schema changes?
3. What is Alembic?
4. What is a revision?
5. What does `upgrade head` mean?
6. What does `downgrade -1` mean?
7. What is `alembic_version`?
8. What is `env.py`?
9. What is `alembic.ini`?
10. What is `target_metadata`?

## Intermediate

1. What does `alembic init` create?
2. Why should Alembic use environment-aware settings?
3. What does autogenerate compare?
4. Why can autogenerate be wrong about renames?
5. What is the difference between schema migration and data migration?
6. Why should migrations run in CI?
7. What does `alembic current` tell you?
8. What does `alembic history` tell you?
9. What is the purpose of offline SQL?
10. What is a migration branch?

## Advanced

1. How would you safely change a required column on a huge production table?
2. Why can `lock_timeout` be safer than waiting?
3. Why is `CREATE INDEX CONCURRENTLY` special?
4. What is expand-and-contract?
5. How would you perform a zero-downtime column rename?
6. Why can a downgrade script be misleading?
7. What does `stamp` do?
8. How do you recover after a failed migration when schema state is uncertain?
9. How would you validate Alembic's migration SQL before production?
10. When would Alembic not be the primary schema-management layer?

---

# 79. Architecture Questions

Answer these by reasoning from:

```text
schema state
+
application compatibility
+
data volume
+
locks
+
deployment order
+
recovery
+
operational visibility
```

### 1. Continuous production application

Design a migration strategy for a PostgreSQL database serving a continuously running application.

### 2. Huge required column

A production table has 100 million rows. You need to add a required field. How would you evolve the schema?

### 3. Column rename

How would you change a column name without requiring a synchronized application/database deployment?

### 4. Production index

A heavily used table needs a new index. How would you evaluate the safest implementation?

### 5. Lock wait

A migration has waited on a lock for several minutes. What should the system do?

### 6. CI

What gates would you put around migration changes?

### 7. Existing database adoption

How would you introduce Alembic to an existing production database?

### 8. Branching

Two engineers create migrations from the same parent. How do you resolve the migration graph?

### 9. Schema vs data

How do you decide whether a data backfill should be part of the schema migration?

### 10. Partial failure

A migration fails and the engineer does not know exactly what database state remains. What is your first move?

### 11. PostgreSQL and warehouse

How would you define the ownership boundary between Alembic for PostgreSQL and dbt for warehouse transformations?

---

# 80. Decision Framework

# How to Design a Safe Migration

Ask these questions in order.

## 1. What schema state is required?

Define the final target precisely.

## 2. Does existing data need modification?

Separate structural change from data movement.

## 3. What is the table size?

Use actual production characteristics.

## 4. Is the table actively serving traffic?

A maintenance-only table and an always-hot transactional table have different constraints.

## 5. What locks can occur?

Understand the DDL and workload.

## 6. Can the change be expanded first?

Look for compatibility-friendly intermediate states.

## 7. Can the backfill be batched?

Avoid unnecessarily huge transactions.

## 8. Can old and new application versions coexist?

This determines whether expand-and-contract is needed.

## 9. Is the change reversible?

Do not confuse syntax-level downgrade with data recovery.

## 10. What is the recovery plan?

Know what you will do if the migration fails.

## 11. Can the SQL be reviewed offline?

Use:

```bash
alembic upgrade head --sql
```

when controlled SQL review is useful.

## 12. How will the migration be observed?

Define what operators will watch.

The framework is:

```text
Schema design
      ↓
Application compatibility
      ↓
Lock analysis
      ↓
Data migration plan
      ↓
Deployment plan
      ↓
Recovery plan
      ↓
Observation
```

---

# 81. Common Migration Anti-Patterns

## Anti-pattern 1 — Editing an already-applied migration

**Beginner belief**

> It is easier to fix the old file.

**Actual behavior**

Existing environments may already depend on the old revision.

**Production consequence**

Migration histories diverge.

**Correct mental model**

Once a migration is part of shared/production history, create a new corrective revision instead.

---

## Anti-pattern 2 — Blindly trusting autogenerate

**Beginner belief**

> Alembic generated it, so it must be correct.

**Actual behavior**

Autogenerate detects structural differences, not every semantic intention.

**Production consequence**

Renames or subtle changes can become destructive.

**Correct mental model**

Autogenerate is a candidate generator.

---

## Anti-pattern 3 — Treating rename as drop + add

**Beginner belief**

> Both schemas contain one column, so the result is equivalent.

**Actual behavior**

Drop + add can remove the old data.

**Production consequence**

Data loss.

**Correct mental model**

Schema identity and data identity both matter.

---

## Anti-pattern 4 — Giant one-shot backfill

**Beginner belief**

> One SQL statement is simpler.

**Actual behavior**

A huge update can create a long transaction and heavy WAL/load.

**Production consequence**

Database pressure and hard recovery.

**Correct mental model**

Bound data movement.

---

## Anti-pattern 5 — DDL without lock awareness

**Beginner belief**

> DDL is metadata, so it is harmless.

**Actual behavior**

Some DDL requires significant locks or work.

**Production consequence**

Production blocking.

**Correct mental model**

Every migration is an operational workload.

---

## Anti-pattern 6 — Downgrade equals disaster recovery

**Beginner belief**

> We have `downgrade()`, so rollback is solved.

**Actual behavior**

Data loss and compatibility problems may make reversal unsafe.

**Production consequence**

False confidence.

**Correct mental model**

Rollback and recovery are separate decisions.

---

## Anti-pattern 7 — Using `stamp` to hide problems

**Beginner belief**

> Stamp head and Alembic will stop complaining.

**Actual behavior**

Only bookkeeping changes.

**Production consequence**

Migration state becomes misleading.

**Correct mental model**

Stamp only after schema equivalence is verified.

---

## Anti-pattern 8 — Breaking deployment order

**Beginner belief**

> Deploy the new application and migrate immediately.

**Actual behavior**

Old and new application instances may coexist.

**Production consequence**

Some instances query missing structures.

**Correct mental model**

Design compatible intermediate schema states.

---

## Anti-pattern 9 — Ignoring development/production scale

**Beginner belief**

> It was fast locally.

**Actual behavior**

Production has more rows and concurrent traffic.

**Production consequence**

Unexpected runtime and locking.

**Correct mental model**

Scale is a migration requirement.

---

## Anti-pattern 10 — Ignoring observability

**Beginner belief**

> The migration command returning successfully is enough.

**Actual behavior**

The application may still degrade afterward.

**Production consequence**

Hidden operational impact.

**Correct mental model**

Observe database and application effects.

---

## Anti-pattern 11 — Assuming `create_all()` replaces migrations

**Beginner belief**

> It creates the tables, so versioning is unnecessary.

**Actual behavior**

`create_all()` does not represent a versioned upgrade path.

**Production consequence**

Schema evolution becomes uncontrolled.

**Correct mental model**

Use each tool according to its role.

---

# 82. Debugging Decision Tree

Use this when a migration fails:

```text
Migration failed
      ↓
Check current revision
      ↓
Inspect actual schema
      ↓
Inspect locks/errors
      ↓
Determine transaction outcome
      ↓
Identify non-transactional steps
      ↓
Choose:
   retry
   repair
   manual intervention
   forward migration
```

The most important step is:

```text
Inspect actual schema
```

Do not let `alembic_version` substitute for database inspection.

---

# 83. Full Production Case Study

Assume:

```text
orders
10 million+ rows
```

Requirements:

- add `currency`
- populate existing rows
- keep application available
- add an index
- control production locks

A staged design:

```text
Phase 1
---------
Add nullable currency

Phase 2
---------
Deploy compatible application

Phase 3
---------
Backfill in bounded batches

Phase 4
---------
Validate data

Phase 5
---------
Enforce final constraint

Phase 6
---------
Create index with appropriate strategy

Phase 7
---------
Remove compatibility code later
```

During execution, observe:

```text
migration duration
lock wait
blocked queries
database resource usage
WAL
replication
application errors
```

Recovery thinking:

```text
If lock timeout occurs
    → inspect blockers

If batch fails
    → identify completed batches

If index operation fails
    → inspect index state

If application becomes incompatible
    → determine whether forward or application rollback is safer

If version state is uncertain
    → inspect schema directly
```

The point is not one universal procedure. The point is to connect schema correctness with operational safety.

---

# 84. Final Checkpoint

You should be able to demonstrate all of the following.

- [ ] Create, apply, and roll back migrations in a disposable development environment.
- [ ] Explain what `alembic.ini` does.
- [ ] Explain what `env.py` does.
- [ ] Configure Alembic from environment/application settings.
- [ ] Explain revisions and the migration graph.
- [ ] Use `upgrade`.
- [ ] Use `downgrade`.
- [ ] Use `current`.
- [ ] Use `history`.
- [ ] Explain `alembic_version`.
- [ ] Explain the relationship between SQLAlchemy `MetaData` and Alembic.
- [ ] Use autogenerate and manually review the result.
- [ ] Identify a dangerous rename generated as drop + add.
- [ ] Distinguish schema migration from data migration.
- [ ] Use `lock_timeout`.
- [ ] Explain `CREATE INDEX CONCURRENTLY`.
- [ ] Explain why concurrent index creation has special transaction requirements.
- [ ] Design nullable-first schema evolution.
- [ ] Design a batched backfill.
- [ ] Explain expand-and-contract.
- [ ] Design a zero-downtime column rename.
- [ ] Explain zero-downtime removal.
- [ ] Generate offline SQL.
- [ ] Explain branches and merge revisions.
- [ ] Explain `stamp`.
- [ ] Design CI migration gates.
- [ ] Explain why rollback and recovery are different.
- [ ] Decide whether Alembic is the appropriate schema-management layer.

The learner must demonstrate understanding through implementation and reasoning, not memorized definitions.

---

# 84. Common Mistakes

## Mistake 1 — Trusting autogenerate blindly

**Beginner belief:** “Alembic generated it, so it must be correct.”

**Actual behavior:** Autogenerate compares structural metadata and database state; it cannot reliably infer every semantic intention.

**Production consequence:** A rename can be emitted as a destructive drop/add candidate.

**Correct mental model:** Autogenerate proposes. Engineers review and decide.

## Mistake 2 — Editing an already-applied migration

**Beginner belief:** “I can change the old migration to fix production.”

**Actual behavior:** Shared environments may already depend on the existing revision.

**Production consequence:** Migration histories diverge.

**Correct mental model:** Once shared history has been applied, create a new corrective revision.

## Mistake 3 — Mixing a massive backfill into schema DDL

**Beginner belief:** “One migration file is simpler.”

**Actual behavior:** Large data changes can create long transactions, heavy WAL generation, and sustained database load.

**Production consequence:** Slow application traffic and difficult recovery.

**Correct mental model:** Stage large data movement deliberately.

## Mistake 4 — Migrating without lock awareness

**Beginner belief:** “Correct SQL is automatically safe SQL.”

**Actual behavior:** DDL can wait for locks held by live workload.

**Production consequence:** Production traffic can be blocked.

**Correct mental model:** Analyze lock behavior and use a deliberate timeout policy where appropriate.

## Mistake 5 — Assuming downgrade is disaster recovery

**Beginner belief:** “If something goes wrong, just downgrade.”

**Actual behavior:** Data loss, irreversible transformations, and application compatibility can make reversal unsafe.

**Production consequence:** A downgrade can fail to restore the system.

**Correct mental model:** Define recovery independently from downgrade.

## Mistake 6 — Using `stamp` to hide migration problems

**Beginner belief:** “Stamping head makes the database current.”

**Actual behavior:** `stamp` changes Alembic's recorded state without executing the missing migrations.

**Production consequence:** Alembic can report a false schema state.

**Correct mental model:** Stamp only after actual schema equivalence is verified.

## Mistake 7 — Designing from development-scale behavior

**Beginner belief:** “The migration was fast on my laptop.”

**Actual behavior:** Production can have millions more rows and much higher concurrency.

**Production consequence:** Unexpected lock waits, WAL pressure, and latency.

**Correct mental model:** Table size and workload are migration requirements.

## Mistake 8 — Ignoring migration observability

**Beginner belief:** “The command succeeded, so we are done.”

**Actual behavior:** The database or application can still be under stress.

**Production consequence:** Operational impact is detected too late.

**Correct mental model:** Observe and verify the migration and its effects.

## Mistake 9 — Ignoring the revision graph

**Beginner belief:** “Migration files are unrelated scripts.”

**Actual behavior:** Revisions form a dependency graph.

**Production consequence:** Multiple heads or incorrect ordering can complicate deployment.

**Correct mental model:** Treat revisions as graph nodes with explicit lineage.

## Mistake 10 — Reviewing Python but not the database operation

**Beginner belief:** “The migration code is small, so the change is safe.”

**Actual behavior:** PostgreSQL executes the resulting SQL and may acquire locks or perform substantial work.

**Production consequence:** Operational risk remains hidden.

**Correct mental model:** Review generated SQL, transaction assumptions, lock behavior, and production scale.

# 85. The Migration Mental Model

```text
Schema change
      ↓
Versioned migration
      ↓
Review
      ↓
Test
      ↓
Deploy
      ↓
Observe
      ↓
Verify
```

Then:

```text
Alembic
=
versioned instructions for schema evolution

alembic_version
=
recorded migration state

MetaData
=
desired/application-side schema representation

Database
=
actual schema state
```

And:

```text
Small table
    ≠
Large production table

Simple migration
    ≠
Zero-downtime migration
```

Finally:

```text
Schema correctness
+
application compatibility
+
operational safety
+
recovery plan
=
production-safe migration
```

---

# 86. Final Review

You should now understand:

- schema migrations
- schema-as-code
- Alembic
- `alembic.ini`
- `env.py`
- revisions
- revision graphs
- `upgrade` and `downgrade`
- `current` and `history`
- `alembic_version`
- SQLAlchemy metadata integration
- autogenerate
- autogenerate limitations
- manual migration review
- schema vs data migrations
- CI/CD migration gates
- deployment compatibility
- large-table safety
- `lock_timeout`
- concurrent indexes
- nullable-first changes
- batched backfills
- expand-and-contract
- offline SQL
- branches and merges
- `stamp`
- rollback vs recovery
- Alembic vs `metadata.create_all()`
- Alembic vs ORM
- Alembic vs dbt and lakehouse table formats

## What You Can Implement

You should be able to:

- initialize Alembic
- connect it to application settings
- create revisions
- apply revisions
- inspect migration state
- review autogenerated operations
- write manual migration operations
- design large-table schema changes
- batch data backfills
- implement compatibility-friendly schema evolution
- generate offline SQL
- reason about revision branches
- adopt Alembic into an existing database
- design CI validation

## What You Can Debug

You should be able to investigate:

- failed connections
- missing metadata
- destructive autogenerate output
- blocked DDL
- unsafe index creation
- heavy backfills
- unsafe downgrades
- multiple migration heads
- incorrect stamps
- application/schema incompatibility
- unknown database state after failure

## What Comes Next

Topic 09 focuses on high-performance bulk loading with `COPY` and `executemany`.

Do not treat the backfill patterns in this topic as a replacement for the bulk-loading techniques covered next.

---

# 87. Production Rules to Remember

1. Treat schema changes as versioned code.
2. Never edit a migration that has already been applied to shared/production environments.
3. Review autogenerated migrations manually.
4. Never assume a rename will be inferred safely.
5. Separate schema changes from large data backfills when practical.
6. Consider table size and traffic before designing a migration.
7. Use `lock_timeout` where failing fast is safer than blocking production.
8. Understand when `CREATE INDEX CONCURRENTLY` is appropriate.
9. Prefer compatibility-friendly expand-and-contract changes for zero-downtime evolution.
10. Test migrations in CI.
11. Generate offline SQL when controlled review is required.
12. Understand migration branches and merge revisions.
13. Never use `stamp` to hide an unknown or mismatched schema state.
14. Treat downgrade as a schema operation, not automatically as a disaster-recovery mechanism.
15. Always know the actual database state after a failure.
16. Observe migrations during production execution.
17. Use Alembic where runtime relational schema evolution requires versioned migrations.

---

# 88. The Most Important Engineering Distinction

A migration has two dimensions:

```text
1. Does it produce the correct schema?
2. Can it safely change production without causing unacceptable impact?
```

Therefore:

```text
Correct SQL
      ≠
Safe migration
```

For every significant schema change, ask:

```text
What is changing?
Who depends on it?
How much data exists?
What locks are involved?
Can old and new application versions coexist?
Is data preserved?
Can the change be reversed?
What happens if it fails?
How do I recover?
How do I observe it?
```

A mature production change often looks like:

```text
Design
  →
Review
  →
Test
  →
Expand
  →
Migrate data
  →
Verify
  →
Contract
  →
Observe
  →
Recover if necessary
```

---

# 89. Final Engineering Mindset

Do not ask only:

> “How do I run an Alembic migration?”

Ask:

> “What schema state do I need?”

> “How does the application remain compatible?”

> “What will this do to a large live table?”

> “What locks might occur?”

> “How do I make the change incrementally?”

> “How do I recover if it fails?”

> “How do I prove the migration is safe?”

That mindset is what separates a migration command from production-grade schema evolution.

The learner should now be prepared to defend migration decisions in:

- production planning
- code reviews
- architecture reviews
- CI/CD design
- incident investigations
- database change reviews
- Data Engineering interviews
