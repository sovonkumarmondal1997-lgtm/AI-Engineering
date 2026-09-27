# Roadmap — Module 2.18: Containers, Infrastructure, and CI/CD for Data

This is the learning roadmap for the eighteenth module of Stage 2, **Python
for Data Engineering**. It tells you **what** to learn about containers,
infrastructure as code, CI/CD, environments, and secrets, **in what
order**, **how** to learn each topic, and **how to prove to yourself** that
you have learned it before you move on.

By now you can build a complete data platform: ingestion, transformation,
quality, orchestration, Spark, lakehouse tables, streaming, and cloud
services. But so far you created much of it by hand: you ran `docker
compose up` from recipes, clicked or typed cloud resources into existence,
and deployed code by copying it. That does not survive a team, an audit,
or a 3 a.m. incident. Production data engineering needs:

- **Containers**, so a pipeline runs identically on a laptop, in CI, and in
  production.
- **Kubernetes** concepts, because orchestrators, Spark, Flink, and Kafka
  increasingly run on it.
- **Infrastructure as code**, so buckets, roles, catalogs, and warehouses
  are reviewed, versioned, and reproducible.
- **CI/CD**, so every change is tested automatically and deployed the same
  way every time.
- **Environments and promotion**, so changes reach production only after
  proving themselves in dev and staging.
- **Secrets management**, so credentials are never in code, images, logs,
  or state files.

---

## 1. Module outcome

By the end of this module you will be able to:

- Build small, secure, reproducible **Docker images** for Python, dbt, and
  Spark workloads with `uv`, multi-stage builds, and non-root users.
- Run a full local data stack with **Docker Compose**: health checks,
  dependencies, volumes, profiles, and one-shot set-up services.
- Explain **Kubernetes** building blocks for data workloads — pods, Jobs,
  CronJobs, resources, service accounts, operators, autoscaling — and run
  data jobs on a local cluster.
- Manage data infrastructure with **Terraform**: providers, resources,
  modules, remote state, plans, and safe changes.
- Build **CI pipelines** that lint, type-check, test, validate DAGs, run dbt
  slim CI, check contracts, build and scan images, and plan infrastructure.
- Promote code and infrastructure through **dev, staging, and production**
  with approvals, immutable artifacts, and rollback plans.
- Store, deliver, and rotate credentials with **cloud secrets managers** and
  workload identity — and respond correctly to a leaked secret.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.17. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Processes, signals, filesystems, networking, permissions | Stage 0 — OS Fundamentals | Containers are isolated processes; signals and permissions matter inside them |
| Command line and shell scripts | Stage 0 — Command Line | Entrypoints, build scripts, and CI steps |
| Git and GitHub, local secrets hygiene, `uv` workspaces | Stage 0 — Developer Environment | CI runs on Git events; local `.env` hygiene is **not** re-taught |
| Packages, `pyproject.toml`, lock files, Ruff, type hints | Stage 1 — Module 1.6 | Images and CI are built from these |
| pytest and test design | Stage 1 — Module 1.7 | CI runs your tests |
| Configuration, logging, dependency upgrades and supply chain awareness | Stage 1 — Module 1.10 | Environment configuration and pinned, scanned dependencies |
| Alembic migrations | Stage 2 — Module 2.7 | Deployed in order during promotion |
| Contract and schema-diff checks | Stage 2 — Modules 2.11 and 2.16 | Run in CI |
| Config-driven pipelines, dbt | Stage 2 — Module 2.12 | Environment overlays and dbt slim CI |
| Airflow and DAG tests | Stage 2 — Module 2.13 | Deployed and tested by CI/CD |
| Spark jobs and packaging | Stage 2 — Module 2.14 | Spark images and Spark on Kubernetes |
| Table formats, time travel, clones | Stage 2 — Module 2.15 | Data rollback and ephemeral environments |
| Streaming infrastructure and consumer lag | Stage 2 — Module 2.16 | Kafka and Flink on Kubernetes; autoscaling on lag |
| Cloud storage, IAM, OIDC federation, warehouses, managed Spark | Stage 2 — Module 2.17 | The resources you now manage as code |

Earlier modules used Docker Compose files as working recipes. This module
teaches Docker and Compose properly, from first principles, so you can
write and debug them yourself.

**Tools needed:**

- **Docker** with BuildKit and `buildx` (multi-platform builds).
- A local Kubernetes cluster: **kind**, **k3d**, or **minikube**, plus
  `kubectl` and **Helm**.
- **Terraform** (or the open-source fork OpenTofu), `tflint`, and an IaC
  security scanner (e.g. Checkov or Trivy).
- A **GitHub** repository with **GitHub Actions** (other CI systems use the
  same ideas).
- `pre-commit`, a secret scanner (e.g. `gitleaks`), and an image scanner
  (e.g. Trivy).
