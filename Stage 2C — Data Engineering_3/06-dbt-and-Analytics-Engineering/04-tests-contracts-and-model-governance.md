# Tests, Contracts, and Model Governance in dbt

> **Roadmap location:**
> `Stage 2C — Data Engineering_3/06-dbt-and-Analytics-Engineering/04-tests-contracts-and-model-governance.md`\
> **Scope:** dbt data tests, unit tests, model contracts, versioning,
> access and ownership metadata, monitoring, and test-cost decisions.\
> **Prerequisites:** a configured dbt project, `ref()` and source
> declarations, models such as `stg_orders`, `stg_order_items`, and
> `fct_orders`, and familiarity with YAML.

## Learning outcomes

You will learn to choose tests that express consumer guarantees, make
failures actionable, distinguish data tests from unit tests and
contracts, and evolve public models without silently breaking downstream
users.

## 1. Why tests and contracts matter

A dbt model can compile and run successfully while producing incorrect
or incomplete data. Tests express assumptions about the data and return
evidence when those assumptions are violated. Contracts describe a
model's output interface. Governance metadata helps dbt and its
consumers understand ownership, intended access, and compatibility.

These controls solve different problems:

  -----------------------------------------------------------------------
  Control                 Main question           What it does not
                                                  guarantee
  ----------------------- ----------------------- -----------------------
  Generic data test       Does the data satisfy a It does not prove every
                          declared rule?          business rule or future
                                                  input is correct.

  Singular data test      Which rows violate a    It does not
                          custom SQL rule?        automatically define a
                                                  reusable test API.

  Unit test               Does model logic        It does not prove
                          produce expected        production data quality
                          results for specified   or all warehouse
                          fixtures?               behavior.

  Model contract          Does a model output     It does not guarantee
                          conform to its declared that values are
                          interface?              semantically correct.

  Version/access/group    How should consumers    Metadata alone does not
  metadata                depend on and access a  migrate consumers or
                          model?                  grant warehouse
                                                  permissions.

  Monitoring and alerting Are failures occurring  An alert is only useful
                          over time, and who      if its query, routing,
                          should respond?         and response process
                                                  work.
  -----------------------------------------------------------------------

Testing is a layered safety system, not a single command. A sensible
workflow tests model logic, validates real data, checks the published
interface, and monitors results after deployment.

## 2. Beginner: generic data tests

Generic tests are parameterized tests that can be declared against
models, columns, or sources in YAML. dbt includes `unique`, `not_null`,
`accepted_values`, and `relationships`.

### 2.1 Example model and schema YAML

Assume `fct_orders` has one row per order and includes `order_id`,
`customer_id`, `order_status`, and `order_total`. Create
`models/marts/schema.yml`:

``` yaml
version: 2

models:
  - name: fct_orders
    description: "One row per order, including its customer, status, and total."
    columns:
      - name: order_id
        description: "Stable identifier for an order."
        data_tests:
          - not_null
          - unique

      - name: customer_id
        data_tests:
          - not_null
          - relationships:
              arguments:
                to: ref('dim_customers')
                field: customer_id

      - name: order_status
        data_tests:
          - accepted_values:
              arguments:
                values: ['placed', 'shipped', 'cancelled', 'pending']

      - name: order_total
        data_tests:
          - not_null
```

**Version note:** newer dbt releases support the `arguments:` nesting
shown for generic tests. Older releases may require arguments directly
under the test name, for example `accepted_values: values: [...]`. Use
the syntax supported by your installed dbt version. The `data_tests` key
is preferred in newer dbt YAML; older projects may use `tests`.

What each test does:

-   `unique`: detects duplicated non-null values according to the test
    query. Pair it with `not_null` for a primary-key-like guarantee;
    `unique` alone does not prohibit nulls in every adapter/test
    implementation.
-   `not_null`: finds rows where the selected column is null.
-   `accepted_values`: finds values outside the declared list. Consider
    case, whitespace, null behavior, and whether the list represents a
    stable business contract.
-   `relationships`: finds non-null child keys with no matching parent
    key in the referenced relation. Null child keys are typically
    excluded by the relationship test, so add `not_null` separately if
    null is invalid.

