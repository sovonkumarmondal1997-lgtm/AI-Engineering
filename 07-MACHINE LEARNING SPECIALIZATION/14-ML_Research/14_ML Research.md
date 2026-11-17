# ML Research — ML Specialization Roadmap

**Group 14 (G14)**, the last group of the specialization that follows Stage 5D of the [Roadmap](./Roadmap.md). It covers original category **34 ML Research and Algorithm Development**. The group's defining question is: *how do I invent new learning methods?* It follows G1 to G13: [`01_Classical and Applied ML.md`](./01_Classical%20and%20Applied%20ML.md), [`02_Deep Learning by Modality.md`](./02_Deep%20Learning%20by%20Modality.md), [`03_Generative and Foundation Models.md`](./03_Generative%20and%20Foundation%20Models.md), [`04_Agents and Sequential Decisions.md`](./04_Agents%20and%20Sequential%20Decisions.md), [`05_Time and Anomaly Modeling.md`](./05_Time%20and%20Anomaly%20Modeling.md), [`06_Personalization Search and Matching.md`](./06_Personalization%20Search%20and%20Matching.md), [`07_Statistical Reasoning.md`](./07_Statistical%20Reasoning.md), [`08_Graphs and Optimization.md`](./08_Graphs%20and%20Optimization.md), [`09_Industry Domain ML.md`](./09_Industry%20Domain%20ML.md), [`10_Efficient and Scalable Systems.md`](./10_Efficient%20and%20Scalable%20Systems.md), [`11_MLOps and Reliability.md`](./11_MLOps%20and%20Reliability.md), [`12_Trustworthy ML.md`](./12_Trustworthy%20ML.md), [`13_Data and Evaluation.md`](./13_Data%20and%20Evaluation.md).

**Important context:** research cannot be taught as a list of results, because results change faster than any curriculum. G14 therefore teaches research as a craft: choosing questions, running experiments that can support claims, studying theory and training dynamics, developing and honestly testing new methods, writing and reviewing, and doing all of it responsibly and on a limited budget. It deliberately asserts no current state-of-the-art claims.

## G14 summary

| Item | Count |
|---|---|
| Modules (including overview and capstones) | 13 |
| Lesson files | 106 |
| Hands-on project files (module projects, overview project and capstones) | 39 |
| Folders inside the G14 tree | 25 |
| Files inside the G14 tree | 177 |

| Original category | Modules |
|---|---|
| 34 ML Research and Algorithm Development | 01 to 11 |

## Scope and how G14 avoids repeating the Roadmap

These are **already learned** and are only referenced, never retaught. From **Stage 5C**: how to read a paper, the essential paper list, reproducing results and writing paper summaries. From **Stages 4A to 4C**: probability, concentration inequalities (Markov, Chebyshev, Hoeffding), expected versus empirical risk and generalization, estimator bias and variance, convex optimization, convergence rates of gradient descent, stochastic optimization theory, the standard optimizers and learning-rate schedules, information theory, and the mathematics of backpropagation, attention, normalization and generative models. From **Stages 5A and 5B**: train, validation and test design, nested validation, comparing models across folds, ablation studies and error analysis, and the specialist methods surveyed there. From **earlier groups**: custom autograd, Hydra configuration and silent-failure debugging (G2), muP-style small-scale architecture experiments and scaling-law fitting (G3), seed variance and reporting for RL (G4), pre-analysis plans and multiple testing (G7), statistical comparison methods, benchmark construction and replication (G13), safety evaluation and responsible release frameworks (G12) and compute access (G10).

**Boundaries with other groups** (so nothing overlaps): this group does not re-teach any topic area. The specialist groups G1 to G13 hold the area knowledge; G14 holds the research method that applies to all of them. Module 07 shows how to build an area map and does not summarize any area's current results.

| Roadmap topic already covered | Where G14 goes further |
|---|---|
| Reading and reproducing papers, summaries (5C) | Module 01: choosing questions, systematic review, claim tracking and writing proposals |
| Ablations, nested validation, comparison across folds (5A, 5B) | Module 02: hypothesis-to-experiment design, fair baselines, research debugging and scale-transfer checks |
| Concentration inequalities, expected risk and generalization (4B, 4C) | Module 03: PAC learning, capacity measures, PAC-Bayes, double descent and implicit bias |
| Optimization theory and optimizers (4C), tuning playbook (5C) | Module 04: training dynamics, edge of stability, preconditioned optimizers, grokking and optimizer benchmarking |
| Custom autograd and debugging (G2), architecture ablations (G3) | Module 05: method invention, toy problems, case studies of method evolution and library-grade release |
| Mathematical foundations (4A to 4C) | Module 06: reading and writing proofs, derivation checking and toy theory |
| Specialist groups G1 to G13 | Module 07: how to map any research area and find tractable open problems |
| Scaling-law fitting (G3), compute access (G10) | Module 08: research strategy under a fixed compute budget |
| Paper summaries (5C), replication (G13) | Module 09: writing papers, peer review, rebuttals and publishing norms |
| Responsible release and safety (G12), evaluation integrity (G13) | Module 10: research integrity, reproducibility problems, dual-use and release decisions |
| Portfolio work across the specialization | Module 11: roles, graduate study, collaboration, open-source contribution and research profiles |

## G14 — ML Research

**Defining question:** How do I invent new learning methods?

