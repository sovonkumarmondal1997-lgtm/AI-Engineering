# 04 — Dimensional Modeling: Facts, Dimensions and Grain

> **Roadmap location:** Stage 2D — Data Architecture → `04-Conceptual-Logical-and-Physical-Data-Modeling/` → `04-dimensional-modeling-facts-dimensions-and-grain.md`  
> **Prerequisites:** Modules 2–3 (relational modeling, keys, constraints, normalization), the Stage 2D warehouse/lakehouse layers topic, and basic SQL aggregation.  
> **Scope:** Dimensional modeling fundamentals, star schemas, grain, additivity, SCD Types 1–3, fact-table types, conformed dimensions, bridges, fact-less facts, join correctness and consumption layers. Data Vault and broader historical modeling are covered in Module 5.  
> **Illustrative-data notice:** Northbridge Bank and all names, records, metrics, thresholds and results in this lesson are fictional teaching examples, not real institutional data or measured production performance.

## 1. Learning objectives

By completing this lesson, you will be able to:

1. Explain why dimensional models organize analytical facts around business processes and descriptive dimensions.
2. Define a fact, measure, dimension, attribute, hierarchy, surrogate key, business key and degenerate dimension.
3. State the exact grain of every fact table before choosing its dimensions or measures.
4. Follow the sequence: choose business process → declare grain → identify dimensions → identify facts/measures.
5. Design a star schema for card transactions with Date, Customer, Card, Merchant and Channel dimensions.
6. Classify measures as additive, semi-additive or non-additive and aggregate them correctly.
7. Distinguish transaction, periodic snapshot and accumulating snapshot fact tables.
8. Choose Type 1, Type 2 or Type 3 slowly changing dimension behavior based on the required historical question.
9. Use conformed dimensions, drill-across, bridge tables, fact-less facts, unknown members and late-arriving dimension handling.
10. Detect mixed grain, join fan-out, double counting, missing rows and unsafe joins between facts.
11. Define a business-question coverage matrix and validate it against illustrative data and expected query results.
12. Explain how a dimensional model serves analytics and semantic consumption without replacing integrated, normalized or historical data structures.

## 2. Why the topic matters in real-world Data Architecture

Business users ask questions such as “How much did customers spend last month?”, “Which merchant categories grew?”, and “What was the average month-end balance by segment?” They usually do not want to navigate a normalized operational schema or reconstruct business meaning independently for each report.

Dimensional modeling organizes analytical data around **business processes** (such as card transactions, payments, balances or account opening) and describes each event using dimensions such as date, customer, product, merchant and channel. It makes common filters, groupings and measures easier to understand and query.

The principal risk is that a query can return a plausible but incorrect number. A fact table with mixed grain, a join that multiplies rows, a historical dimension join that matches two versions, or a semi-additive balance summed over time can silently inflate or distort totals. Correctness therefore begins with grain and business semantics—not with SQL syntax or dashboard layout.

### 2.1 The design sequence

Use this sequence for every dimensional design:

1. **Choose the business process.** Name the measurable process or lifecycle, such as posted card transactions.
2. **Declare the grain.** State exactly what one row means. This must be precise enough to decide whether two events belong in the same row.
3. **Identify the dimensions.** Determine the who/what/where/when/how context required to filter and group the process.
4. **Identify the facts and measures.** Select values that are true at that grain, document units and additivity, and define how derived measures are calculated.

Do not start by listing columns from an existing report. Reports can mix grains and repeat facts in ways that should not become the logical model.

## 3. Prerequisite knowledge

You should already understand:

- Module 2: entities, relationships, cardinality, optionality, identifiers and referential integrity.
- Module 3: relations, keys, dependencies, normalization, decomposition and justified denormalization.
- The difference between integrated/source structures and consumption-oriented warehouse models.
- Basic SQL joins, `GROUP BY`, `SUM`, `COUNT`, `AVG`, `CASE` and date filtering.

Dimensional modeling is not a replacement for relational reasoning. Keys and constraints still matter; they are applied to a model designed around analytical questions.

## 4. Beginner-level learning sequence

### 4.1 Start with the business question, then declare grain

**One row per card transaction.**

This is the grain sentence for the first worked example. It means each row represents one identifiable card transaction event—not one customer per day, not one card per month, and not one transaction line mixed with a daily balance. If the source contains multiple authorization attempts, reversals and settlement records, the business must decide which events count as transactions and whether reversals are separate events. The grain cannot resolve that policy by itself.

For the illustrative Northbridge Bank card-spend process:

- **Business process:** card transaction events accepted into the analytics model.
- **Grain:** one row per card transaction.
- **Dimensions:** Date, Customer, Card, Merchant and Channel.
- **Facts/measures:** transaction amount in the transaction currency, fee amount in that currency, and a transaction count represented by one row per transaction.

A measure must be meaningful at this grain. A current account balance is not a transaction-level measure merely because it can be joined to a transaction.

### 4.2 Definitions

| Term | Meaning | Example |
|---|---|---|
| Business process | A measurable organizational activity or lifecycle. | Card purchase, payment, month-end account balance. |
| Fact table | Rows recording events, snapshots or process instances at a declared grain. | `FactCardTransaction`. |
| Fact | A measurable event/value or fact-table record. | A transaction amount; the occurrence of an eligibility event. |
| Measure | A value to aggregate or analyze. | Amount, fee, duration, count. |
| Dimension | Descriptive context used to filter, group or label facts. | Date, Customer, Merchant. |
| Dimension attribute | A descriptive field on a dimension. | Customer segment, merchant category, channel name. |
| Hierarchy | A meaningful path through dimensional levels. | Date → Month → Quarter → Year; Merchant → Category. |
| Business key | Identifier from the source/business domain. | `CustomerID`, `MerchantID`, transaction reference. |
| Surrogate key | Warehouse-managed identifier for a dimension row/version. | `CustomerKey = 2041`. |
| Degenerate dimension | A dimensional identifier kept directly in the fact table without a separate dimension table. | Transaction reference number. |
| Grain | The exact business meaning of one row in a fact table. | One row per card transaction. |

A fact table is not simply “the table with numbers.” It records facts at a specified grain and links those facts to the context in which they occurred.

### 4.3 Illustrative card-transaction star schema

A **star schema** places one fact table at the center and connects it directly to descriptive dimension tables. In a conventional dimensional star, dimensions are usually denormalized for usability; this is a consumption model, not a reason to abandon the normalized operational source.

**Fact table grain: one row per card transaction.**

