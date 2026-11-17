# Cloud Secrets Managers

> **Stage 2 — Python for Data Engineering**  
> **Module 2.18 — Containers, Infrastructure, and CI/CD for Data**  
> **Phase E — Protecting Credentials**  
> **Topic 07 — Cloud Secrets Managers**

## 1. Why Secrets Management Matters

A production data platform continuously handles credentials: database passwords, API keys, access tokens, private keys, SFTP passwords, warehouse credentials, and service identities. The engineering problem is not merely where to store a password. It is how to make sure a workload can obtain exactly the credential it needs, for only as long as it needs it, without developers copying credentials into source code, images, logs, notebooks, CI jobs, or infrastructure state.

A useful production principle is:

> **Identity authenticates the workload; authorization determines which secret it may read; the secrets manager stores and versions the secret; the application retrieves it at runtime; rotation changes the credential without unnecessarily stopping the workload.**

Secrets management therefore sits at the intersection of application design, cloud IAM, infrastructure security, CI/CD, containers, Kubernetes, orchestration, and incident response.

### The progression

```text
Secret
  ↓
Secret vs configuration
  ↓
Secrets manager
  ↓
Runtime retrieval
  ↓
Workload identity
  ↓
Caching + refresh
  ↓
Rotation + versioning
  ↓
Least privilege
  ↓
Airflow / Kubernetes / Spark / serverless
  ↓
CI/CD + OIDC
  ↓
Dynamic credentials
  ↓
KMS + SOPS
  ↓
Terraform state protection
  ↓
Secret detection
  ↓
Leak response
  ↓
Production secrets architecture
```

The goal of this chapter is not to memorize cloud-product commands. It is to develop the engineering judgment required to design and operate a secure secrets lifecycle.

---

## 2. Learning Objectives

By the end of this topic, you should be able to:

- distinguish configuration from secrets and credentials;
- identify where secrets commonly leak;
- explain why deleting a secret from Git does not revoke it;
- compare AWS Secrets Manager, AWS Parameter Store, Google Secret Manager, Azure Key Vault, and HashiCorp Vault at a conceptual level;
- retrieve secrets at runtime from Python using provider SDKs;
- use workload identity instead of bootstrap/static cloud keys;
- cache secrets safely in memory;
- refresh credentials after expiry or rotation;
- design versioned, zero-downtime credential rotation;
- apply least privilege at the secret/workload level;
- integrate secrets with Airflow, Kubernetes, managed Spark, and serverless workloads;
- secure CI/CD with OIDC federation;
- recognize when a CI secret is unavoidable and constrain it;
- understand dynamic database credentials and Vault database engines;
- understand KMS as key-management infrastructure behind encrypted secret storage;
- use SOPS appropriately for encrypted secrets in Git;
- understand Terraform's relationship with sensitive values and state;
- add pre-commit and CI secret scanning;
- understand repository push protection, image scanning, and log scanning;
- respond correctly when a credential is leaked;
- design a production secrets architecture across dev/staging/prod;
- demonstrate competence through the `secrets/` hands-on project and final assessment.

---

## 3. Prerequisites

This topic assumes the earlier Stage 2 modules provide familiarity with:

- Python;
- configuration-driven data pipelines;
- logging and redaction;
- Airflow;
- containers;
- Kubernetes concepts;
- Terraform;
- CI/CD;
- environment promotion;
- cloud storage and cloud IAM/workload identity.

You do **not** need to know a particular cloud provider's syntax before starting. Provider-specific examples are introduced after the underlying security model.

---

## 4. What Is a Secret?

A **secret** is sensitive information whose unauthorized disclosure could enable unauthorized access, impersonation, data access, infrastructure changes, or another security-impacting action.

Examples include:

| Value | Usually secret? | Why |
|---|---:|---|
| `DATABASE_HOST` | No | Usually identifies a service |
| `DATABASE_PORT` | No | Connection metadata |
| `DATABASE_NAME` | Usually no | Configuration, though context matters |
| `DATABASE_PASSWORD` | Yes | Authenticates to the database |
| API key | Yes | Grants API access |
| Access token | Yes | Represents an authenticated session/identity |
| Private key | Yes | Cryptographic authentication material |
| SFTP password | Yes | Authenticates to an external system |
| Warehouse credential | Yes | Can grant data access |

The classification is contextual. A value should be treated as sensitive when disclosure creates meaningful security risk.

### Credentials, authentication, and authorization

These terms are related but not identical:

- **Credential**: information used to prove identity or obtain access, such as a password, token, certificate, or private key.
- **Authentication**: establishing *who or what* is making a request.
- **Authorization**: determining *what that identity is allowed to do*.
- **Secret**: a broad operational category for sensitive authentication or access material.

A secrets manager addresses storage, retrieval, lifecycle, and access control for sensitive values. It does not replace IAM.

---

## 5. Secrets vs Configuration

Not every configuration value is a secret.

```text
CONFIGURATION
    DATABASE_HOST=postgres.internal
    DATABASE_PORT=5432
    DATABASE_NAME=warehouse

SECRET
    DATABASE_PASSWORD=...
    API_KEY=...
    PRIVATE_KEY=...
    ACCESS_TOKEN=...
```

### Why the distinction matters

Treating every configuration value as a secret can create unnecessary operational complexity:

- more permissions to manage;
- more secret-manager calls;
- more difficult debugging;
- more complicated local development;
- unnecessary rotation workflows.

Conversely, treating sensitive credentials as ordinary configuration makes accidental exposure much easier.

### Practical rule

Ask:

> **If an attacker learns this value, can it materially increase their ability to authenticate, impersonate, access data, or modify systems?**

If yes, treat it as sensitive.

---

## 6. What Counts as a Secret?

Common data-engineering secrets include:

- database passwords;
- API keys;
- access tokens;
- private keys;
- warehouse credentials;
- SFTP passwords;
- service credentials;
- third-party API credentials;
- certificates or certificate private keys;
- webhook signing secrets.

A secret can be a simple string or structured data.

Example structured secret:

```json
{
  "username": "pipeline_reader",
  "password": "FAKE_ONLY_REPLACE_ME",
  "host": "db.example.internal",
  "port": 5432,
  "database": "analytics"
}
```

Use fake placeholders in learning environments. Never paste real production credentials into examples, notebooks, issue trackers, or documentation.

---

## 7. Why Secrets Must Not Live in Code

Bad:

```python
DATABASE_PASSWORD = "my-production-password"
```

Also bad:

```yaml
environment:
  DATABASE_PASSWORD: my-production-password
```

Other dangerous locations include:

- Python source;
- Git repositories;
- Dockerfiles;
- Docker image layers;
- committed `.env` files;
- CI logs;
- application logs;
- Terraform outputs;
- Terraform state;
- notebooks;
- shell history;
- Kubernetes manifests;
- configuration repositories.

### Why deletion is not revocation

Suppose a password is committed:

```text
commit A → password leaked
commit B → password deleted
```

The password may still exist in:

- Git history;
- forks;
- clones;
- CI artifacts;
- caches;
- developer machines;
- logs;
- screenshots;
- backups.

Therefore:

> **Removing a secret from the latest source tree does not invalidate the credential.**

The first security action is normally to **revoke or rotate the credential**. Repository cleanup is a separate containment/remediation action.

---

## 8. Where Secrets Commonly Leak

Think in terms of the complete delivery path:

```text
Developer machine
   ↓
Source code / Git
   ↓
CI
   ↓
Container image
   ↓
Deployment configuration
   ↓
Runtime
   ↓
Logs / traces / errors
   ↓
Artifacts / state / backups
```

A secret can leak at any stage.

### High-risk examples

#### Dockerfile

```dockerfile
ENV DATABASE_PASSWORD=FAKE_PASSWORD
```

This embeds sensitive configuration into the image metadata/history.

#### Build arguments

