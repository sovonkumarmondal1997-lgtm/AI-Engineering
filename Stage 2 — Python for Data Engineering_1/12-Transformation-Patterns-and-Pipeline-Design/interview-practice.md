# Module 2.12 — Transformation Patterns and Pipeline Design
# Interview Practice — Questions and Solutions

## How to Use This Interview Practice

Use this as an interview simulation, not as a memorization sheet.

- Read the problem and formulate an answer aloud.
- State assumptions and identify the data grain.
- Define the run contract and correctness requirements.
- Explain the simplest correct design.
- Discuss retries, duplicates, late data, state or backfills where relevant.
- Explain performance, cost and operational trade-offs.
- State how you would verify correctness.
- Then compare your answer with the provided solution.

### Recommended Answer Pattern

**Clarify assumptions → define grain → define run contract → propose design → discuss failure modes → discuss retries/late data/duplicates → discuss performance → state trade-offs → explain verification.**

---

# Part I — Basic Interview Questions

## Question 1 — Refactor a 1,000-line ETL script

### Problem / Scenario

A single orders script reads files, transforms rows, writes tables, calculates dates, logs failures, and contains recovery logic.

### Interview Question

How would you refactor it into a production-grade transformation pipeline?

### What the Interviewer Is Testing

ETL boundaries, deterministic transformations, RunContext, contracts and testability.

### Expected Answer / Solution

Put readers and writers at the edges; keep transformation functions as pure as practical; introduce a RunContext with run_id, logical interval and configuration; define explicit step contracts; validate inputs and outputs; and keep the CLI thin. Partitioned outputs should be explicit rather than hidden inside transformation functions.

### How to Reason About It

Start with the data grain and run contract. Separate I/O from business transformation, remove hidden state, make logical time explicit, then define deterministic outputs and tests.

### Production Considerations

Keep now(), random(), hidden latest-state queries, global mutable state, and mid-step file writes out of core transformations unless deliberately injected as inputs or side effects.

### Common Weak Answers / Mistakes

Weak answers merely split one script into several files. Strong answers explain why the new boundaries improve replay, testing, recovery and observability.

### Strong Candidate Signals

Strong candidates explicitly demonstrate etl boundaries, deterministic transformations, runcontext, contracts and testability. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

A production transformation pipeline makes data flow, time scope and side effects explicit.

---

## Question 2 — RunContext and logical data intervals

### Problem / Scenario

A daily job produces different historical results depending on the machine clock because transformations call now() and discover the latest available data.

### Interview Question

What belongs in RunContext, and why should transformations use logical dates or intervals instead of implicit current time?

### What the Interviewer Is Testing

Deterministic execution and explicit run contracts.

### Expected Answer / Solution

Include run_id, logical date/data interval, configuration and execution metadata required by steps. Transformations should consume the requested interval rather than infer it from wall-clock time or hidden latest state.

### How to Reason About It

Separate execution time from business/data time. Ask which interval is being processed and pass that interval explicitly through the pipeline.

### Production Considerations

Clock-dependent transformations are hard to reproduce and backfill. A RunContext also gives retries and audits a stable identity.

### Common Weak Answers / Mistakes

Strong candidates distinguish wall-clock time, logical data time and run identity.

### Strong Candidate Signals

Strong candidates explicitly demonstrate deterministic execution and explicit run contracts. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Logical intervals turn a pipeline run into a reproducible unit of work.

---

## Question 3 — Explain idempotency

### Problem / Scenario

An orders partition is submitted twice after a retry, and the business result must not contain duplicate orders.

### Interview Question

What does idempotency mean for this pipeline, and how would you implement it?

### What the Interviewer Is Testing

Idempotency as convergence of durable output.

### Expected Answer / Solution

The same logical execution should converge to the same intended durable state. For immutable partitions, partition overwrite can be appropriate; for mutable records, deterministic deduplication plus merge/upsert can be appropriate. The target grain and winner rules must be explicit.

### How to Reason About It

Define the target invariant and unique grain first. Then select a load strategy whose repeated execution converges rather than appends another copy.

### Production Considerations

An operation can succeed twice and still be non-idempotent if it creates duplicate durable records.

### Common Weak Answers / Mistakes

Strong candidates connect idempotency to retries, grain, deduplication and load semantics.

### Strong Candidate Signals

Strong candidates explicitly demonstrate idempotency as convergence of durable output. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Idempotency is a property of resulting state, not merely successful execution.

---

## Question 4 — Append versus overwrite versus merge

### Problem / Scenario

A source contains immutable daily snapshots, while another source contains mutable customer records and out-of-order updates.

### Interview Question

How would you choose between append, partition overwrite and merge?

### What the Interviewer Is Testing

Matching load strategy to source and target semantics.

### Expected Answer / Solution

Use append when accumulating immutable records is the intended contract; partition overwrite when a complete immutable partition can be deterministically rebuilt; and merge/upsert when mutable records require updates or deletes.

### How to Reason About It

Ask whether records can change, what uniquely identifies a target row, how retries behave, and whether the whole partition can be replaced safely.

### Production Considerations

Using append for mutable CDC can create duplicates or stale versions. Using merge for simple immutable partitions may add unnecessary complexity and cost.

### Common Weak Answers / Mistakes

Strong candidates justify the strategy from data shape rather than tool preference.

### Strong Candidate Signals

Strong candidates explicitly demonstrate matching load strategy to source and target semantics. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Load strategy should follow data semantics and correctness requirements.

---

## Question 5 — Incremental processing versus full rebuild

### Problem / Scenario

A two-year revenue model changes only for a small set of recent partitions during normal operation.

### Interview Question

When would you choose incremental processing, and when is a full rebuild appropriate?

### What the Interviewer Is Testing

Incremental efficiency, dependency analysis and the full-refresh escape hatch.

### Expected Answer / Solution

Use incremental processing when affected inputs and outputs can be identified safely. Use a full rebuild when logic changes globally, dependencies cannot be bounded confidently, or incremental correctness cannot be established.

### How to Reason About It

Define what changed, determine affected partitions through dependency semantics, estimate cost, and compare that with the confidence of the incremental path.

### Production Considerations

Incremental jobs can silently miss non-local changes. Full rebuilds are simpler but may be expensive or operationally disruptive.

### Common Weak Answers / Mistakes

Strong candidates treat this as a correctness and dependency decision, not just a performance decision.

### Strong Candidate Signals

Strong candidates explicitly demonstrate incremental efficiency, dependency analysis and the full-refresh escape hatch. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Incremental processing is useful only when the affected set can be identified correctly.

---

## Question 6 — Late-arriving data and lookback

### Problem / Scenario

