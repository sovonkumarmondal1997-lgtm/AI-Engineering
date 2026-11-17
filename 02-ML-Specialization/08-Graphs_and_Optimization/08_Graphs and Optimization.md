# Graphs and Optimization — ML Specialization Roadmap

**Group 8 (G8)** of the specialization that follows Stage 5D of the [Roadmap](./Roadmap.md). It covers original categories **17 Graph Machine Learning and 36 Operations Research and ML Optimization**. The group's defining question is: *how do I use relationships and constraints?* It follows G1 to G7: [`01_Classical and Applied ML.md`](./01_Classical%20and%20Applied%20ML.md), [`02_Deep Learning by Modality.md`](./02_Deep%20Learning%20by%20Modality.md), [`03_Generative and Foundation Models.md`](./03_Generative%20and%20Foundation%20Models.md), [`04_Agents and Sequential Decisions.md`](./04_Agents%20and%20Sequential%20Decisions.md), [`05_Time and Anomaly Modeling.md`](./05_Time%20and%20Anomaly%20Modeling.md), [`06_Personalization Search and Matching.md`](./06_Personalization%20Search%20and%20Matching.md), [`07_Statistical Reasoning.md`](./07_Statistical%20Reasoning.md).

## G8 summary

| Item | Count |
|---|---|
| Modules (including overview and capstones) | 16 |
| Lesson files | 130 |
| Hands-on project files (module projects, overview project and capstones) | 48 |
| Folders inside the G8 tree | 31 |
| Files inside the G8 tree | 216 |

| Original category | Modules |
|---|---|
| 17 Graph Machine Learning | 01 to 07 |
| 36 Operations Research and ML Optimization | 08 to 14 |

## Scope and how G8 avoids repeating the Roadmap

G8 starts where Stages 3, 4C and 5B stop. These are **already learned** and are only referenced, never retaught: graph representations, BFS and DFS, topological sort, union-find, Dijkstra, Bellman-Ford, Floyd-Warshall, minimum spanning trees, the introductions to max-flow and min-cut and to bipartite matching, bipartite graphs, dynamic programming including knapsack and bitmask DP, and greedy algorithms (Stage 3); convex sets and functions, optimality conditions, Lagrange multipliers, KKT conditions, duality introduction, convergence of gradient descent, conditioning, Newton and quasi-Newton methods, proximal methods and coordinate descent (Stage 4C); graph data and features, node embeddings with DeepWalk and node2vec, link prediction and graph-based fraud detection, the graph Laplacian and message-passing GNN basics, and graph ML evaluation and scaling (Stage 5B); Neo4j and Cypher as a graph database, and embedding and vector pipelines (Stage 2D); reinforcement learning (Stage 5B and G4); bandit and off-policy methods (Stage 5B); forecasting and probabilistic intervals (Stage 5B and G5); assignment, stable matching and min-cost flow used in matching markets (G6); decision-system design and predict-then-optimize in outline (G6); Bayesian optimization (G7); and the human-in-the-loop and serving patterns of Stage 5D.

**Boundaries with other groups** (so nothing overlaps): reinforcement-learning algorithms belong to **G4** and are only referenced in module 12; fraud, healthcare, financial and scientific domain applications belong to **G9** (module 06 covers only the graph methods); model compression and distributed training belong to **G10**; adversarial robustness and privacy methods for graphs belong to **G12**; benchmark and evaluation-system design belongs to **G13**.

| Roadmap topic already covered | Where G8 goes further |
|---|---|
| Graph representations and Neo4j (Stages 3, 2D) | Module 01: graph modeling choices, building graphs from data, processing engines, leakage and quality |
| Graph features and node embeddings (5B) | Module 02: centrality, PageRank, community detection, motifs, network models and diffusion |
| Message-passing GNN basics (5B) | Module 03: GCN, GraphSAGE, GAT, GIN, over-smoothing, graph transformers, heterophily and benchmark pitfalls |
| Graph ML evaluation and scaling (5B) | Module 04: neighbor sampling, precomputation, partitioning, temporal graphs and GNN serving |
| Link prediction and graph-based fraud (5B) | Modules 05 and 06: knowledge graph embeddings, heterogeneous graphs, GraphRAG, graph anomalies and recommenders |
| Contrastive learning (5C), graph ML (5B) | Module 07: graph self-supervision, text-attributed graphs, explanation reliability and fairness |
| KKT and duality theory (4C), max-flow introduction (Stage 3) | Module 08: formulation, duality in practice, MILP modeling, solver internals and debugging |
| Convex optimization theory (4C) | Module 09: CVXPY, conic solvers, nonlinear programming, derivative-free methods and differentiable layers |
| DP, greedy and shortest paths (Stage 3) | Module 10: VRP, local search, metaheuristics, CP-SAT scheduling and benchmark instances |
| Probabilistic forecasting (5B, G5), Bayesian methods (G7) | Module 11: stochastic and robust optimization, chance constraints and rolling-horizon planning |
| Decision-focused ideas (G6), RL (G4) | Module 12: decision-focused learning, learned heuristics and ML-assisted solvers |
| Matching markets (G6), forecasting (G5) | Module 13: logistics, network design, pricing, scheduling and resource allocation |
| Serving and CI/CD (5D) | Module 14: optimization services, anytime solutions, testing, explanation and licensing |

## G8 — Graphs and Optimization

**Defining question:** How do I use relationships and constraints?