```bash
docker build --build-arg PASSWORD=...
```

Build arguments are not a general-purpose secret store. Use BuildKit secret mechanisms when a build genuinely needs secret material.

#### Logging

```python
logger.info("Connection configuration=%s", config)
```

If `config` contains a password, the logging pipeline may now become a secret-distribution system.

#### Terraform

A value marked `sensitive` may still be stored in state. Sensitivity primarily changes display behavior; it does not magically erase the value from Terraform's data model.

#### Kubernetes

A Kubernetes `Secret` object is not synonymous with a complete enterprise secrets-management system. Base64 encoding is not encryption.

---

# 9. Secrets Management Architecture

A production secrets architecture separates five concerns:

1. **Identity** — who is requesting access?
2. **Authorization** — may that identity read this secret?
3. **Storage** — where is the secret encrypted and versioned?
4. **Delivery** — how does the workload receive it?
5. **Lifecycle** — how is it rotated, revoked, audited, and recovered?

A conceptual flow:

```text
                +----------------+
                |   Workload     |
                | Python/Airflow |
                +-------+--------+
                        |
                        | identity
                        v
                +---------------+
                | Cloud IAM /   |
                | Workload ID   |
                +-------+-------+
                        |
                        | authorized request
                        v
                +---------------+
                | Secret Manager|
                +-------+-------+
                        |
             +----------+----------+
             |          |          |
          versions    rotation    audit
             |
             v
            KMS
```

The important boundary is that the application should not need a permanent cloud administrator credential merely to retrieve its database password.

---

# 10. Cloud Secrets Managers

Cloud providers implement the same broad pattern with different APIs and integration models.

## 10.1 AWS Secrets Manager

AWS Secrets Manager is designed for sensitive values such as database credentials, API credentials, and application secrets.

Conceptually:

```text
Workload identity
      ↓
AWS IAM
      ↓
Secrets Manager
      ↓
Secret + version
```

Typical capabilities include:

- encrypted secret storage;
- versioning;
- IAM-based access;
- audit integration;
- rotation workflows;
- SDK retrieval.

Representative Python pattern:

```python
import json
import boto3

client = boto3.client("secretsmanager")

response = client.get_secret_value(
    SecretId="data-platform/prod/postgres"
)

secret = json.loads(response["SecretString"])

password = secret["password"]
```

The application should obtain AWS credentials through the environment's workload identity chain, not through a hardcoded access key.

### Production considerations

- grant `secretsmanager:GetSecretValue` only for the required secret;
- avoid wildcard access across all secrets;
- use environment-specific secret paths/names;
- monitor access;
- design rotation compatibility;
- do not log `response` or `secret`.

---

## 10.2 AWS Systems Manager Parameter Store

Parameter Store provides centralized configuration/parameter storage. It can also store sensitive values using appropriate parameter types and encryption.

Conceptually:

```text
Parameter
  ├── non-sensitive configuration
  └── sensitive parameter protected with encryption
```

A useful distinction is:

- Parameter Store is often convenient for configuration and parameters;
- Secrets Manager is specifically oriented toward secrets lifecycle capabilities.

The correct choice depends on the application's requirements rather than product branding.

---

## 10.3 Google Secret Manager

Google Secret Manager provides managed secret storage with access control, versioning, and integration with Google Cloud identity.

Representative Python pattern:

```python
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()

name = (
    "projects/PROJECT_ID/"
    "secrets/data-platform-db/"
    "versions/latest"
)

response = client.access_secret_version(request={"name": name})
secret_value = response.payload.data.decode("utf-8")
```

In production, the workload should authenticate using its Google Cloud workload identity mechanism rather than a service-account key committed to the application.

---

## 10.4 Azure Key Vault

Azure Key Vault provides managed storage and access control for secrets and cryptographic material.

Representative Python pattern:

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()

client = SecretClient(
    vault_url="https://EXAMPLE.vault.azure.net/",
    credential=credential,
)

secret = client.get_secret("data-platform-db-password")

password = secret.value
```

`DefaultAzureCredential` is useful because it supports a credential chain suitable for different environments. Production deployments should rely on an appropriate managed identity/workload identity rather than embedding long-lived client secrets.

---

## 10.5 HashiCorp Vault

HashiCorp Vault provides a general-purpose secrets platform with strong support for:

- secret engines;
- authentication methods;
- policies;
- leases;
- dynamic secrets;
- revocation;
- audit devices.

A conceptual Vault flow:

```text
Workload
   ↓
Vault authentication
   ↓
Vault policy
   ↓
Secret engine
   ↓
Static or dynamic secret
```

Vault becomes especially interesting when the requirement is not simply “store this password” but:

> “Issue this workload a short-lived database credential and revoke it when the lease expires.”

---

## 10.6 Open-source Vault forks / ecosystem awareness

Vault-style ecosystems include open-source and compatible alternatives. The engineering lesson is broader than any one product:

- authenticate workloads strongly;
- define policies explicitly;
- store sensitive material encrypted;
- issue the minimum required access;
- support versions/leases where appropriate;
- audit access;
- design rotation and revocation.

Do not select a secrets platform solely because a product is popular. Select based on identity integration, lifecycle requirements, operational model, compliance needs, cloud environment, and workload patterns.

---

## Provider Comparison

| Capability | AWS Secrets Manager | AWS Parameter Store | Google Secret Manager | Azure Key Vault | HashiCorp Vault |
|---|---|---|---|---|---|
| Secret storage | Yes | Yes | Yes | Yes | Yes |
| Versioning | Yes | Yes | Yes | Yes | Yes |
| Workload identity integration | IAM | IAM | Cloud IAM | Managed identity | Vault auth methods |
| Dynamic DB credentials | Rotation/integrations | Not primary model | Not primary model | Not primary model | Strong capability |
| Encryption/KMS integration | AWS KMS | KMS | Cloud KMS concepts | Key Vault keys | Encryption managed by Vault architecture |
| Audit integration | CloudTrail | CloudTrail | Cloud Audit Logs | Azure Monitor/Activity Logs | Vault audit devices |
| Best conceptual fit | Application secrets | Parameters/config + protected values | GCP workloads | Azure workloads | Multi-system/dynamic secrets |

This is an architectural comparison, not a product ranking.

---

# 11. Secrets Manager vs Environment Variables vs Config Files

These mechanisms solve different problems.

| Mechanism | Main purpose | Persistent plaintext risk | Good production role |
|---|---|---:|---|
| Config file | Static application configuration | Medium | Non-sensitive configuration |
| Environment variable | Runtime configuration injection | Medium | Limited, controlled runtime values |
| Secrets manager | Secret lifecycle | Lower when correctly designed | Preferred source of sensitive credentials |
| Dynamic credential | Short-lived access | Low exposure window | High-security workloads |

Environment variables are not inherently a secrets manager.

For example:

```text
Secrets Manager
      ↓
runtime retrieval
      ↓
process memory
```

is fundamentally different from:

```text
Git repository
      ↓
.env file
      ↓
container image
      ↓
process
```

The second pattern expands the number of places in which the credential exists.

---

# 12. Runtime Secret Retrieval

The preferred production flow is:

```text
Application
    |
    | authenticate using workload identity
    v
Cloud IAM
    |
    | authorize access
    v
Secrets Manager
    |
    | return secret
    v
Application
```

### Step 1 — identify the workload

The platform establishes an identity for the running workload.

Examples:

- Kubernetes service account/workload identity;
- cloud-managed service identity;
- managed compute identity;
- CI OIDC identity.

### Step 2 — authorize

IAM evaluates whether that identity can access the requested secret.

### Step 3 — retrieve

The provider SDK retrieves the current permitted version.

### Step 4 — use carefully

The application keeps the value in memory only as long as necessary and never logs it.

### Why runtime retrieval?

It avoids baking credentials into:

- Git;
- images;
- static source;
- deployment bundles.

It also makes rotation possible without rebuilding every artifact.

---

# 13. Workload Identity

**Workload identity** means the running workload receives a platform-managed identity that can be authorized to access resources.

Instead of:

```text
Python application
    ↓
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
    ↓
