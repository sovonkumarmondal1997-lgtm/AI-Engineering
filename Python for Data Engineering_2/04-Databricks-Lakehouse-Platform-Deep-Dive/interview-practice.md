# Databricks Lakehouse Platform Deep Dive
# Interview Practice

## Purpose

This is the cumulative interview-preparation document for **Gap Module G4 — Databricks Lakehouse Platform Deep Dive**.

The interview set is designed to evaluate whether the learner can:

- explain Databricks platform concepts clearly;
- reason from workload and business requirements;
- choose Databricks capabilities and defend alternatives;
- troubleshoot production failures;
- reason about governance, security, reliability, performance, and cost;
- design CI/CD and environment boundaries;
- connect data engineering systems to MLflow and feature-engineering handoff.

The source curriculum is the G4 roadmap and its 14 topic files. The roadmap explicitly positions interview practice as a cumulative exercise covering platform features, Spark/Delta depth already learned earlier, architecture, ingestion choices, declarative pipelines, SCD Type 2, cost diagnosis, bundles/CI/CD, secure sharing, and ML handoff.

## Interview Answer Method

Use this sequence in every interview:

```text
Clarify requirements
        ↓
Classify workload / source / data product
        ↓
Choose the Databricks capability
        ↓
Explain alternatives and trade-offs
        ↓
Define governance + identity
        ↓
Choose execution model
        ↓
Explain reliability + recovery
        ↓
Define observability + validation
        ↓
Measure performance + cost
        ↓
State production risks and prevention
```

## Difficulty Progression

| Level | Questions | Interview Objective |
|---|---:|---|
| Basic | 01–10 | Explain platform fundamentals and why they exist |
| Moderate | 11–20 | Make practical engineering decisions |
| Hard | 21–30 | Diagnose production issues and defend trade-offs |
| Advanced | 31–40 | Lead architecture, reliability, security, FinOps, and ML-platform discussions |

## Important Scope Boundary

This document does not re-teach Spark internals, Delta Lake internals, Structured Streaming, Kafka, dbt, Airflow, or cloud IAM foundations that the G4 roadmap explicitly treats as prerequisites. Those concepts may appear only when they are necessary to reason about a G4 platform decision.

> **Current-product safety:** Databricks product names, APIs, compute modes, CLI behavior, serverless capabilities, AI/BI features, and model/feature APIs evolve. Before implementing a version-sensitive answer in a real workspace, verify the current Databricks documentation for the relevant cloud, runtime, region, and account configuration.

---

# Part I — Basic Interview Questions

## Question 01 — Explain Databricks Architecture Without Mixing Planes

**Difficulty:** Basic  
**Primary Topics:** 01 Architecture; 02 Compute  
**Question Type:** Conceptual / platform explanation

### Interview Question

A hiring manager asks you to draw Databricks architecture and explain where management, compute, and data actually live.

### What the Interviewer Evaluates

Can the candidate distinguish account, workspace, control plane, compute plane, and data storage without conflating them?

### Expected Approach

Start with a layered diagram: account → workspace → management/control functions → classic/serverless execution → governed storage. State what each layer owns before discussing configuration.

### Model Answer

The key distinction is that a Databricks workspace is a management and collaboration boundary, not the same thing as the runtime that executes every workload. The candidate should separate account-level organization, workspace objects and permissions, control-plane functions, classic compute, serverless compute, and governed storage. This prevents incorrect assumptions about where data lives, who owns compute, and what a workspace boundary actually provides.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 02 — Choose the Right Databricks Compute Model

**Difficulty:** Basic  
**Primary Topics:** 02 Compute  
**Question Type:** Conceptual / platform explanation

### Interview Question

A nightly production transformation currently runs on an always-on interactive cluster. The team wants lower cost and better isolation.

### What the Interviewer Evaluates

Can the candidate match execution mode to workload lifecycle, isolation, cost, and governance?

### Expected Approach

Classify the workload as interactive, scheduled, SQL/BI, or serverless-capable. Compare lifecycle, isolation, access mode, autoscaling, startup behavior, cost, and policy requirements.

### Model Answer

Use a workload-driven decision. Scheduled production transformations generally belong on jobs-oriented execution or an appropriate serverless job mode rather than a long-lived interactive cluster. Explain isolation, lifecycle, access mode, autoscaling, auto-termination, policy controls, observability, and cost. The strongest answer says that compute size is a consequence of workload measurements, not the first decision.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 03 — How Would You Organize a Databricks Codebase?

**Difficulty:** Basic  
**Primary Topics:** 03 Notebooks/Git  
**Question Type:** Conceptual / platform explanation

### Interview Question

A team has notebooks containing all business logic, no tests, and fragile notebook-to-notebook dependencies.

### What the Interviewer Evaluates

Can the candidate explain why production logic should be testable, reviewable, and independently deployable?

### Expected Approach

Identify reusable logic, move it into a package-oriented Git structure, add tests, separate configuration, and leave notebooks as thin entry/development surfaces.

### Model Answer

A strong design makes notebooks thin and reusable logic independently testable. Move business logic into version-controlled Python modules/packages, add unit tests, separate configuration and secrets, and deploy the package through the team's controlled release mechanism. Notebooks can remain useful for exploration, debugging, and entry points, but production correctness should not depend on interactive notebook state.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 04 — Design a Unity Catalog Governance Boundary

**Difficulty:** Basic  
**Primary Topics:** 04 Unity Catalog  
**Question Type:** Conceptual / platform explanation

### Interview Question

An enterprise needs development and production isolation plus domain ownership for sales and risk data.

### What the Interviewer Evaluates

Can the candidate design namespace, identity, ownership, and least-privilege boundaries?

### Expected Approach

Choose environment/domain boundaries first, then catalogs/schemas, group/service-principal identity, ownership, grants, and sensitive-data controls.

### Model Answer

Start with governance boundaries, not table names. Decide whether environment and domain boundaries belong at the catalog/schema level, define owners, use groups/service principals, apply least privilege, and then add row/column protections for sensitive data. A good answer also distinguishes authentication from authorization and explains how external locations/storage credentials fit into governed data access.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 05 — Explain Auto Loader's Incremental State

