# `hashlib`, `hmac`, `secrets`, and `uuid`: Integrity, Authentication, and Identifiers

> **Roadmap position:** Stage 1 — Programming & Computational Thinking → Module 13, Standard Library Toolkit → Phase C, Security Primitives and Numbers → Lesson 06.  
> **Target:** Python 3.12+. Version-specific features are labelled.  
> **Scope:** Python's standard-library primitives and their correct boundaries—not a cryptography course and not a substitute for a reviewed cryptographic protocol.

## Learning objectives

By the end, you should be able to:

- Explain the difference between hashing, authentication, secure random generation, and identifiers.
- Hash large files with bounded memory and verify content digests correctly.
- Produce reproducible fingerprints for structured records without confusing them with signatures or privacy guarantees.
- Create and verify HMAC-SHA-256 tags safely, including webhook verification over the exact raw request bytes.
- Generate unpredictable tokens with `secrets` and select UUID versions for random or deterministic identifiers.
- Explain password hashing, salts, peppers, entropy, collision risks, length-extension attacks, and replay protection.
- Test cryptographic plumbing and edge cases without claiming that unit tests prove a design secure.
- Recognize when to use a dedicated cryptographic library and when to obtain a formal security review.

## Prerequisites and boundaries

This lesson assumes familiarity with bytes versus text, file handling with `pathlib` and binary mode, JSON serialization, exception handling, functions, `datetime`, environment-based configuration, input validation, and `pytest` fixtures such as `tmp_path`. Earlier Stage 1 lessons cover these foundations, plus idempotency and safe file writes.

The Module 13 roadmap puts this lesson after local file/process/database work and before reproducible randomness/statistics. The goal is to use the standard library correctly in data pipelines, ingestion jobs, local tooling, integrity checks, authentication tags, and identifier design.

**Not in scope:** implementing encryption, TLS, password protocols, key exchange, digital signatures, or a complete webhook protocol from scratch. For encryption, public-key signatures, certificate handling, and protocol-level cryptography, prefer a maintained specialist library such as `cryptography` and follow the relevant protocol/provider guidance.

---

## 1. The four jobs are different

| Primitive | Question it answers | Typical tool | Does not provide by itself |
|---|---|---|---|
| Cryptographic hash | “What digest corresponds to these bytes?” | `hashlib.sha256` | Sender identity, secrecy, or proof that data is trusted |
| Keyed message authentication | “Was this message tagged by someone holding this shared key, and was it changed?” | `hmac` | Encryption, non-repudiation, or replay prevention |
| Secure random token | “Can an attacker feasibly guess this bearer secret?” | `secrets` | Identity or authorization policy by itself |
| Identifier | “How do I refer to this entity?” | `uuid` | Authentication, secrecy, or guaranteed global uniqueness |

These primitives can be combined in an application, but they are not interchangeable. A SHA-256 digest of an attacker-controlled file can detect accidental or unexpected changes only when the expected digest comes from a trusted source. If an attacker can replace both the file and the digest, the comparison proves little.

### Threat-model checklist

Before selecting a primitive, identify:

1. **Asset:** file bytes, event body, password, API token, or record identity.
2. **Adversary:** accidental corruption, a network attacker, a malicious tenant, a database reader, or a party able to modify both data and metadata.
3. **Required property:** reproducibility, collision resistance, authenticity, unpredictability, confidentiality, or privacy.
4. **Trust anchor:** trusted expected digest, secret HMAC key, password verifier, or namespace identifier.
5. **Lifecycle:** rotation, expiration, revocation, replay handling, key access, logging, and deletion.

A primitive is only one part of the control. For example, HMAC verification does not decide whether a webhook event is authorized, recent, unique, or safe to process.

## 2. Hashes and digests: beginner foundations

### 2.1 What a cryptographic hash does

A cryptographic hash maps an input of arbitrary length to a fixed-size digest (except extendable-output functions such as SHAKE). For the same algorithm and bytes, the result is deterministic. A secure hash aims to make it computationally infeasible to find a preimage, a second preimage, or a collision, subject to the algorithm's security properties and output size.

```python
import hashlib

payload = b"batch=2026-10-17"
digest = hashlib.sha256(payload).digest()       # raw bytes, 32 bytes
hex_digest = hashlib.sha256(payload).hexdigest()  # 64 hexadecimal characters

print(len(digest))
print(len(hex_digest))
print(hex_digest == hashlib.sha256(payload).hexdigest())
```

Expected output:

```text
32
64
True
```

`digest()` is useful for binary protocols and internal composition. `hexdigest()` is convenient for logs, manifests, JSON, and command-line tools. Hexadecimal is an encoding of the digest, not a stronger digest. A SHA-256 hex string is 64 characters because each byte is represented by two hex digits.

**Use cases:** checking a downloaded artifact against a trusted manifest, content-addressable storage, detecting unexpected changes, and reproducible record fingerprints.  
**Trade-off:** hashing is fast and deterministic; it does not prove who produced the input.  
**Application example:** an ingestion job stores a SHA-256 digest beside a source file version to avoid processing identical bytes twice, while its trust policy obtains the expected digest from a trusted channel.

### 2.2 Choosing an algorithm

- **SHA-256 (`hashlib.sha256`)**: strong default for fixed-size collision-resistant digests, file checksums, fingerprints, and HMAC-SHA-256.
- **SHA-3 (`sha3_256`, `sha3_512`)**: standardized SHA-3 family with different internal construction from SHA-2. Use when required by policy or interoperability, or when its properties are specifically desired.
- **BLAKE2 (`blake2b`, `blake2s`)**: fast modern hash family. Python exposes keyed mode and configurable digest size; use keyed BLAKE2 only when its semantics are appropriate and documented for the protocol. Do not silently substitute it where an external protocol specifies HMAC-SHA-256.
- **SHAKE (`shake_128`, `shake_256`)**: extendable-output functions. Call `digest(length)` or `hexdigest(length)` with an explicit requested output length. They do not have one fixed digest length.
- **MD5 and SHA-1**: collision attacks make them unsuitable for modern collision-resistant security uses, such as adversarial integrity or digital-signature contexts. They can still occur in legacy protocols or non-adversarial caches/checksums where compatibility is mandatory and an attacker cannot exploit collisions. Prefer SHA-256 for new general-purpose checksum designs. Do not describe MD5/SHA-1 checksums as secure against a malicious party.

