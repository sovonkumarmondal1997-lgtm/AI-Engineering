# Project Tree — Senior Applied AI Engineer Roadmap

This is the folder and file plan that follows [`Roadmap.md`](./Roadmap.md) stage by stage.
Every stage and module here matches a stage and module in the roadmap, in the same order.

## How to read this tree

- **Stages 0–2 already exist** in this repository. Their module folders are listed from disk, with file counts.
- **Stages 3–18 are new.** Create each folder only when you start that stage, the same rule the repo already uses.
- Naming follows the existing repo conventions:
  - Stage folder: a readable title, e.g. `Mathematics for Machine Learning/`
  - Stage overview: `00-Stage-N-Overview/` with `README.md`, `learning-plan.md` and the stage project in `Projects/`
  - Module folder: `NN-Title-In-Kebab-Case/`
  - Lesson file: `NN-lesson-name.md`
  - Every module has `README.md`, its lessons, `practice-questions.md` and a hands-on lab in `Projects/`
- **Stage 16 (Flagship Portfolio Projects)** is laid out as real GitHub-style repositories, because those are what hiring managers open.

## 1. Top-level layout

```text
AI Engineering/
├── README.md
├── Roadmap.md
├── Roadmap_ptree.md
├── Computer & Digital Foundation/           # Stage 0 (exists)
├── Programming & Computational Thinking/    # Stage 1 (exists)
├── Python for Data Engineering_1/           # Stage 2 (exists)
├── Python for Data Engineering_2/           # Stage 2B (exists)
├── Data Structures & Algorithms/            # Stage 3
├── Mathematics for Machine Learning/        # Stage 4
├── Machine Learning Foundations/            # Stage 5
├── Deep Learning & Transformers/            # Stage 6
├── Backend Engineering for AI Systems/      # Stage 7
├── LLM Application Engineering/             # Stage 8
├── Retrieval & RAG Systems/                 # Stage 9
├── Evaluation & Experimentation/            # Stage 10
├── AI Agents & Tool Use/                    # Stage 11
├── AI Safety, Security & Responsible AI/    # Stage 12
├── Model Customization & Inference/         # Stage 13
├── LLMOps & AI System Design/               # Stage 14
├── Applied AI in the Field/                 # Stage 15
├── Flagship Portfolio Projects/             # Stage 16
├── Interview Preparation & Getting Hired/   # Stage 17
└── Career Growth to Senior/                 # Stage 18
```

## 2. Existing stages (0–2) — already in this repository

These folders already exist, and their lesson files are written. Only the module level is shown here, to keep the tree readable.

### Stage 0 — `Computer & Digital Foundation/`

```text
Computer & Digital Foundation/
├── 00-Stage-0-Overview/   (4 files — already written)
├── 01-How-Computers-Work/   (23 files — already written)
├── 02-Operating-System-Fundamentals/   (19 files — already written)
├── 03-Command-Line/   (15 files — already written)
├── 04-Developer-Environment/   (17 files — already written)
└── README.md
```

### Stage 1 — `Programming & Computational Thinking/`

```text
Programming & Computational Thinking/
├── 00-Stage-1-Overview/   (7 files — already written)
├── 01-Computational-Thinking-and-Program-Design/   (11 files — already written)
├── 02-Python-Core-Language-and-Data-Types/   (12 files — already written)
├── 03-Control-Flow-Functions-Scope-and-Errors/   (9 files — already written)
├── 04-Problem-Solving-Collections-and-Algorithmic-Habits/   (10 files — already written)
├── 05-Text-Files-Structured-Data-and-CLI-Programs/   (11 files — already written)
├── 06-Modules-Packages-Dependencies-and-Code-Quality/   (9 files — already written)
├── 07-Testing-and-Systematic-Debugging/   (9 files — already written)
├── 08-Object-Oriented-Design-Data-Modelling-and-Functional-Style/   (10 files — already written)
├── 09-Advanced-Production-Oriented-Python-Foundations/   (13 files — already written)
├── 10-Production-Habits-for-Python-Programs/   (10 files — already written)
└── README.md
```

### Stage 2 — `Python for Data Engineering_1/`

```text
Python for Data Engineering_1/
├── 00-Stage-2-Overview/   (17 files — already written)
├── 01-Data-Engineering-Foundations-and-Pipeline-Thinking/   (11 files — already written)
├── 02-Numerical-Computing-with-NumPy/   (9 files — already written)
├── 03-DataFrames-with-pandas/   (17 files — already written)
├── 04-Columnar-Engines-Arrow-Polars-and-DuckDB/   (12 files — already written)
├── 05-Data-Formats-Compression-and-File-Layout/   (13 files — already written)
├── 06-SQL-for-Data-Engineers/   (14 files — already written)
├── 07-Python-Database-Connectivity/   (13 files — already written)
├── 08-Data-Modelling-for-Analytics/   (12 files — already written)
├── 09-Data-Ingestion-and-Extraction-Patterns/   (14 files — already written)
├── 10-Concurrency-and-Parallelism-in-Practice/   (12 files — already written)
├── 11-Data-Validation-Contracts-and-Quality/   (12 files — already written)
├── 12-Transformation-Patterns-and-Pipeline-Design/   (13 files — already written)
├── 13-Orchestration-and-Workflow-Management/   (14 files — already written)
├── 14-Distributed-Processing-with-PySpark/   (20 files — already written)
├── 15-Lakehouse-Table-Formats/   (12 files — already written)
├── 16-Streaming-and-Event-Driven-Data/   (17 files — already written)
├── 17-Cloud-Storage-and-Cloud-Data-Platforms/   (12 files — already written)
├── 18-Containers-Infrastructure-and-CI-CD-for-Data/   (10 files — already written)
├── 19-Testing-Data-Pipelines/   (10 files — already written)
├── 20-Observability-Lineage-Governance-and-Security/   (13 files — already written)
├── 21-Performance-Scaling-and-Cost-Optimization/   (10 files — already written)
└── 22-Serving-Data-for-Analytics-ML-and-AI/   (8 files — already written)
```

### Stage 2B — Data Engineering Gap Modules — `Python for Data Engineering_2/`

```text
Python for Data Engineering_2/
├── 00-Gap-Modules-Overview/   (13 files — already written)
├── 01-Docker-Essentials-for-Data-Labs/   (13 files — already written)
├── 02-Linux-and-Shell-for-Data-Servers/   (13 files — already written)
├── 03-AWS-Data-Engineering-Deep-Dive/   (19 files — already written)
├── 04-Databricks-Lakehouse-Platform-Deep-Dive/   (19 files — already written)
├── 05-Data-Engineering-System-Design-Interviews/   (22 files — already written)
└── README.md
```

## 3. New stages (3–18) — full file plan

### Stage 3 — Data Structures & Algorithms — `Data Structures & Algorithms/`

```text
Data Structures & Algorithms/
├── README.md
├── 00-Stage-3-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-algorithm-toolkit-and-benchmark.md
├── 01-Complexity-and-Big-O/
│   ├── README.md
│   ├── 01-what-an-algorithm-is.md
│   ├── 02-counting-steps-and-growth.md
│   ├── 03-big-o-notation.md
│   ├── 04-time-vs-space-complexity.md
│   ├── 05-amortized-analysis.md
│   ├── 06-measuring-real-performance-in-python.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-benchmark-python-collections.md
├── 02-Arrays-Strings-and-Hashing/
│   ├── README.md
│   ├── 01-arrays-and-dynamic-arrays.md
│   ├── 02-strings-and-immutability.md
│   ├── 03-hash-tables-internals.md
│   ├── 04-hash-map-and-set-patterns.md
│   ├── 05-prefix-sums.md
│   ├── 06-frequency-counting-patterns.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-build-a-hash-map-from-scratch.md
├── 03-Two-Pointers-Sliding-Window-and-Binary-Search/
│   ├── README.md
│   ├── 01-two-pointers.md
│   ├── 02-sliding-window.md
│   ├── 03-binary-search.md
│   ├── 04-binary-search-on-the-answer.md
│   ├── 05-pattern-recognition-drills.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-log-window-analyzer.md
├── 04-Stacks-Queues-and-Linked-Lists/
│   ├── README.md
│   ├── 01-stacks.md
│   ├── 02-queues-and-deques.md
│   ├── 03-monotonic-stack.md
│   ├── 04-singly-and-doubly-linked-lists.md
│   ├── 05-lru-cache-design.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-implement-an-lru-cache.md
├── 05-Recursion-Backtracking-and-Sorting/
│   ├── README.md
│   ├── 01-recursion-and-the-call-stack.md
│   ├── 02-backtracking.md
│   ├── 03-sorting-algorithms.md
│   ├── 04-merge-sort-and-quick-sort.md
│   ├── 05-divide-and-conquer.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-sorting-benchmark.md
├── 06-Trees-and-Tries/
│   ├── README.md
│   ├── 01-tree-terminology.md
│   ├── 02-tree-traversals.md
│   ├── 03-binary-search-trees.md
│   ├── 04-balanced-trees-intuition.md
│   ├── 05-tries-and-prefix-search.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-autocomplete-with-a-trie.md
├── 07-Heaps-and-Priority-Queues/
│   ├── README.md
│   ├── 01-heap-structure.md
│   ├── 02-heapq-in-python.md
│   ├── 03-top-k-problems.md
│   ├── 04-merging-sorted-streams.md
│   ├── 05-scheduling-with-priority-queues.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-top-k-streaming-tracker.md
├── 08-Graphs-BFS-DFS-and-Shortest-Paths/
│   ├── README.md
│   ├── 01-graph-representations.md
│   ├── 02-breadth-first-search.md
│   ├── 03-depth-first-search.md
│   ├── 04-topological-sort.md
│   ├── 05-union-find.md
│   ├── 06-dijkstra-shortest-paths.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-dependency-resolver.md
├── 09-Dynamic-Programming/
│   ├── README.md
│   ├── 01-what-dynamic-programming-is.md
│   ├── 02-memoization-vs-tabulation.md
│   ├── 03-one-dimensional-dp-patterns.md
│   ├── 04-two-dimensional-dp-patterns.md
│   ├── 05-edit-distance-and-sequence-alignment.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-fuzzy-text-matcher.md
└── 10-Coding-Interview-Method/
    ├── README.md
    ├── 01-structured-problem-solving-framework.md
    ├── 02-communicating-while-coding.md
    ├── 03-testing-and-edge-cases.md
    ├── 04-spaced-repetition-practice-system.md
    ├── 05-mock-interview-routine.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-practice-log-first-50-problems.md
```