Secrets Manager
```

prefer:

```text
Python application
    ↓
workload identity
    ↓
IAM
    ↓
Secrets Manager
```

### Why static bootstrap keys are dangerous

A long-lived cloud access key can:

- be copied;
- leak through logs;
- be included in images;
- survive after an employee changes role;
- remain valid until manually revoked;
- have broader permissions than intended.

Workload identity reduces the need to distribute such keys.

### Provider-neutral mental model

```text
Workload
   ↓
platform proves workload identity
   ↓
IAM policy evaluates identity
   ↓
secret access granted or denied
```

The exact implementation varies by cloud and runtime.

---

# 14. Python Runtime Secret Retrieval

Do not scatter provider-specific calls through every pipeline function.

Bad:

```python
def load_customer_data():
    client = boto3.client("secretsmanager")
    secret = client.get_secret_value(SecretId="prod/db")
    # business logic mixed with credential retrieval
    ...
```

Prefer separation:

```text
SecretProvider
     ↓
AWS/GCP/Azure/Vault implementation
     ↓
Pipeline application
```

A small abstraction:

```python
from dataclasses import dataclass
from typing import Protocol


class SecretProvider(Protocol):
    def get(self, name: str) -> str:
        ...


@dataclass
class DatabaseCredentials:
    username: str
    password: str
    host: str
    port: int
    database: str
```

Provider-specific code can then be isolated:

```python
import json
import boto3


class AwsSecretProvider:
    def __init__(self, client=None):
        self.client = client or boto3.client("secretsmanager")

    def get_json(self, name: str) -> dict:
        response = self.client.get_secret_value(SecretId=name)
        return json.loads(response["SecretString"])
```

Business code receives a typed result rather than knowing the details of AWS.

### Error handling

Handle:

- authentication failure;
- authorization failure;
- secret not found;
- network timeout;
- throttling;
- malformed secret structure;
- unavailable provider.

Do not convert all failures into a generic “password incorrect” error. Diagnosis requires knowing whether identity, authorization, availability, or data shape failed.

Example:

```python
class SecretRetrievalError(RuntimeError):
    pass


def load_database_secret(provider, name: str) -> DatabaseCredentials:
    try:
        raw = provider.get_json(name)
    except Exception as exc:
        # Do not log the secret or exception payload if it may contain it.
        raise SecretRetrievalError(
            f"Unable to retrieve secret metadata for {name!r}"
        ) from exc

    required = {"username", "password", "host", "port", "database"}

    if not required.issubset(raw):
        raise SecretRetrievalError("Database secret has an invalid structure")

    return DatabaseCredentials(
        username=raw["username"],
        password=raw["password"],
        host=raw["host"],
        port=int(raw["port"]),
        database=raw["database"],
    )
```

---

# 15. Secret Caching

Calling a secrets manager before every database operation is usually a poor design.

It can introduce:

- latency;
- API cost;
- rate-limit pressure;
- dependency on the secrets service for every operation;
- unnecessary network traffic.

A common pattern is:

```text
retrieve
   ↓
cache in memory
   ↓
use
   ↓
refresh when expired/rotated
```

### Safe cache principles

- cache only in process memory unless persistent caching is explicitly justified;
- use a bounded TTL;
- refresh before credentials expire when possible;
- never log cached values;
- understand behavior with multiple workers;
- invalidate after known rotation events;
- avoid treating a stale cached credential as permanently valid.

A minimal TTL cache:

```python
import time
from dataclasses import dataclass


@dataclass
class CachedSecret:
    value: dict
    expires_at: float


class SecretCache:
    def __init__(self, provider, ttl_seconds: int = 300):
        self.provider = provider
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, CachedSecret] = {}

    def get(self, name: str) -> dict:
        now = time.monotonic()
        cached = self._cache.get(name)

        if cached and cached.expires_at > now:
            return cached.value

        value = self.provider.get_json(name)
        self._cache[name] = CachedSecret(
            value=value,
            expires_at=now + self.ttl_seconds,
        )
        return value
```

This example deliberately keeps the cache in memory.

---

# 16. Secret Refresh

Rotation creates a stale-cache problem.

Suppose:

```text
12:00 → cache password A
12:15 → secret manager changes to password B
12:20 → application still has A
```

A production application needs a refresh strategy.

Possible approaches:

1. short TTL;
2. refresh before expected expiry;
3. refresh after authentication failure;
4. explicit cache invalidation after a rotation event;
5. provider-specific version/change detection.

A robust database client can combine:

```text
normal use
   ↓
cached credential
   ↓
authentication failure
   ↓
invalidate cache
   ↓
retrieve current credential
   ↓
reconnect once
```

Avoid infinite retries. A wrong credential may be an IAM/configuration incident rather than a transient error.

---

# 17. Secret Redaction and Logging

Never do this:

```python
logger.info("Database credentials: %s", credentials)
```

Also avoid:

```python
logger.debug("Application configuration=%r", config)
```

if `config` may contain secrets.

### Safe logging

Log metadata, not the credential:

```python
logger.info(
    "Loaded database credentials for environment=%s",
    environment,
)
```

Good diagnostic fields include:

- environment;
- secret identifier;
- provider;
- version identifier;
- workload identity;
- operation result.

Do not log:

- password;
- token;
- private key;
- secret payload;
- complete authorization headers.

### Exception leakage

Be cautious with:

```python
raise RuntimeError(f"Request failed: {response.text}")
```

If the response body contains an access token or credential, the exception may enter logs.

Use explicit redaction where necessary:

```python
def redact(value: str, visible: int = 4) -> str:
    if not value:
        return value
    if len(value) <= visible:
        return "*" * len(value)
    return value[:visible] + "..." + "*" * 8
```

Redaction is a safety layer, not permission to handle secrets carelessly.

---

# 18. Secret Rotation

**Rotation** means replacing a credential with a new credential while preserving required application access.

Reasons to rotate:

- scheduled security policy;
- suspected exposure;
- employee/offboarding events;
- vendor requirements;
- credential age;
- incident response;
- compliance.

### The naive rotation problem

```text
Application uses password A
        ↓
Password changes to B
        ↓
Application still uses A
        ↓
Pipeline fails
```

The secure design must include application behavior, not just secret-manager configuration.

### Versioned secrets

A conceptual model:

```text
Secret: prod/postgres
   ├── Version A
   └── Version B ← current
```

The application should retrieve the appropriate current version and have a controlled refresh path.

Versioning also improves:

- rollback analysis;
- auditability;
- controlled rotation;
- troubleshooting.

---

# 19. Designing Applications for Zero-Downtime Rotation

Credential rotation becomes a distributed-systems problem when multiple workers hold credentials or database connection pools.

A robust pattern is:

```text
1. Prepare new credential
2. Make new credential valid
3. Publish/update secret
4. Allow workloads to refresh
5. Establish new connections
6. Drain old connections
7. Revoke old credential
8. Verify
```

Where the underlying database supports overlapping credentials, overlap is often safer than an instantaneous cutover.

### Connection pools

A connection pool may keep old credentials longer than the application cache.

Therefore consider:

- maximum connection lifetime;
- pool recycling;
- reconnect behavior;
- refresh triggers;
- transaction boundaries.

### Controlled example

```text
Credential A active
       ↓
Create credential B
       ↓
Store B as new version
       ↓
Application refreshes
       ↓
New DB connections use B
       ↓
Old connections drain
       ↓
