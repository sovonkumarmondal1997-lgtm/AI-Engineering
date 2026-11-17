# PROMPT — Generate `SYLLABUS-Reinforcement-Learning-Foundations.md` (Stage 5B, module S5B-13)

> Paste everything between `=== BEGIN PROMPT ===` and `=== END PROMPT ===` into a long-context LLM. The output is large, so use the **Delivery Protocol** (Section 13): the model delivers numbered parts and you type `continue` between parts. Save the concatenation as `SYLLABUS-Reinforcement-Learning-Foundations.md` in `Stage 5B — Advanced Machine Learning/13-Reinforcement-Learning-Foundations/`. Then split it into the target files listed in Section 2.

=== BEGIN PROMPT ===

# 1. ROLE

You are a **Senior Machine Learning Engineer with MLOps expertise and 15 years of industry experience**. You have seen reinforcement-learning projects fail in predictable ways: an agent that "learned" by exploiting a bug in the simulator's reward; a reward written to proxy a goal, optimised until the proxy and the goal parted ways; a learning curve from one lucky seed presented as the algorithm's performance; an evaluation that reused the training environment's random seed so the agent had memorised the trajectory; a Q-table that diverged once a function approximator replaced it; a policy-gradient run whose variance was so high that "improvement" was noise; a discount factor chosen because it worked, with the horizon of the real problem never examined; an agent trained against a simulator whose dynamics differed from production in exactly the places that mattered; a "PPO" run whose result depended on implementation details nobody reported; an offline log of a deployed policy used to train a new policy with no thought for what the log never explored; an exploration scheme that was safe in simulation and unsafe in the world. You teach the way you work: **first ask whether the problem is really sequential, whether a simpler method (supervised learning, a bandit, a rule, an optimiser) would do; define the MDP precisely — states, actions, transitions, rewards, discount, horizon — and say which parts are known and which are sampled; solve small problems exactly so you have an oracle; test every learning algorithm against that oracle; evaluate over many seeds with held-out evaluation episodes and report the spread; read the reward as the specification it is and ask how it can be gamed; and never present a result you cannot reproduce from a seed.**

You are also a careful technical author. You never invent a function, signature, default, version, statistic, citation, or **claim about how well any RL method performs in general, "RL achieves X" figure presented as fact, claim about how any real company, robotics team, or game system uses RL, general ranking of algorithms ("PPO beats DQN", "policy gradients are better than value methods"), claim that an algorithm "converges" without stating the conditions (tabular, step-size schedule, exploration, ergodicity), claim of safety, legal, or regulatory sufficiency, or rule-of-thumb value (discount 0.99, learning rate, epsilon schedule, PPO clip 0.2, GAE lambda 0.95) as a law**. When unsure, say so and mark it `[VERIFY]`; practitioner opinion and rules of thumb are marked `[JUDGEMENT]` or `HEURISTIC`.

# 2. TASK

Produce **one complete learning syllabus with full teaching content** for the folder:

`Stage 5B — Advanced Machine Learning / 13-Reinforcement-Learning-Foundations/` (module code **S5B-13**, the **foundations of reinforcement learning as an engineering discipline: MDPs and Bellman equations; value and policy iteration; Monte Carlo and temporal-difference learning; Q-learning and function approximation; policy gradients and REINFORCE; actor-critic methods and PPO intuition; and reward design, exploration, and RL in practice**).

Output file name: **`SYLLABUS-Reinforcement-Learning-Foundations.md`**, saved inside that folder.

All code, labs, worked examples, and the projects are in **Python** (NumPy-centred; SciPy, pandas, scikit-learn and pytest as helpers). **Environments are written by the learner from scratch** (a small `Env` interface with `reset(seed)`/`step(action)` returning next state, reward, terminated, truncated, info, in the style of Gymnasium but self-contained): tabular gridworlds (with slippery transitions, cliffs, and walls), a multi-armed/contextual bandit, a small inventory or queueing MDP, a chain/"river-swim" exploration problem, and a continuous-state cart-pole-like task written in NumPy. **Gymnasium is an optional cross-check, never required.** The learner implements **from scratch, as spec-literal references, and checks against exact solutions and, where noted, library behaviour**: an MDP container with validators; an exact policy-evaluation solver (linear system) and the Bellman optimality operator; value iteration and policy iteration; first-visit/every-visit Monte Carlo prediction and control; TD(0), n-step TD, SARSA, expected SARSA, and Q-learning, with eligibility traces (TD(λ)) as an extension; linear and small-neural-network function approximation in NumPy with semi-gradient updates, plus a demonstration of the **deadly triad** divergence on a planted counter-example; REINFORCE with and without a baseline; one-step actor-critic and generalised advantage estimation; the PPO clipped objective as a function with a gradient check (**no large-scale PPO training**); and an RL experiment harness with seed handling, learning curves, evaluation episodes, confidence intervals, and reward-hacking tests. See Section 3.

Teach, **one after another, from beginner to advanced**, these units in this exact order. Each unit maps to a file later written from this syllabus (all currently empty; the tree below is the source of truth):

| # | Unit | Target file |
|---|---|---|
| 0 | Module orientation | `README.md` |
| 1 | MDPs and Bellman equations | `01-mdps-and-bellman-equations.md` |
| 2 | Value and policy iteration | `02-value-and-policy-iteration.md` |
| 3 | Monte Carlo and temporal-difference learning | `03-monte-carlo-and-temporal-difference-learning.md` |
| 4 | Q-learning and function approximation | `04-q-learning-and-function-approximation.md` |
| 5 | Policy gradients and REINFORCE | `05-policy-gradients-and-reinforce.md` |
| 6 | Actor-critic and PPO intuition | `06-actor-critic-and-ppo-intuition.md` |
| 7 | Reward design, exploration, and RL in practice | `07-reward-design-exploration-and-rl-in-practice.md` |
| 8 | Practice questions | `practice-questions.md` |
| 9 | Projects index | `Projects/README.md` |
| 10 | Project 1: tabular Q-learning agent | `Projects/01-tabular-q-learning-agent.md` |
| 11 | Project 2: policy-gradient agent | `Projects/02-policy-gradient-agent.md` |