### Stage 4 — Mathematics for Machine Learning — `Mathematics for Machine Learning/`

```text
Mathematics for Machine Learning/
├── README.md
├── 00-Stage-4-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-math-for-ml-notebook-library.md
├── 01-Math-Refresher-and-Notation/
│   ├── README.md
│   ├── 01-numbers-and-algebra-refresher.md
│   ├── 02-functions-and-graphs.md
│   ├── 03-exponents-and-logarithms.md
│   ├── 04-summation-and-product-notation.md
│   ├── 05-reading-math-in-papers.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-plot-common-functions.md
├── 02-Vectors-and-Vector-Spaces/
│   ├── README.md
│   ├── 01-what-a-vector-is.md
│   ├── 02-vector-operations.md
│   ├── 03-dot-product-and-projection.md
│   ├── 04-norms-and-distance.md
│   ├── 05-linear-independence-and-span.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-vectors-in-numpy.md
├── 03-Matrices-and-Linear-Transformations/
│   ├── README.md
│   ├── 01-matrices-as-data-and-functions.md
│   ├── 02-matrix-multiplication.md
│   ├── 03-transpose-inverse-and-identity.md
│   ├── 04-matrix-shapes-and-broadcasting.md
│   ├── 05-eigenvalues-and-eigenvectors.md
│   ├── 06-svd-and-low-rank-approximation.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-image-compression-with-svd.md
├── 04-Similarity-Distance-and-Embedding-Math/
│   ├── README.md
│   ├── 01-cosine-similarity.md
│   ├── 02-euclidean-vs-cosine.md
│   ├── 03-high-dimensional-geometry.md
│   ├── 04-nearest-neighbors-intuition.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-word-vector-similarity-explorer.md
├── 05-Derivatives-and-Gradients/
│   ├── README.md
│   ├── 01-rates-of-change.md
│   ├── 02-derivative-rules.md
│   ├── 03-partial-derivatives.md
│   ├── 04-gradients.md
│   ├── 05-numerical-vs-analytical-derivatives.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-numerical-gradient-checker.md
├── 06-Chain-Rule-and-Optimization/
│   ├── README.md
│   ├── 01-the-chain-rule.md
│   ├── 02-computational-graphs.md
│   ├── 03-gradient-descent.md
│   ├── 04-learning-rate-and-convergence.md
│   ├── 05-sgd-momentum-and-adam-intuition.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-gradient-descent-visualizer.md
├── 07-Probability-Fundamentals/
│   ├── README.md
│   ├── 01-events-and-probability.md
│   ├── 02-conditional-probability.md
│   ├── 03-bayes-theorem.md
│   ├── 04-random-variables.md
│   ├── 05-expectation-and-variance.md
│   ├── 06-independence-and-correlation.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-probability-simulations.md
├── 08-Distributions-and-Sampling/
│   ├── README.md
│   ├── 01-bernoulli-and-binomial.md
│   ├── 02-normal-distribution.md
│   ├── 03-categorical-distribution-and-softmax.md
│   ├── 04-law-of-large-numbers.md
│   ├── 05-central-limit-theorem.md
│   ├── 06-sampling-methods.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-sampling-from-a-next-token-distribution.md
├── 09-Statistics-for-Experiments-and-Evals/
│   ├── README.md
│   ├── 01-descriptive-statistics.md
│   ├── 02-confidence-intervals.md
│   ├── 03-bootstrap-resampling.md
│   ├── 04-hypothesis-testing-and-p-values.md
│   ├── 05-paired-tests-for-model-comparison.md
│   ├── 06-sample-size-and-statistical-power.md
│   ├── 07-multiple-comparisons.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-is-prompt-b-really-better.md
└── 10-Information-Theory-for-ML/
    ├── README.md
    ├── 01-information-and-surprise.md
    ├── 02-entropy.md
    ├── 03-cross-entropy-loss.md
    ├── 04-kl-divergence.md
    ├── 05-perplexity.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-compute-perplexity-of-text.md
```

### Stage 5 — Machine Learning Foundations — `Machine Learning Foundations/`

```text
Machine Learning Foundations/
├── README.md
├── 00-Stage-5-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-end-to-end-classifier-with-error-analysis.md
├── 01-What-Machine-Learning-Is/
│   ├── README.md
│   ├── 01-rules-vs-learning.md
│   ├── 02-supervised-unsupervised-and-self-supervised.md
│   ├── 03-training-validation-and-test-sets.md
│   ├── 04-the-ml-project-lifecycle.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-first-model-with-scikit-learn.md
├── 02-Data-Preparation-and-Feature-Engineering/
│   ├── README.md
│   ├── 01-exploratory-data-analysis.md
│   ├── 02-missing-values-and-outliers.md
│   ├── 03-encoding-categorical-features.md
│   ├── 04-scaling-and-normalization.md
│   ├── 05-data-leakage.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-leakage-hunt.md
├── 03-Linear-and-Logistic-Regression/
│   ├── README.md
│   ├── 01-linear-regression.md
│   ├── 02-loss-functions.md
│   ├── 03-logistic-regression.md
│   ├── 04-softmax-regression.md
│   ├── 05-implementing-from-scratch-in-numpy.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-regression-from-scratch.md
├── 04-Model-Evaluation-and-Metrics/
│   ├── README.md
│   ├── 01-accuracy-and-its-traps.md
│   ├── 02-precision-recall-and-f1.md
│   ├── 03-roc-and-pr-curves.md
│   ├── 04-regression-metrics.md
│   ├── 05-calibration.md
│   ├── 06-choosing-metrics-for-business-goals.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-metric-selection-report.md
├── 05-Overfitting-Regularization-and-Validation/
│   ├── README.md
│   ├── 01-bias-variance-trade-off.md
│   ├── 02-regularization.md
│   ├── 03-cross-validation.md
│   ├── 04-hyperparameter-tuning.md
│   ├── 05-learning-curves.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-diagnose-an-overfit-model.md
├── 06-Trees-Ensembles-and-Gradient-Boosting/
│   ├── README.md
│   ├── 01-decision-trees.md
│   ├── 02-random-forests.md
│   ├── 03-gradient-boosting.md
│   ├── 04-xgboost-and-lightgbm.md
│   ├── 05-feature-importance.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-tabular-benchmark.md
├── 07-Unsupervised-Learning/
│   ├── README.md
│   ├── 01-k-means-clustering.md
│   ├── 02-hierarchical-and-density-clustering.md
│   ├── 03-pca.md
│   ├── 04-t-sne-and-umap.md
│   ├── 05-anomaly-detection.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-cluster-support-tickets.md
├── 08-Classic-NLP-and-Text-Classification/
│   ├── README.md
│   ├── 01-text-preprocessing.md
│   ├── 02-bag-of-words-and-tf-idf.md
│   ├── 03-naive-bayes-and-linear-text-models.md
│   ├── 04-limits-of-classic-nlp.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-ticket-classifier-baseline.md
├── 09-Experiment-Tracking-and-Reproducibility/
│   ├── README.md
│   ├── 01-why-experiments-go-wrong.md
│   ├── 02-seeds-and-determinism.md
│   ├── 03-mlflow-experiment-tracking.md
│   ├── 04-data-and-model-versioning.md
│   ├── 05-writing-experiment-reports.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-tracked-experiment-suite.md
└── 10-Error-Analysis-and-Model-Debugging/
    ├── README.md
    ├── 01-slicing-performance.md
    ├── 02-confusion-driven-analysis.md
    ├── 03-label-noise.md
    ├── 04-building-a-failure-taxonomy.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-error-analysis-report.md
```

### Stage 6 — Deep Learning & Transformers — `Deep Learning & Transformers/`

