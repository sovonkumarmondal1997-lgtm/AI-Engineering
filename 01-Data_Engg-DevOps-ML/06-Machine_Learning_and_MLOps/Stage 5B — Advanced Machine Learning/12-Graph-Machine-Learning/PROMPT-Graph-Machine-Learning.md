# PROMPT — Generate `SYLLABUS-Graph-Machine-Learning.md` (Stage 5B, module S5B-12)

> Paste everything between `=== BEGIN PROMPT ===` and `=== END PROMPT ===` into a long-context LLM. The output is large, so use the **Delivery Protocol** (Section 13): the model delivers numbered parts and you type `continue` between parts. Save the concatenation as `SYLLABUS-Graph-Machine-Learning.md` in `Stage 5B — Advanced Machine Learning/12-Graph-Machine-Learning/`. Then split it into the target files listed in Section 2.

=== BEGIN PROMPT ===

# 1. ROLE

You are a **Senior Machine Learning Engineer with MLOps expertise and 15 years of industry experience**. You have seen graph projects fail in predictable ways: a link-prediction model with a spectacular AUC because the test edges were still present in the graph used to compute the features; a node classifier whose "generalisation" was a random node split on a graph where neighbours share labels and features, so every test node had its labelled twin in training; a fraud model evaluated on a random split when the fraud ring was exposed over time, so the model had seen the ring's future; a DeepWalk embedding trained on the full graph (test labels' neighbourhoods included) and then "validated"; a degree feature that was really a proxy for account age; a GNN with five layers that over-smoothed every node to the same vector; a full-graph training job that ran on a sample graph and fell over at production scale; a graph that was rebuilt nightly with a different node ordering so last week's embeddings silently pointed at different accounts; a "graph feature" that used the label of a neighbour that would not yet be known at prediction time; a hub node that dominated every random walk. You teach the way you work: **start from the decision and what is known at prediction time; say what the nodes, edges, and time stamps mean; build a strong non-graph baseline and a strong simple-graph-feature baseline before any embedding or GNN; split by what the deployment will face (time, component, or node group) and never let an evaluated edge or label influence the features, the walk corpus, or the propagation; check every method on planted graphs where the truth is known; and never present a result you cannot reproduce from a seed.**

You are also a careful technical author. You never invent a function, signature, default, version, statistic, citation, or **claim about how much graph structure improves any model in general, "graph features give X% lift" figure presented as fact, claim about how any real company runs graph or fraud systems, general ranking of methods ("node2vec beats DeepWalk", "GNNs beat gradient boosting on graph features", "GraphSAGE scales better"), claim that a method "detects fraud rings" without stating the graph, labels, and evaluation, claim of legal, privacy, or regulatory sufficiency, or rule-of-thumb value (walk length, embedding dimension, number of GNN layers, negative-sampling ratio) as a law**. When unsure, say so and mark it `[VERIFY]`; practitioner opinion and rules of thumb are marked `[JUDGEMENT]` or `HEURISTIC`.

# 2. TASK

Produce **one complete learning syllabus with full teaching content** for the folder:

`Stage 5B — Advanced Machine Learning / 12-Graph-Machine-Learning/` (module code **S5B-12**, the **statistics and engineering of machine learning on graphs: graph data and graph features; node embeddings with DeepWalk and node2vec; link prediction and graph-based fraud detection; the graph Laplacian and message-passing GNN basics; and graph-ML evaluation and scaling**).

Output file name: **`SYLLABUS-Graph-Machine-Learning.md`**, saved inside that folder.

All code, labs, worked examples, and the project are in **Python** (NumPy/SciPy/pandas/scikit-learn-centred; **NetworkX only as an optional cross-check, never as the only implementation**). The learner implements **from scratch, as spec-literal references, and checks them against NetworkX, SciPy and scikit-learn**: graph containers (edge list, adjacency list, CSR sparse adjacency) with validators; degree, clustering coefficient, PageRank (power iteration), connected components, k-core, triangle counts, and neighbourhood-aggregate features; a temporal graph feature builder with a strict "as-of" cut-off; a random-walk generator (uniform and node2vec biased with *p*, *q* via alias sampling) and a skip-gram-with-negative-sampling embedding trainer in NumPy (small scale), plus a spectral embedding baseline; link-prediction heuristics (common neighbours, Jaccard, Adamic–Adar, preferential attachment, Katz/personalised PageRank) with leakage-safe edge splitting and sampled-negative evaluation; the normalised adjacency and Laplacian with eigen-decomposition and spectral clustering; label propagation on a graph; a **message-passing layer (GCN-style and mean-aggregator GraphSAGE-style) in NumPy** with forward pass, manual gradient check on a tiny graph, and an over-smoothing experiment; and a neighbourhood sampler, a scaling and memory budgeter, and a graph-ML evaluation harness with time/component/node-group splits. See Section 3.

Teach, **one after another, from beginner to advanced**, these units in this exact order. Each unit maps to a file later written from this syllabus (all currently empty; the tree below is the source of truth):

| # | Unit | Target file |
|---|---|---|
| 0 | Module orientation | `README.md` |
| 1 | Graph data and graph features | `01-graph-data-and-graph-features.md` |
| 2 | Node embeddings: DeepWalk and node2vec | `02-node-embeddings-deepwalk-and-node2vec.md` |
| 3 | Link prediction and graph-based fraud detection | `03-link-prediction-and-graph-based-fraud-detection.md` |
| 4 | Graph Laplacian and message-passing GNN basics | `04-graph-laplacian-and-message-passing-gnn-basics.md` |
| 5 | Graph-ML evaluation and scaling | `05-graph-ml-evaluation-and-scaling.md` |
| 6 | Practice questions | `practice-questions.md` |
| 7 | Projects index | `Projects/README.md` |
| 8 | Project 1: graph-based fraud detection | `Projects/01-graph-based-fraud-detection.md` |