Tree (source of truth):

```
13-Reinforcement-Learning-Foundations/
├── Projects/
│   ├── 01-tabular-q-learning-agent.md
│   ├── 02-policy-gradient-agent.md
│   └── README.md
├── 01-mdps-and-bellman-equations.md
├── 02-value-and-policy-iteration.md
├── 03-monte-carlo-and-temporal-difference-learning.md
├── 04-q-learning-and-function-approximation.md
├── 05-policy-gradients-and-reinforce.md
├── 06-actor-critic-and-ppo-intuition.md
├── 07-reward-design-exploration-and-rl-in-practice.md
├── README.md
└── practice-questions.md
```

Do not add, rename, or merge files. `PROMPT-…md` is this prompt and is not part of the syllabus.

# 3. LEARNER AND CONTEXT

- **Learner:** an aspiring Senior Applied AI / ML Engineer who has finished Stages 0–4B, **all of Stage 5A**, and `../00-Stage-Overview/` to `../12-…` of 5B (the 5B protocol card; validation and planted-truth evaluation (5B-01); uncertainty (5B-02); thresholds and decisions under cost (5B-03); calibration (5B-04); time-aware evaluation (5B-08); recommendation, exposure bias, and off-policy estimators (5B-09); causal inference, **bandits and off-policy evaluation (5B-10, Unit 9)**; label scarcity (5B-11); graph ML (5B-12)). They know probability, expectation, conditional expectation, Markov chains, linear algebra, gradient descent, and logistic regression. They have **not** yet studied deep learning in depth (Stage 5C): **teach function approximation with linear models and tiny NumPy networks; name DQN, deep policy-gradient stacks, replay buffers, and large-scale PPO as clearly labelled previews with `[VERIFY]` citations**.
- **Already taught — link, never re-teach:** probability, expectation, variance, conditional expectation, Markov chains and stationary distributions (Stage 4B); gradient descent and the chain rule (Stage 4B); linear systems (Stage 4B); logistic/softmax regression (5A); the bootstrap and corrected tests (5B-01); **bandits, exploration–exploitation basics, and off-policy estimators — importance sampling, doubly-robust ideas (5B-10 Unit 9; 5B-09)** — link, then extend to sequential settings only where needed. Reference them by exact folder/file names from the repository tree; never invent a path. If unsure a path exists, write `[VERIFY path]`.
- **Environment:** Python 3.10+, NumPy, SciPy, pandas, scikit-learn, pytest, matplotlib (optional), Gymnasium (optional cross-check). No network at run time, no downloaded environments, datasets, or models, no paid APIs, no GPU. **Every environment is generated by the harness with a known exact solution** (computed by value iteration or a linear solve) so every learning curve can be compared with the optimum.
- **Time:** assume 6–8 hours per unit plus the projects; mark every time figure `[ASSUMPTION]`.

# 4. TEACHING MODEL — THE FOUR LEVELS (UNITS 1–7, 10, 11)

Each of these units progresses through **exactly these four levels** with identical headings.

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner — Foundations | States the MDP, computes returns and values by hand on a tiny problem, and runs the basic algorithm on a toy environment. |
| **L2** | Intermediate — Working Practice | Implements the algorithm unaided, checks it against the exact solution, tunes it, and avoids the classic failure modes. |
| **L3** | Advanced — Engineering Rigor | States convergence conditions and acceptance criteria as checkable properties, measures variance across seeds, justifies design decisions, defends trade-offs. |
| **L4** | Expert — Mastery and Teaching Others | Diagnoses failures in others' RL code, rewards, and evaluations; decides whether RL is the right tool; could coach a peer. |

Units 0, 8, and 9 use their own structures (Sections 6–8).

# 5. MANDATORY STRUCTURE FOR UNITS 1–7, 10 AND 11

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
- Measurement method (what to measure; how to avoid fooling yourself: seeds, evaluation episodes, baselines)
- Exercise requiring a defended justification or counterexample

### N.6 Level 4 — Expert
- Failure scenarios and diagnosis (symptom → hypothesis → test → root cause → fix → prevention)
- Adversarial situations specific to the unit (see Section 6)
- Automation (aggregate verification commands, regression guards, consistency checks)
- Coaching: reviewing a peer's MDP definition, reward, or learning-curve report with evidence-based feedback
- Edge cases and library differences (Gymnasium `terminated` vs `truncated` semantics, seeding API, NumPy random generator behaviour, float32 vs float64)

### N.7 Engineering lens
(Where this fails in real ML engineering — verifiable failures only, never a company claim or failure-rate statistic. Failure modes, blast radius, cost; simulator fidelity, reproducibility, logging, safe rollout, offline vs online data.)

### N.8 Integrity lens
(Measurement risks: single-seed curves, evaluating on the training seed, tuning on evaluation episodes, reward edited after seeing results, reporting the best run, cherry-picked environments, copying notebooks, AI-assistance disclosure. Controls, each verifiable by a command, test, or written check.)

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

- **The MDP card** (one per environment): states, actions, transition model (known/sampled; stochasticity), reward function and **the behaviour it is meant to encourage and how it could be gamed**, discount factor and **the horizon it implies**, episodic vs continuing, terminal vs time-limit truncation, start-state distribution, observability (is the state really Markov?), and the **exact optimum** (value, policy) with how it was computed.
- **The RL experiment card** (one per experiment): environment and MDP card; algorithm and hyperparameters (and how tuned — on a **separate tuning set of seeds**, never on the reporting seeds); number of independent training seeds (≥ 20 for tabular, ≥ 10 for function-approximation runs; quick mode ≥ 5); **evaluation protocol** (greedy/deterministic policy, evaluation episodes drawn from fresh seeds not used in training, number of episodes, frequency); metrics (return, regret against the exact optimum, sample efficiency, stability); aggregation (mean, median, interquartile range, bootstrap interval across seeds); planted-truth check; decision.
- **Evaluation hygiene rules:** (1) report the **spread across training seeds**, not only a mean; (2) evaluation uses separate, fixed seeds and a separate environment instance; (3) tune on tuning seeds, report on reporting seeds; (4) always compare to an **exact solution, a random policy, and a simple heuristic/baseline policy**; (5) report **both** returns and **regret/optimality gap** where the optimum is known; (6) state the number of environment steps used; (7) never modify the reward or environment after seeing results without recording it as a new experiment; (8) every learning curve states what is on the x-axis (steps, episodes, updates).
- **Terminology convention:** `terminated` (true MDP terminal) vs `truncated` (time limit; bootstrap through it) are distinguished everywhere; confusing them is a defect and the syllabus must show the bias it causes.
- **Seed convention:** `SeedSequence` with named spawn keys for environment, agent, and evaluation streams; results independent of `n_jobs`.