```text
ML Specialization/
└── G8 — Graphs and Optimization/
    ├── 00-G8-Overview/
    │   ├── Projects/
    │   │   ├── 01-g8-graph-and-solver-environment-bootstrap.md
    │   │   └── README.md
    │   ├── 01-g8-scope-and-boundaries-with-stage-3-5b-and-other-groups.md
    │   ├── 02-prerequisite-map-from-the-roadmap.md
    │   ├── 03-dataset-and-tooling-register.md
    │   ├── 04-evaluation-and-reporting-standards.md
    │   ├── 05-completion-gate.md
    │   ├── README.md
    │   └── learning-plan.md
    ├── 01-Graph-Data-Engineering-and-Graph-Stores/
    │   ├── Projects/
    │   │   ├── 01-transaction-graph-builder-with-quality-checks.md
    │   │   ├── 02-graph-split-leakage-demonstration.md
    │   │   ├── 03-graph-engine-scale-benchmark.md
    │   │   └── README.md
    │   ├── 01-deciding-what-is-a-node-and-what-is-an-edge.md
    │   ├── 02-building-graphs-from-tabular-event-and-document-data.md
    │   ├── 03-property-graphs-vs-rdf-triples.md
    │   ├── 04-graph-stores-in-ml-pipelines.md
    │   ├── 05-graph-processing-engines.md
    │   ├── 06-heterogeneous-and-multi-relational-schemas.md
    │   ├── 07-temporal-graph-construction.md
    │   ├── 08-leakage-in-graph-learning.md
    │   ├── 09-graph-data-quality.md
    │   ├── 10-graph-store-selection-and-maintenance-risk.md
    │   └── README.md
    ├── 02-Graph-Analytics-and-Network-Science/
    │   ├── Projects/
    │   │   ├── 01-community-detection-comparison-with-ground-truth.md
    │   │   ├── 02-graph-features-for-gbdt.md
    │   │   ├── 03-influence-and-cascade-simulation.md
    │   │   └── README.md
    │   ├── 01-centrality-measures.md
    │   ├── 02-pagerank-and-personalized-pagerank.md
    │   ├── 03-community-detection.md
    │   ├── 04-label-propagation-and-spectral-clustering-on-graphs.md
    │   ├── 05-structural-features.md
    │   ├── 06-graph-similarity-and-kernels.md
    │   ├── 07-random-graph-models.md
    │   ├── 08-diffusion-and-influence-on-networks.md
    │   ├── 09-evaluating-communities-and-centralities-without-ground-truth.md
    │   └── README.md
    ├── 03-Graph-Neural-Network-Architectures/
    │   ├── Projects/
    │   │   ├── 01-gnn-from-scratch-then-library.md
    │   │   ├── 02-gnn-benchmark-with-strong-baselines.md
    │   │   ├── 03-over-smoothing-and-depth-study.md
    │   │   └── README.md
    │   ├── 01-the-message-passing-framework.md
    │   ├── 02-graph-convolutional-networks.md
    │   ├── 03-graphsage.md
    │   ├── 04-graph-attention-networks.md
    │   ├── 05-graph-isomorphism-networks-and-expressive-power-bounded-by-the-weisfeiler-lehman-test.md
    │   ├── 06-over-smoothing-and-over-squashing.md
    │   ├── 07-positional-and-structural-encodings.md
    │   ├── 08-graph-transformers.md
    │   ├── 09-heterophily.md
    │   ├── 10-implementation-with-pytorch-geometric-and-dgl-and-library-maintenance-checks.md
    │   ├── 11-benchmarking-pitfalls.md
    │   └── README.md
    ├── 04-Scalable-and-Temporal-Graph-Learning/
    │   ├── Projects/
    │   │   ├── 01-sampling-vs-full-batch-on-ogbn.md
    │   │   ├── 02-temporal-link-prediction-with-honest-evaluation.md
    │   │   ├── 03-gnn-inference-service.md
    │   │   └── README.md
    │   ├── 01-why-full-batch-gnn-training-fails-at-scale.md
    │   ├── 02-sampling-based-training.md
    │   ├── 03-precomputation-methods.md
    │   ├── 04-graph-partitioning-and-distributed-gnn-training.md
    │   ├── 05-gpu-graph-processing-and-memory-management.md
    │   ├── 06-temporal-graphs.md
    │   ├── 07-dynamic-link-prediction-evaluation.md
    │   ├── 08-streaming-graph-updates-and-online-embedding-refresh.md
    │   ├── 09-serving-gnn-predictions.md
    │   └── README.md
    ├── 05-Knowledge-Graphs-Link-Prediction-and-Heterogeneous-Graphs/
    │   ├── Projects/
    │   │   ├── 01-kg-completion-benchmark.md
    │   │   ├── 02-kg-from-documents-pipeline.md
    │   │   ├── 03-graph-rag-vs-plain-rag.md
    │   │   └── README.md
    │   ├── 01-knowledge-graph-embeddings.md
    │   ├── 02-knowledge-graph-completion-evaluation.md
    │   ├── 03-relational-gnns.md
    │   ├── 04-heterogeneous-graph-networks.md
    │   ├── 05-constructing-knowledge-graphs-from-text-using-extraction-models-from-g2-and-language-models.md
    │   ├── 06-entity-alignment-and-merging-graphs-from-several-sources.md
    │   ├── 07-ontologies-and-querying.md
    │   ├── 08-graph-based-retrieval-augmented-generation.md
    │   ├── 09-rules-reasoning-and-combining-symbolic-and-neural-methods.md
    │   └── README.md
    ├── 06-Graph-Applications-Fraud-Rings-Anomalies-and-Recommenders/
    │   ├── Projects/
    │   │   ├── 01-graph-fraud-detection-benchmark.md
    │   │   ├── 02-graph-recommender-vs-simple-baselines.md
    │   │   ├── 03-molecular-property-prediction.md
    │   │   └── README.md
    │   ├── 01-fraud-ring-and-collusion-detection.md
    │   ├── 02-graph-anomaly-detection.md
    │   ├── 03-camouflage-and-adversarial-behavior-in-graph-fraud.md
    │   ├── 04-social-network-analysis.md
    │   ├── 05-graph-recommenders.md
    │   ├── 06-spatio-temporal-graph-forecasting.md
    │   ├── 07-molecular-and-scientific-graphs.md
    │   ├── 08-supply-chain-and-infrastructure-networks.md
    │   ├── 09-choosing-between-a-graph-model-and-a-feature-engineered-tabular-model.md
    │   └── README.md
    ├── 07-Graph-Self-Supervision-Explanation-and-Graph-Foundation-Models/
    │   ├── Projects/
    │   │   ├── 01-graph-self-supervised-pretraining-study.md
    │   │   ├── 02-lm-plus-gnn-on-text-attributed-graphs.md
    │   │   ├── 03-gnn-explanation-reliability-test.md
    │   │   └── README.md
    │   ├── 01-graph-self-supervision.md
    │   ├── 02-masked-graph-autoencoders.md
    │   ├── 03-pretraining-on-molecules-and-transfer-across-graphs.md
    │   ├── 04-text-attributed-graphs.md
    │   ├── 05-graph-foundation-models.md
    │   ├── 06-explaining-gnn-predictions.md
    │   ├── 07-robustness.md
    │   ├── 08-fairness-and-privacy-in-graph-learning.md
    │   └── README.md
    ├── 08-Optimization-Modeling-Linear-and-Integer-Programming/
    │   ├── Projects/
    │   │   ├── 01-formulation-workbook-ten-classic-problems.md
    │   │   ├── 02-model-debugging-clinic.md
    │   │   ├── 03-sensitivity-analysis-for-a-business-plan.md
    │   │   └── README.md
    │   ├── 01-modeling-language.md
    │   ├── 02-linear-programming.md
    │   ├── 03-duality-in-practice.md
    │   ├── 04-mixed-integer-modeling.md
    │   ├── 05-classic-formulations-as-integer-programs.md
    │   ├── 06-network-flow-formulations.md
    │   ├── 07-piecewise-linear-and-nonconvex-modeling-tricks.md
    │   ├── 08-branch-and-bound-and-cutting-planes.md
    │   ├── 09-solver-tooling.md
    │   ├── 10-debugging-models.md
    │   └── README.md
    ├── 09-Convex-and-Nonlinear-Optimization-in-Practice/
    │   ├── Projects/
    │   │   ├── 01-portfolio-and-allocation-with-cvxpy.md
    │   │   ├── 02-solver-comparison-on-convex-problems.md
    │   │   ├── 03-black-box-optimization-comparison.md
    │   │   └── README.md
    │   ├── 01-disciplined-convex-programming-with-cvxpy.md
    │   ├── 02-quadratic-programming.md
    │   ├── 03-second-order-cone-and-semidefinite-programming-in-practice.md
    │   ├── 04-solver-choice-and-settings.md
    │   ├── 05-nonlinear-programming-with-ipopt-through-pyomo-or-casadi.md
    │   ├── 06-derivative-free-and-black-box-optimization.md
    │   ├── 07-constraint-handling-and-reformulation.md
    │   ├── 08-differentiable-optimization-layers.md
    │   ├── 09-numerical-issues.md
    │   └── README.md
    ├── 10-Combinatorial-Optimization-Routing-and-Scheduling/
    │   ├── Projects/
    │   │   ├── 01-vrp-solver-comparison-on-benchmark-instances.md
    │   │   ├── 02-shift-scheduling-with-cp-sat.md
    │   │   ├── 03-metaheuristic-vs-exact-study.md
    │   │   └── README.md
    │   ├── 01-routing-problems.md
    │   ├── 02-routing-with-or-tools-and-pyvrp.md
    │   ├── 03-local-search.md
    │   ├── 04-metaheuristics.md
    │   ├── 05-constraint-programming-with-cp-sat.md
    │   ├── 06-job-shop-and-workforce-scheduling.md
    │   ├── 07-bin-packing-and-cutting-stock.md
    │   ├── 08-benchmark-instance-libraries.md
    │   ├── 09-exact-vs-heuristic.md
    │   └── README.md
    ├── 11-Optimization-Under-Uncertainty/
    │   ├── Projects/
    │   │   ├── 01-two-stage-stochastic-vs-deterministic-planning.md
    │   │   ├── 02-scenario-count-study.md
    │   │   ├── 03-rolling-horizon-replanning-simulation.md
    │   │   └── README.md
    │   ├── 01-stochastic-programming.md
    │   ├── 02-sample-average-approximation-and-the-number-of-scenarios-needed.md
    │   ├── 03-robust-optimization.md
    │   ├── 04-chance-constraints-and-their-approximations.md
    │   ├── 05-distributionally-robust-optimization-introduction.md
    │   ├── 06-multi-period-planning-and-rolling-horizon-re-optimization.md
    │   ├── 07-inventory-models-under-demand-uncertainty-using-forecasts-from-g5.md
    │   ├── 08-simulation-optimization.md
    │   ├── 09-evaluating-plans-under-uncertainty.md
    │   └── README.md
    ├── 12-Predict-then-Optimize-and-Learning-to-Optimize/
    │   ├── Projects/
    │   │   ├── 01-two-stage-vs-decision-focused-learning.md
    │   │   ├── 02-learned-heuristic-vs-solver-benchmark.md
    │   │   ├── 03-warm-start-and-solver-acceleration.md
    │   │   └── README.md
    │   ├── 01-predict-then-optimize-pipelines-and-how-prediction-error-becomes-decision-regret.md
    │   ├── 02-decision-focused-learning.md
    │   ├── 03-implicit-differentiation-through-optimization-problems.md
    │   ├── 04-regret-as-the-evaluation-metric-and-comparison-with-prediction-accuracy.md
    │   ├── 05-surrogate-models-for-expensive-simulations.md
    │   ├── 06-neural-combinatorial-optimization.md
    │   ├── 07-machine-learning-inside-solvers.md
    │   ├── 08-graph-neural-networks-for-combinatorial-problems-using-the-models-from-modules-03-to-05.md
    │   ├── 09-fair-comparison-with-strong-solvers.md
    │   └── README.md
    ├── 13-Operations-Applications-Logistics-Supply-Chain-and-Resource-Allocation/
    │   ├── Projects/
    │   │   ├── 01-last-mile-routing-with-real-constraints.md
    │   │   ├── 02-network-design-case-study.md
    │   │   ├── 03-dynamic-pricing-under-capacity.md
    │   │   └── README.md
    │   ├── 01-supply-chain-network-design-and-facility-location.md
    │   ├── 02-inventory-routing-and-replenishment-planning.md
    │   ├── 03-last-mile-delivery.md
    │   ├── 04-pricing-and-revenue-management-under-capacity-constraints.md
    │   ├── 05-assortment-and-promotion-planning-with-constraints.md
    │   ├── 06-workforce-and-fleet-scheduling.md
    │   ├── 07-energy-dispatch-and-unit-commitment.md
    │   ├── 08-cloud-and-cluster-resource-allocation.md
    │   ├── 09-case-study-method.md
    │   └── README.md
    ├── 14-Optimization-Systems-Engineering-and-Deployment/
    │   ├── Projects/
    │   │   ├── 01-optimization-service-with-fallbacks.md
    │   │   ├── 02-optimization-regression-test-suite.md
    │   │   ├── 03-licensing-and-solver-selection-review.md
    │   │   └── README.md
    │   ├── 01-optimization-pipelines.md
    │   ├── 02-solver-performance.md
    │   ├── 03-anytime-behavior-and-fallback-solutions-when-time-runs-out.md
    │   ├── 04-decomposition.md
    │   ├── 05-testing-optimization-code.md
    │   ├── 06-explaining-solutions.md
    │   ├── 07-deployment-patterns.md
    │   ├── 08-human-override-and-planner-workflows.md
    │   ├── 09-monitoring.md
    │   ├── 10-licensing-and-cost.md
    │   └── README.md
    ├── 15-G8-Capstones/
    │   ├── 01-graph-learning-system-for-a-real-network.md
    │   ├── 02-knowledge-graph-and-graph-rag-application.md
    │   ├── 03-operations-optimization-platform.md
    │   ├── 04-predict-and-optimize-decision-system.md
    │   ├── 05-g8-readiness-assessment.md
    │   └── README.md
    └── README.md
```

