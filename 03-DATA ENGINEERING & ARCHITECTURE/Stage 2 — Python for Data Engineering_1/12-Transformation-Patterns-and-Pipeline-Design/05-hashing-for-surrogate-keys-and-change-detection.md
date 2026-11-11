# Hashing for Surrogate Keys and Change Detection

> **Stage 2 — Python for Data Engineering**  
> **Module 2.12 — Transformation Patterns and Pipeline Design**  
> **Topic 05 — Hashing for Surrogate Keys and Change Detection**
>
> Hashing is not being taught here as computer-science theory. It is being taught as a **Data Engineering design primitive** for stable identity, change detection, reconciliation, deterministic sampling, partitioning, and privacy-aware pseudonymization.

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- explain what a hash is from first principles;
- distinguish hashing from encryption;
- distinguish cryptographic and non-cryptographic hashing;
- explain the practical roles of SHA-256, SHA-1, MD5, xxHash, and MurmurHash;
- build deterministic hash keys from business keys;
- use hash-based surrogate-key fingerprints safely;
- build hash-diffs for change detection;
- use hash-diffs in SCD Type 2-style processing;
- design a canonical serialization contract;
- normalize strings, NULLs, numbers, decimals, timestamps, and time zones;
- make Python and SQL produce the same hash when required;
- understand hexadecimal, binary, and 64-bit representations;
- estimate collision risk;
- understand birthday-bound intuition;
- use hashes for deterministic sampling and partitioning;
- use fingerprints as one layer of data reconciliation;
- reason about schema changes and hash-contract compatibility;
- distinguish plain hashing from privacy protection;
- use HMAC for keyed pseudonymization where appropriate;
- design, test, version, and operate a production hash contract.

The central mental model is:

```text
Business key
    ↓
canonical representation
    ↓
hash
    ↓
deterministic surrogate / identity fingerprint
```

For change detection:

```text
Descriptive attributes
    ↓
canonical representation
    ↓
hash
    ↓
change-detection fingerprint
```

The most important lesson is:

> **The hash function itself is often not the hardest part. The difficult part is defining exactly what bytes are being hashed.**

---

## 2. Prerequisites

This topic assumes you already understand:

- deterministic pipeline structure;
- logical data intervals;
- partition-scoped processing;
- deduplication;
- merge/upsert strategies;
- incremental processing;
- backfills;
- late-arriving data;
- reprocessing windows;
- business keys and dimensions at a conceptual level.

The dependency chain is:

```text
01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09
```

Topic 05 builds on the previous topics:

```text
idempotent merges
       +
incremental processing
       +
late-data correction
       ↓
stable identity + efficient change detection
```

You do not need to memorize cryptography mathematics before starting this chapter. The required concepts are introduced progressively.

---

# 3. Why Hashing Matters in Data Engineering

Imagine five source systems contain the same customer:

```text
CRM     → customer_id = C123
ERP     → customer_id = 998812
Billing → account_no  = B-771
Support → user_id     = U-91
```

You need a stable way to represent identity across transformations.

You also need to answer:

> Did this customer's descriptive information change?

A naive comparison might compare every column:

```text
name
country
status
segment
address
phone
...
```

A fingerprint can compress the comparison:

```text
descriptive columns
       ↓
canonical representation
       ↓
hash
       ↓
attribute_hash
```

Then:

```text
old_attribute_hash == new_attribute_hash
    → no detected change

old_attribute_hash != new_attribute_hash
    → detected change
```

This can make merge and SCD logic easier to reason about.

### Important qualification

A hash is not magic.

It does not automatically provide:

- uniqueness;
- encryption;
- anonymization;
- perfect equality proof;
- a correct business key;
- stable cross-system compatibility.

Those properties depend on the design around the hash.

---

# 4. What Is a Hash?

A hash function takes input of arbitrary size and produces a fixed-size output.

For example:

```python
import hashlib

value = b"customer-123"

digest = hashlib.sha256(value).hexdigest()

print(digest)
```

The important pieces are:

- `b"customer-123"` is a sequence of **bytes**;
- `sha256` is the hash algorithm;
- `digest` is the raw hash result represented here as hexadecimal text;
- `hexdigest()` converts the digest bytes into readable hexadecimal characters.

The same bytes produce the same digest:

```python
import hashlib

a = hashlib.sha256(b"hello").hexdigest()
b = hashlib.sha256(b"hello").hexdigest()

assert a == b
```

A tiny input change normally produces a very different digest:

```python
a = hashlib.sha256(b"hello").hexdigest()
b = hashlib.sha256(b"Hello").hexdigest()

assert a != b
```

### A beginner analogy

Think of a hash as a compact fingerprint of input data.

```text
Input
  ↓
Fingerprint machine
  ↓
Fixed-size fingerprint
```

The fingerprint is useful for comparison, but it is not the original object.

---

# 5. Hash Function Properties

Important properties include:

### Deterministic

The same input produces the same output.

```text
X → H(X)
X → H(X)
```

The result is the same.

### Fixed-size output

A SHA-256 digest is always 256 bits regardless of whether the input is:

```text
"hi"
```

or a multi-megabyte message.

### Avalanche effect

For well-designed cryptographic hashes, a small input change causes a large-looking output change.

```text
hello
  ↓
hash A

Hello
  ↓
hash B
```

`hash A` and `hash B` should not look nearly identical simply because the inputs differ by one character.

### Collision resistance

Different inputs should be difficult to make produce the same output, within the security assumptions of the algorithm.

### Preimage resistance

For appropriate cryptographic hashes, given a digest, it should be computationally difficult to recover an arbitrary input that produces it.

### Speed

Some hashes are deliberately designed to be very fast.

This is where cryptographic and non-cryptographic hashes differ.

> **Do not assume every hash function has the same security properties.**

---

# 6. Hashes vs Encryption

Hashing and encryption solve different problems.

## Encryption

```text
plaintext
    ↓
encryption + key
    ↓
ciphertext
    ↓
decryption + key
    ↓
plaintext
```

Encryption is designed to be reversible for authorized parties.

Examples in Data Engineering include:

- encrypting files;
- protecting database fields;
- encrypting data in transit or at rest.

## Hashing

```text
input
  ↓
hash
  ↓
digest
```

A cryptographic hash is designed as a one-way construction rather than a reversible encoding.

### Practical distinction

If you need to retrieve the original value:

```text
encryption
```

may be appropriate.

If you need to compare whether a canonical representation changed:

```text
hash
```

may be appropriate.

If you need to pseudonymize an identifier across systems:

```text
HMAC
```

may be appropriate, depending on the threat model.

> A hash is not "encrypted data."

---

# 7. Cryptographic vs Non-Cryptographic Hashes

| Property | Cryptographic hash | Non-cryptographic hash |
|---|---|---|
| Primary goal | Security properties + fingerprinting | Speed/distribution |
| Examples | SHA-256, SHA-1, MD5 | xxHash, MurmurHash |
| Typical speed | Usually slower | Usually very fast |
| Adversarial use | Some algorithms designed for it | Generally not |
| Data Engineering use | Durable fingerprints, interoperability, integrity-related uses | Bucketing, partitioning, fast local fingerprints |
| Privacy construction | Can be combined with keyed constructions | Not a privacy primitive |
| Collision reasoning | Security-oriented analysis | Distribution/performance-oriented analysis |

### SHA-256

Modern cryptographic hash commonly used for:

- durable fingerprints;
- cross-system identity representations;
- integrity-related fingerprints;
- change detection where a strong digest is desired.

### SHA-1

SHA-1 is historically important but has known collision weaknesses. Do not choose SHA-1 for new security-sensitive cryptographic applications.

It may still appear in:

- legacy systems;
- historical datasets;
- compatibility requirements.

### MD5

MD5 is also cryptographically broken for collision resistance.

It can still appear in:

- legacy pipelines;
- non-adversarial compatibility checks;
- historical checksums.

Do not describe MD5 as a modern secure cryptographic choice.

### xxHash

xxHash is designed for very fast non-cryptographic hashing.

Good candidates include:

- partition/bucket assignment;
- fast fingerprints;
- local data-processing workloads.

Do not use it as a cryptographic security mechanism.

### MurmurHash

MurmurHash is another widely used non-cryptographic hash family.

It is useful for:

- hash tables;
- partitioning;
- bucketing;
- deterministic distribution.

Again, it is not a cryptographic privacy primitive.

---

# 8. SHA-256, SHA-1, MD5, xxHash, and MurmurHash

A useful decision table:

| Algorithm | Class | Typical role | Security-sensitive? |
|---|---|---|---|
| SHA-256 | Cryptographic | Durable fingerprints, identity/change detection | Yes, where appropriate |
| SHA-1 | Cryptographic, legacy | Compatibility/historical | No for new collision-resistant security uses |
| MD5 | Cryptographic, broken for modern security | Legacy/checksum compatibility | No |
| xxHash | Non-cryptographic | Fast bucketing/fingerprinting | No |
| MurmurHash | Non-cryptographic | Fast distribution/bucketing | No |

The correct question is not:

> "Which algorithm is strongest?"

It is:

> **"What guarantee do I need, and what workload am I optimizing?"**

For example:

```text
deterministic bucket assignment
    → fast non-cryptographic hash may be appropriate

durable cross-system identifier
    → strong, stable contract may favor SHA-256

pseudonymization with a secret
    → HMAC-based construction
```

---

# 9. Deterministic Hashing

Determinism means:

```text
same canonical input
        ↓
same hash
```

Example:

```python
import hashlib

def hash_value(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()
```

Then:

```python
assert hash_value("customer-123") == hash_value("customer-123")
```

This matters because Data Engineering systems are distributed.

The same logical record may be processed by:

```text
Python worker A
Python worker B
SQL engine
warehouse
backfill job
reconciliation job
```

If the canonical input and algorithm are identical, each can calculate the same fingerprint.

### Determinism is a contract

Do not write:

```python
hash(value)
```

and assume Python's built-in `hash()` is a durable cross-process/cross-language identity mechanism.

Python's built-in hash is primarily intended for in-process data structures such as dictionaries and sets. It is not a production cross-system hashing contract.

Use an explicitly selected algorithm such as:

```python
hashlib.sha256(...)
```

or a deliberately selected non-cryptographic implementation.

