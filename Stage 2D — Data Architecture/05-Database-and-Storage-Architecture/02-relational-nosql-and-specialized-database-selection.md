# Relational, NoSQL and Specialized Database Selection

> **Scope and scenario note:** This lesson follows Topic 2 of `roadmap-Database-and-Storage-Architecture.md` in Stage 2D — Data Architecture. It is vendor-neutral and teaches category-level reasoning, not product administration. Northbridge Bank and every workload value or numerical input below are fictional, illustrative assumptions—not facts about a real organisation, benchmarks, requirements, or targets. Capabilities and guarantees vary by system and configuration; verify them for any real candidate.

## 1. Learning objectives

By the end of this lesson, you should be able to:

1. Explain the relational model and distinguish key-value, document, wide-column, graph, search, time-series, and vector store categories.
2. Translate business needs into explicit queries and updates before considering database categories.
3. Compare candidates using data-model fit, access patterns, relationship complexity, transaction boundaries, consistency, query flexibility, schema variability, workload rate, scale, availability, governance, skills, and total cost of ownership (TCO).
4. Explain normalized and query-shaped (often denormalized) models, including duplication, update anomalies, and application-managed joins.
5. Reason about vertical and horizontal scaling, partition keys, secondary indexes, skew, and hotspots without assuming uniform load.
6. Estimate storage and per-partition write rate using stated assumptions and units.
7. Decide when a specialised store or a polyglot-persistence design is justified—and when a single general-purpose store is the lower-risk answer.
8. Produce a selection matrix and a lightweight Architecture Decision Record (ADR) that names the system of record, rejected alternatives, assumptions, risks, validation, and revisit triggers.

**Core rule:** Workload evidence first; database category second. A category is a candidate, not a decision.

## 2. Why the topic matters in real-world data architecture

A database category shapes what an application can query cheaply, where correctness is enforced, how the system scales, and how much operational work the organisation accepts. A poor choice can create permanent workarounds: joins reconstructed in application code, duplicated records that drift apart, integrity rules enforced inconsistently, or a specialised index treated as authoritative data when it cannot safely serve that role.

The opposite error is also expensive: adding a new database because it is popular even though an existing relational store can meet the measured requirements. Each additional store introduces ownership, access control, monitoring, backup and recovery, upgrades, on-call knowledge, data movement, reconciliation, and incident-response work.

### 2.1 The decision sequence

```text
Business requirement
        ↓
Entities, relationships, keys and correctness rules
        ↓
Important reads and writes: keys, filters, ranges, order, rate, target
        ↓
Workload profile and constraints
        ↓
Baseline + two or three viable category candidates
        ↓
Consistency, transaction, scale, governance and operating-cost review
        ↓
Selection matrix + ADR + validation plan
        ↓
Measure representative behaviour and revisit if evidence changes
```

This sequence prevents technology-first reasoning. For example, “the customer schema changes often” is not enough to select a document store. Ask which fields change, whether records have stable identity, how customer records relate to accounts and addresses, whether cross-entity transactions are required, and which queries must remain flexible.

### 2.2 Terms used in this lesson

- **Data model:** how information and relationships are represented, such as tables, documents, key-value pairs, or graph nodes and edges.
- **Access pattern:** a recurring way an application reads or changes data, described by keys, filters, ranges, sort order, frequency, result size, and response target.
- **System of record (SoR):** the authoritative owner of a business fact. Other stores may hold derived or cached copies, but the design defines which source wins when copies disagree.
- **Schema-on-write:** structure and validation are applied as data are written. Relational systems commonly use this approach, although actual flexibility varies.
- **Schema-on-read:** interpretation or structure is applied when data are read. It can accommodate variation but may move validation and ambiguity into consumers.
- **Normalization:** structuring related facts to reduce unnecessary duplication and update anomalies.
- **Denormalization:** deliberately duplicating or reshaping data to serve a query efficiently.
- **Partition key:** the value used to distribute records or requests across partitions in a partitioned system.
- **Secondary index:** an additional access path that helps query fields other than the primary key; it consumes resources and may add write cost.
- **Eventual consistency:** a model in which replicas may temporarily disagree but are expected to converge if updates stop and replication succeeds. It is not a guarantee of a fixed convergence time.
- **Polyglot persistence:** using more than one kind of data store because distinct workloads justify distinct data models or access paths.

**Check your understanding:** Why is “we have a lot of data” not enough to choose a database category? A good answer names access patterns, correctness, rate, latency, growth, and operating constraints.

## 3. Prerequisite knowledge

The roadmap lists these prerequisites:

- **Topic 1 in this module:** operational versus analytical workload reasoning and the principle that workload shape drives storage choices.
- **Stage 2D, Module 2D.4, Topics 1–3:** conceptual/logical models, entities and relationships, keys, constraints, and normalization.
- **Requirements work from Module 2D.2:** volumes, rates, latency targets, availability, constraints, trade-offs, and ADRs.

You do not need deep database-administration expertise. You should be able to identify entities and keys, describe a join, distinguish a read from a write, and state a business correctness requirement.

### Quick prerequisite check

1. If an account has many transactions, what key identifies the account and what key identifies each transaction?
2. What is the difference between “retrieve one customer by ID” and “find all customers in a region ordered by last activity”?
3. Why might storing the same customer address in five records create a maintenance problem?
4. What does it mean for two changes to be atomic?

**Answer guidance:** A primary identifier distinguishes an entity or record; the second operation is a range/filter/sort query rather than a point lookup; duplicated addresses can diverge during updates; atomicity means the defined transaction succeeds as a unit or has no partial committed effect within its transaction boundary. If these ideas are unclear, revisit logical modeling and transaction basics before proceeding.

## 4. Beginner-level learning sequence

### 4.1 Start with the relational model

A **relational database** represents data as relations, commonly shown as tables. A table has rows (records) and columns (attributes). Keys identify rows and connect related tables. Constraints express rules that valid data must satisfy.

Consider an illustrative banking model:

- `Customer(customer_id, name, status)`
- `Account(account_id, customer_id, currency, status)`
- `LedgerEntry(entry_id, account_id, amount, currency, posted_at)`

`customer_id`, `account_id`, and `entry_id` can be primary keys. `Account.customer_id` can be a foreign key referring to `Customer.customer_id`. A foreign-key constraint can prevent an account from referring to a customer that does not exist, subject to the system's supported constraint behavior and configuration.

A **join** combines related rows using a relationship, such as joining `Account` to `Customer` on `customer_id`. **SQL (Structured Query Language)** supports declarative queries: the user describes the result, while the database chooses an execution plan. This makes many relational systems useful for flexible, unplanned questions as well as known application queries.

A **transaction** groups operations into a defined unit of work. Relational systems commonly provide transaction mechanisms and constraints suited to multi-row business changes, but exact isolation levels, constraint behavior, and distributed transaction scope must be checked for the candidate system.

**Integrity** means that data obey required rules: uniqueness, valid references, allowed values, and business invariants. A database can enforce some rules directly; others may require application logic, transaction design, or domain-level checks. Moving a rule into application code does not make the rule disappear—it makes the application responsible for applying it correctly on every path.