**Difficulty:** Basic  
**Primary Topics:** 05 Auto Loader  
**Question Type:** Conceptual / platform explanation

### Interview Question

A file stream restarts after a failure and the team wants to know how it resumes incrementally.

### What the Interviewer Evaluates

Can the candidate explain checkpoint/state semantics and safe recovery?

### Expected Approach

Separate source files from durable pipeline state. Explain how checkpoint state supports restart/recovery and why changing or deleting it can change replay behavior.

### Model Answer

Checkpoint state is durable operational state for incremental processing. It lets a restarted pipeline resume from known progress rather than treating every historical file as new. The candidate should mention that checkpoint identity and lifecycle affect replay/recovery semantics, so checkpoint deletion or relocation is an operational change, not harmless cleanup.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 06 — Choose Between Auto Loader and Lakeflow Connect

**Difficulty:** Basic  
**Primary Topics:** 06 Lakeflow Connect  
**Question Type:** Conceptual / platform explanation

### Interview Question

An organization receives cloud files, SaaS records, and database changes and asks for one universal ingestion technology.

### What the Interviewer Evaluates

Can the candidate reason from source semantics rather than choosing a platform feature by popularity?

### Expected Approach

Classify each source and compare managed options by semantics, supported capabilities, latency, governance, source limits, reconciliation, and operational burden.

### Model Answer

Do not force one technology onto all sources. Auto Loader is designed around incremental file discovery from cloud object storage; Lakeflow Connect addresses supported managed SaaS/database/query-based ingestion. The candidate should compare supported source types, latency, incremental semantics, schema handling, source/API constraints, governance, reconciliation, and operational burden before selecting a path.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 07 — Explain Lakeflow Declarative Pipelines

**Difficulty:** Basic  
**Primary Topics:** 07 Declarative Pipelines  
**Question Type:** Conceptual / platform explanation

### Interview Question

A team wants declarative transformations, data-quality controls, and incremental data products without writing every orchestration detail by hand.

### What the Interviewer Evaluates

Can the candidate distinguish declarative data-product semantics from orchestration concerns?

### Expected Approach

Define the target data product first. Then choose declarative objects, expectations, stateful behavior, and only afterward define orchestration and recovery.

### Model Answer

Declarative pipelines are about defining the intended data products and quality behavior while the platform manages supported execution details. The candidate should explain the difference between transformation semantics and orchestration, how expectations express quality policy, and when custom processing may still be appropriate. The answer should stay within the module's managed lakehouse scope.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 08 — Design a Recoverable Lakeflow Job

**Difficulty:** Basic  
**Primary Topics:** 08 Lakeflow Jobs  
**Question Type:** Conceptual / platform explanation

### Interview Question

A multi-task production workflow has one failed task while upstream work succeeded.

### What the Interviewer Evaluates

Can the candidate reason about dependency graphs, targeted repair, idempotency, and validation?

### Expected Approach

Inspect run/task history and the dependency graph. Isolate the failed task, repair only what is necessary, validate outputs, and check idempotency.

### Model Answer

For a failed task, inspect the run graph and task output first. If upstream tasks are valid and the failed task is repairable, fix the cause and use a targeted repair/retry rather than automatically reprocessing everything. Then validate data outputs and downstream state. Mention idempotency, backfills, notifications, and concurrency where relevant.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 09 — Explain Photon to a Hiring Panel

**Difficulty:** Basic  
**Primary Topics:** 09 Photon/Performance  
**Question Type:** Conceptual / platform explanation

### Interview Question

A SQL-heavy workload is slow and leadership asks whether Photon alone is the answer.

### What the Interviewer Evaluates

Can the candidate treat Photon as one performance layer and use evidence-based benchmarking?

### Expected Approach

Baseline representative queries, inspect query profiles, scan/shuffle/skew/layout/concurrency, test Photon suitability, then benchmark runtime and cost.

### Model Answer

Photon is a native execution layer intended to accelerate supported data-processing workloads, especially SQL-heavy operations. It is not a magic switch. Diagnose query plans/profiles, data scans, joins, shuffle, skew, layout, concurrency, and unsupported operations. Establish a baseline and compare runtime and cost after enabling or tuning Photon.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 10 — Explain MLflow's Role in a Production Data Platform

**Difficulty:** Basic  
**Primary Topics:** 14 MLflow/Feature Handoff  
**Question Type:** Conceptual / platform explanation

### Interview Question

An ML team wants reproducible experiments and governed model handoff rather than unmanaged model files.

### What the Interviewer Evaluates

Can the candidate connect experiment tracking, model governance, data reproducibility, and downstream inference?

### Expected Approach

Define experiment/run evidence, model governance, approval criteria, version/alias strategy, deployment identity, feature/data lineage, and batch-inference behavior.

### Model Answer

MLflow provides an experiment record around a training run: parameters, metrics, artifacts, and model information, with dataset/version context where available. Production handoff adds governed model registration, approval/version/alias semantics, identity, reproducibility, lineage, and downstream inference. The model file alone cannot explain why or how it was produced.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


---

# Part II — Moderate Interview Questions

## Question 11 — Design a Governed File-Ingestion Pipeline

**Difficulty:** Moderate  
**Primary Topics:** 04 Unity Catalog; 05 Auto Loader; 07 Pipelines  
**Question Type:** Practical engineering / troubleshooting

### Interview Question

A governed pipeline must ingest evolving JSON, preserve bad records, and publish trusted silver data.

### What the Interviewer Evaluates

Can the candidate integrate ingestion state, schema evolution, quality, governance, and observability?

### Expected Approach

Define source and target governance, Auto Loader state/schema strategy, malformed-record handling, expectations, and downstream contract validation.

### Model Answer

Use governed source access plus Auto Loader's incremental state and schema-management capabilities, then apply declarative quality controls. For malformed records, preserve evidence through the configured rescued/corrupt-data path rather than silently discarding data. Treat schema evolution as a contract decision and validate the published silver schema and quality metrics.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 12 — Diagnose a CDC Reconciliation Mismatch

**Difficulty:** Moderate  
**Primary Topics:** 06 Lakeflow Connect; 04 Governance  
**Question Type:** Practical engineering / troubleshooting

