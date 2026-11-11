# BI Tools and Dashboard Design: Metabase, Apache Superset, and Tableau

> **Audience:** Data engineers, analytics engineers, BI developers, and platform owners.  
> **Scope:** How BI tools connect to governed analytical data, define and present metrics, serve dashboards efficiently, and operate securely in production.

## 1. Title and learning objectives

By the end of this lesson, you should be able to:

- Explain the role of BI between a warehouse/lakehouse and business decisions.
- Compare Metabase, Apache Superset, and Tableau without assuming one tool is universally best.
- Expose curated gold-layer models through least-privilege, read-only database identities.
- Decide which business logic belongs in warehouse models, a semantic layer, or a BI-only presentation calculation.
- Design a focused executive dashboard with governed revenue, conversion, retention, and product-ranking metrics.
- Diagnose slow dashboard cards using query history, SQL inspection, and `EXPLAIN` where supported.
- Apply and test authentication, authorization, database permissions, and row-level security as distinct controls.
- Treat BI configuration as deployable software, including environment promotion, backups/exports, usage review, and retirement.

### Roadmap alignment

The Stage 2C tree places this lesson after descriptive statistics, approximate algorithms, hypothesis testing, experimentation, cohort/funnel/retention analysis, and time-series forecasting. This lesson uses those metric concepts but focuses on the serving, governance, and stakeholder-facing layer. The roadmap's hands-on work is to run Metabase and Superset against gold tables, build equivalent executive dashboards, investigate the slowest cards, enforce regional restrictions, export/restore dashboards, and use usage data to propose retirements.

## 2. Role of BI in a Data Engineering platform

A BI tool is a **querying, modelling, visualization, and distribution interface** over analytical data. It commonly provides database connections, dataset exploration, charts, dashboards, filters, sharing, subscriptions, and sometimes a semantic model or embedded analytics surface.

A healthy flow is:

```text
Operational sources → ingestion → validated staging → conformed models → gold/semantic metrics
                                                                         ↓
                                                           BI dataset / governed query
                                                                         ↓
                                               dashboard → decision → feedback/monitoring
```

BI does not automatically make source data trustworthy. Correct dashboards depend on stable grains, definitions, joins, freshness, access controls, and query performance. A beautiful chart over a fan-out join is still wrong.

### Gold-layer principle

Prefer curated, documented, tested models such as `gold.daily_revenue`, `gold.fct_orders`, `gold.fct_user_activity`, and `gold.dim_product` as BI sources. Raw event tables are often high-volume, weakly typed, late-arriving, and easy to join incorrectly. Raw access can remain available to a small analyst group for exploration, but should not normally be the default dashboard interface.

**Example failure:** `orders` has one row per order and `order_items` has many rows per order. Joining both and summing `orders.order_total` repeats each order total once per item. The correct approach is to aggregate items to order grain first, or use a tested order-level model.

### Responsibility boundaries

| Layer | Owns | Examples |
|---|---|---|
| Warehouse transformation | Canonical grain, joins, deduplication, business entities, reusable transformations | dbt models for orders, customers, daily revenue |
| Semantic layer / governed model | Shared metric definitions, dimensions, permitted aggregation paths | dbt Semantic Layer/MetricFlow, LookML, Power BI model |
| BI presentation layer | Layout, visual encoding, dashboard-specific interaction, labels, display formatting | KPI tile, date filter, drill-through, conditional formatting |
| Operational platform | Credentials, network access, query limits, logs, backups, capacity, deployment | Read-only role, connection pool, alerting, CI/CD |

The preferred order is **warehouse model → semantic layer → BI-only calculation**. This is a governance default, not an absolute rule: presentation-only calculations belong in BI; reusable business definitions should not be copied independently into many cards.

## 3. Prerequisites and lab architecture

### Prerequisites

- Docker Engine and Docker Compose plugin.
- A SQL database or warehouse and permission to create a demonstration schema.
- Basic SQL, joins, aggregation, and dimensional modelling.
- A browser and a local environment where ports `3000`, `8088`, and `5432` are available.

The lab uses PostgreSQL as a portable demonstration analytics database. The same principles apply to BigQuery, Snowflake, Redshift, Databricks SQL, Trino, ClickHouse, and other supported engines, but drivers, SQL dialects, caching, security, and query-plan tools differ.

### Architecture

```text
                         ┌────────────────────┐
Browser ─────────────────► Metabase :3000      │
                         └─────────┬──────────┘
                                   │ read-only role
                         ┌─────────▼──────────┐
                         │ PostgreSQL analytics│ :5432
                         │ gold schema         │
                         └─────────▲──────────┘
                                   │ read-only role
                         ┌─────────┴──────────┐
Browser ─────────────────► Superset :8088      │
                         └────────────────────┘
```

Superset also needs its own metadata database for dashboards, users, and configuration. In production, do not use an ephemeral SQLite metadata database for a multi-user deployment. Use a supported external metadata database and follow the version-specific deployment documentation.

## 4. BI fundamentals and tool landscape

### What BI tools typically do

1. **Connect:** authenticate to a database, warehouse, semantic model, or API.
2. **Model:** define datasets, relationships, calculated fields, dimensions, metrics, and labels.
3. **Explore:** let users filter, drill, pivot, or inspect records.
4. **Visualize:** render tables, KPI cards, bars, lines, maps, funnels, and heatmaps.
5. **Compose:** assemble charts into dashboards with shared filters and explanatory context.
6. **Distribute:** share links, schedule subscriptions, export, or embed content.
7. **Govern:** apply identities, roles, data permissions, audit logs, and certified content—capabilities vary by product and edition.

### Landscape overview

| Tool | Typical fit | Important consideration |
|---|---|---|
| **Metabase** | Fast self-service analytics; SQL and GUI exploration; small-to-medium teams | Simple onboarding; advanced governance, embedding, serialization, and some administration capabilities depend on edition/version |
| **Apache Superset** | Open-source SQL-first dashboards; teams comfortable operating a web application | Flexible and extensible; more operational setup and governance configuration may be required |
| **Tableau** | Rich visual exploration, governed workbooks, broad enterprise BI use | Licensing, deployment model, extract/live choices, and governance workflow affect total cost |
| **Power BI** | Microsoft-centric organizations, Excel/Entra ID/Fabric integration | Capacity, licensing, tenant settings, model refresh, and deployment options vary by offering |
| **Looker** | Governed modelling with LookML, often paired with BigQuery or other supported databases | Modelling workflow and platform ecosystem are central; product fit depends on skills and commercial terms |
| **Mode** | SQL-oriented analysis and reporting workflows | Check current product packaging and integration needs before selecting |
| **ThoughtSpot** | Search/AI-assisted analytics and governed exploration | Value depends on data model quality and user question patterns; validate AI-generated answers |
| **Hex** | Collaborative notebooks, analysis, and app-like data experiences | Often complements rather than replaces enterprise BI governance |
| **Observable** | Code-oriented, interactive data visualization and exploratory analysis | Best fit depends on developer skills and publishing/governance requirements |

