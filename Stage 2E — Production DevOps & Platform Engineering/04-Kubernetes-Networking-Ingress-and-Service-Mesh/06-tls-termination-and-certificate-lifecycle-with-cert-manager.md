# TLS termination and certificate lifecycle with cert-manager

## Unit 6 — TLS termination and certificate lifecycle with cert-manager

**Target file:** `06-tls-termination-and-certificate-lifecycle-with-cert-manager.md` | **Estimated time:** 8–12 hours across reading and labs | **Prerequisites:** M01–M03; M04 Units 1–5; working Linux shell, OpenSSL, `kubectl`, Docker, and `kind`  
**Core tools:** OpenSSL, `curl`, Kubernetes Secrets, Ingress, cert-manager, `kind` | **Awareness:** ACME, private PKI, Gateway API TLS listeners, trust-manager, external issuers, OCSP/revocation | **Last reviewed:** 2026-10-28 (authoring date; not a live-doc verification date) | **Kubernetes/tool baseline assumed:** Kubernetes API concepts common to recent releases; exact Kubernetes, cert-manager, Gateway API, and controller versions are intentionally not pinned and must be verified before execution.

> **Status: DRAFT-AUDITED.** This lesson was drafted from the available roadmap, M04 syllabus, the uploaded Unit 6 prompt, and the neighboring M04 lessons. It is a reasoned technical review, not a live-cluster test. Current installation URLs, versions, CRD schemas, controller behavior, and metrics are marked for verification wherever not independently checked. Do not treat illustrative output as measured evidence.

### 6.0 Why this matters in production

An expired leaf certificate can turn a healthy model-scoring API into a client-visible outage even when its Pods, Service, and database remain healthy. The same symptom—“HTTPS is broken”—can also come from a wrong Subject Alternative Name (SAN), an incomplete chain, a trust-store change, a stale certificate still served by a proxy, or a controller that failed to reload an updated Secret. These incidents recur when certificates are treated as static files rather than owned, monitored lifecycle objects. This unit teaches you to trace the actual TLS path, issue a lab certificate through cert-manager, verify the certificate served to a client, and recover from renewal and issuer failures without confusing certificate issuance with client trust.

### 6.1 Learning objectives

By the end, a learner should be able to:

1. **[L1]** Explain the TLS handshake, certificate chain, SAN/hostname validation, SNI, trust anchors, and where plaintext can exist.
2. **[L1]** Inspect a certificate presented by a local endpoint with `openssl s_client`, decode metadata with `openssl x509`, and test trust with `curl --cacert`.
3. **[L2]** Generate a lab-only local CA and leaf certificate, verify key/certificate correspondence, and create a `kubernetes.io/tls` Secret without printing private keys.
4. **[L2]** Explain `Issuer`, `ClusterIssuer`, `Certificate`, `CertificateRequest`, and ACME `Order`/`Challenge` scope and roles.
5. **[L2]** Create a cert-manager `Certificate` using a local CA issuer and connect its Secret to an Ingress TLS host.
6. **[L2/L3]** Compare the Secret, certificate resource status, and certificate actually served by the local endpoint before and after a renewal event.
7. **[L3]** Design certificate expiry alerts, least-privilege Secret access, issuer boundaries, and a private-PKI rotation plan.
8. **[L4]** Diagnose an expired certificate, failed renewal, deleted issuer, stale proxy certificate, or exposed private key using evidence and reversible mitigations.

### 6.2 Concept map and vocabulary

### The request path comes before configuration

[ASSUMPTION] The shared M04 example uses namespace `ml-demo`, an Ingress controller selected in Unit 3, a Service named `model-api`, and a FastAPI scoring workload. The hostname below is a local-only name; it is not a public domain. The example does not require the feature service, Postgres, Redis, ETL worker, or metrics endpoint to be externally exposed.

```text
Developer's client
  curl --cacert lab-root.crt https://model-api.local/
        |
        | TLS encrypted on client -> local entry point
        v
Host / WSL2 localhost port mapping -> kind node/controller
        |
        | TLS terminates here in the chosen Ingress implementation
        | HTTP may exist on the controller -> Service -> Pod segment
        v
Ingress controller -> Service model-api.ml-demo.svc -> FastAPI Pod
        |
        +--> internal feature-service / Postgres / Redis remain internal
        +--> metrics endpoint is not automatically public
```

If TLS terminates at the Ingress controller, the client-to-controller segment is encrypted, but the controller-to-Pod segment may be plaintext unless separately protected. TLS at the edge is not end-to-end encryption. If the application terminates TLS itself, encryption can extend to the Pod, but certificate distribution, readiness, probes, and reload behavior become application concerns. A service mesh proxy may add a separate workload-to-workload mTLS layer; Unit 8 covers mesh mTLS configuration. A local `kind` port mapping is not a cloud load balancer and does not prove production network behavior.

### Certificate chain and trust

```text
Client trust store
  contains / trusts the lab root CA certificate
                  |
                  v
             Root CA (trust anchor)
                  |
                  | signs
                  v
        [Intermediate CA — optional]
                  |
                  | signs
                  v
       Leaf certificate for model-api.local
       SAN = DNS:model-api.local; public key = server key
```

The server normally presents the leaf and any required intermediate certificates; clients build a path to a trust anchor they already trust. A root certificate is not trusted merely because a server sends it. A missing intermediate can break path building even when the leaf is otherwise valid. For this lab, the root is self-created and trusted explicitly with `--cacert`; it must never be installed globally as a trusted root without deliberate review.

### TLS handshake trace

```text
Client                                      TLS endpoint
  |---- ClientHello: versions, ciphers, SNI ---->|
  |<--- ServerHello and selected parameters -----|
  |<--- Certificate chain -----------------------|
  |     Client checks validity, chain, SAN,      |
  |     key usage and trust anchor locally       |
  |<--- key-exchange / handshake messages ------>|
  |---- Finished / Finished -------------------->|
  |==== encrypted application data ==============|
```

This is a simplified trace; exact messages differ between TLS 1.2 and TLS 1.3. The certificate is presented by the server, but the client performs server-certificate validation. SNI (Server Name Indication) lets a client indicate the requested hostname during the handshake so a shared endpoint can choose a certificate. SAN (Subject Alternative Name) carries the identities the certificate is valid for; modern hostname validation should be based on SAN, not on an assumption that a Common Name is sufficient.

### Glossary

| Term | Precise definition | Common misconception |
|---|---|---|
| TLS | Protocol providing confidentiality and integrity for traffic and, with correct certificate validation, server authentication. | TLS alone authorizes a caller or proves the caller is safe. |
| CA | Certificate Authority that signs certificates under a defined trust policy. | Any CA certificate is trusted by every client. |
| Root / intermediate / leaf | Trust anchor / subordinate issuing CA / endpoint identity certificate. | The server should always send the root certificate. |
| SAN | Certificate extension listing DNS names or IP identities. | A valid signature makes any hostname acceptable. |
| SNI | ClientHello extension indicating the intended server name. | SNI replaces hostname verification. |
| Issuer | cert-manager resource defining how certificates are issued; namespaced. | It is the same as a certificate. |
| ClusterIssuer | Cluster-scoped cert-manager issuer usable across namespaces subject to policy/RBAC. | Cluster scope means safe for every tenant. |
| Certificate | cert-manager desired-state resource describing a certificate and its target Secret. | `Ready=True` proves every proxy serves the new certificate. |
| CertificateRequest | Request object created for issuance/signing; commonly generated by cert-manager from a Certificate. | It is the same as the Secret consumed by a proxy. |
| ACME Order / Challenge | ACME workflow resources for ordering a certificate and proving control of identifiers. | They are used for every CA issuer. |
| TLS Secret | Kubernetes Secret with type `kubernetes.io/tls` and `tls.crt`/`tls.key` keys. | Base64 encoding encrypts private keys. |
| Termination | Point where a TLS connection is decrypted. | The entire path remains encrypted after termination. |
| Renewal | Lifecycle operation that obtains/replaces certificate material before expiry. | Renewal automatically proves the serving proxy reloaded it. |
| Rotation | Replacement of keys/certificates or trust anchors under a controlled transition. | Rotation is just deleting an old Secret. |
| EKU | Extended Key Usage constraining intended certificate purpose, such as server or client authentication. | A server-auth certificate is automatically suitable for client authentication. |

**Keep these concepts separate:** issuance answers “who signed this certificate?”; trust answers “does this client accept that signer and chain?”; identity answers “does the certificate represent the requested hostname or workload?”; encryption protects traffic on a connection; authorization answers “may this identity perform this action?” TLS or mTLS does not replace application authorization.

### TLS failure decision tree (overview)

```text
HTTPS fails
  |
  +-- TCP connection fails? -> inspect port mapping, listener, controller, route
  |
  +-- TLS handshake fails? -> inspect protocol/cipher, SNI, listener, key/cert match
  |
  +-- Handshake completes but client rejects certificate?
  |      -> check notBefore/notAfter and system clock
  |      -> check SAN against requested hostname
  |      -> check chain and trust anchor
  |
  +-- Client accepts cert but app request fails?
         -> inspect route attachment, Service endpoints, app logs, authorization
  |
  +-- Secret is new but endpoint serves old cert?
         -> inspect controller events/logs/reload behavior and actual serving path
```

### 6.3 Level 1 — Beginner: Foundations

### What a certificate proves—and what it does not

A certificate binds a public key to one or more identities under a CA signature. A client checks whether the certificate is within its validity interval, the chain leads to a trusted anchor, the requested hostname matches a SAN, and relevant usage constraints permit the operation. The private key must remain secret; possession of it lets a holder prove control of the corresponding public key during a handshake. A certificate is not proof that the application is benign, that a user has logged in, or that a request is authorized.

Key usage and EKU constrain intended use. Server TLS generally needs a certificate appropriate for server authentication; a client certificate for mutual TLS (mTLS) has a different role. Exact profile and algorithm requirements depend on the issuer and current security guidance. **[VERIFY]** Check current Mozilla TLS configuration guidance, NIST publications, and the chosen CA/controller documentation before selecting production algorithms or cipher policy.

### Termination choices

