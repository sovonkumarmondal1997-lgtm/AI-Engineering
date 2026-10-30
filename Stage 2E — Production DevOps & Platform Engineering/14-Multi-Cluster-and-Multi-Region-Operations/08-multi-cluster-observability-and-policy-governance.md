# Multi-Cluster Observability and Policy Governance

> **Stage:** Stage 2E --- Production DevOps & Platform Engineering\
> **Module:** M14 --- Multi-Cluster and Multi-Region Operations\
> **Unit:** 8\
> **Target filename:**
> `08-multi-cluster-observability-and-policy-governance.md`\
> **Target path:**
> `Stage 2E — Production DevOps & Platform Engineering/14-Multi-Cluster-and-Multi-Region-Operations/08-multi-cluster-observability-and-policy-governance.md`\
> **Estimated time:** 40--60 hours, illustrative\
> **Prerequisites:** M03 cluster architecture/version skew/RBAC; M04
> networking; M07 IaC/parity; M08 GitOps; M09 identity/secrets; M10 SLOs
> and incident management; M11 single-cluster observability; M12
> admission/policy; M13 DR/evidence; M14 Units 1--7\
> **Stack profile:** Fleet+GitOps plus minimal observability; Core and
> Extended profiles defined below\
> **Footprint:** zero-budget laptop lab, approximately 4 CPU cores, 8 GB
> RAM, 30 GB disk; measure yours\
> **Clusters touched:** `stage2e-east-lab` and `stage2e-west-lab` only
> if those names match the supplied roadmap and actual contexts\
> **Destructive labs:** yes, but only in verified throwaway lab
> contexts\
> **Review date:** 2026-10-29\
> **Tool baseline:** exact versions not independently inventoried;
> version-sensitive details marked `[VERIFY]`\
> **Authenticity status:** teaching artifact authored; no labs, scripts,
> or tests were executed during authoring; live official documentation
> was not consulted in this pass.

## 1. Exact M11/M12 handoff statement

> M11 built the single-cluster observability stack and listed federation
> and multi-cluster aggregation as Awareness; M12 taught policy engines,
> admission controls, and identity audits for a cluster and deferred
> multi-cluster policy distribution and fleet conformance to this
> module. This unit teaches how to **see and govern a fleet**:
> aggregating metrics, logs, and traces across clusters; per-region and
> global SLOs; alert routing and deduplication; the hub-failure problem
> for observability; and distributing and verifying policy, RBAC, and
> baselines across clusters --- without re-teaching the single-cluster
> tools.

## 2. Learning outcomes and scope

By completing this unit, the learner can:

1.  Diagnose fleet visibility gaps across metrics, logs, traces,
    Kubernetes events, change metadata, and policy reports.
2.  Apply consistent `cluster`, `region`, `env`, `tier`, and `team`
    identity dimensions while controlling metric cardinality.
3.  Compare six multi-cluster aggregation approaches and defend a
    resource-aware choice.
4.  Operate two local Prometheus instances with unique cluster labels
    and a central Grafana view with two datasources and a cluster
    selector.
5.  Build dashboards and rules as code, including worst-cluster,
    regional, global, GitOps, version, and conformance views.
6.  Calculate a global service-level indicator (SLI) from summed
    eligible events, not an unweighted average of regional percentages.
7.  Test recording and alert rules with `promtool` and route/grouping
    behavior with `amtool`, subject to version verification.
8.  Keep useful local alert evaluation available when the central
    observability hub is down.
9.  Correlate logs/traces across clusters when the chosen lab profile
    supports it, or explicitly constrain the lab to metrics/logs.
10. Detect planted fleet non-conformances and treat missing/unreachable
    clusters as `UNKNOWN` or `UNREACHABLE`, never silently green.
11. Integrate conformance quarantine with the M14 Unit 3 ring advancer
    using an inspected interface or a clearly labelled fixture.
12. Distribute one policy engine's policy through
    `audit → warn → enforce`, east then west, with compatibility gates
    and rollback.
13. Inventory RBAC and credential metadata without revealing tokens,
    private keys, kubeconfigs, or secret values.
14. Measure local telemetry volume/cardinality and model growth
    transparently without pretending to know cloud billing.
15. Run a fleet incident exercise and hub-compromise tabletop with
    evidence and blameless follow-up.
16. Define governance metrics, owners, review cadence, exception
    handling, access review, and safe bounds for automation.

### Scope boundaries

This unit teaches fleet-level observability and governance. It applies
rather than re-teaches M11's single-cluster observability stack and
M12's single-cluster policy engine/admission fundamentals. It does not
implement the full M17 capstone or replace M13 recovery procedures.

-   **M03:** cluster identity, version skew, upgrade and RBAC
    fundamentals.
-   **M04:** cross-cluster networking and east-west trace path.
-   **M07:** IaC, quota and environment parity.
-   **M08:** GitOps, dashboards/rules as code, drift detection, and ring
    rollout.
-   **M09:** identity, trust, secrets, and credential rotation.
-   **M10:** SLOs, incident roles, alert routing, communication, and
    postmortems.
-   **M11:** single-cluster metrics/logs/traces; federation and
    multi-cluster aggregation were Awareness.
-   **M12:** policy/admission/image-signature and identity audit at
    cluster scope; multi-cluster policy distribution and conformance
    were deferred here.
-   **M13:** DR, evidence conventions, and regional failure exercises.
-   **M14 Unit 2:** lifecycle and supported-version inventory.
-   **M14 Unit 3:** GitOps hub/spoke, ring rollout, and ring advancer;
    this unit adds quarantine integration.
-   **M14 Unit 4:** cross-cluster discovery and trace path.
-   **M14 Unit 7:** replication-lag panel only if the data lab exists.
-   **M15:** telemetry/egress cost and FinOps, forward reference.
-   **M16:** platform golden paths, cluster vending, and service
    catalog, forward reference.
-   **M17/capstone:** integrated multi-phase failover game and broader
    capstone evidence.

------------------------------------------------------------------------

# L1 --- Fleet visibility foundations

## 3. The fleet visibility problem

In a single cluster, an engineer can often inspect one Prometheus, one
alerting path, and one dashboard. Across N clusters, the first challenge
is not drawing a larger graph; it is establishing that every signal has
a trustworthy identity and that missing signals are visible.

An incident-first diagnostic workflow asks:

1.  **Which cluster and region are affected?** Verify the source
    identity before interpreting the aggregate.
2.  **Is this local, regional, shared-dependency, or hub failure?**
    Compare independent local signals and change history.
3.  **Which clusters have stopped reporting?** Missing telemetry is
    unknown health, not zero errors.
4.  **Does the fleet average hide a bad cluster?** Inspect per-cluster
    and per-region values and denominators.
5.  **Did the symptom begin after a rollout, policy change, version
    update, or credential rotation?** Correlate alert timestamps with
    GitOps and audit events.
6.  **Can responders diagnose the event without the central hub?** Local
    telemetry and local alert evaluation must remain useful.

### Signal taxonomy

  -----------------------------------------------------------------------
  Signal                  Answers                 Main risk
  ----------------------- ----------------------- -----------------------
  Metrics                 How much, how often,    High cardinality,
                          how fast, what          missing series,
                          proportion?             aggregation errors

  Logs                    What happened in a      Excessive volume,
                          specific operation or   PII/secrets,
                          process?                inconsistent fields

  Traces                  How did a request       Missing context
                          traverse services and   propagation, sampling
                          clusters?               gaps, clock skew

  Kubernetes events       What did the control    Short retention, event
                          plane report about      loss, uneven collection
                          objects?                

  Change metadata         What                    Missing commit
                          version/config/policy   correlation or identity
                          changed and when?       

  Conformance/policy      Which required controls Stale reports,
  reports                 pass, fail, or lack     untrusted central
                          evidence?               aggregation, score
                                                  masking
  -----------------------------------------------------------------------

**\[TECHNICAL FACT\]** Aggregation does not fix identity or missing
data. If two clusters share one `cluster` label, their series may be
merged or become ambiguous. If a cluster disappears from the data path,
an aggregate can look healthier simply because its bad observations
disappeared.

## 4. Telemetry identity and cardinality contract

Every signal should use the same required dimensions:

-   `cluster`: unique, immutable cluster identity---not merely a
    friendly label that may be reused.
-   `region`: a region/failure-domain label. In kind, `east` and `west`
    are logical names only.
-   `env`: for example `dev`, `staging`, or `prod`.
-   `tier`: a bounded criticality tier such as `critical`, `general`, or
    `sandbox`.
-   `team`: a bounded owning team identifier.

Additional fields such as `service`, `namespace`, and `version` may be
useful where bounded and defined. Define the contract centrally and
validate it at ingestion or in CI.

### Resource attributes versus indexed labels

-   **Prometheus external labels:** identify a Prometheus instance or
    its outgoing series in supported federation/remote-write paths.
    Exact application and collision behavior depends on the selected
    version and path **\[VERIFY\]**.
-   **OpenTelemetry resource attributes:** describe the entity producing
    telemetry, such as service, deployment environment, or cluster.
    Verify semantic conventions and exporter mapping for the chosen
    version **\[VERIFY\]**.
-   **Loki labels:** indexed labels should be low-cardinality and useful
    for filtering. Keep request IDs and arbitrary message fields in log
    content or structured metadata as supported by the selected version
    **\[VERIFY\]**.
-   **Trace resource attributes:** make a trace's originating
    service/cluster identifiable. Do not assume a resource attribute is
    automatically indexed or queryable in every backend.
-   **Friendly names:** use them for display; retain a stable unique
    identifier for correlation and inventory.
-   **Normalization:** define a mapping when cluster names differ across
    kubeconfig, GitOps, Prometheus, OTel, and policy reports. Do not
    silently guess.

### Contract examples

  -----------------------------------------------------------------------
  Field                   Example                 Validation
  ----------------------- ----------------------- -----------------------
  `cluster`               `stage2e-east-lab`      Required, stable,
                                                  unique across inventory

  `region`                `east-lab`              Required, bounded, not
                                                  claimed to be a real
                                                  cloud region

  `env`                   `lab`                   Required, allowlisted

  `tier`                  `general`               Required, allowlisted

  `team`                  `platform`              Required, owner exists
                                                  in registry

  `service`               `inference-api`         Required for
                                                  service-level metrics,
                                                  bounded

  `request_id`            `8f…`                   Never a metric label;
                                                  log/trace field if
                                                  permitted

  `user_id`               customer-specific       Never a metric label;
                                                  avoid in telemetry
                                                  unless approved and
                                                  protected

  Raw URL                 arbitrary path/query    Avoid as metric label;
                                                  normalize route
                                                  templates
  -----------------------------------------------------------------------

### Identity failure consequences

-   Missing `cluster`: dashboards cannot safely compare clusters; alerts
    may collapse into a single series.
-   Duplicate `cluster`: east and west may look like one source,
    corrupting per-cluster alert grouping and conformance attribution.
-   Unbounded `request_id`/URL labels: each unique value can create a
    new time series, increasing memory, storage, query cost, and alert
    evaluation burden.
-   Friendly name reuse after cluster replacement: historical telemetry
    becomes ambiguous unless a stable identity/generation is also
    captured.

### Suggested lab artifact: `telemetry_identity_validator.py`

This checks declarative inventory data, not live clusters.

``` python
REQUIRED = ("cluster", "region", "env", "tier", "team")

def validate_inventory(records):
    errors = []
    seen = set()
    for index, record in enumerate(records):
        for key in REQUIRED:
            if not record.get(key):
                errors.append({"index": index, "error": "missing", "field": key})
        cluster = record.get("cluster")
        if cluster:
            if cluster in seen:
                errors.append({"index": index, "error": "duplicate", "field": "cluster", "value": cluster})
            seen.add(cluster)
    return {"valid": not errors, "errors": errors}

def validate_metric_labels(labels, forbidden=("request_id", "user_id", "raw_url", "exception")):
    return sorted(set(labels) & set(forbidden))

if __name__ == "__main__":
    sample = [
        {"cluster": "stage2e-east-lab", "region": "east-lab", "env": "lab", "tier": "general", "team": "platform"},
        {"cluster": "stage2e-west-lab", "region": "west-lab", "env": "lab", "tier": "general", "team": "platform"},
    ]
    print(validate_inventory(sample))
```

**Tests to add:** all required fields present; missing `cluster` fails;
duplicate `cluster` fails; forbidden high-cardinality labels are
reported. **\[EXPECTED --- ILLUSTRATIVE\]** The script is authored for
the lesson; it was not executed.

## 5. Aggregation architecture taxonomy

``` text
 EAST CLUSTER                         WEST CLUSTER
 +----------------------+             +----------------------+
 | app / kube events    |             | app / kube events    |
 | Prometheus + alerts  |             | Prometheus + alerts  |
 | local logs/OTel      |             | local logs/OTel      |
 +----------+-----------+             +-----------+----------+
            |                                     |
            | selected metrics/logs/traces        |
            +------------------+------------------+
                               |
                      CENTRAL VIEW / QUERY
                      +--------------------+
                      | Grafana             |
                      | optional aggregator |
                      | policy/conformance  |
                      +--------------------+
                      (not sole alert authority)
```

