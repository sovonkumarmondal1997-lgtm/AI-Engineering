# Data Replication and Consistency Across Regions

> **Stage:** Stage 2E --- Production DevOps & Platform Engineering\
> **Module:** M14 --- Multi-Cluster and Multi-Region Operations\
> **Unit:** 7\
> **Target filename:**
> `07-data-replication-and-consistency-across-regions.md`\
> **Target path:**
> `Stage 2E — Production DevOps & Platform Engineering/14-Multi-Cluster-and-Multi-Region-Operations/07-data-replication-and-consistency-across-regions.md`\
> **Estimated study time:** 30--50 hours, illustrative\
> **Prerequisites:** M13 DR units; M14 Units 1--6; Kubernetes/stateful
> workloads, PostgreSQL fundamentals, observability, GitOps, SRE/SLOs,
> data contracts, and schema evolution\
> **Budget:** zero; laptop-based WSL2 Ubuntu or native Linux;
> approximately 4 CPU, 8 GB RAM, 30 GB free disk\
> **Review status:** authored 2026-10-29; live official documentation
> was not consulted in this authoring pass; labs were not executed.

**Authenticity labels used throughout**

-   **\[ROADMAP REQUIREMENT\]** Explicit curriculum requirement from the
    supplied Unit 7 prompt.
-   **\[TECHNICAL FACT\]** General distributed-systems or database fact;
    product/version details still require verification where noted.
-   **\[RECOMMENDATION\]** Conditional engineering advice, with
    assumptions stated.
-   **\[ASSUMPTION\]** A premise used in an example.
-   **\[SYNTHETIC\] / \[ILLUSTRATIVE\]** Example data or expected
    output, not a real measurement.
-   **\[VERIFY\]** A version-sensitive or environment-specific detail
    that must be checked before use.

Never infer that a command succeeded because it appears in this lesson.
No cluster, database, replication setup, failure drill, or production
environment was operated while authoring this document.

------------------------------------------------------------------------

## 1. Learning outcomes

By the end of this unit, you should be able to:

1.  Explain why data is replicated and why wide-area network (WAN)
    latency, partitions, ordering, and concurrent writes make it
    difficult.
2.  Distinguish linearizability, sequential consistency, causal
    consistency, read-your-writes, monotonic reads/writes, eventual
    consistency, and bounded staleness.
3.  Explain CAP and PACELC without reducing CAP to a simplistic "pick
    any two" slogan.
4.  Compare primary/replica, multi-leader, leaderless/quorum,
    consensus-based, synchronous, asynchronous, and semi-synchronous
    designs.
5.  Compare physical/WAL, logical, storage-level, application-level,
    outbox/CDC, stream-mirroring, and object-store replication.
6.  Measure lag at idle and under load, report percentiles only when
    sample size supports them, and estimate a scenario RPO without
    pretending lag alone guarantees data loss.
7.  Explain synchronous commit latency and availability coupling,
    asynchronous acknowledged-write loss, promotion, and fencing.
8.  Demonstrate stale reads and read-your-writes/monotonic-read
    mitigations with explicit limitations.
9.  Identify replication-slot/WAL-retention hazards, schema
    incompatibility, divergence, duplicate/reordered events, and delete
    propagation.
10. Define consistency requirements for at least 12 dataset classes.
11. Gate model alias promotion on artifact availability and hash
    verification.
12. Demonstrate a toy multi-writer last-writer-wins (LWW) lost update
    and redesign it using partitioned ownership, a suitable CRDT-like
    structure, or explicit merge/reconciliation.
13. Explain quorum placement across two versus three failure domains and
    why automatic failover needs a valid majority and fencing design.
14. Verify object replication, deletion behavior, schema compatibility,
    and divergence detection.
15. Design replication SLOs, alerts, readiness/parity checks, region
    seeding/decommission plans, runbooks, and architecture decision
    records (ADRs).
16. Make a safe failover recommendation when lag exceeds the business
    RPO and stakeholders demand an immediate traffic shift.
17. Explain exactly what a local simulation demonstrates---and what it
    does not.

------------------------------------------------------------------------

## 2. Scope and links to adjacent units

Replication is a mechanism, not a disaster-recovery strategy by itself.
Copies can improve availability and locality, but they can also
reproduce accidental deletion, corrupted writes, compromised
credentials, and bad schema changes.

This unit teaches replication mechanisms, consistency semantics, data
integrity, and region-to-region operating policy. It does not replace
the surrounding roadmap units:

-   **M13 Unit 1:** business criticality and RTO/RPO definitions.
-   **M13 Unit 2:** backup scope, immutability, and why a replica is not
    a backup.
-   **M13 Unit 4:** idempotency, replay, queue and pipeline recovery.
-   **M13 Unit 5:** model artifacts and registry metadata recovery.
-   **M13 Unit 6:** promotion, fencing, split-brain, failover/fail-back
    mechanics.
-   **M13 Unit 7:** restore drills and evidence conventions.
-   **M13 Units 8/10:** bounded fault injection and chaos experiments.
-   **M14 Unit 1:** cluster topology, cells, and failure domains.
-   **M14 Unit 3:** GitOps/config parity and safe changes.
-   **M14 Unit 4:** cross-cluster connectivity and service routing.
-   **M14 Unit 5:** global traffic and failover timing.
-   **M14 Unit 6:** active-active/active-passive patterns and
    home-region ownership.
-   **M14 Unit 8:** fleet observability and policy governance.
-   **M08 Unit 11:** schema evolution/migration safety; **M08 Unit 12:**
    data contracts.
-   **M09:** secrets, identity, and key access.
-   **M10:** SLOs, incident command, load shedding, communication, and
    postmortems.
-   **M11:** monitoring, alerting, capacity, and load experiments.
-   **M15:** cost, egress, capacity, and FinOps.

**Boundary:** M13 Unit 6 taught DR strategy and failure handling:
failure domains, dependency outages, the DR strategy spectrum, failover
and fail-back drills, split-brain/fencing, and post-failover steady
state, using a primary and a DR cluster. This unit adds the steady-state
data replication and consistency choices, how to measure them, how they
can fail, and how to govern data integrity across regions. Refer back to
M13 for actual promotion/fencing procedures rather than duplicating
them.

------------------------------------------------------------------------

## 3. Why replicate---and why it is difficult

### 3.1 Legitimate reasons to replicate

-   **Availability and disaster recovery:** maintain another copy that
    may be used after failure. The acceptable data-loss window and
    restoration time are business requirements; see M13 Unit 1.
-   **Read latency:** serve read-heavy workloads near users, if
    stale-read semantics are acceptable.
-   **Data locality/residency:** place data and processing within
    permitted boundaries. A database copy is only one part of residency;
    backups, logs, telemetry, feature stores, model artifacts, and
    support access also matter.
-   **Regional evacuation and migration:** move workloads while
    preserving a defined data state.
-   **Data/ML platforms:** replicate model artifacts, feature snapshots,
    registry metadata, object data, streaming events, and pipeline
    state.
-   **Operational autonomy:** allow a region to continue limited work
    when a central control plane is unavailable, if the design supports
    it.

### 3.2 The hard parts

WAN round-trip time is not zero. Links can lose packets, become
asymmetric, partition, or recover with bursts of queued traffic. A
replica can be alive but stale. Two replicas can both be reachable and
still disagree. More copies create costs for coordination, retention,
encryption/key management, monitoring, delete governance, schema
compatibility, and incident response.

**\[TECHNICAL FACT\]** Under a network partition, a distributed data
service cannot guarantee every operation will complete while also
preserving a single strongly consistent view across the partition. The
actual trade-off depends on the operation, model, topology, and failure
assumptions. Avoid the slogan "always pick two of three"; it is not a
useful design procedure.

A good design starts with the data invariant and the user-visible
guarantee, then chooses a mechanism. Do not start with a product logo or
"multi-region" as the goal.

------------------------------------------------------------------------

# L1 --- Fundamentals and vocabulary

## 4. Consistency models

Consistency describes what clients are allowed to observe when
operations overlap, replicate, or fail. Product labels vary; check the
selected system's formal guarantee and documentation **\[VERIFY\]**.

  ------------------------------------------------------------------------------------------
  Model                  Meaning                        User-visible      Important caveat
                                                        example           
  ---------------------- ------------------------------ ----------------- ------------------
  **Strong consistency / Each operation appears to take After a confirmed May require
  linearizability**      effect at one point between    account update, a coordination and
                         invocation and response,       later read sees   incur latency or
                         respecting real-time order of  it, assuming the  availability costs
                         non-overlapping operations.    same linearizable under partitions.
                                                        data item and     
                                                        healthy contract. 

  **Sequential           Operations appear in one       A client's writes The global order
  consistency**          global order that preserves    are not reordered need not respect
                         each process's program order.  relative to one   real-time order
                                                        another in the    between different
                                                        observed          clients.
                                                        sequence.         

  **Causal consistency** Causally related operations    A reply should    Requires a defined
                         preserve their order.          not appear before causal
                         Concurrent operations may be   the message it    relationship and
                         observed in different orders.  replies to.       system support;
                                                                          does not mean all
                                                                          concurrent writes
                                                                          agree immediately.

  **Read-your-writes**   A client can observe its own   A profile edit is May require
                         completed writes in subsequent visible to the    session affinity,
                         reads under the stated         same user after   a version token,
                         guarantee.                     saving.           or reading from
                                                                          the authority; not
                                                                          necessarily a
                                                                          global guarantee.

  **Monotonic reads**    Once a client has observed a   A dashboard does  Session routing
                         version, later reads in that   not move backward and failover can
                         session do not return an older from version 12   break this if not
                         version under the model's      to version 10.    designed
                         guarantee.                                       explicitly.

  **Monotonic writes**   A client's writes are          A rename is       Ordering across
                         applied/observed in the        applied before a  independent
                         required order.                later update      clients is a
                                                        based on the      separate problem.
                                                        renamed object.   

  **Eventual             If updates stop and            Two read replicas Does not specify
  consistency**          communication/reconciliation   may temporarily   how long
                         proceeds under the system's    differ, then      convergence takes
                         assumptions, replicas          converge.         or prevent bad
                         eventually converge.                             conflict
                                                                          resolution.

  **Bounded staleness**  Staleness is limited by a      A read is no more The exact bound,
                         declared bound such as time,   than a stated     enforcement, and
                         version distance, or log       number of         behavior when the
                         position, with precise         versions behind.  bound cannot be
                         semantics.                                       met are
                                                                          system-specific.
  ------------------------------------------------------------------------------------------

### 4.1 A stale-read timeline

``` text
t0  Client writes profile version 18 to primary East.
t1  East commits version 18 and acknowledges success.
t2  West replica has only applied version 17.
t3  Client reads West and sees version 17.
t4  West applies version 18; subsequent reads can see version 18.
```

This is an illustrative asynchronous-replication timeline, not a
guarantee about every product.

### 4.2 Read-your-writes mitigations

1.  **Session pinning to the primary/authority:** after a successful
    write, direct that session's reads to the write authority for a
    bounded interval. A time window is not a correctness guarantee if
    lag or outages exceed it.
2.  **Version/position token:** return a committed version or
    replication position and wait until the replica has applied it.
    Database-specific replay-position APIs and semantics must be
    verified **\[VERIFY\]**.
3.  **Client-visible pending state:** the application may display the
    confirmed write result while a replica catches up, provided it does
    not falsely label stale reads as fresh.
4.  **Read policy:** route a read to the authority if its freshness
    requirement is stricter than the replica can prove.

Monotonic reads can use a session's last-seen version as a lower bound
and refuse or reroute reads that would move backward. This adds
complexity; define timeout behavior when no replica can satisfy the
bound.

## 5. CAP and PACELC

### 5.1 CAP, carefully stated

-   **Consistency (C):** in the common CAP formulation, operations
    behave according to a single-copy/linearizable consistency model.
-   **Availability (A):** every request received by a non-failing node
    receives a response, though that response need not be the newest
    value under a weaker model.
-   **Partition tolerance (P):** the system continues to operate despite
    communication loss between parts of the system.

When a partition separates nodes that need to coordinate, a system
preserving linearizable consistency may have to reject or wait on some
operations. A system continuing to answer on both sides may have to
weaken consistency for those operations. The choice is per system and
sometimes per operation; it is not a universal "choose any two" menu
because a network partition is a failure condition that real distributed
systems must account for.

**Worked partition example \[ILLUSTRATIVE\]:** East and West both have a
copy of a bank balance. A network partition prevents coordination. If
both sides accept withdrawals based on their local copy, they can
jointly violate the balance invariant. If only the designated authority
accepts writes, the other side may reject writes during the partition.
Which behavior is acceptable is a business and data-integrity decision.

### 5.2 PACELC

PACELC extends the trade-off framing: **if a partition occurs (P), trade
availability (A) against consistency (C); else (E), trade latency (L)
against consistency (C).**

**Normal-operation example \[ILLUSTRATIVE\]:** a read could contact a
nearby replica quickly and risk stale data, or coordinate with a remote
authority for a stronger guarantee at greater latency. Even with no
partition, the system may trade latency against consistency.

CAP and PACELC are conceptual models, not substitute requirements
documents. State the actual operation, failure mode, guarantee, and
evidence. Attribution/details should be checked against the cited
distributed-systems source before publication **\[VERIFY\]**.

## 6. Replication topologies

### 6.1 Primary--replica / single leader

One authority accepts writes and propagates changes to replicas. Reads
may go to the primary or replicas depending on freshness requirements.
This is often easier to reason about because concurrent writes to the
same data are serialized at one authority.

-   **Strengths:** clear write authority; easier conflict model;
    familiar operational workflow.
-   **Trade-offs:** primary is a critical dependency; remote writes pay
    network latency; asynchronous replicas may be stale or miss recently
    acknowledged writes after a failure.
-   **Failure behavior:** failover requires a controlled decision about
    data freshness, old-primary fencing, and new-primary authority. A
    reachable replica is not automatically safe to promote.
-   **Evidence:** write authority, lag distribution, replica apply rate,
    promotion gate, and stale-read tests.

### 6.2 Multi-leader / multi-primary

Multiple sites accept writes and replicate them. Writes may conflict or
arrive out of order.

-   **Strengths:** local write availability/latency for selected
    workloads.
-   **Trade-offs:** conflict semantics, clock/order assumptions,
    uniqueness, deletes, transactions, reconciliation, and on-call
    complexity.
