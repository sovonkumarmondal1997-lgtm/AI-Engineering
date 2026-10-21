# Cost Modeling, Unit Economics and FinOps

## 1. Purpose, scope, and learning outcomes

### Purpose

This lesson teaches how to translate workload and architecture choices into a transparent cost model, compare alternatives fairly, explain unit economics, allocate shared spend, and govern optimisation through FinOps practices. The goal is not to predict an exact invoice without evidence. The goal is to make assumptions visible, quantify consequences, identify uncertainty, and create a model that can later be reconciled with actual usage and bills.

The module roadmap frames Topic 06 as the point where the capacity and design choices developed in earlier topics are priced. It expects consistent units and assumptions, reproducible arithmetic, sensitivity analysis, and no invented prices. This lesson follows that scope.

### Scope and pricing caution

All monetary amounts, unit prices, discounts, thresholds, and workload quantities in worked examples are **illustrative placeholders**. They are not current market prices, vendor quotes, benchmarks, or savings claims. Real prices vary by provider, region, service, contract, commitment, usage tier, currency, tax treatment, and time. Replace placeholders with dated, sourced prices before using a model for a procurement or production decision.

No cloud account, production telemetry, or billing records are assumed to be available. The methods work with explicit hypothetical inputs and can be populated with actual evidence later.

### Learning outcomes

By the end, you should be able to:

1. Explain how workload, architecture, resource consumption, pricing units, and operational choices combine to create cost.
2. Distinguish fixed, variable, direct, indirect, recurring, usage-based, committed, and step costs.
3. Build a cost-driver inventory for compute, storage, memory, requests, transfer/egress, orchestration, logging, monitoring, licences, and people.
4. Convert capacity and workload forecasts into monthly and annual cost estimates.
5. Compare low, expected, and high demand scenarios without changing assumptions silently.
6. Calculate average, marginal, incremental, and business-unit costs with explicit denominators.
7. Design a cost allocation and showback approach for shared platform resources.
8. Evaluate reserved/committed capacity against flexible consumption using break-even and utilisation assumptions.
9. Model retention, replication, redundancy, compute sizing, scheduling, caching, materialisation, and data-transfer trade-offs.
10. Use FinOps practices for ownership, budgets, forecasting, variance analysis, anomaly response, and optimisation governance.
11. Identify uncertainty, sensitivity, model exclusions, and risks to performance, reliability, security, and governance.
12. Produce the cost model, scenario table, unit-economics analysis, allocation proposal, sensitivity analysis, and optimisation register expected by the roadmap.

### Core principle

A cost model is a structured estimate, not a bill and not proof of savings. A credible model makes the chain explicit:

**business workload → resource demand → resource consumption → pricing units → cost → unit economics → decision and validation plan.**

A cheaper design is not acceptable if it fails a required latency, throughput, freshness, reliability, security, residency, or recovery objective.

---

## 2. Prerequisites and connections to earlier topics

The module roadmap specifies Topic 06 prerequisites as **Sequence 1, Sequence 4, Sequence 5, and P6**.
In the roadmap table notation, the prerequisite entry is **`Seq 1, 4, 5; P6`**.

- **Sequence 1 — Capacity planning and growth forecasting:** demand volumes, peak factors, headroom, and low/expected/high growth assumptions.
- **Sequence 4 — Scaling, partitioning, sharding, and hotspots:** how scaling choices, skew, replication, and shard count affect resource requirements and cost.
- **Sequence 5 — Caching, materialisation, and serving trade-offs:** hit ratio, miss-path load, refresh compute, materialised storage, and freshness constraints.
- **P6 — Cloud cost drivers:** compute, storage, requests, transfer, regions, and egress. The roadmap identifies P6 as a prerequisite provided by the cloud/hybrid/multi-cloud architecture module. If that prior material is unavailable, use the driver explanations in this lesson as a minimum recap rather than assuming the prerequisite has been completed.

### Connection to Topic 01: capacity planning

Topic 01 provides the workload forecast and capacity envelope. Cost modelling should use the same workload units, time window, peak assumptions, and scenarios. If the capacity forecast says 600 million events per month, the cost model must not silently price 600 million events per day.

### Connection to Topic 04: scaling and hotspots

Partition count, replication, sharding, hot-key mitigation, and capacity headroom change the resource footprint. Scaling out may improve throughput or fault isolation while increasing baseline nodes, cross-partition coordination, storage copies, or data movement. Cost must be compared at a workload that meets the performance objective, not at an artificially under-provisioned configuration.

### Connection to Topic 05: caching and materialisation

Caching can trade memory and operational complexity for fewer backend requests. Materialisation can trade refresh compute and storage for less repeated query compute. Cost modelling must include both sides: avoided work is not a saving unless the cost of maintaining the alternative is included and correctness/freshness remains acceptable.

### Connection to Topic 07: performance testing and capacity validation

The cost model predicts resource use and spend; Topic 07 tests whether the planned capacity actually meets performance and reliability criteria. A cost model should state what must be load-tested, measured, and reconciled before its assumptions are accepted.

### Prerequisite checkpoint

Before modelling, write down:

- workload volume, average rate, peak rate, and expected growth;
- data size, retention, replication, and transfer path;
- latency, throughput, availability, recovery, and freshness objectives;
- query/processing cost drivers and the likely bottlenecks;
- what is measured, what is assumed, and what is unknown.

Unknown inputs are not a reason to stop. They are a reason to use ranges and record a measurement plan.

---

## 3. Beginner-level cost terminology and examples

### 3.1 What is a cost model?

A cost model estimates expenditure from quantities and rates over a defined period. A basic line item is:

\[
\text{line-item cost} = \text{billable quantity} \times \text{price per billing unit}
\]

For example, if an illustrative processing service is modelled at 300 billed hours/month and an assumed placeholder rate of $2/hour, the line-item estimate is 300 × $2 = $600/month. This calculation says nothing about whether 300 hours is the right quantity or whether $2/hour is a real price; those are separate inputs that must be justified.

### 3.2 Total cost is more than compute

A data platform can incur costs from:

- compute or processing capacity;
- memory and provisioned capacity, when billed separately or embedded in compute;
- persistent and temporary storage;
- requests, reads, writes, scans, and API operations;
- data transfer within or across zones, regions, or providers, and egress;
- orchestration, schedulers, and managed-service capacity units;
- logging, metrics, tracing, audit records, and retention;
- backups, snapshots, replicas, disaster-recovery environments, and retained versions;
- software licences and support;
- engineering, on-call, incident response, and operational work;
- migration, lock-in exit, compliance, and opportunity costs where material.

Some items are bundled into a managed-service price. Avoid double-counting them as separate charges unless the price structure actually bills them separately.

### 3.3 Cost classifications

| Classification | Meaning | Example | Modelling implication |
|---|---|---|---|
| Fixed (within a range) | Does not change with small workload changes during the period | Minimum platform fee or fixed support allocation | Remains even at low demand; can dominate unit cost at low volume |
| Variable | Changes with workload or consumption | Bytes scanned, events processed, requests | Model the driver and the rate, including tiers if applicable |
| Step cost | Changes when a threshold forces another capacity increment | Adding a worker/node or licence block | Cost curve is not smoothly linear |
| Direct | Can be attributed to a specific workload/product | Dedicated pipeline compute | Easier to assign to an owner |
| Indirect/shared | Supports multiple workloads | Shared control plane, platform on-call | Needs an explicit allocation rule or remains centrally funded |
| Recurring | Repeats by period | Monthly support, always-on cluster | Forecast over the full period, including idle time |
| Usage-based | Billed by measured activity | Per request, per GB processed | Depends on workload and meter semantics |
| Committed | Capacity or spend is contracted for a period | Illustrative commitment paid whether used or not | Include unused capacity and commitment term risk |
| One-time | Occurs once or during a transition | Migration or initial backfill | Separate setup cost from recurring run rate |
| Avoidable | Can be removed if the activity/resource is removed | Idle duplicate environment | Confirm dependency and deletion safety before treating as savings |
| Allocated | A share of a common cost assigned to a team/product | Shared storage allocated by GB-month | Allocation is a policy choice, not always a change in total spend |

These categories overlap. A direct compute resource can be variable and recurring; a shared support contract can be indirect and recurring.

### 3.4 Capacity, utilisation, and billed consumption are different

- **Capacity** is what a system can supply (for example, 16 worker-hours per wall-clock hour, or 2 TB of provisioned storage).
- **Utilisation** is how much of that capacity is used during a period, according to a defined meter.
- **Billed consumption** is the quantity the billing model charges for. It may be provisioned capacity, runtime, bytes scanned, requests, committed spend, or a combination.

A resource at 20% CPU utilisation may still incur the full charge for a provisioned node. A serverless service may bill measured execution units while having no continuously provisioned worker. Never calculate cost by multiplying CPU utilisation by price unless the billing unit actually follows that metric.

### 3.5 Average, marginal, and incremental cost

- **Average cost per unit** = total cost over a period ÷ units delivered in that period.
- **Marginal cost** = change in total cost caused by one additional unit (or a small additional amount) under the current operating conditions.
- **Incremental cost** = change in total cost between two defined workload or design scenarios.

Average cost spreads fixed costs across all units. Marginal cost can be low while spare capacity exists, then jump when a capacity step is required. Incremental cost should compare two scenarios over the same time window and include any new fixed or step costs.