| Table | Example columns | Key/relationship notes |
|---|---|---|
| `FactCardTransaction` | `TransactionFactKey`, `DateKey`, `CustomerKey`, `CardKey`, `MerchantKey`, `ChannelKey`, `TransactionRef`, `Amount`, `FeeAmount`, optional `TransactionCount` | In this design, `TransactionFactKey` is the PK; enforce a separate source-event deduplication key for the declared transaction identity. FKs point to dimension surrogate keys. `TransactionRef` is a degenerate dimension unless it needs its own descriptive dimension. |
| `DimDate` | `DateKey`, `FullDate`, `Day`, `Month`, `MonthName`, `Quarter`, `Year`, `IsBusinessDay` | `DateKey` is the dimension PK; a readable date is also retained. |
| `DimCustomer` | `CustomerKey`, `CustomerID`, `CustomerName`, `Segment`, `Region`, `ValidFrom`, `ValidTo`, `IsCurrent` | `CustomerKey` is the surrogate PK; `CustomerID` is the business key. Type 2 versions can share one business key. |
| `DimCard` | `CardKey`, `CardID`, `CardType`, `CardStatus`, `IssueDate`, `ExpiryMonth` | Use a surrogate key if card attributes are historized or source keys are unstable across systems. |
| `DimMerchant` | `MerchantKey`, `MerchantID`, `MerchantName`, `MerchantCategory`, `City`, `Country` | Merchant category is a descriptive attribute/hierarchy level, not usually a transaction measure. |
| `DimChannel` | `ChannelKey`, `ChannelCode`, `ChannelName`, `ChannelGroup` | Channel can represent POS, e-commerce, ATM, mobile or another agreed channel vocabulary. |

Illustrative relationships (each dimension's PK is referenced by the fact's matching FK):

```text
                 DimDate
                    |
DimCustomer --- FactCardTransaction --- DimMerchant
                    |
                  DimCard
                    |
                 DimChannel
```

This is a schematic, not a physical layout; each FK-to-PK relationship is many fact rows to one dimension row. A transaction fact must resolve to exactly one row per dimension role, including a documented unknown or inferred row where appropriate. If a transaction can have multiple merchants, customers or channels by business definition, use an explicit allocation/bridge or revise the grain rather than forcing a false one-to-one attribution.

Every transaction fact should reference exactly one row in each required dimension at the transaction's declared grain. If the source does not yet know the customer or merchant, use a documented unknown/inferred dimension row rather than dropping the fact or leaving an unexplained dangling key.

**Keys and attributes**
- The fact table contains dimension foreign keys and measures at the declared grain.
- Dimension surrogate keys identify dimension rows. With Type 2 history, multiple dimension rows may share the same business key.
- Business keys remain useful for lineage, source matching and deduplication.
- Descriptive labels belong in dimensions, not copied into every fact row unless there is an explicit snapshot or physical projection decision.
- A transaction reference with no independent descriptive attributes can remain a degenerate dimension in the fact. If `TransactionCount` is stored, set it to `1` for every row so it is additive; otherwise use `COUNT`/`COUNT DISTINCT` according to event identity and deduplication rules.

### 4.4 Additive, semi-additive and non-additive measures

Measure classification depends on its business meaning, unit, and dimension—not only on its SQL data type.

| Type | Example | Correct behavior |
|---|---|---|
| **Additive** | Transaction amount, fee amount, posted debit/credit amount | Can be summed across the dimensions for which the measure has compatible units and meaning. Currency conversion may be required before combining currencies. |
| **Semi-additive** | Account balance at a point in time | Can often be summed across accounts at the same snapshot time, but should not normally be summed across time. |
| **Non-additive** | Interest rate, percentage, ratio, average | Do not sum the displayed values. Recompute from additive components or use a specifically defined weighted calculation. |

“Transaction amount is additive across all dimensions” is only shorthand under explicit assumptions. Amounts in different currencies cannot be meaningfully summed without a currency conversion policy; a transaction amount may also be signed or gross/net according to business definitions. A dimension can expose a grouping that makes an otherwise valid measure meaningless unless the semantic layer defines the correct unit and aggregation.

**Example: average transaction amount**

Suppose one day has two transactions of 10 and 30 currency units, and another day has one transaction of 100. The average of all three transactions is `(10 + 30 + 100) / 3 = 46.67`, not the average of the two daily averages `(20 + 100) / 2 = 60`. For rollups, retain additive components such as `SUM(Amount)` and `COUNT(TransactionID)` and compute `SUM(Amount) / COUNT(TransactionID)` at the requested level.

**Example: balance**

Month-end balances for two accounts are 100 and 200 units. Total balance at that month-end is 300. If the same balances are recorded at the next month-end, summing both months' balances gives 600, which is not a meaningful two-month total. Use a point-in-time measure such as month-end balance for a selected date, or calculate a defined average balance over the period.

### 4.5 Exercise: loan repayment process

Before listing columns, write a grain sentence. One valid option is:

> One row per posted loan repayment transaction.

Possible dimensions: Date, Customer, Loan Account, Payment Channel, Currency, and Payment Status (if the status is meaningful at the repayment event grain). Possible measures: posted repayment amount and fee amount. If the requirement is instead to measure each loan's monthly outstanding balance, that is a different business process and grain, and should normally use a periodic snapshot fact.

**Beginner checkpoint:** Can you say what one row means without using vague phrases such as “a customer transaction record”? If not, the grain is not yet defined.

## 5. Intermediate-level learning sequence

### 5.1 Design dimensions and their hierarchies

Dimensions should carry the descriptive attributes needed for filtering, grouping, sorting and labeling. Keep the business vocabulary understandable; avoid forcing analysts to repeatedly decode operational codes.

Examples:
- Date: day → month → quarter → year.
- Merchant: merchant → merchant category → category group, if these levels are part of the approved business taxonomy.
- Customer: customer → region, with segment history handled explicitly.
- Channel: channel → channel group.

A hierarchy is not automatically a strict parent-child hierarchy. If a merchant can belong to multiple categories at once, model the many-to-many relationship rather than storing a single misleading category attribute.

### 5.2 Slowly changing dimensions (SCD Types 1, 2 and 3)

Suppose customer `C-10` changes segment from `Standard` to `Preferred` on 1 July 2026. The correct SCD choice depends on the business question.