-   **Appropriate when:** writes are naturally partitioned or merge
    semantics are explicitly correct and tested.
-   **Avoid when:** correctness depends on global uniqueness or
    multi-object invariants that the system cannot preserve under
    concurrent writes.
-   **Evidence:** conflict tests, invariant checks, reconciliation
    backlog, duplicate/reorder tests, and partition-heal drills.

### 6.3 Leaderless/quorum replication

A write may be sent to multiple replicas and considered successful after
a configured number of acknowledgements. Common notation uses (N)
replicas, (W) acknowledgements required for a write, and (R) replicas
consulted for a read.

A frequently used intuition is that (W + R \> N) makes read and write
replica sets overlap. **This overlap alone does not guarantee a
linearizable read or the desired freshness**: concurrent writes, version
selection, sloppy quorums, hinted handoff, conflict resolution, replica
membership, and failure semantics matter. Verify the actual database's
quorum and read-repair behavior **\[VERIFY\]**.

### 6.4 Consensus-based replication

Protocols in the Raft/Paxos family use a defined voting/consensus
protocol to establish an ordered authoritative log or state under
specified failure assumptions.

-   A majority is a property of the configured voting set, not a synonym
    for "two regions."
-   Three independent failure domains can be useful if voter placement
    and network paths actually allow a majority to survive the intended
    loss.
-   In a two-voter design, loss of either voter leaves no majority. A
    witness/tie-breaker can change the outcome only according to its
    protocol and placement; verify the product behavior **\[VERIFY\]**.
-   Do not assert that a design tolerates region loss without
    enumerating voter placement, quorum requirements, and failure
    assumptions.
-   Never recommend automatic promotion without a split-brain
    prevention/fencing plan. See M13 Unit 6.

### 6.5 Two-region versus three-region quorum placement

``` text
Two-region, two-voter illustration:
  East [Voter A] <------ WAN ------> West [Voter B]
  Loss of either voter leaves no majority in a 2-voter majority system.

Three failure domains, three voters:
  East [A] <----> Central [B] <----> West [C]
     \_______________________________/
       A majority of 2 can remain after
       one voter/domain is lost, if the
       protocol and placement support it.
```

The diagram is conceptual. Real quorum placement depends on the
product's voting membership, witness semantics, failure-domain
awareness, network topology, and reconfiguration rules **\[VERIFY\]**. A
third voter sharing power/network with another site may not be an
independent failure domain.

### 6.6 Synchronous, asynchronous, and semi-synchronous replication

  -----------------------------------------------------------------------------------------------------------
  Mode               Acknowledgement     Benefit              Cost/risk                Evidence to gather
                     condition                                                         
  ------------------ ------------------- -------------------- ------------------------ ----------------------
  Synchronous        Commit waits for    Can reduce           Added latency; writes    Commit
                     the configured      acknowledged-write   may block/fail if        latency/throughput,
                     remote              loss within stated   required replica/network unavailable-standby
                     acknowledgement     durability/failure   unavailable.             behavior, exact
                     condition.          assumptions.                                  configuration,
                                                                                       promotion semantics.

  Asynchronous       Primary can         Lower foreground     Acknowledged writes may  Lag distribution, last
                     acknowledge before  latency and less     be lost if primary fails acknowledged/applied
                     remote replica      coupling to replica  before changes reach a   positions,
                     applies/receives    availability.        promoted replica.        failover-loss
                     the change.                                                       exercise.

  Semi-synchronous / Waits for a         Middle ground under  Semantics vary; may      Exact documented
  quorum commit      system-specific     particular failure   acknowledge before       guarantee and failure
                     subset/phase of     assumptions.         remote apply or durable  tests.
                     acknowledgements.                        flush depending on       
                                                              product/configuration.   
  -----------------------------------------------------------------------------------------------------------

"RPO approximately zero" is never unconditional. It depends on what
acknowledgement means, which copies have durably received data, storage
assumptions, the failure model, and the promotion procedure.

### 6.7 Acknowledged-write-loss timeline

``` text
t0  Primary commits write IDs 101–110.
t1  Primary acknowledges those writes to clients.
t2  Async replica has applied only through ID 106.
t3  Primary becomes unavailable.
t4  Approved recovery process selects a safe authority based on evidence.
t5  If a replica missing IDs 107–110 is promoted, those acknowledged writes
    may be absent from the new primary.
```

This is a synthetic failure scenario. Do not convert the timeline into a
universal claim about a particular database.

## 7. Replication methods

  --------------------------------------------------------------------------------------------------------------------
  Method               Unit copied                Advantages        Failure/consistency risks Verification
  -------------------- -------------------------- ----------------- ------------------------- ------------------------
  Physical/WAL         Database physical          Efficient         Version/configuration     Lag/apply positions,
  streaming or archive changes/log records        whole-instance    coupling; lag; WAL        recovery state,
  shipping                                        replication;      retention;                version-specific
                                                  compatible with   promotion/data-loss risk  PostgreSQL docs
                                                  physical standby                            
                                                  use cases                                   

  Logical replication  Selected logical changes   Selective         DDL/schema compatibility, Schema compatibility
                       such as rows/publications  tables/data flows replica identity,         matrix, row counts,
                                                  and some          ordering/initial copy,    version-specific docs
                                                  migration         sequence/object behavior  
                                                  patterns                                    

  Storage/block        Blocks/volumes             Can replicate at  Crash                     Vendor-specific
  replication                                     storage layer     consistency/application   durability/consistency
                                                  without app-level quiescing, write          tests; application
                                                  row logic         ordering, split-brain and restore validation
                                                                    storage ownership         

  Application dual     Application writes to two  Application can   Partial success, retries, Fault injection between
  writes               destinations               tailor data       duplicate writes,         writes; idempotency and
                                                  model/semantics   inconsistent outcomes     reconciliation

  Transactional        Transactional event/outbox Couples business  Duplicate delivery, lag,  Outbox backlog,
  outbox + CDC         rows emitted downstream    transaction and   schema evolution, poison  replay/idempotency,
                                                  event record in   events                    event-version tests
                                                  one local                                   
                                                  transaction                                 

  Stream/topic         Events/topics/partitions   Regional          Duplicate delivery,       Event IDs, offsets,
  mirroring                                       consumers and     offset mapping, ordering, ordering assertions,
                                                  streaming         lag, replay semantics     consumer idempotency
                                                  locality                                    

  Object/bucket/site   Objects, versions,         Regional          Replication delay, delete Inventory, hashes,
  replication          metadata, possibly delete  artifact/data     propagation, version      object-version/delete
                       markers                    availability      semantics,                tests, provider docs
                                                                    credentials/residency     
  --------------------------------------------------------------------------------------------------------------------

**\[VERIFY\] PostgreSQL logical replication:** exact DDL behavior,
supported version combinations, replica identity, sequence behavior,
slot management, and synchronization details depend on PostgreSQL
versions and configuration. Do not assume DDL is automatically
replicated.

**\[VERIFY\] Object stores:** replication rules, versioning, delete
markers, metadata, encryption keys, and existing-object backfill differ
by product/version. Verify the selected system's current official
documentation before configuring it.

------------------------------------------------------------------------

# Baseline architecture and fidelity limits

## 8. Zero-budget east/west lab

The intended scenario is a PostgreSQL primary in east and a
standby/replica in west, plus an optional object-store replication
exercise. Use the exact cluster names `stage2e-east-lab` and
`stage2e-west-lab` only if they match the supplied roadmap and actual
kubeconfig. Verify contexts first.

``` text
Client/workload generator
          |
          v
  East API / writer
          |
          v
  PostgreSQL primary (East)
          |
          | WAL/replication stream
          v
  PostgreSQL standby/replica (West) ---> local read test
          |
          +---- optional object replication: East -> West
                 model artifacts / manifests / hashes
```

**Fidelity caveat --- mandatory:** two `kind` clusters on one laptop are
not two real geographic regions. They share host, power, storage,
kernel, and often networking. Laptop networking has little natural
geographic latency or packet loss; inject or simulate faults in a
bounded lab. Results demonstrate the workflow and selected mechanisms
only. They do not establish real-WAN performance, true regional
isolation, production RPO, database correctness, or multi-region
resilience. Absence of anomalies in a lab is not proof of correctness.

### 8.1 Resource-aware execution order

1.  Run preflight and record versions/context mapping.
2.  Run PostgreSQL pair only.
3.  Stop unnecessary services before object-store/stream labs.
4.  Use a deterministic toy simulator for a specific anomaly when a real
    component is too expensive.
5.  Label every observation as `[LOCAL LAB MEASUREMENT]`, `[SYNTHETIC]`,
    or `[EXPECTED — ILLUSTRATIVE]`.
6.  Do not combine all Kubernetes, database, object-store,
    observability, and chaos components simultaneously on an 8 GB
    laptop.

### 8.2 Preflight and explicit contexts

``` bash
kind get clusters
kubectl config get-contexts
kubectl config current-context
docker info --format '{{.ServerVersion}}'
python3 --version
git --version
free -h
df -h .
```

Read output before any mutation. Verify the real context names and
cluster identities; examples are not authoritative. Use explicit context
flags on all Kubernetes commands:

``` bash
kubectl --context kind-stage2e-east-lab get nodes
kubectl --context kind-stage2e-west-lab get nodes
kubectl --context kind-stage2e-east-lab get namespaces
kubectl --context kind-stage2e-west-lab get namespaces
```

If names do not match, stop and map the actual throwaway contexts. Do
not create or delete clusters until the mapping is verified.

### 8.3 Choosing PostgreSQL setup

Preferred options, in order of feasibility:

-   **Option A:** CloudNativePG replica-cluster feature only if the
    exact feature, installed version, supported topology, and resource
    footprint are verified in current official docs **\[VERIFY\]**.
-   **Option B:** two plain PostgreSQL containers/pods with a documented
    physical streaming or WAL-archive setup. Verify exact version,
    settings, replication role, access, and promotion behavior
    **\[VERIFY\]**.
-   **Option C:** deterministic simulation for a specific consistency
    anomaly if the database pair exceeds the laptop budget. This teaches
    state transitions, not PostgreSQL behavior.

No operator API or replication command is prescribed as established here
because no target versions were supplied or live-verified. Before
implementing, pin versions and check the official PostgreSQL
documentation and selected operator docs.

------------------------------------------------------------------------

# L2 --- Hands-on replication operations

## 9. Lag measurement and RPO reasoning

### 9.1 What "lag" can mean

-   **Network lag:** delay moving bytes/events across the link.
-   **Receive lag:** delay before the replica receives changes.
-   **Apply/replay lag:** delay before received changes become visible
    in the replica's data.
-   **Byte/position lag:** distance between log positions; conversion to
    time depends on write rate and is not a universal time estimate.
-   **Heartbeat freshness:** age of the latest primary-generated canary
    visible at the replica.
-   **End-to-end freshness:** time between a source event/write and its
    availability to the intended consumer.

These are not interchangeable. A replica can receive data quickly but
apply slowly; a low byte lag at a quiet period may still represent an
important stale business record.

### 9.2 PostgreSQL instrumentation

PostgreSQL exposes replication-related statistics and functions,
including views/functions commonly used for sender/receiver state, WAL
positions, and replay status. Exact names, columns, privilege
requirements, and semantics vary by version. Consult the installed
version's official documentation for `pg_stat_replication`,
`pg_stat_wal_receiver`, WAL LSN functions, replay functions, synchronous
commit, replication slots, and standby behavior **\[VERIFY\]** before
using SQL.

Do not infer RPO solely from a single lag column. Record: - timestamp
and clock source; - write rate; - primary and replica log positions
where available; - receive and replay state; - last canary
sequence/version; - replica health and query visibility; - network
condition and workload; - whether the observation is fresh.

### 9.3 Canary heartbeat method

A canary heartbeat is a small record written on the primary with a
monotonic sequence and timestamp. A measurement process polls the
replica and records when each sequence becomes visible.

``` text
Primary: write seq=501 at t0
Replica: seq=500 visible at t1
Replica: seq=501 visible at t2
Observed end-to-end freshness for seq=501 = t2 - t0
```

This includes more than network transit: scheduling, write/commit,
replication, apply, polling, and clock effects may contribute. Use a
monotonic clock for local elapsed intervals when possible. Timestamp
comparisons across hosts can be distorted by clock skew. In the laptop
lab, distinguish same-host monotonic duration from cross-host wall-clock
comparisons.

### 9.4 Percentiles and sample size

Capture a sample for each scenario: idle, steady load, burst/backfill,
injected delay, standby unavailable, and recovery. Report
p50/p95/p99/p99.9 only when the sample count and sampling design support
meaningful tail estimates. With a small sample, p99.9 is not credible;
report sample count and maximum observed value instead.

**Results template --- fill only with actual observations:**

  ------------------------------------------------------------------------------------------------------------
  Scenario              Sample     p50     p95     p99   p99.9        Max   Write Network     Interpretation
                         count                                   observed    rate condition   
  ------------------- -------- ------- ------- ------- ------- ---------- ------- ----------- ----------------
  Idle                     ---     ---     ---     ---     ---        ---     --- baseline    Not measured

  Steady load              ---     ---     ---     ---     ---        ---     --- baseline    Not measured

  Backfill/burst           ---     ---     ---     ---     ---        ---     --- baseline    Not measured

  Injected delay/loss      ---     ---     ---     ---     ---        ---     --- injected    Not measured

  Recovery/catch-up        ---     ---     ---     ---     ---        ---     --- restored    Not measured
  ------------------------------------------------------------------------------------------------------------

### 9.5 RPO estimate from observed lag

An observed lag can help estimate a potential data-loss window, but it
is not by itself a guarantee of actual loss. The relevant evidence
includes which writes were acknowledged, which changes reached/durably
persisted on the candidate replica, the exact failure, commit mode, and
promotion path.

A simple scenario estimate:

\[ `\text{Observed heartbeat age}`{=tex} = t\_{`\text{now}`{=tex}} -
t\_{`\text{last visible canary}`{=tex}} \]

If a canary last visible on the replica is 42 seconds old, the
observation is **\[SYNTHETIC\]** evidence that this canary path is at
least 42 seconds behind at that sample time. It does not prove exactly
42 seconds of acknowledged business writes will be lost. Writes can be
bursty, canary cadence can be sparse, and database commit/replication
semantics matter.

Use sequence IDs to count missing acknowledged writes in a controlled
experiment. Label the result as the loss observed in that scenario, not
a universal RPO guarantee.

