# PII Detection, Masking, and Tokenization

> **Stage 2 → Python for Data Engineering → Module 2.20 — Observability, Lineage, Governance, and Security**

**Progression:** Beginner → Intermediate → Advanced → Production/Expert

> **Core principle:** PII protection is not one transformation applied to one database column. It is a system of detection, classification, minimization, protection, access control, observability hygiene, testing, monitoring, and incident response across the entire data lifecycle.

---

## 1. Learning Objectives

By the end of this module you should be able to:

- define PII, personal data, sensitive data, direct identifiers, quasi-identifiers, and sensitive attributes
- locate PII across databases, files, APIs, streams, lakehouses, warehouses, observability systems, quarantine data, test data, and backups
- detect candidate PII using deterministic rules, checksums, column heuristics, and sampling
- use Microsoft Presidio for text-oriented detection and anonymization
- understand why automated detection requires human review for important assets
- convert PII findings into catalog metadata and policy inputs
- implement redaction, static masking, dynamic masking, pseudonymisation, keyed hashing, and tokenization
- reason about token vaults, vaultless tokenization, and format-preserving encryption
- choose a protection technique based on reversibility, joins, analytics, access, security, and operational requirements
- understand re-identification, linking attacks, k-anonymity, and differential privacy at an appropriate awareness level
- prevent PII leakage through logs, traces, metrics, errors, alerts, events, quarantine data, and development/test data
- continuously scan new sources and schema changes
- enforce privacy controls in CI/CD
- test and verify PII detection and protection
- design a production PII protection architecture
- reason about failures, incidents, auditability, key management, and data copies

### Mental model

```text
Discover
   ↓
Detect
   ↓
Classify
   ↓
Review
   ↓
Minimize
   ↓
Protect
   ↓
Publish metadata
   ↓
Enforce access
   ↓
Monitor
   ↓
Test
   ↓
Audit
   ↓
Respond to incidents
```

## 2. Why PII Protection Matters in Data Engineering

Data Engineers move data between systems. Every copy, transformation, log statement, retry queue, export, backup, and debugging workflow can create another place where personal information exists.

The security problem is therefore larger than:

```text
"Protect the production database."
```

A realistic pipeline is:

```text
API
 ↓
Kafka
 ↓
Raw object storage
 ↓
Spark
 ↓
Lakehouse
 ↓
Warehouse
 ↓
BI
```

But operational copies may also exist:

```text
Logs
Traces
Metrics
Alerts
Dead-letter queues
Quarantine tables
Temporary files
Notebooks
Developer laptops
Test fixtures
Backups
```

A single `email` field can therefore propagate much farther than the original source.

### Why Data Engineers need privacy awareness

A Data Engineer controls or influences:

- schemas
- ingestion
- transformations
- storage layers
- retention
- data movement
- observability
- testing
- CI/CD
- access paths
- failure handling

A privacy-safe pipeline asks:

```text
Do we need this field?
Who needs it?
Where does it travel?
Can it be transformed?
Can it be joined without exposing the original?
Who can reverse the transformation?
How long do copies remain?
Can telemetry leak it?
How is the control tested?
```

### Production perspective

Privacy is a **systems property**. A perfectly masked warehouse is still unsafe if the raw Kafka topic, exception logs, quarantine table, and developer dataset contain the original values.

## 3. What Is Personally Identifiable Information?

### Simple explanation

**Personally Identifiable Information (PII)** is information that can identify, describe, contact, or be linked to an individual, depending on context and the applicable privacy framework.

Terminology differs across jurisdictions and organizational policies. Treat your organization's formal legal/privacy definitions as authoritative.

Common examples include:

```text
email
phone_number
full_name
government_id
passport_number
customer_id
IP address
device identifier
date of birth
postal code
location
financial information
health information
```

### Direct identifiers

A direct identifier can identify a person by itself or is strongly associated with an individual.

Examples:

```text
passport_number
government_id
email_address
phone_number
```

### Quasi-identifiers

A quasi-identifier may not identify a person alone but can contribute to identification when combined with other information.

Examples:

```text
date_of_birth
postal_code
location
age
gender
```

The key Data Engineering lesson is:

```text
Column-by-column thinking
        ↓
is insufficient
        ↓
Think about combinations of attributes
```

For example:

```text
Age + ZIP + Date of Birth + Location
```

may be substantially more identifying than any one field considered independently.

### Sensitive attributes

Sensitive information may include financial, health-related, identity, or other categories that require stronger controls under organizational policy or applicable law.

Do not assume that every organization uses the same taxonomy. The engineering system should encode the organization's approved classification scheme.

## 4. Direct Identifiers, Quasi-Identifiers, and Sensitive Data

| Category | Example | Main risk |
|---|---|---|
| Direct identifier | email | Direct association/contact |
| Direct identifier | government ID | Strong identity linkage |
| Quasi-identifier | date of birth | Combination-based identification |
| Quasi-identifier | postal code | Linking with auxiliary data |
| Sensitive attribute | financial information | Sensitive disclosure |
| Sensitive attribute | health information | Sensitive disclosure |
| Device identifier | device ID | Tracking/linkability |

### Engineering rule

Do not build detection exclusively around field names such as `email` or `phone`.

Use multiple signals:

```text
Schema
+
Column name
+
Data type
+
Value patterns
+
Sample values
+
Uniqueness
+
Distribution
+
Business context
+
Existing metadata
```

### Checkpoint

**Q1. What is the difference between a direct identifier and a quasi-identifier?**

**Answer:** A direct identifier can directly identify or strongly identify an individual; a quasi-identifier contributes to identification when combined with other information.

**Q2. Why inspect combinations?**

**Answer:** Multiple individually weak attributes can become identifying when linked with each other or with auxiliary datasets.

## 5. Where PII Appears in a Modern Data Platform

PII can exist in almost every data representation:

```text
OLTP databases
Raw ingestion
Bronze/raw data
Silver/cleaned data
Gold/analytics data
Warehouses
Lakehouses
Object storage
Kafka/events
JSON
CSV
Parquet
APIs
Logs
Traces
Metrics
Exception messages
Alerts
Quarantine tables
Dead-letter queues
Temporary files
Notebooks
Development datasets
Test fixtures
Backups
```

### Example propagation

```text
POST /customers
    ↓
API payload contains email
    ↓
Kafka event contains email
    ↓
Consumer writes raw event to object storage
    ↓
Spark job reads event
    ↓
Silver table retains email
    ↓
Exception prints bad record
    ↓
Log system stores email
    ↓
Quarantine table stores original event
    ↓
Developer copies sample locally
```

Protecting only the PostgreSQL source did not protect the system.

### Data lifecycle map

| Location | PII risk | Typical control |
|---|---|---|
| OLTP | Source PII | Least privilege, encryption |
| Bronze | Raw PII | Restricted access, encryption, retention |
| Silver | Derived PII | Tokenization/masking/pseudonymisation |
| Gold | Analytical PII | Minimization, aggregation |
| Kafka | Event payload/header | Minimize, classify, protect |
| Logs | Accidental copies | Structured redacted logging |
| Traces | Span attributes | Attribute allowlisting |
| Metrics | Labels | Never use user identifiers |
| Quarantine | Failed raw records | Restricted, encrypted, short retention |
| Test data | Developer copies | Synthetic/masked/tokenized |
| Backups | Long-lived copies | Encryption, access, lifecycle controls |

## 6. PII Detection Fundamentals

No single detector is perfect.

A production detection system combines signals:

```text
Deterministic rules
      +
Checksums
      +
Column heuristics
      +
Sampling
      +
NLP/entity recognition
      +
Metadata
      +
Human review
```

The output should be treated as a **classification candidate**, not unquestionable truth.

