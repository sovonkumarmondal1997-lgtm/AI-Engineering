# Industry Domain ML — ML Specialization Roadmap

**Group 9 (G9)** of the specialization that follows Stage 5D of the [Roadmap](./Roadmap.md). It covers original categories **14 Fraud Detection and Risk Modeling, 18 Geospatial Machine Learning, 21 Scientific Machine Learning, 22 Healthcare and Biomedical Machine Learning, 23 Financial Machine Learning and 24 Industrial and Predictive Maintenance ML**. The group's defining question is: *which regulated or physical industry is this for?* It follows G1 to G8: [`01_Classical and Applied ML.md`](./01_Classical%20and%20Applied%20ML.md), [`02_Deep Learning by Modality.md`](./02_Deep%20Learning%20by%20Modality.md), [`03_Generative and Foundation Models.md`](./03_Generative%20and%20Foundation%20Models.md), [`04_Agents and Sequential Decisions.md`](./04_Agents%20and%20Sequential%20Decisions.md), [`05_Time and Anomaly Modeling.md`](./05_Time%20and%20Anomaly%20Modeling.md), [`06_Personalization Search and Matching.md`](./06_Personalization%20Search%20and%20Matching.md), [`07_Statistical Reasoning.md`](./07_Statistical%20Reasoning.md), [`08_Graphs and Optimization.md`](./08_Graphs%20and%20Optimization.md).

## G9 summary

| Item | Count |
|---|---|
| Modules (including overview and capstones) | 21 |
| Lesson files | 184 |
| Hands-on project files (module projects, overview project and capstones) | 64 |
| Folders inside the G9 tree | 41 |
| Files inside the G9 tree | 296 |

| Original category | Modules |
|---|---|
| 14 Fraud Detection and Risk Modeling | 01 to 03 |
| 23 Financial Machine Learning | 04 to 05 |
| 18 Geospatial Machine Learning | 06 to 08 |
| 22 Healthcare and Biomedical Machine Learning | 09 to 13 |
| 21 Scientific Machine Learning | 14 to 15 |
| 24 Industrial and Predictive Maintenance ML | 16 to 18 |
| Shared by all six domains | 19 |

## Scope and how G9 avoids repeating the Roadmap

G9 is the application group, so it reuses methods taught earlier and teaches only what is specific to each industry: its data, its labels, its validation rules, its regulation and its costs. These are **already learned** and are only referenced, never retaught: imbalanced learning, threshold optimization and alert capacity, calibration, anomaly detection, feature stores, point-in-time correctness, monitoring and drift, model cards and fairness monitoring, and the real-time fraud and risk platform architecture case (Stages 5B, 5D and 2D); graph-based fraud detection (Stage 5B and G8); gradient boosting, WOE scorecards, reason codes, PSI, survival analysis, censored and noisy labels and decision-focused evaluation (G1); segmentation, detection, transfer learning and medical-agnostic computer vision (Stage 5C and G2); audio and signal features (G2); language models for domain text (G2 and G3); time-series forecasting, state-space models, anomaly detection, SPC charts and intermittent demand (G5); Bayesian and Gaussian-process methods, conformal prediction, causal inference and copulas (G7); graph neural networks, optimization and decision under uncertainty (G8); and the edge deployment and compression covered later in G10.

**Boundaries with other groups** (so nothing overlaps): general responsible-AI, privacy and adversarial methods belong to **G12** (module 03 and 13 cover only domain-specific governance and regulation); benchmark and evaluation-system design belongs to **G13**; edge deployment and model compression belong to **G10**; MLOps platforms belong to **G11**. This group does not teach clinical medicine, finance or engineering theory beyond the minimum needed to model correctly; lessons that need domain background say so and teach it in context.

| Roadmap topic already covered | Where G9 goes further |
|---|---|
| Imbalanced learning, alert capacity, anomaly detection (5B); real-time fraud platform case (2D) | Module 01: delayed and biased labels, adversaries, hybrid rules and models, AML and sanctions screening |
| Scorecards and WOE (G1), survival analysis (G1) | Module 02: PD, LGD, EAD, expected credit loss, vintages, stress testing and lending-specific validation |
| Model cards, audit trails and fairness monitoring (5D) | Module 03: independent validation, model inventory, tiering and financial-services governance |
| Time-series forecasting and backtesting (5B, G5) | Module 04: market-data biases, triple-barrier labels, purged cross-validation and backtest-overfitting corrections |
| Tweedie objectives (G1), copulas (G7) | Module 05: frequency-severity pricing, reserving and tail risk |
| Pandas and data-engineering lessons (Stage 2) | Module 06: coordinate systems, spatial indexes, H3, rasters, STAC and geocoding, which the Roadmap does not cover |
| Gaussian processes (G7), GNN forecasting (G8) | Module 07: spatial autocorrelation, spatial validation, geostatistics and location intelligence |
| Segmentation and transfer learning (5C, G2) | Module 08: spectral indices, SAR, cloud masking, geospatial foundation models and regional shift |
| Calibration (5B), leakage (5A) | Modules 09 and 10: clinical data standards, phenotyping, TRIPOD+AI, decision curves and external validation |
| Computer vision essentials (5C, G2) | Module 11: DICOM, 3D segmentation, pathology, biosignals and shortcut audits |
| Molecular GNNs (G8), language models (G2) | Module 12: drug-discovery evaluation, omics batch effects, biomedical text mining and trial ML |
| Model governance (5D) | Module 13: device-software classification, evidence generation, hazard analysis and post-market monitoring |
| Differential-equation math is not in the Roadmap | Modules 14 and 15: surrogates, PINNs, neural operators, equation discovery, interatomic potentials and materials ML |
| Anomaly detection and SPC (G5), signals (G2) | Modules 16 to 18: vibration analysis, condition monitoring, RUL, maintenance policy and manufacturing quality ML |
| Human-in-the-loop pattern (5D) | Module 19: expert elicitation, validation ladders, safety cases and domain selection |

## G9 — Industry Domain ML

**Defining question:** Which regulated or physical industry is this for?

