# Jinja, Macros, and Packages in dbt

> **Roadmap location:**
> `Stage 2C — Data Engineering_3/06-dbt-and-Analytics-Engineering/03-jinja-macros-and-packages.md`\
> **Topic boundary:** reusable SQL with Jinja, macros, packages, project
> variables, hooks, dispatch, package development, and macro testing.\
> **Prerequisite:** a working dbt project with a configured adapter and
> basic models, sources, and `ref()` usage.

## Learning outcomes

By the end of this lesson, you should be able to:

-   Read and write Jinja expressions, statements, and comments inside
    dbt resources.
-   Explain compilation versus warehouse execution and inspect compiled
    SQL.
-   Use dbt context functions safely and understand when they are
    available.
-   Create readable macros with arguments, defaults, return values, and
    tests.
-   Generate repeated SQL, including pivot columns and unions, without
    hiding business rules.
-   Install and use packages with deliberate version constraints.
-   Manage project variables and environment variables without leaking
    credentials.
-   Use `adapter.dispatch`, schema/alias naming overrides, hooks, and
    `dbt run-operation` with clear trade-offs.
-   Package reusable macros for internal distribution and decide when a
    macro is not justified.

## 1. The mental model: Jinja writes SQL; the warehouse runs SQL

dbt models are usually SQL files with Jinja embedded in them. During
dbt's parsing and compilation process, Jinja is evaluated to produce SQL
and to identify dependencies such as `ref()` and `source()`. The adapter
then submits the compiled SQL to the data platform as part of the
selected dbt command.

``` text
model.sql + Jinja + project config + dbt context
                    |
                    v
            parse / compile
                    |
                    v
         target/compiled/<project>/...
                    |
                    v
          adapter submits SQL
                    |
                    v
             warehouse result
```

Compilation does **not** prove that the SQL is valid for the target
warehouse, that permissions are sufficient, or that the query returns
correct data. Those require an appropriate execution and validation
step.

### 1.1 Three Jinja delimiters

  -----------------------------------------------------------------------------------------------------------
  Syntax                  Purpose                 Example
  ----------------------- ----------------------- -----------------------------------------------------------
  `{{ ... }}`             Expression: render a    `select {{ cents_to_dollars('amount_cents') }} as amount`
                          value or macro output   
                          into the template       

  `{% ... %}`             Statement: control      `{% if target.name == 'prod' %}`
                          flow, assignment, macro 
                          definitions, or dbt     
                          directives              

  `{# ... #}`             Template comment:       `{# temporary explanation for maintainers #}`
                          removed from rendered   
                          output                  
  -----------------------------------------------------------------------------------------------------------

Jinja is a templating language, not a SQL dialect. SQL keywords and
expressions inside the template are still intended for the warehouse;
Jinja decides what text gets emitted.

### 1.2 Variables and expressions

``` sql
{% set tax_rate = 0.08 %}
{% set amount = 125.00 %}

select
    {{ amount }} as subtotal,
    {{ (amount * tax_rate) | round(2) }} as tax
```

Illustrative compiled SQL:

``` sql
select
    125.00 as subtotal,
    10.0 as tax
```

The example demonstrates template arithmetic only. Business-critical
financial calculations should normally remain explicit in SQL with a
documented numeric type and rounding policy; do not rely on a Jinja
floating-point calculation for financial precision.

Jinja filters transform template values. For example, `| lower`
lowercases a string and `| replace(' ', '_')` replaces spaces. Filters
operate during rendering, not on warehouse rows.

### 1.3 Conditions

``` sql
select *
from {{ ref('stg_orders') }}
where 1 = 1
{% if var('include_test_orders', false) %}
  -- keep all order types for a controlled test run
{% else %}
  and is_test_order = false
{% endif %}
```

With the default variable, the compiled SQL includes the filter. With
`--vars '{"include_test_orders": true}'`, the condition is omitted. The
SQL syntax for boolean literals can differ by adapter; use a
warehouse-appropriate expression in real models.

Prefer conditions that are short, visible, and easy to reason about. If
a condition changes business meaning, document it and test both
branches.

### 1.4 Loops

``` sql
select
    order_id,
    {% for column_name in ['subtotal', 'tax', 'shipping'] %}
    {{ column_name }}{% if not loop.last %},{% endif %}
    {% endfor %}
from {{ ref('int_order_amounts') }}
```

Compiled SQL:

``` sql
select
    order_id,
    subtotal,
    tax,
    shipping
from <resolved relation for int_order_amounts>
```

Loops are useful for repeating known-safe SQL fragments. A loop over
values discovered from live data is more dynamic and has additional
reliability concerns; see the pivot section below.

### 1.5 Whitespace control

Jinja supports whitespace control with `-`, such as `{%-` and `-%}`. It
removes adjacent whitespace and can make compiled SQL compact. Use it
when it improves readability or avoids unwanted blank lines, but do not
make templates so compressed that the source becomes hard to review.
Readable compiled SQL matters during incident response.

## 2. Compilation and compiled SQL

### 2.1 Inspect the result, not only the template

Run a command appropriate to your project:

``` bash
dbt compile --select stg_payments
```

Then inspect the compiled model under a path similar to:

``` text
target/compiled/<project_name>/models/staging/stg_payments.sql
```

The exact subdirectory follows your model path and project
configuration. `target/compiled/` is generated output and can be
overwritten by later commands. Do not edit it as the source of truth or
commit it unless your repository has a specific reason to retain
generated artifacts.

To inspect SQL actually submitted during execution, use the run
artifacts and logs generated by the dbt command (for example,
`target/run/` where applicable) and the platform's query history.
`target/compiled/` shows rendered SQL; it does not guarantee the
warehouse accepted or ran it.

### 2.2 Before and after

Source model:

``` sql
select
    payment_id,
    {{ cents_to_dollars('amount_cents') }} as amount
from {{ ref('stg_payments') }}
```

Assuming `cents_to_dollars` expands to
`round((cast(amount_cents as decimal(18, 2)) / 100), 2)`, compiled SQL
is conceptually:

``` sql
select
    payment_id,
    round((cast(amount_cents as decimal(18, 2)) / 100), 2) as amount
from <database>.<schema>.<resolved_stg_payments_relation>
```

The relation placeholder above is explanatory, not literal compiled SQL.
dbt renders the actual relation name for the active target. The
adapter's identifier quoting and relation naming conventions also affect
the exact text.

### 2.3 Parsing versus execution context

dbt parses project files to build the manifest and dependency graph.
Some macros execute database queries while compiling or running; such
macros must account for the parse phase, when query execution is not
available. The `execute` context variable indicates whether dbt is in an
execution-capable phase. `dbt_utils.get_column_values` is an example of
a macro that guards query work and can return a default while parsing.

A common failure pattern is to dereference query results during parsing
without checking whether they exist. When authoring introspective
macros, make parse-time behavior explicit and test both the initial
build (when a relation may not exist) and subsequent runs.

## 3. The dbt context functions you need to recognize

