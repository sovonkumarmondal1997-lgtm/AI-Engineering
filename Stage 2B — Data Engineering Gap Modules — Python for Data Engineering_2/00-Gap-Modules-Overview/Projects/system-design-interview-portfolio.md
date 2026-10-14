# Project Roadmap — System Design Interview Portfolio

This is the end-to-end roadmap for **Gap Project 05: System Design Interview
Portfolio**, the project for **Gap Module G5 — Data Engineering System
Design Interviews**. It takes you from scattered notes to a
**production-grade interview portfolio**: a versioned, peer-reviewed,
consistently structured body of design cases, method sheets, follow-up
answers, behavioural stories, a take-home kit, company-specific briefs, and
measurable evidence that your interview performance has reached your target
level.

"Production grade" for a portfolio means: every artefact follows a
consistent template; every design is backed by estimates, trade-offs, and
failure handling; claims are honest and linked to real work; the portfolio
has been reviewed by others; your readiness is **measured** with a rubric
over repeated mock interviews; nothing confidential from any employer is
included; and there is a maintenance process that keeps it current after
every real interview.

It is written as a sequence of **milestones**. Each milestone has a goal,
tasks, deliverables, and **acceptance criteria**. Commit and tag the
repository at the end of each milestone (`m0`, `m1`, …).

---

## 1. Why this project matters

Most candidates prepare for data engineering interviews by reading
solutions. They recognise good answers but cannot produce them under time
pressure, cannot handle follow-up questions, and tell vague stories with no
results. A portfolio built through deliberate practice fixes this:

- it turns knowledge from Stage 2 and the capstone into **ready-to-use
  designs and stories**;
- it makes weaknesses **visible** through scoring and an error log;
- it lets you **prepare for a specific company in hours**, not weeks;
- it gives you **public proof** of your thinking (a published case study);
- it stays useful for years — for promotions, design reviews, and mentoring
  others.

---

## 2. Project goal and scope

### Goal

Build `de-interview-portfolio`, a private (with one public artefact)
repository containing:

1. **Method sheets**: design framework, clarifying-question checklist,
   estimation templates and reference numbers, trade-off catalogue, diagram
   conventions, and scoring rubric.
2. **Case portfolio**: nine complete written designs (the G5 case library)
   with diagrams, estimates, trade-offs, failure handling, follow-ups, and
   links to your own project work.
3. **Deep-dive cards and a follow-up bank**: at least 40 follow-up questions
   with concise answers, plus one-page component deep dives.
4. **Story bank**: 10–12 quantified behavioural stories mapped to themes.
5. **Take-home kit**: a reusable template repository, one completed
   take-home, and recorded live-coding drills.
6. **Practice evidence**: a mock-interview log with scores over time and an
   error log showing improvement.
7. **Company briefs**: a template and at least two completed briefs.
8. **A public artefact**: one published design case study or capstone
   write-up.
9. **A readiness review and maintenance plan**.

### In scope

- Writing, diagramming, recording, reviewing, and practising — using all
  Stage 2 knowledge, the capstone, and your chosen depth track (G3 or G4).

### Out of scope

- Learning new technology (return to the relevant module if a gap appears).
- SQL and Python question banks already in Stage 1 and Stage 2 (practise
  them alongside, but they are not rebuilt here).

---

## 3. Prerequisites and timing

- **Gap Module G5** studied (Topics 01–19).
- **Stage 2** completed; the **Capstone** (Project 07) in progress or done;
  ideally one of **G3 (AWS)** or **G4 (Databricks)**.
- At least one practice partner (peer, mentor, or study group).

**Estimated effort:** about **4–5 weeks** at 8–10 hours per week, followed
by ongoing maintenance (a few hours per week while interviewing).

---

## 4. Readiness criteria (write them down in M0)