## 10. Lag sources and WAL-retention hazards

  ----------------------------------------------------------------------------------
  Cause                  Typical signal          Why it matters    Safe response
                                                                   direction
  ---------------------- ----------------------- ----------------- -----------------
  WAN latency, bandwidth Network                 Replica receives  Validate
  limit, packet loss     throughput/retransmit   changes more      link/fault;
                         and lag increase        slowly            reduce
                                                                   unnecessary
                                                                   transfer; bound
                                                                   workload

  Replica apply          Receive advances faster Data arrives but  Inspect replica
  bottleneck             than replay/apply       remains stale     CPU/I/O/query
                                                                   conflicts and
                                                                   apply rate

  Long-running           Apply delay, blocked    Some changes may  Diagnose queries
  query/conflict         replay or conflicts     wait for          and documented
                                                 conflicting work  conflict behavior

  Bulk                   Lag and WAL generation  Source produces   Throttle,
  load/backfill/schema   spike                   changes faster    schedule, monitor
  lock                                           than replica can  catch-up
                                                 catch up          

  Replication slot       Retained WAL grows      Primary disk can  Alert on slot lag
  retains WAL            while consumer is       fill, threatening and disk
                         down/slow               the primary       headroom; assess
                                                 itself            consumer/reseed
                                                                   plan

  Storage pressure       I/O latency, disk       Both primary and  Stop or throttle
                         pressure, growing       replica may       source workload
                         queues                  degrade           under approved
                                                                   plan; restore
                                                                   capacity

  Replica disconnected   Receiver status stale,  Read freshness    Alert, assess
                         lag unbounded           and failover      whether catch-up
                                                 safety            is possible,
                                                 deteriorate       repair or reseed
                                                                   safely
  ----------------------------------------------------------------------------------

A disconnected or slow logical/physical consumer may retain WAL
depending on configuration. A replication slot that retains WAL until
the primary disk fills can turn a replica problem into a primary outage.

**Safe mitigation sequence:** 1. Alert on retained WAL bytes, slot lag,
disk free/headroom, replica apply rate, and consumer status. 2. Confirm
the affected slot/consumer and whether it can catch up. 3. Throttle/stop
the source workload if needed to protect the primary. 4. Repair the
consumer or re-seed from a verified source if it cannot catch up. 5.
Only remove a slot after confirming its identity, consequences, and
reseed/recovery plan. Never blindly drop a slot. 6. Verify the replica
is current enough for its stated role and that disk headroom recovered.

`max_slot_wal_keep_size` and related settings are version-sensitive;
verify exact semantics against the target PostgreSQL version
**\[VERIFY\]**. Do not copy a setting into production from this lesson.

## 11. Synchronous versus asynchronous experiment

### Objective

Measure write latency, throughput, replication lag, and behavior when
the standby is unavailable under two documented configurations.

### Experimental protocol

1.  Pin the PostgreSQL version and capture configuration/cluster
    identity.
2.  Choose a bounded synthetic workload and a fixed duration; use the
    same workload for both modes.
3.  Record p50/p95/p99 write latency, successful writes/sec,
    errors/timeouts, replica lag, and primary/replica resource use.
4.  Test normal standby operation.
5.  Make the standby unavailable only within the disposable lab. Observe
    whether writes block, fail, or proceed according to the exact
    configuration.
6.  Restore connectivity and observe catch-up.
7.  Repeat enough times to distinguish repeatable behavior from one
    noisy run.
8.  Do not compare different request mixes or quietly change timeouts
    between modes.

**Results template:**

  -----------------------------------------------------------------------------------------------------------------------
  Mode/config      Standby state     Samples Write         Throughput   Errors/timeouts   Lag            Interpretation
  revision                                   p50/p95/p99                                  observations   
  ---------------- ------------- ----------- ------------- ------------ ----------------- -------------- ----------------
  Async / version: Available             --- ---           ---          ---               ---            Not measured
  \_\_\_                                                                                                 

  Async / version: Unavailable           --- ---           ---          ---               ---            Not measured
  \_\_\_                                                                                                 

  Sync/semi-sync / Available             --- ---           ---          ---               ---            Not measured
  version: \_\_\_                                                                                        

  Sync/semi-sync / Unavailable           --- ---           ---          ---               ---            Not measured
  version: \_\_\_                                                                                        
  -----------------------------------------------------------------------------------------------------------------------

Do not invent results to fill this table. Explain the chosen policy in
terms of accepted RPO, latency impact, availability coupling, failure
assumptions, and the promotion procedure. Verify PostgreSQL
commit/standby settings and exact behavior **\[VERIFY\]**.

## 12. Bounded WAN fault injection and partition experiment

**⚠ LAB SIMULATION ONLY.** Prefer a deterministic simulator if you
cannot prove the network rule is scoped to throwaway lab traffic. `tc`
and Chaos Mesh options are version/environment-specific **\[VERIFY\]**.
Do not alter host-wide networking, production interfaces, or any shared
network path.

### Preflight

-   Confirm both cluster contexts and throwaway resources.
-   Record the current network configuration and how to remove the
    fault.
-   Identify exact interface/namespace/traffic selector.
-   Set a short duration and stop threshold for lag, disk use, error
    rate, and latency.
-   Confirm no public or production traffic can match the rule.

### Exercise

1.  Establish a baseline for writes, lag, and resource usage.
2.  Inject a bounded delay into only the lab replication path.
3.  Observe sync/async behavior and record time series.
4.  If safe and supported, test packet loss or a brief partition with a
    clear timeout.
5.  Watch WAL generation, retained WAL, disk headroom, and replica
    state.
6.  Stop the fault at the first abort threshold.
7.  Remove the exact rule and verify normal connectivity.
8.  Confirm the replica catches up or document why a re-seed is
    required.

**Abort immediately** if target/interface is ambiguous, host
connectivity is affected, disk headroom falls below the predeclared
threshold, primary latency/errors exceed the lab budget, or traffic may
escape the lab. Never improvise a `tc` command from an unverified
example. Store the exact command used only after it has been reviewed
for the actual interface and namespace.

## 13. Stale reads, read-your-writes, and monotonic reads lab

**Objective:** demonstrate the anomaly and a mitigation without claiming
global strong consistency.

1.  Write a record/version to the primary.
2.  Read the record from the replica before the update is visible;
    record both versions.
3.  Implement one mitigation: session pinning to primary, or a
    version/LSN wait whose exact semantics were verified for the
    selected database.
4.  Add a session last-seen-version check for monotonic reads, or
    explicitly route to the authority.
5.  Test a read from the same region and a read from another region.
6.  Test timeout when the replica cannot meet the required version; fail
    closed or route to authority according to policy.
7.  Restore baseline and capture evidence.

**Positive tests:** stale read is detected; the selected mitigation
works for the test path.\
**Negative tests:** a read below the session's version bound is not
reported as fresh; an unavailable authority does not silently invent a
successful strong read.\
**Fidelity:** if a deterministic simulation is used, it proves the state
machine only, not PostgreSQL behavior.

## 14. Failover consistency and acknowledged-write loss

**Safety boundary:** this lab references M13 Unit 6. Do not promote a
real replica unless the approved fencing/safety plan is satisfied. The
safer local option is a deterministic state-machine simulation.

### Procedure

1.  Generate numbered writes with a client journal of acknowledged IDs.
2.  Hold back a subset from the asynchronous replica in the simulation
    or verified lab setup.
3.  Record the replica's last applied ID and primary's last acknowledged
    ID.
4.  Simulate old-primary failure.
5.  Require a synthetic fencing/authority gate before any simulated
    promotion.
6.  Compare acknowledged IDs with the new authority's state.
7.  Count missing acknowledged writes and identify them by ID.
8.  Reconcile from the lab client journal/queue only under a defined
    idempotency policy.
9.  Compare with the synchronous-mode assumptions and results, if
    actually measured.
10. Reset the synthetic state.

**Evidence:** acknowledged ID list, replica-applied list, gate state,
missing-ID report, reconciliation log, timestamps, cleanup status. Do
not claim production data loss or a real promotion result.

------------------------------------------------------------------------

# Object-store replication, model artifacts, schema evolution, and streams

## 15. Object-store replication and delete propagation

Object replication can improve availability of model artifacts and data
files, but a replica is not automatically a backup. Replication may also
propagate deletes, corrupt objects, compromised writes, or malicious
changes. Exact semantics for versioning, delete markers, metadata,
pre-existing objects, encryption, and replication status vary by
implementation **\[VERIFY\]**.

### Architecture

``` text
Model build/publish
       |
       v
East artifact bucket
  - immutable object/version
  - manifest + SHA-256
       |
       | replication rule
       v
West artifact bucket
  - replicated object/version
  - independently verified hash
       |
       v
Alias promotion gate
  - all required targets present?
  - hashes match?
  - metadata/version approved?
       |
       +---- PASS: alias may advance
       +---- FAIL: keep previous alias / block promotion
```

### Verification sequence

1.  Pin MinIO or other object-store version and check current official
    replication/versioning docs **\[VERIFY\]**.
2.  Use synthetic artifacts only.
3.  Upload an immutable artifact and a manifest containing expected
    SHA-256.
4.  Wait for replication status according to the selected product's
    documented semantics.
5.  Compare source/destination inventory and hashes.
6.  Test overwrite/version behavior and deletion propagation in the
    disposable lab.
7.  Demonstrate that deleting the source object can affect the replica
    depending on configured semantics.
8.  Separately test a backup/restore path that is not writable by the
    same replication credentials.
9.  Do not claim successful replication until the observed evidence
    supports it.

### Model alias gate

An alias such as `production` is mutable metadata; the artifact should
be immutable and identified by digest/version. The gate should fail
when: - a required regional artifact is absent; - any target's hash
differs; - artifact metadata/version is not approved; - the replication
state is unknown/stale; - residency policy forbids a target.

A gate passing does not guarantee that a model will load or perform
correctly; it proves only the checks actually implemented.

### Complete model-alias gate script with tests

Save as `model_alias_gate.py`. It operates on declarative sample
metadata only; it does not contact a bucket, registry, or cloud
provider.

``` python
from dataclasses import dataclass
import hashlib
import unittest

@dataclass(frozen=True)
class ArtifactCopy:
    region: str
    present: bool
    sha256: str
    approved: bool = True

def valid_sha256(value: str) -> bool:
    if len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True

def evaluate_alias(required_regions, copies, expected_sha256):
    if not valid_sha256(expected_sha256):
        raise ValueError("expected_sha256 must be 64 hexadecimal characters")
    if not required_regions or len(set(required_regions)) != len(required_regions):
        raise ValueError("required_regions must be non-empty and unique")
    by_region = {c.region: c for c in copies}
    if len(by_region) != len(copies):
        raise ValueError("duplicate region entries")
    failures = []
    for region in required_regions:
        copy = by_region.get(region)
        if copy is None or not copy.present:
            failures.append(f"{region}: missing")
            continue
        if not valid_sha256(copy.sha256):
            failures.append(f"{region}: invalid hash")
        elif copy.sha256.lower() != expected_sha256.lower():
            failures.append(f"{region}: hash mismatch")
        if not copy.approved:
            failures.append(f"{region}: not approved")
    return {"promote": not failures, "failures": failures}

class AliasGateTests(unittest.TestCase):
    def setUp(self):
        self.digest = hashlib.sha256(b"synthetic-model").hexdigest()

    def test_all_regions_present_and_matching(self):
        copies = [ArtifactCopy("east", True, self.digest),
                  ArtifactCopy("west", True, self.digest)]
        self.assertTrue(evaluate_alias(["east", "west"], copies, self.digest)["promote"])

    def test_missing_artifact_blocks(self):
        copies = [ArtifactCopy("east", True, self.digest),
                  ArtifactCopy("west", False, "")]
        self.assertFalse(evaluate_alias(["east", "west"], copies, self.digest)["promote"])

    def test_hash_mismatch_blocks(self):
        copies = [ArtifactCopy("east", True, self.digest),
                  ArtifactCopy("west", True, hashlib.sha256(b"other").hexdigest())]
        self.assertFalse(evaluate_alias(["east", "west"], copies, self.digest)["promote"])

    def test_unapproved_copy_blocks(self):
        copies = [ArtifactCopy("east", True, self.digest),
                  ArtifactCopy("west", True, self.digest, approved=False)]
        self.assertFalse(evaluate_alias(["east", "west"], copies, self.digest)["promote"])

    def test_invalid_digest_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_alias(["east"], [], "not-a-digest")

if __name__ == "__main__":
    unittest.main()
```

**Expected behavior \[EXPECTED --- ILLUSTRATIVE\]:** the five tests are
designed to pass when the script is saved and run. They were not
executed during authoring.

## 16. Schema evolution and logical replication compatibility

A schema change must be compatible with every reader, writer, replica,
consumer, and replay path during rollout---not merely with the current
primary.

### Expand/contract pattern

1.  **Expand:** add a compatible nullable column/table/field or new
    representation without removing the old contract.
2.  Deploy readers that tolerate old and new shapes.
3.  Deploy writers that populate the new representation, with
    compatibility checks.
4.  Backfill in bounded batches and monitor replication lag/WAL.
5.  Verify counts, constraints, and consumer compatibility.
6.  Switch reads only after evidence shows the new representation is
    complete.
7.  **Contract:** remove the old field only after every old
    reader/writer/consumer is gone and rollback requirements are
    satisfied.

Do not assume a DDL statement is replicated by a logical replication
mechanism. PostgreSQL logical replication DDL behavior, sequences,
initial table synchronization, replica identity, and version
compatibility require official-version verification **\[VERIFY\]**.

  -----------------------------------------------------------------------
  Risk                                Control
  ----------------------------------- -----------------------------------
  New writer emits field old reader   Backward-compatible rollout and
  cannot parse                        consumer contract tests

  DDL not propagated to logical       Explicit schema rollout to each
  subscriber                          side; compatibility gate

  Backfill floods WAL and causes lag  Batch/throttle, monitor slot
                                      retention and apply rate

  Rollback removes data written only  Reversible transition plan; retain
  to new schema                       old representation until safe

  Version skew changes behavior       Version compatibility matrix and
                                      staging tests

  Replay processes old events under   Versioned event schema, idempotent
  new schema                          consumers, replay test
  -----------------------------------------------------------------------

## 17. Stream mirroring, CDC, ordering, and idempotency