## Unit 0 — Module orientation (`README.md`)

What RL is and is *not* (a framework for sequential decision-making under uncertainty with delayed reward); **the decision map** (supervised learning / bandit / off-policy evaluation / planning with a known model / RL — with the data, simulator, risk, and cost required at each); how this module connects to bandits (5B-10), causal/off-policy evaluation (5B-10, 5B-09), and the later deep-RL and LLM-alignment topics (Stage 5C and beyond, named as previews only); prerequisites; the MDP card, the RL experiment card, and evaluation hygiene rules; how units connect (running example reused across units); what is out of scope; safety notes (reward specification risk, safe exploration, simulation-to-real gap, human impact); how to use the evidence log. Not four-level; ≤ 2 pages equivalent plus the decision-map diagram.

## Unit 1 — MDPs and Bellman equations

- **L1:** the agent–environment loop; state, action, reward, transition, episode; return and **discounting** (what γ means and the horizon it implies, ≈ 1/(1−γ) as a **HEURISTIC** with a derivation of when it is exact); policies (deterministic/stochastic); a **tiny MDP by hand** (a 3-state chain and a 4×4 gridworld); computing returns for a trajectory; **the state-value function *v_π* and action-value function *q_π*** defined; the Markov property and what breaks when it fails.
- **L2:** the **Bellman expectation equations** derived in full for *v_π* and *q_π*; **policy evaluation as a linear system** (*v = r_π + γP_π v → v = (I − γP_π)⁻¹ r_π*) implemented and checked by enumeration on a tiny MDP; the **Bellman optimality equations** for *v\** and *q\**; optimal policies from *q\**; the MDP container with validators (rows of *P* sum to 1, rewards finite, γ ∈ [0,1), terminal handling); a gridworld, a slippery gridworld, a cliff, and an inventory MDP built as running examples with **known optima**.
- **L3:** **proofs (written in full):** the Bellman expectation operator and optimality operator are **γ-contractions in the sup-norm** and hence have unique fixed points (Banach); existence of a deterministic optimal stationary policy stated and cited (`[VERIFY]`) with the conditions; policy-improvement theorem proved; the **performance-difference lemma** stated and proved (or cited) as the tool used later for policy gradients; episodic vs continuing formulations, average-reward formulation named only, with citation; **discount as modelling choice vs as a convergence device**; partial observability (POMDP) named as a boundary with a concrete example of non-Markov state and the "state augmentation" fix; reward shaping and **potential-based shaping preserves optimal policies** (stated, proved in the tabular case, cited `[VERIFY]`).
- **L4 adversarial situations:** γ = 1 on a continuing task; a "state" that omits velocity so the problem is non-Markov; a reward that pays for activity rather than outcome; terminal states with nonzero value leaking through the bootstrap; time-limit truncation treated as terminal; a transition matrix whose rows don't sum to 1; a policy-evaluation solve with a near-singular system.
- **Running example for Units 1–7:** a **family of small environments with exact solutions** (gridworld with slip probability and a cliff; a 6-state "river-swim" exploration chain; a small inventory MDP; a continuous-state cart-pole-like task) used throughout, with the exact optimum recorded in the MDP card.

## Unit 2 — Value and policy iteration

- **L1:** dynamic programming idea (known model, solve exactly); iterative policy evaluation by hand on the gridworld for 2–3 sweeps; greedy policy improvement; why alternating the two works (intuition).
- **L2:** **iterative policy evaluation**, **policy iteration**, **value iteration** (and Q-value iteration) implemented from scratch with stopping criteria and a check against the exact linear-solve; **in-place (Gauss–Seidel) vs synchronous** sweeps; the greedy-policy tie-breaking rule and its effect; convergence plots (error vs sweep); a **known-model planning** example on the inventory MDP (policy compared with a simple heuristic, e.g. an (s,S) rule); **asynchronous DP** and prioritised sweeping named with a short implementation.
- **L3:** **convergence rates**: value iteration's *γ^k* geometric rate and the error bound relating Bellman residual to distance from *v\** (derive: ‖v_k − v\*‖∞ ≤ γ/(1−γ)‖v_k − v_{k−1}‖∞) and its use as a **stopping criterion** with a **policy-extraction error** bound `[VERIFY]`; policy iteration's finite convergence and typical iteration count (measured, **HEURISTIC**); **generalised policy iteration (GPI)** as the unifying pattern used by every later unit; cost per sweep (*O(|S|²|A|)* dense vs sparse); curse of dimensionality (measure state-space growth); **model error**: how errors in *P̂* and *r̂* propagate to the policy (simulation-lemma-style bound stated, cited `[VERIFY]`; measured empirically by perturbing a planted MDP); using a **learned/estimated model then planning** (certainty equivalence) and its failure when data are sparse.
- **L4 adversarial situations:** value iteration stopped on an absolute-change threshold with γ near 1 (premature stop); a policy extracted from a not-yet-converged value; wrongly handled terminal states; a model estimated from too few transitions then planned on as if exact; an (s,S) heuristic beating a "solved" policy because the model was wrong; dense iteration on a state space too large for memory.

## Unit 3 — Monte Carlo and temporal-difference learning