Most mobile events arrive within one day, but some arrive several days after event time.

### Interview Question

How would you design a reprocessing/lookback window?

### What the Interviewer Is Testing

Event time, load time, lateness distribution and correctness/cost trade-offs.

### Expected Answer / Solution

Measure the lateness distribution and choose a routine window based on observed behavior and business requirements. Data outside the window needs a targeted repair/backfill path rather than silent loss.

### How to Reason About It

Define the business partitioning time, measure p95/p99 lateness, select a cost-appropriate routine window, and explicitly handle exceptional late records.

### Production Considerations

An arbitrary window can miss valid data or waste compute. Published periods also need a restatement policy.

### Common Weak Answers / Mistakes

Strong candidates quantify lateness and describe both routine and exceptional paths.

### Strong Candidate Signals

Strong candidates explicitly demonstrate event time, load time, lateness distribution and correctness/cost trade-offs. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

A lookback window is an operational policy balancing completeness and compute cost.

---

## Question 7 — Hash keys versus hash diffs

### Problem / Scenario

A customer dimension needs a stable deterministic identifier and a way to detect tracked-attribute changes.

### Interview Question

What is the difference between a hash key and a hash diff?

### What the Interviewer Is Testing

Deterministic hashing for identity and change detection.

### Expected Answer / Solution

A hash key can deterministically derive an identifier from canonical business-key values. A hash diff fingerprints selected attributes so changes can be detected without comparing every field individually.

### How to Reason About It

Define the exact fields and canonical serialization first, then choose an appropriate deterministic hash such as SHA-256 and a stable output representation.

### Production Considerations

Raw concatenation can create Python/SQL mismatches. Hashing is not automatically anonymization or pseudonymisation.

### Common Weak Answers / Mistakes

Strong candidates distinguish identity from change detection and emphasize canonicalization.

### Strong Candidate Signals

Strong candidates explicitly demonstrate deterministic hashing for identity and change detection. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Hash correctness depends on the serialization contract as much as the hash algorithm.

---

## Question 8 — Safe lookup enrichment

### Problem / Scenario

Revenue is joined to a product-category reference table, and the metric unexpectedly doubles.

### Interview Question

What would you check before trusting the enrichment?

### What the Interviewer Is Testing

Lookup uniqueness, join cardinality, missing matches and temporal semantics.

### Expected Answer / Solution

Check reference-key uniqueness, compare row counts and measures before/after the join, identify fan-out keys, and determine whether a point-in-time lookup is required.

### How to Reason About It

Isolate the enrichment step, measure cardinality by key, validate the reference contract, and define missing-match behavior.

### Production Considerations

A many-to-one assumption that is not enforced can become many-to-many and multiply measures.

### Common Weak Answers / Mistakes

Strong candidates use cardinality and reconciliation evidence instead of guessing.

### Strong Candidate Signals

Strong candidates explicitly demonstrate lookup uniqueness, join cardinality, missing matches and temporal semantics. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

An enrichment join needs an explicit and tested cardinality contract.

---

## Question 9 — Why metadata-driven pipelines exist

### Problem / Scenario

A platform has hundreds of datasets that share extraction, validation, deduplication and loading patterns but differ in source, target, keys and ownership.

### Interview Question

Why use metadata/configuration instead of copying similar Python code?

### What the Interviewer Is Testing

Configuration versus reusable code, validation and standardization.

### Expected Answer / Solution

Put declarative dataset-specific properties into validated configuration and keep reusable behavior in code. Pydantic can validate DatasetConfig; registries/plugins can handle controlled variations.

### How to Reason About It

Identify what varies by dataset, validate it before execution, and keep behavior and invariants in reusable code.

### Production Considerations

Excessive flags or executable expressions can turn YAML into an opaque programming language and create an inner-platform problem.

### Common Weak Answers / Mistakes

Strong candidates explain the boundary between data describing a pipeline and code implementing behavior.

### Strong Candidate Signals

Strong candidates explicitly demonstrate configuration versus reusable code, validation and standardization. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Metadata-driven design reduces duplicated implementation without making configuration responsible for arbitrary logic.

---

## Question 10 — Checkpoints and dbt dependencies

### Problem / Scenario

A multi-step pipeline finishes staging and intermediate work but fails before its final output. A dbt project also contains dependent models.

### Interview Question

What role do checkpoints play, and how does dbt represent dependencies?

### What the Interviewer Is Testing

Durable progress, safe retry and dbt's dependency DAG.

### Expected Answer / Solution

A checkpoint records durable progress such as step or partition status so recovery can resume safely. dbt uses ref() and source() to declare dependencies, producing a DAG that determines build order.

### How to Reason About It

Define what durable output exists, what state is committed, and which steps are safe to rerun. In dbt, distinguish source declarations from model-to-model refs.

### Production Considerations

Marking COMPLETE before output is durable can cause data loss on retry. A model list without dependencies does not communicate the full DAG.

### Common Weak Answers / Mistakes

Strong candidates connect state to actual durable output and explain ref/source semantics.

### Strong Candidate Signals

Strong candidates explicitly demonstrate durable progress, safe retry and dbt's dependency dag. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Checkpoint state is useful only when it corresponds to verifiable durable progress.

---

# Part II — Moderate Interview Questions

## Question 11 — Remove hidden side effects

### Problem / Scenario

A transformation calls now(), queries a latest-customer table, and writes a temporary file before returning a DataFrame.

### Interview Question

How would you refactor it and what would you test?

### What the Interviewer Is Testing

Functional transformation design and deterministic testability.

### Expected Answer / Solution

Move reads and writes to edges, pass time and required reference data explicitly, and return deterministic transformation results. Test fixed inputs against expected outputs and separately test the I/O boundaries.

### How to Reason About It

Classify every hidden dependency as input, state or side effect, then make it explicit in the run contract.

### Production Considerations

Hidden latest-state queries make historical replay unstable; mid-step writes complicate recovery and partial failure handling.

### Common Weak Answers / Mistakes

Strong candidates can explain exactly how each hidden dependency becomes explicit.

### Strong Candidate Signals

Strong candidates explicitly demonstrate functional transformation design and deterministic testability. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Determinism comes from controlling every input that can affect transformation output.

---

## Question 12 — Design a CDC merge

### Problem / Scenario

A CDC source can resend events and sometimes delivers an older update after a newer update.

### Interview Question

How would you design the target load?

### What the Interviewer Is Testing

Batch deduplication, version ordering, merge correctness and idempotency.

### Expected Answer / Solution

Define the business key and deterministic version rule, deduplicate the source batch, select the winning version, and use a target merge with a version guard so stale records cannot overwrite newer state. Define delete/tombstone behavior explicitly.

