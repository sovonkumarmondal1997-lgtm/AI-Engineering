# Trustworthy ML — ML Specialization Roadmap

**Group 12 (G12)** of the specialization that follows Stage 5D of the [Roadmap](./Roadmap.md). It covers original categories **30 Responsible AI and ML Risk Engineering, 31 Adversarial Machine Learning and ML Security and 32 Federated and Privacy-Preserving Machine Learning**. The group's defining question is: *is the model safe, fair and private?* It follows G1 to G11: [`01_Classical and Applied ML.md`](./01_Classical%20and%20Applied%20ML.md), [`02_Deep Learning by Modality.md`](./02_Deep%20Learning%20by%20Modality.md), [`03_Generative and Foundation Models.md`](./03_Generative%20and%20Foundation%20Models.md), [`04_Agents and Sequential Decisions.md`](./04_Agents%20and%20Sequential%20Decisions.md), [`05_Time and Anomaly Modeling.md`](./05_Time%20and%20Anomaly%20Modeling.md), [`06_Personalization Search and Matching.md`](./06_Personalization%20Search%20and%20Matching.md), [`07_Statistical Reasoning.md`](./07_Statistical%20Reasoning.md), [`08_Graphs and Optimization.md`](./08_Graphs%20and%20Optimization.md), [`09_Industry Domain ML.md`](./09_Industry%20Domain%20ML.md), [`10_Efficient and Scalable Systems.md`](./10_Efficient%20and%20Scalable%20Systems.md), [`11_MLOps and Reliability.md`](./11_MLOps%20and%20Reliability.md).

## G12 summary

| Item | Count |
|---|---|
| Modules (including overview and capstones) | 16 |
| Lesson files | 134 |
| Hands-on project files (module projects, overview project and capstones) | 48 |
| Folders inside the G12 tree | 31 |
| Files inside the G12 tree | 221 |

| Original category | Modules |
|---|---|
| 30 Responsible AI and ML Risk Engineering | 01 to 05 |
| 31 Adversarial Machine Learning and ML Security | 06 to 09 |
| 32 Federated and Privacy-Preserving Machine Learning | 10 to 13 |
| Integration across all three | 14 |

## Scope and how G12 avoids repeating the Roadmap

These are **already learned** and are only referenced, never retaught. From **Stage 5D**: sensitive-data privacy and retention, model cards, dataset cards and audit trails, fairness monitoring and responsible deployment, and one lesson on ML-specific security (model extraction, adversarial inputs and data poisoning). From **Stage 5B**: SHAP and feature attribution, permutation importance, partial dependence, explanation stability and causal limits, counterfactual explanations and recourse, calibration, conformal prediction and abstention. From **Stages 2C and 2D**: PII detection, masking, tokenization and de-identification, encryption at rest and in transit and key management, row and column level access control, consent, purpose limitation and data residency, retention, deletion and GDPR compliance, regulatory controls and evidence design, and governance by design. From **earlier groups**: interpretable models and reason codes (G1), attribution sanity checks, shortcut learning, OOD detection and corruption robustness (G2), application-layer LLM security, prompt injection and guardrails (G3), agent security and sandboxing (G4), uncertainty and causal methods (G7), model-risk governance in finance and healthcare regulation (G9), and supply-chain signing, ML bills of materials, policy-as-code gates and poisoned-feedback defenses (G11).

**Boundaries with other groups** (so nothing overlaps): synthetic-data generation and data-centric AI belong to **G13** (module 13 only tests synthetic-data privacy claims); benchmark and evaluation-system design belongs to **G13**; edge and on-device deployment belongs to **G10**; domain-specific regulation for finance and healthcare is applied in **G9**.

| Roadmap topic already covered | Where G12 goes further |
|---|---|
| Model cards, dataset cards and audit trails (5D) | Module 01: harm taxonomies, impact assessments, risk registers, red lines and system cards |
| Fairness monitoring (5D) | Module 02: definitions and impossibility results, group definition problems, mitigation methods and trade-offs |
| SHAP, stability and recourse (5B) | Module 03: evaluating explanation faithfulness, user comprehension, fairwashing and language-model explanations |
| RLHF and constitutional AI (5C), LLM app security (G3) | Module 04: model-level safety evaluation, red-team method, refusal calibration and safety cases |
| Regulatory controls and evidence design (2D), governance (5D, G9) | Module 05: AI-specific regulation, standards, algorithmic audits and automated compliance evidence |
| Adversarial inputs overview (5D), OOD and corruptions (G2) | Module 06: threat models, evasion attacks, adaptive evaluation, adversarial training and certified robustness |
| Data-poisoning overview (5D), signing (G11) | Module 07: backdoors, clean-label and language-model poisoning, detection and defenses |
| Model extraction overview (5D), prompt extraction (G3) | Module 08: membership inference, memorization, extraction, watermarking and privacy auditing |
| ML-specific security and ops (5D, 2E) | Module 09: ML threat modeling, security testing, detection in production and purple teaming |
| PII masking and de-identification (2C, 2D) | Module 10: differential privacy: guarantees, DP-SGD, accounting and auditing |
| Federated queries (2C), sensitive data (5D) | Module 11: federated learning systems, non-IID data, secure aggregation and attacks |
| Encryption and key management (2D) | Module 12: secure computation, homomorphic encryption, confidential computing and technique selection |
| Retention, deletion and GDPR (2C, 2D) | Module 13: model-level privacy risk, machine unlearning, anonymization limits and breach response |
| Governance and audit (5D, G9, G11) | Module 14: assurance cases, trade-offs among trust goals and failure case studies |

## G12 — Trustworthy ML

**Defining question:** Is the model safe, fair and private?