Compare these six approaches. They solve different problems and are not
interchangeable.

  ----------------------------------------------------------------------------------------------------------------
  Approach                Topology/data path Freshness/query behavior  Cost and security       Hub failure / local
                                                                                               capability
  ----------------------- ------------------ ------------------------- ----------------------- -------------------
  Per-cluster stacks +    One Grafana        Queries fan out; each     Duplicate UI/query      Central UI fails,
  multi-datasource        queries each       source retains its own    overhead; central UI    but local
  Grafana                 cluster's          data; cross-source        needs read access to    Prometheus and
                          Prometheus/Loki    expressions may be        each source             alerts can remain
                                             limited                                           useful

  Prometheus federation   Central Prometheus Central view is sampled   Central                 Central view
                          scrapes selected   and can be stale; choose  scrape/query/storage;   degrades;
                          series/recording   bounded selectors and     network and auth        per-cluster
                          rules through      aggregates                boundary to each source Prometheus/alerts
                          `/federate`                                                          should remain

  `remote_write` to a     Local Prometheus   Central store provides a  Ingestion, storage,     Remote-write outage
  central                 sends selected     consolidated query path;  egress, retention,      may create
  Prometheus-compatible   series to a        buffering/backpressure    deduplication/HA design queues/dropped
  receiver/store          central endpoint   and ingestion semantics                           samples depending
                                             matter                                            on implementation;
                                                                                               local
                                                                                               collection/alerts
                                                                                               remain

  Sidecar/object-store    Local Prometheus   Global query spans        Object storage,         Global query layer
  global query            data is            blocks/sidecars;          components, retention,  may fail while
  (Thanos-style           exposed/stored for freshness and             IAM, egress             local Prometheus
  awareness)              a global query     deduplication depend on                           remains; object
                          layer              topology                                          store is another
                                                                                               dependency

  OTel Collector gateway  Local agents send  Queueing/buffering and    Gateway capacity,       Gateway outage may
  for logs/traces         telemetry to       exporter retry behavior   egress, retention, PII  backpressure/drop
                          regional/central   are                       and credential boundary data after queues
                          gateways and       version/config-specific                           fill; local app
                          backends                                                             should not depend
                                                                                               on trace backend
                                                                                               for correctness

  Vendor SaaS             Agents/exporters   Provider query and        Subscription, egress,   SaaS outage removes
                          send to provider   retention model; check    residency, lock-in,     central visibility;
                                             ingestion limits and      support access          local alerting
                                             outage behavior                                   still required
  ----------------------------------------------------------------------------------------------------------------

**Awareness examples:** Thanos, Mimir, Cortex, and VictoriaMetrics are
not interchangeable products. Verify current architecture, support
status, APIs, limits, and operating model before selecting one
**\[VERIFY\]**. Vendor SaaS is a trade-off, not a default.

### Primary lab selection

**\[RECOMMENDATION\]** Use per-cluster Prometheus plus central Grafana
with two datasources as the Core profile. In Extended profile, select
**Prometheus federation** as the single primary aggregation method if
resources and version support permit. Do not install federation and
remote-write stacks simultaneously just to demonstrate both.
Remote-write, object-store query, OTel gateway, and SaaS remain
comparison options.

Why this choice: two datasources provide a small, visible baseline with
few components. Federation can demonstrate a central aggregated query
path without requiring a full long-term storage stack. The exact
Prometheus configuration and `/federate` selector syntax must be checked
against the installed version **\[VERIFY\]**.

### Security boundary

-   Central Grafana should use read-only, least-privilege access to
    telemetry endpoints.
-   Never place tokens/passwords in dashboard JSON or Git.
-   Do not assume the central hub is trusted merely because it is
    internal.
-   Local alert evaluation must not require a central dashboard or
    central query to remain available.
-   A central aggregator is a view and collection mechanism, not an
    independent source of truth for every cluster's health.

## 6. Hub failure and local authority

The management/observability plane must not share a failure domain with
the workloads it observes. A central hub can be unavailable or
compromised; local telemetry and local alert evaluation should still
function.

### Hub-down drill sequence

1.  Capture baseline: local alert rule state, local receiver
    configuration, central dashboard status, and cluster identities.
2.  Confirm the central stack is a throwaway lab deployment, not a
    shared service.
3.  Stop only the central view/aggregator component using its documented
    lab-specific stop method **\[VERIFY\]**.
4.  Trigger a harmless synthetic alert in each cluster.
5.  Verify local alert evaluation and local receiver delivery
    independently.
6.  Verify central cross-cluster queries degrade as expected and do not
    falsely report green.
7.  Restore the central component.
8.  Check whether queued/backfilled data returns according to the
    selected component's documented behavior; if unsupported or not
    tested, say so.
9.  Save timestamps, local receiver evidence, central outage evidence,
    restoration evidence, and cleanup status.

**Failure versus expected degradation:** central dashboards unavailable
during hub outage is expected if that is the chosen architecture; local
alerts failing because they depended on central query is a design
failure unless explicitly accepted and documented. No lab result is
claimed here: the drill is a procedure, not an executed test.

------------------------------------------------------------------------

# L2 --- Working fleet observability

## 7. Resource-aware architecture and profiles

### Architecture

``` text
                   Git repository
                  dashboards/rules/
                  policy bundles/RBAC
                         |
                    GitOps hub
                     /       \
                    v         v
 EAST: stage2e-east-lab   WEST: stage2e-west-lab
 +--------------------+   +--------------------+
 | workload + metrics |   | workload + metrics |
 | Prometheus + rules |   | Prometheus + rules |
 | local alerting     |   | local alerting     |
 +----------+---------+   +----------+---------+
            |                        |
            +------ federation ------+  (Extended, optional)
                         |
                  Central Grafana
               two datasources + cluster
                    selector variable
```

### Profiles

  -----------------------------------------------------------------------------------
  Profile           Components            When to use               Resource policy
  ----------------- --------------------- ------------------------- -----------------
  **Core**          Two kind clusters,    First dashboard and local Stop GitOps and
                    per-cluster           alert labs                optional services
                    Prometheus/local                                when not needed
                    rules, central                                  
                    Grafana with two                                
                    datasources, tiny                               
                    synthetic workload                              

  **Extended**      Core + one selected   SLO/routing/conformance   Add one component
                    central federation    labs                      at a time; record
                    endpoint, `promtool`,                           actual memory/CPU
                    `amtool`,                                       
                    dashboards-as-code,                             
                    conformance scanner                             

  **Full optional** Extended + OTel       Correlation and policy    Do not run every
                    logs/traces and       reporting                 component at once
                    policy-report                                   on 8 GB; use a
                    aggregation if                                  staged sequence
                    feasible                                        
  -----------------------------------------------------------------------------------

The roadmap baseline uses `stage2e-east-lab` and `stage2e-west-lab` only
if confirmed by the actual tree and kubeconfig. Cluster names in this
lesson are labels, not proof of actual context existence.

### Preflight

``` bash
kind get clusters
kubectl config get-contexts
kubectl config current-context
docker info --format '{{.ServerVersion}}'
free -h
df -h .
```

Inspect output before mutation. Verify each context maps to the intended
disposable cluster:

``` bash
kubectl --context kind-stage2e-east-lab get nodes
kubectl --context kind-stage2e-west-lab get nodes
kubectl --context kind-stage2e-east-lab get namespaces
kubectl --context kind-stage2e-west-lab get namespaces
```

If these contexts do not exist or do not map to the intended lab
clusters, stop and map the actual contexts. Do not create/delete or
apply resources to an ambiguous context. Every mutation in this unit
must use an explicit `--context` or a reviewed wrapper.

### Measure your footprint

Record baseline and per-profile: - host memory used/free; -
Docker/container CPU and memory; - disk before/after; - Prometheus
time-series count and scrape load; - dashboard query latency under the
local workload; - telemetry bytes produced over a fixed interval.

Label measurements `[LOCAL LAB MEASUREMENT]`. Do not extrapolate local
resource use or throughput to cloud cost or production scale.

## 8. Prometheus and Grafana lab configuration

This is a minimal configuration pattern, not a verified drop-in
manifest. Pin the actual image versions and verify configuration fields
against official docs for that version **\[VERIFY\]**.

### Per-cluster Prometheus configuration concept

``` yaml
# Suggested in-document artifact: prometheus-east.yml
global:
  scrape_interval: 30s
  external_labels:
    cluster: stage2e-east-lab
    region: east-lab
    env: lab
    tier: general
    team: platform

scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets: ["localhost:9090"]
```

For West, use a separate configuration with a unique `cluster` label and
`region: west-lab`. The sample scrape target assumes Prometheus runs in
a topology where `localhost:9090` is correct; adjust and verify the
target when using containers/pods. Do not copy this snippet without
checking the deployment topology.

### Central Grafana datasources concept

``` yaml
# Suggested in-document artifact: grafana-datasources.yml
apiVersion: 1
datasources:
  - name: Prometheus-East
    type: prometheus
    access: proxy
    url: http://prometheus-east.example.invalid
    isDefault: true
  - name: Prometheus-West
    type: prometheus
    access: proxy
    url: http://prometheus-west.example.invalid
```

`example.invalid` is a placeholder and will not connect. Replace it only
after choosing a reachable lab topology and verifying Grafana's
provisioning schema/version **\[VERIFY\]**. Do not embed credentials in
this file.

Configure a dashboard variable named `cluster` or a datasource variable
that lets the operator choose East or West. The dashboard should expose
the active datasource/cluster clearly; never present an unlabelled
metric as fleet-wide.

### Optional federation configuration pattern

A central Prometheus may scrape selected aggregated series from a
per-cluster Prometheus `/federate` endpoint. Exact query parameters,
external-label handling, authentication, TLS, and scrape configuration
must be verified against the pinned Prometheus version **\[VERIFY\]**.
Keep the federation selector bounded to selected recording rules/series;
avoid pulling every raw high-cardinality series by default.

**Expected behavior \[EXPECTED --- ILLUSTRATIVE\]:** a query with the
`cluster` dimension should separate East and West. If labels are missing
or collide, the identity validator should fail before the dashboard is
accepted. This behavior was not executed.

## 9. Fleet dashboards as code

### Required dashboard panels

1.  Fleet health by `cluster` and `region`.
2.  Worst-cluster error ratio, latency percentile, availability,
    saturation, and SLO burn where source metrics exist.
3.  Telemetry heartbeat/last-seen and scrape failure/absent series.
4.  GitOps sync/health and current rollout ring.
5.  Kubernetes version/support status from a trusted inventory; support
    windows are `[VERIFY]` and version-specific.
6.  Replication lag only if M14 Unit 7's data lab is present.
7.  Alert firing state and receiver delivery status.
8.  Policy enforcement mode, policy bundle version, report count, denial
    rate, and bypass signal.
9.  Conformance report freshness, critical failures, quarantine, and
    remediation age.
10. Credential rotation coverage and unexpected broad RBAC, based on
    metadata only.
11. Time-series count, log bytes, span volume if present, and
    transparent cost proxy.
12. Hub availability and central query freshness.

### Query design principles

-   Prefer recording rules for expensive reusable fleet aggregates.
-   Keep high-cardinality dimensions out of metric labels.
-   Show per-cluster results alongside the global summary.
-   Show denominators and sample counts next to ratios.
-   Treat absent series as `unknown/no data`, not zero.
-   Use explicit time windows and explain any extrapolation or
    aggregation.
-   Avoid invented exporter metric names; use a verified metric from the
    actual lab or label the query `[VERIFY]`.

### Suggested in-document artifact: `dashboard_validator.py`

The validator uses a deliberately small internal dashboard contract, not
a universal Grafana JSON schema. It verifies required datasource names,
variables, and panel identifiers in a simplified fixture.

``` python
REQUIRED_DATASOURCES = {"Prometheus-East", "Prometheus-West"}
REQUIRED_VARIABLES = {"cluster"}
REQUIRED_PANELS = {
    "fleet-health", "worst-cluster", "telemetry-heartbeat",
    "gitops-health", "policy-conformance", "telemetry-cost"
}

def validate_dashboard(doc):
    errors = []
    datasources = set(doc.get("datasources", []))
    variables = set(doc.get("variables", []))
    panels = set(doc.get("panels", []))
    for name in sorted(REQUIRED_DATASOURCES - datasources):
        errors.append(f"missing datasource: {name}")
    for name in sorted(REQUIRED_VARIABLES - variables):
        errors.append(f"missing variable: {name}")
    for name in sorted(REQUIRED_PANELS - panels):
        errors.append(f"missing panel: {name}")
    return {"valid": not errors, "errors": errors}

if __name__ == "__main__":
    example = {
        "datasources": ["Prometheus-East", "Prometheus-West"],
        "variables": ["cluster"],
        "panels": sorted(REQUIRED_PANELS),
    }
    print(validate_dashboard(example))
```

**Tests:** valid fixture passes; missing West datasource fails; missing
cluster selector fails; missing policy panel fails. This contract
validates only its own fixture shape. It does not validate a real
Grafana dashboard API/schema. Exact dashboard schema/provisioning
behavior is `[VERIFY]`.

### GitOps and rollback

-   Store dashboard definitions and recording/alert rules in Git with
    review.
-   Validate syntax/contract in CI before rollout.
-   Roll out first to the lab/canary, inspect the rendered dashboard and
    query cost, then promote.
-   Preserve the last known-good revision and define a rollback trigger.
-   Keep credentials out of Git and dashboard JSON.
-   If the central dashboard fails, use local dashboards/alerts and
    direct local evidence rather than treating the hub as authoritative.

## 10. Global SLOs and the averaging trap

### Definitions

An SLI measures a service property; an SLO sets a target over a time
window. For a request-success SLI:

\[ `\text{Success ratio}`{=tex} =
`\frac{\text{eligible good requests}}{\text{all eligible requests}}`{=tex}
\]

A global ratio for comparable eligible requests should generally be
calculated from summed numerators and denominators:

\[ `\text{Global success ratio}`{=tex} =
`\frac{\sum_r \text{good requests}_r}{\sum_r \text{eligible requests}_r}`{=tex}
\]

