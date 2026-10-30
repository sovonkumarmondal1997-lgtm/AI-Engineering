## Unit 4 — Image signing and deployment verification

**Target file:** `04-image-signing-and-deployment-verification.md` | **Module:** M12 | **Stage:** 2E  
**Estimated study time:** 10–14 hours, including labs and review | **Prerequisites:** M01–M11 and M12 Units 1–3  
**Core tools:** local container registry from M01, cosign, container tooling, Python 3, shell test harness  
**Awareness/optional:** keyless Sigstore, private Sigstore, ORAS, policy-controller/Ratify, Notation/Notary v2  
**Last reviewed:** 2026-10-29 | **Tool/spec baseline:** Current official documentation was checked for the cosign signing, verification, and in-toto attestation examples linked in §4.14. Exact installed versions, registry behavior, and some flags remain `[VERIFY]`; record actual local versions in `versions.txt`.  
**Footprint:** Target no more than the existing M01 local registry plus one small lab image and local scripts; measure with `docker system df`, `docker images`, and the operating system’s disk/memory tools. Keep at least 30 GB free before pulling images.  
**Internet:** Internet is needed to install/pull tools and images and to consult current documentation. Core policy tests use local fixture data and can run offline after prerequisites are cached. Registry-backed cosign operations require the local registry to be running; fully air-gapped behavior depends on the chosen cosign/registry combination and must be tested.

### 4.0 Why this matters in production

Signing and verification answer a narrow but critical question: **does this exact artifact digest have a signature accepted by our configured trust policy?** A tag such as `service:release` is a mutable name and can later refer to different bytes, so a release must be identified and promoted by immutable digest. Registry write access alone does not establish trust: an actor who can push content may also attempt to publish misleading signature material, which is why the verifier must pin the expected key or identity and validate the subject digest. A valid signature is not a safety certificate; a compromised builder can produce a harmful image and still sign it with an accepted identity. The production chain is therefore build → capture digest → sign → attach evidence attestations → verify signer, subject, and policy → promote/deploy by digest → retain evidence. This unit consumes the SBOM produced in Unit 3, relies on trusted builder and short-lived CI identity controls in Unit 5, hands admission enforcement to Unit 8, provenance interpretation to Unit 10, and reuses M08 GitOps promotion-by-digest.

### 4.1 Learning objectives

By the end, the learner can:

1. **[L1]** Explain the difference between a content digest, a cryptographic signature, an attestation, an SBOM, a vulnerability scan, and build provenance.
2. **[L1]** State exactly what successful signature verification proves and list at least four claims it does not prove.
3. **[L1]** Explain key-based and keyless signing, including identity binding and the role of transparency evidence.
4. **[L2]** Generate a throwaway key pair, sign a digest in the M01 local registry, and verify it with the expected public key.
5. **[L2]** Demonstrate why moving a tag does not transfer the original signature to the new digest.
6. **[L2]** Attach SBOM, scan-summary, and test-report attestations and check their subject digest against the image being promoted.
7. **[L2]** Implement a local promotion gate with positive and negative tests for missing signatures, wrong signers, missing evidence, subject mismatch, and a policy-denied scan result.
8. **[L3]** Design a trust model that includes the builder, signer, registry, identity issuer, transparency log, verifier, and policy owner.
9. **[L3]** Evaluate narrow identity pinning, freshness, replay/rollback, multi-role approval, offline verification, and registry portability trade-offs.
10. **[L4]** Run a key-rotation and signing-outage exercise; define auditable exception handling and operational metrics without treating coverage as proof of safety.

### 4.2 Concept map and vocabulary

### Glossary

| Term | Precise definition | Common misconception |
|---|---|---|
| Digest | A content-derived identifier, commonly represented as algorithm plus hash, for a specific manifest or byte sequence. | A digest proves who produced the content. |
| Cryptographic hash | A deterministic function mapping input bytes to a fixed-size digest with security properties such as collision resistance. | A hash is a secret or an authentication mechanism. |
| Signature | A cryptographic value created with a private key and checked with a corresponding public key over defined content or claims. | Any valid signature means the artifact is safe. |
| Private/public key | A paired asymmetric key: the private part signs; the public part verifies. | The public key must be secret. |
| Signer | The key holder or identity that signs an artifact statement. | The registry account that pushed an image is automatically the trusted signer. |
| Verifier | Software that checks signature material and applies configured trust rules. | Verifying only that *some* signature exists is sufficient. |
| Trust root | A key, certificate authority, or other configured anchor from which trust decisions are derived. | A trust root removes the need to review policy. |
| Key-based signing | Signing with a managed private key and verifying against the corresponding trusted public key or key reference. | A local key file is production-grade key management. |
| Keyless signing | Signing through a short-lived identity-bound credential/certificate flow, typically tied to an OpenID Connect (OIDC) identity and transparency evidence. | “Keyless” means no cryptographic key is used at all. |
| OIDC identity | An identity assertion issued through OpenID Connect; trust depends on issuer, subject and policy context. | Any account at a trusted issuer should be allowed to sign production. |
| Short-lived certificate | A certificate with a limited validity interval, often binding an ephemeral public key to an authenticated identity. | Short lifetime alone prevents misuse during its validity. |
| Transparency log | An append-oriented public or private record of signing-related events that can make unexpected events detectable. | A log guarantees the signer or artifact is trustworthy. |
| Fulcio | Sigstore’s certificate authority component for issuing signing certificates in its identity-based flow. | Fulcio scans artifacts for malware. |
| Rekor | Sigstore’s transparency-log component for recording signing-related evidence. | A Rekor entry is a security approval. |
| TUF | The Update Framework, a framework for securely distributing and updating trusted metadata. | TUF is itself the image signature. |
| Attestation | A signed statement describing an artifact or process, such as test results, SBOM, scan outcome, or provenance. | An attestation is true merely because it is signed. |
| Predicate | The domain-specific payload in an attestation that states the claim being made. | Every predicate schema is interchangeable. |
| in-toto Statement | A standardized statement model that connects a subject to a predicate and its type. | Any JSON object is automatically a valid in-toto statement. |
| DSSE envelope | A signing envelope format that signs typed payload bytes in a structured way. | DSSE alone validates the meaning or quality of a predicate. |
| Subject digest | The digest identifying the artifact an attestation or signature claim refers to. | A nearby filename is enough to bind evidence to an artifact. |
| Registry artifact/referrer | Registry-stored content that can refer to another artifact, depending on registry and client support. | All registries store and copy signatures identically. |
| Identity pinning | A verification rule that accepts only a specifically expected identity and issuer, not any signer. | An issuer-only check is equivalent to a precise identity constraint. |
| Key rotation | Replacing a signing key and deliberately changing verifier trust to transition from old to new keys. | Generating a new key automatically invalidates old trust. |
| Revocation | A policy or trust action that rejects a credential/key or its signatures according to a defined mechanism. | Removing a key file from one machine revokes every copy of that key. |
| Freshness | A policy about how recent evidence must be relative to a defined event or evaluation time. | A recent signature means a recent vulnerability scan. |
| Replay/rollback | Reusing an older, previously valid artifact or evidence set after policy or risk has changed. | A valid old signature means the old artifact remains acceptable. |
| TOCTOU | Time-of-check to time-of-use gap: the object checked may differ from the object ultimately used. | A CI check alone guarantees the runtime image matches. |
| Verification policy | Rules specifying accepted signers, subjects, required attestations, evidence freshness, and decision behavior. | Policy is just a list of trusted public keys. |
| Promotion gate | A control that refuses to promote an artifact unless required verification and policy checks pass. | A gate is effective even if it can be bypassed without audit. |
| Admission control | A Kubernetes API request control that can validate whether a workload is allowed to be created or changed. | CI verification alone guarantees all cluster workloads comply. |
| Break-glass procedure | A narrow, time-limited, approved, logged emergency process when the standard control path is unavailable. | Emergency means unlogged bypass is acceptable. |

### Supply-chain path and control placement

```text
Source + reviewed ref
        |
        v
Trusted build system / builder  <---- Unit 5: isolation and short-lived CI identity
        |
        v
Image manifest + immutable digest
        |                  \
        |                   \--> Unit 3 SBOM + Unit 2 scan result + tests
        v
Registry <---- sign digest + attach signed attestations
        |
        v
Verify expected signer + subject digest + evidence policy
        |
        v
M08 promotion by digest ----> Unit 8/11 admission policy (later units)
        |
        v
Running workload / model loader
        |
        v
Audit evidence + freshness/revocation review + M11 telemetry
```

| Control | Main question answered | Does not establish |
|---|---|---|
| Digest | Are these the same identified bytes/manifest? | Who produced them or whether they are safe. |
| Signature | Did an accepted key/identity sign the claim for this digest? | That the builder was uncompromised or the code is benign. |
| SBOM | Which components does this inventory report? | Complete inventory, absence of vulnerabilities, or provenance by itself. |
| Scan result | What did this scanner/database/policy report at a point in time? | Current risk forever or completeness of detection. |
| Provenance attestation | What build process/source/materials does the attestation claim? | Truth if the builder or attester is compromised. |
| Test attestation | What tests/results are asserted for the subject? | That tests are sufficient or representative. |
| Verification policy | Does this evidence set satisfy our declared acceptance rules? | Correctness of the policy or trustworthiness of every upstream system. |

### Key-based versus keyless signing

