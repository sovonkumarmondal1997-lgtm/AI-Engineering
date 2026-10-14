# Roadmap — Module 2C.6: dbt and Analytics Engineering

This is the learning roadmap for the sixth module of Stage 2C, **Data
Engineering_3**. It tells you **what** to learn about dbt and analytics
engineering, **in what order**, **how** to learn each topic, and **how to
prove to yourself** that you have learned it before you move on.

Stage 2 Module 2.12 introduced dbt in a single lesson. That was enough to
read a dbt project. It is not enough to **own** one. In most modern data
teams, the warehouse transformation layer — the part between raw tables and
dashboards — is built in dbt, and the people who build it are called
**analytics engineers**: part data engineer (version control, testing,
CI/CD, performance) and part analyst (business logic, metrics, modelling).

dbt turns SQL `SELECT` statements into a tested, documented, version-
controlled dependency graph of tables and views. This module teaches dbt
in depth, from project structure to production deployment and the semantic
layer, using Python and SQL.

---

## 1. Module outcome

By the end of this module you will be able to:

- Structure a dbt project with staging, intermediate, and mart layers, and
  choose **materialisations** deliberately.
- Define **sources**, **seeds**, **snapshots (SCD2)**, and **incremental
  models** with correct strategies.
- Use **Jinja**, macros, packages, and project variables to remove
  repetition without making code unreadable.
- Write generic and singular **tests**, enforce **model contracts**,
  versions, and access modifiers.
- Generate **documentation**, lineage, and **exposures**.
- Make dbt runs faster and cheaper with state selection, **slim CI**, and
  tuning.
- Define metrics with the **dbt Semantic Layer / MetricFlow**.
- Deploy dbt with **Airflow**, dbt Cloud, or other orchestrators.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| SQL: CTEs, joins, window functions, MERGE | Stage 2 — Module 2.6 | dbt models are SQL |
| Dimensional modelling, SCDs, star schemas | Stage 2 — Module 2.8 | What marts and snapshots implement |
| Incremental processing, dedup, late data | Stage 2 — Module 2.12 | Incremental models |
| dbt fundamentals (one lesson) | Stage 2 — Module 2.12 Topic 09 | The starting point |
| Data quality and contracts | Stage 2 — Module 2.11 | dbt tests and contracts |
| Testing pipelines | Stage 2 — Module 2.19 | CI for dbt |
| CI/CD and environments | Stage 2 — Module 2.18 | Slim CI, deploys |
| Airflow | Stage 2 — Module 2.13 | Running dbt from Airflow |
| A warehouse: Snowflake / BigQuery / Databricks / DuckDB | Modules 2C.3–2C.5; Stage 2B | dbt runs *on* one |
| Python packaging and Git | Stage 1 | dbt-core install, branches, PRs |

**Tools needed:**

- Python 3.12+ in a `uv` project: `uv add dbt-core dbt-duckdb sqlfluff
  pytest` (use **DuckDB** locally; add `dbt-snowflake`, `dbt-bigquery`, or
  `dbt-databricks` if you have accounts).
- Git, a pre-commit setup with SQLFluff, and optionally a free dbt Cloud
  developer account.
- A sample dataset (e.g., jaffle-shop style orders, customers, payments).

**A note on versions:** dbt Core 1.x continues to evolve (contracts,
unit tests, microbatch incremental, the Fusion engine and the new
authoring layer). Check the version you install before following older
tutorials.

---

## 3. How the module is organised

The eight topics are grouped into four phases. Work through them **in
order**.

```text
Phase A — Building Models                            (Basics → Intermediate)
  01 Project structure and materialisations
  02 Sources, seeds, snapshots, and incremental models

Phase B — Reusable Code                              (Intermediate)
  03 Jinja, macros, and packages

Phase C — Trust and Communication                    (Intermediate → Advanced)
  04 Tests, contracts, and model governance
  05 Documentation, lineage, and exposures

Phase D — Production                                 (Advanced)
  06 Performance and slim CI
  07 Semantic Layer and MetricFlow
  08 Deploying dbt with Airflow and dbt Cloud

Consolidate
  Module mini-project: a tested, documented analytics warehouse
```

The dependency chain:

```text
01 ► 02 ► 03 ► 04 ► 05 ► 06 ► 07 ► 08
build  load   DRY   prove  show  fast  one    ship it
models history code  it    it    & cheap source
                                          of truth
                                          for metrics
```