Stream replication/mirroring may preserve partitions or map them
differently; offsets may not be globally interchangeable. Verify the
selected platform's current documentation **\[VERIFY\]**.

-   **Duplicates:** consumers should be idempotent for effects that can
    be retried.
-   **Ordering:** ordering is usually scoped to a defined partition/key
    or source log, not necessarily global across regions.
-   **Offset translation:** a destination offset may not equal the
    source offset.
-   **Replay:** preserve event IDs, schema version, source position, and
    processing result where needed.
-   **Outbox/CDC:** helps avoid the "database committed but event was
    not published" dual-write gap, but downstream delivery may still be
    at-least-once and require idempotency.
-   **Poison events:** define quarantine/dead-letter and replay
    ownership; do not silently skip integrity-critical events.
-   **Consumer checkpoints:** ensure ownership is explicit during
    failover to avoid duplicate processing or gaps.

**Negative test:** replay the same event twice; assert the business
effect occurs once for the chosen idempotency contract. **Negative
test:** reorder two dependent events; assert the consumer detects or
safely handles the ordering violation.

------------------------------------------------------------------------

# L3 --- Consistency design, integrity, security, and cost

## 18. Dataset consistency requirements matrix

Complete this matrix for the actual system. These are
**\[RECOMMENDATION\] starting points**, not universal requirements.

  -----------------------------------------------------------------------------------------------------------------------
  Dataset class           Candidate topology    Consistency/freshness   Failure behavior          Integrity evidence
                                                requirement                                       
  ----------------------- --------------------- ----------------------- ------------------------- -----------------------
  Account/billing ledger  Single writer or      Strong invariants; no   Block writes if authority Transaction/audit
                          consensus-backed      silent lost updates     unknown                   reconciliation
                          store                                                                   

  Tenant configuration    Single writer with    Read-your-writes for    Route reads to authority  Version and checksum
                          replicas              edits                   while replica stale       

  Inference API           Same immutable        Exact artifact/config   Region not ready on       Image digest/config
  code/config             release per region    parity                  mismatch                  revision

  Model artifact files    Object replication    Hash-identical before   Keep old alias if target  SHA-256 and inventory
                                                alias promotion         incomplete                

  Model registry metadata Controlled writer +   Alias/version           Alias gate blocks         Version, artifact
                          replicated metadata   consistency             incomplete release        digest, approval

  Feature store online    Partitioned or        Per-feature freshness   Mark stale or use         Freshness distribution
  values                  replicated reads      SLA                     approved fallback         

  Feature offline history Append-only/object    Eventual catch-up may   Backfill/replay           Counts, checksums,
                          replication           be acceptable                                     event IDs

  ETL checkpoints         Single owner per      No duplicate/skip       Pause until owner         Checkpoint/offset audit
                          job/partition         outside contract        established               

  Stream events           Log replication or    Ordering per declared   Replay idempotently       Event IDs/offsets
                          per-region consumers  key/partition                                     

  Cache entries           Regional cache,       TTL/consistency defined Rebuild; bound stale      Hit ratio, invalidation
                          rebuildable           per key                 reads                     tests

  Tenant-to-home-region   Replicated versioned  No ambiguous ownership  Unknown/stale map fails   Version and parity
  map                     control data                                  closed                    

  Secrets/key metadata    Approved regional     Rotation and access     Region unready if         Version/presence
                          key/secret            correctness             required key unavailable  metadata; no secret
                          distribution                                                            values

  Audit/security logs     Durable               Retention and           Buffer locally; do not    Sequence gaps,
                          append-oriented       tamper-evidence         silently discard          retention checks
                          replication           requirements                                      

  User                    Session or            Read-your-writes as     Reauthenticate/re-route   Session/version tests
  session/preferences     partition-based       product requires        per contract              
                          design                                                                  

  Analytics aggregates    Async                 Bounded staleness often Mark freshness; replay    Watermarks, row counts
                          pipeline/replicated   acceptable                                        
                          warehouse                                                               

  Object                  Explicit              Defined deletion        Preserve independent      Delete-marker/version
  deletes/tombstones      version/delete policy propagation and         backup                    inventory
                                                recovery                                          

  Residency-restricted    Only permitted        Policy-enforced         Block prohibited          Target policy audit
  records                 targets               location boundary       replication               

  Search index            Rebuildable CDC/index Eventual with lag       Rebuild/replay            Source/index counts and
                          pipeline              objective                                         freshness
  -----------------------------------------------------------------------------------------------------------------------

For every dataset, record: owner, source of truth, writers, consumers,
staleness bound, RPO, residency, retention/delete semantics,
encryption/key policy, replication mechanism, monitoring, failover rule,
and reconciliation procedure.

## 19. Quorum placement and topology choice

Do not choose a quorum layout from region count alone. Document: -
voting members and their failure domains; - what counts as a successful
commit; - whether a majority can survive the intended failure; -
behavior during asymmetric partition; - reconfiguration and rejoin
rules; - how stale nodes are prevented from writing; - witness location,
trust, availability, and protocol-specific semantics; - evidence from
controlled failure tests.

A two-region system with one voter per region may lose quorum when
either region is lost. A third vote in a third independent failure
domain can permit a majority to survive one voter loss, but only if the
selected protocol actually uses that arrangement and the remaining
members can communicate. A witness does not magically make all data
durable or all writes available. Mark product-specific claims
`[VERIFY]`.

## 20. Divergence detection and repair

Lag means replicas may be behind; divergence means they disagree beyond
the expected lag/consistency contract. These are different conditions.

### Detection methods

-   **Row counts:** useful for broad inventory, but equal counts do not
    prove equal contents.
-   **Checksums/hashes:** compare stable canonical representations; be
    careful with ordering, nulls, encoding, and volatile fields.
-   **Canary rows/sequence IDs:** detect missing or stale expected
    records.
-   **Business invariants:** balances, unique ownership,
    foreign-key-like relationships, monotonic version constraints.
-   **Object inventory/hash:** compare key/version/size/hash where
    supported and semantically meaningful.
-   **Stream event IDs/offsets:** identify gaps and duplicates.
-   **Reconciliation backlog:** track conflicts awaiting repair.

False positives occur if the comparison runs while a replica is normally
behind. Compare against a defined watermark/lag tolerance, or compare
only a consistent snapshot. A mismatch should be classified as expected
lag, missing data, duplicate, content mismatch, delete mismatch, or
unknown---not merely "replication broken."

### Data-integrity response table

  -------------------------------------------------------------------------------
  Signal            First question         Safe response        Evidence
  ----------------- ---------------------- -------------------- -----------------
  Row-count         Is replica behind the  Wait within bound or Counts,
  mismatch          agreed watermark?      investigate after    watermark, lag
                                           bound expires        

  Hash mismatch     Is comparison          Preserve sample and  Canonical input,
                    deterministic and      isolate scope; do    hashes, versions
                    snapshot-consistent?   not overwrite        
                                           blindly              

  Missing           Is there a source      Pause dependent      IDs, source
  sequence/event    log/client journal to  processing if        positions, replay
                    reconcile?             integrity is at risk status

  Duplicate effects Is consumer            Contain repeated     Event IDs,
                    idempotency effective? processing and       idempotency
                                           reconcile state      records

  Delete mismatch   Are tombstone/version  Apply approved       Object versions,
                    semantics understood?  deletion/retention   delete markers
                                           policy; preserve     
                                           backup evidence      

  Divergent         Which business         Stop unsafe writes   Conflict
  multi-writer      invariant is violated? if necessary;        versions,
  record                                   preserve both        timestamps, audit
                                           versions             trail

  Unknown integrity Can the candidate      Do not claim         Positions, lag,
  state during      authority be proven    RPO/integrity;       incident timeline
  failover          safe?                  escalate and follow  
                                           M13                  
  -------------------------------------------------------------------------------

### Divergence detector script with tests

This is a toy inventory comparison over declarative records; it does not
connect to PostgreSQL or object storage.

``` python
import hashlib
import json
import unittest

def canonical_hash(record):
    payload = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def compare_inventories(primary, replica, watermark_ok=True):
    if not isinstance(primary, dict) or not isinstance(replica, dict):
        raise ValueError("inventories must be dictionaries keyed by stable IDs")
    if not watermark_ok:
        return {"status": "INCONCLUSIVE_LAG", "missing": [], "extra": [], "mismatch": []}
    missing = sorted(set(primary) - set(replica))
    extra = sorted(set(replica) - set(primary))
    mismatch = sorted(k for k in set(primary) & set(replica)
                      if canonical_hash(primary[k]) != canonical_hash(replica[k]))
    status = "MATCH" if not (missing or extra or mismatch) else "DIVERGED"
    return {"status": status, "missing": missing, "extra": extra, "mismatch": mismatch}

class InventoryTests(unittest.TestCase):
    def test_matching_inventories(self):
        a = {"1": {"v": 1}, "2": {"v": 2}}
        self.assertEqual(compare_inventories(a, dict(a))["status"], "MATCH")

    def test_missing_row_detected(self):
        r = compare_inventories({"1": {"v": 1}, "2": {"v": 2}}, {"1": {"v": 1}})
        self.assertEqual(r["missing"], ["2"])
        self.assertEqual(r["status"], "DIVERGED")

    def test_corrupt_record_detected(self):
        r = compare_inventories({"1": {"v": 1}}, {"1": {"v": 9}})
        self.assertEqual(r["mismatch"], ["1"])

    def test_lag_is_inconclusive_not_divergence(self):
        r = compare_inventories({"1": {"v": 1}}, {}, watermark_ok=False)
        self.assertEqual(r["status"], "INCONCLUSIVE_LAG")

    def test_invalid_input_rejected(self):
        with self.assertRaises(ValueError):
            compare_inventories([], {})

if __name__ == "__main__":
    unittest.main()
```

**\[EXPECTED --- ILLUSTRATIVE\]:** tests are intended to pass if saved
and executed. They were not executed during authoring. Production
comparison needs a stable snapshot/watermark and domain-specific
canonicalization.

## 21. Distributed transactions, idempotency, replay, time, and ordering

### 21.1 Avoid casual cross-region transactions

A transaction that synchronously coordinates multiple regions pays WAN
latency and is exposed to partitions. Use cross-region atomic
transactions only when the chosen system explicitly supports the
required semantics and the business invariant justifies the cost
**\[VERIFY\]**.

Alternatives include: - **Single-writer ownership:** one authority owns
the invariant. - **Partitioned ownership:** each tenant/key range has a
home writer. - **Transactional outbox:** atomically persist the business
change and an event record locally, then deliver asynchronously. -
**Saga/workflow:** sequence local transactions with explicit
compensating actions; compensation is not the same as rollback of a
globally atomic transaction. - **Append-only events:** preserve the
event history and build projections with idempotent consumers. -
**Reconciliation:** detect and repair known divergence with ownership
and audit controls.

### 21.2 Idempotency and unknown outcomes

A timeout does not prove a write failed. The server may have committed
and the response may have been lost. Retrying with a new identity can
duplicate an operation. A robust idempotency contract specifies key
scope, retention period, result replay, transaction boundaries, and
behavior if the same key is reused with different input.

### 21.3 Time and ordering

Wall clocks can skew; timestamps are not a universal ordering oracle.
Use database log positions, sequence/version tokens, or protocol-defined
logical clocks where appropriate. A logical clock provides ordering
information according to its rules, not necessarily physical time.
Last-write-wins based on timestamps can discard valid writes if clock
assumptions are wrong.

### 21.4 Toy LWW lost-update example

**\[SYNTHETIC\]** Two sites read `counter=10`.

``` text
East reads 10; applies +3 -> writes 13 with logical timestamp 120
West reads 10; applies +5 -> writes 15 with logical timestamp 125
LWW keeps 15 and discards East's update.
Correct combined counter, if both increments should count, is 18.
```

The problem is not merely clock skew: whole-value LWW does not preserve
concurrent increments. A suitable counter CRDT or append-only increment
events may fit a counter; a financial ledger or arbitrary multi-field
transaction needs different semantics.

### 21.5 Toy LWW simulator and redesign tests

``` python
import unittest

def lww_merge(a, b):
    # Records: {"value": int, "ts": int, "writer": str}
    # Timestamp order is intentionally simplistic for teaching.
    return max([a, b], key=lambda x: (x["ts"], x["writer"]))

def increment_events(events):
    # Event IDs must be unique; duplicate delivery is ignored.
    seen = set()
    total = 0
    for event in events:
        if event["id"] in seen:
            continue
        seen.add(event["id"])
        total += event["delta"]
    return total

class ConflictTests(unittest.TestCase):
    def test_lww_can_lose_concurrent_increment(self):
        east = {"value": 13, "ts": 120, "writer": "east"}
        west = {"value": 15, "ts": 125, "writer": "west"}
        self.assertEqual(lww_merge(east, west)["value"], 15)
        self.assertNotEqual(lww_merge(east, west)["value"], 18)

    def test_event_model_preserves_both_unique_increments(self):
        events = [{"id": "e1", "delta": 3}, {"id": "w1", "delta": 5}]
        self.assertEqual(increment_events(events), 8)

    def test_duplicate_delivery_is_idempotent(self):
        events = [{"id": "e1", "delta": 3}, {"id": "e1", "delta": 3}]
        self.assertEqual(increment_events(events), 3)

if __name__ == "__main__":
    unittest.main()
```

The event model is illustrative. Production needs durable event IDs,
atomic deduplication with the effect, retention/replay policy, and
domain invariants. A CRDT is appropriate only for operations whose merge
semantics preserve the required invariants.

## 22. Security, residency, deletion, and cost

### 22.1 Security controls

-   Encrypt in transit and at rest using the selected system's supported
    mechanisms.
-   Replicate only to approved identities and destinations; least
    privilege should scope both source-read and destination-write
    permissions.
-   Keep secrets and private keys out of Git, logs, terminal output,
    screenshots, and evidence bundles.
-   Verify key availability and rotation in each permitted region
    without printing secret values.
-   Alert on changes to replication targets/rules, access policies, and
    destination identities.
-   Separate replication credentials from backup/deletion administration
    where feasible.
-   Keep an independent backup path with distinct access controls and
    retention.
-   Treat replication-rule changes as security-sensitive changes with
    review, audit, and rollback.

### 22.2 Data residency and replication targets

``` text
Dataset with residency policy
        |
        v
Policy check: allowed regions + data class + purpose
        |
        +---- target allowed ----> replication may proceed
        |
        +---- target prohibited -> BLOCK + alert + audit evidence
```

