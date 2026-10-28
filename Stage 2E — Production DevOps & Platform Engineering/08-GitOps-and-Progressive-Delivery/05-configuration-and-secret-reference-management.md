# Unit 5 — Configuration and Secret Reference Management

**Target file:** `05-configuration-and-secret-reference-management.md` | **Module:** M08 | **Stage:** 2E — Production DevOps & Platform Engineering  
**Estimated time:** 12–20 hours including Labs A–E; allow additional time for local Docker/Git networking troubleshooting.  
**Prerequisites:** M01–M07; Git, `kubectl`, `kind`, Kustomize, basic Helm, Kubernetes Deployments/ConfigMaps/Secrets/RBAC, and M08 Units 1–4.  
**Core tools:** Git, Docker, `kind`, `kubectl`, Flux CLI/controllers, SOPS, age, Python 3, and PyYAML for the policy-check lab.  
**Awareness:** Sealed Secrets, External Secrets Operator (ESO), Secrets Store CSI Driver, Vault Agent, cloud KMS/workload identity, admission policy. **M09 owns deep secret lifecycle and identity implementation.**  
**Last reviewed:** 2026-10-28. Official documentation links listed in §5.25 were consulted for the claims noted there.  
**Tool baseline assumed:** Linux/WSL2 Ubuntu; current stable Flux CLI/controller and SOPS/age releases available on the day of the lab. Pin and record exact versions before use; exact installer URLs, flags, and compatibility must be checked against the official docs marked `[VERIFY]`. No binaries were installed or live commands run while authoring this lesson.  
**Footprint:** Approximately 4 CPU cores, 8 GB RAM, and 10–20 GB free disk depending on images. Run only one local `kind` cluster and a lightweight local Git server. Stop unrelated Argo CD, monitoring, or other lab controllers to preserve memory. All values and keys are synthetic and `LAB-ONLY`.

> **Safety contract.** Use a disposable repository and a disposable cluster. Before every cluster mutation, run `kubectl config current-context` and confirm it is the specifically named lab context. Never use production credentials or real user data. Never print decoded secret data. A local lab is not evidence of production security, provider auditability, or regulatory compliance. Expected outputs are representative, not captured from a live run.

## 5.0 Why this matters in production

Imagine an engineer commits a Kubernetes `Secret` manifest to a private GitOps repository. The values are base64 encoded, so the diff looks opaque. A CI job clones the repository, a developer forks it to debug a release, and a log archive retains the rendered YAML. Later, the repository is made public briefly or a collaborator account is compromised. Deleting the manifest in a follow-up commit does not retract the old commit, clone, cache, fork, build artifact, or log. Meanwhile, a GitOps controller may continue applying the credential, and an application may continue using it until a safe rotation reaches the workload.

The failure is not “GitOps is unsafe.” GitOps needs versioned desired state. The failure is putting a reusable secret value into a system designed to replicate and retain source history. A safer design keeps non-sensitive desired state in Git and stores either **ciphertext** or a **reference** in the repository. Decryption keys and provider credentials enter through a separately controlled trust path. Access is scoped, rotation is rehearsed, and evidence proves that the new value reached its consumer.

Three outcomes must not be confused:

1. **Remove a value from the latest tree:** stops future desired state from containing it, but does not invalidate the credential.
2. **Purge old Git history and caches:** reduces future discoverability where copies can be controlled, but cannot guarantee that all copies disappear.
3. **Rotate or revoke the credential at its source:** makes the exposed value unusable, which is the essential response to a real leak.

This unit teaches the GitOps integration and operating model. M09, *Secrets and Identity Management*, owns deeper Vault architecture, dynamic secrets, cloud identity federation, CSI and ESO provider implementations, and full lifecycle engineering. M08 introduces one pattern hands-on so you can understand the control flow and its limits.

## 5.1 Learning objectives

After completing the lesson, you should be able to:

- **[L1]** Classify a value as configuration, secret, or identity based on disclosure impact—not its variable name.
- **[L1]** Explain why base64 is not encryption, why Git history persists, and why deletion is not revocation.
- **[L1]** Compare encrypted-in-Git, reference-in-Git/value-elsewhere, and runtime retrieval/workload identity patterns.
- **[L2]** Encrypt a synthetic Kubernetes Secret with SOPS and age, commit only ciphertext, and configure Flux native SOPS decryption for a disposable cluster.
- **[L2]** Prove that a workload can consume a mounted secret without printing its value, while confirming the secret never appears in the Git tree.
- **[L2]** Run a local policy check that rejects unapproved plaintext Kubernetes Secret manifests without echoing detected values.
- **[L3]** Draw the root-of-trust and secret-zero paths, scope controller identities, define key backup/recovery, and separate development from production decryption authority.
- **[L3]** Design source-secret rotation, encryption-key rotation, and application reload as separate but coordinated operations.
- **[L4]** Respond to a leaked secret, key loss, over-privileged store, or stale consumer with containment, recovery, evidence, and prevention steps.
- **[L4]** Define a platform golden path, ownership model, and migration plan from plaintext/base64 secrets in Git to an approved pattern.

**Depth boundary:** SOPS + age + Flux is the selected local implementation. Sealed Secrets and ESO/CSI are compared at Awareness level. Vault, cloud KMS, workload identity/OIDC, admission-policy implementation, and organization-wide secret lifecycle are handed off to M09/M12/M16.

## 5.2 Concept map and vocabulary

### Mental model

Git stores the **desired deployment contract**, not every sensitive input needed to execute it. In the chosen pattern, Git stores an encrypted Secret manifest and a public age recipient. A private age identity is provisioned separately into the Flux controller namespace. Flux downloads the source, builds manifests, decrypts the SOPS-protected values in the reconciliation path, and applies the Kubernetes Secret. Kubernetes then exposes that value only to workloads explicitly configured to consume it. Each transition is a trust boundary.

```text
Developer workstation
  fake plaintext exists briefly outside repo
        | SOPS encrypts using public age recipient
        v
Git repository: manifests + ciphertext + public recipient/config
        | Git read identity; repository review + secret scan
        v
Flux source-controller -> source artifact/cache [sensitive metadata]
        | kustomize-controller + SOPS decryption
        | reads private age identity from a Kubernetes Secret
        v
Kubernetes API -> Secret object -> etcd [protect with RBAC + encryption at rest]
        | only referenced by authorized workload/container
        v
scoring-api mounts a file and reads it without logging the value

Trust roots: private age identity / cluster API authorization / Git read access
Evidence: Git revision, reconciliation condition, policy result, rotation record
```

The private age key must not be in the repository or in a CI log. In this local exercise, the key is created outside the repository and injected into the `flux-system` namespace as a Kubernetes Secret. That is a bootstrap convenience, not a production key-custody design: a production cluster administrator who can read that Secret may obtain the key. M09 should replace this with a reviewed custody, identity, and recovery design appropriate to the organization.

### Vocabulary

| Term | Precise definition | Common misconception |
|---|---|---|
| Configuration | Non-sensitive settings needed to shape behavior, such as log level, replica count, or a non-private endpoint. | “Anything in an environment variable is configuration.” Sensitivity depends on the value and consequence of disclosure. |
| Secret value | Confidential data whose disclosure or misuse can cause harm: passwords, API tokens, private keys, database credentials. | “If it is base64, it is protected.” Base64 is reversible encoding. |
| Identity | A principal used to authenticate and authorize actions: Kubernetes ServiceAccount, federated workload identity, or human identity. | “A token and an identity are the same thing.” A token is one possible credential for an identity. |
| Ciphertext | Encrypted representation of data; readable without the key only as encrypted structure/metadata. | “Ciphertext is safe regardless of key handling.” Key compromise can expose retained ciphertext history. |
| Secret reference | A pointer to an external secret, such as a provider path and property. | “The `ExternalSecret` contains the value.” It describes where/how to obtain it. |
| Kubernetes Secret | API object used to distribute confidential data to authorized workloads. Its data fields are base64 encoded in serialized YAML/API representation. | “Creating a Secret automatically encrypts etcd.” Encryption at rest must be configured and verified separately. |
| Root of trust | Key, identity provider, controller key, or external service whose compromise enables decryption or retrieval. | “The tool is the root of trust.” The tool is only as strong as its key custody and authorization. |
| Secret zero | The first credential/key needed to let the system obtain or decrypt other secrets. | “Bootstrap credentials can safely be stored with the ciphertext.” That creates a circular trust failure. |
| Rotation | Replacing a secret value or key and proving dependent consumers use the new one. | “Changing a Kubernetes Secret means the process uses the new value.” The app may need restart/reload. |
| Reconciliation | A controller repeatedly attempts to make actual cluster state match declared desired state. | “Reconciliation validates that a secret is correct or safe.” It can apply an unsafe value faithfully. |
| Secret leakage | Unauthorized exposure of a value or the means to decrypt it. | “Deleting the file un-leaks it.” Rotate/revoke the value first. |

### Rotation and reconciliation sequence

```text
1. Secret owner rotates/revokes source credential
2. Update encrypted Git representation or external reference
3. Review/policy checks pass; commit is merged
4. GitOps controller fetches revision and decrypts/resolves the value
5. Kubernetes Secret/CSI materialization changes
6. Workload reload/restart mechanism activates the new value
7. Smoke test proves the old credential fails and new one works
8. Evidence records source revision, check IDs, owner, time, and result
```

If step 6 is missing, Kubernetes may hold the new value while the process keeps the old one. If step 7 is missing, “reconciled” is not proof that the application can authenticate.

## 5.3 The threat model: what belongs in Git and what does not

### Classification rule

Ask: *If a person outside the intended trust boundary can read or replay this value, what can they do?* A field named `endpoint` can still be sensitive if it embeds a token or reveals a private management plane. A field named `password` in a synthetic test fixture is not a production secret, but should still be clearly marked and isolated. Classification is about consequence, not naming convention.

