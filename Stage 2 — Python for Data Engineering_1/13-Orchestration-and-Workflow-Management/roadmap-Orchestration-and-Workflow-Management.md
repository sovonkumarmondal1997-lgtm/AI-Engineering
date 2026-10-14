# Roadmap — Module 2.13: Orchestration and Workflow Management

This is the learning roadmap for the thirteenth module of Stage 2, **Python
for Data Engineering**. It tells you **what** to learn about orchestrating
data pipelines, **in what order**, **how** to learn each topic, and **how
to prove to yourself** that you have learned it before you move on.

By now you have built ingestion jobs (Module 2.9), quality gates (Module
2.11), and transformation pipelines with CLI entry points, data intervals,
backfills, and state (Module 2.12). Something must now run all of them: in
the right order, on the right schedule or when the right data arrives,
with retries, timeouts, alerts, history, and a way to re-run last March
without breaking today. That is **orchestration**.

Apache Airflow is the most widely deployed orchestrator and appears in most
data engineering job descriptions, so it is the main tool of this module.
Dagster and Prefect represent two different, popular philosophies —
asset-centric and Python-flow-centric — and a senior engineer must be able
to compare them honestly. The most important lesson, though, is
tool-independent: **an orchestrator coordinates work; it should not do the
heavy work itself.**

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain DAGs, dependencies, schedules, data intervals, runs, and task
  states in a tool-independent way.
- Explain the limits of cron and when a full orchestrator is (and is not)
  worth it.
- Describe **Airflow's architecture** — scheduler, DAG processor, API
  server, triggerer, executors, workers, metadata database — and how a DAG
  becomes running tasks.
- Write Airflow DAGs with operators and the **TaskFlow API**, including
  dynamic task mapping, task groups, branching, and trigger rules.
- Manage **connections, variables, hooks, and XComs** safely and use XComs
  only for small metadata.
- Wait for external events efficiently with **sensors, deferrable
  operators**, and **data-aware (asset) scheduling**.
- Design **retries, timeouts, deadlines, and failure callbacks** that alert
  the right people with useful context.
- Run **backfills, catch-up, and partitioned runs** safely.
- Build **software-defined assets** in Dagster and **flows and tasks** in
  Prefect, and compare the three tools.
- **Test and validate** DAGs in CI so broken pipelines never reach
  production.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.12. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Processes, signals, environment variables, cron-style scheduling basics | Stage 0 — OS Fundamentals and Command Line | Schedulers and workers are processes; tasks receive signals |
| Docker and Docker Compose basics | Stage 0 — Developer Environment | Running Airflow, Dagster, and Prefect locally |
| CLI programs, exit codes, logging | Stage 1 — Modules 1.5 and 1.10 | Orchestrators judge tasks by exit codes and logs |
| Pytest and mocking | Stage 1 — Module 1.7 | Testing DAGs and tasks |
| Freshness SLAs and dataset tiers | Stage 2 — Module 2.1 | What orchestration must guarantee |
| PostgreSQL | Stage 2 — Modules 2.6–2.7 | Airflow's metadata database |
| Ingestion jobs, file-arrival checks, retry rules | Stage 2 — Module 2.9 | Tasks you will orchestrate; retry logic **inside** tasks is not re-taught |
| Concurrency and resource limits | Stage 2 — Module 2.10 | Pools, parallelism, and concurrency limits in orchestrators |
| Quality gates and write–audit–publish | Stage 2 — Module 2.11 | Gates become tasks and dependencies |
| Run contexts, data intervals, idempotent tasks, backfills, pipeline state, dbt | Stage 2 — Module 2.12 | The orchestrator calls these; the patterns are **not** re-taught |

**Tools needed:**

- Docker and Docker Compose.
- **Apache Airflow 3.x**, run with the official Docker Compose setup (or
  `airflow standalone` in a `uv` environment installed with Airflow's
  constraints file). A PostgreSQL metadata database, not SQLite, for
  anything beyond first experiments.
- **Dagster** (`dagster`, `dagster-webserver`, and `dagster-dbt`) run with
  `dagster dev`.
- **Prefect 3** run with a local Prefect server.
- Your platform code from Modules 2.9–2.12 (ingestion CLIs, dbt project,
  quality checks), plus PostgreSQL, MinIO, and the SFTP server in Docker.
- `pytest` and `ruff` for DAG tests and linting.

**A note on versions:** Airflow 3 changed a lot compared with Airflow 2
(for example the API server replacing the old webserver, assets replacing
"datasets", scheduler-managed backfills, a new task SDK import path, and
removal of the legacy SLA feature). Most blog posts and Stack Overflow
answers still describe Airflow 2. Always check that examples match your
installed version, and learn to recognise Airflow 2 code because you will
maintain it at work. Dagster and Prefect also evolve quickly — use their
current documentation.

---

## 3. How the module is organised

The eleven topics are grouped into five phases. Work through them **in
order**.

```text
Phase A — Orchestration Concepts                 (Basics)
  01 DAGs, dependencies, and scheduling concepts
  02 The limits of cron and why orchestrators exist

Phase B — Airflow Core                           (Basics → Intermediate)
  03 Apache Airflow architecture
  04 Airflow DAGs, operators, and the TaskFlow API
  05 Airflow connections, variables, hooks, and XComs

Phase C — Airflow in Production                  (Intermediate → Advanced)
  06 Sensors, deferrable operators, and data-aware scheduling
  07 Task retries, SLAs, and failure callbacks
  08 Backfills, catch-up, and partitioned runs

Phase D — Other Orchestration Philosophies       (Intermediate → Advanced)
  09 Dagster software-defined assets
  10 Prefect flows and tasks

Phase E — Quality of Orchestration Code          (Advanced)
  11 Testing and validating DAGs

Consolidate
  practice-questions.md
  Module mini-project: orchestrating the data platform
```

