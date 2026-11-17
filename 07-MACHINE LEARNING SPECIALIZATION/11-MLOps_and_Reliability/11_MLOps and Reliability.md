# MLOps and Reliability — ML Specialization Roadmap

**Group 11 (G11)** of the specialization that follows Stage 5D of the [Roadmap](./Roadmap.md). It covers original categories **28 MLOps and ML Platform Engineering and 29 ML Reliability and Observability Engineering**. The group's defining question is: *how do I run models in production and keep them healthy?* It follows G1 to G10: [`01_Classical and Applied ML.md`](./01_Classical%20and%20Applied%20ML.md), [`02_Deep Learning by Modality.md`](./02_Deep%20Learning%20by%20Modality.md), [`03_Generative and Foundation Models.md`](./03_Generative%20and%20Foundation%20Models.md), [`04_Agents and Sequential Decisions.md`](./04_Agents%20and%20Sequential%20Decisions.md), [`05_Time and Anomaly Modeling.md`](./05_Time%20and%20Anomaly%20Modeling.md), [`06_Personalization Search and Matching.md`](./06_Personalization%20Search%20and%20Matching.md), [`07_Statistical Reasoning.md`](./07_Statistical%20Reasoning.md), [`08_Graphs and Optimization.md`](./08_Graphs%20and%20Optimization.md), [`09_Industry Domain ML.md`](./09_Industry%20Domain%20ML.md), [`10_Efficient and Scalable Systems.md`](./10_Efficient%20and%20Scalable%20Systems.md), [`11_MLOps and Reliability.md`](./11_MLOps%20and%20Reliability.md), [`12_Trustworthy ML.md`](./12_Trustworthy%20ML.md).

**Important context:** Stage 5D of the Roadmap is already a complete MLOps course (17 modules) and Stage 2E covers DevOps and platform engineering. G11 therefore does not teach MLOps again. It covers the layer above one team's pipeline: building and running an ML **platform** for many teams, and **reliability and observability engineering** as a discipline. Read the scope table before starting.

## G11 summary

| Item | Count |
|---|---|
| Modules (including overview and capstones) | 19 |
| Lesson files | 153 |
| Hands-on project files (module projects, overview project and capstones) | 57 |
| Folders inside the G11 tree | 37 |
| Files inside the G11 tree | 254 |

| Original category | Modules |
|---|---|
| 28 MLOps and ML Platform Engineering | 01 to 09 |
| 29 ML Reliability and Observability Engineering | 10 to 16 |
| Shared operating model for both | 17 |

## Scope and how G11 avoids repeating the Roadmap

These are **already learned** and are only referenced, never retaught. From **Stage 5D**: the production ML lifecycle and system design, code quality and testing, data contracts and quality gates, idempotency, point-in-time correctness, feature stores in practice, Airflow orchestration, MLflow tracking, registry, lineage and approval workflows, reproducible training, containers for ML, CI/CD with quality gates and canary, blue-green and shadow releases, rollback, batch and online serving, FastAPI services, BentoML, TorchServe, Triton and KServe, load testing, inference optimization and autoscaling, cloud deployment, logs, metrics and traces for ML, data and concept drift, delayed labels, Evidently, Prometheus and Grafana, alerts and runbooks, retraining triggers and champion validation, SLIs, SLOs and error budgets, circuit breakers and fallbacks, model cards and audit trails, fairness monitoring, disaster recovery and incident response for ML, ML-specific security, and production architecture patterns. From **Stage 2E**: container and CI/CD engineering, Kubernetes operations, Helm, Argo CD and GitOps, Argo Rollouts and Flagger, secrets and identity, SRE and incident management, the production observability stack, SBOM and SLSA, chaos engineering with Litmus and Chaos Mesh, backup and disaster recovery, multi-cluster operations, FinOps, and developer portals and Backstage. From **Stages 2C and 2D**: Dagster software-defined assets, Prefect flows, OpenLineage, data catalogs, data quality, reliability and disaster recovery for data systems. From **earlier groups**: GPU cluster scheduling and cost (G10), LLM application production integration and observability dashboards (G3), agent reliability and trajectory replay (G4), multiple-testing theory (G7), and decision-system design (G6).

**Boundaries with other groups** (so nothing overlaps): adversarial ML research, privacy-preserving training and responsible-AI methods belong to **G12**; benchmark and evaluation-system design belongs to **G13**; inference acceleration and distributed-training systems belong to **G10**; domain-specific regulatory validation belongs to **G9**.

| Roadmap topic already covered | Where G11 goes further |
|---|---|
| Production lifecycle and architecture patterns (5D), developer portals and Backstage (2E) | Module 01: the ML platform as a product, personas, golden paths, multi-tenancy and platform metrics |
| Airflow (5D), Dagster and Prefect (2C), Argo CD (2E) | Module 02: ML-native pipeline platforms (Kubeflow, Argo Workflows, Flyte, Metaflow, ZenML), caching correctness and migration |
| Feature stores in practice (5D) | Module 03: designing and operating a shared feature platform, skew automation, streaming features and deprecation |
| MLflow tracking, registry and lineage (5D), OpenLineage and catalogs (2D) | Module 04: running metadata, registry and dataset services for many teams, end-to-end lineage and labeling operations |
| Reproducible training and containers (5D) | Module 05: developer environments, base-image lifecycle, job abstractions, cost attribution and reproducibility as a guarantee |
| Serving frameworks, KServe and load testing (5D), Argo Rollouts and Flagger (2E) | Module 06: multi-model serving platforms, model gateways, model-specific canary analysis and batch inference contracts |
| SBOM, SLSA and secrets (2E), ML security (5D) | Module 07: model and dataset provenance, signing, ML bills of materials and policy-as-code promotion gates |
| LLM production integration (G3), agent reliability (G4) | Module 08: shared LLM and agent platform services: registries, evaluation gates, spend governance and tool sandboxes |
| IaC and GitOps (2E) | Module 09: ML infrastructure modules, environment promotion, platform upgrades and metadata disaster recovery |
| Logs, metrics and traces for ML (5D) | Module 10: telemetry schema design, outcome-join pipelines, sketches and monitors as code |
| Drift monitoring and delayed labels (5D) | Module 11: multivariate drift, label-free performance estimation, slice monitoring and alert statistics |
| SLIs, SLOs, error budgets and circuit breakers (5D), SRE (2E) | Module 12: quality SLOs, burn-rate alerts, degradation ladders and launch readiness |
| Chaos engineering tools (2E), DR (5D) | Module 13: ML-specific fault injection, silent failures, game days and resilience scorecards |
| Incident response for ML (5D), incident management (2E) | Module 14: ML triage playbooks, lineage-based blast radius and blameless postmortems for statistical causes |
| LLM observability dashboard (G3), trajectory replay (G4) | Module 15: operational design of tracing, online quality monitoring and judge audits |
| Retraining and feedback loops (5D) | Module 16: feedback-loop failures, poisoned feedback, retraining guardrails and staged promotion |
| Delivery and SRE practice (2E) | Module 17: ML on-call, delivery metrics, cost governance, technical debt and maturity roadmaps |

## G11 — MLOps and Reliability

**Defining question:** How do I run models in production and keep them healthy?

