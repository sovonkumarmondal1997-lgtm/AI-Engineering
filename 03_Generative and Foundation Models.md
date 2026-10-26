# Generative and Foundation Models — ML Specialization Roadmap

**Group 3 (G3)** of the specialization that follows Stage 5D of the [Roadmap](./Roadmap.md). It covers original categories **6 Generative AI Engineering, 7 Large Language Model Engineering and 8 Transformer Model Engineering**. The group's defining question is: *how do I build, adapt and ship large generative models?* It follows [`01_Classical and Applied ML.md`](./01_Classical%20and%20Applied%20ML.md) (G1) and [`02_Deep Learning by Modality.md`](./02_Deep%20Learning%20by%20Modality.md) (G2).

## G3 summary

| Item | Count |
|---|---|
| Modules (including overview and capstones) | 21 |
| Lesson files | 170 |
| Hands-on project files (module projects, overview project and capstones) | 59 |
| Folders inside the G3 tree | 41 |
| Files inside the G3 tree | 277 |

| Original category | Modules |
|---|---|
| 8 Transformer Model Engineering | 01 to 06 |
| 7 Large Language Model Engineering | 07 to 13 |
| 6 Generative AI Engineering | 14 to 19 |

## Scope and how G3 avoids repeating the Roadmap

G3 starts where Stage 5C and the Stage 4C mathematics stop. These are **already learned** and are only referenced, never retaught: attention, multi-head attention, masking, the transformer block, encoder-decoder and decoder-only architectures, efficient attention and FlashAttention, the mixture-of-experts and state-space overview, tokenization and BPE, building a GPT from scratch, pretraining objectives, pretraining data overview, scaling laws, compute and memory accounting, DDP, FSDP and activation checkpointing, long-context and training stability overview, SFT, reward models and RLHF, DPO, constitutional AI, reinforcement learning for reasoning, greedy and sampling decoding, KV-cache and speculative decoding intuition, chain of thought and test-time compute, vision transformers, CLIP and VLM introductions, diffusion in practice, and the mathematics of RoPE, LoRA, VAEs, GANs and diffusion (Stage 4C). Experiment tracking, serving, CI/CD, monitoring and containers from Stages 5D and 2E are reused rather than repeated.

**Boundaries with other groups** (so nothing overlaps): multi-step agents, planning, memory and tool-use loops belong to **G4**; retrieval and ranking *models* belong to **G6** (G3 uses retrieval as a component); distributed training, kernels, quantization internals and inference acceleration belong to **G10**; adversarial ML and responsible-AI methods in general belong to **G12** (G3 covers application-layer LLM security); rigorous benchmark design and synthetic data belong to **G13** (G3 covers application-level evaluation); encoder and sequence-to-sequence NLP and speech synthesis were covered in **G2**.

| Roadmap topic already covered | Where G3 goes further |
|---|---|
| Transformer block, GPT from scratch, efficient attention (5C) | Modules 01 and 02: modern variants, RoPE scaling, GQA, MoE routing, hybrid models and multimodal connectors |
| Pretraining, scaling laws and compute accounting (5C) | Module 03: data deduplication and filtering, tokenizer training, mixtures, stability recipes and your own scaling-law fit |
| LoRA mathematics (4C) and SFT concepts (5C) | Module 04: PEFT tooling, QLoRA, chat-template bugs, forgetting checks and model merging |
| RLHF, DPO and RL for reasoning concepts (5C) | Module 05: running DPO, KTO, ORPO and GRPO-style training, reward models and reward-hacking audits |
| Attribution and probing basics (G2) | Module 06: residual-stream analysis, logit lens, activation patching and sparse autoencoders |
| Decoding and reasoning concepts (5C) | Modules 07 and 11: structured outputs, constrained decoding, caching, routing and cost control |
| Embeddings and sentence embeddings (5C), cross-encoders (G2) | Module 08: full RAG systems, chunking, vector stores, hybrid retrieval and RAG evaluation |
| Model monitoring and CI/CD (5D) | Modules 09 and 11: LLM evaluation gates, judge calibration, tracing and rollout of prompts and models |
| ML-specific security (5D) | Module 10: prompt injection, guardrails, red teaming and the OWASP LLM review |
| Diffusion in practice and GAN/VAE/diffusion math (5C, 4C) | Modules 14 to 16: implementations, evaluation metrics, latent diffusion, flow matching, personalization and control |

## G3 — Generative and Foundation Models

**Defining question:** How do I build, adapt and ship large generative models?

