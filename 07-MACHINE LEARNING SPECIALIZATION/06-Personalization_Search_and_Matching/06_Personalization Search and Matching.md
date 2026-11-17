# Personalization, Search and Matching — ML Specialization Roadmap

**Group 6 (G6)** of the specialization that follows Stage 5D of the [Roadmap](./Roadmap.md). It covers original categories **11 Recommendation Systems Engineering, 12 Search and Ranking Engineering, 35 Recommender and Personalization Research and 37 Ranking, Matching and Decision Systems**. The group's defining question is: *which item should a given user or query get?* It follows G1 to G5: [`01_Classical and Applied ML.md`](./01_Classical%20and%20Applied%20ML.md), [`02_Deep Learning by Modality.md`](./02_Deep%20Learning%20by%20Modality.md), [`03_Generative and Foundation Models.md`](./03_Generative%20and%20Foundation%20Models.md), [`04_Agents and Sequential Decisions.md`](./04_Agents%20and%20Sequential%20Decisions.md), [`05_Time and Anomaly Modeling.md`](./05_Time%20and%20Anomaly%20Modeling.md).

## G6 summary

| Item | Count |
|---|---|
| Modules (including overview and capstones) | 22 |
| Lesson files | 181 |
| Hands-on project files (module projects, overview project and capstones) | 66 |
| Folders inside the G6 tree | 43 |
| Files inside the G6 tree | 297 |

| Original category | Modules |
|---|---|
| 12 Search and Ranking Engineering | 01 to 07 |
| 11 Recommendation Systems Engineering | 08 to 13 |
| 35 Recommender and Personalization Research | 14 to 15 (plus research rigor in 11 to 13) |
| 37 Ranking, Matching and Decision Systems | 16 to 19 |
| Shared operations for all four | 20 |

## Scope and how G6 avoids repeating the Roadmap

G6 starts where Stage 5B and the Stage 3 and Stage 2D data-infrastructure lessons stop. These are **already learned** and are only referenced, never retaught: recommendation problems and baselines, user-item matrices and feedback types, collaborative filtering, matrix factorization, content-based and hybrid recommendation, the two-tower retrieval idea, cold start, pointwise, pairwise and listwise ranking, precision and recall at k, MAP and nDCG, offline versus online evaluation, popularity bias, diversity and feedback loops (Stage 5B); bandits, off-policy evaluation, uplift modeling and experimentation methods (Stage 5B); sentence embeddings (Stage 5C); HNSW and graph-based ANN search and a mini vector search engine (Stage 3); Elasticsearch and OpenSearch as data infrastructure, embedding and vector data pipelines and feature stores (Stages 2D, 2C and 5D); the model-serving, monitoring and release lessons of Stage 5D; and, from earlier groups, bi-encoder and cross-encoder training basics (G2), RAG engineering (G3), reinforcement-learning algorithms (G4) and decision-focused evaluation (G1).

**Boundaries with other groups** (so nothing overlaps): graph neural network recommenders and graph learning belong to **G8**; operations-research optimization in depth belongs to **G8**; causal inference and uncertainty beyond what Stage 5B covers belong to **G7**; federated and privacy-preserving training belongs to **G12**; general benchmark design belongs to **G13**; inference acceleration and model compression belong to **G10**; MLOps platform design belongs to **G11**.

| Roadmap topic already covered | Where G6 goes further |
|---|---|
| Elasticsearch and OpenSearch infrastructure (2D), ranking metrics (5B) | Module 01: BM25 tuning, analyzers, Indic-language analysis, judgment lists and relevance workflow |
| Sentence embeddings (5C), cross-encoders (G2) | Module 03: dense, learned-sparse and late-interaction retriever training, hard negatives and benchmarking |
| HNSW and mini vector search engine (Stage 3) | Module 04: IVF, product quantization, disk-based and filtered search, sharding and benchmarks |
| Pointwise, pairwise and listwise ranking (5B) | Module 05: LambdaMART, neural listwise, cross-encoder and LLM rerankers and cascade design |
| Offline vs online evaluation (5B), bandit OPE (5B) | Modules 06 and 12: click models, unbiased learning to rank, interleaving and slate off-policy evaluation |
| Two-tower retrieval, cold start (5B) | Modules 08 and 09: impression logging, negative sampling, logQ correction, multi-interest and multi-source candidates |
| Matrix factorization and hybrids (5B) | Modules 10 and 11: CTR models, multi-task ranking, sequential and generative recommenders |
| Popularity bias, diversity, feedback loops (5B) | Module 13: exposure fairness, diversity re-ranking and marketplace dynamics |
| Bandits and OPE (5B), RL algorithms (G4) | Modules 14 and 15: personalization research methods and off-policy learning for recommendation |
| Graph algorithms (Stage 3) | Modules 16 and 17: matching markets, assignment, stable matching and job-candidate systems |
| Decision-focused evaluation (G1), human-in-the-loop pattern (5D) | Modules 18 and 19: auctions, pacing and decision-system design |
| Serving, monitoring and release (5D) | Module 20: index versioning, ranking monitoring, guardrail metrics and privacy |

## G6 — Personalization, Search and Matching

**Defining question:** Which item should a given user or query get?

