# Claude Code Task — Build the Complete Learning Module

## ROLE

Act as a **Senior Data Engineer with 10+ years of production industry experience** designing, building, deploying, and operating production-grade data platforms.

You are highly experienced in:

- Docker
- Docker Compose
- Python Data Engineering
- PostgreSQL
- Object Storage
- MinIO
- Kafka
- Schema Registry
- Apache Airflow
- Data pipelines
- Integration testing
- Local development environments
- CI/CD
- Container networking
- Container storage
- Health checks
- Production reliability
- Container security
- Resource management

Your task is to create a **complete, detailed, beginner-to-advanced learning module** for:

`18-Containers-Infrastructure-and-CI-CD-for-Data/02-docker-compose-for-local-data-stacks.md`

The learner has already studied:

`01-docker-images-for-python-pipelines.md`

Therefore, this module must build directly on the Docker image/container foundation from Topic 01 and teach Docker Compose as the next layer.

---

# 1. AUTHORITATIVE SOURCE OF TRUTH

The authoritative roadmap is the Module 2.18 roadmap:

`18-Containers-Infrastructure-and-CI-CD-for-Data/`

The target topic is:

**Topic 02 — Docker Compose for local data stacks**

The roadmap defines this topic as the mechanism for running a complete local data platform stack involving services such as:

- PostgreSQL
- Object storage / MinIO
- Kafka
- Schema Registry
- Airflow
- Pipeline containers

The roadmap specifically requires:

### Basics

- Compose files
- Services
- Images vs builds
- Ports
- Environment variables
- `docker compose up`
- `docker compose down`
- `docker compose logs`
- `docker compose exec`
- Networks
- Service names as hostnames
- Named volumes
- Bind mounts
- Environment files
- Variable substitution

### Intermediate

- Health checks
- `depends_on` conditions
- Dependency readiness
- One-shot setup services
- Bucket initialization
- Kafka topic initialization
- Database schema initialization
- Seed data
- Idempotent initialization
- Profiles
- `core`, `streaming`, `spark`, `airflow` style profiles
- Override files
- Local vs CI configurations
- Resource limits

### Advanced

- Live development workflows
- Bind mounts/watch mode vs rebuilt images
- Compose in CI
- Integration-test environments
- Containerized test fixtures
- Compose secrets
- Secret files vs environment variables
- Resource constraints
- Limitations of Compose
- Single-host architecture
- Lack of production self-healing/scaling
- Why production often uses Kubernetes or managed services

Use these roadmap requirements as the **source of truth**.

Do not skip any concept.

Do not silently replace roadmap concepts with unrelated technologies.

---

# 2. STRICT FILE-SCOPE RULE

You may modify **ONLY**:

`18-Containers-Infrastructure-and-CI-CD-for-Data/02-docker-compose-for-local-data-stacks.md`

Do **NOT** modify:

- `README.md`
- `learning-plan.md`
- `01-docker-images-for-python-pipelines.md`
- `03-kubernetes-concepts-for-data-workloads.md`
- `04-terraform-basics-for-data-infrastructure.md`
- `05-ci-pipelines-for-data-projects.md`
- `06-environment-promotion-dev-staging-and-prod.md`
- `07-cloud-secrets-managers.md`
- `practice-questions.md`
- Any other Markdown file
- Any other folder
- Any project source file
- Any configuration file outside the target learning file

Do not rename, move, delete, or create other files.

The **only expected modification is**:

`02-docker-compose-for-local-data-stacks.md`

---

# 3. PRIMARY LEARNING OBJECTIVE

Teach the learner how to design, write, run, debug, test, and maintain a **complete local data-engineering stack using Docker Compose**.

The learner must progress through:

```text
Docker fundamentals from Topic 01
        ↓
Why Compose exists
        ↓
Compose mental model
        ↓
Compose file structure
        ↓
Services
        ↓
Images vs builds
        ↓
Ports
        ↓
Environment configuration
        ↓
Networks
        ↓
Volumes
        ↓
Service discovery
        ↓
Health checks
        ↓
depends_on conditions
        ↓
Initialization services
        ↓
Idempotent setup
        ↓
Profiles
        ↓
Override files
        ↓
Resource limits
        ↓
Development workflows
        ↓
Compose-based integration testing
        ↓
Secrets
        ↓
Complete local data stack
        ↓
Debugging
        ↓
Production boundaries
        ↓
Advanced architecture
```