```text
ML Specialization/
└── G3 — Generative and Foundation Models/
    ├── 00-G3-Overview/
    │   ├── Projects/
    │   │   ├── 01-g3-environment-and-api-budget-bootstrap.md
    │   │   └── README.md
    │   ├── 01-g3-scope-and-boundaries-with-stage-5c-and-other-groups.md
    │   ├── 02-prerequisite-map-from-the-roadmap.md
    │   ├── 03-dataset-and-tooling-register.md
    │   ├── 04-evaluation-and-reporting-standards.md
    │   ├── 05-completion-gate.md
    │   ├── README.md
    │   └── learning-plan.md
    ├── 01-Transformer-Architecture-Engineering/
    │   ├── Projects/
    │   │   ├── 01-llama-style-model-from-config.md
    │   │   ├── 02-long-context-extension-experiment.md
    │   │   ├── 03-moe-layer-and-routing-diagnostics.md
    │   │   └── README.md
    │   ├── 01-reading-a-model-config.md
    │   ├── 02-context-extension.md
    │   ├── 03-attention-head-sharing.md
    │   ├── 04-block-design-choices.md
    │   ├── 05-attention-patterns.md
    │   ├── 06-mixture-of-experts-engineering.md
    │   ├── 07-hybrid-and-state-space-architectures.md
    │   ├── 08-small-scale-architecture-experiments.md
    │   ├── 09-reimplementing-a-published-architecture.md
    │   └── README.md
    ├── 02-Multimodal-Transformer-Architecture-Design/
    │   ├── Projects/
    │   │   ├── 01-connector-ablation-at-small-scale.md
    │   │   ├── 02-token-budget-study.md
    │   │   └── README.md
    │   ├── 01-modality-tokenization.md
    │   ├── 02-connector-designs.md
    │   ├── 03-early-fusion-vs-late-fusion-vs-cross-attention-in-a-single-backbone.md
    │   ├── 04-any-to-any-and-unified-token-models.md
    │   ├── 05-training-stages-for-multimodal-models.md
    │   ├── 06-resolution-and-token-count.md
    │   ├── 07-reading-multimodal-model-papers-and-reproducing-the-connector-ablations-at-small-scale.md
    │   └── README.md
    ├── 03-Pretraining-Data-Tokenizers-and-Small-Scale-Training-Recipes/
    │   ├── Projects/
    │   │   ├── 01-dedup-and-quality-filter-pipeline.md
    │   │   ├── 02-train-a-small-model-and-fit-scaling-laws.md
    │   │   ├── 03-indic-tokenizer-training.md
    │   │   └── README.md
    │   ├── 01-pretraining-data-sources-and-licensing.md
    │   ├── 02-text-extraction-and-cleaning-pipelines-for-web-scale-data.md
    │   ├── 03-deduplication.md
    │   ├── 04-quality-filtering.md
    │   ├── 05-data-mixtures-and-curriculum.md
    │   ├── 06-training-a-tokenizer.md
    │   ├── 07-training-stability-recipes.md
    │   ├── 08-fitting-your-own-scaling-laws-at-small-scale-and-extrapolating-with-error-bars.md
    │   ├── 09-continued-pretraining.md
    │   ├── 10-contamination.md
    │   └── README.md
    ├── 04-Fine-Tuning-and-Parameter-Efficient-Adaptation/
    │   ├── Projects/
    │   │   ├── 01-lora-vs-full-finetune-study.md
    │   │   ├── 02-chat-template-and-loss-masking-bug-hunt.md
    │   │   ├── 03-model-merging-experiment.md
    │   │   └── README.md
    │   ├── 01-choosing-between-prompting-retrieval-fine-tuning-and-continued-pretraining.md
    │   ├── 02-full-fine-tuning-vs-parameter-efficient-methods.md
    │   ├── 03-lora-qlora-and-dora-in-practice.md
    │   ├── 04-other-adapters.md
    │   ├── 05-tooling.md
    │   ├── 06-instruction-data.md
    │   ├── 07-data-quality-for-tuning.md
    │   ├── 08-forgetting-and-regression.md
    │   ├── 09-merging-and-combining-models.md
    │   ├── 10-serving-many-adapters.md
    │   └── README.md
    ├── 05-Preference-Optimization-and-Reasoning-Post-Training-in-Practice/
    │   ├── Projects/
    │   │   ├── 01-dpo-run-with-before-after-evaluation.md
    │   │   ├── 02-grpo-on-verifiable-math-tasks.md
    │   │   ├── 03-reward-model-evaluation.md
    │   │   └── README.md
    │   ├── 01-preference-data.md
    │   ├── 02-training-with-trl.md
    │   ├── 03-reward-model-training.md
    │   ├── 04-reinforcement-learning-with-verifiable-rewards.md
    │   ├── 05-reward-hacking.md
    │   ├── 06-rejection-sampling-and-best-of-n-distillation.md
    │   ├── 07-synthetic-training-data-from-stronger-models.md
    │   ├── 08-safety-tuning.md
    │   ├── 09-cost-and-compute-planning-for-post-training-runs.md
    │   └── README.md
    ├── 06-Transformer-Interpretability-and-Debugging/
    │   ├── Projects/
    │   │   ├── 01-induction-head-investigation.md
    │   │   ├── 02-activation-patching-on-a-factual-recall-task.md
    │   │   ├── 03-precision-and-framework-mismatch-debug.md
    │   │   └── README.md
    │   ├── 01-the-residual-stream-view.md
    │   ├── 02-logit-lens-and-tuned-lens.md
    │   ├── 03-attention-head-analysis.md
    │   ├── 04-activation-patching-and-causal-tracing.md
    │   ├── 05-sparse-autoencoders-for-features.md
    │   ├── 06-tooling.md
    │   ├── 07-debugging-numerical-and-implementation-mismatches-between-frameworks-and-precisions.md
    │   ├── 08-limits-of-interpretability-claims.md
    │   └── README.md
    ├── 07-Prompting-Context-and-Structured-Output-Engineering/
    │   ├── Projects/
    │   │   ├── 01-prompt-regression-test-suite.md
    │   │   ├── 02-schema-validated-extraction-service.md
    │   │   ├── 03-model-selection-cost-quality-study.md
    │   │   └── README.md
    │   ├── 01-llm-api-fundamentals.md
    │   ├── 02-prompt-design.md
    │   ├── 03-prompt-testing-and-versioning.md
    │   ├── 04-context-window-management.md
    │   ├── 05-prompt-caching-and-cost-aware-prompt-layout.md
    │   ├── 06-structured-outputs.md
    │   ├── 07-constrained-decoding.md
    │   ├── 08-function-and-tool-calling-in-a-single-request.md
    │   ├── 09-reliability-engineering.md
    │   ├── 10-choosing-a-model.md
    │   └── README.md
    ├── 08-Retrieval-Augmented-Generation-Engineering/
    │   ├── Projects/
    │   │   ├── 01-rag-over-a-real-document-set.md
    │   │   ├── 02-chunking-and-embedding-ablation.md
    │   │   ├── 03-rag-failure-taxonomy.md
    │   │   └── README.md
    │   ├── 01-rag-architecture-and-when-it-beats-fine-tuning-or-long-context.md
    │   ├── 02-document-ingestion.md
    │   ├── 03-chunking-strategies.md
    │   ├── 04-embedding-model-selection.md
    │   ├── 05-vector-stores.md
    │   ├── 06-hybrid-retrieval.md
    │   ├── 07-reranking-with-cross-encoders-from-g2-and-query-rewriting.md
    │   ├── 08-grounded-generation.md
    │   ├── 09-index-maintenance.md
    │   ├── 10-beyond-flat-chunks.md
    │   ├── 11-rag-evaluation.md
    │   └── README.md
    ├── 09-LLM-Evaluation-for-Applications/
    │   ├── Projects/
    │   │   ├── 01-judge-calibration-against-human-labels.md
    │   │   ├── 02-eval-gated-release-pipeline.md
    │   │   ├── 03-llm-eval-variance-study.md
    │   │   └── README.md
    │   ├── 01-building-evaluation-sets.md
    │   ├── 02-metrics-by-task-type.md
    │   ├── 03-llm-as-judge.md
    │   ├── 04-calibrating-a-judge-against-human-labels-and-reporting-agreement.md
    │   ├── 05-pairwise-comparison-and-rating-systems-for-model-and-prompt-comparison.md
    │   ├── 06-human-evaluation.md
    │   ├── 07-evaluation-harnesses.md
    │   ├── 08-evaluation-in-ci.md
    │   ├── 09-online-evaluation.md
    │   ├── 10-statistical-rigor-for-llm-evals.md
    │   └── README.md
    ├── 10-LLM-Application-Security-and-Guardrails/
    │   ├── Projects/
    │   │   ├── 01-indirect-injection-lab.md
    │   │   ├── 02-guardrail-layer-evaluation.md
    │   │   ├── 03-owasp-llm-top-10-review.md
    │   │   └── README.md
    │   ├── 01-threat-model-for-llm-applications.md
    │   ├── 02-prompt-injection.md
    │   ├── 03-jailbreaks-and-policy-bypass.md
    │   ├── 04-information-disclosure.md
    │   ├── 05-output-handling.md
    │   ├── 06-input-and-output-guardrails.md
    │   ├── 07-pii-handling.md
    │   ├── 08-least-privilege-for-tool-calls-and-per-request-permission-design.md
    │   ├── 09-red-teaming-for-applications.md
    │   ├── 10-the-owasp-top-10-for-llm-applications-as-a-review-checklist.md
    │   └── README.md
    ├── 11-LLM-Production-Integration-Cost-and-Reliability/
    │   ├── Projects/
    │   │   ├── 01-gateway-with-routing-and-fallback.md
    │   │   ├── 02-semantic-cache-risk-study.md
    │   │   ├── 03-llm-observability-dashboard.md
    │   │   └── README.md
    │   ├── 01-llm-gateway-pattern.md
    │   ├── 02-cost-accounting.md
    │   ├── 03-caching.md
    │   ├── 04-model-routing-and-cascades.md
    │   ├── 05-latency-engineering.md
    │   ├── 06-tracing-and-observability.md
    │   ├── 07-versioning-and-rollout-of-prompts-and-models.md
    │   ├── 08-asynchronous-and-batch-pipelines.md
    │   ├── 09-privacy-data-residency-and-vendor-terms.md
    │   ├── 10-failure-handling.md
    │   └── README.md
    ├── 12-Open-Weight-Models-in-Practice/
    │   ├── Projects/
    │   │   ├── 01-api-vs-self-hosted-cost-model.md
    │   │   ├── 02-open-model-bakeoff-on-your-task.md
    │   │   ├── 03-local-llm-memory-planner.md
    │   │   └── README.md
    │   ├── 01-open-weight-landscape.md
    │   ├── 02-indic-focused-and-multilingual-open-models.md
    │   ├── 03-gpu-memory-arithmetic.md
    │   ├── 04-running-models-with-hugging-face-transformers-and-pipelines.md
    │   ├── 05-local-runtimes.md
    │   ├── 06-serving-with-vllm.md
    │   ├── 07-api-vs-self-hosting.md
    │   ├── 08-model-cards-safety-evaluations-and-license-compliance-checks.md
    │   └── README.md
    ├── 13-LLM-Applications-in-Code-SQL-Extraction-and-Multilingual-Settings/
    │   ├── Projects/
    │   │   ├── 01-text-to-sql-with-execution-evaluation.md
    │   │   ├── 02-llm-vs-encoder-classification-comparison.md
    │   │   ├── 03-indic-language-llm-quality-audit.md
    │   │   └── README.md
    │   ├── 01-code-generation.md
    │   ├── 02-code-benchmarks-and-their-limits.md
    │   ├── 03-text-to-sql.md
    │   ├── 04-information-extraction-at-scale.md
    │   ├── 05-long-document-pipelines.md
    │   ├── 06-llms-vs-fine-tuned-encoders.md
    │   ├── 07-multilingual-and-indic-use.md
    │   ├── 08-human-in-the-loop-designs.md
    │   └── README.md
    ├── 14-Generative-Modeling-Implementations-and-Evaluation/
    │   ├── Projects/
    │   │   ├── 01-vae-and-gan-on-a-small-image-set.md
    │   │   ├── 02-fid-reliability-study.md
    │   │   └── README.md
    │   ├── 01-generative-model-families-compared.md
    │   ├── 02-implementing-a-vae.md
    │   ├── 03-implementing-a-gan.md
    │   ├── 04-normalizing-flows-and-autoregressive-image-models.md
    │   ├── 05-evaluation-metrics.md
    │   ├── 06-text-conditioned-evaluation.md
    │   ├── 07-memorization-and-privacy-in-generative-models.md
    │   ├── 08-choosing-a-family-for-a-product-requirement.md
    │   └── README.md
    ├── 15-Diffusion-and-Flow-Model-Engineering/
    │   ├── Projects/
    │   │   ├── 01-ddpm-from-scratch-on-mnist-and-cifar.md
    │   │   ├── 02-flow-matching-vs-ddpm.md
    │   │   ├── 03-classifier-free-guidance-study.md
    │   │   └── README.md
    │   ├── 01-implementing-ddpm-and-ddim.md
    │   ├── 02-noise-schedules-and-loss-weighting.md
    │   ├── 03-fast-samplers.md
    │   ├── 04-latent-diffusion.md
    │   ├── 05-denoiser-architectures.md
    │   ├── 06-conditioning.md
    │   ├── 07-flow-matching-and-rectified-flow.md
    │   ├── 08-distillation-for-few-step-generation.md
    │   ├── 09-using-the-diffusers-library-and-reproducing-published-pipelines.md
    │   ├── 10-training-on-small-datasets.md
    │   └── README.md
    ├── 16-Controllable-Image-Generation-and-Editing/
    │   ├── Projects/
    │   │   ├── 01-personalization-comparison.md
    │   │   ├── 02-controlnet-product-image-pipeline.md
    │   │   ├── 03-inpainting-quality-audit.md
    │   │   └── README.md
    │   ├── 01-prompting-image-models.md
    │   ├── 02-personalization.md
    │   ├── 03-spatial-control.md
    │   ├── 04-image-prompt-adapters.md
    │   ├── 05-editing.md
    │   ├── 06-instruction-based-editing-models.md
    │   ├── 07-super-resolution-and-restoration-pipelines.md
    │   ├── 08-workflow-tooling.md
    │   ├── 09-evaluating-controllability.md
    │   └── README.md
    ├── 17-Video-and-3D-Generation/
    │   ├── Projects/
    │   │   ├── 01-image-to-video-pipeline-and-consistency-audit.md
    │   │   ├── 02-gaussian-splatting-reconstruction.md
    │   │   └── README.md
    │   ├── 01-video-diffusion.md
    │   ├── 02-image-to-video-and-text-to-video-pipelines-and-their-conditioning.md
    │   ├── 03-temporal-consistency.md
    │   ├── 04-video-generation-evaluation.md
    │   ├── 05-compute-and-cost-of-video-generation.md
    │   ├── 06-neural-radiance-fields-and-3d-gaussian-splatting-for-scene-reconstruction.md
    │   ├── 07-text-to-3d-and-image-to-3d-approaches-and-datasets-such-as-objaverse.md
    │   ├── 08-practical-limits-and-failure-catalogs.md
    │   └── README.md
    ├── 18-Music-and-General-Audio-Generation/
    │   ├── Projects/
    │   │   ├── 01-codec-reconstruction-and-token-study.md
    │   │   ├── 02-text-to-audio-generation-evaluation.md
    │   │   └── README.md
    │   ├── 01-neural-audio-codecs.md
    │   ├── 02-autoregressive-audio-generation-over-codec-tokens.md
    │   ├── 03-text-to-music-and-text-to-audio-models-such-as-musicgen.md
    │   ├── 04-diffusion-based-audio-generation.md
    │   ├── 05-conditioning.md
    │   ├── 06-evaluating-generated-audio.md
    │   ├── 07-rights-licensing-and-artist-consent-for-music-data.md
    │   └── README.md
    ├── 19-Generative-Content-Provenance-Safety-and-Governance/
    │   ├── Projects/
    │   │   ├── 01-provenance-and-watermark-robustness-test.md
    │   │   ├── 02-safety-filter-evaluation-for-image-generation.md
    │   │   ├── 03-generative-product-governance-pack.md
    │   │   └── README.md
    │   ├── 01-misuse-landscape.md
    │   ├── 02-content-safety-filtering-for-generated-images-audio-and-text.md
    │   ├── 03-provenance-and-watermarking.md
    │   ├── 04-detection-limits.md
    │   ├── 05-copyright-and-training-data-questions.md
    │   ├── 06-disclosure-and-consent-policy-for-synthetic-media.md
    │   ├── 07-india-specific-considerations.md
    │   ├── 08-incident-response-for-generative-products.md
    │   └── README.md
    ├── 20-G3-Capstones/
    │   ├── 01-train-and-adapt-a-small-foundation-model.md
    │   ├── 02-production-rag-and-llm-application.md
    │   ├── 03-controllable-generative-image-product.md
    │   ├── 04-transformer-research-reproduction.md
    │   ├── 05-g3-readiness-assessment.md
    │   └── README.md
    └── README.md
```