```text
ML Specialization/
└── G6 — Personalization, Search and Matching/
    ├── 00-G6-Overview/
    │   ├── Projects/
    │   │   ├── 01-g6-ranking-evaluation-and-simulator-bootstrap.md
    │   │   └── README.md
    │   ├── 01-g6-scope-and-boundaries-with-stage-5b-and-other-groups.md
    │   ├── 02-prerequisite-map-from-the-roadmap.md
    │   ├── 03-dataset-and-tooling-register.md
    │   ├── 04-evaluation-and-reporting-standards.md
    │   ├── 05-completion-gate.md
    │   ├── README.md
    │   └── learning-plan.md
    ├── 01-Lexical-Retrieval-and-Relevance-Engineering/
    │   ├── Projects/
    │   │   ├── 01-bm25-and-analyzer-tuning-on-a-test-collection.md
    │   │   ├── 02-judgment-list-construction-and-agreement.md
    │   │   ├── 03-indic-search-analyzer-study.md
    │   │   └── README.md
    │   ├── 01-the-bm25-family.md
    │   ├── 02-analyzers-in-depth.md
    │   ├── 03-language-specific-analysis.md
    │   ├── 04-field-design-and-boosting.md
    │   ├── 05-query-construction-for-relevance.md
    │   ├── 06-test-collections.md
    │   ├── 07-search-metrics-for-judged-data.md
    │   ├── 08-relevance-tuning-workflow.md
    │   ├── 09-tooling-for-experiments.md
    │   └── README.md
    ├── 02-Query-Understanding-and-Search-Experience/
    │   ├── Projects/
    │   │   ├── 01-spell-correction-and-autocomplete-system.md
    │   │   ├── 02-query-intent-classifier-for-product-search.md
    │   │   ├── 03-hinglish-query-normalization.md
    │   │   └── README.md
    │   ├── 01-query-log-analysis.md
    │   ├── 02-spelling-correction.md
    │   ├── 03-autocomplete-and-query-suggestion.md
    │   ├── 04-query-classification-and-intent-detection.md
    │   ├── 05-entity-and-attribute-recognition-in-queries-using-methods-from-g2.md
    │   ├── 06-query-rewriting-and-expansion.md
    │   ├── 07-mixed-script-and-transliterated-queries-such-as-hinglish.md
    │   ├── 08-zero-result-queries-facets-and-filters-and-recovery-strategies.md
    │   ├── 09-evaluating-query-understanding.md
    │   └── README.md
    ├── 03-Dense-Sparse-and-Hybrid-Retrieval-Models/
    │   ├── Projects/
    │   │   ├── 01-train-a-dense-retriever-with-hard-negatives.md
    │   │   ├── 02-retrieval-architecture-bakeoff.md
    │   │   ├── 03-domain-adaptation-with-synthetic-queries.md
    │   │   └── README.md
    │   ├── 01-dense-retriever-training.md
    │   ├── 02-negative-mining-and-false-negatives.md
    │   ├── 03-late-interaction-retrieval.md
    │   ├── 04-learned-sparse-retrieval.md
    │   ├── 05-knowledge-distillation-from-cross-encoders-into-retrievers.md
    │   ├── 06-domain-adaptation-with-synthetic-queries.md
    │   ├── 07-multilingual-and-indic-retrieval.md
    │   ├── 08-hybrid-fusion.md
    │   ├── 09-retrieval-benchmarks.md
    │   ├── 10-choosing-a-retrieval-stack.md
    │   └── README.md
    ├── 04-Approximate-Nearest-Neighbor-Systems-at-Scale/
    │   ├── Projects/
    │   │   ├── 01-ann-index-benchmark-on-your-embeddings.md
    │   │   ├── 02-filtered-search-failure-study.md
    │   │   ├── 03-embedding-compression-quality-trade-off.md
    │   │   └── README.md
    │   ├── 01-recall-latency-and-cost.md
    │   ├── 02-inverted-file-indexes.md
    │   ├── 03-product-quantization-and-optimized-variants.md
    │   ├── 04-scalar-and-binary-quantization-and-matryoshka-style-dimension-truncation.md
    │   ├── 05-disk-based-search.md
    │   ├── 06-anisotropic-quantization-and-scann-style-methods.md
    │   ├── 07-filtered-search.md
    │   ├── 08-sharding-replication-and-index-updates.md
    │   ├── 09-gpu-search-with-faiss-and-cuvs.md
    │   ├── 10-benchmarks-and-tooling.md
    │   └── README.md
    ├── 05-Learning-to-Rank-and-Reranking-Systems/
    │   ├── Projects/
    │   │   ├── 01-lambdamart-ltr-on-mslr-or-istella.md
    │   │   ├── 02-three-stage-search-cascade.md
    │   │   ├── 03-llm-reranker-cost-quality-study.md
    │   │   └── README.md
    │   ├── 01-learning-to-rank-datasets-and-features.md
    │   ├── 02-lambdamart-with-lightgbm-and-xgboost.md
    │   ├── 03-neural-listwise-ranking.md
    │   ├── 04-cross-encoder-rerankers.md
    │   ├── 05-llm-rerankers.md
    │   ├── 06-cascade-ranking.md
    │   ├── 07-multi-objective-ranking.md
    │   ├── 08-ranking-feature-engineering-and-leakage-in-click-derived-features.md
    │   ├── 09-evaluating-rankers.md
    │   └── README.md
    ├── 06-Click-Data-Counterfactual-Ranking-and-Search-Evaluation/
    │   ├── Projects/
    │   │   ├── 01-click-model-and-position-bias-estimation.md
    │   │   ├── 02-unbiased-ltr-vs-naive-click-training.md
    │   │   ├── 03-interleaving-vs-ab-sensitivity.md
    │   │   └── README.md
    │   ├── 01-what-clicks-mean.md
    │   ├── 02-click-models.md
    │   ├── 03-position-bias-estimation.md
    │   ├── 04-unbiased-learning-to-rank.md
    │   ├── 05-counterfactual-evaluation-of-rankings.md
    │   ├── 06-interleaving.md
    │   ├── 07-online-metrics.md
    │   ├── 08-llm-based-relevance-judgments.md
    │   ├── 09-offline-online-gap.md
    │   └── README.md
    ├── 07-Search-Product-Architecture-and-Generated-Answers/
    │   ├── Projects/
    │   │   ├── 01-product-search-with-attributes-and-substitutes.md
    │   │   ├── 02-answer-or-results-decision-policy.md
    │   │   ├── 03-search-cost-model.md
    │   │   └── README.md
    │   ├── 01-end-to-end-search-architecture.md
    │   ├── 02-vertical-and-federated-search.md
    │   ├── 03-product-search-specifics.md
    │   ├── 04-enterprise-search.md
    │   ├── 05-answer-engines.md
    │   ├── 06-attribution-and-citation-quality-for-generated-answers.md
    │   ├── 07-evaluating-answer-search-systems.md
    │   ├── 08-search-cost-model.md
    │   └── README.md
    ├── 08-Industrial-Recommender-Architecture-and-Training-Data/
    │   ├── Projects/
    │   │   ├── 01-recommender-training-data-pipeline.md
    │   │   ├── 02-negative-sampling-effect-study.md
    │   │   ├── 03-exposure-bias-demonstration.md
    │   │   └── README.md
    │   ├── 01-multi-stage-architecture.md
    │   ├── 02-impression-logging.md
    │   ├── 03-label-definition.md
    │   ├── 04-negative-sampling-and-unobserved-is-not-negative.md
    │   ├── 05-time-based-data-construction.md
    │   ├── 06-id-embeddings-and-the-hashing-trick.md
    │   ├── 07-feedback-loops-in-training-data.md
    │   ├── 08-experiment-and-data-flywheel-design.md
    │   └── README.md
    ├── 09-Retrieval-and-Candidate-Generation-for-Recommendations/
    │   ├── Projects/
    │   │   ├── 01-two-tower-with-logq-correction.md
    │   │   ├── 02-multi-source-candidate-merging.md
    │   │   ├── 03-cold-start-item-retrieval-with-content-embeddings.md
    │   │   └── README.md
    │   ├── 01-two-tower-training.md
    │   ├── 02-mixed-and-hard-negative-strategies-and-their-bias.md
    │   ├── 03-multi-interest-models.md
    │   ├── 04-item-to-item-retrieval.md
    │   ├── 05-session-and-sequence-based-candidate-generation.md
    │   ├── 06-content-based-retrieval-for-new-items-using-the-models-from-g2-and-g3.md
    │   ├── 07-merging-candidate-sources.md
    │   ├── 08-serving-retrieval-with-ann-indexes-from-module-04.md
    │   ├── 09-evaluating-retrieval.md
    │   └── README.md
    ├── 10-CTR-Prediction-and-Multi-Objective-Ranking-Models/
    │   ├── Projects/
    │   │   ├── 01-ctr-model-zoo-on-criteo-or-avazu.md
    │   │   ├── 02-multi-task-click-and-conversion-model.md
    │   │   ├── 03-calibration-and-blending-study.md
    │   │   └── README.md
    │   ├── 01-feature-interactions.md
    │   ├── 02-wide-and-deep-deepfm-and-dcn-v2.md
    │   ├── 03-dlrm-style-architectures.md
    │   ├── 04-user-behavior-sequence-models.md
    │   ├── 05-multi-task-learning.md
    │   ├── 06-conversion-modeling-with-sample-selection-bias.md
    │   ├── 07-calibration-for-ctr-models.md
    │   ├── 08-combining-objectives.md
    │   ├── 09-training-with-very-large-embedding-tables.md
    │   ├── 10-delayed-conversion-feedback-and-label-correction.md
    │   └── README.md
    ├── 11-Sequential-Session-Based-and-Generative-Recommendation/
    │   ├── Projects/
    │   │   ├── 01-sequential-model-comparison-with-honest-baselines.md
    │   │   ├── 02-sampled-vs-full-metrics-demonstration.md
    │   │   ├── 03-semantic-id-generative-retrieval-prototype.md
    │   │   └── README.md
    │   ├── 01-session-based-baselines.md
    │   ├── 02-recurrent-and-convolutional-sequence-models.md
    │   ├── 03-transformer-sequence-models.md
    │   ├── 04-long-user-histories.md
    │   ├── 05-generative-recommenders.md
    │   ├── 06-semantic-ids-and-generative-retrieval.md
    │   ├── 07-llm-based-sequential-recommendation.md
    │   ├── 08-evaluation-traps.md
    │   ├── 09-scaling-behavior.md
    │   └── README.md
    ├── 12-Recommender-Evaluation-Rigor-and-Reproducibility/
    │   ├── Projects/
    │   │   ├── 01-baseline-strength-audit.md
    │   │   ├── 02-slate-off-policy-evaluation-study.md
    │   │   ├── 03-beyond-accuracy-evaluation-suite.md
    │   │   └── README.md
    │   ├── 01-why-recommender-progress-is-hard-to-verify.md
    │   ├── 02-dataset-selection.md
    │   ├── 03-splitting-protocols.md
    │   ├── 04-beyond-accuracy-metrics.md
    │   ├── 05-statistical-testing-for-recommender-comparisons-and-multiple-comparison-problems.md
    │   ├── 06-counterfactual-evaluation-for-slates.md
    │   ├── 07-simulators-for-recommender-research-and-their-validity-limits.md
    │   ├── 08-frameworks-and-tooling.md
    │   ├── 09-user-studies-and-satisfaction-surveys-alongside-logs.md
    │   └── README.md
    ├── 13-Fairness-Diversity-and-Marketplace-Effects/
    │   ├── Projects/
    │   │   ├── 01-exposure-fairness-reranker.md
    │   │   ├── 02-feedback-loop-simulation.md
    │   │   ├── 03-diversity-reranking-comparison.md
    │   │   └── README.md
    │   ├── 01-whose-interests-count.md
    │   ├── 02-exposure-fairness.md
    │   ├── 03-user-side-fairness.md
    │   ├── 04-popularity-bias-and-its-mitigation.md
    │   ├── 05-diversity-re-ranking.md
    │   ├── 06-filter-bubbles-and-feedback-loops.md
    │   ├── 07-two-sided-marketplace-dynamics.md
    │   ├── 08-long-term-effects.md
    │   ├── 09-transparency-and-user-control.md
    │   └── README.md
    ├── 14-User-Modeling-and-Personalization-Algorithms/
    │   ├── Projects/
    │   │   ├── 01-onboarding-preference-elicitation-study.md
    │   │   ├── 02-llm-recommender-evaluation.md
    │   │   ├── 03-research-reproduction-and-extension.md
    │   │   └── README.md
    │   ├── 01-user-representation-learning.md
    │   ├── 02-context-aware-personalization.md
    │   ├── 03-preference-elicitation-and-onboarding.md
    │   ├── 04-cross-domain-and-transfer-learning-for-personalization.md
    │   ├── 05-privacy-preserving-personalization.md
    │   ├── 06-llm-based-personalization.md
    │   ├── 07-conversational-recommendation.md
    │   ├── 08-explainable-recommendation.md
    │   ├── 09-long-term-value-and-satisfaction-as-objectives.md
    │   ├── 10-research-method.md
    │   └── README.md
    ├── 15-Bandits-Counterfactual-Learning-and-RL-for-Personalization/
    │   ├── Projects/
    │   │   ├── 01-contextual-bandit-with-logged-data.md
    │   │   ├── 02-exploration-budget-study.md
    │   │   ├── 03-safe-exploration-guardrails.md
    │   │   └── README.md
    │   ├── 01-contextual-bandits-in-production.md
    │   ├── 02-slate-and-ranking-bandits.md
    │   ├── 03-off-policy-learning.md
    │   ├── 04-learning-from-logged-bandit-feedback-with-propensity-logging-requirements.md
    │   ├── 05-delayed-and-long-term-rewards-in-personalization.md
    │   ├── 06-reinforcement-learning-for-recommendation.md
    │   ├── 07-simulators-and-sim-to-real-gaps-for-recommendation-research.md
    │   ├── 08-safe-exploration.md
    │   ├── 09-open-bandit-pipeline-and-experiment-tooling.md
    │   └── README.md
    ├── 16-Matching-Markets-and-Assignment-Foundations/
    │   ├── Projects/
    │   │   ├── 01-dispatch-matching-simulator.md
    │   │   ├── 02-stable-matching-and-incentives.md
    │   │   ├── 03-capacity-constrained-assignment.md
    │   │   └── README.md
    │   ├── 01-matching-problem-types.md
    │   ├── 02-assignment-problem.md
    │   ├── 03-stable-matching.md
    │   ├── 04-capacity-and-fairness-constraints-in-matching.md
    │   ├── 05-online-and-batched-matching.md
    │   ├── 06-reciprocal-recommendation.md
    │   ├── 07-learning-preferences-for-matching.md
    │   ├── 08-congestion-and-market-thickness.md
    │   ├── 09-solving-with-or-tools-and-scipy-and-knowing-when-to-hand-over-to-g8-methods.md
    │   └── README.md
    ├── 17-Job-Candidate-and-Resource-Matching-Systems/
    │   ├── Projects/
    │   │   ├── 01-resume-job-matching-pipeline.md
    │   │   ├── 02-adverse-impact-audit.md
    │   │   ├── 03-support-routing-system.md
    │   │   └── README.md
    │   ├── 01-document-understanding-for-matching.md
    │   ├── 02-skills-and-taxonomy-normalization.md
    │   ├── 03-two-sided-scoring.md
    │   ├── 04-candidate-job-retrieval-and-ranking-pipelines.md
    │   ├── 05-hiring-specific-fairness-and-legal-considerations.md
    │   ├── 06-explanations-and-recourse-for-candidates-and-recruiters.md
    │   ├── 07-request-to-resource-matching.md
    │   ├── 08-spam-gaming-and-abuse-in-marketplaces.md
    │   ├── 09-evaluating-matching.md
    │   └── README.md
    ├── 18-Auctions-Ads-Ranking-and-Budget-Pacing/
    │   ├── Projects/
    │   │   ├── 01-auction-simulator-and-bidding-strategies.md
    │   │   ├── 02-budget-pacing-controller.md
    │   │   ├── 03-calibration-impact-on-auction-revenue.md
    │   │   └── README.md
    │   ├── 01-ad-ranking.md
    │   ├── 02-auction-basics.md
    │   ├── 03-bid-shading-and-bidding-strategies-in-first-price-settings.md
    │   ├── 04-budget-pacing-and-delivery-smoothing.md
    │   ├── 05-calibration-requirements-for-auction-models.md
    │   ├── 06-bidding-and-allocation-as-constrained-optimization.md
    │   ├── 07-experimentation-in-ads.md
    │   ├── 08-brand-safety-policy-and-quality-filters.md
    │   └── README.md
    ├── 19-Decision-Systems-Policies-Constraints-and-Human-Review/
    │   ├── Projects/
    │   │   ├── 01-score-to-decision-policy-with-constraints.md
    │   │   ├── 02-decision-logging-for-counterfactual-learning.md
    │   │   ├── 03-strategic-behavior-simulation.md
    │   │   └── README.md
    │   ├── 01-from-score-to-action.md
    │   ├── 02-policy-layers.md
    │   ├── 03-predict-then-optimize-in-practice-and-when-decision-focused-learning-is-worth-it.md
    │   ├── 04-queues-and-capacity.md
    │   ├── 05-decision-logging-for-later-counterfactual-learning.md
    │   ├── 06-simulating-policies-before-launch.md
    │   ├── 07-explaining-and-contesting-decisions.md
    │   ├── 08-long-term-effects-and-strategic-behavior-of-the-people-being-decided-about.md
    │   ├── 09-decision-system-failures.md
    │   └── README.md
    ├── 20-Operating-Personalization-Search-and-Matching-Systems/
    │   ├── Projects/
    │   │   ├── 01-embedding-and-index-version-rollout.md
    │   │   ├── 02-ranking-system-monitoring-with-injected-regressions.md
    │   │   ├── 03-guardrail-metric-design-workshop.md
    │   │   └── README.md
    │   ├── 01-latency-budgets-and-caching-for-ranked-results.md
    │   ├── 02-feature-freshness-and-real-time-user-features.md
    │   ├── 03-embedding-and-index-versioning.md
    │   ├── 04-experimentation-platform-requirements.md
    │   ├── 05-north-star-and-guardrail-metric-design.md
    │   ├── 06-monitoring-ranking-systems.md
    │   ├── 07-privacy-consent-and-data-retention-for-behavioral-data-under-the-dpdp-act.md
    │   ├── 08-incident-handling-for-bad-rankings-and-recommendation-failures.md
    │   ├── 09-cost-management-for-large-scale-retrieval-and-ranking.md
    │   └── README.md
    ├── 21-G6-Capstones/
    │   ├── 01-search-system-from-lexical-to-learned-ranking.md
    │   ├── 02-recommender-system-with-rigorous-evaluation.md
    │   ├── 03-matching-and-decision-platform.md
    │   ├── 04-personalization-research-project.md
    │   ├── 05-g6-readiness-assessment.md
    │   └── README.md
    └── README.md
```

