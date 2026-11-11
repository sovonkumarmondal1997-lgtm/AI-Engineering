# Free-Tier Cloud Account and Cost Safety — Stage 2E

> Prevent surprise cloud spend by securing the account first, setting alerts before provisioning, and treating every cloud exercise as a time-boxed experiment with a verified teardown.

**Estimated time:** 2–3 hours for initial guardrails; 10–15 minutes for a routine daily cost check  
**Default provider:** AWS  
**Last reviewed:** 2026-10-24  
**Free-tier terms:** Re-check the provider page, since values change.

---

## 1. Purpose and the golden rules

This guide is about avoiding surprise bills, not optimising production cloud spend; Stage 2E uses AWS as its reference provider.
The free programme, account eligibility, credits, service coverage, limits, and console behaviour can change, so check current terms before creating anything.
Use local kind/minikube and LocalStack labs whenever they can teach the required mechanics; see [local-lab-kind-minikube-and-localstack.md](local-lab-kind-minikube-and-localstack.md).
Use real cloud only when the lesson depends on real provider behaviour, and follow a written teardown plan.
A budget is an alerting mechanism, **not a guaranteed spending cap**; billing data can arrive late.
No control can promise that every charge will be prevented.
Account security is cost control: an exposed credential can let someone create resources faster than billing alerts can warn you.

### Golden rules — memorise these

<box>
- **Local first.** Cloud only when the lesson needs real provider fidelity.
- **One dedicated lab account.** Keep it separate from personal and work environments.
- **MFA before resources.** Secure root and daily identities before provisioning.
- **Budget and notifications before the first resource.** Budgets alert; they do not cap spend.
- **Tag every resource** with project, owner, environment, and expiry where supported.
- **Use one planned region** unless the lesson specifically tests regional behaviour.
- **Destroy the same day.** Every exercise starts with a written teardown step and time limit.
- **No real keys in Git, notebooks, logs, shell history, or screenshots.**
- **Check cost and resource inventories.** A stopped VM may leave billable resources behind.
- **Treat every alert as actionable.** Do not assume the free-tier label protects you.
</box>

---

## 2. When to use real cloud (and when not to)

The default is local-only. “Real cloud optional” means use it only if the learning objective requires a real provider API and the current account terms have been checked. “Real cloud needed for fidelity” means the specific behaviour cannot be proven locally; it does **not** mean you must use cloud to finish this stage.

| Module | Default recommendation | Cost risk | Reason and local alternative |
|---|---|---|---|
| M01 — Container images | Local only | Low | Build/load/scan images locally; use the local registry pattern in [local-lab-kind-minikube-and-localstack.md](local-lab-kind-minikube-and-localstack.md). |
| M02 — CI/CD | Local only | Low | Practise pipeline logic and local deployment first; cloud runners and registry auth can be conceptual. |
| M03 — Kubernetes operations | Local only | High if managed cluster used | Use kind/minikube; managed control planes and worker resources may incur charges. If needed, time-box the exercise. |
| M04 — Networking | Local first; real cloud optional | High | kind plus a policy-enforcing CNI teaches selected mechanics; VPC routes, cloud load balancers, and security-group behaviour need provider testing. |
| M05 — Storage | Local first; real cloud optional | High | Local PVCs teach Kubernetes objects, not cloud CSI, zonal attachment, or managed storage durability. |
| M06 — Helm/Kustomize | Local only | Low | Render and deploy charts/overlays to kind. |
| M07 — Infrastructure as Code | LocalStack/local files first; real cloud optional | High | Practise state, plans, and drift locally; real-provider fidelity needs a separately approved, cost-guarded exercise. |
| M08 — GitOps | Local only | Medium | Use kind and a local Git repository; external identity and hosted service integrations can be conceptual. |
| M09 — Secrets | Local only with dummy values | Medium | Practise references and access patterns without real secrets; managed secret services may incur charges. |
| M10 — SRE | Local only | Low | Exercise probes, rollouts, failure notes, and local SLOs without real customer traffic. |
| M11 — Observability | Local first; real cloud optional | High | Keep local retention short; hosted ingestion, metrics, traces, and security events may be metered. |
| M12 — Security/supply chain | Local only | Low | Scan local images and manifests; do not upload proprietary artefacts or secrets. |
| M13 — Backup/DR | Local first; real cloud optional | High | Test restore mechanics locally; real backup storage and cross-region copies can accumulate cost. |
| M14 — Multi-cluster | Local only by default | High | Use two named kind clusters to simulate regions; real multi-region tests multiply resources and transfer. |
| M15 — FinOps | Local data and reviewed billing data | Medium | Practise cost models with synthetic/local data; real billing visibility is useful only after account guardrails exist. |
| M16 — Platform engineering | Local only | Low | Build templates and self-service workflows around kind and local scripts. |
| M17 — Capstone | Local by default; real cloud optional | High | Local end-to-end evidence is sufficient for the local track. If real cloud is chosen, the cost plan and teardown proof are part of the deliverable. |

**Rule:** the “needed for fidelity” label describes a limitation of the local lab, not a requirement to spend money. If your zero-surprise requirement means no risk of charges at all, keep that exercise conceptual and local.

