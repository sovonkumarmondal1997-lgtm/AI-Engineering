# Efficient and Scalable Systems — ML Specialization Roadmap

**Group 10 (G10)** of the specialization that follows Stage 5D of the [Roadmap](./Roadmap.md). It covers original categories **25 Edge and Embedded Machine Learning, 26 ML Performance and Inference Optimization and 27 Distributed and Large-Scale Machine Learning**. The group's defining question is: *how do I make models fast, small and big?* It follows G1 to G9: [`01_Classical and Applied ML.md`](./01_Classical%20and%20Applied%20ML.md), [`02_Deep Learning by Modality.md`](./02_Deep%20Learning%20by%20Modality.md), [`03_Generative and Foundation Models.md`](./03_Generative%20and%20Foundation%20Models.md), [`04_Agents and Sequential Decisions.md`](./04_Agents%20and%20Sequential%20Decisions.md), [`05_Time and Anomaly Modeling.md`](./05_Time%20and%20Anomaly%20Modeling.md), [`06_Personalization Search and Matching.md`](./06_Personalization%20Search%20and%20Matching.md), [`07_Statistical Reasoning.md`](./07_Statistical%20Reasoning.md), [`08_Graphs and Optimization.md`](./08_Graphs%20and%20Optimization.md), [`09_Industry Domain ML.md`](./09_Industry%20Domain%20ML.md).

## G10 summary

| Item | Count |
|---|---|
| Modules (including overview and capstones) | 16 |
| Lesson files | 133 |
| Hands-on project files (module projects, overview project and capstones) | 48 |
| Folders inside the G10 tree | 31 |
| Files inside the G10 tree | 219 |

| Original category | Modules |
|---|---|
| 26 ML Performance and Inference Optimization | 01 to 04 |
| 25 Edge and Embedded Machine Learning | 05 to 08 |
| 27 Distributed and Large-Scale Machine Learning | 09 to 13 |
| Shared measurement and planning for all three | 14 |

## Scope and how G10 avoids repeating the Roadmap

G10 starts where Stage 5C and Stage 5D stop. These are **already learned** and are only referenced, never retaught: the CPU, RAM, cache and GPU fundamentals and why GPUs matter for AI (Stage 0); mixed-precision training, gradient clipping and accumulation, activation checkpointing and the introductions to DDP and FSDP, efficient attention and FlashAttention as an idea, KV-cache and speculative-decoding intuition, and compute, FLOPs and memory accounting (Stage 5C); profiling inference bottlenecks, model export and ONNX, ONNX Runtime, TensorRT and torch.compile usage, quantization and pruning for non-LLM models, GPU inference and dynamic batching, prediction and feature caching, edge and on-device deployment basics, cost per prediction and autoscaling, and capacity planning (Stage 5D); GPU-enabled container images, model-serving frameworks (BentoML, TorchServe, Triton), serving on Kubernetes with KServe, load testing and cloud deployment of ML (Stage 5D); Kubernetes, FinOps, SRE and observability (Stage 2E); Spark, Dask and Polars (Stages 2B and 2C); external-memory and distributed boosting and GPU data science with RAPIDS (G1); hardware-aware neural architecture search (G1); basic vLLM configuration and the API-versus-self-hosting cost model (G3); approximate-nearest-neighbor indexes (G6); and RL actor-learner systems (G4).

**Boundaries with other groups** (so nothing overlaps): LLM post-training and PEFT belong to **G3**; privacy-preserving and federated training belongs to **G12**; MLOps platform design (registries, pipelines) belongs to **G11**; benchmark and evaluation-system design belongs to **G13**; industrial edge gateways for plant data are applied in **G9**.

| Roadmap topic already covered | Where G10 goes further |
|---|---|
| GPU basics (Stage 0), compute and memory accounting (5C) | Module 01: roofline modeling, memory hierarchy, numeric formats and measured-versus-predicted performance |
| torch.compile, ONNX Runtime and TensorRT usage (5D), FlashAttention idea (5C) | Module 02: CUDA and Triton kernels, fusion, compiler internals and kernel profiling |
| Quantization and pruning for non-LLM models (5D) | Module 03: GPTQ, AWQ, FP8, KV-cache quantization, 2:4 sparsity and distillation with honest quality checks |
| Dynamic batching and KV-cache intuition (5D, 5C), vLLM basics (G3) | Module 04: paged KV cache, continuous batching, prefix caching, speculative decoding in practice and serving under latency objectives |
| Edge deployment basics (5D) | Modules 05 to 07: full conversion and benchmarking, microcontrollers, and on-device language, vision and speech models |
| Release strategies and rollback (5D), Kubernetes (2E) | Module 08: over-the-air updates, device heterogeneity, signed delivery and edge drift monitoring |
| DDP and FSDP introductions (5C) | Module 09: collective communication, scaling efficiency, hang debugging, elastic training and checkpoints at scale |
| Architectures and MoE (5C, G3) | Module 10: tensor, pipeline, sequence and expert parallelism and configuration planning |
| Spark and Dask processing (2B, 2C), streaming-data design (2D) | Module 11: sharded, resumable, streaming training pipelines and input-bottleneck analysis |
| Distributed boosting (G1), RL systems (G4), Kubernetes (2E) | Module 12: Ray, schedulers, gang scheduling, multi-tenancy and preemptible capacity |
| Cloud cost controls and FinOps (5D, 2E) | Module 13: GPU cluster operations, utilization audits, cost per run, carbon and compute access in India |
| Load testing and capacity planning (5D) | Module 14: efficiency metrics, MLPerf rules, fair comparison, queueing models and regression tests |

## G10 — Efficient and Scalable Systems

**Defining question:** How do I make models fast, small and big?

