# Metadata-Driven Platform Design

**Roadmap location:** Stage 2C — Data Engineering_3  
**Module:** `08-Data-Platform-Architecture-and-Data-Products`  
**Target file:** `05-metadata-driven-platform-design.md`  
**Hands-on project:** `experiments/05_metadata_platform/`  
**Level:** Beginner to advanced platform engineering

> **Syllabus authority and scope.** The module roadmap's Topic 05 establishes the order and required learning outcomes: describe pipeline intent in metadata; validate YAML/JSON with Pydantic/JSON Schema; use control tables; generate orchestrator and dbt artifacts; compare dlt, Airbyte, Azure Data Factory (ADF), Databricks Lakeflow, and custom Python; distinguish control and data planes; store run state; onboard through reviewed configuration; automate governance, migration, tests, lineage, and platform-as-a-product practices. `Roadmap_ptree.md` confirms the target filename under `Stage 2C — Data Engineering_3/08-Data-Platform-Architecture-and-Data-Products/`. This lesson follows that sequence.

## 1. Learning objectives

After completing this lesson, you should be able to:

1. Explain what metadata-driven design is and why it reduces repeated pipeline code.
2. Separate pipeline intent, executable logic, runtime state, and operational evidence.
3. Design versioned YAML/JSON metadata with explicit semantics, validation, defaults, and safe failure behavior.
4. Validate metadata with Pydantic and export JSON Schema for tooling and review.
5. Use configuration to generate a scheduler-neutral execution plan and dbt staging models.
6. Explain how Airflow DAG factories, Dagster definitions, dlt, Airbyte, ADF metadata pipelines, and Databricks Lakeflow differ.
7. Design control-plane/data-plane boundaries, checkpoints, idempotency, run history, and error reporting.
8. Build a self-service onboarding path based on a reviewed pull request, tests, deployment, and rollback.
9. Drive masking, retention, ownership workflows, access review, lineage, and notifications from metadata.
10. Migrate schema versions and test both the generator and its generated artifacts.
11. Recognise when a configuration system becomes an undocumented programming language.
12. Decide when to reuse a framework, keep a simple pipeline, or build source-specific logic.

---

## 2. Prerequisites and terminology

### 2.1 Prerequisites

Helpful foundations are Python, YAML/JSON, SQL, batch and incremental ingestion, orchestration, data quality, data contracts, IAM, data catalogues, and Git-based code review. You do not need a deployed Airflow or Dagster installation to complete the core lab.

### 2.2 Terminology

| Term | Meaning |
|---|---|
| **Metadata** | Information describing a data asset, source, schema, owner, classification, lineage, or execution. |
| **Configuration** | The subset of metadata that controls a particular runtime or generator. |
| **Execution logic** | The code that performs extraction, validation, transformation, loading, retries, and error handling. |
| **Runtime state** | Mutable progress needed to continue safely, such as a watermark, cursor, checkpoint, or last committed batch. |
| **Operational metadata** | Run IDs, start/end times, status, row counts, error category, retry count, and config/model version. |
| **Control table** | A structured store of ingestion definitions, enablement, priorities, and sometimes current state. |
| **Control plane** | The system that defines, validates, authorises, schedules, configures, and observes workloads. |
| **Data plane** | The execution path that reads, transforms, and writes data. |
| **Generator** | Code that turns validated configuration into plans, DAG definitions, SQL models, or infrastructure resources. |
| **Golden path** | A documented, supported default workflow that makes a common task safe and easy. |
| **Escape hatch** | A controlled extension point for source-specific behavior that does not fit the generic abstraction. |

**Important distinction:** metadata is not automatically truth just because it is in YAML or a catalogue. Decide which system is authoritative for each field. A Git-reviewed YAML file may be the source of truth for desired pipeline configuration, a catalogue may be the discoverable index, a control database may hold current operational status, and the scheduler may own its own run state.

---

## 3. Metadata-driven architecture fundamentals

### 3.1 Describe what; implement how

A metadata-driven platform describes *what should happen*:
- Read `crm.customers`.
- Use incremental extraction with `updated_at` as the watermark.
- Write to the bronze layer.
- Require `customer_id` to be non-null and unique.
- Run hourly.
- Assign an owner.
- Apply confidential-data controls.
- Retain data for a defined period.

A generic engine implements *how*:
- Resolve a connection reference from a secret manager.
- Open the connector.
- Fetch data using the selected extraction mode.
- Apply retries and checkpoints.
- Run quality checks.
- Write to the target.
- Emit status and lineage.
- Handle errors and notify the owner.

Metadata-driven does **not** mean “no code.” It means the platform's reusable code handles common patterns and configuration expresses source-specific parameters. Connectors, quality-check implementations, scheduler integrations, and governance actions are still code that must be maintained.

### 3.2 Why hand-written pipelines become expensive

Imagine 80 sources, each with its own script. Each script independently implements authentication, retries, watermarks, logging, quality checks, alerts, and target naming. A change to retry behavior may require 80 edits. A security fix may be applied inconsistently. One pipeline may silently skip a watermark update while another advances it before the target commit.

A shared framework can implement these behaviors once and allow source definitions to declare only the differences.

| Concern | Repeated implementation | Metadata-driven implementation |
|---|---|---|
| Retry and timeout policy | Duplicated in each script | Shared engine defaults and approved overrides |
| Source table/object | Hard-coded | `source.system` and `source.object` |
| Extraction mode | Branches copied across scripts | Validated enum: full/incremental/CDC |
| Watermark | Custom per script | Explicit field plus shared state protocol |
| Target | Repeated SQL or path strings | Validated target layer and dataset |
| Quality checks | Inconsistent ad hoc logic | Typed check definitions and common runner |
| Classification/retention | Often manual and forgotten | Required metadata drives policy artifacts |
| Run evidence | Different log formats | Standard operational event and history schema |
| New source | Copy, edit, debug, review | Add a config, pass checks, deploy; add code only for a genuinely new behavior |

### 3.3 Shared pattern versus source-specific variation

The useful metadata is the set of differences that vary across otherwise similar pipelines.

**Usually shared:** lifecycle, retries, observability, run IDs, quality-check execution, target write protocol, checkpoint safety, lineage emission, owner notification, and policy enforcement.

**Usually variable:** source system/object, connector, extraction mode, key columns, watermark column, target, quality rules, schedule, owner, classification, retention, and occasional transformation or pagination strategy.

Do not abstract differences that are not actually common. The roadmap explicitly warns against building the framework before at least three real pipelines have shown which behaviors are shared.

### 3.4 Configuration-driven versus hard-coded

Configuration-driven is most useful when:
- Many sources follow a small number of stable patterns.
- Source onboarding is frequent.
- Governance and observability need consistent enforcement.
- The cost of fixing the same behavior in many pipelines is high.

Hard-coded or source-specific logic can be justified when:
- The workflow is unique and unlikely to recur.
- A configuration abstraction would be more complex than the behavior.
- A specialized connector needs unusual semantics that cannot be safely expressed by existing extension points.

The goal is not maximum abstraction. The goal is lower total lifecycle cost without losing clarity or correctness.

---

## 4. Configuration schema design

### 4.1 Recommended metadata fields

| Field | Meaning | Validation / policy |
|---|---|---|
| `schema_version` | Version of the metadata contract | Exact supported version; migrate old versions before execution |
| `pipeline_id` | Stable logical pipeline name | Unique, lowercase identifier |
| `source.system` | Namespace/source system | Required, controlled naming |
| `source.object` | Table, endpoint, stream, or object | Required and validated for the connector |
| `source.connector` | Adapter implementation | Allow-listed connector type |
| `source.connection_ref` | Reference to connection/secret configuration | Never put credentials in YAML |
| `source.extraction_mode` | `full`, `incremental`, or `cdc` | Enum; each mode has distinct semantics |
| `source.keys` | Business/technical key columns | Non-empty, unique, safe identifiers, and members of `source.columns` |
| `source.columns` | Approved source/landing columns used for generated dbt SQL | Non-empty, unique safe identifiers; quality checks and keys must refer to declared columns |
| `source.dbt_schema` | Warehouse schema for the declared dbt source relation | Explicit schema identifier; must match the landing relation in the deployed dbt environment |
| `source.watermark` | Source column used for incremental extraction | Required only for `incremental`; must be a declared column |
| `source.cdc_cursor` | Log sequence number, offset, or connector cursor for change-data capture | Required for `cdc`; distinct from a column watermark and never inferred automatically |
| `target.layer` | `bronze`, `silver`, or `gold` | Enum |
| `target.dataset` | Target table/dataset identifier | Safe identifier and unique within deployment scope |
| `quality_checks` | Typed quality assertions | Check type and required parameters validated |
| `schedule` | Five-field cron expression for the lab | Numeric field ranges are validated locally; use the actual scheduler parser and explicit time-zone policy in production |
| `owner` | Accountable team/contact | Valid contact format; ideally a catalogue team identity |
| `classification` | Data sensitivity category | Enum tied to enforceable policy |
| `retention_days` | Retention duration | Positive and bounded; policy must define deletion behavior |
| `tags` | Discovery and operational labels | Optional, controlled vocabulary recommended |
| `custom_logic` | Named plugin hook | Must resolve to an allow-listed implementation; never evaluate arbitrary code from config |

### 4.2 Defaults and invalid configurations

Defaults should be few, visible, and safe:
- Retry policy may default to three attempts with exponential backoff.
- A run ID is generated by the runtime.
- `tags` can default to an empty list.
- A schedule should not silently default to “run every minute.”
- Missing keys, a missing incremental watermark or CDC cursor, an unknown connector, invalid cron ranges, or unknown fields should fail validation.
- A restricted dataset should not silently default to public access or unmasked non-production output.

A default is a policy decision. Document it, test it, and make it visible in generated plans.

### 4.3 YAML and JSON

YAML is readable and convenient for source-controlled configuration. JSON is explicit and convenient for APIs and machines. Both are data formats, not security boundaries. Parse the file, validate it against a schema, enforce cross-field rules, and never use YAML as a place to store secrets.

Example v3 YAML:

```yaml
schema_version: "3.0"
pipeline_id: "crm_customers"
description: "Ingest customer master records from CRM"
source:
  system: "crm"
  object: "customers"
  connector: "csv_file"
  connection_ref: "local.crm_customers"
  extraction_mode: "incremental"
  keys: ["customer_id"]
  columns: ["customer_id", "email", "full_name", "updated_at"]
  dbt_schema: "crm_raw"
  watermark: "updated_at"
  cdc_cursor: null
target:
  layer: "bronze"
  dataset: "crm_customers"
quality_checks:
  - type: "not_null"
    column: "customer_id"
  - type: "unique"
    column: "customer_id"
  - type: "not_null"
    column: "updated_at"
schedule: "0 * * * *"
owner: "crm-data@example.com"
classification: "confidential"
retention_days: 365
tags: ["customer", "crm"]
custom_logic: null
```

### 4.4 Pydantic and JSON Schema

Pydantic models validate parsed Python data and can export JSON Schema. Pydantic is useful in the Python runtime and CI; JSON Schema can be consumed by editors, portals, policy checks, and other languages. Neither replaces business-semantic validation.

The lab uses Pydantic v2 and exports `schema/metadata-v3.schema.json` for the v3 metadata contract. It also uses cross-field validators: incremental mode requires a declared column watermark; full mode cannot specify a watermark or CDC cursor; CDC requires a separate log cursor; keys and quality-check columns must be declared; cron fields must be within numeric ranges; and confidential/restricted pipelines require a non-null check for every key.

The lab validates safe column identifiers, key/column membership, quality-check column references, extraction/cursor consistency, and numeric ranges for five-field cron expressions. A production schema should additionally validate connector-specific options, the actual scheduler's cron/time-zone semantics, target namespace permissions, owner existence, retention/legal holds, and live source fields where discovery is available.

### 4.5 Schema evolution

A schema version identifies the shape and meaning of the configuration contract. It is not the pipeline's business-data schema version.

- **Backward-compatible addition:** a new optional field with a safe default may be accepted by old configs.
- **Breaking change:** renaming `mode` to `source.extraction_mode`, changing a field's semantics, or changing a default that affects behavior requires migration or a new major schema version.
- **Unknown fields:** reject by default to catch misspellings and stale configurations.
- **Migration:** transform old configs explicitly, validate the new result, and review the diff before deployment.

---

## 5. Validation and control-table patterns

### 5.1 Layered validation

Validation should happen at more than one point:

1. **Syntax:** YAML/JSON can be parsed.
2. **Schema:** required fields, types, enums, lengths, and patterns are valid.
3. **Semantic rules:** incremental mode requires a watermark; restricted data has required quality checks.
4. **Environment checks:** connection reference exists, source object is accessible, target namespace is permitted, owner exists, and schedule is supported.
5. **Policy checks:** classification/retention rules meet governance policy; production writes are authorised.
6. **Runtime checks:** actual schema and data satisfy expectations; watermark advancement is safe.

A valid YAML file is not necessarily safe to execute. Validation should fail closed when policy-sensitive metadata is missing or contradictory. The local simulation is recorded as `SIMULATED`, not `COMPLETE`, because it does not read or write source/target data and never advances a checkpoint.

### 5.2 Control tables

A control table stores definitions and operational control state in a queryable form. A typical design separates relatively static configuration from mutable run state.

**`ingestion_definition`** (desired configuration):