Do not blindly average regional percentages. A regional guardrail
remains necessary even when global performance is acceptable.

### Skewed-traffic example \[ILLUSTRATIVE\]

  Region        Good requests   Eligible requests   Success ratio
  ----------- --------------- ------------------- ---------------
  East                 99,900             100,000           99.9%
  West                    600               1,000           60.0%
  **Total**       **100,500**         **101,000**   **99.50495%**

Incorrect unweighted average of regional percentages:

\[ (99.9% + 60.0%) / 2 = 79.95% \]

In this example the arithmetic mean is much worse than the
traffic-weighted ratio; the trap can also work in the opposite direction
depending on the traffic distribution. The important point is that a
global service SLO is defined by its eligible events and
numerator/denominator---not by an arbitrary average of regions. The
global value of 99.50495% still hides a West success ratio of 60%, so a
per-region guardrail is essential.

### Missing and zero-denominator behavior

-   No eligible requests: ratio is undefined, not 100% success.
-   Missing telemetry: state is unknown/no data; do not treat it as zero
    errors.
-   Low traffic: show sample size and confidence/uncertainty; avoid
    claiming a stable tail percentile from a handful of requests.
-   Global SLO: use the agreed eligibility definition; exclude traffic
    only according to a documented policy, never to make the score look
    better.

### Recording/alert rule pattern

**\[VERIFY\]** The following is a conceptual Prometheus rule template.
Replace metric names with those emitted by the selected
application/exporter, validate syntax with the installed Prometheus
version, and test with `promtool` before deployment.

``` yaml
groups:
  - name: fleet-slo
    rules:
      - record: region:request_success_ratio:rate5m
        expr: |
          sum by (cluster, region, env, tier, team) (
            rate(http_requests_total{outcome="good"}[5m])
          )
          /
          sum by (cluster, region, env, tier, team) (
            rate(http_requests_total[5m])
          )

      - record: fleet:request_success_ratio:rate5m
        expr: |
          sum(rate(http_requests_total{outcome="good"}[5m]))
          /
          sum(rate(http_requests_total[5m]))

      - alert: RegionSLOGuardrailBreached
        expr: region:request_success_ratio:rate5m < 0.99
        for: 10m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "Regional success ratio below the illustrative guardrail"
          description: "Inspect cluster, region, denominator, missing data, and recent changes."

      - alert: FleetTelemetryMissing
        expr: absent(up{job="fleet-heartbeat"})
        for: 3m
        labels:
          severity: critical
          team: platform
        annotations:
          summary: "Expected fleet heartbeat is absent"
```

The sample uses `http_requests_total{outcome="good"}` as a teaching
metric, not a verified metric from a third-party exporter. A real rule
needs a reliable inventory of expected clusters and a per-cluster
absence test; `absent()` against one selector alone may not enumerate
every missing cluster. Implement an expected-cluster inventory
comparison in the conformance/heartbeat workflow.

### `promtool` tests

Suggested in-document artifacts: `fleet-slo.rules.yml` and
`fleet-slo.test.yml`. Exact test schema and CLI flags are `[VERIFY]` for
the pinned Prometheus version.

Test cases: 1. Correct global ratio from summed numerator/denominator.
2. The skewed-traffic example: global ratio differs from arithmetic
mean. 3. Zero denominator yields no valid ratio, not 100%. 4. Missing
region/series triggers an explicit missing-data state or inventory
alert. 5. A deliberately regressed expression that averages regional
ratios must fail the test.

**Test fixture idea \[ILLUSTRATIVE\]:** create synthetic counters for
East and West with known rates; assert the ratio-of-sums equals
`100500/101000` for the static example only if the fixture's time series
are constructed to encode those counts. For counter-rate tests, choose
sample values and scrape intervals that make the expected rate
unambiguous. Do not compare a static arithmetic table with a rate
expression without designing a consistent fixture.

Do not claim `promtool test rules` passed unless it was run with a
pinned version. No tests were executed during authoring.

## 11. Alerting, routing, and absent-cluster detection

### Alert architecture

-   **Local alerts:** evaluate within each cluster or its local
    monitoring boundary; route to a local receiver that does not depend
    on the central query service.
-   **Global alerts:** detect fleet SLO/burn or shared-dependency
    conditions using a central aggregate when available.
-   **Heartbeat/absent-cluster:** compare an expected-cluster inventory
    against telemetry last-seen. Unknown/unreachable must be explicit.
-   **Grouping:** group related alerts to reduce noise while retaining
    cluster/region context.
-   **Inhibition:** suppress derivative symptoms only when the root
    cause is evidenced; do not silence useful regional diagnosis.
-   **Ownership:** include bounded `team`, `tier`, `region`, and
    `cluster` labels plus a runbook link where supported.
-   **Change correlation:** record Git revision, rollout ring, policy
    version, and change timestamp.
-   **Receiver validation:** every cluster must have a valid route;
    null/default receiver behavior must be tested.

### Alertmanager fixture

**\[VERIFY\]** This minimal shape illustrates intent, not a verified
complete production config for every Alertmanager version. Add actual
receiver configuration and secrets outside source control.

``` yaml
route:
  receiver: platform-default
  group_by: ["alertname", "env", "tier", "team"]
  routes:
    - matchers:
        - severity="critical"
      receiver: platform-critical
      group_by: ["alertname", "cluster", "region", "team"]

inhibit_rules:
  - source_matchers:
      - alertname="SharedDependencyDown"
      - severity="critical"
    target_matchers:
      - alertname="RegionalDependencyErrors"
    equal: ["env", "team"]
```

Grouping and inhibition syntax is version-sensitive. The example
illustrates the need to retain per-cluster labels on critical alerts; it
does not define a complete receiver delivery system.

### `amtool` routing tests

Use the installed `amtool` version and verify exact command syntax
**\[VERIFY\]**. Test: - critical regional alert routes to the intended
critical receiver; - a new cluster with no configured owner/route fails
validation; - missing identity labels fail CI; - a null/default receiver
is detected before onboarding; - a shared-cause alert groups/inhibits
derivative alerts without hiding the regional symptom; - central hub
down does not prevent local alert evaluation and local delivery.

**No data is not zero errors.** A cluster that stops emitting `up` or
application metrics may disappear from a query. Use an expected-cluster
inventory, heartbeat timestamp, and last-seen SLI; never infer health
from an empty result.

## 12. Cross-cluster logs, traces, and correlation

### Collection patterns

-   **Agent/DaemonSet:** collects node/pod telemetry locally; verify
    permissions, resource overhead, and collection scope.
-   **Regional/central gateway:** receives telemetry from agents and
    exports to a backend; queues, retries, backpressure, and failure
    behavior depend on configuration/version.
-   **Resource identity:** apply the same cluster/region/env/tier/team
    contract to OTel resources and logs.
-   **Trace context:** propagate W3C Trace Context or another explicitly
    selected standard only after verifying the framework and collector
    behavior **\[VERIFY\]**.
-   **Cross-cluster call:** use M14 Unit 4's east-west request path;
    correlate parent/child spans or links, trace ID, timestamps, and
    deployment changes.
-   **Sampling:** document head/tail sampling and the possibility that
    one side of a distributed trace is missing.
-   **Privacy:** redact PII/secrets; limit retention and access.
-   **Clock skew:** timestamps from different hosts can be out of order;
    trace parentage/IDs and logical event relationships may be more
    reliable than wall-clock order alone.

### Full-profile optional trace exercise

1.  Add `cluster` and `region` resource attributes to the chosen OTel
    SDK/collector configuration.
2.  Send a synthetic request from East to West through the verified Unit
    4 path.
3.  Confirm trace context propagation is configured at the client and
    server.
4.  Query the selected trace backend and verify spans from both clusters
    share the intended trace context.
5.  Introduce a synthetic timestamp offset in test data rather than
    changing the host clock.
6.  Record missing spans, sampling policy, resource attributes, and
    cleanup.

If the Full profile exceeds laptop resources, use logs plus metrics and
an explicit correlation ID fixture. State that a real distributed trace
was not captured. No trace capture is claimed in this document.

------------------------------------------------------------------------

# L3 --- Fleet conformance and policy governance

## 13. Conformance as code

The fleet scanner must check each cluster independently and return a
machine-readable result plus a human-readable report. It must not report
green when a cluster is unreachable or evidence is missing.

### Required baseline checks

  -------------------------------------------------------------------------------------------
  Check ID                   Control                   Evidence source    Unknown/failure
                                                                          rule
  -------------------------- ------------------------- ------------------ -------------------
  `K8S_VERSION`              Kubernetes                API                `UNKNOWN` if
                             version/support status    server/inventory   unavailable;
                                                                          support window
                                                                          `[VERIFY]`

  `TELEMETRY_BASELINE`       Required telemetry agents Namespaced         Missing component
                             present/healthy           inventory/health   is `FAIL`

  `CLUSTER_IDENTITY`         Required identity         Registry and       Missing/duplicate
                             metadata                  telemetry          ID is `FAIL`

  `PSS_BASELINE`             Pod Security Standards    Namespace metadata Missing required
                             labels/baselines where                       baseline is `FAIL`
                             applicable                                   

  `NETWORK_DEFAULT_DENY`     Required NetworkPolicy    Policy inventory   Unsupported
                             baseline where CNI        and capability     CNI/evidence
                             supports it               record             unknown is
                                                                          `UNKNOWN`, not pass

  `ADMISSION_POLICY`         Required admission policy API                Missing or weakened
                             exists and mode matches   resource/policy    mode is `FAIL`
                                                       report             

  `NO_EXTRA_CLUSTER_ADMIN`   No unexpected             RBAC inventory     Unapproved binding
                             cluster-admin binding                        is `FAIL`

  `IMAGE_SIGNATURE_POLICY`   Required signature policy Policy             Not applicable only
                             active if installed by    inventory/report   with documented
                             M12                                          scope; otherwise
                                                                          `UNKNOWN`

  `AUDIT_LOGGING`            Audit logging enabled     Cluster            `UNKNOWN` if not
                             where inspectable         config/inventory   exposed

  `ENCRYPTION_AT_REST`       Reliable encryption       Provider/cluster   `UNKNOWN` if no
                             status where inspectable  configuration      reliable evidence

  `GITOPS_DRIFT`             Config matches approved   GitOps             Stale/missing
                             Git revision              status/inventory   status is `UNKNOWN`

  `OBSERVABILITY_DRIFT`      Dashboards/rules/labels   GitOps/config      Mismatch is `FAIL`
                             align with baseline       checks             
  -------------------------------------------------------------------------------------------

### Status semantics

-   `PASS`: the check ran against a reachable, correctly identified
    cluster and evidence meets the declared expectation.
-   `FAIL`: evidence demonstrates non-conformance.
-   `UNKNOWN`: insufficient or stale evidence, unsupported inspection,
    or a check not completed.
-   `UNREACHABLE`: cluster/API cannot be reached or identity cannot be
    confirmed.
-   `NOT_APPLICABLE`: an approved policy explicitly excludes the control
    with owner, reason, scope, expiry, and review.

Rollout eligibility fails closed if any critical check is `FAIL`,
`UNKNOWN`, or `UNREACHABLE`, unless a named, approved exception policy
explicitly permits a bounded exception. A missing cluster is never
silently counted as compliant.

### Score limitations

A fleet score can help trend broad conformance, but a weighted average
can hide a critical failure. Never let a high score override a failed
security-critical gate. Use: - per-cluster drill-down; -
critical-control hard gates; - report freshness; - owner and remediation
age; - evidence timestamp; - independent spot checks.

A score is an indicator, not proof of security.

### Suggested in-document artifact: `fleet_conformance.py`

This reference scanner consumes a declarative inventory fixture. It does
not query Kubernetes and does not inspect actual RBAC, policy resources,
encryption, or versions.

``` python
import json

CRITICAL_CHECKS = {
    "ADMISSION_POLICY", "NO_EXTRA_CLUSTER_ADMIN",
    "CLUSTER_IDENTITY", "TELEMETRY_BASELINE"
}

def scan_cluster(cluster, checks, reachable=True):
    if not reachable:
        return {
            "cluster": cluster,
            "status": "UNREACHABLE",
            "checks": checks,
            "rollout_eligible": False,
        }
    states = [item.get("status", "UNKNOWN") for item in checks.values()]
    critical_bad = any(checks.get(name, {}).get("status") != "PASS"
                       for name in CRITICAL_CHECKS)
    if "FAIL" in states:
        status = "FAIL"
    elif any(s in ("UNKNOWN", "UNREACHABLE") for s in states):
        status = "UNKNOWN"
    else:
        status = "PASS"
    return {
        "cluster": cluster,
        "status": status,
        "checks": checks,
        "rollout_eligible": status == "PASS" and not critical_bad,
    }

def fleet_report(inventory):
    results = []
    for item in inventory:
        results.append(scan_cluster(
            item["cluster"], item.get("checks", {}),
            reachable=item.get("reachable", True)
        ))
    states = [r["status"] for r in results]
    overall = "PASS" if results and all(s == "PASS" for s in states) else "NOT_GREEN"
    return {"overall": overall, "clusters": results}

if __name__ == "__main__":
    fixture = [{
        "cluster": "stage2e-east-lab",
        "reachable": True,
        "checks": {
            "CLUSTER_IDENTITY": {"status": "PASS"},
            "ADMISSION_POLICY": {"status": "FAIL"},
            "NO_EXTRA_CLUSTER_ADMIN": {"status": "PASS"},
            "TELEMETRY_BASELINE": {"status": "PASS"},
        },
    }, {
        "cluster": "stage2e-west-lab",
        "reachable": False,
        "checks": {},
    }]
    print(json.dumps(fleet_report(fixture), indent=2))
```

