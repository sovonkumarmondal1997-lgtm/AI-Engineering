# Unit 9 — Terragrunt, OpenTofu, and Pulumi alternatives

**Target file:** `09-terragrunt-opentofu-and-pulumi-alternatives.md`  |  **Estimated time:** 12–16 hours  |  **Prerequisites:** Stage 2E M01–M06; HCL, modules, providers, plans, state, Git, Linux, CI/CD, least privilege
**Core tools:** Terraform or OpenTofu, Terragrunt, Git, Python 3 for local fixture checks  |  **Awareness:** Pulumi, CloudFormation, Bicep, CDK/CDKTF, Crossplane, Ansible, Terramate, Terraform stacks  |  **Last reviewed:** 2026-10-28  |  **Tool baseline assumed:** Terraform/OpenTofu/Terragrunt/Pulumi versions are intentionally not pinned to unverified releases; pin exact versions in your scratch lab and verify current supported ranges `[VERIFY]`  |  **Substrate:** local-only; no required real-cloud, paid account, or cloud credentials

> **Source and path note:** The available roadmap tree uses `Stage 2E — Production DevOps & Platform Engineering/02-Advanced-Infrastructure-as-Code-and-Cloud-Operations/`. Some prompt material calls the module `07-Advanced-Infrastructure-as-Code-and-Cloud-Operations/`. The tree path is authoritative; this lesson does not rename or alter either path. This is a standalone lesson artifact. Lab file paths below are illustrative scratch-directory paths, not files created in the repository.

> **Verification policy:** Tool command names, configuration schemas, registry endpoints, compatibility boundaries, state-encryption behavior, and licensing/governance information can change. Tags `[VERIFY]` and `[VERSION-SENSITIVE]` are deliberate review gates, not claims that a behavior was tested. Any output labelled `[ILLUSTRATIVE — NOT EXECUTED]` is an example, not observed output.

---

### 9.0 Why this matters in production

A data platform often begins with one Terraform root module and grows into multiple environments, accounts, regions, and teams. At that point, repeated backend/provider configuration, dependency ordering, engine upgrades, and review boundaries become operational risks—not merely style problems. A wrapper can reduce repetition while also hiding the command, generated files, working directory, or scope that a reviewer must understand. Switching engines or languages can improve governance or developer ergonomics, but it can also introduce state compatibility, dependency, and rollback risks. This unit teaches how to evaluate those trade-offs without letting a tool migration become an uncontrolled infrastructure migration.

### 9.1 Learning objectives

By completion, the learner can:

1. **[L1]** Distinguish an IaC engine, wrapper, general-purpose-language IaC platform, configuration-management tool, and Kubernetes-native control plane.
2. **[L1]** Trace configuration through plan/preview, approval, apply/up, state, and actual infrastructure, including who can write each boundary.
3. **[L2]** Build and debug a small Terragrunt live-repository pattern with shared configuration, dependencies, pinned source, and provider-free components.
4. **[L2]** Explain how mock outputs, hooks, generated configuration, caching, parallelism, and multi-directory execution can change operational risk.
5. **[L2]** Run a Terraform/OpenTofu compatibility comparison on a copied configuration and state, without applying unexpected changes.
6. **[L2]** Explain Pulumi stacks, previews, state backends, secrets, components, and arbitrary-code/dependency risks; complete the guided local walkthrough without cloud access.
7. **[L3]** Compare toolchains against reviewability, testing, state risk, staffing, governance, lock-in, and exit cost using an explicit weighted framework.
8. **[L3]** Produce migration playbooks and an Architecture Decision Record (ADR) that preserve one authoritative owner per resource.
9. **[L4]** Design version-upgrade rings, evidence gates, rollback criteria, incident controls, and a human verification plan for version-sensitive claims.

### 9.2 Concept map and vocabulary

#### The execution and ownership model

```text
Versioned source (HCL / Python / TypeScript / YAML)
        │  code review, dependency pinning, static checks
        ▼
Engine or runtime ── optional wrapper/orchestrator (e.g., Terragrunt)
        │                         │ renders/configures/runs scoped units
        ▼                         ▼
Provider packages / plugins / language dependencies
        │
        ▼
Plan / preview ── policy + risk analysis ── human approval
        │                                        │ approved artifact + identity
        └────────────────────────────────────────▼
                                             Apply / up
                                                │
                       ┌────────────────────────┴──────────────────────┐
                       ▼                                               ▼
                 State/backend                              Real or simulated infrastructure
          (one writer boundary, lock,                     (APIs, resources, external drift)
           access control, backup)
```

A plan or preview is a time-bounded proposal based on a particular code revision, state snapshot, toolchain, provider/dependency set, identity, and observed reality. It is not a permanent guarantee: those inputs can change before apply/up. Preserve the exact reviewed artifact and its provenance where the engine supports it; verify Terragrunt-specific saved-plan workflows for the pinned release `[VERIFY]`.

#### Glossary

| Term | Precise definition | Common misconception |
|---|---|---|
| Infrastructure as Code (IaC) | A repeatable way to describe, review, provision, and/or reconcile infrastructure through versioned configuration or programs. | IaC does not automatically make a change safe or reversible. |
| Declarative DSL | A domain-specific language that describes desired resources and relationships rather than every execution step. | Declarative does not mean side-effect-free or deterministic in every provider. |
| HCL | HashiCorp Configuration Language, used by Terraform and OpenTofu configuration. | Similar syntax does not prove full engine/provider compatibility. |
| Engine | Program that evaluates configuration, constructs a plan, coordinates providers, and manages state lifecycle. | Terragrunt is not an engine equivalent to Terraform/OpenTofu. |
| Provider/plugin | Integration code that translates IaC resource operations into API calls or other actions. | A successful plan does not prove the provider's API behavior is correct. |
| Module | Reusable unit of configuration/API, typically with inputs, resources, and outputs. | A module is not automatically an isolated state boundary. |
| Stack | A logical deployment instance and state boundary in tools such as Pulumi; exact semantics are tool-specific. | A stack is not necessarily equivalent to a Terraform workspace or directory. |
| Backend | Mechanism/location used to store state and coordinate access. | State storage and infrastructure ownership are not the same thing. |
| Wrapper | A layer that composes configuration and/or orchestrates an engine across directories or stacks. | A wrapper cannot remove the underlying engine's state, provider, or API risks. |
| Dependency graph | Directed relationships determining ordering and output flow between components. | A graph edge does not eliminate eventual consistency or external prerequisites. |
| Drift | Difference between recorded/declared desired state and observed infrastructure. | Drift detection and continuous reconciliation are not the same operating model. |
| Compatibility | Ability of a particular code/provider/module/state/tool combination to behave acceptably together. | Similar CLIs or shared HCL do not guarantee compatibility. |
| Lock-in | Cost or difficulty of leaving a tool, language, provider, backend, or operating model. | Open formats do not automatically make migration simple. |
| Exit cost | Engineering, downtime, re-import, testing, retraining, and governance effort to move away. | Exporting state alone does not translate resource semantics. |
| Generated configuration | Files created from higher-level configuration before an engine runs. | Generated files are not harmless; they can change what the engine reads. |
| Mock output | Synthetic dependency output used in a narrow plan/test scenario when a dependency is unavailable. | A mock value is not proof that the real dependency exists or returns the same schema/value. |
| Provider bridge | Integration path that lets one IaC system use provider logic originally developed for another ecosystem. | A bridge does not guarantee feature parity or identical lifecycle semantics. |
| Preview | Proposed operations calculated before mutation, as in Pulumi. | Preview is not a substitute for reviewing program execution and dependency provenance. |
| State ownership | The explicit declaration of which state/tool is authoritative for a resource's lifecycle. | Two tools should not concurrently manage the same resource because each has a state file. |

#### IaC landscape map

| Category | Examples | What it is good for | Main trade-off to investigate |
|---|---|---|---|
| Declarative DSL engines | Terraform, OpenTofu | Provider ecosystem, explicit plans, reusable HCL modules, state-based lifecycle | Engine/provider compatibility, state governance, version and licensing review `[VERIFY]` |
| Cloud-native declarative | AWS CloudFormation, Azure Bicep | Tight alignment to a cloud's native resource model and workflows | Cloud coupling, cross-cloud portability, ecosystem and team skills |
| General-purpose language IaC | Pulumi; AWS CDK; CDKTF | Abstractions, loops/types/tests and language ecosystem | Program evaluation, package supply chain, nondeterminism, code review complexity; CDKTF status/support must be checked `[VERIFY]` |
| Wrapper/orchestration | Terragrunt; Terramate | Shared configuration, multi-directory execution, dependency orchestration | Additional layer, generated files, version coupling, hidden scope and harder debugging |
| Kubernetes-native control plane | Crossplane (Unit 12) | API-based self-service and controller reconciliation | Cluster/controller becomes critical; reconciliation/deletion semantics differ |
| Configuration management | Ansible (Unit 10) | Configure hosts and execute ordered tasks, often after provisioning | Idempotency, inventory, secrets, execution order, and drift behavior differ from IaC engines |

**Tool selection is an operating-model decision.** Compare the size and skill of the team, module/provider ecosystem, environment hierarchy, state boundaries, governance, CI maturity, debugging burden, licensing review, upgrade discipline, and credible exit path. Syntax preference is only one criterion.

### 9.3 Level 1 — Beginner

#### What the tools read, write, and compare

A Terraform/OpenTofu engine reads configuration, selected provider binaries, module code, variables, backend settings, and current state. It refreshes observations through providers and produces a proposed action graph. During apply, provider operations change infrastructure and state is updated. The engine does not automatically inventory every object in an account: unmanaged objects may remain invisible unless separately discovered. A state entry is not proof that the object still exists, and a cloud object is not automatically managed merely because it has a matching name.

Pulumi evaluates a program in a language runtime and produces a preview from program output, stack state, provider behavior, and observed resources. This brings normal software concerns—package resolution, code execution, test quality, and nondeterminism—into the infrastructure workflow. Terragrunt generally wraps Terraform/OpenTofu invocations and organizes configuration across directories; it does not replace their state or providers.

#### First local experiment: provider-free engine boundary

**Substrate:** local-only. **Real-cloud touch:** No. **Purpose:** illustrate that engine configuration and state can be studied without a cloud provider. Run only in a new scratch directory. The exact `terraform_data` availability depends on the selected engine/version; verify it first `[VERIFY]`.

Illustrative scratch file `scratch/unit9/minimal/main.tf`:

```hcl
terraform {
  required_version = ">= 1.4.0" # illustrative lower bound; verify for chosen engine
}

resource "terraform_data" "marker" {
  input = {
    component = "metadata-demo"
    environment = "dev"
  }
}

output "component_name" {
  value = terraform_data.marker.output.component
}
```

Commands for Terraform; for OpenTofu, substitute `tofu` only after verifying that the resource and syntax exist in the selected release `[VERIFY]`:

```bash
cd scratch/unit9/minimal
terraform version
terraform init
terraform validate
terraform plan -out=review.tfplan
terraform show review.tfplan
# Stop and review the plan. It should describe only the local provider-free marker.
terraform apply review.tfplan
terraform state list
terraform output component_name
terraform plan
```

Expected evidence is a state entry for `terraform_data.marker`, an output of `metadata-demo`, and a second plan with no changes. These are **expected outcomes, not executed results**. Do not run `apply` if the directory is not the isolated scratch directory, the binary/version is unexpected, or the plan includes anything else. Cleanup after inspection: `terraform destroy` only in this scratch directory, inspect its plan first, and verify a subsequent plan is empty. State and plan files may reveal configuration and must not be committed.

#### What just happened?

1. Configuration described a provider-free marker; it did not declare an AWS/Azure/GCP resource.
2. `init` prepared the local working directory and selected the engine's dependencies.
3. `validate` checked configuration structure, not whether production behavior would be safe.
4. `plan` compared configuration, state, and what the engine could observe.
5. `apply` executed the approved plan and recorded the resulting state.
6. The second plan checked whether the configuration and recorded state converged for this local example.

#### Beginner mistakes

