# Data and Evaluation — ML Specialization Roadmap

**Group 13 (G13)** of the specialization that follows Stage 5D of the [Roadmap](./Roadmap.md). It covers original categories **38 Synthetic Data and Data-Centric AI and 39 AI Evaluation and Benchmarking Engineering**. The group's defining question is: *how good are the data and the measurements?* It follows G1 to G12: [`01_Classical and Applied ML.md`](./01_Classical%20and%20Applied%20ML.md), [`02_Deep Learning by Modality.md`](./02_Deep%20Learning%20by%20Modality.md), [`03_Generative and Foundation Models.md`](./03_Generative%20and%20Foundation%20Models.md), [`04_Agents and Sequential Decisions.md`](./04_Agents%20and%20Sequential%20Decisions.md), [`05_Time and Anomaly Modeling.md`](./05_Time%20and%20Anomaly%20Modeling.md), [`06_Personalization Search and Matching.md`](./06_Personalization%20Search%20and%20Matching.md), [`07_Statistical Reasoning.md`](./07_Statistical%20Reasoning.md), [`08_Graphs and Optimization.md`](./08_Graphs%20and%20Optimization.md), [`09_Industry Domain ML.md`](./09_Industry%20Domain%20ML.md), [`10_Efficient and Scalable Systems.md`](./10_Efficient%20and%20Scalable%20Systems.md), [`11_MLOps and Reliability.md`](./11_MLOps%20and%20Reliability.md), [`12_Trustworthy ML.md`](./12_Trustworthy%20ML.md).

**Important context:** earlier groups already teach evaluation and data work inside each topic (LLM application evaluation in G3, agent evaluation in G4, recommender evaluation in G6, anomaly-benchmark critique in G5, uncertainty evaluation in G7, labeling and annotation in G2). G13 does not repeat those. It teaches the shared science underneath: how to design valid evaluations, build and maintain benchmarks, compare models with honest statistics, and how to improve and generate data systematically.

## G13 summary

| Item | Count |
|---|---|
| Modules (including overview and capstones) | 16 |
| Lesson files | 128 |
| Hands-on project files (module projects, overview project and capstones) | 48 |
| Folders inside the G13 tree | 31 |
| Files inside the G13 tree | 214 |

| Original category | Modules |
|---|---|
| 38 Synthetic Data and Data-Centric AI | 01 to 06 |
| 39 AI Evaluation and Benchmarking Engineering | 07 to 14 |

## Scope and how G13 avoids repeating the Roadmap

These are **already learned** and are only referenced, never retaught. From **Stage 5A**: exploratory data analysis and data quality, label noise and data errors, data-centric versus model-centric improvement, ablation studies, error analysis and slices, train, validation and test splitting, and metric selection. From **Stage 5B**: pseudo-labeling, active learning query strategies, weak supervision and noisy labels, SMOTE limitations, nested validation, comparing models across folds and datasets, and calibration. From **Stage 4B**: confidence intervals, the bootstrap, hypothesis tests, effect size and power. From **Stages 2C and 5D**: synthetic and sampled test data for pipelines, benchmarking pipelines, property-based testing, and data and model behavior tests. From **earlier groups**: confident learning and label-quality audits (G1), annotation workflows, vision annotation and label audits and augmentation policies (G2), pretraining data filtering, LLM application evaluation, judge calibration and the principle of synthetic data from stronger models (G3), agent evaluation and synthetic agent environments (G4), anomaly-benchmark critique (G5), recommender evaluation rigor (G6), proper scoring rules and experimentation (G7), safety evaluation and red-teaming (G12), and the evaluation service of the ML platform (G11).

**Boundaries with other groups** (so nothing overlaps): privacy attacks and differential privacy theory belong to **G12** (module 05 applies them to synthetic data); the MLOps platform for evaluation services belongs to **G11**; domain validation (clinical, financial, spatial) belongs to **G9**; efficiency benchmarking belongs to **G10**.

| Roadmap topic already covered | Where G13 goes further |
|---|---|
| Error analysis, label noise and data-centric versus model-centric (5A), confident learning (G1) | Module 01: training-dynamics diagnostics, embedding-space diagnostics, coverage analysis and data requirement specification |
| Active learning query strategies (5B), pretraining data filtering (G3) | Module 02: data attribution and valuation, data pruning, batch active learning at scale and data-mixture optimization |
| Annotation workflows and agreement (G2), weak supervision (5B) | Module 03: labeling operations, aggregation models, disagreement modeling, LLM-assisted labeling and labeling ethics |
| Synthetic test data for pipelines (2C), SMOTE (5B) | Module 04: tabular, simulation, image and text synthesis, conditional generation and sim-to-real gaps |
| Membership inference and DP (G12) | Module 05: fidelity, utility and privacy evaluation of synthetic data, DP synthesis and model collapse |
| Synthetic data from stronger models (G3), agent environments (G4) | Module 06: verified synthetic-data pipelines, decontamination and synthetic evaluation-set validity |
| Metric selection and splits (5A), decision-focused evaluation (G1) | Module 07: construct validity, Goodhart effects, test-set reuse, power analysis and evaluation plans |
| Anomaly benchmark flaws (G5), recommender evaluation (G6) | Module 08: benchmark construction, saturation, contamination, leaderboard gaming and maintenance |
| Bootstrap and tests (4B), comparing models across folds (5B), LLM eval variance (G3) | Module 09: dependent-item tests, ranking uncertainty, Bradley-Terry, item response theory and aggregation |
| LLM judges for applications (G3), judge audits (G11) | Module 10: human evaluation design, rater reliability, arena biases and meta-evaluation of judges |
| LLM application evaluation (G3), safety evaluation (G12) | Module 11: general foundation-model evaluation, sensitivity, reproducibility, elicitation and Indic evaluation |
| Behavior tests (5D), property-based testing (2C) | Module 12: behavioral test suites, metamorphic relations, challenge sets and incident-derived regression tests |
| Evaluation gates in CI (G3), evaluation service (G11) | Module 13: harness architecture, determinism, adaptive cost reduction, sandboxing and integrity tests |
| Model cards (5D), system cards (G12) | Module 14: evaluation reporting, independent evaluation, replication and the Indian benchmark ecosystem |

## G13 — Data and Evaluation

**Defining question:** How good are the data and the measurements?