### Detection quality

Two important error types:

- **False positive:** a non-PII value is classified as PII.
- **False negative:** actual PII is missed.

For sensitive datasets, false negatives can be particularly costly, while excessive false positives can create operational fatigue.

A practical detector therefore produces:

```text
Field
Candidate classification
Evidence
Confidence
Reviewer decision
Final policy
```

## 7. Rule-Based Detection and Checksums

### Rule-based detection

Common rules include:

- email-like patterns
- phone number patterns
- credit-card-like patterns
- government-identifier patterns
- known field names

Example:

```python
import re

EMAIL_RE = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)

def looks_like_email(value: str) -> bool:
    return bool(EMAIL_RE.match(value.strip()))
```

Use this as a **candidate detector**, not as proof.

### Why regex is insufficient

Regex does not understand business context.

A field called `email` may contain:

```text
unknown
N/A
example@invalid
```

A field called `contact` may contain an email even though its name provides no clue.

Free text can also contain multiple entity types:

```text
"Call John at +91... or email john@example.com"
```

### Checksums

Some identifiers include validation/checksum rules. A checksum can reduce false positives after a structural pattern has matched.

Conceptually:

```text
Pattern match
    ↓
Candidate
    ↓
Checksum/validation
    ↓
Higher-confidence candidate
```

Do not claim that a valid checksum proves an identifier belongs to a real person.

### Example detection pipeline

```python
def classify_candidate(value: str) -> str:
    if looks_like_email(value):
        return "possible_email"
    return "unknown"
```

Production detectors should record evidence and confidence rather than silently mutating data based on a single regex.

## 8. Column Heuristics

Column metadata provides useful prior information.

Examples:

```text
email
email_address
customer_email
phone
phone_number
dob
date_of_birth
passport_no
national_id
```

Useful heuristics include:

- column name
- data type
- uniqueness
- null percentage
- value distribution
- entropy awareness
- sample values
- schema metadata

### Simple classifier

```python
PII_NAME_HINTS = {
    "email", "email_address", "phone", "phone_number",
    "date_of_birth", "dob", "passport", "national_id",
    "government_id"
}

def column_name_score(name: str) -> float:
    normalized = name.lower().replace("-", "_")
    tokens = set(normalized.split("_"))

    return 1.0 if tokens & PII_NAME_HINTS else 0.0
```

This is deliberately simple.

A production classifier should combine:

```text
Name score
+
Observed-value score
+
Schema/type score
+
Uniqueness score
+
Business metadata
```

### Limitation

Column heuristics fail when:

```text
customer_contact
payload
field_7
identifier
notes
```

contains PII without an obvious name.

They can also produce false positives because a field named `email_template` is not itself necessarily personal data.

## 9. Sampling-Based Detection

Scanning every value may be expensive for very large datasets.

A sampling strategy can inspect a representative subset:

```text
Full dataset
     ↓
Sample
     ↓
Detect candidate PII
     ↓
Estimate confidence
```

Possible approaches:

- random sampling
- stratified sampling awareness
- partition-aware sampling
- recent-data sampling
- schema-based targeted sampling

### Python example

```python
import pandas as pd

df = pd.read_parquet("customers.parquet")

sample = df.sample(
    n=min(10_000, len(df)),
    random_state=42,
)

email_candidates = sample["contact"].dropna().map(looks_like_email)

print("Candidate rate:", email_candidates.mean())
```

### Sampling risks

Poor samples can miss:

- rare PII
- records concentrated in a small partition
- newly introduced values
- unusual tenants
- seasonal fields

Therefore:

```text
Sampling reduces cost
≠
Sampling guarantees detection
```

For critical data, combine sampling with schema rules, metadata, targeted scans, and human review.

## 10. PII Detection with Microsoft Presidio

**Microsoft Presidio** is a framework for detecting and anonymizing sensitive information in text.

Core concepts:

- **Analyzer** — evaluates text for entities.
- **Recognizer** — identifies a particular entity pattern/type.
- **Entity** — a detected category such as email or phone.
- **Score** — confidence associated with a result.
- **Anonymizer** — transforms detected entities.
- **Custom recognizer** — organization-specific detection logic.

### Basic analyzer example

```python
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()

results = analyzer.analyze(
    text="Contact john@example.com",
    language="en",
)

for result in results:
    print(result.entity_type, result.score)
```

The important mental model is:

```text
Text
 ↓
Analyzer
 ↓
Recognizer(s)
 ↓
Entity + score
 ↓
Review/policy
 ↓
Anonymization/protection
```

### Anonymization concept

```python
from presidio_anonymizer import AnonymizerEngine

anonymizer = AnonymizerEngine()

result = anonymizer.anonymize(
    text="Contact john@example.com",
    analyzer_results=results,
)

print(result.text)
```

Exact supported entities, recognizers, configuration, and package APIs depend on the installed Presidio version.

### Custom recognizers

Organizations often need custom detection for:

```text
Internal customer IDs
Employee IDs
National identifiers
Product-specific identifiers
Tenant-specific identifiers
```

### Production considerations

Tune:

- confidence thresholds
- recognizers
- custom patterns
- false positives
- false negatives
- language support
- domain-specific rules
- human review

> **Presidio assists detection; it does not make privacy classification infallible.**

## 11. Classification and Human Review

Automated PII detection should not be treated as a perfect oracle.

A practical workflow is:

```text
Detect
  ↓
Score
  ↓
Classify
  ↓
Human Review
  ↓
Approve / Reject
  ↓
Apply Protection Policy
  ↓
Record Metadata
```

Human review is particularly valuable for:

- high-impact datasets
- ambiguous free text
- new identifier types
- low-confidence findings
- sensitive classifications
- exceptions to standard policy

### Review record

```yaml
field: customer.contact
candidate: PII
entity: EMAIL
confidence: 0.97
evidence:
  - column_name
  - sample_values
review_status: approved
reviewer: privacy-data-steward
policy: restricted
```

The review decision should be auditable.

### Checkpoint

**Why not automate everything?**

Because detection is probabilistic and contextual. An organization must be able to distinguish:

```text
machine suggestion
```

from:

```text
approved classification
```

## 12. PII Metadata, Tags, and Data Catalog Integration

A detection result should become usable metadata.

Example:

```text
customer.email
    ↓
PII
    ↓
Identity
    ↓
Confidential
    ↓
Restricted
```

Catalog metadata can include:

```yaml
classification:
  sensitivity: restricted
  categories:
    - pii
    - identity
tags:
  - pii
  - email
owner: customer-data
```

### Why this matters

Metadata can become an input to:

```text
Access controls
Masking policies
Audit requirements
Retention rules
Scanning priorities
Catalog search
Incident response
```

However:

> **A catalog tag is metadata; it does not automatically enforce access unless a specific policy integration does so.**

### Example policy flow

```text
Catalog classification
       ↓
Policy engine
       ↓
Access/masking rule
       ↓
Runtime enforcement
       ↓
Audit
```

This separation prevents a common architectural mistake: assuming that merely labeling a field `PII` protects it.

## 13. Redaction

**Redaction** removes sensitive information from the output.

Example:

```text
john.doe@example.com
        ↓
[REDACTED]
```

Python:

```python
def redact(value: str) -> str:
    return "[REDACTED]"
```

Redaction is appropriate when the original value is not required by the consumer.

### Example: safe error message

Unsafe:

```text
Failed customer=alice@example.com
```

Safer:

```text
Failed processing customer record
```

or:

```text
Failed processing customer_id=internal-token
```

### When to prefer redaction

Use it when:

- consumers do not need the original value
- the value should not be recoverable
- logs/alerts/errors need diagnostic context without sensitive data

Redaction is irreversible, which is often exactly what makes it appropriate for telemetry.