Example: an illustrative $10,000 monthly platform processes 500 million events/month. Average platform cost is $20 per million events. If the next 10 million events fit in spare capacity and require $80 of additional measured processing, the marginal cost for that increment is $8 per million. These numbers are illustrative and show why average and marginal cost can differ.

### 3.6 Total cost of ownership (TCO)

TCO broadens the view beyond a service line item. Depending on the decision, include setup/migration, recurring infrastructure, licences, people, operations, reliability controls, data transfer, incident exposure, training, and eventual exit or migration cost. State the analysis horizon (for example, 12 or 36 months) and which costs are excluded. Do not pretend that every indirect cost can be estimated precisely; use ranges and confidence levels.

---

## 4. Cost-driver inventory and measurement units

A cost-driver inventory connects a resource to its meter, unit, price source, and owner. The price source should be a dated quote, current published rate, internal rate card, contract, or explicitly labelled placeholder.

| Driver | Common quantity/billing units | Example quantity formula | Common hidden factor | Owner/evidence to capture |
|---|---|---|---|---|
| Compute | vCPU-hour, worker-hour, node-hour, execution-second, processing unit, bytes scanned | worker count × hours, or workload volume × measured resource per unit | Idle time, minimums, autoscaling delay, retries, peak headroom | Platform owner; runtime and capacity telemetry |
| Memory | GB-hour, provisioned memory, bundled compute-memory unit | provisioned GB × hours, if separately metered | Replica count, cache sizing, memory over-provisioning | Serving/platform owner; memory and eviction telemetry |
| Persistent storage | GB-month or TB-month | average stored GB × fraction of month | Compression, indexes, snapshots, replicas, minimum billable size | Data owner; measured stored size and retention |
| Object/record operations | request count, read/write/list operation | operations per event/query × volume | Small files, retries, listing scans, multipart operations | Pipeline owner; request telemetry |
| Query/scan | query count, bytes scanned, compute units | query mix × volume; bytes scanned/query × query count | Unpruned partitions, repeated joins, fan-out | Analytics owner; query history and scan metrics |
| Data transfer | GB/TB transferred, sometimes direction/zone/region-specific | bytes per event × events, or replica movement | Cross-zone traffic, egress, duplicate transfers | Network/platform owner; flow/transfer metrics |
| Orchestration | job runs, task minutes, workflow steps | runs/day × tasks/run × days | Retries, tiny tasks, polling, idle control plane | Data engineering; scheduler history |
| Logging/monitoring | ingested GB, retained GB-month, metrics series, traces/events | events × bytes/event × retention | Verbose logs, high-cardinality labels, debug mode | Observability owner; ingest and retention meters |
| Backup/DR/replication | stored GB-month, replica capacity, transfer | primary data × copy count × retention | Multiple snapshots, cross-region copies, old versions | Reliability owner; copy/retention policy |
| Managed service | capacity units, throughput units, requests, fixed tier | capacity × time or usage × rate | Minimum tiers, autoscaling floors, premium features | Service owner; provider meter definitions |
| Licences/support | seat-month, instance, contract period | seats × monthly rate or fixed contract | Minimum seats, add-ons, renewals | Procurement/owner; contract terms |
| People/operations | staff hours, on-call allocation, loaded labour cost | hours × internal rate, or allocated FTE share | Incident work, toil, specialist support | Team manager; stated allocation method |
| Security/compliance | scan volume, keys, audit logs, retention, control-plane services | events/data/operations × rates | More retention, replication, encryption/audit overhead | Security/governance owner; policy and meter |

### 4.1 Cost-model input register

For every material line item, record:

- resource or service;
- cost category and owner;
- billing unit and unit conversion;
- quantity formula and period;
- unit price and source/date, or placeholder label;
- scenario (low/expected/high);
- whether price is fixed, tiered, committed, or usage-based;
- whether tax, discount, support, transfer, and currency conversion are included;
- confidence level and next validation step.

### 4.2 Unit consistency rules

1. Convert all quantities to compatible units before multiplying.
2. Use the same period for all cost lines in a total.
3. State whether GB is decimal (1 GB = 1,000,000,000 bytes) or GiB (1 GiB = 1,073,741,824 bytes) when precision matters.
4. Do not mix per-hour prices with monthly quantities without multiplying by billable hours.
5. Do not mix event count with successful-event count without defining failures and retries.
6. Do not sum costs in different currencies without a documented exchange-rate date and treatment.
7. Do not include a cost twice because it appears in both a managed-service charge and a resource estimate.

---

## 5. Worked cost-estimation calculations

All amounts and prices in this section are illustrative placeholders.

### 5.1 Unit cost: cost per million events

Assume a pipeline costs $12,000 over one calendar month and processes 600,000,000 eligible events during that same month. For this example, “processed event” means one unique event successfully accepted by the defined pipeline boundary; failed attempts and duplicate retries are excluded from the denominator, while their compute cost remains in the $12,000 numerator.

Cost per event:

\[
\$12{,}000 / 600{,}000{,}000 = \$0.00002\text{ per event}
\]

Cost per million eligible events:

\[
\$12{,}000 / (600{,}000{,}000 / 1{,}000{,}000) = \$20\text{ per million events}
\]

The denominator is the number of successful eligible events in the same month, not all attempted deliveries. If failed/duplicate work grows, cost per successful event can rise even when successful volume is flat. Report failed attempts and retry volume separately so the unit metric is explainable.

### 5.2 Capacity-to-cost estimate for an always-on cluster

Assumptions for one illustrative month:

- 8 worker nodes;
- each node is billed at a placeholder $1.25 per node-hour;
- 730 billable hours in the modelled month;
- storage, network, support, licences, and people are priced separately;
- node-hour billing is based on provisioned nodes, not CPU utilisation.

Compute estimate:

\[
8\text{ nodes} \times 730\text{ hours} \times \$1.25/\text{node-hour} = \$7{,}300/\text{month}
\]

If average CPU utilisation is 30%, this estimate remains $7,300 under the stated provisioned-node pricing assumption. Utilisation is diagnostic evidence for right-sizing, not a multiplier that automatically reduces the invoice.

### 5.3 Storage, retention, and replication

Assume the platform stores 18 TB of retained data on average, has two additional full copies (three copies total including primary), and uses an illustrative storage price of $18 per TB-month per copy. The 18 TB is the logical dataset size before replication; this simplified model assumes each copy is the same size and excludes indexes, snapshots, metadata, and request charges.

\[
18\text{ TB} \times 3\text{ copies} \times \$18/\text{TB-month} = \$972/\text{month}
\]

If retention grows from 30 to 90 days at a stable ingest rate and no deletions, retained logical data may approach three times its prior volume after the system reaches the new steady state. Replication then multiplies the physical stored volume. Actual growth depends on compaction, compression, late deletion, snapshots, and whether all retained data has the same copy count and storage tier.

Do not multiply by three if the measured storage price already includes the relevant replication. Read the meter definition and document what the price covers.

### 5.4 Data transfer and egress

Assume 600 million events/month, with an average payload of 2 KB per event transferred out of the processing region. Use decimal units for this example: 1 KB = 1,000 bytes and 1 GB = 1,000,000,000 bytes. Ignore protocol overhead, compression, retries, and other transfers.

Monthly transfer bytes:

\[
600{,}000{,}000 \times 2{,}000 = 1.2\times10^{12}\text{ bytes} = 1{,}200\text{ GB}
\]

At an illustrative placeholder price of $0.08/GB for the specific transfer class:

\[
1{,}200\text{ GB} \times \$0.08/\text{GB} = \$96/\text{month}
\]

This is not a vendor egress rate. The actual cost depends on source/destination, direction, region/zone, provider, transfer tier, free allowances, and whether the bytes are billed at all. Replication, backup, retries, and consumers may create additional transfer paths; model them separately rather than assuming this is total network cost.

### 5.5 Monthly and annual cost build-up

Assume the following illustrative monthly line items for one architecture:

| Cost line | Quantity basis | Placeholder monthly cost |
|---|---|---:|
| Compute | Provisioned workers and scheduled jobs | $7,300 |
| Storage | Primary data and included copies as explicitly defined | $972 |
| Transfer | 1,200 GB under the stated transfer class | $96 |
| Requests/orchestration | Job and object operations | $420 |
| Logging/monitoring | Ingest and retention | $310 |
| Shared operations allocation | Defined internal allocation | $1,200 |
| **Total** | Sum of included line items | **$10,298/month** |

Annualised run rate if every month is identical:

\[
\$10{,}298 \times 12 = \$123{,}576/\text{year}
\]

This annualisation is not a full annual forecast if seasonality, growth, price changes, annual licences, one-time migration, or capacity steps differ by month. It is simply 12 times the stated monthly run rate. The line items are mutually exclusive for this example; in a real model, verify that compute does not already include orchestration, monitoring, or storage charges.

### 5.6 Low, expected, and high growth scenarios

A scenario model should change workload drivers, not arbitrarily apply a blanket multiplier to all costs. For a simple first pass, suppose a baseline pipeline has the following monthly assumptions:

- compute: $7,300 at baseline volume;
- storage: $972 at baseline retained data;
- transfer: $96 at baseline transferred bytes;
- requests/orchestration: $420 at baseline event/job volume;
- logging/monitoring: $310 at baseline event volume;
- shared operations: $1,200 fixed allocation for this model.

Assume the low, expected, and high scenarios have volume multipliers 0.7×, 1.0×, and 1.8×. For the deliberately simplified model, compute, transfer, requests, and logging scale linearly with event volume; storage scales linearly with retained data; shared operations remain fixed. This ignores capacity steps, discounts, nonlinear scaling, retention changes, and optimisation effects.

| Line item | Low (0.7× variable volume) | Expected (1.0×) | High (1.8×) |
|---|---:|---:|---:|
| Compute | $5,110 | $7,300 | $13,140 |
| Storage | $680.40 | $972 | $1,749.60 |
| Transfer | $67.20 | $96 | $172.80 |
| Requests/orchestration | $294 | $420 | $756 |
| Logging/monitoring | $217 | $310 | $558 |
| Shared operations | $1,200 | $1,200 | $1,200 |
| **Monthly total** | **$7,568.60** | **$10,298** | **$17,576.40** |
| **Annualised run rate** | **$90,823.20** | **$123,576** | **$210,916.80** |

The high scenario is not simply “1.8× total cost” because the shared operations allocation remains fixed. A production forecast should add nonlinear effects such as additional nodes, capacity tiers, peak headroom, higher logging volume, and new support requirements when thresholds are crossed.

### 5.7 Utilisation and committed capacity break-even

The module roadmap provides an illustrative commitment example: if committed capacity costs 60% of the on-demand price and is paid regardless of usage, the commitment becomes cheaper than paying on-demand for the same capacity when utilisation of the committed capacity exceeds 60%, under a simplified proportional usage model.

Let P be the on-demand price per hour for one capacity unit, and u be the fraction of the unit used over the hour:

- committed cost = 0.6P per hour, paid regardless of usage;
- on-demand cost = uP per hour;
- break-even occurs when 0.6P = uP, so u = 0.6 (60%).

This assumes the same capacity and service are comparable, no additional fees, no different performance or flexibility, and no commitment term risk. Real contracts may have minimum spend, scope restrictions, upfront payments, unused commitments, and changing demand. A nominal discount does not guarantee a lower total bill if the committed capacity is underused or does not match the workload.

### 5.8 Marginal cost and a capacity step

Suppose an illustrative service costs $4,000/month for up to 300 million events, then needs an additional $1,500/month capacity block to handle volume above that threshold. At 300 million events, average cost is $13.33 per million. At 301 million events, total cost becomes $5,500, so average cost is approximately $18.27 per million. Across the move from 300 million to 301 million events, incremental cost is $1,500 per additional million events over that interval. This is a step-cost effect, not evidence that each later million will cost $1,500; the capacity block may serve additional volume until the next threshold.

This is why linear extrapolation should be treated as an assumption, not a law. Identify the points where a new node, licence tier, throughput unit, replica, or support tier is required.

---

## 6. Intermediate scenario-based cost modelling

### 6.1 A transparent model has four layers

1. **Workload inputs:** events, requests, queries, bytes, retention, concurrency, peak factor, retries, and growth.
2. **Resource formulas:** node-hours, execution units, GB-month, request count, transfer GB, log ingest, and operations hours.
3. **Pricing inputs:** unit price, discount, billing tier, region, contract, and date/source.
4. **Outputs:** monthly/annual cost, unit cost, scenario range, break-even, uncertainty, and validation criteria.

Keep inputs separate from formulas and outputs. This makes the model auditable and allows a price change or workload update without rewriting calculations manually.

### 6.2 Compare two options fairly

The module roadmap gives this placeholder structure for two architectures at 600 million events/month:

| Option | Compute | Storage | Transfer | Ops (people) | Total/month | Cost per million events |
|---|---:|---:|---:|---:|---:|---:|
| A: always-on cluster | $9,000 | $2,000 | $500 | $4,000 | $15,500 | $25.83 |
| B: elastic/serverless | $5,500 | $2,000 | $500 | $2,500 | $10,500 | $17.50 |

The values are placeholders from the module roadmap, not market prices or proof that option B is cheaper in a real deployment. Cost per million events is total monthly cost divided by 600 million / 1 million = 600 million-unit batches. Option A: $15,500 / 600 = $25.83 per million; Option B: $10,500 / 600 = $17.50 per million.

The comparison is only valid if both options process the same workload, satisfy the same latency/availability/security requirements, and include costs on the same basis. Check whether the operations allocation includes engineering and on-call time for each option, whether storage replication is comparable, and whether elastic pricing includes orchestration and data transfer.

### 6.3 Sensitivity to volume and utilisation

For each option, ask:

- What changes if event volume doubles?
- Which line items scale linearly, and which are fixed or stepwise?
- How does always-on cluster utilisation change from 30% to 70%?
- Is capacity billed when idle, or only while execution occurs?
- Does high demand trigger additional workers, partitions, replicas, licences, or network transfer?
- Do request retries, backfills, and reprocessing grow with data volume?

Do not automatically scale every line item by 2× when volume doubles. A storage line may scale with retained data, not throughput; a shared operations allocation may stay fixed until a staffing threshold; compute may scale in discrete increments; and transfer may depend on architecture rather than event count alone.

### 6.4 Example: query optimisation versus larger compute

Consider a recurring analytical query. Option A uses a larger compute tier; Option B improves partition pruning and reduces bytes scanned. To compare them, capture:

- baseline query count and bytes scanned/query;
- runtime distribution and concurrency;
- current and proposed compute billing units;
- storage/layout changes and any compaction cost;
- latency target and acceptable result semantics;
- refresh or materialisation cost if precomputation is proposed.

A query that scans fewer bytes may reduce compute and improve latency, but only if the billing model or workload actually charges less for the reduced work. A larger tier can shorten runtime while costing more per hour; the total cost depends on runtime × rate and whether capacity remains allocated afterward. Measure both cost and performance under the same workload before claiming a saving.

### 6.5 Cost of resilience and controls

Redundancy, backup, disaster recovery, encryption, audit logging, monitoring, and security scanning are cost drivers. They are not automatically waste. The decision should compare the added cost against the required recovery time, recovery point, availability, compliance, and risk reduction.

Examples of costs that are easy to omit:

- standby capacity or a second region;
- retained snapshots and replicas;
- replication traffic and cross-region egress;
- audit log ingestion and long retention;
- monitoring cardinality and trace volume;
- test environments, backfills, and restore drills;
- engineering effort to operate and validate the controls.

Do not remove a resilience control solely because it increases the bill. Establish which objective it satisfies, whether the same objective can be met more efficiently, and how the alternative will be tested.

---

## 7. Advanced unit economics, sensitivity analysis, allocation, and FinOps

### 7.1 Choose a denominator that reflects delivered value

A unit metric is useful only when its denominator is well-defined and aligned with the decision. Examples include:

- cost per million successfully processed events;
- cost per successful query or report;
- cost per TB processed or scanned;
- cost per active customer per month;
- cost per decision served within a latency/freshness objective;
- cost per feature vector served or model inference supported;
- cost per business transaction completed.

The denominator must specify the boundary and treatment of failures, retries, duplicates, cancellations, and partial results. If 10 million attempts yield 9.5 million successful events, and the total cost includes all attempts, report cost per successful event as total cost / 9.5 million and separately disclose the 0.5 million failures/retries. Do not divide by attempted volume and call it cost per successful event.

A lower cost per unit can still be misleading if quality or scope changes. For example, dropping validation or retention may lower cost per event but violate the service contract. Pair unit economics with service-level indicators and business outcomes.

### 7.2 Average, marginal, and incremental economics

For total cost function C(Q), where Q is delivered volume:

- average cost: C(Q) / Q;
- marginal cost: the change in cost for an additional unit (conceptually dC/dQ for a smooth model, but many cloud costs are tiered/stepwise);
- incremental cost between Q1 and Q2: [C(Q2) − C(Q1)] / [Q2 − Q1].

For a discrete capacity step, use actual scenario differences rather than pretending the cost curve is smooth. Report the time horizon and denominator units.

### 7.3 Break-even analysis

For two options A and B, break-even is the workload level where their total costs are equal, subject to both meeting hard requirements. A simple linear model can be written:

\[
C_A(Q) = F_A + v_A Q, \quad C_B(Q) = F_B + v_B Q
\]

where F is fixed cost per period and v is variable cost per unit. If v_A differs from v_B, the algebraic crossover is:

\[
Q^* = (F_B - F_A)/(v_A - v_B)
\]

Only interpret Q* if it is non-negative, lies within the model's valid range, and neither option crosses an unmodelled capacity step first. If costs are tiered, use piecewise scenarios or a numerical table rather than a misleading single crossover.

### 7.4 Sensitivity and uncertainty

A sensitivity analysis varies one or more assumptions and records how the decision changes. Common high-impact inputs are:

- demand volume and peak-to-average ratio;
- average payload size and retained-data growth;
- query scans/compute per unit;
- utilisation and idle hours;
- retries, failure rate, and backfill frequency;
- storage copies, retention, and compression;
- egress volume and destination mix;
- commitment utilisation and term;
- labour/operations effort;
- price changes, discounts, and currency conversion.