```text
ML Specialization/
└── G13 — Data and Evaluation/
    ├── 00-G13-Overview/
    │   ├── Projects/
    │   │   ├── 01-g13-data-versioning-and-evaluation-harness-bootstrap.md
    │   │   └── README.md
    │   ├── 01-g13-scope-and-boundaries-with-stages-2c-5a-5b-and-other-groups.md
    │   ├── 02-prerequisite-map-from-the-roadmap.md
    │   ├── 03-dataset-and-tooling-register.md
    │   ├── 04-evaluation-and-reporting-standards.md
    │   ├── 05-completion-gate.md
    │   ├── README.md
    │   └── learning-plan.md
    ├── 01-Data-Centric-AI-Workflow-and-Dataset-Diagnostics/
    │   ├── Projects/
    │   │   ├── 01-dataset-cartography-and-label-issue-discovery.md
    │   │   ├── 02-coverage-gap-analysis-and-targeted-collection.md
    │   │   ├── 03-data-requirements-document.md
    │   │   └── README.md
    │   ├── 01-the-data-centric-iteration-loop.md
    │   ├── 02-training-dynamics-diagnostics.md
    │   ├── 03-embedding-space-diagnostics.md
    │   ├── 04-coverage-analysis.md
    │   ├── 05-data-requirement-specification.md
    │   ├── 06-estimating-how-much-more-data-will-help.md
    │   ├── 07-label-taxonomy-design-and-evolution.md
    │   ├── 08-data-debt.md
    │   ├── 09-measuring-the-effect-of-a-data-fix.md
    │   └── README.md
    ├── 02-Data-Valuation-Attribution-Selection-and-Mixtures/
    │   ├── Projects/
    │   │   ├── 01-data-valuation-and-pruning-study.md
    │   │   ├── 02-batch-active-learning-benchmark.md
    │   │   ├── 03-instruction-data-selection-experiment.md
    │   │   └── README.md
    │   ├── 01-data-attribution.md
    │   ├── 02-data-valuation.md
    │   ├── 03-data-pruning-and-coreset-selection.md
    │   ├── 04-curriculum-and-ordering.md
    │   ├── 05-active-learning-at-scale.md
    │   ├── 06-data-mixture-optimization.md
    │   ├── 07-selecting-high-quality-instruction-and-fine-tuning-data-for-language-models.md
    │   ├── 08-dataset-distillation-and-compression-overview.md
    │   ├── 09-evaluating-data-selection-methods.md
    │   └── README.md
    ├── 03-Labeling-Operations-Annotation-Quality-and-Human-Feedback/
    │   ├── Projects/
    │   │   ├── 01-annotator-aggregation-comparison.md
    │   │   ├── 02-llm-assisted-labeling-audit.md
    │   │   ├── 03-labeling-operations-playbook.md
    │   │   └── README.md
    │   ├── 01-labeling-as-a-system.md
    │   ├── 02-quality-control.md
    │   ├── 03-aggregation-models.md
    │   ├── 04-agreement-statistics.md
    │   ├── 05-disagreement-as-signal.md
    │   ├── 06-annotation-budget-allocation.md
    │   ├── 07-llm-assisted-labeling.md
    │   ├── 08-collecting-preference-and-feedback-data-for-language-models.md
    │   ├── 09-ethics-and-labor.md
    │   ├── 10-privacy-and-security-in-labeling-pipelines.md
    │   └── README.md
    ├── 04-Synthetic-Data-Generation-Methods-and-Augmentation/
    │   ├── Projects/
    │   │   ├── 01-tabular-synthesis-method-comparison.md
    │   │   ├── 02-rare-class-synthesis-vs-resampling.md
    │   │   ├── 03-sim-to-real-gap-study.md
    │   │   └── README.md
    │   ├── 01-why-generate-data.md
    │   ├── 02-tabular-synthesis.md
    │   ├── 03-simulation-based-data.md
    │   ├── 04-image-synthesis-for-training.md
    │   ├── 05-text-synthesis.md
    │   ├── 06-conditional-generation-for-rare-classes-and-edge-cases.md
    │   ├── 07-augmentation-versus-synthesis.md
    │   ├── 08-time-series-and-graph-synthesis-with-pointers-to-g5-and-g8.md
    │   ├── 09-sim-to-real-gaps.md
    │   └── README.md
    ├── 05-Synthetic-Data-Evaluation-Fidelity-Utility-and-Privacy/
    │   ├── Projects/
    │   │   ├── 01-synthetic-data-quality-report-card.md
    │   │   ├── 02-dp-synthetic-data-utility-privacy-frontier.md
    │   │   ├── 03-recursive-training-collapse-experiment.md
    │   │   └── README.md
    │   ├── 01-three-axes-of-quality.md
    │   ├── 02-fidelity-metrics.md
    │   ├── 03-utility-metrics.md
    │   ├── 04-privacy-metrics.md
    │   ├── 05-differentially-private-synthetic-data.md
    │   ├── 06-validity-and-constraints.md
    │   ├── 07-bias-amplification-and-fairness-effects-of-synthesis.md
    │   ├── 08-model-collapse.md
    │   ├── 09-disclosure-documentation-and-legal-status-of-synthetic-data.md
    │   └── README.md
    ├── 06-Synthetic-Data-Pipelines-for-Language-Models-and-Agents/
    │   ├── Projects/
    │   │   ├── 01-verified-synthetic-math-and-code-data-pipeline.md
    │   │   ├── 02-diversity-and-quality-of-instruction-data.md
    │   │   ├── 03-synthetic-eval-set-validity-study.md
    │   │   └── README.md
    │   ├── 01-pipeline-design.md
    │   ├── 02-verification-as-the-quality-gate.md
    │   ├── 03-diversity-measurement-and-control-in-generated-data.md
    │   ├── 04-judge-based-filtering-and-its-biases.md
    │   ├── 05-decontamination.md
    │   ├── 06-synthetic-evaluation-sets.md
    │   ├── 07-synthetic-tasks-and-environments-for-agents-with-automatic-verifiers.md
    │   ├── 08-terms-of-use-licensing-and-provenance-of-generated-data.md
    │   ├── 09-cost-and-scaling-of-generation-pipelines.md
    │   └── README.md
    ├── 07-Evaluation-Design-Validity-and-Test-Set-Engineering/
    │   ├── Projects/
    │   │   ├── 01-construct-validity-audit-of-a-metric.md
    │   │   ├── 02-test-set-reuse-simulation.md
    │   │   ├── 03-evaluation-plan-and-power-analysis.md
    │   │   └── README.md
    │   ├── 01-evaluation-as-measurement.md
    │   ├── 02-from-goals-to-capabilities.md
    │   ├── 03-metric-design-and-goodhart-effects.md
    │   ├── 04-test-set-design.md
    │   ├── 05-test-set-reuse-and-adaptive-overfitting.md
    │   ├── 06-temporal-and-distributional-validity.md
    │   ├── 07-power-analysis-for-evaluation.md
    │   ├── 08-evaluation-plans.md
    │   ├── 09-linking-evaluation-to-decisions.md
    │   └── README.md
    ├── 08-Benchmark-Construction-Maintenance-and-Contamination/
    │   ├── Projects/
    │   │   ├── 01-benchmark-shortcut-and-artifact-audit.md
    │   │   ├── 02-contamination-detection-study.md
    │   │   ├── 03-build-a-small-benchmark-end-to-end.md
    │   │   └── README.md
    │   ├── 01-benchmark-purpose-and-scope.md
    │   ├── 02-data-sourcing-annotation-and-quality-assurance-for-benchmark-items.md
    │   ├── 03-splits-and-secrecy.md
    │   ├── 04-difficulty-calibration-and-the-lifecycle-of-a-benchmark.md
    │   ├── 05-contamination.md
    │   ├── 06-dynamic-and-time-based-benchmarks-as-contamination-defenses.md
    │   ├── 07-leaderboard-design-and-gaming.md
    │   ├── 08-shortcuts-and-artifacts-in-benchmark-data.md
    │   ├── 09-benchmark-documentation-versioning-licensing-and-maintenance.md
    │   └── README.md
    ├── 09-Statistical-Methods-for-Model-Comparison/
    │   ├── Projects/
    │   │   ├── 01-comparison-test-calibration-by-simulation.md
    │   │   ├── 02-ranking-uncertainty-with-bradley-terry.md
    │   │   ├── 03-irt-shortened-benchmark.md
    │   │   └── README.md
    │   ├── 01-paired-comparison-tests.md
    │   ├── 02-dependent-test-items.md
    │   ├── 03-multiple-comparisons-across-many-models-metrics-and-benchmarks.md
    │   ├── 04-uncertainty-in-rankings.md
    │   ├── 05-pairwise-preference-models.md
    │   ├── 06-item-response-theory-for-evaluation.md
    │   ├── 07-accounting-for-hyperparameter-budgets-and-seeds-when-reporting.md
    │   ├── 08-equivalence-testing-and-minimum-detectable-differences.md
    │   ├── 09-aggregating-across-tasks.md
    │   ├── 10-meta-analysis-of-evaluation-results-across-studies.md
    │   └── README.md
    ├── 10-Human-Evaluation-LLM-Judges-and-Meta-Evaluation/
    │   ├── Projects/
    │   │   ├── 01-human-eval-study-with-reliability-analysis.md
    │   │   ├── 02-judge-bias-quantification.md
    │   │   ├── 03-meta-evaluation-of-judges.md
    │   │   └── README.md
    │   ├── 01-human-evaluation-design.md
    │   ├── 02-rater-recruitment-training-and-reliability.md
    │   ├── 03-converting-judgments-into-scores.md
    │   ├── 04-crowdsourced-arena-evaluation.md
    │   ├── 05-expert-versus-crowd-raters-and-when-each-is-needed.md
    │   ├── 06-cultural-and-language-effects-on-judgments-including-indic-language-raters.md
    │   ├── 07-judge-models.md
    │   ├── 08-meta-evaluation.md
    │   ├── 09-ethics-of-human-evaluation.md
    │   └── README.md
    ├── 11-Evaluating-Foundation-Models/
    │   ├── Projects/
    │   │   ├── 01-prompt-and-format-sensitivity-study.md
    │   │   ├── 02-reproducing-published-evaluation-numbers.md
    │   │   ├── 03-indic-language-evaluation-suite.md
    │   │   └── README.md
    │   ├── 01-capability-taxonomies-and-the-main-evaluation-families-for-language-models.md
    │   ├── 02-evaluation-ecosystems.md
    │   ├── 03-sensitivity-to-prompt-format-few-shot-examples-and-decoding-settings.md
    │   ├── 04-reproducibility.md
    │   ├── 05-capability-elicitation.md
    │   ├── 06-evaluating-reasoning-long-context-and-tool-use-with-verifiable-and-unverifiable-tasks.md
    │   ├── 07-robustness-and-distribution-shift-evaluation.md
    │   ├── 08-multilingual-and-indic-language-evaluation.md
    │   ├── 09-multimodal-evaluation.md
    │   └── README.md
    ├── 12-Behavioral-Testing-and-Stress-Evaluation/
    │   ├── Projects/
    │   │   ├── 01-checklist-style-suite-for-a-task.md
    │   │   ├── 02-metamorphic-relations-catalog.md
    │   │   ├── 03-incident-to-regression-test-pipeline.md
    │   │   └── README.md
    │   ├── 01-behavioral-testing-frameworks.md
    │   ├── 02-metamorphic-testing.md
    │   ├── 03-challenge-sets-and-adversarially-collected-data.md
    │   ├── 04-template-and-automated-test-generation-with-validation-of-the-generated-cases.md
    │   ├── 05-slice-based-and-disaggregated-evaluation-reports.md
    │   ├── 06-stress-tests-for-rare-events-and-the-long-tail.md
    │   ├── 07-simulation-based-scenario-evaluation-for-safety-relevant-systems.md
    │   ├── 08-turning-incidents-into-permanent-regression-tests.md
    │   ├── 09-coverage-criteria-for-test-suites.md
    │   └── README.md
    ├── 13-Evaluation-Harness-Engineering-and-Platforms/
    │   ├── Projects/
    │   │   ├── 01-evaluation-harness-from-scratch.md
    │   │   ├── 02-adaptive-evaluation-cost-reduction.md
    │   │   ├── 03-harness-leakage-and-integrity-tests.md
    │   │   └── README.md
    │   ├── 01-harness-architecture.md
    │   ├── 02-determinism-and-reproducibility.md
    │   ├── 03-parallelism-retries-and-rate-limits-for-model-based-evaluation.md
    │   ├── 04-cost-control.md
    │   ├── 05-sandboxed-execution-for-code-and-tool-using-evaluations.md
    │   ├── 06-evaluation-registries-versioning-and-provenance-of-results.md
    │   ├── 07-analysis-and-dashboards.md
    │   ├── 08-open-harnesses-and-frameworks-including-inspect-and-lm-evaluation-harness-with-maintenance-and-licence-checks.md
    │   ├── 09-protecting-private-evaluation-data-and-preventing-leakage-through-the-harness.md
    │   └── README.md
    ├── 14-Evaluation-Practice-Reporting-and-Ecosystem/
    │   ├── Projects/
    │   │   ├── 01-independent-evaluation-report.md
    │   │   ├── 02-replication-of-an-evaluation-paper.md
    │   │   ├── 03-indic-benchmark-gap-analysis.md
    │   │   └── README.md
    │   ├── 01-writing-evaluation-reports.md
    │   ├── 02-pre-registered-and-replicated-evaluations.md
    │   ├── 03-independent-and-third-party-evaluation.md
    │   ├── 04-evaluation-in-procurement-and-regulation.md
    │   ├── 05-organizing-an-evaluation-function.md
    │   ├── 06-ethics-of-evaluation-research.md
    │   ├── 07-indian-ecosystem.md
    │   ├── 08-evaluation-research-frontiers-and-open-problems.md
    │   ├── 09-portfolio-and-career.md
    │   └── README.md
    ├── 15-G13-Capstones/
    │   ├── 01-data-centric-improvement-campaign.md
    │   ├── 02-synthetic-data-program-with-quality-gates.md
    │   ├── 03-benchmark-and-evaluation-suite-for-a-task.md
    │   ├── 04-foundation-model-evaluation-study.md
    │   ├── 05-g13-readiness-assessment.md
    │   └── README.md
    └── README.md
```