Capabilities and product names change over time. Treat this table as a decision framework, not a feature guarantee. Confirm current documentation, edition restrictions, supported drivers, deployment modes, and licensing before procurement. In particular, Metabase row/column security, database impersonation/routing, authenticated embedding, and serialization are edition-dependent; native SQL questions do not inherit Metabase's query-builder row/column security. Superset RLS and dataset/database permissions must be tested against the exact query paths and roles you enable. Public embeds are public, and guest/static embeds do not provide the same user-session-based authorization as authenticated embedding. See the official security and serialization references in Section 18.

### Comparative analysis: Metabase vs Superset vs Tableau

| Criterion | Metabase | Apache Superset | Tableau |
|---|---|---|---|
| Typical use cases | Self-service questions, lightweight dashboards, SQL exploration | SQL-first dashboards, open-source BI platform, analyst-built datasets | Rich visual analysis, enterprise reporting and exploratory dashboards |
| Data connectivity | Common SQL databases and supported drivers; verify exact connector/version | SQLAlchemy-based ecosystem and supported drivers; install/verify required driver | Broad connector ecosystem; validate connector behavior and warehouse-specific features |
| Modelling | GUI models/questions, saved metrics/definitions depending on version/edition; often paired with dbt | Datasets, virtual datasets, calculated columns/metrics; often paired with warehouse/dbt | Data sources, relationships/joins, calculations, extracts; Tableau data model and governance practices matter |
| Semantic integration | Can query curated tables and semantic-layer-backed SQL; integration depth varies | Can query curated models and semantic-layer outputs; avoid assuming a universal native semantic layer | Tableau semantic/data modelling capabilities; external metric governance may still be needed |
| Authoring/interactivity | Generally approachable for non-specialists | Flexible, SQL-centric; dashboard authoring and configuration require more familiarity | Strong visual authoring and interaction; broader learning curve for some teams |
| Governance | Users, groups, collection/content permissions; advanced controls may be edition-dependent | Flask-AppBuilder roles, dataset/database permissions, optional RLS rules; configuration needs testing | Project/site/workbook permissions, row-level patterns and data policies depend on architecture/edition |
| Performance | Database performance, query caching and model choices; options vary by edition/version | Database performance, cache configuration, async/query settings and deployment capacity | Live query vs extract, workbook design, caching and Server/Cloud capacity |
| Deployment | Relatively simple to start; production backup/upgrade strategy still required | Self-hosting gives control but adds application, metadata DB, security, and upgrade operations | Tableau Cloud reduces some infrastructure work; Server requires capacity and platform operations |
| Collaboration/distribution | Sharing, collections, subscriptions/embedding options vary | Dashboards, roles, export/import workflows and embedding options vary | Workbooks, projects, subscriptions, sharing and governed publishing workflows |
| Licensing/TCO | Open-source core with paid offerings; evaluate edition needs and support | Apache-licensed open source; infrastructure and staff time are real costs | Commercial licensing and capacity costs; estimate users, roles, content, and refresh needs |
| Limitations | Some complex enterprise workflows may need paid features or external governance | Operational complexity and extension compatibility can be non-trivial | Cost, governance complexity, and deployment/capacity planning can be significant |
| Suitable team profile | Wants rapid adoption and low setup friction | Has SQL and platform-operations capability and values open-source control | Needs mature visual analytics and is prepared to fund and govern the platform |

No row implies that a product automatically guarantees correct metrics, fast queries, secure tenant isolation, or successful adoption. Those outcomes depend on design and operation.

## 5. Connecting BI tools to analytical data platforms

### Use a dedicated read-only identity

Do not connect dashboards with a personal database account, an owner account, or a role that can write/drop tables. A BI database identity should normally have only `CONNECT`, schema `USAGE`, and `SELECT` on the explicitly approved objects. Keep BI users separate from warehouse transformation identities.

Illustrative PostgreSQL grants (run as a database administrator and adapt database/schema names):

```sql
CREATE ROLE bi_reader LOGIN;
-- Set the password separately with `\password bi_reader` in an interactive psql session,
-- or provision it through a secret manager. Never put the password in source control.
GRANT CONNECT ON DATABASE analytics TO bi_reader;
GRANT USAGE ON SCHEMA gold TO bi_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA gold TO bi_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA gold GRANT SELECT ON TABLES TO bi_reader;

-- Verify a denied write with a test identity in a non-production environment:
-- SET ROLE bi_reader;
-- SELECT * FROM gold.daily_revenue LIMIT 5;  -- expected allowed
-- UPDATE gold.fct_orders SET net_amount = net_amount WHERE false; -- expected permission denied
```

**Important:** PostgreSQL `ALTER DEFAULT PRIVILEGES` applies to objects created by the role whose default privileges are being altered. Run it as the object-creating role or specify `FOR ROLE <creator>` as appropriate. Grants on tables do not automatically cover every future schema, view, function, or materialized view. Re-test grants after deployment.

A safe provisioning script can read secrets from a secret manager or environment at runtime. Avoid putting passwords in a committed Compose file, SQL repository, dashboard export, or command history. Use TLS and network restrictions for remote databases.

### Expose gold schemas deliberately

Typical BI-facing models:

- `gold.fct_orders`: one row per order; includes canonical order status, customer key, order timestamp, currency, and net amount.
- `gold.fct_order_items`: one row per order line.
- `gold.dim_product`: one row per product key.
- `gold.daily_revenue`: one row per business date and approved dimensions.
- `gold.fct_user_activity_daily`: one row per user and activity date, or a governed aggregate if user-level access is not appropriate.
- `gold.metric_conversion_daily`: one row per date/channel/cohort grain with a documented numerator and denominator.

Document the grain and keys in model metadata. Hide or restrict raw PII and raw events unless a clear use case and control framework justify exposure.

### Authentication, authorization, and database access are different

- **Authentication:** who is the user/service? (SSO, password, service identity.)
- **Authorization:** what content or action can that identity access? (dashboard, collection, dataset, SQL editor.)
- **Database permissions:** what can the BI service's database identity query or modify?
- **Row-level security (RLS):** which rows may a query return for a particular viewer or security context?
- **Tenant isolation:** can one customer ever access another customer's data, including through filters, exports, cached results, or embedded tokens?

A dashboard filter is not a security boundary. A user who can edit SQL or query the underlying table may remove a filter. Enforce sensitive row restrictions in the database, a trusted semantic layer, or a BI RLS mechanism that is verified against all query paths. For multi-tenant embedding, use signed/short-lived tokens and server-validated tenant context; never trust a tenant ID supplied only by a client-side URL parameter.