| Asset | Actor or accident | Attack path / impact | Preventive control | Detective control | Recovery and evidence |
|---|---|---|---|---|---|
| Database/API credential | Contributor accidentally commits value | Git history, clone, fork, CI artifact; unauthorized access | SOPS/reference pattern; least-privilege write access; secret scanning | Pre-commit + CI scanner; provider access logs | Revoke/rotate first; inspect use; sanitized incident timeline and rotation record |
| Age private key | Repo admin or malicious contributor | Key stored beside ciphertext decrypts historical secrets | Keep private key outside Git; restricted custody and backup | Repository scanner/policy; access review | Rotate underlying secret values if key exposed; replace key and re-encrypt; evidence of recipients and recovery test |
| Flux controller identity | Compromised controller or cluster admin | Can decrypt/apply values within its authority | Separate per environment; scoped namespace/RBAC; protect controller namespace | Audit API reads and controller changes where available | Contain identity, rotate keys, restore approved controller config, capture access review |
| External store credential | Overbroad provider role | One reference retrieves every team’s secret | Per-namespace/per-service identity and least privilege | Provider audit logs and periodic access tests | Disable/replace identity; narrow policies; record negative tests |
| Kubernetes Secret in etcd | Unauthorized API/etcd access | Base64 values exposed if not encrypted at rest | RBAC, TLS, encryption-at-rest configuration, backup protection | Configuration audit and access logs | Rotate exposed values; validate encryption config; preserve incident evidence |
| Workload environment/file | Debugging, crash dump, log statement | Process or mounted value leaks | Minimize consumers; avoid logging; file permissions; no shell tracing | Log scans, runtime audit where available | Rotate value; fix consumer; add regression test |
| CI build context/artifact | Build args, copied `.env`, verbose logs | Secret copied into image layer/cache or retained artifacts | BuildKit secret mounts or provider-native injection; exclude local files | Image/config scan; CI artifact review | Rebuild clean image after rotate; purge artifacts where feasible; verify no value remains |

### What belongs in Git?

Generally appropriate: ConfigMaps containing non-sensitive settings; environment overlays; a SOPS-encrypted Secret whose values are actually encrypted; a SealedSecret ciphertext; or an approved external-secret reference. Never commit plaintext credentials, a private decryption key, provider credentials, or rendered plaintext Secret manifests. Avoid putting secret values into annotations, labels, commit messages, test output, Pod templates, generated diffs, or evidence files.

Git history is replicated by design. Private repository visibility reduces exposure but does not turn plaintext storage into a sound secret-management pattern. A repository access change is not a credential rotation.

## 5.4 Configuration vs secrets vs identity

| Example | Default classification | Reason / handling |
|---|---|---|
| `LOG_LEVEL=INFO` | Configuration | Usually non-sensitive; use ConfigMap/overlay. |
| `MODEL_TIMEOUT_SECONDS=4` | Configuration | Operational tuning; review as normal config. |
| `INFERENCE_ENDPOINT=https://inference.internal` | Depends | Non-secret in many contexts; classify based on topology sensitivity and whether credentials are embedded. |
| Database password | Secret | Can authenticate to data plane; rotate if exposed. |
| Private TLS key | Secret | Enables impersonation/decryption; protect separately from certificate metadata. |
| Kubernetes ServiceAccount name | Identity reference | Name is not a credential by itself; its permissions still matter. |
| ServiceAccount token / cloud access token | Credential | Treat as secret, scope and rotate/expire appropriately. |
| OIDC workload identity | Identity mechanism | Prefer short-lived identity-bound access where supported; M09 covers implementation. |

Use ConfigMaps for non-confidential settings. Use environment-specific Kustomize overlays or Helm values for replica counts, log level, resource requests, and non-sensitive endpoints. Secret *references* can vary by environment; secret values should not be copied from dev into staging or prod. If a “configuration” value grants access, reclassify it as a secret.

## 5.5 Three secret-management families

### Family 1 — Encrypted-in-Git

SOPS encrypts selected values in YAML/JSON/ENV/INI and supports age, PGP, and provider-backed key systems. The public age recipient can be shared; the private identity decrypts. Flux can natively decrypt SOPS-encrypted manifests during Kustomize reconciliation. Sealed Secrets instead seals a Kubernetes Secret for a controller/cluster key; only the matching controller can unseal it. Both preserve encrypted material in Git, so old ciphertext and key custody remain important.

### Family 2 — Reference-in-Git, value elsewhere

ESO and the Secrets Store CSI Driver use references to a provider or mounted secret. The Git repo holds a pointer and access configuration, while the value remains in an external store until retrieved/materialized. This reduces ciphertext/key management in Git but adds provider availability, identity, network, and permission dependencies. An `ExternalSecret` is not itself the secret value. ESO/CSI configuration and exact schemas depend on selected versions/provider integrations; verify them against official docs before production adoption.

### Family 3 — Runtime retrieval using workload identity

An application or agent obtains credentials at runtime using a workload identity, often with short-lived credentials. A Vault Agent/sidecar is an example at Awareness level. This can reduce long-lived static credentials in Kubernetes, but requires identity federation, provider policy, network availability, renewal/revocation behavior, and application support. Deep implementation is deferred to M09.

| Criterion | Encrypted-in-Git (chosen for lab) | Reference-in-Git / value elsewhere | Runtime retrieval / identity |
|---|---|---|---|
| Git stores | Ciphertext + public recipient/config | Store path/property/reference | Endpoint/policy/config, no value |
| Plaintext appears | At encryption source briefly; controller during reconciliation; Kubernetes Secret/workload | Provider and destination materialization; possibly Kubernetes Secret or CSI mount | Provider and consuming process/agent memory or file |
| Who can read/decrypt | Key holders and controller identity with key access | Provider-authorized identity and permitted destination consumers | Workload identity/provider policy and process access |
| Root of trust | age private key or KMS identity | Provider auth/identity and secret store | Identity issuer, federation, provider and application/agent |
| Backup/recovery | Private key and encrypted repo history | Provider backup/DR and access config | Provider, identity config, renewal and application dependencies |
| Rotation | Rotate value, re-encrypt; key rotation is separate | Rotate at source; verify refresh/sync | Rotate/expire lease and prove renewal/new credential use |
| Offline/rebuild | Ciphertext available; cannot decrypt without private key | External provider must be reachable and data recoverable | Identity/provider must be available |
| Audit | Git review plus controller/API access; key access may be limited | Provider audit logs plus Git reference changes | Provider identity/access logs; process-level audit depends on design |
| Local lab effort | Low–moderate with Flux SOPS | Depends on a valid fake provider and CRDs | Higher; identity/provider simulation is complex |
| Main trade-off | Key compromise exposes ciphertext history; key loss can make it unrecoverable | Provider becomes runtime dependency; permissions may be broad | Strong identity model possible, but operational integration is more complex |
| Best fit | Teams needing offline/reviewable encrypted desired state | Platform with an approved managed/self-hosted secret store | Mature platform with workload identity and applications able to retrieve/renew credentials |

No family is automatically secure. Each requires least privilege, protected bootstrap, rotation, audit, recovery, and a clear owner.

## 5.6 Kubernetes Secret, ConfigMap, RBAC, and etcd: precise security boundaries

Kubernetes Secret values are commonly represented as base64-encoded fields in YAML/API serialization. Base64 is encoding, not encryption. A person who can read the manifest can decode the value. Kubernetes documentation notes that Secret data is stored unencrypted by default unless encryption at rest is configured. Confirm the cluster's actual API-server encryption configuration; do not infer it from the object kind.

The controls are distinct:

- **Authentication:** who is making the API request?
- **Authorization/RBAC:** may that identity `get`, `list`, `watch`, `create`, `patch`, or `delete` Secrets in this scope? `list`/`watch` can expose many values, so least privilege matters.
- **Transport protection:** is traffic to the API server/provider protected in transit?
- **Encryption at rest:** are persisted API values encrypted in etcd and are encryption keys protected/backed up?
- **Workload exposure:** which containers mount or receive the value, which processes can inspect it, and whether logs/crash dumps expose it?
- **Backup exposure:** do etcd snapshots and cluster backups contain Secrets, and are those backups encrypted/access-controlled?

A Secret object is a distribution mechanism, not a complete secret-management system. Restrict access to the smallest required namespace and workload; avoid giving every container in a Pod a secret it does not need. Protect GitOps controller namespaces and repository credentials. Argo CD repository credentials are commonly stored as Kubernetes Secrets; rendered manifest/cache surfaces and exact component behavior are version-dependent, so review current Argo CD security guidance before choosing plugin-based decryption. Flux's native SOPS path is selected here partly to avoid adding a custom manifest-generation plugin, but the controller still needs access to the decryption key and API permissions.

## 5.7 Choose the local implementation and justify the decision

**Decision record — `[ASSUMPTION]` chosen path: Flux native SOPS + age.** This fits the zero-budget local lab, demonstrates encryption and GitOps reconciliation, avoids cloud KMS, and does not require an additional secret operator. Flux's current documentation describes native SOPS decryption for Kustomize resources. The precise CLI/controller versions must be recorded and verified before running the commands below.

Rejected for the main lab:

- **Sealed Secrets:** viable for encrypted-in-Git, but adds a separate controller and makes cluster sealing-key backup/recovery central to the exercise. Covered conceptually, not installed here.
- **ESO/CSI:** realistic for provider-backed secret references, but a reliable local fake provider and exact API schema add more components and version dependencies. M09 owns the deeper implementation.
- **Argo CD plugin-based SOPS:** possible, but plugin execution and plaintext rendered-manifest/cache handling expand the attack surface. This unit already has a Flux controller path from Unit 3; do not install Argo CD and Flux together in this cluster.

**Trust boundary:** the private age key is installed manually into `flux-system` as a Kubernetes Secret. The lab demonstrates the mechanism, not ideal production custody. A cluster admin able to read that Secret can recover the key. Production must separately design key distribution, environment separation, audit, backup, and rotation.

## 5.8 Lab environment and repository layout

### Prerequisites

On WSL2 Ubuntu or native Linux, install Docker, Git, `kind`, `kubectl`, Flux CLI, SOPS, age, Python 3, and PyYAML. Use the official installation instructions rather than copying unverified package commands; pin versions and record them:

```bash
# Record installed versions before lab work. These commands are observational.
git --version
docker version --format '{{.Client.Version}}'
kubectl version --client
kind version
flux --version
sops --version
age --version
python3 --version
python3 -m pip show PyYAML || true
```

If any command is missing, install only from the official project instructions linked in §5.25. `[VERIFY]` Package names, release assets, and install flags can change. Do not run `flux bootstrap` against a repository you care about.

