# Prerequisites and Exit Criteria — Stage 2E

> A measurable Gate In and Gate Out for a zero-budget, lab-based Production DevOps & Platform Engineering stage.

- **Estimated self-assessment time:** 2–3 hours
- **Estimated gap-remediation time:** 1–4 weeks, depending on prior experience
- **Last reviewed:** 2026-10-24
- **Assumed tooling baseline:** a currently supported Kubernetes minor version, Linux/WSL2, Git, a container engine, Terraform/OpenTofu, and current compatible versions of the tools selected for each lab. Check upstream support policies before installing or upgrading.

## 1. Purpose of this file

This file defines objective entry and completion gates for Stage 2E. It is a self-assessment contract, not a promise of job readiness or certification success. Every Gate Out criterion must have an inspectable evidence artifact. Fast-moving tools and features must be checked against their current upstream documentation before use.

Use the free-lab principle throughout: prefer local clusters and local services. If a capability normally requires paid multi-region or managed infrastructure, demonstrate the failure mode locally and label it as a simulation.

## 2. How to use this file

1. **Self-assess:** run the diagnostic tests in Section 4 and record pass/fail evidence.
2. **Remediate:** for every failed test, review the named concept and rerun the test without copying a solution blindly.
3. **Start:** proceed when your score is at least 80%; at 60–79%, start only with a written remediation list; below 60%, finish prerequisite remediation first.
4. **Collect evidence:** save commands, manifests, test outputs, diagrams, decisions, and runbooks in the relevant module or project folder.
5. **Certify yourself:** complete the Stage Completion Checklist and verify that every module has an evidence artifact. This is a self-certification of demonstrated work, not an external credential.

## 3. Prerequisites (Gate In)

### Linux & shell

- **Skill:** navigate a Linux filesystem, inspect processes, permissions, environment variables, logs, and exit codes.
- **You are ready if you can…** find a file, inspect permissions, identify a process, redirect command output, and explain a non-zero exit status.
- **Remediation hint:** review shell navigation, quoting, pipes/redirection, permissions, processes, and signals.

### Networking

- **Skill:** reason about IP addresses, ports, DNS, HTTP(S), TLS, routing, and client/server connectivity.
- **You are ready if you can…** distinguish a DNS failure from a refused connection, identify the listening port of a local service, and use a client request to test an endpoint.
- **Remediation hint:** review DNS resolution, TCP ports, HTTP status codes, TLS certificates, and basic packet-flow reasoning.

### Git & collaboration

- **Skill:** use branches, commits, diffs, merges, and a reviewable change history.
- **You are ready if you can…** create a branch, commit a small change, inspect a diff, resolve a simple conflict, and revert a bad commit safely.
- **Remediation hint:** review the Git working tree, staging area, commits, branches, remotes, and pull-request workflow.

### Containers

- **Skill:** build and run images, inspect logs, map ports, pass configuration, and distinguish an image from a container.
- **You are ready if you can…** build a small image, run it, inspect its logs, stop it, and explain why a container exit does not necessarily mean the image is unusable.
- **Remediation hint:** review image layers, container lifecycle, bind mounts, environment variables, networking, and non-root execution.

### Programming/scripting

- **Skill:** read and modify a small Python or shell program, handle errors, use configuration, and write automated tests.
- **You are ready if you can…** write a script that validates input, returns a meaningful exit code, logs useful context, and has at least one automated test.
- **Remediation hint:** review functions, exceptions, structured logging, environment configuration, unit tests, and idempotent scripts.

### Cloud & IaC fundamentals

- **Skill:** understand identity and access management, regions/zones, networking, object storage, resource lifecycle, and declarative infrastructure.
- **You are ready if you can…** read an IaC plan, explain what would change before applying it, identify where state is stored, and describe least privilege.
- **Remediation hint:** review provider/resource/state concepts, variables and outputs, IAM roles, cost budgets/alerts, and teardown.

