# Active-Active vs Active-Passive Regional Designs

> **Stage:** Stage 2E --- Production DevOps & Platform Engineering\
> **Module:** M14 --- Multi-Cluster and Multi-Region Operations\
> **Unit:** 6 --- Active-active vs active-passive regional designs\
> **Target filename:**
> `06-active-active-vs-active-passive-regional-designs.md`\
> **Estimated time:** 24--40 hours, illustrative\
> **Prerequisites:** M13 DR foundations; M14 Units 1--5; Kubernetes
> workloads, Services, probes, GitOps, PostgreSQL fundamentals,
> SRE/SLOs, observability, and capacity basics.\
> **Core tools:** two local `kind` clusters, `kubectl`, Docker, Git,
> Python 3, `curl`, `psql` if available, and a local load generator.\
> **Awareness:** Cluster API, global traffic management, multi-writer
> databases, CRDTs, global database products, and managed regional
> services.\
> **Stack profile:** sequence labs; do not run all heavy components
> simultaneously on an 8 GB laptop.\
> **Footprint:** approximately 4 CPU cores, 8 GB RAM, and 30 GB free
> disk; measure yours.\
> **Clusters touched:** `stage2e-east-lab`, `stage2e-west-lab` only
> after verifying they are throwaway lab clusters.\
> **Destructive labs:** only scoped operations against verified lab
> resources.\
> **Review status:** authoring review, 2026-10-29. Live
> official-document verification and end-to-end lab execution were not
> performed. Version-sensitive items are marked `[VERIFY]`.

## Learning outcomes

By completing this unit, you should be able to:

1.  Define active-active, active-passive, cold standby, pilot light,
    warm standby, hot standby, follow-the-sun, read-local/write-primary,
    regional affinity, home region, and cell-based architecture.
2.  Select a pattern per workload/component instead of calling an entire
    platform "active-active."
3.  Compare designs against recovery time objective (RTO), recovery
    point objective (RPO), user latency, consistency, availability
    objectives, compliance/data residency, cost, team capability, and
    operational complexity.
4.  Explain why stateless serving is usually the easiest active-active
    tier and why multi-writer state is substantially harder.
5.  Design a request path served end-to-end in one region, with regional
    dependencies resolved locally.
6.  Explain read-local/write-primary, replication lag, stale reads,
    read-your-writes options, write forwarding, idempotency, and failure
    behavior.
7.  Design tenant home-region routing and cells, including migration,
    isolation, global uniqueness, residency boundaries, and
    routing-layer availability.
8.  Operate active-passive standby with configuration parity, readiness
    checks, capacity pre-provisioning or scale-on-demand, replication
    monitoring, and routine evacuation/fail-back practice.
9.  Calculate N+1 capacity and measure the SLO impact of evacuating a
    region.
10. Compare single-writer replication, partitioned writes, and
    multi-writer data designs, including anomalies each can permit.
11. Produce a workload decision matrix and architecture decision record
    (ADR) with assumptions, evidence, trade-offs, and revisit triggers.
12. Conduct safe, bounded local evacuation exercises with context
    guards, abort criteria, cleanup, and retained evidence.
13. Explain precisely what two local clusters demonstrate---and what
    they cannot prove.

------------------------------------------------------------------------

## Relationship to M13 and Unit Boundaries

> M13 Unit 6 taught DR strategy and failure handling: failure domains,
> dependency outages, the DR strategy spectrum, failover and fail-back
> drills, split-brain/fencing, and post-failover steady state, using a
> primary and a DR cluster. This unit teaches the **steady-state
> architecture and operation** of multi-region designs: active-passive
> and active-active patterns, partitioning/cells, routing, capacity,
> consistency implications, and operational practice. DR recovery
> mechanics, recovery markers, and restore verification are not repeated
> --- they are referenced.

This unit extends M13 rather than duplicating it. Refer to M13 for
recovery mechanics, recovery markers, restore verification,
promotion/fencing procedures, and the full treatment of RTO/RPO. M14
Unit 5 covers the global traffic layer, DNS/client behavior, traffic
weights, and local traffic-switching simulation. M14 Unit 7 owns deeper
replication-topology and consistency guarantees. This unit explains the
architectural implications of those mechanisms so you can choose a
design without re-teaching the complete recovery or database-consistency
syllabus.

**Roadmap constraints:** The stage is zero-budget. Two `kind` clusters
on one laptop are logical lab regions, not real regions. They share host
power, CPU, kernel, storage, and often networking. The roadmap marks
true global traffic management as "Not feasible free"; local endpoint
switching can be simulated, but real global routing and independent
regional failure detection require real infrastructure. Never claim that
local results establish geographic resilience, provider behavior, WAN
performance, or production correctness.

------------------------------------------------------------------------

## The core design question: what does "active" mean for each component?

"Active-active platform" is too broad to be a useful design statement. A
platform can have two active inference APIs, one writable PostgreSQL
primary, read replicas in both regions, replicated object storage, a
home-region tenant map, and a single central deployment controller.
Those components have different availability, consistency, and failure
semantics.

Ask these questions for every component:

-   Does it serve production traffic in both regions at steady state?
-   Can both regions accept writes, or is there one write authority?
-   Is state replicated, partitioned, reconstructed, or not shared?
-   Are dependencies local to the serving region?
-   What happens during a network partition or asymmetric failure?
-   How much capacity remains after one region is lost?
-   Can the team observe and operate the component if a management plane
    is unavailable?
-   What evidence supports the stated RTO, RPO, latency, and
    availability claims?

A design is a set of component-level decisions, not a label.
Active-active stateless serving does not imply multi-writer databases.
Conversely, a multi-writer database does not automatically make the
application safely active-active.

## Failure-domain model

``` text
Business service
├── Region East
│   ├── cluster east
│   ├── local inference API / cache / dependencies
│   └── regional data replica or assigned data partitions
├── Region West
│   ├── cluster west
│   ├── local inference API / cache / dependencies
│   └── regional data replica or assigned data partitions
├── Shared dependencies (possible hidden coupling)
│   ├── identity/secrets authority
│   ├── tenant-to-home-region map
│   ├── global DNS/traffic control
│   └── database write authority
└── Management plane
    ├── GitOps hub / CI
    ├── central observability
    └── fleet policy and routing control
```

**Interpretation:** two regional clusters are not independent if both
depend synchronously on a service in one region, or if a single routing
map, identity service, or database authority is a shared failure point.
Distinguish region, cluster, host, network, shared dependency, and
management/control plane. An outage in the control plane may prevent a
change while already-running data-plane traffic continues; whether it
continues depends on where policy and dependencies live. Test this
explicitly.

------------------------------------------------------------------------

# L1 --- Foundations and precise definitions

## 1. Pattern taxonomy

### Active-passive

One region serves production traffic while another is standby. The
standby may be almost absent, partially running, fully running, or
receiving replicated data. "Passive" describes production-serving
responsibility, not necessarily whether the infrastructure is powered
on.

**Why it exists:** it simplifies write authority and conflict handling.
It can be cheaper than maintaining two regions capable of serving all
traffic, but recovery time and capacity depend on how much is
pre-provisioned and tested.

#### Cold standby

Most application infrastructure is recreated or restored after a
failure. It may be economical for low-criticality workloads but depends
on reliable automation, backups, quotas, images, secrets, and recovery
practice. Refer to M13 backup/restore units for mechanics; do not treat
"we have infrastructure-as-code" as proof that the service can be
restored within its RTO.

#### Pilot light

A minimal set of foundational services and data replication remain
running; the full serving stack is started or scaled after an incident.
It reduces some rebuild time but creates scale-up, dependency, and
configuration-parity risks. Test the missing pieces, not only the
components already running.

#### Warm standby

A substantially complete but scaled-down stack remains running and
receives relevant data/configuration updates. Failover still requires
capacity expansion and traffic movement. The standby can be "healthy"
while unable to serve full demand or missing a certificate, model
artifact, quota, secret, or dependency.

#### Hot standby

A complete standby is kept ready, often near production capacity. The
term varies across providers and frameworks `[VERIFY]`. It can reduce
activation time but costs more and still needs continuous parity, data
readiness, routing, and fencing checks. "Hot" does not mean
automatically safe for writes.

### Active-active

Multiple regions serve production traffic concurrently. This can reduce
user latency and improve resilience, but only when regional
dependencies, capacity, data behavior, routing, and operations support
it.

-   **Stateless active-active:** both regions run the same application
    and can serve requests independently. Usually the simplest form,
    assuming sessions, caches, authentication, feature lookups, model
    artifacts, and downstream dependencies do not reintroduce a
    single-region dependency.
-   **Active-active with partitioned data:** both regions serve traffic,
    but each tenant/data partition has a designated owner or home
    region. Partition ownership avoids many concurrent-write conflicts
    and can align with residency boundaries.
-   **Active-active with replicated multi-writer data:** both regions
    can accept writes to overlapping logical data. This is the most
    demanding pattern because concurrent operations can conflict, arrive
    out of order, or be reconciled in ways that violate business
    invariants.

### Follow-the-sun

The active region changes by a schedule or operating window, for example
to align processing with a team's working hours. It requires explicit
handover of ownership, queued work, credentials, schedules, and data
state. It is not automatically a disaster-recovery pattern: scheduled
handover must be rehearsed, and a time-based switch must not permit two
regions to believe they own the same writes.

### Read-local/write-primary

Reads are served from a regional replica where acceptable; writes are
forwarded to one designated primary. This reduces read latency but may
return stale values and adds cross-region latency to writes. If the
primary is unavailable, writes generally fail or queue under an
explicitly designed policy; a regional endpoint must not silently
promote itself.

### Regional affinity and home region

A user, tenant, dataset, or workload is assigned to a preferred region.
Affinity reduces repeated cross-region calls and can support residency
constraints. The assignment map is critical state: if it exists only in
one region or cannot be read during an incident, routing may fail
globally. Define behavior for unknown, stale, or conflicting
assignments.

### Cell-based architecture

The system is divided into bounded, largely self-contained cells. A cell
serves a tenant or a set of tenants and limits the blast radius of many
failures. Cells may be placed across regions, but a "cell" is not
automatically a geographic region. Global control, identity, analytics,
and routing can still create shared dependencies. Cross-cell analytics
is often better served through asynchronous read models than synchronous
fan-out in user requests.

### Comparison table

  ---------------------------------------------------------------------------------------------------------------------------
  Pattern                    Traffic/data flow    Typical fit     Main benefit           Principal         Evidence required
                                                                                         cost/risk         
  -------------------------- -------------------- --------------- ---------------------- ----------------- ------------------
  Cold standby               Primary serves;      Lower           Lower steady-state     Restore and       Timed
                             standby              criticality,    spend                  provisioning      restore/failover
                             rebuilt/restored     tolerant RTO                           time; hidden      drill, dependency
                             after incident                                              missing           inventory
                                                                                         dependencies      

  Pilot light                Primary serves;      Moderate        Less rebuild work than Scale-up and      Activation time,
                             minimal foundations  recovery needs  cold                   missing-stack     parity checks,
                             and data path remain                                        risk              quota verification

  Warm standby               Primary serves;      Moderate/high   Faster activation than Capacity ramp and Readiness plus
                             complete smaller     criticality     pilot light            stale config/data scale-up and load
                             stack and                                                                     test
                             replication remain                                                            

  Hot standby                Primary serves;      Shorter         Less scale-up delay    Higher cost;      Full traffic
                             standby close to     activation                             still requires    rehearsal, parity,
                             full                 target                                 fencing and       capacity and data
                             readiness/capacity                                          routing           checks

  Stateless active-active    Both regions serve;  Global          Regional latency and   Duplicate         Per-region SLO,
                             dependencies local   inference/API   serving redundancy     capacity,         evacuation test,
                             or explicitly safe   serving                                dependency        dependency traces
                                                                                         coupling          

  Partitioned active-active  Both regions serve   Home-region or  Limits conflicting     Migration and     Partition
                             disjoint             cell workloads  writes                 ownership         ownership,
                             partitions/tenants                                          complexity        isolation and
                                                                                                           migration tests

  Multi-writer active-active Both regions write   Only when       Local write            Conflicts,        Formal semantics,
                             overlapping data     semantics       availability/latency   anomalies,        conflict tests,
                                                  justify it                             reconciliation,   partition drills
                                                                                         operational       
                                                                                         burden            

  Read-local/write-primary   Local reads; writes  Read-heavy      Fast local reads with  Staleness and     Lag, stale-read,
                             to one authority     workloads       simple write authority remote write      write-timeout,
                                                                                         latency           authority tests

  Follow-the-sun             Serving/ownership    Batch or        Aligns                 Handover,         Rehearsed
                             changes on schedule  staffed         compute/ownership with duplicate jobs,   handover,
                                                  operations      schedule               clock/schedule    ownership and
                                                                                         errors            queue tests

  Home region/cells          Requests pinned to   Multi-tenant    Isolation and          Mapping           Mapping
                             tenant/cell          platforms,      predictable data       dependency and    availability,
                             assignment           residency       locality               migration         tenant isolation,
                                                  constraints                            complexity        migration rollback
  ---------------------------------------------------------------------------------------------------------------------------