| Termination point | Encrypted segments | Plaintext exposure / trade-off |
|---|---|---|
| External load balancer | Client to load balancer | Backend may be plaintext; provider-specific certificate and health-check behavior. |
| Ingress controller | Client to controller | Controller-to-Service/Pod can be plaintext unless separately protected. Common for the local lab. |
| Gateway listener | Client to Gateway data plane | Listener certificate attachment and supported policy are implementation/version-sensitive. |
| Application Pod | Client to application | More end-to-end control, but application must manage certificate loading, rotation, and TLS configuration. |
| Mesh proxy | Workload-to-proxy and proxy-to-proxy can be encrypted under mesh policy | Does not automatically encrypt traffic before the first proxy or authorize every request. |

An HTTP-to-HTTPS redirect helps move browser navigation to HTTPS but the initial HTTP request is not protected. HSTS (HTTP Strict Transport Security) tells a supporting browser to use HTTPS for a domain for a policy period. HSTS cannot repair an invalid certificate and does not make the first visit safe unless browser policy already applies. HSTS preload and production-domain behavior are out of scope for a local lab.

### Inspect a certificate without weakening validation

For a reachable local TLS endpoint:

```bash
# File: commands/inspect-served-certificate.sh
set -euo pipefail
HOST="model-api.local"
PORT="8443"

openssl s_client -connect "127.0.0.1:${PORT}" -servername "${HOST}" -showcerts </dev/null
```

This is diagnostic output, not a complete trust assertion. Review the presented chain, negotiated protocol, and verification result. To extract the leaf certificate from a saved PEM file:

```bash
# File: commands/inspect-leaf.sh
set -euo pipefail
openssl x509 -in leaf.crt -noout -subject -issuer -serial -dates -fingerprint -sha256
openssl x509 -in leaf.crt -noout -text
```

`-text` can expose metadata and extensions; it does not print the private key. To test trust and hostname validation, use the intended hostname and root certificate:

```bash
# File: commands/verify-local-endpoint.sh
set -euo pipefail
curl --verbose --cacert ./lab-root.crt \
  --resolve model-api.local:8443:127.0.0.1 \
  https://model-api.local:8443/health
```

`--resolve` supplies a local address for the requested hostname while retaining the hostname for TLS validation and HTTP routing. It is useful when the lab's local name is not in public DNS. The endpoint must actually be listening on that port. A test with the wrong CA or wrong hostname should fail; that failure is evidence that validation is active. Do not use `curl -k` or `--insecure` as a fix. If used briefly to isolate a lab failure, label it diagnostic-only, never use it to declare success, and immediately repeat a correct validation test.

### Beginner errors → symptom → cause → correction

| Error | Symptom | Likely cause | Correction |
|---|---|---|---|
| Connect by IP while certificate only has DNS SAN | Hostname mismatch | Requested identity differs from certificate SAN | Use the intended DNS name or issue a certificate with the correct IP SAN when that is the design. |
| Trust only the leaf when policy expects a CA | Trust failure on another client | Wrong trust-distribution model | Deliberately distribute the intended root/intermediate trust anchor. |
| Send only leaf when intermediate is required | Chain-building failure | Incomplete served chain | Configure the issuer/controller to provide required intermediates; verify the actual endpoint. |
| Check only Secret data | Secret appears correct, endpoint is stale | Consumer did not reload or request hit another endpoint | Inspect served certificate from the client path. |
| Set a redirect but omit TLS | Redirect lands on failing HTTPS endpoint | No usable certificate/listener | Establish and validate HTTPS before treating redirect as complete. |

### Small manual exercise

Before creating any cluster resource, inspect an existing certificate or use Lab 1 to generate a local-only CA and leaf. Record subject, issuer, SAN, validity, serial, and SHA-256 fingerprint. Do not record private-key bytes. Write down exactly which client trust store is used for the test; trust is a client-side decision.

### 6.4 Level 2 — Intermediate: Working Practice

### Local-only OpenSSL CA and leaf workflow

Run this in a disposable working directory, not in the repository. These files are **LAB-ONLY**. A root private key on a developer laptop is not a production PKI design; the exercise exists to make trust mechanics reproducible.

```bash
# File: lab/tls/create-lab-ca-and-leaf.sh
set -euo pipefail
umask 077
LAB_DIR="${PWD}/tls-lab-material"
mkdir -p "${LAB_DIR}"
cd "${LAB_DIR}"

# LAB-ONLY root CA key and self-signed root certificate.
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 -out lab-root.key
openssl req -x509 -new -sha256 -days 30 \
  -key lab-root.key -out lab-root.crt \
  -subj "/CN=M04 Local Lab Root CA" \
  -addext "basicConstraints=critical,CA:TRUE" \
  -addext "keyUsage=critical,keyCertSign,cRLSign"

# LAB-ONLY leaf key and CSR.
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out model-api.key
openssl req -new -key model-api.key -out model-api.csr \
  -subj "/CN=model-api.local"

cat > model-api.ext <<'EOF'
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=DNS:model-api.local
EOF

openssl x509 -req -in model-api.csr -CA lab-root.crt -CAkey lab-root.key \
  -CAcreateserial -out model-api.crt -days 7 -sha256 -extfile model-api.ext

# Verify the signature chain and key correspondence without printing key contents.
openssl verify -CAfile lab-root.crt model-api.crt
openssl x509 -in model-api.crt -pubkey -noout | openssl pkey -pubin -outform DER | openssl dgst -sha256
openssl pkey -in model-api.key -pubout -outform DER | openssl dgst -sha256
```

The two final SHA-256 digests should match; output is illustrative and depends on generated material. `openssl verify` validates this leaf against the supplied root, but does not prove a Kubernetes controller serves it. The extension file supplies a DNS SAN and server-auth usage. Exact OpenSSL option support can vary; verify with the installed `openssl version` and local man page if an option is unavailable.

### Create a Kubernetes TLS Secret

First confirm a deliberately named throwaway context. Never apply or delete resources on an unknown current context.

```bash
# File: commands/guard-kind-context.sh
set -euo pipefail
EXPECTED_CONTEXT="kind-m04-tls-lab"
ACTUAL_CONTEXT="$(kubectl config current-context)"
if [[ "${ACTUAL_CONTEXT}" != "${EXPECTED_CONTEXT}" ]]; then
  printf 'Refusing mutation: expected context %s, got %s\n' "${EXPECTED_CONTEXT}" "${ACTUAL_CONTEXT}" >&2
  exit 20
fi
kubectl --context "${EXPECTED_CONTEXT}" cluster-info
```

Create the cluster using `kind create cluster --name m04-tls-lab` only after reviewing the environment and ensuring that name is not a valuable existing cluster. The expected context is commonly `kind-m04-tls-lab`, but verify the actual context emitted by your local `kind` and kubeconfig. Then:

```bash
# File: commands/create-manual-tls-secret.sh
set -euo pipefail
EXPECTED_CONTEXT="kind-m04-tls-lab"
test "$(kubectl config current-context)" = "${EXPECTED_CONTEXT}" || { echo "Wrong context; refusing" >&2; exit 20; }
kubectl --context "${EXPECTED_CONTEXT}" create namespace ml-demo \
  --dry-run=client -o yaml | kubectl --context "${EXPECTED_CONTEXT}" apply -f -
kubectl --context "${EXPECTED_CONTEXT}" -n ml-demo create secret tls model-api-tls \
  --cert=./tls-lab-material/model-api.crt \
  --key=./tls-lab-material/model-api.key \
  --dry-run=client -o yaml | kubectl --context "${EXPECTED_CONTEXT}" apply -f -
kubectl --context "${EXPECTED_CONTEXT}" -n ml-demo get secret model-api-tls \
  -o custom-columns=NAME:.metadata.name,TYPE:.type
```

The Secret must be `kubernetes.io/tls`; the conventional data keys are `tls.crt` and `tls.key`. Do not print `.data` or raw Secret YAML into logs or evidence. Kubernetes Secret data is base64-encoded in API representations, not automatically confidential. RBAC, encryption at rest for etcd, audit policy, backups, and access boundaries are separate controls.

### Ingress attachment pattern

This example shows the generic Kubernetes Ingress TLS reference. It assumes an Ingress controller is already installed and configured to serve local traffic. Controller class name, local port mapping, path behavior, and reload behavior must match the Unit 3 implementation. **[VERIFY]** A TLS Secret is normally referenced in the same namespace as the Ingress. A controller must support the relevant Ingress behavior.

```yaml
# File: lab/manifests/model-api-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: model-api
  namespace: ml-demo
spec:
  # Add ingressClassName only after checking the class installed in the lab.
  tls:
    - hosts:
        - model-api.local
      secretName: model-api-tls
  rules:
    - host: model-api.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: model-api
                port:
                  number: 8000
```

The Service and its ready endpoints must exist, and the controller must recognize this Ingress. This manifest is an attachment example, not a complete application deployment. If the cluster uses Gateway API, use the selected implementation's documented listener certificate attachment; exact API version/channel and cross-namespace reference rules are **[VERIFY]**. Do not copy a Gateway listener from a different controller and assume compatibility.

### cert-manager objects and control flow

cert-manager reconciles declared certificate intent. A `Certificate` describes a desired certificate and target Secret. The referenced `Issuer` or `ClusterIssuer` supplies signing/issuance behavior. The controller creates supporting resources and updates status as it reconciles; exact resource details and timings vary by issuer and version.

```text
Issuer (namespace-scoped) OR ClusterIssuer (cluster-scoped)
                         |
                         v
                 Certificate (namespace)
                         |
                         v
               CertificateRequest (namespace)
                         |
            +------------+-------------------+
            |                                |
      CA/SelfSigned path                 ACME path
            |                                |
        signer logic                 Order -> Challenge(s)
            |                                |
            +---------------+----------------+
                            v
                Secret: tls.crt + tls.key
                            |
                            v
                 Ingress/Gateway consumer
                            |
                            v
            Validate actual certificate over TLS
```

- **Issuer:** namespaced cert-manager resource; it can generally be referenced by Certificates in its namespace.
- **ClusterIssuer:** cluster-scoped resource that can serve Certificates across namespaces, making its permissions and tenant boundaries important.
- **Certificate:** namespaced desired-state object; specifies `secretName`, `dnsNames`, and `issuerRef`, plus optional lifecycle/key settings.
- **CertificateRequest:** namespaced signing request used in the issuance workflow.
- **Order / Challenge:** ACME workflow resources for orders and domain-control challenges; not used in every issuer path.
- **SelfSigned issuer:** creates a self-signed certificate; useful for bootstrapping a root certificate but does not create a public trust relationship.
- **CA issuer:** signs leaves using a CA certificate and key stored in a Secret; protecting that CA key is critical.