- **L1:** learning without a model: sample episodes; **Monte Carlo prediction** by hand (average returns); **TD(0)** by hand (bootstrapping: update toward *r + γV(s′)*); why TD can learn online and from incomplete episodes; the **bias–variance contrast** between MC and TD (intuition).
- **L2:** first-visit and every-visit MC prediction; MC control with exploring starts and with **ε-soft/ε-greedy policies**; **TD(0) prediction**; **on-policy TD control: SARSA**; **expected SARSA**; **n-step TD** and **TD(λ)** with eligibility traces (forward view and backward view, shown equivalent in the tabular offline case on a tiny example); step-size schedules (constant vs decaying); every algorithm checked against the **exact *v_π* / *q\**** from Unit 2; learning curves over ≥ 20 seeds with spread.
- **L3:** **convergence conditions**: tabular TD(0) and SARSA convergence under step-size conditions (Robbins–Monro: Σα = ∞, Σα² < ∞) and sufficient exploration (GLIE) — **stated precisely and cited `[VERIFY]`; the stochastic-approximation argument sketched, not claimed beyond its conditions**; **bias and variance of MC vs TD, measured empirically** on a planted problem (the batch-TD "certainty-equivalence" result stated and demonstrated on a tiny dataset, cited `[VERIFY]`); effect of **γ, α, ε, λ** (sensitivity grid over seeds; no setting wins everywhere); **on-policy vs off-policy evaluation with importance sampling** (ordinary vs weighted; variance explosion over long horizons — link 5B-10/5B-09) with a measured demonstration; **truncation vs termination bias** reproduced (bootstrapping through a time-limit vs treating it as terminal); initial-value optimism as exploration.
- **L4 adversarial situations:** MC on a task with very long or non-terminating episodes; step-size too large (divergence) or decaying too fast (stuck); ε never decayed so the learned policy is evaluated under exploration noise; evaluation using the exploratory policy; terminal-state bug that leaks value; reporting a curve from one seed; importance-sampling ratios exploding on a 200-step horizon.

## Unit 4 — Q-learning and function approximation

- **L1:** **Q-learning** (off-policy TD control): the update *Q(s,a) ← Q(s,a) + α[r + γ max Q(s′,·) − Q(s,a)]*, a hand-run on the gridworld; why it learns the optimal policy while behaving ε-greedily (off-policy); the **cliff-walking** contrast with SARSA (explain, then measure).
- **L2:** a tabular **Q-learning agent** in NumPy checked against *q\** from value iteration; exploration schedules (ε-greedy, decaying, Boltzmann/softmax, optimistic initialisation); **double Q-learning** and the **maximisation bias** reproduced on a planted counter-example; **function approximation** — state features, **linear semi-gradient TD/Q-learning**, tile coding or radial basis features on the cart-pole-like task, and a small NumPy neural Q-function; a **replay buffer** and **target network** explained and implemented minimally (previews of DQN, citing `[VERIFY]`, no deep-RL training at scale).
- **L3:** **convergence of Q-learning** (tabular; conditions; cited `[VERIFY]`); **the deadly triad** — function approximation + bootstrapping + off-policy training can **diverge** — shown on a planted counter-example (a small Baird-style example written by the learner; the original is cited `[VERIFY]`) and what mitigations do (on-policy training, residual/gradient methods named, target networks, regularisation) with measured effects; **what linear function approximation can and cannot represent** (aliasing; bias of the fixed point — stated with citation `[VERIFY]`); **overestimation** from the max operator measured; sample-efficiency and stability measurement (≥ 10 seeds; median and IQR); hyperparameter sensitivity; the role of feature scaling; **exploration is not solved by ε-greedy**: river-swim shows ε-greedy failing and an optimism/count-based bonus succeeding (measure).
- **L4 adversarial situations:** a Q-table agent reported as "solved" with evaluation under the ε-greedy policy; Q-values diverging after switching to a function approximator; overestimation hidden by a positive reward scale; a bug where the target uses the online parameters and the update propagates through the target; reward scale changes breaking hyperparameters; a function approximator that cannot represent the optimal value and is blamed on "needs more training".

## Unit 5 — Policy gradients and REINFORCE

- **L1:** why learn the policy directly (stochastic policies, continuous actions, simple structure); a softmax policy over actions; the idea "make good actions more likely" and the **score function** in words; one REINFORCE update by hand on a tiny bandit.
- **L2:** the **policy-gradient theorem** (statement and a derivation of the log-derivative trick for the episodic case); **REINFORCE** in NumPy with a softmax (discrete) and Gaussian (continuous) policy; **return-to-go** vs full-return weighting (derive why causality allows return-to-go); **baselines** (constant and learned value baseline) and **why a baseline does not bias the gradient** (proved) but cuts variance (measured); **gradient check against finite differences** on a tiny MDP; comparison with Q-learning on the same environment; entropy regularisation.
- **L3:** **variance of the gradient estimator**: measured as a function of horizon, baseline, batch size, and reward scale over ≥ 10 seeds; **natural-gradient and trust-region ideas** introduced as the motivation for the next unit (Fisher information, KL-constrained update — stated, cited `[VERIFY]`; no full derivation of TRPO); policy parameterisation and **parameter-space vs policy-space step sizes** (why equal parameter steps are unequal policy changes — show on a softmax); **off-policy policy gradients** and importance weights named with their variance problem; **continuous actions** and the Gaussian policy's std-collapse failure mode; **comparison across the value/policy divide** as evidence, never as a ranking; the **performance-difference lemma** (Unit 1) used to explain why a policy-gradient step improves in expectation under conditions.
- **L4 adversarial situations:** reward scale changes making the same code diverge; no baseline and long horizons so the "learning curve" is noise; log-prob computed on the wrong action (sampled with one policy, scored with another); sampled-action gradient with a stale policy; entropy collapse; evaluation using sampled actions vs greedy not stated; a reported improvement within the seed-to-seed spread.

## Unit 6 — Actor-critic and PPO intuition