| Column | Purpose |
|---|---|
| `pipeline_id` | Stable identifier |
| `config_version` / `config_digest` | Exact config revision |
| `source_system`, `source_object`, `extraction_mode` | Source behavior |
| `key_columns`, `watermark_column` | Key/cursor semantics |
| `target_layer`, `target_dataset` | Destination |
| `schedule`, `owner`, `classification`, `retention_days` | Operational and governance metadata |
| `enabled`, `priority`, `effective_from` | Controlled deployment state |

**`ingestion_run`** (runtime history):

| Column | Purpose |
|---|---|
| `run_id`, `pipeline_id` | Run identity |
| `config_digest` | Config used |
| `started_at`, `ended_at`, `status` | Lifecycle |
| `source_window`, `watermark_before`, `watermark_after` | Incremental processing |
| `records_read`, `records_written`, `quality_failures` | Metrics |
| `error_code`, `error_summary`, `retry_count` | Failure diagnostics |

**`ingestion_checkpoint`** (current progress):

| Column | Purpose |
|---|---|
| `pipeline_id`, `partition_key` | State identity |
| `committed_watermark` | Last safely committed cursor |
| `updated_at`, `run_id` | Provenance |

For incremental mode, the watermark is a source-column cursor; for CDC, the checkpoint is a log position/offset and is not necessarily a source column. The checkpoint should advance only after the target write and its commit protocol succeed. Updating it before the data commit can permanently skip records after a crash. Use transactions where possible, idempotent writes, replayable windows, and an explicit recovery policy.

### 5.3 Git configuration versus control database

A Git-reviewed YAML file is strong for desired-state review, history, diff, and promotion. A database control table is strong for runtime querying, enablement, priorities, and current state. They can coexist:
- Git stores approved desired configuration.
- CI validates and deploys it.
- A deployment process materialises a versioned read model/control table.
- The runtime records mutable checkpoints and run history separately.
- The catalogue indexes the pipeline and data asset for discovery.

Avoid two writable sources of truth for the same field. If operators can edit both Git and the control table, define precedence and reconciliation explicitly.

Microsoft's ADF metadata-driven copy pattern uses a control table and parameterised pipelines to configure repeated copy jobs; it is an example of the pattern, not the only way to implement it.

---

## 6. Pipeline generation and reusable frameworks

### 6.1 What can be generated?

From validated metadata, a platform can generate:
- Scheduler-neutral execution plans.
- Airflow DAG definitions or Dagster jobs/assets.
- dbt staging SQL or model scaffolding.
- Governance policy artifacts.
- Data-quality check configuration.
- Documentation and catalogue registration payloads.
- Infrastructure requests or Terraform module inputs.
- OpenLineage-shaped run events.

Generated artifacts should be deterministic: the same canonical config and generator version should produce the same plan except for explicitly time-varying fields. The lab records the config digest, generator version, schema version, and a `generated_manifest.json` containing SHA-256 digests for generated plans, SQL, source declarations, and policy artifacts.

### 6.2 Airflow and Dagster

**Airflow dynamic DAG generation** creates DAG definitions from code/config when the DAG file is parsed. Keep parsing fast, avoid unnecessary metadata database calls at module import time, and make task definitions deterministic. A generated DAG is a scheduler definition, not a source connector by itself.

**Dagster factories** can create asset/job definitions from metadata. Dagster is asset-oriented: it models data assets, dependencies, and compute definitions. Use the factory to define repeated asset patterns, but keep unusual business logic in typed Python functions.

The lab does not import or run Airflow/Dagster. It generates a scheduler-neutral plan and simulates a run. This is deliberate: a real integration needs a compatible scheduler installation, deployment topology, secrets, source connectors, and integration tests.

### 6.3 dbt staging models

A template is appropriate when source models follow a stable pattern: consistent `source()` declarations, standard metadata columns, standard tags, and repeatable select lists. Keep complex business transformation in readable SQL models/macros rather than hiding the entire project in a generator.

Generated SQL must use validated identifiers and trusted schema metadata. Do not interpolate arbitrary strings into SQL. In production, prefer adapter quoting and a known schema registry/catalogue; test compilation using the actual dbt project and adapter.

The lab generates one dbt-style staging SQL file per source and a matching `sources.yml` declaration using the configured `dbt_schema`. This makes the `source()` references internally coherent, but it does not prove the named warehouse relations exist. It does not run `dbt compile` because dbt and a configured warehouse adapter are not part of the core environment.

### 6.4 Framework comparison

| Framework | Primary abstraction | Metadata/config role | Strengths | Limitations / fit |
|---|---|---|---|---|
| **dlt** | Python pipelines, sources/resources, destinations, normalisation and loading state | Python configuration and pipeline/resource definitions | Python-friendly ingestion, incremental loading patterns, useful for teams that want code-first flexibility | Not a universal scheduler or enterprise governance system; destination and source capabilities vary |
| **Airbyte** | Source/destination connectors and sync connections | Connector configuration; declarative YAML for some connector types | Broad connector ecosystem, managed sync concepts, connector reuse | Connector behavior, sync mode, deployment, and governance depend on connector/platform capabilities |
| **Azure Data Factory metadata pipelines** | Activities and parameterised pipelines reading control tables | Control-table rows and linked-service/pipeline parameters | Useful for large numbers of similar copy jobs in Azure environments | ADF orchestration and connectors are not equivalent to a general Python framework; control-table design remains important |
| **Databricks Lakeflow / declarative pipelines** | Declarative batch/streaming data pipelines and dependencies | Pipeline configuration plus SQL/Python definitions | Managed orchestration and dependency handling within Databricks; fits its lakehouse runtime | Platform-specific runtime and semantics; not interchangeable with Airbyte or ADF |
| **Custom Python** | Whatever interface the team defines | Pydantic/YAML/JSON or database control tables | Full control, easy to test domain rules, can bridge systems | Team owns retries, connectors, state, scheduler integration, security, observability, and upgrades |
| **Airflow** | Task DAGs and scheduling | DAG code/config and scheduler state | Broad orchestration ecosystem | Orchestration does not automatically supply ingestion connectors, data contracts, or governance |
| **Dagster** | Assets, jobs, dependencies, resources | Definitions and configuration | Strong asset-oriented development and observability model | Requires adopting its model and runtime; not simply a YAML ingestion engine |

Choose the abstraction that matches the workload. Do not imply that all tools use the same config schema or orchestration model.

---

## 7. Control plane versus data plane

### 7.1 Architecture

<CodeBlock language="mermaid">
flowchart TB
    PR[Source-controlled YAML / JSON] --> CI[CI: schema, policy, tests]
    CI --> DEP[Approved deployment]
    DEP --> CAT[Catalogue / metadata index]
    DEP --> CTRL[Versioned control definitions]
    CTRL --> ORCH[Airflow / Dagster / managed scheduler]
    ORCH --> ENG[Reusable execution engine]
    ENG --> SRC[Source connectors]
    ENG --> TGT[Target storage / warehouse]
    ENG --> STATE[Checkpoint and run history]
    ENG --> Q[Quality checks]
    ENG --> LIN[Lineage / observability events]
    CAT --> PORTAL[Self-service portal]
    STATE --> ALERT[Owner alerts / SLO monitoring]
    LIN --> CAT
</CodeBlock>

### 7.2 Control plane responsibilities

- Validate and approve desired configuration.
- Resolve policy, access, ownership, schedule, and runtime settings.
- Generate workload definitions.
- Register discoverable assets and lineage.
- Track deployment version and current status.
- Manage lifecycle, rollout, rollback, and policy enforcement.

### 7.3 Data plane responsibilities

- Read from source systems using approved credentials.
- Apply extraction and transformation logic.
- Persist output safely and idempotently.
- Advance checkpoints only after successful commits.
- Run quality checks and report metrics.
- Emit run and lineage events.

The control plane should not carry bulk data. The data plane should not invent governance policy. Runtime state is mutable and separate from desired configuration. The catalogue can be a source of discovery and lineage while the reviewed config remains authoritative for pipeline intent.

---

## 8. Self-service onboarding

### 8.1 Golden-path onboarding workflow

1. Engineer creates a branch and adds a YAML definition.
2. CI parses the file and validates the schema.
3. CI checks uniqueness, source access, target naming, owner, classification, retention, and connector capability.
4. Unit tests assert generated plan and dbt output.
5. Policy checks verify required masking/access/retention behavior.
6. Code owners review data ownership, target, schedule, and operational impact.
7. Approved change is deployed to a non-production environment.
8. Smoke tests and source-schema checks run.
9. Promotion deploys the same config digest to production.
10. Catalogue, run history, lineage, and owner notification are updated.
11. Rollback returns to a known config version or disables the pipeline without deleting state.

### 8.2 Measure onboarding as a product

Measure:
- Median time from accepted request to first successful production run.
- Percentage of sources onboarded without custom code.
- CI failure reasons and rework rate.
- First-week failure rate and data-quality defect rate.
- Adoption of standard templates.
- Percentage of assets with owner/classification/retention metadata.
- Time to recover or roll back a bad config.

The platform is a product with users, documentation, support, release notes, an upgrade policy, and feedback—not just a shared library.

### 8.3 Backstage and Terraform

Backstage software templates can provide a portal form that scaffolds a repository/config file and publishes it through a workflow. They do not automatically provide data ingestion or governance; the template should call the platform's validation and deployment pipeline.

Terraform modules can provision reusable infrastructure such as storage, IAM, secrets references, scheduler resources, or service accounts. They should not be confused with the runtime data pipeline itself. A good internal developer platform combines templates, modules, policy checks, catalogues, and deployment workflows into one supported path.

---

## 9. Governance through metadata

### 9.1 Classification-driven policy

A classification field is useful only if it triggers enforceable controls. Example policy mapping:

| Classification | Example control |
|---|---|
| `public` | Standard access; no default masking |
| `internal` | Authenticated internal access; ordinary audit |
| `confidential` | Restricted access, masked non-production copies, access review, owner approval |
| `restricted` | Stronger access boundaries, mask direct identifiers, explicit approval and audit |

The mapping is illustrative; a real organisation must use its approved taxonomy and policy engine. Do not treat this table as a legal classification standard.

The lab generates a governance artifact from `classification`, `retention_days`, and `owner`. Confidential and restricted data trigger non-production masking requirements and access review; owner metadata becomes the recipient for failure and quality-failure notification policy. The artifact explicitly says `policy_artifact_only`: it does not execute masking, enforce IAM, send notifications, or delete data by itself.

### 9.2 Retention-driven lifecycle

Retention metadata should produce a lifecycle rule or policy request that specifies:
- Data asset and scope.
- Retention duration and effective date.
- Delete/expire/archive action.
- Legal hold or regulatory exception behavior.
- Backup and replica treatment.
- Evidence of completion.

A `retention_days` value alone does not delete anything. The lifecycle controller must translate it into the target platform's native policy, verify application, and report failures. Reject a retention policy that conflicts with legal holds or minimum retention requirements.

### 9.3 Ownership-driven workflow

Owner metadata can drive:
- Alerts on failures and freshness/SLO breaches.
- Access requests and approval routing.
- Review reminders for stale or unused assets.
- Escalation after a run remains failed.
- Documentation and catalogue ownership.

Validate that the owner exists in an authoritative directory. An email-shaped string is a useful syntax check but not proof that the owner is active or authorised.

### 9.4 Security invariants

- Never store credentials in metadata; store secret references.
- Never allow an unknown classification to fall back to public.
- Do not permit config to disable mandatory policy checks without an approved exception.
- Keep connector types and custom hooks allow-listed.
- Treat config pull requests as code changes: review, test, authorise, and audit them.
- Apply least privilege to the runtime identity, not only to the person who edited YAML.
- Separate the ability to author metadata from the ability to deploy or approve restricted data flows.

---

## 10. Observability and lineage

### 10.1 Operational events

At minimum, capture:
- Pipeline ID, run ID, config digest, schema version, generator version.
- Start/end time, status, duration, retry count, and error category.
- Source window, checkpoint before/after, and number of records read/written.
- Quality checks executed and failed.
- Target dataset and write/commit outcome.
- Owner and classification (avoid unnecessary PII in logs).

Error reports should distinguish validation failure, source connectivity failure, schema drift, data-quality failure, target-write failure, checkpoint-commit failure, and policy denial. Redact credentials and sensitive row values.

### 10.2 Checkpoints and idempotency

For incremental extraction, define:
- Whether the cursor is monotonic and unique enough.
- Inclusive/exclusive window boundaries.
- How late-arriving updates are captured.
- How a failed run is replayed.
- Whether writes are upserts, append-only, or replace-partition.
- When checkpoint state is committed.

A robust sequence is: read window → write idempotently → validate commit → commit checkpoint → mark run complete. If a checkpoint is committed before target data, failures can lose data. If data commits but checkpoint fails, a replay should be safe.

### 10.3 OpenLineage

OpenLineage defines a standard event model for jobs, runs, and datasets. A framework can emit run events with inputs and outputs so lineage does not depend entirely on manually maintained documentation. Events should include stable namespaces, dataset names, run IDs, timestamps, and relevant facets. Do not send sensitive column values or secrets as lineage facets.

The lab emits **OpenLineage-shaped JSON payloads locally**. Because no data-plane work is performed, simulated runs are recorded as `SIMULATED`, and their event type is `OTHER` rather than falsely claiming an OpenLineage `COMPLETE` event. The lab does not install the OpenLineage client, publish events, or connect to a backend. A production integration should use the official client/integration supported by the deployed scheduler and configure transport and authentication securely.