### 00 — G13 Overview

**Purpose:** the single authoritative plan for G13 with scope, boundaries, prerequisite map, dataset and tooling register, evaluation and reporting standards and completion gate.

- `01-g13-scope-and-boundaries-with-stages-2c-5a-5b-and-other-groups.md` — what G13 teaches and what it leaves to other stages and groups.
- `02-prerequisite-map-from-the-roadmap.md` — Roadmap lessons assumed for each G13 module, named precisely.
- `03-dataset-and-tooling-register.md` — every dataset with licence and access conditions, and every library or harness with version, licence and maintenance status.
- `04-evaluation-and-reporting-standards.md` — evaluation-plan template, uncertainty reporting, comparison-test rules and the report template used by all projects.
- `05-completion-gate.md` — measurable criteria to finish G13.
- `learning-plan.md` — recommended order and two tracks (data and evaluation).

**Project 1: g13 data versioning and evaluation harness bootstrap**  
- Data: a small dataset and two small models.  
- Task: build a reproducible workspace with pinned tooling, dataset versioning, a minimal evaluation harness with paired-bootstrap comparison and a registered evaluation-plan template.  
- Deliverables: lockfile, harness with tests and the plan template.  
- Pass gate: a clean machine reproduces the tests from the lockfile, and the harness reports a difference as not significant when two identical models are compared.

### 01 — Data Centric AI Workflow and Dataset Diagnostics

