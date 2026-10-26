# ML Specialization

The specialization curriculum that follows Stage 5D of the [Roadmap](./Roadmap.md). This file currently contains **Group 1 (G1) — Classical and Applied ML**, which covers original categories **1 Traditional ML Engineering, 2 Applied ML and 33 AutoML and Neural Architecture Search**. Groups G2 to G14 are added as separate sections later.

## G1 summary

| Item | Count |
|---|---|
| Modules (including overview and capstones) | 19 |
| Lesson files | 161 |
| Hands-on project files (module projects, overview project and capstones) | 57 |
| Folders inside the G1 tree | 37 |
| Files inside the G1 tree | 262 |

## Scope and how G1 avoids repeating the Roadmap

G1 starts where Stages 5A and 5B stop. The following are **already learned** and are only referenced, never retaught: regression and classification algorithms, preprocessing and scikit-learn pipelines, cross-validation and tuning basics, random forests and the introduction to XGBoost, LightGBM and CatBoost, imbalanced learning and thresholds, calibration and conformal prediction, anomaly detection, SHAP and permutation importance, nested validation and Bayesian optimization concepts, survival-analysis concepts, causal inference and uplift, experiment tracking and MLflow, model serving, CI/CD, monitoring, PySpark and Spark MLlib, Dask DataFrames and Polars.

| Roadmap topic already covered | Where G1 goes further |
|---|---|
| Multi-label classification introduction (5A) | Module 01: classifier chains, label powerset, ordinal, hierarchical and extreme label spaces |
| Survival analysis concepts (5B) | Module 02: Cox, AFT, survival forests, evaluation, competing risks, PU learning and noisy labels |
| Gradient boosting fundamentals and tuning (5A) | Module 03: internals, custom objectives, GPU and tree compilation |
| Feature engineering, selection and importance (5A, 5B) | Module 04: automated and relational features, embeddings and Boruta/null-importance selection |
| Voting, stacking and blending (5A) | Module 05: multi-level stacking, ensemble selection, distillation and failure patterns |
| SHAP and explainability (5B) | Module 06: models that are interpretable by construction, scorecards and reason codes |
| Deep learning for tabular data, one lesson (5C) | Module 07: modern deep tabular models and tabular foundation models with fair benchmarks |
| Spark MLlib, Dask, Polars (Stages 2B, 2C) | Module 08: out-of-core boosting, distributed XGBoost and GPU data science |
| Business problem framing and metrics (5A) | Modules 09 and 10: discovery, value estimation, profit curves and pilots |
| Bayesian optimization and multi-fidelity tuning (5B) | Modules 14 to 17: AutoML systems, frameworks, your own AutoML and neural architecture search |

## G1 — Classical and Applied ML

**Defining question:** How do I build and automate models on tabular data?