| Area | Target |
| --- | --- |
| **Design cases** | Each of the nine cases completed in **45 minutes** with a rubric score of **"strong" (≥ 2.5/3 average)** in at least one timed attempt after the first |
| **Follow-ups** | Average ≥ 2.5/3 across two follow-up-only mocks |
| **Estimation** | Any standard estimate (volume, storage, partitions, cost) in ≤ 3 minutes, within an order of magnitude |
| **Behavioural** | Every common theme covered by a story delivered in ≤ 3 minutes with a measurable result |
| **Take-home** | One realistic take-home delivered within its time limit with README, tests, and a 15-minute presentation |
| **Trend** | Mock scores improve across at least 10 mocks; at least three recurring mistakes eliminated |
| **Review** | Portfolio reviewed by at least two people; all critical findings fixed |
| **Integrity** | No confidential employer information; every personal claim accurate |

---

## 5. Repository structure

```text
de-interview-portfolio/
├── README.md                     # purpose, how to use it, readiness status, index
├── method/
│   ├── framework.md              # one-page design framework + cross-cutting checklist
│   ├── clarifying-questions.md
│   ├── estimation.md             # templates + reference numbers
│   ├── tradeoffs.md              # 20+ trade-offs with deciding criteria
│   ├── diagram-conventions.md
│   └── rubric.md                 # scoring rubric (1–3 per area) + time plan
├── cases/
│   ├── _template.md
│   ├── 07-batch-analytics-platform/          # design.md, diagram.(png|svg|excalidraw), followups.md, attempts.md
│   ├── 08-real-time-clickstream/
│   ├── 09-cdc-replication/
│   ├── 10-ml-feature-platform/
│   ├── 11-log-and-metrics-analytics/
│   ├── 12-ad-attribution-and-dedup/
│   ├── 13-iot-telemetry/
│   ├── 14-gdpr-deletion/
│   └── 15-rag-vector-platform/
├── deep-dives/                   # one-page component cards (Kafka, Spark, table formats, orchestration, warehouses, caches, CDC, streaming state)
├── followups/
│   └── bank.md                   # 40+ questions with structured answers
├── stories/
│   ├── _template.md
│   ├── bank.md                   # 10–12 stories
│   └── theme-matrix.md           # themes × stories
├── take-home/
│   ├── template/                 # reusable repo skeleton (or a link to a separate repo)
│   ├── completed-01/             # a completed take-home with README and tests
│   └── live-coding/              # drill problems, solutions, notes
├── practice/
│   ├── mock-log.csv              # date, type, case, partner, scores per rubric area, total, notes
│   ├── error-log.md              # mistake → cause → fix → recurred?
│   ├── progress.md               # charts/tables of scores over time
│   └── recordings.md             # index of recordings (stored privately, not in Git)
├── companies/
│   ├── _template.md
│   └── <company>.md              # company-specific briefs
├── public/
│   └── case-study.md             # the published write-up (sanitised)
└── docs/
    ├── review-checklist.md
    ├── reviews/                  # reviewer feedback and resolutions
    ├── readiness-review.md
    └── maintenance.md
```

---

## 6. Milestones overview

```text
M0   Framing: target roles, readiness criteria, and plan
M1   Repository, templates, and tracking
M2   Method sheets
M3   Baseline assessment
M4   Case portfolio, part 1 (cases 07–10)
M5   Case portfolio, part 2 (cases 11–15)
M6   Follow-up bank and component deep-dive cards
M7   Story bank
M8   Take-home kit and live-coding drills
M9   Mock-interview programme
M10  Peer review and quality assurance
M11  Company-specific briefs
M12  Public artefact
M13  Readiness review and maintenance plan
(M14 Optional stretch goals)
```

---

## 7. Milestones

### M0 — Framing: target roles, readiness criteria, and plan

**Goal:** Know exactly which roles you are preparing for and how you will
know you are ready.

**Tasks**

1. Define target **roles and level** (e.g. data engineer, senior data
   engineer, analytics engineer, platform data engineer) and the **domains**
   you are interested in (product analytics, fintech, ad tech, IoT, AI
   platforms).
2. Study five real job descriptions at your target level and list the
   recurring skills and interview formats.
3. Write the **readiness criteria** (Section 4), adjusted to your level.
4. Create a **4–5 week plan** with weekly goals and mock slots booked with
   partners.

**Acceptance criteria**

- [ ] Target roles, level, and domains are written.
- [ ] Readiness criteria are measurable.
- [ ] Practice partners and mock dates are scheduled.

---

### M1 — Repository, templates, and tracking