```text
ML Specialization/
└── G14 — ML Research/
    ├── 00-G14-Overview/
    │   ├── Projects/
    │   │   ├── 01-g14-research-notebook-and-reproducibility-bootstrap.md
    │   │   └── README.md
    │   ├── 01-g14-scope-and-boundaries-with-stage-5c-and-other-groups.md
    │   ├── 02-prerequisite-map-from-the-roadmap.md
    │   ├── 03-research-tooling-and-source-register.md
    │   ├── 04-research-reporting-and-integrity-standards.md
    │   ├── 05-completion-gate.md
    │   ├── README.md
    │   └── learning-plan.md
    ├── 01-Research-Foundations-Problem-Selection-and-Literature-Strategy/
    │   ├── Projects/
    │   │   ├── 01-systematic-review-of-a-narrow-topic.md
    │   │   ├── 02-claim-tracking-and-state-of-the-art-audit.md
    │   │   ├── 03-research-proposal-with-risk-analysis.md
    │   │   └── README.md
    │   ├── 01-what-ml-research-is.md
    │   ├── 02-choosing-problems.md
    │   ├── 03-turning-an-interest-into-a-research-question-and-a-falsifiable-hypothesis.md
    │   ├── 04-literature-search.md
    │   ├── 05-systematic-literature-review.md
    │   ├── 06-tracking-the-state-of-the-art-honestly.md
    │   ├── 07-reading-critically-for-weaknesses.md
    │   ├── 08-reference-and-note-management.md
    │   ├── 09-writing-a-research-proposal.md
    │   ├── 10-negative-and-null-results.md
    │   └── README.md
    ├── 02-Experimental-Methodology-and-Research-Engineering/
    │   ├── Projects/
    │   │   ├── 01-ablation-and-baseline-fairness-study.md
    │   │   ├── 02-silent-bug-catalog-for-research-code.md
    │   │   ├── 03-small-scale-transfer-experiment.md
    │   │   └── README.md
    │   ├── 01-from-hypothesis-to-experiment.md
    │   ├── 02-baselines.md
    │   ├── 03-ablation-design.md
    │   ├── 04-research-debugging.md
    │   ├── 05-proxy-tasks-and-small-scale-experiments.md
    │   ├── 06-sweeps-and-compute-budgeting.md
    │   ├── 07-research-code-structure.md
    │   ├── 08-research-logbooks.md
    │   ├── 09-analyzing-results.md
    │   ├── 10-scaling-up-checks.md
    │   └── README.md
    ├── 03-Learning-Theory-for-ML-Researchers/
    │   ├── Projects/
    │   │   ├── 01-generalization-bound-numerical-study.md
    │   │   ├── 02-double-descent-reproduction.md
    │   │   ├── 03-implicit-bias-experiment.md
    │   │   └── README.md
    │   ├── 01-the-learning-problem-formalized.md
    │   ├── 02-pac-learning-and-sample-complexity.md
    │   ├── 03-capacity-measures.md
    │   ├── 04-uniform-convergence-and-margin-bounds.md
    │   ├── 05-pac-bayes-bounds-and-their-use-for-neural-networks.md
    │   ├── 06-algorithmic-stability-and-generalization.md
    │   ├── 07-why-classical-bounds-fail-for-deep-networks.md
    │   ├── 08-implicit-bias-of-gradient-descent.md
    │   ├── 09-neural-tangent-kernel-and-lazy-training.md
    │   ├── 10-no-free-lunch-results-and-inductive-bias.md
    │   └── README.md
    ├── 04-Optimization-and-Training-Dynamics-Research/
    │   ├── Projects/
    │   │   ├── 01-optimizer-benchmark-with-fair-tuning.md
    │   │   ├── 02-edge-of-stability-and-sharpness-lab.md
    │   │   ├── 03-grokking-reproduction-and-ablation.md
    │   │   └── README.md
    │   ├── 01-stochastic-gradient-noise-and-its-link-to-generalization.md
    │   ├── 02-loss-landscapes-and-sharpness.md
    │   ├── 03-edge-of-stability-and-large-learning-rate-dynamics.md
    │   ├── 04-convergence-analysis-of-adaptive-methods-and-known-counterexamples.md
    │   ├── 05-second-order-and-preconditioned-methods-for-deep-networks.md
    │   ├── 06-large-batch-training-and-the-critical-batch-size.md
    │   ├── 07-grokking-and-phase-transitions-in-training.md
    │   ├── 08-feature-learning-versus-lazy-regimes-and-hyperparameter-transfer-across-width.md
    │   ├── 09-benchmarking-optimizers.md
    │   ├── 10-designing-and-testing-a-new-optimizer.md
    │   └── README.md
    ├── 05-Algorithm-Design-and-Developing-New-Methods/
    │   ├── Projects/
    │   │   ├── 01-new-method-on-a-toy-problem-then-real-data.md
    │   │   ├── 02-method-evolution-case-study.md
    │   │   ├── 03-library-grade-implementation.md
    │   │   └── README.md
    │   ├── 01-where-methods-come-from.md
    │   ├── 02-toy-problems-and-synthetic-tasks-that-isolate-a-phenomenon.md
    │   ├── 03-designing-objectives-and-architectures.md
    │   ├── 04-case-studies-of-method-evolution.md
    │   ├── 05-complexity-and-efficiency-analysis-of-a-new-method.md
    │   ├── 06-implementing-a-new-method-in-a-framework.md
    │   ├── 07-sensitivity-and-robustness-analysis.md
    │   ├── 08-failure-analysis-of-your-own-method.md
    │   ├── 09-honest-claims.md
    │   ├── 10-from-idea-to-library.md
    │   └── README.md
    ├── 06-Proofs-Derivations-and-Mathematical-Writing/
    │   ├── Projects/
    │   │   ├── 01-derive-and-verify-five-results.md
    │   │   ├── 02-find-the-flaw-exercises.md
    │   │   ├── 03-mini-theory-paper.md
    │   │   └── README.md
    │   ├── 01-reading-a-theorem.md
    │   ├── 02-proof-techniques-used-in-ml.md
    │   ├── 03-typical-proof-structure-in-learning-and-optimization-papers.md
    │   ├── 04-checking-derivations-numerically-with-automatic-differentiation-and-simulation.md
    │   ├── 05-common-errors-in-proofs-and-derivations-and-how-to-catch-them.md
    │   ├── 06-writing-precise-statements.md
    │   ├── 07-toy-theory.md
    │   ├── 08-the-interplay-of-theory-and-experiments.md
    │   ├── 09-formal-checking-tools.md
    │   └── README.md
    ├── 07-Research-Areas-Survey-Method-and-Open-Problems/
    │   ├── Projects/
    │   │   ├── 01-area-map-with-open-problem-list.md
    │   │   ├── 02-tractability-and-compute-feasibility-analysis.md
    │   │   ├── 03-expert-interview-and-reading-group.md
    │   │   └── README.md
    │   ├── 01-how-to-map-a-research-area.md
    │   ├── 02-area-map.md
    │   ├── 03-area-map-2.md
    │   ├── 04-area-map-3.md
    │   ├── 05-area-map-4.md
    │   ├── 06-area-map-5.md
    │   ├── 07-area-map-6.md
    │   ├── 08-area-map-7.md
    │   ├── 09-identifying-tractable-open-problems-for-small-teams-and-limited-compute.md
    │   ├── 10-choosing-an-area.md
    │   └── README.md
    ├── 08-Compute-Constrained-Research/
    │   ├── Projects/
    │   │   ├── 01-small-scale-study-of-a-large-model-phenomenon.md
    │   │   ├── 02-scaling-extrapolation-validity-test.md
    │   │   ├── 03-research-compute-plan.md
    │   │   └── README.md
    │   ├── 01-questions-that-can-be-answered-at-small-scale-and-questions-that-cannot.md
    │   ├── 02-using-public-checkpoints-datasets-and-benchmarks-as-shared-infrastructure.md
    │   ├── 03-compute-efficient-experiment-design.md
    │   ├── 04-scaling-law-style-extrapolation.md
    │   ├── 05-distillation-and-proxy-models-for-studying-large-model-behavior.md
    │   ├── 06-accessing-compute.md
    │   ├── 07-reproducing-large-scale-results-at-reduced-scale-and-reporting-what-was-changed.md
    │   ├── 08-theory-and-analysis-as-low-compute-contributions.md
    │   ├── 09-planning-a-research-agenda-around-a-fixed-budget.md
    │   └── README.md
    ├── 09-Academic-Writing-Peer-Review-and-Publishing/
    │   ├── Projects/
    │   │   ├── 01-workshop-style-paper-from-your-own-results.md
    │   │   ├── 02-three-peer-reviews.md
    │   │   ├── 03-rebuttal-simulation.md
    │   │   └── README.md
    │   ├── 01-paper-structure.md
    │   ├── 02-claims-versus-evidence.md
    │   ├── 03-figures-and-tables-that-communicate.md
    │   ├── 04-writing-clearly.md
    │   ├── 05-reproducibility-and-ethics-checklists-and-statements.md
    │   ├── 06-venues-and-tracks.md
    │   ├── 07-the-peer-review-process.md
    │   ├── 08-writing-a-good-review.md
    │   ├── 09-responding-to-reviews-and-handling-rejection.md
    │   ├── 10-preprints-code-and-artifact-release.md
    │   └── README.md
    ├── 10-Research-Integrity-Ethics-and-Responsible-Release/
    │   ├── Projects/
    │   │   ├── 01-reproducibility-audit-of-published-papers.md
    │   │   ├── 02-release-decision-memo.md
    │   │   ├── 03-research-ethics-case-analyses.md
    │   │   └── README.md
    │   ├── 01-research-integrity.md
    │   ├── 02-reproducibility-problems-in-published-ml-work-and-how-they-arose.md
    │   ├── 03-data-and-licensing-ethics-in-research.md
    │   ├── 04-dual-use-research.md
    │   ├── 05-open-and-staged-release-of-models-code-and-data.md
    │   ├── 06-environmental-cost-of-research-and-reporting-it.md
    │   ├── 07-authorship-credit-and-collaboration-norms.md
    │   ├── 08-conflicts-of-interest-and-industry-academia-relationships.md
    │   ├── 09-societal-impact-statements.md
    │   └── README.md
    ├── 11-Research-Careers-Collaboration-and-Ecosystem/
    │   ├── Projects/
    │   │   ├── 01-research-portfolio-and-profile.md
    │   │   ├── 02-opportunity-mapping-and-outreach-plan.md
    │   │   ├── 03-open-source-research-contribution.md
    │   │   └── README.md
    │   ├── 01-research-roles.md
    │   ├── 02-graduate-study.md
    │   ├── 03-research-internships-residencies-and-fellowships.md
    │   ├── 04-industry-and-academic-research-groups-in-india.md
    │   ├── 05-collaboration-and-mentorship.md
    │   ├── 06-open-source-research-software.md
    │   ├── 07-building-a-research-profile.md
    │   ├── 08-time-management-and-sustainability-in-research-work.md
    │   ├── 09-evaluating-opportunities.md
    │   └── README.md
    ├── 12-G14-Capstones/
    │   ├── 01-reproduce-and-extend-a-paper.md
    │   ├── 02-original-research-project.md
    │   ├── 03-theory-and-optimization-study.md
    │   ├── 04-peer-review-and-research-integrity-simulation.md
    │   ├── 05-g14-readiness-assessment.md
    │   └── README.md
    └── README.md
```