### Earlier-stage knowledge (2–2D, as skills)

- **Skill:** earlier stages (2–2D) should have given you practical data-pipeline, data-platform, and data-architecture context; exact prior file names are intentionally not assumed here.
- **You are ready if you can…** describe a pipeline's source, transformations, persistence layer, consumers, data-quality checks, and failure/replay implications.
- **Remediation hint:** revisit the relevant earlier-stage skills: pipeline lifecycle, data contracts, storage/compute separation, schema changes, and recovery from partial failure.

### Hardware & accounts

- **Skill:** operate a local Linux-compatible development environment without risking personal files or unexpected cloud charges.
- **You are ready if you can…** run a small local cluster, inspect resource usage, keep project files inside the intended workspace, and verify cloud resources are removed after a lab.
- **Practical baseline:** aim for 4 CPU cores, 8 GB RAM available to the environment, and 30 GB free disk for a minimal lab; more is helpful when running observability and multiple clusters together. These are planning targets, not guarantees that every stack will fit.
- **WSL2 notes:** keep repositories in a filesystem location appropriate for your workflow; verify Docker/container-engine integration and resource limits; restart or stop local clusters when not in use.
- **Free-tier readiness:** use local kind/minikube and LocalStack first. Cloud free tiers can change and may require payment details. Set budgets/alerts where available, avoid creating managed clusters for this stage, and inspect all resources before and after each lab.
- **Remediation hint:** read [free-tier-cloud-account-and-cost-safety.md](free-tier-cloud-account-and-cost-safety.md) and [lab-environment-setup.md](lab-environment-setup.md).

## 4. Self-assessment diagnostic

Run each test in a disposable directory or local lab. A test passes only when the stated pass signal is observed and you can explain why it occurred. Record output or a screenshot as evidence. Tests that depend on optional tools should be marked not-run and remediated before relying on that capability.

| # | Skill | Quick test (≤10 min) | Pass signal | Fail signal |
|---:|---|---|---|---|
| 1 | Shell navigation | Run `pwd`, `ls`, and `printf 'gate-in\n' > gate-in.txt`; then read the file. | The file contains exactly `gate-in`. | Wrong directory, missing file, or unexpected content. |
| 2 | Exit codes | Run `python -c "raise SystemExit(7)"` and inspect the immediately following exit status using your shell's supported method. | The Python process exits with status 7. | You cannot observe or explain the status. |
| 3 | Process inspection | Start a long-running local command, identify its PID, and stop only that process. | You identify the intended process and confirm it exits. | You cannot distinguish it from unrelated processes. |
| 4 | Network listener | Start a local HTTP server on a chosen unused port and request it from the same machine. | The client receives an HTTP response from the server. | Connection fails and you cannot diagnose why. |
| 5 | DNS vs connectivity | Resolve a known hostname, then request its HTTPS endpoint if internet access is available. | You can distinguish name-resolution output from HTTP response status. | You treat DNS, TCP, TLS, and HTTP as the same failure layer. |
| 6 | Git diff | Initialize a temporary repository, commit one file, change it, and inspect `git diff`. | The diff shows only the intended change. | The change is untracked/unexplained or the diff is misunderstood. |
| 7 | Container lifecycle | Build and run a tiny containerized program, inspect logs, then stop/remove it. | You can show image and container lifecycle separately. | You cannot locate logs or determine container state. |
| 8 | Non-root/container config | Inspect the user configured by a small container image and identify where configuration enters. | You can state the effective user and configuration source. | The image runs as root by accident or configuration is hard-coded without explanation. |
| 9 | Python test | Write a small function and one pytest test, then run the test. | The test passes; deliberately breaking the expected value makes it fail. | The test cannot detect the deliberate defect. |
| 10 | HTTP diagnosis | Request a local endpoint that returns a known status, such as a deliberately missing path. | You observe the expected HTTP status and distinguish it from a connection error. | You cannot explain the difference. |
| 11 | YAML hygiene | Parse a small Kubernetes manifest using a locally installed YAML-aware tool or `kubectl` client-side validation. | The manifest parses; a deliberately malformed version is rejected. | Both valid and malformed versions are treated as valid. |
| 12 | Kubernetes context | Run `kubectl config current-context` and list namespaces in a disposable local cluster. | The context is the intended local cluster and namespaces are returned. | You cannot identify which cluster the command targets. |
| 13 | Kubernetes rollout | Deploy a tiny workload and inspect its rollout status. | The rollout completes and the workload becomes ready. | It remains unavailable and you cannot inspect events/logs. |
| 14 | Resource controls | Add CPU/memory requests and limits to a test workload and inspect the admitted pod specification. | The pod specification contains the configured values. | The values are absent or placed at the wrong level. |
| 15 | IaC plan discipline | In a disposable IaC directory, initialize and create a plan using a safe local provider/configuration. | You can inspect the proposed changes without applying them. | You apply changes without reviewing the plan or cannot explain state. |
| 16 | Secret hygiene | Search a temporary Git repository for a deliberately planted fake token, then remove it and check the diff. | You detect and remove the fake value; no real credential is used. | You commit the fake token or cannot explain why secrets should not be committed. |
| 17 | Observability | Generate a known request and find its corresponding metric or log in a local stack. | The signal is present and you can identify its time/window. | The request cannot be correlated to any useful signal. |
| 18 | Recovery thinking | Back up a small file, delete the working copy, restore it, and compare checksums. | Restored checksum matches the original. | No verified restore exists. |

