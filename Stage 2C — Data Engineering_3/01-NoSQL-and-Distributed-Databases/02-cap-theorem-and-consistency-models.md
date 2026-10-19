# CAP Theorem and Consistency Models

**Stage:** Stage 2C — Data Engineering_3  
**Module:** 01 — NoSQL and Distributed Databases  
**Lesson:** Topic 02 — CAP theorem and consistency models  
**Output filename:** `02-cap-theorem-and-consistency-models.md`

------------------------------------------------------------------------

## Learning objectives

After this lesson, you should be able to:

1.  Explain why distributed databases replicate data and how node failures and network partitions affect requests.
2.  State CAP precisely and explain why “pick two of three” is misleading.
3.  Distinguish ACID transaction consistency from CAP consistency and explain BASE.
4.  Compare linearizability, sequential consistency, causal consistency, read-your-writes, monotonic reads, and eventual consistency.
5.  Explain PACELC and the normal-operation latency/consistency trade-off.
6.  Calculate read/write quorum combinations for (N=3) and (N=5), and state the assumptions behind (R+W\>N).
7.  Identify practical consistency controls in Cassandra, DynamoDB, and MongoDB without assigning a permanent CP/AP label to an entire product.
8.  Explain leader/follower, multi-leader, and leaderless replication, replication lag, and conflict resolution.
9.  Describe consensus, leader election, split brain, two-phase commit, and sagas at an architectural level.
10. Build a small replica simulation, perform the Cassandra consistency experiment, and demonstrate a lost update and a repair strategy.
11. Explain how Jepsen-style testing can evaluate consistency claims and why a toy simulation is not proof of a database’s guarantees.

## How this lesson fits the roadmap

This is Topic 02 in:

``` text
Stage 2C — Data Engineering_3/
└── 01-NoSQL-and-Distributed-Databases/
    ├── 01-nosql-families-and-when-to-use-them.md
    ├── 02-cap-theorem-and-consistency-models.md  ← this lesson
    ├── 03-mongodb-document-modelling-and-aggregation.md
    ├── 04-cassandra-wide-column-partitioning-and-tombstones.md
    ├── 05-dynamodb-single-table-design-and-streams.md
    ├── 06-redis-caching-and-data-structures.md
    ├── 07-elasticsearch-and-opensearch-for-search-and-logs.md
    ├── 08-graph-databases-neo4j-and-cypher.md
    └── 09-change-streams-and-nosql-to-lakehouse-ingestion.md
```

Topic 01 introduced the five NoSQL families and the principle of choosing a store by its access patterns. This lesson adds the language needed to reason about what happens when data is replicated, nodes fail, or clients read after a write. Topics 03–08 apply these concepts to individual systems; Topic 09 uses them when extracting changes reliably into a lakehouse.

### Prerequisites

The roadmap assumes you have studied:

- SQL transactions and isolation levels (Stage 2, Module 2.6).
- Normalization and denormalization (Stage 2, Module 2.8).
- CDC, watermarks, idempotent merge loads, and deduplication (Stage 2).
- Kafka and Debezium basics (Stage 2).
- Topic 01: NoSQL families, replication at a high level, and the difference between a system of record and a derived store.

This lesson uses basic probability-free arithmetic and small Python examples. It does not assume prior knowledge of distributed consensus.

## 1. Why distribution creates consistency questions

A single database process can keep one current copy of a value in memory and durable storage. A distributed database may keep copies on multiple machines so the service can survive machine failure, place data near users, or serve more traffic.

**Replication** means maintaining multiple copies of data. It can improve availability and read capacity, and it can reduce the risk that a single node failure makes data inaccessible. It also creates a coordination problem: after a write, how do the copies learn about it, and what may a read return before all copies have caught up?

### 1.1 Three replicas

Assume a key `account:42` has value `balance=100` on three replicas.

``` text
                 client
                   |
             write balance=90
                   |
          ┌────────┴────────┐
          ▼                 ▼
      Replica A         Replica B         Replica C
      balance=90        balance=90        balance=100
      updated            updated           stale copy
```

If the write reaches A and B but not C, the system has two versions in circulation. A read from C may return the old value. This delay is called **replication lag** when replicas have not yet applied an update.

Whether that stale read is allowed depends on the database, the operation, the consistency setting, the failure state, and the read path. A system can wait for more acknowledgements, route reads to a leader, consult multiple replicas, or allow a fast local response that may be stale.

### 1.2 Node failure versus network partition

- **Node failure:** a process or machine stops, crashes, or becomes unreachable.
- **Network partition:** nodes that are still running cannot communicate reliably across some network boundary. A partition can be asymmetric or intermittent; it does not necessarily mean every link is down.
- **Timeout:** the caller did not receive a response within a deadline. A timeout does not prove that the operation failed—the server may have committed it and lost the response.
- **Acknowledgement:** a response indicating that a node or system has accepted or completed some defined part of an operation. Read the exact contract: “acknowledged” can mean different things across products and settings.

Consider a partition splitting A from B and C:

``` text
           Network partition
       ┌────────────────────────┐
       │                        │
   ┌───▼───┐                ┌───▼───┐
   │   A   │   X no link X  │   B   │
   └───────┘                └───┬───┘
                                │
                            ┌───▼───┐
                            │   C   │
                            └───────┘
```

A and B/C may each receive requests from clients. If both sides accept conflicting writes to the same key, the system needs a policy to prevent divergence or reconcile it later. If only one side is allowed to accept writes, clients on the other side may receive errors or wait.

That tension motivates CAP.

## 2. CAP theorem from first principles

CAP concerns three properties of a distributed data service:

- **Consistency (C, in CAP):** in the formal CAP framing, every successful read sees the most recent successful write, or an error is returned. This is closely associated with **linearizability** for a single object. It does not mean “the data is valid according to business rules.”
- **Availability (A, in CAP):** every request received by a non-failing node eventually receives a non-error response. A response that returns stale data can count as available under this definition.
- **Partition tolerance (P):** the system continues to operate despite communication failures that divide nodes into groups unable to communicate. In a distributed deployment, partitions are possible failures that the architecture must account for.

### 2.1 What CAP actually says

When a network partition separates replicas, a distributed system cannot guarantee both:

1.  every request returns a response (availability), and
2.  every successful read returns the latest value according to the consistency definition above.

The system must choose its behavior for operations affected by the partition: refuse or delay some requests to preserve consistency, or respond on reachable sides and accept that some responses may be stale or conflicting.

``` text
                    Network partition
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
     Preserve consistency        Preserve availability
     for affected operations     for affected operations
     by refusing/waiting         by responding where possible
     on one side                 even if data may be stale
```

**Important:** partition tolerance is not a switch that a real distributed system can simply turn off. Networks can fail. CAP is most useful for understanding the trade-off a system makes **during a partition**, not for declaring that a database has selected any two properties forever.

### 2.2 Why “pick two of three” is misleading

The slogan makes CAP sound like a static menu where a designer chooses any two of C, A, and P. That is not the practical meaning.

- If the network never partitions, the specific CAP conflict is not activated.
- A distributed deployment generally has to tolerate the possibility of partitions.
- During a partition, the key question is how operations on the separated sides behave.
- Different operations, settings, and deployment topologies can have different behavior.
- “Consistency” in CAP has a formal meaning; it is not the same as every business rule or ACID consistency.