```text
ML Specialization/
└── G11 — MLOps and Reliability/
    ├── 00-G11-Overview/
    │   ├── Projects/
    │   │   ├── 01-g11-platform-sandbox-and-fault-injection-bootstrap.md
    │   │   └── README.md
    │   ├── 01-g11-scope-and-boundaries-with-stage-5d-2e-and-other-groups.md
    │   ├── 02-prerequisite-map-from-the-roadmap.md
    │   ├── 03-tooling-and-maintenance-register.md
    │   ├── 04-evaluation-and-reporting-standards.md
    │   ├── 05-completion-gate.md
    │   ├── README.md
    │   └── learning-plan.md
    ├── 01-ML-Platform-Product-Design-and-Operating-Model/
    │   ├── Projects/
    │   │   ├── 01-platform-user-research-and-journey-maps.md
    │   │   ├── 02-build-buy-assemble-decision-record.md
    │   │   ├── 03-golden-path-template-and-adoption-experiment.md
    │   │   └── README.md
    │   ├── 01-platform-as-a-product.md
    │   ├── 02-personas-and-journeys.md
    │   ├── 03-maturity-models.md
    │   ├── 04-golden-paths-and-escape-hatches.md
    │   ├── 05-platform-scope-decisions.md
    │   ├── 06-build-buy-or-assemble.md
    │   ├── 07-platform-interfaces.md
    │   ├── 08-multi-tenancy-design.md
    │   ├── 09-platform-metrics.md
    │   ├── 10-organization-design.md
    │   └── README.md
    ├── 02-Workflow-and-Pipeline-Platforms-Beyond-Airflow/
    │   ├── Projects/
    │   │   ├── 01-same-pipeline-on-three-orchestrators.md
    │   │   ├── 02-pipeline-caching-correctness-tests.md
    │   │   ├── 03-orchestrator-migration-plan.md
    │   │   └── README.md
    │   ├── 01-what-ml-pipelines-need-that-data-pipelines-do-not.md
    │   ├── 02-kubernetes-native-pipeline-systems.md
    │   ├── 03-python-first-ml-systems.md
    │   ├── 04-artifact-passing-and-content-addressed-caching.md
    │   ├── 05-dynamic-and-conditional-pipelines.md
    │   ├── 06-pipeline-portability.md
    │   ├── 07-scaling-pipelines.md
    │   ├── 08-testing-pipelines.md
    │   ├── 09-choosing-and-migrating-between-orchestrators-including-maintenance-and-ownership-checks.md
    │   └── README.md
    ├── 03-Feature-Platform-Engineering/
    │   ├── Projects/
    │   │   ├── 01-feature-platform-with-skew-detection.md
    │   │   ├── 02-streaming-feature-pipeline-with-freshness-slo.md
    │   │   ├── 03-feature-deprecation-and-impact-analysis.md
    │   │   └── README.md
    │   ├── 01-feature-platform-architecture.md
    │   ├── 02-online-store-design.md
    │   ├── 03-materialization-and-backfill-at-scale.md
    │   ├── 04-consistency-between-offline-and-online-values.md
    │   ├── 05-streaming-features.md
    │   ├── 06-feature-discovery-ownership-and-deprecation.md
    │   ├── 07-feature-versioning-and-compatibility-between-models-and-feature-definitions.md
    │   ├── 08-feature-platform-reliability.md
    │   ├── 09-cost-model.md
    │   ├── 10-tool-landscape.md
    │   └── README.md
    ├── 04-Metadata-Registry-and-Dataset-Platforms/
    │   ├── Projects/
    │   │   ├── 01-end-to-end-lineage-from-prediction-to-raw-data.md
    │   │   ├── 02-multi-team-registry-with-access-control-and-retention.md
    │   │   ├── 03-dataset-versioning-comparison.md
    │   │   └── README.md
    │   ├── 01-metadata-architecture.md
    │   ├── 02-operating-a-multi-team-tracking-and-registry-service.md
    │   ├── 03-model-registry-governance-at-organization-scale.md
    │   ├── 04-dataset-registry-and-versioning.md
    │   ├── 05-end-to-end-lineage-across-data-features-models-and-predictions-with-openlineage.md
    │   ├── 06-evaluation-results-as-first-class-records.md
    │   ├── 07-labeling-operations.md
    │   ├── 08-search-and-reuse.md
    │   ├── 09-migrating-or-federating-metadata-stores-without-losing-history.md
    │   └── README.md
    ├── 05-Training-Environment-and-Compute-Platform/
    │   ├── Projects/
    │   │   ├── 01-job-submission-cli-with-cost-attribution.md
    │   │   ├── 02-rebuild-and-reproduce-test-service.md
    │   │   ├── 03-base-image-lifecycle-automation.md
    │   │   └── README.md
    │   ├── 01-developer-environments.md
    │   ├── 02-base-image-strategy.md
    │   ├── 03-job-submission-abstractions.md
    │   ├── 04-reproducibility-as-a-platform-guarantee.md
    │   ├── 05-quotas-priorities-and-fair-sharing-from-the-user-s-point-of-view.md
    │   ├── 06-cost-visibility-and-attribution.md
    │   ├── 07-data-access-from-training-jobs.md
    │   ├── 08-environment-promotion.md
    │   ├── 09-platform-support-model.md
    │   └── README.md
    ├── 06-Model-Serving-and-Inference-Platform-Engineering/
    │   ├── Projects/
    │   │   ├── 01-multi-model-serving-platform-prototype.md
    │   │   ├── 02-automated-canary-analysis.md
    │   │   ├── 03-batch-inference-contract-and-backfill-tool.md
    │   │   └── README.md
    │   ├── 01-serving-platform-requirements.md
    │   ├── 02-multi-model-serving.md
    │   ├── 03-model-gateway.md
    │   ├── 04-autoscaling-beyond-cpu.md
    │   ├── 05-model-specific-canary-analysis.md
    │   ├── 06-request-and-response-logging-for-ml.md
    │   ├── 07-batch-inference-platform.md
    │   ├── 08-serving-platform-failure-modes.md
    │   ├── 09-cost-allocation-and-capacity-planning-for-shared-serving.md
    │   └── README.md
    ├── 07-ML-Supply-Chain-Security-Policy-as-Code-and-Compliance-Automation/
    │   ├── Projects/
    │   │   ├── 01-signed-model-promotion-pipeline.md
    │   │   ├── 02-ml-bom-generator-and-license-audit.md
    │   │   ├── 03-policy-as-code-promotion-gates.md
    │   │   └── README.md
    │   ├── 01-ml-supply-chain.md
    │   ├── 02-unsafe-model-formats-and-deserialization-risks.md
    │   ├── 03-model-and-artifact-signing.md
    │   ├── 04-extending-the-sbom-of-earlier-stages-to-ai-and-ml-bills-of-materials.md
    │   ├── 05-applying-license-scanning-to-models-and-datasets-which-have-different-license-types-from-code.md
    │   ├── 06-policy-as-code-for-ml.md
    │   ├── 07-secrets-and-identity-for-training-and-serving-workloads.md
    │   ├── 08-compliance-automation.md
    │   ├── 09-access-control-and-audit-logging-across-data-features-and-models.md
    │   └── README.md
    ├── 08-LLMOps-and-Agent-Platform-Operations/
    │   ├── Projects/
    │   │   ├── 01-prompt-and-eval-registry-with-release-gates.md
    │   │   ├── 02-llm-spend-governance-dashboard.md
    │   │   ├── 03-agent-tool-registry-and-sandbox-service.md
    │   │   └── README.md
    │   ├── 01-what-changes-for-the-platform.md
    │   ├── 02-prompt-and-configuration-registry.md
    │   ├── 03-evaluation-as-a-platform-service.md
    │   ├── 04-fine-tuning-as-a-platform-service.md
    │   ├── 05-vector-index-operations.md
    │   ├── 06-shared-llm-gateway-and-policy-enforcement-for-many-teams.md
    │   ├── 07-spend-governance.md
    │   ├── 08-agent-platform-services.md
    │   ├── 09-platform-risk-for-generative-workloads.md
    │   └── README.md
    ├── 09-Infrastructure-as-Code-and-GitOps-for-ML-Platforms/
    │   ├── Projects/
    │   │   ├── 01-ml-platform-infrastructure-modules-with-tests.md
    │   │   ├── 02-platform-upgrade-rehearsal.md
    │   │   ├── 03-metadata-store-disaster-recovery-drill.md
    │   │   └── README.md
    │   ├── 01-ml-infrastructure-modules.md
    │   ├── 02-environment-promotion-for-ml-systems.md
    │   ├── 03-ephemeral-environments.md
    │   ├── 04-gitops-for-model-and-configuration-releases.md
    │   ├── 05-testing-infrastructure-code-and-platform-upgrades.md
    │   ├── 06-upgrade-management.md
    │   ├── 07-platform-backup-restore-and-disaster-recovery-for-metadata-and-registries.md
    │   ├── 08-multi-cloud-and-exit-planning.md
    │   └── README.md
    ├── 10-ML-Observability-Architecture-and-Telemetry-Design/
    │   ├── Projects/
    │   │   ├── 01-prediction-log-and-outcome-join-pipeline.md
    │   │   ├── 02-distribution-sketch-monitoring.md
    │   │   ├── 03-monitors-as-code-with-tests.md
    │   │   └── README.md
    │   ├── 01-observability-questions-for-ml.md
    │   ├── 02-prediction-logging-schema.md
    │   ├── 03-joining-outcomes-to-predictions.md
    │   ├── 04-logging-at-scale.md
    │   ├── 05-profiles-and-sketches.md
    │   ├── 06-monitoring-stack-choices.md
    │   ├── 07-standard-telemetry-formats.md
    │   ├── 08-dashboards-that-answer-questions.md
    │   ├── 09-observability-as-code.md
    │   └── README.md
    ├── 11-Drift-Detection-Performance-Estimation-and-Slice-Monitoring/
    │   ├── Projects/
    │   │   ├── 01-drift-detector-benchmark-with-injected-shifts.md
    │   │   ├── 02-label-free-performance-estimation-study.md
    │   │   ├── 03-slice-monitoring-with-false-alarm-control.md
    │   │   └── README.md
    │   ├── 01-multivariate-drift-detection.md
    │   ├── 02-embedding-and-representation-drift-for-text-image-and-other-unstructured-inputs.md
    │   ├── 03-estimating-model-performance-without-labels.md
    │   ├── 04-detecting-concept-drift-from-delayed-or-partial-labels.md
    │   ├── 05-slice-discovery-and-slice-monitoring.md
    │   ├── 06-attribution-drift.md
    │   ├── 07-alert-statistics.md
    │   ├── 08-choosing-detection-windows-and-reference-data.md
    │   ├── 09-evaluating-monitors.md
    │   └── README.md
    ├── 12-Alerting-SLOs-and-Reliability-Engineering-for-ML/
    │   ├── Projects/
    │   │   ├── 01-quality-slo-design-and-burn-rate-alerts.md
    │   │   ├── 02-degradation-ladder-implementation.md
    │   │   ├── 03-model-launch-readiness-review.md
    │   │   └── README.md
    │   ├── 01-quality-slos.md
    │   ├── 02-multi-window-multi-burn-rate-alerting-applied-to-ml-signals.md
    │   ├── 03-model-and-feature-staleness-objectives.md
    │   ├── 04-dependency-mapping.md
    │   ├── 05-degradation-ladders.md
    │   ├── 06-load-shedding-backpressure-and-retry-storm-control-for-inference-services.md
    │   ├── 07-reliability-reviews.md
    │   ├── 08-the-cost-of-unreliability.md
    │   ├── 09-reliability-roadmaps-and-error-budget-policy.md
    │   └── README.md
    ├── 13-Chaos-Engineering-and-Resilience-Testing-for-ML-Systems/
    │   ├── Projects/
    │   │   ├── 01-ml-chaos-experiment-suite.md
    │   │   ├── 02-silent-failure-hunt.md
    │   │   ├── 03-game-day-runbook-and-retrospective.md
    │   │   └── README.md
    │   ├── 01-ml-failure-taxonomy.md
    │   ├── 02-failure-mode-and-effects-analysis-for-ml-systems.md
    │   ├── 03-fault-injection-for-data.md
    │   ├── 04-fault-injection-for-infrastructure.md
    │   ├── 05-silent-failures.md
    │   ├── 06-game-days.md
    │   ├── 07-testing-monitors-and-runbooks-by-injecting-known-faults.md
    │   ├── 08-safety-limits-for-experiments.md
    │   ├── 09-resilience-scorecards-and-tracking-improvement-over-time.md
    │   └── README.md
    ├── 14-Incident-Management-and-Root-Cause-Analysis-for-ML/
    │   ├── Projects/
    │   │   ├── 01-ml-incident-simulator-and-triage-playbook.md
    │   │   ├── 02-lineage-based-blast-radius-tool.md
    │   │   ├── 03-postmortem-library-and-trend-analysis.md
    │   │   └── README.md
    │   ├── 01-ml-incident-types-and-severity.md
    │   ├── 02-triage-playbooks.md
    │   ├── 03-diagnosis-workflow.md
    │   ├── 04-lineage-based-impact-analysis.md
    │   ├── 05-mitigation-options.md
    │   ├── 06-communication-during-incidents.md
    │   ├── 07-blameless-postmortems-for-ml.md
    │   ├── 08-learning-from-incidents.md
    │   ├── 09-incident-databases-and-trend-analysis.md
    │   └── README.md
    ├── 15-LLM-and-Agent-Observability-and-Online-Evaluation/
    │   ├── Projects/
    │   │   ├── 01-production-quality-monitor-with-judge-audit.md
    │   │   ├── 02-failure-to-eval-case-pipeline.md
    │   │   ├── 03-privacy-safe-llm-logging.md
    │   │   └── README.md
    │   ├── 01-what-to-observe-in-llm-systems.md
    │   ├── 02-tracing-conventions-for-generative-systems-and-span-design.md
    │   ├── 03-online-quality-monitoring.md
    │   ├── 04-calibrating-and-auditing-judges-in-production.md
    │   ├── 05-hallucination-refusal-and-safety-event-rates-as-monitored-metrics.md
    │   ├── 06-cost-and-latency-anomaly-detection.md
    │   ├── 07-privacy-safe-logging-of-prompts-and-outputs.md
    │   ├── 08-closing-the-loop.md
    │   ├── 09-alerting-on-quality-with-noisy-metrics.md
    │   └── README.md
    ├── 16-Reliability-of-Learning-Loops-and-Safe-Retraining/
    │   ├── Projects/
    │   │   ├── 01-feedback-loop-degradation-simulation.md
    │   │   ├── 02-poisoned-feedback-detection.md
    │   │   ├── 03-safe-retraining-pipeline-with-staged-promotion.md
    │   │   └── README.md
    │   ├── 01-feedback-loop-failures.md
    │   ├── 02-poisoned-and-low-quality-feedback-data.md
    │   ├── 03-retraining-guardrails.md
    │   ├── 04-evaluation-drift.md
    │   ├── 05-safe-exploration-data-collection-to-break-feedback-loops.md
    │   ├── 06-rollback-of-learned-systems.md
    │   ├── 07-monitoring-the-loop.md
    │   ├── 08-human-oversight-of-automatic-retraining.md
    │   └── README.md
    ├── 17-MLOps-Operating-Practices-Teams-Costs-and-Maturity/
    │   ├── Projects/
    │   │   ├── 01-mlops-maturity-assessment-and-roadmap.md
    │   │   ├── 02-ml-delivery-metrics-dashboard.md
    │   │   ├── 03-technical-debt-register-and-prioritization.md
    │   │   └── README.md
    │   ├── 01-ownership-and-on-call-for-models.md
    │   ├── 02-delivery-metrics-for-ml-teams.md
    │   ├── 03-cost-governance-for-ml.md
    │   ├── 04-technical-debt-in-ml-systems.md
    │   ├── 05-migration-from-ad-hoc-to-platform-based-workflows.md
    │   ├── 06-vendor-selection-and-contract-risks-for-ml-tools.md
    │   ├── 07-documentation-onboarding-and-knowledge-transfer.md
    │   ├── 08-metrics-that-matter.md
    │   ├── 09-career-paths-and-skills-for-mlops-and-ml-reliability-engineers.md
    │   └── README.md
    ├── 18-G11-Capstones/
    │   ├── 01-internal-ml-platform-mvp.md
    │   ├── 02-ml-observability-and-reliability-program.md
    │   ├── 03-llmops-platform-extension.md
    │   ├── 04-mlops-operating-model-and-roadmap.md
    │   ├── 05-g11-readiness-assessment.md
    │   └── README.md
    └── README.md
```