## 6. Semantic modelling and metric governance

### One definition, many consumers

Define each metric with:

- Business name and owner.
- Grain and aggregation rule.
- Numerator and denominator, where applicable.
- Included/excluded statuses and time zone.
- Currency/unit and treatment of refunds, cancellations, and late events.
- Dimensions that may be used to slice it.
- Freshness SLA, tests, and lineage.

Example metric contract:

| Field | `net_revenue` example |
|---|---|
| Grain | Order-level source, aggregated by business date and approved dimensions |
| Definition | Completed order merchandise value minus discounts and refunds, excluding tax/shipping if the business definition says so |
| Aggregation | Sum of canonical order-level `net_amount`; do not sum after joining to line-level rows unless re-aggregated correctly |
| Currency | Report in one currency or explicitly group/convert with documented FX policy |
| Time zone | Business reporting zone, for example `America/New_York`; use one declared policy per metric |
| Owner | Finance/Revenue Analytics |
| Validation | Reconcile to source-of-truth financial report; test uniqueness and accepted statuses |

The example is illustrative: your organization must agree on what “revenue” means. Do not quietly substitute gross bookings, paid order value, recognized revenue, and net revenue.

### Semantic-layer options

- **LookML:** Looker's modelling language for reusable views, dimensions, measures, joins, and governed exploration. Correct join relationships and fanout declarations remain essential.
- **dbt Semantic Layer / MetricFlow:** define metrics and dimensions centrally and query them through supported integrations/API paths. Verify current adapter, metric type, and consumer integration support before committing to an architecture.
- **Power BI data models:** relationships, measures (often DAX), row-level security, and refresh/storage modes provide a governed model for Power BI consumers.
- **Metabase/Superset/Tableau modelling:** these tools have their own dataset, calculated-field, model, or data-source features, but the exact capabilities and governance boundaries differ. Use them for presentation and tool-specific semantics while keeping enterprise-wide definitions centralized when possible.

### Where should logic live?

| Logic | Preferred home | Reason |
|---|---|---|
| Deduplicate events, canonical order status, identity stitching | Warehouse transformation | Shared and testable for all consumers |
| Revenue treatment, conversion denominator, business calendar | Warehouse and/or semantic layer | Prevents dashboards from disagreeing |
| Metric aggregation and approved dimensions | Semantic layer or well-defined gold model | Reuse and governed aggregation paths |
| Date display label, chart-specific reference line | BI layer | Presentation-specific, not a core business definition |
| Ad hoc one-off exploratory calculation | BI layer, clearly labelled exploratory | Avoid premature centralization, but promote if it becomes reused |

Metric ownership is part of governance. A metric without an owner or definition will eventually fork into competing interpretations.

## 7. Dashboard design principles

### Start with a decision, not a chart catalog

A dashboard should answer one principal question for a known audience. For an executive revenue dashboard, a useful question is: **“Are revenue and conversion on track, and where should we investigate?”** The dashboard should guide the next action, not display every available field.

### Suggested hierarchy

1. **Context:** title, reporting period, last successful refresh time, metric caveats.
2. **Headline KPIs:** revenue, conversion rate, and comparison against a meaningful prior period or target.
3. **Trend:** daily/weekly time series with a clearly defined comparison.
4. **Retention:** cohort heatmap where rows are cohort start periods and columns are cohort age; annotate immature cells.
5. **Top products:** sorted horizontal bar chart or table with a named measure and period.
6. **Filters:** a small set of high-value controls such as date, region, channel; show defaults clearly.
7. **Drill-down:** a path to investigate drivers without crowding the top-level view.

### Chart selection and common errors

| Question | Usually suitable | Avoid |
|---|---|---|
| How did a metric change over time? | Line chart with consistent interval | Unsorted timestamps or arbitrary dual axes |
| Which regions differ? | Sorted bar chart or dot plot | 3D bars, inconsistent scales |
| What is the headline state? | KPI tile with unit, period, and comparison | Large number without definition or context |
| How do cohorts retain? | Heatmap with explicit cohort age and denominator | Colour scale without labels or mixing immature cohorts with complete ones |
| Which products lead? | Sorted bar/table with metric and time range | Pie chart with many categories |
| Where is the funnel dropping? | Ordered funnel/table with counts and conversion denominator | A funnel graphic that hides the denominator or mixes user/session grains |

Use consistent units, legible labels, accessible contrast, and colour-blind-safe encodings. Red/green should not be the only way to communicate state. Avoid clutter, decorative 3D, excessive gridlines, and unexplained abbreviations. State whether percentage changes are percentage points or relative percent.

## 8. Performance, caching, and query optimisation

Dashboard latency is a system property: query design, table layout, partitioning, warehouse concurrency, connection pools, result size, BI rendering, cache behavior, and refresh strategy all matter.

### Live queries versus extracts

- **Live query:** each interaction may query the source system. Advantages: freshness and less duplicated data. Risks: concurrency/cost, source workload, variable latency, and dependency on source availability.
- **Extract/import:** data is copied into a BI-managed or engine-specific store. Advantages: predictable interactive latency and reduced source query load. Risks: refresh delay, storage, refresh failures, stale data, and duplicated governance surfaces.
- **Cache:** reuse prior query results under configured keys/TTL/permissions. Improves repeated queries but introduces freshness and invalidation questions. Verify that cache keys preserve identity and RLS context; never let a shared cache leak one tenant's rows to another.

A materialized aggregate in the warehouse is different from a BI cache: it is a maintained data model that can be tested, versioned, and reused by multiple consumers.

### Slow-dashboard debugging sequence

1. Record the three slowest cards and representative filter values.
2. Capture generated SQL and query duration from BI logs/history where available.
3. Run the SQL directly against the serving engine and inspect `EXPLAIN` or the engine's query profile. Use `EXPLAIN ANALYZE` only when it is safe: it executes the query and may consume significant resources.
4. Check scanned rows/bytes, join fanout, missing predicates, non-sargable filters, sorts, spill, and skew.
5. Verify cardinality and grain. Aggregate the many-side before joining; never “fix” duplicated totals with `DISTINCT` unless distinctness is the metric's actual definition.
6. Consider partition pruning, appropriate indexes (where relevant), incremental transformations, pre-aggregated tables, and query limits.
7. Test concurrency and cold-cache/warm-cache behavior separately; do not call one timing a benchmark.
8. Re-check correctness and freshness after optimization.

### Example: gold aggregate

PostgreSQL example, with an assumed `gold.fct_orders` row per order:

```sql
CREATE MATERIALIZED VIEW gold.daily_revenue_by_region AS
SELECT
  (created_at AT TIME ZONE 'UTC')::date AS business_date,
  region,
  SUM(net_amount) AS net_revenue,
  COUNT(*) AS completed_orders
FROM gold.fct_orders
WHERE status = 'completed'
GROUP BY 1, 2;

CREATE INDEX IF NOT EXISTS ix_daily_revenue_region_date
  ON gold.daily_revenue_by_region (business_date, region);
```