Revoke A
```

A rotation test should verify **continued application functionality**, not merely that a secret value changed.

---

# 20. Least Privilege Per Secret

Prefer:

```text
pipeline-A → secret-A
pipeline-B → secret-B
pipeline-C → secret-C
```

over:

```text
all pipelines → all secrets
```

Least privilege should exist at multiple layers:

- workload identity;
- IAM role;
- secret-level permission;
- environment;
- read/write capability;
- human vs workload identity.

### Bad design

```text
Role: data-platform-admin
Permission: read every secret
Assigned to: every pipeline
```

One compromised pipeline can now expose unrelated credentials.

### Better design

```text
Role: pipeline-a-reader
  → Get secret-A

Role: pipeline-b-reader
  → Get secret-B
```

Humans should generally receive different permissions from workloads.

---

# 21. Delivering Secrets to Data Platforms

## 21.1 Airflow

Airflow should not contain production passwords inside DAG source.

A conceptual flow:

```text
DAG
 ↓
Airflow connection lookup
 ↓
Secrets backend
 ↓
Cloud Secrets Manager / Vault
```

Airflow's secrets backend capability allows connection and variable retrieval to be delegated to an external secret store.

Conceptual configuration:

```python
# Illustrative configuration pattern; exact provider settings vary.
secrets_backend_kwargs = {
    "connections_prefix": "airflow/connections",
    "variables_prefix": "airflow/variables",
}
```

The key architectural idea is:

> The DAG asks for a connection; the configured secrets backend resolves it.

Do not copy credentials into DAG files merely because a connection needs a password.

---

## 21.2 Kubernetes

A native Kubernetes Secret can be used as a runtime object, but:

> **Base64 encoding is not encryption.**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: example
type: Opaque
data:
  password: <BASE64_FAKE_VALUE>
```

This should not be interpreted as an automatically secure enterprise secrets architecture.

A stronger architecture is:

```text
Cloud Secrets Manager
       ↓
External secret mechanism
       ↓
Kubernetes Secret / mounted value
       ↓
Pod
```

The external system remains the authoritative secret source.

---

## 21.3 External Secrets

An External Secrets mechanism can reconcile an external secret store into Kubernetes.

Conceptually:

```text
Secret Manager
      ↓
External Secret controller
      ↓
Kubernetes Secret
      ↓
Job/Pod
```

Important questions include:

- what identity does the controller use?
- which secret can it read?
- which namespace can receive the resulting object?
- how often is it refreshed?
- what happens when the external value changes?

---

## 21.4 CSI Secret Store

A Secrets Store CSI Driver-style architecture can expose external secret material to a workload through a volume.

Conceptually:

```text
Pod
 ↓
CSI driver
 ↓
provider plugin
 ↓
Cloud secret manager
```

This can reduce the need to maintain Kubernetes Secret objects, depending on the chosen configuration and application requirements.

---

## 21.5 Managed Spark

For managed Spark, credentials should be delivered through the platform's supported secret/configuration mechanisms and workload identity.

Avoid:

```python
spark.conf.set("api.password", "REAL_SECRET")
```

or embedding credentials in:

- source code;
- notebooks;
- image layers;
- command-line arguments;
- job definitions stored in Git.

The desired architecture is:

```text
Spark workload identity
        ↓
Cloud IAM
        ↓
Secrets Manager
        ↓
Runtime credential
```

Where platform-specific secret references are available, prefer them over plaintext configuration.

---

## 21.6 Serverless Functions

Serverless functions should retrieve sensitive configuration through the platform's supported secret integration or SDK at runtime.

The function identity should have permission to read only the required secret.

```text
Function identity
       ↓
IAM
       ↓
Secret Manager
       ↓
Secret
```

Avoid placing production credentials in deployment source or packaging artifacts.

---

# 22. Secrets in CI/CD

The strongest CI/CD design often contains **no long-lived cloud credential at all**.

Prefer:

```text
GitHub Actions
      |
      | OIDC token
      v
Cloud IAM
      |
      v
Temporary role/session
      |
      v
Cloud resources / Secrets Manager
```

Instead of:

```text
GitHub Actions
      |
      v
LONG_LIVED_ACCESS_KEY
      |
      v
Cloud
```

### Why OIDC is better

OIDC federation can provide:

- short-lived identity;
- repository/branch/environment conditions;
- no stored cloud access key;
- centralized cloud IAM;
- smaller blast radius.

The trust relationship should constrain which CI identities may assume which cloud roles.

---

# 23. OIDC Federation

OIDC stands for **OpenID Connect**. In this context, CI obtains a signed identity token from the CI platform. The cloud provider validates the token and exchanges it for temporary credentials according to a configured trust policy.

Conceptually:

```text
GitHub Actions job
       |
       | OIDC token
       v
Cloud identity provider
       |
       | trust policy
       v
Temporary cloud role/session
       |
       v
Secret Manager / cloud APIs
```

A trust policy should constrain claims such as:

- repository;
- organization;
- branch;
- tag;
- environment;
- workflow identity.

Do not create an OIDC role that any repository can assume.

---

# 24. When CI Secrets Are Unavoidable

Sometimes an external system requires a credential that cannot yet be replaced by federation.

If so:

- scope it to one environment;
- grant minimum permissions;
- minimize lifetime;
- rotate it;
- restrict who can access it;
- use protected environments;
- never print it;
- avoid putting it into build artifacts;
- document its owner and rotation schedule.

Example:

```text
CI secret
  ↓
Production deployment environment only
  ↓
One external vendor API
  ↓
Minimum required API permission
```

The objective is not “never use a secret in CI.” It is:

> **Eliminate long-lived cloud credentials where federation can provide identity, and tightly constrain any remaining secrets.**

---

# 25. Dynamic Secrets

A static credential has a long validity period:

```text
Password A
─────────────── long lifetime ───────────────
```

A dynamic credential is generated for a specific workload or job:

```text
Job starts
   ↓
Request temporary DB credentials
   ↓
Use credentials
   ↓
Job ends
   ↓
Credentials expire/revoke
```

Dynamic credentials reduce blast radius because a leaked credential has a shorter useful lifetime.

They are especially valuable for:

- CI jobs;
- batch data pipelines;
- temporary administrative operations;
- short-lived ETL jobs.

---

# 26. Vault Database Engines

Vault database secret engines can generate database credentials dynamically.

Conceptually:

```text
Pipeline Job
    ↓
Vault authentication
    ↓
Database secrets engine
    ↓
CREATE/GRANT temporary DB user
    ↓
Lease + TTL
    ↓
Pipeline
    ↓
Lease expires / revoke
```

Important concepts:

- **lease** — period for which issued credentials remain valid;
- **TTL** — time-to-live;
- **revocation** — invalidating credentials before normal expiry;
- **credential generation** — Vault can execute configured database operations to create access.

An illustrative command flow might look like:

```bash
# Illustrative only: requires a real Vault environment.
vault read database/creds/etl-reader
```

The returned credential should be treated as sensitive. Never paste it into logs or source control.

Dynamic credentials shift the security question from:

> “Where do we securely store this permanent password?”

toward:

> “Who may request a temporary credential, and for how long?”

---

# 27. KMS and Encryption

A **secret** and an **encryption key** are different concepts.

```text
Secret
  = sensitive application credential/data

KMS key
  = cryptographic key-management capability
```

Conceptually:

```text
Application
    ↓
Secrets Manager
    ↓
KMS
    ↓
Encrypted secret storage
```

### Encryption at rest

The secret store encrypts stored secret material. KMS or an equivalent key-management service can provide key management, access control, auditing, and rotation capabilities.

### Key rotation

Key rotation changes the cryptographic protection strategy; it is not the same operation as rotating a database password.

Do not confuse:

```text
Rotate database password
```

with:

```text
Rotate encryption key
```

They protect different layers.

### Separation of duties

A mature design separates:

- workload access to secrets;
- permission to administer secret metadata;
- permission to administer encryption keys;
- human administrative access.

---

# 28. SOPS and Encrypted Secrets in Git