```text
ML Specialization/
└── G12 — Trustworthy ML/
    ├── 00-G12-Overview/
    │   ├── Projects/
    │   │   ├── 01-g12-trust-evaluation-and-isolated-attack-lab-bootstrap.md
    │   │   └── README.md
    │   ├── 01-g12-scope-and-boundaries-with-stages-2d-5b-5d-and-other-groups.md
    │   ├── 02-prerequisite-map-from-the-roadmap.md
    │   ├── 03-ethics-and-safe-handling-rules.md
    │   ├── 04-tooling-and-legal-source-register.md
    │   ├── 05-evaluation-and-reporting-standards.md
    │   ├── 06-completion-gate.md
    │   ├── README.md
    │   └── learning-plan.md
    ├── 01-Responsible-AI-Foundations-Harms-and-Risk-Assessment/
    │   ├── Projects/
    │   │   ├── 01-harm-and-stakeholder-analysis-for-three-systems.md
    │   │   ├── 02-algorithmic-impact-assessment-document.md
    │   │   ├── 03-system-card-for-an-end-to-end-system.md
    │   │   └── README.md
    │   ├── 01-harm-taxonomies.md
    │   ├── 02-sociotechnical-framing.md
    │   ├── 03-stakeholder-mapping-and-participatory-methods.md
    │   ├── 04-impact-assessments.md
    │   ├── 05-risk-frameworks.md
    │   ├── 06-risk-registers.md
    │   ├── 07-red-lines-and-go-or-no-go-criteria.md
    │   ├── 08-documentation-beyond-the-model-and-dataset-cards-of-stage-5d.md
    │   ├── 09-roles-and-review-bodies.md
    │   ├── 10-india-context.md
    │   └── README.md
    ├── 02-Fairness-Measurement-and-Mitigation/
    │   ├── Projects/
    │   │   ├── 01-fairness-audit-with-uncertainty.md
    │   │   ├── 02-mitigation-comparison-and-trade-off-curves.md
    │   │   ├── 03-proxy-and-missing-attribute-analysis.md
    │   │   └── README.md
    │   ├── 01-fairness-definitions.md
    │   ├── 02-impossibility-results.md
    │   ├── 03-defining-groups.md
    │   ├── 04-india-specific-fairness-questions.md
    │   ├── 05-measurement-uncertainty.md
    │   ├── 06-pre-processing-mitigation.md
    │   ├── 07-in-processing-mitigation.md
    │   ├── 08-post-processing-mitigation.md
    │   ├── 09-fairness-under-distribution-shift-and-over-time.md
    │   ├── 10-fairness-for-language-and-generative-models.md
    │   ├── 11-documenting-fairness-decisions.md
    │   └── README.md
    ├── 03-Explanation-Quality-Faithfulness-and-Accountability/
    │   ├── Projects/
    │   │   ├── 01-explanation-faithfulness-benchmark.md
    │   │   ├── 02-explanation-comprehension-study.md
    │   │   ├── 03-fairwashing-demonstration.md
    │   │   └── README.md
    │   ├── 01-what-an-explanation-is-for.md
    │   ├── 02-evaluating-explanations.md
    │   ├── 03-explanation-disagreement.md
    │   ├── 04-explanations-for-decision-subjects.md
    │   ├── 05-explanation-user-studies.md
    │   ├── 06-explanation-misuse.md
    │   ├── 07-language-model-explanations.md
    │   ├── 08-legal-and-regulatory-expectations-for-explanations-to-be-read-from-primary-sources.md
    │   ├── 09-when-to-avoid-post-hoc-explanation.md
    │   └── README.md
    ├── 04-AI-Safety-Evaluation-and-Red-Teaming-of-Models/
    │   ├── Projects/
    │   │   ├── 01-structured-red-team-exercise.md
    │   │   ├── 02-refusal-calibration-evaluation.md
    │   │   ├── 03-safety-case-for-a-deployment.md
    │   │   └── README.md
    │   ├── 01-model-behavior-risks.md
    │   ├── 02-red-teaming-methodology.md
    │   ├── 03-safety-benchmarks.md
    │   ├── 04-refusal-calibration.md
    │   ├── 05-jailbreak-robustness-evaluation.md
    │   ├── 06-evaluating-dangerous-capability-risks-at-the-policy-level.md
    │   ├── 07-safety-cases-and-frontier-safety-frameworks-published-by-ai-developers-read-from-primary-sources.md
    │   ├── 08-monitoring-and-incident-reporting-for-deployed-models.md
    │   ├── 09-responsible-disclosure-and-handling-sensitive-findings.md
    │   ├── 10-alignment-evaluation.md
    │   └── README.md
    ├── 05-AI-Governance-Regulation-and-Assurance/
    │   ├── Projects/
    │   │   ├── 01-regulatory-mapping-for-a-product.md
    │   │   ├── 02-algorithmic-audit-of-a-public-model.md
    │   │   ├── 03-compliance-evidence-automation.md
    │   │   └── README.md
    │   ├── 01-regulatory-landscape.md
    │   ├── 02-data-protection-law-for-ml.md
    │   ├── 03-standards-and-assurance.md
    │   ├── 04-algorithmic-audits.md
    │   ├── 05-documentation-and-traceability-required-for-high-risk-systems.md
    │   ├── 06-post-market-monitoring-and-incident-reporting-duties.md
    │   ├── 07-procurement-and-vendor-assurance-for-third-party-models.md
    │   ├── 08-liability-and-accountability.md
    │   ├── 09-producing-compliance-evidence-from-the-ml-platform-using-the-policy-as-code-of-g11.md
    │   └── README.md
    ├── 06-Adversarial-Examples-and-Robustness-Evaluation/
    │   ├── Projects/
    │   │   ├── 01-pgd-attack-and-adversarial-training-study.md
    │   │   ├── 02-broken-defense-reproduction.md
    │   │   ├── 03-certified-robustness-with-randomized-smoothing.md
    │   │   └── README.md
    │   ├── 01-threat-models.md
    │   ├── 02-gradient-based-evasion-attacks.md
    │   ├── 03-black-box-attacks.md
    │   ├── 04-physical-world-and-patch-attacks-and-their-limits.md
    │   ├── 05-adversarial-training-and-its-costs.md
    │   ├── 06-certified-robustness.md
    │   ├── 07-evaluating-defenses-correctly.md
    │   ├── 08-robustness-benchmarks-and-standardized-evaluation-with-autoattack-style-suites.md
    │   ├── 09-adversarial-examples-beyond-images.md
    │   ├── 10-robustness-accuracy-trade-offs-and-when-robustness-is-worth-its-cost.md
    │   └── README.md
    ├── 07-Data-Poisoning-Backdoors-and-Training-Time-Attacks/
    │   ├── Projects/
    │   │   ├── 01-backdoor-injection-and-detection-lab.md
    │   │   ├── 02-poisoning-rate-vs-damage-study.md
    │   │   ├── 03-third-party-model-behavior-audit.md
    │   │   └── README.md
    │   ├── 01-poisoning-goals.md
    │   ├── 02-backdoors-and-trojans.md
    │   ├── 03-clean-label-and-data-supply-attacks-on-web-scale-and-crowdsourced-data.md
    │   ├── 04-poisoning-language-models.md
    │   ├── 05-detection.md
    │   ├── 06-defenses.md
    │   ├── 07-evaluating-defenses-against-adaptive-attackers.md
    │   ├── 08-pretrained-model-risks.md
    │   ├── 09-differential-privacy-and-certified-defenses-as-limits-on-poisoning.md
    │   └── README.md
    ├── 08-Privacy-Attacks-Model-Extraction-and-Inference-Threats/
    │   ├── Projects/
    │   │   ├── 01-membership-inference-audit.md
    │   │   ├── 02-language-model-memorization-measurement.md
    │   │   ├── 03-model-extraction-and-query-monitoring.md
    │   │   └── README.md
    │   ├── 01-what-models-leak.md
    │   ├── 02-membership-inference.md
    │   ├── 03-attribute-inference-and-model-inversion.md
    │   ├── 04-training-data-extraction-from-language-models-and-measuring-memorization.md
    │   ├── 05-model-extraction-and-stealing-through-query-access.md
    │   ├── 06-defenses.md
    │   ├── 07-model-watermarking-and-fingerprinting-for-ownership-claims.md
    │   ├── 08-attacks-on-embeddings-and-retrieval-systems.md
    │   ├── 09-privacy-auditing.md
    │   └── README.md
    ├── 09-ML-Security-Engineering-Threat-Modeling-and-Red-Team-Operations/
    │   ├── Projects/
    │   │   ├── 01-ml-system-threat-model-and-attack-tree.md
    │   │   ├── 02-purple-team-exercise-on-your-own-system.md
    │   │   ├── 03-ml-security-testing-in-ci.md
    │   │   └── README.md
    │   ├── 01-threat-modeling-for-ml-systems.md
    │   ├── 02-knowledge-bases.md
    │   ├── 03-secure-ml-development-lifecycle.md
    │   ├── 04-security-testing-tools.md
    │   ├── 05-detecting-attacks-in-production.md
    │   ├── 06-incident-response-for-ml-attacks-and-coordination-with-security-teams.md
    │   ├── 07-purple-teaming.md
    │   ├── 08-vulnerability-disclosure-and-bug-bounty-practice-for-ml-systems.md
    │   ├── 09-security-metrics-and-reporting-to-leadership.md
    │   └── README.md
    ├── 10-Differential-Privacy-Foundations-and-Practice/
    │   ├── Projects/
    │   │   ├── 01-dp-sgd-utility-privacy-frontier.md
    │   │   ├── 02-dp-mechanisms-from-scratch-with-tests.md
    │   │   ├── 03-dp-implementation-audit.md
    │   │   └── README.md
    │   ├── 01-the-definition.md
    │   ├── 02-basic-mechanisms.md
    │   ├── 03-sensitivity-and-clipping.md
    │   ├── 04-composition-and-privacy-accounting.md
    │   ├── 05-dp-sgd.md
    │   ├── 06-utility-under-privacy.md
    │   ├── 07-differentially-private-statistics-and-tabular-models.md
    │   ├── 08-local-central-and-shuffle-models-and-real-deployments.md
    │   ├── 09-pitfalls.md
    │   ├── 10-empirical-privacy-auditing-of-dp-implementations.md
    │   └── README.md
    ├── 11-Federated-Learning-Systems/
    │   ├── Projects/
    │   │   ├── 01-federated-learning-benchmark-with-non-iid-data.md
    │   │   ├── 02-cross-silo-healthcare-style-simulation.md
    │   │   ├── 03-gradient-inversion-risk-study.md
    │   │   └── README.md
    │   ├── 01-cross-device-and-cross-silo-settings-and-when-each-applies.md
    │   ├── 02-federated-averaging-and-the-effect-of-non-identical-client-data.md
    │   ├── 03-client-drift-remedies.md
    │   ├── 04-communication-efficiency.md
    │   ├── 05-personalization.md
    │   ├── 06-secure-aggregation.md
    │   ├── 07-federated-learning-with-differential-privacy.md
    │   ├── 08-system-heterogeneity.md
    │   ├── 09-attacks-on-federated-systems.md
    │   ├── 10-frameworks.md
    │   ├── 11-evaluation.md
    │   └── README.md
    ├── 12-Cryptographic-and-Hardware-Privacy-Techniques/
    │   ├── Projects/
    │   │   ├── 01-encrypted-inference-feasibility-study.md
    │   │   ├── 02-private-set-intersection-for-record-matching.md
    │   │   ├── 03-privacy-technique-decision-memo.md
    │   │   └── README.md
    │   ├── 01-threat-models-for-private-computation.md
    │   ├── 02-secret-sharing-and-secure-multi-party-computation-basics.md
    │   ├── 03-homomorphic-encryption.md
    │   ├── 04-private-set-intersection-and-private-data-joins.md
    │   ├── 05-trusted-execution-environments-and-confidential-computing-for-cpus-and-gpus.md
    │   ├── 06-zero-knowledge-proofs-for-ml.md
    │   ├── 07-private-inference-and-encrypted-retrieval.md
    │   ├── 08-data-clean-rooms-and-privacy-preserving-analytics-products.md
    │   ├── 09-decision-framework.md
    │   └── README.md
    ├── 13-Privacy-Engineering-and-Privacy-Risk-Management-for-ML/
    │   ├── Projects/
    │   │   ├── 01-reidentification-risk-study.md
    │   │   ├── 02-machine-unlearning-evaluation.md
    │   │   ├── 03-synthetic-data-privacy-test.md
    │   │   └── README.md
    │   ├── 01-privacy-by-design-for-ml-systems.md
    │   ├── 02-privacy-risk-assessment-for-models.md
    │   ├── 03-anonymization-limits.md
    │   ├── 04-machine-unlearning.md
    │   ├── 05-deletion-requests-and-trained-models.md
    │   ├── 06-synthetic-data-and-privacy-claims.md
    │   ├── 07-privacy-budgets-as-governance.md
    │   ├── 08-privacy-breach-response-for-ml-systems-and-notification-duties-to-be-confirmed-from-primary-sources.md
    │   ├── 09-privacy-in-on-device-and-edge-ml-with-links-to-g10.md
    │   └── README.md
    ├── 14-Trustworthy-ML-Practice-Integration-and-Assurance-Cases/
    │   ├── Projects/
    │   │   ├── 01-assurance-case-for-a-high-stakes-model.md
    │   │   ├── 02-trade-off-analysis-across-trust-goals.md
    │   │   ├── 03-trust-failure-case-study-library.md
    │   │   └── README.md
    │   ├── 01-assurance-cases.md
    │   ├── 02-tensions-between-goals.md
    │   ├── 03-trustworthiness-requirements-in-the-project-lifecycle.md
    │   ├── 04-release-gates-for-trust-properties-and-exception-processes.md
    │   ├── 05-review-boards-and-independent-challenge.md
    │   ├── 06-incident-learning.md
    │   ├── 07-case-studies.md
    │   ├── 08-communicating-limits-and-risks-to-users-and-the-public.md
    │   ├── 09-building-a-culture-that-surfaces-concerns.md
    │   └── README.md
    ├── 15-G12-Capstones/
    │   ├── 01-responsible-ai-review-of-a-high-stakes-system.md
    │   ├── 02-model-safety-and-red-team-report.md
    │   ├── 03-adversarial-robustness-and-security-evaluation.md
    │   ├── 04-privacy-preserving-training-system.md
    │   ├── 05-g12-readiness-assessment.md
    │   └── README.md
    └── README.md
```