```python
import hashlib

print(hashlib.sha256(b"data").hexdigest())
print(len(hashlib.blake2b(b"data", digest_size=20).digest()))
print(len(hashlib.sha3_256(b"data").digest()))
print(len(hashlib.shake_256(b"data").digest(24)))  # caller requests 24 bytes
```

The availability of algorithms may depend on the Python build and linked cryptographic provider. Check `hashlib.algorithms_available` when portability across constrained environments matters; do not use that set as a policy for deciding which algorithms are secure.

### 2.3 Integrity checksum versus security control

A hash can detect changed bytes when the expected digest is trusted. It does not authenticate the source, hide content, or prevent an attacker from calculating a new digest after modifying the content. Use a digital signature or a keyed MAC when the threat model requires authenticity and the protocol calls for it. A MAC key must remain secret; a public-key signature has a different trust and key-distribution model.

A checksum also does not guarantee the file is safe to parse. Verify integrity, then still validate structure, size, encoding, schema, and application-level constraints.

## 3. Hash files incrementally

### 3.1 Chunked hashing with bounded memory

Read a file in binary chunks. Memory use is bounded by the chunk buffer rather than the total file size.

```python
from pathlib import Path
import hashlib


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the SHA-256 hex digest of a file using bounded memory."""
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")

    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()
```

`update()` can be called repeatedly; the result is equivalent to hashing the concatenation of all chunks in order. The file is opened as `rb` so platform newline conversion and text decoding cannot change the bytes being hashed.

**Why it matters:** loading a multi-gigabyte object into memory just to hash it is unnecessary and can exhaust memory.  
**Trade-off:** chunk size affects I/O overhead and memory footprint, not the digest.  
**Failure handling:** normal file errors such as permission failures and missing paths should be allowed to propagate or be translated at the application boundary; do not return a made-up digest after an error.

### 3.2 `hashlib.file_digest()` (Python 3.11+)

Python 3.11 introduced `hashlib.file_digest(fileobj, digest)`. It is a concise option for a binary file object:

```python
import hashlib

with open("artifact.bin", "rb") as stream:
    digest = hashlib.file_digest(stream, "sha256").hexdigest()
```

Use the file object as binary input. The function may bypass Python-level I/O and the file object's state after the call should be treated as unspecified; do not assume the stream is positioned for another read. On Python 3.10 and earlier, use the explicit chunk loop. The `digest` argument can be an algorithm name or a supported digest constructor/callable as documented for the Python version in use.

### 3.3 Verifying a downloaded file

Obtain the expected digest through a trusted channel. Compare the calculated and expected normalized digest; for ordinary public checksum strings, direct equality is usually fine because the value is not a secret. Validate format and algorithm explicitly. If a digest string itself is an authentication secret, reconsider the design rather than relying on a constant-time comparison to make a public checksum into authentication.

For a hostile file, also consider TOCTOU issues: if another process can replace the file after verification but before use, hash and consume the same open file descriptor or use a controlled immutable staging path.

## 4. Secure randomness and bearer tokens

### 4.1 `secrets` versus `random`

`random` is designed for simulation, sampling, and reproducible pseudorandom sequences. Its output must not be used for passwords, reset links, session identifiers, API credentials, CSRF tokens, or other security-sensitive bearer secrets. Use `secrets`, which draws from the operating system's cryptographically strong randomness source, or APIs explicitly documented for security.

```python
import secrets

hex_token = secrets.token_hex(32)       # 32 random bytes -> 64 hex chars
url_token = secrets.token_urlsafe(32)   # 32 random bytes, URL-safe Base64-like text
alphabet_choice = secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789")
print(len(hex_token))
```

The last output is `64`. The `32` argument is a number of random bytes, not a guarantee that the textual token has 32 characters. URL-safe token length varies with encoding details. If omitted, `nbytes` uses a reasonable default that may change between Python versions; specify it when a token-length policy requires stable entropy.

### 4.2 Entropy and token lifecycle

For an ideal token with `n` uniformly random bits, a blind guess succeeds with probability approximately `2^-n` per independent guess, before accounting for rate limits, leaked tokens, or implementation mistakes. `secrets.token_hex(32)` starts with 256 random bits. Real security also requires:

- sufficient token length and a strong system randomness source;
- secure transport and storage (often store a verifier/hash of a token rather than the raw bearer token);
- expiration, revocation, scoped permissions, and rate limiting;
- avoiding tokens in URLs where logs, referrers, browser history, and analytics may capture them;
- redacting tokens from logs, exceptions, traces, and support tickets.

A token is a bearer credential: anyone who obtains it may be able to use it. A random token does not itself identify a person or grant only appropriate permissions.

### 4.3 `os.urandom()` and secure randomness

`secrets` is the high-level API to prefer. `os.urandom(n)` returns `n` bytes suitable for cryptographic use, as provided by the operating system. Avoid rolling your own entropy collection or calling `random.seed()` to try to make `random` secure. Reproducibility and unpredictability are opposing goals in many workflows.

## 5. UUIDs and identifier design

A UUID is a 128-bit identifier with version- and variant-specific layouts. It is useful for distributed record identifiers where a central sequence allocator is undesirable. UUIDs are identifiers, not credentials: do not assume an ID is secret or use it as the only authorization check.

### 5.1 UUIDv4: random identifier

```python
import uuid

record_id = uuid.uuid4()
print(record_id)
print(record_id.version)  # 4
```

UUIDv4 is appropriate for a new random identifier when collision probability is negligible and the UUID's random source is appropriate. It does not guarantee uniqueness mathematically; systems should still enforce uniqueness with a database constraint where correctness depends on it.

### 5.2 UUIDv5: deterministic identifier

UUIDv5 derives a deterministic UUID from a namespace UUID and a name using SHA-1 as specified by the UUID standard. Same namespace and same name produce the same UUID; different names are not guaranteed collision-free. It is useful for compatibility, deterministic mapping, or migration from a stable external key, but not for secret tokens. SHA-1's role here is a fixed legacy specification for UUIDv5; do not generalize that to security-sensitive SHA-1 use.