- **L1:** the idea: an **actor** (policy) and a **critic** (value) learn together; the critic's TD error as a low-variance signal for the actor; one actor-critic update by hand.
- **L2:** **one-step and n-step actor-critic** in NumPy on the gridworld and the cart-pole-like task; the **advantage function** *A = Q − V* and its estimate by the TD error; **generalised advantage estimation (GAE)** with λ as a bias–variance dial (derive the form; implement; verify against explicit n-step returns on a tiny trajectory); shared vs separate actor/critic parameters; the critic's **learning rate relative to the actor's**.
- **L3:** **PPO intuition**: the problem (large policy updates destroy performance; sample reuse requires importance ratios); the **probability ratio *r_t(θ) = π_θ(a|s)/π_old(a|s)***; the **clipped surrogate objective** *L^{CLIP}* implemented as a function and **gradient-checked**, with a table of its gradient in each regime (advantage sign × ratio region); what clipping does and does not guarantee (**it is a heuristic trust region, not a guarantee** — measured); the role of **multiple epochs and mini-batches** and the value-loss and entropy terms; what implementation details matter in practice (advantage normalisation, observation normalisation, learning-rate annealing, gradient clipping, orthogonal initialisation — named and cited `[VERIFY]`, with the explicit statement that reported PPO results are sensitive to such details); TRPO and KL-penalty variants named; **no end-to-end deep PPO training**: previews of PPO in RLHF/LLM post-training are labelled `[VERIFY]` and out of scope.
- **L4 adversarial situations:** a critic that lags so badly the advantages are noise; ratio computed without detaching the old log-probs; advantages normalised across the wrong axis; clipping applied to the wrong side for negative advantages; value targets computed with a bootstrapped value across a truncation; "PPO" results quoted without the implementation details that produced them; GAE with a mishandled episode boundary.

## Unit 7 — Reward design, exploration, and RL in practice

- **L1:** the reward is the specification; how rewards go wrong (a list of small constructed examples: loop-for-points, reward for activity, reward leakage); sparse vs dense reward; exploration vs exploitation recalled; why simulators matter.
- **L2:** **reward design practice**: writing the reward from the objective, **reward-hacking tests** (adversarial policies that maximise the proxy reward; implemented against a gridworld with a planted loophole and detected with a held-out true-objective metric); **potential-based shaping** (Unit 1) applied and verified to preserve the optimal policy, versus a naive shaping that changes it; **exploration methods**: ε-greedy, optimism/count bonuses, Thompson sampling for bandits (link 5B-10), and intrinsic-motivation named only; **curriculum** and start-state design; **safe-exploration constraints** as simple action masks and a constrained-MDP framing (named, cited `[VERIFY]`).
- **L3:** **RL in practice**: when **not** to use RL (decision checklist: Is the problem sequential? Is there a simulator or safe data? Is a bandit, supervised model, or optimiser enough? Is the reward measurable? What does failure cost?); **simulation-to-real gap** and **domain randomisation** (named; tested in miniature by perturbing the planted environment's dynamics at evaluation time and measuring policy degradation); **offline RL and off-policy evaluation**: logged-data limits, **coverage/support** of the behaviour policy, distribution shift, importance-sampling and doubly-robust estimators for policies (link 5B-10 Unit 9 and 5B-09), why offline RL is hard (named; one tiny demonstration of an unsupported action having an unreliable value); **evaluation and reproducibility**: seed variance, implementation sensitivity, statistically honest comparison (bootstrap/rliable-style aggregate metrics named and cited `[VERIFY]`); logging, checkpointing, deterministic replay, and **MLOps for RL** (experiment tracking, environment versioning, policy registry, canary/shadow rollout of a policy, monitoring for reward and state drift, rollback); **safety and human impact** (reward misspecification harms, feedback loops from deployed policies — link 5B-09/5B-10); **alignment-adjacent previews** (RLHF, reward models) as one-line `[VERIFY]` pointers only.
- **L4 adversarial situations:** an agent that learns to exploit a simulator bug; a reward model that is gamed; a "success" in simulation that fails under small dynamics shift; an offline policy that selects actions the log never contained; a deployed policy that changes the data it will later be trained on; an RL solution where a tuned bandit or rule would have matched; a result presented without seed spread.

## Unit 8 — Practice questions (`practice-questions.md`) — see Section 7

## Unit 9 — Projects index (`Projects/README.md`) — see Section 8

## Unit 10 — Project 1: tabular Q-learning agent (`Projects/01-tabular-q-learning-agent.md`) — see Section 9

## Unit 11 — Project 2: policy-gradient agent (`Projects/02-policy-gradient-agent.md`) — see Section 9

# 7. UNIT 8 — PRACTICE QUESTIONS (REQUIREMENTS)

At least **80 questions**, tagged by unit and level (L1–L4) and type, with a worked answer key: conceptual short answer; MCQ with "why the wrong answers are tempting"; **derivations and proofs** (Bellman expectation and optimality equations; policy evaluation as a linear system; contraction of the Bellman operators; policy-improvement theorem; value-iteration residual-to-error bound; potential-based shaping preserves optimal policies; the log-derivative trick and the policy-gradient theorem in the episodic case; a baseline does not bias the gradient; GAE as a λ-weighted sum of n-step advantages; the gradient of the PPO clipped objective in each regime); **hand calculations** (a Q-learning, SARSA, and TD(0) update on a tiny table; a REINFORCE update on a 2-armed bandit; returns and GAE on a 5-step trajectory; policy iteration on a 3-state MDP); **code-reading and bug-finding** (terminal vs truncation handled incorrectly; evaluation under the training seed; target-network update bug; ratio without detach; log-prob of the wrong action; reward-hacking loophole; ε never decayed; off-by-one in return-to-go; discounting applied inconsistently); **design-a-protocol** questions (given a decision problem, data, simulator availability, and risk, decide whether RL is warranted and defend the evaluation, baselines, and rollout plan); 5 **interview-style scenario** questions with senior answers; 5 **negative-result** questions ("show a case where Q-learning/policy gradient/shaping fails"). Keys give the reasoning; every numeric key is verified by an independent computation (second method, exact solve, or enumeration on a tiny MDP).

# 8. UNIT 9 — PROJECTS README (REQUIREMENTS)

Explain the projects' purpose; prerequisites; the deliverable layout (`rlfound/` package with `envs/`, `agents/`, `eval/`; `tests/`, `reports/`, `results/`); the grading rubric as **checkable properties** (not subjective); the reproducibility contract (`make quick`, `make full`, root seed, hashes of config and outputs); the integrity rules from Section 6; how the projects connect (Project 2 reuses Project 1's environments and harness; both reuse the exact solvers of Units 1–2); how they connect to other modules (bandits and off-policy evaluation `../10-…`, uncertainty `../02-…`, calibration `../04-…`, capstones `../15-…`, Stage 5C deep RL as a preview); and a short "how to present results to a product or operations stakeholder" template (the objective, the baseline, the improvement with spread, the risks, the assumptions, what would make RL the wrong tool).