Use at least three scenarios—low, expected, high—and explain what drives each. For uncertain inputs, use ranges and sensitivity rather than spurious precision. A $10,298.43 forecast is not more accurate than a $10,300 forecast if key quantities are uncertain by 20%.

Separate:

- **parameter uncertainty:** the true price, volume, or runtime is uncertain;
- **model uncertainty:** the formula or scaling relationship may be wrong;
- **structural uncertainty:** the architecture or workload may change;
- **price/contract uncertainty:** future rates, discounts, or terms may change.

### 7.5 Cost-performance-reliability frontier

A candidate architecture should be evaluated across at least cost, latency/throughput, and reliability. A candidate is **dominated** if another option costs no more and is at least as good on every relevant metric, with a strict improvement on one, under comparable evidence. A cost-performance frontier contains options where improving one dimension requires sacrificing another.

The “best” option is not necessarily the cheapest. First remove options that fail hard requirements. Then compare the remaining options on cost, performance, reliability, freshness, operability, and uncertainty. If performance data are only estimated, label them as hypotheses until Topic 07 validates them.

### 7.6 FinOps: accountability and collaboration

FinOps is a collaborative operating practice across engineering, finance, procurement, product/business owners, and platform teams. It makes cloud spend visible and actionable rather than treating cost as a finance-only after-the-fact report.

A practical operating loop:

1. **Inform:** collect cost and usage data; tag resources; allocate spend; publish showback and unit-cost trends.
2. **Optimize:** identify idle/over-provisioned resources, inefficient queries, uncontrolled retries, excessive retention, unnecessary transfer, and commitment opportunities.
3. **Operate:** assign owners, budgets, forecasts, alerts, review cadence, approval rules, and evidence-based optimisation checks.
4. **Learn:** compare model with actual usage/bill, record variance, and improve assumptions.

FinOps does not mean “minimise cost at any price.” It means make cost and value visible and choose deliberately within performance, reliability, security, and business constraints.

### 7.7 Tagging, ownership, and allocation

A minimum useful tag/metadata scheme often includes:

- owner/team;
- product or workload;
- business domain/cost centre;
- environment (production, staging, development, test);
- application or service;
- data classification or residency group when appropriate;
- lifecycle/expiry date for temporary resources.

Tag enforcement should include validation at provisioning time, an owner for untagged spend, and a remediation path. Tags alone do not allocate shared costs accurately; allocation needs a defined policy.

### 7.8 Showback versus chargeback

- **Showback** reports cost to the teams/products that consume or benefit from it. It builds awareness without necessarily transferring budget.
- **Chargeback** assigns the financial charge to a team, product, or cost centre and can create stronger incentives and accountability.

The roadmap recommends building visibility through showback before introducing chargeback. Chargeback with weak meters or unexplained allocations can create resentment and incentives to game the metric.

### 7.9 Shared-cost allocation example

Assume an illustrative shared analytics platform costs $12,000/month. Three teams have measured usage shares of 50%, 30%, and 20% using a chosen metering basis (for example, weighted compute units). If allocated by usage:

- Team A: $12,000 × 50% = $6,000;
- Team B: $12,000 × 30% = $3,600;
- Team C: $12,000 × 20% = $2,400.

The allocation reconciles to $12,000. This does not prove the weights are fair: weighted compute may not reflect shared availability, peak capacity reserved for all teams, or value received. A flat one-third split would be $4,000 each, simpler but less sensitive to usage. Headcount allocation might suit some people costs but be a poor proxy for query or storage consumption.

A robust policy separates:

1. directly attributable costs;
2. shared variable costs allocated by a usage meter;
3. shared fixed/platform-readiness costs allocated by a documented policy;
4. unallocated/unknown costs with an owner and remediation deadline.

The sum of allocated and unallocated costs should reconcile to the source total. Do not silently drop untagged spend or allocate the same shared line twice.

### 7.10 Budget, forecast, variance, and anomaly response

- **Budget:** approved spending envelope or control for a period; not a prediction.
- **Forecast:** expected spend based on current workload, resource use, and assumptions.
- **Actual:** billed or accrued spend for the period, subject to invoice and attribution timing.
- **Variance:** actual minus forecast or budget, with the comparison basis stated.
- **Anomaly:** unusual deviation from expected spend/usage, which requires investigation rather than automatic deletion.

A variance review should identify the driver: workload growth, unit price change, resource mix, idle time, retries, backfills, retention, transfer, commitment utilisation, or allocation changes. Budget alerts should have owners, thresholds, response steps, and a distinction between warning and action. Automatically shutting down a resource can break production if the alert policy ignores criticality.

### 7.11 Reserved/committed versus flexible consumption

Committed capacity may lower the effective unit price in exchange for a term, minimum spend, or reduced flexibility. Flexible/on-demand consumption may have a higher nominal unit price but avoid paying for unused capacity and may suit uncertain or spiky workloads.

Compare both over the commitment term, including:

- utilisation distribution, not only average utilisation;
- baseline and seasonal demand;
- coverage and scope restrictions;
- upfront or recurring commitment payment;
- growth/decline and migration risk;
- capacity required for performance headroom;
- what happens to unused commitment;
- whether the committed product matches the workload and region;
- exit or change costs.

Do not claim a commitment is universally cheaper. A 40% discount to a price basis is only useful if enough eligible consumption uses it and the contractual scope fits the workload.

### 7.12 Cost risks and optimisation opportunities

| Opportunity | Evidence to seek | Potential benefit | Risks and validation requirements |
|---|---|---|---|
| Right-size compute | CPU/memory, queueing, runtime, peak tests | Lower provisioned capacity or shorter runtime | Can violate latency/headroom; validate at peak and failure conditions |
| Autoscale or schedule | Time-of-day demand, scale lag, idle windows | Avoid paying for unused capacity | Cold start, scale oscillation, missed deadlines; test ramp and recovery |
| Optimise query/scan | Bytes scanned, query plans, repeated joins | Lower processing work and possibly runtime | Changed semantics or added preprocessing; compare results and measured cost |
| Cache repeated reads | Reuse distribution, miss fan-out, freshness contract | Reduce backend work | Memory, stale data, stampede, outage fallback; test cache-disabled path |
| Materialise repeated aggregates | Query frequency/cost, refresh cadence, freshness need | Avoid repeated compute | Refresh/storage/reconciliation cost; verify end-to-end lag and correctness |
| Tier storage/lifecycle | Access frequency, retention, retrieval needs | Lower storage cost for colder data | Retrieval fees/latency, restore delays, lifecycle mistakes; test restore and access |
| Compact small files | File counts, request/list cost, scan overhead | Fewer requests and improved query efficiency | Compaction compute and concurrent-write effects; validate query and ingestion performance |
| Reduce transfer | Data flow map, bytes by route, consumer locality | Lower egress and improve locality | Added replication/storage or architectural complexity; test resilience and freshness |
| Control retries | Retry rate, failure classes, backoff, duplicate work | Avoid amplified compute and requests | Too few retries can reduce reliability; set bounded policy and validate recovery |
| Remove idle resources | Ownership, utilisation, dependencies, expiry | Avoid unnecessary recurring cost | Accidental deletion or hidden dependency; require owner confirmation and rollback |
| Improve logging/metrics | Ingest volume, cardinality, retention | Lower telemetry cost | Reduced incident visibility; preserve critical security/audit signals |
| Commit baseline capacity | Stable eligible consumption and term forecast | Potential lower unit rate | Underutilisation/lock-in; run break-even and downside scenarios |
| Improve allocation | Untagged spend and meter quality | Better accountability and decisions | False precision or unfair incentives; reconcile and review policy |

A savings hypothesis becomes a validated outcome only after a comparable before/after measurement, with workload and service quality controlled and the total cost boundary documented.

---

## 8. Industry-style case studies and architecture comparisons

### 8.1 Case study A — event ingestion platform

**Situation:** an event pipeline has a monthly target of 600 million successful events. A placeholder estimate gives $12,000/month total cost. The business asks for unit economics and a forecast for volume growth.

**Model:** cost per million successful events = $12,000 / 600 = $20 per million. The model must define whether retries and duplicates are counted in the denominator; here they are excluded, but their costs remain in the numerator.

**Risks:** event volume could grow while retry rate also rises; the cost curve may become nonlinear when another capacity block is needed; retention and replication may grow independently of event throughput.

**Recommendation:** publish cost per million successful events alongside success rate, retry/duplicate volume, data retention, and peak throughput. Create low/expected/high volume scenarios and mark the threshold at which capacity must step up. Validate with actual billing and Topic 07 performance testing.

### 8.2 Case study B — always-on versus elastic processing

Use the roadmap's illustrative two-option monthly comparison for 600 million events:

| Metric | Always-on cluster A | Elastic/serverless B |
|---|---:|---:|
| Compute | $9,000 | $5,500 |
| Storage | $2,000 | $2,000 |
| Transfer | $500 | $500 |
| Operations | $4,000 | $2,500 |
| Total/month | $15,500 | $10,500 |
| Cost per million events | $25.83 | $17.50 |

These are placeholder estimates. Option B appears lower by $5,000/month in this model, but the comparison is not enough to choose it. Confirm identical workload, data retention, resilience, latency, operational support, and failure recovery. An elastic design can incur cold-start latency, request-based charges, or unpredictable spend; an always-on cluster can pay for idle capacity but may provide predictable latency. Validate the service objective and actual cost meters.

