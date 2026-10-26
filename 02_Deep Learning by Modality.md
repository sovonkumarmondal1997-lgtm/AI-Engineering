# Deep Learning by Modality — ML Specialization Roadmap

**Group 2 (G2)** of the specialization that follows Stage 5D of the [Roadmap](./Roadmap.md). It covers original categories **3 Deep Learning Engineering, 4 Natural Language Processing, 5 Computer Vision Engineering, 19 Speech and Audio Machine Learning and 20 Multimodal Machine Learning**. The group's defining question is: *what kind of raw data does the network learn from?* It follows [`Classical and Applied ML_SPECIALIZATION_Roadmap.md`](./Classical%20and%20Applied%20ML_SPECIALIZATION_Roadmap.md), which holds G1.

## G2 summary

| Item | Count |
|---|---|
| Modules (including overview and capstones) | 26 |
| Lesson files | 201 |
| Hands-on project files (module projects, overview project and capstones) | 78 |
| Folders inside the G2 tree | 51 |
| Files inside the G2 tree | 337 |

| Original category | Modules |
|---|---|
| 3 Deep Learning Engineering | 01 to 05 |
| 4 Natural Language Processing | 06 to 11 |
| 5 Computer Vision Engineering | 12 to 16 |
| 19 Speech and Audio Machine Learning | 17 to 20 |
| 20 Multimodal Machine Learning | 21 to 24 |

## Scope and how G2 avoids repeating the Roadmap

G2 starts where Stage 5C stops. These are **already learned** and are only referenced, never retaught: neurons and backpropagation, PyTorch tensors, autograd, `nn.Module` and dataloaders, the training loop, optimizers and schedules, initialization and normalization, dropout and basic augmentation, mixed precision, gradient clipping, the tuning playbook and debugging basics, convolutions, CNN architectures and residual connections, transfer learning and fine-tuning, object detection and segmentation essentials and their metrics, recurrent networks and gated units, word and sentence embeddings, contrastive learning and autoencoder introductions, attention and the transformer block, efficient attention, tokenization and BPE, building a GPT from scratch, pretraining and scaling laws, SFT, RLHF and DPO, decoding and sampling, reasoning models, vision transformers, CLIP and VLM introductions, audio and speech model introductions, diffusion in practice, paper reading. Classical NLP (TF-IDF, naive Bayes), clustering, calibration and SHAP from Stages 5A and 5B, and experiment tracking and MLflow from Stage 5D are also reused rather than repeated.

**Boundaries with other groups** (so nothing overlaps): large language model engineering, RAG, parameter-efficient fine-tuning and image generation belong to **G3**; search and recommendation systems belong to **G6**; model compression, edge deployment and inference acceleration belong to **G10**; dataset curation at scale and synthetic data belong to **G13**; medical and satellite imaging belong to **G9**.

| Roadmap topic already covered | Where G2 goes further |
|---|---|
| PyTorch fundamentals and the training loop (5C) | Module 01: custom autograd, hooks, Lightning, Hydra, compile and profiling, data pipelines and reproducibility on GPUs |
| CNN architectures, tuning playbook (5C) | Module 02: architecture design principles, modern recipes, long-tailed learning and multi-task losses |
| Contrastive learning and autoencoders (5C) | Module 03: SimCLR, BYOL, DINO, MAE, JEPA, metric learning and representation evaluation |
| Transfer learning and fine-tuning (5C) | Module 04: domain shift, test-time adaptation, few-shot, meta-learning and continual learning |
| SHAP and permutation importance for tabular models (5B) | Module 05: Grad-CAM, attribution sanity checks, probing, shortcut learning and OOD detection for deep nets |
| Transformer block, GPT from scratch, tokenization (5C) | Modules 06 to 09: encoder fine-tuning, extraction, text-pair models, seq2seq and evaluation |
| Classical NLP and text classification (5A) | Modules 06 and 11: where encoders beat TF-IDF baselines and applied NLP systems |
| Tokenization lessons (5C) | Module 10: Indic scripts, code-mixing and cross-lingual transfer |
| Detection and segmentation basics, ViT (5C) | Modules 12 to 14: modern backbones, DETR, SAM, tracking, pose and video |
| Audio and speech models introduction (5C), Fourier math (4C) | Modules 17 to 20: audio features in practice, classification, ASR, TTS and speaker systems |
| CLIP and VLM introductions (5C) | Modules 21 to 24: alignment from scratch, fusion, VQA, cross-modal systems and evaluation |

## G2 — Deep Learning by Modality

**Defining question:** What kind of raw data does the network learn from?