### Local Git server and network model

Flux running inside a `kind` node cannot treat its own `localhost` as the host's localhost or as another container. For this lab, run a lightweight Gitea container on Docker's `kind` network so the controller can reach it by the container DNS name `gitea`. Create a dedicated cluster and server:

```bash
kind create cluster --name secret-lab
kubectl config current-context
# Expected context name includes kind-secret-lab; stop if it is not the lab context.
docker network inspect kind >/dev/null
docker run -d --name gitea --network kind \
  -p 3000:3000 -p 2222:22 \
  -e USER_UID=1000 -e USER_GID=1000 \
  gitea/gitea:1.22
```

`gitea/gitea:1.22` is an illustrative version pin, not a current-version recommendation; select and record a currently supported version before use. For a real lab, pin an image digest. Visit `http://localhost:3000` from the host and complete the initial setup. Create a **public, empty, disposable repository** named `secret-lab` under a lab-only account. Public is acceptable only because the repository contains fake data and encrypted values; use a local network and do not expose this port to untrusted networks. The controller will use `http://gitea:3000/<owner>/secret-lab.git` from inside the `kind` network. If Docker DNS/network behavior differs in your environment, verify reachability from a disposable debug container attached to `kind`; do not substitute `localhost` blindly.

For the examples below, replace `<OWNER>` with the local Gitea username. Never put a real token into the URL or shell history. Because this repository is public to the local lab network, the Flux `GitRepository` needs no credentials. If you choose a private repository, provision credentials out-of-band as a separate exercise and do not commit them.

### Target repository tree

```text
secret-lab/                                  # throwaway Git repository
├── .sops.yaml                               # public age recipient only
├── .gitignore
├── clusters/secret-lab/
│   ├── flux-source.yaml                     # Flux source for local Gitea
│   └── flux-kustomization.yaml               # enables SOPS decryption
└── apps/scoring-api/
    ├── kustomization.yaml
    ├── configmap.yaml                       # non-secret settings only
    ├── deployment.yaml                      # consumes mounted file
    └── secret.enc.yaml                      # SOPS ciphertext only

Outside repository:
├── age-lab.agekey                           # PRIVATE key; never commit
└── secret-plaintext.yaml                    # temporary fake plaintext; never commit
```

The actual file tree should not contain the private key or plaintext manifest. The public recipient in `.sops.yaml` is not a secret; it enables authorized writers to encrypt new values but does not decrypt existing values.

## 5.9 End-to-end implementation walkthrough

### Step 1 — Create an isolated workspace and age identity

```bash
mkdir -p "$HOME/gitops-secret-lab" "$HOME/.local/share/secret-lab"
chmod 700 "$HOME/.local/share/secret-lab"
cd "$HOME/gitops-secret-lab"

# Private key is outside the Git repository. Never enable shell tracing here.
umask 077
age-keygen -o "$HOME/.local/share/secret-lab/age-lab.agekey"
chmod 600 "$HOME/.local/share/secret-lab/age-lab.agekey"
age-keygen -y "$HOME/.local/share/secret-lab/age-lab.agekey" \
  > "$HOME/.local/share/secret-lab/age-recipient.txt"
AGE_RECIPIENT="$(cat "$HOME/.local/share/secret-lab/age-recipient.txt")"
printf 'Public recipient recorded (value intentionally not echoed).\n'
```

The public recipient is not sensitive. The private key is the root of trust. Back it up securely before a recovery exercise; do not treat a second unprotected file on the same disk as production-grade backup. `age-keygen` output and file formats should be checked against the installed age version.

### Step 2 — Create the repository and SOPS policy

```bash
mkdir -p secret-lab/{clusters/secret-lab,apps/scoring-api}
cd secret-lab
git init -b main
cat > .gitignore <<'EOF'
# Never commit local private keys, plaintext test secrets, or temporary credentials.
*.agekey
age-lab.agekey
secret-plaintext.yaml
*.plaintext.yaml
.env
EOF
cat > .sops.yaml <<EOF
creation_rules:
  - path_regex: apps/scoring-api/secret\\.enc\\.yaml$
    age: ${AGE_RECIPIENT}
EOF
```

Inspect `.sops.yaml` to confirm it contains only the public recipient. The `path_regex` is deliberately narrow; broad encryption rules can accidentally include files that need a different policy. SOPS syntax is version-sensitive—verify it against the official SOPS configuration documentation before using it beyond the lab.

### Step 3 — Create synthetic plaintext outside the repository

```bash
cat > "$HOME/.local/share/secret-lab/secret-plaintext.yaml" <<'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: scoring-api-credentials
  namespace: secret-lab
type: Opaque
stringData:
  api-key: LAB-ONLY-DO-NOT-USE
EOF
chmod 600 "$HOME/.local/share/secret-lab/secret-plaintext.yaml"
```

The value is a synthetic marker and grants no access. Encrypt only `data`/`stringData`, leaving the object identity fields readable to Kustomize/Flux:

```bash
sops --encrypt \
  --age "$AGE_RECIPIENT" \
  --encrypted-regex '^(data|stringData)$' \
  "$HOME/.local/share/secret-lab/secret-plaintext.yaml" \
  > apps/scoring-api/secret.enc.yaml
```

**Do not run `sops -d` to the terminal or check the plaintext file into Git.** Check only that ciphertext markers exist and the fake marker does not:

```bash
grep -q 'ENC\[' apps/scoring-api/secret.enc.yaml && echo 'ciphertext marker present'
if grep -R -n --exclude='*.md' 'LAB-ONLY-DO-NOT-USE' .; then
  echo 'Unexpected plaintext marker in repository; stop and clean the disposable repo.' >&2
  exit 1
else
  echo 'No plaintext marker found in repository tree.'
fi
```

This marker check is a lab sanity check, not a general secret scanner. SOPS file structure can vary by format/version; verify that sensitive values are encrypted and the `apiVersion`, `kind`, and `metadata` remain readable.

### Step 4 — Add non-secret configuration and workload

`apps/scoring-api/configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: scoring-api-config
data:
  LOG_LEVEL: "INFO"
  MODEL_TIMEOUT_SECONDS: "4"
```

`apps/scoring-api/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: scoring-api
  template:
    metadata:
      labels:
        app: scoring-api
    spec:
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        runAsUser: 65534
        runAsGroup: 65534
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: verifier
          # Teaching image only. In production, pin a verified digest and use an app image.
          image: busybox:1.36.1
          command: ["sh", "-c"]
          args:
            - >-
              test -s /var/run/scoring-api/api-key &&
              echo 'secret-file-present; value intentionally not printed' &&
              sleep 36000
          envFrom:
            - configMapRef:
                name: scoring-api-config
          volumeMounts:
            - name: credentials
              mountPath: /var/run/scoring-api
              readOnly: true
          resources:
            requests:
              cpu: 10m
              memory: 16Mi
            limits:
              cpu: 100m
              memory: 64Mi
      volumes:
        - name: credentials
          secret:
            secretName: scoring-api-credentials
            defaultMode: 0440
```

`apps/scoring-api/kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - configmap.yaml
  - deployment.yaml
  - secret.enc.yaml
```

This small workload proves file availability, not a real application authentication flow. The container image tag is used for lab convenience, not as a recommendation for production promotion. Production images should be verified and digest-pinned as taught in M01. The Secret file is mounted read-only, and the process only prints whether a file exists. Do not `cat` the file or add it to logs.

### Step 5 — Add Flux source and reconciliation entry point

`clusters/secret-lab/flux-source.yaml` (replace `<OWNER>` before applying):

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: secret-lab
  namespace: flux-system
spec:
  interval: 1m
  url: http://gitea:3000/<OWNER>/secret-lab.git
  ref:
    branch: main
```

`clusters/secret-lab/flux-kustomization.yaml`:

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: scoring-api
  namespace: flux-system
spec:
  interval: 1m
  path: ./apps/scoring-api
  prune: true
  sourceRef:
    kind: GitRepository
    name: secret-lab
  targetNamespace: secret-lab
  decryption:
    provider: sops
    secretRef:
      name: sops-age
```

The Flux API versions above match the current official Flux documentation consulted for this lesson, but must be checked against the installed CRDs. The Flux `Kustomization` is a custom resource, not the local `kustomization.yaml` file. `prune: true` means Flux may delete resources it previously managed when they are removed from the declared source. Use only the disposable lab repository and namespace.

Create the namespace manually before the app reconciliation:

```bash
kubectl config current-context
kubectl create namespace secret-lab
```

### Step 6 — Install Flux and provide the private key out-of-band

Install Flux CLI/controllers using the official current instructions, then record the versions. The command below is the controller installation step, not Git bootstrap:

```bash
kubectl config current-context
flux install
kubectl -n flux-system get deployments
```

Create the decryption-key Secret from the external private key file. The `.agekey` suffix is significant to Flux's documented age-key handling:

```bash
kubectl -n flux-system create secret generic sops-age \
  --from-file=identity.agekey="$HOME/.local/share/secret-lab/age-lab.agekey"
```

This command sends the key to the cluster API; protect access to `flux-system` and the cluster. Do not print the Secret or its decoded data. In production, decide how the initial key is delivered, who can read it, how access is audited, how it is rotated, and how it is restored. This is the **secret-zero** problem.

### Step 7 — Push the repo and enable reconciliation

Configure Git to point at the local Gitea repo. Replace `<OWNER>` with the local account and verify the URL before pushing:

```bash
git add .sops.yaml .gitignore apps
git status --short
git commit -m 'Add encrypted lab secret and scoring-api workload'
git remote add origin http://localhost:3000/<OWNER>/secret-lab.git
git push -u origin main
```

Flux inside the cluster must use `http://gitea:3000/...`, while the host Git client may use `http://localhost:3000/...`. These host/container addresses are intentionally different. If the push prompts for credentials, use the local Gitea lab account; never put credentials into the remote URL or commit them.

Apply the two Flux objects after replacing the owner placeholder in the source URL:

```bash
sed "s/<OWNER>/YOUR_LOCAL_GITEA_USERNAME/g" clusters/secret-lab/flux-source.yaml \
  | kubectl apply -f -
kubectl apply -f clusters/secret-lab/flux-kustomization.yaml
```