### Interview Question

A CDC destination is missing rows relative to the source while deletes and updates continue.

### What the Interviewer Evaluates

Can the candidate reconcile source/target state using time windows, keys, and CDC semantics?

### Expected Approach

Set a reconciliation timestamp, compare stable keys and operation classes, inspect connector state/cursors, and distinguish source latency from actual data loss.

### Model Answer

Reconciliation must use a defined observation window and stable keys. Compare inserts, updates, and deletes separately, inspect connector progress/cursor state, and distinguish expected source-to-target latency from true missing data. The candidate should avoid treating a raw row-count difference as proof of connector failure.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 13 — Design Data-Quality Expectations

**Difficulty:** Moderate  
**Primary Topics:** 07 Pipelines  
**Question Type:** Practical engineering / troubleshooting

### Interview Question

A critical financial pipeline needs different responses for advisory and release-blocking data-quality violations.

### What the Interviewer Evaluates

Can the candidate choose quality actions according to business risk?

### Expected Approach

Classify each rule by business consequence. Use record/warn, drop/quarantine, or fail according to the release risk and define metrics and ownership.

### Model Answer

Quality actions should map to business risk. Advisory rules can record violations; unusable records may be dropped or quarantined; critical financial invariants can fail publication. A strong candidate explains how violation counts are observed, who owns remediation, and how thresholds are reviewed rather than applying one severity to every rule.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 14 — Design Parameterized Lakeflow Jobs

**Difficulty:** Moderate  
**Primary Topics:** 08 Jobs  
**Question Type:** Practical engineering / troubleshooting

### Interview Question

A single production job must support different business dates, environments, and controlled backfills.

### What the Interviewer Evaluates

Can the candidate make jobs reproducible and safe for backfills?

### Expected Approach

Parameterize stable run inputs, pass derived task values explicitly, record parameters, and test both normal runs and backfills.

### Model Answer

Use job-level parameters for stable run inputs such as business date and environment, then pass derived values through supported task-value mechanisms. Avoid hidden global state and hard-coded dates. This makes normal runs, reruns, and backfills explicit and auditable.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 15 — Diagnose a Slow Databricks SQL Workload

**Difficulty:** Moderate  
**Primary Topics:** 09 Performance; 10 SQL/AI-BI  
**Question Type:** Practical engineering / troubleshooting

### Interview Question

A BI workload becomes slower as data and concurrency grow, even though SQL text is unchanged.

### What the Interviewer Evaluates

Can the candidate diagnose physical workload behavior before increasing compute?

### Expected Approach

Capture representative slow queries and compare profiles. Diagnose scans, joins, skew, layout, concurrency, repeated work, and warehouse behavior before scaling.

### Model Answer

Start with query history and a representative query profile. Inspect scan volume, joins, shuffle/skew, data layout, repeated dashboard work, and concurrency before scaling the warehouse. If compute tuning is appropriate, benchmark it with realistic concurrency and compare tail latency and cost, not only one query's median runtime.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 16 — Prevent Metric Drift in AI/BI

**Difficulty:** Moderate  
**Primary Topics:** 10 SQL/AI-BI; 04 Governance  
**Question Type:** Practical engineering / troubleshooting

### Interview Question

Finance users report that an AI/BI dashboard's revenue metric differs from the official finance number.

### What the Interviewer Evaluates

Can the candidate preserve a governed semantic definition rather than patching a dashboard?

### Expected Approach

Find the authoritative metric definition, govern its source, make AI/BI consume it, and reconcile output with a repeatable validation query.

### Model Answer

Create an authoritative governed metric and dataset, then make the dashboard consume that source. Apply Unity Catalog permissions and sensitive-data controls as required. Validate the dashboard metric against a repeatable reconciliation query and treat metric definition as a governed data-product concern rather than a visualization concern.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 17 — Design Secure Delta Sharing

**Difficulty:** Moderate  
**Primary Topics:** 11 Delta Sharing; 04 Governance  
**Question Type:** Practical engineering / troubleshooting

### Interview Question

A partner needs regional aggregates but must not receive customer PII or raw transactions.

### What the Interviewer Evaluates

Can the candidate minimize data exposure and design auditable sharing?

### Expected Approach

Define the minimum partner data product, govern the share and recipient, test positive/negative access, and establish audit/revocation procedures.

### Model Answer

Create a purpose-built, minimized shareable dataset at the required grain. Exclude PII and raw transactions that are not necessary, govern the source with Unity Catalog, define the recipient, test allowed and denied access, and establish audit/revocation procedures. The strongest answer treats sharing as a data-product contract and security boundary.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 18 — Design Dev/Staging/Prod with Asset Bundles

**Difficulty:** Moderate  
**Primary Topics:** 12 Asset Bundles; 04 Governance; 08 Jobs  
**Question Type:** Practical engineering / troubleshooting

### Interview Question

A single codebase must deploy the same Jobs resources to development, staging, and production with different resources and identities.

### What the Interviewer Evaluates

Can the candidate separate common application code from environment-specific deployment configuration?

### Expected Approach

Keep one bundle project, use target overrides for environment differences, deploy with controlled identities, and validate each target before promotion.

### Model Answer

Use one source-controlled bundle project with target-specific overrides for catalogs, compute, schedules, permissions, and other environment configuration. Production should use a controlled identity rather than a developer credential. Validate and test each target before deployment, and keep application logic independent of environment-specific names.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 19 — Explain Databricks Cost Attribution

**Difficulty:** Moderate  
**Primary Topics:** 13 Cost; 02 Compute  
**Question Type:** Practical engineering / troubleshooting

### Interview Question

Databricks spend rises sharply and the team blames serverless without evidence.

### What the Interviewer Evaluates

Can the candidate attribute cost to workloads and avoid misleading billing joins?

### Expected Approach

Start from billing usage and pricing, then attribute by workspace/workload/tags/SKU and correlate with operational activity before accepting any cost hypothesis.

### Model Answer

