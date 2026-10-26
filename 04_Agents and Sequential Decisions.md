# Agents and Sequential Decisions — ML Specialization Roadmap

**Group 4 (G4)** of the specialization that follows Stage 5D of the [Roadmap](./Roadmap.md). It covers original categories **9 Reinforcement Learning Engineering and 40 AI Agents and Reinforcement Learning Systems**. The group's defining question is: *how does a system act over many steps?* It follows G1 ([`01_Classical and Applied ML.md`](./01_Classical%20and%20Applied%20ML.md)), G2 ([`02_Deep Learning by Modality.md`](./02_Deep%20Learning%20by%20Modality.md)) and G3 ([`03_Generative and Foundation Models.md`](./03_Generative%20and%20Foundation%20Models.md)).

## G4 summary

| Item | Count |
|---|---|
| Modules (including overview and capstones) | 21 |
| Lesson files | 154 |
| Hands-on project files (module projects, overview project and capstones) | 62 |
| Folders inside the G4 tree | 41 |
| Files inside the G4 tree | 264 |

| Original category | Modules |
|---|---|
| 9 Reinforcement Learning Engineering | 01 to 09 |
| 40 AI Agents and Reinforcement Learning Systems | 10 to 19 |

## Scope and how G4 avoids repeating the Roadmap

G4 starts where Stage 5B and Stage 5C stop. These are **already learned** and are only referenced, never retaught: Markov decision processes and Bellman equations, value and policy iteration, Monte Carlo and temporal-difference learning, Q-learning with function approximation, REINFORCE, actor-critic and PPO intuition, reward design and exploration basics (Stage 5B); contextual bandits and off-policy evaluation for one-step decisions (Stage 5B); the DAG scheduler and agent-workflow graphs and state machines as data structures (Stage 3); SFT, RLHF, DPO, reward models, constitutional AI, reinforcement learning for reasoning, chain-of-thought and test-time compute (Stage 5C); and from Stages 5D and 2E, containers, CI/CD, monitoring, SLOs, circuit breakers, human-in-the-loop review patterns and champion-challenger routing. Single-request function calling, structured outputs, RAG, LLM evaluation and application-layer LLM security are covered in G3 and are referenced only.

**Boundaries with other groups** (so nothing overlaps): LLM post-training algorithms (DPO, KTO, GRPO runs) belong to **G3**; tool calling in a single request and RAG belong to **G3**; operations-research optimization and graph learning belong to **G8**; distributed training, kernels and inference acceleration belong to **G10**; adversarial ML and responsible-AI methods in general belong to **G12**; rigorous benchmark design belongs to **G13**.

| Roadmap topic already covered | Where G4 goes further |
|---|---|
| Tabular Q-learning and policy-gradient agents (5B) | Modules 02 and 03: DQN and Rainbow, PPO implementation details, TD3 and SAC |
| Reward design, exploration and RL in practice (5B) | Modules 01 and 04: experiment protocol, curiosity, hindsight relabeling and imitation learning |
| MDPs and dynamic programming (5B) | Module 05: MCTS, AlphaZero, MuZero and learned world models |
| Bandits and off-policy evaluation (5B) | Module 06: offline RL, sequential off-policy evaluation and constrained RL |
| RL concepts (5B), RL for reasoning (5C) | Modules 07 to 09: multi-agent RL, scaling simulators and when RL is the right tool |
| Agent workflow graphs and state machines (Stage 3) | Modules 10 and 14: the agent loop, workflows vs agents and orchestration with frameworks |
| Human-in-the-loop review pattern, circuit breakers (5D) | Module 15: durable execution, approval gates and trajectory replay |
| ML-specific security (5D) | Module 17: sandboxing, indirect injection through tools and the lethal trifecta |
| RLHF, DPO and RL for reasoning concepts (5C) | Module 19: multi-turn RL and trajectory training for tool-using agents |

## G4 — Agents and Sequential Decisions

**Defining question:** How does a system act over many steps?