| Mistake | Symptom | Safer correction |
|---|---|---|
| Treating Terragrunt as the state engine | Confusion about which state/backend a command uses | Identify the underlying engine and exact working directory/state before any command. |
| Running commands from the wrong directory | Unexpected module, backend, or empty plan | Print `pwd`, inspect config files, and assert the scratch path. |
| Treating `sensitive = true` as encryption | Secret still appears in state or artifacts | Treat state, plans, logs, and stack files as sensitive; use protected storage and secret-manager references. |
| Assuming shared HCL means shared behavior | Different plans or errors under another engine | Pin versions and run compatibility tests on copies. |
| Treating a successful plan as approval | Destructive actions are overlooked | Review deletes/replacements, identity, target environment, policy output, and rollback. |

### 9.4 Level 2 — Intermediate

#### Running data-platform example

Use one fictional platform with `dev`, `staging`, and `prod`; components include storage metadata, catalog metadata, IAM/secrets, and network foundations. Each environment/component gets an explicit state ownership boundary. The storage-metadata component emits a harmless identifier; a consumer reads that output. No lab creates a cloud bucket or cloud identity.

#### Terragrunt working model

Terragrunt is useful when several Terraform/OpenTofu roots share backend/provider setup and have dependencies. Its abstraction cost is justified only if it reduces total operational complexity. A plausible live layout is:

```text
scratch/unit9/terragrunt-demo/
├── modules/
│   ├── storage-metadata/main.tf
│   └── catalog-consumer/main.tf
├── live/
│   ├── root.hcl
│   ├── dev/account-dev/us-test-1/storage/terragrunt.hcl
│   ├── dev/account-dev/us-test-1/catalog/terragrunt.hcl
│   ├── staging/account-stage/us-test-1/storage/terragrunt.hcl
│   └── prod/account-prod/us-test-1/storage/terragrunt.hcl
└── README.md
```

The path `us-test-1` is a fictional label, not a cloud region. This is a layout illustration; it does not imply that every Terragrunt release supports every shown syntax identically.

`modules/storage-metadata/main.tf`:

```hcl
terraform {
  required_version = ">= 1.4.0" # verify chosen Terraform/OpenTofu baseline
}

resource "terraform_data" "metadata" {
  input = {
    name        = var.name
    environment = var.environment
  }
}

variable "name" { type = string }
variable "environment" { type = string }

output "metadata_id" {
  value = terraform_data.metadata.id
}
output "metadata_name" {
  value = terraform_data.metadata.output.name
}
```

`modules/catalog-consumer/main.tf`:

```hcl
variable "storage_metadata_id" { type = string }
variable "environment" { type = string }

resource "terraform_data" "catalog" {
  input = {
    environment          = var.environment
    storage_metadata_id  = var.storage_metadata_id
  }
}

output "catalog_id" { value = terraform_data.catalog.id }
```

A root configuration such as `live/root.hcl` centralizes conventions. A representative Terragrunt pattern is shown below, but current Terragrunt syntax and recommended root-file naming must be verified against the pinned version `[VERIFY] [VERSION-SENSITIVE]`:

```hcl
# live/root.hcl — illustrative; not a version-certified configuration
locals {
  environment = "dev"
  account_label = "account-dev" # fictional label; not a real account ID
  region_label = "us-test-1"
}

# Local-only backend example for an isolated scratch lab. Exact Terragrunt
# remote_state/generate schema is version-sensitive: verify before execution.
remote_state {
  backend = "local"
  config = {
    path = "${get_terragrunt_dir()}/terraform.tfstate"
  }
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
}

# Production backend/provider configuration is intentionally omitted. A real
# backend needs explicit identity, locking, encryption, recovery and access
# controls; it must not be inferred from this local example.
```

`live/dev/us-test-1/storage/terragrunt.hcl` (illustrative pattern):

```hcl
include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  # Pin an immutable Git commit or an exact reviewed release/tag.
  # Mutable branches and floating tags are not acceptable for production.
  source = "../../../../../modules/storage-metadata"
}

inputs = {
  name        = "dev-storage-metadata"
  environment = "dev"
}
```

Version-selection conventions: a repository may use `.terraform-version` or `.tool-versions` to communicate the expected engine/runtime versions, but support depends on the version manager and CI image `[VERIFY]`. These files are conventions, not enforcement by themselves. CI must assert the installed binary path/version and fail when it differs from the reviewed baseline. Pin Terragrunt separately; an engine version file does not pin the wrapper.

`live/dev/us-test-1/catalog/terragrunt.hcl` (illustrative pattern):

```hcl
include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../../../modules/catalog-consumer"
}

dependency "storage" {
  config_path = "../storage"

  # Mocks are only for commands explicitly allowed by the chosen policy.
  # Exact attribute names and command filters are version-sensitive.
  mock_outputs = {
    metadata_id = "mock-metadata-id-for-plan-only"
  }
}

inputs = {
  storage_metadata_id = dependency.storage.outputs.metadata_id
  environment         = "dev"
}
```

**Important path check:** The corrected relative source paths assume the shown tree and are still to be validated by the pinned Terragrunt binary. A common deliberate defect is pointing `source` one directory too high or expecting an output key that the producer does not export. The local backend block is an illustrative provider-free pattern; verify `remote_state` and `generate` schema before running. For real cloud backends, do not copy a provider/backend example without separately reviewing identity, encryption, locking, and recovery. A generated provider configuration is another valid DRY use, but this lab has no cloud provider and intentionally avoids a real provider block.

##### `include`, `inputs`, `remote_state`, `generate`, `dependency`, and `source`

- `include` imports shared configuration. Confirm the exact parent lookup and merge behavior in the pinned release `[VERIFY]`.
- `inputs` passes variables into the underlying module. Check type and naming alignment with module variables.
- `remote_state` centralizes backend configuration in real systems. This lesson intentionally does not configure a cloud backend in the required lab. Backend arguments, locking features, and generated config are engine/backend/version-dependent `[VERIFY]`.
- `generate` can create files such as provider/backend configuration. Generated files are executable configuration inputs; inspect their final contents and permissions, and never assume they are benign.
- `dependency` reads outputs from another Terragrunt unit and expresses ordering/output flow. Dependency output resolution can require the producer state to exist.
- `mock_outputs` supplies synthetic output values for selected commands or scenarios. It can unblock a plan/test while the producer is absent; it can also conceal a missing output or wrong dependency path. A mock must never be the evidence used to authorize a real apply.
- `terraform { source = ... }` chooses a module source. Pin to an immutable commit or exact reviewed release, record the source in evidence, and verify how the selected Terragrunt version resolves it.
- `before_hook` / `after_hook` execute commands around engine actions. Treat them as arbitrary code: review shell expansion, inherited environment, permissions, output, failure behavior, and whether they run for every intended command.

##### Mock-output guard

A safer workflow is to separate `plan/test` configuration from apply configuration or use a reviewed policy that rejects mock outputs for any apply-like command. The exact Terragrunt `mock_outputs_allowed_terraform_commands`-style setting and command names are `[VERIFY] [VERSION-SENSITIVE]`; do not rely on a guessed setting. Independently add a CI gate: if the plan evidence contains a known mock sentinel, fail the job; require a real producer state and compare its actual outputs before approval. A sentinel check is a defense-in-depth control, not a substitute for validating the real dependency.

##### `run-all` / `run --all`, blast radius, caching, and parallelism

Terragrunt CLI command names have changed across releases. The historical `run-all` form and newer `run --all` forms are not assumed interchangeable here `[VERIFY] [VERSION-SENSITIVE]`. Before invoking a multi-directory command, print the resolved unit list, filter to one environment/component, and generate plans separately. Require per-component plan evidence, environment/account assertions, policy results, and approvals before any multi-unit apply. A single umbrella command can otherwise cross ten states or accounts before a reviewer understands the full diff.

Parallelism can reduce elapsed time but may increase provider API pressure, throttling, race conditions, or exposure to eventual consistency. Caching can reduce repeated downloads/work, but stale or incorrectly keyed caches can conceal source changes. Treat cache keys, invalidation, source immutability, and concurrency as part of the evidence. Never increase parallelism to mask dependency-order defects.

##### Generated configuration and saved plans

Debug in this order: (1) `pwd` and target-unit list; (2) exact Terragrunt/engine binaries and versions; (3) resolved module source and commit; (4) dependency output names and actual producer state; (5) generated configuration contents; (6) plan JSON/text and resource addresses; (7) provider logs with secrets redacted. The exact command used to render/inspect Terragrunt configuration changes over time `[VERIFY]`; use the pinned release's documented command and save the rendered result in a protected scratch location.

In CI, bind the reviewed plan to a commit SHA, lock-file digest, module source digest, tool versions, backend/state identity, target environment, plan artifact checksum, reviewer approval, and execution identity. Ensure apply consumes the same reviewed plan artifact where supported; do not silently regenerate a fresh plan after approval and call it the same review. Saved-plan workflows under Terragrunt vary by release and orchestration mode `[VERIFY]`.

#### Pattern catalogue

| Pattern | Use when | Do not use when |
|---|---|---|
| Plain engine + repo conventions | Small number of roots; repeated config is manageable | Duplication and ordering failures are already material and measurable |
| Terragrunt shared root config | Several roots share backend/provider inputs and hierarchy | Team cannot debug generated config or pin wrapper/engine together |
| Dependency outputs | Consumer truly needs a producer's exported contract | It creates broad cross-environment coupling or hides ownership boundaries |
| Mock outputs for plan/test | Dependency bootstrap is intentionally incomplete and guarded | Apply, production promotion, or approval relies on mock values |
| Multi-unit run | Fleet operations are explicitly scoped and every unit has reviewed evidence | Broad unfiltered apply across accounts/environments |
| Hooks | A controlled pre/post action is necessary and auditable | Hook is a hidden deployment script or has unreviewed network/secret access |
| Immutable source pin | Reproducible module consumption | Floating branch/tag is needed for an emergency shortcut without a recorded exception |

#### Anti-pattern catalogue

| Bad workflow | Damage mechanism | Corrected approach |
|---|---|---|
| `run-all apply` directly from a broad live root | Many states/accounts mutate under one review | Enumerate units; plan each; approve each; then use a narrowly scoped apply workflow. |
| Mocks enabled without apply guard | Plan may look valid despite missing producer | Restrict mock commands, sentinel-check output, require real producer state. |
| Module source uses a branch name | Same configuration can fetch different code later | Pin immutable commit/exact release and capture digest. |
| Hook downloads and executes a remote script | Supply-chain code runs with CI permissions | Vendor/review script, pin checksum, minimize permissions, log redacted evidence. |
| Generated provider config is not inspected | Wrong region/identity/backend may be selected | Render, assert target values, and review generated files before plan. |
| Cache shared across unrelated source revisions | Stale code/config or confusing results | Content-addressed keys, provenance, explicit invalidation. |

#### When not to add a wrapper

| Question | If yes | Decision |
|---|---|---|
| Is duplication small and obvious? | Yes | Prefer plain Terraform/OpenTofu conventions. |
| Can native modules and environment folders solve reuse? | Yes | Keep the simpler model until a measured gap appears. |
| Does the team lack ownership for wrapper upgrades/debugging? | Yes | Do not add it yet; build operational capability first. |
| Is multi-stack ordering causing repeated incidents? | Yes | Prototype Terragrunt in a sandbox and measure benefit and new failure modes. |
| Will the wrapper obscure plan identity or approval? | Yes | Redesign the pipeline before adoption. |
| Is migration motivated only by fashion or syntax preference? | Yes | Do not migrate without a quantified operational problem and exit plan. |

#### OpenTofu: practical compatibility and migration depth

OpenTofu is an IaC engine with a `tofu` CLI. Do not assume every Terraform configuration, provider, module, registry endpoint, state behavior, or feature works identically in every version. Compatibility is a tested relationship among exact engine versions, provider versions, module sources, backend settings, state snapshot, and features used. Current registry endpoints, governance/licensing documents, state encryption, variable/locals evaluation, provider-defined functions, and test syntax must be verified against official documentation for the exact release `[VERIFY] [VERSION-SENSITIVE]`.

##### Divergence verification table