### 00 — G12 Overview

**Purpose:** the single authoritative plan for G12 with scope, boundaries, prerequisite map, ethics and safe-handling rules, tooling register, evaluation standards and completion gate.

- `01-g12-scope-and-boundaries-with-stages-2d-5b-5d-and-other-groups.md` — what G12 teaches and what it leaves to other stages and groups.
- `02-prerequisite-map-from-the-roadmap.md` — Roadmap lessons assumed for each G12 module, named precisely.
- `03-ethics-and-safe-handling-rules.md` — rules for attack, red-team, privacy and human-subject work: isolated environments, owned or synthetic data, consent, disclosure and what not to publish.
- `04-tooling-and-legal-source-register.md` — every library with version, licence and maintenance status, and every legal or standards document with issuer, version, date accessed and the passage relied on.
- `05-evaluation-and-reporting-standards.md` — uncertainty reporting for trust metrics, adaptive-attack rules, privacy-audit rules and report template.
- `06-completion-gate.md` — measurable criteria to finish G12.
- `learning-plan.md` — recommended order, three tracks and the order in which to learn attacks and defenses safely.

**Project 1: g12 trust evaluation and isolated attack lab bootstrap**  
- Data: small public datasets and models you train yourself.  
- Task: build a reproducible, network-isolated lab with pinned tooling, a trust-metrics harness (subgroup metrics with intervals, robust accuracy, membership-inference and privacy-budget reporting) and a written safe-handling checklist.  
- Deliverables: lockfile, harness with tests, isolation configuration and checklist.  
- Pass gate: a clean machine reproduces the tests from the lockfile, and the harness refuses to run an attack module outside the isolated configuration.

### 01 — Responsible AI Foundations Harms and Risk Assessment

**Outcome:** Identify who can be harmed by a system, how, and how severe it is, before building. Model cards, audit trails and fairness monitoring are covered in Stage 5D, financial model-risk governance in G9 and healthcare regulation in G9; this module is the general, cross-domain foundation.

**Lessons**