A database may, for example, provide strong consistency for one read mode and eventual consistency for another, or allow writes only through a leader while still serving some reads from followers. A service’s actual guarantees must be evaluated at the operation/configuration level.

### 2.3 A partition example

Suppose the current value is `status="pending"`. A client connected to replica A updates it to `"approved"`. A network partition prevents A from reaching replicas B and C.

- **Consistency-preserving behavior:** A cannot safely confirm a write under the system’s chosen strong consistency contract unless it can satisfy the required coordination. It may reject or time out the write. A read from the isolated side may also be rejected.
- **Availability-preserving behavior:** A may accept the write and answer local reads. B/C may still return `"pending"` or accept another update. The system must later reconcile divergent state.

Neither behavior is universally right. A social “like” counter may tolerate temporary divergence; an account transfer or inventory reservation may require stronger coordination and explicit failure to proceed.

## 3. ACID versus BASE

CAP consistency and ACID consistency share a word but mean different things.

### 3.1 ACID

ACID describes transaction properties:

- **Atomicity:** a transaction’s changes commit as a unit or are rolled back as a unit.
- **Consistency (ACID):** a transaction preserves declared database invariants and constraints when moving from one valid state to another.
- **Isolation:** concurrent transactions behave according to the selected isolation level.
- **Durability:** committed changes survive the failures covered by the durability contract.

For example, a bank transfer should debit one account and credit another as one logical transaction. A constraint might prohibit a negative balance. ACID consistency refers to preserving such invariants, not to CAP’s latest-write/read guarantee.

### 3.2 BASE

BASE is an informal design philosophy often associated with highly available distributed systems:

- **Basically Available:** the service aims to keep responding under expected failures, possibly with reduced or stale information.
- **Soft State:** replicas or derived state may temporarily differ while updates propagate.
- **Eventual Consistency:** if no new updates occur and the system’s repair/propagation process succeeds, replicas will eventually converge.

BASE is not a formal protocol and is not a promise that every BASE-labelled system behaves identically. It describes a common set of trade-offs, not an alternative set of transaction properties guaranteed by every NoSQL product.

### 3.3 Comparison

| Question                  | ACID transaction properties                              | CAP / BASE concerns                                                                                |
|---------------------------|----------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| Main concern              | Correct transactional state changes and failure handling | Behavior of distributed reads/writes, especially under partitions                                  |
| “Consistency” means       | Preserve database/business invariants                    | In CAP, latest-write visibility under the formal model                                             |
| Typical example           | Debit and credit succeed together                        | Whether an isolated replica accepts a write or serves a read                                       |
| Can the concepts coexist? | Yes                                                      | A distributed database can offer ACID transactions and still face CAP trade-offs during partitions |

A distributed SQL database may provide ACID transactions while still needing to choose which requests can succeed during a network partition. A database using eventual consistency can still enforce local constraints or atomic updates for some operations.

## 4. Consistency models: what can a read observe?

A **consistency model** is a contract describing which histories of reads and writes are allowed. Stronger models rule out more surprising histories, usually at some cost in coordination, latency, availability, or throughput.

For intuition, use this timeline:

``` text
time ───────────────────────────────────────────────►

Client A:  write x=1 ───── receives success
Client B:                    read x → ?
Replicas:  A has x=1; B and C may still have x=0
```

The question is not simply whether a replica is “up.” It is what the contract allows the read to return.

### 4.1 Linearizability

**Guarantee:** each operation appears to take effect at one instant between its invocation and response, and operations respect real-time order. If a write completes before a later read begins, that read must reflect the write or a later write.

``` text
A: write x=1 ───── success
B:                       read x ─────► 1 (or a later value)
```

**Does not guarantee:** a transaction across multiple keys unless the database’s transaction contract says so; nor does it automatically enforce application rules that were never encoded.

**Stale read?** A read that returns an older value than a completed prior write is not allowed for the same linearizable object.

**Where it matters:** balances, inventory reservations, uniqueness, lock ownership, and control-plane decisions where clients rely on a single real-time order.

**Cost/trade-off:** often requires coordination with a leader or quorum. During a partition, some requests may fail or wait.

### 4.2 Sequential consistency

**Guarantee:** operations appear in one total order that preserves each individual process’s program order.

**Difference from linearizability:** the total order need not respect the real-time ordering between operations from different clients. A write that completed in wall-clock time before another client began a read can still appear later in the sequential order if the model allows it.

**Stale read?** A read may appear stale relative to wall-clock events across clients, but the history must still fit one sequential order and preserve each client’s own operation order.

**Where it matters:** useful as a theoretical model and in reasoning about concurrent shared memory. Database products do not all expose a setting literally named “sequential consistency”; check product documentation rather than mapping terminology by name alone.

### 4.3 Causal consistency

**Guarantee:** causally related operations are observed in an order that respects their cause-and-effect relationship. If write B was performed after observing write A, a client should not observe B without the causal context that makes A precede it.

Example:

1.  Alice posts: “I adopted a dog.”
2.  Bob reads the post.
3.  Bob comments: “Congratulations on the dog!”

A causally consistent observer should not see Bob’s comment while missing the post it responds to, assuming both are part of the same causal history.

**Does not guarantee:** one global order for concurrent, causally unrelated writes. Two independent updates can be observed in different orders by different clients.

**Stale read?** A client may miss a concurrent or not-yet-observed update, but the system should preserve causal order for related operations.

**Where it matters:** collaborative apps, messaging, social feeds, and workflows where “reply after reading” relationships should remain understandable.

### 4.4 Read-your-writes

**Guarantee:** after a client successfully writes a value, that same client’s subsequent reads see that write or a later value.

**Does not guarantee:** that every other client immediately sees the write, or that all writes have a global real-time order.

**Stale read?** A user may still see old data from another user’s session, but should not be shown their own prior update as if it never happened.

**Where it matters:** profile editing, changing a setting and immediately viewing it, or posting content and seeing it on one’s own page.

**Implementation approaches:** route a session to a suitable replica, use a session token/version, read from a leader, or wait until a replica has applied the client’s write. Product support varies.

### 4.5 Monotonic reads

**Guarantee:** once a client has observed a value/version, later reads by that client do not move backward to an older state.

Example: after a user sees message 120, a later page refresh should not show a history ending at message 115.

**Does not guarantee:** the client immediately sees every new update or that different clients observe the same latest version.

**Stale read?** A client can remain behind the newest global version, but should not regress relative to what that client has already observed.

**Where it matters:** feeds, timelines, dashboards, and paginated data served from replicas with different lag.

### 4.6 Eventual consistency

**Guarantee:** if updates stop and communication/repair eventually succeeds, replicas converge to a consistent state according to the system’s conflict-resolution rules.

**Does not guarantee:** a fixed convergence deadline, immediate read-your-writes, monotonic reads, or that conflicting updates preserve all user intent. If conflict resolution discards an update, replicas can converge while a logical change has been lost.

**Stale read?** Yes, while replicas are catching up or when a read is routed to a lagging replica.

**Where it matters:** caches, likes, view counters, some social features, search indexes, and derived read models where temporary divergence is acceptable.

