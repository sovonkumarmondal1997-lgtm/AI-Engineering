# Documentation, Lineage, and Exposures in dbt

> **Roadmap location:** `Stage 2C — Data Engineering_3/06-dbt-and-Analytics-Engineering/05-documentation-lineage-and-exposures.md`  
> **Scope:** Consumer-oriented documentation, dbt's dependency graph, exposures, governance metadata, persisted warehouse comments, artifacts, impact analysis, and external catalogue publishing.  
> **Prerequisites:** A working dbt project; `ref()` and `source()`; staging, intermediate, and mart models; YAML; tests and contracts from Topic 04.  
> **Project continuity:** This lesson continues with `stg_orders`, `stg_order_items`, `stg_customers`, `int_orders_payments`, `fct_orders`, and `dim_customers`.

## Learning outcomes

By completing this lesson, you will be able to:

- Describe models, columns, and sources in YAML for analysts and downstream consumers.
- Generate and serve dbt documentation and navigate the model DAG.
- Reuse documentation with `{% docs %}` blocks.
- Declare dashboard and machine-learning feature-set exposures, with owners and maturity.
- Use `meta`, tags, and `persist_docs` for governance and warehouse discoverability.
- Add documentation-coverage checks to CI.
- Explain and parse `manifest.json`, `catalog.json`, and `run_results.json` without confusing their roles.
- Identify upstream and downstream impact from manifest dependencies.
- Understand the limits of column-level lineage, OpenLineage, and external catalogue integrations.
- Build a maintainable documentation and lineage workflow rather than treating docs as a one-time exercise.

---

## 1. Why documentation and lineage are engineering controls

A model that builds successfully can still be difficult to trust. A column called `revenue` does not tell a consumer whether it is gross revenue, net revenue, recognized revenue, or a sum of order totals. A dashboard can depend on a model without its owner knowing that the model is changing. A downstream feature set can silently inherit a breaking change.

Documentation and lineage reduce these risks by making the intended meaning and dependency structure discoverable.

| Control | Answers | Does not guarantee |
|---|---|---|
| Model/column/source descriptions | What does this object mean and how should it be used? | That the description is true or up to date |
| dbt DAG / manifest dependencies | What depends on what in the declared dbt project? | All runtime dependencies outside dbt |
| Exposure | Which named downstream consumer is declared to depend on dbt resources? | That the consumer is automatically discovered or that its deployment is healthy |
| `meta` and tags | What governance labels or routing hints have been declared? | Enforcement by themselves |
| `persist_docs` | Can descriptions be copied to supported warehouse comments? | That every adapter supports every comment type, or that comments are synchronized continuously |
| Artifact parser | What can be derived from a particular generated artifact? | That stale or incomplete artifacts represent current production state |
| External catalogue | How does the wider organization search and govern data assets? | Complete or identical lineage semantics across all products |

### The four metadata planes

Keep these concepts separate when debugging or designing governance.

1. **Declared dbt metadata** — YAML and project configuration authored in Git: descriptions, owners, tags, `meta`, exposures, and dependency declarations.
2. **Generated dbt artifacts** — files produced by commands, notably `manifest.json`, `catalog.json`, and `run_results.json`. These are snapshots of a particular invocation/environment and can become stale.
3. **Actual warehouse metadata** — relation and column comments, schemas, data types, permissions, and physical objects that exist in the warehouse. `persist_docs` may publish descriptions into this plane when supported.
4. **External catalogue information** — assets, owners, policies, lineage, classifications, and glossary terms ingested or curated in tools such as Purview, DataHub, OpenMetadata, or Dataplex. It may combine dbt metadata with warehouse, orchestration, BI, and other integrations.

These planes can disagree. For example, a YAML description may be correct in Git while the warehouse comment is old because the latest deployment did not run; a catalogue may show an old manifest; or a warehouse relation may be created outside dbt and therefore be absent from the dbt DAG.

---

## 2. Beginner: write documentation for consumers

### 2.1 Model, column, and source descriptions

Descriptions belong in YAML, normally in a model properties file such as `models/marts/marts.yml`. Write for the person using the model, not for the person who wrote the SQL.

A useful description answers:

- **Meaning:** What does the model or column represent?
- **Grain:** What does one row represent?
- **Business rules:** Which filters, deduplication, or definitions matter?
- **Nullability and caveats:** When can a value be missing or approximate?
- **Safe use:** What should a downstream analyst avoid assuming?

Weak: `Revenue for orders.`

Stronger: `Net order revenue in the reporting currency, at one row per order. Cancelled orders are excluded; refunds are not deducted in this model. Use the finance-approved net-revenue model for recognized revenue.`

Example `models/marts/marts.yml`:

```yaml
version: 2

models:
  - name: fct_orders
    description: >
      One row per order. Contains order-level totals and lifecycle dates
      for operational and commercial analysis. Cancelled orders are
      excluded from the reported order count. This model's order total
      is not the same as recognized accounting revenue.
    config:
      meta:
        owner: analytics-engineering
        domain: commerce
        contains_pii: false
        sla: "daily by 07:00 UTC"
    columns:
      - name: order_id
        description: Stable business identifier for one order.
        data_tests:
          - not_null
          - unique
      - name: customer_id
        description: >
          Identifier of the customer associated with the order. Join to
          dim_customers using this key; it is not a customer name.
        data_tests:
          - not_null
      - name: order_date
        description: Calendar date on which the order was placed.
      - name: order_total
        description: >
          Total amount for the order in the model's reporting currency.
          Confirm refund and tax treatment before using it as a finance
          metric.
      - name: status
        description: Normalized lifecycle status for the order.

  - name: dim_customers
    description: >
      One row per customer in the current customer dimension. Includes
      customer attributes used for segmentation. Access to identifying
      attributes is governed separately from this model description.
    config:
      meta:
        owner: analytics-engineering
        domain: customer
        contains_pii: true
        sla: "daily by 07:00 UTC"
    columns:
      - name: customer_id
        description: Stable customer key used to join customer-level facts.
        data_tests:
          - not_null
          - unique
      - name: first_order_date
        description: Date of the customer's first qualifying order, if any.
      - name: lifetime_order_count
        description: Number of qualifying orders represented in the model.
```