## 14. Static Masking

Static masking transforms stored data into a safer representation.

Example:

```text
john.doe@example.com
        ↓
j***@example.com
```

A simple educational implementation:

```python
def mask_email(email: str) -> str:
    local, domain = email.split("@", 1)
    visible = local[:1]
    return f"{visible}***@{domain}"
```

### Typical use cases

- development
- testing
- analytics access
- non-production environments

### Risks

Predictable masks can leak information.

For example:

```text
john.doe@example.com
j***@example.com
```

still reveals the domain and first character.

A masking strategy must be designed around the consumer's actual need.

### Static vs irreversible

Some static transformations are irreversible; others preserve enough information to infer or reconstruct data.

Do not call a partially masked value anonymous.

## 15. Dynamic Masking

Dynamic masking determines what a user can see at query/runtime time.

Example:

```text
Privileged user:
john.doe@example.com

Normal analyst:
j***@example.com
```

Conceptually:

```text
User
 ↓
Identity / Role
 ↓
Policy
 ↓
Query
 ↓
Masked or unmasked result
```

### Advantages

- one underlying dataset
- different views by role
- central policy enforcement
- reduced duplication

### Limitations

- policy complexity
- performance considerations
- export paths
- cached extracts
- downstream copies
- alternate access interfaces

A database/warehouse can provide native dynamic masking, or a policy engine can mediate access.

### SQL-style conceptual example

```sql
SELECT
    CASE
        WHEN current_user_role() = 'privacy_admin'
            THEN email
        ELSE '***@***'
    END AS email
FROM customers;
```

This is **conceptual SQL**; exact role/masking syntax varies by database.

> **Dynamic masking does not protect copies made through privileged access.**

## 16. Pseudonymisation

Pseudonymisation replaces an identifier with a stable pseudonymous value.

```text
customer_id = 12345
        ↓
pseudonymous_id = 8f92...
```

The important property is that the original identity is no longer directly exposed to ordinary consumers, while a controlled system may still be able to link records.

### Pseudonymisation vs anonymisation

| Property | Pseudonymisation | Anonymisation |
|---|---|---|
| Linkability | Usually preserved | Intended to be removed |
| Reversal/link-back | May be possible | Should not be reasonably possible |
| Secret/key may exist | Often | Not sufficient to define anonymisation |
| Personal-data risk | May remain | Depends on whether identification is truly prevented |

> **Pseudonymized data may still be personal data.**

### Production questions

```text
Who can reverse/link it?
Where is the key?
Can datasets be joined?
Can auxiliary data re-identify users?
How are keys rotated?
How are access events audited?
```

## 17. Keyed Hashing

Keyed hashing is useful when you need a deterministic pseudonym without storing a direct mapping table.

A common construction is HMAC:

```text
HMAC(secret_key, customer_id)
```

Python:

```python
import hashlib
import hmac

def pseudonymize(value: str, secret_key: bytes) -> str:
    digest = hmac.new(
        secret_key,
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return digest
```

Example:

```python
key = b"example-secret-key"
print(pseudonymize("12345", key))
```

> **Educational example — not production key-management infrastructure.**

### Why HMAC?

Plain hashing such as:

```text
SHA-256(customer_id)
```

can be vulnerable to dictionary/brute-force attacks when the input space is predictable.

A secret key changes the attack model:

```text
HMAC(secret, value)
```

### Production considerations

- store keys in a managed secret/KMS-backed system
- never embed keys in source code
- separate keys by environment/purpose where appropriate
- control access
- audit use
- plan key rotation
- understand consequences of rotation for deterministic joins
- do not expose raw keys to ordinary data consumers

### Key rotation trade-off

If:

```text
HMAC(K1, customer_id)
```

becomes:

```text
HMAC(K2, customer_id)
```

then historical and new pseudonyms may no longer join.

A rotation strategy therefore needs explicit versioning or a controlled migration design.

## 18. Tokenization

Tokenization replaces a sensitive value with a token that has no direct business meaning to ordinary consumers.

Example:

```text
4111 1111 1111 1111
        ↓
tok_8f72ab...
```

Conceptually:

```text
Original value
     ↓
Tokenization service
     ↓
Token
```

A tokenization system may maintain a mapping:

```text
Token                  Original
tok_8f72ab...          sensitive value
```

### Why choose tokenization?

Tokenization is useful when:

- the original value may occasionally need to be recovered
- controlled detokenization is required
- applications need stable references
- regulated values should not be broadly propagated

### Important properties

- token uniqueness
- mapping protection
- authorization
- encryption
- auditability
- availability
- scalability
- failure handling

### Hashing vs tokenization

Hashing is typically a one-way transformation.

Tokenization commonly involves a controlled mapping that supports detokenization.

Therefore:

```text
Need controlled recovery?
        ↓
Consider tokenization
```

while:

```text
Need stable one-way join key?
        ↓
Consider keyed hashing/pseudonymisation
```

Always evaluate the threat model and data requirements.

## 19. Token Vaults

A token vault stores the mapping between tokens and protected originals.

```text
Application
    |
    v
Tokenization Service
    |
    +---- Token
    |
    +---- Secure Vault
              |
              +---- Original PII
```

### Vault responsibilities

A production vault may require:

- encryption at rest
- encryption in transit
- strict access control
- audit logging
- key management
- authorization for detokenization
- availability controls
- backup/recovery
- monitoring
- retention/deletion

### Simplified educational implementation

```python
import secrets

class EducationalTokenVault:
    def __init__(self):
        self._mapping = {}

    def tokenize(self, value: str) -> str:
        token = "tok_" + secrets.token_urlsafe(18)
        self._mapping[token] = value
        return token

    def detokenize(self, token: str) -> str:
        return self._mapping[token]
```

> **Educational example — not production security infrastructure.**

This example is intentionally incomplete. It lacks:

- persistent secure storage
- encryption
- authorization
- audit controls
- key management
- concurrency guarantees
- HA
- disaster recovery
- deletion workflows

A production system should use a vetted tokenization service or a carefully designed security platform rather than an in-memory dictionary.

## 20. Vault-Based vs Vaultless Tokenization

| Approach | Vault | Reversible | Main trade-off | Typical consideration |
|---|---:|---:|---|---|
| Vault-based | Yes | Usually | Central mapping infrastructure | Strong control and explicit detokenization |
| Vaultless | No central mapping vault | Depends on technique | Cryptographic/design complexity moves elsewhere | Scale and architecture |

### Vault-based

```text
Token ↔ protected mapping ↔ original
```

Advantages:

- explicit mapping
- controlled detokenization
- clear audit boundary

Costs:

- availability dependency
- operational complexity
- secure storage
- scaling

### Vaultless awareness

Vaultless approaches derive tokens through cryptographic mechanisms rather than maintaining the same style of centralized mapping vault.

Do not assume:

```text
Vaultless = automatically safer
```

or:

```text
Vault-based = automatically safer
```

Evaluate:

- reversibility
- format requirements
- threat model
- key management
- operational dependencies
- latency
- auditability
- rotation

## 21. Format-Preserving Encryption Awareness

**Format-preserving encryption (FPE)** is an encryption approach designed to preserve aspects of an input's format.

For example, an application may need a transformed value that remains compatible with a numeric field shape.

Potential requirement:

```text
Original:
1234567890123456

Protected:
another 16-digit value
```

The exact cryptographic construction and security properties depend on the chosen standard and implementation.

Use vetted cryptographic libraries/services for production.

### Why organizations consider FPE

- legacy schema compatibility
- fixed-width fields
- numeric-only interfaces
- systems that cannot easily accept arbitrary token formats

### Risks and considerations