```text
ML Specialization/
└── G9 — Industry Domain ML/
    ├── 00-G9-Overview/
    │   ├── Projects/
    │   │   ├── 01-g9-domain-data-register-and-validation-bootstrap.md
    │   │   └── README.md
    │   ├── 01-g9-scope-and-boundaries-with-earlier-stages-and-groups.md
    │   ├── 02-prerequisite-map-from-the-roadmap.md
    │   ├── 03-dataset-and-tooling-register.md
    │   ├── 04-evaluation-and-reporting-standards.md
    │   ├── 05-completion-gate.md
    │   ├── README.md
    │   └── learning-plan.md
    ├── 01-Fraud-and-Financial-Crime-Detection-Systems/
    │   ├── Projects/
    │   │   ├── 01-delayed-label-fraud-model-with-maturation-windows.md
    │   │   ├── 02-aml-transaction-monitoring-triage.md
    │   │   ├── 03-name-matching-for-sanctions-screening.md
    │   │   └── README.md
    │   ├── 01-fraud-taxonomy.md
    │   ├── 02-label-delay-and-label-bias.md
    │   ├── 03-adversarial-adaptation.md
    │   ├── 04-behavioral-and-device-features.md
    │   ├── 05-rules-plus-models.md
    │   ├── 06-real-time-decision-constraints.md
    │   ├── 07-case-management.md
    │   ├── 08-anti-money-laundering.md
    │   ├── 09-sanctions-and-watchlist-screening.md
    │   ├── 10-payment-rail-specifics-for-india.md
    │   ├── 11-evaluating-under-delay.md
    │   └── README.md
    ├── 02-Credit-Risk-and-Lending-ML/
    │   ├── Projects/
    │   │   ├── 01-pd-model-with-vintage-and-calibration-analysis.md
    │   │   ├── 02-loss-given-default-and-ecl-estimation.md
    │   │   ├── 03-credit-model-stress-test.md
    │   │   └── README.md
    │   ├── 01-credit-risk-components.md
    │   ├── 02-expected-credit-loss-and-provisioning-concepts-under-ifrs-9-and-similar-standards.md
    │   ├── 03-application-vs-behavioral-scoring-and-the-lending-lifecycle.md
    │   ├── 04-thin-file-and-alternative-data-borrowers.md
    │   ├── 05-loss-given-default-and-exposure-modeling-with-censored-and-long-horizon-outcomes.md
    │   ├── 06-vintage-and-cohort-analysis.md
    │   ├── 07-backtesting-and-monitoring-credit-models.md
    │   ├── 08-stress-testing-and-macro-scenarios-for-portfolios.md
    │   ├── 09-collections-and-early-warning-models.md
    │   ├── 10-fair-lending-and-explainability-obligations-with-india-s-digital-lending-rules-to-be-checked-in-primary-sources.md
    │   └── README.md
    ├── 03-Model-Risk-Management-and-Regulated-Model-Governance/
    │   ├── Projects/
    │   │   ├── 01-model-validation-report-for-your-own-credit-model.md
    │   │   ├── 02-model-inventory-and-tiering-system.md
    │   │   ├── 03-governance-gap-analysis-against-free-ai.md
    │   │   └── README.md
    │   ├── 01-model-risk.md
    │   ├── 02-model-lifecycle-governance.md
    │   ├── 03-independent-validation.md
    │   ├── 04-ongoing-monitoring.md
    │   ├── 05-documentation-standards.md
    │   ├── 06-challenger-models-and-benchmarking-as-validation-tools.md
    │   ├── 07-ai-specific-governance-frameworks.md
    │   ├── 08-explainability-and-adverse-decision-communication-in-regulated-settings.md
    │   ├── 09-third-party-and-vendor-model-risk.md
    │   ├── 10-incident-reporting-and-audit-trails.md
    │   └── README.md
    ├── 04-Financial-Time-Series-and-Market-Data-ML/
    │   ├── Projects/
    │   │   ├── 01-backtest-overfitting-demonstration.md
    │   │   ├── 02-triple-barrier-labeling-and-purged-cv-pipeline.md
    │   │   ├── 03-factor-model-and-risk-report.md
    │   │   └── README.md
    │   ├── 01-market-data-structure.md
    │   ├── 02-information-driven-bars-and-sampling.md
    │   ├── 03-labeling.md
    │   ├── 04-stationarity-with-memory.md
    │   ├── 05-backtest-overfitting.md
    │   ├── 06-purged-and-embargoed-cross-validation-for-overlapping-labels.md
    │   ├── 07-transaction-costs-slippage-and-capacity.md
    │   ├── 08-factor-models-and-portfolio-construction-with-shrinkage-covariance-estimates.md
    │   ├── 09-risk-measures.md
    │   ├── 10-market-regimes-and-non-stationarity.md
    │   ├── 11-indian-market-context.md
    │   └── README.md
    ├── 05-Insurance-Pricing-and-Quantitative-Risk-Models/
    │   ├── Projects/
    │   │   ├── 01-frequency-severity-pricing-model.md
    │   │   ├── 02-loss-reserving-with-triangles.md
    │   │   ├── 03-tail-risk-with-evt.md
    │   │   └── README.md
    │   ├── 01-insurance-data-and-exposure.md
    │   ├── 02-frequency-severity-and-pure-premium-modeling-with-glms-and-gradient-boosting.md
    │   ├── 03-claims-development-and-reserving.md
    │   ├── 04-telematics-and-usage-based-pricing-features.md
    │   ├── 05-pricing-governance.md
    │   ├── 06-claims-triage-and-fraud-signals-in-insurance.md
    │   ├── 07-catastrophe-and-tail-risk.md
    │   ├── 08-portfolio-risk-aggregation-and-dependence-with-copulas-from-g7.md
    │   ├── 09-evaluating-pricing-models.md
    │   ├── 10-insurance-regulation-in-india.md
    │   └── README.md
    ├── 06-Geospatial-Data-Foundations/
    │   ├── Projects/
    │   │   ├── 01-projection-and-area-error-audit.md
    │   │   ├── 02-h3-aggregation-and-spatial-join-pipeline.md
    │   │   ├── 03-address-geocoding-quality-study.md
    │   │   └── README.md
    │   ├── 01-coordinate-reference-systems-and-projections.md
    │   ├── 02-vector-data.md
    │   ├── 03-spatial-joins-indexes-and-the-r-tree.md
    │   ├── 04-discrete-global-grids.md
    │   ├── 05-postgis-basics.md
    │   ├── 06-raster-data.md
    │   ├── 07-catalogs-and-access.md
    │   ├── 08-geocoding-and-address-handling.md
    │   ├── 09-gps-traces.md
    │   ├── 10-spatial-data-quality.md
    │   └── README.md
    ├── 07-Spatial-Statistics-and-Spatial-Machine-Learning/
    │   ├── Projects/
    │   │   ├── 01-spatial-cv-vs-random-cv-leakage-study.md
    │   │   ├── 02-site-selection-model.md
    │   │   ├── 03-kriging-vs-ml-interpolation.md
    │   │   └── README.md
    │   ├── 01-spatial-autocorrelation.md
    │   ├── 02-why-random-cross-validation-fails-on-spatial-data-and-spatial-block-validation.md
    │   ├── 03-geographically-weighted-regression-and-spatial-lag-and-error-models.md
    │   ├── 04-kriging-and-geostatistics-as-spatial-gaussian-processes.md
    │   ├── 05-hotspot-analysis-and-kernel-density-estimation.md
    │   ├── 06-spatial-feature-engineering.md
    │   ├── 07-location-intelligence.md
    │   ├── 08-mobility-data.md
    │   ├── 09-evaluating-spatial-models.md
    │   └── README.md
    ├── 08-Remote-Sensing-and-Earth-Observation-ML/
    │   ├── Projects/
    │   │   ├── 01-crop-type-mapping-from-time-series-imagery.md
    │   │   ├── 02-flood-mapping-with-sar.md
    │   │   ├── 03-geospatial-foundation-model-evaluation.md
    │   │   └── README.md
    │   ├── 01-satellite-sensors-and-products.md
    │   ├── 02-preprocessing.md
    │   ├── 03-spectral-indices.md
    │   ├── 04-scene-classification-and-land-cover-segmentation-with-torchgeo.md
    │   ├── 05-change-detection-and-image-time-series.md
    │   ├── 06-synthetic-aperture-radar.md
    │   ├── 07-geospatial-foundation-models.md
    │   ├── 08-labels-for-earth-observation.md
    │   ├── 09-domain-shift-across-regions-seasons-and-sensors.md
    │   ├── 10-applications-with-indian-relevance.md
    │   └── README.md
    ├── 09-Clinical-Data-and-Healthcare-ML-Foundations/
    │   ├── Projects/
    │   │   ├── 01-omop-style-cohort-and-label-pipeline.md
    │   │   ├── 02-coding-system-mapping-exercise.md
    │   │   ├── 03-deidentification-risk-assessment.md
    │   │   └── README.md
    │   ├── 01-healthcare-data-landscape.md
    │   ├── 02-medical-coding-systems.md
    │   ├── 03-interoperability.md
    │   ├── 04-india-s-digital-health-context.md
    │   ├── 05-de-identification-and-privacy.md
    │   ├── 06-defining-cohorts-and-labels.md
    │   ├── 07-irregular-and-informative-measurement.md
    │   ├── 08-healthcare-specific-leakage.md
    │   ├── 09-access-and-ethics.md
    │   └── README.md
    ├── 10-Clinical-Prediction-and-Decision-Support-Models/
    │   ├── Projects/
    │   │   ├── 01-sepsis-early-warning-with-clinical-validation.md
    │   │   ├── 02-tripod-ai-and-probast-self-audit.md
    │   │   ├── 03-calibration-drift-and-model-updating-study.md
    │   │   └── README.md
    │   ├── 01-clinical-prediction-targets.md
    │   ├── 02-reporting-and-bias-standards.md
    │   ├── 03-time-aware-design.md
    │   ├── 04-decision-curve-analysis.md
    │   ├── 05-external-and-temporal-validation.md
    │   ├── 06-calibration-drift-and-updating-models.md
    │   ├── 07-subgroup-performance-and-equity-checks-across-patient-groups.md
    │   ├── 08-alerting-and-workflow.md
    │   ├── 09-case-study.md
    │   ├── 10-uncertainty-and-abstention-for-clinical-use-using-methods-from-g7.md
    │   └── README.md
    ├── 11-Medical-Imaging-and-Biosignal-ML/
    │   ├── Projects/
    │   │   ├── 01-chest-xray-classification-with-shortcut-audit.md
    │   │   ├── 02-volumetric-segmentation-with-nnu-net.md
    │   │   ├── 03-ecg-classification-with-patient-level-evaluation.md
    │   │   └── README.md
    │   ├── 01-medical-image-formats-and-handling.md
    │   ├── 02-modalities.md
    │   ├── 03-annotation-in-medicine.md
    │   ├── 04-3d-and-volumetric-segmentation.md
    │   ├── 05-whole-slide-pathology.md
    │   ├── 06-medical-foundation-models.md
    │   ├── 07-biosignals.md
    │   ├── 08-shortcut-learning-in-medical-imaging.md
    │   ├── 09-evaluation.md
    │   ├── 10-explainability-limits-and-failure-analysis-for-medical-models.md
    │   └── README.md
    ├── 12-Biomedical-and-Life-Science-ML/
    │   ├── Projects/
    │   │   ├── 01-admet-prediction-with-honest-splits.md
    │   │   ├── 02-batch-effect-detection-in-omics.md
    │   │   ├── 03-biomedical-literature-mining-pipeline.md
    │   │   └── README.md
    │   ├── 01-biology-for-ml-engineers.md
    │   ├── 02-protein-ml.md
    │   ├── 03-drug-discovery-pipeline.md
    │   ├── 04-realistic-evaluation-in-drug-discovery.md
    │   ├── 05-generative-chemistry.md
    │   ├── 06-omics-data.md
    │   ├── 07-biomedical-text-mining.md
    │   ├── 08-clinical-trial-ml.md
    │   ├── 09-biostatistics-essentials.md
    │   └── README.md
    ├── 13-Healthcare-Regulation-Safety-and-Deployment/
    │   ├── Projects/
    │   │   ├── 01-regulatory-classification-and-evidence-plan.md
    │   │   ├── 02-hazard-analysis-for-a-clinical-model.md
    │   │   ├── 03-silent-trial-protocol-and-monitoring-plan.md
    │   │   └── README.md
    │   ├── 01-software-as-a-medical-device.md
    │   ├── 02-india-s-medical-device-rules-and-software-guidance-to-be-checked-in-primary-sources.md
    │   ├── 03-united-states-and-european-frameworks.md
    │   ├── 04-icmr-ethical-guidance-for-ai-in-health-and-ethics-committee-review.md
    │   ├── 05-evidence-generation.md
    │   ├── 06-reporting-guidelines.md
    │   ├── 07-safety-engineering.md
    │   ├── 08-post-market-monitoring-and-updates.md
    │   ├── 09-equity.md
    │   ├── 10-privacy-security-and-consent-in-clinical-deployment.md
    │   └── README.md
    ├── 14-Scientific-ML-Surrogates-and-Physics-Informed-Learning/
    │   ├── Projects/
    │   │   ├── 01-pinn-vs-numerical-solver-benchmark.md
    │   │   ├── 02-neural-operator-extrapolation-study.md
    │   │   ├── 03-equation-discovery-from-noisy-data.md
    │   │   └── README.md
    │   ├── 01-when-ml-helps-in-science.md
    │   ├── 02-scientific-data-formats.md
    │   ├── 03-surrogate-modeling-of-expensive-simulators-with-sampling-design-and-uncertainty-from-g7.md
    │   ├── 04-physics-informed-neural-networks.md
    │   ├── 05-neural-operators.md
    │   ├── 06-evaluating-scientific-surrogates.md
    │   ├── 07-equation-discovery.md
    │   ├── 08-differentiable-simulation-with-jax.md
    │   ├── 09-weather-and-climate-ml.md
    │   ├── 10-data-assimilation-and-its-link-to-the-kalman-filtering-of-g5.md
    │   └── README.md
    ├── 15-Molecular-Materials-and-Simulation-ML/
    │   ├── Projects/
    │   │   ├── 01-equivariant-model-vs-descriptor-baseline.md
    │   │   ├── 02-materials-property-benchmark.md
    │   │   ├── 03-active-learning-for-discovery.md
    │   │   └── README.md
    │   ├── 01-representing-atoms-and-materials.md
    │   ├── 02-symmetry-and-equivariance.md
    │   ├── 03-machine-learned-interatomic-potentials.md
    │   ├── 04-molecular-dynamics-essentials-for-ml-users.md
    │   ├── 05-materials-property-prediction.md
    │   ├── 06-datasets-and-leakage-in-atomistic-ml.md
    │   ├── 07-active-learning-and-bayesian-optimization-loops-for-discovery-using-g7.md
    │   ├── 08-generative-models-for-molecules-and-materials-and-their-validation.md
    │   ├── 09-reproducibility-and-baselines-in-scientific-ml.md
    │   └── README.md
    ├── 16-Industrial-Sensor-Data-and-Condition-Monitoring/
    │   ├── Projects/
    │   │   ├── 01-bearing-vibration-feature-engineering.md
    │   │   ├── 02-sensor-data-quality-pipeline.md
    │   │   ├── 03-maintenance-log-label-extraction.md
    │   │   └── README.md
    │   ├── 01-industrial-data-sources.md
    │   ├── 02-vibration-analysis.md
    │   ├── 03-temperature-current-pressure-and-acoustic-signals-as-condition-indicators.md
    │   ├── 04-sensor-data-quality.md
    │   ├── 05-operating-condition-normalization.md
    │   ├── 06-failure-labels-from-maintenance-logs-and-work-orders.md
    │   ├── 07-health-indicators.md
    │   ├── 08-digital-twins.md
    │   ├── 09-data-collection-design-for-new-monitoring-programs.md
    │   └── README.md
    ├── 17-Failure-Prediction-Remaining-Useful-Life-and-Maintenance-Optimization/
    │   ├── Projects/
    │   │   ├── 01-rul-on-c-mapss-with-honest-protocol.md
    │   │   ├── 02-condition-based-maintenance-cost-simulation.md
    │   │   ├── 03-hard-drive-failure-prediction.md
    │   │   └── README.md
    │   ├── 01-problem-forms.md
    │   ├── 02-degradation-models.md
    │   ├── 03-deep-learning-for-remaining-useful-life-and-the-pitfalls-of-common-benchmark-protocols.md
    │   ├── 04-failure-mode-classification-and-root-cause.md
    │   ├── 05-alarm-design-and-management.md
    │   ├── 06-maintenance-policies.md
    │   ├── 07-spare-parts-planning-with-intermittent-demand-methods-from-g5.md
    │   ├── 08-rare-failures.md
    │   ├── 09-business-value.md
    │   └── README.md
    ├── 18-Manufacturing-Process-Quality-and-Optimization-ML/
    │   ├── Projects/
    │   │   ├── 01-semiconductor-yield-prediction-on-secom.md
    │   │   ├── 02-process-fault-detection-on-tennessee-eastman.md
    │   │   ├── 03-wafer-map-defect-classification.md
    │   │   └── README.md
    │   ├── 01-process-data-structure.md
    │   ├── 02-soft-sensors-and-virtual-metrology.md
    │   ├── 03-yield-and-defect-prediction-under-high-dimensionality-and-few-failures.md
    │   ├── 04-design-of-experiments-and-response-surface-methods-combined-with-bayesian-optimization.md
    │   ├── 05-recipe-and-setpoint-optimization-with-constraints.md
    │   ├── 06-wafer-map-and-defect-pattern-classification.md
    │   ├── 07-root-cause-analysis-in-processes-using-causal-tools-from-g7.md
    │   ├── 08-energy-and-resource-efficiency-optimization.md
    │   ├── 09-deploying-models-on-the-shop-floor.md
    │   └── README.md
    ├── 19-Domain-Project-Delivery-and-Cross-Domain-Practice/
    │   ├── Projects/
    │   │   ├── 01-expert-elicitation-and-labeling-protocol.md
    │   │   ├── 02-validation-ladder-plan.md
    │   │   ├── 03-domain-choice-memo.md
    │   │   └── README.md
    │   ├── 01-working-with-domain-experts.md
    │   ├── 02-validation-ladder.md
    │   ├── 03-domain-specific-metrics.md
    │   ├── 04-data-access-contracts-and-sharing-under-confidentiality.md
    │   ├── 05-learning-from-small-noisy-and-proprietary-datasets.md
    │   ├── 06-safety-cases-and-failure-mode-analysis-for-ml-systems-in-regulated-domains.md
    │   ├── 07-documentation-for-audits-across-finance-healthcare-and-industry.md
    │   ├── 08-change-management.md
    │   ├── 09-choosing-a-first-domain.md
    │   └── README.md
    ├── 20-G9-Capstones/
    │   ├── 01-financial-risk-decision-platform.md
    │   ├── 02-clinical-ai-study-with-external-validation.md
    │   ├── 03-geospatial-earth-observation-system.md
    │   ├── 04-industrial-condition-monitoring-and-maintenance-system.md
    │   ├── 05-scientific-ml-reproduction-study.md
    │   ├── 06-g9-readiness-assessment.md
    │   └── README.md
    └── README.md
```