These functions and context objects are available in dbt templates, but
their meaning and safe use differ.

  ---------------------------------------------------------------------------------------
  Function / object                       Purpose                 Important behavior or
                                                                  limitation
  --------------------------------------- ----------------------- -----------------------
  `ref('model_name')`                     Resolves a dbt model    Prefer this over
                                          reference and records a hard-coded relation
                                          DAG dependency          names. A `ref()` hidden
                                                                  in conditional or
                                                                  dynamically constructed
                                                                  code may not be
                                                                  detected as expected;
                                                                  keep dependencies
                                                                  explicit.

  `source('source_name', 'table_name')`   Resolves a declared     The source and table
                                          source relation and     must be declared in
                                          records lineage         YAML.

  `config(...)`                           Sets model              Commonly used for
                                          configuration from      materialization and
                                          within a model template hooks. Prefer
                                                                  project-level config
                                                                  for shared defaults;
                                                                  configuration
                                                                  precedence matters.

  `var('name', default)`                  Reads a project         A variable is
                                          variable from           configuration, not a
                                          `dbt_project.yml` or    secret store. Validate
                                          CLI `--vars`            allowed values and
                                                                  defaults.

  `env_var('NAME', default)`              Reads an environment    Useful for deployment
                                          variable                configuration. Missing
                                                                  required variables can
                                                                  fail rendering;
                                                                  secret-prefixed
                                                                  variables have
                                                                  additional restrictions
                                                                  in dbt.

  `this`                                  Represents the current  Particularly useful in
                                          model's database        incremental models and
                                          relation                hooks. The relation may
                                                                  not yet exist on the
                                                                  first build.

  `target`                                Describes the active    Useful for
                                          target, including       environment-specific
                                          attributes such as      behavior. Do not use
                                          `name`, `schema`, and   target checks to
                                          adapter-related         silently change
                                          configuration           business definitions.

  `is_incremental()`                      Returns true when the   The macro's branch must
                                          model is configured as  be valid SQL in both
                                          incremental and dbt     incremental and
                                          considers it an         non-incremental cases.
                                          incremental run rather  
                                          than an                 
                                          initial/full-refresh    
                                          build                   
  ---------------------------------------------------------------------------------------

Example of `is_incremental()` in context:

``` sql
{{ config(materialized='incremental', unique_key='payment_id') }}

select payment_id, updated_at, amount
from {{ source('stripe', 'payments') }}
{% if is_incremental() %}
where updated_at >= (select coalesce(max(updated_at), '1900-01-01') from {{ this }})
{% endif %}
```

This illustrates conditional SQL, not a complete late-arriving-data
strategy. Choose a warehouse-compatible timestamp literal, consider a
lookback window, and ensure the unique key and incremental strategy match
the source's update behavior. On the initial build or a full refresh, the
incremental filter is omitted.

Examples:

``` sql
select *
from {{ source('stripe', 'payments') }}
```

``` sql
{{ config(materialized='view') }}

select *
from {{ ref('stg_payments') }}
```

``` sql
{% set reporting_currency = var('reporting_currency', 'USD') %}
select '{{ reporting_currency }}' as reporting_currency
```

The last example is only safe if the variable is controlled and
appropriately quoted/validated. Do not concatenate arbitrary untrusted
values into SQL. For identifiers, use adapter-aware quoting and
allowlists; for values, use the warehouse's supported parameterization
or safe literal-handling pattern where available.

## 4. From repeated SQL to a macro

A macro is a named Jinja template that can be called from models, tests,
hooks, and other macros. It can render SQL text or return structured
values. Store project macros under `macros/` by convention.

### 4.1 First macro

Create `macros/cents_to_dollars.sql`:

``` sql
{% macro cents_to_dollars(cents_expression, scale=2) -%}
    round(
        (cast({{ cents_expression }} as decimal(18, 2)) / 100),
        {{ scale }}
    )
{%- endmacro %}
```

Call it from a model:

``` sql
select
    payment_id,
    {{ cents_to_dollars('amount_cents') }} as amount
from {{ ref('stg_payments') }}
```

Conceptual compiled expression:

``` sql
round(
    (cast(amount_cents as decimal(18, 2)) / 100),
    2
)
```

**Argument contract:** `cents_expression` is a SQL expression supplied
by a trusted model author, not an arbitrary user-provided string.
`scale` is a numeric SQL literal and should be restricted to a
reasonable integer range. The example's decimal type is illustrative and
may need adjustment for the adapter's numeric type syntax and precision
rules.

### 4.2 Rounding is a business rule

For this macro, the explicit policy is: cast to a decimal type, divide
cents by 100, and round the result to two decimal places. Test boundary
values such as `0`, `1`, `105`, `-105`, and large amounts. Warehouse
engines can differ in tie-breaking rules and numeric types, so do not
assume this expression is a universal financial standard. If the
warehouse supports a suitable numeric type and a defined rounding
policy, encode that policy deliberately.

A different policy might preserve the full decimal result and round only
at presentation time. Neither policy is universally correct; choose
according to accounting requirements and apply it consistently.

### 4.3 Defaults, invocation, and return semantics

Jinja macro arguments can have defaults:

``` sql
{% macro example_label(value, prefix='value_') -%}
    '{{ prefix }}' || cast({{ value }} as varchar)
{%- endmacro %}
```

Call with the default:

``` sql
{{ example_label('order_id') }}
```

Or override it:

``` sql
{{ example_label('order_id', prefix='order_') }}
```

The string concatenation and cast syntax is adapter-dependent; this
example illustrates arguments, not a cross-database implementation.

There are two patterns to distinguish:

1.  **Rendered SQL text:** most SQL-generating macros emit template
    text, which becomes part of the model SQL.
2.  **Structured return values:** dbt's `return()` helper can return a
    list, dictionary, boolean, or other object without forcing it into a
    string. This is useful when a macro computes a value that another
    macro or template will inspect.

Example:

``` sql
{% macro payment_method_names() %}
    {% set names = ['card', 'cash', 'bank_transfer'] %}
    {{ return(names) }}
{% endmacro %}
```

Use the returned list in a template:

``` sql
{% set methods = payment_method_names() %}
{% for method in methods %}
  -- generate a fragment for {{ method }}
{% endfor %}
```

A macro that returns a list is not the same as a macro that emits a
comma-separated SQL list. Decide which contract is needed and
name/document the macro accordingly.

### 4.4 Use the cents macro in five models

For the lab, the same transformation will be used in five models:

-   `stg_payments`
-   `stg_refunds`
-   `int_order_payments`
-   `int_order_refunds`
-   `fct_payment_activity`

Each model must have an `amount_cents` expression available at the point
of use. If a model does not have that column, do not force the macro
into it merely to reach five calls. In the lab fixture, create the
minimal input columns explicitly or adapt the five model names to your
existing project. A shared macro is justified because the conversion
rule is genuinely repeated; a macro for a one-off two-line expression
usually is not.

## 5. Repetitive SQL: loops, unions, and pivots

### 5.1 Static loops versus data-driven loops

A static loop over a known list is predictable:

``` sql
{% set amount_columns = ['subtotal_cents', 'tax_cents', 'shipping_cents'] %}
select
    order_id,
    {% for col in amount_columns %}
    {{ cents_to_dollars(col) }} as {{ col | replace('_cents', '') }}{% if not loop.last %},{% endif %}
    {% endfor %}
from {{ ref('stg_orders') }}
```