```text
ML Specialization/
└── G10 — Efficient and Scalable Systems/
    ├── 00-G10-Overview/
    │   ├── Projects/
    │   │   ├── 01-g10-hardware-and-benchmark-harness-bootstrap.md
    │   │   └── README.md
    │   ├── 01-g10-scope-and-boundaries-with-stage-5c-5d-and-other-groups.md
    │   ├── 02-prerequisite-map-from-the-roadmap.md
    │   ├── 03-hardware-dataset-and-tooling-register.md
    │   ├── 04-benchmarking-and-reporting-standards.md
    │   ├── 05-completion-gate.md
    │   ├── README.md
    │   └── learning-plan.md
    ├── 01-Hardware-Performance-Modeling-for-ML/
    │   ├── Projects/
    │   │   ├── 01-roofline-measurement-and-prediction.md
    │   │   ├── 02-model-latency-estimator.md
    │   │   ├── 03-benchmarking-methodology-audit.md
    │   │   └── README.md
    │   ├── 01-the-roofline-model.md
    │   ├── 02-gpu-architecture-for-ml.md
    │   ├── 03-cpu-performance.md
    │   ├── 04-accelerator-families.md
    │   ├── 05-interconnects.md
    │   ├── 06-numeric-formats.md
    │   ├── 07-back-of-envelope-estimation.md
    │   ├── 08-benchmarking-method.md
    │   ├── 09-measuring-power-and-energy-per-inference.md
    │   └── README.md
    ├── 02-GPU-Kernels-and-ML-Compiler-Stacks/
    │   ├── Projects/
    │   │   ├── 01-triton-fused-kernels-with-benchmarks.md
    │   │   ├── 02-tiled-attention-kernel.md
    │   │   ├── 03-graph-break-and-compile-debugging-clinic.md
    │   │   └── README.md
    │   ├── 01-cuda-programming-model-for-ml-engineers.md
    │   ├── 02-kernel-optimization-patterns.md
    │   ├── 03-writing-kernels-in-triton.md
    │   ├── 04-operator-fusion.md
    │   ├── 05-implementing-a-flashattention-style-tiled-attention-kernel-and-verifying-it-against-a-reference.md
    │   ├── 06-how-torch-compile-works.md
    │   ├── 07-xla-and-jax-compilation.md
    │   ├── 08-compiler-infrastructure-overview.md
    │   ├── 09-kernel-level-profiling.md
    │   ├── 10-correctness-testing-for-custom-kernels.md
    │   └── README.md
    ├── 03-Quantization-Pruning-and-Distillation-in-Depth/
    │   ├── Projects/
    │   │   ├── 01-llm-quantization-quality-and-speed-matrix.md
    │   │   ├── 02-distillation-vs-training-small-from-scratch.md
    │   │   ├── 03-structured-sparsity-on-tensor-cores.md
    │   │   └── README.md
    │   ├── 01-post-training-quantization-vs-quantization-aware-training.md
    │   ├── 02-calibration-for-int8.md
    │   ├── 03-weight-only-quantization-for-language-models.md
    │   ├── 04-activation-quantization-and-outliers.md
    │   ├── 05-low-precision-floating-point.md
    │   ├── 06-practical-formats.md
    │   ├── 07-kv-cache-quantization-and-long-context-degradation.md
    │   ├── 08-evaluating-compressed-models.md
    │   ├── 09-pruning.md
    │   ├── 10-knowledge-distillation.md
    │   ├── 11-other-compression.md
    │   └── README.md
    ├── 04-LLM-Inference-Engines-and-Serving-Optimization/
    │   ├── Projects/
    │   │   ├── 01-llm-serving-benchmark-under-slo.md
    │   │   ├── 02-kv-cache-memory-budget-study.md
    │   │   ├── 03-speculative-decoding-gain-analysis.md
    │   │   └── README.md
    │   ├── 01-prefill-and-decode.md
    │   ├── 02-kv-cache-memory-management.md
    │   ├── 03-continuous-batching-and-chunked-prefill.md
    │   ├── 04-prefix-caching-and-prompt-reuse.md
    │   ├── 05-speculative-decoding-in-practice.md
    │   ├── 06-tensor-parallel-inference-and-disaggregating-prefill-from-decode.md
    │   ├── 07-long-context-serving.md
    │   ├── 08-multi-adapter-serving.md
    │   ├── 09-engines-compared.md
    │   ├── 10-serving-metrics.md
    │   ├── 11-capacity-planning-and-autoscaling-for-llm-replicas.md
    │   └── README.md
    ├── 05-Edge-and-On-Device-ML-Foundations/
    │   ├── Projects/
    │   │   ├── 01-convert-and-benchmark-across-runtimes.md
    │   │   ├── 02-thermal-throttling-study.md
    │   │   ├── 03-operator-gap-debugging.md
    │   │   └── README.md
    │   ├── 01-edge-constraints.md
    │   ├── 02-device-classes.md
    │   ├── 03-runtimes.md
    │   ├── 04-accelerators-on-devices.md
    │   ├── 05-conversion-pipelines.md
    │   ├── 06-efficient-architectures-for-the-edge.md
    │   ├── 07-on-device-benchmarking.md
    │   ├── 08-packaging-and-updating-models-inside-applications.md
    │   ├── 09-privacy-and-security-benefits-and-risks-of-on-device-inference.md
    │   └── README.md
    ├── 06-TinyML-and-Microcontroller-Machine-Learning/
    │   ├── Projects/
    │   │   ├── 01-keyword-spotting-on-a-microcontroller.md
    │   │   ├── 02-sensor-anomaly-detector-on-device.md
    │   │   ├── 03-memory-budget-planning-tool.md
    │   │   └── README.md
    │   ├── 01-microcontroller-constraints.md
    │   ├── 02-sensor-pipelines.md
    │   ├── 03-tensorflow-lite-for-microcontrollers-and-cmsis-nn.md
    │   ├── 04-integer-only-quantization-and-binary-or-very-low-bit-networks.md
    │   ├── 05-keyword-spotting-and-sensor-anomaly-detection-on-microcontrollers-using-models-from-g2-and-g5.md
    │   ├── 06-power-management.md
    │   ├── 07-firmware-integration.md
    │   ├── 08-hardware-in-the-loop-testing-and-field-validation.md
    │   ├── 09-benchmarks-and-platforms.md
    │   └── README.md
    ├── 07-On-Device-Language-Vision-and-Speech-Models/
    │   ├── Projects/
    │   │   ├── 01-on-device-assistant-feasibility-study.md
    │   │   ├── 02-edge-cloud-offloading-policy.md
    │   │   ├── 03-real-time-camera-pipeline.md
    │   │   └── README.md
    │   ├── 01-small-language-models-for-devices.md
    │   ├── 02-running-language-models-locally.md
    │   ├── 03-in-browser-inference-with-webgpu-and-webassembly.md
    │   ├── 04-on-device-speech-recognition.md
    │   ├── 05-real-time-vision-on-mobile.md
    │   ├── 06-edge-cloud-split-inference.md
    │   ├── 07-on-device-personalization-and-adaptation-with-brief-links-to-federated-learning-in-g12.md
    │   ├── 08-battery-and-thermal-cost-of-generative-workloads.md
    │   ├── 09-evaluating-the-user-experience.md
    │   └── README.md
    ├── 08-Edge-Fleet-Operations-and-Deployment/
    │   ├── Projects/
    │   │   ├── 01-ota-model-update-with-rollback.md
    │   │   ├── 02-edge-drift-monitoring-under-bandwidth-limits.md
    │   │   ├── 03-signed-model-delivery.md
    │   │   └── README.md
    │   ├── 01-over-the-air-model-updates.md
    │   ├── 02-device-heterogeneity.md
    │   ├── 03-telemetry-under-bandwidth-limits.md
    │   ├── 04-monitoring-without-labels-at-the-edge.md
    │   ├── 05-secure-delivery.md
    │   ├── 06-offline-first-design-and-edge-cloud-synchronization.md
    │   ├── 07-collecting-edge-data-for-retraining-safely.md
    │   ├── 08-edge-orchestration-with-lightweight-kubernetes-distributions-and-gateways.md
    │   ├── 09-regulated-and-safety-relevant-edge-systems.md
    │   └── README.md
    ├── 09-Distributed-Training-Fundamentals-and-Communication/
    │   ├── Projects/
    │   │   ├── 01-ddp-scaling-study.md
    │   │   ├── 02-distributed-hang-debugging-clinic.md
    │   │   ├── 03-elastic-and-resumable-training.md
    │   │   └── README.md
    │   ├── 01-data-parallelism-in-detail.md
    │   ├── 02-collective-communication.md
    │   ├── 03-topology-awareness.md
    │   ├── 04-launching-and-orchestration.md
    │   ├── 05-scaling-efficiency.md
    │   ├── 06-debugging-distributed-jobs.md
    │   ├── 07-fault-tolerance.md
    │   ├── 08-sharded-and-asynchronous-checkpointing-at-scale.md
    │   ├── 09-reproducibility-and-numerical-differences-across-parallel-configurations.md
    │   ├── 10-measuring-efficiency.md
    │   └── README.md
    ├── 10-Model-Parallelism-Tensor-Pipeline-Sequence-and-Expert/
    │   ├── Projects/
    │   │   ├── 01-tensor-and-pipeline-parallel-from-scratch.md
    │   │   ├── 02-parallelism-configuration-planner.md
    │   │   ├── 03-fsdp2-vs-zero-comparison.md
    │   │   └── README.md
    │   ├── 01-why-data-parallelism-is-not-enough.md
    │   ├── 02-optimizer-state-sharding.md
    │   ├── 03-tensor-parallelism.md
    │   ├── 04-pipeline-parallelism.md
    │   ├── 05-sequence-and-context-parallelism.md
    │   ├── 06-expert-parallelism-for-mixture-of-experts-models.md
    │   ├── 07-combining-strategies.md
    │   ├── 08-frameworks.md
    │   ├── 09-activation-recomputation-and-offloading-trade-offs.md
    │   ├── 10-testing-parallel-correctness.md
    │   └── README.md
    ├── 11-Large-Scale-Data-Loading-and-Training-Pipelines/
    │   ├── Projects/
    │   │   ├── 01-streaming-dataset-pipeline-with-resume.md
    │   │   ├── 02-input-pipeline-bottleneck-study.md
    │   │   ├── 03-shuffle-quality-vs-throughput.md
    │   │   └── README.md
    │   ├── 01-why-data-loading-limits-training.md
    │   ├── 02-sharded-storage-formats.md
    │   ├── 03-streaming-datasets.md
    │   ├── 04-object-storage-throughput-and-local-caching-tiers.md
    │   ├── 05-shuffling-at-scale-and-its-effect-on-convergence.md
    │   ├── 06-tokenization-and-preprocessing-pipelines-at-scale.md
    │   ├── 07-ray-data-and-distributed-preprocessing.md
    │   ├── 08-data-pipeline-testing.md
    │   ├── 09-cost-of-data-movement.md
    │   └── README.md
    ├── 12-Distributed-Frameworks-and-Cluster-Scheduling/
    │   ├── Projects/
    │   │   ├── 01-ray-vs-kubernetes-jobs-comparison.md
    │   │   ├── 02-gpu-job-queue-with-fair-share.md
    │   │   ├── 03-preemptible-training-cost-study.md
    │   │   └── README.md
    │   ├── 01-ray-for-training-tuning-and-serving.md
    │   ├── 02-parameter-server-and-all-reduce-architectures-compared.md
    │   ├── 03-cluster-schedulers.md
    │   ├── 04-gang-scheduling-priorities-and-preemption-for-training-jobs.md
    │   ├── 05-multi-tenancy.md
    │   ├── 06-hyperparameter-search-at-cluster-scale.md
    │   ├── 07-spot-and-preemptible-capacity.md
    │   ├── 08-running-distributed-jobs-on-kubernetes-with-operators-for-training-jobs.md
    │   ├── 09-choosing-a-framework.md
    │   └── README.md
    ├── 13-GPU-Cluster-Operations-and-AI-Compute-Economics/
    │   ├── Projects/
    │   │   ├── 01-gpu-utilization-and-waste-audit.md
    │   │   ├── 02-training-run-cost-and-carbon-model.md
    │   │   ├── 03-buy-vs-rent-vs-credits-decision-memo.md
    │   │   └── README.md
    │   ├── 01-gpu-cluster-architecture.md
    │   ├── 02-gpu-partitioning-and-sharing.md
    │   ├── 03-gpu-health-and-monitoring.md
    │   ├── 04-failure-handling.md
    │   ├── 05-capacity-planning.md
    │   ├── 06-cost-of-a-training-run-and-cost-per-token-served.md
    │   ├── 07-energy-and-carbon-accounting-for-ml-workloads.md
    │   ├── 08-accessing-compute-in-india.md
    │   ├── 09-procurement-and-total-cost-of-ownership-modeling.md
    │   └── README.md
    ├── 14-Efficiency-Measurement-Benchmarking-and-Capacity-Planning/
    │   ├── Projects/
    │   │   ├── 01-efficiency-regression-test-in-ci.md
    │   │   ├── 02-queueing-model-vs-load-test.md
    │   │   ├── 03-pareto-report-for-a-deployment-decision.md
    │   │   └── README.md
    │   ├── 01-efficiency-metrics.md
    │   ├── 02-accuracy-efficiency-pareto-analysis-and-how-to-report-it.md
    │   ├── 03-public-benchmarks.md
    │   ├── 04-fair-comparison-pitfalls.md
    │   ├── 05-load-modeling-and-queueing-basics-for-inference-capacity.md
    │   ├── 06-forecasting-compute-demand-and-budgeting.md
    │   ├── 07-efficiency-regression-testing-in-ci.md
    │   ├── 08-writing-performance-reports-and-decision-records.md
    │   ├── 09-responsible-reporting.md
    │   └── README.md
    ├── 15-G10-Capstones/
    │   ├── 01-inference-optimization-study-for-a-production-model.md
    │   ├── 02-edge-deployment-of-a-model-to-real-hardware.md
    │   ├── 03-multi-gpu-training-system.md
    │   ├── 04-accuracy-efficiency-pareto-research-project.md
    │   ├── 05-g10-readiness-assessment.md
    │   └── README.md
    └── README.md
```