**Why it matters:** relational modeling is a strong baseline when entities have meaningful relationships, correctness rules cross records, and queries evolve over time.

**Where it can be less suitable:** a relational category may be a poor fit if the measured workload requires a specialized access path at a scale or rate the candidate cannot meet economically. That conclusion must be based on representative evidence, not a blanket claim that relational systems cannot scale.

**Trade-offs and failure modes:** normalized data can require joins; indexes consume storage and slow some writes; contention can occur under concurrent work; and a poorly designed schema or query can perform badly. These are design and implementation concerns to measure, not reasons to dismiss the category automatically.

**Check:** If a payment must update a ledger entry and an account status together, which selection question matters most? **Answer:** whether the chosen system can enforce the required transaction boundary and invariants, including the failure behavior if one step fails.

### 4.2 NoSQL is a family, not one interchangeable technology

**NoSQL** is a broad label for database approaches that do not use the conventional relational table model as their primary organizing model. The term does not identify one consistency model, query language, transaction capability, or scaling guarantee. The categories below are distinct and should be evaluated separately.

| Category | Conceptual model | Natural access pattern | Why it can fit | Typical limitation / question to verify |
|---|---|---|---|---|
| **Key-value** | Key maps to a value treated largely as one item | Get, put, or delete by known key | Very direct lookups such as sessions, tokens, or precomputed state | Arbitrary filtering, joins, and multi-item constraints may be awkward or unsupported; a cache may not be durable enough to be authoritative |
| **Document** | Self-describing document, often nested fields and arrays | Retrieve or update a document by ID and selected indexed attributes | Variable-structure profiles or aggregates naturally read as a unit | Cross-document joins, duplication, and multi-document integrity can be costly or vary by system; flexible fields still need governance |
| **Wide-column** | Rows grouped by partition key, with column families or flexible columns depending on the design | High-rate writes and key/range access within a known partition | Large event/time-oriented datasets where queries are designed around partition and clustering keys | Query flexibility often depends heavily on data modeling and partition choice; hot partitions and secondary-query limitations can dominate |
| **Graph** | Nodes represent entities; edges represent relationships, with optional properties | Traverse relationships across multiple hops | Questions such as “which accounts connect through shared devices and beneficiaries?” | Simple point reads may not need graph traversal; large traversals, changing graph structure, or high-degree nodes may be expensive; operational and consistency behavior vary |

Do not infer that every system in a category has identical transaction or consistency guarantees. Verify the specific candidate's documented semantics and configuration against the business requirement.

**Example:** A session lookup by session ID is naturally key-value-shaped. A customer profile with nested preferences may be document-shaped. A relationship investigation across many linked accounts is graph-shaped. A relational store may still serve any of these adequately if the access patterns, rate, and correctness needs fit it; category fit is a hypothesis to test.

**Check:** Why is “NoSQL is faster” not a valid selection argument? **Answer:** it does not identify the category, query, data shape, correctness requirements, or measured target.

### 4.3 Specialized stores: purpose-fit, not universal replacements

Specialized stores optimize for a narrower access pattern. They can be valuable as derived serving systems while a separate system remains authoritative.

| Specialized category | How it works conceptually | Useful for | Important limitations and safeguards |
|---|---|---|---|
| **Search store** | Maintains an index—often an inverted index mapping terms to documents—to support text retrieval, filtering, relevance ranking, and facets | Full-text search across product descriptions, support documents, or case notes | Indexing is often asynchronous or derived; results can lag source changes. Rebuild/reconciliation, access filtering, deletion propagation, and source-of-record ownership must be designed. A search index is not automatically the authoritative record store. |
| **Time-series store** | Organizes timestamped measurements, often with time-aware retention, aggregation, and downsampling | Metrics, telemetry, sensor readings, and time-window queries | High-cardinality dimensions, late data, corrections, long retention, and queries outside the expected time shape can raise cost or complexity. It may not suit complex entity relationships or transactional business records. |
| **Vector store** | Stores vector embeddings and supports similarity search, often using approximate nearest-neighbor techniques and optional metadata filters | Finding items semantically similar to a query vector, such as related text chunks or images | Similarity is not a source of truth; results may be approximate, embedding versions can change, and metadata filters/authorization must be enforced correctly. It does not replace transactional records or full-text search for every use case. |

The roadmap's specialized examples are search, time-series, and vector stores. Their suitability depends on the access pattern and verified system behavior, not on the category name alone.

**When not to add one:** if a general-purpose store meets latency, relevance, volume, and governance targets with acceptable cost, a specialized store may add more operational burden than value.

**Check:** Why should a search result be verified against the source of record for a sensitive account operation? **Answer:** the index may be stale, incomplete, or not designed to enforce authoritative transactional invariants.

### 4.4 Important modeling vocabulary

**Normalized model:** facts are stored in a way that limits unnecessary duplication. If a customer address changes, one authoritative customer record may be updated and related views join to it. Benefits include fewer update anomalies and clearer ownership. Costs include joins and the need to execute related queries efficiently.

**Query-shaped or denormalized model:** data are duplicated or nested to serve a known query with fewer joins or lookups. A document might embed the customer's display name and delivery preferences to return a page in one read. Benefits include predictable reads and fewer cross-record fetches. Costs include duplicated facts, extra storage, fan-out updates, possible inconsistency, and more complicated correction logic.

An **update anomaly** occurs when duplicated facts are not updated consistently. For example, a customer changes their legal name, but one copied profile is updated and three others are not. The system must define which value is authoritative, how copies are updated, and how divergence is detected and repaired.

**Application-managed joins** mean the application retrieves separate records and combines them itself. This can be valid for a small, bounded query, but may create extra network round trips, complicated error handling, partial results, and logic that each caller must implement consistently.

**Schema-on-write** applies validation/structure as records are stored; **schema-on-read** interprets data when a consumer reads it. Neither is universally superior. Schema-on-read can accommodate evolving source data, but it may cause inconsistent interpretation. Schema-on-write can catch invalid data earlier, but schema changes require compatibility planning. A document store can still enforce schemas or validators; a relational system can also support flexible data types. Treat these as tendencies, not absolute boundaries.

**Short exercise:** A team duplicates a customer's address into every order to avoid a join. Name two benefits and three risks.

**Answer guidance:** Benefit: an order view can be read without a join and preserves the address as it was at order time if that is intentional. Risks: storage duplication, update ambiguity if the address should be current, and inconsistent semantics if consumers confuse historical order address with current customer address. The correct model depends on the business meaning of the field.

### 4.5 Beginner checkpoint: match pattern to category

For each pattern, name a natural candidate and one reason a different category may be a poor fit:

1. Retrieve a session by exact session ID.
2. Retrieve a variable-structure customer profile as one unit.
3. Retrieve all events for a known device over a time range.
4. Find documents containing relevant terms and rank them.
5. Traverse accounts connected by shared devices across four hops.
6. Find the nearest semantic text chunks to an embedding.