SOPS is useful when a team has a legitimate need to keep **encrypted** secret material in a Git repository.

The important distinction is:

```text
plaintext secret in Git
        ≠
encrypted secret in Git
```

A conceptual workflow:

```text
Developer
   ↓
SOPS encrypt
   ↓
Encrypted file in Git
   ↓
CI / authorized developer
   ↓
KMS/key access
   ↓
Decrypt at controlled runtime
```

SOPS can integrate with cloud KMS systems.

### When this can be appropriate

- declarative configuration workflows;
- environments where encrypted configuration must travel with code;
- GitOps patterns with strong key access controls.

### What it does not solve

Encryption in Git does not eliminate:

- key-management requirements;
- access-control requirements;
- audit requirements;
- decryption-time exposure;
- accidental plaintext copies.

The encryption key must be protected at least as seriously as the encrypted data.

---

# 29. Terraform and Secrets

Terraform is powerful but has a critical security property:

> **Sensitive does not mean absent from state.**

For example:

```hcl
variable "database_password" {
  type      = string
  sensitive = true
}
```

The value can still become part of Terraform's state if a resource uses it.

### Common exposure paths

Secrets may appear in:

- state;
- outputs;
- plan representations;
- provider arguments;
- logs;
- generated configuration;
- resource metadata.

### Safer pattern

Prefer Terraform to provision the **secret infrastructure and access policy**, while the actual secret value is supplied through an appropriate secret-management workflow.

For example:

```hcl
resource "aws_secretsmanager_secret" "database" {
  name = "data-platform/prod/postgres"
}
```

The infrastructure code can manage:

- secret existence;
- tags;
- policies;
- rotation configuration;
- KMS association.

Avoid using Terraform as a general plaintext secret vault.

---

# 30. Protecting Terraform State

Connect this directly to the Terraform module.

State should be:

- stored in a secure remote backend;
- encrypted at rest;
- protected by strict IAM;
- locked where supported;
- excluded from Git;
- backed up appropriately;
- accessible only to required operators/workflows.

Bad:

```text
terraform.tfstate
    ↓
Git repository
```

Better:

```text
Terraform
   ↓
secure remote state backend
   ├── encryption
   ├── access control
   └── locking
```

Remember that a secure backend reduces risk but does not make state harmless. If the state contains a secret, anyone who can read that state may potentially obtain it.

---

# 31. Avoiding Secrets in Terraform Outputs and Plans

Avoid:

```hcl
output "database_password" {
  value     = var.database_password
  sensitive = true
}
```

Marking an output sensitive can suppress ordinary CLI display, but it does not eliminate the underlying value from state.

Prefer exposing non-sensitive metadata:

```hcl
output "secret_arn" {
  value = aws_secretsmanager_secret.database.arn
}
```

The application can then retrieve the actual credential at runtime.

### Plan safety

Review plans for:

- unexpected credential changes;
- secret values;
- generated connection strings;
- provider arguments containing credentials.

Use appropriate Terraform workflows and protected CI logs. Never assume that `sensitive = true` means “safe to publish the plan.”

---

# 32. Secret Detection

Secrets security has three layers:

```text
Prevention
    ↓
Detection
    ↓
Response
```

A layered model:

```text
Developer machine
      ↓
pre-commit scan
      ↓
Git push protection
      ↓
CI scan
      ↓
image scan
      ↓
runtime/log monitoring
      ↓
incident response
```

No single scanner is sufficient.

---

# 33. Pre-commit Secret Scanning

A pre-commit scanner catches many mistakes before they reach the remote repository.

One option is `gitleaks`.

Illustrative local scan:

```bash
gitleaks detect --source . --no-banner
```

A pre-commit configuration can call a scanner:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.24.2
    hooks:
      - id: gitleaks
```

Use a version appropriate to the tool version approved by your project.

### Fake-secret exercise

Create a test file containing an intentionally fake credential:

```text
FAKE_API_KEY=FAKE_ONLY_DO_NOT_USE_123456789
```

Run the scanner and observe:

```text
secret detected
→ commit blocked
→ remove test credential
→ re-run
→ commit allowed
```

Do not test secret scanners with actual production credentials.

---

# 34. CI Secret Scanning

Pre-commit is a developer-side control. CI provides an independent enforcement layer.

A conceptual GitHub Actions job:

```yaml
name: secret-scan

on:
  pull_request:
  push:

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    permissions:
      contents: read

    steps:
      - uses: actions/checkout@v4

      - name: Run gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

For production repositories, pin third-party actions according to your organization's supply-chain policy, ideally to immutable commit SHAs.

The scanner should block the pipeline when a credential-like value is detected, with documented procedures for false positives.

---

# 35. Repository Push Protection

Repository hosting platforms can detect likely secrets during pushes and block them before they become part of the remote repository.

This is useful because:

```text
developer mistake
      ↓
push protection
      ↓
push blocked
      ↓
credential never reaches central repository
```

Treat push protection as another barrier, not a replacement for pre-commit or CI scanning.

---

# 36. Scanning Images and Logs

Secrets can leak after source control.

### Image scanning

Inspect:

- image layers;
- environment metadata;
- packaged files;
- build artifacts.

Do not assume deleting a secret from the final Dockerfile line removes it from an earlier layer.

### Log scanning

Inspect:

- application logs;
- CI logs;
- orchestration logs;
- HTTP request logs;
- exception traces;
- debug output.

A logging pipeline can accidentally become a high-value secret archive.

---

# 37. Leaked Secret Incident Response

Treat a leaked credential as a security incident.

Required sequence:

```text
1. Revoke / rotate immediately
2. Audit access logs
3. Determine whether the secret was used
4. Remove secret from history where appropriate
5. Replace affected credentials
6. Verify systems
7. Document the incident
8. Write a post-mortem
```

### What not to do

Do not merely:

```text
delete commit
```

Correct response:

```text
REVOKE
+
ROTATE
+
AUDIT
+
CLEAN HISTORY WHERE APPROPRIATE
+
VERIFY
+
DOCUMENT
```

### Evidence to collect

Depending on the system:

- secret identifier;
- credential version;
- exposure time;
- repository commit/PR;
- CI job logs;
- cloud access logs;
- database authentication logs;
- API access records;
- source of disclosure;
- identities that accessed the credential;
- affected resources.

Never preserve the leaked secret in an incident report merely for evidence. Record identifiers and relevant metadata instead.

---

# 38. Secret Rotation/Revoke Drill

Scenario:

> A developer accidentally commits a fake production-style API key to a test branch. The key is assumed compromised.

Your procedure:

### 1. Detect

Identify:

- repository;
- commit;
- branch;
- secret type;
- affected environment.

### 2. Revoke or rotate

Invalidate the credential immediately.

### 3. Audit

Check whether the credential was used during the exposure window.

### 4. Clean history where appropriate

Remove the plaintext credential from accessible history according to the organization's repository-remediation procedure.

### 5. Replace

Issue a new credential and update the authoritative secret manager.

### 6. Verify

Run the affected application and confirm:

- new credential works;
- old credential fails;
- no logs expose the new credential.

### 7. Document

Record:

- timeline;
- detection mechanism;
- containment;
- root cause;
- remediation;
- prevention improvements.

---

# 39. Production Secrets Architecture

Bring the concepts together:

```text
Developer
   |
   +--> pre-commit secret scanning
   |
   v
Git
   |
   v
CI/CD
   |
   +--> OIDC
   |
   v
Cloud IAM
   |
   v
Secrets Manager
   |
   +--> KMS
   +--> Secret versions
   +--> Rotation
   +--> Audit logs
   +--> Least-privilege access
   |
   +-----------------------------+
   |             |               |
   v             v               v
Airflow       Kubernetes        Spark
   |             |               |
   +-------------+---------------+
                 |
                 v
             Data Platform
```

### Component responsibilities