```text
ML Specialization/
└── G4 — Agents and Sequential Decisions/
    ├── 00-G4-Overview/
    │   ├── Projects/
    │   │   ├── 01-g4-environment-simulator-and-budget-bootstrap.md
    │   │   └── README.md
    │   ├── 01-g4-scope-and-boundaries-with-stage-5b-and-other-groups.md
    │   ├── 02-prerequisite-map-from-the-roadmap.md
    │   ├── 03-dataset-and-tooling-register.md
    │   ├── 04-evaluation-and-reporting-standards.md
    │   ├── 05-completion-gate.md
    │   ├── README.md
    │   └── learning-plan.md
    ├── 01-RL-Engineering-Foundations-and-Experiment-Protocol/
    │   ├── Projects/
    │   │   ├── 01-custom-environment-with-validation-suite.md
    │   │   ├── 02-seed-variance-and-reporting-study.md
    │   │   ├── 03-rl-debugging-playbook-on-broken-agents.md
    │   │   └── README.md
    │   ├── 01-environment-interface.md
    │   ├── 02-writing-a-custom-environment.md
    │   ├── 03-vectorized-environments-and-seeding.md
    │   ├── 04-library-landscape.md
    │   ├── 05-why-rl-results-are-unreliable.md
    │   ├── 06-reporting-protocol.md
    │   ├── 07-debugging-rl.md
    │   ├── 08-logging-and-monitoring-a-run.md
    │   └── README.md
    ├── 02-Deep-Value-Based-Reinforcement-Learning/
    │   ├── Projects/
    │   │   ├── 01-dqn-from-scratch-on-cartpole-and-atari.md
    │   │   ├── 02-rainbow-component-ablation.md
    │   │   ├── 03-overestimation-bias-measurement.md
    │   │   └── README.md
    │   ├── 01-dqn.md
    │   ├── 02-double-dqn-and-the-overestimation-problem.md
    │   ├── 03-dueling-networks-and-prioritized-experience-replay.md
    │   ├── 04-multi-step-returns-and-noisy-networks.md
    │   ├── 05-distributional-rl.md
    │   ├── 06-rainbow.md
    │   ├── 07-atari-preprocessing-frame-stacking-and-evaluation-conventions.md
    │   ├── 08-hyperparameters-that-matter.md
    │   └── README.md
    ├── 03-Deep-Policy-Gradient-and-Actor-Critic-Methods/
    │   ├── Projects/
    │   │   ├── 01-ppo-from-scratch-with-implementation-detail-ablation.md
    │   │   ├── 02-continuous-control-comparison.md
    │   │   ├── 03-action-masking-for-structured-decisions.md
    │   │   └── README.md
    │   ├── 01-a2c-and-generalized-advantage-estimation-in-code.md
    │   ├── 02-ppo-implementation-details.md
    │   ├── 03-trpo-and-natural-policy-gradients.md
    │   ├── 04-continuous-control.md
    │   ├── 05-td3.md
    │   ├── 06-soft-actor-critic.md
    │   ├── 07-action-space-design.md
    │   ├── 08-sensitivity-and-tuning.md
    │   └── README.md
    ├── 04-Exploration-Imitation-and-Goal-Conditioned-Learning/
    │   ├── Projects/
    │   │   ├── 01-sparse-reward-exploration-comparison.md
    │   │   ├── 02-her-on-robotic-reaching-tasks.md
    │   │   ├── 03-behavior-cloning-vs-dagger.md
    │   │   └── README.md
    │   ├── 01-exploration-strategies.md
    │   ├── 02-reward-shaping.md
    │   ├── 03-sparse-reward-learning.md
    │   ├── 04-goal-conditioned-rl-and-hindsight-experience-replay.md
    │   ├── 05-behavior-cloning.md
    │   ├── 06-dagger.md
    │   ├── 07-inverse-rl-and-gail.md
    │   ├── 08-combining-demonstrations-with-rl.md
    │   └── README.md
    ├── 05-Model-Based-Reinforcement-Learning-and-Planning/
    │   ├── Projects/
    │   │   ├── 01-mcts-agent-for-a-board-game.md
    │   │   ├── 02-alphazero-lite-on-a-small-game.md
    │   │   ├── 03-learned-dynamics-model-error-study.md
    │   │   └── README.md
    │   ├── 01-why-model-based-rl.md
    │   ├── 02-dyna-style-methods.md
    │   ├── 03-monte-carlo-tree-search.md
    │   ├── 04-alphazero.md
    │   ├── 05-muzero.md
    │   ├── 06-latent-world-models.md
    │   ├── 07-model-predictive-control-with-learned-dynamics.md
    │   ├── 08-planning-under-model-uncertainty.md
    │   └── README.md
    ├── 06-Offline-Safe-and-Constrained-Reinforcement-Learning/
    │   ├── Projects/
    │   │   ├── 01-offline-rl-benchmark.md
    │   │   ├── 02-sequential-off-policy-evaluation-study.md
    │   │   ├── 03-constrained-rl-with-cost-limit.md
    │   │   └── README.md
    │   ├── 01-offline-rl-problem.md
    │   ├── 02-conservative-methods.md
    │   ├── 03-sequence-modeling-approaches.md
    │   ├── 04-offline-datasets-and-benchmarks.md
    │   ├── 05-off-policy-evaluation-for-sequential-decisions.md
    │   ├── 06-constrained-mdps.md
    │   ├── 07-safe-exploration.md
    │   ├── 08-from-simulation-to-deployment.md
    │   └── README.md
    ├── 07-Multi-Agent-Reinforcement-Learning-and-Games/
    │   ├── Projects/
    │   │   ├── 01-cooperative-marl-comparison.md
    │   │   ├── 02-poker-exploitability-measurement.md
    │   │   ├── 03-self-play-cross-play-evaluation.md
    │   │   └── README.md
    │   ├── 01-multi-agent-settings.md
    │   ├── 02-game-theory-essentials-for-learners.md
    │   ├── 03-independent-learning-and-its-failure-modes.md
    │   ├── 04-centralized-training-with-decentralized-execution.md
    │   ├── 05-self-play-and-population-based-training.md
    │   ├── 06-communication-and-coordination.md
    │   ├── 07-environments-and-tooling.md
    │   ├── 08-evaluating-multi-agent-systems.md
    │   └── README.md
    ├── 08-Scaling-RL-Systems-and-Simulators/
    │   ├── Projects/
    │   │   ├── 01-rl-throughput-optimization.md
    │   │   ├── 02-jax-environment-vs-cpu-simulator.md
    │   │   └── README.md
    │   ├── 01-where-rl-time-goes.md
    │   ├── 02-distributed-actor-learner-architectures.md
    │   ├── 03-off-policy-correction.md
    │   ├── 04-accelerated-simulation.md
    │   ├── 05-gpu-physics-simulation.md
    │   ├── 06-throughput-engineering.md
    │   ├── 07-cost-accounting.md
    │   ├── 08-checkpointing-and-fault-tolerance-for-long-rl-runs.md
    │   └── README.md
    ├── 09-Applied-RL-Problem-Selection-and-Deployment/
    │   ├── Projects/
    │   │   ├── 01-inventory-control-rl-vs-baselines.md
    │   │   ├── 02-reward-hacking-case-study.md
    │   │   ├── 03-rl-decision-memo.md
    │   │   └── README.md
    │   ├── 01-rl-vs-supervised-learning-vs-bandits-vs-optimization.md
    │   ├── 02-formulating-a-business-problem-as-an-mdp.md
    │   ├── 03-simulators-for-business-problems.md
    │   ├── 04-reward-specification-risks.md
    │   ├── 05-application-areas.md
    │   ├── 06-safe-deployment.md
    │   ├── 07-monitoring-rl-policies-in-production.md
    │   ├── 08-case-studies-of-successes-and-failures.md
    │   └── README.md
    ├── 10-Agent-Foundations-Workflows-and-the-Agent-Loop/
    │   ├── Projects/
    │   │   ├── 01-agent-from-scratch-without-a-framework.md
    │   │   ├── 02-workflow-vs-agent-comparison.md
    │   │   ├── 03-runaway-agent-containment-tests.md
    │   │   └── README.md
    │   ├── 01-workflows-vs-agents.md
    │   ├── 02-the-agent-loop.md
    │   ├── 03-building-a-minimal-agent-from-raw-api-calls-without-a-framework.md
    │   ├── 04-stop-conditions-and-budgets.md
    │   ├── 05-reflexion-and-self-correction-loops.md
    │   ├── 06-autonomy-levels-and-human-oversight.md
    │   ├── 07-complexity-cost-and-latency-trade-offs-of-agentic-designs.md
    │   ├── 08-choosing-a-model-for-agent-work.md
    │   └── README.md
    ├── 11-Tool-Design-and-the-Model-Context-Protocol/
    │   ├── Projects/
    │   │   ├── 01-mcp-server-for-an-internal-data-source.md
    │   │   ├── 02-tool-description-ablation.md
    │   │   ├── 03-many-tools-selection-study.md
    │   │   └── README.md
    │   ├── 01-tool-interface-design.md
    │   ├── 02-tool-results-and-errors.md
    │   ├── 03-idempotency-and-side-effects.md
    │   ├── 04-model-context-protocol-architecture.md
    │   ├── 05-building-an-mcp-server.md
    │   ├── 06-authentication-and-authorization-for-mcp-servers.md
    │   ├── 07-code-execution-browser-and-computer-use-tools.md
    │   ├── 08-tool-selection-at-scale.md
    │   ├── 09-testing-tools.md
    │   └── README.md
    ├── 12-Agent-Memory-and-Context-Engineering/
    │   ├── Projects/
    │   │   ├── 01-long-horizon-task-with-compaction.md
    │   │   ├── 02-long-term-memory-store-with-evaluation.md
    │   │   ├── 03-subagent-context-isolation-experiment.md
    │   │   └── README.md
    │   ├── 01-context-as-the-working-memory.md
    │   ├── 02-compaction-and-summarization-for-long-running-tasks-and-their-information-loss.md
    │   ├── 03-scratchpads-notes-and-files-as-external-memory.md
    │   ├── 04-long-term-memory.md
    │   ├── 05-memory-read-and-write-policies.md
    │   ├── 06-forgetting-staleness-and-privacy-in-memory-stores.md
    │   ├── 07-subagents-for-context-isolation.md
    │   ├── 08-evaluating-memory.md
    │   └── README.md
    ├── 13-Planning-Verification-and-Reasoning-in-Agents/
    │   ├── Projects/
    │   │   ├── 01-verified-code-fixing-agent.md
    │   │   ├── 02-plan-and-execute-vs-interleaved.md
    │   │   ├── 03-clarifying-question-policy-study.md
    │   │   └── README.md
    │   ├── 01-task-decomposition.md
    │   ├── 02-search-over-plans.md
    │   ├── 03-verification.md
    │   ├── 04-self-critique-and-reflection.md
    │   ├── 05-reasoning-models-inside-agents.md
    │   ├── 06-replanning-and-recovery.md
    │   ├── 07-specifying-goals.md
    │   ├── 08-cost-aware-planning.md
    │   └── README.md
    ├── 14-Multi-Agent-Orchestration-and-Frameworks/
    │   ├── Projects/
    │   │   ├── 01-same-system-three-ways.md
    │   │   ├── 02-handoff-and-state-bug-hunt.md
    │   │   ├── 03-framework-maintenance-and-portability-audit.md
    │   │   └── README.md
    │   ├── 01-orchestration-patterns.md
    │   ├── 02-when-multiple-agents-help-and-when-a-single-agent-is-better.md
    │   ├── 03-debate-and-critic-patterns.md
    │   ├── 04-frameworks-compared.md
    │   ├── 05-agent-communication-standards.md
    │   ├── 06-shared-state-message-passing-and-conflict-resolution.md
    │   ├── 07-cost-multiplication-and-coordination-failures-in-multi-agent-systems.md
    │   ├── 08-framework-risk.md
    │   └── README.md
    ├── 15-Agent-Reliability-Durable-Execution-and-Human-Oversight/
    │   ├── Projects/
    │   │   ├── 01-durable-agent-with-crash-recovery.md
    │   │   ├── 02-approval-gate-design-and-evaluation.md
    │   │   ├── 03-trajectory-replay-debugger.md
    │   │   └── README.md
    │   ├── 01-why-agents-fail-in-production.md
    │   ├── 02-durable-execution.md
    │   ├── 03-retries-timeouts-and-idempotency-keys-across-tool-calls.md
    │   ├── 04-human-in-the-loop-design.md
    │   ├── 05-budgets-and-circuit-breakers-for-agent-runs.md
    │   ├── 06-tracing-agent-runs.md
    │   ├── 07-replay-and-debugging.md
    │   ├── 08-versioning-agents.md
    │   └── README.md
    ├── 16-Agent-Evaluation/
    │   ├── Projects/
    │   │   ├── 01-agent-benchmark-reproduction.md
    │   │   ├── 02-custom-agent-test-suite-with-ci-gate.md
    │   │   ├── 03-trajectory-judge-calibration.md
    │   │   └── README.md
    │   ├── 01-what-to-measure.md
    │   ├── 02-outcome-based-checks.md
    │   ├── 03-trajectory-evaluation.md
    │   ├── 04-reliability-metrics.md
    │   ├── 05-simulated-users-and-environments-for-conversational-agents.md
    │   ├── 06-public-agent-benchmarks.md
    │   ├── 07-building-a-custom-agent-test-suite-and-regression-gate.md
    │   ├── 08-cost-and-efficiency-evaluation.md
    │   └── README.md
    ├── 17-Agent-Security-Sandboxing-and-Governance/
    │   ├── Projects/
    │   │   ├── 01-agent-sandbox-escape-tests.md
    │   │   ├── 02-lethal-trifecta-audit.md
    │   │   ├── 03-agent-red-team-suite.md
    │   │   └── README.md
    │   ├── 01-excessive-agency.md
    │   ├── 02-indirect-prompt-injection-through-tools-web-pages-and-documents.md
    │   ├── 03-the-lethal-trifecta.md
    │   ├── 04-sandboxing.md
    │   ├── 05-least-privilege-tool-permissions-scoped-credentials-and-secrets-handling.md
    │   ├── 06-audit-logs-kill-switches-and-incident-response-for-agents.md
    │   ├── 07-computer-use-and-browser-agent-risks.md
    │   ├── 08-red-teaming-agents.md
    │   ├── 09-governance.md
    │   └── README.md
    ├── 18-Agent-Applications-and-Design-Patterns/
    │   ├── Projects/
    │   │   ├── 01-data-analysis-agent-with-validation.md
    │   │   ├── 02-support-agent-with-policy-checks.md
    │   │   ├── 03-agent-unit-economics-model.md
    │   │   └── README.md
    │   ├── 01-coding-agents.md
    │   ├── 02-research-agents.md
    │   ├── 03-data-analysis-agents.md
    │   ├── 04-customer-support-and-back-office-agents.md
    │   ├── 05-browser-and-computer-use-agents.md
    │   ├── 06-enterprise-integration.md
    │   ├── 07-agent-unit-economics.md
    │   ├── 08-pattern-library-and-anti-patterns-from-real-deployments.md
    │   └── README.md
    ├── 19-Training-Agents-with-Reinforcement-Learning/
    │   ├── Projects/
    │   │   ├── 01-trajectory-sft-and-rejection-sampling-for-a-tool-agent.md
    │   │   ├── 02-multi-turn-rl-with-verifiable-reward.md
    │   │   ├── 03-train-vs-prompt-decision-study.md
    │   │   └── README.md
    │   ├── 01-from-single-turn-to-multi-turn-rl.md
    │   ├── 02-building-training-environments-for-agents.md
    │   ├── 03-reward-design-for-agents.md
    │   ├── 04-collecting-and-filtering-agent-trajectories.md
    │   ├── 05-rejection-sampling-and-iterative-improvement-of-agent-policies.md
    │   ├── 06-reinforcement-learning-with-verifiable-rewards-in-agentic-environments.md
    │   ├── 07-evaluating-trained-agents.md
    │   ├── 08-cost-compute-and-when-prompting-and-scaffolding-beat-training.md
    │   └── README.md
    ├── 20-G4-Capstones/
    │   ├── 01-deep-rl-research-grade-study.md
    │   ├── 02-rl-system-for-a-business-decision.md
    │   ├── 03-production-grade-agent-system.md
    │   ├── 04-trained-tool-using-agent.md
    │   ├── 05-g4-readiness-assessment.md
    │   └── README.md
    └── README.md
```