```text
Deep Learning & Transformers/
├── README.md
├── 00-Stage-6-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-train-a-small-gpt-and-write-the-report.md
├── 01-Neural-Networks-and-Backpropagation/
│   ├── README.md
│   ├── 01-the-neuron.md
│   ├── 02-layers-and-activations.md
│   ├── 03-forward-pass.md
│   ├── 04-backpropagation.md
│   ├── 05-build-micrograd.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-autograd-engine-from-scratch.md
├── 02-PyTorch-Fundamentals/
│   ├── README.md
│   ├── 01-tensors.md
│   ├── 02-autograd.md
│   ├── 03-nn-module.md
│   ├── 04-datasets-and-dataloaders.md
│   ├── 05-gpu-and-device-management.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-mnist-mlp-in-pytorch.md
├── 03-Training-Deep-Networks/
│   ├── README.md
│   ├── 01-the-training-loop.md
│   ├── 02-optimizers.md
│   ├── 03-initialization-and-normalization.md
│   ├── 04-dropout-and-regularization.md
│   ├── 05-learning-rate-schedules.md
│   ├── 06-debugging-training-runs.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-training-diagnostics-dashboard.md
├── 04-CNNs-and-RNNs-Essentials/
│   ├── README.md
│   ├── 01-convolutions.md
│   ├── 02-cnn-architectures.md
│   ├── 03-recurrent-networks.md
│   ├── 04-why-rnns-struggle.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-transfer-learning-image-classifier.md
├── 05-Embeddings-and-Representation-Learning/
│   ├── README.md
│   ├── 01-one-hot-vs-dense-embeddings.md
│   ├── 02-word2vec-intuition.md
│   ├── 03-contrastive-learning.md
│   ├── 04-sentence-embeddings.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-train-small-word-embeddings.md
├── 06-Attention-and-the-Transformer/
│   ├── README.md
│   ├── 01-the-attention-idea.md
│   ├── 02-queries-keys-and-values.md
│   ├── 03-scaled-dot-product-attention.md
│   ├── 04-multi-head-attention.md
│   ├── 05-positional-encoding.md
│   ├── 06-the-transformer-block.md
│   ├── 07-encoder-decoder-and-decoder-only.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-attention-from-scratch.md
├── 07-Tokenization/
│   ├── README.md
│   ├── 01-why-tokenization-matters.md
│   ├── 02-characters-words-and-subwords.md
│   ├── 03-byte-pair-encoding.md
│   ├── 04-tokenizer-quirks-and-costs.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-build-a-bpe-tokenizer.md
├── 08-Build-a-GPT-From-Scratch/
│   ├── README.md
│   ├── 01-bigram-language-model.md
│   ├── 02-self-attention-head.md
│   ├── 03-full-gpt-model.md
│   ├── 04-training-on-a-text-corpus.md
│   ├── 05-sampling-from-your-model.md
│   ├── 06-scaling-it-up.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-nano-gpt-on-custom-corpus.md
├── 09-Pretraining-Scaling-Laws-and-Compute/
│   ├── README.md
│   ├── 01-pretraining-objectives.md
│   ├── 02-pretraining-data.md
│   ├── 03-scaling-laws.md
│   ├── 04-compute-flops-and-memory.md
│   ├── 05-distributed-training-overview.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-scaling-mini-experiment.md
├── 10-Post-Training-SFT-RLHF-DPO-and-Constitutional-AI/
│   ├── README.md
│   ├── 01-from-base-model-to-assistant.md
│   ├── 02-supervised-fine-tuning.md
│   ├── 03-reward-models-and-rlhf.md
│   ├── 04-dpo.md
│   ├── 05-constitutional-ai-and-rlaif.md
│   ├── 06-reinforcement-learning-for-reasoning.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-compare-base-vs-instruct-models.md
├── 11-Decoding-and-Sampling/
│   ├── README.md
│   ├── 01-greedy-and-beam-search.md
│   ├── 02-temperature.md
│   ├── 03-top-k-and-top-p.md
│   ├── 04-kv-cache-intuition.md
│   ├── 05-speculative-decoding-intuition.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-sampling-parameters-experiment.md
├── 12-Reasoning-Models-and-Test-Time-Compute/
│   ├── README.md
│   ├── 01-chain-of-thought.md
│   ├── 02-test-time-compute.md
│   ├── 03-how-reasoning-models-are-trained.md
│   ├── 04-when-reasoning-helps-and-hurts.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-reasoning-budget-vs-accuracy.md
├── 13-Multimodal-Models/
│   ├── README.md
│   ├── 01-vision-transformers.md
│   ├── 02-clip-and-contrastive-image-text.md
│   ├── 03-vision-language-models.md
│   ├── 04-audio-and-speech-models.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-zero-shot-image-classification-with-clip.md
└── 14-Reading-and-Reproducing-ML-Papers/
    ├── README.md
    ├── 01-how-to-read-a-paper.md
    ├── 02-the-essential-paper-list.md
    ├── 03-reproducing-results.md
    ├── 04-writing-paper-summaries.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-reproduce-a-small-paper-result.md
```

### Stage 7 — Backend Engineering for AI Systems — `Backend Engineering for AI Systems/`

```text
Backend Engineering for AI Systems/
├── README.md
├── 00-Stage-7-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-production-ready-ai-api-service.md
├── 01-HTTP-REST-and-API-Design/
│   ├── README.md
│   ├── 01-how-the-web-works.md
│   ├── 02-http-methods-status-codes-and-headers.md
│   ├── 03-rest-api-design.md
│   ├── 04-json-and-api-contracts.md
│   ├── 05-api-versioning.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-design-an-api-spec.md
├── 02-FastAPI-and-Pydantic/
│   ├── README.md
│   ├── 01-first-fastapi-service.md
│   ├── 02-request-validation-with-pydantic.md
│   ├── 03-dependency-injection.md
│   ├── 04-error-handling.md
│   ├── 05-openapi-docs.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-crud-service.md
├── 03-Async-Python-and-Concurrent-API-Calls/
│   ├── README.md
│   ├── 01-sync-vs-async.md
│   ├── 02-asyncio-event-loop.md
│   ├── 03-async-http-clients.md
│   ├── 04-concurrency-limits-and-semaphores.md
│   ├── 05-async-pitfalls.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-parallel-llm-call-runner.md
├── 04-Databases-for-AI-Applications/
│   ├── README.md
│   ├── 01-postgresql-for-applications.md
│   ├── 02-orm-and-migrations.md
│   ├── 03-redis-fundamentals.md
│   ├── 04-storing-conversations-and-traces.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-conversation-store.md
├── 05-Caching-Queues-and-Background-Jobs/
│   ├── README.md
│   ├── 01-caching-strategies.md
│   ├── 02-message-queues.md
│   ├── 03-background-workers.md
│   ├── 04-idempotency.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-job-queue-for-batch-inference.md
├── 06-Streaming-Responses/
│   ├── README.md
│   ├── 01-server-sent-events.md
│   ├── 02-websockets.md
│   ├── 03-streaming-llm-tokens-to-clients.md
│   ├── 04-backpressure-and-cancellation.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-streaming-chat-endpoint.md
├── 07-Auth-Rate-Limiting-and-API-Security/
│   ├── README.md
│   ├── 01-authentication-and-api-keys.md
│   ├── 02-authorization.md
│   ├── 03-rate-limiting-algorithms.md
│   ├── 04-owasp-api-security-basics.md
│   ├── 05-secrets-management.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-secure-the-api.md
├── 08-Resilience-and-Failure-Handling/
│   ├── README.md
│   ├── 01-timeouts.md
│   ├── 02-retries-with-backoff-and-jitter.md
│   ├── 03-circuit-breakers.md
│   ├── 04-graceful-degradation.md
│   ├── 05-handling-provider-outages.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-chaos-test-an-llm-service.md
├── 09-Testing-AI-Backends/
│   ├── README.md
│   ├── 01-unit-and-integration-tests.md
│   ├── 02-mocking-llm-calls.md
│   ├── 03-contract-tests.md
│   ├── 04-load-testing.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-test-suite-and-load-test.md
├── 10-Deployment-and-CI-CD/
│   ├── README.md
│   ├── 01-containerizing-ai-services.md
│   ├── 02-ci-cd-pipelines.md
│   ├── 03-cloud-deployment-options.md
│   ├── 04-configuration-and-environments.md
│   ├── 05-logging-and-metrics-basics.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-deploy-to-the-cloud.md
└── 11-Minimal-Frontends-for-AI-Demos/
    ├── README.md
    ├── 01-streamlit-and-gradio.md
    ├── 02-basic-react-and-nextjs.md
    ├── 03-chat-ui-patterns.md
    ├── 04-demo-polish.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-demo-ui.md
```

### Stage 8 — LLM Application Engineering — `LLM Application Engineering/`