```text
ML Specialization/
└── G2 — Deep Learning by Modality/
    ├── 00-G2-Overview/
    │   ├── Projects/
    │   │   ├── 01-g2-gpu-environment-and-evaluation-bootstrap.md
    │   │   └── README.md
    │   ├── 01-g2-scope-and-boundaries-with-stage-5c-and-other-groups.md
    │   ├── 02-prerequisite-map-from-the-roadmap.md
    │   ├── 03-dataset-and-tooling-register.md
    │   ├── 04-evaluation-and-reporting-standards.md
    │   ├── 05-completion-gate.md
    │   ├── README.md
    │   └── learning-plan.md
    ├── 01-Deep-Learning-Engineering-Craft/
    │   ├── Projects/
    │   │   ├── 01-custom-autograd-op-and-gradient-check.md
    │   │   ├── 02-lightning-and-hydra-training-template.md
    │   │   ├── 03-training-performance-audit.md
    │   │   └── README.md
    │   ├── 01-custom-autograd-functions.md
    │   ├── 02-hooks-and-model-surgery.md
    │   ├── 03-training-frameworks.md
    │   ├── 04-configuration-management.md
    │   ├── 05-compiling-and-profiling.md
    │   ├── 06-efficient-data-pipelines.md
    │   ├── 07-reproducibility-on-gpus.md
    │   ├── 08-checkpointing-for-long-runs.md
    │   ├── 09-debugging-silent-failures.md
    │   ├── 10-experiment-logging.md
    │   └── README.md
    ├── 02-Architecture-Design-and-Optimization-Beyond-the-Basics/
    │   ├── Projects/
    │   │   ├── 01-recipe-ablation-from-baseline-to-modern.md
    │   │   ├── 02-long-tailed-classification-study.md
    │   │   ├── 03-multi-task-loss-weighting-experiment.md
    │   │   └── README.md
    │   ├── 01-architecture-design-principles.md
    │   ├── 02-modernized-convolutional-networks.md
    │   ├── 03-normalization-and-activation-choices.md
    │   ├── 04-regularization-recipes.md
    │   ├── 05-optimizer-variants.md
    │   ├── 06-learning-rate-science.md
    │   ├── 07-loss-design.md
    │   ├── 08-long-tailed-and-imbalanced-deep-learning.md
    │   ├── 09-training-recipes.md
    │   └── README.md
    ├── 03-Representation-Learning-and-Self-Supervision/
    │   ├── Projects/
    │   │   ├── 01-simclr-vs-mae-small-scale-study.md
    │   │   ├── 02-face-or-product-retrieval-with-metric-learning.md
    │   │   ├── 03-self-supervised-features-for-small-labeled-data.md
    │   │   └── README.md
    │   ├── 01-why-self-supervision-works.md
    │   ├── 02-contrastive-methods.md
    │   ├── 03-non-contrastive-methods.md
    │   ├── 04-distillation-based-and-masked-methods.md
    │   ├── 05-joint-embedding-predictive-architectures.md
    │   ├── 06-metric-learning.md
    │   ├── 07-evaluating-representations.md
    │   ├── 08-self-supervision-beyond-images.md
    │   └── README.md
    ├── 04-Transfer-Domain-Adaptation-and-Continual-Learning/
    │   ├── Projects/
    │   │   ├── 01-domain-shift-benchmark-digits-and-corruptions.md
    │   │   ├── 02-few-shot-fine-grained-classification.md
    │   │   ├── 03-continual-learning-replay-study.md
    │   │   └── README.md
    │   ├── 01-kinds-of-shift.md
    │   ├── 02-unsupervised-domain-adaptation.md
    │   ├── 03-test-time-adaptation.md
    │   ├── 04-few-shot-learning.md
    │   ├── 05-meta-learning.md
    │   ├── 06-continual-learning.md
    │   ├── 07-evaluation-under-shift.md
    │   ├── 08-choosing-an-adaptation-strategy.md
    │   └── README.md
    ├── 05-Interpreting-Probing-and-Stress-Testing-Deep-Models/
    │   ├── Projects/
    │   │   ├── 01-attribution-sanity-check-study.md
    │   │   ├── 02-shortcut-learning-detection.md
    │   │   ├── 03-ood-detection-benchmark.md
    │   │   └── README.md
    │   ├── 01-saliency-methods.md
    │   ├── 02-sanity-checks-for-attribution.md
    │   ├── 03-attention-analysis.md
    │   ├── 04-probing-classifiers.md
    │   ├── 05-concept-based-explanations.md
    │   ├── 06-spurious-correlations.md
    │   ├── 07-robustness-testing.md
    │   ├── 08-out-of-distribution-detection.md
    │   └── README.md
    ├── 06-NLP-Encoder-Models-and-Text-Understanding/
    │   ├── Projects/
    │   │   ├── 01-encoder-finetuning-benchmark.md
    │   │   ├── 02-domain-adaptive-pretraining-study.md
    │   │   ├── 03-few-label-text-classification-with-setfit.md
    │   │   └── README.md
    │   ├── 01-encoder-pretraining-objectives.md
    │   ├── 02-the-encoder-family.md
    │   ├── 03-fine-tuning-for-text-classification.md
    │   ├── 04-long-documents.md
    │   ├── 05-continued-pretraining.md
    │   ├── 06-few-label-text-classification.md
    │   ├── 07-multi-label-and-hierarchical-text-classification-with-encoders.md
    │   ├── 08-calibration-and-error-analysis-of-text-classifiers.md
    │   ├── 09-comparing-encoder-fine-tuning-with-classical-tf-idf-baselines-from-stage-5a-and-with-prompting.md
    │   └── README.md
    ├── 07-Sequence-Labeling-and-Information-Extraction/
    │   ├── Projects/
    │   │   ├── 01-ner-from-scratch-to-production-quality.md
    │   │   ├── 02-annotate-and-model-a-custom-extraction-task.md
    │   │   ├── 03-weak-supervision-labeling-function-study.md
    │   │   └── README.md
    │   ├── 01-sequence-labeling.md
    │   ├── 02-named-entity-recognition-with-encoders.md
    │   ├── 03-evaluation-of-extraction.md
    │   ├── 04-span-based-models-and-nested-entities.md
    │   ├── 05-relation-extraction-and-event-extraction.md
    │   ├── 06-entity-linking-and-normalization-to-knowledge-bases.md
    │   ├── 07-zero-shot-and-generalist-extraction-models-such-as-gliner.md
    │   ├── 08-annotation-workflows.md
    │   ├── 09-weak-supervision-for-text.md
    │   └── README.md
    ├── 08-Semantic-Matching-Question-Answering-and-Inference/
    │   ├── Projects/
    │   │   ├── 01-sentence-embedding-finetuning-study.md
    │   │   ├── 02-extractive-qa-on-squad-2.md
    │   │   ├── 03-duplicate-detection-pipeline.md
    │   │   └── README.md
    │   ├── 01-sentence-pair-modeling.md
    │   ├── 02-training-sentence-embeddings.md
    │   ├── 03-semantic-textual-similarity-and-paraphrase-detection.md
    │   ├── 04-natural-language-inference.md
    │   ├── 05-extractive-question-answering.md
    │   ├── 06-duplicate-and-near-duplicate-detection-at-scale.md
    │   ├── 07-zero-shot-classification-via-entailment.md
    │   ├── 08-evaluating-semantic-models.md
    │   └── README.md
    ├── 09-Sequence-to-Sequence-NLP-Translation-and-Summarization/
    │   ├── Projects/
    │   │   ├── 01-fine-tune-a-summarizer-and-audit-faithfulness.md
    │   │   ├── 02-domain-adapted-translation-system.md
    │   │   ├── 03-metric-vs-human-judgement-study.md
    │   │   └── README.md
    │   ├── 01-encoder-decoder-models.md
    │   ├── 02-fine-tuning-seq2seq-models.md
    │   ├── 03-machine-translation-fundamentals.md
    │   ├── 04-abstractive-and-extractive-summarization-compared.md
    │   ├── 05-constrained-and-controlled-generation.md
    │   ├── 06-automatic-metrics.md
    │   ├── 07-faithfulness-and-hallucination-in-summaries.md
    │   ├── 08-human-evaluation-design.md
    │   └── README.md
    ├── 10-Multilingual-and-Indic-Language-NLP/
    │   ├── Projects/
    │   │   ├── 01-multilingual-classification-and-transfer-study.md
    │   │   ├── 02-tokenizer-fragmentation-audit.md
    │   │   ├── 03-hinglish-sentiment-system.md
    │   │   └── README.md
    │   ├── 01-indian-language-landscape.md
    │   ├── 02-tokenization-for-indic-scripts.md
    │   ├── 03-normalization-and-transliteration.md
    │   ├── 04-code-mixed-text-such-as-hinglish.md
    │   ├── 05-multilingual-encoders.md
    │   ├── 06-cross-lingual-transfer.md
    │   ├── 07-indic-translation.md
    │   ├── 08-evaluating-across-languages.md
    │   └── README.md
    ├── 11-Applied-NLP-Systems/
    │   ├── Projects/
    │   │   ├── 01-pii-redaction-pipeline.md
    │   │   ├── 02-toxicity-moderation-with-bias-audit.md
    │   │   ├── 03-topic-discovery-and-evaluation.md
    │   │   └── README.md
    │   ├── 01-text-classification-at-scale.md
    │   ├── 02-sentiment-and-aspect-based-analysis.md
    │   ├── 03-content-moderation.md
    │   ├── 04-pii-detection-and-redaction.md
    │   ├── 05-topic-discovery.md
    │   ├── 06-document-processing-pipelines.md
    │   ├── 07-human-review-workflows-and-active-learning-for-text.md
    │   ├── 08-nlp-error-monitoring-in-production.md
    │   └── README.md
    ├── 12-Modern-Vision-Backbones-and-Training-Recipes/
    │   ├── Projects/
    │   │   ├── 01-backbone-selection-benchmark.md
    │   │   ├── 02-augmentation-policy-study.md
    │   │   ├── 03-fine-grained-recognition-project.md
    │   │   └── README.md
    │   ├── 01-backbone-landscape.md
    │   ├── 02-data-efficient-transformers.md
    │   ├── 03-using-timm.md
    │   ├── 04-augmentation-policies.md
    │   ├── 05-resolution-and-aspect-ratio.md
    │   ├── 06-fine-grained-recognition.md
    │   ├── 07-ensembling-and-calibration-for-image-classifiers.md
    │   ├── 08-choosing-a-backbone.md
    │   └── README.md
    ├── 13-Advanced-Detection-Segmentation-and-Tracking/
    │   ├── Projects/
    │   │   ├── 01-detector-comparison-on-custom-data.md
    │   │   ├── 02-sam-assisted-labeling-pipeline.md
    │   │   ├── 03-multi-object-tracking-system.md
    │   │   └── README.md
    │   ├── 01-real-time-detectors.md
    │   ├── 02-transformer-detectors.md
    │   ├── 03-instance-and-panoptic-segmentation.md
    │   ├── 04-promptable-segmentation.md
    │   ├── 05-open-vocabulary-detection.md
    │   ├── 06-multi-object-tracking.md
    │   ├── 07-pose-estimation-and-keypoints.md
    │   ├── 08-detection-error-analysis.md
    │   ├── 09-small-object-and-crowded-scene-detection.md
    │   └── README.md
    ├── 14-Video-and-Temporal-Visual-Understanding/
    │   ├── Projects/
    │   │   ├── 01-action-recognition-benchmark.md
    │   │   ├── 02-frame-sampling-efficiency-study.md
    │   │   ├── 03-scene-bias-diagnostic.md
    │   │   └── README.md
    │   ├── 01-video-data-fundamentals.md
    │   ├── 02-two-stream-and-3d-convolution-models.md
    │   ├── 03-video-transformers.md
    │   ├── 04-optical-flow-and-motion-cues.md
    │   ├── 05-temporal-action-localization.md
    │   ├── 06-efficient-video-inference.md
    │   ├── 07-video-self-supervision-and-pretraining.md
    │   ├── 08-evaluating-video-models.md
    │   └── README.md
    ├── 15-OCR-Document-and-Visual-Text-Understanding/
    │   ├── Projects/
    │   │   ├── 01-receipt-and-invoice-extraction.md
    │   │   ├── 02-crnn-ctc-recognizer-from-scratch.md
    │   │   ├── 03-table-extraction-pipeline.md
    │   │   └── README.md
    │   ├── 01-text-detection.md
    │   ├── 02-text-recognition.md
    │   ├── 03-transformer-ocr.md
    │   ├── 04-layout-analysis.md
    │   ├── 05-table-detection-and-structure-recognition.md
    │   ├── 06-handwriting-recognition.md
    │   ├── 07-indic-script-ocr.md
    │   ├── 08-ocr-evaluation.md
    │   └── README.md
    ├── 16-Vision-Data-Pipelines-and-Annotation-Engineering/
    │   ├── Projects/
    │   │   ├── 01-annotation-format-converter-and-validator.md
    │   │   ├── 02-near-duplicate-leakage-audit.md
    │   │   ├── 03-dataloader-throughput-optimization.md
    │   │   └── README.md
    │   ├── 01-annotation-formats.md
    │   ├── 02-annotation-tooling-and-guidelines-for-boxes-masks-and-keypoints.md
    │   ├── 03-label-quality-in-vision.md
    │   ├── 04-augmentation-libraries.md
    │   ├── 05-fast-data-loading.md
    │   ├── 06-image-quality-issues.md
    │   ├── 07-privacy-in-vision-data.md
    │   ├── 08-dataset-versioning-and-splits-for-images.md
    │   └── README.md
    ├── 17-Audio-Signal-Foundations-and-Representations/
    │   ├── Projects/
    │   │   ├── 01-feature-extraction-from-first-principles.md
    │   │   ├── 02-augmentation-ablation-for-audio-classification.md
    │   │   ├── 03-audio-bug-hunt.md
    │   │   └── README.md
    │   ├── 01-digital-audio.md
    │   ├── 02-spectrograms.md
    │   ├── 03-mel-scales-and-features.md
    │   ├── 04-audio-tooling.md
    │   ├── 05-audio-augmentation.md
    │   ├── 06-learned-audio-representations.md
    │   ├── 07-audio-datasets-and-licensing.md
    │   ├── 08-common-audio-bugs.md
    │   └── README.md
    ├── 18-Audio-Classification-Enhancement-and-Source-Separation/
    │   ├── Projects/
    │   │   ├── 01-urban-sound-event-detection.md
    │   │   ├── 02-keyword-spotting-system.md
    │   │   ├── 03-speech-enhancement-evaluation.md
    │   │   └── README.md
    │   ├── 01-audio-classification-with-cnns-on-spectrograms.md
    │   ├── 02-audio-transformers-and-pretrained-audio-models.md
    │   ├── 03-sound-event-detection.md
    │   ├── 04-keyword-spotting.md
    │   ├── 05-speech-enhancement-and-denoising.md
    │   ├── 06-source-separation.md
    │   ├── 07-music-information-retrieval-basics.md
    │   ├── 08-audio-quality-evaluation.md
    │   └── README.md
    ├── 19-Automatic-Speech-Recognition/
    │   ├── Projects/
    │   │   ├── 01-finetune-wav2vec2-and-whisper.md
    │   │   ├── 02-streaming-asr-latency-study.md
    │   │   ├── 03-accent-and-noise-robustness-audit.md
    │   │   └── README.md
    │   ├── 01-asr-problem-and-history.md
    │   ├── 02-ctc.md
    │   ├── 03-rnn-transducer-and-attention-encoder-decoder-models.md
    │   ├── 04-self-supervised-speech-models.md
    │   ├── 05-whisper.md
    │   ├── 06-language-model-fusion-and-decoding-with-beam-search.md
    │   ├── 07-streaming-asr.md
    │   ├── 08-speaker-diarization-and-punctuation-restoration.md
    │   ├── 09-evaluating-asr.md
    │   ├── 10-indic-asr.md
    │   └── README.md
    ├── 20-Text-to-Speech-Voice-and-Speaker-Systems/
    │   ├── Projects/
    │   │   ├── 01-single-speaker-tts-system.md
    │   │   ├── 02-speaker-verification-system.md
    │   │   ├── 03-synthetic-speech-detector-and-consent-policy.md
    │   │   └── README.md
    │   ├── 01-tts-pipeline.md
    │   ├── 02-acoustic-models.md
    │   ├── 03-neural-vocoders.md
    │   ├── 04-end-to-end-tts.md
    │   ├── 05-multi-speaker-and-expressive-speech.md
    │   ├── 06-speaker-verification.md
    │   ├── 07-voice-conversion-and-its-risks.md
    │   ├── 08-evaluating-tts.md
    │   ├── 09-synthetic-speech-detection-and-consent-policy.md
    │   └── README.md
    ├── 21-Multimodal-Alignment-and-Fusion/
    │   ├── Projects/
    │   │   ├── 01-small-clip-from-scratch.md
    │   │   ├── 02-missing-modality-robustness-study.md
    │   │   ├── 03-image-plus-tabular-fusion.md
    │   │   └── README.md
    │   ├── 01-fusion-strategies.md
    │   ├── 02-contrastive-alignment.md
    │   ├── 03-extending-alignment.md
    │   ├── 04-missing-and-noisy-modalities.md
    │   ├── 05-modality-imbalance.md
    │   ├── 06-multimodal-pretraining-objectives.md
    │   ├── 07-tabular-and-sensor-fusion-with-images-or-text.md
    │   ├── 08-evaluating-fusion.md
    │   └── README.md
    ├── 22-Vision-Language-Tasks-and-Models/
    │   ├── Projects/
    │   │   ├── 01-vqa-with-bias-analysis.md
    │   │   ├── 02-domain-specific-captioning.md
    │   │   ├── 03-vlm-hallucination-probe.md
    │   │   └── README.md
    │   ├── 01-image-captioning.md
    │   ├── 02-visual-question-answering.md
    │   ├── 03-visual-grounding-and-referring-expressions.md
    │   ├── 04-image-text-retrieval.md
    │   ├── 05-vision-language-model-architectures.md
    │   ├── 06-adapting-a-vision-language-model-to-a-task-with-a-small-trainable-adapter.md
    │   ├── 07-hallucination-in-vision-language-models.md
    │   ├── 08-document-and-chart-question-answering.md
    │   └── README.md
    ├── 23-Audio-Video-and-Cross-Modal-Systems/
    │   ├── Projects/
    │   │   ├── 01-audio-text-retrieval-system.md
    │   │   ├── 02-cascaded-vs-end-to-end-speech-translation.md
    │   │   ├── 03-video-text-retrieval-prototype.md
    │   │   └── README.md
    │   ├── 01-audio-captioning-and-audio-text-retrieval.md
    │   ├── 02-video-text-retrieval-and-video-captioning.md
    │   ├── 03-video-question-answering.md
    │   ├── 04-audio-visual-speech-recognition-and-active-speaker-detection.md
    │   ├── 05-speech-translation.md
    │   ├── 06-multimodal-emotion-and-sentiment-analysis.md
    │   ├── 07-time-alignment-across-modalities.md
    │   ├── 08-cost-of-multimodal-inference.md
    │   └── README.md
    ├── 24-Multimodal-Evaluation-Robustness-and-Responsible-Use/
    │   ├── Projects/
    │   │   ├── 01-modality-ablation-and-bias-audit.md
    │   │   ├── 02-benchmark-contamination-check.md
    │   │   ├── 03-multimodal-failure-catalog.md
    │   │   └── README.md
    │   ├── 01-multimodal-benchmark-landscape-and-contamination-risks.md
    │   ├── 02-modality-bias-and-shortcut-detection.md
    │   ├── 03-robustness.md
    │   ├── 04-bias-and-fairness-across-demographic-groups-in-vision-and-speech-models.md
    │   ├── 05-privacy-and-consent-for-faces-voices-and-documents.md
    │   ├── 06-deepfake-and-synthetic-media-risks-and-detection-limits.md
    │   ├── 07-evaluation-reporting.md
    │   ├── 08-deployment-checklist-for-multimodal-products.md
    │   └── README.md
    ├── 25-G2-Capstones/
    │   ├── 01-modality-specialist-project-nlp.md
    │   ├── 02-modality-specialist-project-vision.md
    │   ├── 03-modality-specialist-project-speech.md
    │   ├── 04-multimodal-system-project.md
    │   ├── 05-g2-readiness-assessment.md
    │   └── README.md
    └── README.md
```