**Outcome:** Improve models by improving data, using systematic diagnostics rather than ad-hoc cleaning. Error analysis, label noise and data errors, the data-centric versus model-centric comparison and ablation studies are covered in Stage 5A; confident learning and label-quality audits in G1; none are repeated.

**Lessons**

- `01-the-data-centric-iteration-loop.md` — The data-centric iteration loop: diagnose, fix data, retrain, measure and decide when to stop
- `02-training-dynamics-diagnostics.md` — Training-dynamics diagnostics: dataset cartography and learning-speed maps to find ambiguous and mislabeled examples
- `03-embedding-space-diagnostics.md` — Embedding-space diagnostics: clusters, outliers and near-duplicates at scale
- `04-coverage-analysis.md` — Coverage analysis: which situations are missing from the data and how to find them
- `05-data-requirement-specification.md` — Data requirement specification: writing down what data a task needs before collecting it
- `06-estimating-how-much-more-data-will-help.md` — Estimating how much more data will help: learning curves and value-of-data forecasts
- `07-label-taxonomy-design-and-evolution.md` — Label taxonomy design and evolution: splitting, merging and versioning classes
- `08-data-debt.md` — Data debt: tracking known data problems and their cost
- `09-measuring-the-effect-of-a-data-fix.md` — Measuring the effect of a data fix: controlled comparisons with seed variance

**Hands-on projects**

- **Project 1: dataset cartography and label issue discovery**  
  - Data: A public image or text classification dataset with known label problems, such as CIFAR-10 or a sentiment dataset  
  - Task: Use training-dynamics maps to find ambiguous and suspect examples, review a sample by hand and measure the gain from fixing them.  
  - Deliverables: Diagnostic notebook, reviewed sample and before-and-after results.  
  - Pass gate: Fix effect measured with several seeds and a held-out set untouched by cleaning.
- **Project 2: coverage gap analysis and targeted collection**  
  - Data: A classification dataset with metadata or an embedding model to define situations  
  - Task: Find under-covered situations, collect or select targeted additional data and compare with random additional data of equal size.  
  - Deliverables: Gap analysis and comparison.  
  - Pass gate: Equal data budgets for targeted and random additions.
- **Project 3: data requirements document**  
  - Data: A task of your choice  
  - Task: Write a data requirements specification and test its assumptions with a small pilot dataset and a learning curve.  
  - Deliverables: Specification and pilot results.  
  - Pass gate: Every requirement has a stated way to verify it.

### 02 — Data Valuation Attribution Selection and Mixtures

**Outcome:** Decide which data points and which data sources matter. Active learning query strategies are covered in Stage 5B and data deduplication and filtering for language-model pretraining in G3.

**Lessons**

- `01-data-attribution.md` — Data attribution: leave-one-out, influence functions and trajectory-based methods
- `02-data-valuation.md` — Data valuation: Shapley-style values and efficient approximations
- `03-data-pruning-and-coreset-selection.md` — Data pruning and coreset selection: how much data can be removed without losing accuracy
- `04-curriculum-and-ordering.md` — Curriculum and ordering: when example order helps
- `05-active-learning-at-scale.md` — Active learning at scale: batch selection, diversity and cost-aware labeling, and the pitfalls of evaluating it
- `06-data-mixture-optimization.md` — Data-mixture optimization: weighting sources and domains for training
- `07-selecting-high-quality-instruction-and-fine-tuning-data-for-language-models.md` — Selecting high-quality instruction and fine-tuning data for language models
- `08-dataset-distillation-and-compression-overview.md` — Dataset distillation and compression overview
- `09-evaluating-data-selection-methods.md` — Evaluating data-selection methods: strong random baselines and compute-matched comparisons

**Hands-on projects**

- **Project 1: data valuation and pruning study**  
  - Data: CIFAR-10 and a tabular dataset with injected harmful examples  
  - Task: Compare influence, Shapley-style and loss-based scores on finding harmful examples and on pruning, against random pruning.  
  - Deliverables: Comparison with intervals.  
  - Pass gate: Random pruning baseline included at every pruning level.
- **Project 2: batch active learning benchmark**  
  - Data: A text or image dataset with an unlabeled pool  
  - Task: Compare uncertainty, diversity and hybrid batch strategies against random sampling under equal labeling budgets with several seeds.  
  - Deliverables: Learning curves.  
  - Pass gate: Gains reported only if they exceed seed variance.
- **Project 3: instruction data selection experiment**  
  - Data: A public instruction dataset and a small open model  
  - Task: Fine-tune on selected subsets chosen by quality and diversity heuristics and compare with random subsets of equal size.  
  - Deliverables: Comparison on held-out tasks.  
  - Pass gate: Same training budget for every subset.

### 03 — Labeling Operations Annotation Quality and Human Feedback

**Outcome:** Run labeling as an engineered, ethical operation. Annotation workflows, guidelines, agreement and adjudication for text are introduced in G2, vision annotation formats and label audits in G2, and weak supervision and noisy labels in Stage 5B.

**Lessons**

- `01-labeling-as-a-system.md` — Labeling as a system: task decomposition, instruction design and iteration on guidelines
- `02-quality-control.md` — Quality control: gold questions, qualification, redundancy and spot checks
- `03-aggregation-models.md` — Aggregation models: majority vote versus probabilistic annotator models such as Dawid-Skene
- `04-agreement-statistics.md` — Agreement statistics: kappa and Krippendorff's alpha, their assumptions and misuse
- `05-disagreement-as-signal.md` — Disagreement as signal: modeling ambiguity instead of forcing one label
- `06-annotation-budget-allocation.md` — Annotation budget allocation: where to spend labeling money
- `07-llm-assisted-labeling.md` — LLM-assisted labeling: quality, bias and calibration against human labels
- `08-collecting-preference-and-feedback-data-for-language-models.md` — Collecting preference and feedback data for language models
- `09-ethics-and-labor.md` — Ethics and labor: fair pay, working conditions, exposure to harmful content and vendor oversight
- `10-privacy-and-security-in-labeling-pipelines.md` — Privacy and security in labeling pipelines

**Hands-on projects**

- **Project 1: annotator aggregation comparison**  
  - Data: A crowdsourced labeling dataset with multiple labels per item, plus simulated annotators with known accuracy  
  - Task: Compare majority vote with Dawid-Skene-style models on label accuracy and recovery of annotator quality.  
  - Deliverables: Comparison with simulated ground truth.  
  - Pass gate: Ground truth known in simulation and held out on real data.
- **Project 2: llm assisted labeling audit**  
  - Data: A labeling task with a human gold set of at least 300 items  
  - Task: Compare human, LLM and hybrid labeling on accuracy, cost and bias by subgroup.  
  - Deliverables: Audit report.  
  - Pass gate: Hybrid design validated on items not used to design it.
- **Project 3: labeling operations playbook**  
  - Data: A hypothetical labeling project  
  - Task: Write the instructions, quality plan, pay and welfare policy and escalation rules, and test the instructions with pilot annotators.  
  - Deliverables: Playbook and pilot results.  
  - Pass gate: Instructions revised from measured disagreement.

### 04 — Synthetic Data Generation Methods and Augmentation

**Outcome:** Generate training and test data across modalities and know when generation helps. Synthetic test data for pipelines is covered in Stage 2C and SMOTE limitations in Stage 5B; vision augmentation policies are covered in G2.

**Lessons**