| Dimension | Key-based | Keyless identity-based |
|---|---|---|
| Trust anchor | Explicit public key or key reference configured by the verifier. | Accepted identity, issuer, trust roots, and the selected Sigstore verification model. |
| Key custody | Long-lived or managed key material must be protected, backed up, rotated, and retired. | Ephemeral signing key is used with a short-lived identity-bound certificate in the typical Sigstore model. |
| Identity binding | Often indirect: policy maps the public key to a role/team. | Identity claims are checked against verifier policy; issuer and subject constraints matter. |
| Online requirements | Registry access is needed for registry-backed signatures; local public-key verification can reduce external trust dependencies. | Issuance/transparency dependencies may be required during signing; offline verification depends on retained evidence/bundles and exact tool support. |
| Rotation | Explicit public-key trust update and retirement process. | Identity/issuer policy and trust-root/certificate semantics must be maintained; key lifetime is shorter but policy remains important. |
| Strength | Clear, portable trust anchor; useful for local/offline or controlled environments. | Can reduce long-lived private-key handling and bind signing to an authenticated workload/person identity. |
| Limitation | Key theft or broad key sharing can blur accountability. | Identity misconfiguration, overly broad matching, and infrastructure dependence can undermine trust. |
| Suitable use | This unit’s hands-on lab, isolated systems, or controlled release keys. | CI identity-based signing when the issuer/workflow identity can be constrained and verified. |

The practical course path uses **key-based signing** with throwaway keys. Public Sigstore keyless infrastructure is awareness-level here; do not improvise a local certificate authority or OIDC system and call it equivalent to production.

### Digest pinning and the exact signature claim

A tag is a human-readable pointer. It can be reassigned. If `registry.example/team/api:release` points to digest `sha256:AAA...` today and `sha256:BBB...` tomorrow, a signature for `AAA` does not automatically authenticate `BBB`. Promotion and deployment records should carry the full image reference with digest, and the verifier must verify that digest.

A successful key-based check supports this narrow claim: **the private key corresponding to the public key supplied to the verifier signed the relevant claim for the subject digest, and the signature checks under the tool’s verification rules.** The policy owner must separately decide whether that public key is trusted for this repository, environment, source ref, and release purpose. It does not prove build isolation, source review, scan freshness, absence of malicious code, deployment correctness, or that the same digest is still running.

### Sigstore, in-toto, and DSSE

In the common Sigstore keyless model, an authenticated OIDC identity is used to obtain a short-lived signing certificate from Fulcio; signing-related evidence is recorded in Rekor; trusted metadata/root distribution is part of the wider trust model, including TUF. The precise workflow and offline evidence requirements are version-sensitive. Verify current documentation for the installed cosign version and do not assume all registries or local environments behave identically.

An attestation adds a structured claim to a signature. in-toto Statement provides a standard subject-and-predicate model; DSSE provides a signing envelope for payloads. The signature authenticates the signed payload bytes under the relevant trust model; a policy engine still has to validate predicate meaning, subject digest, signer, source, freshness, and acceptable results. Do not invent or copy fields from a different predicate type. Custom JSON examples in this module are explicitly `[ILLUSTRATIVE]`, not standardized predicate schemas.

### 4.3 Level 1 — Beginner

#### 4.3.1 The production problem

A release is not just “the image with the expected tag.” It is a particular artifact built from a source revision by a particular process and approved under a particular policy. Common failure paths include:

- a mutable tag moves after review;
- an attacker with registry write access pushes a replacement;
- an image is signed by a key that is valid but not trusted for production;
- a signature refers to digest A while deployment uses digest B;
- a scan report is attached but stale or about another image;
- a builder is compromised and signs the output it produced;
- a verifier accepts any signature rather than the expected signer.

Signing helps with identity and integrity; it must be combined with provenance, scanning, test evidence, least privilege, and enforcement.

#### 4.3.2 Hash → sign → verify

1. Build or select an artifact and calculate its digest.
2. Sign the digest-related artifact claim with a private key.
3. The verifier uses the corresponding public key to check the signature.
4. The policy then asks whether that key is authorized for this artifact and environment.

A hash is not secret. A signature is not encryption. If an attacker changes the content, its digest changes with overwhelming probability under a secure hash function; a signature over the old content does not validate the changed content. But if the trusted builder itself is compromised, it may produce and sign malicious content. The trust boundary includes the builder and signing authorization, not just the signature algorithm.

#### 4.3.3 Beginner walkthrough: local key-based signing

Use the M01 registry and a small image already available locally. The example uses placeholders so that it does not assume a registry name, authentication mode, or runtime that was not confirmed in your environment.

```bash
# Record tool versions before the lab.
cosign version
docker version
docker info

# Generate a throwaway key pair interactively.
# cosign prompts for a password; use a unique lab-only password.
# Run from a disposable workspace, not from the repository.
mkdir -p "$HOME/m12-unit4-lab"
chmod 700 "$HOME/m12-unit4-lab"
cd "$HOME/m12-unit4-lab"
cosign generate-key-pair
```

The generated files are commonly named `cosign.key` and `cosign.pub`; confirm actual output for your installed version. Keep the private key outside the repository and do not print or paste it. Use the local registry path from M01 and push a harmless lab image.

```bash
# Replace these placeholders with the actual M01 registry/image.
export IMAGE_TAG='localhost:5000/m12-lab/signing-demo:unit4'
# Build/push using the container runtime and registry steps already taught in M01.
# Capture the registry's authoritative digest after push; do not invent one.
export IMAGE_DIGEST='localhost:5000/m12-lab/signing-demo@sha256:REPLACE_WITH_REAL_DIGEST'

# Sign the immutable digest, not the mutable tag.
cosign sign --key cosign.key "$IMAGE_DIGEST"

# Verify against the expected public key and same digest.
cosign verify --key cosign.pub "$IMAGE_DIGEST"
```

**Important:** `IMAGE_DIGEST` is intentionally a placeholder. Do not run the verification command until you replace it with the exact digest reported for your image. Confirm the command syntax against `cosign sign --help` and `cosign verify --help` for the installed release. The current official Sigstore docs show key generation, key-based image signing, and verification by image reference; registry storage details remain implementation-sensitive.

**Illustrative evidence, not command output:** the positive case should return verification evidence for the exact digest under the supplied public key. If verification fails, inspect the image reference, key path/password, registry connectivity/authentication, signature retrieval, and whether the digest is the one signed. Do not interpret a failure as proof that the image is malicious; it means the required verification did not succeed.

#### 4.3.4 Attestation concepts

An attestation is a signed statement about an artifact, such as “this SBOM was generated,” “this test suite passed,” or “this scan had no findings that violate this lab policy.” It has at least three distinct checks:

1. **Cryptographic:** is the attestation signed by an accepted signer?
2. **Binding:** does its subject refer to the exact digest under review?
3. **Semantic/policy:** does the claim use an expected predicate and satisfy the rule?

A signature on an attestation does not mean the statement is true. Trust depends on who produced it, how the claim was generated, whether the process is protected, and whether the verifier understands the predicate.

#### 4.3.5 Common beginner mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Sign only a tag | Later deployment resolves to a different digest. | Capture and promote by immutable digest. |
| Verify with an arbitrary public key | Verification passes, but signer is not authorized. | Pin the expected key or exact identity and issuer in policy. |
| Check only that a signature exists | Wrong signer or wrong digest can pass a weak check. | Verify expected signer, subject digest, and policy. |
| Treat signature as a scan | Known vulnerable artifact can still be signed. | Keep scan and freshness requirements separate. |
| Store private key in Git | Key is exposed to repository readers/history. | Keep it outside the repository; rotate immediately if exposed. |
| Ignore registry behavior | Signature cannot be found after copying the image. | Test the chosen registry’s signature/referrer support and copy behavior. |
| Accept old signed artifacts forever | Previously approved but now-denied digest can be replayed. | Apply freshness/deny-list and rollback policy. |

### 4.4 Level 2 — Intermediate

#### 4.4.1 Lab workspace and safety boundaries

Use a dedicated disposable directory, for example:

```text
$HOME/m12-unit4-lab/
├── versions.txt
├── evidence/
│   ├── image-digest.txt
│   ├── verify-positive.txt
│   ├── verify-negative.txt
│   ├── tag-mutation-report.md
│   ├── attestations/
│   │   ├── sbom-predicate.json
│   │   ├── scan-predicate.json
│   │   └── test-predicate.json
│   ├── policy/
│   │   ├── policy.json
│   │   └── fixtures/
│   └── audit/
├── scripts/
│   └── promotion_gate.py
└── keys/                 # disposable; never copy into repository
    ├── cosign.key
    └── cosign.pub
```

Keep the private key under `keys/` only for the lab, set restrictive directory permissions, and delete it during cleanup. Do not use a production key, real identity, production registry, or real sensitive data. Do not put password material into command history or the evidence directory. Use the interactive password prompt supported by the selected version, and inspect `cosign generate-key-pair --help` before scripting any noninteractive password mechanism.

Prerequisites: M01 local registry and a small harmless image; Python 3; cosign; container CLI; enough disk space for the image and generated evidence. Measure footprint before and after with `docker system df` (or the equivalent runtime command). Registry-backed operations may need network access to the local registry but not to a public service when using key-based signing. Download and cache tools/images before an offline session.