This example assumes UTC business dates; change the conversion if the approved metric uses a local business zone. `REFRESH MATERIALIZED VIEW` semantics and locking differ from incremental dbt models and other warehouses. For large tables, schedule a refresh strategy appropriate to the engine, and verify that the source has one row per order and that refunds/cancellations match the metric contract.

## 9. Metabase and Superset setup

The following is a **local learning setup**, not a production deployment recipe. Pin image versions for repeatable work; replace `latest` with a tested version tag or digest before relying on the environment. Confirm version-specific environment variables and image names in official docs.

### 9.1 Compose topology

Create a directory `experiments/07_bi_tools/` with `compose.yaml`. This example provides an analytics PostgreSQL database, Metabase, Superset, and a separate Superset metadata database. It intentionally does not include default admin passwords in source control. Set secret environment variables in your shell or an ignored `.env` file, and do not commit that file.

```yaml
services:
  analytics-db:
    image: postgres:16
    environment:
      POSTGRES_DB: analytics
      POSTGRES_USER: lab_admin
      POSTGRES_PASSWORD: ${ANALYTICS_ADMIN_PASSWORD:?set ANALYTICS_ADMIN_PASSWORD}
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - analytics_data:/var/lib/postgresql/data
      - ./sql:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U lab_admin -d analytics"]
      interval: 5s
      timeout: 3s
      retries: 20

  metabase:
    image: metabase/metabase:v0.52.3
    depends_on:
      analytics-db:
        condition: service_healthy
    ports:
      - "127.0.0.1:3000:3000"
    environment:
      MB_DB_FILE: /metabase-data/metabase.db
    volumes:
      - metabase_data:/metabase-data

  superset-meta-db:
    image: postgres:16
    environment:
      POSTGRES_DB: superset_meta
      POSTGRES_USER: superset_meta
      POSTGRES_PASSWORD: ${SUPERSET_META_PASSWORD:?set SUPERSET_META_PASSWORD}
    volumes:
      - superset_meta_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U superset_meta -d superset_meta"]
      interval: 5s
      timeout: 3s
      retries: 20

  superset:
    image: apache/superset:4.1.1
    depends_on:
      superset-meta-db:
        condition: service_healthy
      analytics-db:
        condition: service_healthy
    ports:
      - "127.0.0.1:8088:8088"
    environment:
      SUPERSET_SECRET_KEY: ${SUPERSET_SECRET_KEY:?set a long random SUPERSET_SECRET_KEY}
      SUPERSET_CONFIG_PATH: /app/pythonpath/superset_config.py
      SUPERSET_META_PASSWORD: ${SUPERSET_META_PASSWORD:?set SUPERSET_META_PASSWORD}
    volumes:
      - superset_home:/app/superset_home
      - ./superset_config.py:/app/pythonpath/superset_config.py:ro
    command: >
      /bin/sh -c "superset db upgrade &&
      superset init && superset run -h 0.0.0.0 -p 8088"

volumes:
  analytics_data:
  metabase_data:
  superset_meta_data:
  superset_home:
```

**Version/driver caveat:** Superset images, initialization conventions, and installed drivers evolve. This is a local teaching topology, not a production deployment recipe. Verify the pinned image and current official Compose instructions. If the image lacks a PostgreSQL SQLAlchemy driver, build a derived image pinned to the same Superset release and install a compatible driver in that image. Confirm that the selected release honors `SUPERSET_CONFIG_PATH` and the startup command before relying on this example; version-specific official configuration takes precedence.

Create `superset_config.py` beside `compose.yaml`:

```python
import os
from sqlalchemy.engine import URL

SECRET_KEY = os.environ["SUPERSET_SECRET_KEY"]
SQLALCHEMY_DATABASE_URI = URL.create(
    "postgresql+psycopg2",
    username="superset_meta",
    password=os.environ["SUPERSET_META_PASSWORD"],
    host="superset-meta-db",
    port=5432,
    database="superset_meta",
)
```

Using `URL.create` avoids breaking the connection URI when a password contains reserved URL characters. The image must have a compatible PostgreSQL driver. For production, prefer the official Compose/configuration for that exact release and its supported metadata database setup.

### 9.2 Environment variables

Create a local `.env` file that is ignored by version control (for example, add `.env` to `.gitignore`) and restrict its file permissions. Generate each secret once for this lab, then keep it stable across restarts. In particular, changing Superset's `SECRET_KEY` without a planned migration can make previously encrypted metadata credentials unreadable. Example one-time initialization:

```bash
if [ ! -f .env ]; then
  umask 077
  cat > .env <<EOF
ANALYTICS_ADMIN_PASSWORD=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
SUPERSET_META_PASSWORD=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
SUPERSET_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(48))')
EOF
else
  echo '.env already exists; preserving its secrets.'
fi
grep -qxF '.env' .gitignore 2>/dev/null || printf '\n.env\n' >> .gitignore
chmod 600 .env
# Review the file locally; do not print it in shared logs or commit it.
docker compose config >/dev/null  # validate interpolation without printing rendered secrets
docker compose up -d
```

The PostgreSQL initialization password is used only when its data volume is first initialized; changing `.env` later does not rotate the database password inside an existing volume. Rotate it in PostgreSQL and update the secret together. After Superset starts, create the first administrator interactively so the password is not embedded in Compose or passed as a command-line argument:

```bash
docker compose exec superset superset fab create-admin \
  --username admin --firstname BI --lastname Admin \
  --email bi-admin@example.invalid
```

Enter the password at the prompt. If the pinned Superset release behaves differently, follow its official version-specific instructions. Do not use example strings as real credentials. For actual deployments, use a secret manager, rotate credentials with a plan, restrict network access, and avoid exposing PostgreSQL on a public interface. The host bindings above limit ports to loopback.

### 9.3 Create demo gold tables

Save as `sql/001_gold_demo.sql`. This SQL is PostgreSQL-specific. The initialization scripts run only when the database data directory is first initialized; if a volume already exists, rerun the SQL deliberately or recreate the local volume after preserving any data you need.