```text
ML Specialization/
└── G1 — Classical and Applied ML/
    ├── 00-G1-Overview/
    │   ├── Projects/
    │   │   ├── 01-g1-environment-and-benchmark-bootstrap.md
    │   │   └── README.md
    │   ├── 01-g1-scope-and-how-it-differs-from-stages-5a-5d.md
    │   ├── 02-prerequisite-map-from-the-roadmap.md
    │   ├── 03-dataset-and-tooling-register.md
    │   ├── 04-evaluation-and-reporting-standards.md
    │   ├── 05-completion-gate.md
    │   ├── README.md
    │   └── learning-plan.md
    ├── 01-Multi-Output-Multi-Label-and-Non-Standard-Targets/
    │   ├── Projects/
    │   │   ├── 01-multi-label-benchmark-on-emotions-and-yeast.md
    │   │   ├── 02-ordinal-vs-nominal-modeling-of-wine-quality.md
    │   │   ├── 03-hierarchical-text-classifier-on-20-newsgroups.md
    │   │   └── README.md
    │   ├── 01-multi-output-regression.md
    │   ├── 02-multi-label-decomposition.md
    │   ├── 03-multi-label-metrics.md
    │   ├── 04-label-dependence-analysis.md
    │   ├── 05-ordinal-classification.md
    │   ├── 06-ordinal-evaluation.md
    │   ├── 07-hierarchical-classification.md
    │   ├── 08-extreme-classification.md
    │   ├── 09-compositional-targets.md
    │   ├── 10-target-formulation-guide.md
    │   └── README.md
    ├── 02-Censored-Noisy-and-Partially-Observed-Labels/
    │   ├── Projects/
    │   │   ├── 01-survival-models-on-whas500-and-rossi.md
    │   │   ├── 02-pu-learning-from-hidden-positives.md
    │   │   ├── 03-label-noise-injection-and-recovery-with-cleanlab.md
    │   │   └── README.md
    │   ├── 01-censoring-and-truncation.md
    │   ├── 02-cox-proportional-hazards-in-practice.md
    │   ├── 03-accelerated-failure-time-models.md
    │   ├── 04-survival-forests-and-boosted-survival-models.md
    │   ├── 05-survival-evaluation.md
    │   ├── 06-competing-risks-and-recurrent-events.md
    │   ├── 07-positive-unlabeled-learning.md
    │   ├── 08-learning-with-noisy-labels.md
    │   ├── 09-selection-bias-in-labels.md
    │   ├── 10-label-quality-audit-protocol.md
    │   └── README.md
    ├── 03-Advanced-Gradient-Boosting-Engineering/
    │   ├── Projects/
    │   │   ├── 01-gradient-boosting-from-scratch.md
    │   │   ├── 02-asymmetric-business-loss-with-custom-objectives.md
    │   │   ├── 03-tree-inference-compilation-benchmark.md
    │   │   └── README.md
    │   ├── 01-histogram-splits.md
    │   ├── 02-newton-boosting.md
    │   ├── 03-custom-objectives-and-metrics.md
    │   ├── 04-non-gaussian-objectives.md
    │   ├── 05-catboost-internals.md
    │   ├── 06-lightgbm-options.md
    │   ├── 07-regularization-playbook.md
    │   ├── 08-early-stopping-and-seed-variance.md
    │   ├── 09-gpu-boosting.md
    │   ├── 10-tree-ensemble-compilation.md
    │   ├── 11-model-size-reduction.md
    │   └── README.md
    ├── 04-Advanced-Feature-Engineering-and-Tabular-Representation/
    │   ├── Projects/
    │   │   ├── 01-multi-table-credit-features-with-home-credit.md
    │   │   ├── 02-feature-selection-method-shootout.md
    │   │   ├── 03-text-plus-tabular-price-model.md
    │   │   └── README.md
    │   ├── 01-deep-feature-synthesis.md
    │   ├── 02-multi-table-feature-engineering.md
    │   ├── 03-interaction-discovery.md
    │   ├── 04-entity-embeddings.md
    │   ├── 05-numerical-embeddings.md
    │   ├── 06-out-of-fold-feature-frameworks.md
    │   ├── 07-advanced-feature-selection.md
    │   ├── 08-text-plus-tabular-models.md
    │   ├── 09-feature-ablation-by-group.md
    │   ├── 10-feature-gain-accounting.md
    │   └── README.md
    ├── 05-Ensembling-Stacking-and-Model-Combination-at-Depth/
    │   ├── Projects/
    │   │   ├── 01-multi-level-stacking-pipeline.md
    │   │   ├── 02-ensemble-distillation-study.md
    │   │   ├── 03-leaky-stacking-reproduction-and-fix.md
    │   │   └── README.md
    │   ├── 01-why-ensembles-work.md
    │   ├── 02-oof-prediction-protocol.md
    │   ├── 03-multi-level-stacking.md
    │   ├── 04-greedy-ensemble-selection.md
    │   ├── 05-averaging-schemes.md
    │   ├── 06-diversity-sources.md
    │   ├── 07-ensembles-under-group-and-time-aware-validation.md
    │   ├── 08-ensemble-calibration.md
    │   ├── 09-cost-of-ensembles.md
    │   ├── 10-ensemble-distillation.md
    │   └── README.md
    ├── 06-Interpretable-and-Glass-Box-Models/
    │   ├── Projects/
    │   │   ├── 01-credit-scorecard-with-reason-codes.md
    │   │   ├── 02-ebm-vs-gbdt-vs-gam-benchmark.md
    │   │   ├── 03-sparse-integer-risk-score-for-heart-disease.md
    │   │   └── README.md
    │   ├── 01-glass-box-rationale.md
    │   ├── 02-generalized-additive-models.md
    │   ├── 03-explainable-boosting-machines.md
    │   ├── 04-optimal-binning.md
    │   ├── 05-logistic-scorecards.md
    │   ├── 06-rule-based-models.md
    │   ├── 07-sparse-integer-risk-scores.md
    │   ├── 08-monotonic-and-constrained-models-as-glass-box-compromises.md
    │   ├── 09-adverse-action-reason-codes.md
    │   ├── 10-the-rashomon-effect.md
    │   └── README.md
    ├── 07-Deep-Learning-and-Foundation-Models-for-Tabular-Data/
    │   ├── Projects/
    │   │   ├── 01-tabular-benchmark-harness.md
    │   │   ├── 02-small-data-learning-curves.md
    │   │   ├── 03-self-supervised-pretraining-with-few-labels.md
    │   │   └── README.md
    │   ├── 01-evidence-review.md
    │   ├── 02-strong-mlp-baselines.md
    │   ├── 03-numerical-feature-embeddings.md
    │   ├── 04-attention-based-tabular-models.md
    │   ├── 05-tabnet-and-node.md
    │   ├── 06-tabm.md
    │   ├── 07-retrieval-based-tabular-models.md
    │   ├── 08-self-supervised-pretraining-for-tabular-data.md
    │   ├── 09-in-context-tabular-foundation-models.md
    │   ├── 10-decision-guide.md
    │   └── README.md
    ├── 08-Scaling-Tabular-ML-Beyond-a-Single-Machine-Core/
    │   ├── Projects/
    │   │   ├── 01-train-on-data-larger-than-memory.md
    │   │   ├── 02-cpu-vs-gpu-cost-report.md
    │   │   └── README.md
    │   ├── 01-how-much-data-do-you-need.md
    │   ├── 02-external-memory-boosting.md
    │   ├── 03-distributed-boosting.md
    │   ├── 04-dask-ml-and-joblib.md
    │   ├── 05-gpu-data-science.md
    │   ├── 06-distributed-hyperparameter-search.md
    │   ├── 07-cost-performance-benchmarking.md
    │   ├── 08-scaling-pitfalls.md
    │   └── README.md
    ├── 09-Applied-ML-Problem-Discovery-and-Scoping/
    │   ├── Projects/
    │   │   ├── 01-three-case-scoping-packets.md
    │   │   ├── 02-roi-model-with-sensitivity-analysis.md
    │   │   ├── 03-churn-label-definition-study.md
    │   │   └── README.md
    │   ├── 01-decision-mapping.md
    │   ├── 02-opportunity-assessment.md
    │   ├── 03-ml-canvas-and-stakeholder-interview-protocol.md
    │   ├── 04-success-metric-trees.md
    │   ├── 05-label-and-outcome-design.md
    │   ├── 06-estimating-value-before-building.md
    │   ├── 07-build-vs-buy-vs-rules-vs-analytics.md
    │   ├── 08-data-audit-for-applied-projects.md
    │   ├── 09-scoping-documents-milestones-and-uncertainty-aware-estimation.md
    │   ├── 10-ethics-and-harm-screening-at-scoping-time.md
    │   └── README.md
    ├── 10-Decision-Focused-Evaluation-and-Pilots/
    │   ├── Projects/
    │   │   ├── 01-campaign-targeting-simulator.md
    │   │   ├── 02-pilot-power-analysis-and-readout.md
    │   │   ├── 03-executive-model-readout.md
    │   │   └── README.md
    │   ├── 01-lift-gain-ks-gini-and-decile-analysis.md
    │   ├── 02-profit-curves.md
    │   ├── 03-offline-to-business-translation.md
    │   ├── 04-pilot-design.md
    │   ├── 05-silent-launch-and-phased-business-evaluation.md
    │   ├── 06-human-in-the-loop-analysis.md
    │   ├── 07-decision-environment-drift.md
    │   ├── 08-executive-reporting.md
    │   └── README.md
    ├── 11-Applied-Customer-and-Marketing-ML/
    │   ├── Projects/
    │   │   ├── 01-customer-lifetime-value-on-cdnow-and-online-retail-ii.md
    │   │   ├── 02-churn-and-survival-on-telco.md
    │   │   ├── 03-marketing-mix-model-with-known-ground-truth.md
    │   │   ├── 04-price-elasticity-study.md
    │   │   └── README.md
    │   ├── 01-behavioral-segmentation.md
    │   ├── 02-churn-modeling-in-practice.md
    │   ├── 03-customer-lifetime-value.md
    │   ├── 04-ml-based-lifetime-value.md
    │   ├── 05-propensity-and-lead-scoring.md
    │   ├── 06-next-best-action.md
    │   ├── 07-marketing-mix-modeling.md
    │   ├── 08-price-and-promotion-elasticity.md
    │   ├── 09-customer-data-pitfalls.md
    │   └── README.md
    ├── 12-Applied-Operations-ML-and-Entity-Resolution/
    │   ├── Projects/
    │   │   ├── 01-splink-deduplication-on-historical-and-febrl-data.md
    │   │   ├── 02-complaint-triage-priority-queue.md
    │   │   ├── 03-messy-erp-extract-cleaning-project.md
    │   │   └── README.md
    │   ├── 01-predictive-triage.md
    │   ├── 02-operational-risk-prediction.md
    │   ├── 03-entity-resolution-fundamentals.md
    │   ├── 04-probabilistic-record-linkage-with-splink.md
    │   ├── 05-learned-matching.md
    │   ├── 06-deduplication-and-master-data.md
    │   ├── 07-messy-enterprise-extracts.md
    │   ├── 08-matching-evaluation.md
    │   ├── 09-operating-applied-models.md
    │   └── README.md
    ├── 13-Applied-ML-Delivery-Communication-and-Stakeholder-Practice/
    │   ├── Projects/
    │   │   ├── 01-design-document-and-decision-memo.md
    │   │   ├── 02-stakeholder-prototype-with-feedback-loop.md
    │   │   ├── 03-post-launch-review-simulation.md
    │   │   └── README.md
    │   ├── 01-ml-design-documents-and-decision-memos.md
    │   ├── 02-rapid-prototypes.md
    │   ├── 03-data-storytelling.md
    │   ├── 04-ownership-and-handoff.md
    │   ├── 05-value-tracking.md
    │   ├── 06-hidden-technical-debt-in-ml-systems.md
    │   ├── 07-managing-expectations.md
    │   ├── 08-case-study-writing.md
    │   └── README.md
    ├── 14-AutoML-Foundations-and-Search-Spaces/
    │   ├── Projects/
    │   │   ├── 01-hpo-algorithms-from-scratch.md
    │   │   ├── 02-meta-learning-warm-start-study.md
    │   │   ├── 03-search-space-design-critique.md
    │   │   └── README.md
    │   ├── 01-the-automl-problem.md
    │   ├── 02-search-space-design.md
    │   ├── 03-search-strategies.md
    │   ├── 04-bandit-based-budget-allocation.md
    │   ├── 05-meta-learning-and-warm-starting.md
    │   ├── 06-post-hoc-ensembling-and-stacking-inside-automl.md
    │   ├── 07-budget-semantics.md
    │   ├── 08-automl-benchmarking.md
    │   └── README.md
    ├── 15-AutoML-Frameworks-and-HPO-Systems/
    │   ├── Projects/
    │   │   ├── 01-five-framework-comparison-under-equal-budget.md
    │   │   ├── 02-distributed-multi-objective-optuna-study.md
    │   │   ├── 03-automl-audit-with-injected-leakage.md
    │   │   └── README.md
    │   ├── 01-optuna.md
    │   ├── 02-ray-tune.md
    │   ├── 03-smac3-hyperopt-and-keras-tuner-compared.md
    │   ├── 04-autogluon-tabular.md
    │   ├── 05-flaml-h2o-automl-and-auto-sklearn.md
    │   ├── 06-cloud-automl-services.md
    │   ├── 07-customizing-automl.md
    │   ├── 08-experiment-tracking.md
    │   ├── 09-automl-failure-modes.md
    │   ├── 10-automl-governance.md
    │   └── README.md
    ├── 16-Build-Your-Own-AutoML-System/
    │   ├── Projects/
    │   │   ├── 01-automl-mvp.md
    │   │   ├── 02-automl-benchmark-against-frameworks.md
    │   │   ├── 03-refusal-and-safety-tests.md
    │   │   └── README.md
    │   ├── 01-automl-system-design.md
    │   ├── 02-data-profiling.md
    │   ├── 03-preprocessing-generation.md
    │   ├── 04-model-zoo-and-scheduler.md
    │   ├── 05-experiment-store.md
    │   ├── 06-ensembling-and-final-model-selection.md
    │   ├── 07-automatic-reports.md
    │   ├── 08-serving-and-cli.md
    │   ├── 09-testing-and-benchmarking.md
    │   └── README.md
    ├── 17-Neural-Architecture-Search/
    │   ├── Projects/
    │   │   ├── 01-nas-bench-201-search-strategy-comparison.md
    │   │   ├── 02-darts-instability-reproduction.md
    │   │   ├── 03-hardware-aware-search-under-latency-budget.md
    │   │   └── README.md
    │   ├── 01-nas-formulation.md
    │   ├── 02-search-spaces.md
    │   ├── 03-nas-benchmarks.md
    │   ├── 04-reinforcement-learning-and-evolutionary-nas.md
    │   ├── 05-one-shot-nas.md
    │   ├── 06-differentiable-nas.md
    │   ├── 07-cheap-performance-estimation.md
    │   ├── 08-hardware-aware-and-multi-objective-nas.md
    │   ├── 09-nas-tooling.md
    │   ├── 10-honest-nas-evaluation.md
    │   ├── 11-when-not-to-use-nas.md
    │   └── README.md
    ├── 18-G1-Capstones/
    │   ├── 01-tabular-model-benchmark-and-decision-report.md
    │   ├── 02-end-to-end-applied-business-case.md
    │   ├── 03-glass-box-scoring-system-with-monitoring.md
    │   ├── 04-automl-and-nas-engineering-study.md
    │   ├── 05-g1-readiness-assessment.md
    │   └── README.md
    └── README.md
```