| Feature/area | Current claim in this lesson | Evidence source to inspect | Status / impact |
|---|---|---|---|
| CLI naming | OpenTofu commands use `tofu`; Terraform commands use `terraform` | OpenTofu CLI docs; Terraform CLI docs | Basic distinction; still pin binary and capture `which`/version. |
| Provider registry | Do not hardcode assumptions that both engines resolve all providers identically | OpenTofu registry docs and provider installation docs; Terraform provider registry docs | `[VERIFY]`; missing provider can block init/migration. |
| Module registry/source | Source addressing and module compatibility must be checked per module | Official module source/registry docs for both engines | `[VERIFY]`; source may be unavailable or semantics may differ. |
| Provider compatibility | Shared provider ecosystem does not imply every provider build/schema is identical | Provider docs, release notes, lock-file diff | `[VERIFY]`; plan/runtime divergence risk. |
| Lock files | Preserve and review `.terraform.lock.hcl`; do not delete it as a migration shortcut | CLI dependency lock-file docs for both | `[VERIFY]`; provider selection/checksums can change. |
| State format | Do not assume all versions can read/write all state snapshots or preserve semantics | State compatibility/migration docs for exact versions | `[VERIFY]`; state may become unreadable or rollback blocked. |
| State encryption | OpenTofu-specific state-encryption options and migration implications are version-sensitive | Official OpenTofu state encryption docs and release notes | `[VERIFY] [VERSION-SENSITIVE]`; loss of key/config can threaten recovery. |
| Variable/locals evaluation | Evaluation timing/features may diverge by release | Official language docs and release notes for both | `[VERIFY] [VERSION-SENSITIVE]`; expressions may fail or evaluate differently. |
| Provider-defined functions | Availability/semantics are release-specific | Official language/provider docs and changelog | `[VERIFY] [VERSION-SENSITIVE]`; module behavior may change. |
| Test framework | Test syntax/behavior must be checked against exact engine version | Official test docs for each engine | `[VERIFY] [VERSION-SENSITIVE]`; CI tests may not port. |
| Licensing/governance | Verify current project licenses, governance model, and policies directly; no status is asserted here | Current official license, governance, security, and contribution documents | `[VERIFY]`; legal/procurement review is a release gate. |
| Saved plans | Plan file compatibility is not assumed across engines or versions | CLI plan/apply docs and migration notes | `[VERIFY]`; generate and review plans with the intended candidate tool. |
| Provider/module checksums | Validate selection and checksum changes rather than blindly regenerating | Official lock-file docs; PR diff | `[VERIFY]`; changed binary provenance can alter behavior. |
| State encryption portability | Encrypted state may depend on configuration/key material; portability must be proven | Official encryption docs; restore test | `[VERIFY]`; missing key/config can block recovery. |
| Compatibility boundary | An empty plan proves only this tested combination | Reproducible scratch test and official docs | Evidence, not universal equivalence. |

##### Safe engine migration protocol

1. Inventory current engine and exact version, binary path, provider lock file, modules, backend, workspace/directory, state lineage/serial where available, and features used.
2. Announce and freeze writes to the affected state. Confirm no scheduled jobs or parallel operators can apply.
3. Copy configuration, lock files, module references, backend metadata (without secrets), and state into a protected scratch directory. Verify the copy by checksum and record the original separately.
4. Verify candidate engine availability for providers/modules, registry source, encryption/decryption requirements, test syntax, and state format.
5. Initialize the copy using the candidate tool's documented syntax. Do not point it at the original backend. Do not apply.
6. Run and save a baseline plan with the source engine on the copied state; then run candidate plan on an independent copy of that same baseline. Compare normalized actions, resource addresses, outputs, replacements, provider selections, and warnings.
7. Prefer an empty plan when the example is expected to be stable. If plans differ, classify each difference as **expected**, **unsafe**, or **unresolved** with evidence. Never suppress a difference just to get a green pipeline.
8. Keep original engine, state, config, keys, and rollback instructions available. Verify the rollback tool can read the retained original copy before changing production workflows.
9. Migrate one low-risk component after a human-reviewed change window and a rehearsed recovery plan.
10. Record versions, hashes, reviewers, test output, unresolved risks, owner, acceptance criteria, and post-migration drift checks.

An empty plan is useful evidence for one code/tool/provider/state combination. It is not proof of semantic equivalence across untested features, future versions, all providers, or later infrastructure changes. Never perform an in-place conversion of the only state copy.

#### Pulumi awareness: concepts, risk, and mapping

Pulumi lets infrastructure be described using general-purpose languages such as Python and TypeScript. A stack represents a deployment instance with configuration and state. `pulumi preview` previews proposed changes; `pulumi up` performs them. Component resources package multiple resources into reusable abstractions. State backend and login behavior, local backend syntax, encryption provider setup, provider bridging, and import/export features are version-sensitive and must be checked in current official documentation `[VERIFY]`.

| Terraform/OpenTofu concept | Pulumi analogue | Important non-equivalence |
|---|---|---|
| Provider | Provider package/plugin | Package APIs and resource lifecycle semantics differ; bridge support is not universal. |
| Resource | Resource | Similar purpose, but schemas, IDs, defaults, replacement rules, and import support may differ. |
| State file/backend | Stack state and backend | Format, encryption, history, access control, and migration mechanisms differ. |
| Module | Component resource / reusable package | Component resources are program abstractions, not a one-to-one module/state mapping. |
| Directory/workspace/environment | Stack plus program/config convention | A stack is not exactly equivalent to a Terraform workspace or directory. |
| Plan | Preview | Preview evaluates program code and dependencies; it is not a static HCL-only calculation. |
| `apply` | `up` | Approval and execution semantics differ; inspect the exact reviewed preview and state. |
| `sensitive` output | Secret configuration/value propagation | Secret marking/encryption behavior depends on backend and configuration; do not assume all logs/artifacts are safe. |

Risks to control: arbitrary code can execute during program evaluation/preview; dependencies may be fetched; unpinned packages and mutable sources can change behavior; package lifecycle scripts may run; code may make network calls or depend on time/randomness; secrets can leak into stack config/state/logs; language-level abstraction can make the effective resource graph harder to review. Mitigate with lock files, immutable versions, package allow-lists, isolated no-credential preview, network restrictions where practical, tests, secret scanning, reviewed generated outputs, and least-privilege apply identities.

### 9.5 Level 3 — Advanced

#### Tool comparison matrix

Ratings are intentionally qualitative and conditional; validate them against the actual team and versions. Terragrunt is a wrapper layer, OpenTofu is an engine, and Pulumi is a programming-language IaC platform—not interchangeable peers.

| Criterion | Terraform/OpenTofu | Terragrunt layer | Pulumi | Trade-off / verification note |
|---|---|---|---|---|
| Language expressiveness vs reviewability | Declarative HCL is structured and plan-oriented | Adds composition/indirection around HCL | General-purpose language enables richer abstractions and execution | Review the effective graph and rendered config/program. |
| Learning curve/hiring | HCL/IaC skills commonly map across teams; verify local market | Requires engine + wrapper knowledge | Requires language/runtime + IaC knowledge | Assess hiring and on-call depth in your market. |
| Testing ecosystem | Validation, plans, native tests vary by version | Tests wrapper resolution and multi-root orchestration too | Language tests plus IaC-specific testing | Verify exact test feature/version and integration cost. |
| Provider coverage/bridging | Engine-specific provider sources and schemas | Usually relies on underlying engine providers | Native providers and bridges for some ecosystems | Provider bridge coverage and parity `[VERIFY]`. |
| State/backend model | Engine state with backend/locking options | Usually retains underlying engine state per unit | Stack state and backend model | Recovery and access control differ. |
| Encryption/secrets | State often contains sensitive attributes; backend controls matter | Same underlying state risk plus generated files/logs | Secret handling/encryption depends on backend/config | Verify encryption, key custody, logs and exports. |
| Plan/preview reviewability | Explicit plan workflow | Must preserve per-unit plan identity and scope | Preview is useful but evaluates code | No plan should be approved without source/dependency provenance. |
| Drift detection/reconciliation | Plan/refresh-driven workflow | Orchestrates engine runs; not continuous reconciliation itself | Preview/update workflow; not automatically Crossplane-like reconciliation | Distinguish detection from continuous correction. |
| Policy ecosystem | External/native policy integrations vary | Wrapper can orchestrate gates but doesn't replace them | Policy options depend on platform/edition/tooling | Verify policy licensing and enforcement location. |
| CI/approval flow | Established plan/apply split patterns | Multi-unit pipeline requires per-component gates | Preview/up workflow with program build/test gates | Protect artifacts, identity, and approval scope. |
| Multi-cloud reality | Provider ecosystem can span clouds, but behavior varies | Helps hierarchy, not provider parity | Can span providers but code is not portability by itself | Portability requires tests and abstraction discipline. |
| Environment/region/account hierarchy | Directories, modules, variables, state boundaries | Hierarchy and shared config are core strengths | Stacks/config conventions, program abstractions | Avoid coupling prod to dev outputs/state. |
| Dependency handling | Resource graph within a state; cross-state links need explicit design | Cross-directory dependency/output orchestration | Program/resource dependencies and stack references | Verify cycle handling and bootstrap behavior. |
| Version coupling/upgrade burden | Engine + providers + modules + backend | Adds wrapper version and generated syntax | CLI + language runtime + packages + providers | Maintain a compatibility matrix and upgrade rings. |
| Community/vendor risk | Verify governance, support and security posture | Additional project dependency and maintainers | Project/vendor ecosystem and support options | Review current advisories and governance documents. |
| Licensing/governance | Check current official docs and internal policy `[VERIFY]` | Wrapper license plus underlying engine terms | Check current Pulumi and provider/package terms `[VERIFY]` | No licensing conclusion is asserted in this lesson. |
| Lock-in/exit cost | HCL/state/provider dependencies still create exit work | Adds wrapper conventions and generated config | Language code and state/resource translation can increase exit cost | State export/import support is not semantic translation `[VERIFY]`. |
| Debugging/operational complexity | Engine/provider/state debugging | More indirection and generated files | Program/runtime/package execution and state | Choose complexity the on-call team can diagnose. |
| Cost of abstraction | Lower for a simple repository | Justified only if duplication/ordering pain is real | Abstractions can improve reuse but obscure resource graph | Measure cognitive load and failure rate, not line count only. |
| Migration/rollback complexity | Depends on state/backend/provider changes | Wrapper migration adds orchestration/config migration | Cross-language and state translation may be substantial | Copy state, freeze writes, compare plans, preserve original tool. |

#### Migration playbooks

| Migration | Preconditions and inventory | Parallel-run / comparison | Acceptance criteria | Rollback and exit criteria |
|---|---|---|---|---|
| Terraform → OpenTofu (or reverse) | Freeze writes; inventory versions, provider/module sources, lock files, backend, state and feature use; review current official docs | Independent state copies; source-engine baseline plan; candidate plan; compare resource actions, outputs, provider selections and warnings | Empty plan or every divergence classified and accepted; restore test passes; approved owner and change window | Restore original code/lock/state/tool; no apply on unexpected differences; stop if state encryption/format unclear. |
| Plain Terraform/OpenTofu → Terragrunt | Inventory roots, state boundaries, shared settings, CI paths, module source pins, dependency edges and current apply process | Run wrapper only against scratch copies; compare resolved directories/config and individual plans to baseline | Same intended resources/actions, clear unit ownership, per-unit approval, documented debug/runbook | Revert wrapper config and use original roots/state; do not move state unless separately planned. Exit if indirection outweighs reduced duplication. |
| CloudFormation → Terraform via import (awareness) | Inventory stack/resources/immutable IDs/unsupported types/retention and drift; CloudFormation remains owner until explicit handoff | Build HCL; import existing resources into a new isolated state following current import docs; plan without apply; compare properties | Reviewed import map; no unintended create/replace/delete; CloudFormation ownership and stack policy reviewed | Keep CloudFormation as owner until acceptance; remove competing management only after verified handoff. No real-cloud lab here. |
| Terraform/OpenTofu → Pulumi or CDKTF | Inventory resource schemas, IDs, provider behavior, state backend, language dependencies, secret values and import limits | Translate code, import/adopt resources in copied/test state where supported, compare preview/plan and properties | Every resource has one owner; import/translation gaps documented; preview is reviewed and regression tests pass | Restore original tool/state and ownership; no dual management. State translation/import support and limits `[VERIFY]`. |