Resource scope and exact state transitions should be checked against the installed cert-manager version's API reference. **[VERIFY]** Current cert-manager documentation must confirm the chosen installation method, CRDs, supported Kubernetes versions, API fields, key rotation behavior, and renewal-trigger procedure.

### Recommended lab pattern: explicit Certificate

For this unit, prefer an explicit `Certificate` resource over Ingress-shim because it makes issuer, SAN, Secret name, and lifecycle intent visible in one place. Ingress-shim can be useful when a team intentionally wants a controller-created Certificate based on Ingress annotations; its annotation semantics and issuer defaults must be reviewed carefully. Avoid having two controllers or declarative sources compete over the same Secret.

```yaml
# File: lab/manifests/lab-selfsigned-issuer.yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: lab-selfsigned
  namespace: ml-demo
spec:
  selfSigned: {}
---
# File: lab/manifests/lab-root-certificate.yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: lab-root
  namespace: ml-demo
spec:
  isCA: true
  commonName: M04 Local Lab Root CA
  secretName: lab-root-ca
  issuerRef:
    name: lab-selfsigned
    kind: Issuer
  # Omitted duration/key options use installed-version defaults; inspect the result.
```

This bootstraps a self-signed root Secret. A CA issuer then references the CA Secret. Do not use this as a production root-CA arrangement: a production root should usually be offline or strongly isolated, with controlled intermediate issuing CAs.

```yaml
# File: lab/manifests/lab-ca-issuer-and-api-certificate.yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: lab-ca
  namespace: ml-demo
spec:
  ca:
    secretName: lab-root-ca
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: model-api
  namespace: ml-demo
spec:
  secretName: model-api-tls
  dnsNames:
    - model-api.local
  issuerRef:
    name: lab-ca
    kind: Issuer
  # duration and renewBefore intentionally omitted in this baseline.
```

**[VERIFY]** Validate these manifests against the CRDs actually installed by the chosen cert-manager release. In particular, confirm current defaults and minimum validity/renewal constraints before setting short durations. The Secret created by the Certificate replaces the manually created Secret of the same name; do not run both patterns concurrently against one Secret. For a clean cert-manager lab, remove the manual Secret first only after verifying the context and confirming the lab owns it.

### Install cert-manager safely

Use the official cert-manager installation documentation and choose one supported installation route (official manifest or Helm if the current official instructions recommend it). The command below intentionally contains a placeholder and is not executable until a human verifies and substitutes a real release version and the canonical official manifest path.

```bash
# File: commands/cert-manager-install-template.sh
set -euo pipefail
EXPECTED_CONTEXT="kind-m04-tls-lab"
test "$(kubectl config current-context)" = "${EXPECTED_CONTEXT}" || { echo "Wrong context; refusing" >&2; exit 20; }

# TEMPLATE ONLY: verify current official instructions and substitute <VERSION>.
# Do not execute with the literal placeholder.
# kubectl apply -f <OFFICIAL_CERT_MANAGER_MANIFEST_URL_FOR_VERSION>
kubectl --context "${EXPECTED_CONTEXT}" get crd certificates.cert-manager.io
kubectl --context "${EXPECTED_CONTEXT}" get pods -A
```

CRDs and admission webhooks must be ready before applying custom resources or relying on server-side dry-run. **[VERIFY]** Confirm the official install page's current manifest URL, release version, Kubernetes compatibility, CRD installation/update process, and whether Helm or manifest installation is recommended. Do not delete cert-manager CRDs as routine cleanup: deleting a CRD can delete all custom resources of that kind and may cause broad operational impact.

### Renewal lifecycle and consumer reload

A `Certificate` expresses desired state. cert-manager schedules renewal ahead of expiry according to its configuration and installed-version behavior. `duration` and `renewBefore` influence lifecycle timing; exact constraints and the current default must be verified. The resulting Secret may be updated, but a consumer must observe the new content. Some controllers watch Secrets and reload certificates; others may have implementation-specific behavior or defects. Applications that read a certificate only at startup may need a controlled restart or an application-specific reload mechanism.

Always compare at least three layers: (1) Certificate status and events, (2) Secret certificate metadata/fingerprint, and (3) the certificate actually served from the client path. Only the third confirms what a client receives at that endpoint. Never claim zero downtime without repeated client requests across the rotation window and recorded results.

### Pattern and anti-pattern tables

| Pattern | Appropriate use | Guardrail |
|---|---|---|
| Manual TLS Secret | Small diagnostic exercise or externally managed certificate | Define owner, renewal process, and reload test; avoid permanent manual drift. |
| Explicit `Certificate` | Recommended learning pattern and clear GitOps intent | One authoritative owner for the target Secret. |
| Ingress-shim | Standardized issuance from Ingress metadata | Review annotations, issuer scope, and controller assumptions. |
| Namespaced `Issuer` | Namespace-local ownership and boundaries | RBAC still determines who can create Certificates and read Secrets. |
| `ClusterIssuer` | Shared platform-managed issuer | Add admission/policy controls and carefully restrict Secret/Certificate creation. |

| Bad configuration / practice | Production consequence | Correction |
|---|---|---|
| Put a private key in Git | Long-lived credential exposure | Generate locally; rotate if committed; use secret-scanning and repository history response. |
| Treat base64 as encryption | Key readable by anyone with Secret access | Least-privilege RBAC, etcd encryption at rest, audit and backup controls. |
| Verify only `Certificate Ready=True` | Endpoint may still serve stale material | Probe the actual TLS endpoint and compare fingerprints/serials. |
| Use a root CA key as routine leaf signer | Root compromise has broad blast radius | Keep root offline; use constrained intermediate issuing CA. |
| Share a ClusterIssuer without tenant controls | Unintended certificate identities or Secret access | Scope permissions, enforce allowed names/issuers, audit ownership. |
| Turn off client validation to “fix” TLS | Enables interception and masks identity errors | Repair chain, SAN, trust distribution, clock, or served certificate. |

### 6.5 Level 3 — Advanced: Production Engineering

### ACME awareness: HTTP-01, DNS-01, and local CA

ACME automates certificate issuance by proving control of requested identifiers. HTTP-01 proves control through a challenge response reachable at a domain's HTTP endpoint; it commonly requires public reachability for public certificate authorities. DNS-01 proves control using a DNS TXT record and can support wildcard identifiers because the proof is DNS-based. Wildcard public certificates require DNS-01 in the standard public ACME workflow. Exact CA rules and constraints should be checked against the selected CA's current documentation.

| Option | How it works | Fit for this learner |
|---|---|---|
| HTTP-01 | CA checks a challenge response over HTTP for a domain | Not used: no public domain or public endpoint in this lab. |
| DNS-01 | CA validates a DNS TXT record, often via DNS API credentials | Awareness only; credentials and DNS automation introduce risk. |
| Local CA | Local root signs a leaf trusted explicitly by the test client | Recommended for local-only, zero-budget practice. |
| Local ACME test server (e.g. Pebble) | Test ACME server simulates protocol workflows | Optional stretch only; version, installation, trust and API behavior `[VERIFY]`. |

Public ACME rate limits change and vary by CA. **[VERIFY]** Consult the selected CA's official rate-limit documentation before designing automation; no numerical limit is asserted here. Do not point this lab at a real public domain or public ACME account.

### Private PKI design and key algorithms

A common production pattern is an offline root CA that signs one or more intermediates, with intermediates issuing shorter-lived workload or service certificates. Trust anchors are distributed through an explicit client trust-management process. Ownership must cover issuance, renewal, monitoring, key custody, incident response, backup/recovery, and retirement. A developer laptop's lab root key is not suitable as a shared production CA key.

Choose algorithms, key sizes, validity periods, and protocol/cipher policy using current guidance and compatibility testing—not folklore or a copied cipher list. TLS 1.2 and TLS 1.3 differ in handshake and cipher-suite negotiation. **[VERIFY]** Use current Mozilla TLS configuration guidance, NIST publications, OpenSSL support, and controller-specific documentation. The exact meaning and behavior of cert-manager `rotationPolicy` is version-sensitive; inspect the installed API reference and release notes before relying on it.

A client-authentication certificate is not interchangeable with a server-authentication certificate. Extended Key Usage and issuer policy must match the intended purpose. Workload mTLS adds client identity and authenticated transport between peers, but authorization still needs a policy decision. Unit 8 handles mesh mTLS configuration.

### Issuer scope and multi-tenancy

A namespaced `Issuer` is often easier to align with team ownership, but namespace boundaries alone are not a complete security boundary. A `ClusterIssuer` is cluster-scoped and may be consumed by Certificates in multiple namespaces, which can simplify operations while increasing the impact of an over-permissive identity or compromised issuer. Restrict who may create `Certificate` objects, which issuer references are allowed, which SANs may be requested, and who can read resulting Secrets. Consider admission policy, audit trails, and separate issuers for distinct trust domains. M14 expands this to multi-cluster PKI and trust federation.

### Certificate observability and alert design

Track the certificate's expiry horizon, issuance/renewal failures, Certificate readiness, TLS handshake errors, and freshness of the certificate actually served. The candidate metric `certmanager_certificate_expiration_timestamp_seconds` is **[VERIFY]** until confirmed in the selected cert-manager version and its metric documentation. Do not assume labels or alert-rule syntax from an example on another release. If the metric is absent or its semantics differ, use a command-based inventory check while building verified monitoring.

A useful alert design contains:

- **Signal:** days until expiry and renewal readiness, plus an independent external probe of the served certificate.
- **Thresholds:** configurable examples such as warning at 21 days and critical at 7 days **[ILLUSTRATIVE]**; choose thresholds based on renewal lead time, incident response coverage, and certificate inventory.
- **Owner:** named platform or service owner, not just a generic team mailbox.
- **Runbook:** inspect issuer and Certificate status, related events, controller logs, Secret metadata, then served certificate.
- **Test:** create a short-lived certificate only after verifying minimum-duration constraints, or use a safe synthetic alert test; never wait for production expiry to test alerting.
- **False positives:** stale inventory, multiple replicas/endpoints, clock skew, disabled metrics, or a certificate that exists in a Secret but is not served.

### Secret security controls