- cryptographic strength
- domain size
- key management
- format leakage
- reversibility
- implementation correctness

Do not invent a custom FPE algorithm.

## 22. Choosing the Correct Protection Technique

| Technique | Reversible? | Stable for joins? | Typical purpose |
|---|---:|---:|---|
| Redaction | No | No | Remove sensitive content |
| Static masking | Usually no | Usually no | Safer copies/views |
| Dynamic masking | Underlying value remains | Yes internally | Role-based visibility |
| Plain hashing | One-way | Yes | Limited deterministic identifiers; often weak for low-entropy secrets |
| Keyed hashing/HMAC | One-way without key | Yes | Stable pseudonyms |
| Pseudonymisation | May support controlled linkage | Yes | Reduce direct exposure |
| Tokenization | Usually controlled recovery possible | Yes | Controlled replacement |
| Encryption | Yes with key | Depends | Protect stored/transmitted data |

### Decision framework

Ask:

```text
Do consumers need the original?
        ↓
     yes/no

If no:
  Redaction / masking / pseudonymisation

If stable joins are required:
  Keyed hashing / pseudonymisation

If controlled recovery is required:
  Tokenization / encryption

If users need different visibility:
  Dynamic masking

If no business value exists:
  Prefer minimization/removal
```

### Production questions

1. Is reversibility required?
2. Are joins required?
3. Is the source low entropy?
4. Who needs access?
5. Is detokenization required?
6. What is the threat model?
7. What is the performance requirement?
8. How will keys be managed?
9. What happens during rotation?
10. How are copies protected?
11. How is usage audited?
12. How is deletion performed?

> The best privacy control is often **not collecting or propagating data that is not required**.

## 23. Re-identification and Linking Risks

Removing a name does not automatically make data anonymous.

### Re-identification

Re-identification occurs when a person can be inferred from data that no longer contains an obvious identifier.

### Linking attack

An attacker combines datasets:

```text
Dataset A
Age + ZIP + Date

       +

Dataset B
Public/auxiliary information

       ↓

Potential individual
```

Example:

```text
Age: 43
ZIP: 700001
Date: 1983-04-17
```

may be much more identifying when combined with external data.

### Risk factors

- uniqueness
- quasi-identifiers
- external datasets
- rare combinations
- location
- timestamps
- behavioral patterns
- auxiliary knowledge

### Production lesson

```text
Remove email
    ≠
Guarantee anonymity
```

Privacy evaluation must consider what information remains and what an adversary can reasonably combine with it.

## 24. k-Anonymity Awareness

**k-anonymity** is a privacy model based on quasi-identifiers.

A dataset is k-anonymous with respect to a chosen set of quasi-identifiers when each resulting equivalence class contains at least `k` records.

Example:

```text
Age  ZIP
---  ------
40   700001
40   700001
40   700001
```

For these quasi-identifiers:

```text
k = 3
```

### Why it helps

A larger equivalence class makes simple re-identification based only on those quasi-identifiers harder.

### Limitations

k-anonymity does not automatically prevent:

- homogeneity attacks
- background-knowledge attacks
- inference from sensitive attributes
- attacks using additional information

Therefore:

```text
k-anonymity
```

is a privacy model, not a universal guarantee of anonymity.

## 25. Differential Privacy Awareness

**Differential privacy** provides a formal framework for limiting how much the output of an analysis reveals about any one individual.

Core concepts:

- aggregate queries
- controlled noise
- privacy budget
- epsilon (`ε`)
- privacy/utility trade-off

Conceptually:

```text
Private dataset
      ↓
Privacy mechanism
      ↓
Noisy aggregate
      ↓
Analyst
```

A smaller privacy budget generally corresponds to stronger privacy protection but can reduce analytical utility.

The important engineering awareness is:

```text
Individual-level data
       ↓
Controlled statistical output
```

rather than simply releasing a transformed row-level dataset.

Differential privacy is an advanced field; this module provides awareness rather than a complete mathematical treatment.

## 26. Why Pseudonymized Data Can Still Be Personal Data

Pseudonymisation changes how directly an identity is represented. It does not necessarily eliminate the ability to link the data to an individual.

For example:

```text
customer_id
   ↓
HMAC(customer_id)
   ↓
pseudonymous_id
```

If the organization retains:

```text
the key
+
other identifying information
```

the pseudonymous identifier can remain linkable.

Therefore:

> **Pseudonymized data may still constitute personal data.**

Engineering consequences:

- continue access controls
- retain classification
- protect keys
- restrict joins
- audit access
- define retention
- apply appropriate governance

Do not label a dataset “anonymous” merely because names were replaced.

## 27. PII in Logs

Unsafe:

```text
INFO Processing customer john@example.com
```

Logs are frequently copied to centralized systems and retained longer than developers expect.

### Safer structured logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info(
    "Processing customer record",
    extra={"customer_token": "tok_abc123"}
)
```

Better still, emit only the minimum diagnostic context required.

### Avoid

```python
logger.exception("Failed event=%s", full_event)
```

if `full_event` contains PII.

Prefer:

```python
logger.exception(
    "Failed event processing",
    extra={"event_id": event_id}
)
```

where `event_id` is itself non-sensitive.

### Production rule

Treat logs as a **data store** with:

- access control
- retention
- classification
- monitoring
- deletion/lifecycle controls

## 28. PII in Distributed Traces

Tracing is another data path.

Unsafe span attributes:

```text
email
phone
customer_address
government_id
```

unless there is a documented, protected reason.

Prefer:

```text
customer_token
tenant_id
request_id
operation
schema_version
```

where these identifiers are approved and non-sensitive.

### Safe tracing principle

Use an allowlist for span attributes rather than blindly copying request payloads.

```python
SAFE_ATTRIBUTES = {
    "operation",
    "schema_version",
    "request_id",
}

span.set_attribute("operation", "customer_lookup")
span.set_attribute("schema_version", "v3")
```

Never do:

```python
span.set_attribute("request_payload", payload)
```

when payload may contain PII.

Connect this to distributed tracing architecture:

```text
Application
   ↓
Span
   ↓
Collector
   ↓
Backend
```

Every stage must be considered a potential copy of sensitive data.

## 29. PII in Metrics, Labels, Errors, and Alerts

### Metrics

Never use personal values as metric labels.

Unsafe:

```text
request_total{email="john@example.com"}
```

This is both a privacy risk and a cardinality disaster.

Use bounded dimensions:

```text
request_total{
    service="orders",
    operation="create_order",
    status="success"
}
```

### Errors

Unsafe:

```text
Invalid customer email john@example.com
```

Safer:

```text
Invalid customer contact field
```

with a non-sensitive correlation identifier if needed.

### Alerts

Alert payloads may be copied into:

- Slack
- PagerDuty
- email
- ticketing systems

Therefore avoid sending raw records.

Unsafe:

```text
ALERT: Failed customer:
{"name":"John","email":"john@example.com", ...}
```

Safer:

```text
ALERT: Customer pipeline failed validation
run_id=run_123
error_code=INVALID_CONTACT
```

### Observability rule

```text
Metrics → bounded non-sensitive dimensions
Logs → redacted structured context
Traces → allowlisted safe attributes
Alerts → minimum actionable context
```

## 30. PII in Events and Streaming Systems

PII can appear in:

- Kafka message values
- message headers
- schemas
- dead-letter queues
- replay topics
- consumer logs

Example event:

```json
{
  "event_type": "customer.updated",
  "customer_id": "12345",
  "email": "john@example.com"
}
```

Ask whether consumers actually need the email.

A minimized event might be:

```json
{
  "event_type": "customer.updated",
  "customer_token": "tok_abc123"
}
```

### Streaming protection strategies

- minimize payloads
- classify schemas
- tokenize/pseudonymize identifiers
- restrict topic access
- protect schema metadata
- control retention
- protect replay topics
- redact consumer logs
- protect DLQs

### Kafka-style Python example

```python
event = {
    "event_type": "customer.updated",
    "customer_token": pseudonymize("12345", key),
}
```

Do not log the original event:

```python
# Unsafe
logger.info("Consumed event=%s", event)
```

if the event contains sensitive data.

## 31. PII in Quarantine Data

Quarantine is often overlooked.

```text
Raw Record
    ↓