### 8.3 Case study C — shared platform cost dispute

**Situation:** three product teams contest a $12,000/month shared platform bill. One team consumes 50% of the chosen weighted compute meter, another 30%, and the third 20%.

**Options:**

- Flat split: $4,000 per team. Easy to administer, but weakly connected to consumption.
- Usage-based showback: $6,000 / $3,600 / $2,400 under the stated weights. More reflective of the meter, but may underrepresent common baseline capacity and platform readiness.
- Chargeback: the same allocation affects team budgets. Stronger incentives, but only after the meter and shared-cost policy are trusted.

**Recommendation:** start with reconciled showback, split direct and shared costs, publish the allocation rule and uncertainty, allow teams to dispute source data, and move to chargeback only after governance is agreed. Reconcile allocations to the full $12,000 and keep unallocated spend visible.

### 8.4 Case study D — cache/materialisation versus repeated compute

**Situation:** a dashboard repeatedly queries an expensive aggregate. Topic 05 established that a materialised view could reduce repeated computation but incurs refresh, storage, and operations costs.

**Cost comparison:** calculate repeated live query cost as query count × measured marginal query cost. Calculate materialised cost as refresh cost + storage + serving + transfer + reconciliation/operations. Keep the freshness contract as a hard constraint. If materialisation cannot meet freshness, it is not a viable candidate regardless of the cost result.

**Recommendation:** measure query frequency and query cost, optimise the query plan first, then model a materialised view and optional cache. Include refresh failures, late-arriving corrections, cache misses, and cold starts. Validate total cost and data correctness before declaring a saving.

### 8.5 Architecture comparison table

| Architecture | Cost shape | Strengths | Cost/performance risks | Evidence needed |
|---|---|---|---|---|
| Always-on cluster | Mostly provisioned time/capacity plus storage/transfer | Predictable baseline capacity and potentially stable latency | Idle spend, step capacity additions, underutilisation | Utilisation over time, peak test, runtime, actual billed node-hours |
| Elastic/serverless | Usage/execution/requests, sometimes minimums | Can track variable demand and reduce idle capacity | Cold starts, burst costs, per-operation charges, scaling limits | Demand distribution, meter semantics, concurrency test, request volume |
| Hybrid with commitment | Committed baseline plus flexible overflow | Potentially lower baseline unit price with burst flexibility | Unused commitment, wrong coverage, term risk, duplicate capacity | Eligible consumption, utilisation percentiles, term forecast, break-even model |
| On-demand query | Query/scan/compute usage | Flexible query shapes and limited precomputation maintenance | Repeated scans and unpredictable expensive queries | Query history, bytes scanned, frequency, latency and concurrency |
| Materialised aggregate | Refresh compute + storage + serving | Predictable repeated reads and reduced repeated computation | Freshness lag, refresh cost, reconciliation, version retention | Query reuse, refresh duration, correctness, storage, freshness distribution |
| Layered cache + backing store | Cache infrastructure plus miss path and source | Reuses hot data and can lower backend load | Staleness, invalidation, stampede, duplicated storage | Hit/miss by workload, miss fan-out, cache-outage capacity, freshness |

---

## 9. Practical exercises at three difficulty levels

Attempt the exercises before reading the answer key.

### Level 1 — Beginner: unit cost and cost drivers

A hypothetical event pipeline costs $12,000 per month and processes 600 million successful events in that month. The total cost includes compute, storage, transfer, and operations. Failed attempts and retries are included in the cost but not in the successful-event denominator.

1. Calculate cost per successful event and cost per million successful events.
2. List five cost drivers that should be tracked separately.
3. Explain why the total monthly bill alone is insufficient to tell whether efficiency improved.
4. State two assumptions that should be documented before using the unit cost for a forecast.

### Level 2 — Intermediate: compare two architectures

For 600 million events/month, use the roadmap's illustrative placeholder figures:

- Option A: compute $9,000; storage $2,000; transfer $500; operations $4,000.
- Option B: compute $5,500; storage $2,000; transfer $500; operations $2,500.

1. Calculate each monthly total and cost per million events.
2. Calculate the modelled monthly and annual difference.
3. If volume doubles, show the result under the deliberately simplified assumption that compute, transfer, and storage double, while operations remain fixed. Explain why this is only a sensitivity case, not a forecast.
4. List three reasons the lower modelled cost may not make an option preferable.

### Level 3 — Advanced: three options, commitment break-even, and allocation

A hypothetical platform has the following modelled monthly cost functions, in dollars, where Q is the number of million successful events per month. All numbers are illustrative and all three options are assumed to meet the hard performance/security requirements for this exercise:

- Option A (always-on): fixed cost $8,000 + $4 × Q.
- Option B (elastic): fixed cost $2,000 + $14 × Q.
- Option C (hybrid): fixed cost $5,000 + $7 × Q.

Tasks:

1. Calculate total cost and cost per million events at Q = 300, 600, and 900 for each option.
2. Find the pairwise break-even volume for A vs B, A vs C, and B vs C using the linear model. Check that the crossover is meaningful and explain the cheaper side of each crossover.
3. At Q = 600, choose a provisional option and state the assumptions that could change the decision.
4. A separate shared platform bill is $12,000/month and the usage meter gives shares of 50%, 30%, and 20%. Calculate showback allocations and propose one fairness limitation.
5. Give a sensitivity plan for workload volume, utilisation, price changes, and retry rate.
6. Define the evidence required before describing the choice as an optimisation.

---

## 10. Answer key and reasoning

### Level 1 — answer

1. Cost per successful event = $12,000 / 600,000,000 = $0.00002. Cost per million = $12,000 / 600 = **$20 per million successful events**.
2. Example drivers: compute hours/units, stored GB-month, transfer GB, request count, orchestration runs, logging ingest/retention, retries, operations hours, replicas/backups.
3. Total cost can rise because volume grew, or fall because work was omitted. Unit cost adds context, but should be paired with service quality, success rate, and scope.
4. Examples: same billing period and workload boundary; denominator excludes failed attempts but numerator includes their cost; prices are placeholders; retention and replication are stable; no capacity step is crossed.

### Level 2 — answer

Option A total = $9,000 + $2,000 + $500 + $4,000 = **$15,500/month**. Cost per million = $15,500 / 600 = **$25.83**.

Option B total = $5,500 + $2,000 + $500 + $2,500 = **$10,500/month**. Cost per million = $10,500 / 600 = **$17.50**.

Modelled difference = $15,500 − $10,500 = **$5,000/month**; annualised at a constant monthly difference = **$60,000/year**. This is an estimate from placeholders, not measured savings.

Under the exercise's simplified sensitivity, double compute, transfer, and storage but hold operations fixed:

- A: compute $18,000 + storage $4,000 + transfer $1,000 + operations $4,000 = **$27,000/month**.
- B: compute $11,000 + storage $4,000 + transfer $1,000 + operations $2,500 = **$18,500/month**.

This is not a forecast because actual compute can scale nonlinearly, storage may scale with retained data rather than event volume, operations may step up, discounts may change, and peak capacity may require discrete increments. An option may be less preferable if it misses latency/reliability targets, has unacceptable lock-in or operational complexity, has unmodelled egress/requests, or performs worse under failure and peak conditions.

### Level 3 — answer

For Q = 300:

- A = $8,000 + $4 × 300 = **$9,200**, or $30.67 per million.
- B = $2,000 + $14 × 300 = **$6,200**, or $20.67 per million.
- C = $5,000 + $7 × 300 = **$7,100**, or $23.67 per million.

For Q = 600:

- A = $8,000 + $2,400 = **$10,400**, or $17.33 per million.
- B = $2,000 + $8,400 = **$10,400**, or $17.33 per million.
- C = $5,000 + $4,200 = **$9,200**, or $15.33 per million.

For Q = 900:

- A = $8,000 + $3,600 = **$11,600**, or $12.89 per million.
- B = $2,000 + $12,600 = **$14,600**, or $16.22 per million.
- C = $5,000 + $6,300 = **$11,300**, or $12.56 per million.

Pairwise break-even:

- A vs B: 8,000 + 4Q = 2,000 + 14Q → 6,000 = 10Q → **Q = 600 million**. Below 600, B is cheaper; above 600, A is cheaper under this linear model.
- A vs C: 8,000 + 4Q = 5,000 + 7Q → 3,000 = 3Q → **Q = 1,000 million**. Below 1,000, C is cheaper; above 1,000, A is cheaper.
- B vs C: 2,000 + 14Q = 5,000 + 7Q → 7Q = 3,000 → **Q ≈ 428.57 million**. Below that crossover, B is cheaper; above it, C is cheaper.

At Q = 600, Option C is the lowest-cost modelled option at $9,200/month. This is provisional because the exercise assumes all three options meet hard requirements and uses linear placeholder cost functions. Real capacity steps, utilisation, term commitments, data transfer, reliability controls, support, and performance tests could change the result.

Shared platform showback: Team A = $12,000 × 50% = **$6,000**; Team B = $12,000 × 30% = **$3,600**; Team C = $12,000 × 20% = **$2,400**. The shares sum to 100% and allocations reconcile to $12,000. Fairness limitation: the chosen usage meter may not represent baseline capacity reserved for all teams or common availability benefits.