**Goal:** A structured portfolio that makes consistent, measurable practice
easy.

**Tasks**

1. Create the repository structure from Section 5 (private repository;
   recordings stored outside Git).
2. Write `cases/_template.md` with fixed sections: prompt; clarified
   requirements (functional and non-functional with numbers); assumptions;
   estimates; high-level diagram; component choices with justification;
   data model and storage layout; processing (batch/streaming); serving;
   cross-cutting concerns (quality, idempotency/backfills, late data, schema
   evolution, orchestration, observability, security/privacy, cost); failure
   scenarios; evolution (10×, new consumers); key trade-offs; follow-ups;
   "evidence from my work" links; attempt history.
3. Write `stories/_template.md` (theme, situation, task, actions with "I",
   result with numbers, lesson, questions it answers) and
   `companies/_template.md`.
4. Create `practice/mock-log.csv` with columns for each rubric area, and
   `practice/error-log.md`.
5. Write the README index with a readiness status table.

**Acceptance criteria**

- [ ] Every artefact type has a template.
- [ ] Mock scores and mistakes can be logged in under 2 minutes.

---

### M2 — Method sheets

**Goal:** Concise, personal reference sheets that you can apply under
pressure.

**Tasks**

1. `framework.md`: your one-page framework (requirements → estimates →
   high-level flow → storage and model → processing → serving →
   cross-cutting → failures → evolution) with a time plan for 45 and 60
   minutes.
2. `clarifying-questions.md`: at most one page, grouped by consumers, scale,
   freshness, correctness, retention, access/privacy, existing systems.
3. `estimation.md`: templates (event rates, storage with compression and
   replication, partitions/shards, cluster size, serving QPS, monthly cost)
   and a small set of reference numbers you can recall.
4. `tradeoffs.md`: at least 20 trade-offs, each ending with "…so for
   requirement X, I choose Y", with an example from your projects.
5. `diagram-conventions.md` and `rubric.md` (scoring 1–3 per area:
   requirements, estimation, architecture, depth, trade-offs,
   reliability/quality, security/privacy, cost, communication).
6. Test each sheet by applying it to one simple prompt.

**Acceptance criteria**

- [ ] Each sheet fits on one or two pages and is written in your own words.
- [ ] You can reproduce the framework and 10 trade-offs from memory.
- [ ] Estimation templates produce answers within 3 minutes.

---

### M3 — Baseline assessment

**Goal:** Measure where you start, so you can prove improvement.

**Tasks**

1. Do **two cold mocks** (one design case, one behavioural set) with a
   partner, recorded, before studying the case notes in depth.
2. Score them with your rubric; ask the partner to score independently.
3. Seed the **error log** with every mistake observed (e.g. no estimates,
   silent drawing, missing failure handling, vague results).
4. Prioritise the top five weaknesses and plan targeted practice.

**Acceptance criteria**

- [ ] Baseline scores are logged for each rubric area.
- [ ] The error log has at least five concrete entries with planned fixes.

---

### M4 — Case portfolio, part 1 (cases 07–10)

**Goal:** Four complete, high-quality designs — each first attempted under
time pressure, then refined.

**Tasks**

For **batch analytics platform (07)**, **real-time clickstream (08)**,
**CDC replication (09)**, and **ML feature platform (10)**:

1. **Timed attempt**: 45 minutes, aloud, with a diagram, using only your
   method sheets; record it; log the score in `attempts.md`.
2. **Refined write-up** in `design.md` using the template, with numbers,
   trade-offs, failure handling, and evolution.
3. **Clean diagram** following your conventions (source file plus exported
   image).
4. **Follow-ups**: at least five follow-up questions answered in
   `followups.md`.
5. **Evidence links**: the Stage 2 modules, projects, capstone parts, or
   G3/G4 work where you built something similar — with what you learned.
6. A **second timed attempt** a week later without notes; log the score.

**Acceptance criteria**

- [ ] Four complete case folders following the template.
- [ ] Each case has two logged attempts; the second scores higher or at
      target.
- [ ] Every design includes estimates, cross-cutting concerns, failure
      handling, and cost.

---

### M5 — Case portfolio, part 2 (cases 11–15)