```text
LLM Application Engineering/
├── README.md
├── 00-Stage-8-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-structured-document-extraction-service.md
├── 01-How-LLM-APIs-Work/
│   ├── README.md
│   ├── 01-messages-and-roles.md
│   ├── 02-tokens-and-context-windows.md
│   ├── 03-sampling-parameters-in-apis.md
│   ├── 04-pricing-and-usage.md
│   ├── 05-sdks-for-major-providers.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-first-llm-api-calls.md
├── 02-Model-Selection-Cost-and-Latency/
│   ├── README.md
│   ├── 01-model-families-and-tiers.md
│   ├── 02-capability-vs-cost-vs-latency.md
│   ├── 03-benchmarking-models-on-your-task.md
│   ├── 04-open-weight-vs-api-models.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-model-selection-matrix.md
├── 03-Prompt-Engineering-Fundamentals/
│   ├── README.md
│   ├── 01-clear-and-direct-instructions.md
│   ├── 02-system-prompts-and-roles.md
│   ├── 03-few-shot-examples.md
│   ├── 04-xml-tags-and-structure.md
│   ├── 05-letting-the-model-think.md
│   ├── 06-prompt-iteration-workflow.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-prompt-iteration-log.md
├── 04-Context-Engineering/
│   ├── README.md
│   ├── 01-what-goes-in-the-context-window.md
│   ├── 02-long-context-strategies.md
│   ├── 03-lost-in-the-middle.md
│   ├── 04-context-compression-and-summarization.md
│   ├── 05-prompt-templates.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-long-document-qa.md
├── 05-Structured-Outputs-and-Validation/
│   ├── README.md
│   ├── 01-json-outputs.md
│   ├── 02-schemas-and-pydantic-validation.md
│   ├── 03-retry-and-repair-strategies.md
│   ├── 04-extraction-patterns.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-invoice-extractor.md
├── 06-Tool-Use-and-Function-Calling/
│   ├── README.md
│   ├── 01-how-tool-calling-works.md
│   ├── 02-defining-tool-schemas.md
│   ├── 03-handling-tool-results.md
│   ├── 04-parallel-tool-calls.md
│   ├── 05-tool-errors.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-multi-tool-assistant.md
├── 07-Streaming-and-Conversation-Management/
│   ├── README.md
│   ├── 01-streaming-responses.md
│   ├── 02-multi-turn-conversations.md
│   ├── 03-conversation-memory.md
│   ├── 04-ux-for-latency.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-streaming-assistant.md
├── 08-Prompt-Caching-Batching-and-Cost-Control/
│   ├── README.md
│   ├── 01-prompt-caching.md
│   ├── 02-batch-apis.md
│   ├── 03-token-budgeting.md
│   ├── 04-cost-estimation-and-tracking.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-cost-reduction-experiment.md
├── 09-Extended-Thinking-and-Reasoning-Controls/
│   ├── README.md
│   ├── 01-reasoning-modes-in-apis.md
│   ├── 02-thinking-budgets.md
│   ├── 03-when-to-use-reasoning.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-reasoning-vs-standard-comparison.md
├── 10-Vision-PDFs-and-Multimodal-Inputs/
│   ├── README.md
│   ├── 01-image-inputs.md
│   ├── 02-pdf-and-document-inputs.md
│   ├── 03-charts-and-tables.md
│   ├── 04-multimodal-limits.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-receipt-and-chart-reader.md
├── 11-Model-Context-Protocol/
│   ├── README.md
│   ├── 01-what-mcp-is.md
│   ├── 02-hosts-clients-and-servers.md
│   ├── 03-tools-resources-and-prompts.md
│   ├── 04-using-mcp-servers.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-connect-an-app-to-mcp-servers.md
├── 12-Prompt-Management-and-Versioning/
│   ├── README.md
│   ├── 01-prompts-as-code.md
│   ├── 02-prompt-versioning.md
│   ├── 03-configuration-driven-prompts.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-prompt-registry.md
└── 13-LLM-Failure-Modes-and-Mitigations/
    ├── README.md
    ├── 01-hallucination.md
    ├── 02-instruction-drift.md
    ├── 03-sycophancy.md
    ├── 04-inconsistency-and-non-determinism.md
    ├── 05-mitigation-playbook.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-failure-mode-catalog.md
```

### Stage 9 — Retrieval & RAG Systems — `Retrieval & RAG Systems/`

```text
Retrieval & RAG Systems/
├── README.md
├── 00-Stage-9-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-rag-v1-foundation-for-flagship-1.md
├── 01-Why-RAG-and-When-Not-To/
│   ├── README.md
│   ├── 01-the-knowledge-problem.md
│   ├── 02-rag-vs-long-context-vs-fine-tuning.md
│   ├── 03-rag-architecture-overview.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-naive-rag-baseline.md
├── 02-Document-Parsing-and-Ingestion/
│   ├── README.md
│   ├── 01-parsing-pdfs-html-and-office-files.md
│   ├── 02-tables-and-images-in-documents.md
│   ├── 03-metadata-extraction.md
│   ├── 04-ingestion-pipelines.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-ingestion-pipeline.md
├── 03-Chunking-Strategies/
│   ├── README.md
│   ├── 01-fixed-size-chunking.md
│   ├── 02-structure-aware-chunking.md
│   ├── 03-semantic-chunking.md
│   ├── 04-chunk-size-and-overlap-experiments.md
│   ├── 05-contextual-chunk-enrichment.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-chunking-experiment.md
├── 04-Embedding-Models/
│   ├── README.md
│   ├── 01-how-embedding-models-work.md
│   ├── 02-choosing-embedding-models.md
│   ├── 03-embedding-benchmarks.md
│   ├── 04-domain-adaptation-of-embeddings.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-embedding-model-comparison.md
├── 05-Vector-Search-and-ANN-Indexes/
│   ├── README.md
│   ├── 01-exact-vs-approximate-search.md
│   ├── 02-hnsw.md
│   ├── 03-ivf-and-product-quantization.md
│   ├── 04-vector-databases-and-pgvector.md
│   ├── 05-filtering-and-metadata.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-ann-recall-vs-latency.md
├── 06-Lexical-and-Hybrid-Retrieval/
│   ├── README.md
│   ├── 01-bm25.md
│   ├── 02-when-keyword-search-wins.md
│   ├── 03-hybrid-retrieval-and-score-fusion.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-hybrid-vs-dense.md
├── 07-Reranking/
│   ├── README.md
│   ├── 01-bi-encoders-vs-cross-encoders.md
│   ├── 02-reranking-models.md
│   ├── 03-llm-based-reranking.md
│   ├── 04-reranking-cost-trade-offs.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-reranker-impact-study.md
├── 08-Query-Understanding-and-Rewriting/
│   ├── README.md
│   ├── 01-query-rewriting.md
│   ├── 02-query-decomposition.md
│   ├── 03-hyde.md
│   ├── 04-routing-queries.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-query-rewrite-experiment.md
├── 09-Context-Construction-and-Citations/
│   ├── README.md
│   ├── 01-context-assembly.md
│   ├── 02-citation-generation.md
│   ├── 03-citation-verification.md
│   ├── 04-handling-conflicting-sources.md
│   ├── 05-saying-i-dont-know.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-verified-citations.md
├── 10-Retrieval-Evaluation/
│   ├── README.md
│   ├── 01-building-a-retrieval-test-set.md
│   ├── 02-recall-and-precision-at-k.md
│   ├── 03-mrr-and-ndcg.md
│   ├── 04-synthetic-query-generation.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-retrieval-eval-harness.md
├── 11-Generation-Evaluation-for-RAG/
│   ├── README.md
│   ├── 01-faithfulness-and-groundedness.md
│   ├── 02-answer-relevance-and-correctness.md
│   ├── 03-end-to-end-rag-evaluation.md
│   ├── 04-component-vs-system-metrics.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-rag-eval-report.md
├── 12-Production-RAG-Freshness-Scale-and-Access-Control/
│   ├── README.md
│   ├── 01-incremental-indexing.md
│   ├── 02-document-updates-and-deletes.md
│   ├── 03-permission-aware-retrieval.md
│   ├── 04-scaling-to-millions-of-documents.md
│   ├── 05-rag-latency-and-cost.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-incremental-reindexing.md
└── 13-Advanced-RAG-Patterns/
    ├── README.md
    ├── 01-agentic-rag.md
    ├── 02-multi-hop-retrieval.md
    ├── 03-graph-rag.md
    ├── 04-multimodal-rag.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-agentic-rag-prototype.md
```

### Stage 10 — Evaluation & Experimentation — `Evaluation & Experimentation/`