**Tests required:** missing admission policy produces `FAIL`; unexpected
extra cluster-admin binding produces `FAIL`; outdated-version fixture
produces `FAIL` when unsupported by the declared inventory; unreachable
cluster is `UNREACHABLE` and not eligible; unknown encryption status is
not treated as pass; empty fleet is not green. This is an illustrative
fixture scanner and is not connected to live Kubernetes.

## 14. Quarantine and ring-advancer integration

M14 Unit 3 owns the ring advancer. Unit 8 should integrate a conformance
result with the existing interface only if the actual artifact is
supplied and inspected. Otherwise use a clearly documented contract
fixture; do not claim a real integration.

### Gate contract

Input fields: - cluster ID; - report timestamp and freshness limit; -
report status; - critical check results; - quarantine state and
reason; - exception owner/scope/expiry; - scanner version and evidence
fingerprint.

Decision: - `ALLOW`: report fresh, cluster reachable, all critical
checks pass, no quarantine, exception policy satisfied. - `BLOCK`: any
critical failure or active quarantine. - `UNKNOWN`: stale/missing
report, scanner unavailable, identity mismatch, or unreachable cluster.

### Suggested in-document artifact: `ring_gate.py`

``` python
from datetime import datetime, timezone, timedelta

def can_advance(report, now, max_age_seconds=300):
    if not report or not report.get("cluster"):
        return {"decision": "UNKNOWN", "reason": "missing identity/report"}
    if report.get("reachable") is not True:
        return {"decision": "UNKNOWN", "reason": "cluster unreachable"}
    if report.get("quarantined"):
        return {"decision": "BLOCK", "reason": "cluster quarantined"}
    if report.get("status") != "PASS":
        return {"decision": "BLOCK", "reason": f"conformance={report.get('status')}"}
    raw = report.get("timestamp")
    try:
        observed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if observed.tzinfo is None:
            return {"decision": "UNKNOWN", "reason": "timestamp lacks timezone"}
    except (ValueError, AttributeError):
        return {"decision": "UNKNOWN", "reason": "invalid timestamp"}
    age = (now - observed.astimezone(timezone.utc)).total_seconds()
    if age < 0 or age > max_age_seconds:
        return {"decision": "UNKNOWN", "reason": "stale or future report"}
    return {"decision": "ALLOW", "reason": "fresh passing report"}

if __name__ == "__main__":
    sample = {
        "cluster": "stage2e-east-lab",
        "reachable": True,
        "quarantined": False,
        "status": "PASS",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    print(can_advance(sample, datetime.now(timezone.utc)))
```

This simple contract does not itself solve concurrent races. The real
ring advancer must re-check eligibility atomically immediately before
promotion, or use a versioned/leased decision so a quarantine added
after selection invalidates the promotion. Scanner unavailability must
block advancement, not imply success.

### Tests

-   passing fresh report → `ALLOW`;
-   active quarantine → `BLOCK`;
-   failed conformance → `BLOCK`;
-   unreachable cluster → `UNKNOWN`;
-   stale/future/invalid timestamp → `UNKNOWN`;
-   scanner unavailable → `UNKNOWN`;
-   quarantine arrives after selection → promotion rechecks and is
    blocked;
-   clearing quarantine requires fresh evidence and approved review.

## 15. Policy distribution by rings

Choose **one engine at a time**. This lesson uses **Kyverno as the
conceptual primary example**, but exact API, report resources, CLI, and
policy features are `[VERIFY]` until the installed version is pinned.
Kubernetes ValidatingAdmissionPolicy (VAP) is an alternative, not
combined with Kyverno in one supposed implementation.

### Progression

1.  **Audit:** observe and classify violations without blocking. Confirm
    report freshness and false-positive rate.
2.  **Warn:** make violations visible to owners and require an explicit
    remediation path.
3.  **Enforce:** deny non-compliant changes only after compatibility,
    exceptions, rollback, and alerting are proven.
4.  **Ring order:** lab/canary → East → West. Do not promote to West
    until East is healthy and report evidence is fresh.
5.  **Source of truth:** versioned Git policy bundle, review,
    compatibility matrix, and rollback commit.
6.  **Gate:** each cluster reports bundle version, policy resource
    presence, engine version, enforcement mode, report freshness, denial
    rate, and bypass signal.
7.  **Stop:** missing evidence, unsupported fields, unexpected
    enforcement weakening, or a critical violation halts rollout.

### Version-skew negative scenario

A policy field or capability may not be supported by an older
engine/API. Do not assume it will always fail loudly. A cluster might
reject a resource, ignore an unsupported feature, or behave differently
depending on version. Test the exact versions and schema/capabilities
before enforcement **\[VERIFY\]**.

### Bypass detection

Alert per cluster if: - expected policy resource disappears; - bundle
version drifts; - enforcement mode changes from declared `enforce` to
`audit`/disabled; - exclusions change unexpectedly; - trusted
identity/signature policy is weakened; - policy report freshness
disappears; - the hub's GitOps state claims success but independent
cluster inspection disagrees.

The monitoring signal must not rely solely on the same hub that can
remove the policy and silence its alert. Use independent per-cluster
evidence or a separate trust boundary for critical controls.

### Policy report aggregation

Aggregate counts by cluster, policy, severity, enforcement mode, result,
and timestamp. Keep report freshness visible. Do not invent exact
Kyverno PolicyReport APIs or metric names; verify the selected
engine/version and report API **\[VERIFY\]**.

**Suggested in-document artifact: `policy_report_normalizer.py`**

``` python
def normalize_reports(reports):
    summary = {}
    for report in reports:
        cluster = report.get("cluster") or "UNKNOWN_CLUSTER"
        if report.get("reachable") is not True:
            summary.setdefault(cluster, {"status": "UNKNOWN", "violations": 0, "denials": 0})
            summary[cluster]["status"] = "UNKNOWN"
            continue
        entry = summary.setdefault(cluster, {"status": "PASS", "violations": 0, "denials": 0})
        if report.get("fresh") is not True:
            entry["status"] = "UNKNOWN"
        entry["violations"] += int(report.get("violations", 0))
        entry["denials"] += int(report.get("denials", 0))
        if report.get("critical_failure"):
            entry["status"] = "FAIL"
    return summary
```

Tests: fresh clean reports pass; critical violation fails; stale report
is unknown; unreachable cluster is unknown; missing cluster identity is
not merged into a valid cluster. This is a simplified normalized
contract, not a native policy-report parser.

## 16. RBAC-as-code and credential inventory

### RBAC-as-code

-   Map identity-provider/OIDC groups to least-privilege Kubernetes
    roles.
-   Keep bindings version-controlled and reviewed.
-   Prefer read-only fleet views for routine diagnosis.
-   Use just-in-time elevation where supported; break-glass is separate,
    auditable, time-bounded, and periodically tested.
-   Do not give the observability/GitOps hub broader access than its
    function requires.
-   A hub with cluster-admin access to every spoke is a high-value
    fleet-wide credential. Assume compromise could affect policy,
    workloads, telemetry, and incident evidence.

### Metadata-only credential inventory

Inventory metadata such as owner, purpose, scope, cluster reach,
issued/rotated/expiry time where reliably available, and revocation
status. Never print token values, kubeconfig content, passwords, private
keys, or secret data. If age/expiry is not reliably observable, return
`UNKNOWN`.

**Suggested in-document artifact: `credential_inventory.py`**

``` python
SENSITIVE_KEYS = {"token", "password", "client-key-data", "private_key", "secret_value"}

def safe_credential_record(record):
    # Metadata-only allowlist: never serialize arbitrary source fields.
    allowed = ("kind", "name", "owner", "purpose", "scope",
               "cluster_reach", "created_at", "expires_at", "last_rotated_at")
    safe = {key: record.get(key) for key in allowed}
    if not safe.get("owner") or not safe.get("scope"):
        safe["status"] = "UNKNOWN"
    else:
        safe["status"] = "INVENTORIED"
    return safe

def detect_broad_rbac(bindings):
    findings = []
    for binding in bindings:
        if binding.get("role") == "cluster-admin" and not binding.get("approved", False):
            findings.append({
                "binding": binding.get("name", "UNKNOWN"),
                "status": "FAIL",
                "reason": "unexpected cluster-admin binding",
            })
    return findings
```

Tests: output contains only allowlisted metadata; injected
token/private-key fields never appear; missing owner/scope yields
`UNKNOWN`; unapproved cluster-admin binding is detected; approved
exception requires owner/reason/expiry. This fixture checker does not
read real kubeconfig files or secret objects.

### Hub credential review

Document: - each hub identity's purpose and scope; - clusters and
namespaces it can reach; - write verbs and sensitive resources it can
modify; - how the credential is issued, rotated, revoked, and audited; -
independent detection for policy/alert weakening; - emergency
break-glass owner and expiry; - recovery from a compromised Git
repository/controller.

A "read-only" credential should be tested with a harmless attempted
mutation that is denied. Do not test by changing production resources.

------------------------------------------------------------------------

# L4 --- Fleet operating model and governance

## 17. Operating model, governance metrics, and safe automation

### Ownership model

  -----------------------------------------------------------------------
  Role                                Accountabilities
  ----------------------------------- -----------------------------------
  Platform team                       Telemetry baseline, dashboard/rule
                                      templates, fleet identity contract,
                                      scanner and ring-gate
                                      implementation

  Regional/cluster owner              Local alert delivery, cluster
                                      inventory correctness, local
                                      conformance remediation

  Application/service owner           SLI semantics, runbooks,
                                      service-level dashboards, exception
                                      remediation

  Security/policy owner               Baselines, policy compatibility,
                                      RBAC review, exception approval,
                                      hub-compromise controls

  Data/ML owner                       Data freshness/replication
                                      visibility where applicable,
                                      artifact parity, model-serving
                                      readiness

  Incident commander                  Scope, communications, decision
                                      log, escalation, and post-incident
                                      follow-up

  Governance reviewer                 Exception expiry, access reviews,
                                      conformance trends, overdue
                                      remediation
  -----------------------------------------------------------------------

### Fleet governance metrics

-   Conformance score distribution **plus** critical-control failure
    count.
-   Time to detect and remediate non-conformance.
-   Percentage of clusters on supported Kubernetes versions, where
    support status is verified.
-   Telemetry coverage: expected clusters with fresh heartbeat / total
    expected clusters.
-   Percentage of clusters with validated alert routes.
-   Local-alert delivery success during central-hub outage tests.
-   Policy bundle/version parity and unexpected enforcement-mode
    changes.
-   Quarantine count, age, owner, expiry, and blocked promotions.
-   RBAC exceptions and credential rotation coverage.
-   Dashboard/rule drift and rollback frequency.
-   Telemetry series/log bytes/span volume by cluster and team.
-   SLO/error-budget attainment by region and global service.
-   Mean time to detect missing telemetry and critical policy bypass.

### Review cadence

-   **Daily/continuous:** critical alert delivery, hub availability,
    missing cluster heartbeat, critical conformance failure, policy
    bypass, and SLO burn.
-   **Weekly:** fleet health review, quarantines, stale reports, policy
    denial trends, GitOps drift, telemetry volume, and overdue
    remediation.
-   **Monthly:** access/credential review, policy exceptions,
    supported-version plan, dashboard/query cost, hub recovery tabletop
    actions.
-   **Quarterly or on major change:** hub-compromise tabletop, ring
    rollout design review, policy version compatibility, residency
    boundary changes, and exception expiry audit.

### Safe auto-remediation boundaries

Appropriate candidates may include opening a ticket, marking a cluster
quarantined, halting a ring, or reverting a clearly versioned
dashboard/rule change when a reviewed rollback condition is met.
Automatically deleting workloads, changing cluster-admin bindings,
rotating credentials, disabling policy, or promoting a region requires
stronger authorization and carefully tested controls.

For every automation define: - allowed actions and targets; - dry-run
mode; - preconditions and evidence freshness; - idempotency and
concurrency behavior; - rate limit/blast-radius bound; - human approval
threshold; - rollback and audit trail; - behavior when the hub/scanner
is unavailable.

### Multi-tenant and multi-cloud considerations

-   Use stable normalized identities while retaining provider-specific
    IDs as metadata.
-   Do not assume equivalent metrics, support windows, admission
    behavior, or policy report semantics across providers.
-   Use a capability matrix and mark controls `UNKNOWN` where inspection
    differs.
-   Separate tenant views/access boundaries; a central dashboard can
    leak metadata if datasources or folder permissions are too broad.
-   Data residency and telemetry retention apply to logs/traces/metrics
    and support access, not only application records.
-   Keep provider adapters narrow and tested; avoid a
    lowest-common-denominator abstraction that hides critical control
    differences.

## 18. Telemetry cardinality, volume, and cost model

### Local measurement plan

For each cluster, over the same fixed interval, record: - active
time-series count; - samples ingested or estimated sample rate; - log
bytes produced; - spans emitted/sampled if tracing is enabled; - local
storage growth; - central aggregation bytes and query latency; -
host/container CPU and memory.

Do not invent metric names from exporters. Use actual tool outputs or a
clearly documented measurement method. If a metric cannot be measured,
label it `UNKNOWN`.

### Transparent cost calculator

**\[ILLUSTRATIVE\]** Let: - (C) = cluster count; - (S) = average active
series per cluster; - (f) = samples per series per second; - (b) =
average stored bytes per sample including an assumed overhead factor; -
(L) = average log bytes per cluster per day; - (E) = fraction of
telemetry sent across the region/network boundary.

