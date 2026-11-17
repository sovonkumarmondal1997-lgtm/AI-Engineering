# Statistical Reasoning — ML Specialization Roadmap

**Group 7 (G7)** of the specialization that follows Stage 5D of the [Roadmap](./Roadmap.md). It covers original categories **15 Probabilistic Machine Learning and Uncertainty Quantification and 16 Causal Machine Learning**. The group's defining question is: *how sure are we, and what causes what?* It follows G1 to G6: [`01_Classical and Applied ML.md`](./01_Classical%20and%20Applied%20ML.md), [`02_Deep Learning by Modality.md`](./02_Deep%20Learning%20by%20Modality.md), [`03_Generative and Foundation Models.md`](./03_Generative%20and%20Foundation%20Models.md), [`04_Agents and Sequential Decisions.md`](./04_Agents%20and%20Sequential%20Decisions.md), [`05_Time and Anomaly Modeling.md`](./05_Time%20and%20Anomaly%20Modeling.md), [`06_Personalization Search and Matching.md`](./06_Personalization%20Search%20and%20Matching.md).

## G7 summary

| Item | Count |
|---|---|
| Modules (including overview and capstones) | 18 |
| Lesson files | 155 |
| Hands-on project files (module projects, overview project and capstones) | 54 |
| Folders inside the G7 tree | 35 |
| Files inside the G7 tree | 251 |

| Original category | Modules |
|---|---|
| Shared statistical foundation for both | 01 |
| 15 Probabilistic Machine Learning and Uncertainty Quantification | 02 to 09 |
| 16 Causal Machine Learning | 10 to 16 |

## Scope and how G7 avoids repeating the Roadmap

G7 starts where Stages 4B, 4C and 5B stop. These are **already learned** and are only referenced, never retaught: probability axioms, conditional probability, Bayes' theorem, random variables and common distributions, expectation, variance and covariance, the law of large numbers and the central limit theorem, confidence intervals, the bootstrap, hypothesis testing and p-values, t-tests, proportion tests and A/B testing, effect size, sample size and power, correlation versus causation (Stage 4B); joint, conditional and multivariate Gaussian distributions, change of variables, Monte Carlo and importance sampling, Markov chains, MCMC with Metropolis-Hastings and Gibbs sampling, likelihood and maximum likelihood, bias and variance of estimators, Fisher information, MAP estimation, Bayesian inference with conjugate priors, aleatoric and epistemic uncertainty and calibration concepts, the exponential family, EM and Gaussian mixtures, latent-variable models, the ELBO, VAEs, GANs and diffusion mathematics (Stage 4C); probabilistic classifiers, Bayesian linear and logistic regression in practice, ensembles and bootstrap for uncertainty, Gaussian processes for small data, split conformal prediction, conformalized quantile regression, abstention, calibration with reliability diagrams and the Brier score, Platt and temperature scaling, isotonic regression (Stage 5B); prediction versus causal inference, confounding and causal diagrams, treatment effects and selection bias, propensity scores, matching and weighting, difference-in-differences and synthetic control, uplift and heterogeneous treatment effects, instrumental variables and regression discontinuity introductions, CUPED and sequential testing, bandits and off-policy evaluation (Stage 5B); survival analysis (G1), OOD detection (G2), adaptive conformal prediction for time series (G5) and slate off-policy evaluation (G6).

**Boundaries with other groups** (so nothing overlaps): reinforcement-learning algorithms belong to **G4**; time-series modeling beyond the references above belongs to **G5**; graph-based inference belongs to **G8**; fairness, privacy and adversarial robustness methods belong to **G12**; general benchmark and evaluation-system design belongs to **G13**; healthcare, finance and other regulated domain applications belong to **G9**.

| Roadmap topic already covered | Where G7 goes further |
|---|---|
| Hypothesis tests, bootstrap, power (4B) | Module 01: multiple testing, permutation tests, clustered inference, p-hacking and meta-analysis |
| Bayes, conjugate priors, MCMC theory (4B, 4C) | Modules 02 and 03: Bayesian workflow in code, diagnostics, hierarchical models and MRP |
| Metropolis-Hastings, Gibbs, ELBO (4C) | Module 04: HMC and NUTS behavior, flow-based VI, ABC and neural simulation-based inference |
| Gaussian processes for small data (5B) | Module 05: kernel design, scalable GPs and Bayesian optimization practice |
| Ensembles and bootstrap uncertainty, calibration (5B) | Module 06: MC dropout, deep ensembles, Laplace methods and LLM uncertainty |
| Split conformal and CQR (5B) | Module 07: jackknife+, APS and RAPS, Mondrian, weighted and risk-controlling conformal |
| Reliability diagrams, Brier score, expected-cost thresholds (5B) | Module 08: proper scoring, calibration-metric flaws, value of information and CVaR |
| EM, Gaussian mixtures and VAE math (4C) | Module 09: LDA, Poisson factorization, Dirichlet processes and copulas |
| Causal diagrams and selection bias (5B) | Module 10: do-calculus, identification, mediation, counterfactuals and target trial emulation |
| Propensity scores, matching and weighting (5B) | Module 11: overlap, doubly robust, TMLE, double ML and sensitivity analysis |
| Uplift and HTE (5B) | Module 12: meta-learners, causal forests, CATE evaluation and policy learning |
| DiD, synthetic control, IV and RDD introductions (5B) | Module 13: staggered adoption, event studies, RD in practice and robust inference |
| CUPED and sequential testing (5B), A/B tests (4B) | Module 14: SRM, ratio metrics, interference, switchbacks, geo and marketplace experiments |
| Selection bias and graphs (5B), graph algorithms (Stage 3) | Module 15: causal discovery, causal RCA and causal analysis with text |

## G7 — Statistical Reasoning

**Defining question:** How sure are we, and what causes what?