Do not accept the hypothesis that serverless is responsible until usage is attributed. Start from billing usage and pricing, segment by workload/SKU/tags, correlate with Jobs/query/pipeline activity, and normalize for workload volume. Then quantify the top driver and test an optimization. Reconcile the analysis back to total spend.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 20 — Explain Point-in-Time Correct Feature Data

**Difficulty:** Moderate  
**Primary Topics:** 14 MLflow/Feature Handoff  
**Question Type:** Practical engineering / troubleshooting

### Interview Question

A churn model is trained with historical labels but the feature join uses current values.

### What the Interviewer Evaluates

Can the candidate explain temporal information boundaries and leakage prevention?

### Expected Approach

Define label time and feature availability time, use point-in-time semantics, trace lineage, record source/version context, and add leakage tests.

### Model Answer

Current feature values can contain information that did not exist at the historical label time, creating leakage. Define label and feature timestamps, perform point-in-time lookups, validate that feature availability is not after label time, and preserve the training-data version/context so the result can be reproduced.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


---

# Part III — Hard Interview Questions

## Question 21 — Refactor Notebook-Centric Production Code

**Difficulty:** Hard  
**Primary Topics:** 03 Code; 08 Jobs; 12 CI/CD  
**Question Type:** Production debugging / trade-off / architecture

### Interview Question

A production job fails because a renamed notebook helper was imported by downstream tasks.

### What the Interviewer Evaluates

Can the candidate move from notebook convenience to production packaging and CI/CD?

### Expected Approach

Stabilize the release, extract logic into a tested package, package it, deploy through the bundle, and add CI tests to eliminate notebook-state coupling.

### Model Answer

Stabilize the release first. Then remove notebook-to-notebook production dependencies by moving shared logic into tested Python packages, packaging it, and deploying through controlled CI/CD. Add unit and integration tests so a renamed helper is caught before production.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 22 — Handle Schema Evolution and Bad Files

**Difficulty:** Hard  
**Primary Topics:** 05 Auto Loader; 07 Pipelines  
**Question Type:** Production debugging / trade-off / architecture

### Interview Question

New columns appear in incoming files while malformed records also increase.

### What the Interviewer Evaluates

Can the candidate distinguish schema evolution from malformed input and preserve evidence?

### Expected Approach

Treat schema evolution and malformed input separately. Verify the schema strategy, preserve bad-record evidence, measure impact, and validate downstream contracts.

### Model Answer

Schema evolution and malformed data are different failure modes. Confirm the configured schema-evolution behavior, preserve malformed records, quantify impact, update downstream contracts if necessary, and validate the resulting data quality. Do not solve both problems by restarting the stream or silently dropping records.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 23 — Diagnose Lakeflow Connect Freshness

**Difficulty:** Hard  
**Primary Topics:** 06 Connect; 13 Cost  
**Question Type:** Production debugging / trade-off / architecture

### Interview Question

A managed SaaS connector meets neither freshness nor API-usage expectations.

### What the Interviewer Evaluates

Can the candidate investigate connector cursors, source limits, freshness, and cost together?

### Expected Approach

Measure freshness and API consumption, inspect cursor behavior and source limits, identify expensive entities/tables, and reconcile destination completeness.

### Model Answer

Inspect connector freshness, cursor advancement, source API limits, selected entities/tables, scheduling, and destination reconciliation. Managed ingestion removes plumbing but does not remove source constraints. The strongest answer quantifies both freshness and source/API consumption before changing architecture.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 24 — Design SCD Type 2 with Lakeflow

**Difficulty:** Hard  
**Primary Topics:** 07 Pipelines; 08 Jobs  
**Question Type:** Production debugging / trade-off / architecture

### Interview Question

A customer-status pipeline must preserve historical states and handle late changes.

### What the Interviewer Evaluates

Can the candidate separate temporal transformation logic from scheduling/recovery?

### Expected Approach

Define business key, effective/end timestamps, deterministic sequencing, late-arrival policy, and backfill behavior; use Jobs for operational scheduling.

### Model Answer

Define the business key and temporal semantics explicitly. Maintain effective/end timestamps and current-state indicators appropriate to the data product, sequence multiple changes deterministically, and define a late-arrival/backfill strategy. Use Jobs to schedule and recover the pipeline rather than embedding operational orchestration inside transformation logic.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 25 — Investigate a Query Performance Regression

**Difficulty:** Hard  
**Primary Topics:** 09 Performance; 10 SQL  
**Question Type:** Production debugging / trade-off / architecture

### Interview Question

A dashboard query regresses after the data volume doubles; Photon is already enabled.

### What the Interviewer Evaluates

Can the candidate build a controlled performance investigation and benchmark changes?

### Expected Approach

Compare controlled runs, inspect query profiles and physical changes, then benchmark one targeted optimization at a time with both performance and cost metrics.

### Model Answer

Compare controlled pre/post runs and inspect physical execution behavior. Determine whether growth changed scan volume, skew, shuffle, join strategy, or layout. Benchmark one targeted change at a time, including Photon suitability, data layout, query rewrite, or compute configuration, and compare both latency and cost.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 26 — Debug a Production Bundle Deployment

**Difficulty:** Hard  
**Primary Topics:** 12 CI/CD; 04 Governance  
**Question Type:** Production debugging / trade-off / architecture

### Interview Question

Bundle validation passes outside production but production deployment uses the wrong catalog and identity permissions.

### What the Interviewer Evaluates

Can the candidate diagnose rendered target configuration and production identity differences?

### Expected Approach

Inspect the resolved production target, catalog references, identity, grants, and deployment permissions; validate again before production smoke testing.

### Model Answer

Inspect the rendered production target configuration and the identity executing deployment. Verify catalog/schema references, permissions, service-principal grants, and target overrides. Revalidate the bundle, deploy, and run a controlled smoke test. Production-only failures are often configuration/identity differences rather than application-code bugs.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 27 — Investigate a Databricks Cost Spike

**Difficulty:** Hard  
**Primary Topics:** 13 Cost; 02 Compute; 09 Performance  
**Question Type:** Production debugging / trade-off / architecture

### Interview Question

Monthly Databricks cost increases by 40%; platform leadership wants a causal explanation.

### What the Interviewer Evaluates

Can the candidate build a causal cost investigation rather than accept a hypothesis?