- Your cloud account and budget from Module 2.17 (with teardown scripts),
  and optionally a local AWS emulator for Terraform experiments.
- Your platform code from Modules 2.9–2.17.

---

## 3. How the module is organised

The seven topics are grouped into five phases. Work through them **in
order**.

```text
Phase A — Containers                                  (Basics → Intermediate)
  01 Docker images for Python pipelines
  02 Docker Compose for local data stacks

Phase B — Running Containers at Scale                 (Intermediate → Advanced)
  03 Kubernetes concepts for data workloads

Phase C — Infrastructure as Code                      (Intermediate → Advanced)
  04 Terraform basics for data infrastructure

Phase D — Delivering Changes                          (Intermediate → Advanced)
  05 CI pipelines for data projects
  06 Environment promotion: dev, staging, and prod

Phase E — Protecting Credentials                      (Advanced)
  07 Cloud secrets managers

Consolidate
  practice-questions.md
  Module mini-project: shipping the data platform like software
```

The dependency chain:

```text
01 ──► 02 ──► 03 ──► 04 ──► 05 ──► 06 ──► 07
package  run a   run at   create   test &   promote   deliver
one job  stack   scale    infra    build    safely    secrets
                          as code  every               safely
                                   change
```

Why this order:

- An image (01) is the unit that Compose (02), Kubernetes (03), and CI (05)
  all run.
- Kubernetes (03) comes before Terraform (04) so that you know what
  infrastructure data workloads need before you define it as code.
- CI (05) builds and tests the images and plans the infrastructure;
  promotion (06) moves those artifacts through environments.
- Secrets (07) come last because they touch every earlier layer: images,
  Compose, Kubernetes, Terraform, CI, and each environment.

---

## 4. Suggested schedule

About **4 weeks at 8–10 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — Docker images · Topic 02 — Docker Compose |
| 2 | Topic 03 — Kubernetes for data workloads |
| 3 | Topic 04 — Terraform · Topic 05 — CI pipelines |
| 4 | Topic 06 — environment promotion · Topic 07 — secrets managers · practice questions · mini-project |

---

## 5. How to study every topic (the delivery loop)