WSL2 caveat: ensure the registry endpoint is reachable from the shell that runs cosign. `localhost` may resolve differently between Windows, WSL2, containers, and Docker Desktop. Use the exact endpoint that worked in M01. Native Linux has fewer cross-boundary networking surprises, but firewall and loopback settings still matter.

#### 4.4.2 Push and capture the digest

Use the M01 image-build and registry workflow. Do not repeat image-building mechanics here. Capture the digest from the registry/runtime’s authoritative push or inspect output. Store a complete reference in `evidence/image-digest.txt`, for example:

```text
[ILLUSTRATIVE — not a real digest]
localhost:5000/m12-lab/signing-demo@sha256:0123456789abcdef...replace-with-full-digest...
```

Never truncate the digest in executable configuration. If the registry does not expose a usable digest in the command you use, query the registry or image tool in a way verified for your installed version and record the exact command in `versions.txt`.

#### 4.4.3 Sign and verify the digest

```bash
# In the disposable workspace; confirm actual names from cosign output.
mkdir -p keys evidence
chmod 700 keys
cd keys
cosign generate-key-pair
# Move the generated files into this directory if they were written elsewhere.
# Never overwrite a key without confirming which one is being used.
cd ..

# IMAGE_DIGEST must contain the full, real digest reference.
cosign sign --key keys/cosign.key "$IMAGE_DIGEST"
cosign verify --key keys/cosign.pub "$IMAGE_DIGEST" > evidence/verify-positive.txt
```

The password prompt is expected for an encrypted private key. Do not disable encryption for convenience. If the installed version or environment uses a different key-file flow, follow its official help and record the exact verified commands. These examples have been checked against current Sigstore documentation, but are **not execution-verified in your local environment**.

Negative tests:

- Verify an unsigned digest: it must not be accepted by the promotion gate.
- Verify with a different throwaway public key: the signature check must fail.
- Verify a different digest: it must not be accepted as the previously signed artifact.
- Attempt to use the tag as deployment input: the gate should reject it when policy requires a digest reference.

A command failure can have multiple causes (auth, missing signature, registry incompatibility, incorrect digest). Record the exact error and classify it; do not treat every failure as a successful security test until the expected failure reason is confirmed.

#### 4.4.4 Attestation examples

The following custom predicates are `[ILLUSTRATIVE]` training fixtures, not standardized SBOM, vulnerability, test, or provenance schemas. Reuse the real SBOM generated in Unit 3 as an input; do not fabricate a claim that a scan actually ran. Bind every statement to the exact subject digest and record the signer that produced it.

Example scan summary fixture:

```json
{
  "_comment": "ILLUSTRATIVE local policy fixture; not a standardized predicate",
  "subject_digest": "sha256:REPLACE_WITH_FULL_DIGEST",
  "scanner": "REPLACE_WITH_ACTUAL_TOOL_AND_VERSION",
  "database_updated_at": "REPLACE_WITH_ACTUAL_TIMESTAMP_OR_UNKNOWN",
  "critical_fixable_findings": 0,
  "result_source": "local-lab-evidence"
}
```

Example test report fixture:

```json
{
  "_comment": "ILLUSTRATIVE local policy fixture; not a standardized predicate",
  "subject_digest": "sha256:REPLACE_WITH_FULL_DIGEST",
  "test_suite": "release-smoke-tests",
  "result": "pass",
  "run_id": "local-lab-run-001"
}
```

For a current cosign version that supports the documented command form, a local key-based attestation workflow is:

```bash
# Check `cosign attest --help` first; this is a version-sensitive interface.
cosign attest --key keys/cosign.key --predicate evidence/attestations/scan-predicate.json --type custom "$IMAGE_DIGEST"
cosign verify-attestation --key keys/cosign.pub "$IMAGE_DIGEST"
```

Repeat for the SBOM predicate and test-report predicate, using a suitable predicate type and valid schema for the chosen tool version. The official docs document `cosign attest --predicate ... --key ...` and `cosign verify-attestation --key ...`; predicate type/schema choices and output encoding must be verified. Do not infer that a command succeeded just because it appears in this file.

#### 4.4.5 A local policy checker with positive and negative tests

This offline checker is intentionally separate from cosign. It evaluates a normalized JSON evidence record **after** cryptographic verification and predicate parsing have been performed by the selected toolchain. It does not verify cryptographic signatures, registry objects, certificate identity, or an actual scanner result. This separation avoids pretending that a simple Python script can replace cosign.

Save as `scripts/promotion_gate.py`:

```python
#!/usr/bin/env python3
"""Offline policy logic for normalized lab evidence; not a signature verifier."""
import json
import sys
from pathlib import Path

REQUIRED_ATTESTATIONS = {"sbom", "scan", "test"}

def evaluate(record: dict, expected_digest: str, expected_signer: str) -> list[str]:
    errors = []
    if not record.get("signature_verified"):
        errors.append("signature_not_verified")
    if record.get("signer") != expected_signer:
        errors.append("unexpected_signer")
    if record.get("subject_digest") != expected_digest:
        errors.append("subject_digest_mismatch")

    attestations = record.get("attestations", {})
    missing = REQUIRED_ATTESTATIONS - set(attestations)
    if missing:
        errors.append("missing_attestations:" + ",".join(sorted(missing)))

    for name, att in attestations.items():
        if att.get("subject_digest") != expected_digest:
            errors.append(f"{name}_subject_digest_mismatch")
        if not att.get("verified"):
            errors.append(f"{name}_signature_not_verified")
        if att.get("stale") is True:
            errors.append(f"{name}_stale")

    scan = attestations.get("scan", {})
    # Lab rule, not a universal severity policy.
    if scan.get("critical_fixable_findings", 0) > 0:
        errors.append("critical_fixable_findings")
    if scan.get("policy_result") not in (None, "pass"):
        errors.append("scan_policy_failed")

    return errors

def main() -> int:
    if len(sys.argv) != 4:
        print("usage: promotion_gate.py RECORD.json EXPECTED_DIGEST EXPECTED_SIGNER", file=sys.stderr)
        return 2
    record_path = Path(sys.argv[1])
    record = json.loads(record_path.read_text(encoding="utf-8"))
    errors = evaluate(record, sys.argv[2], sys.argv[3])
    if errors:
        print(json.dumps({"decision": "DENY", "reasons": errors}, indent=2))
        return 1
    print(json.dumps({"decision": "ALLOW", "reasons": []}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Save the following as `scripts/test_promotion_gate.py`:

```python
import unittest
from promotion_gate import evaluate

DIGEST = "sha256:abc123"
SIGNER = "unit4-lab-public-key"

def valid_record():
    return {
        "signature_verified": True,
        "signer": SIGNER,
        "subject_digest": DIGEST,
        "attestations": {
            "sbom": {"verified": True, "subject_digest": DIGEST},
            "scan": {
                "verified": True, "subject_digest": DIGEST,
                "critical_fixable_findings": 0, "policy_result": "pass"
            },
            "test": {"verified": True, "subject_digest": DIGEST}
        }
    }

class PromotionGateTests(unittest.TestCase):
    def test_valid_evidence_is_allowed(self):
        self.assertEqual(evaluate(valid_record(), DIGEST, SIGNER), [])

    def test_unsigned_image_is_denied(self):
        record = valid_record()
        record["signature_verified"] = False
        self.assertIn("signature_not_verified", evaluate(record, DIGEST, SIGNER))

    def test_wrong_signer_is_denied(self):
        self.assertIn("unexpected_signer", evaluate(valid_record(), DIGEST, "other-key"))

    def test_subject_mismatch_is_denied(self):
        record = valid_record()
        record["subject_digest"] = "sha256:other"
        self.assertIn("subject_digest_mismatch", evaluate(record, DIGEST, SIGNER))

    def test_missing_sbom_is_denied(self):
        record = valid_record()
        del record["attestations"]["sbom"]
        self.assertTrue(any(x.startswith("missing_attestations:") for x in evaluate(record, DIGEST, SIGNER)))

    def test_scan_with_critical_fixable_finding_is_denied(self):
        record = valid_record()
        record["attestations"]["scan"]["critical_fixable_findings"] = 1
        self.assertIn("critical_fixable_findings", evaluate(record, DIGEST, SIGNER))

    def test_stale_test_attestation_is_denied(self):
        record = valid_record()
        record["attestations"]["test"]["stale"] = True
        self.assertIn("test_stale", evaluate(record, DIGEST, SIGNER))

    def test_attestation_subject_mismatch_is_denied(self):
        record = valid_record()
        record["attestations"]["sbom"]["subject_digest"] = "sha256:other"
        self.assertIn("sbom_subject_digest_mismatch", evaluate(record, DIGEST, SIGNER))

if __name__ == "__main__":
    unittest.main()