**Scoring rule:** one point per passed test; exclude no tests from the denominator. If a test cannot be run because the tool is not installed, count it as not passed and record the installation/remediation action. **14–18 (≥80%)**: start. **11–13 (60–79%)**: start with a written remediation list and address gaps before the related module. **0–10 (<60%)**: complete prerequisite remediation first.

## 5. Gate-In decision matrix

| Decision | Rule | Recommended action |
|---|---|---|
| **Ready** | At least 80% of diagnostic tests pass and no critical safety gap remains around Git, container basics, cluster context, or cloud-cost controls. | Start Stage 2E and preserve evidence as you go. |
| **Ready with remediation** | 60–79% pass, or one non-critical skill gap is clearly bounded and has a remediation plan. | Start only the modules whose prerequisites are met; schedule and retest gaps before dependent labs. |
| **Not ready** | Below 60%, or you cannot safely identify the active cluster/account, manage credentials, or tear down resources. | Stop infrastructure labs; remediate fundamentals and repeat the diagnostic. |

## 6. Exit criteria (Gate Out)

Complete every criterion in each module. An artifact is evidence only when another person—or you after a break—can inspect it and reproduce the result from its instructions. Save credentials, private keys, access tokens, and other secrets nowhere in the evidence repository.

### 01-Container-Image-Engineering-and-Registry-Hygiene

- **Confidence:** High
- **Free-lab environment:** Docker/Podman locally; local image archive or local registry.
- **Exit criteria:**
  - I can build a non-root image.
  - I can explain and reduce image layers and size.
  - I can scan the image and record findings.
  - I can generate an SBOM and sign or document a locally simulated signing flow.
  - I can deploy by immutable digest rather than a mutable tag..
- **Evidence artifact:** Image build file, scan output, SBOM, digest-pinned deployment manifest, and remediation notes.
- **Pass rule:** every criterion is demonstrated, the evidence is committed or otherwise safely retained, and the lab can be reproduced from its README/runbook.

### 02-CI-CD-Pipeline-Engineering

- **Confidence:** High
- **Free-lab environment:** Local Git repository and a free CI tier or local runner.
- **Exit criteria:**
  - I can create a pipeline that runs formatting, linting, unit tests, and image build.
  - I can fail the pipeline when a required check fails.
  - I can cache dependencies safely.
  - I can publish an artifact only after gates pass.
  - I can demonstrate rollback to a known-good release..