Residency includes primary copies, replicas, snapshots, backups, logs,
traces, feature stores, model artifacts, derived datasets, and access by
support personnel. The precise legal requirement must come from the
policy owner; engineers should not invent legal interpretations.

### 22.3 Residency policy checker with tests

Save as `residency_policy.py`. It validates sample declarative data only
and does not connect to cloud services.

``` python
import unittest

def check_targets(dataset, allowed_regions, targets):
    if not isinstance(dataset, str) or not dataset.strip():
        raise ValueError("dataset must be a non-empty string")
    if not allowed_regions or any(not isinstance(x, str) or not x for x in allowed_regions):
        raise ValueError("allowed_regions must contain non-empty region names")
    if any(not isinstance(x, str) or not x for x in targets):
        raise ValueError("targets must contain non-empty region names")
    violations = sorted(set(targets) - set(allowed_regions))
    return {"dataset": dataset, "allowed": sorted(set(allowed_regions)),
            "targets": sorted(set(targets)), "violations": violations,
            "allowed_to_replicate": not violations}

class ResidencyTests(unittest.TestCase):
    def test_allowed_targets_pass(self):
        r = check_targets("model-a", ["east", "west"], ["east", "west"])
        self.assertTrue(r["allowed_to_replicate"])

    def test_prohibited_target_blocks(self):
        r = check_targets("restricted", ["east"], ["east", "west"])
        self.assertFalse(r["allowed_to_replicate"])
        self.assertEqual(r["violations"], ["west"])

    def test_empty_dataset_rejected(self):
        with self.assertRaises(ValueError):
            check_targets("", ["east"], ["east"])

    def test_empty_target_name_rejected(self):
        with self.assertRaises(ValueError):
            check_targets("x", ["east"], [""])

if __name__ == "__main__":
    unittest.main()
```

**\[EXPECTED --- ILLUSTRATIVE\]:** the tests are intended to pass if
saved and executed; they were not run during authoring. A production
policy engine needs authenticated inventory, policy versioning,
approval, audit, and enforcement at the actual replication control
plane.

### 22.4 Replication is not backup

Replication typically keeps a secondary copy current according to its
mechanism. If a user or compromised identity deletes or corrupts source
data, the change may propagate. Backups should have independent
retention/recovery properties, and ideally separate permissions and
deletion paths. See M13 Unit 2.

### 22.5 Cost model without invented prices

Measure rather than invent: - bytes replicated/day and peak bandwidth; -
initial seeding bytes/time; - storage footprint by version/retention; -
egress and inter-region transfer; - duplicate compute for
replication/CDC/validation; - backup copies and restore tests; -
engineering/on-call burden; - impact of synchronous remote commit on
latency; - extra capacity required during seeding and failover.

Use M15 for cost/FinOps. Do not state cloud prices or savings without
current, region-specific evidence.

## 23. Global database/tooling decision framework

Global database products and distributed SQL systems have different
consistency, latency, partition, replication, conflict, and residency
semantics. Product names are awareness examples only, not endorsements.
Verify current guarantees, supported topology, failure modes, version,
pricing, and operational controls **\[VERIFY\]**.

Ask: 1. What invariant must survive concurrent updates? 2. Which
operations require linearizable behavior? 3. What staleness is
acceptable for each read class? 4. Is local write availability during a
partition mandatory? 5. Can writes be partitioned by tenant or key? 6.
What is the actual quorum/voter placement? 7. How does the product
behave when a region is isolated? 8. How are conflicts, deletes, schema
changes, and replays handled? 9. What data residency, encryption, and
key-access controls apply? 10. What evidence from failure tests
demonstrates the claimed behavior? 11. What are the full costs and
operational skills required? 12. Would a single writer with replicas
satisfy the business objectives more simply?

**Recommendation:** default to the simplest topology that meets the
written requirements. Multi-writer is not a badge of maturity; it is a
commitment to conflict semantics and operational complexity.

------------------------------------------------------------------------

# L4 --- Production operations and expert judgment

## 24. Replication SLIs/SLOs and RPO governance

One lag threshold is not appropriate for every dataset. A feature cache,
audit log, account ledger, and model artifact have different freshness
and integrity requirements.

### Suggested indicators

-   lag p50/p95/p99/p99.9 and maximum over a declared window, per
    dataset;
-   replica receive/apply rate, write rate, replication errors;
-   WAL/slot retained bytes and primary disk headroom;
-   heartbeat freshness and sequence gaps;
-   time outside the dataset's declared freshness/RPO objective;
-   divergence/checksum mismatch and reconciliation backlog;
-   object replication completeness and delete-propagation lag;
-   artifact hash mismatch and alias blocked/promoted state;
-   bytes replicated/day and seeding duration;
-   unauthorized replication-target/rule changes;
-   residency-policy violations;
-   region/cell and primary/replica identity in logs/traces.

Avoid uncontrolled high-cardinality labels such as raw tenant IDs in
metrics. Use bounded labels and access-controlled logs/traces for
targeted investigations.

### SLO governance checklist

1.  Dataset owner defines the business consequence of stale/missing
    data.
2.  Data contract states freshness/consistency expectations and what
    consumers should do when unmet.
3.  SLI query and time window are documented and tested.
4.  Alert includes owner, severity, runbook, and action threshold.
5.  Promotion readiness consumes fresh lag/integrity evidence---not only
    process health.
6.  RPO exception requires explicit business/incident approval and
    records uncertainty.
7.  SLO and threshold changes are reviewed and versioned.
8.  Post-incident actions add a regression test, not only a dashboard.

### RPO governance under pressure

If measured lag is beyond the accepted RPO, do not claim the objective
is met. Preserve evidence, quantify what can be quantified, state
uncertainty, and follow the approved promotion/fencing process. Business
stakeholders may choose to accept a documented data-loss risk, but
traffic pressure must not silently bypass data-safety controls.

## 25. Region bring-up, seeding, and decommission

### 25.1 Bring-up checklist

-   Residency/policy approval for data classes and destination.
-   Target capacity, quotas, networking, security, keys/secrets, and
    identity.
-   Compatible schema/application versions.
-   Baseline snapshot/backup and verified source identity.
-   Initial seed plan with throttling and expected resource impact.
-   Streaming catch-up and lag/freshness objective.
-   Counts/checksums/canary and business-invariant verification.
-   Replication SLOs/alerts and dashboard ownership.
-   Model artifact and registry metadata completeness.
-   Read/write routing gate and write authority.
-   Canary traffic and rollback criteria.
-   Runbook, on-call ownership, evidence retention, and decommission
    path.

### 25.2 Seeding approaches

  ----------------------------------------------------------------------------
  Approach          Benefit           Risks/considerations   Evidence
  ----------------- ----------------- ---------------------- -----------------
  Initial           Bulk transfer can Snapshot consistency,  Bytes, elapsed
  backup/snapshot   be efficient      transfer time, source  time, source
  then stream                         load, catch-up lag     position,
  catch-up                                                   post-seed
                                                             checksums

  Continuous        May avoid a       Topology/version       Supported
  streaming from an separate full     constraints; ongoing   topology, lag,
  existing replica  snapshot in some  load and slot/WAL      retained WAL,
                    topologies        retention              apply rate

  Object            Useful for        Existing-object        Inventory, hash,
  inventory/copy    artifacts/files   backfill and           object version,
  then verification                   delete/version         replication
                                      semantics vary         status
  ----------------------------------------------------------------------------

Measure elapsed time and bytes in the local lab, but do not extrapolate
laptop throughput to a real WAN. Throttle seed/backfill so it does not
starve production replication.

### 25.3 Decommission checklist

1.  Approve the data/region retirement and retention policy.
2.  Redirect traffic and verify no required reads/writes remain.
3.  Confirm ownership, checkpoints, and any tenant migrations.
4.  Preserve required audit evidence and backup retention.
5.  Stop replication only after the owner confirms consequences.
6.  Remove slots/targets only after preflight and recovery implications
    are understood.
7.  Revoke credentials, keys, routes, and policy grants.
8.  Verify no stale routing, DNS, secret references, object replication
    rules, or scheduled jobs remain.
9.  Record final checksums/inventory and deletion evidence where
    required.
10. Review monitoring to remove stale alerts without hiding active
    dependencies.

## 26. Parity and readiness

A region is not ready merely because its pods are healthy. Check: -
application/config revision and immutable image digest; - schema
compatibility and replication state; - lag and freshness within the
dataset-specific bound; - artifact/model files present and
hash-matched; - certificates and trust metadata valid (never log private
keys); - required secret references/versions present (never values); -
identity and authorization path works; - destination capacity, quotas,
and storage headroom; - residency targets permitted; - telemetry and
local evidence available; - routing/authority/fencing gates satisfied; -
runbooks and owners are current.

### Simple parity checker with tests

``` python
import unittest

REQUIRED_FIELDS = {
    "image_digest", "config_revision", "schema_revision",
    "certificate_present", "secret_reference_present",
    "model_artifact_digest", "residency_policy_revision"
}

def compare_parity(expected, actual):
    if not isinstance(expected, dict) or not isinstance(actual, dict):
        raise ValueError("expected and actual must be dictionaries")
    missing_fields = sorted(REQUIRED_FIELDS - set(expected) | (REQUIRED_FIELDS - set(actual)))
    mismatches = sorted(k for k in REQUIRED_FIELDS
                        if k in expected and k in actual and expected[k] != actual[k])
    return {"ready": not missing_fields and not mismatches,
            "missing_fields": missing_fields, "mismatches": mismatches}

class ParityTests(unittest.TestCase):
    def setUp(self):
        self.expected = {
            "image_digest": "sha256:example",
            "config_revision": "rev-17",
            "schema_revision": "v4",
            "certificate_present": True,
            "secret_reference_present": True,
            "model_artifact_digest": "sha256:model",
            "residency_policy_revision": "policy-3"
        }

    def test_matching_metadata_passes(self):
        self.assertTrue(compare_parity(self.expected, dict(self.expected))["ready"])

    def test_mismatch_blocks(self):
        actual = dict(self.expected)
        actual["model_artifact_digest"] = "sha256:wrong"
        self.assertFalse(compare_parity(self.expected, actual)["ready"])

    def test_missing_field_blocks(self):
        actual = dict(self.expected)
        del actual["certificate_present"]
        self.assertFalse(compare_parity(self.expected, actual)["ready"])

    def test_invalid_inputs_rejected(self):
        with self.assertRaises(ValueError):
            compare_parity([], {})

if __name__ == "__main__":
    unittest.main()
```

This is a metadata-only demonstration. It does not inspect real
certificates, secret values, Kubernetes objects, or model storage. In a
real checker, make sure absence is distinguished from "unknown";
critical unknown status should not be treated as ready.

## 27. Incident stories: symptom → evidence → root cause → containment → durable fix → regression test

These nine scenarios are curriculum examples, not claims about named
real-world incidents. Numeric values are scenario facts only.

### 1. Async lag reached 18 minutes during nightly backfill; failover lost data

-   **Symptom:** reports or transactions are missing after promotion.
-   **Evidence:** lag history, write IDs acknowledged by old primary,
    replica's applied position, backfill start time.
-   **Root cause:** replication lag exceeded the assumed recovery point;
    the team treated replica health as proof of freshness.
-   **Containment:** preserve primary/replica logs and journals; follow
    M13 Unit 6 promotion/fencing procedure; quantify loss and
    uncertainty before reconciliation.
-   **Durable fix:** dataset-specific RPO alert, backfill throttling,
    promotion gate based on fresh replication evidence.
-   **Regression test:** inject deterministic lag beyond the threshold
    and assert the gate blocks an unapproved promotion.

### 2. Replication slot retained WAL until primary disk filled

-   **Symptom:** primary disk exhaustion and database outage.
-   **Evidence:** disk free trend, retained WAL, slot/consumer status,
    write rate.
-   **Root cause:** disconnected/slow consumer retained WAL with no
    effective headroom alert or remediation threshold.
-   **Containment:** protect disk and primary availability; identify the
    exact slot and consumer; do not blindly drop the slot.
-   **Durable fix:** retained-WAL/disk alerts, slot ownership, bounded
    retention policy verified for version, reseed plan.
-   **Regression test:** simulated consumer outage triggers alert before
    the declared disk threshold.

### 3. Two-site automatic failover without witness split-brained during link flap

-   **Symptom:** both sites accept writes and data diverges.
-   **Evidence:** primary identities, lease/authority history, network
    flap timeline, concurrent versions.
-   **Root cause:** both sites inferred authority without a valid
    quorum/fencing protocol.
-   **Containment:** follow the approved fencing and authority recovery
    plan; preserve both histories.
-   **Durable fix:** explicit quorum/witness semantics, fencing, write
    gate, asymmetric-partition drill.
-   **Regression test:** neither side accepts unsafe writes when
    authority cannot be established.

### 4. Multi-leader LWW dropped customer updates due to clock skew

-   **Symptom:** a valid update disappears after convergence.
-   **Evidence:** both versions, timestamps, clock telemetry, merge
    rule.
-   **Root cause:** timestamp-based whole-record LWW did not preserve
    business intent.
-   **Containment:** preserve audit history and stop unsafe conflicting
    writes if integrity is at risk.
-   **Durable fix:** single-writer/partitioned ownership or
    domain-specific merge/CRDT semantics.
-   **Regression test:** concurrent updates with skewed logical clocks
    preserve the intended invariant.

### 5. Model alias advanced before artifact reached West

-   **Symptom:** West returns 404 or cannot load the newly selected
    model.
-   **Evidence:** alias revision, replication status, target inventory,
    hash mismatch/missing object.
-   **Root cause:** alias promotion was not gated on complete
    replication.
-   **Containment:** return to the previous known-good alias through
    approved controls.
-   **Durable fix:** per-region artifact presence/hash gate and
    immutable artifact identity.
-   **Regression test:** missing or mismatched target artifact blocks
    alias promotion.

### 6. Object deletion propagated to standby; replica was mistaken for backup

-   **Symptom:** deleted object is absent in both locations.
-   **Evidence:** object versions/delete markers, replication rule,
    identity/audit log.
-   **Root cause:** replication semantics propagated deletion; no
    independent recovery copy.
-   **Containment:** use the approved backup/version recovery path;
    preserve audit data.
-   **Durable fix:** separate backup/retention boundary and tested
    restore.