---

## 3. Mental model: how cloud bills actually work

Cloud bills are composed of different meters, not one simple “server is on/off” switch.

- **Time-based usage:** compute instances, managed control planes, gateways, and some endpoints can accrue charges while running or provisioned. Check the current provider terms for each resource.
- **Capacity-based usage:** disks, snapshots, databases, and allocated storage can remain billable even when the associated compute is stopped.
- **Per-GB usage:** storage, logs, backups, and some network transfers can scale with retained data.
- **Per-request or per-event usage:** APIs, functions, monitoring, security findings, and managed integrations may be metered by activity.
- **Data transfer:** internet egress, cross-zone traffic, and cross-region replication may have separate meters. Exact rules vary by service and region. `[VERIFY]`
- **Resources that survive the main resource:** deleting a cluster or VM does not necessarily delete its load balancers, volumes, snapshots, IP addresses, registries, logs, keys, or network components.
- **Billing delay:** usage and cost data can lag. A quiet dashboard is not proof that the current experiment is free.
- **Free programme versus credits versus on-demand:** these are different models. Identify which applies to your account, what expires, what is eligible, and what happens when a credit or allowance is exhausted. Do not rely on remembered values.
- **Idle is not always free:** an allocated resource can cost money while no user traffic is reaching it.
- **“Stopped” is not “deleted”:** stopping compute may leave storage, addresses, snapshots, or other associated resources behind. The exact behaviour depends on the service. `[VERIFY]`

**Budget honesty:** budgets and cost alerts are useful warning systems, not hard caps. Billing data can be delayed, thresholds may be evaluated after usage occurs, and notification delivery can fail. Some budget actions may restrict selected resources, but their availability and behaviour vary and they are not a guaranteed spending ceiling. `[VERIFY]`

The only dependable prevention strategy is to avoid creating unnecessary costly resources, secure credentials, tag what you create, keep the exercise short, and verify teardown. A prepaid or limit-controlled payment method may be an account-management option for some users, but availability and consequences vary; consult provider documentation and support rather than treating it as a technical cost cap.

---

## 4. Phase 1 — Account setup and identity security (do first)

### 4.1 Use a dedicated lab account

Use a separate lab account, isolated from personal and work workloads. A dedicated email alias can make notifications and ownership easier to recognise.
Do not use a work account or attach a personal production workload to a learning exercise.
Before signup, read the provider's current account eligibility, billing, identity, and free-programme terms. Record the date checked and any expiry or eligibility conditions in a private `cloud-account-notes` file. Do not store passwords, recovery codes, secret keys, payment details, or full account identifiers in that notes file.

### 4.2 Secure the root identity

- Set a strong, unique password and store it in a password manager.
- Enable MFA before creating any lab resources. Prefer a hardware security key or an authenticator app where supported.
- Do not create root access keys.
- Use the root identity only for tasks that explicitly require it.
- Store recovery information securely and test that the recovery method is usable.
- Keep account contact and billing notification email addresses current.

The exact current root-account setup and MFA flow are described in AWS account and IAM documentation. Console labels can change. `[VERIFY]`

### 4.3 Create a daily identity with least privilege

Use the provider's currently recommended identity approach to create a non-root daily identity. Enable MFA and grant only the permissions needed for the exercise.
Prefer temporary credentials or role-based access over long-lived access keys when the selected workflow supports them.
Do not create a broad administrator access key merely because it makes a tutorial easier. If a task genuinely needs elevated permissions, grant them deliberately for that task and remove them when no longer needed.
The exact AWS identity service names, recommended account setup flow, and temporary-credential configuration should be checked against current AWS IAM and identity documentation. `[VERIFY]`

Never put credentials in source files, Docker images, Kubernetes manifests, Terraform code, shell commands that may be recorded, notebooks, screenshots, or chat transcripts.
For local LocalStack exercises, use the dummy values and explicit endpoint pattern from [local-lab-kind-minikube-and-localstack.md](local-lab-kind-minikube-and-localstack.md), not real AWS credentials.

### 4.4 Enable billing visibility and contact details

Open the Billing and Cost Management area and find the account's available cost visibility, budgets, notifications, and free-tier usage features. Exact feature availability and console navigation can vary by account type and current provider setup. `[VERIFY]`
Set the billing contact to an inbox you monitor. Confirm notification delivery rather than assuming that entering an address is sufficient.
Do not create a resource just to test account setup.

### 4.5 Verify gate

| Control | How to verify | Done |
|---|---|---|
| Dedicated lab account | Confirm account is separate from personal/work workloads | [ ] |
| Root password | Unique and stored securely | [ ] |
| Root MFA | Sign-in requires the configured second factor | [ ] |
| No root access keys | Review root security credentials; no access keys exist | [ ] |
| Daily non-root identity | Sign in with the intended daily identity | [ ] |
| MFA on daily identity | Confirm MFA is enabled | [ ] |
| Least privilege | Review assigned permissions against the planned lab task | [ ] |
| Billing contact | Confirm current contact email | [ ] |
| Cost visibility | Find the billing/cost pages and record the navigation goal in notes | [ ] |
| Current free programme | Record which programme applies, eligibility, expiry, and exclusions | [ ] |