- **Evidence artifact:** Pipeline configuration, passing run, intentionally failing run, artifact metadata, and rollback log.
- **Pass rule:** every criterion is demonstrated, the evidence is committed or otherwise safely retained, and the lab can be reproduced from its README/runbook.

### 03-Production-Kubernetes-Operations

- **Confidence:** High
- **Free-lab environment:** kind or minikube.
- **Exit criteria:**
  - I can deploy a workload with requests and limits.
  - I can configure startup, readiness, and liveness probes appropriately.
  - I can diagnose a deliberately broken pod.
  - I can demonstrate a rolling update and rollback.
  - I can explain disruption budgets and node drain limitations in a local cluster..
- **Evidence artifact:** Manifests, command transcripts, failure diagnosis, rollout/rollback evidence, and operational notes.
- **Pass rule:** every criterion is demonstrated, the evidence is committed or otherwise safely retained, and the lab can be reproduced from its README/runbook.

### 04-Kubernetes-Networking-Ingress-and-Service-Mesh

- **Confidence:** Medium (verify against current docs)
- **Free-lab environment:** kind/minikube with a compatible CNI and ingress/Gateway implementation; mesh can be a local simulation.
- **Exit criteria:**
  - I can trace pod-to-pod and service traffic.
  - I can write and test a NetworkPolicy where the local CNI supports it.
  - I can expose an application through Ingress or Gateway API supported by the chosen cluster.
  - I can document TLS termination.
  - I can explain when mTLS/service mesh complexity is justified..
- **Evidence artifact:** Network diagram, policy tests, routing/TLS manifests, and a note on unsupported local capabilities.
- **Pass rule:** every criterion is demonstrated, the evidence is committed or otherwise safely retained, and the lab can be reproduced from its README/runbook.

### 05-Kubernetes-Storage-and-Stateful-Data-Workloads

- **Confidence:** High
- **Free-lab environment:** kind/minikube storage provisioner and local filesystem.
- **Exit criteria:**
  - I can create and bind a PVC.
  - I can deploy a StatefulSet.
  - I can demonstrate persistence across pod replacement.
  - I can create a supported local snapshot or a documented file-level backup.
  - I can restore data and verify it with a checksum or query..
- **Evidence artifact:** PVC/StatefulSet manifests, persistence test, backup artifact, restore log, and verification result.
- **Pass rule:** every criterion is demonstrated, the evidence is committed or otherwise safely retained, and the lab can be reproduced from its README/runbook.

### 06-Helm-Kustomize-and-Kubernetes-Packaging

- **Confidence:** High
- **Free-lab environment:** Local Helm and kubectl/kustomize.
- **Exit criteria:**
  - I can package an app with Helm.
  - I can render and inspect templates.
  - I can create Kustomize base and environment overlays.
  - I can compare rendered output.
  - I can document which configuration belongs in values/patches versus the application image..
- **Evidence artifact:** Chart, values files, Kustomize overlays, rendered manifests, and comparison notes.
- **Pass rule:** every criterion is demonstrated, the evidence is committed or otherwise safely retained, and the lab can be reproduced from its README/runbook.

### 07-Advanced-Infrastructure-as-Code-and-Cloud-Operations

- **Confidence:** High
- **Free-lab environment:** OpenTofu/Terraform with local provider or LocalStack; optional cloud free tier only after cost controls.
- **Exit criteria:**
  - I can define reusable Terraform/OpenTofu configuration.
  - I can separate variables and outputs.
  - I can use state safely and keep secrets out of state where feasible.
  - I can run plan before apply.
  - I can detect and explain drift.
  - I can destroy lab resources and verify cleanup..
- **Evidence artifact:** IaC module, plan output, drift exercise, state-handling notes, and teardown evidence.
- **Pass rule:** every criterion is demonstrated, the evidence is committed or otherwise safely retained, and the lab can be reproduced from its README/runbook.