### 00 — G9 Overview

**Purpose:** the single authoritative plan for G9 with scope, boundaries, prerequisite map, dataset and access register, regulatory source register, evaluation standards and completion gate.

- `01-g9-scope-and-boundaries-with-earlier-stages-and-groups.md` — what G9 teaches and what it leaves to other groups.
- `02-prerequisite-map-from-the-roadmap.md` — Roadmap stages and groups assumed for each G9 module.
- `03-dataset-and-tooling-register.md` — every dataset with licence, access route and credentialing steps, and every library with version and maintenance status.
- `04-evaluation-and-reporting-standards.md` — time-aware, group-aware and spatial validation rules, domain metrics and report template.
- `05-completion-gate.md` — measurable criteria to finish G9.
- `learning-plan.md` — recommended order, per-domain tracks and how to pick one primary domain.
- A regulatory source register template: for every regulatory or guideline statement used, record the issuing body, document, version, date accessed and the exact passage relied on.

**Project 1: g9 domain data register and validation bootstrap**  
- Data: one small public dataset from each of three domains of your choice.  
- Task: build a reproducible workspace with pinned tooling, a dataset register recording licence and access conditions, and a validation harness that supports time-ordered, group-wise and spatial-block splits.  
- Deliverables: lockfile, register, harness and smoke tests.  
- Pass gate: a clean machine reproduces the tests from the lockfile, and a deliberately leaky split of each type (time, group, spatial) is rejected by the harness.

### 01 — Fraud and Financial Crime Detection Systems

**Outcome:** Design fraud and anti-money-laundering detection as an adversarial, delayed-label decision system. Imbalanced learning, alert capacity, anomaly detection and graph-based fraud detection are covered in Stages 5B and G8, and the real-time fraud and risk platform architecture case in Stage 2D.

**Lessons**

- `01-fraud-taxonomy.md` — Fraud taxonomy: card-not-present, account takeover, payment-rail fraud, merchant fraud, synthetic identity, first-party and claims fraud
- `02-label-delay-and-label-bias.md` — Label delay and label bias: chargebacks, investigations and unobserved fraud
- `03-adversarial-adaptation.md` — Adversarial adaptation: concept drift caused by attackers and what it does to models
- `04-behavioral-and-device-features.md` — Behavioral and device features: velocity, session, device fingerprint and behavioral biometrics
- `05-rules-plus-models.md` — Rules plus models: hybrid decisioning, rule mining and rule retirement
- `06-real-time-decision-constraints.md` — Real-time decision constraints: latency budgets, feature availability and decision outcomes beyond approve or decline
- `07-case-management.md` — Case management: investigator workflows, feedback capture and label quality
- `08-anti-money-laundering.md` — Anti-money-laundering: transaction monitoring, typologies, alert triage and suspicious-activity reporting
- `09-sanctions-and-watchlist-screening.md` — Sanctions and watchlist screening: name matching and false-positive control
- `10-payment-rail-specifics-for-india.md` — Payment-rail specifics for India: UPI and instant-payment risk patterns
- `11-evaluating-under-delay.md` — Evaluating under delay: cost-based metrics, maturation windows and champion-challenger comparison

**Hands-on projects**