### 00 — G2 Overview

**Purpose:** the single authoritative plan for G2 with scope, boundaries, prerequisite map, dataset and licence register, evaluation standards and completion gate.

- `01-g2-scope-and-boundaries-with-stage-5c-and-other-groups.md` — what G2 teaches and what it leaves to other groups.
- `02-prerequisite-map-from-the-roadmap.md` — Roadmap stages and modules assumed for each G2 module.
- `03-dataset-and-tooling-register.md` — every dataset, licence, access condition, library and version pin, including datasets that need registration or have usage restrictions.
- `04-evaluation-and-reporting-standards.md` — seeds, confidence intervals, subgroup reporting, human-evaluation protocols and report template.
- `05-completion-gate.md` — measurable criteria to finish G2.
- `learning-plan.md` — recommended order, per-modality tracks and compute budget.

**Project 1: g2 gpu environment and evaluation bootstrap**  
- Data: small samples of one text, one image and one audio dataset.  
- Task: build a reproducible GPU workspace with pinned tooling and an evaluation skeleton that logs seeds, splits, hardware and library versions.  
- Deliverables: lockfile, smoke tests for each modality and a compute log.  
- Pass gate: a clean machine reproduces the smoke tests from the lockfile.

### 01 — Deep Learning Engineering Craft

**Outcome:** Write, debug, profile and scale training code like an engineer rather than a notebook user. PyTorch basics, the training loop, mixed precision and tuning playbooks are covered in Stage 5C and are not repeated.

**Lessons**

- `01-custom-autograd-functions.md` — Custom autograd functions: writing forward and backward passes and verifying them with gradient checks
- `02-hooks-and-model-surgery.md` — Hooks and model surgery: forward and backward hooks, feature extraction and layer replacement
- `03-training-frameworks.md` — Training frameworks: PyTorch Lightning and plain-PyTorch trainer design compared
- `04-configuration-management.md` — Configuration management: Hydra and structured configs for reproducible experiments
- `05-compiling-and-profiling.md` — Compiling and profiling: torch.compile, the PyTorch profiler and finding data-loader vs GPU bottlenecks
- `06-efficient-data-pipelines.md` — Efficient data pipelines: sharded datasets, WebDataset and streaming from object storage
- `07-reproducibility-on-gpus.md` — Reproducibility on GPUs: nondeterministic kernels, seeds and what can actually be made deterministic
- `08-checkpointing-for-long-runs.md` — Checkpointing for long runs: resumable training, EMA weights and best-model selection
- `09-debugging-silent-failures.md` — Debugging silent failures: overfit-one-batch tests, gradient and activation statistics and data-bug hunts
- `10-experiment-logging.md` — Experiment logging: Weights & Biases and TensorBoard alongside MLflow from Stage 5D

**Hands-on projects**

- **Project 1: custom autograd op and gradient check**  
  - Data: Synthetic data and a small image dataset  
  - Task: Implement a custom activation and a custom loss as autograd functions, verify with numerical gradient checks and use them in a network.  
  - Deliverables: Tested functions, gradient-check report and a training run using them.  
  - Pass gate: Analytical and numerical gradients agree within a stated tolerance in float64.
- **Project 2: lightning and hydra training template**  
  - Data: CIFAR-100  
  - Task: Build a reusable training template with Lightning, Hydra configs, logging, checkpoint resume and a smoke-test suite.  
  - Deliverables: Template repository, three example configs and tests.  
  - Pass gate: A run killed midway resumes to the same final metric within seed noise.
- **Project 3: training performance audit**  
  - Data: A model and dataset of your choice from Stage 5C  
  - Task: Profile an existing training run, remove data-loading and kernel bottlenecks and report throughput before and after.  
  - Deliverables: Profiler traces, change log and throughput table.  
  - Pass gate: Every claimed speed-up is measured on the same hardware with repeated runs.

### 02 — Architecture Design and Optimization Beyond the Basics

**Outcome:** Understand why modern architectures and training recipes work, and design and train them deliberately. Residual networks, normalization basics and tuning playbooks are covered in Stage 5C.

**Lessons**

- `01-architecture-design-principles.md` — Architecture design principles: receptive field, depth vs width and compound scaling as in EfficientNet
- `02-modernized-convolutional-networks.md` — Modernized convolutional networks: ConvNeXt design choices and MLP-Mixer-style models
- `03-normalization-and-activation-choices.md` — Normalization and activation choices: LayerNorm, GroupNorm, RMSNorm, GELU and SwiGLU in context
- `04-regularization-recipes.md` — Regularization recipes: label smoothing, stochastic depth, mixup and CutMix
- `05-optimizer-variants.md` — Optimizer variants: AdamW, Lion, Sharpness-Aware Minimization and weight averaging
- `06-learning-rate-science.md` — Learning-rate science: warmup, cosine and one-cycle schedules and why they work
- `07-loss-design.md` — Loss design: focal, margin, ranking and multi-task losses and uncertainty-weighted multi-task training
- `08-long-tailed-and-imbalanced-deep-learning.md` — Long-tailed and imbalanced deep learning: re-weighting, logit adjustment and decoupled training
- `09-training-recipes.md` — Training recipes: reproducing a modern recipe step by step and ablating each component

**Hands-on projects**

- **Project 1: recipe ablation from baseline to modern**  
  - Data: CIFAR-100 and Oxford-IIIT Pets  
  - Task: Start from a plain ResNet recipe and add one change at a time (augmentation, schedule, regularization, optimizer); record the effect of each.  
  - Deliverables: Ablation table with confidence intervals across seeds.  
  - Pass gate: At least 3 seeds per row; changes with gains inside seed noise are labeled as such.