---

# 10. Canonical Serialization

This is one of the most important concepts in the chapter.

Suppose the logical record is:

```text
customer_id = 123
country     = IN
status      = ACTIVE
```

You need a deterministic representation before hashing:

```text
123|IN|ACTIVE
```

Then:

```text
canonical string
      ↓
UTF-8 bytes
      ↓
hash
```

### Why this matters

These are different byte sequences:

```text
123|IN|ACTIVE
```

and:

```text
IN|123|ACTIVE
```

Even though they contain the same three values.

Therefore:

> **The serialization contract is part of the hash contract.**

### What the contract must define

At minimum:

- column order;
- delimiter;
- delimiter escaping;
- NULL representation;
- string trimming;
- case normalization rules;
- numeric formatting;
- decimal scale;
- timestamp timezone;
- timestamp precision;
- encoding;
- hash algorithm;
- output representation;
- contract version.

### Do not rely on arbitrary object serialization

Avoid making a durable hash contract depend on:

```python
str(dict)
```

or an implementation-specific object representation.

Instead, explicitly construct the canonical representation.

---

# 11. Column Ordering and Delimiters

Column order must be fixed.

Compare:

```text
123|IN|ACTIVE
```

with:

```text
IN|123|ACTIVE
```

The hashes differ.

Therefore:

```python
KEY_COLUMNS = [
    "customer_id",
    "country",
    "status",
]
```

should be part of a documented contract.

## Delimiter ambiguity

Naive concatenation can be ambiguous.

Suppose:

```text
field_1 = "AB"
field_2 = "C"
```

and:

```text
field_1 = "A"
field_2 = "BC"
```

Both can become:

```text
ABC
```

A delimiter helps:

```text
AB|C
A|BC
```

But even delimiters can occur inside values.

For example:

```text
country = "US|CA"
```

A robust contract therefore needs one of:

- escaping;
- length-prefixing;
- a structured serialization format;
- another representation with unambiguous boundaries.

### Simple escaping example

```python
DELIMITER = "|"
ESCAPE = "\\"

def escape_value(value: str) -> str:
    return (
        value
        .replace(ESCAPE, ESCAPE + ESCAPE)
        .replace(DELIMITER, ESCAPE + DELIMITER)
    )
```

The exact escape convention must be shared by every implementation.

---

# 12. Canonicalizing Strings

Consider:

```text
"India"
" india "
"INDIA"
```

Should they produce the same hash?

There is no universal answer.

It depends on business semantics.

If the business says country codes are case-insensitive and whitespace is irrelevant, you may define:

```python
value.strip().upper()
```

But if the field is case-sensitive, changing case would change its meaning.

### A canonicalization policy might say

```text
trim leading/trailing whitespace
preserve internal whitespace
preserve case
normalize Unicode using documented rules
```

or:

```text
trim
uppercase
```

The important principle is:

> **Do not normalize because it is convenient. Normalize because the business semantics require it.**

### Empty string is not automatically NULL

These can represent different states:

```text
None
""
"<NULL>"
" "
```

Your contract must decide.

---

# 13. NULL Handling

NULL handling is critical.

Do not accidentally make:

```text
NULL
```

indistinguishable from:

```text
""
```

or:

```text
"NULL"
```

A simple canonical token is:

```text
<NULL>
```

Example:

```python
NULL_TOKEN = "<NULL>"

def canonicalize(value):
    if value is None:
        return NULL_TOKEN
    return str(value)
```

But there is an important caveat.

What if a real business value is literally:

```text
<NULL>
```

Then the token is ambiguous.

A robust production contract must guarantee that the NULL representation cannot collide with a valid serialized value.

Options include:

- escaping reserved tokens;
- length-prefixed fields;
- typed structured serialization.

### Test it

```python
assert canonicalize(None) == "<NULL>"
assert canonicalize("") == ""
assert canonicalize("<NULL>") != canonicalize(None)
```

The final assertion only works if your serialization contract explicitly distinguishes the two.

---

# 14. Number and Decimal Canonicalization

These values may be semantically identical:

```text
1
1.0
1.00
```

or they may not be, depending on the field.

For money, you often want an explicit decimal scale.

```python
from decimal import Decimal

value = Decimal("1.00")
canonical = format(value, ".2f")

assert canonical == "1.00"
```

If the contract says two decimal places:

```text
1
1.0
1.00
```

can all become:

```text
1.00
```

### Avoid blind float serialization

Binary floating-point can represent decimal values approximately.

For example:

```python
0.1
```

does not have an exact finite binary floating-point representation.

For durable financial-style canonicalization, prefer an explicit decimal representation:

```python
from decimal import Decimal

amount = Decimal("10.50")
```

and define the scale and rounding behavior.

### Contract example

```text
amount:
- Decimal
- scale = 2
- rounding = explicitly defined
- serialization = fixed-point text
```

Do not let a Python/SQL type conversion silently decide your hash contract.

---

# 15. Timestamp and Time-Zone Canonicalization

Consider:

```text
2025-03-01 10:00 UTC
```

and:

```text
2025-03-01 15:30 IST
```

Depending on the actual timezone offset, these may represent the same instant.

If one system hashes the UTC representation and another hashes local wall-clock text, the hashes can differ even though the timestamps represent the same instant.

### Production rule

If the semantic field represents an instant, normalize to a common timezone, commonly UTC:

```text
source timestamp
      ↓
timezone-aware conversion
      ↓
UTC
      ↓
defined precision
      ↓
canonical string
      ↓
hash
```

### Precision must be defined

These are not necessarily the same:

```text
2025-03-01T10:00:00.123Z
2025-03-01T10:00:00.123000Z
```

Define whether the contract uses:

```text
seconds
milliseconds
microseconds
```

and normalize accordingly.

### Python example

```python
from datetime import datetime, timezone

def canonical_timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("Timestamp must be timezone-aware")

    value = value.astimezone(timezone.utc)

    # Example contract: microsecond precision.
    return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
```

The actual project contract may choose another format, but every implementation must use the same one.

---

# 16. Business-Key Hashes

A business-key hash represents identity.

The pattern is:

```text
business key columns
        ↓
canonical serialization
        ↓
hash
        ↓
stable identity fingerprint
```

Example:

```text
source_system = CRM
customer_id   = C123
```

Canonical:

```text
CRM|C123
```

Python:

```python
import hashlib

def customer_key(source_system: str, customer_id: str) -> str:
    canonical = f"{source_system}|{customer_id}"
    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()
```

### Why include source system?

Without it:

```text
CRM:C123
ERP:C123
```

could collapse to the same representation if only `C123` were hashed.

Including the source namespace makes the identity definition explicit:

```text
CRM|C123
ERP|C123
```

produce different fingerprints.

### Business-key hash versus entity resolution

A deterministic hash does **not** discover that:

```text
CRM:C123
```

and:

```text
ERP:998812
```

are the same human/customer.

It only produces a stable fingerprint **after you have defined the canonical identity input**.

Entity resolution is a separate problem.

---

# 17. Hash-Based Surrogate Keys

A surrogate key is an identifier used by a data model rather than being the original business identifier.

Traditional example:

```text
customer_key = 5821
```

Hash-based example:

```text
customer_key = SHA256(canonical_business_key)
```

## Advantages

Hash-based keys can be:

- deterministic;
- reproducible;
- generated independently by workers;
- parallel-safe;
- stable across reloads;
- convenient across distributed systems.

No centralized sequence table is required.

## Disadvantages

They can be:

- larger than integer keys;
- less human-readable;
- more expensive to store/index;
- sensitive to canonicalization changes;
- subject to collision risk;
- difficult to migrate after publication.

### Comparison

| Approach | Deterministic | Distributed | Compact | Human-readable |
|---|---:|---:|---:|---:|
| Sequence integer | No across rebuilds | Usually requires coordination | Yes | Often |
| UUID | Yes | Yes | Moderate | No |
| Hash fingerprint | Yes | Yes | Depends | No |

Do not present hash keys as universally better.

The correct choice depends on:

- scale;
- interoperability;
- storage;
- warehouse indexing;
- reproducibility requirements;
- source identity semantics.

---

# 18. Hash-Diffs for Change Detection

This is a central Data Engineering use case.

Separate:

```text
identity
```

from:

```text
descriptive state
```

For example:

```text
business-key columns:
source_system
customer_id
```

and:

```text
descriptive columns:
name
country
status
segment
```

Create two fingerprints:

```text
business_key_hash
attribute_hash
```

Then:

```text
business_key_hash
    → identifies the logical entity

attribute_hash
    → fingerprints the descriptive state
```

If:

```text
old_attribute_hash != new_attribute_hash
```

a change is detected.

### Why this is useful

It can simplify:

- SCD Type 2 change detection;
- merge logic;
- incremental transformation;
- CDC validation;
- Data Vault satellite change detection;
- reconciliation.

### Important limitation

A hash difference says:

> The canonicalized inputs differ.

It does not explain **which** attribute changed.

For debugging and audit, you may still need column-level comparisons.

---

# 19. SCD Change-Detection Example

Initial customer:

```text
customer_id | name  | country | status
------------+-------+---------+--------
C123        | Alice | India   | ACTIVE
```

Later:

```text
customer_id | name  | country   | status
------------+-------+-----------+--------
C123        | Alice | Singapore | ACTIVE
```

Identity is unchanged:

```text
business_key_hash
        SAME
```

Descriptive state changed:

```text
attribute_hash
        DIFFERENT
```

A Type 2-style process can then:

```text
close old version
      ↓
insert new version
```

Example:

```text
customer_key | valid_from | valid_to | country
-------------+------------+----------+---------
K1           | 2025-01-01 | 2025-03-10 | India
K2           | 2025-03-10 | NULL       | Singapore
```

The exact surrogate-key strategy may differ. The important part is that the hash-diff identifies the change.

---

# 20. Which Columns Should Be Included in a Hash-Diff?

This is a production design decision.

Suppose a row contains:

```text
customer_id
name
country
status
updated_at
_ingested_at
_run_id
source_file
```

You probably do not want:

```text
_ingested_at
_run_id
```

to trigger a business-state change.

The hash-diff should normally include:

```text
business-relevant descriptive attributes
```

and exclude operational metadata.

### Rule

