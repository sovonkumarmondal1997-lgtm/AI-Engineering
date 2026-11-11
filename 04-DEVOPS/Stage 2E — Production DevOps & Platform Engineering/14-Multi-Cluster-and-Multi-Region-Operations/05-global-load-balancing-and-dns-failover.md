# Global Load Balancing and DNS Failover

> **Stage:** Stage 2E --- Production DevOps & Platform Engineering\
> **Module:** M14 --- Multi-Cluster and Multi-Region Operations\
> **Unit:** 5 --- Global load balancing and DNS failover\
> **Target:** `05-global-load-balancing-and-dns-failover.md`\
> **Prerequisites:** M14 Units 1--4; Kubernetes networking and health
> checks; GitOps basics; SRE, observability, and DR foundations.\
> **Duration:** 18--30 hours (illustrative).\
> **Environment:** WSL2 Ubuntu or native Linux; Docker, `kind`,
> `kubectl`, Python 3, Git, `curl`, `dig`/`drill`, OpenSSL.\
> **Budget:** Zero cloud spend; approximately 4 CPU cores, 8 GB RAM, 30
> GB free disk.\
> **Review status:** Authoring review only, 2026-10-29. Live
> official-document verification and end-to-end execution were not
> performed. Version-sensitive items are marked `[VERIFY]`.

## Table of contents