```sql
CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS gold.fct_orders (
  order_id       BIGINT PRIMARY KEY,
  user_id        BIGINT NOT NULL,
  created_at     TIMESTAMPTZ NOT NULL,
  region         TEXT NOT NULL,
  status         TEXT NOT NULL CHECK (status IN ('completed','cancelled','refunded')),
  net_amount     NUMERIC(12,2) NOT NULL CHECK (net_amount >= 0)
);

CREATE TABLE IF NOT EXISTS gold.fct_order_items (
  order_id       BIGINT NOT NULL REFERENCES gold.fct_orders(order_id),
  line_number    INTEGER NOT NULL,
  product_id     BIGINT NOT NULL,
  quantity       INTEGER NOT NULL CHECK (quantity > 0),
  net_line_amount NUMERIC(12,2) NOT NULL CHECK (net_line_amount >= 0),
  PRIMARY KEY (order_id, line_number)
);

CREATE TABLE IF NOT EXISTS gold.dim_product (
  product_id BIGINT PRIMARY KEY,
  product_name TEXT NOT NULL,
  category TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS gold.fct_user_activity_daily (
  activity_date DATE NOT NULL,
  user_id BIGINT NOT NULL,
  region TEXT NOT NULL,
  PRIMARY KEY (activity_date, user_id)
);

CREATE TABLE IF NOT EXISTS gold.metric_conversion_daily (
  metric_date DATE NOT NULL,
  region TEXT NOT NULL,
  eligible_users BIGINT NOT NULL CHECK (eligible_users >= 0),
  converted_users BIGINT NOT NULL CHECK (converted_users >= 0),
  CHECK (converted_users <= eligible_users),
  PRIMARY KEY (metric_date, region)
);

INSERT INTO gold.dim_product (product_id, product_name, category) VALUES
  (1, 'Trail Bottle', 'Accessories'),
  (2, 'Daypack', 'Bags'),
  (3, 'Rain Shell', 'Apparel')
ON CONFLICT (product_id) DO NOTHING;

INSERT INTO gold.fct_orders (order_id, user_id, created_at, region, status, net_amount) VALUES
  (1001, 501, '2025-01-02 10:00:00+00', 'north', 'completed', 80.00),
  (1002, 502, '2025-01-02 11:00:00+00', 'south', 'completed', 120.00),
  (1003, 501, '2025-01-03 12:00:00+00', 'north', 'completed', 45.00),
  (1004, 503, '2025-01-03 13:00:00+00', 'south', 'cancelled', 20.00)
ON CONFLICT (order_id) DO NOTHING;

INSERT INTO gold.fct_order_items (order_id, line_number, product_id, quantity, net_line_amount) VALUES
  (1001, 1, 1, 1, 30.00), (1001, 2, 2, 1, 50.00),
  (1002, 1, 2, 2, 120.00), (1003, 1, 3, 1, 45.00),
  (1004, 1, 1, 1, 20.00)
ON CONFLICT (order_id, line_number) DO NOTHING;

INSERT INTO gold.fct_user_activity_daily (activity_date, user_id, region) VALUES
  ('2025-01-02', 501, 'north'), ('2025-01-02', 502, 'south'),
  ('2025-01-03', 501, 'north'), ('2025-01-04', 503, 'south')
ON CONFLICT (activity_date, user_id) DO NOTHING;

INSERT INTO gold.metric_conversion_daily (metric_date, region, eligible_users, converted_users) VALUES
  ('2025-01-02', 'north', 100, 8), ('2025-01-02', 'south', 80, 10),
  ('2025-01-03', 'north', 110, 11), ('2025-01-03', 'south', 90, 9)
ON CONFLICT (metric_date, region) DO NOTHING;
```

### 9.4 Provision a read-only BI role

Create a separate role for the lab using a secure interactive process or secret manager. Example SQL for the object owner to run after setting a secure password out of band:

```sql
CREATE ROLE bi_reader LOGIN;
GRANT CONNECT ON DATABASE analytics TO bi_reader;
GRANT USAGE ON SCHEMA gold TO bi_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA gold TO bi_reader;
-- Execute for the role that will create future gold tables:
ALTER DEFAULT PRIVILEGES FOR ROLE lab_admin IN SCHEMA gold
  GRANT SELECT ON TABLES TO bi_reader;
```

If the SQL is executed via `psql`, provision the password with `\password bi_reader` interactively or another secure mechanism. Do not store the password in this lesson or a checked-in SQL file. Verify `bi_reader` cannot modify persistent approved tables and cannot read schemas other than `gold`. PostgreSQL databases often grant `TEMP` to `PUBLIC` by default, so a role may still be able to create session-local temporary tables; if your policy prohibits that, review and explicitly manage database-level `TEMP` privileges rather than assuming the three grants above remove them. Connect each BI tool to host `analytics-db` and port `5432` when running inside Compose; use `localhost:5432` only from the host machine.

### 9.5 Tool-specific startup guidance

- **Metabase:** open `http://localhost:3000`, complete initial setup, and add PostgreSQL. Use host `analytics-db`, database `analytics`, schema `gold`, and the `bi_reader` credentials. The lab uses the built-in Metabase application database for simplicity; production deployments should evaluate a supported external application database, backup strategy, upgrade path, and current official guidance.
- **Superset:** the Compose command runs `superset db upgrade`, `superset init`, and the web server. After the service is healthy, create the initial administrator with the interactive command above; do not hide admin-creation failures with `|| true`. Then add PostgreSQL as a database using the `bi_reader` account. Supply the connection URI through secure configuration or the UI's secret handling, not a committed export. Validate that the chosen image includes a compatible PostgreSQL driver and that the startup sequence matches the pinned release.
- **Both:** create a test viewer identity and a separate administrator. Do not use the database administrator account in the BI connection.

## 10. Dashboard implementation and comparison

Build the same dashboard question and metric contract in both tools. UI labels differ by version, so the following are implementation goals rather than exact click-by-click UI labels.

### Card 1 — Revenue

Definition for this lab: sum of `net_amount` for `completed` orders in the selected period, using UTC date boundaries. This is a demo metric, not a universal accounting definition.

```sql
SELECT
  (created_at AT TIME ZONE 'UTC')::date AS order_date,
  SUM(net_amount) AS net_revenue
FROM gold.fct_orders
WHERE status = 'completed'
  AND created_at >= :start_ts
  AND created_at <  :end_ts
GROUP BY 1
ORDER BY 1;
```

The `:start_ts`/`:end_ts` syntax is conceptual parameter notation; bind parameters using the actual BI tool's supported filter mechanism. Use a half-open interval to avoid double-counting boundary timestamps.

### Card 2 — Conversion

Definition: converted eligible users divided by eligible users for the same date and segment. Do not average daily conversion percentages unless the intended metric is the unweighted mean of daily rates. For an overall rate, sum numerators and denominators first.

```sql
SELECT
  metric_date,
  SUM(converted_users)::numeric / NULLIF(SUM(eligible_users), 0) AS conversion_rate
FROM gold.metric_conversion_daily
WHERE metric_date >= :start_date AND metric_date < :end_date
GROUP BY metric_date
ORDER BY metric_date;
```

### Card 3 — Retention heatmap

The demo activity table is deliberately small and is not a mature cohort data set. For this lab, define a cohort as the week of a user's **first observed activity** and retention as at least one active day in each subsequent calendar week. This is not signup retention unless first activity is known to equal signup. The cohort denominator is fixed at cohort entry.