### 00 — G1 Overview

**Purpose:** the single authoritative plan for G1 with scope, prerequisite map, dataset register, reporting standards and completion gate.

- `01-g1-scope-and-how-it-differs-from-stages-5a-5d.md` — what G1 teaches and what it deliberately skips.
- `02-prerequisite-map-from-the-roadmap.md` — exact Roadmap stages and modules assumed for each G1 module.
- `03-dataset-and-tooling-register.md` — every dataset, library, licence and access condition used in G1, with version pins.
- `04-evaluation-and-reporting-standards.md` — repeated-CV rules, confidence intervals, seed policy and report template used by all projects.
- `05-completion-gate.md` — measurable criteria to finish G1.
- `learning-plan.md` — recommended order and time budget.

**Project 1: g1 environment and benchmark bootstrap**  
- Data: three OpenML datasets chosen for the later benchmark.  
- Task: build a reproducible G1 workspace with the pinned tooling and a benchmark skeleton that logs seeds, splits and versions.  
- Deliverables: lockfile, benchmark skeleton and a smoke test.  
- Pass gate: a clean machine reproduces the smoke test from the lockfile.

### 01 — Multi Output Multi Label and Non Standard Targets

**Outcome:** Model targets that are not a single number or a single class: several outputs at once, label sets, ordered levels, label hierarchies, huge label spaces and proportions.

**Lessons**

- `01-multi-output-regression.md` — Multi-output regression: independent, chained and joint strategies; when target correlation is worth exploiting
- `02-multi-label-decomposition.md` — Multi-label decomposition: binary relevance, classifier chains and label powerset, with their cost and failure modes
- `03-multi-label-metrics.md` — Multi-label metrics: Hamming loss, subset accuracy, example-based vs micro/macro F1 and per-label thresholds
- `04-label-dependence-analysis.md` — Label dependence analysis: co-occurrence matrices, conditional label structure and when dependence helps
- `05-ordinal-classification.md` — Ordinal classification: cumulative-link models and ordinal-aware gradient boosting
- `06-ordinal-evaluation.md` — Ordinal evaluation: quadratic weighted kappa, ordinal MAE and why accuracy misleads
- `07-hierarchical-classification.md` — Hierarchical classification: flat, top-down and hierarchy-consistent prediction
- `08-extreme-classification.md` — Extreme classification: large label spaces, negative sampling and label trees
- `09-compositional-targets.md` — Compositional targets: proportions, simplex outputs and log-ratio transforms
- `10-target-formulation-guide.md` — Target formulation guide: regression vs classification vs ordinal vs multi-label decision rules and failure patterns

**Hands-on projects**

- **Project 1: multi label benchmark on emotions and yeast**  
  - Data: Emotions and Yeast multi-label datasets (MULAN benchmark collection)  
  - Task: Compare binary relevance, classifier chains and label powerset with LightGBM and logistic regression; tune per-label thresholds.  
  - Deliverables: Notebook, metric table (Hamming, subset accuracy, micro/macro F1), co-occurrence heatmap, written recommendation.  
  - Pass gate: Per-label thresholds beat a global 0.5 threshold on micro-F1 with a confidence interval across repeated CV; results reproducible from one config.
- **Project 2: ordinal vs nominal modeling of wine quality**  
  - Data: UCI Wine Quality (red and white)  
  - Task: Model quality scores as nominal classes, plain regression with rounding, and ordinal models; evaluate with QWK and ordinal MAE.  
  - Deliverables: Comparison report with error-distance analysis (how far wrong, not just how often wrong).  
  - Pass gate: Report shows at least one case where accuracy ranks models differently from QWK, with an explanation.
- **Project 3: hierarchical text classifier on 20 newsgroups**  
  - Data: 20 Newsgroups with its implied topic hierarchy (comp.*, rec.*, sci.* ...)  
  - Task: Build flat, top-down and hierarchy-consistent classifiers on TF-IDF features; measure hierarchical precision and recall.  
  - Deliverables: Three pipelines, hierarchical metric implementation, error taxonomy by tree level.  
  - Pass gate: Hierarchy-consistent predictions never violate parent-child constraints; metric code is unit tested.

### 02 — Censored Noisy and Partially Observed Labels

**Outcome:** Train and evaluate models when the label is incomplete, delayed, wrong or only partly observed, which is the normal state of business data.

**Lessons**

- `01-censoring-and-truncation.md` — Censoring and truncation: right, left and interval censoring, and why plain regression and classification fail
- `02-cox-proportional-hazards-in-practice.md` — Cox proportional hazards in practice: fitting, assumption checks and interpretation with lifelines and scikit-survival
- `03-accelerated-failure-time-models.md` — Accelerated failure time models: parametric survival and when it beats Cox
- `04-survival-forests-and-boosted-survival-models.md` — Survival forests and boosted survival models: random survival forests and XGBoost survival objectives
- `05-survival-evaluation.md` — Survival evaluation: concordance index, time-dependent AUC, integrated Brier score and horizon calibration
- `06-competing-risks-and-recurrent-events.md` — Competing risks and recurrent events: cause-specific hazards and cumulative incidence introduction
- `07-positive-unlabeled-learning.md` — Positive-unlabeled learning: SCAR assumption, class-prior estimation and nnPU-style training
- `08-learning-with-noisy-labels.md` — Learning with noisy labels: noise models and confident learning with cleanlab
- `09-selection-bias-in-labels.md` — Selection bias in labels: reject inference, inverse-propensity label weighting and missing-not-at-random outcomes
- `10-label-quality-audit-protocol.md` — Label-quality audit protocol: a repeatable checklist for tabular datasets before modeling