**Technical fact:** the serving pattern and data consistency pattern are
separate dimensions. For example, two active inference APIs can read
from regional replicas while only one PostgreSQL primary accepts writes.

## 2. Pattern selection criteria

Choose the least complex architecture that satisfies the actual business
requirement. Active-active is not inherently superior to a well-tested
single-region design with a credible DR plan.

  -----------------------------------------------------------------------
  Criterion               Questions to answer     Architectural
                                                  implication
  ----------------------- ----------------------- -----------------------
  Business criticality    What user journey must  Low criticality may
                          survive? What is the    justify cold/warm
                          impact of regional      standby; critical
                          loss?                   user-facing serving may
                                                  justify active-active

  RTO/RPO                 What recovery time and  Refer to M13 Unit 1 for
                          data-loss window are    full definitions;
                          accepted?               validate with timed
                                                  drills and lag evidence

  Latency                 Are users               Local serving helps
                          geographically          only if dependencies
                          distributed? Is local   are local too
                          data access required?   

  Consistency             Can users tolerate      Single-writer,
                          stale reads, reordered  partitioned ownership,
                          events, or conflicts?   or multi-writer
                                                  semantics must be
                                                  explicit

  Residency/compliance    Must particular data    Pin data/workloads by
                          remain in a             design and verify
                          jurisdiction?           backups, telemetry,
                                                  logs, artifacts, and
                                                  replicas

  Dependency locality     Does every request call Remove or explicitly
                          a central               accept cross-region
                          DB/cache/identity       synchronous
                          service?                dependencies

  Capacity                Can a survivor absorb   N+1 capacity,
                          demand within the       pre-scaling, quotas,
                          required time?          and shedding policy

  Replication/network     How much state crosses  Measure transfer and
  cost                    regions and how often?  operational burden; M15
                                                  covers deeper economics

  Team/on-call capability Can the team diagnose   Complexity without
                          both regions and data   operational ownership
                          conflicts at 03:00?     is a reliability risk

  Partial failure         What if one direction   Define authority,
                          of the network fails or timeouts, safe mode,
                          signals disagree?       and fencing

  Management plane        Can traffic/data plane  Avoid hidden runtime
                          continue if GitOps or   dependence on a single
                          central observability   control-plane region
                          is down?                

  Necessity               Is a second active      A simpler single-region
                          region required to meet plus tested DR may be
                          objectives?             the right answer
  -----------------------------------------------------------------------

### Quick decision framework

1.  Start with business SLO, RTO/RPO, residency, and demand---not a
    product preference.
2.  Decide per component whether it must serve, read, or write in both
    regions.
3.  Make state ownership explicit.
4.  Keep synchronous request dependencies regional where possible.
5.  Prove one-region-loss capacity and data safety.
6.  Rehearse failure, degraded mode, and fail-back.
7.  Record what evidence would cause the design to change.

## 3. Cost of active-active and N+1 capacity

Active-active has costs beyond duplicating compute: regional data
replicas, inter-region transfer, duplicated caches and dependencies,
observability, testing, deployment governance,
consistency/reconciliation work, on-call training, and the capacity
needed when one region is lost. "Both regions run at 50%" does not prove
either region can take 100% of total load. Safe throughput, not nominal
utilization, is the relevant measurement.

### Synthetic capacity example

`[SYNTHETIC]` Suppose total normal demand is 1,000 requests/second
(req/s), split evenly between two regions. Each region has a tested
sustainable capacity of 700 req/s, and the design targets no more than
70% utilization under the expected post-evacuation load.

-   Normal traffic per region = `1,000 / 2 = 500 req/s`.
-   Normal utilization per region = `500 / 700 ≈ 71.4%`.
-   After evacuating one region, survivor demand = `1,000 req/s`.
-   Raw post-failure utilization = `1,000 / 700 ≈ 142.9%`; the survivor
    cannot safely serve all demand.
-   Capacity required to stay at or below 70% utilization =
    `1,000 / 0.70 ≈ 1,429 req/s`.
-   Capacity shortfall relative to current 700 req/s =
    `1,429 - 700 = 729 req/s`.
-   If autoscaling takes 4 minutes, that 4-minute interval must be
    covered by pre-provisioned capacity, load shedding, queueing, or a
    deliberate brownout policy. Scaling after the surge begins does not
    erase the overload interval.

The numbers are assumptions for arithmetic, not benchmark results.
Capacity depends on request mix, cache state, model size, dependency
throughput, quotas, and latency SLOs.

``` text
[SYNTHETIC] Normal:
East   500 req/s -> 700 req/s tested capacity  (~71%)
West   500 req/s -> 700 req/s tested capacity  (~71%)

[SYNTHETIC] After West evacuation:
East 1,000 req/s -> 700 req/s tested capacity (~143%)  OVERLOAD

Target with 30% headroom:
East needs at least 1,429 req/s tested sustainable capacity.
```

### Capacity calculator with tests

Save as `capacity_model.py` in a learner-owned temporary lab directory.
This script is a calculator; it is not a load test and cannot establish
real safe capacity.

``` python
from dataclasses import dataclass
import math
import unittest

@dataclass(frozen=True)
class CapacityResult:
    total_load_rps: float
    regions: int
    capacity_per_region_rps: float
    safe_utilization: float
    load_per_region_normal_rps: float
    utilization_normal: float
    utilization_after_one_region_loss: float
    required_capacity_per_survivor_rps: float
    overloaded_after_loss: bool

def evaluate(total_load_rps, regions, capacity_per_region_rps,
             safe_utilization=0.70):
    if not math.isfinite(total_load_rps) or total_load_rps <= 0:
        raise ValueError("total_load_rps must be finite and > 0")
    if not isinstance(regions, int) or regions < 2:
        raise ValueError("regions must be an integer >= 2")
    if not math.isfinite(capacity_per_region_rps) or capacity_per_region_rps <= 0:
        raise ValueError("capacity_per_region_rps must be finite and > 0")
    if not 0 < safe_utilization < 1:
        raise ValueError("safe_utilization must be between 0 and 1")
    normal = total_load_rps / regions
    post_loss = total_load_rps / capacity_per_region_rps
    required = total_load_rps / safe_utilization
    return CapacityResult(
        total_load_rps, regions, capacity_per_region_rps, safe_utilization,
        normal, normal / capacity_per_region_rps, post_loss, required,
        post_loss > 1.0
    )

class CapacityTests(unittest.TestCase):
    def test_two_regions_fit_normal_but_overload_after_loss(self):
        r = evaluate(1000, 2, 700, 0.70)
        self.assertAlmostEqual(r.load_per_region_normal_rps, 500)
        self.assertGreater(r.utilization_after_one_region_loss, 1.0)
        self.assertTrue(r.overloaded_after_loss)
        self.assertAlmostEqual(r.required_capacity_per_survivor_rps, 1000/0.70)

    def test_three_regions_post_loss_is_two_survivors_not_one(self):
        # Model reports a single survivor requirement; this is the conservative
        # one-region-left case, not a two-survivor redistribution simulation.
        r = evaluate(900, 3, 600, 0.75)
        self.assertAlmostEqual(r.load_per_region_normal_rps, 300)
        self.assertAlmostEqual(r.utilization_after_one_region_loss, 1.5)

    def test_invalid_inputs_rejected(self):
        for args in [(0, 2, 100), (100, 1, 100), (100, 2, 0)]:
            with self.assertRaises(ValueError):
                evaluate(*args)

if __name__ == "__main__":
    result = evaluate(1000, 2, 700, 0.70)
    print(result)
    unittest.main(argv=["capacity_model.py"], exit=False)
```

**Interpretation note:** `utilization_after_one_region_loss`
deliberately models the conservative case where one surviving region
takes all demand. For more than two regions, create a separate
distribution model that calculates demand across all surviving regions;
do not mistake the simplified conservative calculation for a general
multi-region scheduler.

### Capacity verification checklist

-   Use representative request mix, not only a trivial health endpoint.
-   Measure sustainable throughput at the latency/error SLO.
-   Test cold caches, dependency saturation, model load, and concurrent
    scale-up.
-   Verify regional quotas and autoscaling limits before the incident.
-   Calculate the interval before extra capacity becomes ready.
-   Define load shedding, admission control, queue bounds, and retry
    budgets.
-   Re-run after material traffic, model, dependency, or quota changes.

------------------------------------------------------------------------

# L2 --- Implementing and operating the patterns

## 4. Data/AI platform workload mapping

These are `[RECOMMENDATION]` starting points for a sample data/ML
platform, not universal mandates.

  -------------------------------------------------------------------------------------
  Component            Starting pattern          Rationale         Key risks / evidence
  -------------------- ------------------------- ----------------- --------------------
  Inference API        Stateless active-active   Requests can be   Prove identical
                       when dependencies are     served in either  image digest,
                       regional                  region            per-region SLO,
                                                                   local dependency
                                                                   path, N+1 capacity

  Feature lookups      Regional read replicas or Low-latency reads Stale features may
                       replicated feature store;                   change prediction
                       home-region where                           quality; measure lag
                       freshness matters                           and feature
                                                                   freshness

  PostgreSQL system of Single-writer primary     Clear write       Lag, stale reads,
  record               with cross-region replica authority         write latency,
                       unless justified                            promotion/fencing;
                       otherwise                                   Unit 7 covers deeper
                                                                   guarantees

  Model                Replicated object         Serving region    Digest mismatch,
  registry/artifacts   storage/artifacts; writes needs immutable   replication delay,
                       may originate in training artifact          missing artifact on
                       region                    availability      standby

  ETL/batch            One region near data or   Data gravity and  Duplicate jobs,
                       explicit per-region       controlled        checkpoint
                       partitions                ownership         collisions, transfer
                                                                   cost

  Streaming            Per-region consumers on   Regional          Ordering, duplicate
                       mirrored topics or        processing        events,
                       partition by region       autonomy          offset/consumer
                                                                   ownership

  Notebooks            Region-local where data   Data locality and Central auth, data
                       residency/interactive     analyst           movement, notebook
                       latency justifies it      experience        state and idle
                                                                   resource cost

  Caches               Local caches, with        Avoid             Stale cache,
                       explicit invalidation/TTL cross-region      cold-start surge,
                       semantics                 cache latency     divergent keys

  Secrets/identity     Regional agents/caches    Runtime auth      Stale rotated
                       and a resilient identity  should not rely   credentials, central
                       design                    on one failed     issuer outage,
                                                 region            unsafe fallback

  Registry mirrors     Local                     Avoid remote      Missing digest,
                       pull-through/replicated   image pulls       trust policy drift,
                       mirrors                   during region     cache warming
                                                 failure           

  Telemetry            Local                     Keep local        Lost buffered data,
                       buffering/collection plus diagnosis         cardinality, central
                       central aggregation       available if hub  hub SPOF
                                                 is down           

  CI/CD/GitOps control Central management may be Easier governance Hub failure prevents
  plane                acceptable if data plane                    changes; global
                       keeps serving                               rollout blast
                                                                   radius; verify
                                                                   runtime independence

  Tenant routing map   Replicated, versioned map Route each tenant Map availability
                       or carefully designed     to owner          becomes global
                       routing service                             dependency;
                                                                   stale/unknown
                                                                   mapping behavior
  -------------------------------------------------------------------------------------