### 00 — G6 Overview

**Purpose:** the single authoritative plan for G6 with scope, boundaries, prerequisite map, dataset and tooling register, evaluation standards and completion gate.

- `01-g6-scope-and-boundaries-with-stage-5b-and-other-groups.md` — what G6 teaches and what it leaves to other groups.
- `02-prerequisite-map-from-the-roadmap.md` — Roadmap stages and modules assumed for each G6 module.
- `03-dataset-and-tooling-register.md` — every dataset, licence and access condition, library with version and maintenance status.
- `04-evaluation-and-reporting-standards.md` — splitting protocols, full-ranking metrics, baseline-tuning rules, significance testing and report template.
- `05-completion-gate.md` — measurable criteria to finish G6.
- `learning-plan.md` — recommended order, search, recommendation and matching tracks and compute budget.

**Project 1: g6 ranking evaluation and simulator bootstrap**  
- Data: a small judged search collection and a small interaction dataset.  
- Task: build a reproducible workspace with pinned tooling, a ranking-evaluation library (nDCG, MRR, recall, coverage) tested against reference values, a temporal-split harness and a tiny recommender simulator with known preferences.  
- Deliverables: lockfile, evaluation library with tests and the simulator.  
- Pass gate: a clean machine reproduces the tests from the lockfile, and a deliberately leaky split is caught by the harness.

### 01 — Lexical Retrieval and Relevance Engineering

**Outcome:** Tune and evaluate keyword search properly. Running Elasticsearch and OpenSearch as data infrastructure is covered in Stage 2D, and precision, recall, MAP and nDCG are introduced in Stage 5B; this module is about relevance.

**Lessons**

- `01-the-bm25-family.md` — The BM25 family: term saturation, length normalization and parameter tuning
- `02-analyzers-in-depth.md` — Analyzers in depth: tokenizers, stemmers, stop words, synonyms and decompounding
- `03-language-specific-analysis.md` — Language-specific analysis: Hindi and other Indic languages, transliteration and normalization
- `04-field-design-and-boosting.md` — Field design and boosting: titles, bodies, structured fields and multi-field scoring
- `05-query-construction-for-relevance.md` — Query construction for relevance: boolean, phrase, proximity and fuzzy matching
- `06-test-collections.md` — Test collections: judgment lists, graded relevance and annotator guidelines
- `07-search-metrics-for-judged-data.md` — Search metrics for judged data: nDCG, MRR and recall at depth, with judgment-coverage problems
- `08-relevance-tuning-workflow.md` — Relevance tuning workflow: offline evaluation, regression sets and avoiding overfitting to a query set
- `09-tooling-for-experiments.md` — Tooling for experiments: Pyserini, PyTerrier and Anserini

**Hands-on projects**

- **Project 1: bm25 and analyzer tuning on a test collection**  
  - Data: A TREC-style or BEIR collection plus a small Hindi or other Indic-language collection you assemble  
  - Task: Tune BM25 parameters, analyzers and field boosts and measure each change on nDCG and recall with confidence intervals.  
  - Deliverables: Tuning log, ablation table and a held-out query evaluation.  
  - Pass gate: Final numbers computed on queries never used for tuning.
- **Project 2: judgment list construction and agreement**  
  - Data: A product or document corpus of your choice with 100 queries  
  - Task: Write guidelines, collect graded judgments from two annotators, measure agreement and study how unjudged results distort metrics.  
  - Deliverables: Guidelines, judgments and analysis.  
  - Pass gate: Agreement and unjudged-document rate reported.