Each migration must name: **change owner**, state owner, security reviewer, operational reviewer, change window, stop conditions, evidence location, rollback operator, and post-change monitor. A “parallel run” means comparison on isolated copies or read-only observation—not two tools applying the same live resource.

#### Multi-tool ownership boundary

```text
Organization / account boundary
├── Terraform/OpenTofu state A: network foundation (owner: platform team)
├── Terraform/OpenTofu state B: storage metadata (owner: data platform)
├── Pulumi stack C: app-owned service resources (owner: service team; separate resources)
└── Crossplane control plane: explicitly scoped managed resources (Unit 12)

Handoff protocol: freeze writer → inventory IDs/properties → backup/export → import/adopt
→ compare plan/preview → approve owner switch → disable old writer → monitor drift.
```

**Rule:** two IaC tools/states must not concurrently manage the same resource. Distinct tools can coexist if ownership boundaries are explicit at resource ID, state, provider identity, and lifecycle level. A tool that merely reads outputs is not automatically an owner, but data-source/API side effects still require review. Before handoff, identify which system controls updates, deletion, tags, defaults, and drift correction. Import/adoption is not the same as a safe ownership transfer; verify the destination's semantics and rollback limitations.

#### Version-upgrade governance

| Ring | Scope | Required evidence | Promotion gate | Rollback trigger |
|---|---|---|---|---|
| 0 — sandbox | Provider-free fixture and copied state | Binary path/version, init, validate, tests, plan diff, state read/restore test | No unexplained plan/state change; docs reviewed | State unreadable, unexpected replacement, dependency drift |
| 1 — dev | One low-risk component | Integration tests, logs, plan/preview evidence, recovery rehearsal | Owner + reviewer approve; no critical open item | New drift, runtime error, policy regression |
| 2 — staging | Representative environment/region | Consumer matrix, rate-limit/timeout checks, audit and rollback drill | SRE/security/platform approval as applicable | Error budget impact or non-reproducible plan |
| 3 — production | Small cohort first, then wider fleet | Change record, pinned artifacts, owner confirmation, monitored post-apply checks | Explicit change approval and rollback operator | Any unexplained destructive diff, state-format concern, or failed verification |

Rollout checklist: pin engine/wrapper/provider/module/language-package versions; update lock files in a pull request; generate a plan-diff matrix across consumers/environments; run regression and policy tests; check state/backend compatibility; preserve old binary and original state; update CI image and provenance; test rollback; promote in rings; monitor change-failure rate, plan drift, provider/API errors, and lock contention. Dependabot/Renovate-style automation is awareness only: configure it to propose changes for review, not to auto-apply infrastructure `[VERIFY]`.

### 9.6 Level 4 — Expert

#### Fleet governance and operational contracts

A multi-team platform should maintain a toolchain manifest for each supported path: engine/wrapper versions, provider/module versions, language runtime, lock-file policy, backend, state owner, plan artifact format, secret handling, test suite, supported migration direction, and EOL response. The manifest is not proof that combinations work; the compatibility test matrix is the evidence. Treat each tool upgrade as a controlled code change with a rollback path that does not depend on the new tool successfully reading the state.

Vendor/community risk review should monitor release cadence, security advisories, maintainers, compatibility policy, issue response, dependency health, governance/licensing documents, and credible exit paths. This lesson makes no current assertion about any project's governance or licensing. Legal/procurement teams should review current primary documents before adoption. A fork or alternative engine can reduce one class of dependency while adding another maintenance and compatibility burden.

#### Failure scenarios: diagnosis before remediation

For every incident, first assert the blast radius and rollback path. Do not “fix forward” by applying another broad command while ownership or state identity is uncertain.

| Symptom | Hypothesis and test | Root cause pattern | Safe fix / prevention |
|---|---|---|---|
| Wrong account/environment in plan | Print identity, backend key, directory, inputs and resource addresses; compare to change record | Generated config or inherited environment selected wrong target | Abort; restore intended identity/config; add explicit target assertions and negative tests. |
| Dependency output missing | Inspect producer state/output schema and dependency path | Typo, producer not applied, stale mock, wrong directory | Plan-only diagnosis; fix contract and rerun producer/consumer plans separately. |
| Candidate engine can't read state | Work only on copy; capture tool/version and state metadata; inspect official compatibility notes | Unsupported format/encryption/config or version boundary | Stop; restore original copy; use source tool; design migration with documented conversion, never overwrite sole copy. |
| Plan differs after wrapper upgrade | Compare rendered config, source digest, engine version, inputs and per-unit plan | Changed merge/source/CLI semantics or mutable module source | Pin and revert wrapper/config; stage upgrade with matrix testing. |
| Preview triggers unexpected network/process activity | Run in no-credential sandbox with controlled network and verbose audit logs | Arbitrary program code/package lifecycle behavior | Quarantine dependency, rotate exposed credentials if any, rebuild from trusted lock, constrain egress and package sources. |

#### Five required incident analyses

**Incident 1 — `run-all apply` applies a half-reviewed change across ten accounts/modules**

- **Symptoms/timeline:** A broad multi-unit command begins; several modules change before a reviewer notices that one account's plan was never reviewed. Alerts show unexpected resource modifications across environments.
- **Detection gap:** Approval attached to a parent PR but not to each resolved unit/plan; no scope assertion or per-account inventory in the apply job.
- **Root cause:** The orchestration command's blast radius exceeded the review boundary; the team treated a multi-directory run as one atomic transaction.
- **Immediate containment:** Stop queued/future jobs; do not blindly interrupt an in-flight provider operation without assessing partial-apply risk. Identify completed/in-flight units and state locks. Freeze writes for affected states, preserve logs and plan artifacts, and involve each state owner.
- **Durable fix:** Enumerate units first; produce per-unit plan artifacts; require target environment/account assertions, policy checks, and per-unit approval. Apply only the approved artifact for the intended unit. Restrict multi-unit applies to an explicitly approved runbook.
- **Evidence/regression test:** CI fixture with ten synthetic units where an unreviewed unit blocks promotion; artifact lists commit, state identity, unit, tool versions and digest.
- **Owner/residual risk:** Platform CI owner; residual risk includes provider operations that partially succeeded before interruption and must be reconciled state by state.

**Incident 2 — Mock outputs leak into a real apply and conceal a missing dependency**

- **Symptoms/timeline:** Consumer plan succeeds despite producer output being unavailable; apply records a placeholder or incorrect reference.
- **Detection gap:** Mock values look structurally valid and there is no sentinel or apply-mode restriction.
- **Root cause:** A test convenience became an operational input.
- **Immediate containment:** Stop further consumer changes; inspect actual resource state and downstream effects; preserve state and plan; identify whether the placeholder created a real object or invalid configuration.
- **Durable fix:** Restrict mocks to explicit plan/test commands; fail CI when sentinel values appear in plan inputs/outputs; require real producer state and a contract test. Use a distinct mock value that cannot be mistaken for production data.
- **Evidence/regression test:** Test proves apply job fails with mock sentinel and with missing producer state; mock configuration and allowed command list are reviewed against pinned Terragrunt docs `[VERIFY]`.
- **Owner/residual risk:** Component owner; residual risk remains if a real output happens to resemble the sentinel or is incorrectly typed.

**Incident 3 — OpenTofu/Terraform divergence breaks a shared module**

- **Symptoms/timeline:** A module validates under one engine but fails init/test/plan under the other; CI or a developer reports provider resolution or expression behavior differences.
- **Detection gap:** Compatibility was inferred from shared HCL and a single empty plan.
- **Root cause:** The module uses an engine-specific feature, provider source, test syntax, or state behavior not included in the compatibility matrix.
- **Immediate containment:** Stop promotion and writes; preserve original engine/state; reproduce on copies and pin binaries/dependencies.
- **Durable fix:** Define supported engine/version combinations, run a test matrix for features used, classify divergences, and require explicit module compatibility metadata. Do not advertise parity that is not tested.
- **Evidence/regression test:** A fixture exercises the divergent feature and CI fails for unsupported combinations; lock-file and provider-source diffs are retained.
- **Owner/residual risk:** IaC platform owner; residual risk includes future upstream divergence and providers whose compatibility is independently maintained.

**Incident 4 — Tool upgrade changes state behavior/format and blocks rollback**

- **Symptoms/timeline:** New tool writes or expects state that the old binary cannot safely read; rollback pipeline fails after an upgrade.
- **Detection gap:** Upgrade changed production state before a rollback test; backups existed but restore was not rehearsed with the old binary.
- **Root cause:** Rollback was treated as a code revert rather than a tool/state compatibility operation.
- **Immediate containment:** Freeze writes; preserve the exact current state and all backups; do not attempt repeated state pushes/conversions. Identify the last known readable snapshot and tool versions with a specialist owner.
- **Durable fix:** Test upgrades against copied state; check state format and encryption docs; verify old-tool restore/read on a copy; gate production on an explicit state compatibility test and rollback rehearsal.
- **Evidence/regression test:** CI creates a scratch copy, tests candidate and rollback binary, and records checksums and outcomes; no test touches production backend.
- **Owner/residual risk:** State owner; residual risk includes unsupported cross-version conversions and loss of encryption keys/configuration.

**Incident 5 — Pulumi program fetches a compromised dependency during preview/program execution**

- **Symptoms/timeline:** Preview invokes package resolution or program code; unexpected network destination or process appears, or a dependency alert is raised.
- **Detection gap:** Preview was treated as static and safe; dependency was unpinned and CI had broad network/credential access.
- **Root cause:** Program evaluation and dependency installation are executable supply-chain surfaces.
- **Immediate containment:** Stop pipeline; revoke/rotate any credentials that may have been exposed; preserve logs and dependency lock files; isolate runner and assess artifact provenance.
- **Durable fix:** Pin dependencies and verify checksums where supported; use approved registries, isolated preview without write credentials, network egress restrictions, dependency scanning, signed/reproducible builds where available, and least-privilege apply identity.
- **Evidence/regression test:** A malicious test package is blocked in an isolated fixture; preview runner has no cloud write credentials and logs package provenance.
- **Owner/residual risk:** Build/security owner; residual risk includes transitive dependency compromise and runtime behaviors not captured by static scanners.

#### ADR template

Use this template for any toolchain decision. Replace subjective values with team evidence; scores are not universal benchmarks.

```markdown
# ADR-<ID>: <Toolchain decision>
- Status: Proposed | Accepted | Superseded
- Date / Review date:
- Decision owner / reviewers:

## Context and constraints
- Organization/team profile:
- Workload, environments, accounts, regions:
- Required reviewability, security, recovery and compliance controls:
- Skills, support capacity, CI and cost constraints:

## Requirements and non-goals
- Must / should / won't:
- Explicitly out of scope:

## Options considered
- Plain Terraform/OpenTofu conventions:
- Terraform/OpenTofu + Terragrunt:
- Pulumi:
- Other candidates:

## Criteria and weighted scores
- Criterion | Weight | Option score | Evidence | Confidence/assumption
- Explain weight normalization and uncertainty.

## State/resource ownership
- State/backend per component:
- Resource ownership map:
- No-dual-management rule and handoff process:

## Security and operations
- Identity, secrets, policy, plan/preview approvals, artifact handling:
- Tool/provider/module/runtime pinning and upgrade rings:
- Observability, incident owner, rollback:

## Migration and exit plan
- Preconditions, trial, acceptance, rollback, estimated effort:
- State export/import and translation limitations:
- Revisit triggers and date:

## Consequences
- Benefits, costs, risks accepted, unresolved verification items:
```

#### Lab 4 — Filled ADR (fictional profile)

**Profile:** Small data/ML platform team; strong Python skills, moderate HCL experience; three environments; multiple accounts; strict plan review; modest on-call capacity; local-cost-safe training requirement. All scoring is `[ASSUMPTION]` and should be revisited with hiring data and internal support requirements.