The first command replaces a placeholder only. Confirm the cluster context before applying. Then observe reconciliation without exposing secret values:

```bash
kubectl -n flux-system get gitrepositories,kustomizations
kubectl -n flux-system describe gitrepository secret-lab
kubectl -n flux-system describe kustomization scoring-api
kubectl -n secret-lab rollout status deployment/scoring-api --timeout=120s
kubectl -n secret-lab get pods
kubectl -n secret-lab exec deploy/scoring-api -- \
  sh -c 'test -s /var/run/scoring-api/api-key && echo mounted-file-present'
```

`kubectl exec` verifies that the file is present without printing its contents. Do not use `kubectl get secret -o yaml`, `kubectl describe secret`, `base64 -d`, or terminal decryption as routine validation. A successful rollout and file check are representative acceptance criteria, not evidence that this environment actually ran successfully.

### Step 8 — Commit only intended artifacts and verify repository safety

```bash
git status --short
git ls-files | sort
if git ls-files | grep -E '(^|/)(.*\.agekey|secret-plaintext\.yaml|.*plaintext\.yaml)$'; then
  echo 'Private key or plaintext file is tracked; stop.' >&2
  exit 1
fi
```

A Git ignore rule does not remove a file already tracked. If a private key or real secret is ever committed, treat it as exposed, rotate/revoke the credential or key as appropriate, and follow §5.15. Do not assume deleting the file or rewriting history solves the incident.

### Cleanup

Only after collecting sanitized evidence, delete the lab cluster and local Gitea container. Confirm context and names first:

```bash
kubectl config current-context
kind get clusters
docker ps --filter name='^gitea$'
# Only if the output confirms the dedicated lab resources:
kind delete cluster --name secret-lab
docker rm -f gitea
```

Retain the lab private key only if you need to restore this exercise; otherwise securely delete the throwaway key and any temporary plaintext file. For recovery drills, do not delete the only recovery copy. These cleanup commands are destructive to the named lab resources and must never be repurposed against a real environment.

## 5.10 Config refresh, immutable objects, and rollout-on-change

Updating an API object and making an application use its new value are different events.

- **Environment variable:** Kubernetes populates it when the container starts. Updating the referenced Secret or ConfigMap does not mutate an already running process environment. A rollout/restart or application-specific refresh is usually required.
- **Mounted Secret/ConfigMap volume:** Kubernetes updates projected content eventually, subject to propagation behavior and volume implementation. An application that reads the file only once may still keep the old value in memory. `subPath` mounts have different update behavior; check current Kubernetes documentation before relying on live refresh. Do not assume file update means process reload.
- **Immutable ConfigMaps/Secrets:** can prevent in-place mutation and encourage versioned objects, but require a clear lifecycle and cleanup strategy. This is an Awareness-level pattern; validate Kubernetes version and consumers.
- **Checksum annotation:** common chart patterns compute a checksum of rendered non-secret configuration and place it on the Pod template so a change triggers a rollout. Do not place secret values or an unsalted hash of low-entropy secret values into annotations; hashes can leak information. For secret changes, use a reviewed mechanism that changes the Pod template without exposing the value, or a reload controller whose security and ownership have been reviewed.
- **Reloader-style controller:** watches configuration objects and triggers workload restarts. This adds a privileged controller and must be scoped, tested, and monitored.
- **Kustomize `secretGenerator`:** generated names can change when content changes, causing referencing workloads to update when rendered correctly. M06's generator behavior and Flux SOPS integration details must be verified for installed versions. Do not assume a manually named Secret or a Helm chart follows the same mechanism.

Safe non-secret change example: change `LOG_LEVEL` from `INFO` to `DEBUG` in the dev ConfigMap, render/diff, and reconcile. For a production secret change, rotate at the authoritative source, update the encrypted representation/reference, ensure reconciliation completes, confirm the application reloads, and test authentication. Avoid rollout loops by ensuring a checksum is deterministic, excludes volatile fields, and changes only when intended configuration changes. Never copy plaintext secret values into diffs, annotations, labels, or GitOps UI output.

See M06 Units 5–6 for Kustomize overlays, Helm values, `secretGenerator`, and packaging. See [Unit 6 — Deployment drift detection and reconciliation](06-deployment-drift-detection-and-reconciliation.md) for deeper drift behavior.

## 5.11 Prevent plaintext commits: developer hooks, CI, and policy

Use defense in depth:

1. `.gitignore` prevents accidental addition of common local files; it is not a security boundary.
2. Pre-commit secret scanning catches mistakes early. A Gitleaks/TruffleHog-class scanner detects known patterns but can miss secrets or flag test fixtures.
3. CI scans commits and relevant history, fails closed on findings, and redacts output. Push protection may be available on some Git hosts, but exact behavior depends on provider, plan, repository rules, and version `[VERIFY]`.
4. A repository policy rejects Kubernetes `kind: Secret` with plaintext `data` or `stringData` except approved encrypted representations. A naive grep is not sufficient: YAML formatting, multi-document files, templating, generated manifests, base64 values, and custom resource kinds create false positives/negatives.
5. Restrict exceptions. Every exception has an owner, rationale, expiry, and test. An allow-list that silently grows becomes a bypass.

### Practical YAML policy check for the lab

This checker requires Python 3 and PyYAML (`python3 -m pip install PyYAML` in an isolated virtual environment). It reads YAML values but never prints a detected value. It rejects ordinary Kubernetes Secret values unless every value under `data`/`stringData` is visibly SOPS-encrypted. It is a starter guard, **not** a production policy engine: it does not render Helm/Kustomize, inspect all generated output, verify SOPS cryptographic authenticity, understand every custom secret CRD, or prove the repository has no secrets in arbitrary files.

`tools/check_plaintext_secrets.py` (inline teaching file; create it only in the disposable lab repo):

```python
#!/usr/bin/env python3
"""Lab policy: reject plaintext values in Kubernetes Secret manifests.

Requires PyYAML. Does not print values. Not a complete secret scanner or
production policy engine; inspect rendered output and run a dedicated scanner too.
"""
from pathlib import Path
import sys
import yaml

ALLOWED_SOPS_PREFIX = "ENC["


def encrypted_value(value):
    return isinstance(value, str) and value.startswith(ALLOWED_SOPS_PREFIX)


def main(root):
    failures = []
    for path in Path(root).rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".yaml", ".yml"}:
            continue
        if any(part in {".git", ".venv"} for part in path.parts):
            continue
        try:
            documents = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
        except (OSError, yaml.YAMLError):
            failures.append(f"{path}: cannot parse YAML; manual review required")
            continue
        for index, obj in enumerate(documents, start=1):
            if not isinstance(obj, dict) or obj.get("kind") != "Secret":
                continue
            data_fields = [obj.get(field) for field in ("data", "stringData") if field in obj]
            if not data_fields:
                continue
            values = [v for mapping in data_fields if isinstance(mapping, dict)
                      for v in mapping.values()]
            if not values or not all(encrypted_value(v) for v in values):
                failures.append(
                    f"{path} document {index}: plaintext/unapproved Secret data detected"
                )
    if failures:
        print("FAIL: review file locations; secret values are suppressed:")
        print("\n".join(f"- {item}" for item in failures))
        return 1
    print("PASS: no unapproved plaintext Kubernetes Secret data found by this limited check")
    return 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    raise SystemExit(main(target))
```

The checker deliberately treats ordinary base64 strings as unapproved. It recognizes only a simplified SOPS marker, not cryptographic correctness. A production implementation should use a proper YAML parser, explicit policy for approved kinds, rendered-output checks, SOPS verification, a secret scanner, and tests for templated/generated content.

**Positive/negative test (disposable repo only):**

```bash
mkdir -p policy-fixtures
cat > policy-fixtures/negative-secret.yaml <<'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: unsafe-fixture
stringData:
  token: LAB-ONLY-NEGATIVE-TEST
EOF
python3 tools/check_plaintext_secrets.py policy-fixtures
# Expected/representative: exit status 1; output identifies file, not the value.

cat > policy-fixtures/positive-encrypted.yaml <<'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: encrypted-fixture
stringData:
  token: 'ENC[AES256_GCM,data:REDACTED,iv:REDACTED,tag:REDACTED,type:str]'
EOF
python3 tools/check_plaintext_secrets.py policy-fixtures/positive-encrypted.yaml
# Expected/representative: exit status 0. This fixture proves only the marker rule,
# not that the ciphertext is authentic or decryptable.
```

Remove the negative fixture before pushing any lab repository. A scanner should redact findings by default. Never put real secrets in fixtures or paste scanner output containing secrets into tickets. Link this section to M02 Unit 5 (path-based CI) and M02's secret-safe CI variable/log practices. M01 covers image build-context/layer exposure: do not use Docker build arguments or copy `.env` files into image layers for credentials.

## 5.12 L3 production design checklist

### Root of trust and blast radius

For every secret path, write down who can decrypt or retrieve values and which resources that identity can reach. With SOPS + age, a person with the private key can decrypt any ciphertext addressed to that key; if one production key encrypts every environment, compromise spans all of them. Use distinct production and development recipients/keys or distinct external identities where the threat model requires isolation. Do not give a development controller a production decryption key. If multiple teams share a key, treat it as a shared high-impact platform asset.

Flux's kustomize-controller can decrypt resources when configured to do so and apply them using its Kubernetes identity. Scope controller permissions and its decryption Secret; restrict access to `flux-system`, Git repository credentials, and cluster-admin privileges. A controller is part of the production trust boundary, not a harmless background process.

| Design question | Required decision | Failure mode if omitted | Evidence to retain |
|---|---|---|---|
| Who owns the root of trust? | Named key/provider owner and backup custodian | Unrecoverable ciphertext or untracked privileged key | Key inventory and approved custody record; never include private key |
| Which controller can decrypt? | Per-environment identity and narrow scope | Dev controller can read prod credentials | RBAC review and negative authorization tests |
| How is the key bootstrapped? | Out-of-band process, no circular Git dependency | Controller cannot decrypt, or bootstrap key is committed | Bootstrap runbook and access approval |
| How are values rotated? | Owner, trigger, reload, test, expiry | Old credential remains in use | Rotation ticket with old-value revocation evidence and consumer test |
| How are keys rotated? | New recipient/key, re-encryption, overlap window, recovery test | Old ciphertext becomes unreadable or old key remains over-trusted | Key rotation plan and recovery exercise |
| How is access audited? | Git review plus cluster/provider/key access logs where available | Reads cannot be attributed | Access review and audit retention record |
| What happens during provider outage? | Defined fail-closed/fail-open behavior and fallback | Workload starts without valid credentials or outage cascades | Failure test and incident runbook |
| Which data can enter logs? | Redaction and output policy | CI/debug logs become secret stores | Scan result and regression test |