### 00 — G8 Overview

**Purpose:** the single authoritative plan for G8 with scope, boundaries, prerequisite map, dataset and tooling register, evaluation standards and completion gate.

- `01-g8-scope-and-boundaries-with-stage-3-5b-and-other-groups.md` — what G8 teaches and what it leaves to other groups.
- `02-prerequisite-map-from-the-roadmap.md` — Roadmap stages and modules assumed for each G8 module.
- `03-dataset-and-tooling-register.md` — every dataset, licence and access condition, library or solver with version, licence and maintenance status.
- `04-evaluation-and-reporting-standards.md` — split rules for graphs, optimality-gap and regret reporting, benchmark-instance rules and report template.
- `05-completion-gate.md` — measurable criteria to finish G8.
- `learning-plan.md` — recommended order, graph and optimization tracks and compute budget.

**Project 1: g8 graph and solver environment bootstrap**  
- Data: a small graph and a small optimization instance with a known optimum.  
- Task: build a reproducible workspace with pinned tooling, a graph-split harness that rejects leaky splits, and an optimization harness that verifies feasibility and reports optimality gaps against known-answer instances.  
- Deliverables: lockfile, both harnesses and smoke tests.  
- Pass gate: a clean machine reproduces the tests from the lockfile, a deliberately leaky split is rejected and an infeasible solution is flagged by the verifier.

### 01 — Graph Data Engineering and Graph Stores

**Outcome:** Turn raw records into trustworthy graphs and choose where to store and query them. Graph representations, traversal, Dijkstra, shortest paths and graph features are covered in Stages 3 and 5B, and the Neo4j and Cypher graph-database lesson in Stage 2D; none are repeated.

**Lessons**