## 5. Active-active stateless serving

### Request-flow rule

A request should usually be served end-to-end in one region:

``` text
Client
  -> regional entry
  -> inference API in West
       -> West cache
       -> West feature read model/replica
       -> West model artifact mirror
       -> West identity/secret access path
       -> response with region=west, trace_id=...
```

A common anti-pattern is "the API is active-active" while every request
calls a database, feature store, cache, or identity service in East.
When East fails, West's pods can remain green while the user journey
fails. Every cross-region synchronous call needs an explicit timeout,
fallback, owner, and reason; preferably remove it from the request path
by localizing or partitioning the dependency.

### GitOps and parity

Use M14 Unit 3 for the actual GitOps controller workflow. The principles
here are:

-   Build once and deploy the same immutable image digest to both
    regions.
-   Keep common configuration common; keep regional differences explicit
    and reviewed.
-   Avoid mutable tags such as `latest` as evidence of artifact parity.
-   Check deployment image digests, configuration revisions,
    certificate/secret presence (never values), model artifact digests,
    dependency endpoints, and readiness.
-   Roll changes through a canary/ring or one region at a time when the
    architecture permits it.
-   Do not let one bad global configuration fan out to both regions
    without a halt gate.

Illustrative layout (not a claim about the supplied repository tree):

``` text
platform-config/
  base/
    inference-api.yaml
  regions/
    east/
      values.yaml
    west/
      values.yaml
  policy/
    parity-checks.yaml
```

A regional overlay should change only what is region-specific, such as
replica count, local endpoint, zone/region label, or regional quota.
Secret values belong in the approved secret system, not in Git.

### Proving which region served a request

Add a non-sensitive response header such as `X-Serving-Region: east` and
structured log/trace fields like `region`, `cluster`, `image_digest`,
and `config_revision`. Do not add raw tenant IDs as unbounded metric
labels; use bounded dimensions and carefully controlled sampling for
tenant-specific diagnostics.

**Positive test:** send requests directly to both regional endpoints and
confirm distinct region identity with the same image digest.

**Negative test:** configure the West API to call an East-only
dependency. The detector should fail the lab or mark the dependency as
cross-region. A simple local substitute is a dependency allowlist that
compares each region's declared local endpoints against the actual
request destination. It does not replace distributed tracing in
production.

Example detector input:

``` json
{
  "serving_region": "west",
  "dependency": "feature-store",
  "declared_local_endpoint": "http://feature-store.west.svc",
  "observed_endpoint": "http://feature-store.east.svc",
  "expected": "west-local",
  "result": "FAIL"
}
```

The sample is illustrative. Collect actual evidence from request
logs/traces in the lab; do not claim the sample was observed.

### Regional and global SLOs

Define per-region service-level indicators (SLIs) and objectives (SLOs)
for request success, latency, saturation, and critical dependencies.
Define a global SLO too, but never rely only on a global average: high
traffic in East can mask a complete outage in West. Label metrics by
region and service; avoid uncontrolled high-cardinality labels.

## 6. Read-local/write-primary, lag, and write forwarding

### Request paths

``` text
READ:
Client -> West API -> West read replica -> response
                       (may be stale)

WRITE:
Client -> West API -> bounded authenticated forwarding
                  -> East primary -> commit
                  <- result/timeout <- 
```

Cross-region writes add network latency and can fail when the primary is
unreachable. A local replica may lag behind committed writes. "The write
committed" and "the replica can immediately show it" are different
claims.

### Replication-lag timeline

``` text
t0  Client sends write v42 to primary East
t1  East commits v42 and returns success
t2  Replication stream has not yet applied v42 in West
t3  Client reads locally from West and sees v41 (stale)
t4  West applies v42; later read sees v42
```

This is a simplified eventual-visibility example, not a universal
database guarantee.

### Read-your-writes options

1.  **Pin the session to the primary for a bounded window.**
    `[ILLUSTRATIVE]` For example, route a user to the primary for 10
    seconds after a successful write. The window must be measured and
    chosen for the actual replication behavior; it is not a guarantee if
    lag exceeds the window.
2.  **Use a replication position/version token and wait for replica
    catch-up.** PostgreSQL-specific LSN and replay-wait behavior must be
    checked against the installed PostgreSQL version and official docs
    `[VERIFY]`. Define timeout and fallback if the replica cannot catch
    up.
3.  **Return the committed version and make reads version-aware.**
    Application semantics must handle "not yet visible" without silently
    returning an older value as fresh.

Do not confuse eventual visibility with durability, linearizability, or
exactly-once execution.

### Write forwarding, retries, and idempotency

A forwarding API needs: - bounded connect/read timeouts and an overall
deadline; - authenticated, authorized routing to the designated
primary; - idempotency keys for operations where duplicate submission
would be harmful; - a durable way to associate a request key with its
result where required; - clear handling of unknown outcomes; - bounded
retries with backoff/jitter and a retry budget; - observability for
forwarding latency, errors, timeout, duplicate suppression, and primary
identity.

**Ambiguous outcome:** the primary may commit a write and the response
may be lost. A client retry can submit the same operation again.
Idempotency can make duplicate attempts safe only if the application and
storage transaction implement the contract correctly.

**Primary unavailable:** do not send writes to a replica merely because
it is reachable. Writes remain blocked until the approved promotion and
fencing mechanism confirms one authoritative writer. Refer to M13 Unit 6
and M14 Unit 7; this unit does not substitute for their
promotion/consistency procedures.

### Negative tests

-   A write request targeting an unpromoted replica is rejected.
-   A timeout after primary commit is retried with the same idempotency
    key and does not duplicate the effect in the test implementation.
-   A stale local read is visible in the controlled simulation and is
    not mislabeled as fresh.
-   Unknown primary authority blocks writes rather than choosing a
    region by convenience.

## 7. Tenant home-region routing and cells

### Routing model

``` text
Client request (tenant key)
       |
       v
Routing layer -> versioned tenant map
       |                |
       | tenant A       | tenant B
       v                v
   Cell/East          Cell/West
   local API          local API
   local data         local data
```

The mapping is critical control data. If the map is stored only in East,
then East can become a global routing dependency even when West's
application and data are healthy. Replicate/version the map or design an
explicitly safe fallback. Unknown or stale mappings should not silently
route to an arbitrary region.

### Global uniqueness and data residency

-   Region-prefixed identifiers can help avoid collisions, but consumers
    must preserve the prefix and uniqueness assumptions.
-   UUID-family identifiers may be appropriate depending on the system,
    but collision risk, ordering, and application semantics still need
    to be understood.
-   A global sequence or centralized ID service may introduce a
    cross-region dependency.
-   Residency must be enforced across primary data, replicas, backups,
    logs, telemetry, feature stores, model artifacts, and support
    access---not only the database's main table.
-   Product examples of globally distributed databases are awareness
    material, not endorsements; verify current guarantees and residency
    behavior `[VERIFY]`.

### Tenant migration procedure

1.  Define source, destination, tenant scope, data classes, and rollback
    conditions.
2.  Confirm destination capacity, dependency readiness, residency
    eligibility, and artifact availability.
3.  Plan data movement/replication and the handling of writes during
    migration.
4.  Freeze or coordinate writes if required by the data model; never
    assume a generic copy is transactionally safe.
5.  Validate counts, checksums, versions, ownership, and relevant
    application invariants.
6.  Change the versioned routing map using an approved rollout.
7.  Observe errors, latency, data freshness, and duplicate work.
8.  Roll back routing if gates fail, while preserving data-integrity
    controls.
9.  Remove source copies only after explicit validation, retention, and
    compliance requirements are satisfied.

A small lab script can demonstrate the routing state machine; it cannot
safely migrate production data by itself.

### Cell isolation test

Create two synthetic tenants assigned to different cells. Stop or block
West's cell and verify that East-owned requests continue, while
West-owned requests receive the documented degraded/unavailable response
rather than being sent to the wrong cell. This is a local logical
isolation test, not proof of physical region isolation.

## 8. Active-passive operations and warm-standby readiness

Active-passive reduces write conflicts but does not remove operational
complexity. The standby must be continuously tested, not merely declared
available in a diagram.

### Parity/readiness dimensions

-   **Configuration:** approved revision, feature flags, policy bundle,
    service account and network policy.
-   **Artifact:** same immutable image digest; required model/data
    artifacts exist and have verified digests.
-   **TLS:** certificate exists, hostname/trust is valid, expiry is
    monitored.
-   **Secrets/identity:** required secret references and identity trust
    are available; do not log secret values.
-   **Dependencies:** endpoints, credentials, quotas, registry mirrors,
    object storage, telemetry path.
-   **Data:** replication health/lag and promotion/fencing status where
    relevant.
-   **Capacity:** measured safe throughput, quotas, autoscaling
    behavior, cache warm-up, queue capacity.
-   **Routing:** traffic can be shifted and the standby can be observed
    end-to-end.
-   **Operations:** runbook, owner, alert routing, rollback, and
    evidence retention.

A standby with healthy pods but a missing certificate or model artifact
is not ready. Readiness must reflect the user journey and required
dependencies, not only process health.

### Pre-provisioning versus scale-on-demand

  -----------------------------------------------------------------------
  Strategy                Benefit                 Risk
  ----------------------- ----------------------- -----------------------
  Pre-provision enough    Shorter activation      Higher steady-state
  capacity for full load  time; less dependence   cost and idle resources
                          on quota/scaling        

  Keep scaled-down        Lower baseline cost     Scale-up delay, quota
  standby and scale on                            limits, cold starts,
  demand                                          cache/model loading

  Hybrid: baseline        Balances cost and       Requires measured
  capacity plus reserved  recovery speed          scaling curve and quota
  scaling headroom                                management
  -----------------------------------------------------------------------

Use M15 for deeper cost/FinOps analysis. This unit does not invent cloud
prices or universal headroom percentages.

### Routine evacuation

A planned evacuation is an operational exercise: verify standby
readiness, shift or drain traffic using the Unit 5 mechanism, measure
user impact and survivor capacity, observe queues and asynchronous work,
and then reintroduce the region gradually. Fail-back is a controlled
rollout, not an immediate reversal.

------------------------------------------------------------------------

# L3 --- Architecture decisions and advanced failure analysis

## 9. Workload-by-workload architecture decision matrix