### 00 — G11 Overview

**Purpose:** the single authoritative plan for G11 with scope, boundaries, prerequisite map, tooling and maintenance register, evaluation standards and completion gate.

- `01-g11-scope-and-boundaries-with-stage-5d-2e-and-other-groups.md` — what G11 teaches and what it leaves to Stages 5D and 2E and other groups.
- `02-prerequisite-map-from-the-roadmap.md` — Roadmap lessons assumed for each G11 module, named precisely.
- `03-tooling-and-maintenance-register.md` — every platform, orchestrator, monitoring and security tool with version, licence, maintenance status and exit cost.
- `04-evaluation-and-reporting-standards.md` — rules for validating monitors and platform claims with injected faults and replayed incidents, and the report template.
- `05-completion-gate.md` — measurable criteria to finish G11.
- `learning-plan.md` — recommended order, platform and reliability tracks and a low-cost local-cluster setup for learners without cloud budgets.

**Project 1: g11 platform sandbox and fault-injection bootstrap**  
- Data: the training and serving pipeline from Stage 5D.  
- Task: stand up a local or low-cost sandbox of the platform components with infrastructure as code, a replayable incident library and a fault-injection harness.  
- Deliverables: infrastructure code, harness, three seeded incidents and smoke tests.  
- Pass gate: a clean machine recreates the sandbox from code and the harness reproduces each seeded incident.

### 01 — ML Platform Product Design and Operating Model

**Outcome:** Design an internal ML platform as a product used by many teams, rather than as a pile of tools. Stage 5D teaches how one team operates ML in production, and Stage 2E covers platform engineering and internal developer platforms in general; this module is about the ML-specific platform.

**Lessons**