- `01-deciding-what-is-a-node-and-what-is-an-edge.md` — Deciding what is a node and what is an edge: modeling choices and their consequences
- `02-building-graphs-from-tabular-event-and-document-data.md` — Building graphs from tabular, event and document data
- `03-property-graphs-vs-rdf-triples.md` — Property graphs vs RDF triples: when each fits
- `04-graph-stores-in-ml-pipelines.md` — Graph stores in ML pipelines: exporting, sampling and indexing graphs from a graph database for training (Neo4j and Cypher themselves are covered in Stage 2D)
- `05-graph-processing-engines.md` — Graph processing engines: NetworkX limits, igraph, graph-tool, cuGraph and Spark GraphFrames
- `06-heterogeneous-and-multi-relational-schemas.md` — Heterogeneous and multi-relational schemas: typed nodes, typed edges and metadata
- `07-temporal-graph-construction.md` — Temporal graph construction: timestamps, event streams and snapshots
- `08-leakage-in-graph-learning.md` — Leakage in graph learning: transductive vs inductive splits and edge-level leakage
- `09-graph-data-quality.md` — Graph data quality: duplicate nodes, missing edges, spam and noisy links
- `10-graph-store-selection-and-maintenance-risk.md` — Graph store selection and maintenance risk: checking project status before adopting

**Hands-on projects**

- **Project 1: transaction graph builder with quality checks**  
  - Data: A public transaction or interaction dataset such as the Elliptic Bitcoin dataset or MovieLens  
  - Task: Build a graph with explicit schema, load it into a graph store and write quality checks for duplicates, orphans and timestamp consistency.  
  - Deliverables: Builder, schema, loaded graph and checks.  
  - Pass gate: Checks catch deliberately injected defects.
- **Project 2: graph split leakage demonstration**  
  - Data: A citation graph such as Cora or ogbn-arxiv  
  - Task: Show how random edge splits, transductive splits and temporal splits change link-prediction and node-classification scores.  
  - Deliverables: Comparison with explanation.  
  - Pass gate: Temporal split used as the reference.
- **Project 3: graph engine scale benchmark**  
  - Data: SNAP graphs of increasing size  
  - Task: Compare NetworkX, igraph and cuGraph (if a GPU is available) on common analytics at several graph sizes.  
  - Deliverables: Benchmark report with time and memory.  
  - Pass gate: Same algorithms and settings across engines.

### 02 — Graph Analytics and Network Science

**Outcome:** Use the classical graph toolkit before and alongside neural methods. Graph feature basics and graph algorithms are covered in Stages 3 and 5B; this module covers centrality, communities and network models.

**Lessons**

- `01-centrality-measures.md` — Centrality measures: degree, closeness, betweenness and eigenvector centrality and their costs
- `02-pagerank-and-personalized-pagerank.md` — PageRank and personalized PageRank: computation and use as a feature
- `03-community-detection.md` — Community detection: modularity, Louvain and Leiden and the resolution limit
- `04-label-propagation-and-spectral-clustering-on-graphs.md` — Label propagation and spectral clustering on graphs
- `05-structural-features.md` — Structural features: triangles, clustering coefficient, k-cores and motifs
- `06-graph-similarity-and-kernels.md` — Graph similarity and kernels: Weisfeiler-Lehman and its role in expressiveness
- `07-random-graph-models.md` — Random graph models: Erdos-Renyi, preferential attachment and stochastic block models
- `08-diffusion-and-influence-on-networks.md` — Diffusion and influence on networks: cascades and epidemic models
- `09-evaluating-communities-and-centralities-without-ground-truth.md` — Evaluating communities and centralities without ground truth

**Hands-on projects**

- **Project 1: community detection comparison with ground truth**  
  - Data: SNAP graphs with ground-truth communities and LFR synthetic benchmarks  
  - Task: Compare Louvain, Leiden, label propagation and spectral methods using normalized mutual information and stability.  
  - Deliverables: Comparison across graph types.  
  - Pass gate: Stability measured over repeated runs.
- **Project 2: graph features for gbdt**  
  - Data: A fraud or churn dataset with relationships  
  - Task: Build centrality, community and motif features, add them to a G1 gradient-boosting model and measure the gain.  
  - Deliverables: Feature pipeline and ablation.  
  - Pass gate: Features computed without leaking future edges.
- **Project 3: influence and cascade simulation**  
  - Data: A social graph from SNAP  
  - Task: Simulate cascades under independent-cascade and threshold models and compare seed-selection heuristics.  
  - Deliverables: Simulation results with intervals.  
  - Pass gate: Many simulation runs per seed set.

### 03 — Graph Neural Network Architectures

**Outcome:** Implement and compare the main GNN families and know their limits. The graph Laplacian and the message-passing basics are covered in Stage 5B.

**Lessons**

- `01-the-message-passing-framework.md` — The message-passing framework: aggregation, update and readout design
- `02-graph-convolutional-networks.md` — Graph convolutional networks: spectral motivation and spatial practice
- `03-graphsage.md` — GraphSAGE: inductive learning and aggregators
- `04-graph-attention-networks.md` — Graph attention networks: attention over neighbors
- `05-graph-isomorphism-networks-and-expressive-power-bounded-by-the-weisfeiler-lehman-test.md` — Graph isomorphism networks and expressive power bounded by the Weisfeiler-Lehman test
- `06-over-smoothing-and-over-squashing.md` — Over-smoothing and over-squashing: causes and remedies
- `07-positional-and-structural-encodings.md` — Positional and structural encodings: Laplacian and random-walk encodings
- `08-graph-transformers.md` — Graph transformers: Graphormer and GPS-style architectures
- `09-heterophily.md` — Heterophily: when neighbors differ and how models adapt
- `10-implementation-with-pytorch-geometric-and-dgl-and-library-maintenance-checks.md` — Implementation with PyTorch Geometric and DGL, and library maintenance checks
- `11-benchmarking-pitfalls.md` — Benchmarking pitfalls: weak baselines, fixed splits and dataset size on citation graphs

**Hands-on projects**

- **Project 1: gnn from scratch then library**  
  - Data: Cora, CiteSeer and PubMed  
  - Task: Implement GCN, GraphSAGE and GAT in plain PyTorch and match library implementations.  
  - Deliverables: Implementations and equivalence tests.  
  - Pass gate: Outputs match the library on a fixed seed within tolerance.
- **Project 2: gnn benchmark with strong baselines**  
  - Data: Several node-classification datasets including a heterophilous one  
  - Task: Compare GNNs with tuned MLP, label propagation and feature-plus-graph-features GBDT using many random splits.  
  - Deliverables: Benchmark with intervals.  
  - Pass gate: Baselines tuned with equal budgets and at least 10 random splits.
- **Project 3: over smoothing and depth study**  
  - Data: Cora and a larger graph  
  - Task: Measure accuracy and representation similarity as depth grows and test residual connections and normalization remedies.  
  - Deliverables: Depth curves and diagnostics.  
  - Pass gate: Representation similarity measured with a stated metric.

### 04 — Scalable and Temporal Graph Learning

**Outcome:** Train and serve graph models on large and evolving graphs. Graph machine learning evaluation and scaling basics are covered in Stage 5B.

**Lessons**

- `01-why-full-batch-gnn-training-fails-at-scale.md` — Why full-batch GNN training fails at scale: neighborhood explosion
- `02-sampling-based-training.md` — Sampling-based training: neighbor sampling, Cluster-GCN and GraphSAINT
- `03-precomputation-methods.md` — Precomputation methods: SGC and SIGN for fast training and inference
- `04-graph-partitioning-and-distributed-gnn-training.md` — Graph partitioning and distributed GNN training
- `05-gpu-graph-processing-and-memory-management.md` — GPU graph processing and memory management
- `06-temporal-graphs.md` — Temporal graphs: continuous-time and discrete-time models such as TGN and TGAT
- `07-dynamic-link-prediction-evaluation.md` — Dynamic link prediction evaluation: negative sampling and the Temporal Graph Benchmark
- `08-streaming-graph-updates-and-online-embedding-refresh.md` — Streaming graph updates and online embedding refresh
- `09-serving-gnn-predictions.md` — Serving GNN predictions: latency, caching and feature freshness

