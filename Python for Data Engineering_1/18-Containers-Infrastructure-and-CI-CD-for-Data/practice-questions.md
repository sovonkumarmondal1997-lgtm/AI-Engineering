# Module 2.18 — Practice Questions

## Overview

This workbook contains **exactly 40 production-oriented problem-solving questions** for Module 2.18 — Containers, Infrastructure, and CI/CD for Data.

The questions are grounded in the seven Module 2.18 learning topics:

1. Docker Images for Python Pipelines
2. Docker Compose for Local Data Stacks
3. Kubernetes Concepts for Data Workloads
4. Terraform Basics for Data Infrastructure
5. CI Pipelines for Data Projects
6. Environment Promotion: Dev, Staging, and Prod
7. Cloud Secrets Managers

The set intentionally progresses from fixing one component to designing and recovering a multi-system production data platform.

## Difficulty Distribution

| Difficulty | Number |
|---|---:|
| Basic | 10 |
| Moderate | 10 |
| Hard | 10 |
| Advanced | 10 |
| **TOTAL** | **40** |

## How to Use This Practice Set

For each problem:

1. Read the scenario before looking at the solution.
2. Write your own diagnosis and design first.
3. If code is requested, implement it before comparing your answer.
4. For incident questions, identify the safest first action before changing configuration.
5. Compare your reasoning with the solution, not only the final configuration.
6. For production scenarios, explain trade-offs, security implications, and rollback implications.

The intended engineering loop is:

```text
Read
→ Write as code
→ Review diff
→ Run locally
→ Run in CI
→ Break
→ Recover / Rollback
→ Measure
→ Document
→ Explain
```


# Part I — Basic

## Question 1 — Shrink and Secure a Python Pipeline Image

### Difficulty

Basic

### Problem

A Python ingestion image is 1.6 GB. The Dockerfile copies the entire repository before installing dependencies, includes `.venv`, runs as root, and installs development tools into the runtime image. The pipeline only needs a small Python runtime and its locked production dependencies.

**Primary coverage:** Docker

### What You Need to Do

1. Identify the main causes of image bloat and poor cache reuse.
2. Redesign the Dockerfile using a slim Debian-based Python image, `.dockerignore`, dependency-first copying, `uv`, and a non-root runtime user.
3. Explain why Alpine is not automatically the best choice for Python data workloads.

### Solution

Use a production-oriented structure such as:

```dockerfile
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/
RUN uv sync --frozen --no-dev

RUN useradd --create-home --uid 10001 appuser
USER appuser

ENTRYPOINT ["python", "-m", "pipeline"]
```

The exact dependency/build pattern may vary, but the principles are stable: copy dependency metadata before application code, install from the lock file, exclude development dependencies, and run as a non-root user.

A `.dockerignore` should exclude at least local virtual environments, Git metadata, caches, secrets, test artifacts that are not needed at runtime, and other irrelevant files.

Use a Debian/slim base when Python/native-wheel compatibility is the priority. Alpine uses musl libc and can introduce native-extension or wheel compatibility complications. Smaller is not automatically better if it increases build complexity or runtime failures.

### Why This Solution Works

The largest optimization is usually not a clever Docker command; it is structuring the build so stable dependency layers are reusable and unnecessary files never enter the build context.

### Key Takeaway

Keep dependency installation cacheable, runtime images minimal, and application processes non-root.

## Question 2 — Fix a Compose Hostname Mistake

### Difficulty

Basic

### Problem

A Python pipeline container is configured with `DATABASE_HOST=localhost`. PostgreSQL is another service in the same Compose project. The pipeline starts, attempts `localhost:5432`, and fails even though PostgreSQL is healthy.

**Primary coverage:** Docker Compose

### What You Need to Do

1. Explain why `localhost` is wrong inside the pipeline container.
2. Provide the correct Compose-oriented connection configuration.
3. State when `localhost` would be correct.

### Solution

If the Compose services are named `pipeline` and `postgres`, container-to-container traffic should use the service name:

```yaml
services:
  postgres:
    image: postgres:16

  pipeline:
    build: .
    environment:
      DATABASE_HOST: postgres
      DATABASE_PORT: "5432"
```

Inside `pipeline`, `localhost` means the pipeline container itself. Compose's network DNS makes the service name `postgres` resolve to the PostgreSQL container.

`localhost:5432` is appropriate when the client is running on the host and the PostgreSQL container publishes port 5432 to the host, for example `5432:5432`. It is not the normal container-to-container address.

### Why This Solution Works

Compose provides service discovery through its network. The hostname is therefore a service identity, not the host machine's loopback interface.

### Key Takeaway

In Compose networking, use the service name for inter-container communication; reserve `localhost` for the current container/process or a host-side client.

## Question 3 — Make PostgreSQL Readiness Explicit

### Difficulty

Basic

### Problem

A Compose stack has PostgreSQL and a Python setup service. `depends_on` starts PostgreSQL first, but the setup service sometimes fails because PostgreSQL is still initializing.

**Primary coverage:** Docker Compose

### What You Need to Do

1. Explain why startup order is not readiness.
2. Add a PostgreSQL health check.
3. Configure dependency behavior around the health check rather than adding an arbitrary sleep.

### Solution

Use a health check:

```yaml
services:
  postgres:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d analytics"]
      interval: 5s
      timeout: 3s
      retries: 10

  setup:
    build: ./setup
    depends_on:
      postgres:
        condition: service_healthy
```

The health check asks whether PostgreSQL is actually accepting connections. `depends_on` with a health condition then gives the setup service a meaningful readiness signal.

Avoid `sleep 20`: startup time varies across machines and CI runners, so a fixed delay is both slow and unreliable.

### Why This Solution Works

Container creation, process start, and application readiness are different states. Data stacks need readiness-aware orchestration.

### Key Takeaway

Model readiness explicitly; never use arbitrary sleeps as the primary dependency mechanism.

## Question 4 — Diagnose a Kubernetes Job That Runs Out of Memory

### Difficulty

Basic

### Problem

A Kubernetes Job running a Python transformation is repeatedly terminated. `kubectl describe pod` shows `OOMKilled`. The manifest has no memory request or limit, and the developer assumes Kubernetes will automatically provide more memory.

**Primary coverage:** Kubernetes

### What You Need to Do

1. Identify the failure.
2. Show how to add realistic resource requests and a limit.
3. Explain what `OOMKilled` means operationally.

### Solution

Inspect:

```bash
kubectl describe pod <pod>
kubectl get events --sort-by=.lastTimestamp
kubectl logs <pod> --previous
```

Then define resources:

```yaml
resources:
  requests:
    cpu: "500m"
    memory: "512Mi"
  limits:
    cpu: "1"
    memory: "1Gi"
```

The values are workload-specific; they must be measured rather than copied blindly.

`OOMKilled` means the container exceeded its available memory boundary and was terminated. A limit does not create memory. Requests influence scheduling and communicate expected resource needs; limits constrain consumption.

After changing the manifest, rerun the workload and observe actual memory usage rather than assuming the first new value is correct.

### Why This Solution Works

Resource configuration is part of workload design. A data job that is too large for its memory boundary must be resized, optimized, partitioned, or moved to an execution model appropriate for the workload.

### Key Takeaway

Use requests and limits deliberately, then measure actual workload behavior.

## Question 5 — Protect Terraform State

### Difficulty

Basic

### Problem

A team runs Terraform locally and commits `terraform.tfstate` to Git so everyone can share the same infrastructure state.

**Primary coverage:** Terraform

### What You Need to Do

1. Explain why this is unsafe.
2. Describe the production-oriented replacement.
3. List the properties the shared state backend should provide.

### Solution

Remove state from Git and use a secure remote backend appropriate to the cloud/platform. The backend should provide:

- controlled access;
- encryption at rest;
- locking where supported;
- backup/recovery;
- auditability.

The conceptual model becomes:

```text
Terraform configuration
        ↓
shared remote state
   ├── encryption
   ├── IAM
   └── locking
```