- **Project 3: indic search analyzer study**  
  - Data: Public Hindi, Bengali or Tamil text with queries  
  - Task: Compare default and custom analyzers including normalization and transliteration handling.  
  - Deliverables: Analyzer comparison.  
  - Pass gate: Per-language results reported.

### 02 — Query Understanding and Search Experience

**Outcome:** Understand what searchers mean and handle messy queries, including mixed-script Indian queries.

**Lessons**

- `01-query-log-analysis.md` — Query log analysis: head, torso and tail queries and intent distributions
- `02-spelling-correction.md` — Spelling correction: noisy-channel and neural approaches with evaluation
- `03-autocomplete-and-query-suggestion.md` — Autocomplete and query suggestion: candidate generation, ranking and bias
- `04-query-classification-and-intent-detection.md` — Query classification and intent detection: category, navigational and transactional intent
- `05-entity-and-attribute-recognition-in-queries-using-methods-from-g2.md` — Entity and attribute recognition in queries using methods from G2
- `06-query-rewriting-and-expansion.md` — Query rewriting and expansion: synonyms, learned expansion and LLM-assisted rewriting with safeguards
- `07-mixed-script-and-transliterated-queries-such-as-hinglish.md` — Mixed-script and transliterated queries such as Hinglish
- `08-zero-result-queries-facets-and-filters-and-recovery-strategies.md` — Zero-result queries, facets and filters, and recovery strategies
- `09-evaluating-query-understanding.md` — Evaluating query understanding: component metrics against end-to-end search quality

**Hands-on projects**

- **Project 1: spell correction and autocomplete system**  
  - Data: A public query log such as AOL-style or a synthetic log you generate from a product catalog  
  - Task: Build spelling correction and autocomplete and evaluate by accepted-suggestion rate proxies and offline ranking metrics.  
  - Deliverables: System and evaluation.  
  - Pass gate: Training and test queries split by user or time, not randomly.
- **Project 2: query intent classifier for product search**  
  - Data: Amazon Shopping Queries dataset (ESCI) or Wayfair WANDS  
  - Task: Build a query category and attribute classifier and measure the effect on search ranking.  
  - Deliverables: Classifier and ranking-impact analysis.  
  - Pass gate: Gain measured end to end, not only classifier accuracy.
- **Project 3: hinglish query normalization**  
  - Data: Mixed-script queries you collect or simulate  
  - Task: Normalize transliterated queries and measure recall gains.  
  - Deliverables: Normalizer and recall analysis.  
  - Pass gate: Transliteration variants evaluated per script.

### 03 — Dense Sparse and Hybrid Retrieval Models

**Outcome:** Train and compare retrieval models rather than only calling them. Sentence-embedding fundamentals are covered in Stage 5C, bi-encoder and cross-encoder basics in G2, and application-level hybrid retrieval in G3.

**Lessons**

- `01-dense-retriever-training.md` — Dense retriever training: in-batch and hard negatives, loss functions and temperature
- `02-negative-mining-and-false-negatives.md` — Negative mining and false negatives: effects on training and evaluation
- `03-late-interaction-retrieval.md` — Late-interaction retrieval: ColBERT-style models and their index cost
- `04-learned-sparse-retrieval.md` — Learned sparse retrieval: SPLADE-style models and expansion
- `05-knowledge-distillation-from-cross-encoders-into-retrievers.md` — Knowledge distillation from cross-encoders into retrievers
- `06-domain-adaptation-with-synthetic-queries.md` — Domain adaptation with synthetic queries
- `07-multilingual-and-indic-retrieval.md` — Multilingual and Indic retrieval: model choice and evaluation
- `08-hybrid-fusion.md` — Hybrid fusion: reciprocal rank fusion and learned fusion
- `09-retrieval-benchmarks.md` — Retrieval benchmarks: BEIR, MS MARCO and MIRACL, with their licences and saturation problems
- `10-choosing-a-retrieval-stack.md` — Choosing a retrieval stack: quality, latency, index size and operational complexity

**Hands-on projects**

- **Project 1: train a dense retriever with hard negatives**  
  - Data: MS MARCO passage subset (check licence) and a BEIR task  
  - Task: Train a bi-encoder with in-batch and mined hard negatives and compare with BM25 and a pretrained model.  
  - Deliverables: Training code and evaluation.  
  - Pass gate: False-negative rate in mined negatives estimated and reported.
- **Project 2: retrieval architecture bakeoff**  
  - Data: BEIR subsets and MIRACL languages including Hindi  
  - Task: Compare BM25, dense, learned sparse, late interaction and hybrid fusion on quality, latency and index size.  
  - Deliverables: Bake-off table with intervals across datasets.  
  - Pass gate: Same corpus preprocessing and hardware for all methods.
- **Project 3: domain adaptation with synthetic queries**  
  - Data: A target-domain corpus without labels  
  - Task: Generate synthetic queries, fine-tune a retriever and measure gains on a small human-labeled test set.  
  - Deliverables: Pipeline and evaluation.  
  - Pass gate: Human-labeled test set not used in generation or tuning.

### 04 — Approximate Nearest Neighbor Systems at Scale

**Outcome:** Operate vector search at scale. HNSW and graph-based ANN search and a mini vector search engine are covered in Stage 3, and embedding pipelines in Stage 2D; this module covers the rest of the index families and the scale problems.

**Lessons**

- `01-recall-latency-and-cost.md` — Recall, latency and cost: how to measure an ANN index honestly
- `02-inverted-file-indexes.md` — Inverted-file indexes: IVF and cell-probe tuning
- `03-product-quantization-and-optimized-variants.md` — Product quantization and optimized variants: memory vs recall
- `04-scalar-and-binary-quantization-and-matryoshka-style-dimension-truncation.md` — Scalar and binary quantization and Matryoshka-style dimension truncation
- `05-disk-based-search.md` — Disk-based search: DiskANN-style graphs and memory budgets
- `06-anisotropic-quantization-and-scann-style-methods.md` — Anisotropic quantization and ScaNN-style methods
- `07-filtered-search.md` — Filtered search: pre-filter, post-filter and in-graph filtering and their failure modes
- `08-sharding-replication-and-index-updates.md` — Sharding, replication and index updates: deletes, inserts and rebuild strategy
- `09-gpu-search-with-faiss-and-cuvs.md` — GPU search with FAISS and cuVS
- `10-benchmarks-and-tooling.md` — Benchmarks and tooling: ANN-Benchmarks, big-ann-benchmarks and hnswlib

**Hands-on projects**

- **Project 1: ann index benchmark on your embeddings**  
  - Data: A million-vector embedding set from a public corpus  
  - Task: Benchmark IVF, IVF-PQ, HNSW and a disk-based index on recall at fixed latency and memory.  
  - Deliverables: Recall-latency-memory frontier plots.  
  - Pass gate: Ground truth from exact search on a query sample.
- **Project 2: filtered search failure study**  
  - Data: Vectors with metadata filters of varying selectivity  
  - Task: Measure recall as filter selectivity changes under pre-filter, post-filter and in-index filtering.  
  - Deliverables: Selectivity-recall analysis.  
  - Pass gate: Selectivity levels from 0.1 percent to 50 percent.
- **Project 3: embedding compression quality trade off**  
  - Data: A retrieval benchmark with embeddings  
  - Task: Compare dimension truncation, scalar quantization and binary codes on retrieval quality and cost.  
  - Deliverables: Quality-vs-size table.  
  - Pass gate: Quality measured on the downstream retrieval metric.

### 05 — Learning to Rank and Reranking Systems

**Outcome:** Build the ranking layers of a search system. The pointwise, pairwise and listwise ideas are introduced in Stage 5B; this module implements them and builds cascades.

**Lessons**

- `01-learning-to-rank-datasets-and-features.md` — Learning-to-rank datasets and features: query-document, document and query features
- `02-lambdamart-with-lightgbm-and-xgboost.md` — LambdaMART with LightGBM and XGBoost: objectives and tuning
- `03-neural-listwise-ranking.md` — Neural listwise ranking: softmax cross-entropy and TF-Ranking-style losses
- `04-cross-encoder-rerankers.md` — Cross-encoder rerankers: training with hard negatives and distillation
- `05-llm-rerankers.md` — LLM rerankers: pointwise and listwise prompting, cost and consistency
- `06-cascade-ranking.md` — Cascade ranking: stage budgets and latency allocation
- `07-multi-objective-ranking.md` — Multi-objective ranking: relevance, freshness, quality and business signals
- `08-ranking-feature-engineering-and-leakage-in-click-derived-features.md` — Ranking feature engineering and leakage in click-derived features
- `09-evaluating-rankers.md` — Evaluating rankers: significance testing across queries and per-query regressions

**Hands-on projects**

- **Project 1: lambdamart ltr on mslr or istella**  
  - Data: MSLR-WEB30K or Istella22 (check licence)  
  - Task: Train LambdaMART and neural listwise models and compare with BM25 as features.  
  - Deliverables: Models and nDCG comparison with paired tests.  
  - Pass gate: Paired significance tests across queries.
- **Project 2: three stage search cascade**  
  - Data: A BEIR or ESCI-based setup  
  - Task: Build BM25 plus dense retrieval, a LambdaMART stage and a cross-encoder reranker and tune the budget per stage.  
  - Deliverables: Cascade and quality-latency curve.  
  - Pass gate: Latency measured end to end at stated load.