### 4.7 Comparison table

| Model                  | Core guarantee                                                                 | What it does not promise                                                        | Can a read be stale?                                                    | Typical use                                 |
|------------------------|--------------------------------------------------------------------------------|---------------------------------------------------------------------------------|-------------------------------------------------------------------------|---------------------------------------------|
| Linearizability        | Respects real-time order; completed write visible to later read of same object | Multi-key transaction semantics unless separately guaranteed                    | Not relative to a completed prior write on the same linearizable object | Balances, reservations, coordination        |
| Sequential consistency | One total order preserves each process’s operation order                       | Cross-client real-time ordering                                                 | May be stale relative to wall-clock order                               | Formal reasoning about concurrent histories |
| Causal consistency     | Causal dependencies are preserved                                              | Global order for concurrent unrelated writes                                    | Yes for unseen concurrent/unrelated updates                             | Social interactions, collaborative state    |
| Read-your-writes       | A client sees its own completed writes on later reads                          | Visibility to other clients                                                     | Not for that client’s own completed write, if contract is honored       | Profile/settings updates                    |
| Monotonic reads        | A client’s observed state does not move backward                               | Immediate visibility of all latest writes                                       | Can be behind global latest, but not regress for that client            | Feeds and timelines                         |
| Eventual consistency   | Replicas converge if updates stop and propagation/repair succeeds              | Immediate visibility, fixed deadline, or preservation of all conflicting intent | Yes                                                                     | Caches, derived indexes, tolerant counters  |

These guarantees are not always a simple ladder. Read-your-writes and monotonic reads are session guarantees; causal consistency captures dependencies; linearizability and sequential consistency describe histories differently. A product may combine or selectively expose guarantees.

## 5. PACELC: the trade-off outside partitions

CAP highlights the conflict during a partition. **PACELC** adds the normal-operation case:

- **If there is a Partition (P):** trade off Availability (A) versus Consistency (C).
- **Else (E), when there is no partition:** trade off Latency (L) versus Consistency (C).

In short: **P → A/C; else → L/C.**

Even when all nodes can communicate, a strongly coordinated read or write may need messages to a leader or multiple replicas. Waiting for those messages can improve consistency but add latency. A local replica read may be faster but may not include the newest write.

| Situation    | More consistency-oriented choice                                           | More latency/availability-oriented choice                                 |
|--------------|----------------------------------------------------------------------------|---------------------------------------------------------------------------|
| Partition    | Reject or wait for operations that cannot satisfy the consistency contract | Answer from reachable replicas, possibly with stale/conflicting data      |
| No partition | Coordinate with leader/quorum and wait for required acknowledgements       | Read locally or acknowledge before all replicas are updated, if supported |

PACELC is a useful design lens, not a universal numeric formula. A database’s actual trade-off depends on the operation, configuration, network topology, and failure mode.

## 6. Quorums: calculate read and write overlap

A **replica set** stores copies of the same logical data on several replicas. A quorum is a required number of replica responses for an operation.

- (N): number of replicas participating in the replication group for the item.
- (W): minimum replica acknowledgements required for a successful write.
- (R): number of replicas consulted for a read, according to the system’s protocol.

A common quorum-intersection condition is:

\[ R + W \> N \]

If read and write quorums are chosen from the same fixed set of (N) replicas, this inequality means every read quorum must overlap every write quorum by at least one replica.

### 6.1 Why overlap helps

For (N=3), if (W=2), a successful write is acknowledged by any two replicas. If (R=2), a read consults any two replicas. Two sets of two chosen from the same three members must overlap in at least one member.

``` text
N = 3 replicas:  A   B   C

Write quorum W=2: [A] [B]  C
Read quorum  R=2:  A  [B] [C]
                         ▲
                     overlap B
```

This intersection is useful because the read can encounter a replica that knows about the write. But overlap alone does not tell the system how to select the newest value, resolve concurrent writes, or repair stale replicas.

### 6.2 Worked combinations for N = 3

For this table, a “quorum intersection” means only the arithmetic condition (R+W\>3).

|   R |   W | R + W | Intersects every write quorum? | Simple interpretation                                                    |
|----:|----:|------:|--------------------------------|--------------------------------------------------------------------------|
|   1 |   1 |     2 | No                             | Fast, but a read can miss a write acknowledged elsewhere                 |
|   1 |   2 |     3 | No (strict inequality fails)   | A single-replica read can miss a two-replica write                       |
|   1 |   3 |     4 | Yes                            | Reads all possible one-member read sets overlap a full-replica write set |
|   2 |   1 |     3 | No (strict inequality fails)   | A one-replica write can be outside a two-replica read set                |
|   2 |   2 |     4 | Yes                            | Any two-member read set overlaps any two-member write set                |
|   2 |   3 |     5 | Yes                            | Read quorum overlaps a full-replica write                                |
|   3 |   1 |     4 | Yes                            | Full-replica read overlaps any write quorum                              |
|   3 |   2 |     5 | Yes                            | Full-replica read overlaps a two-replica write                           |
|   3 |   3 |     6 | Yes                            | Both read and write require all replicas                                 |

For symmetric quorum settings, (R=W=2) with (N=3) satisfies the inequality. It is not the only combination that satisfies it.

### 6.3 Worked combinations for N = 5

Here (R+W\>5) is required for intersection under the same assumptions.

|   R |   W | R + W | Intersects every write quorum? |
|----:|----:|------:|--------------------------------|
|   1 |   3 |     4 | No                             |
|   1 |   5 |     6 | Yes                            |
|   2 |   3 |     5 | No (strict inequality fails)   |
|   2 |   4 |     6 | Yes                            |
|   3 |   3 |     6 | Yes                            |
|   3 |   4 |     7 | Yes                            |
|   4 |   2 |     6 | Yes                            |
|   5 |   1 |     6 | Yes                            |
|   5 |   5 |    10 | Yes                            |

Complete matrix for (N=5) (✓ means (R+W\>5); — means the strict condition is not met):

| R \\ W |  1  |  2  |  3  |  4  |  5  |
|-------:|:---:|:---:|:---:|:---:|:---:|
|      1 |  —  |  —  |  —  |  —  |  ✓  |
|      2 |  —  |  —  |  —  |  ✓  |  ✓  |
|      3 |  —  |  —  |  ✓  |  ✓  |  ✓  |
|      4 |  —  |  ✓  |  ✓  |  ✓  |  ✓  |
|      5 |  ✓  |  ✓  |  ✓  |  ✓  |  ✓  |

The matrix shows all 25 combinations. For example, (R=3,W=3) intersects; (R=2,W=3) does not satisfy the strict condition.

### 6.4 What the equation does not prove

Do not treat (R+W\>N) as a universal proof of linearizability. The reasoning assumes, among other things:

1.  Read and write quorums are selected from the same fixed replica configuration for the item.
2.  The protocol’s acknowledged writes are represented on the intersecting replicas in a way the read can detect.
3.  The read protocol can determine which version should win and does not blindly return an older value.
4.  Concurrent writes are handled by an appropriate ordering or conflict-resolution rule.
5.  Membership changes, hinted handoff, sloppy quorums, and replica replacement do not invalidate the simple fixed-set assumption.
6.  The application is not confusing a successful acknowledgement with an operation that timed out after possibly committing.