This emits three expressions. The list is controlled by source code,
which makes the generated schema reviewable.

A data-driven loop can discover values from a relation. This is useful
for pivoting but can make output columns change when the data changes.
That affects downstream models, contracts, BI dashboards, and CI
reproducibility.

### 5.2 `dbt_utils.get_column_values`

After installing `dbt_utils`, retrieve distinct values from a relation:

``` sql
{% set payment_methods = dbt_utils.get_column_values(
    table=ref('stg_payments'),
    column='payment_method',
    where='payment_method is not null',
    order_by='payment_method',
    default=[]
) %}
```

Important details:

-   The `table` argument is a dbt `Relation`, commonly returned by
    `ref()` or `source()`.
-   The macro queries the warehouse when execution is available; it is
    not simply a static parser of your model file.
-   `order_by` is SQL supplied to the macro and controls ordering. A
    deterministic order is important for stable generated SQL.
-   `default=[]` handles cases where the relation is not yet available
    during parsing or on a first run. It does **not** create missing
    columns or guarantee the model can execute with zero pivot values.
-   Introspective queries can add compilation latency and can fail when
    the relation is missing, inaccessible, or the column name is wrong.
-   Values are based on data observed at compile/run time. If new values
    appear, generated SQL may change.
-   The macro's exact implementation and adapter behavior depend on the
    installed `dbt_utils` version; inspect the installed package source
    when behavior matters.

For a production mart, consider an explicit, governed list of payment
methods when the set of output columns is part of a stable interface.

### 5.3 A pivot macro with a loop

Create `macros/pivot_payment_methods.sql`:

``` sql
{% macro pivot_payment_methods(
    method_column,
    amount_expression,
    payment_methods
) -%}
    {% for method in payment_methods %}
    sum(
        case
            when {{ method_column }} = '{{ method | replace("'", "''") }}'
            then {{ amount_expression }}
            else 0
        end
    ) as {{ adapter.quote('amount_' ~ (method | lower | replace(' ', '_') | replace('-', '_'))) }}
    {%- if not loop.last %},{% endif %}
    {% endfor %}
{%- endmacro %}
```

Use it in `models/marts/fct_payment_method_summary.sql`:

``` sql
{% set payment_methods = dbt_utils.get_column_values(
    table=ref('stg_payments'),
    column='payment_method',
    where='payment_method is not null',
    order_by='payment_method',
    default=[]
) %}

select
    customer_id,
    {{ pivot_payment_methods(
        'payment_method',
        'amount',
        payment_methods
    ) }}
from {{ ref('stg_payments') }}
group by customer_id
```

This example assumes `stg_payments` exposes `customer_id`,
`payment_method`, and a numeric `amount` column. The macro escapes
apostrophes in string literals and quotes generated aliases through the
active adapter. However, the simple alias normalization can still cause
collisions (for example, `bank-transfer` and `bank transfer` both
normalize to `bank_transfer`). Production code should validate allowed
values, detect alias collisions, and preferably use an explicitly
maintained mapping from source values to stable column names.

If `payment_methods` is empty, the generated `select` list is invalid.
Handle this case deliberately---for example, fail compilation with a
clear error or supply a governed default list. Do not assume
`default=[]` makes an empty pivot executable.

### 5.4 Unioning many relations

A union macro can reduce repetitive `select ... union all` blocks, but
prefer a well-tested package macro such as `dbt_utils.union_relations`
when its semantics fit. Read its documentation and source for behavior
around column alignment, source columns, and type casting. Do not
replace a straightforward two-table union with a custom framework just
to avoid a few lines of SQL.

## 6. Packages and dependency management

Packages distribute macros, tests, and other dbt resources. They are
dependencies, not magic functions; their macros still have inputs,
version constraints, adapter support, and runtime behavior.

### 6.1 `packages.yml` and `dbt deps`

A project may declare dependencies in a root-level `packages.yml`:

``` yaml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.3.0

  - package: metaplane/dbt_expectations
    version: 0.10.10

  - package: dbt-labs/audit_helper
    version: 0.12.2

  - package: dbt-labs/codegen
    version: 0.12.1
```

These are **example pins**, not a guarantee that this combination is
compatible with every dbt Core/dbt platform version or adapter. Check the
package hub and repository compatibility notes for your exact dbt
version and adapter before adopting them. The maintained fork currently
documents `metaplane/dbt_expectations`; the original
`calogica/dbt_expectations` repository has stated that it is no longer
actively supported. Do not silently switch package namespaces without
reviewing migration implications.

Install dependencies:

``` bash
dbt deps
```

`dbt deps` resolves and installs declared packages into the project's
dependency directory (commonly `dbt_packages/`). Run it after changing
package declarations and in CI/deployment environments. Commit the
dependency declaration; use the project's lockfile support if available
in your dbt version and workflow, and keep versions deliberately pinned
for reproducibility. Avoid unbounded version ranges in production.

### 6.2 What the packages are for

  -----------------------------------------------------------------------
  Package                 Typical use             Trade-offs / caution
  ----------------------- ----------------------- -----------------------
  `dbt_utils`             Cross-database utility  Check macro contracts
                          macros, introspection   and adapter support.
                          helpers, SQL            Some macros query the
                          generators, and generic warehouse and depend on
                          tests                   relation existence.

  `dbt_expectations`      Great                   Package maintenance and
                          Expectations-inspired   namespace/version
                          data tests such as      compatibility must be
                          ranges, patterns, and   checked. More
                          distribution checks     expressive tests can
                                                  cost more warehouse
                                                  compute.

  `audit_helper`          Comparing model outputs Use for controlled
                          during migrations or    comparisons; compare
                          refactors               equivalent grain and
                                                  filter conditions.

  `codegen`               Generating source YAML, Generated output is a
                          model YAML, and         starting point for
                          boilerplate from        review, not finished
                          warehouse metadata      documentation or
                                                  governance.
  -----------------------------------------------------------------------

Read the source of at least two `dbt_utils` macros before relying on
them. Check argument names, defaults, dispatch behavior, parse-time
guards, and what happens when a relation is missing.

### 6.3 Example package usage

After confirming the installed package version supports these names and
arguments, a `dbt_utils` test can be declared in model YAML:

``` yaml
models:
  - name: stg_payments
    columns:
      - name: payment_id
        data_tests:
          - not_null
          - unique
```

The built-in `not_null` and `unique` tests are shown here as baseline
examples; they are not specific to `dbt_utils`. A package-specific test
can be used when its documented contract matches the requirement.
Generic-test YAML syntax can differ by dbt version, so follow the syntax
supported by your installed dbt release.

Example of a `dbt_expectations`-style expectation (confirm the current
package namespace and test name before use):

``` yaml
models:
  - name: stg_payments
    columns:
      - name: amount
        data_tests:
          - dbt_expectations.expect_column_values_to_be_between:
              arguments:
                min_value: 0
                strictly: false
```