### Expected Approach

Break cost into SKU/workload dimensions, correlate with jobs/queries/pipelines, normalize for workload volume, and quantify the top causal drivers.

### Model Answer

Use billing usage and pricing as the financial source, then attribute to workloads through tags and operational identifiers. Correlate the spike with compute configuration, query volume, pipeline frequency, or workload growth. Avoid double-counting system-table grains and normalize for business volume before declaring a cause.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 28 — Design MLflow-to-Batch-Inference Handoff

**Difficulty:** Hard  
**Primary Topics:** 14 MLflow; 08 Jobs; 04 Governance  
**Question Type:** Production debugging / trade-off / architecture

### Interview Question

Daily model training produces an approved model that must be governed and consumed by batch inference.

### What the Interviewer Evaluates

Can the candidate design a governed, reproducible ML lifecycle?

### Expected Approach

Track training runs in MLflow, govern the model in Unity Catalog, define promotion rules, deploy with controlled identity, and have Jobs consume the approved model reference.

### Model Answer

Track training runs in MLflow, register/govern models through Unity Catalog, define promotion criteria, and use controlled version/alias semantics appropriate to the current platform workflow. Lakeflow Jobs can orchestrate batch inference against the approved model reference. Validate prediction outputs, lineage, and reproducibility.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 29 — Investigate Feature Freshness SLA Failure

**Difficulty:** Hard  
**Primary Topics:** 14 Feature Handoff; 08 Jobs  
**Question Type:** Production debugging / trade-off / architecture

### Interview Question

A feature freshness SLA is 15 minutes, but predictions use 90-minute-old features while Jobs report success.

### What the Interviewer Evaluates

Can the candidate treat freshness as an end-to-end data-product SLA?

### Expected Approach

Trace freshness end-to-end from source arrival through feature publication to inference. Alert on the feature SLA, not merely on job status.

### Model Answer

Pipeline success does not equal feature freshness. Trace source arrival, job scheduling/queueing, task duration, retries, feature-table update time, and inference start time. Define an explicit freshness metric and alert tied to the feature contract so a green job cannot hide a stale data product.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 30 — Design a Data-to-ML Handoff Contract

**Difficulty:** Hard  
**Primary Topics:** 14 Feature Handoff; 04 Governance; 12 CI/CD  
**Question Type:** Production debugging / trade-off / architecture

### Interview Question

Development and production feature consumers disagree about schema and timestamp semantics.

### What the Interviewer Evaluates

Can the candidate make an ML handoff explicit, versioned, testable, and environment-safe?

### Expected Approach

Write a feature contract covering schema, keys, timestamp semantics, freshness, ownership, and compatibility. Enforce it in CI and staging.

### Model Answer

Define a formal contract containing entity key, feature schema, types, timestamp semantics, freshness SLA, ownership, compatibility rules, and environment boundaries. Test schema and temporal semantics in CI/staging, use target configuration for environment paths, and block promotion when contract tests fail.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


---

# Part IV — Advanced / Senior-Staff Interview Questions

## Question 31 — Design an Enterprise Databricks Platform

**Difficulty:** Advanced  
**Primary Topics:** 01 Architecture; 02 Compute; 04 Governance; 08 Jobs; 13 Cost  
**Question Type:** Senior/Staff architecture / production system design

### Interview Question

An enterprise has many workspaces, business units, data products, and pipelines and wants governance without blocking autonomy.

### What the Interviewer Evaluates

Can the candidate balance central governance with domain autonomy and meaningful isolation?

### Expected Approach

Design workspace boundaries only where required, centralize governance, standardize compute guardrails, enable domain ownership, and establish cost/audit observability.

### Model Answer

Choose workspace boundaries from real isolation requirements such as security, regulatory, organizational, or operational constraints. Centralize governance with Unity Catalog, standardize identity and compute guardrails, allow domain teams to own governed data products, and use system-table/cost metadata for accountability. The goal is governed autonomy, not maximum isolation.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 32 — Design Multi-Source Lakehouse Ingestion

**Difficulty:** Advanced  
**Primary Topics:** 05 Auto Loader; 06 Connect; 07 Pipelines; 08 Jobs  
**Question Type:** Senior/Staff architecture / production system design

### Interview Question

An enterprise must combine files, SaaS, and database CDC into governed medallion data products.

### What the Interviewer Evaluates

Can the candidate preserve source-specific ingestion semantics while standardizing operations?

### Expected Approach

Use Auto Loader for cloud files and supported Lakeflow Connect capabilities for SaaS/database sources, then standardize governed bronze, quality, orchestration, reconciliation, and SLAs.

### Model Answer

Use source-specific ingestion: Auto Loader for cloud files and supported Lakeflow Connect connectors for SaaS/database sources. Land governed bronze data, apply declarative transformations and quality rules, use Jobs for scheduling/recovery, and define freshness/reconciliation per source. Standardize operations without pretending the sources have identical semantics.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 33 — Optimize Performance and Cost Together

**Difficulty:** Advanced  
**Primary Topics:** 02 Compute; 09 Performance; 10 SQL; 13 Cost  
**Question Type:** Senior/Staff architecture / production system design

### Interview Question

A BI workload has acceptable median latency but poor tail latency and rising cost per dashboard.

### What the Interviewer Evaluates

Can the candidate optimize latency and cost as a combined workload objective?

### Expected Approach

Optimize query/layout first, then compute/concurrency. Measure tail latency, workload throughput, and cost per dashboard together.

### Model Answer

Treat performance and cost as one optimization problem. Measure query volume, concurrency, tail latency, scan volume, warehouse utilization, and cost per dashboard. Fix query/layout issues first, then tune compute/concurrency, and validate the unit economics after every material change.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 34 — Respond to a Delta Sharing Exposure

**Difficulty:** Advanced  
**Primary Topics:** 11 Sharing; 04 Governance  
**Question Type:** Senior/Staff architecture / production system design

### Interview Question

A partner reports receiving data outside the approved Delta Sharing contract.

### What the Interviewer Evaluates

Can the candidate handle sharing incidents as data-security events with evidence and containment?

### Expected Approach