Real databases add their own rules: timestamps, versions, read repair, anti-entropy repair, leader epochs, conditional writes, or consensus. Some systems use “quorum” in a product-specific way that should not be equated mechanically with the abstract (R) and (W) model.

The inequality is a valuable first calculation. It is not a substitute for reading the product’s consistency contract.

## 7. Consistency controls in real databases

### 7.1 Cassandra

Cassandra exposes **consistency levels** that specify how many replicas must respond to an operation. Exact availability and consistency behavior depends on replication factor, topology, and consistency level.

Common levels include:

- `ONE`: one replica response is sufficient.
- `QUORUM`: a majority of replicas for the relevant replication scope must respond.
- `LOCAL_QUORUM`: a majority in the local data center must respond.
- `ALL`: all replicas in the relevant replication scope must respond.

For a single data center with replication factor (RF) 3, `QUORUM` normally requires 2 replica responses. With one replica unavailable, the other two can satisfy `QUORUM` if both are reachable. `ONE` can succeed with one reachable replica, but a read at `ONE` may return stale data depending on which replica responds and what repair has occurred.

Cassandra is often described as having tunable consistency because the application can select levels per operation. This does not mean every combination is linearizable. Timestamp conflict resolution, concurrent writes, repair, and the selected consistency levels all matter. Cassandra’s lightweight transactions (LWT) use a Paxos-based protocol for conditional operations and have different latency/cost characteristics from ordinary writes.

**What to record in the lab:** Cassandra version, keyspace replication strategy, RF, data-center topology, consistency level on every read/write, which node was stopped, and the exact result or exception. Do not report an expected result as an observed result.

### 7.2 DynamoDB

DynamoDB provides:

- **Eventually consistent reads** as the default for many read operations.
- **Strongly consistent reads** for supported operations and table/index types when requested. Strong reads are not supported for every access path—for example, global secondary indexes do not support strongly consistent reads.
- **Conditional writes** to guard an update against a known condition, such as an expected version.
- **Transactions** for supported multi-item atomic workflows, subject to service limits and costs.
- **Global tables** with replication behavior that must be evaluated for the chosen configuration and current service mode; do not assume cross-Region writes have the same immediate conflict semantics as a single-region transaction.

For a `GetItem`, a client can request `ConsistentRead=True` where supported. This is an operation-level setting, not a blanket guarantee that every index, region, and multi-item workflow has linearizable semantics.

### 7.3 MongoDB

MongoDB exposes multiple related controls:

- **Write concern:** how many members must acknowledge a write (for example, `w: "majority"`), and optionally a journaling requirement.
- **Read concern:** the consistency/isolation guarantees for data returned by a read, including `"local"`, `"majority"`, and `"linearizable"` in supported contexts.
- **Read preference:** which replica-set members are eligible to serve reads, such as primary or secondary preferences. Secondary reads can be stale because replication is asynchronous.
- **Causally consistent sessions:** can provide causal guarantees when used with appropriate concerns and session behavior.
- **Transactions:** support multi-document transactional operations in supported deployments, with additional coordination and performance cost.

These settings are not synonyms. `readPreference=secondary` answers “which member may serve the read”; read concern answers “what data visibility guarantee applies”; write concern answers “what acknowledgement is required.” Check the exact version and deployment documentation before relying on a specific combination.

### 7.4 Compare the control surface

| System    | Typical controls                                                                                     | Important caution                                                                               |
|-----------|------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| Cassandra | `ONE`, `QUORUM`, `LOCAL_QUORUM`, `ALL`, LWT                                                          | RF, topology, timestamps, repair, and per-operation settings matter                             |
| DynamoDB  | Eventually consistent vs strongly consistent reads where supported; conditional writes; transactions | Strong reads are not supported on every index/path; multi-Region semantics need separate review |
| MongoDB   | Write concern, read concern, read preference, causal sessions, transactions                          | Read routing and data-visibility guarantees are separate choices                                |

The correct question is not “Is Cassandra/DynamoDB/MongoDB strongly consistent?” It is “For this operation, under this configuration and failure scenario, what does the database guarantee?”

## 8. Replication architectures

### 8.1 Leader/follower

One replica is the leader (or primary) for a replication group. Writes go through it; followers copy the changes.

``` text
                  writes
Client ─────────────────────► Leader
                                │
                     ┌──────────┴──────────┐
                     ▼                     ▼
                 Follower B            Follower C
```

**Advantages:** a clear write order is easier to establish; conflict handling is simpler when only the leader accepts ordinary writes.

**Trade-offs:** leader failure can require election/failover; follower reads may lag; writes may be unavailable if a new leader cannot be safely elected. Whether writes are acknowledged before or after replication affects durability and read visibility.

**Visible replication-lag symptoms:** a user edits a profile and refreshes through a secondary that still shows the old value; a report misses a recent event; a read replica’s metrics trail the primary.

### 8.2 Multi-leader

Multiple leaders accept writes, often in different regions or sites.

``` text
Client West ─► Leader West ◄──── replication ────► Leader East ◄─ Client East
```

**Advantages:** local write latency and continued writes in more than one location may improve.

**Trade-offs:** two leaders can concurrently update the same logical record. The system needs conflict detection and resolution, or application-level rules. A last-write-wins rule may discard meaningful updates.

**Typical fit:** multi-region applications that tolerate conflict handling and have clear merge semantics. It is risky for invariants that require one globally coordinated order unless the system provides stronger transactional semantics.

### 8.3 Leaderless / quorum-oriented replication

There may be no single permanent leader for ordinary reads/writes. A coordinator sends an operation to multiple replicas and waits for the required number of acknowledgements.

``` text
                  coordinator
                 /     |     \
                ▼      ▼      ▼
              Rep A  Rep B  Rep C
                \      |      /
                 quorum responses
```

**Advantages:** requests can be served through multiple replicas and tunable quorum settings can balance latency and consistency.

**Trade-offs:** reads may need to reconcile different versions; conflicts and replica repair are important; quorum settings do not eliminate every anomaly. Cassandra is a well-known example of a leaderless replication architecture for ordinary writes, while LWT adds a consensus protocol for conditional operations.

### 8.4 Replication lag and symptoms

Replication lag is the gap between a change being accepted at one point and becoming visible at another. It can be caused by network delays, overloaded replicas, write bursts, disk stalls, large transactions, or backlogs.

Symptoms include: - read-after-write returning the previous value; - replicas returning different versions; - a search index not yet containing a newly created record; - dashboards or feature stores trailing operational state; - failover exposing a version that had not been replicated to the new primary, depending on acknowledgement and durability settings.

For data engineering, lag affects snapshots, incremental extraction, CDC consumers, and reconciliation. A pipeline should track offsets/resume tokens, lag, errors, duplicate handling, and recovery procedures rather than assuming source reads are instantly current.

## 9. Conflict resolution: what happens when writes disagree?

A conflict occurs when concurrent or independently accepted updates cannot be combined by simply applying one after the other in a known order.

### 9.1 Last-write-wins (LWW)

LWW chooses the value with the greatest timestamp or ordering metadata according to the implementation. If timestamps tie, a deterministic tie-breaker may be used.

Example starting state: `preferences = {"theme": "light", "language": "en"}`.