### 00 — G14 Overview

**Purpose:** the single authoritative plan for G14 with scope, boundaries, prerequisite map, research tooling and source register, reporting and integrity standards and completion gate.

- `01-g14-scope-and-boundaries-with-stage-5c-and-other-groups.md` — what G14 teaches and what it leaves to other stages and groups.
- `02-prerequisite-map-from-the-roadmap.md` — Roadmap lessons assumed for each G14 module, named precisely, with a self-check for the mathematics needed in modules 03, 04 and 06.
- `03-research-tooling-and-source-register.md` — every tool for search, references, experiment tracking and writing with version, licence and maintenance status, plus the register of primary sources relied on in each project.
- `04-research-reporting-and-integrity-standards.md` — pre-registration template, claim-evidence table, seed and budget reporting rules, negative-result policy and the report and paper templates.
- `05-completion-gate.md` — measurable criteria to finish G14.
- `learning-plan.md` — recommended order, a twelve-month research timeline and how to choose between a theory-leaning and an empirical-leaning path.

**Project 1: g14 research notebook and reproducibility bootstrap**  
- Data: one small published result with public code.  
- Task: build a research workspace with pinned tooling, a research logbook, a claim-evidence table template and an experiment harness that records seeds, budgets and environment, then reproduce the small result with it.  
- Deliverables: lockfile, logbook, templates, harness and the reproduction.  
- Pass gate: a clean machine reproduces the result from the lockfile and logbook, and the harness refuses to mark a comparison valid when tuning budgets differ.