```text
ML Specialization/
└── G7 — Statistical Reasoning/
    ├── 00-G7-Overview/
    │   ├── Projects/
    │   │   ├── 01-g7-probabilistic-and-causal-simulation-bootstrap.md
    │   │   └── README.md
    │   ├── 01-g7-scope-and-boundaries-with-stage-4-5b-and-other-groups.md
    │   ├── 02-prerequisite-map-from-the-roadmap.md
    │   ├── 03-dataset-and-tooling-register.md
    │   ├── 04-evaluation-and-reporting-standards.md
    │   ├── 05-completion-gate.md
    │   ├── README.md
    │   └── learning-plan.md
    ├── 01-Applied-Statistical-Inference-for-ML-Practitioners/
    │   ├── Projects/
    │   │   ├── 01-multiple-testing-simulation-and-correction.md
    │   │   ├── 02-clustered-data-analysis.md
    │   │   ├── 03-p-hacking-demonstration-and-preregistered-analysis.md
    │   │   └── README.md
    │   ├── 01-multiple-testing.md
    │   ├── 02-multiplicity-in-ml-work.md
    │   ├── 03-permutation-and-randomization-tests.md
    │   ├── 04-nonparametric-tests.md
    │   ├── 05-robust-and-clustered-standard-errors.md
    │   ├── 06-multilevel-data-and-mixed-effects-models-in-the-frequentist-framework.md
    │   ├── 07-model-diagnostics-and-misspecification.md
    │   ├── 08-researcher-degrees-of-freedom.md
    │   ├── 09-meta-analysis.md
    │   ├── 10-frequentist-or-bayesian-reporting.md
    │   └── README.md
    ├── 02-Bayesian-Workflow-and-Probabilistic-Programming/
    │   ├── Projects/
    │   │   ├── 01-full-bayesian-workflow-on-a-real-dataset.md
    │   │   ├── 02-prior-sensitivity-study.md
    │   │   ├── 03-ppl-comparison.md
    │   │   └── README.md
    │   ├── 01-probabilistic-programming-languages.md
    │   ├── 02-specifying-models.md
    │   ├── 03-prior-predictive-checks.md
    │   ├── 04-mcmc-diagnostics.md
    │   ├── 05-posterior-predictive-checks.md
    │   ├── 06-model-comparison.md
    │   ├── 07-prior-sensitivity-analysis-and-robustness-of-conclusions.md
    │   ├── 08-reparameterization-for-geometry.md
    │   ├── 09-the-bayesian-workflow-as-an-iterative-process-and-documenting-it.md
    │   ├── 10-tooling.md
    │   └── README.md
    ├── 03-Hierarchical-and-Multilevel-Bayesian-Models/
    │   ├── Projects/
    │   │   ├── 01-partial-pooling-for-many-small-groups.md
    │   │   ├── 02-hierarchical-ab-testing-across-experiments.md
    │   │   ├── 03-mrp-survey-estimation.md
    │   │   └── README.md
    │   ├── 01-partial-pooling.md
    │   ├── 02-varying-intercepts-and-slopes-with-correlated-random-effects.md
    │   ├── 03-hierarchical-bayesian-a-b-testing-and-many-experiment-shrinkage.md
    │   ├── 04-small-area-estimation-and-multilevel-regression-with-poststratification.md
    │   ├── 05-bayesian-generalized-linear-models.md
    │   ├── 06-measurement-error-and-missing-data-models.md
    │   ├── 07-rating-and-comparison-models.md
    │   ├── 08-bayesian-survival-and-censored-data-models.md
    │   ├── 09-checking-hierarchical-models.md
    │   └── README.md
    ├── 04-Advanced-Inference-Algorithms-and-Simulation-Based-Inference/
    │   ├── Projects/
    │   │   ├── 01-nuts-vs-vi-vs-laplace-accuracy-study.md
    │   │   ├── 02-simulation-based-inference-for-a-simulator.md
    │   │   ├── 03-funnel-and-reparameterization-lab.md
    │   │   └── README.md
    │   ├── 01-hamiltonian-monte-carlo-and-nuts.md
    │   ├── 02-posterior-geometry-pathologies.md
    │   ├── 03-stochastic-variational-inference-and-automatic-differentiation-vi-with-numpyro-and-pyro.md
    │   ├── 04-richer-variational-families.md
    │   ├── 05-laplace-approximations-and-when-they-are-enough.md
    │   ├── 06-sequential-monte-carlo-and-particle-methods.md
    │   ├── 07-approximate-bayesian-computation-for-simulator-models.md
    │   ├── 08-neural-simulation-based-inference.md
    │   ├── 09-validating-inference.md
    │   ├── 10-scaling-bayesian-inference.md
    │   └── README.md
    ├── 05-Gaussian-Processes-and-Bayesian-Optimization-in-Practice/
    │   ├── Projects/
    │   │   ├── 01-gp-kernel-design-on-real-series.md
    │   │   ├── 02-scalable-gp-vs-gbdt-with-uncertainty.md
    │   │   ├── 03-bayesian-optimization-for-an-expensive-simulator.md
    │   │   └── README.md
    │   ├── 01-kernel-design.md
    │   ├── 02-hyperparameter-learning-and-the-marginal-likelihood.md
    │   ├── 03-scalable-gaussian-processes.md
    │   ├── 04-non-gaussian-likelihoods-and-classification-with-gps.md
    │   ├── 05-multi-output-and-multi-fidelity-gps.md
    │   ├── 06-deep-kernel-learning-and-when-it-overfits.md
    │   ├── 07-bayesian-optimization-in-practice.md
    │   ├── 08-multi-objective-and-high-dimensional-bayesian-optimization.md
    │   ├── 09-where-gps-fail.md
    │   └── README.md
    ├── 06-Neural-Network-and-LLM-Uncertainty/
    │   ├── Projects/
    │   │   ├── 01-deep-uncertainty-method-comparison.md
    │   │   ├── 02-llm-confidence-calibration-study.md
    │   │   ├── 03-selective-prediction-system.md
    │   │   └── README.md
    │   ├── 01-aleatoric-and-epistemic-uncertainty-in-deep-regression.md
    │   ├── 02-monte-carlo-dropout-and-its-limits.md
    │   ├── 03-deep-ensembles.md
    │   ├── 04-weight-space-approximations.md
    │   ├── 05-last-layer-bayesian-methods-and-evidential-approaches-with-their-critiques.md
    │   ├── 06-selective-prediction.md
    │   ├── 07-uncertainty-under-dataset-shift.md
    │   ├── 08-language-model-confidence.md
    │   ├── 09-semantic-entropy-and-hallucination-detection.md
    │   ├── 10-calibration-and-abstention-for-llm-systems.md
    │   └── README.md
    ├── 07-Conformal-Prediction-and-Distribution-Free-Guarantees/
    │   ├── Projects/
    │   │   ├── 01-conformal-classification-with-group-coverage.md
    │   │   ├── 02-weighted-conformal-under-shift.md
    │   │   ├── 03-conformal-risk-control-for-a-business-loss.md
    │   │   └── README.md
    │   ├── 01-coverage-guarantees-revisited.md
    │   ├── 02-beyond-split-conformal.md
    │   ├── 03-classification-sets.md
    │   ├── 04-class-conditional-and-group-conditional-coverage.md
    │   ├── 05-weighted-conformal-prediction-under-covariate-shift.md
    │   ├── 06-conformal-risk-control-for-general-losses.md
    │   ├── 07-conformal-methods-for-structured-outputs-and-language-models.md
    │   ├── 08-local-and-adaptive-nonconformity-scores.md
    │   ├── 09-limits-of-distribution-free-inference.md
    │   ├── 10-tooling.md
    │   └── README.md
    ├── 08-Uncertainty-Evaluation-and-Decision-Making/
    │   ├── Projects/
    │   │   ├── 01-scoring-rule-and-ece-pitfalls-demonstration.md
    │   │   ├── 02-value-of-information-analysis.md
    │   │   ├── 03-uncertainty-communication-experiment.md
    │   │   └── README.md
    │   ├── 01-proper-scoring-rules.md
    │   ├── 02-calibration-metrics-and-their-flaws.md
    │   ├── 03-sharpness-versus-calibration.md
    │   ├── 04-coverage-and-width-trade-offs-for-intervals-and-sets.md
    │   ├── 05-benchmarking-uncertainty-methods-fairly.md
    │   ├── 06-bayesian-decision-theory.md
    │   ├── 07-value-of-information.md
    │   ├── 08-risk-sensitive-decisions.md
    │   ├── 09-communicating-uncertainty.md
    │   ├── 10-monitoring-uncertainty-in-production.md
    │   └── README.md
    ├── 09-Latent-Variable-Models-and-Bayesian-Nonparametrics/
    │   ├── Projects/
    │   │   ├── 01-topic-model-comparison-and-stability.md
    │   │   ├── 02-dirichlet-process-clustering.md
    │   │   ├── 03-copula-dependence-modeling.md
    │   │   └── README.md
    │   ├── 01-topic-models.md
    │   ├── 02-poisson-factorization-and-probabilistic-matrix-factorization.md
    │   ├── 03-dirichlet-process-mixtures-and-the-chinese-restaurant-process.md
    │   ├── 04-hierarchical-dirichlet-processes-and-choosing-the-number-of-components.md
    │   ├── 05-bayesian-mixture-models-in-practice-with-scikit-learn-and-pymc.md
    │   ├── 06-copulas.md
    │   ├── 07-evaluating-latent-variable-models.md
    │   ├── 08-identifiability-and-label-switching.md
    │   └── README.md
    ├── 10-Causal-Foundations-Structural-Models-and-Identification/
    │   ├── Projects/
    │   │   ├── 01-identification-exercises-with-dags.md
    │   │   ├── 02-collider-and-selection-bias-simulation.md
    │   │   ├── 03-target-trial-emulation-protocol.md
    │   │   └── README.md
    │   ├── 01-structural-causal-models.md
    │   ├── 02-d-separation-and-conditional-independence-implications.md
    │   ├── 03-the-do-operator-and-identification.md
    │   ├── 04-the-do-calculus.md
    │   ├── 05-mediation.md
    │   ├── 06-counterfactuals.md
    │   ├── 07-collider-selection-and-measurement-error-traps-in-practice.md
    │   ├── 08-target-trial-emulation.md
    │   ├── 09-invariance-and-distribution-shift.md
    │   ├── 10-dowhy-workflow.md
    │   └── README.md
    ├── 11-Observational-Estimation-Doubly-Robust-and-Double-ML/
    │   ├── Projects/
    │   │   ├── 01-doubly-robust-vs-naive-vs-ipw-benchmark.md
    │   │   ├── 02-sensitivity-analysis-report.md
    │   │   ├── 03-negative-control-falsification-study.md
    │   │   └── README.md
    │   ├── 01-overlap-and-positivity.md
    │   ├── 02-balance-diagnostics-and-balancing-methods.md
    │   ├── 03-augmented-inverse-probability-weighting-and-doubly-robust-estimation.md
    │   ├── 04-targeted-maximum-likelihood-estimation.md
    │   ├── 05-double-machine-learning.md
    │   ├── 06-confidence-intervals-for-ml-based-causal-estimators.md
    │   ├── 07-bad-controls-and-variable-selection-for-adjustment.md
    │   ├── 08-negative-controls-and-falsification-tests.md
    │   ├── 09-sensitivity-analysis-for-unmeasured-confounding.md
    │   ├── 10-benchmarking-against-randomized-results.md
    │   ├── 11-tooling.md
    │   └── README.md
    ├── 12-Heterogeneous-Effects-and-Policy-Learning/
    │   ├── Projects/
    │   │   ├── 01-cate-estimator-benchmark.md
    │   │   ├── 02-budget-constrained-treatment-policy.md
    │   │   ├── 03-spurious-heterogeneity-test.md
    │   │   └── README.md
    │   ├── 01-meta-learners.md
    │   ├── 02-causal-forests-and-generalized-random-forests.md
    │   ├── 03-neural-cate-models.md
    │   ├── 04-honest-estimation-and-confidence-intervals-for-individual-effects.md
    │   ├── 05-evaluating-cate-models.md
    │   ├── 06-calibration-of-effect-estimates-and-detecting-spurious-heterogeneity.md
    │   ├── 07-policy-learning.md
    │   ├── 08-budget-constrained-and-fairness-constrained-targeting.md
    │   ├── 09-transportability.md
    │   ├── 10-interpreting-heterogeneity.md
    │   └── README.md
    ├── 13-Quasi-Experiments-and-Panel-Methods/
    │   ├── Projects/
    │   │   ├── 01-staggered-did-failure-and-fix.md
    │   │   ├── 02-rdd-with-robustness.md
    │   │   ├── 03-synthetic-control-for-a-policy-or-launch.md
    │   │   └── README.md
    │   ├── 01-two-way-fixed-effects-and-why-staggered-adoption-breaks-it.md
    │   ├── 02-modern-difference-in-differences-estimators.md
    │   ├── 03-event-studies.md
    │   ├── 04-sensitivity-to-parallel-trends-violations.md
    │   ├── 05-synthetic-control-extensions.md
    │   ├── 06-regression-discontinuity-in-practice.md
    │   ├── 07-instrumental-variables-with-machine-learning.md
    │   ├── 08-interrupted-time-series-and-bayesian-structural-time-series-approaches.md
    │   ├── 09-placebo-tests-falsification-and-inference-with-few-treated-units.md
    │   ├── 10-tooling.md
    │   └── README.md
    ├── 14-Experimentation-at-Scale-and-Online-Controlled-Experiments/
    │   ├── Projects/
    │   │   ├── 01-experiment-analysis-pipeline-with-srm-checks.md
    │   │   ├── 02-interference-and-switchback-simulation.md
    │   │   ├── 03-surrogate-index-long-term-effect-study.md
    │   │   └── README.md
    │   ├── 01-randomization-units-and-sample-ratio-mismatch-checks.md
    │   ├── 02-ratio-metrics-and-the-delta-method.md
    │   ├── 03-variance-reduction-beyond-cuped.md
    │   ├── 04-many-metrics-and-many-experiments.md
    │   ├── 05-interference-and-network-effects.md
    │   ├── 06-switchback-and-geo-experiments-for-marketplaces-and-operations.md
    │   ├── 07-two-sided-marketplace-experimentation.md
    │   ├── 08-long-term-effects.md
    │   ├── 09-novelty-and-primacy-effects-and-experiment-duration.md
    │   ├── 10-bayesian-experimentation-and-decision-rules.md
    │   ├── 11-experiment-platform-architecture-and-organizational-pitfalls.md
    │   └── README.md
    ├── 15-Causal-Discovery-and-Causal-Reasoning-with-Unstructured-Data/
    │   ├── Projects/
    │   │   ├── 01-causal-discovery-benchmark-on-synthetic-and-real-graphs.md
    │   │   ├── 02-root-cause-analysis-on-a-service-graph.md
    │   │   ├── 03-text-confounding-adjustment-study.md
    │   │   └── README.md
    │   ├── 01-causal-discovery.md
    │   ├── 02-score-based-and-functional-methods.md
    │   ├── 03-what-discovery-can-and-cannot-identify.md
    │   ├── 04-discovery-for-time-series.md
    │   ├── 05-graph-based-root-cause-analysis-for-systems-and-incidents.md
    │   ├── 06-text-and-images-in-causal-analysis.md
    │   ├── 07-adjusting-with-learned-representations.md
    │   ├── 08-language-models-and-causal-reasoning.md
    │   ├── 09-tooling.md
    │   └── README.md
    ├── 16-Applied-Causal-ML-Projects-and-Communication/
    │   ├── Projects/
    │   │   ├── 01-incrementality-measurement-with-geo-lift.md
    │   │   ├── 02-pricing-effect-estimation-with-confounding.md
    │   │   ├── 03-causal-analysis-review-and-replication.md
    │   │   └── README.md
    │   ├── 01-scoping-causal-questions-with-stakeholders.md
    │   ├── 02-triangulation.md
    │   ├── 03-marketing-incrementality.md
    │   ├── 04-pricing-and-promotion-effects.md
    │   ├── 05-intervention-policies-for-retention-and-growth.md
    │   ├── 06-causal-inference-in-health-and-public-policy.md
    │   ├── 07-writing-causal-analyses.md
    │   ├── 08-pre-analysis-plans-replication-and-review.md
    │   └── README.md
    ├── 17-G7-Capstones/
    │   ├── 01-bayesian-modeling-project-with-full-workflow.md
    │   ├── 02-uncertainty-quantification-system-for-deployed-models.md
    │   ├── 03-causal-effect-estimation-and-policy-study.md
    │   ├── 04-experimentation-platform-and-analysis-toolkit.md
    │   ├── 05-g7-readiness-assessment.md
    │   └── README.md
    └── README.md
```