Sensitivity plan: vary Q at low/expected/high levels; test low/expected/high utilisation; vary each major unit price by a documented range; vary retry/failure rate and include its additional compute/requests; identify capacity-step thresholds; calculate whether the preferred option changes. Before claiming optimisation, reconcile actual costs, run equivalent workload tests, confirm success/latency/freshness/reliability, include all relevant cost categories, and compare a measured before/after period with scope documented.

---

## 11. Python examples with tests and assertions

The following examples use only the Python standard library and require Python 3.10 or later (the annotations use built-in generic types and `float | None`). They are deterministic teaching models, not billing integrations, cloud price lookups, or production benchmarks. All prices are illustrative placeholders. Each code block is self-contained.

### 11.1 Unit economics with a denominator guard

```python
import math

def _finite_number(value, name: str) -> float:
    # bool is a subclass of int in Python, but is not a meaningful cost/quantity.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return float(value)


def unit_cost(total_cost: float, successful_units: int, units_per_batch: int = 1_000_000) -> dict:
    total_cost = _finite_number(total_cost, "total_cost")
    if total_cost < 0:
        raise ValueError("total_cost must be non-negative")
    if isinstance(successful_units, bool) or not isinstance(successful_units, int) or successful_units <= 0:
        raise ValueError("successful_units must be a positive integer")
    if isinstance(units_per_batch, bool) or not isinstance(units_per_batch, int) or units_per_batch <= 0:
        raise ValueError("units_per_batch must be a positive integer")

    return {
        "cost_per_successful_unit": total_cost / successful_units,
        "cost_per_batch": total_cost / (successful_units / units_per_batch),
    }


result = unit_cost(total_cost=12_000, successful_units=600_000_000)
assert abs(result["cost_per_successful_unit"] - 0.00002) < 1e-12
assert abs(result["cost_per_batch"] - 20.0) < 1e-12

for bad_args in (
    {"total_cost": -1, "successful_units": 1},
    {"total_cost": float("nan"), "successful_units": 1},
    {"total_cost": float("inf"), "successful_units": 1},
    {"total_cost": 100, "successful_units": 0},
    {"total_cost": 100, "successful_units": True},
    {"total_cost": 100, "successful_units": 10, "units_per_batch": 0},
):
    try:
        unit_cost(**bad_args)
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid inputs must be rejected: {bad_args}")

print(result)
```

Expected: `$0.00002` per successful event and `$20.0` per million successful events. The total cost may include failed/retried work while the denominator counts successful eligible units; document this convention.

### 11.2 Monthly line items and annualisation

```python
import math

def monthly_total(cost_lines: dict[str, float]) -> float:
    if not isinstance(cost_lines, dict):
        raise ValueError("cost_lines must be a dictionary")
    total = 0.0
    for name, value in cost_lines.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("cost line names must be non-empty strings")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"cost line {name!r} must be finite numeric")
        if value < 0:
            raise ValueError("cost line items must be non-negative")
        total += value
    if not math.isfinite(total):
        raise ValueError("total cost overflowed to a non-finite value")
    return total


lines = {
    "compute": 7300,
    "storage": 972,
    "transfer": 96,
    "requests_orchestration": 420,
    "logging_monitoring": 310,
    "shared_operations": 1200,
}
monthly = monthly_total(lines)
annual_run_rate = monthly * 12

assert monthly == 10_298
assert annual_run_rate == 123_576
assert sum(lines.values()) == monthly  # all line items are counted once in this model
assert monthly_total({}) == 0.0  # an explicitly empty cost model sums to zero

for invalid_lines in ({"compute": -1}, {"compute": float("nan")}, {"compute": float("inf")}, {"": 1}, {"compute": True}):
    try:
        monthly_total(invalid_lines)
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid cost lines must be rejected: {invalid_lines}")

print({"monthly_total": monthly, "annual_run_rate": annual_run_rate})
```

Expected: `$10,298/month` and `$123,576/year` if every month matches the modelled run rate. It is not a seasonal or growth-aware forecast.

### 11.3 Scenario model with fixed and variable cost

```python
import math

def scenario_cost(base_lines: dict[str, float], variable_keys: set[str], volume_multiplier: float) -> dict:
    if not isinstance(base_lines, dict) or not isinstance(variable_keys, set):
        raise ValueError("base_lines must be a dict and variable_keys a set")
    if isinstance(volume_multiplier, bool) or not isinstance(volume_multiplier, (int, float)) or not math.isfinite(volume_multiplier):
        raise ValueError("volume multiplier must be finite numeric")
    if volume_multiplier < 0:
        raise ValueError("volume multiplier must be non-negative")
    if not variable_keys.issubset(base_lines):
        raise ValueError("variable_keys must exist in base_lines")
    for key, value in base_lines.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("base line names must be non-empty strings")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError("base costs must be finite and non-negative")

    result = {
        key: value * volume_multiplier if key in variable_keys else value
        for key, value in base_lines.items()
    }
    result["total"] = sum(result.values())
    if any(not math.isfinite(value) for value in result.values()):
        raise ValueError("scenario cost overflowed to a non-finite value")
    return result


base = {
    "compute": 7300,
    "storage": 972,
    "transfer": 96,
    "requests": 420,
    "logging": 310,
    "operations_fixed": 1200,
}
variable = {"compute", "storage", "transfer", "requests", "logging"}
low = scenario_cost(base, variable, 0.7)
expected = scenario_cost(base, variable, 1.0)
high = scenario_cost(base, variable, 1.8)

assert abs(low["total"] - 7568.6) < 1e-9
assert abs(expected["total"] - 10298.0) < 1e-9
assert abs(high["total"] - 17576.4) < 1e-9
assert low["operations_fixed"] == expected["operations_fixed"] == high["operations_fixed"] == 1200
assert scenario_cost(base, variable, 0)["total"] == 1200  # variable lines vanish; fixed line remains

for bad_multiplier in (-1, float("nan"), float("inf"), True):
    try:
        scenario_cost(base, variable, bad_multiplier)
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid volume multiplier must be rejected: {bad_multiplier}")
try:
    scenario_cost(base, {"missing"}, 1)
except ValueError:
    pass
else:
    raise AssertionError("unknown variable keys must be rejected")

print({"low": low, "expected": expected, "high": high})
```

Expected totals: `$7,568.60`, `$10,298.00`, and `$17,576.40` per month. The model deliberately treats storage as linear in volume and operations as fixed; revise these formulas when evidence supports different behaviour.

### 11.4 Committed capacity break-even

```python
import math

def commitment_break_even(commit_fraction_of_full_price: float) -> float:
    if isinstance(commit_fraction_of_full_price, bool) or not isinstance(commit_fraction_of_full_price, (int, float)) or not math.isfinite(commit_fraction_of_full_price):
        raise ValueError("commit fraction must be finite numeric")
    if not 0 <= commit_fraction_of_full_price <= 1:
        raise ValueError("commit fraction must be between 0 and 1")
    return float(commit_fraction_of_full_price)


threshold = commitment_break_even(0.60)
assert abs(threshold - 0.60) < 1e-12
assert commitment_break_even(0) == 0.0
assert commitment_break_even(1) == 1.0

# Under the simplified model, commitment is cheaper only when eligible utilisation exceeds 60%.
for utilisation in (0.40, 0.60, 0.80):
    commitment_cost = 0.60  # normalised to full on-demand price P=1 per period
    on_demand_cost = utilisation
    if utilisation < threshold:
        assert commitment_cost > on_demand_cost
    elif utilisation == threshold:
        assert commitment_cost == on_demand_cost
    else:
        assert commitment_cost < on_demand_cost

for invalid_fraction in (-0.01, 1.01, float("nan"), float("inf"), True):
    try:
        commitment_break_even(invalid_fraction)
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid commitment fraction must be rejected: {invalid_fraction}")

print({"break_even_utilisation": threshold})
```

Expected break-even is 60% under the explicit assumption that committed cost is a fixed 60% of the full price and on-demand cost is proportional to usage. Real contract terms can change the model.

### 11.5 Allocation and variance analysis