Why this order:

- Models (01–02) are the substance; macros (03) reduce repetition once you
  have something repeated.
- Tests (04) and docs (05) turn models into a trusted product.
- Performance (06), metrics (07), and deployment (08) take it to
  production.

---

## 4. Suggested schedule

About **4–5 weeks at 8 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — structure and materialisations · Topic 02 — sources, seeds, snapshots, incremental |
| 2 | Topic 03 — Jinja, macros, packages · Topic 04 — tests and contracts |
| 3 | Topic 05 — docs and lineage · Topic 06 — performance and slim CI |
| 4 | Topic 07 — Semantic Layer · Topic 08 — deployment |
| 5 | Mini-project and review |

---

## 5. How to study every topic (the analytics engineering loop)

```text
Read → Sketch the DAG → Write the model → Run it → Test it → Document it
→ Open a PR → Let CI build it → Review the diff → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Sketch the DAG**: which sources, which layers, which grain.
3. **Write the model** as a single readable `SELECT` with CTEs.
4. **Run it** with `dbt build --select` and inspect the compiled SQL in
   `target/`.
5. **Test it**: not-null, unique, relationships, accepted values, and at
   least one business rule.
6. **Document it**: description for the model and every key column.
7. **Open a PR** from a branch; let CI run with state selection.
8. **Review the diff** of row counts and values (data diffs).
9. **Write it down** in `module-2c6-notes.md`.
10. **Explain aloud** why each model exists and what it guarantees.

Keep one `dbt_lab/` project:

```text
dbt_lab/
├── dbt_project.yml
├── profiles.yml            # git-ignored; use env vars for credentials
├── models/
│   ├── staging/            # one model per source table
│   ├── intermediate/       # joins and reusable logic
│   └── marts/              # facts and dimensions
├── seeds/
├── snapshots/
├── macros/
├── tests/                  # singular tests
├── analyses/
├── packages.yml
└── .github/workflows/      # CI with slim builds
```

---

## 6. Phase A — Building Models (Basics → Intermediate)

### Topic 01 — [dbt project structure and materializations](01-dbt-project-structure-and-materializations.md)

**Why it comes first:** project structure and materialisation choices
determine readability, cost, and speed for the life of the project.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What dbt does (the "T" in ELT): compiles SQL + Jinja, runs it in the warehouse, builds a DAG; what it does **not** do (extract/load, scheduling) |
| Basics | Installing dbt Core and an adapter; `dbt init`, `dbt_project.yml`, `profiles.yml`, targets (dev/prod) |
| Basics | Models as `SELECT` statements; `ref()` and the DAG; the commands `run`, `test`, `build`, `compile`, `show`, `docs` |
| Basics | Node selection: `--select`, `+model`, `model+`, tags, paths, `--exclude`, `--select state:modified+` |
| Intermediate | **Layered structure**: staging (rename, cast, one-to-one with sources) → intermediate (joins, business logic) → marts (facts, dimensions); naming conventions (`stg_`, `int_`, `fct_`, `dim_`) |
| Intermediate | **Materialisations**: `view`, `table`, `incremental`, `ephemeral`, and materialised view; trade-offs of build time, query time, and cost |
| Intermediate | Configs at project, folder, and model level; schemas, aliases, and `generate_schema_name` for dev isolation |
| Intermediate | Style: CTEs over subqueries, one grain per model, SQLFluff linting |
| Advanced | Dimensional modelling in dbt (links to Module 2.8): grain, surrogate keys (`generate_surrogate_key`), conformed dimensions |
| Advanced | Multi-project and multi-environment setups; custom schemas per layer; `dbt-mesh` ideas (cross-project refs) |
| Advanced | Python models (Snowpark/PySpark/BigQuery DataFrames) and when SQL is still better |
| Advanced | Anti-patterns: giant models, circular logic, business logic in staging, `SELECT *` into marts |

**How to learn it**

1. Read the topic file.
2. Take the jaffle-shop raw tables and plan the layers on paper: list
   staging models, two intermediate models, three marts, and the grain of
   each.
3. For each model, choose a materialisation and justify it.

**Hands-on exercise — `experiments/01_structure/`**

1. Initialise a project on DuckDB; build staging models for orders,
   customers, and payments.
2. Build `int_orders_payments` and marts `fct_orders` and `dim_customers`.
3. Change a materialisation from view to table and record build/query
   effects.
4. Use `--select` forms to run only a model and its parents/children.
5. Add SQLFluff and fix all lint errors.

**Checkpoint — you are ready to move on when you can:**

- [ ] Explain what dbt does and does not do.
- [ ] Build a layered project with correct naming and grain.
- [ ] Choose a materialisation and defend it.
- [ ] Use node selection fluently.

**Common mistakes:** one 800-line model; joining in staging; everything
as a table (slow builds) or everything as a view (slow queries); no
consistent grain.

---

### Topic 02 — [Sources, seeds, snapshots, and incremental models](02-sources-seeds-snapshots-and-incremental-models.md)

**Why here:** the next step beyond static models is handling raw inputs,
history, and large tables that cannot be rebuilt every day.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Sources**: `sources.yml`, `source()`, descriptions, and the raw layer boundary |
| Basics | **Source freshness**: `loaded_at_field`, `warn_after`/`error_after`, and `dbt source freshness` |
| Basics | **Seeds**: small CSV reference data; `dbt seed`; when seeds are appropriate and when they are not |
| Intermediate | **Snapshots** for SCD Type 2: `timestamp` and `check` strategies, `unique_key`, `valid_from`/`valid_to` (`dbt_valid_from`/`dbt_valid_to`), hard deletes |
| Intermediate | **Incremental models**: `is_incremental()`, `{{ this }}`, `unique_key`, and the filter on a watermark |
| Intermediate | **Incremental strategies**: `append`, `merge`, `delete+insert`, `insert_overwrite`, and **microbatch** (time-based batches) — which adapters support which |
| Intermediate | Full refresh (`--full-refresh`) and `on_schema_change` (`ignore`, `append_new_columns`, `sync_all_columns`, `fail`) |
| Advanced | Handling late-arriving data with lookback windows (links to Module 2.12 Topic 04) |
| Advanced | Idempotent incremental design: deterministic keys, dedup before merge, and safe backfills |
| Advanced | Snapshot design pitfalls: unreliable `updated_at`, snapshot-of-snapshot, and building SCD2 dimensions from snapshots |
| Advanced | Large-table patterns: partition + cluster configs, `incremental_predicates` |
| Advanced | When to avoid dbt incremental: streaming/very low latency needs (use dynamic tables or streaming engines, Module 2C.3) |

**How to learn it**

1. Read the topic file.
2. For a 500 million-row events table, decide on a strategy: watermark
   column, unique key, lookback, and failure recovery.
3. Sketch how a snapshot records a customer address change.

**Hands-on exercise — `experiments/02_sources_incremental/`**

1. Declare sources with freshness checks; simulate a stale source and see
   the failure.
2. Build an incremental `fct_events` using `merge`; load day 1, day 2, and
   a late-arriving row; verify no duplicates.
3. Add a lookback window and prove late data is captured.
4. Create a snapshot of customers using the `check` strategy; mutate the
   source and inspect history rows.
5. Trigger a schema change in the source and compare `on_schema_change`
   settings.
6. Run `--full-refresh` and verify identical results.

**Checkpoint:**

- [ ] Declare sources and freshness.
- [ ] Choose an incremental strategy and write a correct incremental model.
- [ ] Build and use snapshots for SCD2.
- [ ] Prove an incremental model equals a full refresh.

**Common mistakes:** incremental models without a unique key; filtering on
a non-monotonic column; trusting `updated_at` blindly; snapshotting
volatile derived data.

---

## 7. Phase B — Reusable Code (Intermediate)

### Topic 03 — [Jinja, macros, and packages](03-jinja-macros-and-packages.md)

**Why here:** once you have many models, repetition appears. Jinja and
macros fix it — but they are easy to overuse.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Jinja basics: `{{ }}` expressions, `{% %}` statements, `{# #}` comments, variables, `if`, `for` |
| Basics | The compile step: seeing what Jinja produces in `target/compiled/` |
| Basics | Built-ins: `ref`, `source`, `config`, `var`, `env_var`, `this`, `target`, `is_incremental()` |
| Intermediate | **Macros**: arguments, defaults, return values, and calling macros from models |
| Intermediate | Loops for repetitive SQL (`pivot` columns, unions of many sources) and `dbt_utils.get_column_values` |
| Intermediate | **Packages**: `packages.yml`, `dbt deps`; essentials like `dbt_utils`, `dbt_expectations`, `audit_helper`, `codegen` |
| Intermediate | Project variables (`--vars`), environment variables, and secrets handling |
| Advanced | Cross-database macros with `adapter.dispatch`; overriding built-in macros (`generate_schema_name`, `generate_alias_name`) |
| Advanced | **Hooks** (`pre-hook`, `post-hook`, `on-run-start/end`) for grants and audit logging; operations with `dbt run-operation` |
| Advanced | Writing and testing your own package; versioning and publishing internally |
| Advanced | Balancing DRY and readability; macro anti-patterns; testing macros |
| Advanced | `run_query` and `statement` blocks: when dynamic SQL generation is justified |

**How to learn it**

1. Read the topic file.
2. Find three repeated SQL patterns in your lab and decide which deserve
   macros.
3. Read the source of two `dbt_utils` macros.

**Hands-on exercise — `experiments/03_macros/`**

1. Write a macro that converts cents to dollars with rounding; use it in
   five models.
2. Write a macro that pivots payment methods using a loop and
   `get_column_values`.
3. Install `dbt_utils` and `dbt_expectations`; use two tests and one macro.
4. Override `generate_schema_name` so each developer gets an isolated
   schema.
5. Add a post-hook that grants select to a role.
6. Write a macro unit test using a small seed.

**Checkpoint:**

- [ ] Read and write Jinja in dbt.
- [ ] Create and test macros.
- [ ] Use packages responsibly.
- [ ] Decide when not to write a macro.

**Common mistakes:** macros that hide business logic; deep nested Jinja
nobody can read; unpinned package versions; secrets in `vars`.

---

## 8. Phase C — Trust and Communication (Intermediate → Advanced)

### Topic 04 — [Tests, contracts, and model governance](04-tests-contracts-and-model-governance.md)

**Why here:** transformation code without tests is a liability. This topic
turns dbt models into products with guarantees (extending Module 2.11).

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Generic tests**: `unique`, `not_null`, `accepted_values`, `relationships`; configuring severity (`warn`/`error`) |
| Basics | **Singular tests**: custom SQL files that return failing rows |
| Basics | Running tests: `dbt test`, `dbt build`, test selection, `--store-failures` |
| Intermediate | **Custom generic tests** with Jinja; `dbt_expectations` (distribution, regex, row counts) |
| Intermediate | Test design: primary key tests on every model, relationship tests on foreign keys, business-rule tests on marts; thresholds (`warn_if`, `error_if`, `limit`) |
| Intermediate | **Unit tests** (dbt 1.8+): `given`/`expect` fixtures for model logic without real data |
| Intermediate | **Model contracts**: `contract: enforced`, declared column names, types, and constraints (`not_null`, `primary_key`) |
| Advanced | **Model versions** (`latest_version`, `deprecation_date`) for safe breaking changes |
| Advanced | **Access modifiers** (`public`, `protected`, `private`) and **groups** for ownership; cross-project refs in dbt Mesh |
| Advanced | Monitoring test results over time: `store_failures`, `dbt-artifacts`, Elementary, and surfacing results to alerting |
| Advanced | Test cost and speed: sampling tests, running heavy tests on schedule, and `dbt build` ordering |
| Advanced | Combining dbt tests with external tools (Great Expectations, Soda — Module 2.11) and data contracts with producers |

**How to learn it**

1. Read the topic file.
2. For `fct_orders`, list the guarantees consumers expect and the test for
   each.
3. Decide which tests block deployment and which only warn.

**Hands-on exercise — `experiments/04_tests_contracts/`**

1. Add unique/not-null/relationship tests to all marts; break each on
   purpose.
2. Write a singular test (e.g., "order total equals sum of items") and a
   custom generic test.
3. Add a unit test for a CASE-heavy model with `given`/`expect`.
4. Enforce a contract on `fct_orders`; change a column type and see the
   build fail.
5. Create `v2` of a model with a breaking change and a deprecation date.
6. Store failures and build a small report of recurring failures.

**Checkpoint:**

- [ ] Choose the right tests for each model.
- [ ] Write unit tests and enforce contracts.
- [ ] Use versions and access modifiers for safe change.
- [ ] Decide test severity and gating.

**Common mistakes:** testing only that columns are not null; tests that
always warn and are ignored; contracts missing on public models;
breaking a public model without versioning.

---

### Topic 05 — [Documentation, lineage, and exposures](05-documentation-lineage-and-exposures.md)

**Why here:** documentation and lineage let people trust and find your
work. Exposures connect models to the dashboards and apps that depend on
them.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `description` fields in YAML for models, columns, sources; `dbt docs generate` and `dbt docs serve` |
| Basics | The lineage graph (DAG) in the docs site; navigating upstream and downstream |
| Basics | Doc blocks (`{% docs %}`) for reusable text; markdown in descriptions |
| Intermediate | **Exposures**: declaring dashboards, ML models, and apps that consume models, with owner and maturity |
| Intermediate | **Meta** and **tags** for ownership, PII flags, SLAs, and domain; `meta` driving governance automation |
| Intermediate | `persist_docs` to push descriptions into warehouse column comments (so BI tools see them) |
| Intermediate | Documentation coverage checks in CI (`dbt-project-evaluator`, `dbt-checkpoint`) |
| Advanced | Artifacts: `manifest.json`, `catalog.json`, `run_results.json`; parsing them for custom lineage, impact analysis, and reports |
| Advanced | Column-level lineage (dbt Cloud Explorer) and OpenLineage integration (links to Module 2.20) |
| Advanced | Hosting docs (static site on object storage / dbt Cloud) and keeping them current |
| Advanced | Documentation culture: writing for consumers, ownership, deprecation notices |
| Advanced | Publishing to a catalogue (Purview, DataHub, OpenMetadata, Dataplex) from dbt metadata |

**How to learn it**

1. Read the topic file.
2. Write descriptions for every mart column as if for a new analyst.
3. List the dashboards that would break if `fct_orders` changed.

**Hands-on exercise — `experiments/05_docs_lineage/`**

1. Document all models and columns; add a doc block for a metric
   definition used in several places.
2. Declare two exposures (a dashboard and an ML feature set).
3. Enable `persist_docs` and verify column comments in the warehouse.
4. Use `dbt-project-evaluator` and fix the top findings.
5. Parse `manifest.json` to produce a list of models with no owner, no
   tests, or no description.

**Checkpoint:**

- [ ] Produce docs and explain lineage.
- [ ] Declare exposures and ownership.
- [ ] Automate documentation coverage in CI.
- [ ] Use artifacts for impact analysis.

**Common mistakes:** docs written once and never updated; no ownership
metadata; ignoring downstream consumers when changing models.

---

## 9. Phase D — Production (Advanced)

### Topic 06 — [dbt performance and slim CI](06-dbt-performance-and-slim-ci.md)

**Why here:** as projects grow, builds slow down and bills rise. Slim CI
makes pull requests fast and safe.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why builds slow: too many models, wrong materialisations, wide full-table rebuilds, serial dependencies |
| Basics | Threads (`threads` in profiles) and DAG parallelism; finding the critical path in `run_results.json` |
| Basics | Timing and cost per model: adapters' query history, `dbt run` timings |
| Intermediate | **State-based selection**: `state:modified+`, `--defer`, `--state` artifacts from production |
| Intermediate | **Slim CI**: build only changed models and their dependents in a temporary schema; drop on PR close |
| Intermediate | Incremental conversion for large tables; partitioning/clustering configs per warehouse |
| Intermediate | **Warehouse-specific tuning**: warehouse size and `snowflake_warehouse` configs, BigQuery partition filters and slot use, Databricks liquid clustering, DuckDB threads |
| Advanced | `dbt clone` for zero-copy environments; data diffs on PRs (audit_helper, Datafold-style diffs) |
| Advanced | Test cost control; running heavy checks nightly; `--fail-fast` and `--warn-error` |
| Advanced | Splitting large projects: multi-project / dbt Mesh, selectors in `selectors.yml`, and per-domain jobs |
| Advanced | Cost attribution with `query_comment` and tags; profiling expensive models |
| Advanced | Faster parsing and the newer engines (dbt Fusion) — awareness |

**How to learn it**

1. Read the topic file.
2. Identify the 10 slowest models in `run_results.json` and propose a fix
   for each.
3. Draft a CI workflow that builds only what a PR changed.

**Hands-on exercise — `experiments/06_performance_ci/`**

1. Generate a 100-model project (script) and time a full build.
2. Tune threads and materialisations; record before/after.
3. Save production artifacts; run `dbt build --select state:modified+
   --defer --state prod_artifacts` on a branch.
4. Add a GitHub Actions workflow that does slim CI with a per-PR schema
   and cleanup.
5. Add a data-diff step comparing row counts for changed models.

**Checkpoint:**

- [ ] Find and fix slow models.
- [ ] Run slim CI with state and defer.
- [ ] Choose warehouse-specific optimisations.
- [ ] Control CI and test costs.

**Common mistakes:** full builds on every PR; ignoring the critical path;
no cleanup of PR schemas; too many threads for the warehouse.

---

### Topic 07 — [Semantic Layer and MetricFlow](07-semantic-layer-and-metricflow.md)

**Why here:** the same metric ("revenue") is often defined five ways in
five dashboards. A semantic layer defines it once and serves it everywhere
(extending Module 2.22 Topic 03).

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The metric consistency problem; why semantic layers exist |
| Basics | Core concepts: **semantic models**, **entities** (primary, foreign, unique), **dimensions** (categorical, time), and **measures** |
| Basics | **Metrics** types: simple, ratio, cumulative, derived, conversion |
| Intermediate | Writing semantic model and metric YAML; time spines and granularities |
| Intermediate | **MetricFlow**: query planning that generates SQL joins from entities; `mf query` and `mf validate-configs` |
| Intermediate | Saved queries, exports, and caching; dimension and metric naming standards |
| Intermediate | Handling fan-out and join-key issues; aggregation semantics (sum vs average of ratios) |
| Advanced | Serving metrics: dbt Semantic Layer APIs (JDBC/GraphQL), BI integrations (Tableau, Power BI, Hex, Mode), and notebooks |
| Advanced | Governance: owners, certified metrics, deprecation, and version control for definitions |
| Advanced | Comparisons: Cube, LookML, AtScale, Looker semantic layer, Snowflake/Databricks metric views — trade-offs |
| Advanced | Testing metrics against known answers; reconciliation with finance numbers |
| Advanced | Semantic layers for AI: natural-language-to-metric queries and governed context for LLMs (links to Module 2.22 Topic 05) |

**How to learn it**

1. Read the topic file.
2. Write a one-page metric dictionary for revenue, active customers, and
   conversion rate: formula, grain, filters, owner.
3. Identify where each metric is currently defined inconsistently.

**Hands-on exercise — `experiments/07_semantic_layer/`**

1. Define semantic models over `fct_orders` and `dim_customers`.
2. Define simple, ratio, and cumulative metrics (revenue, AOV, running
   revenue).
3. Validate configs and query metrics with `mf query` by dimension and
   time grain.
4. Compare MetricFlow's generated SQL against hand-written SQL for the
   same answer.
5. Connect a BI tool or notebook to the semantic layer API (if available).

**Checkpoint:**

- [ ] Define semantic models, entities, and metrics.
- [ ] Explain how MetricFlow generates joins.
- [ ] Govern metric definitions.
- [ ] Compare dbt's semantic layer with alternatives.

**Common mistakes:** metrics defined on top of non-conformed dimensions;
averaging averages; semantic layer built before the marts are stable.

---

### Topic 08 — [Deploying dbt with Airflow and dbt Cloud](08-deploying-dbt-with-airflow-and-dbt-cloud.md)

**Why it comes last:** development is half the job. Production means
scheduling, environments, secrets, alerts, and recoverability.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Environments: dev, CI, staging, production; one target and schema strategy per environment |
| Basics | Running `dbt build` on a schedule; exit codes; reading `run_results.json` |
| Basics | **dbt Cloud** basics: projects, environments, jobs (deploy, CI, merge), IDE, and scheduling |
| Intermediate | **Airflow + dbt**: BashOperator, `dbt-core` in a virtualenv or container, and **Cosmos** (rendering a dbt DAG as Airflow tasks); per-model retries (links to Module 2.13) |
| Intermediate | Job design: full vs partial builds, selectors, source freshness before run, and test gating before downstream refresh |
| Intermediate | Secrets and credentials: environment variables, cloud secret managers, key-pair auth, and OIDC from CI |
| Intermediate | Containerising dbt (Docker) and running on Kubernetes/Cloud Run jobs/ECS |
| Advanced | Orchestration alternatives: Dagster (`dagster-dbt` software-defined assets), Prefect, Databricks Workflows, ADF, Snowflake tasks |
| Advanced | CI/CD pipeline: lint → compile → slim build → test → docs → deploy on merge; promotion and rollback |
| Advanced | Observability: run artifacts to a table, alerts (Slack/PagerDuty), Elementary, freshness SLAs, and cost dashboards |
| Advanced | Backfills and reruns: `--full-refresh` on selected models, microbatch backfills, and communicating to consumers |
| Advanced | Operating at scale: ownership, on-call, runbooks, and deprecation processes |

**How to learn it**

1. Read the topic file.
2. Draw the production flow: ingestion finishes → freshness check → dbt
   build → tests → publish docs → notify.
3. Write a runbook for "a test failed in production".

**Hands-on exercise — `experiments/08_deployment/`**

1. Containerise the dbt project; run it from a clean container with env
   vars only.
2. Build an Airflow DAG with Cosmos (or a DAG per layer) that runs
   freshness → build → docs.
3. Add Slack/email alerting on failure with the failing model name.
4. Implement CI/CD: PR → slim CI; merge → production deploy.
5. Run the same project in dbt Cloud (free tier) and compare the effort.
6. Store `run_results.json` in a table and chart build durations.

**Checkpoint:**

- [ ] Deploy dbt with a scheduler and secure credentials.
- [ ] Gate downstream refreshes on tests.
- [ ] Alert, rerun, and backfill safely.
- [ ] Compare dbt Cloud, Airflow, and Dagster deployments.

**Common mistakes:** running dbt manually in production; credentials in
the repo; one job that rebuilds everything every hour; no ownership of
failures.

---

## 10. Module mini-project — a tested, documented analytics warehouse

**Goal:** build a production-grade dbt project from raw tables to
governed metrics.

**Requirements**

1. A source layer with freshness checks and at least five raw tables.
2. Staging → intermediate → marts with a clear grain; at least one fact,
   two dimensions, one SCD2 dimension from a snapshot, and one incremental
   fact with late-data handling.
3. Tests on every model; at least two singular tests, one custom generic
   test, three unit tests, and contracts on public marts.
4. Full documentation with descriptions, doc blocks, ownership meta, and
   two exposures.
5. Three macros and two packages, with a macro unit test.
6. A semantic layer with five metrics, validated against hand-written SQL.
7. CI with SQLFluff, slim builds, and per-PR schemas; deployment through
   Airflow (Cosmos) or dbt Cloud; failure alerts; and run artifacts stored
   for analysis.
8. A README covering architecture, conventions, and a runbook.

**Done when** a new teammate can clone the repo, build the whole project
in minutes, and a bad change in a PR is caught by tests before reaching
production.

---

## 11. Module self-assessment — exit criteria

You have completed this module when you can do all of the following
**without notes**:

- [ ] Structure a dbt project and choose materialisations.
- [ ] Build incremental models and SCD2 snapshots correctly.
- [ ] Write macros, use packages, and avoid over-engineering.
- [ ] Test, contract, and version models.
- [ ] Document models and track lineage and exposures.
- [ ] Run fast, cost-aware slim CI.
- [ ] Define governed metrics in a semantic layer.
- [ ] Deploy, monitor, and operate dbt in production.

---

## 12. Recommended reading and references

- dbt documentation (docs.getdbt.com) — best practices guides on project
  structure, materialisations, and CI.
- *Fundamentals of Analytics Engineering* — Dumky de Wilde et al.
- *The Data Warehouse Toolkit* — Kimball (for modelling).
- dbt Labs "How we structure our dbt projects"; dbt Community Slack and
  Coalesce talks.
- Package hubs: `dbt_utils`, `dbt_expectations`, `elementary`, `dbt-project-evaluator`.

---

## 13. Where this module leads

- **Module 2C.7** covers the engines that dbt can target for low-latency
  analytics (ClickHouse, Trino).
- **Module 2C.8** places the transformation layer in the wider data
  platform and data product model.
- **Module 2C.9** uses your marts for analysis, experiments, and BI.
- **Module 2C.10** hands curated tables to ML pipelines.