| Criterion | Weight | Plain Terraform/OpenTofu conventions | Engine + Terragrunt | Pulumi | Rationale / uncertainty |
|---|---:|---:|---:|---:|---|
| Reviewability | 15 | 5 | 4 | 3 | `[ASSUMPTION]` HCL plan workflow is familiar; wrapper and program execution add review surfaces. |
| Reuse / hierarchy | 12 | 3 | 5 | 4 | `[ASSUMPTION]` shared config and code abstractions differ. |
| Dependency orchestration | 10 | 2 | 5 | 4 | `[ASSUMPTION]` multi-root orchestration is a current pain point. |
| Testing | 10 | 4 | 4 | 5 | `[ASSUMPTION]` language testing may fit Python team but IaC semantics still need tests. |
| Learning / hiring | 8 | 4 | 3 | 4 | Must validate against local hiring and on-call coverage. |
| State risk / recovery | 12 | 4 | 4 | 3 | State models and migrations require direct testing; not a factual ranking. |
| CI / approvals | 10 | 5 | 4 | 4 | Per-unit plan identity must be engineered for wrapper path. |
| Policy / governance review | 7 | 4 | 4 | 3 | Exact policy/licensing capabilities require current documentation. |
| Operational burden | 8 | 5 | 3 | 3 | One more tool/runtime increases support surface. |
| Lock-in / exit cost | 8 | 4 | 3 | 2 | `[ASSUMPTION]` translation from language programs may cost more. |

**Decision:** Keep Terraform/OpenTofu engine conventions as the baseline and trial Terragrunt only for the multi-root hierarchy where duplication/dependency cost is documented. Do not adopt Pulumi as the default platform in this phase; allow a separate time-boxed evaluation for teams whose language abstractions materially improve their workflow. This is a decision for the fictional profile, not a universal recommendation. The engine choice remains subject to current licensing/governance and compatibility review `[VERIFY]`.

**Ownership:** One state owner per component/environment. No resource may be managed by both engine state and Pulumi/Crossplane simultaneously. Cross-tool handoff requires write freeze, inventory, backup, import/adoption proof, plan comparison, owner switch, and disablement of the previous writer.

**Controls:** Pin binaries, providers, modules and language packages; review lock-file changes; promote sandbox → dev → staging → production; require a reviewed plan/preview, policy checks, identity assertions and explicit approval; apply only the reviewed artifact where supported; retain original state/tool and rehearse rollback. Revisit if wrapper debugging costs exceed saved effort, engine compatibility diverges, hiring/ownership changes, or migration/exit costs become unacceptable. Review date: six months after adoption or after a major engine/wrapper policy change.

### 9.7 SRE lens

#### SLIs/SLOs and operating signals

| Signal | Definition | Use |
|---|---|---|
| Infrastructure change failure rate | Failed or rolled-back changes / total changes, with agreed classification | Detect unsafe upgrade or orchestration patterns. |
| Plan-to-apply elapsed time | Time between reviewed plan and execution | Long gaps increase stale-plan risk; policy must define when replanning is required. |
| Plan divergence rate | Approved plans that differ from later recomputation or execution expectations | Detect mutable sources, changing state, and weak artifact identity. |
| Drift count/age | Detected differences grouped by severity and time unresolved | Distinguish urgent ownership drift from low-risk changes. |
| State lock contention | Lock wait/failure frequency by state | Detect oversized state, pipeline overlap, or poor ownership boundaries. |
| Policy violation rate | Violations per plan and repeat offender category | Detect governance gaps and noisy policies. |
| Recovery time for state incident | Time to restore readable, reconciled state and resume safe changes | Validate backup/rollback quality. |
| Toolchain upgrade failure rate | Failed promotions by version ring | Tune test matrix and rollout pace. |

#### Runbook snippet: unexpected plan or apply

1. **Alert:** plan includes unexpected delete/replace, wrong account, missing dependency, or state read error.
2. **Triage:** pause promotion; identify exact binary, directory, state key, commit, module/package versions, identity, and plan artifact. Do not run a broad apply or state surgery.
3. **Blast-radius check:** enumerate affected units/resources and any in-flight jobs; freeze writes to those state boundaries; capture logs and plan artifacts with secrets redacted.
4. **Mitigate:** revert source/wrapper version if state remains compatible; restore only a verified state backup when justified; do not restore state without reconciling actual infrastructure.
5. **Recover:** test the recovery plan on a copy, then have the state owner approve the smallest safe action. Check provider API and eventual-consistency behavior.
6. **Follow-up:** add regression tests, update the compatibility matrix, and review whether the failure was caught by the intended policy/approval gate.

#### Cost and capacity notes

Terragrunt can increase parallel API activity; Pulumi programs can increase runtime and dependency installation needs; provider initialization and test matrices consume CI minutes. Optimize only after measuring latency and failure modes. Caches should be keyed by immutable dependency inputs. A low-cost local lab is useful for logic and workflow, but cannot validate cloud quotas, IAM propagation, provider API behavior, or real-cloud state backend semantics.

### 9.8 Security lens

| Threat | Concrete control | Verification evidence |
|---|---|---|
| State/plan/stack secrets leak | Restrict storage/artifacts; encrypt backend; sanitize outputs; never commit state/plans | Repo secret scan; artifact ACL review; inspect sample state in scratch only; access log review. |
| State tampering or wrong backend | Separate state roles, locks, backend identity assertions, versioned backups | CI checks expected backend/key; test lock behavior and restore procedure. |
| Overprivileged apply pipeline | Separate read/plan identity from write/apply identity where practical; short-lived credentials | Inspect role policy and job permissions; negative test proves plan job cannot mutate. |
| Wrong account or region | Explicit environment/account assertions before plan and apply | Intentionally wrong target must fail before provider mutation. |
| Compromised provider/module/package | Pin versions/sources, review lock-file changes, scan dependencies, restrict registry/egress | Dependency inventory, lock diff, allow-list, provenance records. |
| Terragrunt hook abuse | Review hook commands, arguments, env, filesystem/network access and failure behavior | Hook allow-list, unit test, logs, least-privilege runner. |
| Pulumi program executes unexpected code | No cloud write credentials during preview; isolate runtime; restrict network; inspect package lifecycle scripts | Sandbox log/egress test and dependency lock review. |
| Mock values reach apply | Command restriction plus sentinel-based CI gate and producer-state check | Test apply pipeline rejects sentinel/missing producer. |
| Same resource has two owners | Ownership registry and handoff checklist; prohibit duplicate IDs across states | Periodic inventory/state reconciliation and duplicate-owner report. |
| Generated config points to wrong target | Render/inspect config and assert backend/provider identity | Test with intentionally wrong target; job must fail. |
| Secret configuration committed | Use supported encrypted secret mechanism and external secret manager for high-value secrets | Repo scanner, access review, rotation plan; verify encryption key recovery. |
| Destructive change abuse | Policy gate, reviewed plan artifact, narrow approvals, break-glass log | Negative plan tests for delete/replace and audit trail. |

What this unit does **not** provide: a complete cloud IAM design, legal compliance determination, proof of encryption configuration, or proof that any provider is free of vulnerabilities. Those require current official documentation and organizational controls. Do not put credentials, account IDs, production resource names, tokens, or real secret values in examples or evidence.

### 9.9 Production checklist

- [ ] The team can explain whether each selected tool is an engine, wrapper, language runtime, or controller.
- [ ] Exact binary paths and versions are recorded in CI logs and change evidence.
- [ ] Provider, module, wrapper, language package, and runtime versions are pinned or constrained by an explicit reviewed policy.
- [ ] Lock-file changes are reviewed and not regenerated casually during migration.
- [ ] Every component/environment has a named owner and state/backend boundary.
- [ ] A resource ownership registry prevents two tools/states from managing the same resource.
- [ ] Backend identity and target environment/account are asserted before plan and apply/up.
- [ ] Plan/preview output is reviewed before state-changing actions; unreviewed differences block apply.
- [ ] The exact reviewed plan artifact and its commit/tool/source/state identity are preserved where supported.
- [ ] Terragrunt multi-unit commands enumerate scope; per-component plans and approvals are required.
- [ ] Mock outputs are restricted to documented plan/test scenarios and are rejected by apply gates.
- [ ] Generated configuration and hooks are inspected and treated as executable inputs.
- [ ] Parallelism/caching settings are tested for rate limits, eventual consistency, and invalidation behavior.
- [ ] OpenTofu/Terraform compatibility is documented for actual features used, not inferred from syntax similarity.
- [ ] Pulumi preview runs with least privilege; dependency and program execution risks are reviewed.
- [ ] State, plans, stack files, logs, and artifacts are protected as potentially sensitive.
- [ ] State backup, restore, and rollback are tested with the intended old and candidate tools on copies.
- [ ] Upgrade rings and promotion gates are documented; no automatic infrastructure apply from dependency bot PRs.
- [ ] Current licensing/governance/security documents have been reviewed by the appropriate human owner.
- [ ] Incidents have runbooks, on-call owners, rollback conditions, and evidence retention.
- [ ] Toolchain exit strategy and revisit triggers are recorded in an ADR.

### 9.10 Hands-on lab set

All labs are local-only/simulated. **Real-cloud touch: No.** Use `scratch/unit9/` outside the repository. Do not use real credentials or production state. Commands and outputs that have not been run are explicitly labelled illustrative. The optional Pulumi lab uses the guided Path B because its exact local backend syntax has not been independently verified in this artifact.

#### Lab 1 — Terragrunt DRY layout, dependencies, and debugging failure

**Goal:** See how shared configuration and cross-directory dependencies reduce repetition while adding indirection. **Substrate:** local-only, provider-free `terraform_data`; **real cloud:** No. **Prerequisites:** Git, Terraform/OpenTofu and Terragrunt binaries pinned by the learner; exact versions recorded. **Resource budget:** small; no cluster/emulator needed.

**Files:** Use the `modules/storage-metadata/main.tf`, `modules/catalog-consumer/main.tf`, `live/root.hcl`, and two `terragrunt.hcl` examples in §9.4. Save them under `scratch/unit9/terragrunt-demo/`. Add an explicit `versions.tf` with your verified engine baseline and avoid backend blocks that point outside local scratch state. The example root/module paths are illustrative; correct relative paths after inspecting the actual directory.

**Procedure:**
1. Record `pwd`, `command -v terraform`, `terraform version`, `command -v terragrunt`, and the corresponding version output. If using OpenTofu, record `command -v tofu` and `tofu version` separately.
2. Copy the scratch fixture and verify its files. Use only the local backend; do not inherit a cloud profile or backend from your shell.
3. Run the pinned Terragrunt release's documented single-unit init/validate/plan command. Do not assume the CLI syntax; verify it first `[VERIFY]`.
4. Plan storage first. Inspect resource addresses, output names, and state directory. Apply only the provider-free plan after confirming it is limited to the scratch marker.
5. Plan the catalog consumer with real dependency output. Record the dependency output and per-unit plan evidence.
6. Introduce a deliberate defect: change `dependency.storage.outputs.metadata_id` to a nonexistent output key. Re-run plan and capture the failure. Do not add a mock to make the error disappear.
7. Diagnose in this order: working directory, resolved source path, producer output declaration/state, consumer input name/type, rendered/generated config, tool versions.
8. Restore the correct key. Separately test a mock sentinel only in a plan/test scenario; verify the apply workflow rejects the sentinel. The exact mock-allowlist key is release-sensitive and must be checked in official Terragrunt docs.
9. Compare with plain engine conventions: two explicit root directories, shared local module, pinned source, and per-component CI jobs. Write which duplicated lines Terragrunt removes and which debugging steps it adds.

**Expected evidence (illustrative, not executed):** version inventory; tree; producer plan/output; consumer plan; failed-plan diagnostic for missing output; corrected plan; mock-sentinel rejection; decision note comparing wrapper vs plain conventions.

**Cleanup/recovery:** inspect plans before any destroy; destroy only the two provider-free scratch components in dependency-safe order; verify empty plans and no leftover state/backend files beyond scratch. If path/state identity is uncertain, stop and remove only the scratch directory after preserving evidence—never point cleanup at a shared backend.

**Failure injection:** wrong source path, wrong output key, stale mock value, and wrong working directory. **Abort conditions:** unexpected provider, remote backend, non-scratch path, destructive action beyond the local marker, or unknown tool version.