**Goal:** Complete the remaining five designs to the same standard.

**Tasks**

Repeat the M4 process for **log and metrics analytics (11)**, **ad
attribution and dedup (12)**, **IoT telemetry (13)**, **GDPR deletion
(14)**, and **RAG and vector platform (15)** — paying special attention to
each case's hardest deep dive (e.g. seven-day attribution state, reconnect
storms, deleting from immutable history, re-embedding at scale).

**Acceptance criteria**

- [ ] All nine case folders complete, each with two logged attempts.
- [ ] Each case's hardest deep dive is written up in detail.
- [ ] A one-page **case index** in the README summarises each design in
      three bullets.

---

### M6 — Follow-up bank and component deep-dive cards

**Goal:** Calm, concrete answers to the questions that decide senior
interviews.

**Tasks**

1. `followups/bank.md`: at least **40** questions across scale, failures,
   data problems (late, duplicate, malformed, schema change), operations
   (backfills, upgrades), cost, security/privacy, disaster recovery, and
   evolution. Answer each in five sentences or fewer using **detect →
   contain → recover → prevent** where it fits, with numbers.
2. `deep-dives/`: one-page cards for core components — Kafka (partitions,
   consumer groups, delivery semantics), Spark (shuffles, skew, AQE), table
   formats (commits, merges, compaction, time travel), streaming state and
   watermarks, orchestration (idempotency, backfills), warehouses (layout,
   cost), CDC (snapshots, ordering), caches (invalidation).
3. Two **follow-up-only mocks** (30 minutes each), recorded and scored.

**Acceptance criteria**

- [ ] 40+ answered follow-ups and 8+ deep-dive cards.
- [ ] Follow-up mock scores meet the readiness target.

---

### M7 — Story bank

**Goal:** Specific, honest, quantified stories for every behavioural theme.

**Tasks**

1. Draft **10–12 stories** using the template: ownership, ambiguity,
   conflict/disagreement, failure and learning, influence without
   authority, prioritisation, mentoring/helping others, a data-quality
   incident, a metric dispute, a reliability improvement, a cost reduction,
   and a migration or trade-off decision.
2. Use real professional experience where you have it; use Stage 2 projects
   and the capstone where you do not — **clearly described as projects**.
3. Quantify results (SLA improvements, incidents reduced, hours saved, cost
   reduced, adoption).
4. Build `theme-matrix.md` mapping themes to stories so each theme has at
   least two options.
5. Deliver each story aloud to a timer and a partner; tighten to under 3
   minutes.
6. Prepare five questions to ask interviewers.

**Acceptance criteria**

- [ ] Every theme has at least two stories.
- [ ] Every story has a measurable result and clear personal actions.
- [ ] Two behavioural mocks meet the readiness target.

---

### M8 — Take-home kit and live-coding drills

**Goal:** Deliver take-homes and live pipeline coding with production habits
— on time.

**Tasks**

1. **Template repository**: project layout, `uv` configuration, Docker
   Compose for PostgreSQL/MinIO, pytest set-up with fixtures, linting,
   logging and configuration skeleton, and a README template (how to run,
   assumptions, design, trade-offs, tests, next steps).
2. **Completed take-home** within a strict time limit (e.g. 4 hours):
   incremental ingestion of a paginated API into PostgreSQL, deduplication,
   two modelled tables, three SQL answers, data-quality checks, tests, and a
   README.
3. **Presentation**: a 15-minute walkthrough of the take-home, including
   "how this changes at 100× scale".
4. **Live-coding drills** (45 minutes each, recorded, thinking aloud):
   latest record per key, sessionisation, incremental upsert with late data,
   and a small streaming-style aggregation.

**Acceptance criteria**

- [ ] The take-home was completed within its time limit with passing tests
      and a clear README.
- [ ] The presentation was delivered and questioned by a partner.
- [ ] Four live-coding drills are recorded with self-reviews.

---

### M9 — Mock-interview programme

**Goal:** Turn preparation into consistent performance — and prove it with
data.

**Tasks**

1. Complete at least **10 mocks**: six design (mix of cases, including at
   least two you have not rehearsed recently), two follow-up-only, and two
   behavioural. At least half with partners; the rest recorded solo.