The following matrix is a starting point for the sample data/ML
platform. Each decision must be reviewed against real workload
semantics.

  -----------------------------------------------------------------------------------------------------
  Workload           Candidate pattern      Why it may fit Main trade-offs / risks  Required evidence
  ------------------ ---------------------- -------------- ------------------------ -------------------
  Inference API      Stateless              Independent    Hidden single-region     Same digest, local
                     active-active          serving can    feature/auth/artifact    dependency traces,
                                            continue in    dependency; N+1 capacity per-region SLO,
                                            either region                           evacuation test

  Feature store      Read-local replicas;   Low-latency    Stale features can       Freshness
                     tenant partitioning if lookups        change predictions;      distribution,
                     writes occur                          replication lag          stale-read test,
                                                                                    fallback behavior

  PostgreSQL system  Single writer with     Clear write    Remote write latency,    Lag alerts,
  of record          replica                authority and  RPO exposure during lag, write-block test,
                                            simpler        promotion risk           M13
                                            conflict model                          promotion/fencing
                                                                                    evidence

  Model registry     Replicated             Serving needs  Metadata/artifact        Digest parity and
                     metadata/artifacts or  stable model   mismatch, stale          artifact
                     region-local read      identity       registry, replication    availability
                     model                                 delay                    

  Object storage     Replication with       Large          Egress/transfer cost,    Checksums,
                     explicit write         artifacts      replication delay,       versioning,
                     ownership              available near overwrite conflict       regional
                                            serving                                 availability test

  ETL/batch          Home-region execution  Data gravity   Duplicate jobs and       Scheduler
                     or partitioned jobs    and explicit   cross-region data        ownership,
                                            checkpoint     movement                 checkpoint/offset
                                            ownership                               uniqueness

  Streaming          Per-region             Regional       Ordering, duplicates,    Lag/duplicate
                     consumers/mirrored     processing     mirror lag, offset       tests, consumer
                     topics or                             semantics                ownership
                     region-partitioned                                             
                     stream                                                         

  Notebooks          Region-local by data   Interactive    State sync, identity     Access/data-path
                     boundary               latency and    dependency, idle cost    audit, session
                                            residency                               continuity
                                                                                    expectations

  Cache              Region-local,          Low latency    Cold cache surge, stale  Warm-up test,
                     reconstructable        and            values, invalidation     TTL/invalidation
                                            independent    divergence               contract
                                            request path                            

  Secrets/identity   Regional trust/cache   Reduces        Stale rotated secret,    Rotation parity
                     with tested central    runtime        identity/control-plane   test, auth during
                     dependencies           dependence on  outage                   hub outage
                                            one region                              

  Registry mirror    Regional pull-through  Deploy/scale   Missing digest or        Digest and
                     or replicated          without remote trust-policy drift       signature
                     immutable artifacts    registry                                verification in
                                            dependency                              both regions

  Telemetry          Local                  Local incident Buffer loss,             Hub-outage test and
                     collection/buffering   visibility if  cardinality, central     local
                     with central           hub is down    view delay               dashboards/logs
                     aggregation                                                    

  CI/CD and GitOps   Central control with   Central        Changes stop if hub is   Runtime
                     independent running    governance     down; bad rollout fans   independence and
                     data plane                            out                      ring/rollback test

  Tenant routing     Replicated, versioned  Predictable    Routing map can become   Map failover,
                     home-region map        ownership      global SPOF              stale/unknown
                                                                                    tenant tests
  -----------------------------------------------------------------------------------------------------

## 10. Partitioned writes versus multi-writer data

### Partitioned ownership

Each tenant or key range has a designated write owner. Other regions may
serve read replicas, but writes are forwarded to the owner or rejected
during an ownership transition. This limits conflict scope but makes
migration, ownership transfer, and owner unavailability explicit design
problems.

### Multi-writer designs

Both regions accept writes to overlapping logical data. They require
defined conflict semantics, not merely replication enabled. Possible
approaches include: - **Last-write-wins (LWW):** choose one update based
on a timestamp/order rule. Simple but may discard a valid update; clocks
and tie-breaking can affect the result. - **Application merge:**
business-specific reconciliation such as set union or merging
independent fields. Correctness depends on domain invariants. -
**Conflict-free replicated data types (CRDTs):** data types with defined
merge properties for particular operations. They do not magically solve
arbitrary business transactions or cross-object invariants. - **Event
sourcing/append-only events:** preserve operations for
replay/reconciliation, but still require idempotency, ordering
semantics, and projection correctness.

Global database products such as Spanner, CockroachDB, YugabyteDB,
Cosmos DB, DynamoDB global tables, Aurora Global, or Cassandra
multi-datacenter patterns are awareness examples only. Their guarantees,
latency, conflict behavior, availability modes, and pricing differ and
change over time `[VERIFY]`. Do not infer equivalence from the phrase
"global database."

### LWW lost-update timeline

`[SYNTHETIC]` A user's balance is 100.

``` text
t0 East reads balance=100; West reads balance=100
t1 East applies purchase -30 -> balance=70
t2 West applies purchase -20 -> balance=80
t3 Replication sees concurrent values; LWW selects West's later timestamp
t4 Final balance=80, so East's purchase is lost from the stored balance
```

This example demonstrates a possible lost update under a naïve
whole-value LWW rule. Real products have specific conflict semantics;
verify them. A safer domain model might record two idempotent purchase
events and derive the balance, or assign the account to one writer. The
correct choice depends on invariants and latency/availability
requirements.

### Decision questions for multi-writer feasibility

-   Are concurrent writes to the same entity possible?
-   Can operations commute or be merged without violating business
    invariants?
-   What happens to uniqueness constraints and multi-object
    transactions?
-   How are deletes/tombstones, retries, duplicate events, and
    reordering handled?
-   What happens during asymmetric partition when both sides accept
    writes?
-   Can reconciliation be observed, bounded, and safely retried?
-   What is the operational procedure if automatic merge produces an
    invalid business state?
-   Is the availability/latency gain worth the consistency and on-call
    burden?

If these questions lack testable answers, prefer a single writer or
partitioned ownership rather than claiming multi-writer safety.

## 11. Capacity engineering, brownout, and failover surge

A regional loss moves load as well as traffic. Autoscaling may be too
slow, quotas may block it, model artifacts may need loading, caches may
be cold, and retries can amplify demand.

Use a controlled policy: 1. Verify the surviving region's tested safe
capacity. 2. Shift only the amount that the target can accept. 3. Shed
non-critical work or degrade optional features when necessary. 4. Bound
retries, queue depth, concurrency, and request deadlines. 5. Watch
per-region latency, error rate, saturation, queue age, and dependency
limits. 6. Halt or roll back when a gate fails. 7. Do not interpret
"endpoint healthy" as "capacity healthy."

### Brownout examples

-   Serve a smaller or cached feature set if the product explicitly
    permits it.
-   Disable expensive optional enrichment behind a feature flag.
-   Reduce batch/backfill concurrency before sacrificing interactive
    inference.
-   Return a clear retryable or non-retryable error rather than queueing
    without bound.
-   Apply admission control and rate limits to protect the core user
    journey.

Every degraded mode must be documented and tested. Do not silently
degrade a prediction in ways that violate model/data safety or business
semantics.

## 12. Regional dependency and failure-mode catalog

  ----------------------------------------------------------------------------------------------------
  Failure mode        Symptoms         Evidence to       Immediate         Durable
                                       collect           containment       prevention/regression test
  ------------------- ---------------- ----------------- ----------------- ---------------------------
  Inference API       West pods green; Trace             Remove or route   Cross-region-call detector
  secretly depends on predictions fail destinations,     around unsafe     with planted violation
  East feature store  when East        request errors,   dependency only   
                      unavailable      dependency timing under approved    
                                                         policy            

  LWW drops           Final state      Conflict logs,    Stop unsafe       Domain conflict tests;
  concurrent update   lacks one        versions, event   writes if         single-writer/partitioned
                      operation        history           integrity at      design
                                                         risk; preserve    
                                                         evidence          

  West quota blocks   Surge causes     Scale events,     Shed load and     N+1 load test and quota
  scale-up            latency/errors   quota errors,     protect critical  preflight
                      despite healthy  saturation        path              
                      pods                                                 

  Global              Same failure     Git revision,     Halt fan-out;     Rings, canary, policy
  ApplicationSet      appears nearly   rollout           roll back         gates, blast-radius limits
  pushes bad config   simultaneously   timestamps,       known-good        
  to both regions                      config diff       revision          

  Replication lag     Promotion would  Lag history,      Block unsafe      Lag alert, promotion gate,
  causes RPO breach   lose more recent last-applied      promotion;        controlled lag exercise
                      writes than      position, primary quantify          
                      allowed          timeline          potential loss;   
                                                         follow M13/Unit 7 

  Secrets replica     Authentication   Secret version    Restore approved  Rotation parity check and
  stale after         fails after      metadata, auth    secret/identity   regional auth test
  rotation            regional shift   errors, issuer    path; avoid       
                                       status            printing values   

  Tenant home-region  Router cannot    Map               Use documented    Replicated versioned map
  map only in East    assign tenants   source/version,   safe              and hub-failure test
                      when East fails  route errors,     cache/fallback or 
                                       cache state       explicit          
                                                         unavailable mode  

  Partition heals     Conflicting      Version history,  Stop conflicting  Partition drill,
  after both sides    state, duplicate event IDs,        writes where      ownership/fencing,
  accepted writes     operations       conflict metrics  possible;         reconciliation test
                                                         preserve logs     

  Shared identity     Both regions     Auth path,        Use only approved Failure-domain review and
  dependency fails    reject auth      token/issuer      bounded           identity outage test
                      despite local    dependency,       cache/grace       
                      compute health   regional          policy            
                                       telemetry                           

  Cold cache after    Latency and      Cache hit ratio,  Rate-limit/warm   Warm-up exercise and N+1
  evacuation          backend load     backend           selectively; shed test
                      spike            saturation,       optional load     
                                       request latency                     

  Artifact missing in Pods start but   Artifact digest,  Keep region out   Artifact parity/readiness
  standby             model load fails registry logs,    of service        gate
                                       readiness                           

  Central telemetry   Global dashboard Local             Diagnose locally; Local observability and
  hub unavailable     missing; local   logs/metrics, hub preserve evidence hub-outage drill
                      service may      health, buffer                      
                      still run        state                               

  Cross-region stream Duplicate        Event IDs,        Pause affected    Idempotent consumers and
  duplicate/reorder   downstream       offsets, lag,     consumer if       ordering tests
                      effects or       processing logs   correctness       
                      out-of-order                       requires          
                      state                                                

  Fail-back           Restored region  Traffic weights,  Stop ramp; return Gradual ramp/bake and
  thundering herd     saturates on     cache misses,     to last safe      capacity gate
                      re-entry         latency           distribution      
  ----------------------------------------------------------------------------------------------------

## 13. Eight organizational incident stories

These are fictional scenarios for analysis, not real company incidents
or measured events.

### Story 1 --- "Active-active" inference secretly depends on East

-   **False assumption:** active APIs mean independent regions.
-   **Evidence:** traces show West synchronously calling East's feature
    store.
-   **Immediate safe action:** contain the affected request path; use a
    tested fallback or mark the affected capability unavailable rather
    than silently returning unsafe predictions.
-   **Long-term correction:** regional feature read model, partitioning,
    or an explicitly accepted dependency with a documented SLO.
-   **Regression test:** plant the cross-region endpoint and make the
    detector fail.

### Story 2 --- LWW loses updates for weeks

-   **False assumption:** latest timestamp always represents the correct
    business result.
-   **Evidence:** concurrent version histories and a reconciliation
    mismatch.
-   **Immediate safe action:** preserve event/version evidence and stop
    unsafe writes if integrity is at risk.
-   **Long-term correction:** single-writer or partitioned ownership, or
    a domain-specific merge with proven invariants.
-   **Regression test:** concurrent update test during a simulated
    partition.

### Story 3 --- West's default quota prevents scale-up

-   **False assumption:** autoscaling configuration guarantees capacity.
-   **Evidence:** quota errors, pending replicas, saturation, rising
    latency.
-   **Immediate safe action:** cap/shed non-critical traffic and
    preserve the core path.
-   **Long-term correction:** quota preflight, reserved capacity where
    justified, N+1 test.
-   **Regression test:** simulate blocked scale-up and verify brownout
    behavior.

### Story 4 --- One global GitOps change breaks both regions

-   **False assumption:** a single desired-state commit is automatically
    safe.