```sql
WITH first_activity AS (
  SELECT user_id, MIN(activity_date) AS first_active_date
  FROM gold.fct_user_activity_daily
  GROUP BY user_id
), cohorts AS (
  SELECT user_id,
         DATE_TRUNC('week', first_active_date::timestamp)::date AS cohort_week
  FROM first_activity
), active_weeks AS (
  SELECT DISTINCT user_id,
         DATE_TRUNC('week', activity_date::timestamp)::date AS activity_week
  FROM gold.fct_user_activity_daily
), cohort_sizes AS (
  SELECT cohort_week, COUNT(*) AS cohort_users
  FROM cohorts
  GROUP BY cohort_week
), retained AS (
  SELECT c.cohort_week,
         ((a.activity_week - c.cohort_week) / 7)::integer AS cohort_age_week,
         COUNT(DISTINCT c.user_id) AS active_users
  FROM cohorts c
  JOIN active_weeks a USING (user_id)
  WHERE a.activity_week >= c.cohort_week
  GROUP BY 1, 2
)
SELECT r.cohort_week, r.cohort_age_week, s.cohort_users,
       r.active_users,
       r.active_users::numeric / NULLIF(s.cohort_users, 0) AS retention_rate
FROM retained r
JOIN cohort_sizes s USING (cohort_week)
ORDER BY r.cohort_week, r.cohort_age_week;
```

The query returns only observed cohort-age cells. To render a complete triangle, generate the expected cohort-age grid and left-join observed counts; leave future/immature cells `NULL`, not zero. For large datasets, precompute the cohort activity grain and test the denominator against a small hand-worked cohort.

### Card 4 — Top products

Definition: top products by completed-order net line amount during the selected period. Aggregate at product grain after joining line items to the unique product dimension. Because this uses line amounts rather than order header totals, do not sum order totals across order-item rows.

```sql
SELECT
  p.product_name,
  SUM(i.net_line_amount) AS product_revenue
FROM gold.fct_order_items AS i
JOIN gold.fct_orders AS o USING (order_id)
JOIN gold.dim_product AS p USING (product_id)
WHERE o.status = 'completed'
  AND o.created_at >= :start_ts
  AND o.created_at <  :end_ts
GROUP BY p.product_id, p.product_name
ORDER BY product_revenue DESC
LIMIT 10;
```

This assumes the order-line net amount reconciles to the chosen revenue metric. If discounts/refunds are handled elsewhere, document the discrepancy and use a consistent gold model.

### Comparison worksheet

For each tool, record:

- Time to connect and validate the read-only source.
- Time to create the four cards and one shared date filter.
- Whether the tool can reuse the canonical metric without duplicating logic.
- Filter behavior, drill-down, export, accessibility, and mobile layout.
- Query history and explain-plan workflow.
- Permissions required to share content with a viewer.
- Ease of export/restore in a fresh instance.
- Admin and maintenance effort, including upgrade/backup burden.

Do not infer universal superiority from one short lab. Results depend on the author's familiarity, exact version/edition, database, and metric complexity.

## 11. Access control and security validation

### Regional restrictions

Suppose users may only see rows where `region` matches their authorized region. The exact setup depends on the tool and edition. Use one of these tested patterns:

1. Database-enforced security views or row-level policies keyed by a trusted database identity.
2. BI-supported RLS with a trusted, non-user-editable identity-to-region mapping.
3. Separate schemas/credentials for hard isolation where required.

Do not rely only on a dashboard filter. If all BI users share one database service account, database policies based on `current_user` see the service identity, not necessarily the interactive BI viewer. The BI tool must enforce the mapping correctly or propagate a trusted identity through a supported mechanism.

### Example security-view pattern

For a simple lab with one role per region, a view can provide a testable boundary. This is not a scalable identity system by itself.

```sql
CREATE ROLE bi_north_reader LOGIN;
CREATE SCHEMA IF NOT EXISTS bi_north;
CREATE VIEW bi_north.orders AS
SELECT order_id, created_at, net_amount, region
FROM gold.fct_orders
WHERE region = 'north';

REVOKE ALL ON SCHEMA gold FROM bi_north_reader;
GRANT USAGE ON SCHEMA bi_north TO bi_north_reader;
GRANT SELECT ON bi_north.orders TO bi_north_reader;
```

Use a separate role `bi_north_reader` with no inherited membership in a broad reader role. Confirm it cannot query `gold.fct_orders` directly and can query only the intended view. The view predicate is fixed to `north`; do not replace it with a client-supplied parameter. Test the view as the actual login role and verify that the view owner and grants behave as expected in your PostgreSQL version. For production, dynamic policies must map identity to authorized scope using trusted server-side context; a static view is just a demonstration.

### Required tests

Use two non-admin test identities, one authorized for `north` and one for `south`:

- **Permitted test:** north viewer can see expected north rows and expected aggregates.
- **Denied test:** north viewer cannot retrieve south rows through the dashboard, SQL editor, download/export, drill-through, saved question, or alternate dataset.
- **Filter tampering:** removing/changing the region filter must not expose unauthorized rows.
- **Cache isolation:** run as north, then south; confirm the cached response cannot cross identities.
- **Default deny:** an identity with no region mapping sees no protected rows or receives an explicit authorization error.
- **Admin separation:** a BI administrator's content privileges must not accidentally grant database write access.

Record identity, request path, expected outcome, actual outcome, timestamp, and evidence. A successful test of a dashboard filter is not sufficient evidence of RLS.

### Collections, workspaces, and certification

Use separate spaces/collections/projects for development, shared analysis, and certified production content. Restrict who can publish/overwrite certified dashboards. Display owner, definition link, freshness, and certification state. Certification is a governance label and review process—not proof of correctness unless backed by tests and ownership.

### Embedding and multi-tenancy

For embedded dashboards, treat each request as a security boundary. Validate signed token claims server-side, enforce tenant context in the query/model path, scope caches to tenant and permission context, and test exports/drill-downs. Do not put database credentials or long-lived secrets in browser code. A tenant filter parameter is a convenience, not authorization. Metabase public embedding intentionally exposes content to anyone with the link; guest/static embeds do not provide the same signed-in user context as authenticated embedding, and locked parameters alone must not be treated as a general replacement for row/column security. Check current plan restrictions and the exact embed mode before using customer data.

## 12. Deployment, operations, and cost

### Development → test → production

A robust promotion path is:

1. Develop metric models and dashboard configuration in development.
2. Test SQL, expected totals, permission matrices, filter defaults, and freshness in test.
3. Export/version the supported configuration artifacts and review diffs.
4. Promote through a documented deployment mechanism; use environment-specific connection references and secrets.
5. Smoke-test production dashboards with viewer and restricted identities.
6. Roll back by restoring a known configuration/version and, where required, database model version.

