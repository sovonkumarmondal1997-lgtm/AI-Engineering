# Terraform Basics for Data Infrastructure

> **Stage 2 — Python for Data Engineering**  
> **Module 2.18 — Containers, Infrastructure, and CI/CD for Data**  
> **Phase C — Infrastructure as Code**  
> **Topic 04 — Terraform Basics for Data Infrastructure**
>
> **Audience:** Data Engineers moving from manually created cloud resources to reviewed, versioned, repeatable infrastructure.  
> **Progression:** Beginner → Fundamentals → Intermediate → Advanced → Production.

---

# 1. Module Outcome

By the end of this module, you should be able to:

- explain why Infrastructure as Code (IaC) matters for Data Engineering;
- understand Terraform's desired-state model;
- write basic HCL;
- configure providers;
- create and reference resources;
- read existing infrastructure with data sources;
- use variables, outputs, and locals;
- use the Terraform CLI safely;
- read and challenge `terraform plan`;
- understand Terraform state and why it is sensitive;
- use remote state and state locking;
- build reusable modules;
- use `count` and `for_each`;
- represent dev, staging, and production infrastructure safely;
- model data lakes, IAM, KMS, catalogs, warehouses, managed Spark, and Kafka resources conceptually;
- protect data-bearing resources with `prevent_destroy`;
- recognize forced replacement;
- use backups as a separate data-safety layer;
- import existing infrastructure;
- detect and resolve drift;
- lint Terraform with `tflint`;
- security-scan IaC with tools such as Checkov or Trivy;
- understand how Terraform fits into CI without duplicating the next CI module;
- understand Terraform's relationship with OpenTofu, Pulumi, and cloud-native templates;
- reason about Terraform as a production Data Engineering discipline.

The central idea is:

> **Terraform turns infrastructure from something engineers manually create into something teams can review, version, reproduce, protect, and continuously reconcile.**

---

# 2. Why Infrastructure as Code?

Imagine a data platform created manually:

```text
Cloud Console
   ↓
Create bucket
   ↓
Create IAM role
   ↓
Create KMS key
   ↓
Create warehouse
   ↓
Create Kafka topic
   ↓
Create managed Spark resources
```

It may work once.

The problem appears when you need:

```text
dev
staging
prod
```

or when a new engineer joins.

You now have questions:

- Which settings did we use?
- Which resources exist?
- Who changed them?
- What permissions were granted?
- Was encryption enabled?
- What lifecycle policy was configured?
- Can we reproduce production?
- What happens if somebody changes a setting manually?
- Can we review infrastructure changes before applying them?

Manual infrastructure creates an operational memory problem.

---

# 3. The Evolution to IaC

The progression is:

```text
Manual Cloud Configuration
        ↓
CLI / SDK
        ↓
Infrastructure as Code
        ↓
Reviewed Terraform Configuration
        ↓
Repeatable Environments
        ↓
Production-Safe Infrastructure Delivery
```

CLI and SDKs are still useful. They are often excellent for:

- discovery;
- debugging;
- one-off inspection;
- learning provider APIs.

But production infrastructure benefits from a declarative source of truth.

---

# 4. What Is Infrastructure as Code?

Infrastructure as Code means representing infrastructure configuration in machine-readable files that can be:

- version controlled;
- reviewed;
- validated;
- planned;
- applied;
- reproduced.

Instead of saying:

> "Create a bucket with encryption and a lifecycle policy."

you express the desired infrastructure in code.

Conceptually:

```text
Terraform Configuration
        ↓
Desired Infrastructure
```

Git then becomes the review/history layer:

```text
Engineer
   ↓
Terraform change
   ↓
Git diff
   ↓
Code review
   ↓
Plan
   ↓
Approved change
   ↓
Infrastructure
```

---

# 5. Why IaC Matters Specifically for Data Engineering

Data infrastructure is unusually sensitive because infrastructure often holds or controls:

- production datasets;
- object-storage buckets;
- warehouse schemas;
- IAM permissions;
- encryption keys;
- Kafka topics;
- catalogs;
- compute resources;
- backup/recovery infrastructure.

A mistake in application code may break a pipeline.

A mistake in infrastructure can:

- delete data;
- expose data;
- remove access;
- increase cloud costs;
- break an entire platform.

Therefore:

> Infrastructure changes deserve the same engineering discipline as application changes.

---

# 6. Benefits of Terraform

## Repeatability

The same configuration can create equivalent infrastructure in multiple environments.

## Reviewability

A reviewer can inspect:

```text
What changed?
```

before infrastructure changes.

## Version History

Git records:

```text
who
what
when
why
```

for infrastructure code changes.

## Reproducibility

A destroyed development environment can be recreated from code.

## Consistency

Teams reduce configuration differences between environments.

## Drift Detection

Terraform can identify differences between:

```text
declared configuration
```

and:

```text
real infrastructure
```

## Controlled Change

A plan provides a preview before applying.

---

# 7. Terraform Mental Model

Start with this model:

```text
Terraform Configuration
        ↓
Provider
        ↓
Resources / Data Sources
        ↓
Terraform State
        ↓
Terraform Plan
        ↓
Terraform Apply
        ↓
Real Infrastructure
```

A more precise relationship is:

```text
             Configuration
                   │
                   │ desired state
                   ▼
            Terraform Engine
              /          \
             /            \
         State          Providers
           │                │
           │                ▼
           │         Cloud/Data APIs
           │                │
           └───────┬────────┘
                   ▼
            Real Infrastructure
```

Terraform compares what you declared with what it knows about the real infrastructure and produces a proposed set of changes.

---

# 8. Desired State vs Actual State

Suppose Terraform configuration says:

```text
bucket encryption = enabled
```

but the actual cloud bucket has:

```text
encryption = disabled
```

There is a difference.

Terraform can identify the difference during planning.

Think:

```text
Desired state
      ≠
Actual infrastructure
      ↓
Potential change
```

This is one reason Terraform is useful for production platforms.

---

# 9. Configuration vs State

These are not the same thing.

## Configuration

Your `.tf` files describe:

> What infrastructure should exist.

## State

Terraform state records information Terraform uses to track managed objects.

A useful simplified mental model is:

```text
Configuration
   = desired definition

State
   = Terraform's tracking record

Cloud
   = actual infrastructure
```

Terraform uses all three concepts when planning changes.

---

# 10. HCL Fundamentals

Terraform configurations are generally written in HashiCorp Configuration Language (HCL).

A minimal structure looks like:

```hcl
terraform {
  required_version = ">= 1.6.0"
}

provider "example" {
  # provider configuration
}

resource "example_resource" "data_lake" {
  # resource arguments
}
```

The exact provider/resource names depend on the platform.

---

# 11. HCL Blocks

A block has a type and sometimes labels.

Example:

```hcl
resource "example_bucket" "raw" {
  name = "example-raw-data"
}
```

Here:

```text
resource
```

is the block type.

```text
example_bucket
```

is the resource type.

```text
raw
```

is Terraform's local name for that resource.

---

# 12. HCL Arguments

Inside the block:

```hcl
name = "example-raw-data"
```

`name` is an argument.

The value is:

```text
"example-raw-data"
```

Terraform evaluates arguments to determine the desired resource configuration.

---

# 13. HCL Data Types

Common Terraform types include:

### String

```hcl
environment = "dev"
```

### Number

```hcl
retention_days = 30
```

### Boolean

```hcl
enabled = true
```

### List

```hcl
pipelines = ["ingestion", "quality", "transformation"]
```

### Set

```hcl
regions = toset(["us-east-1", "us-west-2"])
```

### Map

```hcl
tags = {
  Environment = "dev"
  ManagedBy   = "terraform"
}
```

### Object-like values

```hcl
pipeline = {
  name    = "ingestion"
  enabled = true
}
```

---

# 14. Expressions and References

Terraform becomes powerful when values can reference other values.

Example:

```hcl
resource "example_bucket" "raw" {
  name = "data-${var.environment}-raw"
}
```

Here:

```hcl
var.environment
```

references an input variable.

Another resource may reference an attribute:

```hcl
resource "example_role_policy" "pipeline" {
  role_name = example_role.pipeline.name
}
```

Terraform can build dependencies from such references.