### How to Reason About It

Separate duplicate suppression from ordering. Then define merge semantics and concurrency behavior.

### Production Considerations

MERGE does not automatically deduplicate its source. updated_at may be insufficient if timestamps tie or are unreliable.

### Common Weak Answers / Mistakes

Strong candidates distinguish duplicates from legitimate successive versions and explain stale-update protection.

### Strong Candidate Signals

Strong candidates explicitly demonstrate batch deduplication, version ordering, merge correctness and idempotency. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

A correct CDC merge needs both deterministic winner selection and target-side version protection.

---

## Question 13 — Find affected partitions

### Problem / Scenario

A customer correction arrives today but changes historical revenue attribution.

### Interview Question

How would you determine which revenue partitions need reprocessing?

### What the Interviewer Is Testing

Dependency-aware incremental processing.

### Expected Answer / Solution

Trace the changed customer through affected orders and map those records to the revenue partitions they contribute to. Reprocess the affected set rather than assuming today's load date identifies the outputs.

### How to Reason About It

Start with target grain, identify changed source keys, trace downstream dependencies, and materialize the affected partition set.

### Production Considerations

Using only _loaded_at or source load date can miss historical outputs affected by a dimension/reference change.

### Common Weak Answers / Mistakes

Strong candidates reason from data dependencies rather than ingestion timestamps.

### Strong Candidate Signals

Strong candidates explicitly demonstrate dependency-aware incremental processing. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Incremental scope follows the dependency graph of the transformation.

---

## Question 14 — Diagnose a late-data gap

### Problem / Scenario

A report misses events that arrived four days after event time, while the pipeline only reprocesses two days.

### Interview Question

How would you investigate and fix it?

### What the Interviewer Is Testing

Incident diagnosis, lookback policy and targeted repair.

### Expected Answer / Solution

Compare event_time and load_time, quantify lateness, identify missed partitions, run a targeted repair, then reassess the normal window based on observed distribution and business impact.

### How to Reason About It

Use symptom → hypotheses → investigation → root cause → fix → prevention. Separate immediate repair from changing steady-state policy.

### Production Considerations

Extending the lookback indefinitely can be expensive; ignoring known late arrivals guarantees recurrence.

### Common Weak Answers / Mistakes

Strong candidates quantify the lateness and define what happens beyond the normal window.

### Strong Candidate Signals

Strong candidates explicitly demonstrate incident diagnosis, lookback policy and targeted repair. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Late-data handling needs a routine policy plus an exceptional repair mechanism.

---

## Question 15 — Investigate a Python/SQL hash mismatch

### Problem / Scenario

Python and SQL generate different customer hash keys for records that appear identical.

### Interview Question

How would you investigate?

### What the Interviewer Is Testing

Canonical serialization and cross-engine parity.

### Expected Answer / Solution

Compare the exact preimage bytes: column order, delimiters, trimming, case, NULL tokens, numeric formatting, timestamps/time zones, UTF-8 encoding, algorithm and hex/binary representation. Use shared test vectors.

### How to Reason About It

Do not change the hash algorithm first. Prove that the canonical input bytes are identical, then compare digest representation.

### Production Considerations

Timestamp, NULL and numeric formatting are frequent parity failures.

### Common Weak Answers / Mistakes

Strong candidates define a cross-engine canonicalization contract.

### Strong Candidate Signals

Strong candidates explicitly demonstrate canonical serialization and cross-engine parity. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Cross-engine hashing requires identical canonical inputs and digest interpretation.

---

## Question 16 — Point-in-time tax lookup

### Problem / Scenario

Orders must use the tax rate valid when the order occurred rather than today's rate.

### Interview Question

How would you design the lookup?

### What the Interviewer Is Testing

Temporal reference data and as-of correctness.

### Expected Answer / Solution

Store validity intervals or equivalent temporal versions and perform an as-of join. Validate that exactly one applicable version exists, with explicit policies for gaps and overlaps.

### How to Reason About It

Define valid time and reference grain, test boundary timestamps, and enforce temporal uniqueness.

### Production Considerations

A current-state dictionary lookup makes historical results change when reference data changes. Overlapping versions can cause fan-out.

### Common Weak Answers / Mistakes

Strong candidates distinguish current state from historical truth.

### Strong Candidate Signals

Strong candidates explicitly demonstrate temporal reference data and as-of correctness. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Time-varying reference data requires temporal semantics, not a simple dictionary join.

---

## Question 17 — Design DatasetConfig

### Problem / Scenario

A generic engine needs source, target, keys, load strategy, partitioning, quality rules, owner and SLA.

### Interview Question

What belongs in DatasetConfig and how would you validate it?

### What the Interviewer Is Testing

Configuration schema design and code/config boundaries.

### Expected Answer / Solution

DatasetConfig should hold declarative properties. Pydantic can enforce types, required fields, allowed strategies, defaults and cross-field constraints before execution.

### How to Reason About It

List variable properties, distinguish required from optional values, validate combinations, and reject unsafe or incomplete configurations early.

### Production Considerations

Putting arbitrary executable expressions into YAML blurs code and configuration and moves failures to runtime.

### Common Weak Answers / Mistakes

Strong candidates discuss schema validation, dry-run behavior and controlled escape hatches.

### Strong Candidate Signals

Strong candidates explicitly demonstrate configuration schema design and code/config boundaries. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Configuration should describe a valid execution plan, not become an unbounded programming language.

---

## Question 18 — Recover after output-before-checkpoint crash

### Problem / Scenario

A partition output is written successfully, but the process crashes before recording COMPLETE.

### Interview Question

What should happen on retry?

### What the Interviewer Is Testing

Checkpoint ordering, durable state and idempotent recovery.

### Expected Answer / Solution

Retry should verify or safely replace durable output and rerun the partition as needed. The output/load must be idempotent, and COMPLETE should only be recorded after durable output is committed and validated.

### How to Reason About It

Treat state as evidence about data, not as the data itself. Define recovery for every output/state boundary.

### Production Considerations

Blindly skipping because output exists can accept corrupt output. Marking state first can cause false completion.

### Common Weak Answers / Mistakes

Strong candidates explain output-before-checkpoint ordering and state repair.

### Strong Candidate Signals

Strong candidates explicitly demonstrate checkpoint ordering, durable state and idempotent recovery. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Checkpointing is safe only when state and durable output have an explicit consistency contract.

---

## Question 19 — Design a dbt incremental fact

### Problem / Scenario

A fact table receives new and corrected order lines and must tolerate duplicates and late data.

### Interview Question

How would you structure the dbt incremental model?