- `01-platform-as-a-product.md` — Platform as a product: users, jobs to be done and the adoption problem
- `02-personas-and-journeys.md` — Personas and journeys: data scientist, ML engineer, analyst, reviewer and on-call engineer
- `03-maturity-models.md` — Maturity models: automation levels in ML delivery and what each level costs
- `04-golden-paths-and-escape-hatches.md` — Golden paths and escape hatches: paved roads for common ML workflows
- `05-platform-scope-decisions.md` — Platform scope decisions: what to standardize and what to leave to teams, building on the developer-portal and service-catalog lessons of Stage 2E
- `06-build-buy-or-assemble.md` — Build, buy or assemble: cloud managed services, open-source stacks and commercial platforms
- `07-platform-interfaces.md` — Platform interfaces: SDKs, command-line tools, APIs and configuration contracts
- `08-multi-tenancy-design.md` — Multi-tenancy design: isolation, quotas, cost attribution and noisy neighbors
- `09-platform-metrics.md` — Platform metrics: adoption, time to first model in production, lead time and platform reliability
- `10-organization-design.md` — Organization design: platform team, enabling team and stream-aligned teams

**Hands-on projects**

- **Project 1: platform user research and journey maps**  
  - Data: Five interviews with practitioners or simulated personas built from public case studies  
  - Task: Run interviews, map the model-to-production journey for each persona and rank pain points by frequency and severity.  
  - Deliverables: Research report with journey maps and a prioritized backlog.  
  - Pass gate: Priorities justified by evidence from the interviews, not opinion.
- **Project 2: build buy assemble decision record**  
  - Data: Requirements for a hypothetical team of 15 ML practitioners  
  - Task: Score managed, open-source and commercial options against requirements, cost and risk and write a decision record with exit costs.  
  - Deliverables: Decision record with scoring and sensitivity analysis.  
  - Pass gate: Prices and capabilities cited with source and date.
- **Project 3: golden path template and adoption experiment**  
  - Data: A training-to-serving workflow from Stage 5D  
  - Task: Turn the workflow into a template with an escape hatch, test it with two outside users and measure time to a deployed model.  
  - Deliverables: Template, usage notes and timing results.  
  - Pass gate: Time-to-deploy measured before and after the template with at least two users.

### 02 — Workflow and Pipeline Platforms Beyond Airflow

**Outcome:** Choose and operate workflow systems built for ML artifacts. DAG concepts, Airflow fundamentals, failure handling and parameterized pipelines (Stage 5D), and Dagster software-defined assets and Prefect flows (Stage 2C) are already covered.

**Lessons**

- `01-what-ml-pipelines-need-that-data-pipelines-do-not.md` — What ML pipelines need that data pipelines do not: typed artifacts, caching, lineage and GPU steps
- `02-kubernetes-native-pipeline-systems.md` — Kubernetes-native pipeline systems: Kubeflow Pipelines and Argo Workflows
- `03-python-first-ml-systems.md` — Python-first ML systems: Flyte, Metaflow and ZenML compared with the Dagster and Prefect covered in Stage 2C
- `04-artifact-passing-and-content-addressed-caching.md` — Artifact passing and content-addressed caching: skipping unchanged steps safely
- `05-dynamic-and-conditional-pipelines.md` — Dynamic and conditional pipelines: fan-out over data, models or hyperparameters
- `06-pipeline-portability.md` — Pipeline portability: separating pipeline definition from execution backend
- `07-scaling-pipelines.md` — Scaling pipelines: parallelism limits, scheduling latency and cost
- `08-testing-pipelines.md` — Testing pipelines: unit, local-run and integration tests, and pipeline contracts
- `09-choosing-and-migrating-between-orchestrators-including-maintenance-and-ownership-checks.md` — Choosing and migrating between orchestrators, including maintenance and ownership checks

**Hands-on projects**

- **Project 1: same pipeline on three orchestrators**  
  - Data: The training pipeline from Stage 5D  
  - Task: Implement it on two ML-native orchestrators besides Airflow and compare development effort, caching behavior, observability and failure recovery.  
  - Deliverables: Three implementations and a comparison.  
  - Pass gate: Identical outputs verified across implementations.
- **Project 2: pipeline caching correctness tests**  
  - Data: A pipeline with expensive steps  
  - Task: Add content-addressed caching and write tests that prove stale outputs are never reused after code, data or parameter changes.  
  - Deliverables: Caching layer and tests.  
  - Pass gate: Every cache-invalidating change is detected by a test.
- **Project 3: orchestrator migration plan**  
  - Data: A legacy script-based workflow  
  - Task: Plan and execute a staged migration with parallel runs and output comparison.  
  - Deliverables: Migration plan and comparison results.  
  - Pass gate: Old and new systems agree on outputs before cut-over.

### 03 — Feature Platform Engineering

**Outcome:** Design and operate a shared feature platform. Using a feature store, point-in-time correctness, batch and online feature computation and data contracts are covered in Stage 5D.

**Lessons**

- `01-feature-platform-architecture.md` — Feature platform architecture: offline store, online store, registry and transformation engine
- `02-online-store-design.md` — Online store design: key-value stores, latency targets and capacity
- `03-materialization-and-backfill-at-scale.md` — Materialization and backfill at scale: incremental updates and recomputation cost
- `04-consistency-between-offline-and-online-values.md` — Consistency between offline and online values: skew sources and automated checks
- `05-streaming-features.md` — Streaming features: windowed aggregates with a stream processor
- `06-feature-discovery-ownership-and-deprecation.md` — Feature discovery, ownership and deprecation: governing a shared catalog
- `07-feature-versioning-and-compatibility-between-models-and-feature-definitions.md` — Feature versioning and compatibility between models and feature definitions
- `08-feature-platform-reliability.md` — Feature platform reliability: freshness objectives and degraded-mode serving
- `09-cost-model.md` — Cost model: storage, compute and the economics of sharing features across teams
- `10-tool-landscape.md` — Tool landscape: open-source and commercial feature stores and their maintenance status

**Hands-on projects**

- **Project 1: feature platform with skew detection**  
  - Data: A public dataset with timestamps, such as a transactions or events dataset  
  - Task: Build offline and online feature serving from one definition and an automated check that compares values between them.  
  - Deliverables: Platform prototype and skew checker.  
  - Pass gate: Injected offline-online discrepancies are detected.
- **Project 2: streaming feature pipeline with freshness slo**  
  - Data: A simulated event stream  
  - Task: Compute windowed features in a stream processor, define a freshness objective and test behavior under delay and outage.  
  - Deliverables: Pipeline and freshness tests.  
  - Pass gate: Freshness objective violations alert within a stated delay.
- **Project 3: feature deprecation and impact analysis**  
  - Data: A feature catalog with consuming models  
  - Task: Build tooling that reports which models depend on a feature and simulate a safe deprecation.  
  - Deliverables: Lineage-based impact tool and deprecation runbook.  
  - Pass gate: Impact report matches the known dependency graph.

### 04 — Metadata Registry and Dataset Platforms

**Outcome:** Run experiment tracking, model registry, dataset registry and lineage as shared services. MLflow tracking, registry, packaging, lineage and promotion workflows are covered in Stage 5D, and data catalogs and OpenLineage in Stage 2D.

**Lessons**

- `01-metadata-architecture.md` — Metadata architecture: what to record about data, code, models and runs and how to keep it queryable
- `02-operating-a-multi-team-tracking-and-registry-service.md` — Operating a multi-team tracking and registry service: scale, access control and retention
- `03-model-registry-governance-at-organization-scale.md` — Model registry governance at organization scale: stages, owners, approvals and deprecation
- `04-dataset-registry-and-versioning.md` — Dataset registry and versioning: lakeFS, DVC and table-format snapshots compared
- `05-end-to-end-lineage-across-data-features-models-and-predictions-with-openlineage.md` — End-to-end lineage across data, features, models and predictions with OpenLineage
- `06-evaluation-results-as-first-class-records.md` — Evaluation results as first-class records: linking metrics to datasets, code and thresholds
- `07-labeling-operations.md` — Labeling operations: tools such as Label Studio, quality assurance and feedback ingestion
- `08-search-and-reuse.md` — Search and reuse: finding models, datasets and experiments across teams
- `09-migrating-or-federating-metadata-stores-without-losing-history.md` — Migrating or federating metadata stores without losing history

**Hands-on projects**

- **Project 1: end to end lineage from prediction to raw data**  
  - Data: A pipeline from Stage 5D with data, features and a registered model  
  - Task: Emit lineage events at every step and build a query that traces any served prediction back to code, model, features and raw data.  
  - Deliverables: Lineage service and trace queries.  
  - Pass gate: Trace of a sample prediction verified by hand against the pipeline.
- **Project 2: multi team registry with access control and retention**  
  - Data: A tracking and registry deployment you set up  
  - Task: Add team isolation, promotion approvals and retention policies and test them with simulated teams.  
  - Deliverables: Configuration and policy tests.  
  - Pass gate: A team cannot read or promote another team's models in tests.