**Hands-on projects**

- **Project 1: sampling vs full batch on ogbn**  
  - Data: ogbn-arxiv and ogbn-products (check size and hardware)  
  - Task: Compare full-batch, neighbor sampling, Cluster-GCN and precomputation on accuracy, memory and time.  
  - Deliverables: Cost-accuracy comparison.  
  - Pass gate: Hardware and memory limits recorded.
- **Project 2: temporal link prediction with honest evaluation**  
  - Data: Temporal Graph Benchmark datasets or JODIE Wikipedia and Reddit  
  - Task: Compare TGN, simple recency baselines and memory-free models using the benchmark's negative-sampling protocol.  
  - Deliverables: Results with strong simple baselines.  
  - Pass gate: Benchmark evaluation protocol followed exactly.
- **Project 3: gnn inference service**  
  - Data: A trained node model  
  - Task: Serve predictions with cached neighborhoods and measure latency and staleness as the graph changes.  
  - Deliverables: Service and latency analysis.  
  - Pass gate: Staleness measured against a freshly recomputed result.

### 05 — Knowledge Graphs Link Prediction and Heterogeneous Graphs

**Outcome:** Model typed relations and multi-relational data, and build knowledge graphs from text. Basic link prediction is covered in Stage 5B; relation extraction from text is covered in G2.

**Lessons**

- `01-knowledge-graph-embeddings.md` — Knowledge graph embeddings: TransE, DistMult, ComplEx and RotatE
- `02-knowledge-graph-completion-evaluation.md` — Knowledge graph completion evaluation: filtered ranking, Hits at k and test-leakage traps such as inverse relations
- `03-relational-gnns.md` — Relational GNNs: R-GCN
- `04-heterogeneous-graph-networks.md` — Heterogeneous graph networks: HAN and HGT
- `05-constructing-knowledge-graphs-from-text-using-extraction-models-from-g2-and-language-models.md` — Constructing knowledge graphs from text using extraction models from G2 and language models
- `06-entity-alignment-and-merging-graphs-from-several-sources.md` — Entity alignment and merging graphs from several sources
- `07-ontologies-and-querying.md` — Ontologies and querying: schemas and SPARQL basics
- `08-graph-based-retrieval-augmented-generation.md` — Graph-based retrieval-augmented generation: building entity graphs and community summaries and evaluating against plain RAG from G3
- `09-rules-reasoning-and-combining-symbolic-and-neural-methods.md` — Rules, reasoning and combining symbolic and neural methods

**Hands-on projects**

- **Project 1: kg completion benchmark**  
  - Data: FB15k-237 and WN18RR  
  - Task: Compare TransE, DistMult, ComplEx, RotatE and R-GCN with filtered ranking and examine leakage in the older FB15k.  
  - Deliverables: Benchmark and leakage analysis.  
  - Pass gate: Filtered metrics used and inverse-relation leakage demonstrated.
- **Project 2: kg from documents pipeline**  
  - Data: A public document corpus such as government reports or Wikipedia articles  
  - Task: Extract entities and relations, build and clean a graph and measure precision against a hand-labeled sample.  
  - Deliverables: Pipeline and precision analysis.  
  - Pass gate: Hand-labeled sample of at least 200 triples.
- **Project 3: graph rag vs plain rag**  
  - Data: A question set needing multi-hop reasoning over a corpus  
  - Task: Compare plain RAG with graph-based RAG on accuracy and cost and identify where the graph helps.  
  - Deliverables: Comparison with cost.  
  - Pass gate: Index-building cost included in the comparison.

### 06 — Graph Applications Fraud Rings Anomalies and Recommenders

**Outcome:** Apply graph models to the standard application families. Fraud and risk as a business domain is covered later in G9; this module covers the graph methods.

**Lessons**

- `01-fraud-ring-and-collusion-detection.md` — Fraud-ring and collusion detection: graph features, GNNs and their label scarcity
- `02-graph-anomaly-detection.md` — Graph anomaly detection: node, edge and subgraph anomalies and reconstruction-based methods
- `03-camouflage-and-adversarial-behavior-in-graph-fraud.md` — Camouflage and adversarial behavior in graph fraud
- `04-social-network-analysis.md` — Social network analysis: bots, coordinated behavior and influence
- `05-graph-recommenders.md` — Graph recommenders: LightGCN and PinSage-style models and when they beat simpler methods
- `06-spatio-temporal-graph-forecasting.md` — Spatio-temporal graph forecasting: traffic and sensor networks as an application
- `07-molecular-and-scientific-graphs.md` — Molecular and scientific graphs: property prediction with GNNs
- `08-supply-chain-and-infrastructure-networks.md` — Supply-chain and infrastructure networks: risk propagation
- `09-choosing-between-a-graph-model-and-a-feature-engineered-tabular-model.md` — Choosing between a graph model and a feature-engineered tabular model

**Hands-on projects**

- **Project 1: graph fraud detection benchmark**  
  - Data: Elliptic Bitcoin dataset and a public fraud graph such as YelpChi or Amazon from CARE-GNN data  
  - Task: Compare GBDT with graph features, GCN, GraphSAGE and a fraud-specific GNN with temporal splits and precision at review capacity.  
  - Deliverables: Benchmark with temporal evaluation.  
  - Pass gate: Temporal split and an alert-capacity metric used.
- **Project 2: graph recommender vs simple baselines**  
  - Data: MovieLens or Amazon Reviews  
  - Task: Compare LightGCN with matrix factorization and a tuned item-kNN under G6 evaluation rules.  
  - Deliverables: Comparison with intervals.  
  - Pass gate: Baselines tuned with equal effort.
- **Project 3: molecular property prediction**  
  - Data: OGB ogbg-molhiv or a MoleculeNet task  
  - Task: Train a GNN and compare with fingerprint-based GBDT using scaffold splits.  
  - Deliverables: Comparison under scaffold split.  
  - Pass gate: Scaffold split used, not random.

### 07 — Graph Self Supervision Explanation and Graph Foundation Models

**Outcome:** Learn from unlabeled graphs, combine graphs with language models and explain and stress-test graph models.

**Lessons**

- `01-graph-self-supervision.md` — Graph self-supervision: contrastive learning with DGI, GRACE and GraphCL
- `02-masked-graph-autoencoders.md` — Masked graph autoencoders: GraphMAE-style pretraining
- `03-pretraining-on-molecules-and-transfer-across-graphs.md` — Pretraining on molecules and transfer across graphs
- `04-text-attributed-graphs.md` — Text-attributed graphs: combining language models with GNNs
- `05-graph-foundation-models.md` — Graph foundation models: what exists, what is evidenced and what is hype
- `06-explaining-gnn-predictions.md` — Explaining GNN predictions: GNNExplainer and PGExplainer and their reliability
- `07-robustness.md` — Robustness: graph adversarial attacks and defenses as an overview with depth in G12
- `08-fairness-and-privacy-in-graph-learning.md` — Fairness and privacy in graph learning: link and attribute leakage