**Verify:** do not proceed to Phase 2 until root MFA, the daily identity, and billing contact are checked.

**If this goes wrong:** stop account setup and consult current AWS account/IAM documentation and provider support. Do not compensate by sharing root credentials or creating permanent keys.

---

## 5. Phase 2 — Budgets, alerts and anomaly detection (before any resource)

### 5.1 Create a cost budget first

Before provisioning any resource, open the Budgets area in AWS Billing and Cost Management and create a cost budget suitable for a learner. Exact console paths, available budget types, and feature access are subject to current provider documentation. `[VERIFY]`
Choose a low threshold that you can monitor and configure notifications to an email inbox you actually read.
You can use example alert tiers such as 25%, 50%, 75%, and 100% of your chosen budget as a **personal warning scheme**, not as AWS rules or a guarantee that notification occurs before spend. The correct tiers depend on the budget and available configuration.
A learner may choose a zero-spend or very-low-budget target as a warning objective, but a zero budget does not make cloud provisioning technically impossible and does not stop a request from creating a billable resource.

**Important:** a budget is an alert, not a hard cap. Cost data may lag actual usage, and the alert may arrive after the resource has already accrued cost.

### 5.2 Add anomaly detection if available

Cost anomaly detection looks for spending patterns that differ from a baseline. It can help identify unexpected changes, but it is not a preventive control.
It may need historical data, may not detect every event immediately, and may not cover every cost type in the way you expect. Availability, setup, notification behaviour, and coverage must be checked in current AWS Billing and Cost Management documentation. `[VERIFY]`
Do not wait for anomaly detection before checking the cost view.

### 5.3 Free-tier usage alerts

Find the account's current free-tier or credit-usage view and any available usage alerts. The programme model and alert features can differ for new and existing accounts and may change over time. `[VERIFY]`
Record:
- the current programme type;
- eligible services and exclusions;
- expiry or credit exhaustion conditions, if applicable;
- usage thresholds and notification recipients;
- the date you checked the terms.

Do not write assumed limits into your notes as facts. Re-check monthly and before a new service.

### 5.4 Two-minute daily cost check

Before and after each cloud lab, inspect:
1. the current cost-by-service view;
2. budget status and recent notifications;
3. the resource inventory in the chosen region;
4. any other region where you might have created resources;
5. recent activity if usage looks unexpected.

For a small lab, “normal” means you can explain every resource and cost category visible—not merely that the total looks small. Billing data can lag, so repeat the check the next day after teardown.

### 5.5 Verify gate

- [ ] A budget exists before the first resource.
- [ ] Notifications go to an inbox you read.
- [ ] Alert thresholds are understood as warning levels, not spend caps.
- [ ] The current free-programme view and terms have been checked.
- [ ] An anomaly-detection feature is enabled only if available and understood.
- [ ] Notification delivery has been tested if the provider supports a test, or the configuration and recipient have been reviewed.

**Verify:** capture evidence of the budget configuration and notification recipient without exposing sensitive account details.

**If this goes wrong:** do not create resources until notifications and budget settings are understood. Remember that no budget or alert guarantees a maximum bill.

---

## 6. Phase 3 — Guardrails before the first resource

### 6.1 Region discipline

Choose one region for ordinary exercises and record it in your private lab notes. Multiple regions make it easier to forget resources and may introduce transfer or replication costs.
Use additional regions only when regional behaviour is the actual learning objective. List resources in every region you used before closing the exercise.
Some services are global, regional, or have special regional behaviour; check the current service documentation rather than assuming one region setting controls everything. `[VERIFY]`

### 6.2 Tags and naming

Use a consistent prefix and tags where the service supports them. A proposed convention:

| Field | Example value | Purpose |
|---|---|---|
| `project` | `stage2e-lab` | Identifies the roadmap project |
| `owner` | `learner` | Identifies responsibility without exposing personal data |
| `env` | `lab` | Distinguishes the disposable environment |
| `expires` | `YYYY-MM-DD` | Reminds you when the resource should be removed |
| Name prefix | `s2e-lab-` | Makes inventory searches easier |

These are proposed lab conventions, not a guarantee that every service supports every tag or that tags are automatically enforced.
Use a date that is meaningful to the exercise; do not use an invented placeholder as the actual expiry tag.
Tags aid inventory and accountability, but they do not prevent spend by themselves.

### 6.3 Quotas and policy guardrails

Review service quotas and any account-level controls relevant to the planned service. Quotas can reduce the likelihood of accidentally creating some resources, but they are a soft safety net, not a budget cap; limits vary by service and can sometimes be changed. `[VERIFY]`
Deny-by-default is the right design mindset: do not grant permissions or open network access unless the exercise needs them.
Organisation-level policies can impose stronger guardrails across multiple accounts, but they are awareness material for this solo track, not a prerequisite. Their availability depends on account and organisation setup. `[VERIFY]`

### 6.4 Credential hygiene and secret scanning