### What the Interviewer Is Testing

dbt incremental semantics, grain, unique_key, lookback and reconciliation.

### Expected Answer / Solution

Define target grain and unique_key, select the necessary source changes using a measured predicate/lookback, deduplicate the incremental input, and choose an appropriate strategy such as merge where supported. Validate uniqueness and compare selected periods with full refresh.

### How to Reason About It

Define target invariant first, then source-change scope, late-data coverage, deduplication and write semantics.

### Production Considerations

A current-day-only predicate can miss late updates. A unique_key does not compensate for missing source rows or ambiguous winners.

### Common Weak Answers / Mistakes

Strong candidates map dbt settings to the same correctness contract used in custom transformations.

### Strong Candidate Signals

Strong candidates explicitly demonstrate dbt incremental semantics, grain, unique_key, lookback and reconciliation. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

dbt incremental correctness still depends on explicit grain, change scope and deduplication.

---

## Question 20 — Choose SQL versus Python/Polars

### Problem / Scenario

A transformation has relational joins and filters plus a specialized transformation that is clearer in Python/Polars.

### Interview Question

How would you decide where the boundary belongs?

### What the Interviewer Is Testing

Engine selection, maintainability, execution cost and clear transformation boundaries.

### Expected Answer / Solution

Use SQL for relational work that fits the database engine and use Python/Polars when it materially improves expression, validation or capability. Keep the boundary explicit and deterministic.

### How to Reason About It

Assess data location, operation type, scale, engine capability, movement cost and maintainability.

### Production Considerations

Using Python everywhere can increase movement and memory pressure; forcing awkward logic into SQL can reduce clarity.

### Common Weak Answers / Mistakes

Strong candidates compare semantics and operational characteristics rather than declaring one language universally superior.

### Strong Candidate Signals

Strong candidates explicitly demonstrate engine selection, maintainability, execution cost and clear transformation boundaries. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Choose the execution engine based on the transformation and operational contract.

---

# Part III — Hard Interview Questions

## Question 21 — CDC duplicates survive a retry

### Problem / Scenario

After a retry, a customer target contains duplicate logical records even though the pipeline uses MERGE. The source contains duplicate and out-of-order CDC events.

### Interview Question

Diagnose the design and explain how you would make it correct.

### What the Interviewer Is Testing

Debugging across source deduplication, version ordering, merge keys, idempotency and concurrency.

### Expected Answer / Solution

Inspect target grain, source duplicates, merge keys, winner-selection logic and concurrent execution. Deduplicate the source deterministically, apply a version guard, and coordinate conflicting partition/entity writes where necessary.

### How to Reason About It

Use symptom → hypotheses → investigation → root cause → fix → prevention. Verify the source-to-merge input is unique at the merge grain and replay the same interval twice.

### Production Considerations

MERGE does not automatically make a duplicate source batch safe. A wrong key or missing version guard can still corrupt state.

### Common Weak Answers / Mistakes

Strong candidates separate batch deduplication, version ordering, target semantics and concurrency.

### Strong Candidate Signals

Strong candidates explicitly demonstrate debugging across source deduplication, version ordering, merge keys, idempotency and concurrency. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Idempotent CDC requires deterministic source selection, correct keys and safe concurrent execution.

### Likely Interviewer Follow-Ups

- **What if the same CDC batch runs twice?**
  - The deduplication and idempotent merge should converge to the same target state.

- **What if an older version arrives after a newer one?**
  - The target version guard must prevent stale data from regressing the record.

---

## Question 22 — Incremental revenue silently misses history

### Problem / Scenario

A daily revenue job is green, but a periodic full rebuild shows historical differences.

### Interview Question

How would you investigate?

### What the Interviewer Is Testing

Incremental correctness, dependency propagation and equivalence testing.

### Expected Answer / Solution

Compare the incremental input selection with the full-refresh input, inspect late-data handling, reference dependencies and affected-partition logic, then reproduce the first divergent period and reconcile keys, counts, sums and fingerprints.

### How to Reason About It

Treat full rebuild as a reference execution for the same source state. Trace the first missing or differently transformed input through the dependency chain.

### Production Considerations

Successful execution does not prove semantic correctness. Incremental predicates can miss changes propagated through joins.

### Common Weak Answers / Mistakes

Strong candidates use equivalence and reconciliation evidence rather than job status.

### Strong Candidate Signals

Strong candidates explicitly demonstrate incremental correctness, dependency propagation and equivalence testing. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

An incremental pipeline is correct only if it produces the same intended result as the complete transformation for the relevant state.

### Likely Interviewer Follow-Ups

- **How do you prove incremental correctness?**
  - Compare affected periods with a full rebuild and reconcile keys, counts, sums and fingerprints.

- **Why not full-refresh every day?**
  - Because safely bounded incremental work can reduce cost and runtime.

---

## Question 23 — Late data beyond seven days

### Problem / Scenario

A routine seven-day lookback misses a small but material number of events arriving 20 days late and affecting a closed monthly report.

### Interview Question

How would you handle this without recomputing months of history every day?

### What the Interviewer Is Testing

Routine lookback, targeted backfill, restatement and publication semantics.

### Expected Answer / Solution

Keep the routine window if its cost/coverage trade-off is justified, but route older events to targeted partition repair. Validate the restatement and retain audit history; for closed periods, follow an explicit restatement policy.

### How to Reason About It

Separate normal lateness from exceptional lateness, identify affected outputs, repair them, and decide whether observed tail behavior warrants changing the normal window.

### Production Considerations

Continuously widening the lookback can be expensive; silently dropping late events creates incorrect history.

### Common Weak Answers / Mistakes

Strong candidates balance correctness, cost and business publication semantics.

### Strong Candidate Signals

Strong candidates explicitly demonstrate routine lookback, targeted backfill, restatement and publication semantics. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Bounded routine processing and targeted exceptional repair can coexist.

### Likely Interviewer Follow-Ups

- **What happens outside the normal lookback?**
  - Route the records to targeted reprocessing rather than silently dropping them.

- **When should the window change?**
  - When observed lateness, business impact or compute economics justify a new steady-state policy.

---

## Question 24 — Reference correction changes history

### Problem / Scenario

A product-category reference table is corrected today and historical revenue by category changes when the model is rerun.

### Interview Question

How would you determine whether the new history is correct?

### What the Interviewer Is Testing

Point-in-time enrichment, reference versioning and historical reproducibility.

### Expected Answer / Solution

First establish whether the business definition requires the value valid at event time or the corrected current truth. For historical reproducibility, use versioned/as-of reference data. If correction should restate history, perform targeted recomputation, reconciliation and audit.

### How to Reason About It