- `01-why-generate-data.md` — Why generate data: scarcity, privacy, balance, coverage and testing
- `02-tabular-synthesis.md` — Tabular synthesis: copula, GAN, VAE, diffusion and language-model approaches with the SDV and synthcity libraries
- `03-simulation-based-data.md` — Simulation-based data: rule-based generators, simulators and procedural generation
- `04-image-synthesis-for-training.md` — Image synthesis for training: generative models from G3, rendering and domain randomization
- `05-text-synthesis.md` — Text synthesis: prompt-based, persona-based and evolved instruction data and their diversity limits
- `06-conditional-generation-for-rare-classes-and-edge-cases.md` — Conditional generation for rare classes and edge cases
- `07-augmentation-versus-synthesis.md` — Augmentation versus synthesis: where the boundary lies and how each changes the data distribution
- `08-time-series-and-graph-synthesis-with-pointers-to-g5-and-g8.md` — Time-series and graph synthesis with pointers to G5 and G8
- `09-sim-to-real-gaps.md` — Sim-to-real gaps: measuring and closing them

**Hands-on projects**

- **Project 1: tabular synthesis method comparison**  
  - Data: Three public tabular datasets  
  - Task: Compare several tabular generators on downstream utility, fidelity and training cost.  
  - Deliverables: Comparison with intervals.  
  - Pass gate: Real held-out test data never used in generator training.
- **Project 2: rare class synthesis vs resampling**  
  - Data: An imbalanced dataset  
  - Task: Compare synthetic oversampling with generators, SMOTE variants and cost-sensitive training.  
  - Deliverables: Comparison at several imbalance levels.  
  - Pass gate: Synthesis done inside training folds only.
- **Project 3: sim to real gap study**  
  - Data: A task with a simulator or renderer you can run and a small real dataset  
  - Task: Train on simulated data, test on real data and measure how domain randomization and small real fine-tuning sets close the gap.  
  - Deliverables: Gap curves.  
  - Pass gate: Real data used only for evaluation and stated fine-tuning amounts.

### 05 — Synthetic Data Evaluation Fidelity Utility and Privacy

**Outcome:** Judge whether synthetic data is good, useful and safe. Membership inference and privacy auditing are taught in G12 and differential privacy foundations in G12; this module applies them to synthetic data.

**Lessons**

- `01-three-axes-of-quality.md` — Three axes of quality: fidelity, utility and privacy, and why they trade off
- `02-fidelity-metrics.md` — Fidelity metrics: marginal and joint distribution checks and classifier two-sample tests
- `03-utility-metrics.md` — Utility metrics: train-on-synthetic test-on-real and ranking preservation of models
- `04-privacy-metrics.md` — Privacy metrics: closest-record distance, membership and attribute-inference attacks
- `05-differentially-private-synthetic-data.md` — Differentially private synthetic data: marginal-based and generator-based methods
- `06-validity-and-constraints.md` — Validity and constraints: logical rules, referential integrity and impossible records
- `07-bias-amplification-and-fairness-effects-of-synthesis.md` — Bias amplification and fairness effects of synthesis
- `08-model-collapse.md` — Model collapse: recursive training on generated data and mixing with real data
- `09-disclosure-documentation-and-legal-status-of-synthetic-data.md` — Disclosure, documentation and legal status of synthetic data

**Hands-on projects**

- **Project 1: synthetic data quality report card**  
  - Data: Synthetic data from module 04  
  - Task: Build an evaluation report covering fidelity, utility, privacy and validity with intervals and a recommended use.  
  - Deliverables: Report-card tooling and reports.  
  - Pass gate: Privacy assessed with attacks, not distance alone.
- **Project 2: dp synthetic data utility privacy frontier**  
  - Data: A tabular dataset  
  - Task: Generate differentially private synthetic data at several budgets and plot the utility-privacy frontier with attacks.  
  - Deliverables: Frontier plots.  
  - Pass gate: Accounting method and parameters recorded.
- **Project 3: recursive training collapse experiment**  
  - Data: A small generative model on a simple dataset  
  - Task: Train repeatedly on generated data with different fractions of real data and measure loss of diversity and tails.  
  - Deliverables: Collapse curves.  
  - Pass gate: Diversity measured with defined metrics across several generations.

### 06 — Synthetic Data Pipelines for Language Models and Agents

**Outcome:** Build verified synthetic data pipelines for language-model training and evaluation. The principle of using stronger-model data for post-training is in G3 and synthetic task environments for agents in G4; this module is the quality-control engineering.

**Lessons**

- `01-pipeline-design.md` — Pipeline design: seed data, generation, filtering, deduplication and sampling
- `02-verification-as-the-quality-gate.md` — Verification as the quality gate: executable checkers, unit tests and answer verification
- `03-diversity-measurement-and-control-in-generated-data.md` — Diversity measurement and control in generated data
- `04-judge-based-filtering-and-its-biases.md` — Judge-based filtering and its biases
- `05-decontamination.md` — Decontamination: keeping generated training data out of evaluation sets
- `06-synthetic-evaluation-sets.md` — Synthetic evaluation sets: generating test cases and their validity risks
- `07-synthetic-tasks-and-environments-for-agents-with-automatic-verifiers.md` — Synthetic tasks and environments for agents with automatic verifiers
- `08-terms-of-use-licensing-and-provenance-of-generated-data.md` — Terms-of-use, licensing and provenance of generated data
- `09-cost-and-scaling-of-generation-pipelines.md` — Cost and scaling of generation pipelines

**Hands-on projects**

- **Project 1: verified synthetic math and code data pipeline**  
  - Data: Seed problems and automatic checkers for math answers or code unit tests  
  - Task: Generate problems and solutions, verify with checkers, filter and train a small model, comparing with unfiltered synthetic data.  
  - Deliverables: Pipeline and training comparison.  
  - Pass gate: Evaluation tasks excluded from generation and verified decontaminated.
- **Project 2: diversity and quality of instruction data**  
  - Data: Generated instruction data from two generation methods  
  - Task: Measure diversity and quality and the effect on a fine-tuned model.  
  - Deliverables: Analysis.  
  - Pass gate: Same filtering and training budgets.
- **Project 3: synthetic eval set validity study**  
  - Data: A task with a human-written test set  
  - Task: Generate a synthetic test set and measure how well it ranks models compared with the human-written set.  
  - Deliverables: Rank-agreement analysis.  
  - Pass gate: Model ranking correlation reported with intervals.

### 07 — Evaluation Design Validity and Test Set Engineering

**Outcome:** Design evaluations that measure what you care about. Metric selection basics and train, validation and test splitting are covered in Stage 5A, proper scoring in G7, decision-focused evaluation in G1 and LLM application evaluation sets in G3.

**Lessons**

- `01-evaluation-as-measurement.md` — Evaluation as measurement: construct validity and what a score actually means
- `02-from-goals-to-capabilities.md` — From goals to capabilities: decomposing a task into measurable parts
- `03-metric-design-and-goodhart-effects.md` — Metric design and Goodhart effects: how metrics get gamed
- `04-test-set-design.md` — Test-set design: sampling frames, stratification, hard subsets and long-tail coverage
- `05-test-set-reuse-and-adaptive-overfitting.md` — Test-set reuse and adaptive overfitting: how repeated use erodes validity
- `06-temporal-and-distributional-validity.md` — Temporal and distributional validity: when yesterday's test set stops representing today
- `07-power-analysis-for-evaluation.md` — Power analysis for evaluation: how many test items you need
- `08-evaluation-plans.md` — Evaluation plans: registering metrics and analysis before running
- `09-linking-evaluation-to-decisions.md` — Linking evaluation to decisions: thresholds, go or no-go and cost of errors