- **Project 3: llm reranker cost quality study**  
  - Data: A BEIR subset  
  - Task: Compare a cross-encoder with pointwise and listwise LLM reranking on quality, cost and run-to-run variability.  
  - Deliverables: Cost-quality analysis.  
  - Pass gate: Repeated runs and prices recorded with dates.

### 06 — Click Data Counterfactual Ranking and Search Evaluation

**Outcome:** Learn from user behavior without being fooled by position bias, and measure search quality online. Offline versus online evaluation basics and bandit off-policy evaluation are covered in Stage 5B.

**Lessons**

- `01-what-clicks-mean.md` — What clicks mean: implicit feedback, noise and dwell-time signals
- `02-click-models.md` — Click models: position-based, cascade and dynamic Bayesian network models
- `03-position-bias-estimation.md` — Position bias estimation: intervention harvesting and EM-based methods
- `04-unbiased-learning-to-rank.md` — Unbiased learning to rank: inverse-propensity weighting and dual learning
- `05-counterfactual-evaluation-of-rankings.md` — Counterfactual evaluation of rankings: estimators and their variance
- `06-interleaving.md` — Interleaving: team-draft and probabilistic interleaving for sensitive online tests
- `07-online-metrics.md` — Online metrics: success, abandonment, reformulation and long-term value
- `08-llm-based-relevance-judgments.md` — LLM-based relevance judgments: calibration against human labels and failure modes
- `09-offline-online-gap.md` — Offline-online gap: why offline gains fail online

**Hands-on projects**

- **Project 1: click model and position bias estimation**  
  - Data: Baidu-ULTR or a click simulator you build with known propensities  
  - Task: Fit click models, estimate position bias and recover known propensities in simulation.  
  - Deliverables: Estimation accuracy and real-data analysis.  
  - Pass gate: Estimators validated on simulated data with ground truth.
- **Project 2: unbiased ltr vs naive click training**  
  - Data: Simulated clicks over a public LTR dataset such as MSLR  
  - Task: Compare naive click-trained rankers with IPS-corrected ones under varying bias strength.  
  - Deliverables: Comparison across bias levels.  
  - Pass gate: True relevance labels used only for evaluation.
- **Project 3: interleaving vs ab sensitivity**  
  - Data: Simulated users with known preferences  
  - Task: Measure how many sessions team-draft interleaving needs compared with A/B testing to detect the same improvement.  
  - Deliverables: Sensitivity analysis.  
  - Pass gate: Many simulation repetitions with intervals.

### 07 — Search Product Architecture and Generated Answers

**Outcome:** Assemble search into a product that may also produce generated answers. RAG engineering is covered in G3; this module covers search-product decisions.

**Lessons**

- `01-end-to-end-search-architecture.md` — End-to-end search architecture: retrieval, ranking, blending and result presentation
- `02-vertical-and-federated-search.md` — Vertical and federated search: merging results from several sources
- `03-product-search-specifics.md` — Product search specifics: structured attributes, availability and substitutes and complements
- `04-enterprise-search.md` — Enterprise search: permissions, freshness and heterogeneous content
- `05-answer-engines.md` — Answer engines: when to show a generated answer and when not to
- `06-attribution-and-citation-quality-for-generated-answers.md` — Attribution and citation quality for generated answers
- `07-evaluating-answer-search-systems.md` — Evaluating answer-search systems: relevance, faithfulness and user outcomes
- `08-search-cost-model.md` — Search cost model: infrastructure, model calls and caching

**Hands-on projects**

- **Project 1: product search with attributes and substitutes**  
  - Data: Amazon ESCI or WANDS  
  - Task: Build a product search stack handling exact, substitute and complement results and evaluate by label class.  
  - Deliverables: System and per-class evaluation.  
  - Pass gate: Per-class metrics reported, not only a single score.
- **Project 2: answer or results decision policy**  
  - Data: A query set with both factual and exploratory queries  
  - Task: Build a policy that decides when to show a generated answer and evaluate user-outcome proxies and error cost.  
  - Deliverables: Policy and error analysis.  
  - Pass gate: Wrong-answer cost explicitly modeled.
- **Project 3: search cost model**  
  - Data: Measured costs from your stack  
  - Task: Build a per-query cost model and find the cost drivers.  
  - Deliverables: Cost model with sensitivity.  
  - Pass gate: Every cost input measured or sourced with a date.

### 08 — Industrial Recommender Architecture and Training Data

**Outcome:** Understand how production recommenders are structured and how their training data is built. Recommendation baselines, collaborative filtering, matrix factorization, hybrids and cold-start basics are covered in Stage 5B.

**Lessons**

- `01-multi-stage-architecture.md` — Multi-stage architecture: retrieval, pre-ranking, ranking and re-ranking
- `02-impression-logging.md` — Impression logging: exposure, position and context as first-class data
- `03-label-definition.md` — Label definition: clicks, watch time, purchases, satisfaction and delayed feedback
- `04-negative-sampling-and-unobserved-is-not-negative.md` — Negative sampling and unobserved-is-not-negative: implications for training and evaluation
- `05-time-based-data-construction.md` — Time-based data construction: leakage-safe splits and point-in-time features
- `06-id-embeddings-and-the-hashing-trick.md` — ID embeddings and the hashing trick: huge categorical vocabularies
- `07-feedback-loops-in-training-data.md` — Feedback loops in training data: exposure bias and exploration data
- `08-experiment-and-data-flywheel-design.md` — Experiment and data-flywheel design: logging what you need for future models

**Hands-on projects**

- **Project 1: recommender training data pipeline**  
  - Data: H&M Personalized Fashion or Otto session data (Kaggle; accept terms)  
  - Task: Build impression-aware, leakage-safe training sets with several label and negative-sampling definitions.  
  - Deliverables: Pipeline with leakage tests.  
  - Pass gate: A deliberately leaky feature is caught by the tests.
- **Project 2: negative sampling effect study**  
  - Data: MovieLens-25M or Amazon Reviews 2023 subset  
  - Task: Compare random, popularity-based and hard negative sampling on offline metrics and on a debiased test set.  
  - Deliverables: Comparison with intervals.  
  - Pass gate: Evaluation protocol fixed before comparison.
- **Project 3: exposure bias demonstration**  
  - Data: A recommender simulator you build  
  - Task: Show how training on logged exposure biases a model and how exploration data corrects it.  
  - Deliverables: Simulation and analysis.  
  - Pass gate: True preferences known in the simulator.

### 09 — Retrieval and Candidate Generation for Recommendations

**Outcome:** Build the first stage that selects hundreds from millions. The two-tower idea is introduced in Stage 5B; this module covers the training details and alternatives.

**Lessons**

- `01-two-tower-training.md` — Two-tower training: sampled softmax, in-batch negatives and logQ correction
- `02-mixed-and-hard-negative-strategies-and-their-bias.md` — Mixed and hard negative strategies and their bias
- `03-multi-interest-models.md` — Multi-interest models: representing users with several vectors
- `04-item-to-item-retrieval.md` — Item-to-item retrieval: co-occurrence, item embeddings and nearest neighbors
- `05-session-and-sequence-based-candidate-generation.md` — Session and sequence-based candidate generation
- `06-content-based-retrieval-for-new-items-using-the-models-from-g2-and-g3.md` — Content-based retrieval for new items using the models from G2 and G3
- `07-merging-candidate-sources.md` — Merging candidate sources: quotas, deduplication and diversity
- `08-serving-retrieval-with-ann-indexes-from-module-04.md` — Serving retrieval with ANN indexes from module 04
- `09-evaluating-retrieval.md` — Evaluating retrieval: recall at K, coverage and source contribution

**Hands-on projects**

- **Project 1: two tower with logq correction**  
  - Data: MovieLens-25M or Amazon Reviews  
  - Task: Train a two-tower retrieval model with in-batch negatives with and without logQ correction and compare popularity bias.  
  - Deliverables: Model and bias analysis.  
  - Pass gate: Popularity bias measured with a stated metric.
- **Project 2: multi source candidate merging**  
  - Data: Any public interaction dataset  
  - Task: Build item-to-item, two-tower and popularity sources and tune merging quotas on recall and diversity.  
  - Deliverables: Merged retrieval and source-contribution analysis.  
  - Pass gate: Quotas tuned on validation data only.
- **Project 3: cold start item retrieval with content embeddings**  
  - Data: A catalog with item text or images and interaction history  
  - Task: Retrieve brand-new items using content embeddings and measure performance against collaborative-only retrieval.  
  - Deliverables: Evaluation on a new-item holdout.  
  - Pass gate: Items in the holdout have zero training interactions.

### 10 — CTR Prediction and Multi Objective Ranking Models

**Outcome:** Build the ranking models used in feeds and ads. Learning-to-rank concepts from search carry over; this module adds the feature-interaction and multi-task models used in recommendation.

**Lessons**