- **Project 2: long tailed classification study**  
  - Data: CIFAR-100-LT (long-tailed version) built by you from CIFAR-100  
  - Task: Compare plain training, re-weighting, logit adjustment and decoupled training on head, medium and tail classes.  
  - Deliverables: Per-group accuracy table and recommendation.  
  - Pass gate: Report tail-class accuracy separately from overall accuracy.
- **Project 3: multi task loss weighting experiment**  
  - Data: A dataset with two labels, for example Oxford-IIIT Pets breed and species  
  - Task: Train multi-task networks with fixed, uncertainty-weighted and gradient-balanced loss weighting.  
  - Deliverables: Comparison against single-task models.  
  - Pass gate: Negative transfer cases reported where they occur.

### 03 — Representation Learning and Self Supervision

**Outcome:** Learn useful representations without labels and measure their quality properly. The introductory contrastive learning and autoencoder lessons in Stage 5C are the starting point.

**Lessons**

- `01-why-self-supervision-works.md` — Why self-supervision works: pretext tasks, invariances and collapse
- `02-contrastive-methods.md` — Contrastive methods: SimCLR, MoCo and the role of negatives and temperature
- `03-non-contrastive-methods.md` — Non-contrastive methods: BYOL, SimSiam, Barlow Twins and VICReg
- `04-distillation-based-and-masked-methods.md` — Distillation-based and masked methods: DINO, DINOv2 and masked autoencoders
- `05-joint-embedding-predictive-architectures.md` — Joint-embedding predictive architectures: I-JEPA and predictive objectives
- `06-metric-learning.md` — Metric learning: triplet loss, ArcFace and hard-example mining
- `07-evaluating-representations.md` — Evaluating representations: linear probing, k-NN, few-label fine-tuning and their disagreements
- `08-self-supervision-beyond-images.md` — Self-supervision beyond images: sequences, tabular data and audio overview

**Hands-on projects**

- **Project 1: simclr vs mae small scale study**  
  - Data: CIFAR-10 or STL-10 unlabeled split  
  - Task: Pretrain a small network with SimCLR and with a masked autoencoder; compare with supervised pretraining on linear probe and 1 percent label fine-tuning.  
  - Deliverables: Pretraining code, evaluation table and collapse diagnostics.  
  - Pass gate: Report representation-quality metrics with the same probe protocol for every method.
- **Project 2: face or product retrieval with metric learning**  
  - Data: A public product-image or fine-grained retrieval dataset such as Stanford Online Products or CUB-200  
  - Task: Train an embedding with triplet and ArcFace losses and evaluate Recall@K.  
  - Deliverables: Embedding model, retrieval evaluation and hard-negative analysis.  
  - Pass gate: Recall@K reported on a split with disjoint classes from training.
- **Project 3: self supervised features for small labeled data**  
  - Data: Any small labeled image dataset with 100 to 1000 labels  
  - Task: Compare DINOv2 features, supervised ImageNet features and training from scratch under tiny label budgets.  
  - Deliverables: Label-budget learning curves.  
  - Pass gate: Confidence bands from repeated label sampling.

### 04 — Transfer Domain Adaptation and Continual Learning

**Outcome:** Make models work when the data distribution shifts, labels are scarce or tasks arrive over time. Basic transfer learning and fine-tuning are covered in Stage 5C and are not repeated.

**Lessons**

- `01-kinds-of-shift.md` — Kinds of shift: covariate, label and concept shift in deep models
- `02-unsupervised-domain-adaptation.md` — Unsupervised domain adaptation: DANN, CORAL and pseudo-labeling
- `03-test-time-adaptation.md` — Test-time adaptation: entropy minimization and batch-norm statistic adaptation
- `04-few-shot-learning.md` — Few-shot learning: prototypical networks and matching networks
- `05-meta-learning.md` — Meta-learning: MAML and when it is worth the cost
- `06-continual-learning.md` — Continual learning: catastrophic forgetting, replay and regularization methods
- `07-evaluation-under-shift.md` — Evaluation under shift: held-out domains, worst-group accuracy and benchmark pitfalls
- `08-choosing-an-adaptation-strategy.md` — Choosing an adaptation strategy: decision tree from labels available to compute available

**Hands-on projects**

- **Project 1: domain shift benchmark digits and corruptions**  
  - Data: MNIST to SVHN to USPS and CIFAR-10-C corruptions  
  - Task: Measure the drop under shift, then apply DANN, CORAL and test-time adaptation and compare.  
  - Deliverables: Shift-severity curves and a method comparison.  
  - Pass gate: Source-only baseline and oracle target-supervised upper bound reported for every setting.
- **Project 2: few shot fine grained classification**  
  - Data: CUB-200 or Omniglot  
  - Task: Compare prototypical networks, fine-tuning a pretrained backbone and a linear probe in 1-shot and 5-shot settings.  
  - Deliverables: Episodic evaluation with confidence intervals.  
  - Pass gate: At least 600 test episodes per setting.
- **Project 3: continual learning replay study**  
  - Data: Split-CIFAR-100 in 10 sequential tasks  
  - Task: Compare naive fine-tuning, experience replay and a regularization method on average accuracy and forgetting.  
  - Deliverables: Forgetting curves and memory-budget analysis.  
  - Pass gate: Memory budget of the replay buffer stated and enforced.

### 05 — Interpreting Probing and Stress Testing Deep Models

**Outcome:** Look inside deep networks, check what they actually rely on and test robustness before trusting them. SHAP and permutation importance for tabular models are covered in Stage 5B.

**Lessons**

- `01-saliency-methods.md` — Saliency methods: gradients, Grad-CAM and Integrated Gradients
- `02-sanity-checks-for-attribution.md` — Sanity checks for attribution: randomization tests and failure cases
- `03-attention-analysis.md` — Attention analysis: what attention maps do and do not explain
- `04-probing-classifiers.md` — Probing classifiers: what a layer encodes and the limits of probing
- `05-concept-based-explanations.md` — Concept-based explanations: TCAV and concept bottleneck models
- `06-spurious-correlations.md` — Spurious correlations: shortcut learning and worst-group evaluation
- `07-robustness-testing.md` — Robustness testing: common corruptions, adversarial intuition and distribution-shift test suites
- `08-out-of-distribution-detection.md` — Out-of-distribution detection: max-softmax, energy and Mahalanobis scores

**Hands-on projects**

- **Project 1: attribution sanity check study**  
  - Data: ImageNet-pretrained ResNet on a sample of images  
  - Task: Apply Grad-CAM and Integrated Gradients, then run randomization sanity checks to see which explanations pass.  
  - Deliverables: Attribution gallery and sanity-check results.  
  - Pass gate: Methods that fail randomization checks are reported as such.
- **Project 2: shortcut learning detection**  
  - Data: Waterbirds-style dataset built from CUB birds and Places backgrounds, or the public Waterbirds data  
  - Task: Train a standard classifier, expose its reliance on background and compare with a worst-group-robust training method.  
  - Deliverables: Worst-group accuracy table and explanation evidence.  
  - Pass gate: Worst-group accuracy reported alongside average accuracy.
- **Project 3: ood detection benchmark**  
  - Data: CIFAR-10 as in-distribution against SVHN and CIFAR-100 as out-of-distribution  
  - Task: Compare max-softmax, energy and Mahalanobis OOD detectors by AUROC and false-positive rate at 95 percent recall.  
  - Deliverables: Detector comparison and failure examples.  
  - Pass gate: Near-OOD and far-OOD sets analyzed separately.

### 06 — NLP Encoder Models and Text Understanding

**Outcome:** Fine-tune and adapt encoder language models for classification and understanding tasks. Transformer internals, tokenization and decoder-only LLMs are covered in Stage 5C; large-model engineering is covered later in G3.

**Lessons**

- `01-encoder-pretraining-objectives.md` — Encoder pretraining objectives: masked language modeling, ELECTRA-style replaced-token detection and sentence-pair objectives
- `02-the-encoder-family.md` — The encoder family: BERT, RoBERTa, DeBERTa and distilled variants compared
- `03-fine-tuning-for-text-classification.md` — Fine-tuning for text classification: hyperparameters, stability and seed variance
- `04-long-documents.md` — Long documents: chunking, sliding windows and long-context encoders
- `05-continued-pretraining.md` — Continued pretraining: adapting an encoder to a domain with unlabeled text
- `06-few-label-text-classification.md` — Few-label text classification: SetFit and data-efficient fine-tuning
- `07-multi-label-and-hierarchical-text-classification-with-encoders.md` — Multi-label and hierarchical text classification with encoders
- `08-calibration-and-error-analysis-of-text-classifiers.md` — Calibration and error analysis of text classifiers
- `09-comparing-encoder-fine-tuning-with-classical-tf-idf-baselines-from-stage-5a-and-with-prompting.md` — Comparing encoder fine-tuning with classical TF-IDF baselines from Stage 5A and with prompting

**Hands-on projects**

- **Project 1: encoder finetuning benchmark**  
  - Data: SST-2, AG News and a multi-label dataset such as GoEmotions  
  - Task: Fine-tune three encoders and a TF-IDF baseline; report accuracy, F1, variance across seeds and training cost.  
  - Deliverables: Benchmark table with confidence intervals and cost per point of accuracy.  
  - Pass gate: At least 5 seeds per configuration.
- **Project 2: domain adaptive pretraining study**  
  - Data: A domain corpus of your choice, for example public biomedical abstracts or legal text, with a downstream classification task  
  - Task: Compare off-the-shelf, continued-pretrained and from-scratch encoders on the downstream task.  
  - Deliverables: Pretraining logs and downstream comparison.  
  - Pass gate: Compute budget stated; gains compared with seed variance.
- **Project 3: few label text classification with setfit**  
  - Data: A public text dataset with 8, 16 and 64 labels per class  
  - Task: Compare SetFit, standard fine-tuning and TF-IDF with logistic regression at each label budget.  
  - Deliverables: Label-budget curves.  
  - Pass gate: Repeated label sampling with confidence bands.

### 07 — Sequence Labeling and Information Extraction

**Outcome:** Extract entities, relations and structure from text, and build the annotation and evaluation workflow that makes extraction trustworthy.

**Lessons**