# 9. UNITS 10 AND 11 — THE TWO PROJECTS (REQUIREMENTS)

## Unit 10 — `Projects/01-tabular-q-learning-agent.md` — builds the **`rlfound`** tabular core

**Goal:** an honest, reproducible tabular Q-learning (and SARSA/expected-SARSA) study that **matches the exact optimum on small MDPs, shows where it fails, and is evaluated rigorously.**

Required:

1. **Environments** (self-written, `reset(seed)`/`step` with `terminated`/`truncated`): a slippery gridworld with a cliff, a river-swim exploration chain, and a small inventory MDP, each with an **MDP card and an exact solution** (value iteration + exact policy evaluation).
2. **Agents:** Q-learning, SARSA, expected SARSA, double Q-learning, with configurable exploration (ε-greedy with schedules, optimistic initialisation, a count-based bonus) and step-size schedules; precondition checks (valid action masks; no mutation of inputs).
3. **Evaluation protocol:** separate evaluation seeds, greedy evaluation, ≥ 20 seeds (`--quick` ≥ 5), regret against the exact optimum, learning curves with interquartile range and bootstrap intervals, sample-efficiency table (steps to within ε of optimal), and baselines (random policy, simple heuristic, exact optimum).
4. **Required experiments:** (a) agreement with *q\** on the gridworld; (b) SARSA vs Q-learning on the cliff (behaviour and online return, explained); (c) maximisation bias and double Q-learning; (d) exploration failure and fix on river-swim; (e) terminal-vs-truncation bias reproduced and fixed; (f) a hyperparameter-sensitivity grid; (g) a **reward-hacking test** with a planted loophole.
5. **Engineering deliverables:** `pytest` suite with oracle tests (exact-solution agreement within stated tolerances; invariants such as the Bellman optimality residual of the learned Q on visited states) that **pass on the reference and fail on deliberately broken variants** (terminal bug; target uses wrong max; ε never decays); deterministic run log; config and result hashing; checkpointing; a **decision memo** (≤ 2 pages) with the MDP card, RL experiment card, results with spread, risks, and when tabular RL is (not) appropriate.
6. **Acceptance criteria** as commands and expected checks; self-review checklist; stretch goals (TD(λ) traces; prioritised sweeping; a model-based Dyna-style agent compared on sample efficiency).

## Unit 11 — `Projects/02-policy-gradient-agent.md` — builds the **`rlfound`** policy-gradient core

**Goal:** an honest, reproducible policy-gradient study — **REINFORCE with and without a baseline, and a one-step actor-critic with GAE** — on the gridworld and on a NumPy continuous-state task, **with measured variance and a gradient check**.

Required:

1. **Environments:** reuse the Unit 10 gridworld and add a **cart-pole-like continuous-state task** in NumPy with a documented MDP card (dynamics, termination, truncation, reward); an exact-optimum surrogate where available (discretised value iteration as an **approximate** reference, labelled as such) and a hand-written heuristic controller as the baseline.
2. **Agents:** softmax-linear and small NumPy-network policies; Gaussian policy for a continuous-action variant; REINFORCE (return-to-go), REINFORCE with baseline, one-step/n-step actor-critic with GAE(λ); an **entropy bonus**; a **PPO-clip surrogate as a function with gradient check** (training with it optional stretch, small scale).
3. **Verification:** **finite-difference gradient checks** of the policy-gradient estimator on a tiny MDP; unbiasedness check of the baseline versions against the exact gradient (computed by enumeration on a tiny MDP) over many samples; GAE checked against explicit n-step returns.
4. **Evaluation protocol:** as the RL experiment card; ≥ 10 seeds (`--quick` ≥ 5) for the continuous task, ≥ 20 for the gridworld; median and IQR with bootstrap intervals; measured **gradient-estimator variance** versus baseline, horizon, and reward scale; sample-efficiency comparison with the Unit 10 tabular agent on the shared gridworld (**as evidence, not a ranking**).
5. **Stress scenarios (≥ 4):** reward-scale change; longer horizon; dynamics perturbation at evaluation time (sim-to-real in miniature); entropy collapse; a deliberately mis-specified reward (reward hacking) with a held-out true-objective metric.
6. **Engineering deliverables:** `pytest` oracle tests that **pass on the reference and fail on broken variants** (wrong-action log-prob; missing detach; no return-to-go; truncation treated as terminal; ratio clip on the wrong side); deterministic run log; hashes; policy checkpoint with a version manifest; a **rollout plan sketch** (shadow evaluation, canary, rollback criteria, monitoring signals); a **decision memo** (≤ 2 pages) with the MDP card, the RL experiment card, results with spread, risks (reward specification, safety), and what would change the recommendation (including "use a simpler method").
7. **Acceptance criteria** as commands and expected checks; self-review checklist; stretch goals (small-scale PPO training with multiple epochs; a learned value baseline with different learning rates; an off-policy evaluation of a logged policy using importance sampling and a doubly-robust estimator, linking 5B-10).

# 10. CODE AND COMMAND RULES (NON-NEGOTIABLE)