### 01 — Research Foundations Problem Selection and Literature Strategy

**Outcome:** Choose research questions worth answering and survey a field efficiently. How to read a paper, the essential paper list, reproducing results and writing paper summaries are covered in Stage 5C and are not repeated.

**Lessons**

- `01-what-ml-research-is.md` — What ML research is: empirical, theoretical, methods, benchmark, systems and position work
- `02-choosing-problems.md` — Choosing problems: impact, tractability, novelty and your comparative advantage
- `03-turning-an-interest-into-a-research-question-and-a-falsifiable-hypothesis.md` — Turning an interest into a research question and a falsifiable hypothesis
- `04-literature-search.md` — Literature search: arXiv, citation graphs, venue proceedings and alert workflows
- `05-systematic-literature-review.md` — Systematic literature review: scoping, inclusion rules and synthesis tables
- `06-tracking-the-state-of-the-art-honestly.md` — Tracking the state of the art honestly: claims, benchmarks and what has changed since a paper appeared
- `07-reading-critically-for-weaknesses.md` — Reading critically for weaknesses: confounders, unfair baselines and unsupported claims
- `08-reference-and-note-management.md` — Reference and note management: building a searchable research notebook
- `09-writing-a-research-proposal.md` — Writing a research proposal: question, related work, plan, risks and success criteria
- `10-negative-and-null-results.md` — Negative and null results: recognizing and reporting them

**Hands-on projects**

- **Project 1: systematic review of a narrow topic**  
  - Data: A narrow topic of your choice with 30 to 50 papers from the last five years  
  - Task: Define scope and inclusion rules, build a synthesis table of claims, methods, datasets and weaknesses and identify three open questions.  
  - Deliverables: Review document and synthesis table.  
  - Pass gate: Inclusion rules fixed before searching and every open question linked to evidence in the table.
- **Project 2: claim tracking and state of the art audit**  
  - Data: Three headline claims from recent papers in one area  
  - Task: Trace each claim forward through later work and benchmarks to see whether it held, was refuted or was superseded.  
  - Deliverables: Audit report.  
  - Pass gate: Every conclusion cites the later papers or results it relies on.
- **Project 3: research proposal with risk analysis**  
  - Data: A question from the first project  
  - Task: Write a four-page proposal with hypotheses, experiments, baselines, compute budget, risks and a kill criterion, and have it reviewed by one peer.  
  - Deliverables: Proposal and written peer review.  
  - Pass gate: Proposal includes a stated result that would make you abandon the idea.

### 02 — Experimental Methodology and Research Engineering

**Outcome:** Run experiments that can support claims. Seed variance and hyperparameter fairness are discussed in G1, G4 and G13, reproducible training in Stages 5D and G2, and statistical comparison in G13; this module is the day-to-day research method.

**Lessons**

- `01-from-hypothesis-to-experiment.md` — From hypothesis to experiment: controls, confounders and the smallest experiment that could falsify the idea
- `02-baselines.md` — Baselines: choosing them, tuning them fairly and reproducing them from scratch
- `03-ablation-design.md` — Ablation design: isolating each component and avoiding interaction traps
- `04-research-debugging.md` — Research debugging: overfit-one-batch, unit tests for losses and gradient checks, and a catalog of silent bugs
- `05-proxy-tasks-and-small-scale-experiments.md` — Proxy tasks and small-scale experiments: when results transfer to larger scale and when they do not
- `06-sweeps-and-compute-budgeting.md` — Sweeps and compute budgeting: planning experiments before running them
- `07-research-code-structure.md` — Research code structure: config-driven experiments and separating exploration from reportable runs
- `08-research-logbooks.md` — Research logbooks: recording decisions, failures and dead ends
- `09-analyzing-results.md` — Analyzing results: looking at examples and failures, not only aggregate numbers
- `10-scaling-up-checks.md` — Scaling up checks: verifying that a small-scale win survives larger models and datasets

**Hands-on projects**

- **Project 1: ablation and baseline fairness study**  
  - Data: A published method with public code and a standard dataset  
  - Task: Reproduce the baseline and the method, tune both with equal budgets and ablate each component with several seeds.  
  - Deliverables: Study with ablation table and tuning-budget accounting.  
  - Pass gate: Equal tuning budgets and at least five seeds per cell.
- **Project 2: silent bug catalog for research code**  
  - Data: Research code you write  
  - Task: Plant ten classic bugs (leakage, wrong normalization, off-by-one in masking, train-eval mode errors, label shuffling) and write checks that detect each.  
  - Deliverables: Catalog and automated checks.  
  - Pass gate: Every planted bug is caught by a check.
- **Project 3: small scale transfer experiment**  
  - Data: A method evaluated at three model scales  
  - Task: Test whether conclusions from the smallest scale predict the larger ones and report where they break.  
  - Deliverables: Transfer analysis.  
  - Pass gate: Prediction made before running the larger scales.

### 03 — Learning Theory for ML Researchers

**Outcome:** Read and use the main results of learning theory. Concentration inequalities, expected versus empirical risk, bias and variance of estimators and optimization convergence rates are covered in Stages 4C and 5A; this module covers the formal framework and its modern challenges.

**Lessons**

- `01-the-learning-problem-formalized.md` — The learning problem formalized: hypothesis classes, risk and the realizable and agnostic settings
- `02-pac-learning-and-sample-complexity.md` — PAC learning and sample complexity
- `03-capacity-measures.md` — Capacity measures: VC dimension and Rademacher complexity
- `04-uniform-convergence-and-margin-bounds.md` — Uniform convergence and margin bounds
- `05-pac-bayes-bounds-and-their-use-for-neural-networks.md` — PAC-Bayes bounds and their use for neural networks
- `06-algorithmic-stability-and-generalization.md` — Algorithmic stability and generalization
- `07-why-classical-bounds-fail-for-deep-networks.md` — Why classical bounds fail for deep networks: interpolation, double descent and benign overfitting
- `08-implicit-bias-of-gradient-descent.md` — Implicit bias of gradient descent
- `09-neural-tangent-kernel-and-lazy-training.md` — Neural tangent kernel and lazy training: what it explains and what it misses
- `10-no-free-lunch-results-and-inductive-bias.md` — No-free-lunch results and inductive bias