Validation
    ↓
FAILED
    ↓
Quarantine
```

The quarantine record may contain the **original raw PII**.

### Controls

- strict access control
- encryption
- short retention
- masking where possible
- deletion
- audit logging
- monitoring

Do not assume:

```text
"Failed records are not production data."
```

They may be more sensitive because they preserve malformed raw input.

### Design question

If an analyst does not need the original failed payload, do not give them access merely because it is stored in a quarantine table.

## 32. PII in Test and Development Data

Copying production data into development creates a major privacy path.

Unsafe:

```text
Production
   ↓
pg_dump
   ↓
Developer laptop
```

Safer options:

- synthetic data
- masked data
- tokenized data
- pseudonymized data
- appropriately sampled protected data

### Synthetic example

```python
from faker import Faker

fake = Faker()

record = {
    "name": fake.name(),
    "email": fake.email(),
    "phone": fake.phone_number(),
}
```

Synthetic data is useful because it is generated rather than copied from real individuals.

However, validate that the generator itself does not accidentally contain real production data and that synthetic values are suitable for the intended test.

### Development rule

```text
Production data
     ↓
Do not copy by default
     ↓
Require explicit approved protection path
```

## 33. Continuous PII Scanning

PII scanning should be continuous.

```text
New source
   ↓
Schema discovery
   ↓
PII scan
   ↓
Classification
   ↓
Human review
   ↓
Protection policy
   ↓
Catalog metadata
   ↓
CI/CD enforcement
   ↓
Continuous monitoring
```

### Trigger points

Scan when there are:

- new datasets
- new columns
- schema changes
- source changes
- pipeline changes
- new event types
- new vendors

### Example operational workflow

```text
Schema registry/source metadata
           ↓
       Schema diff
           ↓
       New field?
          / \
        no   yes
             ↓
         PII scan
             ↓
       Policy validation
             ↓
       Review if needed
             ↓
       Approve / block
```

The goal is to catch privacy drift before the new field propagates widely.

## 34. Detecting PII During Schema and Source Changes

A new column is a common privacy failure point.

Example:

```text
Before:
customer_id
order_id
amount

After:
customer_id
order_id
amount
customer_email   ← new
```

The CI system should detect:

```text
Schema diff
   ↓
New candidate PII field
   ↓
Classification required
   ↓
Policy required
   ↓
PASS / FAIL
```

### Conceptual validator

```python
PII_HINTS = {
    "email", "phone", "passport",
    "national_id", "government_id"
}

def likely_pii_column(name: str) -> bool:
    normalized = name.lower()
    return any(hint in normalized for hint in PII_HINTS)

def validate_schema_change(new_columns: list[str]) -> list[str]:
    findings = []
    for column in new_columns:
        if likely_pii_column(column):
            findings.append(
                f"PII review required for new column: {column}"
            )
    return findings
```

This is a **gate**, not a complete detector.

A production control should combine:

```text
Name heuristics
+
Value scanning
+
Schema metadata
+
Catalog classification
+
Approved policy
```

## 35. Production PII Protection Architecture

A realistic architecture:

```text
                 ┌──────────────────┐
                 │ Source Systems   │
                 │ APIs / DB / SaaS │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Ingestion        │
                 │ API / Kafka      │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ PII Detection    │
                 │ Rules / Presidio │
                 │ Sampling         │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Classification   │
                 │ + Human Review   │
                 └────────┬─────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
       ┌──────────────┐        ┌──────────────┐
       │ Catalog      │        │ Policy       │
       │ PII metadata │        │ Engine       │
       └──────────────┘        └──────┬───────┘
                                      │
                                      ▼
                              Protection policy
                                      │
                                      ▼
                                ┌───────────┐
                                │ Silver    │
                                │ protected │
                                └─────┬─────┘
                                      │
                                      ▼
                                ┌───────────┐
                                │ Gold      │
                                │ minimized │
                                └─────┬─────┘
                                      │
                                      ▼
                                  Consumers
```

Cross-cutting controls:

```text
Access Control
KMS / encryption
Secrets management
Audit logs
Lineage
Monitoring
CI/CD
Retention
Incident response
```

### Layer policy example

```text
Bronze:
restricted raw PII

Silver:
tokenized/pseudonymized customer identity

Gold:
aggregated/minimized analytics
```

This is a design pattern, not a universal requirement. Some workloads may need raw PII in controlled silver processing; others may eliminate it earlier.

## 36. End-to-End Python Data Pipeline Example

The following is an educational pipeline illustrating the control flow.

> **Educational example — not production security infrastructure.**

```python
import hashlib
import hmac
import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

EMAIL_RE = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)

@dataclass
class Finding:
    field: str
    entity: str
    confidence: float

def detect_email(value: str) -> bool:
    return bool(EMAIL_RE.match(value.strip()))

def detect_record(record: dict) -> list[Finding]:
    findings = []

    email = record.get("email")
    if isinstance(email, str) and detect_email(email):
        findings.append(
            Finding("email", "EMAIL", 0.95)
        )

    if "phone" in record:
        findings.append(
            Finding("phone", "PHONE", 0.80)
        )

    return findings