-   [1. Purpose, Scope, and Learning
    Outcomes](#1-purpose-scope-and-learning-outcomes)
-   [2. Mental Model: DNS, Traffic Steering, and Regional
    Entry](#2-mental-model-dns-traffic-steering-and-regional-entry)
-   [3. Level 1 --- Foundations and Global Traffic
    Architecture](#3-level-1--foundations-and-global-traffic-architecture)
-   [4. Level 2 --- Build a Local Global-Traffic
    Simulation](#4-level-2--build-a-local-global-traffic-simulation)
-   [5. Level 3 --- Failover Timing, Health Policy, and Routing
    Safety](#5-level-3--failover-timing-health-policy-and-routing-safety)
-   [6. Level 4 --- Production Operations, Security, and
    Capacity](#6-level-4--production-operations-security-and-capacity)
-   [7. Hands-On Labs](#7-hands-on-labs)
-   [8. Incident Analysis: Diagnose, Fix,
    Prevent](#8-incident-analysis-diagnose-fix-prevent)
-   [9. Failover Runbook and Decision
    Exercise](#9-failover-runbook-and-decision-exercise)
-   [10. Verification, Evidence, and
    Cleanup](#10-verification-evidence-and-cleanup)
-   [11. Knowledge Check and
    Self-Assessment](#11-knowledge-check-and-self-assessment)
-   [12. References and Version-Sensitive
    Verification](#12-references-and-version-sensitive-verification)
-   [13. Final Roadmap Alignment and Authenticity
    Audit](#13-final-roadmap-alignment-and-authenticity-audit)

------------------------------------------------------------------------

## 1. Purpose, Scope, and Learning Outcomes

This unit teaches how clients reach regional service endpoints and how
traffic can be steered, failed over, gradually shifted, or kept behind a
proxy-based global entry point. The emphasis is global traffic
management (GTM), also called global server load balancing (GSLB),
DNS/client convergence, health-check decisions, TLS continuity, safe
traffic changes, capacity, and end-to-end failover measurement.

By the end, you should be able to:

1.  Explain authoritative DNS, recursive resolvers, A/AAAA/CNAME, TTL,
    negative caching, client caches, connection pools, and why TTL is
    not a global convergence guarantee.
2.  Compare DNS-based steering, anycast, global Layer 7 (L7) load
    balancing/CDNs, proxy-based entry, client-side selection, and hybrid
    patterns.
3.  Design health checks with explicit intervals, timeouts, thresholds,
    hysteresis, and independent vantage points.
4.  Measure failover from detection through decision, route publication,
    client convergence, and warm-up.
5.  Build a local simulation with east/west endpoints, a local DNS
    authority, policy controller, and client harness.
6.  Demonstrate false positives, blackholing, flapping, fail-static, and
    gray failures.
7.  Separate routing from database promotion/write authority.
8.  Shift and fail back gradually using service-level objective (SLO)
    gates and capacity checks.
9.  Validate TLS hostname/trust in both regions and manage DNS changes
    through review, canary, rollback, and drift detection.
10. State what a laptop simulation proves and what it cannot prove.

**Scope boundary:** This unit focuses on client-to-regional-entry
traffic. M14 Unit 4 covers cross-cluster east-west discovery/routing;
Unit 6 covers active-active versus active-passive design; Unit 7 covers
replication/consistency; Unit 8 covers fleet-wide observability/policy
governance; M13 covers broader DR strategy. Do not re-teach those
modules here.

Sibling paths named by the supplied prompt (confirm they exist in the
repository before relying on them): - [Unit 1 --- Multi-cluster
topologies](01-multi-cluster-topologies-and-when-to-split-clusters.md) -
[Unit 2 --- Fleet management and Cluster
API](02-fleet-management-and-cluster-lifecycle-with-cluster-api.md) -
[Unit 3 --- Multi-cluster
GitOps](03-multi-cluster-gitops-and-config-propagation.md) - [Unit 4 ---
Cross-cluster
discovery/routing](04-cross-cluster-service-discovery-and-traffic-routing.md) -
[Unit 6 --- Regional
designs](06-active-active-vs-active-passive-regional-designs.md) - [Unit
7 ---
Replication/consistency](07-data-replication-and-consistency-across-regions.md) -
[Unit 8 --- Observability/policy
governance](08-multi-cluster-observability-and-policy-governance.md) -
[Practice questions](practice-questions.md) - [Two-region failover
project](Projects/01-two-region-failover-for-a-data-platform.md)

**Critical fidelity limit:** two `kind` clusters on one laptop share
host power, kernel, storage, CPU, and often networking. This lab
demonstrates local policy, endpoint switching, selected cache behavior,
and measurement; it does not prove geographic resilience, independent
failure domains, WAN latency, provider GTM behavior, or Internet
resolver convergence.

------------------------------------------------------------------------

## 2. Mental Model: DNS, Traffic Steering, and Regional Entry

### 2.1 Request flow

``` text
Application/browser
   | local OS / app cache or resolver request
   v
Recursive resolver ---- cached answer? ----> client
   |
   | cache miss
   v
Authoritative DNS / GTM policy
   |
   | A / AAAA / CNAME answer
   v
Client chooses address; opens or reuses connection
   |
   v
Regional entry (east or west)
   |
   v
TLS validation -> HTTP request -> application -> dependencies/data authority
```

The authoritative server publishes records for a zone. A recursive
resolver looks up answers for clients and may cache them. A GTM
controller/provider may decide which answers should be published, but
the client generally receives a DNS answer, not the controller's
complete health state.

A client may not query DNS for every request. Application/OS/browser
caches, connection pools, keep-alive, HTTP/2 multiplexing, WebSockets,
retries, and long-lived connections can continue using an old endpoint.
Therefore, distinguish: - authoritative record update; - recursive
resolver's view; - first client using a new route; - last client in a
defined sample switching; - end-to-end user journey recovery; -
destination capacity becoming stable.

### 2.2 DNS fundamentals

-   **A:** name to IPv4 address.
-   **AAAA:** name to IPv6 address.
-   **CNAME:** alias to another DNS name; zone-apex restrictions and
    implementation details require verification.
-   **TTL (time to live):** cache lifetime for an answer. It is not a
    command that all clients must switch by that deadline.
-   **Negative caching:** a negative answer, such as a nonexistent name,
    may be cached. Creating a record later may not immediately change
    the view of clients holding the negative result.
-   **Resolver/client caching:** caches may exist at multiple layers;
    behavior varies.
    `[VERIFY: exact TTL clamping/cache behavior for the selected resolver, OS, and client versions.]`
-   **Connection reuse:** an existing connection may remain attached to
    an old endpoint even after DNS changes.
-   **Retries:** may help transient failures but can amplify load or
    duplicate writes if semantics are unsafe.

Lowering TTL during an incident cannot retroactively change a cache
entry that was obtained under an earlier TTL. For planned changes, lower
TTL sufficiently in advance and allow old entries to age out. TTL is a
cache hint, not a global convergence guarantee.

### 2.3 Global traffic patterns

  ------------------------------------------------------------------------------------------------
  Pattern        Decision location Strengths              Failure modes / burden   Laptop
                                                                                   feasibility
  -------------- ----------------- ---------------------- ------------------------ ---------------
  DNS-based      DNS policy        Broad client           Cache/client tail,       Good simulation
  GTM/GSLB       chooses answer    compatibility; region  authority dependency,    
                 set               selection without a    existing connections     
                                   per-request proxy      unaffected               

  Anycast        Same IP prefix    Network-level steering Routing convergence,     Not
                 announced from                           route leaks, network     meaningfully
                 multiple                                 complexity; not a DNS    proven by
                 locations using                          feature                  `kind`
                 routing such as                                                   
                 BGP                                                               

  Global L7 load Global edge       Request-level policy   Edge/provider            Local proxy is
  balancer/CDN   chooses backend   and edge observability dependency, capacity,    only an
                                                          TLS/origin configuration approximation

  Proxy-based    L4/L7 proxy       Active health checks   Proxy                    Good local
  entry          chooses backend   and backend switching  capacity/availability;   comparison
                                   for new                active sessions may      
                                   requests/connections   remain attached          

  Client-side    SDK/application   Client-specific        Every client must        Easy to model
  selection      chooses endpoint  fallback and retry     implement safe logic;    
                                   logic                  stale config and retry   
                                                          storms                   

  Hybrid         DNS selects broad Layered control        Conflicting policies,    Possible with
                 entry; proxy                             loops, unclear ownership explicit
                 chooses regional                                                  hierarchy
                 backend                                                           
  ------------------------------------------------------------------------------------------------

These patterns are not interchangeable. DNS maps names to records;
anycast is network routing; a proxy selects a backend after the client
reaches it; client-side routing is an application decision.

### 2.4 Health-check engineering

  -----------------------------------------------------------------------
  Check                   Establishes             Can miss
  ----------------------- ----------------------- -----------------------
  TCP connect             A connection is         HTTP errors, broken
                          possible from one       dependencies, TLS, user
                          vantage                 journey, capacity

  HTTP status             One endpoint returns a  Real journey,
                          configured status       authorization, data
                                                  correctness

  Readiness               Declared readiness      Missing or overly
                          conditions pass         shallow criteria

  Synthetic user journey  A selected end-to-end   Uncovered user paths or
                          action succeeds from a  regions
                          vantage                 

  Dependency probe        A dependency operation  May over-couple regions
                          succeeds                to a shared dependency
  -----------------------------------------------------------------------

Define interval, timeout, failure threshold, recovery threshold,
hysteresis/debounce, vantage, stale-signal behavior, and
controller-outage behavior. There is no universal interval/threshold.
Deep checks can amplify an outage or mark both regions down due to a
shared dependency.

**Fail-static definition used here:** if fresh health evidence or
controller authority is unavailable, retain the last known approved
route rather than publishing an empty set or oscillating. This does not
mean blindly routing to an endpoint known to be unsafe. A confirmed
safety-gate failure may require an approved emergency
withdrawal/unavailable mode. Document the age limit, override, alert,
and owner.

### 2.5 Failover-time anatomy

`T_failover ≈ T_detect + T_decide + T_propagate + T_client + T_warmup`

-   `T_detect`: interval, timeout, threshold, and vantage effects.
-   `T_decide`: controller logic, safety gates, and human approval if
    required.
-   `T_propagate`: authoritative update and relevant resolver/edge
    distribution.
-   `T_client`: next lookup, client cache, connection pool, retry, and
    client tail.
-   `T_warmup`: capacity, autoscaling, cache warm-up, connection ramp,
    and dependency readiness.

This is a decomposition, not a guarantee that all phases are strictly
additive; some overlap.

**Illustrative arithmetic, not a benchmark:** detection 18 s + decision
4 s + authority visibility 2 s + slow client cohort 240 s + warm-up 35 s
= 299 s, or about 5 minutes. The DNS record can change near the start
while some clients still use the old route.

-   **p50:** median observed convergence time.
-   **p95:** 95th percentile for a defined sample.
-   **p99:** 99th percentile only when sample size and estimator support
    meaningful interpretation.
-   **Maximum observed:** largest value in this sample, not a universal
    upper bound.

Define cohort, sample size, start/stop event, clock source, failures,
and censored observations. Excluding disconnected clients makes the tail
look artificially good.

------------------------------------------------------------------------

## 3. Level 1 --- Foundations and Global Traffic Architecture

### 3.1 Select the pattern by failure semantics

1.  Decide whether clients can tolerate changes only on new connections
    or require request-level backend selection.
2.  Name the owner of routing decisions: DNS/GTM, proxy, or client.
    Avoid independent controllers modifying the same policy.
3.  Define "healthy": reachability, user journey, TLS, dependencies,
    capacity, and/or data authority.
4.  Keep write authority separate from endpoint routing. A route change
    cannot promote/fence a database.
5.  Define client cache, connection, retry, and session behavior.
6.  Prove the destination can absorb traffic before shifting.
7.  Treat fail-back as a controlled migration, not a blind reversal.

### 3.2 Policy modes

-   **Primary/secondary:** choose preferred endpoint while health and
    safety gates pass; otherwise choose approved secondary. Define
    both-down and stale-signal behavior.
-   **Weighted:** distribute new selections according to configured
    weights. Resolver caching and connection reuse mean observed request
    shares may differ from configured weights.
-   **Latency-based:** select using a defined latency signal. This
    lesson's lab uses synthetic values; do not claim the DNS authority
    measures application latency unless the selected implementation
    does.
-   **Geo-based:** selection depends on a location signal that may
    reflect a recursive resolver rather than the end user. `[VERIFY]`
    exact product behavior.
-   **Fail-static:** retain last approved route under missing evidence,
    subject to documented override for confirmed danger.

### 3.3 Example policy (assumptions, not defaults)

`[ASSUMPTION]` Two regions, read-only requests safe in either region,
writes gated separately. Candidate policy: probe every 5 seconds;
1-second timeout; 3 consecutive failures to mark unhealthy; 4 successes
to recover; two logical probe vantage points should agree for automatic
withdrawal. If probes disagree or become stale, freeze the last approved
route and alert. Writes remain blocked unless data authority is
confirmed. Tune these values using measured noise and service
objectives.

### 3.4 DNSSEC and account protection

DNS Security Extensions (DNSSEC) support validation of DNS data
authenticity/integrity when correctly deployed. They do not make a
compromised registrar account or unauthorized but validly signed change
harmless. Least privilege, strong authentication, audit logs,
privileged-action alerts, and tested recovery remain necessary. Verify
current implementation guidance before deploying.

### 3.5 DNS-provider outage strategy

Multiple authoritative providers may reduce selected provider-specific
risks only if delegation, zones, credentials, automation, monitoring,
and operations are sufficiently independent. Shared compromised
credentials, common change pipelines, invalid delegation, or common
network dependencies can defeat the design. Static fallback can help
selected internal names but can also become stale. Document exactly
which failure modes the design covers.

------------------------------------------------------------------------

## 4. Level 2 --- Build a Local Global-Traffic Simulation

### 4.1 Architecture and preflight

**SIMULATION --- NOT REAL GLOBAL ROUTING.**

``` text
Host / WSL2
  ├── kind-stage2e-east-lab -> app -> served-by: east
  ├── kind-stage2e-west-lab -> app -> served-by: west
  ├── local policy/controller
  ├── local authoritative DNS server
  └── client harness -> request timestamps and route identity
```

The DNS server, controller, and client are separate roles. Kubernetes
CoreDNS is not automatically authoritative for an arbitrary external lab
name.

Read-only preflight:

``` bash
kind get clusters
kubectl config get-contexts
kubectl config current-context
docker info --format '{{.ServerVersion}}'
python3 --version
git --version
command -v dig || command -v drill
df -h .
free -h
```

Verify that the two exact clusters exist and that actual contexts map to
them. A common `kind` context pattern is `kind-<cluster-name>`, but
inspect output instead of assuming it.

For every Kubernetes command, use an explicit context:

``` bash
kubectl --context kind-stage2e-east-lab get nodes
kubectl --context kind-stage2e-west-lab get nodes
kubectl --context kind-stage2e-east-lab get namespaces
kubectl --context kind-stage2e-west-lab get namespaces
```

If names differ, substitute verified lab contexts. Stop if mapping is
ambiguous.

### 4.2 Safe context guard

Create this helper in a temporary lab directory. It is a guard against
mistakes, not a security boundary:

``` bash
#!/usr/bin/env bash
set -euo pipefail
require_lab_context() {
  local expected="$1" actual
  actual="$(kubectl config current-context)"
  if [[ "$actual" != "$expected" ]]; then
    echo "ABORT: expected $expected, got $actual" >&2
    return 20
  fi
}
require_lab_cluster() {
  case "$1" in
    stage2e-east-lab|stage2e-west-lab) ;;
    *) echo "ABORT: non-lab cluster $1" >&2; return 21 ;;
  esac
}
```

Use M14 Unit 1's CIDR plan if available. Otherwise choose
non-overlapping unused ranges after checking host, VPN, and Docker
routes. Example CIDRs are not defaults; record actual choices. Check
resource/disk availability before creating clusters.

### 4.3 Choose the entry path

-   **NodePort:** reachability depends on `kind` node-container
    networking and port mappings; it is not automatically available at
    any host address.
-   **Ingress/Gateway:** requires a controller and verified
    configuration/version.
-   **MetalLB:** needs compatible local network configuration; do not
    assume it is installed.
-   **Port-forward:** useful for functional checks but not
    representative of a global entry architecture.

Choose one path and prove that the client harness can directly reach
both endpoints before steering tests. Do not assume node IPs are stable.

### 4.4 DNS implementation: verify before running

Choose one authoritative DNS server only after checking official
documentation for authoritative zone syntax, A/AAAA/CNAME syntax, TTL,
validation/reload/update method, authentication, and direct
authoritative queries.

`[VERIFY: choose a DNS implementation and exact version; validate official syntax and safe update/reload mechanism before using it.]`

Do not mix server syntaxes. Keep port 53 private to the lab. Explicitly
document where queries originate: host, WSL, Docker container, or
Kubernetes pod. Each may use a different resolver configuration.

### 4.5 Pure policy model

This example validates policy decisions but does not contact Kubernetes
or change DNS. Save as `policy_model.py` in the temporary lab directory:

``` python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Region:
    name: str
    healthy: Optional[bool]  # None means stale/missing
    synthetic_latency_ms: float
    weight: int

def choose(regions, mode, last_approved):
    allowed = {"east", "west"}
    if len(regions) != 2 or {r.name for r in regions} != allowed:
        raise ValueError("exactly east and west are required")
    if mode not in {"failover", "weighted", "latency"}:
        raise ValueError("invalid mode")
    if any(r.weight < 0 for r in regions):
        raise ValueError("weights must be non-negative")
    by_name = {r.name: r for r in regions}
    if any(r.healthy is None for r in regions):
        if not last_approved or not set(last_approved) <= allowed:
            raise ValueError("no valid last-approved route")
        return tuple(last_approved)
    healthy = [r for r in regions if r.healthy]
    if not healthy:
        if not last_approved or not set(last_approved) <= allowed:
            raise ValueError("both unhealthy and no valid last-approved route")
        return tuple(last_approved)
    if mode == "failover":
        return ("east",) if by_name["east"].healthy else ("west",)
    if mode == "latency":
        return (min(healthy, key=lambda r: r.synthetic_latency_ms).name,)
    eligible = tuple(r.name for r in healthy if r.weight > 0)
    return eligible or (min(healthy, key=lambda r: r.name).name,)

if __name__ == "__main__":
    rs = [Region("east", True, 22, 80), Region("west", True, 55, 20)]
    print("failover:", choose(rs, "failover", ("east",)))
    print("weighted eligible:", choose(rs, "weighted", ("east",)))
    print("synthetic latency:", choose(rs, "latency", ("east",)))
    down = [rs[0], Region("west", False, 55, 20)]
    print("both unhealthy / fail-static:", choose(down, "failover", ("east",)))
```

Expected **representative/synthetic** output:

``` text
failover: ('east',)
weighted eligible: ('east', 'west')
synthetic latency: ('east',)
both unhealthy / fail-static: ('east',)
```

Weighted mode returns eligible endpoints; it is not a request scheduler
and does not prove statistical weighting. Add tests for invalid mode,
negative weights, stale health, both-down behavior, and latency
selection.

### 4.6 Client harness and update protocol

For each request, record timestamp, cohort, whether lookup occurred,
answer/region, connection reuse, attempt, status, latency, and retry
outcome. Keep raw rows and include failures. A simulated cache is useful
for exploring behavior but does not prove a particular real resolver
implementation.

CSV schema:

``` text
timestamp_utc,elapsed_ms,cohort,lookup_performed,answer,connection_reused,attempt,status,latency_ms
```

Before a DNS change: save baseline config/checksum; validate proposed
config; verify exact test name and target; query current authority;
capture baseline HTTP results; apply only through the selected server's
documented mechanism; query authority and intended recursive resolver
separately; run actual HTTP requests; roll back on failed validation or
SLO breach.

Do not use blind string replacement on arbitrary zone files. If dynamic
updates are unsupported, use version-controlled configuration plus
validated reload. Test names must remain private to the lab.

### 4.7 Preflight acceptance gate

-   [ ] Both exact clusters and contexts verified.
-   [ ] CIDRs do not overlap host/VPN/Docker routes.
-   [ ] Resource budget adequate.
-   [ ] East/west endpoints return distinct identity.
-   [ ] DNS authority distinguished from cluster DNS and host resolver.
-   [ ] Test hostname resolves only through intended lab path.
-   [ ] Policy model tests pass.
-   [ ] Both direct endpoints work before steering.
-   [ ] Baseline and rollback copies saved.
-   [ ] No public DNS, production credentials, customer data, or real
    private keys.

Stop if any check fails.

------------------------------------------------------------------------

## 5. Level 3 --- Failover Timing, Health Policy, and Routing Safety

### 5.1 Timestamp experiment

Capture `t0_failure`, `t1_first_probe_failure`, `t2_threshold`,
`t3_decision`, `t4_route_change`, `t5_first_client_switch`,
`t6_last_observed_switch`, and `t7_stable`.

Calculate: - detection = `t2 - t0`; - decision = `t3 - t2`; - route
publication = `t4 - t3`; - observed client tail = `t6 - t4`; -
stability/warm-up = `t7 - t5`; - end-to-end recovery = `t7 - t0`.

Keep raw timestamps. Some phases may overlap; state the exact definition
used.

Use cohorts for fresh lookup, simulated TTL cache, application cache,
persistent connections, and bounded retries with jitter. Vary one factor
at a time. Define a fixed observation window; include timeouts and
censored observations. For small samples, report count, median, and
maximum observed rather than a misleading p99.

### 5.2 Health-policy experiments

  -----------------------------------------------------------------------------
  Failure           Safe model        Expected behavior       Evidence
  ----------------- ----------------- ----------------------- -----------------
  False positive    One transient     No switch below         Probe/state
                    probe failure     threshold               timeline

  Blackholing       Shallow endpoint  Journey probe catches   Probe and request
                    green, user path  mismatch                logs
                    fails                                     

  Flapping          Alternate results Hysteresis reduces      Route transition
                    near threshold    oscillation             count

  Stale evidence    Stop refreshing   Freeze/alert per policy Signal age and
                    one signal                                decision

  Shared dependency Same dependency   Avoid blind cascading   Regional/shared
  failure           fails in both     withdrawal              signals
                    regions                                   

  Both down         Both endpoints    Explicit                Route state and
                    unhealthy         fail-static/emergency   alert
                                      policy                  
  -----------------------------------------------------------------------------

Abort if the route oscillates without bound, any endpoint becomes public
unintentionally, non-lab DNS changes, or writes reach an unpromoted
region. Restore baseline and clear injected faults.

### 5.3 Proxy comparison

A proxy can select a backend for new requests/connections based on its
policy. It does not automatically migrate an arbitrary TCP session,
WebSocket, or application transaction. Exact behavior is
implementation-dependent.

Compare detection, decision path, client caches, existing connections,
TLS placement, observability, proxy capacity, proxy outage, and
operations. Use the same workload for DNS and proxy variants.
`[VERIFY: select proxy/version; check official syntax for active health checks, backend selection, TLS, validation/reload, and connection draining.]`
If installation is too heavy, use the guided comparison and mark it "not
executed," not measured.

### 5.4 Write-routing safety

``` text
WRITES_DISABLED
  -> PROMOTION_PENDING
  -> readiness + fencing + authority verified
  -> AUTHORITY_CONFIRMED
  -> explicit gate -> WRITES_ENABLED
  -> ambiguity/lost fencing -> ROLLBACK_OR_UNCERTAIN -> WRITES_DISABLED
```

A route change cannot make a read-only replica writable. In the lab,
reads may route to a healthy endpoint; writes must be rejected until a
synthetic promotion marker and fencing/readiness gates pass. Negative
test: write before promotion returns a rejection and does not mutate
synthetic state. Switching DNS/weights must not change write authority.

Do not promote a real database. Split-brain, stale replicas, ambiguous
write timeouts, and duplicate retries are data-layer risks; M14 Unit 7
owns the full consistency treatment.

### 5.5 Gradual shift and surge arithmetic

Use staged shifts and bake periods only when the architecture permits
them. Example stages 5% → 20% → 50% → 100% are illustrative, not
universal. Every stage needs error/latency/capacity gates, halt, and
rollback.

`[ASSUMPTION]` Total demand is 1,200 requests/s; surviving west safe
capacity is 900 requests/s: - deficit = `1,200 - 900 = 300 req/s`; -
supportable fraction = `900 / 1,200 = 0.75`, or 75%; - the remaining 300
req/s must be safely shed, queued, or served elsewhere.

These are synthetic assumptions, not benchmarks. Validate N-1 capacity,
scaling lag, quotas, warm caches, connection ramps, dependency limits,
bounded retries, jitter, rate limits, concurrency limits, queueing, and
load shedding.

Fail-back is a controlled migration: verify the recovered region's
dependencies, TLS, capacity, data state, and write authority; shift a
small amount; wait through a bake period; proceed only while gates pass.
Do not blindly reverse the failover.

------------------------------------------------------------------------

## 6. Level 4 --- Production Operations, Security, and Capacity

### 6.1 DNS change control

1.  Store intended DNS/GTM config in version control.
2.  Validate syntax and policy with the selected implementation's
    supported tools.
3.  Review hostname, TTL, targets, weights, and blast radius.
4.  Lower TTL in advance for planned changes if useful; old cached
    entries retain their prior lifetime.
5.  Test a canary subdomain/low-impact record.
6.  Require peer review and least-privilege approval for critical names.
7.  Shift progressively and monitor SLOs and client convergence.
8.  Halt automatically on safety-gate/SLO breach.
9.  Keep a known-good config and rollback procedure.
10. Verify authority, recursive resolver, client route, TLS, and user
    journey separately.
11. Detect unexpected changes using live-versus-approved drift and audit
    events.
12. Test account recovery and emergency access.

A local Git workflow can simulate review/change control without a GitOps
controller. Do not modify repository files as part of this task; learner
artifacts belong in their own lab directory.

### 6.2 Readiness gates and multi-vantage probes

Hard gates must not be hidden inside a weighted score:

``` text
eligible_for_read =
  endpoint_reachable AND tls_valid AND journey_passes
  AND capacity_passes AND critical_dependencies_acceptable

eligible_for_write =
  eligible_for_read AND data_authority_confirmed AND fencing_confirmed
```

`[ASSUMPTION]` An advisory score might weight journey 40%, capacity 25%,
dependency health 20%, signal freshness 15%. These weights are examples
only; a high score cannot override invalid TLS, stale critical evidence,
or missing write authority.

Use two logical probe clients in the local lab, clearly stating that
they share one physical failure domain. A real deployment needs
independent vantage points. Record timestamp, vantage, DNS answer, TLS
result, HTTP journey, latency, dependency status, capacity, region
identity, and config revision. Missing/contradictory critical evidence
should freeze changes or enter a documented safe mode and alert---not
silently become healthy.

### 6.3 TLS continuity

For a shared hostname, each possible TLS termination point needs a valid
certificate with correct SAN/hostname, validity period, trust chain, and
client trust. Ensure renewal does not depend exclusively on the failed
region. Use a throwaway local CA and certificates; protect private keys;
test missing, wrong-SAN, expired, and untrusted certificates. Restore
valid certs and remove lab keys at cleanup.

`[VERIFY: exact cert-manager/OpenSSL commands, issuer/challenge configuration, CA constraints, and renewal behavior for selected versions.]`
Never disable TLS verification to make a test pass.

### 6.4 SLI/SLO examples

An SLI is a measured indicator; an SLO is a target over a defined
window. All numeric targets must be labelled assumptions or measured
results.

  -----------------------------------------------------------------------
  SLI                     Example definition      Why it matters
  ----------------------- ----------------------- -----------------------
  Detection               Fault to threshold      Monitor/policy response
                          declaration             

  Decision                Threshold to            Controller/approval
                          accepted/rejected       delay
                          decision                

  Route publication       Decision to DNS/proxy   Control-plane time
                          change                  

  Client convergence      Per-client first        Cache and connection
                          success through new     tail
                          route                   

  Failover success        Exercises meeting all   Avoids equating route
                          defined gates           change with recovery

  False-failover rate     Unnecessary switches    Noisy policy
                          per period              

  Flapping count          Route transitions per   Stability
                          incident                

  Journey success         Successful synthetic    User-visible health
                          journeys / valid        
                          attempts                

  DNS lookup success      Lookups successful by   DNS dependency
                          vantage/resolver        

  TLS validity            Hostname/trust checks   Secure fallback
                          by region               

  Capacity headroom       Tested capacity minus   Overload risk
                          forecast demand         

  Weight drift            Actual config vs        Unauthorized/manual
                          approved state          changes

  Fail-back duration      Start to stable         Recovery risk
                          SLO-compliant state     
  -----------------------------------------------------------------------

A DNS-update metric alone says nothing about client convergence, TLS,
journey success, data authority, or capacity. Global averages can hide
one failing region; show per-region and per-vantage views. Use Unit 8
for fleet-wide governance.

### 6.5 Security, complex failure, and capacity

Control critical DNS records with least privilege, strong
authentication, audit logs, separation of duties, approved emergency
overrides, and alerts for unexpected targets/delegation changes. For
suspected account compromise, preserve evidence and contain identities
through a trusted recovery path; do not assume the current console state
is trustworthy.

  -----------------------------------------------------------------------
  Failure                 Why green metrics can   Defense
                          mislead                 
  ----------------------- ----------------------- -----------------------
  Gray failure            Probes pass while some  Client telemetry and
                          users fail              journey probes

  Correlated failure      Regions share DNS,      Map common
                          identity, DB, or other  dependencies; safe
                          dependency              degraded mode

  Failover storm          Retries and clients     Jitter, retry budgets,
                          shift together          rate limits, staged
                                                  shifts

  Fail-back storm         Restored region         Ramp, bake, rollback
                          receives sudden load    gate

  Split DNS/stale cache   Different clients see   Multi-resolver and
                          different routes        client measurements

  DNS-provider outage     Name discovery fails    Tested, independent
                                                  contingency where
                                                  justified

  TLS asymmetry           Secondary certificate   Per-region TLS
                          missing/invalid         readiness

  Capacity collapse       Reachable region        N-1 tests, quotas,
                          overloaded              warm-up, load shedding

  Unauthorized change     Route differs from      Audit, drift detection,
                          approved state          privileged-access alert
  -----------------------------------------------------------------------

HTTP/3/QUIC migration, service-mesh global traffic/xDS, and edge compute
are awareness topics.
`[VERIFY: current protocol behavior, product capability, and supported version.]`
Standby capacity trades cost for recovery speed; quotas, autoscaling
lag, warm-up, data transfer, and cache misses matter. Do not invent
provider prices or universal capacity percentages. M07 is relevant to
quota/capacity foundations; M15 to deeper capacity/FinOps.

------------------------------------------------------------------------

## 7. Hands-On Labs

> **Safety for every lab:** These are local simulations. Use only the
> two named lab clusters and verified contexts. Every mutating action
> must identify target, preconditions, expected effect, abort path, and
> cleanup. No public DNS, cloud spend, production credentials, customer
> data, or real database promotion. Stop on context ambiguity, public
> exposure, uncontrolled flapping, or a write-authority violation.

### Lab 1 --- Local GSLB simulation

**Objective/level:** Primary/secondary, weighted and synthetic-latency
policy; Level 2. **Time:** 2--4 h, illustrative. **Resources:** two
local clusters, Python, DNS diagnostics, direct endpoint access.

**Topology:** east/west apps, private authoritative DNS, policy
controller, client harness. **Preflight:** verify `kind get clusters`,
contexts, and `kubectl --context kind-stage2e-east-lab get nodes` / west
equivalent. Stop if context mapping is wrong.

1.  Save baseline DNS/config and checksum in a temporary directory.
2.  Deploy distinct east/west response identities using explicit
    contexts and a lab namespace.
3.  Prove direct HTTP reachability for both endpoints.
4.  Select one DNS server and validate its official authoritative
    syntax/update method.
5.  Run `policy_model.py`; add tests for invalid policy, negative
    weights, stale health, both-down, and latency.
6.  Connect to DNS update mechanism only after authentication and target
    zone are verified.
7.  Test primary/secondary with east healthy and then unhealthy.
8.  Test weighted policy with a fixed sample; compare with a predeclared
    statistical tolerance.
9.  Test latency policy with synthetic inputs only.
10. Test invalid policy and rollback; query authority, recursive
    resolver, and HTTP client separately.

**Positive/negative tests:** healthy primary selects east; failed east
selects west after threshold; invalid mode and negative weights
rejected; missing evidence freezes route; both-down does not fabricate a
healthy destination.

**Expected representative output (not observed):**

``` text
policy=failover desired_route=east
policy=failover desired_route=west reason=east_unhealthy
policy=latency desired_route=east source=synthetic_latency
invalid_policy=rejected
dns_authority_answer=recorded
client_route=recorded
```

**Evidence:** versions, endpoint outputs, DNS config diff,
authority/resolver answers, controller logs, request CSV, tests,
rollback. **Common mistakes:** assuming CoreDNS is authoritative;
testing `dig` but not HTTP; assuming stable node IPs; mixing server
syntax; exposing port 53. **Abort/cleanup:** abort if update target is
unclear or listener is public; restore saved config, verify baseline,
stop controller, remove only exact lab resources. **Does not prove:**
Internet convergence or real global routing.

### Lab 2 --- Failover-time anatomy

**Objective:** measure detection, decision, publication, client tail,
warm-up. **Time:** 90--150 min. **Preflight:** stable Lab 1, baseline
route saved, controlled lab-only failure.

1.  Run a fixed baseline cohort.
2.  Add cohorts for simulated TTL values (e.g. 5/30/120 s), app cache,
    and connection reuse; these are settings, not production
    recommendations.
3.  Inject one reversible endpoint failure and timestamp it.
4.  Capture first failed probe, threshold, decision, route change, first
    client switch, last observed switch, and stable state.
5.  Repeat and retain raw rows.
6.  Calculate p50/p95/p99 only when sample size supports interpretation;
    otherwise report count, median, maximum.
7.  Plot route publication separately from client convergence and
    stability.
8.  Restore and verify baseline.

  -------------------------------------------------------------------------------------
  Run        Cohort          n   Detect   Decide   Publish    First       Last Stable
                                                             switch   observed 
  ---------- -------- -------- -------- -------- --------- -------- ---------- --------
  Fill with                                                                    
  measured                                                                     
  data                                                                         

  -------------------------------------------------------------------------------------

**Expected:** authority may change before some modeled clients switch;
measure this in the selected harness. **Evidence:** CSV, cohort
definitions, percentile method, plot, clock source. **Abort:** stop if
fault escapes lab or clocks are incomparable. **Cleanup:** restore
endpoint and route. **Does not prove:** production timing or Internet
resolver behavior.

### Lab 3 --- Health-check engineering

**Objective:** false positives, blackholing, flapping, hysteresis,
fail-static, shared dependency. **Time:** 2 h. **Preflight:** record
baseline, thresholds, probe IDs, alert policy.

1.  Inject one transient failure below threshold; verify no switch.
2.  Make shallow health green while user journey fails; verify journey
    alert.
3.  Alternate results near threshold; count transitions.
4.  Add recovery hysteresis and repeat.
5.  Stop refreshing one logical probe; verify stale signal handling.
6.  Simulate shared dependency failure; compare regional and shared
    signals.
7.  Mark both down; verify documented fail-static/emergency policy.
8.  Clear faults and confirm stable route.

  -----------------------------------------------------------------------
  Scenario          Expected          Observed          Evidence
  ----------------- ----------------- ----------------- -----------------
  One transient     No switch below   Fill after run    State log
  failure           threshold                           

  Shallow green,    Journey alarm     Fill after run    Probe outputs
  journey broken                                        

  Alternating       Fewer transitions Fill after run    Transition count
  health            with hysteresis                     

  Stale probe       Freeze/alert      Fill after run    Signal age

  Shared dependency Avoid blind       Fill after run    Regional signals
  down              cascade                             

  Both down         Explicit safe     Fill after run    Route/alert
                    state                               
  -----------------------------------------------------------------------

**Abort:** repeated uncontrolled switching, accidental all-down, or any
non-lab impact. **Recovery:** clear faults, restore thresholds, verify
route and journey. **Does not prove:** independent physical vantage
points.

### Lab 4 --- Proxy-based global entry

**Objective:** compare proxy backend switching with DNS. **Time:** 2--3
h. **Preflight:** choose proxy/version; `[VERIFY]` official syntax for
active checks, backend selection, TLS, validation/reload, connection
draining. Save config and validate before start.

1.  Configure proxy to use east/west.
2.  Bind only to a lab-reachable interface.
3.  Send requests and capture region identity/latency.
4.  Inject lab-only east failure; observe backend choice.
5.  Compare same workload with DNS experiment.
6.  Stop proxy to observe entry-point failure mode.
7.  Restore config and stop process/container.

**Tests:** healthy backend selected; failed backend excluded per
configured policy; invalid config rejected; proxy outage detected; TLS
verification stays enabled. **Evidence:** config checksum, validation,
logs, CSV, failure timeline, resource use. **Abort:** public bind or
route outside lab. **Fallback:** if installation is too heavy, provide
guided architecture analysis and mark "not executed." **Does not
prove:** global edge behavior or arbitrary existing-session migration.

### Lab 5 --- Write-routing safety

**Objective:** prove route change is not data promotion. **Time:**
60--90 min. **Preflight:** synthetic state only; initial
`WRITES_DISABLED`.

1.  Send read and confirm selected endpoint.
2.  Send write before promotion; expect rejection and no mutation.
3.  Change DNS/weight only; write must still fail.
4.  Set synthetic promotion marker only after lab readiness/fencing
    checks.
5.  Verify write behavior after explicit gate.
6.  Simulate uncertain authority; return to `WRITES_DISABLED`.
7.  Reset and repeat negative test.

**Representative expected result:** read accepted; pre-promotion write
rejected; route change leaves authority unchanged; uncertain authority
disables writes. **Evidence:** transitions, request IDs, before/after
synthetic data. **Abort:** any real DB credential/endpoint appears.
**Cleanup:** reset state. **Does not prove:** real database
fencing/consistency.

### Lab 6 --- Gradual failover/fail-back and surge

**Objective:** staged weights, SLO gates, rollback, capacity limits.
**Time:** 2 h. **Preflight:** bounded synthetic generator, saved
weights, defined stop thresholds.

1.  Measure baseline rate, latency, errors, and capacity.
2.  Shift through documented stages (e.g. 5/20/50/100%, illustrative).
3.  Bake and inspect error, latency, saturation, and readiness at each
    stage.
4.  Inject a lab-only error rise or capacity reduction.
5.  Verify halt/rollback.
6.  Simulate capacity limit; test rate limiting/load shedding.
7.  Restore health and confirm TLS/data authority/readiness before
    staged fail-back.

**Tests:** no progression after SLO breach; no writes without authority;
fail-back blocked on stale readiness. **Evidence:** weights, per-region
request/error/latency data, assumptions, gate logs. **Abort:** host
instability or non-lab traffic. **Cleanup:** restore weights/fault
flags. **Does not prove:** production load capacity.

### Lab 7 --- TLS across regions

**Objective:** validate hostname/trust in both regions and negative
cases. **Time:** 2--3 h. **Preflight:** throwaway CA/certificates; no
real keys.

1.  Create a certificate for the exact test hostname using verified
    OpenSSL syntax.
2.  Install at both regional termination points.
3.  Verify hostname/SAN, validity, and trust in each region.
4.  Route client to each endpoint and validate.
5.  Replace west certificate with wrong-SAN or untrusted certificate.
6.  Verify client rejects it; do not use insecure flags.
7.  Restore valid certificate and remove lab keys.

**Tests:** both valid endpoints pass; invalid endpoint fails; restored
endpoint passes. **Evidence:** SAN/validity, chain result, handshake per
region, config diff. **Abort:** production hostname/key appears.
**Cleanup:** restore and remove temporary key material. **Does not
prove:** renewal automation or production custody.

### Lab 8 --- DNS change control

**Objective:** review, validate, canary, shift, drift-alert, rollback.
**Time:** 90--150 min. **Preflight:** temporary Git repo outside task
repository; synthetic config only; verify DNS validation/reload docs.

1.  Commit baseline.
2.  Propose a change on a branch; review hostname, TTL, targets,
    weights, blast radius.
3.  Reject invalid targets/negative weights/missing rollback.
4.  Lower TTL in advance for a planned change if useful.
5.  Canary subdomain; verify authority, resolver, client, TLS, journey.
6.  Simulate approval, apply change, monitor gates.
7.  Alter live lab config outside approved revision and verify drift
    alert.
8.  Roll back and verify authoritative answer/client path.

**Evidence:** Git log/diff, validation, canary results, live-vs-desired
state, alert, rollback. **Abort:** any production/public DNS target.
**Cleanup:** restore baseline and remove only lab repo/branch. **Does
not prove:** full GitOps controller or registrar security.

### Lab 9 --- Multi-vantage probes and readiness

**Objective:** combine journey, dependencies, capacity,
replication/readiness, TLS. **Time:** 90 min. **Preflight:** two logical
probe clients; same laptop failure domain explicitly recorded.

1.  Capture resolution, route, TLS, journey, latency, dependency,
    capacity, synthetic replication state.
2.  Implement hard gates for endpoint, TLS, journey, capacity; add
    write-authority/fencing gate for writes.
3.  Add an advisory score with `[ASSUMPTION]` weights only.
4.  Test missing/stale/contradictory signals and gray failure.
5.  Verify missing critical evidence blocks readiness.
6.  Restore all synthetic faults.

**Representative states:** contradictory journey evidence blocks
readiness; invalid TLS blocks readiness; unknown write authority keeps
writes disabled. **Evidence:** probe JSON/CSV, signal age, gate
decisions, assumptions. **Abort:** probe reaches non-lab endpoint or
missing data counts as healthy. **Cleanup:** clear faults. **Does not
prove:** physical vantage independence.

### Lab 10 --- Runbook/tabletop

**Objective:** planned vs unplanned decision, roles, safety gates,
communication, fail-back. **Time:** 60--120 min. **Preflight:** assign
facilitator, IC, routing operator, data owner, observability lead,
communications owner.

**Scenario:** both regions' shallow checks are green, but users fail.
Facilitator reveals one vantage fails TLS, latency rises, shared
dependency degrades, and the candidate region has limited headroom.

1.  Classify impact and assign IC.
2.  Identify independent, stale, contradictory, and shallow signals.
3.  Decide whether to freeze, run deeper probes, or shift.
4.  State required TLS/capacity/dependency/data-authority evidence.
5.  Choose automation versus human approval.
6.  Specify shift increments, bake, stop gates, rollback, customer
    update.
7.  Verify client convergence and journey recovery.
8.  Define fail-back gates separately.

**Facilitator answer:** "both green" is insufficient when journey/TLS
signals conflict. Do not automatically shift based on one shallow check.
Preserve evidence, assess shared dependencies/capacity, and block writes
without authority/fencing. If no target is demonstrably safe, explicit
degraded/unavailable mode can be safer than sending traffic to an
unverified endpoint.

**Rubric, 0--2 each:** journey distinction; contradictory signals;
TLS/capacity; write gate; stop/rollback; client convergence;
roles/communications; fail-back. Score 0--5 repeat, 6--11 partial,
12--16 tabletop criteria met. This is not certification. **Abort:**
participants propose unguarded writes, blind 100% shift, or disabled TLS
verification. **Does not prove:** on-call execution under real pressure.

------------------------------------------------------------------------

## 8. Incident Analysis: Diagnose, Fix, Prevent

All timelines and outputs below are **synthetic/representative**, not
provider claims or measured results. Each incident includes symptoms,
timeline, impact, hypotheses, diagnostics, mitigation, durable controls,
recovery, prevention, and lesson.

### Incident 1 --- TTL says 300 seconds; 40% of clients take 15 minutes

-   **Symptoms/misleading signal:** authority changes in 30 s; dashboard
    says "failover complete"; clients remain on old endpoint.
-   **Synthetic timeline:** 10:00 failure; 10:00:20 threshold; 10:00:30
    authority updated; 10:01 fresh resolver sees west; 10:15 last
    observed slow cohort succeeds.
-   **Impact:** inconsistent client experience due to caches, app
    refresh, connection reuse, retries.
-   **Hypotheses:** application cache, resolver/client behavior,
    persistent connection, retries, biased sampling.
-   **Diagnostics:** query authority directly and recursive resolvers
    separately; inspect client lookup, route, connection, retry logs;
    compare fresh and persistent cohorts.
-   **Mitigation:** keep secondary ready; use bounded safe
    retry/fallback; do not repeatedly rewrite DNS.
-   **Durable controls:** measure client-tail SLO; test varied
    caches/connections; pre-lower TTL for planned changes; improve
    retry/connection lifecycle.
-   **Recovery/fail-back:** only after east is ready and staged return
    passes gates.
-   **Prevention:** measure end-to-end recovery, not just record change.
-   **Lesson:** DNS publication and user-visible failover are different
    events.

### Incident 2 --- Static health page green while application is dead

-   **Symptoms:** shallow probe succeeds while user requests fail.
-   **Synthetic timeline:** 09:00 dependency degrades; 09:02 static
    probe remains green; 09:10 journey errors rise; 12:00 discovered.
-   **Impact:** dashboard masks user failure; failover may not occur or
    may be inappropriate.
-   **Hypotheses:** probe bypasses app path; single vantage; missing
    journey coverage; deep probe could overload shared dependency.
-   **Diagnostics:** compare TCP, readiness, shallow HTTP, journey;
    inspect traces, per-region failures, dependency saturation.
-   **Mitigation:** controlled shift only if alternate passes
    journey/TLS/capacity/data gates; avoid marking both down solely due
    to shared dependency.
-   **Durable controls:** layered bounded probes, clear dependency
    semantics, journey telemetry.
-   **Recovery:** wait for journey/dependency recovery through bake.
-   **Prevention:** do not equate static health endpoint with user
    health.
-   **Lesson:** a health endpoint proves only its own contract.

### Incident 3 --- Automatic failover flaps during a network blip

-   **Symptoms:** route alternates and connection churn increases.
-   **Synthetic timeline:** 14:00 loss; 14:00:05 east down; 14:00:10
    west selected; 14:00:15 east recovers; 14:00:20 shifts back; cycle
    repeats.
-   **Impact:** retries, cold cache, unstable sessions, higher load.
-   **Hypotheses:** threshold too low, no recovery hysteresis, shared
    probe path, multiple controllers.
-   **Diagnostics:** reconstruct probe/state timeline, compare vantage
    points, inspect controller ownership and config revisions.
-   **Mitigation:** freeze changes under defined fail-static policy;
    avoid competing manual toggles.
-   **Durable controls:** tune thresholds, recovery hysteresis, minimum
    dwell/bake, independent probes, transition alerts.
-   **Recovery:** restore stable route after fresh evidence and full
    readiness.
-   **Prevention:** transient-failure lab and transition-count alert.
-   **Lesson:** faster action is not always safer action.

### Incident 4 --- Failover routes writes to a read-only replica

-   **Symptoms:** route works but writes fail or become uncertain.
-   **Synthetic timeline:** 11:00 primary fails; 11:01 DNS changes;
    11:02 secondary receives traffic; writes rejected.
-   **Impact:** write outage; unsafe retries can duplicate effects after
    ambiguous timeout.
-   **Hypotheses:** routing confused with promotion, no fencing gate,
    stale replica, missing app gate.
-   **Diagnostics:** inspect authority state, fencing evidence, write
    rejection, replication/readiness, route audit.
-   **Mitigation:** disable writes and return explicit safe error;
    continue reads only if acceptable.
-   **Durable controls:** promotion/fencing gate, negative pre-promotion
    test, separate read/write policy.
-   **Recovery:** follow Unit 7; fail back only when data state is
    proven.
-   **Prevention:** routing cannot bypass write-authority gate.
-   **Lesson:** endpoint selection does not grant data authority.

### Incident 5 --- Surviving region collapses under surge

-   **Symptoms:** healthy before failover, overloaded after shift.
-   **Synthetic arithmetic:** 1,200 req/s demand; 900 req/s safe
    capacity; deficit `1,200 - 900 = 300 req/s`.
-   **Impact:** latency/errors/queues rise; retries can overload both
    regions.
-   **Hypotheses:** no N-1 test, slow scaling, quota, cold caches,
    unbounded retries.
-   **Diagnostics:** rate, saturation, queue depth, p95/p99, cache
    misses, scale events, quota errors.
-   **Mitigation:** cap accepted traffic, shed noncritical load, bound
    retries/queues, shift only to tested capacity.
-   **Durable controls:** N-1 load tests, pre-scale, quota checks, cache
    warm-up, staged shifts.
-   **Recovery:** restore original region, verify data state, staged
    fail-back.
-   **Prevention:** capacity gate based on tested safe throughput.
-   **Lesson:** health does not imply headroom.

### Incident 6 --- DNS provider outage with no secondary plan

-   **Symptoms:** direct endpoints work but global name does not resolve
    for affected clients.
-   **Synthetic timeline:** 08:00 authority/control path fails; 08:05
    new lookups fail; cached clients behave differently.
-   **Impact:** endpoint discovery failure and inconsistent client
    experience.
-   **Hypotheses:** single authority dependency, delegation issue,
    unavailable account, shared dependencies in supposed secondary.
-   **Diagnostics:** query authority and recursive resolvers separately;
    inspect delegation/audit via trusted path; compare cached and fresh
    clients.
-   **Mitigation:** use tested namespace-specific contingency; do not
    improvise broad resolver changes.
-   **Durable controls:** threat-model authority/control plane,
    independently managed redundancy where justified, test
    restore/delegation.
-   **Recovery:** validate authority and delegation from multiple
    vantage points.
-   **Prevention:** exercise the DNS dependency plan.
-   **Lesson:** healthy endpoints cannot help clients that cannot
    discover them.

### Incident 7 --- Certificate exists only in failed region

-   **Symptoms:** secondary reachable but TLS fails due to
    missing/invalid/wrong-SAN/untrusted certificate.
-   **Synthetic timeline:** 16:00 east valid; 16:05 failover to west;
    16:05:02 client rejects TLS.
-   **Impact:** secure clients cannot use fallback.
-   **Hypotheses:** certificate coupled to primary, renewal depends on
    failed region, wrong hostname/chain, missing secret.
-   **Diagnostics:** verify hostname/SAN, validity, chain, trust,
    termination point, per-region inventory.
-   **Mitigation:** route only to valid endpoint; restore approved
    certificate; never bypass verification.
-   **Durable controls:** provision/monitor certs in every region;
    renewal independent of primary; protect keys.
-   **Recovery:** both regions must pass TLS before enabling shifts.
-   **Prevention:** TLS readiness gate.
-   **Lesson:** TLS is part of readiness.

### Incident 8 --- Unauthorized DNS change via compromised account

-   **Symptoms:** unexpected target/delegation while application
    dashboard remains green.
-   **Synthetic timeline:** 02:00 unapproved change; 02:03 drift
    alert/customer report; 02:10 responders question control-plane
    trust.
-   **Impact:** misdirection, interception risk, or outage; cache tail
    varies.
-   **Hypotheses:** stolen session, overprivileged token, missing MFA,
    compromised CI identity, alerting gap.
-   **Diagnostics:** preserve audit logs and zone/delegation evidence;
    compare live with approved revision; inspect identity history via
    trusted path.
-   **Mitigation:** invoke security incident process, contain identity
    via trusted recovery, restore only after control integrity is
    verified, rotate credentials as directed.
-   **Durable controls:** least privilege, strong authentication,
    separate approvals, protected automation credentials, drift alerts,
    tested recovery.
-   **Recovery:** verify authority/delegation from independent vantage
    points and monitor convergence.
-   **Prevention:** account controls plus unapproved-change alerts.
-   **Lesson:** global routing is a security-critical control plane.

Gray failure and correlated failure apply across incidents: health may
pass while users fail, and shared dependencies can invalidate both
regions. Diagnose the dependency graph rather than assuming two region
labels mean independent systems.

------------------------------------------------------------------------

## 9. Failover Runbook and Decision Exercise

### 9.1 Runbook template

**Scope:** service `[service]`, hostname `[hostname]`, primary
`[region-A]`, candidate `[region-B]`, routing control `[DNS/GTM/proxy]`.

**Roles:** incident commander (IC), routing operator, data-authority
owner, observability/SRE lead, security lead if compromise is suspected,
communications owner. State severity, approvers, customer/status
channel, and update cadence using the organization's policy.

**Do not proceed if:** target identity is uncertain; TLS fails; critical
signals are stale/contradictory; destination capacity is unproven; write
authority/fencing is unknown for writes; control plane may be
compromised; change is not reversible/auditable; or target scope exceeds
the declared hostname/record.

### 9.2 Decision matrix

  -----------------------------------------------------------------------
  Condition               Automation              Human approval / gate
  ----------------------- ----------------------- -----------------------
  Planned reversible      Pre-approved small      Approve plan and
  migration, validated    canary may be automated expansion gates
  target                                          

  Clear failure,          Pre-approved failover   Notify/approve
  independent probes      may run                 according to policy
  agree, destination                              
  ready, read-only                                
  traffic                                         

  Stale/contradictory     Freeze/fail-static and  Required for override
  signals                 alert                   

  Write authority/fencing Must not enable writes  Data owner resolves
  uncertain                                       

  Both regions unhealthy  No fictional "healthy"  IC chooses safe
                          choice                  degraded/unavailable
                                                  mode

  Suspected DNS/registrar Do not trust suspect    Security lead and
  compromise              control path            authorized approver

  Fail-back               No blind reverse toggle Approve after
                                                  readiness/data checks
  -----------------------------------------------------------------------

### 9.3 Execution

1.  Declare incident and IC; capture impact.
2.  Freeze automatic changes if evidence is contradictory.
3.  Verify hostname, target, current config, and blast radius.
4.  Gather authority/resolver answers, independent journeys, TLS,
    dependencies, capacity, and data-authority evidence.
5.  Choose planned shift, pre-approved failover, human-approved
    failover, or degraded/unavailable mode.
6.  Keep writes disabled unless authority and fencing are confirmed.
7.  Shift gradually where feasible; apply bake periods and stop gates.
8.  Verify authority/proxy change, first/last observed client switch,
    TLS, journey, errors, latency, and capacity.
9.  Communicate timestamped updates.
10. Restore failed region safely; verify data and dependencies.
11. Fail back in stages only after gates pass.
12. Preserve logs, diffs, approvals, timeline, and follow-up actions.

### 9.4 Worked arithmetic

`[ASSUMPTION]` demand is 1,000 req/s; candidate tested safe capacity is
1,100 req/s; exercise requires 10% headroom (not a universal rule): -
required capacity = `1,000 × 1.10 = 1,100 req/s`; - safe capacity =
`1,100 req/s`; - headroom above raw demand =
`1,100 - 1,000 = 100 req/s`, or 10%.

The gate is met exactly under these assumptions; check forecast spikes,
scaling lag, quotas, dependency capacity, and load shedding.
Illustrative time: 20 s detection + 10 s decision + 3 s publication +
180 s client tail + 40 s warm-up = 253 s. This is arithmetic, not an
SLA; real phases may overlap.

### 9.5 Fail-back checklist

-   [ ] Original region endpoint and journey pass from required vantage
    points.
-   [ ] TLS hostname/trust/validity are correct.
-   [ ] Dependencies, capacity, quotas, and scaling are ready.
-   [ ] Data/replication/write authority and fencing are safe (Unit 7).
-   [ ] Approved config diff and rollback exist.
-   [ ] Traffic increments, bake periods, SLO gates, and owner are
    explicit.
-   [ ] Client convergence is measured after each shift.
-   [ ] Final state and residual cache tail are recorded.

------------------------------------------------------------------------

## 10. Verification, Evidence, and Cleanup

### 10.1 Test matrix

  ------------------------------------------------------------------------------------------
  Test                    Method            Expected         Evidence         Does not prove
                                            representative                    
                                            result                            
  ----------------------- ----------------- ---------------- ---------------- --------------
  Healthy primary         Query authority   East selected    DNS + CSV        Global
                          and send requests                                   convergence

  Primary unhealthy       Lab-only failure  West after       Probe/decision   Geographic
                                            threshold        log              detection

  Weighted distribution   Fixed sample      Within declared  Raw rows/weights Exact shares
                                            tolerance or                      for all
                                            inconclusive                      clients

  Synthetic latency       Change synthetic  Lowest-latency   Inputs/log       Real geography
                          input             eligible                          
                                            endpoint                          

  False-positive          One transient     No switch below  State log        Zero false
  suppression             failure           threshold                         positives

  Blackholing             Shallow green,    Journey blocks   Probe results    All user paths
                          journey broken    readiness                         

  Fail-static             Stop/age evidence Last approved    State/alert      Safety
                                            route retained                    indefinitely
                                            and alert                         

  TTL/client tail         Cohorts           Measured         CSV/method       Internet
                                            distribution for                  clients
                                            harness                           

  Proxy vs DNS            Same workload     Different paths  Logs/CSV         Global edge
                                            measured                          behavior

  Write before promotion  Synthetic write   Rejected, no     Request/state    Real fencing
                                            mutation         log              

  SLO breach              Inject lab-only   Shift            Gate log         Production
                          error             halts/rolls back                  correctness

  Fail-back gate          Readiness false   Fail-back        Readiness log    Full recovery
                                            blocked                           

  TLS both regions        Validate each     Both pass        Sanitized cert   Renewal
                          endpoint                           output           automation

  Invalid TLS             Wrong             Client rejects   Verification     Every trust
                          SAN/untrusted                      output           store
                          cert                                                

  DNS rollback            Invalid config    Invalid          Diff/log         Provider
                          then restore      rejected;                         console
                                            baseline                          
                                            restored                          

  Unauthorized change     Live config       Drift alert      Diff/alert       Registrar
                          diverges from Git                                   security

  Missing/contradictory   Remove/conflict   Block/freeze per Decision log     All edge cases
  signal                  critical input    policy                            
  ------------------------------------------------------------------------------------------

For every test, record exact method/command, version, expected and
observed result, deviations, and evidence. A zero exit code alone does
not prove a test passed.

### 10.2 Evidence directory

``` text
evidence/
  lab-01/
    README-experiment-notes.md
    versions.txt
    topology.txt
    config-before/
    config-after/
    config-diff.patch
    dns-authority-answers.txt
    resolver-answers.txt
    controller-events.jsonl
    client-requests.csv
    measurements.json
    plots/
    cleanup-verification.txt
  lab-02/
    raw-runs/
    percentile-method.md
    convergence-distribution.csv
  lab-03/
    probe-timeline.csv
    route-transitions.csv
    incident-notes.md
```

Record UTC timestamp, clock source, sample size, cohort, cache model,
connection behavior, fault, version/config revision, expected/observed
result, and cleanup. Sanitize secrets and sensitive paths before
sharing. Do not create or modify repository files as part of this task.

### 10.3 Cleanup

1.  Stop only the controller, DNS, proxy, and client
    processes/containers started for the lab; verify exact
    PIDs/container names.

2.  Restore saved DNS/proxy config and weights; query authority and
    intended resolver to verify baseline.

3.  Inspect namespaces before deletion:

    ``` bash
    kubectl --context kind-stage2e-east-lab get namespaces
    kubectl --context kind-stage2e-west-lab get namespaces
    ```

    Delete only exact lab namespaces after verifying names and contents.

4.  Restore any lab-created host records/resolver changes using the
    saved baseline.

5.  Clear faults, latency injection, and synthetic write state; verify
    request rate returns to zero.

6.  Remove temporary DNS credentials and proxy configs.

7.  Remove throwaway certificates/private keys after verifying valid
    baseline; never remove system/production keys.

8.  Close only the lab Git branch/repository created for the exercise.

9.  Verify no listener is exposed unintentionally and no public DNS name
    was created.

10. If deleting the clusters is intended, first inspect
    `kind get clusters`.

**⚠ LAB SIMULATION ONLY --- DESTRUCTIVE:** only if the exact names are
present and you intentionally want to rebuild, run:

``` bash
kind delete cluster --name stage2e-east-lab
kind delete cluster --name stage2e-west-lab
```

Abort if either name is absent, unexpected, or used by other work. Save
evidence first and verify the remaining cluster list afterward. Do not
use broad deletion commands.

### 10.4 Rebuild

Stop generators/controllers; restore known-good DNS/proxy config; verify
test name and direct endpoints; clear faults; confirm writes disabled;
inspect contexts/resources before rebuilding; recreate only exact named
lab clusters if needed; rerun preflight. Preserve evidence and record
why the prior state failed.

------------------------------------------------------------------------

## 11. Knowledge Check and Self-Assessment

### 1. Authoritative DNS vs recursive resolver?

**Answer:** Authoritative DNS serves a zone; recursive resolver looks up
answers and may cache them. **Distractor:** a recursive resolver is not
automatically the source of truth.

### 2. Does TTL 60 guarantee every client switches within 60 seconds?

**Answer:** No; caches, app refresh, connections, retries, and polling
matter. **Distractor:** TTL is not a global deadline.

### 3. Why can a client use a failed endpoint after DNS changes?

**Answer:** Cached answer, no new lookup, or existing connection.
**Distractor:** DNS is not consulted for every request.

### 4. What is negative caching?

**Answer:** A cached negative answer such as name-not-found.
**Distractor:** creating a record later does not necessarily invalidate
cached negatives.

### 5. Is anycast DNS steering?

**Answer:** No; anycast is routing the same IP prefix from multiple
locations. **Distractor:** DNS maps names to records.

### 6. When may proxy routing be preferable?

**Answer:** When request-level backend choice is needed without waiting
for a new DNS lookup. **Distractor:** proxy introduces
capacity/availability dependencies and does not migrate all existing
sessions.

### 7. What does TCP connect prove?

**Answer:** A connection can be established from one vantage.
**Distractor:** it does not prove HTTP journey, TLS, dependencies, or
capacity.

### 8. What is blackholing here?

**Answer:** Health probe passes while real user traffic fails along an
uncovered path. **Distractor:** green probe does not prove every path
works.

### 9. How does hysteresis help?

**Answer:** Different/stronger thresholds for down and recovery reduce
oscillation. **Distractor:** lower thresholds may amplify noise.

### 10. What if critical evidence is stale?

**Answer:** Freeze/alert or follow the documented conservative policy;
do not silently call it healthy. **Distractor:** missing data is not
health.

### 11. Define fail-static.

**Answer:** Retain last approved route when fresh evidence/control is
unavailable, with explicit override for confirmed danger.
**Distractor:** it is not indefinite traffic to a known-unsafe endpoint.

### 12. Calculate 18 + 4 + 2 + 240 + 35 seconds.

**Answer:** 299 seconds. **Distractor:** illustrative sequential
approximation, not guaranteed recovery time.

### 13. What is p99 convergence?

**Answer:** Estimated 99th percentile for a defined sample when sample
size supports it. **Distractor:** not a universal maximum.

### 14. Why is maximum observed not a universal bound?

**Answer:** It is only the largest sample value in the observation
window. **Distractor:** unseen clients may be slower or never converge.

### 15. What if both regions are unhealthy?

**Answer:** Use explicit fail-static/emergency policy and alert; do not
invent a healthy destination. **Distractor:** default selection does not
make it safe.

### 16. How can deep checks cause cascade?

**Answer:** A shared dependency failure may mark both regions down.
**Distractor:** more checks are not automatically better.

### 17. Does DNS make a read-only replica writable?

**Answer:** No; promotion/fencing/data authority are separate.
**Distractor:** route success is not database role.

### 18. What is N-1 capacity?

**Answer:** Whether remaining capacity meets demand/SLO after one
capacity unit or region is lost. **Distractor:** idle health is not
capacity evidence.

### 19. Demand 1,200 req/s, capacity 900 req/s: deficit?

**Answer:** 300 req/s. **Distractor:** routing does not create capacity.

### 20. Why is fail-back risky?

**Answer:** Recovered region may lack capacity, data readiness, TLS, or
dependencies; sudden shift creates surge. **Distractor:** infrastructure
recovery does not imply traffic readiness.

### 21. What TLS checks matter in both regions?

**Answer:** Hostname/SAN, validity, trust chain, client trust, and
termination point. **Distractor:** valid certificate in east says
nothing about west.

### 22. Why may lowering TTL during incident not help immediately?

**Answer:** Existing cache entries retain earlier TTL; clients may not
resolve again. **Distractor:** new TTL does not rewrite every cache.

### 23. What is a DNS canary for?

**Answer:** Lower-impact validation before critical change, if it
exercises relevant dependencies. **Distractor:** an unrelated canary can
create false confidence.

### 24. How detect unauthorized DNS changes?

**Answer:** Compare live and approved config; inspect authoritative
answers, audit/identity logs, targets and delegation. **Distractor:**
application health cannot prove authorization.

### 25. Does DNSSEC prevent registrar compromise?

**Answer:** Not by itself; it supports validation of signed data but
does not replace account security. **Distractor:** integrity controls do
not replace access controls.

### 26. Why are two probes on one laptop not independent?

**Answer:** They share host power/kernel/network failure domains.
**Distractor:** different process labels do not create physical
independence.

### 27. Why compare proxy and DNS with same workload?

**Answer:** Reduces confounding and isolates routing-path differences.
**Distractor:** unrelated workloads cannot isolate architecture effects.

### 28. High readiness score but invalid TLS?

**Answer:** Hard TLS gate blocks eligibility. **Distractor:** weighted
averages must not override safety gates.

### 29. What does local `kind` prove?

**Answer:** Selected local policy, endpoint, cache-model, and
measurement behavior. **Distractor:** not WAN, provider, Internet
resolver, or geographic independence.

### 30. When is automation inappropriate?

**Answer:** Stale/contradictory signals, unverified
target/TLS/capacity/authority, compromised control plane, or unvalidated
irreversible action. **Distractor:** automation is safe only inside
tested gates.

**Self-assessment:** 26--30 with sound reasoning: proceed to supervised
local labs; 20--25: revisit cache, health, and write gates; below 20:
repeat Levels 1--2. This is not production certification.

------------------------------------------------------------------------

## 12. References and Version-Sensitive Verification

**Live verification status:** official documentation was not consulted
live while authoring. URLs are known entry points, not a claim that
current versions or exact syntax were verified.

-   RFC 1034 --- Domain Names: Concepts and Facilities:
    https://www.rfc-editor.org/rfc/rfc1034
-   RFC 1035 --- Domain Names: Implementation and Specification:
    https://www.rfc-editor.org/rfc/rfc1035
-   RFC 2308 --- Negative Caching:
    https://www.rfc-editor.org/rfc/rfc2308
-   RFC 4033 --- DNS Security Introduction and Requirements:
    https://www.rfc-editor.org/rfc/rfc4033
-   kind docs: https://kind.sigs.k8s.io/
-   Kubernetes networking:
    https://kubernetes.io/docs/concepts/services-networking/
-   Gateway API: https://gateway-api.sigs.k8s.io/
-   MetalLB: https://metallb.universe.tf/
-   cert-manager: https://cert-manager.io/docs/
-   OpenSSL docs: https://www.openssl.org/docs/

**Open `[VERIFY]` items:** 1. Select and pin a DNS server; verify
authoritative mode, zone syntax, TTL, validation/reload/update
mechanism, and authentication. 2. Select and pin a proxy; verify active
health checks, backend selection, TLS, validation/reload, and
connection-draining behavior. 3. Verify actual `kind` contexts, CIDRs,
port mapping, host/client resolver path, and endpoint reachability. 4.
Verify OpenSSL/cert-manager commands and CA behavior for installed
versions. 5. Verify current API fields, CLI flags, provider features,
and supported versions before use. 6. Execute labs and save real
evidence before marking tests passed.

Provider-specific GTM features, SLAs, pricing, and performance figures
are not asserted. HTTP/3/QUIC, service-mesh global traffic/xDS, edge
compute, and DNSSEC deployment specifics require current official
verification.

------------------------------------------------------------------------

## 13. Final Roadmap Alignment and Authenticity Audit

### Pass A --- Source alignment and scope

  -----------------------------------------------------------------------
  Item                    Status                  Evidence / remediation
  ----------------------- ----------------------- -----------------------
  Filename and Stage      **PASS**                Metadata specifies
  2E/M14 placement                                exact target.

  Requirements grounded   **PASS**                Numeric policies are
  in prompt or labelled                           illustrative or
  assumption                                      `[ASSUMPTION]`.

  Distinct from Units 4,  **PASS**                Scope boundaries and
  6, 7, 8                                         cross-links.

  Zero-budget/laptop      **PASS**                Repeated across
  limitations explicit                            architecture and labs.

  Source gaps recorded    **PARTIAL**             Actual roadmap/tree and
                                                  sibling files were not
                                                  independently
                                                  inspected; verify
                                                  before merging.
  -----------------------------------------------------------------------

### Pass B --- Required coverage

  ------------------------------------------------------------------------------------------------
  Item                            Status                  Evidence / remediation
  ------------------------------- ----------------------- ----------------------------------------
  DNS, TTL, negative caching,     **PASS**                Sections 2, 5, 11.
  client caches/connections                               

  GTM, anycast, L7/CDN, client,   **PASS**                Section 2.3.
  proxy, hybrid                                           

  Health thresholds, hysteresis,  **PASS**                Sections 2.4, 3.3, 5.2, Lab 3.
  vantage, false positives,                               
  blackholing, flapping,                                  
  fail-static, cascade                                    

  Failover formula and arithmetic **PASS**                Sections 2.5, 5, 9.

  DNS/controller/client           **PARTIAL**             Architecture and policy model provided;
  simulation                                              integrated DNS update stack not
                                                          implemented/executed.

  Failover, weighted, synthetic   **PASS**                Sections 3.2, 4.5, Lab 1; weighted
  latency                                                 scheduler itself remains to be
                                                          integrated.

  Timing experiment/client tail   **PASS**                Procedure and data template; no measured
                                                          results claimed.

  Proxy variant                   **PARTIAL**             Procedure/comparison provided; exact
                                                          proxy config and measured run remain
                                                          open.

  Write safety and negative test  **PASS**                Section 5.4, Lab 5.

  Gradual                         **PASS**                Section 5.5, Lab 6.
  failover/fail-back/surge                                

  TLS continuity and negative     **PASS**                Section 6.3, Lab 7.
  case                                                    

  DNS change                      **PASS**                Section 6.1, Lab 8.
  control/canary/rollback/drift                           

  Multi-vantage readiness         **PASS**                Section 6.2, Lab 9.

  Ten labs                        **PASS**                Section 7, all ten with
                                                          steps/tests/evidence/cleanup/fidelity.

  Eight incident analyses         **PASS**                Section 8, all eight named incidents.

  Runbook, test matrix, cleanup,  **PASS**                Sections 9--11, 30 Q&A.
  25+ Q&A                                                 
  ------------------------------------------------------------------------------------------------

### Pass C --- Technical authenticity and safety

  ----------------------------------------------------------------------------
  Item                     Status                  Evidence / remediation
  ------------------------ ----------------------- ---------------------------
  TTL/cache claims         **PASS**                TTL not treated as
  qualified                                        convergence guarantee.

  DNS/proxy syntax         **PASS**                Product-specific syntax
  verified or `[VERIFY]`                           withheld pending selection.

  DNS, anycast, proxy,     **PASS**                Section 2.3.
  client routing distinct                          

  Fail-static defined      **PASS**                Section 2.4.

  End-to-end measurement   **PASS**                Sections 2.5 and 5.1.
  separated from record                            
  update                                           

  Write routing separate   **PASS**                Section 5.4.
  from promotion/fencing                           

  TLS verification remains **PASS**                Lab 7.
  enabled                                          

  Mutating commands        **PARTIAL**             Explicit contexts and
  safety-bounded                                   narrow cluster deletion;
                                                   implementation-specific
                                                   DNS/proxy mutations await
                                                   verified choice.

  No invented              **PASS**                Values labelled
  SLA/pricing/benchmarks                           illustrative; no provider
                                                   figures.

  Outputs/timings labelled **PASS**                Expected outputs are
                                                   representative/synthetic.

  Laptop fidelity limits   **PASS**                Architecture, labs, and
  repeated                                         audit.

  Version-sensitive claims **PASS**                Open items listed; no live
  verified or tagged                               verification claimed.
  ----------------------------------------------------------------------------

### Pass D --- Internal consistency and teaching quality

  --------------------------------------------------------------------------
  Item                     Status                  Evidence / remediation
  ------------------------ ----------------------- -------------------------
  Hostnames, contexts,     **PARTIAL**             Test hostname and
  DNS/controller/proxy                             contexts defined;
  integrated consistently                          concrete DNS/entry
                                                   implementation remains to
                                                   be selected.

  Commands correct for     **PARTIAL**             Read-only and Python
  actual installed                                 model examples provided;
  versions                                         implementation-specific
                                                   commands await version
                                                   verification.

  Test matrix matches labs **PASS**                Matrix maps to policy,
                                                   client, proxy, write,
                                                   TLS, governance,
                                                   readiness.

  Beginner-to-operations   **PASS**                Sections 2--11.
  progression                                      

  Stop/rollback gates      **PASS**                Labs and runbook.

  Planned/unplanned        **PASS**                Section 9.
  runbook and                                      
  communication                                    

  Cross-links accurate     **PARTIAL**             Names follow supplied
  against actual tree                              prompt; tree not
                                                   independently inspected.

  Complete lesson, not     **PASS**                Full teaching content,
  outline                                          ten labs, eight
                                                   incidents, runbook,
                                                   matrix, Q&A, references,
                                                   audit; integrated stack
                                                   remains open.
  --------------------------------------------------------------------------

### Open verification items

-   Choose/pin DNS implementation and verify official syntax, TTL,
    validation, update/reload, authentication.
-   Choose/pin proxy and verify health checks, backend switching, TLS,
    reload, and connection behavior.
-   Verify actual lab contexts, CIDRs, ports, resolver origin, and
    endpoint reachability.
-   Verify certificate commands against installed versions.
-   Inspect actual roadmap/tree and neighboring M14 files before
    merging.
-   Execute labs and save evidence before marking any implementation
    test as passed.

### Required trust statement

An AI self-audit does not replace a human running each configuration,
DNS change, health-check fault, certificate validation, write-routing
test, and recovery procedure against installed versions. Sample outputs
and timings are representative/synthetic unless captured from a real
run. Exact DNS server/proxy behavior, CLI flags, API fields, provider
features, and supported versions must be checked against current
official documentation. Two `kind` clusters on one laptop do not prove
real multi-region resilience or WAN/global routing behavior. No global
traffic-management design should be considered production-ready until
exercised and measured from independent vantage points, threat-modelled,
capacity-tested, and reviewed in the target environment.

**Overall audit: PARTIAL for implementation readiness; PASS for lesson
structure and conceptual coverage.** This is a complete learning
artifact, but a fully integrated, copy-pasteable DNS/proxy stack remains
open until exact components are selected, official syntax is verified,
the roadmap is inspected, and labs are executed with evidence.