### 00 — G7 Overview

**Purpose:** the single authoritative plan for G7 with scope, boundaries, prerequisite map, dataset and tooling register, evaluation standards and completion gate.

- `01-g7-scope-and-boundaries-with-stage-4-5b-and-other-groups.md` — what G7 teaches and what it leaves to other groups.
- `02-prerequisite-map-from-the-roadmap.md` — Roadmap stages and modules assumed for each G7 module.
- `03-dataset-and-tooling-register.md` — every dataset, licence and access condition, library with version and maintenance status.
- `04-evaluation-and-reporting-standards.md` — simulation-validation rules, coverage and calibration reporting, assumption statements and report template.
- `05-completion-gate.md` — measurable criteria to finish G7.
- `learning-plan.md` — recommended order, probabilistic and causal tracks and compute budget.

**Project 1: g7 probabilistic and causal simulation bootstrap**  
- Data: simulated datasets generated from known structural models.  
- Task: build a reproducible workspace with pinned tooling and a simulation harness that generates data with known truth, runs an estimator many times and reports bias, interval coverage and calibration.  
- Deliverables: lockfile, simulation harness with tests and a library of three reference data-generating processes.  
- Pass gate: a clean machine reproduces the tests from the lockfile, and a deliberately miscalibrated estimator is flagged by the coverage check.

### 01 — Applied Statistical Inference for ML Practitioners

**Outcome:** Close the gaps between the basic inference of Stage 4B and what real analyses need. Confidence intervals, the bootstrap, hypothesis tests, t-tests, proportion tests, effect size and power are covered in Stage 4B and are not repeated.

**Lessons**