Then a rough raw sample volume/day is:

\[ V\_{`\text{samples/day}`{=tex}} = C `\times `{=tex}S `\times `{=tex}f
`\times 86400`{=tex} `\times `{=tex}b \]

A rough daily log volume is:

\[ V\_{`\text{logs/day}`{=tex}} = C `\times `{=tex}L \]

Estimated egress proxy:

\[ V\_{`\text{egress/day}`{=tex}} `\approx `{=tex}E
`\times `{=tex}(V\_{`\text{samples/day}`{=tex}} +
V\_{`\text{logs/day}`{=tex}}) \]

This is a model, not a bill. Compression, batching, indexes, retention,
replicas, protocol overhead, sampling, and provider billing definitions
can materially change actual cost. Use current region/service pricing
only when researched and dated; no cloud price is asserted here.

**Suggested in-document artifact: `telemetry_cost.py`**

``` python
def estimate(cluster_count, series_per_cluster, samples_per_second,
             bytes_per_sample, log_bytes_per_cluster_day, egress_fraction):
    values = (cluster_count, series_per_cluster, samples_per_second,
              bytes_per_sample, log_bytes_per_cluster_day)
    if any(v < 0 for v in values):
        raise ValueError("counts and sizes must be non-negative")
    if not 0 <= egress_fraction <= 1:
        raise ValueError("egress_fraction must be between 0 and 1")
    samples = cluster_count * series_per_cluster * samples_per_second * 86400 * bytes_per_sample
    logs = cluster_count * log_bytes_per_cluster_day
    total = samples + logs
    return {
        "sample_bytes_day": samples,
        "log_bytes_day": logs,
        "total_bytes_day": total,
        "egress_proxy_bytes_day": total * egress_fraction,
        "status": "ILLUSTRATIVE_ESTIMATE",
    }

if __name__ == "__main__":
    print(estimate(2, 10000, 1, 2, 100_000_000, 0.25))
```

The values above are only example inputs if run; they are not a measured
cost. Tests should cover zero clusters, increasing cluster count
linearly under fixed assumptions, invalid negative inputs, and egress
fractions outside `[0,1]`.

### Cost-control levers

-   Drop or aggregate unnecessary high-cardinality metrics at source.
-   Use recording rules for common summaries.
-   Sample traces according to an explicit policy.
-   Use structured logs with bounded retention and privacy controls.
-   Avoid debug logging as a permanent default.
-   Measure remote-write/collector queues and drops.
-   Separate critical security/audit telemetry from low-value debug
    data.
-   Keep local alert evaluation even if central export is throttled or
    unavailable.

## 19. Weekly fleet health review

Agenda: 1. Missing/unreachable clusters and telemetry heartbeat gaps. 2.
Worst-cluster and per-region SLO guardrails. 3. Critical conformance
failures and quarantines. 4. GitOps drift, ring status, and recent
changes. 5. Policy bundle version, enforcement mode, report freshness,
and denial rate. 6. RBAC exceptions, credential rotation, and hub access
scope. 7. Telemetry cardinality/volume and cost proxies. 8. Incidents,
false positives, and alert routing gaps. 9. Expiring exceptions and
overdue remediation. 10. Decisions, owners, due dates, and regression
tests.

A fleet average is not a substitute for the per-cluster list. Review any
missing evidence as an explicit action.

## 20. Production readiness checklist

-   [ ] All expected clusters have unique stable identities.
-   [ ] Required `cluster`, `region`, `env`, `tier`, `team` dimensions
    are validated.
-   [ ] High-cardinality labels are controlled and reviewed.
-   [ ] Per-cluster Prometheus/local alerting remains useful without the
    hub.
-   [ ] Central Grafana has both expected datasources and a cluster
    selector.
-   [ ] Fleet and worst-cluster dashboards show denominators and missing
    data.
-   [ ] Global SLO arithmetic uses summed eligible
    numerators/denominators.
-   [ ] Regional guardrails prevent the global average from hiding local
    failure.
-   [ ] `promtool` tests are run against the pinned version and retained
    as evidence.
-   [ ] `amtool` route tests cover critical routes, missing labels,
    null/default receiver, and grouping/inhibition.
-   [ ] Absent-cluster detection uses an expected inventory/heartbeat.
-   [ ] Hub-down drill proves local alerts still evaluate and deliver.
-   [ ] Dashboard definitions/rules are version-controlled with
    rollback.
-   [ ] OTel resource attributes align with the identity contract where
    enabled.
-   [ ] Conformance scanner reports PASS/FAIL/UNKNOWN/UNREACHABLE
    correctly.
-   [ ] Missing policy, unexpected admin binding, and outdated-version
    fixture are detected.
-   [ ] Unreachable or stale-evidence clusters cannot advance a ring.
-   [ ] Quarantine is rechecked immediately before promotion to avoid
    races.
-   [ ] One policy engine is selected and version compatibility is
    checked.
-   [ ] Policy rollout follows audit → warn → enforce, East then West.
-   [ ] Unexpected enforcement weakening and policy removal are
    independently detected.
-   [ ] Credential inventory exposes metadata only; no secret values are
    printed.
-   [ ] Hub credential scope, break-glass, rotation, and revocation are
    documented.
-   [ ] Telemetry cost/cardinality model states assumptions and
    unknowns.
-   [ ] Evidence contains timestamps, versions, context identity,
    results, cleanup, and owners.
-   [ ] No local lab result is misrepresented as real geographic or
    production proof.

------------------------------------------------------------------------

# Required labs

## 21. Shared safety contract

**⚠ LAB SIMULATION ONLY.** No production credentials, customer data,
shared cluster, or production kubeconfig. All mutating commands must use
explicit verified lab contexts. Use the actual cluster names from the
roadmap and `kubectl config`; examples are not authoritative.

Before each lab: 1. Record context mapping and tool versions. 2. Capture
baseline state and disk/memory use. 3. Identify exact target
namespace/component and stop procedure. 4. Set abort thresholds for
memory, disk, error rate, and unintended network effects. 5. Run one
change at a time. 6. Save expected versus observed results without
secrets. 7. Restore baseline and verify cleanup before moving to another
lab.

If an actual Unit 3 ring-advancer artifact is not supplied/readable, use
a fixture and state that the integration is simulated.

## 22. Lab 1 --- Two-cluster telemetry identity and central dashboard

**Profile:** Core. **Clusters:** East and West. **Destructive:** no,
except stopping throwaway components during cleanup.

**Goal:** show separate local telemetry and one central view with
correct identity.

**Steps** 1. Verify both contexts with `kubectl config get-contexts` and
`kubectl --context ... get nodes`. 2. Deploy/configure per-cluster
Prometheus with unique external labels, after pinning versions and
verifying syntax `[VERIFY]`. 3. Configure central Grafana with two
datasources and a cluster selector. 4. Deploy a tiny synthetic workload
that exposes a known counter/health signal. 5. Confirm a query
distinguishes East from West and dashboard panels identify the selected
cluster. 6. Run the identity validator with correct, missing, and
duplicate cluster IDs. 7. Save screenshots or query output with
credentials redacted.

**Positive tests:** both clusters visible and distinguishable.\
**Negative tests:** missing/duplicate `cluster` label fails the
validator; missing datasource fails dashboard validation.\
**Evidence:** context map, versions, configs, query output, validator
output.\
**Abort:** ambiguous context, wrong cluster identity, host resource
threshold breached.\
**Cleanup:** remove only the exact lab resources and verify both
contexts return to baseline.\
**Fidelity:** local clusters share one laptop and do not represent
geographic independence.

## 23. Lab 2 --- SLO arithmetic, recording rules, `promtool`

**Profile:** Extended. **Clusters:** both or synthetic rule fixture.
**Destructive:** no.

1.  Use the illustrative East/West counts in Section 10.
2.  Compute global success ratio from summed good/eligible events.
3.  Compute unweighted mean and explain why it is not the global request
    ratio.
4.  Author per-region and global recording/alert rules using actual lab
    metric names or clearly marked fixtures.
5.  Add `promtool` tests for numerator/denominator aggregation,
    averaging trap, zero denominator, missing data, and a deliberately
    broken expression.
6.  Run `promtool` only after verifying its version and test syntax
    **\[VERIFY\]**.
7.  Save rule/test files, command version, exit status, and outputs.

**Positive tests:** global ratio equals ratio-of-sums for fixture;
region guardrail catches bad region.\
**Negative tests:** zero denominator is not reported as 100%; missing
telemetry is not treated as healthy; deliberately broken rule fails.\
**Expected results:** illustrative only until executed.\
**Cleanup:** remove test rules from lab and verify deployed rules return
to baseline.\
**Fidelity:** rule tests do not prove production SLI semantics unless
the real event eligibility contract is correct.

## 24. Lab 3 --- Local/global alerts, routes, absent cluster, hub-down

**Profile:** Extended. **Clusters:** both. **Destructive:** stopping the
central throwaway component only.

1.  Configure local alerts and local receivers per cluster.
2.  Configure a central global alert and expected-cluster
    heartbeat/inventory.
3.  Add grouping/inhibition for a shared root cause without suppressing
    regional diagnosis.
4.  Use `amtool` route tests for critical routing, missing labels, new
    cluster with no route, and null/default receiver.
5.  Trigger a synthetic local alert in East and West and confirm local
    receiver evidence.
6.  Stop only the central hub/view/aggregator; trigger the synthetic
    alert again.
7.  Verify local evaluation/delivery continues and central cross-cluster
    view degrades as designed.
8.  Restore the hub and check data recovery/backfill only if the chosen
    components support it.

**Positive tests:** local alerts deliver during hub outage.\
**Negative tests:** absent cluster is unknown/unreachable; missing route
fails CI; hub-dependent local alert is identified as a failure.\
**Evidence:** alert state, receiver delivery, timestamps, `amtool`
output, hub stop/restore.\
**Abort:** stopping target cannot be identified with certainty.\
**Cleanup:** restore central components and verify local/central
baseline.\
**Fidelity:** simulated hub outage only exercises the configured path.

## 25. Lab 4 --- Cross-cluster logs/traces and correlation

**Profile:** Full optional; fallback is logs + metrics. **Clusters:**
both. **Destructive:** no.

1.  Apply cluster/region resource attributes to OTel configuration if
    selected.
2.  Generate an East-to-West synthetic request over the verified Unit 4
    path.
3.  If the full stack fits, verify both clusters appear in one trace
    with correct context propagation.
4.  If it does not fit, use structured logs with a synthetic correlation
    ID and metrics, and state that no distributed trace was captured.
5.  Correlate a change timestamp/Git revision with the event.
6.  Use synthetic timestamp offset for clock-skew discussion; do not
    alter host clock.
7.  Review sampling, retention, PII, and secret redaction.

**Positive tests:** identity and correlation fields consistent.\
**Negative tests:** missing cluster attribute is detected; trace absence
is not represented as proof of no request.\
**Evidence:** resource config, trace/log sample, correlation timeline,
sampling/retention settings.\
**Cleanup:** stop OTel/backend components and restore baseline.\
**Fidelity:** local trace path does not establish WAN trace reliability.

## 26. Lab 5 --- Conformance scanner and planted failures

**Profile:** Extended. **Clusters:** both or fixture. **Destructive:**
only controlled lab metadata/policy changes.

1.  Implement scanner checks for identity, telemetry baseline, PSS,
    default-deny NetworkPolicy capability, admission policy,
    cluster-admin bindings, signature policy where installed, audit
    logging, encryption status if inspectable, GitOps drift, and version
    inventory.
2.  Return PASS/FAIL/UNKNOWN/UNREACHABLE/NOT_APPLICABLE with timestamp
    and tool fingerprint.
3.  Plant a missing admission policy fixture.
4.  Plant an unexpected cluster-admin binding in a disposable lab or
    fixture.
5.  Represent an unsupported Kubernetes version with a fixture if safely
    changing a cluster version is impossible.
6.  Simulate an unreachable cluster and confirm it is never green.
7.  Produce JSON/YAML machine report plus a human summary and score.

**Positive tests:** compliant fixture passes; required checks have
evidence.\
**Negative tests:** three planted non-conformances detected; unreachable
is not green; unknown encryption status is not PASS.\
**Evidence:** input fixture, output report, tests, timestamps.\
**Cleanup:** restore policy/RBAC if changed; verify access.\
**Fidelity:** fixture detection does not prove live cluster inspection
correctness.

## 27. Lab 6 --- Quarantine and ring-advancer gate

**Profile:** Extended. **Clusters:** both or fixture. **Destructive:**
rollout blocked in fixture; no production ring.

1.  Inspect the actual Unit 3 ring-advancer artifact only if supplied
    and readable; otherwise document the contract fixture.
2.  Feed the conformance report into the gate.
3.  Test a fresh PASS report, FAIL report, quarantine, stale report,
    scanner outage, and unreachable cluster.
4.  Simulate quarantine arriving after selection; require a final
    atomic/revision-aware re-check immediately before promotion.
5.  Require evidence-backed remediation and approved review to clear
    quarantine.
6.  Confirm ring promotion does not proceed for blocked/unknown state.

**Positive tests:** fresh passing report can advance only when all other
gates pass.\
**Negative tests:** quarantined/unknown/unreachable clusters cannot
advance; scanner unavailable blocks.\
**Evidence:** gate inputs/outputs, race test, approval record fixture.\
**Cleanup:** reset fixtures and confirm no actual ring state was
changed.\
**Fidelity:** this is not a real Unit 3 integration unless the actual
interface is inspected and exercised.

## 28. Lab 7 --- Policy ring rollout, reports, version skew, bypass