Kubernetes Secret objects are not automatically encrypted at rest merely because their values are base64 encoded. Use least-privilege RBAC; avoid broad `list`/`get` access to Secrets; enable and validate etcd encryption at rest in clusters where the platform supports it; audit Secret access; restrict backup access; and prevent raw Secret YAML or keys from entering CI logs. Treat backup copies as sensitive. M09 covers broader secret management and workload identity. This lesson does not prescribe a universal production secret backend.

### Additional awareness topics

- **trust-manager:** can help distribute trust bundles; verify current project documentation, supported APIs, and bundle semantics before adoption.
- **External issuers:** Vault or cloud CA integrations can centralize key custody or issuance policy, but require identity, permissions, network, and availability design.
- **OCSP stapling and revocation:** client support and deployment behavior vary; revocation is not guaranteed to be checked by every client. Do not promise immediate invalidation without validating the client population and mechanism.
- **Certificate Transparency:** public certificate logging supports visibility into publicly trusted certificate issuance; it is not a private-PKI inventory substitute.
- **Metrics:** verify names, labels, scrape endpoint, and metric semantics for the installed release before publishing an alert rule.

### Production trade-offs

| Decision | Option A | Option B | Decision factors |
|---|---|---|---|
| Termination point | Ingress/Gateway | Application/mesh proxy | Where plaintext is acceptable, ownership, reload semantics, observability, and workload requirements. |
| Lifecycle | Manual Secret | cert-manager Certificate | Manual simplicity versus repeatable reconciliation and lifecycle visibility. |
| Issuer scope | Namespaced Issuer | ClusterIssuer | Team autonomy versus central control and cross-tenant blast radius. |
| Trust model | Public ACME | Private CA | Publicly trusted internet identity versus internal identity, trust distribution, and CA operations. |
| Leaf lifetime | Longer-lived | Shorter-lived | Renewal reliability, incident exposure window, issuer availability, and operational maturity. |

Short-lived leaves can reduce the time a stolen leaf remains useful, but only if renewal, monitoring, trust distribution, and reload behavior are reliable. Shortening lifetime without operational readiness can increase outage frequency.

### Measure renewal and reload rather than assuming it

For a controlled lab, record the served certificate fingerprint and `notAfter` before renewal, wait for the controller's documented renewal trigger or use a version-verified procedure, then poll the endpoint until it serves the replacement. Run repeated requests during the observation window and record failures. A changed Secret proves the Kubernetes object changed; a changed endpoint fingerprint proves the observed endpoint began serving new material. Neither one alone proves zero downtime, nor does one successful request prove all replicas/endpoints converged.

### 6.6 Level 4 — Expert: Operating at Scale and Under Failure

### Expired-certificate outage runbook

**Symptom:** clients report certificate expired, trust failure, or intermittent HTTPS errors; application Pods may remain healthy.

1. **Scope safely.** Identify the affected hostname, client population, endpoint path, and time of first failure. Avoid broad restarts or deleting Secrets before preserving evidence.
2. **Inspect what is served.** Use `openssl s_client` with the correct SNI and capture the leaf certificate metadata/fingerprint. Probe each endpoint or load-balancer path where possible.
3. **Classify the failure.** Compare `notBefore`/`notAfter`, SAN, issuer/chain, client trust, local system clock, negotiated protocol, and SNI. Do not treat all TLS failures as expiry.
4. **Inspect desired state.** `kubectl describe certificate`, related `CertificateRequest`, `Issuer`/`ClusterIssuer` readiness, events, and cert-manager controller logs. For ACME only, inspect `Order`/`Challenge` resources.
5. **Mitigate.** Restore the last known-good certificate through the approved path or repair issuance and reload. Confirm the private key matches the certificate and the client trusts the chain. A temporary bypass of validation is not a mitigation.
6. **Verify recovery.** Probe the real endpoint using normal validation; compare served fingerprint/serial/expiry; run representative API requests; monitor errors.
7. **Prevent recurrence.** Assign inventory ownership, expiry alerts, renewal-failure alerts, a renewal game day, controller reload tests, and evidence retention.

### Renewal failure diagnosis

| Symptom | Hypothesis | Evidence/test | Safe mitigation | Prevention |
|---|---|---|---|---|
| Certificate not Ready | Issuer unavailable or request rejected | `describe certificate`, issuer status, events | Repair issuer reference or credentials | Alert on readiness and age of pending request |
| ACME challenge pending | DNS/HTTP validation unreachable | Inspect `Order`/`Challenge`, DNS records and reachability | Fix challenge routing/credentials | Test DNS/HTTP automation before rollout |
| Secret exists but endpoint expired | Consumer did not reload or endpoint differs | Inspect Secret metadata and served certificate | Trigger documented reload/restart only after safety review | Add end-to-end served-cert probe |
| Renewals stop after issuer deletion | Existing leaf remains usable but future issuance fails | Inspect issuer existence/readiness and Certificate events | Restore issuer from reviewed configuration | Protect issuer changes with review and alerts |
| Key/cert mismatch | Secret was manually edited or partially rotated | Compare public-key digests locally; inspect events/logs | Reissue and atomically restore valid Secret | Single source of truth; RBAC; avoid manual Secret edits |
| Webhook/controller unavailable | Reconciliation or admission disrupted | Pod readiness, logs, API events, CRD/webhook health | Restore compatible controller/webhook deployment | Upgrade test, availability monitoring, rollback plan |

Do not print Secret data to diagnose a mismatch. Compare public-key digests from local certificate and key files or use a carefully reviewed command that emits only a match/mismatch result.

### Issuer deletion and delayed failure

Deleting or misconfiguring an issuer does not necessarily invalidate an already-issued leaf immediately. The endpoint may continue serving that leaf until it expires or the consumer changes it. The latent failure appears when renewal or a new issuance is required. Record a healthy baseline, perform the deletion only in the throwaway lab, observe the new issuance path fail, restore the issuer, and verify recovery. This models why issuer readiness and certificate expiry must be monitored independently.

### CA rotation without avoidable downtime

1. Inventory every certificate and every client trust store that relies on the old CA.
2. Establish the new trust anchor alongside the old one where the clients support overlap.
3. Validate trust distribution before issuing replacement leaves.
4. Issue new leaves from the new CA and roll them out in bounded rings.
5. Verify actual served certificates and client validation from representative consumers.
6. Keep rollback criteria explicit; do not remove old trust until migration evidence shows it is no longer needed.
7. Remove old trust only after the dependency inventory and rollback window are satisfied.

Rotation is not complete when the CA Secret changes. It is complete when consumers and clients have converged, old credentials are retired, and evidence supports the transition.

### Exposed wildcard private key

A wildcard private key may authorize impersonation of multiple hostnames within its scope, so blast radius can be much larger than a single service. Restrict access immediately, preserve audit evidence, identify all consumers and copies, replace the key and certificates, and revoke the old certificate where the issuer/client ecosystem supports meaningful revocation. Rotate associated trust or credentials if evidence indicates CA or issuer compromise. Investigate repository history, CI logs, backups, developer machines, and access records. Never paste the exposed key into incident tickets or chat; preserve it only through approved evidence-handling controls.

### cert-manager upgrade and CRD risk

Test upgrades in a disposable cluster using the intended Kubernetes version. Review release notes, API changes, CRD installation/update requirements, webhook behavior, and issuer-specific behavior. Back up relevant configuration and custom resources where appropriate. Validate a new issuance and renewal in the test cluster before production rollout. **Do not delete CRDs as routine cleanup:** doing so can delete custom resources and break controllers that depend on them. If a rollout fails, restore a compatible controller/CRD state using the documented recovery procedure rather than improvising schema rollback.

### Risk register

| Event | Primary risk | Immediate controls | Recovery / prevention |
|---|---|---|---|
| Wildcard key exposed | Broad hostname impersonation | Restrict access; preserve evidence; identify copies | Reissue/rotate; revoke where effective; audit; shorten exposure window |
| CA rotation | Trust gap or mixed-generation failures | Maintain old/new trust overlap | Ring-based leaf replacement; verify clients; remove old trust after evidence |
| ClusterIssuer deleted | Future issuance/renewal silently fails | Alert on issuer readiness/existence | Restore reviewed issuer; test renewal; protect changes |
| cert-manager upgrade | CRD/webhook/controller incompatibility | Pause rollout; inspect release notes and readiness | Test in throwaway cluster; documented rollback; no casual CRD deletion |

### Fleet operations and policy-as-code

Maintain a certificate inventory with hostname, namespace, issuer, Secret, expiry, owner, renewal status, alert, and evidence. Define policy for permitted issuer references, SAN scope, validity periods, key handling, namespace ownership, and exceptions. Enforce through admission policy or platform workflows appropriate to the cluster; verify the policy engine and exact rule syntax separately. M08 covers automated progressive delivery/GitOps, M09 covers secrets/identity, M10 covers SLOs, M11 covers the full observability stack, and M14 covers multi-cluster concerns.

### 6.7 SRE lens

Certificate operations need indicators tied to user impact, not only controller health.

| Indicator | Measurement method | Operational question |
|---|---|---|
| Days to expiry | Certificate metadata or verified expiry metric | Is there enough time to recover if renewal fails? |
| Renewal success/failure | Certificate readiness, events, issuance outcomes | Is automation renewing before the safety window? |
| Certificate readiness | Resource status plus age of pending work | Is desired state being reconciled? |
| TLS handshake errors | Client/proxy telemetry verified for the selected implementation | Are clients failing before HTTP reaches the application? |
| Served-certificate freshness | External/local probe of endpoint fingerprint and `notAfter` | Did the consumer actually reload? |
| Request success during rotation | Repeated client probes and application request checks | Did rotation affect availability? |

Alert design should include a named owner, actionable runbook, severity tied to remaining recovery time, and a tested notification path. Expiry is often a time-to-impact signal; a failed renewal can be urgent long before clients see errors. Consider blast radius: a shared ClusterIssuer or wildcard key can affect many namespaces, while a namespaced leaf may be isolated. On a laptop lab, the “cost” is primarily CPU, memory, and debugging time; do not run a mesh or full monitoring stack at the same time as certificate labs on the 4-CPU/8-GB baseline.

### 6.8 Security lens