**Hands-on projects**

- **Project 1: generalization bound numerical study**  
  - Data: Small networks and datasets where you can compute quantities  
  - Task: Compute several generalization bounds (norm-based and PAC-Bayes) for trained networks and compare with the true gap.  
  - Deliverables: Comparison and analysis of tightness.  
  - Pass gate: Every bound computed with stated assumptions and its code tested on a toy case.
- **Project 2: double descent reproduction**  
  - Data: Random-features or linear models on synthetic and real data  
  - Task: Reproduce double descent in model size and in training epochs and test how label noise and regularization change it.  
  - Deliverables: Reproduction and extension.  
  - Pass gate: Many seeds with intervals and an explanation tied to theory.
- **Project 3: implicit bias experiment**  
  - Data: Linearly separable and overparameterized regression problems  
  - Task: Show the solution gradient descent selects and compare with the theoretical prediction.  
  - Deliverables: Experiment and comparison with theory.  
  - Pass gate: Theoretical prediction stated before running.

### 04 — Optimization and Training Dynamics Research

**Outcome:** Study why training behaves as it does and evaluate new optimizers rigorously. Optimization theory and the standard optimizers are covered in Stage 4C and the tuning playbook in Stage 5C.

**Lessons**

- `01-stochastic-gradient-noise-and-its-link-to-generalization.md` — Stochastic gradient noise and its link to generalization
- `02-loss-landscapes-and-sharpness.md` — Loss landscapes and sharpness: measures, pitfalls and what they predict
- `03-edge-of-stability-and-large-learning-rate-dynamics.md` — Edge of stability and large learning rate dynamics
- `04-convergence-analysis-of-adaptive-methods-and-known-counterexamples.md` — Convergence analysis of adaptive methods and known counterexamples
- `05-second-order-and-preconditioned-methods-for-deep-networks.md` — Second-order and preconditioned methods for deep networks: Shampoo-style and orthogonalization-based optimizers
- `06-large-batch-training-and-the-critical-batch-size.md` — Large-batch training and the critical batch size
- `07-grokking-and-phase-transitions-in-training.md` — Grokking and phase transitions in training
- `08-feature-learning-versus-lazy-regimes-and-hyperparameter-transfer-across-width.md` — Feature learning versus lazy regimes and hyperparameter transfer across width
- `09-benchmarking-optimizers.md` — Benchmarking optimizers: time-to-result protocols and the AlgoPerf-style design
- `10-designing-and-testing-a-new-optimizer.md` — Designing and testing a new optimizer: toy problems, ablations and fair tuning

**Hands-on projects**

- **Project 1: optimizer benchmark with fair tuning**  
  - Data: Three workloads such as a CNN, a small transformer and a recommendation model  
  - Task: Compare several optimizers with equal tuning budgets and time-to-target metrics.  
  - Deliverables: Benchmark with intervals.  
  - Pass gate: Tuning budget identical per optimizer and per workload.
- **Project 2: edge of stability and sharpness lab**  
  - Data: A small network on a standard dataset  
  - Task: Measure sharpness over training under different learning rates and compare with published behavior.  
  - Deliverables: Reproduction and analysis.  
  - Pass gate: Sharpness metric validated on a toy quadratic.
- **Project 3: grokking reproduction and ablation**  
  - Data: Modular arithmetic tasks with small transformers  
  - Task: Reproduce delayed generalization and test the effect of weight decay, data fraction and optimizer.  
  - Deliverables: Reproduction and ablation.  
  - Pass gate: Many seeds with the timing of generalization reported.

### 05 — Algorithm Design and Developing New Methods

**Outcome:** Invent, implement and test new learning methods. Custom autograd and training frameworks are covered in G2 and experimental discipline in module 02.

**Lessons**

- `01-where-methods-come-from.md` — Where methods come from: failure modes, inductive biases, borrowed ideas and constraints
- `02-toy-problems-and-synthetic-tasks-that-isolate-a-phenomenon.md` — Toy problems and synthetic tasks that isolate a phenomenon
- `03-designing-objectives-and-architectures.md` — Designing objectives and architectures: principled choices versus tricks
- `04-case-studies-of-method-evolution.md` — Case studies of method evolution: normalization, residual connections, attention, low-rank adaptation and tiled attention kernels
- `05-complexity-and-efficiency-analysis-of-a-new-method.md` — Complexity and efficiency analysis of a new method
- `06-implementing-a-new-method-in-a-framework.md` — Implementing a new method in a framework: clean, tested and benchmarked code
- `07-sensitivity-and-robustness-analysis.md` — Sensitivity and robustness analysis: hyperparameters, data scale and random seeds
- `08-failure-analysis-of-your-own-method.md` — Failure analysis of your own method: where and why it breaks
- `09-honest-claims.md` — Honest claims: scope, assumptions and limitations of a result
- `10-from-idea-to-library.md` — From idea to library: documentation, packaging and releasing a method

**Hands-on projects**

- **Project 1: new method on a toy problem then real data**  
  - Data: A synthetic task you design and one real benchmark  
  - Task: Propose a small modification to an existing method, show it fixes a failure mode on the toy task and test whether it helps on real data against tuned baselines.  
  - Deliverables: Method description, code, experiments and limitations.  
  - Pass gate: Result stated as positive, negative or mixed with evidence and intervals.
- **Project 2: method evolution case study**  
  - Data: Original papers and later critiques of one widely used technique  
  - Task: Reconstruct how the technique emerged, which parts proved essential in later ablations and which were incidental, and reimplement the minimal version.  
  - Deliverables: Case study and minimal implementation.  
  - Pass gate: Minimal version matches the original on a stated benchmark.
- **Project 3: library grade implementation**  
  - Data: A method from the previous projects  
  - Task: Package it with tests, documentation, benchmarks and a reproducibility script usable by an outsider.  
  - Deliverables: Installable package.  
  - Pass gate: An outside user reproduces the headline result from the instructions.

