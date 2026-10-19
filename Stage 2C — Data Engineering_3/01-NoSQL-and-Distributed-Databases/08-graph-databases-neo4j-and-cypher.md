# Graph Databases: Neo4j and Cypher

**Stage 2C — Data Engineering_3 · Topic 08**  
**Target path:** `Stage 2C — Data Engineering_3/01-NoSQL-and-Distributed-Databases/08-graph-databases-neo4j-and-cypher.md`

> **Version note:** Examples use modern Neo4j 5.x-style Cypher and the Neo4j Python driver. Graph Data Science (GDS) is a separate library/product capability; procedures, syntax, and availability depend on the installed version and edition. Verify examples against the version you run. No runtime, profiling, or algorithm measurements are claimed here.

## 1. Learning objectives

By the end of this lesson, you should be able to:

- Explain nodes, labels, relationships, relationship types, and properties in the property graph model.
- Explain graph traversal, index-free adjacency, and when a graph is or is not a better fit than relational joins.
- Write Cypher with `MATCH`, `WHERE`, `RETURN`, `CREATE`, `MERGE`, `SET`, `DELETE`, `LIMIT`, variable-length paths, `OPTIONAL MATCH`, `WITH`, aggregation, and `UNWIND`.
- Model customers, accounts, devices, and transactions without creating unnecessary nodes or dangerous super nodes.
- Use constraints, indexes, `EXPLAIN`, and `PROFILE` to reason about query plans.
- Load data using `LOAD CSV`, batched `UNWIND`, and the Python driver with idempotent `MERGE`.
- Understand PageRank, community detection, similarity, and path-finding at an introductory level.
- Explain Neo4j scaling trade-offs, alternatives, RDF/SPARQL, GraphRAG, and graph-to-lakehouse export.

## 2. Prerequisites and module position

This topic follows NoSQL families and consistency, MongoDB, Cassandra, DynamoDB, Redis, and Elasticsearch/OpenSearch. Topic 09 continues with reliable NoSQL-to-lakehouse ingestion. The module roadmap positions Neo4j as a specialised store for relationship-centric questions—not a replacement for every relational or analytical workload.

Expected prerequisites: Python and JSON, SQL joins and grouping, transactions, nested data, batch versus streaming, Docker Compose, stable identifiers, idempotency, and basic incremental data movement.

## 3. Graph fundamentals

### 3.1 The property graph model

A **property graph** consists of:

- **Node:** an entity, such as a customer, account, or device.
- **Label:** a node category such as `:Customer` or `:Account`; nodes can have multiple labels.
- **Relationship:** a directed connection between two nodes.
- **Relationship type:** the meaning of a connection, such as `:OWNS`, `:USES`, or `:TRANSFERRED_TO`.
- **Property:** a key/value attribute on a node or relationship, such as `customer_id`, `status`, `amount`, or `occurred_at`.

Example:

```text
(:Customer {customer_id: "C101"})
       -[:OWNS {since: date("2024-02-01")}]->
(:Account {account_id: "A501", status: "active"})

(:Customer {customer_id: "C101"})-[:USES]->
(:Device {device_id: "D77", device_type: "mobile"})

(:Account {account_id: "A501"})
       -[:TRANSFERRED_TO {transfer_id: "T900", amount: 750.0,
                          occurred_at: datetime("2025-01-02T10:00:00Z")}]->
(:Account {account_id: "A502"})
```

Arrows matter. `(:Customer)-[:OWNS]->(:Account)` is not the same directed pattern as the reverse. A query can match a specific direction or intentionally match either direction.

### 3.2 Customers–accounts–devices–transactions domain

Use this consistent domain throughout the lesson:

```text
(Customer)-[:OWNS]->(Account)
(Customer)-[:USES]->(Device)
(Account)-[:TRANSFERRED_TO {transfer_id, amount, occurred_at}]->(Account)
```

Questions naturally expressed as traversals include: which accounts are connected to a known fraudster through shared devices; which customers share a device; what is the shortest relationship path between accounts; which devices bridge customer groups; and which connected entities interacted shortly before a suspicious transfer.

### 3.3 Node, relationship, or property?

Use a **node** when an entity has independent identity, lifecycle, or relationships. Customers, accounts, and devices usually qualify. Use a **relationship** when information primarily describes a connection between two entities. Use a **property** when the value describes one entity or relationship and does not need independent connections.

A transfer can be a relationship when it is a simple event between two accounts. Model it as a `(:Transfer)` node when it needs its own identity, multiple links (authorization, settlement, dispute, payment rail), audit history, or lifecycle. The correct choice follows access patterns and lifecycle requirements; not all events must be relationships.

### 3.4 Traversal versus relational joins

A relational schema can store `customers`, `accounts`, `devices`, and `transfers` with foreign keys. One-hop joins may be straightforward. Variable-depth connectivity may require repeated self-joins, recursive CTEs, or application iteration. Cypher expresses the connected pattern directly:

```cypher
MATCH (known:Customer {customer_id: $customer_id})-[:USES]->(d:Device)
      <-[:USES]-(other:Customer)-[:OWNS]->(a:Account)
RETURN DISTINCT other.customer_id, a.account_id;
```

**Index-free adjacency** means that once the engine reaches a node, its relationships directly connect it to neighbors; the engine need not perform a fresh global foreign-key join for every hop. It does not mean every query is constant-time or that indexes are unnecessary. Finding the starting node, filtering large neighborhoods, expanding many edges, sorting, aggregating, and returning large result sets can still be expensive.

Choose a graph when multi-hop connectivity is central and relationship-rich. Prefer relational tables when the workload is mainly tabular aggregation, a small fixed set of joins, conventional reporting, or relational constraints. The systems can coexist.