Access to state must be limited because state can contain resource metadata and potentially sensitive values. `.gitignore` prevents accidental future commits, but it does not clean already-published state.

### Why This Solution Works

Terraform state is part of the infrastructure control plane. If it is lost, shared execution becomes unreliable; if it is exposed, sensitive values may be exposed.

### Key Takeaway

Treat Terraform state as sensitive infrastructure data: centralize it securely, lock it, encrypt it, and control access.

## Question 6 — Fix a CI Workflow That Skips Data Tests

### Difficulty

Basic

### Problem

A pull-request workflow runs Ruff and then immediately reports success. It never runs pytest, Airflow DAG import tests, or SQL/data-contract checks. A broken DAG is merged.

**Primary coverage:** CI/CD

### What You Need to Do

1. Identify the missing CI layers.
2. Propose a minimal job sequence.
3. Explain why data projects need checks beyond Python syntax.

### Solution

A minimal workflow should validate at least:

```text
checkout
  ↓
install locked dependencies
  ↓
lint/format/type checks
  ↓
unit tests + coverage
  ↓
Airflow DAG import/policy checks
  ↓
SQL/data-contract checks where applicable
```

For a data project, code can be syntactically valid while a DAG fails to import, a schema contract breaks, or SQL becomes invalid. Therefore CI must test the artifacts and interfaces that actually operate the data platform.

Use the project's locked dependency file and cache dependencies when safe to reduce repeated setup time.

### Why This Solution Works

Data engineering CI validates operational behavior and data interfaces, not merely whether Python parses.

### Key Takeaway

CI should prevent the classes of failures the production platform can actually experience.

## Question 7 — Separate Environment Credentials

### Difficulty

Basic

### Problem

A developer discovers that dev and production pipelines both read `data-platform/shared/postgres-password`. The credentials are valid in both environments.

**Primary coverage:** Environment Promotion, Secrets

### What You Need to Do

1. Identify the security and operational problem.
2. Redesign the secret layout.
3. Explain how this connects to environment promotion.

### Solution

Create environment-specific secrets:

```text
data-platform/dev/postgres
data-platform/staging/postgres
data-platform/prod/postgres
```

Then map each workload identity only to its environment's secret:

```text
dev pipeline → dev secret
staging pipeline → staging secret
prod pipeline → prod secret
```

The application code should remain environment-independent; the runtime identity/configuration determines which secret is available.

If the shared credential is already exposed broadly, rotate it and audit access rather than simply renaming the secret.

### Why This Solution Works

Environment isolation is not only about separate buckets and schemas. Credentials are part of the environment boundary.

### Key Takeaway

Promote the same artifact while changing environment-specific identity and configuration—not by sharing production credentials.

## Question 8 — Promote the Same Image

### Difficulty

Basic

### Problem

A team builds a Docker image in dev, then rebuilds from the same Git commit separately for staging and production. The resulting digests differ.

**Primary coverage:** Environment Promotion, Docker

### What You Need to Do

1. Explain why rebuilding violates the intended promotion model.
2. Describe the correct artifact flow.
3. Explain why a Git SHA tag alone is not the strongest runtime identity.

### Solution

Build once:

```text
source
  ↓
CI build
  ↓
image tagged with Git SHA
  ↓
scan/test
  ↓
store immutable image
  ↓
promote exact digest
```

Use the image digest as the immutable identity:

```text
registry/app@sha256:<digest>
```

The same digest should move:

```text
dev → staging → production
```

A Git SHA tag is useful for traceability, but tags can be moved. A digest identifies the exact image content.

### Why This Solution Works

Promotion should change deployment context, not rebuild the artifact. This creates a direct chain from tested artifact to production artifact.

### Key Takeaway

Build once, store once, and promote the exact immutable artifact.

## Question 9 — Find the Secret in a Dockerfile

### Difficulty

Basic

### Problem

A Dockerfile contains:

```dockerfile
ENV API_KEY=FAKE_PRODUCTION_STYLE_KEY
COPY .env /app/.env
```

The image is already pushed to a registry.

**Primary coverage:** Docker, Secrets

### What You Need to Do

1. Explain why both lines are dangerous.
2. State the immediate response if the credential represented a real secret.
3. Give the correct runtime pattern.

### Solution

Both approaches put sensitive material into an image/distribution path. The correct pattern is:

```text
application
   ↓
workload identity
   ↓
secret manager
   ↓
runtime retrieval
```

For a real credential, first revoke/rotate it. Then remove the secret from source/image history as appropriate and rebuild the image. Do not assume deleting the Dockerfile line invalidates a credential already present in an image or registry.

For build-time credentials that are genuinely necessary, use BuildKit secret mechanisms rather than `ENV` or ordinary build arguments.

### Why This Solution Works

Container registries and image layers are durable distribution systems. A secret baked into an image can outlive the source-code mistake.

### Key Takeaway

Never bake production secrets into images; runtime secret retrieval is the normal production boundary.

## Question 10 — Use an Idempotent Setup Service

### Difficulty

Basic

### Problem

A Compose stack has a setup container that creates a PostgreSQL schema and Kafka topics. The first `docker compose up` succeeds. The second run fails because the objects already exist.

**Primary coverage:** Docker Compose

### What You Need to Do

1. Explain idempotency in this context.
2. Redesign the setup logic.
3. State why idempotency matters in CI.

### Solution

Make initialization safe to execute repeatedly. Examples:

```sql
CREATE SCHEMA IF NOT EXISTS analytics;
```

For topic creation, use a setup command that checks whether the topic exists before creating it, or treats an already-existing topic as a successful desired state.

The setup service should converge the environment toward the required state rather than assume it starts empty.

In CI, the same environment may be recreated, retried, or initialized after a partial failure. Idempotent setup makes these operations predictable.

### Why This Solution Works

Initialization is infrastructure convergence at local-stack scope. A one-shot service should be safe to rerun.

### Key Takeaway

Setup steps should be repeatable and converge on the desired state rather than depend on a pristine machine.


# Part II — Moderate

## Question 11 — Recover a Slow Docker Build

### Difficulty

Moderate

### Problem

A Python pipeline changes one source file and the Docker build reinstalls 700 MB of dependencies. The Dockerfile copies the entire repository before running `uv sync`.

**Primary coverage:** Docker

### What You Need to Do

1. Reorder the build steps.
2. Use the lock file for deterministic dependency installation.
3. Explain how cache mounts can further improve dependency builds.

### Solution

Use dependency metadata before source code:

```dockerfile
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv     uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/
RUN --mount=type=cache,target=/root/.cache/uv     uv sync --frozen --no-dev
```

The first dependency layer remains reusable when only source files change. `uv.lock` makes dependency resolution deterministic, while a BuildKit cache mount can reuse downloaded packages across builds.

The exact `uv` layout depends on the project's packaging model, but the invariant is: stable inputs first, frequently changing inputs later.

### Why This Solution Works

Layer caching is a build-system design problem. The order of instructions determines which changes invalidate expensive layers.

### Key Takeaway

Separate dependency inputs from source inputs and use locked, cache-aware installation.

## Question 12 — Choose a Compose Volume Strategy

### Difficulty

Moderate

### Problem

A local PostgreSQL container uses a bind mount to a developer's host directory. Different developers see permission problems, and one developer accidentally deletes the database files. The team wants persistent database state but portable application source mounts.

**Primary coverage:** Docker Compose

### What You Need to Do

1. Choose named versus bind mounts.
2. Design the Compose volume configuration.
3. Explain which storage pattern is appropriate for live application development.

### Solution

Use a named volume for database storage:

```yaml
services:
  postgres:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data

  pipeline:
    build: .
    volumes:
      - ./src:/app/src

volumes:
  postgres_data:
```

The database gets a Docker-managed named volume, while source code can use a bind mount for development/live editing.

Bind mounts are useful when the host must directly edit files. Database storage generally benefits from a managed named volume because ownership and lifecycle are controlled by Docker rather than arbitrary host paths.

### Why This Solution Works