### 08-GitOps-and-Progressive-Delivery

- **Confidence:** Medium (verify against current docs)
- **Free-lab environment:** kind/minikube; Argo CD or Flux; progressive delivery may be simulated if an add-on is unavailable.
- **Exit criteria:**
  - I can reconcile a cluster from Git using Argo CD or Flux.
  - I can demonstrate drift correction.
  - I can promote a change through environments.
  - I can simulate canary or blue/green rollout and define abort criteria.
  - I can restore the previous desired state..
- **Evidence artifact:** GitOps configuration, reconciliation evidence, rollout comparison, and rollback/abort record.
- **Pass rule:** every criterion is demonstrated, the evidence is committed or otherwise safely retained, and the lab can be reproduced from its README/runbook.

### 09-Secrets-and-Identity-Management

- **Confidence:** High
- **Free-lab environment:** Local cluster and local secret store; cloud identity can be represented by a written simulation.
- **Exit criteria:**
  - I can keep secrets out of Git and container images.
  - I can inject a local secret through a supported secret mechanism.
  - I can rotate a test secret and prove the old value no longer works.
  - I can apply least-privilege service-account/RBAC rules.
  - I can explain workload identity versus long-lived cloud keys..
- **Evidence artifact:** Secret-handling procedure, rotation test, RBAC manifests, and repository/image secret scan evidence.
- **Pass rule:** every criterion is demonstrated, the evidence is committed or otherwise safely retained, and the lab can be reproduced from its README/runbook.

### 10-Site-Reliability-Engineering-and-Incident-Management

- **Confidence:** High
- **Free-lab environment:** Local app plus synthetic traffic and local monitoring.
- **Exit criteria:**
  - I can define a user-relevant SLI and SLO.
  - I can calculate an error budget from stated assumptions.
  - I can write an actionable alert and runbook.
  - I can run an incident game day.
  - I can produce a blameless postmortem with timeline, contributing factors, and owned actions..
- **Evidence artifact:** SLI/SLO document, alert rule, runbook, incident timeline, postmortem, and action tracker.
- **Pass rule:** every criterion is demonstrated, the evidence is committed or otherwise safely retained, and the lab can be reproduced from its README/runbook.

### 11-Production-Observability-Stack-and-Performance-Operations

- **Confidence:** High
- **Free-lab environment:** Local Prometheus/Grafana and OpenTelemetry-compatible components; lightweight setup preferred.
- **Exit criteria:**
  - I can instrument or scrape service metrics.
  - I can centralize structured logs.
  - I can capture a trace where supported.
  - I can correlate a request across signals.
  - I can diagnose a deliberately introduced latency/error issue.
  - I can tune an alert to reduce noise and include actionable context..
- **Evidence artifact:** Dashboard/export, sample logs and traces, fault-injection notes, alert test, and diagnosis report.
- **Pass rule:** every criterion is demonstrated, the evidence is committed or otherwise safely retained, and the lab can be reproduced from its README/runbook.

### 12-Production-Security-and-Software-Supply-Chain

- **Confidence:** Medium (verify against current docs)
- **Free-lab environment:** Local tools; Sigstore/cosign and SLSA concepts checked against current project docs.
- **Exit criteria:**
  - I can threat-model the delivery path.
  - I can scan dependencies and images.
  - I can generate and retain an SBOM.
  - I can pin important dependencies/artifacts.
  - I can demonstrate signature verification or document the local trust setup.
  - I can create a remediation record with severity and owner..
- **Evidence artifact:** Threat model, scan reports, SBOM, verification transcript, and tracked remediation items.
- **Pass rule:** every criterion is demonstrated, the evidence is committed or otherwise safely retained, and the lab can be reproduced from its README/runbook.

### 13-Backup-Disaster-Recovery-and-Resilience-Testing