The learner should finish this module able to build a local data platform from a clean clone using Compose.

---

# 4. TEACHING PHILOSOPHY

Teach everything from **simple → practical → intermediate → advanced → production**.

Do not merely document Compose syntax.

For every major concept explain:

### What

What is this?

### Why

Why does Docker Compose need this?

### How

How does it work?

### Example

Show a realistic Compose example.

### Data Engineering relevance

Why does a Data Engineer care?

### Failure mode

What happens when it is configured incorrectly?

### Debugging

How do you identify and fix the problem?

### Production consideration

How would this be handled in a serious engineering environment?

### Mental model

Give a concise mental model.

---

# 5. START WITH THE PROBLEM DOCKER COMPOSE SOLVES

Begin with the real-world problem.

A data platform rarely contains one container.

Explain a realistic local platform:

```text
Python Pipeline
       ↓
PostgreSQL
       ↓
MinIO / Object Storage
       ↓
Kafka
       ↓
Schema Registry
       ↓
Airflow
```

Explain why running each container manually becomes difficult.

For example:

```bash
docker run ...
docker run ...
docker run ...
docker run ...
```

Then introduce Docker Compose as a way to declaratively define the stack.

Explain:

> Compose describes the services, networks, storage, configuration, health requirements, and relationships required to run the local system.

---

# 6. DOCKER COMPOSE MENTAL MODEL

Build a clear mental model:

```text
                    compose.yaml
                         |
        +----------------+----------------+
        |                |                |
     Service          Service           Service
        |                |                |
   Container        Container         Container
        |                |                |
      Volume           Volume           Volume
        \                |               /
         +----------- Network -----------+
```

Explain:

- Compose project
- Compose file
- Service
- Container
- Network
- Volume
- Configuration
- Dependency

Clearly distinguish:

```text
Compose service
```

from:

```text
running container
```

---

# 7. COMPOSE FILE FUNDAMENTALS

Teach the basic structure of a Compose file.

Use a realistic example.

Explain:

```yaml
services:
  postgres:
    image: postgres:...
    environment:
      ...
    ports:
      ...
    volumes:
      ...
```

Teach:

- `services`
- service names
- `image`
- `build`
- `ports`
- `environment`
- `volumes`
- `networks`
- `healthcheck`
- `depends_on`
- profiles
- secrets where appropriate

Do not introduce all advanced features at once.

Build the file progressively.

---

# 8. IMAGE VS BUILD

Explain the difference between:

```yaml
image:
```

and:

```yaml
build:
```

Teach when to use each.

Examples:

### Existing image

```yaml
postgres:
  image: postgres:...
```

### Build local application

```yaml
pipeline:
  build:
    context: ..
    dockerfile: docker/pipeline.Dockerfile
```

Explain:

- Registry image
- Local image build
- Build context
- Dockerfile
- Rebuild behavior
- Image reuse

Connect this briefly to Topic 01.

Do not reteach the complete Docker image curriculum.

---

# 9. CORE COMPOSE COMMANDS

Teach:

```bash
docker compose up
docker compose up -d
docker compose down
docker compose ps
docker compose logs
docker compose logs -f
docker compose exec
docker compose run
docker compose build
docker compose pull
docker compose restart
docker compose config
```

For each important command explain:

- Purpose
- Syntax
- Example
- What happens
- Common mistake
- Data-engineering use case

Show a normal workflow:

```text
Validate
↓
Build
↓
Start
↓
Check status
↓
Check health
↓
Read logs
↓
Exec into service
↓
Run integration tests
↓
Tear down
```

---

# 10. PORTS

Teach container networking and port publishing.

Explain:

```yaml
ports:
  - "5432:5432"
```

Clearly explain:

```text
HOST_PORT:CONTAINER_PORT
```

Explain the difference between:

### Container-to-container communication

```text
postgres:5432
```

and:

### Host-to-container communication

```text
localhost:5432
```

Emphasize:

> Inside a Compose network, services should normally communicate using service names rather than `localhost`.

Show examples.

---

# 11. NETWORKS

Teach:

- Compose default network
- Custom networks
- Service discovery
- DNS
- Service names as hostnames
- Network isolation

Example:

```yaml
services:
  pipeline:
    ...
  postgres:
    ...
```

Explain that the pipeline can connect to:

```text
postgres:5432
```

rather than:

```text
localhost:5432
```

Explain why this is a frequent beginner mistake.

---

# 12. VOLUMES

Teach:

### Named volumes

```yaml
volumes:
  postgres_data:
```

### Bind mounts

```yaml
volumes:
  - ./src:/app/src
```

Explain:

- Persistence
- Container lifecycle
- Host filesystem
- Development workflow
- Data durability
- File permissions
- Performance considerations

Compare:

| Feature | Named Volume | Bind Mount |
|---|---|---|
| Managed by Docker | | |
| Host path controlled directly | | |
| Good for DB persistence | | |
| Good for live source code | | |
| Portability | | |

Explain why PostgreSQL data normally belongs in a named volume while source code may use a bind mount during development.

---

# 13. ENVIRONMENT VARIABLES

Teach:

- Environment variables
- `.env`
- variable substitution
- Compose interpolation
- runtime configuration
- environment-specific values

Example:

```yaml
environment:
  POSTGRES_DB: ${POSTGRES_DB}
  POSTGRES_USER: ${POSTGRES_USER}
```

Explain:

```text
Compose configuration
        ↓
environment variables
        ↓
container runtime
```

Explain what belongs in environment variables and what does not.

Do not turn this into the full cloud secrets-management topic.

---

# 14. ENVIRONMENT FILES

Teach:

- `.env`
- environment-specific files where appropriate
- variable substitution
- avoiding committed credentials
- local-development configuration

Explain the distinction between:

```text
configuration
```

and:

```text
secret
```

Explain why blindly committing `.env` files can be dangerous.

---

# 15. HEALTH CHECKS

This is one of the most important Compose concepts.

Explain the difference between:

```text
container started
```

and:

```text
service ready
```

Use PostgreSQL as the example.

Teach:

```yaml
healthcheck:
  test:
    ...
  interval: ...
  timeout: ...
  retries: ...
  start_period: ...
```

Explain:

- command
- interval
- timeout
- retries
- start period
- exit code
- healthy
- unhealthy

Explain why:

```bash
sleep 10
```

is a poor replacement for a health check.

---

# 16. depends_on

Teach:

```yaml
depends_on:
```

Explain the difference between:

```text
dependency exists
```

and:

```text
dependency is ready
```

Show how health conditions can be used where supported by the Compose specification.

Example:

```yaml
depends_on:
  postgres:
    condition: service_healthy
```

Explain what this does and what it does **not** guarantee.

Do not incorrectly claim that `depends_on` guarantees application-level correctness.

---

# 17. ONE-SHOT SETUP SERVICES

This is a major roadmap requirement.

Teach how to create services whose purpose is initialization.

Examples:

```text
MinIO bucket initialization
Kafka topic creation
PostgreSQL schema initialization
Seed data
```

Explain the pattern:

```text
Infrastructure services
        ↓
Setup service
        ↓
Validation
        ↓
Application/pipeline
```

Show a realistic Compose example.

---

# 18. IDEMPOTENT INITIALIZATION

Explain what idempotency means.

A setup service should be safe to run repeatedly.

Bad:

```text
CREATE TABLE users ...
```

if the second execution fails.

Better:

```text
CREATE TABLE IF NOT EXISTS ...
```

Similarly for:

- Kafka topics
- MinIO buckets
- database schemas
- seed data

Explain:

> Running `docker compose up` twice should not corrupt or duplicate the local platform.

Provide examples.

---

# 19. COMPLETE LOCAL DATA STACK

Build progressively toward the roadmap's required stack:

```text
PostgreSQL
MinIO
Kafka
Schema Registry
Airflow
Pipeline container
```

Do not simply dump a giant Compose file.

Build it service by service.

For each service explain:

- Purpose
- Image
- Ports
- Environment
- Volumes
- Network
- Health
- Dependencies
- Initialization requirements