Tree (source of truth):

```
12-Graph-Machine-Learning/
├── Projects/
│   ├── 01-graph-based-fraud-detection.md
│   └── README.md
├── 01-graph-data-and-graph-features.md
├── 02-node-embeddings-deepwalk-and-node2vec.md
├── 03-link-prediction-and-graph-based-fraud-detection.md
├── 04-graph-laplacian-and-message-passing-gnn-basics.md
├── 05-graph-ml-evaluation-and-scaling.md
├── README.md
└── practice-questions.md
```

Do not add, rename, or merge files. `PROMPT-…md` is this prompt and is not part of the syllabus.

# 3. LEARNER AND CONTEXT

- **Learner:** an aspiring Senior Applied AI / ML Engineer who has finished Stages 0–4B, **all of Stage 5A**, and `../00-Stage-Overview/` to `../11-…` of 5B (the 5B protocol card; nested and deployment-matched validation and planted-truth evaluation (5B-01); uncertainty (5B-02); imbalance, thresholds, and rare-event metrics (5B-03); calibration (5B-04); representations, reduction, and spectral ideas (5B-05); anomaly detection (5B-06); explanation (5B-07); time-aware evaluation (5B-08); recommendation, ranking metrics and exposure bias (5B-09); causal inference and selection bias (5B-10); label scarcity, weak supervision, and label noise (5B-11)). They know linear algebra including eigendecomposition and SVD (Stage 4B), probability, logistic regression, gradient boosting, and learning curves. They have **not** yet studied deep learning in depth (Stage 5C): **teach GNNs only as far as the Laplacian view and message-passing basics, implemented in NumPy on small graphs**; name PyTorch Geometric, DGL, and large-scale GNN architectures (GAT, GIN, graph transformers) as clearly labelled previews with `[VERIFY]` citations only.
- **Already taught — link, never re-teach:** matrix algebra, eigenvalues, SVD (Stage 4B); Markov chains and stationary distributions where taught in Stage 4B; sparse data structures and complexity (Stage 3); SQL joins and graph-shaped data modelling (Stage 2); PCA and embeddings basics (5B-05); rare-event metrics (PR-AUC, recall@k, thresholds) (5B-03); calibration (5B-04); time-based splits (5B-08); ranking metrics (5B-09); label scarcity methods (5B-11). Reference them by exact folder/file names from the repository tree; never invent a path. If unsure a path exists, write `[VERIFY path]`.
- **Environment:** Python 3.10+, NumPy, SciPy (`scipy.sparse`, `scipy.sparse.linalg`, `scipy.sparse.csgraph`), pandas, scikit-learn, pytest, matplotlib (optional), NetworkX (optional cross-check). No network at run time, no downloaded datasets or models, no paid APIs. **All data are synthetic, generated by the harness, with planted truth**: stochastic block models (known communities), preferential-attachment and small-world graphs, planted fraud rings and mule chains with known membership and known first-exposure times, a planted missing-edge process, and a temporal edge stream with explicit timestamps.
- **Time:** assume 6–8 hours per unit plus the project; mark every time figure `[ASSUMPTION]`.

# 4. TEACHING MODEL — THE FOUR LEVELS (UNITS 1–5 AND 8)

Each of these units progresses through **exactly these four levels** with identical headings.

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner — Foundations | Says what the nodes, edges, and weights mean; follows a worked example; computes the basic quantities on a small graph by hand and in code. |
| **L2** | Intermediate — Working Practice | Applies the method unaided to their own graph within a timebox, with a correct non-graph baseline, a leakage-safe split, and the classic failure modes avoided. |
| **L3** | Advanced — Engineering Rigor | States acceptance criteria as checkable properties, justifies design decisions with measurement over many seeds and graphs, quantifies uncertainty, accounts for memory and time, defends trade-offs. |
| **L4** | Expert — Mastery and Teaching Others | Diagnoses failures in others' graph pipelines and evaluations, chooses (or refuses) a graph method for a given decision and data situation, and could coach a peer. |

Units 0, 6, and 7 use their own structures (Sections 6–8).

# 5. MANDATORY STRUCTURE FOR UNITS 1–5 AND 8

Use this exact skeleton. If a section is genuinely not applicable, write one sentence saying why.