**Answer guidance:** key-value; document; wide-column or time-series depending on the event/query model; search; graph (with relational recursive queries as a baseline); vector. These are starting hypotheses. A relational system may remain viable for some cases if the data volume and response target are modest and its query plan is adequate.

## 5. Intermediate-level learning sequence

### 5.1 List the access patterns before shortlisting categories

For each important read and write, record:

- **Operation:** read, insert, update, delete, relationship traversal, search, or aggregation.
- **Key:** exact primary/partition key, compound key, or no known key.
- **Filters and ranges:** equality, range, time window, text terms, vector similarity, or multiple conditions.
- **Sort order and result size:** top N, page, full range, or aggregate.
- **Frequency and concurrency:** requests per second, bursts, concurrent users or jobs, and peak factor.
- **Response target:** an explicit target or a measured current baseline, not an invented universal latency.
- **Write semantics:** idempotency, uniqueness, multi-record atomicity, correction and deletion requirements.
- **Data horizon and growth:** current state, recent history, or long-lived history; entities, item size, and retention.
- **Freshness and consistency:** how stale a derived copy may be and what a reader must observe after a write.

Do not write “high traffic” without a rate and time window. Do not write “real time” without a measurable freshness or response requirement.

#### Example access-pattern inventory (illustrative)

| ID | Operation | Key/filter/range | Order/result | Illustrative rate | Correctness / response question |
|---|---|---|---|---:|---|
| AP-1 | Read account balance | Exact `account_id` | One balance | 4,000 reads/s average, burst factor 3 | Must it reflect the latest committed posting? What is the response target? |
| AP-2 | Post ledger entry | Account key plus unique entry ID | Insert entry and update related state | 700 writes/s average, burst factor 2 | Must duplicate retries be prevented? What changes commit atomically? |
| AP-3 | List recent transactions | Account ID + time range | Newest first, up to 50 rows | 1,200 reads/s average | How many rows are touched and what is the allowed horizon? |
| AP-4 | Investigate account network | Seed account, traverse relationships up to 4 hops | Ranked candidate network | 15 analyst queries/minute | What graph size, traversal limit, and response target are acceptable? |

These values are illustrative only. They demonstrate what a useful profile looks like; they are not database capacity requirements.

**Check:** Which evidence would help decide between a relational and a wide-column candidate for AP-3? **Answer:** measured row count per account/time range, query frequency, partition-key design, sort/range needs, joins and constraints, growth, latency, and candidate-specific test results.

### 5.2 Use a repeatable selection matrix

Start with the minimum-change **baseline**—the current or most familiar general-purpose category, if one exists and is viable. Compare it with two or three feasible alternatives. Score only criteria relevant to the workload; a weighted score can organize discussion but must not hide hard constraints or unsupported assumptions.

| Criterion | Evidence or question to record | Hard constraint or preference? |
|---|---|---|
| Data model fit | Tables, documents, key-value items, graph relationships, time-series, text index, or vectors; cardinality and ownership | State explicitly |
| Access-pattern fit | Top reads/writes, keys, filters, ranges, sort order, result size, query frequency | Usually central |
| Relationship complexity | Number of entities involved, traversal depth, join complexity, integrity across records | State invariants |
| Transactions and integrity | Required atomic boundary, uniqueness, referential rules, idempotency, recovery behavior | Hard correctness rules cannot be traded away silently |
| Consistency | Read-after-write needs, stale-read tolerance, replica behavior, conflict handling | State exact expectation |
| Query flexibility | Known queries versus ad hoc filters, joins, reports, new questions | Explain expected change rate |
| Schema variability | Which fields change, optional fields, validation ownership, compatibility approach | Avoid “schema changes often” as sole evidence |
| Read/write workload | Rates, burst, item sizes, scans, concurrent clients, rows touched | Quantify and measure |
| Scale and growth | Entities, bytes, growth horizon, partition counts, hot keys, retention | State forecast assumptions |
| Availability and distribution | Failure tolerance, regions, network partitions, recovery expectations | Verify candidate guarantees |
| Governance and security | Access controls, audit, encryption, deletion, retention, data residency, sensitive copies | Hard constraints where applicable |
| Operations and skills | Monitoring, backups, restores, upgrades, incident response, staffing, on-call readiness | Include people cost |
| Total cost of ownership | Compute, storage, replicas, indexes, transfer, licences/service, migration, support, labour | Estimate range, not false precision |
| Validation | Representative workload test, correctness tests, failure tests, acceptance criteria | Required before final decision |
| Exit/revisit | What evidence would change the decision or justify removing a store? | Must be explicit |

**Selection procedure:**

1. Eliminate candidates that cannot satisfy hard correctness, security, residency, or availability requirements.
2. Compare the remaining candidates against actual access patterns.
3. Quantify volume, rate, and storage where possible; mark unknowns and ranges.
4. Compare operational effort and failure behavior, not only query speed.
5. Name a rejected alternative and the specific mismatch.
6. Validate with representative queries and failure tests before committing.

### 5.3 Relational versus query-shaped modeling

Use normalization where shared facts have one authoritative meaning and must remain consistent. Consider denormalization where a known read path is frequent and joins or cross-store lookups demonstrably fail the target.

| Question | Normalized relational tendency | Query-shaped / denormalized tendency |
|---|---|---|
| How is data duplicated? | Minimized where practical | Deliberately duplicated or nested |
| Read path | Joins may be needed | Common reads may be one item or fewer lookups |
| Update path | Update the authoritative fact, then query relationships | May need to update multiple copies or accept temporary lag |
| Ad hoc queries | Often flexible when model and indexes support them | New query can require another projection or re-modeling |
| Integrity | Constraints and transactions may enforce cross-row rules | Application, transaction scope, or reconciliation may carry more responsibility |
| Common failure | Expensive joins or poorly indexed query | Divergent copies, write amplification, and application-managed joins |

These are tendencies, not guarantees. Relational databases can denormalize; document and wide-column systems can validate data and support some transactions. Judge the candidate system and configuration, not the label alone.

**Example:** An order record should preserve the delivery address used at purchase time. Copying that address into the order may be correct historical modeling—not a defect—because the meaning is “address at order time.” Copying the customer's current risk status into many independent records may be unsafe if decisions require the latest authoritative status. Duplication must be tied to explicit semantics.

### 5.4 Consistency and transaction guarantees must be verified

Do not assign one guarantee to an entire category. For each candidate, verify:

- What operations can commit atomically, and across how many records or partitions?
- What does a successful write guarantee to subsequent reads from the same client, another client, or another region?
- Can readers observe stale replicas or partial application-level updates?
- How are concurrent updates and conflicts resolved?
- What happens during network partition, failover, retry, or recovery?
- Are uniqueness, references, and other constraints enforced by the store, or by application logic?

A design that moves integrity from the database to the application must account for every write path, concurrent writers, retries, partial failures, tests, and reconciliation. A rule enforced in only one API endpoint is not a system-wide invariant.

**Check:** If a system supports single-item atomic writes, does that prove two independent items can be updated atomically? **Answer:** no. The transaction boundary must be verified explicitly.

### 5.5 Scaling: vertical, horizontal, partitions, indexes, and skew