- **Project 1: delayed label fraud model with maturation windows**  
  - Data: IEEE-CIS Fraud Detection (Kaggle) or the Bank Account Fraud dataset suite  
  - Task: Build a fraud model with time-ordered splits, simulate label delay and compare training on immature against matured labels.  
  - Deliverables: Pipeline and delay-impact analysis.  
  - Pass gate: Evaluation uses only labels that would have been known at decision time.
- **Project 2: aml transaction monitoring triage**  
  - Data: IBM synthetic AML transaction data or a simulator you build with known laundering patterns  
  - Task: Build alert generation and ML triage and measure typology recall, false-positive reduction and investigator workload.  
  - Deliverables: System and workload analysis.  
  - Pass gate: Typology recall reported per pattern, not only overall.
- **Project 3: name matching for sanctions screening**  
  - Data: A public sanctions list and synthetic name variants including Indian-name transliterations  
  - Task: Compare rule-based, phonetic and learned matching on recall at a fixed review volume.  
  - Deliverables: Matching comparison.  
  - Pass gate: Variants generated by a documented procedure.

### 02 — Credit Risk and Lending ML

**Outcome:** Build and validate credit models the way lenders use them. WOE scorecards, reason codes and PSI are covered in G1, reject inference concepts in G1, survival analysis in G1 and imbalanced learning in Stage 5B.

**Lessons**

- `01-credit-risk-components.md` — Credit risk components: probability of default, loss given default and exposure at default
- `02-expected-credit-loss-and-provisioning-concepts-under-ifrs-9-and-similar-standards.md` — Expected credit loss and provisioning concepts under IFRS 9 and similar standards
- `03-application-vs-behavioral-scoring-and-the-lending-lifecycle.md` — Application vs behavioral scoring and the lending lifecycle
- `04-thin-file-and-alternative-data-borrowers.md` — Thin-file and alternative-data borrowers: bureau data, bank-statement and account-aggregator data in India
- `05-loss-given-default-and-exposure-modeling-with-censored-and-long-horizon-outcomes.md` — Loss-given-default and exposure modeling with censored and long-horizon outcomes
- `06-vintage-and-cohort-analysis.md` — Vintage and cohort analysis: roll rates and delinquency curves
- `07-backtesting-and-monitoring-credit-models.md` — Backtesting and monitoring credit models: discrimination, calibration and stability over time
- `08-stress-testing-and-macro-scenarios-for-portfolios.md` — Stress testing and macro scenarios for portfolios
- `09-collections-and-early-warning-models.md` — Collections and early-warning models
- `10-fair-lending-and-explainability-obligations-with-india-s-digital-lending-rules-to-be-checked-in-primary-sources.md` — Fair lending and explainability obligations, with India's digital lending rules to be checked in primary sources

**Hands-on projects**

- **Project 1: pd model with vintage and calibration analysis**  
  - Data: Freddie Mac Single-Family Loan-Level data (public) or Home Credit  
  - Task: Build a PD model with out-of-time validation and vintage curves and test calibration drift across origination years.  
  - Deliverables: Model and vintage report.  
  - Pass gate: Out-of-time and out-of-vintage validation used.
- **Project 2: loss given default and ecl estimation**  
  - Data: Freddie Mac loan-level data  
  - Task: Estimate LGD with censoring-aware methods and combine PD, LGD and EAD into portfolio expected loss.  
  - Deliverables: ECL estimate with uncertainty.  
  - Pass gate: Components validated separately and in combination.
- **Project 3: credit model stress test**  
  - Data: The PD model and public macro series such as FRED data  
  - Task: Link default rates to macro scenarios and report portfolio loss under baseline and adverse paths.  
  - Deliverables: Stress-test report.  
  - Pass gate: Scenario assumptions documented with sources.

### 03 — Model Risk Management and Regulated Model Governance

**Outcome:** Run models under independent validation and regulatory expectations. General responsible-AI methods are covered later in G12; this module covers governance as practiced in financial services.

**Lessons**

- `01-model-risk.md` — Model risk: why models fail and what supervisors expect
- `02-model-lifecycle-governance.md` — Model lifecycle governance: inventory, tiering, ownership and change control
- `03-independent-validation.md` — Independent validation: conceptual soundness, data checks and outcome analysis
- `04-ongoing-monitoring.md` — Ongoing monitoring: thresholds, escalation and model retirement
- `05-documentation-standards.md` — Documentation standards: development, validation and use limitations
- `06-challenger-models-and-benchmarking-as-validation-tools.md` — Challenger models and benchmarking as validation tools
- `07-ai-specific-governance-frameworks.md` — AI-specific governance frameworks: NIST AI RMF, ISO/IEC 42001 and India's RBI FREE-AI recommendations
- `08-explainability-and-adverse-decision-communication-in-regulated-settings.md` — Explainability and adverse-decision communication in regulated settings
- `09-third-party-and-vendor-model-risk.md` — Third-party and vendor model risk
- `10-incident-reporting-and-audit-trails.md` — Incident reporting and audit trails

**Hands-on projects**

- **Project 1: model validation report for your own credit model**  
  - Data: The credit model from module 02  
  - Task: Act as an independent validator: test conceptual soundness, data, performance and limitations and write a validation report.  
  - Deliverables: Validation report with findings and severity.  
  - Pass gate: Findings backed by reproducible tests.
- **Project 2: model inventory and tiering system**  
  - Data: Models you built across G1 to G9  
  - Task: Build an inventory with risk tiers, owners, monitoring thresholds and review dates.  
  - Deliverables: Inventory tooling and an example inventory.  
  - Pass gate: Tiering criteria written before assigning tiers.
- **Project 3: governance gap analysis against free ai**  
  - Data: A hypothetical lender's AI practices  
  - Task: Map practices to the FREE-AI report's recommendations and NIST AI RMF and list gaps with remediation.  
  - Deliverables: Gap analysis.  
  - Pass gate: Each requirement cited from the primary document.

### 04 — Financial Time Series and Market Data ML

**Outcome:** Research market-data models without fooling yourself. Forecasting methods, GARCH and backtesting basics are covered in Stage 5B and G5; this module covers what is specific to financial data. This is research education, not investment advice, and the module forbids live trading.

**Lessons**

- `01-market-data-structure.md` — Market data structure: ticks, bars, adjusted prices and survivorship and look-ahead biases
- `02-information-driven-bars-and-sampling.md` — Information-driven bars and sampling: time, volume and dollar bars
- `03-labeling.md` — Labeling: triple-barrier labels and meta-labeling
- `04-stationarity-with-memory.md` — Stationarity with memory: fractional differentiation
- `05-backtest-overfitting.md` — Backtest overfitting: multiple testing, the deflated Sharpe ratio and probability of backtest overfitting
- `06-purged-and-embargoed-cross-validation-for-overlapping-labels.md` — Purged and embargoed cross-validation for overlapping labels
- `07-transaction-costs-slippage-and-capacity.md` — Transaction costs, slippage and capacity
- `08-factor-models-and-portfolio-construction-with-shrinkage-covariance-estimates.md` — Factor models and portfolio construction with shrinkage covariance estimates
- `09-risk-measures.md` — Risk measures: value at risk, expected shortfall and their backtests
- `10-market-regimes-and-non-stationarity.md` — Market regimes and non-stationarity
- `11-indian-market-context.md` — Indian market context: exchange data sources and securities-regulator rules on algorithmic trading and research, to be checked in primary sources

**Hands-on projects**

- **Project 1: backtest overfitting demonstration**  
  - Data: Free daily price data and a pool of simulated and real signals  
  - Task: Generate many strategy variants, show how the best backtest is illusory and measure deflated performance.  
  - Deliverables: Demonstration with corrected statistics.  
  - Pass gate: Number of trials recorded and used in the correction.
- **Project 2: triple barrier labeling and purged cv pipeline**  
  - Data: Free intraday or daily data such as public crypto exchange data  
  - Task: Build labeling and purged, embargoed cross-validation and compare with naive k-fold on inflated scores.  
  - Deliverables: Pipeline and leakage-gap analysis.  
  - Pass gate: Purge and embargo lengths derived from label horizons.
- **Project 3: factor model and risk report**  
  - Data: Kenneth French factor data and a public index universe  
  - Task: Estimate factor exposures, build a risk report with VaR and expected shortfall and backtest the risk model.  
  - Deliverables: Risk report and backtest.  
  - Pass gate: VaR violations tested statistically.

### 05 — Insurance Pricing and Quantitative Risk Models

**Outcome:** Model insurance losses and portfolio risk with the methods actuaries and risk teams use. Tweedie objectives are covered in G1 and survival models in G1.

**Lessons**

- `01-insurance-data-and-exposure.md` — Insurance data and exposure: frequency, severity and exposure offsets
- `02-frequency-severity-and-pure-premium-modeling-with-glms-and-gradient-boosting.md` — Frequency-severity and pure-premium modeling with GLMs and gradient boosting
- `03-claims-development-and-reserving.md` — Claims development and reserving: chain-ladder methods and ML extensions
- `04-telematics-and-usage-based-pricing-features.md` — Telematics and usage-based pricing features
- `05-pricing-governance.md` — Pricing governance: explainability, monotonic constraints and fairness
- `06-claims-triage-and-fraud-signals-in-insurance.md` — Claims triage and fraud signals in insurance
- `07-catastrophe-and-tail-risk.md` — Catastrophe and tail risk: extreme value theory basics
- `08-portfolio-risk-aggregation-and-dependence-with-copulas-from-g7.md` — Portfolio risk aggregation and dependence with copulas from G7
- `09-evaluating-pricing-models.md` — Evaluating pricing models: Gini, lift and loss ratios by segment
- `10-insurance-regulation-in-india.md` — Insurance regulation in India: the insurance regulator's expectations to be checked in primary sources