| Component | Responsibility |
|---|---|
| Developer tooling | Prevent accidental commits |
| Git | Version code, not plaintext secrets |
| CI/CD | Validate changes and use federated identity |
| OIDC | Establish short-lived CI identity |
| IAM | Authorize workload actions |
| Secrets manager | Store/version/serve secrets |
| KMS | Protect encryption keys |
| Rotation | Replace credentials |
| Airflow | Resolve connections through a secrets backend |
| Kubernetes | Run workloads and integrate external secret delivery |
| Spark | Obtain runtime credentials without embedding them |
| Audit logs | Provide evidence of access |
| Incident response | Contain and recover from exposure |

---

# 40. Hands-on Project — `secrets/`

Create this project structure:

```text
secrets/
├── README.md
├── inventory.md
├── python/
│   ├── secret_provider.py
│   ├── cached_provider.py
│   └── pipeline.py
├── airflow/
│   └── secrets-backend-notes.md
├── kubernetes/
│   └── external-secret-example.yaml
├── ci/
│   ├── secret-scan.yml
│   └── oidc-notes.md
├── terraform/
│   ├── secret-infrastructure.tf
│   └── state-security.md
├── scanning/
│   └── .gitleaks.toml
└── incident/
    ├── drill.md
    └── postmortem.md
```

All values must be fake.

## Exercise 1 — Secrets Inventory

Create:

| Secret | Owner | Environment | Storage | Readers | Rotation |
|---|---|---|---|---|---|
| Database credential | Data Platform | Dev | Secrets Manager | Pipeline A | 30 days |
| API credential | Ingestion | Prod | Secrets Manager | Pipeline B | 60 days |
| SFTP credential | Ingestion | Prod | Secrets Manager | Pipeline C | 30 days |

Add:

- secret identifier;
- business purpose;
- owner;
- environment;
- authorized workloads;
- rotation policy;
- incident contact.

The inventory provides accountability.

---

## Exercise 2 — Store Platform Credentials

Create fake secrets for:

- database;
- API;
- SFTP.

Use:

```text
one secret per system
+
one secret per environment
```

Example naming model:

```text
data-platform/dev/postgres
data-platform/staging/postgres
data-platform/prod/postgres
```

This makes authorization and environment isolation easier to reason about.

---

## Exercise 3 — Runtime Retrieval

Refactor a Python pipeline:

```text
OLD
pipeline → .env → password

NEW
pipeline → workload identity → secrets manager → password
```

Requirements:

- provider SDK;
- structured secret;
- error handling;
- in-memory caching;
- refresh;
- redaction;
- no hardcoded cloud access keys.

---

## Exercise 4 — Airflow

Design:

```text
DAG
 ↓
Airflow connection lookup
 ↓
Secrets backend
 ↓
Secrets Manager
```

Evidence of completion:

- DAG contains no password;
- Airflow configuration identifies an external secrets backend;
- workload identity is documented;
- secret permissions are least-privilege.

---

## Exercise 5 — Kubernetes

Use an external secret mechanism:

```text
Secrets Manager
      ↓
External Secret mechanism
      ↓
Kubernetes workload
```

Explain:

- identity;
- secret selection;
- namespace boundary;
- refresh behavior;
- failure behavior.

---

## Exercise 6 — Secret Rotation

Rotate a fake PostgreSQL password.

Prove:

```text
credential A active
      ↓
credential B created
      ↓
secret version changes
      ↓
application refreshes
      ↓
new connection succeeds
      ↓
A revoked
      ↓
application continues
```

If a local environment cannot perform true provider-managed rotation, simulate the lifecycle with two fake versions and a test database.

---

## Exercise 7 — Secret Scanning

Add:

```text
pre-commit
+
CI
```

Commit a deliberately fake credential on a test branch.

Expected:

```text
scanner detects
→ commit/pipeline blocks
→ remove credential
→ scan passes
```

---

## Exercise 8 — Leaked Secret Drill

Simulate:

```text
fake credential committed
```

Perform:

```text
rotate
→ revoke
→ audit
→ clean history where appropriate
→ verify
→ post-mortem
```

Document evidence and decisions.

---

# 41. Failure Scenarios and Debugging

Secrets failures should be diagnosed systematically.

## 41.1 Authentication failure

**Symptom**

```text
Unable to authenticate to cloud provider
```

**Root cause possibilities**

- workload identity unavailable;
- wrong service account/role;
- OIDC trust mismatch;
- expired identity;
- local developer credential problem.

**Diagnosis**

Ask:

> Who is the workload?

Do not immediately change the secret's permissions. First establish the caller identity.

---

## 41.2 Authorization failure

**Symptom**

```text
AccessDenied / PermissionDenied / Forbidden
```

**Root cause**

The workload identity exists but cannot read this specific secret.

**Diagnosis**

Check:

```text
workload identity
→ IAM role
→ secret resource
→ action
→ environment
```

**Fix**

Grant only the required secret permission.

---

## 41.3 Secret not found

Check:

- secret name;
- environment;
- region;
- project;
- account;
- namespace;
- version;
- spelling.

A common failure is reading:

```text
prod/postgres
```

from a development workload when the intended value is:

```text
dev/postgres
```

---

## 41.4 Rotation failure

**Symptom**

```text
pipeline suddenly gets authentication errors
```

Check:

- secret version;
- connection pool;
- cache TTL;
- refresh logic;
- credential validity;
- old-credential revocation timing.

A successful secret-manager rotation does not prove application rotation compatibility.

---

## 41.5 Kubernetes failure

Check:

- ServiceAccount;
- workload identity;
- external-secret configuration;
- CSI configuration;
- namespace;
- controller events;
- pod events;
- pod logs.

Use:

```bash
kubectl describe pod <pod>
kubectl get events --sort-by=.lastTimestamp
```

Never print secret values while debugging.

---

## 41.6 CI failure

Check:

- OIDC trust relationship;
- repository/branch/environment claims;
- IAM role;
- GitHub environment protection;
- workflow permissions;
- secret scope.

A CI authentication failure is often an identity/trust problem, not a secret-value problem.

---

## 41.7 Cached credential becomes stale

**Symptom**

```text
database authentication fails after rotation
```

**Likely cause**

Process cache or connection pool still uses the previous credential.

**Fix**

```text
invalidate cache
→ retrieve new credential
→ recycle affected connections
```

Add controlled retry behavior rather than an unlimited retry loop.

---

## Debugging workflow

Use this sequence:

```text
1. Identify workload
2. Identify environment
3. Identify requested secret
4. Identify secret version
5. Confirm workload identity
6. Confirm IAM authorization
7. Confirm secret exists
8. Confirm network/provider availability
9. Inspect cache state
10. Inspect connection-pool state
11. Inspect audit logs
12. Rotate only when evidence supports rotation
```

This prevents random permission changes.

---

# 42. Common Mistakes

## Secret in an image

**Why it happens:** developer copies `.env` into build.

**Danger:** every image holder may access it.

**Fix:** remove credential from image; rotate it; rebuild.

**Prevention:** image scanning and secure runtime retrieval.

---

## Secret in environment files

**Why it happens:** local development convenience.

**Danger:** `.env` gets committed or copied into artifacts.

**Fix:** remove and rotate if exposed.

**Prevention:** `.gitignore`, pre-commit scanning, secret manager.

---

## Secret in Terraform outputs

**Why it happens:** output is convenient for debugging.

**Danger:** output/state may expose credential.

**Fix:** output identifiers, not secret values.

---

## Secret in logs

**Why it happens:** debugging.

**Danger:** logs are widely replicated and retained.

**Fix:** redact; rotate exposed credential.

---

## One secret shared by all environments

**Why it happens:** simpler setup.

**Danger:** development compromise can become production compromise.

**Fix:** separate environment credentials.

---

## No rotation

**Why it happens:** rotation requires application design.

**Danger:** credentials become long-lived and difficult to replace.