| Threat | Control | How to verify | Residual risk |
|---|---|---|---|
| Private-key theft | Narrow Secret RBAC, protected files, no Git/CI logging | Review RBAC, repository diff/history, CI logs, file permissions | Authorized reader or host compromise can still expose keys |
| Untrusted or incorrect SAN | Issuance policy and client hostname validation | Inspect SAN and run correct/wrong-host tests | Misissued but trusted identities may still occur |
| Broad issuer permissions | Namespaced issuers where appropriate; policy on ClusterIssuer use | Review RBAC, admission controls, issuer references | Platform admin remains high privilege |
| DNS challenge credentials leaked | Least-privilege DNS API token, scoped zone permissions, rotation | Audit secret access and provider permissions | Provider account compromise may affect zone |
| Stale/expired certificate | Expiry alerts and served-cert probes | Compare expiry metadata and endpoint handshake | Probe coverage may miss an alternate endpoint |
| Plaintext after termination | Document and protect each segment; TLS/mTLS where required | Trace path and inspect listener/backend configuration | Node-level or application compromise remains possible |
| Secret backup exposure | Encrypt/protect backups and restrict restore access | Review backup access and retention | Old copies may outlive certificate rotation |
| Unauthorized certificate issuance | Restrict Certificate creation and SAN/issuer scope | Review RBAC, audit logs, policy tests | Policy gaps or privileged bypass remain |

TLS and mTLS provide transport security and identity signals, not application authorization. A service must still enforce which caller may score a model, read features, query Postgres/Redis, or access metrics. Unit 5 NetworkPolicy can constrain network reachability but is not a replacement for TLS identity or application authorization.

### 6.9 Production checklist

Use this as a review gate; check an item only after producing evidence.

- [ ] **Inventory:** hostname, namespace, issuer, Secret, expiry, owner and evidence are recorded. Verify with `kubectl get certificate -A` plus a maintained inventory; the command alone may not include every manually managed certificate.
- [ ] **SAN and hostname:** inspect certificate SANs and test the intended hostname with normal validation.
- [ ] **Trust chain:** test with the intended client trust store; document trust-anchor distribution.
- [ ] **Issuer readiness:** inspect issuer status, events, and references.
- [ ] **Renewal window:** verify current `duration`/`renewBefore` semantics for the installed release and confirm renewal lead time is sufficient.
- [ ] **Monitoring:** test expiry and renewal-failure alerts; verify metric name/labels before deploying rules.
- [ ] **Consumer reload:** compare Secret metadata to the certificate actually served.
- [ ] **RBAC:** review who can create Certificates, read Secrets, and alter issuers.
- [ ] **Encryption at rest:** verify cluster etcd encryption configuration independently of base64 representation.
- [ ] **Private-key handling:** inspect repository diff, local permissions, CI logs, and backup paths; never include key material in evidence.
- [ ] **CA rotation:** document trust overlap, rollout rings, rollback criteria, and old-trust removal conditions.
- [ ] **Incident runbook:** test expiry, issuer deletion, and failed renewal in a throwaway environment.
- [ ] **Evidence retention:** save sanitized metadata, fingerprints, status/events, tests, and cleanup proof—not raw Secret YAML or keys.

### 6.10 Hands-on lab set

| Lab | Goal | Steps / evidence | Cleanup | Stretch |
|---|---|---|---|---|
| Lab 1 | Manual TLS Secret and local trust | Generate local CA/leaf; verify SAN/key match; attach to existing lab Ingress; correct and deliberately incorrect trust tests | Remove owned resources and crypto directory; verify absent | Compare client trust stores on WSL2 and native Linux |
| Lab 2 (mandatory) | cert-manager local CA issues API ingress certificate and renewal is observed | Install verified cert-manager release; bootstrap CA; create Certificate; verify served chain; trigger renewal using version-verified procedure; test issuer failure and recovery | Delete only lab-owned namespace/cluster and local material; verify cleanup | Add a second test client and repeat trust validation |
| Lab 3 | Renewal failure incident runbook | Misconfigure a lab issuer reference or delete the lab issuer after recording baseline; capture events/status/logs; restore and verify | Restore healthy issuer before teardown | Write an incident timeline with hypotheses and evidence |
| Lab 4 (optional) | Expiry alert design | Verify metric or run command-based expiry check; record alert intent, owner, threshold and test | Remove temporary rule/config and test resources | Build a small inventory report from sanitized certificate metadata |

All time and resource figures below are planning estimates, not measurements. The labs are local only and do not require public DNS or internet-exposed endpoints. If the laptop is under memory pressure, run one lab at a time and remove the previous throwaway cluster before starting another.

### Lab 1 — Manual TLS Secret and local trust

**Goal / success criteria:** a local client succeeds when it trusts the lab root and uses the correct SAN; a wrong trust anchor or hostname fails. **Estimate:** 45–90 minutes; small cluster plus a few local crypto files. **Prerequisites:** OpenSSL, `curl`, `kind`, `kubectl`, a working Ingress controller from Unit 3, and an application Service named `model-api` in `ml-demo`.

1. Create or reuse only the explicitly named `kind-m04-tls-lab` context; verify `kubectl config current-context`, `kind get clusters`, and `kubectl --context kind-m04-tls-lab cluster-info`. Stop if the expected cluster identity does not match.
2. Run the local CA/leaf workflow in Section 6.4. Verify the leaf chain, SAN, dates, and public-key digest correspondence. Never `cat` a `.key` file.
3. Create `model-api-tls` from local files with the guarded Secret command. Apply the Ingress attachment only after confirming the Service and controller class.
4. Configure a local-only host port mapping using the controller-specific Unit 3 procedure. Do not expose a public firewall port. If using WSL2, run Docker, `kind`, and `kubectl` in the same environment where their configuration is available; Windows `localhost`, WSL2 `localhost`, a kind node, and a Pod are distinct network contexts.
5. Correct test: use `curl --cacert lab-root.crt --resolve model-api.local:8443:127.0.0.1 https://model-api.local:8443/health` after adapting the port to the actual mapping. Wrong-trust test: use a different CA file and confirm validation fails. Wrong-host test: request a hostname not present in SAN while directing it to the same local endpoint.
6. Capture only sanitized output, certificate metadata and fingerprints. Expected results are **[ILLUSTRATIVE]**: correct CA + correct hostname validates; wrong CA reports a trust error; wrong hostname reports an identity mismatch.
7. Evidence proves that the tested client validated the certificate on that path at that time. It does not prove every client trust store is configured correctly or that production traffic uses the same path.

**Cleanup:** verify context before each mutation. Delete only the Ingress and Secret created by this lab; remove the local CA/leaf directory after evidence is sanitized. Verify the resources are absent and no port-forward remains. If the lab created the entire cluster solely for this exercise, delete it only after checking `kind get clusters` and confirming the exact lab name. Re-run by recreating the lab directory and following the same guarded steps.

### Lab 2 — Mandatory: cert-manager local CA issues the API ingress certificate

**Goal / success criteria:** a Certificate becomes ready, the Ingress endpoint serves a chain trusted by the lab client, the served certificate changes after a version-supported renewal trigger, and a deliberately broken issuer prevents new issuance until restored. **Estimate:** 2–4 hours; small `kind` cluster plus cert-manager controller/webhook. These are planning estimates, not measured resource consumption.

**Prerequisites and guard:** Docker, `kind`, `kubectl`, OpenSSL, `curl`, a local Ingress controller, and enough disk/RAM for a throwaway cluster. Create or reuse the named lab cluster only after confirming it is not valuable. Before every mutation, assert `kubectl config current-context` equals `kind-m04-tls-lab` and run `kubectl --context kind-m04-tls-lab cluster-info`. A context name is not proof by itself; check cluster identity and ownership.

**Step 1 — Install cert-manager.** Read the current official cert-manager installation documentation. Select a release compatible with the actual Kubernetes version; replace `<VERSION>` and the official installation path only after checking the docs. Do not execute the literal placeholder. Follow the documented CRD installation route and wait for controller/webhook readiness using resource names from the selected release. Check `kubectl get crd certificates.cert-manager.io` and `kubectl get pods -A`. **[VERIFY]** Installation URL, release version, CRD update process, supported Kubernetes versions, and Helm-versus-manifest route are intentionally not hard-coded.

**Step 2 — Bootstrap the lab root.** Apply the `lab-selfsigned` Issuer and `lab-root` Certificate manifests in Section 6.4 after checking that the `cert-manager.io/v1` CRDs are installed. Wait by observing status/events, not by assuming a fixed transition time. Verify the root certificate metadata from its Secret without printing Secret data. Then apply `lab-ca` Issuer and `model-api` Certificate. For each mutation, repeat the context guard.

**Step 3 — Confirm resource state.**

```bash
# File: commands/inspect-cert-manager-state.sh
set -euo pipefail
EXPECTED_CONTEXT="kind-m04-tls-lab"
test "$(kubectl config current-context)" = "${EXPECTED_CONTEXT}" || { echo "Wrong context; refusing" >&2; exit 20; }
kubectl --context "${EXPECTED_CONTEXT}" -n ml-demo get issuer,certificate,certificaterequest
kubectl --context "${EXPECTED_CONTEXT}" -n ml-demo describe issuer lab-ca
kubectl --context "${EXPECTED_CONTEXT}" -n ml-demo describe certificate model-api
kubectl --context "${EXPECTED_CONTEXT}" -n ml-demo get events --sort-by=.metadata.creationTimestamp
```

Representative state is **[ILLUSTRATIVE]**: `lab-ca` reports Ready, and `model-api` eventually reports Ready with the target Secret present. A status condition is evidence of controller reconciliation, not proof that the ingress endpoint serves the new certificate. If a resource remains pending, inspect conditions, events, issuer reference, CA Secret existence, RBAC, and controller logs before changing fields.

**Step 4 — Attach the Certificate Secret.** Ensure the Ingress references `model-api-tls` and hostname `model-api.local`; confirm Service `model-api` has ready endpoints. Use the existing controller and its documented local port mapping. If the selected implementation cannot serve the Ingress/TLS setup, document the incompatibility and switch to the controller-supported alternative already available in the lab. Do not assume Gateway listener behavior without checking the implementation's documentation.

**Step 5 — Verify the real served path.** Use OpenSSL with SNI and `curl --cacert` with the local root. Save the leaf's serial, SHA-256 fingerprint, SAN, issuer, and `notAfter` before renewal. Verify that the endpoint serves the expected hostname certificate, not merely that the Secret exists. If the controller path uses a different port or address, substitute the observed mapping.