- Never commit credentials, `.env` files with real values, private keys, cloud tokens, kubeconfigs containing sensitive contexts, or state files with secrets.
- Keep secrets out of command-line arguments where they may enter shell history or process listings.
- Use local secret-scanning tools or repository-scanning tools to check changes before commit. Choose a maintained tool and follow its official documentation; this guide names tool categories rather than prescribing an unverified command.
- If a secret appears in Git, deleting the latest file is not enough: the secret may remain in history, forks, logs, or caches.

### 6.5 If a key leaks: incident response

1. **Contain immediately:** disable or revoke the exposed credential using the provider's documented identity workflow.
2. **Rotate:** replace it with a new credential only if the workflow still requires one; prefer temporary credentials where possible.
3. **Review activity:** inspect authentication and audit activity for unexpected sign-ins, API calls, identity changes, and resource creation.
4. **Check billing and inventory:** inspect cost-by-service, all used regions, and newly created resources.
5. **Remove persistence:** delete unauthorised resources after preserving the evidence needed for investigation and confirming their identity.
6. **Search for copies:** inspect repository history, logs, notebooks, build artefacts, and shared messages; remove the secret from exposed locations.
7. **Document and escalate:** record the timeline and actions. Contact provider support if activity or charges are unexplained.

Do not wait for a billing alert after a key leak. Cost data and alerts can lag behind resource creation.

**Verify gate**
- [ ] One planned region is documented.
- [ ] Resource naming and tags are agreed before creation.
- [ ] Quotas and available guardrails have been reviewed.
- [ ] Secret scanning is part of the local workflow.
- [ ] You know how to revoke a credential and inspect account activity.

**If this goes wrong:** stop provisioning, revoke the exposed credential, inspect account activity and costs, and follow provider security guidance. Do not paste the key into a chat or ticket to ask whether it is valid.

---

## 7. Phase 4 — Cost-safe lab workflow

### 7.1 The repeatable loop

Every real-cloud exercise follows this sequence:

1. **Plan:** write the learning objective, required services, expected resources, region, estimated lifetime, and teardown command/steps.
2. **Tag:** define names, tags, and expiry before creation.
3. **Create with IaC where practical:** keep configuration in a dedicated directory and review the plan before applying.
4. **Verify:** confirm the correct account, region, endpoint, resource list, and application behaviour.
5. **Destroy:** execute the written teardown while the exercise is still fresh.
6. **Confirm zero:** inventory resources, check the cost view, and repeat the cost check the next day because billing data may lag.

A cloud lab is not complete when the application works. It is complete when the resources are accounted for and teardown is verified.

### 7.2 The teardown contract

Every exercise begins with a written teardown contract:

- **Owner:** who is responsible for cleanup (for solo study, you).
- **Resource inventory:** every resource expected to be created, including dependent resources.
- **Time limit:** a specific end time or same-day deadline.
- **Delete/stop procedure:** the exact reviewed procedure, including manual resources not managed by IaC.
- **Verification:** which console/resource inventory views prove resources are gone.
- **Next-day check:** cost-by-service and alerts are reviewed after billing data has had time to update.
- **Fallback:** what you will do if a resource cannot be deleted.

If you cannot explain the teardown before creation, do not create the resource.

### 7.3 Terraform/OpenTofu and destroy discipline

Use a dedicated directory and state for each exercise. Keep state and plan files private; they may contain sensitive values even if the current lab uses dummy credentials.
Before `apply`, inspect the selected identity, region, provider configuration, and plan.
Before `destroy`, inspect the current directory, workspace/state, account identity, region, and planned deletions.
Do not assume that IaC owns resources created manually or resources created by a managed service as dependencies.
Do not run `apply` or `destroy` from an unknown directory or while the active account/profile is uncertain.

For LocalStack, follow the explicit endpoint and dummy-credential safeguards in [local-lab-kind-minikube-and-localstack.md](local-lab-kind-minikube-and-localstack.md). A real-cloud provider configuration must be treated as a separate, deliberate exercise.

### 7.4 Verify nothing remains

Use several views; no single inventory method is complete:

- Search resources by the lab naming prefix and tags in the region used.
- Review service-specific inventories for resources that may not be tagged or may have different tag behaviour.
- Review other regions if the exercise ever switched regions.
- Inspect dependency resources: storage, snapshots, addresses, logs, load balancers, registries, network components, keys, and hosted zones.
- Review the provider's cost-by-service view the next day and again if a cost line is unexplained.
- Record what was removed and what could not be removed.

Some resource types are global or have special visibility and billing rules. Check the service documentation. `[VERIFY]`

### 7.5 Leftover traps

The following resources can survive deletion of the primary workload or can have separate lifecycle and billing behaviour; verify the current service-specific behaviour before each exercise. `[VERIFY]`

- snapshots and unattached volumes;
- public IPv4 addresses or elastic IP-style resources;
- load balancers and target resources;
- NAT gateways and related network components;
- container registries and stored image layers;
- log groups, retained logs, and monitoring resources;
- managed Kubernetes cluster resources and worker compute;
- KMS keys and other managed security resources;
- hosted DNS zones and records;
- database snapshots, backups, and allocated storage;
- cross-region copies and data-transfer-producing resources.