### 00 — G10 Overview

**Purpose:** the single authoritative plan for G10 with scope, boundaries, prerequisite map, hardware and software register, benchmarking standards and completion gate.

- `01-g10-scope-and-boundaries-with-stage-5c-5d-and-other-groups.md` — what G10 teaches and what it leaves to other groups.
- `02-prerequisite-map-from-the-roadmap.md` — Roadmap stages and groups assumed for each G10 module.
- `03-hardware-dataset-and-tooling-register.md` — every device, accelerator, cloud instance, dataset, library and framework with version, licence, price and date, and maintenance status for each tool.
- `04-benchmarking-and-reporting-standards.md` — warmup, repeats, percentiles, clock and thermal control, equal-conditions rules and report template.
- `05-completion-gate.md` — measurable criteria to finish G10.
- `learning-plan.md` — recommended order, tracks for inference, edge and distributed training, and a compute-access plan for learners with limited hardware.

**Project 1: g10 hardware and benchmark harness bootstrap**  
- Data: a small model of your choice.  
- Task: build a reproducible workspace with pinned tooling and a benchmark harness that controls warmup, repeats, clocks where possible, records hardware and software versions and reports percentiles with variance.  
- Deliverables: lockfile, harness with tests and a hardware inventory file.  
- Pass gate: a clean machine reproduces the tests from the lockfile, and the harness flags a deliberately noisy measurement as unreliable.

### 01 — Hardware Performance Modeling for ML

**Outcome:** Predict and explain model speed from hardware first principles before touching code. The Stage 0 lessons on GPUs and why they matter for AI are the starting point, and general inference profiling is covered in Stage 5D.

**Lessons**