**Hands-on projects**

- **Project 1: construct validity audit of a metric**  
  - Data: A metric used in a public benchmark or product  
  - Task: Test whether the metric measures its claimed construct with controlled manipulations and correlations with independent measures.  
  - Deliverables: Audit report.  
  - Pass gate: Manipulations defined before running.
- **Project 2: test set reuse simulation**  
  - Data: Simulated leaderboards with known true performance  
  - Task: Show how repeated submissions inflate apparent performance and compare with holdout-reuse protections.  
  - Deliverables: Simulation results.  
  - Pass gate: Many simulation runs with intervals.
- **Project 3: evaluation plan and power analysis**  
  - Data: A model comparison task  
  - Task: Write an evaluation plan with metrics, subsets, sample sizes and analysis rules and verify its power by simulation.  
  - Deliverables: Plan and power simulation.  
  - Pass gate: Plan time-stamped before results are seen.

### 08 — Benchmark Construction Maintenance and Contamination

**Outcome:** Build benchmarks that stay useful and detect when they stop being so. Anomaly-benchmark flaws are discussed in G5 and recommender evaluation in G6.

**Lessons**

- `01-benchmark-purpose-and-scope.md` — Benchmark purpose and scope: what question a benchmark answers
- `02-data-sourcing-annotation-and-quality-assurance-for-benchmark-items.md` — Data sourcing, annotation and quality assurance for benchmark items
- `03-splits-and-secrecy.md` — Splits and secrecy: public, private and held-out sets and what each risks
- `04-difficulty-calibration-and-the-lifecycle-of-a-benchmark.md` — Difficulty calibration and the lifecycle of a benchmark: saturation and retirement
- `05-contamination.md` — Contamination: how test data leaks into training and how to detect it
- `06-dynamic-and-time-based-benchmarks-as-contamination-defenses.md` — Dynamic and time-based benchmarks as contamination defenses
- `07-leaderboard-design-and-gaming.md` — Leaderboard design and gaming: private variants, selective reporting and sampling bias
- `08-shortcuts-and-artifacts-in-benchmark-data.md` — Shortcuts and artifacts in benchmark data
- `09-benchmark-documentation-versioning-licensing-and-maintenance.md` — Benchmark documentation, versioning, licensing and maintenance

**Hands-on projects**

- **Project 1: benchmark shortcut and artifact audit**  
  - Data: A public NLP or vision benchmark  
  - Task: Find shortcuts with partial-input and simple baselines and measure how much of the benchmark they solve.  
  - Deliverables: Audit report.  
  - Pass gate: Baselines fixed before inspecting labels.
- **Project 2: contamination detection study**  
  - Data: A benchmark and a model with documented training data or a model you fine-tune with planted test items  
  - Task: Compare overlap, perplexity and canary-based contamination detectors on recall and false positives.  
  - Deliverables: Detector comparison.  
  - Pass gate: Planted contamination known by construction.
- **Project 3: build a small benchmark end to end**  
  - Data: A task and data you can legally use  
  - Task: Design, collect, annotate with quality control, split, document and baseline a benchmark of at least 500 items.  
  - Deliverables: Benchmark release package with documentation.  
  - Pass gate: Inter-annotator agreement and baseline results reported.

### 09 — Statistical Methods for Model Comparison

**Outcome:** Say honestly whether one model is better than another. Hypothesis testing and the bootstrap are covered in Stage 4B, comparing models across folds in Stage 5B, evaluation-variance measurement for LLMs in G3 and reporting of RL results in G4; this module adds the methods for dependent items, rankings and aggregation.

**Lessons**

- `01-paired-comparison-tests.md` — Paired comparison tests: paired bootstrap, permutation tests and McNemar's test
- `02-dependent-test-items.md` — Dependent test items: clustered and grouped bootstrap when items share structure
- `03-multiple-comparisons-across-many-models-metrics-and-benchmarks.md` — Multiple comparisons across many models, metrics and benchmarks
- `04-uncertainty-in-rankings.md` — Uncertainty in rankings: rank intervals and probability of being best
- `05-pairwise-preference-models.md` — Pairwise preference models: Bradley-Terry and Elo-style ratings with confidence intervals
- `06-item-response-theory-for-evaluation.md` — Item response theory for evaluation: item difficulty and ability and shortened benchmarks
- `07-accounting-for-hyperparameter-budgets-and-seeds-when-reporting.md` — Accounting for hyperparameter budgets and seeds when reporting
- `08-equivalence-testing-and-minimum-detectable-differences.md` — Equivalence testing and minimum detectable differences
- `09-aggregating-across-tasks.md` — Aggregating across tasks: mean rank, performance profiles and their pitfalls
- `10-meta-analysis-of-evaluation-results-across-studies.md` — Meta-analysis of evaluation results across studies

**Hands-on projects**

- **Project 1: comparison test calibration by simulation**  
  - Data: Simulated model outputs with known true differences and correlated items  
  - Task: Compare naive and clustered tests on false-positive rate and power.  
  - Deliverables: Simulation study.  
  - Pass gate: False-positive rate checked against the nominal level.
- **Project 2: ranking uncertainty with bradley terry**  
  - Data: Public pairwise preference data or simulated comparisons  
  - Task: Fit rating models with bootstrap intervals and show how many comparisons are needed to separate close models.  
  - Deliverables: Rankings with intervals and sample-size analysis.  
  - Pass gate: Intervals validated by simulation.
- **Project 3: irt shortened benchmark**  
  - Data: Model results on a public benchmark with many models  
  - Task: Fit an item response model, select a small item subset and test how well it recovers full-benchmark rankings on held-out models.  
  - Deliverables: Recovery analysis.  
  - Pass gate: Held-out models excluded from item selection.

### 10 — Human Evaluation LLM Judges and Meta Evaluation

**Outcome:** Collect and validate human and model judgments at research grade. Application-level LLM-as-judge calibration is covered in G3 and production judge audits in G11; this module covers the measurement science.

**Lessons**

- `01-human-evaluation-design.md` — Human evaluation design: rubrics, side-by-side comparison and ranking protocols
- `02-rater-recruitment-training-and-reliability.md` — Rater recruitment, training and reliability
- `03-converting-judgments-into-scores.md` — Converting judgments into scores: ratings versus preferences
- `04-crowdsourced-arena-evaluation.md` — Crowdsourced arena evaluation: style and length biases and sampling effects
- `05-expert-versus-crowd-raters-and-when-each-is-needed.md` — Expert versus crowd raters and when each is needed
- `06-cultural-and-language-effects-on-judgments-including-indic-language-raters.md` — Cultural and language effects on judgments, including Indic-language raters
- `07-judge-models.md` — Judge models: bias quantification, ensembles of judges and calibration against humans at scale
- `08-meta-evaluation.md` — Meta-evaluation: evaluating the evaluators with judge and reward-model benchmarks
- `09-ethics-of-human-evaluation.md` — Ethics of human evaluation: consent, welfare and data protection

**Hands-on projects**

- **Project 1: human eval study with reliability analysis**  
  - Data: Outputs from three systems on a task you define  
  - Task: Run a human evaluation with a written protocol and at least three raters, and analyze reliability and rater effects.  
  - Deliverables: Study report.  
  - Pass gate: Agreement and rater bias reported with intervals.