```text
Evaluation & Experimentation/
├── README.md
├── 00-Stage-10-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-evalforge-v1-foundation-for-flagship-2.md
├── 01-Why-Evals-Are-the-Core-Skill/
│   ├── README.md
│   ├── 01-evals-as-the-product-spec.md
│   ├── 02-vibe-checks-vs-measurement.md
│   ├── 03-eval-driven-development.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-write-your-first-eval.md
├── 02-Defining-Success-Criteria/
│   ├── README.md
│   ├── 01-specific-measurable-success-criteria.md
│   ├── 02-quality-dimensions.md
│   ├── 03-guardrail-metrics-latency-cost-safety.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-success-criteria-doc.md
├── 03-Building-Eval-Datasets/
│   ├── README.md
│   ├── 01-golden-datasets.md
│   ├── 02-sampling-from-production-data.md
│   ├── 03-synthetic-data-generation.md
│   ├── 04-edge-cases-and-adversarial-examples.md
│   ├── 05-dataset-versioning.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-build-a-300-example-eval-set.md
├── 04-Code-Based-Graders/
│   ├── README.md
│   ├── 01-exact-match-and-regex.md
│   ├── 02-schema-and-format-checks.md
│   ├── 03-execution-based-grading.md
│   ├── 04-string-similarity-metrics.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-grader-library.md
├── 05-LLM-as-Judge/
│   ├── README.md
│   ├── 01-judge-prompt-design.md
│   ├── 02-rubrics-and-scoring-scales.md
│   ├── 03-pairwise-comparison.md
│   ├── 04-judge-biases.md
│   ├── 05-calibrating-judges-against-humans.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-judge-agreement-study.md
├── 06-Human-Evaluation-and-Labeling/
│   ├── README.md
│   ├── 01-labeling-guidelines.md
│   ├── 02-inter-annotator-agreement.md
│   ├── 03-labeling-tools-and-workflows.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-label-and-measure-agreement.md
├── 07-Statistical-Rigor-in-Evals/
│   ├── README.md
│   ├── 01-variance-and-non-determinism.md
│   ├── 02-confidence-intervals-for-evals.md
│   ├── 03-significance-testing-for-model-comparison.md
│   ├── 04-how-many-examples-you-need.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-significance-report.md
├── 08-Regression-Testing-and-CI-for-AI/
│   ├── README.md
│   ├── 01-eval-suites-as-tests.md
│   ├── 02-ci-gates-for-prompt-and-model-changes.md
│   ├── 03-tracking-results-over-time.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-github-actions-eval-gate.md
├── 09-Online-Evaluation-and-User-Feedback/
│   ├── README.md
│   ├── 01-implicit-and-explicit-feedback.md
│   ├── 02-ab-testing-ai-features.md
│   ├── 03-shadow-and-canary-evaluation.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-ab-test-simulation.md
├── 10-Benchmarks-and-Their-Limits/
│   ├── README.md
│   ├── 01-public-benchmarks-overview.md
│   ├── 02-contamination.md
│   ├── 03-benchmark-vs-task-specific-evals.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-benchmark-critique.md
└── 11-Error-Analysis-and-Failure-Taxonomies/
    ├── README.md
    ├── 01-reading-model-outputs.md
    ├── 02-open-and-axial-coding.md
    ├── 03-prioritizing-failures.md
    ├── 04-closing-the-loop.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-failure-taxonomy.md
```

### Stage 11 — AI Agents & Tool Use — `AI Agents & Tool Use/`

```text
AI Agents & Tool Use/
├── README.md
├── 00-Stage-11-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-analyst-agent-v1-foundation-for-flagship-3.md
├── 01-Workflows-vs-Agents/
│   ├── README.md
│   ├── 01-what-an-agent-is.md
│   ├── 02-workflows-vs-autonomous-agents.md
│   ├── 03-when-not-to-build-an-agent.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-workflow-vs-agent-comparison.md
├── 02-The-Agent-Loop/
│   ├── README.md
│   ├── 01-observe-think-act.md
│   ├── 02-building-an-agent-loop-from-scratch.md
│   ├── 03-stop-conditions.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-agent-in-100-lines.md
├── 03-Designing-Tools-for-Agents/
│   ├── README.md
│   ├── 01-tool-interface-design.md
│   ├── 02-tool-descriptions-and-examples.md
│   ├── 03-error-messages-for-models.md
│   ├── 04-tool-output-formatting.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-tool-design-ab-test.md
├── 04-Workflow-Patterns/
│   ├── README.md
│   ├── 01-prompt-chaining.md
│   ├── 02-routing.md
│   ├── 03-parallelization.md
│   ├── 04-orchestrator-workers.md
│   ├── 05-evaluator-optimizer.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-pattern-implementations.md
├── 05-Planning-Reflection-and-Self-Correction/
│   ├── README.md
│   ├── 01-planning.md
│   ├── 02-react-pattern.md
│   ├── 03-reflection-and-critique.md
│   ├── 04-verification-steps.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-self-correcting-agent.md
├── 06-State-Memory-and-Context-Management/
│   ├── README.md
│   ├── 01-short-term-state.md
│   ├── 02-long-term-memory.md
│   ├── 03-context-management-for-agents.md
│   ├── 04-compaction-and-summarization.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-long-running-agent-memory.md
├── 07-Sandboxed-Code-Execution/
│   ├── README.md
│   ├── 01-why-sandboxing.md
│   ├── 02-containers-and-isolation.md
│   ├── 03-resource-limits.md
│   ├── 04-safe-file-and-network-access.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-python-execution-sandbox.md
├── 08-Building-MCP-Servers/
│   ├── README.md
│   ├── 01-mcp-server-anatomy.md
│   ├── 02-exposing-tools-and-resources.md
│   ├── 03-authentication-and-security.md
│   ├── 04-testing-mcp-servers.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-database-mcp-server.md
├── 09-Multi-Agent-Systems/
│   ├── README.md
│   ├── 01-when-multiple-agents-help.md
│   ├── 02-orchestrator-and-subagents.md
│   ├── 03-communication-and-handoffs.md
│   ├── 04-cost-and-failure-amplification.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-research-multi-agent-system.md
├── 10-Reliability-Budgets-and-Termination/
│   ├── README.md
│   ├── 01-infinite-loops-and-runaway-costs.md
│   ├── 02-step-and-token-budgets.md
│   ├── 03-retries-and-recovery.md
│   ├── 04-human-in-the-loop.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-agent-reliability-harness.md
├── 11-Evaluating-Agents/
│   ├── README.md
│   ├── 01-outcome-vs-trajectory-evaluation.md
│   ├── 02-task-success-metrics.md
│   ├── 03-tool-call-accuracy.md
│   ├── 04-agent-benchmarks.md
│   ├── 05-simulated-environments.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-agent-eval-suite.md
├── 12-Coding-Agents-and-Computer-Use/
│   ├── README.md
│   ├── 01-how-coding-agents-work.md
│   ├── 02-repository-understanding.md
│   ├── 03-edit-test-loops.md
│   ├── 04-computer-use-agents.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-mini-coding-agent.md
└── 13-Agent-Frameworks-and-SDKs/
    ├── README.md
    ├── 01-framework-landscape.md
    ├── 02-agent-sdks-from-model-providers.md
    ├── 03-framework-vs-from-scratch-trade-offs.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-rebuild-your-agent-with-an-sdk.md
```

### Stage 12 — AI Safety, Security & Responsible AI — `AI Safety, Security & Responsible AI/`

```text
AI Safety, Security & Responsible AI/
├── README.md
├── 00-Stage-12-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-red-team-report-foundation-for-flagship-4.md
├── 01-Why-Safety-Matters-at-Frontier-Labs/
│   ├── README.md
│   ├── 01-the-mission-of-frontier-labs.md
│   ├── 02-types-of-ai-risk.md
│   ├── 03-safety-as-an-engineering-discipline.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-summarize-lab-safety-policies.md
├── 02-Alignment-Fundamentals/
│   ├── README.md
│   ├── 01-what-alignment-means.md
│   ├── 02-rlhf-recap.md
│   ├── 03-constitutional-ai.md
│   ├── 04-interpretability-overview.md
│   ├── 05-model-specs-and-behavior-policies.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-alignment-paper-summaries.md
├── 03-Frontier-Safety-Frameworks/
│   ├── README.md
│   ├── 01-responsible-scaling-policies.md
│   ├── 02-dangerous-capability-evaluations.md
│   ├── 03-system-cards.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-compare-safety-frameworks.md
├── 04-Prompt-Injection/
│   ├── README.md
│   ├── 01-direct-prompt-injection.md
│   ├── 02-indirect-prompt-injection.md
│   ├── 03-data-exfiltration-attacks.md
│   ├── 04-defenses-and-their-limits.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-injection-attack-suite.md
├── 05-Jailbreaks-and-Misuse/
│   ├── README.md
│   ├── 01-jailbreak-techniques-overview.md
│   ├── 02-misuse-categories.md
│   ├── 03-abuse-monitoring.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-misuse-risk-assessment.md
├── 06-Red-Teaming/
│   ├── README.md
│   ├── 01-red-teaming-methodology.md
│   ├── 02-automated-red-teaming.md
│   ├── 03-attack-success-rate-metrics.md
│   ├── 04-reporting-findings.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-red-team-your-rag-system.md
├── 07-Guardrails/
│   ├── README.md
│   ├── 01-input-classification.md
│   ├── 02-output-filtering.md
│   ├── 03-policy-enforcement-layers.md
│   ├── 04-guardrail-latency-and-cost.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-guardrail-layer.md
├── 08-Agent-Security/
│   ├── README.md
│   ├── 01-least-privilege-for-tools.md
│   ├── 02-confirmation-for-risky-actions.md
│   ├── 03-sandbox-escapes-and-supply-chain.md
│   ├── 04-audit-logging.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-agent-permission-system.md
├── 09-Privacy-and-Data-Governance/
│   ├── README.md
│   ├── 01-pii-detection-and-redaction.md
│   ├── 02-data-retention.md
│   ├── 03-regulations-overview.md
│   ├── 04-training-data-and-consent.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-pii-redaction-pipeline.md
├── 10-Fairness-Bias-and-Harm-Evaluation/
│   ├── README.md
│   ├── 01-sources-of-bias.md
│   ├── 02-measuring-bias-in-llm-outputs.md
│   ├── 03-mitigation-strategies.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-bias-probe-eval.md
├── 11-Helpfulness-vs-Harmlessness/
│   ├── README.md
│   ├── 01-over-refusal.md
│   ├── 02-measuring-false-refusal-rate.md
│   ├── 03-balancing-safety-and-usefulness.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-refusal-calibration-study.md
└── 12-Documentation-and-Transparency/
    ├── README.md
    ├── 01-model-cards.md
    ├── 02-system-documentation-for-ai-features.md
    ├── 03-communicating-limitations.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-write-a-system-card.md
```