**Limitations:** no real cloud provider, API rate limit, remote backend, or Terragrunt version behavior is proven by the provider-free fixture.

#### Lab 2 — Terraform ↔ OpenTofu compatibility on a copied state

**Goal:** Practice evidence-based compatibility assessment, not prove universal equivalence. **Substrate:** local-only provider-free resource; **real cloud:** No. **Prerequisites:** both tools if available; otherwise perform the inventory and comparison design as a guided lab and mark unavailable tool tests `OPEN`.

**Safety plan before state changes:** (1) verify scratch path and both binary paths/versions; (2) create an isolated directory with no inherited cloud backend; (3) copy code and state separately for each tool and compute checksums; (4) record abort conditions; (5) preserve original tool/state untouched; (6) no apply after candidate migration. State files may be sensitive even in a local lab.

**Procedure:**
1. Create the provider-free configuration from §9.3 and initialize with the source engine. Save a baseline plan and state snapshot. Record the provider/module inventory and lock-file digest.
2. Make two independent copies: `source-copy/` and `candidate-copy/`. Verify state checksums and directory paths. Do not let both point at one backend.
3. Record exact binary paths and versions, OS, registry settings, lock file, backend configuration, and feature usage. Confirm there are no real credentials.
4. On the source copy, run init/validate/plan with the source engine. Save output and classify all actions.
5. On the candidate copy, use the candidate tool's documented initialization and migration workflow only after checking current official docs `[VERIFY]`. Do not use undocumented state conversion flags. If candidate initialization requires modifying state, stop and preserve a second backup before proceeding.
6. Run candidate plan without apply. Compare resource actions, resource addresses, outputs, provider selections, state read/write warnings, lock file changes, and any encryption configuration.
7. Classify each difference: **expected** (documented and accepted), **unsafe** (could change resources or state recovery), or **unresolved** (insufficient evidence). Unexpected differences block apply.
8. Check current official documentation for registry endpoints, provider/module sourcing, state compatibility/encryption, early variable/locals evaluation, provider-defined functions, and test framework syntax. If a feature is unused in the sample, mark it “not exercised” rather than declaring it compatible.
9. Restore the source copy and verify the source tool can read it. Keep the candidate copy separate. Document a hypothetical rollback and acceptance criteria for one low-risk component.

**Illustrative evidence table — not executed:**

| Check | Source tool | Candidate tool | Result |
|---|---|---|---|
| Binary path/version | Recorded from local command | Recorded from local command | Must be exact, not inferred |
| Config validation | Output saved | Output saved | PASS only if expected |
| Plan actions | Baseline saved | Candidate saved | Empty plan or explained differences |
| Provider/module resolution | Lock/source inventory | Lock/source inventory | Any unresolved source blocks migration |
| State readability/restore | Source copy readable | Candidate copy readable on its own copy | No writes to original |
| State encryption | Existing configuration recorded | Candidate support/config verified | If unclear, STOP |
| Rollback | Original snapshot retained | Candidate discarded/isolated | Original tool must read retained copy |

**Expected evidence:** version inventory, checksums, source baseline, candidate plan, divergence table, verification sources, rollback checklist, and explicit statement of what was not exercised. **Cleanup:** delete candidate copies only after preserving sanitized evidence; never delete the original source fixture before restore proof. **Abort:** unexpected plan, unknown state format, unavailable encryption key, or candidate requiring unreviewed mutation. **Limitations:** one provider-free example cannot establish provider parity, production state compatibility, or future version behavior.

#### Lab 3 — Pulumi optional local walkthrough (Path B)

**Path chosen:** guided walkthrough, because exact local backend command/behavior is not independently verified here. **Substrate:** conceptual/local-only; **real cloud:** No; **no cloud login and no `pulumi up` required.** If you choose to run a local backend later, first verify current Pulumi docs for local backend setup, encryption provider, and stack configuration.

Illustrative layout:

```text
scratch/unit9/pulumi-demo/
├── Pulumi.yaml
├── requirements.txt
├── __main__.py
└── README.md
```

Illustrative `Pulumi.yaml` (syntax is a teaching example; verify current schema):

```yaml
name: local-metadata-demo
runtime: python
description: Local-only conceptual resource graph; no cloud provider configured
```

Correct any schema validation issue using the current official schema before running. Illustrative `requirements.txt`:

```text
# Pin a reviewed, currently supported version in an actual lab.
# Do not install unpinned packages or copy a made-up version here.
pulumi
```

Illustrative `__main__.py` — shows a component/resource concept, not an executable local resource:

```python
"""Guided example only: no cloud provider and no real resource creation."""
import os

# Program evaluation is executable code. Avoid network calls, secrets, and
# non-deterministic inputs in preview. This sample intentionally does not
# import a cloud provider or create a resource.
environment = os.environ.get("DEMO_ENV", "dev")
if environment not in {"dev", "staging", "prod"}:
    raise ValueError("DEMO_ENV must be an approved environment")

# In a real Pulumi program, a ComponentResource groups child resources.
# Exact constructors and exports depend on the chosen provider/package.
print(f"Illustrative preview graph: environment={environment}")
```

**Guided sequence:**
1. Inspect current official Pulumi docs for project schema, stack semantics, local backend login syntax, config/secrets, and component resources. Record the exact version and source section. Do not infer that `pulumi login --local` is valid for your installed version without verification `[VERIFY]`.
2. Explain the difference between program evaluation, preview, and up. Preview evaluates code and dependencies; it is not a safe sandbox by itself.
3. Choose a local backend only after verification. Create a disposable stack with no cloud provider and no real secrets. If any setup would require cloud login, stop and use this guided path.
4. Configure a non-secret value such as `environment=dev`. Discuss secret config as a concept only; do not put a fake secret in source control and do not treat encryption-at-rest as permission to expose stack files.
5. Run preview only after reviewing program and dependencies. **Illustrative expected output — not executed:**

```text
[ILLUSTRATIVE EXPECTED OUTPUT — NOT EXECUTED]
Preview summary:
  environment: dev
  cloud resources: none
  program side effects: none expected in this reviewed example
  action: no infrastructure mutation requested
```

6. Do not run `up` for this code: it intentionally creates no infrastructure. In a verified local-backend lab with a genuine local resource, inspect preview, approve only the local resource, then run `up` and cleanup using current documented commands.
7. Discuss component resources as reusable program abstractions and map them to Terraform modules only as an analogy. Identify language package lock files, dependency provenance, program side effects, secrets, and stack state as review artifacts.

**Expected evidence:** current-doc verification checklist; stack/backend choice (or documented reason not run); source review; illustrative preview labelled not executed; concept mapping; dependency-risk review; cleanup plan. **Recovery:** if a stack points to a remote backend or provider, stop and do not run up; preserve only sanitized logs. **Limitations:** no Pulumi command or local backend behavior is claimed to have been executed here.

#### Lab 4 — Written toolchain ADR

**Goal:** Defend a toolchain choice with explicit assumptions. **Substrate:** written/simulated; **real cloud:** No.

1. Read the fictional profile and filled ADR in §9.6.
2. Replace at least three `[ASSUMPTION]` scores with evidence from your team: skill inventory, number of roots, duplicate configuration count, incident history, CI time, and support capacity.
3. Score plain engine conventions, engine + Terragrunt, and Pulumi using weighted criteria. Document score confidence and a sensitivity check: does the winner change if reviewability or operational burden is weighted twice as heavily?
4. Define a state ownership map for storage, network, identity, and application service resources. Include explicit “not selected” options.
5. Specify pinned versions, upgrade rings, plan/preview gate, approval scope, artifact identity, rollback owner, exit plan, and revisit triggers.
6. Have a peer challenge the ADR with at least three objections: “why not just native modules?”, “how will we debug the wrapper at 02:00?”, and “what is the state handoff if we leave this tool?” Record the response and residual risk.

**Evidence:** filled ADR, weighted matrix, ownership diagram, dissent/objection log, and verification items. **Cleanup:** none. **Failure injection:** adjust weights and document whether decision changes. **Limitations:** subjective scores are not market benchmarks or proof of technical compatibility.

#### Additional short exercise — upgrade-ring tabletop

Create a synthetic compatibility matrix with rows for sandbox/dev/staging/prod and columns for engine, wrapper, provider, module, language runtime, plan result, tests, rollback proof. Inject one failed test in staging and explain why production promotion blocks. Evidence is the completed matrix and rollback decision. No infrastructure is created.

### 9.11 Self-check questions

1. **Why is Terragrunt not an alternative engine in the same category as OpenTofu?** — It orchestrates/configures underlying Terraform/OpenTofu units; state and provider semantics remain with the engine. Wrong answer temptation: both are invoked from a CLI, but CLI presence does not define architecture.
2. **What does an empty candidate-engine plan prove?** — Only that the tested code/tool/provider/state combination proposes no changes under the observed conditions. It does not prove universal parity. Tempting wrong answer: “shared HCL means identical behavior.”
3. **Why can mock outputs be dangerous?** — They can hide missing producers or wrong output contracts and can contaminate a real apply if not gated. Tempting wrong answer: “the type matched, so the value is real.”
4. **What must be reviewed before a multi-directory apply?** — Enumerated target units, environment/account assertions, per-unit plans/policy/approvals, tool/source identity, and rollback. Tempting wrong answer: “one approval on the parent PR is sufficient.”
5. **What is the safe way to compare Terraform and OpenTofu?** — Freeze writes, copy code/lock/state, run source and candidate plans on independent copies, classify differences, and retain original rollback path. Tempting wrong answer: switch the production binary and see what happens.
6. **Why can Pulumi preview still be a security surface?** — Program evaluation and dependency resolution may execute code or network actions. Tempting wrong answer: preview never mutates infrastructure, therefore it cannot be risky.
7. **Can two tools manage the same real resource if they use different state files?** — No; competing writers can overwrite settings, misinterpret drift, or delete resources. Tempting wrong answer: separate state files provide isolation automatically.
8. **When should a team avoid adding Terragrunt?** — When duplication is small, native conventions suffice, or the team cannot debug and govern another layer. Tempting wrong answer: DRY is always better regardless of operational cost.
9. **What is required to promote an engine upgrade?** — Version-pinned evidence, consumer plan/test matrix, state compatibility/restore check, explicit approvals, and rollback rehearsal. Tempting wrong answer: passing validation alone proves runtime compatibility.
10. **What is the most important exit-cost question?** — Can the team reconstruct ownership, state, resource IDs, secret/config semantics, and behavior under the destination tool without dual management? Tempting wrong answer: state export/import is equivalent to translating all resource semantics.

### 9.12 Evidence artifacts

Save only sanitized evidence in the learner's designated evidence folder, not in the repository's IaC state directories:

- `unit9-toolchain-inventory.md`: OS, exact binary paths/versions, registry/runtime settings, and unavailable tools.
- `unit9-terragrunt-tree.txt`: scratch layout and source pins.
- `unit9-terragrunt-plans/`: sanitized per-component plan summaries, dependency outputs, and failure/recovery evidence; never commit raw plan/state files if they can contain secrets.
- `unit9-mock-guard-test.md`: mock-sentinel rejection evidence and the exact version-specific setting verified.
- `unit9-engine-compatibility.md`: source/candidate version inventory, checksums, divergence table, source references, acceptance/rollback decisions.
- `unit9-pulumi-walkthrough.md`: local backend verification or reason not executed, preview sample labelled correctly, dependency/secret risk analysis.
- `unit9-toolchain-adr.md`: filled ADR, weighted criteria, ownership boundaries, objections and revisit triggers.
- `unit9-upgrade-matrix.csv`: synthetic upgrade-ring results and promotion decision.
- `unit9-incident-playbooks.md`: five incident records with owner and residual risk.
- `unit9-verification-checklist.md`: every open `[VERIFY]` item, official document/section checked, reviewer, date, evidence, and migration-blocking status.

Do not save credentials, account IDs, production resource names, plaintext secrets, raw state, unprotected plan files, or stack configuration containing sensitive values. Redaction must be reviewed; do not assume that `sensitive` flags automatically redact all artifacts.

### 9.13 Common interview and design-review questions