The storage semantics differ: source-code development benefits from host visibility; database state benefits from controlled persistence.

### Key Takeaway

Choose mounts according to workload semantics, not because one volume type is universally better.

## Question 13 — Prevent Overlapping CronJobs

### Difficulty

Moderate

### Problem

A daily Kubernetes data Job normally finishes in 20 minutes. One day it runs for 90 minutes, and the next scheduled run starts while the previous run is still active, producing duplicate processing.

**Primary coverage:** Kubernetes

### What You Need to Do

1. Configure the CronJob to prevent overlapping runs.
2. Choose a concurrency policy.
3. Explain what else you would inspect if the job regularly exceeds its schedule.

### Solution

Use:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-ingestion
spec:
  schedule: "0 2 * * *"
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      backoffLimit: 2
      template:
        spec:
          restartPolicy: Never
          containers:
            - name: ingestion
              image: registry.example/ingestion@sha256:FAKE_DIGEST
```

`Forbid` prevents a new scheduled run from starting while the previous one is active.

Then investigate why the workload expanded from 20 to 90 minutes: input volume, resource throttling, downstream latency, partitioning, or a regression. If the schedule is inherently too frequent, redesign the cadence or processing model.

### Why This Solution Works

Scheduling policy controls overlap, but it does not solve the underlying performance problem. Both operational correctness and capacity need attention.

### Key Takeaway

For batch workloads, explicitly define concurrency behavior and investigate runtime growth rather than allowing accidental overlap.

## Question 14 — Fix Terraform Drift Before Applying

### Difficulty

Moderate

### Problem

Terraform manages a production object-storage bucket. An operator changed its lifecycle policy manually in the cloud console. The next `terraform plan` shows an unexpected change.

**Primary coverage:** Terraform

### What You Need to Do

1. Explain drift.
2. Describe the safe response before applying.
3. State when import or configuration changes may be required.

### Solution

Treat the plan as evidence, not as an instruction to apply blindly.

```text
actual infrastructure
      ↕
Terraform state
      ↕
configuration
```

Determine whether the console change was intentional.

- If intentional and permanent, update Terraform configuration to represent the desired state.
- If the resource is outside Terraform management, consider import where appropriate.
- If the console change was accidental, decide whether Terraform should restore the declared configuration.
- Review the plan for unrelated changes before applying.

Never respond to unexpected drift with an automatic `terraform apply`.

### Why This Solution Works

Terraform's value is controlled desired state. Manual console changes create an unreviewed second source of truth.

### Key Takeaway

Investigate drift, reconcile the intended state, review the full plan, and only then apply.

## Question 15 — Build Data-Specific CI with dbt Slim Checks

### Difficulty

Moderate

### Problem

A dbt repository contains 500 models. Every pull request runs the entire production-sized test suite against a shared schema, making CI slow and causing developers to interfere with one another.

**Primary coverage:** CI/CD

### What You Need to Do

1. Design a slim CI approach.
2. Use an isolated CI schema.
3. Explain the role of `--defer` and changed-model selection.

### Solution

Use the CI artifacts/state from the trusted target environment and select modified models plus required descendants/related dependencies according to the project's dbt strategy. Run into an isolated CI schema.

Conceptually:

```text
PR
 ↓
identify modified models
 ↓
select affected graph
 ↓
build/test in isolated CI schema
 ↓
defer unchanged dependencies to trusted artifacts
 ↓
report result
```

`--defer` can allow unchanged dependencies to resolve against the prior target state rather than rebuilding the entire graph.

The exact selector should be validated against the repository's dbt project structure; the key design is selective testing plus isolation.

### Why This Solution Works

Data CI must balance confidence and feedback time. Shared mutable schemas undermine reproducibility and developer isolation.

### Key Takeaway

Use graph-aware, isolated dbt CI rather than rebuilding an entire production-shaped environment for every pull request.

## Question 16 — Diagnose a CI Image That Cannot Be Promoted

### Difficulty

Moderate

### Problem

CI builds a Python pipeline image and tags it `latest`. Security scanning passes. Staging deploys successfully, but when production deployment starts later, the registry's `latest` tag points to a newer image built by another workflow.

**Primary coverage:** CI/CD, Docker, Environment Promotion

### What You Need to Do

1. Identify the artifact-identity problem.
2. Redesign the tag/promotion strategy.
3. Explain what production should record.

### Solution

Build the image once and assign an immutable identity, for example:

```text
registry.example/pipeline:<git-sha>
registry.example/pipeline@sha256:<digest>
```

Use the digest as the deployment identity. CI should:

```text
build → test → scan → push → record digest
```

Then:

```text
dev → staging → production
```

should all reference that exact digest.

`latest` can remain a convenience tag if desired, but it should never be the authoritative production release identity.

Production should record the image digest, Git commit, deployment time, environment, and approval/change record.

### Why This Solution Works

Mutable tags break the chain of evidence between the artifact tested and the artifact deployed.

### Key Takeaway

Promotion requires immutable artifact identity; a digest is stronger than a movable tag.

## Question 17 — Handle a Kubernetes Secret Correctly

### Difficulty

Moderate

### Problem

A team stores a database password in a Kubernetes `Secret` and says, “It is secure because the value is base64 encoded.”

**Primary coverage:** Kubernetes, Secrets

### What You Need to Do

1. Correct the misconception.
2. Describe a stronger external-secret architecture.
3. Identify the identity boundary.

### Solution

Base64 is an encoding, not encryption:

```text
plaintext
  ↓
base64
  ↓
encoded bytes
```

For a production-oriented architecture:

```text
Cloud Secrets Manager
       ↓
workload/controller identity
       ↓
external secret mechanism or CSI
       ↓
Kubernetes workload
```

The external secret system can remain the authoritative source, with narrowly scoped access. Kubernetes-native Secret objects can still be used as delivery mechanisms where appropriate, but their security properties must be understood rather than inferred from the name “Secret.”

### Why This Solution Works

The security boundary is created by encryption, identity, access control, and lifecycle—not by the field name or encoding.

### Key Takeaway

Never equate base64 with encryption; design the complete secret-delivery chain.

## Question 18 — Rotate a Cached Database Credential

### Difficulty

Moderate

### Problem

A Python worker caches a PostgreSQL credential for 30 minutes. The credential is rotated after 10 minutes. New connections fail for the remainder of the cache lifetime.

**Primary coverage:** Secrets, Python

### What You Need to Do

1. Identify the stale-cache failure.
2. Design a refresh strategy.
3. Explain how connection pools complicate the fix.

### Solution

Use a bounded cache with refresh/invalidation behavior. A practical sequence is:

```text
cached credential A
      ↓
authentication failure
      ↓
invalidate credential cache
      ↓
retrieve current version B
      ↓
reconnect
      ↓
retry once
```

Also configure the database connection pool so existing connections do not live indefinitely with credential A. The exact pool controls depend on the client library.

Avoid infinite retries. If the new credential is also invalid, the system should fail clearly rather than repeatedly hammering the database or secret manager.

### Why This Solution Works

Credential rotation affects both application caches and existing network connections. Updating only the secret store is insufficient.

### Key Takeaway

Rotation-safe applications need cache invalidation and connection lifecycle behavior, not merely secret versioning.

## Question 19 — Add a Terraform Plan Gate

### Difficulty

Moderate

### Problem

A GitHub Actions workflow automatically runs `terraform apply` on every pull request. A pull request changes an object-storage lifecycle rule and unexpectedly proposes a destructive replacement elsewhere.

**Primary coverage:** Terraform, CI/CD

### What You Need to Do

1. Redesign the workflow.
2. Separate plan from apply.
3. Add an approval boundary for production.

### Solution

A safer flow is:

```text
Pull request
 ↓
terraform fmt
 ↓
terraform validate
 ↓
security/lint checks
 ↓
terraform plan
 ↓
review
 ↓
merge/protected environment
 ↓