---

# 20. POSTGRESQL SERVICE

Create a production-like local development configuration.

Cover:

- Database
- User
- Password placeholder
- Persistent volume
- Port
- Health check

Show how another service connects using:

```text
postgres:<port>
```

rather than localhost.

Explain local-development limitations.

---

# 21. MINIO SERVICE

Use MinIO as the local S3-compatible object-storage component.

Teach:

- Server container
- Console where appropriate
- Persistent volume
- Credentials through configuration
- Bucket initialization
- Health check

Explain why MinIO is useful for local data-platform development.

Do not turn this into a complete object-storage lesson from Module 2.17.

---

# 22. KAFKA SERVICE

The roadmap specifically requires Kafka KRaft in the Compose stack.

Explain at the level necessary to operate it locally:

- Kafka service
- KRaft concept
- Listener configuration
- Broker connectivity
- Internal vs external access
- Persistent storage where appropriate
- Health/readiness
- Topic initialization

Do not turn this into the complete Kafka/streaming curriculum from Module 2.16.

Focus on:

> How to run Kafka correctly as part of a local Compose data stack.

---

# 23. SCHEMA REGISTRY

Explain why a schema registry is useful in the local data stack.

Teach:

- Service dependency
- Kafka connection
- Port
- Health/readiness
- Network configuration
- Configuration through environment variables

Again, stay within Compose scope.

---

# 24. AIRFLOW

Use Airflow as the orchestrator component of the local stack.

Explain:

- Airflow service components at a high level
- Database dependency
- Initialization
- Health checks
- Volumes
- Configuration
- Profiles

Do not reteach Airflow itself.

Focus on:

> How Compose coordinates an orchestrator and its dependencies locally.

---

# 25. PIPELINE SERVICE

Add the Python pipeline image from Topic 01.

Explain:

```yaml
pipeline:
  build:
    ...
```

or:

```yaml
pipeline:
  image:
    ...
```

Explain:

- Runtime configuration
- Dependency on infrastructure
- Networking
- Batch execution
- Logs
- Exit codes

Show how a daily batch pipeline can run against the local stack.

---

# 26. PROFILES

Teach Compose profiles thoroughly.

Example:

```yaml
profiles:
  - streaming
```

and:

```yaml
profiles:
  - airflow
```

Use practical profiles:

```text
core
streaming
spark
airflow
```

Explain why profiles matter.

For example:

### Core

```text
PostgreSQL
MinIO
```

### Streaming

```text
Kafka
Schema Registry
```

### Airflow

```text
Airflow
```

### Spark

```text
Spark-related services
```

Explain how profiles reduce laptop resource usage.

Show commands for activating specific profiles.

---

# 27. OVERRIDE FILES

Teach Compose override files.

Explain:

```text
base configuration
        +
local/CI override
```

Use examples such as:

```text
compose.yaml
compose.ci.yaml
```

Explain how CI can use:

- Smaller resources
- Temporary volumes
- Different environment configuration
- Test-specific services

Explain the principle:

> Same logical stack, different execution context.

---

# 28. RESOURCE LIMITS

Teach local resource constraints.

Explain:

- CPU
- Memory
- Resource limits
- Why laptops need limits
- Why unrestricted containers can starve the host
- CI runner constraints

Use realistic examples.

Do not claim that all Compose resource behavior is identical across Docker Desktop, Linux Docker Engine, and all Compose implementations; clearly note platform differences when relevant.

---

# 29. DEVELOPMENT WORKFLOWS

Teach two major workflows.

### Workflow A — Bind mounts / live reload

```text
Host source
   ↓
Bind mount
   ↓
Container
```

### Workflow B — Rebuild image

```text
Source
 ↓
Docker build
 ↓
New image
 ↓
Container
```

Compare:

| Characteristic | Bind Mount | Rebuild |
|---|---|---|
| Feedback speed | | |
| Reproducibility | | |
| Production similarity | | |
| Dependency changes | | |
| Best use | | |

Explain when each is appropriate.

---

# 30. COMPOSE IN CI

Teach the roadmap's required CI integration pattern.

Explain:

```text
CI runner
   ↓
docker compose up
   ↓
Wait for health
   ↓
Run integration tests
   ↓
Collect logs if failure
   ↓
docker compose down
```

Teach:

- CI-specific Compose override
- Smaller resources
- Ephemeral state
- Health checks
- Test execution
- Cleanup
- Failure diagnostics

Do not teach complete GitHub Actions architecture; that belongs to Topic 05.

The focus is:

> Using Compose as an integration-test environment.

---

# 31. CONTAINERIZED TEST FIXTURES

Explain why data-engineering integration tests need real dependencies.

Examples:

```text
PostgreSQL fixture
MinIO fixture
Kafka fixture
```

Show how Compose can provide those dependencies.

Explain the difference between:

```text
unit test
```

and:

```text
integration test
```

and why Compose is useful for the latter.

---

# 32. COMPOSE SECRETS

Teach the roadmap's Compose-level secrets concepts.

Explain:

- Secrets vs environment variables
- Secret files
- Why environment variables can be exposed
- Local development secret handling
- Avoiding committed credentials

Keep this scoped to Compose.

Do not fully teach:

- AWS Secrets Manager
- Google Secret Manager
- Azure Key Vault
- Vault
- secret rotation architecture

Those belong to Topic 07.

---

# 33. DEBUGGING

Create a dedicated troubleshooting section.

Include realistic scenarios.

### Scenario 1 — Application cannot connect to PostgreSQL

Investigate:

- localhost mistake
- service name
- network
- port
- health

### Scenario 2 — PostgreSQL container starts but pipeline fails immediately

Investigate:

- readiness
- health check
- dependency condition

### Scenario 3 — Kafka client cannot connect

Investigate:

- listeners
- advertised addresses
- internal vs external access
- service name
- port

### Scenario 4 — Data disappears after `docker compose down`

Investigate:

- named volume
- bind mount
- anonymous volume
- intentional teardown behavior

### Scenario 5 — Compose stack consumes all laptop memory

Investigate:

- unnecessary services
- profiles
- resource limits
- Spark/Airflow overhead

### Scenario 6 — Setup service fails on second execution

Investigate:

- lack of idempotency

### Scenario 7 — CI passes locally but fails in Compose CI

Investigate:

- environment differences
- ports
- volume behavior
- startup timing
- missing health checks

### Scenario 8 — Container-to-container connection uses localhost

Explain why it fails.

---

# 34. OBSERVABILITY AND DEBUGGING COMMANDS

Teach practical debugging:

```bash
docker compose ps
docker compose logs
docker compose logs -f
docker compose exec
docker compose config
docker inspect
docker stats
```

Explain how to inspect:

- Environment
- Networks
- Mounts
- Health
- Resource usage
- Container state

Create a systematic debugging workflow:

```text
Status
 ↓
Health
 ↓
Logs
 ↓
Network
 ↓
Configuration
 ↓
Volumes
 ↓
Resources
 ↓
Dependency readiness
```

---

# 35. COMPLETE COMPOSE LAB

Create a progressive hands-on lab.

The learner must build:

```text
compose/
├── compose.yaml
├── compose.ci.yaml
└── .env.example
```

Do not require actual creation of additional repository files outside the target Markdown document; the lab should describe what the learner would create.

The stack must eventually contain:

```text
PostgreSQL
MinIO
Kafka
Schema Registry
Airflow
Python pipeline
```

The lab must progress through:

1. One service
2. Two services
3. Networks
4. Volumes
5. Environment variables
6. Health checks
7. `depends_on`
8. Initialization services
9. Idempotent setup
10. Profiles
11. Resource limits
12. Override file
13. CI configuration
14. Integration test workflow
15. Secrets

---

# 36. MEASUREMENT

The roadmap explicitly requires measurement.

Have the learner measure:

- Stack startup time
- Time until services are healthy
- Memory consumption
- CPU consumption
- Integration-test duration
- Time to tear down
- Time to recreate from a clean clone

Provide a table:

| Configuration | Startup Time | Memory | CPU | Test Time |
|---|---:|---:|---:|---:|
| Core | | | | |
| Full stack | | | | |
| CI configuration | | | | |

Do not invent numbers.