## 4. Neo4j architecture and local setup

- **Database:** a logical graph namespace containing nodes, relationships, schema, and transactions.
- **Instance/server:** a process or deployment hosting databases.
- **Cluster:** multiple servers providing availability and, depending on topology, some read scaling.
- **Cypher:** declarative graph query language.
- **Bolt:** protocol used by drivers.
- **Neo4j Browser/Workspace:** interactive query and exploration tools; UI varies by release.
- **Python driver:** official driver for parameterized Cypher.
- **Graph Data Science (GDS):** optional library for graph projections and algorithms; not the same as core Cypher.

Create `experiments/08_neo4j/docker-compose.yml`:

```yaml
services:
  neo4j:
    image: neo4j:5
    container_name: neo4j-lab
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/replace-with-a-local-lab-password
      NEO4J_server_memory_heap_initial__size: 512m
      NEO4J_server_memory_heap_max__size: 1G
      # Optional for a disposable local lab only; downloads a compatible plugin at startup.
      NEO4J_PLUGINS: '["graph-data-science"]'
    volumes:
      - ./data:/data
```

Run:

```bash
mkdir -p experiments/08_neo4j/data
cd experiments/08_neo4j
docker compose up -d
docker compose logs -f neo4j
```

Open `http://localhost:7474` and sign in with the configured lab credentials. Bolt is at `bolt://localhost:7687`. The optional `NEO4J_PLUGINS` setting asks the development image's plugin installer to download Graph Data Science; it requires network access and is not a production plugin-management strategy. If you omit it, install a GDS version compatible with the Neo4j server and edition before running Section 11. GDS procedures are not available just because the core database is running. This is a learning setup, not a production security template. Do not expose it to untrusted networks or commit credentials. Pin an image tag/digest and compatible plugin version for reproducibility; use a secret manager in production.

## 5. Cypher fundamentals

### 5.1 Pattern notation

- `()` matches a node.
- `(c:Customer)` matches a `Customer` node and binds it to `c`.
- `[:OWNS]` matches a relationship type.
- `-[r:TRANSFERRED_TO]->` binds a directed relationship to `r`.
- `{customer_id: $id}` is a property map using parameter `$id`.
- `--` matches an unspecified relationship; use only when broad direction/type matching is intended.

### 5.2 Create nodes and relationships

```cypher
CREATE (:Customer {customer_id: "C101", name: "Asha"});
CREATE (:Account {account_id: "A501", status: "active"});

MATCH (c:Customer {customer_id: "C101"}),
      (a:Account {account_id: "A501"})
CREATE (c)-[:OWNS {since: date("2024-02-01")}]->(a);
```

`CREATE` creates new graph elements every time it runs. Re-running statements can create duplicates. Use stable keys, uniqueness constraints, and `MERGE` for replayable ingestion.

### 5.3 Match, filter, return, limit

```cypher
MATCH (c:Customer)-[:OWNS]->(a:Account)
WHERE a.status = "active"
RETURN c.customer_id AS customer_id, a.account_id AS account_id
ORDER BY customer_id, account_id
LIMIT 50;
```

Return only fields required by the caller. Returning entire nodes or large paths can use excessive memory and network bandwidth.

### 5.4 Update with `SET`

```cypher
MATCH (a:Account {account_id: $account_id})
SET a.status = $status,
    a.updated_at = datetime()
RETURN a.account_id, a.status, a.updated_at;
```

Parameterize user input instead of concatenating strings into Cypher. Parameters reduce injection risk and can help plan reuse.

### 5.5 Delete carefully

Delete a relationship without deleting its endpoints:

```cypher
MATCH (c:Customer {customer_id: $customer_id})-[r:USES]->(d:Device {device_id: $device_id})
DELETE r;
```

A node can be deleted with `DELETE` only when it has no relationships. `DETACH DELETE` also deletes all attached relationships and is destructive:

```cypher
MATCH (d:Device {device_id: $device_id})
DETACH DELETE d;
```

### 5.6 `MERGE` and idempotency

`MERGE` matches a pattern if it exists or creates it otherwise. Use stable identity keys; avoid merging an entity by mutable properties such as name or status.

```cypher
MERGE (c:Customer {customer_id: $customer_id})
ON CREATE SET c.created_at = datetime()
SET c.name = $name,
    c.updated_at = datetime();
```

For a transfer relationship:

```cypher
MATCH (source:Account {account_id: $source_id})
MATCH (target:Account {account_id: $target_id})
MERGE (source)-[t:TRANSFERRED_TO {transfer_id: $transfer_id}]->(target)
ON CREATE SET t.created_at = datetime()
SET t.amount = $amount,
    t.occurred_at = datetime($occurred_at);
```

This is replay-safe for the intended relationship identity only if `transfer_id` is stable, non-null, and unique for the ordered `(source, target)` pair, and endpoint matches are unambiguous. Replaying this statement may update `amount` and `occurred_at`; it is structurally idempotent, not an immutable event-ingestion contract. If a transfer ID must be globally unique independent of endpoints, enforce that identity with a `(:Transfer {transfer_id})` node and a uniqueness constraint, then connect source/target accounts to that event node. Create node uniqueness constraints before concurrent `MERGE` loads; `MERGE` without a uniqueness constraint does not guarantee uniqueness for node identities under every concurrent ingestion pattern.

### 5.7 Aggregation

```cypher
MATCH (c:Customer)-[:OWNS]->(a:Account)
RETURN c.customer_id, count(DISTINCT a) AS account_count
ORDER BY account_count DESC;
```