---

# 15. Terraform Providers

Terraform itself does not contain implementation logic for every cloud or data platform.

Providers connect Terraform to APIs.

Conceptually:

```text
Terraform
    ↓
Provider
    ↓
Provider API Client
    ↓
Cloud/Data Platform API
```

Examples of provider ecosystems include:

- AWS;
- Azure;
- Google Cloud;
- Snowflake;
- Confluent;
- Kubernetes;
- other infrastructure platforms.

The purpose of this module is not to teach every provider.

The important concept is:

> A provider gives Terraform the ability to manage a particular external system.

---

# 16. Provider Requirements

A production project should constrain provider versions appropriately.

Conceptual example:

```hcl
terraform {
  required_providers {
    example = {
      source  = "example/example"
      version = "~> 1.0"
    }
  }
}
```

Provider version constraints reduce unexpected behavior caused by uncontrolled upgrades.

After initialization, Terraform also maintains dependency information in:

```text
.terraform.lock.hcl
```

Treat the lock file as part of reproducibility.

---

# 17. Provider Authentication

Terraform providers need credentials or workload identity to communicate with external systems.

Prefer mechanisms such as:

```text
developer identity
OIDC/workload identity
cloud credential chain
environment-aware authentication
```

Avoid putting credentials directly into Terraform source.

Bad:

```hcl
provider "example" {
  access_key = "real-secret"
}
```

Better:

```text
Terraform
   ↓
approved authentication mechanism
   ↓
provider
```

Authentication and secret management become more sophisticated in Topic 07.

---

# 18. Resources

A resource represents infrastructure Terraform manages.

Conceptually:

```hcl
resource "example_bucket" "raw" {
  name = "data-dev-raw"
}
```

Terraform can:

- create it;
- update it where supported;
- replace it where required;
- destroy it.

---

# 19. Resource Identity

Terraform identifies a resource using its address.

For:

```hcl
resource "example_bucket" "raw" {
}
```

the address is:

```text
example_bucket.raw
```

This identity matters.

Changing the Terraform address through refactoring can affect how Terraform maps configuration to state.

That is why renaming resources should be treated carefully.

---

# 20. Resource Dependencies

Suppose:

```text
KMS key
   ↓
bucket encryption
   ↓
data lake
```

Terraform can infer dependencies when one resource references another.

Example:

```hcl
resource "example_kms_key" "data" {
  description = "Data lake encryption key"
}

resource "example_bucket" "raw" {
  encryption_key_id = example_kms_key.data.id
}
```

Terraform can determine:

```text
KMS key must exist before bucket encryption can reference it.
```

---

# 21. Implicit vs Explicit Dependencies

An implicit dependency comes from a reference:

```hcl
key_id = example_kms_key.data.id
```

An explicit dependency can be declared with:

```hcl
depends_on = [
  example_resource.something
]
```

Prefer implicit dependencies when the actual relationship can be represented naturally.

Use `depends_on` when Terraform cannot infer a real dependency from expressions.

Overusing explicit dependencies can make configurations harder to reason about.

---

# 22. Data Sources

A resource generally represents infrastructure Terraform manages.

A data source reads information about existing infrastructure.

Mental model:

```text
resource
= Terraform manages the object

data
= Terraform reads the object
```

Example:

```hcl
data "example_current_account" "this" {}
```

Then:

```hcl
account_id = data.example_current_account.this.id
```

---

# 23. Data Source Use Cases

Data sources are useful when:

- a VPC already exists;
- a KMS key is managed elsewhere;
- an existing subnet must be discovered;
- a cloud account ID is needed;
- a managed platform exposes an object Terraform should read.

Data sources reduce unnecessary duplication.

They should not become an excuse to hide ownership boundaries.

---

# 24. Variables

Input variables parameterize Terraform configuration.

Example:

```hcl
variable "environment" {
  type        = string
  description = "Deployment environment"
}
```

Then:

```hcl
resource "example_bucket" "raw" {
  name = "data-${var.environment}-raw"
}
```

Now the same code can represent:

```text
dev
staging
prod
```

---

# 25. Variable Types

Prefer explicit types.

```hcl
variable "retention_days" {
  type        = number
  description = "Object retention period"
  default     = 30
}
```

For a list:

```hcl
variable "pipelines" {
  type = list(string)
}
```

For a map:

```hcl
variable "tags" {
  type    = map(string)
  default = {}
}
```

Explicit typing improves validation and readability.

---

# 26. Variable Validation

Variables can have validation rules.

Example:

```hcl
variable "environment" {
  type = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}
```

This prevents invalid environment values from progressing unnecessarily far.

---

# 27. Sensitive Variables

Terraform supports:

```hcl
variable "api_token" {
  type      = string
  sensitive = true
}
```

This can reduce accidental display in normal CLI output.

However:

> `sensitive = true` does not mean the value disappears from state.

Sensitive data can still exist in state depending on the resource/provider.

Therefore state security remains essential.

---

# 28. Variable Files

Environment-specific values can be stored in variable files.

For example:

```text
dev.tfvars
staging.tfvars
prod.tfvars
```

Example:

```hcl
environment    = "dev"
retention_days = 7
```

Then:

```bash
terraform plan -var-file=dev.tfvars
```

The exact environment strategy should be designed consistently across the repository.

---

# 29. Outputs

Outputs expose useful values from a Terraform configuration.

Example:

```hcl
output "raw_bucket_name" {
  value = example_bucket.raw.name
}
```

For a module:

```hcl
output "role_arn" {
  value = example_role.pipeline.arn
}
```

Outputs can become interfaces between infrastructure components.

---

# 30. Sensitive Outputs

Outputs can be marked sensitive:

```hcl
output "endpoint" {
  value     = example_database.main.endpoint
  sensitive = true
}
```

Again:

> Sensitive output handling does not remove the need to secure Terraform state.

---

# 31. Locals

Locals define reusable computed values.

Example:

```hcl
locals {
  environment = var.environment

  common_tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }

  name_prefix = "data-${var.environment}"
}
```

Then:

```hcl
name = "${local.name_prefix}-raw"
```

---

# 32. Variables vs Locals

A useful distinction:

| Concept | Purpose |
|---|---|
| Variable | Input supplied to configuration |
| Local | Computed/reusable value inside configuration |
| Output | Value exposed to callers/users |

Think:

```text
Variable
   ↓
Configuration logic
   ↓
Local
   ↓
Resource
   ↓
Output
```

---

# 33. Terraform CLI Workflow

The standard workflow is:

```text
terraform init
        ↓
terraform fmt
        ↓
terraform validate
        ↓
terraform plan
        ↓
Review
        ↓
terraform apply
```

Destroy is a separate destructive operation:

```text
terraform destroy
```

Never treat these commands as interchangeable.

---

# 34. `terraform init`

Initialize a working directory:

```bash
terraform init
```

Initialization can:

- install providers;
- initialize the backend;
- download modules;
- prepare Terraform's working directory.

It creates local working data under:

```text
.terraform/
```

and may update:

```text
.terraform.lock.hcl
```

---

# 35. Why the Lock File Matters

The provider lock file helps ensure consistent provider selections across environments.

Without controlled provider versions, two engineers may unexpectedly use different provider versions.

That creates reproducibility problems.

A production repository should treat provider dependency changes as deliberate changes.

---

# 36. `terraform fmt`

Run:

```bash
terraform fmt
```

This standardizes Terraform formatting.

For checking rather than changing:

```bash
terraform fmt -check
```

Formatting is not merely cosmetic.

Consistent formatting makes:

- code review easier;
- diffs smaller;
- style consistent;
- automated checks predictable.

---

# 37. `terraform validate`

Run:

```bash
terraform validate
```

Validation checks whether the configuration is structurally valid.

But:

```text
validate ≠ plan
plan ≠ apply
```

`validate` can tell you:

> "This configuration is structurally valid."

It does not prove:

- credentials work;
- resources exist;
- the plan is safe;
- the provider will accept every operation;
- production data is protected.

---

# 38. `terraform plan`

Run:

```bash
terraform plan
```

The plan is one of the most important safety mechanisms in Terraform.

It answers:

> What does Terraform intend to change?