- **Project 3: dataset versioning comparison**  
  - Data: A dataset that changes weekly  
  - Task: Compare two dataset versioning approaches on storage cost, reproducibility and workflow effort.  
  - Deliverables: Comparison report.  
  - Pass gate: Reproducibility verified by retraining from a past version.

### 05 — Training Environment and Compute Platform

**Outcome:** Give practitioners reliable, reproducible and cost-visible compute. Reproducible training, containers and resource profiling are covered in Stage 5D, and GPU cluster scheduling and cost in G10.

**Lessons**

- `01-developer-environments.md` — Developer environments: managed notebooks, remote development and dev containers
- `02-base-image-strategy.md` — Base image strategy: curated images, versioning, vulnerability scanning and update cadence
- `03-job-submission-abstractions.md` — Job submission abstractions: one interface over local, cluster and cloud execution
- `04-reproducibility-as-a-platform-guarantee.md` — Reproducibility as a platform guarantee: pinning, provenance and rebuild tests
- `05-quotas-priorities-and-fair-sharing-from-the-user-s-point-of-view.md` — Quotas, priorities and fair sharing from the user's point of view
- `06-cost-visibility-and-attribution.md` — Cost visibility and attribution: showback and chargeback for ML spend
- `07-data-access-from-training-jobs.md` — Data access from training jobs: credentials, mounts and egress control
- `08-environment-promotion.md` — Environment promotion: from notebook to scheduled job to production
- `09-platform-support-model.md` — Platform support model: documentation, on-call and office hours

**Hands-on projects**

- **Project 1: job submission cli with cost attribution**  
  - Data: A small cluster or cloud account you control  
  - Task: Build a CLI that submits jobs to local and remote backends, tags every job with owner and project and produces a cost report.  
  - Deliverables: CLI and cost report.  
  - Pass gate: Costs reconcile with the provider's bill within a stated tolerance.
- **Project 2: rebuild and reproduce test service**  
  - Data: Ten past training runs with recorded environments  
  - Task: Rebuild each environment and rerun the job automatically and report which runs are still reproducible and why others are not.  
  - Deliverables: Reproducibility report and tooling.  
  - Pass gate: Non-reproducible runs have an identified cause.
- **Project 3: base image lifecycle automation**  
  - Data: A set of curated ML images  
  - Task: Automate scanning, rebuilds and compatibility tests and measure patch lead time.  
  - Deliverables: Pipeline and lead-time metrics.  
  - Pass gate: A vulnerable dependency injected for the test is patched within the target time.

### 06 — Model Serving and Inference Platform Engineering

**Outcome:** Run many models for many teams on shared serving infrastructure. Writing one inference service, serving frameworks, KServe, load testing and release strategies are covered in Stage 5D, Argo Rollouts and Flagger progressive delivery in Stage 2E, and engine-level LLM serving in G10.

**Lessons**

- `01-serving-platform-requirements.md` — Serving platform requirements: tiers, service-level objectives and standardized contracts
- `02-multi-model-serving.md` — Multi-model serving: density, cold starts and scale-to-zero
- `03-model-gateway.md` — Model gateway: routing, versioning, authentication and quota across models
- `04-autoscaling-beyond-cpu.md` — Autoscaling beyond CPU: queue-depth and latency-based scaling with event-driven autoscalers
- `05-model-specific-canary-analysis.md` — Model-specific canary analysis: quality and business metrics and statistical decision rules on top of the Argo Rollouts and Flagger traffic analysis of Stage 2E
- `06-request-and-response-logging-for-ml.md` — Request and response logging for ML: capture, sampling and privacy at platform level
- `07-batch-inference-platform.md` — Batch inference platform: large-scale scoring jobs and output contracts
- `08-serving-platform-failure-modes.md` — Serving-platform failure modes: noisy neighbors, thundering herds and cascading timeouts
- `09-cost-allocation-and-capacity-planning-for-shared-serving.md` — Cost allocation and capacity planning for shared serving

**Hands-on projects**

- **Project 1: multi model serving platform prototype**  
  - Data: Five small models with different latency and traffic profiles  
  - Task: Build a platform with a gateway, per-model autoscaling and quotas and test noisy-neighbor behavior.  
  - Deliverables: Platform and isolation tests.  
  - Pass gate: A misbehaving model cannot degrade others beyond a stated limit.
- **Project 2: automated canary analysis**  
  - Data: A model service with a baseline and candidate version  
  - Task: Implement canary comparison with statistical decision rules and automatic rollback and test with a degraded candidate.  
  - Deliverables: Canary analyzer and fault-injection tests.  
  - Pass gate: A degraded candidate is rolled back within the target time without false rollbacks on identical versions.
- **Project 3: batch inference contract and backfill tool**  
  - Data: A large scored dataset  
  - Task: Build a batch scoring service with idempotent outputs, resumability and an output schema contract.  
  - Deliverables: Service and failure tests.  
  - Pass gate: Killing the job at any step and resuming yields identical outputs.

### 07 — ML Supply Chain Security Policy as Code and Compliance Automation

**Outcome:** Secure and govern what the platform ships. Software supply-chain basics, SBOM and license compliance, SLSA provenance, secrets and policy as code are covered in Stages 1 to 2E, and ML-specific attacks in Stage 5D; adversarial-ML research is covered later in G12.

**Lessons**

- `01-ml-supply-chain.md` — ML supply chain: datasets, pretrained weights, containers and packages as attack surface
- `02-unsafe-model-formats-and-deserialization-risks.md` — Unsafe model formats and deserialization risks: safe serialization practices
- `03-model-and-artifact-signing.md` — Model and artifact signing: provenance and verification with Sigstore-based tooling and the OpenSSF model-signing effort
- `04-extending-the-sbom-of-earlier-stages-to-ai-and-ml-bills-of-materials.md` — Extending the SBOM of earlier stages to AI and ML bills of materials: recording models, datasets and licenses
- `05-applying-license-scanning-to-models-and-datasets-which-have-different-license-types-from-code.md` — Applying license scanning to models and datasets, which have different license types from code
- `06-policy-as-code-for-ml.md` — Policy as code for ML: admission control and promotion gates with policy engines
- `07-secrets-and-identity-for-training-and-serving-workloads.md` — Secrets and identity for training and serving workloads
- `08-compliance-automation.md` — Compliance automation: evidence collection from the platform for audits
- `09-access-control-and-audit-logging-across-data-features-and-models.md` — Access control and audit logging across data, features and models

**Hands-on projects**

- **Project 1: signed model promotion pipeline**  
  - Data: A registry and a deployment pipeline  
  - Task: Require signature verification and policy checks before a model can be deployed and test with tampered and unapproved artifacts.  
  - Deliverables: Pipeline and tamper tests.  
  - Pass gate: Tampered and unapproved artifacts are rejected in tests.
- **Project 2: ml bom generator and license audit**  
  - Data: Models and datasets from your registry  
  - Task: Generate a bill of materials for each deployed model including datasets, base models and licenses and flag conflicts.  
  - Deliverables: Generator and audit report.  
  - Pass gate: License terms read from primary sources and dated.
- **Project 3: policy as code promotion gates**  
  - Data: A set of governance rules you write  
  - Task: Encode rules such as required evaluation reports, documented owners and fairness checks and test them against passing and failing cases.  
  - Deliverables: Policy set and test suite.  
  - Pass gate: Every rule has at least one passing and one failing test.

### 08 — LLMOps and Agent Platform Operations

**Outcome:** Extend the platform to language-model applications. Application-level LLM production integration is covered in G3, agent reliability in G4 and LLM observability in module 15; this module covers platform services shared across teams.

**Lessons**

- `01-what-changes-for-the-platform.md` — What changes for the platform: prompts, adapters, vector indexes, evaluation sets and traces as managed assets
- `02-prompt-and-configuration-registry.md` — Prompt and configuration registry: versioning, review and rollout
- `03-evaluation-as-a-platform-service.md` — Evaluation as a platform service: shared datasets, judges and release gates
- `04-fine-tuning-as-a-platform-service.md` — Fine-tuning as a platform service: job templates, data governance and adapter registry
- `05-vector-index-operations.md` — Vector index operations: lifecycle, rebuilds and access control
- `06-shared-llm-gateway-and-policy-enforcement-for-many-teams.md` — Shared LLM gateway and policy enforcement for many teams
- `07-spend-governance.md` — Spend governance: budgets, anomaly alerts and chargeback for model usage
- `08-agent-platform-services.md` — Agent platform services: tool registry, sandbox runtime and run history
- `09-platform-risk-for-generative-workloads.md` — Platform risk for generative workloads: data leakage, abuse and incident response