Define temporal semantics before changing data. Then identify affected partitions and choose current-state versus historical semantics deliberately.

### Production Considerations

A reference correction is not automatically a reason to rewrite all historical facts.

### Common Weak Answers / Mistakes

Strong candidates distinguish technical possibilities from business-defined temporal truth.

### Strong Candidate Signals

Strong candidates explicitly demonstrate point-in-time enrichment, reference versioning and historical reproducibility. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Reference-data changes require an explicit historical semantics and restatement contract.

### Likely Interviewer Follow-Ups

- **Why not always use the latest reference value?**
  - It changes historical semantics and can make prior outputs irreproducible.

- **How do you validate a restatement?**
  - Recompute affected partitions, reconcile them and preserve audit evidence.

---

## Question 25 — Lookup fan-out doubles revenue

### Problem / Scenario

Revenue doubles immediately after a product enrichment step while source orders are unchanged.

### Interview Question

Walk through your incident investigation and prevention strategy.

### What the Interviewer Is Testing

Join cardinality, uniqueness validation, reconciliation and prevention.

### Expected Answer / Solution

Compare row counts and measures before/after the join, identify keys with multiple matches, inspect reference duplicates and verify temporal join conditions. Add uniqueness/cardinality quality gates before aggregation.

### How to Reason About It

Isolate the enrichment step, quantify fan-out by key, establish intended cardinality, correct the reference or join, and rerun reconciliation.

### Production Considerations

Arbitrarily choosing one duplicate reference row can hide a temporal or ownership problem.

### Common Weak Answers / Mistakes

Strong candidates use measurable cardinality invariants and targeted diagnostics.

### Strong Candidate Signals

Strong candidates explicitly demonstrate join cardinality, uniqueness validation, reconciliation and prevention. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Enrichment correctness begins with an explicit cardinality contract.

### Likely Interviewer Follow-Ups

- **How do you prevent fan-out recurring?**
  - Validate lookup uniqueness/cardinality before the enrichment.

- **What if multiple versions are legitimate?**
  - Use point-in-time semantics or an explicit version-selection rule.

---

## Question 26 — Design the 300-dataset engine boundary

### Problem / Scenario

A platform has 300 structurally similar datasets with a few dataset-specific transformations.

### Interview Question

How would you decide what belongs in configuration versus code?

### What the Interviewer Is Testing

Metadata-driven architecture, registries, validation, safe SQL generation and escape hatches.

### Expected Answer / Solution

Put source, target, keys, partitioning, load strategy, quality rules, owner and SLA in validated configuration. Keep transformation behavior in code, use registries/plugins for controlled variations, and provide a custom escape hatch for genuinely exceptional logic.

### How to Reason About It

Classify each varying property. If it is validated data interpreted by stable code, it can be configuration. If it is arbitrary behavior, it belongs in code.

### Production Considerations

Excessive flags make configuration a programming language. An engine that cannot handle exceptions becomes an inner-platform problem.

### Common Weak Answers / Mistakes

Strong candidates discuss Pydantic validation, dry runs, allowlists/identifier quoting and plugin boundaries.

### Strong Candidate Signals

Strong candidates explicitly demonstrate metadata-driven architecture, registries, validation, safe sql generation and escape hatches. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Configuration should express stable variation while code owns behavior and invariants.

### Likely Interviewer Follow-Ups

- **How do you test a configuration before execution?**
  - Validate the schema and produce a dry-run execution plan without committing data.

- **What if one dataset is genuinely exceptional?**
  - Use a controlled registered plugin or escape hatch rather than multiplying generic flags.

---

## Question 27 — Checkpoint says COMPLETE but output is missing

### Problem / Scenario

A partition ledger says COMPLETE, but the expected durable output is absent.

### Interview Question

How would you investigate and prevent this state corruption?

### What the Interviewer Is Testing

State/data commit ordering, repairability and audit evidence.

### Expected Answer / Solution

Inspect run/audit records and the write/checkpoint ordering. Repair the ledger by invalidating the false completion and rerun or reconcile the partition. Change the implementation so completion is recorded only after durable output is committed and validated.

### How to Reason About It

Treat COMPLETE as an assertion about durable data. Find when output was committed, then repair state and replay deterministically.

### Production Considerations

Marking state before output creates false progress. A state system without repair tooling turns incidents into manual intervention.

### Common Weak Answers / Mistakes

Strong candidates state explicit invariants and propose a repair path.

### Strong Candidate Signals

Strong candidates explicitly demonstrate state/data commit ordering, repairability and audit evidence. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

State must agree with durable output and must be repairable when it does not.

### Likely Interviewer Follow-Ups

- **What if output exists but is corrupt?**
  - Validate it; if invalid, invalidate state and safely rerun the partition.

- **How should state be repaired?**
  - Treat the ledger as an assertion, reconcile it with durable data and correct the state.

---

## Question 28 — Two workers process one partition

### Problem / Scenario

Two workers start the same dataset partition after a scheduler retry.

### Interview Question

How would you prevent or safely handle the concurrent writers?

### What the Interviewer Is Testing

Concurrency, advisory locks, idempotency and exactly-once effects.

### Expected Answer / Solution

Use a dataset/partition-scoped advisory lock or equivalent coordination, with stale-owner recovery. Keep the transformation and write idempotent so a retry remains safe even if coordination fails.

### How to Reason About It

Define the lock key, ownership lifecycle, timeout/stale handling and retry behavior. Identify which work can safely run concurrently.

### Production Considerations

A global lock destroys throughput; a lock with no stale recovery can deadlock progress. Locks alone do not replace idempotent effects.

### Common Weak Answers / Mistakes

Strong candidates combine coordination with idempotent recovery.

### Strong Candidate Signals

Strong candidates explicitly demonstrate concurrency, advisory locks, idempotency and exactly-once effects. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Locks reduce races; idempotency makes failure recovery safe.

### Likely Interviewer Follow-Ups

- **Why not rely only on a lock?**
  - A lock coordinates active workers but does not replace idempotent crash recovery.

- **How do you handle stale ownership?**
  - Use bounded ownership and a safe stale-recovery policy.

---

## Question 29 — dbt incremental differs from full refresh

### Problem / Scenario

A dbt incremental model has different totals from the same model run with --full-refresh.

### Interview Question

How would you diagnose the discrepancy?

### What the Interviewer Is Testing

Incremental predicate correctness, unique keys, lookback, deduplication, schema evolution and reconciliation.

### Expected Answer / Solution

Compare the records selected by the incremental predicate with full-refresh inputs, inspect unique_key and winner logic, verify late-data lookback, inspect on_schema_change behavior, and reconcile the first divergent partition.