- `01-the-roofline-model.md` — The roofline model: arithmetic intensity, memory-bound and compute-bound regimes
- `02-gpu-architecture-for-ml.md` — GPU architecture for ML: streaming multiprocessors, warps, memory hierarchy and tensor cores
- `03-cpu-performance.md` — CPU performance: vector instructions, caches, memory channels and NUMA
- `04-accelerator-families.md` — Accelerator families: TPUs, NPUs and cloud inference chips and how they differ from GPUs
- `05-interconnects.md` — Interconnects: PCIe, NVLink and network fabrics and what bandwidth means for models
- `06-numeric-formats.md` — Numeric formats: FP32, TF32, BF16, FP16, FP8, INT8, INT4 and block-scaled formats
- `07-back-of-envelope-estimation.md` — Back-of-envelope estimation: predicting latency and throughput of a model from its shape and the hardware specification
- `08-benchmarking-method.md` — Benchmarking method: warmup, variance, percentiles, clock and thermal effects
- `09-measuring-power-and-energy-per-inference.md` — Measuring power and energy per inference

**Hands-on projects**

- **Project 1: roofline measurement and prediction**  
  - Data: Matrix-multiply, convolution and attention operators on a GPU or CPU available to you  
  - Task: Measure achieved throughput against the hardware roofline for several operator shapes and predict which are memory-bound.  
  - Deliverables: Roofline plot with predictions and measurements.  
  - Pass gate: Prediction error reported for each operator shape.
- **Project 2: model latency estimator**  
  - Data: Three models of different families, such as a CNN, an encoder transformer and a decoder LLM  
  - Task: Build a calculator that estimates latency and memory from model shapes and device specifications and validate it against measurements.  
  - Deliverables: Calculator and validation table.  
  - Pass gate: Error against measurement reported at several batch sizes.
- **Project 3: benchmarking methodology audit**  
  - Data: Published performance claims you choose  
  - Task: Reproduce a claim and identify methodology weaknesses such as missing warmup, small samples or unstated clocks.  
  - Deliverables: Audit report.  
  - Pass gate: Every reproduced number reported with run-to-run variance.

### 02 — GPU Kernels and ML Compiler Stacks

**Outcome:** Understand and write the low-level operations that dominate inference and training time. Using torch.compile, ONNX Runtime and TensorRT is covered in Stage 5D and the FlashAttention idea in Stage 5C; this module covers how they work.

**Lessons**

- `01-cuda-programming-model-for-ml-engineers.md` — CUDA programming model for ML engineers: threads, blocks, memory coalescing and shared memory
- `02-kernel-optimization-patterns.md` — Kernel optimization patterns: tiling a matrix multiply and parallel reductions
- `03-writing-kernels-in-triton.md` — Writing kernels in Triton: fused softmax, layer normalization and matrix multiply
- `04-operator-fusion.md` — Operator fusion: why fused kernels win and what fusion cannot fix
- `05-implementing-a-flashattention-style-tiled-attention-kernel-and-verifying-it-against-a-reference.md` — Implementing a FlashAttention-style tiled attention kernel and verifying it against a reference
- `06-how-torch-compile-works.md` — How torch.compile works: graph capture, graph breaks and the Inductor code generator, and debugging compile failures
- `07-xla-and-jax-compilation.md` — XLA and JAX compilation: tracing, jit and sharding annotations
- `08-compiler-infrastructure-overview.md` — Compiler infrastructure overview: MLIR, TVM and vendor libraries such as cuBLAS, cuDNN and CUTLASS
- `09-kernel-level-profiling.md` — Kernel-level profiling: Nsight Systems, Nsight Compute and the PyTorch profiler
- `10-correctness-testing-for-custom-kernels.md` — Correctness testing for custom kernels: numerical tolerance and edge shapes

**Hands-on projects**

- **Project 1: triton fused kernels with benchmarks**  
  - Data: Random tensors and a small transformer layer  
  - Task: Write fused softmax and layer-normalization kernels in Triton and compare speed and accuracy with PyTorch eager and compiled versions.  
  - Deliverables: Kernels, tests and benchmark.  
  - Pass gate: Outputs match a float64 reference within a stated tolerance across shapes.
- **Project 2: tiled attention kernel**  
  - Data: Attention inputs of several sequence lengths  
  - Task: Implement a tiled attention kernel with online softmax and compare memory use and speed with naive attention.  
  - Deliverables: Kernel and scaling analysis.  
  - Pass gate: Numerical equivalence to naive attention verified.
- **Project 3: graph break and compile debugging clinic**  
  - Data: A model with dynamic control flow  
  - Task: Find and remove graph breaks and measure compile time against speed-up.  
  - Deliverables: Debug log and measurements.  
  - Pass gate: Each fix measured, not assumed.

### 03 — Quantization Pruning and Distillation in Depth

**Outcome:** Compress models while knowing exactly what quality is lost. Quantization and pruning for non-LLM models are covered in Stage 5D; the QLoRA quantized base weights are used in G3.

**Lessons**

- `01-post-training-quantization-vs-quantization-aware-training.md` — Post-training quantization vs quantization-aware training: when each is needed
- `02-calibration-for-int8.md` — Calibration for INT8: min-max, percentile and entropy methods, per-channel scaling and outlier handling
- `03-weight-only-quantization-for-language-models.md` — Weight-only quantization for language models: GPTQ and AWQ
- `04-activation-quantization-and-outliers.md` — Activation quantization and outliers: SmoothQuant and mixed-precision approaches
- `05-low-precision-floating-point.md` — Low-precision floating point: FP8 formats for training and inference
- `06-practical-formats.md` — Practical formats: GGUF k-quants and bitsandbytes 4-bit formats
- `07-kv-cache-quantization-and-long-context-degradation.md` — KV-cache quantization and long-context degradation
- `08-evaluating-compressed-models.md` — Evaluating compressed models: perplexity vs task accuracy vs long-context and safety behavior
- `09-pruning.md` — Pruning: structured, unstructured and hardware-supported 2:4 sparsity, and pruning large language models
- `10-knowledge-distillation.md` — Knowledge distillation: logit, feature and sequence-level distillation and distilling language models
- `11-other-compression.md` — Other compression: low-rank factorization, token pruning and early exit

**Hands-on projects**

- **Project 1: llm quantization quality and speed matrix**  
  - Data: A small open language model and a task suite including long-context and instruction-following checks  
  - Task: Compare FP16, INT8, GPTQ, AWQ and 4-bit formats on speed, memory and several quality measures.  
  - Deliverables: Quality-speed-memory matrix.  
  - Pass gate: Quality measured on tasks beyond perplexity.
- **Project 2: distillation vs training small from scratch**  
  - Data: A text classification or vision task with a large teacher model  
  - Task: Compare distilled students with students trained directly on labels across sizes.  
  - Deliverables: Size-quality curves.  
  - Pass gate: Same student architectures and training budget.
- **Project 3: structured sparsity on tensor cores**  
  - Data: A vision model  
  - Task: Apply 2:4 sparsity with fine-tuning and measure real speed-up on supporting hardware.  
  - Deliverables: Accuracy and speed results.  
  - Pass gate: Speed measured on hardware that supports sparsity.

### 04 — LLM Inference Engines and Serving Optimization

**Outcome:** Tune and operate language-model serving at the engine level. Dynamic batching, serving frameworks and KV-cache and speculative-decoding intuition are covered in Stages 5D and 5C, and basic vLLM configuration and API-versus-self-hosting cost in G3.

**Lessons**

