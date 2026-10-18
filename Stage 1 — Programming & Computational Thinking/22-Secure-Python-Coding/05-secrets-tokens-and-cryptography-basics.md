# Lesson 05 — Secrets, Tokens, and Cryptography Basics

> **Audience:** beginner-to-advanced Python developers, data engineers, and AI platform engineers  
> **Security posture:** defensive learning. Use only credentials and systems you own or are explicitly authorised to test. All examples use placeholders or generated test keys; never paste real credentials into source, notebooks, test output, or this lesson.

## Learning outcomes

By the end of this lesson, you should be able to:

- Trace a secret from creation through delivery, use, rotation, and revocation.
- Load runtime secrets without committing them, granting excessive access, or leaking them through logs, exceptions, command lines, or representations.
- Choose correctly among hashes, password KDFs, MACs, authenticated encryption, digital signatures, and TLS.
- Generate unpredictable tokens with `secrets`; implement authenticated encryption with `cryptography`; and verify HMAC webhooks safely.
- Explain nonce uniqueness, key separation, associated data, replay protection, and the difference between confidentiality, integrity, authenticity, and authorisation.
- Apply secure password storage, JWT validation, TLS verification, key rotation, secret scanning, and leak-response procedures.
- Build and test the `secretkit` mini-exercise, including redaction, missing configuration, token generation, tamper detection, and webhook verification.

## Prerequisites

- Python functions, exceptions, context managers, environment variables, and logging.
- Basic HTTP, Git, unit testing, and dependency management.
- Familiarity with `hashlib`, `hmac`, `secrets`, `subprocess`, and `.gitignore`.
- Earlier module lessons on untrusted input, safe subprocesses, and reproducible environments.

## Vocabulary

| Term | Meaning | Does **not** automatically provide |
|---|---|---|
| Secret | Value whose disclosure grants access or reveals protected information | Protection after it is logged or committed |
| Entropy | Unpredictability of a value | Correct authorisation or expiry |
| Hash | One-way digest of bytes | Confidentiality or proof of who created the data |
| Password KDF | Deliberately expensive derivation for password verification | Recovery of the original password |
| MAC / HMAC | Tag proving integrity and possession of a shared key | Publicly verifiable authorship or confidentiality |
| Authenticated encryption (AEAD) | Encryption plus integrity/authenticity under a key | Protection if the key is exposed or nonce rules are broken |
| Digital signature | Private-key signing, public-key verification | Confidentiality or proof that a signer is authorised for every use |
| Salt | Public, per-password random input to a password KDF | A secret key |
| Nonce | Value required by a cryptographic operation, often unique per key | A secret value in common AEAD schemes |
| KMS / HSM | Managed key protection and cryptographic operations | Correct application authorisation by itself |
| Rotation | Replacing a credential/key and transitioning consumers | Revocation of already copied plaintext or data |

---

## 1. Secrets lifecycle and threat model

### 1.1 Identify assets, entry points, and trust boundaries

Secrets include cloud and warehouse credentials, database passwords, API keys, OAuth refresh tokens, signing keys, encryption keys, webhook secrets, session cookies, private certificates, recovery codes, and service-account tokens. In data/AI systems, also consider notebook outputs, pipeline logs, prompt traces, model-evaluation artifacts, cache entries, CI artifacts, container layers, crash dumps, and data exports.

A minimal threat model asks:

1. **What does the secret grant?** Read-only dataset access, production write access, billing authority, signing authority, or administrator access?
2. **Who can read it?** Developer, CI job, runtime process, operator, other tenant, support tool, logging vendor, or compromised dependency?
3. **Where can copies persist?** Git history, build layers, shell history, process listings, logs, telemetry, backups, local disks, memory dumps, and browser history.
4. **How is it revoked?** Which control plane disables the old credential, and how quickly do dependent services receive the replacement?
5. **How do we detect misuse?** Audit events, unusual source IPs, API volume, privilege changes, unexpected regions, or billing spikes.

Use one credential per environment and workload where feasible. A development notebook should not receive production database administrator credentials. Give tools and agents scoped, short-lived credentials; do not expose a master key to a general-purpose agent or plugin.

### 1.2 Lifecycle stages

1. **Create:** generate with a trusted identity or cryptographic RNG; assign an owner, purpose, scope, and expiry.
2. **Deliver:** prefer workload identity, OIDC federation, or a secret manager. Restrict which job/service can retrieve the value.
3. **Use:** keep it in memory only as long as necessary; avoid command-line arguments and logs; send it only to the intended endpoint.
4. **Observe:** audit access without recording secret values. Alert on unusual usage and failed/denied access.
5. **Rotate:** issue a replacement, deploy it, verify consumers, then revoke the old value. Design overlap only when necessary and time-box it.
6. **Revoke and respond:** disable compromised credentials immediately, investigate use, remove persistence, and document corrective actions.

Rotation does not make leaked data secret again. If a credential was exposed, assume it was copied. Revoke or rotate first; then clean repository history and secondary copies.

### 1.3 Environment variables, `.env`, and secret managers

Environment variables are often a reasonable local-development delivery mechanism, but they are not a vault. They may be visible to processes with sufficient privileges, inherited by child processes, captured in diagnostics, or exposed by crash/debug tooling. They are also commonly static and long-lived.

- **Local development:** a local `.env` file may be convenient if it is excluded from Git, has restrictive permissions, contains only development credentials, and is never copied into an image. Prefer an example file containing placeholders, such as `.env.example`.
- **Production:** prefer workload identity/OIDC or a managed secret store with access policies and audit logs. Avoid baking secrets into image layers, Docker `ARG`/`ENV` build metadata, source, notebook outputs, or deployment manifests.
- **CI:** use scoped environment/repository secrets or OIDC federation to cloud roles. Do not print environment dumps. Forked pull requests and untrusted build steps must not receive privileged secrets.
- **Kubernetes:** base64 encoding a `Secret` is not encryption. Restrict RBAC, enable encryption at rest, consider an external secret operator or workload identity, and avoid granting every pod access to every secret.
- **Docker BuildKit:** use build-time secret mounts for the build step that needs a secret; do not persist it in a layer. Runtime secrets should be delivered at runtime.

Example `.gitignore` entries:

```gitignore
.env
.env.*
!.env.example
*.pem
*.key
secrets/
```

Adapt this to your repository: do not blanket-ignore legitimate public test certificates or checked-in fixtures without reviewing them. `.gitignore` prevents accidental additions; it does not remove already tracked files. Verify with `git status --ignored` and `git ls-files .env` as appropriate.

### 1.4 Fail-fast configuration and secret redaction

The following small configuration object reads a required environment variable and deliberately avoids exposing its value in `repr` or `str`.

```python
from dataclasses import dataclass, field
import os

@dataclass(frozen=True)
class SecretValue:
    _value: str = field(repr=False)

    def __repr__(self) -> str:
        return "SecretValue([REDACTED])"

    def __str__(self) -> str:
        return "[REDACTED]"

    def reveal_for_use(self) -> str:
        """Use only at the narrow boundary that needs the credential."""
        return self._value

@dataclass(frozen=True)
class Settings:
    provider_api_key: SecretValue

    @classmethod
    def from_env(cls) -> "Settings":
        value = os.environ.get("PROVIDER_API_KEY")
        if not value:
            raise RuntimeError("Required setting PROVIDER_API_KEY is missing")
        return cls(provider_api_key=SecretValue(value))
```