```python
import math

def allocate_shared_cost(total: float, shares: dict[str, float]) -> dict[str, float]:
    if isinstance(total, bool) or not isinstance(total, (int, float)) or not math.isfinite(total) or total < 0:
        raise ValueError("total must be finite and non-negative")
    if not isinstance(shares, dict) or not shares:
        raise ValueError("shares must be a non-empty dictionary")
    for team, share in shares.items():
        if not isinstance(team, str) or not team.strip():
            raise ValueError("team names must be non-empty strings")
        if isinstance(share, bool) or not isinstance(share, (int, float)) or not math.isfinite(share) or share < 0:
            raise ValueError("shares must be finite and non-negative")
    if abs(sum(shares.values()) - 1.0) > 1e-9:
        raise ValueError("shares must sum to 1.0")
    allocation = {team: total * share for team, share in shares.items()}
    if any(not math.isfinite(value) for value in allocation.values()):
        raise ValueError("allocated value is non-finite")
    return allocation


def variance_metrics(forecast: float, actual: float) -> dict[str, float | None]:
    for name, value in (("forecast", forecast), ("actual", actual)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError(f"{name} must be finite and non-negative")
    variance = actual - forecast
    # Percentage variance is undefined for a zero forecast; do not divide by zero.
    variance_percent = None if forecast == 0 else variance / forecast * 100
    return {"variance": variance, "variance_percent": variance_percent}


allocation = allocate_shared_cost(12_000, {"A": 0.50, "B": 0.30, "C": 0.20})
assert allocation == {"A": 6000.0, "B": 3600.0, "C": 2400.0}
assert abs(sum(allocation.values()) - 12_000) < 1e-9

# Variance is defined as actual minus forecast; positive means overspend versus forecast.
forecast = 10_298.0
actual = 11_100.0
variance = variance_metrics(forecast, actual)
assert abs(variance["variance"] - 802.0) < 1e-9
assert abs(variance["variance_percent"] - (802 / 10298 * 100)) < 1e-9
assert variance_metrics(0, 100) == {"variance": 100, "variance_percent": None}
assert variance_metrics(100, 0) == {"variance": -100, "variance_percent": -100.0}

for bad_shares in ({}, {"A": 0.5}, {"A": float("nan"), "B": 1.0}, {"A": True, "B": 0.0}):
    try:
        allocate_shared_cost(100, bad_shares)
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid allocation shares must be rejected: {bad_shares}")
try:
    allocate_shared_cost(float("inf"), {"A": 1.0})
except ValueError:
    pass
else:
    raise AssertionError("non-finite total must be rejected")

print({"allocation": allocation, "variance": variance["variance"], "variance_percent": variance["variance_percent"]})
```

Expected allocation: `$6,000`, `$3,600`, `$2,400`. Expected variance: `$802` above forecast, approximately `7.79%`. Positive variance means actual cost is greater than forecast under the stated convention; investigate drivers before assigning blame.

### 11.6 Pairwise break-even and scenario cost

```python
import math

def _finite_nonnegative(value, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and non-negative")
    return float(value)


def linear_cost(fixed: float, variable_per_million: float, volume_millions: float) -> float:
    fixed = _finite_nonnegative(fixed, "fixed")
    variable_per_million = _finite_nonnegative(variable_per_million, "variable_per_million")
    volume_millions = _finite_nonnegative(volume_millions, "volume_millions")
    total = fixed + variable_per_million * volume_millions
    if not math.isfinite(total):
        raise ValueError("calculated cost is non-finite")
    return total


A = (8000, 4)
B = (2000, 14)
C = (5000, 7)

assert linear_cost(*A, 600) == 10_400
assert linear_cost(*B, 600) == 10_400
assert linear_cost(*C, 600) == 9_200
assert linear_cost(0, 5, 0) == 0

# Solve F1 + v1*Q = F2 + v2*Q, where Q is millions of successful events.
def break_even(option1: tuple[float, float], option2: tuple[float, float]) -> float:
    if len(option1) != 2 or len(option2) != 2:
        raise ValueError("each option must contain fixed and variable cost")
    f1 = _finite_nonnegative(option1[0], "option1 fixed cost")
    v1 = _finite_nonnegative(option1[1], "option1 variable cost")
    f2 = _finite_nonnegative(option2[0], "option2 fixed cost")
    v2 = _finite_nonnegative(option2[1], "option2 variable cost")
    if v1 == v2:
        raise ValueError("parallel cost lines have no unique crossover")
    return (f2 - f1) / (v1 - v2)


assert abs(break_even(A, B) - 600.0) < 1e-12
assert abs(break_even(A, C) - 1000.0) < 1e-12
assert abs(break_even(B, C) - (3000 / 7)) < 1e-12
try:
    break_even((100, 5), (200, 5))
except ValueError:
    pass
else:
    raise AssertionError("parallel cost lines must not report a unique crossover")
try:
    linear_cost(float("nan"), 1, 1)
except ValueError:
    pass
else:
    raise AssertionError("non-finite model inputs must be rejected")

print({"Q600": {"A": linear_cost(*A, 600), "B": linear_cost(*B, 600), "C": linear_cost(*C, 600)},
       "break_even_A_B": break_even(A, B),
       "break_even_A_C": break_even(A, C),
       "break_even_B_C": break_even(B, C)})
```

Expected at 600 million events: A `$10,400`, B `$10,400`, C `$9,200`. Pairwise crossovers: A/B = 600 million; A/C = 1,000 million; B/C ≈ 428.57 million. The model is valid only where its linear assumptions and capacity bounds hold.

---

## 12. Common mistakes, limitations, and troubleshooting

### 12.1 Common mistakes

| Mistake | Why it is problematic | Correction |
|---|---|---|
| Using real-looking prices without a source | Creates false confidence and can mislead a budget decision | Use clearly labelled placeholders or dated, sourced prices |
| Comparing options with different workloads | The cheaper result may simply do less work | Use the same volume, retention, performance and reliability constraints |
| Treating capacity as billed usage | Provisioned resources may be billed while idle | Model the actual billing meter and utilisation separately |
| Multiplying every cost by volume | Fixed and step costs do not scale linearly | Classify each line item and model thresholds |
| Ignoring people, transfer, logs, and retries | Understates TCO and hidden work | Include relevant direct/indirect costs or list exclusions |
| Double-counting bundled service costs | Inflates estimates and biases comparisons | Map each charge to a unique cost boundary and inspect meter definitions |
| Choosing a misleading denominator | Unit cost can improve while success or quality degrades | Define successful units and report failures/retries separately |
| Using average cost as marginal cost | Hides spare capacity and capacity steps | Calculate scenario deltas and identify thresholds |
| Buying commitments based on peak or average alone | Commitment may be underused or mis-scoped | Model demand distribution, term, eligibility, and downside scenarios |
| Allocating all shared spend by headcount | May not reflect consumption or reserved capacity | Choose a transparent driver; separate fixed and variable shared costs |
| Introducing chargeback before meters are trusted | Encourages disputes and metric gaming | Start with reconciled showback and improve attribution first |
| Cutting resilience to meet a budget | Can violate availability, recovery, or compliance objectives | Treat service objectives as hard constraints and validate alternatives |
| Declaring savings from an estimate | Modelled deltas are not observed outcomes | Compare measured before/after cost under equivalent workload and scope |
| Reporting precise totals from uncertain inputs | False precision hides uncertainty | Use scenario ranges, confidence labels, and sensitivity analysis |

### 12.2 Troubleshooting cost anomalies

| Symptom | Possible drivers | Evidence to inspect | Candidate response |
|---|---|---|---|
| Spend rises while traffic is flat | Price/mix changes, idle resources, retries, retention, logging, transfer | Cost by service/tag/day, usage meters, retry and storage trends | Attribute the variance before changing capacity |
| Cost per event rises | More retries, more work per event, capacity step, higher unit price, lower success rate | Successful volume, attempts, query/compute units, current price | Decompose numerator and denominator separately |
| Compute utilisation is low but bill is high | Provisioned capacity billed regardless of use, minimums, reserved baseline | Billing unit, hourly provisioned capacity, idle periods | Right-size/schedule only after peak and recovery validation |
| Storage cost rises unexpectedly | Retention increase, replicas, snapshots, old versions, data growth | Stored GB-month by copy/tier and lifecycle policies | Identify copies and retention; verify deletion and restore needs |
| Transfer cost spikes | New region/consumer, cross-zone traffic, replication, egress | Bytes by source/destination/direction and workload | Revisit locality and replication without weakening resilience |
| Logs/metrics grow rapidly | Debug logging, high-cardinality labels, trace sampling changes | Ingest volume, retention, cardinality, deployment history | Tune verbosity/retention while preserving critical audit/security signals |
| Commitment savings fail to appear | Low utilisation, ineligible consumption, wrong scope, double baseline | Eligible usage, commitment coverage, invoice line items | Recalculate effective price and downside case; adjust future commitments |
| Forecast misses every month | Workload or price drift, omitted drivers, wrong scaling formula | Forecast vs actual by line item and assumptions | Update driver model; distinguish forecast error from allocation changes |
| Shared cost allocations do not reconcile | Untagged resources, duplicated allocation, timing mismatch | Source bill total, unallocated pool, allocation ledger | Reconcile to the same period and document unallocated spend |
| Optimisation worsens latency or reliability | Reduced headroom, aggressive scale-down, weaker redundancy | Before/after p95/p99, errors, recovery, queue depth | Roll back if hard objectives fail; repeat with controlled tests |

### 12.3 Model limitations

- Placeholder prices demonstrate formulas, not actual market pricing.
- Linear scenario models can miss capacity steps, tier discounts, nonlinear query cost, seasonal peaks, and commitment constraints.
- A monthly average can hide short peak periods that drive capacity and reliability requirements.
- Internal labour and opportunity costs are difficult to allocate precisely; document ranges and methods rather than implying exactness.
- Shared-cost allocation is a policy choice and may not represent causal resource use perfectly.
- Annualising a single month assumes that volume, pricing, and resource mix remain constant.
- A cost model cannot prove performance. Topic 07 must validate workload and capacity assumptions with repeatable tests.
- A lower cloud bill does not automatically mean lower TCO if operational effort, incident risk, migration, or exit costs rise.

---

## 13. Practical deliverables

Complete the following artefacts for a realistic data platform workload. These templates are intentionally explicit so another reviewer can reproduce the model.

### 13.1 Cost-driver inventory