**Hands-on projects**

- **Project 1: survival models on whas500 and rossi**  
  - Data: WHAS500 (scikit-survival) and Rossi recidivism (lifelines)  
  - Task: Fit Cox, AFT, random survival forest and boosted survival models; compare with a naive classifier that ignores censoring.  
  - Deliverables: Evaluation table (C-index, time-dependent AUC, IBS), calibration-at-horizon plots, short interpretation memo.  
  - Pass gate: Naive classifier is shown to be biased by censoring with a quantified gap; calibration checked at two or more horizons.
- **Project 2: pu learning from hidden positives**  
  - Data: UCI Adult or Covertype converted to a PU problem by hiding 70 percent of positives  
  - Task: Estimate the class prior, train PU classifiers and compare with naive positive-vs-unlabeled training.  
  - Deliverables: Experiment grid over label frequency, prior-estimation error analysis, recommendation on when PU is safe.  
  - Pass gate: PU method recovers at least the naive baseline at all label frequencies and degrades predictably when SCAR is violated.
- **Project 3: label noise injection and recovery with cleanlab**  
  - Data: UCI Adult with synthetic symmetric and class-conditional noise at known rates  
  - Task: Inject noise, detect suspect labels with confident learning, retrain on cleaned data and measure real gains against ground truth.  
  - Deliverables: Precision/recall of detected label issues, before/after metrics, label-quality audit report.  
  - Pass gate: Detection precision measured against known flipped labels; improvement reported with a confidence interval, including cases where cleaning hurts.

### 03 — Advanced Gradient Boosting Engineering

**Outcome:** Understand gradient boosting well enough to customize objectives, control variance, use accelerators and ship compact fast tree models.

**Lessons**

- `01-histogram-splits.md` — Histogram splits: binning, leaf-wise vs level-wise growth and split-finding internals
- `02-newton-boosting.md` — Newton boosting: gradients, Hessians and second-order updates
- `03-custom-objectives-and-metrics.md` — Custom objectives and metrics: writing gradient and Hessian functions in XGBoost, LightGBM and CatBoost
- `04-non-gaussian-objectives.md` — Non-Gaussian objectives: Poisson, Tweedie, Gamma, quantile and expectile boosting
- `05-catboost-internals.md` — CatBoost internals: ordered boosting and ordered target statistics vs LightGBM categorical splits
- `06-lightgbm-options.md` — LightGBM options: GOSS, exclusive feature bundling, linear trees and DART
- `07-regularization-playbook.md` — Regularization playbook: interaction of learning rate, tree count, leaves, minimum child weight and subsampling
- `08-early-stopping-and-seed-variance.md` — Early stopping and seed variance: reporting boosted-model results honestly
- `09-gpu-boosting.md` — GPU boosting: when GPU training helps and when it does not
- `10-tree-ensemble-compilation.md` — Tree-ensemble compilation: Treelite, Hummingbird, ONNX-ML and GPU forest inference
- `11-model-size-reduction.md` — Model size reduction: tree pruning, leaf quantization and distilling a large ensemble

**Hands-on projects**

- **Project 1: gradient boosting from scratch**  
  - Data: California Housing (regression) and Adult (classification)  
  - Task: Implement histogram-based gradient boosting with squared and logistic loss in NumPy; match scikit-learn HistGradientBoosting.  
  - Deliverables: Tested implementation, comparison plots, notes on every point where results diverge and why.  
  - Pass gate: Predictions agree with scikit-learn within a documented tolerance; unit tests cover split finding and leaf values.
- **Project 2: asymmetric business loss with custom objectives**  
  - Data: California Housing with a stated cost of under-prediction vs over-prediction  
  - Task: Derive gradient and Hessian for an asymmetric loss, implement in XGBoost and LightGBM, compare with quantile and plain MSE models.  
  - Deliverables: Derivation, implementation, cost-weighted evaluation table.  
  - Pass gate: Custom objective lowers expected business cost against MSE with a confidence interval; gradient check passes numerically.
- **Project 3: tree inference compilation benchmark**  
  - Data: A trained XGBoost and LightGBM model on Covertype  
  - Task: Benchmark native predict, Treelite, Hummingbird and ONNX runtimes on latency, throughput and memory across batch sizes.  
  - Deliverables: Benchmark harness, results table, deployment recommendation by batch size.  
  - Pass gate: Every compiled model is checked for prediction equivalence to the native model before timing.

### 04 — Advanced Feature Engineering and Tabular Representation

**Outcome:** Go beyond hand-built transformations: automated and relational features, learned interactions, embeddings and disciplined feature selection.

**Lessons**

- `01-deep-feature-synthesis.md` — Deep feature synthesis: automated feature generation with Featuretools
- `02-multi-table-feature-engineering.md` — Multi-table feature engineering: aggregating over relational entities with point-in-time-correct joins
- `03-interaction-discovery.md` — Interaction discovery: GBDT-leaf features, factorization machines and learned crosses
- `04-entity-embeddings.md` — Entity embeddings: dense representations of high-cardinality categoricals reused in tree models
- `05-numerical-embeddings.md` — Numerical embeddings: piecewise-linear encoding, quantile bins and periodic features
- `06-out-of-fold-feature-frameworks.md` — Out-of-fold feature frameworks: nested OOF encodings and meta-features
- `07-advanced-feature-selection.md` — Advanced feature selection: Boruta, null importance, stability selection and SHAP-based selection
- `08-text-plus-tabular-models.md` — Text-plus-tabular models: combining TF-IDF or sentence-embedding signals with GBDT
- `09-feature-ablation-by-group.md` — Feature ablation by group: cost-aware selection and feature retirement
- `10-feature-gain-accounting.md` — Feature gain accounting: measuring gain against complexity and maintenance cost

**Hands-on projects**

- **Project 1: multi table credit features with home credit**  
  - Data: Home Credit Default Risk multi-table data (Kaggle; accept competition rules)  
  - Task: Build features from bureau, previous applications and installments tables manually and with Featuretools; compare under identical validation.  
  - Deliverables: Feature pipeline with point-in-time checks, ablation by table, gain-vs-cost table.  
  - Pass gate: No leakage across the application date (verified by a test); each added table justified by validated gain.
- **Project 2: feature selection method shootout**  
  - Data: Synthetic data with known informative features plus three real OpenML tabular datasets  
  - Task: Compare Boruta, null importance, stability selection, SHAP-based and filter methods on recovery of true features and downstream accuracy.  
  - Deliverables: Recovery precision/recall on synthetic data, downstream accuracy on real data, runtime table.  
  - Pass gate: Selected-feature sets reported with stability across resamples, not a single run.
- **Project 3: text plus tabular price model**  
  - Data: Inside Airbnb listings with description text  
  - Task: Combine TF-IDF/sentence-embedding signals with tabular features in a GBDT using OOF text predictions.  
  - Deliverables: Pipeline, ablation (tabular only, text only, combined), leakage test for OOF text features.  
  - Pass gate: OOF construction proven leak-free; combined model improves on best single-source model with a confidence interval.

### 05 — Ensembling Stacking and Model Combination at Depth

**Outcome:** Combine models in a principled, leakage-safe way and know when the added cost is not worth it.

**Lessons**

- `01-why-ensembles-work.md` — Why ensembles work: error-ambiguity decomposition and diversity measures
- `02-oof-prediction-protocol.md` — OOF prediction protocol: generating and analyzing out-of-fold predictions and model correlation
- `03-multi-level-stacking.md` — Multi-level stacking: leakage-safe folds and meta-learner choice
- `04-greedy-ensemble-selection.md` — Greedy ensemble selection: Caruana selection and constrained weight optimization
- `05-averaging-schemes.md` — Averaging schemes: rank, probability and logit averaging, and ensembling for ranking metrics
- `06-diversity-sources.md` — Diversity sources: seeds, feature views, algorithms and resampling schemes
- `07-ensembles-under-group-and-time-aware-validation.md` — Ensembles under group and time-aware validation: common failure patterns
- `08-ensemble-calibration.md` — Ensemble calibration: probability quality and uncertainty of combined models
- `09-cost-of-ensembles.md` — Cost of ensembles: latency, memory, maintenance and where to stop
- `10-ensemble-distillation.md` — Ensemble distillation: compressing an ensemble into one deployable model