---

## 11. Versioning and migration

### 11.1 Schema evolution from v1/v2 to the current v3 contract

The current contract is **schema version `3.0`**. This is a breaking bump from the draft v2 contract because v3 requires an explicit approved `source.columns` list and `source.dbt_schema`, and separates CDC log cursors from incremental column watermarks.

Version 1 used flattened fields:

```yaml
schema_version: "1.0"
pipeline_id: "legacy_customers"
source_system: "crm"
source_object: "customers"
connector: "csv_file"
connection_ref: "local.crm_customers"
mode: "incremental"
primary_key: "customer_id"
watermark_column: "updated_at"
target_layer: "bronze"
target_dataset: "legacy_customers"
owner: "crm-data@example.com"
classification: "confidential"
retention_days: 365
schedule: "0 * * * *"
```

Version 2 grouped fields under `source` and `target`, but did not require a complete column inventory or explicit dbt schema. Version 3 requires those fields so generated SQL does not rely on a hard-coded object-to-column mapping. It also models `source.watermark` for incremental column-based extraction separately from `source.cdc_cursor` for log positions/offsets.

The lab provides two explicit migrations:

- `migrate_v1_to_v3()` migrates the older flat format directly to v3.
- `migrate_v2_to_v3()` upgrades existing nested v2 configs by adding v3 metadata.

Both functions reject unknown fields and validate the resulting object with the v3 Pydantic model. Because old configs do not necessarily contain the full source schema, migration only infers a minimal column list from keys, quality checks, and any column watermark. Treat that result as a scaffold: enrich and review it against the real source/landing schema before deployment. Legacy CDC configs are rejected when the old watermark field cannot be safely mapped to a log cursor.

Migration process:
1. Detect the config version before validating against the current schema.
2. Use the version-specific migration function.
3. Reject unknown fields and invalid semantic combinations.
4. Produce v3 configuration and validate it with the v3 model.
5. Review the diff and complete inferred source columns; never silently overwrite the original.
6. Run generator fixture tests and policy checks.
7. Deploy gradually and retain the prior config version for rollback.

### 11.2 Backward compatibility policy

- Support old configs only for a declared deprecation window.
- Emit warnings before removing a version.
- Do not change extraction semantics or retention defaults silently.
- Store config digests and generator versions with every run.
- Make migrations deterministic and idempotent.
- Keep old schema fixtures to test the migration path.

---

## 12. Testing and extensibility

### 12.1 Test the configuration and the generator

A reliable suite includes:
- Valid configuration tests.
- Missing required field and invalid enum tests.
- Cross-field validation tests.
- Unknown-field rejection.
- Duplicate pipeline/target detection.
- Security policy invariants.
- Version migration tests.
- Snapshot/contract tests for generated plans and SQL.
- Idempotency and checkpoint tests for the runtime.
- Connector contract tests.
- End-to-end tests in an integration environment.

Testing only the Pydantic model is insufficient: a valid config can still generate an incorrect DAG or unsafe SQL.

### 12.2 Safe extension points

Use named adapters/plugins with stable interfaces, for example:

```python
class SourceAdapter:
    def discover_schema(self, spec): ...
    def read_window(self, spec, checkpoint): ...
    def commit_checkpoint(self, spec, new_checkpoint): ...
```

The ellipses above are interface placeholders, not executable implementation. The platform should resolve a validated connector enum to a registered adapter. For source-specific behavior:
- First check whether an existing adapter supports a parameter.
- Add a new typed metadata field only if the behavior is reusable.
- Add a named plugin when behavior is substantial but bounded.
- Keep exceptional business transformation in normal code with tests.
- Never `eval()` a YAML string or dynamically import arbitrary user-supplied module names.

The lab's `custom_logic` is a restricted identifier field and is recorded as `custom_logic_requested`; the generated plan explicitly sets `custom_logic_executed` to `false`, and the sample runner does not execute a custom plugin. A real runtime must implement and test an explicit plugin registry before using it.

### 12.3 Test generated artifacts

Generated files are code. Tests should assert:
- Required tasks/dependencies or plan steps exist.
- Source and target names are correct.
- The correct watermark/checkpoint is represented.
- Classification creates the required policy.
- Retention is preserved.
- dbt SQL contains the expected `source()` reference and validated columns.
- Schema migration yields the same intended behavior.
- No secret value appears in generated files.
- Generator output is deterministic for a fixed input and generator version.

---

## 13. Limits and anti-patterns

### 13.1 When configuration becomes a bad programming language

Warning signs:
- Nested conditionals and arbitrary expressions in YAML.
- String fields that contain SQL, Python, or shell commands.
- A generic field whose meaning changes by connector without a schema.
- Unclear precedence between global, source, environment, and runtime settings.
- Many one-off flags that no one can explain.
- Debugging requires reading the entire generator to understand one source.
- Every new source requires multiple bespoke config exceptions.

At that point, move complex behavior into typed code, a plugin, or a dedicated pipeline. Configuration should be declarative and reviewable, not a hidden general-purpose programming language.

### 13.2 Other common anti-patterns

- Building a framework before understanding three real pipelines.
- Treating the catalogue, Git, control table, and scheduler as simultaneous sources of truth.
- Updating watermarks before output commits.
- Making retention and classification descriptive fields that are never enforced.
- Allowing arbitrary connector types or dynamic code execution from YAML.
- Generating a giant DAG with hundreds of thousands of tasks at parse time.
- Assuming generated dbt SQL is valid without compilation/tests.
- Hiding transformations in overly generic macros.
- Using mutable runtime state as if it were desired configuration.
- Having no migration strategy or rollback.
- Over-abstracting a one-off pipeline.
- Calling a simulation a deployed scheduler integration.

### 13.3 Decision framework

| Situation | Recommended approach |
|---|---|
| One or two simple pipelines, low change rate | Keep simple explicit code; standardise logging/tests first |
| Three to five similar pipelines reveal repeated lifecycle behavior | Extract a small shared library and typed configuration |
| Dozens/hundreds of sources follow a stable pattern | Metadata-driven framework with schema, policy, catalogue, and run state |
| Most sources fit a connector product and managed sync semantics | Evaluate Airbyte/dlt/managed ingestion before building connectors |
| Azure-centric copy workloads across many objects | Evaluate ADF metadata-driven pipelines and control tables |
| Databricks-centric batch/streaming transformations | Evaluate Lakeflow/declarative pipelines with source/target configuration |
| Complex source-specific behavior with little reuse | Dedicated adapter or custom pipeline; do not contort the generic schema |
| Regulated data or high-risk policy differences | Keep mandatory policy in central code/policy engine; configuration may tighten but not bypass it |

**Decision rule:** introduce a framework when the lifecycle behavior is genuinely repeated and the cost of standardising it is lower than maintaining copies. Keep a simple pipeline when abstraction adds more concepts than it removes. Build custom code for irreducible domain behavior, not for routine retry/logging/ownership behavior.

---

## 14. Hands-on implementation

### 14.1 Project tree

```text
experiments/05_metadata_platform/
├── pyproject.toml
├── README.md
├── metadata_platform.py
├── run_lab.py
├── configs/
│   ├── customers.yaml
│   ├── orders.yaml
│   └── product_catalog.yaml
├── data/
│   ├── data_customers.csv
│   ├── data_orders.csv
│   └── data_products.csv
├── fixtures/
│   ├── legacy_customers_v1.yaml
│   └── expected_crm_plan_contract.json
├── schema/
│   ├── generate_json_schema.py
│   └── metadata-v3.schema.json
├── templates/
│   └── staging_model.sql.j2
├── generated/
│   ├── crm_customers.plan.json
│   ├── commerce_orders.plan.json
│   ├── erp_product_catalog.plan.json
│   ├── sources.yml
│   ├── governance_policies.json
│   ├── generated_manifest.json
│   └── stg_*.sql
├── reports/
│   ├── run_history.jsonl
│   └── *.openlineage.json
└── tests/
    └── test_platform.py
```

Generated artifacts and run history are created when the lab runs; the ZIP bundle includes the verified outputs from this run.

### 14.2 Setup

Python 3.10+:

```bash
cd experiments/05_metadata_platform
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install -e ".[test]"
python schema/generate_json_schema.py
python run_lab.py
pytest -q
```

### 14.3 What the lab implements

1. Pydantic v3 models with `extra="forbid"`.
2. Versioned v3 YAML metadata for three source definitions.
3. Cross-field checks for extraction mode, keys, columns, column watermarks versus CDC cursors, quality rules, classification, owner, target, and cron field ranges.
4. Exported JSON Schema.
5. Scheduler-neutral execution-plan generation.
6. dbt-style staging SQL and matching `sources.yml` generation from configured source metadata, without a hard-coded source-object-to-column map.
7. Governance policy generation for masking, retention, owner notifications, and access review; outputs are policy artifacts only.
8. v1-to-v3 and v2-to-v3 migration functions plus legacy fixtures, including explicit handling of incomplete legacy schema metadata.
9. Run history with config digest, generator version, `SIMULATED` status, timestamps, and a checkpoint that is explicitly not advanced.
10. Local OpenLineage-shaped `OTHER` event payloads, not successful ingestion events.
11. Pytest tests for valid/invalid configs, schema artifact, migration, governance, SQL safety, new-source onboarding, generated output contract, determinism, and simulation semantics.

### 14.4 The three definitions

- `customers.yaml`: incremental CRM landing relation, declared columns, `updated_at` column watermark, confidential classification, one-year retention.
- `orders.yaml`: full commerce landing relation, declared columns, internal classification, two-year retention.
- `product_catalog.yaml`: incremental ERP landing relation, declared columns, `modified_at` column watermark, public classification, five-year retention.

Each config declares the source columns and dbt schema used by generated SQL. They share the same engine but vary source, keys, extraction mode, target, schedule, owner, classification, retention, and quality checks. A CDC config would use a log cursor rather than pretending the log position is a source column watermark.

### 14.5 Generated outputs

A generated plan contains:
- Canonical source and target metadata.
- Schedule, owner, quality checks.
- SHA-256 config digest and generator version.
- Governance policy, owner notification route, and explicit policy-only enforcement status.
- Checkpoint key where relevant; the simulation never advances it.
- Retry/idempotency contract and `custom_logic_executed: false`.
- The local simulation execution mode.
- A generated manifest with SHA-256 hashes of the generated artifacts.

A dbt-style staging file contains the configured source reference and validated column list; `sources.yml` declares matching source names, tables, and schemas. A governance artifact maps classification and retention into policy instructions. These outputs are integration contracts, not proof that a warehouse masking policy, lifecycle rule, notification, or data movement was performed.

---

## 15. Automated tests and expected outputs

### 15.1 Test coverage

The core test suite verifies:
- Three configs validate and have unique pipeline IDs and layer/dataset targets.
- Incremental mode requires a column watermark that exists in declared columns; full mode rejects cursors; CDC requires a separate log cursor.
- Invalid cron ranges, unknown fields, unsafe identifiers, duplicate keys/columns/tags, and quality checks against unknown columns fail validation.
- Confidential/restricted configs require non-null checks for every key.
- Classification, retention, and owner metadata generate explicit policy-only instructions.
- Generated plan, dbt SQL, and `sources.yml` match the configured source metadata.
- A fourth source can be added without editing a hard-coded object-to-columns map.
- v1-to-v3 and v2-to-v3 migrations validate outputs, report missing fields, and reject ambiguous legacy CDC.
- Simulated run history does not claim ingestion success or advance a checkpoint.
- Generated artifacts have deterministic SHA-256 manifest entries.
- Exported JSON Schema agrees with the Pydantic v2 contract.

### 15.2 Actual execution

The project was executed in the available Python environment.

`python run_lab.py` completed with:

```json
{
  "pipelines_loaded": 3,
  "plans_generated": 3,
  "dbt_models_generated": 3,
  "governance_policies": 3,
  "dbt_source_definitions_generated": 3,
  "artifact_manifest_generated": true,
  "simulated_runs": 3,
  "statuses": {
    "crm_customers": "SIMULATED",
    "commerce_orders": "SIMULATED",
    "erp_product_catalog": "SIMULATED"
  },
  "note": "local orchestration simulation; no Airflow, Dagster, source, warehouse, or OpenLineage backend invoked"
}
```

`pytest -q` completed with:

```text
21 passed
```

These results confirm the local configuration validation, generation, migration, governance artifact, and history code paths. They do **not** demonstrate a live ingestion, deployed scheduler, real masking, lifecycle deletion, warehouse execution, or remote lineage emission. Those integrations require the corresponding platform and integration tests.

### 15.3 Example generated policy for `crm_customers`

```json
{
  "pipeline_id": "crm_customers",
  "classification": "confidential",
  "masking": {
    "mask_pii": true,
    "policy": "mask_email_phone_in_nonprod"
  },
  "retention": {
    "days": 365,
    "action": "expire_or_delete_after_retention",
    "enforcement_status": "policy_artifact_only"
  },
  "owner": "crm-data@example.com",
  "owner_notifications": {
    "on_failure": true,
    "on_quality_failure": true,
    "recipient": "crm-data@example.com"
  },
  "access_review_required": true,
  "enforcement_status": "policy_artifact_only"
}
```