This checks that `amount` is at least zero, subject to the package
version's supported argument syntax and adapter behavior. Do not add a
test merely because it exists: make sure its rule reflects the data
contract.

Example of code generation:

``` bash
dbt run-operation codegen.generate_source --args '{"schema_name": "RAW_STRIPE"}'
```

This is a template command. Confirm the installed `codegen` macro's
current argument names, target database/schema, and permissions. Review
generated YAML before adding it to source control.

`audit_helper` is commonly used in controlled migration validation, for
example to compare a legacy query with a refactored model. The following
analysis illustrates a documented `compare_column_values` pattern; adapt
the legacy relation, key, and compared column to your project:

``` sql
-- analyses/compare_payment_status.sql
{% set old_query %}
select payment_id, status
from legacy_schema.payments
{% endset %}

{% set new_query %}
select payment_id, status
from {{ ref('stg_payments') }}
{% endset %}

{{ audit_helper.compare_column_values(
    a_query=old_query,
    b_query=new_query,
    primary_key='payment_id',
    column_to_compare='status'
) }}
```

This produces comparison SQL for inspection; it is not automatically a
deployment gate. The key must be unique and non-null in both datasets for
reliable row matching. The legacy relation is illustrative and must be
replaced with a relation your development credentials can access. Confirm
the installed package's current macro signature before relying on it.

## 7. Variables, environment variables, and secrets

### 7.1 Project variables and `--vars`

Declare non-secret project configuration in `dbt_project.yml`:

``` yaml
vars:
  reporting_currency: USD
  include_test_orders: false
```

Read values in a model or macro:

``` sql
{% set currency = var('reporting_currency', 'USD') %}
```

Override for a controlled run:

``` bash
dbt run --vars '{"reporting_currency": "USD", "include_test_orders": true}'
```

Use variables for parameters that legitimately vary by invocation. Avoid
turning them into a hidden business-logic switchboard. Validate
enumerated values and document defaults. A variable used to change an
output schema or business definition should be reviewed like a code
change.

### 7.2 Environment variables

Environment variables are useful for deployment-specific values:

``` yaml
# profiles.yml example; use your adapter's required profile fields
outputs:
  dev:
    type: <adapter>
    schema: "{{ env_var('DBT_SCHEMA', 'analytics_dev') }}"
```

The `<adapter>` placeholder is not literal YAML to copy. Keep your real
profile structure for the chosen adapter. `env_var()` can also be used
in supported dbt project configuration fields. Use environment variables
for configuration such as schema names, account identifiers, and
deployment mode---not as a substitute for access control.

### 7.3 Secrets: practical rules

-   Never place passwords, tokens, private keys, or connection strings
    in `vars`, committed YAML, model SQL, seed files, or macro
    arguments.
-   Inject credentials through the platform's supported secret manager,
    CI secret store, or profile/connection mechanism.
-   dbt has special handling for environment variables with the
    `DBT_ENV_SECRET_` prefix. Their permitted usage is intentionally
    restricted (commonly to profiles and package configuration) and
    values are scrubbed from dbt logs in supported contexts. Verify the
    rules for your dbt version/platform; do not assume secret-prefixed
    variables can be referenced inside model SQL or arbitrary macros.
-   Do not print secrets with `log()`, `print()`, debug statements,
    exceptions, or custom audit hooks.
-   Treat `target/compiled/`, `target/run/`, `manifest.json`, logs, and
    CI artifacts as potentially sensitive. A secret interpolated into
    rendered SQL may persist in artifacts even if logs are scrubbed.
-   Use least-privilege credentials and restrict access to artifacts.
    Rotate any secret that was accidentally committed or rendered;
    deleting a line from the latest file does not erase repository
    history or prior artifacts.
-   Do not use Jinja escaping as a replacement for secret management or
    SQL injection defenses.

## 8. Advanced: cross-database macros and `adapter.dispatch`

SQL syntax varies across adapters. A cross-database macro should either
use dbt's existing cross-database helpers or explicitly dispatch to
adapter-specific implementations.

### 8.1 Dispatch pattern

A public wrapper calls `adapter.dispatch`:

``` sql
{% macro safe_divide(numerator, denominator) -%}
    {{ return(adapter.dispatch('safe_divide', 'my_project')(numerator, denominator)) }}
{%- endmacro %}
```

Define a default implementation in `macros/safe_divide.sql`:

``` sql
{% macro default__safe_divide(numerator, denominator) -%}
    case
      when {{ denominator }} is null or {{ denominator }} = 0 then null
      else {{ numerator }} / {{ denominator }}
    end
{%- endmacro %}
```

For a platform with different syntax, add an adapter-specific
implementation using the appropriate adapter prefix, for example:

``` sql
{% macro bigquery__safe_divide(numerator, denominator) -%}
    safe_divide({{ numerator }}, {{ denominator }})
{%- endmacro %}
```

The `adapter.dispatch` search order depends on the active adapter,
configured dispatch search order, and macro namespace. The wrapper's
package argument (`'my_project'` here) must match the namespace whose
dispatch configuration should be considered. Confirm the exact dispatch
behavior for the dbt version and adapter in use. The examples illustrate
the pattern; test the default and each supported adapter separately.

Use dispatch when implementations genuinely differ by adapter. Do not
create adapter branches for SQL that already works portably or can be
expressed with a dbt cross-database macro.

### 8.2 Cross-database testing

At minimum, test: - Normal numeric inputs. - A zero denominator. - Null
numerator and denominator behavior. - Type coercion and return types. -
The compiled SQL for each supported adapter.

A macro that compiles on one adapter is not automatically cross-database
compatible. Declare the supported adapters and fail clearly for
unsupported behavior rather than emitting plausible but invalid SQL.

## 9. Customizing schema and alias names

dbt exposes naming macros that projects can override. These affect
relation names and therefore can affect downstream tooling, permissions,
and deployment layout. Keep overrides small, documented, and tested.

### 9.1 `generate_schema_name`

The default behavior commonly combines a custom schema value with the
target schema so models do not all land in one shared schema. An
override that blindly returns `custom_schema_name` can unintentionally
remove environment isolation. Understand the default implementation for
your dbt version before changing it.

Example developer-isolation override in
`macros/generate_schema_name.sql`:

``` sql
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set base_schema = target.schema -%}
    {%- if target.name == 'prod' -%}
        {%- if custom_schema_name is not none -%}
            {{ custom_schema_name | trim }}
        {%- else -%}
            {{ base_schema }}
        {%- endif -%}
    {%- else -%}
        {%- set developer_schema = env_var('DBT_USER_SCHEMA', base_schema) | trim -%}
        {%- if custom_schema_name is not none -%}
            {{ developer_schema }}_{{ custom_schema_name | trim }}
        {%- else -%}
            {{ developer_schema }}
        {%- endif -%}
    {%- endif -%}
{%- endmacro %}
```

This is a **policy example**, not a universal production-ready override.
It assumes that production custom schemas should be used as-is and that
development schemas should be prefixed with `DBT_USER_SCHEMA`. Validate
names against your warehouse's identifier length and character rules,
make sure the environment variable is set consistently, and test
dev/CI/prod separately. In particular, do not let an untrusted user
control `target.name` or schema naming values in a way that grants
access to production schemas. Many teams prefer to retain dbt's default
concatenation behavior and only add a developer prefix.