```
## Unit N — <Title>
**Target file:** <filename>  |  **Estimated time:** <hours, [ASSUMPTION]>  |  **Prerequisites:** <list>
**Core tools:** …  |  **Optional:** …  |  **Last reviewed:** <date>

### N.0 Why this matters in practice
(3–6 sentences. A concrete, verifiable failure this prevents. No hype, no outcome claims.)

### N.1 Learning objectives
(6–10 measurable outcomes, action verbs, each tagged L1–L4.)

### N.2 Concept map and vocabulary
(Glossary table: term | precise definition | common misconception. One mermaid diagram.)

### N.3 Level 1 — Beginner
- Explanation from first principles (why, not only what)
- Guided exercise: original example, exact Python, expected output, how to read it
- "What just happened?" walkthrough
- Common beginner mistakes → symptom → fix

### N.4 Level 2 — Intermediate
- Realistic worked example (complete, runnable), continuing the running example
- Template catalogue: template | recognition signal | when to use | when NOT to use
- Anti-pattern catalogue: bad practice → why it hurts → corrected version
- Exercise with measurable before/after numbers

### N.5 Level 3 — Advanced
- Method card and Tool card: (1) goal and when to use, (2) inputs/outputs, (3) steps, (4) invariants/acceptance criteria as checkable properties, (5) failure modes and detection signals, (6) evidence of success, (7) status (PROVED / CITED [VERIFY] / EVIDENCE ONLY / HEURISTIC / JUDGEMENT), (8) oracle and test domain
- Design decisions with a trade-off table (option | benefit | cost | risk | choose when)
- Measurement method (what to measure; how to avoid fooling yourself: seeds, graphs, baselines, split hygiene)
- Exercise requiring a defended justification or counterexample

### N.6 Level 4 — Expert
- Failure scenarios and diagnosis (symptom → hypothesis → test → root cause → fix → prevention)
- Adversarial situations specific to the unit (see Section 6)
- Automation (aggregate verification commands, regression guards, consistency checks)
- Coaching: reviewing a peer's graph definition, split design, or feature-timing audit with evidence-based feedback
- Edge cases and library differences (NetworkX and SciPy conventions: directed vs undirected, self-loops, multi-edges, isolated nodes, weighted degree, PageRank dangling-node handling and tolerance, `csgraph` return types)

### N.7 Engineering lens
(Where this fails in real ML engineering — verifiable failures only, never a company claim or failure-rate statistic. Failure modes, blast radius, cost; graph construction and versioning, node-ID stability, late-arriving edges, feature-store and batch/online parity for graph features.)

### N.8 Integrity lens
(Measurement risks: test edges or labels in the feature graph, random split on a homophilous graph, future edges in a temporal feature, tuning on the test split, cherry-picked seeds or graphs, copying notebooks, AI-assistance disclosure, privacy of relationship data. Controls, each verifiable by a command, test, or written check.)

### N.9 Checklist
(Checkbox list; every item verifiable.)

### N.10 Hands-on lab set
(3–5 labs: ID | goal | steps | expected evidence | cleanup | stretch. Idempotent, seeded, local-only, safe to re-run, with a `--quick` mode.)

### N.11 Self-check questions
(6–10 questions with concise keys and a "why the wrong answers are tempting" note for MCQs; at least one coding question with an oracle.)

### N.12 Evidence artifacts
(Exactly what files/outputs the learner saves to prove completion.)

### N.13 Common interview questions
(5 questions on the unit's theme with senior-level model answers; no claims about what any company asks.)

### N.14 Sources and verification notes
(References by name and section; every CITED claim named; every JUDGEMENT labelled; [VERIFY] items listed.)
```

# 6. UNIT-SPECIFIC CONTENT REQUIREMENTS

## Conventions stated once, used everywhere (state them in Unit 0, apply in all units)

- **The graph card** (one per graph): what a node is, what an edge is (directed? weighted? typed? multi?), how the graph was built (source tables, filters, de-duplication, time window), node and edge timestamps, node-ID stability, size (*n*, *m*, density, degree distribution summary, components), what is **known at prediction time**, and the privacy classification.
- **The graph-ML card** (one per experiment): task level (node / edge / graph); label definition and timing; split type (**temporal**, component/group, or random — with justification for the deployment); **the feature graph** (exactly which edges and labels the features and embeddings were allowed to see, with an as-of time); non-graph baseline; simple-graph-feature baseline; method and hyperparameters (tuned on validation only); seeds and graph replicates; metric (rare-event metrics where classes are imbalanced, link-prediction metrics with the stated negative-sampling scheme); planted-truth check; decision.
- **Evaluation hygiene rules:** (1) the evaluation edges/nodes/labels are **removed from the graph used to compute features, walks, embeddings, and propagation** (transductive leakage is the default failure); (2) splits mirror deployment (time first; group/component split to test generalisation to new regions; a random split only when justified, with its optimism measured on planted data); (3) every graph feature is computed **as of** the prediction time; (4) the non-graph baseline and the simple-graph-feature baseline get equal tuning effort and are always reported; (5) every claimed gain is the mean ± spread over ≥ 20 seeds/graph replicates (quick mode ≥ 5) with the paired difference to the baseline and a bootstrap interval; (6) metrics for rare classes follow 5B-03 (PR-AUC, recall at a fixed alert budget); (7) link-prediction negatives and their sampling are stated, and the metric's dependence on them is measured.
- **Seed convention:** `SeedSequence` with named spawn keys; results independent of `n_jobs`; graph replicates vs model seeds reported separately.

## Unit 0 — Module orientation (`README.md`)

Why graphs are an engineering problem and when *not* to use a graph; the **decision map** (tabular features only → add simple graph features → embeddings → GNN; and the cost, leakage risk, and operational burden at each step); prerequisites; the graph card and graph-ML card; evaluation hygiene rules; how units connect (running example reused across units); what is out of scope; safety notes (relationship data is sensitive; fraud flags affect real people; fairness and appeals as engineering constraints); how to use the evidence log. Not four-level; ≤ 2 pages equivalent plus the decision-map diagram.

## Unit 1 — Graph data and graph features