The dependency chain:

```text
01 ► 02 ► 03 ► 04 ► 05 ► 06 ► 07 ► 08 ► 09 ► 10 ► 11
ideas why  how  write  wire   wait    fail    rerun  assets flows  prove it
      not  it   DAGs   to     for     well    the    view   view   works
      cron runs        systems data           past
```

Why this order:

- Concepts (01) and the case against cron (02) give you tool-independent
  judgement before any tool's details.
- Airflow's architecture (03) explains *why* its DAG-writing rules (04)
  exist — such as keeping top-level code light.
- Connections and XComs (05) come before sensors and assets (06), which
  depend on them.
- Failure handling (07) and backfills (08) are what make a DAG production
  grade.
- Dagster (09) and Prefect (10) are easiest to understand as contrasts with
  Airflow.
- Testing (11) applies to all three and closes the module.

---

## 4. Suggested schedule

About **5 weeks at 8–10 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — concepts · Topic 02 — cron limits · Topic 03 — Airflow architecture (run Airflow locally) |
| 2 | Topic 04 — DAGs, operators, TaskFlow · Topic 05 — connections, variables, hooks, XComs |
| 3 | Topic 06 — sensors and assets · Topic 07 — retries and failure handling · Topic 08 — backfills |
| 4 | Topic 09 — Dagster · Topic 10 — Prefect |
| 5 | Topic 11 — testing DAGs · practice questions · mini-project |

---

## 5. How to study every topic (the orchestration loop)