Explain how to collect them.

---

# 37. PRODUCTION BOUNDARY

This section is extremely important.

Explain clearly:

> Docker Compose is excellent for local development, reproducible integration environments, and CI fixtures, but it is not a production orchestration platform for large distributed data workloads.

Explain the roadmap's limitations:

- Single host
- No production-grade self-healing
- Limited scaling
- Limited scheduling
- No cluster-level orchestration

Then explain at a high level why production may use:

- Kubernetes
- Managed services
- Serverless platforms

Do not teach Kubernetes in detail here.

That belongs to:

`03-kubernetes-concepts-for-data-workloads.md`

---

# 38. ARCHITECTURE DIAGRAMS

Use Mermaid diagrams where they improve understanding.

At minimum include diagrams for:

### Local stack

```text
Developer
   ↓
Docker Compose
   ↓
+-----------------------------+
| PostgreSQL                  |
| MinIO                       |
| Kafka                       |
| Schema Registry             |
| Airflow                     |
| Pipeline                    |
+-----------------------------+
```

### Networking

```text
Pipeline
   ↓
Compose Network
   ├── PostgreSQL
   ├── MinIO
   ├── Kafka
   └── Schema Registry
```

### CI integration

```text
Pull Request
    ↓
CI
    ↓
Compose Stack
    ↓
Health Checks
    ↓
Integration Tests
    ↓
Teardown
```

### Initialization

```text
Infrastructure
      ↓
Setup Services
      ↓
Health
      ↓
Pipeline
```

Use diagrams only where they improve comprehension.

---

# 39. CONCEPTUAL EXERCISES

Include exercises covering:

1. What problem does Compose solve?
2. Service vs container.
3. Image vs build.
4. Container-to-container networking.
5. `localhost` mistake.
6. Named volume vs bind mount.
7. Health check vs startup.
8. `depends_on`.
9. Initialization service.
10. Idempotency.
11. Profiles.
12. Override files.
13. Resource limits.
14. Compose in CI.
15. Compose secrets.
16. Why Compose is not Kubernetes.

Provide solutions immediately after each exercise.

---

# 40. CODING EXERCISES

Include practical exercises with solutions.

### Exercise 1

Create a PostgreSQL service.

### Exercise 2

Add a Python pipeline service.

### Exercise 3

Connect Python to PostgreSQL using the service hostname.

### Exercise 4

Add a health check.

### Exercise 5

Add dependency readiness.

### Exercise 6

Add MinIO.

### Exercise 7

Add an idempotent bucket initialization service.

### Exercise 8

Add Kafka and topic initialization.

### Exercise 9

Add profiles.

### Exercise 10

Create a CI override.

### Exercise 11

Run integration tests.

### Exercise 12

Add resource limits.

### Exercise 13

Add Compose secrets.

Each exercise should include:

- Objective
- Starting point
- Code
- Explanation
- Expected behavior
- Common mistake
- Validation

---

# 41. PRODUCTION INCIDENT SIMULATIONS

Include realistic incident scenarios.

### Incident 1 — Morning pipeline failure

PostgreSQL starts slowly and Airflow launches before it is ready.

Learner must diagnose and fix readiness handling.

### Incident 2 — Developer laptop becomes unusable

Full Compose stack consumes excessive memory.

Learner must use profiles and resource constraints.

### Incident 3 — CI integration tests are flaky

Tests begin before dependencies are ready.

Learner must introduce health checks and readiness handling.

### Incident 4 — Local data unexpectedly disappears

Learner must diagnose volume configuration.

### Incident 5 — Kafka works from host but not from another container

Learner must diagnose listener/address configuration.

### Incident 6 — Setup service corrupts state when run twice

Learner must implement idempotency.

---

# 42. KNOWLEDGE CHECKPOINTS

After every major learning section, include:

```markdown
### Knowledge Check

Before moving forward, I should be able to:

- [ ] ...
- [ ] ...
- [ ] ...
```

Make these checks practical.

Examples:

- Can I explain why service names work as hostnames?
- Can I distinguish container startup from readiness?
- Can I explain why health checks are better than fixed sleeps?
- Can I explain named volumes vs bind mounts?
- Can I design an idempotent initialization service?
- Can I create a Compose profile?
- Can I use Compose as an integration-test environment?
- Can I explain why Compose is not a production orchestrator?