| Type | What changes in the dimension | What a historical report means | Appropriate when |
|---|---|---|---|
| **Type 1 — overwrite** | Replace `Standard` with `Preferred` in the existing dimension row. | Historical facts joined to that row now appear as Preferred, including earlier transactions. | Corrections or attributes for which prior values must not be retained. |
| **Type 2 — new version** | End-date the old row and insert a new row with a new surrogate key, validity dates and current flag. | Each fact can remain associated with the dimension version valid when the event occurred. | Historical reporting must preserve segment-at-event semantics. |
| **Type 3 — previous value column** | Keep current segment plus a limited previous-segment field (for example `CurrentSegment`, `PreviousSegment`). | Preserves only a bounded comparison, not an arbitrary history of changes. | A specific limited “current versus prior” analysis is required. |

**Type 2 example**

| CustomerKey | CustomerID | Segment | ValidFrom | ValidTo | IsCurrent |
|---:|---|---|---|---|---|
| 101 | C-10 | Standard | 2025-01-01 | 2026-07-01 | false |
| 205 | C-10 | Preferred | 2026-07-01 | 9999-12-31 | true |

Use a consistent interval convention such as `[ValidFrom, ValidTo)`: the start is inclusive and end is exclusive. A transaction on 30 June joins key 101; one on 1 July joins key 205. Dimension ETL must prevent overlapping effective intervals and define what happens when a change arrives late.

**Historical-report implication:** Type 1 changes past report labels by design. Type 2 preserves event-time classification when the fact's surrogate key is assigned to the correct version. Type 3 supports only the explicitly retained prior value and can lose older history after subsequent changes. A report asking “segment now” is different from one asking “segment when the transaction occurred.”

### 5.3 Transaction, periodic snapshot and accumulating snapshot facts

Every fact type needs its own grain sentence.

| Fact type | Explicit grain example | Row behavior | Good for |
|---|---|---|---|
| **Transaction fact** | One row per card transaction. | Insert a row for each event; normally not updated except for controlled corrections or status/event modeling. | Event-level detail, counts, spend and drill-down. |
| **Periodic snapshot fact** | One row per account per calendar month-end snapshot. | A row represents the state measured at a defined periodic boundary; new periods add rows. | Month-end balance, utilization and periodic portfolio state. |
| **Accumulating snapshot fact** | One row per loan application lifecycle instance. | The same row is updated as milestones occur, such as application, approval, funding and closure; milestone dates/lag measures are filled over time. | Process pipeline, durations and completion rates. |

Do not combine these grains in one fact table. A card transaction and an account's month-end balance represent different kinds of facts. If both are needed, create separate fact tables and combine their aggregated results using conformed dimensions and carefully defined measures.

### 5.4 Conformed dimensions and drill-across

A **conformed dimension** uses consistent business definitions, attributes, keys/identity rules and governance across fact tables. For example, `DimDate` and a governed customer identity/segment dimension can support both card-transaction and monthly-account-balance analytics.

**Drill-across** compares measures from separate fact tables at a common dimensional level. It is not a direct join of raw facts to one another. First aggregate each fact to the shared grain (for example customer segment × month), then join those aggregate results on the conformed dimension keys. This prevents one transaction row from multiplying one balance snapshot row.

Conformance requires shared semantics, not merely identically named columns. If one fact's “month” means posting month and another means statement month, the business must define whether comparing them is valid.

### 5.5 Unknown members and late-arriving dimensions

A fact can arrive before its dimension details. Two common cases:

- **Unknown/not supplied:** the source does not know which customer or merchant the event belongs to yet.
- **Late-arriving dimension:** the business key is known, but the descriptive dimension record arrives after the fact.

A robust warehouse pattern uses special dimension rows with documented surrogate keys, such as `-1 = Unknown`, `-2 = Not Applicable`, and a separate inferred-member convention if needed. The exact keys are implementation choices, not universal standards. Do not use one generic unknown row to mean several different states if those states matter analytically.

For a late-arriving known business key, create an **inferred dimension member** with the business key and placeholder descriptive attributes, then update or Type-2-version it when authoritative details arrive. The ETL must preserve fact identity, avoid duplicate business-key matches and correctly assign the fact to the applicable historical version. Unknown dimension members prevent facts disappearing through inner joins, but they do not replace data-quality monitoring.

### 5.6 Bridge tables, many-to-many dimensions and fact-less facts

A **bridge table** models a many-to-many association that cannot be represented by one dimension key on the fact without losing meaning. For example, one customer may belong to multiple customer segments or groups. A bridge might contain `CustomerKey`, `SegmentKey`, effective dates and an optional allocation weight.

If one transaction belongs to a customer with two segment memberships, joining the transaction fact directly to both memberships duplicates the transaction amount. Options depend on the business question:
- Report the transaction under each segment, but clearly label the measure as overlapping/non-additive across segments.
- Use allocation weights that sum to 1 for each transaction's applicable membership set, if the business approves allocating rather than duplicating value.
- Define one primary segment per transaction using a deterministic business rule.
- Report at the customer level first, then show membership counts separately.

A **fact-less fact table** records the occurrence of an event or relationship without a numeric measure. Examples include customer eligibility by product and date, attendance, or customer–segment membership. Counts can be derived from its rows, but the row grain and duplicate rules must be explicit. A fact-less fact is not a workaround for missing measures; it represents an event/coverage relationship whose occurrence itself matters.

### 5.7 Fan-out, mixed grain and missing rows

**Fan-out** occurs when a join matches one row on one side to multiple rows on the other, multiplying the joined result. This can happen when:
- A Type 2 dimension join matches more than one effective version.
- A fact is joined to a many-to-many bridge without allocation or an explicit overlapping-membership policy.
- Two fact tables at different grains are joined directly.
- A supposed dimension key is not unique.

**Mixed grain** means one fact table contains rows with different meanings, such as transaction rows and month-end balance rows. A query can then sum measures together or count rows under assumptions that are false for some rows.

**Missing rows** can arise from inner joins to absent dimensions, filtering out unknown members, or joining on the wrong business key. A fact row should not disappear silently merely because dimension ETL is late.

#### Numerical example: correct and incorrect results

Illustrative data:

`FactCardTransaction` grain: one row per card transaction.

| TransactionID | Month | CustomerID | Amount |
|---|---|---|---:|
| T1 | 2026-06 | C-10 | 100 |
| T2 | 2026-06 | C-10 | 50 |
| T3 | 2026-06 | C-20 | 80 |

Correct June transaction total: `100 + 50 + 80 = 230`.

Illustrative customer-segment bridge, grain: one row per customer-segment membership for the valid period:

| CustomerID | Segment |
|---|---|
| C-10 | Standard |
| C-10 | Rewards |
| C-20 | Standard |

Joining the raw transaction fact to this bridge produces four joined rows:
- T1 appears twice (Standard and Rewards): 100 + 100
- T2 appears twice: 50 + 50
- T3 appears once: 80

Naive `SUM(Amount)` after the join is `100 + 100 + 50 + 50 + 80 = 380`, not 230. The query is syntactically valid but semantically wrong for a total across all customers.

If the business wants overlapping segment views, the segment totals are Standard = 230 and Rewards = 150; these totals must not be added together because the memberships overlap. If the business wants an allocated total and approves equal allocation for C-10's two memberships, T1 contributes 50 to each segment and T2 contributes 25 to each; Standard becomes 155 (50 + 25 + 80) and Rewards 75 (50 + 25), totaling 230. Equal allocation is only illustrative; weights must be business-defined and sum to 1 per transaction/customer membership set.

### 5.8 Consumption and semantic layers

The **semantic layer** defines business measures and dimensions in reusable terms: “posted card spend,” “active customer,” “month-end balance,” currency conversion, exclusions, time basis and allowed aggregation. It can expose certified metrics, governed hierarchies, access rules and safe query patterns.

A semantic layer cannot repair an ambiguous grain or missing business rule by naming a metric. It should encode the approved definition and test that implementation against reference results.

**Logical versus physical denormalization**
- **Logical/model-level denormalization:** choose a consumption-friendly dimensional structure, such as a star schema whose dimension table stores descriptive attributes and hierarchy labels together rather than splitting every attribute into normalized operational tables. This is an intentional modeling choice for usability and query semantics.
- **Physical/performance denormalization:** introduce storage- or execution-level copies, such as materialized aggregates, summary tables, cached derived columns or precomputed joins, to meet measured workload targets. This is an implementation optimization, not a change to the business definition or declared fact grain.
- **Controls for either:** name the authoritative source of each duplicated fact, define refresh/rebuild and late-correction behavior, test reconciliation against the authoritative facts, document freshness, and measure the workload benefit. Physical duplication without these controls creates consistency and maintenance risks; logical star-schema design alone does not prove that a materialized aggregate is correct.

Performance structures such as aggregate tables or materialized views are physical consumption optimizations; they must preserve measure semantics and declare freshness. Do not claim a performance gain without workload evidence or label the expected gain as an illustrative hypothesis to benchmark.

Dimensional models generally serve consumption needs. They do **not** replace integrated or historical structures such as normalized operational models, curated integration layers or the Data Vault/historical approach in Module 5. Those structures preserve integration, lineage and change history; dimensional marts make selected business processes easier to analyze.

## 6. Advanced-level learning sequence

### 6.1 Scenario: average balance by customer segment by month

**Business question:** “What was the average month-end account balance by customer segment and month?”

Start by clarifying whether “average” means:
- Average across accounts at each month-end;
- Average daily balance within the month;
- Average balance per customer (with joint accounts handled explicitly);
- Or an average of account balances weighted by days or ownership share.

For the simplest interpretation, use a periodic snapshot fact with grain:

> One row per account per calendar month-end snapshot.

`FactAccountMonthEndBalance(AccountKey, DateKey, BalanceAmount)` has one balance per account at each month-end. Join each snapshot to the segment version valid under the approved rule (for example, segment at snapshot date versus current segment). For average month-end balance by segment and month, use `AVG(BalanceAmount)` over account rows in that month/segment, while documenting whether joint accounts count once per account, are assigned to a primary customer, or are allocated by ownership share. If a segment has multiple memberships per customer, bridge fan-out must be resolved first.

If the requested measure is average daily balance, a month-end snapshot alone is insufficient. You need daily balances or another defensible calculation based on the account's daily state.

### 6.2 Scenario: summing month-end balances across months

A month-end balance is semi-additive: it may be summed across accounts at a single date if the currency/ownership semantics permit, but summing the same account's balance across June, July and August does not produce a meaningful total balance. For a period-level report:
- Select a single reporting date for a point-in-time balance.
- Calculate the average of the monthly snapshots if that is the approved metric.
- Calculate average daily balance if that is what the business defines.
- For flows over a period, sum additive transaction amounts, not snapshot balances.

Never silently label `SUM(MonthEndBalance)` as “total balance for the quarter.”

### 6.3 Scenario: customers belonging to multiple segments

Clarify whether segments are mutually exclusive customer classifications or overlapping memberships. If exclusive, enforce one valid segment per customer per effective interval. If overlapping, model a bridge with validity dates and decide whether reporting uses overlapping totals, primary-segment attribution or weighted allocation. Define whether weights are effective-dated and ensure the sum of applicable weights is exactly 1 within an approved tolerance.

The bridge grain must be explicit, for example:

> One row per customer-segment membership version and its effective interval.

If a customer can re-enter the same segment later, a key may need a membership/version identifier or start date; `(CustomerKey, SegmentKey)` alone may not distinguish separate episodes. A Type 2 customer dimension can preserve changing attributes, but it does not automatically solve a many-to-many relationship between customers and segments.

### 6.4 Slowly changing dimensions and fact assignment

For Type 2 dimensions, the ETL process must assign the dimension surrogate key valid at the fact's event time. The business key alone is not sufficient to choose a historical version. Validate:
- No overlapping validity intervals for a business key when one version is expected at a time.
- Exactly one matching version for each fact event time, unless the business explicitly permits none/multiple.
- A documented rule for corrections arriving after facts were loaded.
- A current flag consistent with validity dates.
- Stable treatment of late-arriving facts and retroactive dimension corrections.

If the fact's surrogate key is wrong, the report may look complete while attributing transactions to the wrong segment. A correct Type 2 dimension table alone does not guarantee historical correctness; key assignment is part of the fact load.

### 6.5 Business-question coverage matrix

The matrix below is a design contract. “Answered by” identifies the relevant fact grain and dimensions; each question should be tested against a reference result.