approved apply
```

Production apply should require the appropriate protected environment approval. The plan should be an inspectable artifact or PR output, subject to the project's handling rules.

If the plan proposes a destructive replacement, stop and investigate. Do not bypass the review merely because the change was expected to be “small.”

### Why This Solution Works

Terraform makes infrastructure changes reviewable; automatic production apply removes the most important human/control boundary.

### Key Takeaway

Plan in CI, review the impact, protect production apply, and never normalize blind destructive changes.

## Question 20 — Create a Multi-Platform Pipeline Image

### Difficulty

Moderate

### Problem

Developers use Apple Silicon laptops, while production Kubernetes nodes are mostly `amd64`. A locally built image works on a developer machine but fails to run in production.

**Primary coverage:** Docker

### What You Need to Do

1. Explain the architecture mismatch.
2. Design a multi-platform build strategy.
3. State how the artifact should be referenced after the build.

### Solution

Build and publish a multi-platform image using Docker Buildx:

```bash
docker buildx build   --platform linux/amd64,linux/arm64   -t registry.example/pipeline:git-abc123   --push .
```

The registry can expose a multi-platform manifest so the runtime pulls the appropriate architecture.

If the application contains native dependencies, test both platforms and confirm that compatible wheels/binaries exist. The final release should still be identified immutably by digest/manifest identity rather than relying on `latest`.

Do not assume a successful local ARM build proves production AMD64 compatibility.

### Why This Solution Works

Container portability includes CPU architecture and native dependency compatibility, not only Python source portability.

### Key Takeaway

Test and publish the architectures you actually operate, and keep artifact identity immutable.


# Part III — Hard

## Question 21 — Recover a Kubernetes OOMKilled Spark-Like Batch Job

### Difficulty

Hard

### Problem

A containerized Python/Spark-oriented batch job succeeds locally but repeatedly gets `OOMKilled` in Kubernetes. The image is 900 MB, the pod requests 256Mi, limits 512Mi, and CI has no resource-oriented validation.

**Primary coverage:** Kubernetes, Docker, CI/CD

### What You Need to Do

1. Diagnose in the correct order.
2. Separate image size from runtime memory usage.
3. Design a recovery and prevention plan.

### Solution

Start with runtime evidence:

```bash
kubectl describe pod <pod>
kubectl get events --sort-by=.lastTimestamp
kubectl logs <pod> --previous
kubectl top pod <pod>   # when metrics are available
```

The 900 MB image size is not equivalent to 900 MB runtime memory usage. The immediate issue is the pod's memory boundary versus its workload requirement.

Then:

1. measure peak memory;
2. identify whether the workload or container configuration is responsible;
3. raise the request/limit only to a measured safe range;
4. inspect CPU throttling and data volume;
5. partition/reduce memory pressure if the job is intrinsically too large;
6. add CI/config validation so resource settings are reviewed;
7. rerun and observe.

Do not solve every OOM by arbitrarily multiplying the memory limit; that can merely move the failure to a larger bill or an overloaded node.

### Why This Solution Works

Production debugging separates symptoms. Image optimization helps distribution/build performance, while memory limits govern runtime behavior.

### Key Takeaway

Measure the workload, fix the runtime resource problem, and use CI plus Kubernetes evidence to prevent recurrence.

## Question 22 — Design a Safe Local Data Stack

### Difficulty

Hard

### Problem

A team needs a reproducible local stack containing PostgreSQL, MinIO, Kafka, Schema Registry, Airflow, and a Python pipeline. Developers currently start containers manually in different orders and put passwords into `.env` files that occasionally reach Git.

**Primary coverage:** Docker Compose, Docker, Secrets

### What You Need to Do

1. Design the Compose project structure.
2. Define health/dependency and initialization behavior.
3. Separate local convenience from production secret management.

### Solution

Use Compose services with explicit service names, networks, named volumes for persistent data, health checks, dependency conditions, and one-shot setup services.

Conceptually:

```text
core
 ├── postgres
 ├── minio
 └── pipeline

streaming profile
 ├── kafka
 └── schema-registry

airflow profile
 ├── airflow
 └── scheduler/worker as required
```

Use profiles to avoid forcing every developer to run the full stack. Setup services should be idempotent.

Use `.env.example` for non-sensitive defaults. Do not commit real credentials. Local secrets can use controlled developer mechanisms, but the production architecture should use a cloud secrets manager and workload identity.

CI can run a reduced integration profile, wait for health, run tests, collect logs, and tear the environment down.

### Why This Solution Works

Compose is a reproducibility tool for local and integration environments, not a replacement for production orchestration.

### Key Takeaway

Build local stacks declaratively, make initialization repeatable, and keep local secret convenience from becoming production credential architecture.

## Question 23 — Stop a Destructive Terraform Replacement

### Difficulty

Hard

### Problem

A Terraform plan proposes replacing a production data bucket because an attribute changed. The bucket contains important data. The engineer wants to apply immediately because the change is in a merged pull request.

**Primary coverage:** Terraform, Data Safety

### What You Need to Do

1. Diagnose the replacement.
2. Design a safe response.
3. Use Terraform safeguards and data backups appropriately.

### Solution

First stop the apply. Read the plan carefully and identify why Terraform believes replacement is required.

Then:

```text
plan
 ↓
identify replacement trigger
 ↓
confirm desired behavior
 ↓
backup/verify recoverability
 ↓
consider prevent_destroy where appropriate
 ↓
redesign resource/change if possible
 ↓
plan again
 ↓
review
 ↓
apply only after approval
```

A resource may use:

```hcl
lifecycle {
  prevent_destroy = true
}
```

when accidental destruction would be unacceptable and the team understands the operational implications.

`prevent_destroy` is not a substitute for backups. Data safety requires both infrastructure safeguards and recoverability.

### Why This Solution Works

Terraform can faithfully execute a dangerous desired state. The engineer must treat destructive plan output as a production safety signal.

### Key Takeaway

Read plans for replacement, protect critical resources, maintain backups, and redesign before applying destructive changes.

## Question 24 — Debug a Secret Retrieval Failure Across Identity Layers

### Difficulty

Hard

### Problem

A Kubernetes Job cannot retrieve `data-platform/prod/postgres`. The team says the secret exists and grants the namespace's ServiceAccount access. The Job still receives `Forbidden`.

**Primary coverage:** Secrets, Kubernetes, Terraform

### What You Need to Do

1. Diagnose authentication versus authorization.
2. Trace the identity chain.
3. Identify the likely infrastructure/IAM locations to inspect.

### Solution

Use the sequence:

```text
Who is the workload?
        ↓
Which ServiceAccount does the Job use?
        ↓
How is that ServiceAccount mapped to cloud identity?
        ↓
Which IAM principal reaches the cloud?
        ↓
Does that principal have read permission on this exact secret?
        ↓
Is the secret in the expected account/project/region?
```

Inspect Kubernetes configuration and events:

```bash
kubectl describe job <job>
kubectl describe pod <pod>
kubectl get serviceaccount <service-account>
kubectl get events --sort-by=.lastTimestamp
```

Then inspect the cloud IAM binding and secret resource policy. Terraform should be the source of truth for infrastructure permissions where it manages them.

Do not respond by granting broad `read-all-secrets` permissions. Correct the identity mapping or narrowly add the required permission.

### Why This Solution Works

Authentication establishes the caller; authorization decides whether that caller may access this secret. Mixing these diagnoses leads to excessive permissions.

### Key Takeaway

Trace identity → IAM → exact resource permission before changing access.

## Question 25 — Design Secure CI for a Data Repository

### Difficulty

Hard

### Problem

A GitHub Actions pipeline currently stores an AWS access key as a repository secret. The same credential can build images, read all secrets, and apply Terraform to production. The workflow also uses floating third-party Actions tags.

**Primary coverage:** CI/CD, Secrets, Terraform, Docker

### What You Need to Do

1. Redesign the identity and permission model.
2. Separate build, test, and deployment permissions.
3. Replace long-lived cloud keys with OIDC.
4. Add supply-chain and secret controls.

### Solution

Use:

```text
PR
 ↓
lint/test/data checks
 ↓