**Hands-on projects**

- **Project 1: graph self supervised pretraining study**  
  - Data: Cora, ogbn-arxiv and a molecular dataset  
  - Task: Compare supervised training with contrastive and masked pretraining under few labels.  
  - Deliverables: Label-budget curves.  
  - Pass gate: Same probe protocol for every method.
- **Project 2: lm plus gnn on text attributed graphs**  
  - Data: ogbn-arxiv with paper text  
  - Task: Compare GNN on bag-of-words, language-model embeddings and fine-tuned language models with and without graph structure.  
  - Deliverables: Ablation.  
  - Pass gate: Structure and text contributions separated.
- **Project 3: gnn explanation reliability test**  
  - Data: A graph dataset with planted ground-truth motifs  
  - Task: Test whether GNN explainers recover the planted motifs and how often explanations change under small perturbations.  
  - Deliverables: Explainer reliability analysis.  
  - Pass gate: Ground truth known by construction.

### 08 — Optimization Modeling Linear and Integer Programming

**Outcome:** Formulate real problems as linear and integer programs and solve them reliably. Convex sets, optimality conditions, KKT conditions and duality introductions are covered in Stage 4C; shortest paths, flows and matching introductions in Stage 3; assignment and min-cost flow used in matching in G6.

**Lessons**

- `01-modeling-language.md` — Modeling language: variables, constraints, objectives and the formulation workflow
- `02-linear-programming.md` — Linear programming: feasible regions, simplex and interior-point intuition
- `03-duality-in-practice.md` — Duality in practice: shadow prices, reduced costs and sensitivity analysis
- `04-mixed-integer-modeling.md` — Mixed-integer modeling: binaries, logical constraints, big-M and indicator constraints
- `05-classic-formulations-as-integer-programs.md` — Classic formulations as integer programs: knapsack (solved by dynamic programming in Stage 3), set cover, facility location, transportation and assignment
- `06-network-flow-formulations.md` — Network flow formulations: min-cost flow and multi-commodity flow
- `07-piecewise-linear-and-nonconvex-modeling-tricks.md` — Piecewise-linear and nonconvex modeling tricks
- `08-branch-and-bound-and-cutting-planes.md` — Branch-and-bound and cutting planes: what the solver is doing and why models are slow
- `09-solver-tooling.md` — Solver tooling: SciPy HiGHS, PuLP, Pyomo, OR-Tools, SCIP and commercial solvers with licence checks
- `10-debugging-models.md` — Debugging models: infeasibility, unboundedness, scaling problems and irreducible infeasible subsets

**Hands-on projects**

- **Project 1: formulation workbook ten classic problems**  
  - Data: Ten problem statements you write covering production planning, blending, scheduling, location and packing  
  - Task: Formulate each, solve with two solvers, verify against brute force on small instances and interpret shadow prices.  
  - Deliverables: Workbook of models and verification.  
  - Pass gate: Each model verified against an independent method on small instances.
- **Project 2: model debugging clinic**  
  - Data: Deliberately broken models you construct  
  - Task: Diagnose infeasible, unbounded and badly scaled models and document the fix for each.  
  - Deliverables: Debugging log.  
  - Pass gate: Every broken model fixed with the cause identified.
- **Project 3: sensitivity analysis for a business plan**  
  - Data: A production-planning model  
  - Task: Use dual values and re-solves to answer what-if questions and verify the answers by re-optimizing.  
  - Deliverables: Sensitivity report.  
  - Pass gate: Dual-based answers match re-solved results.

### 09 — Convex and Nonlinear Optimization in Practice

**Outcome:** Solve convex and nonlinear problems with modeling tools instead of hand-written solvers. The theory of convexity, optimality conditions, Newton and quasi-Newton methods and proximal methods is covered in Stage 4C.

**Lessons**

- `01-disciplined-convex-programming-with-cvxpy.md` — Disciplined convex programming with CVXPY
- `02-quadratic-programming.md` — Quadratic programming: portfolio-style and regularized problems
- `03-second-order-cone-and-semidefinite-programming-in-practice.md` — Second-order cone and semidefinite programming in practice
- `04-solver-choice-and-settings.md` — Solver choice and settings: OSQP, SCS and Clarabel
- `05-nonlinear-programming-with-ipopt-through-pyomo-or-casadi.md` — Nonlinear programming with IPOPT through Pyomo or CasADi
- `06-derivative-free-and-black-box-optimization.md` — Derivative-free and black-box optimization: Nelder-Mead and CMA-ES
- `07-constraint-handling-and-reformulation.md` — Constraint handling and reformulation: turning problems into convex form
- `08-differentiable-optimization-layers.md` — Differentiable optimization layers: cvxpylayers and implicit differentiation
- `09-numerical-issues.md` — Numerical issues: scaling, conditioning and solver failure modes

**Hands-on projects**

- **Project 1: portfolio and allocation with cvxpy**  
  - Data: Public asset-return data or a synthetic allocation problem  
  - Task: Build mean-variance and robust allocation models with constraints and compare out-of-sample.  
  - Deliverables: Models and out-of-sample evaluation.  
  - Pass gate: Out-of-sample period never used in estimation.
- **Project 2: solver comparison on convex problems**  
  - Data: A suite of QP, SOCP and SDP instances  
  - Task: Compare solvers on time, accuracy and failure rate.  
  - Deliverables: Benchmark.  
  - Pass gate: Same instances and tolerances for every solver.
- **Project 3: black box optimization comparison**  
  - Data: An expensive simulator or benchmark function  
  - Task: Compare random search, CMA-ES, Nelder-Mead and Bayesian optimization at fixed budgets.  
  - Deliverables: Regret curves with repeats.  
  - Pass gate: At least 20 repeats per method.

### 10 — Combinatorial Optimization Routing and Scheduling

**Outcome:** Solve routing, scheduling and packing problems with exact and heuristic methods. Dynamic programming, bitmask DP, greedy algorithms and shortest paths are covered in Stage 3 and are not repeated.

**Lessons**

- `01-routing-problems.md` — Routing problems: TSP, capacitated VRP and time-window variants
- `02-routing-with-or-tools-and-pyvrp.md` — Routing with OR-Tools and PyVRP
- `03-local-search.md` — Local search: 2-opt, Or-opt and large neighborhood search
- `04-metaheuristics.md` — Metaheuristics: simulated annealing, tabu search and genetic algorithms and when they are justified
- `05-constraint-programming-with-cp-sat.md` — Constraint programming with CP-SAT: modeling and propagation
- `06-job-shop-and-workforce-scheduling.md` — Job-shop and workforce scheduling: shift and rostering problems
- `07-bin-packing-and-cutting-stock.md` — Bin packing and cutting stock
- `08-benchmark-instance-libraries.md` — Benchmark instance libraries: TSPLIB, Solomon and MIPLIB, and optimality-gap reporting
- `09-exact-vs-heuristic.md` — Exact vs heuristic: choosing by instance size, time limit and gap tolerance

**Hands-on projects**

- **Project 1: vrp solver comparison on benchmark instances**  
  - Data: Solomon and Homberger VRPTW instances  
  - Task: Compare OR-Tools routing, PyVRP and a hand-written local search on cost and time against best-known solutions.  
  - Deliverables: Gap-to-best-known table.  
  - Pass gate: Gap reported against published best-known values.