| # | Analytical business question | Fact table and explicit grain | Dimensions / measure | Correctness rule |
|---:|---|---|---|---|
| 1 | What was total posted card spend by month? | `FactCardTransaction`: one row per card transaction. | Date; `SUM(Amount)` after currency normalization. | Include only approved posted statuses; do not mix currencies. |
| 2 | What was spend by merchant category and channel? | `FactCardTransaction`: one row per card transaction. | Merchant, Channel; `SUM(Amount)`. | Merchant category must be unique for the reporting attribution or explicitly bridge/allocation handled. |
| 3 | How many card transactions occurred by day? | `FactCardTransaction`: one row per card transaction. | Date; `COUNT(*)` or count distinct transaction ID. | Duplicate source events must be deduplicated by event identity. |
| 4 | What were fees by customer segment? | `FactCardTransaction`: one row per card transaction. | Customer Type 2 segment; `SUM(FeeAmount)`. | Assign segment surrogate key as of transaction time if “segment then” is intended. |
| 5 | What was average transaction amount by channel? | `FactCardTransaction`: one row per card transaction. | Channel; `SUM(Amount) / COUNT(valid transaction IDs)`. | Do not average pre-aggregated averages without weighting. |
| 6 | What was total month-end balance by month? | `FactAccountMonthEndBalance`: one row per account per calendar month-end snapshot. | Date; `SUM(BalanceAmount)` across accounts at a single month-end. | Do not sum balances across different month-end dates. |
| 7 | What was average month-end balance by segment and month? | `FactAccountMonthEndBalance`: one row per account per calendar month-end snapshot. | Date and segment; `AVG(BalanceAmount)` under a defined account/customer weighting rule. | Resolve joint ownership and segment membership before aggregation. |
| 8 | How long did a loan application take from submission to funding? | `FactLoanApplicationLifecycle`: one row per loan application lifecycle instance. | Milestone dates; elapsed time. | Define business-day/calendar-day rules and handle incomplete cases. |
| 9 | Which customers were eligible for a product but did not transact? | `FactCustomerProductEligibility`: one row per customer-product eligibility interval. | Customer, Product, Date; row existence/count. | Eligibility population and effective dates must be complete; absence of transaction is tested at compatible grain. |
| 10 | How much spend should be attributed to overlapping customer segments? | `FactCardTransaction`: one row per card transaction, joined to an effective-dated customer-segment bridge. | Customer, Segment; allocated or explicitly overlapping amount. | Never sum overlapping segment totals as if they were disjoint; use approved weights if allocating. |
| 11 | How much did card spend change compared with the prior month? | `FactCardTransaction`: one row per card transaction. | Date/month; current and prior month `SUM(Amount)`. | Compare like-for-like periods and consistent currency/status definitions. |
| 12 | What share of applications reached funding? | `FactLoanApplicationLifecycle`: one row per loan application lifecycle instance. | Milestones/status; funded application count / eligible application count. | Define cohort/denominator and do not count milestone rows as separate applications. |

Every row names the fact table's grain first, so the coverage matrix can expose when a question requires another fact type or a different attribution rule. Questions 6–7 cannot be correctly answered from transaction facts alone; Question 8 requires an accumulating snapshot; Question 9 requires eligibility coverage plus a compatible-grain anti-join against the relevant transaction/application process (often represented by a fact-less eligibility fact). The supplemental fixtures below make all 12 questions testable without mixing fact grains.

### 6.6 Small illustrative dataset and expected query results

All data below are illustrative and use one reporting currency to avoid mixing units.

**Fact grain: one row per card transaction.**

| TransactionID | Month | CustomerID | ProductID | SegmentAtTxn | MerchantCategory | Channel | Amount | FeeAmount |
|---|---|---|---|---|---|---|---:|---:|
| T1 | 2026-06 | C-10 | P-CARD | Standard | Grocery | POS | 100 | 1.00 |
| T2 | 2026-06 | C-10 | P-CARD | Standard | Fuel | POS | 50 | 0.50 |
| T3 | 2026-06 | C-20 | P-CARD | Preferred | Grocery | Online | 80 | 0.80 |
| T4 | 2026-07 | C-10 | P-CARD | Preferred | Grocery | Online | 70 | 0.70 |
| T5 | 2026-07 | C-20 | P-CARD | Preferred | Fuel | POS | 40 | 0.40 |
| T6 | 2026-07 | C-30 | P-CARD | Standard | Travel | Online | 60 | 0.60 |
| T7 | 2026-07 | C-30 | P-CARD | Standard | Grocery | POS | 30 | 0.30 |
| T8 | 2026-08 | C-10 | P-CARD | Preferred | Travel | POS | 120 | 1.20 |
| T9 | 2026-08 | C-20 | P-CARD | Preferred | Grocery | Online | 90 | 0.90 |
| T10 | 2026-08 | C-30 | P-CARD | Standard | Fuel | POS | 20 | 0.20 |
| T11 | 2026-08 | C-30 | P-CARD | Standard | Travel | Online | 40 | 0.40 |
| T12 | 2026-08 | C-20 | P-CARD | Preferred | Grocery | POS | 10 | 0.10 |

**Expected results**
- June total = `100 + 50 + 80 = 230`.
- July total = `70 + 40 + 60 + 30 = 200`.
- August total = `120 + 90 + 20 + 40 + 10 = 280`.
- Three-month transaction total = `230 + 200 + 280 = 710`.
- June Grocery total = `100 + 80 = 180`.
- June POS total = `100 + 50 = 150`.
- June average transaction amount = `230 / 3 = 76.67` (rounded to two decimals).
- Monthly transaction counts: June `3`, July `4`, August `5` (12 total).
- Monthly average transaction amounts: June `230 / 3 = 76.67`; July `200 / 4 = 50.00`; August `280 / 5 = 56.00`.
- Monthly category totals: June Grocery `180`, Fuel `50`; July Grocery `100`, Fuel `40`, Travel `60`; August Grocery `100`, Fuel `20`, Travel `160`. Across all months: Grocery `380`, Fuel `110`, Travel `220` (total `710`).
- Monthly channel totals: June POS `150`, Online `80`; July POS `70`, Online `130`; August POS `150`, Online `130`. Across all months: POS `370`, Online `340` (total `710`).
- Fees by segment at transaction time (using the illustrative `FeeAmount` values): Standard `3.00`; Preferred `4.10`; total fees `7.10`.

The next two SQL examples query the flattened illustrative dataset in Section 6.6, whose displayed columns include `Month`, `Amount` and `TransactionID`; a physical star implementation would normally group by the appropriate `DimDate` attributes.

Illustrative SQL for monthly spend:

```sql
SELECT Month, SUM(Amount) AS TotalSpend
FROM FactCardTransaction
GROUP BY Month
ORDER BY Month;
```

Expected output:

| Month | TotalSpend |
|---|---:|
| 2026-06 | 230 |
| 2026-07 | 200 |
| 2026-08 | 280 |

Illustrative SQL for average transaction amount:

```sql
SELECT Month,
       SUM(Amount) / NULLIF(COUNT(TransactionID), 0) AS AvgTransactionAmount
FROM FactCardTransaction
GROUP BY Month
ORDER BY Month;
```

The exact decimal/casting syntax varies by database. A production query should define rounding and currency rules explicitly. In SQL dialects that perform integer division, cast the numerator or denominator to a decimal type before division. The query above assumes `TransactionID` is non-null and unique after deduplication; otherwise use the approved event key and deduplication rule.

#### Reference fixtures for the full business-question matrix

The 12-row transaction dataset above validates transaction questions. The following small, separate fixtures support the other fact types. They are intentionally illustrative and are not additional rows in `FactCardTransaction`.

**Account-month balance fixture** — grain: one row per account per calendar month-end snapshot. For this fixture only, each account has one primary customer and one segment at month-end; joint ownership and overlapping segments require a separately approved attribution/allocation rule.

| Month-end | AccountID | CustomerID | SegmentAtSnapshot | BalanceAmount |
|---|---|---|---|---:|
| 2026-06-30 | A-1 | C-10 | Standard | 500 |
| 2026-06-30 | A-2 | C-20 | Preferred | 300 |
| 2026-06-30 | A-3 | C-30 | Standard | 200 |
| 2026-07-31 | A-1 | C-10 | Preferred | 550 |
| 2026-07-31 | A-2 | C-20 | Preferred | 250 |
| 2026-07-31 | A-3 | C-30 | Standard | 250 |
| 2026-08-31 | A-1 | C-10 | Preferred | 600 |
| 2026-08-31 | A-2 | C-20 | Preferred | 300 |
| 2026-08-31 | A-3 | C-30 | Standard | 150 |

Expected account-balance results:

| Month-end | Total balance at that date | Average balance across 3 accounts | Standard average | Preferred average |
|---|---:|---:|---:|---:|
| 2026-06-30 | 1,000 | 333.33 | 350.00 | 300.00 |
| 2026-07-31 | 1,050 | 350.00 | 250.00 | 400.00 |
| 2026-08-31 | 1,050 | 350.00 | 150.00 | 450.00 |

These totals may be summed across accounts **within the same month-end only**. Do not add 1,000 + 1,050 + 1,050 and call it a total balance. The average month-end balance over the three month-end observations for the portfolio, if that is the explicitly approved metric, is `(333.33… + 350 + 350) / 3 = 344.44` (equivalently `(1000 + 1050 + 1050) / (3 accounts × 3 month-end observations) = 344.44`). This is not average daily balance.

**Loan application lifecycle fixture** — grain: one row per loan application lifecycle instance. Use calendar days in this example; exclude the submission day by calculating date difference as `FundingDate - SubmissionDate`. The observation cohort contains four applications submitted in July 2026, with the status frozen at 2026-08-31.

| ApplicationID | CustomerID | SubmissionDate | FundingDate | Status as of 2026-08-31 |
|---|---|---|---|---|
| LA-1 | C-10 | 2026-07-01 | 2026-07-11 | Funded |
| LA-2 | C-20 | 2026-07-05 | 2026-07-20 | Funded |
| LA-3 | C-50 | 2026-07-08 | NULL | Not funded by observation date |
| LA-4 | C-40 | 2026-07-10 | 2026-07-25 | Funded |

Expected lifecycle results: LA-1 `10` calendar days, LA-2 `15`, LA-4 `15`; average elapsed time among funded applications is `(10 + 15 + 15) / 3 = 13.33` calendar days. Funding share for this defined cohort is `3 funded / 4 applications = 75%`. The cohort, observation date and incomplete-application treatment are part of the metric definition; do not infer a permanent failure from a still-open application.

**Eligibility fact-less fixture** — grain: one row per customer-product eligibility interval. For this example, the transaction rows explicitly carry `ProductID = P-CARD`; the eligibility product is also `P-CARD`, and interval boundaries are `[EligibleFrom, EligibleTo)`. The loan-application fixtures below concern a separate product/process and are not used for this card-transaction anti-join.

| CustomerID | ProductID | EligibleFrom | EligibleTo |
|---|---|---|---|
| C-10 | P-CARD | 2026-07-01 | 2027-01-01 |
| C-20 | P-CARD | 2026-07-01 | 2027-01-01 |
| C-30 | P-CARD | 2026-07-01 | 2027-01-01 |
| C-40 | P-CARD | 2026-07-01 | 2027-01-01 |

Against the 12-row card-transaction fixture for the defined July–August observation window, C-40 is eligible for `P-CARD` but has no card transaction; C-10, C-20 and C-30 do have card transactions. This is an anti-join at customer-product and cohort-period grain. Eligibility intervals must be complete, and duplicate/overlapping eligibility episodes must be governed before counting eligible customers.

**Reference output for the 12-question coverage matrix**

| Question | Expected result from these illustrative fixtures | Key qualification |
|---:|---|---|
| 1. Monthly posted spend | June `230`; July `200`; August `280` | Sample assumes all 12 rows are valid posted transactions in one reporting currency. |
| 2. Spend by category and channel | Category totals: Grocery `380`, Fuel `110`, Travel `220`; channel totals: POS `370`, Online `340` | Grouped totals sum to `710` because each transaction has one category and one channel. |
| 3. Transaction count by month | June `3`; July `4`; August `5` | Count distinct deduplicated transaction IDs. |
| 4. Fees by segment at transaction time | Standard `3.00`; Preferred `4.10` | Uses `SegmentAtTxn` and the illustrative `FeeAmount`; Type 2 key assignment must match event time. |
| 5. Average transaction amount by month | June `76.67`; July `50.00`; August `56.00` | Ratio of total amount to transaction count, not average of averages. |
| 6. Total month-end balance | June `1,000`; July `1,050`; August `1,050` | Each total is for one month-end date only. |
| 7. Average month-end balance by segment and month | Use the four segment-average columns above: June Standard `350`, Preferred `300`; July Standard `250`, Preferred `400`; August Standard `150`, Preferred `450` | Sample has one primary customer per account and one segment per account at each snapshot. |
| 8. Time from submission to funding | Funded applications: `10`, `15`, `15` days; mean `13.33` days | Calendar days; funded applications only for elapsed-time mean. |
| 9. Eligible customers with no card transaction | C-40 | Anti-join at customer-product/cohort grain; C-40 is eligible for `P-CARD` but has no matching card transaction in the sample window. |
| 10. Spend for overlapping segments | In the separate three-transaction bridge example: Standard `230`, Rewards `150`; raw joined sum `380` versus true all-customer spend `230` | Segment totals overlap and cannot be added; allocation requires approved weights. |
| 11. Spend change vs prior month | June→July: `-30` (`-13.04%`); July→August: `+80` (`+40.00%`) | Change is current month minus prior month; percent change divides by prior month. |
| 12. Share of applications funded | `3 / 4 = 75%` | Cohort is the four July applications observed through 2026-08-31. |