This is a teaching wrapper, not a complete secret-management system. `reveal_for_use()` intentionally makes access explicit, but Python cannot prevent code from calling it or copying the string. In production, use a secret manager or identity-based retrieval where appropriate. Pydantic's `SecretStr` is another option; confirm how your version serializes models and explicitly control structured logging.

Avoid embedding the actual secret in configuration errors. A missing variable name is usually safe to report; a value, full request header, or token-bearing URL is not.

### 1.5 Interactive input and command-line leakage

For an interactive local tool, `getpass` avoids echoing the entered value:

```python
from getpass import getpass

password = getpass("Password: ")
# Use it immediately; do not print it or include it in an exception.
```

Do not pass credentials as command-line flags such as `--password secret-value`: process listings, shell history, CI logs, and command diagnostics can reveal them. Prefer a supported secret file descriptor, protected file, stdin protocol, environment injection with awareness of its limitations, or the tool's native secret-manager integration. Do not assume stdin is safe if the child echoes or logs it.

### 1.6 Secret scanning and Git hygiene

Use multiple layers:

- `detect-secrets` to establish and maintain a reviewed baseline.
- Gitleaks locally and/or in CI; GitHub secret scanning and push protection where available.
- A `pre-commit` hook for fast feedback.
- CI checks on pull requests and default-branch changes.
- Periodic scans of repositories, notebooks, build artifacts, and relevant logs.