Contain the share, establish recipient and exposure window, inspect share and governed asset, review audit evidence, revoke/narrow if necessary, and validate corrected access.

### Model Answer

Contain the share, identify recipient and exposure window, inspect the share and governed asset, compare actual delivered data with the approved contract, and use audit evidence to establish scope. Revoke or narrow access when required, publish a corrected minimal data product, and test both positive and negative access before restoring delivery.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 35 — Design Code and Data Rollback

**Difficulty:** Advanced  
**Primary Topics:** 12 CI/CD; 07 Pipelines; 04 Governance  
**Question Type:** Senior/Staff architecture / production system design

### Interview Question

A deployment introduced incorrect data and the team is unsure whether to roll back code, configuration, or data.

### What the Interviewer Evaluates

Can the candidate separate application rollback from data recovery?

### Expected Approach

Contain publication, classify code/config/data impact, roll back deployment through CI/CD, recover data with the appropriate versioned mechanism, and reconcile.

### Model Answer

Separate code/configuration rollback from data recovery. First contain incorrect publication, identify the release and affected data interval, roll back application state through CI/CD, recover data through the appropriate versioned mechanism where safe, then reconcile downstream outputs before resuming.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 36 — Investigate ML Training Leakage

**Difficulty:** Advanced  
**Primary Topics:** 14 MLflow; 05/07 Data Engineering; 08 Jobs  
**Question Type:** Senior/Staff architecture / production system design

### Interview Question

Offline ML performance is excellent but production performance is poor because historical feature values were computed after labels.

### What the Interviewer Evaluates

Can the candidate reconstruct historical information availability and prove leakage remediation?

### Expected Approach

Reconstruct feature availability relative to labels, quantify leakage, rebuild point-in-time data, record reproducible evidence, retrain, and automate leakage checks.

### Model Answer

Reconstruct the historical training set using feature and label timestamps. Identify values that were created after the label, trace their lineage, quantify the affected examples, rebuild with point-in-time semantics, record reproducible data/version context in MLflow, retrain, and add automated leakage tests.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 37 — Design Multi-Environment Feature Engineering

**Difficulty:** Advanced  
**Primary Topics:** 14 Features; 04 Governance; 12 CI/CD  
**Question Type:** Senior/Staff architecture / production system design

### Interview Question

Multiple ML environments need identical feature logic but isolated data and access.

### What the Interviewer Evaluates

Can the candidate maintain code consistency while isolating environment data and access?

### Expected Approach

Keep feature logic in version-controlled code, use environment-specific governed locations, declarative pipelines and Jobs for operations, and bundles for deployment.

### Model Answer

Keep feature logic in version-controlled code, deploy it through environment-specific bundle targets, and isolate feature data and access by environment. Declarative pipelines compute the data product, Jobs handles scheduling/freshness, Unity Catalog governs it, and CI enforces feature-contract compatibility.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 38 — Design ML Unit Economics

**Difficulty:** Advanced  
**Primary Topics:** 13 Cost; 14 MLflow  
**Question Type:** Senior/Staff architecture / production system design

### Interview Question

Finance wants cost per 1,000 predictions and a breakdown between feature computation, training, and inference.

### What the Interviewer Evaluates

Can the candidate define useful ML unit economics and allocate shared platform costs?

### Expected Approach

Define cost boundaries, stable workload attribution, prediction denominators, and separate feature/training/inference costs before calculating unit economics.

### Model Answer

Define the ML product's cost boundary and allocate feature computation, training, and inference separately. Join billing to workload metadata at compatible grains, collect prediction counts and feature-refresh counts, and report cost per refresh, training run, and 1,000 predictions. Reconcile allocated totals to platform spend.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 39 — Design an End-to-End Data + ML Platform

**Difficulty:** Advanced  
**Primary Topics:** 01–14 integrated  
**Question Type:** Senior/Staff architecture / production system design

### Interview Question

An enterprise needs governed ingestion, transformations, orchestration, analytics, sharing, CI/CD, FinOps, and ML handoff.

### What the Interviewer Evaluates

Can the candidate integrate all G4 layers into coherent contracts and operating controls?

### Expected Approach

Connect ingestion, governance, pipelines, Jobs, analytics, sharing, CI/CD, FinOps, MLflow, and feature contracts as explicit interfaces with observable SLAs.

### Model Answer

The end-to-end design should connect source-specific ingestion, governed bronze/silver/gold data products, declarative transformations, Jobs orchestration, SQL/AI-BI consumption, minimized sharing, Asset Bundle CI/CD, cost/audit observability, and MLflow/feature contracts. Each boundary should have an owner, SLA, recovery path, and validation signal.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?


## Question 40 — Lead a Full Databricks Production Architecture Interview

**Difficulty:** Advanced  
**Primary Topics:** 01–14 integrated  
**Question Type:** Senior/Staff architecture / production system design

### Interview Question

During one incident, feature freshness degrades, dashboards slow down, and platform cost rises. You must lead the architecture and incident discussion.

### What the Interviewer Evaluates

Can the candidate lead a multi-symptom incident using evidence, ownership, and cross-system reasoning?

### Expected Approach

Separate symptoms into feature freshness, query performance, and cost attribution. Lead with evidence, owners, containment, root cause, remediation, validation, and prevention.

### Model Answer

Lead the discussion by separating the three symptoms: feature freshness is an ML data-product SLA issue, dashboard latency is a workload-performance issue, and rising cost is a FinOps attribution issue. Establish evidence and owners for each, contain business impact, diagnose root causes, apply targeted remediation, validate recovery, and document prevention. A senior answer connects the systems without assuming one symptom explains all three.

### How to Solve the Problem

1. **Clarify the requirement.** Identify workload, data volume, latency/freshness, governance, reliability, security, and cost constraints.
2. **Map the problem to the G4 capability.** Use the topic boundary rather than introducing unrelated platform features.
3. **State the design or diagnosis before naming configuration details.** Explain the principle first, then the Databricks capability.
4. **Compare the nearest alternative.** Explain why it is less suitable under the stated constraints.
5. **Define validation evidence.** Say what you would measure, inspect, reconcile, or test.
6. **Close with operations.** Cover ownership, observability, recovery, cost, and prevention.