build image
 ↓
scan image
 ↓
publish immutable artifact
 ↓
protected deployment environment
 ↓
OIDC
 ↓
environment-specific IAM role
 ↓
Terraform/app deployment
```

Grant the workflow only the permissions required for its job. Production should use a protected environment and an approval boundary.

Use OIDC so the CI platform receives a short-lived identity rather than storing a long-lived cloud key.

Pin third-party Actions according to the repository's supply-chain policy, preferably to immutable commit SHAs. Add secret scanning, dependency scanning, and minimal workflow permissions.

### Why This Solution Works

The biggest security flaw is not merely the presence of a repository secret; it is that one long-lived identity has excessive authority across build, secrets, and production infrastructure.

### Key Takeaway

Split trust boundaries: build identity, deployment identity, environment, and resource permissions should be independently constrained.

## Question 26 — Promote a Data Pipeline Without Rebuilding

### Difficulty

Hard

### Problem

A data pipeline has passed tests in staging. The release engineer rebuilds the Docker image for production and reruns Terraform from a slightly different working tree. Production behavior differs from staging.

**Primary coverage:** Environment Promotion, Docker, CI/CD, Terraform

### What You Need to Do

1. Redesign the promotion flow.
2. Define what is promoted versus what changes by environment.
3. Explain how to record the release.

### Solution

Use immutable promotion:

```text
Git commit
   ↓
CI build
   ↓
image digest
   ↓
tests + scans
   ↓
staging deployment
   ↓
approval
   ↓
same image digest → production
```

Environment-specific values change through configuration/IAM/secret references, not through rebuilding the application artifact.

Terraform should use the production environment's state/configuration and undergo its own plan/review. The exact application image remains unchanged.

Record:

- Git SHA;
- image digest;
- dbt artifact/version where applicable;
- Terraform plan/change;
- environment;
- approval;
- deployment timestamp.

This creates traceability from source to production.

### Why This Solution Works

Promotion separates artifact identity from environment configuration. Rebuilding introduces an untested artifact and breaks reproducibility.

### Key Takeaway

Promote immutable artifacts; do not rebuild production from the same source revision.

## Question 27 — Implement Shadow Validation Before Production

### Difficulty

Hard

### Problem

A new Spark/Python pipeline version changes transformation logic. The team wants to compare its output with the current production version using production-like inputs without allowing the new result to replace production data.

**Primary coverage:** Environment Promotion, Kubernetes, CI/CD

### What You Need to Do

1. Design a shadow run.
2. Use shadow tables or isolated outputs.
3. Define a promotion gate.

### Solution

Use:

```text
production inputs
      ↓
+------------------+
| current version  | → production output
+------------------+
      |
+------------------+
| candidate version| → shadow output
+------------------+
      ↓
comparison
      ↓
promotion decision
```

The candidate writes to a separate shadow table/schema or other isolated destination. Compare:

- row counts;
- keys;
- aggregates;
- null/error rates;
- business-specific invariants.

Only after comparison meets the agreed thresholds should the candidate be promoted.

The candidate must still use controlled credentials and resource boundaries. A shadow run is not permission to let experimental code write to production tables.

### Why This Solution Works

Shadow execution separates validation from production mutation. It provides evidence about real inputs without requiring immediate cutover.

### Key Takeaway

Validate candidate outputs in isolation before allowing them to become authoritative production data.

## Question 28 — Recover From a Bad Release

### Difficulty

Hard

### Problem

A new image and Airflow DAG are deployed to production. The DAG writes incorrect aggregates for two hours. The code rollback is straightforward, but the incorrect data remains in the warehouse.

**Primary coverage:** Environment Promotion, Docker, Kubernetes, Airflow

### What You Need to Do

1. Separate code rollback from data recovery.
2. Design a safe recovery sequence.
3. Explain when time travel, restore, or backfill may be appropriate.

### Solution

Use two distinct tracks:

```text
CONTROL PLANE
image/DAG rollback
       ↓
stop further bad writes

DATA PLANE
identify affected partitions/time window
       ↓
restore/time-travel if supported
OR
recompute from trusted inputs
       ↓
validate
       ↓
backfill/reconcile
```

First prevent additional corruption. Then identify the exact affected data interval. Use table-format/warehouse recovery capabilities, backups, or trusted source data as appropriate. Validate restored results before re-enabling normal processing.

Record the incident/change history and preserve evidence.

Do not assume reverting the Git commit automatically reverses already-written data.

### Why This Solution Works

Code is declarative history for behavior; data is a durable state that may require independent recovery.

### Key Takeaway

Always plan code rollback and data rollback as separate but coordinated operations.

## Question 29 — Design Environment Isolation With Protected Promotion

### Difficulty

Hard

### Problem

A company has one cloud account and one database schema for dev, staging, and production. Developers can run CI against the same schema used by production-like workloads, and CI can read production credentials.

**Primary coverage:** Environment Promotion, CI/CD, Secrets

### What You Need to Do

1. Design an environment-isolation model.
2. Define protected production access.
3. Explain how credentials and data should differ.

### Solution

Prefer separate cloud accounts/projects where practical, with separate:

- buckets;
- catalogs/schemas;
- secret namespaces;
- workload identities;
- Terraform state;
- CI environments.

Use:

```text
dev → automatic
staging → automated after checks
production → protected environment + approval
```

Non-production data should be synthetic, sampled appropriately, or masked; do not copy raw sensitive production data into developer environments without a justified controlled process.

Production credentials must not be available to developer CI jobs. OIDC roles and IAM should encode these boundaries.

### Why This Solution Works

Environment isolation is a security and blast-radius control, not merely a deployment convenience.

### Key Takeaway

Separate state, data, identity, and credentials; then add protected production promotion.

## Question 30 — Diagnose a Multi-Layer Pipeline Failure

### Difficulty

Hard

### Problem

A production pipeline follows:

```text
GitHub → CI → Docker image → Kubernetes Job → Airflow → PostgreSQL
```

After a release, the Job starts but exits quickly. The image was scanned successfully, the pod is not OOMKilled, and logs show a database authentication error.

**Primary coverage:** Docker, Kubernetes, Secrets, CI/CD, Environment Promotion

### What You Need to Do

1. Define the debugging order.
2. Distinguish image, Kubernetes, identity, secret, and database problems.
3. Specify what evidence you would collect before changing permissions.

### Solution

Use a layered diagnosis:

1. **Artifact** — confirm the deployed image digest is the intended promoted digest.
2. **Kubernetes** — inspect pod status, events, ServiceAccount, environment/config references.
3. **Identity** — establish which workload identity the Job actually uses.
4. **Secret access** — verify the workload can read the intended environment's secret.
5. **Secret version** — determine whether rotation changed the credential.
6. **Database** — verify host, database, user, network path, and credential validity.
7. **Application** — inspect whether the client caches credentials or uses stale connection pools.

Useful commands include:

```bash
kubectl describe pod <pod>
kubectl logs <pod>
kubectl get events --sort-by=.lastTimestamp
```

Do not immediately grant broad database or secret permissions. The authentication failure could be caused by stale cached credentials or the wrong environment secret.

### Why This Solution Works

Distributed systems require layered debugging. Starting at the symptom and jumping directly to permissions often creates security regressions.

### Key Takeaway

Debug from immutable artifact identity through runtime identity, secret version, connection configuration, and target system.


# Part IV — Advanced

## Question 31 — Architect the Full Production Delivery Platform

### Difficulty

Advanced

### Problem

A data platform is moving from manual laptop deployments to a reproducible production platform. It contains Python ingestion, dbt, Airflow, Spark, PostgreSQL, object storage, Kubernetes Jobs, Terraform, and GitHub Actions.

**Primary coverage:** Docker, Docker Compose, Kubernetes, Terraform, CI/CD, Environment Promotion, Secrets

### What You Need to Do

1. Design the end-to-end architecture.
2. Define local development, CI, promotion, runtime identity, and rollback boundaries.
3. Explain which components are production orchestration versus development tooling.

### Solution

A strong architecture is:

```text
Developer
  ↓