A senior engineer should read the plan rather than treating it as noise before `apply`.

---

# 39. Reading Plan Symbols

Common plan indicators include:

```text
+   create
-   destroy
~   update in place
-/+ replace
```

Conceptually:

```text
+ resource
```

means Terraform intends to create something.

```text
- resource
```

means Terraform intends to destroy it.

```text
~ resource
```

means an in-place update is expected.

```text
-/+ resource
```

means replacement is expected.

Replacement is particularly important for data infrastructure.

---

# 40. The Eight Plan Questions

Before applying a plan, ask:

1. What will be created?
2. What will be changed?
3. What will be destroyed?
4. Why is each change occurring?
5. Is any resource being replaced?
6. Is any data-bearing resource involved?
7. Is this the correct environment?
8. Is the change intentional and recoverable?

If you cannot answer these, do not apply.

---

# 41. Example Plan Review

Imagine the plan says:

```text
# example_bucket.raw must be replaced
-/+ resource "example_bucket" "raw" {
    name = "data-prod-raw"
  }
```

Do not think:

> "Terraform wants to update the bucket."

Think:

> "Terraform wants to destroy and recreate a data-bearing resource."

That is a fundamentally different risk.

---

# 42. `terraform apply`

Apply the reviewed configuration:

```bash
terraform apply
```

Terraform will calculate and execute the required changes.

A safer workflow is:

```text
plan
 ↓
review
 ↓
approval
 ↓
apply
```

For higher-control workflows, a saved plan can be reviewed and applied explicitly.

---

# 43. `terraform destroy`

Destroy:

```bash
terraform destroy
```

This is useful for disposable development infrastructure.

For example:

```text
temporary dev environment
        ↓
terraform destroy
        ↓
cloud resources removed
```

But it is dangerous for data-bearing resources.

A production environment should have multiple protection layers.

---

# 44. State: The Critical Concept

Terraform state is not simply a cache.

It is a critical part of Terraform's tracking model.

State helps Terraform understand:

- which real resource corresponds to a Terraform resource;
- resource identifiers;
- tracked attributes;
- relationships;
- information needed for planning.

Simplified:

```text
Configuration
      +
State
      +
Provider observations
      ↓
Plan
```

---

# 45. Why State Exists

Imagine Terraform configuration says:

```hcl
resource "example_bucket" "raw" {
  name = "data-dev-raw"
}
```

Terraform needs to know which real bucket corresponds to:

```text
example_bucket.raw
```

State helps maintain that mapping.

Without a reliable state model, safe lifecycle management becomes difficult.

---

# 46. State Is Sensitive

Terraform state can contain sensitive infrastructure information.

Depending on the provider/resource, it may include:

- identifiers;
- configuration;
- connection-related values;
- generated secrets;
- resource metadata.

Therefore:

```text
terraform.tfstate
```

should not be treated as ordinary source code.

---

# 47. Never Commit State to Git

Do not do:

```text
git add terraform.tfstate
```

A repository should generally ignore local state files:

```text
*.tfstate
*.tfstate.*
.terraform/
```

The exact repository policy should be established deliberately.

The important rule is:

> Terraform state belongs in an appropriately secured state backend, not in source control.

---

# 48. Remote State

Local state works for a single-person experiment.

A team needs shared state.

Conceptually:

```text
Engineer A ─┐
            │
Engineer B ─┼──> Remote State Backend
            │
CI          ─┘
```

The remote backend provides a shared state location with access controls.

Common architectural choices use object storage plus a locking mechanism, depending on the backend/provider/version.

---

# 49. Why Teams Need Remote State

Without shared state:

```text
Engineer A → state-A
Engineer B → state-B
```

Both engineers can believe they manage the same infrastructure while holding different records.

That creates:

- conflicting plans;
- stale state;
- accidental changes;
- operational confusion.

Remote state provides a shared source for Terraform's state.

---

# 50. State Locking

Two engineers should not modify the same state concurrently without coordination.

Potentially dangerous:

```text
Engineer A → terraform apply
Engineer B → terraform apply
             ↓
       concurrent operation
```

A lock helps serialize state-changing operations.

Conceptually:

```text
Terraform A
    ↓
Acquire lock
    ↓
Apply
    ↓
Release lock

Terraform B
    ↓
Wait / fail safely
```

The exact locking implementation depends on the chosen backend.

---

# 51. State Security Architecture

A production state backend should be designed around:

- least-privilege access;
- encryption at rest;
- encryption in transit;
- versioning/backups where supported;
- audit logging;
- controlled access;
- separate state per environment.

Think:

```text
Terraform
    ↓
Secure Backend
    ↓
Encrypted State
    ↓
Controlled Access
    ↓
Audit Trail
```

---

# 52. Modules

A module is a reusable Terraform building block.

Without modules:

```text
dev code
staging code
prod code
```

may drift into duplicated copies.

With modules:

```text
data_lake module
       ↓
dev
staging
prod
```

The same infrastructure design can be parameterized.

---

# 53. Root and Child Modules

A typical structure:

```text
root module
   |
   +-- data_lake child module
   |
   +-- pipeline_role child module
   |
   +-- warehouse child module
```

The root module composes reusable building blocks.

---

# 54. Module Inputs and Outputs

A module should have a clear interface.

Example:

```hcl
module "data_lake" {
  source = "../../modules/data_lake"

  environment    = var.environment
  bucket_name    = var.raw_bucket_name
  retention_days = var.retention_days
}
```

The module exposes outputs:

```hcl
output "bucket_name" {
  value = example_bucket.raw.name
}
```

The caller can consume:

```hcl
module.data_lake.bucket_name
```

---

# 55. Data Lake Module

A realistic conceptual module:

```text
modules/
└── data_lake/
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```

The module can represent:

```text
Bucket
 ├── encryption
 ├── versioning
 ├── lifecycle
 └── public-access blocking
```

The exact resources are provider-specific.

The design goal is more important:

> A data lake module should encapsulate the organization's baseline safety and lifecycle expectations.

---

# 56. Conceptual Data Lake Module

```hcl
variable "environment" {
  type = string
}

variable "bucket_name" {
  type = string
}

variable "retention_days" {
  type = number
}

resource "example_kms_key" "data" {
  description = "Encryption key for ${var.environment} data"
}

resource "example_bucket" "raw" {
  name = var.bucket_name

  encryption_key_id = example_kms_key.data.id

  versioning_enabled = true

  lifecycle_rule {
    expiration_days = var.retention_days
  }

  public_access_blocked = true
}

output "bucket_name" {
  value = example_bucket.raw.name
}
```

This is intentionally provider-shaped pseudocode where provider-specific attributes vary.

Use the current provider documentation when converting the pattern to a real cloud implementation.

---

# 57. Pipeline Role Module

A data platform should avoid one giant role for every pipeline.

Instead:

```text
ingestion_pipeline
transformation_pipeline
quality_pipeline
```

can have distinct identities.

Conceptually:

```text
pipeline_role/
├── main.tf
├── variables.tf
└── outputs.tf
```

Inputs might include:

```hcl
pipeline_name
allowed_buckets
allowed_actions
```

Outputs might include:

```text
role ARN / role ID
```

---

# 58. Least Privilege

Bad:

```text
pipeline → administrator access
```

Better:

```text
ingestion
  → read source
  → write raw bucket

transformation
  → read raw
  → write curated

quality
  → read curated
  → write quality results
```

The infrastructure module should make least privilege easy to express.

Avoid:

```text
Action = "*"
Resource = "*"
```

unless there is a clearly justified exception.

---

# 59. `count`

`count` creates multiple instances of a resource.

Example:

```hcl
variable "pipeline_count" {
  type = number
}

resource "example_pipeline" "worker" {
  count = var.pipeline_count

  name = "worker-${count.index}"
}
```

If:

```text
pipeline_count = 3
```

Terraform creates:

```text
example_pipeline.worker[0]
example_pipeline.worker[1]
example_pipeline.worker[2]
```

---

# 60. When `count` Is Useful

Use `count` when:

- instances are essentially interchangeable;
- a numeric quantity controls how many resources exist;
- index-based identity is acceptable.

Example:

```text
N identical workers
```

---

# 61. `count` Limitation

Index identity can be awkward when a list changes.