**Version note:** dbt's schema-property syntax evolves. The `data_tests` spelling is used by current dbt versions; older projects may use `tests`. Keep the syntax consistent with the installed dbt version and adapter. Do not put sensitive personal data in a description or `meta` field.

Descriptions are contracts with human consumers, not substitutes for tests. If the description says one row per order, test uniqueness of `order_id`. If it says cancelled orders are excluded, test or reconcile that rule where feasible.

### 2.2 Describe sources

A source description explains the upstream system, ownership, freshness expectations, and important source semantics. Example `models/staging/sources.yml`:

```yaml
version: 2

sources:
  - name: commerce
    description: >
      Raw commerce application data landed in the analytics warehouse.
      Source tables retain upstream identifiers and may contain late
      updates; staging models normalize names and types.
    database: raw
    schema: commerce
    config:
      meta:
        owner: data-platform
        domain: commerce
        source_system: commerce_app
    tables:
      - name: orders
        description: One source record per order identifier; records may be updated after creation.
        columns:
          - name: order_id
            description: Upstream order identifier.
          - name: customer_id
            description: Upstream customer identifier.
      - name: order_items
        description: Order line items; an order can have multiple rows.
      - name: customers
        description: Source customer records, including attributes that may be personal data.
```

The physical `database` and `schema` must match your warehouse. In some adapters, database/catalog naming differs. `source()` establishes a declared dependency and lets dbt use source metadata and freshness features; it does not ingest the source data.

A staging model can use `{{ source('commerce', 'orders') }}` and a mart can use `{{ ref('stg_orders') }}`. Prefer `source()` and `ref()` over hard-coded relation names so the graph can represent dependencies.

### 2.3 Write descriptions in Markdown

YAML folded scalars (`>`) make multi-line descriptions easier to read in Git. Descriptions can include Markdown, such as inline code, lists, links, and short caveats. Keep them readable in the docs site and avoid enormous paragraphs.

Example:

```yaml
      - name: order_total
        description: >
          **Order-level amount** in the reporting currency.

          - Includes: item amounts and the order-level adjustments defined
            in the transformation.
          - Excludes: recognized-revenue accounting adjustments.
          - Consumer note: use the approved finance metric for reporting
            recognized revenue.
```

Only document business semantics that are actually implemented and verified in the SQL. If the rule is uncertain, mark it as a question to resolve rather than presenting an assumption as fact.

### 2.4 Reusable documentation blocks

When the same definition is used by several models, put it in a docs block. Create `docs/metrics.md`:

```jinja
{% docs order_total_definition %}
**Order total** is the order-level amount in the reporting currency.

It follows the transformation's order-total logic. It must not be
interpreted as recognized accounting revenue unless the finance definition
explicitly says so.
{% enddocs %}
```

Reference it from a YAML description:

```yaml
version: 2

models:
  - name: fct_orders
    description: >
      One row per order for operational and commercial analysis.
    columns:
      - name: order_total
        description: "{{ doc('order_total_definition') }}"
```

A docs block is reusable authored text. It does not calculate a metric, inspect the SQL, or automatically prove that the implementation matches the definition. Use a single source of truth for shared definitions and update all affected descriptions when the definition changes.

### 2.5 Generate and serve documentation

Run from the dbt project root in the environment configured for the target profile:

```bash
dbt parse
dbt docs generate
dbt docs serve
```

- `dbt parse` checks project parsing and writes a manifest without running model SQL.
- `dbt docs generate` generates the documentation site inputs, including a manifest and catalog information. Catalog collection queries the warehouse and can require relations to exist and the adapter credentials to have metadata access.
- `dbt docs serve` starts a local web server for the generated documentation. It is intended for local inspection, not as a production hosting solution.

For a first build, run `dbt build` before `dbt docs generate` if models and relations do not yet exist. Some project/adapter configurations can generate only partial catalog information if relations are missing or inaccessible. `dbt docs generate` does not build the models for you.

The docs site combines model/source descriptions with the lineage graph and warehouse-derived catalog details. It is not proof that a relation is fresh or that its values are correct.

### 2.6 Understand the DAG

The dbt directed acyclic graph (DAG) shows declared dependencies. An edge points from an upstream dependency to the downstream resource that depends on it.

Example:

```text
source.commerce.orders ──> stg_orders ───────────┐
                                                  ├──> int_orders_payments ──> fct_orders
source.commerce.order_items -> stg_order_items ──┘                           │
                                                                            └──> dashboard exposure
stg_customers ────────────────────────────────────────────────────────────────> dim_customers
                                                                                 │
                                                                                 └──> ML feature-set exposure
```

The precise graph depends on the SQL and `ref()`/`source()` calls. An exposure is a declared downstream consumer, not a model that dbt materializes.

Useful selection examples:

```bash
# Build one model and its ancestors
dbt build --select +fct_orders

# Select the model and descendants
dbt ls --select fct_orders+

# Select the model, ancestors, and descendants
dbt ls --select +fct_orders+

# Inspect the graph in the generated docs site
dbt docs generate
dbt docs serve
```

Selection syntax and behavior should be checked against the installed dbt version. The plus sign is a graph selector: `+model` selects ancestors, `model+` selects descendants, and `+model+` selects both directions. A model can have many descendants; inspect the actual graph before approving a breaking change.

---

## 3. Intermediate: exposures and governance metadata

### 3.1 What an exposure represents