- `01-prefill-and-decode.md` — Prefill and decode: two different performance regimes
- `02-kv-cache-memory-management.md` — KV-cache memory management: paged allocation and fragmentation
- `03-continuous-batching-and-chunked-prefill.md` — Continuous batching and chunked prefill: scheduling for throughput and latency
- `04-prefix-caching-and-prompt-reuse.md` — Prefix caching and prompt reuse
- `05-speculative-decoding-in-practice.md` — Speculative decoding in practice: draft models and tree-based schemes
- `06-tensor-parallel-inference-and-disaggregating-prefill-from-decode.md` — Tensor-parallel inference and disaggregating prefill from decode
- `07-long-context-serving.md` — Long-context serving: attention windows and KV compression
- `08-multi-adapter-serving.md` — Multi-adapter serving: many LoRA adapters on one base model
- `09-engines-compared.md` — Engines compared: vLLM, SGLang, TensorRT-LLM, llama.cpp and Hugging Face serving, with maintenance and licence checks
- `10-serving-metrics.md` — Serving metrics: time to first token, time per output token, throughput and goodput under latency objectives
- `11-capacity-planning-and-autoscaling-for-llm-replicas.md` — Capacity planning and autoscaling for LLM replicas

**Hands-on projects**

- **Project 1: llm serving benchmark under slo**  
  - Data: A mixed workload of short and long prompts with arrival patterns you generate  
  - Task: Benchmark two engines under varied load and report goodput under latency objectives.  
  - Deliverables: Load-test harness and results.  
  - Pass gate: Same hardware, model, workload and sampling settings for each engine.
- **Project 2: kv cache memory budget study**  
  - Data: A model and workload with different context lengths  
  - Task: Predict concurrent-request capacity from the memory model and validate against measured capacity.  
  - Deliverables: Prediction versus measurement.  
  - Pass gate: Memory accounting verified against reported usage.
- **Project 3: speculative decoding gain analysis**  
  - Data: Several task types such as code, chat and extraction  
  - Task: Measure speed-up from speculative decoding by task and batch size and find where it hurts.  
  - Deliverables: Speed-up map.  
  - Pass gate: Output quality verified unchanged for greedy decoding.

### 05 — Edge and On Device ML Foundations

**Outcome:** Deploy models to phones, single-board computers and smart cameras. Introductory edge deployment is covered in Stage 5D; this module covers the full conversion, benchmarking and packaging workflow.

**Lessons**

- `01-edge-constraints.md` — Edge constraints: memory, power, thermal limits, latency and connectivity
- `02-device-classes.md` — Device classes: phones, single-board computers, cameras, vehicles and wearables
- `03-runtimes.md` — Runtimes: LiteRT (formerly TensorFlow Lite), ONNX Runtime Mobile, ExecuTorch, Core ML and OpenVINO
- `04-accelerators-on-devices.md` — Accelerators on devices: NPUs, DSPs and mobile GPUs and delegate selection
- `05-conversion-pipelines.md` — Conversion pipelines: operator support gaps, numerical differences and fallbacks
- `06-efficient-architectures-for-the-edge.md` — Efficient architectures for the edge: mobile CNNs, small transformers and distilled models
- `07-on-device-benchmarking.md` — On-device benchmarking: latency, memory, energy and thermal throttling
- `08-packaging-and-updating-models-inside-applications.md` — Packaging and updating models inside applications
- `09-privacy-and-security-benefits-and-risks-of-on-device-inference.md` — Privacy and security benefits and risks of on-device inference

**Hands-on projects**

- **Project 1: convert and benchmark across runtimes**  
  - Data: A vision or audio model from earlier groups  
  - Task: Convert to two or more edge runtimes, verify numerical equivalence and benchmark latency, memory and energy on a real device.  
  - Deliverables: Conversion pipeline and device benchmark.  
  - Pass gate: Accuracy on a held-out set verified after conversion.
- **Project 2: thermal throttling study**  
  - Data: A continuous-inference workload  
  - Task: Measure sustained performance over thirty minutes and quantify throttling effects.  
  - Deliverables: Time-series of latency and temperature.  
  - Pass gate: Run lengths long enough to reach steady state.
- **Project 3: operator gap debugging**  
  - Data: A model with unsupported operators for the target runtime  
  - Task: Diagnose and fix operator gaps by rewriting or replacing operations and measure the accuracy effect.  
  - Deliverables: Debug log and accuracy comparison.  
  - Pass gate: Each rewrite verified numerically.

### 06 — TinyML and Microcontroller Machine Learning

**Outcome:** Run models on devices with kilobytes of memory.

**Lessons**

- `01-microcontroller-constraints.md` — Microcontroller constraints: flash, RAM, clock speed and no operating system
- `02-sensor-pipelines.md` — Sensor pipelines: sampling, analog-to-digital conversion and on-device feature extraction
- `03-tensorflow-lite-for-microcontrollers-and-cmsis-nn.md` — TensorFlow Lite for Microcontrollers and CMSIS-NN
- `04-integer-only-quantization-and-binary-or-very-low-bit-networks.md` — Integer-only quantization and binary or very low-bit networks
- `05-keyword-spotting-and-sensor-anomaly-detection-on-microcontrollers-using-models-from-g2-and-g5.md` — Keyword spotting and sensor anomaly detection on microcontrollers using models from G2 and G5
- `06-power-management.md` — Power management: duty cycling and wake-on-event design
- `07-firmware-integration.md` — Firmware integration: C and C++ basics, build systems and memory budgets
- `08-hardware-in-the-loop-testing-and-field-validation.md` — Hardware-in-the-loop testing and field validation
- `09-benchmarks-and-platforms.md` — Benchmarks and platforms: MLPerf Tiny and Edge Impulse

**Hands-on projects**

- **Project 1: keyword spotting on a microcontroller**  
  - Data: Google Speech Commands and a development board such as an Arduino-class or ESP32-class device  
  - Task: Train, quantize and deploy a keyword-spotting model and measure accuracy on-device, memory and power.  
  - Deliverables: Firmware, model and measurements.  
  - Pass gate: On-device accuracy compared with desktop accuracy and the gap explained.
- **Project 2: sensor anomaly detector on device**  
  - Data: Accelerometer or temperature data from a low-cost sensor  
  - Task: Build an on-device anomaly detector with duty cycling and measure battery life.  
  - Deliverables: Firmware and battery analysis.  
  - Pass gate: Battery life estimated from measured current.
- **Project 3: memory budget planning tool**  
  - Data: Several small models  
  - Task: Build a tool that predicts flash and RAM use before deployment and validate on hardware.  
  - Deliverables: Tool and validation.  
  - Pass gate: Prediction error against measured usage reported.

### 07 — On Device Language Vision and Speech Models

**Outcome:** Run larger generative and perception models on phones and laptops. Quantized small language models use the compression methods of module 03.

**Lessons**

- `01-small-language-models-for-devices.md` — Small language models for devices: capabilities and limits
- `02-running-language-models-locally.md` — Running language models locally: llama.cpp, MLX and mobile runtimes
- `03-in-browser-inference-with-webgpu-and-webassembly.md` — In-browser inference with WebGPU and WebAssembly
- `04-on-device-speech-recognition.md` — On-device speech recognition: efficient Whisper-class models
- `05-real-time-vision-on-mobile.md` — Real-time vision on mobile: camera pipelines and frame scheduling
- `06-edge-cloud-split-inference.md` — Edge-cloud split inference: partitioning models and offloading decisions
- `07-on-device-personalization-and-adaptation-with-brief-links-to-federated-learning-in-g12.md` — On-device personalization and adaptation with brief links to federated learning in G12
- `08-battery-and-thermal-cost-of-generative-workloads.md` — Battery and thermal cost of generative workloads
- `09-evaluating-the-user-experience.md` — Evaluating the user experience: perceived latency and quality under device limits