Suppose:

```text
["ingestion", "quality", "transform"]
```

is represented by indexes.

If an item is removed from the middle, Terraform may perceive changes to later indexes.

For named infrastructure, this can create confusing plans.

---

# 62. `for_each`

`for_each` creates instances from a map or set.

Example:

```hcl
variable "pipelines" {
  type = set(string)
}

resource "example_pipeline" "role" {
  for_each = var.pipelines

  name = each.key
}
```

With:

```hcl
pipelines = [
  "ingestion",
  "quality",
  "transformation"
]
```

Terraform creates named instances such as:

```text
example_pipeline.role["ingestion"]
example_pipeline.role["quality"]
example_pipeline.role["transformation"]
```

---

# 63. `count` vs `for_each`

| Situation | Prefer |
|---|---|
| N interchangeable instances | `count` |
| Named instances | `for_each` |
| Stable identity based on key | `for_each` |
| Simple quantity toggle | `count` |

For data-platform resources with meaningful names, `for_each` is often easier to reason about.

---

# 64. Resource Addressing

With `count`:

```text
resource.name[0]
```

With `for_each`:

```text
resource.name["ingestion"]
```

This matters during:

- plan review;
- imports;
- refactoring;
- state operations;
- debugging.

---

# 65. Environments

A data platform commonly has:

```text
dev
staging
prod
```

Terraform should keep environments isolated.

Isolation can include:

- state;
- cloud accounts/projects;
- buckets;
- catalogs;
- schemas;
- credentials;
- resource sizes.

---

# 66. Separate State Per Environment

Avoid one shared state file controlling everything:

```text
dev + staging + prod
```

A failure or mistaken operation in one environment should not unnecessarily endanger another.

Prefer:

```text
dev state
staging state
prod state
```

with appropriate access controls.

---

# 67. Environment Directories

One approach:

```text
infra/
├── modules/
│   ├── data_lake/
│   └── pipeline_role/
│
└── environments/
    ├── dev/
    ├── staging/
    └── prod/
```

Each environment can configure the same modules differently.

---

# 68. Workspaces

Terraform workspaces can also separate state instances.

They can be useful for certain patterns, but they are not automatically the best environment strategy.

For high-risk production data platforms, explicit environment directories and/or separate backend/state boundaries are often easier for teams to understand and secure.

The important requirement is:

> Environment state must be intentionally isolated.

---

# 69. Variable Files by Environment

Example:

```text
dev.tfvars
staging.tfvars
prod.tfvars
```

Dev might use:

```text
small compute
short retention
non-production bucket
```

Production might use:

```text
protected resources
longer retention
production bucket
higher availability
```

The code remains reusable while configuration varies.

---

# 70. Data Infrastructure as Code

Terraform can represent many layers of a data platform.

Conceptually:

```text
                 Terraform
                     |
       +-------------+-------------+
       |             |             |
    Storage         IAM           KMS
       |             |             |
       +-------------+-------------+
                     |
              Data Platform
             /      |       \
         Catalog  Warehouse  Kafka
             |
           Spark
```

The point is not to turn Terraform into a complete cloud tutorial.

The point is:

> **Understand how data-platform infrastructure becomes code.**

---

# 71. Object Storage

Terraform can manage object-storage properties such as:

- bucket;
- versioning;
- encryption;
- lifecycle;
- public-access blocking;
- policies.

Conceptual resource:

```hcl
resource "example_bucket" "raw" {
  name = "data-${var.environment}-raw"

  versioning_enabled  = true
  public_access_blocked = true
}
```

Provider-specific syntax will differ.

---

# 72. Lifecycle Rules

Lifecycle rules control data-retention behavior.

For example:

```text
raw/
  ↓
older objects
  ↓
transition/archive
  ↓
eventual expiration
```

Terraform should define the intended lifecycle rather than relying on manual console configuration.

But lifecycle rules are data-governance decisions.

Before applying them, verify:

- retention requirements;
- regulatory constraints;
- recovery expectations;
- backup requirements.

---

# 73. IAM

Terraform can manage:

- roles;
- policies;
- attachments;
- trust relationships;
- pipeline-specific identities.

The goal should be:

```text
least privilege
+
reviewability
+
repeatability
```

rather than:

```text
one admin role for everything
```

---

# 74. KMS and Encryption

Terraform can represent encryption infrastructure such as:

- encryption keys;
- key policies;
- aliases;
- references from storage resources.

Conceptually:

```text
KMS key
   ↓
encrypted bucket
   ↓
encrypted data
```

Key management itself is security-sensitive.

Avoid creating broad key access simply to make initial deployment easier.

---

# 75. Catalogs

A data catalog can contain:

```text
database
schema
table metadata
permissions
```

Terraform can manage catalog-related resources when a provider supports them.

Use Terraform for infrastructure and durable configuration, while keeping data transformation/table contents in their appropriate data-engineering tools.

---

# 76. Warehouses

Terraform providers can manage warehouse infrastructure such as:

- databases;
- schemas;
- roles;
- compute/warehouse objects.

A useful division is:

```text
Terraform
→ infrastructure and stable platform configuration

dbt / SQL migration tooling
→ analytical transformations and database object evolution where appropriate
```

Do not force every data change into Terraform.

---

# 77. Managed Spark

Terraform can represent managed Spark resources such as:

- clusters;
- pools;
- roles;
- supporting infrastructure.

The exact resource model depends on the cloud/provider.

The concept is:

```text
Terraform
   ↓
Managed Spark infrastructure
   ↓
Data processing
```

This complements, rather than replaces, the Spark application curriculum.

---

# 78. Kafka

Terraform providers can represent Kafka infrastructure and topics.

Conceptually:

```hcl
resource "example_kafka_topic" "events" {
  name       = "events"
  partitions = 6
}
```

Topic configuration is infrastructure.

The actual streaming application remains application code.

Keep that ownership boundary clear.

---

# 79. Safety: Data Infrastructure Is Different

Not all resources have the same risk.

Consider:

```text
temporary dev compute
        ↓
low risk

production data lake
        ↓
high risk
```

A Senior Data Engineer asks:

> What happens if this resource is destroyed?

before asking:

> Can Terraform create it?

---

# 80. `prevent_destroy`

Terraform supports lifecycle protection:

```hcl
lifecycle {
  prevent_destroy = true
}
```

This can protect a data-bearing resource from accidental Terraform destruction.

Conceptually:

```text
Plan proposes destroy
       ↓
prevent_destroy
       ↓
Terraform refuses
```

---

# 81. What `prevent_destroy` Protects Against

It can prevent accidental destruction through Terraform when the configuration would otherwise cause a destroy.

It is useful for:

- production data buckets;
- critical databases;
- important infrastructure.

But it does not protect against:

- manual console deletion;
- provider-side incidents;
- credential compromise;
- every possible destructive action;
- loss of data that was never backed up.

Therefore:

> `prevent_destroy` is a guardrail, not a backup strategy.

---

# 82. Forced Replacement

Some changes cannot be made in place.

Terraform may show:

```text
-/+
```

or:

```text
forces replacement
```

Meaning:

```text
destroy old
+
create new
```

This is fundamentally different from:

```text
~ update in place
```

---

# 83. Why Forced Replacement Is Dangerous

For a stateless resource:

```text
replace API node
```

may be acceptable.

For:

```text
production data bucket
```

replacement can be catastrophic.

Therefore, when a plan says:

```text
forces replacement
```

stop and investigate.

---

# 84. Replacement Analysis

Ask:

1. Which attribute caused replacement?
2. Is the resource data-bearing?
3. Is the replacement intentional?
4. Can the change be performed in place another way?
5. Is a migration required?
6. Is backup available?
7. Is `prevent_destroy` appropriate?
8. Is the plan targeting the correct environment?

---

# 85. Backups Before Risky Changes

Terraform safety controls are not backups.

Before risky production changes, consider:

```text
Backup/snapshot
      +
Plan review
      +
Protection
      +
Approval
```

For data systems, verify that backups are:

- actually enabled;
- recent;
- restorable;
- accessible;
- tested.

A backup that has never been restored is an assumption, not evidence.

---

# 86. Importing Existing Infrastructure