For Question 11, percentage changes are `(200 - 230) / 230 × 100 = -13.043…%` and `(280 - 200) / 200 × 100 = 40%`. The month-to-month comparison is based on the monthly totals above and uses consistent event status and currency rules.

### 6.7 Flawed-model exercise: mixed grain and unsafe joins

Suppose a team creates one table containing transaction rows and monthly account balances:

| RowType | AccountID | TransactionID | Month | Amount | MonthEndBalance |
|---|---|---|---|---:|---:|
| Transaction | A-1 | T1 | 2026-06 | 100 | NULL |
| Transaction | A-1 | T2 | 2026-06 | 50 | NULL |
| Balance | A-1 | NULL | 2026-06 | NULL | 500 |

This table has at least two grains: one row per transaction and one row per account-month-end. Summing `Amount` may appear to work because balance rows have NULL Amount, but row counts and averages now have mixed meanings. A query that counts rows as “transactions” will count the balance row too. If the balance value is copied onto every transaction row instead, `SUM(MonthEndBalance)` becomes 1,000 for the same account-month because 500 is repeated twice.

**Correction**
- `FactCardTransaction`: one row per card transaction.
- `FactAccountMonthEndBalance`: one row per account per calendar month-end snapshot.
- Aggregate each fact to the requested common dimensional grain before joining (for example month and customer segment).
- Keep measure definitions and fact grain in the semantic layer.

**Correctness proof for the copied-balance defect:** two transaction rows each carry 500, so the naive sum is `500 + 500 = 1,000`, but the account's month-end balance is 500. The duplicated value is not additive across transaction rows. The correct balance fact has one account-month row with 500; summing across accounts for that month is valid under the stated currency and ownership assumptions.

### 6.8 Practice exercise with verified answer

**Question:** In the sample dataset, what is the total spend for July by channel?

July rows:
- Online: T4 = 70, T6 = 60, so Online total = 130.
- POS: T5 = 40, T7 = 30, so POS total = 70.
- Total = 130 + 70 = 200, matching the monthly total.

**Question:** If customer C-10 is joined to two active segment memberships and every C-10 transaction is joined to both, what happens to the total?

C-10's sample transactions sum to `100 + 50 + 70 + 120 = 340`. The raw join repeats those four transactions twice, so C-10 contributes 680 to a naive total, an overstatement of 340. The right result depends on the business rule: overlapping reporting (do not add segment totals), single-segment attribution, or a weight-based allocation.

## 7. Industry-application exercises

### 7.1 Northbridge card and payment analytics design

Design the dimensional model for Northbridge Bank to answer the 12 business questions in Section 6.5. At minimum, include:
- `FactCardTransaction` at one row per card transaction.
- `FactAccountMonthEndBalance` at one row per account per calendar month-end snapshot if balance analytics are required.
- `FactLoanApplicationLifecycle` at one row per loan application lifecycle instance if milestone analysis is required.
- `FactCustomerProductEligibility` at one row per customer-product eligibility interval if eligibility coverage is required. If individual assessment events must be analyzed, create a separate fact with one row per eligibility assessment event.
- Date, Customer, Card, Merchant, Channel, Account, Product and other dimensions only where justified by the questions.
- Explicit PK/FK strategy, business keys, surrogate keys, degenerate dimensions, additivity, SCD treatment, unknown-member policy and late-arriving handling.

**Required review:** Every fact table must have a grain sentence before the measure list. Do not use one generic fact table for transactions, balances, eligibility and application milestones.

### 7.2 Validate using a small dataset

Use the 12 transaction rows in Section 6.6 and add sufficient illustrative dimension rows to test all dimensions. Validate at least:
1. Monthly spend.
2. Spend by merchant category.
3. Spend by channel.
4. Transaction count.
5. Average transaction amount using additive components.
6. Segment-at-transaction historical attribution.
7. A many-to-many segment join that intentionally exposes fan-out.
8. Month-end balance aggregation on a separate fact.
9. An unknown/late-arriving dimension event that must not disappear from the total.
10. A question that requires an accumulating snapshot or fact-less fact rather than the transaction fact.

Record expected results before running SQL, then compare query outputs. A passing query against only happy-path data is insufficient; include duplicates, unknown members, late records and multiple memberships.

### 7.3 SCD decision exercise

For a customer segment change, write three short reports:
- Type 1: prior transaction totals now labeled with the current segment.
- Type 2: prior transactions remain associated with the segment version valid at event time.
- Type 3: current and previous segment are available, but older transitions are not fully retained.

Explain which report the business actually needs and why. Do not choose Type 2 automatically if the only requirement is to correct an erroneous label, and do not choose Type 1 when regulatory or analytical requirements demand the historical segment.

### 7.4 Flawed-model review checklist

Inspect a proposed model and record:
- Every fact table's exact grain.
- Whether every measure is true at that grain.
- Whether dimension keys are unique at join time.
- Whether Type 2 date ranges are non-overlapping and fact keys use event time.
- Whether bridge joins multiply measures.
- Whether all required unknown/late-arriving rows survive.
- Whether snapshot measures are aggregated only across valid dimensions.
- Whether the semantic layer documents units, filters, denominators and historical semantics.

## 8. Practical scenarios and case-based reasoning

### 8.1 Average balance by customer segment by month

The word “average” is ambiguous until the population and time basis are specified. Average across accounts at month-end differs from average daily balance and average balance per customer. Use a periodic snapshot for month-end balance; define joint-account treatment and segment attribution before calculating. If a customer has multiple segment memberships, do not duplicate account balance into every segment and then add segment totals as if mutually exclusive.

### 8.2 Summing month-end balances across months

Month-end balance is semi-additive. Summing balances across accounts at one month-end can answer total balance at that point in time. Summing the same balances over multiple months does not answer “total balance.” Choose a point-in-time balance, average month-end balance, average daily balance or transaction flow according to the business question.

### 8.3 Customers belonging to multiple segments