**Hands-on projects**

- **Project 1: on device assistant feasibility study**  
  - Data: A small language model and a laptop or phone you own  
  - Task: Measure memory, speed, battery and quality for several quantization levels on a defined task set and decide where on-device is viable.  
  - Deliverables: Feasibility report with measurements.  
  - Pass gate: Task quality compared with a cloud baseline.
- **Project 2: edge cloud offloading policy**  
  - Data: A vision or speech workload with simulated network conditions  
  - Task: Design a policy that chooses local or cloud inference and evaluate latency, cost and accuracy.  
  - Deliverables: Policy and simulation.  
  - Pass gate: Network conditions varied systematically.
- **Project 3: real time camera pipeline**  
  - Data: A live or recorded video stream  
  - Task: Build a detection pipeline with frame skipping and measure end-to-end latency and accuracy.  
  - Deliverables: Pipeline and trade-off curve.  
  - Pass gate: End-to-end latency measured from capture to output.

### 08 — Edge Fleet Operations and Deployment

**Outcome:** Operate many devices running models over years. Kubernetes basics, CI/CD and release strategies are covered in Stages 2E and 5D; this module covers constraints unique to devices.

**Lessons**

- `01-over-the-air-model-updates.md` — Over-the-air model updates: staged rollout, rollback and compatibility
- `02-device-heterogeneity.md` — Device heterogeneity: testing across hardware and firmware versions
- `03-telemetry-under-bandwidth-limits.md` — Telemetry under bandwidth limits: what to log and how to sample
- `04-monitoring-without-labels-at-the-edge.md` — Monitoring without labels at the edge: input and output drift signals
- `05-secure-delivery.md` — Secure delivery: model signing, secure boot and tamper resistance
- `06-offline-first-design-and-edge-cloud-synchronization.md` — Offline-first design and edge-cloud synchronization
- `07-collecting-edge-data-for-retraining-safely.md` — Collecting edge data for retraining safely
- `08-edge-orchestration-with-lightweight-kubernetes-distributions-and-gateways.md` — Edge orchestration with lightweight Kubernetes distributions and gateways
- `09-regulated-and-safety-relevant-edge-systems.md` — Regulated and safety-relevant edge systems: cases where failure affects safety

**Hands-on projects**

- **Project 1: ota model update with rollback**  
  - Data: A simulated or real device fleet  
  - Task: Implement a staged model rollout with health checks and automatic rollback and test with a faulty model.  
  - Deliverables: Update system and fault-injection tests.  
  - Pass gate: A deliberately faulty model is rolled back automatically.
- **Project 2: edge drift monitoring under bandwidth limits**  
  - Data: Simulated device streams with injected drift  
  - Task: Design compact summary statistics and detect drift with a small telemetry budget.  
  - Deliverables: Detector and detection-delay analysis.  
  - Pass gate: Telemetry volume measured against detection performance.
- **Project 3: signed model delivery**  
  - Data: A model artifact  
  - Task: Add signing and verification to model delivery and test against tampered artifacts.  
  - Deliverables: Delivery pipeline and tamper tests.  
  - Pass gate: Tampered artifacts are rejected in tests.

### 09 — Distributed Training Fundamentals and Communication

**Outcome:** Train on many GPUs and diagnose scaling problems. The ideas of DDP, FSDP and activation checkpointing are explained in Stage 5C, and mixed precision and gradient accumulation in Stage 5C; this module covers the communication systems beneath them.

**Lessons**

- `01-data-parallelism-in-detail.md` — Data parallelism in detail: gradient bucketing and overlapping communication with compute
- `02-collective-communication.md` — Collective communication: all-reduce algorithms, ring and tree, and NCCL
- `03-topology-awareness.md` — Topology awareness: intra-node and inter-node bandwidth and placement
- `04-launching-and-orchestration.md` — Launching and orchestration: torchrun, SLURM and Kubernetes jobs
- `05-scaling-efficiency.md` — Scaling efficiency: strong and weak scaling and where efficiency is lost
- `06-debugging-distributed-jobs.md` — Debugging distributed jobs: hangs, deadlocks and collective mismatches
- `07-fault-tolerance.md` — Fault tolerance: elastic training, preemption and restart
- `08-sharded-and-asynchronous-checkpointing-at-scale.md` — Sharded and asynchronous checkpointing at scale
- `09-reproducibility-and-numerical-differences-across-parallel-configurations.md` — Reproducibility and numerical differences across parallel configurations
- `10-measuring-efficiency.md` — Measuring efficiency: model FLOPs utilization and throughput accounting

**Hands-on projects**

- **Project 1: ddp scaling study**  
  - Data: A vision or language model trained on 1, 2, 4 and 8 devices if available, or simulated with CPU processes  
  - Task: Measure throughput and scaling efficiency, then identify and fix the dominant bottleneck.  
  - Deliverables: Scaling curves and bottleneck analysis.  
  - Pass gate: Efficiency computed against a single-device baseline.
- **Project 2: distributed hang debugging clinic**  
  - Data: Intentionally broken distributed training scripts you build  
  - Task: Reproduce mismatched collectives, uneven data and rank-specific failures and write diagnostics for each.  
  - Deliverables: Failure catalog and diagnostics.  
  - Pass gate: Each failure diagnosed from logs and tooling.
- **Project 3: elastic and resumable training**  
  - Data: A long training run  
  - Task: Kill workers at random and verify the run resumes to the same result within tolerance.  
  - Deliverables: Fault-injection tests.  
  - Pass gate: Final metric matches an uninterrupted run within seed noise.

### 10 — Model Parallelism Tensor Pipeline Sequence and Expert

**Outcome:** Train models too large for one device by choosing and combining parallelism strategies. The transformer and mixture-of-experts architecture content is in Stage 5C and G3.

**Lessons**

- `01-why-data-parallelism-is-not-enough.md` — Why data parallelism is not enough: the memory model of training
- `02-optimizer-state-sharding.md` — Optimizer-state sharding: ZeRO stages and FSDP2 in practice
- `03-tensor-parallelism.md` — Tensor parallelism: column and row partitioning of transformer layers
- `04-pipeline-parallelism.md` — Pipeline parallelism: GPipe, one-forward-one-backward schedules and bubble reduction
- `05-sequence-and-context-parallelism.md` — Sequence and context parallelism: ring attention and related methods
- `06-expert-parallelism-for-mixture-of-experts-models.md` — Expert parallelism for mixture-of-experts models
- `07-combining-strategies.md` — Combining strategies: choosing a configuration for a given model and cluster
- `08-frameworks.md` — Frameworks: Megatron-LM, DeepSpeed, torchtitan and JAX sharding
- `09-activation-recomputation-and-offloading-trade-offs.md` — Activation recomputation and offloading trade-offs
- `10-testing-parallel-correctness.md` — Testing parallel correctness: equivalence to single-device training

**Hands-on projects**

- **Project 1: tensor and pipeline parallel from scratch**  
  - Data: A small transformer language model  
  - Task: Implement tensor and pipeline parallelism in a small framework of your own across processes and verify equivalence with single-device training.  
  - Deliverables: Implementation and equivalence tests.  
  - Pass gate: Losses and gradients match single-device training within tolerance.