**Hands-on projects**

- **Project 1: multi level stacking pipeline**  
  - Data: Covertype or a chosen OpenML-CC18 dataset  
  - Task: Build a leakage-safe two-level stack, run an ablation of each level and compare with greedy ensemble selection.  
  - Deliverables: Pipeline, OOF correlation matrix, ablation table, cost table.  
  - Pass gate: Stack beats best single model with a confidence interval or the report states plainly that it did not.
- **Project 2: ensemble distillation study**  
  - Data: The ensemble from the previous project  
  - Task: Distill into a single GBDT and a linear model using soft targets; compare accuracy, latency and size.  
  - Deliverables: Distillation pipeline and Pareto plot of accuracy vs latency vs size.  
  - Pass gate: Distilled model's gap to the teacher is quantified and the deployment choice is justified.
- **Project 3: leaky stacking reproduction and fix**  
  - Data: Any tabular dataset with a time or group column  
  - Task: Deliberately build a leaky stack, show inflated validation scores, then fix it with group- or time-aware folds.  
  - Deliverables: Before/after report and a regression test that fails on the leaky version.  
  - Pass gate: Test reliably detects the leak; inflated and honest scores both reported.

### 06 — Interpretable and Glass Box Models

**Outcome:** Build models whose logic can be read, audited and explained to a regulator or a customer, without defaulting to a black box.

**Lessons**

- `01-glass-box-rationale.md` — Glass-box rationale: regulated decisions, sparsity and the accuracy-interpretability trade-off
- `02-generalized-additive-models.md` — Generalized additive models: splines and shape functions with pyGAM
- `03-explainable-boosting-machines.md` — Explainable Boosting Machines: interaction terms and global and local explanations with InterpretML
- `04-optimal-binning.md` — Optimal binning: weight of evidence and information value with OptBinning
- `05-logistic-scorecards.md` — Logistic scorecards: points scaling, points-to-double-odds, score bands and stability monitoring with PSI
- `06-rule-based-models.md` — Rule-based models: decision lists, RuleFit and the imodels library
- `07-sparse-integer-risk-scores.md` — Sparse integer risk scores: RiskSLIM-style and clinical scoring systems
- `08-monotonic-and-constrained-models-as-glass-box-compromises.md` — Monotonic and constrained models as glass-box compromises
- `09-adverse-action-reason-codes.md` — Adverse-action reason codes: documenting decision explanations
- `10-the-rashomon-effect.md` — The Rashomon effect: many equally accurate models and choosing the interpretable one

**Hands-on projects**

- **Project 1: credit scorecard with reason codes**  
  - Data: UCI Default of Credit Card Clients (Taiwan) or UCI German Credit  
  - Task: Build a WOE-binned logistic scorecard with scaled points, PSI monitoring and reason codes; compare with a GBDT.  
  - Deliverables: Scorecard table, reason-code generator, PSI report, accuracy gap analysis.  
  - Pass gate: Every reason code traces to scorecard points; PSI computed between development and a later holdout.
- **Project 2: ebm vs gbdt vs gam benchmark**  
  - Data: Five OpenML tabular datasets  
  - Task: Benchmark EBM, GAM, GBDT and logistic regression; audit EBM shape functions for implausible patterns.  
  - Deliverables: Benchmark table with confidence intervals and shape-function audit notes.  
  - Pass gate: Interpretability cost (accuracy gap) is stated per dataset, not averaged away.
- **Project 3: sparse integer risk score for heart disease**  
  - Data: UCI Heart Disease (Cleveland)  
  - Task: Build a small integer-coefficient risk score and validate its calibration and discrimination.  
  - Deliverables: Score card, calibration plot, comparison with logistic regression and GBDT.  
  - Pass gate: Score uses a fixed maximum number of integer points and is checked for calibration, not only AUC.

### 07 — Deep Learning and Foundation Models for Tabular Data

**Outcome:** Know when neural and pretrained models beat or complement boosted trees on tabular data, and prove it with fair benchmarks.

**Lessons**

- `01-evidence-review.md` — Evidence review: when deep learning helps on tabular data and what the benchmarks show
- `02-strong-mlp-baselines.md` — Strong MLP baselines: regularization, embeddings and ensembling in practice
- `03-numerical-feature-embeddings.md` — Numerical feature embeddings: periodic and piecewise-linear embeddings for deep tabular models
- `04-attention-based-tabular-models.md` — Attention-based tabular models: FT-Transformer and SAINT
- `05-tabnet-and-node.md` — TabNet and NODE: sparse attention and differentiable trees
- `06-tabm.md` — TabM: parameter-efficient ensembling of MLPs
- `07-retrieval-based-tabular-models.md` — Retrieval-based tabular models: TabR and nearest-neighbor ideas
- `08-self-supervised-pretraining-for-tabular-data.md` — Self-supervised pretraining for tabular data: VIME and SCARF
- `09-in-context-tabular-foundation-models.md` — In-context tabular foundation models: TabPFN capabilities, size limits and license checks
- `10-decision-guide.md` — Decision guide: GBDT vs deep tabular vs foundation model vs AutoML

**Hands-on projects**

- **Project 1: tabular benchmark harness**  
  - Data: A subset of OpenML-CC18 and the Grinsztajn et al. tabular benchmark datasets  
  - Task: Compare CatBoost, LightGBM, tuned MLP, FT-Transformer, TabM and TabPFN with matched tuning budgets; aggregate with rank statistics and a critical-difference analysis.  
  - Deliverables: Reusable harness, results database, rank plot, decision guide.  
  - Pass gate: Equal tuning budget per model; seeds and splits logged; datasets where TabPFN limits apply are excluded or flagged.
- **Project 2: small data learning curves**  
  - Data: Three datasets sampled from 100 to 50,000 rows  
  - Task: Plot learning curves for each model family to find crossover points between methods.  
  - Deliverables: Learning-curve figure and a rule of thumb for model choice by data size.  
  - Pass gate: Each curve uses repeated sampling with confidence bands.
- **Project 3: self supervised pretraining with few labels**  
  - Data: A tabular dataset with 5, 10 and 20 percent of labels retained  
  - Task: Compare supervised-only training with SCARF-style pretraining then fine-tuning.  
  - Deliverables: Experiment report with label-fraction sweep.  
  - Pass gate: Result is compared with a tuned GBDT trained on the same labeled subset.

### 08 — Scaling Tabular ML Beyond a Single Machine Core

**Outcome:** Train tabular models on data larger than memory using GPUs and clusters, with a cost-aware view of when scale is justified. Spark MLlib, Dask DataFrames and Polars are already covered in earlier stages and are not repeated.

**Lessons**

- `01-how-much-data-do-you-need.md` — How much data do you need: learning curves and subsampling strategies
- `02-external-memory-boosting.md` — External-memory boosting: out-of-core training with XGBoost and LightGBM
- `03-distributed-boosting.md` — Distributed boosting: XGBoost on Dask and Ray
- `04-dask-ml-and-joblib.md` — Dask-ML and joblib: parallel scikit-learn pipelines
- `05-gpu-data-science.md` — GPU data science: RAPIDS cuDF and cuML
- `06-distributed-hyperparameter-search.md` — Distributed hyperparameter search: scheduling trials across workers
- `07-cost-performance-benchmarking.md` — Cost-performance benchmarking: CPU vs GPU vs cluster
- `08-scaling-pitfalls.md` — Scaling pitfalls: skew, shuffle cost, nondeterminism and reproducibility

**Hands-on projects**

- **Project 1: train on data larger than memory**  
  - Data: NYC Taxi trip records (multiple years) or an Avazu/Criteo click-log sample  
  - Task: Train the same model with subsampling, external memory and distributed boosting; compare cost, time and accuracy.  
  - Deliverables: Benchmark report with cost per experiment and recommended strategy.  
  - Pass gate: Subsampling baseline learning curve shows whether more data actually helps before scaling.