- Client A changes theme to `"dark"`.
- Client B changes language to `"fr"` concurrently.
- Each client writes a whole replacement object.
- LWW chooses one entire object.

If A’s object is selected, B’s language change can disappear; if B’s object is selected, A’s theme change can disappear. The final value may be deterministic but still lose a valid user intent.

LWW can be acceptable when a single scalar value is intentionally “latest update wins,” but it is dangerous when independent fields or increments must be preserved. Wall clocks can skew, so timestamps are not always a reliable causal order.

### 9.2 Version checks / optimistic concurrency

Store a version number with the value. An update succeeds only if the version still equals the version the client read.

``` text
Read value at version 7
Client A: conditional update WHERE version = 7 → success, version 8
Client B: conditional update WHERE version = 7 → rejected (stale version)
Client B rereads version 8, merges its intended change, retries
```

SQL-style example:

``` sql
UPDATE account_settings
SET value = '{"theme":"dark","language":"en"}',
    version = version + 1
WHERE user_id = 42
  AND version = 7;
```

The application must check the affected-row count. If zero rows were updated, another writer changed the record; reread and merge or return a conflict. The SQL is illustrative and assumes a table with `user_id`, `value`, and `version` columns. The conditional predicate and update must be atomic in the database.

Version checks prevent silent overwriting by stale writers, but they do not decide how to merge the user’s intentions. The application needs a retry, merge, or user-visible conflict policy.

### 9.3 Vector clocks and version vectors

A **vector clock** records a logical counter per participant (or replica) to help determine causal ordering. One version dominates another if it is at least as large in every component and greater in at least one; incomparable vectors indicate concurrent updates.

Example:

``` text
Version v1: {A: 2, B: 1}
Version v2: {A: 1, B: 2}
```

Neither dominates the other, so the versions represent concurrent histories under the vector-clock comparison. The system can preserve both siblings for application merge instead of arbitrarily choosing one immediately.

**Version vectors** are closely related metadata structures used to track versions across replicas/participants. Terminology varies by system. These structures can grow or become costly as the set of participants changes, so modern systems may use variants or other conflict metadata.

They detect concurrency; they do not magically merge arbitrary business objects.

### 9.4 CRDTs

A **Conflict-free Replicated Data Type (CRDT)** is a data structure designed so concurrent updates can be merged according to defined rules while preserving specified invariants.

A simple example is a grow-only counter composed of per-replica components. Each replica increments its own component; the total is the sum. Merging takes the maximum observed value for each replica component, so duplicate delivery does not double-count a component.

Illustrative state:

``` text
Replica A: {A: 3, B: 0}  total = 3
Replica B: {A: 0, B: 2}  total = 2
Merged:    {A: 3, B: 2}  total = 5
```

This is a conceptual **G-counter**. Real implementations must define replica identity, state retention, reset semantics, and merge behavior. A generic CRDT counter is not suitable for all accounting rules: a counter that can only grow does not model arbitrary decrements, and even a PN-counter does not automatically enforce a “never negative” invariant across disconnected replicas.

### 9.5 Application-level merge

Sometimes the right merge policy is domain-specific:

- merge independent profile fields;
- append unique event IDs rather than overwrite a whole list;
- reject conflicting edits and ask the user to resolve them;
- use a versioned state machine for order transitions;
- use a transactional database for inventory or ledger invariants;
- preserve both conflicting versions for review.

**Rule:** choose conflict resolution from business semantics, not convenience alone. “Eventually converges” is not enough if the convergence rule discards legitimate updates.

## 10. Consensus, leader election, and split brain

### 10.1 Consensus in one level of detail

A consensus protocol lets a group of nodes agree on a value or ordered sequence despite certain failures, under defined assumptions. Consensus is commonly used to replicate a log or safely elect a leader.

Two important families are:

- **Raft:** uses terms, leader election, replicated logs, and quorum-based commitment. A candidate requests votes; a leader replicates log entries; entries become committed when the protocol’s quorum and log-safety conditions are met.
- **Paxos:** a family of consensus protocols based on proposers, acceptors, and learners (roles may be combined in an implementation). Safety depends on intersecting quorums and protocol rules that prevent conflicting chosen values.

This lesson does not require implementing either protocol. The key concept is that a leader is not safe merely because it claims to be leader; the election and commitment protocol must prevent incompatible leaders from committing conflicting histories.

### 10.2 Why leader election matters

If a leader crashes, a cluster needs a safe way to choose a replacement. Nodes may disagree temporarily about who is leader because messages are delayed. Protocols use terms/epochs, votes, quorum rules, and log checks to ensure the new leader does not overwrite committed history.

A system may stop accepting writes if it cannot obtain the quorum required to safely elect or maintain a leader. That is a deliberate safety-over-availability decision under some failure conditions.

### 10.3 Split brain

**Split brain** occurs when two partitions or nodes both act as independent leaders for the same logical data, potentially accepting conflicting writes.

``` text
Partition 1: A believes it is leader ─► writes x=10
Partition 2: B believes it is leader ─► writes x=20
                         │
                 connectivity returns
                         ▼
               conflict must be resolved
```

A safe leader-election protocol aims to prevent two leaders from committing incompatible operations in the same epoch. Fencing tokens, leases with carefully defined assumptions, quorum protocols, and epoch checks can help prevent stale leaders from continuing to write. A timeout alone is not proof that the previous leader has stopped.

### 10.4 Consensus is not the same as a distributed transaction

Consensus can agree on a log entry or leader, but an application transaction may touch multiple independent systems. Coordinating atomic commit across systems is a separate problem.

## 11. Distributed transactions: two-phase commit and sagas

### 11.1 Two-phase commit (2PC)

Two-phase commit coordinates a transaction across multiple participants.

1.  **Prepare phase:** coordinator asks participants whether they can commit; participants prepare and promise they can commit or abort according to the protocol.
2.  **Commit/abort phase:** coordinator decides and tells participants to commit or abort.

``` text
Coordinator ── PREPARE ──► Participant A
            └─ PREPARE ──► Participant B
                    ▲
              votes/prepare state
                    │
Coordinator ── COMMIT/ABORT ──► Participant A
Coordinator ── COMMIT/ABORT ──► Participant B
```

The important trade-off is that participants may hold resources or remain blocked while waiting for the final decision, especially if the coordinator fails at an unfortunate time. Production implementations require durable logs, recovery protocols, and careful timeout handling. 2PC coordinates atomic commit but is not itself a general-purpose consensus algorithm; systems may combine it with consensus for replicated transaction state.

### 11.2 Sagas

A **saga** breaks a long workflow into local transactions, each with a compensating action if a later step fails.

Example order workflow: 1. Create order (`PENDING`). 2. Reserve inventory. 3. Authorize payment. 4. Confirm order.

If payment fails after inventory is reserved, a compensating action releases the reservation and marks the order failed. Compensation is a new business action, not necessarily a literal rollback of history; it can fail too and needs retries and observability.

Sagas are useful across services that do not share one transaction manager. They provide eventual workflow completion rather than instantaneous atomicity across all participants.

### 11.3 Why some NoSQL systems limit multi-key transactions