### 00 — G4 Overview

**Purpose:** the single authoritative plan for G4 with scope, boundaries, prerequisite map, environment and tooling register, evaluation standards and completion gate.

- `01-g4-scope-and-boundaries-with-stage-5b-and-other-groups.md` — what G4 teaches and what it leaves to other groups.
- `02-prerequisite-map-from-the-roadmap.md` — Roadmap stages and modules assumed for each G4 module.
- `03-dataset-and-tooling-register.md` — every environment, dataset, framework, licence, model and API price with version pins and dates, including maintenance status for each library.
- `04-evaluation-and-reporting-standards.md` — seed counts, interquartile-mean reporting, repeated agent trials, pass-to-the-k reliability and report template.
- `05-completion-gate.md` — measurable criteria to finish G4.
- `learning-plan.md` — recommended order, two tracks (reinforcement learning and agents) with the bridge module, and compute and API budget.

**Project 1: g4 environment simulator and budget bootstrap**  
- Data: a toy Gymnasium environment and a scripted fake model API.  
- Task: build a reproducible workspace with pinned tooling, a spending cap, a seeded RL smoke test and an agent smoke test that runs against a scripted model so tests cost nothing.  
- Deliverables: lockfile, smoke tests and a call-and-cost logging wrapper.  
- Pass gate: a clean machine reproduces both smoke tests from the lockfile, and the spending cap blocks a deliberately excessive run.

### 01 — RL Engineering Foundations and Experiment Protocol

**Outcome:** Set up reinforcement-learning work so that results can be trusted. MDPs, Bellman equations, dynamic programming, Monte Carlo and TD learning, tabular Q-learning, REINFORCE and the PPO intuition are covered in Stage 5B and are not repeated.

**Lessons**

- `01-environment-interface.md` — Environment interface: Gymnasium, spaces, wrappers and the step/reset contract
- `02-writing-a-custom-environment.md` — Writing a custom environment: observation, action and reward design with validation checks
- `03-vectorized-environments-and-seeding.md` — Vectorized environments and seeding: reproducible rollouts and what determinism means in RL
- `04-library-landscape.md` — Library landscape: Stable-Baselines3, CleanRL, TorchRL and RLlib compared, with maintenance checks
- `05-why-rl-results-are-unreliable.md` — Why RL results are unreliable: seed variance, sensitivity and evaluation-vs-training returns
- `06-reporting-protocol.md` — Reporting protocol: many seeds, interquartile mean, performance profiles and confidence intervals with rliable
- `07-debugging-rl.md` — Debugging RL: sanity environments, reward and observation audits and learning-curve diagnosis
- `08-logging-and-monitoring-a-run.md` — Logging and monitoring a run: returns, losses, entropy, value error and gradient norms

**Hands-on projects**

- **Project 1: custom environment with validation suite**  
  - Data: A small inventory or resource-allocation simulator you write  
  - Task: Implement a Gymnasium environment, validate it with the environment checker and property tests, and solve it with a baseline algorithm.  
  - Deliverables: Environment package, test suite and baseline results.  
  - Pass gate: Environment passes the API checker and tests prove rewards and termination behave as documented.
- **Project 2: seed variance and reporting study**  
  - Data: CartPole, LunarLander and one MuJoCo task from Gymnasium  
  - Task: Train the same algorithm with at least 10 seeds and compare naive mean reporting against interquartile mean with confidence intervals.  
  - Deliverables: Report showing how conclusions change with the reporting method.  
  - Pass gate: At least 10 seeds per setting and intervals shown for every curve.
- **Project 3: rl debugging playbook on broken agents**  
  - Data: Intentionally broken training scripts you construct  
  - Task: Inject five bugs (reward scale, missing done flag, observation normalization, off-by-one in returns, wrong action mask) and write diagnostics that detect each.  
  - Deliverables: Bug catalog and automated checks.  
  - Pass gate: Every injected bug is detected by a diagnostic before training finishes.