- **Confidence:** High
- **Free-lab environment:** Local volumes and filesystem; restore test in a fresh local namespace/cluster.
- **Exit criteria:**
  - I can define data-loss and recovery objectives.
  - I can back up application data and required configuration.
  - I can restore into a clean environment.
  - I can measure elapsed recovery time.
  - I can calculate observed data loss against the chosen RPO.
  - I can record gaps and corrective actions..
- **Evidence artifact:** Backup, restore procedure, timestamps, checksum/query verification, measured RTO/RPO, and review notes.
- **Pass rule:** every criterion is demonstrated, the evidence is committed or otherwise safely retained, and the lab can be reproduced from its README/runbook.

### 14-Multi-Cluster-and-Multi-Region-Operations

- **Confidence:** Medium (verify against current docs)
- **Free-lab environment:** Two kind clusters or two local contexts; explicitly a simulation, not proof of cloud-region resilience.
- **Exit criteria:**
  - I can create or document two isolated clusters.
  - I can deploy equivalent workloads.
  - I can simulate primary-cluster failure.
  - I can redirect a test client or manually switch the endpoint.
  - I can measure recovery.
  - I can document differences between this simulation and real multi-region service..
- **Evidence artifact:** Two-cluster manifests, failover runbook, test timeline, observed recovery, and limitations.
- **Pass rule:** every criterion is demonstrated, the evidence is committed or otherwise safely retained, and the lab can be reproduced from its README/runbook.

### 15-Platform-Capacity-Compute-Economics-and-FinOps

- **Confidence:** High
- **Free-lab environment:** Local metrics plus spreadsheet or script; all prices clearly marked hypothetical unless sourced.
- **Exit criteria:**
  - I can estimate CPU, memory, storage, and request volume from explicit assumptions.
  - I can compare requests/limits with observed usage.
  - I can calculate unit cost using declared hypothetical prices.
  - I can identify idle resources and cost guardrails.
  - I can verify the lab is torn down..
- **Evidence artifact:** Capacity worksheet, usage observations, unit-economics assumptions, and cost/teardown checklist.
- **Pass rule:** every criterion is demonstrated, the evidence is committed or otherwise safely retained, and the lab can be reproduced from its README/runbook.

### 16-Platform-Engineering-and-Internal-Developer-Platforms

- **Confidence:** Medium (verify against current docs)
- **Free-lab environment:** Local Git repository; Backstage/Crossplane or policy tools are optional and version-sensitive.
- **Exit criteria:**
  - I can define a small golden path for creating and deploying a service.
  - I can provide a reusable template with safe defaults.
  - I can document developer inputs and platform-owned responsibilities.
  - I can add a validation step.
  - I can measure a simple developer outcome such as steps or time to first successful deploy..
- **Evidence artifact:** Template repository, golden-path README, policy/validation checks, and a short usability test.
- **Pass rule:** every criterion is demonstrated, the evidence is committed or otherwise safely retained, and the lab can be reproduced from its README/runbook.

### 17-Production-DevOps-Integrated-Capstone

- **Confidence:** High
- **Free-lab environment:** Local kind/minikube, local tooling, and optional LocalStack; no paid infrastructure required.
- **Exit criteria:**
  - I can deploy a service through the full tested pipeline.
  - I can reconcile desired state from Git.
  - I can apply identity and security controls.
  - I can demonstrate metrics/logs/alerts.
  - I can execute a failure, rollback, backup restore, and teardown.
  - I can map every acceptance criterion to evidence..
- **Evidence artifact:** Capstone repository, architecture diagram, runbooks, CI/GitOps evidence, incident report, restore evidence, and signed-off checklist.
- **Pass rule:** every criterion is demonstrated, the evidence is committed or otherwise safely retained, and the lab can be reproduced from its README/runbook.

## 7. Cross-cutting competencies