The `node` argument is part of the naming macro signature even if unused
in this example. Do not omit required parameters when overriding a
built-in macro.

### 9.2 `generate_alias_name`

This macro determines the relation alias (the table/view name) from a
model's configured alias and node metadata. An override can enforce
naming conventions, but a global rewrite may break downstream
references, grants, exposures, or operational scripts. Preserve the
default behavior for models without a custom alias unless the project
explicitly wants another policy.

Illustrative minimal override:

``` sql
{% macro generate_alias_name(custom_alias_name=none, node=none) -%}
    {%- if custom_alias_name is not none -%}
        {{ custom_alias_name | trim }}
    {%- else -%}
        {{ node.name }}
    {%- endif -%}
{%- endmacro %}
```

Compare this with the implementation shipped in your installed dbt
version before using it. Built-in macro signatures and defaults can
evolve. Add tests for models with and without `alias`, and test any
downstream naming contracts.

## 10. Hooks and operations

Hooks run SQL at defined points in a dbt command. Their timing,
transaction behavior, permissions, and syntax can vary by adapter and
dbt version.

### 10.1 Hook types

-   **`pre-hook`**: runs before the relevant resource is built. Use
    sparingly for required setup or platform-specific preparation.
-   **`post-hook`**: runs after a resource is built. Common examples
    include grants or metadata operations. If the model build fails, the
    hook should not be assumed to have completed.
-   **`on-run-start`**: runs at the beginning of a run/test/operation
    command where supported by the command and dbt version.
-   **`on-run-end`**: runs after command processing, commonly for
    run-level audit logging or cleanup. Some results are only available
    through run-result context; do not assume it fires after every
    possible process crash.

Hooks are configuration with operational consequences. A hook that is
valid SQL on one warehouse may fail on another. Consider whether the
operation is idempotent, whether it needs elevated privileges, and
whether it should be managed by a platform grants policy instead.

### 10.2 Post-hook grant example

In `dbt_project.yml` (or model config where appropriate):

``` yaml
models:
  my_project:
    marts:
      +post-hook:
        - "grant select on {{ this }} to role ANALYTICS_READ_ONLY"
```

This is **warehouse- and permission-dependent**. The role syntax and
grant syntax differ across platforms; some platforms use different
principal names or grant mechanisms. The executing identity must have
permission to grant access. Test in a non-production schema first,
confirm the exact compiled hook SQL and the resulting privilege, and
consider adapter-supported grants configuration where available. Do not
blindly copy this role syntax into BigQuery, Postgres, Snowflake, or
another platform without verifying its semantics.

### 10.3 Run-level hooks

A simple run-level logging hook can be configured as:

``` yaml
on-run-start:
  - "select 1"

on-run-end:
  - "select 1"
```

These are placeholders illustrating where hooks are configured, not
meaningful audit logging. For real audit logging, use a
warehouse-specific insert/procedure or a supported logging integration,
pass only non-sensitive metadata, and verify how run results are exposed
in the installed dbt version. A SQL statement that succeeds in a model
may not be valid in a hook context.

### 10.4 `dbt run-operation`

`dbt run-operation` invokes a macro outside the normal model build
sequence:

``` bash
dbt run-operation my_maintenance_macro --args '{"dry_run": true}'
```

Macro example:

``` sql
{% macro my_maintenance_macro(dry_run=true) %}
    {% if dry_run %}
        {{ log('Dry run: no warehouse changes requested.', info=true) }}
    {% else %}
        {# Put a reviewed, adapter-specific operation here. #}
        {{ exceptions.raise_compiler_error(
            'Implement and test the adapter-specific operation before disabling dry_run'
        ) }}
    {% endif %}
{% endmacro %}
```

This macro intentionally refuses to perform a real change until the
operation is implemented. `run-operation` can execute privileged SQL
through the configured connection; review its arguments, permissions,
and logs as carefully as a deployment command. Avoid putting secrets in
`--args`.

## 11. `run_query` and `statement` blocks

Use these when a macro genuinely needs query results during execution or
must issue a controlled SQL statement. They are lower-level tools than
ordinary SQL-generating macros and introduce additional complexity.

### 11.1 `run_query`

Example pattern:

``` sql
{% if execute %}
    {% set result = run_query('select 1 as example_value') %}
    {% if result is not none and result.rows | length > 0 %}
        {% set example_value = result.columns[0].values()[0] %}
    {% else %}
        {% set example_value = none %}
    {% endif %}
{% else %}
    {% set example_value = none %}
{% endif %}
```

`run_query` returns a result object for a query when execution is
available; statements that do not return rows may produce no result
table. Check the result before dereferencing it. The query is
adapter-specific SQL and may incur warehouse cost. Keep introspection
queries small, deterministic, and guarded by `execute`.

### 11.2 `statement` blocks

`statement` blocks provide lower-level control over SQL execution and
result fetching:

``` sql
{% if execute %}
    {% call statement('example_query', fetch_result=true) %}
        select 1 as example_value
    {% endcall %}
    {% set result = load_result('example_query') %}
{% endif %}
```

This is illustrative; the result structure and statement options should
be checked against the installed dbt version. Prefer `run_query` for
simple result-returning SQL when it meets the need. Use `statement` only
when explicit result handling or execution control justifies the extra
machinery.

Never execute destructive DDL/DML from an introspective macro without
explicit safeguards, narrow permissions, and a reviewed invocation path.

## 12. Writing and publishing a reusable package

An internal package is worthwhile when multiple projects need a stable,
tested capability---not merely because a macro exists.

### 12.1 Suggested package structure

``` text
company_dbt_utils/
├── dbt_project.yml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── packages.yml
├── macros/
│   ├── cents_to_dollars.sql
│   └── safe_divide.sql
├── tests/
│   └── assert_macro_cents_check.sql
└── integration_tests/
    ├── dbt_project.yml
    ├── models/
    ├── seeds/
    └── profiles.yml.example
```

The package project name is the namespace used by dbt. Avoid a name that
conflicts with a built-in package or another dependency.

### 12.2 Development workflow

1.  Define the public macro contract: arguments, defaults, accepted
    inputs, output SQL/return type, supported adapters, and failure
    behavior.
2.  Keep private helper macros private by naming
    convention/documentation and avoid exposing internal details as
    public APIs.
3.  Add unit-style tests for logic and integration tests that compile
    and run on each supported adapter.
4.  Pin compatible dependencies and define `require-dbt-version` when
    appropriate for the package's actual support range.
5.  Use semantic versioning: patch for compatible fixes, minor for
    backwards-compatible features, major for breaking changes. Follow
    the organization's release policy if it differs.
6.  Publish to an internal Git repository or package registry supported
    by your deployment process. Use a tag or immutable revision rather
    than tracking a moving branch in production.
7.  Maintain a changelog, review contributions, scan dependencies, and
    document upgrade steps.

A package is not validated merely because `dbt deps` succeeds. That only
establishes dependency resolution/installation; it does not prove that
macros compile or behave correctly for each adapter.