**Verify gate**
- [ ] Teardown is written before provisioning.
- [ ] All resources are tagged/named where supported.
- [ ] The identity, region, and plan have been reviewed.
- [ ] Cleanup steps include dependencies and manual resources.
- [ ] Next-day cost check is scheduled or written into the routine.

**If this goes wrong:** stop creating new resources, inventory the current account and all regions used, remove only resources you can identify safely, and contact provider support for unexplained usage. Do not run an account-wide cleanup script without a dry run and a dedicated lab account.

---

## 8. The expensive-resource watchlist

This table is a prevention checklist, not a price list. Cost behaviour and billing rules vary by region, service version, account eligibility, and current provider terms. Verify each item in the current AWS documentation before using it. `[VERIFY]`

| Resource | Relative risk | Why it surprises people | Safer alternative for learning | Teardown check |
|---|---|---|---|---|
| NAT gateways | High | Provisioned network components and traffic can be metered even when the app seems idle | Use LocalStack or a diagram/simulation for API concepts | Inspect network resources and the cost-by-service view; confirm the gateway and related resources are removed |
| Managed Kubernetes control planes | High | The cluster control plane may have a separate cost from worker compute and add-ons | Use kind or minikube | Delete the cluster and separately inspect workers, load balancers, volumes, addresses, and logging resources |
| Load balancers | High | May remain after an app or cluster is removed; data processing may be metered | Use kind ingress with local port mappings | Inspect load-balancer inventory and associated target/resources |
| Idle public IPv4 addresses | Medium/High | Allocation/association rules may cause charges even when not serving traffic | Use localhost or private local networking | Inspect allocated addresses and release only the lab-owned ones |
| Large or multi-AZ databases | High | Compute, allocated storage, replicas, backups, and cross-zone traffic can all matter | Use a local database container with small synthetic data | Delete the instance and inspect snapshots, backups, replicas, and allocated storage |
| Unattached volumes and old snapshots | Medium/High | Storage can persist after compute is stopped or deleted | Use local Docker volumes or disposable files | Inventory volumes/snapshots and delete only those confirmed as lab data |
| Cross-AZ and internet data transfer | Medium/High | Network paths can create separate metered usage | Use local Docker networks for mechanics | Review network architecture and cost-by-service after the exercise |
| Verbose log ingestion and retention | Medium/High | High event volume and long retention accumulate data | Local logs with short retention and bounded sample data | Inspect log groups, retention, and any exports/streams |
| GPU or large instances | High | High-capacity compute can be costly and may be ineligible for free programmes | Use CPU-sized local examples or conceptual GPU labs | Confirm instance termination and inspect attached storage and addresses |
| Managed observability/security services | Medium/High | Events, metrics, scans, findings, and ingestion may be metered | Use local Prometheus/Grafana or local scanning tools where appropriate | Disable/remove the service configuration and inspect retained logs, data, and linked resources |
| KMS keys | Medium | Key lifecycle and related operations may have separate billing or deletion-delay behaviour | Use dummy local secrets for mechanics | Inspect keys, aliases, deletion schedules, and dependencies before closing the exercise |
| Always-on endpoints | High | Provisioned endpoints may continue to accrue usage while idle | Use a local endpoint or run only during a timed session | Inventory endpoints and related compute/networking resources |
| Marketplace subscriptions | High | Terms may be separate from standard service usage and may involve ongoing commitments | Avoid marketplace products in this zero-budget stage | Review subscriptions and contract state in provider documentation; contact support if uncertain |

**Zero-budget rule:** if the expected billing behaviour is unclear, do not provision the resource. Use the local lab or a conceptual exercise instead.

---

## 9. Cost-safe patterns for common Stage 2E exercises

### M03 — Kubernetes operations

- Prefer kind/minikube for clusters, rollouts, probes, and basic scheduling.
- Treat managed Kubernetes as high risk until the current control-plane, worker, network, storage, and logging costs are understood.
- If a real managed cluster is essential for a specific fidelity test, create a time-boxed plan, verify account identity and region, and include all dependent resources in teardown.
- Never leave a managed cluster running overnight merely because its workers are idle.

### M07 — Infrastructure as Code

- Practise syntax, state, plans, and drift locally first; use LocalStack for supported API calls with explicit endpoints and dummy credentials.
- For a real-provider exercise, separate the configuration and state from the emulator exercise.
- Review identity, region, provider endpoints, and plan before applying.
- After destroy, inventory resources that may not be managed by the state.
- Never treat a successful `destroy` as proof that the billable resource count is zero.

### M11 — Observability

- Start with local metrics, logs, and traces.
- Bound log volume and use short retention for disposable labs.
- Check whether hosted ingestion, metrics, traces, security events, or exports have per-event or retention-based meters. `[VERIFY]`
- Teardown must include log groups, dashboards, data stores, agents, and exported data where applicable.

### M13 — Backup and disaster recovery

- Use local snapshots and restore exercises first.
- Treat cloud backup copies, retained snapshots, cross-region replication, and allocated backup storage as potential cost risks. `[VERIFY]`
- Record the expected data volume and delete only lab-owned backups after confirming they are disposable.
- Do not create a cross-region copy unless the exercise specifically tests that behaviour and has a teardown plan.