### Stage 13 — Model Customization & Inference — `Model Customization & Inference/`

```text
Model Customization & Inference/
├── README.md
├── 00-Stage-13-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-specialized-small-model-foundation-for-flagship-7.md
├── 01-Prompting-vs-RAG-vs-Fine-Tuning/
│   ├── README.md
│   ├── 01-decision-framework.md
│   ├── 02-what-fine-tuning-can-and-cannot-do.md
│   ├── 03-cost-and-maintenance-trade-offs.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-decision-memo.md
├── 02-Open-Weight-Models-and-Hugging-Face/
│   ├── README.md
│   ├── 01-hugging-face-hub-and-transformers.md
│   ├── 02-model-licenses.md
│   ├── 03-running-models-locally.md
│   ├── 04-chat-templates.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-run-an-open-model-locally.md
├── 03-Supervised-Fine-Tuning/
│   ├── README.md
│   ├── 01-preparing-sft-data.md
│   ├── 02-training-configuration.md
│   ├── 03-running-sft.md
│   ├── 04-overfitting-and-catastrophic-forgetting.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-sft-a-small-model.md
├── 04-Parameter-Efficient-Fine-Tuning/
│   ├── README.md
│   ├── 01-lora.md
│   ├── 02-qlora.md
│   ├── 03-adapter-merging-and-serving.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-lora-vs-full-fine-tune.md
├── 05-Preference-Tuning/
│   ├── README.md
│   ├── 01-preference-data.md
│   ├── 02-dpo-in-practice.md
│   ├── 03-evaluating-preference-tuned-models.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-dpo-experiment.md
├── 06-Distillation-and-Synthetic-Data/
│   ├── README.md
│   ├── 01-distillation-from-larger-models.md
│   ├── 02-synthetic-data-quality-control.md
│   ├── 03-terms-of-service-and-licensing.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-distill-a-classifier.md
├── 07-Evaluating-Customized-Models/
│   ├── README.md
│   ├── 01-before-and-after-evaluation.md
│   ├── 02-regression-on-general-capabilities.md
│   ├── 03-cost-quality-latency-frontier.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-fine-tune-evaluation-report.md
├── 08-Inference-Fundamentals/
│   ├── README.md
│   ├── 01-prefill-and-decode.md
│   ├── 02-ttft-tpot-and-throughput.md
│   ├── 03-memory-bandwidth-bottlenecks.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-measure-inference-metrics.md
├── 09-KV-Cache-and-Batching/
│   ├── README.md
│   ├── 01-kv-cache.md
│   ├── 02-static-and-continuous-batching.md
│   ├── 03-pagedattention.md
│   ├── 04-prefix-caching.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-batching-experiment.md
├── 10-Quantization/
│   ├── README.md
│   ├── 01-number-formats.md
│   ├── 02-post-training-quantization.md
│   ├── 03-quality-impact-of-quantization.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-quantization-trade-off-study.md
├── 11-Serving-Open-Models-with-vLLM/
│   ├── README.md
│   ├── 01-vllm-architecture.md
│   ├── 02-deploying-vllm.md
│   ├── 03-load-testing-inference-servers.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-throughput-latency-characterization.md
└── 12-GPUs-and-Cost-Modeling/
    ├── README.md
    ├── 01-gpu-architecture-for-inference.md
    ├── 02-gpu-memory-math.md
    ├── 03-cloud-gpu-cost-modeling.md
    ├── 04-build-vs-buy-inference.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-inference-cost-model.md
```

### Stage 14 — LLMOps & AI System Design — `LLMOps & AI System Design/`

```text
LLMOps & AI System Design/
├── README.md
├── 00-Stage-14-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-observability-layer-for-your-portfolio.md
├── 01-LLM-Observability-and-Tracing/
│   ├── README.md
│   ├── 01-logs-metrics-and-traces.md
│   ├── 02-opentelemetry-for-llm-apps.md
│   ├── 03-tracing-agents-and-tool-calls.md
│   ├── 04-observability-tools-landscape.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-instrument-your-rag-system.md
├── 02-Production-Metrics/
│   ├── README.md
│   ├── 01-quality-metrics-in-production.md
│   ├── 02-reliability-metrics-and-slos.md
│   ├── 03-cost-per-request-and-per-user.md
│   ├── 04-dashboards-that-matter.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-ai-system-dashboard.md
├── 03-Routing-Fallbacks-and-Multi-Provider/
│   ├── README.md
│   ├── 01-model-routing.md
│   ├── 02-fallback-chains.md
│   ├── 03-provider-abstraction.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-router-with-fallbacks.md
├── 04-Caching-and-Cost-Optimization/
│   ├── README.md
│   ├── 01-exact-and-semantic-caching.md
│   ├── 02-cost-optimization-playbook.md
│   ├── 03-quality-cost-trade-offs.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-cost-optimization-case-study.md
├── 05-Rate-Limits-and-Capacity-Planning/
│   ├── README.md
│   ├── 01-provider-rate-limits.md
│   ├── 02-queueing-and-load-shedding.md
│   ├── 03-capacity-planning.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-load-test-and-capacity-plan.md
├── 06-Release-Management-for-AI/
│   ├── README.md
│   ├── 01-versioning-prompts-models-and-indexes.md
│   ├── 02-staged-rollouts-and-feature-flags.md
│   ├── 03-rollback-strategies.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-canary-release.md
├── 07-Monitoring-Drift-and-Regressions/
│   ├── README.md
│   ├── 01-input-drift.md
│   ├── 02-quality-drift.md
│   ├── 03-model-version-changes.md
│   ├── 04-alerting.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-drift-monitor.md
├── 08-Incident-Response-for-AI-Systems/
│   ├── README.md
│   ├── 01-ai-incident-types.md
│   ├── 02-runbooks.md
│   ├── 03-postmortems.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-write-a-postmortem.md
├── 09-Data-Flywheels-and-Continuous-Improvement/
│   ├── README.md
│   ├── 01-capturing-feedback.md
│   ├── 02-turning-failures-into-eval-cases.md
│   ├── 03-improvement-loops.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-feedback-to-eval-pipeline.md
├── 10-AI-System-Design-Framework/
│   ├── README.md
│   ├── 01-requirements-and-constraints.md
│   ├── 02-architecture-building-blocks.md
│   ├── 03-back-of-envelope-estimation.md
│   ├── 04-trade-off-discussion.md
│   ├── 05-design-doc-template.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-system-design-doc.md
└── 11-AI-System-Design-Case-Studies/
    ├── README.md
    ├── 01-customer-support-assistant.md
    ├── 02-enterprise-search.md
    ├── 03-coding-assistant.md
    ├── 04-document-processing-pipeline.md
    ├── 05-voice-agent.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-five-mock-designs.md
```

### Stage 15 — Applied AI in the Field — `Applied AI in the Field/`

```text
Applied AI in the Field/
├── README.md
├── 00-Stage-15-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-mock-customer-engagement.md
├── 01-The-Applied-AI-Role-at-Frontier-Labs/
│   ├── README.md
│   ├── 01-role-variants.md
│   ├── 02-a-week-in-the-life.md
│   ├── 03-skills-that-differentiate.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-role-research-notes.md
├── 02-Customer-Discovery-and-Problem-Framing/
│   ├── README.md
│   ├── 01-asking-the-right-questions.md
│   ├── 02-finding-the-real-problem.md
│   ├── 03-feasibility-assessment.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-discovery-interview-script.md
├── 03-Scoping-Prototypes-and-Success-Metrics/
│   ├── README.md
│   ├── 01-scoping-a-proof-of-concept.md
│   ├── 02-defining-success-with-customers.md
│   ├── 03-prototype-to-production-plan.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-poc-scope-document.md
├── 04-Design-Docs-and-Architecture-Decision-Records/
│   ├── README.md
│   ├── 01-design-doc-structure.md
│   ├── 02-writing-adrs.md
│   ├── 03-reviewing-others-docs.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-write-a-design-doc.md
├── 05-Technical-Demos-and-Presentations/
│   ├── README.md
│   ├── 01-demo-storytelling.md
│   ├── 02-live-demo-risk-management.md
│   ├── 03-recording-demo-videos.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-ten-minute-demo.md
├── 06-Explaining-AI-to-Non-Technical-Stakeholders/
│   ├── README.md
│   ├── 01-translating-technical-trade-offs.md
│   ├── 02-setting-expectations-about-ai-limits.md
│   ├── 03-handling-objections.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-executive-summary.md
├── 07-Business-Case-and-ROI/
│   ├── README.md
│   ├── 01-estimating-value.md
│   ├── 02-total-cost-of-ownership.md
│   ├── 03-roi-reporting.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-roi-model.md
├── 08-Technical-Writing-and-Building-in-Public/
│   ├── README.md
│   ├── 01-writing-technical-blog-posts.md
│   ├── 02-sharing-experiments.md
│   ├── 03-open-source-contribution.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-publish-first-post.md
└── 09-Senior-Behaviors-Ownership-Leadership-and-Mentoring/
    ├── README.md
    ├── 01-ownership-and-ambiguity.md
    ├── 02-leading-without-authority.md
    ├── 03-mentoring.md
    ├── 04-cross-team-collaboration.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-leadership-reflection-log.md
```