## 13. Testing macros

Macro testing has multiple layers because a macro can fail while
rendering, produce invalid SQL, or produce valid SQL with incorrect
results.

### 13.1 Test strategy

  ----------------------------------------------------------------------------
  Layer                   What it proves          Example
  ----------------------- ----------------------- ----------------------------
  Template/compile check  Jinja renders and       `dbt compile --select ...`
                          dependencies resolve    

  SQL execution test      Generated SQL is        Build a small fixture model
                          accepted by the adapter 

  Result assertion        Output matches expected Singular test or controlled
                          business behavior       seed comparison

  Adapter matrix          Dispatch implementation CI jobs against supported
                          works on each claimed   adapters
                          adapter                 

  Edge-case test          Nulls, zeroes,          Dedicated fixtures and
                          negatives, missing      assertions
                          relations, and unusual  
                          values are handled      
  ----------------------------------------------------------------------------

### 13.2 A seed-based test for cents conversion

Create `seeds/macro_cents_cases.csv`:

``` csv
case_id,amount_cents,expected_amount
zero,0,0.00
one_cent,1,0.01
positive_rounding,105,1.05
negative_rounding,-105,-1.05
```

The fixture assumes the chosen warehouse decimal type and rounding
policy make these expected values correct. Add explicit half-way
rounding cases for the target adapter, because rounding tie behavior can
differ.

Create `models/marts/macro_cents_check.sql`:

``` sql
select
    case_id,
    amount_cents,
    expected_amount,
    {{ cents_to_dollars('amount_cents') }} as actual_amount
from {{ ref('macro_cents_cases') }}
```

The seed is referenced with `ref()` like a dbt resource. Configure seed
column types if the adapter's inferred types are unsuitable.

Create `tests/assert_macro_cents_check.sql`:

``` sql
select *
from {{ ref('macro_cents_check') }}
where actual_amount is null
   or actual_amount != expected_amount
```

A singular test passes when it returns zero rows. The comparison
operator and numeric equality semantics should be appropriate for the
adapter and precision policy. If the expected values are approximate
floating-point values, use a tolerance rather than exact equality; for
fixed-scale decimal amounts, exact comparison is usually preferable.

Run:

``` bash
dbt seed --select macro_cents_cases
dbt run --select macro_cents_check
dbt test --select assert_macro_cents_check
```

The exact selection behavior for tests and resources depends on dbt
version and selection syntax; if a selector does not match, use `dbt ls`
to inspect resource names and selection. The seed must exist before the
dependent model runs.

## 14. Hands-on lab: `experiments/03_macros/`

This lab is designed to be added to a working dbt project. It does not
assume a particular warehouse. Replace adapter-specific profile settings
and SQL where marked, and run it against a development schema only.

### 14.1 Lab goals

1.  Find three repeated SQL patterns and decide whether each deserves a
    macro.
2.  Create and use the cents-to-dollars macro in five models.
3.  Create a loop-based pivot macro using `dbt_utils.get_column_values`.
4.  Install and use `dbt_utils` and `dbt_expectations` from declared
    dependencies.
5.  Override schema generation to isolate developers.
6.  Add a post-hook grant where the warehouse supports it.
7.  Test a macro using a small seed.
8.  Inspect compiled SQL and verify resulting behavior.

Before coding, record three candidates in a short design note:

| Repeated pattern | Usually a macro? | Reasoning |
|---|---|---|
| Convert cents to a defined decimal amount in several models | Yes | One shared rule prevents drift and can be tested against representative values. |
| Add a one-off filter used by only one model | Usually no | A macro can hide a simple business rule without removing meaningful repetition. |
| Implement safe division with adapter-specific syntax across several projects | Often yes | A documented wrapper plus `adapter.dispatch` can centralize cross-database behavior. |

Treat these as starting hypotheses, not mandates. Inspect your own lab
models and record the expected benefit, edge cases, and maintenance cost
before introducing each abstraction. Also read the source of two installed
`dbt_utils` macros (for example, `get_column_values` and
`union_relations`) and note their arguments, defaults, parse-time behavior,
and failure cases.

### 14.2 Suggested lab structure

``` text
experiments/03_macros/
├── README.md
├── packages.yml
├── dbt_project.yml
├── macros/
│   ├── cents_to_dollars.sql
│   ├── pivot_payment_methods.sql
│   ├── generate_schema_name.sql
│   └── my_maintenance_macro.sql
├── seeds/
│   ├── macro_cents_cases.csv
│   ├── lab_payments.csv
│   └── lab_refunds.csv
├── models/
│   ├── staging/
│   │   ├── stg_payments.sql
│   │   └── stg_refunds.sql
│   ├── intermediate/
│   │   ├── int_order_payments.sql
│   │   └── int_order_refunds.sql
│   └── marts/
│       ├── fct_payment_activity.sql
│       ├── fct_payment_method_summary.sql
│       └── macro_cents_check.sql
└── tests/
    └── assert_macro_cents_check.sql
```

**Project placement note:** dbt expects one project root. If
`experiments/03_macros/` is a standalone project, run dbt commands from
that directory and give it its own `dbt_project.yml` and compatible
profile target. If it is part of the main project, merge the files into
the existing project root and preserve unique model names. Do not create
nested `dbt_project.yml` files under the main project's `models/`
directory and expect dbt to treat them as independent projects.

### 14.3 Example lab `dbt_project.yml`

``` yaml
name: experiments_03_macros
version: "1.0.0"
config-version: 2

profile: your_existing_profile_name

model-paths: ["models"]
macro-paths: ["macros"]
seed-paths: ["seeds"]
test-paths: ["tests"]
clean-targets: ["target", "dbt_packages"]

models:
  experiments_03_macros:
    staging:
      +materialized: view
    intermediate:
      +materialized: view
    marts:
      +materialized: table
      +post-hook:
        - "grant select on {{ this }} to role ANALYTICS_READ_ONLY"

seeds:
  experiments_03_macros:
    +quote_columns: false
```

Replace `your_existing_profile_name` with the profile configured for
your adapter. The hook shown is only for warehouses whose grant syntax
supports it; comment it out until adapted and tested. For a standalone
lab, ensure the profile target points to a development database/schema
and the configured user has only the permissions required for the lab.

### 14.4 Lab dependencies

Use a root `packages.yml` with tested versions for your dbt release and
adapter. A starter declaration is:

``` yaml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.3.0
  - package: metaplane/dbt_expectations
    version: 0.10.10
```

The maintained fork currently documents `metaplane/dbt_expectations`;
the original `calogica/dbt_expectations` repository has stated that it is
no longer actively supported. Confirm the latest tested release and
compatibility with your dbt version before pinning. Then run:

``` bash
dbt deps
```

Inspect the installed package's README and macro/test source under
`dbt_packages/` before relying on package-specific names.

### 14.5 Seed fixtures

`seeds/lab_payments.csv`:

``` csv
payment_id,order_id,customer_id,payment_method,amount_cents
p1,o1,c1,card,1050
p2,o1,c1,bank_transfer,2500
p3,o2,c2,card,500
p4,o3,c3,cash,1200
```