`count(*)` counts matched rows; `count(x)` ignores null; `count(DISTINCT x)` counts distinct values. `DISTINCT` is useful when a pattern produces duplicate rows, but it has a cost and should not hide a modelling mistake.

## 6. Constraints and indexes

Constraints protect data integrity; indexes help find starting points. Example Neo4j 5.x uniqueness constraints:

```cypher
CREATE CONSTRAINT customer_id_unique IF NOT EXISTS
FOR (c:Customer) REQUIRE c.customer_id IS UNIQUE;
CREATE CONSTRAINT account_id_unique IF NOT EXISTS
FOR (a:Account) REQUIRE a.account_id IS UNIQUE;
CREATE CONSTRAINT device_id_unique IF NOT EXISTS
FOR (d:Device) REQUIRE d.device_id IS UNIQUE;
```

Constraint syntax and available types vary by release and edition. A uniqueness constraint commonly has a backing index useful for lookups by that property.

Example range index:

```cypher
CREATE INDEX account_status_idx IF NOT EXISTS
FOR (a:Account) ON (a.status);
SHOW CONSTRAINTS;
SHOW INDEXES;
```

A low-selectivity property such as a status with only two values may not be a useful standalone index. A unique ID lookup is often a stronger candidate. Full-text and vector indexes are separate capabilities; their syntax and availability are version/edition-dependent.

Neo4j is schema-optional, but production data still needs naming discipline. Keep labels and property names stable, validate source data, and avoid creating a new label/property for every arbitrary source field.

## 7. Intermediate traversal patterns

### 7.1 Variable-length paths

```cypher
MATCH p = (start:Account {account_id: $start_id})
          -[:TRANSFERRED_TO*1..3]->(end:Account)
RETURN end.account_id AS reached_account, length(p) AS hops
ORDER BY hops, reached_account
LIMIT 100;
```

`*1..3` means one to three relationship hops. Expansion can grow quickly with branching factor and depth. Bound the maximum depth, filter the start node, and return only necessary fields. Path uniqueness and matching semantics matter; do not assume every possible walk with repeated edges is enumerated.

### 7.2 Three-hop fraud investigation using shared devices

The business path is exactly three relationships: known customer → device, device ← another customer, other customer → account.

```cypher
MATCH p = (fraudster:Customer {customer_id: $fraudster_id})
          -[:USES]->(d:Device)
          <-[:USES]-(other:Customer)-[:OWNS]->(a:Account)
WHERE other.customer_id <> fraudster.customer_id
RETURN DISTINCT a.account_id AS candidate_account,
       other.customer_id AS related_customer,
       collect(DISTINCT d.device_id) AS shared_devices
ORDER BY candidate_account
LIMIT 200;
```

This explicit pattern is preferable to an unrestricted `*1..3` pattern for this business rule because it encodes the intended semantics. Shared-device evidence is a lead for investigation, not proof of fraud.

A broad bounded traversal can be useful for exploration but is semantically weaker:

```cypher
MATCH p = (fraudster:Customer {customer_id: $fraudster_id})
          -[:USES|OWNS|TRANSFERRED_TO*1..3]-(candidate)
RETURN DISTINCT labels(candidate) AS labels,
       candidate.customer_id AS customer_id,
       candidate.account_id AS account_id,
       min(length(p)) AS min_hops
ORDER BY min_hops
LIMIT 100;
```

This may return different node types and irrelevant connections. Whitelist valid relationship/node combinations and avoid exposing unnecessary sensitive data.

### 7.3 Shortest path

```cypher
MATCH (a:Account {account_id: $source_id}),
      (b:Account {account_id: $target_id})
MATCH p = shortestPath((a)-[:TRANSFERRED_TO*..8]-(b))
RETURN [n IN nodes(p) | n.account_id] AS accounts_on_path,
       length(p) AS hops;
```

This matches transfer relationships in either direction. Use directed arrows when direction is part of the business rule. Fewest hops is not necessarily lowest-risk, lowest-cost, or earliest path. Weighted paths require suitable relationship weights and algorithm support; verify the target version's syntax.

### 7.4 `OPTIONAL MATCH`

`OPTIONAL MATCH` behaves like an outer match; if the pattern is absent, newly introduced variables are null.

```cypher
MATCH (c:Customer {customer_id: $customer_id})
OPTIONAL MATCH (c)-[:USES]->(d:Device)
RETURN c.customer_id, collect(DISTINCT d.device_id) AS device_ids;
```

A `WHERE` attached to an `OPTIONAL MATCH` constrains that optional pattern. A later filter can remove rows whose optional values are null; understand scope and placement.

### 7.5 `WITH` for query stages

```cypher
MATCH (c:Customer)-[:USES]->(d:Device)
WITH d, count(DISTINCT c) AS customer_count
WHERE customer_count >= 3
RETURN d.device_id, customer_count
ORDER BY customer_count DESC;
```

`WITH` passes selected variables to the next stage. Variables not carried through it leave scope. It is useful for aggregation, filtering intermediate results, and controlling row counts.

### 7.6 `UNWIND`

`UNWIND` converts a list into rows, useful for batched loading:

```cypher
UNWIND $rows AS row
MERGE (c:Customer {customer_id: row.customer_id})
SET c.name = row.name;
```

Batch size is a workload parameter. Very large transactions increase memory usage and transaction duration; tune based on actual observations.

### 7.7 Four-hop SQL self-join to Cypher

SQL example:

```sql
SELECT DISTINCT t4.target_account_id
FROM transfers t1
JOIN transfers t2 ON t2.source_account_id = t1.target_account_id
JOIN transfers t3 ON t3.source_account_id = t2.target_account_id
JOIN transfers t4 ON t4.source_account_id = t3.target_account_id
WHERE t1.source_account_id = :source_account_id;
```