### 00 — G3 Overview

**Purpose:** the single authoritative plan for G3 with scope, boundaries, prerequisite map, model and dataset register, evaluation standards, API and compute budget and completion gate.

- `01-g3-scope-and-boundaries-with-stage-5c-and-other-groups.md` — what G3 teaches and what it leaves to other groups.
- `02-prerequisite-map-from-the-roadmap.md` — Roadmap stages and modules assumed for each G3 module.
- `03-dataset-and-tooling-register.md` — every model, dataset, licence, access condition, library and version pin, with prices and dates for any paid API.
- `04-evaluation-and-reporting-standards.md` — seeds, repeated runs, confidence intervals, judge-calibration rules and report template.
- `05-completion-gate.md` — measurable criteria to finish G3.
- `learning-plan.md` — recommended order, three tracks (foundation models, LLM applications, generative media) and compute and API budget.

**Project 1: g3 environment and api budget bootstrap**  
- Data: small prompts and a toy dataset.  
- Task: build a reproducible workspace with pinned tooling, a spending cap and logging for every model call, and an evaluation skeleton that records seeds, model versions and prices.  
- Deliverables: lockfile, call-logging wrapper with cost tracking and smoke tests.  
- Pass gate: a clean machine reproduces the smoke tests, and the spending cap blocks a deliberately excessive run.

### 01 — Transformer Architecture Engineering

**Outcome:** Read, modify and implement modern transformer variants and know what each design choice costs. The attention mechanism, the transformer block, GPT from scratch, efficient attention and the mixture-of-experts and state-space overview are covered in Stage 5C and the math of RoPE in Stage 4C; none are repeated.

**Lessons**

- `01-reading-a-model-config.md` — Reading a model config: mapping a Hugging Face config to every tensor in a Llama-style model
- `02-context-extension.md` — Context extension: RoPE scaling, NTK-aware scaling and YaRN
- `03-attention-head-sharing.md` — Attention head sharing: multi-query, grouped-query and latent attention and their memory effects
- `04-block-design-choices.md` — Block design choices: pre-norm vs post-norm, RMSNorm, SwiGLU and bias-free layers
- `05-attention-patterns.md` — Attention patterns: sliding-window, sparse and local-global layouts and their quality trade-offs
- `06-mixture-of-experts-engineering.md` — Mixture-of-experts engineering: routing, load-balancing losses, capacity and expert collapse
- `07-hybrid-and-state-space-architectures.md` — Hybrid and state-space architectures: Mamba-style layers and attention-hybrid designs in code
- `08-small-scale-architecture-experiments.md` — Small-scale architecture experiments: ablation methodology, muP-style hyperparameter transfer and avoiding misleading wins
- `09-reimplementing-a-published-architecture.md` — Reimplementing a published architecture: matching reference logits layer by layer

**Hands-on projects**

- **Project 1: llama style model from config**  
  - Data: A small open Llama-style checkpoint and its config  
  - Task: Implement the model from scratch in PyTorch from the config alone and match the reference logits and generated tokens.  
  - Deliverables: Implementation, layer-by-layer equivalence tests and a memory-per-component table.  
  - Pass gate: Logits match the reference within a stated tolerance in float32 and the test fails if any component is changed.
- **Project 2: long context extension experiment**  
  - Data: A small pretrained model and a long-document evaluation set  
  - Task: Extend the context window with RoPE scaling methods and measure perplexity and a retrieval-style needle test at several lengths.  
  - Deliverables: Length-vs-quality curves for each method.  
  - Pass gate: Results reported at lengths beyond training length and compared with no extension.