An exposure declares a downstream asset that depends on dbt resources. It can represent a dashboard, notebook, application, or ML consumer. Exposures help answer: “If `fct_orders` changes, which declared consumers should be reviewed?”

Exposures are metadata, not deployment automation. dbt does not create the dashboard, retrain the model, or verify that the consumer uses the model as declared.

Create `models/marts/exposures.yml`:

```yaml
version: 2

exposures:
  - name: executive_commerce_dashboard
    label: Executive Commerce Dashboard
    type: dashboard
    maturity: high
    url: https://bi.example.invalid/dashboards/executive-commerce
    description: >
      Executive dashboard for order volume, order totals, and customer
      activity. Owners must review metric-definition or grain changes
      before deployment.
    owner:
      name: Commerce Analytics
      email: commerce-analytics@example.invalid
    depends_on:
      - ref('fct_orders')
      - ref('dim_customers')
    tags:
      - commerce
      - tier_1
    meta:
      domain: commerce
      sla: "daily by 07:00 UTC"
      change_review: required

  - name: customer_value_feature_set
    label: Customer Value ML Feature Set
    type: ml
    maturity: medium
    description: >
      Customer-level features used by the customer-value training and
      scoring pipeline. Review grain, leakage risk, and feature meaning
      before changing upstream models.
    owner:
      name: Applied ML
      email: applied-ml@example.invalid
    depends_on:
      - ref('dim_customers')
      - ref('fct_orders')
    tags:
      - customer
      - ml
    meta:
      domain: customer
      contains_pii: true
      review_before_release: true
```

The `.invalid` URLs and email addresses are deliberate placeholders; replace them with real, approved destinations and owners before use. Do not assume dbt validates URL reachability or verifies that the named owner still exists.

Common exposure types include `dashboard`, `notebook`, `analysis`, `ml`, and `application` in dbt versions that support them. Verify allowed values for your installed version. Maturity values are commonly `low`, `medium`, and `high`. `depends_on` should point to resources that actually feed the consumer, not merely resources that seem related.

### 3.2 `meta` versus tags versus descriptions

- **Description:** human-readable explanation of meaning and use.
- **Tags:** simple labels useful for grouping and selection; they are not a security boundary.
- **`meta`:** structured project-defined metadata that custom scripts and integrations can interpret.
- **Owner field:** an explicit owner on supported resource types (for example, exposure owner); model ownership is often expressed through a project convention in `meta`.
- **Tests:** executable assertions about data; a tag or description cannot replace a test.
- **Warehouse comments:** physical metadata published to the warehouse, where supported; not identical to YAML or external catalogue records.

A consistent convention might use `meta.owner`, `meta.domain`, `meta.contains_pii`, and `meta.sla`. These keys are **your governance schema**, not universally enforced dbt properties. Standardize casing and allowed values, document the policy, and make CI check it.

Example model-level metadata:

```yaml
models:
  - name: dim_customers
    config:
      meta:
        owner: customer-analytics
        domain: customer
        contains_pii: true
        sla: "daily by 07:00 UTC"
        classification: confidential
    tags:
      - customer
      - governed
```

A `contains_pii: true` declaration does not mask columns, restrict warehouse access, or satisfy legal obligations by itself. Enforce actual controls in the warehouse and relevant privacy systems. Avoid embedding personal data in metadata values.

### 3.3 `persist_docs`: publish descriptions as warehouse comments

In `dbt_project.yml`, configure persistence for models:

```yaml
name: analytics
version: "1.0.0"
config-version: 2
profile: analytics

model-paths: ["models"]
seed-paths: ["seeds"]
test-paths: ["tests"]
macro-paths: ["macros"]
docs-paths: ["docs"]

models:
  analytics:
    +persist_docs:
      relation: true
      columns: true
```

Merge this into the existing project file rather than replacing unrelated settings. The top-level project key under `models:` must match the project name. Some dbt configurations use different model paths or project names.

`relation: true` asks dbt to persist model/relation descriptions; `columns: true` asks it to persist column descriptions. Support and exact behavior depend on adapter, relation type, warehouse privileges, and dbt version. This setting is not a guarantee that every description reaches every warehouse object.

Verification workflow:

1. Add or update a model and column description in YAML.
2. Run the relevant model with the project's configured profile, for example `dbt build --select fct_orders`.
3. Query the warehouse's metadata/comments interface for the resulting relation and columns.
4. Compare the comments with the source YAML.
5. Repeat in the target deployment environment; a local DuckDB profile and production Snowflake profile can behave differently.

Illustrative SQL for a warehouse that exposes `information_schema.columns`:

```sql
-- Adapt the catalog/schema names and comment column to your warehouse.
select
    table_schema,
    table_name,
    column_name,
    comment
from information_schema.columns
where lower(table_name) = 'fct_orders'
order by ordinal_position;
```

This query is **not portable as written**: `comment` and metadata views differ among warehouses. For example, some engines expose comments in `information_schema`, others require vendor-specific metadata commands or views. Check the adapter documentation and use the appropriate catalog query. If comments are absent, check adapter support, privileges, whether the model ran, whether YAML was parsed, and whether the target relation is the expected one.

### 3.4 Documentation coverage in CI

Two ecosystem tools can help surface missing documentation and governance gaps:

- **`dbt-project-evaluator`**: project-level checks. The invocation is version-sensitive: the 1.x package line uses dbt models/tests and is commonly run with `dbt build --select package:dbt_project_evaluator`; the 2.x line is designed for dbt 2.x and uses native `dbt check` rules. Do not combine a 2.x package with a dbt Core 1.x project or assume the 1.x invocation applies to 2.x.
- **`dbt-checkpoint`**: pre-commit checks for dbt project conventions, including model and column descriptions, source descriptions, and metadata keys. Pin a release and verify its hook IDs and arguments against that release's hook catalogue.