```python
import uuid

source_namespace = uuid.uuid5(uuid.NAMESPACE_URL, "https://data.example.test/source/customer")
external_id = "customer-0042"
record_id = uuid.uuid5(source_namespace, external_id)
assert record_id == uuid.uuid5(source_namespace, external_id)
```

Namespace choice and name encoding must be stable. If the source ID has case or Unicode normalization rules, normalize according to the domain contract before creating the UUID. Namespace IDs are part of the identifier scheme; changing them changes every generated UUID.

### 5.3 UUIDv7: time-ordered identifiers (Python 3.14+)

`uuid.uuid7()` was added in Python 3.14. UUIDv7 places a Unix-millisecond timestamp in the high-order bits and includes random/counter bits according to the implementation/specification. This generally improves approximate time ordering and database index locality compared with UUIDv4, but it can reveal creation-time information and is not a strict global ordering guarantee across clocks, hosts, or processes. Do not call it on Python 3.12/3.13 without a compatibility plan. If time-ordering is a hard requirement, document clock behavior and test the chosen library/runtime.

### 5.4 Choosing among them

| Need | Usually consider | Caveats |
|---|---|---|
| New random entity ID | UUIDv4 | Enforce uniqueness at the persistence boundary |
| Repeatable ID from stable namespace + name | UUIDv5 | SHA-1 is part of the standard; not for secrecy/authentication |
| Approximate time-ordered ID | UUIDv7 on Python 3.14+ | Timestamp disclosure; ordering is not globally authoritative |
| Unpredictable one-time secret | `secrets`, not UUID | Add expiry, scope, storage, and revocation policy |
| Content identity | Cryptographic digest, not necessarily UUID | Hash collision and trust assumptions; content may be sensitive |

UUIDv1 and UUIDv6 exist as well, with different time/node layouts. UUIDv1 can expose node-related information and has privacy considerations. Choose a version intentionally rather than treating all UUIDs as equivalent.

## 6. Stable fingerprints for structured records

### 6.1 Canonicalization comes before hashing

A hash function sees bytes, not Python dictionaries. These JSON texts are semantically similar as objects but bytewise different:

```json
{"id":7,"status":"ok"}
{"status": "ok", "id": 7}
```

To create a reproducible fingerprint, define a canonical serialization contract: key ordering, separators, Unicode handling, numeric representation, missing versus `null`, timestamp format/time zone, and normalization rules for domain strings. `json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=False)` is a useful controlled baseline, but it is not a universal canonical JSON standard. Cross-language systems should adopt a documented canonicalization standard such as RFC 8785 where its constraints fit, rather than assuming Python's serializer is universal.

```python
from __future__ import annotations
import hashlib
import json
import math
import unicodedata
from typing import Any


def _validate_json_value(value: Any, path: str = "$", *, normalize_strings: bool = False) -> Any:
    """Validate a JSON-compatible tree and reject non-finite floats."""
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"non-finite float at {path}")
        return value
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value) if normalize_strings else value
    if isinstance(value, list):
        return [_validate_json_value(v, f"{path}[{i}]", normalize_strings=normalize_strings) for i, v in enumerate(value)]
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"JSON object key at {path} must be str")
            canonical_key = unicodedata.normalize("NFC", key) if normalize_strings else key
            if canonical_key in out:
                raise ValueError(f"duplicate key after normalization at {path}")
            out[canonical_key] = _validate_json_value(item, f"{path}.{canonical_key}", normalize_strings=normalize_strings)
        return out
    raise TypeError(f"unsupported value at {path}: {type(value).__name__}")


def canonical_record_bytes(record: dict[str, Any]) -> bytes:
    """Application-specific canonical JSON for a documented record schema."""
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")
    validated = _validate_json_value(record, normalize_strings=True)
    text = json.dumps(
        validated,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return text.encode("utf-8")


def record_fingerprint(record: dict[str, Any]) -> str:
    """Return a reproducible SHA-256 fingerprint, not an authentication tag."""
    return hashlib.sha256(b"record-fingerprint-v1\0" + canonical_record_bytes(record)).hexdigest()
```

This example deliberately rejects unsupported Python values such as `datetime`, `Decimal`, sets, bytes, and custom objects. Convert them through an explicit schema rule first (for example, UTC timestamps in a specified ISO 8601 format and decimals represented as normalized strings or integer minor units). The function normalizes strings to Unicode NFC, which is a domain choice; do not normalize identifiers or opaque values unless the source contract says those values are equivalent. It detects dictionary-key collisions introduced by normalization.

**Why it matters:** deterministic fingerprints help compare records, detect changes, de-duplicate stable payloads, and build incremental pipeline manifests.  
**Trade-off:** canonicalization policy becomes part of the data contract and must be versioned. A change in normalization can change fingerprints.  
**Important:** a plain fingerprint is not secret and does not authenticate a record. Low-entropy personal data may be guessed from its digest.

### 6.2 Fingerprints, identity, and content addressing

A record fingerprint answers “do these canonicalized bytes match?” A business key answers “is this the same real-world entity?” They are not the same. Two valid versions of one customer can have different fingerprints, while two records with equal content can share a fingerprint despite representing different entities.

Content-addressable storage names an object by its digest. This is useful for immutable artifacts and deduplication. A production design must define algorithm/version metadata, verify bytes on read, handle storage races atomically, and consider the negligible-but-not-zero collision risk. For adversarial or high-value content, a digest alone does not prove who published the content; authenticate the manifest or use signatures/MACs as appropriate.

### 6.3 Merkle-style change detection

A Merkle-style design hashes canonical leaf records or partitions, then hashes parent nodes from child digests. If a leaf changes, hashes along its path change; unchanged partitions can be skipped. Real systems must specify stable ordering, leaf boundaries, empty-tree behavior, domain separation (different prefixes for leaf and internal nodes), versioning, and trust in the root digest. A single flat hash cannot identify which region changed without re-reading/re-hashing relevant content. Merkle trees are a design pattern, not a feature automatically supplied by `hashlib`.

## 7. HMAC: message authentication with a shared key

### 7.1 Why HMAC exists

HMAC combines a secret key and a hash function using a standardized construction. It is designed to authenticate messages for parties that share a secret key. Prefer HMAC over invented constructions such as `SHA256(key + message)`: naive prefix hashing can be vulnerable to length-extension attacks for Merkle–Damgård hashes, and custom constructions may have other flaws.