`seeds/macro_cents_cases.csv`:

``` csv
case_id,amount_cents,expected_amount
zero,0,0.00
one_cent,1,0.01
positive_rounding,105,1.05
negative_rounding,-105,-1.05
```

Use a decimal seed column type if inference produces a floating-point
type or a type unsuitable for exact financial comparisons. The exact
seed configuration syntax should match your dbt version and adapter.

### 14.6 Staging model and five macro calls

`models/staging/stg_payments.sql`:

``` sql
select
    payment_id,
    order_id,
    customer_id,
    payment_method,
    amount_cents,
    {{ cents_to_dollars('amount_cents') }} as amount
from {{ ref('lab_payments') }}
```

Create `seeds/lab_refunds.csv`:

``` csv
refund_id,order_id,customer_id,amount_cents
r1,o1,c1,200
r2,o3,c3,100
```

Use these minimal models so the macro is invoked in five named models.
The repeated conversions are intentionally an exercise in reusing one
rule; in a production DAG, avoid recalculating a value at every layer if
an upstream model already exposes a validated canonical amount.

`models/staging/stg_refunds.sql`:

``` sql
select
    refund_id,
    order_id,
    customer_id,
    amount_cents,
    {{ cents_to_dollars('amount_cents') }} as amount
from {{ ref('lab_refunds') }}
```

`models/intermediate/int_order_payments.sql`:

``` sql
select
    order_id,
    customer_id,
    payment_id as activity_id,
    amount_cents,
    {{ cents_to_dollars('amount_cents') }} as amount,
    'payment' as activity_type
from {{ ref('stg_payments') }}
```

`models/intermediate/int_order_refunds.sql`:

``` sql
select
    order_id,
    customer_id,
    refund_id as activity_id,
    amount_cents,
    {{ cents_to_dollars('amount_cents') }} as amount,
    'refund' as activity_type
from {{ ref('stg_refunds') }}
```

`models/marts/fct_payment_activity.sql`:

``` sql
select order_id, customer_id, activity_id, amount_cents,
       {{ cents_to_dollars('amount_cents') }} as amount,
       activity_type
from (
    select order_id, customer_id, payment_id as activity_id,
           amount_cents, 'payment' as activity_type
    from {{ ref('stg_payments') }}
    union all
    select order_id, customer_id, refund_id as activity_id,
           amount_cents, 'refund' as activity_type
    from {{ ref('stg_refunds') }}
) as activity
```

This is the fifth model call. The two intermediate models demonstrate
the same macro separately, while the final fact demonstrates a union of
compatible payment/refund rows. For production, establish whether refunds
should be represented as positive amounts with an activity type or as
negative amounts; that is a business convention, not a Jinja decision.

### 14.7 Pivot model

`models/marts/fct_payment_method_summary.sql`:

``` sql
{% set payment_methods = dbt_utils.get_column_values(
    table=ref('stg_payments'),
    column='payment_method',
    where='payment_method is not null',
    order_by='payment_method',
    default=[]
) %}

{% if payment_methods | length == 0 %}
    {{ exceptions.raise_compiler_error(
        'No payment_method values found; supply a governed list or load lab_payments first.'
    ) }}
{% endif %}

select
    customer_id,
    {{ pivot_payment_methods('payment_method', 'amount', payment_methods) }}
from {{ ref('stg_payments') }}
group by customer_id
```

This model intentionally fails with a clear message if no payment
methods are found. If the relation is missing during parse, `default=[]`
may trigger the failure, so run the seed and staging model first;
alternatively use a static list for the first compilation. That
distinction should be deliberate and documented.

### 14.8 Add two tests and use one package macro

Baseline built-in tests in `models/staging/schema.yml`:

``` yaml
version: 2

models:
  - name: stg_payments
    columns:
      - name: payment_id
        data_tests:
          - not_null
          - unique
      - name: amount
        data_tests:
          - not_null
```

For a project using dbt 1.10+ and the maintained
`metaplane/dbt_expectations` package, the same schema can include a
package test like this (confirm the exact signature against the installed
release):

``` yaml
version: 2

models:
  - name: stg_payments
    columns:
      - name: payment_id
        data_tests:
          - not_null
          - unique
      - name: amount
        data_tests:
          - not_null
          - dbt_expectations.expect_column_values_to_be_between:
              arguments:
                min_value: 0
                strictly: false
```

On dbt versions before the `arguments:` convention is supported or
recommended, follow that version's generic-test YAML syntax (often the
parameters are written directly under the test name). Do not copy the
newer nested form blindly into an older project. Use a lower bound of zero
only if negative amounts are invalid for this model; refunds may
legitimately be negative or represented separately, so do not apply the
same assertion indiscriminately.

### 14.9 Developer schema isolation

Place the `generate_schema_name` override under `macros/` in the
standalone lab project. Set a unique environment variable before
running:

``` bash
# Bash / Linux / macOS
export DBT_USER_SCHEMA=analytics_dev_alex
dbt debug
dbt compile
```

PowerShell:

``` powershell
$env:DBT_USER_SCHEMA = "analytics_dev_alex"
dbt debug
dbt compile
```

Confirm that the resolved schema is isolated from other developers and
cannot accidentally target production. The naming policy in Section 9 is
an example and must be aligned with your warehouse identifier rules and
your team's default schema policy.

### 14.10 Run the lab in order

From the project root:

``` bash
dbt debug
dbt deps
dbt seed --select lab_payments lab_refunds macro_cents_cases
dbt run --select stg_payments
dbt compile --select stg_payments
dbt run --select fct_payment_method_summary
dbt test --select stg_payments
dbt run-operation my_maintenance_macro --args '{"dry_run": true}'
```

Run the other four cents-conversion models once you have created their
minimal fixtures. Run the seed-based macro check after its model and
singular test are in place. If a selector does not behave as expected,
use `dbt ls` to inspect the exact resource names.

Inspect: - `target/compiled/experiments_03_macros/...` for rendered
SQL. - dbt logs for compile/runtime errors, without printing secrets. -
Warehouse query history and relation metadata for the actual execution
and output. - The target schema and grants to verify isolation and hook
effects.

Do not claim the lab passed solely because compilation succeeded.
Confirm row counts, expected numeric values, pivot columns, target
schema, tests, and grants separately.

Expected outcomes for the supplied fixtures (subject to adapter numeric
semantics):

- `lab_payments` seeds four rows and `lab_refunds` seeds two rows.
- `stg_payments` contains four rows with amounts `10.50`, `25.00`, `5.00`,
  and `12.00` for payment IDs `p1` through `p4`.
- `stg_refunds` contains two rows with amounts `2.00` and `1.00`.
- The pivot includes `amount_bank_transfer`, `amount_card`, and
  `amount_cash` for the observed methods. A customer with no payments for
  a method receives the aggregate's zero behavior from the `else 0` branch.
- The seed-based singular test returns zero failing rows.
- The target schema follows the developer naming policy; a grant is only
  expected if the hook was adapted, executed successfully, and the caller
  had the required privileges.