### How to Reason About It

Use full refresh as a reference path for the same source state. Trace the first divergence rather than comparing only final totals.

### Production Considerations

A syntactically valid incremental model can still be semantically incomplete. unique_key does not fix missing inputs.

### Common Weak Answers / Mistakes

Strong candidates treat dbt configuration as an implementation of a correctness contract.

### Strong Candidate Signals

Strong candidates explicitly demonstrate incremental predicate correctness, unique keys, lookback, deduplication, schema evolution and reconciliation. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Incremental and full-refresh paths should converge under the same authoritative source state.

### Likely Interviewer Follow-Ups

- **What does dbt not solve automatically?**
  - It does not guarantee correct source semantics, late-data handling or a correct incremental predicate.

- **Why compare to full refresh?**
  - It provides a concrete reference execution for the same source state.

---

## Question 30 — Backfill with a logic-version change

### Problem / Scenario

A revenue transformation changes its business rule, but only some historical partitions are affected. The existing target contains outputs produced by an older transformation version.

### Interview Question

How would you decide which partitions to rebuild and how would you prevent old and new logic from being mixed?

### What the Interviewer Is Testing

Transform versioning, affected-partition selection, deterministic backfills and validation.

### Expected Answer / Solution

Assign a new transform_version, identify the affected partitions from the changed logic and dependency graph, rebuild them deterministically into a shadow target, validate the result, and promote it atomically. Record the logic version with the partition state so future retries know which implementation produced the output.

### How to Reason About It

Define the changed invariant first, then determine the minimum affected partition set. Keep old and new outputs distinguishable, validate the new result, and only then replace the old result.

### Production Considerations

Blindly rerunning every historical partition may waste resources; overwriting production partitions in place can leave mixed versions after failure. State must also be invalidated when logic changes.

### Common Weak Answers / Mistakes

Strong candidates treat transformation logic as versioned state and explain how affected partitions and downstream recomputation are identified.

### Strong Candidate Signals

Strong candidates explicitly demonstrate transform versioning, affected-partition selection, deterministic backfills and validation. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Logic changes are data changes: affected outputs need version-aware rebuild and controlled promotion.

### Likely Interviewer Follow-Ups

- **Why record a transform version?**
  - It lets state and outputs be tied to the exact transformation logic that produced them.

- **How do you avoid mixing old and new results?**
  - Build and validate the new version separately, then promote it atomically.

---

# Part IV — Advanced Interview Questions

## Question 31 — Architecture for hundreds of datasets

### Problem / Scenario

Design a transformation layer for hundreds of similar datasets with deterministic runs, configurable load strategies, quality rules, retries, backfills and controlled exceptions.

### Interview Question

Design the architecture and explain what belongs in code, configuration, metadata and state.

### What the Interviewer Is Testing

Architecture reasoning within Module 2.12: metadata-driven execution, RunContext, validation, state, recovery and maintainability.

### Expected Answer / Solution

Use a generic engine with validated DatasetConfig, registered transformation/load strategies, explicit RunContext, deterministic partition-scoped steps, quality gates, durable run/partition state and advisory locks. Configuration describes dataset-specific properties; code owns reusable behavior and invariants; plugins handle controlled variation.

### How to Reason About It

Begin with grain and run contract. Define configuration schema, execution lifecycle, strategy registry, state model, concurrency key, quality gates, dry-run and repair paths. Explain onboarding and exceptions.

### Production Considerations

Over-generalization creates an inner platform. Excessive flags make behavior opaque. Generated SQL needs safe identifier handling and configuration needs strong validation.

### Common Weak Answers / Mistakes

Strong candidates explain contracts and failure modes rather than naming a generic framework.

### Strong Candidate Signals

Strong candidates explicitly demonstrate architecture reasoning within module 2.12: metadata-driven execution, runcontext, validation, state, recovery and maintainability. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

A transformation platform is a set of explicit contracts, not just reusable scripts.

### Likely Interviewer Follow-Ups

- **How do you onboard an exceptional dataset?**
  - Use a controlled plugin/escape hatch while preserving the common engine contract.

- **How do you keep configuration understandable?**
  - Limit it to validated declarative properties and keep behavior in code.

---

## Question 32 — Idempotent CDC transformation platform

### Problem / Scenario

A high-volume CDC source produces duplicates, out-of-order versions, deletes and late delivery. The target must converge correctly after retries and concurrent execution.

### Interview Question

Design the transformation and load semantics.

### What the Interviewer Is Testing

End-to-end correctness across deduplication, version guards, merge, late data and concurrency.

### Expected Answer / Solution

Define business key and version ordering; deduplicate each input batch deterministically; use merge/upsert with a target-side version guard; represent deletes explicitly; partition processing and coordinate conflicting writes; keep every effect idempotent.

### How to Reason About It

Define the target invariant first, then source normalization, winner selection, merge behavior, late-data handling, concurrency and recovery. Finish with reconciliation.

### Production Considerations

Arrival order is not a version rule. MERGE alone does not solve duplicate input or stale updates. Locking alone does not solve crash recovery.

### Common Weak Answers / Mistakes

Strong candidates reason about convergence under reordering and repeated delivery.

### Strong Candidate Signals

Strong candidates explicitly demonstrate end-to-end correctness across deduplication, version guards, merge, late data and concurrency. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Correct CDC processing is a convergence problem under at-least-once, out-of-order delivery.

### Likely Interviewer Follow-Ups

- **How do you prove CDC idempotency?**
  - Replay the same interval repeatedly and verify the durable state converges.

- **How do you handle late versions?**
  - Use version ordering and a target guard rather than arrival order.

---

## Question 33 — Safe 12-month backfill

### Problem / Scenario

A business rule changes and 12 months of revenue output must be rebuilt while the daily pipeline continues.

### Interview Question

Design the backfill and promotion strategy.

### What the Interviewer Is Testing

Transform versioning, affected partitions, bounded parallelism, shadow output, validation, atomic swap and downstream invalidation.

### Expected Answer / Solution

Create a new transform_version, identify affected partitions, estimate cost, run with bounded parallelism into shadow output, validate quality/reconciliation, atomically promote validated results, and invalidate/recompute downstream partitions affected by the change.

### How to Reason About It

Separate backfill from live output, make it resumable, protect normal capacity, validate before promotion and record state/audit evidence.

### Production Considerations

Direct production overwrites can leave mixed logic after failure. Unbounded parallelism can starve normal runs.

### Common Weak Answers / Mistakes

Strong candidates describe shadow output, resource limits, atomic promotion and downstream dependency handling.

### Strong Candidate Signals