> **Metadata columns should never enter a business-state hash-diff unless the explicit business requirement says they define state.**

Otherwise every pipeline run could look like a data change.

### Example

```python
HASH_DIFF_COLUMNS = [
    "name",
    "country",
    "status",
]
```

Not:

```python
HASH_DIFF_COLUMNS = df.columns
```

unless the schema itself is deliberately the contract.

---

# 21. A Formal Canonical Serialization Contract

A production hash contract could be:

```text
Contract version:
v1

Business-key columns:
source_system
customer_id

Hash-diff columns:
name
country
status
segment

String normalization:
trim leading/trailing whitespace

Case:
preserve

NULL:
reserved escaped token

Numbers:
Decimal with explicit scale

Timestamps:
UTC

Timestamp precision:
microseconds

Encoding:
UTF-8

Column order:
exactly as listed

Delimiter:
|

Delimiter escaping:
backslash escaping

Hash:
SHA-256

Output:
lowercase hexadecimal

Metadata columns:
excluded
```

This contract is more important than merely writing:

```text
"we use SHA-256"
```

Two teams can both use SHA-256 and still produce different hashes.

---

# 22. Python Implementation

A robust example should make canonicalization explicit.

```python
from __future__ import annotations

import hashlib
from decimal import Decimal
from datetime import datetime, timezone

DELIMITER = "|"
ESCAPE = "\\"
NULL_TOKEN = "<NULL>"


def escape_text(value: str) -> str:
    return (
        value
        .replace(ESCAPE, ESCAPE + ESCAPE)
        .replace(DELIMITER, ESCAPE + DELIMITER)
    )


def canonicalize(value) -> str:
    if value is None:
        return NULL_TOKEN

    if isinstance(value, datetime):
        if value.tzinfo is None:
            raise ValueError("datetime must be timezone-aware")

        value = value.astimezone(timezone.utc)
        return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    if isinstance(value, Decimal):
        return format(value, "f")

    if isinstance(value, str):
        return escape_text(value.strip())

    return escape_text(str(value))


def canonical_row(values: list) -> str:
    return DELIMITER.join(
        canonicalize(value)
        for value in values
    )


def hash_row(values: list) -> str:
    canonical = canonical_row(values)

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()
```

### Example

```python
key = hash_row([
    "CRM",
    "C123",
])

diff = hash_row([
    "Alice",
    "India",
    "ACTIVE",
])
```

### Important production caveat

This example is educational.

A production implementation should also:

- define reserved-token escaping formally;
- define numeric types explicitly;
- define supported timestamp types;
- pin behavior with test vectors;
- publish the contract version;
- test against every target engine.

---

# 23. SQL Implementation

A compatible SQL engine such as DuckDB can conceptually implement:

```text
canonical representation
        ↓
SHA-256
        ↓
hash
```

For example:

```sql
SELECT
    sha256(
        CAST(
            source_system || '|' || customer_id
            AS BLOB
        )
    ) AS business_key_hash
FROM customers;
```

For a hash-diff:

```sql
SELECT
    sha256(
        CAST(
            COALESCE(name, '<NULL>') || '|' ||
            COALESCE(country, '<NULL>') || '|' ||
            COALESCE(status, '<NULL>')
            AS BLOB
        )
    ) AS attribute_hash
FROM customers;
```

This is illustrative rather than a universal SQL standard.

Different SQL engines expose:

- different hash functions;
- different string-to-byte behavior;
- different NULL semantics;
- different timestamp formatting;
- different binary conversion functions.

Therefore:

> **Never assume Python and SQL hash results will match merely because both say "SHA-256."**

The bytes must be identical.

---

# 24. Python/SQL Hash Parity

Cross-engine parity should be tested deliberately.

The parity workflow is:

```text
1. Build canonical representation in Python
          ↓
2. Build canonical representation in SQL
          ↓
3. Compare canonical representations
          ↓
4. Compare bytes if necessary
          ↓
5. Compare hash values
          ↓
6. Diagnose the first difference
```

### Test vector

Use a small fixed test set:

```text
source_system = CRM
customer_id   = C123
name          = Alice
country       = India
status        = ACTIVE
```

Expected canonical forms:

```text
CRM|C123
```

and:

```text
Alice|India|ACTIVE
```

Store expected hashes as test vectors.

### Why compare canonical strings first?

Suppose:

```text
Python hash != SQL hash
```

The immediate instinct may be:

> "The hash implementation is broken."

Usually the more useful question is:

> "Did both systems hash exactly the same bytes?"

Compare:

```text
Python canonical:
CRM|C123

SQL canonical:
CRM|C123 
```

That trailing space is enough to change the digest.

### Common parity failures

- NULL representation;
- column order;
- whitespace;
- case;
- timestamp formatting;
- timezone conversion;
- decimal formatting;
- delimiter escaping;
- character encoding;
- implicit type casts.

---

# 25. Hash Storage: Hex, Binary, and 64-bit Values

A SHA-256 digest contains:

```text
256 bits
=
32 bytes
```

### Hexadecimal

A 32-byte digest represented as hexadecimal requires:

```text
64 hex characters
```

Example:

```text
9f86d081884c7d65...
```

**Advantages:**

- human-readable;
- easy to log;
- widely interoperable.

**Disadvantages:**

- twice the byte width of the raw digest;
- larger indexes and storage.

### Binary

Store the raw 32-byte digest.

**Advantages:**

- compact;
- exact representation;
- efficient storage.

**Disadvantages:**

- less human-readable;
- tooling may be less convenient.

### 64-bit hash

A 64-bit hash uses:

```text
8 bytes
```

This is much smaller.

It can be useful for:

- bucketing;
- partitioning;
- fast fingerprints.

But the collision space is much smaller than SHA-256.

### Important

If you truncate a SHA-256 digest:

```text
SHA-256
    ↓
take first 8 bytes
    ↓
64-bit value
```

you no longer have 256-bit collision resistance.

The effective collision space is the truncated width.

---

# 26. Collision Probability

A collision occurs when:

```text
different inputs
      ↓
same hash
```

Every finite hash function has a finite number of outputs.

If the hash has `n` bits, the output space has:

```text
2^n
```

possible values.

Therefore, no finite hash can mathematically guarantee uniqueness for unlimited arbitrary inputs.

### Why this matters

Suppose you have:

```text
10 billion rows
```

and use a 32-bit hash.

There are only:

```text
2^32
```

possible outputs, roughly 4.3 billion.

You are putting more logical records into the system than there are possible 32-bit values, so collisions are unavoidable by the pigeonhole principle.

Even when the number of rows is smaller than the number of possible values, collisions can become likely much earlier than intuition suggests.

---

# 27. Birthday Bound Intuition

The birthday paradox explains why collisions become significant sooner than:

```text
number of rows ≈ number of possible hashes
```

would suggest.

For an `n`-bit uniformly distributed hash, collision probability becomes material around roughly:

```text
2^(n/2)
```

samples.

This is an intuition, not a universal exact threshold.

### Approximate scales

| Hash width | Output space | Birthday-scale intuition |
|---:|---:|---:|
| 32-bit | ~4.3 × 10^9 | ~65,536 |
| 64-bit | ~1.84 × 10^19 | ~4.3 × 10^9 |
| 128-bit | ~3.4 × 10^38 | ~1.8 × 10^19 |
| 256-bit | ~1.16 × 10^77 | ~3.4 × 10^38 |

The exact probability depends on the number of samples and distribution assumptions.

### 10^9 rows example

For approximately one billion rows:

```text
32-bit
→ collisions are overwhelmingly expected

64-bit
→ collision probability is not negligible

128-bit
→ extremely small under ordinary assumptions

256-bit
→ vastly smaller still
```

This is why "just use a 32-bit hash" is usually a poor durable-identity decision at large scale.

---

# 28. Collision Risk and Engineering Trade-Offs

Choose hash width based on:

- record count;
- number of historical versions;
- whether values are adversarially chosen;
- acceptable collision risk;
- storage;
- performance;
- interoperability;
- consequence of a collision.

### A 64-bit hash can be reasonable for

- deterministic partitioning;
- bucketing;
- non-security sampling;
- fast approximate fingerprints.

### A stronger digest can be appropriate for

- durable cross-system identity fingerprints;
- audit-sensitive change detection;
- long-lived datasets;
- compatibility across multiple platforms.

### Collision strategy

For critical identity systems, consider:

```text
hash
  +
original business key
  +
uniqueness validation
```

For example, enforce:

```text
business_key_hash
```

as a candidate key while retaining the original business-key columns.

If two different business keys ever produce the same hash, the collision can be detected instead of silently merging the entities.

> **Do not promise zero collision risk.**

---

# 29. Deterministic Sampling

Hashes can create deterministic pseudo-random samples.

Conceptually:

```text
hash(customer_id) % 100
```

Then:

```text
0–9 → approximately 10%
```

of uniformly distributed hash values.

### Why this is useful

A random sample can change every run.

A deterministic hash sample gives:

```text
customer A
    ↓
always in bucket 7
```

assuming the hash contract remains unchanged.

This is useful for:

- QA;
- pipeline validation;
- canary datasets;
- reproducible sampling;
- debugging.

### Example

```python
def sample_bucket(hash_integer: int, buckets: int = 100) -> int:
    return hash_integer % buckets
```

For a cryptographic hexadecimal digest:

```python
digest = hashlib.sha256(
    b"C123"
).digest()

bucket = int.from_bytes(digest[:8], "big") % 100
```

### Important

Deterministic sampling is not a security randomization mechanism.

It also depends on the hash distribution and the selected hash contract.

---

# 30. Hash-Based Partitioning

A common conceptual strategy is:

```text
partition = hash(key) % N
```

For example:

```text
partition = hash(customer_id) % 16
```

This can distribute entities across:

```text
partition 0
partition 1
...
partition 15
```

### Benefits

- deterministic routing;
- parallel processing;
- simple bucket assignment;
- no centralized assignment table.

### Risks

#### Skew

A poor hash or highly structured input can produce uneven distribution.

#### Changing partition count

Suppose:

```text
hash(key) % 16
```

becomes:

```text
hash(key) % 32
```

Many keys move.

That can require data reshuffling.

#### Compatibility

Different hash functions or serialization rules can route the same key to different partitions.