- **Project 2: judge bias quantification**  
  - Data: Pairs of outputs where quality and style are controlled  
  - Task: Measure position, length and self-preference bias for several judges and test debiasing methods.  
  - Deliverables: Bias analysis.  
  - Pass gate: Controlled pair construction documented.
- **Project 3: meta evaluation of judges**  
  - Data: A human-labeled preference set  
  - Task: Compare judges and reward models on agreement with humans overall and by category.  
  - Deliverables: Meta-evaluation report.  
  - Pass gate: Per-category agreement reported.

### 11 — Evaluating Foundation Models

**Outcome:** Evaluate broad models fairly and reproducibly. Application-level LLM evaluation is in G3 and safety evaluation in G12; this module covers general capability measurement.

**Lessons**

- `01-capability-taxonomies-and-the-main-evaluation-families-for-language-models.md` — Capability taxonomies and the main evaluation families for language models
- `02-evaluation-ecosystems.md` — Evaluation ecosystems: HELM and lm-evaluation-harness and their configuration choices
- `03-sensitivity-to-prompt-format-few-shot-examples-and-decoding-settings.md` — Sensitivity to prompt format, few-shot examples and decoding settings
- `04-reproducibility.md` — Reproducibility: numerical differences, batching and inference-engine effects on scores
- `05-capability-elicitation.md` — Capability elicitation: why scores can understate what a model can do
- `06-evaluating-reasoning-long-context-and-tool-use-with-verifiable-and-unverifiable-tasks.md` — Evaluating reasoning, long context and tool use with verifiable and unverifiable tasks
- `07-robustness-and-distribution-shift-evaluation.md` — Robustness and distribution shift evaluation: paraphrase, perturbation and shifted domains
- `08-multilingual-and-indic-language-evaluation.md` — Multilingual and Indic-language evaluation: coverage, translation artifacts and cultural validity
- `09-multimodal-evaluation.md` — Multimodal evaluation: pointers to G2 and combined-modality pitfalls

**Hands-on projects**

- **Project 1: prompt and format sensitivity study**  
  - Data: A benchmark subset and two open models  
  - Task: Vary prompt format, few-shot choice and decoding settings and quantify score changes against the claimed differences between models.  
  - Deliverables: Sensitivity analysis.  
  - Pass gate: Many configurations per model and intervals reported.
- **Project 2: reproducing published evaluation numbers**  
  - Data: A published model and benchmark with public code  
  - Task: Reproduce reported scores with different harness versions and engines and document discrepancies.  
  - Deliverables: Reproduction report.  
  - Pass gate: Every setting, version and seed recorded.
- **Project 3: indic language evaluation suite**  
  - Data: Public Indic benchmarks such as IndicXTREME tasks, with licences checked  
  - Task: Evaluate several models across languages and analyze gaps, translation artifacts and variance.  
  - Deliverables: Per-language report.  
  - Pass gate: Per-language results reported with intervals.

### 12 — Behavioral Testing and Stress Evaluation

**Outcome:** Find failures that aggregate metrics hide. Data and model behavior tests are introduced in Stage 5D, property-based testing in Stage 2C and slice analysis in Stage 5A; this module builds systematic suites.

**Lessons**

- `01-behavioral-testing-frameworks.md` — Behavioral testing frameworks: capabilities by test type as in CheckList
- `02-metamorphic-testing.md` — Metamorphic testing: invariance and directional-expectation relations by task
- `03-challenge-sets-and-adversarially-collected-data.md` — Challenge sets and adversarially collected data
- `04-template-and-automated-test-generation-with-validation-of-the-generated-cases.md` — Template and automated test generation with validation of the generated cases
- `05-slice-based-and-disaggregated-evaluation-reports.md` — Slice-based and disaggregated evaluation reports
- `06-stress-tests-for-rare-events-and-the-long-tail.md` — Stress tests for rare events and the long tail
- `07-simulation-based-scenario-evaluation-for-safety-relevant-systems.md` — Simulation-based scenario evaluation for safety-relevant systems
- `08-turning-incidents-into-permanent-regression-tests.md` — Turning incidents into permanent regression tests
- `09-coverage-criteria-for-test-suites.md` — Coverage criteria for test suites: how to know a suite is enough

**Hands-on projects**

- **Project 1: checklist style suite for a task**  
  - Data: A classification or extraction model of your choice  
  - Task: Build a behavioral test suite with invariance, directional and minimum-functionality tests and find bugs that held-out accuracy missed.  
  - Deliverables: Test suite and bug report.  
  - Pass gate: At least one failure type invisible in aggregate accuracy is found and documented.
- **Project 2: metamorphic relations catalog**  
  - Data: Two tasks from different modalities  
  - Task: Define and validate metamorphic relations and measure violation rates across models.  
  - Deliverables: Catalog and results.  
  - Pass gate: Relations validated by humans on a sample.
- **Project 3: incident to regression test pipeline**  
  - Data: Failures from earlier projects  
  - Task: Convert failures into labeled tests automatically with review and track suite growth and regression catches.  
  - Deliverables: Pipeline and metrics.  
  - Pass gate: A reintroduced bug is caught by the suite.

### 13 — Evaluation Harness Engineering and Platforms

**Outcome:** Build evaluation systems that are reproducible, fast and affordable. CI gates for LLM applications are covered in G3, the evaluation service of the ML platform in G11 and agent test suites in G4; this module covers the harness itself.

**Lessons**

- `01-harness-architecture.md` — Harness architecture: datasets, runners, scorers, caching and result stores
- `02-determinism-and-reproducibility.md` — Determinism and reproducibility: seeds, containers, versions and recorded environments
- `03-parallelism-retries-and-rate-limits-for-model-based-evaluation.md` — Parallelism, retries and rate limits for model-based evaluation
- `04-cost-control.md` — Cost control: caching, adaptive sampling and early stopping of evaluations
- `05-sandboxed-execution-for-code-and-tool-using-evaluations.md` — Sandboxed execution for code and tool-using evaluations
- `06-evaluation-registries-versioning-and-provenance-of-results.md` — Evaluation registries, versioning and provenance of results
- `07-analysis-and-dashboards.md` — Analysis and dashboards: from raw scores to decisions
- `08-open-harnesses-and-frameworks-including-inspect-and-lm-evaluation-harness-with-maintenance-and-licence-checks.md` — Open harnesses and frameworks, including Inspect and lm-evaluation-harness, with maintenance and licence checks
- `09-protecting-private-evaluation-data-and-preventing-leakage-through-the-harness.md` — Protecting private evaluation data and preventing leakage through the harness

**Hands-on projects**

- **Project 1: evaluation harness from scratch**  
  - Data: Three small benchmarks and two models  
  - Task: Build a harness with caching, parallel execution, deterministic settings and a result store, and verify it reproduces known scores.  
  - Deliverables: Harness and reproduction tests.  
  - Pass gate: Re-running any evaluation gives identical stored results.
- **Project 2: adaptive evaluation cost reduction**  
  - Data: A benchmark with many items and several models  
  - Task: Implement adaptive sampling and early stopping and measure cost saved against ranking errors introduced.  
  - Deliverables: Cost-versus-error analysis.  
  - Pass gate: Ranking agreement with the full evaluation reported.
- **Project 3: harness leakage and integrity tests**  
  - Data: Your harness  
  - Task: Add tests that detect answer leakage in prompts, caching mistakes and scorer bugs.  
  - Deliverables: Integrity test suite.  
  - Pass gate: Injected leaks and scorer bugs are caught.