---

# 43. FINAL PRACTICAL ASSESSMENT

Create a final assessment titled:

## Build a Production-Style Local Data Platform

Scenario:

> A Data Engineering team needs a reproducible local environment that mirrors the major dependencies of its platform.

The learner must design a Compose stack containing:

```text
PostgreSQL
MinIO
Kafka
Schema Registry
Airflow
Python Pipeline
```

Requirements:

- Services defined declaratively
- Correct networking
- Named volumes where persistence is required
- Environment-based configuration
- Health checks
- Dependency conditions
- Idempotent initialization
- Profiles
- CI override
- Resource limits
- Integration-test workflow
- Safe local secrets handling
- Complete teardown
- Debugging instructions

The assessment must require the learner to:

1. Design the architecture.
2. Write Compose configuration.
3. Start the stack.
4. Verify health.
5. Run the pipeline.
6. Run integration tests.
7. Intentionally break the system.
8. Diagnose the failure.
9. Recover it.
10. Tear it down.
11. Recreate it from scratch.

---

# 44. FINAL MASTERY CHECKLIST

End with:

```markdown
## Final Mastery Checklist

- [ ] I understand why Docker Compose exists.
- [ ] I understand Compose services.
- [ ] I can write a Compose file.
- [ ] I understand image vs build.
- [ ] I understand Compose networking.
- [ ] I can use service names correctly.
- [ ] I understand named volumes and bind mounts.
- [ ] I can configure environment variables.
- [ ] I can use health checks.
- [ ] I understand dependency readiness.
- [ ] I can build idempotent setup services.
- [ ] I can use Compose profiles.
- [ ] I can use override files.
- [ ] I can apply resource limits.
- [ ] I can run a complete local data stack.
- [ ] I can debug networking problems.
- [ ] I can debug readiness problems.
- [ ] I can use Compose in CI integration tests.
- [ ] I understand Compose secrets.
- [ ] I understand the limitations of Compose.
- [ ] I can explain when Kubernetes or managed services become appropriate.
```

---

# 45. SENIOR DATA ENGINEER INTERVIEW QUESTIONS

Finish with interview-level questions and answers.

Cover:

- Why Docker Compose for Data Engineering?
- Compose vs Docker CLI?
- Service vs container?
- Image vs build?
- Why use service names instead of localhost?
- Named volume vs bind mount?
- Health check vs `depends_on`?
- Why are fixed sleeps unreliable?
- How do you make initialization idempotent?
- What are Compose profiles?
- Why use override files?
- How do you run Compose in CI?
- How do you debug flaky integration tests?
- How do you control local resource usage?
- How do Compose secrets differ from environment variables?
- Why is Compose not a production orchestration platform?
- When would you choose Compose vs Kubernetes?
- How would you design a local Kafka/PostgreSQL/MinIO stack?
- How would you diagnose a service that starts but is not ready?
- How would you make a local data platform reproducible for a new engineer?

Answers must be technically accurate and concise but sufficiently detailed for Senior Data Engineer interview preparation.

---

# 46. DO NOT OVERLAP WITH FUTURE TOPICS

This file must teach Docker Compose deeply but must respect the roadmap boundaries.

Do not turn this into the complete curriculum for:

### Topic 03

Kubernetes concepts.

### Topic 04

Terraform.

### Topic 05

CI/CD implementation.

### Topic 06

Environment promotion.

### Topic 07

Cloud secrets managers.

You may explain the relationship between Compose and these topics, but detailed implementation belongs to those respective files.

---

# 47. CODE QUALITY REQUIREMENTS

All Compose YAML and command examples must be:

- syntactically valid where practical
- internally consistent
- realistic
- easy to understand
- production-aware
- aligned with the roadmap

Do not:

- hard-code real credentials
- use fake secrets as if they were production credentials
- use unexplained configuration
- use arbitrary `sleep` commands as readiness mechanisms
- use `localhost` incorrectly for container-to-container communication
- pretend Compose provides Kubernetes-level orchestration
- invent resource measurements
- present platform-specific behavior as universal