- **Project 3: moe layer and routing diagnostics**  
  - Data: A small language-modeling corpus such as TinyStories  
  - Task: Add a mixture-of-experts layer to a small transformer, train with and without a load-balancing loss and log expert utilization.  
  - Deliverables: Training curves and expert-utilization plots.  
  - Pass gate: Expert collapse demonstrated and fixed with measured utilization.

### 02 — Multimodal Transformer Architecture Design

**Outcome:** Design how images, audio and text enter one transformer. G2 covered using vision-language models; this module covers how they are built.

**Lessons**

- `01-modality-tokenization.md` — Modality tokenization: patches, audio frames, discrete codes and token budgets per modality
- `02-connector-designs.md` — Connector designs: linear projectors, Q-Former and Perceiver-style resamplers
- `03-early-fusion-vs-late-fusion-vs-cross-attention-in-a-single-backbone.md` — Early fusion vs late fusion vs cross-attention in a single backbone
- `04-any-to-any-and-unified-token-models.md` — Any-to-any and unified token models: shared vocabularies for several modalities
- `05-training-stages-for-multimodal-models.md` — Training stages for multimodal models: alignment, instruction tuning and data mixing
- `06-resolution-and-token-count.md` — Resolution and token count: dynamic resolution and its cost
- `07-reading-multimodal-model-papers-and-reproducing-the-connector-ablations-at-small-scale.md` — Reading multimodal model papers and reproducing the connector ablations at small scale

**Hands-on projects**

- **Project 1: connector ablation at small scale**  
  - Data: COCO Captions subset with a frozen vision encoder and a small frozen language model  
  - Task: Compare a linear projector, an MLP projector and a Q-Former-style resampler on captioning and VQA quality and token cost.  
  - Deliverables: Ablation table and cost analysis.  
  - Pass gate: Frozen components and token budgets identical across variants.
- **Project 2: token budget study**  
  - Data: A document-image or chart question answering set  
  - Task: Measure answer accuracy as image resolution and token count change.  
  - Deliverables: Accuracy-vs-tokens curve.  
  - Pass gate: Cost per query computed from measured token counts.

### 03 — Pretraining Data Tokenizers and Small Scale Training Recipes

**Outcome:** Understand how pretraining corpora and recipes are built and run honest small-scale experiments. Pretraining objectives, scaling laws, compute accounting and DDP/FSDP basics are covered in Stage 5C; large-scale parallelism and kernels are covered later in G10.

**Lessons**

- `01-pretraining-data-sources-and-licensing.md` — Pretraining data sources and licensing: web crawls, code and curated corpora
- `02-text-extraction-and-cleaning-pipelines-for-web-scale-data.md` — Text extraction and cleaning pipelines for web-scale data
- `03-deduplication.md` — Deduplication: exact, MinHash near-duplicate and substring dedup, and their effect on memorization
- `04-quality-filtering.md` — Quality filtering: heuristic filters and classifier-based filters
- `05-data-mixtures-and-curriculum.md` — Data mixtures and curriculum: domain weights, annealing and multilingual balance
- `06-training-a-tokenizer.md` — Training a tokenizer: vocabulary size, byte-level fallback and coverage for Indic scripts
- `07-training-stability-recipes.md` — Training stability recipes: loss spikes, z-loss, QK-norm and warm restarts
- `08-fitting-your-own-scaling-laws-at-small-scale-and-extrapolating-with-error-bars.md` — Fitting your own scaling laws at small scale and extrapolating with error bars
- `09-continued-pretraining.md` — Continued pretraining: domain adaptation without forgetting
- `10-contamination.md` — Contamination: detecting benchmark leakage into training data

**Hands-on projects**

- **Project 1: dedup and quality filter pipeline**  
  - Data: A public web-text sample such as a FineWeb or C4 slice  
  - Task: Build exact and MinHash deduplication plus heuristic and classifier filters and measure what each removes.  
  - Deliverables: Pipeline, removal statistics and a downstream small-model perplexity comparison.  
  - Pass gate: Each filter's effect measured by training the same small model on filtered and unfiltered data.
- **Project 2: train a small model and fit scaling laws**  
  - Data: TinyStories or a similar small corpus  
  - Task: Train models at several sizes, fit loss vs compute and predict a held-out larger run.  
  - Deliverables: Fitted curves with prediction intervals.  
  - Pass gate: Prediction compared against an actually trained larger model.
- **Project 3: indic tokenizer training**  
  - Data: Public Hindi, Bengali and English text  
  - Task: Train tokenizers with different vocabulary sizes and measure fragmentation and downstream loss.  
  - Deliverables: Fragmentation table and loss comparison.  
  - Pass gate: Same text and model size across tokenizers.

### 04 — Fine Tuning and Parameter Efficient Adaptation

**Outcome:** Adapt foundation models to a task or domain with the least cost and risk. The low-rank mathematics of LoRA is covered in Stage 4C and the idea of supervised fine-tuning in Stage 5C; this module is the engineering.

**Lessons**

- `01-choosing-between-prompting-retrieval-fine-tuning-and-continued-pretraining.md` — Choosing between prompting, retrieval, fine-tuning and continued pretraining: a decision framework
- `02-full-fine-tuning-vs-parameter-efficient-methods.md` — Full fine-tuning vs parameter-efficient methods: memory, speed and quality
- `03-lora-qlora-and-dora-in-practice.md` — LoRA, QLoRA and DoRA in practice: rank, alpha, target modules and quantized base weights
- `04-other-adapters.md` — Other adapters: prefix tuning, prompt tuning and IA3
- `05-tooling.md` — Tooling: Hugging Face Transformers, PEFT, TRL, Unsloth, Axolotl and LLaMA-Factory compared
- `06-instruction-data.md` — Instruction data: chat templates, formatting bugs and loss masking
- `07-data-quality-for-tuning.md` — Data quality for tuning: curation, mixing and measuring each subset's effect
- `08-forgetting-and-regression.md` — Forgetting and regression: general-capability checks after tuning
- `09-merging-and-combining-models.md` — Merging and combining models: adapter merging, TIES and SLERP with mergekit
- `10-serving-many-adapters.md` — Serving many adapters: multi-LoRA deployment patterns

**Hands-on projects**

- **Project 1: lora vs full finetune study**  
  - Data: A public instruction or domain task dataset and a small open model  
  - Task: Fine-tune with full tuning, LoRA and QLoRA; compare quality, memory, time and general-capability regression.  
  - Deliverables: Comparison table and training logs.  
  - Pass gate: General-capability benchmark run before and after for every variant.
- **Project 2: chat template and loss masking bug hunt**  
  - Data: Any instruction dataset  
  - Task: Reproduce common formatting errors (wrong template, unmasked prompt, missing EOS) and measure their effect on outputs.  
  - Deliverables: Bug catalog with failing examples and unit tests.  
  - Pass gate: Each bug shown to change loss or outputs measurably.
- **Project 3: model merging experiment**  
  - Data: Two adapters trained for different tasks on the same base  
  - Task: Merge with linear, TIES and SLERP methods and evaluate on both tasks.  
  - Deliverables: Merge comparison and interference analysis.  
  - Pass gate: Single-task adapters included as upper bounds.

### 05 — Preference Optimization and Reasoning Post Training in Practice

**Outcome:** Run preference-based and reward-based post-training end to end. RLHF, DPO, constitutional AI and reinforcement learning for reasoning are explained in Stage 5C and are not re-explained here.

**Lessons**

- `01-preference-data.md` — Preference data: collection, annotator guidelines, pairwise noise and agreement
- `02-training-with-trl.md` — Training with TRL: DPO, KTO and ORPO runs and their hyperparameters
- `03-reward-model-training.md` — Reward model training: data format, evaluation and calibration of reward models
- `04-reinforcement-learning-with-verifiable-rewards.md` — Reinforcement learning with verifiable rewards: GRPO-style training on math and code tasks
- `05-reward-hacking.md` — Reward hacking: detection, monitoring and mitigations
- `06-rejection-sampling-and-best-of-n-distillation.md` — Rejection sampling and best-of-n distillation
- `07-synthetic-training-data-from-stronger-models.md` — Synthetic training data from stronger models: quality control, licenses and terms of use
- `08-safety-tuning.md` — Safety tuning: refusal behavior, over-refusal and regression testing
- `09-cost-and-compute-planning-for-post-training-runs.md` — Cost and compute planning for post-training runs

**Hands-on projects**