**Hands-on projects**

- **Project 1: frequency severity pricing model**  
  - Data: freMTPL2 motor insurance data (OpenML)  
  - Task: Build GLM and gradient-boosting frequency and severity models with exposure offsets and compare on pure premium lift.  
  - Deliverables: Pricing models and lift charts.  
  - Pass gate: Exposure handled correctly and verified in tests.
- **Project 2: loss reserving with triangles**  
  - Data: A public run-off triangle dataset such as those in the chainladder package  
  - Task: Compare chain-ladder, Mack variability estimates and an ML-based reserve and evaluate on later development.  
  - Deliverables: Reserve comparison.  
  - Pass gate: Evaluation uses later development periods not used in fitting.
- **Project 3: tail risk with evt**  
  - Data: Public large-loss data such as Danish fire losses  
  - Task: Fit peaks-over-threshold models and compare tail estimates with a normal assumption.  
  - Deliverables: Tail-risk report.  
  - Pass gate: Threshold stability analyzed.

### 06 — Geospatial Data Foundations

**Outcome:** Handle geographic data correctly before modeling it. The Roadmap has no GIS lessons, so this module starts from the basics.

**Lessons**

- `01-coordinate-reference-systems-and-projections.md` — Coordinate reference systems and projections: why distance and area calculations go wrong
- `02-vector-data.md` — Vector data: points, lines and polygons with GeoPandas, Shapely and PyProj
- `03-spatial-joins-indexes-and-the-r-tree.md` — Spatial joins, indexes and the R-tree: making geometry queries fast
- `04-discrete-global-grids.md` — Discrete global grids: H3 and S2 cells for aggregation and joins
- `05-postgis-basics.md` — PostGIS basics: spatial SQL for large datasets
- `06-raster-data.md` — Raster data: rasterio, xarray and cloud-optimized GeoTIFF
- `07-catalogs-and-access.md` — Catalogs and access: STAC and public sources such as Sentinel, Landsat, OpenStreetMap and Indian government geospatial portals
- `08-geocoding-and-address-handling.md` — Geocoding and address handling: Indian address quality and matching using entity resolution from G1
- `09-gps-traces.md` — GPS traces: cleaning, map matching and privacy risks of location data
- `10-spatial-data-quality.md` — Spatial data quality: topology errors, resolution and positional accuracy

**Hands-on projects**

- **Project 1: projection and area error audit**  
  - Data: Administrative boundary data for India and world regions  
  - Task: Compute areas and distances in several projections and show where each fails.  
  - Deliverables: Error audit and rules of thumb.  
  - Pass gate: Results compared against geodesic calculations.
- **Project 2: h3 aggregation and spatial join pipeline**  
  - Data: Point-of-interest data from OpenStreetMap and a public mobility dataset  
  - Task: Build a pipeline that aggregates points to H3 cells and joins to polygons and compare with direct spatial joins on speed and accuracy.  
  - Deliverables: Pipeline and benchmark.  
  - Pass gate: Both methods checked against a brute-force result on a sample.
- **Project 3: address geocoding quality study**  
  - Data: Synthetic and public Indian address strings  
  - Task: Geocode with several services or tools and measure accuracy and failure patterns by address type.  
  - Deliverables: Quality report.  
  - Pass gate: Terms of service of each geocoder respected.

### 07 — Spatial Statistics and Spatial Machine Learning

**Outcome:** Model location-dependent data without leaking neighbors into test sets. Gaussian processes are covered in G7 and spatio-temporal graph forecasting in G5 and G8.

**Lessons**

- `01-spatial-autocorrelation.md` — Spatial autocorrelation: Moran's I and local indicators
- `02-why-random-cross-validation-fails-on-spatial-data-and-spatial-block-validation.md` — Why random cross-validation fails on spatial data and spatial block validation
- `03-geographically-weighted-regression-and-spatial-lag-and-error-models.md` — Geographically weighted regression and spatial lag and error models
- `04-kriging-and-geostatistics-as-spatial-gaussian-processes.md` — Kriging and geostatistics as spatial Gaussian processes
- `05-hotspot-analysis-and-kernel-density-estimation.md` — Hotspot analysis and kernel density estimation
- `06-spatial-feature-engineering.md` — Spatial feature engineering: distance to features, neighborhood aggregates and cell features
- `07-location-intelligence.md` — Location intelligence: catchment analysis and site selection
- `08-mobility-data.md` — Mobility data: origin-destination flows and privacy
- `09-evaluating-spatial-models.md` — Evaluating spatial models: spatial residual checks and transfer to new regions

**Hands-on projects**

- **Project 1: spatial cv vs random cv leakage study**  
  - Data: A spatial regression dataset such as house prices or air-quality measurements with coordinates  
  - Task: Show inflated scores under random cross-validation and honest scores under spatial block validation for several model types.  
  - Deliverables: Leakage-gap analysis.  
  - Pass gate: Block size chosen from the spatial autocorrelation range.
- **Project 2: site selection model**  
  - Data: Public demographic, points-of-interest and foot-traffic proxy data  
  - Task: Build a store or facility site-scoring model with spatial features and validate on held-out regions.  
  - Deliverables: Model and regional validation.  
  - Pass gate: Validation regions geographically separated from training.
- **Project 3: kriging vs ml interpolation**  
  - Data: Sparse sensor measurements such as air quality or rainfall  
  - Task: Compare kriging, GBDT with coordinates and spatial features and a spatial GP on interpolation error.  
  - Deliverables: Comparison with intervals.  
  - Pass gate: Held-out sites chosen by spatial blocks.

### 08 — Remote Sensing and Earth Observation ML

**Outcome:** Train models on satellite imagery and Earth-observation data. Segmentation, detection and transfer learning are covered in Stage 5C and G2; this module covers the data and the domain-specific pitfalls.

**Lessons**

- `01-satellite-sensors-and-products.md` — Satellite sensors and products: optical, multispectral and radar and their resolutions
- `02-preprocessing.md` — Preprocessing: atmospheric correction, cloud masking and compositing
- `03-spectral-indices.md` — Spectral indices: NDVI, NDWI and what they measure
- `04-scene-classification-and-land-cover-segmentation-with-torchgeo.md` — Scene classification and land-cover segmentation with torchgeo
- `05-change-detection-and-image-time-series.md` — Change detection and image time series: crop phenology and seasonal patterns
- `06-synthetic-aperture-radar.md` — Synthetic aperture radar: flood mapping and all-weather monitoring
- `07-geospatial-foundation-models.md` — Geospatial foundation models: Prithvi-style models, fine-tuning and their evidence
- `08-labels-for-earth-observation.md` — Labels for Earth observation: sparse, noisy and region-specific labels
- `09-domain-shift-across-regions-seasons-and-sensors.md` — Domain shift across regions, seasons and sensors
- `10-applications-with-indian-relevance.md` — Applications with Indian relevance: crop mapping and yield, flood extent, urban growth and air quality

**Hands-on projects**

- **Project 1: crop type mapping from time series imagery**  
  - Data: Sentinel-2 time series with public crop labels  
  - Task: Build a crop classifier on image time series and test on a held-out region and season.  
  - Deliverables: Model and shift analysis.  
  - Pass gate: Held-out region and year, not random pixels.
- **Project 2: flood mapping with sar**  
  - Data: Sentinel-1 flood datasets such as Sen1Floods11  
  - Task: Segment flooded areas and compare optical and radar inputs and a pretrained foundation model.  
  - Deliverables: Segmentation comparison.  
  - Pass gate: Metrics reported per event and region.
- **Project 3: geospatial foundation model evaluation**  
  - Data: EuroSAT, BigEarthNet or a regional task  
  - Task: Compare a pretrained geospatial foundation model with an ImageNet-pretrained model and a small task-specific model under few labels.  
  - Deliverables: Label-budget comparison.  
  - Pass gate: Same splits and tuning budgets for all models.

### 09 — Clinical Data and Healthcare ML Foundations

**Outcome:** Understand clinical data, its standards and its traps before modeling. The Roadmap has no healthcare lessons, so this module starts from the basics.

**Lessons**

- `01-healthcare-data-landscape.md` — Healthcare data landscape: EHR, claims, registries, devices and imaging
- `02-medical-coding-systems.md` — Medical coding systems: ICD-10, SNOMED CT, LOINC and RxNorm
- `03-interoperability.md` — Interoperability: HL7 FHIR and the OMOP common data model
- `04-india-s-digital-health-context.md` — India's digital health context: ABDM and related standards, to be checked in primary sources
- `05-de-identification-and-privacy.md` — De-identification and privacy: HIPAA-style methods and India's DPDP Act
- `06-defining-cohorts-and-labels.md` — Defining cohorts and labels: computable phenotypes and prediction time
- `07-irregular-and-informative-measurement.md` — Irregular and informative measurement: missingness that carries information
- `08-healthcare-specific-leakage.md` — Healthcare-specific leakage: future labs, treatment effects on labels and patient overlap across splits
- `09-access-and-ethics.md` — Access and ethics: credentialed datasets, ethics boards and consent

**Hands-on projects**

- **Project 1: omop style cohort and label pipeline**  
  - Data: MIMIC-IV demo or a synthetic EHR dataset such as Synthea  
  - Task: Define a cohort and prediction time, build labels and features and write tests that catch leakage of post-prediction information.  
  - Deliverables: Pipeline and leakage tests.  
  - Pass gate: Each feature timestamped before the prediction time.