**Hands-on projects**

- **Project 1: prompt and eval registry with release gates**  
  - Data: Two LLM applications from earlier groups  
  - Task: Build a registry for prompts and evaluation sets with review workflow and a gate that blocks regressions.  
  - Deliverables: Registry and gate demonstration.  
  - Pass gate: A deliberately worse prompt is blocked by the gate.
- **Project 2: llm spend governance dashboard**  
  - Data: Usage logs from your applications or simulated logs  
  - Task: Build per-team budgets, anomaly alerts and chargeback reports and test with an injected runaway workload.  
  - Deliverables: Dashboard and alert tests.  
  - Pass gate: Injected spend spike alerts within a stated delay.
- **Project 3: agent tool registry and sandbox service**  
  - Data: Tools from G4  
  - Task: Build a registry with permissions and a sandboxed execution service shared across agents.  
  - Deliverables: Service and permission tests.  
  - Pass gate: An agent cannot call a tool outside its granted scope.

### 09 — Infrastructure as Code and GitOps for ML Platforms

**Outcome:** Manage the platform itself as versioned, testable code. Infrastructure as code, GitOps and progressive delivery are covered in Stage 2E; this module applies them to ML-specific infrastructure.

**Lessons**

- `01-ml-infrastructure-modules.md` — ML infrastructure modules: reusable definitions for storage, clusters, registries and endpoints
- `02-environment-promotion-for-ml-systems.md` — Environment promotion for ML systems: development, staging and production parity
- `03-ephemeral-environments.md` — Ephemeral environments: per-branch pipelines and preview deployments
- `04-gitops-for-model-and-configuration-releases.md` — GitOps for model and configuration releases
- `05-testing-infrastructure-code-and-platform-upgrades.md` — Testing infrastructure code and platform upgrades
- `06-upgrade-management.md` — Upgrade management: operators, drivers, runtimes and library compatibility matrices
- `07-platform-backup-restore-and-disaster-recovery-for-metadata-and-registries.md` — Platform backup, restore and disaster recovery for metadata and registries
- `08-multi-cloud-and-exit-planning.md` — Multi-cloud and exit planning: portability and lock-in trade-offs

**Hands-on projects**

- **Project 1: ml platform infrastructure modules with tests**  
  - Data: A cloud account or local Kubernetes cluster  
  - Task: Write reusable infrastructure modules for an ML environment and automated tests that create, verify and destroy them.  
  - Deliverables: Modules and test pipeline.  
  - Pass gate: Environments are created and destroyed by automation only.
- **Project 2: platform upgrade rehearsal**  
  - Data: A staging copy of your platform  
  - Task: Rehearse an upgrade of a core component with rollback and compatibility tests.  
  - Deliverables: Runbook and rehearsal report.  
  - Pass gate: Rollback verified by restoring prior behavior.
- **Project 3: metadata store disaster recovery drill**  
  - Data: Your tracking and registry services  
  - Task: Back up and restore the metadata and artifact stores in a drill and measure recovery time and data loss.  
  - Deliverables: Drill report.  
  - Pass gate: Recovery time and recovery point compared with stated targets.

### 10 — ML Observability Architecture and Telemetry Design

**Outcome:** Design what to record about a production model so that problems can be found and explained later. Logs, metrics and traces, basic drift monitoring, Evidently, Prometheus and Grafana, and alert runbooks are covered in Stage 5D and Stage 2E.

**Lessons**

- `01-observability-questions-for-ml.md` — Observability questions for ML: what must be answerable after an incident
- `02-prediction-logging-schema.md` — Prediction logging schema: inputs, features, outputs, versions, identifiers and timestamps
- `03-joining-outcomes-to-predictions.md` — Joining outcomes to predictions: delayed ground-truth pipelines and their failure modes
- `04-logging-at-scale.md` — Logging at scale: sampling, retention, cost and privacy-preserving logs
- `05-profiles-and-sketches.md` — Profiles and sketches: compact summaries of data distributions for monitoring
- `06-monitoring-stack-choices.md` — Monitoring stack choices: open-source libraries, platforms and in-house systems with maintenance checks
- `07-standard-telemetry-formats.md` — Standard telemetry formats: OpenTelemetry conventions for ML and generative systems
- `08-dashboards-that-answer-questions.md` — Dashboards that answer questions: from model health to business impact
- `09-observability-as-code.md` — Observability as code: versioned monitors, dashboards and tests

**Hands-on projects**

- **Project 1: prediction log and outcome join pipeline**  
  - Data: A simulated model service with delayed labels  
  - Task: Build the logging schema and a join pipeline that attaches outcomes days later, handles late and missing labels and reports join coverage.  
  - Deliverables: Pipeline and coverage report.  
  - Pass gate: Join correctness verified against ground truth in simulation.
- **Project 2: distribution sketch monitoring**  
  - Data: A high-volume feature stream  
  - Task: Compare full-data monitoring with sketch-based monitoring on accuracy of drift detection and cost.  
  - Deliverables: Cost-accuracy comparison.  
  - Pass gate: Detection delay and false-alarm rate reported for both.
- **Project 3: monitors as code with tests**  
  - Data: Monitors from Stage 5D  
  - Task: Rewrite monitors as versioned code and add unit tests that replay known incidents to confirm they fire.  
  - Deliverables: Monitor repository and replay tests.  
  - Pass gate: Each monitor is tested against a replayed incident.

### 11 — Drift Detection Performance Estimation and Slice Monitoring

**Outcome:** Detect real model problems while limiting false alarms. Data drift versus concept drift, feature and prediction distribution monitoring and delayed labels are covered in Stage 5D; multiple-testing theory in G7.

**Lessons**

- `01-multivariate-drift-detection.md` — Multivariate drift detection: classifier two-sample tests and kernel methods
- `02-embedding-and-representation-drift-for-text-image-and-other-unstructured-inputs.md` — Embedding and representation drift for text, image and other unstructured inputs
- `03-estimating-model-performance-without-labels.md` — Estimating model performance without labels: confidence-based and drift-based estimators
- `04-detecting-concept-drift-from-delayed-or-partial-labels.md` — Detecting concept drift from delayed or partial labels
- `05-slice-discovery-and-slice-monitoring.md` — Slice discovery and slice monitoring: finding the subgroups that fail
- `06-attribution-drift.md` — Attribution drift: monitoring explanations and feature importance
- `07-alert-statistics.md` — Alert statistics: controlling false alarms across many features and slices
- `08-choosing-detection-windows-and-reference-data.md` — Choosing detection windows and reference data
- `09-evaluating-monitors.md` — Evaluating monitors: detection delay, false-alarm rate and incident recall on replayed history

**Hands-on projects**

- **Project 1: drift detector benchmark with injected shifts**  
  - Data: Several public datasets with synthetic covariate, label and concept shifts injected at known times  
  - Task: Compare univariate tests, classifier two-sample tests and embedding-based detectors on detection delay and false alarms.  
  - Deliverables: Benchmark.  
  - Pass gate: Many replications with known shift timing.
- **Project 2: label free performance estimation study**  
  - Data: A model with held-out later data  
  - Task: Estimate accuracy over time without labels using two methods and compare with realized accuracy.  
  - Deliverables: Estimation-error analysis.  
  - Pass gate: Estimators fitted without access to later labels.
- **Project 3: slice monitoring with false alarm control**  
  - Data: A model with many segments  
  - Task: Monitor hundreds of slices with and without multiple-testing control and measure alert precision.  
  - Deliverables: Alert-precision comparison.  
  - Pass gate: Known injected failures in selected slices.

### 12 — Alerting SLOs and Reliability Engineering for ML

**Outcome:** Set reliability targets for model behavior and alert on them sensibly. SLIs, SLOs, error budgets and circuit breakers for ML services are introduced in Stage 5D, and SRE practice in Stage 2E.

**Lessons**

- `01-quality-slos.md` — Quality SLOs: defining objectives for correctness, freshness and coverage when labels are delayed
- `02-multi-window-multi-burn-rate-alerting-applied-to-ml-signals.md` — Multi-window, multi-burn-rate alerting applied to ML signals
- `03-model-and-feature-staleness-objectives.md` — Model and feature staleness objectives
- `04-dependency-mapping.md` — Dependency mapping: upstream data, feature, model and downstream consumer reliability
- `05-degradation-ladders.md` — Degradation ladders: fallback models, cached predictions and rule-based safeguards
- `06-load-shedding-backpressure-and-retry-storm-control-for-inference-services.md` — Load shedding, backpressure and retry-storm control for inference services
- `07-reliability-reviews.md` — Reliability reviews: launch checklists and readiness criteria for new models
- `08-the-cost-of-unreliability.md` — The cost of unreliability: quantifying incidents in money and trust
- `09-reliability-roadmaps-and-error-budget-policy.md` — Reliability roadmaps and error-budget policy