2. After each: score with the rubric, log to `mock-log.csv`, and update the
   error log (did an old mistake recur?).
3. Update `progress.md` with a table or chart of scores over time per
   rubric area.
4. **Interview others** at least twice using your rubric — it sharpens your
   own judgement.
5. Run one **loop simulation**: three or four rounds in one day (design,
   follow-ups, behavioural, live coding) to build stamina.

**Acceptance criteria**

- [ ] 10+ mocks logged with scores and notes.
- [ ] Score trends show improvement; three recurring mistakes eliminated.
- [ ] The loop simulation is completed and reviewed.

---

### M10 — Peer review and quality assurance

**Goal:** The portfolio is accurate, consistent, clear, and free of
confidential or misleading content.

**Tasks**

1. Write `docs/review-checklist.md`: template completeness, correct
   technical claims, estimates that make sense, trade-offs tied to
   requirements, failure handling present, diagrams readable, stories
   honest and quantified, no confidential employer information, consistent
   terminology.
2. Ask **two reviewers** (a peer and, ideally, a more senior engineer) to
   review at least three cases, the story bank, and the take-home using the
   checklist.
3. Record feedback and resolutions in `docs/reviews/`; fix all critical
   findings.
4. Run a **consistency pass**: same terminology, diagram style, and section
   order everywhere; update the README index.
5. Run a **confidentiality pass**: remove any employer names, internal
   system names, numbers, or details you are not allowed to share.

**Acceptance criteria**

- [ ] Two reviews completed; all critical findings resolved.
- [ ] Consistency and confidentiality passes documented.

---

### M11 — Company-specific briefs

**Goal:** Prepare for any specific company in a few hours.

**Tasks**

1. Complete `companies/_template.md`: product and business model, likely
   data scale and domains, known technology stack (from public engineering
   blogs and job descriptions), likely design questions, which of your cases
   to adapt and how, relevant stories, questions to ask, and interview
   format.
2. Write **two complete briefs** for real target companies (using public
   information only).