- `01-sequence-labeling.md` — Sequence labeling: BIO and BILOU schemes and token-level modeling
- `02-named-entity-recognition-with-encoders.md` — Named entity recognition with encoders: subword alignment problems and CRF output layers
- `03-evaluation-of-extraction.md` — Evaluation of extraction: entity-level metrics with seqeval and strict vs partial matching
- `04-span-based-models-and-nested-entities.md` — Span-based models and nested entities
- `05-relation-extraction-and-event-extraction.md` — Relation extraction and event extraction
- `06-entity-linking-and-normalization-to-knowledge-bases.md` — Entity linking and normalization to knowledge bases
- `07-zero-shot-and-generalist-extraction-models-such-as-gliner.md` — Zero-shot and generalist extraction models such as GLiNER
- `08-annotation-workflows.md` — Annotation workflows: guidelines, Label Studio, inter-annotator agreement and adjudication
- `09-weak-supervision-for-text.md` — Weak supervision for text: labeling functions, distant supervision and their noise

**Hands-on projects**

- **Project 1: ner from scratch to production quality**  
  - Data: CoNLL-2003 and WNUT-17 (emerging entities)  
  - Task: Train a BiLSTM-CRF, an encoder-based tagger and a zero-shot model; analyze errors by entity type and subword effects.  
  - Deliverables: Models, strict and partial match metrics, error taxonomy.  
  - Pass gate: Metrics use entity-level matching and the matching rule is stated.
- **Project 2: annotate and model a custom extraction task**  
  - Data: 200 to 500 public-domain documents you annotate yourself, for example job postings or recipes  
  - Task: Write guidelines, annotate with a second annotator on a subset, measure agreement and train an extraction model.  
  - Deliverables: Guidelines, agreement report, adjudicated dataset and model.  
  - Pass gate: Inter-annotator agreement computed and disagreements explained.
- **Project 3: weak supervision labeling function study**  
  - Data: A text classification or extraction dataset with a held-out gold set  
  - Task: Write labeling functions, combine them with a label model and compare with a small gold-labeled training set.  
  - Deliverables: Labeling-function coverage and conflict analysis.  
  - Pass gate: Final evaluation only on the untouched gold set.

### 08 — Semantic Matching Question Answering and Inference

**Outcome:** Model relationships between texts: similarity, entailment, duplication and extractive answers. Retrieval systems are built in G6 and retrieval-augmented generation in G3; this module covers the underlying text-pair models.

**Lessons**

- `01-sentence-pair-modeling.md` — Sentence-pair modeling: cross-encoders and bi-encoders compared
- `02-training-sentence-embeddings.md` — Training sentence embeddings: contrastive fine-tuning with in-batch and hard negatives
- `03-semantic-textual-similarity-and-paraphrase-detection.md` — Semantic textual similarity and paraphrase detection
- `04-natural-language-inference.md` — Natural language inference: entailment as a general-purpose building block
- `05-extractive-question-answering.md` — Extractive question answering: SQuAD-style span prediction and unanswerable questions
- `06-duplicate-and-near-duplicate-detection-at-scale.md` — Duplicate and near-duplicate detection at scale
- `07-zero-shot-classification-via-entailment.md` — Zero-shot classification via entailment
- `08-evaluating-semantic-models.md` — Evaluating semantic models: correlation metrics, exact match, F1 and annotation noise

**Hands-on projects**

- **Project 1: sentence embedding finetuning study**  
  - Data: STS-B, MultiNLI and a duplicate-question dataset such as Quora Question Pairs  
  - Task: Fine-tune a bi-encoder with several negative-sampling strategies and compare with a cross-encoder on accuracy and latency.  
  - Deliverables: Training code, evaluation and latency table.  
  - Pass gate: Latency measured per pair at stated batch size.
- **Project 2: extractive qa on squad 2**  
  - Data: SQuAD 2.0  
  - Task: Fine-tune an encoder for span extraction with unanswerable-question handling; analyze errors by question type.  
  - Deliverables: Model, exact-match and F1 and an error taxonomy.  
  - Pass gate: No-answer threshold chosen on validation only.
- **Project 3: duplicate detection pipeline**  
  - Data: Quora Question Pairs or a public product-listing duplicates dataset  
  - Task: Build a two-stage pipeline: cheap candidate generation then a cross-encoder verifier.  
  - Deliverables: Pipeline with precision and recall at each stage.  
  - Pass gate: Candidate-stage recall reported separately.

### 09 — Sequence to Sequence NLP Translation and Summarization

**Outcome:** Build and evaluate encoder-decoder systems for translation, summarization and text rewriting, with honest metrics. Decoding and sampling basics are covered in Stage 5C.

**Lessons**

- `01-encoder-decoder-models.md` — Encoder-decoder models: T5, BART and multilingual variants
- `02-fine-tuning-seq2seq-models.md` — Fine-tuning seq2seq models: data formatting, length control and training stability
- `03-machine-translation-fundamentals.md` — Machine translation fundamentals: parallel data, back-translation and domain adaptation
- `04-abstractive-and-extractive-summarization-compared.md` — Abstractive and extractive summarization compared
- `05-constrained-and-controlled-generation.md` — Constrained and controlled generation: lexical constraints and length control in beam search
- `06-automatic-metrics.md` — Automatic metrics: BLEU, chrF, ROUGE, BERTScore and COMET with their blind spots
- `07-faithfulness-and-hallucination-in-summaries.md` — Faithfulness and hallucination in summaries: detection and measurement
- `08-human-evaluation-design.md` — Human evaluation design: rating protocols and agreement

**Hands-on projects**

- **Project 1: fine tune a summarizer and audit faithfulness**  
  - Data: CNN/DailyMail or XSum, and SAMSum for dialogue  
  - Task: Fine-tune a seq2seq summarizer, evaluate with ROUGE and BERTScore and audit faithfulness on a hand-labeled sample.  
  - Deliverables: Model, metric table and faithfulness audit.  
  - Pass gate: Audit sample of at least 100 summaries with stated criteria.
- **Project 2: domain adapted translation system**  
  - Data: A public parallel corpus plus a small in-domain set, for example WMT data plus a domain test set  
  - Task: Adapt a translation model with fine-tuning and back-translation; compare with the base model on in-domain data.  
  - Deliverables: Adaptation experiments with BLEU, chrF and COMET.  
  - Pass gate: Test data excluded from every training and back-translation step.
- **Project 3: metric vs human judgement study**  
  - Data: Outputs from three systems on a small test set  
  - Task: Collect human rankings on a sample and compute correlation between automatic metrics and human judgement.  
  - Deliverables: Correlation analysis and recommended metric.  
  - Pass gate: Raters follow a written protocol and agreement is reported.

### 10 — Multilingual and Indic Language NLP

**Outcome:** Build NLP systems for Indian languages and code-mixed text, where tokenization, scripts and data scarcity change the engineering.

**Lessons**

- `01-indian-language-landscape.md` — Indian language landscape: scripts, morphology and resource availability
- `02-tokenization-for-indic-scripts.md` — Tokenization for Indic scripts: subword fragmentation and its cost
- `03-normalization-and-transliteration.md` — Normalization and transliteration: romanized text and script conversion
- `04-code-mixed-text-such-as-hinglish.md` — Code-mixed text such as Hinglish: challenges and datasets
- `05-multilingual-encoders.md` — Multilingual encoders: XLM-R, mBERT, MuRIL and IndicBERT compared
- `06-cross-lingual-transfer.md` — Cross-lingual transfer: zero-shot transfer and translate-train and translate-test
- `07-indic-translation.md` — Indic translation: IndicTrans2 and the Samanantar parallel corpus
- `08-evaluating-across-languages.md` — Evaluating across languages: IndicGLUE, FLORES-style benchmarks and fairness across languages

**Hands-on projects**

- **Project 1: multilingual classification and transfer study**  
  - Data: An Indic text classification benchmark such as IndicGLUE tasks (check licenses)  
  - Task: Compare multilingual encoders in monolingual, zero-shot cross-lingual and translate-train settings.  
  - Deliverables: Per-language results and transfer gaps.  
  - Pass gate: Per-language results reported, not only averages.
- **Project 2: tokenizer fragmentation audit**  
  - Data: Sample text in Hindi, Bengali, Tamil and English  
  - Task: Measure tokens-per-word and cost across several tokenizers and relate fragmentation to downstream accuracy.  
  - Deliverables: Fragmentation table and accuracy relation.  
  - Pass gate: Same sampled sentences used across tokenizers.
- **Project 3: hinglish sentiment system**  
  - Data: A public code-mixed sentiment dataset  
  - Task: Build a classifier handling romanized Hindi and mixed script; evaluate robustness to spelling variants.  
  - Deliverables: Model and spelling-variation robustness tests.  
  - Pass gate: Test set includes adversarial spelling variants.

### 11 — Applied NLP Systems

**Outcome:** Assemble NLP models into dependable applications for moderation, redaction, topic discovery and document processing.

**Lessons**

- `01-text-classification-at-scale.md` — Text classification at scale: throughput, batching and cost per document
- `02-sentiment-and-aspect-based-analysis.md` — Sentiment and aspect-based analysis
- `03-content-moderation.md` — Content moderation: toxicity detection, label ambiguity and bias in annotations
- `04-pii-detection-and-redaction.md` — PII detection and redaction: rules, models and recall-first evaluation
- `05-topic-discovery.md` — Topic discovery: BERTopic and clustering embeddings with evaluation
- `06-document-processing-pipelines.md` — Document processing pipelines: language identification, cleaning and routing
- `07-human-review-workflows-and-active-learning-for-text.md` — Human review workflows and active learning for text
- `08-nlp-error-monitoring-in-production.md` — NLP error monitoring in production: drift in vocabulary and label distribution

**Hands-on projects**

- **Project 1: pii redaction pipeline**  
  - Data: A public dataset with annotated PII or synthetic PII injected into public text  
  - Task: Build a hybrid rule-plus-model redactor and evaluate recall by entity type.  
  - Deliverables: Pipeline and recall-first evaluation.  
  - Pass gate: Recall on each PII class reported with a confidence interval.
- **Project 2: toxicity moderation with bias audit**  
  - Data: Jigsaw toxicity data (check access terms) or another public moderation set  
  - Task: Train a classifier and audit false-positive rates across identity-term subgroups.  
  - Deliverables: Model and subgroup error analysis.  
  - Pass gate: Subgroup metrics reported with sample sizes.