### Hash partitioning vs time partitioning

Time partitioning:

```text
event_date = 2025-03-01
```

is excellent for time-bounded analytics and retention.

Hash partitioning:

```text
hash(customer_id) % 16
```

is useful for spreading entities across workers or storage buckets.

They solve different problems and can sometimes be combined.

---

# 31. Hashes for Data Reconciliation

Hashes can help compare source and target datasets.

Conceptually:

```text
Source
  ↓
row fingerprints
  ↓
partition fingerprint

Target
  ↓
row fingerprints
  ↓
partition fingerprint

        ↓
compare
```

### Row-level fingerprint

For example:

```text
customer_id
name
country
status
```

becomes:

```text
row_hash
```

### Partition-level fingerprint

You can aggregate information about a partition to detect likely differences.

However:

> **A single aggregate hash should not automatically be treated as a mathematically perfect proof of equality.**

Use hashes as one layer of reconciliation alongside:

- row counts;
- sums;
- min/max;
- key counts;
- sampled comparisons;
- business invariants.

### Practical reconciliation

```text
row count
    +
business-key count
    +
aggregate metrics
    +
deterministic fingerprints
    ↓
higher-confidence reconciliation
```

---

# 32. Hashes for SCD Change Detection

For an SCD Type 2 dimension:

```text
incoming customer
       ↓
calculate business_key_hash
       ↓
find existing entity
       ↓
calculate attribute_hash
       ↓
compare
```

If:

```text
attribute_hash == current_attribute_hash
```

then:

```text
no business-state change
```

If:

```text
attribute_hash != current_attribute_hash
```

then:

```text
business-state change detected
```

### Merge-style SQL pattern

Conceptually:

```sql
MERGE INTO dim_customer AS target
USING staged_customer AS source
ON target.business_key_hash = source.business_key_hash
AND target.is_current = TRUE

WHEN MATCHED
     AND target.attribute_hash <> source.attribute_hash
THEN
    -- close current version / stage new version

WHEN NOT MATCHED
THEN
    -- insert new entity
;
```

For SCD Type 2, actual implementation generally needs a deliberate close-and-insert pattern rather than treating `MERGE` as a complete SCD engine.

### Metadata exclusion

Do not include:

```text
_ingested_at
_run_id
_loaded_by
source_file
```

in the business-state hash unless they intentionally define the state.

---

# 33. Schema Changes and Hash Compatibility

Schema evolution creates a subtle problem.

Old contract:

```text
name|country|status
```

New contract:

```text
name|country|status|segment
```

If `segment` is included in the hash-diff, every row may receive a new hash.

That may look like:

```text
every customer changed
```

even if the original business attributes did not change.

### Strategies

#### Strategy A — Version the hash contract

```text
hash_contract_v1
hash_contract_v2
```

Store the version alongside the fingerprint.

#### Strategy B — Preserve the old hash

Keep:

```text
attribute_hash_v1
```

while introducing:

```text
attribute_hash_v2
```

#### Strategy C — Add a new hash only for new logic

Useful when historical comparability matters.

#### Strategy D — Controlled backfill

If the new schema genuinely changes the business-state definition, intentionally recompute history.

### Key distinction

A schema change can be:

```text
technical change
```

or:

```text
business-state change
```

Do not let the hash contract accidentally confuse the two.

---

# 34. HMAC and Pseudonymization

HMAC means:

```text
HMAC(key, message)
```

It is a keyed cryptographic construction.

Conceptually:

```text
identifier
    +
secret key
    ↓
HMAC
    ↓
pseudonymous identifier
```

Compare:

```text
SHA256(email)
```

with:

```text
HMAC(secret, email)
```

The second requires the secret key to reproduce the pseudonym.

### Why the secret matters

If an attacker knows:

```text
SHA256(email)
```

they can hash candidate emails and look for a match.

If the construction uses a protected secret:

```text
HMAC(secret, email)
```

the attacker also needs the secret to reproduce the mapping.

### Python example

```python
import hashlib
import hmac

secret = b"example-development-secret"

email = b"alice@example.com"

token = hmac.new(
    secret,
    email,
    hashlib.sha256,
).hexdigest()

print(token)
```

Never put real production secrets directly into source code.

Use an approved secret-management system.

---

# 35. Why Plain Hashes Do Not Anonymize PII

Consider:

```text
alice@example.com
```

A plain SHA-256 hash looks random:

```text
SHA256(email)
```

but email addresses often have a small enough practical search space for an attacker to enumerate candidates.

An attacker can do:

```text
candidate email
      ↓
SHA-256
      ↓
compare to target hash
```

This is a dictionary or guessing attack.

The same issue applies to:

- phone numbers;
- usernames;
- postal codes;
- customer identifiers;
- other low-entropy values.

Therefore:

> **SHA-256(email) is not automatically anonymization.**

### Pseudonymization vs anonymization

**Pseudonymization** means replacing an identifying value with another value while linkage may remain possible under controlled conditions.

**Anonymization** implies a stronger privacy property where re-identification is not reasonably possible under the applicable threat model.

Do not claim:

```text
HMAC → automatically anonymous
```

HMAC can provide a stronger keyed pseudonymization mechanism, but privacy depends on:

- secret protection;
- access controls;
- linkage opportunities;
- surrounding data;
- threat model;
- retention;
- governance.

Privacy details belong more deeply in later security/governance material; this chapter establishes the engineering primitive and its limitations.

---

# 36. Production Hashing Design

A production hash contract should look like an explicit specification, not an undocumented function.

Example:

```text
Hash purpose:
customer identity

Contract version:
v1

Algorithm:
SHA-256

Encoding:
UTF-8

Business-key columns:
source_system, customer_id

Column order:
fixed

String normalization:
trim leading/trailing whitespace

Case:
preserve

NULL:
reserved escaped token

Numbers:
explicit Decimal formatting

Timestamps:
UTC

Precision:
microseconds

Delimiter:
|

Escaping:
documented

Output:
lowercase hexadecimal

Metadata columns:
excluded
```

### Why version it?

Because changing any of these can change every hash:

```text
algorithm
column order
NULL token
timestamp precision
case normalization
delimiter
escaping
included columns
```

A version allows downstream systems to know what produced a fingerprint.

---

# 37. Hands-On Implementation

We will build a small customer hashing lab entirely inside this chapter.

## 37.1 Scenario

Customer records:

```text
source_system
customer_id
name
country
status
updated_at
```

We want:

```text
business_key_hash
attribute_hash
```

### Business identity

```text
source_system
customer_id
```

### Business state

```text
name
country
status
```

Exclude:

```text
updated_at
```

if it represents operational update metadata rather than business state.

---

## 37.2 Step 1 — Create Sample Records

```python
from datetime import datetime, timezone
from decimal import Decimal

customers = [
    {
        "source_system": "CRM",
        "customer_id": "C123",
        "name": "Alice",
        "country": "India",
        "status": "ACTIVE",
        "updated_at": datetime(
            2025, 3, 1, 10, 0,
            tzinfo=timezone.utc,
        ),
    },
    {
        "source_system": "CRM",
        "customer_id": "C124",
        "name": "Bob",
        "country": "India",
        "status": "ACTIVE",
        "updated_at": datetime(
            2025, 3, 1, 11, 0,
            tzinfo=timezone.utc,
        ),
    },
]
```

---

## 37.3 Step 2 — Create Canonical Serialization

```python
BUSINESS_KEY_COLUMNS = [
    "source_system",
    "customer_id",
]

ATTRIBUTE_COLUMNS = [
    "name",
    "country",
    "status",
]


def canonical_business_key(row):
    return canonical_row([
        row[column]
        for column in BUSINESS_KEY_COLUMNS
    ])


def canonical_attributes(row):
    return canonical_row([
        row[column]
        for column in ATTRIBUTE_COLUMNS
    ])
```

---

## 37.4 Step 3 — Generate Business-Key Hashes

```python
def hash_text(text: str) -> str:
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


for row in customers:
    row["business_key_hash"] = hash_text(
        canonical_business_key(row)
    )
```

Now each customer has a stable identity fingerprint.

---

## 37.5 Step 4 — Generate Attribute Hashes

```python
for row in customers:
    row["attribute_hash"] = hash_text(
        canonical_attributes(row)
    )
```

The identity and state fingerprints now have separate purposes.

---

## 37.6 Step 5 — Detect Changed Customers

Suppose the incoming row becomes:

```python
incoming = {
    "source_system": "CRM",
    "customer_id": "C123",
    "name": "Alice",
    "country": "Singapore",
    "status": "ACTIVE",
}
```

The business key is unchanged:

```text
CRM|C123
```

The attribute representation changes:

```text
Alice|India|ACTIVE
```

to:

```text
Alice|Singapore|ACTIVE
```

Therefore:

```text
business_key_hash
    SAME

attribute_hash
    DIFFERENT
```

This is exactly what a change-detection fingerprint should tell us.

---

## 37.7 Step 6 — SCD Type 2-Style Processing

Conceptually:

```text
incoming row
     ↓
business key lookup
     ↓
entity exists?
  ┌──┴──┐
 no     yes
 ↓       ↓
insert   compare attribute_hash
         ┌──────┴──────┐
       same          different
        ↓               ↓
      no-op       close + insert
```

For a changed row:

```text
old:
valid_to = NULL
is_current = TRUE
```

becomes:

```text
old:
valid_to = change_time
is_current = FALSE
```

and a new version is inserted.

The hash-diff does not replace the SCD logic. It identifies whether the business-state comparison requires that logic.

---

## 37.8 Step 7 — Python Hash

```python
python_business_hash = hash_text(
    canonical_business_key(customers[0])
)

python_attribute_hash = hash_text(
    canonical_attributes(customers[0])
)
```

Store these values for the parity test.

---

## 37.9 Step 8 — Equivalent DuckDB Hash

Conceptually:

```sql
SELECT
    sha256(
        CAST(
            source_system || '|' || customer_id
            AS BLOB
        )
    ) AS business_key_hash,

    sha256(
        CAST(
            name || '|' || country || '|' || status
            AS BLOB
        )
    ) AS attribute_hash
FROM customers;
```

This only matches Python if:

```text
Python canonical representation
=
SQL canonical representation
```

exactly.