Do not commit production secrets, user tokens, or sensitive query results in exports. Export files may contain SQL, metadata, chart definitions, or connection references; inspect them before version control.

### Version-control and deployment patterns

- **Superset:** supports import/export workflows for dashboards and related assets; command names, formats, dependency handling, and compatibility vary by release. Use the export/import mechanism documented for the pinned version, export required datasets/charts/databases as appropriate, and test restoration into a clean instance.
- **Metabase:** the current serialization CLI/API workflow is available on Pro and Enterprise plans; do not imply it is a universal Community Edition feature. It exports supported content/configuration, not every user, group, permission, alert, subscription, credential, or environment setting. If your edition lacks serialization, treat a full application-database backup/restore as disaster recovery—not as a portable, reviewable dashboard-as-code workflow—and choose an edition or supported alternative that satisfies the lab's version-control requirement. Test a fresh-instance restore with the exact version and edition. See the official serialization documentation in Section 18.
- **Tableau:** packaged workbooks, data sources, projects, Tableau Server/Cloud publishing, and supported deployment tooling can be used; credentials and connection configuration need environment-specific handling.
- **Power BI:** deployment pipelines and workspace promotion are available in supported service/capacity contexts; PBIP/Git workflows and feature availability depend on current tooling and tenant configuration. Validate refresh credentials, gateways, RLS, and model bindings after promotion.

Keep transformation code (for example, dbt) versioned independently from dashboard layout, but tie both to the same release/change ticket when metric definitions change.

### Capacity and total cost

Evaluate total cost, not only license price:

- BI seats, viewer/creator/admin roles, embedding terms, support contracts.
- Warehouse/query-engine compute, scanned bytes, concurrency, and reserved capacity.
- Extract storage, refresh frequency, and refresh-window collisions.
- BI application infrastructure, metadata database, monitoring, backups, and upgrades.
- Engineering/administrator time, onboarding, incident response, and migration risk.
- Power BI Premium/Fabric capacity concepts and Tableau Server capacity concepts: model refresh, concurrent users, memory/CPU, workload peaks, and service limits matter. Exact packaging and licensing change; consult current vendor documentation rather than relying on static price claims.

A cache can lower repeated query cost but may increase staleness; an extract can reduce interactive load but create refresh load. Model both workloads.

### Usage analytics and dashboard retirement

Collect views/queries, last-used time, audience, owner, freshness incidents, duplicate purpose, and business criticality where the platform exposes these signals. Do not retire a dashboard solely because it has few views: it may support month-end, compliance, or incident response.

Suggested retirement process:

1. Identify candidates: no owner, stale definitions, low use, duplicated content, or broken refresh.
2. Contact owner and audience; document downstream links and subscriptions.
3. Mark “deprecated” and announce a transition window.
4. Migrate users to the certified replacement; preserve necessary audit evidence.
5. Archive/export configuration, then remove access/content under a change ticket.
6. Recheck usage and support tickets after retirement.

## 13. Hands-on lab and troubleshooting

### Lab acceptance checklist

- [ ] Metabase and Superset connect to the same analytics database using `bi_reader`.
- [ ] BI role can `SELECT` approved gold objects but cannot write or read unapproved schemas.
- [ ] Both dashboards use the same metric definitions and filter boundaries.
- [ ] Revenue, conversion, retention heatmap, and top products are present.
- [ ] The three slowest cards are recorded with SQL and execution evidence.
- [ ] At least one slow card is improved with a validated pre-aggregation or safe cache configuration.
- [ ] Regional restrictions pass permitted, denied, filter-tampering, and cache-isolation tests.
- [ ] Dashboard configuration is exported and restored into a fresh lab instance using the supported version-specific workflow.
- [ ] Usage review identifies retirement candidates and records stakeholder/criticality checks.
- [ ] Cleanup is completed.

### Find the three slowest cards

Use each product's query history/logging or the database's query statistics. Record card ID/name, SQL, parameter values, duration, scanned rows/bytes if available, cache hit/miss, and result size. For PostgreSQL, inspect `pg_stat_statements` if installed and authorized; otherwise use `EXPLAIN (ANALYZE, BUFFERS)` carefully in a non-production setting. For warehouses, use their query history/profile interfaces.

Do not label the top three from a single warm-cache run as the platform's definitive slowest cards. Repeat under representative filters and load.

### Diagnose common issues

| Symptom | Likely causes | Checks and remediation |
|---|---|---|
| Dashboard total differs from finance report | Metric definition mismatch, status/refund policy, time zone, join fanout | Compare canonical order IDs, reconcile at order grain, inspect filter interval and currency |
| Revenue inflated after adding product | Header total joined to line items | Aggregate line metrics or retain order grain; test uniqueness and reconciliation |
| Data appears stale | Cache TTL, extract refresh failure, late events, materialized view not refreshed | Inspect freshness timestamp, refresh logs, cache policy, source watermark |
| Query is slow | Large scan, poor pruning, expensive joins, concurrency, spill, too many cards | Inspect SQL/plan, aggregate first, precompute common grains, reduce default date range |
| User sees another region | UI-only filter, incorrect RLS mapping, broad database grants, shared cache | Treat as security incident; revoke access, inspect logs, test all query/export paths |
| One user can see a dashboard but another cannot | Content permission, database permission, role mapping, collection/workspace inheritance | Test each layer independently; avoid broad admin grants as a workaround |
| Restore fails | Missing dependencies, incompatible version, secret/environment references, omitted datasets | Pin versions, export dependent assets, restore into clean test instance, inspect logs |
| Scheduled email is missing | Scheduler configuration, permissions, SMTP/provider settings, query failure | Check scheduler/job logs, recipient authorization, and delivery configuration |

### Cleanup

After saving any required export and evidence, stop the local stack:

```bash
docker compose down
```

To remove all lab data permanently, after verifying that no wanted data remains:

```bash
docker compose down -v
```

The second command deletes named volumes, including local database and BI metadata. Do not run it against a shared or production environment. Remove ignored secret files securely and rotate any secret that may have been exposed.

## 14. Exercises with solutions

### Exercise 1 — Choose a tool

A five-person analytics team has SQL skills, limited operations capacity, a BigQuery warehouse, and a requirement for central metric definitions. Recommend a shortlist and identify unknowns.

**Solution outline:** Compare Metabase for low-friction exploration, Superset if the team can operate its stack and values open-source flexibility, and Looker/Power BI/Tableau where governance, ecosystem, licensing, and user experience justify the cost. BigQuery compatibility alone does not decide the choice. Validate semantic-layer integration, identity/SSO, embedding, content permissions, and total cost with a proof of concept. A recommendation should state assumptions and trade-offs rather than declare a universal winner.

### Exercise 2 — Find the fanout bug

Why can this query overstate revenue?

