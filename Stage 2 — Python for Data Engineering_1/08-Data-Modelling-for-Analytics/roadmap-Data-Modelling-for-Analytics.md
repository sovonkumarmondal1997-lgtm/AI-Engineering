# Roadmap — Module 2.8: Data Modelling for Analytics

This is the learning roadmap for the eighth module of Stage 2, **Python for
Data Engineering**. It tells you **what** to learn about data modelling,
**in what order**, **how** to learn each topic, and **how to prove to
yourself** that you have learned it before you move on.

Tools change every few years; data models last for a decade. A good model
makes every dashboard, metric, ML feature, and ad-hoc question easy and
correct. A bad model makes every query a puzzle, every metric a debate, and
every new source a rewrite. Data modelling is where a data engineer stops
being "the person who moves data" and becomes "the person who designs how
the business sees itself in data". It is also a guaranteed part of senior
data engineering interviews ("design the data model for a ride-sharing
app").

By now you can store data efficiently (Module 2.5), query it correctly
(Module 2.6), and move it between systems (Module 2.7). This module is
about **what shape the data should have** once it arrives.

---

## 1. Module outcome

By the end of this module you will be able to:

- Normalise an operational schema to third normal form and explain when and
  why analytics **denormalises** it again.
- Design **dimensional models** with the Kimball process: business
  process, grain, dimensions, facts.
- Choose between **transaction, periodic snapshot, accumulating snapshot,
  and factless** fact tables, and classify measures as additive,
  semi-additive, or non-additive.
- Design **star** and **snowflake** schemas and choose between them for a
  given engine and team.
- Write a precise **grain statement** for every table and choose between
  natural, surrogate, and durable keys.
- Choose the right **slowly changing dimension type** per attribute (Types
  0, 1, 2, 3, 4, 6) and design for late-arriving data.
- Model a raw integration layer with **Data Vault** (hubs, links,
  satellites) and explain when it is worth the cost.
- Design **one big table (OBT)** and wide denormalised models for BI and
  ML, and know their trade-offs.
- Model **event and clickstream data**: event schemas, sessions, identity
  stitching, funnels, and retention.
- Document a model so that others can use it without asking you.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.7. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| State modelling, decomposition | Stage 1 — Module 1.1 | Modelling is decomposition of a business into entities and events |
| Dataclasses and data models | Stage 1 — Module 1.8 | The same thinking at table scale |
| OLTP vs OLAP, medallion layers | Stage 2 — Module 2.1 | Normalised models serve OLTP; dimensional models serve gold layers |
| Join cardinality, grain in pandas | Stage 2 — Module 2.3 | Grain and cardinality are the core of modelling |
| Nested data, flatten and explode | Stage 2 — Module 2.5 | Event properties and wide models |
| Joins, fan traps, window functions, constraints, **SCD Type 1 and 2 implementation in SQL** | Stage 2 — Module 2.6 | SQL mechanics are **not** re-taught; this module decides *what* to build |
| Loading from Python, metadata tables | Stage 2 — Module 2.7 | Loading models you design here |

**Tools needed:**

- **DuckDB** (main engine for exercises — fast, local, and supports every
  pattern here); PostgreSQL optional.
- Python (from earlier modules) to **generate** realistic source data with
  history, duplicates, and late arrivals.
- A diagramming tool: pen and paper, Mermaid `erDiagram` in Markdown,
  dbdiagram.io, or Excalidraw.
- A spreadsheet or Markdown table for the **bus matrix** and data
  dictionary.

---

## 3. How the module is organised

The eight topics are grouped into five phases. Work through them **in
order**.

```text
Phase A — Modelling Foundations                 (Basics)
  01 Normalization and denormalization

Phase B — The Dimensional Core                  (Basics → Intermediate)
  02 Dimensional modelling: facts and dimensions
  03 Star and snowflake schemas
  04 Grain, natural keys, and surrogate keys

Phase C — Modelling Change Over Time            (Intermediate → Advanced)
  05 Slowly changing dimension types

Phase D — Alternative Modelling Paradigms       (Advanced)
  06 Data Vault: hubs, links, and satellites
  07 One big table and wide denormalized models

Phase E — Modelling Behavioural Data            (Advanced)
  08 Modelling event and clickstream data

Consolidate
  practice-questions.md
  interview-practice.md
  Module mini-project: an end-to-end model for an online marketplace
```

The dependency chain:

```text
01 ──► 02 ──► 03 ──► 04 ──► 05 ──► 06 ──► 07 ──► 08
source  facts &  arrange keys &  history  integrate  flatten   model
shapes  dims     them    grain   over     many       for       behaviour
                                 time     sources    consumers
```

Why this order:

- You must understand normalised source systems (01) before you can
  reshape them for analytics.
- Facts and dimensions (02) come before schema shapes (03); grain and keys
  (04) formalise what 02–03 used informally.
- SCD types (05) need keys and grain — every SCD decision is a key
  decision.
- Data Vault (06) and OBT (07) are best understood as **contrasts** with
  the dimensional model: one sits before it (integration), one after it
  (consumption).
- Event data (08) combines everything: grain, keys, identity, history, and
  wide models.

---

## 4. Suggested schedule

About **4 weeks at 8–10 hours per week**. Modelling is learned by
designing; expect to spend more time drawing and discussing than coding.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — normalization · Topic 02 — facts and dimensions |
| 2 | Topic 03 — star and snowflake · Topic 04 — grain and keys · Topic 05 — SCD types |
| 3 | Topic 06 — Data Vault · Topic 07 — OBT and wide models |
| 4 | Topic 08 — event data · practice questions · interview practice · mini-project |

---

## 5. How to study every topic (the modelling loop)

```text
Understand the business → List the questions → Identify processes & entities
→ Declare the grain → Draw the model → Build it on sample data
→ Answer the questions with SQL → Stress it with change → Document
→ Explain it to a non-engineer
```

1. **Understand the business**: write a paragraph on how the business
   makes money and what happens, step by step, in the process you model.
2. **List the questions** consumers will ask (at least ten real
   questions, e.g. "revenue by product category by week, as the category
   was at the time of sale").
3. **Identify processes and entities**: business processes become facts;
   the nouns that describe them become dimensions.
4. **Declare the grain** of every table in one sentence before adding a
   single column.
5. **Draw the model** as an ER diagram with keys and cardinalities.
6. **Build it** in DuckDB with generated data.
7. **Answer the questions** with SQL. If a question is hard to answer, the
   model — not the SQL — is usually wrong.
8. **Stress it with change**: a customer moves, a product changes
   category, a new source system arrives, an order is cancelled, data
   arrives late.
9. **Document** it: grain, keys, column definitions, SCD policy, and known
   limitations.
10. **Explain it** to someone non-technical. If they cannot follow the
    story of the model, simplify it.

Keep one `modelling_lab/` project:

```text
modelling_lab/
├── generators/      # Python scripts producing source data
├── models/<topic>/  # DDL + load SQL per topic
├── diagrams/        # Mermaid / image ER diagrams
├── docs/            # grain statements, bus matrix, data dictionary
└── tests/           # assertion queries (return zero rows when correct)
```

---

## 6. Phase A — Modelling Foundations (Basics)

### Topic 01 — [Normalization and denormalization](01-normalization-and-denormalization.md)

**Why it comes first:** Almost every source you ingest is a normalised
operational database. You must be able to read it, reason about it, and
explain why analytics reshapes it.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Levels of modelling: **conceptual** (business entities), **logical** (tables, keys, relationships), **physical** (types, indexes, partitions, engine specifics) |
| Basics | Entities, attributes, relationships, and cardinality (1:1, 1:N, N:M); ER diagrams and crow's-foot notation |
| Basics | Update, insert, and delete **anomalies** — the problems normalisation solves |
| Intermediate | **Functional dependencies** and the normal forms: 1NF (atomic values, no repeating groups), 2NF (no partial dependency on a composite key), 3NF (no transitive dependency), BCNF |
| Intermediate | Resolving many-to-many relationships with associative (bridge) tables |
| Intermediate | Why OLTP systems normalise: write efficiency, consistency, one place to update each fact |
| Intermediate | **Denormalisation** for analytics: fewer joins, simpler queries, faster scans in columnar engines — at the cost of redundancy and update complexity |
| Advanced | Where each shape lives in a platform: normalised sources → (integration layer) → dimensional marts → wide consumption tables (connecting to medallion layers in Module 2.1) |
| Advanced | Reading an unfamiliar source schema quickly: finding keys, relationships, soft deletes, audit columns, and status columns from metadata and data profiling |
| Advanced | Normalisation in semi-structured sources: JSON documents that embed repeated groups (Module 2.5) |

**How to learn it**

1. Read the topic file.
2. Take one unnormalised spreadsheet (e.g. orders with customer and
   product details repeated on every row) and normalise it step by step to
   3NF, writing the functional dependency behind each split.
3. Demonstrate each anomaly on the unnormalised version.

**Hands-on exercise — `models/01/`**

1. Normalise a flat `sales.csv` (one row per order line with customer,
   address, product, category, and store details repeated) into 3NF
   tables in DuckDB; draw the ER diagram.
2. Show one update anomaly in the flat file and prove it is impossible in
   the 3NF model.
3. Write five business questions and answer them on the 3NF model; count
   joins per query.
4. Build a denormalised version and answer the same questions; compare
   query complexity and scan time.
5. Reverse-engineer a provided OLTP schema (from Module 2.6 or 2.7): list
   entities, keys, relationships, and soft-delete and audit columns.

**Checkpoint — you are ready to move on when you can:**

- [ ] Explain conceptual vs logical vs physical models.
- [ ] Normalise a table to 3NF and justify every split.
- [ ] Explain update, insert, and delete anomalies.
- [ ] Explain why analytics denormalises and what it costs.

**Common mistakes:** confusing "normalised" with "good" (and
"denormalised" with "bad"); skipping the conceptual model; ignoring soft
deletes and status columns in source systems.

---

## 7. Phase B — The Dimensional Core (Basics → Intermediate)

### Topic 02 — [Dimensional modelling: facts and dimensions](02-dimensional-modelling-facts-and-dimensions.md)

**Why here:** Dimensional modelling (Kimball) is the most widely used
approach for analytics and BI. Its vocabulary — facts, dimensions, grain,
conformed dimensions — is used everywhere, including dbt projects and
semantic layers.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Facts** (measurements of a business process: amounts, quantities, durations) and **dimensions** (the context: who, what, where, when, how) |
| Basics | The **four-step design process**: (1) select the business process, (2) declare the grain, (3) identify the dimensions, (4) identify the facts |
| Basics | The **date dimension**: why a table of calendar attributes (fiscal periods, holidays, weekdays) beats computing them in every query |
| Intermediate | **Fact table types**: transaction, periodic snapshot (e.g. daily account balance), accumulating snapshot (e.g. order lifecycle with milestone dates), and factless fact tables (events or coverage with no measures) |
| Intermediate | **Measure additivity**: additive (sum over any dimension), semi-additive (balances: not summable over time), non-additive (ratios, percentages — store numerator and denominator instead) |
| Intermediate | Dimension design: descriptive, text-rich attributes; flattened hierarchies (product → category → department); readable labels instead of codes |
| Intermediate | **Conformed dimensions** and the **enterprise bus matrix** (business processes × dimensions) for integrating many fact tables |
| Advanced | Special dimensions: **degenerate** (an order number stored in the fact table), **junk** (grouping low-cardinality flags), **role-playing** (one date dimension used as order date, ship date, delivery date), **audit** dimensions (load metadata) |
| Advanced | Special cases: the "unknown" / "not applicable" member rows (so facts never have NULL foreign keys), **late-arriving facts**, and **late-arriving dimensions** (inferred members created before the dimension row arrives) |
| Advanced | **Bridge tables** for many-to-many relationships between facts and dimensions (e.g. a patient with several diagnoses) and weighting factors |
| Advanced | Consolidated and aggregate fact tables for performance, and why they must reconcile with the atomic facts |

**How to learn it**

1. Read the topic file.
2. For three businesses (e-commerce, bank, hospital), list five business
   processes each and classify each one's fact table type.
3. Build a bus matrix for one of them.

**Hands-on exercise — `models/02/`**

For an online retailer:

1. Run the four-step process for **order lines**, **daily inventory**, and
   **order fulfilment**; write the grain, dimensions, and facts for each.
2. Build `fct_order_lines` (transaction), `fct_inventory_daily` (periodic
   snapshot), and `fct_order_fulfilment` (accumulating snapshot with
   ordered/paid/shipped/delivered dates) in DuckDB with generated data.
3. Build `dim_date` (with fiscal year and holidays), `dim_product`,
   `dim_customer`, and `dim_store`, including unknown-member rows.
4. Use `dim_date` in three roles (order, ship, delivery) with views.
5. Show why summing inventory balances across days is wrong and compute
   the correct month-end balance.
6. Create a bus matrix for the retailer with at least six processes.

**Checkpoint:**

- [ ] Apply the four-step dimensional design process.
- [ ] Choose between the four fact table types.
- [ ] Classify measures as additive, semi-additive, or non-additive.
- [ ] Explain conformed dimensions and the bus matrix.
- [ ] Explain degenerate, junk, role-playing, and bridge constructs.

**Common mistakes:** storing ratios as facts; NULL foreign keys in facts;
dimensions full of cryptic codes; one giant fact table mixing several
business processes.

---

### Topic 03 — [Star and snowflake schemas](03-star-and-snowflake-schemas.md)

**Why here:** Facts and dimensions can be arranged in different shapes.
The shape affects query simplicity, performance, and how BI tools see the
data.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Star schema**: one fact table joined directly to denormalised dimension tables |
| Basics | **Snowflake schema**: dimensions normalised into sub-dimension tables (product → category → department) |
| Basics | Typical star queries: filter on dimension attributes, group by dimension attributes, aggregate facts |
| Intermediate | Trade-offs: star (simple SQL, fewer joins, BI-friendly, some redundancy) vs snowflake (less redundancy, more joins, harder for users) |
| Intermediate | **Outriggers**: a limited, deliberate snowflake (e.g. a date attached to a customer dimension) |
| Intermediate | **Galaxy / fact constellation**: several fact tables sharing conformed dimensions; drilling across facts at a common grain |
| Intermediate | Why columnar engines and cloud warehouses favour star schemas (cheap redundancy through compression, efficient joins of large facts to small dimensions) |
| Advanced | How engines optimise star joins (dimension filters pushed into fact scans, broadcast joins in Spark — Module 2.14) |
| Advanced | BI and semantic-layer compatibility: why most tools expect stars (semantic layers in Module 2.22) |
| Advanced | Physical design of a star: partitioning and sorting the fact table by date, clustering by frequently filtered keys (Module 2.5 and 2.15) |

**How to learn it**

1. Read the topic file.
2. Build the same model as a star and as a snowflake; write ten business
   queries against each.
3. Count joins and measure query time on 50 million fact rows in DuckDB.

**Hands-on exercise — `models/03/`**

1. Extend your Topic 02 model into a snowflake (product → subcategory →
   category → department; store → city → region → country).
2. Write the same ten queries on the star and on the snowflake; compare
   lines of SQL, joins, and runtimes.
3. Add a second fact table (`fct_returns`) sharing conformed dimensions,
   and write a drill-across query comparing sales and returns by month and
   category.
4. Write a short recommendation: star or snowflake for this retailer, and
   where an outrigger is justified.

**Checkpoint:**

- [ ] Draw a star and a snowflake for the same process.
- [ ] Explain the trade-offs between them.
- [ ] Write a correct drill-across query between two fact tables.
- [ ] Explain why cloud warehouses favour star schemas.

**Common mistakes:** snowflaking by habit from OLTP design; joining two
fact tables directly (fan trap from Module 2.6) instead of drilling across
at a common grain.

---

### Topic 04 — [Grain, natural keys, and surrogate keys](04-grain-natural-keys-and-surrogate-keys.md)

**Why here:** You have used grain and keys informally. This topic makes
them rigorous — because almost every modelling bug is a grain bug or a key
bug.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Grain**: exactly what one row represents, written as a sentence ("one row per order line per order"); atomic (lowest) grain vs aggregated grain |
| Basics | **Natural (business) keys**: identifiers from source systems (order number, email, SKU) |
| Basics | **Surrogate keys**: warehouse-generated keys with no business meaning |
| Intermediate | Why the lowest possible grain is usually best: it answers the most questions and can always be aggregated later |
| Intermediate | **Mixed grain** in one table (e.g. order headers and order lines together) and why it breaks sums |
| Intermediate | Why surrogate keys: independence from source changes, integrating several sources, SCD Type 2 versions, unknown members, and smaller join keys |
| Intermediate | Kinds of surrogate keys: integer sequences vs deterministic hash keys (implementation in Module 2.12) — trade-offs in parallel loading, reproducibility, and join performance |
| Intermediate | **Durable keys** (a stable identifier for an entity across all its SCD Type 2 versions) |
| Advanced | Natural key problems: reuse, changes, format differences across sources, and collisions (the same id meaning different things in two systems) |
| Advanced | Key mapping (cross-reference) tables for integrating identities from several systems |
| Advanced | Composite keys, and the "smart key" anti-pattern (encoding meaning into keys), with the common exception of `yyyymmdd` date keys |
| Advanced | Testing grain and keys: uniqueness of the grain columns, referential integrity from facts to dimensions, no orphan facts (assertion queries from Module 2.6) |

**How to learn it**

1. Read the topic file.
2. Write a grain statement for every table you built in Topics 02–03 and
   add a uniqueness test for each.
3. Find three mixed-grain tables in public datasets or your earlier work
   and explain how they mislead.

**Hands-on exercise — `models/04/`**

1. Integrate customers from two source systems (CRM and web shop) whose
   ids overlap but mean different things; build a key-mapping table and a
   single `dim_customer` with surrogate and durable keys.
2. Build a mixed-grain `orders` table (headers + lines) and show a revenue
   double-count; split it into proper tables.
3. Write assertion queries for grain uniqueness, referential integrity,
   and orphan facts; run them after every load.
4. Compare integer surrogate keys and hash keys: load two sources in
   parallel and discuss what breaks with sequences.

**Checkpoint:**

- [ ] Write a precise grain statement for any table.
- [ ] Explain natural, surrogate, and durable keys.
- [ ] Explain the problem of mixed grain.
- [ ] Integrate keys from several sources with a mapping table.
- [ ] Test grain and referential integrity with SQL.

**Common mistakes:** undocumented grain; surrogate keys that are
regenerated on every full reload (breaking downstream joins); trusting
that source ids never change or collide.

---

## 8. Phase C — Modelling Change Over Time (Intermediate → Advanced)

### Topic 05 — [Slowly changing dimension types](05-slowly-changing-dimension-types.md)

**Why here:** Dimension attributes change: customers move, products change
category, employees change department. How you store that change decides
whether reports show history "as it was" or "as it is". In Module 2.6 you
implemented Type 1 and Type 2 in SQL; this topic teaches **which type to
choose and why**, including the other types.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The core question for every attribute: when it changes, should old facts report the **old value** or the **new value**? |
| Basics | **Type 0** (never changes — retain original), **Type 1** (overwrite — no history), **Type 2** (new row per version — full history) |
| Intermediate | **Type 3** (previous-value column — limited history, e.g. `current_region`, `previous_region`) |
| Intermediate | **Type 4** (history in a separate table, or a mini-dimension for rapidly changing attributes such as age band or credit score band) |
| Intermediate | **Type 6** (hybrid of 1 + 2 + 3: history rows plus a current-value column on every row) — and awareness of Types 5 and 7 |
| Intermediate | Choosing a type **per attribute**, not per table; writing an SCD policy table (attribute → type → reason) with business stakeholders |
| Intermediate | Type 2 conventions: `valid_from` / `valid_to` (half-open intervals), `is_current`, far-future end dates, version numbers |
| Advanced | Facts and Type 2: assigning the correct dimension version at load time (surrogate key lookup by event time) vs point-in-time joins at query time |
| Advanced | "As was" vs "as is" reporting from the same model using durable keys and Type 6 current columns |
| Advanced | Rapidly changing and very large dimensions: when Type 2 explodes in size and mini-dimensions or snapshots are better |
| Advanced | Late and out-of-order changes, back-dated corrections, and deletes in the source — design decisions (the SQL repair mechanics were covered in Module 2.6) |
| Advanced | Alternatives: daily dimension **snapshots** (cheap storage, simple logic, big tables) and tool-based snapshots (e.g. dbt snapshots, Module 2.12) |

**How to learn it**

1. Read the topic file.
2. For a customer dimension with 15 attributes, fill in an SCD policy
   table and defend each choice as if in a stakeholder meeting.
3. For one customer's history of changes, draw the rows under Types 1, 2,
   3, 4, and 6.

**Hands-on exercise — `models/05/`**

1. Generate 90 days of customer snapshots with changes to address,
   segment, email, and birth date (a correction).
2. Build `dim_customer` with a **mixed policy**: Type 0 for signup date,
   Type 1 for email and name corrections, Type 2 for segment and region,
   Type 6 current columns for segment.
3. Build a Type 4 mini-dimension for rapidly changing `loyalty_points_band`.
4. Load `fct_orders` with the correct `customer_key` version at order time.
5. Answer "revenue by segment as it was at the time of the order" and "as
   the segment is today" from the same model.
6. Compare with a daily-snapshot design: table size and query simplicity.

**Checkpoint:**

- [ ] Explain Types 0, 1, 2, 3, 4, and 6 with examples.
- [ ] Choose an SCD type per attribute and justify it.
- [ ] Explain "as was" vs "as is" reporting and support both.
- [ ] Explain when snapshots or mini-dimensions beat Type 2.

**Common mistakes:** Type 2 on every column "just in case" (huge tables,
confusing reports); Type 1 on attributes the business needs history for;
not agreeing the policy with business users.

---

## 9. Phase D — Alternative Modelling Paradigms (Advanced)

### Topic 06 — [Data Vault: hubs, links, and satellites](06-data-vault-hubs-links-and-satellites.md)

**Why here:** Dimensional models are built for consumers. When a company
integrates many changing source systems and needs full auditability, a
separate integration layer is often modelled with Data Vault — and
dimensional marts are built on top of it.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The problem Data Vault solves: many sources, frequent source changes, full history, auditability, and parallel loading |
| Basics | **Hubs**: unique business keys of core business concepts (customer, product, order) with load date and record source |
| Basics | **Links**: relationships between hubs (order ↔ customer, order ↔ product) |
| Basics | **Satellites**: descriptive attributes and their history, attached to a hub or link, split by source or rate of change |
| Intermediate | Standard columns: hash keys, **hash diffs** (change detection), `load_date`, `record_source` (hashing implementation details are in Module 2.12) |
| Intermediate | Insert-only loading: why Data Vault never updates or deletes, and how that supports audit and parallel loads |
| Intermediate | **Raw vault** (source-aligned, no business rules) vs **business vault** (derived, rule-applied structures) |
| Intermediate | Building **information marts** (star schemas) on top of the vault |
| Advanced | Query helpers: **PIT (point-in-time) tables** and **bridge tables** to make vault queries fast |
| Advanced | Modelling challenges: choosing business keys, same-as links for duplicates, multi-active satellites, effectivity satellites for relationship validity |
| Advanced | Costs and criticism: many tables, complex queries, heavy tooling needs — and when Data Vault is overkill (small teams, few sources) |
| Advanced | Comparing integration approaches: Data Vault vs a normalised (Inmon-style) enterprise layer vs going straight from staging to dimensional marts |

**How to learn it**

1. Read the topic file.
2. Take your retailer model and redraw its integration layer as hubs,
   links, and satellites.
3. Add a new source system to both designs (dimensional only vs vault +
   marts) and list what changes in each.

**Hands-on exercise — `models/06/`**

1. Build a raw vault in DuckDB for customers, products, and orders from
   **two source systems**: `hub_customer`, `hub_product`, `hub_order`,
   `link_order_customer`, `link_order_product`, and source-specific
   satellites with hash diffs.
2. Load 10 days of changes insert-only; prove no row is ever updated.
3. Build a PIT table for customers and an information mart (`dim_customer`
   Type 2 and `fct_order_lines`) from the vault.
4. Add a third source system and document which tables change (compare
   with the effort in a dimensional-only design).
5. Write a one-page decision: would you use Data Vault for this company?

**Checkpoint:**

- [ ] Explain hubs, links, and satellites.
- [ ] Explain hash keys, hash diffs, load dates, and record sources.
- [ ] Build an information mart from a vault.
- [ ] Explain when Data Vault is worth its cost and when it is not.

**Common mistakes:** putting business rules in the raw vault; choosing
technical ids instead of business keys for hubs; exposing the vault
directly to BI users.

---

### Topic 07 — [One big table and wide denormalized models](07-one-big-table-and-wide-denormalized-models.md)

**Why here:** At the consumption end, many teams flatten stars into single
wide tables for dashboards, analysts, and ML. Modern columnar engines make
this practical — but not free.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **One big table (OBT)**: facts and all needed dimension attributes pre-joined into one wide table at a clear grain |
| Basics | Why teams use it: no joins for users, simple BI configuration, fast scans in columnar formats (Modules 2.4–2.5) |
| Intermediate | Trade-offs: duplicated attributes, expensive rebuilds when a dimension changes, frozen "as was" vs "as is" semantics, and very wide schemas |
| Intermediate | OBT as a **derived** layer: built from a star schema (the source of truth), never instead of it |
| Intermediate | Choosing columns: consumer-driven, not "everything"; naming conventions for prefixed dimension attributes |
| Intermediate | Nested and repeated fields as an alternative to exploding (e.g. an order row with an array of line items) — engine support from Module 2.5 |
| Advanced | Wide tables for ML: entity-level feature tables (one row per customer per day) and point-in-time correctness to avoid leakage (feature stores in Module 2.22) |
| Advanced | Incremental maintenance of wide tables: which partitions to rebuild when a dimension attribute changes |
| Advanced | Aggregated wide tables (pre-computed metrics) and their consistency with atomic facts |
| Advanced | Awareness of related patterns: the activity schema (one narrow activity stream + derived wide tables) and metric/semantic layers (Module 2.22) as alternatives to many hand-built wide tables |

**How to learn it**

1. Read the topic file.
2. Build an OBT from your star and write the same ten business queries
   against both; compare SQL length and speed.
3. Change a dimension attribute and measure the cost of refreshing the
   OBT.

**Hands-on exercise — `models/07/`**

1. Build `obt_order_lines` (one row per order line with product, customer,
   store, and date attributes) from your star in DuckDB, stored as sorted,
   partitioned Parquet.
2. Compare storage size, query time, and SQL complexity with the star.
3. Change 1% of product categories and implement an incremental refresh of
   only affected partitions; compare with a full rebuild.
4. Build `customer_features_daily` for an ML churn model with
   point-in-time-correct features (only information known on that day).
5. Build a nested version (order with an array of lines) and compare query
   convenience.

**Checkpoint:**

- [ ] Explain when an OBT helps and what it costs.
- [ ] Build an OBT as a derived layer from a star.
- [ ] Refresh a wide table incrementally.
- [ ] Explain point-in-time correctness for ML feature tables.

**Common mistakes:** OBT as the only model (no source of truth);
hundreds of unused columns; ML features that leak future information;
silently mixing "as was" and "as is" attributes.

---

## 10. Phase E — Modelling Behavioural Data (Advanced)

### Topic 08 — [Modelling event and clickstream data](08-modelling-event-and-clickstream-data.md)

**Why last:** Event data — clicks, page views, app actions, IoT signals —
is usually the largest data in a company, and it combines every idea from
this module: grain, keys, identity, history, and wide models.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What an event is: something that happened, immutable, with a timestamp, an actor, an action, an object, and properties |
| Basics | A standard event envelope: `event_id`, `event_name`, `event_timestamp`, `received_at`, `user_id`, `anonymous_id`, `session_id`, `context` (device, app version, page), `properties` |
| Basics | Event tables as append-only transaction facts at the grain of one event |
| Intermediate | **Tracking plans**: agreed event names, required properties, types, and owners (the event version of a data contract — Module 2.11) |
| Intermediate | Storing event properties: typed columns for common properties, a JSON/struct column for the long tail, per-event-type tables for important events |
| Intermediate | Event time vs received time; late and out-of-order events (streaming treatment in Module 2.16) |
| Intermediate | Deduplicating events with `event_id` (client retries send duplicates) |
| Intermediate | **Sessions** as a derived model (session fact table with start, end, duration, pages, source) — the SQL sessionisation technique is in Module 2.6 |
| Advanced | **Identity stitching**: linking anonymous device ids to logged-in user ids across devices; identity graphs; re-attributing past anonymous events |
| Advanced | Derived behavioural models: funnels (ordered steps with time limits), retention cohorts, activation metrics, and attribution (first touch, last touch, multi-touch) |
| Advanced | Bot and internal-traffic filtering, and test-event pollution |
| Advanced | Physical design for huge event volumes: partitioning by event date, clustering by user or event name, retention and aggregation of old raw events (Modules 2.5, 2.15) |
| Advanced | Privacy in event data: PII in properties, consent flags, and deletion requests (Module 2.20) |
| Advanced | Awareness of event specifications used in industry (e.g. Segment-style and Snowplow-style schemas) and how they shape your models |

**How to learn it**

1. Read the topic file.
2. Write a tracking plan for a small mobile app (10 events) with required
   properties and types.
3. Draw the models derived from raw events: sessions, identity map,
   funnel, retention, and daily user activity.

**Hands-on exercise — `models/08/`**

Generate 30 days of clickstream data for 100,000 users (anonymous and
logged-in, several devices, duplicates, late events, bots):

1. Build `fct_events` with a typed envelope and a JSON properties column;
   deduplicate by `event_id`.
2. Build an identity map from `anonymous_id` to `user_id` and restate past
   anonymous events to known users.
3. Build `fct_sessions` (30-minute inactivity rule) with duration, pages,
   and entry source.
4. Build a signup → first purchase funnel with conversion rates and a time
   limit, and weekly retention cohorts.
5. Filter bots by user-agent and behaviour rules and show their effect on
   metrics.
6. Build `user_activity_daily` (a wide, per-user-per-day table) for
   analysts and ML.

**Checkpoint:**

- [ ] Design an event schema and a tracking plan.
- [ ] Explain event time vs received time and deduplication by event id.
- [ ] Build sessions, funnels, and retention from raw events.
- [ ] Explain identity stitching and its effect on historical metrics.
- [ ] Explain how to handle PII and deletion in event data.

**Common mistakes:** free-form event names ("Clicked Button", "button
click", "btnClick"); dumping every property into JSON forever; counting
anonymous and known ids of the same person as two users; ignoring bots.

---

## 11. Consolidate — practice questions and interview practice

### [`practice-questions.md`](practice-questions.md)

For every question:

1. Summarise the business and list at least ten questions the model must
   answer.
2. Identify business processes, declare the grain of every table, and
   choose fact table types.
3. Choose dimensions, keys, and SCD policy per attribute.
4. Draw the ER diagram.
5. Build it on generated data and answer the questions in SQL.
6. Stress it with a change (new source, attribute change, late data) and
   note what breaks.

### [`interview-practice.md`](interview-practice.md)

Data modelling rounds are open-ended design conversations. Practise with a
**45-minute timer**, out loud, with a whiteboard or paper:

1. **Clarify** (5 min): users, key questions, scale, freshness, history
   needs.
2. **Processes and grain** (10 min): list processes, pick the most
   important, state its grain.
3. **Facts and dimensions** (10 min): draw the star, including keys.
4. **Change and edge cases** (10 min): SCD choices, late data, many-to-many
   relationships, identity.
5. **Physical and scale** (5 min): partitioning, clustering, OBTs for
   consumers.
6. **Trade-offs** (5 min): what you would do differently at 100× the scale
   or with ten sources.

Typical prompts: ride-sharing (trips, drivers, pricing, ratings), music
streaming (plays, playlists, subscriptions), e-commerce (orders, returns,
inventory), banking (accounts, balances, transactions), hotel booking
(reservations and cancellations), food delivery (order lifecycle),
advertising (impressions, clicks, attribution), and "our revenue numbers
differ between two dashboards — how do you find out why?".

---

## 12. Module mini-project — an end-to-end model for an online marketplace

This is the proof that you have finished the module.

**Scenario:** A two-sided marketplace (buyers and sellers) runs three
source systems: an OLTP orders database, a CRM, and a web/app event
tracker. Leadership wants trustworthy revenue, seller performance, buyer
retention, and funnel metrics; the data science team wants churn features.

Build `marketplace_model/` in DuckDB (with Python data generators) with:

1. **Discovery** — a business summary, 20 business questions, and an
   enterprise **bus matrix**.
2. **Source analysis** — 3NF source schemas reverse-engineered and
   documented, including keys, soft deletes, and overlapping ids between
   the CRM and the orders database.
3. **Integration layer** — a Data Vault raw vault for buyers, sellers,
   listings, and orders from all sources (insert-only), with a PIT table.
4. **Dimensional marts** — `fct_order_lines` (transaction),
   `fct_seller_daily` (periodic snapshot), `fct_order_lifecycle`
   (accumulating snapshot), conformed `dim_date`, `dim_buyer`,
   `dim_seller`, `dim_listing`; an SCD policy per attribute with Types 1,
   2, and 6; unknown members; a bridge table for listings in multiple
   categories.
5. **Events** — `fct_events`, identity map, `fct_sessions`, a purchase
   funnel, and weekly retention cohorts.
6. **Consumption** — an OBT for the BI team and a point-in-time-correct
   `buyer_features_daily` table for churn modelling.
7. **Quality** — assertion queries for grain, keys, referential integrity,
   SCD integrity, and reconciliation (revenue identical across vault,
   star, and OBT).
8. **Documentation** — ER diagrams, grain statements, a data dictionary,
   and a design decision log explaining every major choice.

**Grading yourself:** all 20 business questions are answered with short,
readable SQL; "as was" and "as is" reports both work; adding a fourth
source requires changes only in the integration layer; every table has a
documented grain and a passing uniqueness test; and a non-engineer can
follow your diagram.

---

## 13. Module self-assessment — exit criteria

Only move to Module 2.9 when you can tick every box without looking at your
notes:

- [ ] I can normalise to 3NF and explain when to denormalise.
- [ ] I can apply the four-step dimensional design process.
- [ ] I can choose fact table types and classify measure additivity.
- [ ] I can design star and snowflake schemas and drill across facts.
- [ ] I can write grain statements and choose natural, surrogate, and
      durable keys.
- [ ] I can choose SCD types per attribute and support "as was" and "as
      is" reporting.
- [ ] I can model an integration layer with Data Vault and build marts on
      it.
- [ ] I can design OBTs and ML feature tables as derived layers.
- [ ] I can model events, sessions, identity, funnels, and retention.
- [ ] I have finished the practice questions, interview practice, and the
      mini-project.

---

## 14. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| *The Data Warehouse Toolkit*, 3rd edition — Ralph Kimball and Margy Ross (Wiley) | 02, 03, 04, 05 |
| Kimball Group — "Dimensional Modeling Techniques" reference pages | 02–05 |
| *Building a Scalable Data Warehouse with Data Vault 2.0* — Dan Linstedt and Michael Olschimke (Morgan Kaufmann) | 06 |
| *Agile Data Warehouse Design* — Lawrence Corr (DecisionOne Press) — business-driven modelling and the bus matrix | 02, 05 |
| *Database Design for Mere Mortals* — Michael J. Hernandez | 01 |
| *Fundamentals of Data Engineering* — Joe Reis and Matt Housley, chapter on data modelling | 01, 06, 07 |
| dbt Labs guides on modelling layers and dimensional modelling in dbt | 02, 07 |
| Segment and Snowplow documentation on event specifications and tracking plans | 08 |

---

## 15. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| Source schemas and change patterns | 2.9 Data Ingestion — incremental extraction and CDC |
| Tracking plans and schema agreements | 2.11 Data Validation — data contracts |
| Hash keys, hash diffs, merges, dbt snapshots | 2.12 Transformation Patterns and Pipeline Design |
| Star joins and broadcast joins at scale | 2.14 PySpark |
| Physical layout of large fact and event tables | 2.15 Lakehouse Table Formats — clustering and Z-ordering |
| Event time, late events, sessions in streams | 2.16 Streaming and Event-Driven Data |
| Warehouse-specific physical modelling | 2.17 Cloud Data Platforms |
| PII in dimensions and events; deletion | 2.20 Observability, Lineage, Governance, and Security |
| Semantic layers, metrics, and feature stores | 2.22 Serving Data for Analytics, ML, and AI |

Every pipeline you build from here on produces tables that someone will
query, trust, and make decisions from. The discipline of this module —
start from business questions, declare the grain, choose keys and history
deliberately, and document the model — is what makes those tables worth
trusting.