- **Project 1: dpo run with before after evaluation**  
  - Data: UltraFeedback or a similar public preference set and a small instruct model  
  - Task: Run DPO, evaluate with pairwise judgments and general benchmarks and inspect response length drift.  
  - Deliverables: Training config, evaluation and length-bias analysis.  
  - Pass gate: Length-controlled comparison reported.
- **Project 2: grpo on verifiable math tasks**  
  - Data: GSM8K-style problems with automatic answer checking  
  - Task: Train a small model with a verifiable reward and track accuracy and reward-hacking signals.  
  - Deliverables: Reward curves, accuracy and hacking audit.  
  - Pass gate: Held-out problems and a hacking audit of sampled outputs.
- **Project 3: reward model evaluation**  
  - Data: A preference dataset with held-out pairs  
  - Task: Train a reward model and test accuracy, calibration and sensitivity to length and style.  
  - Deliverables: Reward-model report.  
  - Pass gate: Spurious-feature probes included.

### 06 — Transformer Interpretability and Debugging

**Outcome:** Inspect what transformers compute and find the cause of strange behavior. General attribution and probing methods are covered in G2; this module is specific to transformer internals.

**Lessons**

- `01-the-residual-stream-view.md` — The residual stream view: reading a transformer as additive updates
- `02-logit-lens-and-tuned-lens.md` — Logit lens and tuned lens: following predictions through layers
- `03-attention-head-analysis.md` — Attention head analysis: induction heads and head ablations
- `04-activation-patching-and-causal-tracing.md` — Activation patching and causal tracing: locating where facts and behaviors live
- `05-sparse-autoencoders-for-features.md` — Sparse autoencoders for features: training and interpreting dictionary features
- `06-tooling.md` — Tooling: TransformerLens and nnsight-style libraries
- `07-debugging-numerical-and-implementation-mismatches-between-frameworks-and-precisions.md` — Debugging numerical and implementation mismatches between frameworks and precisions
- `08-limits-of-interpretability-claims.md` — Limits of interpretability claims: what evidence is and is not enough

**Hands-on projects**

- **Project 1: induction head investigation**  
  - Data: A small open transformer language model  
  - Task: Find induction-like heads with repeated-token prompts, confirm by ablation and report the effect on in-context copying.  
  - Deliverables: Experiment notebook with ablation evidence.  
  - Pass gate: Claims backed by causal intervention, not attention maps alone.
- **Project 2: activation patching on a factual recall task**  
  - Data: Small model and a set of factual prompts  
  - Task: Patch activations between clean and corrupted prompts to localize layers important to recall.  
  - Deliverables: Patching heatmaps and written interpretation.  
  - Pass gate: Corrupted-prompt design documented and controls included.
- **Project 3: precision and framework mismatch debug**  
  - Data: A model exported between two frameworks or precisions  
  - Task: Find where outputs diverge layer by layer and explain the cause.  
  - Deliverables: Divergence report.  
  - Pass gate: Divergence located to a specific operation.

### 07 — Prompting Context and Structured Output Engineering

**Outcome:** Use LLM APIs reliably: prompts, context, structured outputs and single-call tool use. Multi-step agent loops, memory and planning are covered in G4.

**Lessons**

- `01-llm-api-fundamentals.md` — LLM API fundamentals: messages, roles, system prompts, parameters and streaming
- `02-prompt-design.md` — Prompt design: instructions, examples, delimiters and the failure modes of each
- `03-prompt-testing-and-versioning.md` — Prompt testing and versioning: treating prompts as code with regression tests
- `04-context-window-management.md` — Context window management: truncation, summarization and ordering effects
- `05-prompt-caching-and-cost-aware-prompt-layout.md` — Prompt caching and cost-aware prompt layout
- `06-structured-outputs.md` — Structured outputs: JSON schemas, validation and repair loops
- `07-constrained-decoding.md` — Constrained decoding: grammar-based generation with libraries such as Outlines
- `08-function-and-tool-calling-in-a-single-request.md` — Function and tool calling in a single request: schema design and error handling
- `09-reliability-engineering.md` — Reliability engineering: retries, rate limits, timeouts and idempotency
- `10-choosing-a-model.md` — Choosing a model: capability, cost, latency and data-handling terms

**Hands-on projects**

- **Project 1: prompt regression test suite**  
  - Data: A classification or extraction task with 200 labeled examples  
  - Task: Build a prompt test harness that scores each prompt version on a fixed set and blocks regressions.  
  - Deliverables: Harness, versioned prompts and score history.  
  - Pass gate: A deliberately worse prompt is caught by the harness.
- **Project 2: schema validated extraction service**  
  - Data: Public documents such as press releases or job postings  
  - Task: Extract fields into a strict schema with validation, repair retries and failure logging.  
  - Deliverables: Service, validation rules and failure analysis.  
  - Pass gate: Schema-violation rate measured and reduced with documented changes.
- **Project 3: model selection cost quality study**  
  - Data: The same task evaluated on three or more models  
  - Task: Compare quality, latency and cost per 1,000 requests and recommend a model.  
  - Deliverables: Cost-quality table with confidence intervals.  
  - Pass gate: Prices recorded with source and date.

### 08 — Retrieval Augmented Generation Engineering

**Outcome:** Build and evaluate RAG systems end to end. Retrieval relevance models and learned ranking are built in G6; here retrieval is a component of a generation system.

**Lessons**

- `01-rag-architecture-and-when-it-beats-fine-tuning-or-long-context.md` — RAG architecture and when it beats fine-tuning or long context
- `02-document-ingestion.md` — Document ingestion: parsing PDFs, HTML and tables, and metadata capture
- `03-chunking-strategies.md` — Chunking strategies: fixed, structural and semantic chunking and their evaluation
- `04-embedding-model-selection.md` — Embedding model selection: MTEB, domain tests and multilingual coverage
- `05-vector-stores.md` — Vector stores: FAISS, pgvector, Qdrant and managed options compared
- `06-hybrid-retrieval.md` — Hybrid retrieval: BM25 plus dense retrieval and rank fusion
- `07-reranking-with-cross-encoders-from-g2-and-query-rewriting.md` — Reranking with cross-encoders from G2 and query rewriting
- `08-grounded-generation.md` — Grounded generation: citations, quote verification and abstention
- `09-index-maintenance.md` — Index maintenance: updates, deletions, freshness and access control
- `10-beyond-flat-chunks.md` — Beyond flat chunks: hierarchical, graph-based and multi-hop retrieval overview
- `11-rag-evaluation.md` — RAG evaluation: retrieval metrics, faithfulness and end-to-end answer quality

**Hands-on projects**

- **Project 1: rag over a real document set**  
  - Data: A public corpus such as a government policy document set or open documentation  
  - Task: Build ingestion, hybrid retrieval, reranking and cited answers, with a hand-built question set.  
  - Deliverables: Working system, question set and results.  
  - Pass gate: Retrieval recall and answer faithfulness measured separately.
- **Project 2: chunking and embedding ablation**  
  - Data: The same corpus and question set  
  - Task: Vary chunk size, overlap, structure-aware chunking and embedding models and measure retrieval recall@k.  
  - Deliverables: Ablation table with confidence intervals.  
  - Pass gate: Question set fixed before experiments.
- **Project 3: rag failure taxonomy**  
  - Data: Outputs of the first project  
  - Task: Classify 100 failures into retrieval, ranking, context and generation failures and fix the top two classes.  
  - Deliverables: Failure taxonomy and measured fixes.  
  - Pass gate: Before and after measured on a held-out question set.

### 09 — LLM Evaluation for Applications

**Outcome:** Measure whether an LLM application works. This module covers application-level evaluation; rigorous benchmark design and stress-testing systems are covered later in G13.

**Lessons**

- `01-building-evaluation-sets.md` — Building evaluation sets: sourcing, labeling, coverage and versioning
- `02-metrics-by-task-type.md` — Metrics by task type: exact match, semantic and rubric-based scoring
- `03-llm-as-judge.md` — LLM-as-judge: prompt design, position bias, verbosity bias and self-preference
- `04-calibrating-a-judge-against-human-labels-and-reporting-agreement.md` — Calibrating a judge against human labels and reporting agreement
- `05-pairwise-comparison-and-rating-systems-for-model-and-prompt-comparison.md` — Pairwise comparison and rating systems for model and prompt comparison
- `06-human-evaluation.md` — Human evaluation: rater guidelines, agreement and cost
- `07-evaluation-harnesses.md` — Evaluation harnesses: lm-evaluation-harness, Inspect and custom runners
- `08-evaluation-in-ci.md` — Evaluation in CI: gating releases on quality using the Stage 5D pipeline
- `09-online-evaluation.md` — Online evaluation: user feedback, A/B tests and implicit signals
- `10-statistical-rigor-for-llm-evals.md` — Statistical rigor for LLM evals: sample size, variance across runs and confidence intervals