### Stage 16 — Flagship Portfolio Projects — `Flagship Portfolio Projects/`

Every project folder is meant to become **its own public GitHub repository**. The layout below is what a hiring manager should see when they open it.

```text
Flagship Portfolio Projects/
├── README.md
├── 00-Portfolio-Overview/
│   ├── README.md
│   ├── portfolio-strategy.md
│   ├── how-the-projects-connect.md
│   ├── repo-standards.md
│   ├── readme-template.md
│   ├── adr-template.md
│   ├── experiment-report-template.md
│   ├── resume-bullets-guide.md
│   └── interview-question-bank.md
├── 01-Grounded-RAG-Platform/
│   ├── README.md
│   ├── pyproject.toml
│   ├── Makefile
│   ├── docker-compose.yml
│   ├── .github/
│   │   └── workflows/
│   │       ├── ci.yml
│   │       └── eval-gate.yml
│   ├── docs/
│   │   ├── architecture.md
│   │   ├── evaluation.md
│   │   ├── experiments.md
│   │   ├── failure-analysis.md
│   │   ├── cost-and-latency.md
│   │   ├── lessons-learned.md
│   │   └── decisions/
│   │       ├── ADR-001-document-parsing.md
│   │       ├── ADR-002-chunking-strategy.md
│   │       ├── ADR-003-hybrid-retrieval.md
│   │       ├── ADR-004-reranker-choice.md
│   │       └── ADR-005-citation-verification.md
│   ├── src/
│   │   └── grounded/
│   │       ├── ingestion/
│   │       ├── parsing/
│   │       ├── chunking/
│   │       ├── indexing/
│   │       ├── retrieval/
│   │       ├── reranking/
│   │       ├── generation/
│   │       ├── citations/
│   │       ├── api/
│   │       └── observability/
│   ├── evals/
│   │   ├── datasets/
│   │   │   ├── retrieval-testset.jsonl
│   │   │   ├── answer-testset.jsonl
│   │   │   └── unanswerable-testset.jsonl
│   │   ├── graders/
│   │   └── run_evals.py
│   ├── experiments/
│   │   ├── exp-001-chunk-size-and-overlap.md
│   │   ├── exp-002-dense-vs-bm25-vs-hybrid.md
│   │   ├── exp-003-reranker-impact.md
│   │   ├── exp-004-query-rewriting.md
│   │   └── exp-005-latency-optimization.md
│   ├── benchmarks/
│   │   ├── latency_benchmark.py
│   │   ├── load_test.py
│   │   └── results/
│   ├── configs/
│   │   ├── base.yaml
│   │   └── experiments/
│   ├── scripts/
│   │   ├── download_corpus.py
│   │   └── build_index.py
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   └── demo/
│       ├── app.py
│       └── demo-script.md
├── 02-EvalForge-Evaluation-Platform/
│   ├── README.md
│   ├── pyproject.toml
│   ├── docker-compose.yml
│   ├── .github/
│   │   └── workflows/
│   │       └── ci.yml
│   ├── docs/
│   │   ├── architecture.md
│   │   ├── grader-design.md
│   │   ├── judge-calibration.md
│   │   ├── statistics.md
│   │   ├── lessons-learned.md
│   │   └── decisions/
│   │       ├── ADR-001-experiment-storage.md
│   │       ├── ADR-002-judge-model-choice.md
│   │       └── ADR-003-significance-testing-method.md
│   ├── src/
│   │   └── evalforge/
│   │       ├── datasets/
│   │       ├── runners/
│   │       ├── graders/
│   │       │   ├── code_graders/
│   │       │   └── llm_judges/
│   │       ├── stats/
│   │       ├── storage/
│   │       ├── reports/
│   │       ├── ci/
│   │       └── dashboard/
│   ├── human-labels/
│   │   ├── labeling-guidelines.md
│   │   └── judge-vs-human-agreement.md
│   ├── examples/
│   │   ├── evaluate-grounded-rag/
│   │   └── evaluate-analyst-agent/
│   ├── experiments/
│   │   ├── exp-001-judge-bias-study.md
│   │   ├── exp-002-prompt-v1-vs-v2-significance.md
│   │   └── exp-003-model-a-vs-model-b.md
│   └── tests/
├── 03-Data-Analyst-Agent/
│   ├── README.md
│   ├── pyproject.toml
│   ├── docker-compose.yml
│   ├── docs/
│   │   ├── architecture.md
│   │   ├── tool-design.md
│   │   ├── sandbox-security.md
│   │   ├── agent-evaluation.md
│   │   ├── failure-analysis.md
│   │   ├── lessons-learned.md
│   │   └── decisions/
│   │       ├── ADR-001-workflow-vs-agent.md
│   │       ├── ADR-002-sandbox-technology.md
│   │       ├── ADR-003-memory-strategy.md
│   │       └── ADR-004-mcp-server-design.md
│   ├── src/
│   │   └── analyst_agent/
│   │       ├── agent_loop/
│   │       ├── tools/
│   │       │   ├── sql_tool.py
│   │       │   ├── python_tool.py
│   │       │   ├── schema_tool.py
│   │       │   └── chart_tool.py
│   │       ├── sandbox/
│   │       ├── memory/
│   │       ├── budgets/
│   │       ├── mcp_server/
│   │       ├── api/
│   │       └── observability/
│   ├── evals/
│   │   ├── tasks/
│   │   │   ├── analytics-questions.jsonl
│   │   │   └── ground-truth-answers.jsonl
│   │   ├── trajectory_graders/
│   │   └── run_agent_evals.py
│   ├── experiments/
│   │   ├── exp-001-tool-description-variants.md
│   │   ├── exp-002-planning-vs-no-planning.md
│   │   └── exp-003-model-comparison-cost-vs-success.md
│   ├── data/
│   │   └── README.md
│   ├── tests/
│   └── demo/
├── 04-Red-Team-and-Guardrails-Harness/
│   ├── README.md
│   ├── pyproject.toml
│   ├── docs/
│   │   ├── threat-model.md
│   │   ├── attack-taxonomy.md
│   │   ├── defense-design.md
│   │   ├── results.md
│   │   ├── responsible-disclosure-note.md
│   │   ├── lessons-learned.md
│   │   └── decisions/
│   │       ├── ADR-001-guardrail-placement.md
│   │       └── ADR-002-classifier-vs-llm-guard.md
│   ├── src/
│   │   └── redteam/
│   │       ├── attacks/
│   │       │   ├── direct_injection/
│   │       │   ├── indirect_injection/
│   │       │   ├── data_exfiltration/
│   │       │   └── tool_misuse/
│   │       ├── attack_generators/
│   │       ├── guardrails/
│   │       │   ├── input_filters/
│   │       │   ├── output_filters/
│   │       │   └── tool_permissions/
│   │       └── scoring/
│   ├── evals/
│   │   ├── attack-suite.jsonl
│   │   ├── benign-suite.jsonl
│   │   └── run_redteam.py
│   ├── reports/
│   │   ├── baseline-attack-success-rate.md
│   │   ├── after-defenses.md
│   │   └── system-card.md
│   └── tests/
├── 05-Customer-Deployment-Case-Study/
│   ├── README.md
│   ├── discovery/
│   │   ├── customer-brief.md
│   │   ├── discovery-interview-notes.md
│   │   └── problem-statement.md
│   ├── design/
│   │   ├── design-doc.md
│   │   ├── success-criteria.md
│   │   └── decisions/
│   │       └── ADR-001-build-approach.md
│   ├── prototype/
│   │   ├── src/
│   │   ├── evals/
│   │   └── tests/
│   ├── pilot/
│   │   ├── pilot-plan.md
│   │   ├── pilot-results.md
│   │   └── rollout-plan.md
│   ├── business/
│   │   ├── roi-model.md
│   │   ├── total-cost-of-ownership.md
│   │   └── executive-summary.md
│   └── demo/
│       ├── demo-script.md
│       └── demo-video-link.md
├── 06-Capstone-Autonomous-Coding-Agent/
│   ├── README.md
│   ├── pyproject.toml
│   ├── docker-compose.yml
│   ├── .github/
│   │   └── workflows/
│   │       ├── ci.yml
│   │       └── nightly-benchmark.yml
│   ├── docs/
│   │   ├── architecture.md
│   │   ├── benchmark-design.md
│   │   ├── scaffold-experiments.md
│   │   ├── safety-and-permissions.md
│   │   ├── cost-and-latency.md
│   │   ├── failure-analysis.md
│   │   ├── lessons-learned.md
│   │   └── decisions/
│   │       ├── ADR-001-repository-indexing.md
│   │       ├── ADR-002-edit-format.md
│   │       ├── ADR-003-test-execution-sandbox.md
│   │       ├── ADR-004-context-management.md
│   │       └── ADR-005-stopping-criteria.md
│   ├── src/
│   │   └── coding_agent/
│   │       ├── indexer/
│   │       ├── retrieval/
│   │       ├── tools/
│   │       │   ├── search_code.py
│   │       │   ├── read_file.py
│   │       │   ├── edit_file.py
│   │       │   ├── run_tests.py
│   │       │   └── run_shell.py
│   │       ├── sandbox/
│   │       ├── context/
│   │       ├── planner/
│   │       ├── guardrails/
│   │       ├── observability/
│   │       └── cli/
│   ├── benchmark/
│   │   ├── tasks/
│   │   ├── task-selection-criteria.md
│   │   ├── harness/
│   │   └── results/
│   ├── experiments/
│   │   ├── exp-001-baseline-scaffold.md
│   │   ├── exp-002-repo-map-vs-no-repo-map.md
│   │   ├── exp-003-model-comparison.md
│   │   └── exp-004-budget-vs-success-rate.md
│   ├── tests/
│   └── demo/
└── 07-Optional-Specialized-Model-Study/
    ├── README.md
    ├── pyproject.toml
    ├── docs/
    │   ├── study-design.md
    │   ├── data-generation.md
    │   ├── training-runs.md
    │   ├── inference-benchmarks.md
    │   ├── results-and-recommendation.md
    │   └── decisions/
    │       ├── ADR-001-base-model-choice.md
    │       └── ADR-002-lora-vs-full-fine-tune.md
    ├── src/
    │   ├── data/
    │   ├── training/
    │   ├── evaluation/
    │   └── serving/
    ├── configs/
    │   ├── lora.yaml
    │   ├── qlora.yaml
    │   └── vllm.yaml
    ├── benchmarks/
    │   ├── throughput_latency.py
    │   └── results/
    ├── model-card.md
    └── tests/
```