- **Project 3: topic discovery and evaluation**  
  - Data: A public news or review corpus  
  - Task: Compare BERTopic against classical topic models with coherence and human labeling checks.  
  - Deliverables: Topic comparison and a human-interpretability check.  
  - Pass gate: Human check on a sample of topics, not coherence alone.

### 12 — Modern Vision Backbones and Training Recipes

**Outcome:** Choose, train and evaluate modern vision backbones with the timm ecosystem. CNN basics, residual networks and transfer learning are covered in Stage 5C; the Vision Transformer introduction is in Stage 5C.

**Lessons**

- `01-backbone-landscape.md` — Backbone landscape: ConvNeXt, EfficientNet, Swin and ViT variants compared
- `02-data-efficient-transformers.md` — Data-efficient transformers: DeiT-style distillation tokens and training tricks
- `03-using-timm.md` — Using timm: model zoo, feature extraction and reproducing published results
- `04-augmentation-policies.md` — Augmentation policies: RandAugment, AutoAugment and test-time augmentation
- `05-resolution-and-aspect-ratio.md` — Resolution and aspect ratio: training and testing resolution effects
- `06-fine-grained-recognition.md` — Fine-grained recognition: attention to parts and high-resolution crops
- `07-ensembling-and-calibration-for-image-classifiers.md` — Ensembling and calibration for image classifiers
- `08-choosing-a-backbone.md` — Choosing a backbone: accuracy, latency, memory and licensing trade-offs

**Hands-on projects**

- **Project 1: backbone selection benchmark**  
  - Data: Oxford-IIIT Pets, Food-101 and a custom small dataset  
  - Task: Fine-tune five backbones under identical budgets; report accuracy, latency and memory.  
  - Deliverables: Pareto plot and selection guide.  
  - Pass gate: Latency measured on stated hardware at several batch sizes.
- **Project 2: augmentation policy study**  
  - Data: CIFAR-100 and Oxford-IIIT Pets  
  - Task: Compare none, standard, RandAugment, CutMix and test-time augmentation with repeated seeds.  
  - Deliverables: Ablation table with confidence intervals.  
  - Pass gate: At least 3 seeds per setting.
- **Project 3: fine grained recognition project**  
  - Data: CUB-200 or Stanford Cars  
  - Task: Reach a target accuracy with resolution scaling and part-aware cropping; document the gain of each step.  
  - Deliverables: Training recipe and ablation.  
  - Pass gate: Each step justified by a measured gain.

### 13 — Advanced Detection Segmentation and Tracking

**Outcome:** Go beyond the detection and segmentation essentials of Stage 5C: modern detectors, promptable segmentation, open-vocabulary models, tracking and pose.

**Lessons**

- `01-real-time-detectors.md` — Real-time detectors: anchor-free YOLO-family designs and training pipelines
- `02-transformer-detectors.md` — Transformer detectors: DETR and RT-DETR
- `03-instance-and-panoptic-segmentation.md` — Instance and panoptic segmentation
- `04-promptable-segmentation.md` — Promptable segmentation: Segment Anything and SAM 2
- `05-open-vocabulary-detection.md` — Open-vocabulary detection: OWL-ViT and Grounding DINO
- `06-multi-object-tracking.md` — Multi-object tracking: SORT-style association and ByteTrack
- `07-pose-estimation-and-keypoints.md` — Pose estimation and keypoints
- `08-detection-error-analysis.md` — Detection error analysis: localization vs classification vs background errors with TIDE-style breakdowns
- `09-small-object-and-crowded-scene-detection.md` — Small-object and crowded-scene detection

**Hands-on projects**

- **Project 1: detector comparison on custom data**  
  - Data: COCO subset plus a custom dataset you label  
  - Task: Train a YOLO-family model and an RT-DETR model; compare accuracy, speed and error types.  
  - Deliverables: Model comparison and TIDE-style error breakdown.  
  - Pass gate: Labeling guidelines and split rules documented.
- **Project 2: sam assisted labeling pipeline**  
  - Data: A new image set to segment  
  - Task: Use SAM prompts to speed up mask labeling, measure labeling time and mask quality against manual labels and train a segmentation model.  
  - Deliverables: Time-and-quality comparison and trained model.  
  - Pass gate: Quality measured by IoU against a manually labeled subset.
- **Project 3: multi object tracking system**  
  - Data: MOT17 or a video you record with consent  
  - Task: Combine a detector with ByteTrack and evaluate with MOTA and IDF1.  
  - Deliverables: Tracker and ID-switch analysis.  
  - Pass gate: Detector and tracker contributions evaluated separately.

### 14 — Video and Temporal Visual Understanding

**Outcome:** Model motion and time in video: classification, localization and efficient inference.

**Lessons**

- `01-video-data-fundamentals.md` — Video data fundamentals: decoding, frame sampling and codecs
- `02-two-stream-and-3d-convolution-models.md` — Two-stream and 3D convolution models: I3D and SlowFast
- `03-video-transformers.md` — Video transformers: TimeSformer and VideoMAE
- `04-optical-flow-and-motion-cues.md` — Optical flow and motion cues
- `05-temporal-action-localization.md` — Temporal action localization
- `06-efficient-video-inference.md` — Efficient video inference: frame selection and clip aggregation
- `07-video-self-supervision-and-pretraining.md` — Video self-supervision and pretraining
- `08-evaluating-video-models.md` — Evaluating video models: clip vs video-level accuracy and dataset bias towards scenes

**Hands-on projects**

- **Project 1: action recognition benchmark**  
  - Data: UCF101 or HMDB51 subset  
  - Task: Compare an I3D-style model, a SlowFast model and a video transformer on accuracy and compute.  
  - Deliverables: Accuracy-compute table.  
  - Pass gate: Clip-level and video-level accuracy reported separately.
- **Project 2: frame sampling efficiency study**  
  - Data: A video classification dataset  
  - Task: Study accuracy as a function of frames per clip, resolution and sampling strategy.  
  - Deliverables: Efficiency frontier.  
  - Pass gate: Throughput measured on stated hardware.
- **Project 3: scene bias diagnostic**  
  - Data: A video action dataset  
  - Task: Test whether models rely on scene context by evaluating on masked or shuffled-frame inputs.  
  - Deliverables: Bias diagnostic report.  
  - Pass gate: Control inputs described and applied identically to all models.

### 15 — OCR Document and Visual Text Understanding

**Outcome:** Read text from images and understand document layout, including Indic scripts.

**Lessons**

- `01-text-detection.md` — Text detection: scene text and document text detectors
- `02-text-recognition.md` — Text recognition: CRNN with CTC and attention-based recognizers
- `03-transformer-ocr.md` — Transformer OCR: TrOCR and end-to-end OCR-free models such as Donut
- `04-layout-analysis.md` — Layout analysis: LayoutLMv3-style models and layout-aware extraction
- `05-table-detection-and-structure-recognition.md` — Table detection and structure recognition
- `06-handwriting-recognition.md` — Handwriting recognition
- `07-indic-script-ocr.md` — Indic-script OCR: script-specific challenges and datasets
- `08-ocr-evaluation.md` — OCR evaluation: character and word error rate, field-level accuracy and downstream impact

**Hands-on projects**

- **Project 1: receipt and invoice extraction**  
  - Data: SROIE receipts and FUNSD forms  
  - Task: Compare an OCR plus layout model pipeline with an OCR-free model for field extraction.  
  - Deliverables: Pipeline comparison with field-level metrics.  
  - Pass gate: Errors attributed to OCR vs extraction stage.
- **Project 2: crnn ctc recognizer from scratch**  
  - Data: Synthetic text-line images plus IAM handwriting if access is granted  
  - Task: Build a CRNN with CTC loss and decoding, evaluating character error rate.  
  - Deliverables: Implementation and error analysis.  
  - Pass gate: CTC decoding tested against a reference decoder on a small example.
- **Project 3: table extraction pipeline**  
  - Data: PubLayNet or PubTables-1M subset  
  - Task: Detect tables and recover structure; evaluate cell-level accuracy.  
  - Deliverables: Pipeline and failure catalog.  
  - Pass gate: Metrics defined at cell level, not table level only.

### 16 — Vision Data Pipelines and Annotation Engineering

**Outcome:** Build the vision-specific data plumbing that production projects need. General data-centric AI and synthetic data are covered later in G13.

**Lessons**

- `01-annotation-formats.md` — Annotation formats: COCO, YOLO and Pascal VOC and conversion pitfalls
- `02-annotation-tooling-and-guidelines-for-boxes-masks-and-keypoints.md` — Annotation tooling and guidelines for boxes, masks and keypoints
- `03-label-quality-in-vision.md` — Label quality in vision: box tightness, missing objects and class confusion audits
- `04-augmentation-libraries.md` — Augmentation libraries: Albumentations and Kornia, and geometric consistency of labels
- `05-fast-data-loading.md` — Fast data loading: DALI, image decoding and cache design
- `06-image-quality-issues.md` — Image quality issues: blur, exposure, compression and corrupted files
- `07-privacy-in-vision-data.md` — Privacy in vision data: faces, license plates and consent
- `08-dataset-versioning-and-splits-for-images.md` — Dataset versioning and splits for images: leakage from near-duplicates and video frames

**Hands-on projects**

- **Project 1: annotation format converter and validator**  
  - Data: COCO and a YOLO-format dataset  
  - Task: Write converters and validators that catch malformed boxes, empty masks and class-id mismatches.  
  - Deliverables: Tested converter library.  
  - Pass gate: Round-trip conversion preserves every annotation in tests.
- **Project 2: near duplicate leakage audit**  
  - Data: A public image dataset and a video-frame dataset  
  - Task: Find near-duplicates across train and test splits and measure how much they inflate accuracy.  
  - Deliverables: Leakage report with inflated vs clean metrics.  
  - Pass gate: Duplicate-detection method validated on planted duplicates.
- **Project 3: dataloader throughput optimization**  
  - Data: Large image dataset on local or object storage  
  - Task: Optimize decoding, caching and augmentation to saturate the GPU and report utilization before and after.  
  - Deliverables: Benchmark report.  
  - Pass gate: GPU utilization measured, not assumed.

### 17 — Audio Signal Foundations and Representations