```python
import hashlib
import hmac


def create_hmac_sha256(key: bytes, message: bytes) -> str:
    if not isinstance(key, bytes) or not key:
        raise ValueError("key must be non-empty bytes")
    if not isinstance(message, bytes):
        raise TypeError("message must be bytes")
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def verify_hmac_sha256(key: bytes, message: bytes, supplied_hex: str) -> bool:
    if not isinstance(key, bytes) or not key:
        return False
    if not isinstance(message, bytes) or not isinstance(supplied_hex, str):
        return False
    # Enforce one representation: exactly 64 ASCII hex characters for SHA-256.
    if len(supplied_hex) != 64 or any(c not in "0123456789abcdefABCDEF" for c in supplied_hex):
        return False
    expected = hmac.new(key, message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, supplied_hex.lower())
```

`hmac.compare_digest()` avoids content-dependent short-circuit comparison for supported values and is the appropriate standard-library comparison for MAC/signature strings. It does not make the entire request handler constant-time, hide all timing signals, protect the secret key, or eliminate side channels elsewhere. Validate the tag format first and use a consistent string/bytes type.

A shared-key MAC also does not provide non-repudiation: either party holding the key can create a valid tag. If public verification is required, use an appropriate digital-signature protocol from a reviewed library.

### 7.2 Key management

Use a cryptographically random key generated for the protocol and stored in a secret manager or protected runtime configuration. Do not hard-code production keys, commit them to source control, put them in exception messages, or log them. Keep keys separate by environment and purpose. Establish key IDs, rotation windows, emergency revocation, and an overlap period if old signatures must remain valid during a controlled transition.

A key ID supplied by a message is untrusted input: use it only to select from a bounded local allow-list of active keys. Do not allow the sender to specify a filesystem path, URL, or arbitrary secret-manager lookup key. Keep the key used to verify a message separate from any data-derived fingerprint.

## 8. Webhook verification and replay protection

### 8.1 Verify the exact raw request bytes

Webhook providers commonly sign the exact raw HTTP body. Do not parse JSON and then serialize it again before verifying: whitespace, key order, escapes, and number formatting may differ. The provider's exact signing format (header prefix, digest encoding, timestamp inclusion, and key rotation rules) is authoritative; the following is an illustrative scheme, not a universal provider protocol.

```python
import hashlib
import hmac


def webhook_tag(secret: bytes, timestamp_text: str, raw_body: bytes) -> str:
    """Example protocol: ASCII timestamp + b'.' + exact raw body."""
    if not secret or not isinstance(secret, bytes):
        raise ValueError("secret must be non-empty bytes")
    if not isinstance(timestamp_text, str) or not timestamp_text.isascii() or not timestamp_text.isdigit():
        raise ValueError("timestamp must be decimal ASCII seconds")
    if not isinstance(raw_body, bytes):
        raise TypeError("raw_body must be bytes")
    signed = timestamp_text.encode("ascii") + b"." + raw_body
    return hmac.new(secret, signed, hashlib.sha256).hexdigest()


def verify_webhook(secret: bytes, timestamp_text: str, raw_body: bytes, supplied_hex: str) -> bool:
    if not isinstance(supplied_hex, str) or len(supplied_hex) != 64:
        return False
    if any(c not in "0123456789abcdefABCDEF" for c in supplied_hex):
        return False
    try:
        expected = webhook_tag(secret, timestamp_text, raw_body)
    except (TypeError, ValueError):
        return False
    return hmac.compare_digest(expected, supplied_hex.lower())
```

In an HTTP application, cap body size before buffering, preserve the raw bytes, and parse/validate the payload only after signature verification according to the provider's required order. Avoid logging the body or signature when it may contain personal data or credentials.

### 8.2 Timestamp, nonce, and idempotency

A valid HMAC proves possession of the signing key for the signed bytes. It does **not** prove that the message is fresh. An attacker may replay a previously valid request. A production protocol may sign a timestamp and require a narrow acceptance window, then store an event ID/nonce in durable storage with a uniqueness constraint. Timestamp checks alone do not prevent replay within the window. A nonce without persistent replay state is also insufficient across restarts or multiple workers.

Recommended flow (adapt to provider documentation):

1. Enforce request-size and header-format limits.
2. Resolve a known key ID from an allow-list; optionally verify during a bounded key-rotation overlap.
3. Verify HMAC over the provider-defined exact bytes using `compare_digest`.
4. Parse timestamp and reject messages outside a carefully chosen clock-skew window.
5. Validate event schema and authorization rules.
6. Insert event ID into a durable deduplication table in the same transaction as the business effect, or use a durable idempotency mechanism.
7. Return a response according to the provider's retry contract. Ensure processing and acknowledgement semantics are explicit.

Do not invent header names or signing input for a real provider. Follow the provider's documented scheme and test with its published vectors.

## 9. Password storage: hashing is not enough

Passwords are low-entropy human-chosen secrets. A fast general-purpose hash such as SHA-256 allows attackers to test guesses very quickly. Store a password verifier produced by a password-hashing/KDF scheme with a unique salt and configurable cost, not `sha256(password)`.

Standard-library options include:

- `hashlib.scrypt`: memory-hard password-based key derivation; tune and benchmark parameters for the deployment and threat model.
- `hashlib.pbkdf2_hmac`: standardized password-based derivation, available in the standard library; use a suitable iteration count, salt, and stored algorithm/parameter metadata. Policy guidance evolves; select parameters using current organizational guidance rather than copying a stale number blindly.
- Dedicated password libraries such as Argon2 (`argon2-cffi`) or bcrypt are often preferable because they provide password-specific APIs, encodings, and established operational patterns. Argon2id is commonly recommended where available. Follow current specialist guidance and framework support.

A salt is random, unique per password, and stored alongside the verifier. It prevents precomputed tables and makes identical passwords produce different stored outputs; it does not need to be secret. A pepper is an additional secret kept separately from the password database (for example, in a secret manager). It can add defense in depth but introduces rotation, availability, and recovery complexity. Do not treat a pepper as a replacement for a salt or a password KDF.