Equivalent Cypher pattern:

```cypher
MATCH (start:Account {account_id: $source_account_id})
      -[:TRANSFERRED_TO]->()
      -[:TRANSFERRED_TO]->()
      -[:TRANSFERRED_TO]->()
      -[:TRANSFERRED_TO]->(target:Account)
RETURN DISTINCT target.account_id AS target_account_id;
```

This preserves four directed hops. If the SQL includes date, amount, or status filters, include those predicates in the Cypher translation too. This is a readability comparison, not a claim that graph queries are always faster.

## 8. Production graph modelling

### 8.1 Avoid super nodes

A **super node** has an unusually high degree, such as a device connected to millions of events. Traversing through it can produce a huge candidate set and dominate query cost.

Mitigations:

- Avoid connecting all unrelated entities to a generic global node just to make them reachable.
- Model event nodes or time buckets when they reflect real domain semantics.
- Filter from indexed starting nodes before traversal.
- Bound variable-length paths and return limited projections.
- Detect high-degree hubs and design specific query rules for them.
- For analytics, consider a filtered GDS projection or batch processing instead of interactive traversal through a massive neighborhood.

Do not split a genuine high-degree entity into fake entities without preserving semantics. If a device really is shared, represent it honestly and design queries around its degree.

### 8.2 Modelling time and events

When transfer identity and lifecycle matter, use a transfer node:

```text
(Account)-[:SENT]->(Transfer {transfer_id, amount, occurred_at, status})
(Transfer)-[:RECEIVED_BY]->(Account)
```

This allows a unique event constraint and additional links to authorization, dispute, channel, or source record, at the cost of extra nodes and relationships. Store timestamps consistently in UTC and document whether event time, processing time, or source update time is used.

### 8.3 Relationship duplication and concurrency

Use stable identifiers and uniqueness constraints before parallel ingestion. If the model needs globally unique transfer IDs, a `Transfer` node with a unique key is often clearer than trying to enforce uniqueness on a relationship property. A retry may commit even if the client loses the response; idempotent operations are essential.

### 8.4 Privacy and access

Graph traversals can reveal sensitive indirect relationships. Use least-privilege roles, parameterized queries, retention policies, and selective projections. A relationship can be as sensitive as a node property.

## 9. Query tuning: `EXPLAIN` and `PROFILE`

- `EXPLAIN` plans a query without executing it.
- `PROFILE` executes the query and returns operator-level statistics such as rows and database hits, depending on version.
- Profiling a write query may perform writes. Use disposable data or a controlled rollback strategy.
- Profile numbers describe that run and environment; they are not universal benchmarks.

```cypher
EXPLAIN
MATCH (a:Account {account_id: $account_id})-[:TRANSFERRED_TO]->(b:Account)
RETURN b.account_id;

PROFILE
MATCH (a:Account {account_id: $account_id})-[:TRANSFERRED_TO]->(b:Account)
RETURN b.account_id;
```

Inspect:

- Index seek versus broad label scan for selective predicates.
- Estimated versus actual rows.
- Relationship expansion and rows produced at each step.
- Filters applied late, large intermediate results, sorts, aggregations, or Cartesian products.
- Database hits and total work, not only wall-clock latency.

For a fair index comparison, use the same dataset, query, parameters, cache state, and environment. Create or remove only the relevant index, wait until it is online, warm up, run repeated trials, and record median and spread. Do not drop a required uniqueness constraint just to manufacture a no-index case; use a non-unique property or an isolated test database. An index may not help if traversal dominates cost.

## 10. Loading data

### 10.1 `LOAD CSV`

Place `customers.csv` in Neo4j's configured import directory:

```csv
customer_id,name
C101,Asha
C102,Ravi
C103,Mina
```

Load it idempotently:

```cypher
LOAD CSV WITH HEADERS FROM 'file:///customers.csv' AS row
MERGE (c:Customer {customer_id: row.customer_id})
SET c.name = row.name;
```

For larger files, use supported transactional batching syntax or the Python driver. Example syntax for a compatible Neo4j 5.x release:

```cypher
LOAD CSV WITH HEADERS FROM 'file:///customers.csv' AS row
CALL {
  WITH row
  MERGE (c:Customer {customer_id: row.customer_id})
  SET c.name = row.name
} IN TRANSACTIONS OF 1000 ROWS;
```

This commits batches rather than one all-or-nothing transaction for the full file. Earlier batches remain committed if a later batch fails. Run `CALL { ... } IN TRANSACTIONS` as an implicit/auto-commit query; it cannot be nested inside an already-open explicit transaction such as a normal `execute_write` callback. Local file access and URL import are controlled by server settings; do not enable arbitrary imports in production without security review.

### 10.2 Python driver

Install dependencies:

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install "neo4j>=5,<6" pandas pyarrow
```

Set credentials via environment variables:

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="replace-with-your-lab-password"
export NEO4J_DATABASE="neo4j"
```

Example loader:

```python
import os
from neo4j import GraphDatabase

URI = os.environ["NEO4J_URI"]
AUTH = (os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"])
DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

def load_customers(tx, rows):
    result = tx.run(
        """
        UNWIND $rows AS row
        MERGE (c:Customer {customer_id: row.customer_id})
        SET c.name = row.name,
            c.updated_at = datetime()
        RETURN count(c) AS processed
        """,
        rows=rows,
    )
    return result.single()["processed"]

driver = GraphDatabase.driver(URI, auth=AUTH)
rows = [
    {"customer_id": "C101", "name": "Asha"},
    {"customer_id": "C102", "name": "Ravi"},
]
try:
    with driver.session(database=DATABASE) as session:
        processed = session.execute_write(load_customers, rows)
        print(f"Rows processed: {processed}")
finally:
    driver.close()
```