- **Project 2: coding system mapping exercise**  
  - Data: Public code sets and synthetic records  
  - Task: Map local codes to standard vocabularies and measure how mapping errors change cohort size.  
  - Deliverables: Mapping tool and sensitivity analysis.  
  - Pass gate: Mapping accuracy verified against a labeled sample.
- **Project 3: deidentification risk assessment**  
  - Data: Synthetic patient records with quasi-identifiers  
  - Task: Test re-identification risk before and after de-identification and report the utility cost.  
  - Deliverables: Risk assessment.  
  - Pass gate: Only synthetic data used.

### 10 — Clinical Prediction and Decision Support Models

**Outcome:** Build and evaluate prediction models that could support clinical decisions. Calibration and survival modeling are covered in Stage 5B and G1; this module covers clinical validation and reporting.

**Lessons**

- `01-clinical-prediction-targets.md` — Clinical prediction targets: diagnosis, prognosis, deterioration and readmission
- `02-reporting-and-bias-standards.md` — Reporting and bias standards: TRIPOD+AI and PROBAST
- `03-time-aware-design.md` — Time-aware design: prediction at a defined time and rolling or landmark prediction
- `04-decision-curve-analysis.md` — Decision curve analysis: net benefit instead of accuracy
- `05-external-and-temporal-validation.md` — External and temporal validation: why internal validation overstates performance
- `06-calibration-drift-and-updating-models.md` — Calibration drift and updating models
- `07-subgroup-performance-and-equity-checks-across-patient-groups.md` — Subgroup performance and equity checks across patient groups
- `08-alerting-and-workflow.md` — Alerting and workflow: alert fatigue and clinician interaction
- `09-case-study.md` — Case study: published critiques of deployed sepsis-prediction models
- `10-uncertainty-and-abstention-for-clinical-use-using-methods-from-g7.md` — Uncertainty and abstention for clinical use using methods from G7

**Hands-on projects**

- **Project 1: sepsis early warning with clinical validation**  
  - Data: PhysioNet/Computing in Cardiology 2019 sepsis challenge data  
  - Task: Build an early-warning model with hospital-wise external validation, decision curves and alert-burden analysis.  
  - Deliverables: Model, validation and reporting-checklist assessment.  
  - Pass gate: Validated on a hospital not used in training.
- **Project 2: tripod ai and probast self audit**  
  - Data: A published clinical prediction paper with public data  
  - Task: Audit the paper against TRIPOD+AI and PROBAST and rerun key analyses with corrected methods.  
  - Deliverables: Audit report.  
  - Pass gate: Every checklist item scored with evidence.
- **Project 3: calibration drift and model updating study**  
  - Data: Multi-year clinical data  
  - Task: Measure calibration drift over time and compare recalibration, refitting and rolling updates.  
  - Deliverables: Drift and update analysis.  
  - Pass gate: Evaluation always on later data than fitting.

### 11 — Medical Imaging and Biosignal ML

**Outcome:** Train and validate models on medical images and physiological signals. General computer vision is covered in Stage 5C and G2; this module covers the medical specifics.

**Lessons**

- `01-medical-image-formats-and-handling.md` — Medical image formats and handling: DICOM, windowing and metadata
- `02-modalities.md` — Modalities: radiographs, CT, MRI, ultrasound and pathology slides
- `03-annotation-in-medicine.md` — Annotation in medicine: expert variability and consensus labels
- `04-3d-and-volumetric-segmentation.md` — 3D and volumetric segmentation: nnU-Net and MONAI
- `05-whole-slide-pathology.md` — Whole-slide pathology: multiple-instance learning
- `06-medical-foundation-models.md` — Medical foundation models: capabilities, limits and evaluation
- `07-biosignals.md` — Biosignals: ECG and EEG preprocessing and models
- `08-shortcut-learning-in-medical-imaging.md` — Shortcut learning in medical imaging: hospital markers, devices and demographics
- `09-evaluation.md` — Evaluation: Dice, AUROC with confidence intervals, reader studies and external test sets
- `10-explainability-limits-and-failure-analysis-for-medical-models.md` — Explainability limits and failure analysis for medical models

**Hands-on projects**

- **Project 1: chest xray classification with shortcut audit**  
  - Data: NIH ChestX-ray14 or CheXpert, with licence terms accepted  
  - Task: Train a classifier, test for shortcuts such as devices and labels in images and evaluate on an external dataset.  
  - Deliverables: Model, shortcut audit and external-validation results.  
  - Pass gate: External test from a different institution.
- **Project 2: volumetric segmentation with nnu net**  
  - Data: A Medical Segmentation Decathlon task  
  - Task: Train and evaluate a 3D segmentation model and analyze failures by case difficulty.  
  - Deliverables: Model and failure analysis.  
  - Pass gate: Patient-level splits enforced.
- **Project 3: ecg classification with patient level evaluation**  
  - Data: PTB-XL or MIT-BIH  
  - Task: Train an ECG classifier and compare record-level with patient-level splits.  
  - Deliverables: Leakage-gap analysis.  
  - Pass gate: Patients never shared across splits.

### 12 — Biomedical and Life Science ML

**Outcome:** Apply ML to molecules, proteins, omics and the biomedical literature, with realistic evaluation. Physical-simulation ML and materials are in modules 14 and 15; molecular GNN architectures are in G8.

**Lessons**

- `01-biology-for-ml-engineers.md` — Biology for ML engineers: sequences, structures and assays and what their noise looks like
- `02-protein-ml.md` — Protein ML: sequence embeddings and using predicted structures
- `03-drug-discovery-pipeline.md` — Drug discovery pipeline: QSAR, virtual screening and ADMET prediction
- `04-realistic-evaluation-in-drug-discovery.md` — Realistic evaluation in drug discovery: scaffold and time splits and benchmark leakage
- `05-generative-chemistry.md` — Generative chemistry: capabilities, validity and synthesizability checks
- `06-omics-data.md` — Omics data: high-dimensional low-sample problems and batch effects
- `07-biomedical-text-mining.md` — Biomedical text mining: domain-adapted language models from G2 applied to literature
- `08-clinical-trial-ml.md` — Clinical trial ML: patient matching, site selection and enrollment forecasting
- `09-biostatistics-essentials.md` — Biostatistics essentials: trial design, interim analyses and reporting guidelines

**Hands-on projects**

- **Project 1: admet prediction with honest splits**  
  - Data: Therapeutics Data Commons ADMET tasks  
  - Task: Compare fingerprint GBDT, GNN and pretrained molecular models under random, scaffold and time splits.  
  - Deliverables: Benchmark under several splits.  
  - Pass gate: Split type reported with every number.
- **Project 2: batch effect detection in omics**  
  - Data: A public gene-expression dataset with known batches  
  - Task: Show how batch effects create spurious predictors and compare correction methods.  
  - Deliverables: Batch-effect analysis.  
  - Pass gate: Batch information held out in evaluation.
- **Project 3: biomedical literature mining pipeline**  
  - Data: PubMed abstracts on a chosen topic  
  - Task: Build entity extraction and relation mining and validate against a hand-labeled sample.  
  - Deliverables: Pipeline and validation.  
  - Pass gate: Hand-labeled sample of at least 200 sentences.

### 13 — Healthcare Regulation Safety and Deployment

**Outcome:** Move a healthcare model from research toward safe use. Regulatory statements in this module must be confirmed from primary sources at the time of use.

**Lessons**

- `01-software-as-a-medical-device.md` — Software as a medical device: classification by clinical consequence
- `02-india-s-medical-device-rules-and-software-guidance-to-be-checked-in-primary-sources.md` — India's medical device rules and software guidance, to be checked in primary sources
- `03-united-states-and-european-frameworks.md` — United States and European frameworks: change-control plans and the EU AI Act for high-risk systems, to be checked in primary sources
- `04-icmr-ethical-guidance-for-ai-in-health-and-ethics-committee-review.md` — ICMR ethical guidance for AI in health and ethics-committee review
- `05-evidence-generation.md` — Evidence generation: retrospective study, silent trial, prospective study and reader study
- `06-reporting-guidelines.md` — Reporting guidelines: TRIPOD+AI, CONSORT-AI and DECIDE-AI
- `07-safety-engineering.md` — Safety engineering: hazard analysis and failure-mode analysis for ML systems
- `08-post-market-monitoring-and-updates.md` — Post-market monitoring and updates
- `09-equity.md` — Equity: dataset diversity and performance for Indian populations
- `10-privacy-security-and-consent-in-clinical-deployment.md` — Privacy, security and consent in clinical deployment

**Hands-on projects**

- **Project 1: regulatory classification and evidence plan**  
  - Data: A hypothetical clinical AI product  
  - Task: Classify the product under applicable frameworks, define the intended use and write an evidence-generation plan.  
  - Deliverables: Classification memo and evidence plan.  
  - Pass gate: Every regulatory claim cited to a primary source with the date accessed.
- **Project 2: hazard analysis for a clinical model**  
  - Data: The model from module 10  
  - Task: Run a hazard and failure-mode analysis covering data, model, workflow and human factors.  
  - Deliverables: Hazard log with mitigations.  
  - Pass gate: Each mitigation maps to a test or monitor.
- **Project 3: silent trial protocol and monitoring plan**  
  - Data: Simulated clinical workflow data  
  - Task: Design a silent trial and post-deployment monitoring plan and test it on simulated drift.  
  - Deliverables: Protocol and simulation.  
  - Pass gate: Drift scenarios trigger the planned alarms.

### 14 — Scientific ML Surrogates and Physics Informed Learning

**Outcome:** Use ML inside scientific and engineering simulation workflows. Differential-equation mathematics is outside the Roadmap's ML scope, so the needed background is taught as part of each lesson.