Sometimes infrastructure already exists:

```text
Cloud bucket
   ↓
created manually
```

and you now want Terraform to manage it.

Conceptually:

```text
Existing resource
       ↓
terraform import
       ↓
Terraform state
       ↓
Matching configuration
       ↓
terraform plan
```

Import connects an existing real resource to Terraform state.

---

# 87. Import Is Not Configuration Generation

A common misconception:

> "If I import the resource, Terraform will automatically create the perfect `.tf` configuration."

Do not assume that.

Import primarily establishes Terraform's knowledge of the existing resource.

You still need configuration that accurately represents the intended state.

Then:

```bash
terraform plan
```

should be used to identify mismatches.

---

# 88. Import Workflow

A disciplined process:

```text
1. Identify resource
2. Record current configuration
3. Import resource
4. Write Terraform configuration
5. Run plan
6. Understand differences
7. Reconcile safely
8. Commit configuration
```

Do not import production resources casually.

---

# 89. Drift

Drift occurs when real infrastructure changes outside Terraform.

Example:

```text
Terraform:
public_access = false

Cloud Console:
public_access = true
```

Now:

```text
Configuration
      ≠
Actual infrastructure
```

This is drift.

---

# 90. Drift Is an Operational Problem

Manual changes can cause:

- security exposure;
- inconsistent environments;
- unexpected plans;
- undocumented behavior;
- broken reproducibility.

A strong platform culture says:

> If Terraform owns it, change it through the Terraform workflow unless there is a documented emergency procedure.

---

# 91. Drift Detection

A common mechanism is:

```bash
terraform plan
```

Terraform refreshes/compares relevant remote information and can reveal differences.

Conceptually:

```text
Terraform code
     ↓
State / provider observation
     ↓
Actual infrastructure
     ↓
Plan
     ↓
Drift visible
```

The exact refresh behavior depends on Terraform/provider versions and configuration.

---

# 92. Drift Incident Lab

Perform:

1. Create a development resource with Terraform.
2. Change one attribute manually in the provider console.
3. Run:

```bash
terraform plan
```

4. Identify the difference.
5. Decide whether the manual change was:
   - unauthorized drift that should be reverted, or
   - a legitimate desired change that should become code.
6. Correct the source of truth.
7. Run `terraform plan` again.
8. Confirm convergence.

The key lesson:

> Drift is not merely a technical difference. It is an ownership and change-management problem.

---

# 93. Linting with tflint

Terraform validation is not the same as linting.

A useful quality stack is:

```text
terraform fmt
        ↓
terraform validate
        ↓
tflint
```

`tflint` can identify Terraform/provider-oriented issues beyond basic syntax.

Typical benefits include:

- style consistency;
- suspicious configuration;
- provider-specific issues;
- maintainability feedback.

---

# 94. Security Scanning

Infrastructure code should be security-scanned before deployment.

Common ecosystem tools include:

- Checkov;
- Trivy.

They can detect patterns such as:

- public storage;
- missing encryption;
- wildcard permissions;
- insecure networking;
- overly permissive configuration.

The exact checks depend on tool/version/provider.

---

# 95. Intentionally Insecure Example

Conceptually bad:

```hcl
resource "example_bucket" "raw" {
  name = "production-data"

  public_access_blocked = false
}
```

and:

```hcl
resource "example_policy" "pipeline" {
  actions   = ["*"]
  resources = ["*"]
}
```

Potential findings:

```text
public data exposure
+
excessive permissions
```

The goal of scanning is not to make a green dashboard.

It is to identify real risk.

---

# 96. Security Fix

Prefer:

```text
public access blocked
+
specific allowed actions
+
specific resources
+
encryption enabled
```

For IAM:

```text
ingestion role
 → write raw bucket only

transformation role
 → read raw
 → write curated

quality role
 → read curated
 → write quality results
```

Least privilege should be part of module design.

---

# 97. Production Terraform Quality Gate

A useful conceptual quality gate is:

```text
terraform fmt
        ↓
terraform validate
        ↓
tflint
        ↓
security scan
        ↓
terraform plan
        ↓
human review
        ↓
approved apply
```

Each stage answers a different question:

| Stage | Question |
|---|---|
| fmt | Is the code consistently formatted? |
| validate | Is the configuration structurally valid? |
| tflint | Are there static/provider-specific issues? |
| security scan | Is there an obvious security misconfiguration? |
| plan | What will actually change? |
| review | Is the change intentional and safe? |
| apply | Execute the approved change |

---

# 98. Terraform in CI — Awareness

Terraform will later run as part of CI.

A pull request might produce:

```text
Pull Request
     ↓
fmt check
     ↓
validate
     ↓
lint
     ↓
security scan
     ↓
plan
     ↓
review
```

After approval:

```text
approved
   ↓
controlled apply
```

The complete implementation belongs to Topic 05.

This module establishes the Terraform side of that workflow.

---

# 99. OpenTofu and the IaC Ecosystem

Terraform is not the only infrastructure-as-code tool.

Relevant ecosystem concepts include:

### Terraform

The primary tool taught in this module.

### OpenTofu

An open-source IaC project that emerged from the Terraform ecosystem and maintains a closely related configuration/workflow model.

### Pulumi

Uses general-purpose programming languages for infrastructure definitions.

### Cloud-native templates

Cloud providers also have native infrastructure template systems.

The objective is not to master all of them.

The important skill is:

> Understand declarative infrastructure, state, dependency graphs, review, drift, and safe change regardless of the specific IaC tool.

---

# 100. Terraform vs Pulumi — High-Level

| Dimension | Terraform | Pulumi |
|---|---|---|
| Main configuration model | HCL | General-purpose languages |
| State | Yes | Yes |
| Provider ecosystem | Broad | Broad |
| Declarative infrastructure | Yes | Yes |
| Learning focus here | Primary | Awareness |

Terraform is the primary learning tool because it provides a strong foundation for understanding production IaC concepts.

---

# 101. Terraform vs OpenTofu — High-Level

The learner should understand:

```text
Terraform ecosystem
        ↔
OpenTofu ecosystem
```

Both are relevant to modern IaC discussions.

For production, always verify:

- supported versions;
- provider compatibility;
- module compatibility;
- organizational policy;
- licensing/governance requirements.

Do not assume all versions or ecosystem components are interchangeable.

---

# 102. Production Data Platform Architecture

A conceptual architecture:

```text
                       Git
                        |
                  Terraform Code
                        |
              +---------+---------+
              |         |         |
           Storage     IAM       KMS
              |         |         |
              +---------+---------+
                        |
                 Data Platform
                /      |       \
           Catalog  Warehouse   Kafka
                \      |       /
                  Managed Spark
                        |
                    Pipelines
```

Terraform represents the infrastructure layer.

Application and data tools remain responsible for:

- pipeline logic;
- transformations;
- business rules;
- schema evolution;
- data quality.

---

# 103. Recommended Terraform Repository Structure

A practical structure is:

```text
infra/
├── modules/
│   ├── data_lake/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   ├── pipeline_role/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   └── warehouse_or_catalog/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
│
└── environments/
    ├── dev/
    ├── staging/
    └── prod/
```

This is a useful pattern, not a universal law.

Repository structure should reflect:

- ownership;
- deployment boundaries;
- state boundaries;
- team workflows;
- security requirements.

---

# 104. Complete Hands-On Lab

## Objective

Convert a manually created data platform into Terraform-managed infrastructure.

The lab should include conceptually:

```text
Object Storage
IAM
KMS
Lifecycle
Catalog
Warehouse
Kafka
Managed Spark
```

Provider-specific implementations should use the cloud/data platform available to you.

---

# 105. Lab Phase 1 — Bootstrap

Create:

```text
infra/
```

with:

```text
main.tf
variables.tf
outputs.tf
```

Start with one simple resource.

Run:

```bash
terraform init
terraform fmt
terraform validate
terraform plan
```

Do not apply until you understand the plan.

---

# 106. Lab Phase 2 — Variables

Add:

```hcl
variable "environment" {
  type = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Invalid environment."
  }
}
```

Use:

```text
dev
```

first.

---

# 107. Lab Phase 3 — Outputs

Expose:

```text
bucket name
resource identifier
role identifier
```