-   **Evidence:** same revision rollout precedes both regional failures.
-   **Immediate safe action:** halt fan-out and roll back the known-good
    revision through approved controls.
-   **Long-term correction:** canary/ring deployment, policy validation,
    region-by-region gates.
-   **Regression test:** a failing canary prevents promotion to the next
    ring.

### Story 5 --- Replication lag causes a surprise RPO breach

-   **Scenario fact:** in this fictional exercise, lag reached 25
    minutes before the team discovered it. This is not a general
    statistic.
-   **False assumption:** replica availability means recent data is
    present.
-   **Evidence:** lag history, applied position, write timestamps, alert
    gap.
-   **Immediate safe action:** do not promote blindly; quantify
    potential data loss and follow M13/Unit 7 procedures.
-   **Long-term correction:** lag SLO/alert, promotion gate, owner and
    escalation.
-   **Regression test:** inject deterministic lag and assert the gate
    blocks unsafe promotion.

### Story 6 --- Secrets replica is stale after rotation

-   **False assumption:** regional secret references are equivalent
    because the application manifest is identical.
-   **Evidence:** version metadata differs; auth fails in standby.
-   **Immediate safe action:** keep region out of service until approved
    credentials/trust are valid.
-   **Long-term correction:** parity checks that reveal version presence
    without exposing values; rotation rehearsals.
-   **Regression test:** stale-version mismatch prevents readiness.

### Story 7 --- Tenant map is a hidden global dependency

-   **False assumption:** tenant routing is stateless and can always be
    reconstructed.
-   **Evidence:** route failures coincide with loss of the only map
    endpoint.
-   **Immediate safe action:** use a validated cached version only
    within its safety contract; otherwise return explicit unavailable
    rather than arbitrary routing.
-   **Long-term correction:** replicated, versioned map, cache expiry
    semantics, ownership.
-   **Regression test:** stop map authority and test stale/unknown
    tenant behavior.

### Story 8 --- Network partition allows both sides to accept writes

-   **False assumption:** eventual merge will preserve every business
    invariant.
-   **Evidence:** concurrent versions, conflicting events, uniqueness or
    balance violation.
-   **Immediate safe action:** contain writes under the approved
    ownership/fencing policy and preserve event history.
-   **Long-term correction:** partitioned ownership or formally
    specified conflict handling.
-   **Regression test:** partition/heal exercise with explicit invariant
    assertions.

------------------------------------------------------------------------

# L4 --- Production readiness and expert judgment

## 14. Mandatory lab safety contract

All labs are local simulations. Before any mutation: - Inventory
clusters and contexts; print the current context. - Verify both cluster
names and map contexts explicitly. - Use `kubectl --context ...` on
every Kubernetes command. - Use a dedicated lab namespace and explicit
resource names. - Save baseline config and evidence before fault
injection. - Do not use production credentials, customer data, public
DNS, or paid cloud resources. - Abort if target identity is ambiguous, a
listener is unexpectedly public, writes could reach a real database, or
faults escape the lab. - Never log secret values. - Restore state and
verify cleanup.

Two `kind` clusters on one host do not create independent regions. On a
resource-constrained laptop, run one lab profile at a time: Fleet-Core
for cluster/context and application tests; Fleet+GitOps only for GitOps
labs; Fleet+Data only for the database/object-store simulation. Stop
heavy components between labs and record actual memory/CPU use.

### Preflight inventory

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

Verify actual context names from output; do not assume the mapping.
Examples below use `kind-stage2e-east-lab` and `kind-stage2e-west-lab`
only if those are the verified contexts.

``` bash
kubectl --context kind-stage2e-east-lab get nodes
kubectl --context kind-stage2e-west-lab get nodes
kubectl --context kind-stage2e-east-lab get namespaces
kubectl --context kind-stage2e-west-lab get namespaces
```

If the names do not match, stop and substitute the verified lab contexts
only after confirming their cluster identities.

### Lab guard helper

``` bash
#!/usr/bin/env bash
set -euo pipefail
require_context() {
  local expected="$1" actual
  actual="$(kubectl config current-context)"
  [[ "$actual" == "$expected" ]] || {
    echo "ABORT: expected context $expected; current is $actual" >&2
    return 20
  }
}
require_lab_name() {
  case "$1" in
    stage2e-east-lab|stage2e-west-lab) ;;
    *) echo "ABORT: cluster name is not an approved lab name: $1" >&2; return 21 ;;
  esac
}
```

This is a mistake-prevention helper, not a security boundary. Prefer
explicit `--context` flags rather than changing the current context.

## 15. Lab 1 --- Active-active stateless inference API

**Objective:** deploy the same stateless API to both local clusters,
prove region identity and artifact parity, and detect a planted
cross-region dependency.\
**Prerequisites/resources:** verified lab clusters, Docker, `kubectl`,
`curl`, Git; Fleet-Core profile.\
**Diagram:** client → East or West API → local dependency stub →
response with serving-region identity.\
**Files to create:** learner-owned `app/`, `deploy/`, `checks/`,
`evidence/`; do not write to or claim to modify the repository.

**Procedure** 1. Record cluster/context versions and save preflight
output. 2. Build one small HTTP API that returns `region`,
`image_digest`, `config_revision`, and request ID. Use a fixed
digest/tag strategy and record the resulting immutable digest. 3. Deploy
the same artifact into a dedicated lab namespace in each cluster using
explicit contexts. Keep region-specific config limited to region
identity and local dependency endpoint. 4. Add local dependency stubs
for feature store/cache/artifact lookup. Where a real component is too
heavy, document the stub and its fidelity limit. 5. Send requests
directly to each endpoint; record identity and digest. 6. Add a
dependency destination allowlist: West requests should use West-local
dependency endpoints. Plant a West configuration pointing at an
East-only dependency. 7. Run the detector and assert the negative case
fails. Restore the West-local endpoint and assert it passes. 8. Simulate
an East endpoint failure and verify West remains functional only for the
paths whose dependencies are local. 9. Save logs, configs, digest, test
results, and cleanup evidence.

**Expected observations `[ILLUSTRATIVE]`:** both endpoints report the
same image digest; region labels differ; planted cross-region dependency
causes a failed test. These are expected results, not claimed execution.

**Positive tests:** both APIs respond; digests match; local dependency
checks pass.\
**Negative tests:** wrong digest or cross-region endpoint fails
parity/route check.\
**Success criteria:** evidence proves artifact identity, serving region,
and detector behavior.\
**Common failures:** assuming different clusters mean different regions;
mutable image tags; hidden default endpoint.\
**Abort/rollback:** stop if contexts are unclear or any non-lab endpoint
appears; restore saved configs and remove only exact lab resources.\
**Cleanup:** delete only the lab namespace after inspecting its
contents.\
**Evidence:** preflight, digest, response samples, dependency map,
detector output, request logs, cleanup verification.\
**Does not prove:** geographic routing, independent failure domains, WAN
behavior, or production inference capacity.

## 16. Lab 2 --- N+1 capacity evacuation test

**Objective:** measure local SLO impact when one region's traffic is
evacuated and verify the calculator catches overload.\
**Prerequisites/resources:** Lab 1, bounded load generator,
`capacity_model.py`; Fleet-Core profile.\
**Diagram:** fixed request generator → East/West APIs → metrics
collection; a controlled traffic switch directs all requests to the
survivor.

**Procedure** 1. Run `python3 capacity_model.py`; record interpreter
version and test output. 2. Review the assumptions and alter synthetic
demand/capacity values only with an explicit note. 3. Generate a low,
bounded baseline request rate across both APIs. Record request rate,
errors, latency, and resource use. 4. Evacuate one endpoint using the
local Unit 5 switching mechanism or a client-side distribution switch.
Do not claim a global load balancer was tested. 5. Measure survivor
latency/errors and resource use during the switch. 6. Simulate a
capacity cap or controlled delay; verify load shedding or brownout
behavior. 7. Restore the distribution gradually and observe
cache/connection surge. 8. Stop load generation, verify request rate
returns to zero, and save evidence.

**Tests:** calculator rejects invalid inputs; overload case is flagged;
service gate halts shift or sheds load when the target is over
capacity.\
**Success criteria:** raw measurements are labelled
`[LOCAL LAB MEASUREMENT]`; assumptions are separate from measured
values; no unsupported production conclusion is made.\
**Expected output:** the sample calculator reports overload for 1,000
req/s total and 700 req/s per region after one region loss. This is
synthetic arithmetic.\
**Abort:** host instability, unexpected network exposure, or load
escaping the lab.\
**Cleanup:** stop the exact generator process and restore traffic
distribution.\
**Evidence:** script/tests, request CSV, latency/error samples,
start/end timestamps, CPU/memory, cleanup record.\
**Does not prove:** real regional capacity, WAN latency, cloud quotas,
or production safe throughput.

## 17. Lab 3 --- Read-local/write-primary with PostgreSQL primary and replica

**Objective:** demonstrate local reads, forwarding to one write
authority, replication lag/stale reads, and write rejection when
authority is unknown.\
**Prerequisites/resources:** PostgreSQL container(s) only if laptop
resources allow; otherwise deterministic simulation; `psql` if
installed. Fleet+Data profile.\
**Diagram:** East API → East PostgreSQL primary; West API → West read
replica for reads and forwards writes to East.

**Safety:** never use production credentials or database endpoints. Do
not run real promotion in this lab. Promotion/fencing mechanics remain
M13/Unit 7 territory.

**Procedure** 1. Choose either an isolated PostgreSQL primary/replica
lab with a version pinned by the learner, or a deterministic in-memory
simulation. Mark which was used. 2. If PostgreSQL is selected, verify
the installed version and official docs for replication setup, lag
monitoring, and replay-position behavior `[VERIFY]` before commands are
executed. 3. Create synthetic records and record the initial version in
both regions. 4. Route reads to the local replica and writes only
through the East primary API. 5. Add a controlled delay in the
simulation or a documented safe lab lag method; observe a stale West
read. 6. Demonstrate one read-your-writes option: bounded session
pinning to primary, or a version/LSN wait after verifying
version-specific semantics. 7. Send a write while the primary authority
marker is false/unconfirmed; it must be rejected and must not mutate
data. 8. Simulate primary commit with response timeout and retry the
same idempotency key; verify the test implementation does not duplicate
the effect. 9. Reset all synthetic state and verify the write gate is
disabled.

**Positive tests:** normal write reaches primary; local read reports
version; replica eventually catches up in the chosen simulation.\
**Negative tests:** unapproved primary rejects write; stale read is
identified; duplicate attempt is handled by the idempotency contract.\
**Success criteria:** authority state and observed versions are
recorded; all PostgreSQL-specific unverified behavior remains marked
`[VERIFY]`.\
**Common failures:** assuming replica health means zero lag; assuming a
timeout means the write failed; retrying with a new idempotency key.\
**Abort/rollback:** abort if any real database endpoint/credential
appears or if authority is ambiguous; restore the synthetic baseline.\
**Evidence:** versions, replication/lag observations or simulation
inputs, write/read log, idempotency test, gate state.\
**Does not prove:** production database durability, exact PostgreSQL
behavior until version docs are verified, or safe real promotion.

## 18. Lab 4 --- Tenant home-region routing and cell isolation

**Objective:** implement a simple tenant-to-region map and test
unknown/stale mappings, migration state, and logical isolation.\
**Prerequisites/resources:** Python 3; two local API stubs; Fleet-Core.\
**Diagram:** request with tenant key → versioned router map → East or
West cell.

**Procedure** 1. Create a small router with a versioned mapping such as
`tenant-a -> east`, `tenant-b -> west`. 2. Implement explicit outcomes
for unknown tenant, unavailable home region, stale map version, and
migration-in-progress. 3. Route normal requests and record
destination/decision reason. 4. Start a tenant migration state machine:
`PRECHECK -> COPYING -> VALIDATING -> ROUTE_SWITCHED -> OBSERVING -> COMPLETE`;
rollback on validation or SLO failure. 5. Simulate checksum/version
mismatch; routing must not switch. 6. Stop or block West's cell and
verify East-owned tenant requests continue while West-owned tenants
receive the documented safe response. 7. Simulate the routing-map
authority being unavailable and test the stale-map policy. 8. Restore
all services and reset mapping.