- **Vertical scaling** increases resources for a node or instance. It can be operationally simpler, but capacity and cost may have limits and a larger node does not automatically remove all bottlenecks.
- **Horizontal scaling** adds nodes or partitions. It can increase capacity, but only if the workload distributes effectively and the system can coordinate the required operations. Cross-partition work may be more expensive or constrained.
- **Partitioning** divides data or requests using a key or strategy. A good partition key distributes traffic and supports important queries. A poor key can concentrate traffic.
- **Hotspot:** a node or partition receives disproportionate traffic, becoming a bottleneck even when total capacity looks adequate.
- **Skew:** the actual distribution is uneven. The assumption that each partition receives an equal share is often only a first estimate.
- **Secondary index:** provides a query path on fields that are not the primary key. It may improve reads but consume storage and add write maintenance; index consistency and query limits vary by system.

A key that distributes stored rows evenly may still be a poor choice if one key receives most writes. Conversely, a partition key that makes a frequent range query efficient may produce uneven traffic. Evaluate both data distribution and request distribution.

#### Worked quantitative example: storage estimate

The roadmap's illustrative formula is:

```text
storage_needed = entities × average_item_size × replication_factor × (1 + index_overhead)
```

Assumptions for this example only:

- Entity count: 20,000,000 customers (20 million entities).
- Average item size: 3 KB/entity, interpreted as 3,000 bytes/entity (decimal units).
- Replication factor: 3 total copies, assumed for the estimate.
- Index overhead: 30% of the replicated base data, so `index_overhead = 0.30` and multiplier `(1 + 0.30) = 1.30`.
- This simplified estimate excludes other overheads such as logs, snapshots, temporary space, compression effects, metadata, and backup copies unless they are included separately.

Formula and substitution:

```text
base_data = 20,000,000 entities × 3,000 bytes/entity
          = 60,000,000,000 bytes
          = 60 GB (decimal; 1 GB = 1,000,000,000 bytes)

replicated_data = 60 GB × 3 copies
                = 180 GB

storage_needed ≈ 180 GB × (1 + 0.30)
               = 180 GB × 1.30
               = 234 GB
```

**Interpretation:** under these assumptions, the rough stored footprint is 234 GB before any additional unmodeled overhead. It is not a benchmark or a capacity guarantee. Real item size, indexes, compression, replication semantics, and retained copies must be measured or confirmed for a specific system.

#### Worked quantitative example: average writes per partition

The roadmap gives:

```text
per-partition_write_rate = total_write_rate / partitions
```

This formula assumes a uniform distribution of writes and partitions of comparable capacity.

Illustrative assumptions: total write rate is 12,000 writes/second and there are 120 active partitions.

```text
average writes per partition
  = 12,000 writes/second ÷ 120 partitions
  = 100 writes/second/partition
```

**Interpretation:** 100 writes/second/partition is an average only. If 25% of writes target one partition, that partition receives 3,000 writes/second before accounting for other traffic, not 100. The design must measure key-frequency distribution and test the hottest partitions; uniform-key division is not a safe capacity promise.

**Check:** What changes if average item size doubles from 3 KB to 6 KB while other assumptions remain constant? **Answer:** the estimate doubles from 234 GB to 468 GB because the formula is linear in item size.

## 6. Advanced-level learning sequence

### 6.1 Quantify alternatives instead of relying on labels

For each candidate, estimate or measure:

- request rates, peak factors, item sizes, entities, growth, and retention;
- storage, replicas, indexes, and any derived copies;
- read and write amplification from denormalization or index maintenance;
- partition counts, key distribution, hotspots, and cross-partition query needs;
- representative query latency and throughput under expected concurrency;
- recovery, backup/restore, migration, and failure behavior;
- the cost of the people and processes needed to operate it.

A benchmark is useful only if its dataset, access patterns, concurrency, correctness checks, and environment represent the intended workload. Do not use a synthetic result as a universal property of a database category.

### 6.2 Integrity: database-enforced versus application-enforced

Suppose an application requires a unique external transaction reference. If the chosen store can enforce uniqueness within the needed scope, the store may provide a strong guard against concurrent duplicate submissions. If uniqueness is only checked by application code before inserting, two concurrent requests can both observe “not present” and then insert unless the design has another correct coordination mechanism.

Before moving integrity into code, identify:

1. all writers and update paths;
2. concurrent execution and retry behavior;
3. the atomicity boundary available in the candidate;
4. partial-failure and recovery behavior;
5. tests and reconciliation that detect violations;
6. the owner who will maintain the invariant.

The trade-off is not simply “database versus code.” It is the cost and reliability of enforcing the same business rule across all paths.

### 6.3 Query flexibility versus pre-shaped access paths

A relational model can be attractive when new filters, joins, and analytical questions are expected because the relationships are explicit and the query model is flexible. Query-shaped NoSQL models can be attractive when a known set of access patterns dominates and predictable item-level access matters. However, if a second important query appears, the original model may not serve it cheaply; another index, projection, duplication strategy, or store may be needed.

Ask: **What is the second-most-important query, and does the design serve it without an expensive workaround?** If the answer is unknown, record that uncertainty and validate it rather than assuming the first query is the only one that will matter.

### 6.4 Polyglot persistence: when multiple stores are justified

Polyglot persistence means deliberately combining different data-store categories. It can be justified when one workload has a materially different access pattern and a general-purpose baseline cannot meet a required target at acceptable total cost.

Illustrative example:

- A relational system remains the system of record for accounts and ledger entries because transaction boundaries, integrity, and flexible joins are central.
- A graph store may serve multi-hop fraud-network exploration if representative tests show the graph traversal is materially better suited than relational recursive queries and meets the required response target.
- A search index may serve full-text search over case documents if relevance and text retrieval requirements justify indexing a derived copy.
- A time-series store may serve high-volume metric telemetry if time-window queries and retention/downsampling dominate.

This is not a recommendation to adopt all four. Each added store must pass a separate justification test.

#### Added costs of every extra store

- **Data duplication:** more bytes, more copies to protect, and more opportunities for divergence.
- **Synchronization:** propagation delay, ordering, retry, delete handling, reconciliation, and stale reads.
- **Ownership boundaries:** a clear authoritative source and named owner for each entity and derived view.
- **Monitoring and incident response:** another set of availability, lag, capacity, backup, and correctness signals.
- **Skills and on-call:** training, runbooks, troubleshooting, upgrades, and support coverage.
- **Security and governance:** access policy, audit, encryption, retention, deletion, and sensitive-data controls must be equivalent where required.
- **Migration and exit:** data conversion, backfill, rollback, and eventual retirement of obsolete copies.

A store is not justified merely because it can perform a task. It is justified when the benefit over the baseline is supported by evidence and exceeds the full cost and risk of operating it.

### 6.5 General-purpose versus specialized: a decision threshold

A mature general-purpose store may be adequate for a niche workload if its measured behavior meets response, correctness, scale, and governance needs. Prefer that simpler baseline when the specialized alternative offers no material benefit.

A specialized store becomes a stronger candidate when:

- the access pattern is central to the business;
- representative tests show the baseline misses a stated target or requires costly workarounds;
- the specialized category has the necessary query semantics;
- consistency, authorization, deletion, and reconciliation can be handled safely; and
- the organization can support its operational lifecycle.

State the **evidence threshold** before testing—for example, a defined response-time target at an agreed concurrency and dataset size, plus correctness and recovery tests. Do not invent a universal threshold or infer a pass from category reputation.

### 6.6 Worked decision: graph store proposal for fraud investigation

**Illustrative proposal:** analysts want to follow links among accounts, devices, phone numbers, addresses, and beneficiaries up to four hops to identify suspicious clusters.

**Access-pattern evidence to collect:** number of entities and edges; distribution of degree (including high-degree nodes); maximum traversal depth; filters applied at each hop; query frequency; analyst concurrency; response target; update frequency; and whether a result must reflect the latest relationship update.

**Candidates:**

1. **Baseline relational store with recursive queries:** attractive if the relationship graph is modest, traversal depth is bounded, existing relational data and skills are sufficient, and representative queries meet the target. Avoids another store and a synchronization pipeline.
2. **Graph store:** attractive if traversals are a dominant workload and representative tests demonstrate a meaningful benefit at the required graph size and response target. Requires graph data ownership, ingestion/update synchronization, access controls, monitoring, and a plan for stale or missing edges.
3. **Precomputed relationship projection:** may be sufficient if the required questions are known and can be served from derived tables or summaries. It may not support exploratory, previously unknown traversals as flexibly.

**Do not decide from the word “graph.”** Compare correctness, freshness, operations, and total cost. A graph projection that omits a recently added relationship may produce a different investigation result; the design must state whether that lag is acceptable and how it is detected.

**Revisit triggers:** the baseline repeatedly misses the agreed target under representative peak load; query depth or graph size grows beyond tested bounds; or the maintenance cost of the relational workaround exceeds the measured cost of operating a graph projection. If the graph store does not meet the target or creates unacceptable synchronization risk, retain or redesign the baseline.

### 6.7 Failure modes to design against

| Failure mode | Why it happens | Mitigation / evidence |
|---|---|---|
| Selecting before listing access patterns | Decision follows fashion or team familiarity | Require a query/update inventory and workload profile before scoring candidates |
| Treating NoSQL as one category | Different data models and query semantics are conflated | Evaluate key-value, document, wide-column, and graph separately |
| Document model recreates joins in application code | Related entities are split or duplicated without a query plan | Inventory relationship queries; estimate network calls and fan-out; compare relational baseline |
| Cache used as system of record | Durability, eviction, failover, or consistency is assumed rather than verified | Keep an authoritative source unless the candidate's documented guarantees meet the business requirement; test failure and recovery |
| Integrity moved into application code incompletely | Some writers or concurrency paths bypass the rule | Enumerate all writers, use correct atomic mechanisms, test races/retries, and reconcile |
| Search index treated as authoritative | Index lag, partial indexing, or deletes are ignored | Define SoR, lag monitoring, backfill/rebuild, delete propagation, and source verification |
| Hot partition or key skew | Average rate hides concentration | Measure key distribution and hottest-partition rate; load-test skewed data |
| Secondary indexes proliferate | Each index is added without accounting for write/storage cost | Tie each index to a query, measure benefit, and remove unused indexes after safe validation |
| Too many stores with unclear ownership | No team owns authoritative facts or cross-store correctness | Name SoR and owners; document synchronization, conflict rules, security, and retirement path |
| Specialized store adopted without a measurable advantage | Category reputation substitutes for evidence | Define baseline, target, representative test, and cost comparison before adoption |

### 6.8 Architecture Decision Record (ADR) outline

An ADR is a concise, reviewable record of why a decision was made and what evidence could change it. Use this outline for each important database-category decision.

```markdown
# ADR: [Workload / Decision]

- Status: Proposed | Accepted | Superseded
- Date / owner / reviewers:

## Context and requirements
- Business outcome and entities:
- Important access patterns (keys, filters, ranges, order, frequency):
- Data volume, rates, growth, and response/freshness targets:
- Correctness, transaction, consistency, availability, governance constraints:

## Candidates considered
- Baseline / minimal-change option:
- Candidate A:
- Candidate B:
- Other viable option(s):

## Decision
- Selected category and scope:
- Evidence linking access patterns to the selection:
- System of record and data owner:
- Derived copies, synchronization, and conflict/repair policy:

## Rejected alternatives
- Alternative:
- Specific reason it was rejected (target mismatch, integrity gap, cost, or operational risk):

## Assumptions and risks
- Quantified assumptions and unknowns:
- Failure modes and mitigations:
- Security, retention, deletion, and audit implications:

## Validation plan
- Representative dataset and workload:
- Correctness and failure tests:
- Metrics and acceptance criteria:
- Who runs/reviews the validation and when:

## Revisit triggers and exit plan
- Evidence that would change the decision:
- Conditions to add, replace, or retire a store:
- Migration/rollback approach:
```

A decision without a named system of record or a specific rejected alternative is incomplete. “Too complex” is not a reason; specify the concrete burden, such as needing a second on-call rotation, maintaining a change pipeline, or duplicating access-control rules.

## 7. Industry-application exercises

All scenarios and values in this section are illustrative. Complete the exercises before reading the answer guidance in Section 8.

### Exercise 1 — Twenty access patterns

Classify each operation by its **natural candidate category** and explain why. More than one category may be viable; where the operation is mixed, state which part dominates and what evidence could change your choice. Include a plausible poor fit for each item.

| # | Operation | Your classification and reason |
|---:|---|---|
| 1 | Retrieve a session using an exact session token | |
| 2 | Update a user's nested notification preferences as one aggregate | |
| 3 | Enforce uniqueness of an external payment reference while posting a ledger entry | |
| 4 | Join customers to accounts and filter on several changing business attributes | |
| 5 | List the latest 100 events for a known device within a time range | |
| 6 | Count metrics by service and five-minute interval over 90 days | |
| 7 | Search case documents for terms, then rank by relevance | |
| 8 | Find semantically similar text chunks to a query embedding | |
| 9 | Traverse accounts connected through shared devices and beneficiaries up to four hops | |
| 10 | Read an item by known immutable key with no filtering | |
| 11 | Retrieve a customer profile containing variable optional attributes | |
| 12 | Update a balance and append a ledger entry as one required atomic business operation | |
| 13 | Scan all orders for an ad hoc combination of customer, status, date, and amount | |
| 14 | Ingest a high rate of timestamped sensor readings and query by device/time range | |
| 15 | Retrieve records for a known partition key and ordered range of event time | |
| 16 | Filter documents by a field, then perform full-text relevance ranking | |
| 17 | Find nearest product embeddings and filter results by authorized tenant | |
| 18 | Maintain a short-lived response cache where recomputation from an authoritative store is possible | |
| 19 | Analyze relationships between people, addresses, phone numbers, and accounts | |
| 20 | Update a customer's current address while preserving the address used on historical orders | |

For each answer, do not simply write a category name. Identify the access pattern, correctness boundary, likely limitation, and one condition under which another category could be preferable.