**Lessons**

- `01-when-ml-helps-in-science.md` — When ML helps in science: surrogates, inverse problems and discovery
- `02-scientific-data-formats.md` — Scientific data formats: NetCDF, HDF5, Zarr and xarray
- `03-surrogate-modeling-of-expensive-simulators-with-sampling-design-and-uncertainty-from-g7.md` — Surrogate modeling of expensive simulators with sampling design and uncertainty from G7
- `04-physics-informed-neural-networks.md` — Physics-informed neural networks: formulation and training pathologies
- `05-neural-operators.md` — Neural operators: Fourier neural operators and DeepONet
- `06-evaluating-scientific-surrogates.md` — Evaluating scientific surrogates: extrapolation, conservation laws and stability of rollouts
- `07-equation-discovery.md` — Equation discovery: sparse regression and symbolic regression
- `08-differentiable-simulation-with-jax.md` — Differentiable simulation with JAX
- `09-weather-and-climate-ml.md` — Weather and climate ML: data sources such as ERA5 and models such as GraphCast
- `10-data-assimilation-and-its-link-to-the-kalman-filtering-of-g5.md` — Data assimilation and its link to the Kalman filtering of G5

**Hands-on projects**

- **Project 1: pinn vs numerical solver benchmark**  
  - Data: Standard PDE problems such as Burgers' and Poisson equations  
  - Task: Train PINNs and compare accuracy and cost with a classical numerical solver, documenting training failures.  
  - Deliverables: Benchmark and failure catalog.  
  - Pass gate: Reference solutions from a verified numerical solver.
- **Project 2: neural operator extrapolation study**  
  - Data: PDEBench tasks  
  - Task: Compare FNO, DeepONet and a CNN baseline on in-distribution and out-of-distribution parameters and long rollouts.  
  - Deliverables: Comparison with rollout-error curves.  
  - Pass gate: Out-of-distribution tests defined before training.
- **Project 3: equation discovery from noisy data**  
  - Data: Simulated dynamical systems and a real experimental dataset  
  - Task: Recover governing equations with sparse regression and symbolic regression under increasing noise.  
  - Deliverables: Recovery analysis.  
  - Pass gate: Ground-truth equations known for simulated data.

### 15 — Molecular Materials and Simulation ML

**Outcome:** Learn from atomistic and materials data with models that respect physical symmetries.

**Lessons**

- `01-representing-atoms-and-materials.md` — Representing atoms and materials: descriptors, graphs and 3D coordinates
- `02-symmetry-and-equivariance.md` — Symmetry and equivariance: E(3)-equivariant networks
- `03-machine-learned-interatomic-potentials.md` — Machine-learned interatomic potentials: NequIP- and MACE-style models
- `04-molecular-dynamics-essentials-for-ml-users.md` — Molecular dynamics essentials for ML users
- `05-materials-property-prediction.md` — Materials property prediction: benchmarks such as Matbench and the Materials Project
- `06-datasets-and-leakage-in-atomistic-ml.md` — Datasets and leakage in atomistic ML: QM9, MD17 and Open Catalyst
- `07-active-learning-and-bayesian-optimization-loops-for-discovery-using-g7.md` — Active learning and Bayesian optimization loops for discovery using G7
- `08-generative-models-for-molecules-and-materials-and-their-validation.md` — Generative models for molecules and materials and their validation
- `09-reproducibility-and-baselines-in-scientific-ml.md` — Reproducibility and baselines in scientific ML

**Hands-on projects**

- **Project 1: equivariant model vs descriptor baseline**  
  - Data: QM9 or MD17  
  - Task: Compare an equivariant GNN with descriptor-based GBDT on accuracy, data efficiency and cost.  
  - Deliverables: Learning curves and cost table.  
  - Pass gate: Standard splits used and data-efficiency curves reported.
- **Project 2: materials property benchmark**  
  - Data: Matbench tasks  
  - Task: Compare composition-only and structure-based models and analyze when structure matters.  
  - Deliverables: Benchmark with intervals.  
  - Pass gate: Nested cross-validation following the benchmark protocol.
- **Project 3: active learning for discovery**  
  - Data: A materials or molecule dataset with a hidden property you reveal on request  
  - Task: Compare random, uncertainty-based and Bayesian-optimization selection for finding top candidates under a budget.  
  - Deliverables: Discovery-efficiency curves.  
  - Pass gate: Many repeated runs with intervals.

### 16 — Industrial Sensor Data and Condition Monitoring

**Outcome:** Turn machine and process signals into reliable features. Signal processing for audio in G2, anomaly detection in G5 and edge deployment in G10 are referenced, not repeated.

**Lessons**

- `01-industrial-data-sources.md` — Industrial data sources: sensors, PLCs, SCADA, historians and common protocols such as OPC UA and MQTT
- `02-vibration-analysis.md` — Vibration analysis: spectra, envelope analysis and time-frequency methods for rotating machinery
- `03-temperature-current-pressure-and-acoustic-signals-as-condition-indicators.md` — Temperature, current, pressure and acoustic signals as condition indicators
- `04-sensor-data-quality.md` — Sensor data quality: drift, calibration, dropouts and timestamp alignment
- `05-operating-condition-normalization.md` — Operating-condition normalization: separating wear from load and environment
- `06-failure-labels-from-maintenance-logs-and-work-orders.md` — Failure labels from maintenance logs and work orders: text mining and label uncertainty
- `07-health-indicators.md` — Health indicators: constructing and validating degradation signals
- `08-digital-twins.md` — Digital twins: what they are and what they add to ML
- `09-data-collection-design-for-new-monitoring-programs.md` — Data collection design for new monitoring programs

**Hands-on projects**

- **Project 1: bearing vibration feature engineering**  
  - Data: CWRU bearing data and the NASA IMS bearing dataset  
  - Task: Build time, frequency and envelope features and compare with raw-signal deep models on fault classification under different loads.  
  - Deliverables: Feature library and comparison.  
  - Pass gate: Test conditions differ from training load or machine.
- **Project 2: sensor data quality pipeline**  
  - Data: A public industrial sensor dataset with injected faults  
  - Task: Detect drift, dropouts and stuck sensors and measure the effect on downstream models.  
  - Deliverables: Pipeline and impact analysis.  
  - Pass gate: Injected faults detected at a measured rate.
- **Project 3: maintenance log label extraction**  
  - Data: Synthetic or public maintenance work-order text  
  - Task: Extract failure events and times from free text and measure label error against a manual sample.  
  - Deliverables: Extraction pipeline and error analysis.  
  - Pass gate: Manual sample of at least 200 records.

### 17 — Failure Prediction Remaining Useful Life and Maintenance Optimization

**Outcome:** Predict failures and turn predictions into maintenance decisions. Survival models are covered in G1, change detection in G5 and optimization under uncertainty in G8.

**Lessons**

- `01-problem-forms.md` — Problem forms: classification of imminent failure, remaining-useful-life regression and survival framing
- `02-degradation-models.md` — Degradation models: stochastic processes and filtering approaches
- `03-deep-learning-for-remaining-useful-life-and-the-pitfalls-of-common-benchmark-protocols.md` — Deep learning for remaining useful life and the pitfalls of common benchmark protocols
- `04-failure-mode-classification-and-root-cause.md` — Failure-mode classification and root cause
- `05-alarm-design-and-management.md` — Alarm design and management: thresholds, persistence and alarm floods
- `06-maintenance-policies.md` — Maintenance policies: run-to-failure, time-based and condition-based with cost models
- `07-spare-parts-planning-with-intermittent-demand-methods-from-g5.md` — Spare-parts planning with intermittent demand methods from G5
- `08-rare-failures.md` — Rare failures: very few events, simulation and transfer between machines
- `09-business-value.md` — Business value: downtime avoided, false-alarm cost and return on investment

**Hands-on projects**

- **Project 1: rul on c mapss with honest protocol**  
  - Data: NASA C-MAPSS turbofan degradation data  
  - Task: Compare survival, regression and deep models on RUL with proper per-engine splits and report the effect of common protocol shortcuts.  
  - Deliverables: Benchmark and protocol-sensitivity analysis.  
  - Pass gate: Splits by engine; evaluation protocol stated explicitly.
- **Project 2: condition based maintenance cost simulation**  
  - Data: Predictions from the RUL models and cost assumptions you state  
  - Task: Simulate maintenance policies driven by predictions and compare total cost with time-based and run-to-failure policies.  
  - Deliverables: Policy cost comparison.  
  - Pass gate: Cost parameters varied in a sensitivity analysis.
- **Project 3: hard drive failure prediction**  
  - Data: Backblaze hard-drive statistics  
  - Task: Predict failures with time-aware validation and measure lead time and false alarms.  
  - Deliverables: Model and lead-time analysis.  
  - Pass gate: Drives never shared across train and test.

### 18 — Manufacturing Process Quality and Optimization ML

**Outcome:** Apply ML to process quality, yield and control. SPC charts are covered in G5, Bayesian optimization in G7 and optimization in G8.

**Lessons**