**Outcome:** Turn sound into model inputs correctly. The Fourier transform math is covered in Stage 4C and the introductory audio-model lesson in Stage 5C; this module applies them in practice.

**Lessons**

- `01-digital-audio.md` — Digital audio: sampling, bit depth, resampling and aliasing
- `02-spectrograms.md` — Spectrograms: STFT, window choice and time-frequency trade-offs
- `03-mel-scales-and-features.md` — Mel scales and features: log-mel spectrograms and MFCCs
- `04-audio-tooling.md` — Audio tooling: torchaudio, librosa and loading pitfalls
- `05-audio-augmentation.md` — Audio augmentation: SpecAugment, noise mixing, room impulse responses and speed perturbation
- `06-learned-audio-representations.md` — Learned audio representations: wav2vec 2.0 and HuBERT overview
- `07-audio-datasets-and-licensing.md` — Audio datasets and licensing: LibriSpeech, Common Voice, AudioSet and VoxCeleb
- `08-common-audio-bugs.md` — Common audio bugs: sample-rate mismatch, clipping, silence and channel handling

**Hands-on projects**

- **Project 1: feature extraction from first principles**  
  - Data: A handful of recordings you capture plus LibriSpeech samples  
  - Task: Implement STFT and log-mel features in NumPy and match torchaudio outputs.  
  - Deliverables: Tested implementation and comparison plots.  
  - Pass gate: Outputs match torchaudio within a stated tolerance.
- **Project 2: augmentation ablation for audio classification**  
  - Data: Speech Commands or ESC-50  
  - Task: Measure the effect of each augmentation on accuracy and robustness to noise.  
  - Deliverables: Ablation table.  
  - Pass gate: Multiple seeds and a noisy test condition.
- **Project 3: audio bug hunt**  
  - Data: A deliberately broken audio pipeline you build  
  - Task: Inject five bugs (sample rate, clipping, channel order, normalization, leakage) and write tests that catch them.  
  - Deliverables: Bug catalog and automated checks.  
  - Pass gate: Every injected bug is caught by a test.

### 18 — Audio Classification Enhancement and Source Separation

**Outcome:** Classify sounds, detect events and clean or separate audio.

**Lessons**

- `01-audio-classification-with-cnns-on-spectrograms.md` — Audio classification with CNNs on spectrograms
- `02-audio-transformers-and-pretrained-audio-models.md` — Audio transformers and pretrained audio models: AST and PANNs
- `03-sound-event-detection.md` — Sound event detection: strong vs weak labels and event-based metrics
- `04-keyword-spotting.md` — Keyword spotting: small-footprint models and false-accept vs false-reject trade-offs
- `05-speech-enhancement-and-denoising.md` — Speech enhancement and denoising: masking and waveform models
- `06-source-separation.md` — Source separation: Demucs and mask-based separation, with SDR metrics
- `07-music-information-retrieval-basics.md` — Music information retrieval basics: tagging, beat tracking and transcription overview
- `08-audio-quality-evaluation.md` — Audio quality evaluation: PESQ, STOI and subjective tests

**Hands-on projects**

- **Project 1: urban sound event detection**  
  - Data: UrbanSound8K and ESC-50  
  - Task: Compare a CNN, AST and a PANNs model; evaluate with the dataset's fold protocol.  
  - Deliverables: Model comparison across folds.  
  - Pass gate: Predefined folds respected to avoid leakage.
- **Project 2: keyword spotting system**  
  - Data: Google Speech Commands  
  - Task: Build a small keyword-spotting model and tune the false-accept rate for a stated use.  
  - Deliverables: Model and operating-point analysis.  
  - Pass gate: False-accept rate measured on background-only audio.
- **Project 3: speech enhancement evaluation**  
  - Data: DNS Challenge data or LibriSpeech plus noise  
  - Task: Train or apply a denoiser and evaluate with objective metrics and a small listening test.  
  - Deliverables: Metrics and listening-test results.  
  - Pass gate: Objective and subjective results compared.

### 19 — Automatic Speech Recognition

**Outcome:** Build, adapt and evaluate speech recognizers including for Indian languages. The Whisper-class models named in Stage 5C are used here as engineering tools.

**Lessons**

- `01-asr-problem-and-history.md` — ASR problem and history: acoustic models, language models and the move to end-to-end
- `02-ctc.md` — CTC: alignment-free training and decoding
- `03-rnn-transducer-and-attention-encoder-decoder-models.md` — RNN-Transducer and attention encoder-decoder models
- `04-self-supervised-speech-models.md` — Self-supervised speech models: wav2vec 2.0 and HuBERT fine-tuning
- `05-whisper.md` — Whisper: architecture, fine-tuning and practical limits
- `06-language-model-fusion-and-decoding-with-beam-search.md` — Language model fusion and decoding with beam search
- `07-streaming-asr.md` — Streaming ASR: chunking, latency and endpointing
- `08-speaker-diarization-and-punctuation-restoration.md` — Speaker diarization and punctuation restoration
- `09-evaluating-asr.md` — Evaluating ASR: WER, CER, per-accent breakdowns and normalization effects
- `10-indic-asr.md` — Indic ASR: datasets and models such as those from AI4Bharat

**Hands-on projects**

- **Project 1: finetune wav2vec2 and whisper**  
  - Data: Common Voice or LibriSpeech subset, plus an Indic language set such as Common Voice Hindi  
  - Task: Fine-tune wav2vec 2.0 with CTC and a Whisper model; compare WER, CER and compute.  
  - Deliverables: Fine-tuned models and evaluation.  
  - Pass gate: Text normalization applied identically before scoring.
- **Project 2: streaming asr latency study**  
  - Data: A streaming-capable model and test audio  
  - Task: Measure the latency-accuracy trade-off across chunk sizes.  
  - Deliverables: Latency-WER curve.  
  - Pass gate: Latency measured end to end.
- **Project 3: accent and noise robustness audit**  
  - Data: Common Voice with accent metadata and added noise  
  - Task: Evaluate WER by accent group and noise level and propose a mitigation.  
  - Deliverables: Subgroup WER report.  
  - Pass gate: Subgroup sample sizes reported.

### 20 — Text to Speech Voice and Speaker Systems

**Outcome:** Build and evaluate speech synthesis and speaker models, with the ethics of synthetic voice built in.

**Lessons**

- `01-tts-pipeline.md` — TTS pipeline: text frontend, acoustic model and vocoder
- `02-acoustic-models.md` — Acoustic models: Tacotron 2 and FastSpeech 2
- `03-neural-vocoders.md` — Neural vocoders: HiFi-GAN and neural audio codecs
- `04-end-to-end-tts.md` — End-to-end TTS: VITS and its successors
- `05-multi-speaker-and-expressive-speech.md` — Multi-speaker and expressive speech
- `06-speaker-verification.md` — Speaker verification: x-vectors and ECAPA-TDNN with equal error rate
- `07-voice-conversion-and-its-risks.md` — Voice conversion and its risks
- `08-evaluating-tts.md` — Evaluating TTS: MOS, intelligibility and speaker similarity
- `09-synthetic-speech-detection-and-consent-policy.md` — Synthetic speech detection and consent policy

**Hands-on projects**

- **Project 1: single speaker tts system**  
  - Data: LJSpeech or LibriTTS subset  
  - Task: Train or fine-tune an acoustic model and vocoder and evaluate intelligibility with ASR-based word error rate and a small MOS test.  
  - Deliverables: TTS system and evaluation.  
  - Pass gate: Listening test uses blind and randomized samples.
- **Project 2: speaker verification system**  
  - Data: VoxCeleb subset or VCTK (check licenses)  
  - Task: Train an embedding model and evaluate equal error rate on unseen speakers.  
  - Deliverables: Model and EER analysis.  
  - Pass gate: Evaluation speakers disjoint from training speakers.
- **Project 3: synthetic speech detector and consent policy**  
  - Data: Real speech plus speech synthesized by models you train  
  - Task: Build a detector, test how well it generalizes to an unseen synthesizer and write a consent and disclosure policy.  
  - Deliverables: Detector, generalization results and policy document.  
  - Pass gate: Generalization to unseen synthesizers reported honestly.

### 21 — Multimodal Alignment and Fusion

**Outcome:** Combine modalities: align embedding spaces and fuse inputs, including when a modality is missing. CLIP and vision-language models are introduced in Stage 5C.

**Lessons**

- `01-fusion-strategies.md` — Fusion strategies: early, late and cross-attention fusion
- `02-contrastive-alignment.md` — Contrastive alignment: training a small CLIP-style model and SigLIP-style loss
- `03-extending-alignment.md` — Extending alignment: CLAP for audio-text and ImageBind-style binding
- `04-missing-and-noisy-modalities.md` — Missing and noisy modalities: modality dropout and robustness
- `05-modality-imbalance.md` — Modality imbalance: when one modality dominates training
- `06-multimodal-pretraining-objectives.md` — Multimodal pretraining objectives: matching, masked and generative
- `07-tabular-and-sensor-fusion-with-images-or-text.md` — Tabular and sensor fusion with images or text
- `08-evaluating-fusion.md` — Evaluating fusion: unimodal baselines, ablations and gain attribution

**Hands-on projects**

- **Project 1: small clip from scratch**  
  - Data: Flickr30k or COCO Captions subset  
  - Task: Train a small image-text contrastive model and evaluate retrieval Recall@K and zero-shot classification.  
  - Deliverables: Model, evaluation and ablation of temperature and batch size.  
  - Pass gate: Compared against a pretrained CLIP baseline on the same protocol.
- **Project 2: missing modality robustness study**  
  - Data: A multimodal classification dataset such as image plus text product data  
  - Task: Train with and without modality dropout and test with each modality removed.  
  - Deliverables: Robustness table.  
  - Pass gate: Unimodal baselines included.
- **Project 3: image plus tabular fusion**  
  - Data: A dataset with images and structured attributes, for example real-estate or product listings  
  - Task: Compare early, late and cross-attention fusion against image-only and tabular-only models, including the G1 GBDT baseline.  
  - Deliverables: Fusion comparison with confidence intervals.  
  - Pass gate: Gain over the best unimodal model quantified.

### 22 — Vision Language Tasks and Models