### Exercise 2 — Profile six Northbridge workloads

For each workload below, produce an access-pattern list and select a category with a rejected alternative. The names are fictional and the values below are illustrative assumptions only.

1. **Account ledger:** posting entries, enforcing unique transaction references, retrieving entries by account/time, and preserving auditability.
2. **Customer profile:** retrieve/update a profile by customer ID, with optional attributes and relationships to accounts and contact points.
3. **Session store:** high-rate get/put/delete by session key with short retention; session data can be recreated or reauthenticated according to the application's policy.
4. **Fraud relationship network:** multi-hop traversal across accounts, devices, phone numbers, and beneficiaries.
5. **Document search:** search case notes and documents by terms, filters, and relevance ranking.
6. **Metric telemetry:** ingest timestamped service metrics and query time windows, aggregations, and retention/downsampling.

For each workload, document: entities and keys; top reads/writes; query frequency and expected peak; rows/items touched; transaction and consistency requirements; data horizon; governance constraints; candidate categories; baseline; rejected alternative; SoR owner; validation; revisit trigger.

### Exercise 3 — Customer-profile selection matrix

Compare at least three candidate categories **plus a separate baseline/minimal-change option** for the customer-profile workload (four options total when three distinct categories are viable). At minimum evaluate relational and document categories, plus a third plausible category selected from the access-pattern evidence; record the existing-store/minimal-change baseline separately. A key-value candidate is appropriate only if the access patterns are genuinely key-oriented. If a third category is not viable, state why rather than padding the comparison with an implausible candidate. State:

- the five most important access patterns;
- which relationships and integrity rules must be preserved;
- whether unplanned queries are likely;
- schema variability and validation approach;
- the specific reason for rejecting each alternative;
- the system of record and any derived copy ownership;
- operational skills, security, and TCO; and
- the test that would validate the choice.

### Exercise 4 — Quantification and sensitivity

Use the worked storage formula in Section 5.5. Then change one assumption at a time: item size from 3 KB to 6 KB; replication factor from 3 to 2; index overhead from 30% to 50%. Calculate the new estimate and explain why each change affects storage. Do not treat this estimate as a full production capacity plan.

### Exercise 5 — Graph proposal challenge

For the fraud-network scenario in Section 6.6, compare relational recursive queries, a graph store, and a precomputed projection. Define the test dataset, graph degree/skew cases, traversal depth, query frequency, response target, freshness requirement, correctness checks, staffing assumptions, and cost categories. Recommend one only after the evidence is specified. State what would make you add, reject, or retire the graph store.

### Exercise 6 — Cache failover incident

A service begins returning stale balances after a cache failover. Write a short incident analysis that distinguishes the authoritative balance from the cached copy. Identify the assumed durability and consistency properties, how stale values are detected, the safe fallback, and how cache invalidation/repopulation should be tested. Do not assume a cache is durable merely because it held the last observed value.

## 8. Practical scenarios and case-based reasoning

### 8.1 Scenario: “Use a document store because the account ledger schema changes often”

**Questions to ask before choosing:**

- Which fields change, how often, and are changes additive or do they alter the meaning of existing data?
- Is the ledger append-oriented? What uniqueness, ordering, audit, and correction rules apply?
- Does a posting require an atomic update across ledger entry, balance, and related state?
- Which reports and joins must work without advance planning?
- Can the selected candidate enforce the required invariants under concurrency and retry?
- Is schema evolution better handled through versioned records and compatibility rules without changing the primary data model?

**Reasoning:** variable fields alone do not justify a document store. A ledger's correctness and transaction boundaries may outweigh schema convenience. Consider a document category only if the full access pattern and correctness profile fit it, and prove the transaction semantics. A relational baseline is a serious candidate, not an automatic winner.

### 8.2 Scenario: Fraud analysts need chains of related accounts several hops deep

This is a relationship-traversal workload. Graph storage is a natural candidate because nodes and edges are the primary model. Relational recursive queries or precomputed relationship projections remain viable alternatives if the graph is modest, the traversal is bounded, the query rate is low, or the existing system meets the response target.

Test realistic degree distribution, including high-degree nodes; the average alone can hide expensive traversals. Define how quickly new edges must become visible and how missing or duplicate relationships are reconciled. A graph store should not silently become the authoritative owner of accounts or ledger entries unless the architecture explicitly assigns that ownership and the store meets the relevant requirements.

### 8.3 Scenario: A cache holds balances and serves stale values after failover

A cache is normally a performance aid, not proof of durable authoritative state. The failure may reflect eviction, asynchronous refresh, replication lag, failover behavior, invalidation loss, or a missing consistency check. The actual cause depends on the system and configuration; do not infer it from the category name.

The design should state:

- which store owns the authoritative balance;
- whether a read can use cached data and under what freshness condition;
- how invalidation, expiration, and repopulation work;
- what happens when the cache is unavailable or suspect; and
- which tests prove stale data cannot be used for a correctness-critical decision.

For a critical balance read, the safe behavior may be to consult the authoritative source or reject/slow the operation rather than return a known-stale value. That policy must follow business requirements and be tested.

### 8.4 Scenario: Northbridge customer profile

**Illustrative context:** a fictional team serves a customer-service screen that displays customer details, contact points, account summaries, and recent interactions. Some fields are optional and evolve over time. Staff may also ask unplanned questions about status, region, and linked accounts.

Possible candidates:

- **Relational baseline:** likely attractive when profile-to-account relationships, integrity, and changing filters matter. A read model or view can optimize the common screen if measurements require it.
- **Document category:** potentially attractive if the profile is a cohesive aggregate, most reads retrieve it as a unit, fields vary substantially, and cross-document integrity is not the dominant need. Relationships to accounts may still require additional queries or duplication.
- **Key-value category:** potentially attractive for a precomputed profile blob accessed only by exact key, but less suitable if the team needs ad hoc filtering and joins. It may be a derived cache, not the source of truth.

**Recommended method:** do not pick a winner from this description alone. Inventory the five most frequent reads and updates, identify whether the customer-service screen needs a consistent point-in-time view, measure profile size and update rate, and test candidates. A defensible baseline might remain relational until evidence shows a specific target is missed. If a document projection is introduced, keep a named SoR for customer identity and define how profile changes, deletes, and access controls propagate.

### 8.5 Scenario: Small workload versus a specialized store

An internal team asks for a vector store to find similar paragraphs in a small document collection. First compare a minimal-change baseline that performs an acceptable scan or uses an existing search capability with a vector candidate. If the collection is small, latency targets are relaxed, and the workload is infrequent, a separate store may not justify its operational and governance cost. If semantic retrieval is central, the collection grows, and representative tests show the baseline misses the target, a vector store may be justified.

The decision should consider embedding generation and versioning, update/deletion propagation, tenant filtering, evaluation of retrieval quality, and on-call ownership—not only similarity-query speed.

### 8.6 Reusable recommendation framework

For any workload, complete this sequence:

1. **Requirement:** What business outcome is needed, and what would count as failure?
2. **Workload:** List reads, writes, keys, filters, ranges, order, frequency, concurrency, response targets, and data horizon.
3. **Correctness:** Define invariants, transaction boundary, stale-read tolerance, deletion, and recovery needs.
4. **Constraints:** Security, privacy, residency, availability, budget, skills, and dependencies.
5. **Candidates:** Baseline/minimal-change plus at least two viable alternatives where meaningful.
6. **Quantification:** Estimate data size, rate, replicas, indexes, and growth with units and assumptions.
7. **Comparison:** Evaluate access fit, query flexibility, integrity, scale, operational burden, and TCO.
8. **Decision:** Choose the simplest category that meets the evidence-backed requirements; name a rejected alternative with a specific reason.
9. **Ownership:** Name the system of record, owners, derived-copy policy, and repair path.
10. **Validation:** Define representative workload, correctness/failure tests, metrics, and acceptance criteria.
11. **Revisit trigger:** State the measurable change that would make you reconsider the choice.

### 8.7 Lightweight validation and measurement plan

A selection matrix is a hypothesis. Validate it with:

- a representative dataset and realistic data distribution, including skew;
- the top read/write patterns, not only a convenient demo query;
- expected average and peak concurrency where known;
- correctness tests for uniqueness, transaction boundaries, retries, and stale reads;
- failure tests for node/replica loss, timeout, retry, and recovery where relevant;
- storage and index-growth measurements;
- operational tests such as backup/restore or rebuilding a derived index;
- security tests for authorization and tenant isolation; and
- a cost model including compute, storage, network transfer, migration, people, support, monitoring, and incident response.

Record unknowns rather than inventing precision. If no representative test has been run, label the result a proposed architecture, not a validated one.

### 8.8 Exercise answer guidance and quantitative cross-checks

These are defensible starting points, not universal winners. A different answer can earn full credit if it fits the stated access pattern, names its assumptions, explains the rejected alternative, and identifies validation evidence.

**Exercise 1 — Twenty access patterns: natural candidates and key caveats**

| # | Natural candidate | Reasoning and a plausible poor fit |
|---:|---|---|
| 1 | Key-value | Exact-token lookup is a direct key access; a graph store adds unnecessary relationship machinery. Confirm expiry, revocation, and durability requirements. |
| 2 | Document | A cohesive nested aggregate may be read/updated as one unit; a key-value value may make attribute-level querying awkward. Relational remains viable if integrity and joins dominate. |
| 3 | Relational baseline | Uniqueness and ledger posting correctness are central; a simple key-value store may not enforce the required multi-record invariant. Verify the exact transaction boundary and retry behavior. |
| 4 | Relational | Multiple changing filters, joins, and query flexibility fit a relational baseline; a key-value store is a poor fit without precomputed access paths. |
| 5 | Wide-column or time-series | Known device plus ordered time range is a natural time-oriented access pattern; graph traversal is unnecessary. Choose based on aggregation, retention, and query requirements. |
| 6 | Time-series or analytical relational/warehouse path | Long-window time-bucket aggregation is the key pattern; a key-value store cannot naturally answer broad aggregates without a separate process. Test cardinality and retention costs. |
| 7 | Search | Term matching plus relevance ranking is full-text search; a plain relational filter may be inadequate if relevance and scale targets are demonstrated, though it can be the baseline. |
| 8 | Vector | Similarity to an embedding is the defining access pattern; a relational point lookup does not by itself provide nearest-neighbor search. Validate retrieval quality and authorization filters. |
| 9 | Graph, with relational recursive query as baseline | Multi-hop relationship traversal is central; key-value lookups require application-managed traversal. Measure graph size, degree skew, depth, and freshness. |
| 10 | Key-value or relational primary-key lookup | Known-key retrieval is simple; a graph store is likely unnecessary unless surrounding relationship queries matter. |
| 11 | Document or relational | Variable optional attributes favor a document hypothesis only if the aggregate and query profile fit; a key-value-only design may hinder filters. Test schema governance and joins. |
| 12 | Relational or another candidate with verified atomic support | The requirement is an atomic balance/ledger boundary, not a category label. A system lacking that boundary is a poor fit unless the business design changes. |
| 13 | Relational/analytical query engine depending on volume and freshness | Ad hoc combinations of filters favor query flexibility; a query-shaped key-value model would need many precomputed paths. State whether this is operational or analytical. |
| 14 | Time-series or wide-column | Timestamped ingest and device/time range are natural; a graph store is not justified by this access pattern alone. Test late data, aggregation, and retention. |
| 15 | Wide-column or relational with suitable index/layout | Known partition key plus ordered range is the core access path; a document or key-value store may be awkward if ordered range retrieval is not supported efficiently. |
| 16 | Search plus source-of-record lookup, or a relational baseline if sufficient | Full-text ranking plus field filter suggests search; do not treat a derived index as authoritative without explicit justification. Validate deletion and authorization propagation. |
| 17 | Vector plus enforced tenant/authorization filtering | Similarity and tenant filtering are both requirements; an unfiltered nearest-neighbor result is unsafe. Verify filtering semantics and retrieval quality. |
| 18 | Cache/key-value | Short-lived recomputable responses are cache-shaped; a durable ledger database is an unnecessarily costly cache unless it already meets the need. Define invalidation and fallback. |
| 19 | Graph, with relational baseline if traversals are bounded | Many entity types linked by relationships suggests graph traversal; a simple key-value store shifts traversal and consistency burden to application code. |
| 20 | Relational plus explicit historical snapshot semantics, or equivalent model | Current address and historical order address have different meanings. Overwriting all historical copies is wrong if the order must preserve the address used at purchase; denormalization is valid when semantics are explicit. |

**Exercise 2 — Six workload profiles:** a defensible initial hypothesis is relational for the account ledger; relational or document for customer profile depending on joins and query flexibility; key-value for short-lived sessions; graph or relational recursive queries for fraud relationships depending on measured traversal performance; search for full-text document retrieval; and time-series or wide-column for metric telemetry. These are hypotheses only. Each profile must still name the baseline, rejected alternative, SoR owner, correctness/freshness requirements, validation test, and revisit trigger.

**Exercise 3 — Customer-profile matrix:** include the current/minimal-change baseline and at least three plausible category candidates when available. Do not assign a winner without access-pattern evidence. The comparison should identify (a) top queries/updates, (b) relationships and integrity rules, (c) unplanned-query need, (d) schema validation, (e) operational/TCO burden, (f) SoR and derived-copy ownership, and (g) measurable acceptance criteria. Reject candidates for specific mismatches, not category stereotypes.

**Exercise 4 — Quantification and sensitivity:** use the baseline assumptions from Section 5.5: 20,000,000 entities, 3,000 bytes/entity, replication factor 3 total copies, and index overhead applied as a 1.30 multiplier to replicated data.

- Baseline: `20,000,000 × 3,000 bytes = 60,000,000,000 bytes = 60 GB`; `60 GB × 3 = 180 GB`; `180 GB × 1.30 = 234 GB` (decimal).
- Item size increases to 6,000 bytes/entity, other assumptions unchanged: `20,000,000 × 6,000 = 120,000,000,000 bytes = 120 GB`; `120 × 3 × 1.30 = 468 GB`.
- Replication factor decreases to 2 total copies, original 3,000-byte items and 30% index overhead: `60 GB × 2 × 1.30 = 156 GB`.
- Index overhead increases to 50%, original 3,000-byte items and 3 total copies: `60 GB × 3 × 1.50 = 270 GB`.