The policy is a generated instruction. A production policy controller must apply it to the actual data platform and report success/failure.

---

## 16. Common mistakes and misconceptions

1. Metadata-driven design means no code is needed.
2. YAML parsing alone validates a pipeline.
3. A valid config guarantees the source exists and the target is writable.
4. A catalogue is automatically the authoritative source for every field.
5. A control table should store desired configuration, checkpoints, and run history in one unversioned row.
6. A watermark can be advanced before the target commit.
7. Retention metadata deletes data automatically without a lifecycle controller.
8. Classification metadata is useful even if no policy engine consumes it.
9. An Airflow DAG generator is a connector framework.
10. A dbt SQL template is safe even when arbitrary identifiers are interpolated.
11. All ingestion frameworks share the same config schema and state model.
12. Every one-off source deserves a generic abstraction.
13. Complex SQL, Python, and shell snippets belong in YAML.
14. A custom hook can safely be an arbitrary module name from a pull request.
15. A local simulation proves production reliability.
16. Generated artifacts do not need tests because they are generated.
17. Schema migration can be done by renaming fields without checking semantics.
18. Platform success is measured only by number of pipelines rather than onboarding time, quality, adoption, and reliability.

---

## 17. Practice questions with answers

### Q1. What is the difference between metadata and execution logic?
**Answer:** Metadata declares source, target, extraction mode, rules, ownership, and policy. Execution logic implements connector behavior, retries, data movement, quality evaluation, state commits, and error handling.

### Q2. Why not write every pipeline explicitly?
**Answer:** Repeated behavior drifts across implementations, fixes are duplicated, and governance/observability become inconsistent. A framework is justified when the shared lifecycle is stable and common.

### Q3. What should happen if incremental mode has no watermark?
**Answer:** Configuration validation should fail before scheduling or execution. The platform should not guess a watermark or silently switch to full extraction.

### Q4. What is the difference between a control table and run history?
**Answer:** A control table usually describes desired behavior or enablement; run history records what happened. Checkpoints store mutable progress and should be managed separately or in clearly separate tables.

### Q5. Why is the catalogue not always the source of truth?
**Answer:** A catalogue is primarily for discovery, metadata management, and lineage. Pipeline configuration may be controlled by Git, while the runtime database owns checkpoints. Authority must be assigned field by field.

### Q6. How should config changes be deployed?
**Answer:** Through reviewed version control, schema/policy/generator tests, environment validation, deployment of a known config digest, smoke testing, and a rollback path.

### Q7. What makes a generated artifact testable?
**Answer:** Deterministic output, explicit fixtures/contracts, assertions for source/target/schedule/checkpoint/policy, security checks, and integration compilation or execution in the target environment.

### Q8. When is a custom adapter appropriate?
**Answer:** When source-specific behavior is real and irreducible, or reusable but too complex for existing configuration fields. The adapter must follow a typed interface and have contract tests.

### Q9. Why can configuration become a bad programming language?
**Answer:** Arbitrary expressions, deeply nested conditions, opaque precedence, and many one-off flags make behavior harder to reason about than ordinary code. Move complex logic into typed implementations.

### Q10. How does classification metadata become an actual control?
**Answer:** A policy controller maps classification to access, masking, audit, and approval requirements, applies those controls to the target system, and records success/failure. Generating a policy document alone is not enforcement.

### Q11. What does the lab's OpenLineage event prove?
**Answer:** Only that a local event-shaped payload can be generated. It does not prove delivery to a lineage backend or compatibility with a particular production integration.

### Q12. How should a platform measure self-service success?
**Answer:** Median onboarding lead time, proportion of sources onboarded without custom code, rework, first-week failures, policy completeness, adoption, and operational reliability.

---

## 18. Completion checklist

- [ ] I can explain “describe what, implement how.”
- [ ] I can identify common lifecycle behavior and source-specific variation.
- [ ] I can design a versioned YAML/JSON schema and validate it with Pydantic/JSON Schema.
- [ ] I can define extraction modes, keys, watermarks, targets, checks, schedules, owners, classification, and retention.
- [ ] I can explain the control-table pattern and separate desired configuration from checkpoints and run history.
- [ ] I can generate an execution plan and dbt staging model safely.
- [ ] I can compare Airflow, Dagster, dlt, Airbyte, ADF, Lakeflow, and custom Python without treating them as interchangeable.
- [ ] I can explain control plane versus data plane.
- [ ] I can design a reviewed self-service onboarding workflow.
- [ ] I can make classification, retention, and ownership drive real policy actions.
- [ ] I can design run history, errors, checkpoints, idempotency, and OpenLineage events.
- [ ] I can migrate old config versions and retain rollback capability.
- [ ] I can test both configs and generated artifacts.
- [ ] I can create a safe escape hatch without evaluating arbitrary code from YAML.
- [ ] I can identify when configuration complexity exceeds the value of the abstraction.
- [ ] I can measure platform adoption and onboarding lead time.

**Checkpoint:** You are ready to progress when you can add a source by configuration, explain every generated artifact, demonstrate fail-closed policy behavior, reproduce the output from a config digest, and describe how a failed incremental run recovers without losing or duplicating data.

---

## 19. Verified references and further reading

The module roadmap is the authority for syllabus sequence. These official documentation sources were consulted to verify tool roles and relevant implementation patterns:

- **Pydantic validation and JSON Schema:** https://pydantic.dev/docs/validation/latest/get-started/
- **Apache Airflow dynamic DAG generation:** https://airflow.apache.org/docs/apache-airflow/stable/howto/dynamic-dag-generation.html
- **Dagster asset definitions:** https://docs.dagster.io/guides/build/assets/defining-assets
- **dlt documentation:** https://dlthub.com/docs/intro
- **Airbyte documentation and connectors:** https://docs.airbyte.com/ and https://docs.airbyte.com/integrations
- **Airbyte Connector Builder (declarative YAML connector definitions):** https://docs.airbyte.com/platform/connector-development/connector-builder-ui/overview
- **Azure Data Factory metadata-driven copy pattern and control tables:** https://learn.microsoft.com/en-us/azure/data-factory/copy-data-tool-metadata-driven
- **Databricks Lakeflow / Spark Declarative Pipelines:** https://docs.databricks.com/aws/en/ldp/concepts/pipelines
- **dbt Jinja and macros:** https://docs.getdbt.com/docs/build/jinja-macros
- **OpenLineage Python client:** https://openlineage.io/docs/client/python/
- **Backstage software templates:** https://backstage.io/docs/features/software-templates/
- **Terraform modules:** https://developer.hashicorp.com/terraform/language/modules

Tool APIs and features vary by version, edition, deployment, and connector. Pin versions, consult the documentation for the deployed release, and run integration tests in the target environment.

---

# Appendix A — Complete runnable project source

The downloadable `experiments-05-metadata-platform.zip` contains the current runnable lab, including the full generator, three v3 YAML configs, v1 and v2 migration paths, v3 JSON Schema, CSV samples, generated plans, matching dbt source declarations and SQL, governance policy artifacts, manifest digests, run history, local lineage-shaped events, and tests. The bundle is the canonical executable source so code blocks in this document do not have to be copied manually.

## A.1 `pyproject.toml`