1. **You have 40 nearly identical roots across three environments. Would you adopt Terragrunt?**
   **Model answer:** First measure duplication, ordering failures, and operational pain. Prototype the wrapper on isolated copies; verify per-unit plans, dependency contracts, generated configuration, source pinning, and CLI/version behavior. Adopt only if reduced repetition exceeds the new debugging and upgrade cost. Keep plain engine conventions as the fallback.

2. **A team proposes switching from Terraform to OpenTofu because “the code is compatible.” What evidence do you require?**
   **Model answer:** Exact versions and feature inventory; current official compatibility docs; provider/module/registry and lock-file review; state/encryption analysis; copied-state baseline and candidate plans; test matrix; restore test with original tool; documented divergence classifications; one low-risk pilot and rollback owner. Shared syntax is not evidence of full compatibility.

3. **A Terragrunt dependency uses `mock_outputs`, and the plan is green. Is that enough for approval?**
   **Model answer:** No. Verify the producer state and actual outputs, inspect the exact command context and mock allowlist for the pinned version, reject sentinel values in apply artifacts, and run a plan using real dependency data. A green plan built on a mock is not a production dependency proof.

4. **What should an approval system bind to when using Terragrunt or Pulumi?**
   **Model answer:** Commit SHA, exact toolchain/runtime/dependency versions, immutable module/package sources, backend/state identity, target environment, plan/preview artifact digest, policy results, reviewer, and execution identity. Ensure apply/up consumes the reviewed artifact or explicitly require re-review if it must be recomputed.

5. **How do you migrate a resource from Terraform to Pulumi without dual management?**
   **Model answer:** Freeze writes, inventory the resource and ownership, back up state/configuration, verify destination import/state semantics, test on a copy, compare destination preview and resource properties, schedule a reviewed ownership switch, disable the old writer only after destination acceptance, then monitor drift. Abort if import or rollback limits are unclear.

### 9.14 Sources and verification notes

#### Official documentation basis

The lesson is grounded in the following primary documentation families by title/topic. The sources were **not live-verified during authoring**, so no specific release behavior is presented as freshly checked. Before adopting syntax or migrating state, open the official current version of each relevant document and record the date, version, and evidence.

| Topic | Official source/document to inspect | Human verification task |
|---|---|---|
| Terraform CLI, state, backends, locking, plans, modules, providers, tests | HashiCorp Terraform documentation: CLI commands; State; Backends; Providers; Modules; Dependency Lock File; Plan and Apply; Testing | Verify exact CLI and backend syntax for pinned version; confirm saved plan/state behavior. |
| OpenTofu CLI, registry, state compatibility/encryption, language features, tests | OpenTofu documentation: CLI; provider/module installation; state and encryption; language; tests; migration/compatibility notes | Confirm exact registry endpoints, feature support, state format/encryption, and version boundaries. |
| Terragrunt configuration and CLI | Terragrunt documentation: `terragrunt.hcl`; includes; inputs; dependencies and mock outputs; remote state; generate; hooks; CLI command reference | Verify `run-all`/`run --all`, source pinning, generated config, hook behavior, mock guard and saved-plan workflow. |
| Pulumi language/runtime, stacks, state backends, local backend, config/secrets, providers/components, preview/up, import/export | Pulumi documentation: projects/stacks; state and backends; configuration/secrets; providers; component resources; preview/update; import/export | Verify local backend syntax, secret encryption/provider, provider bridge limits and migration support. |
| Cloud-native IaC landscape | AWS CloudFormation documentation; Microsoft Azure Bicep documentation; AWS CDK documentation; CDK for Terraform documentation | Verify current project support/lifecycle before choosing a production dependency. |
| Kubernetes-native infrastructure | Crossplane documentation: concepts, providers, managed resources, compositions, claims and functions | Unit 12 owns operational depth; verify current APIs and lifecycle before use. |
| Configuration management | Ansible documentation: playbooks, inventories, idempotency and execution | Unit 10 owns operational depth. |
| Dependency update automation | Dependabot/Renovate documentation for the chosen repository platform | Verify configuration and ensure updates create reviewable PRs, not automatic infrastructure applies. |

#### Migration and tool-selection verification checklist

Before a real migration, verify each item against current official documentation and a reproducible scratch test:

- [ ] **Terragrunt CLI:** exact `run-all` vs `run --all` syntax, unit selection, exit-code behavior, working directory, and version support. **Method:** use pinned binary `--version` and official CLI reference; save a harmless provider-free invocation. **Evidence:** command and resolved unit list. **Blocks migration:** yes if command scope is unclear.
- [ ] **Dependencies and mocks:** `dependency` output behavior, mock output schema, command allowlist, producer-state requirements. **Method:** official reference plus negative test where producer output is absent. **Evidence:** real-output plan and mock-sentinel rejection. **Blocks migration:** yes if mocks can reach apply.
- [ ] **Hooks:** when hooks execute, arguments/environment inheritance, failure handling and output capture. **Method:** inspect official hook reference and test harmless logging hook in sandbox. **Evidence:** reviewed hook inventory and logs. **Blocks migration:** yes if unreviewed code can run with privileged identity.
- [ ] **Remote state and generate:** exact `remote_state` fields, generated file naming/merge behavior, backend config, provider config, locking. **Method:** official docs for pinned wrapper + engine/backend. **Evidence:** rendered config and target assertions. **Blocks migration:** yes if backend or identity is ambiguous.
- [ ] **Source pinning and saved plans:** immutable module source syntax, cache behavior, plan path and apply workflow. **Method:** official source/CLI docs and artifact-digest test. **Evidence:** source digest and plan identity. **Blocks migration:** yes if approved plan cannot be tied to apply.
- [ ] **Terraform/OpenTofu state:** exact versions' read/write compatibility, rollback behavior, state serial/lineage checks, encryption configuration and key custody. **Method:** current official state/migration docs and copy-based restore test. **Evidence:** readable backup with original tool. **Blocks migration:** yes if state recovery is not proven.
- [ ] **Registries and lock files:** provider/module source endpoints, checksums, mirror configuration, lock-file update semantics. **Method:** official installation/lock-file docs and review diffs. **Evidence:** resolved source inventory. **Blocks migration:** yes if required dependencies cannot be sourced reproducibly.
- [ ] **Language/test divergences:** early variable/locals evaluation, provider-defined functions, native test syntax, saved-plan behavior. **Method:** official language/test docs and feature-specific fixture tests. **Evidence:** supported-feature matrix. **Blocks migration:** yes for features used but not verified.
- [ ] **Pulumi local backend:** exact local login/backend and stack initialization behavior. **Method:** current official docs; no cloud credentials; disposable directory. **Evidence:** successful local-only init or explicit not-run note. **Blocks migration:** yes if required lab would need cloud login or remote backend unintentionally.
- [ ] **Pulumi secrets and state:** encryption provider, config secret behavior, export/import and provider bridge limitations. **Method:** official docs plus a disposable secret test with fake value. **Evidence:** redacted output and key-recovery plan. **Blocks migration:** yes if secret recovery or state import semantics are unclear.
- [ ] **Licensing/governance/community:** current license text, governance/contribution docs, security policy, advisory response, support/EOL policy, transitive dependency terms. **Method:** legal/procurement review of primary documents. **Evidence:** dated review record. **Blocks migration:** yes where organizational policy requires approval.
- [ ] **CI and pinning:** runner image, binary checksum/source, lock files, artifact retention/ACL, identity separation, concurrency group and update bot behavior. **Method:** inspect workflow permissions and test a blocked apply. **Evidence:** workflow diff and negative test. **Blocks migration:** yes if plan and apply can target different identities/resources without detection.

#### Appendix A — Claim Register

Confidence is the author's confidence in the general concept, not a claim of live documentation verification. Source titles below are document families to inspect, not assertions that the current release was consulted.

| ID | Section | Claim | Source (official document + section/title) | Confidence | Tag |
|---|---|---|---|---|---|
| C01 | 9.2 | Terraform/OpenTofu are engines while Terragrunt is a wrapper/orchestration layer. | Terraform CLI docs; Terragrunt overview | High | — |
| C02 | 9.2 | State maps configured resources to tracked real objects/attributes. | Terraform State docs; OpenTofu state docs | High | `[VERIFY]` |
| C03 | 9.2 | Plan output depends on code, state, toolchain, providers, and observed infrastructure. | Terraform Plan/Apply docs | High | — |
| C04 | 9.4 | `include` composes shared Terragrunt configuration. | Terragrunt `include` reference | Medium | `[VERIFY]` |
| C05 | 9.4 | `inputs` passes values to underlying modules. | Terragrunt `inputs` reference | High | `[VERIFY]` |
| C06 | 9.4 | `remote_state` and `generate` can centralize backend/provider configuration. | Terragrunt remote state/generate reference | Medium | `[VERIFY] [VERSION-SENSITIVE]` |
| C07 | 9.4 | `dependency` exposes outputs from another unit. | Terragrunt dependency reference | High | `[VERIFY]` |
| C08 | 9.4 | Mock outputs can hide absent real dependencies if not constrained. | Terragrunt mock outputs reference | High | `[VERIFY] [VERSION-SENSITIVE]` |
| C09 | 9.4 | `run-all` / `run --all` command forms are version-sensitive. | Terragrunt CLI reference/changelog | High | `[VERIFY] [VERSION-SENSITIVE]` |
| C10 | 9.4 | Multi-unit apply can expand blast radius across several state boundaries. | Terragrunt CLI reference; Terraform apply docs | High | — |
| C11 | 9.4 | Hook commands execute as an additional code surface requiring review. | Terragrunt hooks reference | High | `[VERIFY]` |
| C12 | 9.4 | Immutable module source pins improve reproducibility. | Terraform Module Sources docs; Terragrunt source reference | High | `[VERIFY]` |
| C13 | 9.4 | Generated configuration should be inspected before apply. | Terragrunt generate reference; Terraform backend/provider docs | High | `[VERIFY]` |
| C14 | 9.4 | Caching can reduce repeated work but must have correct keys/invalidation. | Terragrunt cache/CLI docs; general build-cache guidance | Medium | `[VERIFY]` |
| C15 | 9.4 | Parallelism can increase API pressure and rate-limit risk. | Terraform CLI parallelism docs; provider docs | High | `[VERIFY]` |
| C16 | 9.4 | Saved-plan identity must remain bound to the reviewed source and target. | Terraform plan/apply docs; Terragrunt CLI docs | High | `[VERIFY] [VERSION-SENSITIVE]` |
| C17 | 9.4 | Plain engine conventions may be preferable when orchestration complexity is small. | Engineering decision; test against team workflow | Medium | `[ASSUMPTION]` |
| C18 | 9.4 | Terramate and Terraform stacks are alternatives to evaluate at awareness level. | Terramate docs; Terraform stacks docs | Medium | `[VERIFY] [VERSION-SENSITIVE]` |
| C19 | 9.4 | OpenTofu uses the `tofu` CLI. | OpenTofu CLI docs | High | `[VERIFY]` |
| C20 | 9.4 | Terraform/OpenTofu registry/provider/module compatibility must be checked per version. | OpenTofu provider/module installation docs; Terraform registry docs | High | `[VERIFY] [VERSION-SENSITIVE]` |
| C21 | 9.4 | State-format compatibility must not be assumed across engines or versions. | OpenTofu state/migration docs; Terraform state docs | High | `[VERIFY] [VERSION-SENSITIVE]` |
| C22 | 9.4 | OpenTofu state encryption behavior and key/config requirements are version-sensitive. | OpenTofu state encryption docs | High | `[VERIFY] [VERSION-SENSITIVE]` |
| C23 | 9.4 | Variable/locals evaluation and provider-defined functions require feature-specific verification. | OpenTofu language/release notes; Terraform language docs | Medium | `[VERIFY] [VERSION-SENSITIVE]` |
| C24 | 9.4 | Test framework syntax may differ by engine/version. | Terraform testing docs; OpenTofu testing docs | High | `[VERIFY] [VERSION-SENSITIVE]` |
| C25 | 9.4 | An empty plan is evidence for one tested combination, not universal parity. | Terraform Plan docs; migration test design | High | — |
| C26 | 9.4 | Pulumi programs use general-purpose language runtimes such as Python/TypeScript. | Pulumi language docs | High | `[VERIFY]` |
| C27 | 9.4 | Pulumi stacks have configuration/state associated with deployment instances. | Pulumi stacks/state docs | High | `[VERIFY]` |
| C28 | 9.4 | Pulumi `preview` proposes changes and `up` performs updates. | Pulumi CLI docs | High | `[VERIFY] [VERSION-SENSITIVE]` |
| C29 | 9.4 | Pulumi component resources group resources into reusable abstractions. | Pulumi component resources docs | High | `[VERIFY]` |
| C30 | 9.4 | Pulumi preview may evaluate arbitrary program code and dependencies. | Pulumi programming model/runtime docs; language package docs | High | `[VERIFY]` |
| C31 | 9.4 | Secret handling depends on backend/config and must be verified. | Pulumi config/secrets and state backend docs | High | `[VERIFY] [VERSION-SENSITIVE]` |
| C32 | 9.4 | Provider bridges do not guarantee feature parity. | Pulumi provider docs; bridge/provider package docs | High | `[VERIFY]` |
| C33 | 9.5 | Multi-tool ownership must be exclusive for each resource lifecycle. | IaC state/import docs; platform ownership design | High | — |
| C34 | 9.5 | CloudFormation-to-Terraform adoption requires import and explicit handoff. | AWS CloudFormation docs; Terraform import docs | High | `[VERIFY]` |
| C35 | 9.5 | Terraform/OpenTofu-to-Pulumi migration requires feature-specific import/state validation. | Pulumi import/state docs; Terraform state docs | High | `[VERIFY] [VERSION-SENSITIVE]` |
| C36 | 9.5 | Upgrade rings reduce blast radius of version promotion. | Operational governance pattern | High | `[ASSUMPTION]` |
| C37 | 9.5 | Dependency-update bots should create reviewable changes, not auto-apply infrastructure. | Dependabot/Renovate docs; CI policy | High | `[VERIFY]` |
| C38 | 9.6 | Rollback must account for state/tool compatibility, not only code revert. | Terraform/OpenTofu state docs; upgrade playbook | High | `[VERIFY]` |
| C39 | 9.7 | Plan-to-apply elapsed time is a useful stale-plan risk signal. | Internal SRE metric design | Medium | `[ASSUMPTION]` |
| C40 | 9.8 | State, plans, logs and stack files can contain sensitive information. | Terraform state docs; Pulumi state/secrets docs | High | `[VERIFY]` |
| C41 | 9.8 | A `sensitive` marker does not by itself mean state is encrypted. | Terraform sensitive data docs | High | `[VERIFY]` |
| C42 | 9.8 | Preview jobs should use least privilege and avoid write credentials where possible. | Pulumi security docs; CI identity docs | High | `[VERIFY]` |
| C43 | 9.8 | Hook/package/program code are supply-chain execution surfaces. | Terragrunt hooks docs; language package manager security docs | High | `[VERIFY]` |
| C44 | 9.10 | Provider-free `terraform_data` availability depends on selected engine/version. | Terraform `terraform_data` resource docs; OpenTofu resource docs | Medium | `[VERIFY] [VERSION-SENSITIVE]` |
| C45 | 9.10 | The Pulumi local backend command and secret provider must be verified for the installed release. | Pulumi local backend and secrets docs | High | `[VERIFY] [VERSION-SENSITIVE]` |
| C46 | 9.10 | State copies must be independent during compatibility testing. | Terraform state/migration docs; OpenTofu migration docs | High | — |
| C47 | 9.10 | Local fixtures do not validate real cloud IAM, quota, or eventual consistency behavior. | Local emulator/provider documentation; test limitations | High | — |
| C48 | 9.14 | Licensing/governance should be reviewed from current primary documents. | Official license/governance/security/contribution docs for each project | High | `[VERIFY]` |
| C49 | 9.14 | Provider/module lock files and source digests should be reviewed during upgrades. | Terraform dependency lock docs; package manager docs | High | `[VERIFY]` |
| C50 | 9.14 | Import/export is not equivalent to semantic code/state translation. | Official import/state docs for source and destination tools | High | `[VERIFY] [VERSION-SENSITIVE]` |