- **Project 2: cpu vs gpu cost report**  
  - Data: A mid-size tabular dataset (1 to 10 million rows)  
  - Task: Compare CPU, single GPU and cluster training on time, cost and run-to-run variance.  
  - Deliverables: Cost/performance table and decision rule.  
  - Pass gate: Costs computed from stated hourly prices with sources and dates.

### 09 — Applied ML Problem Discovery and Scoping

**Outcome:** Turn a vague business pain point into a scoped, valued and feasible ML project, or decide not to build it. Problem framing basics and 'when not to use ML' are covered in Stage 5A; this module covers the discovery and value work around them.

**Lessons**

- `01-decision-mapping.md` — Decision mapping: from a business pain point to the decision a model would change
- `02-opportunity-assessment.md` — Opportunity assessment: feasibility, data readiness, actionability and risk scorecard
- `03-ml-canvas-and-stakeholder-interview-protocol.md` — ML canvas and stakeholder interview protocol
- `04-success-metric-trees.md` — Success-metric trees: linking model metrics to operational and financial KPIs
- `05-label-and-outcome-design.md` — Label and outcome design: proxy labels, observation windows and label delay
- `06-estimating-value-before-building.md` — Estimating value before building: expected-value models, break-even and ROI
- `07-build-vs-buy-vs-rules-vs-analytics.md` — Build vs buy vs rules vs analytics: choosing the simplest solution that works
- `08-data-audit-for-applied-projects.md` — Data audit for applied projects: access, lineage, consent and legal constraints including the DPDP Act
- `09-scoping-documents-milestones-and-uncertainty-aware-estimation.md` — Scoping documents, milestones and uncertainty-aware estimation
- `10-ethics-and-harm-screening-at-scoping-time.md` — Ethics and harm screening at scoping time

**Hands-on projects**

- **Project 1: three case scoping packets**  
  - Data: Three fictional but realistic cases: retail demand returns, bank early collections, logistics delays  
  - Task: Run the opportunity assessment and write a scoping packet and go/no-go recommendation for each.  
  - Deliverables: Three packets with canvas, metric tree, data audit and decision.  
  - Pass gate: At least one case ends in a justified no-go or non-ML recommendation.
- **Project 2: roi model with sensitivity analysis**  
  - Data: Assumptions from the chosen case  
  - Task: Build an ROI model with break-even point and a sensitivity analysis over uncertain inputs.  
  - Deliverables: Notebook or sheet with tornado chart and plain-language summary.  
  - Pass gate: Every input has a source or is marked as an assumption with a range.
- **Project 3: churn label definition study**  
  - Data: Telco Customer Churn and Online Retail II  
  - Task: Show how different churn definitions and observation windows change prevalence, model quality and business meaning.  
  - Deliverables: Comparison table and recommended definition with reasoning.  
  - Pass gate: Study demonstrates sensitivity of results to definition choice.

### 10 — Decision Focused Evaluation and Pilots

**Outcome:** Evaluate models by the decisions and money they influence and design pilots that prove impact. Basic metric selection and alert capacity are covered in Stages 5A and 5B and are not repeated.

**Lessons**

- `01-lift-gain-ks-gini-and-decile-analysis.md` — Lift, gain, KS, Gini and decile analysis
- `02-profit-curves.md` — Profit curves: cost-benefit matrices and budget-constrained targeting
- `03-offline-to-business-translation.md` — Offline-to-business translation: expected impact with confidence intervals
- `04-pilot-design.md` — Pilot design: control groups, holdouts, power analysis and run length
- `05-silent-launch-and-phased-business-evaluation.md` — Silent launch and phased business evaluation: measuring impact rather than release safety
- `06-human-in-the-loop-analysis.md` — Human-in-the-loop analysis: overrides, acceptance rates and automation bias
- `07-decision-environment-drift.md` — Decision-environment drift: when the business process changes under the model
- `08-executive-reporting.md` — Executive reporting: one-page model readouts and honest uncertainty

**Hands-on projects**

- **Project 1: campaign targeting simulator**  
  - Data: UCI Bank Marketing  
  - Task: Simulate budgeted campaign targeting; choose the contact fraction that maximizes profit under stated costs.  
  - Deliverables: Profit curve, decile table and recommendation.  
  - Pass gate: Optimal fraction reported with a confidence interval from resampling.
- **Project 2: pilot power analysis and readout**  
  - Data: Simulated customer outcomes with a known effect size  
  - Task: Design a pilot with power analysis, run it in simulation and write the readout, including a case where the pilot is inconclusive.  
  - Deliverables: Design document, simulation code and readout.  
  - Pass gate: Readout states clearly what the data can and cannot conclude.
- **Project 3: executive model readout**  
  - Data: Output of the campaign project  
  - Task: Produce a one-page readout that a non-technical executive can act on.  
  - Deliverables: One-page PDF plus an appendix for analysts.  
  - Pass gate: A reviewer unfamiliar with the project can state the decision and its risks after reading it.

### 11 — Applied Customer and Marketing ML

**Outcome:** Solve the standard customer-analytics problems: segmentation, churn, lifetime value, propensity, marketing mix and pricing. Uplift modeling and experimentation methods are covered in Stage 5B and are not repeated.

**Lessons**

- `01-behavioral-segmentation.md` — Behavioral segmentation: RFM and designing segments that people can act on
- `02-churn-modeling-in-practice.md` — Churn modeling in practice: contractual vs non-contractual settings and survival-based churn
- `03-customer-lifetime-value.md` — Customer lifetime value: BG/NBD, Pareto/NBD and Gamma-Gamma models
- `04-ml-based-lifetime-value.md` — ML-based lifetime value: regression and value-tier targeting
- `05-propensity-and-lead-scoring.md` — Propensity and lead scoring: calibration for sales workflows
- `06-next-best-action.md` — Next-best-action: offer selection with constraints
- `07-marketing-mix-modeling.md` — Marketing mix modeling: adstock, saturation and Bayesian MMM with PyMC-Marketing, Meridian and Robyn
- `08-price-and-promotion-elasticity.md` — Price and promotion elasticity: modeling with causal caveats
- `09-customer-data-pitfalls.md` — Customer-data pitfalls: identity resolution, consent, privacy and survivorship bias

**Hands-on projects**

- **Project 1: customer lifetime value on cdnow and online retail ii**  
  - Data: CDNOW sample and UCI Online Retail II  
  - Task: Fit BG/NBD with Gamma-Gamma and an ML CLV model; compare on a held-out future window.  
  - Deliverables: Calibration plots of expected vs actual purchases and a value-tier action plan.  
  - Pass gate: Evaluation uses a true future holdout, not a random split.
- **Project 2: churn and survival on telco**  
  - Data: IBM Telco Customer Churn  
  - Task: Compare classification-based churn with survival-based time-to-churn and produce a retention-targeting policy.  
  - Deliverables: Model comparison and targeting policy with costs.  
  - Pass gate: Policy evaluated by expected profit, not AUC alone.
- **Project 3: marketing mix model with known ground truth**  
  - Data: Synthetic multi-channel spend and sales data generated with known adstock and saturation  
  - Task: Fit Bayesian MMM and check whether it recovers the true channel effects; test with collinear spend.  
  - Deliverables: Parameter-recovery report and budget-allocation recommendation with uncertainty.  
  - Pass gate: Recovery error reported; limits under collinearity stated.
- **Project 4: price elasticity study**  
  - Data: Retail scanner data such as Dominick's Finer Foods (Kilts Center) or a simulated equivalent  
  - Task: Estimate elasticity with and without confounder controls and discuss bias.  
  - Deliverables: Elasticity estimates, sensitivity analysis and caveats memo.  
  - Pass gate: Naive and adjusted estimates compared explicitly.

### 12 — Applied Operations ML and Entity Resolution

**Outcome:** Apply ML to queues, delays and messy enterprise records, including matching and deduplicating records across systems.

**Lessons**