- `01-multiple-testing.md` — Multiple testing: family-wise error, Bonferroni and Holm corrections and false discovery rate control with Benjamini-Hochberg
- `02-multiplicity-in-ml-work.md` — Multiplicity in ML work: many metrics, many models and many slices
- `03-permutation-and-randomization-tests.md` — Permutation and randomization tests: exact inference without distributional assumptions
- `04-nonparametric-tests.md` — Nonparametric tests: Mann-Whitney, Wilcoxon signed-rank and Kolmogorov-Smirnov, with their assumptions
- `05-robust-and-clustered-standard-errors.md` — Robust and clustered standard errors: heteroskedasticity and correlated observations
- `06-multilevel-data-and-mixed-effects-models-in-the-frequentist-framework.md` — Multilevel data and mixed-effects models in the frequentist framework
- `07-model-diagnostics-and-misspecification.md` — Model diagnostics and misspecification: residual checks and influence
- `08-researcher-degrees-of-freedom.md` — Researcher degrees of freedom: p-hacking, forking paths and pre-analysis plans
- `09-meta-analysis.md` — Meta-analysis: combining evidence across studies and heterogeneity
- `10-frequentist-or-bayesian-reporting.md` — Frequentist or Bayesian reporting: choosing and communicating intervals honestly

**Hands-on projects**

- **Project 1: multiple testing simulation and correction**  
  - Data: Simulated experiments with known true and null effects  
  - Task: Run thousands of simulated analyses and compare uncorrected testing with Bonferroni, Holm and Benjamini-Hochberg on false discoveries and power.  
  - Deliverables: Simulation code and comparison plots.  
  - Pass gate: True false-discovery proportion measured against the nominal rate.
- **Project 2: clustered data analysis**  
  - Data: A grouped dataset such as repeated-measures or students-within-schools data  
  - Task: Analyze with naive, clustered-standard-error and mixed-effects approaches and show how intervals change.  
  - Deliverables: Report with intervals under each approach.  
  - Pass gate: Coverage of each method checked by simulation from the same structure.
- **Project 3: p hacking demonstration and preregistered analysis**  
  - Data: A public dataset with many variables  
  - Task: Show how flexible analysis yields spurious findings, then write and follow a pre-analysis plan on a held-out portion.  
  - Deliverables: Demonstration and preregistered analysis.  
  - Pass gate: Plan time-stamped before the held-out data is opened.

### 02 — Bayesian Workflow and Probabilistic Programming

**Outcome:** Build, check and criticize Bayesian models in code. Bayes' theorem, conjugate priors, MAP estimation, MCMC theory and the ELBO are covered in Stages 4B and 4C; this module is the practical workflow.

**Lessons**

- `01-probabilistic-programming-languages.md` — Probabilistic programming languages: PyMC, Stan and NumPyro compared
- `02-specifying-models.md` — Specifying models: priors, likelihoods and the generative story
- `03-prior-predictive-checks.md` — Prior predictive checks: choosing priors that imply sensible data
- `04-mcmc-diagnostics.md` — MCMC diagnostics: R-hat, effective sample size, divergences and trace plots
- `05-posterior-predictive-checks.md` — Posterior predictive checks: finding where a model fails
- `06-model-comparison.md` — Model comparison: leave-one-out cross-validation, WAIC and Pareto-k diagnostics
- `07-prior-sensitivity-analysis-and-robustness-of-conclusions.md` — Prior sensitivity analysis and robustness of conclusions
- `08-reparameterization-for-geometry.md` — Reparameterization for geometry: centered vs non-centered parameterizations
- `09-the-bayesian-workflow-as-an-iterative-process-and-documenting-it.md` — The Bayesian workflow as an iterative process and documenting it
- `10-tooling.md` — Tooling: ArviZ for diagnostics and visualization

**Hands-on projects**

- **Project 1: full bayesian workflow on a real dataset**  
  - Data: A public regression or count dataset  
  - Task: Build a model through prior checks, fitting, diagnostics, posterior checks and comparison of at least three alternatives.  
  - Deliverables: Notebook documenting every iteration and a final report.  
  - Pass gate: All diagnostics reported and at least one model rejected with evidence.
- **Project 2: prior sensitivity study**  
  - Data: The model from the previous project  
  - Task: Vary priors systematically and report which conclusions change.  
  - Deliverables: Sensitivity analysis.  
  - Pass gate: Prior range justified before fitting.
- **Project 3: ppl comparison**  
  - Data: One model implemented in PyMC, Stan and NumPyro  
  - Task: Compare posterior agreement, sampling efficiency and developer effort.  
  - Deliverables: Comparison report.  
  - Pass gate: Same priors, data and effective-sample-size targets.

### 03 — Hierarchical and Multilevel Bayesian Models

**Outcome:** Share information across groups safely and estimate for small groups.

**Lessons**

- `01-partial-pooling.md` — Partial pooling: no pooling, complete pooling and the hierarchical compromise
- `02-varying-intercepts-and-slopes-with-correlated-random-effects.md` — Varying intercepts and slopes with correlated random effects
- `03-hierarchical-bayesian-a-b-testing-and-many-experiment-shrinkage.md` — Hierarchical Bayesian A/B testing and many-experiment shrinkage
- `04-small-area-estimation-and-multilevel-regression-with-poststratification.md` — Small-area estimation and multilevel regression with poststratification
- `05-bayesian-generalized-linear-models.md` — Bayesian generalized linear models: logistic, Poisson and ordinal outcomes
- `06-measurement-error-and-missing-data-models.md` — Measurement error and missing-data models
- `07-rating-and-comparison-models.md` — Rating and comparison models: Bradley-Terry and item-response models
- `08-bayesian-survival-and-censored-data-models.md` — Bayesian survival and censored-data models
- `09-checking-hierarchical-models.md` — Checking hierarchical models: shrinkage plots and group-level predictive checks

**Hands-on projects**

- **Project 1: partial pooling for many small groups**  
  - Data: A dataset with many groups of very different sizes, such as radon or school-level data  
  - Task: Compare no pooling, complete pooling and hierarchical models on held-out group prediction.  
  - Deliverables: Comparison with shrinkage visualizations.  
  - Pass gate: Held-out groups and small-group accuracy reported separately.
- **Project 2: hierarchical ab testing across experiments**  
  - Data: Simulated results from many experiments with known effects  
  - Task: Compare per-experiment estimates with a hierarchical model on error and false-positive rate.  
  - Deliverables: Simulation study.  
  - Pass gate: Ground-truth effects known.
- **Project 3: mrp survey estimation**  
  - Data: A public survey with known population margins  
  - Task: Estimate subgroup opinions with MRP and compare with raw survey means.  
  - Deliverables: Estimates with uncertainty.  
  - Pass gate: Poststratification frame and assumptions documented.

### 04 — Advanced Inference Algorithms and Simulation Based Inference

**Outcome:** Understand how inference engines work, when they fail and what to do when the likelihood is unavailable. Metropolis-Hastings, Gibbs sampling and the ELBO are covered in Stage 4C.

**Lessons**

- `01-hamiltonian-monte-carlo-and-nuts.md` — Hamiltonian Monte Carlo and NUTS: step size, mass matrix and tree depth
- `02-posterior-geometry-pathologies.md` — Posterior geometry pathologies: funnels, multimodality and fixes
- `03-stochastic-variational-inference-and-automatic-differentiation-vi-with-numpyro-and-pyro.md` — Stochastic variational inference and automatic-differentiation VI with NumPyro and Pyro
- `04-richer-variational-families.md` — Richer variational families: normalizing-flow VI
- `05-laplace-approximations-and-when-they-are-enough.md` — Laplace approximations and when they are enough
- `06-sequential-monte-carlo-and-particle-methods.md` — Sequential Monte Carlo and particle methods
- `07-approximate-bayesian-computation-for-simulator-models.md` — Approximate Bayesian computation for simulator models
- `08-neural-simulation-based-inference.md` — Neural simulation-based inference: neural posterior estimation with the sbi library
- `09-validating-inference.md` — Validating inference: simulation-based calibration and coverage checks
- `10-scaling-bayesian-inference.md` — Scaling Bayesian inference: mini-batch methods and their approximations

**Hands-on projects**

- **Project 1: nuts vs vi vs laplace accuracy study**  
  - Data: Models with known or very accurately sampled posteriors  
  - Task: Compare NUTS, ADVI, flow-based VI and Laplace on posterior accuracy and cost.  
  - Deliverables: Accuracy-cost comparison.  
  - Pass gate: Reference posterior from long, well-diagnosed NUTS runs.
- **Project 2: simulation based inference for a simulator**  
  - Data: A simple epidemiological or physical simulator you write  
  - Task: Infer parameters with ABC and neural posterior estimation and validate calibration.  
  - Deliverables: Posteriors and calibration checks.  
  - Pass gate: Simulation-based calibration passes or failures are reported.