**Hands-on projects**

- **Project 1: quality slo design and burn rate alerts**  
  - Data: A model with delayed labels in simulation  
  - Task: Define quality and freshness SLOs and implement multi-window burn-rate alerts, then evaluate on replayed incidents.  
  - Deliverables: SLO document and alert tests.  
  - Pass gate: Alerts fire on injected incidents and stay quiet on normal variation.
- **Project 2: degradation ladder implementation**  
  - Data: A model service with a fallback model and rules  
  - Task: Implement automatic degradation steps and measure quality and latency at each step under dependency failures.  
  - Deliverables: Implementation and failure-injection results.  
  - Pass gate: Each step triggers and recovers as designed under tests.
- **Project 3: model launch readiness review**  
  - Data: A model you plan to deploy  
  - Task: Run a readiness review with a checklist, a failure-mode analysis and a go or no-go decision.  
  - Deliverables: Review record.  
  - Pass gate: Every checklist item has evidence.

### 13 — Chaos Engineering and Resilience Testing for ML Systems

**Outcome:** Find weaknesses by breaking things on purpose, safely. Chaos engineering with Litmus and Chaos Mesh and disaster recovery are covered in Stages 2D and 2E; this module covers faults that are specific to ML and does not repeat the general tooling.

**Lessons**

- `01-ml-failure-taxonomy.md` — ML failure taxonomy: data, features, model, infrastructure and feedback-loop failures
- `02-failure-mode-and-effects-analysis-for-ml-systems.md` — Failure mode and effects analysis for ML systems
- `03-fault-injection-for-data.md` — Fault injection for data: corrupted, missing, stale and shifted inputs
- `04-fault-injection-for-infrastructure.md` — Fault injection for infrastructure: feature-store outage, model-server crash, GPU failure and network partition
- `05-silent-failures.md` — Silent failures: faults that keep the system running with wrong outputs
- `06-game-days.md` — Game days: planning, running and learning from exercises
- `07-testing-monitors-and-runbooks-by-injecting-known-faults.md` — Testing monitors and runbooks by injecting known faults
- `08-safety-limits-for-experiments.md` — Safety limits for experiments: blast-radius control and abort conditions
- `09-resilience-scorecards-and-tracking-improvement-over-time.md` — Resilience scorecards and tracking improvement over time

**Hands-on projects**

- **Project 1: ml chaos experiment suite**  
  - Data: A staging deployment of a model service with features and monitoring  
  - Task: Build and run a suite of data and infrastructure fault injections and record detection, impact and recovery for each.  
  - Deliverables: Experiment suite and results table.  
  - Pass gate: Experiments run only in staging with abort conditions.
- **Project 2: silent failure hunt**  
  - Data: A pipeline with deliberately planted silent bugs  
  - Task: Find silent failures using only the monitoring in place and add checks that would have caught each.  
  - Deliverables: Findings and new checks.  
  - Pass gate: Each planted bug is caught by a new automated check.
- **Project 3: game day runbook and retrospective**  
  - Data: A simulated incident scenario  
  - Task: Run a team exercise from a runbook and write a blameless retrospective with action items.  
  - Deliverables: Runbook and retrospective.  
  - Pass gate: Each action item has an owner and a verification step.

### 14 — Incident Management and Root Cause Analysis for ML

**Outcome:** Respond to model incidents quickly and learn from them. Disaster recovery and incident response for ML are introduced in Stage 5D, and incident management in Stage 2E; this module covers diagnosis specific to learned systems.

**Lessons**

- `01-ml-incident-types-and-severity.md` — ML incident types and severity: quality, fairness, safety, cost and availability
- `02-triage-playbooks.md` — Triage playbooks: separating data, feature, model, serving and feedback causes
- `03-diagnosis-workflow.md` — Diagnosis workflow: change history, slice analysis and counterfactual replay
- `04-lineage-based-impact-analysis.md` — Lineage-based impact analysis: what else is affected and who must be told
- `05-mitigation-options.md` — Mitigation options: rollback, freeze, fallback, retrain and manual override
- `06-communication-during-incidents.md` — Communication during incidents: users, regulators and leadership
- `07-blameless-postmortems-for-ml.md` — Blameless postmortems for ML: recording causes that are statistical, not only technical
- `08-learning-from-incidents.md` — Learning from incidents: converting findings into monitors, tests and design changes
- `09-incident-databases-and-trend-analysis.md` — Incident databases and trend analysis

**Hands-on projects**

- **Project 1: ml incident simulator and triage playbook**  
  - Data: A model system with a library of injected faults  
  - Task: Build a simulator that produces incident symptoms and a playbook that leads responders to the cause, and time responders on it.  
  - Deliverables: Simulator, playbook and timing results.  
  - Pass gate: Mean time to diagnosis measured before and after the playbook.
- **Project 2: lineage based blast radius tool**  
  - Data: Lineage data from module 04  
  - Task: Given a bad dataset or model version, compute which downstream models, predictions and consumers were affected.  
  - Deliverables: Tool and validation.  
  - Pass gate: Output matches a manually traced example.
- **Project 3: postmortem library and trend analysis**  
  - Data: Public ML incident reports and your own simulated incidents  
  - Task: Write blameless postmortems, categorize causes and identify the top recurring failure classes.  
  - Deliverables: Postmortem collection and analysis.  
  - Pass gate: Categories defined before classification.

### 15 — LLM and Agent Observability and Online Evaluation

**Outcome:** Observe language-model systems whose outputs have no single correct answer. Application-level evaluation and the LLM observability dashboard are covered in G3, and trajectory replay in G4; this module covers the operational design.

**Lessons**

- `01-what-to-observe-in-llm-systems.md` — What to observe in LLM systems: prompts, context, outputs, tool calls, cost and latency
- `02-tracing-conventions-for-generative-systems-and-span-design.md` — Tracing conventions for generative systems and span design
- `03-online-quality-monitoring.md` — Online quality monitoring: user feedback, implicit signals and sampled judge scoring
- `04-calibrating-and-auditing-judges-in-production.md` — Calibrating and auditing judges in production
- `05-hallucination-refusal-and-safety-event-rates-as-monitored-metrics.md` — Hallucination, refusal and safety-event rates as monitored metrics
- `06-cost-and-latency-anomaly-detection.md` — Cost and latency anomaly detection
- `07-privacy-safe-logging-of-prompts-and-outputs.md` — Privacy-safe logging of prompts and outputs
- `08-closing-the-loop.md` — Closing the loop: turning production failures into evaluation cases
- `09-alerting-on-quality-with-noisy-metrics.md` — Alerting on quality with noisy metrics

**Hands-on projects**

- **Project 1: production quality monitor with judge audit**  
  - Data: Traces from an LLM application of yours or a simulated one  
  - Task: Build sampled judge scoring with periodic human audits and alerting, and test on injected quality regressions.  
  - Deliverables: Monitor, audit procedure and regression tests.  
  - Pass gate: Judge agreement with human audit tracked over time.
- **Project 2: failure to eval case pipeline**  
  - Data: Logged failures from the monitor  
  - Task: Automatically convert failures into labeled evaluation cases with review and track growth of coverage.  
  - Deliverables: Pipeline and coverage metrics.  
  - Pass gate: New cases reviewed by a human before entering the suite.
- **Project 3: privacy safe llm logging**  
  - Data: Conversations containing synthetic personal data  
  - Task: Build redaction and retention controls for logs and measure leakage of personal data.  
  - Deliverables: Controls and leakage test.  
  - Pass gate: Zero planted identifiers survive in stored logs.

### 16 — Reliability of Learning Loops and Safe Retraining

**Outcome:** Keep systems that learn from their own outputs from degrading. Retraining triggers, champion validation and feedback loops are covered in Stage 5D; this module covers failures of the loop itself.

**Lessons**

- `01-feedback-loop-failures.md` — Feedback-loop failures: self-reinforcing predictions, selection bias and narrowing exposure
- `02-poisoned-and-low-quality-feedback-data.md` — Poisoned and low-quality feedback data: detection and quarantine
- `03-retraining-guardrails.md` — Retraining guardrails: data checks, evaluation gates and staged promotion
- `04-evaluation-drift.md` — Evaluation drift: when the test set stops representing production
- `05-safe-exploration-data-collection-to-break-feedback-loops.md` — Safe exploration data collection to break feedback loops
- `06-rollback-of-learned-systems.md` — Rollback of learned systems: state, data and model versions together
- `07-monitoring-the-loop.md` — Monitoring the loop: stability of metrics across retrains
- `08-human-oversight-of-automatic-retraining.md` — Human oversight of automatic retraining