---

## 37.10 Step 9 — Verify Python/SQL Parity

For each test row compare:

```text
Python canonical string
SQL canonical string
```

first.

Then:

```text
Python hash
SQL hash
```

The expected invariant is:

```text
canonical_python == canonical_sql
AND
hash_python == hash_sql
```

---

## 37.11 Step 10 — Introduce NULL

Change:

```text
country = India
```

to:

```text
country = NULL
```

The canonical value must use the documented NULL representation.

Do not allow:

```text
NULL
```

to silently become:

```text
"None"
```

in Python while SQL uses:

```text
"<NULL>"
```

That is a classic parity failure.

---

## 37.12 Step 11 — Introduce Timestamp Differences

Compare:

```text
2025-03-01T10:00:00Z
```

with an equivalent timezone representation.

Normalize both to UTC before hashing.

Then verify:

```text
same instant
→ same canonical timestamp
→ same hash
```

if the field's semantics are "instant in time."

---

## 37.13 Step 12 — Introduce Decimal Formatting Differences

Compare:

```text
1
1.0
1.00
```

Define:

```text
scale = 2
```

Then canonicalize all to:

```text
1.00
```

Verify the hash is stable.

---

## 37.14 Step 13 — Fix Canonicalization

For every mismatch, compare:

```text
raw value
↓
normalized value
↓
canonical representation
↓
bytes
↓
hash
```

Do not jump straight to the final digest.

The first mismatch in the chain is usually the root cause.

---

## 37.15 Step 14 — Deterministic Samples

Conceptually:

```python
digest = hashlib.sha256(
    b"C123"
).digest()

bucket = int.from_bytes(
    digest[:8],
    "big",
) % 100

if bucket < 10:
    print("sample")
```

Run it repeatedly.

The same customer should remain in the same sample bucket.

---

## 37.16 Step 15 — Hash Partitions

Conceptually:

```python
partition = int.from_bytes(
    digest[:8],
    "big",
) % 16
```

This provides deterministic routing.

Measure the distribution across all test rows rather than assuming it is perfectly even.

---

## 37.17 Step 16 — Dataset Reconciliation

For a source and target dataset:

```text
source row fingerprint
        ↓
target row fingerprint
        ↓
compare
```

Combine:

```text
row count
+
business-key count
+
numeric totals
+
row fingerprints
```

for stronger reconciliation.

---

## 37.18 Step 17 — Hash Contract Versioning

Create:

```text
hash_contract_version = v1
```

Then add a new attribute:

```text
segment
```

If the new business-state contract includes `segment`, create:

```text
attribute_hash_v2
```

rather than silently changing:

```text
attribute_hash
```

This allows controlled migration.

---

## 37.19 Step 18 — HMAC Pseudonymization

For a sensitive identifier:

```python
import hmac
import hashlib

secret = b"development-only-secret"

pseudonym = hmac.new(
    secret,
    b"alice@example.com",
    hashlib.sha256,
).hexdigest()
```

Compare conceptually:

```text
SHA256(email)
```

versus:

```text
HMAC(secret, email)
```

The HMAC requires knowledge of the secret to reproduce.

Never use the example secret in production.

---

# 38. Testing and Validation

Hashing should be tested as a contract.

## Test 1 — Same input produces same hash

```python
assert hash_text("CRM|C123") == hash_text("CRM|C123")
```

**Invariant:** deterministic output.

---

## Test 2 — Different input normally produces different hash

```python
assert hash_text("CRM|C123") != hash_text("CRM|C124")
```

**Invariant:** ordinary distinct inputs should not intentionally collapse.

This is not a mathematical guarantee.

---

## Test 3 — Column order is part of the contract

```text
C123|CRM
```

must not be silently treated as:

```text
CRM|C123
```

**Invariant:** canonical order is fixed.

---

## Test 4 — NULL differs from empty string

```text
NULL
```

and:

```text
""
```

must have distinct canonical representations.

**Invariant:** semantically distinct states remain distinct when the contract says they are distinct.

---

## Test 5 — Timestamp normalization

Equivalent instants represented in different time zones should produce the same canonical timestamp when the contract is instant-based.

**Invariant:**

```text
same instant
→ same normalized representation
```

---

## Test 6 — Decimal normalization

```text
1
1.0
1.00
```

should produce the same canonical value only if the business contract defines them as equivalent.

**Invariant:** numeric semantics are explicit.

---

## Test 7 — Python and DuckDB parity

For every fixed test vector:

```text
canonical_python == canonical_sql
hash_python == hash_sql
```

**Invariant:** cross-engine contract compatibility.

---

## Test 8 — Descriptive-field change changes hash-diff

Change:

```text
country = India
```

to:

```text
country = Singapore
```

**Invariant:**

```text
attribute_hash_old != attribute_hash_new
```

---

## Test 9 — Non-key attribute change does not change business-key hash

Change:

```text
country
```

while keeping:

```text
source_system
customer_id
```

constant.

**Invariant:**

```text
business_key_hash_old == business_key_hash_new
```

---

## Test 10 — Business-key change changes identity hash

Change:

```text
customer_id = C123
```

to:

```text
customer_id = C124
```

**Invariant:**

```text
business_key_hash_old != business_key_hash_new
```

---

## Test 11 — Deterministic sampling

Run the same identifier through the sampling function repeatedly.

**Invariant:** same identifier → same bucket.

---

## Test 12 — Hash partition assignment

Run the same identifier through:

```text
hash(key) % 16
```

multiple times.

**Invariant:** same identifier → same partition under the same contract.

---

## Test 13 — Contract version changes are detectable

Store:

```text
hash_contract_version
```

alongside the hash.

**Invariant:** consumers can identify which canonicalization rules produced a fingerprint.

---

## Test 14 — Repeated pipeline execution

Run the same dataset through the same transformation twice.

**Invariant:**

```text
fingerprints_run_1 == fingerprints_run_2
```

This is especially important for incremental pipelines.

---

# 39. Debugging Hash Mismatches

## Scenario 1 — Python and SQL produce different hashes

### Symptoms

```text
Python hash:
A...

SQL hash:
B...
```

### Likely causes

- canonical string differs;
- NULL handling;
- timestamp formatting;
- encoding;
- column order;
- trailing whitespace.

### Investigation

Print:

```text
Python canonical
SQL canonical
```

before comparing hashes.

### Incorrect fix

Change the hash algorithm in one system.

### Correct fix

Make the canonical representation identical.

### Prevention

Maintain cross-engine test vectors.

---

## Scenario 2 — NULL values cause mismatches

### Symptoms

Rows without a country differ between systems.

### Likely cause

Python:

```text
None
```

SQL:

```text
<NULL>
```

### Correct fix

Define one canonical NULL representation and apply it in both systems.

---

## Scenario 3 — Timestamps differ

### Symptoms

Only timestamp-containing records fail parity.

### Likely causes

- local timezone vs UTC;
- milliseconds vs microseconds;
- timezone offset text;
- naive timestamps.

### Correct fix

Normalize:

```text
timezone
precision
format
```

before hashing.

---

## Scenario 4 — `1`, `1.0`, and `1.00` differ unexpectedly

### Cause

Different serialization rules.

### Correct fix

Define numeric semantics and explicit decimal formatting.

---

## Scenario 5 — Whitespace causes a business-state change

### Symptoms

Changing:

```text
"Alice"
```

to:

```text
"Alice "
```

creates a new hash.

### Question

Should trailing whitespace be meaningful?

If no:

```text
trim
```

If yes:

```text
preserve
```

Do not silently choose.

---

## Scenario 6 — Column order changed

### Symptoms

Every fingerprint changes after a refactor.

### Likely cause

The canonical serialization column order changed.

### Correct fix

Restore the contract or version the contract deliberately.

---

## Scenario 7 — Schema change causes every row hash to change

### Symptoms

Adding one column creates mass SCD changes.

### Cause

The new column entered the hash-diff contract.

### Correct approaches

- exclude it if it is not business state;
- introduce a new hash contract;
- preserve the old hash;
- perform a controlled migration if it truly changes state semantics.

---

## Scenario 8 — Different text encoding

### Symptoms

Non-ASCII names produce mismatches while ASCII values match.

### Likely cause

Different encoding.

### Correct fix

Use:

```text
UTF-8
```

explicitly in every implementation.

---

# 40. Anti-Patterns

| Anti-pattern | Why it fails | Better approach |
|---|---|---|
| Hash raw `str(dict)` | Serialization contract is unclear | Explicit canonical serialization |
| Ignore NULL semantics | Different values may collapse | Explicit NULL representation |
| Ignore column order | Cross-system mismatch | Fixed schema order |
| Hash local timestamps | Time-zone mismatch | Normalize timestamps |
| Hash floats blindly | Representation issues | Explicit numeric canonicalization |
| Assume SHA-256 provides privacy | Low-entropy values can be guessed | Use an appropriate keyed/privacy design |
| Truncate hashes without analysis | Higher collision risk | Choose width deliberately |
| Use one hash for every purpose | Workloads need different guarantees | Match algorithm to use case |
| Treat hash as perfect equality proof | Collisions are possible | Combine with other reconciliation |
| Change hash contract silently | Historical fingerprints become incompatible | Version the contract |
| Include `_run_id` in hash-diff | Every run may look like a change | Exclude operational metadata |
| Include ingestion timestamp in business hash | Operational timing becomes business state | Separate business and operational fields |
| Use Python `hash()` as a durable identity | Not a cross-system contract | Explicitly select a stable algorithm |
| Assume a business key is correct because it hashes | Hashing does not define identity | Define business identity first |
| Use MD5 for new security-sensitive designs | Collision weaknesses | Use modern cryptographic constructions |
| Use xxHash for privacy | It is not a cryptographic privacy primitive | Use HMAC or another appropriate construction |
| Change partition count without planning | Keys can move between partitions | Version or redesign partitioning deliberately |
| Log sensitive raw values while debugging | Creates unnecessary exposure | Log safe test vectors and controlled diagnostics |

---

# 41. Production Case Study

A company receives customer data from:

```text
CRM
ERP
Billing
Support
```

Each system has different identifiers.

Requirements:

- create deterministic cross-system identity fingerprints;
- detect customer attribute changes;
- support SCD-style history;
- reconcile daily source/target data;
- partition large workloads;
- maintain Python/SQL consistency;
- avoid exposing customer PII unnecessarily.

## Step 1 — Define identity

Do not start with the hash.

First define:

```text
What identifies a customer in each source?
```

Suppose source-local identity is:

```text
(source_system, source_customer_id)
```

Then:

```text
CRM|C123
ERP|998812
```

can be deterministically fingerprinted.

If the requirement is to determine that CRM C123 and ERP 998812 are the same real-world customer, an identity-resolution mapping is required before hashing a cross-system global key.

---

## Step 2 — Define canonical serialization

```text
UTF-8
fixed column order
explicit NULL semantics
explicit escaping
documented string normalization
```

---

## Step 3 — Select hash algorithm

For a durable cross-system identity fingerprint:

```text
SHA-256
```

may be appropriate.

For fast bucketing:

```text
xxHash / MurmurHash
```

may be appropriate.

These are separate workloads.

---

## Step 4 — Create business-key hash

```text
source_system + source_customer_id
        ↓
canonical representation
        ↓
SHA-256
        ↓
business_key_hash
```

---

## Step 5 — Create attribute hash

```text
name + country + status + segment
        ↓
canonical representation
        ↓
SHA-256
        ↓
attribute_hash
```

Exclude:

```text
_run_id
_ingested_at
source_file
```

unless they intentionally define business state.

---

## Step 6 — SCD processing

```text
business_key_hash matches
        ↓
compare attribute_hash
        ↓
same → no change
different → new SCD version
```

---

## Step 7 — Reconciliation

Compare:

```text
row counts
business-key counts
aggregate values
row fingerprints
sampled records
```

Do not depend solely on one checksum.

---

## Step 8 — Partitioning

For a distributed workload:

```text
hash(business_key) % N
```

can route records consistently.

Measure skew.

---

## Step 9 — Privacy

Do not use:

```text
SHA256(email)
```

as if it were anonymization.

For a keyed pseudonym:

```text
HMAC(secret, email)
```

can provide a stronger controlled linkage mechanism.

Protect the secret and restrict access.

---

## Step 10 — Contract versioning

Store:

```text
hash_contract_version = v1
```

alongside the fingerprints.

If the schema or canonicalization changes:

```text
v2
```

can be introduced deliberately.

### Senior reference design

```text
                 Source Systems
              /       |       \
            CRM      ERP     Billing
              \       |       /
               \      |      /
                ▼     ▼     ▼
             Identity Mapping
                    │
                    ▼
            Canonical Serialization
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
   Business-Key Hash     Attribute Hash
          │                   │
          │                   ▼
          │              SCD Detection
          │                   │
          └─────────┬─────────┘
                    ▼
              Transformation
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
    Sampling    Partitioning Reconciliation
        │           │           │
        └───────────┴───────────┘
                    │
                    ▼
              Published Data
```

The architecture makes the hash contract explicit rather than hiding it inside individual transformations.

---

# 42. Senior Data Engineer Reasoning

Use this decision flow:

```text
What am I hashing?
        ↓
Why am I hashing it?
        ↓
Does identity need to be deterministic?
        ↓
What fields define identity?
        ↓
What fields define change?
        ↓
How are values canonicalized?
        ↓
What hash algorithm fits the use case?
        ↓
What collision risk is acceptable?
        ↓
Must Python and SQL match?
        ↓
Will the schema evolve?
        ↓
Is sensitive data involved?
        ↓
Do I need a keyed construction such as HMAC?
        ↓
How will I test and version the contract?
```

### Senior-level questions

Before writing:

```python
hashlib.sha256(...)
```

ask:

1. What exactly is the input?
2. Is identity stable?
3. Which fields belong in identity?
4. Which fields define business state?
5. Which fields are metadata?
6. What happens with NULL?
7. What happens with whitespace?
8. What happens with time zones?
9. What happens with decimal scale?
10. Will another SQL engine need to reproduce the result?
11. How many values will be hashed?
12. What collision risk is acceptable?
13. Is there an adversary?
14. Does the identifier contain PII?
15. How will the contract evolve?

The most important question is:

> **What exact canonical representation am I hashing, and what guarantee do I need from the resulting fingerprint?**

---

# 43. Interview Questions

## Basic — 10

### 1. What is a hash?

**Expected answer:** A deterministic function that maps input data to a fixed-size fingerprint.

**Explanation:** The output depends on the input and selected algorithm.

**Key concepts:** digest, deterministic, fixed-size.

**Senior insight:** In Data Engineering, the canonicalization contract often matters more than the hash call itself.

---

### 2. Why is determinism important?

**Expected answer:** The same logical input must produce the same fingerprint across runs and systems.

**Explanation:** This supports stable identity and repeatable change detection.

**Key concepts:** reproducibility.

**Senior insight:** Determinism requires identical canonical bytes, not merely the same algorithm name.

---

### 3. Is hashing the same as encryption?

**Expected answer:** No. Encryption is designed to be reversible with a key; hashing is designed as a one-way fingerprinting construction.

**Explanation:** They solve different problems.

**Key concepts:** encryption, hash.

**Senior insight:** Choosing the wrong primitive creates architectural problems.

---

### 4. What is SHA-256?

**Expected answer:** A cryptographic hash function producing a 256-bit digest.

**Explanation:** It is commonly used for durable fingerprints.

**Key concepts:** cryptographic hash.

**Senior insight:** SHA-256 does not by itself define serialization or privacy.

---

### 5. What is a hash collision?

**Expected answer:** Two different inputs produce the same hash value.

**Explanation:** Every finite hash has a finite output space.

**Key concepts:** collision.

**Senior insight:** Collision risk must be considered relative to scale and consequences.

---

### 6. What is a business-key hash?

**Expected answer:** A deterministic fingerprint generated from canonicalized business-key fields.

**Explanation:** It can act as a reproducible identity representation.

**Key concepts:** identity.

**Senior insight:** The hash does not decide what the business key is.

---

### 7. What is a hash-diff?

**Expected answer:** A fingerprint of descriptive attributes used to detect whether the row's business state changed.

**Explanation:** Old and new fingerprints are compared.

**Key concepts:** change detection.

**Senior insight:** Metadata fields should generally be excluded.

---

### 8. Why is NULL handling important?

**Expected answer:** Different systems may serialize NULL differently, causing mismatched hashes.

**Explanation:** NULL must have an explicit canonical representation.

**Key concepts:** serialization.

**Senior insight:** A reserved token must itself be unambiguous.

---

### 9. What is deterministic sampling?

**Expected answer:** Using a hash to assign records consistently to sample buckets.

**Explanation:** The same record stays in the same sample.

**Key concepts:** reproducibility.

**Senior insight:** It is useful for QA and debugging, not a security randomness mechanism.

---

### 10. What is HMAC?

**Expected answer:** A keyed cryptographic construction that combines a secret key and message to produce a digest.

**Explanation:** Reproduction requires the key.

**Key concepts:** keyed hash, pseudonymization.

**Senior insight:** HMAC is not automatically anonymization.

---

## Moderate — 10

### 11. Why is canonical serialization necessary?

**Expected answer:** Different representations of the same logical record can otherwise produce different hashes.

**Explanation:** Hashes operate on bytes, not abstract business objects.

**Key concepts:** canonicalization.

**Senior insight:** The serialization contract is part of the identity contract.

---

### 12. Why can Python and SQL SHA-256 results differ?

**Expected answer:** They may hash different bytes because of NULL handling, formatting, encoding, ordering, or timezone differences.

**Explanation:** Same algorithm does not imply same input bytes.

**Key concepts:** parity.

**Senior insight:** Compare canonical representations before comparing digests.

---

### 13. Why should metadata columns be excluded from hash-diffs?

**Expected answer:** Operational metadata can change every run without changing business state.

**Explanation:** Including `_run_id` or ingestion time creates false changes.

**Key concepts:** business state.

**Senior insight:** Define hash-diff columns as an explicit contract.

---

### 14. When might xxHash be preferable to SHA-256?

**Expected answer:** For fast non-security uses such as bucketing or partitioning.

**Explanation:** xxHash is designed for speed rather than cryptographic security.

**Key concepts:** workload-specific algorithm choice.

**Senior insight:** "Faster" is valuable only when the required guarantees are still satisfied.

---

### 15. Why is 64-bit hashing different from 256-bit hashing?

**Expected answer:** The output space is much smaller, so collision risk is much higher at scale.

**Explanation:** Birthday-bound behavior depends on hash width.

**Key concepts:** collision probability.

**Senior insight:** 64-bit may be fine for partitioning but inappropriate for durable identity in some large systems.

---

### 16. What happens when a hash-diff column is added?

**Expected answer:** Existing rows may all receive different hashes.

**Explanation:** The canonical representation changed.

**Key concepts:** schema evolution.

**Senior insight:** Version the contract or preserve the old hash rather than silently interpreting every row as a business change.

---

### 17. Why isn't SHA-256(email) automatically anonymous?

**Expected answer:** Emails are often guessable, so an attacker can hash candidate values and compare.

**Explanation:** Hashing does not remove the small search space.

**Key concepts:** dictionary attack.

**Senior insight:** Pseudonymization and anonymization are different privacy outcomes.

---

### 18. What is a hash-based surrogate key?

**Expected answer:** A deterministic key generated from canonical business-key values.

**Explanation:** It can be generated independently without a centralized sequence.

**Key concepts:** surrogate key.

**Senior insight:** Cross-system canonicalization becomes critical.

---

### 19. What is the birthday bound?

**Expected answer:** Collision probability becomes significant around roughly `2^(n/2)` samples for an n-bit uniformly distributed hash.

**Explanation:** Collisions emerge much earlier than the full output-space size.

**Key concepts:** birthday paradox.

**Senior insight:** Use it for engineering intuition, not as a complete collision analysis.

---

### 20. How would you debug a hash mismatch?

**Expected answer:** Compare raw values, normalized values, canonical strings, encoded bytes, and finally hashes.

**Explanation:** The first mismatch identifies the contract problem.

**Key concepts:** troubleshooting.

**Senior insight:** Do not replace algorithms before proving the input bytes differ.

---

## Hard — 10

### 21. Design a deterministic customer key across three systems.