Multi-key transactions across partitions require coordination, extra network round trips, logging, and recovery. Those costs can conflict with goals such as low latency, high write throughput, or availability during partitions. Some products offer transactions but limit their scope, throughput, duration, or cost; others encourage single-item atomic operations and access-pattern-first modelling.

Do not conclude that “NoSQL cannot do transactions.” The correct question is which transaction scope, isolation, failure behavior, and cost the selected product supports.

## 12. Jepsen-style consistency testing — awareness

Jepsen is associated with experimental testing of distributed systems by generating concurrent operations, introducing faults (such as process crashes or network partitions), recording operation histories, and checking whether those histories satisfy a formal consistency model.

A simplified test process:

1.  Define a workload and expected model, such as a register where a completed write must be visible to a later linearizable read.
2.  Run concurrent clients that record invocation and response times.
3.  Inject faults: partition nodes, kill processes, delay messages, or restart nodes.
4.  Collect the complete history and database state.
5.  Check whether the observed history could have occurred under the claimed consistency model.
6.  Re-run with different seeds, timing, topologies, and workloads; retain versions and configuration.

A test that finds a counterexample is strong evidence of a bug or a mismatch between implementation and claimed guarantee. A test that finds no counterexample is **not** a mathematical proof: it only covers the tested schedules, workloads, and environment. Formal verification and implementation reasoning are complementary.

For your lab, the Python simulation in the next section teaches one failure pattern. It is not a substitute for testing a real database or a Jepsen-style history checker.

## 13. Hands-on lab: `experiments/02_consistency/`

### Objectives

You will: 1. Trace writes and reads across three replicas. 2. simulate random message delays and observe a stale read with `R=1, W=1`; 3. explain when `R=2, W=2` avoids that stale read; 4. compare Cassandra `ONE` and `QUORUM` while one node is unavailable; 5. demonstrate a last-write-wins lost update and repair it with version checks or a suitable CRDT counter.

### Suggested directory layout

``` text
experiments/
└── 02_consistency/
    ├── README.md
    ├── replica_simulation.py
    ├── lost_update_demo.py
    ├── cassandra_lab.md
    └── results/
        └── observations.md
```

### 13.1 Three-replica trace

Initial state: replicas A, B, and C store `x=0`.

**Case A — write quorum 1, read quorum 1**

1.  Client writes `x=1`.
2.  Replica A stores the value and acknowledges; propagation to B and C is delayed.
3.  The write returns success under this simplified protocol.
4.  A later read is routed to C before C receives the update.
5.  The read returns `x=0`.

A stale read is possible because the read and write sets do not necessarily overlap.

**Case B — write quorum 2, read quorum 2**

1.  Client writes `x=1`; A and B store it and acknowledge.
2.  The write succeeds after two acknowledgements.
3.  A later read queries two replicas.
4.  Under the assumptions below, at least one queried replica has the write, so the read protocol can select `x=1`.

The arithmetic is (R+W=2+2=4\>N=3). This avoids the illustrated stale read only under a restricted model: same fixed replica set, sequential single-writer operations, correct version comparison/read protocol, no concurrent conflicting write, and no configuration change or sloppy-quorum behavior. A real database may have additional rules and guarantees; do not generalize this toy trace to all systems.

### 13.2 Runnable Python simulation

Save as `experiments/02_consistency/replica_simulation.py`. It uses only the Python standard library. The model uses a virtual clock and a queue of messages with randomized delivery times. A fixed seed makes the schedule reproducible. It is an educational model, not a production protocol.

``` python
from __future__ import annotations

import heapq
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class VersionedValue:
    version: int
    value: int


class Replica:
    def __init__(self, name: str) -> None:
        self.name = name
        self.record = VersionedValue(version=0, value=0)

    def apply(self, record: VersionedValue) -> None:
        if record.version > self.record.version:
            self.record = record
        elif (record.version == self.record.version
              and record.value != self.record.value):
            raise ValueError(
                f"conflicting values at version {record.version} on {self.name}"
            )


class Network:
    """Tiny virtual-time network that delivers messages after random delays."""

    def __init__(self, seed: int = 7) -> None:
        self.rng = random.Random(seed)
        self.now = 0.0
        self._events: list[tuple[float, int, Replica, VersionedValue]] = []
        self._sequence = 0

    def send(self, replica: Replica, record: VersionedValue) -> float:
        delay = self.rng.uniform(1.0, 10.0)
        self._sequence += 1
        delivery_time = self.now + delay
        heapq.heappush(
            self._events,
            (delivery_time, self._sequence, replica, record),
        )
        return delivery_time

    def deliver_until(self, deadline: float) -> None:
        while self._events and self._events[0][0] <= deadline:
            delivery_time, _, replica, record = heapq.heappop(self._events)
            self.now = delivery_time
            replica.apply(record)
        self.now = max(self.now, deadline)


def read_one(replica: Replica) -> VersionedValue:
    return replica.record


def read_quorum(replicas: list[Replica], r: int) -> VersionedValue:
    if not 1 <= r <= len(replicas):
        raise ValueError("R must be between 1 and the replica count")
    # Simplified: query the first r replicas and choose the greatest version.
    # This assumes one writer assigns a unique increasing version per update.
    # Real databases have protocol-specific reconciliation and repair rules.
    responses = [replica.record for replica in replicas[:r]]
    return max(responses, key=lambda item: item.version)


def run_demo(seed: int = 7) -> None:
    replicas = [Replica(name) for name in ("A", "B", "C")]
    network = Network(seed=seed)
    new_record = VersionedValue(version=1, value=100)

    # W=1: A stores and acknowledges the write. Updates to B and C are in flight.
    replicas[0].apply(new_record)
    delivery_times = {
        replica.name: network.send(replica, new_record)
        for replica in replicas[1:]
    }
    print("Randomized message delivery times:", delivery_times)
    print("At W=1 acknowledgement:",
          [(r.name, r.record.value, r.record.version) for r in replicas])

    # The write has been acknowledged, but neither delayed message has arrived.
    stale = read_one(replicas[2])
    print(f"R=1 read from C before delivery: value={stale.value}, "
          f"version={stale.version}")

    # Deliver all pending updates. Eventual propagation brings B and C up to date.
    network.deliver_until(max(delivery_times.values()))
    print("After message delivery:",
          [(r.name, r.record.value, r.record.version) for r in replicas])

    # Fresh fixed-set example: W=2 means A and B acknowledge version 1.
    replicas = [Replica(name) for name in ("A", "B", "C")]
    replicas[0].apply(new_record)
    replicas[1].apply(new_record)
    quorum_result = read_quorum(replicas, r=2)
    print("After W=2:", [(r.name, r.record.value, r.record.version)
                         for r in replicas])
    print(f"R=2 result: value={quorum_result.value}, "
          f"version={quorum_result.version}")


if __name__ == "__main__":
    run_demo()
```

Run it with:

``` bash
python replica_simulation.py
```

**Expected qualitative outcome:** the first display shows A at version 1 and B/C at version 0; the read from C is stale. The randomized delivery schedule is printed, then B and C eventually receive version 1. In the second setup, A and B have version 1, so the simplified two-replica read selects version 1. The script prints its actual delivery times and state; do not copy invented timing numbers into your report.