```toml
[project]
name = "metadata-platform-lab"
version = "0.1.0"
description = "Educational metadata-driven ingestion platform"
requires-python = ">=3.10"
dependencies = ["pydantic>=2.6,<3", "PyYAML>=6,<7", "Jinja2>=3.1,<4"]

[project.optional-dependencies]
test = ["pytest>=8,<9"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

## A.2 Core model and generator API

The full implementation is in `metadata_platform.py`. Its public interfaces include:

```python
load_spec(path)
load_all_specs(config_dir=None)
generate_plan(spec)
render_dbt_model(spec, columns=None, template_dir=None)
generate_dbt_sources(specs)
governance_policy(spec)
migrate_v1_to_v3(raw)
migrate_v2_to_v3(raw)
generate_dbt_sources(specs)
make_openlineage_event(spec, run_id, state, started_at, ended_at=None)
execute_simulation(spec, run_id, history_path=None)
write_generated(config_dir=None, output_dir=None)
```

All code, YAML, test fixtures, and expected generated outputs are included in the ZIP bundle.

## A.3 Runtime boundary

The core runner generates plans and records simulated runs. It does not read the CSV samples, connect to a database/API, write to a warehouse, launch a scheduler, enforce masking, delete expired data, or transmit lineage events. These are explicit integration seams for a production implementation—not implied capabilities of the demo.


# Appendix B — Complete project file contents

The listings below are generated from the current executable project files and generated outputs after the final test run. They are included for inspection; the ZIP bundle is the runnable project. The lineage payloads and policy JSON are local artifacts only, not evidence of a live integration.


## B.1 `README.md`

````markdown
# Metadata-driven platform lab

This is a local educational framework, not a deployed scheduler or ingestion service.

## Requirements
- Python 3.10+
- Pydantic 2, PyYAML, Jinja2
- pytest for tests

## Setup
```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
python schema/generate_json_schema.py
python run_lab.py
pytest -q
```

## What runs
- Validates three YAML definitions against the Pydantic v2 schema.
- Generates deterministic JSON execution plans, dbt-style staging SQL, a matching `sources.yml`, governance policy JSON, and an artifact-digest manifest.
- Records `SIMULATED` run history and creates local OpenLineage-shaped `OTHER` events; it does not claim data movement succeeded.
- Demonstrates schema v1-to-v3 and v2-to-v3 migrations in tests. A legacy config without full column metadata is migrated to a minimal key/watermark column list and must be reviewed/enriched before production. Legacy CDC configs require explicit manual mapping to a log cursor.

No Airflow, Dagster, real source, warehouse, masking engine, lifecycle manager, or OpenLineage backend is invoked. The runtime plan and governance artifacts are integration contracts for a future deployment.

## Extension point
`source.connector` is an enum allow-list. To add a connector:
1. Implement a connector adapter that conforms to the platform's source interface.
2. Add a reviewed connector type and configuration schema.
3. Add contract tests and a fixture for its output.
4. Keep secrets in a secret manager; `connection_ref` is only a reference, never a credential.
5. Only add `custom_logic` after review; it is recorded as a request in this lab and never executed. A real runtime must resolve it through an explicit allow-listed plugin registry.

## Metadata schema versioning
`fixtures/legacy_customers_v1.yaml` illustrates the old flat shape. `migrate_v1_to_v3()` converts it to the current nested v3 shape and validates the migrated object with `PipelineSpec`. `migrate_v2_to_v3()` upgrades existing draft v2 configs by adding column and dbt-schema metadata; inferred columns must be reviewed before production. The migration is deterministic but cannot infer a full source schema from the old format.
````


## B.2 `pyproject.toml`

````toml
[project]
name = "metadata-platform-lab"
version = "0.1.0"
description = "Educational metadata-driven ingestion platform"
requires-python = ">=3.10"
dependencies = ["pydantic>=2.6,<3", "PyYAML>=6,<7", "Jinja2>=3.1,<4"]

[project.optional-dependencies]
test = ["pytest>=8,<9"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
````


## B.3 `metadata_platform.py`

````python
from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ROOT = Path(__file__).resolve().parent
SCHEMA_VERSION = "3.0"
GENERATOR_VERSION = "0.2.0"
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
ALLOWED_CONNECTORS = {"csv_file", "http_api", "database"}


def _valid_cron_field(field: str, minimum: int, maximum: int) -> bool:
    """Validate a five-field numeric cron component, including lists/ranges/steps."""
    if field == "*":
        return True
    for item in field.split(","):
        if not item:
            return False
        base, slash, step_text = item.partition("/")
        if slash:
            if not step_text.isdigit() or int(step_text) < 1:
                return False
        if base == "*":
            continue
        if "-" in base:
            parts = base.split("-")
            if len(parts) != 2 or not all(p.isdigit() for p in parts):
                return False
            start, end = map(int, parts)
            if start < minimum or end > maximum or start > end:
                return False
        else:
            if not base.isdigit() or not minimum <= int(base) <= maximum:
                return False
    return True


def validate_cron(value: str) -> str:
    fields = value.split()
    ranges = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]
    if len(fields) != 5:
        raise ValueError("schedule must contain five cron fields")
    for field, (minimum, maximum) in zip(fields, ranges):
        if not _valid_cron_field(field, minimum, maximum):
            raise ValueError(f"invalid cron field {field!r}; expected values in {minimum}..{maximum}")
    return value


class SourceSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    system: str = Field(min_length=2, pattern=r"^[a-z][a-z0-9_-]*$")
    object: str = Field(min_length=1, pattern=r"^[a-zA-Z][a-zA-Z0-9_]*$")
    connector: Literal["csv_file", "http_api", "database"]
    connection_ref: str = Field(min_length=3, pattern=r"^[A-Za-z0-9_.:-]+$")
    extraction_mode: Literal["full", "incremental", "cdc"]
    keys: list[str] = Field(min_length=1)
    columns: list[str] = Field(min_length=1)
    dbt_schema: str = Field(min_length=1, pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    watermark: str | None = None
    cdc_cursor: str | None = None

    @field_validator("keys", "columns")
    @classmethod
    def valid_unique_identifiers(cls, values: list[str]) -> list[str]:
        if any(not isinstance(v, str) or not IDENTIFIER_RE.fullmatch(v) for v in values):
            raise ValueError("keys/columns must contain safe SQL identifiers")
        if len(values) != len(set(values)):
            raise ValueError("source keys/columns must not contain duplicates")
        return values

    @field_validator("watermark", "cdc_cursor")
    @classmethod
    def validate_cursor_name(cls, value: str | None) -> str | None:
        if value is not None and not IDENTIFIER_RE.fullmatch(value):
            raise ValueError("watermark/cdc_cursor must be a safe identifier")
        return value

    @model_validator(mode="after")
    def validate_extraction_cursor(self):
        if not set(self.keys).issubset(self.columns):
            raise ValueError("every source key must appear in source.columns")
        if self.extraction_mode == "incremental":
            if not self.watermark:
                raise ValueError("incremental extraction requires source.watermark")
            if self.watermark not in self.columns:
                raise ValueError("incremental watermark must appear in source.columns")
            if self.cdc_cursor:
                raise ValueError("incremental extraction must not define source.cdc_cursor")
        elif self.extraction_mode == "cdc":
            if not self.cdc_cursor:
                raise ValueError("CDC extraction requires source.cdc_cursor (for example an LSN/offset field)")
            if self.watermark:
                raise ValueError("CDC uses a log cursor, not a column watermark; omit source.watermark")
        else:
            if self.watermark or self.cdc_cursor:
                raise ValueError("full extraction must not define a watermark or CDC cursor")
        return self


class TargetSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    layer: Literal["bronze", "silver", "gold"]
    dataset: str = Field(pattern=r"^[a-z][a-z0-9_]*$")


class QualityCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["not_null", "unique", "accepted_values"]
    column: str = Field(min_length=1, pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    values: list[str] | None = None

    @model_validator(mode="after")
    def values_match_check_type(self):
        if self.type == "accepted_values" and not self.values:
            raise ValueError("accepted_values check requires a non-empty values list")
        if self.type != "accepted_values" and self.values is not None:
            raise ValueError("values is only valid for accepted_values")
        if self.values is not None and len(self.values) != len(set(self.values)):
            raise ValueError("accepted_values must not contain duplicates")
        return self


class PipelineSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["3.0"]
    pipeline_id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    description: str = Field(min_length=10)
    source: SourceSpec
    target: TargetSpec
    quality_checks: list[QualityCheck] = Field(min_length=1)
    schedule: str
    owner: str
    classification: Literal["public", "internal", "confidential", "restricted"]
    retention_days: int = Field(gt=0, le=36500)
    tags: list[str] = Field(default_factory=list)
    custom_logic: Literal["normalize_phone_v1", "custom_api_pagination_v1"] | None = None

    @field_validator("schedule")
    @classmethod
    def cron_shape(cls, value: str) -> str:
        return validate_cron(value)

    @field_validator("owner")
    @classmethod
    def owner_must_be_email(cls, value: str) -> str:
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("owner must be an email address")
        return value

    @field_validator("tags")
    @classmethod
    def tags_must_be_unique(cls, values: list[str]) -> list[str]:
        if any(not tag.strip() for tag in values):
            raise ValueError("tags must not contain blank values")
        if len(values) != len(set(values)):
            raise ValueError("tags must not contain duplicates")
        return values

    @model_validator(mode="after")
    def validate_pipeline_semantics(self):
        if self.source.connector not in ALLOWED_CONNECTORS:
            raise ValueError("unsupported connector")
        columns = set(self.source.columns)
        unknown_check_columns = {check.column for check in self.quality_checks} - columns
        if unknown_check_columns:
            raise ValueError(f"quality checks reference unknown source columns: {sorted(unknown_check_columns)}")
        if self.classification in {"confidential", "restricted"}:
            checked_keys = {q.column for q in self.quality_checks if q.type == "not_null"}
            missing_key_checks = set(self.source.keys) - checked_keys
            if missing_key_checks:
                raise ValueError(
                    "confidential/restricted pipelines require not_null checks for every key; "
                    f"missing: {sorted(missing_key_checks)}"
                )
        return self


def load_spec(path: Path) -> PipelineSpec:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: YAML root must be a mapping")
    return PipelineSpec.model_validate(raw)


def load_all_specs(config_dir: Path | None = None) -> list[PipelineSpec]:
    config_dir = config_dir or ROOT / "configs"
    specs = [load_spec(path) for path in sorted(config_dir.glob("*.yaml"))]
    if not specs:
        raise ValueError(f"no YAML pipeline definitions found in {config_dir}")
    ids = [spec.pipeline_id for spec in specs]
    if len(ids) != len(set(ids)):
        raise ValueError("pipeline_id values must be unique across the config directory")
    targets = [(spec.target.layer, spec.target.dataset) for spec in specs]
    if len(targets) != len(set(targets)):
        raise ValueError("target layer/dataset pairs must be unique across the config directory")
    return specs


def spec_digest(spec: PipelineSpec) -> str:
    payload = json.dumps(spec.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def governance_policy(spec: PipelineSpec) -> dict:
    masking = {
        "public": {"mask_pii": False, "policy": "no_default_masking"},
        "internal": {"mask_pii": False, "policy": "internal_access_controls"},
        "confidential": {"mask_pii": True, "policy": "mask_email_phone_in_nonprod"},
        "restricted": {"mask_pii": True, "policy": "mask_all_direct_identifiers_nonprod"},
    }[spec.classification]
    return {
        "pipeline_id": spec.pipeline_id,
        "classification": spec.classification,
        "masking": masking,
        "retention": {
            "days": spec.retention_days,
            "action": "expire_or_delete_after_retention",
            "enforcement_status": "policy_artifact_only",
        },
        "owner": spec.owner,
        "owner_notifications": {"on_failure": True, "on_quality_failure": True, "recipient": spec.owner},
        "access_review_required": spec.classification in {"confidential", "restricted"},
        "enforcement_status": "policy_artifact_only",
    }


def generate_plan(spec: PipelineSpec) -> dict:
    return {
        "pipeline_id": spec.pipeline_id,
        "schema_version": spec.schema_version,
        "generator_version": GENERATOR_VERSION,
        "config_digest": spec_digest(spec),
        "source": spec.source.model_dump(mode="json"),
        "target": spec.target.model_dump(mode="json"),
        "schedule": spec.schedule,
        "owner": spec.owner,
        "quality_checks": [check.model_dump(mode="json") for check in spec.quality_checks],
        "governance": governance_policy(spec),
        "execution": {
            "mode": "local_simulation",
            "checkpoint_key": f"{spec.pipeline_id}:watermark" if spec.source.watermark else (
                f"{spec.pipeline_id}:cdc_cursor" if spec.source.cdc_cursor else None
            ),
            "retry_policy": {"max_attempts": 3, "backoff": "exponential"},
            "idempotency_key": "pipeline_id + source_window + config_digest",
            "custom_logic_requested": spec.custom_logic,
            "custom_logic_executed": False,
        },
    }


def render_dbt_model(spec: PipelineSpec, columns: list[str] | None = None, template_dir: Path | None = None) -> str:
    selected_columns = columns if columns is not None else spec.source.columns
    if not selected_columns:
        raise ValueError("columns must be supplied from trusted metadata or schema discovery")
    if any(not IDENTIFIER_RE.fullmatch(column) for column in selected_columns):
        raise ValueError("unsafe column identifier in source.columns")
    if len(selected_columns) != len(set(selected_columns)):
        raise ValueError("dbt model columns must be unique")
    env = Environment(
        loader=FileSystemLoader(str(template_dir or ROOT / "templates")),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=False,
        lstrip_blocks=False,
    )
    template = env.get_template("staging_model.sql.j2")
    source_call = f"{{{{ source('{spec.source.system}', '{spec.source.object}') }}}}"
    dbt_config_line = "{{ config(materialized='view', tags=" + repr(spec.tags) + ") }}"
    return template.render(
        pipeline=spec,
        columns=selected_columns,
        source_call=source_call,
        dbt_config_line=dbt_config_line,
    )


def generate_dbt_sources(specs: list[PipelineSpec]) -> str:
    """Generate dbt source declarations matching each generated source() call."""
    grouped: dict[str, dict[str, object]] = {}
    for spec in specs:
        source_name = spec.source.system
        entry = grouped.setdefault(source_name, {"name": source_name, "schema": spec.source.dbt_schema, "tables": []})
        if entry["schema"] != spec.source.dbt_schema:
            raise ValueError(f"source system {source_name!r} maps to multiple dbt schemas")
        tables = entry["tables"]
        assert isinstance(tables, list)
        if not any(table["name"] == spec.source.object for table in tables):
            tables.append({"name": spec.source.object, "description": f"Landing relation for {spec.pipeline_id}"})
    payload = {"version": 2, "sources": list(grouped.values())}
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)


def migrate_v1_to_v3(raw: dict) -> dict:
    """Migrate the documented flat v1 format; legacy column metadata needs review."""
    if not isinstance(raw, dict):
        raise ValueError("v1 config must be a mapping")
    if raw.get("schema_version") != "1.0":
        raise ValueError("migrate_v1_to_v3 expects schema_version '1.0'")
    allowed = {
        "schema_version", "pipeline_id", "source_system", "source_object", "connector", "connection_ref",
        "mode", "primary_key", "watermark_column", "target_layer", "target_dataset", "owner",
        "classification", "retention_days", "schedule", "columns", "dbt_schema",
    }
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError(f"unknown v1 fields: {sorted(unknown)}")
    required = allowed - {"watermark_column", "columns", "dbt_schema"}
    missing = required - set(raw)
    if missing:
        raise ValueError(f"v1 config missing required fields: {sorted(missing)}")
    mode = raw["mode"]
    watermark = raw.get("watermark_column")
    if mode == "cdc":
        raise ValueError("CDC migration requires manual mapping from source log position to source.cdc_cursor")
    if mode not in {"full", "incremental"}:
        raise ValueError(f"unsupported v1 extraction mode: {mode!r}")
    if mode == "incremental" and not watermark:
        raise ValueError("v1 incremental config requires watermark_column")
    if mode == "full" and watermark:
        raise ValueError("v1 full mode cannot carry watermark_column")
    primary_key = raw["primary_key"]
    columns = raw.get("columns") or list(dict.fromkeys([primary_key] + ([watermark] if watermark else [])))
    migrated = {
        "schema_version": SCHEMA_VERSION,
        "pipeline_id": raw["pipeline_id"],
        "description": f"Migrated from schema 1.0: {raw['pipeline_id']}",
        "source": {
            "system": raw["source_system"],
            "object": raw["source_object"],
            "connector": raw["connector"],
            "connection_ref": raw["connection_ref"],
            "extraction_mode": mode,
            "keys": [primary_key],
            "columns": columns,
            "dbt_schema": raw.get("dbt_schema", raw["source_system"]),
            "watermark": watermark,
            "cdc_cursor": None,
        },
        "target": {"layer": raw["target_layer"], "dataset": raw["target_dataset"]},
        "quality_checks": [
            {"type": "not_null", "column": primary_key},
            {"type": "unique", "column": primary_key},
        ],
        "schedule": raw["schedule"],
        "owner": raw["owner"],
        "classification": raw["classification"],
        "retention_days": raw["retention_days"],
        "tags": ["migrated"],
        "custom_logic": None,
    }
    # Fail during migration rather than returning a malformed configuration.
    PipelineSpec.model_validate(migrated)
    return migrated



def migrate_v2_to_v3(raw: dict) -> dict:
    """Migrate a draft v2 config by adding explicit column and dbt-schema metadata."""
    if not isinstance(raw, dict):
        raise ValueError("v2 config must be a mapping")
    if raw.get("schema_version") != "2.0":
        raise ValueError("migrate_v2_to_v3 expects schema_version '2.0'")
    allowed = {
        "schema_version", "pipeline_id", "description", "source", "target", "quality_checks",
        "schedule", "owner", "classification", "retention_days", "tags", "custom_logic",
    }
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError(f"unknown v2 fields: {sorted(unknown)}")
    required = allowed - {"tags", "custom_logic"}
    missing = required - set(raw)
    if missing:
        raise ValueError(f"v2 config missing required fields: {sorted(missing)}")
    source = raw["source"]
    if not isinstance(source, dict):
        raise ValueError("v2 source must be a mapping")
    mode = source.get("extraction_mode")
    if mode == "cdc" and source.get("watermark") and not source.get("cdc_cursor"):
        raise ValueError("v2 CDC migration requires manual mapping from watermark to source.cdc_cursor")
    keys = source.get("keys") or []
    checks = raw.get("quality_checks") or []
    inferred = list(dict.fromkeys(
        list(keys)
        + [check["column"] for check in checks if isinstance(check, dict) and isinstance(check.get("column"), str)]
        + ([source["watermark"]] if source.get("watermark") else [])
    ))
    migrated = dict(raw)
    migrated["schema_version"] = SCHEMA_VERSION
    migrated_source = dict(source)
    migrated_source.setdefault("columns", inferred)
    migrated_source.setdefault("dbt_schema", source.get("system", ""))
    migrated_source.setdefault("cdc_cursor", None)
    migrated["source"] = migrated_source
    PipelineSpec.model_validate(migrated)
    return migrated


def make_openlineage_event(
    spec: PipelineSpec, run_id: str, state: str, started_at: str, ended_at: str | None = None
) -> dict:
    """Create a local OpenLineage-shaped event; no event is sent to a backend."""
    allowed_states = {"START", "RUNNING", "COMPLETE", "ABORT", "FAIL", "OTHER"}
    normalized_state = state.upper()
    event_type = "OTHER" if normalized_state == "SIMULATED" else normalized_state
    if event_type not in allowed_states:
        raise ValueError(f"unsupported OpenLineage event state: {state!r}")
    if not run_id.strip():
        raise ValueError("run_id must not be blank")
    event = {
        "eventType": event_type,
        "eventTime": ended_at or started_at,
        "run": {"runId": run_id},
        "job": {
            "namespace": "urn:metadata-platform-lab:job",
            "name": spec.pipeline_id,
            "facets": {"documentation": {"description": "Local simulation only; no data-plane execution occurred."}},
        },
        "inputs": [{"namespace": f"urn:metadata-platform-lab:source:{spec.source.system}", "name": spec.source.object}],
        "outputs": [{"namespace": f"urn:metadata-platform-lab:target:{spec.target.layer}", "name": spec.target.dataset}],
        "producer": "https://example.invalid/metadata-platform-lab",
        "schemaURL": "https://openlineage.io/spec/2-0-2/OpenLineage.json",
    }
    return event


def execute_simulation(spec: PipelineSpec, run_id: str, history_path: Path | None = None) -> dict:
    """Record a local plan simulation, not a successful ingestion run."""
    if not run_id.strip():
        raise ValueError("run_id must not be blank")
    history_path = history_path or ROOT / "reports/run_history.jsonl"
    now = datetime.now(timezone.utc).isoformat()
    status = "SIMULATED"
    error = None
    try:
        plan = generate_plan(spec)
        if not plan["target"]["dataset"]:
            raise RuntimeError("target dataset missing")
    except Exception as exc:
        status, error = "SIMULATION_FAILED", str(exc)
    row = {
        "run_id": run_id,
        "pipeline_id": spec.pipeline_id,
        "status": status,
        "execution_mode": "local_simulation",
        "started_at": now,
        "ended_at": datetime.now(timezone.utc).isoformat(),
        "config_digest": spec_digest(spec),
        "generator_version": GENERATOR_VERSION,
        "error": error,
        "checkpoint": {
            "key": f"{spec.pipeline_id}:watermark" if spec.source.watermark else f"{spec.pipeline_id}:cdc_cursor",
            "value": None,
            "advanced": False,
        } if (spec.source.watermark or spec.source.cdc_cursor) else None,
    }
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row) + "\n")
    return row


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_generated(config_dir: Path | None = None, output_dir: Path | None = None) -> list[dict]:
    config_dir = config_dir or ROOT / "configs"
    output_dir = output_dir or ROOT / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    specs = load_all_specs(config_dir)
    plans: list[dict] = []
    generated_paths: list[Path] = []
    for spec in specs:
        plan = generate_plan(spec)
        plans.append(plan)
        plan_path = output_dir / f"{spec.pipeline_id}.plan.json"
        plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        generated_paths.append(plan_path)
        sql_path = output_dir / f"stg_{spec.target.dataset}.sql"
        sql_path.write_text(render_dbt_model(spec), encoding="utf-8")
        generated_paths.append(sql_path)

    sources_path = output_dir / "sources.yml"
    sources_path.write_text(generate_dbt_sources(specs), encoding="utf-8")
    generated_paths.append(sources_path)
    policy_path = output_dir / "governance_policies.json"
    policy_path.write_text(json.dumps([governance_policy(spec) for spec in specs], indent=2) + "\n", encoding="utf-8")
    generated_paths.append(policy_path)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "artifacts": {path.name: _sha256_file(path) for path in sorted(generated_paths)},
    }
    manifest_path = output_dir / "generated_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return plans
````


## B.4 `run_lab.py`

````python
import json
from pathlib import Path
from metadata_platform import load_all_specs, write_generated, execute_simulation, make_openlineage_event, ROOT

def main():
    specs = load_all_specs()
    plans = write_generated()
    run_rows = []
    for i, spec in enumerate(specs, 1):
        row = execute_simulation(spec, f"demo-run-{i}")
        run_rows.append(row)
        event = make_openlineage_event(spec, row["run_id"], row["status"], row["started_at"], row["ended_at"])
        (ROOT / "reports" / f"{spec.pipeline_id}.openlineage.json").write_text(json.dumps(event, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({
        "pipelines_loaded": len(specs),
        "plans_generated": len(plans),
        "dbt_models_generated": len(list((ROOT/"generated").glob("stg_*.sql"))),
        "governance_policies": len(plans),
        "dbt_source_definitions_generated": len({spec.source.system for spec in specs}),
        "artifact_manifest_generated": (ROOT / "generated" / "generated_manifest.json").exists(),
        "simulated_runs": len(run_rows),
        "statuses": {r["pipeline_id"]: r["status"] for r in run_rows},
        "output_dir": str(ROOT/"generated"),
        "run_history": str(ROOT/"reports/run_history.jsonl"),
        "note": "local orchestration simulation; no Airflow, Dagster, source, warehouse, or OpenLineage backend invoked"
    }, indent=2))

if __name__ == "__main__":
    main()
````


## B.5 `configs/customers.yaml`

````yaml
schema_version: "3.0"
pipeline_id: "crm_customers"
description: "Ingest customer master records from CRM"
source:
  system: "crm"
  object: "customers"
  connector: "csv_file"
  connection_ref: "local.crm_customers"
  extraction_mode: "incremental"
  keys: ["customer_id"]
  columns: ["customer_id", "email", "full_name", "updated_at"]
  dbt_schema: "crm_raw"
  watermark: "updated_at"
  cdc_cursor: null
target:
  layer: "bronze"
  dataset: "crm_customers"
quality_checks:
  - type: "not_null"
    column: "customer_id"
  - type: "unique"
    column: "customer_id"
  - type: "not_null"
    column: "updated_at"
schedule: "0 * * * *"
owner: "crm-data@example.com"
classification: "confidential"
retention_days: 365
tags: ["customer", "crm"]
custom_logic: null
````


## B.6 `configs/orders.yaml`

````yaml
schema_version: "3.0"
pipeline_id: "commerce_orders"
description: "Ingest orders from commerce export"
source:
  system: "commerce"
  object: "orders"
  connector: "csv_file"
  connection_ref: "local.commerce_orders"
  extraction_mode: "full"
  keys: ["order_id"]
  columns: ["order_id", "customer_id", "amount", "status"]
  dbt_schema: "commerce_raw"
  watermark: null
  cdc_cursor: null
target:
  layer: "bronze"
  dataset: "commerce_orders"
quality_checks:
  - type: "not_null"
    column: "order_id"
  - type: "unique"
    column: "order_id"
schedule: "*/15 * * * *"
owner: "commerce-analytics@example.com"
classification: "internal"
retention_days: 730
tags: ["orders", "commerce"]
custom_logic: null
````


## B.7 `configs/product_catalog.yaml`

````yaml
schema_version: "3.0"
pipeline_id: "erp_product_catalog"
description: "Ingest product catalogue from ERP extract"
source:
  system: "erp"
  object: "product_catalog"
  connector: "csv_file"
  connection_ref: "local.erp_products"
  extraction_mode: "incremental"
  keys: ["sku"]
  columns: ["sku", "name", "category", "modified_at"]
  dbt_schema: "erp_raw"
  watermark: "modified_at"
  cdc_cursor: null
target:
  layer: "silver"
  dataset: "erp_product_catalog"
quality_checks:
  - type: "not_null"
    column: "sku"
  - type: "unique"
    column: "sku"
schedule: "30 2 * * *"
owner: "product-data@example.com"
classification: "public"
retention_days: 1825
tags: ["product", "catalog"]
custom_logic: null
````


## B.8 `fixtures/legacy_customers_v1.yaml`

````yaml
schema_version: "1.0"
pipeline_id: "legacy_customers"
source_system: "crm"
source_object: "customers"
connector: "csv_file"
connection_ref: "local.crm_customers"
mode: "incremental"
primary_key: "customer_id"
watermark_column: "updated_at"
target_layer: "bronze"
target_dataset: "legacy_customers"
owner: "crm-data@example.com"
classification: "confidential"
retention_days: 365
schedule: "0 * * * *"
````


## B.9 `fixtures/expected_crm_plan_contract.json`

````json
{
  "pipeline_id": "crm_customers",
  "schema_version": "3.0",
  "target": {
    "layer": "bronze",
    "dataset": "crm_customers"
  },
  "schedule": "0 * * * *",
  "classification": "confidential",
  "mask_pii": true,
  "retention_days": 365,
  "checkpoint_key": "crm_customers:watermark"
}
````


## B.10 `schema/generate_json_schema.py`

````python
from pathlib import Path
import json
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from metadata_platform import PipelineSpec

out = Path(__file__).resolve().parent / "metadata-v3.schema.json"
out.write_text(json.dumps(PipelineSpec.model_json_schema(), indent=2) + "\n", encoding="utf-8")
print(out)
````


## B.11 `schema/metadata-v3.schema.json`

````json
{
  "$defs": {
    "QualityCheck": {
      "additionalProperties": false,
      "properties": {
        "type": {
          "enum": [
            "not_null",
            "unique",
            "accepted_values"
          ],
          "title": "Type",
          "type": "string"
        },
        "column": {
          "minLength": 1,
          "pattern": "^[A-Za-z_][A-Za-z0-9_]*$",
          "title": "Column",
          "type": "string"
        },
        "values": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Values"
        }
      },
      "required": [
        "type",
        "column"
      ],
      "title": "QualityCheck",
      "type": "object"
    },
    "SourceSpec": {
      "additionalProperties": false,
      "properties": {
        "system": {
          "minLength": 2,
          "pattern": "^[a-z][a-z0-9_-]*$",
          "title": "System",
          "type": "string"
        },
        "object": {
          "minLength": 1,
          "pattern": "^[a-zA-Z][a-zA-Z0-9_]*$",
          "title": "Object",
          "type": "string"
        },
        "connector": {
          "enum": [
            "csv_file",
            "http_api",
            "database"
          ],
          "title": "Connector",
          "type": "string"
        },
        "connection_ref": {
          "minLength": 3,
          "pattern": "^[A-Za-z0-9_.:-]+$",
          "title": "Connection Ref",
          "type": "string"
        },
        "extraction_mode": {
          "enum": [
            "full",
            "incremental",
            "cdc"
          ],
          "title": "Extraction Mode",
          "type": "string"
        },
        "keys": {
          "items": {
            "type": "string"
          },
          "minItems": 1,
          "title": "Keys",
          "type": "array"
        },
        "columns": {
          "items": {
            "type": "string"
          },
          "minItems": 1,
          "title": "Columns",
          "type": "array"
        },
        "dbt_schema": {
          "minLength": 1,
          "pattern": "^[A-Za-z_][A-Za-z0-9_]*$",
          "title": "Dbt Schema",
          "type": "string"
        },
        "watermark": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Watermark"
        },
        "cdc_cursor": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Cdc Cursor"
        }
      },
      "required": [
        "system",
        "object",
        "connector",
        "connection_ref",
        "extraction_mode",
        "keys",
        "columns",
        "dbt_schema"
      ],
      "title": "SourceSpec",
      "type": "object"
    },
    "TargetSpec": {
      "additionalProperties": false,
      "properties": {
        "layer": {
          "enum": [
            "bronze",
            "silver",
            "gold"
          ],
          "title": "Layer",
          "type": "string"
        },
        "dataset": {
          "pattern": "^[a-z][a-z0-9_]*$",
          "title": "Dataset",
          "type": "string"
        }
      },
      "required": [
        "layer",
        "dataset"
      ],
      "title": "TargetSpec",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "schema_version": {
      "const": "3.0",
      "title": "Schema Version",
      "type": "string"
    },
    "pipeline_id": {
      "pattern": "^[a-z][a-z0-9_]*$",
      "title": "Pipeline Id",
      "type": "string"
    },
    "description": {
      "minLength": 10,
      "title": "Description",
      "type": "string"
    },
    "source": {
      "$ref": "#/$defs/SourceSpec"
    },
    "target": {
      "$ref": "#/$defs/TargetSpec"
    },
    "quality_checks": {
      "items": {
        "$ref": "#/$defs/QualityCheck"
      },
      "minItems": 1,
      "title": "Quality Checks",
      "type": "array"
    },
    "schedule": {
      "title": "Schedule",
      "type": "string"
    },
    "owner": {
      "title": "Owner",
      "type": "string"
    },
    "classification": {
      "enum": [
        "public",
        "internal",
        "confidential",
        "restricted"
      ],
      "title": "Classification",
      "type": "string"
    },
    "retention_days": {
      "exclusiveMinimum": 0,
      "maximum": 36500,
      "title": "Retention Days",
      "type": "integer"
    },
    "tags": {
      "items": {
        "type": "string"
      },
      "title": "Tags",
      "type": "array"
    },
    "custom_logic": {
      "anyOf": [
        {
          "enum": [
            "normalize_phone_v1",
            "custom_api_pagination_v1"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Custom Logic"
    }
  },
  "required": [
    "schema_version",
    "pipeline_id",
    "description",
    "source",
    "target",
    "quality_checks",
    "schedule",
    "owner",
    "classification",
    "retention_days"
  ],
  "title": "PipelineSpec",
  "type": "object"
}
````


## B.12 `templates/staging_model.sql.j2`

````jinja
-- Generated from {{ pipeline.pipeline_id }} (schema {{ pipeline.schema_version }})
{{ dbt_config_line }}
select {{ columns | join(', ') }}
from {{ source_call }}
````


## B.13 `tests/test_platform.py`

````python
import json
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from metadata_platform import (
    GENERATOR_VERSION,
    ROOT,
    PipelineSpec,
    execute_simulation,
    generate_dbt_sources,
    generate_plan,
    governance_policy,
    load_all_specs,
    migrate_v1_to_v3,
    migrate_v2_to_v3,
    render_dbt_model,
    spec_digest,
    write_generated,
)


def test_three_configs_validate_and_have_unique_targets():
    specs = load_all_specs()
    assert len(specs) == 3
    assert len({spec.pipeline_id for spec in specs}) == 3
    assert len({(spec.target.layer, spec.target.dataset) for spec in specs}) == 3


def test_incremental_requires_watermark_and_column():
    raw = yaml.safe_load((ROOT / "configs/customers.yaml").read_text())
    raw["source"]["watermark"] = None
    with pytest.raises(ValidationError, match="requires source.watermark"):
        PipelineSpec.model_validate(raw)
    raw = yaml.safe_load((ROOT / "configs/customers.yaml").read_text())
    raw["source"]["watermark"] = "not_a_column"
    with pytest.raises(ValidationError, match="must appear in source.columns"):
        PipelineSpec.model_validate(raw)


def test_full_mode_rejects_watermark():
    raw = yaml.safe_load((ROOT / "configs/orders.yaml").read_text())
    raw["source"]["watermark"] = "updated_at"
    with pytest.raises(ValidationError, match="full extraction"):
        PipelineSpec.model_validate(raw)


def test_cdc_uses_log_cursor_not_column_watermark():
    raw = yaml.safe_load((ROOT / "configs/orders.yaml").read_text())
    raw["source"]["extraction_mode"] = "cdc"
    raw["source"]["cdc_cursor"] = None
    with pytest.raises(ValidationError, match="requires source.cdc_cursor"):
        PipelineSpec.model_validate(raw)
    raw["source"]["cdc_cursor"] = "lsn"
    raw["source"]["watermark"] = None
    spec = PipelineSpec.model_validate(raw)
    assert spec.source.cdc_cursor == "lsn"


def test_unknown_fields_fail_closed():
    raw = yaml.safe_load((ROOT / "configs/orders.yaml").read_text())
    raw["dangerous_unreviewed_option"] = True
    with pytest.raises(ValidationError, match="Extra inputs"):
        PipelineSpec.model_validate(raw)


def test_sensitive_classification_requires_not_null_for_every_key():
    raw = yaml.safe_load((ROOT / "configs/customers.yaml").read_text())
    raw["source"]["keys"] = ["customer_id", "tenant_id"]
    raw["source"]["columns"].append("tenant_id")
    with pytest.raises(ValidationError, match="tenant_id"):
        PipelineSpec.model_validate(raw)


def test_quality_check_columns_must_exist():
    raw = yaml.safe_load((ROOT / "configs/orders.yaml").read_text())
    raw["quality_checks"][0]["column"] = "missing_column"
    with pytest.raises(ValidationError, match="unknown source columns"):
        PipelineSpec.model_validate(raw)


def test_invalid_cron_ranges_fail():
    raw = yaml.safe_load((ROOT / "configs/orders.yaml").read_text())
    raw["schedule"] = "99 * * * *"
    with pytest.raises(ValidationError, match="invalid cron field"):
        PipelineSpec.model_validate(raw)


def test_governance_driven_by_classification_retention_and_owner():
    specs = {spec.pipeline_id: spec for spec in load_all_specs()}
    conf = governance_policy(specs["crm_customers"])
    pub = governance_policy(specs["erp_product_catalog"])
    assert conf["masking"]["mask_pii"] is True
    assert conf["retention"]["days"] == 365
    assert conf["owner_notifications"]["recipient"] == "crm-data@example.com"
    assert conf["retention"]["enforcement_status"] == "policy_artifact_only"
    assert pub["masking"]["mask_pii"] is False
    assert pub["retention"]["days"] == 1825


def test_generator_outputs_match_fixture_contract_and_include_sources(tmp_path):
    plans = write_generated(output_dir=tmp_path)
    assert len(plans) == 3
    plan = json.loads((tmp_path / "crm_customers.plan.json").read_text())
    sql = (tmp_path / "stg_crm_customers.sql").read_text()
    assert plan["pipeline_id"] == "crm_customers"
    assert plan["generator_version"] == GENERATOR_VERSION
    assert plan["execution"]["checkpoint_key"] == "crm_customers:watermark"
    expected = json.loads((ROOT / "fixtures/expected_crm_plan_contract.json").read_text())
    actual = {
        "pipeline_id": plan["pipeline_id"], "schema_version": plan["schema_version"],
        "target": plan["target"], "schedule": plan["schedule"],
        "classification": plan["governance"]["classification"],
        "mask_pii": plan["governance"]["masking"]["mask_pii"],
        "retention_days": plan["governance"]["retention"]["days"],
        "checkpoint_key": plan["execution"]["checkpoint_key"],
    }
    assert actual == expected
    assert "source('crm', 'customers')" in sql
    assert "customer_id" in sql
    sources = yaml.safe_load((tmp_path / "sources.yml").read_text())
    assert sources["version"] == 2
    assert {source["name"] for source in sources["sources"]} == {"crm", "commerce", "erp"}
    assert (tmp_path / "governance_policies.json").exists()
    manifest = json.loads((tmp_path / "generated_manifest.json").read_text())
    assert manifest["generator_version"] == GENERATOR_VERSION
    assert "sources.yml" in manifest["artifacts"]


def test_generator_supports_new_source_without_hardcoded_column_map(tmp_path):
    raw = yaml.safe_load((ROOT / "configs/customers.yaml").read_text())
    raw["pipeline_id"] = "crm_contacts"
    raw["source"]["object"] = "contacts"
    raw["source"]["columns"] = ["contact_id", "email", "updated_at"]
    raw["source"]["keys"] = ["contact_id"]
    raw["quality_checks"] = [
        {"type": "not_null", "column": "contact_id"},
        {"type": "unique", "column": "contact_id"},
        {"type": "not_null", "column": "updated_at"},
    ]
    raw["target"]["dataset"] = "crm_contacts"
    raw["description"] = "Ingest CRM contact records"
    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    for path in (ROOT / "configs").glob("*.yaml"):
        (config_dir / path.name).write_text(path.read_text())
    (config_dir / "contacts.yaml").write_text(yaml.safe_dump(raw, sort_keys=False))
    output_dir = tmp_path / "out"
    write_generated(config_dir=config_dir, output_dir=output_dir)
    sql = (output_dir / "stg_crm_contacts.sql").read_text()
    assert "contact_id" in sql and "source('crm', 'contacts')" in sql


def test_sql_identifier_injection_rejected():
    spec = load_all_specs()[0]
    with pytest.raises(ValueError, match="unsafe column"):
        render_dbt_model(spec, ["customer_id; drop table users"])


def test_v1_migration_yields_valid_v2_spec():
    raw = yaml.safe_load((ROOT / "fixtures/legacy_customers_v1.yaml").read_text())
    migrated = migrate_v1_to_v3(raw)
    spec = PipelineSpec.model_validate(migrated)
    assert spec.schema_version == "3.0"
    assert spec.source.extraction_mode == "incremental"
    assert spec.source.watermark == "updated_at"
    assert spec.source.columns == ["customer_id", "updated_at"]
    assert {check.type for check in spec.quality_checks} == {"not_null", "unique"}


def test_migration_rejects_invalid_legacy_config_and_missing_fields():
    raw = yaml.safe_load((ROOT / "fixtures/legacy_customers_v1.yaml").read_text())
    raw["watermark_column"] = None
    with pytest.raises(ValueError, match="requires watermark"):
        migrate_v1_to_v3(raw)
    raw = yaml.safe_load((ROOT / "fixtures/legacy_customers_v1.yaml").read_text())
    del raw["primary_key"]
    with pytest.raises(ValueError, match="missing required fields"):
        migrate_v1_to_v3(raw)



def test_v2_to_v3_migration_adds_explicit_schema_metadata():
    raw = yaml.safe_load((ROOT / "configs/customers.yaml").read_text())
    raw["schema_version"] = "2.0"
    for field in ("columns", "dbt_schema", "cdc_cursor"):
        raw["source"].pop(field, None)
    migrated = migrate_v2_to_v3(raw)
    spec = PipelineSpec.model_validate(migrated)
    assert spec.schema_version == "3.0"
    assert spec.source.columns == ["customer_id", "updated_at"]  # inferred subset; human schema enrichment is required
    assert spec.source.dbt_schema == "crm"


def test_migration_rejects_ambiguous_legacy_cdc():
    raw = yaml.safe_load((ROOT / "fixtures/legacy_customers_v1.yaml").read_text())
    raw["mode"] = "cdc"
    with pytest.raises(ValueError, match="manual mapping"):
        migrate_v1_to_v3(raw)


def test_run_history_records_simulation_not_successful_ingestion(tmp_path):
    spec = load_all_specs()[0]
    history = tmp_path / "history.jsonl"
    row = execute_simulation(spec, "test-run-1", history)
    assert row["status"] == "SIMULATED"
    assert row["execution_mode"] == "local_simulation"
    assert row["checkpoint"]["advanced"] is False
    saved = json.loads(history.read_text().splitlines()[0])
    assert saved["run_id"] == "test-run-1"
    assert saved["config_digest"] == row["config_digest"]


def test_simulation_lineage_event_uses_valid_other_event_type():
    from metadata_platform import make_openlineage_event
    spec = load_all_specs()[0]
    row = execute_simulation(spec, "lineage-run", ROOT / "reports" / "test_history.jsonl")
    event = make_openlineage_event(spec, row["run_id"], row["status"], row["started_at"], row["ended_at"])
    assert event["eventType"] == "OTHER"
    assert "simulation only" in event["job"]["facets"]["documentation"]["description"].lower()
    (ROOT / "reports" / "test_history.jsonl").unlink(missing_ok=True)


def test_blank_run_id_rejected(tmp_path):
    with pytest.raises(ValueError, match="run_id must not be blank"):
        execute_simulation(load_all_specs()[0], "  ", tmp_path / "history.jsonl")


def test_deterministic_plans_and_manifest_digests(tmp_path):
    specs = load_all_specs()
    first = write_generated(output_dir=tmp_path / "first")
    second = write_generated(output_dir=tmp_path / "second")
    assert first == second
    manifest_a = json.loads((tmp_path / "first/generated_manifest.json").read_text())
    manifest_b = json.loads((tmp_path / "second/generated_manifest.json").read_text())
    assert manifest_a["artifacts"] == manifest_b["artifacts"]
    assert generate_plan(specs[0])["config_digest"] == spec_digest(specs[0])


def test_exported_json_schema_matches_pydantic_model():
    exported = json.loads((ROOT / "schema/metadata-v3.schema.json").read_text())
    assert exported["properties"]["schema_version"]["const"] == "3.0"
    assert "source" in exported["properties"]
    assert "columns" in exported["$defs"]["SourceSpec"]["properties"]
    assert "dbt_schema" in exported["$defs"]["SourceSpec"]["properties"]
````


## B.14 `data/data_customers.csv`

````csv
customer_id,email,full_name,updated_at
1,alice@example.com,Alice Smith,2026-10-18T09:00:00Z
2,bob@example.com,Bob Jones,2026-10-18T10:00:00Z
````


## B.15 `data/data_orders.csv`

````csv
order_id,customer_id,amount,status
O-100,1,49.95,paid
O-101,2,19.50,pending
````


## B.16 `data/data_products.csv`

````csv
sku,name,category,modified_at
SKU-1,Widget,hardware,2026-10-18T08:00:00Z
SKU-2,Gadget,electronics,2026-10-18T08:30:00Z
````


## B.17 `generated/crm_customers.plan.json`

````json
{
  "pipeline_id": "crm_customers",
  "schema_version": "3.0",
  "generator_version": "0.2.0",
  "config_digest": "6c4fd3104126d9fd73f09ca768b773f854c4278154dd483c901fbea30ac36275",
  "source": {
    "system": "crm",
    "object": "customers",
    "connector": "csv_file",
    "connection_ref": "local.crm_customers",
    "extraction_mode": "incremental",
    "keys": [
      "customer_id"
    ],
    "columns": [
      "customer_id",
      "email",
      "full_name",
      "updated_at"
    ],
    "dbt_schema": "crm_raw",
    "watermark": "updated_at",
    "cdc_cursor": null
  },
  "target": {
    "layer": "bronze",
    "dataset": "crm_customers"
  },
  "schedule": "0 * * * *",
  "owner": "crm-data@example.com",
  "quality_checks": [
    {
      "type": "not_null",
      "column": "customer_id",
      "values": null
    },
    {
      "type": "unique",
      "column": "customer_id",
      "values": null
    },
    {
      "type": "not_null",
      "column": "updated_at",
      "values": null
    }
  ],
  "governance": {
    "pipeline_id": "crm_customers",
    "classification": "confidential",
    "masking": {
      "mask_pii": true,
      "policy": "mask_email_phone_in_nonprod"
    },
    "retention": {
      "days": 365,
      "action": "expire_or_delete_after_retention",
      "enforcement_status": "policy_artifact_only"
    },
    "owner": "crm-data@example.com",
    "owner_notifications": {
      "on_failure": true,
      "on_quality_failure": true,
      "recipient": "crm-data@example.com"
    },
    "access_review_required": true,
    "enforcement_status": "policy_artifact_only"
  },
  "execution": {
    "mode": "local_simulation",
    "checkpoint_key": "crm_customers:watermark",
    "retry_policy": {
      "max_attempts": 3,
      "backoff": "exponential"
    },
    "idempotency_key": "pipeline_id + source_window + config_digest",
    "custom_logic_requested": null,
    "custom_logic_executed": false
  }
}
````


## B.18 `generated/commerce_orders.plan.json`

````json
{
  "pipeline_id": "commerce_orders",
  "schema_version": "3.0",
  "generator_version": "0.2.0",
  "config_digest": "6c7805cbb9acc5c479069a78d811f262901305989ce4391e393bf60731ad3997",
  "source": {
    "system": "commerce",
    "object": "orders",
    "connector": "csv_file",
    "connection_ref": "local.commerce_orders",
    "extraction_mode": "full",
    "keys": [
      "order_id"
    ],
    "columns": [
      "order_id",
      "customer_id",
      "amount",
      "status"
    ],
    "dbt_schema": "commerce_raw",
    "watermark": null,
    "cdc_cursor": null
  },
  "target": {
    "layer": "bronze",
    "dataset": "commerce_orders"
  },
  "schedule": "*/15 * * * *",
  "owner": "commerce-analytics@example.com",
  "quality_checks": [
    {
      "type": "not_null",
      "column": "order_id",
      "values": null
    },
    {
      "type": "unique",
      "column": "order_id",
      "values": null
    }
  ],
  "governance": {
    "pipeline_id": "commerce_orders",
    "classification": "internal",
    "masking": {
      "mask_pii": false,
      "policy": "internal_access_controls"
    },
    "retention": {
      "days": 730,
      "action": "expire_or_delete_after_retention",
      "enforcement_status": "policy_artifact_only"
    },
    "owner": "commerce-analytics@example.com",
    "owner_notifications": {
      "on_failure": true,
      "on_quality_failure": true,
      "recipient": "commerce-analytics@example.com"
    },
    "access_review_required": false,
    "enforcement_status": "policy_artifact_only"
  },
  "execution": {
    "mode": "local_simulation",
    "checkpoint_key": null,
    "retry_policy": {
      "max_attempts": 3,
      "backoff": "exponential"
    },
    "idempotency_key": "pipeline_id + source_window + config_digest",
    "custom_logic_requested": null,
    "custom_logic_executed": false
  }
}
````


## B.19 `generated/erp_product_catalog.plan.json`

````json
{
  "pipeline_id": "erp_product_catalog",
  "schema_version": "3.0",
  "generator_version": "0.2.0",
  "config_digest": "5850cc00008ba457db5faf1a1bf8689198d66c33c17b1ee66f1450e53de88264",
  "source": {
    "system": "erp",
    "object": "product_catalog",
    "connector": "csv_file",
    "connection_ref": "local.erp_products",
    "extraction_mode": "incremental",
    "keys": [
      "sku"
    ],
    "columns": [
      "sku",
      "name",
      "category",
      "modified_at"
    ],
    "dbt_schema": "erp_raw",
    "watermark": "modified_at",
    "cdc_cursor": null
  },
  "target": {
    "layer": "silver",
    "dataset": "erp_product_catalog"
  },
  "schedule": "30 2 * * *",
  "owner": "product-data@example.com",
  "quality_checks": [
    {
      "type": "not_null",
      "column": "sku",
      "values": null
    },
    {
      "type": "unique",
      "column": "sku",
      "values": null
    }
  ],
  "governance": {
    "pipeline_id": "erp_product_catalog",
    "classification": "public",
    "masking": {
      "mask_pii": false,
      "policy": "no_default_masking"
    },
    "retention": {
      "days": 1825,
      "action": "expire_or_delete_after_retention",
      "enforcement_status": "policy_artifact_only"
    },
    "owner": "product-data@example.com",
    "owner_notifications": {
      "on_failure": true,
      "on_quality_failure": true,
      "recipient": "product-data@example.com"
    },
    "access_review_required": false,
    "enforcement_status": "policy_artifact_only"
  },
  "execution": {
    "mode": "local_simulation",
    "checkpoint_key": "erp_product_catalog:watermark",
    "retry_policy": {
      "max_attempts": 3,
      "backoff": "exponential"
    },
    "idempotency_key": "pipeline_id + source_window + config_digest",
    "custom_logic_requested": null,
    "custom_logic_executed": false
  }
}
````


## B.20 `generated/stg_crm_customers.sql`

````sql
-- Generated from crm_customers (schema 3.0)
{{ config(materialized='view', tags=['customer', 'crm']) }}
select customer_id, email, full_name, updated_at
from {{ source('crm', 'customers') }}
````


## B.21 `generated/stg_commerce_orders.sql`

````sql
-- Generated from commerce_orders (schema 3.0)
{{ config(materialized='view', tags=['orders', 'commerce']) }}
select order_id, customer_id, amount, status
from {{ source('commerce', 'orders') }}
````


## B.22 `generated/stg_erp_product_catalog.sql`

````sql
-- Generated from erp_product_catalog (schema 3.0)
{{ config(materialized='view', tags=['product', 'catalog']) }}
select sku, name, category, modified_at
from {{ source('erp', 'product_catalog') }}
````


## B.23 `generated/sources.yml`

````yaml
version: 2
sources:
- name: crm
  schema: crm_raw
  tables:
  - name: customers
    description: Landing relation for crm_customers
- name: commerce
  schema: commerce_raw
  tables:
  - name: orders
    description: Landing relation for commerce_orders
- name: erp
  schema: erp_raw
  tables:
  - name: product_catalog
    description: Landing relation for erp_product_catalog
````


## B.24 `generated/governance_policies.json`

````json
[
  {
    "pipeline_id": "crm_customers",
    "classification": "confidential",
    "masking": {
      "mask_pii": true,
      "policy": "mask_email_phone_in_nonprod"
    },
    "retention": {
      "days": 365,
      "action": "expire_or_delete_after_retention",
      "enforcement_status": "policy_artifact_only"
    },
    "owner": "crm-data@example.com",
    "owner_notifications": {
      "on_failure": true,
      "on_quality_failure": true,
      "recipient": "crm-data@example.com"
    },
    "access_review_required": true,
    "enforcement_status": "policy_artifact_only"
  },
  {
    "pipeline_id": "commerce_orders",
    "classification": "internal",
    "masking": {
      "mask_pii": false,
      "policy": "internal_access_controls"
    },
    "retention": {
      "days": 730,
      "action": "expire_or_delete_after_retention",
      "enforcement_status": "policy_artifact_only"
    },
    "owner": "commerce-analytics@example.com",
    "owner_notifications": {
      "on_failure": true,
      "on_quality_failure": true,
      "recipient": "commerce-analytics@example.com"
    },
    "access_review_required": false,
    "enforcement_status": "policy_artifact_only"
  },
  {
    "pipeline_id": "erp_product_catalog",
    "classification": "public",
    "masking": {
      "mask_pii": false,
      "policy": "no_default_masking"
    },
    "retention": {
      "days": 1825,
      "action": "expire_or_delete_after_retention",
      "enforcement_status": "policy_artifact_only"
    },
    "owner": "product-data@example.com",
    "owner_notifications": {
      "on_failure": true,
      "on_quality_failure": true,
      "recipient": "product-data@example.com"
    },
    "access_review_required": false,
    "enforcement_status": "policy_artifact_only"
  }
]
````


## B.25 `generated/generated_manifest.json`

````json
{
  "schema_version": "3.0",
  "generator_version": "0.2.0",
  "artifacts": {
    "commerce_orders.plan.json": "c3c2a7bf44c06b612468008fd9ce7d521e1e6fa867c1ac446b63c7fa91a86694",
    "crm_customers.plan.json": "883a2b58ea884db6458fda2a0ea1e3fc6926905d416577d68db3ed471d96cc87",
    "erp_product_catalog.plan.json": "fcb956d92335828fab0c477c310e3e841b96e9a655da0908944110394e31e61a",
    "governance_policies.json": "8526d2155502204ee0bbcb6f38c0ba60c3930363da11d58a098543d4378017d7",
    "sources.yml": "8fdf187c771a6c4293f82661c09db8a282090282f82cb4ece3661c8f0261667f",
    "stg_commerce_orders.sql": "59e6f24db8250cf99fbc56cca30ea0d551c94623b7644bdd5e444b76c921a5b3",
    "stg_crm_customers.sql": "6833e5b44e6827de0885850458feece57d99c2dd60b6f9e70435751213161608",
    "stg_erp_product_catalog.sql": "74a3cc64c02abba767672840492899a3b11be044d34fc82f74822b73d74a88eb"
  }
}
````


## B.26 `reports/run_history.jsonl`

````jsonl
{"run_id": "demo-run-1", "pipeline_id": "crm_customers", "status": "SIMULATED", "execution_mode": "local_simulation", "started_at": "2026-10-19T09:03:56.393112+00:00", "ended_at": "2026-10-19T09:03:56.393221+00:00", "config_digest": "6c4fd3104126d9fd73f09ca768b773f854c4278154dd483c901fbea30ac36275", "generator_version": "0.2.0", "error": null, "checkpoint": {"key": "crm_customers:watermark", "value": null, "advanced": false}}
{"run_id": "demo-run-2", "pipeline_id": "commerce_orders", "status": "SIMULATED", "execution_mode": "local_simulation", "started_at": "2026-10-19T09:03:56.394381+00:00", "ended_at": "2026-10-19T09:03:56.394469+00:00", "config_digest": "6c7805cbb9acc5c479069a78d811f262901305989ce4391e393bf60731ad3997", "generator_version": "0.2.0", "error": null, "checkpoint": null}
{"run_id": "demo-run-3", "pipeline_id": "erp_product_catalog", "status": "SIMULATED", "execution_mode": "local_simulation", "started_at": "2026-10-19T09:03:56.394730+00:00", "ended_at": "2026-10-19T09:03:56.394987+00:00", "config_digest": "5850cc00008ba457db5faf1a1bf8689198d66c33c17b1ee66f1450e53de88264", "generator_version": "0.2.0", "error": null, "checkpoint": {"key": "erp_product_catalog:watermark", "value": null, "advanced": false}}
````


## B.27 `reports/crm_customers.openlineage.json`

````json
{
  "eventType": "OTHER",
  "eventTime": "2026-10-19T09:03:56.393221+00:00",
  "run": {
    "runId": "demo-run-1"
  },
  "job": {
    "namespace": "urn:metadata-platform-lab:job",
    "name": "crm_customers",
    "facets": {
      "documentation": {
        "description": "Local simulation only; no data-plane execution occurred."
      }
    }
  },
  "inputs": [
    {
      "namespace": "urn:metadata-platform-lab:source:crm",
      "name": "customers"
    }
  ],
  "outputs": [
    {
      "namespace": "urn:metadata-platform-lab:target:bronze",
      "name": "crm_customers"
    }
  ],
  "producer": "https://example.invalid/metadata-platform-lab",
  "schemaURL": "https://openlineage.io/spec/2-0-2/OpenLineage.json"
}
````


## B.28 `reports/commerce_orders.openlineage.json`

````json
{
  "eventType": "OTHER",
  "eventTime": "2026-10-19T09:03:56.394469+00:00",
  "run": {
    "runId": "demo-run-2"
  },
  "job": {
    "namespace": "urn:metadata-platform-lab:job",
    "name": "commerce_orders",
    "facets": {
      "documentation": {
        "description": "Local simulation only; no data-plane execution occurred."
      }
    }
  },
  "inputs": [
    {
      "namespace": "urn:metadata-platform-lab:source:commerce",
      "name": "orders"
    }
  ],
  "outputs": [
    {
      "namespace": "urn:metadata-platform-lab:target:bronze",
      "name": "commerce_orders"
    }
  ],
  "producer": "https://example.invalid/metadata-platform-lab",
  "schemaURL": "https://openlineage.io/spec/2-0-2/OpenLineage.json"
}
````


## B.29 `reports/erp_product_catalog.openlineage.json`

````json
{
  "eventType": "OTHER",
  "eventTime": "2026-10-19T09:03:56.394987+00:00",
  "run": {
    "runId": "demo-run-3"
  },
  "job": {
    "namespace": "urn:metadata-platform-lab:job",
    "name": "erp_product_catalog",
    "facets": {
      "documentation": {
        "description": "Local simulation only; no data-plane execution occurred."
      }
    }
  },
  "inputs": [
    {
      "namespace": "urn:metadata-platform-lab:source:erp",
      "name": "product_catalog"
    }
  ],
  "outputs": [
    {
      "namespace": "urn:metadata-platform-lab:target:silver",
      "name": "erp_product_catalog"
    }
  ],
  "producer": "https://example.invalid/metadata-platform-lab",
  "schemaURL": "https://openlineage.io/spec/2-0-2/OpenLineage.json"
}
````


## Appendix B verification boundary

`python run_lab.py` creates local plans, SQL, policy artifacts, run-history rows marked `SIMULATED`, and OpenLineage-shaped `OTHER` events. It does not execute ingestion, launch Airflow or Dagster, compile dbt, enforce masking or retention, send notifications, or transmit lineage.