- `01-feature-interactions.md` — Feature interactions: factorization machines and field-aware variants
- `02-wide-and-deep-deepfm-and-dcn-v2.md` — Wide and Deep, DeepFM and DCN-v2
- `03-dlrm-style-architectures.md` — DLRM-style architectures: embedding tables and dense interaction layers
- `04-user-behavior-sequence-models.md` — User behavior sequence models: DIN and DIEN
- `05-multi-task-learning.md` — Multi-task learning: shared-bottom, MMoE and PLE
- `06-conversion-modeling-with-sample-selection-bias.md` — Conversion modeling with sample selection bias: ESMM-style approaches
- `07-calibration-for-ctr-models.md` — Calibration for CTR models: why probability quality matters for ads and blending
- `08-combining-objectives.md` — Combining objectives: value models and score blending
- `09-training-with-very-large-embedding-tables.md` — Training with very large embedding tables: sharding and TorchRec concepts
- `10-delayed-conversion-feedback-and-label-correction.md` — Delayed conversion feedback and label correction

**Hands-on projects**

- **Project 1: ctr model zoo on criteo or avazu**  
  - Data: Criteo display ads or Avazu (check licence)  
  - Task: Compare logistic regression, FM, DeepFM, DCN-v2 and a GBDT with log loss, AUC and calibration.  
  - Deliverables: Comparison with calibration plots.  
  - Pass gate: Time-based split and calibration reported alongside AUC.
- **Project 2: multi task click and conversion model**  
  - Data: A dataset with clicks and conversions such as Ali-CCP-style data  
  - Task: Compare separate models, shared-bottom, MMoE and ESMM on click and conversion metrics.  
  - Deliverables: Multi-task comparison.  
  - Pass gate: Conversion evaluated over the full impression space.
- **Project 3: calibration and blending study**  
  - Data: Outputs of the models above  
  - Task: Show how miscalibration distorts expected-value ranking and fix it with post-hoc calibration.  
  - Deliverables: Value-ranking comparison.  
  - Pass gate: Calibration fit and evaluation on separate data.

### 11 — Sequential Session Based and Generative Recommendation

**Outcome:** Model user histories as sequences and understand generative recommenders, with the evaluation traps that surround them.

**Lessons**

- `01-session-based-baselines.md` — Session-based baselines: nearest-neighbor sessions and why they are strong
- `02-recurrent-and-convolutional-sequence-models.md` — Recurrent and convolutional sequence models: GRU4Rec-style models
- `03-transformer-sequence-models.md` — Transformer sequence models: SASRec and BERT4Rec and replicability issues
- `04-long-user-histories.md` — Long user histories: sequence compression and retrieval of history
- `05-generative-recommenders.md` — Generative recommenders: sequential transduction and HSTU-style architectures
- `06-semantic-ids-and-generative-retrieval.md` — Semantic IDs and generative retrieval: TIGER-style quantized item tokens
- `07-llm-based-sequential-recommendation.md` — LLM-based sequential recommendation: prompt and fine-tuning approaches and their evaluation
- `08-evaluation-traps.md` — Evaluation traps: sampled metrics, leave-one-out leakage and global temporal splits
- `09-scaling-behavior.md` — Scaling behavior: what published scaling claims show and do not show

**Hands-on projects**

- **Project 1: sequential model comparison with honest baselines**  
  - Data: MovieLens-1M, Amazon Reviews and a session dataset such as Diginetica or Yoochoose  
  - Task: Compare session-kNN, GRU4Rec, SASRec and BERT4Rec with tuned baselines under a global temporal split and full-ranking metrics.  
  - Deliverables: Comparison with intervals and baseline-tuning effort recorded.  
  - Pass gate: Baselines tuned with the same budget as neural models.
- **Project 2: sampled vs full metrics demonstration**  
  - Data: Any recommendation dataset  
  - Task: Show how sampled evaluation changes model rankings relative to full-ranking evaluation.  
  - Deliverables: Ranking-inversion analysis.  
  - Pass gate: Several sample sizes tested.
- **Project 3: semantic id generative retrieval prototype**  
  - Data: A catalog with item content and interactions  
  - Task: Build item semantic IDs with residual quantization and train a small generative retriever; compare with two-tower retrieval including on cold items.  
  - Deliverables: Prototype and comparison.  
  - Pass gate: Cold-item holdout kept separate.

### 12 — Recommender Evaluation Rigor and Reproducibility

**Outcome:** Evaluate recommenders so conclusions hold up. Offline-versus-online evaluation basics, ranking metrics and popularity bias are introduced in Stage 5B; this module is about rigor.

**Lessons**

- `01-why-recommender-progress-is-hard-to-verify.md` — Why recommender progress is hard to verify: weak baselines and reproducibility results
- `02-dataset-selection.md` — Dataset selection: what MovieLens and other common datasets can and cannot show
- `03-splitting-protocols.md` — Splitting protocols: random, leave-one-out, global temporal and user-based
- `04-beyond-accuracy-metrics.md` — Beyond-accuracy metrics: coverage, novelty, serendipity, diversity and calibration of recommendations
- `05-statistical-testing-for-recommender-comparisons-and-multiple-comparison-problems.md` — Statistical testing for recommender comparisons and multiple-comparison problems
- `06-counterfactual-evaluation-for-slates.md` — Counterfactual evaluation for slates: inverse propensity, self-normalized and doubly robust estimators
- `07-simulators-for-recommender-research-and-their-validity-limits.md` — Simulators for recommender research and their validity limits
- `08-frameworks-and-tooling.md` — Frameworks and tooling: RecBole, Cornac, Elliot, implicit and TorchRec, with maintenance checks
- `09-user-studies-and-satisfaction-surveys-alongside-logs.md` — User studies and satisfaction surveys alongside logs

**Hands-on projects**

- **Project 1: baseline strength audit**  
  - Data: Three public datasets and one recent published neural model  
  - Task: Tune simple baselines properly and test whether the published model still wins.  
  - Deliverables: Audit report.  
  - Pass gate: Equal tuning budgets and multiple seeds.
- **Project 2: slate off policy evaluation study**  
  - Data: Open Bandit Dataset (ZOZO) and a simulator with known policy values  
  - Task: Estimate new-policy value with IPS, SNIPS and doubly robust estimators and compare with ground truth.  
  - Deliverables: Estimator bias and variance analysis.  
  - Pass gate: Ground truth from simulation.
- **Project 3: beyond accuracy evaluation suite**  
  - Data: Recommendations from earlier modules  
  - Task: Build a metric suite for coverage, novelty, diversity and calibration and show trade-offs against accuracy.  
  - Deliverables: Tested metric library and trade-off plots.  
  - Pass gate: Metrics validated on constructed examples.

### 13 — Fairness Diversity and Marketplace Effects

**Outcome:** Reason about the effect of recommendation and ranking on providers, users and the whole ecosystem. General responsible-AI methods are covered later in G12.

**Lessons**

- `01-whose-interests-count.md` — Whose interests count: users, providers, platforms and society
- `02-exposure-fairness.md` — Exposure fairness: amortized and group-based fairness for items and providers
- `03-user-side-fairness.md` — User-side fairness: performance gaps across user groups
- `04-popularity-bias-and-its-mitigation.md` — Popularity bias and its mitigation: re-weighting and re-ranking
- `05-diversity-re-ranking.md` — Diversity re-ranking: maximal marginal relevance and determinantal point processes
- `06-filter-bubbles-and-feedback-loops.md` — Filter bubbles and feedback loops: simulation and measurement
- `07-two-sided-marketplace-dynamics.md` — Two-sided marketplace dynamics: supply, demand and creator incentives
- `08-long-term-effects.md` — Long-term effects: retention, satisfaction and metric gaming
- `09-transparency-and-user-control.md` — Transparency and user control: explanations, settings and regulatory expectations to be checked

**Hands-on projects**

- **Project 1: exposure fairness reranker**  
  - Data: A dataset with provider information such as music or marketplace data  
  - Task: Build a fair-exposure re-ranker and measure the accuracy-exposure trade-off.  
  - Deliverables: Re-ranker and trade-off curve.  
  - Pass gate: Group definitions and metrics fixed before experiments.
- **Project 2: feedback loop simulation**  
  - Data: A recommender simulator you build  
  - Task: Simulate repeated retraining and measure diversity, popularity concentration and satisfaction over time under different policies.  
  - Deliverables: Long-run simulation analysis.  
  - Pass gate: Many simulation runs with intervals.
- **Project 3: diversity reranking comparison**  
  - Data: Recommendations from an earlier module  
  - Task: Compare MMR and DPP re-ranking on diversity, accuracy and user-study-style proxies.  
  - Deliverables: Comparison.  
  - Pass gate: Diversity defined with an explicit similarity measure.

### 14 — User Modeling and Personalization Algorithms

**Outcome:** Develop and test new personalization ideas with research-grade rigor.

**Lessons**

- `01-user-representation-learning.md` — User representation learning: long-term and short-term interests
- `02-context-aware-personalization.md` — Context-aware personalization: time, device and situation
- `03-preference-elicitation-and-onboarding.md` — Preference elicitation and onboarding: active learning for cold-start users
- `04-cross-domain-and-transfer-learning-for-personalization.md` — Cross-domain and transfer learning for personalization
- `05-privacy-preserving-personalization.md` — Privacy-preserving personalization: on-device and federated approaches as an overview, with depth in G12
- `06-llm-based-personalization.md` — LLM-based personalization: user profiles, memory and LLM-as-recommender with evaluation
- `07-conversational-recommendation.md` — Conversational recommendation: dialogue policies and evaluation
- `08-explainable-recommendation.md` — Explainable recommendation: explanation quality and user trust
- `09-long-term-value-and-satisfaction-as-objectives.md` — Long-term value and satisfaction as objectives
- `10-research-method.md` — Research method: forming hypotheses, ablations and negative results in personalization