For the dbt Core 1.x / evaluator 1.x workflow, a package entry has this shape; replace the placeholder with a tested, exact compatible release:

```yaml
packages:
  - package: dbt-labs/dbt_project_evaluator
    version: "REPLACE_WITH_A_COMPATIBLE_1_X_PIN"
```

Then, from the dbt project root:

```bash
dbt deps
dbt parse
# For evaluator 1.x, run its package models and tests in the warehouse:
dbt build --select package:dbt_project_evaluator
```

For dbt Core 2.x with evaluator 2.x, follow the current package documentation; the version constraint and invocation are different. The current 2.x documentation uses a constraint such as `version: [">=2.0.0", "<3.0.0"]` and `dbt check`. These are alternative version tracks, not settings to paste together. Pin and validate the track your project actually uses.

A minimal `.pre-commit-config.yaml` pattern for `dbt-checkpoint` is:

```yaml
repos:
  - repo: https://github.com/dbt-checkpoint/dbt-checkpoint
    rev: REPLACE_WITH_A_VERIFIED_RELEASE_TAG
    hooks:
      - id: check-model-has-description
      - id: check-model-columns-have-desc
      - id: check-source-has-description
      - id: check-model-has-meta-keys
        args: ["--meta-keys", "owner", "domain", "--"]
```

Replace the release-tag placeholder with a real compatible tag before use. Some hooks inspect changed files and/or generated artifacts, so follow the pinned release's requirements for `dbt parse` or `dbt docs generate`. CI should fail on agreed critical gaps (for example, missing descriptions on public marts) while allowing an explicit, reviewed exception process for generated or intentionally undocumented resources.

A small custom artifact check is included in Section 5 and in the lab. It complements package rules; it does not replace them.

---

## 4. Advanced: dbt artifacts and lineage

### 4.1 The three important artifacts

| Artifact | Main purpose | Useful fields | Important limitation |
|---|---|---|---|
| `manifest.json` | Parsed project graph and resource definitions | `metadata`, `nodes`, `sources`, `parent_map`, `child_map`, node `description`, `columns`, `depends_on.nodes`, `tags`, `meta`, `config` | Represents parsed project state; not a record of which models succeeded in the latest run |
| `catalog.json` | Warehouse introspection results used by docs | `nodes`, `sources`, columns and warehouse-derived metadata such as types and stats where available | Requires successful metadata collection and permissions; may be partial or stale |
| `run_results.json` | Results of a particular command invocation | `metadata`, `results`, `unique_id`, `status`, `execution_time`, `message`, `adapter_response` where present | Only includes resources included in that invocation; does not by itself describe the full graph |

Artifact schemas can change between dbt versions. Use the `metadata.dbt_schema_version` and/or `metadata.dbt_version` fields to understand the producer version, and write parsers that tolerate missing optional fields. Prefer the artifacts' declared graph fields over trying to reconstruct dependencies from SQL text.

`manifest.json` is the main input for static graph analysis. `catalog.json` enriches the graph with warehouse introspection. `run_results.json` provides execution outcomes. They are related but not interchangeable.

### 4.2 Python: audit descriptions, ownership, and tests

The following script reads a generated manifest and reports models with missing model descriptions, missing column descriptions, missing ownership metadata, and no test node that declares a dependency on that model.

For the lab tree, save as `experiments/05_docs_lineage/scripts/audit_dbt_docs.py` (or use `scripts/audit_dbt_docs.py` if you deliberately place reusable scripts at the repository root):

```python
#!/usr/bin/env python3
"""Static documentation/governance checks over a dbt manifest.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def read_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict) or not isinstance(payload.get("nodes"), dict):
        raise ValueError("Expected a dbt manifest object with a 'nodes' mapping.")
    return payload


def owner_for(node: dict[str, Any]) -> str | None:
    # This project convention is intentionally explicit. A model owner is
    # not guaranteed to be a standard top-level manifest field.
    meta = node.get("meta") or {}
    if isinstance(meta, dict):
        value = meta.get("owner")
        if value:
            return str(value)
    config = node.get("config") or {}
    config_meta = config.get("meta") or {}
    if isinstance(config_meta, dict) and config_meta.get("owner"):
        return str(config_meta["owner"])
    return None


def main(manifest_path: str) -> int:
    manifest = read_manifest(Path(manifest_path))
    nodes = manifest.get("nodes", {})
    models = {
        uid: node for uid, node in nodes.items()
        if node.get("resource_type") == "model"
    }
    tests = [
        node for node in nodes.values()
        if node.get("resource_type") == "test"
    ]

    tested_ids: set[str] = set()
    for test in tests:
        for dependency_id in (test.get("depends_on") or {}).get("nodes", []):
            tested_ids.add(dependency_id)

    issues: list[tuple[str, str, str]] = []
    for unique_id, model in sorted(models.items()):
        name = model.get("name", unique_id)
        if not (model.get("description") or "").strip():
            issues.append((unique_id, "missing_model_description", name))
        if owner_for(model) is None:
            issues.append((unique_id, "missing_owner_meta", name))
        if unique_id not in tested_ids:
            issues.append((unique_id, "no_test_dependency", name))

        columns = model.get("columns") or {}
        for column_name, column in columns.items():
            if not (column.get("description") or "").strip():
                issues.append((
                    unique_id,
                    "missing_column_description",
                    f"{name}.{column_name}",
                ))

    print(f"dbt version: {manifest.get('metadata', {}).get('dbt_version', 'unknown')}")
    print(f"Manifest schema: {manifest.get('metadata', {}).get('dbt_schema_version', 'unknown')}")
    print(f"Models checked: {len(models)}")
    print(f"Issues found: {len(issues)}")
    for unique_id, issue, subject in issues:
        print(f"{issue}: {subject} [{unique_id}]")

    # A production CI policy should make this configurable; here any issue
    # returns non-zero so the example is easy to wire into a required check.
    return 1 if issues else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python experiments/05_docs_lineage/scripts/audit_dbt_docs.py target/manifest.json", file=sys.stderr)
        raise SystemExit(2)
    try:
        raise SystemExit(main(sys.argv[1]))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Could not audit manifest: {exc}", file=sys.stderr)
        raise SystemExit(2)
```