Clearly identify assumptions where Docker Desktop, Linux Docker Engine, or Compose implementation differences matter.

---

# 48. TEACH FROM SIMPLE TO ADVANCED

The final learning progression should feel like:

```text
Level 1 — What is Docker Compose?
        ↓
Level 2 — Compose file basics
        ↓
Level 3 — Multiple services
        ↓
Level 4 — Networks
        ↓
Level 5 — Volumes
        ↓
Level 6 — Environment configuration
        ↓
Level 7 — Health checks
        ↓
Level 8 — Dependencies
        ↓
Level 9 — Initialization
        ↓
Level 10 — Idempotency
        ↓
Level 11 — Profiles
        ↓
Level 12 — Override files
        ↓
Level 13 — Resource limits
        ↓
Level 14 — Development workflows
        ↓
Level 15 — CI integration testing
        ↓
Level 16 — Secrets
        ↓
Level 17 — Complete data platform
        ↓
Level 18 — Debugging
        ↓
Level 19 — Production boundaries
        ↓
Level 20 — Final assessment
```

The learner must never feel that an advanced concept appeared without the prerequisite mental model.

---

# 49. FINAL VALIDATION BEFORE WRITING

Before writing the file, internally verify:

## File scope

- [ ] Only `02-docker-compose-for-local-data-stacks.md` will be modified.
- [ ] No other file will be modified.
- [ ] No other folder will be modified.

## Roadmap coverage

- [ ] Compose files
- [ ] Services
- [ ] Images
- [ ] Builds
- [ ] Ports
- [ ] Environment variables
- [ ] Networks
- [ ] Service-name DNS
- [ ] Named volumes
- [ ] Bind mounts
- [ ] `.env`
- [ ] Variable substitution
- [ ] Health checks
- [ ] `depends_on`
- [ ] Dependency readiness
- [ ] One-shot setup services
- [ ] Bucket initialization
- [ ] Kafka topic initialization
- [ ] Database schema initialization
- [ ] Seed data
- [ ] Idempotent setup
- [ ] Profiles
- [ ] Override files
- [ ] Local vs CI configurations
- [ ] Resource limits
- [ ] Live development workflows
- [ ] Compose in CI
- [ ] Integration testing
- [ ] Containerized test fixtures
- [ ] Compose secrets
- [ ] Production limitations
- [ ] Kubernetes/managed-service boundary

## Learning quality

- [ ] Beginner-friendly
- [ ] Basic → intermediate → advanced
- [ ] Detailed explanations
- [ ] YAML examples
- [ ] Docker commands
- [ ] Data-engineering examples
- [ ] Complete local stack
- [ ] Debugging
- [ ] Failure scenarios
- [ ] Integration testing
- [ ] Measurement
- [ ] Exercises
- [ ] Solutions
- [ ] Knowledge checkpoints
- [ ] Final assessment
- [ ] Interview preparation

---

# 50. FINAL INSTRUCTION

Now create the **complete learning module** in:

`18-Containers-Infrastructure-and-CI-CD-for-Data/02-docker-compose-for-local-data-stacks.md`

Do not merely summarize the roadmap.

**Actually teach the subject.**

The learner should finish this file capable of independently:

- Designing a Compose architecture
- Writing Compose YAML
- Running multiple data services
- Connecting services correctly
- Persisting local data
- Managing configuration
- Implementing health checks
- Handling service readiness
- Creating idempotent initialization
- Using profiles
- Using Compose overrides
- Controlling resource consumption
- Running integration tests
- Using Compose in CI
- Debugging failures
- Managing local secrets safely
- Understanding Compose's production limitations

The complete learning journey must move from:

**absolute beginner → competent Docker Compose user → advanced Data Engineer capable of building and debugging realistic local data platforms.**

Use realistic examples involving:

**PostgreSQL + MinIO + Kafka + Schema Registry + Airflow + Python pipeline**

while keeping the learning scope strictly within **Docker Compose**.

Finally, verify that **NO FILE OTHER THAN**:

`18-Containers-Infrastructure-and-CI-CD-for-Data/02-docker-compose-for-local-data-stacks.md`

has been changed.