### 02 — Deep Value Based Reinforcement Learning

**Outcome:** Implement and understand deep Q-learning and its modern improvements. The idea of Q-learning with function approximation is covered in Stage 5B.

**Lessons**

- `01-dqn.md` — DQN: replay buffer, target network and the deadly triad in practice
- `02-double-dqn-and-the-overestimation-problem.md` — Double DQN and the overestimation problem
- `03-dueling-networks-and-prioritized-experience-replay.md` — Dueling networks and prioritized experience replay
- `04-multi-step-returns-and-noisy-networks.md` — Multi-step returns and noisy networks
- `05-distributional-rl.md` — Distributional RL: C51 and quantile regression DQN
- `06-rainbow.md` — Rainbow: combining the components and ablating each one
- `07-atari-preprocessing-frame-stacking-and-evaluation-conventions.md` — Atari preprocessing, frame stacking and evaluation conventions
- `08-hyperparameters-that-matter.md` — Hyperparameters that matter: learning rate, buffer size, target update and exploration schedule

**Hands-on projects**

- **Project 1: dqn from scratch on cartpole and atari**  
  - Data: CartPole and one Atari game via the Arcade Learning Environment (check ROM licensing)  
  - Task: Implement DQN in PyTorch and compare it with a library implementation on learning curves.  
  - Deliverables: Implementation, tests and comparison across seeds.  
  - Pass gate: Learning curves match the library within seed variance or the gap is explained.
- **Project 2: rainbow component ablation**  
  - Data: Three Atari games or MinAtar environments  
  - Task: Add Double, Dueling, PER, multi-step, noisy nets and distributional heads one at a time and measure each contribution.  
  - Deliverables: Ablation table with interquartile means and intervals.  
  - Pass gate: At least 5 seeds per variant; components with gains inside noise are labeled as such.
- **Project 3: overestimation bias measurement**  
  - Data: A small environment with known true values  
  - Task: Measure Q-value overestimation for DQN and Double DQN against true returns.  
  - Deliverables: Bias plots and discussion.  
  - Pass gate: True values computed by exact dynamic programming.

### 03 — Deep Policy Gradient and Actor Critic Methods

**Outcome:** Implement the main deep policy-gradient and continuous-control algorithms with the details that make them work. The PPO intuition is covered in Stage 5B and the clipped-objective reasoning is not repeated.

**Lessons**

- `01-a2c-and-generalized-advantage-estimation-in-code.md` — A2C and generalized advantage estimation in code
- `02-ppo-implementation-details.md` — PPO implementation details: normalization, clipping, minibatching, learning-rate annealing and value clipping
- `03-trpo-and-natural-policy-gradients.md` — TRPO and natural policy gradients: why trust regions matter
- `04-continuous-control.md` — Continuous control: DDPG and why it is brittle
- `05-td3.md` — TD3: twin critics, delayed updates and target smoothing
- `06-soft-actor-critic.md` — Soft Actor-Critic: maximum-entropy RL and automatic temperature tuning
- `07-action-space-design.md` — Action-space design: discrete, continuous, hybrid and masked actions
- `08-sensitivity-and-tuning.md` — Sensitivity and tuning: which hyperparameters dominate and how to search them

**Hands-on projects**

- **Project 1: ppo from scratch with implementation detail ablation**  
  - Data: CartPole, LunarLander and a MuJoCo locomotion task  
  - Task: Implement PPO from scratch and ablate each implementation detail (advantage normalization, observation normalization, clipping variants, annealing).  
  - Deliverables: Ablation table with confidence intervals.  
  - Pass gate: Each detail's effect reported across at least 5 seeds.
- **Project 2: continuous control comparison**  
  - Data: MuJoCo tasks such as HalfCheetah, Walker2d and Hopper  
  - Task: Compare DDPG, TD3, SAC and PPO on sample efficiency and stability.  
  - Deliverables: Comparison with performance profiles.  
  - Pass gate: Equal environment-step budgets and tuned baselines.
- **Project 3: action masking for structured decisions**  
  - Data: A grid or scheduling environment with invalid actions  
  - Task: Compare penalizing invalid actions with masking them.  
  - Deliverables: Learning curves and invalid-action rates.  
  - Pass gate: Both approaches given equal tuning effort.

### 04 — Exploration Imitation and Goal Conditioned Learning

**Outcome:** Handle sparse rewards, learn from demonstrations and specify goals. Basic reward design and exploration ideas are covered in Stage 5B.

**Lessons**

- `01-exploration-strategies.md` — Exploration strategies: count-based bonuses, RND and ICM curiosity
- `02-reward-shaping.md` — Reward shaping: potential-based shaping and how shaping goes wrong
- `03-sparse-reward-learning.md` — Sparse-reward learning: curricula and automatic goal generation
- `04-goal-conditioned-rl-and-hindsight-experience-replay.md` — Goal-conditioned RL and hindsight experience replay
- `05-behavior-cloning.md` — Behavior cloning: compounding errors and when it is enough
- `06-dagger.md` — DAgger: interactive imitation learning
- `07-inverse-rl-and-gail.md` — Inverse RL and GAIL: learning rewards or policies from demonstrations
- `08-combining-demonstrations-with-rl.md` — Combining demonstrations with RL: warm starts and regularization

**Hands-on projects**

- **Project 1: sparse reward exploration comparison**  
  - Data: MiniGrid hard-exploration levels  
  - Task: Compare epsilon-greedy, count-based bonus and RND on sparse-reward levels.  
  - Deliverables: Success-rate curves across seeds.  
  - Pass gate: Equal step budget and at least 5 seeds.
- **Project 2: her on robotic reaching tasks**  
  - Data: Gymnasium-Robotics Fetch tasks or a simple goal-reaching environment  
  - Task: Train goal-conditioned agents with and without hindsight relabeling.  
  - Deliverables: Ablation and success-rate comparison.  
  - Pass gate: Relabeling strategy documented and tested.
- **Project 3: behavior cloning vs dagger**  
  - Data: An expert policy trained in a MuJoCo or Gymnasium environment  
  - Task: Compare behavior cloning and DAgger as demonstration data grows and measure compounding error.  
  - Deliverables: Performance vs number of demonstrations.  
  - Pass gate: Expert performance reported as the upper bound.

### 05 — Model Based Reinforcement Learning and Planning

**Outcome:** Use learned models and search to plan, from simple Dyna ideas to AlphaZero- and Dreamer-style agents.

**Lessons**

- `01-why-model-based-rl.md` — Why model-based RL: sample efficiency, model error and compounding
- `02-dyna-style-methods.md` — Dyna-style methods: mixing real and imagined experience
- `03-monte-carlo-tree-search.md` — Monte Carlo tree search: UCT and implementing MCTS from scratch
- `04-alphazero.md` — AlphaZero: self-play, policy-value networks and search-guided training
- `05-muzero.md` — MuZero: learning a model for planning without known dynamics
- `06-latent-world-models.md` — Latent world models: Dreamer-style agents
- `07-model-predictive-control-with-learned-dynamics.md` — Model predictive control with learned dynamics: PETS-style ensembles
- `08-planning-under-model-uncertainty.md` — Planning under model uncertainty: ensembles and pessimism

**Hands-on projects**

- **Project 1: mcts agent for a board game**  
  - Data: Connect Four or Tic-Tac-Toe via PettingZoo or a custom implementation  
  - Task: Implement MCTS and evaluate against random and minimax players at several simulation budgets.  
  - Deliverables: Win-rate vs simulation budget.  
  - Pass gate: Opponent strengths fixed and games alternate first player.
- **Project 2: alphazero lite on a small game**  
  - Data: A small game you implement, such as Connect Four on a reduced board  
  - Task: Train a policy-value network with self-play and MCTS and track Elo against checkpoints.  
  - Deliverables: Training pipeline and Elo curve.  
  - Pass gate: Elo measured against fixed earlier checkpoints.
- **Project 3: learned dynamics model error study**  
  - Data: A MuJoCo task  
  - Task: Train a dynamics ensemble and measure multi-step prediction error and its effect on planning performance.  
  - Deliverables: Error-horizon plots and planning results.  
  - Pass gate: Model error evaluated on held-out trajectories.