Compose local stack
  ↓
pre-commit
  ↓
Git PR
  ↓
CI: lint/type/test/data checks
  ↓
Docker build + scan + SBOM
  ↓
immutable registry artifact
  ↓
Terraform plan/review
  ↓
dev deployment
  ↓
staging validation/shadow checks
  ↓
protected production approval
  ↓
same image digest
  ↓
Kubernetes/Airflow/Spark runtime
  ↓
workload identity
  ↓
Secrets Manager / cloud resources
```

Compose remains the local/integration environment. Kubernetes or managed services provide production orchestration. Terraform manages infrastructure and protected state. CI builds once and promotes the artifact. OIDC replaces long-lived cloud keys. Secrets are retrieved at runtime.

Rollback must cover code/image, orchestration configuration, and data recovery separately.

### Why This Solution Works

The platform becomes reproducible when every boundary has an explicit source of truth: Git for code, registry digest for artifact, Terraform for infrastructure, IAM for access, secrets manager for credentials, and controlled promotion for release.

### Key Takeaway

Senior design means making identity, artifact, infrastructure, environment, data, and recovery boundaries explicit.

## Question 32 — Secure the Platform Against a Credential Leak

### Difficulty

Advanced

### Problem

A developer commits a production-style API credential to Git. The credential appears in a CI log, was copied into a Docker build context, and may have been available to a Kubernetes Job.

**Primary coverage:** Secrets, CI/CD, Docker, Terraform, Kubernetes

### What You Need to Do

1. Execute a complete incident response.
2. Identify the detection and containment layers.
3. Prevent recurrence across Git, CI, images, Kubernetes, and runtime.

### Solution

Immediate sequence:

```text
detect
→ revoke/rotate
→ audit access logs
→ identify affected artifacts/logs/workloads
→ clean repository history where appropriate
→ replace credential references
→ rebuild/redeploy affected artifacts
→ verify old credential fails
→ verify new credential works
→ post-mortem
```

Detection layers include pre-commit scanning, repository push protection, CI scanning, image scanning, and log monitoring.

The long-term design removes credentials from images and source, uses workload identity, retrieves secrets at runtime, restricts Kubernetes workload permissions, and uses OIDC for CI.

Do not delay revocation until Git history cleanup is complete. Containment comes first.

### Why This Solution Works

Secret incidents cross system boundaries. A credential that entered Git can propagate into CI logs, images, artifacts, and runtime systems.

### Key Takeaway

Revoke first, investigate second, clean up comprehensively, then redesign the path that allowed the leak.

## Question 33 — Design Zero-Downtime Rotation Across Airflow and Kubernetes

### Difficulty

Advanced

### Problem

A production database password must rotate. Airflow tasks use connection pooling, while Kubernetes Jobs cache the secret for several minutes. The database must remain available during rotation.

**Primary coverage:** Secrets, Kubernetes, Airflow, Environment Promotion

### What You Need to Do

1. Design a rotation protocol.
2. Account for Airflow, Kubernetes, application cache, and connection pools.
3. Define validation and rollback.

### Solution

Use an overlapping credential strategy where the database supports it:

```text
A active
 ↓
create B
 ↓
publish B as current
 ↓
Airflow/backend refreshes
 ↓
Kubernetes workloads refresh
 ↓
new DB connections use B
 ↓
old connections drain
 ↓
verify workload health
 ↓
revoke A
```

Use bounded caches and explicit refresh. Configure connection pools to recycle old connections. Monitor authentication failures during the transition.

If the platform cannot overlap credentials, coordinate a maintenance window or use an application/database mechanism that supports a safe transition.

Rollback means restoring a known-valid credential version and ensuring clients can refresh again; do not blindly re-enable the revoked credential without investigating the failure.

### Why This Solution Works

Rotation is a distributed rollout. Secret-manager state, application caches, connection pools, schedulers, and database authentication all have to converge.

### Key Takeaway

Design credential rotation as a deployment with compatibility, observation, and recovery—not as a single secret update.

## Question 34 — Protect Terraform, Secrets, and CI as One Trust Chain

### Difficulty

Advanced

### Problem

A Terraform module creates a production database, secret, KMS association, and workload IAM role. CI currently receives a long-lived cloud key and Terraform outputs the database password for convenience.

**Primary coverage:** Terraform, Secrets, CI/CD, Environment Promotion

### What You Need to Do

1. Redesign the trust chain.
2. Decide what Terraform should manage versus what the runtime should retrieve.
3. Define the CI identity and state controls.

### Solution

Use Terraform to manage infrastructure relationships:

```text
secret resource
KMS/key association
IAM policy
workload identity
database infrastructure
```

Avoid exposing the password as a Terraform output. Prefer the application to retrieve the secret at runtime.

Protect remote state with encryption, strict access, locking, and auditability. Remember that `sensitive = true` changes display behavior but does not guarantee the value is absent from state.

CI should use OIDC and an environment-specific role. Production apply should be protected and approved. The workload identity should read only the required secret.

The trust chain becomes:

```text
CI OIDC
 → deployment role
 → Terraform state + infrastructure
 → workload identity
 → exact secret
 → application
```

Each hop should have least privilege.

### Why This Solution Works

Security failures often occur at trust-boundary joins. A secure secret manager cannot compensate for unrestricted Terraform state or an all-powerful CI key.

### Key Takeaway

Design the entire identity and data flow, not isolated security controls.

## Question 35 — Build a Reproducible Multi-Architecture Release

### Difficulty

Advanced

### Problem

A data platform supports ARM developer machines and AMD64 production nodes. Native Python dependencies occasionally produce different results on each architecture. The release process builds independently on developers and production runners.

**Primary coverage:** Docker, CI/CD, Environment Promotion

### What You Need to Do

1. Design a reproducible multi-platform release.
2. Address native wheels, immutable identity, scanning, and promotion.
3. Define what evidence CI should retain.

### Solution

CI should own the release build:

```text
locked dependencies
 + pinned/base-image policy
        ↓
multi-platform Buildx build
        ↓
amd64 + arm64 validation
        ↓
vulnerability scan
        ↓
SBOM
        ↓
immutable registry artifact
        ↓
digest recorded
        ↓
staging
        ↓