**Step 6 — Trigger renewal safely.** Do not invent an annotation or assume any minimum duration. First inspect the installed cert-manager version's Certificate API reference and renewal documentation. Use the documented, supported early-renewal procedure for that release. If choosing a short-lived lab certificate, verify minimum duration and `renewBefore` validation rules first, and change the Certificate declaratively only within the throwaway namespace. If the installed release's supported trigger cannot be confirmed, stop this step and mark it unresolved rather than guessing. **[VERIFY: current official cert-manager renewal/trigger documentation and installed release constraints.]**

**Step 7 — Prove endpoint convergence.** Observe Certificate status/events, then repeatedly query the actual endpoint and capture served serial/fingerprint/expiry. A new Secret fingerprint alone is insufficient. Record results:

| Observation | Before renewal | After renewal |
|---|---|---|
| Certificate Ready condition |  |  |
| Secret leaf serial / fingerprint |  |  |
| Endpoint-served serial / fingerprint |  |  |
| Endpoint-served `notAfter` |  |  |
| Client validation result |  |  |
| Failed requests during repeated probe |  |  |

Do not claim zero downtime unless repeated probes actually ran and results show it; this lesson does not claim that this lab was executed.

**Step 8 — Controlled issuer failure and recovery.** Record healthy state and confirm the endpoint serves a valid leaf. **Warning: the next action deliberately breaks issuance in the throwaway namespace.** After verifying context and resource ownership, delete only `Issuer/lab-ca` or alter its reference in the lab Certificate. Observe the failure using `kubectl describe certificate`, related CertificateRequests, events, and controller logs. An already-issued leaf may continue serving until expiry or replacement; issuer deletion does not necessarily break the current TLS endpoint immediately. Restore the issuer manifest, verify readiness and issuance/reconciliation, and retest the endpoint. If a new issuance is not naturally triggered, use only the version-verified renewal procedure described in Step 6.

**Evidence:** store sanitized output in a local `evidence/unit-06/` directory outside the repository, or ensure it is excluded from commits. Include version inventory, resource status/events, certificate metadata/fingerprints, before/after table, correct and incorrect trust tests, issuer failure/recovery notes, and cleanup proof. Never include private keys, raw Secret YAML, tokens, or unredacted sensitive logs.

**Cleanup and post-cleanup verification:** after a final context/ownership check, delete only lab-owned resources or delete the entire named throwaway cluster if it was created for this lab. Do not delete CRDs as routine cleanup. Remove local lab crypto material securely according to the host's storage policy, and verify the temporary files and port-forwards are gone. Confirm the cluster is absent only if you intentionally deleted it. In WSL2, check both the environment where the files were created and any mounted Windows path; do not assume deleting one copy removes all copies.

### Lab 3 — Renewal failure and incident runbook

**Goal:** distinguish issuer failure from endpoint serving failure and recover safely. **Estimate:** 45–90 minutes; use the same throwaway cluster only after Lab 2 has been cleaned or restored. **Prerequisites:** working cert-manager install and lab-only Certificate.

1. Verify the named context and healthy baseline. Capture `Certificate` readiness, issuer readiness, endpoint fingerprint and expiry.
2. **Warning:** deliberately change only the lab Certificate's `issuerRef` to a nonexistent namespaced issuer, or delete the lab issuer after documenting the baseline. Never perform this in a shared cluster.
3. Inspect `kubectl describe certificate model-api`, related `CertificateRequest` resources, events, and cert-manager logs. If using ACME, inspect `Order` and `Challenge`; they may not exist for the CA issuer.
4. Classify evidence: missing issuer reference, denied request, absent CA Secret, invalid CA, webhook/controller unavailability, or consumer reload problem. Do not print Secret data.
5. Restore the known-good manifest and verify issuer readiness and Certificate reconciliation. Then verify the actual served certificate with normal trust/hostname validation.
6. **Expected output [ILLUSTRATIVE]:** events/conditions identify an unresolved issuer reference or issuance error; after restoration, the resource can reconcile. Exact wording and timing vary by release.
7. Evidence proves the observed failure and recovery path for this version/configuration; it does not prove every issuer implementation behaves identically.

**Cleanup:** restore healthy state before deleting resources. Check the context before every mutation, remove temporary manifests/material, verify no broken Certificate remains, and confirm the endpoint is either intentionally removed or healthy. Re-run by applying the known-good manifests first and repeating the same controlled fault.

### Lab 4 — Optional certificate expiry alert design

**Goal:** design a tested expiry alert without assuming a metric name or label schema. **Estimate:** 30–60 minutes; no full monitoring stack required. **Prerequisites:** a certificate to inspect and the installed cert-manager version's metric documentation if using metrics.

1. Inspect the certificate's `notAfter` using `openssl x509`; record the check time and timezone.
2. If using Prometheus metrics, verify the metric name, labels, semantics, and endpoint in the selected release documentation and actual `/metrics` output. The candidate `certmanager_certificate_expiration_timestamp_seconds` remains **[VERIFY]** until confirmed.
3. If not verified, use this command-based check as a starting point:

```bash
# File: commands/check-certificate-expiry.sh
set -euo pipefail
CERT_FILE="${1:?usage: check-certificate-expiry.sh path/to/cert.pem}"
command -v openssl >/dev/null
openssl x509 -in "${CERT_FILE}" -noout -enddate
```

This prints the expiry timestamp but does not calculate a fleet-wide alert or prove the serving endpoint uses this file. Add a reviewed parser and clock handling before automation. Do not treat a shell date parser as portable without testing it on the learner's platform.

4. Define alert intent, configurable warning/critical horizons **[ILLUSTRATIVE]**, owner, runbook, test, and false-positive handling. Verify the rule schema against the actual Prometheus Operator or Prometheus installation before applying any rule.
5. Test with a synthetic or lab-only certificate and record the expected alert state. Do not wait for a production certificate to near expiry.

**Cleanup:** remove temporary rule/config and synthetic resources; verify no monitoring stack was installed unintentionally. Evidence includes metric source/version, certificate expiry output, alert intent and test notes. The command alone proves only the local file's expiry metadata.

### 6.11 Self-check questions

1. **A certificate is within its validity window and correctly signed, but the client does not trust its CA. Is the connection valid?**  
   **Answer:** Not for that client's trust policy. A valid signature does not install a trust anchor. **Tempting wrong answer:** “The CA signed it, so all clients trust it.” Trust stores are client-specific.

2. **The certificate SAN is `DNS:model-api.local`, but the client requests `https://127.0.0.1`. Why can validation fail?**  
   **Answer:** The requested IP does not match the DNS SAN. Use the DNS name with a local resolution override, or issue a suitable IP SAN when appropriate. **Tempting wrong answer:** “The endpoint reaches the same server, so hostname does not matter.” Routing destination and authenticated identity are separate.

3. **cert-manager issues a leaf certificate. Does that guarantee clients trust it?**  
   **Answer:** No. Issuance and client trust distribution are separate. The client must trust the issuing chain and validate hostname and validity. **Tempting wrong answer:** “Ready means universally trusted.” `Ready` reflects controller state, not every client's trust store.

4. **What happens if an issuer is deleted while a valid leaf is already served?**  
   **Answer:** The existing endpoint may continue serving the leaf until expiry or replacement, while future issuance/renewal can fail. **Tempting wrong answer:** “Deleting the issuer immediately revokes all issued certificates.” Deletion is not universal revocation.

5. **Why is checking a TLS Secret insufficient?**  
   **Answer:** The controller may not have reloaded it, traffic may reach another endpoint, or the Ingress may reference a different Secret. Test the certificate actually served over the real client path. **Tempting wrong answer:** “The API object is correct, therefore every client sees it.”

6. **Does TLS or mTLS replace authorization?**  
   **Answer:** No. TLS protects transport and can authenticate a peer; application or policy enforcement decides what that identity may do. **Tempting wrong answer:** “An authenticated workload may access every API.”

7. **How should CA rotation be sequenced?**  
   **Answer:** Distribute new trust while old trust remains, issue new leaves, roll out and verify, then remove old trust only after migration evidence and rollback windows. **Tempting wrong answer:** “Replace the root and all clients immediately.” That can strand clients that have not received the new trust anchor.

8. **What is the safe response to exposed private key material?**  
   **Answer:** Restrict exposure, preserve evidence, identify scope/copies, replace key and certificate, revoke where effective, audit access and rotate related trust if needed. Never paste the key into logs/tickets. **Tempting wrong answer:** “Delete the file and move on.” Copies and repository history may remain.

9. **A new Secret fingerprint appears, but OpenSSL shows the old endpoint certificate. What does that suggest?**  
   **Answer:** The serving path has not converged, the request reaches a different endpoint, or the controller failed to reload. Inspect controller logs, Ingress references, endpoints, and every served endpoint. **Tempting wrong answer:** “Renewal is complete because the Secret changed.”

### 6.12 Evidence artifacts

Save sanitized evidence outside the repository in a local `evidence/unit-06/` directory, or otherwise ensure it is not committed. Suggested files:

- `versions.txt` — `kubectl version`, `kind version`, `openssl version`, cert-manager image/release information, and selected controller version.
- `served-cert-before.txt` and `served-cert-after.txt` — subject, issuer, SAN, serial, fingerprint, validity; no key material.
- `certificate-status.txt` — sanitized `kubectl get/describe certificate` output.
- `issuer-status.txt` — sanitized issuer status and relevant events.
- `renewal-results.md` — blank/filled before-and-after table, request test results, and failure count if measured.
- `trust-tests.txt` — correct CA/hostname test and controlled wrong-CA/wrong-host outcomes.
- `incident-notes.md` — symptom, hypothesis, test, root cause, mitigation, prevention.
- `cleanup-proof.txt` — absence of lab-owned resources, temporary port-forward processes, and crypto files.
- `review-checklist.md` — which version-specific documentation and controller behaviors were verified.

Evidence must not contain private keys, raw Secret YAML, base64 Secret data, DNS API tokens, public account credentials, or unredacted sensitive logs. A successful command proves only the behavior observed under that environment, version, path, and time.

### 6.13 Common interview and design-review questions

1. **Where would you terminate TLS for a model-scoring API?**  
   **Model answer:** Choose based on trust boundaries, backend encryption requirements, controller capabilities, certificate ownership, and reload behavior. Ingress termination is operationally simple but may leave controller-to-Pod traffic plaintext. Application termination extends the TLS boundary but moves lifecycle responsibility into the application. A mesh may encrypt workload traffic but adds another control/data plane. Evidence should include an explicit hop-by-hop path, client validation tests, and actual served-certificate checks.