-   **Regression test:** deletion propagation is demonstrated in a
    disposable lab while independent backup recovery remains possible.

### 7. DDL broke logical replication and standby stopped applying changes

-   **Symptom:** replica appears connected but data freshness diverges.
-   **Evidence:** schema versions, apply errors, replication status,
    migration timeline.
-   **Root cause:** team assumed DDL was automatically
    replicated/compatible.
-   **Containment:** halt risky schema/data changes; follow
    version-specific repair plan.
-   **Durable fix:** expand/contract migration and per-side schema
    compatibility gates.
-   **Regression test:** compatibility matrix catches the unsupported
    schema transition.

### 8. Stale reads after failover went unnoticed; reports wrong for a day

-   **Symptom:** reports disagree with recent user actions.
-   **Evidence:** replica freshness, read routing, session/version
    traces, report watermark.
-   **Root cause:** process health was used as a proxy for data
    freshness.
-   **Containment:** label stale reports, pause downstream actions if
    needed, quantify affected interval.
-   **Durable fix:** freshness SLO, watermark/sequence checks,
    read-your-writes and monotonic-read policy.
-   **Regression test:** stale replica causes an explicit
    stale/unavailable response rather than silently passing as fresh.

### 9. Seeding a 2 TB replica saturated shared link and harmed production

-   **Symptom:** production latency and replication lag increase during
    region onboarding.
-   **Evidence:** transfer bytes/rate, shared-link saturation,
    workload/lag timeline.
-   **Root cause:** initial seeding was not throttled or capacity
    planned.
-   **Containment:** pause/throttle seed under approved controls and
    protect production traffic.
-   **Durable fix:** seed bandwidth budget, staged schedule,
    resource/lag gates, target capacity plan.
-   **Regression test:** a seed-rate cap and lag guard halt or slow the
    exercise when thresholds are crossed.

------------------------------------------------------------------------

# Mandatory labs (11 packages)

## 28. Safety contract for every lab

**⚠ LAB SIMULATION ONLY.** Every lab must begin with inventory and end
with cleanup verification. Use synthetic data only. Do not use
production kubeconfigs, cloud credentials, customer data, or private
keys.

Before any mutation: 1. Verify cluster names and contexts; use explicit
`--context` on all Kubernetes commands. 2. Record versions and baseline
state. 3. Confirm target namespaces, database endpoints, and network
selectors. 4. Define abort thresholds for lag, disk usage, latency,
errors, and host resource use. 5. Save the rollback procedure and the
exact fault-removal step. 6. Do not promote a replica or route writes
until old-primary fencing and new authority are verified. 7. Never
change the host clock; prefer logical-clock simulation. 8. Never remove
a slot, volume, or replication target without disposable-resource
confirmation and a recovery plan. 9. Never print secrets or claim
unexecuted expected output as a real result. 10. Verify cleanup after
each experiment.

### Start/stop list

-   Start only the components needed for the current lab.
-   Capture baseline and versions.
-   Run one fault or topology change at a time.
-   Stop generators and fault injection before moving to the next
    scenario.
-   Verify connectivity/lag/resource state is stable.
-   Stop unnecessary containers/clusters between heavy labs.
-   At the end, inspect namespaces, processes, containers, network
    rules, and volumes; remove only exact lab resources.

## 29. Lab 1 --- PostgreSQL replication setup and lag measurement

**Objective:** establish east primary/west standby and measure lag at
idle and under load.

**Resources:** verified contexts, pinned PostgreSQL version, small
synthetic database, canary heartbeat, bounded workload generator, Python
analysis script.\
**Architecture:** primary → WAL/replication path → standby; canary
writer and measurement reader.

**Steps** 1. Choose verified CloudNativePG replica-cluster support or
plain PostgreSQL physical replication; otherwise use a labelled
deterministic simulation. Record why. 2. Verify official docs for exact
version/settings/topology **\[VERIFY\]** before executing setup. 3.
Create only synthetic records and a heartbeat table with
sequence/version. 4. Capture primary/standby identity and replication
state. 5. Measure idle freshness and sample count. 6. Run a bounded
steady workload and repeat. 7. Run a controlled burst/backfill and
repeat. 8. Calculate p50/p95/p99/p99.9 only when sample count supports
it; otherwise record maximum and sample count. 9. Estimate scenario RPO
from last visible heartbeat and compare it with missing acknowledged IDs
in a controlled failure scenario if applicable. 10. Save raw samples,
script version, timestamps, configuration fingerprint, and cleanup
evidence.

**Positive tests:** heartbeat advances; replica exposes newer sequence
after replication.\
**Negative tests:** stale/missing heartbeat is detected; low sample
count is not presented as a reliable p99.9.\
**Success criteria:** actual observations are labelled
`[LOCAL LAB MEASUREMENT]`; assumptions and measurement method are
documented.\
**Common failures:** clock skew, sampling too slowly, no load diversity,
interpreting byte lag as time lag.\
**Abort:** unexpected endpoint, disk pressure, excessive host load,
ambiguous context.\
**Cleanup:** stop workload; restore baseline; remove only lab resources
after inspection.\
**Evidence:** versions, SQL/scripts, raw samples, percentiles, workload
rate, lag interpretation.\
**Cannot prove:** real-WAN behavior, production RPO, or regional
independence.

## 30. Lab 2 --- Synchronous versus asynchronous replication

**Objective:** compare latency, throughput, lag, and behavior when the
standby is unavailable.

**Steps** 1. Record exact PostgreSQL version and the documented
commit/replication configuration. 2. Use the same bounded workload and
duration in each mode. 3. Capture write p50/p95/p99, throughput,
errors/timeouts, lag, CPU/I/O. 4. With the standby available, collect
baseline. 5. Make only the lab standby unavailable and observe exact
behavior. 6. Restore it, observe catch-up, and verify no fault remains.
7. Repeat if safe and compare results. 8. Write a policy decision
including RPO, latency, availability coupling, and assumptions.

**Positive tests:** configuration is recorded; results are comparable
and not invented.\
**Negative tests:** standby-unavailable behavior is explicitly observed
or marked not tested; no universal claim is inferred from one setup.\
**Abort/cleanup/evidence:** same safety contract; restore connectivity
and save all measurements.\
**Cannot prove:** behavior of a different version/product or production
failure domain.

## 31. Lab 3 --- WAN delay/loss/partition and WAL-retention hazard

**Objective:** observe lag under a bounded fault and demonstrate why
retained WAL can threaten primary disk.

**Steps** 1. Prefer deterministic simulation unless a network rule can
be scoped precisely. 2. Record interface/namespace, baseline
connectivity, disk headroom, lag, and removal procedure. 3. Verify exact
`tc`/Chaos tooling syntax and targeting **\[VERIFY\]**; do not improvise
commands. 4. Inject a brief, bounded delay on lab replication traffic
only. 5. Observe lag and sync/async behavior. 6. If feasible, simulate
consumer/standby disconnection and monitor retained WAL/slot lag and
disk headroom on a disposable volume. 7. Trigger an alert at a
predeclared threshold. 8. Repair/catch up or re-seed under a documented
plan. 9. Remove shaping/rules and verify network baseline.

**Negative tests:** ambiguous interface or target aborts; disk headroom
threshold stops the drill; no blind slot deletion.\
**Abort:** any host-wide or non-lab effect, primary instability, or disk
threshold breach.\
**Evidence:** exact reviewed fault definition, lag/retention series,
alerts, removal confirmation.\
**Cannot prove:** real WAN fault distribution or production storage
behavior.

## 32. Lab 4 --- Stale reads, read-your-writes, monotonic reads

Follow Section 13. Record primary write ID, replica-visible version,
session policy, and mitigation result. Test the same-region and
cross-region path. Negative test: a read older than the session's
last-seen version is rejected/rerouted, or explicitly marked stale
according to policy. Cleanup resets synthetic state. The lab does not
establish global strong consistency.

## 33. Lab 5 --- Failover consistency and acknowledged-write loss

Follow Section 14. Use a deterministic simulation unless the real
database promotion/fencing procedure has been separately approved and
verified. Keep a client journal of acknowledged IDs, compare against the
promoted test authority, count missing IDs, and reconcile only with
idempotent replay. Negative test: unknown authority keeps writes
blocked. Do not perform unplanned real promotion. Evidence includes IDs,
authority gate, loss window, and cleanup.

## 34. Lab 6 --- Multi-writer LWW conflict, clock skew, redesign

**Objective:** demonstrate lost update and compare a suitable redesign.

1.  Run the toy simulator in Section 21.
2.  Create two concurrent updates with deliberately skewed logical
    timestamps.
3.  Show the LWW winner and identify the lost business operation.
4.  Redesign as partitioned ownership or event-based counter with
    deduplication; explain when that model is and is not appropriate.
5.  Test duplicate delivery and reconciliation.
6.  Save inputs, output, invariant assertions, and caveats.

Optional container clock changes are not required and should be avoided
unless explicitly verified safe. Never change the host clock. The toy
test does not prove any database's conflict semantics.

## 35. Lab 7 --- Object replication, delete propagation, model-alias gate

**Objective:** verify artifact completeness and hash parity; demonstrate
that replication is not backup.

1.  Verify MinIO or chosen object-store version and current official
    docs **\[VERIFY\]**.
2.  If resources permit, configure a disposable east-to-west replication
    rule; otherwise use a deterministic simulator.
3.  Upload synthetic artifact and manifest/hash.
4.  Wait for documented replication completion; compare inventory,
    version, and hash.
5.  Test missing artifact and hash mismatch against
    `model_alias_gate.py`.
6.  Test delete/version semantics only in disposable buckets.
7.  Restore the artifact or remove the lab bucket according to reviewed
    cleanup.
8.  Demonstrate a separately controlled backup/recovery copy if
    feasible; otherwise describe the evidence needed without claiming
    execution.

**Negative tests:** alias cannot advance if any required region lacks
the artifact, hash mismatches, or approval is false.\
**Abort:** target/bucket identity ambiguous or credentials might access
real data.\
**Evidence:** rule/version, inventory, hashes, gate results,
delete/version observations.\
**Cannot prove:** managed object-store guarantees or production recovery
without target-specific tests.

## 36. Lab 8 --- Cross-region divergence detector

**Objective:** detect a missing row or corrupted toy record while
distinguishing normal lag from divergence.

1.  Prepare matching synthetic inventories and a stable watermark.
2.  Run the detector in Section 20.
3.  Plant a missing row and rerun.
4.  Plant a corrupted record and rerun.
5.  Set `watermark_ok=False` and verify the result is inconclusive
    rather than falsely reporting divergence.
6.  Define an anti-entropy/repair plan and record who approves repair.
7.  Reset state.

**Success:** tests detect missing/corrupt data and do not misclassify an
explicitly stale watermark.\
**Evidence:** inventories, hashes, watermark, output, repair plan.\
**Cannot prove:** complete integrity without snapshot consistency,
canonicalization, and full production data coverage.

## 37. Lab 9 --- Schema migration and stream compatibility

**Objective:** exercise expand/contract and consumer compatibility.

1.  Write a compatibility matrix for old/new schema and
    readers/writers/replicas/consumers.
2.  Simulate expand: add a field while old readers still work.
3.  Test new reader against old data and old reader against new data.
4.  Simulate DDL not being applied to a logical subscriber; label it as
    a simulation unless tested against a verified PostgreSQL version.
5.  Add event schema version, duplicate delivery, and reordered event
    tests.
6.  Test idempotent consumer behavior.
7.  Document rollback and contract-phase gate.

**Success:** incompatible rollout is blocked before removal of old
schema.\
**Evidence:** matrix, test outputs, version assumptions, rollback path.\
**Cannot prove:** exact PostgreSQL logical replication behavior until
tested on the pinned version.

## 38. Lab 10 --- Consistency matrix and five ADRs

Create an ADR for each: 1. Primary/replica sync/async policy. 2. Quorum
placement/witness decision. 3. Multi-writer versus partitioned
ownership. 4. Object/model artifact replication and alias gate. 5.
Residency, retention, and deletion policy.

Each ADR must include context, invariants, options, decision,
consequences, assumptions, evidence, rejected options,
migration/rollback, owner, and revisit triggers. Complete Section 18's
dataset matrix for at least 12 dataset classes. If evidence is absent,
state "unknown / needs test," not a guessed fact.

## 39. Lab 11 --- Readiness, parity, seeding, evacuation, residency, tabletop

### Part A: readiness/parity

1.  Build a metadata inventory of image/config/schema revisions,
    certificate/secret-reference presence, artifact digests, policy
    revision, capacity, and lag.
2.  Run parity checker in Section 26.
3.  Plant a mismatch and verify readiness fails.
4.  Never include secret values.

### Part B: routine evacuation and RTA evidence

1.  Follow M13 Unit 7 evidence conventions.
2.  Record **RTA (recovery time actual)** as the measured elapsed time
    in the specific exercise; do not confuse it with **RTO**, the
    target.
3.  Record service interruption, lag, missing IDs, integrity results,
    and routing changes.
4.  Use only a safe simulated authority/fencing gate unless the actual
    promotion process has separate approval.

### Part C: region seeding

1.  Compare snapshot-based seed and streaming catch-up conceptually or
    in a local test.
2.  Measure actual bytes and elapsed time if executed; label local
    measurements.
3.  Throttle and monitor lag; do not extrapolate to WAN throughput.

### Part D: residency policy

Run Section 22's script with allowed and prohibited targets. Negative
test must block prohibited target.

### Part E: tabletop scenario

**Scenario:** replication lag is beyond the declared RPO when a region
fails; business requests immediate traffic shift.

Roles: incident commander (M10), database/data owner, platform/SRE lead,
security/residency owner, product/business decision-maker,
communications lead.

Decision sequence: 1. Establish what failed and whether signals are
fresh. 2. Preserve lag/position/acknowledged-write evidence. 3. Verify
candidate region, authority, and fencing state. 4. State known data-loss
window and uncertainty; do not claim RPO compliance. 5. Identify safe
choices: wait/repair, promote with an explicitly approved risk
acceptance, or keep writes blocked while serving only safe reads if the
contract permits. 6. Record who has authority to accept business
data-loss risk. 7. Communicate user impact and status without inventing
certainty. 8. Follow approved M13 recovery steps; validate invariants
after recovery. 9. Add regression actions and owners.