```sql
SELECT SUM(o.net_amount)
FROM gold.fct_orders o
JOIN gold.fct_order_items i USING (order_id)
WHERE o.status = 'completed';
```

**Solution:** Each order total is repeated for every item line. Sum the order header at order grain without joining lines, or aggregate line amounts to the desired order/product grain and use the line-based metric. Add a reconciliation test between order totals and line totals where the business definition expects equality.

### Exercise 3 — Define conversion

You have 100 eligible users and 12 converters. Daily conversion rates are 12% for this group and 30% for a second group with 10 eligible users and 3 converters. Is overall conversion 21%?

**Solution:** No. The unweighted mean is 21%, but overall conversion is `(12 + 3) / (100 + 10) = 13.64%`. State whether the metric is weighted by eligible users; generally aggregate numerator and denominator before division.

### Exercise 4 — Diagnose a slow card

A card takes 18 seconds with a date filter but 2 seconds without it. What should you inspect first?

**Solution outline:** Capture generated SQL and parameter types; inspect partition/index pruning and plan estimates versus actual rows; check whether the date predicate wraps the timestamp column in a function; check join cardinality and result volume; compare cold/warm cache and warehouse load. If the same date-range aggregation is repeatedly requested, consider a tested daily aggregate. Validate output equality and freshness after optimization.

### Exercise 5 — Test regional RLS

A north-region user sees only north rows when the dashboard filter is set to north. What test is still missing?

**Solution:** Remove/change the filter, use direct SQL or another dataset, download/export, drill-through, and switch identity to ensure south rows remain inaccessible. Test no mapping, cache isolation, and the underlying database grants. A filter-only result does not prove RLS.

### Exercise 6 — Restore a dashboard

A dashboard export imports, but cards fail in the new instance. List plausible reasons.

**Solution:** Missing datasets or database definitions, changed schema names, unsupported export format/version, credentials not provisioned, absent plugins/drivers, mismatched permissions, or environment-specific SQL. Test the full dependency graph in a clean instance and inject secrets/connection references separately.

### Exercise 7 — Retire a dashboard

A dashboard has had no views in 90 days. Should it be deleted?

**Solution:** Not automatically. Check owner, business-criticality, scheduled subscriptions, compliance/audit requirements, incident usage, and replacement coverage. Deprecate with notice, archive configuration, and remove only after stakeholder sign-off.

## 15. Common mistakes and production failure modes

- Dashboard cards independently define revenue, conversion, or retention.
- Raw event tables are exposed without stable grain, deduplication, or business semantics.
- Order-level amounts are summed after joining to order lines.
- Conversion percentages are averaged when a weighted ratio is required.
- A filter is treated as a security boundary.
- Database owner credentials are stored in BI connection settings.
- A shared cache is not scoped to the viewer/tenant's permission context.
- A materialized view or extract is optimized without a freshness contract.
- Live queries overload a warehouse during peak dashboard concurrency.
- A “fast” result comes from a warm cache and is presented as a general benchmark.
- Dashboard exports include sensitive metadata or environment-specific credentials.
- A successful import is assumed to prove full restoration and permission correctness.
- Certifications have no owner, test suite, or review cadence.
- Dashboards are never retired, leading to contradictory definitions and poor discovery.
- A vendor feature is assumed to exist in every edition or release.
- Multi-tenant embedding trusts client-supplied tenant parameters.

## 16. Knowledge checkpoint

You should be able to answer these without looking back:

1. Why should dashboards usually query gold models rather than raw events?
2. What is the difference between authentication, authorization, database grants, and RLS?
3. Why is a dashboard filter not a security control?
4. Where should a shared revenue definition live, and why?
5. How do live queries, extracts, and caches differ in freshness and workload?
6. How can a join inflate a metric while returning plausible-looking charts?
7. What evidence is needed to claim that a slow card has been optimized?
8. How do you verify a regional restriction against query, export, drill-down, and cache paths?
9. What belongs in a BI deployment/restore test?
10. How do you retire an unused dashboard without breaking a critical workflow?

## 17. Final competency checklist

- [ ] I can explain the role and limits of BI tools in an analytical platform.
- [ ] I can justify a tool choice using team skills, governance, ecosystem, cost, and operations.
- [ ] I expose curated gold models with least-privilege database identities.
- [ ] I define metric grain, numerator/denominator, time zone, status rules, and owner.
- [ ] I can design a dashboard around one principal decision and choose suitable charts.
- [ ] I can identify join fanout and validate dashboard metrics against canonical models.
- [ ] I can investigate slow cards using query logs and query plans/profiles.
- [ ] I can choose among pre-aggregation, live queries, extracts, and caching with explicit freshness trade-offs.
- [ ] I can test RLS and tenant isolation through more than a visible filter.
- [ ] I can describe versioned export/restore and dev/test/prod promotion for the selected product.
- [ ] I can account for license, compute, capacity, refresh, and operations costs.
- [ ] I can use usage evidence and stakeholder validation to propose dashboard retirement.

## 18. Authoritative documentation references

Consult current documentation for the exact version and edition deployed. Product-specific details, commands, capabilities, and licensing may change.

- Metabase documentation: <https://www.metabase.com/docs/latest/>
- Metabase serialization (edition restrictions and export coverage): <https://www.metabase.com/docs/latest/installation-and-operation/serialization>
- Metabase data isolation methods and plan restrictions: <https://www.metabase.com/docs/latest/permissions/data-isolation-methods>
- Metabase embedding security modes: <https://www.metabase.com/docs/latest/embedding/securing-embeds>
- Apache Superset documentation: <https://superset.apache.org/docs/>
- Apache Superset Docker installation: <https://superset.apache.org/docs/installation/docker-compose/>
- Apache Superset security and roles: <https://superset.apache.org/docs/security/>
- Apache Superset import/export: <https://superset.apache.org/docs/configuration/importing-exporting-datasources/>
- Tableau help and deployment documentation: <https://help.tableau.com/>
- Tableau Server administration: <https://help.tableau.com/current/server/en-us/admin.htm>
- Microsoft Power BI documentation: <https://learn.microsoft.com/power-bi/>
- Power BI deployment pipelines: <https://learn.microsoft.com/power-bi/create-reports/deployment-pipelines-overview>
- Microsoft Fabric documentation: <https://learn.microsoft.com/fabric/>
- Looker documentation and LookML: <https://cloud.google.com/looker/docs>
- dbt Semantic Layer documentation: <https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl>
- PostgreSQL privileges: <https://www.postgresql.org/docs/current/ddl-priv.html>
- PostgreSQL `EXPLAIN`: <https://www.postgresql.org/docs/current/using-explain.html>

---

**Completion standard:** A dashboard is production-ready only when its metric contract, data grain, freshness, query cost, access model, owner, and operational lifecycle are explicit and tested—not merely when the charts render.