### 14.11 Troubleshooting

  -----------------------------------------------------------------------
  Symptom                 Likely cause            Response
  ----------------------- ----------------------- -----------------------
  `Compilation Error` for Macro file is outside   Check project root,
  an unknown macro        `macro-paths`, has a    file extension,
                          syntax error, or        `dbt deps`, and macro
                          package is not          spelling.
                          installed               

  `get_column_values`     Referenced model/seed   Seed/build
  reports a missing       has not been built, the prerequisites first;
  relation                schema is wrong, or     verify target and
                          permissions are missing relation existence.

  Pivot SQL has no        The value list is empty Add an explicit
  columns or invalid      or loop comma handling  empty-list guard and
  commas                  is wrong                inspect compiled SQL.

  Pivot aliases collide   Different values        Use a governed
                          normalize to the same   value-to-alias mapping
                          alias                   and collision tests.

  SQL compiles but fails  Adapter-specific        Inspect compiled SQL
  in warehouse            syntax/type/grant       and query error; adapt
                          differences             the SQL and test on the
                                                  target adapter.

  Developer models land   Schema override or      Inspect
  in a shared schema      environment variable is `target.schema`,
                          incorrect               rendered relation
                                                  names, and the naming
                                                  macro; test dev and
                                                  prod separately.

  Grant hook fails        Role syntax differs or  Disable in development
                          executing user lacks    until adapted; use
                          grant privilege         least privilege and
                                                  verify effective
                                                  grants.

  Secret appears in       Secret was interpolated Remove the
  compiled SQL or logs    into a rendered         interpolation, restrict
                          resource or logged      artifacts, rotate the
                                                  secret, and review
                                                  repository/log history.

  `dbt deps` succeeds but API/version/adapter     Read installed package
  package macro fails     mismatch or invalid     docs/source and pin a
                          arguments               compatible version.

  Macro works on one      Dialect-specific SQL    Implement dispatch or
  adapter only            without dispatch or     use a cross-database
                          adapter testing         helper and test each
                                                  supported adapter.
  -----------------------------------------------------------------------

### 14.12 Completion checklist

-   [ ] I can explain `{{ }}`, `{% %}`, and `{# #}` and inspect compiled
    SQL.
-   [ ] I can distinguish rendered SQL from SQL executed by the
    warehouse.
-   [ ] I used the cents macro in five appropriate models with a
    documented rounding policy.
-   [ ] I identified three repeated SQL patterns and justified which
    ones deserve macros.
-   [ ] I created a loop-based pivot and handled empty values and alias
    collisions.
-   [ ] I installed dependencies with `dbt deps` and verified package
    versions/API contracts.
-   [ ] I read the source of two `dbt_utils` macros and recorded their
    arguments, defaults, parse-time behavior, and failure modes.
-   [ ] I used `dbt_utils` and `dbt_expectations` only after checking
    the installed version and test semantics.
-   [ ] I tested the cents macro against a small seed and reviewed
    failure rows.
-   [ ] I inspected `target/compiled/` and separately verified execution
    results.
-   [ ] I tested developer schema isolation and did not weaken
    production isolation.
-   [ ] I adapted or disabled the grant hook until its warehouse syntax
    and permissions were verified.
-   [ ] I did not put secrets in `vars`, model SQL, macro arguments,
    logs, or generated artifacts.
-   [ ] I can explain when a macro would make code harder to understand
    and choose not to write it.

## 15. Macro design rules and common failure modes

### Good reasons to write a macro

-   The same transformation rule appears in several places and must stay
    consistent.
-   SQL syntax differs by adapter and dispatch can encapsulate the
    difference.
-   A tested generator can remove substantial, error-prone boilerplate.
-   A package provides a documented capability that fits the project's
    need.

### Reasons not to write a macro

-   The SQL is already short, clear, and used once.
-   The macro hides business logic behind generic arguments.
-   The generated SQL is harder to review than the repeated SQL.
-   A macro requires live data introspection for something that should
    be a stable contract.
-   A macro is created only to make a line count smaller.
-   The abstraction has many flags, nested conditions, or adapter
    branches that no one can confidently test.

### Common mistakes from the roadmap

1.  **Macros hide business logic.** Keep business definitions visible in
    models or well-documented semantic layers; use macros for reusable
    mechanics.
2.  **Deeply nested Jinja.** Prefer small macros, explicit lists, and
    simple control flow. Inspect compiled SQL.
3.  **Unpinned package versions.** Pin and test versions, review
    changelogs, and update intentionally.
4.  **Secrets in `vars`.** Treat variables as non-secret configuration
    and use supported secret injection.
5.  **Assuming compile means execute.** Compile, run, test, and inspect
    the warehouse separately.
6.  **Assuming package APIs are permanent.** Inspect the installed
    source and compatibility notes.
7.  **Ignoring empty or changing dynamic values.** Use defaults, guards,
    stable ordering, and schema-change controls.
8.  **Using hooks for every operational task.** Prefer platform grants,
    deployment automation, or dedicated procedures when they are clearer
    and more reliable.
9.  **Overriding naming macros without preserving isolation.** Compare
    with the default implementation and test every target.
10. **Calling a macro "cross-database" after one successful run.**
    Declare the supported adapters and validate each implementation.

## 16. Final checkpoint

You have completed this topic when you can:

-   Read and write Jinja in dbt and explain what is generated at compile
    time.
-   Create and test macros with clear argument and return contracts.
-   Use packages responsibly and inspect package source when needed.
-   Explain the behavior and limitations of `ref`, `source`, `config`,
    `var`, `env_var`, `this`, `target`, and `is_incremental()`.
-   Safely handle project configuration and secrets.
-   Use dispatch, naming overrides, hooks, and operations with
    adapter-aware safeguards.
-   Decide when not to write a macro and keep generated SQL
    understandable.

**Verification note:** The examples in this lesson have been reviewed
for internal consistency and documented caveats, but they have not been
executed against a live dbt project or warehouse as part of authoring
this file. Validate adapter-specific SQL, package versions, hooks, and
the lab commands in a disposable development target before production
use.

## 17. Primary references and version checks

Use these primary sources to verify syntax and package APIs against the versions actually installed. Package names and release numbers can change; the pinned versions in this lesson are examples, not a recommendation to upgrade or downgrade an existing project without testing.

- dbt Jinja and context: https://docs.getdbt.com/reference/dbt-jinja-functions
- dbt packages and dependency management: https://docs.getdbt.com/docs/build/packages
- `dbt_utils` package and releases: https://hub.getdbt.com/dbt-labs/dbt_utils/latest/ and https://github.com/dbt-labs/dbt-utils/releases
- Maintained `dbt_expectations` package: https://hub.getdbt.com/metaplane/dbt_expectations/latest/
- `audit_helper` package and macro documentation: https://hub.getdbt.com/dbt-labs/audit_helper/latest/ and https://github.com/dbt-labs/dbt-audit-helper
- `codegen` package and `generate_source` arguments: https://github.com/dbt-labs/dbt-codegen

Before using a package macro, check the installed source and signature, the package's `require-dbt-version` constraint, adapter support, and the project's resolved dependency versions. A successful `dbt deps` is not proof that every macro or test works with the active adapter.