def hmac_id(value: str, key: bytes) -> str:
    return hmac.new(
        key,
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

def mask_email(value: str) -> str:
    local, domain = value.split("@", 1)
    return f"{local[:1]}***@{domain}"

def protect_record(record: dict, key: bytes) -> dict:
    protected = dict(record)

    if "customer_id" in protected:
        protected["customer_token"] = hmac_id(
            str(protected["customer_id"]),
            key,
        )
        del protected["customer_id"]

    if "email" in protected:
        protected["email_masked"] = mask_email(
            protected["email"]
        )
        del protected["email"]

    return protected

incoming = {
    "customer_id": "12345",
    "email": "john@example.com",
    "amount": 125.50,
}

findings = detect_record(incoming)

for finding in findings:
    logger.info(
        "PII candidate detected",
        extra={
            "field": finding.field,
            "entity": finding.entity,
            "confidence": finding.confidence,
        },
    )

protected = protect_record(
    incoming,
    key=b"educational-key",
)

print(protected)
```

The important architecture is:

```text
Incoming record
      ↓
Detect
      ↓
Classify
      ↓
Protection policy
      ↓
Protected record
      ↓
Validation
      ↓
Publish
```

### What the example does not solve

A real system still needs:

- managed secrets
- key rotation
- authorization
- audit logging
- production-grade detection
- human review
- catalog integration
- policy enforcement
- schema-change detection
- secure storage
- retention/deletion
- incident response

## 37. Testing PII Detection and Protection

Privacy controls must be tested like any other production data pipeline behavior.

### Unit tests

Test:

- email detection
- phone detection
- masking
- HMAC generation
- tokenization
- false positives
- false negatives where test fixtures can represent known expectations

Example:

```python
def test_email_detection():
    assert detect_email("john@example.com")
    assert not detect_email("not-an-email")
```

```python
def test_email_masking():
    assert mask_email("john@example.com") == "j***@example.com"
```

```python
def test_hmac_is_deterministic():
    key = b"test-key"

    assert hmac_id("123", key) == hmac_id("123", key)
    assert hmac_id("123", key) != hmac_id("124", key)
```

### Integration tests

Test:

```text
Ingestion
   ↓
PII scanner
   ↓
Classification
   ↓
Catalog tags
   ↓
Protection policy
   ↓
Protected output
```

### Security tests

Test:

- unauthorized access
- unauthorized detokenization
- log leakage
- trace leakage
- metric leakage
- insecure exports

### Regression tests

Create known protected datasets and assert that future pipeline changes do not reintroduce raw PII.

Example:

```python
def test_protected_output_contains_no_email():
    output = run_pipeline(sample_input)

    assert "john@example.com" not in str(output)
```

For real systems, prefer structured assertions over string searches alone.

### Negative testing

Test that sensitive values **do not** appear in:

```text
logs
traces
metrics
alerts
errors
quarantine outputs
test artifacts
```

## 38. Failure Injection and Debugging

### Failure 1 — New PII column without classification

```text
Developer adds:
customer_email
```

Expected:

```text
Schema diff
 ↓
PII candidate
 ↓
Policy check
 ↓
CI failure
```

### Failure 2 — PII in exception logging

Unsafe:

```python
try:
    process(record)
except Exception:
    logger.exception("Failed record=%s", record)
```

If `record` contains PII, the error pipeline becomes a data leak.

Safer:

```python
try:
    process(record)
except Exception:
    logger.exception(
        "Failed record processing",
        extra={"run_id": run_id}
    )
```

### Failure 3 — Kafka consumer logs entire event

Problem:

```text
Raw event
  ↓
Consumer log
  ↓
Central logging system
```

Remediation: log event type, schema version, non-sensitive correlation ID, and error code—not the raw payload.

### Failure 4 — Production copied into development

Controls:

```text
Production export request
        ↓
Policy check
        ↓
Approved protection transformation
        ↓
Masked/tokenized/synthetic dataset
        ↓
Development
```

### Failure 5 — Unknown PII field from new source

Response:

```text
Detection
  ↓
Block/quarantine publication when required
  ↓
Classify
  ↓
Review
  ↓
Apply policy
  ↓
Update catalog
  ↓
Resume
```

### Incident lifecycle

For every failure:

```text
Failure
  ↓
Detection
  ↓
Investigation
  ↓
Containment
  ↓
Remediation
  ↓
Prevention
```

## 39. Common Production Mistakes

### 1. Relying only on regex

**Why:** Easy to implement.

**Danger:** Contextual and unusual PII is missed.

**Correct approach:** Combine rules, metadata, sampling, semantic detection, and review.

### 2. Assuming column names are enough

**Why:** Names are cheap signals.

**Danger:** PII may hide in `payload`, `notes`, or free text.

**Correct approach:** Inspect values and context.

### 3. Assuming automated detection is perfect

**Why:** Machine classification looks objective.

**Danger:** False positives/negatives.

**Correct approach:** Confidence + human review for important assets.

### 4. Treating pseudonymisation as anonymisation

**Danger:** Pseudonyms can remain linkable.

**Correct approach:** Retain appropriate privacy controls.

### 5. Using plain hashing incorrectly

**Danger:** Predictable identifiers can be dictionary-attacked.

**Correct approach:** Evaluate HMAC/keyed techniques and threat model.

### 6. Storing token mappings insecurely

**Danger:** Vault compromise can expose original values.

**Correct approach:** Strong access controls, encryption, audit, key management.

### 7. Leaking PII into logs

**Danger:** Logs become an uncontrolled data copy.

**Correct approach:** Structured allowlisted logging.

### 8. Putting PII into metric labels

**Danger:** Privacy leak plus unbounded cardinality.

**Correct approach:** Bounded dimensions only.

### 9. Putting PII into traces

**Danger:** Trace backends retain span attributes.

**Correct approach:** Allowlist safe attributes.

### 10. Copying production data into development

**Danger:** Expands exposure.

**Correct approach:** Synthetic/masked/tokenized data.

### 11. Ignoring quarantine and DLQs

**Danger:** Failed records often preserve raw PII.

**Correct approach:** Apply the same privacy controls to failure paths.

### 12. Ignoring backups

**Danger:** Old copies survive longer than the active dataset.

**Correct approach:** Lifecycle, encryption, access, and deletion strategy.

### 13. Failing to classify new columns

**Danger:** Schema evolution silently introduces PII.

**Correct approach:** CI/schema-change gates.

### 14. No human review

**Danger:** High-impact automated mistakes.

**Correct approach:** Human approval for ambiguous/high-risk findings.

### 15. No CI enforcement

**Danger:** Controls exist only in documentation.

**Correct approach:** Automated gates.

### 16. No audit trail

**Danger:** Cannot establish who changed classifications or accessed sensitive values.

**Correct approach:** Audit metadata changes, policy decisions, and privileged operations.

### 17. No retention/deletion process

**Danger:** Data survives beyond its useful purpose.

**Correct approach:** Explicit lifecycle controls.

### 18. No key management

**Danger:** Cryptographic protection becomes dependent on insecure secrets.

**Correct approach:** Managed key/secret systems, access control, rotation strategy.

## 40. Security and Privacy Design Principles

### Data minimization

Only collect and propagate what is required.

```text
Need email downstream?
  no → do not propagate
  yes → protect and classify
```

### Least privilege

Users and services should receive the minimum access needed.

### Defense in depth

Use multiple layers:

```text
Classification
+
Access control
+
Encryption
+
Masking
+
Monitoring
+
Audit
+
CI
```

### Privacy by design

Consider privacy during schema and architecture design, not after the pipeline is deployed.

### Purpose limitation

Do not repurpose sensitive data without an appropriate approved basis and policy.

### Separation of duties

The person building a pipeline should not automatically have unrestricted detokenization capability.

### Secure defaults

A new dataset should start restricted rather than exposed.

### Fail closed

If a critical classification/policy check cannot be completed, prefer blocking publication over silently publishing sensitive data without controls.

### Auditability

Record:

- classification decisions
- policy changes
- privileged access
- detokenization
- key-management events where appropriate

### Traceability

Use safe correlation IDs rather than raw personal values.

### Encryption

Protect data at rest and in transit where appropriate. Encryption does not replace access control.

### Key separation

Do not store encryption/HMAC secrets alongside the protected dataset.

### Controlled detokenization

Detokenization should be exceptional, authorized, and auditable.

### Limited exposure

Reduce the number of systems and people that ever receive raw PII.

## 41. Hands-On Production Lab

### Lab objective

Build a local simulation:

```text
Customer Source
      ↓
PII Detection
      ↓
Classification
      ↓
Protection
      ↓
Protected Silver Dataset
      ↓
Analytics Gold Dataset
```

### Lab components

Use:

- Python
- pandas
- pytest
- Microsoft Presidio
- HMAC
- structured logging
- representative sample data

### Step 1 — Create source data

```python
records = [
    {
        "customer_id": "1001",
        "name": "John Doe",
        "email": "john@example.com",
        "amount": 100.50,
    },
    {
        "customer_id": "1002",
        "name": "Jane Doe",
        "email": "jane@example.com",
        "amount": 200.00,
    },
]
```

### Step 2 — Detect

Run rule-based detection and, where installed, Presidio against free-text fields.

### Step 3 — Classify

Produce:

```text
customer_id → identity
name → identity
email → PII/email
amount → business/financial context according to organizational policy
```

Do not assume a universal legal classification for every financial field.

### Step 4 — Protect

Create:

```text
customer_token
email_masked
```

and remove raw fields from the protected output when they are not needed.

### Step 5 — Safe logging

```python
logger.info(
    "Customer processed",
    extra={"customer_token": "tok_example"}
)
```

### Step 6 — Test

Assertions:

```text
raw email absent from protected output
raw ID absent where not required
token deterministic for approved join use
logs do not contain email
classification exists
```

### Step 7 — Failure injection

Intentionally:

1. add an unclassified email column
2. log the raw record
3. omit protection
4. remove the classification
5. change the schema

Verify that the controls detect the failures.

### Learning implementation vs production architecture

The local lab demonstrates concepts.

A production system additionally requires:

- managed secrets/KMS
- secure tokenization infrastructure
- authorization
- audit
- HA
- incident response
- retention/deletion
- policy integration
- schema governance
- continuous scanning

## 42. Checkpoint Questions

### Checkpoint 1

1. What is the difference between a direct identifier and a quasi-identifier?
2. Why is regex insufficient for complete PII detection?
3. When would you choose tokenization over hashing?

**Answers**

1. Direct identifiers can directly identify a person; quasi-identifiers become identifying when combined with other information.
2. Regex lacks business context and misses unexpected/free-text representations.
3. When controlled recovery/detokenization is required or a secure mapping is preferable to a one-way pseudonym.

### Checkpoint 2

1. Why can pseudonymized data still be personal data?
2. Why should PII never appear in metric labels?
3. Why does quarantine data require protection?
4. What should happen when a new PII column appears?

**Answers**

1. The data may remain linkable through keys, mappings, or auxiliary information.
2. It leaks personal data and creates potentially unbounded metric cardinality.
3. Quarantine often contains original failed records.
4. Detect the schema change, classify the field, require policy approval, and block or quarantine publication when required.

### Checkpoint 3

Explain this architecture:

```text
Source
 ↓
Detection
 ↓
Classification
 ↓
Policy
 ↓
Protection
 ↓
Catalog
 ↓
Monitoring
```

A strong answer explains that classification creates metadata, policy determines controls, protection transforms data, and monitoring verifies the system continues to behave safely.

## 43. Interview Preparation

### Beginner

**Q: What is PII?**

A: Information that can identify, describe, contact, or be linked to an individual, depending on context and applicable policy.

**Q: What is masking?**

A: Transforming a value so consumers see a reduced representation instead of the original.

**Q: What is tokenization?**

A: Replacing a sensitive value with a token, often with controlled mapping/detokenization.

### Intermediate

**Q: Hashing vs tokenization?**

A: Hashing is generally one-way; tokenization commonly maintains a protected mapping that supports controlled recovery.

**Q: Static vs dynamic masking?**

A: Static masking transforms a stored copy; dynamic masking changes what a user sees at access time according to policy.

**Q: Direct vs quasi-identifiers?**

A: Direct identifiers identify directly; quasi-identifiers contribute to identification when combined.

**Q: How does Presidio help?**

A: It provides analyzer/recognizer/anonymizer capabilities for detecting and transforming sensitive entities in text.

**Q: Why is pseudonymisation not necessarily anonymisation?**

A: Pseudonyms can remain linkable or reversible with keys/mappings/auxiliary information.

### Advanced

**Q: Design a PII detection pipeline.**

A strong answer combines schema metadata, column heuristics, deterministic rules, sampling, semantic/entity detection, confidence, human review, catalog metadata, and CI/runtime enforcement.

**Q: How do you protect PII in Kafka?**

A: Minimize event payloads, classify schemas, use protected identifiers, restrict topics, control retention/replay/DLQs, and prevent raw payload logging.

**Q: How do you protect observability?**

A: Allowlist safe log/span fields, prohibit PII metric labels, sanitize exceptions and alerts, and test telemetry for leakage.

**Q: How does a token vault work?**

A: A controlled service maps protected tokens to originals and enforces authorization, encryption, auditing, and lifecycle controls.

**Q: What is a linking attack?**

A: Combining multiple datasets or auxiliary information to infer an individual's identity.

**Q: What is k-anonymity?**

A: A model requiring each equivalence class formed by chosen quasi-identifiers to contain at least k records.

**Q: How can CI enforce privacy?**

A: Detect schema changes, identify candidate sensitive fields, require classification/policy metadata, and fail changes that violate approved controls.

### Senior / Production

**Q: How would you protect PII across a lakehouse?**

A: Detect and classify at ingestion, restrict raw/Bronze access, apply deliberate Silver protection, minimize Gold data, integrate catalog/lineage, enforce access, protect observability, and continuously test/schema-scan the system.

**Q: How would you detect an unknown PII field?**

A: Combine schema/name heuristics, value sampling, entity recognition, business metadata, and human review; trigger the process on schema/source changes.

**Q: How would you prevent PII leakage into telemetry?**

A: Establish telemetry schemas/allowlists, prohibit raw payload logging, use safe correlation IDs, bound metric labels, sanitize exceptions, and test logs/traces/alerts.

**Q: How would you design a tokenization service?**

A: Define token format and uniqueness, protected mapping, authorization, encryption, key management, audit, HA, rotation, failure behavior, retention, and controlled detokenization.

**Q: How would you handle a PII exposure incident?**

A: Detect, contain, identify scope and copies, revoke/rotate credentials where appropriate, preserve audit evidence, remediate exposure, assess downstream impact, and implement preventive controls.

**Q: How do you balance privacy, analytics utility, and operations?**

A: Minimize data first, then select the least exposing transformation that still supports the required use case; explicitly evaluate joins, reversibility, accuracy, performance, security, and governance.

## 44. Final Assessment

### Conceptual

1. Define PII.
2. Distinguish direct and quasi-identifiers.
3. Explain why combinations matter.
4. Explain the PII lifecycle across Bronze/Silver/Gold.
5. Explain redaction, masking, pseudonymisation, hashing, and tokenization.
6. Explain re-identification.
7. Explain k-anonymity.
8. Explain differential privacy at an awareness level.

### Python

9. Implement email candidate detection.
10. Implement deterministic HMAC pseudonymisation.
11. Implement safe email masking.
12. Write tests for detection and protection.
13. Build a schema-change PII gate.

### SQL/data engineering

14. Design a Silver-layer transformation that removes raw PII.
15. Design a dynamic masking policy.
16. Explain how quarantine tables can leak PII.
17. Design a protected Kafka event.

### Security

18. Explain how a token vault should be protected.
19. Explain key-management requirements.
20. Explain why plain hashing may be inadequate for predictable identifiers.
21. Explain why PII must not appear in metric labels.
22. Explain how to prevent production data from entering development.

### Architecture

23. Design a continuous PII detection pipeline.
24. Integrate PII classification with a data catalog.
25. Design CI enforcement for new sensitive columns.
26. Design observability privacy controls.
27. Design a PII incident response path.

### Reasoning scenario

A team says:

> “We removed names, so the dataset is anonymous.”

Explain why this statement is insufficient and what additional privacy analysis is required.

## 45. Final Production Challenge

### Scenario

Design a production-grade PII protection strategy for a company processing customer data through:

```text
APIs
Kafka
PostgreSQL
Object Storage
Spark
Lakehouse
Analytics Warehouse
```

### Required design

Your architecture must address:

1. PII detection
2. classification
3. catalog tags
4. Bronze/Silver/Gold policies
5. masking
6. pseudonymisation
7. tokenization
8. access controls
9. encryption
10. telemetry protection
11. CI enforcement
12. continuous scanning
13. auditability
14. incident handling

### Suggested architecture

```text
API
 ↓
Schema validation
 ↓
PII detection
 ↓
Classification
 ↓
Catalog metadata
 ↓
Kafka
 ↓
Restricted Bronze
 ↓
Protection transform
 ↓
Protected Silver
 ↓
Minimized Gold
 ↓
Warehouse
 ↓
Approved consumers
```

Cross-cutting:

```text
        ┌───────────────────────────────┐
        │ IAM / Least Privilege         │
        │ KMS / Secrets                 │
        │ Catalog / Lineage             │
        │ CI/CD / Schema Gates          │
        │ Logging / Tracing Hygiene     │
        │ Audit / Monitoring            │
        │ Retention / Deletion          │
        └───────────────────────────────┘
```

### Trade-off reasoning

**Question: Should Bronze contain raw PII?**

Possibly, if the source of truth requires it and access is highly restricted. But do not retain raw PII merely because “Bronze always equals raw.” Minimize retention and exposure.

**Question: Should Silver always tokenize?**

No. Choose the transformation based on downstream requirements. Some pipelines need deterministic pseudonyms; others can remove the field entirely.

**Question: Should Gold contain customer identifiers?**

Only if the analytical use case requires them and the approved classification/policy allows them. Aggregation and minimization should be preferred where individual-level identity is unnecessary.

**Question: Should PII detection block every unknown field?**

For high-risk datasets, blocking may be appropriate. For lower-risk sources, quarantine/review workflows may be more practical. The control should reflect data criticality and risk.

**Question: Should the catalog enforce masking?**

Not necessarily. The catalog should provide trustworthy classification metadata; policy systems and data platforms should enforce the runtime control.

### Senior-level answer

A production solution is not:

```text
"Run Presidio and mask email."
```

It is:

```text
Detect
 ↓
Classify
 ↓
Review
 ↓
Register metadata
 ↓
Minimize
 ↓
Protect
 ↓
Enforce
 ↓
Observe safely
 ↓
Test continuously
 ↓
Audit
 ↓
Respond to incidents
```

## 46. Glossary

| Term | Meaning |
|---|---|
| PII | Personal information that can identify or be linked to an individual depending on context |
| Personal data | Jurisdiction/context-dependent term for data relating to an identifiable person |
| Sensitive data | Data requiring additional protection under policy or applicable requirements |
| Direct identifier | Identifier capable of directly identifying a person |
| Quasi-identifier | Attribute that contributes to identification when combined with other data |
| Redaction | Removing sensitive information from output |
| Masking | Transforming a value to expose only a reduced representation |
| Dynamic masking | Runtime/role-dependent masking |
| Pseudonymisation | Replacing direct identifiers with controlled pseudonyms |
| Anonymisation | Transformation intended to prevent reasonable identification |
| Hashing | One-way cryptographic transformation |
| HMAC | Keyed hash construction |
| Tokenization | Replacing sensitive values with tokens |
| Token vault | Protected system storing token-to-original mappings |
| Vaultless tokenization | Tokenization architecture without the same centralized mapping vault model |
| Format-preserving encryption | Encryption designed to preserve selected input-format properties |
| Re-identification | Inferring an individual's identity from transformed/de-identified data |
| Linkage attack | Combining datasets to identify or infer individuals |
| k-anonymity | Privacy model based on equivalence classes of quasi-identifiers |
| Differential privacy | Formal privacy framework limiting information leakage about individuals through outputs |
| Data minimization | Limiting collection/processing to what is needed |
| Presidio | Framework for detecting and anonymizing sensitive information |
| Recognizer | Presidio component that identifies entity patterns |
| Analyzer | Presidio engine that produces entity findings and confidence |
| Anonymizer | Component that transforms detected entities |
| Data classification | Labeling data according to sensitivity and governance requirements |

## 47. PII Protection Checklist

```text
[ ] I understand direct vs quasi-identifiers.
[ ] I can identify common PII locations.
[ ] I can implement rule-based detection.
[ ] I understand sampling-based detection.
[ ] I can use Presidio.
[ ] I understand masking.
[ ] I understand dynamic masking.
[ ] I can implement deterministic pseudonymisation.
[ ] I understand HMAC-based pseudonyms.
[ ] I understand tokenization.
[ ] I understand token vault architecture.
[ ] I understand re-identification risks.
[ ] I understand k-anonymity.
[ ] I understand differential privacy at an awareness level.
[ ] I can prevent PII leakage into logs.
[ ] I can prevent PII leakage into traces.
[ ] I can prevent PII leakage into metrics.
[ ] I understand PII in Kafka/events.
[ ] I can protect quarantine data.
[ ] I understand safe test data.
[ ] I can implement continuous scanning.
[ ] I can implement CI PII checks.
[ ] I can design a production PII protection architecture.
[ ] I can test PII protection.
[ ] I can explain key management.
[ ] I can reason about incident response.
```

## 48. Roadmap Coverage Audit

The following audit maps the Topic 06 requirements from the authoritative specification to this module.

| Roadmap Requirement | Covered? | Section | Practical Example? |
|---|---|---|---|
| Direct identifiers | Yes | §3–4 | Yes |
| Quasi-identifiers | Yes | §3–4, §23–24 | Yes |
| Sensitive categories | Yes | §3–4 | Yes |
| PII in columns | Yes | §5–8 | Yes |
| PII in free text | Yes | §6, §10 | Yes |
| PII in JSON | Yes | §5, §30 | Yes |
| PII in logs | Yes | §27 | Yes |
| PII in events | Yes | §30 | Yes |
| PII in quarantine | Yes | §31 | Yes |
| PII in test data | Yes | §32 | Yes |
| Detection rules | Yes | §7 | Yes |
| Checksums | Yes | §7 | Yes |
| Column heuristics | Yes | §8 | Yes |
| Sampling | Yes | §9 | Yes |
| Presidio | Yes | §10 | Yes |
| Human review | Yes | §11 | Yes |
| Redaction | Yes | §13 | Yes |
| Static masking | Yes | §14 | Yes |
| Dynamic masking | Yes | §15 | Yes |
| Keyed hashing | Yes | §17 | Yes |
| Tokenization | Yes | §18 | Yes |
| Token vault | Yes | §19 | Yes |
| Vaultless awareness | Yes | §20 | Yes |
| FPE awareness | Yes | §21 | Yes |
| Re-identification | Yes | §23 | Yes |
| Linking | Yes | §23 | Yes |
| k-anonymity awareness | Yes | §24 | Yes |
| Differential privacy awareness | Yes | §25 | Yes |
| Pseudonymized data remains personal data | Yes | §26 | Yes |
| Telemetry PII prevention | Yes | §27–29 | Yes |
| Continuous scanning | Yes | §33 | Yes |
| Schema/source-change scanning | Yes | §34 | Yes |
| PII metadata/catalog integration | Yes | §12 | Yes |
| Bronze/Silver/Gold protection | Yes | §35 | Yes |
| Production architecture | Yes | §35, §45 | Yes |
| End-to-end Python pipeline | Yes | §36 | Yes |
| Testing | Yes | §37 | Yes |
| Failure injection | Yes | §38 | Yes |
| Common production mistakes | Yes | §39 | Yes |
| Security/privacy principles | Yes | §40 | Yes |
| Hands-on production lab | Yes | §41 | Yes |
| Checkpoints | Yes | §42 | Yes |
| Interview preparation | Yes | §43 | Yes |
| Final assessment | Yes | §44 | Yes |
| Production challenge | Yes | §45 | Yes |
| Glossary | Yes | §46 | Yes |
| Learning checklist | Yes | §47 | Yes |

### Final quality gate

Before treating this module as complete, verify that you can reason through:

```text
What data is personal?
Where can it leak?
How do we detect it?
How confident are we?
Who reviews the classification?
How is the classification recorded?
What protection does the use case require?
Can consumers still join records?
Can the value be recovered?
Where are the keys/mappings?
Can telemetry leak it?
Can schema changes introduce it?
Can developers access it?
How is the control tested?
How is it audited?
What happens during failure?
What happens during an incident?
```

> **Production mastery means treating PII protection as an end-to-end data-platform control, not as a single masking function.**