```

Run the fixture-based tests from `scripts/`:

```bash
python -m unittest -v test_promotion_gate.py
```

Expected behavior (descriptive, not a claim of execution): the suite contains one positive case and seven negative cases. The positive record returns no errors; each negative record includes its expected denial reason. The checker is not a substitute for authenticating the record. In a real pipeline, the adapter that creates the normalized record must only set `signature_verified=true` after successful cosign verification and must derive signer/subject from verified evidence, not user-controlled input.

**Production improvement:** make the adapter produce a signed, immutable decision record; validate input schemas; fail closed on missing/unknown fields; define timestamp semantics and clock skew; ensure `critical_fixable_findings` comes from a trusted scan attestation; and test that a caller cannot edit the normalized JSON after verification. For this lab, treat the JSON as an offline policy-logic fixture only.

#### 4.4.6 CI promotion gate and registry permissions

The gate belongs after the trusted build/sign/attest job and before M08 promotion. It must:

1. take a full digest reference from a trusted build output;
2. verify the signature against the pinned public key or tightly constrained identity;
3. verify each required attestation and its subject digest;
4. evaluate policy using authenticated evidence;
5. write a decision record with timestamp, digest, policy version, signer/key identity, and denial reasons;
6. promote the exact digest only when policy allows it.

The CI identity allowed to sign must be distinct from arbitrary pull-request jobs. Never expose the private signing key to untrusted PR code or to build steps that can arbitrarily execute source-controlled scripts. Unit 5 develops build isolation and short-lived CI identity controls; M09 covers secret storage mechanisms. A registry role that can push arbitrary content or signature objects is not automatically a trusted signing role.

#### 4.4.7 Signing other artifact types and Kubernetes handoff

The same design question applies to Helm OCI charts, SBOM files, model artifacts, and Terraform modules: identify the exact artifact, sign it, verify the expected signer, and bind required evidence to that artifact. Commands differ by artifact type and tool/version; verify them before adapting this lab. For a model-like file, verify a cryptographic digest or supported blob signature before loading it. Never load an untrusted pickle file as a test.

Kubernetes admission enforcement is deferred to Units 8 and 11. The future admission rule must verify the actual image digest and expected signer/attestations at admission time; do not treat CI-only verification as proof that every cluster deployment complies. Kyverno `verifyImages`, Sigstore policy-controller, and Ratify are awareness-level pointers here; verify current APIs before implementation.

#### 4.4.8 Key management basics

- Generate lab keys at runtime and restrict file permissions.
- Keep private keys out of source control, build logs, and evidence bundles.
- Separate development, staging, and production signing identities.
- In production, evaluate a managed key service or hardware-backed custody where justified; do not copy a local encrypted key-file pattern into a high-assurance design without threat analysis.
- Document who can request a signature, who can approve a release, and who can change verifier policy.
- Rotate keys through a controlled trust transition, test old-key rejection, and retain only the public verification material needed for audit.
- Define emergency behavior for lost, exposed, or unavailable signing material.

### Pattern catalogue

| Pattern | Use when | Do not use when |
|---|---|---|
| Sign immutable image digest | Releasing a container image to a downstream environment. | The digest is not known or cannot be tied to the actual pushed artifact. |
| Pin one public key in a local gate | Small lab or controlled release flow with explicit key custody. | Multi-team scale requires a role/identity model that the one-key design cannot represent. |
| Require SBOM + scan + test evidence | Release risk warrants consistent component and quality evidence. | The predicate schemas and producers are untrusted or not validated. |
| Verify at promotion and admission | A release can be altered or deployed through multiple paths. | Never skip one layer merely because another exists; instead document scope and residual risk. |
| Use keyless identity pinning | CI identity is stable, constrained, and supported by the verifier. | Policy only checks issuer or uses a broad wildcard. |
| Time-limited exception with audit | A genuine incident requires a controlled temporary exception. | The exception has no owner, expiry, compensating controls, or record. |

### Anti-pattern catalogue

| Bad practice | How it fails | Corrected version |
|---|---|---|
| “Signed by anyone” policy | An untrusted key can sign an artifact and pass a presence-only check. | Pin an expected key or exact identity and issuer. |
| Tag-based deployment | Tag moves after verification. | Promote and deploy the verified digest. |
| Trust all CI identities from one issuer | A less-trusted repository/workflow may satisfy an overly broad rule. | Bind to exact issuer plus repository/workflow/ref identity where available. |
| Sign in a job that runs untrusted PR code | The job may misuse signing authority. | Separate build/test from protected signing; use Unit 5 controls. |
| Accept any attestation on the image | An unrelated or malformed predicate may satisfy a superficial check. | Validate type, schema, signer, subject digest, freshness, and policy meaning. |
| Use scan evidence indefinitely | New advisories make old results stale. | Re-evaluate current risk and enforce evidence-age policy. |
| “Break glass” without a record | Bypass cannot be audited and may become normal practice. | Require approver, reason, expiry, compensating control, and follow-up. |
| Assume signatures survive every registry copy | Storage/discovery semantics may differ. | Test portability on the actual registry pair. |

### 4.5 Level 3 — Advanced

#### 4.5.1 Trust model

Use this table during design review:

| Trust component | Security question | Failure consequence | Verification/evidence |
|---|---|---|---|
| Source repository/ref | Was the source revision reviewed and protected? | A trusted signer can sign attacker-controlled source. | Protected branch/ref policy and source commit in release evidence. |
| Builder/CI | Can untrusted code access signing authority or alter build outputs? | Malicious output can be validly signed. | Job isolation, permissions, provenance, and negative tests. |
| Signer/key | Who can request signatures and under which conditions? | Unauthorized signing or repudiation. | Access review, key-use audit, rotation drill. |
| Registry | Can content/signature evidence be replaced, deleted, or hidden? | Verification failure or misleading evidence discovery. | Registry ACL review and digest-based verification. |
| Identity issuer | Does the issuer assert the identity the policy expects? | Wrong workflow identity is trusted. | Exact issuer/subject constraints and policy tests. |
| Transparency log | Is signing evidence available and verifiable under the selected mode? | Reduced auditability or failed keyless verification. | Log/bundle evidence and documented outage behavior. |
| Trust roots | Are root metadata and key/certificate trust current? | Untrusted identity accepted or legitimate signer rejected. | Controlled trust-root updates and test vectors. |
| Verifier | Does it check the correct subject and trusted signer? | False acceptance or false rejection. | Positive/negative conformance suite and pinned tool version. |
| Policy owner | Are acceptance rules specific, reviewed, and current? | Weak rules or unsafe emergency exceptions. | Versioned policy, review approvals, exception expiry. |
| Deployment path | Does runtime use the verified digest? | TOCTOU or alternate path bypasses CI checks. | Running digest inventory and admission evidence. |

Threat modelling starts with Unit 1’s attack paths. The trust question is not “is the image signed?” but “which identity is authorized to sign which artifact from which source, using which process, and where is that enforced?”

#### 4.5.2 Identity pinning and wildcard exercise

For keyless verification, pin the expected issuer and exact identity (or a carefully scoped pattern if exact identity is not stable). Never use `.*` for production identity acceptance. Current cosign docs include identity and issuer flags, including regexp variants; the exact flag and matching behavior must be checked with the installed version’s `cosign verify --help`.

Review the following **[SYNTHETIC]** policy patterns. These are not executable policy syntax; they are a review exercise.

| # | Candidate identity rule | Assessment |
|---:|---|---|
| 1 | Exact trusted release workflow identity + exact expected issuer | Strongest of this list if the identity claim is actually emitted and policy is tested. |
| 2 | Any identity from expected issuer | Too broad; many identities may be valid at that issuer. |
| 3 | `.*` for identity and `.*` for issuer | Dangerous: effectively removes meaningful identity pinning. |
| 4 | Repository-wide identity, any workflow/ref | Broad; a low-trust workflow may sign. |
| 5 | Exact repository + protected release workflow + exact issuer | Narrower; confirm the claim format and protect the workflow definition. |
| 6 | Exact identity but no issuer constraint | Incomplete where the same subject string can arise from different issuers. |
| 7 | Trusted staging identity accepted for production | Environment separation failure. |
| 8 | Production identity accepted only for one protected branch/ref | Narrower, but ensure policy reflects the real claim and ref protection. |
| 9 | Prefix match on organization name only | Too broad for release authorization. |
| 10 | Exact service account identity but unrestricted audience/workflow context | May be insufficient; inspect issuer claims and authorization model. |

**Answer key:** #1 and #5 are the most defensible starting points in this synthetic set, subject to claim verification and workflow protection. #8 may be appropriate if its exact semantics are verified. #2, #3, #4, #6, #7, #9, and #10 need tightening or additional trust-boundary controls. Do not translate these descriptions into production regexes without testing actual certificate identity values and the matching semantics of the installed tool.

#### 4.5.3 Multiple roles and separation of duties

For higher-risk releases, separate the roles that build, test, scan, and approve. A policy may require evidence from distinct roles, but the exact implementation depends on the selected verifier/policy engine. Do not claim that a single cosign flag automatically enforces a multi-role AND policy unless the current documented tool supports that behavior. A small local wrapper can instead verify each required evidence item and fail closed, with unit tests for:

- missing builder signature;
- missing QA/test evidence;
- scan attestation from an unexpected signer;
- same identity used where policy requires independent approval;
- mismatched subject digest;
- stale scan evidence;
- unknown predicate type;
- missing policy version or decision record.

Separation of duties is only meaningful if the roles are actually independent. Two keys controlled by the same unreviewed workflow may be cryptographically distinct but operationally share the same compromise boundary.

#### 4.5.4 Freshness, TOCTOU, replay, and rollback

A signature usually remains mathematically valid even after a new vulnerability is disclosed. The policy must therefore separate signature validity from current release acceptability. A freshness rule should specify:

- which evidence type is age-limited;
- which timestamp is trusted and how it is obtained;
- how clock skew is handled;
- what happens if evidence is missing;
- who can grant an exception and for how long;
- how the system re-evaluates artifacts after new advisories.

`stale: true` in the local policy fixture is a simplified training marker, not a standard attestation field. Production freshness checks should use authenticated timestamps and well-defined evidence semantics.

**[ILLUSTRATIVE] policy:** reject an image digest if the current deny-list contains that digest or if its scan evidence exceeds the organization’s defined maximum age. A new advisory can cause an otherwise validly signed digest to be denied without changing the original signature. Do not confuse deny-listing with cryptographic signature revocation.

TOCTOU appears when CI verifies digest A but a later deployment uses a mutable tag that now resolves to digest B, or when the deployment controller fetches a different artifact than the one evaluated. The defense is to carry the verified digest through promotion and verify the actual workload image reference after deployment. Replay/rollback controls additionally need release-version policy, digest deny-lists, and approval for reverting to older releases.

#### 4.5.5 Transparency logs and offline verification

Transparency evidence can improve auditability by making signing events discoverable and harder to hide, but it does not judge whether the artifact is safe or the signer should have been authorized. Verify current Rekor and bundle semantics before implementing an offline workflow. An offline verifier needs the artifact, trusted public key or trust roots, signature and required evidence bundle, an explicit policy, and whatever authenticated log/timestamp material the selected verification mode requires. Merely copying a signature file is not enough to establish the whole trust chain.

Offline/air-gapped release should be treated as a tested architecture, not a command-line switch assumed to work. Test both the positive case and failure when a required trust root, bundle, or evidence item is missing. Record which checks are performed offline and which were performed at signing time.

#### 4.5.6 Registry portability

OCI distribution standards describe ways to discover artifacts that refer to a subject, but actual registry implementations, feature versions, authentication, retention, and copy tools can differ. Before adopting a registry migration process:

1. sign and attest an image in registry A;
2. copy the image by digest to registry B;
3. discover whether signatures/attestations were copied;
4. verify the image and all required evidence at registry B;
5. compare subject digests and policy outcomes;
6. document unsupported behavior and block promotion if required evidence is missing.

Do not assume a copied image automatically brings its referrers with it. If two registries are not available locally, use a fixture-based portability report but label it **not equivalent to a live registry test**.

#### 4.5.7 Failure analysis

| Symptom | Hypothesis | Test | Root cause/fix | Prevention |
|---|---|---|---|---|
| Signed image cannot be verified | Wrong digest, missing registry artifact, wrong key, auth failure | Compare exact reference, key, registry logs, and error | Correct the reference/permissions or restore the expected evidence; do not skip verification | Positive/negative test in release pipeline |
| New tag target fails verification | Tag now points to another digest | Resolve tag and compare digest with signed digest | Promote the original verified digest or sign/approve the new release through normal flow | Deployment by digest |
| Wrong signer accepted | Gate checks signature presence only | Verify with an untrusted throwaway key | Pin expected key/identity and test wrong-signer denial | Policy review and regression test |
| Attestation rejected | Wrong subject, unsupported predicate/schema, invalid signer, or stale evidence | Inspect verified payload and schema/version | Fix producer or policy; do not blindly disable validation | Versioned schema fixtures |
| Registry outage blocks release | Verification cannot retrieve signature/attestation | Simulate registry unavailable in a disposable environment | Delay release or use a preapproved offline evidence path if policy supports it | Availability design and contingency exercise |
| Keyless verification fails offline | Required certificate/log/root evidence unavailable | Check bundle and documented offline requirements | Use a supported evidence bundle or an approved key-based offline flow | Document online/offline trust boundaries |
| Retired key still passes | Verifier still trusts old key or cached policy | Verify old signature after cutover | Remove old key from active policy and reload/retest | Rotation test and policy version audit |
| Signing unavailable | Key service, credential, or signer path down | Test signing failure without bypassing gate | Delay release or use authorized, logged contingency | Recovery exercise and owner/expiry |
| Registry copy loses evidence | Referrers/signatures not copied or discovered | Compare `cosign tree`/tool output at source and destination where supported | Use verified copy method or reject destination | Portability test per registry pair |

### 4.6 Level 4 — Expert

#### 4.6.1 Verification policy as versioned code

A production policy should explicitly state:

- allowed registries/repositories and image digest requirements;
- trusted public keys or exact keyless issuer/identity constraints;
- which source repository/ref and builder identity are acceptable;
- required attestation types and schema/predicate versions;
- subject digest consistency across image, SBOM, scan, test, and provenance evidence;
- scan decision and evidence freshness rules;
- deny-list and rollback behavior;
- exception owner, rationale, compensating controls, expiry, and review date;
- policy version, decision timestamp, audit destination, and escalation path.

Treat these as local policy decisions, not universal specification requirements. Keep policy review separate from the code path that creates evidence. Test policy against known-good and known-bad fixtures before enforcement.

#### 4.6.2 Key-rotation drill

This drill uses throwaway lab keys only.

1. Generate key pair A and sign the lab digest.
2. Configure verifier policy to trust A; verify the signature.
3. Generate key pair B and enter a documented dual-trust window where both A and B are accepted.
4. Re-sign the same digest with B; verify with B and record both verification results.
5. Change the active policy to trust B only.
6. Verify that B succeeds and the signature made only by A is rejected under the post-cutover policy.
7. Save the policy version and test results. If the tool returns multiple signatures and the verifier checks any accepted signature, ensure the test isolates the old-key signature or use a clean lab image/reference so the old signature cannot cause a false pass.
8. Document rollback criteria and who may approve a temporary return to A.

**Acceptance criterion:** the retired key cannot authorize a new release after cutover. Do not delete the only evidence of old signatures before the audit policy says they can be retired. Rotation changes trust policy; it does not automatically erase historical signatures.

#### 4.6.3 Signing-outage contingency

**Runbook — signing unavailable**

- **Trigger:** trusted signing step cannot produce or publish required signature/evidence.
- **Triage:** determine whether the failure is key custody, identity, registry, network, transparency service, or policy error; preserve sanitized logs.
- **Decision:** default is delay/reject release. Use an alternate signer only if it is pre-approved, independently controlled, and explicitly trusted by policy. Do not invent a new trusted key during an incident and silently accept it.
- **Break glass:** requires named approver, reason, affected digest, compensating checks, time limit, rollback/expiry, and an audit record. Never disable verification without a record.
- **Recovery:** restore normal signing, re-verify all affected digests, reconcile deployments, expire the exception, and run a post-incident review.
- **Prevention:** exercise recovery, rotate compromised credentials, and test the contingency policy before production use.

#### 4.6.4 Model-artifact integrity before use

A model file is an artifact too. The loader should verify a trusted digest/signature and policy before use, and should refuse an unsigned or changed file. This does not establish model quality, dataset lineage, or training provenance. Never demonstrate this by loading an untrusted pickle: Python pickle deserialization can execute code. Use a harmless model-like byte file and verify its hash/signature before passing it to any loader. If using `cosign sign-blob`/`verify-blob`, verify exact current flags and bundle requirements against the installed version before running; the API is version-sensitive.

A minimal integrity-only helper (not a signature verifier) can demonstrate the fail-closed decision for a pinned SHA-256 digest:

```python
#!/usr/bin/env python3
"""Integrity check for a harmless model-like file; does not authenticate the expected hash."""
import hashlib
import sys
from pathlib import Path