- **Project 3: funnel and reparameterization lab**  
  - Data: Neal's funnel and a hierarchical model  
  - Task: Reproduce divergences and fix them with reparameterization.  
  - Deliverables: Before and after diagnostics.  
  - Pass gate: Divergence counts reported.

### 05 — Gaussian Processes and Bayesian Optimization in Practice

**Outcome:** Use Gaussian processes as practical probabilistic models and as optimizers. The introduction to Gaussian processes for small-data uncertainty is covered in Stage 5B and GP-based hyperparameter search in G1.

**Lessons**

- `01-kernel-design.md` — Kernel design: composition, periodic, spectral-mixture and learned kernels
- `02-hyperparameter-learning-and-the-marginal-likelihood.md` — Hyperparameter learning and the marginal likelihood: pitfalls and priors
- `03-scalable-gaussian-processes.md` — Scalable Gaussian processes: inducing points and stochastic variational GPs with GPyTorch
- `04-non-gaussian-likelihoods-and-classification-with-gps.md` — Non-Gaussian likelihoods and classification with GPs
- `05-multi-output-and-multi-fidelity-gps.md` — Multi-output and multi-fidelity GPs
- `06-deep-kernel-learning-and-when-it-overfits.md` — Deep kernel learning and when it overfits
- `07-bayesian-optimization-in-practice.md` — Bayesian optimization in practice: acquisition functions, batch and constrained optimization with BoTorch and Ax
- `08-multi-objective-and-high-dimensional-bayesian-optimization.md` — Multi-objective and high-dimensional Bayesian optimization
- `09-where-gps-fail.md` — Where GPs fail: dimensionality, nonstationarity and misspecified kernels

**Hands-on projects**

- **Project 1: gp kernel design on real series**  
  - Data: A real series with trend and several seasonalities, such as CO2 concentration data  
  - Task: Design and compare kernels on predictive log-likelihood and extrapolation.  
  - Deliverables: Kernel comparison.  
  - Pass gate: Extrapolation evaluated on a held-out final segment.
- **Project 2: scalable gp vs gbdt with uncertainty**  
  - Data: A tabular regression dataset of 100 thousand rows  
  - Task: Compare sparse GPs with GBDT-based quantile models on accuracy and calibrated uncertainty.  
  - Deliverables: Comparison with calibration.  
  - Pass gate: Calibration measured on held-out data.
- **Project 3: bayesian optimization for an expensive simulator**  
  - Data: A simulator or benchmark function with a limited evaluation budget  
  - Task: Compare random search, TPE and GP-based Bayesian optimization at several budgets.  
  - Deliverables: Regret curves with repeated runs.  
  - Pass gate: At least 20 repeats per method.

### 06 — Neural Network and LLM Uncertainty

**Outcome:** Quantify what deep networks and language models do not know. Temperature scaling and calibration are covered in Stage 5B and OOD detection in G2; this module covers the uncertainty estimators themselves.

**Lessons**

- `01-aleatoric-and-epistemic-uncertainty-in-deep-regression.md` — Aleatoric and epistemic uncertainty in deep regression: heteroscedastic and mixture-density outputs
- `02-monte-carlo-dropout-and-its-limits.md` — Monte Carlo dropout and its limits
- `03-deep-ensembles.md` — Deep ensembles: why they work and their cost
- `04-weight-space-approximations.md` — Weight-space approximations: SWAG and Laplace approximations for neural networks
- `05-last-layer-bayesian-methods-and-evidential-approaches-with-their-critiques.md` — Last-layer Bayesian methods and evidential approaches with their critiques
- `06-selective-prediction.md` — Selective prediction: risk-coverage curves and abstention thresholds
- `07-uncertainty-under-dataset-shift.md` — Uncertainty under dataset shift: what degrades and what survives
- `08-language-model-confidence.md` — Language-model confidence: token probabilities, verbalized confidence and self-consistency
- `09-semantic-entropy-and-hallucination-detection.md` — Semantic entropy and hallucination detection
- `10-calibration-and-abstention-for-llm-systems.md` — Calibration and abstention for LLM systems

**Hands-on projects**

- **Project 1: deep uncertainty method comparison**  
  - Data: CIFAR-10 and a regression benchmark, with a shifted test set  
  - Task: Compare ensembles, MC dropout, Laplace and last-layer methods on accuracy, calibration, selective prediction and shift.  
  - Deliverables: Comparison with intervals.  
  - Pass gate: Compute cost reported next to quality.
- **Project 2: llm confidence calibration study**  
  - Data: A question-answering dataset with checkable answers  
  - Task: Compare token probabilities, verbalized confidence, self-consistency and semantic entropy on predicting correctness.  
  - Deliverables: AUROC and calibration comparison.  
  - Pass gate: Correctness judged by a verified procedure.
- **Project 3: selective prediction system**  
  - Data: A classification task with a review cost  
  - Task: Choose an abstention threshold from risk-coverage curves and compute net value with review costs.  
  - Deliverables: Threshold analysis.  
  - Pass gate: Costs stated and sensitivity analysis included.

### 07 — Conformal Prediction and Distribution Free Guarantees

**Outcome:** Produce prediction sets with guaranteed coverage and know what the guarantee does not say. Split conformal prediction and conformalized quantile regression are covered in Stage 5B and time-series conformal methods in G5.

**Lessons**

- `01-coverage-guarantees-revisited.md` — Coverage guarantees revisited: marginal vs conditional coverage
- `02-beyond-split-conformal.md` — Beyond split conformal: cross-conformal, CV+ and jackknife+
- `03-classification-sets.md` — Classification sets: APS and RAPS scores and set-size control
- `04-class-conditional-and-group-conditional-coverage.md` — Class-conditional and group-conditional coverage: Mondrian conformal
- `05-weighted-conformal-prediction-under-covariate-shift.md` — Weighted conformal prediction under covariate shift
- `06-conformal-risk-control-for-general-losses.md` — Conformal risk control for general losses
- `07-conformal-methods-for-structured-outputs-and-language-models.md` — Conformal methods for structured outputs and language models
- `08-local-and-adaptive-nonconformity-scores.md` — Local and adaptive nonconformity scores
- `09-limits-of-distribution-free-inference.md` — Limits of distribution-free inference
- `10-tooling.md` — Tooling: MAPIE, TorchCP and crepes

**Hands-on projects**

- **Project 1: conformal classification with group coverage**  
  - Data: A multiclass image or tabular dataset with subgroup labels  
  - Task: Compare split, APS, RAPS and Mondrian methods on coverage, set size and subgroup coverage.  
  - Deliverables: Coverage-and-size comparison by group.  
  - Pass gate: Coverage checked over many random calibration splits.
- **Project 2: weighted conformal under shift**  
  - Data: A dataset with a built-in covariate shift between calibration and test  
  - Task: Show coverage loss under shift and recovery with weighted conformal prediction.  
  - Deliverables: Coverage results.  
  - Pass gate: Density-ratio estimation error analyzed.
- **Project 3: conformal risk control for a business loss**  
  - Data: A decision problem with an asymmetric loss  
  - Task: Control the expected loss at a target level and compare with a fixed threshold.  
  - Deliverables: Risk-control evaluation.  
  - Pass gate: Loss control verified empirically over repeated splits.

### 08 — Uncertainty Evaluation and Decision Making

**Outcome:** Judge uncertainty estimates properly and act on them. Reliability diagrams, the Brier score and expected-cost thresholds are covered in Stage 5B; this module adds scoring theory and decision theory.

**Lessons**

- `01-proper-scoring-rules.md` — Proper scoring rules: log score, Brier, CRPS and interval score
- `02-calibration-metrics-and-their-flaws.md` — Calibration metrics and their flaws: binned ECE, smooth and class-wise variants
- `03-sharpness-versus-calibration.md` — Sharpness versus calibration: the Gneiting view of probabilistic forecasts
- `04-coverage-and-width-trade-offs-for-intervals-and-sets.md` — Coverage and width trade-offs for intervals and sets
- `05-benchmarking-uncertainty-methods-fairly.md` — Benchmarking uncertainty methods fairly
- `06-bayesian-decision-theory.md` — Bayesian decision theory: loss functions and posterior expected loss
- `07-value-of-information.md` — Value of information: when to collect more data
- `08-risk-sensitive-decisions.md` — Risk-sensitive decisions: tail risk and CVaR
- `09-communicating-uncertainty.md` — Communicating uncertainty: visual designs and stakeholder understanding
- `10-monitoring-uncertainty-in-production.md` — Monitoring uncertainty in production