**Simulation limitations:** the network is a virtual-time teaching model; it does not model partitions, retries, concurrent writers, membership changes, durable logs, real quorum protocols, or a database’s conflict-resolution behavior. `read_quorum` queries the first `R` replicas and chooses the greatest version; it does not implement a production read-repair protocol. Modify it only after you can explain these limitations.

### 13.3 Cassandra lab: `ONE` versus `QUORUM` with one node down

Use the three-node Cassandra cluster from the module setup. For a single data center, configure a keyspace with replication factor 3. Example CQL:

``` sql
CREATE KEYSPACE IF NOT EXISTS consistency_lab
WITH replication = {
  'class': 'NetworkTopologyStrategy',
  'datacenter1': 3
};

USE consistency_lab;

CREATE TABLE IF NOT EXISTS consistency_lab.register (
    id text PRIMARY KEY,
    value text,
    version int
);
```

**Important:** replace `datacenter1` with the actual Cassandra data-center name shown by your cluster. Confirm the keyspace replication configuration and that all three nodes are in the intended data center before interpreting results.

#### Procedure

1.  Confirm all three nodes are healthy with the appropriate `nodetool status` output.
2.  Choose a fixed key, such as `id='demo'`, and record the starting value.
3.  With all nodes available, use a fresh test key (for example `one_baseline`) to write at `ONE` and read at `ONE`; record the output. Repeat with a separate key for `QUORUM` write/read.
4.  Stop one node using your local lab’s documented procedure. Confirm the cluster sees one node unavailable and note which node is down.
5.  Use a fresh key for each trial. While one node is down, run a write at `ONE` followed by a read at `ONE`; then use another fresh key for a write at `QUORUM` followed by a read at `QUORUM`. Do not reuse one key across all trials unless you explicitly reset it and account for timestamps.
6.  Record whether each operation succeeds, times out, or returns a value. Do not assume a `ONE` read must be stale: the coordinator may contact a replica that has the latest mutation. The purpose is to observe allowed outcomes under a controlled failure, not to force one result.
7.  Restart the node and observe convergence/repair behavior according to the cluster setup. Do not assume every stale replica repairs instantly.
8.  Capture commands, consistency settings, output, timestamps, and any exceptions in `cassandra_lab.md`.

You can set consistency in `cqlsh` using:

``` sql
CONSISTENCY ONE;
INSERT INTO consistency_lab.register (id, value, version)
VALUES ('demo', 'one-write', 1);

CONSISTENCY QUORUM;
INSERT INTO consistency_lab.register (id, value, version)
VALUES ('demo', 'quorum-write', 2);

CONSISTENCY ONE;
SELECT * FROM consistency_lab.register WHERE id = 'demo';

CONSISTENCY QUORUM;
SELECT * FROM consistency_lab.register WHERE id = 'demo';
```

`CONSISTENCY` is a `cqlsh` shell command, not a CQL statement sent to the server. Run each operation as a separate, controlled trial and use a unique key or reset the record between trials. These statements illustrate the setting, but **they are not a complete experiment by themselves**: explicitly stop a node, record which replica is unavailable, and compare outcomes. Avoid interpreting a single `SELECT` as proof that all replicas are identical. A `ONE` read can return either the newest or an older value depending on which replica responds and what it has applied.

#### Expected behavior under the stated assumptions

For RF=3 in one data center: - `ONE` needs one replica response. With one node down, it can succeed if a reachable replica can serve the request. A read at `ONE` may be stale depending on which replica responds and whether the latest write reached it. - `QUORUM` normally needs two replica responses. With one node down, it can still succeed if the two remaining replicas are reachable and eligible to respond. - If only one of the three replicas is reachable, `QUORUM` cannot obtain two acknowledgements and should fail or time out rather than pretending the quorum succeeded. - `QUORUM` is not “always fresh under every possible concurrent-write scenario.” The selected read/write levels, timestamp conflict resolution, concurrent writes, and repair state still matter.

**Do not fabricate observations.** Your report should separate (a) expected behavior based on the configuration from (b) what your actual cluster printed.

### 13.4 Demonstrate a lost update with LWW

Initial shared document:

``` json
{"theme": "light", "language": "en"}
```

Two clients read the same version.

``` text
Client A reads v1                 Client B reads v1
       │                                  │
       ▼                                  ▼
changes theme to dark             changes language to fr
writes whole document             writes whole document
       │                                  │
       └──────── concurrent writes ───────┘
                        │
                        ▼
             LWW chooses one whole value
```

If A’s replacement wins, the final object may be `{"theme":"dark","language":"en"}` and B’s language change is lost. If B’s wins, A’s theme change is lost. Use the exact same initial state and run the two writes in both orders to demonstrate why the result depends on the conflict rule.

#### Repair option A: version check

Store `version=1`. Each update includes the expected version. The first successful update advances the version to 2; the other update fails because its expected version is stale. The application rereads, merges its independent field change with the current value, and retries against version 2. Verify that the final document contains both `theme="dark"` and `language="fr"`.

This works when the version check and update are atomic. A read-then-unconditional-write is not sufficient.

#### Repair option B: CRDT counter

For an increment counter, demonstrate a G-counter with separate per-replica components:

``` python
def merge_g_counter(left: dict[str, int],
                    right: dict[str, int]) -> dict[str, int]:
    """Merge two G-counter states by taking each component's maximum."""
    keys = left.keys() | right.keys()
    return {key: max(left.get(key, 0), right.get(key, 0)) for key in keys}


replica_a = {"A": 2, "B": 0}
replica_b = {"A": 0, "B": 3}
merged = merge_g_counter(replica_a, replica_b)

assert merged == {"A": 2, "B": 3}
assert sum(merged.values()) == 5
print(merged, sum(merged.values()))
```

This code is runnable Python. It demonstrates a grow-only counter’s merge rule; it does not implement network transport, persistence, replica membership, or decrements. Use version checks for the shared profile object and the G-counter for a counter-like operation—the correct repair depends on the data semantics.

### 13.5 Lab deliverables and evaluation

Submit: - `replica_simulation.py` and a short explanation of the stale-read history. - A quorum table for (N=3) and (N=5), including valid and invalid (R,W) examples. - `cassandra_lab.md` with exact configuration, commands, actual outputs, and a distinction between expected and observed results. - `lost_update_demo.py` or equivalent notes showing the lost update and the repair. - A short paragraph stating why the simulation cannot prove a real database’s consistency guarantees.

| Criterion               | Evidence                                                                                 |
|-------------------------|------------------------------------------------------------------------------------------|
| Correct CAP explanation | Partition-time trade-off; no static “pick two” slogan                                    |
| Consistency models      | Each guarantee and limitation explained with a concrete history                          |
| Quorum arithmetic       | Correct strict inequality and calculations for N=3 and N=5                               |
| Simulation              | Reproducible code, actual output, stated assumptions and limitations                     |
| Cassandra trial         | RF/topology/consistency levels/node failure documented; no fabricated results            |
| Conflict repair         | Lost update reproduced; atomic version check or suitable CRDT explained                  |
| Engineering reasoning   | Correctness, latency, availability, recovery, and data-extraction implications discussed |

## 14. Common mistakes