**Fix:** design refresh and rotation before production.

---

## Delete leaked Git commit but do not revoke

**Why it happens:** repository cleanup is mistaken for containment.

**Danger:** credential may still be valid in clones, forks, caches, or history.

**Fix:** revoke/rotate first.

---

# 43. Security Principles

### Never hardcode secrets

Runtime retrieval keeps credentials out of source.

### Never bake secrets into images

Image layers and registries are durable distribution systems.

### Never commit plaintext secrets

Git history is persistent and widely replicated.

### Use workload identity

Eliminate unnecessary bootstrap credentials.

### Use least privilege

A workload should read only what it needs.

### Use short-lived credentials where possible

Reduce the window of exploitation.

### Rotate credentials

Limit credential age and improve incident recovery.

### Cache carefully

Reduce dependency on secret-manager calls without creating stale credentials.

### Never log secrets

Logs often have broader access and longer retention than applications.

### Encrypt secrets

Protect data at rest and manage keys appropriately.

### Protect Terraform state

State can contain sensitive values even when variables are marked sensitive.

### Scan continuously

Use multiple controls across developer, Git, CI, image, and runtime layers.

### Separate environments

Prevent development access from becoming production access.

### Audit access

Security requires evidence of who accessed sensitive material.

### Have a leak-response plan

Assume mistakes will eventually happen and make recovery fast.

---

# 44. Knowledge Checkpoints

## Checkpoint 1 — Secret classification

You should be able to classify:

```text
DATABASE_HOST → configuration
DATABASE_PASSWORD → secret
API_KEY → secret
DATABASE_PORT → configuration
PRIVATE_KEY → secret
```

**Evidence:** explain the security consequence of disclosure for each value.

---

## Checkpoint 2 — Runtime retrieval

You should be able to demonstrate:

```text
workload identity
→ IAM
→ secrets manager
→ application
```

**Evidence:** Python retrieves a fake secret without a hardcoded cloud access key.

---

## Checkpoint 3 — Rotation

You should be able to rotate a fake credential while keeping the pipeline operational.

**Evidence:**

```text
new version active
+
application refresh
+
new connection succeeds
+
old credential revoked
```

---

## Checkpoint 4 — Platform delivery

You should be able to explain secure delivery to:

- Airflow;
- Kubernetes;
- Spark;
- serverless;
- CI/CD.

**Evidence:** architecture diagram plus configuration example.

---

## Checkpoint 5 — Leak response

You should be able to respond:

```text
revoke/rotate
→ audit
→ clean history where appropriate
→ replace
→ verify
→ document
```

**Evidence:** completed incident drill and post-mortem.

---

# 45. Interview Questions

## Beginner

### What is a secret?

**Weak answer:** “A password.”

**Strong answer:** A sensitive value whose disclosure can enable unauthorized authentication, access, impersonation, or control. Examples include passwords, API keys, tokens, and private keys.

**Senior consideration:** Classification is contextual and should be connected to the threat model.

### What is the difference between configuration and a secret?

**Strong answer:** Configuration describes how software should operate; a secret is sensitive information whose disclosure creates security risk. Some configuration can itself be sensitive.

### Why should secrets not be stored in Git?

**Strong answer:** Git history, forks, clones, caches, and artifacts can preserve the value even after the latest commit removes it.

### What is a secrets manager?

**Strong answer:** A system for controlled storage, retrieval, versioning, access control, auditing, and often rotation of sensitive credentials.

---

## Intermediate

### How does workload identity work?

**Strong answer:** The runtime receives a platform-managed identity, and IAM authorizes that identity to access specific resources without distributing long-lived static cloud keys.

### Why is OIDC preferable to long-lived CI credentials?

**Strong answer:** OIDC can exchange a short-lived CI identity for temporary cloud credentials, avoiding stored long-lived cloud keys and reducing blast radius.

### How would you rotate a database password?

**Strong answer:** Create a compatible new credential, make it valid, publish it through the secret manager, refresh application caches/connections, verify new connections, and revoke the old credential after the overlap window.

### How would Airflow retrieve secrets?

**Strong answer:** Configure an Airflow secrets backend so connection/variable lookups resolve against an external secret store instead of storing credentials in DAG code.

### How would Kubernetes retrieve secrets securely?

**Strong answer:** Use workload identity and an external secret mechanism or CSI integration where appropriate, with least-privilege access to the external store.

### Why is a Kubernetes Secret not automatically equivalent to a cloud secrets manager?

**Strong answer:** Kubernetes Secret objects use base64 representation by default; they do not automatically provide the full lifecycle, rotation, external identity, auditing, or key-management capabilities of a dedicated secrets system.

---

## Advanced

### How would you design zero-downtime credential rotation?

Cover:

- overlapping credentials where supported;
- versioning;
- cache refresh;
- connection-pool recycling;
- retry/reconnect;
- old-credential revocation;
- verification.

### How would you implement least privilege per pipeline?

Use separate workload identities/roles and resource-level secret permissions:

```text
pipeline-A → secret-A
pipeline-B → secret-B
```

Avoid broad “read every secret” roles.

### How would you use dynamic database credentials?

Issue credentials per workload/job with a short TTL and revoke or expire them after use.

### How should Terraform handle secrets?

Prefer Terraform to manage secret infrastructure and access policies while avoiding unnecessary plaintext secret values in configuration, outputs, and state.

### How do you prevent secrets from appearing in Terraform plans/state?

Minimize secret values passed through Terraform, use runtime secret retrieval, protect remote state, restrict state access, and review plans for sensitive material.

### How would you design enterprise-wide secret detection?

Layer:

```text
pre-commit
→ push protection
→ CI
→ image scanning
→ log monitoring
→ incident response
```

### What would you do if a production credential was committed to Git?

Immediately revoke/rotate, audit usage, contain affected systems, clean history where appropriate, issue replacement credentials, verify workloads, and document the incident.

### How would you design multi-environment secrets?

Separate credentials by environment, identity, and access policy:

```text
dev workload → dev secrets
staging workload → staging secrets
prod workload → prod secrets
```

---

# 46. Final Practical Assessment

## Scenario

A data platform contains:

- Airflow;
- Python ingestion pipelines;
- PostgreSQL;
- object storage;
- Kubernetes Jobs;
- Spark;
- GitHub Actions;
- Terraform;
- external APIs;
- SFTP integrations;
- dev/staging/prod environments.

Design a production-grade secrets architecture.

## Required deliverables

### 1. Secret inventory

Document:

- secret;
- owner;
- environment;
- source;
- consumers;
- rotation;
- classification.

### 2. Secrets manager

Select and justify the primary secrets system.

### 3. Workload identities

Define identities for:

- Airflow;
- Python jobs;
- Kubernetes Jobs;
- Spark;
- CI.

### 4. IAM permissions

Create least-privilege relationships.

### 5. Runtime retrieval

Show Python retrieval with provider SDK and workload identity.

### 6. Caching

Define:

- TTL;
- refresh;
- invalidation;
- connection behavior.

### 7. Rotation

Design a zero-downtime PostgreSQL credential rotation.

### 8. Airflow

Show secrets backend architecture.

### 9. Kubernetes

Show external secret delivery.

### 10. CI/OIDC

Show:

```text
GitHub Actions
→ OIDC
→ cloud role
→ cloud resources
```

### 11. Secret scanning

Include:

- pre-commit;
- CI;
- repository protection;
- image/log scanning.

### 12. Terraform

Show:

- secret infrastructure;
- state protection;
- no unnecessary secret outputs.

### 13. Incident response

Document:

```text
detect
→ revoke/rotate
→ audit
→ clean history
→ replace
→ verify
→ post-mortem
```

### 14. Audit strategy

Define what evidence proves:

- who accessed secrets;
- which workload accessed them;
- when access occurred;
- which version was used;
- whether suspicious use occurred.

### Assessment standard