**Hands-on projects**

- **Project 1: scoring rule and ece pitfalls demonstration**  
  - Data: Synthetic predictors with known calibration and sharpness  
  - Task: Show how ECE binning choices, accuracy and proper scores can rank models differently.  
  - Deliverables: Demonstration and recommended metric set.  
  - Pass gate: Ground-truth calibration known by construction.
- **Project 2: value of information analysis**  
  - Data: A decision problem with uncertain parameters  
  - Task: Compute the expected value of additional data and decide whether to collect it.  
  - Deliverables: Analysis with assumptions.  
  - Pass gate: Prior and loss assumptions explicit.
- **Project 3: uncertainty communication experiment**  
  - Data: A forecast or risk scenario  
  - Task: Test several uncertainty visualizations with a small group for decision quality.  
  - Deliverables: Study results.  
  - Pass gate: Participants give consent and data are anonymized.

### 09 — Latent Variable Models and Bayesian Nonparametrics

**Outcome:** Model hidden structure with flexible probabilistic models. EM and Gaussian mixtures, the ELBO and VAEs are covered in Stages 4C and 5A; this module covers topic models, nonparametrics and dependence models.

**Lessons**

- `01-topic-models.md` — Topic models: latent Dirichlet allocation with variational and sampling inference
- `02-poisson-factorization-and-probabilistic-matrix-factorization.md` — Poisson factorization and probabilistic matrix factorization
- `03-dirichlet-process-mixtures-and-the-chinese-restaurant-process.md` — Dirichlet process mixtures and the Chinese restaurant process
- `04-hierarchical-dirichlet-processes-and-choosing-the-number-of-components.md` — Hierarchical Dirichlet processes and choosing the number of components
- `05-bayesian-mixture-models-in-practice-with-scikit-learn-and-pymc.md` — Bayesian mixture models in practice with scikit-learn and PyMC
- `06-copulas.md` — Copulas: modeling dependence separately from marginals
- `07-evaluating-latent-variable-models.md` — Evaluating latent-variable models: held-out likelihood, stability and interpretability
- `08-identifiability-and-label-switching.md` — Identifiability and label switching

**Hands-on projects**

- **Project 1: topic model comparison and stability**  
  - Data: A public document corpus  
  - Task: Compare LDA, Poisson factorization and an embedding-based topic model on held-out likelihood, stability and human review.  
  - Deliverables: Comparison.  
  - Pass gate: Stability measured across random seeds.
- **Project 2: dirichlet process clustering**  
  - Data: A dataset with unknown cluster count  
  - Task: Fit a Dirichlet process mixture and compare inferred component count with held-out validation.  
  - Deliverables: Analysis with uncertainty on cluster count.  
  - Pass gate: Synthetic data with known component count included.
- **Project 3: copula dependence modeling**  
  - Data: Two or more dependent variables such as insurance or finance data  
  - Task: Fit copulas and compare joint-risk estimates against an independence assumption.  
  - Deliverables: Joint-risk analysis.  
  - Pass gate: Out-of-sample joint-tail frequencies compared.

### 10 — Causal Foundations Structural Models and Identification

**Outcome:** Formalize causal questions and decide whether data can answer them. Prediction versus causation, confounding and causal diagrams, selection bias and propensity basics are covered in Stage 5B and are not repeated.

**Lessons**

- `01-structural-causal-models.md` — Structural causal models: equations, graphs and interventions
- `02-d-separation-and-conditional-independence-implications.md` — d-separation and conditional independence implications
- `03-the-do-operator-and-identification.md` — The do-operator and identification: backdoor adjustment and the front-door criterion
- `04-the-do-calculus.md` — The do-calculus: when an effect is identifiable and when it is not
- `05-mediation.md` — Mediation: direct and indirect effects and their assumptions
- `06-counterfactuals.md` — Counterfactuals: the ladder from association to intervention to counterfactual
- `07-collider-selection-and-measurement-error-traps-in-practice.md` — Collider, selection and measurement-error traps in practice
- `08-target-trial-emulation.md` — Target trial emulation: framing observational questions as trials
- `09-invariance-and-distribution-shift.md` — Invariance and distribution shift: the causal view and the limits of invariant learning
- `10-dowhy-workflow.md` — DoWhy workflow: model, identify, estimate, refute and documenting assumptions

**Hands-on projects**

- **Project 1: identification exercises with dags**  
  - Data: A set of 20 causal graphs and questions you construct  
  - Task: Decide identifiability, adjustment sets and instruments, then confirm with software and simulation.  
  - Deliverables: Worked solutions and verification code.  
  - Pass gate: Every answer checked by simulation from a known structural model.
- **Project 2: collider and selection bias simulation**  
  - Data: Simulated data with colliders and selection  
  - Task: Show bias introduced by controlling for the wrong variables and by selecting on outcomes.  
  - Deliverables: Simulation and explanation.  
  - Pass gate: True effects known and compared.
- **Project 3: target trial emulation protocol**  
  - Data: A public observational dataset  
  - Task: Write a target-trial protocol and map each element to the data, with documented gaps.  
  - Deliverables: Protocol document.  
  - Pass gate: Eligibility, time zero and assignment defined before analysis.

### 11 — Observational Estimation Doubly Robust and Double ML

**Outcome:** Estimate causal effects from observational data with machine learning while keeping valid inference. Propensity scores, matching and weighting are introduced in Stage 5B.

**Lessons**

- `01-overlap-and-positivity.md` — Overlap and positivity: diagnostics, trimming and what they change
- `02-balance-diagnostics-and-balancing-methods.md` — Balance diagnostics and balancing methods: entropy balancing and covariate balancing propensity scores
- `03-augmented-inverse-probability-weighting-and-doubly-robust-estimation.md` — Augmented inverse probability weighting and doubly robust estimation
- `04-targeted-maximum-likelihood-estimation.md` — Targeted maximum likelihood estimation
- `05-double-machine-learning.md` — Double machine learning: cross-fitting, Neyman orthogonality and nuisance models
- `06-confidence-intervals-for-ml-based-causal-estimators.md` — Confidence intervals for ML-based causal estimators
- `07-bad-controls-and-variable-selection-for-adjustment.md` — Bad controls and variable selection for adjustment
- `08-negative-controls-and-falsification-tests.md` — Negative controls and falsification tests
- `09-sensitivity-analysis-for-unmeasured-confounding.md` — Sensitivity analysis for unmeasured confounding: E-values and omitted-variable-bias bounds
- `10-benchmarking-against-randomized-results.md` — Benchmarking against randomized results: LaLonde-style comparisons and their lessons
- `11-tooling.md` — Tooling: EconML, DoubleML and CausalML, with maintenance checks

**Hands-on projects**

- **Project 1: doubly robust vs naive vs ipw benchmark**  
  - Data: Semi-synthetic data with known effects such as IHDP-style benchmarks, and a LaLonde-style dataset  
  - Task: Compare regression adjustment, IPW, AIPW, TMLE and double ML on bias and interval coverage.  
  - Deliverables: Benchmark with coverage rates over many replications.  
  - Pass gate: Interval coverage measured against known truth.
- **Project 2: sensitivity analysis report**  
  - Data: An observational analysis from the previous project  
  - Task: Quantify how strong an unmeasured confounder would need to be to overturn the conclusion.  
  - Deliverables: Sensitivity report.  
  - Pass gate: Benchmark covariates used to calibrate plausible strength.
- **Project 3: negative control falsification study**  
  - Data: A dataset where null outcomes exist  
  - Task: Use negative-control outcomes to detect residual bias in the estimator.  
  - Deliverables: Falsification analysis.  
  - Pass gate: Negative controls chosen before estimation.

### 12 — Heterogeneous Effects and Policy Learning

**Outcome:** Estimate who benefits and decide whom to treat. Uplift modeling and heterogeneous treatment effects are introduced in Stage 5B.

**Lessons**