### Rotation: source value is not encryption key

**Credential rotation** replaces a password/token/key used by the application. **Encryption-key rotation** changes the key used to encrypt repository data. They have different consequences. If an age private key is exposed, rotating only the age key does not make an already leaked database password unusable. Rotate the underlying credential as well when its confidentiality may be affected.

### Environment and separation of duties

A developer may be allowed to propose encrypted ciphertext for production without being able to decrypt it. That works only if key custody and review are separate, CI does not expose plaintext, and the controller/key access path is controlled. Reviewers need enough metadata to judge the change but must not copy decrypted values into review comments. Use per-environment keys or identities, separate namespaces/cluster roles, and avoid a single broad secret-store identity that reads all tenants.

### Helm, Kustomize, CI, and process exposure

- Never put plaintext secrets into Helm `values.yaml`, Kustomize overlays, generator inputs that are committed in plaintext, rendered manifests, CI artifacts, or GitOps UI output.
- `secretGenerator` does not automatically encrypt its input. If the input file is plaintext, it is plaintext in Git/history unless another approved encryption step is used.
- Helm template output may render Secret values; protect `helm template`, `helm get manifest`, debug output, controller caches, and CI logs.
- Environment variables may be visible to the process itself and to sufficiently privileged debugging/inspection paths depending on OS/runtime; crash dumps and logs can leak them. File mounts can reduce accidental propagation but do not protect a value from a compromised process that can read the file.
- Keep secrets out of Docker build context, image layers, build args, test output, shell history, command echo, and build caches. Use supported secret-mount mechanisms or runtime injection, and inspect the build platform's current documentation.
- Prefer short-lived identity-bound credentials when a mature workload-identity path exists; short TTL reduces exposure duration but does not eliminate abuse during validity. Deep OIDC/federation and dynamic credentials are M09 topics.

### Argo CD and Flux-specific surfaces

Argo CD repository credentials are commonly stored as Kubernetes Secrets and must be protected. If a custom config-management plugin decrypts secrets, the plugin execution environment and rendered manifests become sensitive surfaces; review current official Argo CD security documentation and version-specific architecture before deploying such a plugin. This lesson avoids that path for its hands-on lab.

For Flux, review access to source-controller credentials, the kustomize-controller's SOPS key Secret, controller ServiceAccounts, and any secret material created in the cluster. Native SOPS decryption removes the need for a separate decryption plugin, but does not remove the controller's ability to see plaintext during reconciliation. `[VERIFY]` Confirm exact cache/log behavior for the pinned controller release before making claims about where plaintext is retained.

### ConfigMap vs Secret classification and exceptions

| Data type | Default location | Exception handling |
|---|---|---|
| Non-sensitive tuning, feature defaults, resource values | ConfigMap / overlay / Helm values | Review if the value reveals sensitive topology or business data |
| Password, API token, private key, credential-bearing URL | SOPS-encrypted manifest or approved external reference/runtime identity | No plaintext Git exception; emergency incident artifacts must be protected and short-lived |
| Certificate/public key or public endpoint | Often config, but classify contextually | Private key remains a secret; certificate may still reveal internal topology |
| Secret reference/provider path | Git, with policy and ownership | Restrict who can point workloads at privileged stores or other tenants' paths |
| Synthetic fixture | Dedicated test fixture, clearly labelled | Never reuse a production credential as a test fixture |

A policy exception must include owner, reason, scope, compensating control, expiry date, and reviewer. “The repository is private” is not sufficient justification for plaintext secrets.

## 5.13 L4 platform governance and operating model

A platform golden path can let application teams declare a narrow `ExternalSecret`-style reference while the platform team owns approved stores, identity integration, namespace policy, permitted secret backends, and baseline checks. This pattern is an architectural handoff—not an ESO implementation in this unit. M09 covers provider/identity depth; M16 covers platform self-service and golden paths.

| Activity | Application team | Platform team | Security | On-call/SRE |
|---|---|---|---|---|
| Classify application values and identify consumers | R | C | C | C |
| Own approved integration and controller baseline | C | R/A | C | C |
| Approve store permissions and exception policy | C | R | A | C |
| Rotate application credential | R/A | C | C | C |
| Rotate controller/decryption key | C | R/A | C | C |
| Respond to leak and coordinate revocation | R | C | A/C | R |
| Verify workload recovery and operational health | R | C | C | R/A |
| Review access and audit evidence | C | R | A | C |

R = Responsible; A = Accountable; C = Consulted. Actual allocation is organization-specific `[ASSUMPTION]`; name teams in a service catalog or runbook, not in a generic lesson.

A CI policy can reject plaintext Secret manifests and constrain allowed reference patterns before merge. Admission policy can restrict which secret-store kinds/names are permitted per namespace, who may create/modify store objects, and which ServiceAccounts may use them. Admission policy is Awareness-only here; use an approved policy engine and validate its schema/version in M12. Never rely on CI-only controls if users can mutate the live cluster directly.

Retain sanitized evidence for Git revision/reviewers; scanner/policy results; key access review; provider access events where available; credential/key rotation owner and timestamp; verification that the old credential fails; verification that the new credential works; controller reconciliation status; and access-control tests. Never include private keys or secret values in the evidence. A CI comment saying “passed” is not strong evidence unless linked to a durable, validated check result.

## 5.14 Secret rotation and key lifecycle runbooks

### A. Rotate an application credential with SOPS + age

1. The owner creates a new credential at the authoritative service, using an overlap window only if supported and approved.
2. Update the encrypted representation through the approved secure editing process. Do not paste the value into chat, ticket comments, or Git. In the lab, the external plaintext file is synthetic.
3. Re-encrypt with the approved public recipient and review the ciphertext-only diff. Confirm no plaintext was staged.
4. Merge through normal review/promotion gates; reconcile the correct environment.
5. Trigger workload reload/restart if required. Verify health and test the new credential without printing it.
6. Revoke the old credential; prove it no longer works. Record revision, owner, test IDs, timestamp, and outcome.
7. If failure occurs, roll forward or restore a known-good credential. Do not re-enable a credential known to be exposed merely to simplify rollback.

### B. Rotate an age encryption key

1. Generate a new private key and publish its **public recipient** through an approved change.
2. Update `.sops.yaml` and re-encrypt affected files for the new recipient. A short transition may include old and new recipients only as approved.
3. Provision the new private key out-of-band to the intended controller; never commit it.
4. Reconcile and verify decryption in a disposable/lower environment first, then production under change control.
5. Confirm required ciphertext can be decrypted with the new key and restore procedure works.
6. Remove old recipient access and old controller key after proving no ciphertext depends on it. If the old key was exposed, rotate underlying secret values too when confidentiality is at risk.
7. Preserve a protected recovery backup with named custodians and access reviews.

### C. ESO/reference pattern rotation (Awareness)

Rotate at the source provider; verify the configured `refreshInterval` and selected ESO version's refresh semantics; confirm the destination Secret changed without reading the value; check application reload/restart; verify old credentials fail; inspect provider audit logs; and test provider outage behavior. A reference can remain unchanged while its value rotates. Do not assume a sync interval means the application has reloaded.

### D. Rotation acceptance record (fake schema)

```yaml
recordType: secret-rotation-evidence
status: COMPLETED
service: scoring-api
environment: staging
secretReference: scoring-api-credentials/api-key
sourceRevision: "7b4d9a1" # [ILLUSTRATIVE] fake revision
rotationTicket: "SEC-EXAMPLE-042" # [ILLUSTRATIVE]
checks:
  oldCredentialRejected: "check-fake-101"
  newCredentialAccepted: "check-fake-102"
  workloadReloadVerified: "check-fake-103"
approver: "platform-reviewer-lab" # [ILLUSTRATIVE]
timestamp: "2026-10-28T12:00:00Z" # [ILLUSTRATIVE]
secretValueIncluded: false
```

This is a teaching schema, not a standard. Keep provider-specific identifiers and retention rules in the organization's approved evidence format.

## 5.15 Leaked-secret incident response in a GitOps system

1. **Contain access:** identify the value and systems it can access; restrict repository, CI, cache, artifact, provider, and account access as needed. Avoid posting the value into the incident channel.
2. **Rotate/revoke at source first:** disable or replace the exposed credential. Do not wait for Git history rewriting.
3. **Assess blast radius:** identify clones/forks, CI jobs/logs, caches, artifacts, backups, workstations, controller caches, Kubernetes Secret objects, and workloads that received the value.
4. **Update the approved representation:** encrypt the new value or update the external reference through review; reconcile and verify the workload uses it.
5. **Test old and new values:** old must fail and new must work. Plan overlap/rollout carefully, but do not leave a known-compromised credential active without explicit risk acceptance.
6. **Purge history/caches where feasible:** use reviewed history-rewrite tooling on an authorized repo, coordinate force-pushes, invalidate caches/artifacts where feasible, and notify fork owners. This reduces discoverability; it does not un-leak the credential.
7. **Audit and notify:** inspect provider usage, access logs, affected consumers, and stakeholders. Preserve a sanitized timeline and evidence.
8. **Prevent recurrence:** add scanner/policy tests, fix root cause, review access/key custody, rehearse rotation, and document a blameless post-incident review.

### Avoiding outage during transition

Use a provider-supported overlap period only when safe: create new credential, deploy it, verify all consumers, then revoke the old credential. If immediate revocation is necessary, prioritize containment and use the incident-approved recovery path. Do not silently re-enable an exposed credential for convenience. For shared database credentials, consider per-service identities to narrow blast radius; deep dynamic credential design belongs to M09.

### History purge is not revocation

Rewriting Git history cannot reliably erase every fork, clone, backup, cached artifact, screenshot, log, or human memory. The incident is not closed until the credential is invalidated, consumers are verified, access is audited, and prevention work is assigned. The question is not “Did the string disappear from `main`?” but “Can the exposed value still be used, and do we have evidence?”