1. Every code block states its language and path as a first-line comment (`# File: src/rlfound/agents/qlearning.py`).
2. Every command/snippet is paired with **expected output** labelled "representative — yours will differ in timings, versions, and paths", plus an interpretation.
3. **Code must run** on Python 3.10+ (version differences tagged `[VERSION-SENSITIVE]`), type hints on public functions, shape/dtype annotations, runtime precondition checks (transition probabilities non-negative and rows summing to 1 within tolerance; γ in range; valid state/action indices; episode-length limits; finite rewards; no `NaN` unless stated), and **no mutation of caller inputs (verified by a hash-before/after test)**.
4. Every method and tool has its Method/Tool card before the code; **every experiment ends with an RL experiment card** and **every environment has an MDP card**.
5. Conventions are stated once (Section 6) and applied everywhere; mixing them is a defect.
6. No `==` on floats; tolerances stated and justified; **every algorithm has a spec-literal reference implementation checked against the exact solution (linear solve, value iteration, enumeration) on tiny and random MDPs, including terminal states, absorbing states, γ = 0, a single state, deterministic and fully stochastic transitions, and ties in greedy action selection**; budgets (environment steps × seeds × agents; state-space size for dense tables) are guarded before running.
7. Every worked example and tool has an **independent oracle** (labelled; never importing the function under test; exact, closed-form, enumeration, or planted-truth oracle preferred); tests pass on the reference and fail on a deliberately broken variant.
8. **No unproven claims** about RL performance, convergence beyond stated conditions, algorithm ranking, hiring, interviews, library defaults, hyperparameter "best values", or real systems. Cited-only results are named and tagged `[VERIFY]`.
9. **Proof status is explicit** in every card and in the appendix; every heuristic is labelled `HEURISTIC` with its measured behaviour on the planted environments.
10. Proofs are written in full where a unit requires them; a counterexample is a disproof; agreement on examples is not a proof. Convergence statements always name their assumptions.
11. Library internals (Gymnasium's `terminated`/`truncated` semantics and seeding API; NumPy `Generator` stream behaviour; `scipy.linalg.solve` conditioning) are **not guarantees**: teach the learner to test the behaviour; tag `[VERSION-SENSITIVE]`/`[VERIFY]`.
12. **Resource safety:** step/episode/seed budgets validated and enforced; dense tables sized from state/action counts before allocation; episodes capped; files confined to the project directory; no GPU required.
13. **Security/privacy:** no `pickle`/`eval`/`exec` on untrusted input; strict loaders reject unknown fields and invalid MDP definitions; checkpoints and logs as JSON/`.npz` with shapes, version, and hashes; synthetic environments only; no network at run time.
14. No secrets, paid APIs, or downloaded environments/models; `clean` targets list what they remove and never delete the learner's evidence log or run logs.
15. Every lab ends with cleanup and a stray-file check.
16. Randomness only via `SeedSequence`/`np.random.default_rng(seed)` derived from the recorded root seed with named spawn keys (environment, agent, evaluation streams kept separate); no system-clock reads inside logic; timing only at the CLI edge, reported with spread; results independent of `n_jobs`.

# 11. SCOPE GUARD

Never re-teach Stage 1–4, 5A, or 5B-00 to 5B-12 content (link it; **bandits and off-policy estimators are linked to 5B-10, not re-taught**). Do not teach deep RL (DQN training at scale, deep policy-gradient stacks, SAC/TD3/DDPG, distributed or large-scale PPO), model-based deep RL, multi-agent RL, hierarchical RL, inverse RL, imitation learning in depth, offline RL algorithms (CQL/IQL etc.) beyond naming, game-playing systems, or RLHF/LLM post-training — as one-line previews with `[VERIFY]` citations only (Stage 5C and later). Do not recommend any RL framework or platform as "the best". Do not make claims about robotics, games, trading, or advertising systems in industry.

# 12. AUTHENTICITY, AUDIT, AND VERIFICATION PROTOCOL (MANDATORY)

**All learning content must be audited and verified against authentic sources before final submission.** You act as author, then as an independent auditor of your own work, and you include the audit evidence in the deliverable.

## 12.1 Source hierarchy (every claim traces to a tier)

| Tier | Source type | Examples for this module | Use |
|---|---|---|---|
| **T1** | Official documentation, release notes, standards | Python docs; **NumPy** (`random.Generator`, `linalg`), **SciPy** (`linalg`, `sparse`), **pandas**; **Gymnasium documentation** (environment API, `terminated`/`truncated`, seeding — optional cross-check); scikit-learn docs where used | API behaviour, defaults, versions |
| **T2** | Peer-reviewed papers and established textbooks (cite by title/author/venue/topic, **never invented page numbers or figures**) | Sutton & Barto, *Reinforcement Learning: An Introduction* (2nd ed.); Puterman, *Markov Decision Processes*; Bertsekas, *Dynamic Programming and Optimal Control* and Bertsekas & Tsitsiklis, *Neuro-Dynamic Programming*; Szepesvári, *Algorithms for Reinforcement Learning*; Bellman (1957); Howard (1960) on policy iteration; Watkins & Dayan (1992) on Q-learning; Rummery & Niranjan (1994) on SARSA; Sutton (1988) on TD learning; Singh & Sutton (1996) on traces; van Hasselt (2010) on double Q-learning; Tsitsiklis & Van Roy (1997) on TD with function approximation; Baird (1995) on divergence; Williams (1992) REINFORCE; Sutton et al. (2000) policy-gradient theorem; Kakade & Langford (2002) on approximately optimal approximate RL (performance difference); Kakade (2001) natural policy gradient; Schulman et al. (2015) TRPO and GAE; Schulman et al. (2017) PPO; Ng, Harada & Russell (1999) on potential-based shaping; Mnih et al. (2015) DQN (preview); Henderson et al. (2018) *Deep RL that Matters* and Engstrom et al. (2020)/Huang et al. on PPO implementation details (named, `[VERIFY]`); Agarwal et al. (2021) on statistically reliable RL evaluation (named, `[VERIFY]`); Amodei et al. (2016) *Concrete Problems in AI Safety*; Levine et al. (2020) offline RL tutorial (named, `[VERIFY]`); Pardo et al. (2018) on time limits in RL (named, `[VERIFY]`) | Definitions, methods, equations, known limits |
| **T3** | Reputable university lecture notes and engineering write-ups | Only as a pointer, only if canonical, always `[VERIFY]` | Orientation; never the sole source of a technical claim |
| **T4** | Everything else (blogs, forums, AI output, your own memory) | — | **Never sufficient.** Convert to a derivation, a check, or `[VERIFY]` |

Rules:
1. Every definition, equation, and attributed method cites a T1/T2 source **by name** in the unit's `N.14` and in the appendix source ledger. Paper titles and authors may be given only if you are confident; otherwise write the topic and `[VERIFY]`.
2. **Never fabricate** a citation, DOI, URL, page, figure, benchmark score, or quote. A claim you cannot trace is rewritten as a derivation, replaced by a runnable check against an exact solution, or removed.
3. Numerical statements are either (a) the output of code in the syllabus with a seed, (b) an exact derivation, or (c) cited and `[VERIFY]`.
4. Version-specific API facts name the version checked and are tagged `[VERSION-SENSITIVE]`.

## 12.2 Mandatory multi-pass self-audit (run after drafting, before delivering each part)

- **Pass A — Factual audit:** list every factual claim in the part; assign each a tier and status (PROVED / CITED [VERIFY] / EVIDENCE ONLY / HEURISTIC / JUDGEMENT); fix or remove any with none.
- **Pass B — Mathematical audit:** re-derive every equation, proof, and numeric answer key independently (second method — e.g. exact linear solve against value iteration); check indices, time offsets (*r_{t+1}* vs *r_t*), discount exponents, and signs; verify every hand-calculation by code.
- **Pass C — Code audit:** every snippet is complete, runs as written, has a stated oracle independent of the function under test, and its printed output matches what the code would produce; seeds and budgets present.
- **Pass D — Evaluation-integrity audit:** for every experiment, confirm in writing that evaluation seeds are separate from training and tuning seeds, evaluation is greedy where stated, terminal vs truncation is handled correctly, the exact optimum or baseline is reported, and spread across seeds is shown.
- **Pass E — Over-claim audit:** hunt for universal claims ("always converges", "best", "state of the art", "X% better") and replace with conditional, measured, or cited statements; check every convergence claim names its assumptions.
- **Pass F — Consistency audit:** names, paths, conventions (notation for *s, a, r, γ, π, v, q, A*; time-index convention), seeds, and cross-references match the tree and the other units.
- **Pass G — Safety and integrity audit:** reward-specification risk, safe-exploration notes, resource caps, no network, no secrets, no real-system claims.

## 12.3 Audit artifacts to include inside the syllabus file (final appendices)

- **Appendix A — Source ledger:** every cited work: name, authors, year, tier, what it is used for, `[VERIFY]` flag.
- **Appendix B — Claim ledger:** every non-trivial claim: unit, claim, status, evidence.
- **Appendix C — `[VERIFY]` register:** every unresolved item with exactly how the reader can verify it (which doc or paper, which check).
- **Appendix D — Audit report:** results of Passes A–G per unit (what was found, what was changed), and an honest list of residual risks.
- **Appendix E — Proof and status table; Appendix F — Version and platform notes; Appendix G — Glossary and notation table.**

## 12.4 Trust rules

- Say "I could not verify this" rather than guess. Mark residual uncertainty explicitly; never hide it.
- No claim about the model's own browsing: if you have no tool access to sources, say the citations are from memory, tag each `[VERIFY]`, and list what the human should check first.
- The human operator will perform a final source check; make that easy (Appendix C).

# 13. OUTPUT FORMAT AND DELIVERY PROTOCOL

**Format:** one Markdown document; headings exactly as Section 5; code in fenced blocks with language tags; tables for catalogues; Mermaid for diagrams; no HTML.

**The output is too large for one response.** Deliver in numbered parts:

1. **Part 0:** an outline: unit list with planned sizes, the conventions block and notation table, the running-example specification, the source ledger (draft), and the part plan. Then stop.
2. **Parts 1–N:** one unit per part (Unit 0 and 1 may share; Units 10 and 11 may take two parts each). Each part ends with `PART k/N COMPLETE — audit Passes A–G done — type "continue"`. Never summarise a unit instead of writing it; never truncate with "etc." or "similar to above".
3. **Final part:** Appendices A–G and a **coverage matrix** mapping every bullet in Sections 6–9 to the heading where it is taught.

If a part would be cut off, stop at a clean boundary and say so; resume exactly there on `continue`.

# 14. QUALITY BAR — DEFINITION OF DONE

- [ ] Every unit in Section 2 present, in order, matching the tree; no extra files.
- [ ] Every unit (1–7, 10, 11) has all four levels and every skeleton heading `N.0`–`N.14`.
- [ ] Every Section 6 bullet is taught and appears in the coverage matrix.
- [ ] Every algorithm has a Method/Tool card, a from-scratch reference, an exact-solution oracle, and broken variants that fail the tests.
- [ ] Every experiment has an RL experiment card, separate tuning/reporting/evaluation seeds, ≥ 20 (tabular) or ≥ 10 (function approximation) seeds (quick ≥ 5), spread and intervals, and baselines including the exact optimum where known.
- [ ] Negative results are present: maximisation bias, deadly-triad divergence, ε-greedy exploration failure, policy-gradient variance, reward hacking, terminal-vs-truncation bias.
- [ ] Both projects are complete with stress scenarios, tests, versioned artifacts, rollout sketch, and decision memos.
- [ ] ≥ 80 practice questions with verified keys.
- [ ] All Section 12 audit passes done; Appendices A–G present; every `[VERIFY]` registered; no fabricated citation.
- [ ] No hype, no outcome or hiring claims, no company claims.

# 15. START

Begin with **Part 0** now. Do not ask clarifying questions; record any assumption as `[ASSUMPTION]`.

=== END PROMPT ===

## Notes for the human operator (not part of the prompt)

- **Audit step is yours too.** The prompt makes the model self-audit and emit Appendices A–D, but a model without browsing can only cite from memory. Before accepting the syllabus, work through **Appendix C (`[VERIFY]` register)**: check each cited paper/book against its source, check Gymnasium and NumPy behaviours against the official docs for the versions you install, and run every code block and `pytest` suite. Pay particular attention to every convergence statement (the conditions must be stated) and to the time-index and discount conventions, which are the most common source of silent errors in RL material.
- Split the finished syllabus into the eleven target files listed in Section 2; keep this prompt file alongside.
- If a part comes back truncated or summarised, reply `redo part k in full`.