### 06 — Offline Safe and Constrained Reinforcement Learning

**Outcome:** Learn from logged data and under constraints, which is how RL meets real systems. Bandits and off-policy evaluation for one-step decisions are covered in Stage 5B.

**Lessons**

- `01-offline-rl-problem.md` — Offline RL problem: distribution shift, extrapolation error and why online methods fail on fixed data
- `02-conservative-methods.md` — Conservative methods: CQL and implicit Q-learning
- `03-sequence-modeling-approaches.md` — Sequence-modeling approaches: Decision Transformer and trajectory models
- `04-offline-datasets-and-benchmarks.md` — Offline datasets and benchmarks: D4RL and Minari, and their limits
- `05-off-policy-evaluation-for-sequential-decisions.md` — Off-policy evaluation for sequential decisions: importance sampling and fitted Q-evaluation
- `06-constrained-mdps.md` — Constrained MDPs: Lagrangian methods and cost limits
- `07-safe-exploration.md` — Safe exploration: shielding and safety layers
- `08-from-simulation-to-deployment.md` — From simulation to deployment: sim-to-real gap and staged rollout

**Hands-on projects**

- **Project 1: offline rl benchmark**  
  - Data: Minari or D4RL datasets of mixed and expert quality  
  - Task: Compare behavior cloning, CQL, IQL and Decision Transformer across dataset qualities.  
  - Deliverables: Comparison table with confidence intervals.  
  - Pass gate: Dataset quality reported alongside results.
- **Project 2: sequential off policy evaluation study**  
  - Data: Logged trajectories from a simulator with known ground-truth policy values  
  - Task: Estimate new-policy value with importance sampling and fitted Q-evaluation and compare with ground truth.  
  - Deliverables: Estimator bias and variance analysis.  
  - Pass gate: Ground-truth value computed by running the policy in the simulator.
- **Project 3: constrained rl with cost limit**  
  - Data: Safety Gymnasium or a constrained environment you build  
  - Task: Train a Lagrangian agent and show the reward-cost trade-off against an unconstrained agent.  
  - Deliverables: Trade-off curves and constraint-violation rates.  
  - Pass gate: Constraint violations reported on evaluation episodes.

### 07 — Multi Agent Reinforcement Learning and Games

**Outcome:** Train and evaluate agents that interact with other learners.

**Lessons**

- `01-multi-agent-settings.md` — Multi-agent settings: cooperative, competitive and mixed, and non-stationarity
- `02-game-theory-essentials-for-learners.md` — Game-theory essentials for learners: Nash equilibria, best response and exploitability
- `03-independent-learning-and-its-failure-modes.md` — Independent learning and its failure modes
- `04-centralized-training-with-decentralized-execution.md` — Centralized training with decentralized execution: MAPPO and QMIX
- `05-self-play-and-population-based-training.md` — Self-play and population-based training
- `06-communication-and-coordination.md` — Communication and coordination: learned protocols and conventions
- `07-environments-and-tooling.md` — Environments and tooling: PettingZoo and OpenSpiel
- `08-evaluating-multi-agent-systems.md` — Evaluating multi-agent systems: cross-play, exploitability and Elo

**Hands-on projects**

- **Project 1: cooperative marl comparison**  
  - Data: PettingZoo cooperative environments such as simple spread, or SMAC-style tasks  
  - Task: Compare independent PPO, MAPPO and QMIX.  
  - Deliverables: Learning curves and coordination analysis.  
  - Pass gate: At least 5 seeds with intervals.
- **Project 2: poker exploitability measurement**  
  - Data: Kuhn or Leduc poker in OpenSpiel  
  - Task: Train agents with self-play and measure exploitability against best responses.  
  - Deliverables: Exploitability curves.  
  - Pass gate: Exploitability computed exactly for these small games.
- **Project 3: self play cross play evaluation**  
  - Data: A two-player game environment  
  - Task: Train several self-play agents and evaluate cross-play to detect conventions that do not transfer.  
  - Deliverables: Cross-play matrix.  
  - Pass gate: All pairs evaluated with enough games for stable estimates.

### 08 — Scaling RL Systems and Simulators

**Outcome:** Make RL fast enough to run real experiments. General distributed training and kernels are covered later in G10; this module is specific to actor-learner systems and simulators.

**Lessons**

- `01-where-rl-time-goes.md` — Where RL time goes: environment stepping vs inference vs learning
- `02-distributed-actor-learner-architectures.md` — Distributed actor-learner architectures: IMPALA, Ape-X and asynchronous variants
- `03-off-policy-correction.md` — Off-policy correction: V-trace and staleness
- `04-accelerated-simulation.md` — Accelerated simulation: JAX-based environments such as Brax and Gymnax
- `05-gpu-physics-simulation.md` — GPU physics simulation: MuJoCo MJX and robotics simulators
- `06-throughput-engineering.md` — Throughput engineering: batching, pipelining and profiling an RL run
- `07-cost-accounting.md` — Cost accounting: environment steps per dollar and experiment budgeting
- `08-checkpointing-and-fault-tolerance-for-long-rl-runs.md` — Checkpointing and fault tolerance for long RL runs

**Hands-on projects**

- **Project 1: rl throughput optimization**  
  - Data: A PPO training run on a MuJoCo or Brax task  
  - Task: Profile and speed up a training run through vectorization and batching and report steps per second before and after.  
  - Deliverables: Profiles and throughput table.  
  - Pass gate: Learning performance verified unchanged after optimization.
- **Project 2: jax environment vs cpu simulator**  
  - Data: A task available in both a CPU simulator and a JAX version  
  - Task: Compare wall-clock time and cost to reach the same return.  
  - Deliverables: Cost-to-performance report.  
  - Pass gate: Equal return targets and hardware stated.

### 09 — Applied RL Problem Selection and Deployment

**Outcome:** Decide when reinforcement learning is the right tool and deploy it safely. Operations research methods themselves are covered later in G8.

**Lessons**

- `01-rl-vs-supervised-learning-vs-bandits-vs-optimization.md` — RL vs supervised learning vs bandits vs optimization: a decision framework
- `02-formulating-a-business-problem-as-an-mdp.md` — Formulating a business problem as an MDP: state, action, reward and horizon
- `03-simulators-for-business-problems.md` — Simulators for business problems: building and validating them
- `04-reward-specification-risks.md` — Reward specification risks: Goodhart effects and reward hacking in practice
- `05-application-areas.md` — Application areas: pricing, inventory, scheduling, recommendation sessions and control systems
- `06-safe-deployment.md` — Safe deployment: shadow mode, guardrails and fallback policies
- `07-monitoring-rl-policies-in-production.md` — Monitoring RL policies in production: drift and performance
- `08-case-studies-of-successes-and-failures.md` — Case studies of successes and failures

**Hands-on projects**

- **Project 1: inventory control rl vs baselines**  
  - Data: A simulated inventory problem with stochastic demand  
  - Task: Compare an RL policy with a base-stock heuristic and a supervised-forecast-plus-rule policy.  
  - Deliverables: Cost comparison with confidence intervals.  
  - Pass gate: Strong tuned heuristic baselines included.
- **Project 2: reward hacking case study**  
  - Data: A simulator you build with a flawed reward  
  - Task: Show an agent exploiting the reward, then redesign and re-verify.  
  - Deliverables: Before and after analysis.  
  - Pass gate: Exploit demonstrated with a trajectory, not asserted.
- **Project 3: rl decision memo**  
  - Data: Three candidate business problems  
  - Task: Write a go or no-go memo for RL on each, including a non-RL alternative.  
  - Deliverables: Decision memo.  
  - Pass gate: At least one problem is recommended against RL with reasons.

### 10 — Agent Foundations Workflows and the Agent Loop

**Outcome:** Understand what an agent is, build one from raw API calls and decide when you should not. Single-call function calling and structured outputs are covered in G3; the DAG and state-machine data structures are covered in Stage 3.

**Lessons**