- **Troubleshooting method:** state the symptom, scope, recent change, hypotheses, discriminating test, result, and next action. Preserve evidence before changing the system.
- **Reading telemetry:** distinguish symptoms from causes; correlate metrics, logs, traces, events, and deployment changes by time and request/workload identity.
- **Runbook writing:** include trigger, impact, prerequisites, safe diagnostic commands, decision points, rollback/recovery steps, and verification.
- **Blameless review:** describe system conditions and contributing factors, not personal blame; give every corrective action an owner and a review date.
- **Automation over manual work:** encode repeatable checks and deployment steps; keep manual interventions documented and auditable.
- **Security by default:** least privilege, non-root containers, secret hygiene, dependency/image scanning, provenance where feasible, and explicit trust boundaries.
- **Cost awareness:** estimate resource consumption before provisioning, use local simulations, label hypothetical prices, and verify teardown.
- **Documentation quality:** a new reader can reproduce the lab, understand expected outcomes, find evidence, and clean up safely.

## 8. Stage completion checklist

- [ ] Gate-In diagnostic score and remediation record are saved.
- [ ] Local lab setup and cost-safety instructions have been reviewed.
- [ ] Module 01 evidence artifact exists and passes review.
- [ ] Module 02 evidence artifact exists and passes review.
- [ ] Module 03 evidence artifact exists and passes review.
- [ ] Module 04 evidence artifact exists and passes review.
- [ ] Module 05 evidence artifact exists and passes review.
- [ ] Module 06 evidence artifact exists and passes review.
- [ ] Module 07 evidence artifact exists and passes review.
- [ ] Module 08 evidence artifact exists and passes review.
- [ ] Module 09 evidence artifact exists and passes review.
- [ ] Module 10 evidence artifact exists and passes review.
- [ ] Module 11 evidence artifact exists and passes review.
- [ ] Module 12 evidence artifact exists and passes review.
- [ ] Module 13 evidence artifact exists and passes review.
- [ ] Module 14 evidence artifact exists and passes review.
- [ ] Module 15 evidence artifact exists and passes review.
- [ ] Module 16 evidence artifact exists and passes review.
- [ ] Module 17 capstone evidence artifact exists and passes review.
- [ ] Capstone acceptance criteria are mapped to observable evidence.
- [ ] Capstone deployment can be recreated from documented instructions.
- [ ] CI checks include at least one demonstrated failing case.
- [ ] Rollback has been tested, not merely described.
- [ ] A backup restore has been tested and verified.
- [ ] A deliberate failure/incident exercise and blameless postmortem are complete.
- [ ] Secrets and credentials are absent from committed evidence.
- [ ] Project 01 production-readiness baseline audit is complete: [Projects/01-production-readiness-baseline.md](Projects/01-production-readiness-baseline.md).
- [ ] Every temporary namespace, cluster, container, volume, local service, and cloud resource has been inventoried.
- [ ] Full teardown is complete and verified.
- [ ] Cloud billing/resource consoles have been checked and spend confirmed as $0 for the labs, where cloud was used.
- [ ] Final README links all 17 evidence artifacts and states known limitations.

## 9. Proficiency levels

| Level | Observable behaviour | Stage exit? |
|---|---|---|
| **Beginner** | Follows instructions but cannot reliably diagnose failures or explain the changes being made. | No |
| **Working** | Completes normal tasks and can fix familiar failures with documentation; evidence or rollback may be incomplete. | No |
| **Production-Ready** | Reproduces deployments, diagnoses controlled failures, uses safe defaults, tests rollback/recovery, documents operational decisions, and supplies evidence for all 17 modules. | **Minimum required** |
| **Staff-Level** | Defines platform standards, evaluates cross-team trade-offs, anticipates failure domains, improves developer experience and operational economics, and leads reviews using measurable evidence. | Not required for this stage |

Self-rating is not independent validation. For stronger evidence, ask a peer to reproduce one module from the README without coaching and report any missing steps.

## 10. Common gaps & failure patterns