- `01-meta-learners.md` — Meta-learners: S, T, X, R and DR learners and their trade-offs
- `02-causal-forests-and-generalized-random-forests.md` — Causal forests and generalized random forests
- `03-neural-cate-models.md` — Neural CATE models: TARNet and Dragonnet
- `04-honest-estimation-and-confidence-intervals-for-individual-effects.md` — Honest estimation and confidence intervals for individual effects
- `05-evaluating-cate-models.md` — Evaluating CATE models: Qini and uplift curves, RATE, AUTOC and the R-loss
- `06-calibration-of-effect-estimates-and-detecting-spurious-heterogeneity.md` — Calibration of effect estimates and detecting spurious heterogeneity
- `07-policy-learning.md` — Policy learning: learning treatment rules from data
- `08-budget-constrained-and-fairness-constrained-targeting.md` — Budget-constrained and fairness-constrained targeting
- `09-transportability.md` — Transportability: carrying effects to new populations
- `10-interpreting-heterogeneity.md` — Interpreting heterogeneity: subgroup discovery and its multiplicity problem

**Hands-on projects**

- **Project 1: cate estimator benchmark**  
  - Data: Randomized-trial data such as Criteo uplift (check licence) and semi-synthetic benchmarks  
  - Task: Compare meta-learners, causal forests and neural CATE models using Qini curves, RATE and policy value.  
  - Deliverables: Benchmark with intervals.  
  - Pass gate: Evaluation on randomized held-out data.
- **Project 2: budget constrained treatment policy**  
  - Data: The same randomized data with a cost per treatment  
  - Task: Learn a targeting policy and compare its value with treat-all and random policies under a budget.  
  - Deliverables: Policy value analysis.  
  - Pass gate: Policy value estimated with a held-out randomized sample.
- **Project 3: spurious heterogeneity test**  
  - Data: Randomized data with permuted treatment effects  
  - Task: Show how CATE models find fake heterogeneity and how honest methods guard against it.  
  - Deliverables: False-discovery analysis.  
  - Pass gate: Null data constructed with known zero heterogeneity.

### 13 — Quasi Experiments and Panel Methods

**Outcome:** Estimate effects from natural experiments and policy changes. Difference-in-differences, synthetic control, instrumental variables and regression discontinuity are introduced in Stage 5B.

**Lessons**

- `01-two-way-fixed-effects-and-why-staggered-adoption-breaks-it.md` — Two-way fixed effects and why staggered adoption breaks it
- `02-modern-difference-in-differences-estimators.md` — Modern difference-in-differences estimators: Callaway-Sant'Anna, Sun-Abraham and related methods
- `03-event-studies.md` — Event studies: plots, pre-trend tests and their power problems
- `04-sensitivity-to-parallel-trends-violations.md` — Sensitivity to parallel-trends violations
- `05-synthetic-control-extensions.md` — Synthetic control extensions: augmented and synthetic difference-in-differences
- `06-regression-discontinuity-in-practice.md` — Regression discontinuity in practice: bandwidth selection, manipulation tests and fuzzy designs
- `07-instrumental-variables-with-machine-learning.md` — Instrumental variables with machine learning: weak instruments and valid inference
- `08-interrupted-time-series-and-bayesian-structural-time-series-approaches.md` — Interrupted time series and Bayesian structural time-series approaches
- `09-placebo-tests-falsification-and-inference-with-few-treated-units.md` — Placebo tests, falsification and inference with few treated units
- `10-tooling.md` — Tooling: pyfixest, CausalPy and RD and synthetic-control packages, with maintenance checks

**Hands-on projects**

- **Project 1: staggered did failure and fix**  
  - Data: Simulated panel data with staggered adoption and time-varying effects, plus a real policy dataset  
  - Task: Show two-way fixed-effects bias and compare with modern estimators on known truth.  
  - Deliverables: Estimator comparison.  
  - Pass gate: True effects known in simulation.
- **Project 2: rdd with robustness**  
  - Data: A public discontinuity dataset such as an eligibility threshold  
  - Task: Run an RD analysis with bandwidth sensitivity, manipulation tests and placebo cutoffs.  
  - Deliverables: Analysis with robustness table.  
  - Pass gate: Placebo cutoffs and bandwidth range reported.
- **Project 3: synthetic control for a policy or launch**  
  - Data: Public regional data around a policy change or a simulated launch  
  - Task: Estimate the effect with synthetic control and permutation inference.  
  - Deliverables: Estimate with placebo-in-space inference.  
  - Pass gate: Pre-period fit reported and donors justified.

### 14 — Experimentation at Scale and Online Controlled Experiments

**Outcome:** Run trustworthy experiments in real products. CUPED, sequential testing, A/B tests for proportions and power are covered in Stages 4B and 5B; this module covers design problems at scale.

**Lessons**

- `01-randomization-units-and-sample-ratio-mismatch-checks.md` — Randomization units and sample ratio mismatch checks
- `02-ratio-metrics-and-the-delta-method.md` — Ratio metrics and the delta method
- `03-variance-reduction-beyond-cuped.md` — Variance reduction beyond CUPED: regression adjustment, stratification and CUPAC
- `04-many-metrics-and-many-experiments.md` — Many metrics and many experiments: false discovery control in experimentation
- `05-interference-and-network-effects.md` — Interference and network effects: cluster randomization and ego-network designs
- `06-switchback-and-geo-experiments-for-marketplaces-and-operations.md` — Switchback and geo experiments for marketplaces and operations
- `07-two-sided-marketplace-experimentation.md` — Two-sided marketplace experimentation
- `08-long-term-effects.md` — Long-term effects: surrogate indices and holdbacks
- `09-novelty-and-primacy-effects-and-experiment-duration.md` — Novelty and primacy effects and experiment duration
- `10-bayesian-experimentation-and-decision-rules.md` — Bayesian experimentation and decision rules
- `11-experiment-platform-architecture-and-organizational-pitfalls.md` — Experiment platform architecture and organizational pitfalls

**Hands-on projects**

- **Project 1: experiment analysis pipeline with srm checks**  
  - Data: Simulated experiments with injected data-quality problems  
  - Task: Build an analysis pipeline that detects sample ratio mismatch, handles ratio metrics and applies variance reduction.  
  - Deliverables: Pipeline and tests.  
  - Pass gate: Injected problems are detected.
- **Project 2: interference and switchback simulation**  
  - Data: A marketplace simulator you build  
  - Task: Show bias from user-level randomization under interference and compare cluster and switchback designs.  
  - Deliverables: Bias and variance comparison.  
  - Pass gate: True global effect computed from the simulator.
- **Project 3: surrogate index long term effect study**  
  - Data: Simulated long-term outcomes with short-term surrogates  
  - Task: Estimate long-term effects from short-term data and compare with the full-length truth.  
  - Deliverables: Estimator evaluation.  
  - Pass gate: Surrogacy assumptions tested explicitly.

### 15 — Causal Discovery and Causal Reasoning with Unstructured Data

**Outcome:** Learn structure from data when theory is missing and handle text and images in causal analysis, with a clear view of what can be claimed.

**Lessons**

- `01-causal-discovery.md` — Causal discovery: constraint-based methods such as PC and FCI
- `02-score-based-and-functional-methods.md` — Score-based and functional methods: GES, LiNGAM and continuous-optimization approaches such as NOTEARS
- `03-what-discovery-can-and-cannot-identify.md` — What discovery can and cannot identify: equivalence classes and assumption violations
- `04-discovery-for-time-series.md` — Discovery for time series: Granger causality and PCMCI
- `05-graph-based-root-cause-analysis-for-systems-and-incidents.md` — Graph-based root-cause analysis for systems and incidents
- `06-text-and-images-in-causal-analysis.md` — Text and images in causal analysis: text as treatment, outcome or confounder
- `07-adjusting-with-learned-representations.md` — Adjusting with learned representations: validity conditions and pitfalls
- `08-language-models-and-causal-reasoning.md` — Language models and causal reasoning: what evidence exists and its limits
- `09-tooling.md` — Tooling: causal-learn, gCastle, Tigramite and DoWhy graphical causal models, with maintenance checks

**Hands-on projects**

- **Project 1: causal discovery benchmark on synthetic and real graphs**  
  - Data: Synthetic graphs and a real graph with accepted structure such as the Sachs protein data  
  - Task: Compare PC, GES, LiNGAM and NOTEARS on structure recovery under assumption violations.  
  - Deliverables: Benchmark with structural-Hamming-distance metrics.  
  - Pass gate: Violations injected deliberately and reported.