2. **When choose public ACME versus private PKI?**  
   **Model answer:** Public ACME is suitable for publicly trusted domain identities when identifier validation and endpoint/DNS prerequisites can be met. Private PKI is suitable for internal identities where the organization controls trust distribution and CA operations. The choice depends on trust consumers, automation credentials, governance, revocation limitations, and availability. Do not use public ACME in this local lab.

3. **How do you diagnose a renewal failure?**  
   **Model answer:** Start with Certificate conditions/events and issuer readiness; inspect CertificateRequest and, for ACME, Order/Challenge; read controller logs; validate issuer references, credentials, DNS/HTTP challenge reachability, RBAC, CA Secret integrity, and installed API schema. Then compare Secret metadata to the actual served certificate. Repair the cause and verify with normal client validation.

4. **How do you rotate a CA without avoidable downtime?**  
   **Model answer:** Inventory dependencies, distribute the new trust anchor alongside old trust, issue replacement leaves, roll out in rings, test real client trust and served certificates, retain rollback criteria, then remove old trust after evidence proves migration. A root Secret replacement alone does not rotate clients or consumers.

5. **How do you design issuer tenancy and Secret access?**  
   **Model answer:** Prefer scope aligned to ownership, restrict Certificate creation and allowed SAN/issuer references, limit Secret reads, audit privileged operations, and apply admission policy where appropriate. A ClusterIssuer can reduce duplication but increases cross-namespace impact. Validate with negative tests that a tenant cannot request disallowed identities or read another tenant's private key.

### 6.14 Sources and verification notes

### Consulted sources

- The supplied `Roadmap_ptree.md` copy (`Roadmap(5).md` in the available files): M04 subtree and exact neighboring unit sequence.
- `PROMPT-Kubernetes-Networking-Ingress-and-Service-Mesh.md` (available copy): Unit 6 syllabus topics and M04 cross-module boundaries.
- Uploaded Unit 6 authoring prompt `Pasted markdown(20261027-201018).md`: required structure, labs, security constraints, audit rules.
- Neighboring lessons 01–05 in the available workspace: shared M04 terminology and the `ml-demo` namespace convention used in Unit 2.

### Known official references requiring current-version verification

- Kubernetes documentation: Ingress, TLS Secrets, Secrets, RBAC, API concepts, and Gateway API integration points.
- cert-manager documentation: installation, supported Kubernetes versions, CRDs, Certificate/Issuer/ClusterIssuer APIs, renewal, key rotation, metrics, ACME, and upgrades.
- Selected Ingress/Gateway controller documentation: TLS attachment, Secret watch/reload behavior, listener readiness, and local `kind` exposure.
- OpenSSL `s_client`, `x509`, `verify`, and key command documentation.
- RFC 8446 (TLS 1.3) and RFC 5246 (TLS 1.2).
- Mozilla TLS configuration guidance and NIST cryptographic publications.
- Kubernetes security guidance and Google SRE Book/Workbook for access controls, monitoring, and incident operations.

Canonical URLs and current release pages were not live-verified during this artifact creation; therefore they are intentionally not fabricated here.

### Unresolved verification items

1. Exact cert-manager release, supported Kubernetes version, official installation route/URL, CRD update behavior, and admission-webhook readiness requirements.
2. Installed-version API details and constraints for `Certificate.duration`, `renewBefore`, key algorithms, `rotationPolicy`, and supported early-renewal procedure.
3. Current metric names, labels, and semantics for certificate expiry/renewal monitoring.
4. Selected Ingress controller's installation, `IngressClass`, local port mapping, certificate reload behavior, and whether repeated probes are needed to test all endpoints.
5. Gateway API version/channel and implementation-specific listener certificate attachment if using Gateway instead of Ingress.
6. Current ACME provider rate limits, HTTP-01/DNS-01 requirements, and optional Pebble setup.
7. Current Mozilla/NIST algorithm and TLS policy recommendations.
8. Whether the actual learner environment's `openssl` supports the sample options and whether WSL2/Docker networking matches the assumed local path.

**Runtime execution status:** Reasoned review only; commands and labs were not executed in this environment. No current official documentation was live-verified during this authoring pass.

## Appendix A — Command and manifest reference

| Command / artifact | Purpose | Safe use / expected evidence | Caveat |
|---|---|---|---|
| `openssl s_client -connect host:port -servername name -showcerts` | Inspect actual handshake and presented chain | Save sanitized handshake, verification result and certificate metadata | Requires the real local endpoint and correct SNI |
| `openssl x509 -in leaf.crt -noout -subject -issuer -serial -dates -fingerprint -sha256` | Inspect leaf metadata | Subject, issuer, serial, validity and fingerprint | Does not prove endpoint serves this file |
| `openssl verify -CAfile lab-root.crt leaf.crt` | Verify chain against selected trust anchor | Successful verification for the supplied files | Does not prove all clients trust that root |
| `curl --cacert lab-root.crt --resolve model-api.local:8443:127.0.0.1 https://model-api.local:8443/health` | Test trust and hostname through local mapping | Validated request response | Adapt port to actual mapping; never treat `-k` as a fix |
| `kubectl get certificate,issuer,certificaterequest -n ml-demo` | Inspect cert-manager resources | Resource names and readiness overview | Requires installed CRDs for custom kinds |
| `kubectl describe certificate model-api -n ml-demo` | Diagnose conditions/events | Issuance and reconciliation evidence | Output wording/timing varies |
| `kubectl logs -n <verified-namespace> <verified-controller-pod>` | Inspect controller failure | Sanitized error context | Discover namespace/pod; do not assume names |
| `kubectl apply --dry-run=client -f manifest.yaml` | Client-side parsing/schema-light validation | Local parse and object rendering | Does not prove server schema acceptance |
| `kubectl apply --dry-run=server -f manifest.yaml` | Ask API server to validate without persistence | API-server validation result | Requires CRDs/webhooks ready and permission; not available for unknown custom kinds |
| `kubectl get crd certificates.cert-manager.io` | Confirm CRD presence | CRD listed | Presence alone does not prove controller/webhook readiness |
| `kubectl get events -n ml-demo --sort-by=.metadata.creationTimestamp` | Review recent events | Event sequence | Events expire and may not be a complete audit log |

## Appendix B — Troubleshooting decision trees

Each branch should be followed with evidence before mutation. Use the throwaway context guard before any repair that changes cluster state.

### B1. Client cannot connect over HTTPS

1. **Symptom:** TCP connection refused or timeout.  
   **Hypothesis:** wrong host port, controller not listening, kind mapping absent, or network context mismatch.  
   **Evidence:** `kind get clusters`, `kubectl get pods -A`, controller Service/Pod status, `ss -ltn` on the environment running the client.  
   **Interpretation:** no TLS handshake means certificate validation has not yet occurred.  
   **Mitigation:** repair the local port mapping/controller readiness; do not change certificate trust.  
   **Prevention:** document which host/WSL2/Node/Pod owns each address.

2. **Symptom:** TCP connects but handshake fails.  
   **Hypothesis:** SNI/listener mismatch, key/cert mismatch, unsupported protocol/cipher, or controller error.  
   **Evidence:** `openssl s_client` with explicit SNI; controller logs; certificate metadata.  
   **Interpretation:** identify whether a certificate was presented and where handshake terminated.  
   **Mitigation:** repair listener/Secret and supported TLS configuration.  
   **Prevention:** test the exact controller/version before rollout.

3. **Symptom:** TLS succeeds but HTTP route fails.  
   **Hypothesis:** host/path rule, route attachment, Service port, or ready endpoints are wrong.  
   **Evidence:** inspect Ingress/Gateway, Service, EndpointSlices, and application logs.  
   **Mitigation:** fix route/backend references.  
   **Prevention:** maintain a separate route test after TLS tests.

### B2. `curl` reports hostname or trust failure

- **Hypothesis:** SAN mismatch, wrong CA trust bundle, incomplete chain, expiry/not-yet-valid certificate, or client clock skew.
- **Evidence:** `openssl x509 -text`, `openssl s_client -servername`, `curl -v --cacert`, and system clock inspection.
- **Interpretation:** distinguish hostname identity failure from path/trust failure and validity-window failure.
- **Safe mitigation:** request the intended hostname, correct SAN/chain/trust distribution, or repair time synchronization. Do not disable verification as a fix.
- **Prevention:** CI tests for SANs and trust; monitor expiry; keep trust distribution owned.

### B3. Served certificate differs from Secret

- **Hypothesis:** controller did not reload, endpoint routes to another replica/controller, Ingress references another Secret, or the request hits a different port.
- **Evidence:** compare Secret leaf metadata/fingerprint with `openssl s_client` output; inspect Ingress namespace and `secretName`; enumerate controller replicas and endpoints; read controller logs.
- **Interpretation:** Secret update and serving-plane convergence are separate events.
- **Safe mitigation:** follow the selected controller's documented reload/restart procedure after evaluating availability; confirm each endpoint after change.
- **Prevention:** external served-certificate probe and post-renewal test.

### B4. `Certificate` is not Ready

- **Hypothesis:** issuer missing/not Ready, invalid spec, missing CA Secret, RBAC issue, webhook/CRD issue, or issuer-specific challenge failure.
- **Evidence:** `kubectl describe certificate`, issuer status, CertificateRequest, events and controller logs; inspect Order/Challenge only for ACME.
- **Interpretation:** identify the first failed reconciliation edge rather than repeatedly reapplying the same manifest.
- **Safe mitigation:** repair the documented cause and wait for observed reconciliation; do not delete CRDs.
- **Prevention:** readiness alert and version-verified manifests.

### B5. Renewal is overdue or repeatedly fails

- **Hypothesis:** issuer credentials expired, challenge cannot complete, renewal settings invalid, controller unavailable, or no alerting on failure.
- **Evidence:** inspect Certificate lifecycle/status, issuer readiness, ACME resources where applicable, controller logs, and expiry metadata.
- **Interpretation:** compare remaining certificate lifetime with actual recovery time.
- **Safe mitigation:** restore issuer/challenge access or use approved emergency issuance and reload procedure.
- **Prevention:** test renewal in a throwaway cluster, assign owner, alert on failure and remaining lifetime.

### B6. Issuer/ClusterIssuer is not Ready or deleted