- `01-harm-taxonomies.md` — Harm taxonomies: allocative, quality-of-service, representational, safety and societal harms
- `02-sociotechnical-framing.md` — Sociotechnical framing: models inside institutions, incentives and human processes
- `03-stakeholder-mapping-and-participatory-methods.md` — Stakeholder mapping and participatory methods: including the people who are decided about
- `04-impact-assessments.md` — Impact assessments: algorithmic impact and data-protection impact assessments for ML
- `05-risk-frameworks.md` — Risk frameworks: NIST AI RMF, ISO/IEC 42001 and ISO/IEC 23894 as tools rather than checklists
- `06-risk-registers.md` — Risk registers: severity, likelihood, detectability and residual risk for ML systems
- `07-red-lines-and-go-or-no-go-criteria.md` — Red lines and go or no-go criteria: deciding not to build or deploy
- `08-documentation-beyond-the-model-and-dataset-cards-of-stage-5d.md` — Documentation beyond the model and dataset cards of Stage 5D: system cards that describe the whole sociotechnical system and its limits
- `09-roles-and-review-bodies.md` — Roles and review bodies: ethics boards, model owners and escalation paths
- `10-india-context.md` — India context: the MeitY AI governance guidelines and sector regulators, to be read from primary sources

**Hands-on projects**

- **Project 1: harm and stakeholder analysis for three systems**  
  - Data: Three public case descriptions you choose, such as a loan model, a hiring screen and a content recommender  
  - Task: Map stakeholders, enumerate harms with severity and likelihood and recommend design changes or a no-go.  
  - Deliverables: Three analyses and a risk register.  
  - Pass gate: At least one analysis recommends not deploying, with reasoning.
- **Project 2: algorithmic impact assessment document**  
  - Data: A model from earlier groups  
  - Task: Write a full impact assessment including affected groups, data sources, failure modes, mitigations and monitoring.  
  - Deliverables: Assessment document reviewed against a rubric.  
  - Pass gate: Every mitigation maps to a test or monitor.
- **Project 3: system card for an end to end system**  
  - Data: An end-to-end system from earlier groups  
  - Task: Write a system card covering purpose, users, data, models, human oversight, known failure modes, evaluations and limits, beyond what a model card records.  
  - Deliverables: System card.  
  - Pass gate: Every claim verified by an executed evaluation or marked unknown.

### 02 — Fairness Measurement and Mitigation

**Outcome:** Measure and reduce unfair outcomes with an honest account of trade-offs and uncertainty. Fairness monitoring in deployment is introduced in Stage 5D, and counterfactual explanations and recourse in Stage 5B.

**Lessons**

- `01-fairness-definitions.md` — Fairness definitions: demographic parity, equal opportunity, equalized odds, calibration within groups and individual fairness
- `02-impossibility-results.md` — Impossibility results: why definitions conflict and what that means for choosing one
- `03-defining-groups.md` — Defining groups: missing sensitive attributes, proxies, intersectionality and legal limits on using attributes
- `04-india-specific-fairness-questions.md` — India-specific fairness questions: language, region, religion, caste and gender, and data availability limits
- `05-measurement-uncertainty.md` — Measurement uncertainty: confidence intervals for subgroup metrics and small-group problems
- `06-pre-processing-mitigation.md` — Pre-processing mitigation: reweighing and resampling
- `07-in-processing-mitigation.md` — In-processing mitigation: constrained optimization and adversarial debiasing with Fairlearn-style reductions
- `08-post-processing-mitigation.md` — Post-processing mitigation: group-specific thresholds and their legal and ethical implications
- `09-fairness-under-distribution-shift-and-over-time.md` — Fairness under distribution shift and over time: feedback effects
- `10-fairness-for-language-and-generative-models.md` — Fairness for language and generative models: bias benchmarks and their validity limits
- `11-documenting-fairness-decisions.md` — Documenting fairness decisions: what was chosen, why and what was given up

**Hands-on projects**

- **Project 1: fairness audit with uncertainty**  
  - Data: A public tabular decision dataset such as a census income or credit dataset  
  - Task: Compute subgroup metrics with confidence intervals, test several definitions and show where they conflict.  
  - Deliverables: Audit report.  
  - Pass gate: Every subgroup metric reported with an interval and sample size.
- **Project 2: mitigation comparison and trade off curves**  
  - Data: The same dataset  
  - Task: Compare pre-, in- and post-processing mitigations on accuracy and fairness metrics across several models.  
  - Deliverables: Trade-off curves with intervals.  
  - Pass gate: Test data never used in mitigation fitting.
- **Project 3: proxy and missing attribute analysis**  
  - Data: A dataset with sensitive attributes removed in some versions  
  - Task: Test how well attributes can be inferred from other features and how that affects audit validity.  
  - Deliverables: Analysis and recommendations.  
  - Pass gate: Inference error propagated into audit uncertainty.

### 03 — Explanation Quality Faithfulness and Accountability

**Outcome:** Judge whether explanations are trustworthy and useful to the people who receive them. SHAP, permutation importance, partial dependence, explanation stability and counterfactual recourse are covered in Stage 5B, and attribution sanity checks for deep networks in G2.

**Lessons**

- `01-what-an-explanation-is-for.md` — What an explanation is for: debugging, auditing, contesting a decision and building trust
- `02-evaluating-explanations.md` — Evaluating explanations: faithfulness tests such as deletion and retraining-based removal, and stability
- `03-explanation-disagreement.md` — Explanation disagreement: why methods give different answers and how to report it
- `04-explanations-for-decision-subjects.md` — Explanations for decision subjects: reason codes, recourse and comprehension
- `05-explanation-user-studies.md` — Explanation user studies: designing and analyzing human evaluations
- `06-explanation-misuse.md` — Explanation misuse: fairwashing and post-hoc rationalization
- `07-language-model-explanations.md` — Language-model explanations: self-explanations and chain-of-thought faithfulness evidence
- `08-legal-and-regulatory-expectations-for-explanations-to-be-read-from-primary-sources.md` — Legal and regulatory expectations for explanations, to be read from primary sources
- `09-when-to-avoid-post-hoc-explanation.md` — When to avoid post-hoc explanation: choosing interpretable models from G1 instead

**Hands-on projects**

- **Project 1: explanation faithfulness benchmark**  
  - Data: Tabular and image tasks with known ground-truth feature importance via synthetic construction  
  - Task: Compare several explanation methods on faithfulness, stability and agreement with ground truth.  
  - Deliverables: Benchmark and recommendations.  
  - Pass gate: Ground truth known by construction.
- **Project 2: explanation comprehension study**  
  - Data: Reason-code and recourse presentations for a lending-style decision  
  - Task: Test with a small participant group whether people understand and can act on each presentation.  
  - Deliverables: Study report.  
  - Pass gate: Participants consent and data are anonymized.
- **Project 3: fairwashing demonstration**  
  - Data: A biased model and a post-hoc explainer  
  - Task: Show how explanations can hide a model's reliance on a sensitive proxy and how to detect it.  
  - Deliverables: Demonstration and detection test.  
  - Pass gate: Hidden reliance verified by an independent analysis.

### 04 — AI Safety Evaluation and Red Teaming of Models

**Outcome:** Evaluate foundation-model behavior for misuse and failure with a rigorous, safe process. Application-layer LLM security is covered in G3, agent security in G4 and RLHF and constitutional methods in Stage 5C; this module is model-level safety evaluation, taught at the level of method and policy, not operational detail for causing harm.

**Lessons**