**Tabletop scoring (10 points):** source evidence (2);
write-authority/fencing gate (2); explicit RPO uncertainty (2); customer
communication and roles (1); safe option/trade-off explanation (2);
evidence and follow-up actions (1). 8--10: ready for a facilitated
drill; 5--7: remediate; below 5: repeat. This score is not proof of
production readiness.

### Cleanup

Stop load generators, remove only verified lab faults, restore synthetic
state, verify contexts/resources, and save `cleanup-verification.txt`.
If any fault cannot be confirmed removed, stop further labs and resolve
it.

------------------------------------------------------------------------

## 40. Runbooks

These are educational templates, not production-authorized procedures.

### Runbook A --- Replication lag exceeds dataset SLO

1.  Identify dataset, primary, replica, owner, and declared
    freshness/RPO objective.
2.  Confirm the lag signal is fresh and identify whether it measures
    time, bytes, log position, or end-to-end heartbeat.
3.  Capture write rate, apply rate, retained WAL, disk headroom, replica
    health, and recent changes.
4.  Check for backfill, long-running query, network degradation, slot
    retention, or resource saturation.
5.  Protect primary health; throttle/stop source workload if approved
    and necessary.
6.  Do not promote or route strict-freshness reads to a stale replica
    without an explicit policy.
7.  Escalate before the RPO boundary is breached; record business impact
    and uncertainty.
8.  Recover/catch up or re-seed through the approved procedure.
9.  Verify lag recovery, integrity, and downstream consumers.
10. Create regression test, alert/runbook action, and post-incident
    review.

**Abort:** unknown target, disk pressure beyond threshold, unsafe
slot/volume action, or ambiguous write authority.

### Runbook B --- Suspected divergence or missing acknowledged writes

1.  Preserve source/replica positions, acknowledged-write journal, event
    IDs, versions, and timestamps.
2.  Determine whether the difference is expected lag or actual
    divergence using a stable watermark.
3.  Freeze unsafe reconciliation or writes if invariants are at risk.
4.  Identify affected records and the source of truth for each.
5.  Do not blindly overwrite one side with the other.
6.  Agree on repair/replay using idempotency and domain rules.
7.  Validate counts, hashes, and business invariants after repair.
8.  Communicate scope and uncertainty; retain audit evidence.
9.  Add regression tests for the exact anomaly.

### Runbook C --- Model alias/artifact replication failure

1.  Keep the current known-good alias active.
2.  Check target artifact presence, immutable digest, approval metadata,
    and replication state.
3.  Compare source/target hashes without exposing credentials.
4.  Check residency policy and target authorization.
5.  Repair replication or re-upload through the approved pipeline; do
    not bypass the gate.
6.  Re-run parity/hash verification and serving smoke tests.
7.  Advance alias only when all required regions pass.
8.  Preserve the manifest, digests, gate result, and rollback reference.

### Runbook D --- Suspected residency-policy violation

1.  Identify dataset, replication rule, target, policy revision, and
    time window.
2.  Block new prohibited replication through approved controls without
    deleting evidence.
3.  Preserve audit logs and object/database inventory.
4.  Notify policy/security/data owners and follow the organization's
    incident process.
5.  Determine whether prohibited copies, backups, logs, or artifacts
    already exist.
6.  Execute approved remediation/retention actions with legal/policy
    owner input.
7.  Validate all targets and remove stale rules/credentials.
8.  Add a policy regression test and alert.

## 41. Evidence templates and deterministic bundle

For each lab, retain: - UTC timestamp and clock source; - tool/database
versions and context mapping; - configuration fingerprint/revision; -
exact command or script version run; - scenario, sample count, workload
rate, network condition; - raw observations and calculated values; -
expected versus observed result; - failures, abort decisions, cleanup
status; - reviewer/owner and follow-up.

Never store passwords, tokens, private keys, or secret values. A
reproducible evidence bundle can contain a sorted manifest of relative
paths, file sizes, and SHA-256 hashes; compute hashes only when actually
running the bundle script. A hash proves integrity of the captured file
set relative to the manifest, not truth or completeness of the
observations.

### Evidence directory template

``` text
evidence/
  inventory.txt
  versions.txt
  context-map.txt
  topology.md
  dataset-matrix.md
  lab-01/
    raw-lag-samples.csv
    workload-settings.md
    interpretation.md
  lab-02/
    sync-async-results.csv
    config-fingerprint.txt
  lab-03/
    fault-definition.md
    lag-wal-disk-series.csv
    cleanup.txt
  lab-04/
    read-version-timeline.csv
    mitigation-tests.txt
  lab-05/
    acknowledged-write-ids.txt
    replica-applied-ids.txt
    loss-reconciliation.md
  lab-06/
    conflict-input.json
    test-results.txt
  lab-07/
    object-inventory.csv
    artifact-hashes.txt
    alias-gate-results.txt
  lab-08/
    inventory-comparison.txt
  lab-09/
    schema-compatibility-matrix.md
    stream-tests.txt
  lab-10/
    adr-sync-async.md
    adr-quorum.md
    adr-writer-ownership.md
    adr-artifacts.md
    adr-residency-deletion.md
  lab-11/
    readiness-parity.txt
    seeding-measurements.csv
    residency-policy-results.txt
    tabletop-score.md
  cleanup-verification.txt
  manifest.sha256
```

The filenames are a suggested structure, not evidence that any such
files currently exist.

## 42. ADR template and worked example

### ADR template

``` markdown
# ADR-NNN: <decision title>

- Status: Proposed / Accepted / Superseded
- Owner:
- Date:
- Review/revisit trigger:

## Context
Business objective, data classes, SLO/RTO/RPO references, residency, constraints.

## Invariants and guarantees
Required consistency/freshness, write authority, deletion/retention, security.

## Options considered
For each: benefits, failure behavior, cost/operational burden, evidence.

## Decision
Chosen topology and scope (per dataset/component).

## Consequences
Latency, availability, data-loss/conflict risk, cost, operational work.

## Assumptions and unknowns
Clearly labelled; include `[VERIFY]` items.

## Evidence
Lab/production tests, versions, sample counts, limitations.

## Migration and rollback
Steps, gates, owners, abort criteria, data safety.

## Revisit triggers
SLO miss, load growth, residency change, lag trend, team capability change.
```

### Worked example --- primary/replica for a transactional dataset

**\[ASSUMPTION\] Context:** a transactional dataset has invariants that
make concurrent writes unsafe. Business permits writes to be temporarily
unavailable if authority is uncertain; stale reads are not acceptable
for a subset of user actions.

-   **Options:** asynchronous single writer; synchronous single writer;
    multi-writer; partitioned ownership.
-   **Decision \[RECOMMENDATION\]:** begin with single-writer primary
    and asynchronous replica if measured lag/RPO and business
    requirements allow it. Use primary/authority reads for strict
    freshness. If the required RPO cannot be met, evaluate a documented
    synchronous/quorum mode with measured latency and
    standby-unavailable behavior.
-   **Consequences:** simpler conflict model; remote writes and failover
    still need controlled authority/fencing; async mode can lose
    acknowledged writes under some failures.
-   **Evidence required:** lag distribution under backfill,
    acknowledged-write-loss test, standby-unavailable behavior,
    promotion gate, integrity verification.
-   **Rejected:** multi-writer because no demonstrated conflict
    semantics preserve the invariant.
-   **Rollback/revisit:** revisit if RPO misses, write latency is
    unacceptable, residency changes, or workload can be partitioned by
    tenant.
-   **Unknowns:** actual version-specific PostgreSQL semantics and
    production performance remain `[VERIFY]` until measured/documented.

This is an example decision, not a universal recommendation.

## 43. Readiness review and expert questions

Before calling a design production-ready, answer with evidence:

### Data correctness

-   Which dataset is authoritative and who owns the invariant?
-   What exact guarantee does each read path provide?
-   How is stale data signalled to consumers?
-   Which writes can be lost after each failure scenario?
-   What does the commit acknowledgement actually guarantee?
-   Can both sites accept writes during a partition?
-   How are duplicate, reordered, replayed, and conflicting events
    handled?
-   Can deletion or corruption propagate to all replicas and backups?

### Replication operations

-   Are lag and freshness measured per dataset?
-   Are p99/p99.9 claims supported by sufficient samples?
-   Can a replication slot fill the primary disk?
-   What happens when the replica cannot catch up?
-   Is re-seeding bounded and does it protect production?
-   Are schema and version compatibility tested?
-   Are artifact aliases gated on actual presence and hashes?

### Security/residency

-   Are all targets policy-approved?
-   Are backup, log, telemetry, artifact, and support-access copies
    covered?
-   Are replication credentials least-privileged and audited?
-   Can unauthorized target/rule changes be detected and blocked?
-   Are secret/key rotations tested in every region?

### Failover and governance

-   Is the authority/fencing gate independent from traffic routing?
-   Does the runbook state what to do when lag exceeds RPO?
-   Who may accept a documented data-loss risk?
-   Are global dashboards backed by local evidence if the hub fails?
-   Is the evidence package reproducible and free of secrets?

### Revisit triggers

Revisit the ADR when traffic/data volume changes materially, lag trends
worsen, RPO/SLO changes, a new region or residency boundary is
introduced, data semantics change, incidents expose an assumption, costs
rise, or the team/on-call model changes.

------------------------------------------------------------------------

## 44. What the local labs demonstrate---and cannot demonstrate

  -----------------------------------------------------------------------
  Local lab can demonstrate           It cannot demonstrate
  ----------------------------------- -----------------------------------
  Context discipline and scoped       Geographic independence or physical
  fault-injection workflow            region isolation

  PostgreSQL setup behavior for the   Production RPO or all PostgreSQL
  exact tested version/configuration, failure semantics
  if actually run                     

  Observed lag and write latency in   Real WAN performance or provider
  the local environment               SLA

  A canary detects stale visibility   Complete detection of all data
  in the tested path                  divergence

  A toy LWW example loses a           Behavior of a named multi-writer
  concurrent update                   product

  A metadata gate blocks              Real object-store replication
  missing/mismatched artifact         correctness unless integrated and
  fixtures                            tested

  Residency checker rejects sample    Compliance certification or full
  prohibited targets                  policy enforcement

  Expand/contract compatibility tests Compatibility with every real
  for the tested schemas              consumer/version

  A simulated promotion gate fails    Actual fencing correctness or
  closed                              split-brain prevention

  Seeding bytes/time in a local test  WAN throughput, cloud egress, or
                                      production seed duration

  Runbook/tabletop identifies         Competence under actual incident
  assumptions                         pressure
  -----------------------------------------------------------------------

The absence of an anomaly in a lab is not proof of correctness.
Production readiness needs target-version documentation, realistic
workloads, independent failure domains, security/compliance review, data
integrity checks, and rehearsed operational procedures.

## 45. Knowledge checks and answer key

Score one point per question. For scenario answers, award the point only
if the answer includes the relevant trade-off and evidence.

### Foundations and consistency

**1. Multiple choice:** What does linearizability require?\
A. Replicas eventually converge. B. Operations appear to take effect at
points respecting real-time order. C. All reads are local. D. No
partitions occur.\
**Answer:** B. It is a stronger guarantee than eventual convergence.

**2. Short answer:** How does sequential consistency differ from
linearizability?\
**Answer:** Sequential consistency preserves each process's operation
order in one global order, but that order need not respect real-time
ordering between processes.

**3. Scenario:** A user saves a profile in East and reads an older
version in West. Which guarantee is missing?\
**Answer:** At least read-your-writes for that client/path, or an
equivalent freshness policy. Evidence includes version IDs, routing, and
replica apply state.

**4. Multiple choice:** Eventual consistency guarantees:\
A. A fixed convergence time. B. No conflicting writes. C. Convergence if
updates stop and the model's communication/reconciliation assumptions
hold. D. Linearizable reads.\
**Answer:** C.

**5. Short answer:** Why is a low average lag not enough for an RPO
claim?\
**Answer:** Tail spikes, bursty writes, acknowledged/applied positions,
and failure/promotion semantics matter. Use distributions, maxima, write
IDs, and a defined failure model.

**6. Scenario:** Explain why "we chose two of CAP's three" is
inadequate.\
**Answer:** CAP concerns trade-offs under partition for a specified
consistency/availability model; P is a real failure condition, and
actual behavior depends on operations/system design. State what happens
to affected requests.

**7. Short answer:** Define PACELC.\
**Answer:** If partition occurs, availability versus consistency; else,
latency versus consistency. It is a framing model, not a complete
requirements specification.

**8. Scenario:** Two regions each have one voter. One region is lost.
Can the remaining region automatically form a majority?\
**Answer:** Not in a two-voter majority system. Need exact voter set,
protocol, witness placement, and fencing semantics before asserting
availability.

### Replication and lag

**9. Multiple choice:** What does `W + R > N` guarantee in every
leaderless database?\
A. Linearizability. B. A desired read always sees latest write. C.
Nothing universally; overlap intuition alone is insufficient. D. No
partitions.\
**Answer:** C.

**10. Short answer:** Compare physical/WAL and logical replication.\
**Answer:** Physical replication copies physical database changes/log
state; logical replication streams selected logical changes. Their
supported use cases, compatibility, DDL, and recovery semantics differ
and must be verified for the product/version.

**11. Scenario:** A primary acknowledges IDs 101--110; replica has
applied through 106. What is the potential loss?\
**Answer:** IDs 107--110 may be absent if that replica is promoted,
subject to actual durable positions, commit semantics, failure, and
recovery procedure. Preserve the journal and quantify observed missing
IDs.

**12. Short answer:** Why is heartbeat age not automatically actual
RPO?\
**Answer:** It measures that canary's visibility and may omit bursty
writes, sampling gaps, clock skew, and commit/replication semantics.

**13. Scenario:** A replication slot retains WAL until disk fills. What
safeguards were missing?\
**Answer:** Retained-WAL/disk alerts, slot ownership, consumer-health
monitoring, headroom thresholds, catch-up/reseed plan, and safe
remediation. Do not blindly drop the slot.

**14. Multiple choice:** A synchronous replication configuration always
makes writes available when the standby is down.\
A. True. B. False; behavior depends on exact commit policy and
configuration.\
**Answer:** B. Verify the installed version and exact semantics.

**15. Short answer:** Why are byte lag and time lag different?\
**Answer:** Bytes-to-time depends on write rate and workload; byte lag
can be large during high throughput or represent a different time window
when the system is quiet.