### 06 — Proofs Derivations and Mathematical Writing

**Outcome:** Read, check and write the mathematics that appears in ML papers. The underlying probability, linear algebra and calculus are covered in Stages 4A to 4C; this module is about proof technique and derivation practice.

**Lessons**

- `01-reading-a-theorem.md` — Reading a theorem: assumptions, quantifiers and what is really claimed
- `02-proof-techniques-used-in-ml.md` — Proof techniques used in ML: induction, contradiction, coupling and symmetrization
- `03-typical-proof-structure-in-learning-and-optimization-papers.md` — Typical proof structure in learning and optimization papers: lemmas, appendices and constants
- `04-checking-derivations-numerically-with-automatic-differentiation-and-simulation.md` — Checking derivations numerically with automatic differentiation and simulation
- `05-common-errors-in-proofs-and-derivations-and-how-to-catch-them.md` — Common errors in proofs and derivations and how to catch them
- `06-writing-precise-statements.md` — Writing precise statements: notation, definitions and avoiding ambiguity
- `07-toy-theory.md` — Toy theory: proving a small result about a simplified model to explain an observation
- `08-the-interplay-of-theory-and-experiments.md` — The interplay of theory and experiments: predictions, tests and honest gaps
- `09-formal-checking-tools.md` — Formal checking tools: a first look at proof assistants and what they can verify

**Hands-on projects**

- **Project 1: derive and verify five results**  
  - Data: Five standard results such as a convergence rate, a generalization bound and a gradient identity  
  - Task: Derive each from scratch, then verify numerically with simulation or automatic differentiation.  
  - Deliverables: Derivations and verification code.  
  - Pass gate: Every derivation has an executed numerical check.
- **Project 2: find the flaw exercises**  
  - Data: Proofs with planted errors that you or a partner construct  
  - Task: Find and explain subtle flaws such as a missing assumption or an incorrect exchange of limits.  
  - Deliverables: Flaw catalog.  
  - Pass gate: Each flaw demonstrated by a counterexample or numerical test.
- **Project 3: mini theory paper**  
  - Data: A phenomenon observed in an earlier experiment  
  - Task: Prove a small result in a simplified model that predicts the phenomenon and test the prediction empirically.  
  - Deliverables: Two-page theory note with experiments.  
  - Pass gate: Assumptions stated and the gap between model and practice discussed.

### 07 — Research Areas Survey Method and Open Problems

**Outcome:** Enter a research area with a map of its questions, methods, evidence and open problems. This module teaches the survey method and applies it to areas; it does not assert current state-of-the-art results, which change quickly and must be read from primary sources.

**Lessons**

- `01-how-to-map-a-research-area.md` — How to map a research area: questions, methods, datasets, metrics and venues
- `02-area-map.md` — Area map: generalization and scaling behavior
- `03-area-map-2.md` — Area map: reasoning, post-training and evaluation of language models
- `04-area-map-3.md` — Area map: generative modeling and representation learning
- `05-area-map-4.md` — Area map: reinforcement learning and sequential decision-making
- `06-area-map-5.md` — Area map: interpretability and model understanding
- `07-area-map-6.md` — Area map: efficient, trustworthy and privacy-preserving machine learning
- `08-area-map-7.md` — Area map: machine learning for science, graphs, causality and probabilistic methods
- `09-identifying-tractable-open-problems-for-small-teams-and-limited-compute.md` — Identifying tractable open problems for small teams and limited compute
- `10-choosing-an-area.md` — Choosing an area: fit with skills, mentors, data and compute

**Hands-on projects**

- **Project 1: area map with open problem list**  
  - Data: One area of your choice and 40 or more primary sources  
  - Task: Build a map of questions, methods, datasets, metrics and venues, with a ranked list of open problems and the evidence behind each ranking.  
  - Deliverables: Area map and ranked problem list.  
  - Pass gate: Every ranking claim cites sources and no unverified state-of-the-art claim appears.
- **Project 2: tractability and compute feasibility analysis**  
  - Data: Five open problems from your map  
  - Task: Estimate for each the data, compute and time needed and the first experiment, and choose one to pursue.  
  - Deliverables: Feasibility table.  
  - Pass gate: Estimates made from measured small-scale runs where possible.
- **Project 3: expert interview and reading group**  
  - Data: A researcher or lab willing to talk, and a reading group you form  
  - Task: Interview an expert about the area and run a reading group of at least four sessions with written takeaways.  
  - Deliverables: Interview notes and session notes.  
  - Pass gate: Interviewee consent obtained and claims attributed accurately.

### 08 — Compute Constrained Research

**Outcome:** Do credible research without a large cluster. Compute access programs and costs are covered in G10 and small-scale scaling-law fitting in G3; this module is the research strategy.

**Lessons**

- `01-questions-that-can-be-answered-at-small-scale-and-questions-that-cannot.md` — Questions that can be answered at small scale and questions that cannot
- `02-using-public-checkpoints-datasets-and-benchmarks-as-shared-infrastructure.md` — Using public checkpoints, datasets and benchmarks as shared infrastructure
- `03-compute-efficient-experiment-design.md` — Compute-efficient experiment design: fewer seeds where valid, early stopping and successive halving
- `04-scaling-law-style-extrapolation.md` — Scaling-law style extrapolation: validity, error bars and limits
- `05-distillation-and-proxy-models-for-studying-large-model-behavior.md` — Distillation and proxy models for studying large-model behavior
- `06-accessing-compute.md` — Accessing compute: academic clusters, credits, national programs in India and collaboration
- `07-reproducing-large-scale-results-at-reduced-scale-and-reporting-what-was-changed.md` — Reproducing large-scale results at reduced scale and reporting what was changed
- `08-theory-and-analysis-as-low-compute-contributions.md` — Theory and analysis as low-compute contributions
- `09-planning-a-research-agenda-around-a-fixed-budget.md` — Planning a research agenda around a fixed budget

**Hands-on projects**