**Profile:** Extended; one policy engine. **Clusters:** East then West.
**Destructive:** only disposable policy changes.

1.  Choose Kyverno or VAP according to available baseline and verify
    exact version/features **\[VERIFY\]**.
2.  Store one policy bundle in Git and record revision.
3.  Start in audit mode; inspect reports/freshness and false positives.
4.  Progress to warn after review; assign owners to violations.
5.  Enforce in East only after compatibility/rollback checks; verify
    denial rate and local policy state.
6.  Promote to West only if East health, policy version, report
    freshness, and conformance gates pass.
7.  Plant a version-skew fixture with unsupported policy capability;
    prove rollout halts before enforce/fan-out.
8.  Remove or weaken a policy in a fixture and verify independent bypass
    detection.
9.  Test rollback to last known-good bundle.

**Positive tests:** ring order and expected bundle version visible.\
**Negative tests:** bad policy halts rollout; unsupported field is
caught; unexpected mode weakening alerts; stale report blocks
promotion.\
**Evidence:** bundle revision, per-cluster status, report counts, denial
rates, alerts, rollback.\
**Cleanup:** restore approved baseline and confirm enforcement mode.\
**Fidelity:** local policy tests do not establish provider-managed
enforcement behavior.

## 29. Lab 8 --- RBAC-as-code and credential inventory

**Profile:** Extended. **Clusters:** both. **Destructive:** test only in
disposable lab.

1.  Define group-to-role mapping in code and apply through the selected
    GitOps workflow.
2.  Inventory credential metadata only: owner, purpose, scope, cluster
    reach, age/expiry where reliable.
3.  Ensure script output is allowlisted metadata; never read/print
    secret values.
4.  Plant an unapproved cluster-admin binding fixture and verify
    detection.
5.  Use a read-only role to attempt a harmless mutation in a disposable
    namespace and verify it is denied.
6.  Review hub credential scope, JIT elevation, break-glass
    owner/expiry, rotation and revocation.
7.  Document unknown fields rather than guessing.

**Positive tests:** approved least-privilege mapping passes.\
**Negative tests:** broad binding detected; read-only role cannot
mutate; token values are absent from output.\
**Evidence:** RBAC diff, safe inventory, denial output, review
checklist.\
**Cleanup:** revert lab binding and verify access baseline.\
**Fidelity:** metadata fixture does not prove the identity provider's
real token lifecycle.

## 30. Lab 9 --- Fleet incident and telemetry cost/cardinality

**Profile:** Extended. **Clusters:** both. **Destructive:** controlled
bad ring fixture only.

1.  Plant a safe synthetic rollout/config change that triggers a known
    alert in both clusters.
2.  Correlate alert timestamps with the Git/change timeline.
3.  Halt ring advancement, roll back, and communicate by region using
    M10 incident roles.
4.  Record actual local detection/rollback times as
    `[LOCAL LAB MEASUREMENT]`.
5.  Measure active series count, log bytes, spans if present, storage
    growth, and central export volume over a fixed interval.
6.  Use the cost calculator to model 2, 10, and 100 clusters under
    explicit assumptions.
7.  Triple the synthetic debug-log volume in the model and identify
    control levers.

**Positive tests:** incident is attributed to the change; ring halts;
rollback is verified.\
**Negative tests:** missing telemetry is not treated as recovery; local
times are not represented as cloud performance.\
**Evidence:** timeline, alert group, rollback revision, measurement
samples, assumptions.\
**Cleanup:** restore baseline config and stop generators.\
**Fidelity:** laptop metrics are not provider billing or production
scaling data.

## 31. Lab 10 --- Hub-compromise tabletop and governance review

**Profile:** Core tabletop; no live compromise. **Clusters:** conceptual
East/West. **Destructive:** no.

Scenario: an attacker or compromised automation identity can change
GitOps config, policy bundles, dashboards, alert routes, and possibly
credentials across both clusters.

Roles: incident commander, platform/SRE, security/policy owner,
application/data owner, communications lead.

1.  Map hub permissions to potential blast radius.
2.  Identify controls independent of the hub: local alert evaluation,
    per-cluster audit/evidence, external identity controls, immutable
    trusted source/backup, and separate break-glass access where
    available.
3.  Define containment: stop rollout/fanout, revoke/rotate credentials,
    isolate compromised controller, preserve audit logs, restore trusted
    source.
4.  Verify each cluster's policy and alert configuration independently
    before resuming operations.
5.  Define what telemetry becomes unavailable and how incident command
    operates without central dashboards.
6.  Produce a control matrix, prioritized remediation plan, owners, and
    deadlines.
7.  Conduct weekly fleet health review against Section 19.

**Positive tests:** every action has an owner and independent
verification.\
**Negative tests:** tabletop does not claim to prove live containment;
no credentials are exposed.\
**Evidence:** timeline, permission map, control matrix, decisions,
remediation backlog.\
**Cleanup:** tabletop only; close or assign all action items.\
**Fidelity:** discussion cannot prove incident performance under real
pressure.

------------------------------------------------------------------------

# Incident stories

## 32. Nine incident analyses

These are fictional teaching scenarios. They are not reports of actual
incidents.

### Incident 1 --- Global dashboard looks healthy while West is failing

-   **Symptom:** global success ratio looks acceptable; West has high
    error ratio.
-   **Evidence:** regional numerator/denominator, traffic distribution,
    last-seen, per-cluster query.
-   **Root cause:** team averaged percentages or reviewed only the
    global aggregate.
-   **Containment:** inspect regional guardrail and scope impact;
    communicate local failure.
-   **Durable fix:** ratio-of-sums for global SLI plus per-region
    guardrails and worst-cluster panels.
-   **Regression test:** skewed-traffic `promtool` fixture must catch
    the bad region.

### Incident 2 --- Central Prometheus down silences the fleet

-   **Symptom:** no central alerts and local alerts do not reach
    responders.
-   **Evidence:** local rule evaluation, receiver logs, hub dependency
    map, outage timeline.
-   **Root cause:** local alert path was routed through central
    query/receiver.
-   **Containment:** use local receiver/runbook; restore central view
    independently.
-   **Durable fix:** local evaluation and receiver path, tested hub-down
    drill.
-   **Regression test:** stop central hub and verify local alert
    delivery.

### Incident 3 --- Cluster disappears and global error ratio falls

-   **Symptom:** fleet metric improves after a scrape/remote-write
    outage.
-   **Evidence:** expected cluster inventory, heartbeat, `up`/scrape
    state, last-seen timestamp.
-   **Root cause:** absent telemetry was interpreted as zero errors.
-   **Containment:** mark cluster unknown/unreachable; halt rollout if
    conformance evidence is missing.
-   **Durable fix:** expected-cluster inventory comparison and heartbeat
    alert.
-   **Regression test:** removing a cluster's series cannot increase
    fleet confidence.

### Incident 4 --- Duplicate cluster label merges East and West

-   **Symptom:** dashboard panels show identical values or one cluster
    vanishes.
-   **Evidence:** label contract, external labels, raw series, config
    revisions.
-   **Root cause:** copied Prometheus configuration retained the same
    identity.
-   **Containment:** identify affected time window and correct labels;
    avoid over-interpreting merged history.
-   **Durable fix:** identity validator in CI and per-cluster inventory
    parity.
-   **Regression test:** duplicate identity fixture fails.

### Incident 5 --- New cluster alerts route to a null/default receiver

-   **Symptom:** rules fire but nobody receives them.
-   **Evidence:** route tests, receiver config, onboarding checklist,
    alert delivery status.
-   **Root cause:** cluster onboarding omitted route/owner validation.
-   **Containment:** use approved temporary route and verify delivery.
-   **Durable fix:** `amtool` route test and onboarding gate; no cluster
    marked ready until route passes.
-   **Regression test:** a cluster without a configured owner/receiver
    fails validation.

### Incident 6 --- Conformance scanner reports green after skipping unreachable cluster

-   **Symptom:** ring advances while one cluster has no fresh report.
-   **Evidence:** scan timestamps, reachability status, report
    completeness, ring decision log.
-   **Root cause:** skipped checks defaulted to success.
-   **Containment:** halt ring; mark cluster `UNREACHABLE` and not
    eligible.
-   **Durable fix:** explicit status model and fail-closed gate.
-   **Regression test:** unreachable cluster blocks advancement.

### Incident 7 --- Unsupported policy field causes inconsistent enforcement

-   **Symptom:** East enforces a rule while West does not, despite same
    Git revision.
-   **Evidence:** engine/API versions, policy schema, per-cluster
    resource status, report freshness.
-   **Root cause:** version-skew compatibility was not tested before
    rollout.
-   **Containment:** stop promotion, preserve current known-good policy,
    return to approved state.
-   **Durable fix:** capability matrix and compatibility gate before
    enforce mode.
-   **Regression test:** unsupported-feature fixture blocks rollout.

### Incident 8 --- Policy weakened and alert disabled by same hub

-   **Symptom:** critical policy is now audit/absent and no alert fired.
-   **Evidence:** Git audit, API audit logs, independent per-cluster
    policy state, controller identity.
-   **Root cause:** the hub controlled both policy and its only
    detector.
-   **Containment:** stop fanout, revoke compromised credentials,
    preserve evidence, independently inspect each cluster.
-   **Durable fix:** separate trust boundary and independent local
    verification/alert path.
-   **Regression test:** a local policy-mode mismatch is detected even
    when central dashboard is unavailable.

### Incident 9 --- Debug logging triples telemetry volume

-   **Symptom:** local disk/central ingestion/egress proxy rises
    sharply.
-   **Evidence:** bytes by cluster/service, log level change, series
    count, commit timeline.
-   **Root cause:** debug logging was enabled fleet-wide without a
    volume budget or ring gate.
-   **Containment:** halt ring, revert logging change, retain required
    incident evidence.
-   **Durable fix:** per-ring rollout, telemetry budget, short-lived
    debug policy, cardinality guard.
-   **Regression test:** cost/cardinality model and volume alert
    identify the increase before full rollout.

------------------------------------------------------------------------

# Hub-compromise tabletop

## 33. Control matrix

  ------------------------------------------------------------------------------------
  Threat          Possible impact   Independent        Evidence to     Recovery
                                    control            preserve        direction
  --------------- ----------------- ------------------ --------------- ---------------
  GitOps hub      Malicious rollout Ring gates,        Git audit,      Stop fanout;
  compromised     across all spokes per-cluster        controller      restore trusted
                                    review, least      identity,       source;
                                    privilege,         per-cluster     rotate/revoke
                                    break-glass        revisions       credentials

  Observability   Dashboard/alert   Local alerting,    Local alert     Isolate hub;
  hub compromised tampering or      separate access    state, access   verify local
                  telemetry         boundary, audit    audit,          rules
                  exfiltration      logs               configuration   independently
                                                       hashes          

  Policy weakened Admission bypass  Per-cluster policy Policy bundle   Halt rollout;
                  across fleet      state and          version, API    restore
                                    enforcement-mode   audit, report   approved bundle
                                    check              timestamps      

  Credential      Cross-cluster     Scoped identities, Credential      Revoke/rotate
  stolen          mutation          expiry/rotation,   metadata, auth  everywhere the
                                    audit              logs            credential was
                                                                       used

  Report tampered False green       Signed/versioned   Source report,  Re-run scanner
                  conformance score evidence or        timestamp, tool from trusted
                                    independent API    fingerprint     environment
                                    checks where                       
                                    available                          

  Alert route     Silent incident   Local receiver     Config          Restore route
  removed                           test, independent  revision, test  and prove
                                    route validation   output,         delivery
                                                       delivery        
                                                       records         
  ------------------------------------------------------------------------------------

### Tabletop decision flow

1.  Declare suspected hub compromise and stop further fanout.
2.  Identify credentials and clusters the hub can reach.
3.  Preserve Git/API/audit evidence before cleanup.
4.  Use independent per-cluster access to inspect policy, alerting, and
    workload revisions.
5.  Revoke/rotate affected credentials with an owner and explicit
    dependency inventory.
6.  Restore a trusted Git revision and verify every cluster separately.
7.  Keep rollout blocked until conformance reports are fresh and
    independently checked.
8.  Communicate known impact and uncertainty; do not equate restored
    dashboard with restored trust.
9.  Add regression controls and blameless review actions.

**Tabletop scoring (10 points):** blast-radius map (2); stop-fanout
decision (1); credential scope/rotation plan (2); independent
per-cluster verification (2); evidence preservation (1);
communication/owners (1); regression action (1). Score indicates
exercise completeness, not production readiness.

------------------------------------------------------------------------

# Evidence, governance, and review

## 34. Evidence bundle contract

Each lab evidence record should include: - timestamp and local
environment; - cluster/context identity; - tool versions or
`[VERIFY]`; - Git commit/config fingerprint if available; -
commands/tests run and actual return status; - relevant output snippets
with secrets redacted; - expected versus observed result; - abort,
rollback, and cleanup status; - follow-up issue and owner.

Suggested evidence layout:

``` text
evidence/
  inventory.txt
  versions.txt
  context-map.txt
  telemetry-label-contract.md
  lab-01/
    datasource-query-output.txt
    identity-validator-results.txt
  lab-02/
    slo-fixtures.yml
    promtool-version.txt
    promtool-results.txt
  lab-03/
    amtool-version.txt
    route-test-results.txt
    hub-down-timeline.md
  lab-04/
    trace-or-log-correlation.txt
  lab-05/
    conformance-report.json
    planted-failures.md
  lab-06/
    ring-gate-test-results.txt
  lab-07/
    policy-bundle-revision.txt
    per-cluster-policy-status.md
  lab-08/
    credential-metadata-inventory.json
    rbac-test-results.txt
  lab-09/
    telemetry-volume.csv
    cost-model-assumptions.md
  lab-10/
    tabletop-control-matrix.md
  cleanup-verification.txt
  manifest.sha256
```