### Example

```text
Requirement
   ↓
Workload / source classification
   ↓
Databricks capability selection
   ↓
Unity Catalog governance
   ↓
Compute / execution model
   ↓
Validation + observability
   ↓
Cost + reliability + recovery
```

### Why This Is a Strong Answer

A strong candidate does not merely name a Databricks feature. The candidate connects the feature to requirements, explains trade-offs, identifies operational failure modes, and states how the design will be validated in production.

### Common Weak Answers

- Naming a feature without explaining why it fits the workload.
- Saying “use serverless” or “use Photon” without measuring the workload.
- Ignoring Unity Catalog governance and identity.
- Ignoring failure recovery and data reconciliation.
- Treating successful execution as proof of correct data.
- Optimizing cost or performance without defining the relevant denominator.
- Introducing unrelated technologies simply to sound senior.

### Strong Interview Answer

> “I would first clarify the workload and correctness requirements, then choose the Databricks capability that matches those semantics. I would govern the data and identity through Unity Catalog, choose the cheapest adequate execution model, make the workflow observable and recoverable, and validate the result with measurable evidence. I would also explain the closest alternative and why I rejected it.”

### Production Considerations

- Use least-privilege identity and group/service-principal patterns.
- Separate development, staging, and production concerns.
- Prefer version-controlled code and controlled deployment.
- Make pipelines and jobs safe to retry where practical.
- Monitor freshness, quality, failures, performance, and cost.
- Reconcile important data products rather than relying only on task success.
- Treat version-sensitive Databricks capabilities and syntax as documentation-dependent.

### Follow-Up Questions

1. What changes if the workload is 10× larger?
2. What changes if the data contains PII?
3. How would you test the design before production?
4. What metric would tell you the system is healthy?
5. What would you do if cost increased without a corresponding increase in business volume?

# Topic Coverage Matrix

| Topic | Coverage |
|---|---|
| 01 — Databricks architecture, workspaces, and planes | Q01, Q31, Q39, Q40 |
| 02 — Compute, serverless, and SQL warehouses | Q02, Q09, Q15, Q27, Q31, Q33, Q38, Q40 |
| 03 — Notebooks, Git folders, and project structure | Q03, Q21, Q40 |
| 04 — Unity Catalog, volumes, locations, permissions | Q04, Q11, Q12, Q16, Q17, Q18, Q26, Q28, Q30, Q31, Q34, Q36, Q37, Q39, Q40 |
| 05 — Auto Loader and incremental file ingestion | Q05, Q11, Q22, Q32, Q39, Q40 |
| 06 — Lakeflow Connect managed ingestion | Q06, Q12, Q23, Q32, Q39, Q40 |
| 07 — Lakeflow Declarative Pipelines and expectations | Q07, Q11, Q13, Q22, Q24, Q32, Q35, Q39, Q40 |
| 08 — Lakeflow Jobs orchestration | Q08, Q14, Q21, Q24, Q28, Q29, Q32, Q35, Q37, Q39, Q40 |
| 09 — Photon, performance, predictive optimization | Q09, Q15, Q25, Q27, Q33, Q40 |
| 10 — Databricks SQL, AI/BI, Genie | Q15, Q16, Q25, Q33, Q40 |
| 11 — Delta Sharing and Marketplace | Q17, Q34, Q40 |
| 12 — Asset Bundles and CI/CD | Q18, Q21, Q26, Q28, Q30, Q35, Q37, Q40 |
| 13 — Cost management and system tables | Q19, Q23, Q27, Q33, Q38, Q40 |
| 14 — MLflow and feature-engineering handoff | Q10, Q20, Q28, Q29, Q30, Q36, Q37, Q38, Q39, Q40 |

# Competency Coverage Matrix

| Competency | Demonstrated By |
|---|---|
| Platform architecture | Q01, Q31, Q32, Q39, Q40 |
| Compute selection | Q02, Q09, Q15, Q27, Q33, Q38 |
| Production code organization | Q03, Q21 |
| Governance and security | Q04, Q11, Q16, Q17, Q26, Q30, Q34, Q36, Q37, Q40 |
| Incremental ingestion | Q05, Q06, Q11, Q12, Q22, Q23, Q32, Q39 |
| Data quality | Q07, Q11, Q13, Q22, Q24, Q32, Q40 |
| Orchestration and recovery | Q08, Q14, Q21, Q24, Q28, Q29, Q32, Q35, Q39, Q40 |
| Performance engineering | Q09, Q15, Q25, Q27, Q33, Q40 |
| Analytics and semantic consistency | Q15, Q16, Q33, Q40 |
| External sharing | Q17, Q34 |
| CI/CD | Q18, Q21, Q26, Q28, Q30, Q35, Q37, Q40 |
| FinOps | Q19, Q23, Q27, Q33, Q38, Q40 |
| MLflow | Q10, Q28, Q36, Q38, Q39, Q40 |
| Feature engineering | Q20, Q29, Q30, Q36, Q37, Q38, Q39, Q40 |
| Point-in-time correctness | Q20, Q36, Q39, Q40 |
| Production troubleshooting | Q08, Q12, Q15, Q21, Q22, Q23, Q25, Q26, Q27, Q29, Q34, Q35, Q36, Q40 |
| Architecture trade-offs | Q06, Q18, Q31, Q32, Q33, Q35, Q37, Q39, Q40 |

# Interview Scenario Coverage

| Requirement | Minimum | Covered |
|---|---:|---:|
| Troubleshooting scenarios | 10+ | 20+ |
| Trade-off questions | 8+ | 15+ |
| Architecture scenarios | 8+ | 15+ |
| Production scenarios | 10+ | 30+ |
| Total interview questions | 40 | 40 |

# 30-Minute Databricks Interview Practice Routine

## First 5 Minutes — Clarify

Ask:

- What is the business outcome?
- What is the source and target?
- What is the expected volume?
- What latency/freshness is required?
- What governance or PII constraints exist?
- What reliability/SLA is required?
- What cost constraint matters?

## Next 10 Minutes — Design

Explain:

1. source and ingestion;
2. Unity Catalog governance;
3. compute;
4. pipeline/data-product semantics;
5. Jobs/orchestration;
6. consumers;
7. observability;
8. cost controls.