Example of a standard-library KDF primitive (illustrative only; a production password storage format should use a vetted library/API and store all parameters). The low-cost `n=2**14` setting below is deliberately a lightweight demonstration, **not a production recommendation**; current OWASP guidance recommends a higher scrypt cost (for example, `N=2**17, r=8, p=1` where feasible). Benchmark the deployment and use current policy guidance rather than copying this demonstration setting:

```python
import hashlib
import secrets

password = b"example only - never hard-code real passwords"
salt = secrets.token_bytes(16)
verifier = hashlib.scrypt(password, salt=salt, n=2**14, r=8, p=1, dklen=32)
# Persist algorithm + n/r/p/dklen + salt + verifier using a defined encoding.
# Benchmark parameters and review current security guidance before deployment.
```

Do not log passwords, salts combined with sensitive context unnecessarily, or derived verifier material. Use a constant-time comparison for verifier bytes when implementing a verification layer, while preferring the dedicated library's supported verify API. Apply rate limits, breach-password screening, secure reset flows, MFA where appropriate, and migration/rehash-on-login policies. Never invent a custom password format without a reviewed reason.

## 10. Advanced security concepts and failure modes

### 10.1 Collision resistance and output length

A collision is any two different inputs with the same digest. For an ideal `n`-bit hash, the birthday bound makes collision search scale roughly as `2^(n/2)` work. A 256-bit digest therefore has an approximate generic collision scale of `2^128`, not `2^256`. This is a simplified model; algorithm-specific cryptanalysis and implementation weaknesses matter too.

Do not use a truncated digest without considering the reduced collision space. For an identifier derived from a digest, document truncation, namespace/domain separation, and collision handling. If uniqueness is a correctness invariant, use a unique constraint and define conflict behavior rather than relying solely on probability.

### 10.2 Length-extension attacks

Some Merkle–Damgård hash constructions (including SHA-256) have a length-extension property: knowing `SHA256(secret || message)` can enable calculation of a digest for an extended message under certain conditions without knowing the secret. This is why a homemade prefix-hash MAC is not a safe substitute for HMAC. HMAC uses a standardized inner/outer construction to avoid this class of misuse. Do not build authentication by concatenating a key with data and hashing it.

### 10.3 Timing attacks and `compare_digest`

Ordinary string equality may stop at the first differing character, which can leak timing information in some remotely observable settings. `hmac.compare_digest()` is intended to mitigate content-dependent comparison timing for same-type values. It does not guarantee whole-program constant-time behavior; parsing, length checks, network behavior, key lookup, and error paths can still differ. Normalize and validate formats consistently, avoid leaking detailed verification errors to attackers, and follow protocol guidance.

### 10.4 Hashing personal information does not anonymize it

An email address, phone number, postal code, or small identifier space can often be guessed and hashed offline. A stable hash also enables linkage across datasets and time. Plain hashing is pseudonymization at best in many contexts, not automatic anonymization. HMAC with a secret key can make offline guessing harder for a party without the key, but creates key-management and linkage risks and is not automatically anonymous either.

**Hashing vs tokenization:** hashing deterministically transforms values; tokenization substitutes a token whose mapping may be held separately. Tokenization can support reversibility through a protected mapping, while hashing is not designed to be reversible. Both can remain sensitive personal data depending on linkability, access, and legal context. Minimize collection, restrict access, rotate keys where appropriate, define retention, and consult your data-protection requirements.

### 10.5 Domain separation and canonicalization

Do not reuse the same digest namespace for unrelated purposes without a design reason. Prefixing distinct, unambiguous domain labels before hashing can separate application-level uses (for example, `b"record-v1\0" + canonical_bytes` versus `b"manifest-v1\0" + ...`). This is not a substitute for HMAC or a standardized protocol, but helps prevent accidental cross-purpose collisions. Define version labels, byte encoding, length framing, and field boundaries; naive concatenation can be ambiguous (`ab` + `c` versus `a` + `bc`).

### 10.6 Key and secret handling

- Never commit secrets or place them in source code, test fixtures used outside isolated tests, URLs, logs, crash reports, or telemetry.
- Load production keys from an approved secret manager or protected runtime injection; restrict who can read them.
- Rotate keys with a defined policy and record key IDs, not key values.
- Use separate keys for distinct purposes and environments.
- Ensure exception messages and debug output do not include request secrets.
- Use TLS for transport; HMAC does not encrypt the payload.
- Have a plan for key compromise, token revocation, incident response, and data migration.

## 11. Practical mini-project: artifact manifest and webhook helper

This mini-project demonstrates three distinct jobs: hashing an artifact, fingerprinting a structured record, and authenticating a webhook. It deliberately does not pretend these are one mechanism.

### 11.1 Implementation module

Save as `security_primitives.py`:

```python
from __future__ import annotations

import hashlib
import hmac
import json
import math
import secrets
import unicodedata
import uuid
from pathlib import Path
from typing import Any


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _json_tree(value: Any, path: str = "$") -> Any:
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"non-finite float at {path}")
        return value
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [_json_tree(v, f"{path}[{i}]") for i, v in enumerate(value)]
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"key at {path} must be str")
            normalized_key = unicodedata.normalize("NFC", key)
            if normalized_key in result:
                raise ValueError(f"duplicate key after normalization at {path}")
            result[normalized_key] = _json_tree(item, f"{path}.{normalized_key}")
        return result
    raise TypeError(f"unsupported value at {path}: {type(value).__name__}")


def canonical_record_bytes(record: dict[str, Any]) -> bytes:
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")
    text = json.dumps(
        _json_tree(record), sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False,
    )
    return text.encode("utf-8")


def record_fingerprint(record: dict[str, Any]) -> str:
    return hashlib.sha256(b"record-fingerprint-v1\0" + canonical_record_bytes(record)).hexdigest()


def secure_token(nbytes: int = 32) -> str:
    # Bound allocation if this helper is ever called with externally controlled input.
    if isinstance(nbytes, bool) or not isinstance(nbytes, int) or not 16 <= nbytes <= 4096:
        raise ValueError("nbytes must be an integer from 16 through 4096 for this token policy")
    return secrets.token_urlsafe(nbytes)


def create_tag(key: bytes, message: bytes) -> str:
    if not isinstance(key, bytes) or len(key) < 32:
        raise ValueError("key must be bytes with at least 32 bytes for this example policy")
    if not isinstance(message, bytes):
        raise TypeError("message must be bytes")
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def verify_tag(key: bytes, message: bytes, tag_hex: str) -> bool:
    if not isinstance(key, bytes) or len(key) < 32 or not isinstance(message, bytes):
        return False
    if not isinstance(tag_hex, str) or len(tag_hex) != 64:
        return False
    if any(ch not in "0123456789abcdefABCDEF" for ch in tag_hex):
        return False
    expected = hmac.new(key, message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, tag_hex.lower())


def webhook_tag(key: bytes, timestamp_text: str, raw_body: bytes) -> str:
    """Illustrative protocol: decimal timestamp + dot + exact raw body."""
    if not isinstance(timestamp_text, str) or not timestamp_text.isascii() or not timestamp_text.isdigit():
        raise ValueError("timestamp must be decimal ASCII seconds")
    if not isinstance(raw_body, bytes):
        raise TypeError("raw_body must be bytes")
    return create_tag(key, timestamp_text.encode("ascii") + b"." + raw_body)


def verify_webhook(key: bytes, timestamp_text: str, raw_body: bytes, tag_hex: str) -> bool:
    """Verify the example protocol's HMAC only; freshness/replay checks are separate."""
    if not isinstance(tag_hex, str) or len(tag_hex) != 64:
        return False
    if any(ch not in "0123456789abcdefABCDEF" for ch in tag_hex):
        return False
    try:
        expected = webhook_tag(key, timestamp_text, raw_body)
    except (TypeError, ValueError):
        return False
    return hmac.compare_digest(expected, tag_hex.lower())


def deterministic_record_id(source: str, external_id: str) -> uuid.UUID:
    if not source or not external_id:
        raise ValueError("source and external_id must be non-empty")
    namespace = uuid.uuid5(uuid.NAMESPACE_URL, "https://ids.example.test/source/" + source)
    return uuid.uuid5(namespace, external_id)
```

The minimum key length in this teaching helper is a local policy guard, not a general proof of key quality. Generate HMAC keys from a cryptographically secure source (for example, `secrets.token_bytes(32)`) and manage them securely. Do not generate a new key on each process start if multiple processes must verify each other's messages.

### 11.2 Example use

```python
from pathlib import Path
import secrets
from security_primitives import (
    sha256_file, record_fingerprint, secure_token,
    create_tag, verify_tag, deterministic_record_id,
)

artifact_digest = sha256_file(Path("input.csv"))
record_digest = record_fingerprint({"source": "crm", "id": "0042", "active": True})
token = secure_token()
key = secrets.token_bytes(32)  # demo only; production key must persist in managed secret storage
body = b'{"event_id":"evt-123","type":"customer.updated"}'
tag = create_tag(key, body)
assert verify_tag(key, body, tag)
record_id = deterministic_record_id("crm", "0042")
print(artifact_digest, record_digest, record_id)
# Never print or log `token` or production `key` in real systems.
```

The example's key is ephemeral, so it is suitable only for a self-contained demonstration. Production systems need a stable managed key shared by the legitimate producer and verifier, plus rotation and replay controls.

## 12. Test suite

Save as `test_security_primitives.py` next to `security_primitives.py`, install/use `pytest`, and run `python -m pytest -q`. These tests establish behavior for the code shown; they do not prove a cryptographic construction or deployment secure.

```python
import hashlib
import hmac
import unicodedata
import uuid

import pytest

from security_primitives import (
    canonical_record_bytes,
    create_tag,
    deterministic_record_id,
    record_fingerprint,
    secure_token,
    sha256_file,
    verify_tag,
    webhook_tag,
    verify_webhook,
)


def test_chunked_file_hash_matches_hashlib(tmp_path):
    path = tmp_path / "payload.bin"
    payload = bytes(range(256)) * 500
    path.write_bytes(payload)
    assert sha256_file(path, chunk_size=127) == hashlib.sha256(payload).hexdigest()


def test_file_digest_matches_chunked_hash(tmp_path):
    path = tmp_path / "payload.bin"
    path.write_bytes(b"a\x00b" * 1000)
    with path.open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    assert actual == sha256_file(path, chunk_size=17)


@pytest.mark.parametrize("chunk_size", [0, -1, True, 1.5])
def test_invalid_chunk_size(chunk_size, tmp_path):
    path = tmp_path / "x"
    path.write_bytes(b"x")
    with pytest.raises(ValueError):
        sha256_file(path, chunk_size=chunk_size)


def test_canonical_fingerprint_ignores_mapping_order():
    left = {"id": 7, "status": "ok"}
    right = {"status": "ok", "id": 7}
    assert canonical_record_bytes(left) == canonical_record_bytes(right)
    assert record_fingerprint(left) == record_fingerprint(right)


def test_canonical_record_requires_object_root():
    with pytest.raises(TypeError):
        canonical_record_bytes(["not", "an", "object"])


def test_canonicalization_normalizes_unicode_strings():
    composed = {"label": "caf\u00e9"}
    decomposed = {"label": "cafe\u0301"}
    assert record_fingerprint(composed) == record_fingerprint(decomposed)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), {1: "non-string key"}, {"x": {1, 2}}])
def test_rejects_noncanonical_values(value):
    with pytest.raises((TypeError, ValueError)):
        record_fingerprint({"payload": value})


def test_normalization_collision_is_rejected():
    record = {"\u00e9": 1, "e\u0301": 2}
    with pytest.raises(ValueError):
        canonical_record_bytes(record)


def test_secure_token_policy():
    token = secure_token(32)
    assert isinstance(token, str) and len(token) >= 32
    for bad in (True, 1, 0, -1, 1.2, 4097):
        with pytest.raises(ValueError):
            secure_token(bad)


def test_hmac_valid_and_invalid_messages():
    key = b"k" * 32
    message = b"exact raw request body"
    tag = create_tag(key, message)
    assert verify_tag(key, message, tag)
    assert not verify_tag(key, message + b"!", tag)
    assert not verify_tag(key, message, "0" * 64)


@pytest.mark.parametrize("malformed", [None, "", "g" * 64, "a" * 63, "a" * 65, 123])
def test_hmac_rejects_malformed_tag(malformed):
    assert verify_tag(b"k" * 32, b"body", malformed) is False


def test_hmac_rejects_short_key():
    with pytest.raises(ValueError):
        create_tag(b"short", b"body")
    assert not verify_tag(b"short", b"body", "0" * 64)


def test_webhook_signature_uses_exact_raw_body():
    key = b"w" * 32
    timestamp = "1792200000"
    body = b'{"id":1, "type":"updated"}'
    tag = webhook_tag(key, timestamp, body)
    assert verify_webhook(key, timestamp, body, tag)
    assert not verify_webhook(key, timestamp, body.replace(b" ", b""), tag)
    assert not verify_webhook(key, timestamp, body + b"!", tag)


@pytest.mark.parametrize("timestamp", ["", "-1", "1.2", "１２３", None])
def test_webhook_rejects_malformed_timestamp(timestamp):
    assert not verify_webhook(b"w" * 32, timestamp, b"body", "0" * 64)


def test_webhook_rejects_malformed_signature():
    assert not verify_webhook(b"w" * 32, "1792200000", b"body", "not-a-tag")


def test_webhook_signature_changes_when_timestamp_changes():
    key = b"w" * 32
    body = b"same body"
    tag = webhook_tag(key, "1792200000", body)
    assert not verify_webhook(key, "1792200001", body, tag)


def test_webhook_rejects_invalid_key():
    assert not verify_webhook(b"short", "1792200000", b"body", "0" * 64)


def test_deterministic_uuid_repeats_and_separates_names():
    first = deterministic_record_id("crm", "42")
    assert first == deterministic_record_id("crm", "42")
    assert first != deterministic_record_id("crm", "43")
    assert isinstance(first, uuid.UUID) and first.version == 5


def test_deterministic_uuid_rejects_empty_values():
    with pytest.raises(ValueError):
        deterministic_record_id("", "42")
```