These are suggested filenames, not evidence that the files exist. A
hashed manifest can help detect later file changes; it does not prove
that observations were true or complete. Do not claim a manifest was
generated unless hashing was actually run.

## 35. Governance exception record

Every exception should include: - unique ID; - affected cluster(s),
control, and scope; - reason and business owner; - security/platform
approver; - compensating control; - start and expiry time; - review
cadence; - evidence required to close; - whether rollout eligibility is
affected; - audit trail of creation, renewal, and closure.

No permanent exception should exist merely because remediation is
inconvenient. Expired exceptions should alert and follow the declared
policy; do not silently extend them.

## 36. Runbook snippets

### A. Missing cluster telemetry

**Trigger:** heartbeat is older than the declared freshness threshold or
expected cluster is absent.

1.  Verify inventory and cluster identity.
2.  Check local Prometheus/agent health through the cluster's local
    path.
3.  Compare last scrape, network path, collector queues, and recent
    changes.
4.  Mark health as `UNKNOWN/UNREACHABLE`; do not infer zero errors.
5.  Halt ring advancement if fresh conformance evidence is required.
6.  Restore collection and confirm new timestamp/series before marking
    healthy.
7.  Record the missing interval and downstream dashboards/alerts
    affected.

### B. Fleet SLO breach hidden by aggregate

**Trigger:** regional guardrail fails while global aggregate appears
healthy.

1.  Check numerator, denominator, eligibility, and missing-data state.
2.  Compare per-region and per-cluster panels.
3.  Confirm global ratio uses summed numerator/denominator.
4.  Inspect shared dependency, recent rollout, and alert grouping.
5.  Contain by region; do not suppress local diagnosis because global
    SLO is acceptable.
6.  Communicate scope and evidence.
7.  Add a regression test if the dashboard/rule hid the issue.

### C. Policy mode mismatch or quarantine

**Trigger:** enforcement mode differs from declared mode, report is
stale, or cluster is quarantined.

1.  Block ring advancement.
2.  Confirm cluster identity and evidence freshness.
3.  Inspect policy bundle/version and audit trail independently of
    central status.
4.  Preserve current known-good revision and report.
5.  Assign owner and remediation; do not clear quarantine without fresh
    evidence and approved review.
6.  Re-run conformance and policy checks.
7.  Re-check eligibility immediately before ring promotion.

### D. Suspected hub compromise

Follow the tabletop sequence in Section 33. Stop fanout, preserve
evidence, isolate/revoke credentials through the approved process,
independently inspect each cluster, restore trusted source, and keep
rollout blocked until verification passes.

------------------------------------------------------------------------

# Knowledge checks and answer key

## 37. Questions

Scoring: **80% or higher:** proceed while retaining open risks;
**60--79%:** remediate weak areas and repeat related labs; **below
60%:** repeat the unit and labs. Quiz performance is not proof of
production readiness.

Each answer includes the core rationale and a common wrong answer to
avoid.

### Q01 --- L1, concept: Why does fleet visibility require an expected-cluster inventory?

**Objective:** distinguish missing telemetry from healthy service.\
**Model answer:** an inventory identifies which clusters should report;
without it, absent series may be mistaken for zero errors or a smaller
healthy fleet.\
**Common wrong answer:** "If no errors are reported, the cluster is
healthy." That confuses absence of evidence with evidence of health.

### Q02 --- L1, multiple choice: Which dimension must be unique across clusters?

A. `request_id`\
B. `cluster`\
C. Raw URL\
D. Exception message

**Answer:** B. `cluster` is the stable source identity.\
**Distractors:** A, C, and D are high-cardinality/unbounded values and
should not be metric identity labels.

### Q03 --- L1, concept: What is the difference between an OTel resource attribute and a Prometheus label?

**Objective:** understand signal identity mapping.\
**Model answer:** a resource attribute describes the telemetry-producing
entity in OTel; Prometheus labels identify a time series.
Exporter/backend mappings and indexing are implementation-specific.\
**Common wrong answer:** "They are automatically identical in every
backend." Mapping must be verified.

### Q04 --- L1, multiple choice: Which is a safe default metric label?

A. Unique user ID\
B. Full URL including query string\
C. Bounded `region`\
D. Arbitrary exception string

**Answer:** C.\
**Distractors:** A, B, and D can create unbounded cardinality and
privacy risk.

### Q05 --- L1, concept: Why are per-cluster alerts needed if central Grafana exists?

**Model answer:** the central UI/query layer can fail; local alert
evaluation and receiver paths should remain useful independently.\
**Common wrong answer:** "Grafana is the alert authority." A
visualization UI is not a substitute for a resilient alert path.

### Q06 --- L1, architecture: Name the six aggregation approaches.

**Model answer:** multi-datasource Grafana, Prometheus federation,
remote-write to central store, sidecar/object-store global query,
central OTel Collector gateway, and vendor SaaS.\
**Common wrong answer:** "They all provide the same central Prometheus."
They differ in data path, freshness, storage, cost, and failure
behavior.

### Q07 --- L2, scenario: Two clusters share the same `cluster` label. What can break?

**Model answer:** series can merge/be ambiguous; alert grouping,
per-cluster dashboards, attribution, and conformance may be wrong.
Validate uniqueness and fix source labels.\
**Common wrong answer:** "Only the dashboard title is wrong." The
identity error can affect alerting and incident decisions.

### Q08 --- L2, arithmetic: East has 99,900/100,000 good requests; West has 600/1,000. What is the global success ratio?

**Model answer:**
((99,900+600)/(100,000+1,000)=100,500/101,000`\approx99.50495`{=tex}%).\
**Common wrong answer:** average 99.9% and 60% to get 79.95%. That is
not the global request ratio when traffic differs.

### Q09 --- L2, scenario: Global SLO is acceptable but West has 40% errors on low traffic. What should you inspect?

**Model answer:** per-region guardrail, numerator/denominator, traffic
volume, missing telemetry, worst-cluster view, and recent changes. A
global SLO does not erase regional impact.\
**Common wrong answer:** "Do nothing because global SLO passes." The
regional guardrail exists to prevent that blind spot.

### Q10 --- L2, rule test: What should a zero denominator mean?

**Model answer:** undefined/no eligible data, represented explicitly
according to the SLI contract; never automatically 100% success.\
**Common wrong answer:** divide by zero or default to 100%. That creates
false health.

### Q11 --- L2, tool interpretation: What evidence is needed before claiming `promtool` tests passed?

**Model answer:** actual pinned tool version, command, fixture/rule
files, exit status, output, and timestamp.\
**Common wrong answer:** "The test file exists, so tests passed."
Authored test definitions are not execution evidence.

### Q12 --- L2, scenario: Central Prometheus is down. What must still work?

**Model answer:** local telemetry and local alert evaluation/receiver
path should still operate; central queries may degrade. Verify by
triggering a safe local alert while the hub is stopped.\
**Common wrong answer:** "The local cluster is healthy because central
is down." Health is unknown until local evidence is checked.

### Q13 --- L2, multiple choice: A cluster vanishes from the global metric and error ratio falls. What is the correct interpretation?

A. Service improved\
B. Treat absent telemetry as zero errors\
C. Mark missing/unknown and inspect heartbeat/inventory\
D. Delete the cluster from inventory

**Answer:** C.\
**Distractors:** A and B infer health from missing data; D hides the
failure and corrupts expected fleet scope.

### Q14 --- L2, scenario: New cluster alerts route to a null/default receiver. What should have caught it?

**Model answer:** onboarding validation and `amtool` route tests plus a
required owner/receiver contract.\
**Common wrong answer:** "Wait for the first incident." Route readiness
is a precondition.

### Q15 --- L2, logs/traces: Why should request IDs not be metric labels?

**Model answer:** they are unbounded and create high cardinality; use
approved log/trace fields instead.\
**Common wrong answer:** "More labels always improve debugging."
Cardinality and privacy costs can make telemetry unusable.

### Q16 --- L2, trace fallback: What if the Full OTel profile exceeds laptop resources?

**Model answer:** explicitly use logs and metrics with a synthetic
correlation ID, mark tracing optional, and do not claim a distributed
trace was captured.\
**Common wrong answer:** claim trace success from an architecture
diagram.

### Q17 --- L3, scanner: How should an unreachable cluster be reported?

**Model answer:** `UNREACHABLE` or `UNKNOWN`, not PASS; it must not
advance a rollout unless an explicitly approved exception permits it.\
**Common wrong answer:** skip it and compute a green score from
remaining clusters.

### Q18 --- L3, scenario: Scanner cannot inspect encryption-at-rest state. What is the result?

**Model answer:** `UNKNOWN` with the reason/evidence gap. Only use
`NOT_APPLICABLE` if policy explicitly defines the scope and exception.\
**Common wrong answer:** assume encryption is enabled because the
provider usually enables it.

### Q19 --- L3, scenario: A missing admission policy is planted in East. What should the scanner and ring gate do?

**Model answer:** scanner returns FAIL; cluster becomes
ineligible/quarantined under policy; ring advancer blocks and records
evidence.\
**Common wrong answer:** allow promotion because West is compliant.

### Q20 --- L3, scenario: Quarantine is added after the ring advancer selected a cluster. What race control is required?

**Model answer:** re-check eligibility atomically/immediately before
promotion or use a versioned decision/lease invalidated by quarantine.\
**Common wrong answer:** check quarantine only at selection time.

### Q21 --- L3, policy rollout: Why audit → warn → enforce?

**Model answer:** it surfaces scope/false positives and gives owners
time to remediate before denial begins. Enforce only after
compatibility, exception, and rollback checks.\
**Common wrong answer:** start enforce everywhere to achieve consistency
quickly.

### Q22 --- L3, version skew: A policy field is unsupported by West. What should happen?

**Model answer:** compatibility gate detects it before enforce/fanout;
stop rollout and preserve known-good policy. Exact behavior must be
tested for the selected engine/API version.\
**Common wrong answer:** assume unsupported fields always fail loudly.

### Q23 --- L3, bypass: Policy changes from enforce to audit without approval. What detects it?

**Model answer:** per-cluster declared-versus-observed mode comparison,
API audit, bundle version/drift, and an independent alert path not
controlled solely by the hub.\
**Common wrong answer:** trust the GitOps hub's own green status.

### Q24 --- L3, RBAC: Why is hub cluster-admin access to all spokes dangerous?

**Model answer:** hub compromise can become fleet-wide
control-plane/workload/policy compromise. Minimize scope, separate
identities, audit, rotate/revoke, and verify each cluster
independently.\
**Common wrong answer:** "The hub is internal, so it is trusted."

### Q25 --- L3, credential inventory: What should the script output?

**Model answer:** allowlisted metadata such as owner, purpose, scope,
cluster reach, and reliable age/expiry; secret/token/private-key values
must never be printed. Unknown metadata remains UNKNOWN.\
**Common wrong answer:** dump full kubeconfigs to make the inventory
complete.

### Q26 --- L3, policy reports: Which fields are useful to aggregate?

**Model answer:** cluster, policy, severity, enforcement mode,
result/status, timestamp/freshness, and denial/violation counts, with
product-specific APIs verified.\
**Common wrong answer:** one fleet-wide count without cluster identity
or freshness.

### Q27 --- L4, incident: Hub is down during a fleet incident. How do responders proceed?

**Model answer:** use local alerting and local telemetry, verify
per-cluster context, preserve local evidence, communicate uncertainty,
and restore central visibility independently.\
**Common wrong answer:** wait for central dashboards before diagnosing
any cluster.

### Q28 --- L4, hub compromise: The same hub can change policy and disable its alert. What controls help?

**Model answer:** independent per-cluster verification, separate trust
boundary/identity, external audit trail, least privilege, local
alerting, and a trusted-source recovery procedure.\
**Common wrong answer:** rely on the same hub's own alert to prove it is
safe.

### Q29 --- L4, cost: Debug logging triples telemetry volume. What should happen?

**Model answer:** correlate with change, measure bytes/series by
cluster, halt the ring/revert if thresholds breached, preserve required
evidence, and add budget/cardinality guardrails. Do not equate local
volume with cloud bill.\
**Common wrong answer:** delete logs without retention/privacy review or
leave debug enabled indefinitely.

### Q30 --- L4, auto-remediation: Which action is safer to automate first?

A. Delete a cluster's workloads\
B. Rotate all production credentials without coordination\
C. Halt a rollout and open an incident/ticket when a critical gate
fails\
D. Disable policy to restore availability

**Answer:** C.\
**Distractors:** A and B have large blast radius and need strong
approvals; D weakens controls and may conceal compromise.

### Q31 --- L4, multi-cloud: Why normalize identity but retain provider-specific metadata?

**Model answer:** common labels enable fleet comparison, while
provider-specific capabilities/IDs are needed to preserve semantics and
diagnose platform differences.\
**Common wrong answer:** erase provider differences into one generic
field and assume behavior is identical.

### Q32 --- L4, SLO design: Why keep regional guardrails when a global SLO is weighted correctly?

**Model answer:** a global ratio can be dominated by high-volume regions
and hide serious low-volume regional degradation.\
**Common wrong answer:** a correct global arithmetic ratio makes
regional SLOs unnecessary.

### Q33 --- L4, evidence: Does a hashed evidence bundle prove the observations are true?

**Model answer:** no; it can detect later file changes relative to the
manifest, but does not prove source truth, completeness, or correct
collection.\
**Common wrong answer:** treat a hash as proof that a measurement is
accurate.