### M14 — Multi-cluster and multi-region

- Use two named kind clusters to simulate separate regions.
- A real multi-region setup can multiply compute, storage, endpoints, backups, and transfer paths.
- Do not create real multi-region resources to make a diagram look realistic.
- If a real fidelity exercise is approved, inventory and teardown both sides independently.

### M15 — FinOps

- Practise allocation, tags, budgets, and unit-cost reasoning with synthetic or exported data that contains no secrets.
- If using actual billing data, restrict access, remove account identifiers and sensitive business details before sharing it.
- Do not create spend just to produce a cost chart.
- The deeper cost-engineering curriculum belongs in M15, not this account-safety guide.

### M17 — Capstone

The capstone submission must include:
- a resource diagram and list;
- the account/region assumptions (without exposing account IDs);
- the preflight checklist;
- a cost-risk table;
- the budget/alert configuration evidence with sensitive details redacted;
- a written teardown contract;
- proof that the lab resources were removed;
- a next-day cost check and a note about billing-data delay.

If real cloud is not essential, complete the capstone locally. No cloud resource is required merely to make the project look production-like.

---

## 10. Incident playbook: "I think I am being charged unexpectedly"

Treat an unexplained charge or sudden resource change as an incident. Do not wait for the next budget notification.

1. **Stop new provisioning.** Pause `apply`, deployment scripts, and experiments until you understand the situation.
2. **Open the cost-by-service view.** Identify which service/category changed. Exact console navigation and report availability can change. `[VERIFY]`
3. **Narrow the resource.** Inspect the relevant service inventory in the region used, then check other regions and global resources. Use names, tags, and creation/activity history where available.
4. **Stop or delete the identified lab resource.** Confirm its identity and dependencies first. Do not blindly delete shared or unfamiliar resources.
5. **Check credentials and activity.** If a key may have leaked, revoke it immediately and follow Phase 3's incident steps. Inspect account activity for unexpected resource creation or identity changes.
6. **Inspect dependent resources.** Look for volumes, snapshots, load balancers, IP addresses, logs, gateways, registries, backups, and other resources that may remain after the main resource is removed. `[VERIFY]`
7. **Review the budget and notifications.** Confirm the configured recipient and thresholds, but remember that alerts and billing data can lag.
8. **Contact provider support if charges or resources remain unexplained.** Follow the provider's documentation and support process; do not assume a charge will be reversed.
9. **Document the timeline.** Record what was created, the first alert or cost observation, actions taken, and the control that would have prevented recurrence.
10. **Reopen provisioning only after the cause is understood.** Update the teardown contract, tags, or permissions before repeating the exercise.

Do not run an account-wide cleanup tool as the first response. If such tooling is considered, it must have a reviewed dry run and be restricted to a dedicated lab account; it can still remove data or resources unexpectedly.

---

## 11. Other providers (awareness)

This stage standardises on AWS because the LocalStack exercises and the roadmap's example workflows use AWS APIs. The same prevention principles apply to other providers; do not assume their free programmes, billing delays, budget features, or resource lifecycle rules match AWS.

| Provider | Concepts to locate in current official docs | What to record |
|---|---|---|
| Google Cloud (GCP) | Current free programme, budgets/alerts, billing reports, identity/MFA, quotas, project-level controls `[VERIFY]` | Programme eligibility and expiry, budget notification setup, project/resource ownership, cleanup scope |
| Microsoft Azure | Current free programme, budgets/alerts, cost analysis, identity/MFA, quotas, subscription/resource-group controls `[VERIFY]` | Programme eligibility and expiry, budget notification setup, subscription/resource-group scope, cleanup scope |

For either provider:
- Read the current free-programme terms before creating resources.
- Secure privileged identities and enable MFA.
- Configure cost alerts before provisioning.
- Use a dedicated learning scope/project/subscription where available.
- Tag/name resources and set a teardown deadline.
- Inspect all regions and dependent resources after cleanup.
- Treat budgets as alerts unless the provider's current docs prove a specific control behaves differently; never assume a notification is a hard cap.

---

## 12. Monthly hygiene checklist and end-of-stage closure

### Monthly review

- [ ] Re-read the provider's current free-programme terms and note any changes.
- [ ] Check eligibility, credit/allowance status, and expiry conditions if applicable.
- [ ] Review cost-by-service and budget notifications.
- [ ] Confirm notification email addresses still work.
- [ ] Inspect resources in every region used during the month.
- [ ] Search for lab tags and naming prefixes.
- [ ] Review snapshots, volumes, addresses, load balancers, gateways, registries, logs, keys, backups, and hosted zones.
- [ ] Check recent account activity for unexpected identity or resource changes.
- [ ] Confirm root and daily identity MFA remain enabled.
- [ ] Review repository secret-scanning results and remove any exposed credential through the incident process.
- [ ] Update `cloud-account-notes` with the date reviewed; never store credentials there.

### Stage closure checklist