Example setup commands (install versions through your project's dependency-management process and pin them in CI):

```bash
python -m pip install detect-secrets pre-commit
# Install Gitleaks using its official release/package instructions for your OS.
detect-secrets scan > .secrets.baseline
pre-commit install
```

Example `.pre-commit-config.yaml` fragment; pin a reviewed release tag rather than using an unpinned moving branch:

```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: [--baseline, .secrets.baseline]
```

Example Gitleaks CI invocation depends on the installed Gitleaks version; commonly used commands include `gitleaks detect` or `gitleaks git`. Check the installed version's `gitleaks --help` and pin its version rather than copying a command from an arbitrary blog. GitHub secret-scanning features depend on repository and organisation settings.

A baseline is not a blanket allow-list. Review every finding, document false positives narrowly, and periodically rescan the baseline. Never add a real credential to a baseline just to make CI pass.

**If a secret is committed:**

1. Revoke/disable it or rotate it immediately; notify the credential owner/security on-call.
2. Check audit logs and scope of access from the exposure window; look for suspicious use and secondary copies.
3. Replace dependent deployments and verify the new credential works; revoke the old credential after the intended transition (or immediately if compromised).
4. Remove the value from the working tree and address Git history with a coordinated history rewrite if appropriate. History rewriting cannot remove clones, forks, caches, screenshots, logs, or copies already taken.
5. Rotate any credentials derivable from or accessible through the exposed credential; preserve relevant evidence without spreading the secret further.
6. Add a regression control, update the incident record, and review why prevention/detection failed.

---

## 2. Secret leakage paths and redaction

### 2.1 Common sinks

Never assume a value stays private because it is stored in an environment variable. It can leak through:

- `print(settings)`, `repr(config)`, dataclass dumps, Pydantic serialization, exception text, assertion messages, or debug logs.
- Full HTTP headers, query strings (`?access_token=...`), URLs containing credentials, request/response dumps, traces, telemetry, and crash reports.
- Shell commands, command-line flags, shell history, process listings, build arguments, Docker image layers, CI output, notebook cells/outputs, and generated HTML reports.
- `logging.exception()` when the exception itself embeds sensitive data, or third-party SDK debug logging.
- Prompt traces or agent tool logs containing API keys, user data, system prompts, or secrets pasted into a conversation.

### 2.2 Redact at the boundary; do not rely on regex alone

Best: log safe structured fields (request ID, provider name, status code, latency) instead of raw request objects. If you must log a URL, parse it and omit userinfo/query/fragment rather than using a broad string replacement.

```python
from urllib.parse import urlsplit, urlunsplit

def safe_url_for_log(url: str) -> str:
    parts = urlsplit(url)
    # Do not log userinfo. Keep only query keys known to be non-sensitive;
    # values are omitted to avoid accidental disclosure by unfamiliar keys.
    safe_query_names = {"page", "limit", "format"}
    kept = []
    for item in parts.query.split("&") if parts.query else []:
        name = item.split("=", 1)[0]
        if name in safe_query_names:
            kept.append(item)
    return urlunsplit((parts.scheme, parts.hostname or "", parts.path,
                       "&".join(kept), ""))
```

This is a conservative illustration, not a universal URL canonicalizer. It intentionally drops ports and query values and should be adapted to your routing/logging requirements. Do not log arbitrary URLs if the path itself may contain sensitive identifiers. For HTTP clients, log the host/provider and a request ID rather than raw headers.

Use structured logging and stable redaction policies. Redact authorization headers, cookies, API-key headers, refresh/access tokens, passwords, private keys, and provider-specific credential fields. Test redaction against actual log output. A regex can miss encoding variants, nested structures, renamed fields, and secrets split across messages.

```python
import logging

logger = logging.getLogger(__name__)

def record_provider_result(provider: str, status_code: int, request_id: str) -> None:
    # Safe fields only: no token, request headers, body, or full URL.
    logger.info("provider_request_complete", extra={
        "provider": provider,
        "status_code": status_code,
        "request_id": request_id,
    })
```

Do not put a secret in an exception and hope the top-level handler redacts it later. Raise a generic error while preserving a safe cause when appropriate. Remember that `raise ... from exc` may expose the original exception in tracebacks/logs; inspect whether the original exception includes credentials.

### 2.3 Python memory limitations

Python strings are immutable and may be copied or retained by libraries, tracebacks, allocators, core dumps, and swap. Deleting a variable does not guarantee immediate zeroisation. `bytearray` overwriting can be a best-effort mitigation in carefully controlled code, but copies may remain. Prefer short lifetimes, least privilege, avoiding dumps, and process isolation over claims of perfect memory erasure.

---

## 3. Cryptographic primitives: choose the correct tool

### 3.1 Security properties

| Need | Use | Example | Important limit |
|---|---|---|---|
| Verify password without storing it | Password KDF | Argon2id, scrypt, bcrypt | Must tune cost and rate-limit online attempts |
| Detect accidental or unauthenticated data changes | Hash | SHA-256 | Anyone can recompute a hash; no authenticity by itself |
| Verify message from a party sharing a secret | MAC/HMAC | HMAC-SHA-256 | Both parties can forge; key must remain secret |
| Keep data confidential and detect tampering | AEAD | AES-GCM, ChaCha20-Poly1305 | Nonce and key lifecycle are critical |
| Verify public provenance of an artifact | Digital signature | Ed25519 | Signature is meaningful only if public key identity/trust is established |
| Protect data in transit | TLS | `ssl.create_default_context()` | Does not secure compromised endpoints or authorise an application action |
| Derive a key from a password | Password KDF / KDF | Argon2id, scrypt, HKDF for suitable input key material | Do not use a raw password as an encryption key |
| Generate unpredictable tokens/keys | CSPRNG API | `secrets`, `os.urandom` | Randomness does not grant correct permissions or expiry |

A cryptographic hash is not encryption. A MAC is not a digital signature. Encryption without authentication may permit undetected tampering. A valid signature proves that the corresponding private key signed the bytes; it does not prove the signer was authorised to publish that artifact.

### 3.2 Secure randomness and capability tokens

Use `secrets` or a vetted cryptographic library's key-generation function, not `random`, for session tokens, reset links, API secrets, nonces that require unpredictability, or encryption keys.

```python
import secrets

session_token = secrets.token_urlsafe(32)  # 32 random bytes before URL-safe encoding
reset_token = secrets.token_urlsafe(32)
```

Store only a hash of a bearer token where the design permits lookup by token hash; return the raw token only once. Treat tokens as passwords: narrow scope, expiry, revocation, no logs, and TLS. A UUID4 is useful as an identifier but should not be treated as a secret capability token without a specific security analysis.

### 3.3 Hashing and password storage

Do not store plaintext passwords or fast general-purpose hashes such as `sha256(password)`. Use Argon2id where supported, or scrypt/bcrypt under a vetted library, with a unique random salt and cost parameters selected for your latency and threat model. The encoded password hash should carry the algorithm and parameters so it can be upgraded later.

Install:

```bash
python -m pip install argon2-cffi
```

Example:

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError

# Tune memory_cost, time_cost and parallelism using representative production hardware.
password_hasher = PasswordHasher()

def hash_password(password: str) -> str:
    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string")
    return password_hasher.hash(password)

def verify_password(encoded_hash: str, candidate: str) -> bool:
    try:
        password_hasher.verify(encoded_hash, candidate)
    except (VerifyMismatchError, VerificationError):
        return False
    return True

def password_hash_needs_upgrade(encoded_hash: str) -> bool:
    return password_hasher.check_needs_rehash(encoded_hash)
```

On successful login, if `password_hash_needs_upgrade(stored_hash)` is true, compute a fresh hash with the current parameters and update the database. Handle malformed stored hashes according to your application's error policy; do not treat database corruption as a successful login. The library performs password-hash verification; do not wrap the encoded Argon2 hash in `hmac.compare_digest` as a substitute for using its verifier.

Password controls also require:

- Rate limiting, progressive delays or carefully designed lockouts, monitoring, and MFA; avoid permanent account lockout as a denial-of-service primitive.
- Long passphrases and breached-password screening where feasible. Avoid arbitrary composition rules that encourage predictable substitutions.
- Secure reset tokens, single use, expiry, and invalidation of sessions when required.
- Never log candidates or include them in assertion/error messages.

A salt is not a secret and does not replace the KDF's work factor. Peppering can add defence in depth only if the pepper is stored separately and its loss/rotation has a plan.

### 3.4 Authenticated encryption with AES-GCM

Use the `cryptography` library rather than implementing a cipher. AES-GCM provides confidentiality and integrity when used correctly. Each encryption under a given key must use a unique nonce; for AES-GCM a 96-bit (12-byte) nonce is a common recommended size. **Never reuse a nonce with the same key.** Reuse can catastrophically reveal relationships between plaintexts and undermine authentication.

Install:

```bash
python -m pip install cryptography
```

Self-contained field encryption helper with an explicit key ID and associated data:

```python
from dataclasses import dataclass
import json
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

@dataclass(frozen=True)
class EncryptedField:
    key_id: str
    nonce: bytes
    ciphertext: bytes  # includes the AEAD authentication tag

class FieldCipher:
    def __init__(self, keys: dict[str, bytes], active_key_id: str):
        if active_key_id not in keys:
            raise ValueError("Active key ID is not configured")
        for key_id, key in keys.items():
            if not isinstance(key_id, str) or not key_id:
                raise ValueError("Key IDs must be non-empty strings")
            if not isinstance(key, bytes) or len(key) != 32:
                raise ValueError("AES-256-GCM keys must be 32-byte values")
        self._keys = dict(keys)
        self._active_key_id = active_key_id

    def encrypt_field(self, plaintext: bytes, *, tenant_id: str,
                      record_id: str, field_name: str) -> EncryptedField:
        # Fresh random 96-bit nonce for each encryption. For very high-volume
        # systems, use a formally designed nonce-allocation strategy and limits.
        nonce = os.urandom(12)
        aad = self._aad(tenant_id, record_id, field_name)
        ciphertext = AESGCM(self._keys[self._active_key_id]).encrypt(
            nonce, plaintext, aad
        )
        return EncryptedField(self._active_key_id, nonce, ciphertext)

    @staticmethod
    def _aad(tenant_id: str, record_id: str, field_name: str) -> bytes:
        # JSON array encoding keeps field boundaries unambiguous even when
        # values contain delimiters such as "|". AAD is authenticated, not secret.
        return json.dumps(
            ["v1", tenant_id, record_id, field_name],
            ensure_ascii=False, separators=(",", ":"),
        ).encode("utf-8")

    def decrypt_field(self, item: EncryptedField, *, tenant_id: str,
                      record_id: str, field_name: str) -> bytes:
        key = self._keys.get(item.key_id)
        if key is None:
            raise ValueError("Unknown encryption key ID")
        aad = self._aad(tenant_id, record_id, field_name)
        # Invalid tag, modified ciphertext, wrong key, or wrong AAD raises
        # InvalidTag. Do not return unauthenticated plaintext.
        return AESGCM(key).decrypt(item.nonce, item.ciphertext, aad)
```

Important design notes:

- The nonce is stored with the ciphertext; it is not secret. The key is stored separately in a KMS/secret manager. Persist the key ID, format/version, nonce, ciphertext, and any required metadata.
- Associated data (AAD) is authenticated but not encrypted. Bind ciphertext to context such as tenant, record, and field to prevent valid ciphertext being swapped across contexts. Ensure those values are reconstructed exactly on decryption.
- A fresh random nonce is a standard practical choice for modest volumes; it is not an unlimited-volume guarantee. With random 96-bit nonces, collision probability grows with the number of encryptions per key. Enforce per-key usage limits and rotate; very high-volume systems should use a reviewed nonce-allocation design.
- Never silently retry decryption with a different key/AAD after authentication fails. Do not expose detailed crypto failure diagnostics to untrusted callers.
- Do not store keys next to ciphertext in the same database or object-store bucket without a separate access boundary.

### 3.5 ChaCha20-Poly1305 and Fernet

`cryptography` also provides `ChaCha20Poly1305`, an AEAD suitable for systems where it is preferred or supported by the platform. It uses a 12-byte nonce and also requires nonce uniqueness per key. Use a fresh nonce and the library API; do not manually compose ChaCha20 and Poly1305.

```python
import os
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

key = ChaCha20Poly1305.generate_key()  # store through a key manager in real systems
cipher = ChaCha20Poly1305(key)
nonce = os.urandom(12)  # unique for every encryption under this key
ciphertext = cipher.encrypt(nonce, b"example payload", b"record-v1")
plaintext = cipher.decrypt(nonce, ciphertext, b"record-v1")
```

Fernet provides a simpler authenticated-encryption token format with built-in timestamp information and `MultiFernet` support for key rotation. It is useful for small application tokens, but it has a fixed format, exposes token creation time, and is not a replacement for a general-purpose data format with caller-supplied AAD. Choose it only when those semantics fit. Use `MultiFernet` with a planned migration/re-encryption process and protect all active keys.

```python
from cryptography.fernet import Fernet, InvalidToken

key = Fernet.generate_key()  # persist separately in a secret/KMS system
fernet = Fernet(key)
token = fernet.encrypt(b"example payload")
try:
    plaintext = fernet.decrypt(token, ttl=300)  # reject tokens older than 5 minutes
except InvalidToken:
    raise ValueError("Token is invalid or expired") from None
```

Fernet's TTL is based on its embedded creation timestamp; it is not a replacement for application authorisation, revocation, or a replay policy. Never generate a new key for each process start if previously stored tokens must remain decryptable.

### 3.6 HMAC for webhook verification

HMAC verifies that a message matches a tag created by someone with the shared secret and detects modification. It does not encrypt the body and does not by itself prevent replay. Verify the exact raw request bytes according to the provider's documented protocol, compare tags with `hmac.compare_digest`, and enforce timestamp/replay protection if the protocol supplies a timestamp or event ID.

```python
import hashlib
import hmac


def verify_webhook(raw_body: bytes, supplied_hex_tag: str, secret: bytes) -> bool:
    """Example protocol: hex HMAC-SHA-256 over the exact raw body."""
    if not isinstance(supplied_hex_tag, str) or len(supplied_hex_tag) != 64:
        return False
    try:
        supplied = bytes.fromhex(supplied_hex_tag)
    except ValueError:
        return False
    if len(supplied) != hashlib.sha256().digest_size:
        return False
    expected = hmac.new(secret, raw_body, hashlib.sha256).digest()
    return hmac.compare_digest(expected, supplied)
```

This is an example protocol, not a universal webhook signature format. Real providers may sign a timestamp plus body, use a prefix such as `sha256=`, or use a different encoding. Follow their exact specification. Reject stale timestamps and atomically record event IDs/nonces in a bounded replay store. Do not parse and re-serialize JSON before verification; whitespace/key order changes the signed bytes.

The lab below includes a second illustrative protocol that signs `ASCII(timestamp) + b"." + raw_body`. Its `claim_event_once` callback **must be an atomic, TTL-bounded store operation** (for example, a database insert protected by a unique constraint); a process-local set is only suitable for a single-process unit test. Do not adapt this wire format to a real provider unless it matches that provider's specification.

### 3.7 Ed25519 signatures for artifacts

Use signatures when a consumer must verify artifact provenance independently of the producer's transport channel. Keep the private signing key in a KMS/HSM or protected signing service where possible; distribute the trusted public key out of band or through a verified trust store. Sign an unambiguous, versioned byte representation or a cryptographic digest defined by a documented protocol.

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

# Demo only: generate a fresh key pair. Production verifiers must obtain the
# public key from a trusted, authenticated key-distribution mechanism.
private_key = Ed25519PrivateKey.generate()
public_key = private_key.public_key()
artifact = b"example artifact bytes"
signature = private_key.sign(artifact)

try:
    public_key.verify(signature, artifact)
except InvalidSignature:
    raise ValueError("Artifact signature verification failed")
```

A generated key pair in a demo does not establish trust. Production needs key identity, rotation/revocation, signed metadata (artifact name/version/digest), provenance, and a policy for which keys may sign which artifacts. A signature is not a substitute for scanning or safely parsing an artifact.

### 3.8 JWT validation

JWTs are a token format, not an encryption scheme. A signed JWT's payload is normally readable by anyone holding the token; do not place passwords, API keys, or sensitive personal data in it. A valid signature alone is not enough: validate issuer, audience, expiry, not-before where used, subject, allowed algorithms, and application-specific scopes/roles. Also decide how revocation and key rotation work.

Use a maintained library such as PyJWT or Authlib. Never trust the token's requested algorithm or key source without policy. Reject `alg: none`, algorithm confusion, unexpected key types, untrusted `jku`/`x5u` key URLs, missing required claims, and tokens issued for another service.

Illustrative PyJWT validation:

```python
import jwt

# Trusted values come from server configuration, not from the token itself.
claims = jwt.decode(
    encoded_token,
    key=trusted_verification_key,
    algorithms=["EdDSA"],
    issuer="https://issuer.example.invalid/",
    audience="reports-api",
    options={"require": ["exp", "iat", "iss", "aud", "sub"]},
)
```

Install `PyJWT[crypto]` if using supported asymmetric algorithms. This snippet is illustrative: define the trusted key and its rotation/discovery process, enforce appropriate clock-skew and token-age policy, validate application-specific claims/scopes, and handle decode errors without logging the token. `example.invalid` is a reserved placeholder domain, not a real issuer.

### 3.9 TLS and certificate verification

Use TLS with certificate-chain and hostname verification. In Python's standard library, start with `ssl.create_default_context()`; clients such as `httpx` and `requests` verify TLS by default unless configuration changes it.

```python
import ssl
import urllib.request

context = ssl.create_default_context()
context.minimum_version = ssl.TLSVersion.TLSv1_2  # explicit deployment baseline
with urllib.request.urlopen(
    "https://example.com/health", context=context, timeout=5
) as response:
    status = response.status
```

The example uses a public placeholder endpoint and is not a test fixture. For deterministic unit tests, inject a local test server and trusted test CA rather than contacting the internet.

- Never set `verify=False` or `CERT_NONE` to “fix” a certificate error. Diagnose the CA bundle, hostname, system clock, proxy, or server certificate instead.
- Use a maintained runtime with secure defaults and a minimum protocol policy appropriate to the deployment; TLS 1.2+ is a common baseline, while TLS 1.3 is preferred when compatible. Configure policy centrally and follow your platform/compliance requirements.
- Mutual TLS can authenticate a client workload to a service; still enforce application authorisation after TLS authentication.
- Certificate pinning is a specialised trade-off. It complicates rotation and recovery and is not a universal replacement for normal certificate validation.
- TLS protects data in transit between endpoints; it does not protect secrets after they reach logs, compromised endpoints, or unauthorised application code.

---

## 4. Key management, rotation, and operations

### 4.1 Separate keys by purpose

Do not reuse one key for encryption, HMAC, signing, password reset tokens, and unrelated environments. Use library-supported key separation or independent random keys. Never derive an encryption key directly from a short password. If a password must be used as input, use a suitable KDF with a unique salt and carefully chosen parameters; for protocols, use the KDF specified by the vetted design.

### 4.2 Envelope encryption

A common cloud pattern is envelope encryption:

1. Generate a data-encryption key (DEK) for a record, object, or batch.
2. Encrypt the data locally with an AEAD and a unique nonce.
3. Ask a KMS key-encryption key (KEK) to wrap/encrypt the DEK.
4. Store ciphertext, nonce, AAD/version metadata, key ID, and wrapped DEK; do not store the plaintext DEK alongside it.
5. At read time, authorise the caller, unwrap the DEK through KMS, decrypt, and validate the result.

The KMS key does not automatically authorise access to every encrypted record. Apply application/tenant access checks, IAM policy, audit logs, and data minimisation. Stage 2 cloud modules cover provider-specific KMS/IAM details; this lesson does not assume a specific cloud provider.

### 4.3 Rotation design

- Store a stable key ID with each ciphertext/signature metadata item.
- Support decrypting with current and explicitly approved previous keys during a bounded migration period.
- Encrypt new data with the active key; re-encrypt old data as required; then revoke old keys after verifying no required data remains dependent on them.
- For signing keys, publish trusted verification keys with validity/rotation metadata; plan how verifiers reject revoked or retired keys.
- For API credentials, issue a new credential, deploy it, verify usage, then revoke the old one. If exposure is suspected, prioritise immediate revocation over a graceful overlap.
- Test the failure path: missing KMS permissions, expired identity, unavailable secret manager, revoked key, and a ciphertext with an unknown key ID.

A key rotation that only changes an environment variable but leaves the old key accepted forever is incomplete. Maintain an inventory, owner, scope, expiry, last-used time, and documented revocation path.

### 4.4 CI, containers, notebooks, and AI systems

- Prefer OIDC federation from CI to cloud roles over long-lived cloud access keys where supported. Limit permissions by repository, branch, environment, workflow, and deployment target.
- Do not expose production secrets to untrusted pull requests, forks, arbitrary scripts, or dependency installation hooks.
- Avoid secret values in Docker build context and image layers. Add `.dockerignore` rules for local secret files and use supported BuildKit secret mounts when a build step genuinely needs a secret.
- Keep notebooks and outputs free of credentials. Scan `.ipynb` files and exported HTML; strip outputs where appropriate, but do not rely on stripping as the only control.
- In Kubernetes, constrain service-account token automounting when unnecessary, scope RBAC, use workload identity, restrict secret access by namespace/workload, and enable encryption at rest according to cluster policy.
- For LLMs/agents, use server-side credential injection, per-tool scoped credentials, allow-listed destinations/actions, spend budgets, and redacted traces. Do not put provider keys into prompts or model context. Treat generated output as untrusted and never allow it to request a master secret.

### 4.5 Leak incident runbook

1. **Contain:** revoke the exposed credential, disable affected sessions or signing authority, isolate a compromised workload if necessary.
2. **Preserve evidence:** retain access logs, relevant timestamps, affected commit/build IDs, and audit events in a restricted location. Do not copy the secret into the incident ticket.
3. **Assess scope:** identify permissions, environments, accessible data, downstream credentials, and possible persistence; search for use during the exposure window.
4. **Recover:** issue replacement credentials, redeploy consumers, verify access with the new identity, and confirm old credentials fail.
5. **Eradicate copies:** remove from source and history as appropriate; purge caches/artifacts/logs where feasible and coordinate with repository hosts and downstream consumers. Assume external copies may persist.
6. **Monitor:** watch for anomalous use, new keys/users, permission changes, unusual exports, and billing spikes.
7. **Learn:** record root cause, time to revoke, affected assets, and preventive tests/controls. Run a rotation drill before the next incident.

For a suspected signing-key compromise, treat artifacts signed during the affected interval as potentially untrusted and follow a documented revocation/re-signing policy. For an encryption-key compromise, assess both access to ciphertext and whether plaintext or DEKs were also exposed.

---

## 5. Hands-on lab: `secretkit`

This lab creates a small, testable module with a fail-fast configuration loader, secret redaction, secure token generation, AES-GCM field encryption, and HMAC verification. It deliberately uses generated keys and test secrets only. It is an educational starting point, not a complete production secrets platform.

### 5.1 Setup

Use Python 3.11+ for the examples. `cryptography` supports multiple Python versions depending on its current release; install a version compatible with your runtime and lock it in your project. The code below uses standard library features plus `cryptography` and `argon2-cffi` for the password-hashing exercise.

```bash
python -m venv .venv
# Linux/macOS
. .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install cryptography argon2-cffi pytest
```

Create `secretkit.py`:

```python
"""Small defensive examples for secrets and authenticated data."""
from dataclasses import dataclass, field
import hashlib
import hmac
import json
import os
import secrets
import stat

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


@dataclass(frozen=True)
class SecretValue:
    _value: str = field(repr=False)

    def __repr__(self) -> str:
        return "SecretValue([REDACTED])"

    def __str__(self) -> str:
        return "[REDACTED]"

    def reveal_for_use(self) -> str:
        return self._value


@dataclass(frozen=True)
class Settings:
    provider_api_key: SecretValue

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "Settings":
        source = os.environ if env is None else env
        value = source.get("PROVIDER_API_KEY")
        if not value:
            raise RuntimeError("Required setting PROVIDER_API_KEY is missing")
        return cls(provider_api_key=SecretValue(value))

    @classmethod
    def from_secret_provider(cls, get_secret) -> "Settings":
        """Accept a provider adapter; the adapter must enforce its own access policy."""
        value = get_secret("provider-api-key")
        if not isinstance(value, str) or not value:
            raise RuntimeError("Required secret provider-api-key is missing")
        return cls(provider_api_key=SecretValue(value))


def check_secret_file_permissions(path: str) -> None:
    """Conservative POSIX check; use Windows ACL APIs on Windows."""
    if os.name != "posix":
        raise NotImplementedError("Use a Windows ACL-aware permission check")
    info = os.stat(path, follow_symlinks=False)
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise PermissionError("Secret path must be a regular file, not a link")
    mode = stat.S_IMODE(info.st_mode)
    if mode & 0o077:
        raise PermissionError("Secret file has unsafe group/other permissions, including readable or writable access")


def new_bearer_token(nbytes: int = 32) -> str:
    if nbytes < 32:
        raise ValueError("Use at least 32 random bytes for this token")
    return secrets.token_urlsafe(nbytes)


password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string")
    return password_hasher.hash(password)


def verify_password(encoded_hash: str, candidate: str) -> bool:
    try:
        return password_hasher.verify(encoded_hash, candidate)
    except VerificationError:
        return False


def password_hash_needs_upgrade(encoded_hash: str) -> bool:
    return password_hasher.check_needs_rehash(encoded_hash)


@dataclass(frozen=True)
class EncryptedField:
    key_id: str
    nonce: bytes
    ciphertext: bytes


class FieldCipher:
    def __init__(self, keys: dict[str, bytes], active_key_id: str) -> None:
        if active_key_id not in keys:
            raise ValueError("Active key ID is not configured")
        for key_id, key in keys.items():
            if not isinstance(key_id, str) or not key_id:
                raise ValueError("Each key needs a non-empty ID")
            if not isinstance(key, bytes) or len(key) != 32:
                raise ValueError("Each key must be a 32-byte AES-256 key")
        self._keys = dict(keys)
        self._active_key_id = active_key_id

    def encrypt_field(self, plaintext: bytes, *, tenant_id: str,
                      record_id: str, field_name: str) -> EncryptedField:
        nonce = os.urandom(12)
        aad = self._aad(tenant_id, record_id, field_name)
        ciphertext = AESGCM(self._keys[self._active_key_id]).encrypt(
            nonce, plaintext, aad
        )
        return EncryptedField(self._active_key_id, nonce, ciphertext)

    @staticmethod
    def _aad(tenant_id: str, record_id: str, field_name: str) -> bytes:
        return json.dumps(
            ["v1", tenant_id, record_id, field_name],
            ensure_ascii=False, separators=(",", ":"),
        ).encode("utf-8")

    def decrypt_field(self, item: EncryptedField, *, tenant_id: str,
                      record_id: str, field_name: str) -> bytes:
        key = self._keys.get(item.key_id)
        if key is None:
            raise ValueError("Unknown encryption key ID")
        aad = self._aad(tenant_id, record_id, field_name)
        try:
            return AESGCM(key).decrypt(item.nonce, item.ciphertext, aad)
        except InvalidTag:
            # Do not leak whether the key, ciphertext, or AAD was wrong.
            raise ValueError("Encrypted field authentication failed") from None


def make_webhook_tag(raw_body: bytes, secret: bytes) -> str:
    """Test/helper implementation for the lesson's HMAC-SHA-256 protocol."""
    return hmac.new(secret, raw_body, hashlib.sha256).hexdigest()


def verify_webhook(raw_body: bytes, supplied_hex_tag: str, secret: bytes) -> bool:
    if not isinstance(supplied_hex_tag, str) or len(supplied_hex_tag) != 64:
        return False
    try:
        supplied = bytes.fromhex(supplied_hex_tag)
    except ValueError:
        return False
    if len(supplied) != hashlib.sha256().digest_size:
        return False
    expected = hmac.new(secret, raw_body, hashlib.sha256).digest()
    return hmac.compare_digest(expected, supplied)


def verify_webhook_event(
    raw_body: bytes,
    supplied_hex_tag: str,
    secret: bytes,
    *,
    timestamp: int,
    event_id: str,
    now: int,
    claim_event_once,
    max_skew_seconds: int = 300,
) -> bool:
    """Illustrative timestamp+body protocol with an atomic replay-store callback."""
    if (not isinstance(timestamp, int) or isinstance(timestamp, bool)
            or not isinstance(now, int) or isinstance(now, bool)
            or max_skew_seconds <= 0
            or abs(now - timestamp) > max_skew_seconds
            or not isinstance(event_id, str) or not event_id or len(event_id) > 200):
        return False
    if not isinstance(supplied_hex_tag, str) or len(supplied_hex_tag) != 64:
        return False
    try:
        supplied = bytes.fromhex(supplied_hex_tag)
    except ValueError:
        return False
    signed = str(timestamp).encode("ascii") + b"." + raw_body
    expected = hmac.new(secret, signed, hashlib.sha256).digest()
    if len(supplied) != len(expected) or not hmac.compare_digest(expected, supplied):
        return False
    # Must atomically return False if this event ID has already been claimed.
    return bool(claim_event_once(event_id, now + max_skew_seconds))
```

The `FieldCipher` is intentionally in-memory: the `keys` dictionary must not be populated with source-code constants in a real service. Retrieve keys through a managed secret/KMS interface and ensure access to the object is restricted. Its AAD uses an unambiguous JSON array encoding so field values containing delimiters cannot collapse into the same context string. The `InvalidTag` handling produces a generic error for callers; internal monitoring may count failures without recording plaintext or key material. `check_secret_file_permissions` is POSIX-only, rejects symlinks and non-regular files, and conservatively rejects any group/other mode bits. It is not a substitute for checking parent-directory permissions, ownership, ACLs, mount options, or access-control races. Windows requires an ACL-aware implementation.

### 5.2 Tests

Create `test_secretkit.py`:

```python
import hashlib
import hmac
import logging

import pytest

from secretkit import (
    EncryptedField,
    FieldCipher,
    SecretValue,
    Settings,
    check_secret_file_permissions,
    new_bearer_token,
    make_webhook_tag,
    verify_webhook,
    hash_password,
    verify_password,
    password_hash_needs_upgrade,
    verify_webhook_event,
)


def test_missing_secret_fails_with_a_non_sensitive_error(monkeypatch):
    monkeypatch.delenv("PROVIDER_API_KEY", raising=False)
    with pytest.raises(RuntimeError) as exc:
        Settings.from_env()
    assert str(exc.value) == "Required setting PROVIDER_API_KEY is missing"


def test_secret_provider_stub_is_supported():
    settings = Settings.from_secret_provider(lambda name: "fixture-secret")
    assert repr(settings.provider_api_key) == "SecretValue([REDACTED])"
    assert "fixture-secret" not in repr(settings)
    assert "fixture-secret" not in str(settings)
    with pytest.raises(RuntimeError, match="missing"):
        Settings.from_secret_provider(lambda name: None)


def test_secret_repr_and_str_are_redacted(caplog):
    secret = SecretValue("fixture-secret-never-use-in-production")
    assert "fixture-secret-never-use-in-production" not in repr(secret)
    assert "fixture-secret-never-use-in-production" not in str(secret)
    logger = logging.getLogger("secretkit.test")
    with caplog.at_level(logging.INFO):
        logger.info("configured credential=%s", secret)
    assert "fixture-secret-never-use-in-production" not in caplog.text
    assert "[REDACTED]" in caplog.text


def test_secret_file_permissions_reject_world_readable_file(tmp_path):
    import os
    if os.name != "posix":
        pytest.skip("POSIX mode bits do not represent Windows ACLs")
    path = tmp_path / "secret.txt"
    path.write_text("test-only-value", encoding="utf-8")
    path.chmod(0o644)
    with pytest.raises(PermissionError, match="readable"):
        check_secret_file_permissions(str(path))
    path.chmod(0o600)
    check_secret_file_permissions(str(path))
    path.chmod(0o660)
    with pytest.raises(PermissionError, match="permissions"):
        check_secret_file_permissions(str(path))
    path.chmod(0o600)
    link = tmp_path / "secret-link"
    link.symlink_to(path)
    with pytest.raises(PermissionError, match="regular file"):
        check_secret_file_permissions(str(link))


def test_token_has_sufficient_encoded_length_and_is_not_reused():
    first = new_bearer_token()
    second = new_bearer_token()
    assert len(first) >= 40
    assert first != second
    with pytest.raises(ValueError):
        new_bearer_token(16)


def test_aes_gcm_round_trip_and_context_binding():
    key = __import__("secrets").token_bytes(32)
    cipher = FieldCipher({"key-v1": key}, "key-v1")
    item = cipher.encrypt_field(b"private payload", tenant_id="tenant-a",
                                record_id="record-1", field_name="email")
    assert cipher.decrypt_field(item, tenant_id="tenant-a", record_id="record-1",
                                field_name="email") == b"private payload"
    with pytest.raises(ValueError, match="authentication failed"):
        cipher.decrypt_field(item, tenant_id="tenant-b", record_id="record-1",
                             field_name="email")


def test_aes_gcm_aad_fields_cannot_collide_on_delimiters():
    key = __import__("secrets").token_bytes(32)
    cipher = FieldCipher({"key-v1": key}, "key-v1")
    item = cipher.encrypt_field(b"private payload", tenant_id="a|b",
                                record_id="c", field_name="f")
    with pytest.raises(ValueError, match="authentication failed"):
        cipher.decrypt_field(item, tenant_id="a", record_id="b|c", field_name="f")


def test_aes_gcm_tampering_is_rejected():
    key = __import__("secrets").token_bytes(32)
    cipher = FieldCipher({"key-v1": key}, "key-v1")
    item = cipher.encrypt_field(b"private payload", tenant_id="t", record_id="r",
                                field_name="f")
    changed = bytearray(item.ciphertext)
    changed[0] ^= 1
    tampered = EncryptedField(item.key_id, item.nonce, bytes(changed))
    with pytest.raises(ValueError, match="authentication failed"):
        cipher.decrypt_field(tampered, tenant_id="t", record_id="r", field_name="f")


def test_hmac_verification_accepts_valid_and_rejects_tampered_body():
    secret = b"test-only-webhook-secret"
    body = b'{"event":"report.ready","id":"evt-test-1"}'
    tag = make_webhook_tag(body, secret)
    assert verify_webhook(body, tag, secret)
    assert verify_webhook(body, tag.upper(), secret)
    assert not verify_webhook(body + b" ", tag, secret)
    assert not verify_webhook(body, "not-a-tag", secret)
    assert not verify_webhook(body, tag, b"wrong-test-secret")
    assert not verify_webhook(body, "g" * 64, secret)


def test_webhook_timestamp_and_replay_are_enforced():
    secret = b"test-only-webhook-secret"
    body = b'{"event":"report.ready","id":"evt-test-2"}'
    now = 1_800_000_000
    event_id = "evt-test-2"
    tag = hmac.new(secret, str(now).encode("ascii") + b"." + body,
                   hashlib.sha256).hexdigest()
    seen = set()

    def claim_event_once(candidate_id, expires_at):
        # Unit-test stub only; production must implement this atomically with TTL.
        if candidate_id in seen:
            return False
        seen.add(candidate_id)
        return True

    args = dict(timestamp=now, event_id=event_id, now=now,
                claim_event_once=claim_event_once)
    assert verify_webhook_event(body, tag, secret, **args)
    assert not verify_webhook_event(body, tag, secret, **args)  # replay
    stale_timestamp = now - 1000
    stale_tag = hmac.new(secret, str(stale_timestamp).encode("ascii") + b"." + body,
                         hashlib.sha256).hexdigest()
    stale_args = {**args, "timestamp": stale_timestamp}
    assert not verify_webhook_event(body, stale_tag, secret, **stale_args)


def test_argon2_password_hash_verification_and_upgrade():
    from argon2 import PasswordHasher

    old_hasher = PasswordHasher(time_cost=1, memory_cost=8192, parallelism=1)
    old_hash = old_hasher.hash("test-only passphrase")
    assert password_hash_needs_upgrade(old_hash)
    upgraded_hash = hash_password("test-only passphrase")
    assert verify_password(upgraded_hash, "test-only passphrase")
    assert not verify_password(upgraded_hash, "incorrect test passphrase")
    assert not password_hash_needs_upgrade(upgraded_hash)
```

Remove the unused `InvalidTag` import from the test if your linter flags it; it is not required for the assertions. The tests generate ephemeral encryption keys and use clearly marked test-only webhook material. They do not contact external services or use real credentials.

Run:

```bash
python -m pytest -q
```

Expected result if dependencies install and the files match the snippets: **11 tests pass**. This is an expected result, not a claim that tests were run in your environment. The token collision assertion is a sanity check, not a proof of randomness; security depends on the `secrets` implementation and sufficient entropy.

### 5.3 Lab extensions

1. Add a `doctor` command that reports whether a required variable is present without printing it. On POSIX, check secret-file permissions and reject group/world-readable files when policy requires; document that Windows ACLs need a platform-specific implementation rather than a POSIX mode-bit check.
2. Add an encrypted-record storage format with version, key ID, nonce, ciphertext, and documented AAD. Do not serialize raw key bytes into the record.
3. Add a key-rotation test: ciphertext created with an old key remains decryptable while that key is explicitly in the read key ring; new ciphertext uses the active key. Then test removal of the old key and expected failure.
4. Extend webhook verification with a provider-style timestamp and event ID. Reject timestamps outside the allowed window and use an atomic, TTL-bounded replay store for event IDs. A unit test using an in-memory set is a teaching model; production needs concurrency-safe storage.
5. Add secret-scanning CI and a documented exception policy. Test the pipeline with a deliberately fake marker that cannot be mistaken for a usable credential; do not commit actual secrets.
6. Add tests that assert secrets are absent from logs, exceptions, serialized settings, notebook outputs, and generated reports.

---

## 6. Common mistakes and trade-offs

| Mistake | Why it fails | Better approach |
|---|---|---|
| Committing `.env` or notebook output | Git history and copies persist | Revoke/rotate first, then clean history and add scanning |
| Using `random` for a reset token | PRNG is not designed for secrets | `secrets.token_urlsafe(32)` or a vetted generator |
| `sha256(password)` | Too fast for offline guessing | Argon2id/scrypt/bcrypt with tuned parameters |
| Treating hash as encryption | Original data cannot be recovered | Use AEAD for confidentiality plus integrity |
| Using encryption without authentication | Tampering may go undetected | AEAD such as AES-GCM or ChaCha20-Poly1305 |
| Reusing a GCM nonce with the same key | Can catastrophically undermine confidentiality/authentication | Unique nonce per encryption and per-key usage limits |
| Using `==` for a MAC tag | May expose timing differences | `hmac.compare_digest` |
| Trusting JWT payload because signature passed | Claims may be for another audience or expired | Validate issuer, audience, expiry, required claims, scopes, and algorithm policy |
| Putting sensitive data in a JWT | Signed payloads are normally readable | Store minimal claims; use a separately designed encryption scheme only if needed |
| Setting `verify=False` | Removes server identity verification | Fix trust-store, certificate, hostname, or proxy configuration |
| Treating `.env` as a production vault | File and process exposure remain | Secret manager/workload identity and least privilege |
| Storing ciphertext and key together | One compromise exposes both | Separate KMS/wrapped keys and access boundaries |
| Assuming key rotation is just changing config | Old ciphertext/consumers may still depend on the old key | Key IDs, migration plan, audit, bounded overlap, revocation tests |
| Logging whole HTTP requests for debugging | Headers/URLs/body may contain credentials | Log safe structured fields and test redaction |
| Assuming zeroisation is guaranteed in Python | Copies and allocator/runtime behavior remain | Minimise lifetime and exposure; isolate sensitive work |

### 6.1 Advanced crypto pitfalls and awareness

- **ECB mode** reveals repeated-block patterns and should not be used for general application data. Prefer AEAD.
- **CBC without a correctly designed authentication construction** is malleable and can create padding-oracle vulnerabilities. Do not hand-compose encrypt-then-MAC protocols; use an AEAD library.
- **MAC-then-encrypt and custom composition** are protocol-design hazards. Follow a reviewed protocol or library API rather than selecting an order yourself.
- **Fixed IVs/nonces, nonce reuse, and homemade key derivation** can invalidate security assumptions. Use the algorithm's documented nonce rules and a vetted KDF.
- **Truncated hashes** are not automatically suitable MACs or identifiers; choose a reviewed construction with an appropriate output length and threat model.
- **RSA encryption padding:** do not introduce new RSA PKCS#1 v1.5 encryption designs. Use a vetted protocol and modern padding such as OAEP where RSA encryption is specifically required. For signatures, follow a modern library-supported signature scheme and protocol policy.
- **Timing and side channels:** use constant-time comparison helpers for MACs; do not write custom cryptographic primitives or assume Python code is constant-time. Delegate primitives to audited libraries.
- **FIPS and compliance:** a FIPS requirement applies to the validated cryptographic module, configuration, deployment, and operating procedures—not merely to choosing a named algorithm. Confirm the exact platform and validation requirements with your security/compliance team.
- **Post-quantum awareness:** long-lived confidentiality may face “harvest now, decrypt later” risk. Track standards and supported library/platform roadmaps for post-quantum key establishment and signatures; do not implement ML-KEM, ML-DSA, or hybrid protocols yourself.
- **Pseudonymisation is not anonymisation:** hashing or replacing identifiers may remain reversible, linkable, or vulnerable to guessing when the input space is small. Treat pseudonymised data according to its re-identification risk and applicable policy.
- **Detection:** canary credentials/tokens and anomaly alerts can reveal unexpected use, but they must be isolated, monitored, and designed so the detector itself does not create a new secret exposure.

### 6.2 Operational trade-offs

- **Secret manager vs environment variable:** a manager improves access policy, audit, rotation, and central control but adds availability and operational dependencies. Use workload identity where possible and define safe startup/failure behavior.
- **Short-lived credentials vs long-lived keys:** short-lived credentials reduce exposure windows but require reliable identity exchange and refresh behavior.
- **Per-record keys vs shared data key:** per-record keys can narrow blast radius but add KMS and metadata overhead. Choose based on volume, tenancy, and recovery requirements.
- **Re-encrypt vs retain old key:** re-encryption simplifies long-term retirement but costs compute and can create migration risk; retaining old keys increases long-term exposure. Document and time-box the decision.
- **Certificate pinning vs CA validation:** pinning may constrain trust in specialised environments but creates rotation/outage risks. Normal certificate and hostname validation is the default.

---

## 7. Testing, review, and CI policy

### 7.1 Required security tests

- Missing required secret fails closed without exposing the value.
- `repr`, `str`, logs, exceptions, and serialized configuration redact secrets.
- Token generation uses a CSPRNG and enforces a minimum entropy policy.
- AEAD round trip succeeds; ciphertext, nonce, key ID, or AAD tampering fails closed. Never write a test that reuses a nonce as a usable encryption pattern.
- HMAC accepts a correct tag and rejects changed body, malformed tag, wrong secret, stale timestamp, and replayed event ID where the protocol supports those checks.
- Password verification rejects wrong passwords and supports rehash-on-login after cost-policy changes.
- JWT tests reject wrong issuer/audience, expired tokens, missing required claims, unexpected algorithm, and invalid signatures.
- TLS integration tests verify hostname/certificate failures with a local test CA; never disable verification to make tests pass.
- Key-rotation tests cover old-key reads, new-key writes, missing key IDs, and revocation behavior.

### 7.2 Example dependency setup

For a project using `uv`, a typical starting point is:

```bash
uv add cryptography argon2-cffi "PyJWT[crypto]"
uv add --dev pytest detect-secrets pre-commit
```

Review and lock versions, scan dependencies with your project's SCA tooling, and test upgrades in CI. Use `pip-audit` or an equivalent dependency vulnerability scanner. `cryptography`, OpenSSL bindings, JWT libraries, and SSH/TLS libraries are security-sensitive dependencies; track supported versions and advisories.

### 7.3 Pre-commit and CI principles

- Scan commits and pull requests; fail on confirmed secrets unless a narrowly reviewed false-positive exception is documented.
- Run unit/security regression tests, static analysis, dependency audit, and artifact-signature verification.
- Do not expose production credentials to untrusted build code. Secret scanners and PR workflows themselves should not echo full matching lines into public logs.
- Scope exceptions to a path/rule/finding, name an owner, record a reason and expiry/review date, and keep them visible. Never blanket-disable secret scanning because a legacy repository is noisy.
- Baseline old findings only after triage; make new findings fail the gate where feasible. Monitor the baseline for stale or unjustified entries.

### 7.4 Code-review checklist

- [ ] No real secret in source, tests, notebooks, fixtures, command history, image layers, or logs.
- [ ] Credentials are scoped, environment-specific, owned, expiring, and revocable.
- [ ] No secret-bearing URLs, headers, exception text, `repr`, or diagnostic dumps.
- [ ] Security tokens use `secrets` or a vetted library and have expiry/revocation policy.
- [ ] Passwords use a password KDF with tuned cost, unique salts, and rate limiting/MFA.
- [ ] AEAD keys are separated from data; nonce uniqueness and AAD are documented and tested.
- [ ] MAC verification uses exact protocol bytes and constant-time comparison; replay protections are present when required.
- [ ] Signature verification uses trusted key distribution and a documented signer-authorization policy.
- [ ] JWT algorithms and claims are explicitly validated; tokens contain minimal non-sensitive claims.
- [ ] TLS certificate and hostname verification remain enabled.
- [ ] Key rotation, incident response, and audit events are documented and tested.

---

## 8. Self-check questions with answers

### Q1. A key was pushed to a public repository five minutes ago. What do you do, in order?

**Answer:** Revoke/rotate the key immediately and alert the owner/security team; assess access scope and audit use; replace it in consumers and verify the new key; remove it from the working tree and coordinate history cleanup; purge feasible caches/artifacts and notify downstream consumers; monitor for misuse; document root cause and add preventive controls. History rewriting alone is not containment.

### Q2. Why is AES-GCM nonce reuse dangerous?

**Answer:** GCM's security depends on nonce uniqueness under a given key. Reuse can expose relationships between plaintexts and undermine authentication, enabling forgery. Generate unique nonces, track usage limits, and rotate keys according to a reviewed design.

### Q3. How should password hashing and upgrade-on-login work?

**Answer:** Hash with Argon2id (or an appropriate scrypt/bcrypt configuration) using library-managed random salts and tuned cost parameters. Verify using the library's verifier; rate-limit login attempts. After successful verification, check whether the encoded hash's parameters need an upgrade and rehash the candidate password with current settings if so. Never compare passwords by hashing with plain SHA-256.

### Q4. Is a SHA-256 digest enough to prove who published a model artifact?

**Answer:** No. Anyone who can replace the artifact can calculate a new digest. Use a digital signature verified against a trusted public key and signed metadata/provenance, and still scan and safely load the artifact.

### Q5. Does a valid JWT signature prove the token should be accepted?

**Answer:** No. Verify an allowed algorithm and trusted key, then validate issuer, audience, expiry, required claims, subject, scopes/roles, and revocation/session policy. A signed JWT payload is not inherently confidential.

### Q6. Why is `verify=False` not an acceptable fix for TLS errors?

**Answer:** It removes certificate/hostname verification and permits an attacker to impersonate the endpoint. Correct the trust store, hostname, certificate chain, clock, proxy, or server configuration instead.

### Q7. Why does HMAC not prevent webhook replay?

**Answer:** The same valid body/tag remains valid when resent. Bind a timestamp or event ID into the signed bytes when the provider protocol supports it, enforce a freshness window, and atomically reject duplicate event IDs.

### Q8. What is the difference between a nonce, a salt, and a key?

**Answer:** A key is secret cryptographic material. A nonce is a per-operation value with algorithm-specific rules, often required to be unique but not secret. A salt is public random input that makes password hashes unique and costly to precompute. They are not interchangeable.

---

## 9. Completion checklist and module-project connection

### Lesson completion

- [ ] I can describe secret sources, scope, ownership, expiry, delivery, rotation, and revocation.
- [ ] `.env`, notebooks, build artifacts, CI logs, and generated outputs are covered by a realistic scanning and hygiene policy.
- [ ] I know to revoke/rotate a committed secret before rewriting history.
- [ ] Secret representations, logs, URLs, exceptions, and diagnostics are redacted and tested.
- [ ] I can distinguish hashes, password KDFs, MACs, AEAD, signatures, key derivation, and TLS.
- [ ] Password storage uses a vetted password KDF, salts, tuned cost, rate limiting, and MFA where appropriate.
- [ ] Tokens use secure randomness; encryption uses a vetted AEAD and documented nonce/AAD/key lifecycle.
- [ ] HMAC verification uses the exact protocol bytes, constant-time comparison, and replay protection where applicable.
- [ ] Artifact signatures are verified against a trusted key and provenance policy.
- [ ] JWTs are validated beyond signature verification; TLS certificate and hostname checks remain enabled.
- [ ] Key rotation and incident-response procedures are written and tested.
- [ ] The lab tests cover missing secrets, redaction, token generation, AEAD round-trip, tampering, and HMAC verification.

### `vulnpy` module mini-project connection

For the Module 1.22 project, use this lesson to remediate hard-coded credentials and leaked Git history, weak password hashing, missing token validation, insecure TLS settings, and secrets in logs or notebook outputs. Add regression tests per finding and ensure CI blocks new secret leaks. Document residual risks, owners, and rotation procedures in `HARDENING_REPORT.md`, `SECURITY.md`, and the incident-response runbook. The broader project also requires a threat model, safe storage/HTTP/subprocess controls, static analysis, dependency scanning, and local-only exploit-and-fix demonstrations. Do not claim the whole `vulnpy` project is complete merely because this lesson's lab passes.

**Next:** Lesson 06 — `06-ssrf-and-safe-http-clients.md`.