- `01-model-behavior-risks.md` — Model behavior risks: harmful content, deception, sycophancy, over-refusal and unsafe tool use
- `02-red-teaming-methodology.md` — Red-teaming methodology: scoping, rules of engagement, manual and automated approaches
- `03-safety-benchmarks.md` — Safety benchmarks: what they measure, contamination and saturation
- `04-refusal-calibration.md` — Refusal calibration: measuring harm avoided against helpfulness lost
- `05-jailbreak-robustness-evaluation.md` — Jailbreak robustness evaluation: categories, attack success rates and variance
- `06-evaluating-dangerous-capability-risks-at-the-policy-level.md` — Evaluating dangerous-capability risks at the policy level: threat-model-driven evaluations and expert review
- `07-safety-cases-and-frontier-safety-frameworks-published-by-ai-developers-read-from-primary-sources.md` — Safety cases and frontier safety frameworks published by AI developers, read from primary sources
- `08-monitoring-and-incident-reporting-for-deployed-models.md` — Monitoring and incident reporting for deployed models
- `09-responsible-disclosure-and-handling-sensitive-findings.md` — Responsible disclosure and handling sensitive findings
- `10-alignment-evaluation.md` — Alignment evaluation: honesty, instruction hierarchy and robustness to manipulation

**Hands-on projects**

- **Project 1: structured red team exercise**  
  - Data: An open model run locally with a scope you define  
  - Task: Plan and run a red-team exercise with documented rules, categorize findings and measure rate and severity.  
  - Deliverables: Exercise report and findings database.  
  - Pass gate: Rules of engagement written first and no harmful outputs published.
- **Project 2: refusal calibration evaluation**  
  - Data: Paired sets of harmful and benign-but-similar requests  
  - Task: Measure harmful-request refusal against benign over-refusal across models and settings.  
  - Deliverables: Trade-off analysis.  
  - Pass gate: Benign set designed to match harmful set in surface form.
- **Project 3: safety case for a deployment**  
  - Data: A hypothetical assistant deployment  
  - Task: Write a structured safety case with claims, arguments and evidence and identify its weakest links.  
  - Deliverables: Safety case document.  
  - Pass gate: Each claim linked to evidence or marked as an open gap.

### 05 — AI Governance Regulation and Assurance

**Outcome:** Turn laws, standards and audits into engineering work. Statements about law in this module are education, not legal advice, and must be confirmed from primary sources at the time of use.

**Lessons**

- `01-regulatory-landscape.md` — Regulatory landscape: the EU AI Act risk tiers and general-purpose model obligations, India's approach, United States approaches and other jurisdictions
- `02-data-protection-law-for-ml.md` — Data-protection law for ML: India's DPDP Act and Rules and comparable regimes
- `03-standards-and-assurance.md` — Standards and assurance: ISO/IEC 42001, audit standards and conformity assessment
- `04-algorithmic-audits.md` — Algorithmic audits: internal, external and adversarial audit methodology
- `05-documentation-and-traceability-required-for-high-risk-systems.md` — Documentation and traceability required for high-risk systems
- `06-post-market-monitoring-and-incident-reporting-duties.md` — Post-market monitoring and incident reporting duties
- `07-procurement-and-vendor-assurance-for-third-party-models.md` — Procurement and vendor assurance for third-party models
- `08-liability-and-accountability.md` — Liability and accountability: who is responsible when a model causes harm
- `09-producing-compliance-evidence-from-the-ml-platform-using-the-policy-as-code-of-g11.md` — Producing compliance evidence from the ML platform using the policy-as-code of G11

**Hands-on projects**

- **Project 1: regulatory mapping for a product**  
  - Data: A hypothetical AI product sold in India and the European Union  
  - Task: Classify the product under applicable regimes and build a requirements-to-evidence matrix with owners.  
  - Deliverables: Mapping matrix and gap list.  
  - Pass gate: Every requirement cited to a primary source with the date accessed.
- **Project 2: algorithmic audit of a public model**  
  - Data: A public model or API you have permission to test  
  - Task: Design and run an external-style audit with a written scope, methods and findings.  
  - Deliverables: Audit report.  
  - Pass gate: Methods fixed before testing and findings include limitations.
- **Project 3: compliance evidence automation**  
  - Data: Your G11 platform sandbox or a simulated registry  
  - Task: Generate audit evidence automatically from lineage, evaluation and approval records and test for gaps.  
  - Deliverables: Evidence generator and gap tests.  
  - Pass gate: Missing evidence is detected by tests.

### 06 — Adversarial Examples and Robustness Evaluation

**Outcome:** Understand evasion attacks well enough to evaluate and improve robustness correctly. Corruption robustness and OOD detection are covered in G2, and adversarial inputs are introduced in Stage 5D. This module is defensive: all attacks are run against your own models.

**Lessons**

- `01-threat-models.md` — Threat models: attacker knowledge, capability and goal, and why they must be stated
- `02-gradient-based-evasion-attacks.md` — Gradient-based evasion attacks: FGSM and PGD
- `03-black-box-attacks.md` — Black-box attacks: transfer and query-based methods
- `04-physical-world-and-patch-attacks-and-their-limits.md` — Physical-world and patch attacks, and their limits
- `05-adversarial-training-and-its-costs.md` — Adversarial training and its costs
- `06-certified-robustness.md` — Certified robustness: randomized smoothing and bound propagation
- `07-evaluating-defenses-correctly.md` — Evaluating defenses correctly: adaptive attacks and gradient masking
- `08-robustness-benchmarks-and-standardized-evaluation-with-autoattack-style-suites.md` — Robustness benchmarks and standardized evaluation with AutoAttack-style suites
- `09-adversarial-examples-beyond-images.md` — Adversarial examples beyond images: tabular, text and audio
- `10-robustness-accuracy-trade-offs-and-when-robustness-is-worth-its-cost.md` — Robustness-accuracy trade-offs and when robustness is worth its cost

**Hands-on projects**

- **Project 1: pgd attack and adversarial training study**  
  - Data: CIFAR-10 and a small tabular dataset  
  - Task: Attack your own models, apply adversarial training and report clean and robust accuracy under stated threat models.  
  - Deliverables: Evaluation report.  
  - Pass gate: Robust accuracy measured with a strong, adaptive attack suite.
- **Project 2: broken defense reproduction**  
  - Data: A published defense with public code  
  - Task: Test whether the defense survives adaptive attacks and document gradient masking if present.  
  - Deliverables: Evaluation and analysis.  
  - Pass gate: Attack adapted to the defense and reported honestly.
- **Project 3: certified robustness with randomized smoothing**  
  - Data: CIFAR-10  
  - Task: Compute certified radii and compare with empirical robustness.  
  - Deliverables: Certification results.  
  - Pass gate: Certification parameters and failure rates reported.

### 07 — Data Poisoning Backdoors and Training Time Attacks

**Outcome:** Understand how training data and pretrained weights can be manipulated and how to detect and limit it. One overview lesson on poisoning is in Stage 5D, signing and provenance in G11 and poisoned feedback in G11; this module covers the attack and defense research in depth, defensively.

**Lessons**

- `01-poisoning-goals.md` — Poisoning goals: availability, targeted and backdoor attacks
- `02-backdoors-and-trojans.md` — Backdoors and trojans: triggers, stealth and persistence
- `03-clean-label-and-data-supply-attacks-on-web-scale-and-crowdsourced-data.md` — Clean-label and data-supply attacks on web-scale and crowdsourced data
- `04-poisoning-language-models.md` — Poisoning language models: instruction and preference data and persistent hidden behaviors
- `05-detection.md` — Detection: spectral signatures, activation clustering and trigger reconstruction
- `06-defenses.md` — Defenses: sanitization, robust training and fine-pruning
- `07-evaluating-defenses-against-adaptive-attackers.md` — Evaluating defenses against adaptive attackers
- `08-pretrained-model-risks.md` — Pretrained-model risks: trusting third-party weights and verifying behavior
- `09-differential-privacy-and-certified-defenses-as-limits-on-poisoning.md` — Differential privacy and certified defenses as limits on poisoning