3. Do one mock per brief with an adapted case (e.g. your clickstream design
   adapted to a food-delivery company's scale and domain).

**Acceptance criteria**

- [ ] Two briefs completed from public sources with adapted designs.
- [ ] Each brief was used in a mock.

---

### M12 — Public artefact

**Goal:** Public, verifiable evidence of your design thinking.

**Tasks**

1. Choose one case or your **capstone** and write a sanitised **case
   study** (1,500–2,500 words): problem, requirements, architecture diagram,
   key decisions and trade-offs, failure handling, results or measurements,
   and lessons learned.
2. Publish it (e.g. a blog, GitHub Pages, or portfolio site) with a clean
   diagram; link your public project repositories where appropriate.
3. Align your **résumé and profile bullets** with the portfolio: each claim
   backed by a project, a measurement, or a story.
4. Ask one reviewer to read the published version for clarity and
   accuracy.

**Acceptance criteria**

- [ ] One public case study published, reviewed, and free of confidential
      information.
- [ ] Résumé claims link to evidence in the portfolio.

---

### M13 — Readiness review and maintenance plan

**Goal:** A clear, evidence-based "ready" decision — and a process that
keeps the portfolio useful while you interview.

**Tasks**

1. Complete `docs/readiness-review.md`: each readiness criterion (Section 4)
   with evidence (mock scores, attempt logs, reviews); gaps and a plan for
   each.
2. Run a **final mock loop** with a new partner who has not seen your
   portfolio.
3. Write `docs/maintenance.md`:
   - after every real interview: a reflection within 24 hours (questions
     asked, what went well, gaps), new follow-ups and cases added, error log
     updated;
   - weekly while interviewing: two mocks and one re-attempted case;
   - monthly: refresh reference numbers and tools, add one new case (e.g. a
     staff-level platform-strategy or migration case);
   - interview-day checklist (environment, tools, energy, allowed notes).
4. Write a short **retrospective** on the portfolio project.

**Acceptance criteria**

- [ ] Every readiness criterion is met or has a dated plan.
- [ ] The final mock loop meets the target level.
- [ ] The maintenance process is written and has been used at least once
      (e.g. after a real or simulated interview).

---

### M14 — Optional stretch goals

- **Video walkthroughs**: record 10-minute walkthroughs of three cases.
- **Cloud-specific variants**: write AWS (G3) and Databricks (G4) versions
  of two cases with concrete services.
- **Staff-level cases**: platform strategy (build vs buy across the company),
  migrating from a legacy warehouse to a lakehouse, and designing data
  contracts for 50 teams.
- **Mentoring**: run a mock-interview session for others using your rubric
  and templates.
- **Interactive site**: publish selected cases with diagrams as a small
  portfolio website.

---

## 8. Definition of done

- [ ] Method sheets complete and memorised.
- [ ] Nine case folders complete, each with two timed attempts and a
      refined design.
- [ ] 40+ follow-ups and 8+ deep-dive cards.
- [ ] 10–12 quantified stories covering every theme.
- [ ] Take-home kit, one completed take-home, presentation, and four
      live-coding drills.
- [ ] 10+ scored mocks with improving trends; three recurring mistakes
      eliminated; a loop simulation completed.
- [ ] Two peer reviews resolved; consistency and confidentiality passes
      done.
- [ ] Two company briefs; one public case study; résumé aligned.
- [ ] Readiness review with evidence; maintenance process in use.

---

## 9. Evaluation rubric (self or peer review)

Score each area from 0 to 3. A production-grade portfolio scores **at least
2 in every area** and **3 in Design quality, Evidence of readiness, and
Integrity**.

| Area | What a "3" looks like |
| --- | --- |
| Method | Personal, concise sheets applied consistently; framework recalled from memory |
| Design quality | Nine designs with numbers, justified trade-offs, cross-cutting concerns, failure handling, and cost |
| Depth | Strong follow-up answers and component cards; hardest deep dives covered |
| Communication | Clean diagrams, clear narration, good time management in recordings |
| Behavioural | Specific, quantified, honest stories for every theme within time |
| Practical delivery | Take-home and live coding on time with production habits |
| Evidence of readiness | 10+ scored mocks with measurable improvement and a completed loop simulation |
| Review and consistency | Two external reviews resolved; consistent templates and terminology |
| Integrity | No confidential information; every claim accurate and backed by evidence |
| Sustainability | Maintenance process defined and used; portfolio kept current |

---

## 10. Common pitfalls to avoid

- Writing polished designs without ever practising them under time
  pressure.
- Memorising "the answer" instead of applying a method to new variations.
- Designs without numbers, cost, or failure handling.
- Stories without measurable results, or claiming others' work as your own.
- Practising only alone and never with a pushing interviewer.
- Not recording mocks, so recurring mistakes stay invisible.
- Including confidential employer details in a portfolio or public post.
- Letting the portfolio go stale during a long job search.

---

## 11. Suggested timeline

| Week | Milestones |
| --- | --- |
| 1 | M0 framing · M1 repository and templates · M2 method sheets · M3 baseline |
| 2 | M4 cases 07–10 (first attempts and write-ups) |
| 3 | M5 cases 11–15 · second attempts of cases 07–10 · M6 follow-up bank |
| 4 | M7 story bank · M8 take-home kit · start M9 mocks |
| 5 | M9 mocks and loop simulation · M10 review · M11 company briefs · M12 public artefact · M13 readiness review |
| Ongoing | Maintenance: weekly mocks, post-interview reflections, monthly refresh |

---

## 12. How to use the portfolio in interviews and beyond

- **Before an interview:** read the company brief, re-run one adapted case
  aloud, review the follow-up bank for that domain, and rehearse three
  stories.
- **During the interview:** apply the framework, not a memorised diagram;
  use your estimation templates; draw with your conventions; tie every
  choice to the stated requirements.
- **After the interview:** write the reflection, update the error log, add
  new questions, and adjust your plan.
- **Beyond job searching:** use the same method in real design reviews,
  promotion cases, and when mentoring other engineers.

A portfolio that shows **how you think** — measured, reviewed, honest, and
kept current — is the strongest preparation for data engineering interviews
at any level, and the best bridge from everything you built in Stage 2 to
the roles and the AI engineering stages that come next.