- [ ] All named lab resources have been destroyed or explicitly accounted for.
- [ ] All regions used during the stage have been inspected.
- [ ] Dependent resources and persistent data have been checked.
- [ ] IaC state and plans are stored safely or removed according to the lab policy.
- [ ] Temporary credentials are revoked or expired; unnecessary long-lived credentials are deleted.
- [ ] Root MFA and daily identity MFA remain enabled.
- [ ] Budget and alert settings are still configured.
- [ ] The cost view has been checked after teardown and again after a defined waiting period that accounts for billing-data delay.
- [ ] Any non-zero or unexplained cost is investigated; do not declare closure solely because the current view is empty.
- [ ] The `What this lab hid from me` notes and teardown lessons are committed without secrets.
- [ ] If closing the lab account, follow current provider documentation and support guidance; understand that account closure does not replace checking outstanding charges or retained resources.

A zero-looking cost view at one moment is not a guarantee that no delayed usage will appear. Re-check after the provider's documented reporting delay and investigate any later change.

---

## 13. Common mistakes

1. **Using the main personal/work account.** Use a dedicated lab account separated from real workloads.
2. **Skipping MFA until later.** Enable MFA for root and daily identities before creating resources.
3. **Trusting a “free” label.** Read the current eligibility, expiry, exclusions, and post-allowance terms.
4. **Forgetting other regions.** Inspect every region used and account for global resources.
5. **Leaving a managed cluster overnight.** Prefer kind; if real cloud is necessary, time-box and destroy the same day.
6. **Committing keys to Git.** Revoke exposed keys immediately, review activity, and inspect repository history and logs.
7. **Ignoring alerts.** Check cost and resource inventories; alerts can lag and are not caps.
8. **Creating resources without tags.** Apply a naming prefix and ownership/expiry tags where supported before provisioning.
9. **Deleting the cluster but not its dependencies.** Inspect load balancers, volumes, addresses, snapshots, logs, and other leftovers.
10. **Running `apply` in the wrong account or endpoint.** Confirm identity, region, provider configuration, and plan; for LocalStack use dummy credentials and explicit local endpoints.

---

## 14. Reference Sources

Use official documentation only. Console layouts and free-programme terms change; this guide does not claim that live pages were checked.

### AWS account, identity, and security
- AWS account management documentation
- AWS IAM documentation
- AWS security best practices documentation
- AWS root user security documentation
- AWS MFA documentation
- AWS temporary credentials and role-based access documentation

### AWS billing and free programme
- AWS Billing and Cost Management documentation
- AWS Free Tier documentation
- AWS Budgets documentation
- AWS cost anomaly detection documentation
- AWS free-tier usage alert documentation `[VERIFY current feature availability]`
- AWS pricing documentation
- AWS Well-Architected Framework — Cost Optimization pillar

### AWS resources and guardrails
- AWS service quotas documentation
- AWS resource tagging documentation
- AWS CloudTrail documentation
- AWS resource inventory and service-specific cleanup documentation
- AWS public IPv4 address, networking, storage, load balancing, and managed Kubernetes documentation

### Other providers
- Google Cloud Free Program documentation
- Google Cloud budgets and billing documentation
- Google Cloud IAM and security documentation
- Microsoft Azure free account documentation
- Microsoft Cost Management budgets and alerts documentation
- Microsoft Entra ID and MFA documentation

### Roadmap siblings
- `lab-environment-setup.md`
- `local-lab-kind-minikube-and-localstack.md`
- `production-devops-tooling-map.md`
- `Projects/01-production-readiness-baseline.md`

---

=====AUDIT REPORT=====

## Summary

This is a static content and safety review. No live provider pages were checked, no cloud account was opened, and no resource or billing configuration was created. The classifications describe editorial treatment, not a claim of external verification.

| Class | Approximate count | Meaning |
|---|---:|---|
| VERIFIED-STABLE | 35 claims | General cost-safety, identity-hygiene, tagging, and teardown principles that are stable at the conceptual level |
| VERIFY-AGAINST-DOCS | 27 claims | Current free-programme terms, console features, billing delay, resource lifecycle/billing behaviour, quotas, identity workflows, and provider-specific controls |
| REMOVED | 12 specifics | Stale free-tier amounts/durations, prices, assumed console click paths, unverified CLI/IaC snippets, guaranteed spending caps, and unsupported promises of zero charges |

Counts are approximate editorial counts, not an automated count of every factual statement.

## Audit findings and actions