**Positive tests:** known tenants route correctly; migration requires
validation; East-owned traffic continues during West cell failure.\
**Negative tests:** unknown/stale mapping does not route arbitrarily;
checksum mismatch blocks switch.\
**Success criteria:** transition logs, map version, request identity,
and rollback path are captured.\
**Common failures:** global map exists only in one region; migration
updates routing before data validation; tenant labels leak into
high-cardinality metrics.\
**Abort/rollback:** revert to the saved map version and do not delete
source state.\
**Cleanup:** stop stubs and remove exact lab resources.\
**Evidence:** test output, map revisions, migration timeline, isolation
results.\
**Does not prove:** production data migration safety or physical region
isolation.

## 19. Lab 5 --- Active-passive database promotion by reference

**Objective:** verify the application write gate remains closed until
the authorized primary and fencing state are confirmed.\
**Prerequisites/resources:** Lab 3 synthetic state machine; M13 Unit 6
procedure as a reference, not repeated.\
**Diagram:** read path may reach replica; write path passes through
explicit authority gate.

**Procedure** 1. Initialize `WRITES_DISABLED` and mark the secondary
`UNPROMOTED`. 2. Send a read request; accept it only if the selected
read policy permits. 3. Send a write; assert rejection and no state
mutation. 4. Change the traffic endpoint/weight only; repeat write and
assert it is still rejected. 5. Simulate the approved promotion/fencing
evidence as a synthetic test fixture, not a real database operation. 6.
Enable writes only after both authority and fencing gates are true. 7.
Set authority to unknown and assert the gate returns to
`WRITES_DISABLED`. 8. Reset state.

**Success criteria:** routing changes never alter write authority;
negative tests fail closed.\
**Abort:** any real database endpoint or credentials appear.\
**Evidence:** state transitions, request IDs, before/after synthetic
state, test output.\
**Does not prove:** real promotion, fencing, or split-brain prevention.
Use M13/Unit 7 for the real mechanisms.

## 20. Lab 6 --- Routine region evacuation and fail-back

**Objective:** evacuate West intentionally, observe regional
serving/capacity, then reintroduce it gradually with SLO gates.\
**Prerequisites/resources:** Unit 5 local traffic switch and Lab 1/2;
Fleet-Core.\
**Diagram:** client distribution → regional endpoints; traffic switch
changes West weight to zero and then ramps it back.

**Procedure** 1. Save baseline weights and request distribution. 2.
Verify both endpoints, certificates/trust in the local setup, local
dependencies, and survivor capacity. 3. Set West's traffic share to zero
using the already verified lab mechanism. 4. Verify requests are served
by East, collect error/latency/capacity evidence, and check
background/queued work. 5. Keep the evacuation for a defined observation
window. 6. Reintroduce West with small increments (for example 5%, 20%,
50%, 100%; illustrative only), with a bake interval and gates at each
step. 7. Inject a synthetic error or saturation gate failure; halt and
restore the last known safe distribution. 8. Restore baseline only after
confirming readiness and stable SLOs.

**Positive tests:** traffic drains; no request unexpectedly reaches the
evacuated endpoint; fail-back gates pass.\
**Negative tests:** readiness false or SLO breach blocks ramp-up.\
**Success criteria:** traffic, error, latency, capacity, and transition
timestamps are retained.\
**Common failures:** instant fail-back, cold cache surge, missing
dependency, assuming weights equal exact request percentages.\
**Abort:** host instability, public exposure, unexpected cross-region
route.\
**Cleanup:** restore weights and stop load generators.\
**Does not prove:** real DNS/GTM behavior or geographic failover.

## 21. Lab 7 --- Warm-standby parity and readiness

**Objective:** prove that a standby with missing required
artifacts/configuration is not marked ready.\
**Prerequisites/resources:** manifests/config metadata from Lab 1;
Fleet-Core.\
**Diagram:** parity checker compares desired revision and required
regional artifacts before readiness is true.

**Procedure** 1. Create a parity manifest listing image digest, config
revision, certificate presence/expiry metadata, required secret
references/version metadata, model artifact digest, dependency endpoint,
and replication status. 2. Never include secret values. 3. Run the
checker with matching synthetic inputs. 4. Remove a required
certificate-presence flag or change a model digest in West. 5. Assert
West is not ready for traffic. 6. Restore parity and re-run. 7. Simulate
stale replication status and assert the write-ready gate remains closed.

**Success criteria:** mismatch is detected with actionable field names
and no secret values.\
**Abort/rollback:** restore the baseline manifest; do not alter real
certificates/secrets.\
**Evidence:** before/after manifest, checker output, parity status,
cleanup.\
**Does not prove:** real certificate renewal, secret replication, or
actual database health.

## 22. Lab 8 --- Regional dependency and cross-region-call failure

**Objective:** demonstrate that a hidden cross-region dependency can
make a nominally healthy region fail.\
**Prerequisites/resources:** Lab 1 API/dependency stubs; Fleet-Core.\
**Diagram:** West API → (incorrectly) East dependency; isolate East
dependency and observe West journey failure.

**Procedure** 1. Verify both local request paths work. 2. Plant a West
config pointing to an East-only dependency. 3. Confirm the
cross-region-call detector reports the violation. 4. Block the East
dependency in the lab only. 5. Measure West request errors and compare
with the original local-dependency baseline. 6. Repair by restoring
West-local dependency, explicit partitioning, or documenting the
accepted trade-off and its fallback. 7. Repeat the failure and prove
West's path behaves as documented. 8. Restore baseline and clear network
rules/faults.

**Success criteria:** hidden dependency is identified and the regression
test catches it.\
**Abort:** any rule would affect non-lab traffic.\
**Evidence:** config diff, detector output, request logs, before/after
latency/errors.\
**Does not prove:** real WAN partition behavior or independent regional
failure domains.

## 23. Lab 9 --- Replication lag, stale reads, and RPO alerting

**Objective:** show lag is a data-safety signal and an
availability/consistency trade-off, not just a dashboard number.\
**Prerequisites/resources:** Lab 3 or deterministic lag simulator;
Fleet+Data only if resources permit.\
**Diagram:** primary writes → replication queue/delay → replica applied
version; alert/gate consumes lag signal.

**Procedure** 1. Choose a synthetic lag simulator or version-verified
PostgreSQL replica. 2. Generate numbered writes and track
primary-committed versus replica-applied versions. 3. Inject a
deterministic lag interval or hold back application of events. 4. Alert
when lag exceeds a clearly labelled synthetic threshold. 5. Attempt the
simulated promotion gate; it must not claim RPO compliance when lag
evidence is beyond the declared limit or unknown. 6. Record potential
data-loss window from actual synthetic timestamps/versions. 7. Clear lag
and verify alert recovery only after fresh evidence. 8. Follow M13/Unit
7 for the real promotion and restore workflow; do not promote a real
database here.

**Positive tests:** lag alert fires; version gap is measurable; gate
reflects unknown/stale evidence.\
**Negative tests:** healthy process with stale replication must not be
reported as fully ready.\
**Success criteria:** all lag numbers are labelled `[SYNTHETIC]` or
`[LOCAL LAB MEASUREMENT]`; no production RPO claim.\
**Abort:** any real promotion is about to occur.\
**Evidence:** lag time series, version IDs, alert transition, gate
decision, incident notes.\
**Does not prove:** production replication lag or data-loss guarantees.

## 24. Lab 10 --- ADR and cost review

**Objective:** compare active-active, active-passive/warm standby, and a
hybrid component-level design for the sample data/ML platform.\
**Prerequisites/resources:** previous lab evidence or explicitly
labelled assumptions; Git or a text editor.\
**Diagram:** business requirements → component decision matrix →
options/trade-offs → chosen design and revisit triggers.

**Procedure** 1. Write the business requirements: availability, RTO/RPO
references, latency, data residency, workload mix, and team/on-call
capability. 2. Score the three options against those requirements using
a transparent qualitative scale (e.g., low/medium/high complexity/cost);
do not invent prices. 3. Include per-component choices for inference
API, PostgreSQL, feature store, object storage/model artifacts,
ETL/streaming, identity/secrets, telemetry, and GitOps. 4. Record
capacity evidence and gaps; distinguish calculator output from load-test
measurements. 5. Document rejected options and why. 6. Include
migration/rollback path, owner, approval, validation evidence, and
revisit triggers. 7. Peer-review for hidden cross-region dependencies,
write authority, residency, and management-plane SPOFs. 8. Save the ADR
and a list of open verification items.

**Success criteria:** assumptions are explicit; trade-offs and evidence
gaps are honest; no made-up cloud prices.\
**Abort:** if a cost or guarantee cannot be supported, mark it unknown
rather than inventing it.\
**Evidence:** completed ADR, decision matrix, capacity calculation, open
risks, reviewer notes.\
**Does not prove:** production economics or architecture correctness
without real workload evidence.

------------------------------------------------------------------------

## 25. Observability, SLOs, readiness, and evidence

### SLO model

Use both regional and global views. The global SLO answers whether the
service as a whole meets its objective; per-region SLOs expose regional
brownouts hidden by traffic volume or aggregation.

Minimum dimensions: - requests and errors by region/service; - latency
distribution by region; - saturation and safe capacity/headroom; -
cross-region dependency call count/latency; - replication lag/freshness
where applicable; - parity/readiness mismatch count; - traffic
evacuation/fail-back timestamps and weights; - write rejection while
primary authority is absent; - tenant routing/migration state; - config
revision and image digest; - management-plane availability versus
data-plane health.

Avoid uncontrolled high-cardinality labels. A raw tenant ID as a metric
label can create unbounded time series; use bounded tenant classes or
sampled logs/traces with access controls for tenant-level investigation.

### Evidence collection table

  ------------------------------------------------------------------------------------------
  Evidence              How to collect        Conclusion        Does not support
                                              supported         
  --------------------- --------------------- ----------------- ----------------------------
  Per-region request    Request harness and   Behavior of this  Real-world demand or WAN
  rate/errors/latency   region identity       lab workload      latency

  Cross-region calls    Trace/log destination Known dependency  Complete proof that no
                        or allowlist detector path is detected  hidden path exists without
                                                                instrumentation coverage

  Image digest parity   Inspect deployed      Same artifact     Same
                        image digest          identity in both  configuration/dependencies
                                              clusters          or runtime behavior

  Replication lag       Database telemetry or Observed lag for  Production RPO guarantee
                        deterministic         that environment  
                        simulator                               

  Capacity after        Bounded load test,    Local behavior at Production safe throughput
  evacuation            resource/saturation   tested workload   
                        data                                    

  Readiness mismatch    Parity checker and    Checker blocks    Every possible mismatch is
                        test fixture          the tested        covered
                                              mismatch          

  Tenant migration      Map version,          The scripted      Safe production data
                        checksums, state      test's migration  movement
                        transitions           control flow      

  Write safety          Negative test before  Application gate  Real fencing correctness
                        authority/fencing     fails closed in   
                                              test              

  GitOps drift          Desired/live diff and Specific drift is Control-plane independence
                        revision              visible           

  Cleanup               Resource/process      Named lab         No unobserved host residue
                        inventory after lab   resources were    unless explicitly checked
                                              cleaned           
  ------------------------------------------------------------------------------------------

### Evidence bundle