**Expected answer:** Define source namespace + source identifier, canonicalize deterministically, select a stable hash, store contract version, and retain original identity fields.

**Explanation:** The hash provides a stable fingerprint after identity is defined.

**Key concepts:** identity, namespace.

**Senior insight:** Hashing does not solve entity resolution.

---

### 22. Design an SCD Type 2 hash-diff mechanism.

**Expected answer:** Create a business-key hash and separate attribute hash, exclude metadata, compare current state to incoming state, close the current version and insert a new version when the attribute hash changes.

**Explanation:** Hash-diff provides efficient change detection.

**Key concepts:** SCD2.

**Senior insight:** The hash does not replace temporal versioning.

---

### 23. Why might a hash contract break after a harmless-looking refactor?

**Expected answer:** Column ordering, formatting, NULL semantics, or serialization may change.

**Explanation:** The logical data may be equivalent while the canonical bytes differ.

**Key concepts:** compatibility.

**Senior insight:** Hash contracts require regression test vectors.

---

### 24. When is a 64-bit hash acceptable?

**Expected answer:** Often for bucketing or partitioning where small collision risk is acceptable and collisions do not imply identity corruption.

**Explanation:** Its collision space is smaller than wider hashes.

**Key concepts:** risk.

**Senior insight:** The consequence of collision matters as much as the probability.

---

### 25. How would you reconcile 1 billion source rows against target rows?

**Expected answer:** Use layered reconciliation: counts, key counts, aggregates, deterministic fingerprints, partition-level comparisons, and targeted row-level checks.

**Explanation:** A single checksum is not sufficient evidence.

**Key concepts:** reconciliation.

**Senior insight:** Optimize for high confidence with bounded cost.

---

### 26. How would you make Python and PostgreSQL hashes match?

**Expected answer:** Define identical canonicalization rules, UTF-8 encoding, field ordering, NULL handling, numeric formatting, timestamp normalization, and algorithm/output representation; then test with shared vectors.

**Explanation:** Same algorithm alone is insufficient.

**Key concepts:** cross-engine parity.

**Senior insight:** Treat the canonicalization specification as an interface contract.

---

### 27. How do you prevent every row from appearing changed after adding a column?

**Expected answer:** Determine whether the column is business state. If not, exclude it; otherwise version the hash contract and migrate deliberately.

**Explanation:** Schema change and business-state change are distinct.

**Key concepts:** schema evolution.

**Senior insight:** Never silently redefine historical business state.

---

### 28. How would you use HMAC for email pseudonymization?

**Expected answer:** Normalize email according to the approved business/privacy contract, use a protected secret key with HMAC-SHA-256, store the pseudonym, and tightly control secret access.

**Explanation:** The secret prevents straightforward public recomputation.

**Key concepts:** HMAC, pseudonymization.

**Senior insight:** HMAC reduces a specific attack path but does not automatically anonymize the surrounding dataset.

---

### 29. What should you do if a hash collision is detected in a durable key system?

**Expected answer:** Do not silently merge records. Retain original business keys, detect the collision, investigate the contract, and migrate to a wider/appropriate representation if necessary.

**Explanation:** A collision is a correctness incident for identity.

**Key concepts:** collision mitigation.

**Senior insight:** A hash should usually be treated as a fingerprint, not blindly as the only identity evidence.

---

### 30. How should hash contracts be versioned?

**Expected answer:** Store the contract version with the fingerprint and support old/new representations during controlled migration.

**Explanation:** Canonicalization changes can invalidate historical comparisons.

**Key concepts:** compatibility.

**Senior insight:** Versioning allows reproducibility and rollback.

---

## Advanced — 10

### 31. Design hashing for 10 billion records.

**Expected answer:** Choose hash width from collision risk and consequence, define a stable canonical contract, consider binary storage, test cross-engine parity, measure performance, and retain original keys for collision detection.

**Explanation:** Scale changes the economics and collision analysis.

**Key concepts:** scale.

**Senior insight:** Storage/index cost and collision consequences must be evaluated together.

---

### 32. How would you migrate from MD5 to SHA-256 without breaking downstream systems?

**Expected answer:** Introduce a versioned SHA-256 column, retain MD5 temporarily, publish both during migration, validate parity at the business-key level, migrate consumers, then retire MD5 according to compatibility requirements.

**Explanation:** Hash changes are contract changes.

**Key concepts:** migration.

**Senior insight:** Never silently overwrite a durable identity representation.

---

### 33. Design a cross-language canonicalization standard.

**Expected answer:** Define types, field order, NULL token, escaping, Unicode policy, number formatting, timestamps, encoding, hash algorithm, output representation, and test vectors.

**Explanation:** Every implementation must produce identical bytes.

**Key concepts:** serialization contract.

**Senior insight:** A few dozen test vectors can prevent years of silent incompatibility.

---

### 34. Design deterministic sampling for a distributed platform.

**Expected answer:** Select a stable identity input, hash it with a stable algorithm, map to a bucket, define bucket semantics, and preserve the hash contract.

**Explanation:** All workers independently make the same sample decision.

**Key concepts:** deterministic distribution.

**Senior insight:** Sampling contract changes can change experimental populations.

---

### 35. How would you design hash-based partitioning with changing worker counts?

**Expected answer:** Recognize that `hash(key) % N` changes assignments when N changes; use a deliberate partitioning scheme or consistent-hashing strategy when stable ownership matters.

**Explanation:** Modulo partitioning is not rebalancing-free.

**Key concepts:** partition stability.

**Senior insight:** Partition identity is itself an operational contract.

---

### 36. How would you detect whether a schema change is technical or semantic?

**Expected answer:** Determine whether the new field changes the business-state definition or only metadata/representation.

**Explanation:** Only business-state changes should alter a business-state hash.

**Key concepts:** semantics.

**Senior insight:** Hash design forces explicit domain modeling.

---

### 37. How can hashes support Data Vault-style change detection?

**Expected answer:** Hash keys can represent business-key identities, while hash-diffs can represent descriptive satellite state.

**Explanation:** The two fingerprints serve different purposes.

**Key concepts:** Data Vault, hash key, hash diff.

**Senior insight:** Canonicalization consistency is critical across ingestion and satellite loads.

---

### 38. How would you validate a 100,000-row Python/SQL hash implementation?

**Expected answer:** Generate deterministic fixtures including NULLs, Unicode, timestamps, decimals, delimiters, empty strings, and edge values; compare canonical strings and hashes row by row.

**Explanation:** Random ordinary ASCII data is not enough.

**Key concepts:** property and compatibility testing.

**Senior insight:** Edge-case test vectors are more valuable than only happy-path samples.

---

### 39. How do you distinguish hash mismatch from data mismatch?

**Expected answer:** Compare source values, canonical representations, encoded bytes, and hashes separately.

**Explanation:** A hash mismatch may reflect a serialization mismatch rather than different business data.

**Key concepts:** layered diagnosis.

**Senior insight:** Observability should expose safe canonicalization diagnostics without leaking sensitive values.

---

### 40. What is the strongest production mental model for hashing?

**Expected answer:** First define identity/state semantics, then canonicalize deterministically, then select an appropriate hash, quantify collision risk, test parity, version the contract, and use the fingerprint only for guarantees it actually provides.

**Explanation:** Hashing is one component of a larger data contract.

**Key concepts:** engineering judgment.

**Senior insight:** The right hash is the one whose guarantees match the business and operational requirement.

---

# 44. Architecture Questions

## Architecture 1 — Deterministic customer keys across five source systems

Design a system where:

```text
CRM
ERP
Billing
Support
Marketing
```

all provide customer identifiers.

### Reference solution

1. Define source-local identity.
2. Namespace each source.
3. Define the canonical identity fields.
4. Normalize them.
5. Hash with a durable algorithm.
6. Store original source keys.
7. Store hash contract version.
8. Validate uniqueness.
9. Detect collisions explicitly.
10. Keep entity-resolution logic separate from hashing.

---

## Architecture 2 — SCD Type 2 change detection

### Requirements

- millions of customers;
- daily source refresh;
- many unchanged rows;
- only changed rows should create new SCD versions.

### Reference design

```text
incoming
   ↓
business_key_hash
   ↓
current dimension lookup
   ↓
attribute_hash comparison
   ↓
same → no-op
different → close + insert
```

Use metadata exclusion and deterministic canonicalization.

---

## Architecture 3 — Cross-language hashing

### Requirement

Python, DuckDB, and PostgreSQL must generate identical hashes.

### Reference design

Publish:

```text
hash contract
+
test vectors
+
canonicalization library/specification
```

Validate:

```text
raw values
→ canonical text
→ UTF-8 bytes
→ digest
```

across all engines.

---

## Architecture 4 — Hash partitioning for 10 billion rows

### Reference considerations

- hash width;
- skew;
- partition count;
- partition stability;
- worker parallelism;
- storage layout;
- repartitioning cost.

Do not assume:

```text
hash(key) % N
```

remains stable when `N` changes.

---

## Architecture 5 — Daily source/target reconciliation

### Reference design

For each partition:

```text
row count
+
distinct key count
+
business aggregates
+
row fingerprints
+
deterministic sample
```

Investigate only mismatched partitions at row level.

This creates a scalable reconciliation hierarchy.

---

## Architecture 6 — Hash contract that survives schema evolution

### Reference design

Maintain:

```text
hash_contract_version
```

and separate:

```text
business identity contract
business state contract
operational metadata
```

When a field is added:

1. determine its semantic role;
2. decide whether it belongs in the hash;
3. version the contract if necessary;
4. preserve historical hashes;
5. migrate consumers deliberately.

---

## Architecture 7 — Privacy-aware pseudonymization

### Reference design

```text
PII
 ↓
approved normalization
 ↓
HMAC with protected secret
 ↓
pseudonymous identifier
```

Protect the key.

Do not use plain SHA-256 as if it were anonymization.

Limit linkage and access to the pseudonym mapping.

---

## Architecture 8 — SHA-256 vs xxHash

### Reference decision framework

Use:

```text
SHA-256
```

when stronger cryptographic fingerprint properties and durable interoperability matter.

Use:

```text
xxHash
```

when very fast non-adversarial hashing is sufficient, such as partitioning or local bucketing.

Do not choose based only on raw benchmark speed.