First decide whether segment membership is mutually exclusive or overlapping. If overlapping, model the relationship with an effective-dated bridge and choose overlapping, primary-segment or weighted allocation semantics. Ensure bridge grain and weights are explicit. A bridge does not make a non-additive measure additive; it only represents the relationship.

### 8.4 Late-arriving dimension and unknown member

A transaction arrives for customer C-99, but the customer dimension record has not arrived. The pipeline should retain the transaction with an appropriate unknown or inferred dimension key, record the unresolved business key, and later resolve the correct dimension version. The team must monitor unresolved duration and ensure correction does not duplicate the fact. Do not drop the transaction through an inner join simply because descriptive data is late.

### 8.5 Conformed dimensions across transaction and balance facts

A dashboard wants card spend and month-end balance by customer segment and month. Do not join raw transaction rows to raw account-month snapshot rows. Aggregate spend to month × segment and balances to month × segment independently, then drill-across using conformed month and segment definitions. Validate that the two facts use compatible segment attribution and that joint accounts/overlapping segment memberships have an approved policy.

## 9. Expected outputs and deliverables

Create and retain these artifacts for review:

1. **Grain register:** one explicit sentence for every fact table, its business process, row identity and exclusions.
2. **Star schema:** fact and dimension tables, surrogate/business keys, FKs, dimension attributes and hierarchies.
3. **Measure dictionary:** business definition, unit/currency, additive class, valid aggregation, numerator/denominator, rounding and exclusions.
4. **SCD decision register:** Type 1/2/3 choice per changing dimension, historical report impact, effective dating and late-arriving policy.
5. **Business-question coverage matrix:** at least ten questions, with fact grain, dimensions, measures and correctness rules.
6. **Validated sample dataset:** at least a dozen illustrative transaction rows plus dimensions and expected outputs for key questions.
7. **Flawed-model review:** documented mixed-grain, fan-out, missing-row and semi-additive measure defects with corrected designs and numerical consequences.
8. **Conformed-dimension/drill-across design:** shared definitions and safe aggregation steps across fact tables.
9. **Bridge/fact-less design:** grain, keys, effective dates, weighting or overlapping-membership semantics.
10. **Practice-question answers:** corrected explanations with calculations, not just labels.

## 10. Common mistakes and misconceptions

- **Designing tables before grain:** the columns may look plausible while rows have inconsistent meanings.
- **Treating “one row per customer transaction” as precise:** state exactly which event counts and how reversals/attempts are handled.
- **Mixing transaction and snapshot rows:** row counts and measures no longer share a coherent grain.
- **Summing balances across time:** balances are usually semi-additive.
- **Summing ratios or averages:** recompute from additive components with the correct denominator.
- **Joining raw fact tables directly:** different grains multiply rows and inflate measures.
- **Assuming a Type 2 dimension alone guarantees history:** the fact must use the correct surrogate key for event time.
- **Using Type 1 when historical labels matter:** past reports change because the old attribute value is overwritten.
- **Using Type 3 for unlimited history:** it stores only a limited previous value.
- **Ignoring multi-membership bridges:** a bridge can duplicate fact measures.
- **Treating all segment totals as mutually exclusive:** overlapping membership means segment totals may not sum to the grand total.
- **Dropping facts with missing dimensions:** inner joins can silently remove legitimate events.
- **Using one unknown member for every state:** unknown, not applicable and late-arriving may have different meanings.
- **Calling a fact-less fact a fact table without a grain:** row uniqueness and counting semantics still matter.
- **Assuming same-named dimensions are conformed:** business definitions and time semantics must match.
- **Treating the semantic layer as a substitute for modeling:** metric names cannot fix a wrong grain or a fan-out join.
- **Replacing integrated history with a star schema:** dimensional models serve analytical consumption and generally depend on integrated/historical structures upstream.

## 11. Mastery criteria

You can demonstrate mastery when you can:

- Explain a business question before choosing the fact table.
- State the grain of every fact table in one unambiguous sentence.
- Follow business process → grain → dimensions → facts/measures.
- Design the card transaction star schema with Date, Customer, Card, Merchant and Channel.
- Justify keys, dimension attributes, hierarchies and degenerate dimensions.
- Classify measures and calculate totals/averages with valid aggregation rules.
- Explain transaction, periodic snapshot and accumulating snapshot row meanings and update behavior.
- Select SCD Type 1, 2 or 3 with explicit historical-report consequences.
- Use conformed dimensions and drill-across without joining raw facts at incompatible grains.
- Handle many-to-many segment memberships, bridge weights, fact-less facts, unknown members and late-arriving dimensions.
- Show a numerical fan-out or mixed-grain defect and prove the corrected expected result.
- Complete a coverage matrix for at least ten analytical questions.
- Explain why dimensional models serve consumption and do not replace integrated or historical structures.
- Correct practice answers and record the assumptions that make them valid.

## 12. Completion gate

Do not mark Module 4 complete until the following evidence exists:

- [ ] **Explicit grain statements:** every fact table has a precise grain sentence, including event identity, snapshot period or process instance.
- [ ] **Business-question coverage matrix:** at least ten analytical questions map to the correct fact grain, dimensions, measures and validation rules.
- [ ] **Star schema reviewed:** the card transaction star includes Date, Customer, Card, Merchant and Channel dimensions with keys, measures and degenerate transaction reference.
- [ ] **Additivity verified:** additive, semi-additive and non-additive measures have documented valid aggregation; month-end balances are not summed across months.
- [ ] **SCD decisions justified:** Type 1/2/3 effects on historical reports are demonstrated with a customer-segment change.
- [ ] **Flawed-model exercise corrected:** mixed grain, fan-out, double counting and missing-row risks are identified with a numerical result and a corrected design.
- [ ] **Sample calculations validated:** the illustrative dataset's monthly totals, category/channel totals and averages agree with the stated arithmetic and SQL.
- [ ] **Fact-table types demonstrated:** transaction, periodic snapshot and accumulating snapshot have distinct row meanings and update behavior.
- [ ] **Advanced relationship cases addressed:** conformed dimensions, drill-across, bridge tables, fact-less facts, unknown members and late-arriving dimensions are documented.
- [ ] **Practice questions answered and corrected:** answers include the business assumptions and aggregation reasoning.
- [ ] **Second-pass review completed:** grain, keys, dimension relationships, SCD behavior, join cardinality, calculations and coverage matrix have been checked against the stated requirements.

**Completion standard:** the model is accepted only when each fact row has a precise meaning, each measure has a valid aggregation rule, every requested business question maps to the correct grain, and known join/history risks are either prevented or explicitly governed.