Run after parsing or generating documentation:

```bash
dbt parse
python experiments/05_docs_lineage/scripts/audit_dbt_docs.py target/manifest.json
```

Expected output is a summary followed by zero or more issue lines. Exact counts depend on the project. Exit code `0` means this particular check found no issues; `1` means issues were found; `2` means the script could not read the expected input. It does not prove descriptions are semantically accurate, does not validate warehouse comments, and does not detect every business-rule test gap.

**Version and configuration caveats:**

- dbt artifact structures are versioned. The script uses common manifest fields but should be tested against the pinned dbt release.
- The script assumes owner is declared under `meta.owner` or `config.meta.owner`. This is a project convention, not a universal dbt owner field for models.
- A test counts if a test node's `depends_on.nodes` includes the model. A test on a source, exposure, or downstream model does not count as a test on this model.
- A model with only a weak or irrelevant test will still pass this presence check. Test adequacy requires separate review.
- Disabled models may not appear in the same shape as enabled nodes. The script audits model nodes present in the parsed manifest; adjust policy for disabled resources if needed.

### 4.3 Upstream and downstream impact analysis

The manifest contains dependency references. If a model is changed, downstream descendants are candidates for review. Ancestors show the upstream data and logic the model relies on. Resource definitions are split across top-level collections: models/tests are generally in `nodes`, while exposures, metrics, semantic models, and saved queries may have their own collections. A parser must merge the collections needed to label graph IDs; do not assume every `child_map` ID exists in `nodes`.

For the lab tree, save as `experiments/05_docs_lineage/scripts/impact_analysis.py` (or use `scripts/impact_analysis.py` if you deliberately place reusable scripts at the repository root):

```python
#!/usr/bin/env python3
"""Print dbt graph ancestors and descendants for a model name or unique ID."""

from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path
from typing import Any


def main(manifest_path: str, target: str) -> int:
    manifest: dict[str, Any] = json.loads(
        Path(manifest_path).read_text(encoding="utf-8")
    )
    nodes: dict[str, Any] = manifest.get("nodes", {})
    sources: dict[str, Any] = manifest.get("sources", {})
    exposures: dict[str, Any] = manifest.get("exposures", {})
    metrics: dict[str, Any] = manifest.get("metrics", {})
    semantic_models: dict[str, Any] = manifest.get("semantic_models", {})
    saved_queries: dict[str, Any] = manifest.get("saved_queries", {})
    # dbt stores some resource types (notably exposures) outside `nodes`.
    # Merge the resource collections so graph IDs can be labelled correctly.
    resources = {**sources, **nodes, **exposures, **metrics, **semantic_models, **saved_queries}

    matches = [
        uid for uid, node in resources.items()
        if uid == target or node.get("name") == target
    ]
    if len(matches) != 1:
        print(
            f"Expected one resource matching {target!r}; found {len(matches)}. "
            "Use a unique_id if names collide.",
            file=sys.stderr,
        )
        return 2

    start = matches[0]
    parent_map = manifest.get("parent_map") or {}
    child_map = manifest.get("child_map") or {}

    def walk(graph: dict[str, list[str]], root: str) -> list[str]:
        seen: set[str] = set()
        queue = deque(graph.get(root, []))
        while queue:
            current = queue.popleft()
            if current == root or current in seen:
                continue
            seen.add(current)
            queue.extend(graph.get(current, []))
        return sorted(seen)

    def label(unique_id: str) -> str:
        resource = resources.get(unique_id, {})
        resource_type = resource.get("resource_type") or resource.get("type") or "resource"
        return f"{resource_type}:{resource.get('name', unique_id)}"

    print(f"Target: {label(start)} [{start}]")
    print("\nUpstream dependencies:")
    for uid in walk(parent_map, start):
        print(f"  - {label(uid)} [{uid}]")
    print("\nDownstream dependents / declared consumers:")
    for uid in walk(child_map, start):
        print(f"  - {label(uid)} [{uid}]")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python experiments/05_docs_lineage/scripts/impact_analysis.py target/manifest.json fct_orders", file=sys.stderr)
        raise SystemExit(2)
    try:
        raise SystemExit(main(sys.argv[1], sys.argv[2]))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not analyze manifest: {exc}", file=sys.stderr)
        raise SystemExit(2)
```

Example:

```bash
dbt parse
python experiments/05_docs_lineage/scripts/impact_analysis.py target/manifest.json fct_orders
```

The output should list ancestors such as staging/intermediate models and downstream dependents such as declared exposures, if those relationships exist in the manifest graph. It will not invent a dependency from a dashboard that was never declared as an exposure. If names collide, pass the full `unique_id`, for example `model.analytics.fct_orders`.

**Interpretation rule:** this is static declared lineage. It does not automatically capture ad hoc SQL, undocumented BI queries, application code, scheduler dependencies, external warehouse views, or every transformation performed outside dbt.

### 4.4 Column-level lineage

Model-level lineage says which resources depend on which resources. Column-level lineage says how individual output columns derive from input columns. It is more detailed and harder to infer reliably when SQL includes macros, dynamic SQL, complex expressions, or transformations outside dbt.

dbt Cloud's lineage/explorer capabilities vary by product plan, engine, configuration, and feature availability. Some capabilities can expose column-level lineage or richer metadata; do not assume they are available in every dbt Core setup or every dbt Cloud account. Verify current product documentation and the enabled workspace features before promising column-level lineage.