Strong candidates explicitly demonstrate transform versioning, affected partitions, bounded parallelism, shadow output, validation, atomic swap and downstream invalidation. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Large backfills should be controlled migrations, not oversized daily jobs.

### Likely Interviewer Follow-Ups

- **How do you avoid starving daily workloads?**
  - Bound backfill concurrency and reserve capacity for normal runs.

- **What if the backfill fails halfway?**
  - Resume or rerun affected partitions safely, then validate before promotion.

---

## Question 34 — Late-data architecture at scale

### Problem / Scenario

Most events arrive within one day, p99 lateness is seven days, and a small tail arrives weeks later. Some reports are eventually restated.

### Interview Question

Design steady-state and exceptional late-data paths.

### What the Interviewer Is Testing

Lateness measurement, lookback policy, targeted repair and publication semantics.

### Expected Answer / Solution

Use a measured routine lookback informed by p95/p99 and business impact, route tail events to targeted reprocessing, and define explicit restatement/audit behavior for closed periods. Track event time and load time separately.

### How to Reason About It

Quantify lateness, choose the routine coverage point, identify affected partitions, and define what happens after publication.

### Production Considerations

A percentile alone does not define business tolerance. Recomputing all history for every late event is wasteful.

### Common Weak Answers / Mistakes

Strong candidates balance completeness, compute cost and publication semantics.

### Strong Candidate Signals

Strong candidates explicitly demonstrate lateness measurement, lookback policy, targeted repair and publication semantics. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Late-data handling is both a computation policy and a publication policy.

### Likely Interviewer Follow-Ups

- **Why use p99?**
  - It ties routine processing to observed lateness while leaving an exceptional repair path.

- **What about closed periods?**
  - Use an explicit restatement and audit policy.

---

## Question 35 — Cross-engine deterministic hashing

### Problem / Scenario

Python and SQL must produce identical customer keys and change fingerprints.

### Interview Question

Define a stable cross-engine hashing contract.

### What the Interviewer Is Testing

Canonical serialization, digest representation, schema evolution and collision awareness.

### Expected Answer / Solution

Specify column order, delimiters or framing, trimming/case rules, NULL tokens, numeric/timestamp formats, timezone normalization, UTF-8, hash algorithm and hex/binary representation. Publish test vectors and verify parity continuously.

### How to Reason About It

Define bytes first, then hash. Test NULL, empty string, Unicode, timestamps and numeric edge cases. Treat serialization changes as versioned compatibility events.

### Production Considerations

Changing canonicalization can silently change every key. Short hashes increase collision risk, and plain hashing is not anonymization for low-entropy identifiers.

### Common Weak Answers / Mistakes

Strong candidates describe a canonicalization contract and shared test vectors.

### Strong Candidate Signals

Strong candidates explicitly demonstrate canonical serialization, digest representation, schema evolution and collision awareness. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Cross-engine hashing is primarily a serialization-contract problem.

### Likely Interviewer Follow-Ups

- **What if canonicalization changes?**
  - Treat it as a compatibility/versioning event and deliberately migrate affected keys.

- **Why not shorten the digest?**
  - Shorter hashes increase collision risk.

---

## Question 36 — Point-in-time enrichment at scale

### Problem / Scenario

Orders must use customer and tax reference data as valid/known at order time, while reference corrections occur regularly.

### Interview Question

Design the enrichment architecture and preserve historical reproducibility.

### What the Interviewer Is Testing

Temporal semantics, as-of joins, reference versioning, cardinality, performance and targeted restatement.

### Expected Answer / Solution

Model validity or knowledge-time intervals, perform point-in-time joins, enforce uniqueness of the applicable reference version, preserve reference history, and trigger targeted restatements when the business contract requires corrections.

### How to Reason About It

Define valid time versus transaction/knowledge time, test interval boundaries, determine affected fact partitions, and choose broadcast/partitioned join strategies according to data shape.

### Production Considerations

Current-state lookups cannot reproduce historical truth. Overlapping intervals can fan out facts. Caching must not erase temporal semantics.

### Common Weak Answers / Mistakes

Strong candidates connect reference corrections to affected downstream partitions and audit history.

### Strong Candidate Signals

Strong candidates explicitly demonstrate temporal semantics, as-of joins, reference versioning, cardinality, performance and targeted restatement. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Point-in-time correctness requires versioned temporal semantics.

### Likely Interviewer Follow-Ups

- **What if reference intervals overlap?**
  - Treat overlap as a quality failure unless a deterministic selection rule is explicitly defined.

- **How do corrections propagate?**
  - Identify affected fact partitions and run targeted restatements.

---

## Question 37 — Resumable multi-step pipeline

### Problem / Scenario

A pipeline has standardization, casting, hashing, deduplication, enrichment, validation and loading. Failure can occur after any step.

### Interview Question

Design the state and recovery model.

### What the Interviewer Is Testing

Step-level checkpoints, partition ledger, durable state, commit ordering, idempotency, locks and invalidation.

### Expected Answer / Solution

Persist run and partition state, record step status and useful output metadata, commit durable output before COMPLETE, make every step safe to rerun, and support advisory locks, invalidation and state repair. A partition ledger can include dataset, partition, row counts, logic version and timestamps.

### How to Reason About It

Define state transitions and invariants at every boundary, including crashes after output and before state, and state corruption after logic changes.

### Production Considerations

A simple last-successful-step pointer cannot handle corrupted state or changed transformation logic safely.

### Common Weak Answers / Mistakes

Strong candidates distinguish orchestrator state from application-owned data state and explain exactly-once effects under at-least-once execution.

### Strong Candidate Signals

Strong candidates explicitly demonstrate step-level checkpoints, partition ledger, durable state, commit ordering, idempotency, locks and invalidation. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Resumability comes from durable evidence plus idempotent effects.

### Likely Interviewer Follow-Ups

- **What if a worker crashes after output commit?**
  - Verify durable output and safely finalize or rerun state using idempotent semantics.

- **What if the ledger is wrong?**
  - Invalidate/repair state and reconcile it against durable output.

---

## Question 38 — Concurrency and bounded backfills

### Problem / Scenario

Workers process partitions concurrently, but the same partition must not have conflicting writers and a large backfill must not starve daily workloads.

### Interview Question

Design concurrency controls and resource limits.

### What the Interviewer Is Testing

Advisory locks, bounded parallelism, fairness, stale recovery and throughput/correctness trade-offs.

### Expected Answer / Solution

Use partition-scoped locks for conflicting writes, bounded worker pools, and explicit backfill capacity limits or isolation so normal processing retains capacity. Keep effects idempotent and recover stale ownership safely.

### How to Reason About It