``` text
evidence/
  inventory.txt
  versions.txt
  context-map.txt
  topology.md
  capacity-model-output.txt
  lab-01/
    responses.csv
    image-digests.txt
    dependency-check.txt
  lab-02/
    request-samples.csv
    latency-errors.csv
    assumptions.md
  lab-03/
    read-write-timeline.csv
    lag-observations.csv
    authority-gate-tests.txt
  lab-04/
    tenant-map-before-after.json
    migration-timeline.csv
  lab-05/
    write-gate-transitions.csv
  lab-06/
    evacuation-timeline.csv
    failback-gates.md
  lab-07/
    parity-report.txt
  lab-08/
    dependency-fault-timeline.csv
  lab-09/
    lag-alert-timeline.csv
  lab-10/
    architecture-decision-record.md
  cleanup-verification.txt
```

Keep secrets out of evidence. Record UTC timestamps, versions, context
names, configuration revision, assumptions, expected/observed result,
failures, and cleanup status. Do not fabricate metrics or fill an
"observed" column with expected output.

## 26. Operating model and management-plane boundaries

Assign named ownership for: - regional health and traffic shifting; -
data authority, replication, promotion/fencing; - tenant/home-region
map; - secrets and identity; - model artifacts and registry mirrors; -
GitOps rollout and configuration parity; - observability and incident
command; - customer communications and post-incident actions.

A central management plane can be useful, but the team must know what
happens when GitOps, central observability, identity, or routing control
is unavailable. Existing workloads may continue running while changes
are blocked; do not assume that behavior without testing the actual
components. Local observability and emergency access should be available
through an approved path.

Global config changes need bounded blast radius. Reference Unit 3 for
ring/wave rollout mechanics. A shared desired-state commit is not
automatically safe merely because it is declarative.

## 27. Three operational runbooks

These are educational templates for design review and lab use, not
instructions to execute unreviewed in production.

### Runbook A --- Unplanned region evacuation

1.  Declare incident, appoint incident commander, and record affected
    service/regions.
2.  Freeze risky unrelated changes and preserve current routing/config
    evidence.
3.  Verify whether the failure is regional, shared-dependency,
    control-plane, or a gray failure.
4.  Verify candidate region readiness: local dependencies, TLS,
    artifacts, capacity, quotas, telemetry, and data authority.
5.  If critical signals are stale or contradictory, freeze automation
    and escalate rather than choosing a destination blindly.
6.  Confirm write authority/fencing before any write traffic is enabled.
7.  Shift only through the approved Unit 5 mechanism; use stages where
    possible.
8.  Monitor per-region/global SLOs, capacity, queue age, errors,
    latency, and cross-region calls.
9.  Communicate timestamped status and decisions.
10. Preserve request samples, routing revisions, alerts, and
    data-authority evidence.
11. Do not fail back until readiness and data-state gates pass.

**Abort:** target identity uncertain, TLS invalid, capacity unproven,
control plane suspected compromised, or write authority unknown.

### Runbook B --- Replication lag / potential RPO breach

1.  Identify affected dataset, primary, replica, and last known healthy
    replication state.
2.  Confirm the monitoring signal is fresh and determine whether the lag
    is time-based, byte/position-based, or application-level.
3.  Preserve primary/replica positions, write timestamps, alerts, and
    incident timeline.
4.  Do not promote blindly; block unsafe writes or promotion according
    to the approved data-safety policy.
5.  Quantify the potential data-loss window from available evidence and
    state uncertainty explicitly.
6.  Escalate to the data owner and incident commander; communicate
    impact and decisions.
7.  Follow M13/Unit 7 recovery, promotion, and restore procedures.
8.  After recovery, validate data integrity and replay/reconciliation
    before restoring normal writes.
9.  Add a regression test, alert threshold review, and post-incident
    action.

**Abort:** replication state is unknown and the action would risk
split-brain or unbounded data loss.

### Runbook C --- Planned evacuation and fail-back

1.  Confirm change window, owner, target, customer impact, and rollback.
2.  Validate parity/readiness, TLS, local dependencies, artifact
    digests, quotas, replication/data authority, and capacity.
3.  Save baseline routing/config and define per-stage SLO gates.
4.  Drain or shift traffic away from the region using the approved
    mechanism.
5.  Observe requests, queues, background jobs, and duplicate processing;
    retain evidence.
6.  Restore the region and verify readiness before receiving traffic.
7.  Reintroduce gradually with bake intervals; stop at the first failed
    gate.
8.  Confirm global and per-region SLOs, data state, queue processing,
    and route convergence.
9.  Update the ADR/runbook if evidence changed the design assumptions.

**Abort:** parity mismatch, stale critical signals, capacity gate
failure, unexpected writes, or SLO breach.

## 28. Production-readiness review and expert judgment

A design review should ask:

### Architecture

-   Is "active" defined per component and per operation
    (read/write/serve)?
-   Are synchronous request dependencies regional?
-   Is there a single-writer or partition ownership contract?
-   What is the failure behavior for asymmetric network partitions?
-   Is the routing map itself resilient and versioned?
-   Are cells actually isolated or do they share critical dependencies?

### Data and correctness

-   Which stale reads/anomalies are acceptable?
-   How are idempotency, duplicate events, and unknown write outcomes
    handled?
-   Can both sides write during partition? If so, what invariant is
    preserved?
-   Is the merge/conflict strategy tested with adversarial concurrent
    updates?
-   Is promotion blocked until authority and fencing are verified?

### Capacity and operations

-   Can one region absorb the expected traffic at the latency/error SLO?
-   Is safe capacity measured with representative dependencies, cold
    caches, and model loads?
-   What happens during autoscaling delay and quota exhaustion?
-   Are load shedding and brownout behaviors understood by product
    owners?
-   Is fail-back gradual and observable?

### Security/compliance

-   Are replicas, backups, telemetry, model artifacts, and support
    access covered by residency requirements?
-   Are secret rotations and identity dependencies tested in standby?
-   Are logs/evidence free of secret values and excessive tenant
    identifiers?

### Management plane and governance

-   What keeps serving if GitOps/observability/routing hub is down?
-   Can a bad config reach both regions at once?
-   Are rollout rings and rollback gates tested?
-   Who owns each decision during an incident?

### Evidence and revisit triggers

Revisit the ADR when load grows, a new region/compliance boundary is
added, SLOs repeatedly miss, costs change materially, replication lag
trends worsen, on-call capability changes, or RTO/RPO requirements
change. A design decision without revisit triggers tends to persist
after its assumptions stop being true.

## 29. What the local lab demonstrates---and cannot demonstrate

  -----------------------------------------------------------------------
  Local lab can demonstrate           Local lab cannot demonstrate
  ----------------------------------- -----------------------------------
  Explicit context discipline and     Physical region independence
  guarded operations                  

  Two API deployments with matching   Geographic routing or provider
  image digests                       global-load-balancer behavior

  Region identity in response/logs    Real WAN latency or routing
                                      convergence

  A planted cross-region dependency   Proof that every hidden dependency
  can be detected                     is instrumented

  A synthetic capacity calculator     Production sustainable throughput
  catches arithmetic overload         or cloud quota behavior

  Controlled stale-read/lag           Production PostgreSQL replication,
  simulation and write gate logic     durability, or exact RPO

  Tenant routing state machine and    Real regional isolation or safe
  logical cell isolation              production data migration

  Parity checker catches the          Complete readiness coverage without
  mismatches tested                   a comprehensive inventory

  Local evacuation/fail-back sequence Real Internet resolver convergence
  and evidence capture                or global traffic failover

  A fictional incident/tabletop       Competence under real incident
  exposes assumptions                 pressure

  ADR structure and explicit          Real cloud cost or an architecture
  trade-offs                          proven correct at scale
  -----------------------------------------------------------------------

Do not convert a local lab pass into a production-readiness claim.
Production readiness requires target-environment verification,
independent vantage points, security and compliance review, realistic
capacity tests, tested data-safety procedures, and operational
rehearsal.

## 30. Knowledge checks and answer key

Score each question one point unless a question explicitly asks for
multiple items. For design prompts, award the point only when the
reasoning identifies both the trade-off and the evidence needed.

### Foundations

**1. Multiple choice:** Which statement is most accurate?\
A. Active-active means every component writes in every region.\
B. Active-active is a component/workload-level serving pattern; data
write ownership can remain single-writer.\
C. Active-passive has no running standby resources.\
D. A hot standby is automatically safe for writes.\
**Answer:** B. Serving activity and data write authority are separate
decisions.

**2. Short answer:** Distinguish cold standby, pilot light, warm
standby, and hot standby.\
**Answer:** They represent increasing amounts of pre-existing
infrastructure/readiness, generally reducing activation work while
increasing steady-state cost; terminology varies and the actual
readiness/capacity must be measured.

**3. Short answer:** What is follow-the-sun, and what must be handed
over?\
**Answer:** Scheduled change of serving/processing ownership; hand over
workload ownership, queues/checkpoints, data state, credentials,
routing, and runbook responsibility without allowing two owners to write
concurrently.

**4. Multiple choice:** Which design is usually easiest to make
active-active?\
A. Stateless API with local dependencies.\
B. Arbitrary multi-writer account ledger.\
C. Single global sequence service in one region.\
D. Tenant map available only in East.\
**Answer:** A. It still needs capacity and dependency verification.

**5. Short answer:** Why is "the platform is active-active" an
incomplete statement?\
**Answer:** It does not identify which components serve/write in each
region, data ownership, dependency locality, consistency, capacity, or
failure behavior.

**6. Scenario:** A global SLO is green while West's error rate is 100%.
What should the dashboard include?\
**Answer:** Per-region SLOs, request volume, errors, latency,
saturation, and dependency health alongside the global view; aggregation
can hide a low-volume regional outage.

**7. Short answer:** Define RTO and RPO briefly and state the boundary
here.\
**Answer:** RTO is the target for restoring service; RPO is the
acceptable data-loss window. Refer to M13 Unit 1 for full definitions
and business-objective treatment.

**8. Multiple choice:** What is the main danger of a cross-region
synchronous dependency in a supposedly independent serving region?\
A. It always improves consistency.\
B. It couples availability and latency to the remote region.\
C. It eliminates the need for tracing.\
D. It makes capacity irrelevant.\
**Answer:** B.

### Capacity and workload design

**9. Calculation:** Two regions each receive 500 req/s normally. Total
demand is 1,000 req/s and each region's tested capacity is 700 req/s.
What is survivor utilization after one region is evacuated?\
**Answer:** `1,000 / 700 ≈ 142.9%`; the survivor is overloaded.

**10. Short answer:** Why does 50% utilization in both regions not prove
N+1 capacity?\
**Answer:** Per-region sustainable capacity, traffic mix, dependency
limits, autoscaling delay, quotas, cache state, and post-failure demand
must be tested; utilization alone is insufficient.

**11. Scenario:** West has healthy pods but lacks the current model
artifact and TLS certificate. Is it ready?\
**Answer:** No. Required artifacts and valid TLS are readiness gates,
not optional advisory scores.

**12. Short answer:** Name three ways to handle overload after regional
evacuation.\
**Answer:** Pre-provision capacity, scale with tested headroom, load
shed/degrade non-critical work, apply admission control/rate limits, or
bounded queueing. State the trade-offs.

**13. Scenario:** Autoscaling is configured but a regional quota blocks
new replicas. What evidence and prevention are needed?\
**Answer:** Scale events, pending pods, quota errors, and saturation;
perform quota preflight, test N+1 load, and define a bounded
brownout/load-shedding policy.

**14. Short answer:** What does a capacity calculator prove?\
**Answer:** It validates arithmetic under explicit assumptions. It does
not prove sustainable throughput; that requires a representative load
test.

### Data consistency and failure behavior

**15. Scenario:** An inference API is active-active, but both regions
call one feature store in East. What happens when East fails?\
**Answer:** West can remain process-healthy but its user journey may
fail or degrade. Trace the dependency and localize, partition, or
explicitly accept the dependency with a tested fallback.