### 14 — Evaluation Practice Reporting and Ecosystem

**Outcome:** Report, govern and sustain evaluation work, including in the Indian language and sector context.

**Lessons**

- `01-writing-evaluation-reports.md` — Writing evaluation reports: claims, evidence, limitations and what was not tested
- `02-pre-registered-and-replicated-evaluations.md` — Pre-registered and replicated evaluations
- `03-independent-and-third-party-evaluation.md` — Independent and third-party evaluation: access, incentives and conflicts
- `04-evaluation-in-procurement-and-regulation.md` — Evaluation in procurement and regulation: from benchmarks to requirements
- `05-organizing-an-evaluation-function.md` — Organizing an evaluation function: roles, review and evaluation as a product
- `06-ethics-of-evaluation-research.md` — Ethics of evaluation research: data, people and dual-use findings
- `07-indian-ecosystem.md` — Indian ecosystem: Indic benchmarks, sector needs and gaps in coverage
- `08-evaluation-research-frontiers-and-open-problems.md` — Evaluation research frontiers and open problems
- `09-portfolio-and-career.md` — Portfolio and career: building and presenting evaluation work

**Hands-on projects**

- **Project 1: independent evaluation report**  
  - Data: A public model or system you may legally evaluate  
  - Task: Plan, run and report an independent evaluation with a registered plan, limitations and a response-to-critique section.  
  - Deliverables: Evaluation report.  
  - Pass gate: Plan registered before testing and all deviations recorded.
- **Project 2: replication of an evaluation paper**  
  - Data: A published evaluation or benchmark paper with public code  
  - Task: Replicate the central claim, test robustness and report differences.  
  - Deliverables: Replication report.  
  - Pass gate: Every deviation from the original documented.
- **Project 3: indic benchmark gap analysis**  
  - Data: Public Indic benchmarks and your target use cases  
  - Task: Map benchmark coverage against real tasks and languages, identify gaps and propose a new benchmark design.  
  - Deliverables: Gap analysis and design proposal.  
  - Pass gate: Coverage claims verified against benchmark documentation.

### 15 — G13 Capstones

**Outcome:** integrate the data and evaluation tracks in assessed, portfolio-quality work.

- **Capstone 1: data centric improvement campaign** (uses Modules 01 to 03)  
  Improve a model through a documented data-centric campaign with diagnostics, targeted collection, valuation or selection and labeling quality work, with controlled comparisons against model-centric tuning.
- **Capstone 2: synthetic data program with quality gates** (uses Modules 04 to 06)  
  Build a synthetic data program for a real task with generation, verification, privacy and utility evaluation, and a documented recommendation on when to use it.
- **Capstone 3: benchmark and evaluation suite for a task** (uses Modules 07 to 09, 12, 13)  
  Design and release a benchmark and evaluation harness for a task with validity analysis, contamination controls, statistical comparison methods and a stress-test suite.
- **Capstone 4: foundation model evaluation study** (uses Modules 10, 11, 14)  
  Run a rigorous evaluation of several models including human and judge-based measurement, sensitivity analysis and a reproducibility package, and publish the report.
- **Capstone 5: g13 readiness assessment** (uses All modules)  
  Written and practical assessment against the G13 completion gate.

## G13 completion gate

- Every data-improvement claim is measured with controlled comparisons against a compute-matched or budget-matched random baseline, with seed variance, on held-out data untouched by the improvement.
- Every synthetic-data claim reports fidelity, utility and privacy together, with privacy assessed by attacks and utility measured on real held-out data.
- Every model comparison uses a paired or clustered test appropriate to the data structure, reports intervals and states the multiple-comparison treatment.
- Every benchmark or evaluation set has a written purpose, quality assurance, contamination controls, documentation and a retirement plan.
- Every evaluation plan is time-stamped before results are seen, and all deviations are recorded.
- Every human-labeling or human-evaluation project has written instructions, agreement analysis, fair-pay and welfare policies and consent.
- Every dataset and tool has licence, access conditions and maintenance status recorded before use.
- All results reproduce from a lockfile, configs and logged seeds, with versions recorded.
- At least one negative or inconclusive result per track is reported honestly, including a case where a data fix, synthetic data or a metric did not help.
- The four specialist capstones are complete and the readiness assessment is passed.

## Audit and verification

**What was checked and the result**

- Structure: 14 specialist modules each have 6 to 12 lessons and at least one project; the tree contains 214 files and 31 folders, and these counts equal the counts computed from the curriculum data. The overview file names listed in the description were checked to appear in the tree.
- Overlap with the Roadmap: all 128 lesson file names were compared against every lesson file name in `Roadmap.md`. Exact matches: 0. Near matches (similarity 0.80 or higher): 0.
- Structural problems found by the build script: 0.
- Topic-level overlap check: the Roadmap text was searched for contamination, annotation, inter-annotator agreement, Krippendorff, data valuation, Shapley, influence functions, coresets, curriculum learning, data pruning, dataset distillation, CTGAN, SDV, item response theory, Bradley-Terry, leaderboards, Goodhart, MLPerf and metamorphic testing. None appear as lessons, so G13 teaches them for the first time. The search also found existing lessons that G13 builds on rather than repeats: Stage 2C synthetic and sampled test data and benchmarking pipelines, Stage 5A label noise, data-centric versus model-centric improvement and ablation studies, and the Stage 5B module on semi-supervised, active and weak supervision. The matches for 'kappa' and 'elo' were unrelated words (the Kappa architecture and unrelated terms) and were discounted after reading the lines.
- Verified by web search on the build date (2026-10-26): the model-collapse paper (Shumailov et al., Nature, July 2024) shows recursive training on generated output degrades models, loses rare content first and slows when real data is mixed in, with critics noting its setting is narrow; 'The Leaderboard Illusion' (arXiv 2504.20879, 2025) reports that private testing of many variants on Chatbot Arena can skew rankings, and a rebuttal disputes its framing; tinyBenchmarks applies item response theory to estimate benchmark performance from small item subsets; Inspect AI is an MIT-licensed evaluation framework from the UK AI Security Institute; IndicXTREME is an AI4Bharat benchmark of nine task types over about 20 Indic languages (counts differ between versions); CheckList (ACL 2020) is a behavioral-testing methodology; WILDS (ICML 2021) is a benchmark of in-the-wild distribution shifts.
- Reported but not confirmed: the primary Nature paper and the tinyBenchmarks abstract were not retrieved directly (summaries came from secondary sources); the current status and maintenance of Dynabench, SDV and its metrics library, synthcity, lm-evaluation-harness, HELM and OpenCompass were not confirmed; Inspect's version numbers differ between sources and its Docker-dependence claim comes from one secondary site; dataset cartography, Dawid-Skene, influence functions, data Shapley, DoReMi, LIMA-style data selection, the reusable-holdout results and the Kaggle overfitting meta-analysis are cited from established literature and were not re-checked.
- Not verified: tool and library versions, which change quickly; dataset licences and availability; and any benchmark score or leaderboard claim, none of which this plan asserts.
- Not verified by execution: no code in this plan has been run. Project pass gates are acceptance criteria to be met when the projects are built.
- Safety and ethics note: labeling and human-evaluation projects involve people. Pay fairly, obtain consent, protect annotator privacy and welfare, avoid exposing raters to harmful content without safeguards, and do not generate or release synthetic data that could re-identify real individuals.
- Repository safety: this build created only this file; no existing file or folder was created, changed or deleted by it.