When column-level lineage is unavailable, document critical transformations explicitly and use warehouse/catalogue lineage integrations where they can capture the actual SQL execution. Treat inferred lineage as evidence with known limits, not as a guarantee.

### 4.5 OpenLineage and data observability

OpenLineage is an open standard for describing jobs, runs, and datasets through events. It complements dbt metadata; it is not the same thing as dbt's manifest or docs site.

A typical architecture may emit job/run/dataset events from an orchestrator or supported integration, then send them to a compatible OpenLineage backend. A dbt integration may require a particular adapter, orchestrator, package, environment configuration, or event-emitting wrapper. Support is not universal across all dbt versions and deployment products.

OpenLineage can help connect dbt transformations to orchestration and runtime lineage. A broader observability platform may combine lineage with freshness, volume, schema changes, test failures, and incident response. The standard itself does not automatically provide those monitors or guarantee that an emitter captures every event.

Before adopting an integration, confirm:
1. Which component emits events and which event fields it supports.
2. Whether the integration covers dbt Core, dbt Cloud, the chosen orchestrator, and the installed versions.
3. Whether run identifiers, dataset namespaces, and environment names are stable.
4. How events are authenticated, retained, and reconciled after retries.
5. Whether lineage is inferred, declared, or observed at runtime.

### 4.6 Hosting docs and keeping them current

Common hosting patterns include:

- **dbt Cloud docs** where available and enabled for the project's deployment.
- **Static hosting** of generated documentation assets on an approved web server or object-storage/static-site service.
- **Internal portal/catalogue integration** that links to or ingests dbt metadata.

A practical release pipeline is:

1. Install the pinned dbt version and packages.
2. Run parsing, tests, and the project's build/deploy checks.
3. Generate docs from the intended environment.
4. Run documentation and metadata coverage checks.
5. Publish only artifacts from the approved commit/environment.
6. Record the artifact generation timestamp and commit SHA.
7. Alert or block publication if generation fails; avoid silently serving stale docs.
8. Restrict access when documentation reveals sensitive schemas, operational details, or restricted asset names.

Static documentation should be treated as a build artifact, not a live view of the warehouse. Do not publish a local developer's `target/` directory blindly as production documentation.

### 4.7 External catalogues: a practical publishing approach

Catalogues such as Microsoft Purview, DataHub, OpenMetadata, and Google Dataplex have different ingestion models, APIs, permissions, metadata schemas, and lineage capabilities. There is no single dbt publishing command that works identically for all of them.

A safe integration pattern is:

1. **Choose the authoritative sources.** Decide whether descriptions/owners come from dbt YAML, warehouse metadata, or a governance system. Define precedence when values disagree.
2. **Pin and validate inputs.** Capture `manifest.json` and, where useful, `catalog.json` from a known successful environment. Record commit, dbt version, environment, and generation time.
3. **Map identities.** Map dbt `unique_id`, database, schema, relation name, and column names to the catalogue's asset identifiers. Avoid name-only matching across environments.
4. **Map metadata deliberately.** Translate descriptions, tags, owner conventions, domains, PII flags, and SLA labels to supported catalogue fields. Do not assume custom `meta` keys are automatically mapped.
5. **Publish through a supported connector/API.** Prefer a maintained, documented integration. Otherwise build a small adapter using the catalogue's supported API and authentication method.
6. **Upsert and reconcile.** Make publishing idempotent; handle renames, deletions, retired models, and stale assets explicitly. Never delete catalogue assets just because a partial manifest omitted them.
7. **Publish lineage with caveats.** Map only relationships that the source artifact or runtime integration actually represents. Mark whether lineage is declared, inferred, or observed where the catalogue supports it.
8. **Test in a sandbox.** Compare a few known models, columns, owners, and edges; validate permissions and PII handling before production.
9. **Monitor the sync.** Track last successful sync, records skipped, schema/API errors, and stale assets.

Prerequisites usually include a catalogue tenant/workspace, API credentials or connector permissions, network access, a stable asset naming strategy, a mapping policy, and a pinned integration version. Feature availability and required permissions differ by product and edition. Verify the current vendor documentation for the chosen catalogue and deployment before implementing the publisher.

---

## 5. Hands-on lab — `experiments/05_docs_lineage/`

### Lab objective

Make `fct_orders` and `dim_customers` understandable to analysts, declare their downstream dashboard and ML feature-set consumers, publish descriptions to the warehouse where supported, and use the manifest to check coverage and impact.

The examples assume the existing project contains the models from the preceding lessons. Keep your existing SQL transformations; add or adapt metadata rather than replacing working business logic. The lab snippets are examples to merge into the project, not a complete warehouse profile.

### 5.1 Lab file layout

```text
experiments/
└── 05_docs_lineage/
    ├── README.md
    ├── models/
    │   ├── staging/
    │   │   └── sources.yml
    │   ├── marts/
    │   │   ├── marts.yml
    │   │   └── exposures.yml
    │   └── docs/
    │       └── metrics.md
    ├── scripts/
    │   ├── audit_dbt_docs.py
    │   └── impact_analysis.py
    └── ci/
        └── documentation-check.sh
```

In an existing dbt repository, keep models and YAML in the actual project model paths and place the lab scripts under the lab directory or your repository's `scripts/` directory. dbt will not automatically discover a nested `experiments/05_docs_lineage/models/` folder unless it is configured as a model path; do not assume this lab tree is loaded just because the files exist there.

### 5.2 Step 1 — document all relevant models and mart columns

Create/update `models/staging/sources.yml` with the source example from Section 2.2. Ensure the declared source `commerce` and table names match the actual project.

Create/update `models/marts/marts.yml` with model and column descriptions for `fct_orders` and `dim_customers` from Section 2.1. Also document the relevant staging/intermediate models. For example:

```yaml
version: 2

models:
  - name: stg_orders
    description: >
      Cleaned order records from the commerce source. Normalizes names and
      types while preserving one row per source order identifier.
    columns:
      - name: order_id
        description: Stable identifier for one source order.
      - name: customer_id
        description: Customer identifier supplied by the commerce source.
      - name: order_date
        description: Date on which the source order was placed.
      - name: status
        description: Normalized source order status.

  - name: stg_order_items
    description: >
      Cleaned order-line records. Grain is one row per order line, not one
      row per order.
    columns:
      - name: order_id
        description: Order identifier to which this line belongs.
      - name: order_item_id
        description: Stable line identifier, if supplied by the source.
      - name: quantity
        description: Quantity recorded for the line.
      - name: item_amount
        description: Amount for the line using the source's documented currency semantics.

  - name: stg_customers
    description: >
      Cleaned customer records used to construct the customer dimension.
      Treat identifying attributes according to the project's access policy.
    columns:
      - name: customer_id
        description: Stable source customer identifier.
      - name: created_at
        description: Source timestamp for customer creation, if available.

  - name: int_orders_payments
    description: >
      Intermediate order/payment reconciliation model used by downstream
      order marts. Review its grain and payment-allocation logic before reuse.
    columns:
      - name: order_id
        description: Order key used to reconcile payments to orders.
```

These column names must match the SQL models exactly. If your actual project uses a different set of columns, document the real schema rather than copying this example unchanged. In particular, do not add `order_item_id`, `item_amount`, or `created_at` to YAML unless those columns exist.

### 5.3 Step 2 — add a reusable metric doc block

Create `docs/metrics.md` and add the `{% docs order_total_definition %}` block from Section 2.4. Reference it from the `order_total` column description in `marts.yml`.

Verify the docs block name is unique and the `doc()` reference spelling matches exactly. A block can be reused in multiple descriptions.

### 5.4 Step 3 — declare two exposures

Create `models/marts/exposures.yml` using the dashboard and ML feature-set examples in Section 3.1. Replace placeholder owners, emails, and URLs with approved values. Check that `fct_orders` and `dim_customers` exist and that the exposures accurately represent the real consumers.

Run:

```bash
dbt parse
dbt ls --resource-type exposure
```

Expected result: parsing succeeds and the two exposure names are listed if the project version supports this selector and the YAML is in a configured model path. If your dbt version uses different selector spelling, use its `dbt ls --help` output. Parsing validates structure, not whether the external dashboard or ML pipeline truly consumes the declared resources.

### 5.5 Step 4 — persist descriptions and verify warehouse comments

Merge the `persist_docs` configuration from Section 3.3 into `dbt_project.yml`. Then:

```bash
dbt build --select fct_orders dim_customers
dbt docs generate
```

Inspect the resulting warehouse relation and column comments using the metadata interface for your adapter. The `information_schema.columns` query in Section 3.3 is a starting point only; adapt it to the actual warehouse.

Record in the lab notes:
- Adapter and dbt version.
- Relation and columns checked.
- Whether relation comments appeared.
- Whether column comments appeared.
- Any permission or adapter limitations.

If you are using local DuckDB, verify the comments using DuckDB's supported metadata facilities for your installed version. Do not treat the generic information-schema query as a universal DuckDB command.

### 5.6 Step 5 — run `dbt-project-evaluator`

Choose the evaluator version track described in Section 3.4, add its compatible package pin to `packages.yml`, then run `dbt deps`. For dbt Core 1.x with evaluator 1.x, run `dbt parse` followed by `dbt build --select package:dbt_project_evaluator`. For dbt Core 2.x with evaluator 2.x, use the documented native `dbt check` workflow instead. Do not mix the commands across version tracks; check the pinned release documentation before making the step a required CI gate.

Review the findings and prioritize:
1. Missing descriptions on consumer-facing marts and their columns.
2. Missing tests on important keys and relationships.
3. Missing owner/domain metadata for public or high-impact assets.
4. Unexpected dependency or model-structure findings relevant to the current project.

Fix valid findings, document justified exceptions, and rerun the evaluator. A zero-finding report is not a substitute for reviewing whether the checks fit your governance rules.

### 5.7 Step 6 — parse the manifest

Save the Python scripts from Section 4.2 and Section 4.3 under the lab tree as:

- `experiments/05_docs_lineage/scripts/audit_dbt_docs.py`
- `experiments/05_docs_lineage/scripts/impact_analysis.py`

Run:

```bash
dbt parse
python experiments/05_docs_lineage/scripts/audit_dbt_docs.py target/manifest.json
python experiments/05_docs_lineage/scripts/impact_analysis.py target/manifest.json fct_orders
```

Expected behavior:
- The audit prints dbt version, manifest schema, number of models, issue count, and specific gaps.
- The impact script prints upstream dependencies and downstream dependents found in the manifest graph.
- The audit returns non-zero when issues exist. In a learning project, this is intentional; fix or explicitly waive each issue before using the script as a required CI gate.
- Output counts vary with your project, enabled models, tests, and dbt version.

### 5.8 CI example

Create `experiments/05_docs_lineage/ci/documentation-check.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Run from the dbt project root in an environment with the correct profile.
dbt deps
dbt parse
python experiments/05_docs_lineage/scripts/audit_dbt_docs.py target/manifest.json
```

Run `dbt-project-evaluator` and `dbt-checkpoint` as separate CI steps using their pinned, documented commands. Keep credentials out of logs and do not publish artifacts that contain sensitive metadata to a public location.

### 5.9 Troubleshooting