The count is rows processed, not necessarily newly created nodes. `MERGE` provides stable identity; `SET` updates the name every run. Use `ON CREATE SET` if initialization should happen only once. In concurrent loads, uniqueness constraints are essential.

### 10.3 Synthetic fraud dataset

Create `experiments/08_neo4j/data/` with these CSVs.

`people.csv`
```csv
customer_id,name,known_fraudster
P001,Asha,true
P002,Ravi,false
P003,Mina,false
P004,Dev,false
```

`accounts.csv`
```csv
account_id,owner_id,status
A100,P001,blocked
A200,P002,active
A300,P003,active
A400,P004,active
```

`devices.csv`
```csv
device_id,device_type
D10,mobile
D20,desktop
```

`uses.csv`
```csv
customer_id,device_id,last_seen
P001,D10,2025-01-01T10:00:00Z
P002,D10,2025-01-02T10:00:00Z
P003,D20,2025-01-02T11:00:00Z
P004,D10,2025-01-03T10:00:00Z
```

`transfers.csv`
```csv
transfer_id,source_id,target_id,amount,occurred_at
T001,A200,A300,125.00,2025-01-03T10:30:00Z
T002,A300,A400,75.00,2025-01-03T10:40:00Z
T003,A400,A100,950.00,2025-01-03T11:00:00Z
```

These are synthetic teaching rows, not a fraud model or performance benchmark. Create constraints before loading:

```cypher
CREATE CONSTRAINT customer_id_unique IF NOT EXISTS
FOR (c:Customer) REQUIRE c.customer_id IS UNIQUE;
CREATE CONSTRAINT account_id_unique IF NOT EXISTS
FOR (a:Account) REQUIRE a.account_id IS UNIQUE;
CREATE CONSTRAINT device_id_unique IF NOT EXISTS
FOR (d:Device) REQUIRE d.device_id IS UNIQUE;
```

Load entities first, then relationships. Example batched node query:

```cypher
UNWIND $rows AS row
MERGE (p:Customer {customer_id: row.customer_id})
SET p.name = row.name,
    p.known_fraudster = toBoolean(row.known_fraudster);
```

Accounts and ownership:

```cypher
UNWIND $rows AS row
MERGE (a:Account {account_id: row.account_id})
SET a.status = row.status
WITH row, a
MATCH (p:Customer {customer_id: row.owner_id})
MERGE (p)-[:OWNS]->(a);
```

Devices:

```cypher
UNWIND $rows AS row
MERGE (d:Device {device_id: row.device_id})
SET d.device_type = row.device_type;
```

Device usage:

```cypher
UNWIND $rows AS row
MATCH (p:Customer {customer_id: row.customer_id})
MATCH (d:Device {device_id: row.device_id})
MERGE (p)-[r:USES]->(d)
SET r.last_seen = datetime(row.last_seen);
```

This pattern intentionally stores one current-state `USES` relationship per customer/device pair and overwrites `last_seen` on replay. It does **not** preserve every device-use event. If history, source event IDs, or multiple uses per pair must be queryable, model each usage as a uniquely identified `(:DeviceUse {event_id, occurred_at, ...})` event node connected to both the customer and device (or use a version-supported relationship identity design with an explicit deduplication strategy).

Transfers:

```cypher
UNWIND $rows AS row
MATCH (source:Account {account_id: row.source_id})
MATCH (target:Account {account_id: row.target_id})
MERGE (source)-[t:TRANSFERRED_TO {transfer_id: row.transfer_id}]->(target)
SET t.amount = toFloat(row.amount),
    t.occurred_at = datetime(row.occurred_at);
```

This assumes each transfer ID identifies one relationship between the matched accounts. If IDs must be globally unique regardless of endpoint, use a `Transfer` node with a unique key. Validate missing endpoints and malformed rows before loading; quarantine invalid records instead of silently dropping them.

## 11. Graph Data Science (GDS) awareness

GDS algorithms usually operate on an in-memory **graph projection** of selected nodes and relationships. Projection settings, memory requirements, concurrency, procedures, and write modes vary by GDS version. Verify GDS installation and documentation before running examples.

### 11.1 PageRank

PageRank scores structural importance based on incoming connections. It may help identify structurally central accounts or devices in a defined projection, but centrality is not proof of fraud.

For PageRank, project directed account transfers so the projection preserves transfer direction:

```cypher
CALL gds.graph.project(
  'accountTransfers',
  'Account',
  {TRANSFERRED_TO: {orientation: 'NATURAL'}}
);
```

Run PageRank:

```cypher
CALL gds.pageRank.stream('accountTransfers')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).account_id AS account_id, score
ORDER BY score DESC
LIMIT 20;
```

For Louvain, create a separate undirected projection. Community algorithms can have different direction requirements; do not assume one projection is suitable for every algorithm:

```cypher
CALL gds.graph.project(
  'accountTransfersUndirected',
  'Account',
  {TRANSFERRED_TO: {orientation: 'UNDIRECTED'}}
);
```

### 11.2 Community detection

Community algorithms seek groups with dense or similar connectivity. Results depend on selected relationships, direction, weights, algorithm settings, and data quality. This example intentionally treats transfers as undirected ties for community detection; that is an analytical choice, not a statement that money movement is semantically undirected.

```cypher
CALL gds.louvain.stream('accountTransfersUndirected')
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).account_id AS account_id, communityId
ORDER BY communityId, account_id;
```

Drop both in-memory projections when finished:

```cypher
CALL gds.graph.drop('accountTransfers');
CALL gds.graph.drop('accountTransfersUndirected');
```

These procedures illustrate a common workflow; exact procedure names and projection APIs must match the installed GDS version. Projection memory is separate from ordinary graph storage and requires capacity planning.
Community IDs are labels for one run, not permanent business identities; they can change when data or settings change.

### 11.3 Similarity and path finding

- **Similarity:** compare neighborhoods or features to find customers/accounts with overlapping devices or counterparties. Jaccard similarity is one measure for set overlap.
- **Path finding:** find reachable nodes, shortest paths, or weighted paths based on business-defined costs.
- **Algorithm choice:** define weights carefully, scope the projection, estimate memory, and document assumptions.

Do not run an algorithm against the entire production graph by default. Use representative test data, measure resource use, and select only relevant node and relationship types.

## 12. Industry use cases

- **Fraud rings and identity resolution:** shared devices, contact details, accounts, and counterparties connect entities that look separate in tables. Deterministic IDs and probabilistic evidence should be distinguished; a graph connection is not proof of identity.
- **Recommendations:** connect customers to products, purchases, views, and categories to discover related items or similar customers. Evaluate recommendation quality separately.
- **Knowledge graphs:** connect people, organizations, concepts, products, and claims; preserve provenance for automatically extracted facts.
- **Lineage and dependency graphs:** represent datasets, jobs, tables, reports, and models with `DEPENDS_ON` or `PRODUCES` relationships for impact analysis and root-cause investigation.
- **Operational decision support:** enrich decisions with related accounts or devices, but apply authorization and explainability rules rather than treating a raw score as a final high-stakes decision.

## 13. Scaling, alternatives, and GraphRAG

### 13.1 Neo4j scaling considerations

Neo4j clustering, routing, read replicas, and write behavior depend on product, topology, edition, and version. A cluster can improve availability and distribute some read work, but does not imply unlimited horizontal write scaling. In common clustered Neo4j architectures, writes are coordinated through a leader for each database; do not assume arbitrary write sharding across independent nodes.

Plan for node/relationship growth, property and index footprint, transaction size, heap, page cache, storage I/O, CPU, network, query concurrency, write contention, degree skew, backups, and restore testing. Bigger hardware cannot compensate for unbounded path expansion or poor modelling.

### 13.2 Property graph alternatives and RDF/SPARQL

Other property-graph engines exist, including managed graph services and distributed graph-processing systems. They differ in query language, transactions, deployment, algorithms, and operations.

**RDF** represents information as subject–predicate–object triples, often with named graphs and ontology semantics. **SPARQL** queries RDF datasets. RDF/SPARQL is common in linked data and semantic interoperability. It is not interchangeable with property graphs/Cypher without a mapping decision. Choose based on model, query patterns, governance, integration, and operational needs.

### 13.3 Graph plus LLMs (GraphRAG awareness)

GraphRAG combines graph entities/relationships with retrieval for language-model applications. A pipeline may extract entities and relations from documents, resolve them to known entities, retain provenance, and retrieve relevant subgraphs for an answer.

Risks include incorrect extracted relationships, entity-resolution errors, stale graph data, prompt injection in source text, over-broad retrieval, and answers that omit evidence. Preserve source references and timestamps, validate extracted facts, authorize every retrieval, and distinguish source evidence from inference. A graph does not automatically make LLM output factual.

## 14. Exporting graph data to the lakehouse

Neo4j may be an operational or derived graph store; analytical aggregates can be more economical in a lakehouse. Export stable IDs, event timestamps, schema version metadata, and node/relationship/algorithm-result records. Distinguish a full snapshot from incremental export. Incremental export needs a reliable change source (CDC, outbox, event stream, or a carefully designed update watermark) and explicit delete handling. Polling timestamps alone can miss deletes, late events, and equal-timestamp updates.

Example account summary query:

```cypher
MATCH (a:Account)
OPTIONAL MATCH (a)-[t:TRANSFERRED_TO]->()
RETURN a.account_id AS account_id,
       a.status AS status,
       count(t) AS outgoing_transfer_count,
       coalesce(sum(t.amount), 0.0) AS outgoing_amount;
```

Python export to Parquet in bounded batches:

Python export to Parquet in bounded batches. This example uses an explicit schema so batches with null/missing properties do not infer incompatible schemas. It writes to a temporary file and only replaces the final path after the query finishes successfully; a failed run must not leave a partial file looking complete.

```python
import os
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
from neo4j import GraphDatabase

uri = os.environ["NEO4J_URI"]
auth = (os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"])
database = os.getenv("NEO4J_DATABASE", "neo4j")
output_path = Path("account_summary.parquet")
temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
batch_size = 10_000
query = """
MATCH (a:Account)
OPTIONAL MATCH (a)-[t:TRANSFERRED_TO]->()
RETURN a.account_id AS account_id,
       a.status AS status,
       count(t) AS outgoing_transfer_count,
       coalesce(sum(t.amount), 0.0) AS outgoing_amount
"""
schema = pa.schema([
    ("account_id", pa.string()),
    ("status", pa.string()),
    ("outgoing_transfer_count", pa.int64()),
    ("outgoing_amount", pa.float64()),
])
driver = GraphDatabase.driver(uri, auth=auth)
writer = None
row_count = 0
completed = False
try:
    writer = pq.ParquetWriter(temp_path, schema)
    with driver.session(database=database) as session:
        result = session.run(query)
        buffer = []
        for record in result:
            buffer.append(record.data())
            if len(buffer) >= batch_size:
                table = pa.Table.from_pylist(buffer, schema=schema)
                writer.write_table(table)
                row_count += table.num_rows
                buffer.clear()
        if buffer:
            table = pa.Table.from_pylist(buffer, schema=schema)
            writer.write_table(table)
            row_count += table.num_rows
        result.consume()  # surface any remaining server-side result/summary errors
    writer.close()
    writer = None
    os.replace(temp_path, output_path)  # same-filesystem atomic rename on normal local filesystems
    completed = True
    print(f"Exported {row_count} rows to {output_path}")
finally:
    if writer is not None:
        writer.close()
    driver.close()
    if not completed:
        temp_path.unlink(missing_ok=True)
```