- **Hypothesis:** missing CA Secret, invalid issuer configuration, insufficient permissions, deleted resource, or external issuer dependency failure.
- **Evidence:** `kubectl get/describe issuer` or `clusterissuer`, Secret metadata without contents, events, controller logs and RBAC review.
- **Interpretation:** an existing leaf can remain served while future issuance is broken.
- **Safe mitigation:** restore the reviewed issuer configuration and validate a new issuance/reconciliation.
- **Prevention:** protect issuer changes, monitor readiness/existence, and inventory dependencies.

### B7. CA rotation or cert-manager upgrade causes an incident

- **Hypothesis:** new trust not distributed, old trust removed early, leaf rollout incomplete, CRD/webhook skew, or consumer reload failure.
- **Evidence:** client trust test, served certificate fingerprint, Certificate status, CRD schema/version, controller/webhook logs, release notes.
- **Interpretation:** determine whether failure is issuance, trust, serving, or API compatibility.
- **Safe mitigation:** restore the last known-good compatible state or reinstate overlap trust using the documented rollback plan.
- **Prevention:** staged rollout, throwaway-cluster upgrade tests, rollback criteria, inventory and evidence.

## Appendix C — Claim register

Confidence reflects the technical claim as framed, not proof that the learner's particular cluster behaves this way. The status `VERIFY` means current documentation or runtime confirmation remains outstanding.

| ID | Section | Claim | Source document / section | Confidence | Status tag | Follow-up verification |
|---|---|---|---|---|---|---|
| C01 | 6.2–6.3 | TLS provides confidentiality/integrity and server authentication when validation succeeds; it is not authorization | TLS protocol standards; Kubernetes security guidance | High | General protocol concept | Validate client behavior for the chosen stack |
| C02 | 6.2–6.3 | SAN/hostname verification and trust-anchor validation are distinct checks | OpenSSL verification docs; TLS standards | High | General protocol concept | Run correct/wrong hostname and CA tests |
| C03 | 6.4 | TLS Secret uses type `kubernetes.io/tls` with `tls.crt` and `tls.key` convention | Kubernetes Secret documentation | High | General Kubernetes convention | Validate actual Secret type without printing data |
| C04 | 6.4 | Ingress TLS Secret attachment is namespace-sensitive and controller behavior matters | Kubernetes Ingress docs; selected controller docs | Medium | VERIFY | Check current docs and actual controller behavior |
| C05 | 6.4 | cert-manager `Issuer` is namespaced and `ClusterIssuer` is cluster-scoped | cert-manager API documentation | High | VERIFY current API docs | Confirm installed CRDs/API reference |
| C06 | 6.4 | Certificate workflow produces a Secret and supporting request resources | cert-manager Certificate documentation | High | VERSION-SENSITIVE | Confirm current state flow and status behavior |
| C07 | 6.4 | ACME Order/Challenge resources apply to ACME issuance, not every issuer | cert-manager ACME docs | High | VERIFY current docs | Inspect release-specific ACME docs |
| C08 | 6.4 | Exact install route, supported versions, and CRD update process are release-sensitive | cert-manager installation/upgrade docs | High | VERIFY | Select release and follow official install page |
| C09 | 6.4–6.5 | `duration`, `renewBefore`, and `rotationPolicy` behavior must be checked for installed release | cert-manager Certificate API and renewal docs | High | VERIFY | Confirm field constraints/defaults and key rotation semantics |
| C10 | 6.5 | Wildcard public ACME certificates use DNS-01 in the standard public workflow | ACME/cert-manager documentation | High | VERIFY current CA details | Confirm selected CA's current identifier/challenge rules |
| C11 | 6.5 | Public ACME rate limits vary and can change | Selected ACME CA documentation | High | VERIFY | Consult official current rate-limit page; no number asserted |
| C12 | 6.5 | Candidate expiry metric name is `certmanager_certificate_expiration_timestamp_seconds` | cert-manager metrics documentation | Medium | VERIFY | Confirm metric, labels and semantics for selected release |
| C13 | 6.5 | Kubernetes Secret base64 representation is not itself encryption at rest | Kubernetes Secrets/security docs | High | General security concept | Verify etcd encryption and RBAC in actual cluster |
| C14 | 6.6 | Issuer deletion may break future renewal without immediately invalidating an already-issued leaf | Certificate lifecycle reasoning; cert-manager docs | High | General operational inference | Demonstrate in throwaway cluster |
| C15 | 6.6 | Controller reload behavior is implementation-specific and must be tested on served endpoint | Selected controller docs and runtime test | High | VERIFY per controller | Compare Secret and endpoint fingerprints |
| C16 | 6.6 | CA rotation should overlap old/new trust during migration when supported | PKI operational practice | High | Engineering recommendation | Test clients and rollback constraints |
| C17 | 6.5 | Current cipher/algorithm choices require current Mozilla/NIST guidance | Mozilla TLS guidance; NIST publications | High | VERIFY current guidance | Review published current recommendations |
| C18 | 6.5 | Revocation behavior varies by client and deployment | PKI/client implementation documentation | High | Implementation-dependent | Validate actual client revocation behavior |
| C19 | 6.10 | Local `kind` and WSL2 do not reproduce all cloud LB/network behavior | kind/Kubernetes/WSL2 platform docs | High | Environment caveat | Record local port mapping and environment |
| C20 | Appendix A | `kubectl --dry-run=server` needs API server schema/CRDs and applicable admission behavior | Kubernetes API validation docs | High | Environment-dependent | Run only after CRDs/webhooks are ready |
| C21 | 6.4 | OpenSSL `-addext` availability can depend on installed version | OpenSSL command docs | Medium | VERSION-SENSITIVE | Check `openssl version` and local manual |
| C22 | 6.5 | trust-manager and external issuer integrations are separate products with their own support matrices | Official project/vendor docs | Medium | VERIFY | Check current compatibility and API docs |

## Appendix D — Ten-pass audit and correction log

This is a self-audit only, not an independent external review.

| Pass | Result | Checks performed | Issues / corrections | Unresolved risks |
|---|---|---|---|---|
| 1. Completeness | PASS WITH LIMITATIONS | Exact title, sections 6.0–6.14, Appendices A–E, four labs and mandatory local-CA flow present | Added incident runbooks, evidence and sign-off checklist | Runtime execution remains outstanding |
| 2. Technical correctness | PASS WITH LIMITATIONS | Separated issuance, trust, identity, encryption and authorization; explained served-cert checks | Avoided claiming all controllers reload identically | Confirm behavior against selected controller and cert-manager release |
| 3. Manifest consistency | PASS WITH LIMITATIONS | Certificate, Issuer, Secret and Ingress references use consistent `ml-demo`, `model-api.local`, `model-api-tls` | Explicitly marked Ingress/controller setup as dependent on prior unit | Manifests not server-validated; bootstrap schema needs installed CRDs |
| 4. Executability | PASS WITH LIMITATIONS | Ordered local commands, context guards, representative outputs, cleanup, dry-run distinctions included | Added warnings and refused literal version placeholder execution | Labs not executed; port mapping and Service availability vary |
| 5. Currency | PASS WITH LIMITATIONS | Version-sensitive install, metrics, renewal trigger, key rotation, Gateway behavior tagged | Removed fabricated release numbers, metric assertions, and renewal magic annotation | Official current docs not live-consulted |
| 6. Security | PASS WITH LIMITATIONS | No private-key bytes, no public domain/account, no insecure bypass as fix, RBAC/etcd risks included | Added key exposure and issuer tenancy response | Human must inspect generated evidence and repository status |
| 7. Fabrication scan | PASS WITH LIMITATIONS | Scanned for versions, API fields, flags, metrics, rates, timings and claims of execution | Used placeholders and `[VERIFY]` where unconfirmed | Some generally known API semantics still need release-specific confirmation |
| 8. Pedagogy | PASS | Progression from handshake to lifecycle incidents; diagrams, tables, self-check explanations | Added symptom/hypothesis/evidence/correction mapping | Learner should adapt to actual controller |
| 9. SRE/operations | PASS WITH LIMITATIONS | Expiry/renewal indicators, owner, runbooks, CA rotation, rollback, incident evidence included | Distinguished object status from endpoint freshness | Alert rules intentionally not asserted without metric verification |
| 10. Adversarial/scope review | PASS WITH LIMITATIONS | Checked key leakage, trust bypass, cleanup, issuer deletion nuance and module boundaries | Avoided CRD deletion as routine cleanup; scoped destructive actions to throwaway lab | Human review and real `kind` execution required |

## Appendix E — Human verification checklist and sign-off

Before using this lesson as an executable runbook:

- [ ] Confirm the exact destination is `Stage 2E — Production DevOps & Platform Engineering/04-Kubernetes-Networking-Ingress-and-Service-Mesh/06-tls-termination-and-certificate-lifecycle-with-cert-manager.md`.
- [ ] Read the current official cert-manager installation instructions; verify release, Kubernetes compatibility, install URL/route, CRDs and webhook readiness.
- [ ] Inspect all manifests against the installed CRDs and use server-side dry-run only when prerequisites are available.
- [ ] Verify the chosen Ingress/Gateway controller's TLS attachment, `IngressClass`/listener configuration, local port mapping and reload behavior.
- [ ] Verify renewal trigger and minimum-duration constraints for the exact cert-manager release before attempting early renewal.
- [ ] Verify certificate metric names, labels and semantics before deploying alert rules.
- [ ] Execute all mutations only in the named throwaway cluster and confirm the current context before each mutation.
- [ ] Run the mandatory local-CA/cert-manager lab; compare Secret metadata with the certificate served by the actual endpoint before and after renewal.
- [ ] Test issuer failure and recovery; confirm the existing leaf may continue serving while new issuance fails.
- [ ] Confirm no private keys, raw Secret YAML, tokens or sensitive logs were committed.
- [ ] Verify cleanup of resources, port-forwards, temporary crypto material and throwaway contexts/clusters.
- [ ] Record unresolved issues and do not mark a lab passed without observed evidence.

**Sign-off**

- Reviewer: ______________________________
- Date: __________________________________
- Environment / OS / WSL2 details: ______________________________
- Kubernetes / kind / cert-manager / controller versions: ______________________________
- Result: ______________________________
- Open verification items: ______________________________
- Human review completed: Yes / No

**Content status:** `DRAFT-AUDITED`  
**Audit type:** AI self-audit; not an independent external audit  
**Runtime status:** Reasoned review only; commands and labs were not executed in this environment.  
**Unverified items count:** 8 grouped items in Section 6.14; resolve them against current official documentation and actual local execution before treating this as a production runbook.