- **Project 2: shift scheduling with cp sat**  
  - Data: A staffing scenario with coverage, fairness and legal rules you define  
  - Task: Model and solve shift scheduling and study how constraints change cost and fairness.  
  - Deliverables: Model, solutions and trade-off analysis.  
  - Pass gate: Constraint satisfaction verified by an independent checker.
- **Project 3: metaheuristic vs exact study**  
  - Data: Knapsack and TSP instances of growing size  
  - Task: Compare exact methods with simulated annealing and genetic algorithms as size grows.  
  - Deliverables: Scaling comparison.  
  - Pass gate: Run-time limits equal across methods.

### 11 — Optimization Under Uncertainty

**Outcome:** Plan when inputs are uncertain. Probabilistic forecasts and conformal intervals are covered in Stage 5B and G5; this module uses them inside optimization models.

**Lessons**

- `01-stochastic-programming.md` — Stochastic programming: two-stage models and scenario trees
- `02-sample-average-approximation-and-the-number-of-scenarios-needed.md` — Sample average approximation and the number of scenarios needed
- `03-robust-optimization.md` — Robust optimization: uncertainty sets and the price of robustness
- `04-chance-constraints-and-their-approximations.md` — Chance constraints and their approximations
- `05-distributionally-robust-optimization-introduction.md` — Distributionally robust optimization introduction
- `06-multi-period-planning-and-rolling-horizon-re-optimization.md` — Multi-period planning and rolling-horizon re-optimization
- `07-inventory-models-under-demand-uncertainty-using-forecasts-from-g5.md` — Inventory models under demand uncertainty using forecasts from G5
- `08-simulation-optimization.md` — Simulation-optimization: optimizing systems evaluated by simulation
- `09-evaluating-plans-under-uncertainty.md` — Evaluating plans under uncertainty: out-of-sample cost and risk measures

**Hands-on projects**

- **Project 1: two stage stochastic vs deterministic planning**  
  - Data: A production or inventory planning problem with stochastic demand  
  - Task: Compare deterministic-mean planning, stochastic programming and robust optimization on out-of-sample cost.  
  - Deliverables: Comparison with intervals.  
  - Pass gate: Out-of-sample scenarios held out from planning.
- **Project 2: scenario count study**  
  - Data: The same problem  
  - Task: Measure solution quality and stability as the number of scenarios grows.  
  - Deliverables: Quality-versus-scenarios analysis.  
  - Pass gate: Many resampled scenario sets.
- **Project 3: rolling horizon replanning simulation**  
  - Data: A multi-period operations simulator  
  - Task: Compare static and rolling-horizon planning with forecast errors.  
  - Deliverables: Simulation results.  
  - Pass gate: Forecast errors drawn from realistic distributions.

### 12 — Predict then Optimize and Learning to Optimize

**Outcome:** Combine machine-learned predictions with optimization and know when learned heuristics beat solvers. Reinforcement-learning algorithms are covered in G4 and referenced here.

**Lessons**

- `01-predict-then-optimize-pipelines-and-how-prediction-error-becomes-decision-regret.md` — Predict-then-optimize pipelines and how prediction error becomes decision regret
- `02-decision-focused-learning.md` — Decision-focused learning: the SPO+ loss and perturbed optimizers
- `03-implicit-differentiation-through-optimization-problems.md` — Implicit differentiation through optimization problems
- `04-regret-as-the-evaluation-metric-and-comparison-with-prediction-accuracy.md` — Regret as the evaluation metric and comparison with prediction accuracy
- `05-surrogate-models-for-expensive-simulations.md` — Surrogate models for expensive simulations
- `06-neural-combinatorial-optimization.md` — Neural combinatorial optimization: attention-based routing models and their limits against strong solvers
- `07-machine-learning-inside-solvers.md` — Machine learning inside solvers: learned branching, warm starts and primal heuristics
- `08-graph-neural-networks-for-combinatorial-problems-using-the-models-from-modules-03-to-05.md` — Graph neural networks for combinatorial problems using the models from modules 03 to 05
- `09-fair-comparison-with-strong-solvers.md` — Fair comparison with strong solvers: time, quality and generalization to unseen instance distributions

**Hands-on projects**

- **Project 1: two stage vs decision focused learning**  
  - Data: A shortest-path or assignment problem with noisy edge costs predicted from features  
  - Task: Compare two-stage training with decision-focused training on regret and prediction error.  
  - Deliverables: Regret comparison with intervals.  
  - Pass gate: Regret measured against the true-cost optimum.
- **Project 2: learned heuristic vs solver benchmark**  
  - Data: Random and structured TSP or knapsack instances  
  - Task: Train a neural construction heuristic and compare with OR-Tools and a local search on quality and time across instance distributions.  
  - Deliverables: Benchmark including distribution shift.  
  - Pass gate: Solver given a time budget equal to the learned model's total cost.
- **Project 3: warm start and solver acceleration**  
  - Data: A family of related MILP instances  
  - Task: Learn to predict good starting solutions and measure time-to-gap against solver defaults.  
  - Deliverables: Time-to-gap comparison.  
  - Pass gate: Gaps verified with solver bounds.

### 13 — Operations Applications Logistics Supply Chain and Resource Allocation

**Outcome:** Apply optimization to the recurring operational problem families, including Indian logistics settings.

**Lessons**

- `01-supply-chain-network-design-and-facility-location.md` — Supply-chain network design and facility location
- `02-inventory-routing-and-replenishment-planning.md` — Inventory-routing and replenishment planning
- `03-last-mile-delivery.md` — Last-mile delivery: batching, zones and driver constraints, with Indian address and traffic realities
- `04-pricing-and-revenue-management-under-capacity-constraints.md` — Pricing and revenue management under capacity constraints
- `05-assortment-and-promotion-planning-with-constraints.md` — Assortment and promotion planning with constraints
- `06-workforce-and-fleet-scheduling.md` — Workforce and fleet scheduling
- `07-energy-dispatch-and-unit-commitment.md` — Energy dispatch and unit commitment
- `08-cloud-and-cluster-resource-allocation.md` — Cloud and cluster resource allocation: packing and placement
- `09-case-study-method.md` — Case-study method: from messy requirements to a solved model and an implemented policy

**Hands-on projects**

- **Project 1: last mile routing with real constraints**  
  - Data: Amazon Last Mile Routing Research Challenge data (check terms) or NYC TLC-based simulation  
  - Task: Build a route planner that respects capacity and time windows and compare with driver-preferred routes where available.  
  - Deliverables: Planner and comparison.  
  - Pass gate: Constraint satisfaction verified automatically.
- **Project 2: network design case study**  
  - Data: A synthetic national distribution network based on public population and demand data  
  - Task: Solve a facility-location and flow design and test it against demand scenarios.  
  - Deliverables: Model and scenario results.  
  - Pass gate: Assumptions documented with sources.
- **Project 3: dynamic pricing under capacity**  
  - Data: A simulated perishable-inventory market  
  - Task: Compare fixed, heuristic and optimized pricing policies on revenue and sell-through.  
  - Deliverables: Policy comparison.  
  - Pass gate: Demand model stated and varied.

### 14 — Optimization Systems Engineering and Deployment

**Outcome:** Ship optimization as a dependable decision service. General MLOps, serving and CI/CD are covered in Stage 5D; the decision-system design of G6 is referenced here.

**Lessons**