- **Project 1: small scale study of a large model phenomenon**  
  - Data: Public small model checkpoints  
  - Task: Design a study of a phenomenon reported at large scale using models you can afford and report what transfers.  
  - Deliverables: Study report.  
  - Pass gate: Scale differences and their possible effect on conclusions stated explicitly.
- **Project 2: scaling extrapolation validity test**  
  - Data: A model family trained at several sizes  
  - Task: Fit scaling curves on small sizes and predict held-out larger sizes with intervals.  
  - Deliverables: Prediction accuracy analysis.  
  - Pass gate: Held-out sizes never used in fitting.
- **Project 3: research compute plan**  
  - Data: A research proposal from module 01  
  - Task: Write a compute plan with estimates, fallbacks, access routes and cost, and compare with measured usage after a pilot.  
  - Deliverables: Plan and pilot comparison.  
  - Pass gate: Estimates compared with measured use and differences explained.

### 09 — Academic Writing Peer Review and Publishing

**Outcome:** Communicate research clearly and take part in peer review. Writing paper summaries is covered in Stage 5C; this module covers writing papers, reviewing and publishing.

**Lessons**

- `01-paper-structure.md` — Paper structure: abstract, introduction claims, related work, methods, experiments and limitations
- `02-claims-versus-evidence.md` — Claims versus evidence: aligning every claim with a result
- `03-figures-and-tables-that-communicate.md` — Figures and tables that communicate: design, captions and honest scale
- `04-writing-clearly.md` — Writing clearly: structure, concision and common errors
- `05-reproducibility-and-ethics-checklists-and-statements.md` — Reproducibility and ethics checklists and statements
- `06-venues-and-tracks.md` — Venues and tracks: conferences, journals, workshops and preprints, and what each is for
- `07-the-peer-review-process.md` — The peer-review process: submission, reviews, rebuttal and decisions
- `08-writing-a-good-review.md` — Writing a good review: summarizing, evidence-based criticism and constructive suggestions
- `09-responding-to-reviews-and-handling-rejection.md` — Responding to reviews and handling rejection
- `10-preprints-code-and-artifact-release.md` — Preprints, code and artifact release: norms and licences

**Hands-on projects**

- **Project 1: workshop style paper from your own results**  
  - Data: Results from an earlier module  
  - Task: Write a full six-to-eight page paper with claims tied to evidence, a limitations section and a reproducibility checklist.  
  - Deliverables: Paper draft.  
  - Pass gate: A reader unfamiliar with the work can reproduce the main result from the paper and artifacts.
- **Project 2: three peer reviews**  
  - Data: Three recent open-access papers outside your specialty, or peers' drafts with permission  
  - Task: Write structured reviews and compare them with public reviews on the same papers if available.  
  - Deliverables: Reviews and comparison notes.  
  - Pass gate: Each criticism is tied to specific evidence in the paper.
- **Project 3: rebuttal simulation**  
  - Data: Reviews of your draft from a peer group  
  - Task: Write a point-by-point response that distinguishes accepted changes, new evidence and respectful disagreement, and revise the paper.  
  - Deliverables: Rebuttal and revised paper.  
  - Pass gate: Every new claim in the rebuttal backed by an added experiment or analysis.

### 10 — Research Integrity Ethics and Responsible Release

**Outcome:** Do research honestly and decide responsibly what to publish and release. Safety evaluation and governance are covered in G12 and evaluation integrity in G13.

**Lessons**

- `01-research-integrity.md` — Research integrity: fabrication, selective reporting and questionable practices in ML
- `02-reproducibility-problems-in-published-ml-work-and-how-they-arose.md` — Reproducibility problems in published ML work and how they arose
- `03-data-and-licensing-ethics-in-research.md` — Data and licensing ethics in research: consent, scraped data and dataset terms
- `04-dual-use-research.md` — Dual-use research: weighing benefits and risks before publishing
- `05-open-and-staged-release-of-models-code-and-data.md` — Open and staged release of models, code and data: arguments and decision frameworks
- `06-environmental-cost-of-research-and-reporting-it.md` — Environmental cost of research and reporting it
- `07-authorship-credit-and-collaboration-norms.md` — Authorship, credit and collaboration norms
- `08-conflicts-of-interest-and-industry-academia-relationships.md` — Conflicts of interest and industry-academia relationships
- `09-societal-impact-statements.md` — Societal impact statements: writing them honestly

**Hands-on projects**

- **Project 1: reproducibility audit of published papers**  
  - Data: Five open-access papers with released code  
  - Task: Attempt to reproduce the headline result of each and categorize causes of any failure.  
  - Deliverables: Audit report.  
  - Pass gate: Every attempt documented with versions and communication with authors where possible.
- **Project 2: release decision memo**  
  - Data: A model or dataset you have built  
  - Task: Write a release decision memo covering benefits, risks, mitigations and the chosen release level.  
  - Deliverables: Decision memo.  
  - Pass gate: Risks and benefits supported by evidence, with dissenting views noted.
- **Project 3: research ethics case analyses**  
  - Data: Public ethics controversies from ML research  
  - Task: Analyze at least four cases for what went wrong, early signals and process fixes.  
  - Deliverables: Case analyses.  
  - Pass gate: Facts cited to primary reports with dates.

### 11 — Research Careers Collaboration and Ecosystem

**Outcome:** Plan a path into ML research and build the network and profile that support it. Institution names and programs named in this module must be verified from official sources when you use them.

**Lessons**

- `01-research-roles.md` — Research roles: research engineer, applied scientist, research scientist and academic researcher
- `02-graduate-study.md` — Graduate study: master's by research, PhD routes in India and abroad, and what admission committees look for
- `03-research-internships-residencies-and-fellowships.md` — Research internships, residencies and fellowships
- `04-industry-and-academic-research-groups-in-india.md` — Industry and academic research groups in India: how to find and approach them
- `05-collaboration-and-mentorship.md` — Collaboration and mentorship: working with advisors, peers and open communities
- `06-open-source-research-software.md` — Open-source research software: contributing and maintaining
- `07-building-a-research-profile.md` — Building a research profile: preprints, code, talks, posters and a research blog
- `08-time-management-and-sustainability-in-research-work.md` — Time management and sustainability in research work
- `09-evaluating-opportunities.md` — Evaluating opportunities: advisors, labs, incentives and fit