| Symptom | Likely cause | Corrective action |
|---|---|---|
| A model is missing from the docs site | YAML file is outside configured model paths, parsing failed, or resource is disabled | Check `model-paths`, parse output, and resource status |
| `doc()` reference cannot be resolved | Block name mismatch or docs file not discovered | Compare exact block/function names and `docs-paths` |
| Exposure is absent from `dbt ls` | Invalid YAML, wrong resource type syntax, or unsupported selector/version | Run `dbt parse`, inspect the installed version's help, and check file location |
| Descriptions appear in docs but not warehouse comments | `persist_docs` absent, adapter limitation, relation was not rebuilt, or insufficient privileges | Check config, adapter docs, permissions, and target relation |
| Audit says a model has no owner | Project uses a different metadata key or owner convention | Standardize `meta.owner` or adjust `owner_for()` deliberately |
| Audit says a model has no tests | No test node depends directly on that model, or tests were not parsed | Inspect the manifest test nodes and their `depends_on.nodes` |
| Impact report misses a BI dashboard | Dashboard was not declared as an exposure or dependency was not represented in dbt | Declare the exposure and its `depends_on`; integrate BI lineage separately if available |
| Catalogue has stale/duplicate assets | Identity mapping, environment mapping, or retirement policy is unclear | Use stable identifiers, upserts, reconciliation, and stale-asset monitoring |

### 5.10 Completion criteria

- [ ] All relevant staging, intermediate, and mart models have useful descriptions.
- [ ] All consumer-facing mart columns have descriptions that match their real SQL output.
- [ ] Source descriptions explain origin, grain, ownership, and known caveats.
- [ ] A reusable docs block is referenced by `doc()`.
- [ ] Both the dashboard and ML feature-set exposures parse and have real owners.
- [ ] `meta` and tags follow a documented project convention.
- [ ] `persist_docs` is enabled where supported, and warehouse comments have been checked rather than assumed.
- [ ] Documentation coverage is checked in CI with a pinned evaluator and/or custom script.
- [ ] `manifest.json` parsing identifies missing descriptions, ownership, and direct test dependencies.
- [ ] The `fct_orders` impact report has been reviewed against known descendants and exposures.
- [ ] Known limitations and exceptions are recorded with an owner and review date.

---

## 6. Documentation governance and maintenance

Documentation is an ongoing part of model delivery. Use the following minimum workflow:

1. **Ownership:** every high-impact model has an accountable team or owner in a consistent metadata field.
2. **Definition review:** descriptions are reviewed with SQL changes, especially changes to grain, filters, currency, time zones, null handling, and business definitions.
3. **Consumer review:** inspect downstream models and declared exposures before changing a public mart.
4. **Deprecation:** announce replacement models, migration steps, and retirement dates. Where supported, use dbt model versions and `deprecation_date`; a date in metadata alone does not migrate consumers or remove an old model.
5. **Coverage policy:** fail CI for missing descriptions on public marts and missing required ownership metadata; define an exception path with an expiry date.
6. **Freshness of docs:** generate docs after a successful deployment or approved build, publish the commit/environment/time, and alert if the publication pipeline fails.
7. **Catalogue reconciliation:** monitor stale assets, duplicate identities, missing owners, and failed metadata syncs.
8. **Privacy:** use PII flags as signals for policy automation, but enforce actual access controls, masking, retention, and privacy reviews in the systems responsible for those controls.

### What should block a release?

A useful starting policy:

| Finding | Suggested default | Reason |
|---|---|---|
| Public mart has no description | Block | Consumers cannot reliably interpret the interface |
| High-impact model has no owner | Block or require approved exception | No accountable responder for incidents or changes |
| A required key test is absent | Block | Referential/uniqueness guarantees are not represented |
| Low-risk internal staging column lacks a description | Warn initially; improve incrementally | Avoid overwhelming teams while raising coverage |
| Catalogue sync is delayed | Alert; block only if catalogue publication is a release requirement | A catalogue outage may not invalidate the model itself |
| A model's description disagrees with SQL semantics | Block | Misleading documentation can be worse than missing documentation |

Tune this policy to your consumers and risk model. Do not configure every check as a warning and then ignore the warnings.

---

## 7. Roadmap checkpoint

You are ready to move on when you can answer these questions without guessing:

1. What is the difference between a description, an exposure, a tag, and `meta`?
2. How do `dbt docs generate` and `dbt docs serve` differ?
3. What is the distinction between `manifest.json`, `catalog.json`, and `run_results.json`?
4. How can you identify the upstream dependencies and downstream dependents of `fct_orders`?
5. What does `persist_docs` attempt to publish, and how do you verify that it worked for your adapter?
6. Why is `meta.contains_pii: true` not a security control by itself?
7. What does an exposure communicate, and what does it not automatically execute or validate?
8. How would you safely publish dbt metadata to a catalogue while handling identity mapping, stale data, and partial lineage?

### Common mistakes to avoid

- Writing descriptions once and never updating them when model semantics change.
- Describing columns without explaining grain, filters, units, or business caveats.
- Treating an exposure as automatic discovery of dashboards or ML consumers.
- Assuming tags or `meta` enforce permissions.
- Assuming `persist_docs` works identically across adapters and relation types.
- Treating `manifest.json`, `catalog.json`, and `run_results.json` as interchangeable.
- Assuming model-level lineage is the same as column-level or runtime lineage.
- Publishing stale docs or partial catalogue data without recording environment and generation time.
- Assuming all external catalogues have the same connector, schema, permissions, or lineage features.
- Relying on a “has at least one test” check as proof that a model is adequately tested.
- Failing to review downstream consumers before a breaking change to `fct_orders`.

---

## 8. Verification notes for this lesson

The examples are designed to be internally consistent with the roadmap's model names and learning objectives. YAML and Python examples are instructional templates and must be adapted to the actual project's column names, dbt version, adapter, package pins, and deployment environment.

Static review can check structure and consistency, but it cannot establish that a live warehouse accepts a comment query, that a particular dbt Cloud feature is enabled, or that an external catalogue connector works with your tenant. Those claims require environment-specific execution and current vendor documentation.