---

## Architecture 9 — Zero-downtime hash-contract migration

### Example

```text
v1 → MD5
v2 → SHA-256
```

Reference workflow:

```text
add v2
  ↓
dual-write
  ↓
validate
  ↓
migrate consumers
  ↓
monitor
  ↓
retire v1
```

Never silently reinterpret v1 values as v2.

---

## Architecture 10 — Collision detection and mitigation

### Reference design

Store:

```text
hash
original business key
contract version
```

Enforce or validate:

```text
hash → one business key
```

If a collision occurs:

```text
detect
 ↓
quarantine
 ↓
do not merge
 ↓
investigate
 ↓
increase representation width/change design
 ↓
migrate safely
```

---

# 45. Production Checklist

## Hash contract

- [ ] Hash purpose is defined.
- [ ] Input fields are explicitly defined.
- [ ] Column order is fixed.
- [ ] NULL behavior is defined.
- [ ] String normalization is defined.
- [ ] Case rules are defined.
- [ ] Numeric representation is defined.
- [ ] Decimal scale is defined.
- [ ] Timestamp normalization is defined.
- [ ] Timestamp precision is defined.
- [ ] Encoding is defined.
- [ ] Delimiter is defined.
- [ ] Escaping is defined.
- [ ] Hash algorithm is defined.
- [ ] Output representation is defined.
- [ ] Contract version is defined.
- [ ] Metadata columns are explicitly included/excluded.

## Correctness

- [ ] Determinism is tested.
- [ ] Python/SQL parity is tested.
- [ ] NULL cases are tested.
- [ ] Unicode is tested.
- [ ] Timestamp boundaries are tested.
- [ ] Decimal representations are tested.
- [ ] Delimiter values are tested.
- [ ] Repeated runs produce identical fingerprints.
- [ ] SCD change detection is tested.
- [ ] Schema evolution is deliberately handled.

## Collision

- [ ] Hash width is appropriate.
- [ ] Record volume is considered.
- [ ] Historical version count is considered.
- [ ] Collision risk is understood.
- [ ] Truncation is justified.
- [ ] Original business keys are retained where identity is critical.
- [ ] Collision detection exists where appropriate.

## Performance

- [ ] Hash computation cost is measured.
- [ ] Storage size is considered.
- [ ] Index/join impact is considered.
- [ ] Binary vs hex is evaluated.
- [ ] Partitioning skew is measured.

## Privacy

- [ ] Sensitive fields are identified.
- [ ] Plain hashing is not mistaken for anonymization.
- [ ] Dictionary-attack risk is considered.
- [ ] HMAC is considered where appropriate.
- [ ] Secrets are protected.
- [ ] Secret rotation requirements are defined.
- [ ] Access to pseudonymization keys is restricted.

---

# 46. Exercises

## Beginner

### Exercise 1

Hash a string using SHA-256.

**Goal:** understand deterministic output and hexadecimal representation.

---

### Exercise 2

Hash the same string twice.

**Goal:** prove determinism.

---

### Exercise 3

Hash:

```text
hello
Hello
```

**Goal:** observe input sensitivity.

---

### Exercise 4

Explain hashing versus encryption using a customer dataset.

**Goal:** choose the correct primitive for retrieval versus comparison.

---

### Exercise 5

Build:

```text
customer_id|country|status
```

as a canonical string.

**Goal:** understand serialization.

---

## Intermediate

### Exercise 6

Build a business-key hash from:

```text
source_system
customer_id
```

**Solution guidance:** fix order, encode UTF-8, hash with a documented algorithm.

---

### Exercise 7

Build an attribute hash from:

```text
name
country
status
```

Then change `country`.

**Expected result:** business-key hash unchanged, attribute hash changed.

---

### Exercise 8

Handle:

```text
NULL
""
"NULL"
```

using an unambiguous canonicalization strategy.

---

### Exercise 9

Normalize timestamps to UTC and fixed precision before hashing.

---

### Exercise 10

Normalize decimals to a fixed scale.

---

### Exercise 11

Produce the same hash in Python and DuckDB.

Create at least ten test vectors.

---

## Advanced

### Exercise 12

Implement SCD Type 2 change detection using business-key and attribute hashes.

Include:

```text
new entity
unchanged entity
changed entity
```

---

### Exercise 13

Build deterministic sampling:

```text
10%
25%
50%
```

using hash buckets.

Measure actual sample proportions.

---

### Exercise 14

Build:

```text
hash(customer_id) % 16
```

partition assignment.

Measure distribution and identify skew.

---

### Exercise 15

Build row-level fingerprints and use them for source/target reconciliation.

---

### Exercise 16

Add a column to the hash-diff schema and demonstrate mass hash changes.

Then implement a versioned hash contract.

---

### Exercise 17

Estimate collision risk for:

```text
10^9 rows
32-bit hash
64-bit hash
128-bit hash
```

Use the birthday-bound approximation and explain the engineering implications.

---

## Expert

### Exercise 18

Design a cross-system identity strategy for five source systems with independent customer identifiers.

---

### Exercise 19

Design a billion-row SCD change-detection system.

Consider:

- hash width;
- storage;
- indexing;
- partitioning;
- incremental processing;
- collision handling.

---

### Exercise 20

Design privacy-aware pseudonymization for email addresses.

Compare:

```text
SHA-256(email)
```

and:

```text
HMAC(secret, email)
```

Explain the threat model.

---

### Exercise 21

Design a zero-downtime migration from:

```text
hash_contract_v1
```

to:

```text
hash_contract_v2
```

without breaking consumers.

---

### Exercise 22

Design collision mitigation for a durable identity system.

Include:

- detection;
- quarantine;
- investigation;
- migration;
- downstream correction.

---

# 47. Final Mental Model

## The hashing pipeline

```text
Structured Data
      ↓
Canonical Serialization
      ↓
UTF-8 / Defined Encoding
      ↓
Hash Function
      ↓
Deterministic Fingerprint
```

## For identity

```text
Business Key
      ↓
Canonical Representation
      ↓
Hash
      ↓
Stable Identity Fingerprint
```

## For change detection

```text
Descriptive Attributes
      ↓
Canonical Representation
      ↓
Hash-Diff
      ↓
Compare Old vs New
      ↓
Changed / Unchanged
```

## For sensitive identifiers

```text
Sensitive Identifier
      ↓
Protected Secret + HMAC
      ↓
Pseudonymous Identifier
```

Remember:

> **A hash is only as deterministic as the serialization contract that feeds it.**

And:

> **Hashing is a tool for identity, change detection, partitioning, sampling, and reconciliation — not a universal solution for uniqueness, security, or privacy.**

---

# 48. Exit Criteria

You are ready to move forward when you can independently:

- [ ] explain hashing;
- [ ] explain deterministic hashing;
- [ ] distinguish hashing from encryption;
- [ ] distinguish cryptographic and non-cryptographic hashes;
- [ ] explain SHA-256, SHA-1, MD5, xxHash, and MurmurHash at the appropriate level;
- [ ] build canonical serialization;
- [ ] handle NULL values correctly;
- [ ] canonicalize strings;
- [ ] canonicalize numbers;
- [ ] canonicalize decimals;
- [ ] canonicalize timestamps;
- [ ] normalize time zones;
- [ ] create deterministic business-key hashes;
- [ ] use hashes as surrogate-key fingerprints;
- [ ] create hash-diffs;
- [ ] use hashes for SCD change detection;
- [ ] exclude operational metadata from business-state hashes;
- [ ] make Python and SQL hashing compatible;
- [ ] reason about hex versus binary versus 64-bit representations;
- [ ] understand collisions;
- [ ] understand birthday-bound intuition;
- [ ] choose hash width appropriately;
- [ ] perform deterministic sampling;
- [ ] perform hash-based partitioning;
- [ ] use hashes for reconciliation;
- [ ] reason about schema/hash-contract evolution;
- [ ] explain HMAC;
- [ ] explain why plain hashing does not anonymize PII;
- [ ] design pseudonymization appropriately;
- [ ] test deterministic hashing;
- [ ] debug cross-system hash mismatches;
- [ ] design production-grade hash contracts;
- [ ] explain these decisions in a senior Data Engineering interview.

---

# 49. Quality-Control Summary

Before considering this topic complete, verify that:

- beginner concepts precede advanced concepts;
- hashing is taught as a Data Engineering design primitive;
- deterministic hashing is explicit;
- cryptographic and non-cryptographic hashes are distinguished;
- SHA-256, SHA-1, MD5, xxHash, and MurmurHash are covered;
- canonical serialization is a first-class concept;
- strings, NULLs, numbers, decimals, timestamps, time zones, encoding, column ordering, and delimiters are covered;
- business-key hashes are explained;
- hash-based surrogate keys are explained;
- hash-diffs are explained;
- SCD change detection is explained;
- metadata exclusion is explained;
- Python/SQL parity is demonstrated;
- storage representations are compared;
- collision probability is explained;
- birthday-bound intuition is explained;
- deterministic sampling is included;
- hash partitioning is included;
- reconciliation is included;
- schema evolution is included;
- HMAC is included;
- pseudonymization versus anonymization is clearly distinguished;
- security claims are precise;
- testing is included;
- debugging is included;
- anti-patterns are included;
- production architecture is included;
- exercises progress from beginner to expert;
- 40 interview questions are included;
- 10 architecture questions are included;
- the production checklist is included;
- the final mental model is clear.

---

# 50. Learning Progression

The intended progression is:

```text
Hashing Basics
      ↓
Hash Properties
      ↓
Canonical Serialization
      ↓
Business-Key Hashes
      ↓
Surrogate Keys
      ↓
Hash-Diffs
      ↓
SCD Change Detection
      ↓
Python/SQL Parity
      ↓
Collision Reasoning
      ↓
Sampling / Partitioning
      ↓
Reconciliation
      ↓
Schema Evolution
      ↓
HMAC / Pseudonymization
      ↓
Production Design
      ↓
Testing
      ↓
Debugging
      ↓
Senior Architecture
```

The production habit to carry into the next topics is:

> **Define identity and business state first. Canonicalize explicitly. Hash deliberately. Version the contract. Test parity. Quantify collision risk. Never assume a hash provides guarantees that belong to a different security or data-modeling primitive.**