**Hands-on projects**

- **Project 1: judge calibration against human labels**  
  - Data: 200 model outputs you label yourself with a rubric  
  - Task: Build an LLM judge, measure agreement with your labels and quantify position and verbosity bias.  
  - Deliverables: Judge prompt, agreement statistics and bias report.  
  - Pass gate: Bias measured with swapped-order and padded-length tests.
- **Project 2: eval gated release pipeline**  
  - Data: A prompt-based application from module 07  
  - Task: Add an evaluation stage to CI that blocks a change if quality drops beyond a statistical threshold.  
  - Deliverables: CI configuration and a demonstration of a blocked regression.  
  - Pass gate: Threshold justified by measured run-to-run variance.
- **Project 3: llm eval variance study**  
  - Data: A benchmark subset and a model with sampling  
  - Task: Measure how much scores change across seeds, prompts formats and temperature, and report the minimum detectable difference.  
  - Deliverables: Variance report.  
  - Pass gate: At least 10 repeated runs per setting.

### 10 — LLM Application Security and Guardrails

**Outcome:** Defend LLM applications against misuse and attack at the application layer. Adversarial machine learning in general is covered later in G12.

**Lessons**

- `01-threat-model-for-llm-applications.md` — Threat model for LLM applications: assets, attackers and trust boundaries
- `02-prompt-injection.md` — Prompt injection: direct and indirect injection through documents and tools
- `03-jailbreaks-and-policy-bypass.md` — Jailbreaks and policy bypass: categories and why filters fail
- `04-information-disclosure.md` — Information disclosure: system prompt, context and training-data extraction risks
- `05-output-handling.md` — Output handling: treating model output as untrusted input
- `06-input-and-output-guardrails.md` — Input and output guardrails: moderation models, NeMo Guardrails and Llama Guard
- `07-pii-handling.md` — PII handling: detection and redaction with tools such as Presidio
- `08-least-privilege-for-tool-calls-and-per-request-permission-design.md` — Least privilege for tool calls and per-request permission design
- `09-red-teaming-for-applications.md` — Red teaming for applications: test design and vulnerability scanning with tools such as garak
- `10-the-owasp-top-10-for-llm-applications-as-a-review-checklist.md` — The OWASP Top 10 for LLM Applications as a review checklist

**Hands-on projects**

- **Project 1: indirect injection lab**  
  - Data: A RAG application from module 08  
  - Task: Plant malicious instructions in documents, measure attack success and add layered defenses.  
  - Deliverables: Attack set, success rates before and after each defense.  
  - Pass gate: Attack success measured over a fixed set of at least 50 attacks.
- **Project 2: guardrail layer evaluation**  
  - Data: Safe and unsafe request sets you build  
  - Task: Add input and output guardrails and measure blocked harmful requests against wrongly blocked benign ones.  
  - Deliverables: Precision-recall trade-off report.  
  - Pass gate: False-block rate on benign requests reported.
- **Project 3: owasp llm top 10 review**  
  - Data: Your own LLM application  
  - Task: Review the application against each OWASP LLM risk and fix the top findings.  
  - Deliverables: Review document and fixes.  
  - Pass gate: Every finding has an evidence test.

### 11 — LLM Production Integration Cost and Reliability

**Outcome:** Run LLM features in production with cost control, observability and fallbacks. General MLOps, CI/CD and monitoring are covered in Stage 5D and Stage 2E; this module covers what is specific to LLM calls.

**Lessons**

- `01-llm-gateway-pattern.md` — LLM gateway pattern: routing, fallbacks and provider abstraction with tools such as LiteLLM
- `02-cost-accounting.md` — Cost accounting: tokens, per-request cost and budgets per feature
- `03-caching.md` — Caching: exact, semantic and prompt-level caching and their risks
- `04-model-routing-and-cascades.md` — Model routing and cascades: cheap model first, strong model on demand
- `05-latency-engineering.md` — Latency engineering: streaming, parallel calls and time-to-first-token
- `06-tracing-and-observability.md` — Tracing and observability: Langfuse-style traces and OpenTelemetry for LLM calls
- `07-versioning-and-rollout-of-prompts-and-models.md` — Versioning and rollout of prompts and models: canaries and rollback
- `08-asynchronous-and-batch-pipelines.md` — Asynchronous and batch pipelines: queues and batch APIs
- `09-privacy-data-residency-and-vendor-terms.md` — Privacy, data residency and vendor terms: contracts and the DPDP Act
- `10-failure-handling.md` — Failure handling: degraded modes and human fallbacks

**Hands-on projects**

- **Project 1: gateway with routing and fallback**  
  - Data: A simple LLM-backed endpoint  
  - Task: Build a gateway with provider fallback, a cheap-then-strong cascade and per-request cost logging.  
  - Deliverables: Gateway, cost dashboard and fault-injection test results.  
  - Pass gate: Fallbacks demonstrated under injected provider failures.
- **Project 2: semantic cache risk study**  
  - Data: A question-answering workload with repeated and near-duplicate queries  
  - Task: Add a semantic cache and measure savings against wrong-answer-from-cache errors.  
  - Deliverables: Savings and error analysis across similarity thresholds.  
  - Pass gate: Wrong-hit rate measured by human or judge review.
- **Project 3: llm observability dashboard**  
  - Data: Traces from your applications  
  - Task: Instrument traces with cost, latency and evaluation scores and build a dashboard with alerts.  
  - Deliverables: Dashboard and alert rules.  
  - Pass gate: An injected quality regression triggers an alert.

### 12 — Open Weight Models in Practice

**Outcome:** Choose, run and operate open-weight models. Quantization internals and high-performance serving are covered later in G10; this module covers selecting and using the models.

**Lessons**

- `01-open-weight-landscape.md` — Open-weight landscape: Llama, Mistral, Qwen, Gemma and DeepSeek families, and licenses
- `02-indic-focused-and-multilingual-open-models.md` — Indic-focused and multilingual open models: how to evaluate current options
- `03-gpu-memory-arithmetic.md` — GPU memory arithmetic: weights, KV cache and activations for a given model and context
- `04-running-models-with-hugging-face-transformers-and-pipelines.md` — Running models with Hugging Face Transformers and pipelines
- `05-local-runtimes.md` — Local runtimes: llama.cpp, GGUF and Ollama for development
- `06-serving-with-vllm.md` — Serving with vLLM: configuration for throughput and latency at a basic level
- `07-api-vs-self-hosting.md` — API vs self-hosting: total cost, privacy, control and operations burden
- `08-model-cards-safety-evaluations-and-license-compliance-checks.md` — Model cards, safety evaluations and license compliance checks

**Hands-on projects**

- **Project 1: api vs self hosted cost model**  
  - Data: A workload profile you define in requests per day and tokens per request  
  - Task: Measure throughput on a self-hosted model and compare total cost with API pricing at several volumes.  
  - Deliverables: Break-even analysis with sensitivity.  
  - Pass gate: Hardware, utilization and price assumptions recorded with dates.
- **Project 2: open model bakeoff on your task**  
  - Data: Your task evaluation set  
  - Task: Compare four open models and one API model on quality, speed and memory.  
  - Deliverables: Bake-off report.  
  - Pass gate: License constraints noted for every model.
- **Project 3: local llm memory planner**  
  - Data: Model configs  
  - Task: Write a tool that predicts GPU memory for a model, context length and batch size and validate against measurements.  
  - Deliverables: Tool and validation table.  
  - Pass gate: Prediction error against measured memory reported.

### 13 — LLM Applications in Code SQL Extraction and Multilingual Settings

**Outcome:** Apply LLMs to common task families and evaluate each with the right method.

**Lessons**

- `01-code-generation.md` — Code generation: prompting, repository context and evaluation with unit tests
- `02-code-benchmarks-and-their-limits.md` — Code benchmarks and their limits: HumanEval, MBPP and SWE-bench-style tasks
- `03-text-to-sql.md` — Text-to-SQL: schema linking, execution-based evaluation and safety limits
- `04-information-extraction-at-scale.md` — Information extraction at scale: batching, validation and cost control
- `05-long-document-pipelines.md` — Long-document pipelines: map-reduce summarization and its faithfulness risks
- `06-llms-vs-fine-tuned-encoders.md` — LLMs vs fine-tuned encoders: choosing for classification and extraction using G2 baselines
- `07-multilingual-and-indic-use.md` — Multilingual and Indic use: tokenization cost, quality gaps and evaluation per language
- `08-human-in-the-loop-designs.md` — Human-in-the-loop designs: review queues and confidence routing