This demonstrates a full extract, not a transactional cross-system CDC protocol or a consistent snapshot across concurrent graph writes. The explicit schema allows an empty result to produce a valid zero-row Parquet file. The local `os.replace` protects the final path from partial output when the process fails before commit, but object storage needs its own staging/manifest commit protocol. For production, add snapshot/watermark semantics, output partitioning, checksums, checkpointing, retries, and secure object-storage credentials. Do not collect the whole graph in Python memory.

## 15. Hands-on labs — `experiments/08_neo4j/`

Suggested structure:

```text
experiments/08_neo4j/
├── docker-compose.yml
├── data/ (people.csv, accounts.csv, devices.csv, uses.csv, transfers.csv)
├── scripts/ (generate_data.py, load_graph.py, export_results.py)
└── notes.md
```

Record server, driver, and GDS versions in `notes.md`. Use synthetic data only and keep credentials out of source control.

### Exercise 1 — Whiteboard the domain

Draw `Customer`, `Account`, `Device`, and either transfer relationships or `Transfer` event nodes. Label every edge with direction and meaning. Deliver a diagram, a table of node/relationship/property choices, five graph questions, and one question where SQL is simpler.

**Evaluation:** stable entity identity, justified event modelling, meaningful direction, and no unnecessary global hub node.

### Exercise 2 — Rewrite a four-hop SQL self-join

Use the SQL and Cypher examples in Section 7.7. Test a chain with four edges (should return the endpoint), a chain with three edges (should not), and a reversed edge (should change results for directed traversal).

**Evaluation:** preserve hop count, direction, and all business predicates.

### Exercise 3 — Load synthetic fraud data idempotently

Create the five CSVs in Section 10.3. Add constraints, load nodes first, then ownership/use relationships and transfers. Run the loader twice and check counts:

```cypher
MATCH (c:Customer) RETURN count(c) AS customers;
MATCH (a:Account) RETURN count(a) AS accounts;
MATCH (d:Device) RETURN count(d) AS devices;
MATCH ()-[r:USES]->() RETURN count(r) AS uses;
MATCH ()-[r:TRANSFERRED_TO]->() RETURN count(r) AS transfers;
```

**Expected observation:** a second run should update intended properties but not duplicate nodes/relationships if stable keys and `MERGE` patterns are correct. Record actual counts rather than copying expected counts without running the lab.

### Exercise 4 — Find accounts sharing devices with a known fraudster

Run the explicit three-hop query in Section 7.2.

Test: no shared device returns no candidate; a shared device returns the expected related customer/account; rerunning the query does not change data; shared-device evidence is presented as a lead, not a conclusion.

**Evaluation:** correct three-edge semantics, distinct accounts, correct direction, and evidence identifying the shared device.

### Exercise 5 — Compare plans with and without an index

Use a non-production dataset large enough to inspect plan differences. Inspect `SHOW INDEXES`; profile a selective lookup; profile a query on a non-unique property before/after adding its index; wait for the index to be online. Keep data, query, parameters, cache state, and environment consistent; warm up and run repeated trials. Record actual operators, database hits, and latency. Do not drop a uniqueness constraint to create a no-index case.

**Expected observation:** a suitable selective index can replace a broad label scan, but the speedup depends on selectivity, cache, data size, and traversal cost. No improvement amount is guaranteed.

### Exercise 6 — Run PageRank and community detection, export to Parquet

Verify compatible GDS installation. Create `accountTransfers` with `NATURAL` orientation for PageRank and `accountTransfersUndirected` with `UNDIRECTED` orientation for Louvain, as shown in Section 11. Run both algorithms. To export the account summary, run the Section 14 exporter as written. To export algorithm output instead, replace its Cypher query and Arrow schema together—for PageRank, use columns `account_id: string` and `score: float64`; for Louvain, use `account_id: string` and `community_id: int64`. Keep the selected query's aliases and schema exactly aligned. Record projection settings, algorithm parameters, node count, schema, and actual output row count.

**Expected observation:** results describe structural metrics/groups for the selected projection. Exact scores and communities depend on the data and settings; community IDs are not permanent business identifiers.

### Exercise 7 — Create a super node and investigate impact

Generate synthetic data with one `Device` connected to many customers. Compare a traversal through an ordinary device with traversal through the high-degree device; compare bounded/filtered with unbounded exploration. Record actual rows, database hits, operators, and latency. Do not run a huge write on a shared or production database.

**Expected observation:** high-degree traversal can produce many candidates and intermediate rows. The magnitude depends on query and configuration; measure it rather than assuming a fixed slowdown.

### Exercise 8 — Test batch failure and replay

Choose a batch size, introduce a malformed row or missing endpoint, and decide whether to reject, quarantine, or fail it. Fix the row and rerun. Verify no duplicate entities, relationships, or transfer IDs.

**Evaluation:** failures are visible, retries are safe, invalid records are not silently lost, and counts can be reconciled.

### Exercise 9 — Define a lakehouse export contract

Export account summaries and transfer records to Parquet. Document snapshot time or incremental watermark, record keys, UTC timestamps, schema version, delete handling, replay policy, output row count, checksum/sampled comparison, and output location.