- **Project 2: root cause analysis on a service graph**  
  - Data: A simulated microservice system with injected faults  
  - Task: Build graph-based root-cause analysis and measure how often the true cause ranks first.  
  - Deliverables: RCA system and evaluation.  
  - Pass gate: Faults injected with known causes.
- **Project 3: text confounding adjustment study**  
  - Data: Semi-synthetic text data with known treatment effects  
  - Task: Compare adjustment with text embeddings against ignoring text and show failure cases.  
  - Deliverables: Bias analysis.  
  - Pass gate: True effects known by construction.

### 16 — Applied Causal ML Projects and Communication

**Outcome:** Carry causal questions from the business to a defensible decision. The marketing mix modeling and churn lessons of G1 and the experimentation lessons of this group are referenced, not repeated.

**Lessons**

- `01-scoping-causal-questions-with-stakeholders.md` — Scoping causal questions with stakeholders: decision, estimand and constraints
- `02-triangulation.md` — Triangulation: combining experiments, quasi-experiments and observational estimates
- `03-marketing-incrementality.md` — Marketing incrementality: geo-lift tests and calibrating mix models with experiments
- `04-pricing-and-promotion-effects.md` — Pricing and promotion effects: demand response and its confounding
- `05-intervention-policies-for-retention-and-growth.md` — Intervention policies for retention and growth: from effect estimates to constrained action
- `06-causal-inference-in-health-and-public-policy.md` — Causal inference in health and public policy: caution, ethics and regulation
- `07-writing-causal-analyses.md` — Writing causal analyses: assumptions, sensitivity and limits stated up front
- `08-pre-analysis-plans-replication-and-review.md` — Pre-analysis plans, replication and review

**Hands-on projects**

- **Project 1: incrementality measurement with geo lift**  
  - Data: A simulated or public regional marketing dataset  
  - Task: Design and analyze a geo-lift test and use it to calibrate a marketing mix model.  
  - Deliverables: Test design, analysis and calibration.  
  - Pass gate: Calibrated model compared with the uncalibrated model against known truth.
- **Project 2: pricing effect estimation with confounding**  
  - Data: Retail scanner data such as Dominick's or a simulation  
  - Task: Estimate price response with several methods and compare with a randomized price-test benchmark in simulation.  
  - Deliverables: Estimates with sensitivity.  
  - Pass gate: Benchmark effect known in simulation.
- **Project 3: causal analysis review and replication**  
  - Data: A published applied causal analysis with public data  
  - Task: Replicate it, critique assumptions and run an additional sensitivity analysis.  
  - Deliverables: Replication and critique report.  
  - Pass gate: Every deviation from the original documented.

### 17 — G7 Capstones

**Outcome:** integrate the probabilistic, uncertainty, causal and experimentation tracks in assessed, portfolio-quality work.

- **Capstone 1: bayesian modeling project with full workflow** (uses Modules 02 to 04)  
  Carry out a complete Bayesian analysis with prior checks, hierarchical structure, diagnostics, validation of inference and a sensitivity analysis, ending in a decision-focused report.
- **Capstone 2: uncertainty quantification system for deployed models** (uses Modules 05 to 08)  
  Build uncertainty estimation for a deployed predictor with conformal sets, deep or Bayesian uncertainty, abstention policy, proper-score evaluation and production monitoring.
- **Capstone 3: causal effect estimation and policy study** (uses Modules 10 to 13, 16)  
  Estimate treatment effects with several methods on a realistic problem, test assumptions and sensitivity, learn a treatment policy and deliver a defensible recommendation.
- **Capstone 4: experimentation platform and analysis toolkit** (uses Modules 01, 14)  
  Build an experiment analysis toolkit with data-quality checks, variance reduction, multiple-testing control, interference-aware designs and validated simulations.
- **Capstone 5: g7 readiness assessment** (uses All modules)  
  Written and practical assessment against the G7 completion gate.

## G7 completion gate

- Every estimator or inference method is validated on simulated data with known truth, reporting bias, interval coverage and calibration over many replications, before it is applied to real data.
- Every Bayesian analysis documents prior checks, convergence diagnostics, posterior predictive checks and a prior-sensitivity analysis.
- Every uncertainty claim is evaluated with proper scoring rules and coverage on held-out data, not with accuracy or a single binned calibration metric.
- Every causal claim states its estimand, identification assumptions, a sensitivity analysis and at least one falsification or placebo test.
- Every comparison of methods uses matched budgets, many replications and intervals, and reports cases where the method fails.
- All results reproduce from a lockfile, configs and logged seeds, with library versions and dataset licences recorded.
- At least one negative or inconclusive result per track is reported honestly, including a case where a causal claim could not be supported.
- The four specialist capstones are complete and the readiness assessment is passed.

## Audit and verification

**What was checked and the result**

- Structure: 16 specialist modules each have 6 to 12 lessons and at least one project; the tree contains 251 files and 35 folders, and these counts equal the counts computed from the curriculum data.
- Overlap with the Roadmap: all 155 lesson file names were compared against every lesson file name in `Roadmap.md`. Exact matches: 0. Near matches (similarity 0.80 or higher): 1 — `targeted-maximum-likelihood-estimation` vs Roadmap `maximum-likelihood-estimation` (0.87). Reviewed manually: targeted maximum likelihood estimation is a causal estimator and shares only words with the Stage 5A maximum-likelihood lesson.
- Structural problems found by the build script: 0.
- Topic-level overlap check: the Roadmap text was searched for PyMC, NumPyro, NUTS, HMC, R-hat, WAIC, mixed-effects models, topic models, copulas, simulation-based inference, Laplace approximation, MC dropout, deep ensembles, Mondrian and jackknife conformal methods, the do-calculus, backdoor and front-door criteria, NOTEARS, DoWhy, EconML, double machine learning, TMLE, causal forests, meta-learners, Qini curves, staggered adoption, rdrobust, switchback and geo experiments, the delta method, sample ratio mismatch, multiple testing, false discovery, permutation tests, Thompson sampling in the context of Bayesian A/B testing, proper scoring rules, CRPS, semantic entropy, prior and posterior predictive checks and value of information. None appear as lessons, so G7 teaches them for the first time. The Roadmap does contain Stage 4B inference, Stage 4C Bayesian inference and MCMC mathematics, Stage 5B probabilistic prediction and causal inference lessons, which G7 references and extends and does not reteach; E-values and sensitivity analysis for unmeasured confounding do not appear in the Roadmap (its only sensitivity lesson is Stage 5B robustness and sensitivity analysis for model selection, which is a different topic), so they are taught here.
- Verified by web search on the build date (2026-10-26): the semantic-entropy hallucination-detection method (Farquhar, Kossen, Kuhn and Gal) was published in Nature in June 2024; ArviZ is being split into arviz-base, arviz-stats and arviz-plots and integrates with PyMC, NumPyro, Stan interfaces and Pyro; pre-trends tests are underpowered and conditioning on passing them distorts inference (Roth); two-way fixed effects can give wrong-signed estimates under staggered adoption with heterogeneous effects, and Callaway-Sant'Anna and Sun-Abraham estimators address this.
- Reported but not confirmed: current versions and maintenance status of PyMC, NumPyro, Stan, DoWhy, EconML, CausalPy, DoubleML, CausalML, causal-learn, gCastle, Tigramite, MAPIE and sbi were not confirmed by search and are required in the register; conformal risk control (Angelopoulos et al.) and jackknife+ (Barber et al.) were not confirmed by search and are cited from established literature, so check the primary papers; the Cinelli-Hazlett omitted-variable-bias framework was not confirmed by search and should be read in the original paper.
- Not verified: dataset availability and licences (Criteo uplift, IHDP-style benchmark files, the Sachs protein data, survey and scanner data); library versions, which change quickly; and any regulatory statements for health and policy applications.
- Not verified by execution: no code in this plan has been run. Project pass gates are acceptance criteria to be met when the projects are built.
- Safety note: modules 12, 16 and the health and policy lessons involve decisions about people. Their projects use public, simulated or consented data and must not drive real treatment or targeting decisions without ethical and legal review.
- Repository safety: this build created only this file; no existing file or folder was created, changed or deleted by it.