- `01-predictive-triage.md` — Predictive triage: prioritizing tickets, leads and work queues under capacity
- `02-operational-risk-prediction.md` — Operational risk prediction: delay, return and cancellation models
- `03-entity-resolution-fundamentals.md` — Entity resolution fundamentals: blocking, comparison and the Fellegi-Sunter model
- `04-probabilistic-record-linkage-with-splink.md` — Probabilistic record linkage with Splink
- `05-learned-matching.md` — Learned matching: string similarity, embeddings and supervised pair classifiers
- `06-deduplication-and-master-data.md` — Deduplication and master data: clustering matched records
- `07-messy-enterprise-extracts.md` — Messy enterprise extracts: turning ERP, CRM and spreadsheet data into model-ready tables
- `08-matching-evaluation.md` — Matching evaluation: pairwise vs cluster metrics and review queues
- `09-operating-applied-models.md` — Operating applied models: service levels, exception handling and fallbacks to business rules

**Hands-on projects**

- **Project 1: splink deduplication on historical and febrl data**  
  - Data: Splink historical_50k demo data and Febrl datasets from the recordlinkage package  
  - Task: Block, compare and link records with Splink; evaluate against known truth and tune thresholds.  
  - Deliverables: Linkage pipeline, pairwise and cluster metrics, review-queue design.  
  - Pass gate: Blocking recall measured separately from final matching quality.
- **Project 2: complaint triage priority queue**  
  - Data: CFPB Consumer Complaint Database  
  - Task: Build a triage model that ranks complaints for review under a daily capacity.  
  - Deliverables: Ranking model, capacity simulation and fallback rules.  
  - Pass gate: Evaluated by captured high-priority cases within capacity.
- **Project 3: messy erp extract cleaning project**  
  - Data: A simulated ERP and CRM extract generated with documented defects  
  - Task: Clean, join and model data containing duplicates, mixed units and inconsistent keys.  
  - Deliverables: Documented cleaning pipeline with a defect log and tests.  
  - Pass gate: Every injected defect is detected or explicitly accepted as a risk.

### 13 — Applied ML Delivery Communication and Stakeholder Practice

**Outcome:** Deliver ML work that people adopt: write the documents, build the prototypes and run the post-launch reviews. Model cards and operational runbooks are covered in Stage 5D and are not repeated.

**Lessons**

- `01-ml-design-documents-and-decision-memos.md` — ML design documents and decision memos
- `02-rapid-prototypes.md` — Rapid prototypes: Streamlit and Gradio apps for stakeholders
- `03-data-storytelling.md` — Data storytelling: explaining model behavior to non-technical audiences
- `04-ownership-and-handoff.md` — Ownership and handoff: roles between data science, engineering and business
- `05-value-tracking.md` — Value tracking: benefits realization and post-launch reviews
- `06-hidden-technical-debt-in-ml-systems.md` — Hidden technical debt in ML systems: finding and paying it down
- `07-managing-expectations.md` — Managing expectations: uncertainty, failure and ending projects early
- `08-case-study-writing.md` — Case-study writing: documenting applied ML work for a portfolio

**Hands-on projects**

- **Project 1: design document and decision memo**  
  - Data: One scoping packet from module 09  
  - Task: Write a design document and a one-page decision memo for the chosen use case.  
  - Deliverables: Two documents reviewed against a rubric.  
  - Pass gate: Documents state assumptions, risks and the explicit decision requested.
- **Project 2: stakeholder prototype with feedback loop**  
  - Data: A model from module 10 or 11  
  - Task: Build a Streamlit prototype that lets a stakeholder try inputs and record feedback.  
  - Deliverables: Working app and a feedback log schema.  
  - Pass gate: App shows model uncertainty and has a way to flag wrong outputs.
- **Project 3: post launch review simulation**  
  - Data: A simulated 90-day pilot history  
  - Task: Run a post-launch review comparing promised and realized value and decide continue, change or stop.  
  - Deliverables: Review document with benefits analysis.  
  - Pass gate: Decision is supported by the data, including a reasoned stop option.

### 14 — AutoML Foundations and Search Spaces

**Outcome:** Understand how AutoML systems are built: the CASH problem, search spaces, search strategies, meta-learning and benchmarking. Bayesian optimization and multi-fidelity tuning are introduced in Stage 5B; here they are implemented and extended.

**Lessons**

- `01-the-automl-problem.md` — The AutoML problem: CASH, pipeline synthesis and what can and cannot be automated
- `02-search-space-design.md` — Search-space design: conditional, hierarchical and pipeline-structured spaces
- `03-search-strategies.md` — Search strategies: random search, TPE, Gaussian-process search, SMAC and evolutionary search with TPOT
- `04-bandit-based-budget-allocation.md` — Bandit-based budget allocation: successive halving, Hyperband and BOHB
- `05-meta-learning-and-warm-starting.md` — Meta-learning and warm starting: meta-features, portfolios and zero-shot configurations
- `06-post-hoc-ensembling-and-stacking-inside-automl.md` — Post-hoc ensembling and stacking inside AutoML
- `07-budget-semantics.md` — Budget semantics: time limits, early stopping and resource accounting
- `08-automl-benchmarking.md` — AutoML benchmarking: OpenML-CC18, AMLB and fair comparison protocols

**Hands-on projects**

- **Project 1: hpo algorithms from scratch**  
  - Data: A tabular HPO benchmark such as HPOBench or a surrogate-based benchmark  
  - Task: Implement random search, a TPE-style sampler, successive halving and Hyperband; compare under equal budgets.  
  - Deliverables: Implementations, anytime-performance plots and ranking with confidence bands.  
  - Pass gate: All methods share the same evaluation budget and seeds.
- **Project 2: meta learning warm start study**  
  - Data: 20 or more OpenML datasets  
  - Task: Compute meta-features, build a configuration portfolio and measure warm-start benefit.  
  - Deliverables: Portfolio, leave-one-dataset-out evaluation and analysis.  
  - Pass gate: Evaluation excludes the target dataset from portfolio construction.
- **Project 3: search space design critique**  
  - Data: Search spaces of two public AutoML tools  
  - Task: Document each search space, find gaps and propose and test improvements.  
  - Deliverables: Critique with experiments.  
  - Pass gate: Claims backed by runs, not opinion.

### 15 — AutoML Frameworks and HPO Systems

**Outcome:** Use the main AutoML and HPO tools competently, customize them and audit what they did.

**Lessons**

- `01-optuna.md` — Optuna: samplers, pruners, storage backends, dashboard and distributed studies
- `02-ray-tune.md` — Ray Tune: ASHA and population-based training schedulers
- `03-smac3-hyperopt-and-keras-tuner-compared.md` — SMAC3, Hyperopt and Keras Tuner compared
- `04-autogluon-tabular.md` — AutoGluon-Tabular: bagging, multi-layer stacking and presets
- `05-flaml-h2o-automl-and-auto-sklearn.md` — FLAML, H2O AutoML and auto-sklearn: cost-frugal search and maintenance status checks
- `06-cloud-automl-services.md` — Cloud AutoML services: Vertex AI, SageMaker Autopilot and Azure AutoML
- `07-customizing-automl.md` — Customizing AutoML: custom models, metrics, constraints and feature pipelines
- `08-experiment-tracking.md` — Experiment tracking: integrating AutoML runs with MLflow from Stage 5D
- `09-automl-failure-modes.md` — AutoML failure modes: leakage, validation overfitting, time-series misuse and silent defaults
- `10-automl-governance.md` — AutoML governance: audit trail, explainability, human review and sign-off

**Hands-on projects**

- **Project 1: five framework comparison under equal budget**  
  - Data: Five OpenML tabular datasets  
  - Task: Run AutoGluon, FLAML, H2O AutoML, auto-sklearn (if installable) and an Optuna baseline with identical budgets.  
  - Deliverables: Comparison table, resource usage, reproducibility notes.  
  - Pass gate: Framework versions pinned; tools that fail to install are reported, not silently dropped.