production
```

Where base-image digests are part of the project's reproducibility policy, pin them rather than relying solely on mutable tags.

Test native dependencies on both supported architectures. Do not assume a wheel built on ARM is interchangeable with an AMD64 environment.

Retain Git SHA, image digest/manifest identity, build metadata, scan results, and test evidence.

### Why This Solution Works

Reproducibility includes the build environment and CPU architecture. An identical source tree can still produce incompatible runtime artifacts when native dependencies differ.

### Key Takeaway

Centralize release builds, test every supported architecture, and promote immutable artifacts with evidence.

## Question 36 — Design a Safe Data Rollback Strategy

### Difficulty

Advanced

### Problem

A production release contains three changes: a new image, a new Airflow DAG, and a database schema migration. The release fails halfway through deployment. Some infrastructure is updated, the image is live, and the migration has already run.

**Primary coverage:** Environment Promotion, Terraform, Kubernetes, CI/CD

### What You Need to Do

1. Design an ordered deployment and rollback strategy.
2. Explain why simply reverting Git is insufficient.
3. Use expand-and-contract thinking where appropriate.

### Solution

Use an ordered strategy:

```text
1. infrastructure prerequisites
2. backward-compatible schema expansion
3. application/image deployment
4. DAG/dbt rollout
5. validation
6. contract/cleanup migration later
```

For failure recovery, determine which stages actually completed. Roll back application artifacts where safe, but do not automatically roll back a database migration if the new schema is already being used.

Prefer expand-and-contract:

```text
expand → deploy compatible code → migrate data → validate → contract later
```

This makes application rollback safer because the previous version can continue to understand the expanded schema.

Data restoration, backfill, or time-travel mechanisms are separate decisions if incorrect data was written.

### Why This Solution Works

Schema changes have stateful consequences. Safe rollback requires backward compatibility and an understanding of which state transitions are reversible.

### Key Takeaway

Design migrations and deployment ordering so the system remains compatible throughout the transition.

## Question 37 — Design a Production Secrets and Identity Architecture

### Difficulty

Advanced

### Problem

Design a multi-environment platform where Airflow, Kubernetes Jobs, Spark, serverless functions, and GitHub Actions all require access to different cloud resources. Security requires no long-lived cloud keys and strict environment isolation.

**Primary coverage:** Secrets, Kubernetes, CI/CD, Terraform, Environment Promotion

### What You Need to Do

1. Define identities per workload.
2. Define secret boundaries.
3. Design CI OIDC and production approval.
4. Explain auditing and rotation.

### Solution

Use separate identities:

```text
Airflow-prod identity
Kubernetes-prod identity
Spark-prod identity
Serverless-prod identity
CI-prod deployment role
```

Each receives only the permissions required for its resources and secrets.

Secrets are separated:

```text
dev/* → dev identities
staging/* → staging identities
prod/* → production identities
```

CI uses OIDC:

```text
GitHub job
 → OIDC token
 → cloud trust policy
 → temporary role
```

Production deployment is protected by environment approval. Applications retrieve secrets at runtime. Secret access and IAM actions are audited. Rotation is designed with versioning and refresh behavior.

Terraform manages identity/resource relationships and secure state rather than becoming a plaintext secret repository.

### Why This Solution Works

Identity is the central security primitive. Environment isolation is strongest when it is encoded into identity and authorization rather than merely into naming conventions.

### Key Takeaway

Design each workload as an identity with narrowly scoped permissions and a clearly defined environment boundary.

## Question 38 — Operate a Platform When Everything Changes at Once

### Difficulty

Advanced

### Problem

A release changes the Docker base image, Kubernetes resource limits, Terraform IAM policy, secret version, and application code. Production reports failures immediately after deployment.

**Primary coverage:** Docker, Docker Compose, Kubernetes, Terraform, CI/CD, Environment Promotion, Secrets

### What You Need to Do

1. Create a disciplined debugging sequence.
2. Prevent concurrent changes from hiding the root cause.
3. Explain what evidence should be compared between staging and production.

### Solution

Start with release identity:

```text
Which Git SHA?
Which image digest?
Which Terraform plan?
Which secret version?
Which Kubernetes manifest?
```

Then compare staging and production.

Debug in dependency order:

```text
artifact
 ↓
runtime scheduling/resources
 ↓
workload identity
 ↓
secret access/version
 ↓
network/configuration
 ↓
application/database
```

Inspect:

```bash
kubectl describe pod <pod>
kubectl logs <pod>
kubectl get events --sort-by=.lastTimestamp
```

Review Terraform plan/change records and cloud audit logs. Avoid changing five things simultaneously during incident response.

For recovery, restore the last known-good immutable artifact and known-good configuration where possible. If the secret version is implicated, use the controlled rotation/recovery procedure rather than manually copying credentials.

### Why This Solution Works

Multiple simultaneous changes destroy causal clarity. Production operations need immutable evidence and controlled rollback points.

### Key Takeaway

Track every release input and debug from immutable artifact identity through runtime dependencies before making additional changes.

## Question 39 — Design the Module 2.18 Mini-Project Architecture

### Difficulty

Advanced

### Problem

You are replacing a manually configured data platform with:

```text
Python ingestion
dbt
Airflow
Spark
PostgreSQL
object storage
Kubernetes
Terraform
GitHub Actions
cloud secrets manager
```

The organization wants reproducible local development, automated CI, controlled promotion, and auditable production releases.

**Primary coverage:** Docker, Docker Compose, Kubernetes, Terraform, CI/CD, Environment Promotion, Secrets

### What You Need to Do

1. Produce the architecture.
2. Define local versus production responsibilities.
3. Define artifact, infrastructure, identity, secret, and rollback sources of truth.

### Solution

A strong solution separates concerns:

```text
LOCAL
Compose
 ├── PostgreSQL
 ├── object storage
 ├── streaming dependencies as needed
 ├── Airflow
 └── pipeline containers

CI
 ├── Python/data tests
 ├── integration stack
 ├── Docker build/scan/SBOM
 ├── Terraform fmt/validate/security/plan
 └── secret scanning

PROMOTION
dev → staging → protected production
       same immutable artifacts

PRODUCTION
Kubernetes / managed services
 ├── Airflow
 ├── Jobs
 └── Spark

IDENTITY
workload identity + OIDC

SECRETS
cloud secrets manager + KMS + rotation

INFRASTRUCTURE
Terraform + protected remote state

RECOVERY
code/image rollback
+
schema-safe migration strategy
+
data restoration/backfill where necessary
```

Compose is not the production orchestrator. Terraform is not the secret vault. CI builds and validates but should not hold permanent cloud administrator credentials. Production workloads retrieve secrets at runtime.

### Why This Solution Works

The architecture succeeds because every responsibility has a clear boundary and the same artifact can travel from validation to production without reconstruction.

### Key Takeaway

Production readiness is the composition of reproducibility, identity, infrastructure-as-code, CI, promotion, secrets, and recovery.

## Question 40 — Senior Incident: Secure, Recover, and Explain

### Difficulty

Advanced

### Problem

A production incident unfolds:

1. A developer commits a credential.
2. CI does not detect it.
3. The credential is copied into a Docker build context.
4. The image is deployed with a mutable tag.
5. A Kubernetes Job reads the wrong environment secret.
6. Terraform drift exists in the production bucket policy.
7. The job writes incorrect data.
8. The team considers reverting the Git commit.

**Primary coverage:** Docker, Docker Compose, Kubernetes, Terraform, CI/CD, Environment Promotion, Secrets

### What You Need to Do

1. Respond as the senior engineer leading the incident.
2. Contain the security issue.
3. Stop incorrect writes.
4. Recover infrastructure/application/data safely.
5. Design the permanent prevention controls.
6. Explain the final architecture to an engineering review board.

### Solution

Treat this as multiple connected incidents, not one Git problem.

**Containment**

```text
credential
 → revoke/rotate
 → audit usage
```

Stop the bad workload and prevent additional incorrect writes.

**Artifact**

Determine the exact image digest actually deployed. Do not trust the mutable tag.

**Identity/secrets**

Verify the Kubernetes workload identity and environment-specific secret reference. Correct the IAM/secret mapping without granting broad access.

**Infrastructure**

Inspect Terraform drift and plan before changing the bucket policy. Restore the intended state only after verifying that the plan is safe and data access is preserved.

**Data**

Identify the affected time range/partitions. Use trusted source data, time travel/restore, or controlled backfill according to the platform's recovery capabilities. Validate before reopening normal writes.

**Prevention**

Add:

```text
pre-commit secret scan
→ repository push protection
→ CI secret scan
→ image scan/SBOM
→ OIDC
→ least-privilege IAM
→ environment-specific secrets
→ immutable image digests
→ protected Terraform plan/apply
→ drift detection
→ shadow validation
→ documented rollback
```

**Senior explanation**

The root problem is a missing chain of trust. Code, artifact, identity, infrastructure, environment, secret, and data state were not independently controlled. The corrected platform makes each boundary explicit and auditable.

### Why This Solution Works

This scenario tests the central Module 2.18 competency: moving from ad hoc operations to a reproducible, secure, reviewable, recoverable production platform.

### Key Takeaway

A senior engineer must contain first, preserve evidence, recover safely, and then redesign the system so the same failure is harder to repeat.


# Final Module Coverage Matrix

The matrix below maps all 40 questions to the seven Module 2.18 topics. A check mark means the question materially tests that topic; it is not merely mentioned in passing.

| Question | Docker | Compose | Kubernetes | Terraform | CI/CD | Promotion | Secrets | Difficulty |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|

| Q1 | ✓ |  |  |  |  |  |  | Basic |
| Q2 |  | ✓ |  |  |  |  |  | Basic |
| Q3 |  | ✓ |  |  |  |  |  | Basic |
| Q4 |  |  | ✓ |  |  |  |  | Basic |
| Q5 |  |  |  | ✓ |  |  |  | Basic |
| Q6 |  |  |  |  | ✓ |  |  | Basic |
| Q7 |  |  |  |  |  | ✓ | ✓ | Basic |
| Q8 | ✓ |  |  |  |  | ✓ |  | Basic |
| Q9 | ✓ |  |  |  |  |  | ✓ | Basic |
| Q10 |  | ✓ |  |  |  |  |  | Basic |
| Q11 | ✓ |  |  |  |  |  |  | Moderate |
| Q12 |  | ✓ |  |  |  |  |  | Moderate |
| Q13 |  |  | ✓ |  |  |  |  | Moderate |
| Q14 |  |  |  | ✓ |  |  |  | Moderate |
| Q15 |  |  |  |  | ✓ |  |  | Moderate |
| Q16 | ✓ |  |  |  | ✓ | ✓ |  | Moderate |
| Q17 |  |  | ✓ |  |  |  | ✓ | Moderate |
| Q18 |  |  |  |  |  |  | ✓ | Moderate |
| Q19 |  |  |  | ✓ | ✓ |  |  | Moderate |
| Q20 | ✓ |  |  |  |  |  |  | Moderate |
| Q21 | ✓ |  | ✓ |  | ✓ |  |  | Hard |
| Q22 | ✓ | ✓ |  |  |  |  | ✓ | Hard |
| Q23 |  |  |  | ✓ |  |  |  | Hard |
| Q24 |  |  | ✓ | ✓ |  |  | ✓ | Hard |
| Q25 | ✓ |  |  | ✓ | ✓ |  | ✓ | Hard |
| Q26 | ✓ |  |  | ✓ | ✓ | ✓ |  | Hard |
| Q27 |  |  | ✓ |  | ✓ | ✓ |  | Hard |
| Q28 | ✓ |  | ✓ |  |  | ✓ |  | Hard |
| Q29 |  |  |  |  | ✓ | ✓ | ✓ | Hard |
| Q30 | ✓ |  | ✓ |  | ✓ | ✓ | ✓ | Hard |
| Q31 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Advanced |
| Q32 | ✓ |  | ✓ | ✓ | ✓ |  | ✓ | Advanced |
| Q33 |  |  | ✓ |  |  | ✓ | ✓ | Advanced |
| Q34 |  |  |  | ✓ | ✓ | ✓ | ✓ | Advanced |
| Q35 | ✓ |  |  |  | ✓ | ✓ |  | Advanced |
| Q36 |  |  | ✓ | ✓ | ✓ | ✓ |  | Advanced |
| Q37 |  |  | ✓ | ✓ | ✓ | ✓ | ✓ | Advanced |
| Q38 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Advanced |
| Q39 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Advanced |
| Q40 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Advanced |

## Coverage Notes

The questions intentionally use cross-topic scenarios in the Hard and Advanced sections. In particular:

- Docker is tested through image construction, caching, security, signals, reproducibility, and multi-platform release.
- Compose is tested through networking, health/readiness, volumes, idempotent initialization, and complete local-stack design.
- Kubernetes is tested through Jobs/CronJobs, resources, identity, secrets, runtime diagnosis, and production orchestration.
- Terraform is tested through state, drift, destructive replacement, plan/apply controls, IAM, and production recovery.
- CI/CD is tested through data-specific validation, image build/scan, OIDC, artifact promotion, and protected deployment.
- Environment promotion is tested through immutable artifacts, environment isolation, shadow validation, deployment ordering, and rollback.
- Secrets are tested through runtime retrieval, workload identity, least privilege, rotation, incident response, and cross-platform delivery.

At least five scenarios explicitly require a **break → diagnose → recover** response: Questions 21, 23, 25, 28, 30, 32, 33, 36, 38, and 40.


# Final Readiness Checklist

Use this checklist after completing all 40 problems.

### Docker

- [ ] I can build secure reproducible Docker images.
- [ ] I can optimize Docker layer caching.
- [ ] I can use `uv` and lock files appropriately.
- [ ] I can handle PID 1, signals, and graceful shutdown.
- [ ] I can use non-root runtime users.
- [ ] I can reason about base-image and native dependency trade-offs.
- [ ] I can use image scanning and SBOM concepts.
- [ ] I can avoid secrets in image layers.
- [ ] I can build multi-platform images.

### Docker Compose

- [ ] I can build a complete local data stack.
- [ ] I can use service-name DNS correctly.
- [ ] I can distinguish ports from internal service networking.
- [ ] I can use health checks and dependency conditions.
- [ ] I can create idempotent one-shot setup services.
- [ ] I can choose named volumes versus bind mounts appropriately.
- [ ] I can use profiles and Compose overrides.
- [ ] I can run Compose-based integration tests.
- [ ] I understand Compose's production limitations.

### Kubernetes

- [ ] I understand clusters, nodes, control plane, pods, deployments, and services.
- [ ] I can run and troubleshoot Jobs and CronJobs.
- [ ] I can prevent overlapping batch runs.
- [ ] I can diagnose `OOMKilled`.
- [ ] I can reason about CPU requests, memory requests, and limits.
- [ ] I can use ServiceAccounts and workload identity concepts.
- [ ] I understand Kubernetes Secret limitations.
- [ ] I understand Helm/operators/autoscaling at the level taught by the module.
- [ ] I can debug using `kubectl`, events, and logs.

### Terraform

- [ ] I can write Terraform for data infrastructure.
- [ ] I understand configuration versus state.
- [ ] I can use remote state and locking.
- [ ] I can build reusable modules.
- [ ] I can use `count` and `for_each`.
- [ ] I can detect and reconcile drift.
- [ ] I can recognize destructive replacement in a plan.
- [ ] I can protect critical resources.
- [ ] I can use Terraform safely in CI.

### CI/CD

- [ ] I can build a production-oriented CI workflow.
- [ ] I can run Python, Airflow, SQL, and data-contract checks.
- [ ] I understand dbt slim CI and isolated CI schemas.
- [ ] I can build, scan, and publish immutable images.
- [ ] I can use OIDC instead of long-lived cloud keys.
- [ ] I can apply least-privilege workflow permissions.
- [ ] I understand protected branches and production approvals.
- [ ] I can optimize CI with caching, parallelism, matrices, and path filters.
- [ ] I understand the build-once/store/promote model.

### Environment Promotion

- [ ] I understand dev/staging/prod isolation.
- [ ] I can separate environment-specific credentials and resources.
- [ ] I can promote immutable artifacts rather than rebuild them.
- [ ] I can use image digests for release identity.
- [ ] I can design deployment ordering around infrastructure and migrations.
- [ ] I can use synthetic/masked/non-production data appropriately.
- [ ] I understand shadow validation.
- [ ] I understand ephemeral environments.
- [ ] I can distinguish code rollback from data rollback.
- [ ] I can design expand-and-contract migrations.

### Secrets

- [ ] I can distinguish configuration from secrets.
- [ ] I can use a cloud secrets manager conceptually and from Python.
- [ ] I can use workload identity instead of bootstrap keys.
- [ ] I can cache and refresh secrets safely.
- [ ] I can design zero-downtime rotation.
- [ ] I can enforce least privilege per secret.
- [ ] I can integrate secrets with Airflow and Kubernetes.
- [ ] I understand CI/OIDC and environment-scoped secrets.
- [ ] I understand dynamic secrets, KMS, SOPS, and Terraform secret/state risks.
- [ ] I can detect and respond to leaked credentials.

### Senior-Level Readiness

- [ ] I can diagnose multi-layer production failures systematically.
- [ ] I can explain the security and operational trade-offs in my designs.
- [ ] I can recover a platform without blindly reverting code.
- [ ] I can separate artifact, infrastructure, identity, environment, secret, and data state.
- [ ] I can design an auditable production delivery architecture.
- [ ] I can explain why each control exists and what failure it prevents.