- `01-workflows-vs-agents.md` — Workflows vs agents: prompt chaining, routing, parallelization and when autonomy is justified
- `02-the-agent-loop.md` — The agent loop: observe, think, act and the ReAct pattern
- `03-building-a-minimal-agent-from-raw-api-calls-without-a-framework.md` — Building a minimal agent from raw API calls without a framework
- `04-stop-conditions-and-budgets.md` — Stop conditions and budgets: step, token, time and cost limits
- `05-reflexion-and-self-correction-loops.md` — Reflexion and self-correction loops: when they help and when they spiral
- `06-autonomy-levels-and-human-oversight.md` — Autonomy levels and human oversight: choosing how much freedom to give
- `07-complexity-cost-and-latency-trade-offs-of-agentic-designs.md` — Complexity, cost and latency trade-offs of agentic designs
- `08-choosing-a-model-for-agent-work.md` — Choosing a model for agent work: tool-use reliability, long-horizon behavior and cost

**Hands-on projects**

- **Project 1: agent from scratch without a framework**  
  - Data: A set of small tools you write, such as calculator, file reader and web fetch with a stub  
  - Task: Implement the agent loop directly against a model API with tool calls, budgets and stop conditions.  
  - Deliverables: Agent code, trace logs and tests with a scripted model.  
  - Pass gate: Loop terminates under every stop condition in tests, including a model that never stops.
- **Project 2: workflow vs agent comparison**  
  - Data: A multi-step task such as research-and-report or ticket triage  
  - Task: Build the task as a fixed workflow and as an autonomous agent and compare reliability, cost and latency.  
  - Deliverables: Comparison over at least 50 runs.  
  - Pass gate: Success rate and cost reported with intervals.
- **Project 3: runaway agent containment tests**  
  - Data: An agent you build  
  - Task: Create scenarios that cause loops, tool misuse and cost blowups and add containment for each.  
  - Deliverables: Failure scenarios and containment tests.  
  - Pass gate: Every scenario terminates within a stated budget.

### 11 — Tool Design and the Model Context Protocol

**Outcome:** Design tools that models can use reliably and expose them through the Model Context Protocol.

**Lessons**

- `01-tool-interface-design.md` — Tool interface design: names, descriptions, parameters and examples that models use correctly
- `02-tool-results-and-errors.md` — Tool results and errors: formats that let the model recover
- `03-idempotency-and-side-effects.md` — Idempotency and side effects: designing safe retries
- `04-model-context-protocol-architecture.md` — Model Context Protocol architecture: hosts, clients, servers, tools, resources and prompts
- `05-building-an-mcp-server.md` — Building an MCP server: transports and capability negotiation
- `06-authentication-and-authorization-for-mcp-servers.md` — Authentication and authorization for MCP servers
- `07-code-execution-browser-and-computer-use-tools.md` — Code execution, browser and computer-use tools
- `08-tool-selection-at-scale.md` — Tool selection at scale: many tools, tool search and context cost
- `09-testing-tools.md` — Testing tools: contract tests and evaluating tool-use accuracy

**Hands-on projects**

- **Project 1: mcp server for an internal data source**  
  - Data: A local database or document store you create  
  - Task: Build an MCP server exposing read tools and resources with authentication, and connect it to an MCP client.  
  - Deliverables: Server, client configuration and contract tests.  
  - Pass gate: Server enforces authorization and rejects out-of-scope requests in tests.
- **Project 2: tool description ablation**  
  - Data: A set of 10 tools and 100 task prompts  
  - Task: Vary names, descriptions and error messages and measure tool-selection and argument accuracy.  
  - Deliverables: Ablation table.  
  - Pass gate: Accuracy measured over fixed prompts with repeated runs.
- **Project 3: many tools selection study**  
  - Data: A catalog of 50 to 200 tools  
  - Task: Measure accuracy and cost as the tool count grows and test tool-search designs.  
  - Deliverables: Accuracy-vs-tool-count curve.  
  - Pass gate: Token cost of tool definitions reported.

### 12 — Agent Memory and Context Engineering

**Outcome:** Keep agents coherent across long tasks and sessions. Prompt caching and context-window basics are covered in G3 and vector retrieval in G3 module 08.

**Lessons**

- `01-context-as-the-working-memory.md` — Context as the working memory: what to keep, compress and drop
- `02-compaction-and-summarization-for-long-running-tasks-and-their-information-loss.md` — Compaction and summarization for long-running tasks and their information loss
- `03-scratchpads-notes-and-files-as-external-memory.md` — Scratchpads, notes and files as external memory
- `04-long-term-memory.md` — Long-term memory: episodic, semantic and procedural memory designs
- `05-memory-read-and-write-policies.md` — Memory read and write policies: what to store and how to retrieve it
- `06-forgetting-staleness-and-privacy-in-memory-stores.md` — Forgetting, staleness and privacy in memory stores
- `07-subagents-for-context-isolation.md` — Subagents for context isolation: returning summaries instead of transcripts
- `08-evaluating-memory.md` — Evaluating memory: recall, consistency and harm from wrong memories

**Hands-on projects**

- **Project 1: long horizon task with compaction**  
  - Data: A task requiring hundreds of steps, such as processing many documents  
  - Task: Compare no compaction, summarization compaction and note-taking on task success and cost.  
  - Deliverables: Comparison with failure analysis.  
  - Pass gate: Information-loss errors counted and categorized.
- **Project 2: long term memory store with evaluation**  
  - Data: Multi-session conversation scenarios you script  
  - Task: Build a memory store with write and retrieval policies and test recall and wrong-memory harm.  
  - Deliverables: Store, policies and evaluation.  
  - Pass gate: Includes tests where retrieved memories are stale or wrong.
- **Project 3: subagent context isolation experiment**  
  - Data: A research task with large intermediate outputs  
  - Task: Compare a single-context agent with an orchestrator using subagents on accuracy and tokens.  
  - Deliverables: Accuracy-and-cost comparison.  
  - Pass gate: Token usage measured from logs.

### 13 — Planning Verification and Reasoning in Agents

**Outcome:** Make agents decompose tasks, check their own work and use reasoning budgets wisely. Chain-of-thought and test-time compute for single calls are covered in Stage 5C.

**Lessons**

- `01-task-decomposition.md` — Task decomposition: plan-then-execute vs interleaved planning
- `02-search-over-plans.md` — Search over plans: tree-of-thought style search and Monte Carlo search with language models
- `03-verification.md` — Verification: tests, validators, schemas and checkers as the agent's ground truth
- `04-self-critique-and-reflection.md` — Self-critique and reflection: gains, costs and failure cases
- `05-reasoning-models-inside-agents.md` — Reasoning models inside agents: thinking budgets and when more thinking hurts
- `06-replanning-and-recovery.md` — Replanning and recovery: handling tool failures and surprises
- `07-specifying-goals.md` — Specifying goals: ambiguity, clarifying questions and acceptance criteria
- `08-cost-aware-planning.md` — Cost-aware planning: choosing cheap vs expensive steps

**Hands-on projects**

- **Project 1: verified code fixing agent**  
  - Data: A small set of buggy repositories with unit tests  
  - Task: Build an agent that edits code and uses test results as feedback; compare with a no-verification variant.  
  - Deliverables: Agent and success-rate comparison.  
  - Pass gate: Fresh held-out test cases used for final evaluation.
- **Project 2: plan and execute vs interleaved**  
  - Data: A multi-step research or data task  
  - Task: Compare planning styles on success, cost and recovery from injected tool failures.  
  - Deliverables: Comparison with fault-injection results.  
  - Pass gate: Same tasks and injected failures across variants.
- **Project 3: clarifying question policy study**  
  - Data: Ambiguous task prompts with hidden correct interpretations  
  - Task: Test when asking a clarifying question improves outcomes versus proceeding.  
  - Deliverables: Policy comparison.  
  - Pass gate: Ground-truth interpretation hidden from the agent.

### 14 — Multi Agent Orchestration and Frameworks

**Outcome:** Coordinate several agents when it is justified and choose frameworks with open eyes. Graph and state-machine data structures are covered in Stage 3.

**Lessons**