**Hands-on projects**

- **Project 1: backdoor injection and detection lab**  
  - Data: A small image classifier you train  
  - Task: Insert a backdoor into your own model and compare detection methods on recall and false positives.  
  - Deliverables: Detection comparison.  
  - Pass gate: Run only on models and data you own.
- **Project 2: poisoning rate vs damage study**  
  - Data: A tabular and a text classification task  
  - Task: Measure accuracy and targeted-failure rates as the poisoned fraction grows and test sanitization.  
  - Deliverables: Damage curves and defense results.  
  - Pass gate: Many seeds per poisoning rate.
- **Project 3: third party model behavior audit**  
  - Data: Several open pretrained models  
  - Task: Test unexpected behaviors with trigger-hunting and behavior probes and document limits of what testing can prove.  
  - Deliverables: Audit report.  
  - Pass gate: Claims limited to what the tests can support.

### 08 — Privacy Attacks Model Extraction and Inference Threats

**Outcome:** Measure what a trained or served model leaks. Rate limiting and authentication are covered in Stage 5D and prompt and system-prompt extraction in G3; this module covers statistical privacy attacks and model theft, defensively on your own models.

**Lessons**

- `01-what-models-leak.md` — What models leak: memorization, membership and attribute information
- `02-membership-inference.md` — Membership inference: threshold attacks and likelihood-ratio attacks
- `03-attribute-inference-and-model-inversion.md` — Attribute inference and model inversion
- `04-training-data-extraction-from-language-models-and-measuring-memorization.md` — Training-data extraction from language models and measuring memorization
- `05-model-extraction-and-stealing-through-query-access.md` — Model extraction and stealing through query access
- `06-defenses.md` — Defenses: regularization, output restriction, rate and query-pattern monitoring and differential privacy
- `07-model-watermarking-and-fingerprinting-for-ownership-claims.md` — Model watermarking and fingerprinting for ownership claims
- `08-attacks-on-embeddings-and-retrieval-systems.md` — Attacks on embeddings and retrieval systems
- `09-privacy-auditing.md` — Privacy auditing: empirical measurement of leakage and its limits

**Hands-on projects**

- **Project 1: membership inference audit**  
  - Data: Models you train on CIFAR-10 and a tabular dataset with and without regularization  
  - Task: Run threshold and likelihood-ratio membership attacks and relate leakage to overfitting and defenses.  
  - Deliverables: Attack results and defense comparison.  
  - Pass gate: Attack evaluated at low false-positive rates, not only average accuracy.
- **Project 2: language model memorization measurement**  
  - Data: A small language model you fine-tune on data containing planted canary sequences  
  - Task: Measure extraction of canaries as duplication and model size change and test deduplication as a defense.  
  - Deliverables: Memorization curves.  
  - Pass gate: Only planted synthetic canaries used.
- **Project 3: model extraction and query monitoring**  
  - Data: A prediction API you build over your own model  
  - Task: Extract a surrogate model through queries and detect the extraction with monitoring.  
  - Deliverables: Attack and detector results.  
  - Pass gate: Detector false-alarm rate measured on normal traffic.

### 09 — ML Security Engineering Threat Modeling and Red Team Operations

**Outcome:** Run ML security as an engineering discipline. Supply-chain security and policy-as-code gates are covered in G11, and application-layer LLM security in G3.

**Lessons**

- `01-threat-modeling-for-ml-systems.md` — Threat modeling for ML systems: attack surface across data, training, model, serving and feedback
- `02-knowledge-bases.md` — Knowledge bases: MITRE ATLAS and the OWASP lists for ML and LLM applications
- `03-secure-ml-development-lifecycle.md` — Secure ML development lifecycle: security requirements, reviews and testing
- `04-security-testing-tools.md` — Security testing tools: the Adversarial Robustness Toolbox, Foolbox and TextAttack, with maintenance checks
- `05-detecting-attacks-in-production.md` — Detecting attacks in production: query-pattern and input-anomaly monitoring
- `06-incident-response-for-ml-attacks-and-coordination-with-security-teams.md` — Incident response for ML attacks and coordination with security teams
- `07-purple-teaming.md` — Purple teaming: combining attack and defense exercises
- `08-vulnerability-disclosure-and-bug-bounty-practice-for-ml-systems.md` — Vulnerability disclosure and bug-bounty practice for ML systems
- `09-security-metrics-and-reporting-to-leadership.md` — Security metrics and reporting to leadership

**Hands-on projects**

- **Project 1: ml system threat model and attack tree**  
  - Data: The end-to-end system from your G11 capstone  
  - Task: Build a threat model with attack trees and map each threat to an ATLAS technique, control and test.  
  - Deliverables: Threat model document.  
  - Pass gate: Each high-severity threat has a control and a verification.
- **Project 2: purple team exercise on your own system**  
  - Data: A model service you own  
  - Task: Run attacks from earlier modules against the service and tune detection and response, recording detection time.  
  - Deliverables: Exercise report.  
  - Pass gate: Run only in an isolated environment you own.
- **Project 3: ml security testing in ci**  
  - Data: A model repository  
  - Task: Add automated robustness, leakage and poisoning-sensitivity tests to CI and show a regression being caught.  
  - Deliverables: CI configuration and demonstration.  
  - Pass gate: Thresholds set from measured variance.

### 10 — Differential Privacy Foundations and Practice

**Outcome:** Train and analyze data with formal privacy guarantees and know what the numbers mean. PII masking, de-identification, consent and retention are covered in Stages 2C and 2D, and one sensitive-data lesson in Stage 5D; none of them provide formal guarantees.

**Lessons**

- `01-the-definition.md` — The definition: epsilon, delta and what a guarantee does and does not promise
- `02-basic-mechanisms.md` — Basic mechanisms: Laplace, Gaussian and exponential mechanisms
- `03-sensitivity-and-clipping.md` — Sensitivity and clipping: bounding contributions
- `04-composition-and-privacy-accounting.md` — Composition and privacy accounting: advanced composition, Renyi and moment accountants
- `05-dp-sgd.md` — DP-SGD: per-example gradients, noise calibration and implementation with Opacus
- `06-utility-under-privacy.md` — Utility under privacy: tuning and scaling behavior at different budgets
- `07-differentially-private-statistics-and-tabular-models.md` — Differentially private statistics and tabular models
- `08-local-central-and-shuffle-models-and-real-deployments.md` — Local, central and shuffle models and real deployments
- `09-pitfalls.md` — Pitfalls: implementation bugs, floating-point issues and misread epsilon values
- `10-empirical-privacy-auditing-of-dp-implementations.md` — Empirical privacy auditing of DP implementations

**Hands-on projects**

- **Project 1: dp sgd utility privacy frontier**  
  - Data: MNIST or CIFAR-10 and a tabular dataset  
  - Task: Train with DP-SGD at several privacy budgets and plot the utility-privacy frontier with proper accounting.  
  - Deliverables: Frontier plots with intervals.  
  - Pass gate: Accountant method and parameters recorded for every point.
- **Project 2: dp mechanisms from scratch with tests**  
  - Data: Synthetic data  
  - Task: Implement Laplace and Gaussian mechanisms and a simple accountant and test the guarantees statistically.  
  - Deliverables: Tested implementation.  
  - Pass gate: Statistical tests detect a deliberately buggy mechanism.