| Item | Section | Issue found | Action taken |
|---|---|---|---|
| Free-tier terms | 1–3, 5, 12 | Amounts, credits, durations, and eligibility change | No numeric allowance or price stated; reader is told to check and record current terms |
| Budget alerts | 3, 5, 10, 13 | A budget can be mistaken for a hard cap | Repeatedly stated that budgets alert, billing data lags, and no cap guarantee exists |
| Account identity | 4 | Root or permanent keys could expose the account | Root MFA, no root keys, non-root daily identity, least privilege, and temporary-credential preference included |
| Billing console navigation | 4–5, 10 | Exact console paths can become stale | Described the goal instead of inventing click-by-click paths; marked current feature availability `[VERIFY]` |
| Cost anomalies/free usage | 5 | Availability and coverage vary by account/programme | Described concepts and required current documentation checks |
| Region and tags | 6–7 | Tags do not prevent charges and region scope can be misunderstood | Marked naming/tag values as proposed conventions and warned about global/regional differences |
| Leaked credentials | 6, 10, 13 | Removing a key from the latest file does not revoke it or remove history copies | Added immediate revocation, activity review, billing check, repository/log scan, and documentation steps |
| IaC destroy | 7, 9 | Destroy may not remove manually created or dependent resources | Added preflight checks, inventory, and leftover resource review |
| Expensive resources | 8–9 | Billing/lifecycle behaviour varies by service | Avoided prices and added risk levels, safer alternatives, teardown checks, and `[VERIFY]` |
| Incident response | 10 | Broad cleanup can cause data loss | Required identification and reviewed cleanup; account-wide tools need dry run and a dedicated lab account |
| Other providers | 11 | Free programmes differ and are restructured | Listed only concepts to locate in official docs; no terms or values asserted |
| Stage closure | 12 | Empty current cost view may not include delayed usage | Required follow-up checks and investigation of unexplained changes |
| Zero-cost guarantee | Throughout | No account setting guarantees no charges in every scenario | Explicitly stated residual risk and recommended local-only exercises when zero charge risk is unacceptable |

## Full `[VERIFY]` list

1. **Current AWS Free Tier programme, eligibility, credits/allowances, expiry, and post-allowance behaviour** — AWS Free Tier documentation.
2. **Current account signup and account-type constraints** — AWS account management documentation.
3. **Root-user MFA and root security settings in the current console** — AWS root user security and MFA documentation.
4. **Recommended daily identity approach and temporary credentials** — AWS IAM and temporary credentials/role documentation.
5. **Current Billing and Cost Management feature availability and navigation** — AWS Billing and Cost Management documentation.
6. **Budget types, alert thresholds, notification behaviour, and any available budget actions** — AWS Budgets documentation.
7. **Cost anomaly detection coverage, latency, and notification setup** — AWS cost anomaly detection documentation.
8. **Free-tier usage alert feature availability for the account's programme** — AWS Free Tier and billing documentation.
9. **Billing-data delay and cost-report refresh behaviour** — AWS Billing and Cost Management documentation.
10. **Service-specific billing meters and whether resources bill while idle/stopped** — relevant AWS pricing and service documentation.
11. **Data-transfer billing for internet, cross-AZ, and cross-region traffic** — AWS data-transfer pricing and networking documentation.
12. **Resource lifecycle and deletion behaviour for volumes, snapshots, public IPv4 addresses, load balancers, NAT gateways, registries, logs, KMS keys, hosted zones, and backups** — each corresponding AWS service's official documentation.
13. **Service quota availability and whether a quota can be changed** — AWS Service Quotas documentation.
14. **Tag support/limits and whether each resource type can be tagged at creation** — AWS resource tagging and service documentation.
15. **Organisation-level guardrails and their availability for a given account setup** — AWS Organizations and policy documentation.
16. **Current credential revocation, audit activity, and account incident workflow** — AWS IAM and CloudTrail documentation.
17. **Current managed Kubernetes control-plane and related resource billing** — AWS managed Kubernetes, compute, networking, and pricing documentation.
18. **Current database, backup, observability, security-service, and marketplace billing/lifecycle behaviour** — each relevant AWS service and marketplace documentation.
19. **Current GCP free programme, billing budgets, alerts, quotas, and project controls** — Google Cloud Free Program, billing, IAM, and quota docs.
20. **Current Azure free programme, budgets/alerts, subscription controls, and identity requirements** — Azure free account, Cost Management, and Microsoft Entra ID docs.
21. **Current support path for unexplained charges and account closure** — provider documentation and support.
22. **Any service or account-specific rule not listed above before creating a resource** — the relevant provider's official documentation.

## Confidence statement

**High:** local-first learning, MFA, least privilege, no keys in Git, pre-provision budgets, tagging, and explicit teardown are sound safety practices.  
**Medium:** resource-specific risk levels and cleanup lists are useful planning guidance but vary with current service behaviour and account configuration.  
**Not verified:** no live provider docs, console, free-tier eligibility, budget notification, cloud resource, or billing report was inspected.

## Run it yourself: five steps before creating any resource

1. **Read the current AWS Free Tier terms.** Determine the programme applicable to your account, eligible services, exclusions, expiry/credit rules, and what happens after an allowance ends. Record the date in `cloud-account-notes`; store no secrets there.
2. **Secure identity.** Enable root MFA, verify that root has no access keys, and create a daily non-root identity with MFA and least privilege.
3. **Create a budget and notifications.** Choose a low warning threshold, set an email you monitor, and confirm the configuration. Remember that budgets are alerts—not caps—and billing data lags.
4. **Test the tagging and teardown plan without provisioning.** Write the naming prefix, `project`/`owner`/`env`/`expires` tags where supported, resource inventory, region, and exact cleanup steps. Review the expensive-resource watchlist.
5. **Confirm alert delivery and account scope.** Use a provider-supported test if available; otherwise verify the notification configuration and recipient. Confirm the intended account and region, then decide whether the exercise can remain local. Do not create a cloud resource if any guardrail is unclear.