### Stage 17 — Interview Preparation & Getting Hired — `Interview Preparation & Getting Hired/`

```text
Interview Preparation & Getting Hired/
├── README.md
├── 00-Stage-17-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-job-search-campaign-tracker.md
├── 01-How-Frontier-Labs-Hire/
│   ├── README.md
│   ├── 01-the-hiring-pipeline.md
│   ├── 02-what-each-round-tests.md
│   ├── 03-common-rejection-reasons.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-target-company-research.md
├── 02-Resume-and-Portfolio-Presentation/
│   ├── README.md
│   ├── 01-resume-structure.md
│   ├── 02-writing-impact-bullets.md
│   ├── 03-github-and-portfolio-site.md
│   ├── 04-telling-a-career-change-story.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-resume-v1-and-review.md
├── 03-Coding-Interviews/
│   ├── README.md
│   ├── 01-practice-plan.md
│   ├── 02-practical-coding-rounds.md
│   ├── 03-debugging-rounds.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-timed-mock-coding-sessions.md
├── 04-AI-System-Design-Interviews/
│   ├── README.md
│   ├── 01-interview-framework.md
│   ├── 02-common-prompts.md
│   ├── 03-going-deep-on-trade-offs.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-mock-system-design-sessions.md
├── 05-Project-Deep-Dive-Interviews/
│   ├── README.md
│   ├── 01-preparing-each-project-story.md
│   ├── 02-surviving-the-why-chain.md
│   ├── 03-admitting-limitations.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-project-deep-dive-drills.md
├── 06-ML-and-LLM-Concepts-Interviews/
│   ├── README.md
│   ├── 01-core-ml-questions.md
│   ├── 02-llm-and-transformer-questions.md
│   ├── 03-rag-agents-and-evals-questions.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-concept-flashcards.md
├── 07-Behavioral-and-Mission-Interviews/
│   ├── README.md
│   ├── 01-star-stories.md
│   ├── 02-mission-and-safety-alignment.md
│   ├── 03-values-and-culture-questions.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-story-bank.md
├── 08-Take-Home-Assignments/
│   ├── README.md
│   ├── 01-scoping-a-take-home.md
│   ├── 02-delivering-a-strong-submission.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-practice-take-home.md
├── 09-Networking-and-Referrals/
│   ├── README.md
│   ├── 01-building-a-network-from-zero.md
│   ├── 02-reaching-out-well.md
│   ├── 03-community-and-events.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-outreach-plan.md
└── 10-Offers-and-First-90-Days/
    ├── README.md
    ├── 01-evaluating-offers.md
    ├── 02-negotiation-basics.md
    ├── 03-first-90-days-plan.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-ninety-day-plan.md
```

### Stage 18 — Career Growth to Senior — `Career Growth to Senior/`

```text
Career Growth to Senior/
├── README.md
├── 00-Stage-18-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-senior-readiness-evidence-portfolio.md
├── 01-Choosing-Your-First-AI-Role/
│   ├── README.md
│   ├── 01-role-types-that-build-toward-applied-ai.md
│   ├── 02-startup-vs-big-company.md
│   ├── 03-evaluating-learning-potential.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-role-selection-scorecard.md
├── 02-Growing-From-Junior-to-Mid-Level/
│   ├── README.md
│   ├── 01-delivering-reliably.md
│   ├── 02-owning-features-end-to-end.md
│   ├── 03-getting-feedback.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-quarterly-growth-plan.md
├── 03-What-Senior-Really-Means/
│   ├── README.md
│   ├── 01-scope-and-impact.md
│   ├── 02-technical-judgment.md
│   ├── 03-ambiguity-and-prioritization.md
│   ├── 04-multiplying-others.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-senior-gap-analysis.md
├── 04-Building-Senior-Evidence/
│   ├── README.md
│   ├── 01-brag-document.md
│   ├── 02-measurable-impact-stories.md
│   ├── 03-design-docs-and-launches.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-brag-document.md
├── 05-Staying-Current-With-the-Frontier/
│   ├── README.md
│   ├── 01-reading-routine.md
│   ├── 02-evaluating-new-models-quickly.md
│   ├── 03-separating-hype-from-signal.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-new-model-evaluation-memo.md
└── 06-Applying-as-a-Senior-Candidate/
    ├── README.md
    ├── 01-senior-interview-differences.md
    ├── 02-positioning-your-experience.md
    ├── 03-leveling-and-negotiation.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-senior-application-packet.md
```

## 4. Summary of new stages

| Stage | Folder | Modules | Lessons | Files | Stage project |
|---|---|---|---|---|---|
| 3 | `Data Structures & Algorithms/` | 10 | 53 | 98 | `algorithm-toolkit-and-benchmark` |
| 4 | `Mathematics for Machine Learning/` | 10 | 54 | 99 | `math-for-ml-notebook-library` |
| 5 | `Machine Learning Foundations/` | 10 | 48 | 93 | `end-to-end-classifier-with-error-analysis` |
| 6 | `Deep Learning & Transformers/` | 14 | 69 | 130 | `train-a-small-gpt-and-write-the-report` |
| 7 | `Backend Engineering for AI Systems/` | 11 | 50 | 99 | `production-ready-ai-api-service` |
| 8 | `LLM Application Engineering/` | 13 | 56 | 113 | `structured-document-extraction-service` |
| 9 | `Retrieval & RAG Systems/` | 13 | 54 | 111 | `rag-v1-foundation-for-flagship-1` |
| 10 | `Evaluation & Experimentation/` | 11 | 40 | 89 | `evalforge-v1-foundation-for-flagship-2` |
| 11 | `AI Agents & Tool Use/` | 13 | 51 | 108 | `analyst-agent-v1-foundation-for-flagship-3` |
| 12 | `AI Safety, Security & Responsible AI/` | 12 | 43 | 96 | `red-team-report-foundation-for-flagship-4` |
| 13 | `Model Customization & Inference/` | 12 | 40 | 93 | `specialized-small-model-foundation-for-flagship-7` |
| 14 | `LLMOps & AI System Design/` | 11 | 40 | 89 | `observability-layer-for-your-portfolio` |
| 15 | `Applied AI in the Field/` | 9 | 28 | 69 | `mock-customer-engagement` |
| 16 | `Flagship Portfolio Projects/` | 7 | — | 156 | `7 flagship repos (1 optional)` |
| 17 | `Interview Preparation & Getting Hired/` | 10 | 30 | 75 | `job-search-campaign-tracker` |
| 18 | `Career Growth to Senior/` | 6 | 19 | 48 | `senior-readiness-evidence-portfolio` |
| **Total** | | **172** | **675** | **1566** | |

## 5. Build order

```text
Stage 0 (exists) → 1 (exists) → 2 (exists, wrap up) → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11
                                                                                    │
                                  Milestone M4: start applying for first AI job ◄───┘

→ 12 → 13 → 14 → 16 → 17 → 18 (years, on the job)
  Stage 15 runs in parallel from Stage 8 onward (1–2 hours per week).

Flagship projects begin inside the stages and are finished in Stage 16:
  Stage 9  → Flagship 01 (Grounded RAG)       Stage 12 → Flagship 04 (Red Team & Guardrails)
  Stage 10 → Flagship 02 (EvalForge)          Stage 13 → Flagship 07 (Optional model study)
  Stage 11 → Flagship 03 (Analyst Agent)      Stage 15 → Flagship 05 (Customer case study)
  Stage 11 (Module 12) → Flagship 06 (Capstone coding agent), finished in Stage 16
```