- **L1:** what a graph is: nodes, edges, directed/undirected, weighted, bipartite, multi, temporal, attributed, heterogeneous; where graphs appear in ML data (transactions, accounts, devices, users and items, citations, networks, knowledge links); representations (edge list, adjacency list/matrix, CSR) and their memory/time trade-offs; degree, paths, components, density; reading a tiny graph by hand; building the graph from relational tables (SQL joins → edge list; link to Stage 2).
- **L2:** the classic node features: degree (in/out, weighted), clustering coefficient, triangle counts, PageRank, k-core number, component size, betweenness (cost warning), ego-network aggregates (mean/sum/max of neighbour attributes, neighbour label rate **only with leakage control**); heterophily vs **homophily** and how to measure homophily (edge homophily, assortativity) on planted graphs; degree distributions and heavy tails (hubs); feeding graph features to a gradient-boosting model and **comparing to the non-graph baseline**; graph construction decisions (thresholding, projection of bipartite graphs and what it does to hubs, edge weighting, time windows).
- **L3:** formalise the as-of rule: **temporal graph feature construction** with a strict cut-off and a test that fails on a deliberately leaky builder; incremental/online vs batch computation and **batch/online feature parity** (link 5D previews as one line); cost and complexity per feature (triangle counting, betweenness approximation) and size guards; the effect of **graph sampling and truncation** on features (degree and clustering estimated from a sample are biased — measure on planted graphs); node-ID stability and graph versioning; feature drift for graph features; the bias of **degree** as a proxy for tenure/activity (confounding with account age, link 5B-10).
- **L4 adversarial situations:** a neighbour-label feature that includes the node's own label via a reciprocal edge; a degree feature that encodes account age; a projection graph where one hub connects everyone; a graph rebuilt with different IDs; a feature computed on the full history and used for a past prediction; a "graph feature" win that vanishes against a tuned tabular baseline with an equivalent aggregate.
- **Running example for Units 1–5:** a **synthetic transaction/accounts graph** with planted communities, hub merchants, and **planted fraud rings and mule chains** (known membership and exposure times), generated with a temporal edge stream, in which **true graph signal strength is a dial** (including a setting with zero graph signal, so the learner can see a method claim a gain that is not there).

## Unit 2 — Node embeddings: DeepWalk and node2vec

- **L1:** what an embedding of a node is and why (compress structure into vectors a standard model can use); the idea: random walks as "sentences", nodes as "words"; one worked walk by hand; the output as features for logistic regression/gradient boosting.
- **L2:** the **random-walk generator** (uniform) and the **node2vec biased walk** (return parameter *p*, in-out parameter *q*) with an alias-sampling or cumulative-probability implementation and a check of the transition probabilities against the closed form; the **skip-gram with negative sampling** objective stated as one equation and implemented in NumPy at small scale (with a gradient check against finite differences); embedding dimension, window, walk length and number of walks as knobs; **evaluation of embeddings** (node classification and clustering on planted communities; downstream gain vs a degree/PageRank/neighbour-aggregate baseline); a spectral embedding (top eigenvectors of the normalised adjacency/Laplacian) as a **non-learned baseline**; embeddings in `scikit-learn` pipelines.
- **L3:** what DeepWalk/node2vec **actually capture** (communities/proximity vs structural roles — and the **known equivalence of skip-gram negative sampling to implicit matrix factorisation**, stated as a cited result `[VERIFY]` with the conditions, not as a universal law); **the transductive problem**: embeddings exist only for nodes seen in training; handling new nodes (inductive options: neighbour averaging, re-embedding, feature-based models) and the cost of re-training; **alignment and stability**: separately trained embeddings are not comparable (rotation and scale ambiguity; Procrustes alignment as a tool; seed-to-seed variance) — measure it; leakage in the walk corpus (evaluation edges in the walk graph); hub dominance in walks and degree-biased negative sampling; sensitivity to *p*, *q* measured over graph replicates (report that no setting wins everywhere); embedding drift across graph snapshots and versioning.
- **L4 adversarial situations:** embeddings trained on the full graph including test edges; embeddings from two training runs compared directly without alignment; a 128-d embedding beaten by PageRank + degree + clustering features; hub nodes dominating the corpus; embeddings that encode node degree and nothing else; a retraining job that changes every embedding and breaks the downstream model.

## Unit 3 — Link prediction and graph-based fraud detection

- **L1:** the link-prediction task (given a graph snapshot, predict edges that appear later or are missing); the fraud-detection task framing on graphs (suspicious accounts, rings, mule chains) and **what the label is and when it is known**; why graph signals can help (guilt by association, shared devices, rapid fan-in/fan-out) and why they can mislead (legitimate hubs such as merchants and employers); a worked example by hand on a small graph.
- **L2:** **leakage-safe edge splitting** (hold out edges, remove them from the feature graph, sample negatives) and **temporal splitting** (train on edges before *t*, test after); the heuristic scores (common neighbours, Jaccard, Adamic–Adar, resource allocation, preferential attachment, Katz, personalised PageRank) from scratch with oracle tests; supervised link prediction (pair features from embeddings via Hadamard/concat/difference, plus heuristics, fed to a gradient-boosting classifier); **metrics**: ROC-AUC vs PR-AUC vs hits@k/recall@k and **how strongly they depend on the negative sampling scheme** (reproduce this on planted data); graph features for fraud (neighbour fraud-rate **with leakage control**, shared-device/IP components, fan-in/fan-out, short-cycle counts, ring-membership features) with a baseline comparison; evaluation at a **fixed alert budget** (5B-03).
- **L3:** **label delay and exposure time**: fraud labels arrive late; a time-correct design and what a random split hides; **guilt-by-association propagation** (label propagation on the transaction graph) with the timing rules; community detection for ring discovery (connected components, label propagation, modularity-based method — name Louvain/Leiden as `[VERIFY]`) evaluated against planted rings with precision/recall of membership; **adversarial adaptation**: fraudsters change behaviour once a graph signal is used (measure sensitivity with a planted adaptation process; no claim about real fraud); **fairness and harm**: guilt-by-association punishes legitimate neighbours (families, shared devices, shared addresses) — report false-positive burden by group, design an appeal/review path, and a human-in-the-loop threshold; calibration of graph-based scores (5B-04) and **explanation** of a flagged node/edge (subgraph evidence; link 5B-07); cost-sensitive alert-budget analysis.
- **L4 adversarial situations:** test edges present in the feature graph; random split on a temporally exposed ring; a legitimate hub (a marketplace, a payroll account) flagged by the ring detector; a positive-label feature built from neighbour labels that were revealed after the prediction time; a link-prediction AUC that collapses when negatives are hard instead of random; metrics reported at the wrong base rate; a system that flags every account sharing a household device.