- `01-optimization-pipelines.md` — Optimization pipelines: data to model to solve to decision
- `02-solver-performance.md` — Solver performance: presolve, warm starts, tolerances and time limits
- `03-anytime-behavior-and-fallback-solutions-when-time-runs-out.md` — Anytime behavior and fallback solutions when time runs out
- `04-decomposition.md` — Decomposition: Benders and column generation introductions
- `05-testing-optimization-code.md` — Testing optimization code: property tests, objective regression tests and known-answer instances
- `06-explaining-solutions.md` — Explaining solutions: what-if analysis, shadow prices and infeasibility explanations
- `07-deployment-patterns.md` — Deployment patterns: APIs, batch jobs and rolling re-optimization
- `08-human-override-and-planner-workflows.md` — Human override and planner workflows
- `09-monitoring.md` — Monitoring: optimality gaps, input drift and solve-time regressions
- `10-licensing-and-cost.md` — Licensing and cost: open solvers vs commercial solvers and deployment restrictions

**Hands-on projects**

- **Project 1: optimization service with fallbacks**  
  - Data: A routing or scheduling model from earlier modules  
  - Task: Wrap the model in a service with time limits, anytime solutions, fallback heuristics and structured infeasibility messages.  
  - Deliverables: Service and failure-injection tests.  
  - Pass gate: Service returns a valid solution under every injected failure.
- **Project 2: optimization regression test suite**  
  - Data: A model that changes over time  
  - Task: Build tests that detect objective, feasibility and solve-time regressions.  
  - Deliverables: Test suite and CI configuration.  
  - Pass gate: A deliberately worsened model fails the suite.
- **Project 3: licensing and solver selection review**  
  - Data: A candidate production workload  
  - Task: Benchmark open and commercial solvers on your instances and record licence constraints.  
  - Deliverables: Decision memo.  
  - Pass gate: Licence terms read from primary sources and dated.

### 15 — G8 Capstones

**Outcome:** integrate the graph and optimization tracks in assessed, portfolio-quality work.

- **Capstone 1: graph learning system for a real network** (uses Modules 01 to 07)  
  Build a graph learning system on a real network with a schema, leakage-safe splits, classical and neural models, strong baselines, scalability analysis and an honest write-up.
- **Capstone 2: knowledge graph and graph rag application** (uses Modules 01, 05, 07)  
  Build a knowledge graph from documents with quality evaluation and a graph-based question-answering application compared against plain retrieval.
- **Capstone 3: operations optimization platform** (uses Modules 08 to 11, 13, 14)  
  Build an optimization service for a logistics or scheduling problem with uncertainty handling, tests, fallbacks, explanation and monitoring.
- **Capstone 4: predict and optimize decision system** (uses Modules 11, 12, 14)  
  Build a pipeline that predicts inputs and optimizes decisions, compares two-stage and decision-focused training on regret and documents deployment and monitoring.
- **Capstone 5: g8 readiness assessment** (uses All modules)  
  Written and practical assessment against the G8 completion gate.

## G8 completion gate

- Every graph result uses leakage-safe splits (temporal or inductive where appropriate), tuned non-graph baselines and many random splits or repeated runs with intervals.
- Every optimization result verifies feasibility with an independent checker and reports the optimality gap or the gap to best-known solutions.
- Every learned-heuristic or decision-focused result is compared with a strong solver or baseline under an equal time budget and on instances from a different distribution.
- Every model is compared across several datasets or instance families, with failure cases reported.
- All results reproduce from a lockfile, configs and logged seeds, with library, solver and dataset versions and licences recorded.
- Every library and solver used has its licence and maintenance status recorded in the register before it is adopted.
- At least one negative or inconclusive result per track is reported honestly, including a case where a simple baseline beats the sophisticated method.
- The four specialist capstones are complete and the readiness assessment is passed.

## Audit and verification

**What was checked and the result**

- Structure: 14 specialist modules each have 6 to 12 lessons and at least one project; the tree contains 216 files and 31 folders, and these counts equal the counts computed from the curriculum data.
- Overlap with the Roadmap: all 130 lesson file names were compared against every lesson file name in `Roadmap.md`. Exact matches: 0. Near matches (similarity 0.80 or higher): 0.
- Structural problems found by the build script: 0.
- Topic-level overlap check: the Roadmap text was searched for linear programming, simplex, integer programming, MILP, branch and bound, min-cost flow, vehicle routing, OR-Tools, Gurobi, CVXPY, PuLP, metaheuristics, genetic algorithms, simulated annealing, constraint programming, CP-SAT, stochastic and robust optimization, GCN, GraphSAGE, PyTorch Geometric, DGL, knowledge graphs, TransE, community detection, PageRank, Louvain, heterogeneous and temporal graphs, graph transformers and GraphRAG. None appear as lessons, so G8 teaches them for the first time. The first draft of this plan listed Neo4j and Cypher as a lesson; the Roadmap check found an existing Stage 2D lesson on graph databases with Neo4j and Cypher, so that lesson was rewritten to cover only graph-store integration with ML pipelines. The Roadmap also contains Stage 3 knapsack, shortest-path, minimum-spanning-tree, max-flow and bipartite-matching lessons, Stage 4C convex-optimization theory and Stage 5B graph machine learning lessons, which G8 references and extends and does not reteach.
- Verified by web search on the build date (2026-10-26): the Kuzu graph database repository was archived on 10 October 2025 and Apple agreed to acquire the company, so it is not recommended as a new dependency (one forum post claims a community continuation named LadybugDB, which was not verified); the Temporal Graph Benchmark (NeurIPS 2023) provides datasets, loaders and leaderboards and found that simple methods sometimes beat dedicated temporal graph models; HiGHS is reported as MIT-licensed, SCIP as Apache 2.0 since version 8.0.3, OR-Tools and CP-SAT as Apache 2.0, and the pip-installed Gurobi licence as restricted to non-production use with a model-size limit; PyTorch Geometric's newest release found was 2.7.0 from October 2025.
- Reported but not confirmed: the last DGL PyPI release found was 2.2.1 from May 2024 with a reported unpatched pickle-deserialization issue in its RPC component, so check the repository before depending on it; the licence of PyVRP, the terms of the Amazon Last Mile Routing Research Challenge data, the SPO+ method (Elmachtoub and Grigas), the neural routing models of Kool et al. and the MIPLIB, TSPLIB and Solomon instance licences were not confirmed by search; solver licence statements came from a secondary Japanese comparison page and must be read from official licence files before any commercial decision; the maintenance status of NetworkX, igraph, graph-tool, cuGraph, GraphFrames, Pyomo, PuLP, CVXPY, CasADi and CMA-ES packages was not confirmed.
- Not verified: dataset availability and licences (Elliptic, OGB, SNAP, TSPLIB, Solomon, Homberger, MIPLIB, Amazon Last Mile, YelpChi and Amazon fraud graphs); library, solver and benchmark versions, which change quickly; and any commercial solver terms.
- Not verified by execution: no code in this plan has been run. Project pass gates are acceptance criteria to be met when the projects are built.
- Safety note: graph fraud, social-network and bot-detection projects can expose or mislabel real people. Their projects use public benchmark or synthetic data and must not be applied to real accounts or customers without privacy, fairness and legal review.
- Repository safety: this build created only this file; no existing file or folder was created, changed or deleted by it.