#### Appendix B — Audit report

| Pass | Result | Defects found | Fixes applied | Residual risk |
|---|---|---|---|---|
| 1. Completeness | FIXED | Large scope creates risk of omitted required criterion. | Mapped L1–L4, four labs, comparison/divergence tables, ADR, incidents and appendices into skeleton. | Human should compare every line of the authoritative prompt before production use. |
| 2. Technical accuracy | OPEN | Current syntax and tool-specific behaviors were not live-verified. | Version-sensitive areas are explicitly tagged and the lesson avoids asserting universal parity. | Do not execute Terragrunt/Pulumi migration commands until verified against exact versions. |
| 3. Version currency | OPEN | No exact release baseline was verified in current official docs. | Metadata explicitly leaves version ranges to verification; no invented current versions. | Human must pin and test exact releases. |
| 4. State/migration safety | PASS | Migration can overwrite state if source and candidate share a backend. | Copy-state protocol, write freeze, no-apply-on-diff, restore and exclusive ownership gates included. | Human must validate actual backend isolation and recovery. |
| 5. Executability | OPEN | Terragrunt/Pulumi snippets are illustrative and not run; relative paths/schema need version-specific validation. | All required labs are local/simulated; syntax uncertainty and expected outputs are labelled. | Provider-free engine fixture also requires a locally available supported `terraform_data` resource. |
| 6. Security/supply chain | PASS | Hooks, packages, generated config, state and plan artifacts can expose execution/secret risk. | Least privilege, immutable pins, mock guards, artifact protection and dependency review covered. | Controls depend on actual CI and repository configuration. |
| 7. Fabrication scan | PASS | Risk of invented versions, output, source citations or governance claims. | No versions or execution results are fabricated; official source families are listed with explicit not-live-verified note. | Human must confirm canonical current URLs/sections. |
| 8. Pedagogical progression | FIXED | Advanced terms could appear before definitions. | Glossary and beginner model precede tool labs, trade-offs, incidents and governance. | Learner may need earlier Units 1–6 for state/backend/plan details. |
| 9. Cross-consistency/adversarial review | FIXED | Mock guard, plan identity and ownership handoff can be described inconsistently. | Same no-mock-for-apply and one-owner-per-resource rule repeated across labs, matrix, ADR and incidents. | Verify exact Terragrunt/Pulumi features and workflow integrations before adoption. |
| 10. Local safety/scope | PASS | No actual repository checkout/status was available for diff verification; real-cloud touch is prohibited. | Artifact is standalone in `/mnt/data`; labs are local/simulated and no repository fixture/state files were created by the lesson-writing process. | Repository-wide no-change claim is not made; local commands have not been run. |

#### Appendix C — Adversarial objections and responses

1. **“Mock outputs can reach apply if the command name changes.”** Response: verify exact allowlist syntax and add an independent sentinel/producer-state gate; migration remains blocked until negative test passes.
2. **“The operator may run from the wrong directory.”** Response: assert `pwd`, resolved unit list, backend key, and environment before plan/apply; deliberately test wrong-directory failure.
3. **“The copied state might still point to the original backend.”** Response: inspect backend config and environment, use independent local copies, and prove backend identity before initialization; abort if unclear.
4. **“A new engine may rewrite state and break rollback.”** Response: never mutate the sole copy; test candidate and old-tool readability on copies; keep original state/tool available.
5. **“The module source pin may be mutable.”** Response: use immutable commit/exact release and record source digest; reject branch references in production.
6. **“A hook may execute an unexpected command.”** Response: inventory all hooks, review environment/permissions/egress, run harmless sandbox tests, and fail closed on unknown hook.
7. **“Pulumi preview could fetch or execute a compromised dependency.”** Response: isolate runner, remove write credentials, pin packages, restrict egress and review dependency provenance.
8. **“Terraform and Pulumi may both own one resource after migration.”** Response: freeze writers, map IDs, import/adopt, compare preview, switch ownership explicitly, disable old writer, then monitor.
9. **“Registry divergence could make init succeed with a different provider.”** Response: verify endpoints/mirrors and lock-file/provider selection; review binary/checksum and fail on unexplained source changes.
10. **“Rollback plan may require the new tool that just failed.”** Response: keep original binary/config/state/key material and prove the old tool can read a restored copy before promotion.
11. **“The plan is approved but code or state changed before apply.”** Response: bind artifact to commit/state identity and require re-plan/re-approval when stale; use backend locking/concurrency controls.
12. **“A green validation result proves the provider will behave safely.”** Response: validation is syntax/schema evidence only; inspect plan, test provider behavior, and retain post-apply verification.
13. **“The state is encrypted, so raw artifacts are safe to share.”** Response: protect artifacts and secrets independently; verify encryption scope and never publish raw state/plan/stack files.
14. **“A separate state file makes dual management safe.”** Response: state separation is not resource ownership separation; prohibit concurrent writers for the same resource ID.
15. **“A wrapper always reduces complexity because it removes duplicate lines.”** Response: compare total cognitive load, debug time, change failure rate and upgrade burden; keep plain conventions if net benefit is unproven.
16. **“A Pulumi component is exactly the same as a Terraform module.”** Response: treat as analogous reuse concepts, not one-to-one state/API semantics; test import, lifecycle and outputs explicitly.
17. **“Local tests prove cloud migration safety.”** Response: local tests prove only the exercised logic; real provider semantics, IAM, quotas, and eventual consistency remain untested.
18. **“An empty plan means future versions are compatible.”** Response: plan is scoped to one tested combination; maintain a version matrix and repeat tests on upgrades.

#### Appendix D — Known limitations and assumptions

- Required labs are local-only or simulated; no cloud account, paid resource, cloud credential, or real resource mutation is required.
- LocalStack/MinIO are not used as required dependencies. If added by a learner, their service coverage and behavior must be verified; emulation does not prove real-cloud parity.
- No exact Terraform, OpenTofu, Terragrunt, Pulumi, provider, or runtime version was installed or verified while authoring this lesson. Tool baseline remains `[VERIFY]`.
- Terragrunt `run-all`/`run --all`, `mock_outputs` guard keys, `remote_state`, `generate`, hook execution, rendered config, caching and saved-plan workflow are version-sensitive.
- OpenTofu/Terraform provider/module registry behavior, state format, state encryption, variable/locals evaluation, provider-defined functions, tests and licensing/governance must be verified from current primary documents.
- Pulumi local backend, secret provider, stack state, provider bridging and state import/export syntax/limits are not live-verified. Lab 3 is intentionally a guided walkthrough, not a claimed execution.
- Empty-plan evidence is bounded to tested source, tool versions, providers, modules, state, identity, and observed infrastructure. It is not universal semantic proof.
- State import/export does not automatically translate lifecycle semantics, defaults, replacement behavior, dependencies, or resource schemas.
- ADR scores are subjective `[ASSUMPTION]` values for a fictional team, not benchmark data or an endorsement.
- State, plan files, stack exports/config, logs, generated config, and CI artifacts can contain sensitive information; sanitize evidence and restrict access.
- The lesson cites official document families by name but did not live-open them during authoring. Exact URLs, sections and current release behavior require human verification.
- The snippets are educational; the Terragrunt paths and Pulumi project schema need correction/validation against the chosen pinned versions before execution.
- This file was created in the working artifact directory `/mnt/data`, not committed to a verified repository checkout. No repository-wide status/diff was inspected, so no claim is made that the repository has no other changes.
- The labs do not prove production-grade security, real cloud behavior, licensing suitability, or safe migration of a live state.

#### Appendix E — Sign-off

**Content status:** DRAFT-AUDITED  |  **Audit date:** 2026-10-28  |  **Auditor:** AI self-audit (requires human verification)  |  **Unverified items count:** 84 `[VERIFY]` occurrences and 26 `[VERSION-SENSITIVE]` occurrences in the authored content, mechanically counted.

An AI self-audit is not a substitute for a human running the commands with pinned versions, checking current official documentation, and reviewing migration plans. Do not use this draft as authority to change production state until all migration-blocking verification items are closed.