**16. Scenario:** A write succeeds in the primary, but the client times
out. What is the retry risk?\
**Answer:** The client cannot infer failure from timeout; retrying may
duplicate the effect. Use a correctly implemented idempotency contract
and bounded retries.

**17. Scenario:** A local replica returns an old value immediately after
a successful write. Which guarantee may be missing?\
**Answer:** Read-your-writes/strongly consistent read behavior. Consider
session pinning or a verified version/replication-position wait, with
timeout and fallback.

**18. Explain the anomaly:** East changes a value to 70; West
concurrently changes it to 80; naïve LWW keeps 80.\
**Answer:** East's update may be lost even though it represented a valid
operation. LWW is not a substitute for business conflict semantics.

**19. Multiple choice:** What should happen if write authority is
unknown?\
A. Send writes to the healthiest endpoint.\
B. Enable both writers.\
C. Block writes or use the explicitly approved safe mode until
authority/fencing is resolved.\
D. Disable TLS checks.\
**Answer:** C.

**20. Short answer:** Why is eventual visibility not the same as
durability or linearizability?\
**Answer:** Eventual visibility describes replicas converging later;
durability concerns committed data survival, while linearizability
constrains operations to appear in a single real-time-consistent order.

**21. Scenario:** Both regions accepted writes during a partition. Why
may "merge by latest timestamp" be unsafe?\
**Answer:** It may discard valid operations, depend on
clock/tie-breaking behavior, or violate cross-field/business invariants.
Preserve history and use single-writer/partitioned ownership or a
formally specified merge.

**22. Short answer:** What is the benefit and risk of tenant home-region
routing?\
**Answer:** It improves locality and can support residency/ownership;
the map and migration process become critical dependencies and must
handle stale/unknown state safely.

**23. Scenario:** A tenant home-region map exists only in East. What has
become globally critical?\
**Answer:** The routing map/service. Replicate/version it or define a
safe cached/unavailable behavior and test map-authority failure.

### Operations and governance

**24. Short answer:** Why should fail-back be gradual?\
**Answer:** The recovered region may have cold caches, incomplete
parity, insufficient capacity, or dependency/data issues. Ramp with bake
periods and stop gates.

**25. Scenario:** A global GitOps change breaks both regions within
minutes. What failed in the operating model?\
**Answer:** Change blast radius was unbounded. Add validation,
canary/rings, per-region gates, rollback, and evidence before promotion.

**26. Short answer:** How should a warm standby be continuously tested?\
**Answer:** Parity/readiness checks for config, image digest, artifacts,
certificates/secret references, dependencies, replication health,
quotas/capacity, and end-to-end user journey; run routine evacuation
exercises.

**27. Scenario:** The central observability hub fails. What should the
team know?\
**Answer:** Whether regional telemetry is buffered/available locally,
what data-plane functions continue, how to access evidence via an
approved path, and which global views become unavailable.

**28. Design prompt:** Compare active-active, warm standby, and a hybrid
per-component design for a data/ML platform.\
**Answer:** There is no universal answer. A defensible hybrid may use
active-active stateless inference, single-writer PostgreSQL with a
regional replica, replicated model artifacts, region-pinned ETL, and a
warm standby for lower-criticality components. State assumptions,
capacity, data consistency, residency, cost, and evidence gaps.

**29. Incident diagnosis:** Replication lag exceeds the declared RPO
tolerance, but the replica health endpoint is green. What should
happen?\
**Answer:** The health endpoint is insufficient. Alert on lag/freshness,
preserve evidence, block unsafe promotion as required, quantify
potential loss, and follow M13/Unit 7 procedures.

**30. Expert judgment:** When is a single-region platform with tested DR
preferable to active-active?\
**Answer:** When it meets business SLO/RTO/RPO/residency requirements at
lower operational risk and cost, and the team cannot justify or safely
operate the added complexity of multi-region serving.

**Scoring rubric:** **80% or higher:** proceed to the next unit while
retaining the evidence and open risks; **60--79%:** remediate weak areas
and repeat the corresponding labs; **below 60%:** repeat the unit and
labs. Quiz performance is not proof of production competence.

## 31. Glossary

-   **Active-active:** multiple regions serve production traffic
    concurrently.
-   **Active-passive:** one region serves while another is standby.
-   **ADR:** architecture decision record documenting context, options,
    choice, consequences, evidence, and revisit triggers.
-   **Brownout:** controlled degradation of non-critical functionality
    to preserve core service.
-   **Cell:** bounded unit of workload/tenancy intended to limit blast
    radius.
-   **CRDT:** conflict-free replicated data type with defined merge
    properties for supported operations.
-   **Data residency:** constraints on where specified data may be
    stored/processed/accessed.
-   **Fencing:** mechanism preventing an old or unauthorized writer from
    continuing to mutate state.
-   **Home region:** assigned region responsible for a
    tenant/workload/data partition.
-   **Idempotency key:** identifier used by an operation contract to
    make repeated submissions safe where correctly implemented.
-   **LWW:** last-write-wins conflict policy selecting one update by a
    defined ordering rule.
-   **N+1 capacity:** capacity remains sufficient after losing one
    relevant unit, such as a region, according to the stated design
    target.
-   **RPO:** recovery point objective; acceptable data-loss window.
-   **RTO:** recovery time objective; target restoration time.
-   **SLO:** service-level objective for a measured reliability
    indicator.
-   **Synchronous cross-region dependency:** request waits on a service
    in another region before completing.
-   **Warm standby:** substantially complete but scaled-down standby
    stack requiring some activation/scaling.
-   **Write authority:** the designated permission/state that allows a
    system to accept authoritative writes.

## 32. Verification notes and sources

**Verification status:** live official documentation was not consulted
during this authoring pass. The URLs below are entry points, not a claim
that current versions or exact commands were verified. Do not run
version-sensitive database, Kubernetes, or GitOps commands without
checking the installed version and official documentation.

-   Kubernetes concepts and workloads:
    https://kubernetes.io/docs/concepts/
-   Kubernetes probes:
    https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/
-   kind documentation: https://kind.sigs.k8s.io/
-   PostgreSQL documentation: https://www.postgresql.org/docs/
-   Argo CD documentation (if selected): https://argo-cd.readthedocs.io/
-   Flux documentation (awareness/comparison only):
    https://fluxcd.io/flux/
-   Kubernetes Gateway API: https://gateway-api.sigs.k8s.io/
-   OpenTelemetry documentation: https://opentelemetry.io/docs/

Items to verify before executing implementation-specific steps: 1. Exact
`kind` version and config fields for cluster networking/CIDRs. 2. Actual
cluster names and `kubectl` context mapping. 3. PostgreSQL version,
replication setup, lag metrics, and any LSN/replay-wait behavior. 4.
Exact GitOps controller/version and safe promotion/rollback procedure.
5. Any database/global-product consistency, conflict, residency, and
availability claims. 6. Installed tooling flags, resource footprint, and
listener/network exposure. 7. The actual repository tree and sibling
module contents before merging.

## 33. Final roadmap-alignment and authenticity audit

  --------------------------------------------------------------------------------------------------------
  Requirement                          Status            Evidence sections Notes / follow-up
  ------------------------------------ ----------------- ----------------- -------------------------------
  Exact Unit 6 target filename and M14 **PARTIAL**       Metadata          Target filename matches the
  placement                                                                supplied prompt. The attached
                                                                           file named
                                                                           `Roadmap(20261029-114814).md`
                                                                           was available, but the prompt
                                                                           references `Roadmap_ptree.md`;
                                                                           that exact filename was not
                                                                           independently
                                                                           available/verified in this
                                                                           pass.

  Verbatim M13 handoff included        **PASS**          Relationship to   Paragraph reproduced verbatim
                                                         M13               from the supplied prompt.

  Definitions for all required         **PASS**          L1, Pattern       Includes active-passive
  patterns                                               taxonomy          variants, active-active
                                                                           variants, follow-the-sun,
                                                                           read-local/write-primary, home
                                                                           region, and cells.

  Pattern selection covers business,   **PASS**          Pattern selection RTO/RPO full definitions handed
  RTO/RPO, latency, consistency,                         criteria          off to M13 as required.
  residency, cost, team                                                    

  N+1 capacity, 50% utilization issue, **PASS**          Cost of           Synthetic numbers labelled;
  arithmetic and calculator tests                        active-active;    calculator is not a load test.
                                                         capacity script   

  Data/AI workload mapping             **PASS**          Workload mapping  All listed workload classes
                                                                           included.

  Stateless active-active, GitOps      **PARTIAL**       Active-active     Architecture and detector
  parity, local dependencies, detector                   stateless         contract included; integrated
                                                         serving; Lab 1    app and detector were not built
                                                                           or executed.

  Read-local/write-primary, lag, stale **PASS**          Section 6; Lab 3  PostgreSQL-specific details
  reads, idempotency, write safety                                         remain `[VERIFY]`; no real
                                                                           database test executed.

  Tenant home region, migration,       **PASS**          Section 7; Lab 4  Local state-machine exercise is
  cells, global IDs/residency                                              not production migration
                                                                           assurance.

  Active-passive standby parity and    **PASS**          Section 8; Labs   Implementation and full
  routine evacuation                                     5--7              evacuation not executed.

  Partitioning/multi-writer/LWW/CRDT   **PASS**          Section 10        Product semantics not asserted;
  awareness                                                                verify chosen system.

  Capacity/brownout and failure        **PASS**          Sections 11--12   No production metrics or
  catalog                                                                  benchmarks claimed.

  Eight fictional organizational       **PASS**          Section 13        Scenarios explicitly labelled
  incident stories                                                         fictional.

  Ten mandatory labs with safety,      **PASS**          Sections 15--24   Procedures and expected
  tests, evidence, cleanup/abort                                           observations authored; not
                                                                           executed.

  Observability, SLOs, readiness,      **PASS**          Section 25        Includes measurement limits and
  evidence                                                                 cardinality caution.

  Operating model and three runbooks   **PASS**          Sections 26--27   Educational templates, not
                                                                           production-authorized runbooks.

  Production-readiness review and      **PASS**          Sections 28--29   Clearly distinguishes local
  lab-fidelity table                                                       demonstration from real
                                                                           assurance.

  At least 25 questions and scoring    **PASS**          Section 30        30 questions with concise
  rubric                                                                   reasoning.

  Glossary, verification notes, final  **PASS**          Sections 31--33   Version-sensitive items
  audit                                                                    disclosed.

  Official sources consulted live      **BLOCKED**       Section 32        Live browsing was not
                                                                           performed; source URLs are
                                                                           entry points only.

  Actual sibling tree/content verified **PARTIAL**       Audit             Supplied roadmap was inspected
                                                                           at its opening, but
                                                                           `Roadmap_ptree.md` and sibling
                                                                           files were not independently
                                                                           validated in full.

  End-to-end implementation/test       **BLOCKED**       Labs 15--24       No clusters, database, GitOps
  evidence                                                                 deployment, or failure drills
                                                                           were run.

  No other repository files modified   **PASS**          Task execution    This artifact was created
                                                                           separately; no repository
                                                                           mutation was performed.
  --------------------------------------------------------------------------------------------------------

### Final trust statement

This document is a complete teaching artifact with a traceable
self-audit, not a verified production implementation. The audit is based
on the supplied Unit 6 prompt and the available roadmap excerpt; the
exact `Roadmap_ptree.md` filename and sibling contents remain to be
checked. No official documentation was consulted live, no commands were
executed against clusters, no database replication/promotion was run,
and no measured capacity or failover results are claimed. Verify current
official documentation and installed versions, inspect the real
repository tree, execute the labs with evidence, and obtain a human
technical review before treating any design as production-ready. Two
local `kind` clusters on one laptop do not prove real multi-region
resilience.

**Overall status: PASS for lesson coverage; PARTIAL/BLOCKED for
source-tree verification and implementation readiness.**