Each variation changes only one baseline assumption. These are simplified decimal estimates and exclude unmodelled logs, snapshots, backup copies, compression effects, and other metadata. Do not combine the changed assumptions unless the question explicitly asks for a combined scenario.

**Exercise 5 — Graph proposal:** compare a relational recursive-query baseline, graph store, and precomputed projection using the same representative dataset and query set. Include high-degree/skew cases, traversal depth, write-to-read freshness, correctness of edge creation/deletion, rebuild/reconciliation, latency distribution, storage, synchronization, staffing, and incident response. Add a graph store only if it measurably meets a requirement the baseline misses at acceptable total cost; revisit it if traversal demand, freshness, scale, or measured performance changes materially.

**Exercise 6 — Cache failover:** identify the authoritative store; establish whether the cache can lose or serve stale entries; inspect invalidation, expiration, refresh, and failover semantics; define a safe fallback for correctness-critical balance reads; and test concurrent updates, retries, cache loss, and repopulation. Do not infer the cause without evidence or promote a cache to system of record by assumption.

## 9. Expected outputs and deliverables

Complete these artifacts for the lesson:

1. **Category cards** for relational, key-value, document, wide-column, graph, search, time-series, and vector categories. Each card must state model, natural access pattern, strengths, limitations, consistency/transaction questions to verify, operating burden, and poor-fit example.
2. **Access-pattern inventory** for the workload being evaluated, including keys, filters, ranges, sort order, frequency, response target, write semantics, data horizon, and correctness needs.
3. **Selection matrix** with a current/minimal-change baseline plus at least three distinct candidate categories where viable, as required by the Topic 2 exercise. Every candidate must be linked to evidence and include a specific rejection reason for alternatives; if a category is not viable, record the reason rather than adding a straw candidate.
4. **Quantitative worksheet** with units, formula, assumptions, checked arithmetic, sensitivity, and explicit limits of the estimate.
5. **ADR** using Section 6.8, including selected category, system-of-record ownership, assumptions, risks, validation, and revisit triggers.
6. **Practice-question answers** with corrected reasoning, not only category labels.

## 10. Common mistakes and misconceptions

- **“NoSQL is one database type.”** It is a family. Key-value, document, wide-column, and graph systems solve different access problems.
- **“One category is always faster.”** Performance depends on data model, query shape, data distribution, implementation, configuration, concurrency, and measurement.
- **“Select the database first, then design queries around it.”** This reverses the roadmap's required sequence. List important access patterns first.
- **“A flexible schema means a document store is automatically right.”** Schema flexibility does not resolve transaction, relationship, query, or governance requirements.
- **“Relational systems are only for small datasets.”** This is an unsupported blanket claim. Evaluate actual candidate capacity and access patterns.
- **“Denormalization is always faster and therefore better.”** It can reduce read work but increase storage, write amplification, divergence, and repair complexity.
- **“Application-managed joins are free.”** They add network calls, partial-failure handling, code duplication, and consistency questions.
- **“The category guarantees a particular consistency model.”** Transaction and consistency capabilities vary by system and configuration; verify the exact guarantee.
- **“A cache is durable because it contains data.”** Caching, eviction, failover, and persistence behavior must be understood; a cache is not automatically the system of record.
- **“A search or vector index can replace the source of truth.”** Derived indexes may lag, omit updates, or have different query semantics. Define authority and reconciliation.
- **“More partitions means more capacity automatically.”** Skew, hot keys, coordination, and cross-partition operations can limit scale.
- **“Average writes per partition is a guarantee.”** It assumes uniform distribution; measure and test the hottest partition.
- **“An extra store only costs infrastructure.”** It also costs people, security controls, data movement, monitoring, incident response, and ownership.
- **“Too complex” is enough to reject an alternative.** Name the specific operational or correctness burden and its impact.
- **“A category choice is complete without a rejected alternative.”** A defensible decision explains why another viable option is worse for this workload.
- **“A store can own the same fact as another store without a rule.”** Every core entity needs explicit authoritative ownership and a defined repair/conflict policy for derived copies.

## 11. Mastery criteria

You have mastered this topic when you can demonstrate all of the following without relying on memorized slogans:

- Explain relational, key-value, document, wide-column, graph, search, time-series, and vector categories, including their natural access patterns and typical limitations.
- Extract and list important queries and updates before naming a candidate category.
- Build workload profiles with keys, filters, ranges, sort order, rate, concurrency, response target, data horizon, and correctness requirements.
- Explain normalized versus query-shaped modeling and identify the cost of duplicated facts and application-managed joins.
- Compare candidates using transaction/consistency behavior, query flexibility, schema variability, scale, availability, governance, skills, and TCO.
- Reproduce the storage estimate with correct units and arithmetic, state replication/index assumptions, and explain why partition-rate division depends on uniform keys.
- Compare a baseline and at least two viable alternatives, with a specific reason for rejecting each alternative.
- Justify any specialized or additional store with representative workload evidence and a polyglot-ownership plan.
- Identify the system of record for each core entity and explain how derived copies are synchronized, repaired, protected, and retired.
- Produce an ADR and validation plan that another reviewer can challenge and reproduce.

A strong answer may choose a general-purpose relational system, a NoSQL category, a specialized store, or a multi-store design. The score comes from the evidence and trade-offs, not from which category is selected.

## 12. Completion gate

Do not mark Topic 2 complete until every item below is satisfied.

- [ ] Category cards are complete for relational, key-value, document, wide-column, graph, search, time-series, and vector categories.
- [ ] The twenty-operation exercise is answered, with reasons, poor-fit alternatives, and corrected mistakes.
- [ ] Six Northbridge workloads have access-pattern lists and category recommendations: account ledger, customer profile, session store, fraud relationship network, document search, and metric telemetry.
- [ ] The customer-profile selection matrix includes a separate baseline/minimal-change option plus at least three distinct candidate categories where viable, evidence for each row, and a specific rejected-alternative reason for each selection; any infeasible category is explicitly ruled out with a reason.
- [ ] Quantitative calculations include units, assumptions, independently checked arithmetic, and an explanation of the uniform-key limitation.
- [ ] The graph-store proposal compares relational recursive queries, graph storage, and/or a precomputed projection, with explicit validation and revisit conditions.
- [ ] System-of-record ownership is stated for every core entity; derived copies have defined ownership, synchronization, security, and repair behavior.
- [ ] The ADR includes context, candidates, decision, rejected alternatives, assumptions, risks, validation plan, and revisit/exit triggers.
- [ ] Practice questions are answered and corrected; no category is selected solely from popularity or familiarity.

**Final gate question:** Can another architect trace each category recommendation back to a named access pattern, correctness requirement, quantified assumption, operating-cost trade-off, rejected alternative, and validation test? If not, the decision is not yet defensible.