**16. Scenario:** A standby is connected but stale. What should a
strict-freshness read path do?\
**Answer:** Route to the authority, wait for a verified
version/position, or return explicit stale/unavailable status according
to contract---not silently claim fresh data.

### Conflicts, objects, schema, and streams

**17. Scenario:** LWW chooses a whole-record value from West and loses
East's concurrent increment. How can the model be redesigned?\
**Answer:** Single-writer/partitioned ownership, an appropriate counter
CRDT, or append-only increment events with idempotent deduplication.
Choose based on domain invariants.

**18. Short answer:** When is a CRDT appropriate?\
**Answer:** When its supported operations and merge properties preserve
the required semantics; it does not solve arbitrary transactions or
cross-object invariants.

**19. Scenario:** A model alias points to an artifact not yet replicated
in West. What should happen?\
**Answer:** Promotion is blocked until required target presence, hash,
approval, and policy checks pass.

**20. Short answer:** Why is object replication not a backup strategy by
itself?\
**Answer:** Deletes/corruption/compromised writes can propagate.
Independent retention and access controls plus tested restore are
needed.

**21. Scenario:** A residency policy prohibits West, but a replication
rule targets West. What control should act?\
**Answer:** Policy-as-code/enforcement should block the target before
replication, alert, and retain audit evidence. Verify all copies and
derived data under policy.

**22. Short answer:** What is the purpose of expand/contract schema
migration?\
**Answer:** Maintain compatibility while old and new
readers/writers/replicas coexist, then remove old schema only after
verified usage/compatibility gates pass.

**23. Scenario:** A logical replication subscriber stops applying after
DDL. What assumptions may have failed?\
**Answer:** DDL propagation or compatibility was assumed; inspect exact
product/version behavior, schema revision, and apply errors. Add
explicit per-side schema rollout and compatibility tests.

**24. Short answer:** Why does stream mirroring need idempotency and
ordering tests?\
**Answer:** Delivery may duplicate or reorder events and offsets may map
differently; consumer effects must match the event contract.

### Security and operations

**25. Scenario:** Business demands immediate failover while lag exceeds
the declared RPO. What should the incident commander do?\
**Answer:** Verify fresh evidence, preserve positions/journal, check
authority/fencing, quantify loss/uncertainty, present safe choices, and
require the authorized business owner to accept documented risk if
proceeding. Do not silently bypass safety gates.

**26. Short answer:** What should be checked before adding a region?\
**Answer:** Residency, capacity/quota, keys/secrets, network/security,
schema, seed/catch-up, checksums, lag SLO, artifacts, routing/write
gate, rollback, owner, and evidence.

**27. Scenario:** Seeding a 2 TB replica harms production. What controls
help?\
**Answer:** Measure throughput, throttle seed/backfill, protect
production bandwidth, monitor lag and saturation, schedule windows, and
use abort thresholds.

**28. Short answer:** Name four replication SLI categories.\
**Answer:** Lag/freshness, receive/apply rate, retained WAL/disk
headroom, divergence/checksum mismatches, object replication
completeness, artifact hash status, policy violations, or seed
bytes/time.

**29. Scenario:** A checksum mismatch occurs while the replica is known
to be behind. Is this proven divergence?\
**Answer:** Not yet. Compare against a consistent watermark/snapshot;
classify as inconclusive lag until the agreed bound expires or stable
comparison is possible.

**30. Whiteboard ADR:** Compare async primary/replica, synchronous
replication, and multi-writer for a transactional ledger.\
**Answer:** State invariant and business RPO/latency first. Async lowers
latency but risks acknowledged-write loss; synchronous may reduce loss
under stated assumptions but adds latency/availability coupling;
multi-writer requires conflict semantics and is inappropriate unless
invariants are preserved. Include evidence, fencing, and rollback.

**31. Scenario:** A two-site system loses one site but the remaining
node claims it is primary. What evidence is required?\
**Answer:** Protocol membership/quorum, authority/lease state, fencing
of old writer, durable log/replication state, and approved promotion
procedure. A health endpoint is insufficient.

**32. Short answer:** What is the difference between lag and
divergence?\
**Answer:** Lag is being behind the expected state; divergence is
disagreement beyond the consistency contract/watermark. Use a stable
watermark and compare contents/versions.

**33. Scenario:** Secret rotation occurred, but the replica region has
stale key/secret metadata. What is the safe readiness result?\
**Answer:** Not ready for paths requiring the credential. Validate
version/presence without exposing values and rehearse rotation.

**34. Multiple choice:** Which proves production readiness?\
A. All local tests pass. B. No anomaly observed in kind. C.
Target-environment evidence, verified semantics, realistic load,
integrity/security review, and rehearsed operations. D. Dashboard is
green.\
**Answer:** C.

**35. Expert judgment:** When is a single writer plus replicas better
than multi-writer?\
**Answer:** When it satisfies latency, availability, RPO/RTO, and
residency requirements with clearer invariants and lower operational
complexity. Demonstrate with workload and failure evidence.

**Scoring:** **80% or higher:** proceed while retaining open risks;
**60--79%:** remediate weak areas and repeat related labs; **below
60%:** repeat the unit and labs. Quiz performance is not proof of
production competence.

------------------------------------------------------------------------

## 46. Glossary

-   **ADR:** architecture decision record with context, options, choice,
    consequences, evidence, and revisit triggers.
-   **Apply/replay lag:** delay before received changes are
    applied/visible on a replica.
-   **Bounded staleness:** staleness constrained by a specified,
    system-defined bound.
-   **CDC:** change data capture; emitting source changes to downstream
    systems.
-   **Causal consistency:** preserves causal ordering of related
    operations.
-   **CRDT:** conflict-free replicated data type with defined merge
    properties for supported operations.
-   **Fencing:** prevents an old or unauthorized writer from continuing
    to mutate state.
-   **Linearizability:** operations appear to take effect at points
    respecting real-time order.
-   **LWW:** last-writer-wins conflict rule that selects a value
    according to a defined ordering.
-   **RPO:** recovery point objective; acceptable data-loss window.
-   **RTA:** recovery time actual; measured duration in an exercise, as
    distinct from the RTO target.
-   **RTO:** recovery time objective; target time to restore service.
-   **SLO:** service-level objective for a measured reliability
    indicator.
-   **WAL:** write-ahead log, used by PostgreSQL and other systems for
    durability/recovery and replication mechanisms.
-   **WAL retention/replication slot:** mechanism that may retain log
    data for a consumer; unmanaged retention can threaten disk capacity.
-   **Witness:** a protocol-specific participant/tie-breaker; semantics
    and failure-domain value depend on the implementation.
-   **Read-your-writes:** a session/client can observe its own completed
    writes under the stated guarantee.

## 47. Verification notes and sources

**Verification status:** live official documentation was not consulted
during this authoring pass. The following are canonical entry points,
not a claim that the current versions or exact commands were checked on
2026-10-29. Verify the installed version and the exact page/feature
before executing implementation-specific steps.

-   PostgreSQL documentation: https://www.postgresql.org/docs/
-   PostgreSQL warm standby/streaming replication entry point:
    https://www.postgresql.org/docs/current/warm-standby.html
-   PostgreSQL logical replication entry point:
    https://www.postgresql.org/docs/current/logical-replication.html
-   PostgreSQL replication monitoring entry point:
    https://www.postgresql.org/docs/current/monitoring-stats.html
-   CloudNativePG documentation:
    https://cloudnative-pg.io/documentation/
-   MinIO documentation: https://min.io/docs/
-   Kubernetes documentation: https://kubernetes.io/docs/
-   kind documentation: https://kind.sigs.k8s.io/
-   OpenTelemetry documentation: https://opentelemetry.io/docs/
-   Apache Kafka documentation, if a Kafka-compatible stream is
    selected: https://kafka.apache.org/documentation/
-   Jepsen analyses (system-specific evidence, not a universal model
    reference): https://jepsen.io/analyses

Items that must be verified before implementation: 1. Exact PostgreSQL
version, replication topology support, settings, monitoring
columns/functions, commit semantics, replication slot/WAL retention
behavior, and logical replication limitations. 2. CloudNativePG feature
support and topology/version/resource requirements if selected. 3.
MinIO/object-store replication, delete marker/versioning,
existing-object replication, encryption, and policy semantics. 4. Exact
kind cluster names/context mapping and any network configuration. 5.
`tc`/Chaos tooling version and scoped fault syntax. 6. Global
database/streaming/CRDT product guarantees and version compatibility. 7.
Official source title and review date for any claim that is later
converted from `[VERIFY]` to verified fact.

## 48. Roadmap Alignment and Authenticity Audit

This audit is based on the supplied Unit 7 prompt. The requested
`Roadmap_ptree.md` and primary M14 syllabus file were not independently
verified in full in this pass; therefore, path/sibling alignment is
based on the exact names stated in the supplied prompt, not an
independently inspected repository tree.

  ----------------------------------------------------------------------------------------------------------------------------
  Requirement            Status                   Evidence          Notes/follow-up
                         (PASS/PARTIAL/BLOCKED)   section(s)        
  ---------------------- ------------------------ ----------------- ----------------------------------------------------------
  Exact Unit 7           PASS                     Metadata          Artifact is named
  filename/path and only                                            `07-data-replication-and-consistency-across-regions.md`;
  one target artifact                                               no repository file was modified.

  All required           PASS                     Section 4         Definitions and caveats included.
  consistency models                                                

  CAP/PACELC precise     PASS                     Section 5         Avoids simplistic "pick two" explanation.
  interpretation                                                    

  Primary/replica,       PASS                     Section 6         Product-specific behavior remains `[VERIFY]`.
  multi-leader, quorum,                                             
  consensus,                                                        
  sync/async/semi-sync                                              

  Required replication   PASS                     Section 7         Physical/WAL, logical, storage, application/outbox/CDC,
  methods                                                           streams, objects.

  PostgreSQL baseline    PARTIAL                  Sections 8--13;   Workflow and templates authored; no database setup or
  and lag measurement                             Lab 1             measurement executed.

  p50/p95/p99/p99.9 and  PASS                     Section 9         Sample-size and interpretation caveats included; no
  RPO reasoning                                                     fabricated measurements.

  Sync/async experiment  PARTIAL                  Section 11; Lab 2 Protocol authored; not run; exact settings require
  and                                                               verification.
  standby-unavailable                                               
  case                                                              

  WAN                    PARTIAL                  Section 12; Lab 3 Safety/process authored; fault injection and WAL hazard
  delay/loss/partition                                              not executed.
  and WAL retention                                                 

  Stale reads,           PASS                     Sections 4, 13;   Real database behavior remains unmeasured.
  read-your-writes,                               Lab 4             
  monotonic reads                                                   

  Failover               PARTIAL                  Section 14; Lab 5 Simulation workflow specified; no promotion or loss
  acknowledged-write                                                experiment run.
  loss and                                                          
  reconciliation                                                    

  LWW conflict and       PASS                     Section 21; Lab 6 Toy code included; tests were not executed.
  redesign                                                          

  Object replication,    PARTIAL                  Section 15; Lab 7 Gate code included; no object store configured.
  deletes, versioning,                                              
  alias gate                                                        

  Schema evolution and   PASS                     Sections 16--17;  Version-specific logical DDL behavior requires
  streams                                         Lab 9             verification.

  Dataset matrix with at PASS                     Section 18        17 dataset classes included.
  least 12 classes                                                  

  Quorum/witness and     PASS                     Sections 6, 19    Exact product semantics require verification.
  two/three failure                                                 
  domains                                                           

  Lag sources, WAL       PASS                     Sections 10, 20   No real lag/retention observations claimed.
  retention, divergence                                             

  Distributed            PASS                     Section 21        Educational examples, not production validation.
  transactions,                                                     
  idempotency, replay,                                              
  time/order                                                        

  Security, residency,   PASS                     Section 22        Policy and pricing details are not claimed verified.
  deletion, cost                                                    

  Residency checker with PASS                     Section 22        Sample-data script included; tests not executed.
  tests                                                             

  Model alias gate with  PASS                     Section 15        Sample-data script included; tests not executed.
  tests                                                             

  Divergence/inventory   PASS                     Section 20        Sample-data script included; tests not executed.
  detector with tests                                               

  Parity checker with    PASS                     Section 26        Sample-data script included; tests not executed.
  tests                                                             

  All 11 lab packages    PASS                     Sections 29--39   Steps, tests, evidence, abort/cleanup, and fidelity limits
                                                                    included; labs not executed.

  Nine incident stories  PASS                     Section 27        Scenarios are explicitly fictional.

  Replication SLOs,      PASS                     Sections 24--27,  No real operational measurements claimed.
  readiness, runbooks,                            39--41            
  tabletop                                                          

  Region                 PASS                     Sections 25, 39   Local measurement remains unperformed.
  seeding/decommission                                              

  At least 30 knowledge  PASS                     Section 45        35 questions and answer key included.
  checks and scoring                                                

  Source                 BLOCKED                  Section 47        Live browsing was not performed; URLs are entry points
  titles/URLs/review                                                only.
  dates verified live                                               

  Actual repository tree PARTIAL                  Section 48        Exact named tree/syllabus not independently inspected in
  and sibling content                                               full.
  verified                                                          

  Scripts and automated  BLOCKED                  Sections 15, 20,  Code authored; no execution results claimed.
  tests executed                                  22, 26            

  Database/object        BLOCKED                  Labs 1--11        No cluster/database/object-store tests were run.
  replication or fault                                              
  injection executed                                                

  No other repository    PASS                     Scope and         This is a standalone artifact; no repository mutation was
  files modified                                  metadata          performed.
  ----------------------------------------------------------------------------------------------------------------------------

### Final trust statement

This document is a complete teaching artifact with an explicit
self-audit, not a verified production implementation. The audit reflects
the supplied Unit 7 prompt; the exact `Roadmap_ptree.md` and primary M14
syllabus were not independently verified in full. Official documentation
was not consulted live. The scripts are included for learning but were
not executed; no PostgreSQL replication, MinIO replication, network
fault, promotion, or failover experiment was run. Before use, verify
current official documentation and installed versions, inspect the real
repository tree, run each lab safely with retained evidence, and obtain
technical review. Two local `kind` clusters on one laptop are not two
real geographic regions, and absence of anomalies in a lab is not proof
of correctness.

**Overall status: PASS for teaching-content coverage; PARTIAL for
source-tree verification; BLOCKED for live documentation verification
and implementation/test readiness.**