A production-quality submission should explain **why** each design decision was made, not simply provide configuration.

---

# 47. Final Architecture Review

Use this review before declaring the topic complete.

| Area | What you should know | Production evidence |
|---|---|---|
| Secrets architecture | Source, delivery, lifecycle | End-to-end diagram |
| Identity | Workload identity | Identity mapping |
| IAM | Least privilege | Policy examples |
| Runtime retrieval | SDK-based retrieval | Working Python example |
| Caching | TTL/invalidation | Cache implementation |
| Rotation | Versioned credential lifecycle | Rotation drill |
| Airflow | Secrets backend | Configuration design |
| Kubernetes | External secret delivery | Architecture/YAML |
| Spark | Runtime credential strategy | Workload design |
| CI/CD | Secret-safe CI | Workflow |
| OIDC | Federation | Trust-flow diagram |
| Dynamic secrets | Short-lived credentials | Lease model |
| KMS | Encryption key management | Encryption architecture |
| SOPS | Encrypted Git workflow | Example |
| Terraform | Sensitive values/state | Secure pattern |
| Secret scanning | Prevention/detection | Scanner pipeline |
| Logging/redaction | No credential disclosure | Redaction examples |
| Incident response | Revoke/audit/recover | Completed drill |
| Auditability | Evidence and accountability | Audit plan |

---

# 48. Connections to Earlier Modules

This topic should build on earlier modules rather than duplicate them.

| Earlier topic | Connection |
|---|---|
| Module 2.9 — logging/redaction | Prevent secrets from entering logs and diagnostics |
| Module 2.12 — configuration-driven pipelines | Separate non-sensitive configuration from credentials |
| Module 2.13 — Airflow | Use Airflow's secrets backend instead of DAG hardcoding |
| Module 2.15 — table formats | Credential access protects the systems that store/manage table data |
| Module 2.17 — cloud IAM/workload identity | Provides the identity foundation for runtime secret retrieval |
| Module 2.20 — incident response | Extends secret leakage into operational response |
| Topic 03 — Kubernetes | Integrates Kubernetes workloads with external secret systems |
| Topic 04 — Terraform | Protects state and manages secret infrastructure safely |
| Topic 05 — CI pipelines | Uses OIDC and secret scanning |
| Topic 06 — environment promotion | Separates credentials across dev/staging/prod |

The goal is integration: secrets management should become a cross-cutting security capability of the data platform.

---

# 49. Final Mastery Checklist

Before moving on, you should be able to say **yes** to all of these:

- [ ] I can distinguish configuration from secrets.
- [ ] I can identify database passwords, API keys, private keys, and tokens as sensitive credentials.
- [ ] I understand why Git cleanup does not revoke a leaked credential.
- [ ] I can explain AWS Secrets Manager.
- [ ] I can explain AWS Parameter Store.
- [ ] I can explain Google Secret Manager.
- [ ] I can explain Azure Key Vault.
- [ ] I can explain HashiCorp Vault.
- [ ] I can retrieve a secret from Python at runtime.
- [ ] I can explain workload identity.
- [ ] I can avoid bootstrap cloud keys.
- [ ] I can cache secrets safely in memory.
- [ ] I can refresh after rotation.
- [ ] I can design zero-downtime rotation.
- [ ] I can apply least privilege per pipeline.
- [ ] I can integrate Airflow with an external secrets backend.
- [ ] I can explain Kubernetes Secret limitations.
- [ ] I can explain External Secrets and CSI secret-store approaches.
- [ ] I can explain managed Spark secret delivery.
- [ ] I can explain serverless runtime secret retrieval.
- [ ] I can secure CI/CD with OIDC.
- [ ] I know how to constrain unavoidable CI secrets.
- [ ] I understand dynamic secrets.
- [ ] I understand Vault database engines.
- [ ] I understand KMS's role.
- [ ] I understand SOPS and encrypted Git workflows.
- [ ] I understand Terraform's state sensitivity.
- [ ] I can protect Terraform state.
- [ ] I can configure pre-commit secret scanning.
- [ ] I can configure CI secret scanning.
- [ ] I understand repository push protection.
- [ ] I can reason about image and log scanning.
- [ ] I can respond to a leaked credential.
- [ ] I can run a rotation/revoke drill.
- [ ] I can design a production secrets architecture.
- [ ] I can complete the `secrets/` project.
- [ ] I can defend my design in a senior data-engineering interview.

---

## Topic Coverage Audit

| Roadmap Requirement | Covered? | Where Taught |
|---|---|---|
| Secrets vs configuration | Yes | Sections 4–5 |
| Database passwords/API keys/private keys/tokens | Yes | Sections 4–6 |
| AWS Secrets Manager | Yes | Section 10.1 |
| AWS Parameter Store | Yes | Section 10.2 |
| Google Secret Manager | Yes | Section 10.3 |
| Azure Key Vault | Yes | Section 10.4 |
| HashiCorp Vault | Yes | Section 10.5 |
| Runtime Python retrieval | Yes | Sections 12–14 |
| Workload identity | Yes | Section 13 |
| In-memory caching | Yes | Section 15 |
| Refresh on rotation | Yes | Section 16 |
| Never logging secrets | Yes | Section 17 |
| Automatic rotation | Yes | Section 18 |
| Versioned secrets | Yes | Section 18 |
| Zero-downtime rotation | Yes | Section 19 |
| Least privilege | Yes | Section 20 |
| Airflow secrets backend | Yes | Section 21.1 |
| Kubernetes external secrets | Yes | Sections 21.2–21.3 |
| CSI secret-store drivers | Yes | Section 21.4 |
| Managed Spark secrets | Yes | Section 21.5 |
| Serverless configuration | Yes | Section 21.6 |
| CI/OIDC | Yes | Sections 22–23 |
| Environment-scoped CI secrets | Yes | Section 24 |
| Dynamic secrets | Yes | Section 25 |
| Vault database engines | Yes | Section 26 |
| KMS | Yes | Section 27 |
| SOPS | Yes | Section 28 |
| Terraform secrets | Yes | Section 29 |
| Terraform state protection | Yes | Section 30 |
| Secret scanning | Yes | Sections 32–36 |
| Pre-commit scanning | Yes | Section 33 |
| CI scanning | Yes | Section 34 |
| Repository push protection | Yes | Section 35 |
| Image/log scanning | Yes | Section 36 |
| Leaked-secret response | Yes | Sections 37–38 |
| Revoke/rotate | Yes | Sections 37–38 |
| Access-log auditing | Yes | Sections 37–38 |
| Git-history cleanup | Yes | Sections 37–38 |
| Post-mortem | Yes | Sections 37–38 |
| Secrets inventory | Yes | Section 40, Exercise 1 |
| Full `secrets/` hands-on | Yes | Section 40 |
| Failure-driven learning | Yes | Sections 41–42 |
| Debugging | Yes | Section 41 |
| Security principles | Yes | Section 43 |
| Knowledge checkpoints | Yes | Section 44 |
| Interview preparation | Yes | Section 45 |
| Final practical assessment | Yes | Section 46 |
| Production architecture review | Yes | Section 47 |
| Earlier-module connections | Yes | Section 48 |
| Final mastery checklist | Yes | Section 49 |

## Completion Standard

This topic is complete when you can demonstrate, with fake credentials and a controlled environment, the entire lifecycle:

```text
classify
  ↓
store
  ↓
authenticate workload
  ↓
authorize access
  ↓
retrieve at runtime
  ↓
cache
  ↓
refresh
  ↓
rotate
  ↓
audit
  ↓
detect leakage
  ↓
revoke
  ↓
recover
  ↓
document
```

The senior-level outcome is not memorizing a particular secrets-manager API. It is being able to design a secrets lifecycle in which **credentials are difficult to leak, narrowly accessible when used, short-lived where possible, observable, rotatable, and recoverable when something goes wrong.**