## 5.16 Key loss, rebuild, and disaster recovery

### Recovery prerequisites

- Inventory encrypted files and which key/recipient can decrypt them.
- Protected backup of private age key or Sealed Secrets controller key, stored outside Git with restricted access and tested recovery.
- Versioned controller configuration, CRDs, source references, and documented out-of-band bootstrap steps.
- Access to Git repository and required artifact images.
- A fresh disposable cluster and a way to provision the recovery key without putting it in Git.
- Evidence that restored controller can decrypt the encrypted manifest and workload consumes the value without exposing it.

### Drill procedure

1. Create a protected backup of the **throwaway** key outside the repo and record its location without recording key contents. A same-disk copy is a lab convenience, not production-grade backup.
2. In a disposable copy, simulate losing the working key file while preserving the backup. Do not delete the only recovery copy.
3. Demonstrate that decryption cannot proceed without the private key using Flux status/conditions only. Do not print decrypted output.
4. Recreate a fresh cluster and reinstall Flux/CRDs. Confirm the current context is the fresh `kind` cluster.
5. Restore the key through the out-of-band path into the controller namespace, recreate source/reconciliation objects, and verify workload file presence.
6. Record elapsed time, prerequisites, failure points, key custodian, and sanitized checks. Delete only the disposable cluster after evidence capture.

If the only private key is permanently lost, encrypted data addressed only to that key may be unrecoverable. Git cannot reconstruct the private key from the public recipient or ciphertext. A backup is useful only if its integrity, custody, and restore procedure are tested.

## 5.17 Migration from plaintext/base64 secrets to a secure pattern

Use this sequence:

`inventory → assess exposure → rotate/revoke → choose target pattern → convert → verify consumer → purge exposed history/caches as feasible → enforce policy → document evidence`

1. Inventory repositories, branches, Git history, CI variables/logs, artifacts, Helm values, Kustomize generator inputs, Kubernetes manifests, and workload consumers. Do not copy detected values into the inventory report.
2. Classify each value and identify authoritative owner/provider. Assume any committed base64 Secret is exposed to everyone who could read the file/history.
3. Assess exposure and rotate/revoke credentials before history cleanup. Prioritize privileged and externally reachable credentials.
4. Select a pattern based on team maturity, provider availability, recovery requirements, and blast radius. The local SOPS choice is not a mandate for every production system.
5. Convert to SOPS ciphertext or approved references; provision keys/identities outside Git. Validate the consumer path in a lower environment.
6. Deploy and verify new credentials, reload/restart as needed, and revoke old values.
7. Purge history and invalidate artifacts/caches where feasible; coordinate force-pushes and inform fork/clone owners. Document residual copies and risk.
8. Enforce scanner and policy gates, review controller/provider permissions, and add regression tests.
9. Test backup/recovery and rotation; close migration only with sanitized evidence and named ownership.

- [ ] Inventory complete without recording values.
- [ ] Source owner and consumer list identified.
- [ ] Exposure assessed and credential rotated/revoked.
- [ ] Approved pattern and key/provider owner documented.
- [ ] No plaintext value or private key committed.
- [ ] Lower-environment consumer test passed.
- [ ] Workload rollout/reload verified.
- [ ] Old credential rejected.
- [ ] History/cache/artifact cleanup performed where feasible.
- [ ] Scanner/policy gates enabled and tested.
- [ ] Access review and recovery evidence saved.

## 5.18 Incident case studies: diagnose → fix → prevent

### Case 1 — Base64 Secret committed and mirrored to a public fork

**Symptom/timeline:** A repository scan finds a Kubernetes Secret with base64 `data.password`; a public fork contains the commit. A later commit removes the file, but the credential may still work.

- **Diagnosis/evidence:** identify credential owner and privilege; enumerate forks, CI logs, build artifacts, controller history, and provider access events. Do not paste the value into the report.
- **Immediate containment:** rotate/revoke at source; disable or narrow access if it cannot be rotated immediately; notify security/service owners.
- **Root cause:** base64 was mistaken for encryption and review/scanning did not prevent plaintext Secret objects.
- **Fix:** deliver new value through approved SOPS/reference pattern, reconcile, restart/reload consumers, and prove old value fails/new value works.
- **Prevention/evidence:** CI policy, secret scanning, fork/cache cleanup, sanitized timeline and test IDs. History rewrite is secondary.

### Case 2 — Sealed Secrets controller key lost during cluster rebuild

**Symptom:** Replacement cluster has the controller but cannot decrypt old sealed manifests.

- **Diagnosis:** verify controller/cluster identity and key availability without exposing private material.
- **Containment:** avoid deleting remaining cluster/backups; restore protected key backup if available.
- **Root cause:** sealing key was treated as disposable cluster state and restore was never tested.
- **Fix:** restore approved key and verify unsealing, or reseal from an authorized source if plaintext remains safely available. Without key or plaintext, ciphertext may be unrecoverable.
- **Prevention/evidence:** protected backup, custodian/ACL, periodic restore drill, key inventory, fresh-cluster recovery proof.

### Case 3 — ESO store credentials can access every secret

**Symptom:** A namespace's `SecretStore` identity can read all production paths.

- **Diagnosis:** inspect provider IAM/policy and audit logs; run a negative access test against another team's path without retrieving the value.
- **Containment:** disable/restrict the broad identity, assess reads, rotate provider credentials if necessary.
- **Root cause:** shared identity and wildcard permissions made namespace separation cosmetic.
- **Fix:** use per-team/namespace/service identities with least-privilege paths; update references and verify refresh and consumers.
- **Prevention/evidence:** policy review, denied-access tests, access review, provider audit evidence. Deep ESO/IAM work is M09.

### Case 4 — Age private key stored beside ciphertext

**Symptom:** A commit contains `secret.enc.yaml` and the matching `.agekey` file.

- **Diagnosis:** determine all ciphertext and credentials addressable by the key; do not republish the key in incident records.
- **Containment:** restrict repository access and rotate/revoke underlying secret values; key replacement alone does not invalidate leaked application credentials.
- **Root cause:** public recipient/ciphertext/private identity were not distinguished; `.gitignore` was trusted without checking tracked files.
- **Fix:** generate a new key, re-encrypt for its recipient, provision private key out-of-band, reconcile, verify, and purge history/caches where feasible.
- **Prevention/evidence:** private-key policy, scanner, `git ls-files` check, access review, rotation/recovery record.

### Case 5 — Rotated secret not picked up; pods used old value for weeks

**Symptom:** Provider or encrypted Git value changed, but authentication logs show continued use of the old credential.

- **Diagnosis:** compare source/provider version, Secret metadata, Pod rollout time, mount mode, environment injection, app reload logic, and reconciliation status. Do not print values.
- **Containment:** keep old credential valid only if risk permits; otherwise use emergency revocation and repair consumers promptly.
- **Root cause:** rotation procedure ended at updating the source object and never proved workload reload or old-value rejection.
- **Fix:** reconcile, trigger reload/restart, test new credential, revoke old credential, and confirm traffic succeeds.
- **Prevention/evidence:** end-to-end test covers source update → materialization → reload → new-auth success → old-auth failure; alert on stale age where measurable.

## 5.19 Troubleshooting decision tree

```text
Workload cannot authenticate
  ├─ Is the expected Git revision reconciled?
  │    ├─ No -> inspect GitRepository/Kustomization conditions and source reachability
  │    └─ Yes
  ├─ Can Flux decrypt the SOPS manifest?
  │    ├─ No -> check public recipient, key Secret name/namespace, key suffix, permissions
  │    └─ Yes
  ├─ Does the Kubernetes Secret exist in the target namespace?
  │    ├─ No -> inspect Kustomize path, namespace, apply/RBAC errors (never print values)
  │    └─ Yes
  ├─ Does the Pod reference the correct Secret/key and mount path?
  │    ├─ No -> inspect Pod spec and events
  │    └─ Yes
  ├─ Has the process reloaded after rotation?
  │    ├─ No -> trigger approved rollout/reload and verify
  │    └─ Yes
  └─ Does new credential work and old one fail? If not, check source owner/provider,
     credential scope, expiry, network policy, and audit logs; keep values redacted.
```

| Symptom | Likely causes | Safe checks | Avoid |
|---|---|---|---|
| Flux reports decryption failure | Wrong key, missing `sops-age`, key not in `flux-system`, wrong SOPS rule | Describe Kustomization; inspect name/namespace and file metadata | `kubectl get secret -o yaml`; dumping decrypted manifest |
| GitRepository not ready | Wrong URL, Gitea DNS/network, branch/repo mismatch, auth failure | Describe source; test host and container reachability separately | Assuming `localhost` in a Pod means host |
| Secret object missing | Wrong target namespace, path excludes file, reconciliation failed | Check object metadata and reconciliation conditions | Printing Secret YAML or decoded values |
| Pod starts but file absent | Secret key mismatch, wrong mount, Secret not materialized | Pod events/spec, existence check without reading content | `cat` or logging file contents |
| Rotation did not take effect | Stale process environment, app caches file, no rollout trigger | Compare metadata and Pod start time; safe auth test | Assuming API object update equals process reload |
| Policy blocks legitimate file | SOPS marker differs, YAML parse error, missing approved pattern | Review sanitized structure and checker version | Broad allow-list without owner/expiry |
| Key lost | No backup or wrong key inventory | Test protected backup in disposable cluster | Committing key or deleting last recovery copy |

## 5.20 Labs A–E and acceptance criteria

All labs use synthetic values labelled `LAB-ONLY`. Save only sanitized evidence: version logs, Git revisions, condition summaries, policy exit status, file-presence checks, and recovery timelines. Never save decoded values or private key contents. Lab A is the primary implementation; the other labs build on the disposable repo and can be performed separately.

### Lab A — End-to-end GitOps secret pattern