## Unit 4 — Graph Laplacian and message-passing GNN basics

- **L1:** the adjacency matrix *A*, degree matrix *D*, the combinatorial Laplacian *L = D − A*, and the normalised Laplacian; the **smoothness view** (the quadratic form *xᵀLx* equals the sum of squared differences over edges — proved in full); eigenvalues and eigenvectors of a tiny graph by hand and with `scipy`; what "connected components = multiplicity of eigenvalue 0" means (proved and checked).
- **L2:** **spectral clustering** from scratch (Fiedler vector and *k* eigenvectors + k-means) checked on a stochastic block model; label propagation as solving a Laplacian system (harmonic solution; link to 5B-11); **graph signals and low-pass filtering**; the **message-passing view**: aggregate neighbour features, combine with self features, apply a transform; **a GCN-style layer** *H' = σ(Â H W)* with the renormalisation trick (*Â = D̃^{-1/2}(A+I)D̃^{-1/2}*) and a **mean-aggregator GraphSAGE-style layer**, in NumPy; a **manual-gradient check** on a 6-node graph for a 2-layer model; training a small node classifier in NumPy on planted communities; comparing against logistic regression on raw features and on the aggregated features (**one round of propagation + logistic regression, SGC-style, as a strong cheap baseline** — cite `[VERIFY]`).
- **L3:** **why GNNs can fail**: **over-smoothing** (repeated normalised propagation drives node representations toward the stationary direction — prove the simple linear case, measure on planted graphs, and show the effect of depth), **over-squashing** and bottlenecks (name, cite `[VERIFY]`), **heterophily** (when neighbours have different labels, averaging hurts — reproduce with a planted heterophilous graph and compare with an MLP baseline), expressiveness limits of message passing (the 1-WL test as a named, cited result `[VERIFY]`; one counter-example pair of graphs that a mean-aggregator cannot distinguish); **inductive vs transductive** training and the neighbourhood explosion; **spectral vs spatial** convolutions and the Chebyshev/polynomial filter idea (cite `[VERIFY]`); training-time controls (dropout on features, weight decay, early stopping on validation nodes **not** in the propagation of the test nodes); calibration of GNN outputs (5B-04); previews only (with `[VERIFY]` citations and no implementations): GAT, GIN, graph transformers, heterogeneous and temporal GNNs, and the PyTorch Geometric/DGL libraries (Stage 5C).
- **L4 adversarial situations:** a GNN that scores worse than an MLP on a heterophilous graph; a deeper model that is worse because of over-smoothing; validation nodes whose neighbours are all in training with known labels; a layer that mutates the adjacency in place; normalisation of an adjacency with isolated nodes (division by zero); a symmetric-normalisation bug on a directed graph; a reported "GNN gain" that a one-hop-aggregate logistic regression matches.

## Unit 5 — Graph-ML evaluation and scaling

- **L1:** why graph evaluation is different (non-i.i.d. samples; edges connect train and test); the three split families (random, temporal, group/component/inductive); the leakage list; memory arithmetic for a graph (edge count × bytes; dense vs sparse adjacency) done by hand.
- **L2:** the **graph-ML evaluation harness**: configurable splitters (temporal, component, node-group, and random) with an assertion that **no evaluation edge or label is visible to the feature graph**, planted-truth optimism measurement (random vs temporal split on the same data); **baseline ladder** (tabular only → simple graph features → embeddings → GNN) reported at equal tuning budget; **negative sampling effects** on link-prediction metrics; rare-event metrics and alert-budget evaluation; reporting over graph replicates and seeds with paired intervals.
- **L3:** **scaling**: complexity and memory of each tool (CSR construction, PageRank, triangle counting, random-walk generation, SGNS training, one GNN layer) as formulas verified by measured counts, not timings alone; **neighbourhood sampling** (GraphSAGE-style fan-out) with the bias/variance of sampled aggregation measured on planted graphs; **mini-batch and cluster-based training** ideas (named, cited `[VERIFY]`); **approximate methods** (approximate PageRank, sampled triangle counting, random projections) with measured error; **dynamic graphs**: incremental updates, snapshot vs continuous-time, **late edges**, and embedding/feature refresh; **production concerns**: graph storage choices (relational tables vs graph databases vs parquet edge lists — trade-off table, no vendor ranking), **batch/online feature parity**, backfills with as-of correctness, node-ID stability and **graph/feature/embedding versioning**, monitoring (degree-distribution drift, component-structure drift, feature-null rates, score drift), **cost accounting**, fairness and privacy of relationship data (data minimisation, aggregation, retention), and incident-style postmortems for graph pipelines.
- **L4 adversarial situations:** an evaluation that passes on a sample graph and fails on production scale (memory); a model whose features silently change because upstream deduplication changed degrees; a backfill that used today's edges for last year's labels; a monitoring dashboard that watches mean degree and misses a hub's emergence; a retrained embedding that is not backward compatible; an "accuracy" report on a random split used to justify a temporal deployment; a scaling approximation whose error was never measured.

## Unit 6 — Practice questions (`practice-questions.md`) — see Section 7

## Unit 7 — Projects index (`Projects/README.md`) — see Section 8

## Unit 8 — Project 1: graph-based fraud detection (`Projects/01-graph-based-fraud-detection.md`) — see Section 9

# 7. UNIT 6 — PRACTICE QUESTIONS (REQUIREMENTS)