**Hands-on projects**

- **Project 1: onboarding preference elicitation study**  
  - Data: MovieLens and a simulated user population  
  - Task: Compare question-selection strategies for new users on recommendation quality after few answers.  
  - Deliverables: Strategy comparison.  
  - Pass gate: Simulated users validated against real rating behavior.
- **Project 2: llm recommender evaluation**  
  - Data: MovieLens or Amazon Reviews with item text  
  - Task: Compare a prompted LLM recommender with sequential and two-tower baselines under leakage checks, including memorization of public datasets.  
  - Deliverables: Evaluation with contamination analysis.  
  - Pass gate: Memorization test run before accepting results.
- **Project 3: research reproduction and extension**  
  - Data: One recent personalization paper with public data  
  - Task: Reproduce a headline result, extend it with one new ablation and report differences.  
  - Deliverables: Reproduction report.  
  - Pass gate: Every deviation from the paper recorded.

### 15 — Bandits Counterfactual Learning and RL for Personalization

**Outcome:** Learn from interaction data and explore safely. Contextual bandits and off-policy evaluation are introduced in Stage 5B and RL algorithms in G4; this module covers their use in personalization.

**Lessons**

- `01-contextual-bandits-in-production.md` — Contextual bandits in production: LinUCB, Thompson sampling and exploration budgets
- `02-slate-and-ranking-bandits.md` — Slate and ranking bandits
- `03-off-policy-learning.md` — Off-policy learning: counterfactual risk minimization and doubly robust learning
- `04-learning-from-logged-bandit-feedback-with-propensity-logging-requirements.md` — Learning from logged bandit feedback with propensity logging requirements
- `05-delayed-and-long-term-rewards-in-personalization.md` — Delayed and long-term rewards in personalization
- `06-reinforcement-learning-for-recommendation.md` — Reinforcement learning for recommendation: slate-based value methods and their pitfalls
- `07-simulators-and-sim-to-real-gaps-for-recommendation-research.md` — Simulators and sim-to-real gaps for recommendation research
- `08-safe-exploration.md` — Safe exploration: constraints, guardrails and rollback
- `09-open-bandit-pipeline-and-experiment-tooling.md` — Open Bandit Pipeline and experiment tooling

**Hands-on projects**

- **Project 1: contextual bandit with logged data**  
  - Data: Open Bandit Dataset (ZOZO) or a simulator  
  - Task: Learn a policy offline from logged data and evaluate it with doubly robust estimates, then validate in simulation.  
  - Deliverables: Policy, estimates and validation.  
  - Pass gate: Logging propensities verified present and correct.
- **Project 2: exploration budget study**  
  - Data: A recommender simulator  
  - Task: Measure the short-term cost and long-term gain of different exploration rates.  
  - Deliverables: Cost-benefit curves.  
  - Pass gate: Long-run horizon long enough to show the benefit.
- **Project 3: safe exploration guardrails**  
  - Data: A simulator with a user-harm proxy  
  - Task: Add constraints that cap harm during exploration and measure the learning slowdown.  
  - Deliverables: Constraint-vs-learning analysis.  
  - Pass gate: Constraint violations reported.

### 16 — Matching Markets and Assignment Foundations

**Outcome:** Formulate and solve matching problems between users and resources. Shortest paths and graph algorithms are covered in Stage 3; operations-research optimization in depth is covered later in G8.

**Lessons**

- `01-matching-problem-types.md` — Matching problem types: bipartite, one-sided, two-sided and many-to-many
- `02-assignment-problem.md` — Assignment problem: Hungarian algorithm and min-cost flow in practice
- `03-stable-matching.md` — Stable matching: Gale-Shapley and its variants with preferences
- `04-capacity-and-fairness-constraints-in-matching.md` — Capacity and fairness constraints in matching
- `05-online-and-batched-matching.md` — Online and batched matching: dispatch windows and the value of waiting
- `06-reciprocal-recommendation.md` — Reciprocal recommendation: two-sided preferences and mutual interest
- `07-learning-preferences-for-matching.md` — Learning preferences for matching: estimating utilities from behavior
- `08-congestion-and-market-thickness.md` — Congestion and market thickness: why good recommendations can fail at scale
- `09-solving-with-or-tools-and-scipy-and-knowing-when-to-hand-over-to-g8-methods.md` — Solving with OR-Tools and SciPy and knowing when to hand over to G8 methods

**Hands-on projects**

- **Project 1: dispatch matching simulator**  
  - Data: NYC TLC trip records to generate demand and a supply simulator  
  - Task: Compare greedy, batched Hungarian and learned-value matching on wait time and utilization.  
  - Deliverables: Simulator and policy comparison.  
  - Pass gate: Simulation parameters documented and varied.
- **Project 2: stable matching and incentives**  
  - Data: Synthetic preference data  
  - Task: Implement Gale-Shapley, test stability and study how preference noise changes outcomes.  
  - Deliverables: Implementation and analysis.  
  - Pass gate: Stability verified by an independent checker.
- **Project 3: capacity constrained assignment**  
  - Data: A support-routing or expert-finding scenario you build  
  - Task: Solve with min-cost flow including capacity and fairness constraints and compare with a greedy baseline.  
  - Deliverables: Solver and comparison.  
  - Pass gate: Constraint satisfaction checked automatically.

### 17 — Job Candidate and Resource Matching Systems

**Outcome:** Build matching systems for jobs, candidates and requests, with the legal and fairness questions that come with them.

**Lessons**

- `01-document-understanding-for-matching.md` — Document understanding for matching: resume and job-posting parsing using G2 extraction
- `02-skills-and-taxonomy-normalization.md` — Skills and taxonomy normalization
- `03-two-sided-scoring.md` — Two-sided scoring: relevance, qualification and likelihood of response
- `04-candidate-job-retrieval-and-ranking-pipelines.md` — Candidate-job retrieval and ranking pipelines
- `05-hiring-specific-fairness-and-legal-considerations.md` — Hiring-specific fairness and legal considerations: adverse-impact analysis and applicable law to be checked
- `06-explanations-and-recourse-for-candidates-and-recruiters.md` — Explanations and recourse for candidates and recruiters
- `07-request-to-resource-matching.md` — Request-to-resource matching: support routing, expert finding and task allocation
- `08-spam-gaming-and-abuse-in-marketplaces.md` — Spam, gaming and abuse in marketplaces
- `09-evaluating-matching.md` — Evaluating matching: match quality, downstream outcomes and delayed labels

**Hands-on projects**

- **Project 1: resume job matching pipeline**  
  - Data: A public resume and job-posting dataset with licence checked, or synthetic data you generate  
  - Task: Build parsing, normalization, retrieval and ranking and evaluate with a graded judgment set you create.  
  - Deliverables: Pipeline and evaluation.  
  - Pass gate: No real personal data used without consent.
- **Project 2: adverse impact audit**  
  - Data: Synthetic candidates with protected attributes injected  
  - Task: Audit selection rates and score distributions across groups and test mitigation methods.  
  - Deliverables: Audit and mitigation trade-offs.  
  - Pass gate: Metrics and thresholds defined before analysis.
- **Project 3: support routing system**  
  - Data: A public ticket dataset such as CFPB complaints  
  - Task: Route tickets to teams with capacity limits and measure resolution-proxy metrics.  
  - Deliverables: Router and capacity simulation.  
  - Pass gate: Capacity limits enforced in evaluation.

### 18 — Auctions Ads Ranking and Budget Pacing

**Outcome:** Understand how ranked advertising decisions combine predictions, bids and budgets.

**Lessons**

- `01-ad-ranking.md` — Ad ranking: expected value from predicted click and conversion rates and bids
- `02-auction-basics.md` — Auction basics: first-price, second-price, generalized second-price and VCG
- `03-bid-shading-and-bidding-strategies-in-first-price-settings.md` — Bid shading and bidding strategies in first-price settings
- `04-budget-pacing-and-delivery-smoothing.md` — Budget pacing and delivery smoothing
- `05-calibration-requirements-for-auction-models.md` — Calibration requirements for auction models
- `06-bidding-and-allocation-as-constrained-optimization.md` — Bidding and allocation as constrained optimization
- `07-experimentation-in-ads.md` — Experimentation in ads: interference, budget effects and long-term advertiser outcomes
- `08-brand-safety-policy-and-quality-filters.md` — Brand safety, policy and quality filters

**Hands-on projects**

- **Project 1: auction simulator and bidding strategies**  
  - Data: iPinYou real-time bidding data (check terms) or a simulator you build  
  - Task: Simulate auctions and compare bidding strategies under budget constraints.  
  - Deliverables: Simulator and strategy comparison.  
  - Pass gate: Simulator validated on known equilibrium cases.
- **Project 2: budget pacing controller**  
  - Data: A simulated traffic stream with daily patterns  
  - Task: Build a pacing controller and measure delivery smoothness and spend accuracy.  
  - Deliverables: Controller and evaluation.  
  - Pass gate: Spend accuracy measured against the budget.