The suite tests correct plumbing and specified edge behavior. It does not test side-channel resistance, entropy quality, provider interoperability, key storage, replay resistance, or production throughput. Add integration tests against the actual webhook provider's documented test vectors and deployment controls.

## 13. Threat scenarios and appropriate responses

| Scenario | Incorrect response | Better response |
|---|---|---|
| Downloaded file may be altered | Trust any SHA-256 printed beside the same download | Obtain expected digest from a trusted manifest or authenticate the manifest |
| Webhook body changed in transit | Compare ordinary hash of body | Verify provider-defined HMAC/signature over exact raw bytes |
| Same webhook is sent again | Assume valid HMAC means new event | Timestamp window plus durable event-ID deduplication and idempotent processing |
| Need password storage | Store `sha256(password)` | Use Argon2id/bcrypt or a properly configured password KDF with per-password salt |
| Need reset link | Use `random.random()` or a UUID as a token | Use `secrets`, short lifetime, single use, scope, revocation, and safe storage |
| Need stable ID for external record | Use Python's built-in `hash()` | Use a documented deterministic identifier scheme such as UUIDv5 or canonical digest |
| Need privacy in analytics export | SHA-256 an email and call it anonymous | Minimize data, assess linkability, use governed tokenization/pseudonymization, and restrict access |
| Need to sign data for public verification | Use HMAC and distribute the shared key | Use a reviewed digital-signature scheme from a specialist library |
| Need to encrypt stored or transmitted data | Hash it | Use a vetted encryption protocol/library; hashing is not encryption |

## 14. Common mistakes

1. **Using `random` for secrets.** It is designed for reproducibility/simulation, not adversarial unpredictability.
2. **Using a plain digest as authentication.** An attacker can recompute an unkeyed hash.
3. **Inventing `sha256(key + message)`.** Use HMAC or a protocol-specified MAC.
4. **Comparing a secret tag with `==`.** Use `hmac.compare_digest` with consistent types and a validated format.
5. **Verifying parsed-and-reserialized JSON.** Verify the exact byte sequence the protocol signs.
6. **Treating HMAC as replay protection.** Add freshness and durable deduplication according to the protocol.
7. **Using fast SHA-256 for password storage.** Use a password-specific KDF/library.
8. **Calling a hashed email anonymous.** Stable low-entropy values are often guessable and linkable.
9. **Assuming UUIDs are secret or perfectly unique.** UUIDs are identifiers, not authorization controls; enforce persistence invariants.
10. **Assuming all Python versions expose the same API.** `hashlib.file_digest` is Python 3.11+; `uuid.uuid7` is Python 3.14+.
11. **Assuming sorted JSON is universal canonical JSON.** Cross-language systems need a defined canonicalization standard and schema rules.
12. **Logging secrets for debugging.** Log safe metadata such as key ID, verification outcome, and request correlation ID—not the key, token, password, or full sensitive payload.
13. **Treating passing unit tests as a security certification.** Tests validate selected behavior, not cryptographic proofs, deployment controls, or protocol completeness.

## 15. Hands-on exercises

1. Hash a multi-megabyte file with chunk sizes of 4 KiB and 1 MiB. Confirm equal digests and explain the memory trade-off.
2. Modify one byte of a file and observe the digest change. Explain why that alone does not identify the author.
3. Create two records with different dictionary key order and the same semantic data. Verify canonical fingerprints match. Then change a field and explain why the fingerprint changes.
4. Add a schema-specific timestamp conversion rule. Require timezone-aware timestamps and serialize them as UTC with an explicit `Z` suffix.
5. Generate 10,000 secure tokens and check for duplicates as an experiment. Explain why no observed duplicate is not a proof of uniqueness.
6. Alter a valid HMAC body by one byte. Confirm verification fails. Then explain why a valid old signature can still be replayed.
7. Add key IDs to a webhook verifier. Make sure a supplied unknown key ID is rejected without a filesystem or network lookup.
8. Design a password-verifier record that stores algorithm, parameters, salt, and derived verifier but never the raw password. Explain rehash-on-login.
9. Choose UUIDv4, UUIDv5, or UUIDv7 for a new event table. State requirements for ordering, privacy, deterministic retries, and runtime compatibility.
10. Design a Merkle-style manifest for partitioned data. Define leaf ordering, domain prefixes, algorithm/version metadata, and how the trusted root is distributed.

## 16. Self-check with explained answers

**1. Why is SHA-256 not enough to authenticate a webhook?**  
Because anyone can compute an unkeyed digest. Authentication requires a trusted signing mechanism such as the provider-defined HMAC or digital signature, with a securely managed key and correct verification of the exact signed bytes.

