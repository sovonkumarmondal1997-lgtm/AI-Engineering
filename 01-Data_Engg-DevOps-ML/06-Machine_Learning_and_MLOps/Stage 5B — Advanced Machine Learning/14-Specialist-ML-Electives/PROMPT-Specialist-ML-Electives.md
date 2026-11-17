# PROMPT — Generate `SYLLABUS-Specialist-ML-Electives.md` (Stage 5B, module S5B-14)

> Paste everything between `=== BEGIN PROMPT ===` and `=== END PROMPT ===` into a long-context LLM. The output is large, so use the **Delivery Protocol** (Section 13): the model delivers numbered parts and you type `continue` between parts. Save the concatenation as `SYLLABUS-Specialist-ML-Electives.md` in `Stage 5B — Advanced Machine Learning/14-Specialist-ML-Electives/`. Then split it into the target files listed in Section 2.

=== BEGIN PROMPT ===

# 1. ROLE

You are a **Senior Machine Learning Engineer with MLOps expertise and 15 years of industry experience**. You have seen specialist-method projects fail in predictable ways: a churn model that treated "not churned yet" customers as non-churners, so the model learned the length of observation rather than risk; a survival model whose censoring was informative (customers who were about to leave were also the ones the system stopped tracking) and nobody asked why; a Kaplan–Meier curve compared across groups with no thought for who was at risk at each time; a Cox model whose proportional-hazards assumption was never checked and whose hazard ratio was reported as one number for an effect that reversed over time; a concordance index quoted as "accuracy" for a model whose calibration was far off; a time-varying covariate that leaked the future into the baseline; a hidden Markov model fitted by EM from one random start and reported as "the" regime structure; a regime label that was a random artefact of initialisation; a Kalman filter whose process and measurement noise were tuned until the plot looked smooth, with a filter that was over-confident and whose innovation statistics were never examined; a linear-Gaussian assumption applied to a clearly nonlinear sensor; a specialist method adopted because it was interesting, when a gradient-boosted model on three well-chosen features would have done the job, and which then took a quarter to put in production. You teach the way you work: **start from the decision and the data-generating situation; name the structure that makes a specialist method appropriate (censoring and time-to-event; latent discrete state; latent continuous state with noisy measurement) and the structure that would make it inappropriate; state every assumption and the check for it; build the simplest credible baseline first; verify each method on simulated data where the truth is known; evaluate with the right metric and a time-correct design; and never present a result you cannot reproduce from a seed.**

You are also a careful technical author. You never invent a function, signature, default, version, statistic, citation, or **claim about how much any specialist method improves on a simpler one in general, "survival models beat classifiers" or "Kalman filters beat moving averages" statement, claim about how any real company, hospital, or lab uses these methods, general ranking of methods, claim that a model's assumption "holds" without the check that was run, claim of medical, clinical, legal, or regulatory validity, or rule-of-thumb value (events-per-variable thresholds, number of HMM states, noise ratios, concordance "good" cut-offs) as a law**. When unsure, say so and mark it `[VERIFY]`; practitioner opinion and rules of thumb are marked `[JUDGEMENT]` or `HEURISTIC`.

# 2. TASK

Produce **one complete learning syllabus with full teaching content** for the folder:

`Stage 5B — Advanced Machine Learning / 14-Specialist-ML-Electives/` (module code **S5B-14**, the **concepts, implementation, evaluation and selection of specialist methods that a generalist ML engineer must recognise and use responsibly: survival analysis (censored time-to-event data); hidden Markov models and Kalman filters (latent-state models for sequences and signals); and a decision framework for selecting specialist methods versus simpler alternatives**).

Output file name: **`SYLLABUS-Specialist-ML-Electives.md`**, saved inside that folder.