- `01-orchestration-patterns.md` — Orchestration patterns: orchestrator-worker, handoffs, supervisor and parallel fan-out
- `02-when-multiple-agents-help-and-when-a-single-agent-is-better.md` — When multiple agents help and when a single agent is better
- `03-debate-and-critic-patterns.md` — Debate and critic patterns: evidence for and against
- `04-frameworks-compared.md` — Frameworks compared: LangGraph, OpenAI Agents SDK, Claude Agent SDK, Microsoft Agent Framework, CrewAI and Pydantic AI
- `05-agent-communication-standards.md` — Agent communication standards: MCP for tools and agent-to-agent protocols
- `06-shared-state-message-passing-and-conflict-resolution.md` — Shared state, message passing and conflict resolution
- `07-cost-multiplication-and-coordination-failures-in-multi-agent-systems.md` — Cost multiplication and coordination failures in multi-agent systems
- `08-framework-risk.md` — Framework risk: lock-in, abstraction leakage and maintenance status checks

**Hands-on projects**

- **Project 1: same system three ways**  
  - Data: A research-and-report task  
  - Task: Implement it as a single agent, an orchestrator-worker system and a framework-based graph, and compare quality, cost and complexity.  
  - Deliverables: Three implementations and a comparison.  
  - Pass gate: At least 30 runs per variant with intervals.
- **Project 2: handoff and state bug hunt**  
  - Data: A multi-agent customer-support workflow  
  - Task: Inject lost-context, duplicate-action and conflicting-state bugs and add tests and fixes.  
  - Deliverables: Bug catalog and regression tests.  
  - Pass gate: Each bug reproduced then prevented by a test.
- **Project 3: framework maintenance and portability audit**  
  - Data: Two frameworks of your choice  
  - Task: Port one workflow between frameworks and record migration cost and maintenance signals.  
  - Deliverables: Audit report.  
  - Pass gate: Release history and issue activity recorded with dates.

### 15 — Agent Reliability Durable Execution and Human Oversight

**Outcome:** Run agents that survive failures and ask for help at the right moment. General SRE, monitoring and CI/CD are covered in Stages 2E and 5D; this module is specific to long-running, non-deterministic workflows.

**Lessons**

- `01-why-agents-fail-in-production.md` — Why agents fail in production: compounding errors across steps
- `02-durable-execution.md` — Durable execution: checkpointing, resumption and workflow engines such as Temporal
- `03-retries-timeouts-and-idempotency-keys-across-tool-calls.md` — Retries, timeouts and idempotency keys across tool calls
- `04-human-in-the-loop-design.md` — Human-in-the-loop design: approval gates, escalation and review queues
- `05-budgets-and-circuit-breakers-for-agent-runs.md` — Budgets and circuit breakers for agent runs
- `06-tracing-agent-runs.md` — Tracing agent runs: spans for steps, tools and model calls with OpenTelemetry conventions
- `07-replay-and-debugging.md` — Replay and debugging: reproducing a failed trajectory
- `08-versioning-agents.md` — Versioning agents: prompts, tools and models as a unit

**Hands-on projects**

- **Project 1: durable agent with crash recovery**  
  - Data: A multi-step agent task with side effects in a test system  
  - Task: Make an agent resumable after process crashes without repeating side effects.  
  - Deliverables: Implementation and crash-injection tests.  
  - Pass gate: Killing the process at every step yields correct final state.
- **Project 2: approval gate design and evaluation**  
  - Data: A workflow with risky actions  
  - Task: Add approval gates and measure reviewer load against prevented bad actions.  
  - Deliverables: Load-versus-safety analysis.  
  - Pass gate: Bad-action prevention rate and reviewer burden both reported.
- **Project 3: trajectory replay debugger**  
  - Data: Logged agent runs  
  - Task: Build a tool that replays and diffs trajectories and finds the first diverging step.  
  - Deliverables: Tool and debugging case studies.  
  - Pass gate: Replay reproduces a recorded failure from logs alone.

### 16 — Agent Evaluation

**Outcome:** Measure whether agents work, reliably and cheaply. Rigorous benchmark methodology is covered later in G13 and application-level LLM evaluation in G3 module 09; this module covers what is specific to multi-step agents.

**Lessons**

- `01-what-to-measure.md` — What to measure: task success, process quality, cost, latency and safety
- `02-outcome-based-checks.md` — Outcome-based checks: environment state, tests and database diffs
- `03-trajectory-evaluation.md` — Trajectory evaluation: step-level scoring and LLM judges for transcripts
- `04-reliability-metrics.md` — Reliability metrics: pass-at-k vs pass-to-the-k and why repeated trials matter
- `05-simulated-users-and-environments-for-conversational-agents.md` — Simulated users and environments for conversational agents
- `06-public-agent-benchmarks.md` — Public agent benchmarks: SWE-bench, GAIA, tau-bench, WebArena and OSWorld, and their contamination and scaffolding caveats
- `07-building-a-custom-agent-test-suite-and-regression-gate.md` — Building a custom agent test suite and regression gate
- `08-cost-and-efficiency-evaluation.md` — Cost and efficiency evaluation: successful tasks per dollar

**Hands-on projects**

- **Project 1: agent benchmark reproduction**  
  - Data: A small public benchmark subset such as SWE-bench Lite instances or tau-bench tasks  
  - Task: Run your agent on the subset with repeated trials and report success and reliability honestly.  
  - Deliverables: Results with pass-to-the-k reliability and cost.  
  - Pass gate: At least 5 trials per task and run configuration published.
- **Project 2: custom agent test suite with ci gate**  
  - Data: A task domain of your choice  
  - Task: Build 50 or more tasks with automatic outcome checks and gate changes on a statistical threshold.  
  - Deliverables: Suite, checkers and CI configuration.  
  - Pass gate: A deliberately degraded agent fails the gate.
- **Project 3: trajectory judge calibration**  
  - Data: 100 agent trajectories you label  
  - Task: Build an LLM trajectory judge and measure agreement with your labels.  
  - Deliverables: Agreement analysis and bias checks.  
  - Pass gate: Judge calibrated before it is trusted.

### 17 — Agent Security Sandboxing and Governance

**Outcome:** Contain what agents can do and prove it. Application-layer prompt injection and guardrails are covered in G3 module 10 and adversarial ML in general in G12; this module covers risks that appear when models can act.

**Lessons**

- `01-excessive-agency.md` — Excessive agency: how capabilities, permissions and autonomy combine into risk
- `02-indirect-prompt-injection-through-tools-web-pages-and-documents.md` — Indirect prompt injection through tools, web pages and documents
- `03-the-lethal-trifecta.md` — The lethal trifecta: private data, untrusted content and external communication
- `04-sandboxing.md` — Sandboxing: containers, restricted file systems and network egress control
- `05-least-privilege-tool-permissions-scoped-credentials-and-secrets-handling.md` — Least-privilege tool permissions, scoped credentials and secrets handling
- `06-audit-logs-kill-switches-and-incident-response-for-agents.md` — Audit logs, kill switches and incident response for agents
- `07-computer-use-and-browser-agent-risks.md` — Computer-use and browser agent risks
- `08-red-teaming-agents.md` — Red-teaming agents: scenario design and automated attack suites
- `09-governance.md` — Governance: policies, approvals and accountability for autonomous systems

**Hands-on projects**

- **Project 1: agent sandbox escape tests**  
  - Data: A code-executing agent in a container you build  
  - Task: Attempt file, network and credential escapes and harden the sandbox until tests pass.  
  - Deliverables: Sandbox configuration and attack test suite.  
  - Pass gate: Run only in an isolated environment you own.
- **Project 2: lethal trifecta audit**  
  - Data: An agent with email, document and web access in a test environment  
  - Task: Map which tool combinations create exfiltration risk and break the trifecta with design changes.  
  - Deliverables: Risk map, attack demonstrations and fixes.  
  - Pass gate: Attacks use fake data and an isolated test mailbox.
- **Project 3: agent red team suite**  
  - Data: Your agents from earlier modules  
  - Task: Build an automated suite of injection and misuse scenarios and track attack success over versions.  
  - Deliverables: Suite and trend report.  
  - Pass gate: Fixed scenario set with success rates and intervals.

### 18 — Agent Applications and Design Patterns

**Outcome:** Apply agents to the main real task families and judge each on value, not novelty.

**Lessons**