**Hands-on projects**

- **Project 1: text to sql with execution evaluation**  
  - Data: Spider or BIRD subset  
  - Task: Build a text-to-SQL system and evaluate by executing queries and comparing results, with a read-only safety layer.  
  - Deliverables: System, execution accuracy and failure taxonomy.  
  - Pass gate: Queries executed in a read-only sandbox.
- **Project 2: llm vs encoder classification comparison**  
  - Data: A text classification dataset from G2  
  - Task: Compare zero-shot, few-shot and fine-tuned LLMs with a fine-tuned encoder on accuracy, latency and cost.  
  - Deliverables: Comparison with confidence intervals.  
  - Pass gate: Cost per 1,000 predictions reported.
- **Project 3: indic language llm quality audit**  
  - Data: Parallel prompts in English, Hindi and Bengali  
  - Task: Measure answer quality, token cost and refusal behavior across languages.  
  - Deliverables: Per-language audit.  
  - Pass gate: Native-speaker or documented-rubric review of a sample.

### 14 — Generative Modeling Implementations and Evaluation

**Outcome:** Implement and evaluate the classic generative families. The mathematics of the ELBO, VAEs, GANs and diffusion is covered in Stage 4C; this module is the engineering and the measurement.

**Lessons**

- `01-generative-model-families-compared.md` — Generative model families compared: autoregressive, latent-variable, adversarial, flow and diffusion
- `02-implementing-a-vae.md` — Implementing a VAE: architecture, KL annealing and posterior collapse
- `03-implementing-a-gan.md` — Implementing a GAN: training tricks, spectral normalization and mode collapse diagnosis
- `04-normalizing-flows-and-autoregressive-image-models.md` — Normalizing flows and autoregressive image models: when exact likelihood matters
- `05-evaluation-metrics.md` — Evaluation metrics: FID, KID, precision and recall for generative models and their pitfalls
- `06-text-conditioned-evaluation.md` — Text-conditioned evaluation: CLIPScore, human preference and aesthetic predictors
- `07-memorization-and-privacy-in-generative-models.md` — Memorization and privacy in generative models
- `08-choosing-a-family-for-a-product-requirement.md` — Choosing a family for a product requirement

**Hands-on projects**

- **Project 1: vae and gan on a small image set**  
  - Data: CelebA subset or Oxford Flowers  
  - Task: Implement a VAE and a GAN, diagnose collapse in each and compare samples and metrics.  
  - Deliverables: Implementations, diagnostics and metric comparison.  
  - Pass gate: Metrics computed with the same feature extractor and sample counts.
- **Project 2: fid reliability study**  
  - Data: Generated samples from several models  
  - Task: Show how FID changes with sample count, image resizing and feature network, and compare with KID and human ratings.  
  - Deliverables: Sensitivity analysis.  
  - Pass gate: At least three sample sizes and two resizing methods.

### 15 — Diffusion and Flow Model Engineering

**Outcome:** Train and use diffusion and flow-matching models. The forward process and noise prediction math is covered in Stage 4C and diffusion usage in Stage 5C; this module covers implementation and the full latent-diffusion stack.

**Lessons**

- `01-implementing-ddpm-and-ddim.md` — Implementing DDPM and DDIM: schedules, parameterizations and sampler code
- `02-noise-schedules-and-loss-weighting.md` — Noise schedules and loss weighting: epsilon, velocity and v-prediction
- `03-fast-samplers.md` — Fast samplers: DPM-Solver-style solvers and step-count trade-offs
- `04-latent-diffusion.md` — Latent diffusion: autoencoder, denoiser and the end-to-end pipeline
- `05-denoiser-architectures.md` — Denoiser architectures: U-Net and diffusion transformers
- `06-conditioning.md` — Conditioning: text encoders, cross-attention and classifier-free guidance
- `07-flow-matching-and-rectified-flow.md` — Flow matching and rectified flow: training and sampling
- `08-distillation-for-few-step-generation.md` — Distillation for few-step generation: consistency and latent-consistency approaches
- `09-using-the-diffusers-library-and-reproducing-published-pipelines.md` — Using the Diffusers library and reproducing published pipelines
- `10-training-on-small-datasets.md` — Training on small datasets: overfitting, augmentation and EMA

**Hands-on projects**

- **Project 1: ddpm from scratch on mnist and cifar**  
  - Data: MNIST and CIFAR-10  
  - Task: Implement DDPM and DDIM sampling from scratch and study step count against quality.  
  - Deliverables: Implementation, samples and FID against step count.  
  - Pass gate: Loss and sampler verified against a reference implementation on a toy case.
- **Project 2: flow matching vs ddpm**  
  - Data: CIFAR-10 or a small 2D toy distribution  
  - Task: Train a flow-matching model and a DDPM under the same budget and compare quality and sampling cost.  
  - Deliverables: Comparison with confidence intervals.  
  - Pass gate: Same network and training budget.
- **Project 3: classifier free guidance study**  
  - Data: A class- or text-conditional small model  
  - Task: Vary guidance scale and measure fidelity-diversity trade-offs.  
  - Deliverables: Trade-off curves.  
  - Pass gate: Diversity measured explicitly, not only quality.

### 16 — Controllable Image Generation and Editing

**Outcome:** Customize and control image generators for real workflows.

**Lessons**

- `01-prompting-image-models.md` — Prompting image models: prompt structure, negative prompts and seed control
- `02-personalization.md` — Personalization: textual inversion, DreamBooth and LoRA for diffusion models
- `03-spatial-control.md` — Spatial control: ControlNet and T2I-Adapter conditioning
- `04-image-prompt-adapters.md` — Image-prompt adapters: IP-Adapter and reference-image conditioning
- `05-editing.md` — Editing: img2img, SDEdit, inpainting and outpainting
- `06-instruction-based-editing-models.md` — Instruction-based editing models
- `07-super-resolution-and-restoration-pipelines.md` — Super-resolution and restoration pipelines
- `08-workflow-tooling.md` — Workflow tooling: node-based pipelines and reproducible generation configs
- `09-evaluating-controllability.md` — Evaluating controllability: alignment to conditions, identity preservation and human review

**Hands-on projects**

- **Project 1: personalization comparison**  
  - Data: 10 to 20 images of one subject or product you have rights to use  
  - Task: Compare textual inversion, DreamBooth and a LoRA on identity fidelity, prompt flexibility and overfitting.  
  - Deliverables: Comparison with fixed-seed grids and human ratings.  
  - Pass gate: Consent or rights for all training images documented.
- **Project 2: controlnet product image pipeline**  
  - Data: Product photos you have rights to use  
  - Task: Build a controllable pipeline that changes backgrounds while preserving the product, and measure product-shape preservation.  
  - Deliverables: Pipeline and preservation metrics.  
  - Pass gate: Preservation measured with an objective metric and human review.
- **Project 3: inpainting quality audit**  
  - Data: Images with masked regions  
  - Task: Compare inpainting models on seam quality and consistency and catalog failures.  
  - Deliverables: Failure catalog.  
  - Pass gate: Same masks and seeds across models.

### 17 — Video and 3D Generation

**Outcome:** Understand how video and 3D generation work, what they cost and where they fail. This area changes quickly; each lesson must be checked against current releases.

**Lessons**

- `01-video-diffusion.md` — Video diffusion: temporal layers, latent video models and AnimateDiff-style motion modules
- `02-image-to-video-and-text-to-video-pipelines-and-their-conditioning.md` — Image-to-video and text-to-video pipelines and their conditioning
- `03-temporal-consistency.md` — Temporal consistency: flicker, identity drift and long-clip generation
- `04-video-generation-evaluation.md` — Video generation evaluation: FVD and its limits, human evaluation protocols
- `05-compute-and-cost-of-video-generation.md` — Compute and cost of video generation
- `06-neural-radiance-fields-and-3d-gaussian-splatting-for-scene-reconstruction.md` — Neural radiance fields and 3D Gaussian splatting for scene reconstruction
- `07-text-to-3d-and-image-to-3d-approaches-and-datasets-such-as-objaverse.md` — Text-to-3D and image-to-3D approaches and datasets such as Objaverse
- `08-practical-limits-and-failure-catalogs.md` — Practical limits and failure catalogs

**Hands-on projects**