```text
Read → Draw the workflow → Decide triggers & intervals → Build it thin
→ Run it → Break it (fail, hang, late data, overlap) → Watch the UI & logs
→ Re-run the past → Test it → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Draw the workflow**: tasks, dependencies, what each task reads and
   writes, and which system does the heavy work.
3. **Decide triggers and intervals**: time schedule, data arrival, or
   upstream asset update — and which data interval each run covers.
4. **Build it thin**: tasks call your existing CLIs, dbt, SQL, or services;
   the orchestrator passes the interval and run id, nothing more.
5. **Run it** and watch it in the UI.
6. **Break it**: make tasks fail, hang, run slowly, receive late data, or
   overlap with the next run.
7. **Watch the UI and logs**: task states, retries, durations, and alerts.
8. **Re-run the past**: clear and re-run tasks, run backfills, and confirm
   outputs are identical (idempotency from Module 2.12).
9. **Test it** (from Topic 11 onwards, always).
10. **Write down** what you learned in `module-2.13-notes.md`.
11. **Explain aloud** what happens, step by step, when a task fails at 3 a.m.

Keep one `orchestration_lab/` repository:

```text
orchestration_lab/
├── airflow/
│   ├── docker-compose.yaml
│   ├── dags/            # DAG files only — thin
│   ├── include/         # SQL, configs, helper modules
│   └── tests/
├── dagster_project/
├── prefect_project/
└── platform/            # your Module 2.9–2.12 code, installed as a package
```

---

## 6. Phase A — Orchestration Concepts (Basics)

### Topic 01 — [DAGs, dependencies, and scheduling concepts](01-dags-dependencies-and-scheduling-concepts.md)

**Why it comes first:** Every orchestrator — Airflow, Dagster, Prefect,
Argo, managed cloud services — is built on the same few ideas. Learn them
once and every tool becomes a variation.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Workflow, task, dependency, and the **DAG** (directed acyclic graph); why cycles are not allowed |
| Basics | Topological order, fan-out (one task feeds many), fan-in (many tasks feed one) |
| Basics | Triggers: **time-based** schedules (cron expressions, fixed intervals), **event-based** (a file arrived, a message was published), **data-aware** (an upstream dataset was updated), and manual runs |
| Intermediate | **Runs and task instances**: one execution of a workflow and of each task; task **states** (queued, running, success, failed, up for retry, skipped, upstream failed) |
| Intermediate | **Logical date and data interval**: a run for "2025-03-14" usually executes *after* that day ends — the concept from Module 2.12, now as the orchestrator's contract with your code |
| Intermediate | **Task granularity**: too coarse (one giant task, no partial retry) vs too fine (thousands of tiny tasks, scheduler overhead) |
| Intermediate | **Idempotent, deterministic tasks** as the requirement for safe retries and re-runs |
| Intermediate | Concurrency controls: max active runs, max parallel tasks, resource pools |
| Advanced | **Orchestration vs execution**: the orchestrator coordinates; heavy processing runs in databases, Spark, containers, or other services |
| Advanced | **Task-centric** (Airflow, Prefect) vs **asset-centric** (Dagster, Airflow assets) thinking: "run these steps" vs "keep these datasets up to date" |
| Advanced | Cross-workflow dependencies, and why one enormous DAG is usually worse than several connected ones |
| Advanced | The orchestrator as a source of operational metadata: run history, durations, lineage (Module 2.20) |

**How to learn it**

1. Read the topic file.
2. Draw the full data platform you built in Modules 2.9–2.12 as one or more
   DAGs, marking triggers, data intervals, and where heavy work runs.
3. Decide the granularity of each task and justify it.

**Hands-on exercise — `concepts/`**

1. Write a tiny tool-independent DAG runner in Python (tasks as functions,
   dependencies as a dict) that executes tasks in topological order, runs
   independent tasks in parallel (Module 2.10), records states, and refuses
   cycles.
2. Add retries per task and "upstream failed" propagation.
3. Pass a data interval to every task and run it for three past days.
4. Write a one-page note on what your runner is missing compared with a
   real orchestrator — you will tick items off during this module.

**Checkpoint — you are ready to move on when you can:**

- [ ] Explain a DAG, runs, task instances, and task states.
- [ ] Explain logical dates and data intervals with an example.
- [ ] Choose task granularity and justify it.
- [ ] Explain orchestration vs execution.
- [ ] Compare task-centric and asset-centric orchestration.

**Common mistakes:** confusing the run date with the data date; one task
that does everything; heavy data processing inside the orchestrator
itself.

---

### Topic 02 — [The limits of cron and why orchestrators exist](02-limits-of-cron-and-why-orchestrators-exist.md)

**Why here:** Many pipelines start as cron jobs, and some should stay that
way. Knowing precisely what cron lacks lets you justify an orchestrator —
or avoid adopting one unnecessarily.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Cron syntax and behaviour; systemd timers, Kubernetes CronJobs, and cloud schedulers as cron-like tools |
| Basics | What cron does well: simple, reliable, zero infrastructure for a few independent jobs |
| Intermediate | What cron lacks: dependencies between jobs, retries, run history, a UI, alerting, backfills, parameterised re-runs of past intervals, concurrency control, secret management, and distribution across machines |
| Intermediate | Classic cron failures: overlapping runs (a slow job still running when the next starts), missed runs while the machine was down, daylight-saving time surprises, silent failures with output lost |
| Intermediate | Workarounds and their limits: lock files (`flock`), wrapper scripts, "sleep until the file exists" |
| Advanced | The orchestrator landscape: Airflow, Dagster, Prefect, and others (e.g. Argo Workflows, Kestra, Temporal for application workflows), plus managed offerings of Airflow on the major clouds |
| Advanced | Selection criteria: team skills, number and type of pipelines, asset vs task orientation, deployment model (self-hosted vs managed), Kubernetes needs, cost, ecosystem and integrations |
| Advanced | The cost of an orchestrator: infrastructure, upgrades, security, and on-call — and when cron (plus good scripts from Module 2.12) is the right answer |

**How to learn it**

1. Read the topic file.
2. Schedule three dependent jobs from your platform with cron; make the
   first fail and the second run long; document every problem you see.
3. Write a decision table: for five situations, cron or orchestrator?

**Hands-on exercise — `cron_pain/`**

1. Run extract → transform → quality check as three cron entries in a
   container; show the transform running on missing data when extract
   fails.
2. Show an overlapping run corrupting output, then prevent it with `flock`.
3. Stop the container for three hours and show the missed runs are never
   executed.
4. Write a short ADR: "Why our team is adopting an orchestrator" (or why
   not), listing the specific gaps it closes.

**Checkpoint:**

- [ ] List at least eight things cron does not provide.
- [ ] Explain overlapping and missed runs.
- [ ] Name several orchestrators and what distinguishes them.
- [ ] Decide when cron is sufficient.

**Common mistakes:** adopting a heavyweight orchestrator for two jobs;
keeping dozens of dependent cron jobs chained by timing guesses ("the
extract usually finishes by 2:30").

---

## 7. Phase B — Airflow Core (Basics → Intermediate)

### Topic 03 — [Apache Airflow architecture](03-apache-airflow-architecture.md)

**Why here:** Airflow's rules — keep DAG files light, do not pass data
through XComs, use deferrable sensors — only make sense once you know how
its components work together.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Components: **scheduler**, **DAG processor** (parses DAG files), **API server** (serves the UI and REST API), **triggerer** (runs deferred waits), **executor**, **workers**, and the **metadata database** |
| Basics | How a DAG file becomes runs: files are parsed into DAG definitions, the scheduler creates DAG runs and task instances, the executor sends tasks to workers, results and states are recorded in the metadata database |
| Basics | Running Airflow locally with Docker Compose; the UI's main views (DAG list, grid, graph, task logs) |
| Intermediate | **Executors**: local, Celery (queue-based workers), Kubernetes (one pod per task), and the ability to use more than one executor; how to choose |
| Intermediate | **DAG parsing**: why top-level code in DAG files runs repeatedly, and why it must be fast and free of network calls or heavy imports |
| Intermediate | Where DAG code comes from: DAG folders and DAG bundles (for example from Git); DAG versioning in Airflow 3 |
| Intermediate | Providers: installable packages with operators, hooks, and sensors for external systems |
| Intermediate | Logs: task logs, remote log storage (e.g. object storage), and where to look when something fails |
| Advanced | Airflow 3's task execution model: tasks talk to Airflow through an API and task SDK instead of directly to the metadata database — and what that means for security and remote execution |
| Advanced | Scaling and reliability: multiple schedulers, database load, parsing performance, worker autoscaling |
| Advanced | Deployment options: Docker Compose (learning), the official Helm chart on Kubernetes, and managed Airflow services |
| Advanced | Recognising Airflow 2 architecture (webserver, datasets, SubDAGs, `execution_date`) when reading older code and documentation |

**How to learn it**

1. Read the topic file.
2. Start Airflow with Docker Compose; list every container and match it to
   a component in the architecture diagram.
3. Add a deliberately slow top-level statement to a DAG file and watch the
   parsing time grow.

**Hands-on exercise — `airflow_setup/`**

1. Run Airflow 3 locally with a PostgreSQL metadata database and the
   Celery or local executor; log in to the UI.
2. Write a trivial DAG, trigger it, and trace it through every component
   using logs.
3. Inspect the metadata database tables for DAG runs and task instances.
4. Measure DAG parse times and fix a DAG file with heavy top-level code.
5. Configure remote task logs to MinIO.
6. Draw your final architecture diagram with the executor you chose and
   why.

**Checkpoint:**

- [ ] Name every Airflow component and its role.
- [ ] Explain how a DAG file becomes running tasks.
- [ ] Choose an executor for a scenario.
- [ ] Explain why top-level code must be light.
- [ ] Recognise Airflow 2 vs Airflow 3 differences.

**Common mistakes:** database queries or API calls at the top level of DAG
files; SQLite metadata databases beyond local experiments; ignoring the
triggerer when using deferrable operators.

---

### Topic 04 — [Airflow DAGs, operators, and the TaskFlow API](04-airflow-dags-operators-and-taskflow-api.md)

**Why here:** Now you write DAGs. Airflow offers two styles — classic
operators and the Python-first TaskFlow API — and real projects use both.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Defining a DAG: `dag_id`, `schedule` (cron string, preset, timedelta, or asset), `start_date` (timezone-aware), `catchup`, `tags`, `default_args` |
| Basics | **Operators**: Bash, Python, SQL, and provider operators; tasks as operator instances |
| Basics | Dependencies with `>>` / `<<` and lists; the graph view |
| Basics | **TaskFlow API**: `@dag` and `@task` decorators; return values passed between tasks automatically |
| Intermediate | **Templating** with Jinja: `{{ ds }}`, `{{ data_interval_start }}`, `{{ data_interval_end }}`, `{{ run_id }}`, and passing them into your CLIs and SQL |
| Intermediate | **Task groups** for organising related tasks |
| Intermediate | **Dynamic task mapping** (`.expand()`, `.partial()`): one task per source table, file, or partition, decided at run time |
| Intermediate | **Branching** (`@task.branch`) and short-circuiting; **trigger rules** (`all_success`, `all_done`, `one_failed`, `none_failed`, …) |
| Intermediate | Running your platform code: calling Module 2.12 CLIs with the data interval, running dbt (`dbt build` via a Bash task, or integrations that map dbt models to tasks), and running tasks in isolated environments (virtualenv, Docker, or Kubernetes pod operators) |
| Advanced | Setup and teardown tasks (create and always clean up temporary resources) |
| Advanced | Concurrency controls: `max_active_runs`, `max_active_tasks`, **pools**, `priority_weight`, and queues |
| Advanced | DAG design guidelines: thin DAG files, logic in importable packages, one DAG per logical pipeline, clear ownership tags |
| Advanced | Recognising and migrating Airflow 2 patterns (`schedule_interval`, `execution_date`, old import paths) |

**How to learn it**

1. Read the topic file.
2. Write the same pipeline twice — with classic operators and with
   TaskFlow — and compare readability.
3. For your ingestion platform, decide which parts should be dynamically
   mapped.

**Hands-on exercise — `dags/orders_daily.py`**

1. Build a daily DAG: dynamic-mapped extraction per source (calling your
   Module 2.9 CLIs with `data_interval_start`/`end`) → bronze-to-silver
   (Module 2.12 CLI) → `dbt build` for gold → quality gate (Module 2.11) →
   publish.
2. Use a task group per layer and a branch that skips publishing when the
   quality gate reports critical failures (with an alert task using
   `one_failed`).
3. Limit concurrent extraction with a pool sized to the source's rate
   limits.
4. Add setup/teardown tasks that create and always drop a staging schema.
5. Run it for three past dates and confirm idempotent outputs.

**Checkpoint:**

- [ ] Write DAGs with operators and with TaskFlow.
- [ ] Pass data intervals to tasks through templating or context.
- [ ] Use dynamic task mapping, task groups, branching, and trigger rules.
- [ ] Control concurrency with pools and DAG limits.

**Common mistakes:** `datetime.now()` instead of the data interval; naive
`start_date`s; business logic written inside DAG files; hundreds of static
tasks where mapping would do; unbounded parallelism against a source.

---

### Topic 05 — [Airflow connections, variables, hooks, and XComs](05-airflow-connections-variables-hooks-and-xcoms.md)

**Why here:** DAGs must reach databases, object stores, APIs, and SFTP
servers securely, and tasks must share small pieces of information. Airflow
has specific mechanisms for both — and well-known ways to misuse them.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Connections**: stored credentials and endpoints identified by a connection id; creating them in the UI, CLI, or environment variables (`AIRFLOW_CONN_<ID>`) |
| Basics | **Variables**: small configuration values; reading them inside tasks (not at the top level of DAG files) |
| Basics | **Hooks**: Python interfaces to external systems that use connections (e.g. PostgreSQL, S3-compatible storage, SFTP, HTTP hooks) |
| Intermediate | **Secrets backends**: fetching connections and variables from a secrets manager instead of the metadata database (cloud secrets managers in Module 2.18) |
| Intermediate | **XComs**: small values passed between tasks (TaskFlow return values are XComs); size limits and why they live in the metadata database by default |
| Intermediate | The rule: **pass references, not data** — pass object-storage paths, table names, row counts, and run ids; never DataFrames |
| Intermediate | Custom XCom backends (for example storing larger values in object storage) and their trade-offs |
| Advanced | Writing a **custom hook** (and operator) for an internal API, reusing your Module 2.9 client |
| Advanced | Per-environment configuration: connections and variables for dev, staging, and production without code changes |
| Advanced | Security: least-privilege connection credentials, masking secrets in logs, and who can see connections in the UI |

**How to learn it**

1. Read the topic file.
2. Create every connection your platform needs using environment variables
   only, with no secrets in the DAG repository.
3. Try to pass a 50 MB DataFrame through XCom and observe the effect on the
   metadata database; then redesign with object-storage paths.

**Hands-on exercise — `airflow_integrations/`**

1. Define connections for PostgreSQL, MinIO, SFTP, and your mock API via
   environment variables (and optionally a local secrets backend).
2. Refactor `orders_daily` so tasks use hooks for connections and pass only
   paths, row counts, and run ids through XComs.
3. Write `MockApiHook` and `MockApiExtractOperator` wrapping your Module 2.9
   client, with the connection id as a parameter.
4. Read a variable-controlled lookback window (Module 2.12) inside a task.
5. Verify that secrets are masked in task logs.

**Checkpoint:**

- [ ] Configure connections and variables without secrets in code.
- [ ] Use hooks to talk to external systems.
- [ ] Use XComs only for small metadata.
- [ ] Write a custom hook and operator.

**Common mistakes:** passwords in DAG files or Git; reading variables at
parse time; large payloads through XCom; one shared "admin" connection for
everything.

---

## 8. Phase C — Airflow in Production (Intermediate → Advanced)

### Topic 06 — [Sensors, deferrable operators, and data-aware scheduling](06-sensors-deferrable-operators-and-data-aware-scheduling.md)

**Why here:** Real pipelines wait — for partner files, for upstream DAGs,
for external jobs to finish. Waiting badly wastes worker slots; waiting
well is free. Data-aware scheduling removes many waits altogether.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Sensors**: tasks that wait until a condition is true (file exists, key in object storage, SQL returns rows, external task finished) |
| Basics | `poke_interval`, `timeout`, and `soft_fail` |
| Intermediate | Sensor modes: `poke` (holds a worker slot while waiting) vs `reschedule` (releases it between checks) |
| Intermediate | **Deferrable operators**: the task suspends itself and a lightweight **trigger** in the triggerer process waits asynchronously — no worker slot used |
| Intermediate | **Data-aware scheduling with assets**: producer tasks declare the assets they update; consumer DAGs are scheduled when those assets update, instead of by time |
| Intermediate | Combining asset and time conditions; asset events and their metadata |
| Advanced | Writing a **custom sensor** and a **custom trigger** (async code from Module 2.10) — for example waiting for your SFTP `.done` marker file |
| Advanced | Cross-DAG dependencies: assets vs external-task sensors vs triggering other DAGs — trade-offs |
| Advanced | Event-driven scheduling from external systems (e.g. messages or storage notifications) — awareness level; streaming in Module 2.16 |
| Advanced | Timeouts and failure policies for waits that never end, and alerting when an expected file does not arrive by its deadline (freshness from Module 2.1) |

**How to learn it**

1. Read the topic file.
2. Run 50 file sensors in `poke` mode with a small worker pool and watch
   them block every slot; switch to deferrable and compare.
3. Redraw your platform so that downstream DAGs are triggered by asset
   updates instead of fixed times.

**Hands-on exercise — `dags/partner_files.py` and `dags/assets.py`**

1. Wait for the logistics partner's SFTP file and `.done` marker with a
   deferrable approach (a custom trigger if no suitable one exists), then
   run the Module 2.9 SFTP ingestion.
2. Declare assets for `bronze.orders`, `silver.orders`, and
   `gold.daily_revenue`; schedule the silver and gold DAGs on asset
   updates.
3. Add a deadline: if the partner file has not arrived by 07:00, alert and
   mark the run appropriately.
4. Compare worker-slot usage with poke, reschedule, and deferrable modes.

**Checkpoint:**

- [ ] Explain poke vs reschedule vs deferrable waiting.
- [ ] Write a custom sensor or trigger.
- [ ] Schedule DAGs from asset updates.
- [ ] Handle waits that never complete.

**Common mistakes:** hundreds of poking sensors starving workers; sensors
without timeouts; chains of time-based DAGs guessing when upstream
finishes; forgetting to run the triggerer.

---

### Topic 07 — [Task retries, SLAs, and failure callbacks](07-task-retries-slas-and-failure-callbacks.md)

**Why here:** Everything fails eventually. Production orchestration is
defined by what happens next: automatic recovery for transient problems,
fast failure for permanent ones, and alerts that let a human fix the rest
quickly.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Task-level `retries`, `retry_delay`, exponential backoff, and maximum delay |
| Basics | `execution_timeout` so a hung task fails instead of running forever |
| Basics | Callbacks: `on_failure_callback`, `on_retry_callback`, `on_success_callback` at task and DAG level |
| Intermediate | **Orchestrator retries vs in-task retries**: retrying a whole task (coarse, after in-task retries from Module 2.9 are exhausted) — and why retries require idempotent tasks (Module 2.12) |
| Intermediate | Failing fast on permanent errors: raising an exception that should not be retried (e.g. bad configuration, contract violation) |
| Intermediate | **Alerts with context**: DAG, task, data interval, try number, error summary, log link, owner, runbook link — via notifiers to chat or email |
| Intermediate | **Timeliness guarantees**: expressing "must finish by 07:00" — the legacy SLA mechanism of Airflow 2 was removed in Airflow 3, and newer deadline-alert features replace it; check what your version supports and complement it with freshness checks on the data itself (Module 2.11) |
| Advanced | Alert design: severity by dataset tier, grouping alerts, avoiding alert fatigue, and routing to the owning team |
| Advanced | Handling partial failure in mapped tasks: continue other partitions, then fail or alert at the end |
| Advanced | Runbooks: for each critical DAG, what to check and which re-run commands to use |
| Advanced | Operational metrics: task duration trends, failure rates, and queue times (monitoring in Module 2.20) |

**How to learn it**

1. Read the topic file.
2. Classify ten failure types (API `503`, bad credentials, schema contract
   violation, worker killed, database deadlock, disk full, late partner
   file, logic bug, quality gate failure, upstream DAG failed) into "retry
   automatically", "fail fast", or "wait and alert".
3. Write a runbook for your `orders_daily` DAG.

**Hands-on exercise — `reliability/`**

1. Set retries, exponential backoff, and execution timeouts per task based
   on your classification.
2. Implement a notifier that sends a structured alert (to a local webhook
   receiver, chat, or email) with DAG, task, interval, try number, error,
   log link, owner, and runbook link.
3. Make a task raise a non-retryable error for contract violations and
   show it failing immediately.
4. Implement a completion deadline for the gold DAG with your version's
   deadline or timeout features, plus a freshness check task.
5. Let one mapped extraction fail out of ten; continue the others and
   report the failed partition clearly.

**Checkpoint:**

- [ ] Configure retries, backoff, and timeouts deliberately.
- [ ] Distinguish orchestrator retries from in-task retries.
- [ ] Send actionable failure alerts.
- [ ] Monitor completion deadlines and data freshness.

**Common mistakes:** the same retries for every task; retrying
non-idempotent tasks; no execution timeouts; alerts without context or
owner; SLA features copied from Airflow 2 tutorials into Airflow 3.

---

### Topic 08 — [Backfills, catch-up, and partitioned runs](08-backfills-catchup-and-partitioned-runs.md)

**Why here:** Every pipeline eventually needs to process the past: a new
DAG for historical data, a logic fix, a recovered outage. The orchestrator
turns the backfill pattern from Module 2.12 into managed, observable runs.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Catch-up**: whether a DAG runs all missed intervals since `start_date` when enabled or unpaused (and why it is usually off by default today) |
| Basics | **Backfills**: running a DAG for a chosen range of past intervals |
| Basics | Clearing tasks and runs to re-run them |
| Intermediate | Airflow 3 backfills managed by the scheduler (created from the UI, CLI, or API) vs Airflow 2's CLI-driven backfills |
| Intermediate | Controlling backfill load: maximum active runs, pools, run ordering (newest or oldest first), and not starving daily runs |
| Intermediate | Re-processing behaviour: skip existing successful runs vs re-run failed only vs re-run everything |
| Intermediate | **Partitioned runs**: one run per data interval as a partition; run parameters for re-processing a specific date or source |
| Advanced | Backfills after logic changes: combining with shadow tables and swaps (Module 2.12) and invalidating downstream assets |
| Advanced | Changing a schedule or `start_date` on an existing DAG and its effect on history |
| Advanced | Very large backfills (years): estimating time and cost, batching, running with more parallel workers, and monitoring progress |
| Advanced | Asset partitions and time-partitioned assets as a different model for the same need (explored in Dagster, Topic 09) |

**How to learn it**

1. Read the topic file.
2. Enable catch-up on a DAG with a start date 60 days ago and observe what
   happens; then disable it and backfill deliberately.
3. Plan a 2-year backfill on paper: runs, parallelism, time, and impact on
   daily runs.

**Hands-on exercise — `backfills/`**

1. Run a 90-day backfill of `orders_daily` with at most 4 concurrent runs
   through a dedicated pool, while daily runs continue.
2. Re-run only failed intervals from the backfill.
3. Add a manually triggered "reprocess" DAG that takes `source` and
   `start`/`end` as validated run parameters.
4. After a revenue logic change, backfill gold into a shadow table and swap
   (reusing Module 2.12's pattern), orchestrated as one DAG.
5. Verify every backfilled partition matches a clean full rebuild.

**Checkpoint:**

- [ ] Explain catch-up and backfills and when to use each.
- [ ] Run a controlled backfill that does not disrupt daily runs.
- [ ] Re-run selected intervals or failed tasks only.
- [ ] Orchestrate a logic-change backfill with a shadow swap.

**Common mistakes:** catch-up enabled by accident, launching hundreds of
runs; backfills that overload sources and databases; backfilling
non-idempotent tasks; changing `start_date` casually.

---

## 9. Phase D — Other Orchestration Philosophies (Intermediate → Advanced)

### Topic 09 — [Dagster software-defined assets](09-dagster-software-defined-assets.md)

**Why here:** Airflow asks "which tasks should run?". Dagster asks "which
**data assets** should exist, and are they up to date?". This asset-centric
model maps naturally onto medallion layers and dbt models.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Software-defined assets**: `@asset` functions that produce a named dataset; dependencies declared by function parameters or `deps` |
| Basics | Materialisations, the asset graph, and the Dagster UI (`dagster dev`); the `Definitions` object |
| Basics | Jobs (selections of assets), schedules, and sensors |
| Intermediate | **Resources** (configurable connections and clients) and **I/O managers** (how asset outputs are stored and loaded) |
| Intermediate | **Partitions**: daily, static (e.g. per country), multi-dimensional, and dynamic partitions; partitioned backfills |
| Intermediate | **Asset checks**: data quality checks attached to assets (connecting to Module 2.11) |
| Intermediate | **dbt integration**: every dbt model becomes an asset in the graph |
| Advanced | **Declarative automation**: conditions under which assets materialise automatically (e.g. when upstream updates, on a cron, when missing) |
| Advanced | Observability: asset metadata, lineage, freshness, and run history |
| Advanced | Ops and graphs (the lower-level task model) and when you still need them |
| Advanced | Project structure, code locations, and deployment options (self-hosted and managed) |
| Advanced | Strengths and weaknesses vs Airflow: lineage-first design and local development vs ecosystem size and existing team knowledge |

**How to learn it**

1. Read the topic file.
2. Re-model your platform as assets on paper: every table and file your
   pipelines produce, with its upstream assets and partitions.
3. Compare the resulting graph with your Airflow DAGs.

**Hands-on exercise — `dagster_project/`**

1. Define assets for bronze, silver, and gold orders, daily-partitioned,
   calling your platform code through resources (PostgreSQL, MinIO).
2. Load your Module 2.12 dbt project as assets downstream of silver.
3. Attach asset checks for grain uniqueness and freshness.
4. Add a sensor for new partner files and declarative automation so gold
   updates when silver updates.
5. Backfill 30 partitions from the UI and compare the experience with
   Airflow's backfills.

**Checkpoint:**

- [ ] Explain software-defined assets and the asset graph.
- [ ] Use resources, I/O managers, and partitions.
- [ ] Integrate dbt models as assets.
- [ ] Attach asset checks and automation conditions.
- [ ] Compare Dagster's model with Airflow's.

**Common mistakes:** translating Airflow DAGs task-for-task into ops
instead of thinking in assets; I/O managers that load huge datasets into
memory; assets without partitions for time-series data.

---

### Topic 10 — [Prefect flows and tasks](10-prefect-flows-and-tasks.md)

**Why here:** Prefect takes a third approach: ordinary Python functions
become orchestrated flows with minimal ceremony, and dynamic, code-driven
workflows are natural.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `@flow` and `@task` decorators; running flows as normal Python; the Prefect UI and server |
| Basics | Flow parameters (validated with type hints and Pydantic) and logging |
| Intermediate | Task features: retries, retry delays, timeouts, and **caching** (cache policies and expiry) |
| Intermediate | Concurrency: `.submit()`, `.map()`, futures, and task runners (threads by default; distributed runners as options) |
| Intermediate | Results and persistence, and **states** (completed, failed, cached, crashed) with state hooks |
| Intermediate | **Deployments**: `serve()` for simple long-running processes vs `deploy()` with **work pools** and **workers**; schedules and parameters |
| Advanced | **Events and automations**: triggering flows from events and reacting to state changes |
| Advanced | Blocks and variables for configuration and credentials |
| Advanced | Transactions for grouping tasks with rollback behaviour (Prefect 3) — awareness |
| Advanced | Strengths and weaknesses vs Airflow and Dagster: very low ceremony and dynamic flows vs less asset-centric lineage and a different operating model |

**How to learn it**

1. Read the topic file.
2. Convert one of your Module 2.10 concurrent pipelines into a Prefect flow
   with minimal code changes.
3. Deploy it with a schedule and a work pool, and trigger it with an event.

**Hands-on exercise — `prefect_project/`**

1. Write an `ingest_sources` flow that maps an extraction task over all
   sources (calling your Module 2.9 code) with retries and timeouts.
2. Add caching so re-running the flow for the same interval skips
   completed extractions.
3. Deploy it with a daily schedule and parameters (`start`, `end`), served
   by a worker from a local work pool.
4. Add an automation that runs the transformation flow after ingestion
   completes, and a notification on failure.
5. Compare lines of code, local development experience, and observability
   with your Airflow and Dagster versions.

**Checkpoint:**

- [ ] Write Prefect flows and tasks with retries, timeouts, and caching.
- [ ] Run tasks concurrently with `.submit()` and `.map()`.
- [ ] Deploy flows with schedules, work pools, and workers.
- [ ] Use automations to chain or react to flows.

**Common mistakes:** caching tasks whose outputs depend on time or
external state; treating flows as scripts with no deployment; mixing heavy
processing into the orchestrator process instead of the right execution
environment.

---

## 10. Phase E — Quality of Orchestration Code (Advanced)

### Topic 11 — [Testing and validating DAGs](11-testing-and-validating-dags.md)

**Why last:** A DAG that fails to import takes down every pipeline in its
file; a DAG with a wrong dependency silently publishes unchecked data.
Orchestration code needs tests like any other code — plus some special
ones.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Import tests**: every DAG file loads without errors (load all DAGs and assert no import errors) |
| Basics | Running a DAG locally in one process for debugging (`dag.test()` / `airflow dags test`) |
| Basics | Unit-testing task logic as plain Python functions — easiest when DAG files are thin |
| Intermediate | **Structure tests**: expected tasks and dependencies exist; no cycles; quality gates sit between transform and publish |
| Intermediate | **Policy tests** for all DAGs: owners and tags present, retries and timeouts set, no naive start dates, catch-up deliberate, no forbidden operators |
| Intermediate | Linting DAG code (e.g. Ruff's Airflow-specific rules) and parse-time budgets |
| Intermediate | Mocking hooks and connections in unit tests; test connections via environment variables |
| Advanced | **Integration tests**: running a DAG end to end against Docker services with a small dataset, and asserting on outputs |
| Advanced | Testing templates and data intervals: rendering templated fields for a given logical date |
| Advanced | Testing Dagster assets (materialising in-process with test resources) and Prefect flows (calling flows directly in tests) |
| Advanced | CI for orchestration code: lint, import, structure, policy, and unit tests on every pull request; integration tests on merge (CI/CD details in Module 2.18) |
| Advanced | Validating deployments: ensuring the scheduler sees the new version and no DAG disappeared |

**How to learn it**

1. Read the topic file.
2. Break DAG files in five different ways (syntax error, missing import,
   cycle, missing retries, naive `start_date`) and write a test that
   catches each.
3. Run your whole test suite in a clean container as CI would.

**Hands-on exercise — `airflow/tests/`**

1. Write a DAG import test and a parse-time budget test.
2. Write structure tests for `orders_daily` (tasks, dependencies, quality
   gate before publish) and policy tests for every DAG.
3. Unit-test your custom hook, operator, sensor, and trigger with mocks.
4. Test rendered templates for a fixed logical date.
5. Write an integration test that runs `orders_daily` for one date against
   Docker services and checks gold outputs and quality results.
6. Add equivalent tests for one Dagster asset group and one Prefect flow.
7. Wire lint, import, structure, policy, and unit tests into a single
   `make test` (or script) command suitable for CI.

**Checkpoint:**

- [ ] Write import, structure, and policy tests for DAGs.
- [ ] Unit-test custom operators, hooks, sensors, and triggers.
- [ ] Run integration tests of a whole DAG.
- [ ] Test Dagster assets and Prefect flows.

**Common mistakes:** testing only by clicking "trigger" in the UI; logic
buried in DAG files where it cannot be unit-tested; no import test, so one
broken file hides many DAGs.

---

## 11. Consolidate — practice questions

When all eleven topics are done, open
[`practice-questions.md`](practice-questions.md). For every question:

1. Draw the workflow: tasks or assets, dependencies, triggers, data
   intervals, and where heavy work runs.
2. Choose schedule vs data-aware vs event-driven triggering and justify it.
3. Define retries, timeouts, alerts, and deadlines per task.
4. Explain backfill and re-run behaviour.
5. Implement it in the requested tool and write tests.
6. Explain how you would build the same thing in the other two tools.

---

## 12. Module mini-project — orchestrating the data platform

This is the proof that you have finished the module.

**Scenario:** Your platform from Modules 2.9–2.12 (five ingestion sources,
bronze → silver framework, dbt gold models, quality system) currently runs
by hand. Leadership needs it to run itself, recover from routine failures,
alert the right people, and support backfills — with gold revenue ready by
07:00 every day.

Build `platform_orchestration/` with:

1. **Airflow (primary)** —
   - Ingestion DAGs per source: dynamic task mapping, pools matching source
     rate limits, deferrable waiting for SFTP partner files, and
     connections from environment variables or a secrets backend.
   - Transformation DAGs scheduled by **asset updates**, running the
     Module 2.12 framework and `dbt build`, passing only references through
     XComs.
   - Quality gates and write–audit–publish (Module 2.11) as explicit tasks
     with branching and trigger rules.
   - Retries, backoff, timeouts, and non-retryable errors per task;
     structured alerts with runbook links; a 07:00 deadline and freshness
     checks.
   - A controlled 180-day backfill and a parameterised reprocess DAG.
2. **Dagster slice** — the orders bronze → silver → gold path as
   partitioned assets with dbt integration, asset checks, and declarative
   automation.
3. **Prefect slice** — the ingestion flows with mapping, caching,
   deployments, and an automation chaining transformation.
4. **Testing and CI** — import, structure, policy, unit, and integration
   tests for Airflow, plus tests for the Dagster and Prefect slices,
   runnable with one command.
5. **Operations** — runbooks for every critical DAG and a short
   operations guide (how to re-run a day, run a backfill, pause a source,
   and rotate a credential).
6. **Decision record** — an ADR comparing Airflow, Dagster, and Prefect for
   this platform, based on your experience building all three slices.

**Grading yourself:** a full day runs end to end without manual steps;
killing a worker or failing a source causes retries or clear alerts, never
silent bad data; a 180-day backfill completes without delaying the daily
07:00 deadline; and every DAG passes the test suite before deployment.

---

## 13. Module self-assessment — exit criteria

Only move to Module 2.14 when you can tick every box without looking at your
notes:

- [ ] I can explain orchestration concepts independent of any tool.
- [ ] I can explain when cron is enough and when it is not.
- [ ] I can explain Airflow's architecture and how DAGs become tasks.
- [ ] I can write Airflow DAGs with operators, TaskFlow, mapping, groups,
      branching, and pools.
- [ ] I can use connections, hooks, and XComs safely.
- [ ] I can use deferrable waiting and asset-based scheduling.
- [ ] I can design retries, timeouts, deadlines, and actionable alerts.
- [ ] I can run safe backfills and parameterised re-runs.
- [ ] I can build asset-based pipelines in Dagster and flows in Prefect.
- [ ] I can test and validate orchestration code in CI.
- [ ] I have finished all practice questions and the mini-project.

---

## 14. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| Apache Airflow documentation (3.x) — architecture, DAGs, TaskFlow, dynamic task mapping, assets, deferrable operators, backfills, best practices, and the "Upgrading to Airflow 3" guide | 03–08, 11 |
| Airflow provider package documentation for the systems you use | 04, 05, 06 |
| *Data Pipelines with Apache Airflow* — Bas Harenslak and Julian de Ruiter (Manning; check for an edition covering recent Airflow versions) | 03–08, 11 |
| Dagster documentation — assets, partitions, resources, I/O managers, asset checks, dbt integration, declarative automation, testing | 09, 11 |
| Prefect documentation (3.x) — flows, tasks, caching, deployments, work pools, automations | 10, 11 |
| *Fundamentals of Data Engineering* — Joe Reis and Matt Housley, sections on orchestration as an undercurrent | 01, 02 |
| Maxime Beauchemin — "Functional Data Engineering" essay (orchestration of idempotent, partitioned tasks) | 01, 08 |

---

## 15. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| Submitting heavy work to distributed engines | 2.14 Distributed Processing with PySpark |
| Orchestrating table maintenance (compaction, vacuum) | 2.15 Lakehouse Table Formats |
| Event-driven triggers and continuous jobs | 2.16 Streaming and Event-Driven Data |
| Managed orchestrators and cloud scheduling services | 2.17 Cloud Storage and Cloud Data Platforms |
| Running tasks in containers and on Kubernetes; secrets backends; CI/CD for DAGs | 2.18 Containers, Infrastructure, and CI/CD for Data |
| End-to-end pipeline smoke tests | 2.19 Testing Data Pipelines |
| Run metadata, OpenLineage, alerting, and on-call | 2.20 Observability, Lineage, Governance, and Security |
| Cost of idle workers and over-provisioned schedulers | 2.21 Performance, Scaling, and Cost Optimization |

An orchestrator is only as good as the tasks it runs. The habits you build
here — thin DAGs calling idempotent, interval-scoped tasks; waiting without
wasting resources; failing loudly with context; and re-running the past
safely — are what turn a collection of scripts into a data platform that
runs itself.