- `01-coding-agents.md` — Coding agents: repository context, edit tools, test loops and review workflows
- `02-research-agents.md` — Research agents: search, reading, synthesis and citation verification
- `03-data-analysis-agents.md` — Data-analysis agents: SQL and notebook tools with result validation
- `04-customer-support-and-back-office-agents.md` — Customer-support and back-office agents: policy adherence and escalation
- `05-browser-and-computer-use-agents.md` — Browser and computer-use agents: capabilities and brittleness
- `06-enterprise-integration.md` — Enterprise integration: ticketing, CRM and workflow systems
- `07-agent-unit-economics.md` — Agent unit economics: cost per successful task against human cost
- `08-pattern-library-and-anti-patterns-from-real-deployments.md` — Pattern library and anti-patterns from real deployments

**Hands-on projects**

- **Project 1: data analysis agent with validation**  
  - Data: A public dataset and a set of analytical questions with known answers  
  - Task: Build an agent that writes and runs analysis code and validates its own results; measure answer accuracy.  
  - Deliverables: Agent and accuracy evaluation.  
  - Pass gate: Answers compared with known ground truth over repeated runs.
- **Project 2: support agent with policy checks**  
  - Data: A simulated support domain with policies and a simulated user  
  - Task: Build an agent that follows policy, uses tools and escalates correctly; evaluate with a tau-bench-style protocol.  
  - Deliverables: Agent and policy-violation analysis.  
  - Pass gate: Policy violations counted over repeated trials.
- **Project 3: agent unit economics model**  
  - Data: Measured cost and success from your agents  
  - Task: Compute cost per successful task and compare with an assumed human cost, with sensitivity analysis.  
  - Deliverables: Economics model.  
  - Pass gate: Every cost input measured or sourced.

### 19 — Training Agents with Reinforcement Learning

**Outcome:** Bridge the two halves of G4: use reinforcement learning to improve tool-using agents. Post-training algorithms for language models (DPO, GRPO) are covered in G3 module 05 and RL algorithms earlier in this group.

**Lessons**

- `01-from-single-turn-to-multi-turn-rl.md` — From single-turn to multi-turn RL: credit assignment across tool calls
- `02-building-training-environments-for-agents.md` — Building training environments for agents: tasks, tools and automatic verifiers
- `03-reward-design-for-agents.md` — Reward design for agents: outcome vs process rewards and hacking risks
- `04-collecting-and-filtering-agent-trajectories.md` — Collecting and filtering agent trajectories: supervised fine-tuning on successful traces
- `05-rejection-sampling-and-iterative-improvement-of-agent-policies.md` — Rejection sampling and iterative improvement of agent policies
- `06-reinforcement-learning-with-verifiable-rewards-in-agentic-environments.md` — Reinforcement learning with verifiable rewards in agentic environments
- `07-evaluating-trained-agents.md` — Evaluating trained agents: held-out environments and regression on general ability
- `08-cost-compute-and-when-prompting-and-scaffolding-beat-training.md` — Cost, compute and when prompting and scaffolding beat training

**Hands-on projects**

- **Project 1: trajectory sft and rejection sampling for a tool agent**  
  - Data: A verifiable tool-use task set such as arithmetic-with-tools or SQL tasks with executable checkers  
  - Task: Collect trajectories from a base model, keep verified successes, fine-tune a small model and compare with the base.  
  - Deliverables: Pipeline and held-out evaluation.  
  - Pass gate: Evaluation tasks never used for trajectory collection.
- **Project 2: multi turn rl with verifiable reward**  
  - Data: A small multi-step environment with an automatic checker  
  - Task: Train a small model with RL against the checker and audit for reward hacking.  
  - Deliverables: Training curves and hacking audit.  
  - Pass gate: Hacking audit on sampled trajectories included.
- **Project 3: train vs prompt decision study**  
  - Data: The same task domain  
  - Task: Compare prompt and scaffold engineering with fine-tuning and RL on quality and total cost.  
  - Deliverables: Decision report.  
  - Pass gate: Engineering time and compute cost both reported.

### 20 — G4 Capstones

**Outcome:** integrate the reinforcement-learning track and the agent track in assessed, portfolio-quality work.

- **Capstone 1: deep rl research grade study** (uses Modules 01 to 07)  
  Run a research-style study comparing several deep RL algorithms on a set of tasks with many seeds, interquartile-mean reporting, ablations and a negative result reported honestly.
- **Capstone 2: rl system for a business decision** (uses Modules 06, 08, 09)  
  Formulate a business decision problem, build a validated simulator, train and evaluate an RL policy against strong baselines, and write the deployment and monitoring plan.
- **Capstone 3: production grade agent system** (uses Modules 10 to 18)  
  Build an agent system for a real task family with tools exposed over MCP, memory, verification, durable execution, a test suite with a release gate, a security review and a unit-economics model.
- **Capstone 4: trained tool using agent** (uses Modules 16, 19)  
  Train a small tool-using agent with trajectory fine-tuning and verifiable-reward RL, evaluate it on held-out tasks against a prompted baseline and report cost honestly.
- **Capstone 5: g4 readiness assessment** (uses All modules)  
  Written and practical assessment against the G4 completion gate.

## G4 completion gate

- Every reinforcement-learning result uses at least 5 seeds (10 for headline claims) and reports interquartile means with confidence intervals.
- Every agent result uses repeated trials and reports success rate, reliability across repeats, cost and latency.
- All results reproduce from a lockfile, configs and logged seeds, with library versions, model versions, prices and dates recorded.
- Every agent has a sandbox, a permission model, a budget limit and an audit log before it touches real systems.
- Every library and framework used has its maintenance status and licence recorded in the register.
- At least one negative or inconclusive result per track is reported honestly.
- The four specialist capstones are complete and the readiness assessment is passed.

## Audit and verification

**What was checked and the result**

- Structure: 19 specialist modules each have 6 to 12 lessons and at least one project; the tree contains 264 files and 41 folders, and these counts equal the counts computed from the curriculum data.
- Overlap with the Roadmap: all 154 lesson file names were compared against every lesson file name in `Roadmap.md`. Exact matches: 0. Near matches (similarity 0.80 or higher): 0.
- Structural problems found by the build script: 0.
- Topic-level overlap check: the Roadmap text was searched for Gymnasium, Stable-Baselines, DQN, PPO, SAC, MCTS, AlphaZero, MuZero, multi-agent, offline RL, ReAct, the Model Context Protocol, LangGraph, world models, Dreamer, durable execution and sandboxing. None appear as lessons, so G4 teaches them for the first time. The Roadmap does contain Stage 5B RL foundations, bandits and off-policy evaluation, Stage 5C RL for reasoning and post-training, and Stage 3 agent-workflow graphs and state machines, which G4 references and extends and does not reteach.
- Verified by web search on the build date (2026-10-26): Anthropic donated the Model Context Protocol to the Agentic AI Foundation, a directed fund under the Linux Foundation, on 9 December 2025; AutoGen is in maintenance mode with Microsoft Agent Framework as its successor (reported as generally available in April 2026), and the AG2 fork continues; tau-bench reports pass^k reliability over repeated trials; GAIA, OSWorld, WebArena and SWE-bench Verified are real agent benchmarks with the task types described; Stable-Baselines3 appears actively released.
- Reported but not confirmed: whether the A2A agent protocol is governed by the Linux Foundation was not resolved by search; the status of SWE-bench Verified as a recommended benchmark is disputed (one source says it was deprecated for contamination, which was not confirmed), so lesson 16-06 must check the current status; benchmark score figures conflict across sources and none are quoted in this plan; the maintenance status of CleanRL, TorchRL, PettingZoo and rliable was not confirmed and is required in the register; the dates of AutoGen's move to maintenance mode differ between sources.
- Not verified: library, framework, model and benchmark versions, which change quickly; licences and terms (Atari ROMs, MuJoCo, datasets, model APIs); API prices, which must be recorded with their source and date.
- Not verified by execution: no code in this plan has been run. Project pass gates are acceptance criteria to be met when the projects are built.
- Safety note: module 17 and several agent projects involve attacks, code execution and tool access. Every such project specifies an isolated environment, fake data or a test mailbox, and must be carried out only on systems and accounts you own.
- Repository safety: this build created only this file; no existing file or folder was created, changed or deleted by it.