- **Project 2: parallelism configuration planner**  
  - Data: Model sizes and cluster specifications  
  - Task: Build a planner that estimates memory and time for configurations and validate it on small runs.  
  - Deliverables: Planner and validation.  
  - Pass gate: Predictions compared with measurements on at least three configurations.
- **Project 3: fsdp2 vs zero comparison**  
  - Data: A medium language model  
  - Task: Compare FSDP2 and DeepSpeed ZeRO on memory, throughput and ease of checkpointing.  
  - Deliverables: Comparison.  
  - Pass gate: Same model, batch, precision and hardware.

### 11 — Large Scale Data Loading and Training Pipelines

**Outcome:** Keep accelerators fed when datasets do not fit locally. Dataset versioning and embedding pipelines are covered in Stages 2D and 5D, and Spark and Dask processing in Stages 2B and 2C.

**Lessons**

- `01-why-data-loading-limits-training.md` — Why data loading limits training: measuring input-pipeline stalls
- `02-sharded-storage-formats.md` — Sharded storage formats: Parquet, Arrow, WebDataset shards and Zarr
- `03-streaming-datasets.md` — Streaming datasets: resumable, deterministic and shuffled streaming
- `04-object-storage-throughput-and-local-caching-tiers.md` — Object storage throughput and local caching tiers
- `05-shuffling-at-scale-and-its-effect-on-convergence.md` — Shuffling at scale and its effect on convergence
- `06-tokenization-and-preprocessing-pipelines-at-scale.md` — Tokenization and preprocessing pipelines at scale
- `07-ray-data-and-distributed-preprocessing.md` — Ray Data and distributed preprocessing
- `08-data-pipeline-testing.md` — Data pipeline testing: determinism, coverage and corruption checks
- `09-cost-of-data-movement.md` — Cost of data movement: egress, replication and locality

**Hands-on projects**

- **Project 1: streaming dataset pipeline with resume**  
  - Data: A multi-gigabyte image or text dataset in object storage  
  - Task: Build a sharded streaming pipeline with deterministic shuffling and exact resume and measure GPU utilization.  
  - Deliverables: Pipeline and utilization analysis.  
  - Pass gate: Resumed training sees exactly the same remaining samples.
- **Project 2: input pipeline bottleneck study**  
  - Data: An existing training job  
  - Task: Vary storage, caching and loader workers and map their effect on throughput.  
  - Deliverables: Throughput map.  
  - Pass gate: GPU utilization measured, not assumed.
- **Project 3: shuffle quality vs throughput**  
  - Data: A streaming text dataset  
  - Task: Compare shuffle buffer sizes on training loss and throughput.  
  - Deliverables: Loss-throughput trade-off.  
  - Pass gate: Multiple seeds per setting.

### 12 — Distributed Frameworks and Cluster Scheduling

**Outcome:** Run varied ML workloads on shared clusters. XGBoost on Dask and RAPIDS are covered in G1, RL actor-learner systems in G4, and Kubernetes fundamentals in Stage 2E.

**Lessons**

- `01-ray-for-training-tuning-and-serving.md` — Ray for training, tuning and serving: architecture and failure model
- `02-parameter-server-and-all-reduce-architectures-compared.md` — Parameter-server and all-reduce architectures compared
- `03-cluster-schedulers.md` — Cluster schedulers: SLURM and Kubernetes batch scheduling with Kueue and Volcano
- `04-gang-scheduling-priorities-and-preemption-for-training-jobs.md` — Gang scheduling, priorities and preemption for training jobs
- `05-multi-tenancy.md` — Multi-tenancy: quotas, fairness and noisy neighbors
- `06-hyperparameter-search-at-cluster-scale.md` — Hyperparameter search at cluster scale: scheduling many small jobs efficiently
- `07-spot-and-preemptible-capacity.md` — Spot and preemptible capacity: checkpoint design and cost-risk trade-offs
- `08-running-distributed-jobs-on-kubernetes-with-operators-for-training-jobs.md` — Running distributed jobs on Kubernetes with operators for training jobs
- `09-choosing-a-framework.md` — Choosing a framework: matching workload shape to system

**Hands-on projects**

- **Project 1: ray vs kubernetes jobs comparison**  
  - Data: A hyperparameter search and a distributed training workload  
  - Task: Run both on Ray and on native Kubernetes jobs and compare setup effort, utilization and failure recovery.  
  - Deliverables: Comparison report.  
  - Pass gate: Same workloads, hardware and failure injection.
- **Project 2: gpu job queue with fair share**  
  - Data: A simulated cluster with several teams  
  - Task: Implement or configure a queue with quotas and preemption and evaluate fairness and utilization.  
  - Deliverables: Scheduler configuration and simulation results.  
  - Pass gate: Fairness and utilization both reported.
- **Project 3: preemptible training cost study**  
  - Data: A training job with periodic checkpoints  
  - Task: Model expected cost and completion time on preemptible versus on-demand capacity as checkpoint interval varies.  
  - Deliverables: Cost model validated by simulation.  
  - Pass gate: Preemption rates stated with source and date.

### 13 — GPU Cluster Operations and AI Compute Economics

**Outcome:** Operate accelerator infrastructure and understand its cost. General cloud FinOps and Kubernetes operations are covered in Stage 2E.

**Lessons**

- `01-gpu-cluster-architecture.md` — GPU cluster architecture: nodes, networking and storage
- `02-gpu-partitioning-and-sharing.md` — GPU partitioning and sharing: multi-instance GPU and time-slicing
- `03-gpu-health-and-monitoring.md` — GPU health and monitoring: utilization, memory, ECC and error events with DCGM
- `04-failure-handling.md` — Failure handling: node failures, silent data corruption and stragglers
- `05-capacity-planning.md` — Capacity planning: reserved vs on-demand vs spot
- `06-cost-of-a-training-run-and-cost-per-token-served.md` — Cost of a training run and cost per token served
- `07-energy-and-carbon-accounting-for-ml-workloads.md` — Energy and carbon accounting for ML workloads
- `08-accessing-compute-in-india.md` — Accessing compute in India: the IndiaAI compute portal, cloud credits and academic clusters, with eligibility to be checked on official portals
- `09-procurement-and-total-cost-of-ownership-modeling.md` — Procurement and total-cost-of-ownership modeling

**Hands-on projects**

- **Project 1: gpu utilization and waste audit**  
  - Data: GPU job logs from a cluster or a simulated cluster  
  - Task: Measure utilization and identify waste from idle allocations, small batches and stalls and propose changes with estimated savings.  
  - Deliverables: Audit report.  
  - Pass gate: Savings estimates computed from measured utilization.
- **Project 2: training run cost and carbon model**  
  - Data: A planned training run  
  - Task: Estimate cost, time and energy under several hardware and parallelism choices and validate on a small run.  
  - Deliverables: Model and validation.  
  - Pass gate: Prices and power figures cited with sources and dates.
- **Project 3: buy vs rent vs credits decision memo**  
  - Data: A workload profile you define  
  - Task: Compare owning, renting, cloud credits and government compute programs and recommend.  
  - Deliverables: Decision memo.  
  - Pass gate: Eligibility and prices read from official sources and dated.

### 14 — Efficiency Measurement Benchmarking and Capacity Planning

**Outcome:** Measure and report efficiency credibly across inference, edge and distributed training.

**Lessons**