All code, labs, and worked examples are in **Python** (NumPy/SciPy/pandas/scikit-learn-centred; **`lifelines`, `scikit-survival`, `statsmodels`, `hmmlearn`, `filterpy`/`pykalman` only as optional cross-checks**, never as the only implementation; the module must run with NumPy/SciPy/pandas/scikit-learn alone). The learner implements **from scratch, as spec-literal references, and checks against exact solutions, simulation truth and (where installed) library behaviour**: a censored time-to-event data container with validators; a **simulator** for survival data (parametric hazards, independent and informative censoring, left truncation, time-varying covariates, competing risks) and for HMM/linear-Gaussian state-space data (with known truth); the **Kaplan–Meier** estimator with Greenwood variance and confidence intervals, the **Nelson–Aalen** estimator, the **log-rank** test, parametric survival fits (exponential/Weibull by maximum likelihood with censoring), a **Cox proportional-hazards** partial-likelihood fit (Breslow/Efron tie handling) by Newton–Raphson with Schoenfeld-residual diagnostics, **time-dependent evaluation** (Harrell's and Uno-style concordance, time-dependent AUC and Brier score with IPCW — small implementations), and **calibration at a horizon**; the **HMM forward, backward, Viterbi and Baum–Welch (EM)** algorithms in log-space/scaled form with multi-start and model-selection by held-out likelihood; the **Kalman filter and RTS smoother** for linear-Gaussian models with innovation diagnostics (NIS/whiteness), noise-parameter estimation (EM or marginal likelihood — small), and an **extended Kalman filter** sketch for a mildly nonlinear model; and a **method-selection harness** that compares a specialist model against a strong simple baseline on planted data. See Section 3.

Teach, **one after another, from beginner to advanced**, these units in this exact order. Each unit maps to a file later written from this syllabus (all currently empty; the tree below is the source of truth):

| # | Unit | Target file |
|---|---|---|
| 0 | Module orientation | `README.md` |
| 1 | Survival analysis concepts | `01-survival-analysis-concepts.md` |
| 2 | Hidden Markov models and Kalman filters (introduction) | `02-hidden-markov-models-and-kalman-filters-introduction.md` |
| 3 | Selecting specialist methods | `03-selecting-specialist-methods.md` |
| 4 | Practice questions | `practice-questions.md` |

Tree (source of truth):

```
14-Specialist-ML-Electives/
├── 01-survival-analysis-concepts.md
├── 02-hidden-markov-models-and-kalman-filters-introduction.md
├── 03-selecting-specialist-methods.md
├── README.md
└── practice-questions.md
```

There is **no `Projects/` folder** in this module: the applied work is carried by **mini-projects inside Units 1–3** (Section 6) and by the module's hands-on labs; the module's integrated capstone work lives in `../15-Stage-5B-Capstones/` and is not part of this syllabus. Do not add, rename, or merge files. `PROMPT-…md` is this prompt and is not part of the syllabus.

# 3. LEARNER AND CONTEXT

- **Learner:** an aspiring Senior Applied AI / ML Engineer who has finished Stages 0–4B, **all of Stage 5A**, and `../00-Stage-Overview/` to `../13-…` of 5B (the 5B protocol card; nested and deployment-matched validation and planted-truth evaluation (5B-01); uncertainty and intervals (5B-02); imbalance, thresholds, and rare-event metrics (5B-03); calibration (5B-04); representation (5B-05); anomaly detection (5B-06); explanation (5B-07); **time-series analysis and forecasting, state and structure, rolling-origin evaluation (5B-08)**; recommendation (5B-09); causal inference, selection bias, and experimentation (5B-10); weak supervision and label noise (5B-11); graph ML (5B-12); reinforcement learning foundations, MDPs and Bellman equations (5B-13)). They know probability, likelihood, maximum-likelihood estimation, the bootstrap, Bayes' rule, Markov chains, linear algebra, Gaussian distributions, and logistic regression. They have **not** yet studied deep learning in depth (Stage 5C): deep survival models, neural state-space models, and deep sequence models are **named previews with `[VERIFY]` citations only**.
- **Already taught — link, never re-teach:** maximum likelihood and Fisher information (Stage 4B/5A); logistic regression and classification metrics (5A); the bootstrap and corrected tests (5B-01); confidence intervals and conformal ideas (5B-02); calibration and reliability diagrams (5B-04); imbalance and thresholds (5B-03); stationarity, autocorrelation, ARIMA and state-space intuition, and rolling-origin evaluation (5B-08); Markov chains and MDPs (Stage 4B; 5B-13); Bayes and conditional probability (Stage 4B); selection bias and informative missingness (5B-10). Reference them by exact folder/file names from the repository tree; never invent a path. If unsure a path exists, write `[VERIFY path]`.
- **Environment:** Python 3.10+, NumPy, SciPy, pandas, scikit-learn, pytest, matplotlib (optional); `lifelines`/`scikit-survival`/`statsmodels`/`hmmlearn`/`filterpy` optional cross-checks. No network at run time, no downloaded datasets or models, no paid APIs. **All data are synthetic, generated by the harness with known truth** (known hazards and censoring mechanism; known HMM transition/emission parameters and hidden path; known linear-Gaussian system and hidden state), plus tiny hand-sized tables for exact calculation by enumeration. **No real patient, customer, or sensor data.**
- **Time:** assume 8–10 hours for Unit 1, 8–10 hours for Unit 2, 4–6 hours for Unit 3; mark every time figure `[ASSUMPTION]`.

# 4. TEACHING MODEL — THE FOUR LEVELS (UNITS 1–3)

Each of these units progresses through **exactly these four levels** with identical headings.

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner — Foundations | Recognises when the data have the specialist structure; states the quantities and assumptions; computes the basic estimate by hand on a tiny table and in code. |
| **L2** | Intermediate — Working Practice | Implements and fits the method unaided on simulated data, checks it against the truth and a baseline, and avoids the classic failure modes. |
| **L3** | Advanced — Engineering Rigor | States acceptance criteria and assumption checks as testable properties, evaluates with the right metric and a time-correct design, quantifies uncertainty, defends trade-offs. |
| **L4** | Expert — Mastery and Teaching Others | Diagnoses failures in others' specialist-model work, decides whether the method is warranted at all, and could coach a peer. |

Units 0 and 4 use their own structures (Sections 6 and 7).

# 5. MANDATORY STRUCTURE FOR UNITS 1–3

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
- Method card and Tool card: (1) goal and when to use, (2) inputs/outputs, (3) steps, (4) assumptions and the checks for them, (5) failure modes and detection signals, (6) evidence of success, (7) status (PROVED / CITED [VERIFY] / EVIDENCE ONLY / HEURISTIC / JUDGEMENT), (8) oracle and test domain
- Design decisions with a trade-off table (option | benefit | cost | risk | choose when)
- Measurement method (what to measure; how to avoid fooling yourself: seeds, simulation replicates, baselines, time-correct splits)
- Exercise requiring a defended justification or counterexample

### N.6 Level 4 — Expert
- Failure scenarios and diagnosis (symptom → hypothesis → test → root cause → fix → prevention)
- Adversarial situations specific to the unit (see Section 6)
- Automation (aggregate verification commands, regression guards, consistency checks)
- Coaching: reviewing a peer's specialist-model analysis (assumption checks, evaluation, interpretation) with evidence-based feedback
- Edge cases and library differences (tie handling, convergence tolerances, parameterisations, and defaults in `lifelines`/`scikit-survival`/`hmmlearn`/`filterpy`; float precision in long sequences)

### N.7 Engineering lens
(Where this fails in real ML engineering — verifiable failures only, never a company claim or failure-rate statistic. Failure modes, blast radius, cost; data pipelines, observation windows, as-of correctness, serving, monitoring, retraining, interpretability to stakeholders.)

### N.8 Integrity lens
(Measurement risks: leakage through the observation window, tuning on the evaluation period, cherry-picked seeds or initialisations, reporting an uncalibrated discrimination metric as performance, over-reading a latent state, copying notebooks, AI-assistance disclosure, privacy and the ethics of time-to-event predictions about people. Controls, each verifiable by a command, test, or written check.)

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

- **The specialist-method card** (one per analysis): the decision the model supports; **data structure that justifies the method** (censored time-to-event / latent discrete state / latent continuous state with noisy observations); observation window and as-of time; what is observed and what is latent; assumptions with the check for each; strong simple baseline; method and hyperparameters (tuned on validation only); evaluation design (time-correct) and metrics; simulation/planted-truth check; uncertainty; decision and limits of use.
- **Evaluation hygiene rules:** (1) split by **time or by unit (subject), never by row** when the same subject contributes multiple rows or intervals; (2) features and covariates are computed **as of** the prediction/origin time; (3) the simple baseline gets **equal tuning effort** and is always reported; (4) every comparison reports the mean ± spread over ≥ 20 simulation replicates/seeds (quick ≥ 5) with the paired difference and a bootstrap interval; (5) **discrimination and calibration are reported together** (5B-04); (6) multi-start/initialisation variance is reported for any EM-fitted model; (7) assumption checks are part of the result, not an appendix.
- **Notation convention:** survival (*T*, *C*, observed time *Y = min(T, C)*, event indicator *δ*, hazard *h(t)*, cumulative hazard *H(t)*, survival *S(t)*); HMM (*π, A, B*, hidden *z_t*, observation *x_t*); Kalman (*x_t, F, H, Q, R, K_t, P_t*, innovation *ν_t*, covariance *S_t*) — stated once, used everywhere; mixing symbols is a defect.
- **Seed convention:** `SeedSequence` with named spawn keys; results independent of `n_jobs`.

## Unit 0 — Module orientation (`README.md`)

What "specialist" methods are and why a generalist must know them; the **three structures** (censoring; latent discrete state; latent continuous state) and the **decision map** from data structure to method, including "none of these — use a standard model"; prerequisites; the specialist-method card and evaluation hygiene rules; how the three units connect to 5B-03/04/08/13; what is out of scope; safety notes (time-to-event predictions about people — churn, health, employment, credit — have real consequences; interpretability, consent, and appeals are engineering constraints); how to use the evidence log. Not four-level; ≤ 2 pages equivalent plus the decision-map diagram.

## Unit 1 — Survival analysis concepts

- **L1:** the problem: time until an event, with **censoring** (right, left, interval) and **truncation** named; why ordinary regression and classification on "has churned" misrepresent the data (reproduce the observation-length artefact on simulated data); the data layout (*Y, δ*, covariates, start-time/stop-time rows); the **survival function** *S(t)*, **hazard** *h(t)*, **cumulative hazard** *H(t)* and the relations among them (derived); the **Kaplan–Meier** estimator built by hand on a 10-subject table (risk set, events, product-limit), then in code; reading a survival curve and median survival; **independent vs informative censoring** (what it means; one constructed example).
- **L2:** KM from scratch with **Greenwood** variance and confidence intervals (log-log transform) checked against enumeration and against `lifelines` if installed; **Nelson–Aalen**; the **log-rank test** from scratch (hand check on a tiny table); **parametric models** (exponential, Weibull) fitted by maximum likelihood with censoring (likelihood derived: events contribute *f(y)*, censored contribute *S(y)*), compared to KM; **Cox proportional hazards**: the model, the **partial likelihood** derived, tie handling (Breslow and Efron), a Newton–Raphson fit from scratch checked against `lifelines`/`statsmodels` where installed, **hazard ratio interpretation** (and why it is *not* a risk ratio); baseline hazard estimation; categorical and continuous covariates; **mini-project 1:** a churn/time-to-failure analysis on the planted simulator with a **non-survival baseline** (a classifier at a fixed horizon, with and without handling of censoring) and the survival model, evaluated at a time horizon.
- **L3:** **assumptions and their checks**: proportional hazards (Schoenfeld residuals, log-minus-log plots, time-interaction terms; remedies: stratification, time-varying coefficients, parametric/AFT alternatives, `[VERIFY]` cited); non-informative censoring (cannot be tested from data alone — sensitivity analysis by simulation with a planted informative mechanism); linearity of covariate effects; **competing risks** (cause-specific hazards vs the Fine–Gray subdistribution view; why 1−KM overstates cumulative incidence — reproduce; cited `[VERIFY]`); **time-varying covariates** (start–stop format and the **immortal-time bias** reproduced and fixed); **left truncation/delayed entry**; **AFT models** and what the coefficients mean; **evaluation**: **concordance** (Harrell's *C*; censoring-induced bias and the IPCW/Uno variant — implemented small), **time-dependent AUC**, **Brier score and integrated Brier score with IPCW**, and **calibration at a horizon** (predicted vs KM-observed risk by decile) — reported together; why concordance alone cannot show calibration; **data-splitting** by subject and by time (never by row for multi-row subjects); **machine-learning survival models** (random survival forests, gradient-boosted survival, penalised Cox — named, one small `scikit-learn`-compatible approach shown only if `scikit-survival` is installed, otherwise cited `[VERIFY]`); the **discrete-time hazard model as a logistic regression on person-period data** (a bridge to the learner's existing toolkit, implemented and compared with Cox on simulated data); sample-size and events-per-variable ideas as **HEURISTIC**, measured on planted data, never a rule; uncertainty (bootstrap by subject).
- **L4 adversarial situations:** a churn model that labels "not churned yet" as 0; right-censored subjects dropped; informative censoring (customers that leave the tracked population); a hazard ratio reported as constant when the effect reverses; a covariate measured after baseline used as baseline (immortal-time and look-ahead bias); a time-varying covariate computed with future data; a C-index of 0.7 reported while predicted 1-year risks are all 3× too high; comparing KM curves of groups defined by an outcome-dependent variable; a random row-split of a multi-row dataset; competing risks ignored (death before the event of interest treated as censoring).
- **Running example for Unit 1:** a **synthetic subscription-and-device-failure dataset** with known Weibull hazards, covariates with a planted proportional and a planted non-proportional effect, an independent and an informative censoring mechanism, a competing event, and time-varying usage; the true survival function is known.

## Unit 2 — Hidden Markov models and Kalman filters (introduction)

- **L1:** the shared idea: **a hidden state evolves; we see only noisy observations**; discrete state → HMM, continuous state → state-space/Kalman; examples (regime switching in usage, speech/activity states, sensor tracking, GPS smoothing) as **concepts only**; the HMM defined: *π, A, B*, the generative story, a **3-step toy example computed by hand by enumerating all hidden paths** (likelihood of an observation sequence); the Kalman filter's **predict–update** loop on a 1-D random walk observed with noise, by hand for 3 steps; the **Kalman gain as a weighted average** of prediction and measurement (the intuition).
- **L2:** **HMM algorithms from scratch** in scaled or log-space form, each checked by brute-force enumeration on tiny models: **forward** (likelihood), **backward**, **posterior state probabilities (smoothing)**, **Viterbi** (most likely path; and how it differs from per-step argmax of the posterior — demonstrated), **Baum–Welch (EM)** with the update equations derived; categorical and Gaussian emissions; multi-start, convergence criteria, and the **label-switching** of hidden states; choosing the number of states (held-out log-likelihood, BIC with its caveats, and domain sense); **Kalman filter** for the linear-Gaussian model *x_t = F x_{t-1} + w, y_t = H x_t + v* implemented from scratch (predict, update, Joseph-form covariance update for numerical stability), the **RTS smoother**, constant-velocity tracking example, and a check against the closed-form 1-D steady-state gain and against `filterpy`/`pykalman` where installed; **mini-project 2:** on the planted simulators, (a) fit an HMM to regime-switching data and compare recovered states to truth after permutation matching, with a **non-latent baseline** (e.g. a rolling-window or threshold rule); (b) filter and smooth a noisy trajectory and compare against a moving average and an exponentially weighted average.
- **L3:** **correctness and numerics**: scaling/log-sum-exp for long sequences (show underflow on a naive implementation); degenerate EM solutions (collapsed variances, zero transition probabilities) and the remedies (priors/regularisation, variance floors); **identifiability and interpretability** of hidden states (permutation, equivalence classes; a fitted "regime" can be an initialisation artefact — measure stability across restarts); model misspecification (HMM state durations are geometric — the **geometric-dwell-time limitation** shown, with the hidden semi-Markov model named only); **Kalman filter assumptions and diagnostics**: **innovation analysis** (zero mean, whiteness, normalised innovation squared against its χ² distribution), observability/controllability named with a small example, the effect of mis-specified *Q* and *R* (over-/under-confidence measured; the **steady-state gain** as a function of the *Q/R* ratio), noise-parameter estimation by EM or maximised innovation likelihood (small), **filter divergence** and remedies; **nonlinear and non-Gaussian** extensions named with a worked **extended Kalman filter** sketch on a mildly nonlinear model, and the unscented and particle filters **named only** with `[VERIFY]` citations; the **relationship** of both models to the general state-space framework, to ARIMA/exponential smoothing (5B-08), and to the MDP/POMDP of 5B-13 (a partially observed MDP is a controlled HMM — stated, linked); **evaluation**: held-out log-likelihood, one-step-ahead predictive error with rolling-origin design, state-recovery accuracy on planted data (clearly **unavailable in real data**), and calibration of predictive intervals (5B-02/04); **uncertainty** from the posterior over states and the Kalman covariance; **computational cost** (*O(T K²)* for HMM; *O(T n³)* for Kalman) and size guards; online/streaming operation and **batch/online parity** for a filter.
- **L4 adversarial situations:** an HMM fitted once from a random start and its states named "bull/bear" in the report; a number of states chosen to make the plot look pretty; an overflowing forward pass on a 10,000-step sequence; Viterbi path read as the per-step truth; a Kalman filter with *R* tuned to make the line smooth and innovations clearly autocorrelated; a linear filter applied to an angle (wrap-around) or a saturating sensor; a filter fed missing observations treated as zeros instead of skipped updates; a smoother used in a real-time setting (look-ahead leakage); the Kalman covariance interpreted as a guarantee when the model is wrong.
- **Running example for Unit 2:** a **synthetic device-usage stream** with a hidden 3-regime Markov structure (known *π, A, B* and path) and a **moving-object tracking task** with a known linear-Gaussian system and a known hidden trajectory, plus a nonlinear variant for the EKF sketch.

## Unit 3 — Selecting specialist methods

- **L1:** the question "is a specialist method warranted?" as an engineering decision; a **one-page selection map** mapping data structure and question to candidate methods and to the strong simple alternative: censored time-to-event (survival vs fixed-horizon classifier vs regression); hidden discrete regimes (HMM vs clustering vs change-point/threshold rule); noisy continuous state (Kalman vs smoothing vs ARIMA/ETS); and further **named electives, each with a one-paragraph recognition signal and a pointer, no implementation**: **Gaussian processes**, **change-point detection**, **point processes and event sequences**, **Bayesian hierarchical/mixed-effects models**, **extreme-value analysis**, **spatial statistics**, **optimal transport**, **conformal prediction extensions** (5B-02), **Bayesian optimisation** (cite each `[VERIFY]`; a one-line statement of what structure each addresses).
- **L2:** the **selection checklist** applied to five constructed scenarios (each with data description, decision, cost of error, available data volume, latency and interpretability requirements); building the **strong simple baseline first** for each (a fixed-horizon gradient-boosted classifier; a rolling-statistics rule; an exponentially weighted filter) and the **method-selection harness**: compare specialist vs baseline on planted data over ≥ 20 replicates with paired differences and intervals; report **where the specialist wins, where it ties, and where it loses** (e.g. no censoring → survival is unnecessary; wrong state count; strongly nonlinear dynamics); a **cost-of-ownership table** (data requirements, assumption checks to maintain, retraining cadence, monitoring, explanation burden, staff skill, failure modes).
- **L3:** **a rigorous decision rubric** with checkable criteria (structure present? assumptions testable? baseline beaten by a margin exceeding seed spread? calibration acceptable? operational cost justified? failure modes and harm understood?); **sensitivity of the recommendation** to the assumptions (simulation); **model-risk documentation**: assumptions register, validation evidence, limits of use, monitoring plan (drift in censoring pattern, hidden-state occupancy, innovation statistics), rollback and retraining triggers; **governance for specialist methods** (explanation to non-specialist stakeholders; reviewer checklist; reproducibility contract; handing over to the team that will maintain it); **learning a new specialist method responsibly** (a protocol: read the primary reference, reproduce on simulated data, write the assumption-check list, build the baseline, then decide) — applied to one **unfamiliar method chosen from the named electives** as a worked meta-example (cite sources, state the structure it exploits, implement the smallest toy version, and write the specialist-method card).
- **L4 adversarial situations:** a stakeholder who wants a specialist method because a paper used it; a "survival model" on data with no censoring; an HMM chosen because "regimes" sounds right; a Kalman filter on a system known to be strongly nonlinear; a specialist model that wins by 0.002 C-index with seed spread 0.01; a model nobody on the team can maintain; a result whose assumptions were checked once at development and never monitored; a risk estimate about individuals used with no appeal path.
- **Mini-project 3:** a written **selection memo** (≤ 2 pages) for a scenario of the learner's choosing, with the specialist-method card, the baseline comparison from the harness, the assumptions register, the cost-of-ownership table, and the recommendation (including "use the simple method" when that is the evidence).

## Unit 4 — Practice questions (`practice-questions.md`) — see Section 7

# 7. UNIT 4 — PRACTICE QUESTIONS (REQUIREMENTS)

At least **60 questions**, tagged by unit and level (L1–L4) and type, with a worked answer key: conceptual short answer; MCQ with "why the wrong answers are tempting"; **derivations and proofs** (relations among *S, h, H*; the censored likelihood; the Kaplan–Meier estimator as the nonparametric MLE (sketch or full as the key states); Greenwood's formula (delta-method derivation); the Cox partial likelihood and why the baseline hazard cancels; forward/backward recursions; the Baum–Welch update equations; the Kalman gain from minimising posterior variance; the 1-D steady-state gain; a Kalman filter step as Bayesian conditioning of Gaussians); **hand calculations** (a KM curve and a log-rank statistic on a 10-subject table; a Cox partial-likelihood contribution with ties; HMM likelihood by enumeration on a 2-state, 3-step model; a Viterbi path; two Kalman steps in 1-D); **code-reading and bug-finding** (censored subjects treated as events; risk set computed with the wrong time ordering; immortal-time bias in a time-varying covariate; random row-split of multi-row data; forward pass without scaling; EM with a single random start; Kalman covariance update that loses symmetry; missing observations filled with zero); **design-a-protocol** questions (given a decision, data, observation window, and risk, choose and defend the method and the baseline, the evaluation design, and the monitoring); 5 **interview-style scenario** questions with senior answers; 5 **negative-result** questions ("show a case where the specialist model does not beat the baseline"). Keys give the reasoning; every numeric key is verified by an independent computation (second method or exact enumeration).

# 8. NOTE ON THE ABSENCE OF A PROJECTS FOLDER

Because the tree has no `Projects/` folder, **do not invent project files**. Instead: (a) the three mini-projects in Units 1–3 are written inside those unit files as "Mini-project" sections with a goal, required steps, acceptance criteria (as commands and expected checks), a `pytest` oracle suite that **passes on the reference and fails on a deliberately broken variant**, and a ≤ 1-page decision note; (b) the module `README.md` explains that integrated, graded capstone work is in `../15-Stage-5B-Capstones/` and lists how each mini-project prepares for it.

# 9. (RESERVED — intentionally unused; keep numbering stable with sibling prompts)

# 10. CODE AND COMMAND RULES (NON-NEGOTIABLE)

1. Every code block states its language and path as a first-line comment (`# File: src/specialist/survival/km.py`).
2. Every command/snippet is paired with **expected output** labelled "representative — yours will differ in timings, versions, and paths", plus an interpretation.
3. **Code must run** on Python 3.10+ (version differences tagged `[VERSION-SENSITIVE]`), type hints on public functions, shape/dtype annotations, runtime precondition checks (non-negative times; event indicator binary; no `NaN` unless stated; covariates finite; time ordering of start–stop rows; stochastic matrices non-negative with rows summing to 1; covariance matrices symmetric positive semi-definite within tolerance), and **no mutation of caller inputs (verified by a hash-before/after test)**.
4. Every method and tool has its Method/Tool card before the code; **every analysis ends with a specialist-method card**.
5. Conventions are stated once (Section 6) and applied everywhere; mixing them is a defect.
6. No `==` on floats; tolerances stated and justified; **every tool has a spec-literal reference implementation checked against exact enumeration or a closed form on tiny cases and against `lifelines`/`scikit-survival`/`hmmlearn`/`filterpy` where installed, including: all-censored data, no-censoring data, tied event times, a single subject, a covariate that perfectly separates (Cox non-convergence), empty risk sets, HMM with one state, zero-probability transitions, very long sequences, a Kalman filter with a singular covariance, and missing observations**; budgets (simulation replicates × models × bootstrap × restarts; sequence length × states) are guarded before running.
7. Every worked example and tool has an **independent oracle** (labelled; never importing the function under test; exact, closed-form, enumeration, or planted-truth oracle preferred); tests pass on the reference and fail on a deliberately broken variant (e.g. censored treated as events; unscaled forward pass; wrong Kalman gain).
8. **No unproven claims** about method superiority, clinical or business effects, hiring, interviews, library defaults, thresholds, or real systems. Cited-only results are named and tagged `[VERIFY]`.
9. **Proof status is explicit** in every card and in the appendix; every heuristic is labelled `HEURISTIC` with its measured behaviour on the planted data.
10. Proofs are written in full where a unit requires them; a counterexample is a disproof; agreement on examples is not a proof.
11. Library internals (`lifelines`/`scikit-survival` tie handling, penaliser defaults, convergence tolerances; `hmmlearn` initialisation, covariance types and `n_iter`/`tol` defaults; `filterpy`/`pykalman` covariance-update form) are **not guarantees**: teach the learner to test the behaviour; tag `[VERSION-SENSITIVE]`/`[VERIFY]`.
12. **Resource safety:** budgets validated and enforced; sequence and matrix sizes checked from shapes before allocation; simulation and EM loops capped in code; files confined to the project directory.
13. **Security/privacy:** no `pickle`/`eval`/`exec` on untrusted input; strict loaders reject unknown fields, negative times, and malformed matrices; synthetic data only; logs hold metrics and hashed IDs, never raw individual-level records; no network at run time.
14. No secrets, paid APIs, or downloaded datasets/models; `clean` targets list what they remove and never delete the learner's evidence log.
15. Every lab ends with cleanup and a stray-file check.
16. Randomness only via `SeedSequence`/`np.random.default_rng(seed)`/`random_state` derived from the recorded root seed with named spawn keys; no system-clock reads inside logic (event times are synthetic data); timing only at the CLI edge, reported with spread; results independent of `n_jobs`.

# 11. SCOPE GUARD

Never re-teach Stage 1–4, 5A, or 5B-00 to 5B-13 content (link it). Do not teach deep survival models, neural state-space models, deep sequence models, variational or amortised inference, full Bayesian inference/MCMC, particle filters or unscented filters beyond naming, Gaussian processes or point processes beyond one-paragraph recognition notes, causal survival analysis beyond naming, multi-state and recurrent-event models beyond naming, or clinical-trial methodology. Do not recommend any package or platform as "the best". Do not give medical, clinical, legal, financial, or regulatory advice; present examples as **synthetic modelling and evaluation exercises**.

# 12. AUTHENTICITY, AUDIT, AND VERIFICATION PROTOCOL (MANDATORY)

**All learning content must be audited and verified against authentic sources before final submission.** You act as author, then as an independent auditor of your own work, and you include the audit evidence in the deliverable.

## 12.1 Source hierarchy (every claim traces to a tier)

| Tier | Source type | Examples for this module | Use |
|---|---|---|---|
| **T1** | Official documentation, release notes, standards | Python docs; **NumPy**, **SciPy** (`optimize`, `linalg`, `special`, `stats`), **pandas**; **scikit-learn docs**; and, for optional cross-checks, **lifelines**, **scikit-survival**, **statsmodels** (`duration`, `tsa.statespace`), **hmmlearn**, **filterpy**/**pykalman** documentation | API behaviour, defaults, versions |
| **T2** | Peer-reviewed papers and established textbooks (cite by title/author/venue/topic, **never invented page numbers or figures**) | Kaplan & Meier (1958); Cox (1972) regression models and life tables; Cox (1975) partial likelihood; Breslow (1974); Efron (1977); Greenwood (1926); Nelson (1972) and Aalen (1978); Mantel (1966) / Peto & Peto (1972) on the log-rank test; Kalbfleisch & Prentice, *The Statistical Analysis of Failure Time Data*; Klein & Moeschberger, *Survival Analysis*; Therneau & Grambsch, *Modeling Survival Data: Extending the Cox Model*; Hosmer, Lemeshow & May, *Applied Survival Analysis*; Harrell, *Regression Modeling Strategies* (and Harrell et al. 1982/1996 on concordance); Uno et al. (2011) on the C-statistic under censoring; Graf et al. (1999) on prediction error curves/Brier score; Heagerty, Lumley & Pepe (2000) on time-dependent ROC; Fine & Gray (1999) on subdistribution hazards; Putter, Fiocco & Geskus (2007) on competing risks; Suissa (2008) on immortal-time bias (named, `[VERIFY]`); Ishwaran et al. (2008) random survival forests; Pölsterl (2020) scikit-survival (named, `[VERIFY]`); Rabiner (1989) *A Tutorial on Hidden Markov Models*; Baum et al. (1970) and Dempster, Laird & Rubin (1977) on EM; Viterbi (1967); Murphy, *Probabilistic Machine Learning* (HMM and state-space chapters); Bishop, *Pattern Recognition and Machine Learning* (HMM and linear dynamical systems chapters); Kalman (1960); Rauch, Tung & Striebel (1965); Anderson & Moore, *Optimal Filtering*; Durbin & Koopman, *Time Series Analysis by State Space Methods*; Bar-Shalom, Li & Kirubarajan, *Estimation with Applications to Tracking and Navigation* (innovation tests; NIS); Julier & Uhlmann (1997) unscented filter and Gordon, Salmond & Smith (1993) particle filter (named only, `[VERIFY]`); Rasmussen & Williams, *Gaussian Processes for Machine Learning* (named for the elective note); Gelman et al., *Bayesian Data Analysis* (named) | Definitions, methods, equations, known limits |
| **T3** | Reputable university lecture notes and engineering write-ups | Only as a pointer, only if canonical, always `[VERIFY]` | Orientation; never the sole source of a technical claim |
| **T4** | Everything else (blogs, forums, AI output, your own memory) | — | **Never sufficient.** Convert to a derivation, a check, or `[VERIFY]` |

Rules:
1. Every definition, equation, and attributed method cites a T1/T2 source **by name** in the unit's `N.14` and in the appendix source ledger. Paper titles and authors may be given only if you are confident; otherwise write the topic and `[VERIFY]`.
2. **Never fabricate** a citation, DOI, URL, page, figure, dataset result, or quote. A claim you cannot trace is rewritten as a derivation, replaced by a runnable check on simulated data with known truth, or removed.
3. Numerical statements are either (a) the output of code in the syllabus with a seed, (b) an exact derivation, or (c) cited and `[VERIFY]`.
4. Version-specific API facts name the version checked and are tagged `[VERSION-SENSITIVE]`.

## 12.2 Mandatory multi-pass self-audit (run after drafting, before delivering each part)

- **Pass A — Factual audit:** list every factual claim in the part; assign each a tier and status (PROVED / CITED [VERIFY] / EVIDENCE ONLY / HEURISTIC / JUDGEMENT); fix or remove any with none.
- **Pass B — Mathematical audit:** re-derive every equation, proof, and numeric answer key independently (second method — e.g. brute-force enumeration against forward–backward; direct likelihood against the partial likelihood on a tiny table); check indices, time offsets, risk-set definitions, ties, and signs; verify every hand-calculation by code.
- **Pass C — Code audit:** every snippet is complete, runs as written, has a stated oracle independent of the function under test, and its printed output matches what the code would produce; seeds and budgets present.
- **Pass D — Leakage and design audit:** for every experiment, confirm in writing that splits are by subject/time, covariates are as-of, the observation window and censoring are handled correctly, no future information enters the model, and evaluation (discrimination **and** calibration) is on held-out data.
- **Pass E — Over-claim audit:** hunt for universal claims ("always", "best", "X% better", "assumption holds") and replace with conditional, measured, or cited statements; check every assumption claim names the check that was run.
- **Pass F — Consistency audit:** names, paths, notation (survival, HMM, Kalman), conventions, seeds, and cross-references match the tree and the other units.
- **Pass G — Safety and integrity audit:** ethics of time-to-event predictions about people, no medical/clinical/financial advice, resource caps, no network, no secrets, synthetic data only, no real-system claims.

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

1. **Part 0:** an outline: unit list with planned sizes, the conventions block and notation tables, the running-example specifications, the source ledger (draft), and the part plan. Then stop.
2. **Parts 1–N:** Unit 0 and the survival unit may share a part; Units 1 and 2 each take at least two parts (split at the L2/L3 boundary); Unit 3 and Unit 4 one part each. Each part ends with `PART k/N COMPLETE — audit Passes A–G done — type "continue"`. Never summarise a unit instead of writing it; never truncate with "etc." or "similar to above".
3. **Final part:** Appendices A–G and a **coverage matrix** mapping every bullet in Sections 6–8 to the heading where it is taught.

If a part would be cut off, stop at a clean boundary and say so; resume exactly there on `continue`.

# 14. QUALITY BAR — DEFINITION OF DONE

- [ ] Every unit in Section 2 present, in order, matching the tree; no extra files, no invented `Projects/` files.
- [ ] Every unit (1–3) has all four levels and every skeleton heading `N.0`–`N.14`.
- [ ] Every Section 6 bullet is taught and appears in the coverage matrix.
- [ ] Every method has a Method/Tool card, a from-scratch reference, an exact/closed-form oracle, a library agreement test where the library is installed, and broken variants that fail the tests.
- [ ] Every analysis has a specialist-method card, a strong simple baseline at equal tuning, subject/time-correct splits, ≥ 20 replicates/seeds (quick ≥ 5), paired differences with intervals, discrimination and calibration reported together.
- [ ] Negative results are present: informative censoring; non-proportional hazards; immortal-time bias; competing-risk overstatement; HMM restart instability and label switching; Kalman mis-specified *Q*/*R*; a case where the specialist model does not beat the baseline.
- [ ] Three mini-projects (one per unit 1–3) are complete with acceptance criteria and oracle tests.
- [ ] ≥ 60 practice questions with verified keys.
- [ ] All Section 12 audit passes done; Appendices A–G present; every `[VERIFY]` registered; no fabricated citation.
- [ ] No hype, no outcome or hiring claims, no company claims, no medical/clinical/financial advice.

# 15. START

Begin with **Part 0** now. Do not ask clarifying questions; record any assumption as `[ASSUMPTION]`.

=== END PROMPT ===

## Notes for the human operator (not part of the prompt)

- **Audit step is yours too.** The prompt makes the model self-audit and emit Appendices A–D, but a model without browsing can only cite from memory. Before accepting the syllabus, work through **Appendix C (`[VERIFY]` register)**: check each cited paper/book against its source, check `lifelines`/`scikit-survival`/`hmmlearn`/`filterpy` behaviours against the official docs for the versions you install, and run every code block and `pytest` suite. Pay special attention to the survival risk-set and tie conventions and to the Kalman covariance-update form, which are the most common sources of silent errors.
- This module has **no `Projects/` folder**; the prompt places mini-projects inside Units 1–3 and leaves graded capstones to `../15-Stage-5B-Capstones/`. If you later want standalone project files, add them to the tree first and then extend Section 2 and Section 8 of this prompt.
- Section 9 is intentionally reserved so section numbers match the sibling prompts (11–13).
- Split the finished syllabus into the five target files listed in Section 2; keep this prompt file alongside.
- If a part comes back truncated or summarised, reply `redo part k in full`.