**Outcome:** Caption, answer questions about and ground language in images. Large language model engineering and parameter-efficient fine-tuning are covered in G3; here vision-language models are used and evaluated.

**Lessons**

- `01-image-captioning.md` — Image captioning: encoder-decoder and prefix-based models, with CIDEr and SPICE
- `02-visual-question-answering.md` — Visual question answering: VQAv2 and its language-prior bias
- `03-visual-grounding-and-referring-expressions.md` — Visual grounding and referring expressions
- `04-image-text-retrieval.md` — Image-text retrieval: evaluation and hard negatives
- `05-vision-language-model-architectures.md` — Vision-language model architectures: BLIP-2 and LLaVA-style connectors
- `06-adapting-a-vision-language-model-to-a-task-with-a-small-trainable-adapter.md` — Adapting a vision-language model to a task with a small trainable adapter
- `07-hallucination-in-vision-language-models.md` — Hallucination in vision-language models: measurement with POPE-style probes
- `08-document-and-chart-question-answering.md` — Document and chart question answering

**Hands-on projects**

- **Project 1: vqa with bias analysis**  
  - Data: VQAv2 subset  
  - Task: Compare a vision-language model with a language-only baseline to measure language-prior bias.  
  - Deliverables: Accuracy breakdown by question type.  
  - Pass gate: Language-only baseline included.
- **Project 2: domain specific captioning**  
  - Data: COCO Captions plus a small domain set you caption  
  - Task: Adapt a captioning model to the domain and evaluate with automatic metrics and human review.  
  - Deliverables: Adapted model and evaluation.  
  - Pass gate: Human review protocol written and applied.
- **Project 3: vlm hallucination probe**  
  - Data: Images with known object lists such as COCO  
  - Task: Measure object-hallucination rates of two vision-language models with POPE-style yes/no probes.  
  - Deliverables: Hallucination-rate comparison.  
  - Pass gate: Probe construction documented and balanced.

### 23 — Audio Video and Cross Modal Systems

**Outcome:** Build systems that join sound, video and text.

**Lessons**

- `01-audio-captioning-and-audio-text-retrieval.md` — Audio captioning and audio-text retrieval
- `02-video-text-retrieval-and-video-captioning.md` — Video-text retrieval and video captioning
- `03-video-question-answering.md` — Video question answering
- `04-audio-visual-speech-recognition-and-active-speaker-detection.md` — Audio-visual speech recognition and active speaker detection
- `05-speech-translation.md` — Speech translation: cascaded vs end-to-end speech-to-text translation
- `06-multimodal-emotion-and-sentiment-analysis.md` — Multimodal emotion and sentiment analysis
- `07-time-alignment-across-modalities.md` — Time alignment across modalities: synchronization and drift
- `08-cost-of-multimodal-inference.md` — Cost of multimodal inference: batching, sampling and caching

**Hands-on projects**

- **Project 1: audio text retrieval system**  
  - Data: AudioCaps and Clotho  
  - Task: Train or adapt an audio-text retrieval model and evaluate Recall@K.  
  - Deliverables: Model and retrieval evaluation.  
  - Pass gate: Splits keep clips from the same source video in one split.
- **Project 2: cascaded vs end to end speech translation**  
  - Data: FLEURS or CoVoST speech translation data  
  - Task: Compare an ASR-plus-translation cascade with an end-to-end model on quality and latency.  
  - Deliverables: Comparison with error propagation analysis.  
  - Pass gate: Quality and latency reported together.
- **Project 3: video text retrieval prototype**  
  - Data: MSR-VTT subset  
  - Task: Build a video-text retrieval model and study how the number of sampled frames changes accuracy and cost.  
  - Deliverables: Prototype and cost-accuracy curve.  
  - Pass gate: Frame-sampling settings fixed before evaluating.

### 24 — Multimodal Evaluation Robustness and Responsible Use

**Outcome:** Evaluate multimodal systems rigorously and know where they fail.

**Lessons**

- `01-multimodal-benchmark-landscape-and-contamination-risks.md` — Multimodal benchmark landscape and contamination risks
- `02-modality-bias-and-shortcut-detection.md` — Modality bias and shortcut detection
- `03-robustness.md` — Robustness: missing, misaligned and adversarial modalities
- `04-bias-and-fairness-across-demographic-groups-in-vision-and-speech-models.md` — Bias and fairness across demographic groups in vision and speech models
- `05-privacy-and-consent-for-faces-voices-and-documents.md` — Privacy and consent for faces, voices and documents
- `06-deepfake-and-synthetic-media-risks-and-detection-limits.md` — Deepfake and synthetic-media risks and detection limits
- `07-evaluation-reporting.md` — Evaluation reporting: failure catalogs, slices and uncertainty
- `08-deployment-checklist-for-multimodal-products.md` — Deployment checklist for multimodal products

**Hands-on projects**

- **Project 1: modality ablation and bias audit**  
  - Data: A multimodal model from earlier modules  
  - Task: Ablate each modality and audit performance across subgroups for fairness and shortcut use.  
  - Deliverables: Audit report.  
  - Pass gate: Subgroup sizes and confidence intervals reported.
- **Project 2: benchmark contamination check**  
  - Data: A public benchmark and a pretrained model's documented training data  
  - Task: Check for overlap between benchmark items and known training sources and estimate the effect on scores.  
  - Deliverables: Contamination analysis.  
  - Pass gate: Method and its limits stated.
- **Project 3: multimodal failure catalog**  
  - Data: Outputs from your earlier multimodal projects  
  - Task: Categorize 200 failures by cause and propose mitigations.  
  - Deliverables: Failure taxonomy with examples.  
  - Pass gate: Categories defined before labeling and applied by two reviewers on a subset.

### 25 — G2 Capstones

**Outcome:** integrate each modality track and the multimodal track in assessed, portfolio-quality work.

- **Capstone 1: modality specialist project nlp** (uses Modules 06 to 11)  
  Deliver an NLP system for an Indian-language or domain use case with annotation, a trained model, evaluation, an error analysis and a monitoring plan.
- **Capstone 2: modality specialist project vision** (uses Modules 12 to 16)  
  Deliver a vision system with a custom labeled dataset, detector or segmenter, tracking or OCR as relevant, and a documented failure analysis.
- **Capstone 3: modality specialist project speech** (uses Modules 17 to 20)  
  Deliver a speech system, for example Indic ASR with a TTS demo, with subgroup evaluation and a consent and disclosure policy.
- **Capstone 4: multimodal system project** (uses Modules 21 to 24)  
  Deliver a multimodal application combining at least two modalities with unimodal baselines, ablations, robustness tests and a responsible-use review.
- **Capstone 5: g2 readiness assessment** (uses All modules)  
  Written and practical assessment against the G2 completion gate.

## G2 completion gate

- Every module project has a written report with seed-variance or confidence intervals and a stated limitation.
- All results reproduce from a lockfile, config files and logged seeds, with hardware and library versions recorded.
- Every dataset used has its licence and access conditions recorded in the register before use.
- Subgroup, per-language or per-accent results are reported wherever the modality has them, not only averages.
- At least one negative or inconclusive result per modality is reported honestly.
- The four specialist capstones are complete and the readiness assessment is passed.

## Audit and verification

**What was checked and the result**

- Structure: 24 specialist modules each have 6 to 12 lessons and at least one project; the tree contains 337 files and 51 folders, and these counts equal the counts computed from the curriculum data.
- Overlap with the Roadmap: all 201 lesson file names were compared against every lesson file name in `Roadmap.md`. Exact matches: 0. Near matches (similarity 0.80 or higher): 6 — `encoder-pretraining-objectives` vs Roadmap `pretraining-objectives` (0.85); `training-sentence-embeddings` vs Roadmap `sentence-embeddings` (0.81); `normalization-and-transliteration` vs Roadmap `normalization-and-denormalization` (0.82); `video-transformers` vs Roadmap `vision-transformers` (0.86); `text-detection` vs Roadmap `object-detection` (0.8); `multimodal-pretraining-objectives` vs Roadmap `pretraining-objectives` (0.8). Reviewed manually: encoder-pretraining-objectives and sentence-embedding training deepen Stage 5C introductions (masked, replaced-token and contrastive objectives for encoders, versus the generic pretraining and sentence-embedding lessons); video-transformers, text-detection, normalization-and-transliteration and multimodal-pretraining-objectives share words with Roadmap lessons but cover different topics.
- Structural problems found by the build script: 0.
- Topic-level overlap check: the Roadmap text was searched for BERT, NER, Whisper, wav2vec, OCR, YOLO, DETR, Segment Anything, Grad-CAM, SimCLR, domain adaptation, few-shot, continual learning, spectrogram, BLEU, ROUGE, text-to-speech, speaker, diarization, captioning and VQA; none appear as lessons, so G2 teaches them for the first time. The Roadmap does contain the Fourier transform (Stage 4C), CLIP, audio and speech model introductions and diffusion in practice (Stage 5C), which G2 references and extends.
- Verified by web search on the build date (2026-10-26): GLiNER is a NAACL 2024 generalist NER model; SAM 2 (Ravi et al.) handles images and video, with SAM 2.1 checkpoints released in September 2024; POPE is an EMNLP 2023 object-hallucination benchmark and a later effort (RePOPE) found annotation errors in it; IndicTrans2 supports the 22 scheduled Indic languages and Samanantar is an English to Indic parallel corpus; IndicGLUE was released with IndicBERT; Vistaar is AI4Bharat's Indic ASR benchmark and Kathbath and IndicVoices are AI4Bharat speech corpora.
- Reported by search but not independently confirmed: Samanantar's size is quoted as 46.9 million pairs in the paper and 49.7 million on the project site, so confirm the version; a successor to SAM 2 (SAM 3) appears to exist, and the lessons should be updated if it is adopted.
- Not verified: MuRIL details beyond its title and authors; model, library and benchmark versions, which change quickly; and dataset availability. Several datasets (OntoNotes, IAM, VoxCeleb, ImageNet, Cityscapes, Jigsaw, AudioSet, LRS3-type data) have registration, licence or terms-of-use limits, so each must be checked and recorded in the register before use.
- Not verified by execution: no code in this plan has been run. Project pass gates are acceptance criteria to be met when the projects are built.
- Repository safety: this build created only this file; no existing file or folder was created, changed or deleted by it.
