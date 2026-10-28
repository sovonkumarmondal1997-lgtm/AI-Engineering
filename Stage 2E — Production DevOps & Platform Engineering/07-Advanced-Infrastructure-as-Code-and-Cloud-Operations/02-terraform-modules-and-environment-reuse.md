# Terraform Modules and Environment Reuse

Reusable infrastructure modules turn repeated infrastructure patterns into explicit, reviewable interfaces. Safe environment reuse lets a data/ML platform share implementation while keeping environment-specific inputs, state, permissions, and promotion decisions visible. Modules reduce copy/paste drift, but they do not automatically provide security isolation, independent state, tests, or governance. This unit builds from a provider-free module example to production module API design, version promotion, and organization-scale change control.

- **Module:** M07 — Advanced Infrastructure as Code and Cloud Operations
- **Stage:** 2E — Production DevOps & Platform Engineering
- **Unit:** 2
- **Target file:** `02-terraform-modules-and-environment-reuse.md`
- **Estimated study time:** 12–18 hours, including labs and review
- **Prerequisites:** Git, Linux/WSL2, basic HCL, reading a plan, state fundamentals, least privilege, and CI/CD basics
- **Core tools:** Terraform or OpenTofu (record exact binary/version), Git, shell, text editor
- **Awareness tools:** LocalStack, module registries, `terraform-docs`, CI plan matrices
- **Last reviewed:** 2026-10-28; current tool behavior still requires verification
- **Assumed tool baseline:** Terraform/OpenTofu features and CLI syntax are **[VERIFY]** against the installed versions; examples avoid asserting a specific release
- **Substrate:** provider-free local resources by default; no paid cloud required

## Table of contents