| Field | Example / required entry |
|---|---|
| Resource/cost line | Compute, storage, transfer, requests, logs, people, etc. |
| Workload/product/owner | Product and accountable team |
| Cost classification | Fixed/variable/step; direct/shared; recurring/one-time |
| Billing unit | Node-hour, GB-month, request, GB transferred, etc. |
| Quantity formula | Exact formula, source meter, and time window |
| Quantity by scenario | Low, expected, high |
| Price | Placeholder or dated/sourced rate with currency |
| Price source/date | Contract, rate card, invoice, or placeholder declaration |
| Included components | What the price already covers |
| Exclusions | Tax, support, people, transfer, backup, etc. if excluded |
| Confidence | High/medium/low with rationale |
| Validation owner/action | Who will measure or confirm the input |

### 13.2 Transparent capacity-to-cost model

Use this sequence:

1. Define workload volume, rate, peak factor, retention, payload size, retries, and growth.
2. Translate workload into resource quantities (hours, GB-month, requests, transfer GB, task runs).
3. Apply dated prices or placeholder rates to each quantity.
4. Add recurring and one-time costs separately.
5. Reconcile the cost-line sum and remove double-counting.
6. Calculate monthly, annual, and unit costs.
7. Model low/expected/high scenarios and step thresholds.
8. State assumptions, exclusions, and validation plan.

### 13.3 Low/expected/high forecast template

| Driver | Low | Expected | High | Formula/source | Confidence |
|---|---:|---:|---:|---|---|
| Successful events/month | TBD | TBD | TBD | Topic 01 forecast | TBD |
| Attempts/retries | TBD | TBD | TBD | Telemetry or assumption | TBD |
| Compute quantity | TBD | TBD | TBD | Workload-to-resource formula | TBD |
| Stored logical TB | TBD | TBD | TBD | Ingest × retention × compression assumption | TBD |
| Copy/replica count | TBD | TBD | TBD | Architecture requirement | TBD |
| Transfer GB | TBD | TBD | TBD | Data-flow model | TBD |
| Requests/operations | TBD | TBD | TBD | Calls per workload unit × volume | TBD |
| Logs/monitoring | TBD | TBD | TBD | Events × bytes/event × retention | TBD |
| Operations effort | TBD | TBD | TBD | Hours × internal rate or allocation | TBD |
| Total monthly cost | TBD | TBD | TBD | Sum of non-overlapping line items | TBD |
| Cost per successful unit | TBD | TBD | TBD | Total cost / successful units | TBD |

### 13.4 Unit-economics table

| Metric | Numerator | Denominator | Boundary/period | Caveats |
|---|---|---|---|---|
| Cost per million events | Total included cost | Successful eligible events / 1M | Same calendar month | Report retries and failures separately |
| Cost per successful query | Query-serving cost | Successful queries meeting criteria | Defined query class and period | Do not mix cheap and expensive query classes without disclosure |
| Cost per TB processed | Included processing cost | TB processed under stated GB/TB convention | Same period | Distinguish processed from scanned or stored TB |
| Cost per active customer | Attributable platform cost | Defined active customer count | Monthly active definition | Cohort mix and fixed cost allocation affect the result |
| Cost per decision within SLO | Included serving cost | Decisions meeting latency/freshness/correctness criteria | Same period | Pair with error and failure rate |

### 13.5 Cost allocation and showback proposal

Document:

- which costs are direct and assigned by resource ownership;
- which are shared variable costs and which meter allocates them;
- which fixed platform costs use a separate allocation policy;
- how untagged/unallocated costs are handled;
- source period and reconciliation method;
- dispute and correction process;
- whether the first phase is showback or chargeback;
- how to prevent double allocation and metric gaming.

### 13.6 Sensitivity and variance analysis

At minimum, vary workload volume, utilisation, dominant unit price, retention/replication, transfer, and retries. Record:

| Variable | Base assumption | Low case | High case | Impact on total/unit cost | Does recommendation change? |
|---|---:|---:|---:|---:|---|
| Workload volume | TBD | TBD | TBD | TBD | TBD |
| Utilisation | TBD | TBD | TBD | TBD | TBD |
| Price/unit | TBD | TBD | TBD | TBD | TBD |
| Retry rate | TBD | TBD | TBD | TBD | TBD |
| Retention/copies | TBD | TBD | TBD | TBD | TBD |
| Transfer volume | TBD | TBD | TBD | TBD | TBD |

For variance, define the convention before interpreting it:

\[
\text{absolute variance} = \text{actual cost} - \text{forecast cost}
\]

\[
\text{variance percent} = \frac{\text{actual} - \text{forecast}}{\text{forecast}}\times100\%
\]

If forecast is zero, percentage variance is undefined; report absolute variance and explain the new spend instead of dividing by zero. The Python example below returns `None` for the percentage in that case while retaining the absolute variance.

### 13.7 Optimisation opportunity register

| Opportunity | Baseline evidence | Hypothesised change | Modelled impact | Performance/reliability risk | Validation plan | Owner/status |
|---|---|---|---|---|---|---|
| Right-size compute | TBD | TBD | TBD | TBD | Peak load + failure test | TBD |
| Reduce scan/compute | TBD | TBD | TBD | TBD | Query correctness and cost comparison | TBD |
| Change retention/tiering | TBD | TBD | TBD | TBD | Restore and retrieval test | TBD |
| Reduce retries | TBD | TBD | TBD | TBD | Failure/recovery test | TBD |
| Cache/materialise | TBD | TBD | TBD | TBD | Freshness, outage, and total-cost test | TBD |
| Remove idle resource | TBD | TBD | TBD | TBD | Owner/dependency check and rollback | TBD |

Do not report the modelled impact column as realised savings until measured evidence supports it.

### 13.8 Architecture decision record (ADR) outline

```text
Title and date:
Status and decision owner:
Business and technical requirements:
Workload profile and forecast:
Baseline cost and unit economics:
Cost-driver inventory and price sources:
Options considered:
Hard performance/reliability/security constraints:
Monthly/annual model by scenario:
Break-even and sensitivity analysis:
Allocation/showback implications:
Chosen option and rationale:
Risks and limitations:
Validation plan and success criteria:
Rollback plan:
Actual-vs-model review date:
Open questions and owners:
```

---

## 14. Mastery criteria and completion gate

### Mastery criteria

You should be able to:

- [ ] Explain the relationship between workload, resource use, billing units, and cost.
- [ ] Distinguish capacity, utilisation, billed consumption, fixed cost, variable cost, and step cost.
- [ ] Inventory relevant compute, storage, request, transfer, orchestration, observability, people, and resilience costs.
- [ ] Calculate monthly/annual estimates with consistent units and no double-counting.
- [ ] Build low/expected/high scenarios from driver assumptions.
- [ ] Calculate cost per million events and another business-relevant unit with an explicit denominator.
- [ ] Distinguish average, marginal, and incremental cost.
- [ ] Calculate break-even for a simple committed-capacity model and state its assumptions.
- [ ] Propose a cost allocation/showback policy and reconcile the allocation to the total.
- [ ] Explain FinOps ownership, budgets, forecasts, variance, anomaly response, and governance.
- [ ] Perform sensitivity analysis and identify when a recommendation changes.
- [ ] Identify optimisations with risks and measurable validation requirements.
- [ ] Separate modelled estimates from observed savings and disclose exclusions.

### Completion gate

Submit a short cost architecture review containing:

1. A cost-driver inventory with billing units, prices/source dates or placeholder labels, and owners.
2. A transparent capacity-to-cost model with monthly and annual totals.
3. Low, expected, and high scenarios tied to workload assumptions.
4. At least two unit-economics metrics with defined denominators.
5. A comparison of at least two architecture options and one sensitivity/break-even analysis.
6. A shared-cost allocation or showback example that reconciles to the total.
7. A list of cost-optimisation opportunities, risks, owners, and validation criteria.
8. A clear statement of uncertainty, excluded costs, and evidence still required.

**Pass condition:** another reviewer can reproduce the calculations; units and periods are consistent; all prices are placeholders or sourced and dated; allocation reconciles; the model does not double-count known components; and no estimated saving is presented as measured. Hard performance, reliability, security, and freshness requirements remain constraints rather than optional scorecard points.

---

## 15. Transition to Topic 07 — Performance Testing and Capacity Validation

Topic 06 turns workload and architecture choices into a cost hypothesis. Topic 07 tests whether the assumed capacity and performance actually hold under a defined workload.

Carry forward these inputs:

- workload volumes, peak factors, and growth scenarios from Topic 01;
- throughput, latency percentiles, concurrency, and queueing assumptions from Topic 02;
- query and data-movement cost evidence from Topic 03;
- scaling, partitioning, replication, and hotspot assumptions from Topic 04;
- cache hit ratio, refresh cost, storage, and freshness assumptions from Topic 05;
- the cost-driver inventory, low/expected/high model, unit economics, break-even points, and uncertainty register from this topic.

In Topic 07, define repeatable baseline, load, stress, spike, and soak tests; choose representative data and request mixes; measure latency, throughput, error rate, saturation, and resource consumption; and judge results against explicit success criteria. Reconcile modelled resource consumption and cost against test evidence where billing or usage meters are available.

**Next file:** `07-performance-testing-and-capacity-validation.md`.