Run:

```bash
terraform output
```

Understand which values are safe to expose and which should be sensitive.

---

# 108. Lab Phase 4 — Locals

Add:

```hcl
locals {
  name_prefix = "data-${var.environment}"

  common_tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
```

Use these values throughout the configuration.

---

# 109. Lab Phase 5 — Multiple Resources

Create relationships:

```text
KMS
 ↓
Storage
 ↓
IAM access
```

Use references so Terraform can infer dependencies.

Run:

```bash
terraform plan
```

Predict the order before applying.

---

# 110. Lab Phase 6 — Data Source

Read an existing platform object with a data source.

Example conceptual workflow:

```text
existing account
      ↓
data source
      ↓
account ID
      ↓
IAM resource
```

Explain why Terraform reads rather than creates the object.

---

# 111. Lab Phase 7 — Module

Create:

```text
modules/data_lake/
```

Move storage-related configuration into the module.

Expose:

```text
bucket_name
bucket_id
encryption_key_id
```

Then call it from the environment.

---

# 112. Lab Phase 8 — Pipeline IAM Module

Create:

```text
modules/pipeline_role/
```

Instantiate it for:

```text
ingestion
transformation
quality
```

Use `for_each`:

```hcl
module "pipeline_role" {
  for_each = toset(var.pipelines)

  source = "../../modules/pipeline_role"

  pipeline_name = each.key
}
```

Review the resulting resource addresses.

---

# 113. Lab Phase 9 — Environments

Create:

```text
environments/
├── dev/
├── staging/
└── prod/
```

Use different variables.

The environment should control:

- naming;
- retention;
- resource sizing;
- protection settings.

Do not simply copy/paste entire infrastructure implementations.

---

# 114. Lab Phase 10 — Remote State

Move the environment state to a secure remote backend supported by your chosen platform.

Requirements:

- shared state;
- encryption;
- access control;
- locking where supported;
- backup/versioning where supported.

Never put real credentials into the repository.

---

# 115. Lab Phase 11 — Protection

Protect the production data lake:

```hcl
lifecycle {
  prevent_destroy = true
}
```

Then create a change that would cause replacement.

Run:

```bash
terraform plan
```

Observe how the protection changes the outcome.

---

# 116. Lab Phase 12 — Drift

Manually change a development resource.

Run:

```bash
terraform plan
```

Record:

```text
What changed?
Why?
What does Terraform want to do?
```

Then restore convergence.

---

# 117. Lab Phase 13 — Import

Create or identify an existing development resource outside Terraform.

Import it.

Then write matching configuration.

Run:

```bash
terraform plan
```

Continue until the plan represents your intended state.

---

# 118. Lab Phase 14 — Lint and Security

Run:

```bash
terraform fmt -check
terraform validate
tflint
```

Then run an IaC security scanner such as:

```bash
checkov ...
```

or:

```bash
trivy config ...
```

Fix findings based on actual risk.

---

# 119. Lab Phase 15 — Dev Teardown

Destroy only the development environment:

```bash
terraform destroy
```

Then recreate it:

```bash
terraform apply
```

The key learning objective is:

> Infrastructure can be recreated from code rather than from institutional memory.

---

# 120. Predict → Execute → Inspect → Measure

Use this loop throughout the lab.

## Predict

Before:

```bash
terraform plan
```

write down what you expect.

## Execute

Run the command.

## Inspect

Read:

- plan;
- state;
- provider resources;
- outputs.

## Measure

Record:

- resource count;
- runtime;
- unexpected changes;
- drift;
- security findings.

This turns Terraform from command memorization into engineering reasoning.

---

# 121. Production Incident 1 — Accidental Bucket Replacement

## Scenario

An engineer changes a bucket attribute.

The plan shows:

```text
-/+ bucket
```

## Wrong Response

```text
terraform apply
```

immediately.

## Correct Response

Ask:

1. Why is replacement required?
2. Is the bucket data-bearing?
3. Is the change necessary?
4. Can the desired configuration be achieved in place?
5. Is there a backup?
6. Is `prevent_destroy` appropriate?

## Lesson

> Never treat a replacement plan as a normal update.

---

# 122. Production Incident 2 — Local State

## Scenario

Two engineers maintain the same platform from different laptops.

Engineer A:

```text
state-A
```

Engineer B:

```text
state-B
```

Both believe they have current state.

## Failure

Their plans may disagree.

## Correct Architecture

```text
Engineer A ─┐
Engineer B ─┼──> secure remote state
CI ──────────┘
```

with locking and access control.

---

# 123. Production Incident 3 — State Exposure

## Scenario

A state file is uploaded to a public or overly accessible location.

## Risk

State may reveal sensitive infrastructure information and potentially sensitive values.

## Response

1. restrict access;
2. investigate exposure;
3. rotate affected secrets if necessary;
4. move to secure remote state;
5. review access logs;
6. improve repository and backend controls.

## Lesson

> State is a security-sensitive production artifact.

---

# 124. Production Incident 4 — Manual Console Change

## Scenario

Someone changes:

```text
bucket public access
```

from the console.

Terraform still declares:

```text
public access blocked
```

## Detection

```bash
terraform plan
```

reveals drift.

## Decision

Determine the intended source of truth:

```text
Was the console change authorized?
```

If no:

```text
Terraform configuration wins
```

If yes:

```text
Update Terraform code
```

then reconcile.

---

# 125. Production Incident 5 — Wildcard IAM

## Scenario

Security scanning reports:

```text
actions = "*"
resources = "*"
```

## Risk

A compromised pipeline could access far more infrastructure than necessary.

## Fix

Scope permissions to:

- required actions;
- required resources;
- required data paths;
- required pipeline.

Then rerun the scanner.

---

# 126. Production Incident 6 — Unprotected Data Resource

## Scenario

A plan proposes:

```text
destroy production data resource
```

## Correct response

Stop.

Then:

```text
Plan review
   ↓
Identify replacement cause
   ↓
Backup validation
   ↓
prevent_destroy where appropriate
   ↓
Migration/change strategy
   ↓
Approval
```

Do not solve data-safety problems with urgency.

---

# 127. Troubleshooting Guide

## `terraform init` fails

Check:

- network access;
- provider source;
- provider version;
- backend configuration;
- credentials;
- registry availability.

Commands:

```bash
terraform init
terraform version
```

---

# 128. `terraform validate` Fails

Likely causes:

- syntax errors;
- invalid references;
- malformed blocks;
- incompatible configuration.

Run:

```bash
terraform fmt
terraform validate
```

Then fix the first meaningful error before addressing downstream errors.

---

# 129. Plan Shows Unexpected Resources

Check:

- current directory;
- current workspace/environment;
- variables;
- `.tfvars`;
- module versions;
- state;
- recent code changes.

First question:

> Am I operating on the environment I think I am?

---

# 130. Resource Wants Replacement

Search the plan for:

```text
forces replacement
```

Then identify the attribute causing it.

Ask:

```text
Can the change be made another way?
```

For data-bearing resources, stop before applying.

---

# 131. State Is Locked

Do not immediately force-unlock.

First determine:

- Is another Terraform process actually running?
- Is a CI job active?
- Did a previous operation crash?
- Is the lock stale?

Only use a force-unlock procedure when you understand why the lock exists and have verified no valid operation is still running.

---

# 132. Resource Already Exists

This often means:

```text
resource exists outside Terraform
```

Possible resolution:

```text
import
```

rather than attempting to recreate it.

Then:

```bash
terraform plan
```

to reconcile configuration.

---

# 133. Imported Resource Still Wants Changes

Import only established the state relationship.

It does not mean:

```text
Terraform configuration = existing configuration
```

You need to:

1. inspect current resource settings;
2. write accurate Terraform configuration;
3. plan;
4. decide which settings should become desired state.

---

# 134. Drift Appears

Ask:

```text
What changed?
Who changed it?
Was it intentional?
Should code or infrastructure change?
```

Then converge:

```text
configuration
      ↕
actual infrastructure
```

---

# 135. Security Scanner Finding

Do not automatically suppress the finding.

Classify:

```text
real vulnerability
false positive
accepted risk
```

For a real vulnerability:

```text
finding
 ↓
understand impact
 ↓
fix code
 ↓
scan again
 ↓
review
```

---

# 136. Common Mistakes

## Mistake 1 — Local state on a laptop

Why bad:

- not shared;
- difficult to secure;
- difficult to back up;
- not suitable for team operations.

## Mistake 2 — Committing state to Git

Why bad:

- state can contain sensitive information;
- Git history is difficult to clean safely;
- broad repository access can become state access.

## Mistake 3 — Applying without reading the plan

Why bad:

- unexpected deletion;
- replacement;
- wrong environment;
- accidental scaling;
- security changes.

## Mistake 4 — Renaming resources casually

Terraform resource addresses are part of state identity.

Refactoring names can cause Terraform to believe one object is different from another unless state-aware refactoring is used appropriately.

## Mistake 5 — Manual console changes

Why bad:

```text
Terraform
   ≠
actual infrastructure
```

creates drift.

---

# 137. Practical Exercises — Level 1 Beginner

## Exercise 1 — First Resource

Create one simple provider/resource configuration.

Tasks:

- initialize;
- format;
- validate;
- plan.

### Checkpoint

Explain:

```text
provider
resource
plan
```

---

## Exercise 2 — Variables

Create:

```hcl
variable "environment" {
  type = string
}
```

Use it in a resource name.

Run plans for:

```text
dev
prod
```

Predict the difference.

---

## Exercise 3 — Outputs

Expose a resource identifier.

Run:

```bash
terraform output
```

Explain why outputs are useful.

---

## Exercise 4 — Locals

Create:

```hcl
locals {
  name_prefix = "data-${var.environment}"
}
```

Use it in two resources.

---

# 138. Practical Exercises — Level 2 Intermediate

## Exercise 5 — Multiple Resources

Create:

```text
KMS
 ↓
Bucket
 ↓
Policy
```

Use references for dependencies.

---

## Exercise 6 — Data Source

Read an existing account/project/resource.

Use the result in a managed resource.

---

## Exercise 7 — `count`

Create multiple interchangeable pipeline workers.

Inspect resource addresses.

---

## Exercise 8 — `for_each`

Create one IAM role per pipeline:

```text
ingestion
quality
transformation
```

Compare resource addresses with the `count` implementation.

---

## Exercise 9 — Module

Extract the data-lake resources into:

```text
modules/data_lake/
```

Expose inputs and outputs.

---

# 139. Practical Exercises — Level 3 Advanced

## Exercise 10 — Remote State

Configure remote state in a safe development environment.

Demonstrate:

- shared access;
- locking where supported;
- backend security.

---

## Exercise 11 — `prevent_destroy`

Protect a data-bearing resource.

Attempt a change that would destroy it.

Observe Terraform's behavior.

---

## Exercise 12 — Forced Replacement

Find a provider attribute that forces replacement.

Create a controlled test.

Predict the plan before running it.

---

## Exercise 13 — Import

Import an existing resource.

Write matching configuration.

Reach a converged plan.

---

## Exercise 14 — Drift

Change infrastructure manually.

Detect drift.

Restore convergence.

---

## Exercise 15 — Security Scan

Introduce a deliberately insecure configuration.

Run:

```text
Checkov or Trivy
```

Fix the issue and rescan.

---

# 140. Practical Exercise — Level 4 Production

Build:

```text
Production Data Infrastructure as Code
```

Required:

```text
Data Lake
IAM
KMS
Catalog
Warehouse
Kafka
Managed Spark awareness
```

Include:

- modules;
- variables;
- outputs;
- locals;
- environment separation;
- remote state;
- state locking;
- least privilege;
- encryption;
- lifecycle rules;
- `prevent_destroy`;
- drift detection;
- linting;
- security scanning.

---

# 141. Knowledge Checkpoint — IaC

Answer:

1. What is IaC?
2. Why is Git useful for infrastructure?
3. What is drift?
4. Why is repeatability important?
5. Why are data platforms especially sensitive to infrastructure errors?

---

# 142. Knowledge Checkpoint — Terraform Language

Answer:

1. What is HCL?
2. What is a block?
3. What is an argument?
4. What is a provider?
5. What is a resource?
6. What is a data source?
7. What is a variable?
8. What is an output?
9. What is a local?

---

# 143. Knowledge Checkpoint — CLI

Explain:

```text
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
terraform destroy
```

Then explain:

```text
validate ≠ plan ≠ apply
```

---

# 144. Knowledge Checkpoint — Plan

Given:

```text
+ resource A
~ resource B
-/+ resource C
- resource D
```

Answer:

- Which resource is created?
- Which is updated?
- Which is replaced?
- Which is destroyed?
- Which deserves the most immediate safety investigation?

---

# 145. Knowledge Checkpoint — State

Explain:

1. Why does Terraform need state?
2. Why is local state unsuitable for a team?
3. Why is remote state useful?
4. Why is state locking needed?
5. Why can state be sensitive?
6. Why should state not be committed to Git?

---

# 146. Knowledge Checkpoint — Modules

Explain:

```text
root module
   ↓
data_lake module
   ↓
pipeline_role module
```

Then answer:

> What makes a module reusable instead of merely moving code into another folder?

---

# 147. Knowledge Checkpoint — `count` vs `for_each`

Choose:

### Scenario A

Create exactly five interchangeable workers.

### Scenario B

Create one named role for each of:

```text
ingestion
quality
transformation
```

Expected reasoning:

```text
A → count
B → for_each
```

because named identity is important in B.

---

# 148. Knowledge Checkpoint — Safety

Answer:

> A plan says a production data bucket must be replaced. What do you do?

Strong answer:

```text
Stop
→ identify replacement cause
→ verify environment
→ assess data impact
→ validate backups
→ determine safer alternative
→ consider prevent_destroy
→ review/approve
→ execute controlled migration if necessary
```

---

# 149. Knowledge Checkpoint — Drift

Answer:

> The console says encryption is disabled, but Terraform says encryption should be enabled. What happened?

Expected:

```text
drift
```

Then determine whether the manual change was authorized.

---

# 150. Final Production Quality Gate

Before applying meaningful infrastructure changes:

```text
1. terraform fmt -check
2. terraform validate
3. tflint
4. security scan
5. terraform plan
6. inspect replacements/destructions
7. verify environment
8. verify data protection
9. human review
10. controlled apply
```

This is a conceptual quality gate, not the full CI implementation.

---

# 151. Senior Data Engineer Interview Questions

## Fundamentals

### 1. What is Terraform?

Terraform is an Infrastructure as Code tool that lets engineers declaratively define infrastructure and use providers to manage external systems.

### 2. What is IaC?

Infrastructure as Code represents infrastructure in version-controlled, machine-readable configuration that can be reviewed, reproduced, and applied consistently.

### 3. What is a provider?

A provider connects Terraform to an external API/platform and implements resource/data-source behavior.

### 4. What is a resource?

A resource represents infrastructure Terraform manages.

### 5. What is a data source?

A data source reads information about existing infrastructure without making that object Terraform-owned in the same way a resource is.

### 6. What is state?

State is Terraform's tracking information that maps Terraform configuration/resource identities to real infrastructure and stores information needed for planning.

### 7. What is a plan?

A plan is Terraform's proposed set of changes after evaluating configuration, state, and provider information.

---

# 152. Intermediate Interview Questions

## 8. Why use remote state?

To provide shared, controlled state for a team and automation rather than independent local state files.

## 9. Why use state locking?

To prevent conflicting concurrent state-changing operations.

## 10. Why secure state?

Because state can contain sensitive infrastructure information and potentially sensitive values.

## 11. Modules vs copy/paste?

Modules provide reusable, parameterized infrastructure components with clear interfaces.

## 12. `count` vs `for_each`?

`count` is convenient for interchangeable indexed instances; `for_each` is often better when stable named identity matters.

## 13. How do you manage environments?

Use separate state boundaries, environment-specific configuration, and reusable modules rather than uncontrolled duplication.

## 14. How do you import existing infrastructure?

Import the resource into Terraform state, write matching configuration, then use plans to reconcile differences.

---

# 153. Advanced Interview Questions

## 15. How do you prevent accidental deletion of a data lake?

Use:

- `prevent_destroy`;
- backups/versioning;
- restricted production access;
- plan review;
- controlled applies;
- security and policy controls.

## 16. What causes resource replacement?

A provider may mark particular attribute changes as requiring recreation, producing a replacement plan.

## 17. How do you detect drift?

Use Terraform planning against the current infrastructure and investigate differences between desired configuration and actual state.

## 18. How do you secure Terraform state?

Use a secure remote backend with access control, encryption, locking, auditing, backups/versioning where supported, and environment separation.

## 19. How do you scan Terraform?

Use static/security tools such as `tflint`, Checkov, or Trivy, then investigate and remediate meaningful findings.

## 20. How should Terraform be used in CI?

Typically:

```text
format
→ validate
→ lint
→ security scan
→ plan
→ review
→ approved apply
```

The detailed CI implementation belongs to Topic 05.

## 21. How would you structure Terraform for a production data platform?

A strong answer includes:

- reusable modules;
- explicit environment boundaries;
- secure remote state;
- least-privilege IAM;
- encryption;
- protected data resources;
- plan review;
- drift detection;
- security scanning;
- clear ownership boundaries.

---

# 154. Final Capstone — Production Data Infrastructure as Code

## Objective

Design and implement:

```text
                    Terraform
                        │
        ┌───────────────┼────────────────┐
        │               │                │
    Data Lake        IAM/Roles        Encryption
        │               │                │
        └───────────────┼────────────────┘
                        │
                 Data Platform
                /      |       \
            Catalog  Warehouse  Kafka
```

Requirements:

- reusable modules;
- variables;
- outputs;
- locals;
- environment separation;
- remote state;
- state locking;
- least privilege;
- encryption;
- lifecycle rules;
- `prevent_destroy`;
- plan review;
- drift detection;
- linting;
- security scanning.

The learner must demonstrate:

```text
Create
→ Plan
→ Review
→ Apply
→ Detect Drift
→ Protect
→ Modify
→ Recover
→ Destroy Dev
→ Recreate Dev
```

---

# 155. Capstone Deliverables

The learner should produce:

```text
infra/
├── modules/
│   ├── data_lake/
│   ├── pipeline_role/
│   └── warehouse_or_catalog/
│
└── environments/
    ├── dev/
    ├── staging/
    └── prod/
```

Plus evidence of:

```text
terraform fmt
terraform validate
terraform plan
tflint
security scan
```

and a written explanation of:

- state architecture;
- locking;
- environment boundaries;
- IAM model;
- data protection;
- drift procedure;
- rollback/recovery considerations.

---

# 156. Capstone Assessment Rubric

| Area | Beginner | Intermediate | Production |
|---|---|---|---|
| HCL | Can read syntax | Writes resources | Designs reusable configuration |
| Providers | Can configure | Controls versions | Designs provider boundaries |
| Resources | Creates resources | Connects dependencies | Reviews lifecycle risk |
| State | Understands concept | Uses remote state | Secures/operates state |
| Modules | Uses modules | Creates modules | Designs module interfaces |
| Environments | Uses variables | Separates state | Enforces environment isolation |
| IAM | Understands roles | Creates scoped roles | Designs least privilege |
| Safety | Reads plans | Handles replacements | Protects data-bearing resources |
| Drift | Understands concept | Detects drift | Establishes remediation process |
| Security | Runs scanner | Fixes findings | Builds security into module design |
| Operations | Runs commands | Troubleshoots | Establishes production controls |

---

# 157. Final Assessment

You should be able to answer **YES** to all of these:

- [ ] I understand why Infrastructure as Code is necessary.
- [ ] I understand Terraform's mental model.
- [ ] I can write basic HCL.
- [ ] I can configure providers.
- [ ] I can create and reference resources.
- [ ] I understand data sources.
- [ ] I can use variables, outputs, and locals.
- [ ] I can use `terraform init`.
- [ ] I can use `terraform fmt`.
- [ ] I can use `terraform validate`.
- [ ] I can create and carefully read a `terraform plan`.
- [ ] I can safely use `terraform apply`.
- [ ] I understand the risks of `terraform destroy`.
- [ ] I understand Terraform state.
- [ ] I can explain why remote state is required for teams.
- [ ] I understand state locking.
- [ ] I understand state security.
- [ ] I can build reusable modules.
- [ ] I understand `count` and `for_each`.
- [ ] I can represent dev/staging/prod infrastructure.
- [ ] I can use separate state per environment.
- [ ] I can use environment variable files.
- [ ] I can model data-lake infrastructure.
- [ ] I can model pipeline IAM.
- [ ] I understand KMS/encryption infrastructure conceptually.
- [ ] I can represent catalogs and warehouse objects conceptually.
- [ ] I understand Terraform-managed Kafka infrastructure conceptually.
- [ ] I understand managed Spark infrastructure as an IaC target.
- [ ] I can protect data-bearing resources with `prevent_destroy`.
- [ ] I can identify forced replacement in a plan.
- [ ] I understand why backups are still necessary.
- [ ] I can import existing infrastructure.
- [ ] I can detect and resolve drift.
- [ ] I can run Terraform linting.
- [ ] I can perform IaC security scanning.
- [ ] I understand how Terraform fits into CI.
- [ ] I understand Terraform/OpenTofu/Pulumi at an ecosystem level.
- [ ] I can safely reason about production data infrastructure using Terraform.

---

# 158. Coverage Audit

The roadmap requirements are intentionally mapped below:

```text
[x] Infrastructure as Code
[x] Repeatability
[x] Review/history
[x] Drift detection
[x] HCL
[x] Providers
[x] Resources
[x] Data sources
[x] Variables
[x] Outputs
[x] Locals
[x] terraform init
[x] terraform fmt
[x] terraform validate
[x] terraform plan
[x] terraform apply
[x] terraform destroy
[x] Reading plans
[x] State
[x] Shared state
[x] Remote backend
[x] State locking
[x] State sensitivity
[x] Modules
[x] data_lake module
[x] pipeline_role module
[x] count
[x] for_each
[x] Multiple environments
[x] Separate state
[x] Variable files
[x] Buckets
[x] Lifecycle rules
[x] IAM
[x] KMS
[x] Catalogs
[x] Warehouse objects
[x] Managed Spark
[x] Kafka topics
[x] prevent_destroy
[x] Forced replacement
[x] Backups
[x] Import
[x] Drift
[x] tflint
[x] Checkov/Trivy
[x] Terraform in CI awareness
[x] OpenTofu
[x] Pulumi/cloud-native templates awareness
[x] Hands-on lab
[x] Production scenarios
[x] Troubleshooting
[x] Knowledge checkpoints
[x] Exercises
[x] Interview questions
[x] Final assessment
```

---

# 159. Connection to the Next Topics

The dependency chain is:

```text
Topic 04 — Terraform
        ↓
Topic 05 — CI pipelines
        ↓
Topic 06 — Environment promotion
        ↓
Topic 07 — Cloud secrets managers
```

This topic establishes:

> **Infrastructure as Code**

The next topics build on it:

- CI automates Terraform quality checks and delivery workflows;
- environment promotion governs how changes move through dev/staging/prod;
- cloud secrets managers provide dedicated credential management.

Those topics should not be re-taught here.

---

# 160. Final Mental Model

Remember:

```text
                    Git
                     |
              Terraform Code
                     |
             +-------+-------+
             |       |       |
          Storage   IAM     KMS
             |       |       |
             +-------+-------+
                     |
                Terraform
                     |
             +-------+-------+
             |               |
           State           Plan
             |               |
             +-------+-------+
                     |
                   Apply
                     |
             Real Infrastructure
```

And for every production change:

```text
Change code
    ↓
Format
    ↓
Validate
    ↓
Lint
    ↓
Security scan
    ↓
Plan
    ↓
Read every destructive/replacement change
    ↓
Review
    ↓
Apply
    ↓
Verify
```

The senior-level principle is:

> **Terraform is not primarily about writing HCL. It is about safely managing the lifecycle of infrastructure whose failure can affect data, security, availability, and cost.**

For Data Engineering, the most important mindset is:

> **Treat infrastructure as production software: version it, review it, test it, secure it, measure it, and never assume that a successful `terraform apply` means the change was safe.**