**Hands-on projects**

- **Project 1: feedback loop degradation simulation**  
  - Data: A simulated recommender or risk system retrained repeatedly  
  - Task: Show degradation from a feedback loop and compare mitigations such as randomized exploration and holdout data.  
  - Deliverables: Simulation and mitigation analysis.  
  - Pass gate: Many simulation runs with intervals.
- **Project 2: poisoned feedback detection**  
  - Data: A retraining pipeline with injected bad feedback  
  - Task: Detect and quarantine bad feedback batches before retraining and measure damage avoided.  
  - Deliverables: Detector and impact analysis.  
  - Pass gate: Injected bad batches are quarantined at a measured rate.
- **Project 3: safe retraining pipeline with staged promotion**  
  - Data: A model with periodic retraining  
  - Task: Add gates, shadow comparison and staged promotion and test with a deliberately bad retrain.  
  - Deliverables: Pipeline and fault tests.  
  - Pass gate: A bad retrain never reaches full traffic in tests.

### 17 — MLOps Operating Practices Teams Costs and Maturity

**Outcome:** Run the people and economics side of MLOps and reliability. Team structure and delivery practice are covered at a general level in Stage 2E; this module is specific to ML.

**Lessons**

- `01-ownership-and-on-call-for-models.md` — Ownership and on-call for models: who gets paged and for what
- `02-delivery-metrics-for-ml-teams.md` — Delivery metrics for ML teams: lead time, deployment frequency, change-failure rate and time to restore
- `03-cost-governance-for-ml.md` — Cost governance for ML: unit economics of training and serving and budget guardrails
- `04-technical-debt-in-ml-systems.md` — Technical debt in ML systems: identifying and prioritizing it
- `05-migration-from-ad-hoc-to-platform-based-workflows.md` — Migration from ad-hoc to platform-based workflows: sequencing and change management
- `06-vendor-selection-and-contract-risks-for-ml-tools.md` — Vendor selection and contract risks for ML tools
- `07-documentation-onboarding-and-knowledge-transfer.md` — Documentation, onboarding and knowledge transfer
- `08-metrics-that-matter.md` — Metrics that matter: a small scorecard for platform and reliability health
- `09-career-paths-and-skills-for-mlops-and-ml-reliability-engineers.md` — Career paths and skills for MLOps and ML reliability engineers

**Hands-on projects**

- **Project 1: mlops maturity assessment and roadmap**  
  - Data: A real or hypothetical ML organization  
  - Task: Assess maturity across delivery, platform, monitoring and governance and write a sequenced roadmap with cost and benefit estimates.  
  - Deliverables: Assessment and roadmap.  
  - Pass gate: Every recommendation tied to evidence and a measurable target.
- **Project 2: ml delivery metrics dashboard**  
  - Data: Repository and deployment history from your projects  
  - Task: Compute delivery and reliability metrics for ML work and interpret them.  
  - Deliverables: Dashboard and interpretation.  
  - Pass gate: Metric definitions written before computing.
- **Project 3: technical debt register and prioritization**  
  - Data: An ML system with known shortcuts  
  - Task: Catalog debt items, estimate cost of delay and rank them.  
  - Deliverables: Register and ranking.  
  - Pass gate: Cost estimates stated with assumptions.

### 18 — G11 Capstones

**Outcome:** integrate the platform and reliability tracks in assessed, portfolio-quality work.

- **Capstone 1: internal ml platform mvp** (uses Modules 01 to 09)  
  Build a minimum viable ML platform with a golden path, an ML-native orchestrator, feature and metadata services, a serving gateway with automated canaries, signed promotion and infrastructure as code, and measure its adoption with test users.
- **Capstone 2: ml observability and reliability program** (uses Modules 10 to 14, 16)  
  Design and implement the observability, SLO, alerting, chaos-testing and incident-response program for a production model, validated on replayed and injected incidents.
- **Capstone 3: llmops platform extension** (uses Modules 08, 15)  
  Extend the platform with prompt and evaluation registries, spend governance, tracing, online quality monitoring and privacy-safe logging for two language-model applications.
- **Capstone 4: mlops operating model and roadmap** (uses Modules 01, 17)  
  Produce an operating model, maturity assessment and costed roadmap for an ML organization, defended in a mock review.
- **Capstone 5: g11 readiness assessment** (uses All modules)  
  Written and practical assessment against the G11 completion gate.

## G11 completion gate

- Every platform component is tested with injected faults and has a documented recovery path, and every platform claim (adoption, lead time, cost) is measured.
- Every monitor, alert and SLO is validated by replaying historical or injected incidents, reporting detection delay, false-alarm rate and incident recall.
- Every platform feature has at least one user outside the builder who completed a task with it, with timing recorded.
- Every promotion path enforces provenance, signing and policy checks, demonstrated with tampered and unapproved artifacts.
- Every tool adopted has licence, maintenance status and exit cost recorded in the register before adoption.
- Every cost figure is measured or sourced with date, and spending caps were set before cloud projects ran.
- All results reproduce from infrastructure code, configs and logged seeds, with versions recorded.
- At least one negative or inconclusive result per track is reported honestly, including a case where a simpler approach beat the platform feature.
- The four specialist capstones are complete and the readiness assessment is passed.

## Audit and verification

**What was checked and the result**

- Structure: 17 specialist modules each have 6 to 12 lessons and at least one project; the tree contains 254 files and 37 folders, and these counts equal the counts computed from the curriculum data.
- Overlap with the Roadmap: all 153 lesson file names were compared against every lesson file name in `Roadmap.md`. Exact matches: 0. Near matches (similarity 0.80 or higher): 1 — `dataset-registry-and-versioning` vs Roadmap `model-registry-and-versioning` (0.87). Reviewed manually: the G11 lesson covers dataset registries and dataset version tools at platform level, while the Stage 5D lesson covers model registry and versioning in MLflow; the Stage 5D data-versioning basics lesson is referenced, not repeated.
- Structural problems found by the build script: 0.
- Topic-level overlap check and the corrections it forced: the Roadmap text was searched for Kubeflow, Flyte, Metaflow, ZenML, Feast, Tecton, whylogs, Arize, Langfuse, Unity Catalog, DataHub, Seldon, Ray Serve, Sigstore, cosign, golden paths and ML platform. None appear as lessons. The same search found existing lessons the first draft of this plan had overlooked: Dagster software-defined assets and Prefect flows (Stage 2C), Argo CD and Argo Rollouts and Flagger traffic analysis (Stage 2E), SBOM and license compliance and SLSA build provenance, chaos engineering with Litmus and Chaos Mesh (Stage 2E), and Backstage developer portals (Stage 2E). The affected lessons in modules 01, 02, 06, 07 and 13 were rewritten to extend those lessons, not repeat them, and the scope table names each one. Stage 5D itself contains 17 modules covering the practitioner-level MLOps this group would otherwise have repeated, which is why G11 is framed as platform engineering and reliability engineering.
- Verified by web search on the build date (2026-10-26): OpenSSF, Google and Sigstore created the OpenSSF Model Signing specification, with reference CLI and library, supporting keyless and key-based signing, and its Python package was still labelled alpha at version 1.1.1 in October 2025; Kubeflow, Flyte, Metaflow and ZenML are active ML orchestration options in 2026 comparisons, mostly from vendor or community blogs; the whylogs library is Apache-2.0 with its latest release found dated December 2024.
- Reported but not confirmed: the current maintenance status of NannyML, Evidently, whylogs and WhyLabs, Feast and other feature stores was not confirmed (the last whylogs activity found is old); one competitor blog claims a pending acquisition of Dagster Labs, which was not verified and is not relied on; the status of CycloneDX ML-BOM, the OpenTelemetry generative-AI semantic conventions, MLflow's generative-AI features and the CNCF status of the orchestrators was not confirmed; the multi-window, multi-burn-rate alerting method and the ML automation maturity levels are cited from established SRE and MLOps literature and were not re-checked here.
- Not verified: tool versions and licences, which change quickly; vendor and managed-service capabilities and prices; and any claim from vendor marketing material.
- Not verified by execution: no code in this plan has been run. Project pass gates are acceptance criteria to be met when the projects are built.
- Safety note: fault-injection and chaos projects must run only in staging or sandbox environments you own, with abort conditions and blast-radius limits, and cloud projects must have spending caps and alerts before they start.
- Repository safety: this build created only this file; no existing file or folder was created, changed or deleted by it.