- **Copy-paste YAML without understanding it:** explain every non-obvious field and prove the manifest renders and behaves as intended.
- **Using mutable image tags in deployment manifests:** record the built digest and deploy the digest where the workflow supports it.
- **Treating a passing pipeline as sufficient:** include a controlled failing case and prove required gates block promotion.
- **Using liveness probes as readiness checks:** assign each probe a distinct purpose and verify that a dependency outage does not cause a restart loop.
- **Applying IaC without reviewing the plan:** inspect the plan and state implications before every apply; use disposable resources for experiments.
- **Never testing restores:** delete or isolate the test copy, restore to a clean target, verify content, and measure elapsed time.
- **Secrets in Git, logs, or images:** use a fake credential for the exercise, scan for it, rotate it, and document prevention controls.
- **Alerts with no action:** define severity, owner, runbook, and a condition that warrants human action; remove duplicate/noisy alerts.
- **Claiming multi-region resilience from a local demo:** label the test as a simulation and document real cloud dependencies it does not prove.
- **Skipping teardown:** use a written resource inventory and verify cluster, volume, and cloud-resource deletion.
- **Overbuilding the lab stack:** start with one service and add components only when they test a stated requirement.
- **Evidence that cannot be reproduced:** include versions/assumptions, exact commands, expected signals, failure cases, and cleanup instructions.

## 11. What comes next

- Consider CKA/CKAD/CKS as optional ways to structure Kubernetes practice; check current official certification pages before making a plan.
- Terraform Associate may help organize IaC learning; confirm the current exam scope and requirements from the official provider.
- An AWS associate-level learning path can build cloud operations context, but use free-tier safeguards and verify current terms before provisioning.
- The next roadmap stages should connect this operational foundation to ML-platform and MLOps work: model deployment, experiment/model lifecycle, data/model observability, and controlled release practices.
- Certifications do not replace demonstrable projects, incident reasoning, recovery evidence, and sound engineering judgment.

## 12. Reference Sources

Use these as authoritative sources to confirm against. No URL is embedded because upstream documentation paths and product details can change.

### Kubernetes and container operations

- Kubernetes Documentation: Workloads, Probes, Resource Management, Pod Disruption Budgets, Network Policies, Storage, Security, Debugging, and Cluster Administration.
- Kubernetes release and version-skew/support policy documentation.
- Docker Documentation or Podman Documentation for image builds, containers, and image security.
- Helm Documentation and Kustomize Documentation.

### CI/CD, GitOps, and progressive delivery

- Git Documentation.
- Argo CD Documentation and Flux Documentation.
- Argo Rollouts Documentation, if selected; verify current support and installation requirements.
- DORA research on software delivery performance metrics.

### Infrastructure as Code and cloud

- Terraform Documentation and OpenTofu Documentation.
- AWS, Azure, and Google Cloud official documentation for IAM, billing, budgets, resource cleanup, and free-tier terms, as applicable.
- LocalStack Documentation for local cloud-service simulation.

### Reliability, observability, and incident management

- Google SRE Book and Site Reliability Engineering Workbook, including SLI/SLO and error-budget concepts.
- Prometheus Documentation and Grafana Documentation.
- OpenTelemetry Documentation.
- CNCF project documentation for the selected observability and platform components.

### Security and software supply chain

- Sigstore/cosign Documentation.
- SLSA Specification and Build Levels documentation.
- Kubernetes security documentation and the selected image/dependency scanner's official documentation.
- OWASP guidance relevant to application and supply-chain security.

### Platform engineering and policy

- Backstage Documentation, if selected.
- Crossplane Documentation, if selected.
- Open Policy Agent and Kyverno Documentation, if selected; verify APIs and version compatibility.

---

**Maintenance rule:** before each new cohort or major tool upgrade, re-check fast-moving commands, APIs, feature availability, support windows, and free-tier terms. Update the review date only after that review is actually performed.