```text
Read → Write it as code → Review the diff → Run it locally → Run it in CI
→ Break it (bad change, failed step, leaked value) → Recover or roll back
→ Measure (size, time, cost) → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Write it as code**: Dockerfile, Compose file, Kubernetes manifest,
   Terraform module, workflow file — never click-ops.
3. **Review the diff** as a reviewer would: what changes, what could break,
   what does it cost, what can it access?
4. **Run it locally** (Docker, kind, a local Terraform plan).
5. **Run it in CI** once Topic 05 is done — every later exercise must pass
   CI.
6. **Break it**: introduce a bug, a failing test, a bad Terraform change, a
   wrong permission, or a secret in a file.
7. **Recover or roll back** and time how long it takes.
8. **Measure** image size, build time, CI duration, and cloud cost.
9. **Write down** the rule you learned in `module-2.18-notes.md`.
10. **Explain aloud** how a change travels from a commit to production.

Keep one `platform_delivery/` repository (you will evolve it into the
mini-project):

```text
platform_delivery/
├── docker/              # Dockerfiles for pipeline, dbt, and Spark images
├── compose/             # local stack Compose files and overrides
├── k8s/                 # manifests and Helm values
├── infra/
│   ├── modules/         # reusable Terraform modules
│   └── envs/            # dev, staging, prod configurations
├── .github/workflows/   # CI and CD workflows
├── src/ and dbt/        # platform code from earlier modules
└── docs/                # runbooks, promotion process, secrets inventory
```

---

## 6. Phase A — Containers (Basics → Intermediate)

### Topic 01 — [Docker images for Python pipelines](01-docker-images-for-python-pipelines.md)

**Why it comes first:** "It works on my machine" is not acceptable in
production. A container image packages your code, its exact dependencies,
and its runtime so it behaves the same everywhere — and every later topic
runs images.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Containers vs virtual machines; images, containers, layers, and registries |
| Basics | Core commands: `docker build`, `run`, `ps`, `logs`, `exec`, `stop`, `rm`, `images`, `push`, `pull` |
| Basics | Dockerfile instructions: `FROM`, `WORKDIR`, `COPY`, `RUN`, `ENV`, `ARG`, `USER`, `ENTRYPOINT`, `CMD`, `EXPOSE`, `HEALTHCHECK` |
| Basics | Build context and `.dockerignore` (never sending `.git`, data files, or `.env` into the build) |
| Intermediate | **Layer caching**: ordering instructions so dependency installation is cached and only code changes rebuild |
| Intermediate | Python base images: slim Debian-based images vs Alpine (and why Alpine's C library can break or slow Python wheels) |
| Intermediate | **Installing with `uv`** in images: copying the `uv` binary from its official image, installing from the lock file without dev dependencies, cache mounts, and compiled bytecode |
| Intermediate | **Multi-stage builds**: build dependencies in one stage, copy only the virtual environment and code into a small runtime stage |
| Intermediate | Running as a **non-root user**; `PYTHONUNBUFFERED` for immediate logs; configuration via environment variables and CLI arguments (the run context from Module 2.12) |
| Advanced | **PID 1 and signals**: exec-form `ENTRYPOINT`, an init process (e.g. `--init` or tini) so `SIGTERM` reaches your code and graceful shutdown (Module 2.10) works |
| Advanced | Reproducibility: pinning base images by digest, locked dependencies, immutable tags (git SHA) vs mutable tags (`latest`) |
| Advanced | **Security**: vulnerability scanning, SBOMs, minimal images (distroless awareness), no secrets in layers — using build secrets for private package indexes |
| Advanced | **Multi-platform builds** (`linux/amd64` and `linux/arm64`) with `buildx` for ARM laptops and ARM cloud instances |
| Advanced | Data-specific images: dbt images, Spark images with a JVM (from official Spark base images), and images used by orchestrators to run isolated tasks (Module 2.13) |

**How to learn it**

1. Read the topic file.
2. Write a naive Dockerfile for your Module 2.12 pipeline CLI, then improve
   it step by step (caching, multi-stage, `uv`, non-root, init), measuring
   image size and rebuild time after each step.
3. Run `docker history` and a vulnerability scanner on each version.

**Hands-on exercise — `docker/pipeline.Dockerfile` (plus dbt and Spark)**

1. Build a multi-stage image for your pipeline package using `uv` with the
   lock file, a non-root user, an exec-form entrypoint running your CLI, and
   a health check where relevant.
2. Show that a code-only change rebuilds in seconds while dependencies stay
   cached.
3. Send `SIGTERM` to a running container and prove your pipeline shuts down
   gracefully (checkpoint saved, exit code correct).
4. Build a dbt image and a PySpark image (Module 2.14 job) the same way.
5. Scan all images, fix at least one reported issue, and generate an SBOM.
6. Build for `amd64` and `arm64` and push to a registry with a git-SHA tag.
7. Record image sizes before and after optimisation.

**Checkpoint — you are ready to move on when you can:**

- [ ] Write a multi-stage Python Dockerfile with `uv` and a non-root user.
- [ ] Explain layer caching and order instructions for fast rebuilds.
- [ ] Make containers handle signals correctly.
- [ ] Scan images and keep secrets out of layers.
- [ ] Tag images immutably and build for multiple platforms.

**Common mistakes:** running as root; `COPY . .` before installing
dependencies; secrets in `ENV` or copied `.env` files; shell-form
entrypoints that swallow signals; relying on `latest` tags.

---

### Topic 02 — [Docker Compose for local data stacks](02-docker-compose-for-local-data-stacks.md)

**Why here:** A data pipeline rarely runs alone — it needs a database,
object storage, a broker, an orchestrator. Compose runs the whole stack
locally and in CI integration tests with one command.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Compose files: services, images vs builds, ports, environment, and `docker compose up / down / logs / exec` |
| Basics | Networks (service names as hostnames) and volumes (named volumes vs bind mounts) |
| Basics | Environment files and variable substitution |
| Intermediate | **Health checks** and `depends_on` with conditions, so services start only when dependencies are ready |
| Intermediate | **One-shot set-up services**: creating buckets, topics, schemas, and seed data before the stack is used |
| Intermediate | **Profiles** to start subsets (e.g. `core`, `streaming`, `spark`, `airflow`) and override files for local vs CI differences |
| Intermediate | Resource limits so a laptop can run the stack |
| Advanced | Development workflows: live code reload (watch mode or bind mounts) vs rebuilt images |
| Advanced | Using Compose in CI for integration tests (start, wait for health, test, tear down) — and containerised test fixtures (Module 2.19) |
| Advanced | Secrets in Compose (secret files vs environment variables) for local use |
| Advanced | Limits of Compose: single host, no self-healing or scaling — why production uses Kubernetes or managed services |

**How to learn it**

1. Read the topic file.
2. Collect every Compose file you used in earlier modules and rewrite them
   into one well-structured stack with profiles.
3. Start the stack from scratch on a clean machine (or a fresh clone) and
   time how long it takes to be healthy.

**Hands-on exercise — `compose/`**

1. Build a single Compose stack with PostgreSQL, MinIO, Kafka (KRaft),
   schema registry, and Airflow, grouped into profiles.
2. Add health checks for every service and dependency conditions between
   them.
3. Add set-up services that create buckets, Kafka topics, database
   schemas, and seed data idempotently.
4. Add your pipeline image as a service that runs a daily job against the
   stack.
5. Add an override file for CI (smaller resources, no persistent volumes).
6. Write `make up`, `make test-integration`, and `make down` targets.

**Checkpoint:**

- [ ] Write Compose files with networks, volumes, and environment files.
- [ ] Use health checks and dependency conditions.
- [ ] Initialise a stack idempotently with set-up services.
- [ ] Use profiles and override files for different contexts.
- [ ] Explain why Compose is not a production platform.

**Common mistakes:** fixed `sleep` commands instead of health checks;
set-up scripts that fail when run twice; committing real credentials in
Compose files; one giant stack that no laptop can run.

---

## 7. Phase B — Running Containers at Scale (Intermediate → Advanced)

### Topic 03 — [Kubernetes concepts for data workloads](03-kubernetes-concepts-for-data-workloads.md)

**Why here:** Kubernetes is where many production data platforms run
their orchestrators, Spark jobs, streaming processors, and APIs. A data
engineer does not need to be a Kubernetes administrator, but must
understand its concepts well enough to run, size, secure, and debug data
workloads on it.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why Kubernetes for data: scheduling containers across machines, restarting failed work, scaling, and a common platform for many tools |
| Basics | Cluster, nodes, control plane; **pods**, **deployments**, **services**, **namespaces** |
| Basics | `kubectl` basics: `apply`, `get`, `describe`, `logs`, `exec`, `delete`; events for debugging |
| Basics | Local clusters with kind, k3d, or minikube |
| Intermediate | **Jobs** and **CronJobs** for batch data work: retries (`backoffLimit`), deadlines, parallelism, completion, and concurrency policy |
| Intermediate | **ConfigMaps** and **Secrets** (and why Kubernetes Secrets are only base64-encoded unless encryption and external secret stores are used — Topic 07) |
| Intermediate | **Resource requests and limits**: CPU throttling, memory limits and `OOMKilled`, and sizing data jobs |
| Intermediate | **ServiceAccounts** and **workload identity** (mapping pods to cloud roles — Module 2.17) |
| Intermediate | **Helm**: installing and configuring charts (e.g. the official Airflow chart) with values files |
| Advanced | **Operators** for data systems: Spark on Kubernetes (native submission and Spark operators), Kafka operators, Flink operators — awareness and when to use them |
| Advanced | Running orchestrator tasks as pods (Airflow's Kubernetes executor and pod operator — Module 2.13) |
| Advanced | **Autoscaling**: horizontal pod autoscaling, cluster/node autoscaling, spot node pools, and event-driven autoscaling on metrics such as consumer lag (Module 2.16) |
| Advanced | Scheduling controls: node pools, taints and tolerations, affinity — separating heavy Spark jobs from latency-sensitive services |
| Advanced | Storage: persistent volumes and why data jobs should prefer object storage |
| Advanced | GitOps deployment (e.g. Argo CD or Flux) — awareness |
| Advanced | When **not** to use Kubernetes: small teams and workloads better served by managed services or serverless (Module 2.17) |

**How to learn it**

1. Read the topic file.
2. Create a local kind or k3d cluster and deploy MinIO and PostgreSQL with
   Helm.
3. Run your pipeline image as a Job and a CronJob; break it with too little
   memory and read the resulting events.

**Hands-on exercise — `k8s/`**

1. Run the daily pipeline as a Kubernetes **Job** with a ConfigMap for
   configuration, resource requests and limits, a `backoffLimit`, and an
   active deadline.
2. Schedule it as a **CronJob** with `concurrencyPolicy: Forbid` and show
   overlapping runs being prevented (the cron problem from Module 2.13).
3. Trigger an `OOMKilled` failure, diagnose it with `describe` and events,
   and fix the sizing.
4. Install Airflow with its Helm chart and run one task in its own pod.
5. Run the Module 2.14 Spark job on the cluster (native Spark on Kubernetes
   or a Spark operator) using your Spark image.
6. Use a dedicated ServiceAccount per workload (and document how it would
   map to a cloud role via workload identity).

**Checkpoint:**

- [ ] Explain pods, deployments, services, Jobs, and CronJobs.
- [ ] Size data jobs with requests and limits and diagnose `OOMKilled`.
- [ ] Deploy data tools with Helm and run tasks as pods.
- [ ] Explain operators and autoscaling for data workloads.
- [ ] Decide when Kubernetes is not worth it.

**Common mistakes:** no resource requests (noisy neighbours) or limits far
below real usage; treating Kubernetes Secrets as encrypted; long-running
work in pods without restart handling; one shared ServiceAccount for
everything.

---

## 8. Phase C — Infrastructure as Code (Intermediate → Advanced)

### Topic 04 — [Terraform basics for data infrastructure](04-terraform-basics-for-data-infrastructure.md)

**Why here:** In Module 2.17 you created cloud resources with the CLI and
SDKs. Infrastructure as code turns those resources into reviewed,
versioned, repeatable definitions — so dev, staging, and production are
identical by construction, and nothing exists that is not in Git.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why infrastructure as code: repeatability, review, history, and drift detection |
| Basics | Terraform language (HCL): **providers**, **resources**, **data sources**, **variables**, **outputs**, and **locals** |
| Basics | The workflow: `init`, `fmt`, `validate`, `plan`, `apply`, `destroy` — and reading a plan carefully |
| Intermediate | **State**: what it records, why it must be shared and locked, remote backends (e.g. an object-storage backend with locking), and why state can contain sensitive values |
| Intermediate | **Modules**: reusable building blocks (e.g. a `data_lake` module with bucket, encryption, lifecycle, and access policies) |
| Intermediate | `count` and `for_each` for many similar resources (e.g. one role per pipeline from configuration) |
| Intermediate | Environments: separate state per environment (directories or workspaces) and variable files |
| Intermediate | Data infrastructure as code: buckets and lifecycle rules, IAM roles and policies, KMS keys, catalogs, warehouse objects (databases, schemas, roles, warehouses), managed Spark resources, and Kafka topics — via their providers |
| Advanced | **Safety**: `prevent_destroy` on data-holding resources, careful handling of replacements ("forces replacement" in plans), and backups before risky changes |
| Advanced | Importing existing resources and detecting **drift** from manual changes |
| Advanced | Linting and **security scanning** of Terraform code (e.g. public buckets, wildcard IAM) |
| Advanced | Running Terraform in CI: `plan` on pull requests with the plan posted for review, `apply` only after approval (Topics 05–06) |
| Advanced | The ecosystem: OpenTofu (open-source fork), and alternatives such as Pulumi or cloud-native templates — awareness |

**How to learn it**

1. Read the topic file.
2. Recreate the Module 2.17 lab resources (bucket, roles, policies, key,
   lifecycle rules) in Terraform, then destroy the hand-made versions.
3. Change one attribute that forces replacement of a bucket and read the
   plan output carefully — then protect the bucket.

**Hands-on exercise — `infra/`**

1. Configure a remote state backend with locking.
2. Write modules: `data_lake` (bucket, versioning, encryption, lifecycle,
   blocked public access), `pipeline_role` (least-privilege role per
   pipeline from a list), and one warehouse or catalog module using its
   provider.
3. Instantiate them for `dev` and `staging` with different variables.
4. Add `prevent_destroy` to data-holding resources and show that a
   destructive plan is blocked.
5. Make a manual change in the cloud console and detect it as drift.
6. Run `fmt`, `validate`, a linter, and a security scanner; fix every
   finding.
7. `destroy` the dev environment completely and recreate it from scratch.

**Checkpoint:**

- [ ] Write Terraform with providers, resources, variables, and outputs.
- [ ] Manage remote, locked state and explain its sensitivity.
- [ ] Build reusable modules and multiple environments.
- [ ] Read plans and prevent destructive changes to data.
- [ ] Detect drift and scan infrastructure code.

**Common mistakes:** local state files on a laptop; state committed to Git;
applying without reading the plan; buckets destroyed by an innocent rename;
manual console changes that drift from code.

---

## 9. Phase D — Delivering Changes (Intermediate → Advanced)

### Topic 05 — [CI pipelines for data projects](05-ci-pipelines-for-data-projects.md)

**Why here:** Every earlier module produced checks: tests, DAG tests,
contracts, dbt tests, schema diffs. CI runs all of them automatically on
every change, so broken pipelines never reach production.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Continuous integration: every push and pull request is built and tested automatically |
| Basics | GitHub Actions: workflows, triggers (`push`, `pull_request`, schedules, manual), jobs, steps, runners, and logs |
| Basics | A Python CI job: set up Python and `uv` with caching, install from the lock file, run Ruff (lint and format check), a type checker, and pytest |
| Intermediate | **Data-specific checks**: DAG import/structure/policy tests (Module 2.13), SQL linting, data contract and schema-compatibility checks (Modules 2.11 and 2.16), Pandera schema tests |
| Intermediate | **dbt "slim" CI**: building and testing only modified models and their descendants in an isolated CI schema, deferring unchanged models to production (Module 2.12) |
| Intermediate | **Integration tests** with service containers or Compose (Topic 02) |
| Intermediate | Building, scanning, and pushing **images** tagged with the commit SHA |
| Intermediate | **Terraform** `fmt`, `validate`, security scan, and `plan` on pull requests |
| Intermediate | **Cloud access without stored keys**: OIDC federation from CI to cloud roles (Module 2.17) |
| Advanced | Speed: dependency caching, parallel jobs, matrices, path filters (only run Spark tests when Spark code changes), and test selection |
| Advanced | **Supply-chain safety**: pinning third-party actions to commit SHAs, least-privilege workflow permissions, dependency and secret scanning, protected branches and required checks |
| Advanced | `pre-commit` hooks as the local first line of the same checks |
| Advanced | Continuous delivery basics: build once, store the artifact (image, wheel, dbt package), deploy that exact artifact (Topic 06) |

**How to learn it**

1. Read the topic file.
2. List every check you wrote in Modules 2.11–2.17 and decide which runs on
   every pull request, which on merge, and which nightly.
3. Open a pull request with a deliberate failure for each check and confirm
   CI blocks it.

**Hands-on exercise — `.github/workflows/`**

1. `ci.yml` on pull requests: lint, format check, type check, unit tests
   with coverage, DAG tests, contract/schema-diff checks, SQL lint, and
   Pandera schema tests — in parallel jobs with caching.
2. `dbt-ci.yml`: slim CI against an isolated schema, deferring to
   production state.
3. `integration.yml`: start the Compose stack, run integration tests, tear
   down.
4. `images.yml`: build pipeline, dbt, and Spark images; scan them; push
   with SHA tags on merge.
5. `infra.yml`: Terraform `fmt`, `validate`, scan, and `plan` for changed
   environments using OIDC to your cloud; post the plan summary to the pull
   request.
6. Pin all third-party actions by SHA, set minimal workflow permissions,
   and enable branch protection with required checks.
7. Measure and reduce total CI time for a typical pull request.

**Checkpoint:**

- [ ] Build GitHub Actions workflows with caching and parallel jobs.
- [ ] Run data-specific checks (DAGs, dbt slim CI, contracts) in CI.
- [ ] Build, scan, and push images with immutable tags.
- [ ] Plan infrastructure in CI with OIDC and no stored cloud keys.
- [ ] Secure the CI pipeline itself.

**Common mistakes:** CI that only runs unit tests; slow pipelines nobody
waits for; long-lived cloud keys stored in CI secrets; unpinned third-party
actions; dbt CI that rebuilds the entire project on every change.

---

### Topic 06 — [Environment promotion: dev, staging, and prod](06-environment-promotion-dev-staging-and-prod.md)

**Why here:** Passing CI proves a change is probably correct. Promotion
proves it works against real infrastructure and realistic data before it
touches production — and gives you a way back when it does not.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why separate environments: safe experimentation (dev), realistic validation (staging), and protected production |
| Basics | Isolation: separate cloud accounts or projects, catalogs or schemas, buckets, and credentials per environment |
| Basics | Configuration per environment without code changes (overlays from Module 2.12) |
| Intermediate | **Promote artifacts, do not rebuild them**: the same image digest, dbt package, and DAG version moves from dev to staging to production |
| Intermediate | Deployment workflows: automatic deploy to dev, deploy to staging after tests, production after **approval** (e.g. protected environments with required reviewers) |
| Intermediate | Deploying each part of a data platform: images, DAGs (Module 2.13), dbt jobs, database migrations in the correct order (Module 2.7), and infrastructure applies (Topic 04) |
| Intermediate | **Data for non-production**: synthetic data, sampled data, or masked production data — never raw personal data in dev (Module 2.20) |
| Intermediate | Branching and release strategies: trunk-based development with short-lived branches vs longer release branches; semantic versioning and changelogs |
| Advanced | **Validating data changes**: running the new version in parallel on production inputs and comparing outputs (shadow runs and backfills into shadow tables from Module 2.12) |
| Advanced | **Ephemeral environments per pull request**: warehouse zero-copy clones, table-format branches or clones (Module 2.15), and temporary schemas |
| Advanced | **Rollback**: redeploying the previous image or DAG version (easy) vs rolling back data (hard — time travel and restore from Module 2.15, backfills from Module 2.12) |
| Advanced | Expand-and-contract for breaking schema changes across environments (Modules 2.7 and 2.11) |
| Advanced | Feature flags for pipeline behaviour and progressive rollout (one source or partition first) |
| Advanced | Change records and auditability: who deployed what, when, with which approval |

**How to learn it**

1. Read the topic file.
2. Draw the path of one change — a dbt model edit plus a new column in an
   ingestion pipeline — from commit to production, marking every
   environment, check, approval, and rollback option.
3. Write a promotion checklist and a rollback runbook.

**Hands-on exercise — `.github/workflows/deploy.yml` and `docs/`**

1. Create `dev`, `staging`, and `prod` configurations (Terraform
   environments, catalogs/schemas, buckets, config overlays).
2. Implement a deployment workflow: on merge, deploy the SHA-tagged images,
   DAGs, and dbt project to dev; after integration tests, promote the
   **same** artifacts to staging; after a manual approval, promote to prod.
3. Run database migrations and Terraform applies as ordered deployment
   steps.
4. Create an ephemeral environment per pull request using a table clone or
   branch and a temporary schema; destroy it when the pull request closes.
5. Run a shadow comparison in staging: new vs current gold outputs on the
   same inputs, failing promotion on unexpected differences.
6. Perform a rollback drill: deploy a bad version to staging, roll back the
   code, and restore the affected table with time travel; record the time
   taken.

**Checkpoint:**

- [ ] Isolate environments and configure them without code changes.
- [ ] Promote immutable artifacts through environments with approvals.
- [ ] Deploy code, DAGs, dbt, migrations, and infrastructure in order.
- [ ] Validate data changes with shadow runs and ephemeral environments.
- [ ] Roll back both code and data.

**Common mistakes:** rebuilding images per environment; staging with no
realistic data; production personal data copied into dev; "rollback"
plans that ignore data already written; manual production deployments.

---

## 10. Phase E — Protecting Credentials (Advanced)

### Topic 07 — [Cloud secrets managers](07-cloud-secrets-managers.md)

**Why last:** Every layer of this module touches credentials: images must
not contain them, Compose and Kubernetes must deliver them, Terraform state
may store them, CI must not need them, and each environment needs its own.
Secrets managers are the production answer.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Secrets vs configuration; what counts as a secret (database passwords, API keys, private keys, tokens) |
| Basics | Secrets managers: AWS Secrets Manager and Parameter Store, Google Secret Manager, Azure Key Vault, HashiCorp Vault (and open-source forks) |
| Basics | Retrieving secrets at runtime from Python with the provider SDK, using workload identity (Module 2.17) — no bootstrap keys |
| Intermediate | Caching secrets in memory, refresh on expiry or rotation, and never logging them (redaction from Module 2.9) |
| Intermediate | **Rotation**: automatic rotation of database credentials, versioned secrets, and applications that tolerate rotation without downtime |
| Intermediate | **Least privilege per secret**: each pipeline role can read only its own secrets |
| Intermediate | Delivering secrets to platforms: Airflow secrets backends (Module 2.13), Kubernetes external secrets operators or CSI secret-store drivers, managed Spark job secrets, serverless function configuration |
| Intermediate | CI secrets: prefer OIDC federation (no secret at all); if a secret is unavoidable, scope it to one environment |
| Advanced | **Dynamic secrets**: short-lived database credentials generated per job (e.g. Vault database engines) |
| Advanced | Encryption keys (KMS) behind secrets managers, and encrypted secrets in Git with tools such as SOPS — when appropriate |
| Advanced | Terraform and secrets: generating secrets without exposing them, protecting state, and avoiding secrets in outputs and plans |
| Advanced | **Detection**: secret scanning in pre-commit and CI, repository push protection, and scanning images and logs |
| Advanced | **Incident response for a leaked secret**: revoke and rotate immediately, audit access logs for misuse, remove it from history where possible, and write a post-mortem (Module 2.20) |

**How to learn it**

1. Read the topic file.
2. Build a **secrets inventory** for your platform: every secret, its
   owner, where it is stored, who can read it, and its rotation period.
3. Search your earlier modules' repositories with a secret scanner and fix
   anything found.

**Hands-on exercise — `secrets/`**

1. Store your platform's database, API, and SFTP credentials in a cloud
   secrets manager (created with Terraform), one secret per system and
   environment.
2. Refactor your pipelines to fetch secrets at runtime via workload
   identity, with in-memory caching and redaction.
3. Configure Airflow to read connections from the secrets manager, and
   deliver a secret to a Kubernetes Job via an external secrets mechanism.
4. Enable automatic rotation for the PostgreSQL password (or simulate it)
   and prove pipelines keep working through a rotation.
5. Add secret scanning to `pre-commit` and CI; commit a fake secret on a
   branch and confirm it is blocked.
6. Run a leaked-secret drill: rotate, revoke, audit access logs, and write
   a short post-mortem.

**Checkpoint:**

- [ ] Store and retrieve secrets with a cloud secrets manager and workload
      identity.
- [ ] Rotate secrets without downtime.
- [ ] Deliver secrets to Airflow, Kubernetes, and CI safely.
- [ ] Detect secrets before they reach Git.
- [ ] Respond correctly to a leaked secret.

**Common mistakes:** secrets in images, environment files, Terraform
outputs, or logs; one shared secret for all environments; no rotation;
deleting a leaked secret from Git without revoking it.

---

## 11. Consolidate — practice questions

When all seven topics are done, open
[`practice-questions.md`](practice-questions.md). For every question:

1. Draw how the change or system flows: code → image → CI → environments →
   production, including infrastructure and secrets.
2. Write the artefacts as code (Dockerfile, Compose, manifests, Terraform,
   workflows).
3. Identify what is checked automatically and where approval is required.
4. Define the rollback plan for both code and data.
5. Identify every credential involved and how it is delivered and rotated.
6. Implement it, break it, and recover.

---

## 12. Module mini-project — shipping the data platform like software

This is the proof that you have finished the module.

**Scenario:** Your platform (Modules 2.9–2.17) works, but it is deployed by
hand from one engineer's laptop. The team is growing and an audit is
coming. You must make every part of it reproducible, tested, promoted
through environments, and free of hard-coded credentials.

Build `platform_delivery/` with:

1. **Images** — multi-stage, non-root, `uv`-based images for the pipeline
   package, dbt, and Spark jobs; multi-platform builds; scanning and SBOMs;
   SHA tags.
2. **Local stack** — one Compose file with profiles, health checks, and
   idempotent set-up services for PostgreSQL, MinIO, Kafka, the schema
   registry, and Airflow; `make` targets for up, test, and down.
3. **Kubernetes** — a local kind/k3d cluster running Airflow (Helm) with
   tasks as pods, a pipeline CronJob with correct resources, and a Spark job
   on Kubernetes; one ServiceAccount per workload.
4. **Infrastructure as code** — Terraform modules for the lake, pipeline
   roles, KMS keys, secrets, catalog or warehouse objects, and lifecycle
   rules; remote locked state; `dev`, `staging`, and `prod` configurations;
   `prevent_destroy` on data; drift detection.
5. **CI** — pull-request workflows for lint, types, unit tests, DAG tests,
   contract checks, dbt slim CI, integration tests, image build and scan,
   and Terraform plan — with OIDC, pinned actions, and branch protection.
6. **CD and promotion** — build once, deploy the same artifacts to dev,
   then staging (after integration tests and a shadow comparison), then prod
   (after approval); migrations and infrastructure applied in order;
   ephemeral pull-request environments.
7. **Secrets** — all credentials in a secrets manager, read via workload
   identity, delivered to Airflow and Kubernetes, with rotation and secret
   scanning.
8. **Operations** — a promotion checklist, a rollback runbook (code and
   data), a secrets inventory, and a timed rollback drill.
9. **Teardown** — `terraform destroy` for non-production environments and a
   verified clean-up of every cloud resource.

**Grading yourself:** a new engineer can clone the repository and run the
stack and tests with two commands; no change reaches production without CI
passing and an approval; the exact artifact running in production is known
for every component; no credential exists in Git, images, logs, or state
outputs; and a bad release can be rolled back — code and data — in under
30 minutes.

---

## 13. Module self-assessment — exit criteria

Only move to Module 2.19 when you can tick every box without looking at your
notes:

- [ ] I can build small, secure, reproducible images for Python, dbt, and
      Spark.
- [ ] I can run and initialise a full local data stack with Compose.
- [ ] I can run and debug data jobs on Kubernetes and explain its data
      tooling.
- [ ] I can manage data infrastructure safely with Terraform.
- [ ] I can build CI pipelines with data-specific checks and no stored
      cloud keys.
- [ ] I can promote immutable artifacts through environments and roll back
      code and data.
- [ ] I can manage secrets with cloud secrets managers, including rotation
      and leak response.
- [ ] I have finished all practice questions and the mini-project.

---

## 14. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| Docker documentation — Dockerfile reference, build best practices, multi-stage builds, BuildKit, Compose specification | 01, 02 |
| `uv` documentation — "Using uv in Docker" and GitHub Actions integration | 01, 05 |
| Kubernetes documentation — concepts (pods, Jobs, CronJobs, resources, service accounts), and Helm documentation | 03 |
| Apache Airflow Helm chart and Spark on Kubernetes documentation | 03 |
| Terraform (or OpenTofu) documentation — language, state, modules, and backend configuration; provider documentation for your cloud and warehouse | 04 |
| *Terraform: Up & Running*, 3rd edition — Yevgeniy Brikman (O'Reilly) | 04, 06 |
| GitHub Actions documentation — workflow syntax, caching, environments and deployment protection, OIDC security hardening | 05, 06 |
| dbt documentation — CI jobs, state selection, and `--defer` | 05, 06 |
| AWS Secrets Manager, Google Secret Manager, Azure Key Vault, and HashiCorp Vault documentation | 07 |
| OWASP Secrets Management Cheat Sheet | 07 |
| *Accelerate* — Nicole Forsgren, Jez Humble, Gene Kim — on delivery performance and practices | 05, 06 |

---

## 15. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| Integration tests with containers and CI test stages | 2.19 Testing Data Pipelines |
| Deployment audit trails, access control, and secret-leak incidents | 2.20 Observability, Lineage, Governance, and Security |
| Container and cluster right-sizing, spot capacity, and CI cost | 2.21 Performance, Scaling, and Cost Optimization |
| Deploying data APIs and serving layers with the same pipeline | 2.22 Serving Data for Analytics, ML, and AI |

Data platforms fail less often because of clever code than because of
careless delivery. The habits you build here — package once, define
everything as code, test every change automatically, promote the same
artifact through environments, keep a rollback plan for data as well as
code, and never let a credential touch Git — are what let a team change a
data platform every day without fear.