The `relationships` target must exist and have a matching key. Test
direction matters: `fct_orders.customer_id` should reference
`dim_customers.customer_id`, not the reverse. A test passes when its
failure query returns no rows (or no violating values under the generic
test's implementation).

### 2.2 Test primary and foreign keys deliberately

For each mart, identify its grain and key before adding tests.

-   If `fct_orders` has one row per order, `order_id` should generally
    be `unique` and `not_null`.
-   If `fct_order_items` has one row per order line, test the actual
    line grain (often a composite key such as `order_id` plus
    `order_line_id`). A single `order_id` is not unique in a line-item
    fact.
-   Test every required foreign key with `relationships`, and separately
    test nullability when required.
-   Add business-rule tests to marts, such as non-negative totals, valid
    order lifecycle states, and consistency between item amounts and
    order totals.

A test should match the model's grain and contract. A false uniqueness
assumption can produce noisy failures or encourage incorrect
transformations.

### 2.3 Deliberately introduce a failure

For a controlled exercise, duplicate an `order_id` in a development
fixture or seed, then run the relevant test. The `unique` test should
return a failing result and identify the duplicate key(s). Restore the
fixture after confirming detection. Do not deliberately corrupt
production data.

Similarly, set a required `customer_id` to null to exercise `not_null`,
or set it to an ID absent from `dim_customers` to exercise
`relationships`. Change one condition at a time so you can attribute
each failure correctly.

## 3. Singular tests: SQL that returns failing rows

A singular test is a `.sql` file under the configured `test-paths`
(commonly `tests/`). It is not a model to materialize; it is a query
that selects records violating a rule. Zero returned rows means the test
passes.

### 3.1 Order total equals the sum of item totals

Assume `fct_orders.order_total` and `fct_order_items.line_total` use the
same currency and comparable decimal types. Create
`tests/assert_order_total_matches_items.sql`:

``` sql
with item_totals as (
    select
        order_id,
        sum(line_total) as calculated_total
    from {{ ref('fct_order_items') }}
    group by order_id
),
comparison as (
    select
        o.order_id,
        o.order_total,
        i.calculated_total
    from {{ ref('fct_orders') }} as o
    left join item_totals as i
        on o.order_id = i.order_id
)
select *
from comparison
where calculated_total is null
   or order_total != calculated_total
```

This strict comparison assumes that the order total is defined as
exactly the sum of line totals, with no separate tax, shipping,
discount, or rounding adjustments. If those components exist, include
them in the business rule. For floating-point data, use a tolerance; for
fixed-scale decimal values, exact equality is generally preferable when
both sides follow the same rounding policy.

The `calculated_total is null` branch detects orders without any
matching item rows. If zero-item orders are valid, replace that behavior
with the intended rule rather than treating it as universally invalid.

### 3.2 Run a singular test

``` bash
dbt test --select assert_order_total_matches_items
```

If the test returns rows, dbt marks it as a failure according to the
configured severity. Inspect the returned rows or stored failures to
diagnose the violated rule. Do not simply weaken the test to make CI
green; confirm whether the model or the rule is wrong.

## 4. Running tests and understanding execution order

### 4.1 `dbt test` versus `dbt build`

-   `dbt test` runs selected tests; it does not generally rebuild every
    selected model first. Ensure the relations being tested exist and
    are current.
-   `dbt build` builds selected resources and runs associated tests in
    DAG-aware order. It can include seeds, models, snapshots, tests, and
    other supported resource types depending on selection and dbt
    version.
-   A failed upstream test can affect downstream execution: dbt's build
    ordering and resource selection determine whether downstream
    resources are skipped. Inspect the run results rather than assuming
    every selected model ran.
-   `dbt run` builds models but does not run data tests automatically.

Examples:

``` bash
# List resources matching a selection before running it.
dbt ls --select fct_orders

# Run tests attached to fct_orders and its selected dependencies as appropriate.
dbt test --select fct_orders

# Build a model and run its applicable tests in DAG order.
dbt build --select fct_orders

# Build/test a model and its downstream dependents.
dbt build --select fct_orders+
```

Selection syntax is powerful and version-aware. Use
`dbt ls --select ...` to verify the exact selected resources before a
costly or production run. A trailing `+` selects graph neighbors
according to dbt's selection semantics; check whether you intend
upstream, downstream, or both directions.

### 4.2 Severity: warning versus error

A test can be configured with `severity: warn` or `severity: error`.

``` yaml
models:
  - name: fct_orders
    columns:
      - name: order_id
        data_tests:
          - unique:
              config:
                severity: error
```

For older dbt versions, configuration may be written directly under the
test definition rather than nested under `config`. Confirm your
installed version's schema syntax.

-   **Error:** the test failure is an error and normally produces a
    failing command result. In a CI deployment gate, this should block
    promotion when the pipeline is configured to respect dbt's exit
    status.
-   **Warn:** the test failure is reported as a warning. It does not
    normally fail the command by itself, so a pipeline can continue
    unless it explicitly treats warnings as blocking.
-   `--warn-error` or related warning-as-error configuration can change
    how warnings affect the command; use carefully because it may
    elevate warnings beyond data-test findings.

Do not set every test to warning. A test that protects a public primary
key or prevents invalid financial reporting should usually block
deployment. Warnings are appropriate for monitored drift or a rule with
an agreed temporary tolerance and an owner who will respond.

### 4.3 Thresholds: `warn_if`, `error_if`, and `limit`

Thresholds define how many failing rows trigger a warning or error. The
exact configuration placement and expression semantics depend on dbt
version.

``` yaml
models:
  - name: fct_orders
    columns:
      - name: order_total
        data_tests:
          - not_null:
              config:
                severity: error
                warn_if: "> 0"
                error_if: "> 100"
                limit: 1000
```

This is an illustrative threshold pattern; verify that your installed
dbt version supports these options for the selected test and that
`limit` is interpreted as intended. Under the common threshold model, a
test's failure count is compared with `warn_if` and `error_if`; `limit`
caps the returned failure rows and may affect how many rows are
available for diagnosis. Do not use `limit` as a substitute for
understanding the actual failure count or for reducing the logical scope
of a test.

A threshold policy must be explicit. For example, allowing up to 100
null keys in a public fact table is usually not a reasonable default.
Define thresholds from data volume, business impact, and an agreed
service-level objective.

### 4.4 Store failures

Where supported, run:

``` bash
dbt test --select assert_order_total_matches_items --store-failures
```

Stored failures can help with diagnosis, but behavior depends on dbt
version, adapter support, test configuration, and the configured
schema/database for failure relations. Review the command output to
learn the actual relation name and location. Failure tables can contain
sensitive records and consume warehouse storage; restrict access, set
retention, and avoid storing failures for tests that expose unnecessary
personal or confidential data.

A stored-failure table is usually a snapshot of the latest run for a
test, not a historical incident database by itself. To measure recurring
failures over time, persist run metadata and counts in a monitoring
table or an observability system.

## 5. Custom generic tests with Jinja

A custom generic test is a reusable query template. In current dbt
syntax, define it under `macros/` with a `test` block.

### 5.1 Example: non-negative amounts

Create `macros/generic_tests/test_non_negative.sql`:

``` sql
{% test non_negative(model, column_name) %}

select *
from {{ model }}
where {{ column_name }} < 0

{% endtest %}
```

Use it in schema YAML:

``` yaml
version: 2

models:
  - name: fct_orders
    columns:
      - name: order_total
        data_tests:
          - non_negative
```

The `model` argument is the relation being tested; `column_name` is the
configured column. This simple test does not flag null values, so add
`not_null` when null is invalid. It also assumes negative totals are
invalid for this model; refunds or signed adjustments may require a
different rule.

### 5.2 Example with a configurable threshold

Create `macros/generic_tests/test_max_value.sql`:

``` sql
{% test max_value(model, column_name, max_value) %}

select *
from {{ model }}
where {{ column_name }} > {{ max_value }}

{% endtest %}
```

Declare:

``` yaml
models:
  - name: fct_orders
    columns:
      - name: order_total
        data_tests:
          - max_value:
              arguments:
                max_value: 1000000
```

This example assumes `max_value` is a trusted numeric literal. Never use
a generic test argument as a path for untrusted raw SQL. Validate
argument types and semantics. The test is only meaningful if the bound
reflects a real business rule and the column's currency/units are
defined.

### 5.3 Custom generic-test design rules

-   Give the test a clear, stable name and document what a returned row
    means.
-   Keep the test query focused on violating records.
-   Make null semantics explicit.
-   Test the test: use a small fixture with passing and failing rows.
-   Use package tests when their documented semantics match; avoid
    duplicating an existing generic test without a reason.
-   Use adapter-dispatched SQL or portable SQL where required, and test
    all supported adapters.

## 6. `dbt_expectations` and richer data checks

`dbt_expectations` provides Great Expectations-inspired tests for checks
such as value distributions, regular-expression matching, and row
counts. Package namespaces, maintenance status, test names, and argument
syntax are version-dependent. The original `calogica/dbt_expectations`
project has stated that it is no longer actively supported; verify the
currently recommended distribution or maintained fork and its namespace
before adding it to a new project.

Examples below illustrate the types of checks to look for. Confirm exact
test names and arguments against the installed package's README and
source.

### 6.1 Range/distribution-style check

``` yaml
models:
  - name: fct_orders
    columns:
      - name: order_total
        data_tests:
          - dbt_expectations.expect_column_values_to_be_between:
              arguments:
                min_value: 0
                max_value: 1000000
```

This is appropriate only if negative values and values above the maximum
are genuinely invalid. Distribution checks can also be useful for
expected ranges, percentiles, or row-count drift where supported by the
package. Understand whether a test examines every row or uses aggregate
statistics.

### 6.2 Regular-expression check

``` yaml
models:
  - name: dim_customers
    columns:
      - name: customer_code
        data_tests:
          - dbt_expectations.expect_column_values_to_match_regex:
              arguments:
                regex: "^[A-Z]{2}[0-9]{6}$"
```

Regex dialects can differ by warehouse, and null behavior may require a
separate `not_null` test. The pattern above is an example customer-code
format, not a universal identifier rule.

### 6.3 Row-count check

A row-count test may be appropriate when a relation is expected to
remain within a defined range or match a reference relation. Check the
package version for the precise row-count test name and whether it
supports `min_value`, `max_value`, or comparison against another table.
Avoid asserting a fixed count for a naturally growing fact table unless
the data contract really requires it.

### 6.4 Cost and suitability

Rich tests can execute full scans, regex expressions, joins, aggregates,
or distribution calculations. Choose them based on risk, table size,
partitioning, and warehouse cost. Start with cheap, high-value checks on
every build; schedule expensive checks at a lower frequency only when
the risk assessment permits it. Do not schedule a critical freshness or
integrity test so rarely that consumers can be harmed before it runs.

## 7. Unit tests with `given` and `expect`

dbt unit tests for model SQL were introduced in dbt Core 1.8. Support
and syntax depend on the installed dbt version and adapter. They
validate model logic using controlled input fixtures rather than relying
on the production relation's actual rows.

### 7.1 CASE-heavy model

Suppose `models/intermediate/int_order_status.sql` contains:

``` sql
select
    order_id,
    payment_status,
    shipped_at,
    case
        when payment_status = 'refunded' then 'cancelled'
        when shipped_at is not null then 'shipped'
        when payment_status = 'paid' then 'placed'
        else 'pending'
    end as order_status
from {{ ref('stg_orders') }}
```

Create a unit-test YAML file, for example
`models/intermediate/int_order_status.yml`:

``` yaml
unit_tests:
  - name: test_int_order_status_case_logic
    model: int_order_status
    given:
      - input: ref('stg_orders')
        rows:
          - {order_id: 1, payment_status: 'refunded', shipped_at: null}
          - {order_id: 2, payment_status: 'paid', shipped_at: '2026-01-02'}
          - {order_id: 3, payment_status: 'paid', shipped_at: null}
          - {order_id: 4, payment_status: 'pending', shipped_at: null}
    expect:
      rows:
        - {order_id: 1, payment_status: 'refunded', shipped_at: null, order_status: 'cancelled'}
        - {order_id: 2, payment_status: 'paid', shipped_at: '2026-01-02', order_status: 'shipped'}
        - {order_id: 3, payment_status: 'paid', shipped_at: null, order_status: 'placed'}
        - {order_id: 4, payment_status: 'pending', shipped_at: null, order_status: 'pending'}
```

The `shipped_at` fixture type may need explicit casting or
adapter-specific date syntax. Keep expected rows consistent with the
model's selected columns and the adapter's output types. Unit-test
support for seeds, ephemeral models, macros, and adapter features can
vary; consult the docs for the installed release.

Run:

``` bash
dbt test --select test_type:unit
```

If the selector syntax differs in your dbt release, use the supported
unit-test selection method or select the named unit test directly.
Verify selected resources with `dbt ls`.

### 7.2 What unit tests do and do not prove

Unit tests are good for branch coverage and edge cases such as null
inputs, status combinations, boundary values, and precedence between
`CASE` branches. They do not prove that the production source has no
duplicate IDs, that a join key is complete, or that warehouse
permissions and full-scale performance are correct. Combine unit tests
with data tests and integration/build checks.

## 8. Enforced model contracts

A model contract defines the expected output columns and data types.
With `contract: enforced`, dbt validates the model's output against the
declared interface when building it. Exact behavior and supported
constraints vary by dbt version and adapter.

### 8.1 Contract for `fct_orders`

``` yaml
version: 2

models:
  - name: fct_orders
    config:
      contract:
        enforced: true
    columns:
      - name: order_id
        data_type: bigint
        constraints:
          - type: not_null
          - type: primary_key
      - name: customer_id
        data_type: bigint
        constraints:
          - type: not_null
      - name: order_status
        data_type: varchar
      - name: order_total
        data_type: numeric(18, 2)
```

These types are illustrative. Match the actual adapter's data types and
the model SQL's output types. `primary_key` constraints and their
enforcement semantics are adapter-dependent; on some warehouses, a
declared constraint is informational rather than physically enforced.
Even where a primary-key constraint is supported, retain data tests when
you need explicit validation of actual rows.

Contracts are stricter about the published shape than tests: they catch
incompatible output column names/types, but they do not replace
`unique`, `not_null`, accepted-value, relationship, or business-rule
tests. A model can satisfy its contract while returning the wrong
amount.

### 8.2 Demonstrate an incompatible change

Suppose the contract declares `order_total` as `numeric(18, 2)`, but a
developer changes the model to emit a string:

``` sql
cast(order_total as varchar) as order_total
```

The enforced contract should reject the mismatch when the adapter and
dbt version support the declared contract. Confirm the exact error in
the build output. Restore the intended type or create a new version with
a deliberately changed interface; do not silently weaken the contract to
make the build pass.

Some warehouses infer or normalize types differently. Validate contract
behavior on the target adapter and check whether constraints are
enforced, merely declared, or unsupported.

## 9. Safe breaking changes: model versions and deprecation

Model versions let a producer introduce an incompatible interface while
preserving a compatible version for consumers during migration.
Availability and exact version syntax depend on dbt version and project
features.

### 9.1 Define versions

A simplified `models/marts/schema.yml` example:

``` yaml
version: 2

models:
  - name: fct_orders
    latest_version: 2
    config:
      contract:
        enforced: true
    columns:
      - name: order_id
        data_type: bigint
      - name: customer_id
        data_type: bigint
      - name: order_status
        data_type: varchar
      - name: order_total
        data_type: numeric(20, 4)

    versions:
      - v: 1
        deprecation_date: 2027-06-30
        columns:
          - include: all
          - name: order_total
            data_type: numeric(18, 2)
      - v: 2
        columns:
          - include: all
```

This versioned-model example keeps the breaking change explicit: v1
retains `numeric(18, 2)`, while v2 publishes `numeric(20, 4)` and is the
latest version. The `deprecation_date` is attached to v1 so the migration
notice targets the version being retired. A top-level `deprecation_date`
would apply to the model declaration rather than expressing this
version-specific retirement intent. Model-version and deprecation syntax
must be checked against the installed dbt release; dbt 1.6 introduced
first-class model deprecation support.

### 9.2 Migration workflow

1.  Keep v1 stable for existing consumers.
2.  Add v2 with the new output contract and tests.
3.  Update internal consumers deliberately using version-aware
    references where supported.
4.  Validate both versions and their downstream models.
5.  Communicate the deprecation date, owner, and migration path.
6.  Measure remaining v1 consumers before removal.
7.  Remove v1 only after the compatibility policy and consumer migration
    are satisfied.

A deprecation date is metadata and a signal to consumers; it does not
automatically rewrite downstream SQL or prove all consumers have
migrated. Use lineage, code search, and dbt artifacts to find
dependencies.

## 10. Access modifiers, groups, and ownership

These features help express project-level API boundaries and
accountability. Support and enforcement depend on dbt version and
deployment setup.

### 10.1 Access modifiers

Common access levels include:

-   `private`: intended for use within its group/project boundary and
    not a public interface.
-   `protected`: available within the project but not intended as a
    cross-project public API.
-   `public`: explicitly exposed for supported cross-project
    consumption.

The exact rules for allowed `ref()` calls and cross-project use depend
on dbt version and dbt Mesh configuration. Access metadata is not a
warehouse `GRANT`; use warehouse permissions to control who can query
physical relations.

Example model YAML:

``` yaml
version: 2

groups:
  - name: commerce
    owner:
      name: Commerce Analytics
      email: commerce-analytics@example.com

models:
  - name: int_order_status
    config:
      group: commerce
      access: private
    description: "Internal order-status derivation."

  - name: fct_orders
    config:
      group: commerce
      access: public
    description: "Supported consumer-facing order fact."
    meta:
      owner: commerce-analytics
      support_channel: "#data-commerce"
```

Use a real team distribution address and channel in your project. The
addresses above are placeholders. In some dbt versions, ownership is
declared through a group's `owner` object, while model `meta` is
free-form project metadata. Do not assume `meta.owner` is automatically
enforced as an access control policy.

### 10.2 Groups and ownership

Groups help identify which team owns a model and can participate in
access boundaries. Ownership should make it clear who responds when a
test fails, a contract changes, or a model is deprecated. A name without
an actionable contact path is weak operational metadata.

Recommended minimum for a public mart: - Named owner/group. -
Description and declared grain. - Primary key and required foreign-key
tests. - Business-rule tests for material calculations. - Enforced
contract where supported and valuable. - Version/deprecation policy for
breaking changes. - A clear escalation path for critical failures.

### 10.3 Cross-project references and dbt Mesh

dbt Mesh is an approach to organizing multiple dbt projects with clear
ownership and supported public model interfaces. Cross-project
references require the appropriate project configuration, dependency
declaration/metadata, model access, and compatible dbt tooling. A public
model is an API: its contract, tests, documentation, and version policy
matter to downstream projects.

Do not treat `access: public` alone as a complete cross-project setup.
Verify the required project dependency configuration and supported dbt
version in the deployment environment. Do not bypass the public
interface by hard-coding another project's warehouse relation; doing so
weakens lineage and compatibility checks.

For a project dependency named `commerce`, a downstream model can use the
cross-project reference form supported by dbt Mesh:

``` sql
select
    order_id,
    order_total
from {{ ref('commerce', 'fct_orders') }}
```

The upstream model must expose a supported public interface, and the
consumer project must declare the dependency using the mechanism required
by its dbt version. This syntax is not a warehouse table name and should
not be replaced with a hard-coded relation. Confirm cross-project
reference support and project-dependency configuration before running it.

## 11. Failure storage, artifacts, and recurring-failure monitoring

### 11.1 Useful dbt artifacts

Common artifacts include: - `manifest.json`: parsed project resources,
dependencies, configs, and metadata. - `run_results.json`: results for
resources executed by a command, including statuses and timing where
available. - `catalog.json`: relation/column metadata generated by the
docs workflow when supported and requested. - Stored test-failure
relations: rows returned by a failing test when failure storage is
configured and supported.

Artifacts are command outputs, not a complete long-term observability
database. Their schemas and fields can evolve. Use the artifact schema
corresponding to the dbt version that generated them.

### 11.2 Store failures for diagnosis

``` bash
dbt test --select fct_orders --store-failures
```

Check the command output for the failure relation location and
permissions. Some test types or adapters may have different storage
behavior. Use a development environment first and avoid retaining
sensitive failure rows unnecessarily.

### 11.3 A recurring-failure report

For a basic operational report, persist one record per test execution
with fields such as:

``` text
invocation_id, executed_at, unique_id, test_name, model_name,
status, failure_count, execution_time, target_name
```

Populate this from supported dbt artifacts or an observability
integration; don't assume every field appears under exactly the same
name in every dbt version. Then aggregate by test and time window:

``` sql
select
    test_name,
    model_name,
    count(*) as runs_observed,
    sum(case when status in ('fail', 'error') then 1 else 0 end) as failing_runs,
    max(executed_at) as latest_execution
from analytics_observability.test_run_history
where executed_at >= current_date - interval '30 day'
group by test_name, model_name
order by failing_runs desc, latest_execution desc
```

The date arithmetic and status values may need adjustment for the
warehouse and artifact parser. Store actual failure counts separately
from a boolean status if you want to measure severity. The example is a
reporting pattern, not a built-in dbt table.

### 11.4 Elementary and external alerting

Elementary and other observability tools can ingest dbt test
results/artifacts, track failures, and route alerts. Integration setup,
supported artifacts, permissions, and alert destinations vary by
product/version. Start by defining: - Which failures are actionable. -
Who owns each test. - What constitutes a new incident versus a repeated
known issue. - How to deduplicate and route alerts. - Retention and
privacy rules for stored failure data.

An alert without an owner or runbook becomes noise. Do not route every
low-severity test warning to an on-call engineer.

## 12. Test cost, sampling, and scheduling

### 12.1 Test cost drivers

Costs can come from full table scans, joins for relationship tests,
grouping for uniqueness, regex evaluation, aggregates for distribution
tests, and large fixture/CTE expansions. Use warehouse query plans and
execution history to find expensive checks.

### 12.2 Sampling: when it helps and when it is unsafe

Sampling can be useful for exploratory profiling or non-blocking drift
signals on very large tables. It can miss rare defects and cannot
establish a hard uniqueness, referential integrity, or financial
correctness guarantee over the full dataset. Do not replace a critical
full-population integrity test with a sample simply to reduce cost
without formally accepting the residual risk.

Possible approaches: - Run cheap primary-key and required-field checks
on every build. - Run expensive distribution and deep reconciliation
checks on a schedule if their risk window is acceptable. - Restrict
tests to a relevant partition/window only when the data contract is
window-scoped and older data is separately validated. - Use incremental
models or source partitioning carefully; selection of only changed
models can miss defects introduced by upstream historical changes. -
Track test duration and failure rate so the team can tune checks based
on evidence.

### 12.3 A practical gating framework

  -----------------------------------------------------------------------
  Test/control            Default posture         Reason
  ----------------------- ----------------------- -----------------------
  Public primary key      Block deployment        Duplicate/missing
  (`unique`, `not_null`)                          identifiers can corrupt
                                                  joins and consumers.

  Required foreign key    Block if integrity is   Orphan records can
  (`relationships`)       contractual             break downstream
                                                  metrics and referential
                                                  assumptions.

  Financial/business      Block when the metric   Incorrect totals can
  reconciliation          is material             create material
                                                  reporting errors.

  Contract mismatch on    Block deployment        The published interface
  public model                                    is incompatible.

  Validated critical      Usually block           Unexpected states can
  status/value domain                             invalidate downstream
                                                  logic.

  Exploratory             Warn initially, with    Signal may require
  distribution drift      owner and threshold     investigation before it
                                                  is a proven defect.

  Non-critical profiling  Warn or schedule        Useful for visibility,
  or sampled diagnostic                           but not a full
                                                  integrity guarantee.

  Known issue temporarily Explicit warning with   Prevents silent
  tolerated               expiry and owner        permanent degradation
                                                  of the quality bar.
  -----------------------------------------------------------------------

A warning should have a reason, an owner, a review date, and a
threshold. If a warning remains forever, it is effectively no control at
all. Conversely, blocking on every speculative anomaly can make teams
ignore the pipeline. Gate on consumer impact and confidence in the rule.

## 13. Integrating external quality tools and producer contracts

dbt tests validate transformed relations inside the dbt workflow. Other
tools and producer-side contracts can cover different parts of the data
lifecycle.

-   **Great Expectations:** useful for defining and running expectation
    suites and profiling data in workflows outside or alongside dbt.
-   **Soda:** useful for data quality checks and monitoring in supported
    data pipelines.
-   **Producer-side data contracts:** define schema, semantics, keys,
    freshness, and compatibility obligations at the source boundary
    before data reaches downstream models.

Avoid implementing the same expensive check independently in every
system without a clear owner. Decide where a guarantee is best enforced:
at ingestion, in staging, at a public mart boundary, or in a
consumer-specific workflow. A producer contract cannot replace
downstream semantic tests; dbt tests cannot prevent a producer from
publishing a breaking schema unless a pipeline checks the contract
before accepting it.

## 14. Hands-on lab: `experiments/04_tests_contracts/`

This lab follows the roadmap sequence: key tests, deliberate failures,
singular and custom generic tests, a CASE-heavy unit test, an enforced
contract and incompatible type change, model versioning/deprecation, and
a recurring-failure report.

### 14.1 Lab layout

Use this as a standalone mini-project, or merge its files into the
existing dbt project. A dbt project has one active root; do not place a
nested `dbt_project.yml` inside the main project's `models/` folder and
expect it to behave as an independent project. The lab includes a
singular composite-grain test because `fct_order_items` is unique by the
pair `(order_id, order_line_id)`, not by `order_line_id` alone.

``` text
experiments/04_tests_contracts/
├── README.md
├── dbt_project.yml
├── models/
│   ├── staging/
│   │   ├── stg_orders.sql
│   │   ├── stg_order_items.sql
│   │   └── stg_customers.sql
│   ├── intermediate/
│   │   ├── int_order_status.sql
│   │   └── int_order_status.yml
│   └── marts/
│       ├── fct_orders.sql
│       ├── fct_order_items.sql
│       └── schema.yml
├── seeds/
│   ├── lab_orders.csv
│   ├── lab_order_items.csv
│   └── lab_customers.csv
├── macros/
│   └── generic_tests/
│       └── test_non_negative.sql
└── tests/
    ├── assert_order_total_matches_items.sql
    └── assert_fct_order_items_grain.sql
```

The `schema.yml` and `int_order_status.yml` files contain model and
unit-test properties respectively. Keep names unique if merging into a
larger project.

### 14.2 Project configuration

`dbt_project.yml`:

``` yaml
name: experiments_04_tests_contracts
version: "1.0.0"
config-version: 2
profile: your_existing_profile_name

model-paths: ["models"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
test-paths: ["tests"]
clean-targets: ["target", "dbt_packages"]

models:
  experiments_04_tests_contracts:
    staging:
      +materialized: view
    intermediate:
      +materialized: view
    marts:
      +materialized: table

seeds:
  experiments_04_tests_contracts:
    +quote_columns: false
```

Replace the profile name with your configured profile. Point it to a
development schema only. The project configuration's model path keys
must match the project's name and directory structure.

### 14.3 Seed fixtures

`seeds/lab_customers.csv`:

``` csv
customer_id,customer_name
1,Ada
2,Linus
3,Grace
```

`seeds/lab_orders.csv`:

``` csv
order_id,customer_id,payment_status,shipped_at,order_total
101,1,paid,2026-01-02,15.00
102,2,refunded,,7.50
103,3,pending,,12.00
```

`seeds/lab_order_items.csv`:

``` csv
order_id,order_line_id,line_total
101,1,10.00
101,2,5.00
102,1,7.50
103,1,12.00
```

Seed type inference varies by adapter. Configure seed column types when
necessary, especially for IDs, dates, and fixed-scale decimals. Empty
`shipped_at` cells may be parsed differently across platforms; adjust
the seed type or cast in the staging model.

### 14.4 Staging and mart models

`models/staging/stg_customers.sql`:

``` sql
select
    cast(customer_id as bigint) as customer_id,
    customer_name
from {{ ref('lab_customers') }}
```

`models/staging/stg_orders.sql`:

``` sql
select
    cast(order_id as bigint) as order_id,
    cast(customer_id as bigint) as customer_id,
    payment_status,
    cast(nullif(shipped_at, '') as date) as shipped_at,
    cast(order_total as numeric(18, 2)) as order_total
from {{ ref('lab_orders') }}
```

The `nullif` and cast syntax is broadly common but must be verified on
the chosen adapter. If the seed column is already typed as date, remove
the string conversion and use the appropriate null handling.

`models/staging/stg_order_items.sql`:

``` sql
select
    cast(order_id as bigint) as order_id,
    cast(order_line_id as bigint) as order_line_id,
    cast(line_total as numeric(18, 2)) as line_total
from {{ ref('lab_order_items') }}
```

`models/marts/fct_orders.sql`:

``` sql
select
    order_id,
    customer_id,
    case
        when payment_status = 'refunded' then 'cancelled'
        when shipped_at is not null then 'shipped'
        when payment_status = 'paid' then 'placed'
        else 'pending'
    end as order_status,
    order_total
from {{ ref('stg_orders') }}
```

`models/marts/fct_order_items.sql`:

``` sql
select
    order_id,
    order_line_id,
    line_total
from {{ ref('stg_order_items') }}
```

`models/intermediate/int_order_status.sql`:

``` sql
select
    order_id,
    payment_status,
    shipped_at,
    case
        when payment_status = 'refunded' then 'cancelled'
        when shipped_at is not null then 'shipped'
        when payment_status = 'paid' then 'placed'
        else 'pending'
    end as order_status
from {{ ref('stg_orders') }}
```

These models intentionally keep the business logic small. They are
fixtures for testing semantics, not a complete production commerce
model.

### 14.5 Add mart tests

`models/marts/schema.yml`:

``` yaml
version: 2

models:
  - name: fct_orders
    description: "One row per order."
    config:
      contract:
        enforced: true
    columns:
      - name: order_id
        data_type: bigint
        constraints:
          - type: not_null
          - type: primary_key
        data_tests:
          - not_null
          - unique
      - name: customer_id
        data_type: bigint
        constraints:
          - type: not_null
        data_tests:
          - not_null
          - relationships:
              arguments:
                to: ref('stg_customers')
                field: customer_id
      - name: order_status
        data_type: varchar
        data_tests:
          - accepted_values:
              arguments:
                values: ['placed', 'shipped', 'cancelled', 'pending']
      - name: order_total
        data_type: numeric(18, 2)
        data_tests:
          - not_null
          - non_negative

  - name: fct_order_items
    description: "One row per order line."
    columns:
      - name: order_id
        data_tests:
          - not_null
          - relationships:
              arguments:
                to: ref('fct_orders')
                field: order_id
      - name: order_line_id
        data_tests:
          - not_null
      - name: line_total
        data_tests:
          - not_null

  # The parent key must itself be valid; a child relationship test does
  # not detect duplicate parent keys.
  - name: stg_customers
    columns:
      - name: customer_id
        data_tests:
          - not_null
          - unique
```

This example demonstrates a custom generic test, key tests, and a
contract on `fct_orders`. If your adapter does not support one of the
declared constraints or contract features, remove only the unsupported
constraint after documenting the limitation; keep the data tests where
they are needed. Check whether `varchar` and `bigint` are the correct
adapter types. For a production `fct_order_items`, test a composite key
such as `(order_id, order_line_id)`; `order_line_id` alone is not
assumed globally unique by this fixture.

### 14.6 Custom generic test

Create `macros/generic_tests/test_non_negative.sql`:

``` sql
{% test non_negative(model, column_name) %}
select *
from {{ model }}
where {{ column_name }} < 0
{% endtest %}
```

The test deliberately leaves null detection to `not_null`, so both tests
are needed when the value is required.

### 14.7 Singular reconciliation test

Create `tests/assert_order_total_matches_items.sql`:

``` sql
with item_totals as (
    select order_id, sum(line_total) as calculated_total
    from {{ ref('fct_order_items') }}
    group by order_id
)
select
    o.order_id,
    o.order_total,
    i.calculated_total
from {{ ref('fct_orders') }} as o
left join item_totals as i
    on o.order_id = i.order_id
where i.calculated_total is null
   or o.order_total != i.calculated_total
```

This fixture is designed to pass for the supplied data. In real
projects, include taxes, discounts, shipping, currency conversions, and
rounding if they are part of the order-total definition.

Also create `tests/assert_fct_order_items_grain.sql`:

``` sql
select
    order_id,
    order_line_id,
    count(*) as row_count
from {{ ref('fct_order_items') }}
group by order_id, order_line_id
having count(*) > 1
```

This singular test returns duplicated composite keys. It is separate
from reconciliation because correct totals do not prove that each order
line is unique.

### 14.8 Unit test for CASE logic

Add `models/intermediate/int_order_status.yml`:

``` yaml
unit_tests:
  - name: test_int_order_status_case_logic
    model: int_order_status
    given:
      - input: ref('stg_orders')
        rows:
          - {order_id: 201, customer_id: 1, payment_status: 'refunded', shipped_at: null, order_total: 5.00}
          - {order_id: 202, customer_id: 2, payment_status: 'paid', shipped_at: '2026-01-02', order_total: 6.00}
          - {order_id: 203, customer_id: 3, payment_status: 'paid', shipped_at: null, order_total: 7.00}
    expect:
      rows:
        - {order_id: 201, payment_status: 'refunded', shipped_at: null, order_status: 'cancelled'}
        - {order_id: 202, payment_status: 'paid', shipped_at: '2026-01-02', order_status: 'shipped'}
        - {order_id: 203, payment_status: 'paid', shipped_at: null, order_status: 'placed'}
```

The fixture includes all input columns selected by `int_order_status`,
but `expect` lists only the columns needed to assert the result. Confirm
the installed dbt unit-test syntax and date literal behavior. Unit tests
require dbt Core 1.8+ and adapter support; on unsupported versions,
retain the fixture-based integration test approach and do not claim a
unit test ran.

### 14.9 Deliberate failure exercise

Work only in this development lab.

1.  Run `dbt seed` and `dbt build` to establish a clean baseline.
2.  In `lab_customers.csv`, temporarily duplicate `customer_id=1`, run
    `dbt seed --full-refresh`, then run `dbt test --select stg_customers`.
    The parent's `unique` test should fail. This is separate from the
    child relationship test, which does not detect duplicate parent keys.
3.  Remove customer 2 from `lab_customers.csv`, reload the seed, and run
    `dbt test --select fct_orders`. The order for customer 2 should fail
    the `relationships` test because its parent is missing.
4.  Temporarily set a required `customer_id` in `lab_orders.csv` to an
    empty/null value, reload the seed, and confirm `not_null` fails.
5.  Restore the fixture and reload it before continuing.

To test the `fct_orders.order_id` uniqueness test directly, duplicate an
`order_id` in `lab_orders.csv`, reload the seed, and run
`dbt test --select fct_orders`. To test the order-line grain, duplicate
an `(order_id, order_line_id)` pair in `lab_order_items.csv`, reload the
seed, and run `dbt test --select assert_fct_order_items_grain`. Restore
each fixture after verifying its expected failure.

### 14.10 Contract mismatch exercise

After the baseline contract passes, temporarily change `fct_orders.sql`
to cast `order_total` to a string while the YAML contract still declares
`numeric(18, 2)`:

``` sql
cast(order_total as varchar) as order_total
```

Run:

``` bash
dbt build --select fct_orders
```

Expected result: on a dbt/adapter combination that supports enforced
contracts for this materialization, the build should fail because the
output type does not match the declared contract. If it does not,
inspect adapter support and the actual inferred type; do not report a
successful demonstration without observing the failure. Restore the
numeric type before continuing.

### 14.11 Versioning exercise

After restoring the baseline, confirm model-version support in your dbt
release and then:

1. Rename `models/marts/fct_orders.sql` to
   `models/marts/fct_orders_v1.sql`. Keep the v1 output type for
   `order_total` at `numeric(18, 2)`.
2. Create `models/marts/fct_orders_v2.sql` from v1 and change the
   expression to `cast(order_total as numeric(20, 4)) as order_total`.
   Keep all other output columns and business logic unchanged so the
   interface change is isolated.
3. Replace the `fct_orders` entry in `models/marts/schema.yml` with the
   following versioned declaration. Preserve the tests on the top-level
   columns; the v1 override changes only its `order_total` type.

``` yaml
version: 2

models:
  - name: fct_orders
    latest_version: 2
    config:
      contract:
        enforced: true
    columns:
      - name: order_id
        data_type: bigint
        constraints:
          - type: not_null
          - type: primary_key
        data_tests:
          - not_null
          - unique
      - name: customer_id
        data_type: bigint
        constraints:
          - type: not_null
        data_tests:
          - not_null
          - relationships:
              arguments:
                to: ref('stg_customers')
                field: customer_id
      - name: order_status
        data_type: varchar
        data_tests:
          - accepted_values:
              arguments:
                values: ['placed', 'shipped', 'cancelled', 'pending']
      - name: order_total
        data_type: numeric(20, 4)
        data_tests:
          - not_null
          - non_negative
    versions:
      - v: 1
        deprecation_date: 2027-06-30
        columns:
          - include: all
          - name: order_total
            data_type: numeric(18, 2)
      - v: 2
        columns:
          - include: all
```

4. Compile/build both versions and update one downstream consumer to
   reference the new interface. For example, a consumer that must remain
   on v1 can use `{{ ref('fct_orders', v=1) }}`; a consumer using
   `{{ ref('fct_orders', v=2) }}` is pinned to v2, while an unpinned
   `{{ ref('fct_orders') }}` resolves to `latest_version: 2`.
5. Confirm that the deprecation warning is associated with v1, document
   the owner and migration deadline, and inventory remaining v1
   consumers. Do not remove v1 until migration is complete.

The date is an example policy date; choose a future date approved by the
model owner. Model versioning and deprecation metadata do not migrate
consumers automatically.

### 14.12 Store failures and build a recurring report

Run:

``` bash
dbt test --select assert_order_total_matches_items --store-failures
```

If supported, identify the failure relation from dbt output. Cause one
controlled failure, store the result, then restore the source. Export or
parse run results across at least two controlled runs into a small
history table with invocation, timestamp, test identifier, status, and
failure count. Aggregate by test name to see repeated failures. A single
stored-failure relation cannot by itself demonstrate recurrence across
time.

### 14.13 Commands in sequence

From the lab project root:

``` bash
dbt debug
dbt seed
dbt build
dbt test --select fct_orders
dbt test --select assert_order_total_matches_items
dbt test --select assert_fct_order_items_grain
dbt test --select test_type:unit
dbt test --select fct_orders --store-failures
```

Some commands may need a version-specific selector adjustment. Use
`dbt ls --select ...` to confirm selection. Run the unit-test command
only if the installed dbt version and adapter support unit tests. Run
failure storage only where supported. The first `dbt build` should use
the supplied consistent fixtures and is expected to pass after
types/configuration are adapted to the warehouse.

### 14.14 Troubleshooting

  -------------------------------------------------------------------------------------
  Symptom                 Likely cause              Response
  ----------------------- ------------------------- -----------------------------------
  A relationship test     Relationship tests        Add a separate `not_null` test.
  passes despite null     typically exclude null    
  keys                    child values              

  Contract rejects a      Declared type differs     Inspect compiled SQL and warehouse
  valid model             from actual adapter       type; align the contract
                          output type               intentionally.

  Contract does not fail  Adapter/materialization   Verify support and actual output
  after type change       does not support          type; don't claim enforcement
                          enforcement as expected,  without evidence.
                          or type coercion hides    
                          mismatch                  

  Unit-test fixture fails dbt version, adapter,     Check version-specific unit-test
  to compile              fixture type, or YAML     documentation and type/date syntax.
                          syntax mismatch           

  Custom generic test is  Macro is outside          Verify
  unknown                 `macro-paths` or has      `macros/generic_tests/test_*.sql`
                          invalid naming/syntax     and run `dbt parse`.

  Stored failures are not Unsupported               Read command output and inspect the
  visible                 adapter/configuration,    configured failure schema.
                          test not failing, or      
                          wrong schema              

  Test is always a        Severity/config placement Verify test config and CI exit-code
  warning                 or warning-as-error       policy; set a meaningful severity.
                          policy                    

  `dbt build` skips a     Upstream resource/test    Inspect run results and selection;
  dependent model         failure or graph          do not assume all resources ran.
                          selection                 

  Row-count test is noisy Normal volume changes or  Use a meaningful range/reference
                          an inappropriate fixed    and an owner; don't mask real
                          threshold                 drift.

  Failure report shows    Stored failures are not   Persist per-invocation metadata and
  only the latest issue   retained as history       counts separately.
  -------------------------------------------------------------------------------------

### 14.15 Completion checklist

-   [ ] I wrote down the grain and consumer guarantees for `fct_orders`.
-   [ ] I added `unique`, `not_null`, `accepted_values`, and
    `relationships` tests where appropriate.
-   [ ] I deliberately broke key/null/relationship fixtures and observed
    the expected failure.
-   [ ] I wrote a singular order-total reconciliation test and a
    composite-grain test for `fct_order_items`.
-   [ ] I wrote a custom generic test and tested both passing and
    failing cases.
-   [ ] I wrote a CASE-heavy unit test using `given`/`expect` where
    supported.
-   [ ] I enforced a model contract and observed the result of an
    incompatible type change.
-   [ ] I created a versioned replacement with a deprecation plan and
    updated a consumer.
-   [ ] I documented group ownership and access intent without confusing
    metadata with warehouse grants.
-   [ ] I stored failures where supported and built a report across
    multiple runs.
-   [ ] I chose blocking versus warning behavior based on consumer
    impact and test confidence.
-   [ ] I reviewed test cost and did not substitute sampling for a
    critical integrity guarantee.
-   [ ] I distinguished static compilation from execution and observed
    results before claiming success.

## 15. Checkpoint and common mistakes

### Checkpoint from the roadmap

-   [ ] Choose the right tests for each model.
-   [ ] Write unit tests and enforce contracts.
-   [ ] Use versions and access modifiers for safe change.
-   [ ] Decide test severity and gating.

### Common mistakes from the roadmap

1.  **Testing only that columns are not null.** Add uniqueness,
    referential integrity, domain, and business-rule tests based on the
    model's grain.
2.  **Tests that always warn and are ignored.** Set severity from risk,
    assign owners, and expire temporary exceptions.
3.  **Contracts missing on public models.** Public interfaces should
    have explicit column/type expectations when supported.
4.  **Breaking a public model without versioning.** Introduce a
    compatible migration path and deprecation plan.

### Final decision questions

Before adding or changing a test, ask:

1.  What consumer guarantee does this test protect?
2.  What exact rows or condition constitute a failure?
3.  Is the test scoped to the correct grain and time window?
4.  Is it blocking, warning, or diagnostic---and why?
5.  Who owns the failure and how will they respond?
6.  What is the query cost, and is the frequency appropriate?
7.  Does the test complement the contract, unit tests, and producer-side
    checks rather than confusing their roles?

## Reference documentation

Use the documentation matching the installed dbt release and adapter:

- [dbt data tests](https://docs.getdbt.com/docs/build/data-tests)
- [dbt unit tests](https://docs.getdbt.com/docs/build/unit-tests)
- [Model contracts](https://docs.getdbt.com/docs/mesh/govern/model-contracts)
- [Model versions](https://docs.getdbt.com/docs/mesh/govern/model-versions)
- [Version property syntax](https://docs.getdbt.com/reference/resource-properties/versions)
- [Deprecation date](https://docs.getdbt.com/reference/resource-properties/deprecation_date)
- [dbt artifacts](https://docs.getdbt.com/reference/artifacts/dbt-artifacts)

**Verification note:** This lesson was statically reviewed for syllabus
coverage, naming consistency, code-block syntax where locally checkable,
and documented version/adapter caveats. It was not executed against a
live dbt project or warehouse during authoring because dbt Core, a dbt
adapter, and a warehouse runtime were unavailable. Validate package APIs,
unit-test support, contract enforcement, failure storage, and
adapter-specific SQL in a disposable development target before production
use.