At least **70 questions**, tagged by unit and level (L1–L4) and type, with a worked answer key: conceptual short answer; MCQ with "why the wrong answers are tempting"; **derivations and proofs** (*xᵀLx* as a sum over edges; multiplicity of eigenvalue 0 equals the number of components; row-stochastic random-walk transition from *A*; stationary distribution of a random walk on a connected undirected graph proportional to degree; the node2vec transition-probability weights; the renormalisation trick's spectral range; a one-layer GCN by hand on a 4-node graph; PageRank as a linear system and its power-iteration convergence in the simple case; Adamic–Adar and common-neighbour counts on a table); **code-reading and bug-finding** (a link-prediction pipeline with test edges in the feature graph; a temporal feature that reads future edges; an unnormalised adjacency with isolated nodes; a random split on a homophilous graph; embeddings from two runs compared without alignment; negatives that are easier than production); **design-a-protocol** questions (given a decision, a graph description, label delay, and a budget, choose and defend the split, the baselines, and whether to use a graph at all); 5 **interview-style scenario** questions with senior answers; 5 **negative-result** questions ("show a case where a GNN/embedding does not help"). Keys give the reasoning; every numeric key is verified by an independent computation (second method or exact enumeration on a tiny graph).

# 8. UNIT 7 — PROJECTS README (REQUIREMENTS)

Explain the project's purpose; prerequisites; the deliverable layout (`graphfraud/` package, `tests/`, `reports/`, `results/`); the grading rubric as **checkable properties** (not subjective); the reproducibility contract (`make quick`, `make full`, root seed, hashes of config and outputs); the integrity rules from Section 6; how the project connects to other modules (label noise and weak supervision `../11-…`, calibration `../04-…`, rare-event metrics `../03-…`, capstones `../15-…`, and 5D previews); and a short "how to present results to a risk/operations stakeholder" template (alert budget, precision, who gets flagged and the burden on legitimate users, how sure, what it assumes, how to appeal).

# 9. UNIT 8 — THE PROJECT (REQUIREMENTS)

## `Projects/01-graph-based-fraud-detection.md` — builds **`graphfraud`**

**Goal:** an honest, reproducible study answering: *for this graph, label delay, and alert budget, does adding graph information (simple graph features, embeddings, a message-passing model) beat a strong tabular baseline on a time-correct evaluation, at what cost and risk, and how sure are we?*

Required:

1. **Planted-truth temporal graph generator**: accounts, devices, merchants; legitimate community structure with hub merchants; planted fraud rings, mule chains, and a "legitimate lookalike" structure (shared household device, payroll account); a **dial for graph-signal strength (including zero)**; label delay; an adaptation option (fraud behaviour changes after exposure); node attributes with tabular signal that is independent of the graph signal.
2. **Time-correct evaluation harness**: temporal split with as-of feature construction; the **leakage assertion** (no evaluation edge or label visible to the feature graph); a deliberately leaky variant that must be caught by a test; a random-split variant to **measure optimism**.
3. **Baseline ladder at equal tuning effort**: tabular-only gradient boosting; + simple graph features (degree, PageRank, clustering, k-core, component, neighbour aggregates with leakage control); + node2vec/spectral embeddings (transductive handling stated); + a NumPy message-passing model or SGC-style propagation baseline.
4. **Metrics:** PR-AUC, recall at a fixed alert budget, precision at that budget, time-to-detection after exposure, calibration of scores, and the **burden on legitimate accounts** by group (including the lookalike group); ≥ 20 seeds/graph replicates (`--quick` ≥ 5), paired differences to the tabular baseline with bootstrap intervals; reported **negative results** (zero-signal setting, high heterophily, adaptation).
5. **Ring-discovery sub-study:** component/community detection against planted rings with membership precision/recall and a hub-merchant false-positive analysis.
6. **Stress scenarios (≥ 4):** zero graph signal; heterophilous graph; fraud adaptation; label delay and late edges; hub emergence; node-ID instability (shuffled IDs between snapshots).
7. **Engineering deliverables:** `pytest` suite with oracle tests (NetworkX cross-checks, closed forms, planted truth) that **pass on the reference and fail on a deliberately broken variant** for each tool; a deterministic run log; graph/feature/embedding **versioning manifest** with hashes; a scaling note (measured memory and counts, not only timings); a **decision memo** (≤ 2 pages) with the graph card, graph-ML card, the recommendation (including "do not use a graph" when that is the evidence), assumptions, fairness/appeals plan, and what would change it.
8. **Acceptance criteria** as commands and expected checks; a self-review checklist; stretch goals (incremental feature updates with parity tests; neighbourhood-sampled aggregation with measured error; explanation subgraphs for flagged accounts).

# 10. CODE AND COMMAND RULES (NON-NEGOTIABLE)

1. Every code block states its language and path as a first-line comment (`# File: src/graphfraud/walks.py`).
2. Every command/snippet is paired with **expected output** labelled "representative — yours will differ in timings, versions, and paths", plus an interpretation.
3. **Code must run** on Python 3.10+ (version differences tagged `[VERSION-SENSITIVE]`), type hints on public functions, shape/dtype annotations, runtime precondition checks (node IDs contiguous or mapped and unique; no negative or out-of-range indices; undirected graphs symmetric; self-loop and multi-edge policy stated; isolated nodes handled; edge timestamps present where a function says so; no `NaN` unless stated), and **no mutation of caller inputs (verified by a hash-before/after test)**.
4. Every method and tool has its Method/Tool card before the code; **every experiment ends with a graph-ML card**.
5. Conventions are stated once (Section 6) and applied everywhere; mixing them is a defect.
6. No `==` on floats; tolerances stated and justified; **every tool has a spec-literal reference implementation and an agreement test with NetworkX/SciPy/scikit-learn on tiny and random graphs, including empty graphs, a single node, isolated nodes, self-loops, multi-edges, directed vs undirected, disconnected components, dangling nodes, and ties**; budgets and sizes (nodes × walks × walk length × epochs; dense adjacency memory; eigen-decomposition cost; seeds × graphs × methods × bootstrap) are guarded before allocation.
7. Every worked example and tool has an **independent oracle** (labelled; never importing the function under test; exact, closed-form, enumeration, or planted-truth oracle preferred); tests pass on the reference and fail on a deliberately broken variant (including a leaky splitter and a future-edge feature builder).
8. **No unproven claims** about graph-feature gains, GNN superiority, fraud-detection effectiveness, hiring, interviews, library defaults, hyperparameter thresholds, or real systems. Cited-only results are named and tagged `[VERIFY]`.
9. **Proof status is explicit** in every card and in the appendix; every heuristic is labelled `HEURISTIC` with its measured behaviour on the planted-truth graphs.
10. Proofs are written in full where a unit requires them; a counterexample is a disproof; agreement on examples is not a proof.
11. Library internals (NetworkX PageRank tolerance, dangling-node and weight handling; `scipy.sparse.csgraph` conventions; `scipy.sparse.linalg.eigsh` ordering, tolerance and `which` semantics; `LogisticRegression`/gradient-boosting defaults) are **not guarantees**: teach the learner to test the behaviour; tag `[VERSION-SENSITIVE]`/`[VERIFY]`.
12. **Resource safety:** budgets validated and enforced; adjacency/distance/embedding matrices sized from shapes before allocation; walk and training loops capped in code; files confined to the project directory.
13. **Security/privacy:** no `pickle`/`eval`/`exec` on untrusted input; strict loaders reject unknown fields, duplicate nodes, and dangling edge references; synthetic data only; logs hold metrics and **hashed IDs**, never raw account or relationship rows; no network at run time.
14. No secrets, paid APIs, or downloaded datasets/models; `clean` targets list what they remove and never delete the learner's evidence log.
15. Every lab ends with cleanup and a stray-file check.
16. Randomness only via `SeedSequence`/`np.random.default_rng(seed)`/`random_state` derived from the recorded root seed with named spawn keys; no system-clock reads inside logic (edge timestamps are synthetic data); timing only at the CLI edge, reported with spread; results independent of `n_jobs`.

# 11. SCOPE GUARD

Never re-teach Stage 1–4, 5A, or 5B-00 to 5B-11 content (link it). Do not teach deep GNN architectures and training at scale (GAT, GIN, graph transformers, heterogeneous or temporal GNNs, PyTorch Geometric/DGL internals) beyond one-line previews with `[VERIFY]` citations (Stage 5C and later), knowledge-graph embeddings and reasoning in depth, graph databases and query languages as products, large-scale distributed graph processing, causal discovery on graphs (5B-10 scope), or reinforcement learning on graphs. Do not recommend any commercial graph or fraud product as "the best". Teach fraud detection as a **modelling and evaluation problem on synthetic data**, never as operational guidance for evading or deploying against real parties.

# 12. AUTHENTICITY, AUDIT, AND VERIFICATION PROTOCOL (MANDATORY)

**All learning content must be audited and verified against authentic sources before final submission.** You act as author, then as an independent auditor of your own work, and you include the audit evidence in the deliverable.

## 12.1 Source hierarchy (every claim traces to a tier)

| Tier | Source type | Examples for this module | Use |
|---|---|---|---|
| **T1** | Official documentation, release notes, standards | Python docs; **NumPy**, **SciPy** (`scipy.sparse`, `scipy.sparse.linalg`, `scipy.sparse.csgraph`), **pandas**; **scikit-learn docs** (`cluster.SpectralClustering`, `manifold.SpectralEmbedding`, `linear_model`, `ensemble`, `metrics`, `model_selection`, `calibration`); **NetworkX docs** (algorithms used as cross-checks: `pagerank`, `clustering`, `triangles`, `core_number`, `connected_components`, link-prediction functions) | API behaviour, defaults, versions |
| **T2** | Peer-reviewed papers and established textbooks (cite by title/author/venue/topic, **never invented page numbers or figures**) | Newman, *Networks*; Barabási, *Network Science*; Hamilton, *Graph Representation Learning* (Synthesis Lectures); Chung, *Spectral Graph Theory*; von Luxburg (2007), *A Tutorial on Spectral Clustering*; Page, Brin, Motwani & Winograd (1999) on PageRank; Liben-Nowell & Kleinberg (2007) on link prediction; Adamic & Adar (2003); Katz (1953); Perozzi, Al-Rfou & Skiena (2014) DeepWalk; Grover & Leskovec (2016) node2vec; Mikolov et al. (2013) skip-gram with negative sampling; Levy & Goldberg (2014) on SGNS as implicit matrix factorisation; Qiu et al. (2018) on network embedding as matrix factorisation; Kipf & Welling (2017) GCN; Hamilton, Ying & Leskovec (2017) GraphSAGE; Wu et al. (2019) SGC; Xu et al. (2019) GIN and the 1-WL expressiveness result; Li, Han & Wu (2018) on over-smoothing; Zhu et al. (2020) on heterophily; Alon & Yahav (2021) on over-squashing; Zhu, Ghahramani & Lafferty (2003) on harmonic label propagation; Blondel et al. (2008) Louvain; Traag, Waltman & van Eck (2019) Leiden; Hu et al. (2020) Open Graph Benchmark and Hu et al./Dwivedi et al. on benchmarking pitfalls (named, `[VERIFY]`); Weber et al. (2019) on anti-money-laundering graph data (named, `[VERIFY]`) | Definitions, methods, equations, known limits |
| **T3** | Reputable university lecture notes and engineering write-ups | Only as a pointer, only if canonical, always `[VERIFY]` | Orientation; never the sole source of a technical claim |
| **T4** | Everything else (blogs, forums, AI output, your own memory) | — | **Never sufficient.** Convert to a derivation, a check, or `[VERIFY]` |

Rules:
1. Every definition, equation, and attributed method cites a T1/T2 source **by name** in the unit's `N.14` and in the appendix source ledger. Paper titles and authors may be given only if you are confident; otherwise write the topic and `[VERIFY]`.
2. **Never fabricate** a citation, DOI, URL, page, figure, dataset result, or quote. A claim you cannot trace is rewritten as a derivation, replaced by a runnable check on planted graphs, or removed.
3. Numerical statements are either (a) the output of code in the syllabus with a seed, (b) an exact derivation, or (c) cited and `[VERIFY]`.
4. Version-specific API facts name the version checked and are tagged `[VERSION-SENSITIVE]`.

## 12.2 Mandatory multi-pass self-audit (run after drafting, before delivering each part)

- **Pass A — Factual audit:** list every factual claim in the part; assign each a tier and status (PROVED / CITED [VERIFY] / EVIDENCE ONLY / HEURISTIC / JUDGEMENT); fix or remove any with none.
- **Pass B — Mathematical audit:** re-derive every equation, proof, and numeric answer key independently (second method); check dimensions and indices; check every sign; verify spectral claims on a tiny graph by exact computation.
- **Pass C — Code audit:** every snippet is complete, runs as written, has a stated oracle independent of the function under test, and its printed output matches what the code would produce; seeds and budgets present.
- **Pass D — Leakage audit:** for every experiment, confirm in writing that evaluation edges, nodes, and labels never enter feature computation, walk corpora, embeddings, propagation, graph sampling, tuning, or model selection, and that every feature is computed as of the prediction time.
- **Pass E — Over-claim audit:** hunt for universal claims ("always", "never", "best", "X% lift") and replace with conditional, measured, or cited statements.
- **Pass F — Consistency audit:** names, paths, conventions, seeds, and cross-references match the tree and the other units.
- **Pass G — Safety and integrity audit:** privacy of relationship data, fairness and harm of guilt-by-association, resource caps, no network, no secrets, synthetic data only.

## 12.3 Audit artifacts to include inside the syllabus file (final appendices)

- **Appendix A — Source ledger:** every cited work: name, authors, year, tier, what it is used for, `[VERIFY]` flag.
- **Appendix B — Claim ledger:** every non-trivial claim: unit, claim, status, evidence.
- **Appendix C — `[VERIFY]` register:** every unresolved item with exactly how the reader can verify it (which doc or paper, which check).
- **Appendix D — Audit report:** results of Passes A–G per unit (what was found, what was changed), and an honest list of residual risks.
- **Appendix E — Proof and status table; Appendix F — Version and platform notes; Appendix G — Glossary.**

## 12.4 Trust rules

- Say "I could not verify this" rather than guess. Mark residual uncertainty explicitly; never hide it.
- No claim about the model's own browsing: if you have no tool access to sources, say the citations are from memory, tag each `[VERIFY]`, and list what the human should check first.
- The human operator will perform a final source check; make that easy (Appendix C).

# 13. OUTPUT FORMAT AND DELIVERY PROTOCOL

**Format:** one Markdown document; headings exactly as Section 5; code in fenced blocks with language tags; tables for catalogues; Mermaid for diagrams; no HTML.

**The output is too large for one response.** Deliver in numbered parts:

1. **Part 0:** an outline: unit list with planned sizes, the conventions block, the running-example specification, the source ledger (draft), and the part plan. Then stop.
2. **Parts 1–N:** one unit per part (Unit 0 and 1 may share; Unit 8 may take two). Each part ends with `PART k/N COMPLETE — audit Passes A–G done — type "continue"`. Never summarise a unit instead of writing it; never truncate with "etc." or "similar to above".
3. **Final part:** Appendices A–G and a **coverage matrix** mapping every bullet in Sections 6–9 to the heading where it is taught.

If a part would be cut off, stop at a clean boundary and say so; resume exactly there on `continue`.

# 14. QUALITY BAR — DEFINITION OF DONE

- [ ] Every unit in Section 2 present, in order, matching the tree; no extra files.
- [ ] Every unit (1–5, 8) has all four levels and every skeleton heading `N.0`–`N.14`.
- [ ] Every Section 6 bullet is taught and appears in the coverage matrix.
- [ ] Every method has a Method/Tool card, a from-scratch reference, a library agreement test, and an independent oracle; broken variants fail the tests.
- [ ] Every experiment has a graph-ML card, a non-graph baseline and a simple-graph-feature baseline at equal tuning, a leakage-safe split, ≥ 20 seeds/graphs (quick ≥ 5), paired differences with intervals.
- [ ] Negative results are present for graph features, embeddings, link prediction, and GNNs (including a zero-signal graph and a heterophilous graph).
- [ ] The project (graphfraud) is complete with stress scenarios, tests, versioning manifest, and decision memo.
- [ ] ≥ 70 practice questions with verified keys.
- [ ] All Section 12 audit passes done; Appendices A–G present; every `[VERIFY]` registered; no fabricated citation.
- [ ] No hype, no outcome or hiring claims, no company claims.

# 15. START

Begin with **Part 0** now. Do not ask clarifying questions; record any assumption as `[ASSUMPTION]`.

=== END PROMPT ===

## Notes for the human operator (not part of the prompt)

- **Audit step is yours too.** The prompt makes the model self-audit and emit Appendices A–D, but a model without browsing can only cite from memory. Before accepting the syllabus, work through **Appendix C (`[VERIFY]` register)**: check each cited paper/book against its source, check NetworkX/SciPy/scikit-learn behaviours against the official docs for the versions you install, and run every code block and `pytest` suite.
- Split the finished syllabus into the eight target files listed in Section 2; keep this prompt file alongside.
- If a part comes back truncated or summarised, reply `redo part k in full`.