- **Project 3: dp implementation audit**  
  - Data: A DP training run  
  - Task: Audit it empirically with membership-inference-based lower bounds and compare with the claimed epsilon.  
  - Deliverables: Audit report.  
  - Pass gate: Lower bound never exceeds the claimed epsilon, or the discrepancy is investigated.

### 11 — Federated Learning Systems

**Outcome:** Train across silos or devices without centralizing raw data, and know its limits. Trino and Presto federated queries are covered in Stage 2C and are a different idea from federated learning.

**Lessons**

- `01-cross-device-and-cross-silo-settings-and-when-each-applies.md` — Cross-device and cross-silo settings and when each applies
- `02-federated-averaging-and-the-effect-of-non-identical-client-data.md` — Federated averaging and the effect of non-identical client data
- `03-client-drift-remedies.md` — Client drift remedies: FedProx and SCAFFOLD
- `04-communication-efficiency.md` — Communication efficiency: local steps, compression and sparsification
- `05-personalization.md` — Personalization: global model versus local adaptation
- `06-secure-aggregation.md` — Secure aggregation: what it hides and what it does not
- `07-federated-learning-with-differential-privacy.md` — Federated learning with differential privacy: user-level guarantees
- `08-system-heterogeneity.md` — System heterogeneity: stragglers, dropouts and device availability
- `09-attacks-on-federated-systems.md` — Attacks on federated systems: client poisoning and gradient inversion
- `10-frameworks.md` — Frameworks: Flower, NVIDIA FLARE, OpenFL and others, with maintenance checks
- `11-evaluation.md` — Evaluation: global and per-client metrics, fairness across clients

**Hands-on projects**

- **Project 1: federated learning benchmark with non iid data**  
  - Data: CIFAR-10 or FEMNIST partitioned across simulated clients with controllable heterogeneity  
  - Task: Compare FedAvg, FedProx and SCAFFOLD under increasing heterogeneity and report communication cost.  
  - Deliverables: Benchmark with intervals.  
  - Pass gate: Same client partitions and rounds for all methods.
- **Project 2: cross silo healthcare style simulation**  
  - Data: A public multi-site or partitioned medical dataset  
  - Task: Train across simulated hospitals and compare with centralized and local-only training, including per-site performance.  
  - Deliverables: Comparison with per-site analysis.  
  - Pass gate: Per-site worst-case performance reported.
- **Project 3: gradient inversion risk study**  
  - Data: Your own federated setup  
  - Task: Test how much training data can be reconstructed from shared updates and how secure aggregation and noise change it.  
  - Deliverables: Reconstruction-risk analysis.  
  - Pass gate: Run only on your own synthetic or public data.

### 12 — Cryptographic and Hardware Privacy Techniques

**Outcome:** Know what cryptography and secure hardware can and cannot do for ML, and their cost. Encryption at rest and in transit and key management are covered in Stage 2D.

**Lessons**

- `01-threat-models-for-private-computation.md` — Threat models for private computation: honest-but-curious and malicious parties
- `02-secret-sharing-and-secure-multi-party-computation-basics.md` — Secret sharing and secure multi-party computation basics
- `03-homomorphic-encryption.md` — Homomorphic encryption: schemes, libraries and realistic performance for inference
- `04-private-set-intersection-and-private-data-joins.md` — Private set intersection and private data joins
- `05-trusted-execution-environments-and-confidential-computing-for-cpus-and-gpus.md` — Trusted execution environments and confidential computing for CPUs and GPUs
- `06-zero-knowledge-proofs-for-ml.md` — Zero-knowledge proofs for ML: what is and is not practical
- `07-private-inference-and-encrypted-retrieval.md` — Private inference and encrypted retrieval
- `08-data-clean-rooms-and-privacy-preserving-analytics-products.md` — Data clean rooms and privacy-preserving analytics products
- `09-decision-framework.md` — Decision framework: choosing among differential privacy, federated learning, cryptography and secure hardware

**Hands-on projects**

- **Project 1: encrypted inference feasibility study**  
  - Data: A small logistic regression or tree model  
  - Task: Run inference under homomorphic encryption and compare latency, accuracy loss and cost with plaintext.  
  - Deliverables: Feasibility report.  
  - Pass gate: Accuracy compared on the same test set.
- **Project 2: private set intersection for record matching**  
  - Data: Two synthetic customer lists with overlap  
  - Task: Compute intersection with a PSI protocol and compare with a plaintext join on result and cost.  
  - Deliverables: Protocol implementation and comparison.  
  - Pass gate: Result equals the plaintext join.
- **Project 3: privacy technique decision memo**  
  - Data: Three hypothetical data-sharing scenarios  
  - Task: Recommend a technique for each with threat model, cost and residual risk.  
  - Deliverables: Decision memo.  
  - Pass gate: Each recommendation names what it does not protect against.

### 13 — Privacy Engineering and Privacy Risk Management for ML

**Outcome:** Manage privacy risk across the ML lifecycle. Data governance, consent, retention and GDPR-style deletion are covered in Stages 2C and 2D and sensitive-data handling in Stage 5D; this module covers what a trained model itself reveals and how to respond.

**Lessons**

- `01-privacy-by-design-for-ml-systems.md` — Privacy by design for ML systems: data minimization and purpose limitation in modeling
- `02-privacy-risk-assessment-for-models.md` — Privacy risk assessment for models: what training and serving can leak
- `03-anonymization-limits.md` — Anonymization limits: k-anonymity, l-diversity and why re-identification keeps succeeding
- `04-machine-unlearning.md` — Machine unlearning: exact and approximate methods and how to evaluate them
- `05-deletion-requests-and-trained-models.md` — Deletion requests and trained models: legal motivation and engineering options
- `06-synthetic-data-and-privacy-claims.md` — Synthetic data and privacy claims: testing them with the attacks of module 08
- `07-privacy-budgets-as-governance.md` — Privacy budgets as governance: allocation and approval
- `08-privacy-breach-response-for-ml-systems-and-notification-duties-to-be-confirmed-from-primary-sources.md` — Privacy breach response for ML systems and notification duties to be confirmed from primary sources
- `09-privacy-in-on-device-and-edge-ml-with-links-to-g10.md` — Privacy in on-device and edge ML, with links to G10

**Hands-on projects**

- **Project 1: reidentification risk study**  
  - Data: A synthetic population with quasi-identifiers  
  - Task: Measure re-identification risk under k-anonymity and compare with noise-based methods.  
  - Deliverables: Risk analysis.  
  - Pass gate: Only synthetic data used.
- **Project 2: machine unlearning evaluation**  
  - Data: A classifier on public data  
  - Task: Compare retraining, sharded-training unlearning and approximate methods on forgetting quality, utility and cost using membership inference as the test.  
  - Deliverables: Comparison.  
  - Pass gate: Forgetting measured against full retraining.
- **Project 3: synthetic data privacy test**  
  - Data: Synthetic data generated from a public dataset  
  - Task: Test whether synthetic records leak real ones with nearest-neighbor and membership attacks.  
  - Deliverables: Leakage report.  
  - Pass gate: Claims limited to the attacks tested.

### 14 — Trustworthy ML Practice Integration and Assurance Cases

**Outcome:** Combine fairness, privacy, robustness and safety into delivery practice and resolve their tensions.

**Lessons**