- **Project 1: image to video pipeline and consistency audit**  
  - Data: Still images you have rights to use  
  - Task: Generate short clips with an open image-to-video model and measure temporal consistency.  
  - Deliverables: Consistency metrics and failure catalog.  
  - Pass gate: Metrics defined before generation and applied to all clips.
- **Project 2: gaussian splatting reconstruction**  
  - Data: A photo set of an object or scene you capture  
  - Task: Reconstruct a scene with 3D Gaussian splatting and evaluate novel-view quality on held-out views.  
  - Deliverables: Reconstruction and held-out-view evaluation.  
  - Pass gate: Held-out views never used in optimization.

### 18 — Music and General Audio Generation

**Outcome:** Generate non-speech audio and understand its representations. Speech synthesis and speaker systems are covered in G2.

**Lessons**

- `01-neural-audio-codecs.md` — Neural audio codecs: EnCodec-style discrete tokens
- `02-autoregressive-audio-generation-over-codec-tokens.md` — Autoregressive audio generation over codec tokens
- `03-text-to-music-and-text-to-audio-models-such-as-musicgen.md` — Text-to-music and text-to-audio models such as MusicGen
- `04-diffusion-based-audio-generation.md` — Diffusion-based audio generation
- `05-conditioning.md` — Conditioning: melody, tempo and text control
- `06-evaluating-generated-audio.md` — Evaluating generated audio: FAD, CLAP-based scores and listening tests
- `07-rights-licensing-and-artist-consent-for-music-data.md` — Rights, licensing and artist consent for music data

**Hands-on projects**

- **Project 1: codec reconstruction and token study**  
  - Data: Public-domain or CC-licensed audio  
  - Task: Encode and decode with a neural codec and measure reconstruction quality against bitrate.  
  - Deliverables: Quality-vs-bitrate curves.  
  - Pass gate: Objective metrics plus a short listening test.
- **Project 2: text to audio generation evaluation**  
  - Data: A set of prompts and a public text-to-audio model  
  - Task: Generate audio, compute FAD and CLAP scores and compare with human ratings.  
  - Deliverables: Metric-vs-human correlation analysis.  
  - Pass gate: Blind, randomized listening protocol.

### 19 — Generative Content Provenance Safety and Governance

**Outcome:** Ship generative products responsibly: provenance, safety filtering, copyright and misuse policy.

**Lessons**

- `01-misuse-landscape.md` — Misuse landscape: deepfakes, impersonation, non-consensual imagery and fraud
- `02-content-safety-filtering-for-generated-images-audio-and-text.md` — Content safety filtering for generated images, audio and text
- `03-provenance-and-watermarking.md` — Provenance and watermarking: C2PA metadata and model-level watermarks such as SynthID
- `04-detection-limits.md` — Detection limits: why detectors of generated media are unreliable
- `05-copyright-and-training-data-questions.md` — Copyright and training-data questions: licensing, opt-outs and output similarity checks
- `06-disclosure-and-consent-policy-for-synthetic-media.md` — Disclosure and consent policy for synthetic media
- `07-india-specific-considerations.md` — India-specific considerations: the DPDP Act and the IT Rules amendments on synthetically generated information (confirm final text)
- `08-incident-response-for-generative-products.md` — Incident response for generative products

**Hands-on projects**

- **Project 1: provenance and watermark robustness test**  
  - Data: Generated images you create  
  - Task: Embed provenance metadata and test whether it and any watermark survive resizing, compression and screenshots.  
  - Deliverables: Robustness table.  
  - Pass gate: Transformations applied identically to all samples.
- **Project 2: safety filter evaluation for image generation**  
  - Data: Prompt sets you design with benign and policy-violating cases  
  - Task: Evaluate a prompt and image safety filter for misses and false blocks.  
  - Deliverables: Precision-recall report and policy recommendations.  
  - Pass gate: Handled without producing or retaining harmful content.
- **Project 3: generative product governance pack**  
  - Data: A product concept of your choice  
  - Task: Write the misuse analysis, disclosure policy and incident runbook.  
  - Deliverables: Governance document.  
  - Pass gate: Each risk has an owner and a control.

### 20 — G3 Capstones

**Outcome:** integrate the foundation-model, LLM-application and generative-media tracks in assessed, portfolio-quality work.

- **Capstone 1: train and adapt a small foundation model** (uses Modules 01, 03, 04, 05)  
  Pretrain a small model on curated data, adapt it with parameter-efficient tuning and preference optimization, and report every step with controlled comparisons and honest compute accounting.
- **Capstone 2: production rag and llm application** (uses Modules 07 to 13)  
  Ship a RAG-based LLM application with evaluation gates, security testing, cost and observability dashboards, and a self-hosted vs API decision record.
- **Capstone 3: controllable generative image product** (uses Modules 14 to 16, 19)  
  Build a controllable image generation workflow with evaluation, safety filtering, provenance and a governance pack.
- **Capstone 4: transformer research reproduction** (uses Modules 01, 02, 06)  
  Reproduce a published transformer architecture result at small scale with layer-level equivalence tests and an interpretability analysis.
- **Capstone 5: g3 readiness assessment** (uses All modules)  
  Written and practical assessment against the G3 completion gate.

## G3 completion gate

- Every module project has a written report with repeated-run variance or confidence intervals and a stated limitation.
- All results reproduce from a lockfile, configs and logged seeds, with model versions, hardware, prices and dates recorded.
- Every model and dataset used has its licence and terms of use recorded in the register before use.
- Every LLM application has an evaluation set, a judge calibrated against human labels where a judge is used, and a security test set.
- Spending on paid APIs and compute stays within the recorded budget, with a cost report per capstone.
- At least one negative or inconclusive result per track is reported honestly.
- The four specialist capstones are complete and the readiness assessment is passed.

## Audit and verification

**What was checked and the result**

- Structure: 19 specialist modules each have 6 to 12 lessons and at least one project; the tree contains 277 files and 41 folders, and these counts equal the counts computed from the curriculum data.
- Overlap with the Roadmap: all 170 lesson file names were compared against every lesson file name in `Roadmap.md`. Exact matches: 0. Near matches (similarity 0.80 or higher): 0.
- Structural problems found by the build script: 0.
- Topic-level overlap check: the Roadmap text was searched for RAG, vector search, PEFT, QLoRA, vLLM, prompting, structured outputs, function calling, MCP, prompt injection, Stable Diffusion, GAN, flow matching, latent diffusion, classifier-free guidance, distillation, llama.cpp, Ollama, model merging, LLM-as-judge, hallucination, text-to-image and DeepSpeed. None appear as lessons, so G3 teaches them for the first time. The Roadmap does contain LoRA mathematics, VAE, GAN and diffusion mathematics (Stage 4C), and long-context, MoE, quantization for non-LLM models, SFT, RLHF, DPO and diffusion in practice (Stage 5C and Stage 5D); G3 references and extends these and does not reteach them.
- Verified by web search on the build date (2026-10-26): TRL provides GRPOTrainer and DPOTrainer, and KTO and ORPO are available but their stability labels differ between sources (ORPO appears under an experimental namespace in recent releases), so check current import paths; the OWASP Top 10 for LLM Applications 2025 was published in November 2024 and includes prompt injection, sensitive information disclosure, improper output handling, excessive agency, system prompt leakage, vector and embedding weaknesses, misinformation and unbounded consumption; India's MeitY proposed amendments to the IT Rules, 2021 on synthetically generated information in October 2025 and reports say they were notified with effect from 20 February 2026.
- Reported but not confirmed: the date and final labelling requirements of the India synthetic-media amendments conflict between sources and the final text was not found, so lesson 19-07 must be checked against the notified text; garak's maintainer and features were not confirmed by search; ORPO and KTO stability in TRL is inconsistent across documentation.
- Not verified: library, model and benchmark versions, which change quickly (especially in the video, 3D and image-generation modules); licences of open-weight models; dataset availability and terms; and API prices, which must be recorded with their source and date in the register.
- Manual review of near-name matches: any lesson whose name resembles a Roadmap lesson deepens it for engineering use, and the scope table above states the difference.
- Not verified by execution: no code in this plan has been run. Project pass gates are acceptance criteria to be met when the projects are built.
- Safety note: modules 10, 16 and 19 involve attacks, personal likenesses and misuse analysis. Every project in them specifies consent, rights or a sandbox, and must be carried out only on your own systems and on data you have rights to use.
- Repository safety: this build created only this file; no existing file or folder was created, changed or deleted by it.