- [Unit 2 — Terraform Modules and Environment Reuse](#unit-2--terraform-modules-and-environment-reuse)
  - [2.0 Why this matters in production](#20-why-this-matters-in-production)
  - [2.1 Learning objectives](#21-learning-objectives)
  - [2.2 Concept map and vocabulary](#22-concept-map-and-vocabulary)
  - [2.3 Level 1 — Beginner](#23-level-1--beginner)
  - [2.4 Level 2 — Intermediate](#24-level-2--intermediate)
  - [2.5 Level 3 — Advanced](#25-level-3--advanced)
  - [2.6 Level 4 — Expert](#26-level-4--expert)
  - [2.7 SRE lens](#27-sre-lens)
  - [2.8 Security lens](#28-security-lens)
  - [2.9 Production checklist](#29-production-checklist)
  - [2.10 Hands-on lab set](#210-hands-on-lab-set)
  - [2.11 Self-check questions](#211-self-check-questions)
  - [2.12 Evidence artifacts](#212-evidence-artifacts)
  - [2.13 Common interview and design-review questions](#213-common-interview-and-design-review-questions)
  - [2.14 Sources and verification notes](#214-sources-and-verification-notes)
  - [2.15 Claim register](#215-claim-register)
  - [2.16 Audit report](#216-audit-report)
  - [2.17 Human verification checklist](#217-human-verification-checklist)
  - [2.18 Known limitations and assumptions](#218-known-limitations-and-assumptions)
  - [2.19 Sign-off](#219-sign-off)

## Unit 2 — Terraform Modules and Environment Reuse

### 2.0 Why this matters in production

A module is a reusable package of configuration. An environment root is the deployable composition for one environment/component. For a data platform, the same reviewed bucket pattern may be used for `raw`, `curated`, and `model-artifacts` storage in `dev`, `staging`, and `prod`, while retention, names, access, and approvals differ deliberately. Without modules, copied code drifts. With a poorly designed module, a single defect or unsafe default can affect every consumer.

**Operating principle:** reuse implementation, not risk blindly. A shared module can amplify a defect across many consumers. Each consumer must have an explicit version, a readable plan, a clear state/backend target, and an accountable approver.

A module does not create an independent state by itself. State boundaries are normally determined by the root configuration and backend/workspace arrangement. Nor is a module an authorization boundary: credentials and cloud permissions determine what a caller can do.

### 2.1 Learning objectives

By completion, the learner can:

1. Explain root modules, child modules, inputs, outputs, locals, source addresses, and initialization.
2. Build a deliberately small, typed module API and reuse it across environment roots.
3. Explain `count` versus `for_each`, stable addressing, environment layouts, variable files, provider inheritance, and safe address refactoring.
4. Version modules with a compatibility contract and pin reproducible sources.
5. Review module upgrades with downstream plans, migrate consumers in waves, and report version skew without changing infrastructure.
6. Identify secret, supply-chain, wrong-account, and destructive-refactor risks before apply.

### 2.2 Concept map and vocabulary

| Term | Meaning | Operational consequence |
|---|---|---|
| Root module | Configuration in the working directory from which the CLI is run | Usually defines the deployment unit and backend/state context |
| Child module | Configuration called by a `module` block | Encapsulates reusable configuration; does not automatically isolate state |
| Module source | Where module code is obtained (path, Git, registry, other supported source) | Mutable source refs undermine reproducibility |
| Input variable | A module's declared input contract | Type, validation, nullability, and default determine allowed caller values |
| Output | A named value exposed to the caller | Keep deliberate; outputs can expose sensitive data |
| Local value | A derived expression within one module | Useful for names/tags; not an input or cross-module API |
| Provider configuration | Credentials/region/account and provider settings | Normally owned by root modules and passed/inherited into children |
| Resource address | A stable configuration/state address for a resource instance | Address changes can look like destroy/create unless migration is declared |
| SemVer | Semantic Versioning: PATCH, MINOR, MAJOR | A team-defined compatibility contract, not automatic Terraform behavior |
| Plan matrix | Plans for all relevant consumers/environments for a proposed change | Reveals blast radius before release promotion |
| Version skew | Consumers run different module releases | Can be intentional during rollout; must be visible and bounded |

Module composition:

```text
root module (live/dev/raw)
  └── module "bucket"  --inputs--> child module variables
                                   └── resources/configuration
                                        └── child outputs
  <-- module.bucket.name / module.bucket.id -- root consumers
```

The root decides provider/backend context and passes values. The child declares `required_providers` as needed but, in the standard reusable pattern, does not contain provider configuration blocks.

Repository layout:

```text
infra/
├── modules/
│   └── bucket-pattern/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       ├── versions.tf
│       ├── README.md
│       └── examples/
└── live/
    ├── dev/raw/
    ├── staging/raw/
    └── prod/raw/
```

Module source comparison:

| Source | Example shape | Benefit | Risk / verification |
|---|---|---|---|
| Local path | `source = "../../../modules/bucket-pattern"` | Fast iteration; easy to inspect | Relative path errors; local code changes affect callers immediately |
| Git pinned ref | `source = "git::https://example.invalid/org/repo.git//modules/bucket?ref=<TAG_OR_SHA>"` | Versioned internal distribution | Replace placeholder only with a trusted real source; immutable SHA is strongest reproducibility; verify subdirectory/ref syntax |
| Registry | `source = "namespace/name/provider"`, with `version = "x.y.z"` | Discoverability and version constraints | Verify namespace, provider association, available releases, trust and compatibility |
| OCI/HTTP archive | **[VERIFY]** | May fit artifact distribution systems | Support and exact source syntax vary by engine/version; not used by required labs |

`<iac> init` initializes the working directory and obtains module/provider dependencies as needed. `<iac> get` has overlapping but version-specific module-installation semantics; check the installed CLI help and official docs before relying on it. When a source changes, re-initialize and inspect the resulting diff/plan. Do not assume source changes are harmless.

A common convention is `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`, `README.md`, and `examples/`. These are conventions, not required filenames. `required_version` constrains the CLI engine; `required_providers` declares provider source addresses and version constraints. Neither pins a module's source automatically.

#### Terraform vs OpenTofu divergence table

| Area | Guidance |
|---|---|
| HCL/module basics | Concepts overlap, but validate the exact syntax and behavior against the selected engine/version **[VERIFY]**. |
| `optional()` object attributes | Syntax and defaults are version-sensitive; test a minimal configuration on the chosen binary **[VERSION-SENSITIVE]**. |
| `precondition`, `postcondition`, `check` | Confirm availability, evaluation semantics, and failure behavior for the chosen version **[VERIFY]**. |
| Provider/module compatibility | A provider or module that works with one engine is not automatically guaranteed to work with the other; inspect its declared constraints and test. |
| Registry endpoints | Do not assume identical endpoints or publication behavior; verify official engine documentation and configured registry. |
| Module cache / init behavior | Confirm with CLI help and a disposable module-source change **[VERIFY]**. |
| Test framework | Syntax and behavior may differ by version; full testing is deferred to Unit 11. |
| Licensing/governance | If this affects a decision, read each project's current official license and governance documents; no legal conclusion is made here. |

### 2.3 Level 1 — Beginner

#### What modules solve—and what they do not

Modules package repeated configuration behind a named interface. They improve consistency, make review easier, and give teams a controlled place to change defaults. They do not automatically test code, isolate state, limit credentials, or govern releases. A copy/pasted module can still contain a bad default; a well-written module can still be called with the wrong provider/account.

#### Provider-free starter example

This starter uses `terraform_data`, a built-in resource in supported Terraform versions, to demonstrate module input/output flow without cloud credentials. **[VERIFY]** that the selected Terraform/OpenTofu version supports the resource and syntax; if not, use the engine's documented local/provider-free equivalent and do not install an unreviewed provider just to make the sample run.

File tree:

```text
starter/
├── main.tf
└── modules/
    └── label/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

```hcl
# File: modules/label/variables.tf
variable "environment" {
  description = "Short environment identifier."
  type        = string
  nullable    = false
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be dev, staging, or prod."
  }
}

variable "component" {
  description = "Logical platform component."
  type        = string
  nullable    = false
}
```

```hcl
# File: modules/label/main.tf
locals {
  label = "${var.environment}-${var.component}"
}

resource "terraform_data" "label" {
  input = local.label
}
```

```hcl
# File: modules/label/outputs.tf
output "label" {
  description = "Stable logical label for the caller."
  value       = local.label
}
```

```hcl
# File: main.tf
module "raw_label" {
  source      = "./modules/label"
  environment = "dev"
  component   = "raw"
}

output "platform_label" {
  description = "Label consumed by the root module."
  value       = module.raw_label.label
}
```

Commands (run from `starter/`):

```bash
terraform version                 # or tofu version; record exact output
terraform fmt -recursive
terraform init
terraform validate
terraform plan
```

Representative plan summary (not executed here; exact wording varies): a `terraform_data.label` instance is proposed for creation and the root output is expected to evaluate to `dev-raw`. Review the complete plan, especially resource address and provider requirements, before any apply.

**⚠ STATE-CHANGING — disposable local starter only:** after verifying the working directory is exactly the lab root and the plan contains only the expected provider-free resource, run `terraform apply` and approve interactively. This writes local state and creates a local state-tracked object, not a cloud resource. Read-only alternatives are `terraform plan` and `terraform state list`. If the plan contains an unexpected provider or cloud resource, stop. After inspecting the output, **⚠ DESTRUCTIVE — lab root only:** run `terraform destroy` only after a fresh plan review and confirmation that the root is the disposable lab. Verify the plan is limited to the lab resource.

Trace the flow:

1. Root `module "raw_label"` selects a child module by local path.
2. Root values populate `var.environment` and `var.component` in the child.
3. The child derives `local.label` and stores it in the local resource's input.
4. Child output `label` exposes one deliberate value.
5. Root output `platform_label` consumes `module.raw_label.label`.

Common failures:

- **Incorrect source path:** `init` reports it cannot find module files. Verify `pwd`, `find modules -maxdepth 2 -type f`, and the relative path from the root.
- **Missing input:** validation/plan reports a required argument is absent. Compare caller arguments with child `variable` blocks.
- **Missing output:** a reference such as `module.x.id` fails if the child does not define `output "id"`. Inspect `outputs.tf`; do not expose every internal attribute just to silence the error.
- **Initialization confusion:** after changing a module source, run the documented initialization flow and inspect the change; do not delete state as a first response.

Exercise: add a `curated` module call and output. Explain why adding a module call does not, by itself, create a separate state boundary.

### 2.4 Level 2 — Intermediate

#### Build a safe module API before selecting a cloud provider

A production bucket module should have a clear contract for storage purpose, environment, retention, tags, encryption, public access, and optional logging. The resource implementation is provider-specific; do not pretend that a provider-free module can create a real object-storage bucket. Required labs use provider-free mechanics so the learning path remains zero-cost and deterministic. A real S3/LocalStack example is optional and **[VERIFY]** against the selected provider and LocalStack versions.

Example interface sketch (language-level pattern; not a complete cloud bucket resource):

```hcl
# File: modules/bucket-pattern/variables.tf
variable "environment" {
  description = "Deployment environment."
  type        = string
  nullable    = false
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be dev, staging, or prod."
  }
}

variable "purpose" {
  description = "One of raw, curated, or model-artifacts."
  type        = string
  nullable    = false
  validation {
    condition     = contains(["raw", "curated", "model-artifacts"], var.purpose)
    error_message = "purpose must be raw, curated, or model-artifacts."
  }
}

variable "retention_days" {
  description = "Retention period requested by this environment."
  type        = number
  nullable    = false
  validation {
    condition     = var.retention_days >= 30
    error_message = "retention_days must be at least 30; adjust only with an approved data-retention policy."
  }
}

variable "tags" {
  description = "Non-secret ownership and cost metadata."
  type        = map(string)
  default     = {}
}

variable "enable_logging" {
  description = "Whether logging should be configured by a provider-specific implementation."
  type        = bool
  default     = false
}

# No variable to disable encryption is exposed in this interface.
```

```hcl
# File: modules/bucket-pattern/locals.tf
locals {
  logical_name = "${var.environment}-${var.purpose}"
  common_tags = merge(var.tags, {
    environment = var.environment
    component   = var.purpose
  })
}
```

The above is an interface pattern only; it intentionally contains no provider-specific bucket resource. A complete provider implementation must add, after schema verification, versioning, server-side encryption, public-access blocking, lifecycle policy, tags, and optional access logging where supported. Do not paste guessed provider arguments into production. To verify: select the exact provider version, read its official resource documentation, run `terraform providers`, `terraform validate`, and inspect the installed provider schema using the documented CLI command for that engine. LocalStack is an emulator and does not prove AWS IAM, Organizations/SCPs, quota, networking, billing, or full service parity.

#### Types, defaults, nullability, sensitivity

- **Type:** constrains the shape of caller values (`string`, `bool`, `number`, `list(string)`, `map(string)`, object types, etc.).
- **`default`:** makes an input optional. Use defaults only when the behavior is safe and stable; defaults that alter production resources are a release concern.
- **`nullable`:** controls whether `null` is accepted for a variable in supported syntax. **[VERIFY]** exact engine/version semantics.
- **`sensitive`:** marks values for redaction in normal CLI/UI presentation; it does not encrypt values or prevent persistence in state/plan files.
- **`optional()` object attributes:** useful for evolving object inputs, but syntax and default behavior are **[VERSION-SENSITIVE]**. Test absent, explicit-null, and explicit-value cases on the chosen engine.
- **`validation`:** catches invalid inputs early; it is not a substitute for cloud-side policies or runtime enforcement.

#### `count` versus `for_each`

| Dimension | `count` | `for_each` |
|---|---|---|
| Address identity | Numeric index, e.g. `thing[0]` | Key, e.g. `thing["raw"]` |
| Best fit | Repeated identical instances or simple zero/one toggle | Distinct logical objects with stable names/keys |
| List reorder/removal | Can shift which logical item is associated with an index | Stable keys avoid index shifts when keys remain stable |
| Conditional creation | `count = var.enabled ? 1 : 0` is common; output/address shape changes | Empty map/set can represent none; keys define identity |
| Migration risk | Index mapping must be understood | Key changes also change addresses; keys are not magic |

A reorder does not invariably destroy a real object. The plan depends on address identity, provider lifecycle semantics, and whether attributes require replacement. Always inspect the actual plan.

Illustration:

```hcl
# Index-addressed design: removing the first item can shift later indexes.
variable "names" { type = list(string) }
resource "terraform_data" "item" {
  count = length(var.names)
  input = var.names[count.index]
}
```

```hcl
# Key-addressed design: identity is explicit.
variable "items" { type = map(string) }
resource "terraform_data" "item" {
  for_each = var.items
  input    = each.value
}
```

For a map like `{ raw = "raw", curated = "curated" }`, changing the order in the source does not change the keys. Renaming `raw` to `raw-zone` does change the key/address and requires a reviewed migration if state already exists.

#### `locals`, dynamic blocks, variable files

Use `locals` for common names, derived values, tags, and environment metadata. Inputs express caller intent; locals derive values; outputs expose deliberate results. A `dynamic` block generates repeated nested blocks from a collection; use it only when repetition is real and ordinary explicit HCL would be materially less clear.

`terraform.tfvars`, `*.auto.tfvars`, and `-var-file` are common ways to supply environment values. Exact automatic loading and precedence rules are CLI-specific and should be verified against the selected engine/version. Never commit credentials or secret values in variable files. `sensitive` redaction does not prevent state/plan persistence.

Example environment inputs:

```hcl
# File: live/dev/raw/dev.tfvars
retention_days = 30
```

```hcl
# File: live/staging/raw/staging.tfvars
retention_days = 90
```

```hcl
# File: live/prod/raw/prod.tfvars
retention_days = 365
```

These are illustrative retention choices, not policy recommendations. Validate them against data classification, legal retention, cost, and deletion requirements before use.

#### Environment-reuse approaches

| Criterion | Directory per environment | Workspaces | Long-lived environment branches |
|---|---|---|---|
| Isolation | Can pair separate roots/backends/identities | Separate state instances within a workspace model; configuration/backend assumptions are shared | Code can diverge by branch |
| Reviewability | Explicit files and diffs per environment | Environment may be less visible in same root | Changes can be missed across branches |
| Code duplication | Some root boilerplate | Less root duplication | Often high over time |
| Blast radius | Easier to separate roots and permissions | Mistargeted workspace is a risk | Divergent branch behavior is a risk |
| State/backend separation | Explicitly configured per root | Workspace-specific state behavior; verify backend semantics | Depends on branch and backend config, not branch alone |
| Operational complexity | More files to maintain | Fewer roots, stronger context discipline required | Merge/cherry-pick burden |
| Permissions | Can align with separate identities/accounts | Workspaces are **not** a security boundary | Branch permissions do not equal cloud IAM |

**[ASSUMPTION] Recommendation for the running data/ML platform:** prefer `live/<env>/<component>/` roots with deliberate backend/state and identity separation for dev/staging/prod, while reusing reviewed modules. This is a risk-based engineering judgment, not a universal law. Workspaces can suit ephemeral/test copies when the shared configuration and permission model are appropriate; do not rely on them for production authorization isolation. Long-lived environment branches commonly create drift and should require a strong documented reason.

#### Provider configuration inheritance

Configure providers in the root, where account/region/identity are explicit. Child modules declare provider requirements and normally inherit the default provider configuration. For aliases, pass the intended provider explicitly:

```hcl
# Illustrative HCL; verify alias/provider names against the selected provider.
provider "example" {
  # Root-only configuration: endpoint/account/region settings belong here.
}

provider "example" {
  alias = "secondary"
  # Root-only secondary configuration.
}

module "component" {
  source = "./modules/component"
  providers = {
    example = example.secondary
  }
}
```

`example` is a placeholder, not a real provider. This block is a syntax illustration and cannot be run as-is. **Do not put provider configuration blocks inside reusable child modules** in the standard pattern. Provider aliases are dangerous when an implicit/default selection sends a production module to the wrong account or region. Verify the root's identity/region and plan context before state-changing operations.

#### `moved` blocks and refactoring

A `moved` block declares that a resource address has changed, allowing the engine to interpret the old state address as the new one where supported. **[VERIFY]** syntax and minimum version in official docs for the selected binary. Example:

```hcl
# Illustrative; valid only when the resource addresses and engine support match.
moved {
  from = terraform_data.label
  to   = module.label.terraform_data.label
}
```

A move does not guarantee every refactor is safe. Confirm the exact old/new addresses, review the plan, and stop if unexpected create/delete/replace actions appear. A clean/no-op plan is strong evidence that a state-address refactor was interpreted as intended; it is not proof of every external system's health.

### 2.5 Level 3 — Advanced

#### Design a module as a stable API

A module's public API includes input names/types/defaults, validation, output names/meaning, resource-address behavior, required engine/provider versions, security behavior, and upgrade expectations. Keep the interface minimal and opinionated. Exposing every provider argument makes the module hard to support and weakens the intended abstraction; hiding meaningful controls can also be dangerous. Document why each exposed input exists.

API design table:

| Interface choice | Benefit | Cost/risk | Guidance |
|---|---|---|---|
| Typed inputs | Clear caller contract | Type changes can break consumers | Prefer explicit types and descriptions |
| Safe defaults | Easier adoption | A changed default can alter production | Treat behavior-changing defaults as release-impacting |
| Deliberate outputs | Stable downstream contract | Too few outputs can force duplication; too many expose internals | Expose only values callers genuinely need |
| Stable `for_each` keys | Predictable addresses | Key rename is a migration | Treat keys as persistent identifiers |
| One module per coherent capability | Clear ownership | More composition at root | Avoid unrelated “god modules” |
| Deep nesting | Encapsulation in theory | Discoverability and upgrades become harder | Composition over nesting; 2–3 levels is a **guideline**, not a language limit **[ASSUMPTION]** |
| Thin wrapper around one argument | Small abstraction | Often adds little value | Add a wrapper when it encodes policy, defaults, or a meaningful contract |

Semantic Versioning is a release convention that teams define and enforce; it is not automatically inferred by Terraform/OpenTofu.

| Change | Typical classification | Why / caveat |
|---|---|---|
| Fix a documentation typo only | PATCH | No contract behavior changes |
| Correct an internal bug without changing public behavior | PATCH | Confirm no consumer relied on bug behavior |
| Add an optional input with a safe backward-compatible default | MINOR | Validate default truly preserves old behavior |
| Add a new output | Usually MINOR | Consider naming stability and sensitive exposure |
| Rename a required variable | MAJOR | Existing callers fail until migrated |
| Change a default that changes production resources | MAJOR or explicit breaking release | A default can change behavior without changing caller code |
| Change resource addresses without migration mapping | MAJOR / breaking | Can produce destroy/create plans; `moved` may be appropriate |
| Raise required engine/provider minimum | Potentially MAJOR | Existing consumers may not satisfy constraints |
| Change security behavior to become stricter | Depends on contract; often major-impacting | Can break callers or force resource replacement; document and test |
| Relax a security control | Not automatically compatible | May be a security regression even if technically non-breaking |

A module's README should explain purpose, scope, usage examples, inputs/outputs, supported engine/provider constraints, compatibility, risks, and upgrade instructions. `terraform-docs` can generate tables as an optional helper; verify current command/config syntax before adoption. Generated documentation does not replace design explanation.

#### Composition, conditionals, and validation

Use module-level `for_each` when creating repeated component instances with stable keys:

```hcl
module "bucket_pattern" {
  for_each = var.bucket_definitions
  source   = "../../modules/bucket-pattern"

  environment    = var.environment
  purpose        = each.key
  retention_days = each.value.retention_days
  tags           = local.common_tags
}
```

The object type for `bucket_definitions` must be declared to match the fields used. Key changes alter module instance addresses. For optional modules, `count = var.enabled ? 1 : 0` is simple, but outputs become conditional/list-shaped and address `module.x[0]` appears only when enabled. Consider a stable map-based composition when multiple instances or identity matter.

Use validation to enforce constraints that are knowable from inputs. For example, do not expose `encryption_enabled` at all if the module contract requires encryption. If a business reason requires the variable, validate that it is `true`; do not leave a contradictory variable unused. `precondition`, `postcondition`, and `check` blocks can express additional assertions, but exact syntax/evaluation and support are **[VERIFY]** against the engine version. A validation failure is not a replacement for provider-side controls or policy-as-code.

Cross-stack inputs: explicit variables make dependencies visible; provider data sources query the authoritative system but require appropriate read permissions and may introduce runtime dependency; published configuration parameters can decouple consumers but need ownership/version semantics; remote-state outputs couple stacks and can expose more data than expected. Prefer the narrowest, documented interface and do not assume remote-state values are safe to disclose.

#### Pinning and trust

- Registry modules: use a reviewed version constraint appropriate to the release policy; exact pins maximize reproducibility, while a tested compatible range permits controlled upgrades. Verify registry availability and constraint semantics.
- Git modules: pin a reviewed immutable commit SHA or a protected release tag. A tag is only as trustworthy as the repository's tag governance; a mutable branch such as `main` is not a reproducible production reference.
- Public module trust: inspect source, maintainers, release history, dependencies, provider constraints, security defaults, and change notes. Pinning prevents silent version drift but does not prove the pinned code is trustworthy. For critical controls, a reviewed internal module may be appropriate. Deeper supply-chain controls are deferred to M12.
- Public/private registries: use the official engine documentation for current publishing and authentication details; no private registry endpoint is invented here.

#### Promote the same immutable version

```text
reviewed module release vX.Y.Z (or immutable Git SHA)
             │
             ▼
      dev: pin + plan + review + apply
             │ pass evidence / approval
             ▼
   staging: same module version + plan + review + apply
             │ pass validation / approval
             ▼
      prod: same module version + plan + approval + apply
```

Change the version pin in each environment only after the previous promotion gate passes. Do not silently change the module implementation between environments. Environment-specific values may differ, but the module release remains the same. Formal CI/CD approval and promotion design is deferred to M02 Unit 9; formal plan approval is covered in M07 Unit 4.

Shared `versions.tf` patterns can be copied across roots or generated through an approved mechanism. Explicit per-root files add repetition but make the exact constraints easier to review. DRY is a means, not the objective: choose the pattern that keeps behavior and blast radius visible. Terragrunt is previewed in M07 Unit 9 and is not fully taught here.

### 2.6 Level 4 — Expert

#### Module governance and quality bar

Every published module needs a named owner, maintainers, review ownership (CODEOWNERS or equivalent), release responsibility, compatibility contract, deprecation policy, support window, and searchable catalog entry. The minimum publish gate should include:

| Gate | Evidence required |
|---|---|
| Purpose and scope | README describes capability and explicit non-goals |
| API | Inputs, types, validation, outputs, defaults, and compatibility documented |
| Safety | Safe defaults and security controls reviewed |
| Compatibility | Engine/provider constraints tested against supported matrix |
| Examples | Minimal and realistic examples, checked in CI where practical |
| Tests | Unit/plan/integration checks appropriate to module risk; detailed patterns in Unit 11 |
| Plan review | Representative consumer plans with replacements/deletions classified |
| Security/policy | Dependency and policy checks with recorded results |
| Release | Version, notes, migration steps, support/deprecation status |
| Ownership | Maintainer and escalation path listed |
| Consumer impact | Downstream plan matrix completed before promotion |

#### Forty-consumer breaking-change playbook

Suppose a shared bucket module is used by 40 consumers and the team must rename an input and move a resource into a nested module.

1. **Inventory:** enumerate all 40 consumers, environments, current module versions, provider/engine versions, owners, and deployment cadence.
2. **Classify:** identify API breaks, address changes, provider constraints, changed defaults, and security implications. Estimate blast radius before coding.
3. **Compatibility:** add a `moved` block for a supported address move, or a documented migration step. Import blocks are a distinct tool for binding existing objects into state; support/syntax is **[VERIFY]**. Do not use state surgery as a routine substitute for a designed migration.
4. **Candidate:** publish a prerelease/candidate in a controlled internal channel or immutable Git ref, with migration and rollback notes.
5. **Representative consumer:** choose one low-risk consumer representative of common patterns; plan and test it first.
6. **Plan matrix:** run plans for all consumers/environments, record module version, result, creates/updates/replacements/deletes, and approval state.
7. **Wave rollout:** migrate a small pilot, then low-risk consumers, then higher-risk/prod consumers. Define stop conditions (unexpected replacement, plan failure, owner unavailable, policy failure).
8. **Converge:** verify each consumer's deployed version and clean plan. Remove compatibility scaffolding only in a later reviewed release after adoption is measured.

A `moved` block maps addresses declaratively when supported; CLI `state mv` directly changes state and requires backup, target assertion, lock discipline, and a reviewed runbook; import associates an existing real object with a declared resource and is not equivalent to moving an already-managed address. Exact import-block syntax/support is **[VERIFY]**. See M07 Unit 3 for deeper state migration/import/drift coverage.

#### Version-skew report script

The script below reads a deliberately simple repository manifest and prints consumer/version rows. It does not call Terraform, modify state, or change infrastructure. Assumption: a checked-in `module-versions.csv` has columns `environment,component,module,version`.

```python
# File: scripts/report_module_versions.py
import csv
import sys
from collections import defaultdict
from pathlib import Path

EXPECTED = {"environment", "component", "module", "version"}


def main(path: str) -> int:
    source = Path(path)
    if not source.is_file():
        print(f"ERROR: manifest not found: {source}", file=sys.stderr)
        return 2

    rows = []
    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if set(reader.fieldnames or []) != EXPECTED:
            print(f"ERROR: expected columns exactly: {sorted(EXPECTED)}", file=sys.stderr)
            return 2
        for line_number, row in enumerate(reader, start=2):
            if any(not (row.get(key) or "").strip() for key in EXPECTED):
                print(f"ERROR: blank field on CSV line {line_number}", file=sys.stderr)
                return 2
            rows.append({key: row[key].strip() for key in EXPECTED})

    rows.sort(key=lambda row: (row["module"], row["environment"], row["component"]))
    versions = defaultdict(set)
    for row in rows:
        versions[row["module"]].add(row["version"])
        print("{environment:8} {component:16} {module:24} {version}".format(**row))

    print("\nVersion skew:")
    for module in sorted(versions):
        values = sorted(versions[module])
        print(f"{module}: {', '.join(values)}" + (" [SKEW]" if len(values) > 1 else " [CONSISTENT]"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "module-versions.csv"))
```

Fixture:

```csv
# File: module-versions.csv (do not include the comment line in the actual CSV)
environment,component,module,version
dev,raw,bucket-pattern,1.2.0
staging,raw,bucket-pattern,1.2.0
prod,raw,bucket-pattern,1.1.3
dev,curated,bucket-pattern,1.2.0
```

Representative output:

```text
dev      curated          bucket-pattern           1.2.0
dev      raw              bucket-pattern           1.2.0
prod     raw              bucket-pattern           1.1.3
staging  raw              bucket-pattern           1.2.0

Version skew:
bucket-pattern: 1.1.3, 1.2.0 [SKEW]
```

Run `python3 scripts/report_module_versions.py module-versions.csv`. This is a manifest-based report, not automatic HCL parsing; maintain the manifest through a reviewed process or replace it with a tested parser. Test missing-file, wrong-header, blank-field, consistent-version, and skew fixtures. It must be read-only with respect to infrastructure.

#### Incident analyses

| Incident / symptom | Hypothesis | Read-only evidence | Blast-radius / rollback check | Remediation | Verification and prevention | Do not do |
|---|---|---|---|---|---|---|
| 1. Module default changed; production databases propose replacement | Default changed a lifecycle/name/size input | Compare old/new module source, lock/version pin, and saved/current plans | Inventory every consumer; determine whether replacement risks data loss; confirm backups and restore test | Freeze promotion; pin prior known release if appropriate; fix default and publish reviewed patch/major release | Re-plan all consumers; document upgrade notes and default tests | Do not assume reverting Git code reverses already-applied infrastructure |
| 2. `count` list reorder causes address shifts | Index now represents a different logical item | Inspect state addresses and plan diff; map each index to old/new input | Identify exact resources and whether provider replacement is proposed | Stop apply; map identities; use stable keys and reviewed `moved` mapping where supported | Require no unexpected replace/delete; add stable-key tests | Do not apply merely because names look similar |
| 3. Floating `main` changed behavior | Module source is mutable | Inspect initialized module source, commit/ref, CI logs, and consumer pins | Identify all consumers that resolved the changed code | Freeze rollout; pin last reviewed SHA/tag; candidate-test fix | Require immutable pins and release evidence | Do not assume branch name identifies a fixed version |
| 4. Workspace mix-up applies dev values to prod | Wrong workspace/root/variables selected | Read-only: `pwd`, workspace list/current selection, backend config, var-file path, plan | Confirm target identity/state and all planned mutations; do not apply until proven | Stop; select correct root/context only after verification; regenerate plan and review | Require explicit target assertion, separate identities/backends where warranted, approvals | Do not use workspace selection as an access-control substitute |

For every incident, the order is symptom → hypothesis → read-only evidence → blast-radius/rollback check → remediation → verification → prevention. Infrastructure has no universal undo button; a Git revert is not an infrastructure rollback guarantee.

### 2.7 SRE lens

Module quality affects change-failure rate, recovery time, plan-review effort, and consistency across environments. Reuse improves consistency only when versions, defaults, and rollout are governed; one faulty shared release can amplify blast radius.

Candidate service-level indicators (SLIs) and measurement methods:

| SLI | Data source / method | How to set a target |
|---|---|---|
| Approved-module adoption | Inventory roots and module pins; compare with catalog | Establish baseline, then agree a risk-based target |
| Version skew | Version-skew report grouped by module/environment | Set allowed rollout windows and exception expiry |
| Modules with owner/docs/examples/tests/policy checks | Catalog metadata and CI records | Set minimum publication gates by risk tier |
| Consumer plan failure after release | CI plan results linked to release | Baseline by module/risk class; alert on material regressions |
| Release-to-safe-adoption time | Release timestamp to approved consumer convergence | Measure by consumer cohort and deployment cadence |
| Change-failure rate | Incidents/rollbacks attributable to module releases | Define attribution and severity before target setting |
| Rollback/roll-forward rate | Change records and post-release reviews | Review trend; neither direction is universally better |

Do not invent universal SLO thresholds. Agree thresholds using historical data, risk tolerance, and consumer criticality.

Runbook snippet: defect detected → freeze promotion → identify release and affected consumers → run read-only version inventory and plan matrix → assess data-loss/destruction risk and rollback options → validate candidate rollback/fix on one representative consumer → roll out in waves with approvals → verify convergence → write a blameless retrospective and add a regression test.

### 2.8 Security lens

| Threat/failure path | Preventive control | Detective control | Verification | Residual risk |
|---|---|---|---|---|
| Compromised/abandoned public module | Review source/maintainers/dependencies; pin versions; prefer approved internal modules for critical controls | Dependency/release review and CI inventory | Inspect source, release history, provider constraints, and pin | Reviewed code can still contain unknown defects |
| Mutable branch or unpinned module | Immutable SHA or governed release tag; registry version constraint | Scan module sources in repository | Inspect `source` and version pin in every root | Tags may be moved if governance permits |
| Public access or encryption disabled by default | Safe module contract; avoid a disable switch where policy forbids it | Plan/policy checks | Review module and consumer plan; verify cloud policy separately | Local plans do not prove account enforcement |
| Secrets passed to inputs | Prefer external secret references; least privilege; avoid secret-bearing resources when possible | Scan source/log/artifacts and inspect access audit | Use throwaway test values only; check state/plan handling | Values can persist in state/plan even if redacted |
| Overbroad outputs | Expose only necessary values; mark sensitive where appropriate | Output/API review | Compare outputs with consumer need and state sensitivity | `sensitive` is not encryption/access control |
| Provider alias points to wrong account/region | Explicit root provider and `providers = {}` mapping | Plan/account identity checks | Verify identity, region, root, backend and alias before plan/apply | Human review can miss subtle context errors |
| Workspace/environment confusion | Explicit roots, backend/state and identity boundaries | CI target assertions and audit logs | Assert path/environment/workspace and account before changes | Operator can still bypass process |
| Unsafe `moved`/`count` refactor | Reviewed address mapping and plan | Plan matrix and replacement detection | Compare before/after addresses and full plan | Provider lifecycle behavior may surprise |
| Deep/god module hides behavior | Narrow scope, shallow composition, documentation | Architecture review and module metrics | Inspect resource ownership and module tree | Some domain complexity is irreducible |
| Upgrade affects many consumers | Candidate release, staged waves, plan matrix | Version skew and failure-rate reporting | Enumerate all consumers before release | Inventory may be incomplete |
| CI identity can apply all environments | Least privilege, environment-specific identities, protected approvals | Audit cloud and CI permissions | Inspect role policies and workflow permissions | Credential compromise remains possible |

A module is a code-reuse boundary, **not** an authorization boundary. Secret management and identity architecture are deferred to M09; provider/module supply-chain controls are expanded in M12.

### 2.9 Production checklist

- [ ] **Purpose and ownership:** module README states purpose, non-goals, owner, support window, and escalation path.
- [ ] **Root/child boundary:** root owns backend and provider configuration; child exposes a documented API. Evidence: inspect `live/` and `modules/` tree.
- [ ] **Typed inputs:** every public input has type, description, validation where appropriate, and safe defaults. Evidence: inspect variables and run `validate`.
- [ ] **Deliberate outputs:** outputs are documented and avoid unnecessary sensitive exposure. Evidence: output review.
- [ ] **Provider inheritance:** child modules declare provider requirements but do not configure providers in the standard pattern. Evidence: search child modules for provider blocks.
- [ ] **Reproducible source pins:** module sources use reviewed registry constraints or immutable Git refs. Evidence: source/pin inventory.
- [ ] **Dependency trust:** public module source, maintainers, release notes, provider constraints, and security defaults reviewed. Evidence: review record.
- [ ] **Engine/provider constraints:** `required_version` and `required_providers` match tested support. Evidence: CI validation matrix.
- [ ] **Stable identity:** `for_each` keys are stable where identity matters. Evidence: key design and plan.
- [ ] **Justified `count`:** list-index shift risk is documented and migration plan exists. Evidence: code review and tests.
- [ ] **Environment values:** differences use explicit variables/tfvars rather than unmanaged long-lived code forks. Evidence: root diff.
- [ ] **Workspace safety:** workspaces are not treated as security boundaries. Evidence: architecture review and identity design.
- [ ] **Environment isolation:** dev/staging/prod roots, backend/state, and identities match risk. Evidence: target matrix and permissions review.
- [ ] **Address refactors:** `moved`/state-address changes have a reviewed plan with no unintended destroy/replace. Evidence: before/after plan summary.
- [ ] **SemVer policy:** compatibility and breaking-change policy documented. Evidence: README/release policy.
- [ ] **Downstream plan matrix:** every relevant consumer/environment has a plan before promotion. Evidence: matrix attached to release review.
- [ ] **Quality bar:** README, examples, tests, upgrade notes, and policy checks are complete. Evidence: CI report.
- [ ] **Release governance:** maintainer, deprecation, and support policies are defined. Evidence: catalog entry.
- [ ] **Sensitive artifacts:** state, saved plans, credentials, and secret-bearing tfvars are excluded from source/evidence. Evidence: `.gitignore`, repository scan, artifact retention review.
- [ ] **Local lab cleanup:** only lab resources/files removed and no state/secret artifacts retained. Evidence: cleanup verification.

### 2.10 Hands-on lab set

**Global lab safety contract:** all labs are local and must state **Touches real cloud: no.** Use a disposable directory and a recorded engine/version. Before any state-changing command, verify `pwd`, inspect the selected root and providers, and run/inspect a plan. No example silently uses cloud credentials. Outputs below are representative, not execution claims. If the plan differs materially, stop. `terraform_data` availability is **[VERIFY]**; all labs using it require a compatible installed engine or a verified provider-free substitute. Avoid running labs from a repository containing production state.

#### Lab 1 — Build a reusable bucket module and consume it in dev/staging/prod

**Goal / success criteria:** create a provider-free module contract for `raw`, `curated`, and `model-artifacts`; three roots call the same local module with different retention values; each validates/plans without cloud providers; explain promotion and differences. **Touches real cloud: no.**

**Substrate/resources:** local filesystem, Git optional, Terraform/OpenTofu compatible with `terraform_data`; tiny CPU/disk use. **[VERIFY]** engine support before starting. This demonstrates module mechanics, not a real bucket implementation. Provider-specific versioning/encryption/public-access/lifecycle/logging resources are deliberately not fabricated; their required interface is recorded as a contract for a future verified provider adapter.

File tree:

```text
lab1/
├── modules/bucket-contract/{main.tf,variables.tf,outputs.tf}
└── live/{dev,staging,prod}/raw/{main.tf,env.tfvars}
```

```hcl
# File: modules/bucket-contract/variables.tf
variable "environment" {
  type        = string
  description = "dev, staging, or prod."
  nullable    = false
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be dev, staging, or prod."
  }
}
variable "purpose" {
  type        = string
  description = "Storage purpose."
  nullable    = false
  validation {
    condition     = contains(["raw", "curated", "model-artifacts"], var.purpose)
    error_message = "purpose must be raw, curated, or model-artifacts."
  }
}
variable "retention_days" {
  type        = number
  description = "Illustrative retention input; validate with data policy."
  nullable    = false
  validation {
    condition     = var.retention_days >= 30
    error_message = "retention_days must be at least 30."
  }
}
```

```hcl
# File: modules/bucket-contract/main.tf
locals {
  logical_name = "${var.environment}-${var.purpose}"
  controls = {
    versioning_enabled          = true
    encryption_required         = true
    public_access_block_required = true
    lifecycle_retention_days    = var.retention_days
    logging_enabled             = false
  }
}
resource "terraform_data" "contract" {
  input = {
    name     = local.logical_name
    controls = local.controls
  }
}
```

```hcl
# File: modules/bucket-contract/outputs.tf
output "logical_name" {
  description = "Logical name for the future provider adapter."
  value       = local.logical_name
}
output "controls" {
  description = "Declared control contract; not proof of cloud enforcement."
  value       = local.controls
}
```

```hcl
# File: live/dev/raw/main.tf
module "bucket" {
  source         = "../../../modules/bucket-contract"
  environment    = "dev"
  purpose        = "raw"
  retention_days = var.retention_days
}
variable "retention_days" { type = number }
output "logical_name" { value = module.bucket.logical_name }
output "controls" { value = module.bucket.controls }
```

```hcl
# File: live/dev/raw/env.tfvars
retention_days = 30
```

```hcl
# File: live/staging/raw/main.tf
module "bucket" {
  source         = "../../../modules/bucket-contract"
  environment    = "staging"
  purpose        = "raw"
  retention_days = var.retention_days
}
variable "retention_days" { type = number }
output "logical_name" { value = module.bucket.logical_name }
output "controls" { value = module.bucket.controls }
```

```hcl
# File: live/staging/raw/env.tfvars
retention_days = 90
```

```hcl
# File: live/prod/raw/main.tf
module "bucket" {
  source         = "../../../modules/bucket-contract"
  environment    = "prod"
  purpose        = "raw"
  retention_days = var.retention_days
}
variable "retention_days" { type = number }
output "logical_name" { value = module.bucket.logical_name }
output "controls" { value = module.bucket.controls }
```

```hcl
# File: live/prod/raw/env.tfvars
retention_days = 365
```

All three roots use the same relative path shape because each is three levels below `lab1/`. Verify it with `realpath ../../../modules/bucket-contract` from each root. Repeat the root/module call for `curated` and `model-artifacts` as a stretch; keep the three required purposes in the interface validation.

Target assertion and read-only checks, run from each root:

```bash
pwd
find . -maxdepth 2 -type f -print
# Confirm this is the disposable lab1/live/<env>/raw root.
# Confirm no cloud provider block or cloud resource exists in the lab files.
terraform version
terraform fmt -recursive
terraform init
terraform validate
terraform plan -var-file=env.tfvars
```

Representative plan: one `terraform_data.contract` create and outputs reflecting the selected environment/purpose/retention. Review that no cloud provider is required and that the root path and environment value match. **⚠ STATE-CHANGING — lab1 environment root only:** apply only after reviewing the plan and confirming it contains only the provider-free contract resource. Read-only alternative: keep the plan output and inspect it. **⚠ DESTRUCTIVE — lab1 environment root only:** destroy only after checking a fresh plan and confirming the selected root is disposable. Repeat separately for dev, staging, and prod roots; do not use a loop that hides the selected directory.

Expected learning: dev/staging/prod use the same module source but intentionally different values. Plans need not be identical. Promotion means promoting the same immutable module release after each environment's gate; this local path is for development, while production should pin a reviewed version/ref. A real provider adapter must be separately schema-verified and tested; LocalStack parity is incomplete.

**Backup/rollback:** this is disposable state. Before refactoring, retain sanitized plan summaries and Git diff, never commit `terraform.tfstate`. If a plan is unexpected, do not apply; restore the previous lab configuration from Git and re-plan. **Cleanup verification:** run a fresh destroy plan in each lab root, apply only after review, confirm `terraform state list` is empty, and remove the disposable lab directory only after confirming it is the lab-created path.

**Evidence:** sanitized `version.txt`, each environment plan summary, interface files, and a short note explaining the plan differences. **Stretch:** add `curated` and `model-artifacts` roots and a table of retention policy assumptions. No credentials or state JSON retained.

#### Lab 2 — Refactor an address with `moved` blocks

**Goal:** show a resource moved into a child module while preserving its state identity. **Touches real cloud: no.** Substrate: local `terraform_data`; tiny resource estimate. Verify engine support for `moved` blocks and `terraform_data` first.

Initial tree:

```text
lab2/v1/main.tf
```

```hcl
# File: lab2/v1/main.tf
resource "terraform_data" "label" {
  input = "dev-raw"
}
output "label" { value = terraform_data.label.output }
```

Target assertion: `pwd` must end in `lab2/v1`; inspect `main.tf`, `terraform version`, and ensure no provider blocks. Run `fmt`, `init`, `validate`, and `plan`. **⚠ STATE-CHANGING — lab2/v1 only:** apply after review; record `terraform state list` and output summary; do not commit state.

Refactor to:

```text
lab2/v2/
├── main.tf
└── modules/label/main.tf
```

```hcl
# File: lab2/v2/modules/label/main.tf
resource "terraform_data" "label" {
  input = "dev-raw"
}
output "label" { value = terraform_data.label.output }
```

```hcl
# File: lab2/v2/main.tf
module "label" {
  source = "./modules/label"
}
moved {
  from = terraform_data.label
  to   = module.label.terraform_data.label
}
output "label" { value = module.label.label }
```

This illustrates the intended address mapping; **[VERIFY]** exact `moved` syntax and version support with the selected engine. In practice, use the same root and state directory for before/after configuration, or carefully copy only the disposable lab configuration while keeping its local state in the same working directory. Do not create a second empty state and mistake it for a successful migration.

Read-only evidence: inspect the current state address and plan. The expected plan after the refactor is no infrastructure create/destroy, with the address migration recognized. **STOP** if the plan proposes unexpected create/delete/replace; do not apply. Inspect old/new addresses and restore the known-good lab configuration if needed. **⚠ STATE-CHANGING — lab2 disposable root only:** apply the reviewed move plan. Verify `terraform state list` now shows `module.label.terraform_data.label` and a fresh plan is no-op. Do not run `state mv` as a reflex; use it only under a reviewed migration runbook.

**Rollback/cleanup:** preserve the before-plan summary and configuration in Git; if unexpected actions appear, stop and restore the old config before changing state. After evidence capture, review a destroy plan restricted to the lab, then **⚠ DESTRUCTIVE — lab2 root only** destroy and verify state empty. **Evidence:** old/new address summaries, reviewed plan, clean plan result, sanitized version record. **Stretch:** move a second logical resource and explain why every old/new address must be mapped explicitly.

#### Lab 3 — `count` index-shift risk and `for_each` fix

**Goal:** compare address identity with a disposable provider-free stack. **Touches real cloud: no.** Resource estimate: tiny local state. Verify `terraform_data` and `moved` support.

```hcl
# File: lab3/count/main.tf
variable "names" {
  type    = list(string)
  default = ["raw", "curated", "model-artifacts"]
}
resource "terraform_data" "item" {
  count = length(var.names)
  input = var.names[count.index]
}
output "addresses" {
  value = { for i, item in terraform_data.item : tostring(i) => item.output }
}
```

Target assertion: `pwd` must be `lab3/count`, provider-free source is confirmed, and no cloud credentials are used. Run `init`, `validate`, and plan. **⚠ STATE-CHANGING — lab3/count only:** apply reviewed baseline and record `state list` and output mapping. Then change list order/remove an element and plan again. Explain the address identity: `item[0]` remains the same address but its desired input may now represent a different logical item. Depending on resource/provider lifecycle semantics, this can update or replace; it is not correct to claim every reorder destroys an object.

Equivalent stable-key design:

```hcl
# File: lab3/foreach/main.tf
variable "items" {
  type = map(string)
  default = {
    raw             = "raw"
    curated         = "curated"
    model-artifacts = "model-artifacts"
  }
}
resource "terraform_data" "item" {
  for_each = var.items
  input    = each.value
}
output "addresses" {
  value = { for key, item in terraform_data.item : key => item.output }
}
```

In a real migration, a move mapping must map each old index to its logical key; for example `terraform_data.item[0]` to `terraform_data.item["raw"]`, but the mapping must match the actual baseline state. **[VERIFY]** `moved` syntax and mapping support for the selected engine. Do not copy an illustrative mapping unless index-to-key identity is proven. Generate the before/after plan and stop on unexpected destroys/replacements. Never apply a plan whose address mapping is uncertain.

**Backup/rollback:** retain the old configuration and sanitized plan/state-address summary; do not commit state JSON. If mapping is unclear, stop and rebuild the disposable lab from a clean directory rather than performing state surgery. **⚠ DESTRUCTIVE — lab3 disposable root only:** after reviewing a fresh plan, destroy only the lab resources and verify state is empty. **Evidence:** baseline and changed plan summaries, index/key mapping table, final stable-key plan. **Stretch:** rename a `for_each` key and show why key changes also require migration planning.

#### Lab 4 — Workspace-versus-directory comparison memo

**Goal:** write a design memo and safely inspect local workspace behavior. **Touches real cloud: no.** No cloud resources; local-only.

Memo:

- **Single root with workspaces:** convenient when environments share the same configuration and backend model, but workspace context can be confused and is not a security boundary.
- **Directory per environment:** explicit roots and variable files make differences and plans reviewable; can pair with separate backends/identities, at the cost of repeated root boilerplate.
- **Branch per environment:** allows differences but creates merge/cherry-pick drift and can hide changes from one environment.
- **[ASSUMPTION] Recommendation:** for the data/ML platform, use `live/dev/<component>`, `live/staging/<component>`, and `live/prod/<component>` roots with appropriate backend/state and identity separation. Promote the same module release through all three. Use workspaces for disposable or structurally similar copies only when access controls and backend semantics are appropriate.

Reviewer checklist: Are environment values explicit? Is the state/backend target clear? Are cloud identities separated as risk requires? Are workspaces mistakenly treated as authorization? Can a reviewer identify the target from the plan? Are long-lived branches creating drift? Is module version consistent across promotion gates?

Target assertion: inspect `pwd`, `terraform version`, provider blocks, and backend configuration. If the root is not the disposable lab, stop. If using the workspace demonstration, use only a fresh provider-free local directory and verify workspace commands in installed CLI help. Read-only: list workspaces and inspect current selection. **⚠ STATE-CHANGING — lab4 disposable root only:** creating/selecting a workspace changes the state context; record the current selection, create/select only a lab-named workspace, and verify it before any plan. Do not select a production workspace. Plan before apply; no apply is required for the memo. **⚠ DESTRUCTIVE — lab4 lab-created workspace only:** remove it only after verifying the exact workspace and that its lab state is disposable; if state/resource deletion semantics are unclear, leave it in place and document rather than risking data loss.

**Evidence:** memo, reviewer checklist, sanitized version/target assertion, and workspace list if used. **Stretch:** compare the same module pin in three root directories. Cleanup: remove only the temporary lab directory after verifying its path and absence of state/secret artifacts.

#### Lab 5 — Module versioning and SemVer breaking-change exercise

**Goal:** use a local Git fixture to show immutable refs and a deliberate API change. **Touches real cloud: no.** Substrate: local Git and provider-free `terraform_data`; no public registry/network dependency.

Create a disposable repo:

```bash
mkdir -p lab5/module
cd lab5/module
git init
```

```hcl
# File: lab5/module/main.tf (v1)
variable "label" { type = string }
resource "terraform_data" "label" { input = var.label }
output "label" { value = terraform_data.label.output }
```

```markdown
# File: lab5/module/README.md
# Label module

Purpose: store a caller-provided non-secret label in provider-free state.
Inputs: `label` (required string).
Outputs: `label` (the stored output value).
Compatibility: test against the engine version recorded by the consumer.
Change policy: PATCH fixes behavior without contract changes; MINOR adds backward-compatible optional inputs/outputs; MAJOR changes required inputs, defaults with behavior changes, or resource addresses.
Risks: state and plans can contain values; never pass secrets.
```

```hcl
# File: lab5/consumer/main.tf
module "label" {
  source = "../module"
  label  = "dev-raw"
}
output "label" { value = module.label.label }
```

Initialize and plan from `lab5/consumer`, after verifying the source path points only to the local fixture and no cloud provider is configured. **⚠ STATE-CHANGING — lab5 consumer only:** apply only after reviewing the plan, then capture output/address summary. Create a Git commit and a local tag after reviewing the diff. **⚠ STATE-CHANGING — disposable Git fixture only:** adding a tag changes repository metadata; ensure you are inside `lab5/module`, not a real project. Use a clearly named local tag such as `v1.0.0` only for this exercise.

Candidate v2: rename required input `label` to `name`. This is **MAJOR** because existing callers fail to provide the new required input. Add a migration note and update the consumer deliberately. Compare the plan before/after; a variable rename alone may cause configuration errors, while a resource address or behavior change can produce infrastructure changes. Never assume SemVer classification determines plan behavior. Pin a local Git ref/commit in a separate test consumer using verified Git source syntax; the exact `git::file://` source syntax and `ref` handling are **[VERIFY]** for the chosen engine. If not supported, demonstrate immutable commit pinning conceptually and use a local path only for the runnable interface test.

Unpinned branch example (static anti-pattern only): a source tracking a moving branch such as `main` can resolve to different code over time. Do not fetch arbitrary internet code or use a floating branch for production. Candidate release note must include: change summary, SemVer classification, compatibility, migration steps, rollback/stop conditions, and test evidence.

Downstream matrix example:

| Consumer | Current pin | Candidate pin | Plan | Approval |
|---|---|---|---|---|
| dev/raw | v1.0.0 | v2.0.0 candidate | PASS only after review | Pending |
| staging/raw | v1.0.0 | v2.0.0 candidate | Not run yet | Pending |
| prod/raw | v1.0.0 | v2.0.0 candidate | Not run yet | Blocked until lower gates pass |

Do not mark plans as passing unless actually executed. Here the table is a planning template, not test evidence. **Rollback:** keep v1 source and consumer config; stop if the candidate plan is unexpected; reverting source does not reverse already-applied changes. **⚠ DESTRUCTIVE — lab5 disposable consumer only:** destroy only after a fresh reviewed plan and exact root assertion. Verify state empty and remove only the temporary fixture after confirming no state/secret files remain. **Evidence:** README, release notes, version pin demonstration, plans summarized without state content, matrix, and retrospective. **Stretch:** add a backward-compatible optional output and classify the release.

### 2.11 Self-check questions

#### Q1 — Root vs child module (multiple choice)
Which statement is correct?

A. Every child module has an independent state file.  
B. The root module is the working configuration directory; child modules are called by module blocks.  
C. A module automatically creates an authorization boundary.  
D. Child modules must configure their own provider credentials.

**Answer: B.** A is tempting because modules look like deployable units, but state normally follows root/backend/workspace configuration. C confuses code reuse with IAM. D violates the standard reusable pattern; provider configuration belongs in roots and is inherited/passed.

#### Q2 — Inputs, outputs, locals, and source pinning
A child module calculates a name from `environment` and `purpose`. Which design is clearest?

A. Put credentials in a local.  
B. Expose every internal resource attribute as output.  
C. Accept typed caller inputs, derive the name with a local, and expose only the required output.  
D. Source the module from a mutable branch because it is easiest.

**Answer: C.** A misuses locals and secrets. B expands the API surface and may expose sensitive details. D is convenient but not reproducible. `init` obtains dependencies; verify current `get` semantics and rerun initialization after source changes.

#### Q3 — `count` vs `for_each` (multiple choice)
A list of logical buckets is reordered. What is the best conclusion?

A. Every reorder always destroys all buckets.  
B. `count` addresses are index-based and may associate an address with a different logical item; inspect the plan.  
C. `for_each` keys can be renamed without any address effect.  
D. `-target` is the normal fix.

**Answer: B.** A overstates behavior; lifecycle/provider semantics determine the plan. C ignores key identity. D hides the full change and is not a routine migration strategy.

#### Q4 — Environment layout and security (multiple choice)
Which statement is true?

A. Workspaces are a security boundary.  
B. Branch permissions determine cloud IAM.  
C. Separate environment roots can make backend, variables, and review context explicit; permissions still require identity controls.  
D. Dev and prod should always use different code branches.

**Answer: C.** A and B confuse workflow constructs with authorization. D is not universal and long-lived branches can drift. Choose based on risk, reviewability, state isolation, and operational cost.

#### Q5 — Provider inheritance and bucket module review
A child module includes a provider block with a hard-coded region and a variable `encryption_enabled = false` default, but the documentation claims encryption is mandatory. Identify at least three defects.

**Model answer:** provider configuration is hidden inside a reusable child; region/account selection may be wrong; the default contradicts mandatory encryption; caller may bypass or misread security contract; no evidence of provider schema or cloud policy enforcement. Move provider configuration to root, pass aliases explicitly where needed, remove the disable switch or validate it cannot be false, and review the plan/provider schema. `sensitive` is not encryption.

#### Q6 — Refactoring with `moved`
What proves a resource-to-module refactor is safe?

**Model answer:** exact old/new address mapping, compatible engine syntax, known-good baseline, a reviewed plan with no unintended create/delete/replace, and a subsequent clean plan. A `moved` block is not magic and should not be applied when the address mapping is uncertain.

#### Q7 — SemVer classification (multiple choice)
A module renames a required variable and changes a default that causes production replacement. What is the safest classification/policy?

A. PATCH because only HCL changed.  
B. MINOR because callers can edit their files.  
C. Treat as breaking/MAJOR, document migration, and review downstream plans.  
D. No version bump is needed if the plan is saved.

**Answer: C.** A ignores behavior; B ignores compatibility; D confuses plan artifacts with API versioning. A saved plan does not make a change safe.

#### Q8 — Incident scenario: unpinned module changed production behavior
**Symptom:** multiple plans show replacements after a pipeline started using a changed branch. **Diagnosis:** source ref is mutable or resolved code changed. **Blast-radius/rollback check:** inventory all consumers and versions; inspect module source, provider constraints, state addresses, and plans; determine data-loss and recovery risks. **Remediation:** freeze promotion, pin a known reviewed immutable ref, test a candidate fix on one representative consumer, then run a downstream plan matrix. **Prevention:** immutable pins, release ownership, automated inventory, plan review, and staged promotion. Do not assume reverting Git alone undoes applied infrastructure.

#### Q9 — Design question with rubric
Design a module publishing/promotion process for 40 consumers. Include API policy, release pinning, compatibility, testing, rollout, and rollback/stop conditions.

**Scoring rubric (0–2 each; 10 points total):** (1) complete consumer/version inventory; (2) SemVer and migration notes; (3) immutable pin and quality gates; (4) representative test plus full downstream plan matrix; (5) staged rollout, stop conditions, and convergence verification. Score 8+ only if every environment and destructive-plan review is addressed.

### 2.12 Evidence artifacts

Retain only sanitized evidence:

1. Tool/version record (`terraform version` or `tofu version`), OS/substrate, date, and chosen binary.
2. Module repository tree and README/interface contract.
3. Dev/staging/prod plan summaries with the intended differences explained.
4. Environment-reuse comparison memo and reviewer checklist.
5. `moved` refactor old/new address mapping, reviewed plan, and clean/no-op proof.
6. `count`→`for_each` before/after plan summaries and key mapping.
7. SemVer change log, release note, compatibility statement, and migration instructions.
8. Downstream plan matrix for dev/staging/prod and a version-skew report with test fixtures.
9. Completed production checklist and a short retrospective with unresolved risks.

Do not commit state JSON, saved plan binaries, credentials, private keys, or secret-bearing tfvars. Sanitize plans and outputs because they may contain sensitive values. Remove temporary lab directories only after verifying the path is a disposable lab and no state/secret artifacts need secure handling. A plan summary is not a substitute for preserving required audit evidence under the organization's retention policy.

### 2.13 Common interview and design-review questions

1. **How would you design a reusable module API that remains stable while provider resources evolve?**  
   Define a narrow public contract around domain intent rather than exposing every provider argument. Type and validate inputs, document outputs/defaults/constraints, and test supported engine/provider combinations. Treat behavior-changing defaults and address changes as compatibility events. Use a versioned release, candidate consumer, and downstream plan matrix. Stop on unexpected replacement/deletion; a code rollback is not guaranteed infrastructure rollback.

2. **How do you choose directory-per-environment, workspaces, or branches for dev/staging/prod?**  
   Compare state/backend separation, identity/permissions, review visibility, duplication, drift risk, and operational complexity. For this data/ML platform, separate roots with appropriate backend/state and identity boundaries are the default engineering judgment; workspaces can suit structurally similar disposable environments but are not security boundaries. Avoid long-lived branches unless there is a clear governance reason. Prove the target before changes.

3. **How do you migrate `count` resources to `for_each` without unintended replacement?**  
   Capture baseline addresses and map every index to a stable key. Use verified `moved` mappings or a reviewed supported migration procedure. Inspect the full plan and stop on unexpected destroy/replace. Apply only to a disposable test first, then production under a formal migration/approval runbook. Do not assume reordering always destroys resources or that `for_each` key renames are free.

4. **How should a module be versioned, pinned, promoted, and tested across many consumers?**  
   Define SemVer policy, immutable refs, supported engine/provider matrix, owner, release notes, and deprecation windows. Run tests and one representative consumer plan, then a full downstream plan matrix. Promote the same immutable release dev→staging→prod with approvals and stop conditions. Track version skew and convergence; only remove compatibility scaffolding in a later release.

5. **What would you do if a shared module release changed a default and production plans destructive changes?**  
   Freeze promotion and do not apply. Inventory affected consumers, compare old/new module source and defaults, inspect plans/state addresses and data-loss risk, and check restore/rollback feasibility. Pin a reviewed prior version if appropriate, validate a fix on a representative consumer, then rerun the full plan matrix. Add a regression test, change classification/release note, and policy to flag default changes. Git revert alone does not restore infrastructure already changed.

### 2.14 Sources and verification notes

This document is written from known documentation and engineering practice; **verify against current official docs** before using version-sensitive syntax. No live documentation consultation or command execution is claimed here. Prefer official sources and exact installed versions:

- HashiCorp Terraform documentation: Modules; Module Sources; Module Blocks; Input Variables; Output Values; Local Values; Type Constraints; Variable Validation; `count`; `for_each`; Dynamic Blocks; Provider Configuration; Provider Requirements; Version Constraints; `moved` blocks; Workspaces; CLI `init` and `get`; Module Registry; Testing.
- OpenTofu official documentation for the corresponding language, module source, CLI, and testing behavior.
- Official provider documentation for the exact bucket resources/attributes selected for an optional LocalStack/S3 adapter. Confirm provider version and schema; do not infer AWS support from emulator behavior.
- Git documentation: tags, refs, commit IDs, and source history.
- `terraform-docs` official documentation if used; verify command/config syntax.
- Selected CI platform official documentation if implementing concurrency/approval gates.
- Cross-references: M02 Unit 9 (CI/CD approvals/promotion); M09 (secrets/identity); M12 (supply-chain); M15 (tagging/FinOps); M16 (module catalog/self-service); M07 Unit 4 (plan safety/approval); M07 Unit 9 (Terragrunt); M07 Unit 11 (infrastructure testing).

Version-sensitive verification procedure:

1. Record the exact engine binary and version locally.
2. Read that version's official docs for `optional()` object attributes, nullability, pre/postconditions/checks, `moved` and import features, module sources, `init`/`get`, workspace behavior, and test syntax.
3. Confirm provider source/version constraints and inspect the official resource schema for every provider-specific argument.
4. Run `fmt`, `init`, `validate`, and `plan` in a disposable provider-free fixture before adopting syntax.
5. For LocalStack, verify the endpoint is local and read the exact emulator support matrix; do not infer real cloud IAM/SCP/quota/networking/billing behavior.
6. For source pinning, verify the ref resolves to the intended reviewed commit and inspect the fetched source before use.

No fabricated URLs, release numbers, provider attributes, CLI outputs, or test results are provided. All example outputs are representative unless execution evidence is explicitly recorded by the learner.

### 2.15 Claim register

| ID | Section | Claim | Official source document/section | Confidence | Tag |
|---|---|---|---|---|---|
| C01 | 2.2 | Root module is the working configuration context; child modules are called by module blocks | Terraform Modules / Module Blocks | High | — |
| C02 | 2.2 | Modules do not automatically create independent state boundaries | Terraform State and Modules concepts | High | — |
| C03 | 2.2 | Module source may be local path, Git, or registry where supported | Module Sources | High | `[VERIFY]` exact syntax |
| C04 | 2.2 | OCI/HTTP archive module source support is engine/version-sensitive | Terraform/OpenTofu module-source docs | Medium | `[VERSION-SENSITIVE]` |
| C05 | 2.2 | `init` obtains module/provider dependencies as needed | CLI `init` | High | `[VERIFY]` exact current behavior |
| C06 | 2.2 | `get` semantics should be checked for the selected CLI version | CLI `get` | Medium | `[VERIFY]` |
| C07 | 2.2 | `required_version` constrains engine versions | Version Constraints | High | — |
| C08 | 2.2 | `required_providers` declares provider source/version requirements | Provider Requirements | High | — |
| C09 | 2.3 | Variables accept caller inputs and outputs expose named values | Input Variables / Output Values | High | — |
| C10 | 2.3 | Locals derive values within a module | Local Values | High | — |
| C11 | 2.4 | `sensitive` redacts normal presentation but does not encrypt state | Sensitive Data guidance | High | — |
| C12 | 2.4 | `nullable` behavior should be verified for selected engine/version | Input Variables | Medium | `[VERIFY]` |
| C13 | 2.4 | `optional()` object attribute syntax/defaults are version-sensitive | Type Constraints | Medium | `[VERSION-SENSITIVE]` |
| C14 | 2.4 | Variable validation can reject invalid input values | Variable Validation | High | — |
| C15 | 2.4 | `count` creates index-addressed instances | `count` | High | — |
| C16 | 2.4 | `for_each` uses map/set keys for instance identity | `for_each` | High | — |
| C17 | 2.4 | Reordering `count` inputs does not universally guarantee destruction | `count`, plan lifecycle semantics | High | `[ILLUSTRATIVE]` plan depends on resource |
| C18 | 2.4 | Dynamic blocks generate nested configuration blocks | Dynamic Blocks | High | — |
| C19 | 2.4 | Variable-file loading/precedence is CLI-specific enough to verify | Input Variables / CLI variable options | Medium | `[VERIFY]` |
| C20 | 2.4 | Workspaces are not a security boundary | Workspaces | High | — |
| C21 | 2.4 | Provider config belongs in roots in the standard reusable module pattern | Provider Configuration | High | — |
| C22 | 2.4 | Provider aliases can be mapped to child modules | Provider Configuration / Module Blocks | High | `[VERIFY]` exact names |
| C23 | 2.4 | `moved` blocks declare address moves where supported | `moved` blocks | High | `[VERIFY]` version support |
| C24 | 2.5 | Module API includes inputs, outputs, defaults, constraints, and compatibility | Modules / Input Variables / Outputs | High | `[ASSUMPTION]` design framing |
| C25 | 2.5 | SemVer classification is a team policy rather than automatic engine inference | Git/release engineering practice | High | `[ASSUMPTION]` policy examples |
| C26 | 2.5 | Changed defaults can alter consumer behavior without caller code changes | Input Variables / planning semantics | High | — |
| C27 | 2.5 | Stable keys reduce index-shift risk but key renames change addresses | `for_each` | High | — |
| C28 | 2.5 | `precondition`, `postcondition`, and `check` support/evaluation must be verified | Custom Conditions / Checks | Medium | `[VERIFY]` |
| C29 | 2.5 | Floating Git branches are mutable references | Git refs and module sources | High | — |
| C30 | 2.5 | A pin improves reproducibility but does not prove source trustworthiness | Module Sources / supply-chain practice | High | `[ASSUMPTION]` |
| C31 | 2.6 | `moved`, `state mv`, and import solve different migration problems | `moved` blocks / state commands / import docs | High | `[VERIFY]` import syntax |
| C32 | 2.6 | Downstream plan matrix makes consumer impact visible before rollout | Operational design | High | `[ASSUMPTION]` |
| C33 | 2.6 | Git revert does not guarantee infrastructure rollback | Plan/apply operational semantics | High | — |
| C34 | 2.6 | Version-skew script reads a manifest and does not modify infrastructure | Script shown in this unit | High | `[ILLUSTRATIVE]` unexecuted |
| C35 | 2.7 | Module defects can amplify across many consumers | Operational risk analysis | High | `[ASSUMPTION]` |
| C36 | 2.7 | SLI thresholds should be established from local data and risk | SRE measurement practice | High | `[ASSUMPTION]` |
| C37 | 2.8 | Modules are code-reuse boundaries, not authorization boundaries | Module/provider/IAM concepts | High | — |
| C38 | 2.8 | LocalStack does not prove complete real AWS parity | LocalStack support docs and service-specific behavior | High | `[VERIFY]` emulator version |
| C39 | 2.10 | `terraform_data` is available only in compatible engine versions | Terraform resource docs | Medium | `[VERIFY]` |
| C40 | 2.10 | Local provider-free labs do not prove cloud IAM/SCP/quota/networking/billing | Lab substrate limitation | High | `[ILLUSTRATIVE]` |
| C41 | 2.14 | Exact module/test/source behavior should be checked against current docs | Terraform/OpenTofu docs | High | `[VERIFY]` |
| C42 | 2.14 | Example outputs are representative, not execution evidence | Authoring statement | High | `[ILLUSTRATIVE]` |

### 2.16 Audit report

| Pass | Result (PASS / FIXED / OPEN) | Defects found | Fixes applied | Residual risk |
|---|---|---|---|---|
| 1 — Completeness | PASS | Broad required scope | Required sections, five labs, tables, diagrams, questions, evidence, and governance included | Human should compare against prompt line by line |
| 2 — Technical accuracy | FIXED | Provider-specific bucket resource schema would be risky to guess | Kept bucket lab provider-free and documented provider adapter requirements | Exact engine syntax still requires verification |
| 3 — Executability | OPEN | Examples depend on installed `terraform_data`, `moved`, and engine compatibility | Added target assertions, representative outputs, stop conditions, and version checks | Labs have not been executed in this environment |
| 4 — Currency | OPEN | Terraform/OpenTofu and module source semantics can change | Tagged version-sensitive syntax and provided verification steps | Human must check current official docs |
| 5 — Safety/security | PASS | Wrong target, mutable source, and unsafe refactor risks | Local-only targets, plan-first flow, explicit destructive labels, no cloud credentials | Learner must follow assertions; documentation cannot enforce them |
| 6 — Fabrication scan | PASS | Provider resources/versions/URLs could be fabricated | No specific cloud resource schema or unverified version asserted; outputs labelled representative | Official docs were not live-consulted |
| 7 — Pedagogical progression | PASS | Potential jump from basics to governance | Ordered L1→L4 with vocabulary and examples | Learner may need extra CLI practice |
| 8 — Cross-consistency | FIXED | Bucket requirements could imply real resource creation | Clearly separates provider-free contract from real provider adapter | Optional provider implementation remains unbuilt by design |
| 9 — Adversarial review | PASS | Risks include wrong workspace, default changes, unpinned source, count shifts, provider alias errors, secret persistence, deep modules, incomplete inventory | Each risk has a mitigation/stop condition or incident response | OPEN items tracked below |
| 10 — Lab feasibility and cleanup | OPEN | No command execution evidence available | Labs use local resources, provide cleanup verification and no cloud dependency | Run every lab on installed engine and verify final state manually |

### 2.17 Human verification checklist

| Area | What to check | Where to check | Safe command/test |
|---|---|---|---|
| Terraform/OpenTofu baseline | Exact binary/version and supported resources | Installed CLI and official language/resource docs | `terraform version` or `tofu version`; validate a disposable fixture |
| Module sources | Local/Git/registry syntax and immutable ref behavior | Official Module Sources docs for selected engine | Run `init` in a temporary repo with a known local module; inspect resolved source |
| `optional()`, nullability, validation, conditions | Syntax, defaults, evaluation, failure behavior | Type Constraints, Input Variables, Custom Conditions docs | Test absent/null/valid/invalid inputs in a disposable root |
| Provider inheritance and aliases | Exact `providers = {}` mapping and alias names | Provider Configuration and Module Blocks docs | Use a placeholder provider only after selecting a real, verified local/test provider; inspect plan target |
| `moved` / import / state migration | Supported syntax, minimum version, address semantics | `moved` blocks, import, state command docs | Use provider-free lab state and compare before/after plans |
| Bucket resources/attributes | Versioning, encryption, public-access block, lifecycle, tags, logging | Official docs for exact provider and resource version | `init`/`validate`/plan against disposable configuration; do not apply cloud resources |
| LocalStack endpoint/support | Local endpoint, resource support and limitations | Official LocalStack docs for installed version | Assert configured endpoint is loopback/local and run a read-only health check |
| Registry/version constraints | Available module releases and constraint interpretation | Official registry and engine docs | Initialize a disposable consumer pinned to a reviewed release |
| `terraform-docs` / CI | Exact command/config/concurrency/approval semantics | Official tool/platform docs | Run help/version and test in a throwaway branch/repository |
| WSL2/Docker | Docker socket/ports, localhost mapping, LF endings, mounted-drive permissions | Local WSL2/Docker configuration and official docs | `docker version`, `pwd`, `git config --get core.autocrlf`, inspect permissions |
| Labs and cleanup | No real cloud, expected plan, final empty state | Each lab directory and plan | Run `fmt`, `validate`, `plan`; only apply/destroy after exact root and plan review |

### 2.18 Known limitations and assumptions

- Provider-free labs teach module interfaces, addressing, plans, and local state; they do not prove real cloud IAM, Organizations/SCP, quotas, networking, billing, or complete provider parity.
- All plans and outputs in this document are representative unless the learner captures actual execution evidence. No command or lab execution is claimed here.
- Real cloud is optional and outside the required lab path. Any real-cloud configuration would be **ILLUSTRATIVE — NOT RUN IN LABS** and must follow account/cost safety controls; budgets are alerts, not caps, billing data can lag, and exposed credentials can incur costs before alerts fire.
- A complete provider-specific bucket implementation is intentionally not supplied because provider and version were not selected and unverified resource arguments must not be invented. The interface requires versioning, encryption, public-access block, lifecycle, tags, and optional logging where supported; implement only after official schema verification.
- `terraform_data`, `moved`, `optional()`, pre/postconditions/checks, module source forms, `init`/`get`, variable precedence, and import-block behavior require version verification.
- The roadmap's target is `Stage 2E — Production DevOps & Platform Engineering/07-Advanced-Infrastructure-as-Code-and-Cloud-Operations/02-terraform-modules-and-environment-reuse.md`; sibling modules and capstone are cross-references only.
- Module testing depth is deferred to M07 Unit 11; formal plan approval to Unit 4; Terragrunt to Unit 9; supply-chain controls to M12; secrets/identity to M09; tagging/FinOps to M15; module catalog/self-service to M16.
- The 2–3-level nesting recommendation is an engineering heuristic, not a language limit. The recommended directory-per-environment pattern is **[ASSUMPTION]**, not a universal rule.
- WSL2 Docker/localhost behavior and file permissions vary by configuration; verify locally rather than assuming failure.

### 2.19 Sign-off

- **Content status:** DRAFT-AUDITED
- **Audit date:** 2026-10-28
- **Auditor:** AI self-audit; human verification required
- **Unverified items count:** 10 grouped areas in the human verification checklist; several are version-dependent sub-items

The document has been reviewed for scope, progression, safety framing, and required section coverage. This self-audit is not a substitute for running every lab with the installed Terraform/OpenTofu and provider versions in a disposable environment. The labs have not been executed here; this document is not production-certified. Do not apply a plan with unexpected replacement/deletion, do not use real cloud credentials in the required labs, and do not retain state or secret-bearing artifacts as evidence.