- `01-assurance-cases.md` — Assurance cases: claims, arguments and evidence for ML properties
- `02-tensions-between-goals.md` — Tensions between goals: privacy against fairness, robustness against accuracy and explainability against performance
- `03-trustworthiness-requirements-in-the-project-lifecycle.md` — Trustworthiness requirements in the project lifecycle: from scoping to retirement
- `04-release-gates-for-trust-properties-and-exception-processes.md` — Release gates for trust properties and exception processes
- `05-review-boards-and-independent-challenge.md` — Review boards and independent challenge
- `06-incident-learning.md` — Incident learning: building a library of trust failures
- `07-case-studies.md` — Case studies: a healthcare risk algorithm found biased, a criminal-risk tool, a welfare fraud scoring scandal and an automated debt-recovery failure
- `08-communicating-limits-and-risks-to-users-and-the-public.md` — Communicating limits and risks to users and the public
- `09-building-a-culture-that-surfaces-concerns.md` — Building a culture that surfaces concerns

**Hands-on projects**

- **Project 1: assurance case for a high stakes model**  
  - Data: A model from G9 or earlier groups  
  - Task: Write an assurance case covering fairness, robustness, privacy, safety and explainability, with gaps and a remediation plan.  
  - Deliverables: Assurance case.  
  - Pass gate: Each claim linked to executed tests or marked as an open gap.
- **Project 2: trade off analysis across trust goals**  
  - Data: One dataset and model  
  - Task: Measure how privacy noise, fairness constraints and adversarial training interact on accuracy and each trust metric.  
  - Deliverables: Interaction analysis.  
  - Pass gate: All combinations evaluated with intervals.
- **Project 3: trust failure case study library**  
  - Data: Public investigations and reports of trust failures  
  - Task: Analyze at least five failures for root causes, early warning signs and controls that would have helped.  
  - Deliverables: Case library.  
  - Pass gate: Facts cited to primary reports with dates.

### 15 — G12 Capstones

**Outcome:** integrate the responsible-AI, security and privacy tracks in assessed, portfolio-quality work.

- **Capstone 1: responsible ai review of a high stakes system** (uses Modules 01 to 03, 05, 14)  
  Carry out a full responsible-AI review of a high-stakes model: impact assessment, fairness audit with uncertainty, explanation evaluation, regulatory mapping and an assurance case, ending in a go, conditional-go or no-go recommendation.
- **Capstone 2: model safety and red team report** (uses Modules 04, 09)  
  Plan and run a structured red-team evaluation of a language model in a controlled environment and deliver a safety report with measured rates, limits and mitigations.
- **Capstone 3: adversarial robustness and security evaluation** (uses Modules 06 to 09)  
  Evaluate one model against evasion, poisoning, privacy and extraction threats with honest, adaptive evaluation and a prioritized hardening plan.
- **Capstone 4: privacy preserving training system** (uses Modules 10 to 13)  
  Build a training system that combines differential privacy and federated learning on a realistic task, audit its leakage empirically and document privacy and utility trade-offs.
- **Capstone 5: g12 readiness assessment** (uses All modules)  
  Written and practical assessment against the G12 completion gate.

## G12 completion gate

- Every trust metric (subgroup performance, robust accuracy, leakage rate, privacy budget) is reported with uncertainty, sample sizes and the threat model or group definition used.
- Every robustness claim is tested with adaptive attacks; every privacy claim is tested with an attack-based audit as well as the formal guarantee; every fairness claim states which definition was chosen and what it gives up.
- Every attack, red-team and privacy-audit project ran only in an isolated environment, on models and data you own, synthetic data or public data permitted for the purpose, and no harmful output or exploit detail was published.
- Every legal, regulatory or standards statement is cited to a primary source with issuer, version and date accessed, and none is presented as legal advice.
- Every library has licence and maintenance status recorded before adoption.
- All results reproduce from a lockfile, configs and logged seeds, with versions recorded.
- At least one negative or inconclusive result per track is reported honestly, including a case where a defense failed.
- The four specialist capstones are complete and the readiness assessment is passed.

## Audit and verification

**What was checked and the result**

- Structure: 14 specialist modules each have 6 to 12 lessons and at least one project; the tree contains 221 files and 31 folders, and these counts equal the counts computed from the curriculum data.
- Overlap with the Roadmap: all 134 lesson file names were compared against every lesson file name in `Roadmap.md`. Exact matches: 0. Near matches (similarity 0.80 or higher): 1 — `poisoning-language-models` vs Roadmap `vision-language-models` (0.85). Each was reviewed manually for topic overlap.
- Structural problems found by the build script: 0.
- Topic-level overlap check and the corrections it forced: the Roadmap text was searched for differential privacy, membership inference, demographic parity, equalized odds, red teaming, the EU AI Act, ISO/IEC 42001, k-anonymity, homomorphic encryption, secure multi-party computation, confidential computing, enclaves, backdoors, unlearning, jailbreaks and impact assessments. None appear as lessons, so G12 teaches them for the first time. The search also found a Stage 2D data governance, security, privacy and compliance module (PII masking, consent, retention, GDPR deletion, encryption and key management), Stage 2C PII and deletion lessons, a Stage 2C federated-query lesson (a different idea from federated learning) and Stage 5D lessons on sensitive-data privacy, model cards and dataset cards, fairness monitoring and ML-specific security. The first draft of module 01 included a dataset-datasheet lesson and project that duplicated the Stage 5D dataset-card lesson; both were rewritten into system-card work. The scope table names each lesson G12 builds on.
- Verified by web search on the build date (2026-10-26): the EU AI Act's general-purpose model obligations have applied since 2 August 2025, and a Digital Omnibus agreement moves stand-alone high-risk obligations from 2 August 2026 to 2 December 2027 and product-embedded high-risk obligations to 2 August 2028 (reported as endorsed by Parliament on 16 June 2026 and by the Council on 29 June 2026, with Official Journal publication not confirmed); MeitY released India's AI Governance Guidelines on 5 November 2025 with seven principles and a sectoral, existing-law approach, and the DPDP Rules were notified on 13 November 2025 with phased commencement (main obligations around 18 months later, around May 2027; some dates differ between sources); Flower is a framework-agnostic federated learning framework with nightly builds in July 2026.
- Reported but not confirmed: the Official Journal publication and exact dates of the EU Digital Omnibus changes; the exact DPDP Rules commencement dates and the Data Protection Board's operational status; the maintenance status of TensorFlow Federated, Opacus, OpenDP, the Adversarial Robustness Toolbox, Foolbox, TextAttack, NVIDIA FLARE, OpenFL, Fairlearn and AIF360; MITRE ATLAS and the OWASP ML lists are cited from established practice and were not re-checked; the published frontier safety frameworks of AI developers, the NIST AI RMF and ISO standards were not re-checked and must be read from primary sources; the case studies in module 14 are cited from well-known public reports and must be verified from the primary reports.
- Not verified: library versions, which change quickly; regulatory details, which change and differ by jurisdiction; and statistical performance claims from papers.
- Not verified by execution: no code in this plan has been run. Project pass gates are acceptance criteria to be met when the projects are built.
- Safety note: modules 04, 06 to 09 and 11 involve attack and red-team techniques. This plan presents them for defense, evaluation and education only. Run every attack only against models, data and systems you own, in an isolated environment; do not test third-party systems without written permission; do not publish harmful outputs or operational exploit details; and handle any serious finding through responsible disclosure.
- Legal note: this plan is education, not legal advice. Consult qualified counsel before relying on any regulatory interpretation.
- Repository safety: this build created only this file; no existing file or folder was created, changed or deleted by it.