- `01-efficiency-metrics.md` — Efficiency metrics: latency percentiles, throughput, goodput, energy and cost per request
- `02-accuracy-efficiency-pareto-analysis-and-how-to-report-it.md` — Accuracy-efficiency Pareto analysis and how to report it
- `03-public-benchmarks.md` — Public benchmarks: MLPerf training, inference and tiny, and their rules
- `04-fair-comparison-pitfalls.md` — Fair comparison pitfalls: unequal hardware, batch sizes, precisions and software versions
- `05-load-modeling-and-queueing-basics-for-inference-capacity.md` — Load modeling and queueing basics for inference capacity
- `06-forecasting-compute-demand-and-budgeting.md` — Forecasting compute demand and budgeting
- `07-efficiency-regression-testing-in-ci.md` — Efficiency regression testing in CI
- `08-writing-performance-reports-and-decision-records.md` — Writing performance reports and decision records
- `09-responsible-reporting.md` — Responsible reporting: environmental cost and rebound effects

**Hands-on projects**

- **Project 1: efficiency regression test in ci**  
  - Data: A served model  
  - Task: Add performance tests to CI with variance-aware thresholds and show a regression being caught.  
  - Deliverables: CI configuration and demonstration.  
  - Pass gate: Thresholds set from measured run-to-run variance.
- **Project 2: queueing model vs load test**  
  - Data: A model-serving endpoint  
  - Task: Predict latency under load with a queueing model and compare with load-test results.  
  - Deliverables: Prediction versus measurement.  
  - Pass gate: Model assumptions checked against measured service times.
- **Project 3: pareto report for a deployment decision**  
  - Data: Several compressed and uncompressed variants of one model  
  - Task: Produce an accuracy-latency-cost Pareto report and a recommendation for two different deployment targets.  
  - Deliverables: Decision report.  
  - Pass gate: All measurements on stated hardware with variance.

### 15 — G10 Capstones

**Outcome:** integrate the inference, edge and distributed-training tracks in assessed, portfolio-quality work. Learners without multi-GPU access complete the distributed capstone on a CPU-process simulation plus a small rented or credit-funded run.

- **Capstone 1: inference optimization study for a production model** (uses Modules 01 to 04, 14)  
  Take a model from baseline to optimized serving with kernel, compression and engine-level changes, a quality-regression suite and a cost and efficiency report.
- **Capstone 2: edge deployment of a model to real hardware** (uses Modules 05 to 08)  
  Deploy a model to a phone, single-board computer or microcontroller with on-device benchmarks, an update mechanism and a monitoring design.
- **Capstone 3: multi gpu training system** (uses Modules 09 to 13)  
  Build a scalable training setup with data loading, parallelism, fault tolerance, scheduling and a cost and scaling report.
- **Capstone 4: accuracy efficiency pareto research project** (uses Modules 03, 04, 14)  
  Run a controlled study of compression and serving trade-offs across model families and report the Pareto fronts with honest uncertainty.
- **Capstone 5: g10 readiness assessment** (uses All modules)  
  Written and practical assessment against the G10 completion gate.

## G10 completion gate

- Every performance claim is measured with warmup, repeated runs and reported percentiles and variance, on stated hardware and software versions.
- Every optimization reports quality before and after on tasks beyond a single proxy metric, and shows where quality degrades.
- Every comparison between tools or engines uses equal hardware, model, precision, workload and settings.
- Every custom kernel, conversion and parallelization is verified numerically against a reference implementation.
- Every cost, price and power figure cites its source and date.
- Every library, engine and framework has licence and maintenance status recorded in the register before adoption.
- Every deployed edge or distributed system has a tested rollback or restart path.
- At least one negative or inconclusive result per track is reported honestly, including a case where an optimization did not help.
- The four specialist capstones are complete and the readiness assessment is passed.

## Audit and verification

**What was checked and the result**

- Structure: 14 specialist modules each have 6 to 12 lessons and at least one project; the tree contains 219 files and 31 folders, and these counts equal the counts computed from the curriculum data.
- Overlap with the Roadmap: all 133 lesson file names were compared against every lesson file name in `Roadmap.md`. Exact matches: 0. Near matches (similarity 0.80 or higher): 1 — `speculative-decoding-in-practice` vs Roadmap `speculative-decoding-intuition` (0.81). Reviewed manually: the G10 lesson deliberately deepens the Stage 5C speculative-decoding intuition into engine-level practice (draft models, tree schemes, batch-size effects) and does not reteach the intuition.
- Structural problems found by the build script: 0.
- Topic-level overlap check: the Roadmap text was searched for Triton, CUDA programming, tensor and pipeline parallelism, DeepSpeed, NCCL, Megatron, distillation, quantization-aware training, GPTQ, AWQ, vLLM, PagedAttention, continuous batching, LiteRT or TFLite, Core ML, ExecuTorch, microcontrollers, TinyML, INT8, sparsity, roofline, arithmetic intensity, Ray, Horovod, all-reduce, JAX, XLA, Slurm and Nsight. None appear as lessons, so G10 teaches them for the first time. The Roadmap does contain, and G10 therefore references and extends rather than reteaches, the Stage 5D inference-optimization module (profiling, ONNX, ONNX Runtime and TensorRT, quantization and pruning for non-LLM models, dynamic batching, caching, edge basics, cost per prediction and autoscaling), the Stage 5C pretraining, compute and distributed-training lessons including DDP, FSDP and activation checkpointing, the Stage 5C efficient-attention lesson, and Stage 0 GPU lessons. Searches for 'zero', 'mpi', 'tpu' and 'npu' matched unrelated words and were discounted.
- Verified by web search on the build date (2026-10-26): Google renamed TensorFlow Lite to LiteRT on 4 September 2024 and it now accepts models from PyTorch, JAX and Keras; the IndiaAI compute portal offers subsidised GPU access to eligible startups, researchers and institutions, with reported capacity above 38,000 GPUs and reported rates near 65 to 67 rupees per GPU-hour, while an analysis from February 2026 argued it is heavily underused; PyTorch FSDP2 removes FSDP1's flat-parameter design and implements the ZeRO-3 idea, torchtitan is PyTorch's reference platform for large-scale training with FSDP2, tensor, pipeline and context parallelism, and Megatron-LM and DeepSpeed (ZeRO) are the established alternatives, per secondary sources.
- Reported but not confirmed: the status and licensing of ExecuTorch, Hugging Face's serving library, vLLM, SGLang and TensorRT-LLM were not confirmed by search and are required in the register; benchmark rules for MLPerf Training, Inference and Tiny, PagedAttention and continuous-batching details, the GPTQ, AWQ, SmoothQuant and SparseGPT methods, 2:4 sparsity hardware support, DCGM, Kueue and Volcano behavior, and every device, price and power figure were not confirmed and must be recorded from primary sources; compute-portal eligibility, rates and capacity differ between reports and change quickly.
- Not verified: library, engine and framework versions, which change very quickly in this group; hardware availability and prices; and any vendor performance claim.
- Not verified by execution: no code in this plan has been run. Project pass gates are acceptance criteria to be met when the projects are built, and several projects need specific hardware that learners may need to rent or borrow.
- Safety note: firmware and edge projects can affect physical devices and batteries, and cluster projects can incur large bills. Use isolated test hardware, set spending caps and alerts before running any cloud or cluster project, and do not push untested models to devices that others depend on.
- Repository safety: this build created only this file; no existing file or folder was created, changed or deleted by it.