Identify serial versus parallel work, define lock lifecycle and stale recovery, then define resource budgets and retry behavior.

### Production Considerations

A global lock harms throughput; no lock risks conflicting writers; unbounded backfill concurrency can starve production.

### Common Weak Answers / Mistakes

Strong candidates balance correctness with throughput and operational fairness.

### Strong Candidate Signals

Strong candidates explicitly demonstrate advisory locks, bounded parallelism, fairness, stale recovery and throughput/correctness trade-offs. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Serialize only what must be serialized and bound everything else.

### Likely Interviewer Follow-Ups

- **How do you avoid backfill starvation?**
  - Bound backfill workers and preserve capacity for normal processing.

- **What if two workers target one partition?**
  - Use a partition-scoped lock plus idempotent effects.

---

## Question 39 — Production dbt transformation layer

### Problem / Scenario

An orders platform needs sources, freshness, staging, intermediate models, customer dimensions, order-line facts, daily revenue, tests, documentation and a Python model.

### Interview Question

How would you structure the dbt project and explain its correctness model?

### What the Interviewer Is Testing

dbt DAG design, materialization, incremental correctness, tests, snapshots, contracts and Python models.

### Expected Answer / Solution

Use sources and staging first, intermediate models next, and marts at the business layer. Use ref()/source() for dependencies. Define explicit grain and unique_key for incremental facts, measured lookback and deduplication, snapshots for appropriate SCD2 history, data/unit tests and model contracts, and Python models only where they fit the transformation.

### How to Reason About It

Explain dependency graph, materializations, source freshness, incremental behavior, tests, snapshots, documentation and full-refresh reconciliation.

### Production Considerations

dbt does not guarantee correct source semantics or incremental predicates. Adapter/version behavior matters.

### Common Weak Answers / Mistakes

Strong candidates explain why each layer and materialization exists rather than listing commands.

### Strong Candidate Signals

Strong candidates explicitly demonstrate dbt dag design, materialization, incremental correctness, tests, snapshots, contracts and python models. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

dbt supplies structure and tooling; transformation correctness still depends on explicit model semantics.

### Likely Interviewer Follow-Ups

- **Why dbt instead of custom Python everywhere?**
  - Use dbt where relational transformations, DAGs, tests, documentation and model semantics fit naturally.

- **What if an incremental model is wrong?**
  - Use full-refresh/reference comparison to diagnose and repair the incremental contract.

---

## Question 40 — Prove correctness under change

### Problem / Scenario

You own the Module 2.12 transformation platform. Leadership asks how you know it remains correct under retries, duplicates, late data, logic changes and historical backfills.

### Interview Question

What invariants and validation strategy would you use?

### What the Interviewer Is Testing

System-level correctness, reconciliation, deterministic execution, idempotency and controlled failure testing.

### Expected Answer / Solution

I would define invariants: repeated execution converges to the same result; duplicate delivery does not change target grain; valid late data is eventually incorporated; incremental output equals a full rebuild for the same source state; enrichment preserves intended cardinality; state matches verified durable output; and backfills are validated before promotion. Test these with reruns, controlled failures/chaos tests and reconciliation.

### How to Reason About It

For each failure mode, define an invariant, a falsifying test and a recovery path. Exercise duplicate, out-of-order, late-data, output/state-crash and logic-version scenarios.

### Production Considerations

Job success, absence of exceptions, or simple row counts do not prove semantic correctness.

### Common Weak Answers / Mistakes

Strong candidates turn 'idempotent' and 'correct' into observable invariants and repeatable tests.

### Strong Candidate Signals

Strong candidates explicitly demonstrate system-level correctness, reconciliation, deterministic execution, idempotency and controlled failure testing. and connect the design to correctness, failure behavior and production trade-offs.

### Key Takeaway

Production correctness is demonstrated through explicit invariants, controlled failures and reconciliation.

### Likely Interviewer Follow-Ups

- **What happens if the same partition runs twice?**
  - The result should converge because transformation and load effects are idempotent.

- **How do you prove a late-data window is sufficient?**
  - Measure lateness and reconcile routine results with targeted/full recomputation.

- **How do you verify checkpoint/data consistency?**
  - Treat state as an assertion and reconcile it against durable outputs and audit metadata.

---

# Coverage and Interview Skills

| Topic | Basic | Moderate | Hard | Advanced |
|---|---:|---:|---:|---:|
| 01 ETL Structure | ✓ | ✓ | ✓ | ✓ |
| 02 Deduplication / Merge | ✓ | ✓ | ✓ | ✓ |
| 03 Incremental / Backfill | ✓ | ✓ | ✓ | ✓ |
| 04 Late Data | ✓ | ✓ | ✓ | ✓ |
| 05 Hashing | ✓ | ✓ | ✓ | ✓ |
| 06 Enrichment | ✓ | ✓ | ✓ | ✓ |
| 07 Metadata / Configuration | ✓ | ✓ | ✓ | ✓ |
| 08 State / Checkpoints | ✓ | ✓ | ✓ | ✓ |
| 09 dbt | ✓ | ✓ | ✓ | ✓ |

## Debugging / Incident Coverage

The set includes production investigation scenarios involving duplicate retries, stale CDC versions, missed incremental history, late events, reference corrections, lookup fan-out, Python/SQL hash mismatch, incorrect checkpoint state, concurrent partition processing, dbt incremental/full-refresh divergence, and logic-version backfill safety.

Use the incident sequence:

**SYMPTOM → HYPOTHESES → INVESTIGATION → ROOT CAUSE → FIX → PREVENTION**

## Production Correctness Checklist

- [ ] Data grain is explicit.
- [ ] Run contract is explicit and deterministic.
- [ ] Repeated execution is idempotent where required.
- [ ] Duplicate and version semantics are explicit.
- [ ] Incremental scope is dependency-aware.
- [ ] Late-data behavior includes an exceptional repair path.
- [ ] Hash serialization is canonical and cross-engine testable.
- [ ] Lookup cardinality and temporal semantics are validated.
- [ ] Configuration is validated and does not become arbitrary code.
- [ ] Checkpoint state corresponds to durable output.
- [ ] Concurrent writers are controlled.
- [ ] Backfills are bounded, validated and safely promoted.
- [ ] dbt incremental behavior can be reconciled against a full refresh.

## Final Mental Model

Module 2.12 interviews are fundamentally about making transformations **correct under change**: retries, duplicates, late data, changing reference data, logic changes, long backfills, concurrency and evolving datasets. Strong candidates establish the grain and run contract, choose explicit transformation and load semantics, make execution deterministic and idempotent, make state durable and repairable, and explain how correctness will be demonstrated.