**Objective:** prove a SOPS-encrypted fake Secret can be stored in Git, decrypted by Flux, materialized in Kubernetes, and consumed without printing the value.  
**Prerequisites:** Docker, Git, `kind`, `kubectl`, Flux CLI, SOPS, age, local Gitea; 45–90 minutes; roughly 2 CPU/2–4 GB RAM while running.  
**Exact files/steps:** follow §§5.8–5.9. Files are `.sops.yaml`, `.gitignore`, `apps/scoring-api/{kustomization.yaml,configmap.yaml,deployment.yaml,secret.enc.yaml}`, and `clusters/secret-lab/{flux-source.yaml,flux-kustomization.yaml}`. Private key and plaintext stay outside Git.  
**Validation:**

```bash
kubectl config current-context
kubectl -n flux-system get gitrepositories,kustomizations
kubectl -n flux-system describe kustomization scoring-api
kubectl -n secret-lab rollout status deployment/scoring-api --timeout=120s
kubectl -n secret-lab exec deploy/scoring-api -- sh -c \
  'test -s /var/run/scoring-api/api-key && echo mounted-file-present'
git ls-files | grep -E 'agekey|secret-plaintext|plaintext\.yaml' && exit 1 || true
```

**Expected/representative:** reconciliation Ready, Deployment available, exec prints only `mounted-file-present`, and no key/plaintext path is tracked. These are expectations, not observed results.  
**Failure modes:** wrong Gitea URL, no network reachability, key Secret in wrong namespace, key filename lacks `.agekey`, wrong recipient, Flux CRD mismatch, namespace missing, or image pull failure.  
**Cleanup:** explicit lab cleanup in §5.9 after evidence capture.  
**Evidence:** tool versions, commit ID, sanitized Flux conditions, rollout status, policy output, trust-boundary diagram.  
**Pass gate:** all validations succeed without printing or committing a value. Fail if plaintext/key is tracked or controller cannot decrypt.

### Lab B — Secret leak simulation and incident timeline

**Objective:** detect a synthetic leak, rotate/revoke the fake value, update the approved representation, and demonstrate that history cleanup is secondary.  
**Prerequisites:** disposable local Git repo; policy checker from §5.11; 30–60 minutes; no cluster required if a fake consumer is used.  
**Steps:**

```bash
mkdir -p "$HOME/secret-leak-lab" && cd "$HOME/secret-leak-lab"
git init -b main
cat > leaked.yaml <<'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: fake-leak
stringData:
  token: LAB-ONLY-OLD-VALUE-DO-NOT-USE
EOF
git add leaked.yaml && git commit -m 'Deliberately unsafe negative test; LAB ONLY'
python3 /absolute/path/to/check_plaintext_secrets.py . || echo 'Expected policy failure observed'
```

Replace `/absolute/path/to/check_plaintext_secrets.py` with the actual local script path. Run only against this throwaway repo. Simulate a source that now accepts only `LAB-ONLY-NEW-VALUE-DO-NOT-USE`; keep test output to booleans/status and never echo values. Update the repository to an encrypted/reference representation using Lab A. Verify the fake consumer rejects the old marker and accepts the new marker without printing either value. If practicing history rewrite, use only this local repo with no real remote; verify the tested clone no longer contains the fixture. Remote forks/caches would require separate coordination.

**Incident timeline:** `T0 detection → T1 access containment → T2 source rotation/revocation → T3 GitOps update → T4 workload reload → T5 old-value rejection/new-value acceptance → T6 history/cache cleanup → T7 audit/prevention`.  
**Expected:** policy exits non-zero on negative fixture; sanitized record shows old rejected/new accepted; rewritten local history no longer contains the tested fixture.  
**Cleanup:** delete only `$HOME/secret-leak-lab`; no remote should be configured.  
**Evidence:** fake timeline, policy result, before/after commit IDs, consumer test result.  
**Pass gate:** source rotation is the fix; history rewrite is exposure reduction only.

### Lab C — Key-loss and rebuild / disaster recovery drill

**Objective:** demonstrate failure without the private key and recovery from a protected backup.  
**Prerequisites:** Lab A working; 45–90 minutes; one disposable `kind` cluster; protected lab backup.  
**Steps:**

1. Copy the synthetic key to a protected backup outside the repo and record its location, not contents. Same-disk backup is lab-only, not production DR.
2. In a disposable cluster/copy, move the working key file to quarantine while preserving the backup. Do not delete the backup.
3. Confirm decryption cannot proceed using Flux status/conditions only; do not print decrypted output.
4. Recreate a fresh cluster with `kind create cluster --name secret-dr`; verify current context. Install Flux, recreate namespace, and restore source/reconciliation manifests as in Lab A.
5. Restore the key from backup into the new cluster using the out-of-band Secret creation command from §5.9. Reconcile and verify file presence.
6. Record recovery time, prerequisites, failure points, custodian, and sanitized checks.

**Expected:** without the key Flux cannot decrypt; with the correct restored key reconciliation succeeds. If the only key is lost, ciphertext may be unrecoverable.  
**Cleanup:** delete only clusters named `secret-lab` or `secret-dr` after checking names. Keep or securely delete the throwaway backup based on whether you will repeat the exercise.  
**Evidence:** recovery duration, custody steps, failure/recovery conditions, file check, dependency list.  
**Pass gate:** restore succeeds without committing/printing the private key; no real cluster is touched.

### Lab D — CI policy check for plaintext Secret

**Objective:** demonstrate failing plaintext and passing encrypted-marker fixtures without leaking values.  
**Prerequisites:** Python 3/PyYAML; 20–40 minutes; no cluster.  
**Steps:** create `tools/check_plaintext_secrets.py` from §5.11 and run the positive/negative fixture commands there. Add the checker to a local pre-merge script or CI stage. Ensure logs do not echo YAML bodies.  
**Expected:** plaintext `Secret` exits 1 and prints only a file/document reference; SOPS-marker fixture exits 0. This validates a marker convention, not cryptographic authenticity.  
**Failure modes:** PyYAML missing, malformed/multi-document YAML, templated files, unsupported marker, custom CRDs. Parse errors should fail closed for in-scope YAML and trigger review.  
**Cleanup:** remove the unsafe negative fixture; keep only synthetic tests.  
**Evidence:** script version/hash, fixture names, exit statuses, limitation note.  
**Pass gate:** no value in output and both test cases behave as expected.

### Lab E — Secret-family comparison memo

**Objective:** select a defensible pattern for a named fictional organization.  
**Profile:** `[ILLUSTRATIVE]` a small data/ML team with one local Kubernetes cluster, no cloud account in development, moderate audit needs, and two operators who can maintain recovery keys.  
**Steps:** create a one-page memo comparing SOPS+age, Sealed Secrets, ESO/CSI, and runtime identity on root of trust, value visibility, rotation, key recovery, provider/controller outage, dev/prod isolation, audit, operational burden, and migration. Defend SOPS+age as a local learning choice, not a universal answer. A mature multi-team platform may reasonably prefer a provider reference/runtime identity pattern.  
**Expected:** recommendation names trust root, custodian, rotation owner, recovery dependency, assumptions, and residual risks.  
**Cleanup:** none; memo contains no credentials.  
**Evidence:** decision memo and review checklist.  
**Pass gate:** no claim that one family is universally best; credential rotation is distinct from encryption-key rotation.

## 5.21 Common mistakes and anti-patterns

- **Committing base64:** base64 is not encryption; treat the credential as exposed and rotate it.
- **Committing the private key beside ciphertext:** a reader can decrypt data addressed to that key.
- **Assuming `.gitignore` is enforcement:** ignored files can be tracked, copied, or force-added.
- **Putting plaintext in Helm values/Kustomize generator inputs:** creating a Secret at render time does not protect source history.
- **Using one production key for every environment:** a dev compromise can expose production ciphertext.
- **Treating controller readiness as consumer correctness:** app may use an old value or lack permission to read the mount.
- **Printing secrets for debugging:** inspect metadata, condition, existence, or auth result instead.
- **Putting values or hashes in annotations:** low-entropy values may be guessed, and rendered metadata is widely visible.
- **Giving a shared external identity wildcard read access:** namespace references alone do not provide provider-side isolation.
- **Assuming rotation interval means reload:** verify source → materialization → process reload → old credential rejection.
- **Rewriting Git history before rotating:** copies may persist and the credential remains usable.
- **Backing up a key without testing restore:** an unreadable backup is not a recovery plan.
- **Installing Argo CD and Flux together in the lab:** overlapping controllers complicate resource ownership; this unit uses Flux only.

## 5.22 Self-check questions

1. **Why is a base64 Kubernetes Secret unsafe to commit?** — Anyone with the manifest can decode it. “Private Git makes it safe” is wrong because access controls do not prevent copies/history exposure.
2. **What are the three families?** — Encrypted-in-Git; reference-in-Git/value-elsewhere; runtime retrieval using identity. Each has a distinct trust root and operational dependency.
3. **What is the root of trust in this lab?** — Age private key custody plus Kubernetes/API permissions protecting its Secret. The public recipient cannot decrypt.
4. **Why not commit the private key beside ciphertext?** — It gives readers the means to decrypt the protected values.
5. **What comes first after a credential leak: history purge or rotation?** — Rotate/revoke at source. Purge is only exposure reduction.
6. **What does Flux SOPS decryption prove?** — Controller can decrypt/apply current declared state; not that app auth works or permissions are appropriately scoped.
7. **Does updating a Secret update an environment variable in a running process?** — No; usually a rollout/restart or app reload is needed.
8. **Can a mounted file update while the app uses the old credential?** — Yes; app may cache it. Test reload behavior.
9. **Credential rotation vs age-key rotation?** — One replaces the credential accepted by the provider; the other changes encryption authority. Key exposure may require both.
10. **Why back up the private key?** — Without it ciphertext may be unrecoverable; backup must be protected and restore-tested.
11. **What is secret zero?** — The first credential/key needed to bootstrap access to other secrets; provision outside Git.
12. **Does an ExternalSecret contain the value?** — No; it describes how/where to fetch it.
13. **Why is a regex checker insufficient?** — YAML can be generated, templated, multi-document, or custom; parsing, rendered checks, scanning, and explicit tests are needed.
14. **Why is a broad ESO identity dangerous?** — A compromised app/reference can read unrelated secrets; use least privilege and negative tests.
15. **What closes a rotation?** — Revision/source version, reconciliation, workload reload, new accepted/old rejected checks, owner/time, sanitized evidence—not a comment saying “rotated.”

## 5.23 Interview and design-review questions