if len(sys.argv) != 3:
    raise SystemExit("usage: verify_model_hash.py FILE EXPECTED_SHA256")
path = Path(sys.argv[1])
expected = sys.argv[2].lower()
actual = hashlib.sha256(path.read_bytes()).hexdigest()
if actual != expected:
    raise SystemExit(f"DENY: digest mismatch actual={actual}")
print(f"ALLOW: digest matches {actual}")
```

This is only meaningful if the expected digest arrives through a trusted channel. A production design should verify an authenticated signature/attestation as well as the hash, then validate model format and provenance before load.

#### 4.6.5 Metrics and governance

Define metrics with an explicit numerator, denominator, time window, owner, and limitation:

| Metric | Definition | Limitation |
|---|---|---|
| Verified digest coverage | Production deployment digests with a recorded successful policy verification / all production deployment digests in the window. | Does not prove the policy was strong or the builder trustworthy. |
| Required attestation coverage | Deployed digests with all policy-required attestations / all deployed digests in scope. | Depends on correct classification of required evidence. |
| Promotion gate denial rate | Promotion attempts denied by signature/evidence policy / all promotion attempts. | A high rate may indicate attacks, bad tooling, or broken rollout; investigate causes. |
| Evidence freshness | Distribution of age of scan/test/provenance evidence at promotion/deployment. | Timestamp trust and evidence semantics must be defined. |
| Key-rotation compliance | Active signing identities rotated/tested within the approved window / identities in scope. | Rotation completion alone does not prove compromised copies are gone. |
| Exception age | Age and count of active exceptions by owner and severity. | Exceptions can be formally current but still unsafe; review rationale. |
| Time to contain signer compromise | Time from confirmed compromise signal to stopping new accepted signatures and reconciling affected digests. | Depends on detection quality and incident classification. |
| Verification availability | Successful policy verification requests / eligible verification requests. | Must separate policy denials from infrastructure errors. |

Do not invent target values. Derive them from release criticality, recovery requirements, risk tolerance, and measured baseline. Stage rollout: observe in report-only mode, remediate false positives, test the negative cases, then enforce for a bounded scope with rollback and an owner. “100% signed” is a coverage statement, not a guarantee of safety.

#### 4.6.6 Multi-team and multi-tenant trust

Separate identities by environment and team when their authority differs. Define which repositories, source refs, builders, and namespaces each identity can authorize. Central policy should not accidentally allow the development signer to authorize production artifacts. Registry path/namespace boundaries are useful but not sufficient if the same identity can sign across them. Audit policy changes, signer use, and exceptions; test a cross-team negative case.

#### 4.6.7 Future and alternative ecosystems

Notation/Notary v2, ORAS, TUF, and in-toto can be relevant to interoperability, trust metadata, or artifact distribution. Treat these as awareness topics here; compare the exact current feature set and registry support before selecting one. Do not claim interchangeability between signature formats or policy engines without a verified compatibility test.

### 4.7 SRE lens

Signing and verification are production dependencies. Measure signing duration, verification latency, registry/attestation availability, verification failure reasons, and the proportion of running digests that can be reconciled to approved evidence. Alert on unknown signer, digest mismatch, missing or stale attestation, unexpected key use, policy bypass, key rotation overdue, and sudden verification failure rates. Keep policy denials distinct from infrastructure failures: the former can be correct security behavior, while the latter may indicate registry or trust-service outage.

**Fail-open versus fail-closed:**

- **Development:** a warning/report-only phase may be acceptable while onboarding, but it must not be mistaken for enforcement.
- **Staging:** enforce the intended policy and test recovery before production.
- **Production:** default to rejecting a release when required evidence cannot be verified, unless a narrowly defined, pre-approved contingency is explicitly authorized and audited.
- **Emergency:** use a named approver, exact digest, compensating controls, expiry, and a post-incident reconciliation; never silently disable the gate.
- **Registry or transparency outage:** decide whether a previously collected, verifiable evidence bundle is sufficient under policy. Do not assume offline verification is supported until tested.

**Runbook snippet**

`Trigger → triage → decision → containment → recovery → evidence`

1. Trigger on signature failure, unknown signer, subject mismatch, or verification service outage.
2. Triage whether the cause is policy, artifact identity, registry, key, trust root, or network.
3. Decide reject/delay versus the pre-approved contingency; name the decision-maker.
4. Contain by stopping promotion, denying the digest, or disabling the compromised identity through a controlled policy change.
5. Recover normal verification and re-check deployed digests.
6. Preserve digest, policy version, timestamp, sanitized error, decision, approver, and remediation evidence.

Connect incident command and postmortems to M10, and metrics/alerts to M11. Measure resource use locally rather than assuming a universal overhead number.

### 4.8 Security lens

| Threat/failure | Preventive control | Detective control | Corrective control | Negative test | Evidence | Residual risk / owner |
|---|---|---|---|---|---|---|
| Tag mutation/deploy by tag | Digest-only release policy | Compare deployed reference with approved digest | Roll back to verified digest | Move tag to second harmless image | Tag-mutation report | Alternate deploy paths; platform owner |
| Registry write used to publish fake signature | Pin expected signer | Audit signature identity/key | Remove unauthorized evidence and rotate trust if needed | Sign with wrong throwaway key | Wrong-key denial | Registry admin compromise; security owner |
| Wrong/untrusted key | Explicit key pin | Verification logs | Update policy after investigation | Verify with unrelated public key | Policy decision record | Trusted key compromise; key owner |
| Broad keyless identity rule | Exact issuer/identity constraints | Policy lint/review | Narrow policy and re-verify releases | Test wildcard identity fixture | Identity review answer key | Issuer/claim changes; identity owner |
| Compromised builder signs harmful output | Isolated trusted builder, provenance, review | Compare build evidence and runtime behavior | Revoke builder authority, rebuild and reconcile | Simulate bad build record in fixtures | Builder trust review | Unknown builder compromise; build platform owner |
| Stolen signing key/token | Restricted custody and short-lived access | Key-use audit and anomaly alerts | Stop signer, rotate, investigate affected digests | Simulate retired/untrusted key | Rotation report | Unobserved copies; security/key owner |
| Attestation subject mismatch | Verify subject digest | Automated digest consistency check | Rebuild/re-attach evidence to correct artifact | Mutate fixture digest | Negative-test report | Bad evidence producer; release owner |
| Missing/stale evidence | Required-attestation and freshness policy | Coverage/freshness reports | Rescan/retest or deny digest | Remove or stale a fixture | Gate report | Evidence source integrity; security owner |
| Replay/rollback of old vulnerable image | Release and deny-list policy | Compare deployment digest with allowed release state | Deny/replace old digest | Add digest to local deny-list | Deny-list exercise | Emergency rollback needs; service owner |
| Old key remains accepted | Versioned trust policy and rotation tests | Periodic retired-key test | Remove old trust and reload verifier | Verify old-only signature after cutover | Rotation test | Cached policy; verifier owner |
| Registry/transparency outage | Resilience and documented offline policy | Availability/failure telemetry | Delay release or use approved contingency | Simulated outage/failure fixture | Runbook record | Availability dependency; platform owner |
| Portability failure | Registry pair conformance test | Compare evidence discovery at destination | Reject destination promotion | Copy or fixture simulation | Portability report | Registry-specific behavior; platform owner |
| Private key committed/logged | Secret hygiene and repository scanning | Secret scan and audit | Revoke/rotate key, purge access, investigate | Use synthetic canary only in disposable fixture | Incident record | Historical clones; key owner |
| Model artifact tampering | Verify hash/signature before load | Loader audit logs | Reject artifact and restore trusted version | Change one byte in harmless file | Refusal test | Model/data poisoning upstream; ML platform owner |
| Policy bypass/unlogged break-glass | RBAC and auditable exception path | Audit policy changes and exception use | Revoke bypass, re-verify releases | Test denied unauthorized override | Exception audit | Insider risk; security governance owner |

Map these threats to Unit 1’s trust boundaries and attack paths. Residual risk remains if the source, builder, signer, policy owner, verifier, or model loader is compromised. A signature helps establish artifact identity and signer claims; it does not make the artifact safe.

### 4.9 Production checklist

- [ ] Release, promotion, and deployment records use immutable image digests.
- [ ] Signing occurs only in the trusted release path.
- [ ] Private keys are unavailable to untrusted pull-request jobs.
- [ ] Verification pins the expected public key or exact keyless identity and issuer.
- [ ] Verification checks the expected digest, not merely the presence of any signature.
- [ ] Required attestations are present and refer to the same subject digest.
- [ ] Attestation types, schemas, and predicate versions are checked against selected tool versions.
- [ ] SBOM, scan summary, test report, and provenance are bound to the correct artifact where policy requires them.
- [ ] Freshness and deny-list rules exist for post-signing vulnerability disclosures.
- [ ] CI promotion gate has positive and negative tests.
- [ ] Registry permissions and signature/referrer behavior are documented for each registry.
- [ ] Key storage, rotation, revocation, recovery, and retirement have been exercised.
- [ ] Multi-team and environment trust boundaries are explicit.
- [ ] Admission verification is planned for Units 8/11.
- [ ] Model artifacts are hash/signature verified before use; untrusted pickle files are never loaded.
- [ ] Verification evidence is retained and scrubbed of secrets.
- [ ] Failure modes and break-glass process are tested and auditable.
- [ ] Exceptions have an owner, rationale, expiry, and review date.
- [ ] Running image digests can be reconciled with signed/verified artifact records.

### 4.10 Hands-on lab set

The nine mandatory themes below are grouped into five coherent labs. Every lab is restricted to the learner’s own disposable local environment and harmless fixtures.

| Lab ID | Goal | Steps | Expected evidence | Cleanup | Stretch |
|---|---|---|---|---|---|
| U4-LAB-01 — Sign, verify, attest | Key-based sign/verify end-to-end; attach SBOM, scan, and test attestations; policy rejects wrong signer, missing SBOM, wrong subject, and critical-fixable scan result. | Use M01 local registry and throwaway keys; capture digest; sign by digest; create/use Unit 3 SBOM; attach custom scan/test predicates only after checking current cosign syntax; run local policy tests. | Digest record, key paths (no key contents), verification result, attestation artifacts, positive/negative test report. | Remove disposable registry image/evidence and destroy private key. | Verify the same policy in a clean second workspace. |
| U4-LAB-02 — Tag mutation and promotion gate | Prove a different image under the same tag is not accepted as the previously signed artifact; enforce digest-only promotion. | Push harmless image A and sign digest A; push harmless image B under the same tag; capture digest B; test gate with A and B; use offline promotion-gate tests. | Tag-mutation report, both digests, gate decision, positive and negative tests. | Remove test tags/images and generated records. | Reconcile actual deployed digest from a disposable kind workload. |
| U4-LAB-03 — Keyless identity and policy | Explain keyless flow, test narrow identity pinning conceptually, identify dangerous matching rules. | Read official current docs; record actual installed cosign flags; review ten synthetic policies in §4.5.2; use sample evidence if no safe local OIDC/Sigstore environment exists. | Annotated flow, version notes, policy-review answer key. | Delete temporary samples. | Verify an actual keyless identity only in an authorized, explicitly configured lab. |
| U4-LAB-04 — Rotation, model integrity, freshness | Rotate key, retire old trust, refuse tampered model-like bytes, deny a digest after a synthetic advisory, and record contingency behavior. | Run the key-rotation sequence in §4.6.2; test old-key rejection; use harmless model-like file with trusted hash/signature verification; add digest to deny-list fixture; simulate signing unavailable. | Rotation report, refusal test, deny-list decision, contingency audit record. | Remove keys and files; retain only scrubbed evidence. | Add a policy expiry test and alert on overdue exceptions. |
| U4-LAB-05 — Registry portability | Test whether image and signatures/attestations survive a move between two local registries. | Copy image by digest; use the selected tool’s documented signature/evidence discovery commands; compare source and destination; verify all evidence at destination. If second registry unavailable, produce a fixture analysis explicitly marked non-equivalent. | Portability report with source/destination digests, discovery results, verification decisions, limitations. | Stop disposable registry containers and remove temporary content. | Add registry/version pair to a conformance matrix. |

### Required lab controls and execution notes

For each lab, record the following in `versions.txt`: date/time, OS/kernel, WSL2 or native Linux, container runtime and version, registry implementation/version, cosign version, Python version, exact commands, image digests, and whether the test ran online or offline. Use `docker system df` and OS tools to measure footprint before/after; do not invent performance numbers.

- **Positive tests:** legitimate signed digest, correct key, required attestations with matching subject, acceptable scan/test result.
- **Negative tests:** unsigned image, wrong key, different digest, missing SBOM, subject mismatch, stale scan/test evidence, denied scan result, retired key, tampered model-like file, and unlogged bypass.
- **Internet/offline:** tool/image pulls and official documentation need internet; the normalized policy suite and synthetic identity review run offline. Registry signing/verification may work against a local registry without public internet, but confirm behavior for the chosen registry/version.
- **Troubleshooting:** first separate authentication/connectivity failures from expected policy denials. Compare exact digests; inspect installed `--help`; check registry logs; verify key paths and password prompt; inspect subject digest; avoid weakening policy as a diagnostic shortcut.
- **Cleanup:** delete the private key and temporary signing material after completing the rotation/portability exercises. Keep sanitized reports, public key, digests, and policy versions only if appropriate for the lab.
- **WSL2/native Linux:** localhost networking and filesystem permissions may differ. Do not move encrypted private-key files into shared Windows folders. On native Linux, check local registry firewall/listening state.
- **Scope:** all operations must use lab-owned images, keys, registries, and synthetic fixtures. Do not target third-party registries or production systems.

The pure-Python policy checker tests can run offline, but they only test policy logic over normalized evidence. They do not replace cosign verification or validate actual registry artifacts. Registry portability and keyless labs are not execution-verified unless the learner performs them in the selected environment.

### 4.11 Self-check questions

1. **What does a valid signature prove?**  
   **Answer:** Under the verifier’s rules, the corresponding trusted key/identity signed a claim for the exact subject. It does not prove the artifact is safe, the builder is uncompromised, the scan is fresh, or deployment uses that digest.  
   **Tempting wrong answer:** “It proves the artifact is trusted.” That skips the policy decision and upstream trust assumptions.

2. **Why deploy by digest rather than tag?**  
   **Answer:** Tags can move; a digest identifies the specific manifest/content being approved.  
   **Tempting wrong answer:** “Tags are immutable after signing.” Signing does not freeze a registry tag.

3. **The image has a valid signature, but it was signed by an unknown key. Allow?**  
   **Answer:** No; cryptographic validity is not authorization. The key must be accepted by policy for this repository/environment.  
   **Tempting wrong answer:** “Any valid signature is enough.” That permits anyone to sign a replacement.

4. **Key-based versus keyless: which is safer?**  
   **Answer:** Neither is universally safer. Key-based requires key custody and rotation; keyless requires precise identity/issuer policy and trust in the identity/certificate/transparency model. Choose based on threat model and verify implementation.  
   **Tempting wrong answer:** “Keyless has no secrets, so it has no risk.”

5. **Why are broad identity regexes dangerous?**  
   **Answer:** They may accept unrelated workflows or identities from the same issuer. Pin exact issuer and narrow subject/workflow claims, then test both allowed and denied identities.  
   **Tempting wrong answer:** “The issuer is trusted, so every identity from it is trusted.”

6. **What must match across image and attestations?**  
   **Answer:** Each required attestation must refer to the exact subject digest being evaluated, and the signer/predicate/freshness must satisfy policy.  
   **Tempting wrong answer:** “Matching image name is enough.” Names and tags can be reused.

7. **A scan attestation passed last week; a new advisory appeared today. Is the image still acceptable?**  
   **Answer:** Not automatically. Re-evaluate current risk and apply evidence freshness/deny-list policy. Signature validity does not update scan conclusions.  
   **Tempting wrong answer:** “The signature is still valid, so the scan is still current.”

8. **A compromised builder signs a malicious image with the expected key. What does verification do?**  
   **Answer:** It can pass the signature check. Separate builder trust, provenance, source protection, tests, scanning, and incident response are still required.  
   **Tempting wrong answer:** “The signature detects malicious builds.”

9. **What proves key rotation worked?**  
   **Answer:** After cutover, new key B verifies and an image signed only by retired key A is rejected by the active policy, outside any documented dual-trust window.  
   **Tempting wrong answer:** “A new key was generated.” Generation alone does not change verifier trust.

10. **The registry is unavailable during release. Should verification be bypassed?**  
    **Answer:** Default to delay/reject. Use a previously tested offline evidence path or pre-approved, logged contingency only if policy explicitly allows it.  
    **Tempting wrong answer:** “Temporarily turn off the gate.” Unlogged bypass destroys the control’s value.

### 4.12 Evidence artifacts

Save under `$HOME/m12-unit4-lab/` rather than assuming a repository directory exists:

- `versions.txt` — tool versions, OS/platform, registry implementation, timestamp, commands, and image digests.
- `keys/cosign.pub` — throwaway public key if retained for the lab; list the private-key path only in the evidence index, never include private-key contents.
- `evidence/image-digest.txt` — exact full digest reference.
- `evidence/verify-positive.txt` and `evidence/verify-negative.txt` — sanitized verification outcomes.
- `evidence/tag-mutation-report.md` — original and replacement digests, test method, and decision.
- `evidence/attestations/sbom-predicate.json`, `scan-predicate.json`, and `test-predicate.json` — clearly labelled fixtures or real tool-produced outputs; distinguish them.
- `evidence/attestation-verification.txt` — verification output and subject-digest consistency results.
- `evidence/policy/policy.json` plus fixtures and test report.
- `scripts/promotion_gate.py` and `scripts/test_promotion_gate.py` — local policy logic and tests.
- `evidence/promotion-gate-report.txt` — positive/negative decisions and policy version.
- `evidence/keyless-walkthrough.md` — official docs consulted, version notes, and ten-policy review answer key.
- `evidence/key-rotation-report.md` — dual-trust window, cutover, old-key rejection, rollback plan.
- `evidence/model-integrity-report.md` — trusted digest/signature check and tampered-file refusal; no unsafe deserialization.
- `evidence/freshness-denylist-report.md` — synthetic advisory and deny decision.
- `evidence/signing-outage-runbook.md` and `evidence/contingency-audit-record.json` — simulated failure and authorized decision.
- `evidence/registry-portability-report.md` — live two-registry result or explicitly non-equivalent fixture analysis.
- `evidence/production-checklist.md`, `claim-register.md`, `source-notes.md`, and `audit.md`.

Never retain private key contents, passwords, tokens, or real production identities in evidence. If a key was accidentally exposed, treat it as compromised and rotate it rather than simply deleting the local file.

### 4.13 Common interview and design-review questions

1. **What does an image signature prove, and what does it not prove?**  
   A valid signature proves that the key corresponding to the accepted public key, or an identity accepted by policy, signed a claim for the specific digest. The policy must decide whether that signer is authorized for this source and environment. It does not prove artifact safety, build integrity, scan freshness, or correct deployment. I would retain digest, signer/key identity, policy version, timestamp, and a positive/negative verification record; test with an untrusted key and altered digest.

2. **Why must release and deployment workflows verify by digest rather than mutable tag?**  
   Tags are names that can be reassigned. If CI checks a tag but a deployment resolves it later, the checked object and used object may differ. The pipeline should capture the digest from the trusted push, sign and verify that digest, promote it unchanged, and compare the running workload’s resolved image digest with the release record. The trade-off is less human-friendly naming, which can be handled by keeping tags as metadata while using digest as the deployment identity.

3. **How would you design keyless verification so an unintended CI workflow cannot sign an accepted production image?**  
   Pin both issuer and exact expected identity/workflow claim, protect the workflow definition and release ref, separate production signing authority from untrusted PR jobs, and test nearby-but-untrusted identities as negative cases. Do not accept a broad wildcard or issuer-only rule. Record actual identity claims and verify flag semantics against the selected cosign version. Residual risk includes compromise of the trusted workflow or identity issuer.

4. **How do you verify SBOM, vulnerability-scan, test, and provenance attestations as one consistent evidence set?**  
   First verify signature and signer for each required attestation; then validate predicate type/schema, subject digest, source/builder claims, timestamp/freshness, and policy result. Require all evidence to refer to the exact image digest and preserve a versioned decision record. A signed but stale scan should be rejected or refreshed; a valid provenance claim does not replace scan or test evidence. Unit 10 later deepens provenance semantics.

5. **What happens if the signing key, registry, identity provider, or transparency log is unavailable or compromised?**  
   Availability failure should normally delay or reject release. An offline bundle or alternate signer is acceptable only if it was predesigned, independently controlled, verified, and permitted by policy. If a key/identity is compromised, stop accepting new signatures from it, identify affected digests, revalidate deployments, rotate trust, and preserve evidence. A break-glass path needs a named approver, reason, exact digest, compensating controls, expiry, and post-incident review.

### 4.14 Sources and verification notes

Primary sources consulted for this module:

- **Sigstore, “Signing Containers.”** Current documentation shows `cosign generate-key-pair`, key-based `cosign sign --key ...`, signing an image reference, and `cosign attest --type ... --predicate ...`; it also describes registry-backed signing and OCI referrer usage. Canonical page: https://docs.sigstore.dev/cosign/signing/signing_with_containers/
- **Sigstore, “Verifying Signatures.”** Verification command structure and key-based/keyless verification options. Canonical page: https://docs.sigstore.dev/cosign/verifying/verify/
- **Sigstore, “In-Toto Attestations.”** Documents `cosign attest --predicate ... --key ...` and `cosign verify-attestation --key ...`; predicate schema and installed-version behavior still require local verification. Canonical page: https://docs.sigstore.dev/cosign/verifying/attestation/
- **Sigstore, “Sigstore Quickstart with Cosign.”** Explains keyless identity, short-lived certificate, transparency evidence, and verification identity constraints. Canonical page: https://docs.sigstore.dev/quickstart/quickstart-cosign/
- **Sigstore, “Key Management Overview.”** Key-generation and key-based signing examples. Canonical page: https://docs.sigstore.dev/cosign/key_management/overview/
- **Open Container Initiative, Distribution Specification.** Registry content distribution and referrer discovery semantics; support and copy behavior must be tested against the actual registry. Canonical specification: https://github.com/opencontainers/distribution-spec
- **in-toto Attestation Framework / Statement and DSSE specifications.** Use the current official specifications to validate statement and envelope semantics before defining standardized predicates. Exact predicate fields are not reproduced here.
- **Kubernetes admission documentation; Kyverno `verifyImages`; Sigstore policy-controller and Ratify documentation.** Handoff only: verify current API versions and implementation behavior when completing Units 8 and 11.
- **Course handoffs:** M01 local registry and digest pinning; M08 promotion-by-digest and evidence chain; M09 key/secret hygiene; M12 Unit 1 threat model; Unit 2 scan triage; Unit 3 SBOM generation; Unit 5 trusted builders and short-lived CI identity; Unit 8 admission enforcement; Unit 10 provenance; Unit 11 policy authoring.

### Verification notes

- Current official Sigstore documentation was checked on 2026-10-29 for the linked signing, verification, and attestation pages.
- No cosign binary, local registry, or Kubernetes cluster was available to execute this module’s end-to-end commands in this authoring pass. Tool-specific commands are therefore documentation-reviewed, **not execution-verified**.
- Verify `cosign version`, `cosign generate-key-pair --help`, `cosign sign --help`, `cosign verify --help`, `cosign attest --help`, and `cosign verify-attestation --help` before running. Record the exact installed version and adapt syntax only after checking official documentation.
- Verify the registry’s OCI referrer support, auth requirements, signature retention, deletion, and copy behavior. Do not assume a local registry behaves like a hosted registry.
- Verify attestation predicate types and schema fields for the selected tools. The custom JSON fixtures in this module are policy-learning fixtures, not standardized in-toto predicate examples.
- Verify keyless issuer/identity claims and regex semantics using the actual signer identity and installed cosign version. Never use wildcard identity matching in production.
- Verify the installed cosign version’s bundle/offline verification behavior before designing an air-gapped release flow.
- Do not claim test execution unless the commands have actually been run and their output retained.

## Author’s Verification and Completeness Audit

Status meanings: **PASS** means the requirement is visibly addressed in this artifact; **VERIFY** means the design/content is present but environment/version behavior remains to be checked; **GAP** means a requirement is missing. A PASS on content does not mean a live control was executed.

| Requirement | Status (PASS/VERIFY/GAP) | Evidence pointer | Audit note |
|---|---|---|---|
| Exact Unit 4 heading and section order | PASS | §§4.0–4.14 | Required sequence is present. |
| L1–L4 measurable objectives | PASS | §4.1 | Ten objectives span foundations through governance. |
| Signature semantics and limitations | PASS | §§4.0, 4.2, 4.3 | Explicitly separates identity/integrity from safety. |
| Key-based/keyless comparison and Sigstore model | PASS/VERIFY | §§4.2, 4.5.2, 4.14 | Model described; local/keyless behavior is not run here. |
| Digest pinning and mutable-tag risk | PASS | §§4.2–4.4 | Uses digest-based flow and tag-mutation test plan. |
| Cosign sign/verify/attest command syntax | VERIFY | §§4.3–4.4, 4.14 | Official docs checked; local version and registry syntax not execution-verified. |
| OCI signature/attestation storage and registry limits | VERIFY | §§4.2, 4.5.6, 4.10 | Referrer model linked; actual registry pair must be tested. |
| in-toto Statement and DSSE concepts | PASS/VERIFY | §§4.2, 4.4.4, 4.14 | Concepts covered; standardized predicate fields are intentionally not invented. |
| SBOM, scan, and test attestations; subject digest | PASS/VERIFY | §§4.4.4–4.4.5 | Fixtures and command patterns provided; real schemas/tool outputs require verification. |
| Verification policy and CI promotion gate | PASS | §§4.4.5–4.4.6 | Offline policy logic and unit tests supplied; adapter must authenticate input. |
| Registry permissions and signer pinning | PASS | §§4.4.6, 4.5.1 | Explicitly rejects “any signature” trust. |
| Other artifact types and Kubernetes admission handoff | PASS/VERIFY | §§4.4.7, 4.9 | Design covered; commands/API versions deferred and marked version-sensitive. |
| Key management, rotation, revocation, environment separation | PASS | §§4.4.8, 4.6.2, 4.8 | Rotation acceptance criteria include retired-key rejection. |
| Trust model and ten identity policy exercise | PASS/VERIFY | §§4.5.1–4.5.2 | Synthetic policy descriptions and answer key; actual identity claim format must be verified. |
| Multi-role verification, freshness, TOCTOU, replay/rollback | PASS | §§4.5.3–4.5.4 | Trade-offs and failure cases explained. |
| Transparency logs, offline verification, portability | VERIFY | §§4.5.5–4.5.6 | Requirements and tests defined; local registry/air-gap workflow not executed. |
| Keyless walkthrough lab | PASS/VERIFY | §§4.5.2, 4.10 | Includes official-doc workflow and offline fallback; no local OIDC stack claimed. |
| Key-rotation lab | PASS/VERIFY | §4.6.2, §4.10 | Procedure defined; execution not verified. |
| Model artifact verification/refusal | PASS/VERIFY | §4.6.4 | Integrity helper is included; signature CLI path must be verified before use. No pickle is loaded. |
| Freshness/deny-list exercise | PASS | §§4.5.4, 4.10 | Synthetic deny-list exercise defined; local policy tests can run offline. |
| Signing-failure contingency | PASS | §§4.6.3, 4.7 | Explicit decision, approval, expiry, and audit path. |
| SRE lens and metrics | PASS | §4.7 | Metrics include definitions and limitations; no invented targets. |
| Security lens and residual risk | PASS | §4.8 | Threat/control/negative-test/evidence/owner mapping included. |
| Production checklist | PASS | §4.9 | Verifiable checkbox list included. |
| All nine mandatory lab themes | PASS/VERIFY | §4.10 | Grouped into five labs; live registry, keyless, and portability execution remains unverified. |
| Self-check questions | PASS | §4.11 | Ten questions include answer keys and tempting wrong answers. |
| Evidence artifact paths | PASS | §4.12 | Paths are under a dedicated local workspace and exclude key contents. |
| Exactly five interview questions | PASS | §4.13 | Five senior-level model answers included. |
| Sources and verification notes | PASS | §4.14 | Official source titles and canonical URLs are listed; claims are qualified. |
| Zero-budget, offline, and WSL2 constraints | PASS/VERIFY | Metadata, §§4.4, 4.10 | Core fixture tests are offline; local network/registry specifics must be measured. |
| Cross-module boundaries | PASS | §§4.0, 4.4.7, 4.7, 4.14 | M01/M08/M09 and M12 Units 1–5/8/10/11 handoffs stated. |
| Authenticity and execution status | PASS | §4.14 and this audit | No live tests are claimed; CLI/registry items requiring validation are called out. |
| Private-key and sensitive-data safety | PASS | §§4.3–4.4, 4.6.2, 4.12 | Only throwaway keys; no key material or credentials embedded. |

### Unresolved items before production use

1. Run the module in the learner’s actual M01 registry/runtime and record versions and commands.
2. Confirm local cosign CLI syntax, key password handling, and attestation predicate support for the installed version.
3. Execute the Python policy unit tests; this artifact does not claim they were executed during authoring.
4. Run real registry portability tests or retain the explicitly non-equivalent fixture report.
5. Verify keyless identity claims, bundle/offline behavior, and trust-root handling against current official docs and the selected version.
6. Replace every placeholder digest and illustrative fixture with clearly labelled lab-generated evidence before interpreting a real promotion decision.
7. Before production adoption, have security and platform owners review policy scope, exception handling, signer separation, and failure behavior.