- **Project 3: calibration impact on auction revenue**  
  - Data: Predictions from module 10  
  - Task: Show how miscalibrated click predictions change auction outcomes and revenue.  
  - Deliverables: Revenue-impact analysis.  
  - Pass gate: Calibration manipulated under controlled conditions.

### 19 — Decision Systems Policies Constraints and Human Review

**Outcome:** Turn scores into decisions. Decision-focused evaluation basics are covered in G1, the human-in-the-loop pattern in Stage 5D and optimization methods later in G8; this module covers decision-system design.

**Lessons**

- `01-from-score-to-action.md` — From score to action: thresholds, ranking cut-offs and budgets
- `02-policy-layers.md` — Policy layers: business rules, constraints and exceptions around models
- `03-predict-then-optimize-in-practice-and-when-decision-focused-learning-is-worth-it.md` — Predict-then-optimize in practice and when decision-focused learning is worth it
- `04-queues-and-capacity.md` — Queues and capacity: designing review workloads
- `05-decision-logging-for-later-counterfactual-learning.md` — Decision logging for later counterfactual learning
- `06-simulating-policies-before-launch.md` — Simulating policies before launch
- `07-explaining-and-contesting-decisions.md` — Explaining and contesting decisions: auditability and appeal paths
- `08-long-term-effects-and-strategic-behavior-of-the-people-being-decided-about.md` — Long-term effects and strategic behavior of the people being decided about
- `09-decision-system-failures.md` — Decision-system failures: case studies and incident review

**Hands-on projects**

- **Project 1: score to decision policy with constraints**  
  - Data: Any scored dataset from earlier modules with costs you define  
  - Task: Design a policy with budget and fairness constraints and compare with a single-threshold baseline.  
  - Deliverables: Policy and simulation results.  
  - Pass gate: Assumptions and cost parameters recorded.
- **Project 2: decision logging for counterfactual learning**  
  - Data: A decision service you build  
  - Task: Log decisions with propensities and enough context to later evaluate alternative policies offline.  
  - Deliverables: Logging design and an offline-evaluation demonstration.  
  - Pass gate: Offline estimate matches a later randomized test in simulation.
- **Project 3: strategic behavior simulation**  
  - Data: A simulator where applicants can change features  
  - Task: Show how people game a scoring rule and compare robust designs.  
  - Deliverables: Simulation analysis.  
  - Pass gate: Gaming model documented.

### 20 — Operating Personalization Search and Matching Systems

**Outcome:** Run these systems reliably and measure them honestly. General MLOps, serving and monitoring are covered in Stage 5D; this module covers what is specific to ranking systems.

**Lessons**

- `01-latency-budgets-and-caching-for-ranked-results.md` — Latency budgets and caching for ranked results
- `02-feature-freshness-and-real-time-user-features.md` — Feature freshness and real-time user features
- `03-embedding-and-index-versioning.md` — Embedding and index versioning: compatible model and index rollouts
- `04-experimentation-platform-requirements.md` — Experimentation platform requirements: randomization, interference and guardrail metrics
- `05-north-star-and-guardrail-metric-design.md` — North-star and guardrail metric design
- `06-monitoring-ranking-systems.md` — Monitoring ranking systems: CTR drift, coverage collapse and silent regressions
- `07-privacy-consent-and-data-retention-for-behavioral-data-under-the-dpdp-act.md` — Privacy, consent and data retention for behavioral data under the DPDP Act
- `08-incident-handling-for-bad-rankings-and-recommendation-failures.md` — Incident handling for bad rankings and recommendation failures
- `09-cost-management-for-large-scale-retrieval-and-ranking.md` — Cost management for large-scale retrieval and ranking

**Hands-on projects**

- **Project 1: embedding and index version rollout**  
  - Data: A retrieval service you build  
  - Task: Roll out a new embedding model with index rebuild, dual serving and rollback and test that mismatched versions cannot be served.  
  - Deliverables: Rollout design and tests.  
  - Pass gate: Mismatched model and index is rejected by a test.
- **Project 2: ranking system monitoring with injected regressions**  
  - Data: Simulated production logs  
  - Task: Build monitoring for coverage, CTR drift and rank-distribution shift and test with injected regressions.  
  - Deliverables: Dashboard and detection tests.  
  - Pass gate: Every injected regression is detected within a stated delay.
- **Project 3: guardrail metric design workshop**  
  - Data: A product scenario of your choice  
  - Task: Define north-star and guardrail metrics and show with simulation how optimizing one metric harms another.  
  - Deliverables: Metric design document and simulation.  
  - Pass gate: Harm demonstrated by simulation.

### 21 — G6 Capstones

**Outcome:** integrate the search, recommendation, personalization-research and matching tracks in assessed, portfolio-quality work.

- **Capstone 1: search system from lexical to learned ranking** (uses Modules 01 to 07)  
  Build a search system over a real corpus with lexical, dense and hybrid retrieval, a learning-to-rank cascade, click-based evaluation and a cost model.
- **Capstone 2: recommender system with rigorous evaluation** (uses Modules 08 to 13)  
  Build a multi-stage recommender with retrieval, ranking, sequential models, an honest baseline audit, beyond-accuracy metrics and a fairness analysis.
- **Capstone 3: matching and decision platform** (uses Modules 15 to 19)  
  Build a two-sided matching and decision system with learned preferences, constraints, decision logging and offline counterfactual evaluation.
- **Capstone 4: personalization research project** (uses Modules 14, 15)  
  Carry out a personalization research project with a hypothesis, reproduction of a published result, ablations and an honest write-up including negative results.
- **Capstone 5: g6 readiness assessment** (uses All modules)  
  Written and practical assessment against the G6 completion gate.

## G6 completion gate

- Every search result uses judged queries, held-out query sets that were never used for tuning, graded metrics with confidence intervals and a strong lexical baseline.
- Every recommender result uses leakage-safe temporal or user-aware splits, full-ranking metrics (or documented corrections if sampling is unavoidable) and baselines tuned with the same effort as the new model.
- Every offline-counterfactual claim is validated against a simulator with known ground truth before it is applied to logged data.
- Every comparison reports significance across queries or users and per-segment results, not only an overall mean.
- All results reproduce from a lockfile, configs and logged seeds, with library versions, model versions and dataset licences recorded.
- Every matching or decision system has a documented fairness or adverse-impact analysis and an explanation or appeal path.
- At least one negative or inconclusive result per track is reported honestly, including a case where a simple baseline wins.
- The four specialist capstones are complete and the readiness assessment is passed.

## Audit and verification

**What was checked and the result**

- Structure: 20 specialist modules each have 6 to 12 lessons and at least one project; the tree contains 297 files and 43 folders, and these counts equal the counts computed from the curriculum data.
- Overlap with the Roadmap: all 181 lesson file names were compared against every lesson file name in `Roadmap.md`. Exact matches: 0. Near matches (similarity 0.80 or higher): 1 — `reinforcement-learning-for-recommendation` vs Roadmap `reinforcement-learning-for-reasoning` (0.83). Each was reviewed manually for topic overlap.
- Structural problems found by the build script: 0.
- Topic-level overlap check: the Roadmap text was searched for BM25, Lucene, FAISS, learning to rank, LambdaMART, DeepFM, Wide and Deep, DLRM, SASRec, GRU4Rec, session-based recommendation, implicit feedback, negative sampling, query understanding, inverted index, stable matching, the Hungarian algorithm, interleaving, click models, position bias and inverse propensity. None appear as lessons, so G6 teaches them for the first time. The Roadmap does contain a Stage 5B recommender and learning-to-rank module, bandits and off-policy evaluation, Stage 3 HNSW and a mini vector search engine, Stage 2D Elasticsearch and OpenSearch and embedding pipelines, which G6 references and extends and does not reteach.
- Verified by web search on the build date (2026-10-26): Krichene and Rendle's KDD 2020 paper shows sampled metrics can be inconsistent with exact metrics and recommends avoiding sampling; HSTU (Meta, ICML 2024) recasts recommendation as sequential transduction, and an independent critique says its public-dataset gains are modest; TIGER (NeurIPS 2023) uses RQ-VAE semantic IDs for generative retrieval; the Amazon Shopping Queries (ESCI) dataset has about 130 thousand queries and 2.6 million judgments in English, Japanese and Spanish with Exact, Substitute, Complement and Irrelevant labels.
- Reported but not confirmed: the authors' affiliation for TIGER differs between sources; searches did not confirm details or licences for Wayfair WANDS, Baidu-ULTR, KuaiRec and KuaiRand, ZOZO's Open Bandit Dataset and iPinYou, so each must be checked in the register; the maintenance status of RecBole (one 2025 audit found hidden defaults in its hyperparameter search), LightFM, Cornac, TF-Ranking, TorchRec and NVIDIA Merlin was not confirmed and is required in the register.
- Not verified: library, model and benchmark versions; dataset availability and licences (MS MARCO, MSLR, Istella, Criteo, Avazu, Kaggle competition terms and any resume data, which may contain personal information); and regulatory requirements for hiring and recommender transparency, which must be checked against current law before use.
- Not verified by execution: no code in this plan has been run. Project pass gates are acceptance criteria to be met when the projects are built.
- Safety note: modules 13, 17 and 19 involve fairness, hiring and decisions about people. Their projects use synthetic or consented data and must not be applied to real candidates or users without legal and ethical review.
- Repository safety: this build created only this file; no existing file or folder was created, changed or deleted by it.