1.  **Saying “pick two of three.”** CAP’s central conflict appears during a network partition; partition tolerance is not a casual feature toggle.
2.  **Calling a database permanently CP or AP.** Describe the operation, configuration, topology, and failure assumptions.
3.  **Confusing ACID consistency with CAP consistency.** One is about preserving invariants in transactions; the other has a formal latest-write/read meaning.
4.  **Treating eventual consistency as “eventually wrong.”** Eventual convergence can be correct under a defined merge rule, but may lose user intent if the conflict policy is unsuitable.
5.  **Assuming `R+W>N` proves linearizability.** It proves quorum intersection only under assumptions; version selection, concurrency, membership, and protocol behavior matter.
6.  **Ignoring read-your-writes.** Users notice when an update disappears on refresh, even if the system converges later.
7.  **Treating timeout as proof of failure.** The operation may have committed before its response was lost.
8.  **Assuming replication equals backup.** Replicated deletion or corruption can affect all copies.
9.  **Assuming LWW preserves independent updates.** It can discard a valid concurrent write.
10. **Using a CRDT for an invariant it cannot enforce.** A convergent counter is not automatically a safe bank balance.
11. **Equating consensus with distributed transactions.** Consensus on a log and atomic commit across multiple participants are different problems.
12. **Treating a simulation as proof.** A toy model covers only the behavior it implements; real systems need fault testing and contract analysis.

## 15. Practice questions

1.  Why do distributed databases replicate data, and what new problem does replication create?
2.  Define node failure and network partition. Why is a timeout ambiguous?
3.  State CAP precisely. Why is “pick two” misleading?
4.  Give an example where an available response can be stale.
5.  Explain the difference between ACID consistency and CAP consistency.
6.  What does BASE mean, and why is it not a formal protocol?
7.  What history does linearizability forbid that sequential consistency may permit?
8.  What is causal consistency? Give an example of two causally related operations.
9.  How do read-your-writes and monotonic reads differ?
10. Explain PACELC using a normal-operation example and a partition example.
11. For (N=3), does (R=2,W=1) satisfy quorum intersection? Show the arithmetic.
12. For (N=5), does (R=2,W=4) satisfy quorum intersection? What does that alone not prove?
13. Why can Cassandra `QUORUM` still be unavailable when too few replicas respond?
14. In DynamoDB, why must you check whether a particular index supports strongly consistent reads?
15. Distinguish MongoDB read concern, read preference, and write concern.
16. How does leader/follower replication differ from leaderless replication?
17. What is a split brain, and why is a timeout not sufficient to fence an old leader?
18. How can vector clocks distinguish concurrent writes?
19. Why can LWW lose an update even if all replicas eventually converge?
20. What does a saga compensate for, and why is compensation not always a literal rollback?
21. What does Jepsen-style testing do, and why does passing a finite test suite not prove correctness?

## 16. Roadmap-aligned checkpoint

Before moving to Topic 03, verify each item:

- [ ] **State CAP correctly, including partition tolerance.** Explain the behavior choice during a partition and why “pick two” is an incomplete slogan.
- [ ] **Explain PACELC.** State the P→A/C and E→L/C trade-offs.
- [ ] **Choose R and W for a workload.** Calculate (R+W\>N) for (N=3) and (N=5), and name the assumptions behind the conclusion.
- [ ] **Explain read-your-writes and why users notice its absence.** Give a realistic example.
- [ ] **Name two ways to resolve write conflicts.** For example, version checks, application merge, vector/version metadata, or CRDTs.
- [ ] Distinguish ACID consistency from CAP consistency and explain BASE.
- [ ] Compare all six consistency models from this lesson.
- [ ] Explain the difference between leader/follower, multi-leader, and leaderless replication.
- [ ] Describe consensus, leader election, split brain, 2PC, and sagas at awareness level.
- [ ] Complete the simulation and Cassandra failure experiment without claiming unobserved results.

## 17. Final self-assessment

Score each skill 0–2: **0** = cannot explain; **1** = can explain with notes; **2** = can reason through a new example.

| Skill                                                                                   | Score (0–2) |
|-----------------------------------------------------------------------------------------|------------:|
| Explain replication, node failures, and partitions                                      |             |
| State CAP precisely and correct the “pick two” misconception                            |             |
| Distinguish ACID consistency, CAP consistency, and BASE                                 |             |
| Explain linearizability and sequential consistency                                      |             |
| Explain causal consistency, read-your-writes, monotonic reads, and eventual consistency |             |
| Explain PACELC                                                                          |             |
| Calculate and qualify quorum intersection for N=3 and N=5                               |             |
| Explain Cassandra, DynamoDB, and MongoDB consistency controls                           |             |
| Compare replication architectures and identify replication lag symptoms                 |             |
| Explain LWW, vector clocks/version vectors, CRDTs, and version checks                   |             |
| Explain consensus, split brain, 2PC, sagas, and Jepsen-style testing                    |             |
| Complete all roadmap experiments with honest evidence and limitations                   |             |
| **Total (maximum 24)**                                                                  |             |

Suggested interpretation: - **0–12:** Revisit the diagrams and consistency-model examples before proceeding. - **13–18:** Core vocabulary is developing; redo quorum calculations and the lab. - **19–24:** Ready for Topic 03 if you can explain the assumptions behind every guarantee, not just name the terms.

## 18. Technical references and version notes

Use these official references to verify behavior against the versions and deployment modes you run; product guarantees evolve and configuration matters.

- Apache Cassandra 5.0 documentation: [Dynamo-style replication and tunable consistency](https://cassandra.apache.org/doc/stable/cassandra/architecture/dynamo), [cqlsh `CONSISTENCY` command](https://cassandra.apache.org/doc/stable/cassandra/managing/tools/cqlsh.html), and [read repair](https://cassandra.apache.org/doc/stable/cassandra/managing/operating/read_repair.html).
- Amazon DynamoDB documentation: [read consistency](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html). Check table, local secondary index, global secondary index, stream, and global-table mode separately.
- MongoDB documentation: [read concern](https://www.mongodb.com/docs/manual/reference/read-concern/) and [causal consistency with read/write concerns](https://www.mongodb.com/docs/manual/core/causal-consistency-read-write-concerns/).
- Jepsen: [consistency models](https://jepsen.io/consistency/models) and [Jepsen framework](https://github.com/jepsen-io/jepsen).

These references support independent study; they do not imply that a live database integration test was run as part of this lesson audit.

---

## Summary

Replication improves capacity and resilience but means copies may temporarily disagree. CAP explains why, during a network partition, a system cannot guarantee both that every request succeeds and that every successful read returns the latest value. ACID consistency is about preserving invariants; CAP consistency has a specific distributed-read meaning. Consistency models describe different guarantees, from linearizability to eventual convergence, while PACELC highlights the latency/consistency trade-off even when the network is healthy.

Quorum arithmetic is useful, but (R+W\>N) is an intersection condition—not a universal proof of linearizability. Real behavior depends on replica membership, protocol, version/conflict rules, and product configuration. As a data engineer, understand those guarantees because they shape CDC, incremental extraction, replay, reconciliation, and what downstream lakehouse tables can truthfully claim about freshness.

**Next lesson:** `03-mongodb-document-modelling-and-aggregation.md` — apply consistency and replication vocabulary to MongoDB replica sets, read/write concerns, and transactions.