**Evaluation:** bounded-memory export, explicit schema, final-path protection on failure, empty-result handling, and a clear distinction between full snapshot and reliable change feed. Test a query returning zero rows and deliberately interrupt a test export; confirm no partial final file is published.

## 16. Common mistakes

- Using `CREATE` in replayable ingestion and creating duplicates.
- Relying on `MERGE` without stable keys and uniqueness constraints.
- Matching nodes by mutable values such as names or statuses.
- Modelling every attribute as a node or every event as a relationship.
- Using unbounded path expansion on large/high-degree graphs.
- Treating index-free adjacency as a guarantee that indexes and plans do not matter.
- Returning entire paths or nodes when only a few properties are needed.
- Ignoring relationship direction.
- Treating shared-device evidence as proof of fraud.
- Assuming GDS algorithms are available in core Neo4j without installing compatible GDS.
- Treating community IDs as stable business identifiers.
- Treating one `PROFILE` run as a portable benchmark.
- Assuming clusters scale writes linearly.
- Exporting the entire graph into Python memory at once.
- Using timestamp polling for incremental exports without delete and late-event handling.
- Using GraphRAG without provenance, authorization, or validation.

## 17. Practice questions

1. What is the difference between a node label and a relationship type?
2. Why might a graph traversal be simpler than four relational self-joins?
3. What does index-free adjacency mean—and not mean?
4. When should a transfer be a relationship versus a `Transfer` node?
5. Why is `MERGE` not a complete substitute for uniqueness constraints?
6. How does `OPTIONAL MATCH` differ from `MATCH`?
7. What does `WITH` do to variable scope?
8. What is the difference between `EXPLAIN` and `PROFILE`?
9. Why can a super node make traversal expensive?
10. How do PageRank and community detection answer different questions?
11. What is required for reliable incremental graph-to-Parquet extraction?
12. When is a relational database simpler than Neo4j?
13. How do property graphs/Cypher differ from RDF/SPARQL?
14. Why are graph-derived relationships not automatically proof for a high-stakes decision?

## 18. Checkpoints

- [ ] Model customers, accounts, devices, and transactions as a property graph.
- [ ] Explain when graph traversal is appropriate versus relational joins.
- [ ] Write and parameterize basic Cypher queries and updates.
- [ ] Use variable-length paths, `OPTIONAL MATCH`, `WITH`, aggregation, and `UNWIND`.
- [ ] Explain constraints, indexes, and query-plan operators.
- [ ] Load data in batches with stable IDs and idempotent `MERGE`.
- [ ] Write the three-hop fraud query and four-hop transfer query.
- [ ] Explain GDS PageRank and community detection and their limitations.
- [ ] Explain super-node risk and Neo4j scaling constraints.
- [ ] Define a graph export contract for lakehouse analytics.

## 19. Final self-assessment

Rate each from 1 (need to revisit) to 4 (can implement and explain in a code review).

| Skill | Rating |
|---|---:|
| Property graph modelling and node/relationship/property choices | 1–4 |
| Cypher CRUD, filtering, aggregation, and variable-length paths | 1–4 |
| Constraints, indexes, and `PROFILE` interpretation | 1–4 |
| Batched Python ingestion and idempotent replay | 1–4 |
| Fraud traversal and four-hop query conversion | 1–4 |
| GDS projection and algorithm interpretation | 1–4 |
| Super-node mitigation and scaling trade-offs | 1–4 |
| Lakehouse export, schema, and incremental correctness | 1–4 |

Before moving to Topic 09, demonstrate repeatable graph loading, explain why a query returns its results, and describe how graph data or derived metrics can be extracted without confusing a full snapshot with a reliable change feed.

## 21. Technical references and version notes

Use the documentation matching the exact Neo4j server, driver, and Graph Data Science versions deployed. The lesson examples are intended for a Neo4j 5.x-style environment; current documentation may describe newer Cypher or API behavior.

- [Neo4j Cypher Manual — `MERGE`](https://neo4j.com/docs/cypher-manual/current/clauses/merge/): matching semantics and the role of constraints in reliable identity handling.
- [Neo4j Cypher Manual — transactional subqueries](https://neo4j.com/docs/cypher-manual/current/subqueries/subqueries-in-transactions/): `CALL { ... } IN TRANSACTIONS` and batch failure behavior.
- [Neo4j Graph Data Science — graph projection](https://neo4j.com/docs/graph-data-science/current/management-ops/graph-creation/graph-project/): projection orientation and in-memory graph creation.
- [Neo4j Graph Data Science — Louvain](https://neo4j.com/docs/graph-data-science/current/algorithms/louvain/): algorithm traits, projection expectations, and interpretation.
- [Neo4j Python Driver Manual](https://neo4j.com/docs/python-manual/current/): sessions, transactions, parameters, and result consumption.

These references are technical starting points, not proof that a command was executed against your local installation. Verify API availability, edition/licensing, and syntax against the pinned versions used in the lab.

## 20. Engineering checklist

- Define the source of truth and the graph's role (primary, derived, or serving store).
- Document node identity, relationship direction, event identity, and deletion semantics.
- Add constraints for required unique identifiers.
- Parameterize all user-supplied query values.
- Bound traversals and filter from selective starting nodes.
- Inspect `EXPLAIN` and `PROFILE` on representative data.
- Load in batches and design replay-safe ingestion.
- Track degree distribution and detect high-degree hubs.
- Size GDS projections separately from database storage.
- Version the export schema and reconcile counts/checksums.
- Verify backup/restore, access control, and deployed-version compatibility.
- Treat graph scores as signals requiring context, not unquestionable facts.