### 1. Design root of trust for multi-environment GitOps.

**Model answer:** Enumerate decryption/provider identities and who can access them; separate dev and prod authority; restrict controller and namespace RBAC; provision keys outside Git; define custodians, backups, rotation, audit, and recovery tests. A shared key is an explicit blast-radius decision.

### 2. What if the only age private key is lost?

**Model answer:** Ciphertext remains but may be unrecoverable; the public recipient cannot reconstruct the key. Restore from protected backup. If none exists, acknowledge data loss and rotate reissuable source credentials; prevent recurrence with tested recovery.

### 3. Explain secret-zero bootstrap.

**Model answer:** The initial key/provider identity arrives through a separate trust channel such as controlled operator action or workload identity. It cannot be stored in the repo it unlocks. Define provisioning, read access, rotation, and recovery.

### 4. How do you prove rotation reached the application?

**Model answer:** Track source rotation, encrypted/reference change, Git revision, controller readiness, Kubernetes object metadata, Pod reload/restart, and safe auth tests. Prove old credential rejected and new accepted without printing either.

### 5. A developer can submit production ciphertext but cannot decrypt it. What controls make that real?

**Model answer:** Restrict production key/provider permissions to production controller identities and custodians; prevent CI/review from exposing plaintext; separate environment keys; enforce server-side branch rules and policy; audit access. Review and runtime checks still matter because encrypted changes can be malicious or misdirected.

### 6. A secret appears in Git history and a public fork. Walk through response.

**Model answer:** Contain access and assess scope; rotate/revoke at source first; update approved GitOps representation; reconcile and verify new use/old rejection; inspect provider logs; purge history/caches/artifacts where feasible and coordinate fork owners; document timeline and prevention. History rewriting does not un-leak it.

### 7. Why choose external references/runtime identity instead of SOPS?

**Model answer:** A mature platform may centralize audit, rotation, dynamic credentials, and policy in a provider or identity system. Trade-offs include provider availability, identity integration, and complexity. Choose from threat model and organizational capability.

### 8. Risks of controller/plugin-based decryption?

**Model answer:** Controller/plugin sees plaintext and can potentially access/apply resources within its permissions; plugin execution and rendered-manifest/cache surfaces are sensitive. Restrict identities, repository permissions, namespaces, logs, and blast radius; verify behavior for pinned versions.

## 5.24 Evidence artifacts and completion gate

Save sanitized evidence in your learning area, not in the GitOps repo if it reveals sensitive infrastructure details:

- [ ] Tool/version inventory and exact cluster context name.
- [ ] Repository tree showing ciphertext/public recipient and no tracked private key/plaintext.
- [ ] Git commit ID and `git ls-files` safety check.
- [ ] Sanitized Flux GitRepository/Kustomization conditions.
- [ ] Deployment rollout result and file-presence check (no value).
- [ ] Policy checker source/version and positive/negative exit results.
- [ ] Fake leak incident timeline with rotation-first sequence.
- [ ] Key-loss/rebuild drill result, dependencies, recovery time, and custody note (no key contents).
- [ ] Secret-family decision memo naming assumptions and residual risks.
- [ ] Rotation record with old-value rejection/new-value acceptance checks.
- [ ] Threat model and ownership/RACI table adapted to a fictional or approved training service.

**Completion gate:** Explain where plaintext exists at each stage, who can decrypt/read it, how the first key enters the system, how a leaked value is revoked, how the key is recovered, and how the application is proven to use the rotated credential. Demonstrate that the lab repo contains only ciphertext/reference and non-secret config. If you cannot identify the root-of-trust custodian or recover a lost key, the design is not production-ready.

## 5.25 Sources, version verification, assumptions, and limitations

### Official references consulted

- Kubernetes, **Secrets**: https://kubernetes.io/docs/concepts/configuration/secret/ — Secret object model and usage.
- Kubernetes, **Good practices for Kubernetes Secrets**: https://kubernetes.io/docs/concepts/security/secrets-good-practices/ — base64 encoding, access control, and safe use.
- Kubernetes, **Encrypting Confidential Data at Rest**: https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/ — encryption-at-rest configuration and key considerations.
- Flux, **Manage Kubernetes secrets with SOPS**: https://fluxcd.io/flux/guides/mozilla-sops/ — Flux integration workflow.
- Flux, **Kustomization / decryption**: https://fluxcd.io/flux/components/kustomize/kustomizations/ — SOPS decryption and `spec.decryption` fields.
- Flux, **Secrets management**: https://fluxcd.io/flux/security/secrets-management/ — security context and secret patterns.
- SOPS, **Documentation**: https://getsops.io/docs/ — supported formats and encryption backends.
- age, **Project documentation**: https://github.com/FiloSottile/age — key generation and encryption usage.
- Gitleaks, **Project documentation**: https://github.com/gitleaks/gitleaks — secret-scanning tool and redaction options.
- Helm, **Documentation**: https://helm.sh/docs/ — templating and values handling.
- Kustomize, **Documentation**: https://kubectl.docs.kubernetes.io/references/kustomize/ — bases, overlays, and generator references.
- External Secrets Operator, **Documentation**: https://external-secrets.io/latest/ — provider references and refresh semantics; pin to selected release.
- Secrets Store CSI Driver, **Documentation**: https://secrets-store-csi-driver.sigs.k8s.io/ — secret mounts and provider integration.
- Argo CD, **Security**: https://argo-cd.readthedocs.io/en/stable/operator-manual/security/ — review before using plugin-based decryption or handling repository credentials.
- Flux, **Security**: https://fluxcd.io/flux/security/ — controller and multi-tenancy security guidance.

The current Flux and Kubernetes pages above were inspected during preparation. The complete local lab was **not executed**, and no installed version was available to validate commands end-to-end. Links are official documentation entry points; exact section names and API details may evolve.

### Source/roadmap scope notes

- The roadmap source available in the workspace was `Roadmap(9).md`, not a file literally named `Roadmap_ptree.md`. It confirms the Stage 2E M08 Unit 5 filename, neighboring M08 lessons, and M09 Secrets and Identity Management.
- The authoritative syllabus file available was `/mnt/data/PROMPT-GitOps-and-Progressive-Delivery.md`; it defines Unit 5's L1/L3/L4 scope and the M09/M16 handoffs. The attached prompt supplied detailed L2 and Labs A–E requirements.
- The target directory did not contain Unit 6 at authoring time; its filename was confirmed from the roadmap tree, but its lesson content was not read. Relative links reference the confirmed filename without claiming details from that lesson.
- The selected hands-on path is Flux native SOPS + age. Sealed Secrets and ESO/CSI/runtime identity are Awareness-level comparisons only.

### `[VERIFY]` register

| Item to verify before execution/production | Why it matters | Official source | Status |
|---|---|---|---|
| Exact Flux CLI/controller versions and CRD compatibility | `GitRepository`, `Kustomization`, and SOPS fields must match installed CRDs | https://fluxcd.io/flux/installation/ and Flux Kustomization docs | Not live-tested; verify locally |
| Exact SOPS CLI/config behavior and encryption format | Wrong rules can leave values plaintext or prevent decryption | https://getsops.io/docs/ | Docs consulted; command not executed |
| age CLI/key file format | Key generation, recipient extraction, suffix recognition | https://github.com/FiloSottile/age | Verify installed version |
| Gitea version, setup, Docker DNS/network | `gitea` must resolve from Flux pods; server must remain isolated | https://docs.gitea.com/ | Environment-dependent |
| Flux SOPS private-key Secret format | Key suffix and namespace affect decryption | https://fluxcd.io/flux/components/kustomize/kustomizations/ | Docs consulted; not tested |
| BusyBox image and Pod security compatibility | Lab workload must pull image and run as non-root | https://hub.docker.com/_/busybox and Kubernetes docs | Verify image availability |
| Gitleaks flags/version and redaction | Scanner output must not leak findings | https://github.com/gitleaks/gitleaks | Docs consulted; scanner not run |
| ESO refresh interval/store schema/provider support | Behavior differs by release/provider | https://external-secrets.io/latest/ | Awareness only; not used in primary lab |
| Argo CD plugin/cache exposure details | Rendered manifests may be sensitive | https://argo-cd.readthedocs.io/en/stable/operator-manual/security/ | Version-specific review; not used in lab |
| Encryption at rest in etcd | Secret creation does not prove at-rest encryption | https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/ | Cluster-specific config not inspected |

### Ten-pass self-audit summary

- **Pass 1 — Source/scope:** target filename, M08 Unit 5, M09 handoff, and adjacent lesson names checked against available roadmap/syllabus.
- **Pass 2 — Coverage:** L1–L4 foundations, design criteria, governance, five incident cases, and Labs A–E are represented; the chosen pattern is implemented in the lesson with environment-dependent steps marked.
- **Pass 3 — Secret safety:** values are synthetic; private key/plaintext stay outside Git; verification avoids decoded values; leak response rotates first.
- **Pass 4 — Technical correctness:** Flux API names and SOPS decryption approach checked against official docs; no live cluster, YAML parser, Flux controller, or SOPS command was run, so manifests are static-reviewed rather than execution-verified.
- **Pass 5 — Security design:** root of trust, secret zero, least privilege, environment separation, backup/recovery, and source/key rotation distinction are covered.
- **Pass 6 — Lab reproducibility:** local-first steps and Gitea networking are included; image pulls and exact compatibility remain environment-dependent.
- **Pass 7 — Operations:** incident response, migration, rotation, DR, reload behavior, and all five required incidents are covered.
- **Pass 8 — Cross-links:** exact M08 sibling filenames and M01/M02/M03/M06/M09/M12/M13/M16 handoffs are referenced where supported by the roadmap.
- **Pass 9 — Sources/claims:** official documentation links included; untested/version-sensitive behavior appears in the `[VERIFY]` register.
- **Pass 10 — File/change audit:** target lesson file created at the exact requested path in the available working directory. No other file was intentionally modified by this lesson-generation step.

**Content status: DRAFT-AUDITED | Audit date: 2026-10-28 | Auditor: AI self-audit (human verification required) | Unverified items: 10**

An AI self-audit does not replace a human running every command against the chosen versions and environment. Expected output is representative unless captured from an actual run. This lesson is not execution-verified and does not claim production compliance.