- `01-process-data-structure.md` — Process data structure: batches, recipes and multistep processes
- `02-soft-sensors-and-virtual-metrology.md` — Soft sensors and virtual metrology: predicting hard-to-measure variables
- `03-yield-and-defect-prediction-under-high-dimensionality-and-few-failures.md` — Yield and defect prediction under high dimensionality and few failures
- `04-design-of-experiments-and-response-surface-methods-combined-with-bayesian-optimization.md` — Design of experiments and response-surface methods combined with Bayesian optimization
- `05-recipe-and-setpoint-optimization-with-constraints.md` — Recipe and setpoint optimization with constraints
- `06-wafer-map-and-defect-pattern-classification.md` — Wafer map and defect pattern classification
- `07-root-cause-analysis-in-processes-using-causal-tools-from-g7.md` — Root-cause analysis in processes using causal tools from G7
- `08-energy-and-resource-efficiency-optimization.md` — Energy and resource efficiency optimization
- `09-deploying-models-on-the-shop-floor.md` — Deploying models on the shop floor: operator interfaces and change control

**Hands-on projects**

- **Project 1: semiconductor yield prediction on secom**  
  - Data: UCI SECOM dataset  
  - Task: Build a yield predictor with feature selection suited to few failures and time-ordered validation.  
  - Deliverables: Model and honest-evaluation report.  
  - Pass gate: Time-ordered splits and a stated failure count.
- **Project 2: process fault detection on tennessee eastman**  
  - Data: Tennessee Eastman process data  
  - Task: Compare PCA-based, SPC and deep detectors on detection delay and false alarms by fault type.  
  - Deliverables: Per-fault results.  
  - Pass gate: Detection delay reported per fault.
- **Project 3: wafer map defect classification**  
  - Data: WM-811K wafer maps  
  - Task: Train a defect-pattern classifier handling severe class imbalance and unlabeled maps.  
  - Deliverables: Model and per-class analysis.  
  - Pass gate: Per-class metrics reported.

### 19 — Domain Project Delivery and Cross Domain Practice

**Outcome:** Work effectively with domain experts and regulators and choose a domain deliberately. This applies to all six domains.

**Lessons**

- `01-working-with-domain-experts.md` — Working with domain experts: elicitation, shared vocabulary and expert-labeled data
- `02-validation-ladder.md` — Validation ladder: in-silico, retrospective, silent and prospective stages
- `03-domain-specific-metrics.md` — Domain-specific metrics: net benefit, cost curves and regulatory measures
- `04-data-access-contracts-and-sharing-under-confidentiality.md` — Data access, contracts and sharing under confidentiality
- `05-learning-from-small-noisy-and-proprietary-datasets.md` — Learning from small, noisy and proprietary datasets
- `06-safety-cases-and-failure-mode-analysis-for-ml-systems-in-regulated-domains.md` — Safety cases and failure-mode analysis for ML systems in regulated domains
- `07-documentation-for-audits-across-finance-healthcare-and-industry.md` — Documentation for audits across finance, healthcare and industry
- `08-change-management.md` — Change management: getting models adopted by operators and clinicians
- `09-choosing-a-first-domain.md` — Choosing a first domain: mapping Indian industry demand in banking and finance, healthcare, agriculture, manufacturing and energy to your strengths

**Hands-on projects**

- **Project 1: expert elicitation and labeling protocol**  
  - Data: A domain problem of your choice with two available experts or public expert annotations  
  - Task: Run elicitation, build labeling guidelines, measure expert agreement and report how disagreement limits model quality.  
  - Deliverables: Protocol and agreement analysis.  
  - Pass gate: Agreement statistic reported with the effect on achievable performance.
- **Project 2: validation ladder plan**  
  - Data: A model from earlier modules  
  - Task: Write the staged validation plan with entry and exit criteria for each stage.  
  - Deliverables: Plan document.  
  - Pass gate: Each stage has a measurable pass criterion.
- **Project 3: domain choice memo**  
  - Data: Public job-market and sector data  
  - Task: Evaluate three candidate domains on demand, data access, regulation and your skills and recommend one.  
  - Deliverables: Decision memo.  
  - Pass gate: Sources cited and dated.

### 20 — G9 Capstones

**Outcome:** integrate the six domain tracks in assessed, portfolio-quality work. Choose one primary domain for depth and complete at least one other capstone for breadth.

- **Capstone 1: financial risk decision platform** (uses Modules 01 to 05)  
  Build a fraud or credit risk decision system with delayed-label handling, validation as an independent reviewer, governance documentation and a stress or backtest analysis.
- **Capstone 2: clinical ai study with external validation** (uses Modules 09 to 13)  
  Deliver a clinical prediction or imaging study with cohort definition, external validation, decision-curve analysis, reporting-checklist audit and a regulatory and safety plan.
- **Capstone 3: geospatial earth observation system** (uses Modules 06 to 08)  
  Build a geospatial pipeline and model for a regional problem with spatial validation, region-shift testing and a data-source and licence register.
- **Capstone 4: industrial condition monitoring and maintenance system** (uses Modules 16 to 18)  
  Build a monitoring and failure-prediction system with sensor-quality handling, honest RUL evaluation, a maintenance-cost simulation and a plant deployment plan.
- **Capstone 5: scientific ml reproduction study** (uses Modules 14, 15)  
  Reproduce a scientific ML result, test it against strong classical baselines and out-of-distribution cases and report it honestly.
- **Capstone 6: g9 readiness assessment** (uses All modules)  
  Written and practical assessment against the G9 completion gate.

## G9 completion gate

- Every model uses the validation scheme the domain demands: out-of-time for finance and fraud, patient- and hospital-level for healthcare, spatial-block for geospatial, per-machine or per-engine for maintenance, and out-of-distribution parameters for scientific surrogates.
- Every domain result reports the domain's decision metric (expected cost, net benefit, lead time and false-alarm cost, or task-specific error) beside the statistical metric.
- Every result compares against a strong domain baseline (a scorecard, a clinical score, a physics or numerical solver, a threshold rule) and reports where the baseline wins.
- Every dataset has its licence, access route and any credentialing or ethics requirement recorded before use, and no project uses restricted data in ways its terms forbid.
- Every regulatory or guideline statement is cited to a primary source with the date accessed, and none is presented as legal advice.
- No project connects to live trading, real patients, real customers or real machinery; all deployments are simulated or use public or synthetic data.
- All results reproduce from a lockfile, configs and logged seeds, with library versions recorded.
- At least one negative or inconclusive result per domain track attempted is reported honestly.
- The capstones for the chosen domains are complete and the readiness assessment is passed.

## Audit and verification

**What was checked and the result**

- Structure: 19 specialist modules each have 6 to 12 lessons and at least one project; the tree contains 296 files and 41 folders, and these counts equal the counts computed from the curriculum data.
- Overlap with the Roadmap: all 184 lesson file names were compared against every lesson file name in `Roadmap.md`. Exact matches: 0. Near matches (similarity 0.80 or higher): 1 — `biosignals` vs Roadmap `signals` (0.82). Reviewed manually: the Stage 0 lesson is about operating-system signals, which is unrelated to biomedical signals.
- Structural problems found by the build script: 0.
- Topic-level overlap check: the Roadmap text was searched for credit, geospatial, GeoPandas, H3, raster, DICOM, clinical, EHR, FHIR, HIPAA, MIMIC, bioinformatics, protein, PDE, physics-informed networks, neural operators, volatility, IFRS, remaining useful life, vibration, SCADA, KYC, sanctions, stress tests, value at risk, insurance, actuarial, digital twins and Weibull. None appear as lessons, so G9 teaches them for the first time. The Roadmap does contain a Stage 2D real-time fraud and risk platform case study, a Stage 5B fraud or system anomaly detection project and graph-based fraud detection lesson, and Stage 5D governance lessons; G9 references these and does not reteach them. Searches for 'aml', 'basel' and 'gis' matched unrelated words and were discounted after reading the matching lines.
- Verified by web search on the build date (2026-10-26): the Reserve Bank of India's FREE-AI committee report was released on 13 August 2025 with seven principles and 26 recommendations, is a recommendation document and not binding rules, and was chaired by Pushpak Bhattacharyya; CDSCO issued draft medical-device-software guidance on 21 October 2025 and final guidance is reported as issued in July 2026 (the exact date and numbering are reported inconsistently), and one law-firm analysis says it clarifies existing Medical Devices Rules rather than creating new requirements; Prithvi-EO-2.0 (IBM and NASA, December 2024) and the TerraTorch and TorchGeo tooling exist; PDEBench is a benchmark suite of time-dependent PDE tasks; GraphCast was published in Science.
- Reported but not confirmed: RBI digital-lending directions and model-risk expectations, the securities regulator's rules on algorithmic trading and research analysts, the insurance regulator's AI expectations, ICMR's guidance on AI in health, ABDM standards, TRIPOD+AI, FDA change-control-plan guidance, the EU AI Act's obligations and timelines for high-risk systems and India's DPDP Act obligations were not confirmed by search and are listed in the lessons as items to read from primary sources; the combinatorial purged cross-validation and deflated Sharpe ratio methods (López de Prado and coauthors), the C-MAPSS and Tennessee Eastman benchmark protocols, and the licences and access routes of every dataset named (including IEEE-CIS, Bank Account Fraud, Freddie Mac, MIMIC-IV, CheXpert, ChestX-ray14, PTB-XL, TDC, Matbench, Backblaze, SECOM, WM-811K and Indian address data) were not confirmed.
- Not verified: library, model and benchmark versions, which change quickly; regulatory details, which change and differ by jurisdiction; and whether any named dataset remains publicly available.
- Not verified by execution: no code in this plan has been run. Project pass gates are acceptance criteria to be met when the projects are built.
- Safety and legal note: modules 01 to 05 and 09 to 13 concern decisions affecting people's money, health and safety. This plan is education, not financial, medical or legal advice; projects use public, synthetic or consented data, and none may be used to trade real money, advise patients or screen real customers without qualified professional and legal review.
- Repository safety: this build created only this file; no existing file or folder was created, changed or deleted by it.