**2. Why use `hmac.compare_digest()`?**  
It reduces content-dependent timing leakage during comparison. It does not make the entire request path constant-time or remove the need for consistent validation and error handling.

**3. Why is `SHA256(secret + message)` unsafe as a custom MAC?**  
Some hash constructions permit length-extension attacks, and custom key/hash combinations lack the analysis and standardization of HMAC. Use `hmac.new(key, message, hashlib.sha256)`.

**4. Which UUID version fits a repeatable ID from a namespace and external record ID?**  
UUIDv5 is the standard-library deterministic choice. The namespace and normalized name must be stable; it is not a secret token.

**5. When should you use `secrets` instead of `random`?**  
Use `secrets` for unpredictable bearer secrets, reset tokens, API tokens, and similar security-sensitive values. Use `random` for simulations and reproducible sampling where adversarial unpredictability is not required.

**6. Does hashing an email anonymize it?**  
No. The input space is guessable, and stable digests enable linkage. A digest can be pseudonymous and still be personal data; assess governance and legal requirements.

**7. Why should file hashing be chunked?**  
It bounds memory usage independently of file size and allows processing large files without reading the entire object into RAM.

**8. What does a passing HMAC unit test prove?**  
It shows that the tested implementation behaves as expected for those test vectors and cases. It does not prove the key is safe, the provider format is correct, replay is prevented, or the deployment is secure.

**9. Why are password salts not secret?**  
They make precomputation and cross-account equality attacks harder by ensuring each password verifier uses a unique input. A salt is stored with the verifier; password strength comes from the KDF and cost parameters. A pepper, by contrast, is an additional secret.

**10. Why doesn't a UUID guarantee uniqueness in the mathematical sense?**  
Finite identifiers can collide. The collision probability may be negligible for an appropriate UUID version and workload, but correctness-critical systems should enforce uniqueness at the database or service boundary.

## 17. Final reference table

| Requirement | Preferred starting point | Key cautions |
|---|---|---|
| General content digest | `hashlib.sha256(data)` | Digest is not authentication |
| Large file digest | Chunked `hash.update()`; `file_digest` on Python 3.11+ | Binary mode; trusted expected digest; file replacement races |
| HMAC-SHA-256 | `hmac.new(key, message, hashlib.sha256)` | Shared secret, key management, exact signed bytes |
| MAC verification | `hmac.compare_digest()` | Validate tag encoding; does not prevent replay |
| Secure token | `secrets.token_urlsafe(nbytes)` / `token_hex(nbytes)` | Expiry, scope, revocation, safe storage, log redaction |
| Secure random choice | `secrets.choice()` | Use for security-sensitive selection, not reproducible simulation |
| Random UUID | `uuid.uuid4()` | Identifier only; not an authorization secret |
| Deterministic UUID | `uuid.uuid5(namespace, name)` | Namespace/name contract; no secrecy guarantee |
| Time-ordered UUID | `uuid.uuid7()` on Python 3.14+ | Timestamp leakage and non-global ordering |
| Password verifier | Argon2id/bcrypt library or correctly configured `scrypt`/`pbkdf2_hmac` | Per-password salt, cost tuning, stored parameters, rehash policy |
| Structured record fingerprint | Documented canonical serialization + SHA-256 | Serializer contract/version; not authentication or anonymization |
| Content-addressable storage | Digest + authenticated manifest and collision policy | Verify reads; atomic writes; sensitive-content leakage |
| Publicly verifiable authenticity | Reviewed digital-signature scheme via specialist library | Key lifecycle and protocol correctness |
| Encryption | Reviewed encryption protocol/library | Hashes and HMACs do not encrypt |

## 18. Authoritative references and version notes

Use the documentation for the Python version deployed, and the protocol/provider specification where one exists. These references support API and security-policy details; they do not certify any particular application design.

- [Python `hashlib` documentation](https://docs.python.org/3.13/library/hashlib.html): algorithms, `file_digest()` (3.11+), SHAKE output lengths, and algorithm availability.
- [Python `hmac` documentation](https://docs.python.org/3.13/library/hmac.html): HMAC construction and `compare_digest()` limitations.
- [Python `secrets` documentation](https://docs.python.org/3.13/library/secrets.html): secure token generation and why it is preferred to `random` for security.
- [Python `uuid` documentation](https://docs.python.org/3.14/library/uuid.html): UUID versions and `uuid7()` availability (3.14+).
- [RFC 2104 — HMAC](https://www.rfc-editor.org/rfc/rfc2104): standardized keyed-hash construction.
- [RFC 8785 — JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785): cross-language canonical JSON when its data constraints fit.
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html): current password KDF, salt, and pepper guidance.
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html): key management and cryptographic design principles.

## 19. Final review checklist

Before shipping a system using these primitives, confirm:

- [ ] The primitive matches the required property: integrity, authentication, unpredictability, password verification, or identification.
- [ ] Hash algorithm and encoding are explicitly specified and interoperable.
- [ ] Large files are hashed with bounded memory and binary I/O.
- [ ] Expected digests come from a trusted source if adversarial tampering matters.
- [ ] HMAC covers exactly the bytes and metadata specified by the protocol.
- [ ] Verification uses `hmac.compare_digest()` and rejects malformed tags.
- [ ] Key generation, storage, rotation, revocation, and incident response are defined.
- [ ] Webhook freshness and durable replay/deduplication controls are defined separately from HMAC.
- [ ] Tokens use `secrets`, have lifecycle controls, and are not logged.
- [ ] Passwords use a password KDF/library, per-password salts, suitable cost parameters, and rehash policy.
- [ ] UUID/fingerprint schemes have stable namespace, normalization, and version contracts.
- [ ] Personal-data hashes are not incorrectly described as anonymous.
- [ ] Version-specific APIs are guarded or documented (`file_digest`: 3.11+; UUIDv7: 3.14+).
- [ ] Tests cover valid, invalid, malformed, edge, and reproducibility cases, with provider integration vectors where relevant.
- [ ] A specialist library and security review are used when the problem requires cryptographic protocols beyond these primitives.

**Core principle:** select the primitive for the security property you actually need, define its byte-level contract, manage its keys and lifecycle, and never treat a unit test or a hash string as proof that the whole system is secure.