- **Project 2: distributed multi objective optuna study**  
  - Data: A tabular dataset with a latency constraint  
  - Task: Run a distributed Optuna study optimizing accuracy and inference latency; track with MLflow.  
  - Deliverables: Pareto front and tracked runs.  
  - Pass gate: Study resumable from storage.
- **Project 3: automl audit with injected leakage**  
  - Data: A dataset with a deliberately injected leaky feature  
  - Task: Run an AutoML tool, then audit its output to find the leak and write the audit report.  
  - Deliverables: Audit report and a leakage check that can run on any AutoML output.  
  - Pass gate: Leak is found from the artifacts, not from prior knowledge.

### 16 — Build Your Own AutoML System

**Outcome:** Design and ship a small but honest AutoML system, which forces you to understand every moving part.

**Lessons**

- `01-automl-system-design.md` — AutoML system design: scope, interfaces and non-goals
- `02-data-profiling.md` — Data profiling: automatic task detection and data-quality warnings
- `03-preprocessing-generation.md` — Preprocessing generation: pipeline templates by column type
- `04-model-zoo-and-scheduler.md` — Model zoo and scheduler: search budget management
- `05-experiment-store.md` — Experiment store: leaderboard and artifact management
- `06-ensembling-and-final-model-selection.md` — Ensembling and final model selection
- `07-automatic-reports.md` — Automatic reports: explanations, caveats and warnings
- `08-serving-and-cli.md` — Serving and CLI: safe defaults and refusal rules for when AutoML should say no
- `09-testing-and-benchmarking.md` — Testing and benchmarking: comparing against framework baselines

**Hands-on projects**

- **Project 1: automl mvp**  
  - Data: OpenML-CC18 datasets  
  - Task: Build an MVP that takes a CSV and a target and returns a validated model and a report.  
  - Deliverables: Package, CLI, tests and sample reports.  
  - Pass gate: Runs end to end on at least 10 datasets without manual edits.
- **Project 2: automl benchmark against frameworks**  
  - Data: A held-out set of OpenML datasets  
  - Task: Benchmark your system against AutoGluon and FLAML under equal budgets.  
  - Deliverables: Benchmark report with honest gaps.  
  - Pass gate: Gaps explained with evidence.
- **Project 3: refusal and safety tests**  
  - Data: Synthetic datasets with leakage, constant targets, tiny samples and time order  
  - Task: Add tests where the system must warn or refuse.  
  - Deliverables: Test suite and documented refusal rules.  
  - Pass gate: System refuses or warns on every constructed bad case.

### 17 — Neural Architecture Search

**Outcome:** Understand NAS well enough to use it sparingly, evaluate it honestly and know when pretrained backbones are the better choice.

**Lessons**

- `01-nas-formulation.md` — NAS formulation: search space, search strategy and performance estimation
- `02-search-spaces.md` — Search spaces: cell-based, macro, hierarchical and tabular-network spaces
- `03-nas-benchmarks.md` — NAS benchmarks: NAS-Bench-101, NAS-Bench-201 and surrogate benchmarks
- `04-reinforcement-learning-and-evolutionary-nas.md` — Reinforcement-learning and evolutionary NAS: controllers and regularized evolution
- `05-one-shot-nas.md` — One-shot NAS: weight sharing, ENAS, SPOS and supernets
- `06-differentiable-nas.md` — Differentiable NAS: DARTS, its instabilities and fixes
- `07-cheap-performance-estimation.md` — Cheap performance estimation: low fidelity, learning-curve extrapolation and zero-cost proxies
- `08-hardware-aware-and-multi-objective-nas.md` — Hardware-aware and multi-objective NAS: latency tables, Once-for-All, MnasNet and Pareto fronts
- `09-nas-tooling.md` — NAS tooling: AutoKeras, Keras Tuner, Optuna-based search and tool maintenance checks
- `10-honest-nas-evaluation.md` — Honest NAS evaluation: random-search baselines, seed variance and compute accounting
- `11-when-not-to-use-nas.md` — When not to use NAS: pretrained backbones and transfer learning as the default

**Hands-on projects**

- **Project 1: nas bench 201 search strategy comparison**  
  - Data: NAS-Bench-201 (CIFAR-10 queries; no training required)  
  - Task: Compare random search, regularized evolution and a surrogate-based method under equal query budgets.  
  - Deliverables: Search-curve plots and ranking with many seeds.  
  - Pass gate: Random search included as a baseline; at least 20 seeds.
- **Project 2: darts instability reproduction**  
  - Data: A CIFAR-10 subset  
  - Task: Run DARTS, observe skip-connection collapse and test one published fix.  
  - Deliverables: Experiment report with architecture visualizations.  
  - Pass gate: Collapse measured, not asserted.
- **Project 3: hardware aware search under latency budget**  
  - Data: A small image dataset and a target CPU  
  - Task: Search small CNNs for the best accuracy under a measured latency budget and plot the Pareto front.  
  - Deliverables: Latency table, search code and Pareto plot.  
  - Pass gate: Latency measured on the target hardware, not estimated by FLOPs alone.

### 18 — G1 Capstones

**Outcome:** integrate the whole group in assessed, portfolio-quality work.

- **Capstone 1: tabular model benchmark and decision report** (uses Modules 03, 05, 07, 08)  
  Benchmark boosted trees, ensembles, deep tabular models and a foundation model on a chosen business dataset and write a model-choice decision report with costs.
- **Capstone 2: end to end applied business case** (uses Modules 02, 09, 10, 11, 13)  
  Take one business case from scoping through churn and lifetime-value models, a targeting policy, a pilot plan and an ROI model, ending with an executive readout.
- **Capstone 3: glass box scoring system with monitoring** (uses Modules 06, 10)  
  Build a regulated-style scoring system with scorecard, reason codes, PSI monitoring plan and a documented comparison with a black-box alternative.
- **Capstone 4: automl and nas engineering study** (uses Modules 14, 15, 16, 17)  
  Compare your own AutoML system with framework baselines and a NAS-lite experiment under identical compute budgets, with honest cost accounting.
- **Capstone 5: g1 readiness assessment** (uses All modules)  
  Written and practical assessment against the G1 completion gate.

## G1 completion gate

- Every module project has a written report with confidence intervals and a stated limitation.
- All results reproduce from a lockfile, a config file and logged seeds.
- At least one project in each of three areas (tabular engineering, applied business, AutoML or NAS) shows a negative or inconclusive result honestly reported.
- Benchmarks use matched tuning budgets and report rank statistics, not single-dataset wins.
- Capstone 5 readiness assessment passed.

## Audit and verification

**What was checked and the result**

- Structure: 17 specialist modules each have 6 to 12 lessons and at least one project; the tree contains 262 files and 37 folders, and these counts equal the counts computed from the curriculum data.
- Overlap with the Roadmap: all 161 lesson file names were compared against every lesson file name in `Roadmap.md`. Exact matches: 0. Near matches (similarity 0.80 or higher): 1 — `automl-system-design` vs Roadmap `production-ml-system-design` (0.81). Reviewed manually: the names are similar but the topics differ (AutoML system design here vs production serving architecture in Stage 5D), so there is no content overlap.
- Structural problems found by the build script: 0.
- Tools verified by web search on the build date (2026-10-26): TabM is an ICLR 2025 paper by Gorishniy, Kotelnikov and Babenko; TabPFN v2 was published in Nature in January 2025; Meridian is Google's open-source Bayesian marketing mix model released in January 2025, alongside Meta's Robyn and PyMC-Marketing.
- Not confirmed and flagged: the latest TabPFN version after 2.5 rests on a single secondary source; auto-sklearn's last PyPI release appears to be 0.15.0 from about 2023; the Microsoft NNI repository appears archived (September 2024) according to one source. Lessons 15-05 and 17-09 therefore require a maintenance check before use.
- Not verifiable here: dataset availability, licences and download locations change. The dataset register in `00-G1-Overview` must record each dataset's source URL and licence on the day it is first used.
- Not verified by execution: no code in this plan has been run. Project pass gates are acceptance criteria to be met when the projects are built.
- Repository safety: this build created only `ML_SPECIALIZATION.md`; no other file or folder was created, changed or deleted by it.