### Q34 --- L4, production readiness: Do passing local tests prove multi-region resilience?

**Model answer:** no; local kind clusters share host/network/power and
cannot prove geographic independence, real WAN behavior, or provider
routing.\
**Common wrong answer:** "Two cluster names equal two regions."

### Q35 --- L4, design review: What conditions are needed before auto-promoting a policy ring?

**Model answer:** fresh conformance, correct cluster identity,
compatible engine/API, expected bundle/mode, no quarantine, passing
local health and alert routes, approved exception handling, rollback
plan, and final eligibility re-check.\
**Common wrong answer:** promote when Git sync says successful,
regardless of local evidence.

### Q36 --- L4, incident: Central global SLO rule is healthy but one region's telemetry is stale. What should the incident commander say?

**Model answer:** global state is incomplete/uncertain; region is
unknown until freshness is restored. Do not claim the SLO is met without
evidence.\
**Common wrong answer:** report green because the global
numerator/denominator still calculates.

### Q37 --- L4, policy exception: What makes an exception governable?

**Model answer:** owner, reason, narrow scope, compensating control,
start/expiry, approver, review cadence, evidence to close, and audit
trail.\
**Common wrong answer:** indefinite exception without owner or expiry.

### Q38 --- L4, cross-unit boundary: What does Unit 8 do with M14 Unit 3?

**Model answer:** integrate conformance quarantine with the ring
advancer using the actual interface if inspected; otherwise use a
clearly labelled contract fixture. It does not claim to reimplement or
have inspected missing sibling artifacts.\
**Common wrong answer:** assume a file/controller exists and claim a
working integration.

### Q39 --- L4, governance: Which fleet metric should never be used alone?

**Model answer:** a single weighted conformance score or fleet average;
pair it with per-cluster drill-down and hard gates for critical
controls.\
**Common wrong answer:** optimize one aggregate score while critical
failures remain.

### Q40 --- L4, senior design: Describe the first five actions after detecting unexpected enforcement-mode weakening.

**Model answer:** block ring/fanout; preserve independent evidence;
verify per-cluster policy state and identity; inspect change/audit trail
and hub credential scope; restore approved policy through a trusted path
only after scope and authority are understood. Then test alerting and
assign regression work.\
**Common wrong answer:** immediately overwrite the policy from the
potentially compromised hub without preserving evidence.

## 38. Answer review rubric

-   **80--100%:** proceed to the next M14 unit while tracking unresolved
    `[VERIFY]` items and operational gaps.
-   **60--79%:** remediate weak areas and repeat the corresponding labs.
-   **Below 60%:** repeat the unit and all relevant labs.
-   Any wrong answer that treats unreachable/missing telemetry as
    healthy, prints secrets, bypasses fencing/approval, or advances a
    non-conformant cluster is a **critical safety gap** regardless of
    score.

Quiz performance does not establish production readiness. Production
readiness requires verified target-version semantics, safe test
evidence, access review, and rehearsed operations.

## 39. Glossary

-   **Alert inhibition:** suppressing a derivative alert when a declared
    root-cause alert is active and matching conditions hold.
-   **Cardinality:** number of unique label combinations/time series;
    high cardinality can increase memory, storage, and query cost.
-   **Conformance:** evidence that a cluster meets a declared baseline.
-   **External label:** label added to outgoing Prometheus series in
    supported paths; exact semantics are version/path-specific.
-   **Federation:** central Prometheus scrapes selected series from
    another Prometheus endpoint.
-   **Fleet:** a set of clusters managed under common inventory,
    standards, and governance.
-   **Global SLI:** service indicator aggregated over its defined
    eligible event population.
-   **Hub:** central management/observability/GitOps component; a
    high-value dependency that needs its own failure and security plan.
-   **Inhibition:** alert rule that suppresses selected alerts based on
    another alert's presence.
-   **JIT access:** just-in-time privilege elevation with bounded
    duration and audit.
-   **Quarantine:** state preventing a cluster from advancing through a
    rollout until reviewed evidence clears it.
-   **Recording rule:** precomputes a Prometheus expression into a time
    series.
-   **SLO:** target for a defined service-level indicator over a time
    window.
-   **Unknown:** evidence insufficient to classify a control as pass or
    fail; must not silently count as pass.
-   **Worst-cluster view:** dashboard exposing the most degraded
    cluster/region rather than only fleet average.
-   **Ring advancer:** mechanism that promotes a rollout from one
    bounded group of clusters to the next based on gates.

## 40. Verification notes and sources

**Source verification status:** live official documentation was not
consulted during this authoring pass. The URLs below are canonical entry
points, not a claim that a specific page/version was reviewed on
2026-10-29. Verify exact syntax, support, APIs, and semantics before
execution.

-   Prometheus documentation: https://prometheus.io/docs/
-   Prometheus configuration:
    https://prometheus.io/docs/prometheus/latest/configuration/configuration/
-   Prometheus recording/alerting rules:
    https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/
-   Prometheus rule testing:
    https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/
-   Alertmanager documentation:
    https://prometheus.io/docs/alerting/latest/alertmanager/
-   Grafana documentation: https://grafana.com/docs/grafana/latest/
-   OpenTelemetry documentation: https://opentelemetry.io/docs/
-   Kubernetes RBAC:
    https://kubernetes.io/docs/reference/access-authn-authz/rbac/
-   Kubernetes Pod Security Standards:
    https://kubernetes.io/docs/concepts/security/pod-security-standards/
-   Kubernetes admission control:
    https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/
-   Argo CD documentation: https://argo-cd.readthedocs.io/
-   Kyverno documentation: https://kyverno.io/docs/
-   Kubernetes ValidatingAdmissionPolicy:
    https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/
-   kind documentation: https://kind.sigs.k8s.io/

Items to verify: 1. Prometheus external-label, federation, remote-write,
rule syntax, and `promtool` test schema for the pinned version. 2.
Alertmanager grouping/inhibition/matcher syntax and `amtool` route-test
syntax for the pinned version. 3. Grafana datasource
provisioning/dashboard schema and variable behavior. 4. OTel semantic
conventions, Collector queue/backpressure/exporter behavior, and
trace-context propagation for selected versions. 5. Kubernetes version
support window and availability of encryption/audit configuration
evidence in the selected environment. 6. Argo CD/ApplicationSet
ring-advancer interface and concurrency semantics; actual Unit 3
artifact was not independently inspected here. 7. Kyverno or VAP feature
compatibility and policy-report API for the selected version. 8. Any
named exporter metrics, policy-report metrics, dashboard API fields, or
provider-specific credential metadata. 9. Actual kind cluster
names/context mapping and the footprint of chosen components.

## 41. Roadmap Alignment and Authenticity Audit

This audit compares the authored lesson with the supplied Unit 8 prompt.
The attached roadmap excerpt includes the Stage 2E constraints and M14
sibling names, but the complete `Roadmap_ptree.md` was not supplied
under that exact filename in the available files; a related roadmap tree
excerpt was supplied and read. The primary M14 syllabus attachment was
partially inspected, not independently verified line-by-line in full.
Therefore, repository alignment is based on the target path and sibling
list explicitly stated in the Unit 8 prompt plus the readable roadmap
excerpt.

  -------------------------------------------------------------------------------------------------------------------
  Requirement                                   Status                   Evidence          Notes/follow-up
                                                (PASS/PARTIAL/BLOCKED)   section(s)        
  --------------------------------------------- ------------------------ ----------------- --------------------------
  Exact target filename/path and one artifact   PASS                     Metadata          Target filename/path
  only                                                                                     stated; no repository file
                                                                                           modified.

  Verbatim M11/M12 handoff                      PASS                     Section 1         Included exactly as
                                                                                           supplied.

  Fleet visibility and all signal types         PASS                     Section 3         Incident-first workflow
                                                                                           included.

  Required identity dimensions/cardinality      PASS                     Section 4         Validator concept and
                                                                                           negative cases included.

  Six aggregation patterns compared             PASS                     Section 5         Trade-offs and hub/local
                                                                                           behavior included.

  Hub-failure principle and drill               PASS                     Section 6; Lab 3  Procedure authored; not
                                                                                           executed.

  Two Prometheus instances, unique labels,      PARTIAL                  Sections 7--8;    Config patterns included;
  Grafana two datasources/selector                                       Lab 1             actual deployment not run;
                                                                                           placeholders require
                                                                                           version/topology
                                                                                           verification.

  Resource profiles and laptop constraints      PASS                     Section 7         Core/Extended/Full staged
                                                                                           plan included.

  Dashboards as code and validator              PARTIAL                  Section 9; Lab 1  Simplified fixture
                                                                                           validator included; not a
                                                                                           real Grafana schema/API
                                                                                           validator and not
                                                                                           executed.

  Global/per-region SLO arithmetic and          PASS                     Section 10; Lab 2 Worked illustrative
  averaging trap                                                                           example and
                                                                                           denominator/missing-data
                                                                                           caveats included.

  Prometheus rules and `promtool` tests         PARTIAL                  Section 10; Lab 2 Rule/test design
                                                                                           described; exact syntax
                                                                                           `[VERIFY]`; not executed.

  Local/global alerting, absent-cluster,        PARTIAL                  Section 11; Lab 3 Fixture and required tests
  grouping/inhibition, `amtool`                                                            included; exact CLI/config
                                                                                           version `[VERIFY]`; not
                                                                                           executed.

  Cross-cluster traces or explicit logs/metrics PASS                     Section 12; Lab 4 Full trace optional; no
  fallback                                                                                 trace capture claimed.

  Fleet conformance baseline checks             PARTIAL                  Section 13; Lab 5 Fixture scanner covers
                                                                                           status logic; no live
                                                                                           Kubernetes integration.
                                                                                           Some controls require
                                                                                           provider-specific
                                                                                           evidence.

  Three planted non-conformances                PARTIAL                  Section 13; Lab 5 Scenarios/tests specified;
                                                                                           not actually planted in a
                                                                                           cluster.

  Unreachable cluster never green               PASS                     Sections 13--14;  Explicit
                                                                         Labs 5--6         UNKNOWN/UNREACHABLE and
                                                                                           fail-closed rules.

  Quarantine/ring advancer integration          PARTIAL                  Section 14; Lab 6 Contract fixture included;
                                                                                           actual Unit 3 artifact not
                                                                                           inspected/integrated.

  Policy rings audit → warn → enforce, East     PASS                     Section 15; Lab 7 Procedure authored; not
  then West                                                                                executed.

  Policy report aggregation/denial              PARTIAL                  Section 15; Lab 7 Normalizer fixture
  rates/version skew/bypass                                                                included; engine-specific
                                                                                           semantics `[VERIFY]`; not
                                                                                           executed.

  RBAC-as-code and metadata-only credential     PARTIAL                  Section 16; Lab 8 Safe fixture checkers
  inventory                                                                                included; no real
                                                                                           credential inventory or
                                                                                           live RBAC application
                                                                                           performed.

  Governance metrics, review cadence, safe      PASS                     Sections 17--19   M15/M16 forward references
  auto-remediation, multi-cloud                                                            included.

  Telemetry cost/cardinality calculator         PASS                     Section 18; Lab 9 Assumptions transparent;
                                                                                           values illustrative, no
                                                                                           billing claims.

  Ten lab packages with                         PASS                     Sections 22--31   Authored but not executed.
  steps/tests/evidence/abort/cleanup/fidelity                                              

  Nine incident stories                         PASS                     Section 32        Explicitly fictional.

  Hub-compromise tabletop/control matrix        PASS                     Section 33; Lab   Tabletop only; no live
                                                                         10                compromise.

  Evidence manifest/checklist                   PASS                     Sections 20,      Suggested bundle only; not
                                                                         34--35            created or hashed.

  At least 30 knowledge checks and answers      PASS                     Sections 37--38   40 questions with
                                                                                           answers/common wrong
                                                                                           answers included.

  Verification sources with titles/URLs/review  PARTIAL                  Section 40        Canonical entry points
  date                                                                                     listed; live docs not
                                                                                           consulted, so no
                                                                                           page-level review date
                                                                                           claimed.

  Full exact repository tree and sibling        PARTIAL                  Section 41        Related roadmap excerpt
  content verified                                                                         inspected; exact
                                                                                           `Roadmap_ptree.md` and all
                                                                                           siblings not independently
                                                                                           verified in full.

  Code and automated tests executed             BLOCKED                  Sections 4,       Code is illustrative and
                                                                         9--10, 13--16, 18 unexecuted.

  Real cluster, policy, alert-route, or         BLOCKED                  Labs 1--10        No resources were deployed
  hub-down tests executed                                                                  or mutated.

  No other repository files modified            PASS                     Metadata          One standalone Markdown
                                                                                           artifact created;
                                                                                           repository not changed.
  -------------------------------------------------------------------------------------------------------------------

### Final trust statement

This is a complete teaching artifact and lab plan, not a verified
production implementation. Official documentation was not consulted
live; version-sensitive behavior is marked `[VERIFY]` or called out for
follow-up. The scripts/configuration snippets are illustrative and were
not executed. No cluster, Prometheus, Grafana, Alertmanager, OTel
backend, policy engine, RBAC binding, or ring advancer was deployed or
changed. The actual Unit 3 integration was not performed because its
artifact was not independently inspected. Local kind clusters on one
laptop do not prove geographic independence or production-scale
behavior, and absence of anomalies in a lab is not proof of correctness.

**Overall status: PASS for authored curriculum coverage; PARTIAL for
configuration and repository integration verification; BLOCKED for live
execution and source-version verification.**