**Hands-on projects**

- **Project 1: research portfolio and profile**  
  - Data: Your projects across the specialization  
  - Task: Assemble a portfolio with a research statement, a curated set of reproducible projects, a preprint-ready paper and a public profile.  
  - Deliverables: Portfolio and statement.  
  - Pass gate: Every claim in the portfolio links to code or a report.
- **Project 2: opportunity mapping and outreach plan**  
  - Data: Public listings of labs, programs and fellowships  
  - Task: Map opportunities against your interests and profile, write tailored outreach messages and track responses over eight weeks.  
  - Deliverables: Opportunity map, messages and response log.  
  - Pass gate: Program details verified from official pages and dated.
- **Project 3: open source research contribution**  
  - Data: An open research library or benchmark  
  - Task: Contribute a reviewed fix, test, reproduction or documentation improvement.  
  - Deliverables: Accepted or reviewed contribution.  
  - Pass gate: Contribution follows the project's guidelines and is reviewed by a maintainer.

### 12 — G14 Capstones

**Outcome:** produce research-quality work that could be submitted to a workshop or journal. Choose at least two capstones, one of them the original research project or the theory and optimization study.

- **Capstone 1: reproduce and extend a paper** (uses Modules 01, 02, 09)  
  Reproduce a published result with equal-budget baselines, extend it with one new ablation or setting and write the replication and extension as a short paper with an honest limitations section.
- **Capstone 2: original research project** (uses Modules 01, 02, 05, 08, 09)  
  Carry out a hypothesis-driven research project with a registered plan, strong baselines, ablations and sensitivity analysis, written up as a workshop-style paper with a release of code and data.
- **Capstone 3: theory and optimization study** (uses Modules 03, 04, 06)  
  Study a theoretical or training-dynamics question with a proof or derivation, numerical verification and experiments that test the prediction.
- **Capstone 4: peer review and research integrity simulation** (uses Modules 09, 10)  
  Participate in a simulated conference cycle: submit, review three papers, write a rebuttal and produce a reproducibility audit of another participant's work.
- **Capstone 5: g14 readiness assessment** (uses All modules)  
  Written and practical assessment against the G14 completion gate.

## G14 completion gate

- Every empirical claim is supported by a registered plan, equal-budget tuned baselines, at least five seeds and intervals, and ablations of each component.
- Every theoretical or derived claim has stated assumptions and an executed numerical check.
- Every paper or report links each claim to specific evidence and includes a limitations section and a reproducibility checklist.
- Every reproduction states exactly what was changed from the original and why.
- Every project records data licences, sources and tool versions, and none states a state-of-the-art claim without a primary-source citation and date.
- All results reproduce from a lockfile, configs, logged seeds and recorded environments, and an outside person has reproduced at least one of them.
- At least one negative or inconclusive result is reported honestly in full.
- Research integrity, compute-cost and release-decision statements are included for every capstone.
- At least two capstones are complete and the readiness assessment is passed.

## Audit and verification

**What was checked and the result**

- Structure: 11 specialist modules each have 6 to 12 lessons and at least one project; the tree contains 177 files and 25 folders, and these counts equal the counts computed from the curriculum data. The overview file names listed in the description were checked to appear in the tree.
- Overlap with the Roadmap: all 106 lesson file names were compared against every lesson file name in `Roadmap.md`. Exact matches: 0. Near matches (similarity 0.80 or higher): 2 — `benchmarking-optimizers` vs Roadmap `benchmarking-pipelines` (0.8); `paper-structure` vs Roadmap `heap-structure` (0.83). Reviewed manually: optimizer benchmarking versus the Stage 2C data-pipeline benchmarking lesson, and the structure of a research paper versus the Stage 3 heap data structure, are unrelated topics.
- Structural problems found by the build script: 0.
- Topic-level overlap check: the Roadmap contains the Stage 5C module on reading and reproducing ML papers (how to read a paper, the essential paper list, reproducing results and writing paper summaries), which is why module 01 starts at problem selection and literature strategy and module 09 covers writing full papers and peer review instead of summaries. Stage 4C contains concentration inequalities, empirical risk and generalization, optimization theory and optimizers, which is why modules 03 and 04 start at formal learning theory and training-dynamics research. PAC learning, VC dimension, Rademacher complexity, PAC-Bayes, double descent, edge of stability, grokking, AlgoPerf, proof techniques and peer review were not found as lessons anywhere in the Roadmap.
- Verified by web search on the build date (2026-10-26): Papers with Code was shut down in July 2025 and Hugging Face's Trending Papers is the nearest replacement but does not replace its benchmark leaderboards, so lessons must not depend on Papers with Code; AlgoPerf is MLCommons' time-to-result training-algorithm benchmark with a training-algorithm track and a model track; the NeurIPS paper checklist originated as a reproducibility measure, was required from NeurIPS 2019 and covers reproducibility, transparency, ethics and societal impact.
- Reported but not confirmed: the current NeurIPS checklist text and its policy on language models in peer review, and the current policies of other venues, were not confirmed and must be read from each venue's site; the arXiv policy on review and position papers in computer science was not searched; the Muon optimizer and the edge-of-stability, grokking, double-descent, PAC-Bayes and implicit-bias literatures are cited from established research and were not re-checked here, so each reading list must be built from primary sources; names of Indian institutions, fellowships and programs in module 11 were not verified and must be confirmed from official pages.
- Not verified: library and tool versions, venue deadlines and policies, and any state-of-the-art claim, none of which this plan asserts.
- Not verified by execution: no code in this plan has been run. Project pass gates are acceptance criteria to be met when the projects are built.
- Integrity and safety note: research projects that involve people (interviews, user studies, outreach) need consent and honest attribution; reproduction audits must be conducted courteously and shared with authors before public posting; dual-use findings should follow the release framework of module 10.
- Repository safety: this build created only this file; no existing file or folder was created, changed or deleted by it.