## Next 10 Minutes — Defend

Discuss:

- closest alternative;
- why you rejected it;
- failure modes;
- retry/idempotency;
- security;
- performance;
- cost;
- environment separation;
- CI/CD;
- operational ownership.

## Final 5 Minutes — Validate

State:

- what you would measure;
- how you would test;
- what would page the operator;
- how you would reconcile data;
- how you would roll back or repair;
- what evidence would prove the system is healthy.

# Strong Candidate Answer Pattern

A strong Databricks interview answer usually follows:

```text
1. Clarify requirements
2. State the architecture
3. Select the platform capability
4. Explain why it fits
5. Reject the nearest alternative
6. Explain governance/security
7. Explain execution/compute
8. Explain reliability/recovery
9. Explain observability
10. Explain cost/performance
11. Explain validation
12. State production risks
```

Avoid beginning with a long list of Databricks features. Begin with the problem.

# Senior/Staff-Level Evaluation Rubric

| Dimension | Weak | Strong | Senior/Staff |
|---|---|---|---|
| Requirements | Jumps to product | Clarifies workload | Converts business constraints into engineering objectives |
| Architecture | Lists services | Connects components | Defines boundaries, contracts, ownership, and failure domains |
| Governance | Mentions permissions | Uses Unity Catalog | Designs identity, ownership, least privilege, data minimization, and audit |
| Reliability | Says “retry” | Discusses repair | Designs idempotency, reconciliation, backfill, recovery, and prevention |
| Performance | Says “use Photon” | Profiles workload | Establishes benchmarks, physical bottlenecks, tail latency, and cost |
| Cost | Says “use serverless” | Mentions DBUs | Defines attribution, unit economics, guardrails, and optimization experiments |
| CI/CD | Mentions Git | Uses bundles | Designs promotion, identity, tests, rollback, and drift control |
| ML handoff | Mentions MLflow | Tracks runs/models | Defines feature/data contracts, temporal correctness, lineage, and reproducibility |
| Communication | Gives a tool list | Explains reasoning | Defends trade-offs and adapts design under changing constraints |

# Common Interview Misconceptions

1. **A workspace is a compute cluster.**  
   It is not. Workspace, execution, and storage are separate architectural concerns.

2. **Serverless automatically means cheap.**  
   Cost depends on workload behavior, configuration, usage, and pricing.

3. **Photon fixes slow queries.**  
   Photon is one execution layer; data layout, joins, skew, scans, concurrency, and query shape still matter.

4. **A green job means the data is correct.**  
   Freshness, quality, reconciliation, and downstream contracts can still fail.

5. **Lakeflow Connect removes all ingestion responsibility.**  
   Managed ingestion reduces plumbing, not source constraints, reconciliation, or operational ownership.

6. **Unity Catalog is only a permissions system.**  
   Governance also includes ownership, data locations, lineage, auditing, sharing, and policy design.

7. **Current feature values are valid for historical training.**  
   They can create leakage when they were unavailable at the historical label time.

8. **Rolling back code automatically rolls back data.**  
   Application state and published data state are separate recovery dimensions.

9. **Cost is a monthly number.**  
   Production FinOps needs workload attribution and useful unit denominators.

10. **Notebooks are the production application.**  
    Production logic should be testable, version-controlled, packageable, and deployable independently of interactive notebook state.

# Interview Readiness Checklist

## Basic
- [ ] I can explain all 14 G4 topics in plain technical language.
- [ ] I can explain why each major Databricks capability exists.
- [ ] I can distinguish platform management, compute, storage, governance, and orchestration.

## Intermediate
- [ ] I can select the right ingestion and execution model.
- [ ] I can design Unity Catalog permissions.
- [ ] I can design data-quality expectations.
- [ ] I can explain Jobs parameters, retries, repairs, and backfills.
- [ ] I can diagnose basic performance and cost problems.

## Advanced
- [ ] I can design CI/CD with environment isolation.
- [ ] I can troubleshoot performance using evidence.
- [ ] I can investigate cost using system-table and workload evidence.
- [ ] I can design secure Delta Sharing.
- [ ] I can reason about feature freshness, leakage, and reproducibility.

## Senior / Staff
- [ ] I can design a multi-workspace Databricks platform.
- [ ] I can defend compute, ingestion, governance, and orchestration trade-offs.
- [ ] I can lead a production incident.
- [ ] I can connect data engineering and ML handoff contracts.
- [ ] I can quantify performance and cost trade-offs.
- [ ] I can explain recovery, reconciliation, and prevention.
- [ ] I can communicate architecture clearly under interview pressure.

# Final Quality Audit

- [x] Exactly 40 interview questions.
- [x] Q01–Q10 Basic.
- [x] Q11–Q20 Moderate.
- [x] Q21–Q30 Hard.
- [x] Q31–Q40 Advanced.
- [x] All 14 G4 topics represented.
- [x] Problem/scenario appears before the solution.
- [x] Every question includes interviewer evaluation criteria.
- [x] Every question includes an expected approach.
- [x] Every question includes a model answer.
- [x] Every question includes a step-by-step solving method.
- [x] Every question includes an example architecture/mental model.
- [x] Every question includes common interview mistakes.
- [x] Every question includes production considerations.
- [x] Every question includes a strong-answer pattern.
- [x] Every question includes follow-up questions.
- [x] Troubleshooting, trade-off, architecture, and production scenarios are represented.
- [x] Topic coverage matrix included.
- [x] Competency coverage matrix included.
- [x] Interview answer framework included.
- [x] Senior/Staff evaluation rubric included.
- [x] Interview readiness checklist included.
- [x] Current-product/version-sensitive safety guidance included.
- [x] No unrelated curriculum is required.
- [x] No additional artifact is required to use this document.

# Final Learning Outcome

After completing this interview set, the learner should be able to move from:

```text
"I know Databricks features."
```

to:

```text
"I can explain why a Databricks platform should be designed this way,
choose between alternatives, troubleshoot it when it fails,
measure its performance and cost, govern it safely,
and defend the design in a Senior Data Engineer interview."
```
